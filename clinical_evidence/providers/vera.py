"""Vera Health AI provider — primary clinical evidence reviewer.

Vera Health (https://verahealth.ai) is a retrieval-first clinical decision-support
search engine that searches 60M+ peer-reviewed papers and guidelines. It is the
#1 ranked clinical AI tool (Clinical AI Report 2026, MedExpertQA benchmark 62.2%).

This adapter integrates Vera as the PRIMARY AI provider for evidence synthesis,
recommendation validation, and contradiction detection. The orchestrator prefers
Vera over OpenAI for all AI review tasks.

Configuration (env vars or ProviderConfiguration.extra_config):
  VERAHEALTH_API_KEY       — API key (primary, preferred env var name)
  VERA_API_KEY             — Fallback env var name
  VERAHEALTH_API_BASE_URL  — Base URL (default: https://api.verahealth.ai/v1)
  VERAHEALTH_MODEL         — Model version (default: vera-clinical-1)
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from clinical_evidence.exceptions import ProviderAuthError, ProviderError
from clinical_evidence.providers.base import (
    AIReviewResult,
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class VeraProvider(BaseEvidenceProvider):
    """Vera Health AI provider — highest accuracy structured clinical answers."""

    @property
    def provider_type(self) -> str:
        return "vera"

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.api_key = (
            self.config.get("api_key")
            or os.environ.get("VERAHEALTH_API_KEY")
            or os.environ.get("VERA_API_KEY", "")
        )
        self.base_url = (
            self.config.get("api_base_url")
            or os.environ.get("VERAHEALTH_API_BASE_URL", "https://api.verahealth.ai/v1")
        )
        self.model = (
            self.config.get("model")
            or os.environ.get("VERAHEALTH_MODEL", "vera-clinical-1")
        )
        self._session: Any = None

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_structured_output=True,
            supports_ai_summary=True,
            supports_citations=True,
            max_query_length=2000,
            rate_limit_per_minute=60,
            requires_authentication=True,
        )

    def authenticate(self) -> bool:
        if not self.api_key:
            raise ProviderAuthError(
                "Vera Health API key not configured. Set VERAHEALTH_API_KEY "
                "environment variable or configure via ProviderConfiguration."
            )
        t0 = time.time()
        try:
            url = f"{self.base_url}/health"
            req = self._build_request(url)
            with self._urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as exc:
            raise ProviderAuthError(f"Vera Health authentication failed: {exc}") from exc

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            url = f"{self.base_url}/health"
            req = self._build_request(url)
            with self._urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            return {
                "available": True,
                "latency_ms": (time.time() - t0) * 1000,
                "error": None,
                "model": self.model,
                "api_version": data.get("version", "unknown"),
            }
        except Exception as exc:
            return {
                "available": False,
                "latency_ms": (time.time() - t0) * 1000,
                "error": str(exc),
            }

    # ------------------------------------------------------------------ #
    # Evidence search & retrieval
    # ------------------------------------------------------------------ #
    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        """Search Vera Health's 60M+ paper corpus for clinical evidence."""
        retmax = kwargs.get("max_results", 20)
        payload = {
            "query": query,
            "max_results": retmax,
            "model": self.model,
        }
        try:
            result = self._call_api("search", payload)
        except ProviderError:
            return []
        references = result.get("references", []) or result.get("results", [])
        return [self.normalize(ref) for ref in references]

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        payload = {"identifier": identifier, "identifier_type": id_type}
        try:
            result = self._call_api("retrieve", payload)
            ref = result.get("reference") or result.get("result")
            if ref:
                return self.normalize(ref)
        except ProviderError:
            pass
        return None

    # ------------------------------------------------------------------ #
    # AI clinical review (primary use case)
    # ------------------------------------------------------------------ #
    def review_clinical_question(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> AIReviewResult:
        """Submit a clinical question to Vera Health for structured AI review.

        Vera returns evidence-graded, cited answers — this is the most accurate
        format for GDES clinical decision support and recommendation validation.
        """
        payload: dict[str, Any] = {
            "query": question,
            "model": self.model,
            "structured_output": True,
            "include_citations": True,
        }
        if context:
            payload["context"] = context

        result = self._call_api("clinical/review", payload)

        summary = (
            result.get("summary")
            or result.get("answer")
            or result.get("synthesis", "")
        )

        key_findings = (
            result.get("key_findings", [])
            or result.get("findings", [])
            or []
        )

        supporting = (
            result.get("supporting_evidence", [])
            or result.get("supporting", [])
            or result.get("references", [])
        )

        contradictory = (
            result.get("contradictory_evidence", [])
            or result.get("contradictory", [])
            or []
        )

        confidence = (
            result.get("confidence_score")
            or result.get("confidence")
        )

        alignment = (
            result.get("recommendation_alignment", "")
            or result.get("alignment", "")
        )

        structured = result.get("structured_result") or result
        if isinstance(structured, str):
            try:
                structured = json.loads(structured)
            except (json.JSONDecodeError, TypeError):
                structured = {"summary": structured}

        return AIReviewResult(
            summary=summary,
            key_findings=key_findings,
            limitations=result.get("limitations", []),
            supporting_evidence=supporting,
            contradictory_evidence=contradictory,
            confidence_score=confidence,
            recommendation_alignment=alignment,
            structured_data=structured,
            raw_response=json.dumps(result),
        )

    def validate_recommendation(
        self,
        recommendation_text: str,
        disease_id: str = "",
        guidelines: list[str] | None = None,
    ) -> AIReviewResult:
        """Validate a GDES recommendation against current evidence via Vera Health."""
        context = {"disease_id": disease_id, "guidelines": guidelines or []}
        return self.review_clinical_question(recommendation_text, context=context)

    # ------------------------------------------------------------------ #
    # Normalisation
    # ------------------------------------------------------------------ #
    def normalize(self, raw: dict) -> EvidenceItem:
        authors_raw = raw.get("authors", "")
        if isinstance(authors_raw, list):
            authors = "; ".join(
                a.get("name", "") if isinstance(a, dict) else str(a)
                for a in authors_raw
            )
        else:
            authors = str(authors_raw) if authors_raw else ""

        return EvidenceItem(
            source_type="vera",
            title=raw.get("title", ""),
            authors=authors,
            journal=raw.get("journal", "") or raw.get("journal_name", ""),
            publication_date=raw.get("publication_date") or raw.get("date"),
            pmid=raw.get("pmid", ""),
            pmcid=raw.get("pmcid", ""),
            doi=raw.get("doi", ""),
            abstract=raw.get("abstract", "") or raw.get("summary", ""),
            url=raw.get("url", ""),
            evidence_level=raw.get("evidence_level", "") or raw.get("evidence_grade", ""),
            study_design=raw.get("study_design", ""),
            citation_count=raw.get("citation_count") or raw.get("cited_by"),
            keywords=raw.get("keywords", []),
            relevance_score=raw.get("relevance_score") or raw.get("score"),
            raw_data=raw,
        )

    # ------------------------------------------------------------------ #
    # HTTP helpers
    # ------------------------------------------------------------------ #
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "GDES-CEI-VeraHealth/1.0",
        }

    def _build_request(self, url: str, data: bytes | None = None):
        """Build a urllib Request object."""
        import urllib.request

        return urllib.request.Request(
            url, data=data, headers=self._headers(),
            method="POST" if data is not None else "GET",
        )

    def _urlopen(self, req, timeout: int = 60):
        """Open a urllib request (wrapped for testability)."""
        import urllib.request
        return urllib.request.urlopen(req, timeout=timeout)

    def _call_api(self, endpoint: str, payload: dict, timeout: int = 60) -> dict:
        """Make a POST request to the Vera Health API."""
        import urllib.error
        import urllib.request

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        data = json.dumps(payload).encode()
        req = self._build_request(url, data=data)
        try:
            with self._urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode() if exc.fp else ""
            if exc.code == 401:
                raise ProviderAuthError("Vera Health authentication failed (401)") from exc
            if exc.code == 429:
                raise ProviderError("Vera Health rate limit exceeded (429)") from exc
            raise ProviderError(f"Vera Health API error {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(f"Vera Health connection failed: {exc}") from exc

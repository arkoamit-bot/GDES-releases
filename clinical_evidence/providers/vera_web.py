"""Vera Health web session provider — logs in via the web app as a user.

Uses a real Vera Health user account to authenticate via Supabase Auth,
then calls the internal Next.js API routes (verahealth.ai/api/*) directly
with the session JWT. This is a workaround for when the enterprise API
(api.verahealth.ai) is not yet available.

Caveats:
- Requires a Vera Health user account (email/password).
- Requires the Supabase anon key for the Vera project (auth.verahealth.ai).
- Subject to Vera's terms of service — automated access may be restricted.
- Internal API routes may change without notice.

Configuration (via ProviderConfiguration.extra_config):
    vera_web_email         — User's Vera Health account email (required)
    vera_web_password      — User's Vera Health account password (required)
    supabase_anon_key      — Supabase anon key for auth.verahealth.ai (required)
    web_base_url           — Base URL (default: https://verahealth.ai)
    supabase_auth_url      — Supabase auth URL (default: https://auth.verahealth.ai/auth/v1)
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from clinical_evidence.exceptions import ProviderAuthError, ProviderError
from clinical_evidence.providers.base import (
    AIReviewResult,
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class VeraWebSessionProvider(BaseEvidenceProvider):
    """Vera Health web session provider — uses user credentials to access the web API."""

    @property
    def provider_type(self) -> str:
        return "vera_web"

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.email = self.config.get("vera_web_email", "")
        self.password = self.config.get("vera_web_password", "")
        self.supabase_anon_key = (
            self.config.get("supabase_anon_key")
            or os.environ.get("VERA_SUPABASE_ANON_KEY", "")
        )
        self.web_base_url = (
            self.config.get("web_base_url", "")
            or os.environ.get("VERA_WEB_BASE_URL", "https://verahealth.ai")
        ).rstrip("/")
        self.supabase_auth_url = (
            self.config.get("supabase_auth_url", "")
            or os.environ.get(
                "VERA_SUPABASE_AUTH_URL",
                "https://auth.verahealth.ai/auth/v1",
            )
        ).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "GDES-CEI-VeraWeb/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expires_at: float = 0

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_structured_output=True,
            supports_ai_summary=True,
            supports_citations=True,
            max_query_length=2000,
            rate_limit_per_minute=30,
            requires_authentication=True,
        )

    # ------------------------------------------------------------------ #
    # Authentication
    # ------------------------------------------------------------------ #
    def authenticate(self) -> bool:
        if not self.email or not self.password:
            raise ProviderAuthError(
                "Vera Web credentials not configured. Set vera_web_email "
                "and vera_web_password in ProviderConfiguration.extra_config."
            )
        if not self.supabase_anon_key:
            raise ProviderAuthError(
                "Supabase anon key not configured. Set supabase_anon_key "
                "in ProviderConfiguration.extra_config or "
                "VERA_SUPABASE_ANON_KEY environment variable. "
                "To find it: log into Vera Health in a browser, then run "
                "'python manage.py discover_vera_anon_key'."
            )
        return self._login()

    def _login(self) -> bool:
        url = f"{self.supabase_auth_url}/token?grant_type=password"
        headers = {
            "apikey": self.supabase_anon_key,
            "Authorization": f"Bearer {self.supabase_anon_key}",
        }
        payload = {
            "email": self.email,
            "password": self.password,
            "gotrue_meta_security": {},
        }
        try:
            resp = self._session.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                self._access_token = data.get("access_token")
                self._refresh_token = data.get("refresh_token")
                expires_in = data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 60
                self._session.headers.update({
                    "Authorization": f"Bearer {self._access_token}",
                })
                return True
            if resp.status_code == 401:
                raise ProviderAuthError(
                    f"Vera Web login failed (401): invalid credentials or anon key"
                )
            raise ProviderAuthError(
                f"Vera Web login failed ({resp.status_code}): {resp.text[:200]}"
            )
        except requests.RequestException as exc:
            raise ProviderAuthError(f"Vera Web login connection failed: {exc}") from exc

    def _ensure_auth(self):
        if self._access_token and time.time() < self._token_expires_at:
            return
        if self._refresh_token:
            if self._refresh_session():
                return
        self._login()

    def _refresh_session(self) -> bool:
        url = f"{self.supabase_auth_url}/token?grant_type=refresh_token"
        headers = {
            "apikey": self.supabase_anon_key,
            "Authorization": f"Bearer {self.supabase_anon_key}",
        }
        payload = {"refresh_token": self._refresh_token}
        try:
            resp = self._session.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                self._access_token = data.get("access_token")
                self._refresh_token = data.get("refresh_token")
                expires_in = data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 60
                self._session.headers.update({
                    "Authorization": f"Bearer {self._access_token}",
                })
                return True
        except requests.RequestException:
            pass
        return False

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            self._ensure_auth()
            resp = self._session.get(
                f"{self.web_base_url}/api/health",
                timeout=10,
                allow_redirects=False,
            )
            available = resp.status_code not in (307, 401, 403)
            return {
                "available": available,
                "latency_ms": (time.time() - t0) * 1000,
                "error": None if available else f"HTTP {resp.status_code}",
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
        self._ensure_auth()
        retmax = kwargs.get("max_results", 20)
        payload = {
            "query": query,
            "max_results": retmax,
        }
        try:
            result = self._call_api("api/search", payload)
            references = result.get("references", []) or result.get("results", [])
            return [self.normalize(ref) for ref in references]
        except ProviderError:
            return []

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        self._ensure_auth()
        payload = {"identifier": identifier, "identifier_type": id_type}
        try:
            result = self._call_api("api/evidence", payload)
            ref = result.get("reference") or result.get("result")
            if ref:
                return self.normalize(ref)
        except ProviderError:
            pass
        return None

    # ------------------------------------------------------------------ #
    # AI clinical review
    # ------------------------------------------------------------------ #
    def review_clinical_question(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> AIReviewResult:
        self._ensure_auth()
        payload: dict[str, Any] = {
            "query": question,
            "structured_output": True,
            "include_citations": True,
        }
        if context:
            payload["context"] = context

        result = self._call_api("api/ask", payload)

        summary = (
            result.get("answer")
            or result.get("summary")
            or result.get("synthesis", "")
        )

        key_findings = (
            result.get("key_findings", [])
            or result.get("findings", [])
            or []
        )

        supporting = (
            result.get("supporting_evidence", [])
            or result.get("references", [])
            or result.get("citations", [])
        )

        contradictory = (
            result.get("contradictory_evidence", [])
            or result.get("contradictions", [])
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
            source_type="vera_web",
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
    def _call_api(self, endpoint: str, payload: dict, timeout: int = 60) -> dict:
        url = f"{self.web_base_url}/{endpoint.lstrip('/')}"
        try:
            resp = self._session.post(
                url, json=payload, timeout=timeout, allow_redirects=False,
            )
            if resp.status_code in (307, 401):
                raise ProviderAuthError(
                    f"Vera Web session expired or invalid ({resp.status_code}). "
                    f"Re-authentication needed."
                )
            if resp.status_code == 429:
                raise ProviderError("Vera Web rate limit exceeded (429)")
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as exc:
            body = exc.response.text[:500] if exc.response else ""
            raise ProviderError(
                f"Vera Web API error {exc.response.status_code}: {body}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Vera Web connection failed: {exc}") from exc

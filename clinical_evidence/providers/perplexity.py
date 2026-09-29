"""Perplexity Sonar provider — AI-powered evidence retrieval."""

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


class PerplexityProvider(BaseEvidenceProvider):
    """Perplexity Sonar API provider for evidence search and synthesis."""

    @property
    def provider_type(self) -> str:
        return "perplexity"

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.api_key = (
            self.config.get("api_key")
            or os.environ.get("PERPLEXITY_API_KEY", "")
        )
        self.base_url = (
            self.config.get("api_base_url")
            or os.environ.get("PERPLEXITY_API_BASE_URL", "https://api.perplexity.ai")
        )
        self.model = self.config.get("model") or os.environ.get(
            "PERPLEXITY_MODEL", "sonar-pro"
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_structured_output=True,
            supports_ai_summary=True,
            supports_citations=True,
            max_query_length=2000,
            rate_limit_per_minute=20,
            requires_authentication=True,
        )

    def authenticate(self) -> bool:
        if not self.api_key:
            raise ProviderAuthError("Perplexity API key not configured.")
        t0 = time.time()
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.base_url}/v1/chat/completions",
                data=json.dumps({
                    "model": self.model, "messages": [
                        {"role": "user", "content": "test"},
                    ], "max_tokens": 1,
                }).encode(),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            self.authenticate()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def _chat(self, messages: list[dict], timeout: int = 120) -> dict:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2048,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"Perplexity API error {exc.code}: {exc.read().decode() if exc.fp else ''}") from exc

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        """Use Perplexity's online search to find clinical evidence."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Clinical evidence search assistant. "
                    "Return JSON array: [{title, authors, journal, "
                    "publication_date(YYYY-MM-DD), pmid, doi, abstract(brief), url}]"
                ),
            },
            {"role": "user", "content": f"Find clinical evidence about: {query}"},
        ]
        try:
            result = self._chat(messages)
        except ProviderError:
            return []
        content = (result.get("choices", [{}])[0]
                   .get("message", {}).get("content", "[]"))
        try:
            items = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            items = []
        if isinstance(items, dict):
            items = items.get("results", items.get("evidence", [items]))
        return [self.normalize(item) for item in (items if isinstance(items, list) else [items])]

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        messages = [
            {
                "role": "system",
                "content": (
                    "Clinical evidence retrieval. "
                    "Return JSON: {title, authors, journal, "
                    "publication_date, pmid, doi, abstract}"
                ),
            },
            {"role": "user", "content": f"Retrieve publication {id_type}: {identifier}"},
        ]
        try:
            result = self._chat(messages)
        except ProviderError:
            return None
        content = (result.get("choices", [{}])[0]
                   .get("message", {}).get("content", "{}"))
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return None
        return self.normalize(data) if data.get("title") else None

    def review_clinical_question(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> AIReviewResult:
        """Use Perplexity to review a clinical question with online evidence."""
        context_str = f"\nContext: {json.dumps(context)}" if context else ""
        messages = [
            {
                "role": "system",
                "content": (
                    "Clinical evidence reviewer. "
                    "Return JSON: {summary, key_findings[], limitations[], "
                    "supporting_evidence[](PMID/DOI), contradictory_evidence[](PMID/DOI), "
                    "confidence_score(0-1), recommendation_alignment} "
                    "— one of: aligns|minor_difference|major_difference|"
                    "conflicting|insufficient_evidence."
                ),
            },
            {
                "role": "user",
                "content": f"Review this clinical question: {question}{context_str}",
            },
        ]
        try:
            result = self._chat(messages)
        except ProviderError:
            return AIReviewResult(summary="Provider error during review.")
        content = (result.get("choices", [{}])[0]
                   .get("message", {}).get("content", "{}"))
        try:
            structured = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            structured = {"summary": content}
        return AIReviewResult(
            summary=structured.get("summary", ""),
            key_findings=structured.get("key_findings", []),
            limitations=structured.get("limitations", []),
            supporting_evidence=structured.get("supporting_evidence", []),
            contradictory_evidence=structured.get("contradictory_evidence", []),
            confidence_score=structured.get("confidence_score"),
            recommendation_alignment=structured.get("recommendation_alignment", ""),
            structured_data=structured,
            raw_response=json.dumps(result),
        )

    def normalize(self, raw: dict) -> EvidenceItem:
        return EvidenceItem(
            source_type="perplexity",
            title=raw.get("title", ""),
            authors=raw.get("authors", ""),
            journal=raw.get("journal", ""),
            publication_date=raw.get("publication_date"),
            pmid=raw.get("pmid", ""),
            doi=raw.get("doi", ""),
            abstract=raw.get("abstract", ""),
            url=raw.get("url", ""),
            raw_data=raw,
        )

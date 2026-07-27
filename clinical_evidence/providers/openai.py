"""OpenAI GPT provider — AI clinical reviewer fallback."""

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


class OpenAIProvider(BaseEvidenceProvider):
    """OpenAI GPT provider for AI-assisted clinical evidence synthesis."""

    @property
    def provider_type(self) -> str:
        return "openai"

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.api_key = (
            self.config.get("api_key")
            or os.environ.get("OPENAI_API_KEY", "")
        )
        self.base_url = (
            self.config.get("api_base_url")
            or os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        )
        self.model = self.config.get("model") or os.environ.get(
            "OPENAI_MODEL", "gpt-4o"
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=False,
            supports_retrieve=False,
            supports_structured_output=True,
            supports_ai_summary=True,
            max_query_length=4000,
            rate_limit_per_minute=60,
            requires_authentication=True,
        )

    def authenticate(self) -> bool:
        if not self.api_key:
            raise ProviderAuthError(
                "OpenAI API key not configured. Set OPENAI_API_KEY "
                "environment variable or configure via ProviderConfiguration."
            )
        t0 = time.time()
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as exc:
            raise ProviderAuthError(f"OpenAI auth failed: {exc}") from exc

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                json.loads(resp.read().decode())
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def _call_chat(self, messages: list[dict], timeout: int = 120) -> dict:
        import urllib.request
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 2048,
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
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
            body = exc.read().decode() if exc.fp else ""
            if exc.code == 401:
                raise ProviderAuthError("OpenAI auth failed (401)") from exc
            raise ProviderError(f"OpenAI error {exc.code}: {body}") from exc

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        return []

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        return None

    def review_clinical_question(
        self,
        question: str,
        context: dict[str, Any] | None = None,
    ) -> AIReviewResult:
        """Use GPT to synthesise and review clinical evidence."""
        system_prompt = (
            "Nephrology clinical evidence reviewer. "
            "Return JSON: {summary, key_findings[], limitations[], "
            "supporting_evidence[](PMID/DOI), contradictory_evidence[](PMID/DOI), "
            "confidence_score(0-1), recommendation_alignment}"
            " — one of: aligns|minor_difference|major_difference|"
            "conflicting|insufficient_evidence. "
            "Cite PMIDs/DOIs."
        )
        user_content = f"Clinical question: {question}"
        if context:
            user_content += f"\n\nContext: {json.dumps(context)}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        result = self._call_chat(messages)
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "{}")
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

    def validate_recommendation(
        self,
        recommendation_text: str,
        disease_id: str = "",
        guidelines: list[str] | None = None,
    ) -> AIReviewResult:
        context = {"disease_id": disease_id, "guidelines": guidelines or []}
        return self.review_clinical_question(recommendation_text, context=context)

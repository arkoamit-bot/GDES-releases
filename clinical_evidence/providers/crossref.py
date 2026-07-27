"""Crossref provider."""

import time
import urllib.parse
import urllib.request
from datetime import date

from clinical_evidence.providers.base import (
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class CrossrefProvider(BaseEvidenceProvider):
    """Fetch evidence from Crossref API (free, no token)."""

    BASE_URL = "https://api.crossref.org/works"

    @property
    def provider_type(self) -> str:
        return "crossref"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_retrieve=True,
            max_query_length=500,
            rate_limit_per_minute=50,
            requires_authentication=False,
        )

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            url = f"{self.BASE_URL}?query=cancer&rows=1"
            req = urllib.request.Request(
                url, headers={"User-Agent": "GDES-CEI (mailto:gdesteam@example.com)"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        retmax = kwargs.get("max_results", 20)
        params = urllib.parse.urlencode({
            "query": query, "rows": retmax, "sort": "relevance",
        })
        url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "GDES-CEI (mailto:gdesteam@example.com)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
        except Exception:
            return []
        items = data.get("message", {}).get("items", [])
        return [self.normalize(r) for r in items]

    def retrieve(self, identifier: str, id_type: str = "doi") -> EvidenceItem | None:
        if id_type == "doi":
            url = f"{self.BASE_URL}/{urllib.parse.quote(identifier, safe='')}"
        else:
            params = urllib.parse.urlencode({"query": identifier})
            url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "GDES-CEI (mailto:gdesteam@example.com)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
            msg = data.get("message", {})
            if id_type == "doi":
                return self.normalize(msg) if msg.get("DOI") else None
            items = msg.get("items", [])
            if items:
                return self.normalize(items[0])
        except Exception:
            pass
        return None

    def normalize(self, raw: dict) -> EvidenceItem:
        pub_date = None
        dp = raw.get("published-print", {}).get("date-parts", [[]])[0]
        if not dp:
            dp = raw.get("created", {}).get("date-parts", [[]])[0]
        if dp:
            try:
                pub_date = date(dp[0], dp[1] if len(dp) > 1 else 1, dp[2] if len(dp) > 2 else 1)
            except (ValueError, IndexError, TypeError):
                pass
        authors_list = raw.get("author", [])
        authors = "; ".join(
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in authors_list
        )
        return EvidenceItem(
            source_type="crossref",
            title=raw.get("title", [""])[0] if isinstance(raw.get("title"), list) else str(raw.get("title", "")),
            authors=authors,
            journal=raw.get("container-title", [""])[0] if isinstance(raw.get("container-title"), list) else "",
            publication_date=pub_date,
            doi=raw.get("DOI", ""),
            author_count=len(authors_list),
            raw_data=raw,
        )

"""Semantic Scholar provider."""

import time
import urllib.parse
import urllib.request
from datetime import date

from clinical_evidence.providers.base import (
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class SemanticScholarProvider(BaseEvidenceProvider):
    """Fetch evidence from Semantic Scholar API (free, no token)."""

    SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    RETRIEVE_URL = "https://api.semanticscholar.org/graph/v1/paper"

    @property
    def provider_type(self) -> str:
        return "semantic_scholar"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_retrieve=True,
            max_query_length=300,
            rate_limit_per_minute=10,
            requires_authentication=False,
        )

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            url = f"{self.SEARCH_URL}?query=cancer&limit=1"
            req = urllib.request.Request(
                url, headers={"User-Agent": "GDES-CEI"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def _fields(self) -> str:
        return "title,authors,publicationDate,journal,externalIds,abstract,citationCount,fieldsOfStudy"

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        retmax = kwargs.get("max_results", 20)
        params = urllib.parse.urlencode({
            "query": query, "limit": retmax, "fields": self._fields(),
        })
        url = f"{self.SEARCH_URL}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
        except Exception:
            return []
        results = data.get("data", [])
        return [self.normalize(r) for r in results]

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        if id_type == "pmid":
            param = f"PMID:{identifier}"
        elif id_type == "doi":
            param = f"DOI:{identifier}"
        else:
            param = identifier
        url = f"{self.RETRIEVE_URL}/{urllib.parse.quote(param)}?fields={self._fields()}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
            return self.normalize(data) if data else None
        except Exception:
            return None

    def normalize(self, raw: dict) -> EvidenceItem:
        pub_date = None
        raw_date = raw.get("publicationDate") or raw.get("publication_date")
        if raw_date:
            try:
                parts = raw_date.split("-")
                pub_date = date(int(parts[0]), int(parts[1]) if len(parts) > 1 else 1,
                                int(parts[2]) if len(parts) > 2 else 1)
            except (ValueError, IndexError, TypeError):
                pass
        ext_ids = raw.get("externalIds") or {}
        authors_list = raw.get("authors") or []
        authors = "; ".join(
            a.get("name", "") for a in authors_list if isinstance(a, dict)
        )
        journal_info = raw.get("journal")
        journal = ""
        if isinstance(journal_info, dict):
            journal = journal_info.get("name", "")
        elif isinstance(journal_info, str):
            journal = journal_info
        return EvidenceItem(
            source_type="semantic_scholar",
            title=raw.get("title", ""),
            authors=authors,
            journal=journal,
            publication_date=pub_date,
            pmid=str(ext_ids.get("PMID", "")),
            pmcid=str(ext_ids.get("PMC", "")),
            doi=str(ext_ids.get("DOI", "")),
            abstract=raw.get("abstract", ""),
            citation_count=raw.get("citationCount") or raw.get("citation_count"),
            keywords=raw.get("fieldsOfStudy", []) or [],
            raw_data=raw,
        )

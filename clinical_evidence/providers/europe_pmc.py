"""Europe PMC provider."""

import time
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

from clinical_evidence.providers.base import (
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class EuropePMCProvider(BaseEvidenceProvider):
    """Fetch evidence from Europe PMC (free API, no token)."""

    SEARCH_URL = "https://www.ebi.ac.uk/europepmc/api/search"

    @property
    def provider_type(self) -> str:
        return "europe_pmc"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_retrieve=True,
            max_query_length=500,
            rate_limit_per_minute=15,
            requires_authentication=False,
        )

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            url = f"{self.SEARCH_URL}?query=cancer&pageSize=1&format=json"
            req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        retmax = kwargs.get("max_results", 20)
        params = urllib.parse.urlencode({
            "query": query, "pageSize": retmax, "format": "json", "sort": "RELEVANCE",
        })
        url = f"{self.SEARCH_URL}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            import json
            data = json.loads(resp.read().decode())
        results = data.get("resultList", {}).get("result", [])
        return [self.normalize(r) for r in results]

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        field = "pmid" if id_type == "pmid" else "doi"
        url = f"{self.SEARCH_URL}?query={field}:{identifier}&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
            results = data.get("resultList", {}).get("result", [])
            if results:
                return self.normalize(results[0])
        except Exception:
            pass
        return None

    def normalize(self, raw: dict[str, Any]) -> EvidenceItem:
        pub_date = None
        year = raw.get("pubYear", "")
        month = raw.get("pubMonth", "")
        day = raw.get("pubDay", "")
        if year:
            try:
                pub_date = date(int(year), int(month or "1"), int(day or "1"))
            except (ValueError, TypeError):
                pass
        return EvidenceItem(
            source_type="europe_pmc",
            title=raw.get("title", "") or raw.get("titleText", ""),
            authors=raw.get("authorString", ""),
            journal=raw.get("journalTitle", "") or raw.get("bookOrReportDetails", {}).get("publisher", ""),
            publication_date=pub_date,
            pmid=str(raw.get("pmid", "") or raw.get("id", "")),
            pmcid=raw.get("pmcid", "") or raw.get("pmcId", ""),
            doi=raw.get("doi", ""),
            abstract=raw.get("abstractText", ""),
            url=raw.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", "")
            if raw.get("fullTextUrlList") else "",
            citation_count=raw.get("citedByCount"),
            journal_impact=raw.get("journalImpactFactor"),
            keywords=raw.get("keywordList", {}).get("keyword", []) if isinstance(
                raw.get("keywordList"), dict) else raw.get("keywordList", []),
            mesh_terms=[t.get("term", "") for t in raw.get("meshHeadingList", {}).get("meshHeading", [])]
            if isinstance(raw.get("meshHeadingList"), dict) else [],
            raw_data=raw,
        )

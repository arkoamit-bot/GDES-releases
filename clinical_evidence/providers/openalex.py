"""OpenAlex provider."""

import time
import urllib.parse
import urllib.request
from datetime import date

from clinical_evidence.providers.base import (
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class OpenAlexProvider(BaseEvidenceProvider):
    """Fetch evidence from OpenAlex (free, open API)."""

    BASE_URL = "https://api.openalex.org/works"

    @property
    def provider_type(self) -> str:
        return "openalex"

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
            url = f"{self.BASE_URL}?per_page=1&search=cancer&mailto=gdesteam@example.com"
            req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        retmax = kwargs.get("max_results", 20)
        params = urllib.parse.urlencode({
            "search": query, "per_page": retmax, "sort": "relevance_score:desc",
            "mailto": "gdesteam@example.com",
        })
        url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
        except Exception:
            return []
        results = data.get("results", [])
        return [self.normalize(r) for r in results]

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        if id_type == "pmid":
            filter_param = f"pmid:{identifier}"
        elif id_type == "doi":
            clean_doi = identifier.replace("https://doi.org/", "").replace("doi:", "")
            filter_param = f"doi:{clean_doi}"
        else:
            filter_param = identifier
        params = urllib.parse.urlencode({
            "filter": filter_param, "mailto": "gdesteam@example.com",
        })
        url = f"{self.BASE_URL}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                import json
                data = json.loads(resp.read().decode())
            results = data.get("results", [])
            if results:
                return self.normalize(results[0])
        except Exception:
            pass
        return None

    def normalize(self, raw: dict) -> EvidenceItem:
        pub_date = None
        raw_date = raw.get("publication_date")
        if raw_date:
            try:
                pub_date = date.fromisoformat(raw_date)
            except (ValueError, TypeError):
                pass
        authors_list = raw.get("authorships") or []
        authors = "; ".join(
            a.get("author", {}).get("display_name", "")
            for a in authors_list if isinstance(a, dict)
        )
        ids = raw.get("ids") or {}
        return EvidenceItem(
            source_type="openalex",
            title=raw.get("title", ""),
            authors=authors,
            journal=(raw.get("host_venue") or raw.get("primary_location") or {}).get("display_name", "")
            if raw.get("host_venue") or raw.get("primary_location") else "",
            publication_date=pub_date,
            pmid=str(ids.get("pmid", "")).replace("https://pubmed.ncbi.nlm.nih.gov/", ""),
            doi=str(ids.get("doi", "")).replace("https://doi.org/", ""),
            abstract=raw.get("abstract", "") or (raw.get("abstract_inverted_index") and " ".join(
                list(raw["abstract_inverted_index"].keys())[:100]) or ""),
            citation_count=raw.get("cited_by_count"),
            keywords=[c.get("display_name", "") for c in raw.get("concepts", [])[:10]],
            relevance_score=raw.get("relevance_score"),
            raw_data=raw,
        )

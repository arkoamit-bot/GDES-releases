"""PubMed provider via NCBI E-utilities."""

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime

from clinical_evidence.exceptions import ProviderError
from clinical_evidence.providers.base import (
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)


class PubMedProvider(BaseEvidenceProvider):
    """Fetch evidence from PubMed via NCBI E-utilities (free, no token)."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    @property
    def provider_type(self) -> str:
        return "pubmed"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_search=True,
            supports_retrieve=True,
            supports_structured_output=False,
            max_query_length=300,
            rate_limit_per_minute=10,
            requires_authentication=False,
        )

    def authenticate(self) -> bool:
        return True

    def health_check(self) -> dict:
        t0 = time.time()
        try:
            url = f"{self.BASE_URL}/esearch.fcgi?db=pubmed&retmax=1&term=cancer"
            req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return {"available": True, "latency_ms": (time.time() - t0) * 1000, "error": None}
        except Exception as exc:
            return {"available": False, "latency_ms": (time.time() - t0) * 1000, "error": str(exc)}

    def _esearch(self, term: str, retmax: int = 20) -> list[str]:
        params = urllib.parse.urlencode({
            "db": "pubmed", "term": term, "retmax": retmax,
            "retmode": "json", "sort": "relevance",
        })
        url = f"{self.BASE_URL}/esearch.fcgi?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode()
        import json
        parsed = json.loads(data)
        return parsed.get("esearchresult", {}).get("idlist", [])

    def _efetch(self, pmid: str) -> dict | None:
        params = urllib.parse.urlencode({
            "db": "pubmed", "id": pmid, "retmode": "xml",
        })
        url = f"{self.BASE_URL}/efetch.fcgi?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GDES-CEI"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        article = root.find(".//PubmedArticle")
        if article is None:
            return None
        return self._parse_article(article)

    def _parse_article(self, article: ET.Element) -> dict:
        medline = article.find(".//MedlineCitation")
        if medline is None:
            return {}
        result = {"pmid": medline.findtext("PMID", "")}

        article_elem = medline.find(".//Article")
        if article_elem is not None:
            result["title"] = article_elem.findtext("ArticleTitle", "")
            authors = []
            for author in article_elem.findall(".//Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {fore}".strip())
            result["authors"] = "; ".join(authors)

            journal = article_elem.findtext("Journal/Title", "")
            result["journal"] = journal

            pub_date = article_elem.find(".//Journal/JournalIssue/PubDate")
            if pub_date is not None:
                year = pub_date.findtext("Year", "")
                month = pub_date.findtext("Month", "")
                day = pub_date.findtext("Day", "")
                if year:
                    try:
                        result["publication_date"] = date(
                            int(year),
                            int(month) if month.isdigit() else 1,
                            int(day) if day.isdigit() else 1,
                        )
                    except (ValueError, TypeError):
                        result["publication_date"] = None

        result["abstract"] = ""
        abstract_elem = article_elem.find(".//Abstract/AbstractText") if article_elem is not None else None
        if abstract_elem is not None:
            parts = []
            for elem in article_elem.findall(".//Abstract/AbstractText"):
                label = elem.get("Label", "")
                text = "".join(elem.itertext())
                if label:
                    parts.append(f"{label}: {text}")
                else:
                    parts.append(text)
            result["abstract"] = "\n".join(parts)

        mesh = []
        for mh in medline.findall(".//MeshHeading"):
            desc = mh.find("DescriptorName")
            if desc is not None:
                mesh.append(desc.text or "")
        result["mesh_terms"] = mesh

        return result

    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        retmax = kwargs.get("max_results", 20)
        pmids = self._esearch(query, retmax=retmax)
        items = []
        for pmid in pmids:
            try:
                raw = self._efetch(pmid)
                if raw:
                    items.append(self.normalize(raw))
            except Exception:
                continue
        return items

    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        raw = self._efetch(identifier)
        if raw:
            return self.normalize(raw)
        return None

    def normalize(self, raw: dict) -> EvidenceItem:
        pub_date = raw.get("publication_date")
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.strptime(pub_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pub_date = None
        return EvidenceItem(
            source_type="pubmed",
            title=raw.get("title", ""),
            authors=raw.get("authors", ""),
            journal=raw.get("journal", ""),
            publication_date=pub_date,
            pmid=str(raw.get("pmid", "")),
            abstract=raw.get("abstract", ""),
            mesh_terms=raw.get("mesh_terms", []),
            raw_data=raw,
        )

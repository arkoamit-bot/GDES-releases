"""V8 Layer 5 — online medical evidence retrieval (gated, approved-source only).

DISABLED BY DEFAULT. The pilot is offline-first; this only runs when
`AI_ONLINE_EVIDENCE_ENABLED` is set (GDES_AI_ONLINE_EVIDENCE=1) AND a clinician
explicitly requests it. Guardrails:

- Only an **approved source** is queried: PubMed via NCBI E-utilities (a free,
  no-API-key, government service). No uncontrolled web search, no social media,
  no blogs, no AI-generated sites, no LLM.
- **No patient data leaves the machine.** Callers pass a text query (e.g. a
  disease name + topic); this module never accepts or forwards PHI.
- It returns citations for a clinician to read — it does NOT generate or alter
  recommendations, and it never touches the production knowledge base.

Layers 6 (RAG), 7 (multi-agent LLM) and 11 (guideline monitoring) additionally
require an LLM and are intentionally NOT implemented here — see
GDES_V8_GAP_ANALYSIS_AND_IMPLEMENTATION.md for their design and prerequisites.
"""
from __future__ import annotations

APPROVED_SOURCES = ("PubMed / PubMed Central (NCBI)",)


class EvidenceRetrievalDisabled(RuntimeError):
    """Raised when online evidence retrieval is not enabled."""


def is_enabled() -> bool:
    from django.conf import settings
    return bool(getattr(settings, "AI_ONLINE_EVIDENCE_ENABLED", False))


def _contains_possible_phi(query: str) -> bool:
    """Cheap guard: reject queries that look like they carry identifiers."""
    import re
    q = query or ""
    # long digit runs (MRN/phone/ID), emails.
    return bool(re.search(r"\d{6,}", q) or re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", q))


def search_evidence(query: str, max_results: int = 5, timeout: int = 15) -> list[dict]:
    """Search PubMed for `query`. Returns [{pmid, title, journal, year, url}].

    Raises EvidenceRetrievalDisabled if the feature is off. Raises ValueError if
    the query looks like it contains identifiers (defence in depth against PHI).
    """
    if not is_enabled():
        raise EvidenceRetrievalDisabled(
            "Online evidence retrieval is disabled (offline pilot). Set "
            "GDES_AI_ONLINE_EVIDENCE=1 to enable; it queries only PubMed and "
            "never sends patient data.")
    query = (query or "").strip()
    if not query:
        return []
    if _contains_possible_phi(query):
        raise ValueError("Query rejected: it appears to contain identifiers. "
                         "Search by disease/topic only, never patient details.")

    import json
    import urllib.parse
    import urllib.request

    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    esearch = (f"{base}/esearch.fcgi?db=pubmed&retmode=json&retmax={int(max_results)}"
               f"&term={urllib.parse.quote(query)}")
    req = urllib.request.Request(esearch, headers={"User-Agent": "GDES-EvidenceLookup"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed host)
        ids = json.loads(resp.read()).get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    esum = f"{base}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}"
    req = urllib.request.Request(esum, headers={"User-Agent": "GDES-EvidenceLookup"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        result = json.loads(resp.read()).get("result", {})

    out = []
    for pmid in ids:
        item = result.get(pmid, {})
        out.append({
            "pmid": pmid,
            "title": item.get("title", ""),
            "journal": item.get("fulljournalname") or item.get("source", ""),
            "year": (item.get("pubdate", "") or "")[:4],
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    return out

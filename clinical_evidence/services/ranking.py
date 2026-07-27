"""Evidence ranking engine — scores and sorts evidence items by clinical relevance.

Scoring factors (Phase 6 — Clinical Relevance, not search relevance):
- Guideline citation
- Meta-analysis / RCT / Systematic review
- Journal quality (citation count as proxy)
- Kidney/nephrology relevance
- Publication recency
- Disease specificity
- Sample size
- Evidence level
"""

import math
import re
from datetime import date, datetime

from clinical_evidence.constants import EvidenceLevel
from clinical_evidence.providers.base import EvidenceItem

_LEVEL_SCORE = {
    EvidenceLevel.META_ANALYSIS: 100,
    EvidenceLevel.RCT: 90,
    EvidenceLevel.SYSTEMATIC_REVIEW: 85,
    EvidenceLevel.COHORT: 70,
    EvidenceLevel.CASE_CONTROL: 60,
    EvidenceLevel.CASE_CONTROL_INDIV: 55,
    EvidenceLevel.CASE_SERIES: 40,
    EvidenceLevel.EXPERT_OPINION: 20,
    EvidenceLevel.GUIDELINE: 95,
    EvidenceLevel.FDA_ALERT: 80,
}

_DESIGN_SCORE = {
    "meta_analysis": 100,
    "systematic_review": 90,
    "rct": 85,
    "cohort_prospective": 70,
    "cohort_retrospective": 60,
    "case_control": 55,
    "cross_sectional": 45,
    "case_series": 35,
    "case_report": 20,
    "guideline": 95,
    "fda_alert": 80,
}

# Kidney/nephrology-relevant journal keywords (lowercase substring match)
_KIDNEY_JOURNALS = {
    "kidney", "nephrol", "renal", "dialysis", "transplant",
    "glomerul", "kidney international", "clin j am soc nephrol",
    "nephrol dial transplant", "bmc nephrol", "am j kidney dis",
    "kidney blood press res",
}

# Nephrology-relevant MeSH / keyword terms
_KIDNEY_KEYWORDS = {
    "kidney", "renal", "nephrol", "glomerulonephritis", "glomerular",
    "proteinuria", "hematuria", "ckd", "chronic kidney",
    "dialysis", "transplant", "biopsy", "igad", "lupus nephritis",
    "fsgs", "membranous", "vasculitis", "anca", "anti-gbm",
}


def score_item(
    item: EvidenceItem,
    disease_id: str = "",
    guideline_relevance: float = 0.5,
) -> float:
    """Compute a composite clinical-relevance score (0-100) for an evidence item.

    Weights reflect clinical value, not search relevance:
    - Evidence level (25%): meta-analysis > RCT > cohort > case
    - Study design quality (15%)
    - Recency (15%): last 2 years gets full score, decays after
    - Citation impact (10%): log-scaled
    - Kidney relevance (15%): does it mention nephrology topics?
    - Disease specificity (10%): matches disease_id
    - Sample size (5%): larger = more reliable
    - Provider relevance (5%): from the search provider
    """
    score = 50.0

    # 1. Evidence level (25%)
    if item.evidence_level:
        level_score = _LEVEL_SCORE.get(item.evidence_level, 30)
        score += level_score * 0.25

    # 2. Study design (15%)
    if item.study_design:
        design_score = _DESIGN_SCORE.get(item.study_design, 30)
        score += design_score * 0.15

    # 3. Recency (15%) — last 2 years gets full marks, then decays
    if item.publication_date:
        try:
            if isinstance(item.publication_date, str):
                pub = datetime.strptime(item.publication_date, "%Y-%m-%d").date()
            else:
                pub = item.publication_date
            years_old = (date.today() - pub).days / 365.25
            if years_old <= 2:
                recency = 100.0
            elif years_old <= 5:
                recency = 80.0 - (years_old - 2) * 10
            else:
                recency = max(0, 50.0 - (years_old - 5) * 5)
            score += recency * 0.15
        except (ValueError, TypeError):
            pass

    # 4. Citation impact (10%)
    if item.citation_count is not None and item.citation_count > 0:
        citation_score = min(50, math.log10(item.citation_count + 1) * 15)
        score += citation_score * 0.10

    # 5. Kidney relevance (15%) — new in Phase 6
    kidney_score = _kidney_relevance_score(item)
    score += kidney_score * 0.15

    # 6. Disease specificity (10%) — new in Phase 6
    if disease_id:
        specificity = _disease_specificity_score(item, disease_id)
        score += specificity * 0.10

    # 7. Sample size (5%)
    if item.sample_size is not None and item.sample_size > 0:
        sample_score = min(20, math.log10(item.sample_size) * 5)
        score += sample_score * 0.05

    # 8. Provider relevance (5%)
    if item.relevance_score is not None:
        score += item.relevance_score * 100 * 0.05

    return min(100, max(0, score))


def _kidney_relevance_score(item: EvidenceItem) -> float:
    """Score how relevant an item is to nephrology (0-100)."""
    score = 0.0
    text = f"{item.title} {item.journal} {' '.join(item.keywords)} {' '.join(item.mesh_terms)}".lower()

    # Journal match
    journal_lower = (item.journal or "").lower()
    for kw in _KIDNEY_JOURNALS:
        if kw in journal_lower:
            score += 40.0
            break

    # Keyword/title match
    for kw in _KIDNEY_KEYWORDS:
        if kw in text:
            score += 10.0

    return min(100.0, score)


def _disease_specificity_score(item: EvidenceItem, disease_id: str) -> float:
    """Score how specific an item is to the given disease (0-100)."""
    disease_name = disease_id.replace("_", " ").replace("-", " ").lower()
    text = f"{item.title} {' '.join(item.keywords)} {' '.join(item.mesh_terms)}".lower()

    # Exact disease name match in title is highest signal
    if disease_name in (item.title or "").lower():
        return 100.0

    # Disease terms appear in keywords/mesh
    disease_terms = [t for t in disease_name.split() if len(t) > 3]
    matches = sum(1 for t in disease_terms if t in text)
    if disease_terms:
        return min(100.0, (matches / len(disease_terms)) * 80.0)

    return 0.0


def rank_items(items: list[EvidenceItem], **context) -> list[EvidenceItem]:
    """Rank a list of evidence items by clinical-relevance score, descending."""
    scored = [(score_item(item, **context), item) for item in items]
    scored.sort(key=lambda x: x[0], reverse=True)
    for idx, (s, item) in enumerate(scored):
        item.relevance_score = round(s / 100, 4)
    return [item for _, item in scored]

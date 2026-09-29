"""Evidence fusion engine — deduplicates and fuses results into a package."""

import logging
from difflib import SequenceMatcher
from typing import Any

from clinical_evidence.models import (
    EvidencePackage,
    EvidenceQuery,
    EvidenceResult,
)
from clinical_evidence.providers.base import AIReviewResult, EvidenceItem
from clinical_evidence.services.ranking import rank_items
from clinical_evidence.services.citation import generate_all as generate_citations

logger = logging.getLogger("bgddr.evidence.fusion")


def _is_duplicate(a: EvidenceResult, b: EvidenceResult, threshold: float = 0.85) -> bool:
    """Check if two results are duplicates via PMID, DOI, or title similarity."""
    if a.pmid and b.pmid and a.pmid == b.pmid:
        return True
    if a.doi and b.doi and a.doi.lower() == b.doi.lower():
        return True
    if a.title and b.title:
        ratio = SequenceMatcher(None, a.title.lower(), b.title.lower()).ratio()
        return ratio >= threshold
    return False


def _evidence_result_to_item(r: EvidenceResult) -> EvidenceItem:
    """Convert a persisted EvidenceResult to an EvidenceItem dataclass for ranking."""
    return EvidenceItem(
        source_type=r.source_type,
        title=r.title,
        authors=r.authors,
        journal=r.journal,
        publication_date=r.publication_date,
        pmid=r.pmid,
        pmcid=r.pmcid,
        doi=r.doi,
        abstract=r.abstract,
        url=r.url,
        evidence_level=r.evidence_level,
        study_design=r.study_design,
        citation_count=r.citation_count,
        journal_impact=r.journal_impact,
        sample_size=r.sample_size,
        keywords=r.keywords or [],
        mesh_terms=r.mesh_terms or [],
        relevance_score=r.relevance_score,
        raw_data=r.raw_data or {},
    )


def deduplicate(results: list[EvidenceResult]) -> list[EvidenceResult]:
    """Remove duplicate results, keeping the highest-ranked."""
    unique: list[EvidenceResult] = []
    for result in results:
        if not any(_is_duplicate(result, u) for u in unique):
            unique.append(result)
    return unique


def fuse(
    query: EvidenceQuery,
    ai_summary: str = "",
    ai_confidence: float | None = None,
    ai_provider: str = "",
    ask_ai: bool = True,
) -> EvidencePackage:
    """Fuse all results for a query into a single evidence package.

    When *ask_ai* is True (default), the orchestrator attempts to get an
    AI‑generated summary from the best available reviewer (GPT-5 first,
    Vera fallback). That summary is used as the package's clinical
    synthesis text.
    """
    results = list(query.results.all().order_by("-relevance_score"))
    unique = deduplicate(results)
    evidence_items = [_evidence_result_to_item(r) for r in unique]
    ranked = rank_items(evidence_items)
    # propagate ranked scores back to the EvidenceResult instances
    score_map = {i.pmid or i.doi or i.title: i.relevance_score for i in ranked}
    for r in unique:
        key = r.pmid or r.doi or r.title
        r.relevance_score = score_map.get(key, r.relevance_score)

    supporting = [r for r in unique if (r.relevance_score or 0) >= 0.4]
    contradictory = [r for r in unique if (r.relevance_score or 0) < 0.2]
    neutral = [r for r in unique if r not in supporting and r not in contradictory]

    if ask_ai and not ai_summary:
        result = _synthesise_ai_summary(query, supporting, contradictory)
        if result:
            ai_summary = result.summary
            ai_confidence = result.confidence_score
            ai_provider = result.provider_type

    package = EvidencePackage.objects.create(
        query=query,
        ai_summary=ai_summary or "",
        ai_confidence=ai_confidence,
        ai_provider=ai_provider,
    )
    package.supporting_results.set(supporting)
    package.contradictory_results.set(contradictory)
    package.neutral_results.set(neutral)

    _generate_package_citations(package)
    return package


def _synthesise_ai_summary(
    query: EvidenceQuery,
    supporting: list[EvidenceResult],
    contradictory: list[EvidenceResult],
) -> AIReviewResult | None:
    """Use the best available AI reviewer to generate a clinical evidence summary.

    Returns the AIReviewResult so the caller can persist summary/confidence
    on the EvidencePackage.
    """
    from clinical_evidence.services.orchestrator import get_ai_reviewer

    reviewer = get_ai_reviewer()
    if reviewer is None:
        return None

    context = {
        "supporting_count": len(supporting),
        "contradictory_count": len(contradictory),
        "supporting_titles": [r.title[:200] for r in supporting[:5]],
        "contradictory_titles": [r.title[:200] for r in contradictory[:3]],
    }
    question = (
        f"Summarise the clinical evidence for: {query.query_text}. "
        f"{query.disease_id or ''}"
    )
    try:
        review = reviewer.review_clinical_question(question, context=context)
        review.provider_type = reviewer.provider_type
        return review
    except Exception as exc:
        logger.warning("AI summary generation failed: %s", exc)
        return None


def _generate_package_citations(package: EvidencePackage) -> None:
    """Generate citation formats for all results in a package."""
    from clinical_evidence.models import EvidenceCitation

    all_results = list(package.supporting_results.all()) + \
        list(package.contradictory_results.all()) + \
        list(package.neutral_results.all())

    for result in all_results:
        if hasattr(result, "citation") and result.citation:
            continue
        try:
            citations = generate_citations(
                authors=result.authors,
                publication_date=result.publication_date,
                title=result.title,
                journal=result.journal,
                doi=result.doi,
                pmid=result.pmid,
                abstract=result.abstract,
            )
            EvidenceCitation.objects.update_or_create(
                result=result,
                defaults=citations,
            )
        except Exception as exc:
            logger.warning("Citation generation failed for result %s: %s", result.pk, exc)

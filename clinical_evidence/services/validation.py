"""Recommendation validation engine — compares GDES recommendations against evidence."""

import logging
from typing import Any

from clinical_evidence.constants import ValidationOutcome
from clinical_evidence.models import (
    EvidencePackage,
    GuidelineRecommendation,
    RecommendationValidation,
)
from clinical_evidence.providers.base import AIReviewResult

logger = logging.getLogger("bgddr.evidence.validation")


def validate_recommendation(
    recommendation_text: str,
    gdes_recommendation,
    package: EvidencePackage | None = None,
    encountered_at=None,
    ai_review: AIReviewResult | None = None,
) -> RecommendationValidation:
    """Validate a GDES recommendation against retrieved evidence.

    Uses AI review when available, falls back to guideline matching.
    """
    outcome = ValidationOutcome.PENDING
    confidence = None
    matched_guideline = None
    summary = ""
    details: dict[str, Any] = {}

    if ai_review:
        alignment = ai_review.recommendation_alignment
        outcome = _alignment_to_outcome(alignment)
        confidence = int((ai_review.confidence_score or 0.5) * 100) if ai_review.confidence_score else None
        summary = ai_review.summary
        details = {
            "key_findings": ai_review.key_findings,
            "supporting": ai_review.supporting_evidence,
            "contradictory": ai_review.contradictory_evidence,
            "ai_confidence": ai_review.confidence_score,
        }
    elif package:
        supporting = package.supporting_results.count()
        contradictory = package.contradictory_results.count()
        if supporting > contradictory:
            outcome = ValidationOutcome.VERIFIED
        elif contradictory > supporting:
            outcome = ValidationOutcome.MAJOR_DIFFERENCE
        else:
            outcome = ValidationOutcome.MINOR_DIFFERENCE
        total = supporting + contradictory
        confidence = int((supporting / max(total, 1)) * 100) if total > 0 else 50
        summary = (
            f"{supporting} supporting, {contradictory} contradictory studies found."
        )
        matched_guideline = _match_guideline(recommendation_text)

    if matched_guideline:
        details["matched_guideline"] = str(matched_guideline.recommendation_id)
        details["guideline_source"] = matched_guideline.guideline_source

    validation = RecommendationValidation.objects.create(
        gdes_recommendation=gdes_recommendation,
        package=package,
        outcome=outcome,
        confidence_score=confidence,
        matched_guideline=matched_guideline,
        summary=summary or "No evidence available for validation.",
        details=details,
        encountered_at=encountered_at,
        validated_by="ai" if ai_review else "system",
    )

    _check_for_contradictions(validation, package)
    return validation


def _alignment_to_outcome(alignment: str) -> str:
    mapping = {
        "aligns": ValidationOutcome.VERIFIED,
        "minor_difference": ValidationOutcome.MINOR_DIFFERENCE,
        "major_difference": ValidationOutcome.MAJOR_DIFFERENCE,
        "conflicting": ValidationOutcome.CONFLICTING,
        "insufficient_evidence": ValidationOutcome.UNVERIFIABLE,
    }
    return mapping.get(alignment, ValidationOutcome.PENDING)


def _match_guideline(text: str) -> GuidelineRecommendation | None:
    """Find a matching guideline recommendation by keyword overlap."""
    from clinical_evidence.services.contradiction import extract_keywords

    keywords = extract_keywords(text)
    matches = []
    for guideline in GuidelineRecommendation.objects.filter(is_active=True):
        g_keywords = set(extract_keywords(guideline.recommendation_text))
        overlap = len(keywords & g_keywords)
        if overlap > 0:
            matches.append((overlap, guideline))
    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1]
    return None


def _check_for_contradictions(
    validation: RecommendationValidation,
    package: EvidencePackage | None,
) -> None:
    """Auto-create conflict records if contradictory evidence is significant."""
    if not package:
        return
    contradictory = package.contradictory_results.count()
    if contradictory >= 2:
        from clinical_evidence.models import EvidenceConflict
        EvidenceConflict.objects.create(
            package=package,
            severity="high" if contradictory >= 5 else "medium",
            conflict_type="evidence_contradiction",
            title=f"Contradictory evidence for recommendation #{validation.gdes_recommendation_id}",
            description=(
                f"{contradictory} contradictory studies found vs "
                f"{package.supporting_results.count()} supporting."
            ),
        )

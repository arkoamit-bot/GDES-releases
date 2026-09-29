"""Contradiction detection engine — identifies conflicting evidence."""

import logging
import re
from typing import Any

from clinical_evidence.constants import ConflictSeverity
from clinical_evidence.models import (
    EvidenceAlert,
    EvidenceConflict,
    EvidenceResult,
    GuidelineRecommendation,
    KnowledgeGap,
)

logger = logging.getLogger("bgddr.evidence.contradiction")


def extract_keywords(text: str) -> set[str]:
    """Extract lowercase keywords from text."""
    return set(
        w.lower().rstrip(".,;:!?") for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)
    )


def detect_contradictions(
    results: list[EvidenceResult],
    disease_id: str = "",
) -> list[EvidenceConflict]:
    """Detect contradictions among a set of evidence results."""
    conflicts: list[EvidenceConflict] = []

    if len(results) < 2:
        return conflicts

    for i, a in enumerate(results):
        for b in results[i + 1:]:
            severity = _compare_results(a, b)
            if severity:
                conflict = EvidenceConflict.objects.create(
                    severity=severity,
                    conflict_type="evidence_contradiction",
                    title=_conflict_title(a, b),
                    description=_conflict_description(a, b, severity),
                    affected_disease=disease_id,
                )
                conflict.supporting_results.add(a)
                conflict.contradictory_results.add(b)
                conflicts.append(conflict)

    return conflicts


def detect_guideline_contradictions(
    results: list[EvidenceResult],
    disease_id: str = "",
) -> list[EvidenceConflict]:
    """Detect contradictions between new evidence and active guidelines."""
    conflicts: list[EvidenceConflict] = []
    guidelines = GuidelineRecommendation.objects.filter(
        is_active=True,
        disease_id=disease_id,
    )
    for guideline in guidelines:
        g_keywords = extract_keywords(guideline.recommendation_text)
        for result in results:
            r_keywords = extract_keywords(f"{result.title} {result.abstract}")
            overlap = len(g_keywords & r_keywords)
            if overlap < 3:
                continue
            if _is_contradictory_tone(f"{result.title} {result.abstract}"):
                conflict = EvidenceConflict.objects.create(
                    severity=ConflictSeverity.HIGH,
                    conflict_type="guideline_contradiction",
                    title=f"New evidence contradicts {guideline.guideline_source} "
                          f"{guideline.recommendation_id}",
                    description=(
                        f"Study '{result.title[:100]}' may contradict guideline "
                        f"{guideline.recommendation_id} from {guideline.guideline_source}. "
                        f"PMID: {result.pmid}" if result.pmid else ""
                    ),
                    affected_disease=disease_id,
                    affected_guideline=guideline,
                )
                conflict.contradictory_results.add(result)
                conflicts.append(conflict)
    return conflicts


def _compare_results(a: EvidenceResult, b: EvidenceResult) -> str | None:
    """Compare two results and return severity if contradictory."""
    a_conclusion = _extract_conclusion(f"{a.title} {a.abstract}")
    b_conclusion = _extract_conclusion(f"{b.title} {b.abstract}")
    if not a_conclusion or not b_conclusion:
        return None
    contradictory_pairs = [
        ({"effective", "beneficial", "improves", "reduces"},
         {"ineffective", "harmful", "worsens", "increases"}),
        ({"superior", "better", "more effective"},
         {"inferior", "worse", "less effective"}),
        ({"recommend", "should", "indicated"},
         {"not recommend", "should not", "contraindicated"}),
    ]
    for pos_words, neg_words in contradictory_pairs:
        a_pos = bool(a_conclusion & pos_words)
        a_neg = bool(a_conclusion & neg_words)
        b_pos = bool(b_conclusion & pos_words)
        b_neg = bool(b_conclusion & neg_words)
        if (a_pos and b_neg) or (a_neg and b_pos):
            return ConflictSeverity.MEDIUM
    return None


def _extract_conclusion(text: str) -> set[str]:
    """Extract conclusion-oriented keywords from text."""
    keywords = extract_keywords(text)
    conclusion_indicators = {
        "effective", "ineffective", "beneficial", "harmful",
        "superior", "inferior", "improves", "worsens", "reduces",
        "increases", "recommend", "contraindicated", "safe", "unsafe",
        "significant", "nonsignificant", "better", "worse",
    }
    return keywords & conclusion_indicators


def _is_contradictory_tone(text: str) -> bool:
    """Check if text has a contradictory tone vs established guidelines."""
    negated = re.search(
        r"(no\s+benefit|not\s+effective|no\s+evidence|contraindicated|"
        r"should\s+not|does\s+not\s+reduce|increased\s+risk|higher\s+mortality|unsafe)",
        text.lower(),
    )
    return bool(negated)


def _conflict_title(a: EvidenceResult, b: EvidenceResult) -> str:
    a_short = a.title[:60] if a.title else f"PMID:{a.pmid}"
    b_short = b.title[:60] if b.title else f"PMID:{b.pmid}"
    return f"Contradiction: {a_short} vs {b_short}"


def _conflict_description(
    a: EvidenceResult, b: EvidenceResult, severity: str,
) -> str:
    return (
        f"Potential contradiction detected between two evidence items "
        f"(severity: {severity}). "
        f"[1] {a.title} (PMID: {a.pmid}, DOI: {a.doi}) "
        f"[2] {b.title} (PMID: {b.pmid}, DOI: {b.doi})"
    )


def create_alert_for_conflict(conflict: EvidenceConflict) -> EvidenceAlert:
    return EvidenceAlert.objects.create(
        alert_type="contradiction",
        severity=conflict.severity,
        title=conflict.title,
        description=conflict.description,
        disease_id=conflict.affected_disease,
    )


def identify_knowledge_gap(
    disease_id: str,
    gap_type: str,
    title: str,
    description: str,
    results: list[EvidenceResult] | None = None,
    priority: str = "medium",
) -> KnowledgeGap:
    """Create a knowledge gap record."""
    gap = KnowledgeGap.objects.create(
        disease_id=disease_id,
        gap_type=gap_type,
        title=title,
        description=description,
        priority=priority,
    )
    if results:
        gap.evidence_results.set(results)
    return gap

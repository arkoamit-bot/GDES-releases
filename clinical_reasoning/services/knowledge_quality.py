"""Knowledge Quality Framework — rule quality scoring, conflict detection, and coverage analysis."""
from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from clinical_reasoning.json_util import json_safe

logger = logging.getLogger(__name__)


def score_rule_quality(entry) -> dict:
    """Score a single KnowledgeBaseEntry on quality dimensions.

    Returns scores 0-100 for: completeness, clarity, evidence, testability, overall.
    """
    rule_data = entry.rule_data or {}

    completeness = _score_completeness(entry, rule_data)
    clarity = _score_clarity(rule_data)
    evidence = _score_evidence(entry)
    testability = _score_testability(rule_data)

    overall = round((completeness + clarity + evidence + testability) / 4)

    return {
        "entry_id": entry.entry_id,
        "disease_id": entry.disease_id,
        "completeness": completeness,
        "clarity": clarity,
        "evidence": evidence,
        "testability": testability,
        "overall": overall,
        "grade": _quality_grade(overall),
    }


def _score_completeness(entry, rule_data: dict) -> int:
    score = 50
    if entry.disease_id:
        score += 10
    if entry.source:
        score += 10
    if entry.evidence_grade and entry.evidence_grade != "NG":
        score += 10
    if rule_data.get("conditions"):
        score += 10
    if rule_data.get("explanation"):
        score += 10
    return min(score, 100)


def _score_clarity(rule_data: dict) -> int:
    score = 50
    explanation = rule_data.get("explanation", "")
    if len(explanation) > 20:
        score += 15
    if len(explanation) > 100:
        score += 10
    conditions = rule_data.get("conditions", [])
    if conditions:
        if len(conditions) <= 5:
            score += 15
        else:
            score += 5
    if rule_data.get("weight", 0) != 0:
        score += 10
    return min(score, 100)


def _score_evidence(entry) -> int:
    grade_map = {"1": 100, "2": 75, "OP": 50, "NG": 25}
    base = grade_map.get(entry.evidence_grade, 25)
    if entry.source_id:
        base += 10
    return min(base, 100)


def _score_testability(rule_data: dict) -> int:
    conditions = rule_data.get("conditions", [])
    if not conditions:
        return 30
    score = 50
    for c in conditions:
        field = c.get("field", "")
        operator = c.get("operator", "")
        if field and operator:
            score += 10
    return min(score, 100)


def _quality_grade(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def detect_rule_conflicts(entries=None) -> list[dict]:
    """Detect conflicting rules for the same disease."""
    from knowledge.models import KnowledgeBaseEntry

    if entries is None:
        entries = KnowledgeBaseEntry.objects.filter(
            status=KnowledgeBaseEntry.Status.ACTIVE,
        ).select_related("source")

    conflicts = []
    by_disease: dict[str, list] = {}
    for e in entries:
        by_disease.setdefault(e.disease_id, []).append(e)

    for disease_id, group in by_disease.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                conflict = _check_pair_conflict(group[i], group[j])
                if conflict:
                    conflicts.append(conflict)

    return conflicts


def _check_pair_conflict(e1, e2) -> dict | None:
    """Check if two entries for the same disease have contradictory conditions."""
    r1 = e1.rule_data or {}
    r2 = e2.rule_data or {}
    conditions1 = r1.get("conditions", [])
    conditions2 = r2.get("conditions", [])

    for c1 in conditions1:
        for c2 in conditions2:
            if c1.get("field") == c2.get("field"):
                if _is_contradictory(c1, c2):
                    return {
                        "entry_id_1": e1.entry_id,
                        "entry_id_2": e2.entry_id,
                        "disease_id": e1.disease_id,
                        "field": c1.get("field"),
                        "condition_1": c1,
                        "condition_2": c2,
                        "severity": "medium",
                        "message": f"Contradictory conditions on field '{c1.get('field')}'",
                    }
    return None


def _is_contradictory(c1: dict, c2: dict) -> bool:
    ops_contradict = {
        ("eq", "neq"): True,
        ("gt", "lt"): True,
        ("gt", "lte"): True,
        ("gte", "lt"): True,
        ("gte", "lte"): False,
        ("exists", "not_exists"): True,
    }
    return ops_contradict.get((c1.get("operator"), c2.get("operator")), False)


def analyze_coverage(entries=None) -> dict:
    """Analyze knowledge base coverage across diseases and sources."""
    from knowledge.models import KnowledgeBaseEntry

    if entries is None:
        entries = KnowledgeBaseEntry.objects.filter(
            status=KnowledgeBaseEntry.Status.ACTIVE,
        )

    by_disease: Counter = Counter()
    by_source: Counter = Counter()
    by_grade: Counter = Counter()

    for e in entries:
        by_disease[e.disease_id] += 1
        by_source[e.source.abbreviation if e.source else "unknown"] += 1
        by_grade[e.evidence_grade or "NG"] += 1

    return {
        "total_rules": len(entries),
        "unique_diseases": len(by_disease),
        "unique_sources": len(by_source),
        "rules_per_disease": dict(by_disease.most_common()),
        "rules_per_source": dict(by_source.most_common()),
        "rules_per_grade": dict(by_grade.most_common()),
    }

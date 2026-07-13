"""Rule tester — test rules against known patient cases for validation.

Supports both real patients and synthetic feature dict inputs.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from .services import evaluate_entry, extract_patient_features
from .models import KnowledgeBaseEntry, RuleTestResult


def test_rule(
    entry: KnowledgeBaseEntry,
    features: dict | None = None,
    patient=None,
    expected_score: float | None = None,
    test_name: str = "",
) -> RuleTestResult:
    """Test a single rule against features or a real patient.

    Returns a RuleTestResult with actual_score and matched status.
    """
    if features is None and patient is not None:
        features = extract_patient_features(patient)
    features = features or {}

    result = evaluate_entry(entry, features)
    actual = result.total_score

    if expected_score is not None:
        matched = abs(actual - expected_score) < 0.01
    else:
        matched = actual > 0

    return RuleTestResult.objects.create(
        entry=entry,
        patient=patient,
        test_name=test_name or f"auto-{dt.date.today()}",
        expected_score=expected_score,
        actual_score=actual,
        matched=matched,
        test_input=features,
        test_output={
            "total_score": actual,
            "matched_rules": result.matched_rules,
            "expected_score": expected_score,
        },
    )


def test_disease_suite(
    disease_id: str,
    test_cases: list[dict],
) -> list[RuleTestResult]:
    """Run a test suite against all active rules for a disease.

    Each test_case::
        {"features": {...}, "expected_top_disease": str, "min_score": float}
    """
    entries = KnowledgeBaseEntry.objects.filter(
        disease_id=disease_id, status="active"
    )
    results = []
    for case in test_cases:
        features = case.get("features", {})
        entry_results = []
        for entry in entries:
            tr = test_rule(entry, features=features)
            entry_results.append(tr)
        results.extend(entry_results)

    return results


def test_all_active_rules() -> dict[str, Any]:
    """Test every active rule against its disease's feature set.

    Returns summary stats.
    """
    entries = KnowledgeBaseEntry.objects.filter(status="active")
    total = 0
    passed = 0
    for entry in entries:
        total += 1
        # Use the rule's own conditions as minimal feature set
        features = _minimal_features(entry)
        tr = test_rule(entry, features=features)
        if tr.matched:
            passed += 1

    return {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total * 100, 1) if total else 100.0,
    }


def _minimal_features(entry: KnowledgeBaseEntry) -> dict:
    """Build minimal features that would trigger a rule's conditions."""
    from .services import _evaluate_condition

    features: dict = {}
    conditions = entry.rule_data.get("conditions", [])
    for cond in conditions:
        field = cond.get("field", "")
        operator = cond.get("operator", "eq")
        value = cond.get("value")

        if field in ("features", "labs", "biopsy"):
            features.setdefault(field, [])
            if isinstance(value, str) and value not in features[field]:
                features[field].append(value)
        elif operator in ("exists",):
            features[field] = True
        else:
            features[field] = value
    return features

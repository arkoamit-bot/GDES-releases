"""Rule validator — validates KnowledgeBaseEntry rule_data structure.

Ensures data integrity as the rule base scales to thousands of entries.
"""

from __future__ import annotations

from typing import Any

KNOWN_OPERATORS = frozenset(
    {"eq", "neq", "contains", "not_contains", "gt", "gte", "lt", "lte",
     "in", "exists", "not_exists"}
)

KNOWN_FIELDS = frozenset(
    {"features", "labs", "biopsy", "proteinuria", "albumin", "sediment",
     "egfrTrend", "ageGroup", "disease_phase", "registration_status",
     "latest_egfr", "proteinuria_level", "albumin_level", "biopsy_date",
     "edema_grade", "systolic_bp", "primary_diagnosis", "diabetes_status",
     "cohort"}
)


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def merge(self, other: ValidationResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def validate_rule_data(rule_data: dict, entry_id: str = "") -> ValidationResult:
    """Validate a rule_data dict and return structured errors/warnings."""
    result = ValidationResult()

    if not isinstance(rule_data, dict):
        result.errors.append(f"{entry_id}: rule_data must be a dict")
        return result

    conditions = rule_data.get("conditions", [])
    if not isinstance(conditions, list):
        result.errors.append(f"{entry_id}: conditions must be a list")
    elif len(conditions) == 0:
        result.warnings.append(f"{entry_id}: empty conditions list — rule will always match")

    weight = rule_data.get("weight", 0)
    if not isinstance(weight, (int, float)):
        result.errors.append(f"{entry_id}: weight must be a number")
    elif weight == 0:
        result.warnings.append(f"{entry_id}: weight is 0 — rule has no scoring effect")

    base_score = rule_data.get("base_score", 0)
    if not isinstance(base_score, (int, float)):
        result.errors.append(f"{entry_id}: base_score must be a number")
    elif base_score < -100 or base_score > 100:
        result.warnings.append(f"{entry_id}: base_score {base_score} is unusually large")

    explanation = rule_data.get("explanation", "")
    if not explanation:
        result.warnings.append(f"{entry_id}: missing explanation — rule will be hard to interpret")

    # Validate each condition
    for i, cond in enumerate(conditions):
        _validate_condition(cond, i, entry_id, result)

    return result


def _validate_condition(cond: Any, idx: int, entry_id: str, result: ValidationResult) -> None:
    if not isinstance(cond, dict):
        result.errors.append(f"{entry_id}: condition[{idx}] must be a dict")
        return

    field = cond.get("field")
    if not field:
        result.errors.append(f"{entry_id}: condition[{idx}] missing 'field'")
    elif field not in KNOWN_FIELDS:
        result.warnings.append(
            f"{entry_id}: condition[{idx}] field '{field}' is unknown"
        )

    operator = cond.get("operator", "eq")
    if operator not in KNOWN_OPERATORS:
        result.errors.append(
            f"{entry_id}: condition[{idx}] unknown operator '{operator}'"
        )

    if operator in ("gt", "gte", "lt", "lte") and "value" in cond:
        value = cond["value"]
        if not isinstance(value, (int, float)):
            result.warnings.append(
                f"{entry_id}: condition[{idx}] value is not numeric for {operator}"
            )

    if operator in ("in",) and "value" in cond:
        if not isinstance(cond["value"], list):
            result.errors.append(
                f"{entry_id}: condition[{idx}] 'in' operator requires a list value"
            )


def check_duplicate_conditions(
    rule_data: dict, entry_id: str = ""
) -> ValidationResult:
    """Check for duplicate condition tuples within a rule."""
    result = ValidationResult()
    conditions = rule_data.get("conditions", [])
    seen = set()
    for i, cond in enumerate(conditions):
        key = (cond.get("field"), cond.get("operator"), str(cond.get("value")))
        if key in seen:
            result.warnings.append(
                f"{entry_id}: condition[{i}] duplicates an earlier condition"
            )
        seen.add(key)
    return result


def validate_all_entries() -> list[ValidationResult]:
    """Validate every KnowledgeBaseEntry in the database."""
    from .models import KnowledgeBaseEntry

    results = []
    for entry in KnowledgeBaseEntry.objects.iterator():
        vr = validate_rule_data(entry.rule_data, entry.entry_id)
        dc = check_duplicate_conditions(entry.rule_data, entry.entry_id)
        vr.merge(dc)
        results.append(vr)
    return results

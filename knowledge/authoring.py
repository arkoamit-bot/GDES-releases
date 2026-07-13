"""Rule authoring — builder utilities for creating and editing rules.

Provides high-level helpers for constructing KnowledgeBaseEntry rule_data
from structured inputs, with validation integration.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from .models import GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion, RuleTemplate
from .rule_validator import validate_rule_data


def build_rule_data(
    conditions: list[dict],
    weight: float = 1.0,
    base_score: float = 0.0,
    explanation: str = "",
) -> dict:
    """Build a standard rule_data dict from structured components."""
    return {
        "conditions": conditions,
        "weight": weight,
        "base_score": base_score,
        "explanation": explanation,
    }


def create_rule(
    entry_id: str,
    disease_id: str,
    conditions: list[dict],
    weight: float = 1.0,
    base_score: float = 0.0,
    explanation: str = "",
    source_abbr: str = "",
    source_year: int = 0,
    evidence_grade: str = "NG",
    rule_type: str = "diagnostic",
    tags: list[str] | None = None,
) -> KnowledgeBaseEntry:
    """Create a new KnowledgeBaseEntry with built-in validation.

    Returns the created entry or raises ValidationError.
    """
    rule_data = build_rule_data(conditions, weight, base_score, explanation)
    result = validate_rule_data(rule_data, entry_id)
    if not result.is_valid:
        raise ValueError(
            f"Cannot create rule {entry_id}: " + "; ".join(result.errors)
        )

    source = None
    if source_abbr and source_year:
        source, _ = GuidelineSource.objects.get_or_create(
            abbreviation=source_abbr,
            version_year=source_year,
            defaults={
                "title": f"{source_abbr} {source_year} Guideline",
                "effective_date": f"{source_year}-01-01",
            },
        )
    if source is None:
        source = GuidelineSource.objects.first()
        if source is None:
            source = GuidelineSource.objects.create(
                title="Local Expert Consensus",
                abbreviation="LOCAL",
                version_year=dt.date.today().year,
                effective_date=dt.date.today(),
            )

    entry = KnowledgeBaseEntry.objects.create(
        entry_id=entry_id,
        disease_id=disease_id,
        rule_data=rule_data,
        source=source,
        evidence_grade=evidence_grade,
        rule_type=rule_type,
        status=KnowledgeBaseEntry.Status.DRAFT,
        effective_date=dt.date.today(),
        tags=tags or [],
    )
    return entry


def update_rule(
    entry: KnowledgeBaseEntry,
    conditions: list[dict] | None = None,
    weight: float | None = None,
    base_score: float | None = None,
    explanation: str | None = None,
    evidence_grade: str | None = None,
    change_summary: str = "",
    user=None,
) -> KnowledgeBaseEntry:
    """Update an existing rule with auto-versioning and validation.

    Creates a new version snapshot before modifying.
    """
    # Snapshot current state
    KnowledgeBaseVersion.objects.create(
        entry=entry,
        version_number=(entry.versions.first().version_number + 1)
        if entry.versions.exists() else 1,
        rule_data=entry.rule_data,
        evidence_grade=entry.evidence_grade,
        guideline_chapter=entry.guideline_chapter,
        guideline_paragraph=entry.guideline_paragraph,
        guideline_quote=entry.guideline_quote,
        change_summary=change_summary or f"Auto-snapshot before update",
        changed_by=user,
    )

    # Apply updates
    if conditions is not None:
        entry.rule_data["conditions"] = conditions
    if weight is not None:
        entry.rule_data["weight"] = weight
    if base_score is not None:
        entry.rule_data["base_score"] = base_score
    if explanation is not None:
        entry.rule_data["explanation"] = explanation
    if evidence_grade is not None:
        entry.evidence_grade = evidence_grade

    result = validate_rule_data(entry.rule_data, entry.entry_id)
    if not result.is_valid:
        raise ValueError(
            f"Cannot update rule {entry.entry_id}: " + "; ".join(result.errors)
        )

    entry.save()
    return entry


def apply_template(
    template: RuleTemplate,
    disease_id: str,
    values: dict[str, Any],
    entry_id_prefix: str = "KB",
) -> KnowledgeBaseEntry:
    """Create a rule from a RuleTemplate with user-supplied values.

    The template's condition_schema can specify field mappings and defaults.
    """
    conditions = []
    schema = template.condition_schema or {}
    field_defs = schema.get("fields", [])

    for field_def in field_defs:
        field_name = field_def.get("field")
        operator = field_def.get("operator", "eq")
        default_value = field_def.get("default")
        value = values.get(field_name, default_value)
        if value is not None:
            conditions.append({
                "field": field_name,
                "operator": operator,
                "value": value,
            })

    explanation = values.get("explanation", template.description)
    next_num = KnowledgeBaseEntry.objects.filter(
        disease_id=disease_id
    ).count() + 1
    entry_id = f"{entry_id_prefix}-{disease_id.upper()[:4]}-{next_num:03d}"

    return create_rule(
        entry_id=entry_id,
        disease_id=disease_id,
        conditions=conditions,
        weight=values.get("weight", 1),
        base_score=values.get("base_score", 0),
        explanation=explanation,
        rule_type=template.category,
        tags=values.get("tags", []),
    )

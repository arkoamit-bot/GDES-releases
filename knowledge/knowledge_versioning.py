"""Enhanced versioning — diff tracking, rollback, version groups.

Extends KnowledgeBaseVersion with structural diff computation.
"""

from __future__ import annotations

from typing import Any

from .models import KnowledgeBaseEntry, KnowledgeBaseVersion


def compute_rule_diff(
    old_data: dict, new_data: dict
) -> dict[str, Any]:
    """Compute a structural diff between two rule_data dicts.

    Returns a dict describing additions, removals, and changes.
    """
    diff: dict[str, Any] = {
        "conditions_changed": False,
        "weight_changed": False,
        "base_score_changed": False,
        "explanation_changed": False,
        "added_conditions": [],
        "removed_conditions": [],
        "changed_fields": {},
    }

    old_conditions = old_data.get("conditions", [])
    new_conditions = new_data.get("conditions", [])

    # Detect added/removed conditions by canonical key
    old_set = {_cond_key(c) for c in old_conditions}
    new_set = {_cond_key(c) for c in new_conditions}

    added = new_set - old_set
    removed = old_set - new_set

    if added:
        diff["conditions_changed"] = True
        diff["added_conditions"] = [
            c for c in new_conditions if _cond_key(c) in added
        ]
    if removed:
        diff["conditions_changed"] = True
        diff["removed_conditions"] = [
            c for c in old_conditions if _cond_key(c) in removed
        ]

    # Check scalar fields
    for field in ("weight", "base_score", "explanation"):
        old_val = old_data.get(field)
        new_val = new_data.get(field)
        if old_val != new_val:
            diff[f"{field}_changed"] = True
            diff["changed_fields"][field] = {"from": old_val, "to": new_val}

    return diff


def _cond_key(cond: dict) -> str:
    """Produce a canonical key for a condition dict."""
    return f"{cond.get('field')}|{cond.get('operator')}|{cond.get('value')}"


def create_version(
    entry: KnowledgeBaseEntry,
    change_summary: str = "",
    user=None,
) -> KnowledgeBaseVersion:
    """Create a new version snapshot with auto-computed diff."""
    last_version = entry.versions.first()
    next_number = (last_version.version_number + 1) if last_version else 1

    diff = {}
    if last_version:
        diff = compute_rule_diff(last_version.rule_data, entry.rule_data)

    version = KnowledgeBaseVersion.objects.create(
        entry=entry,
        version_number=next_number,
        rule_data=entry.rule_data,
        rule_data_diff=diff,
        evidence_grade=entry.evidence_grade,
        guideline_chapter=entry.guideline_chapter,
        guideline_paragraph=entry.guideline_paragraph,
        guideline_quote=entry.guideline_quote,
        change_summary=change_summary,
        changed_by=user,
    )
    return version


def rollback_to(
    entry: KnowledgeBaseEntry,
    target_version: KnowledgeBaseVersion,
    user=None,
) -> KnowledgeBaseEntry:
    """Rollback an entry to a specific version (creates auto-snapshot first).

    Returns the updated entry.
    """
    # Snapshot current state
    create_version(entry, change_summary=f"Auto-snapshot before rollback to v{target_version.version_number}", user=user)

    # Restore
    entry.rule_data = target_version.rule_data
    entry.evidence_grade = target_version.evidence_grade
    entry.guideline_chapter = target_version.guideline_chapter
    entry.guideline_paragraph = target_version.guideline_paragraph
    entry.guideline_quote = target_version.guideline_quote
    entry.save()

    return entry


def version_history(entry: KnowledgeBaseEntry) -> list[dict]:
    """Get a structured version history with diffs for display."""
    versions = entry.versions.all()
    return [
        {
            "version": v.version_number,
            "change_summary": v.change_summary,
            "changed_by": str(v.changed_by) if v.changed_by else "",
            "created_at": v.created_at.isoformat(),
            "diff": v.rule_data_diff or {},
        }
        for v in versions
    ]

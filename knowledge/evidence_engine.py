"""Evidence engine — GRADE-based evidence grading, literature lookups.

Provides structured evidence assessment for KnowledgeBaseEntry rules.
"""

from __future__ import annotations

import re
from typing import Any

from .models import EvidenceEntry, KnowledgeBaseEntry

# GRADE mapping: study design → GRADE quality
GRADE_QUALITY = {
    "meta": "High",
    "rct": "High",
    "cohort": "Moderate",
    "case_control": "Low",
    "case_series": "Very Low",
    "expert": "Very Low",
    "other": "Very Low",
}

# GRADE strength: evidence level → recommendation strength
STRENGTH_MAP = {
    "1": "Strong",
    "2": "Weak",
    "NG": "Not graded",
    "OP": "Expert opinion",
}


def grade_evidence(entry: KnowledgeBaseEntry) -> dict[str, Any]:
    """Compute GRADE-based evidence summary for a KnowledgeBaseEntry."""
    evidence_entries = entry.evidence_entries.all()
    if not evidence_entries.exists():
        return _grade_from_entry_fields(entry)

    best_level = _best_evidence_level(evidence_entries)
    return {
        "entry_id": entry.entry_id,
        "evidence_grade": entry.evidence_grade,
        "recommendation_strength": STRENGTH_MAP.get(entry.evidence_grade, "Unknown"),
        "best_evidence_level": best_level,
        "grade_quality": GRADE_QUALITY.get(best_level, "Unknown"),
        "evidence_count": evidence_entries.count(),
        "evidence_summary": _build_evidence_summary(evidence_entries),
        "sources": [
            {
                "title": e.title[:100],
                "authors": e.authors[:100] if e.authors else "",
                "journal": e.journal,
                "year": e.year,
                "doi": e.doi,
                "level": e.evidence_level,
            }
            for e in evidence_entries
        ],
    }


def _best_evidence_level(entries) -> str:
    """Return the highest evidence level among entries."""
    rank = ["other", "expert", "case_series", "case_control",
            "cohort", "rct", "meta"]
    best = "other"
    for e in entries:
        if e.evidence_level in rank:
            if rank.index(e.evidence_level) > rank.index(best):
                best = e.evidence_level
    return best


def _grade_from_entry_fields(entry: KnowledgeBaseEntry) -> dict:
    """Fallback grading using only the entry's own evidence_grade field."""
    quality_map = {
        "1": "High",
        "2": "Moderate",
        "NG": "Not graded",
        "OP": "Very Low",
    }
    return {
        "entry_id": entry.entry_id,
        "evidence_grade": entry.evidence_grade,
        "recommendation_strength": STRENGTH_MAP.get(entry.evidence_grade, "Unknown"),
        "best_evidence_level": "not_available",
        "grade_quality": quality_map.get(entry.evidence_grade, "Unknown"),
        "evidence_count": 0,
        "evidence_summary": "No linked evidence entries — grade based on entry field only.",
        "sources": [],
    }


def _build_evidence_summary(entries) -> str:
    """Build a human-readable summary of evidence."""
    counts: dict[str, int] = {}
    for e in entries:
        level = e.evidence_level or "other"
        counts[level] = counts.get(level, 0) + 1

    parts = []
    label_map = {
        "meta": "meta-analyses",
        "rct": "RCTs",
        "cohort": "cohort studies",
        "case_control": "case-control studies",
        "case_series": "case series",
        "expert": "expert opinions",
        "other": "other references",
    }
    for level, count in sorted(
        counts.items(),
        key=lambda x: list(label_map.keys()).index(x[0]) if x[0] in label_map else 99,
    ):
        label = label_map.get(level, level)
        parts.append(f"{count} {label}")

    return "; ".join(parts) if parts else "No evidence entries"


def suggest_evidence_grade(entry: KnowledgeBaseEntry) -> str:
    """Auto-suggest an evidence grade based on linked evidence entries."""
    g = grade_evidence(entry)
    quality = g.get("grade_quality", "Not graded")

    quality_to_grade = {
        "High": "1",
        "Moderate": "2",
        "Low": "OP",
        "Very Low": "OP",
        "Not graded": "NG",
    }
    return quality_to_grade.get(quality, "NG")


def generate_citation(evidence: EvidenceEntry) -> str:
    """Generate a citation string for an EvidenceEntry."""
    parts = []
    if evidence.authors:
        parts.append(evidence.authors[:120])
    if evidence.year:
        parts.append(f"({evidence.year})")
    parts.append(evidence.title[:200])
    if evidence.journal:
        parts.append(evidence.journal)
    if evidence.doi:
        parts.append(f"doi:{evidence.doi}")
    return ". ".join(parts)

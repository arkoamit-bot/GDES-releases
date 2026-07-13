"""Guideline import — import rules from structured external formats.

Supports JSON, YAML, CSV, and markdown-based guideline imports.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from .models import GuidelineDocument, GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion
from .guideline_parser import parse_json_rules, parse_markdown_guideline


def import_json_guideline(
    data: list[dict],
    source_abbr: str = "",
    source_year: int = 0,
    source_title: str = "",
) -> dict:
    """Import rules from a JSON array.

    Returns import summary with counts.
    """
    candidates = parse_json_rules(data)
    return _create_entries(candidates, source_abbr, source_year, source_title)


def import_csv_guideline(
    csv_content: str,
    source_abbr: str = "",
    source_year: int = 0,
    source_title: str = "",
) -> dict:
    """Import rules from CSV content.

    Expected columns::
        disease_id, conditions_json, weight, explanation, evidence_grade
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    candidates = []
    for row in reader:
        raw_conditions = row.get("conditions_json", "[]")
        try:
            conditions = json.loads(raw_conditions)
        except (json.JSONDecodeError, TypeError):
            conditions = [{"field": "features", "operator": "eq",
                           "value": row.get("explanation", "").lower().replace(" ", "_")}]

        candidates.append({
            "disease_id": row.get("disease_id", "unknown"),
            "conditions": conditions,
            "weight": int(row.get("weight", 1)),
            "explanation": row.get("explanation", ""),
            "evidence_grade": row.get("evidence_grade", "NG"),
            "entry_id": row.get("entry_id", ""),
            "guideline_chapter": row.get("guideline_chapter", ""),
            "guideline_paragraph": row.get("guideline_paragraph", ""),
        })

    return _create_entries(candidates, source_abbr, source_year, source_title)


def import_yaml_guideline(
    yaml_content: str,
    source_abbr: str = "",
    source_year: int = 0,
    source_title: str = "",
) -> dict:
    """Import rules from YAML content.

    Uses PyYAML if available, otherwise falls back to JSON.parse-style.
    """
    try:
        import yaml as _yaml
        data = _yaml.safe_load(yaml_content)
    except ImportError:
        raise ImportError(
            "PyYAML is required for YAML import. Install with: pip install pyyaml"
        )

    if isinstance(data, list):
        candidates = parse_json_rules(data)
    elif isinstance(data, dict):
        candidates = parse_json_rules(data.get("rules", []))
        if not source_abbr:
            source_abbr = data.get("source", {}).get("abbreviation", "")
        if not source_year:
            source_year = data.get("source", {}).get("year", 0)
    else:
        raise ValueError("YAML content must be a list or a dict with 'rules' key")

    return _create_entries(candidates, source_abbr, source_year, source_title)


def import_markdown_guideline(
    doc: GuidelineDocument,
) -> dict:
    """Import rules from a GuidelineDocument with markdown content.

    Parses the document and creates KnowledgeBaseEntry records.
    """
    candidates = parse_markdown_guideline(doc)
    source = doc.source
    return _create_entries(
        candidates,
        source_abbr=source.abbreviation if source else "",
        source_year=source.version_year if source else 0,
        source_title=doc.title,
        doc=doc,
    )


def _create_entries(
    candidates: list[dict],
    source_abbr: str = "",
    source_year: int = 0,
    source_title: str = "",
    doc: GuidelineDocument | None = None,
) -> dict:
    """Create KnowledgeBaseEntry records from parsed candidates."""
    source = None
    if source_abbr and source_year:
        source, _ = GuidelineSource.objects.get_or_create(
            abbreviation=source_abbr,
            version_year=source_year,
            defaults={
                "title": source_title or f"{source_abbr} {source_year}",
                "effective_date": f"{source_year}-01-01",
            },
        )

    created = 0
    skipped = 0
    errors = []
    log_lines = []

    for candidate in candidates:
        entry_id = candidate.get("entry_id", "")
        if not entry_id:
            prefix = candidate.get("disease_id", "unknown").upper()[:8]
            entry_id = f"KB-{prefix}-{KnowledgeBaseEntry.objects.count() + 1:03d}"

        if KnowledgeBaseEntry.objects.filter(entry_id=entry_id).exists():
            skipped += 1
            log_lines.append(f"Skipped existing: {entry_id}")
            continue

        rule_data = {
            "conditions": candidate.get("conditions", []),
            "weight": candidate.get("weight", 1),
            "explanation": candidate.get("explanation", ""),
            "base_score": candidate.get("base_score", 0),
        }

        try:
            KnowledgeBaseEntry.objects.create(
                entry_id=entry_id,
                disease_id=candidate.get("disease_id", "unknown"),
                rule_data=rule_data,
                source=source or GuidelineSource.objects.first(),
                evidence_grade=candidate.get("evidence_grade", "NG"),
                status=KnowledgeBaseEntry.Status.DRAFT,
                effective_date=f"{source_year or 2025}-01-01",
                guideline_chapter=candidate.get("guideline_chapter", ""),
                guideline_paragraph=candidate.get("guideline_paragraph", ""),
                guideline_quote=candidate.get("guideline_quote", ""),
            )
            created += 1
            log_lines.append(f"Created: {entry_id}")
        except Exception as e:
            errors.append(f"{entry_id}: {e}")
            log_lines.append(f"Error: {entry_id}: {e}")

    summary = {
        "candidates": len(candidates),
        "created": created,
        "skipped": skipped,
        "errors": len(errors),
        "error_details": errors[:10],
    }

    if doc:
        doc.import_status = (
            GuidelineDocument.ImportStatus.ERROR
            if errors
            else GuidelineDocument.ImportStatus.COMPLETE
        )
        doc.parsed_rules = candidates
        doc.import_log = "\n".join(log_lines)
        doc.save(update_fields=["import_status", "import_log", "parsed_rules"])

    return summary

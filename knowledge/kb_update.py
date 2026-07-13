"""Update the knowledge base from a downloaded guideline export file.

Used by the admin "Update from file" button. Governance-safe by design:

- New rules are created as **DRAFT**.
- Changed rules are updated **and moved back to DRAFT** for re-review — an
  existing ACTIVE rule is never silently overwritten in place.
- Unchanged rules are left exactly as they are (status preserved).

A clinician then reviews the DRAFT rules and promotes them to ACTIVE via the
existing admin lifecycle actions. Nothing this importer does can put a
new/changed rule live without that human step.

Accepted file shapes (JSON):
  - the app's own export: ``{"entries": [ {entry_id, disease_id, rule_data, …} ]}``
  - a bare list: ``[ {entry_id, …}, … ]``
  - ``{"rules": [ … ]}`` with flat rule fields (conditions/weight/explanation).
"""
from __future__ import annotations

import json
from datetime import date

from django.db import transaction

from .models import GuidelineSource, KnowledgeBaseEntry

# Fields compared to decide whether an existing rule "changed".
_TRACKED_FIELDS = (
    "disease_id", "rule_data", "evidence_grade", "rule_type",
    "guideline_chapter", "guideline_paragraph", "guideline_quote", "tags",
)


def _entries_from(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("entries", "rules"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError(
        "Unrecognized file format — expected a JSON list, or an object with an "
        "'entries' or 'rules' array."
    )


def _resolve_source(item: dict) -> GuidelineSource | None:
    """Find or create the GuidelineSource referenced by an entry."""
    abbr = (item.get("source_abbreviation") or "").strip()
    year = item.get("source_year") or 0

    # Fall back to parsing a combined "KDIGO 2021" style string.
    if (not abbr or not year) and item.get("source"):
        parts = str(item["source"]).split()
        if parts and not abbr:
            abbr = parts[0]
        if not year:
            for p in parts:
                if p.isdigit() and len(p) == 4:
                    year = int(p)
                    break

    if abbr and year:
        source, _ = GuidelineSource.objects.get_or_create(
            abbreviation=abbr, version_year=year,
            defaults={"title": f"{abbr} {year}", "effective_date": f"{year}-01-01"},
        )
        return source
    return None


def _fields_from(item: dict) -> dict:
    rule_data = item.get("rule_data")
    if rule_data is None:  # flat form (conditions/weight/explanation/base_score)
        rule_data = {
            "conditions": item.get("conditions", []),
            "weight": item.get("weight", 1),
            "explanation": item.get("explanation", ""),
            "base_score": item.get("base_score", 0),
        }
    return {
        "disease_id": item.get("disease_id", "unknown"),
        "rule_data": rule_data,
        "evidence_grade": item.get("evidence_grade", "NG"),
        "rule_type": item.get("rule_type", KnowledgeBaseEntry.RuleType.DIAGNOSTIC),
        "guideline_chapter": item.get("guideline_chapter", ""),
        "guideline_paragraph": item.get("guideline_paragraph", ""),
        "guideline_quote": item.get("guideline_quote", ""),
        "tags": item.get("tags") or [],
    }


@transaction.atomic
def import_kb_payload(payload) -> dict:
    """Upsert knowledge entries from a parsed JSON payload. Returns a summary."""
    entries = _entries_from(payload)

    created = updated = unchanged = errors = 0
    error_details: list[str] = []

    for item in entries:
        try:
            entry_id = (item.get("entry_id") or "").strip()
            if not entry_id:
                errors += 1
                error_details.append("Entry without an 'entry_id' was skipped.")
                continue

            fields = _fields_from(item)
            source = _resolve_source(item)
            existing = KnowledgeBaseEntry.objects.filter(entry_id=entry_id).first()

            if existing is None:
                KnowledgeBaseEntry.objects.create(
                    entry_id=entry_id,
                    status=KnowledgeBaseEntry.Status.DRAFT,
                    source=source or GuidelineSource.objects.first(),
                    effective_date=date.today(),
                    **fields,
                )
                created += 1
                continue

            changed = any(getattr(existing, f) != fields[f] for f in _TRACKED_FIELDS)
            if source and existing.source_id != source.id:
                changed = True
            if not changed:
                unchanged += 1
                continue

            for f, v in fields.items():
                setattr(existing, f, v)
            if source:
                existing.source = source
            # A changed rule must be re-reviewed before it can go live again.
            existing.status = KnowledgeBaseEntry.Status.DRAFT
            existing.save()
            updated += 1

        except Exception as exc:  # noqa: BLE001 — report per-entry, keep going
            errors += 1
            error_details.append(f"{item.get('entry_id', '?')}: {exc}")

    return {
        "total": len(entries),
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "errors": errors,
        "error_details": error_details[:20],
    }


def import_kb_text(text: str) -> dict:
    """Parse JSON text and import it. Raises ValueError on bad JSON."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    return import_kb_payload(payload)


# Max download size for a remote guideline file (25 MB) — guards against a huge
# response exhausting memory (guideline PDFs can be a few MB).
_MAX_BYTES = 25 * 1024 * 1024


def download_bytes(url: str, timeout: int = 30) -> bytes:
    """Download an http(s) URL to bytes, with scheme check, timeout and size cap.

    Shared by the JSON-rule importer and the guideline-reference importer.
    """
    import urllib.request
    from urllib.parse import urlparse

    url = (url or "").strip()
    if urlparse(url).scheme not in ("http", "https"):
        raise ValueError("Only http:// or https:// links are supported.")

    req = urllib.request.Request(url, headers={"User-Agent": "GDES-KB-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (scheme checked)
            raw = resp.read(_MAX_BYTES + 1)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not download the link: {exc}") from exc

    if len(raw) > _MAX_BYTES:
        raise ValueError("The linked file is too large (over 25 MB).")
    return raw


def import_kb_url(url: str, timeout: int = 20) -> dict:
    """Fetch a JSON guideline export from an http(s) URL and import it as DRAFT.

    The URL must point directly at the raw JSON (e.g. a raw GitHub link or a
    direct-download share link). Same governance as file import: new/changed
    rules land as DRAFT.
    """
    raw = download_bytes(url, timeout=timeout)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "The linked file is not UTF-8 JSON. If this is a guideline PDF, use "
            "“Import guideline (reference)” instead — a PDF cannot be imported as "
            "rules."
        ) from exc
    return import_kb_text(text)

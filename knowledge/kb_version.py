"""Knowledge-base version stamp + health summary (P1-2 / P1-3).

- PACKAGED_KB_VERSION is the KB version shipped in this build.
- The *installed* version is stamped in a small file under BGDDR_DATA_DIR, so
  seeding on an update only re-runs when the packaged KB is newer (idempotent
  seeders never clobber a clinician-edited KB on same-version launches).
- kb_health_summary() powers the startup health gate (P1-3).
"""
from __future__ import annotations

from pathlib import Path

# Bump this when the packaged knowledge base changes in a way that should
# re-seed on update. Keep in step with the seeders' `knowledge_version`.
PACKAGED_KB_VERSION = "6.6"

_STAMP_NAME = ".kb_version"


def _stamp_path() -> Path:
    from django.conf import settings
    base = Path(getattr(settings, "BGDDR_DATA_DIR", settings.BASE_DIR))
    return base / _STAMP_NAME


def _parse(v: str) -> tuple:
    """Parse a dotted version into a comparable tuple; non-numeric parts -> 0."""
    out = []
    for part in str(v).strip().split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out) or (0,)


def get_installed_kb_version() -> str | None:
    try:
        p = _stamp_path()
        if p.exists():
            return p.read_text(encoding="utf-8").strip() or None
    except OSError:
        pass
    return None


def stamp_kb_version(version: str = PACKAGED_KB_VERSION) -> None:
    try:
        _stamp_path().write_text(str(version).strip(), encoding="utf-8")
    except OSError:
        pass


def should_seed_kb(packaged: str = PACKAGED_KB_VERSION) -> bool:
    """True when seeding should run: no stamp yet, or packaged KB is newer."""
    installed = get_installed_kb_version()
    if not installed:
        return True
    return _parse(packaged) > _parse(installed)


def kb_health_summary() -> dict:
    """Counts + status for the startup health gate. Never raises."""
    summary = {
        "kb_version": get_installed_kb_version() or PACKAGED_KB_VERSION,
        "diseases": 0, "rules_active": 0, "rules_total": 0,
        "pathways": 0, "cases": 0, "guidelines": 0,
        "status": "unknown", "critical": [],
    }
    try:
        from knowledge.models import (
            KnowledgeBaseEntry, Disease, ClinicalCase,
            ClinicalPathway, GuidelineSource,
        )
        summary["rules_total"] = KnowledgeBaseEntry.objects.count()
        summary["rules_active"] = KnowledgeBaseEntry.objects.filter(
            status=KnowledgeBaseEntry.Status.ACTIVE).count()
        for key, model in (("diseases", Disease), ("cases", ClinicalCase),
                           ("pathways", ClinicalPathway), ("guidelines", GuidelineSource)):
            try:
                summary[key] = model.objects.count()
            except Exception:
                summary[key] = 0
    except Exception as exc:  # DB unopenable / models missing
        summary["status"] = "critical"
        summary["critical"].append(f"knowledge base unreadable: {exc}")
        return summary

    # Critical: an empty active rule set makes the CDS layer non-functional.
    if summary["rules_active"] == 0:
        summary["status"] = "critical"
        summary["critical"].append("no ACTIVE knowledge rules")
    else:
        summary["status"] = "ok"
    return summary

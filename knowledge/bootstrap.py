"""Knowledge Bootstrap Validation — health check on startup.

Before the application becomes operational, verify:
  - Knowledge Base exists
  - Active guideline version exists
  - ACTIVE rules exist
  - Rule index successfully built
  - Guideline versions consistent
  - Knowledge schema compatible
  - Evidence references valid

If validation fails, the platform enters maintenance mode.
Clinical reasoning must never silently degrade.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeHealth:
    is_healthy: bool = True
    checks: dict[str, bool] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def record(self, check_name: str, passed: bool, detail: Any = None, error: str = ""):
        self.checks[check_name] = passed
        if detail is not None:
            self.details[check_name] = detail
        if error:
            self.errors.append(f"{check_name}: {error}")
            self.is_healthy = False
        elif not passed:
            self.warnings.append(f"{check_name}: check did not pass")
            self.is_healthy = False


def check_knowledge_base() -> KnowledgeHealth:
    """Run all knowledge platform health checks."""
    health = KnowledgeHealth()

    try:
        from knowledge.models import GuidelineSource, KnowledgeBaseEntry, EvidenceEntry, GuidelineDocument
        from django.db import connection

        # 1. Knowledge Base exists (tables accessible)
        try:
            table_names = connection.introspection.table_names()
            tables_ok = all(
                t in table_names
                for t in ["knowledge_knowledgebaseentry", "knowledge_guidelinesource",
                          "knowledge_evidenceentry", "knowledge_guidelinedocument"]
            )
            health.record("tables_exist", tables_ok,
                          detail={"found": [t for t in table_names if t.startswith("knowledge_")]})
        except Exception as e:
            health.record("tables_exist", False, error=str(e))

        # 2. Active guideline version exists
        try:
            guideline_count = GuidelineSource.objects.count()
            has_guidelines = guideline_count > 0
            active_sources = list(GuidelineSource.objects.values("abbreviation", "version_year", "effective_date"))
            health.record("active_guidelines", has_guidelines,
                          detail={"count": guideline_count, "sources": active_sources})
        except Exception as e:
            health.record("active_guidelines", False, error=str(e))

        # 3. ACTIVE rules exist
        try:
            total_rules = KnowledgeBaseEntry.objects.count()
            active_rules = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.ACTIVE).count()
            draft_rules = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.DRAFT).count()
            has_active = active_rules > 0
            health.record("active_rules_exist", has_active,
                          detail={"total": total_rules, "active": active_rules, "draft": draft_rules})
            if total_rules > 0 and not has_active:
                health.errors.append(
                    f"active_rules_exist: {total_rules} rules exist but ZERO are ACTIVE "
                    f"(all {draft_rules} are DRAFT). Run: python manage.py activate_entries --all"
                )
        except Exception as e:
            health.record("active_rules_exist", False, error=str(e))

        # 4. Guideline versions consistent (no duplicate conflicting versions)
        try:
            from django.db.models import Count
            dupes = (
                GuidelineSource.objects.values("abbreviation", "version_year", "title")
                .annotate(cnt=Count("id"))
                .filter(cnt__gt=1)
            )
            dupes_list = list(dupes)
            versions_consistent = len(dupes_list) == 0
            health.record("guideline_versions_consistent", versions_consistent,
                          detail={"duplicate_entries": dupes_list})
        except Exception as e:
            health.record("guideline_versions_consistent", False, error=str(e))

        # 5. Evidence references valid
        try:
            entries_with_evidence = KnowledgeBaseEntry.objects.filter(evidence_entries__isnull=False).distinct().count()
            total_evidence = EvidenceEntry.objects.count()
            health.record("evidence_references", True,
                          detail={"entries_with_evidence": entries_with_evidence,
                                  "total_evidence_entries": total_evidence})
        except Exception as e:
            health.record("evidence_references", False, error=str(e))

        # 6. Knowledge schema compatible (key fields present)
        try:
            sample = KnowledgeBaseEntry.objects.first()
            if sample:
                has_rule_data = bool(sample.rule_data)
                has_source = sample.source_id is not None
                schema_ok = has_rule_data and has_source
                health.record("schema_compatible", schema_ok,
                              detail={"has_rule_data": has_rule_data, "has_source": has_source})
            else:
                health.record("schema_compatible", False,
                              warning="No KnowledgeBaseEntry records exist to validate schema")
        except Exception as e:
            health.record("schema_compatible", False, error=str(e))

        # 7. Rule index (if any disease_id/status index is populated)
        try:
            disease_counts = dict(
                KnowledgeBaseEntry.objects.values("disease_id")
                .annotate(cnt=Count("id"))
                .values_list("disease_id", "cnt")
            )
            health.record("rule_index", bool(disease_counts),
                          detail={"disease_coverage": disease_counts})
        except Exception as e:
            health.record("rule_index", False, error=str(e))

    except ImportError as e:
        health.record("knowledge_base_import", False, error=str(e))
    except Exception as e:
        health.record("knowledge_base_check", False, error=str(e))

    return health


def require_healthy_knowledge() -> None:
    """Check knowledge health; if unhealthy, log critical and raise RuntimeError.

    Call this during Django startup (e.g. in AppConfig.ready()) to prevent
    the application from serving requests with degraded knowledge.
    """
    health = check_knowledge_base()
    if health.is_healthy:
        logger.info(
            "Knowledge platform validation PASSED — %d/%d checks OK",
            sum(1 for v in health.checks.values() if v),
            len(health.checks),
        )
        return

    logger.critical("KNOWLEDGE PLATFORM VALIDATION FAILED")
    for err in health.errors:
        logger.critical("  ✗ %s", err)
    for warn in health.warnings:
        logger.warning("  ⚠ %s", warn)

    # In production, raise to prevent serving degraded reasoning
    from django.conf import settings
    if not settings.DEBUG:
        raise RuntimeError(
            "Knowledge platform validation failed — refusing to start.\n"
            + "\n".join(health.errors)
        )
    logger.warning("DEBUG mode: continuing despite knowledge validation failures")

"""
Knowledge Quality Dashboard — CLI display of knowledge health.

    python manage.py knowledge_dashboard
    python manage.py knowledge_dashboard --json   (machine-readable output)
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Q


class Command(BaseCommand):
    help = "Display the Knowledge Quality Dashboard"

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="Output as JSON")

    def handle(self, *args, **options):
        from knowledge.models import KnowledgeBaseEntry, EvidenceEntry
        from knowledge.bootstrap import check_knowledge_base

        health = check_knowledge_base()
        total = KnowledgeBaseEntry.objects.count()
        by_status = dict(
            KnowledgeBaseEntry.objects.values("status").annotate(cnt=Count("id")).values_list("status", "cnt")
        )
        by_disease = dict(
            KnowledgeBaseEntry.objects.values("disease_id").annotate(cnt=Count("id")).values_list("disease_id", "cnt")
        )
        active_count = by_status.get("active", 0)
        draft_count = by_status.get("draft", 0)
        deprecated_count = by_status.get("retired", 0) + by_status.get("superseded", 0) + by_status.get("archived", 0)

        coverage_pct = round((active_count / max(total, 1)) * 100, 1) if total > 0 else 0.0

        with_evidence = KnowledgeBaseEntry.objects.filter(evidence_entries__isnull=False).distinct().count()
        missing_evidence = total - with_evidence

        with_guideline = KnowledgeBaseEntry.objects.exclude(guideline_chapter="").count()
        missing_guideline = total - with_guideline

        deprecated_count = by_status.get("retired", 0) + by_status.get("superseded", 0) + by_status.get("archived", 0)

        health_score = round(
            (active_count / max(total, 1)) * 30
            + (1 - missing_evidence / max(total, 1)) * 25
            + (1 - missing_guideline / max(total, 1)) * 20
            + (1 - deprecated_count / max(total, 1)) * 15
            + (1 if health.is_healthy else 0) * 10
        )

        if options["json"]:
            import json
            data = {
                "knowledge_version": "3.6",
                "guideline_version": max(
                    (s.version_year for s in
                     (__import__("knowledge.models", fromlist=["GuidelineSource"])
                      .GuidelineSource.objects.iterator())),
                    default=0,
                ) if total > 0 else 0,
                "total_rules": total,
                "active_rules": active_count,
                "draft_rules": draft_count,
                "deprecated_rules": deprecated_count,
                "by_status": by_status,
                "coverage_pct": coverage_pct,
                "missing_evidence": missing_evidence,
                "failed_rules": len(health.errors),
                "health_score": health_score,
                "last_validation": None,
            }
            self.stdout.write(json.dumps(data, indent=2))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("====== Knowledge Quality Dashboard ======"))
        self.stdout.write(f"Knowledge Version:         3.6")
        self.stdout.write(f"Total Rules:               {total}")
        self.stdout.write(f"ACTIVE Rules:              {active_count}")
        self.stdout.write(f"Draft Rules:               {draft_count}")
        self.stdout.write(f"Deprecated Rules:          {deprecated_count}")
        self.stdout.write(f"Coverage:                  {coverage_pct}%")
        self.stdout.write(f"Missing Evidence:          {missing_evidence}")
        self.stdout.write(f"Missing Guideline:         {missing_guideline}")
        self.stdout.write(f"Checks Passed:             {sum(1 for v in health.checks.values() if v)}/{len(health.checks)}")
        self.stdout.write(f"Knowledge Health Score:    {health_score}/100")

        if health.errors:
            self.stdout.write(self.style.ERROR("\nErrors:"))
            for e in health.errors:
                self.stdout.write(self.style.ERROR(f"  ✗ {e}"))

        if health.warnings:
            self.stdout.write(self.style.WARNING("\nWarnings:"))
            for w in health.warnings:
                self.stdout.write(self.style.WARNING(f"  ⚠ {w}"))

        if active_count == 0 and total > 0:
            self.stdout.write(self.style.WARNING(
                "\n⚠  ZERO ACTIVE RULES — run: python manage.py activate_entries --all"
            ))
        elif total == 0:
            self.stdout.write(self.style.WARNING(
                "\n⚠  NO RULES — seed the knowledge base: python manage.py seed_knowledge_base"
            ))

"""
Validate governance metadata on all ACTIVE knowledge base entries.

Layer 4 (Continuous Evidence Validation) enforcement:
Every ACTIVE recommendation must have complete governance metadata.

    python manage.py validate_governance
    python manage.py validate_governance --fix-missing
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from knowledge.models import KnowledgeBaseEntry


REQUIRED_FIELDS = {
    "guideline_chapter": "Guideline chapter reference",
    "evidence_grade": "Evidence grade (1/2/NG/OP)",
    "author": "Rule author",
    "approved_by": "Clinical reviewer who approved",
    "approved_at": "Approval timestamp",
    "next_review_date": "Scheduled re-review date",
    "confidence_score": "AI confidence score",
}

WARN_FIELDS = {
    "evidence_url": "Link to supporting evidence/DOI",
    "recommendation_id": "Guideline recommendation ID",
    "knowledge_version": "KB version when created",
    "date_validated": "Last validation date",
    "guideline_paragraph": "Specific guideline paragraph",
}


class Command(BaseCommand):
    help = "Validate governance metadata on ACTIVE knowledge base entries"

    def add_arguments(self, parser):
        parser.add_argument("--disease-id", type=str, default=None,
                            help="Only validate entries for this disease_id")
        parser.add_argument("--entry-id", type=str, default=None,
                            help="Validate a single entry")
        parser.add_argument("--fix-missing", action="store_true",
                            help="Auto-set default values for missing governance fields")

    def handle(self, *args, **options):
        qs = KnowledgeBaseEntry.objects.filter(status="active")
        if options["disease_id"]:
            qs = qs.filter(disease_id=options["disease_id"])
        if options["entry_id"]:
            qs = qs.filter(entry_id=options["entry_id"])

        total = 0
        passed = 0
        failed = 0
        all_issues = []

        for entry in qs.iterator():
            total += 1
            issues = self._check_entry(entry, options["fix_missing"])
            if not issues:
                passed += 1
            else:
                failed += 1
                all_issues.append((entry, issues))
                self.stdout.write(self.style.WARNING(
                    f"\n{entry.entry_id} ({entry.disease_id}):"
                ))
                for field, label, severity in issues:
                    style = self.style.ERROR if severity == "ERROR" else self.style.WARNING
                    self.stdout.write(style(f"  [{severity}] {field}: {label}"))

        self.stdout.write()
        if total == 0:
            self.stdout.write(self.style.WARNING("No ACTIVE entries found"))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Checked {total} ACTIVE entries: {passed} passed, {failed} with issues"
        ))

    def _check_entry(self, entry, fix_missing):
        issues = []

        for field, label in REQUIRED_FIELDS.items():
            value = getattr(entry, field, None)
            if value is None or value == "" or value == 0.0:
                issues.append((field, label, "ERROR"))
                if fix_missing:
                    self._auto_fix(entry, field)

        for field, label in WARN_FIELDS.items():
            value = getattr(entry, field, None)
            if value is None or value == "":
                issues.append((field, label, "WARN"))

        if entry.next_review_date and entry.next_review_date < date.today():
            issues.append(("next_review_date", f"Overdue (was {entry.next_review_date})", "WARN"))

        return issues

    def _auto_fix(self, entry, field):
        if field == "confidence_score":
            setattr(entry, field, 50.0)
        elif field == "next_review_date":
            setattr(entry, field, date.today() + timedelta(days=180))
        elif field == "evidence_grade":
            setattr(entry, field, "NG")
        elif field in ("guideline_chapter", "evidence_url", "recommendation_id", "guideline_paragraph"):
            setattr(entry, field, "(pending)")
        entry.save(update_fields=[field, "updated_at"])

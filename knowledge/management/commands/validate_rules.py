"""
Validate all knowledge base entries for structural correctness.

    python manage.py validate_rules
    python manage.py validate_rules --disease_id=iga
    python manage.validate_rules --entry-id=KB-IGA-001
"""
from django.core.management.base import BaseCommand
from knowledge.models import KnowledgeBaseEntry
from knowledge.rule_validator import validate_rule_data, check_duplicate_conditions


class Command(BaseCommand):
    help = "Validate knowledge base entries for data integrity"

    def add_arguments(self, parser):
        parser.add_argument("--disease-id", type=str, default=None,
                            help="Only validate entries for this disease_id")
        parser.add_argument("--entry-id", type=str, default=None,
                            help="Validate a single entry by entry_id")

    def handle(self, *args, **options):
        qs = KnowledgeBaseEntry.objects.all()
        if options["disease_id"]:
            qs = qs.filter(disease_id=options["disease_id"])
        if options["entry_id"]:
            qs = qs.filter(entry_id=options["entry_id"])

        total = 0
        valid = 0
        with_warnings = 0
        with_errors = 0

        for entry in qs.iterator():
            total += 1
            result = validate_rule_data(entry.rule_data, entry.entry_id)
            dc = check_duplicate_conditions(entry.rule_data, entry.entry_id)
            result.merge(dc)

            if not result.is_valid:
                with_errors += 1
                self.stdout.write(self.style.ERROR(
                    f"{entry.entry_id}: ERRORS: {'; '.join(result.errors)}"
                ))
            if result.warnings:
                with_warnings += 1
                self.stdout.write(self.style.WARNING(
                    f"{entry.entry_id}: WARNINGS: {'; '.join(result.warnings)}"
                ))
            if result.is_valid and not result.warnings:
                valid += 1

        self.stdout.write(self.style.SUCCESS(
            f"Validated {total} entries: {valid} clean, "
            f"{with_warnings} with warnings, {with_errors} with errors"
        ))

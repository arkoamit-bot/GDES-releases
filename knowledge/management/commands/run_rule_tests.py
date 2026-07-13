"""
Run rule tests — test all active rules or a specific disease suite.

    python manage.py run_rule_tests                     # Test all active rules
    python manage.py run_rule_tests --disease_id=iga    # Test rules for a disease
"""
import json
from django.core.management.base import BaseCommand, CommandError
from knowledge.rule_tester import test_all_active_rules, test_disease_suite
from knowledge.models import KnowledgeBaseEntry


class Command(BaseCommand):
    help = "Run tests against active knowledge base rules"

    def add_arguments(self, parser):
        parser.add_argument("--disease-id", type=str, default=None,
                            help="Test rules for a specific disease")
        parser.add_argument("--test-cases", type=str, default=None,
                            help="JSON file with test cases for disease suite testing")
        parser.add_argument("--entry-id", type=str, default=None,
                            help="Test a specific rule by entry_id")

    def handle(self, *args, **options):
        disease_id = options.get("disease_id")
        test_cases_file = options.get("test_cases")
        entry_id = options.get("entry_id")

        if entry_id:
            from knowledge.rule_tester import test_rule
            try:
                entry = KnowledgeBaseEntry.objects.get(entry_id=entry_id)
            except KnowledgeBaseEntry.DoesNotExist:
                raise CommandError(f"Entry not found: {entry_id}")
            result = test_rule(entry)
            self.stdout.write(self.style.SUCCESS(
                f"{entry.entry_id}: score={result.actual_score}, matched={result.matched}"
            ))
            return

        if disease_id and test_cases_file:
            with open(test_cases_file, "r") as f:
                test_cases = json.load(f)
            results = test_disease_suite(disease_id, test_cases)
            passed = sum(1 for r in results if r.matched)
            self.stdout.write(self.style.SUCCESS(
                f"Disease '{disease_id}': {passed}/{len(results)} tests passed"
            ))
            return

        summary = test_all_active_rules()
        self.stdout.write(self.style.SUCCESS(
            f"All active rules: {summary['passed']}/{summary['total_tests']} passed "
            f"({summary['pass_rate']}%)"
        ))

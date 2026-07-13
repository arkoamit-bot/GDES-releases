"""
Management command to deactivate TEST-* knowledge base rules.

Usage:
    python manage.py deactivate_test_rules

Sets all KnowledgeBaseEntry where entry_id starts with 'TEST-' to 'draft'
status, as required by the V7.3 Clinical Pilot Stabilization checklist.
"""
from django.core.management.base import BaseCommand, CommandError

from knowledge.models import KnowledgeBaseEntry


class Command(BaseCommand):
    help = "Deactivate all TEST-* knowledge base rules to draft status"

    def handle(self, *args, **options):
        qs = KnowledgeBaseEntry.objects.filter(
            entry_id__startswith="TEST-", status="active"
        )
        count = qs.count()
        if count == 0:
            self.stdout.write("No active TEST-* rules found. Nothing to do.")
            return

        updated = qs.update(status="draft")
        self.stdout.write(
            self.style.SUCCESS(
                f"Deactivated {updated} TEST-* rule(s) (active -> draft)."
            )
        )

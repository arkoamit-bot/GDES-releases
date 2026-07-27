"""Management command to generate improvement suggestions from clinician overrides.

Usage:
    python manage.py generate_suggestions

Can be run as a periodic task (e.g. daily cron) to auto-draft KB revision
suggestions when clinician overrides accumulate on the same recommendation.
"""
from django.core.management.base import BaseCommand

from feedback.services import generate_improvement_suggestions


class Command(BaseCommand):
    help = "Generate improvement suggestions from clinician override patterns"

    def handle(self, *args, **options):
        suggestions = generate_improvement_suggestions()
        if suggestions:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Generated {len(suggestions)} improvement suggestion(s)."
                )
            )
            for s in suggestions:
                self.stdout.write(
                    f"  - {s.rule_id} ({s.disease or 'N/A'}): "
                    f"{s.override_count} overrides — {s.status}"
                )
        else:
            self.stdout.write("No new suggestions to generate.")

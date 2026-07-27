"""
Compute and store today's evidence analytics snapshot.

    python manage.py compute_evidence_analytics
"""
from django.core.management.base import BaseCommand

from clinical_evidence.services.analytics import compute_daily_analytics


class Command(BaseCommand):
    help = "Compute daily evidence analytics snapshot."

    def handle(self, *args, **options):
        snapshot = compute_daily_analytics()
        self.stdout.write(self.style.SUCCESS(
            f"Analytics snapshot #{snapshot.id} created for {snapshot.date}."
        ))

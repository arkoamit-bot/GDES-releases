"""Backfill automatic study-eligibility screening for all existing patients.

Ongoing screening happens automatically via the event bus; this command is for
the one-off initial pass (or after adding new eligibility criteria).

    python manage.py auto_screen_patients
"""
from django.core.management.base import BaseCommand

from studies.services.auto_screen import auto_screen_all


class Command(BaseCommand):
    help = "Run automatic study eligibility screening across all patients."

    def handle(self, *args, **options):
        totals = auto_screen_all()
        self.stdout.write(self.style.SUCCESS(
            f"Screened {totals['patients']} patients — "
            f"{totals['created']} candidate records created, "
            f"{totals['updated']} updated, "
            f"{totals['eligible']} eligible study-matches."
        ))

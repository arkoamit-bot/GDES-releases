"""
Recompute every patient's PatientOutcome from current labs / events / exposures.

    python manage.py compute_outcomes

Re-runnable any time (e.g. nightly, or after a data-entry session). In
production this would be a scheduled job feeding the analytics layer.
"""
from django.core.management.base import BaseCommand

from analytics.services.outcomes import compute_all_outcomes


class Command(BaseCommand):
    help = "Recompute PatientOutcome rows (the outcome engine)."

    def handle(self, *args, **options):
        n = compute_all_outcomes()
        self.stdout.write(self.style.SUCCESS(f"Computed outcomes for {n} patients."))

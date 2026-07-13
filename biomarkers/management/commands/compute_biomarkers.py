"""Recompute every patient's biomarker kinetics. python manage.py compute_biomarkers"""
from django.core.management.base import BaseCommand

from biomarkers.services.kinetics import compute_all_biomarkers


class Command(BaseCommand):
    help = "Recompute BiomarkerKinetics rows from the lab series."

    def handle(self, *args, **options):
        n = compute_all_biomarkers()
        self.stdout.write(self.style.SUCCESS(f"Computed biomarker kinetics for {n} patients."))

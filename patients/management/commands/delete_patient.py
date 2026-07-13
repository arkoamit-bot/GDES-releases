"""
Delete a patient and ALL their data (FK-safe cascade).

    python manage.py delete_patient BGD-00007          # preview (counts only)
    python manage.py delete_patient BGD-00007 --yes     # actually delete

A plain delete is refused while a patient has encounters (they are PROTECTed);
this command removes prescriptions / lab orders / encounters first, then the
patient. Irreversible — take a backup first (python manage.py backup_db).
"""
from django.core.management.base import BaseCommand, CommandError

from patients.models import Patient
from patients.services import delete_patient_cascade


class Command(BaseCommand):
    help = "Delete a patient and all their clinical data."

    def add_arguments(self, parser):
        parser.add_argument("patient_id", help="Study ID, e.g. BGD-00007")
        parser.add_argument("--yes", action="store_true", help="Skip confirmation.")

    def handle(self, *args, **opts):
        try:
            p = Patient.objects.get(patient_id=opts["patient_id"])
        except Patient.DoesNotExist:
            raise CommandError(f"No patient with ID {opts['patient_id']!r}.")

        if not opts["yes"]:
            self.stdout.write(self.style.WARNING(
                f"Would delete {p.patient_id} ({p.name}) and: "
                f"{p.encounters.count()} encounter(s), "
                f"{p.biopsies.count()} biopsy(ies), "
                f"{p.exposures.count()} drug episode(s), "
                f"{p.lab_results.count()} lab result(s).\n"
                "Re-run with --yes to delete. (Back up first: manage.py backup_db)"))
            return
        pid = delete_patient_cascade(p)
        self.stdout.write(self.style.SUCCESS(f"Deleted {pid} and all their data."))

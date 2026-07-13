"""
Safely remove demo / synthetic PATIENT data so you can start entering real
patients on a clean slate.

It only ever touches patient-linked clinical data (patients and everything that
cascades from them, plus their prescriptions). It NEVER deletes reference/config
data — drug formulary, lab catalog, roles, study definitions or user accounts.

SAFE BY DEFAULT: nothing is deleted unless you pass --yes. Without it you get a
preview of exactly what would be removed.

    # see what's in the database, grouped by id prefix
    python manage.py reset_demo_data --list

    # preview removing the known demo patients (SYN-*, ST-*, BGD-DEMO, BGD-LOOP)
    python manage.py reset_demo_data

    # actually remove them
    python manage.py reset_demo_data --yes

    # target specific prefixes
    python manage.py reset_demo_data --prefixes "SYN-,ST-,BMK-,FLAG-" --yes

    # full wipe of ALL patients (fresh start) + clear the audit log
    python manage.py reset_demo_data --all --clear-audit --yes
"""
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

DEFAULT_DEMO_PREFIXES = ["SYN-", "ST-", "BGD-DEMO", "BGD-LOOP"]


class Command(BaseCommand):
    help = "Remove demo/synthetic patient data (preview unless --yes)."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true",
                            help="Target ALL patients (full reset).")
        parser.add_argument("--prefixes", default=",".join(DEFAULT_DEMO_PREFIXES),
                            help="Comma-separated patient_id prefixes to target.")
        parser.add_argument("--list", action="store_true",
                            help="Just list patient-id prefixes with counts and exit.")
        parser.add_argument("--clear-audit", action="store_true",
                            help="Also clear the audit log (for a fully fresh start).")
        parser.add_argument("--yes", action="store_true",
                            help="Actually delete. Without this it is a preview only.")

    def handle(self, *args, **opts):
        from patients.models import Patient

        if opts["list"]:
            self._list(Patient)
            return

        if opts["all"]:
            qs = Patient.objects.all()
            scope = "ALL patients"
        else:
            prefixes = [p.strip() for p in opts["prefixes"].split(",") if p.strip()]
            from django.db.models import Q
            cond = Q()
            for p in prefixes:
                cond |= Q(patient_id__startswith=p)
            qs = Patient.objects.filter(cond) if prefixes else Patient.objects.none()
            scope = f"patients matching {prefixes}"

        n = qs.count()
        if n == 0:
            self.stdout.write(self.style.WARNING(f"No {scope} found — nothing to do."))
            return

        sample = list(qs.order_by("patient_id").values_list("patient_id", flat=True)[:12])
        self.stdout.write(f"Target: {scope}")
        self.stdout.write(f"  {n} patient(s): {', '.join(sample)}"
                          + (" …" if n > len(sample) else ""))

        if not opts["yes"]:
            self.stdout.write(self.style.WARNING(
                "\nPREVIEW ONLY — nothing was deleted. Re-run with --yes to delete."))
            return

        with transaction.atomic():
            # Prescriptions PROTECT their encounter, so remove them before the
            # patients cascade-delete the encounters.
            from prescriptions.models import Prescription
            n_pres, _ = Prescription.objects.filter(encounter__patient__in=qs).delete()
            total, by_model = qs.delete()
            n_audit = 0
            if opts["clear_audit"]:
                from audit.models import AuditLog
                n_audit, _ = AuditLog.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"\nDeleted {n} patient(s) and {total} related record(s)."))
        for model, c in sorted(by_model.items()):
            if c:
                self.stdout.write(f"  {model}: {c}")
        if n_pres:
            self.stdout.write(f"  prescriptions (+items): {n_pres}")
        if opts["clear_audit"]:
            self.stdout.write(f"  audit log cleared: {n_audit}")
        self.stdout.write(self.style.SUCCESS("Clean slate ready for real patient entry."))

    def _list(self, Patient):
        ids = Patient.objects.values_list("patient_id", flat=True)
        groups = Counter(pid.split("-")[0] + ("-" if "-" in pid else "") for pid in ids)
        self.stdout.write("Patient ids by leading prefix:")
        for prefix, c in sorted(groups.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {prefix or '(no prefix)':14s} {c}")
        self.stdout.write(f"  {'TOTAL':14s} {sum(groups.values())}")

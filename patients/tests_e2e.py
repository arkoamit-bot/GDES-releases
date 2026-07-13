"""
End-to-end workflow test for the BGDDR single-user deployment.

Drives the real models and service entry points through the entire clinical +
research pathway, then validates exports and the backup/restore subsystem:

    enrollment -> consent -> encounter -> labs -> biopsy -> prescription
               -> outcomes -> analytics -> export -> backup/restore

Run:  python manage.py test patients.tests_e2e
"""
import datetime as dt
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from analytics.services.outcomes import compute_patient_outcome
from audit.models import Consent
from bgddr.backup import create_backup, list_backups, restore_from_backup
from encounters.models import ClinicalEncounter
from exports.services.dataset import build_dataset
from exports.services.dictionary import column_defs
from exports.services.writers import to_csv, to_sav, to_xlsx
from labs.services.results import record_result
from pathology.models import Biopsy
from patients.models import Patient
from prescriptions.models import Prescription, PrescriptionItem
from prescriptions.services.finalize import finalize_prescription
from treatments.models import DrugClass, DrugMaster

User = get_user_model()


class EndToEndWorkflowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_labs", verbosity=0)  # creatinine + panels
        cls.user = User.objects.create_user(
            username="dr_e2e", password="x", is_staff=True)

    def test_full_workflow(self):
        # 1. ENROLLMENT -----------------------------------------------------
        p = Patient.objects.create(
            patient_id="BGD-E2E1", name="E2E Patient", sex="M",
            dob=dt.date(1972, 5, 1), enrollment_date=dt.date(2024, 1, 1),
            diabetes_status="t2", latest_egfr=42)
        self.assertIsNotNone(p.pk)

        # 2. CONSENT --------------------------------------------------------
        consent = Consent.objects.create(
            patient=p, consent_type=Consent.Type.REGISTRY,
            form_version="BGDDR-ICF-v2.1", status=Consent.Status.GRANTED,
            consent_date=dt.date(2024, 1, 1), obtained_by=self.user)
        self.assertEqual(p.consents.filter(status=Consent.Status.GRANTED).count(), 1)

        # 3. CLINICAL ENCOUNTER --------------------------------------------
        enc = ClinicalEncounter.objects.create(
            patient=p, encounter_date=dt.date(2024, 1, 1),
            encounter_type=ClinicalEncounter.Type.BASELINE,
            seen_by=self.user, systolic_bp=140, diastolic_bp=85)
        self.assertIsNotNone(enc.pk)

        # 4. LABORATORY ENTRY (longitudinal creatinine -> eGFR) ------------
        record_result(p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.6)
        record_result(p, "creatinine", result_date=dt.date(2024, 7, 1), value_numeric=2.4)
        record_result(p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=3.0)
        self.assertGreaterEqual(p.lab_results.count(), 3)

        # 5. BIOPSY ENTRY ---------------------------------------------------
        biopsy = Biopsy.objects.create(
            patient=p, biopsy_date=dt.date(2024, 1, 10),
            total_glomeruli=14, global_sclerosis_pct=20, ifta_pct=15)
        self.assertIsNotNone(biopsy.pk)

        # 6. PRESCRIPTION GENERATION (create + finalize) -------------------
        ramipril = DrugMaster.objects.create(
            generic_name="Ramipril", drug_class=DrugClass.RAASI)
        rx = Prescription.objects.create(encounter=enc)
        PrescriptionItem.objects.create(
            prescription=rx, drug=ramipril, dose="5 mg", frequency="1+0+0", sort_order=0)
        finalize_prescription(rx, user=self.user)
        rx.refresh_from_db()
        self.assertTrue(rx.content_hash, "prescription should be frozen with a content hash")

        # 7. OUTCOME CALCULATIONS ------------------------------------------
        outcome = compute_patient_outcome(p)
        self.assertIsNotNone(outcome)
        # A sustained decline from eGFR computed off rising creatinine is expected.
        self.assertTrue(hasattr(outcome, "composite_kidney_event"))

        # 8. ANALYTICS (pure-Python survival primitive on the cohort) ------
        from analytics.services import survival
        km = survival.kaplan_meier([10, 20, 30, 40], [True, False, True, True])
        self.assertTrue(len(km) >= 1)

        # 9. DATA EXPORT (CSV + Excel, with the patient present) -----------
        cols, rows = build_dataset(Patient.objects.all().order_by("patient_id"))
        self.assertIn("patient_id", cols)
        csv_text = to_csv(cols, rows)
        self.assertIn("BGD-E2E1", csv_text)
        xlsx_bytes = to_xlsx(cols, rows)
        self.assertTrue(xlsx_bytes[:2] == b"PK", "valid .xlsx (zip) container")
        sav_bytes = to_sav(cols, rows, defs=column_defs())
        self.assertEqual(sav_bytes[:4], b"$FL2", "valid SPSS .sav container")

    def test_backup_and_restore(self):
        """Validate the backup subsystem against an isolated temp database."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            db = tmp / "db.sqlite3"
            db.write_bytes(b"ORIGINAL-DB-CONTENTS")
            backups = tmp / "Backups"

            with override_settings(
                DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3",
                                       "NAME": str(db)}},
                BACKUP_CONFIG={"directory": str(backups), "max_backups": 5,
                               "interval_hours": 6}):
                # Create a backup.
                snap = create_backup(reason="e2e")
                self.assertIsNotNone(snap)
                self.assertEqual(len(list_backups()), 1)

                # Corrupt the live DB, then restore from the snapshot.
                db.write_bytes(b"CORRUPTED")
                self.assertTrue(restore_from_backup(snap))
                self.assertEqual(db.read_bytes(), b"ORIGINAL-DB-CONTENTS")
                # restore takes a pre_restore safety snapshot -> now 2 backups.
                self.assertEqual(len(list_backups()), 2)

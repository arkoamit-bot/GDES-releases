"""
Tests for the medication reconciliation engine â€” open / continue / change /
close, plus idempotency and the cross-visit episode history.
"""
import datetime as dt

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from encounters.models import ClinicalEncounter
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster, StopReason, TreatmentExposure

from .models import Prescription, PrescriptionItem
from .pdf import render_prescription_html
from .services.finalize import finalize_prescription
from .services.reconciliation import (AlreadyReconciled, apply_reconciliation,
                                      plan_reconciliation)
from .services.safety import check_prescription
from .services.tapers import (TAPER_PRESETS, course_length_days, is_systemic_steroid,
                              needs_taper)

# Column order `import_bddrugbank`'s DictReader expects. Without this header
# row DictReader consumes the first data row as field names and imports
# nothing -- silently.
CSV_HEADER = ["name", "generic_name", "strength", "therapeutic_class",
              "company", "dosage_form", "medex_url"]

User = get_user_model()


class ReconciliationTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(
            patient_id="BGD-0001", name="Test Patient", sex="M",
            diabetes_status="t2", latest_egfr=28)
        self.ramipril = DrugMaster.objects.create(
            generic_name="Ramipril", drug_class=DrugClass.RAASI)
        self.dapa = DrugMaster.objects.create(
            generic_name="Dapagliflozin", drug_class=DrugClass.SGLT2I,
            renal_dose_adjust=True, egfr_caution_below=25)
        self.hcq = DrugMaster.objects.create(
            generic_name="Hydroxychloroquine", drug_class=DrugClass.HCQ)

    def _encounter(self, day):
        return ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 1, day),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)

    def _rx(self, enc, meds):
        """meds: list of (drug, dose, frequency)."""
        rx = Prescription.objects.create(encounter=enc)
        for i, (drug, dose, freq) in enumerate(meds):
            PrescriptionItem.objects.create(
                prescription=rx, drug=drug, dose=dose, frequency=freq, sort_order=i)
        return rx

    def test_first_visit_opens_episodes(self):
        rx = self._rx(self._encounter(1),
                      [(self.ramipril, "5 mg", "1+0+0"),
                       (self.dapa, "10 mg", "1+0+0")])
        plan = plan_reconciliation(rx)
        self.assertEqual(plan.summary(), {"open": 2, "close": 0, "change": 0, "continue": 0})
        apply_reconciliation(rx)
        self.assertEqual(TreatmentExposure.objects.filter(patient=self.p, ongoing=True).count(), 2)

    def test_continue_is_noop(self):
        apply_reconciliation(self._rx(self._encounter(1), [(self.ramipril, "5 mg", "1+0+0")]))
        rx2 = self._rx(self._encounter(2), [(self.ramipril, "5 mg", "1+0+0")])
        self.assertEqual(plan_reconciliation(rx2).summary()["continue"], 1)
        apply_reconciliation(rx2)
        # Still exactly one ongoing episode, unchanged.
        self.assertEqual(TreatmentExposure.objects.filter(drug=self.ramipril).count(), 1)

    def test_dose_change_splits_episode(self):
        apply_reconciliation(self._rx(self._encounter(1), [(self.ramipril, "5 mg", "1+0+0")]))
        rx2 = self._rx(self._encounter(5), [(self.ramipril, "10 mg", "1+0+0")])
        self.assertEqual(plan_reconciliation(rx2).summary()["change"], 1)
        apply_reconciliation(rx2)
        eps = TreatmentExposure.objects.filter(drug=self.ramipril).order_by("start_date")
        self.assertEqual(eps.count(), 2)
        self.assertEqual(eps[0].stop_reason, StopReason.DOSE_CHANGE)
        self.assertEqual(eps[0].stop_date, dt.date(2026, 1, 5))
        self.assertFalse(eps[0].ongoing)
        self.assertEqual(eps[1].dose, "10 mg")
        self.assertTrue(eps[1].ongoing)

    def test_drug_dropped_is_closed_with_reason(self):
        apply_reconciliation(self._rx(self._encounter(1),
                                      [(self.ramipril, "5 mg", "1+0+0"),
                                       (self.hcq, "200 mg", "1+0+1")]))
        rx2 = self._rx(self._encounter(10), [(self.ramipril, "5 mg", "1+0+0")])
        plan = plan_reconciliation(rx2)
        self.assertEqual(plan.summary()["close"], 1)
        self.assertIn(self.hcq.id, plan.drugs_being_stopped)
        apply_reconciliation(rx2, stop_reasons={self.hcq.id: StopReason.INTOLERANCE})
        hcq_ep = TreatmentExposure.objects.get(drug=self.hcq)
        self.assertFalse(hcq_ep.ongoing)
        self.assertEqual(hcq_ep.stop_reason, StopReason.INTOLERANCE)
        self.assertEqual(hcq_ep.stop_date, dt.date(2026, 1, 10))

    def test_reconcile_is_idempotent(self):
        rx = self._rx(self._encounter(1), [(self.ramipril, "5 mg", "1+0+0")])
        apply_reconciliation(rx)
        with self.assertRaises(AlreadyReconciled):
            apply_reconciliation(rx)
        self.assertEqual(TreatmentExposure.objects.count(), 1)

    def test_finalize_freezes_and_reconciles(self):
        rx = self._rx(self._encounter(1), [(self.ramipril, "5 mg", "1+0+0")])
        finalize_prescription(rx)
        rx.refresh_from_db()
        self.assertTrue(rx.is_final)
        self.assertTrue(rx.content_hash)
        self.assertIsNotNone(rx.reconciled_at)
        self.assertEqual(TreatmentExposure.objects.filter(ongoing=True).count(), 1)


class DrugMasterImportTests(TestCase):
    """Guards the MedEx import's name handling.

    Every case here corresponds to a real defect the refresh introduced:
    qualifier-suffixed MedEx names creating duplicate drugs, devices
    landing as prescribable rows, and case-only differences splitting one
    drug into two rows (which breaks `seed_drug_knowledge`'s iexact lookup
    with MultipleObjectsReturned).
    """

    def test_split_generic_folds_qualifier_and_recovers_route(self):
        from .management.commands.import_bddrugbank import split_generic
        self.assertEqual(split_generic("Chlorhexidine Gluconate [4%]"),
                         ("Chlorhexidine Gluconate", None))
        self.assertEqual(split_generic("Levonorgestrel [Emergency "
                                       "contraceptive pill]"),
                         ("Levonorgestrel", None))
        # An unambiguous form qualifier becomes the route.
        self.assertEqual(split_generic("Sertaconazole Nitrate [Topical]"),
                         ("Sertaconazole Nitrate", "TOP"))
        # A bare form word is not a route: recording PO here would make an
        # injection-only drug appear orally prescribable.
        self.assertEqual(split_generic("Ceftriaxone [Injection]"),
                         ("Ceftriaxone", None))

    def test_split_generic_would_fold_a_curated_seed_name(self):
        """Documents *why* _consolidate needs its curated-name guard.

        split_generic alone is not safe to run over the whole table: it
        reduces `Insulin (soluble/regular)` to `Insulin`, which is neither
        the seed_drug_knowledge lookup key nor a CURATED_BRANDS key.
        """
        from .management.commands.import_bddrugbank import split_generic
        self.assertEqual(split_generic("Insulin (soluble/regular)")[0],
                         "Insulin")
        self.assertEqual(split_generic("Insulin isophane (NPH)")[0],
                         "Insulin isophane")

    def test_norm_collapses_case_and_punctuation(self):
        from .management.commands.import_bddrugbank import norm
        self.assertEqual(norm("Losartan potassium"),
                         norm("LOSARTAN POTASSIUM"))
        self.assertEqual(norm("Zoledronic Acid"), norm("zoledronic acid"))
        self.assertEqual(norm("Multivitamins & Multiminerals"),
                         norm("multivitaminsmultiminerals"))

    def test_canonical_generic_folds_qualifier_to_seed_name(self):
        """The import folds then canonicalises; canonical_generic alone is
        not a superset, it only resolves a name it already holds a mapping
        for. Order matters, so pin the composition the command uses."""
        from .management.commands.import_bddrugbank import (canonical_generic,
                                                            split_generic)
        base = split_generic("Zoledronic Acid [For osteoporosis]")[0]
        self.assertEqual(canonical_generic(base), "Zoledronic acid")
        # Human insulin rows canonicalise onto the curated formulary name
        # rather than creating a competing `Insulin` row.
        self.assertEqual(canonical_generic("Insulin Human"),
                         "Insulin (soluble/regular)")

    def test_is_device_excludes_devices_but_keeps_cosmetics(self):
        from .management.commands.import_bddrugbank import is_device
        for junk in ("Insulin device & needle", "BP monitoring device",
                     "Latex condom", "Surgical needle", "Inhaler device"):
            self.assertTrue(is_device(junk), junk)
        # Topical/cosmetic preparations are legitimately prescribable.
        for real in ("Clotrimazole", "Hydrocortisone Acetate",
                     "Permethrin", "Mometasone Furoate"):
            self.assertFalse(is_device(real), real)

    def test_consolidate_merges_variants_and_repoints_exposure(self):
        from patients.models import Patient
        from treatments.models import TreatmentExposure
        from .management.commands.import_bddrugbank import Command
        p = Patient.objects.create(patient_id="BGD-9002", name="Merge User",
                                   sex="M")
        a = DrugMaster.objects.create(
            generic_name="Chlorhexidine Gluconate [0.2%]",
            brand_names=["A"], available_strengths=["0.2%"])
        b = DrugMaster.objects.create(
            generic_name="Chlorhexidine Gluconate [4%]",
            brand_names=["B"], available_strengths=["4%"])
        clean = DrugMaster.objects.create(
            generic_name="Chlorhexidine Gluconate", brand_names=["C"])
        exp = TreatmentExposure.objects.create(
            drug=b, drug_name=b.generic_name, patient=p,
            start_date=dt.date(2026, 1, 1))

        Command()._consolidate(dry_run=False)

        # TreatmentExposure.drug is on_delete=PROTECT, so consolidation must
        # repoint before deleting or the delete raises ProtectedError.
        self.assertFalse(DrugMaster.objects.filter(pk=b.pk).exists())
        self.assertFalse(DrugMaster.objects.filter(pk=a.pk).exists())
        merged = DrugMaster.objects.get(pk=clean.pk)
        self.assertEqual(sorted(merged.brand_names), ["A", "B", "C"])
        self.assertEqual(sorted(merged.available_strengths), ["0.2%", "4%"])
        exp.refresh_from_db()
        self.assertEqual(exp.drug_id, clean.pk)
        # The denormalised snapshot must not be rewritten.
        self.assertEqual(exp.drug_name, "Chlorhexidine Gluconate [4%]")

    def test_consolidate_never_folds_a_curated_seed_name(self):
        """`Insulin (soluble/regular)` is the seed_drug_knowledge lookup key.

        Folding it to `Insulin` would orphan the formulary entry, so the
        command must leave seeded names untouched.
        """
        from .management.commands.import_bddrugbank import (CURATED_BRANDS,
                                                            Command)
        name = "Insulin (soluble/regular)"
        self.assertIn(name, CURATED_BRANDS)
        row = DrugMaster.objects.create(generic_name=name,
                                        brand_names=["Actrapid"])
        Command()._consolidate(dry_run=False)
        self.assertTrue(DrugMaster.objects.filter(pk=row.pk).exists())
        self.assertEqual(
            DrugMaster.objects.get(generic_name__iexact=name).brand_names,
            ["Actrapid"])

    def test_consolidate_is_idempotent(self):
        from .management.commands.import_bddrugbank import Command
        DrugMaster.objects.create(generic_name="Sodium Cromoglicate [2%]",
                                  brand_names=["A"])
        Command()._consolidate(dry_run=False)
        first = DrugMaster.objects.get(generic_name="Sodium Cromoglicate")
        Command()._consolidate(dry_run=False)
        first.refresh_from_db()
        self.assertEqual(DrugMaster.objects.count(), 1)
        self.assertEqual(first.brand_names, ["A"])

    def test_consolidate_refuses_to_delete_an_in_use_device(self):
        from patients.models import Patient
        from treatments.models import TreatmentExposure
        from .management.commands.import_bddrugbank import Command
        p = Patient.objects.create(patient_id="BGD-9001", name="Dev User",
                                   sex="F")
        device = DrugMaster.objects.create(generic_name="Inhaler device")
        TreatmentExposure.objects.create(
            drug=device, drug_name=device.generic_name, patient=p,
            start_date=dt.date(2026, 1, 1))
        Command()._consolidate(dry_run=False)
        self.assertTrue(DrugMaster.objects.filter(pk=device.pk).exists())

    def test_dry_run_writes_nothing(self):
        """--dry-run must not persist: `apply()` mutates the instance, so
        guarding only the create path silently wrote to the live DB."""
        import csv as _csv
        import os
        import tempfile
        from django.core.management import call_command
        from io import StringIO
        row = DrugMaster.objects.create(
            generic_name="Metformin", brand_names=["Glucophage"])
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(CSV_HEADER)
            w.writerow(["Comet", "Metformin", "500 mg", "1+0+0", "Biguanide"])
        try:
            call_command("import_bddrugbank", path, dry_run=True,
                         stdout=StringIO(), stderr=StringIO())
        finally:
            os.unlink(path)
        row.refresh_from_db()
        self.assertEqual(row.brand_names, ["Glucophage"])
        # `contains` is unsupported on SQLite, so check in Python.
        self.assertFalse(any("Comet" in (o.brand_names or [])
                             for o in DrugMaster.objects.all()))

    def test_import_appends_brands_and_keeps_curated_first(self):
        import csv as _csv
        import os
        import tempfile
        from django.core.management import call_command
        from io import StringIO
        from .management.commands.seed_drugs import DRUGS
        curated = dict((row[0], list(row[4])) for row in DRUGS)
        ramipril = DrugMaster.objects.create(
            generic_name="Ramipril", drug_class=DrugClass.RAASI,
            brand_names=list(curated["Ramipril"]))
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(CSV_HEADER)
            # A scraped brand that sorts before the curated ones, and a
            # scraped strength/route that must be additive.
            w.writerow(["Altace", "Ramipril", "2.5 mg", "1+0+0", "ACE inhibitor"])
            w.writerow(["Ramipres", "Ramipril [For hypertension]", "5 mg",
                        "1+0+0", "ACE inhibitor"])
        try:
            call_command("import_bddrugbank", path, dry_run=False,
                         stdout=StringIO(), stderr=StringIO())
        finally:
            os.unlink(path)
        ramipril.refresh_from_db()
        head = [b for b in curated["Ramipril"] if b in ramipril.brand_names]
        self.assertEqual(ramipril.brand_names[:len(head)], head)
        self.assertIn("Altace", ramipril.brand_names)
        self.assertIn("Ramipres", ramipril.brand_names)
        self.assertIn("2.5 mg", ramipril.available_strengths)
        # The bracket-suffixed row folded into the existing drug.
        self.assertFalse(DrugMaster.objects.filter(
            generic_name__icontains="Ramipril [").exists())


class MedexAutoSyncTests(TestCase):
    """The unattended MedEx refresh.

    These tests all guard one property: a periodic job that runs while nobody
    is watching must never leave the drug database worse than it found it.
    """

    def setUp(self):
        # Every test gets a private lock path. They used to share one file in
        # the OS temp directory, so an interrupted run left the lock behind and
        # every later run failed with "a sync is already running".
        import tempfile
        self._tmp = tempfile.mkdtemp(prefix="bgddr_drugsync_")

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _lock(self, name="t"):
        from pathlib import Path
        return Path(self._tmp) / f"{name}.lock"

    def _write_csv(self, rows, header=True, name="medex.csv"):
        import csv as _csv
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            if header:
                w.writerow(CSV_HEADER)
            w.writerows(rows)
        return path

    def _ok_row(self, brand="Comet", generic="Metformin", strength="500 mg"):
        return [brand, generic, strength, "", "Square", "Tablet", "u"]

    def _good_run(self, rows_scraped, content_hash, **extra):
        from treatments.models import DrugSyncRun
        return DrugSyncRun.objects.create(
            state=DrugSyncRun.State.SUCCESS, trigger="scheduled",
            rows_scraped=rows_scraped, content_hash=content_hash,
            **extra)

    # -- schedule gate ------------------------------------------------------
    def test_due_when_never_run(self):
        from .services.medex_sync import should_sync_now
        self.assertTrue(should_sync_now())

    def test_not_due_right_after_a_successful_run(self):
        from django.test import override_settings
        from .services.medex_sync import should_sync_now
        self._good_run(25416, "abc")
        with override_settings(DRUG_SYNC_CONFIG={
                **self._cfg(), "enabled": True, "interval_hours": 168}):
            self.assertFalse(should_sync_now())

    def test_due_again_after_the_interval(self):
        from django.test import override_settings
        from django.utils import timezone
        from datetime import timedelta
        from treatments.models import DrugSyncRun
        from .services.medex_sync import should_sync_now
        run = self._good_run(25416, "abc")
        DrugSyncRun.objects.filter(pk=run.pk).update(
            finished_at=timezone.now() - timedelta(hours=169))
        with override_settings(DRUG_SYNC_CONFIG={
                **self._cfg(), "enabled": True, "interval_hours": 168}):
            self.assertTrue(should_sync_now())

    def test_a_failed_run_does_not_reset_the_schedule(self):
        """A week of network failures must not trigger a retry storm."""
        from django.test import override_settings
        from django.utils import timezone
        from datetime import timedelta
        from treatments.models import DrugSyncRun
        from .services.medex_sync import should_sync_now
        self._good_run(25416, "abc")
        DrugSyncRun.objects.create(
            state=DrugSyncRun.State.FAILED, trigger="scheduled",
            error="HTTP 503")
        with override_settings(DRUG_SYNC_CONFIG={
                **self._cfg(), "enabled": True, "interval_hours": 168}):
            self.assertFalse(should_sync_now())

    def test_disabled_never_runs(self):
        from django.test import override_settings
        from .services.medex_sync import should_sync_now
        with override_settings(DRUG_SYNC_CONFIG={
                **self._cfg(), "enabled": False, "interval_hours": 168}):
            self.assertFalse(should_sync_now())

    def _cfg(self):
        from django.conf import settings
        return dict(settings.DRUG_SYNC_CONFIG)

    # -- validation gate ----------------------------------------------------
    def test_rejects_a_truncated_scrape(self):
        """The failure that matters: a partial fetch still parses cleanly,
        and the importer only adds, so a truncated run looks like success
        while leaving the tail of the alphabet un-refreshed."""
        from .services.medex_sync import ScrapeRejected, _validate
        self._good_run(25416, "old")
        path = self._write_csv([self._ok_row() for _ in range(100)])
        try:
            with self.assertRaises(ScrapeRejected):
                _validate(_abs(path), self._last_good())
        finally:
            import os
            os.unlink(path)

    def test_accepts_a_scrape_within_the_ratio_floor(self):
        from .services.medex_sync import _validate
        self._good_run(1000, "old")
        path = self._write_csv([self._ok_row(brand=f"B{i}")
                                for i in range(900)])
        try:
            facts = _validate(_abs(path), self._last_good())
            self.assertEqual(facts["rows_scraped"], 900)
            self.assertEqual(len(facts["content_hash"]), 64)
        finally:
            import os
            os.unlink(path)

    def test_rejects_a_csv_with_no_header(self):
        """Without a header DictReader eats the first data row, so the file
        looks empty rather than malformed."""
        from .services.medex_sync import ScrapeRejected, _validate
        path = self._write_csv([self._ok_row()], header=False)
        try:
            with self.assertRaises(ScrapeRejected):
                _validate(_abs(path), None)
        finally:
            import os
            os.unlink(path)

    def test_rejects_an_empty_scrape(self):
        from .services.medex_sync import ScrapeRejected, _validate
        path = self._write_csv([])
        try:
            with self.assertRaises(ScrapeRejected):
                _validate(_abs(path), None)
        finally:
            import os
            os.unlink(path)

    def test_hash_ignores_urls_but_not_payload(self):
        """A cosmetic URL change must not trigger a full re-import."""
        from .services.medex_sync import _hash_csv
        a = self._write_csv([["Comet", "Metformin", "500 mg", "", "S", "T",
                              "https://medex.com.bd/brands/1/"]])
        b = self._write_csv([["Comet", "Metformin", "500 mg", "", "S", "T",
                              "https://medex.com.bd/brands/999/"]])
        c = self._write_csv([["Comet", "Metformin", "850 mg", "", "S", "T",
                              "https://medex.com.bd/brands/1/"]])
        try:
            self.assertEqual(_hash_csv(_abs(a)), _hash_csv(_abs(b)))
            self.assertNotEqual(_hash_csv(_abs(a)), _hash_csv(_abs(c)))
        finally:
            import os
            for p in (a, b, c):
                os.unlink(p)

    def _last_good(self):
        from treatments.models import DrugSyncRun
        return (DrugSyncRun.objects
                .filter(state__in=[DrugSyncRun.State.SUCCESS,
                                   DrugSyncRun.State.UNCHANGED])
                .order_by("-started_at").first())

    # -- engine -------------------------------------------------------------
    def test_unchanged_catalogue_skips_the_import(self):
        """The common case: catalogue identical, so the run must not rewrite
        1.5k rows or re-run the destructive consolidation."""
        from treatments.models import DrugSyncRun
        from .services.medex_sync import run_sync
        calls = []

        def fake_call(name, *a, **kw):
            calls.append(name)
            if name == "scrape_medex_brands":
                with open(kw.get("out"), "w", newline="",
                          encoding="utf-8") as fh:
                    import csv as _csv
                    w = _csv.writer(fh)
                    w.writerow(CSV_HEADER)
                    w.writerow(["Comet", "Metformin", "500 mg", "", "S", "T",
                                "u"])
            return None

        cfg = {**self._cfg(), "backup_before_import": False}
        from unittest.mock import patch
        with patch("prescriptions.services.medex_sync.call_command",
                   side_effect=fake_call), \
            patch("prescriptions.services.medex_sync._lock_path",
                  return_value=self._lock()):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                first = run_sync(trigger="manual", force=True)
                self.assertIn("import_bddrugbank", calls)
                calls.clear()
                second = run_sync(trigger="scheduled")

        self.assertEqual(first["state"], DrugSyncRun.State.SUCCESS)
        self.assertEqual(second["state"], DrugSyncRun.State.UNCHANGED)
        # Scraped again, but never imported.
        self.assertEqual(calls, ["scrape_medex_brands"])

    def test_force_reimports_an_unchanged_catalogue(self):
        from unittest.mock import patch
        from treatments.models import DrugSyncRun
        from .services.medex_sync import run_sync

        def fake_call(name, *a, **kw):
            if name == "scrape_medex_brands":

                with open(kw.get("out"), "w", newline="",
                          encoding="utf-8") as fh:
                    import csv as _csv
                    w = _csv.writer(fh)
                    w.writerow(CSV_HEADER)
                    w.writerow(["Comet", "Metformin", "500 mg", "", "S", "T",
                                "u"])
            return None

        cfg = {**self._cfg(), "backup_before_import": False}
        calls = []
        with patch("prescriptions.services.medex_sync.call_command",
                   side_effect=lambda n, *a, **k: (calls.append(n),
                                                   fake_call(n, *a, **k))[1]), \
            patch("prescriptions.services.medex_sync._lock_path",
                  return_value=self._lock()):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                run_sync(trigger="manual", force=True)
                run_sync(trigger="manual", force=True)
        self.assertEqual(calls.count("import_bddrugbank"), 2)
        self.assertEqual(DrugSyncRun.objects.filter(
            state=DrugSyncRun.State.SUCCESS).count(), 2)

    def test_import_counters_are_parsed_into_the_run_row(self):
        from unittest.mock import patch
        from treatments.models import DrugSyncRun
        from .services.medex_sync import run_sync

        def fake_call(name, *a, **kw):
            sink = kw.get("stdout")

            if name == "scrape_medex_brands":
                with open(kw.get("out"), "w", newline="",
                          encoding="utf-8") as fh:
                    import csv as _csv
                    w = _csv.writer(fh)
                    w.writerow(CSV_HEADER)
                    w.writerow(["Comet", "Metformin", "500 mg", "", "S", "T",
                                "u"])
            elif name == "import_bddrugbank":
                sink.write("  merge 3 group(s), delete 5 row(s), "
                           "repoint 2 FK reference(s)\n")
                sink.write("\nIMPORT COMPLETE:\n")
                sink.write("  New generics created : 4\n")
                sink.write("  Existing updated     : 10\n")
                sink.write("  New brand names added: 120\n")
                sink.write("  New strengths added  : 7\n")
                sink.write("  Routes added         : 2\n")
            return None

        cfg = {**self._cfg(), "backup_before_import": False}
        with patch("prescriptions.services.medex_sync.call_command",
                   side_effect=fake_call), \
            patch("prescriptions.services.medex_sync._lock_path",
                  return_value=self._lock()):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                run_sync(trigger="manual", force=True)

        run = DrugSyncRun.objects.get()
        self.assertEqual(run.generics_created, 4)
        self.assertEqual(run.generics_updated, 10)
        self.assertEqual(run.brands_added, 120)
        self.assertEqual(run.strengths_added, 7)
        self.assertEqual(run.routes_added, 2)
        self.assertEqual(run.rows_merged, 3)
        self.assertEqual(run.rows_deleted, 5)
        self.assertEqual(run.fks_repointed, 2)

    def test_run_records_failure_and_reraises(self):

        from unittest.mock import patch
        from treatments.models import DrugSyncRun
        from .services.medex_sync import run_sync

        def boom(*a, **kw):
            raise RuntimeError("HTTP 503")

        cfg = {**self._cfg(), "backup_before_import": False}
        with patch("prescriptions.services.medex_sync.call_command",
                   side_effect=boom), \
            patch("prescriptions.services.medex_sync._lock_path",
                  return_value=self._lock()):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                with self.assertRaises(RuntimeError):
                    run_sync(trigger="scheduled")
        run = DrugSyncRun.objects.get()
        self.assertEqual(run.state, DrugSyncRun.State.FAILED)
        self.assertIn("HTTP 503", run.error)
        self.assertIsNotNone(run.finished_at)

    def test_concurrent_run_is_refused(self):
        from unittest.mock import patch
        from .services.medex_sync import SyncLockError, run_sync
        lock = self._lock("busy")
        lock.write_text('{"pid": 999}', encoding="utf-8")
        cfg = {**self._cfg()}
        with patch("prescriptions.services.medex_sync._lock_path",
                   return_value=lock):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                with self.assertRaises(SyncLockError):
                    run_sync(trigger="scheduled", force=True)
        lock.unlink()

    def test_stale_lock_is_reclaimed(self):
        import os
        import time
        from unittest.mock import patch
        from .services.medex_sync import ScrapeRejected, run_sync
        lock = self._lock("stale")
        lock.write_text('{"pid": 999}', encoding="utf-8")
        old = time.time() - 9999
        os.utime(lock, (old, old))
        cfg = {**self._cfg(), "backup_before_import": False}

        def fake_call(name, *a, **kw):
            if name == "scrape_medex_brands":
                with open(kw.get("out"), "w", newline="",
                          encoding="utf-8") as fh:
                    fh.write(",".join(CSV_HEADER) + "\n")
            return None

        with patch("prescriptions.services.medex_sync.call_command",
                   side_effect=fake_call), \
            patch("prescriptions.services.medex_sync._lock_path",
                  return_value=lock):
            with self.settings(DRUG_SYNC_CONFIG=cfg):
                # Gets past the lock, then fails validation on the empty CSV.
                with self.assertRaises(ScrapeRejected):
                    run_sync(trigger="scheduled", force=True)
        self.assertFalse(lock.exists())


class SteroidTaperTests(TestCase):
    """A systemic steroid course that ends abruptly can suppress the adrenals,
    so the slip has to carry the step-down â€” and the safety check has to notice
    when it is missing.

    The trap these tests guard: much of the formulary is `drug_class ==
    "steroid"` but is really a topical/ophthalmic combination drop, where a
    taper is meaningless. Eligibility must be narrow.
    """

    def setUp(self):
        self.p = Patient.objects.create(
            patient_id="BGD-0900", name="Taper Patient", sex="F")
        self.enc = ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 3, 1),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        self.pred = DrugMaster.objects.create(
            generic_name="Prednisolone", drug_class=DrugClass.STEROID,
            default_route="PO")
        self.eye_drop = DrugMaster.objects.create(
            generic_name="Dexamethasone + Neomycin Sulphate",
            drug_class=DrugClass.STEROID, default_route="PO")
        self.topical = DrugMaster.objects.create(
            generic_name="Betamethasone", drug_class=DrugClass.STEROID,
            default_route="TOP")

    def _item(self, drug, **kwargs):
        rx = Prescription.objects.create(encounter=self.enc)
        return PrescriptionItem.objects.create(
            prescription=rx, drug=drug, sort_order=1, **kwargs)

    # --- eligibility -------------------------------------------------------

    def test_oral_single_agent_steroid_is_eligible(self):
        self.assertTrue(is_systemic_steroid(self.pred))

    def test_combination_product_is_not_eligible(self):
        # "Dexamethasone + Neomycin" is a fixed-ratio drop, not a titratable
        # steroid course â€” despite carrying drug_class == "steroid".
        self.assertFalse(is_systemic_steroid(self.eye_drop))

    def test_non_systemic_route_is_not_eligible(self):
        self.assertFalse(is_systemic_steroid(self.topical))

    def test_non_steroid_is_not_eligible(self):
        self.assertFalse(is_systemic_steroid(DrugMaster.objects.create(
            generic_name="Ramipril", drug_class=DrugClass.RAASI,
            default_route="PO")))

    def test_a_missing_default_route_does_not_hide_the_panel(self):
        self.assertTrue(is_systemic_steroid(DrugMaster.objects.create(
            generic_name="Methylprednisolone", drug_class=DrugClass.STEROID)))

    def test_line_route_overrides_the_drug_default(self):
        item = self._item(self.pred, route="TOP", duration="6 weeks")
        self.assertFalse(needs_taper(item))

    # --- course-length parsing --------------------------------------------

    def test_course_length_converts_weeks_days_and_months(self):
        self.assertEqual(course_length_days("6 weeks"), 42)
        self.assertEqual(course_length_days("14 days"), 14)
        self.assertEqual(course_length_days("2 months"), 60)

    def test_open_ended_courses_have_no_course_length(self):
        for text in ("", "continue", "long term", "ongoing", "SOS"):
            self.assertIsNone(course_length_days(text), text)

    def test_unparseable_duration_never_raises(self):
        self.assertIsNone(course_length_days("until review"))

    # --- safety check ------------------------------------------------------

    def test_long_course_without_taper_warns(self):
        item = self._item(self.pred, duration="6 weeks", dose="40 mg")
        codes = [w.code for w in check_prescription(item.prescription)]
        self.assertIn("steroid_taper_missing", codes)

    def test_taper_plan_silences_the_warning(self):
        item = self._item(self.pred, duration="6 weeks", dose="40 mg",
                          taper_notes="40 mg 1 wk -> 20 mg 1 wk -> stop")
        codes = [w.code for w in check_prescription(item.prescription)]
        self.assertNotIn("steroid_taper_missing", codes)

    def test_short_course_does_not_warn(self):
        item = self._item(self.pred, duration="10 days", dose="40 mg")
        codes = [w.code for w in check_prescription(item.prescription)]
        self.assertNotIn("steroid_taper_missing", codes)

    def test_maintenance_steroid_does_not_warn(self):
        item = self._item(self.pred, duration="continue", dose="5 mg")
        codes = [w.code for w in check_prescription(item.prescription)]
        self.assertNotIn("steroid_taper_missing", codes)

    def test_combination_drop_never_warns(self):
        item = self._item(self.eye_drop, duration="6 weeks")
        codes = [w.code for w in check_prescription(item.prescription)]
        self.assertNotIn("steroid_taper_missing", codes)

    def test_the_warning_never_blocks_finalization(self):
        item = self._item(self.pred, duration="6 weeks")
        warn = [w for w in check_prescription(item.prescription)
                if w.code == "steroid_taper_missing"]
        self.assertEqual([w.level for w in warn], ["warning"])

    # --- print + immutability --------------------------------------------

    def test_taper_prints_on_the_slip(self):
        item = self._item(self.pred, duration="6 weeks", dose="40 mg",
                          taper_notes="40 mg 1 wk -> 20 mg 1 wk -> stop")
        html = render_prescription_html(item.prescription)
        self.assertIn("Taper before stopping", html)
        self.assertIn("40 mg 1 wk -&gt; 20 mg 1 wk -&gt; stop", html)

    def test_slip_has_no_taper_block_without_a_plan(self):
        item = self._item(self.pred, duration="6 weeks")
        self.assertNotIn("Taper before stopping",
                         render_prescription_html(item.prescription))

    def test_print_typography_is_large_enough_to_read(self):
        # Guards the "make the printed slip bigger" request: a silent CSS
        # regression back to ~9pt body text is the failure mode.
        # 2026-09-27: the scale is now in points and patient-facing text
        # (body, instructions, tapers, advice) is 12 pt (was 14.5px body with
        # 13px instructions and 12.5px advice).
        item = self._item(self.pred, duration="6 weeks")
        html = render_prescription_html(item.prescription)
        self.assertIn("font-size: 12pt; line-height: 1.35", html)
        for selector in (".instr { font-size: 12pt", ".taper { font-size: 12pt",
                         ".advice { margin-top: 7pt; font-size: 12pt"):
            self.assertIn(selector, html)
        self.assertNotIn("font-size: 12.5px;\n         line-height: 1.4;", html)

    def test_taper_notes_are_covered_by_the_content_hash(self):
        item = self._item(self.pred, duration="6 weeks", taper_notes="stop slowly")
        before = item.prescription.compute_hash()
        item.taper_notes = "stop faster"
        item.save(update_fields=["taper_notes"])
        self.assertNotEqual(before, item.prescription.compute_hash())


class PrintTypographyTests(TestCase):
    """Every print size is bumped together, so a normal regimen still fits one
    A4 page. The table grows a full-width row per taper plan."""

    def setUp(self):
        self.p = Patient.objects.create(
            patient_id="BGD-0901", name="Print Patient", sex="M")
        self.enc = ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 4, 1),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)

    def test_each_drug_gets_its_own_tbody_so_striping_cannot_shift(self):
        rx = Prescription.objects.create(encounter=self.enc)
        pred = DrugMaster.objects.create(
            generic_name="Prednisolone", drug_class=DrugClass.STEROID,
            default_route="PO")
        PrescriptionItem.objects.create(
            prescription=rx, drug=pred, duration="6 weeks", sort_order=1,
            taper_notes="reduce slowly")
        PrescriptionItem.objects.create(
            prescription=rx, drug=DrugMaster.objects.create(
                generic_name="Ramipril", drug_class=DrugClass.RAASI),
            sort_order=2)
        html = render_prescription_html(rx)
        # Two medications -> two <tbody> blocks; no nested tbody, so browsers
        # and WeasyPrint agree on the structure.
        self.assertEqual(html.count("<tbody>"), 2)
        self.assertEqual(html.count("</tbody>"), 2)
        self.assertIn("taper-row", html)

    def test_a_normal_regimen_still_fits_one_a4_page(self):
        """The type scale went up ~15%, so the page-fit budget has to be
        defended explicitly — a two-page slip gets separated from the patient
        and read as two scripts. Measured with xhtml2pdf, the pure-Python
        fallback engine: if it fits here, the WeasyPrint output fits too.
        """
        try:
            from io import BytesIO
            from xhtml2pdf import pisa
        except ImportError:  # pragma: no cover - optional engine
            self.skipTest("xhtml2pdf not installed")
        rx = Prescription.objects.create(
            encounter=self.enc, diagnosis_text="FSGS",
            comorbidities="Hypertension, Diabetes mellitus",
            investigations_advised="Serum creatinine, UPCR",
            advice="Low-salt diet. Paracetamol 500 mg up to 3x/day if fever.")
        pred = DrugMaster.objects.create(
            generic_name="Prednisolone", drug_class=DrugClass.STEROID,
            default_route="PO")
        regimen = [(pred, "40 mg", "8 weeks",
                    "TAPER BEFORE STOPPING. 40 mg 1+0+0 x 1 wk, then 20 mg 1+0+0 "
                    "x 1 wk, then 10 mg 1+0+0 x 1 wk, then 5 mg 1+0+0 x 5 days, "
                    "then stop. Do not stop this steroid suddenly.")]
        regimen += [
            (DrugMaster.objects.create(
                generic_name=name, drug_class=cls, default_route="PO"),
             strength, "continue", "")
            for name, cls, strength in [
                ("Ramipril", DrugClass.RAASI, "5 mg"),
                ("Dapagliflozin", DrugClass.SGLT2I, "10 mg"),
            ]
        ]
        for i, (drug, strength, duration, taper) in enumerate(regimen, start=1):
            PrescriptionItem.objects.create(
                prescription=rx, drug=drug, strength=strength, dose=strength,
                route="PO", frequency="1+0+0", duration=duration,
                taper_notes=taper, sort_order=i)

        out = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(render_prescription_html(rx).encode("utf-8")), out,
            encoding="utf-8")
        data = out.getvalue()
        pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
        self.assertFalse(pdf.err)
        self.assertEqual(pages, 1)


class PrescriptionFormTaperTests(TestCase):
    """The guided entry form is where the taper is actually captured, so both
    the GET render and the POST round-trip are covered â€” a template typo would
    otherwise only surface in the browser."""

    def setUp(self):
        self.user = User.objects.create_user("prescriber", password="pw")
        self.client.force_login(self.user)
        self.p = Patient.objects.create(
            patient_id="BGD-0902", name="Form Patient", sex="M")
        ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 5, 4),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        self.pred = DrugMaster.objects.create(
            generic_name="Prednisolone", drug_class=DrugClass.STEROID,
            default_route="PO", available_strengths=["5 mg", "40 mg"],
            default_frequency="1+0+0")
        self.ramipril = DrugMaster.objects.create(
            generic_name="Ramipril", drug_class=DrugClass.RAASI,
            default_route="PO", available_strengths=["5 mg"])

    def test_form_renders_the_taper_panel_and_presets(self):
        resp = self.client.get(reverse("clinic:prescription", args=[self.p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "taper-presets")
        self.assertContains(resp, "Taper this course before stopping")
        # Presets reach the browser as JSON for the row's dropdown.
        self.assertEqual(len(resp.context["taper_presets"]), len(TAPER_PRESETS))

    def test_only_systemic_steroids_are_marked_taperable(self):
        DrugMaster.objects.create(
            generic_name="Dexamethasone + Neomycin Sulphate",
            drug_class=DrugClass.STEROID, default_route="PO")
        resp = self.client.get(reverse("clinic:prescription", args=[self.p.pk]))
        data = resp.context["drug_data"]
        self.assertTrue(data[str(self.pred.pk)]["systemic_steroid"])
        combo = DrugMaster.objects.get(
            generic_name="Dexamethasone + Neomycin Sulphate")
        self.assertFalse(data[str(combo.pk)]["systemic_steroid"])
        self.assertFalse(data[str(self.ramipril.pk)]["systemic_steroid"])

    def test_post_saves_the_taper_plan(self):
        self.client.post(reverse("clinic:prescription", args=[self.p.pk]), {
            "drug_1": str(self.pred.pk), "strength_1": "40 mg",
            "route_1": "PO", "frequency_1": "1+0+0", "timing_1": "after",
            "duration_1": "6 weeks",
            "taper_1": "40 mg 1 wk -> 20 mg 1 wk -> stop",
        })
        item = PrescriptionItem.objects.get(drug=self.pred)
        self.assertEqual(item.duration, "6 weeks")
        self.assertEqual(item.taper_notes, "40 mg 1 wk -> 20 mg 1 wk -> stop")

    def test_taper_plan_carries_forward_to_the_next_prescription(self):
        self.client.post(reverse("clinic:prescription", args=[self.p.pk]), {
            "drug_1": str(self.pred.pk), "strength_1": "40 mg",
            "route_1": "PO", "frequency_1": "1+0+0", "timing_1": "after",
            "duration_1": "6 weeks", "taper_1": "stop slowly",
        })
        finalize_prescription(Prescription.objects.get())
        ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 6, 8),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        resp = self.client.get(reverse("clinic:prescription", args=[self.p.pk]))
        self.assertEqual(resp.context["rows_data"][0]["taper"], "stop slowly")


class LongStrengthTests(TestCase):
    """Combination products carry multi-ingredient strength strings.

    The BD DrugBank formulary contains strengths up to 51 characters, e.g.
    "1000 mg+327 mg (Conventional calcium)+500 mg+400 IU". At the old
    max_length=40 these were offered in the prescription form's strength picker
    and then overflowed PrescriptionItem.strength/dose on PostgreSQL
    (DataError) while SQLite accepted them silently. max_length is now 120 for
    both fields, the importer refuses anything longer, and the view clips a
    hand-crafted over-long POST.
    """

    LONGEST_FORMULARY_STRENGTH = (
        "1000 mg+327 mg (Conventional calcium)+500 mg+400 IU"
    )

    def setUp(self):
        self.user = User.objects.create_user("strength_user", password="pw")
        self.client.force_login(self.user)
        self.p = Patient.objects.create(
            patient_id="BGD-0903", name="Strength Patient", sex="F")
        ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 5, 4),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        self.calcium = DrugMaster.objects.create(
            generic_name="Calcium Lactate Gluconate + Calcium Carbonate + Vitamin C + Vitamin D3",
            drug_class=DrugClass.OTHER, default_route="PO",
            available_strengths=[self.LONGEST_FORMULARY_STRENGTH])

    def test_model_allows_the_longest_real_formulary_strength(self):
        self.assertGreaterEqual(
            PrescriptionItem._meta.get_field("strength").max_length,
            len(self.LONGEST_FORMULARY_STRENGTH))
        # Strength and dose are separate facts (2026-09-27); both hold a
        # combination-product string without truncation.
        self.assertEqual(
            PrescriptionItem._meta.get_field("dose").max_length,
            PrescriptionItem._meta.get_field("strength").max_length)

    def test_real_formulary_strength_round_trips(self):
        resp = self.client.post(reverse("clinic:prescription", args=[self.p.pk]), {
            "drug_1": str(self.calcium.pk),
            "strength_1": self.LONGEST_FORMULARY_STRENGTH,
            "route_1": "PO", "frequency_1": "1+0+0", "timing_1": "after",
            "duration_1": "continue",
        })
        self.assertEqual(resp.status_code, 302)
        item = PrescriptionItem.objects.get(drug=self.calcium)
        self.assertEqual(item.strength, self.LONGEST_FORMULARY_STRENGTH)
        # Replaced 2026-09-27 (entry-linkage review): the old assertion
        # (dose == strength) enshrined copying the product strength into the
        # administered dose. No dose was stated, so none is stored; the
        # regimen amount used by reconciliation is still the strength.
        self.assertEqual(item.dose, "")
        self.assertEqual(item.regimen_dose, self.LONGEST_FORMULARY_STRENGTH)

    def test_absurdly_long_posted_strength_is_clipped_not_rejected(self):
        limit = PrescriptionItem._meta.get_field("strength").max_length
        resp = self.client.post(reverse("clinic:prescription", args=[self.p.pk]), {
            "drug_1": str(self.calcium.pk),
            "strength_1": "9" * (limit + 500), "dose_1": "8" * (limit + 500),
            "route_1": "P" * 50, "frequency_1": "f" * 200,
            "duration_1": "d" * 200, "brand_1": "b" * 300,
            "timing_1": "after",
        })
        self.assertEqual(resp.status_code, 302)
        item = PrescriptionItem.objects.get(drug=self.calcium)
        self.assertEqual(len(item.strength), limit)
        self.assertEqual(len(item.dose), limit)
        self.assertEqual(len(item.route), 20)
        self.assertEqual(len(item.frequency), 40)
        self.assertEqual(len(item.duration), 40)
        self.assertEqual(len(item.brand), 120)

    def test_form_inputs_declare_maxlength_matching_the_model(self):
        resp = self.client.get(reverse("clinic:prescription", args=[self.p.pk]))
        html = resp.content.decode()
        # (input name, css class, model field the limit comes from)
        for name, css, field in (
            ("strength", "strength-inp", "strength"),
            ("brand", "brand-inp", "brand"),
            ("frequency", "freq-inp", "frequency"),
            ("duration", "dur-inp", "duration"),
        ):
            with self.subTest(field=field):
                limit = PrescriptionItem._meta.get_field(field).max_length
                self.assertIn(
                    f'name="{name}_1" class="{css}" maxlength="{limit}"', html)

    def test_importer_refuses_a_strength_longer_than_the_field(self):
        from prescriptions.management.commands.import_bddrugbank import MAX_STRENGTH
        self.assertGreaterEqual(MAX_STRENGTH, len(self.LONGEST_FORMULARY_STRENGTH))
        self.assertEqual(
            MAX_STRENGTH, PrescriptionItem._meta.get_field("strength").max_length)


def _base_dir():
    from django.conf import settings
    return settings.BASE_DIR


def _abs(path):
    from pathlib import Path
    return Path(path)




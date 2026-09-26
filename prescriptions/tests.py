"""
Tests for the medication reconciliation engine â€” open / continue / change /
close, plus idempotency and the cross-visit episode history.
"""
import datetime as dt

from django.test import TestCase

from encounters.models import ClinicalEncounter
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster, StopReason, TreatmentExposure

from .models import Prescription, PrescriptionItem
from .services.finalize import finalize_prescription
from .services.reconciliation import (AlreadyReconciled, apply_reconciliation,
                                      plan_reconciliation)

# Column order `import_bddrugbank`'s DictReader expects. Without this header
# row DictReader consumes the first data row as field names and imports
# nothing -- silently.
CSV_HEADER = ["name", "generic_name", "strength", "therapeutic_class",
              "company", "dosage_form", "medex_url"]


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
                  return_value=_data_dir() / "t.lock"):
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
                  return_value=_data_dir() / "t.lock"):
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
                  return_value=_data_dir() / "t.lock"):
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
                  return_value=_data_dir() / "t.lock"):
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
        lock = _data_dir() / "busy.lock"
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
        lock = _data_dir() / "stale.lock"
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


def _data_dir():
    import tempfile
    from pathlib import Path
    d = Path(tempfile.gettempdir()) / "bgddr_drugsync_tests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _base_dir():
    from django.conf import settings
    return settings.BASE_DIR


def _abs(path):
    from pathlib import Path
    return Path(path)




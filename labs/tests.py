"""
Tests for the longitudinal labs module: eGFR derivation (versioned), the
order→result fulfillment loop, the cached-eGFR loop into prescription safety,
and the eGFR slope.
"""
import datetime as dt

from django.core.management import call_command
from django.test import TestCase

from encounters.models import ClinicalEncounter
from patients.models import Patient

from .models import LabResult
from .services.egfr import ckd_epi_2021
from .services.ordering import order_panel
from .services.results import egfr_slope, record_result


class EgfrFormulaTests(TestCase):
    def test_ckd_epi_2021_reference_values(self):
        # 60-year-old: female has lower eGFR than male at same creatinine.
        egfr_f, ver = ckd_epi_2021(1.0, 60, "F")
        egfr_m, _ = ckd_epi_2021(1.0, 60, "M")
        self.assertEqual(ver, "CKD-EPI-2021-creatinine")
        self.assertTrue(60 < egfr_f < 95)
        self.assertTrue(egfr_m > egfr_f)
        # Higher creatinine -> lower eGFR.
        low, _ = ckd_epi_2021(4.0, 60, "M")
        self.assertTrue(low < 30)


class LabResultTests(TestCase):
    def setUp(self):
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="BGD-L1", name="Lab Patient", sex="M",
            dob=dt.date(1966, 1, 1))

    def test_creatinine_derives_egfr_and_updates_patient(self):
        record_result(self.p, "creatinine", result_date=dt.date(2026, 1, 1),
                      value_numeric=2.5)
        egfr = LabResult.objects.get(patient=self.p, test__code="egfr")
        self.assertEqual(egfr.source, LabResult.Source.DERIVED)
        self.assertEqual(egfr.formula_version, "CKD-EPI-2021-creatinine")
        self.assertIsNotNone(egfr.derived_from)
        self.p.refresh_from_db()
        self.assertEqual(self.p.latest_egfr, egfr.value_numeric)

    def test_high_creatinine_flagged(self):
        r = record_result(self.p, "creatinine", result_date=dt.date(2026, 1, 1),
                          value_numeric=3.0)
        self.assertEqual(r.flag, LabResult.Flag.HIGH)

    def test_latest_egfr_tracks_most_recent(self):
        record_result(self.p, "creatinine", result_date=dt.date(2026, 1, 1),
                      value_numeric=2.0)
        record_result(self.p, "creatinine", result_date=dt.date(2026, 6, 1),
                      value_numeric=3.5)
        self.p.refresh_from_db()
        june = LabResult.series(self.p, "egfr").last()
        self.assertEqual(self.p.latest_egfr, june.value_numeric)

    def test_order_panel_then_fulfil(self):
        enc = ClinicalEncounter.objects.create(
            patient=self.p, encounter_date=dt.date(2026, 1, 1))
        order = order_panel(enc, "renal_monitoring")
        self.assertEqual(order.status, order.Status.ORDERED)
        # Fulfil every ordered item.
        for item in order.items.all():
            record_result(self.p, item.test.code,
                          result_date=dt.date(2026, 1, 3),
                          value_numeric=1.0, order_item=item)
        order.refresh_from_db()
        self.assertEqual(order.status, order.Status.RESULTED)

    def test_egfr_slope(self):
        record_result(self.p, "creatinine", result_date=dt.date(2025, 1, 1),
                      value_numeric=1.5)
        record_result(self.p, "creatinine", result_date=dt.date(2026, 1, 1),
                      value_numeric=2.5)
        slope = egfr_slope(self.p)
        # Creatinine rose, so eGFR fell -> negative slope.
        self.assertIsNotNone(slope)
        self.assertTrue(slope < 0)

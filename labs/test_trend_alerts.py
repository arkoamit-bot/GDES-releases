"""Tests for lab trend alerts (Phase 3.1)."""
import datetime as dt

from django.test import TestCase

from patients.models import Patient
from labs.models import LabTest, LabResult
from .trend_alerts import (
    detect_egfr_trends, detect_creatinine_trends,
    detect_proteinuria_trends, detect_all_trends,
)


class LabTrendAlertTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="TRD-001", name="Trend Test", sex="M",
            dob=dt.date(1980, 1, 1),
        )
        self.egfr_test = LabTest.objects.create(name="eGFR", code="egfr", default_unit="mL/min/1.73m²")
        self.cr_test = LabTest.objects.create(name="Creatinine", code="creatinine", default_unit="mg/dL")
        self.upcr_test = LabTest.objects.create(name="UPCR", code="upcr", default_unit="g/g")

    def _make_result(self, test, value, days_ago):
        return LabResult.objects.create(
            patient=self.patient, test=test,
            value_numeric=str(value),
            result_date=dt.date.today() - dt.timedelta(days=days_ago),
            sample_date=dt.date.today() - dt.timedelta(days=days_ago),
        )

    def test_egfr_rapid_decline(self):
        self._make_result(self.egfr_test, 60, 60)
        self._make_result(self.egfr_test, 50, 10)  # 16.7% decline → warning
        alerts = detect_egfr_trends(self.patient)
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].code, "egfr_rapid_decline")
        self.assertEqual(alerts[0].severity, "warning")

    def test_egfr_critical_decline(self):
        self._make_result(self.egfr_test, 80, 60)
        self._make_result(self.egfr_test, 50, 10)
        alerts = detect_egfr_trends(self.patient)
        self.assertEqual(alerts[0].severity, "critical")

    def test_egfr_stable_no_alert(self):
        self._make_result(self.egfr_test, 70, 60)
        self._make_result(self.egfr_test, 68, 10)
        alerts = detect_egfr_trends(self.patient)
        self.assertEqual(len(alerts), 0)

    def test_ckd_stage_progression(self):
        self._make_result(self.egfr_test, 48, 60)  # G3a
        self._make_result(self.egfr_test, 28, 10)  # G3b
        alerts = detect_egfr_trends(self.patient)
        self.assertTrue(any(a.code == "ckd_stage_progression" for a in alerts))

    def test_creatinine_spike(self):
        self._make_result(self.cr_test, 1.0, 5)
        self._make_result(self.cr_test, 2.0, 1)
        alerts = detect_creatinine_trends(self.patient)
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].code, "creatinine_spike")

    def test_creatinine_stable_no_alert(self):
        self._make_result(self.cr_test, 1.0, 5)
        self._make_result(self.cr_test, 1.1, 1)
        alerts = detect_creatinine_trends(self.patient)
        self.assertEqual(len(alerts), 0)

    def test_nephrotic_proteinuria_new(self):
        self._make_result(self.upcr_test, 2.0, 30)
        self._make_result(self.upcr_test, 4.0, 5)
        alerts = detect_proteinuria_trends(self.patient)
        self.assertTrue(any(a.code == "nephrotic_proteinuria_new" for a in alerts))

    def test_proteinuria_increasing(self):
        self._make_result(self.upcr_test, 1.0, 30)
        self._make_result(self.upcr_test, 2.0, 5)
        alerts = detect_proteinuria_trends(self.patient)
        self.assertTrue(any(a.code == "proteinuria_increasing" for a in alerts))

    def test_proteinuria_stable_no_alert(self):
        self._make_result(self.upcr_test, 1.0, 30)
        self._make_result(self.upcr_test, 1.1, 5)
        alerts = detect_proteinuria_trends(self.patient)
        self.assertEqual(len(alerts), 0)

    def test_detect_all_trends(self):
        self._make_result(self.egfr_test, 90, 60)
        self._make_result(self.egfr_test, 50, 10)
        self._make_result(self.cr_test, 1.0, 5)
        self._make_result(self.cr_test, 2.5, 1)
        alerts = detect_all_trends(self.patient)
        self.assertGreater(len(alerts), 0)
        # Critical alerts should come first
        critical = [a for a in alerts if a.severity == "critical"]
        self.assertGreater(len(critical), 0)

    def test_insufficient_data_no_alerts(self):
        self._make_result(self.egfr_test, 70, 10)
        alerts = detect_egfr_trends(self.patient)
        self.assertEqual(len(alerts), 0)

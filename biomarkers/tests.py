"""
Tests for biomarker kinetics: anti-PLA2R >=50% decline + seroconversion dates,
complement recovery, the Study 6 predictor 2x2, and cohort grouping by early
antibody response.
"""
import datetime as dt

from django.core.management import call_command
from django.test import TestCase

from analytics.services.outcomes import compute_patient_outcome
from labs.services.results import record_result
from patients.models import Patient

from .models import BiomarkerKinetics
from .services.kinetics import compute_biomarker_kinetics
from .services.predictor import pla2r_remission_predictor


class KineticsTests(TestCase):
    def setUp(self):
        call_command("seed_labs", verbosity=0)
        self.idx = dt.date(2024, 1, 1)

    def _p(self, pid, dx="Membranous nephropathy"):
        return Patient.objects.create(
            patient_id=pid, name=pid, sex="M", dob=dt.date(1970, 1, 1),
            enrollment_date=self.idx, primary_diagnosis=dx)

    def test_pla2r_50pct_decline_and_seroconversion(self):
        p = self._p("BM1")
        record_result(p, "anti_pla2r", result_date=self.idx, value_numeric=200)
        record_result(p, "anti_pla2r", result_date=self.idx + dt.timedelta(days=30), value_numeric=80)
        record_result(p, "anti_pla2r", result_date=self.idx + dt.timedelta(days=180), value_numeric=10)
        bk = compute_biomarker_kinetics(p)
        self.assertTrue(bk.pla2r_50pct_decline)
        self.assertEqual(bk.pla2r_50pct_date, self.idx + dt.timedelta(days=30))  # 80 <= 100
        self.assertEqual(bk.pla2r_50pct_days, 30)
        self.assertTrue(bk.early_pla2r_responder(within_days=90))
        # 10 RU/mL < 20 negative cut-off -> immunological remission at day 180.
        self.assertTrue(bk.pla2r_immunological_remission)
        self.assertEqual(bk.pla2r_remission_date, self.idx + dt.timedelta(days=180))
        self.assertAlmostEqual(float(bk.pla2r_pct_decline), 95.0, places=1)

    def test_no_early_response_when_slow_decline(self):
        p = self._p("BM2")
        record_result(p, "anti_pla2r", result_date=self.idx, value_numeric=200)
        record_result(p, "anti_pla2r", result_date=self.idx + dt.timedelta(days=200), value_numeric=90)
        bk = compute_biomarker_kinetics(p)
        self.assertTrue(bk.pla2r_50pct_decline)            # reached, but late
        self.assertFalse(bk.early_pla2r_responder(within_days=90))

    def test_complement_recovery(self):
        p = self._p("BM3", dx="Lupus nephritis")
        record_result(p, "c3", result_date=self.idx, value_numeric=40)        # low
        record_result(p, "c3", result_date=self.idx + dt.timedelta(days=90), value_numeric=95)  # normal (>=90)
        bk = compute_biomarker_kinetics(p)
        self.assertTrue(bk.c3_recovered)
        self.assertEqual(bk.c3_recovered_date, self.idx + dt.timedelta(days=90))


class PredictorTests(TestCase):
    def setUp(self):
        call_command("seed_labs", verbosity=0)
        self.idx = dt.date(2024, 1, 1)

    def _mn(self, pid, early_responder, remits):
        p = Patient.objects.create(
            patient_id=pid, name=pid, sex="M", dob=dt.date(1970, 1, 1),
            enrollment_date=self.idx, primary_diagnosis="Membranous nephropathy")
        record_result(p, "anti_pla2r", result_date=self.idx, value_numeric=200)
        # Early responder: 50% decline by day 30; else by day 200.
        drop_day = 30 if early_responder else 200
        record_result(p, "anti_pla2r", result_date=self.idx + dt.timedelta(days=drop_day), value_numeric=80)
        # Proteinuria: remit (complete <0.3) within 12 months or not.
        record_result(p, "utp_24h", result_date=self.idx, value_numeric=6.0)
        if remits:
            record_result(p, "utp_24h", result_date=self.idx + dt.timedelta(days=180), value_numeric=0.2)
            record_result(p, "utp_24h", result_date=self.idx + dt.timedelta(days=300), value_numeric=0.15)
        else:
            record_result(p, "utp_24h", result_date=self.idx + dt.timedelta(days=300), value_numeric=5.0)
        compute_patient_outcome(p)
        compute_biomarker_kinetics(p)
        return p

    def test_predictor_2x2(self):
        # Early responders mostly remit; non-responders mostly don't.
        for i in range(4):
            self._mn(f"ER{i}", early_responder=True, remits=True)
        self._mn("ERX", early_responder=True, remits=False)     # 1 FP
        for i in range(4):
            self._mn(f"NR{i}", early_responder=False, remits=False)
        self._mn("NRX", early_responder=False, remits=True)     # 1 FN
        res = pla2r_remission_predictor(Patient.objects.all())
        self.assertEqual(res["table"], {"TP": 4, "FP": 1, "FN": 1, "TN": 4})
        self.assertAlmostEqual(res["sensitivity"], 0.8, places=2)
        self.assertAlmostEqual(res["specificity"], 0.8, places=2)
        self.assertGreater(res["relative_risk"], 1.0)

    def test_cohort_group_by_pla2r_response(self):
        from analytics.services.cohort import split_patients
        self._mn("G1", early_responder=True, remits=True)
        self._mn("G2", early_responder=False, remits=False)
        groups = split_patients(Patient.objects.all(), "biomarker:pla2r_response")
        self.assertEqual(set(groups), {"PLAR early responder".replace("PLAR", "PLA2R"),
                                       "PLA2R non-responder"})

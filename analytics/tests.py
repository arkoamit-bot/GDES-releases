"""
Analytics tests.

Survival math is validated against the classic Freireich et al. (1963) 6-MP
leukaemia dataset — the canonical Kaplan-Meier / log-rank teaching example with
widely published reference values (KM survival points and log-rank chi-square
~16.8). If our pure-Python implementation reproduces those, it's trustworthy.
"""
import datetime as dt

from django.test import TestCase

from encounters.models import ClinicalEvent
from labs.services.results import record_result
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster, TreatmentExposure

from .services import survival as S
from .services import cox as C
from .services.cohort import cohort_survival, cox_regression, split_patients
from .services.outcomes import compute_patient_outcome

# Freireich 6-MP group (weeks); censored marked with event=False.
SIXMP = [
    (6, True), (6, True), (6, True), (6, False), (7, True), (9, False),
    (10, True), (10, False), (11, False), (13, True), (16, True), (17, False),
    (19, False), (20, False), (22, True), (23, True), (25, False), (32, False),
    (32, False), (34, False), (35, False),
]
# Placebo group — all events, no censoring.
PLACEBO = [(t, True) for t in
           [1, 1, 2, 2, 3, 4, 4, 5, 5, 8, 8, 8, 8, 11, 11, 12, 12, 15, 17, 22, 23]]


class SurvivalMathTests(TestCase):
    def test_km_matches_published_6mp_values(self):
        d = [x[0] for x in SIXMP]
        e = [x[1] for x in SIXMP]
        steps = S.kaplan_meier(d, e)
        surv = {s.time: s.survival for s in steps}
        # Published S(t) for the 6-MP group.
        expected = {6: 0.857, 7: 0.807, 10: 0.753, 13: 0.690,
                    16: 0.627, 22: 0.538, 23: 0.448}
        for t, val in expected.items():
            self.assertAlmostEqual(surv[t], val, places=2,
                                   msg=f"S({t}) = {surv[t]} != {val}")

    def test_logrank_matches_published_chi_square(self):
        d1 = [x[0] for x in SIXMP]; e1 = [x[1] for x in SIXMP]
        d2 = [x[0] for x in PLACEBO]; e2 = [x[1] for x in PLACEBO]
        lr = S.logrank_test(d1, e1, d2, e2)
        # Published chi-square ~16.79, p ~4e-5.
        self.assertAlmostEqual(lr.chi_square, 16.79, delta=0.3)
        self.assertLess(lr.p_value, 0.001)
        self.assertEqual(lr.df, 1)

    def test_median_survival(self):
        steps = S.kaplan_meier([x[0] for x in PLACEBO], [x[1] for x in PLACEBO])
        # Placebo median is 8 weeks (well established).
        self.assertEqual(S.median_survival(steps), 8)

    def test_nelson_aalen_monotone(self):
        d = [x[0] for x in SIXMP]; e = [x[1] for x in SIXMP]
        na = S.nelson_aalen(d, e)
        hazards = [s.cum_hazard for s in na]
        self.assertEqual(hazards, sorted(hazards))   # non-decreasing

    def test_incidence_rate(self):
        rate, n_events, py = S.incidence_rate([365.25, 365.25], [True, False])
        self.assertEqual(n_events, 1)
        self.assertEqual(py, 2.0)
        self.assertAlmostEqual(rate, 50.0, places=1)   # 1 event / 2 py * 100


class CoxPHTests(TestCase):
    def test_chi2_sf_known_values(self):
        import math
        # df=1: exact erfc form.
        self.assertAlmostEqual(C._chi2_sf(3.84, 1), math.erfc(math.sqrt(3.84 / 2)), places=6)
        # df=2: closed form sf = exp(-x/2).
        self.assertAlmostEqual(C._chi2_sf(5.0, 2), math.exp(-2.5), places=5)

    def test_score_test_equals_logrank_when_no_ties(self):
        # No tied event times -> Breslow Cox score test == log-rank exactly.
        a_t, b_t = [2, 5, 9, 12, 18], [1, 4, 7, 10, 15]
        durations = a_t + b_t
        events = [True] * 10
        X = [[0.0]] * 5 + [[1.0]] * 5
        chi2_cox, _ = C.cox_score_test(X, durations, events)
        lr = S.logrank_test(a_t, [True] * 5, b_t, [True] * 5)
        self.assertAlmostEqual(chi2_cox, lr.chi_square, places=4)

    def test_cox_fit_recovers_freireich_hazard_ratio(self):
        # Treatment indicator: 1 = placebo (worse), 0 = 6-MP.
        durations = [t for t, _ in SIXMP] + [t for t, _ in PLACEBO]
        events = [e for _, e in SIXMP] + [e for _, e in PLACEBO]
        X = [[0.0]] * len(SIXMP) + [[1.0]] * len(PLACEBO)
        res = C.cox_fit(X, durations, events, ["placebo"])
        self.assertTrue(res.converged)
        cov = res.covariates[0]
        # Published Cox HR for placebo vs 6-MP ~ 4.5 (beta ~ 1.5), highly significant.
        self.assertTrue(3.0 < cov.hr < 7.0, f"HR={cov.hr}")
        self.assertLess(cov.p_value, 0.001)
        self.assertTrue(cov.ci_low > 1.0)   # CI excludes 1

    def test_null_covariate_has_hr_near_one(self):
        # A covariate unrelated to outcome -> HR ~ 1, CI spans 1.
        import random
        random.seed(7)
        durations = [random.randint(1, 100) for _ in range(60)]
        events = [random.random() < 0.6 for _ in range(60)]
        X = [[random.gauss(0, 1)] for _ in range(60)]
        res = C.cox_fit(X, durations, events, ["noise"])
        cov = res.covariates[0]
        self.assertTrue(cov.ci_low < 1.0 < cov.ci_high)


class OutcomeEngineTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="BGD-O1", name="Outcome P", sex="M",
            dob=dt.date(1970, 1, 1), enrollment_date=dt.date(2024, 1, 1))

    def test_sustained_40_decline_detected(self):
        # Baseline eGFR high, then a sustained drop below 60% of baseline.
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(self.p, "creatinine", result_date=dt.date(2024, 7, 1), value_numeric=2.2)
        record_result(self.p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=2.6)
        o = compute_patient_outcome(self.p)
        self.assertTrue(o.sustained_40_decline)
        self.assertIsNotNone(o.sustained_40_date)
        # Composite uses the >=50% eGFR-decline endpoint (protocol §9.2).
        self.assertEqual(o.composite_cause, "egfr_decline_50")
        self.assertTrue(o.composite_kidney_event)

    def test_eskd_event_drives_composite(self):
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        ClinicalEvent.objects.create(
            patient=self.p, event_type=ClinicalEvent.Type.ESKD,
            event_date=dt.date(2024, 6, 1))
        o = compute_patient_outcome(self.p)
        self.assertTrue(o.eskd)
        self.assertTrue(o.composite_kidney_event)
        self.assertEqual(o.composite_date, dt.date(2024, 6, 1))
        de = o.duration_event("composite_kidney_event")
        self.assertEqual(de, ((dt.date(2024, 6, 1) - dt.date(2024, 1, 1)).days, True))

    def test_censored_when_no_event(self):
        record_result(self.p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(self.p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=1.05)
        o = compute_patient_outcome(self.p)
        self.assertFalse(o.composite_kidney_event)
        days, event = o.duration_event("composite_kidney_event")
        self.assertFalse(event)
        self.assertGreater(days, 300)

    def _upcr(self, date, value):
        record_result(self.p, "upcr", result_date=date, value_numeric=value)

    def test_complete_proteinuria_remission_time_to_event(self):
        # Baseline 4.0 g/g -> drops below 0.3 at month 6 and stays low.
        self._upcr(dt.date(2024, 1, 1), 4.0)
        self._upcr(dt.date(2024, 7, 1), 0.2)
        self._upcr(dt.date(2025, 1, 1), 0.15)
        o = compute_patient_outcome(self.p)
        self.assertTrue(o.complete_remission)
        self.assertEqual(o.complete_remission_date, dt.date(2024, 7, 1))
        self.assertEqual(o.remission_status, "complete")
        self.assertEqual(float(o.nadir_upcr), 0.15)
        self.assertAlmostEqual(float(o.best_proteinuria_reduction_pct), 96.25, places=1)
        # Time-to-event works for survival analysis.
        days, event = o.duration_event("complete_remission")
        self.assertTrue(event)
        self.assertEqual(days, (dt.date(2024, 7, 1) - dt.date(2024, 1, 1)).days)

    def test_partial_remission_requires_50pct_and_subnephrotic(self):
        # 6.0 -> 2.5 : >=50% reduction and < 3.5 = partial (not complete).
        self._upcr(dt.date(2024, 1, 1), 6.0)
        self._upcr(dt.date(2024, 7, 1), 2.5)
        self._upcr(dt.date(2025, 1, 1), 2.4)
        o = compute_patient_outcome(self.p)
        self.assertTrue(o.partial_remission)
        self.assertFalse(o.complete_remission)
        self.assertEqual(o.remission_status, "partial")
        self.assertEqual(o.any_remission_date, dt.date(2024, 7, 1))

    def test_transient_dip_is_not_sustained_remission(self):
        # Dips to 0.2 once but rebounds -> NOT a sustained complete remission.
        self._upcr(dt.date(2024, 1, 1), 4.0)
        self._upcr(dt.date(2024, 7, 1), 0.2)
        self._upcr(dt.date(2025, 1, 1), 3.0)
        o = compute_patient_outcome(self.p)
        self.assertFalse(o.complete_remission)

    def test_proteinuria_relapse_after_remission(self):
        self._upcr(dt.date(2024, 1, 1), 4.0)
        self._upcr(dt.date(2024, 7, 1), 0.2)
        self._upcr(dt.date(2025, 1, 1), 2.0)   # >= 1.0 after remission = relapse
        # Note: this also breaks "sustained" complete remission; partial may hold.
        o = compute_patient_outcome(self.p)
        self.assertTrue(o.proteinuria_relapse or o.any_relapse)


class ProteinuriaRemissionTests(TestCase):
    """Disease-specific remission per protocol §9.1 / KDIGO, using 24-h UTP."""
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)

    def _p(self, dx, pid="PR-1"):
        return Patient.objects.create(
            patient_id=pid, name=pid, sex="M", dob=dt.date(1975, 1, 1),
            enrollment_date=dt.date(2024, 1, 1), primary_diagnosis=dx)

    def _prot(self, p, code, date, val):
        record_result(p, code, result_date=date, value_numeric=val)

    def test_utp_preferred_over_upcr_on_same_date(self):
        p = self._p("Membranous nephropathy")
        self._prot(p, "utp_24h", dt.date(2024, 1, 1), 4.0)
        self._prot(p, "upcr", dt.date(2024, 1, 1), 3.0)
        o = compute_patient_outcome(p)
        self.assertEqual(float(o.baseline_upcr), 4.0)   # UTP wins
        self.assertEqual(o.proteinuria_source, "utp")
        self.assertEqual(o.remission_definition, "mn")

    def test_igan_30pct_response_distinct_from_complete(self):
        p = self._p("IgA nephropathy")
        self._prot(p, "utp_24h", dt.date(2024, 1, 1), 2.0)
        self._prot(p, "utp_24h", dt.date(2024, 7, 1), 1.2)   # 40% reduction
        self._prot(p, "utp_24h", dt.date(2025, 1, 1), 1.1)
        o = compute_patient_outcome(p)
        self.assertEqual(o.remission_definition, "igan")
        self.assertTrue(o.igan_proteinuria_response)
        self.assertFalse(o.complete_remission)           # not < 0.3
        _, event = o.duration_event("igan_proteinuria_response")
        self.assertTrue(event)

    def test_lupus_complete_uses_0_5_with_preserved_egfr(self):
        p = self._p("Lupus nephritis", "PR-LN1")
        self._prot(p, "utp_24h", dt.date(2024, 1, 1), 3.0)
        self._prot(p, "utp_24h", dt.date(2024, 7, 1), 0.4)   # < 0.5, not < 0.3
        self._prot(p, "utp_24h", dt.date(2025, 1, 1), 0.35)
        o = compute_patient_outcome(p)
        self.assertEqual(o.remission_definition, "lupus")
        self.assertTrue(o.complete_remission)            # lupus CR threshold 0.5

    def test_lupus_complete_blocked_when_egfr_declines(self):
        p = self._p("Lupus nephritis", "PR-LN2")
        self._prot(p, "utp_24h", dt.date(2024, 1, 1), 3.0)
        self._prot(p, "utp_24h", dt.date(2025, 1, 1), 0.4)
        record_result(p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        record_result(p, "creatinine", result_date=dt.date(2025, 1, 1), value_numeric=3.2)
        o = compute_patient_outcome(p)
        self.assertTrue(o.sustained_50_decline)
        self.assertFalse(o.complete_remission)           # eGFR not preserved

    def test_egfr_at_picks_nearest_in_time(self):
        from analytics.services.outcomes import _egfr_at
        egfr = [(dt.date(2024, 1, 1), 90.0), (dt.date(2024, 6, 1), 70.0),
                (dt.date(2024, 12, 1), 50.0)]
        # Nearest to a mid-May date is the June draw (even though it is later).
        self.assertEqual(_egfr_at(egfr, dt.date(2024, 5, 20)), 70.0)
        # Exact match wins.
        self.assertEqual(_egfr_at(egfr, dt.date(2024, 12, 1)), 50.0)
        # Tie prefers the value on/before the date.
        egfr2 = [(dt.date(2024, 1, 1), 88.0), (dt.date(2024, 1, 11), 60.0)]
        self.assertEqual(_egfr_at(egfr2, dt.date(2024, 1, 6)), 88.0)

    def test_egfr_preserved_strict_kdigo_tolerance(self):
        from analytics.services.remission import egfr_preserved
        # Baseline normal (>=60): within 10%.
        self.assertTrue(egfr_preserved(90, 82))     # ~9% drop -> preserved
        self.assertFalse(egfr_preserved(90, 78))    # ~13% drop -> not preserved
        # Baseline reduced (<60): within 15%.
        self.assertTrue(egfr_preserved(40, 35))     # 12.5% drop -> preserved
        self.assertFalse(egfr_preserved(40, 32))    # 20% drop -> not preserved
        # Missing values do not block.
        self.assertTrue(egfr_preserved(None, 50))
        self.assertTrue(egfr_preserved(90, None))


class CohortTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.sglt2 = DrugMaster.objects.create(
            generic_name="Dapagliflozin", drug_class=DrugClass.SGLT2I)

    def _patient(self, pid, exposed, event):
        p = Patient.objects.create(
            patient_id=pid, name=pid, sex="M", dob=dt.date(1970, 1, 1),
            enrollment_date=dt.date(2024, 1, 1))
        record_result(p, "creatinine", result_date=dt.date(2024, 1, 1), value_numeric=1.0)
        if exposed:
            TreatmentExposure.objects.create(
                patient=p, drug=self.sglt2, drug_name="Dapagliflozin",
                start_date=dt.date(2024, 1, 1), ongoing=True)
        if event:
            ClinicalEvent.objects.create(
                patient=p, event_type=ClinicalEvent.Type.ESKD,
                event_date=dt.date(2024, 6, 1))
        else:
            record_result(p, "creatinine", result_date=dt.date(2025, 6, 1), value_numeric=1.05)
        compute_patient_outcome(p)
        return p

    def test_split_by_drug_exposure(self):
        self._patient("E1", True, False)
        self._patient("U1", False, True)
        groups = split_patients(Patient.objects.all(), "drug:sglt2i")
        self.assertEqual(set(groups), {"sglt2i exposed", "sglt2i unexposed"})

    def test_cohort_survival_runs_with_logrank(self):
        for i in range(4):
            self._patient(f"EX{i}", True, i == 0)    # exposed, few events
        for i in range(4):
            self._patient(f"UN{i}", False, i < 3)    # unexposed, more events
        cohort = cohort_survival(Patient.objects.all(), "drug:sglt2i",
                                 "composite_kidney_event")
        self.assertEqual(len(cohort.groups), 2)
        self.assertIsNotNone(cohort.logrank)
        self.assertIn("p_value", cohort.logrank)

    def test_cox_regression_over_cohort(self):
        for i in range(6):
            self._patient(f"EX{i}", True, i == 0)
        for i in range(6):
            self._patient(f"UN{i}", False, i < 4)
        model, meta = cox_regression(
            Patient.objects.all(), ["drug:sglt2i"], "composite_kidney_event")
        names = [c["name"] for c in model["covariates"]]
        self.assertEqual(names, ["drug:sglt2i"])
        self.assertEqual(meta["endpoint"], "composite_kidney_event")
        self.assertGreater(model["n_events"], 0)
        # Exposed group had fewer events -> protective HR (< 1) expected.
        self.assertLess(model["covariates"][0]["hr"], 1.0)

    def test_cox_regression_constant_covariate_errors_cleanly(self):
        # All patients share baseline eGFR here -> singular; must raise readable.
        self._patient("C1", True, False)
        self._patient("C2", False, True)
        with self.assertRaises(ValueError):
            cox_regression(Patient.objects.all(), ["baseline_egfr"],
                           "composite_kidney_event")

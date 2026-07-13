"""
Tests for the safety module: SAE auto-flagging, infection incidence by group
(Study 20), and per-study DSMB tabulation.
"""
import datetime as dt

from django.test import TestCase

from analytics.services.outcomes import compute_patient_outcome
from labs.services.results import record_result
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster, TreatmentExposure

from .models import AdverseEvent
from .services.summary import infection_incidence, safety_summary, study_safety


class AdverseEventModelTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="AE1", name="x", sex="M")

    def test_hospitalization_forces_serious(self):
        ae = AdverseEvent.objects.create(
            patient=self.p, onset_date=dt.date(2026, 1, 1),
            category=AdverseEvent.Category.INFECTION,
            infection_type=AdverseEvent.InfectionType.PNEUMONIA,
            severity=AdverseEvent.Severity.MODERATE, hospitalization=True)
        self.assertTrue(ae.serious)

    def test_g4_severity_forces_serious(self):
        ae = AdverseEvent.objects.create(
            patient=self.p, onset_date=dt.date(2026, 1, 1),
            category=AdverseEvent.Category.HEMATOLOGIC,
            severity=AdverseEvent.Severity.LIFE_THREATENING)
        self.assertTrue(ae.serious)

    def test_mild_event_not_serious(self):
        ae = AdverseEvent.objects.create(
            patient=self.p, onset_date=dt.date(2026, 1, 1),
            category=AdverseEvent.Category.OTHER,
            severity=AdverseEvent.Severity.MILD)
        self.assertFalse(ae.serious)


class InfectionIncidenceTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)
        self.idx = dt.date(2024, 1, 1)

    def _patient(self, pid, diabetes, n_infections):
        p = Patient.objects.create(
            patient_id=pid, name=pid, sex="M", dob=dt.date(1970, 1, 1),
            enrollment_date=self.idx, diabetes_status=diabetes)
        # One year of follow-up.
        record_result(p, "creatinine", result_date=self.idx, value_numeric=1.0)
        record_result(p, "creatinine",
                      result_date=self.idx + dt.timedelta(days=365), value_numeric=1.1)
        compute_patient_outcome(p)
        for i in range(n_infections):
            AdverseEvent.objects.create(
                patient=p, onset_date=self.idx + dt.timedelta(days=30 * (i + 1)),
                category=AdverseEvent.Category.INFECTION,
                infection_type=AdverseEvent.InfectionType.PNEUMONIA,
                severity=AdverseEvent.Severity.MODERATE)
        return p

    def test_infection_incidence_by_diabetes(self):
        # Diabetics: 2 patients, 4 infections over ~2 py -> ~200/100py.
        self._patient("D1", "t2", 2)
        self._patient("D2", "t2", 2)
        # Non-diabetics: 2 patients, 1 infection -> ~50/100py.
        self._patient("N1", "none", 1)
        self._patient("N2", "none", 0)
        res = infection_incidence(Patient.objects.all(), "diabetes")
        rows = {r["group"]: r for r in res["rows"]}
        self.assertEqual(rows["Diabetic"]["n_infections"], 4)
        self.assertEqual(rows["Non-diabetic"]["n_infections"], 1)
        self.assertGreater(rows["Diabetic"]["infections_per_100py"],
                           rows["Non-diabetic"]["infections_per_100py"])

    def test_summary_counts(self):
        p = self._patient("S1", "t2", 0)
        AdverseEvent.objects.create(
            patient=p, onset_date=self.idx, category=AdverseEvent.Category.STEROID_TOXICITY,
            severity=AdverseEvent.Severity.SEVERE, hospitalization=True)
        s = safety_summary(Patient.objects.all())
        self.assertEqual(s["n_serious"], 1)
        self.assertEqual(s["n_hospitalizations"], 1)
        self.assertEqual(s["by_category"]["steroid_toxicity"], 1)


class StudySafetyTests(TestCase):
    def test_per_arm_sae_counts(self):
        from studies.models import Study, StudyArm
        from studies.services.randomization import enroll
        s = Study.objects.create(code="SAF-1", title="t", study_type=Study.Type.RCT,
                                 randomization_scheme=Study.Scheme.BLOCK,
                                 block_multipliers=[2], requires_trial_consent=False)
        StudyArm.objects.create(study=s, code="active", name="A", order=0)
        StudyArm.objects.create(study=s, code="control", name="C", order=1)
        for i in range(4):
            p = Patient.objects.create(patient_id=f"SF{i}", name=f"SF{i}", sex="M")
            enr = enroll(s, p)
            AdverseEvent.objects.create(
                patient=p, onset_date=dt.date(2026, 1, 1),
                category=AdverseEvent.Category.INFECTION,
                infection_type=AdverseEvent.InfectionType.SEPSIS,
                severity=AdverseEvent.Severity.SEVERE, hospitalization=True)
        res = study_safety(s)
        total_serious = sum(a["serious"] for a in res["by_arm"].values())
        self.assertEqual(total_serious, 4)
        self.assertEqual(res["n_enrolled"], 4)

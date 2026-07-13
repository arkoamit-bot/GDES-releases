"""
Clinical app tests — ClinicalAssessment and VitalSign models.
"""
import datetime as dt

from django.test import TestCase

from patients.models import Patient
from patients.workflow import RegistrationStatus
from encounters.models import ClinicalEncounter

from .models import ClinicalAssessment, VitalSign


def _make_patient(**kwargs):
    defaults = {"name": "Test Patient", "sex": "M", "dob": dt.date(1990, 1, 1)}
    defaults.update(kwargs)
    return Patient.objects.create(**defaults)


def _make_encounter(patient, **kwargs):
    defaults = {"patient": patient, "encounter_date": dt.date.today()}
    defaults.update(kwargs)
    return ClinicalEncounter.objects.create(**defaults)


class ClinicalAssessmentTests(TestCase):

    def setUp(self):
        self.patient = _make_patient()
        self.encounter = _make_encounter(self.patient)

    def test_create_assessment(self):
        a = ClinicalAssessment.objects.create(
            encounter=self.encounter,
            chief_complaint="Frothy urine for 2 weeks",
            time_course="subacute",
            features=["edema", "hypertension"],
            syndrome_classification="Nephrotic syndrome",
        )
        self.assertEqual(a.encounter, self.encounter)
        self.assertEqual(a.chief_complaint, "Frothy urine for 2 weeks")
        self.assertEqual(a.time_course, "subacute")
        self.assertEqual(a.features, ["edema", "hypertension"])
        self.assertEqual(a.syndrome_classification, "Nephrotic syndrome")

    def test_defaults(self):
        a = ClinicalAssessment.objects.create(encounter=self.encounter)
        self.assertEqual(a.time_course, "subacute")
        self.assertEqual(a.features, [])
        self.assertEqual(a.severity_flags, [])
        self.assertEqual(a.chief_complaint, "")
        self.assertEqual(a.syndrome_classification, "")

    def test_str(self):
        a = ClinicalAssessment.objects.create(encounter=self.encounter)
        self.assertIn(str(self.encounter.pk), str(a))

    def test_one_to_one_constraint(self):
        ClinicalAssessment.objects.create(encounter=self.encounter)
        with self.assertRaises(Exception):
            ClinicalAssessment.objects.create(encounter=self.encounter)

    def test_time_course_choices(self):
        for tc in ("acute", "subacute", "chronic", "relapsing"):
            a = ClinicalAssessment.objects.create(
                encounter=self.encounter, time_course=tc
            )
            self.assertEqual(a.time_course, tc)
            a.delete()

    def test_severity_flags(self):
        a = ClinicalAssessment.objects.create(
            encounter=self.encounter,
            severity_flags=["critical_hypertension", "nephrotic_range"],
        )
        self.assertEqual(len(a.severity_flags), 2)
        self.assertIn("critical_hypertension", a.severity_flags)

    def test_cascade_delete_from_encounter(self):
        ClinicalAssessment.objects.create(encounter=self.encounter)
        self.encounter.delete()
        self.assertEqual(ClinicalAssessment.objects.count(), 0)


class VitalSignTests(TestCase):

    def setUp(self):
        self.patient = _make_patient()
        self.encounter = _make_encounter(self.patient)

    def test_create_vital_sign(self):
        v = VitalSign.objects.create(
            encounter=self.encounter,
            bp_systolic=120,
            bp_diastolic=80,
            heart_rate=72,
            weight_kg=65.5,
            height_cm=170.0,
        )
        self.assertEqual(v.bp_systolic, 120)
        self.assertEqual(v.bp_diastolic, 80)
        self.assertEqual(v.heart_rate, 72)
        self.assertEqual(v.weight_kg, 65.5)
        self.assertEqual(v.height_cm, 170.0)

    def test_nullable_fields(self):
        v = VitalSign.objects.create(encounter=self.encounter)
        self.assertIsNone(v.bp_systolic)
        self.assertIsNone(v.bp_diastolic)
        self.assertIsNone(v.heart_rate)
        self.assertIsNone(v.weight_kg)
        self.assertIsNone(v.height_cm)

    def test_multiple_vitals_per_encounter(self):
        """Unlike ClinicalAssessment (OneToOne), VitalSign allows multiple rows."""
        v1 = VitalSign.objects.create(
            encounter=self.encounter, bp_systolic=120, bp_diastolic=80
        )
        v2 = VitalSign.objects.create(
            encounter=self.encounter, bp_systolic=130, bp_diastolic=85
        )
        self.assertEqual(VitalSign.objects.filter(encounter=self.encounter).count(), 2)

    def test_recorded_at_auto_set(self):
        v = VitalSign.objects.create(encounter=self.encounter)
        self.assertIsNotNone(v.recorded_at)

    def test_cascade_delete_from_encounter(self):
        VitalSign.objects.create(encounter=self.encounter)
        self.encounter.delete()
        self.assertEqual(VitalSign.objects.count(), 0)

    def test_related_name(self):
        VitalSign.objects.create(
            encounter=self.encounter, bp_systolic=110, bp_diastolic=70
        )
        VitalSign.objects.create(
            encounter=self.encounter, bp_systolic=115, bp_diastolic=75
        )
        self.assertEqual(self.encounter.vitals.count(), 2)

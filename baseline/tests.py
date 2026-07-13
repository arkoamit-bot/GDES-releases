from django.test import TestCase

from patients.models import Patient

from .models import BaselineAssessment, asian_bmi_category


class BaselineTests(TestCase):
    def test_bmi_autocomputed(self):
        p = Patient.objects.create(patient_id="B1", name="x", sex="M")
        b = BaselineAssessment.objects.create(patient=p, height_cm=170, weight_kg=72)
        # 72 / 1.70^2 = 24.9
        self.assertEqual(float(b.bmi), 24.9)
        self.assertEqual(b.bmi_category, "overweight")   # Asian cutoff 23-27.4

    def test_asian_cutoffs(self):
        self.assertEqual(asian_bmi_category(18.0), "underweight")
        self.assertEqual(asian_bmi_category(21.0), "normal")
        self.assertEqual(asian_bmi_category(25.0), "overweight")
        self.assertEqual(asian_bmi_category(30.0), "obese")

    def test_bmi_cleared_without_inputs(self):
        p = Patient.objects.create(patient_id="B2", name="y", sex="F")
        b = BaselineAssessment.objects.create(patient=p)
        self.assertIsNone(b.bmi)
        self.assertEqual(b.bmi_category, "")

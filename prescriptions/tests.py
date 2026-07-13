"""
Tests for the medication reconciliation engine — open / continue / change /
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

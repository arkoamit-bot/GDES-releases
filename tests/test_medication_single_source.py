"""Medication is recorded once, as structured exposure episodes.

The baseline assessment had a free-text "Drug history" box — a third place the
same medication list got typed, after prescribing (which opens a
TreatmentExposure through the reconciliation engine) and Add medication (for
drugs started elsewhere). Text typed there reaches no exposure -> outcome
analysis and can contradict the structured record.

Its only consumer was worse than useless: it sent the medication history to
Vera Health under the key "drug_allergies_note", telling the AI a patient was
allergic to drugs they were merely taking.
"""
import pytest
from datetime import date, timedelta

from django.utils import timezone

pytestmark = pytest.mark.django_db


def _patient(pid="BGD-MED-1"):
    from patients.models import Patient
    return Patient.objects.create(
        patient_id=pid, name="Med", hospital_id=f"H-{pid}", phone="+1234567890",
        sex="F", cohort="GN", diabetes_status="none", primary_diagnosis="iga",
        current_phase="active", registration_status="active",
        registration_date=date.today(), enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now())


def _expose(patient, name="Dapagliflozin", drug_class="sglt2i", ongoing=True):
    from treatments.models import DrugMaster, TreatmentExposure
    drug, _ = DrugMaster.objects.get_or_create(
        generic_name=name, defaults={"drug_class": drug_class, "is_active": True})
    return TreatmentExposure.objects.create(
        patient=patient, drug=drug, drug_name=name, dose="10", dose_unit="mg",
        start_date=date.today() - timedelta(days=30),
        ongoing=ongoing, stop_date=None if ongoing else date.today())


class TestBaselineNoLongerRetypesMedication:
    def test_the_free_text_box_is_gone_from_the_form(self):
        from clinic.forms import BaselineForm
        assert "drug_history" not in BaselineForm(patient=_patient()).fields

    def test_the_baseline_still_asks_its_own_data(self):
        from clinic.forms import BaselineForm
        fields = BaselineForm(patient=_patient("BGD-MED-2")).fields
        for name in ("dm_duration_years", "hba1c", "notes"):
            assert name in fields

    def test_ongoing_medication_is_shown_read_only(self):
        from clinic.forms import BaselineForm
        p = _patient("BGD-MED-3")
        _expose(p)
        names = [m.drug_name for m in BaselineForm(patient=p).carried_medications()]
        assert names == ["Dapagliflozin"]

    def test_stopped_medication_is_not_listed_as_current(self):
        from clinic.forms import BaselineForm
        p = _patient("BGD-MED-4")
        _expose(p, ongoing=False)
        assert BaselineForm(patient=p).carried_medications() == []

    def test_no_patient_is_handled(self):
        from clinic.forms import BaselineForm
        assert BaselineForm().carried_medications() == []


class TestLegacyTextIsPreserved:
    """The column stays: baselines recorded before this must not lose data."""

    def test_existing_free_text_is_still_readable(self):
        from clinic.forms import BaselineForm
        from baseline.models import BaselineAssessment
        p = _patient("BGD-MED-10")
        b = BaselineAssessment.objects.create(
            patient=p, assessment_date=date.today(),
            drug_history="Prednisolone 20mg since March, tapering")
        form = BaselineForm(instance=b, patient=p)
        assert "Prednisolone" in form.legacy_drug_history()

    def test_saving_the_form_does_not_wipe_the_legacy_text(self):
        # An excluded field must be left alone, not blanked.
        from clinic.forms import BaselineForm
        from baseline.models import BaselineAssessment
        p = _patient("BGD-MED-11")
        b = BaselineAssessment.objects.create(
            patient=p, assessment_date=date.today(), drug_history="Enalapril 5mg")
        form = BaselineForm({"assessment_date": date.today().isoformat()},
                            instance=b, patient=p)
        assert form.is_valid(), form.errors
        form.save()
        b.refresh_from_db()
        assert b.drug_history == "Enalapril 5mg"

    def test_blank_history_reports_empty(self):
        from clinic.forms import BaselineForm
        from baseline.models import BaselineAssessment
        p = _patient("BGD-MED-12")
        b = BaselineAssessment.objects.create(patient=p, assessment_date=date.today())
        assert BaselineForm(instance=b, patient=p).legacy_drug_history() == ""


class TestVeraNoLongerCallsItAnAllergy:
    def test_drug_history_is_not_sent_as_an_allergy(self):
        from baseline.models import BaselineAssessment
        from clinical_evidence.services import vera_mapper
        p = _patient("BGD-MED-20")
        BaselineAssessment.objects.create(
            patient=p, assessment_date=date.today(),
            drug_history="Losartan 50mg daily")
        payload = vera_mapper.map_patient_for_vera(p)
        blob = str(payload)
        assert "drug_allergies_note" not in blob
        assert "prior_drug_history_note" in blob

    def test_current_medication_still_goes_out_structured(self):
        from clinical_evidence.services import vera_mapper
        p = _patient("BGD-MED-21")
        _expose(p)
        payload = vera_mapper.map_patient_for_vera(p)
        meds = payload.get("current_medications") or []
        assert any(m.get("medication") == "Dapagliflozin" for m in meds)

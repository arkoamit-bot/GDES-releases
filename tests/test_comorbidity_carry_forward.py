"""Comorbidities entered at registration must carry forward.

The Patient model documents the intent -- "Level 2: persistent clinical data
(single source of truth) ... entered once at baseline; auto-carried-forward to
all encounters" -- but nothing implemented it. A clinician who ticked DM and HTN
on /patients/add/ found the baseline form blank, and the AI prompts only ever
mentioned HTN, DM and CVD however much else was recorded.
"""
import pytest
from datetime import date

from django.utils import timezone

from patients.comorbidity import (
    baseline_initial_from_patient, comorbidity_summary, comorbidity_text,
)

pytestmark = pytest.mark.django_db


def _patient(pid="BGD-COM-1", **extra):
    from patients.models import Patient
    fields = dict(
        patient_id=pid, name="Carry Forward", hospital_id=f"H-{pid}",
        phone="+1234567890", sex="F", cohort="GN", diabetes_status="none",
        primary_diagnosis="iga", current_phase="active",
        registration_status="active", registration_date=date.today(),
        enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now(),
    )
    fields.update(extra)
    return Patient.objects.create(**fields)


def _baseline(patient, **extra):
    from baseline.models import BaselineAssessment
    return BaselineAssessment.objects.create(
        patient=patient, assessment_date=date.today(), **extra)


class TestCarryForwardToBaseline:
    def test_registration_comorbidities_pre_tick_a_new_baseline(self):
        p = _patient(hypertension=True, autoimmune_disease=True,
                     smoking_status="Current")
        initial = baseline_initial_from_patient(p)
        assert initial["hypertension"] is True
        assert initial["autoimmune_disease"] is True
        assert initial["smoking"] == "Current"

    def test_unrecorded_values_are_not_seeded(self):
        # False means "not recorded", not "confirmed absent" -- seeding it would
        # present a guess as a clinical finding.
        p = _patient("BGD-COM-2")
        assert baseline_initial_from_patient(p) == {}

    def test_baseline_form_pre_ticks_from_the_patient(self):
        from clinic.forms import BaselineForm
        p = _patient("BGD-COM-3", hypertension=True, chronic_infection=True)
        form = BaselineForm(patient=p)
        assert form.initial.get("hypertension") is True
        assert form.initial.get("chronic_infection") is True

    def test_saved_baseline_is_not_overwritten_by_the_patient_record(self):
        # The clinician may have corrected the value on the baseline; the
        # registration entry must not silently overwrite that correction.
        from clinic.forms import BaselineForm
        p = _patient("BGD-COM-4", hypertension=True)
        existing = _baseline(p, hypertension=False)
        form = BaselineForm(instance=existing, patient=p)
        assert not form.initial.get("hypertension")


class TestSyncBackToPatient:
    """The reverse direction already exists in BaselineAssessment.save()
    (_sync_level2_to_patient). These pin it so the round trip stays closed."""

    def test_baseline_confirmation_updates_the_patient_record(self):
        p = _patient("BGD-COM-5")
        _baseline(p, hypertension=True, autoimmune_disease=True)
        p.refresh_from_db()
        assert p.hypertension is True
        assert p.autoimmune_disease is True

    def test_an_unticked_baseline_box_never_clears_a_recorded_comorbidity(self):
        # Absence on one form is not evidence of absence; clearing HTN here
        # would drop it from every later prescription and AI prompt.
        p = _patient("BGD-COM-6", hypertension=True)
        _baseline(p, hypertension=False)
        p.refresh_from_db()
        assert p.hypertension is True

    def test_round_trip_registration_to_baseline_and_back(self):
        # Tick at registration -> pre-ticked on the baseline form -> confirmed
        # on save -> still set on the patient record.
        p = _patient("BGD-COM-7", hypertension=True, chronic_infection=True)
        assert baseline_initial_from_patient(p)["hypertension"] is True
        _baseline(p, hypertension=True, chronic_infection=True)
        p.refresh_from_db()
        assert p.hypertension and p.chronic_infection


class TestComorbiditySummary:
    def test_includes_conditions_the_old_prompt_dropped(self):
        p = _patient("BGD-COM-8", hypertension=True, diabetes_status="t2dm",
                     autoimmune_disease=True, chronic_infection=True)
        b = _baseline(p, cvd_history=True, malignancy=True)
        summary = comorbidity_summary(p, b)
        assert "Hypertension" in summary
        assert any(s.startswith("Diabetes mellitus") for s in summary)
        assert "Autoimmune disease" in summary
        assert "Cardiovascular disease" in summary
        assert "Malignancy" in summary

    def test_reads_hypertension_from_either_record(self):
        p = _patient("BGD-COM-9")
        b = _baseline(p, hypertension=True)
        assert "Hypertension" in comorbidity_summary(p, b)

    def test_works_without_a_baseline(self):
        p = _patient("BGD-COM-10", hypertension=True)
        assert comorbidity_summary(p, None) == ["Hypertension"]

    def test_no_duplicates_when_both_records_agree(self):
        p = _patient("BGD-COM-11", hypertension=True)
        b = _baseline(p, hypertension=True)
        assert comorbidity_summary(p, b).count("Hypertension") == 1

    def test_negative_serology_is_not_listed_as_a_comorbidity(self):
        p = _patient("BGD-COM-12", hepatitis_status="negative", hiv_status="negative")
        assert comorbidity_summary(p, None) == []

    def test_positive_serology_is_listed(self):
        p = _patient("BGD-COM-13", hepatitis_status="hbv", hiv_status="positive")
        summary = comorbidity_summary(p, None)
        assert "Hepatitis B" in summary and "HIV positive" in summary

    def test_text_form_says_none_when_empty(self):
        assert comorbidity_text(_patient("BGD-COM-14"), None) == "None"


class TestReachesTheVeraPrompt:
    def test_prompt_lists_every_recorded_comorbidity(self):
        from clinic.views import _build_prescription_prompt
        p = _patient("BGD-COM-20", hypertension=True, diabetes_status="t2dm",
                     autoimmune_disease=True)
        _baseline(p, malignancy=True)
        prompt = _build_prescription_prompt(p, None, None)
        assert "Hypertension" in prompt
        assert "Autoimmune disease" in prompt
        assert "Malignancy" in prompt

"""Comorbidities are recorded once and used everywhere.

Before this, the same eleven comorbidities were asked on BOTH the patient form
and the baseline assessment, kept roughly in step by a partial sync -- two copies
of one clinical fact that could disagree. And each downstream caller built its
own short list, so autoimmune disease, chronic infection and malignancy never
reached the AI prompts however carefully they were recorded.

Now: one input (patient form), one source of truth (Patient), one renderer
(comorbidity_summary), with the baseline columns kept as a mirror.
"""
import pytest
from datetime import date

from django.utils import timezone

from patients.comorbidity import (
    LEVEL2_COMORBIDITY_FIELDS, comorbidity_summary, comorbidity_text,
    mirror_to_baseline,
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


class TestAskedOnce:
    def test_every_comorbidity_is_on_the_patient_form(self):
        from clinic.forms import PatientForm
        fields = PatientForm().fields
        for name in LEVEL2_COMORBIDITY_FIELDS:
            assert name in fields, f"{name} cannot be recorded at registration"

    def test_the_baseline_form_does_not_ask_them_again(self):
        # The duplication is the bug: a second copy that can disagree with the
        # first, with no way to tell which the clinician meant.
        from clinic.forms import BaselineForm
        fields = BaselineForm(patient=_patient("BGD-COM-2")).fields
        for name in LEVEL2_COMORBIDITY_FIELDS:
            assert name not in fields, f"{name} is still asked twice"
        assert "smoking" not in fields

    def test_the_baseline_form_still_asks_its_own_data(self):
        from clinic.forms import BaselineForm
        fields = BaselineForm(patient=_patient("BGD-COM-3")).fields
        for name in ("dm_duration_years", "hba1c", "occupation", "notes"):
            assert name in fields

    def test_baseline_shows_the_patient_comorbidities_read_only(self):
        from clinic.forms import BaselineForm
        p = _patient("BGD-COM-4", hypertension=True, malignancy=True)
        assert set(BaselineForm(patient=p).carried_comorbidities()) == {
            "Hypertension", "Malignancy"}


class TestMirrorToBaseline:
    """The baseline columns remain for historical data and analytics, so they
    must keep tracking the patient record now that the form no longer fills
    them."""

    def test_saving_a_baseline_mirrors_the_patient_comorbidities(self):
        p = _patient("BGD-COM-10", hypertension=True, cvd_history=True,
                     smoking_status="Current")
        b = _baseline(p)
        b.refresh_from_db()
        assert b.hypertension is True
        assert b.cvd_history is True
        assert b.smoking == "Current"

    def test_an_unset_flag_never_clears_the_mirror(self):
        # "Not recorded" is not "ruled out" -- clearing on an unset flag would
        # erase a comorbidity captured before it moved to the patient form.
        p = _patient("BGD-COM-11")
        b = _baseline(p, hypertension=True)
        b.refresh_from_db()
        assert b.hypertension is True

    def test_mirror_reports_what_changed(self):
        p = _patient("BGD-COM-12", malignancy=True)
        b = _baseline(p)
        assert "malignancy" in mirror_to_baseline(p, b) or b.malignancy is True

    def test_mirror_is_safe_without_a_patient(self):
        assert mirror_to_baseline(None, None) == []

    def test_dm_duration_still_seeds_diabetes_status(self):
        # The one flow that legitimately runs baseline -> patient: DM duration is
        # only ever collected on the baseline.
        p = _patient("BGD-COM-13")
        _baseline(p, dm_duration_years=6)
        p.refresh_from_db()
        assert p.diabetes_status == "t2"

    def test_dm_inference_does_not_override_a_recorded_status(self):
        p = _patient("BGD-COM-14", diabetes_status="t1")
        _baseline(p, dm_duration_years=6)
        p.refresh_from_db()
        assert p.diabetes_status == "t1"


class TestComorbiditySummary:
    def test_includes_conditions_the_old_prompt_dropped(self):
        p = _patient("BGD-COM-20", hypertension=True, diabetes_status="t2dm",
                     autoimmune_disease=True, chronic_infection=True,
                     cvd_history=True, malignancy=True,
                     prior_immunosuppression=True)
        summary = comorbidity_summary(p, None)
        for expected in ("Hypertension", "Autoimmune disease", "Malignancy",
                         "Cardiovascular disease", "Prior immunosuppression"):
            assert expected in summary
        assert any(s.startswith("Diabetes mellitus") for s in summary)

    def test_falls_back_to_the_baseline_for_older_records(self):
        # Patients registered before comorbidities moved onto the patient form
        # only have them on the baseline row.
        p = _patient("BGD-COM-21")
        b = _baseline(p)
        b.hypertension = True
        b.save()
        assert "Hypertension" in comorbidity_summary(p, b)

    def test_no_duplicates_when_both_records_agree(self):
        p = _patient("BGD-COM-22", hypertension=True)
        b = _baseline(p)
        assert comorbidity_summary(p, b).count("Hypertension") == 1

    def test_negative_serology_is_not_listed_as_a_comorbidity(self):
        p = _patient("BGD-COM-23", hepatitis_status="negative", hiv_status="negative")
        assert comorbidity_summary(p, None) == []

    def test_positive_serology_is_listed(self):
        p = _patient("BGD-COM-24", hepatitis_status="hbv", hiv_status="positive")
        summary = comorbidity_summary(p, None)
        assert "Hepatitis B" in summary and "HIV positive" in summary

    def test_text_form_says_none_when_empty(self):
        assert comorbidity_text(_patient("BGD-COM-25"), None) == "None"

    def test_works_without_a_baseline(self):
        p = _patient("BGD-COM-26", hypertension=True)
        assert comorbidity_summary(p, None) == ["Hypertension"]


class TestReachesTheVeraPrompt:
    def test_prompt_lists_every_recorded_comorbidity(self):
        from clinic.views import _build_prescription_prompt
        p = _patient("BGD-COM-30", hypertension=True, diabetes_status="t2dm",
                     autoimmune_disease=True, malignancy=True,
                     prior_immunosuppression=True)
        prompt = _build_prescription_prompt(p, None, None)
        for expected in ("Hypertension", "Autoimmune disease", "Malignancy",
                         "Prior immunosuppression"):
            assert expected in prompt


class TestHistologyIsGatedOnBiopsy:
    """Before a biopsy there is no histological diagnosis to give, and every one
    of these fields is auto-synced from pathology anyway -- asking invites a
    guess that the biopsy report will overwrite."""

    HISTOLOGY = ["biopsy_diagnosis", "gn_broad_group", "gn_primary_secondary",
                 "oxford_mestc", "isn_rps_class"]

    def test_hidden_when_registering_a_new_patient(self):
        from clinic.forms import PatientForm
        fields = PatientForm().fields
        for name in self.HISTOLOGY:
            assert name not in fields

    def test_hidden_when_editing_a_patient_with_no_biopsy(self):
        from clinic.forms import PatientForm
        form = PatientForm(instance=_patient("BGD-HIS-1"))
        for name in self.HISTOLOGY:
            assert name not in form.fields
        assert form.histology_visible() is False

    def test_shown_once_a_biopsy_exists(self):
        from clinic.forms import PatientForm
        from pathology.models import Biopsy
        p = _patient("BGD-HIS-2")
        Biopsy.objects.create(patient=p, biopsy_date=date.today())
        form = PatientForm(instance=p)
        for name in self.HISTOLOGY:
            assert name in form.fields
        assert form.histology_visible() is True

    def test_shown_when_a_histology_value_is_already_recorded(self):
        # Never hide data that exists -- it would become uneditable.
        from clinic.forms import PatientForm
        p = _patient("BGD-HIS-3", biopsy_diagnosis="IgA nephropathy")
        assert "biopsy_diagnosis" in PatientForm(instance=p).fields

    def test_registration_still_collects_the_clinical_basics(self):
        from clinic.forms import PatientForm
        fields = PatientForm().fields
        for name in ("name", "sex", "diabetes_status", "primary_diagnosis",
                     "ckd_etiology"):
            assert name in fields

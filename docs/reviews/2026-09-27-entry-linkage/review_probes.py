"""Synthetic review evidence, NOT desired-behavior regression tests.

These assertions reproduce defects present on 2026-09-27. After repair, replace
them with regression tests asserting the corrected behavior. Run explicitly
with pytest; this file is intentionally outside normal test discovery.
Domain-event dispatch is disabled to isolate persistence and avoid integrations.
Use a temporary BGDDR_DATA_DIR and Django's isolated test database.
"""
from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db
DAY = date(2026, 9, 1)


@pytest.fixture(autouse=True)
def isolate_events(monkeypatch):
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)


@pytest.fixture
def patient():
    from patients.models import Patient
    return Patient.objects.create(
        patient_id="REVIEW-SYNTHETIC", name="Synthetic Review", sex="F",
        dob=date(1980, 1, 1), enrollment_date=DAY,
    )


@pytest.fixture
def signed_in(client, django_user_model):
    user = django_user_model.objects.create_user("synthetic_reviewer")
    client.force_login(user)
    return client


def test_corrected_comorbidity_reappears_from_baseline(patient):
    from baseline.models import BaselineAssessment
    from patients.comorbidity import comorbidity_summary
    patient.hypertension = True
    patient.save()
    baseline = BaselineAssessment.objects.create(patient=patient)
    patient.hypertension = False
    patient.save()
    baseline.save()
    baseline.refresh_from_db()
    assert baseline.hypertension is True
    assert "Hypertension" in comorbidity_summary(patient, baseline)


def test_current_comorbidity_rewrites_baseline_when_resaved(patient):
    from baseline.models import BaselineAssessment
    baseline = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
    assert baseline.malignancy is False
    patient.malignancy = True
    patient.save()
    baseline.notes = "Unrelated correction"
    baseline.save()
    baseline.refresh_from_db()
    assert baseline.malignancy is True


def test_baseline_hba1c_and_lab_hba1c_can_disagree(patient, signed_in):
    from baseline.models import BaselineAssessment
    from labs.models import LabTest
    from labs.services.results import record_result
    from exports.services.dataset import build_row
    response = signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
        "assessment_date": DAY.isoformat(), "hba1c": "8.2",
    })
    assert response.status_code == 302
    assert not patient.lab_results.filter(test__code="hba1c").exists()
    LabTest.objects.get_or_create(code="hba1c", defaults={"name": "HbA1c", "default_unit": "%"})
    record_result(patient, "hba1c", result_date=DAY, value_numeric="7.1")
    assert BaselineAssessment.objects.get(patient=patient).hba1c == Decimal("8.2")
    assert build_row(patient)["hba1c"] == Decimal("8.2")


def test_repeated_result_entry_duplicates_same_measurement(patient, signed_in):
    from labs.models import LabTest
    LabTest.objects.get_or_create(code="albumin", defaults={"name": "Albumin"})
    url = reverse("clinic:lab_results", args=[patient.pk])
    payload = {"result_date": DAY.isoformat(), "t_albumin": "3.2"}
    assert signed_in.post(url, payload).status_code == 302
    assert signed_in.post(url, payload).status_code == 302
    assert patient.lab_results.filter(test__code="albumin", result_date=DAY).count() == 2


def test_api_serializer_skips_creatinine_derivation(patient):
    from api.serializers import LabResultSerializer
    from labs.models import LabTest
    creat, _ = LabTest.objects.get_or_create(code="creatinine", defaults={"name": "Creatinine"})
    LabTest.objects.get_or_create(code="egfr", defaults={"name": "eGFR", "is_derived": True})
    serializer = LabResultSerializer(data={
        "patient": patient.pk, "test": creat.pk, "result_date": DAY,
        "value_numeric": "1.2", "unit": "mg/dL",
    })
    assert serializer.is_valid(), serializer.errors
    serializer.save()
    patient.refresh_from_db()
    assert not patient.lab_results.filter(test__code="egfr").exists()
    assert patient.latest_egfr is None


def test_vital_sign_and_encounter_are_independent(patient):
    from encounters.models import ClinicalEncounter
    from clinical.models import VitalSign
    from knowledge.services import extract_patient_features
    encounter = ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY)
    VitalSign.objects.create(encounter=encounter, bp_systolic=180, bp_diastolic=100)
    encounter.refresh_from_db()
    assert encounter.systolic_bp is None
    assert "hypertension" not in extract_patient_features(patient)["features"]


def test_repeat_biopsy_leaves_patient_on_first_diagnosis(patient, signed_in):
    url = reverse("clinic:biopsy", args=[patient.pk])
    assert signed_in.post(url, {
        "bx-biopsy_date": "2026-09-01", "dx-diagnosis": "IgA nephropathy",
    }).status_code == 302
    assert signed_in.post(url, {
        "bx-biopsy_date": "2026-09-20", "dx-diagnosis": "Minimal change disease",
    }).status_code == 302
    patient.refresh_from_db()
    assert patient.biopsies.order_by("-biopsy_date").first().diagnosis.diagnosis == "Minimal change disease"
    assert patient.biopsy_diagnosis == "IgA nephropathy"
    assert patient.primary_diagnosis == "IgA nephropathy"


def test_adjudication_leaves_lupus_panel_and_patient_stale(patient, signed_in):
    from pathology.models import PathologyReview
    from pathology.services.review import adjudicate
    assert signed_in.post(reverse("clinic:biopsy", args=[patient.pk]), {
        "bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "Lupus nephritis class III",
        "lupus-isn_rps_class": "III",
    }).status_code == 302
    biopsy = patient.biopsies.get()
    adjudicate(biopsy, diagnosis="Lupus nephritis class IV", isn_rps_class="IV")
    biopsy.refresh_from_db()
    patient.refresh_from_db()
    assert biopsy.reviews.get(role=PathologyReview.Role.ADJUDICATION).is_final
    assert biopsy.diagnosis.diagnosis == "Lupus nephritis class IV"
    assert biopsy.lupus.isn_rps_class == "III"
    assert patient.isn_rps_class == "III"


def test_fsgs_form_accepts_conflicting_repeated_classification(patient, signed_in):
    response = signed_in.post(reverse("clinic:biopsy", args=[patient.pk]), {
        "bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "FSGS - primary",
        "dx-primary_secondary": "primary", "fsgs-primary_secondary": "secondary",
    })
    assert response.status_code == 302
    biopsy = patient.biopsies.get()
    assert biopsy.diagnosis.primary_secondary == "primary"
    assert biopsy.fsgs.primary_secondary == "secondary"


def test_em_choice_is_not_recognized_by_feature_extractor(patient):
    from pathology.models import Biopsy
    from knowledge.services import extract_patient_features
    Biopsy.objects.create(patient=patient, biopsy_date=DAY, em_findings="foot_process_effacement")
    assert "podocyteEffacement" not in extract_patient_features(patient)["biopsy"]


def test_qualitative_result_semantics_and_aliases_are_lost(patient):
    from labs.models import LabTest
    from labs.services.results import record_result
    from knowledge.services import extract_patient_features
    for code, result in (("anca", "Negative"), ("anti_dsdna", "Positive")):
        LabTest.objects.get_or_create(code=code, defaults={"name": code})
        record_result(patient, code, result_date=DAY, value_text=result)
    labs = extract_patient_features(patient)["labs"]
    assert "anca" in labs
    assert "anaDsDna" not in labs


def test_prescription_tests_do_not_create_order_and_default_replaces_due_date(patient, signed_in):
    from encounters.models import ClinicalEncounter
    from labs.models import LabOrder
    from treatments.models import DrugMaster
    encounter = ClinicalEncounter.objects.create(
        patient=patient, encounter_date=DAY, next_due_date=date(2026, 9, 8))
    drug = DrugMaster.objects.create(generic_name="Synthetic drug", drug_class="other")
    url = reverse("clinic:prescription", args=[patient.pk])
    response = signed_in.get(url)
    assert response.status_code == 200
    suggested = response.context["default_next_visit"]
    assert suggested != encounter.next_due_date.isoformat()
    response = signed_in.post(url, {
        "drug_1": drug.pk, "strength_1": "10 mg", "frequency_1": "1+0+0",
        "investigations_advised": ["Serum creatinine"], "next_due_date": suggested,
    })
    assert response.status_code == 302
    assert encounter.prescriptions.get().investigations_advised == "Serum creatinine"
    assert not LabOrder.objects.filter(encounter=encounter).exists()
    encounter.refresh_from_db()
    assert encounter.next_due_date.isoformat() == suggested


def test_baseline_edit_drops_additional_legacy_syndromes(patient, signed_in):
    from baseline.models import BaselineAssessment
    from clinic.forms import BaselineForm
    baseline = BaselineAssessment.objects.create(
        patient=patient, presentation_syndromes=["nephrotic", "aki"])
    form = BaselineForm(instance=baseline, patient=patient)
    assert form.initial["presentation_syndromes"] == "nephrotic"
    response = signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
        "presentation_syndromes": form.initial["presentation_syndromes"],
        "notes": "Unrelated correction",
    })
    assert response.status_code == 302
    baseline.refresh_from_db()
    assert baseline.presentation_syndromes == ["nephrotic"]

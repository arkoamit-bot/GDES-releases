"""Required-behavior probes for the two user-reported GDES pages.

Synthetic database only; domain-event integrations disabled. Failures expose
current defects. Run explicitly with pytest (outside normal discovery).
"""
from datetime import date
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
    return Patient.objects.create(patient_id="REVIEW-29-SYNTHETIC", name="Synthetic",
                                  sex="F", dob=date(1980, 1, 1), enrollment_date=DAY)


@pytest.fixture
def signed_in(client, django_user_model):
    user = django_user_model.objects.create_user("review29")
    client.force_login(user)
    return client


def test_previous_prescription_diagnosis_prefills_next_entry(patient, signed_in):
    from encounters.models import ClinicalEncounter
    from prescriptions.models import Prescription
    patient.primary_diagnosis = "IgA nephropathy"
    patient.save()
    encounter = ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY)
    Prescription.objects.create(encounter=encounter, diagnosis_text="FSGS - primary",
                                status=Prescription.Status.FINAL)
    response = signed_in.get(reverse("clinic:prescription", args=[patient.pk]))
    assert response.status_code == 200
    print("DIAGNOSIS_PREFILL:", response.context["default_diagnosis"])
    assert response.context["default_diagnosis"] == "FSGS - primary"


def test_fsgs_duplicate_primary_secondary_cannot_conflict(patient, signed_in):
    response = signed_in.post(reverse("clinic:biopsy", args=[patient.pk]), {
        "bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "FSGS - primary",
        "dx-primary_secondary": "primary", "fsgs-primary_secondary": "secondary",
    })
    print("FSGS_CONFLICT:", response.status_code, "saved_biopsies=", patient.biopsies.count())
    assert response.status_code == 200, "Show the conflict and keep the form unsaved."
    assert not patient.biopsies.exists()


def test_absent_crescents_cannot_save_with_positive_percentage(patient, signed_in):
    response = signed_in.post(reverse("clinic:biopsy", args=[patient.pk]), {
        "bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "IgA nephropathy",
        "bx-crescent_pct": "25",
    })
    saved = list(patient.biopsies.values_list("crescents_present", "crescent_pct"))
    print("CRESCENT_CONFLICT:", response.status_code, saved)
    assert response.status_code == 200, "Absent with 25 percent must be reconciled, not saved."
    assert not saved


def test_percentages_above_one_hundred_are_rejected(patient, signed_in):
    response = signed_in.post(reverse("clinic:biopsy", args=[patient.pk]), {
        "bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "IgA nephropathy",
        "bx-global_sclerosis_pct": "150", "bx-ifta_pct": "120",
    })
    print("PERCENT_RANGE:", response.status_code, list(patient.biopsies.values_list(
        "global_sclerosis_pct", "ifta_pct")))
    assert response.status_code == 200
    assert not patient.biopsies.exists()

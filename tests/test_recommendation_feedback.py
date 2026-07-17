"""V8 Layer 10 — nephrologist Accept/Modify/Reject feedback capture."""
import pytest

pytestmark = pytest.mark.django_db


def _patient():
    from patients.models import Patient
    return Patient.objects.create(
        patient_id="FB-1", name="FB", hospital_id="H-FB-1", sex="M",
        cohort="GN", diabetes_status="no", registration_status="active",
    )


def _client():
    from django.test import Client
    from django.contrib.auth import get_user_model
    u = get_user_model().objects.create_superuser("fbdoc", password="x123456")
    c = Client(); c.force_login(u)
    return c


def test_reject_captures_structured_feedback():
    from feedback.models import WorkflowFeedback
    p = _patient(); c = _client()
    r = c.post(f"/patients/{p.pk}/recommendation-feedback/",
               {"action": "reject", "area": "clinical_reasoning",
                "ref": "differential:iga", "comments": "biopsy shows MN"},
               HTTP_HOST="localhost")
    assert r.status_code == 302
    wf = WorkflowFeedback.objects.get(patient=p)
    assert wf.action == "reject"
    assert wf.recommendation_ref == "differential:iga"
    assert wf.rating == 1
    assert "MN" in wf.comments


def test_accept_maps_to_high_rating():
    from feedback.models import WorkflowFeedback
    p = _patient(); c = _client()
    c.post(f"/patients/{p.pk}/recommendation-feedback/",
           {"action": "accept", "ref": "management_plan:iga"}, HTTP_HOST="localhost")
    wf = WorkflowFeedback.objects.get(patient=p)
    assert wf.action == "accept" and wf.rating == 5


def test_invalid_action_creates_nothing():
    from feedback.models import WorkflowFeedback
    p = _patient(); c = _client()
    c.post(f"/patients/{p.pk}/recommendation-feedback/",
           {"action": "bogus"}, HTTP_HOST="localhost")
    assert not WorkflowFeedback.objects.filter(patient=p).exists()

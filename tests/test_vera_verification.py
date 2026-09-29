"""Tests for concise clinical case summary — Vera Health integration."""
import pytest
from unittest.mock import patch, MagicMock
from django.test import Client
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def patient():
    from patients.models import Patient
    from django.utils import timezone
    p = Patient.objects.create(
        patient_id="VERA-TEST-001",
        name="Vera Test Patient",
        hospital_id="H-VERA-001",
        phone="+1234567890",
        sex="M",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="IgAN",
        current_phase="active",
        registration_status="active",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    return p


@pytest.fixture
def clinical_profile(patient):
    from clinical_reasoning.models import ClinicalProfile
    profile, _ = ClinicalProfile.objects.update_or_create(
        patient=patient,
        defaults={
            "differential": [
                {
                    "disease_id": "iga",
                    "disease_name": "IgA Nephropathy",
                    "confidence": 85,
                    "evidence_grade": "1",
                }
            ],
            "features_snapshot": {
                "proteinuria": "moderate",
                "latest_egfr": 45,
                "biopsy": ["Mesangial IgA deposition"],
                "labs": ["UPCR 2.5 g/g", "eGFR 45"],
            },
        },
    )
    return profile


class TestVerifyTreatmentWithVera:
    def test_post_required(self, client, user, patient):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.get(url)
        assert response.status_code == 405

    def test_requires_login(self, client, patient):
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert response.status_code == 302

    def test_no_clinical_profile(self, client, user, patient):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert response.status_code == 200
        assert b"No clinical profile available" in response.content

    def test_success_shows_case_summary(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert response.status_code == 200
        assert b"Clinical Case Summary" in response.content
        assert b"IgA Nephropathy" in response.content

    def test_case_summary_has_required_fields(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "Diagnosis" in content
        assert "eGFR" in content
        assert "Proteinuria" in content
        assert "Blood Pressure" in content
        assert "CKD Stage" in content
        assert "Serum Creatinine" in content
        assert "Kidney Biopsy" in content
        assert "Current GDES Assessment" in content

    def test_copy_for_vera_button(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert b"Copy for Vera" in response.content
        assert b"Open Vera Health" in response.content

    def test_copy_text_contains_prompt(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        content = response.content.decode()
        assert "Please review the following patient independently" in content
        assert "Confirmation or revision of the diagnosis" in content
        assert "personalised treatment plan" in content
        assert "Drug recommendations" in content

    def test_patient_data_populated(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        content = response.content.decode()
        assert "Vera Test Patient" in content or "VERA-TEST-001" in content
        assert "Male" in content
        assert "IgA Nephropathy" in content

    def test_ckd_stage_from_egfr(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        content = response.content.decode()
        assert "G3a" in content  # eGFR 45 → G3a

    def test_proteinuria_highlighted(self, client, user, patient, clinical_profile):
        client.login(username="testuser", password="testpass")
        url = f"/patients/{patient.pk}/verify-treatment/"
        response = client.post(url)
        assert b"moderate" in response.content
        assert b"case-highlight" in response.content


class TestBuildTreatmentVerificationPrompt:
    def test_prompt_generation(self, patient, clinical_profile):
        from clinic.views import _build_treatment_verification_prompt

        management_plan = {
            "first_line": [
                {
                    "drug": "ACEi/ARB",
                    "dose": "Maximum tolerated dose",
                    "duration": "Ongoing",
                    "target": "BP <130/80",
                }
            ],
            "second_line": [],
            "rescue_therapy": [],
        }

        prompt = _build_treatment_verification_prompt(patient, clinical_profile, management_plan)

        assert "Treatment Plan Verification Request" in prompt
        assert "Vera Test Patient" in prompt
        assert "IgA Nephropathy" in prompt
        assert "ACEi/ARB" in prompt
        assert "Please verify this treatment plan" in prompt

"""Tests for clinical_reasoning views (API endpoints).

Tests all three ViewSets:
  - ClinicalProfileViewSet (by_patient, reason, reason_all, explain, recent, etc.)
  - ClinicalInsightViewSet (by_patient, active_alerts, dismiss)
  - RecommendationAuditViewSet (by_patient, review, comparison)
"""
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from clinical_reasoning.models import ClinicalProfile, ClinicalInsight
from clinical_reasoning.json_util import json_safe


pytestmark = pytest.mark.django_db

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_superuser(
        username="testclinician",
        password="testpass123",
        email="test@hospital.org",
        first_name="Test",
        last_name="Clinician",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


# ---------------------------------------------------------------------------
# ClinicalProfileViewSet
# ---------------------------------------------------------------------------

class TestClinicalProfileViewSetByPatient:
    """Tests for the by_patient action."""

    def test_by_patient_missing_param(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-by-patient")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "patient_id" in resp.data["error"]

    def test_by_patient_creates_profile(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-by-patient")
        with patch("clinical_reasoning.views.reason_about_patient") as mock_reason:
            mock_profile = MagicMock()
            mock_profile.patient = patient
            mock_reason.return_value = mock_profile
            resp = authenticated_client.get(url, {"patient_id": patient.pk})
            assert resp.status_code == status.HTTP_200_OK

    def test_by_patient_not_found(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-by-patient")
        resp = authenticated_client.get(url, {"patient_id": 99999})
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestClinicalProfileViewSetReason:
    def test_reason_requires_auth(self, api_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-reason")
        resp = api_client.post(url, {"patient_id": patient.pk}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reason_missing_patient(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-reason")
        resp = authenticated_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_reason_not_found(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-reason")
        resp = authenticated_client.post(
            url, {"patient_id": 99999}, format="json"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_reason_success(self, authenticated_client, patient):
        """Reason endpoint returns 200. The view is patched to avoid
        serializing a MockProfile through a ModelSerializer."""
        url = reverse("clinical_reasoning:clinicalprofile-reason")
        with (
            patch("clinical_reasoning.views.reason_about_patient") as mock_reason,
            patch("clinical_reasoning.views.audit_clinical_reasoning"),
            patch(
                "clinical_reasoning.views.s.ClinicalProfileSerializer"
            ) as mock_ser_cls,
        ):
            mock_ser = MagicMock()
            mock_ser.data = {"reason": "mock_output"}
            mock_ser_cls.return_value = mock_ser
            mock_profile = MagicMock()
            mock_profile.care_pathway = {}
            mock_reason.return_value = mock_profile
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetReasonAll:
    def test_reason_all(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-reason-all")
        with patch("clinical_reasoning.views.recompute_all_profiles") as mock_recompute:
            mock_recompute.return_value = {"total": 5, "errors": 0}
            resp = authenticated_client.post(url)
            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["total"] == 5


class TestClinicalProfileViewSetExplain:
    def test_explain_missing_patient(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-explain")
        resp = authenticated_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_explain_not_found(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-explain")
        resp = authenticated_client.post(
            url, {"patient_id": 99999}, format="json"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_explain_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-explain")
        with patch("clinical_reasoning.views.build_full_explainability") as mock_build:
            mock_build.return_value = {"summary": "test"}
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetRecent:
    def test_recent(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-recent")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)


class TestClinicalProfileViewSetManagementPlan:
    def test_management_plan_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-management-plan")
        with patch("clinical_reasoning.views.generate_management_plan") as mock_gen, \
             patch("clinical_reasoning.views.audit_management_plan"):
            mock_plan = MagicMock()
            mock_plan.to_dict.return_value = {"disease_id": "iga"}
            mock_gen.return_value = mock_plan
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk, "disease_id": "iga"}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK

    def test_management_plan_not_found(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-management-plan")
        resp = authenticated_client.post(
            url, {"patient_id": 99999, "disease_id": "iga"}, format="json"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestClinicalProfileViewSetMonitoringPlan:
    def test_monitoring_plan_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-monitoring-plan")
        with patch("clinical_reasoning.views.generate_monitoring_plan") as mock_gen, \
             patch("clinical_reasoning.views.audit_monitoring_plan"):
            mock_plan = MagicMock()
            mock_plan.to_dict.return_value = {"disease_id": "iga"}
            mock_gen.return_value = mock_plan
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk, "disease_id": "iga"}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetFollowupSchedule:
    def test_followup_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-followup-schedule")
        with patch("clinical_reasoning.views.generate_follow_up_schedule") as mock_gen:
            mock_gen.return_value = [{"visit_id": 1}]
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["count"] == 1


class TestClinicalProfileViewSetDrugToxicity:
    def test_drug_toxicity_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-drug-toxicity")
        with patch("clinical_reasoning.views.detect_drug_toxicity") as mock_det, \
             patch("clinical_reasoning.views.audit_drug_toxicity"):
            mock_report = MagicMock()
            mock_report.to_dict.return_value = {"alerts": []}
            mock_det.return_value = mock_report
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetTreatmentFailure:
    def test_treatment_failure_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-treatment-failure")
        with patch("clinical_reasoning.views.detect_treatment_failure") as mock_det, \
             patch("clinical_reasoning.views.audit_treatment_failure"):
            mock_report = MagicMock()
            mock_report.to_dict.return_value = {"alerts": []}
            mock_det.return_value = mock_report
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetRelapseDetection:
    def test_relapse_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-relapse-detection")
        with patch("clinical_reasoning.views.detect_relapse") as mock_det, \
             patch("clinical_reasoning.views.audit_relapse"):
            mock_det.return_value = []
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK
            assert resp.data["count"] == 0


class TestClinicalProfileViewSetValidateDisease:
    def test_validate_success(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:clinicalprofile-validate-disease")
        with patch("clinical_reasoning.views.validate_disease_management") as mock_val:
            mock_report = MagicMock()
            mock_report.to_dict.return_value = {"score": 85.0}
            mock_val.return_value = mock_report
            resp = authenticated_client.post(
                url, {"patient_id": patient.pk, "disease": "iga"}, format="json"
            )
            assert resp.status_code == status.HTTP_200_OK


class TestClinicalProfileViewSetRetrospectiveValidation:
    def test_retrospective(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalprofile-retrospective-validation")
        with patch("clinical_reasoning.views.run_retrospective_validation") as mock_run:
            mock_report = MagicMock()
            mock_report.to_dict.return_value = {"total_patients": 0}
            mock_run.return_value = mock_report
            resp = authenticated_client.get(url)
            assert resp.status_code == status.HTTP_200_OK


# ---------------------------------------------------------------------------
# ClinicalInsightViewSet
# ---------------------------------------------------------------------------

class TestClinicalInsightViewSetByPatient:
    def test_by_patient_missing_param(self, authenticated_client):
        url = reverse("clinical_reasoning:clinicalinsight-by-patient")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_patient_success(self, authenticated_client, clinical_insight):
        url = reverse("clinical_reasoning:clinicalinsight-by-patient")
        resp = authenticated_client.get(
            url, {"patient_id": clinical_insight.patient.pk}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_excludes_dismissed(self, authenticated_client, clinical_insight, patient):
        """Dismissed insights are excluded from by_patient results.

        The patient fixture triggers automatic profile computation via
        signal handlers which may create additional insights, so we
        create two test insights: one dismissed and one not, then verify
        only the non-dismissed one appears."""
        from clinical_reasoning.models import ClinicalInsight

        # Mark the fixture insight as dismissed
        ClinicalInsight.objects.all().update(dismissed=True)

        # Create a fresh non-dismissed insight
        active = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.DIAGNOSTIC,
            priority=ClinicalInsight.Priority.HIGH,
            title="Active insight",
            description="Should appear",
        )

        url = reverse("clinical_reasoning:clinicalinsight-by-patient")
        resp = authenticated_client.get(
            url, {"patient_id": patient.pk}
        )
        assert resp.status_code == status.HTTP_200_OK
        # Only the active insight should be returned
        assert len(resp.data) == 1
        assert resp.data[0]["title"] == "Active insight"


class TestClinicalInsightViewSetActiveAlerts:
    def test_active_alerts(self, authenticated_client, clinical_insight):
        url = reverse("clinical_reasoning:clinicalinsight-active-alerts")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_no_info_priority_in_alerts(self, authenticated_client, clinical_insight, patient):
        """INFO-priority insights are excluded from active alerts.

        Signal handlers may have already created HIGH/CRITICAL insights,
        so we mark all existing ones as dismissed first to get a clean
        baseline, then verify only INFO insights are not returned."""
        from clinical_reasoning.models import ClinicalInsight

        # Clear existing alerts
        ClinicalInsight.objects.all().delete()

        # Create an INFO insight — should NOT appear in active alerts
        ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.MONITORING,
            priority=ClinicalInsight.Priority.INFO,
            title="Info only",
        )
        url = reverse("clinical_reasoning:clinicalinsight-active-alerts")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        # INFO insights are excluded from active alerts
        assert len(resp.data) == 0


class TestClinicalInsightViewSetDismiss:
    def test_dismiss(self, authenticated_client, clinical_insight):
        url = reverse("clinical_reasoning:clinicalinsight-dismiss", args=[clinical_insight.pk])
        resp = authenticated_client.post(url)
        assert resp.status_code == status.HTTP_200_OK
        clinical_insight.refresh_from_db()
        assert clinical_insight.dismissed is True


# ---------------------------------------------------------------------------
# RecommendationAuditViewSet
# ---------------------------------------------------------------------------

class TestRecommendationAuditViewSetByPatient:
    def test_by_patient_missing_param(self, authenticated_client):
        url = reverse("clinical_reasoning:recommendationaudit-by-patient")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_by_patient_empty(self, authenticated_client, patient):
        url = reverse("clinical_reasoning:recommendationaudit-by-patient")
        resp = authenticated_client.get(url, {"patient_id": patient.pk})
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)


class TestRecommendationAuditViewSetComparison:
    def test_comparison(self, authenticated_client):
        url = reverse("clinical_reasoning:recommendationaudit-comparison")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert "total_recommendations" in resp.data
        assert "acceptance_rate" in resp.data

    def test_comparison_with_disease(self, authenticated_client):
        url = reverse("clinical_reasoning:recommendationaudit-comparison")
        resp = authenticated_client.get(url, {"disease_id": "iga"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["disease_id"] == "iga"

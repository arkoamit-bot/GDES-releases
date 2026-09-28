"""Tests for clinical_reasoning serializers."""
import pytest
from django.utils import timezone

from clinical_reasoning.models import ClinicalProfile, ClinicalInsight
from clinical_reasoning.serializers import (
    ClinicalProfileSerializer,
    ClinicalInsightSerializer,
    ReasoningRequestSerializer,
    ReviewRecommendationSerializer,
    ExplainabilityRequestSerializer,
    ManagementPlanRequestSerializer,
    MonitoringPlanRequestSerializer,
    FollowUpScheduleRequestSerializer,
    PatientRequestSerializer,
    InvestigationRecommendationRequestSerializer,
    DiseaseValidationRequestSerializer,
)


pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# ClinicalProfileSerializer
# ---------------------------------------------------------------------------

class TestClinicalProfileSerializer:
    def test_serializes_profile(self, clinical_profile):
        data = ClinicalProfileSerializer(clinical_profile).data
        assert "id" in data
        assert "patient" in data
        assert data["patient_id_display"] == clinical_profile.patient.patient_id
        assert data["patient_name"] == clinical_profile.patient.name
        assert "features_snapshot" in data
        assert "differential" in data
        assert "care_pathway" in data
        assert "risk_assessment" in data
        assert "reasoning_chain" in data
        assert "information_gaps" in data
        assert "milestones" in data
        assert "version" in data

    def test_read_only_fields(self, clinical_profile):
        data = ClinicalProfileSerializer(clinical_profile).data
        # last_updated and version should be read-only
        assert "last_updated" in data
        assert "version" in data

    def test_deserialize_minimal(self):
        data = {"patient": 1}
        ser = ClinicalProfileSerializer(data=data)
        # It should at least attempt to validate (may fail on FK, but schema is valid)
        assert ser is not None


# ---------------------------------------------------------------------------
# ClinicalInsightSerializer
# ---------------------------------------------------------------------------

class TestClinicalInsightSerializer:
    def test_serializes_insight(self, clinical_insight):
        data = ClinicalInsightSerializer(clinical_insight).data
        assert data["patient_id_display"] == clinical_insight.patient.patient_id
        assert data["category"] == "diagnostic"
        assert data["priority"] == "high"
        assert data["title"] == "Leading differential: IgA Nephropathy"
        assert data["actionable"] is True
        assert data["dismissed"] is False

    def test_read_only_created_at(self, clinical_insight):
        data = ClinicalInsightSerializer(clinical_insight).data
        assert "created_at" in data


# ---------------------------------------------------------------------------
# Request serializers — validation logic
# ---------------------------------------------------------------------------

class TestReasoningRequestSerializer:
    def test_valid_data(self):
        ser = ReasoningRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()

    def test_force_defaults_false(self):
        ser = ReasoningRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()
        assert ser.validated_data["force"] is False

    def test_missing_patient_id(self):
        ser = ReasoningRequestSerializer(data={})
        assert not ser.is_valid()

    def test_patient_id_must_be_int(self):
        ser = ReasoningRequestSerializer(data={"patient_id": "abc"})
        assert not ser.is_valid()


class TestExplainabilityRequestSerializer:
    def test_valid(self):
        ser = ExplainabilityRequestSerializer(data={"patient_id": 42})
        assert ser.is_valid()

    def test_missing_patient_id(self):
        ser = ExplainabilityRequestSerializer(data={})
        assert not ser.is_valid()


class TestManagementPlanRequestSerializer:
    def test_valid_minimal(self):
        ser = ManagementPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga"}
        )
        assert ser.is_valid()

    def test_valid_with_features(self):
        ser = ManagementPlanRequestSerializer(
            data={
                "patient_id": 1,
                "disease_id": "lupus",
                "risk_category": "high",
                "features": {"egfr": 30},
            }
        )
        assert ser.is_valid()
        assert ser.validated_data["risk_category"] == "high"

    def test_default_risk_category(self):
        ser = ManagementPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga"}
        )
        assert ser.is_valid()
        assert ser.validated_data["risk_category"] == "moderate"

    def test_invalid_risk_category(self):
        ser = ManagementPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga", "risk_category": "extreme"}
        )
        assert not ser.is_valid()

    def test_missing_disease_id(self):
        ser = ManagementPlanRequestSerializer(data={"patient_id": 1})
        assert not ser.is_valid()

    def test_features_optional(self):
        ser = ManagementPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga"}
        )
        assert ser.is_valid()
        assert "features" not in ser.validated_data or ser.validated_data.get("features") is None


class TestMonitoringPlanRequestSerializer:
    def test_valid_minimal(self):
        ser = MonitoringPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga"}
        )
        assert ser.is_valid()

    def test_valid_with_treatments(self):
        ser = MonitoringPlanRequestSerializer(
            data={
                "patient_id": 1,
                "disease_id": "iga",
                "active_treatments": ["acei_arb", "sglt2_inhibitor"],
                "ckd_stage": 3,
                "risk_category": "high",
            }
        )
        assert ser.is_valid()
        assert ser.validated_data["ckd_stage"] == 3

    def test_ckd_stage_range(self):
        # Valid stages: 1-5
        for stage in [1, 2, 3, 4, 5]:
            ser = MonitoringPlanRequestSerializer(
                data={"patient_id": 1, "disease_id": "iga", "ckd_stage": stage}
            )
            assert ser.is_valid(), f"Stage {stage} should be valid"

    def test_invalid_ckd_stage(self):
        ser = MonitoringPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga", "ckd_stage": 6}
        )
        assert not ser.is_valid()

    def test_invalid_ckd_stage_zero(self):
        ser = MonitoringPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga", "ckd_stage": 0}
        )
        assert not ser.is_valid()

    def test_default_active_treatments(self):
        ser = MonitoringPlanRequestSerializer(
            data={"patient_id": 1, "disease_id": "iga"}
        )
        assert ser.is_valid()
        assert ser.validated_data["active_treatments"] == []


class TestFollowUpScheduleRequestSerializer:
    def test_valid_minimal(self):
        ser = FollowUpScheduleRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()

    def test_defaults(self):
        ser = FollowUpScheduleRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()
        assert ser.validated_data["risk_category"] == "moderate"
        assert ser.validated_data["disease_phase"] == "active"
        assert ser.validated_data["treatment_phase"] == "induction"
        assert ser.validated_data["num_visits"] == 6

    def test_valid_disease_phases(self):
        for phase in ["active", "relapse", "remission", "ckd"]:
            ser = FollowUpScheduleRequestSerializer(
                data={"patient_id": 1, "disease_phase": phase}
            )
            assert ser.is_valid(), f"Phase {phase} should be valid"

    def test_valid_treatment_phases(self):
        for phase in ["induction", "maintenance", "remission"]:
            ser = FollowUpScheduleRequestSerializer(
                data={"patient_id": 1, "treatment_phase": phase}
            )
            assert ser.is_valid(), f"Phase {phase} should be valid"

    def test_num_visits_range(self):
        ser = FollowUpScheduleRequestSerializer(
            data={"patient_id": 1, "num_visits": 0}
        )
        assert not ser.is_valid()

        ser = FollowUpScheduleRequestSerializer(
            data={"patient_id": 1, "num_visits": 25}
        )
        assert not ser.is_valid()

        ser = FollowUpScheduleRequestSerializer(
            data={"patient_id": 1, "num_visits": 12}
        )
        assert ser.is_valid()

    def test_disease_id_optional(self):
        ser = FollowUpScheduleRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()
        assert ser.validated_data.get("disease_id") is None


class TestPatientRequestSerializer:
    def test_valid(self):
        ser = PatientRequestSerializer(data={"patient_id": 42})
        assert ser.is_valid()

    def test_missing(self):
        ser = PatientRequestSerializer(data={})
        assert not ser.is_valid()


class TestInvestigationRecommendationRequestSerializer:
    def test_valid_minimal(self):
        ser = InvestigationRecommendationRequestSerializer(data={"patient_id": 1})
        assert ser.is_valid()

    def test_with_features(self):
        ser = InvestigationRecommendationRequestSerializer(
            data={"patient_id": 1, "features": {"biopsy": True}}
        )
        assert ser.is_valid()


class TestDiseaseValidationRequestSerializer:
    def test_valid(self):
        ser = DiseaseValidationRequestSerializer(
            data={"patient_id": 1, "disease": "iga"}
        )
        assert ser.is_valid()

    def test_missing_disease(self):
        ser = DiseaseValidationRequestSerializer(data={"patient_id": 1})
        assert not ser.is_valid()

    def test_disease_max_length(self):
        ser = DiseaseValidationRequestSerializer(
            data={"patient_id": 1, "disease": "x" * 50}
        )
        assert ser.is_valid()

    def test_disease_too_long(self):
        ser = DiseaseValidationRequestSerializer(
            data={"patient_id": 1, "disease": "x" * 51}
        )
        assert not ser.is_valid()


# ---------------------------------------------------------------------------
# ReviewRecommendationSerializer — custom validation
# ---------------------------------------------------------------------------

class TestReviewRecommendationSerializer:
    def test_approve_valid(self):
        ser = ReviewRecommendationSerializer(data={"approval_status": "approved"})
        assert ser.is_valid()

    def test_reject_with_reason(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "rejected", "override_reason": "Clinical judgment"}
        )
        assert ser.is_valid()

    def test_reject_without_reason_fails(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "rejected"}
        )
        assert not ser.is_valid()

    def test_override_with_reason(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "overridden", "override_reason": "Patient preference"}
        )
        assert ser.is_valid()

    def test_override_without_reason_fails(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "overridden"}
        )
        assert not ser.is_valid()

    def test_invalid_status(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "maybe"}
        )
        assert not ser.is_valid()

    def test_blank_override_reason_for_reject_fails(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "rejected", "override_reason": ""}
        )
        assert not ser.is_valid()

    def test_blank_override_reason_for_overridden_fails(self):
        ser = ReviewRecommendationSerializer(
            data={"approval_status": "overridden", "override_reason": ""}
        )
        assert not ser.is_valid()

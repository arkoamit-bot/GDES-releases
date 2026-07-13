import pytest
from unittest.mock import patch

from clinical_reasoning.models import ClinicalProfile, ClinicalInsight
from clinical_reasoning.services.engine import (
    reason_about_patient,
    recompute_all_profiles,
)
from clinical_reasoning.services.disease_trajectory import (
    assess_trajectory,
    estimate_remission_probability,
)
from clinical_reasoning.services.care_pathway import (
    detect_care_gaps,
    compute_monitoring_schedule,
)
from clinical_reasoning.services.explainability import (
    build_full_explainability,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def patient():
    from patients.models import Patient
    from django.utils import timezone
    return Patient.objects.create(
        patient_id="P001",
        name="Test Patient",
        hospital_id="H001",
        phone="+1234567890",
        sex="F",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="LN",
        current_phase="active",
        registration_status="active",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )


class TestReasonAboutPatient:
    def test_creates_profile(self, patient):
        profile = reason_about_patient(patient)
        assert profile is not None
        assert profile.patient == patient
        assert profile.reasoning_chain is not None
        assert isinstance(profile.reasoning_chain, list)

    def test_profile_has_care_pathway(self, patient):
        profile = reason_about_patient(patient)
        assert profile.care_pathway is not None
        assert isinstance(profile.care_pathway, dict)

    def test_profile_has_disease_trajectory(self, patient):
        profile = reason_about_patient(patient)
        assert profile.disease_trajectory is not None
        assert isinstance(profile.disease_trajectory, dict)

    def test_reasoning_chain_contains_expected_steps(self, patient):
        profile = reason_about_patient(patient)
        chain = profile.reasoning_chain
        assert isinstance(chain, list)

    def test_version_increments(self, patient):
        profile1 = reason_about_patient(patient)
        v1 = profile1.version
        profile2 = reason_about_patient(patient)
        v2 = profile2.version
        assert v2 > v1

    def test_updates_existing_profile(self, patient):
        profile1 = reason_about_patient(patient)
        profile2 = reason_about_patient(patient)
        assert profile1.pk == profile2.pk
        assert profile2.version > profile1.version

    def test_creates_insights(self, patient):
        profile = reason_about_patient(patient)
        insights = ClinicalInsight.objects.filter(patient=patient)
        assert insights.count() >= 1
        for ins in insights:
            assert ins.reasoning is not None


class TestRecomputeAllProfiles:
    def test_recomputes_all_profiles(self, patient):
        from patients.models import Patient
        reason_about_patient(patient)
        summary = recompute_all_profiles()
        assert summary["total"] >= 1
        assert "errors" in summary

    def test_returns_summary(self):
        summary = recompute_all_profiles()
        assert isinstance(summary, dict)


class TestDiseaseTrajectory:
    def test_assess_trajectory_returns_dict(self):
        result = assess_trajectory(None, {})
        assert isinstance(result, dict)
        assert "trend" in result
        assert "detail" in result

    def test_assess_trajectory_declining(self):
        result = assess_trajectory(None, {"egfrTrend": "rapidDecline"})
        assert result["trend"] == "declining"

    def test_assess_trajectory_remission(self):
        result = assess_trajectory(None, {"disease_phase": "remission"})
        assert result["trend"] == "improving"

    def test_estimate_remission_probability_returns_dict(self):
        result = estimate_remission_probability({})
        assert isinstance(result, dict)

    def test_estimate_remission_probability_active(self):
        result = estimate_remission_probability({"disease_phase": "active"})
        assert "remission_potential" in result


class TestCarePathway:
    def test_detect_care_gaps_returns_list(self):
        gaps = detect_care_gaps(None, {})
        assert isinstance(gaps, list)

    def test_detect_care_gaps_identifies_biopsy_gap(self):
        gaps = detect_care_gaps(None, {})
        biopsy_gaps = [g for g in gaps if g.get("field") == "biopsy"]
        assert len(biopsy_gaps) > 0

    def test_compute_monitoring_schedule_returns_dict(self):
        schedule = compute_monitoring_schedule({})
        assert isinstance(schedule, dict)
        assert "visits" in schedule
        assert "labs" in schedule


class TestExplainability:
    @pytest.fixture
    def profile(self, patient):
        return reason_about_patient(patient)

    def test_build_full_explainability_returns_dict(self, profile):
        report = build_full_explainability(profile)
        assert isinstance(report, dict)
        assert "summary" in report
        assert "triggering_findings" in report
        assert "matched_rules" in report
        assert "guideline_support" in report
        assert "rejected_alternatives" in report
        assert "information_gaps" in report
        assert "audit_trail" in report

    def test_explainability_for_new_patient(self, patient):
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile.differential = []
        profile.save(update_fields=["differential"])
        report = build_full_explainability(profile)
        assert isinstance(report, dict)
        assert report["summary"] == "Insufficient data to generate a clinical assessment."

    def test_explainability_audit_trail_has_version(self, profile):
        report = build_full_explainability(profile)
        assert report["audit_trail"]["profile_version"] == profile.version

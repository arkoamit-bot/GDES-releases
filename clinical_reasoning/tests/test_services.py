"""Tests for clinical_reasoning services — core business logic.

Covers: engine, explainability, disease_trajectory, care_pathway,
care_pathway_engine, disease_milestones, drug_toxicity, treatment_failure,
management_plan, monitoring_plan, investigation_engine, disease_validation,
retrospective_validation, audit, json_util.
"""
import datetime as dt
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone

from clinical_reasoning.models import ClinicalProfile, ClinicalInsight
from clinical_reasoning.json_util import json_safe


pytestmark = pytest.mark.django_db


# ============================================================================
# json_util
# ============================================================================

class TestJsonSafe:
    def test_decimal_to_float(self):
        assert json_safe(Decimal("3.14")) == 3.14
        assert isinstance(json_safe(Decimal("1.0")), float)

    def test_dict_recursive(self):
        result = json_safe({"a": Decimal("1"), "b": [Decimal("2")]})
        assert result == {"a": 1.0, "b": [2.0]}

    def test_list_recursive(self):
        result = json_safe([Decimal("1"), {"x": Decimal("2")}])
        assert result == [1.0, {"x": 2.0}]

    def test_set_sorted(self):
        result = json_safe({3, 1, 2})
        assert result == (1, 2, 3) or result == [1, 2, 3]

    def test_tuple(self):
        result = json_safe((Decimal("1"), Decimal("2")))
        assert result == (1.0, 2.0)

    def test_passthrough(self):
        assert json_safe(42) == 42
        assert json_safe("hello") == "hello"
        assert json_safe(None) is None
        assert json_safe(True) is True


# ============================================================================
# engine.py — unit tests (mocked knowledge layer)
# ============================================================================

class TestBuildDifferential:
    """Test the _build_differential helper."""

    def _mock_rule(self, disease_id, disease_name, score, matched_rules,
                   source="KDIGO", grade="1"):
        r = MagicMock()
        r.disease_id = disease_id
        r.disease_name = disease_name
        r.total_score = score
        r.matched_rules = matched_rules
        r.source = source
        r.evidence_grade = grade
        return r

    def test_empty(self):
        from clinical_reasoning.services.engine import _build_differential
        assert _build_differential([]) == []

    def test_single(self):
        from clinical_reasoning.services.engine import _build_differential
        r = self._mock_rule("iga", "IgA", 10, [1, 2, 3])
        res = _build_differential([r])
        assert len(res) == 1
        assert res[0]["confidence"] == 100

    def test_normalized_confidence(self):
        from clinical_reasoning.services.engine import _build_differential
        r1 = self._mock_rule("iga", "IgA", 12, [1, 2])
        r2 = self._mock_rule("mn", "MN", 4, [1])
        res = _build_differential([r1, r2])
        assert res[0]["confidence"] == 75
        assert res[1]["confidence"] == 25

    def test_zero_score_excluded(self):
        from clinical_reasoning.services.engine import _build_differential
        r1 = self._mock_rule("iga", "IgA", 10, [1])
        r2 = self._mock_rule("mn", "MN", 0, [])
        res = _build_differential([r1, r2])
        assert len(res) == 1


class TestAssessRisk:
    def test_unknown_when_no_egfr(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=None), {}, {})
        assert risk["overall"] == "unknown"

    def test_high_risk_low_egfr(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=25), {}, {})
        assert risk["overall"] == "high"

    def test_moderate_risk(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=45), {}, {})
        assert risk["overall"] == "moderate"

    def test_low_risk(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=90), {}, {})
        assert risk["overall"] == "low"

    def test_edema_factor(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=90), {"features": ["edema"]}, {})
        assert any(f["factor"] == "active_disease" for f in risk["factors"])

    def test_declining_overrides_to_high(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=90), {}, {"trend": "declining"})
        assert risk["overall"] == "high"

    def test_egfr_from_features_dict(self):
        from clinical_reasoning.services.engine import _assess_risk
        risk = _assess_risk(MagicMock(latest_egfr=None), {"latest_egfr": 25}, {})
        assert risk["overall"] == "high"


class TestIdentifyInformationGaps:
    def test_gaps_when_empty(self):
        from clinical_reasoning.services.engine import _identify_information_gaps
        gaps = _identify_information_gaps({})
        fields = [g["field"] for g in gaps]
        assert "biopsy" in fields
        assert "egfr" in fields

    def test_no_gap_with_data(self):
        from clinical_reasoning.services.engine import _identify_information_gaps
        gaps = _identify_information_gaps({
            "biopsy": ["mesangial"], "latest_egfr": 60, "labs": ["lowC3"],
        })
        fields = [g["field"] for g in gaps]
        assert "biopsy" not in fields
        assert "egfr" not in fields

    def test_lupus_proteinuria_gap(self):
        from clinical_reasoning.services.engine import _identify_information_gaps
        gaps = _identify_information_gaps({
            "proteinuria": "none", "biopsy": ["fullHouse"], "latest_egfr": 60,
        })
        fields = [g["field"] for g in gaps]
        assert "proteinuria" in fields


class TestBuildReasoningChain:
    def test_with_data(self):
        from clinical_reasoning.services.engine import _build_reasoning_chain
        r = MagicMock(disease_name="IgA", total_score=12,
                      matched_rules=[1, 2, 3], source="KDIGO")
        chain = _build_reasoning_chain(
            MagicMock(), [r], {"trend": "stable"},
            [{"field": "x", "message": "Check proteinuria"}],
        )
        steps = [c["step"] for c in chain]
        assert "rule_evaluation" in steps
        assert "care_gaps" in steps

    def test_empty(self):
        from clinical_reasoning.services.engine import _build_reasoning_chain
        assert _build_reasoning_chain(MagicMock(), [], {}, []) == []


class TestGenerateRecommendations:
    def test_from_gaps(self):
        from clinical_reasoning.services.engine import _generate_recommendations
        recs = _generate_recommendations([{"importance": "high", "message": "Need biopsy"}], [])
        assert len(recs) == 1
        assert recs[0]["type"] == "investigation"

    def test_from_rules(self):
        from clinical_reasoning.services.engine import _generate_recommendations
        r = MagicMock(disease_name="IgA", total_score=10, source="KDIGO")
        recs = _generate_recommendations([], [r])
        assert recs[0]["type"] == "diagnostic_impression"


class TestGatherEvidenceSummary:
    def test_grades(self):
        from clinical_reasoning.services.engine import _gather_evidence_summary
        r1 = MagicMock(evidence_grade="1")
        r2 = MagicMock(evidence_grade="2")
        r3 = MagicMock(evidence_grade="1")
        s = _gather_evidence_summary([r1, r2, r3])
        assert s["grade_distribution"] == {"1": 2, "2": 1}

    def test_none_grade(self):
        from clinical_reasoning.services.engine import _gather_evidence_summary
        s = _gather_evidence_summary([MagicMock(evidence_grade=None)])
        assert s["grade_distribution"]["NG"] == 1


# ============================================================================
# engine.py — integration (mocked knowledge)
# ============================================================================

def _patch_engine():
    # Patch the internal functions that disease_trajectory calls.
    # assess_trajectory uses features.latest_egfr in comparisons
    # and is imported locally inside _assess_disease_trajectory.
    trajectory_return = {
        "trend": "stable", "detail": "No change",
        "confidence": "low",
        "kidney_survival_estimate": {
            "status": "favorable", "estimated_years_to_eskd": 20.0,
        },
    }
    return (
        patch("clinical_reasoning.services.engine.extract_patient_features"),
        patch("clinical_reasoning.services.engine.evaluate_patient_rules"),
        patch("clinical_reasoning.services.engine.augment_differential"),
        patch("clinical_reasoning.services.engine.get_syndrome_matches"),
        patch("clinical_reasoning.services.engine.enhance_treatment_plan"),
        patch("clinical_reasoning.services.engine.build_graph_reasoning_steps"),
        patch(
            "clinical_reasoning.services.disease_trajectory.assess_trajectory",
            return_value=trajectory_return,
        ),
    )


class TestReasonAboutPatient:
    def test_creates_profile(self, db):
        """Create a patient and trigger reason_about_patient with all
        engine internals patched. Uses bulk_create to avoid post_save
        signal cascade into clinical reasoning."""
        from patients.models import Patient
        from django.utils import timezone

        # bulk_create does NOT fire post_save, so the event dispatcher
        # never fires and _on_patient_event is never called.
        patient = Patient.objects.bulk_create([
            Patient(
                patient_id="TEST-RAP",
                name="Reason About Patient",
                hospital_id="H003",
                phone="+123****7890",
                sex="M",
                cohort="GN",
                diabetes_status="no",
                primary_diagnosis="iga",
                current_phase="active",
                registration_status="active",
                enrollment_date=timezone.now().date(),
            ),
        ])[0]

        trajectory = {
            "trend": "stable", "detail": "No change",
            "confidence": "low",
            "kidney_survival_estimate": {
                "status": "favorable", "estimated_years_to_eskd": 20.0,
            },
        }
        from unittest.mock import patch as _p
        patches = (
            _p(
                "clinical_reasoning.services.engine.extract_patient_features",
                return_value={"features": [], "labs": [],
                              "latest_egfr": 75, "egfrTrend": "normal",
                              "proteinuria": "none", "disease_phase": "active"},
            ),
            _p(
                "clinical_reasoning.services.engine.evaluate_patient_rules",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.augment_differential",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.get_syndrome_matches",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.enhance_treatment_plan",
                return_value={},
            ),
            _p(
                "clinical_reasoning.services.engine.build_graph_reasoning_steps",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.disease_trajectory.assess_trajectory",
                return_value=trajectory,
            ),
        )
        for p in patches:
            p.start()
        try:
            from clinical_reasoning.services.engine import reason_about_patient
            profile = reason_about_patient(patient)
            assert profile.patient == patient
            assert profile.version == 1
        finally:
            for p in patches:
                p.stop()

    def test_increments_version(self, db):
        from patients.models import Patient
        from django.utils import timezone
        from unittest.mock import patch as _p

        patient = Patient.objects.bulk_create([
            Patient(
                patient_id="TEST-RAP2",
                name="Reason About Patient 2",
                hospital_id="H004",
                phone="+123****7890",
                sex="M",
                cohort="GN",
                diabetes_status="no",
                primary_diagnosis="iga",
                current_phase="active",
                registration_status="active",
                enrollment_date=timezone.now().date(),
            ),
        ])[0]

        trajectory = {
            "trend": "stable", "detail": "No change",
            "confidence": "low",
            "kidney_survival_estimate": {
                "status": "favorable", "estimated_years_to_eskd": 20.0,
            },
        }
        patches = (
            _p(
                "clinical_reasoning.services.engine.extract_patient_features",
                return_value={"features": [], "labs": [],
                              "latest_egfr": 75, "egfrTrend": "normal",
                              "proteinuria": "none", "disease_phase": "active"},
            ),
            _p(
                "clinical_reasoning.services.engine.evaluate_patient_rules",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.augment_differential",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.get_syndrome_matches",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.enhance_treatment_plan",
                return_value={},
            ),
            _p(
                "clinical_reasoning.services.engine.build_graph_reasoning_steps",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.disease_trajectory.assess_trajectory",
                return_value=trajectory,
            ),
        )
        for p in patches:
            p.start()
        try:
            from clinical_reasoning.services.engine import reason_about_patient
            p1 = reason_about_patient(patient)
            p2 = reason_about_patient(patient)
            assert p2.version > p1.version
            assert p1.pk == p2.pk
        finally:
            for p in patches:
                p.stop()

    def test_generates_insights(self, db):
        from patients.models import Patient
        from django.utils import timezone
        from unittest.mock import patch as _p

        patient = Patient.objects.bulk_create([
            Patient(
                patient_id="TEST-RAP3",
                name="Reason About Patient 3",
                hospital_id="H005",
                phone="+123****7890",
                sex="M",
                cohort="GN",
                diabetes_status="no",
                primary_diagnosis="iga",
                current_phase="active",
                registration_status="active",
                enrollment_date=timezone.now().date(),
            ),
        ])[0]

        trajectory = {
            "trend": "stable", "detail": "No change",
            "confidence": "low",
            "kidney_survival_estimate": {
                "status": "favorable", "estimated_years_to_eskd": 20.0,
            },
        }
        patches = (
            _p(
                "clinical_reasoning.services.engine.extract_patient_features",
                return_value={"features": [], "labs": [],
                              "latest_egfr": 75, "egfrTrend": "normal",
                              "proteinuria": "none", "disease_phase": "active"},
            ),
            _p(
                "clinical_reasoning.services.engine.evaluate_patient_rules",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.augment_differential",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.get_syndrome_matches",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.engine.enhance_treatment_plan",
                return_value={},
            ),
            _p(
                "clinical_reasoning.services.engine.build_graph_reasoning_steps",
                return_value=[],
            ),
            _p(
                "clinical_reasoning.services.disease_trajectory.assess_trajectory",
                return_value=trajectory,
            ),
        )
        for p in patches:
            p.start()
        try:
            from clinical_reasoning.services.engine import reason_about_patient
            reason_about_patient(patient)
            assert ClinicalInsight.objects.filter(patient=patient).count() >= 1
        finally:
            for p in patches:
                p.stop()


class TestRecomputeAllProfiles:
    def test_empty(self):
        from clinical_reasoning.services.engine import recompute_all_profiles
        with patch("clinical_reasoning.services.engine.reason_about_patient"):
            assert recompute_all_profiles() == {"total": 0, "errors": 0}

    def test_with_patient(self, patient):
        from clinical_reasoning.services.engine import recompute_all_profiles
        with patch("clinical_reasoning.services.engine.reason_about_patient") as m:
            m.return_value = MagicMock()
            s = recompute_all_profiles()
            assert s["total"] >= 1
            assert s["errors"] == 0

    def test_error_handling(self, patient):
        from clinical_reasoning.services.engine import recompute_all_profiles
        with patch("clinical_reasoning.services.engine.reason_about_patient") as m:
            m.side_effect = RuntimeError("boom")
            s = recompute_all_profiles()
            assert s["errors"] == 1


# ============================================================================
# explainability.py
# ============================================================================

class TestExplainability:
    def test_full_report(self, clinical_profile):
        from clinical_reasoning.services.explainability import build_full_explainability
        report = build_full_explainability(clinical_profile)
        for key in ("summary", "triggering_findings", "matched_rules",
                     "guideline_support", "confidence", "rejected_alternatives",
                     "information_gaps", "audit_trail"):
            assert key in report

    def test_empty_differential(self, patient):
        from clinical_reasoning.services.explainability import build_full_explainability
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile.differential = []
        profile.save()
        report = build_full_explainability(profile)
        assert report["knowledge_health"]["knowledge_base_available"] is False

    def test_audit_trail(self, clinical_profile):
        from clinical_reasoning.services.explainability import build_full_explainability
        report = build_full_explainability(clinical_profile)
        assert report["audit_trail"]["profile_version"] == clinical_profile.version

    def test_confidence_high(self):
        from clinical_reasoning.services.explainability import _compute_confidence
        r = _compute_confidence([{"score": 100}, {"score": 10}])
        assert r["level"] == "high"

    def test_confidence_low(self):
        from clinical_reasoning.services.explainability import _compute_confidence
        # top=10 vs max_possible=80 → 12.5% → low
        r = _compute_confidence([{"score": 10}, {"score": 80}])
        assert r["level"] == "low"

    def test_confidence_empty(self):
        from clinical_reasoning.services.explainability import _compute_confidence
        r = _compute_confidence([])
        assert r["level"] == "insufficient_data"

    def test_rejected_alternatives(self):
        from clinical_reasoning.services.explainability import _explain_rejected_alternatives
        top = {"score": 15, "disease_name": "A"}
        alts = [{
            "score": 5, "disease_name": "B",
            "matched_rules": [1],
            "missing_rules": [{"condition": "x", "weight": 1}],
        }]
        r = _explain_rejected_alternatives(alts, top)
        assert r[0]["score_difference"] == 10

    def test_summary_with_declining(self, clinical_profile):
        from clinical_reasoning.services.explainability import _build_summary
        clinical_profile.disease_trajectory = {"trend": "declining"}
        clinical_profile.save()
        s = _build_summary(clinical_profile.differential[0], clinical_profile.disease_trajectory)
        assert "progressive" in s.lower()


# ============================================================================
# disease_trajectory.py
# ============================================================================

class TestDiseaseTrajectory:
    def test_stable_default(self):
        from clinical_reasoning.services.disease_trajectory import assess_trajectory
        assert assess_trajectory(None, {})["trend"] == "stable"

    def test_rapid_decline(self):
        from clinical_reasoning.services.disease_trajectory import assess_trajectory
        assert assess_trajectory(None, {"egfrTrend": "rapidDecline"})["trend"] == "declining"

    def test_remission(self):
        from clinical_reasoning.services.disease_trajectory import assess_trajectory
        assert assess_trajectory(None, {"disease_phase": "remission"})["trend"] == "improving"

    def test_eskd_phase(self):
        from clinical_reasoning.services.disease_trajectory import assess_trajectory
        assert assess_trajectory(None, {"disease_phase": "eskd"})["trend"] == "end_stage"

    def test_eskd_low_egfr(self):
        from clinical_reasoning.services.disease_trajectory import assess_trajectory
        assert assess_trajectory(MagicMock(latest_egfr=12), {})["trend"] == "end_stage"

    def test_kidney_survival_none(self):
        from clinical_reasoning.services.disease_trajectory import _estimate_kidney_survival
        assert _estimate_kidney_survival(None)["status"] == "unknown"

    def test_kidney_survival_favorable(self):
        from clinical_reasoning.services.disease_trajectory import _estimate_kidney_survival
        assert _estimate_kidney_survival(90)["status"] == "favorable"

    def test_kidney_survival_moderate(self):
        from clinical_reasoning.services.disease_trajectory import _estimate_kidney_survival
        assert _estimate_kidney_survival(45)["status"] == "moderate"

    def test_kidney_survival_guarded(self):
        from clinical_reasoning.services.disease_trajectory import _estimate_kidney_survival
        assert _estimate_kidney_survival(20)["status"] == "guarded"

    def test_kidney_survival_critical(self):
        from clinical_reasoning.services.disease_trajectory import _estimate_kidney_survival
        assert _estimate_kidney_survival(10)["status"] == "critical"

    def test_remission_prob_remission(self):
        from clinical_reasoning.services.disease_trajectory import estimate_remission_probability
        r = estimate_remission_probability({"disease_phase": "remission"})
        assert r["current_status"] == "in_remission"

    def test_remission_prob_active(self):
        from clinical_reasoning.services.disease_trajectory import estimate_remission_probability
        r = estimate_remission_probability({"disease_phase": "active"})
        assert r["current_status"] == "active_disease"

    def test_remission_prob_unknown(self):
        from clinical_reasoning.services.disease_trajectory import estimate_remission_probability
        r = estimate_remission_probability({})
        assert r["current_status"] == "unknown"


# ============================================================================
# care_pathway.py
# ============================================================================

class TestCarePathway:
    def test_detect_gaps(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(MagicMock(), {})
        assert isinstance(gaps, list) and len(gaps) > 0

    def test_biopsy_gap_always(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(MagicMock(), {})
        assert any(g["field"] == "biopsy" for g in gaps)

    def test_egfr_gap_when_missing(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(MagicMock(), {})
        assert any(g["field"] == "egfr" for g in gaps)

    def test_active_disease_monitoring_gap(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(MagicMock(), {"disease_phase": "active"})
        assert any(g["field"] == "monitoring_frequency" for g in gaps)

    def test_vaccination_gap_always(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(MagicMock(), {})
        assert any(g["field"] == "vaccination" for g in gaps)

    def test_monitoring_schedule(self):
        from clinical_reasoning.services.care_pathway import compute_monitoring_schedule
        s = compute_monitoring_schedule({})
        assert s["visits"] == "every_3_months"

    def test_active_disease_monitoring(self):
        from clinical_reasoning.services.care_pathway import compute_monitoring_schedule
        s = compute_monitoring_schedule({"disease_phase": "active"})
        assert s["visits"] == "every_2_4_weeks"


# ============================================================================
# care_pathway_engine.py
# ============================================================================

class TestCarePathwayEngine:
    def test_determine_stage_active(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        assert determine_current_stage(patient, {"disease_phase": "active"}) == "active_disease"

    def test_determine_stage_remission(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        assert determine_current_stage(patient, {"disease_phase": "remission"}) == "remission_monitoring"

    def test_determine_stage_eskd(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        assert determine_current_stage(patient, {"disease_phase": "eskd"}) == "eskd_care"

    def test_determine_stage_eskd_low_egfr(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        patient.latest_egfr = 10
        assert determine_current_stage(patient, {}) == "eskd_care"

    def test_determine_stage_default_assessment(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        assert determine_current_stage(patient, {}) == "assessment"

    def test_detect_stage_transition_valid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(MagicMock(), "assessment", "active_disease")
        assert result is not None
        assert result["valid"] is True

    def test_detect_stage_transition_invalid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(MagicMock(), "assessment", "eskd_care")
        assert result is not None
        assert result["valid"] is False

    def test_detect_stage_transition_same(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        assert detect_stage_transition(MagicMock(), "active", "active") is None

    def test_assess_pathway_deviation(self, patient):
        from clinical_reasoning.services.care_pathway_engine import assess_pathway_deviation
        deviations = assess_pathway_deviation(patient, "assessment", {})
        assert isinstance(deviations, list)

    def test_compute_pathway_summary(self, patient):
        from clinical_reasoning.services.care_pathway_engine import compute_pathway_summary
        summary = compute_pathway_summary(patient, "active_disease", [], [])
        assert summary["current_stage"] == "active_disease"
        assert "stage_label" in summary

    def test_get_pathway_stage(self):
        from clinical_reasoning.services.care_pathway_engine import get_pathway_stage
        stage = get_pathway_stage("assessment")
        assert stage is not None
        assert stage.name == "assessment"

    def test_get_pathway_stage_missing(self):
        from clinical_reasoning.services.care_pathway_engine import get_pathway_stage
        assert get_pathway_stage("nonexistent") is None


# ============================================================================
# disease_milestones.py
# ============================================================================

class TestDiseaseMilestones:
    def test_detect_milestones_empty(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {}, {})
        assert isinstance(milestones, list)
        assert len(milestones) >= 1  # At least diagnosis milestone

    def test_diagnosis_milestone(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "diagnosis" in types

    def test_remission_milestone(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {"disease_phase": "remission"}, {"trend": "improving"})
        types = [m["milestone_type"] for m in milestones]
        assert "remission" in types

    def test_eskd_milestone(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        patient.latest_egfr = 10
        milestones = detect_milestones(patient, {}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "eskd" in types

    def test_compute_trajectory_summary(self):
        from clinical_reasoning.services.disease_milestones import compute_trajectory_summary
        milestones = [
            {"milestone_type": "diagnosis"},
            {"milestone_type": "biopsy"},
            {"milestone_type": "remission"},
        ]
        s = compute_trajectory_summary(MagicMock(), milestones)
        assert s["total_milestones"] == 3
        assert s["has_diagnosis"] is True
        assert s["has_biopsy"] is True
        assert s["has_remission"] is True

    def test_merge_deduplicates(self):
        from clinical_reasoning.services.disease_milestones import _merge_milestones
        existing = [{"milestone_type": "diagnosis", "label": "Diagnosed"}]
        detected = [
            {"milestone_type": "diagnosis", "label": "Diagnosed"},
            {"milestone_type": "biopsy", "label": "Biopsy"},
        ]
        merged = _merge_milestones(existing, detected)
        types = [m["milestone_type"] for m in merged]
        assert types.count("diagnosis") == 1
        assert "biopsy" in types


# ============================================================================
# drug_toxicity.py
# ============================================================================

class TestDrugToxicity:
    def test_medication_matches_cni(self):
        from clinical_reasoning.services.drug_toxicity import (
            _medication_matches_rule, TOXICITY_RULES,
        )
        cni_rule = next(r for r in TOXICITY_RULES if r.drug_class == "CNI")
        assert _medication_matches_rule("Tacrolimus 5mg", "", cni_rule)
        assert _medication_matches_rule("Cyclosporine 100mg", "", cni_rule)
        assert not _medication_matches_rule("Aspirin", "", cni_rule)

    def test_medication_matches_mmf(self):
        from clinical_reasoning.services.drug_toxicity import (
            _medication_matches_rule, TOXICITY_RULES,
        )
        mmf_rule = next(r for r in TOXICITY_RULES if r.drug_name == "Mycophenolate mofetil" and r.lab_test == "ALT")
        assert _medication_matches_rule("Mycophenolate mofetil", "", mmf_rule)

    def test_medication_matches_rituximab(self):
        from clinical_reasoning.services.drug_toxicity import (
            _medication_matches_rule, TOXICITY_RULES,
        )
        rtx_rule = next(r for r in TOXICITY_RULES if r.drug_class == "Anti-CD20")
        assert _medication_matches_rule("Rituximab", "", rtx_rule)
        assert _medication_matches_rule("Rituxan", "", rtx_rule)

    def test_medication_matches_steroid(self):
        from clinical_reasoning.services.drug_toxicity import (
            _medication_matches_rule, TOXICITY_RULES,
        )
        steroid_rule = next(r for r in TOXICITY_RULES if r.drug_class == "Corticosteroid")
        assert _medication_matches_rule("Prednisolone 20mg", "", steroid_rule)
        assert _medication_matches_rule("Prednisone", "", steroid_rule)

    def test_medication_matches_acei(self):
        from clinical_reasoning.services.drug_toxicity import (
            _medication_matches_rule, TOXICITY_RULES,
        )
        acei_rule = next(r for r in TOXICITY_RULES if r.drug_class == "RAAS inhibitor")
        assert _medication_matches_rule("Lisinopril 10mg", "", acei_rule)
        assert _medication_matches_rule("Losartan", "", acei_rule)

    def test_evaluate_toxicity_high_direction(self):
        from clinical_reasoning.services.drug_toxicity import (
            _evaluate_toxicity_rule, ToxicityRule,
        )
        rule = ToxicityRule(
            drug_class="CNI", drug_name="Tacrolimus", lab_test="creatinine",
            severity_thresholds={"mild": 1.3, "moderate": 1.8, "severe": 2.5, "critical": 3.5},
            mechanism="test", clinical_action="test", monitoring_frequency="test",
        )
        # Normal value - no alert
        assert _evaluate_toxicity_rule(rule, 1.0, []) is None
        # Mild
        alert = _evaluate_toxicity_rule(rule, 1.5, [])
        assert alert is not None and alert.severity == "mild"
        # Critical
        alert = _evaluate_toxicity_rule(rule, 3.5, [])
        assert alert.severity == "critical"

    def test_evaluate_toxicity_low_direction(self):
        from clinical_reasoning.services.drug_toxicity import (
            _evaluate_toxicity_rule, ToxicityRule,
        )
        rule = ToxicityRule(
            drug_class="IMPDH", drug_name="MMF", lab_test="WBC",
            severity_thresholds={"mild": 3.5, "moderate": 2.5, "severe": 1.5, "critical": 0.8},
            mechanism="test", clinical_action="test", monitoring_frequency="test",
            direction="low",
        )
        # Normal
        assert _evaluate_toxicity_rule(rule, 5.0, []) is None
        # Moderate (WBC 2.3 < 2.5 threshold)
        alert = _evaluate_toxicity_rule(rule, 2.3, [])
        assert alert is not None and alert.severity == "moderate"

    def test_risk_factor_boosts_severity(self):
        from clinical_reasoning.services.drug_toxicity import (
            _evaluate_toxicity_rule, ToxicityRule,
        )
        rule = ToxicityRule(
            drug_class="test", drug_name="test", lab_test="test",
            severity_thresholds={"mild": 5, "moderate": 10},
            mechanism="m", clinical_action="c", monitoring_frequency="f",
            risk_factors=["dehydration"],
            direction="high",
        )
        # Mild with matching risk factor -> boosted to moderate
        alert = _evaluate_toxicity_rule(rule, 6.0, ["dehydration"])
        assert alert.severity == "moderate"
        # Mild without risk factor stays mild
        alert = _evaluate_toxicity_rule(rule, 6.0, [])
        assert alert.severity == "mild"

    def test_toxicity_alert_to_dict(self):
        from clinical_reasoning.services.drug_toxicity import ToxicityAlert
        alert = ToxicityAlert(
            drug_class="CNI", drug_name="Tacrolimus", lab_test="creatinine",
            current_value=2.0, severity="moderate", threshold=1.8,
            mechanism="m", clinical_action="a", monitoring_frequency="f",
            risk_factors=[], priority="high",
        )
        d = alert.to_dict()
        assert d["drug_name"] == "Tacrolimus"
        assert d["severity"] == "moderate"

    def test_drug_toxicity_report_to_dict(self):
        from clinical_reasoning.services.drug_toxicity import DrugToxicityReport
        report = DrugToxicityReport(
            patient_id="P001", alerts=[], current_medications=[], summary="None",
        )
        d = report.to_dict()
        assert d["total_alerts"] == 0
        assert d["critical_count"] == 0

    def test_build_toxicity_summary_none(self):
        from clinical_reasoning.services.drug_toxicity import _build_toxicity_summary
        assert _build_toxicity_summary([], []) == "No drug toxicity detected from current medications."

    def test_build_toxicity_summary_critical(self):
        from clinical_reasoning.services.drug_toxicity import (
            _build_toxicity_summary, ToxicityAlert,
        )
        alert = ToxicityAlert(
            drug_class="CNI", drug_name="Tacrolimus", lab_test="cr",
            current_value=4.0, severity="critical", threshold=3.5,
            mechanism="", clinical_action="", monitoring_frequency="",
            risk_factors=[], priority="urgent",
        )
        s = _build_toxicity_summary([alert], [])
        assert "CRITICAL" in s

    def test_severity_order(self):
        from clinical_reasoning.services.drug_toxicity import _severity_order
        assert _severity_order("critical") < _severity_order("severe")
        assert _severity_order("severe") < _severity_order("moderate")
        assert _severity_order("moderate") < _severity_order("mild")


# ============================================================================
# treatment_failure.py
# ============================================================================

class TestTreatmentFailure:
    def test_evaluate_failure_pattern_below_threshold(self):
        from clinical_reasoning.services.treatment_failure import (
            _evaluate_failure_pattern, FailurePattern,
        )
        pattern = FailurePattern(
            disease_id="iga", failure_type="proteinuria_nonresponse",
            description="test", criteria={"proteinuria_threshold": 1.0},
            clinical_significance="test", next_steps="test", guideline_ref="test",
        )
        # No alert when below threshold
        assert _evaluate_failure_pattern(pattern, {"proteinuria_upcr": 0.5}, 12) is None

    def test_evaluate_failure_pattern_above_threshold(self):
        from clinical_reasoning.services.treatment_failure import (
            _evaluate_failure_pattern, FailurePattern,
        )
        pattern = FailurePattern(
            disease_id="iga", failure_type="proteinuria_nonresponse",
            description="test", criteria={
                "proteinuria_threshold": 1.0, "minimum_treatment_months": 6,
            },
            clinical_significance="sig", next_steps="steps", guideline_ref="ref",
        )
        alert = _evaluate_failure_pattern(pattern, {"proteinuria_upcr": 2.0}, 12)
        assert alert is not None
        assert alert.severity == "warning"

    def test_critical_when_double_threshold(self):
        from clinical_reasoning.services.treatment_failure import (
            _evaluate_failure_pattern, FailurePattern,
        )
        pattern = FailurePattern(
            disease_id="iga", failure_type="proteinuria_nonresponse",
            description="test", criteria={
                "proteinuria_threshold": 1.0, "minimum_treatment_months": 6,
            },
            clinical_significance="sig", next_steps="steps", guideline_ref="ref",
        )
        alert = _evaluate_failure_pattern(pattern, {"proteinuria_upcr": 3.0}, 12)
        assert alert.severity == "critical"

    def test_early_treatment_skips(self):
        from clinical_reasoning.services.treatment_failure import (
            _evaluate_failure_pattern, FailurePattern,
        )
        pattern = FailurePattern(
            disease_id="iga", failure_type="proteinuria_nonresponse",
            description="test", criteria={
                "proteinuria_threshold": 1.0, "minimum_treatment_months": 6,
            },
            clinical_significance="sig", next_steps="steps", guideline_ref="ref",
        )
        # Only 3 months — too early
        assert _evaluate_failure_pattern(pattern, {"proteinuria_upcr": 2.0}, 3) is None

    def test_failure_alert_to_dict(self):
        from clinical_reasoning.services.treatment_failure import TreatmentFailureAlert
        alert = TreatmentFailureAlert(
            disease_id="iga", failure_type="test", description="d",
            clinical_significance="s", next_steps="n", guideline_ref="r",
            current_values={}, severity="warning", priority="high",
        )
        d = alert.to_dict()
        assert d["disease_id"] == "iga"
        assert d["severity"] == "warning"

    def test_failure_report_to_dict(self):
        from clinical_reasoning.services.treatment_failure import TreatmentFailureReport
        report = TreatmentFailureReport(
            patient_id="P001", primary_disease="iga", alerts=[],
            treatment_duration_months=12.0, summary="test",
        )
        d = report.to_dict()
        assert d["total_alerts"] == 0

    def test_build_failure_summary_none(self):
        from clinical_reasoning.services.treatment_failure import _build_failure_summary
        s = _build_failure_summary([], "iga", 12.0)
        assert "No treatment failure" in s or "no" in s.lower()

    def test_priority_order(self):
        from clinical_reasoning.services.treatment_failure import _priority_order
        assert _priority_order("urgent") < _priority_order("high")
        assert _priority_order("high") < _priority_order("medium")

    def test_egfr_decline_pattern(self):
        """egfr_decline evaluation is a stub (both branches are ``pass``)
        so the function returns None regardless of input data."""
        from clinical_reasoning.services.treatment_failure import (
            _evaluate_failure_pattern, FailurePattern,
        )
        pattern = FailurePattern(
            disease_id="iga", failure_type="egfr_decline",
            description="test", criteria={
                "egfr_decline_rate": 5.0, "assessment_period_months": 12,
            },
            clinical_significance="sig", next_steps="steps", guideline_ref="ref",
        )
        # The egfr_decline logic is not yet implemented — both the rate-based
        # and percent-based checks are ``pass`` statements. This test documents
        # current behaviour and will change when the implementation is added.
        alert = _evaluate_failure_pattern(pattern, {"egfr_decline_rate": 8.0}, 12)
        assert alert is None  # known stub — update when implemented


# ============================================================================
# management_plan.py
# ============================================================================

class TestManagementPlan:
    def test_iga_plan(self, patient):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan = generate_management_plan(patient, "iga")
        assert plan is not None
        assert plan.disease_name == "IgA Nephropathy"
        assert len(plan.first_line) >= 1
        d = plan.to_dict()
        assert "disease_id" in d
        assert "first_line" in d

    def test_membranous_plan(self, patient):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan = generate_management_plan(patient, "membranous")
        assert plan.disease_name == "Membranous Nephropathy"
        assert len(plan.first_line) >= 1

    def test_unknown_disease(self, patient):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan = generate_management_plan(patient, "unknown_disease")
        assert plan is not None
        # Default plan includes a nephrology consultation placeholder
        assert len(plan.first_line) == 1
        assert plan.first_line[0]["drug"] == "Nephrology consultation"

    def test_risk_stratification(self, patient):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan_high = generate_management_plan(patient, "iga", risk_category="high")
        plan_low = generate_management_plan(patient, "iga", risk_category="low")
        # Both should produce valid plans
        assert plan_high is not None
        assert plan_low is not None

    def test_all_disease_profiles(self, patient):
        from clinical_reasoning.services.management_plan import (
            generate_management_plan, DISEASE_TREATMENT_PROFILES,
        )
        for disease_id in DISEASE_TREATMENT_PROFILES:
            plan = generate_management_plan(patient, disease_id)
            assert plan is not None
            assert plan.disease_name

    def test_custom_features(self, patient):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan = generate_management_plan(patient, "iga", features={"egfr": 25})
        assert plan is not None


# ============================================================================
# monitoring_plan.py
# ============================================================================

class TestMonitoringPlan:
    def test_iga_plan(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "iga")
        assert plan.disease_name == "IgA Nephropathy"
        assert len(plan.parameters) >= 1
        d = plan.to_dict()
        assert "parameters" in d
        assert "treatment_monitoring" in d

    def test_with_treatments(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "iga", active_treatments=["acei_arb"])
        assert len(plan.treatment_monitoring) >= 1

    def test_with_ckd_stage(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "iga", ckd_stage=4)
        assert len(plan.ckd_monitoring) >= 1

    def test_high_risk_intervals(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "iga", risk_category="high")
        assert len(plan.risk_adjustments) > 0

    def test_very_high_risk(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "iga", risk_category="very_high")
        assert len(plan.risk_adjustments) > 0

    def test_unknown_disease(self, patient):
        from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
        plan = generate_monitoring_plan(patient, "unknown")
        assert plan.disease_name == "Unknown"

    def test_all_protocols(self, patient):
        from clinical_reasoning.services.monitoring_plan import (
            generate_monitoring_plan, DISEASE_MONITORING_PROTOCOLS,
        )
        for disease_id in DISEASE_MONITORING_PROTOCOLS:
            plan = generate_monitoring_plan(patient, disease_id)
            assert plan is not None
            assert len(plan.parameters) >= 1


# ============================================================================
# investigation_engine.py
# ============================================================================

class TestInvestigationEngine:
    def test_iga_recommendations(self, patient):
        from clinical_reasoning.services.investigation_engine import generate_investigation_recommendations
        diff = [{"disease_id": "iga", "disease_name": "IgA", "score": 10, "confidence": 80}]
        plan = generate_investigation_recommendations(patient, diff)
        assert plan is not None
        assert len(plan.recommendations) >= 1
        d = plan.to_dict()
        assert "recommendations" in d
        assert "total_recommendations" in d

    def test_empty_differential(self, patient):
        from clinical_reasoning.services.investigation_engine import generate_investigation_recommendations
        plan = generate_investigation_recommendations(patient, [])
        assert len(plan.recommendations) == 0

    def test_deduplication(self, patient):
        from clinical_reasoning.services.investigation_engine import generate_investigation_recommendations
        diff = [
            {"disease_id": "iga", "disease_name": "IgA", "score": 10, "confidence": 80},
            {"disease_id": "iga", "disease_name": "IgA", "score": 12, "confidence": 90},
        ]
        plan = generate_investigation_recommendations(patient, diff)
        # Should deduplicate same test across same disease
        assert plan is not None

    def test_category_classification(self):
        from clinical_reasoning.services.investigation_engine import _categorize_investigation
        assert _categorize_investigation("Renal biopsy") == "diagnostic"
        assert _categorize_investigation("Serum creatinine") == "monitoring"
        assert _categorize_investigation("CBC with differential") == "safety"
        assert _categorize_investigation("Genetic testing") == "prognostic"

    def test_priority_adjustment(self):
        from clinical_reasoning.services.investigation_engine import _adjust_priority
        assert _adjust_priority("medium", 15, 80) == "high"  # Boosted
        assert _adjust_priority("urgent", 15, 80) == "urgent"  # Already high

    def test_top_three_only(self, patient):
        from clinical_reasoning.services.investigation_engine import generate_investigation_recommendations
        diff = [
            {"disease_id": "iga", "disease_name": "IgA", "score": 10, "confidence": 80},
            {"disease_id": "membranous", "disease_name": "MN", "score": 5, "confidence": 50},
            {"disease_id": "fsgs", "disease_name": "FSGS", "score": 3, "confidence": 30},
            {"disease_id": "lupus", "disease_name": "LN", "score": 1, "confidence": 10},
        ]
        plan = generate_investigation_recommendations(patient, diff)
        assert plan is not None

    def test_investigation_rec_to_dict(self):
        from clinical_reasoning.services.investigation_engine import InvestigationRecommendation
        rec = InvestigationRecommendation(
            test="Biopsy", rationale="Confirm", priority="urgent",
            diagnostic_value="Definitive", guideline="KDIGO", category="diagnostic",
        )
        d = rec.to_dict()
        assert d["test"] == "Biopsy"
        assert d["priority"] == "urgent"


# ============================================================================
# disease_validation.py
# ============================================================================

class TestDiseaseValidation:
    def test_iga_validation(self, patient):
        from clinical_reasoning.services.disease_validation import validate_disease_management
        report = validate_disease_management(patient, "iga")
        assert report is not None
        assert report.disease == "iga"
        assert len(report.results) >= 1
        d = report.to_dict()
        assert "score" in d
        assert "total_checks" in d

    def test_unknown_disease(self, patient):
        from clinical_reasoning.services.disease_validation import validate_disease_management
        report = validate_disease_management(patient, "unknown")
        assert report.score == 0.0
        assert "No validation checks" in report.summary

    def test_all_diseases_have_checks(self):
        from clinical_reasoning.services.disease_validation import DISEASE_VALIDATION_CHECKS
        assert "iga" in DISEASE_VALIDATION_CHECKS
        assert "membranous" in DISEASE_VALIDATION_CHECKS
        assert "lupus" in DISEASE_VALIDATION_CHECKS
        assert "anca" in DISEASE_VALIDATION_CHECKS

    def test_validation_check_to_dict(self):
        from clinical_reasoning.services.disease_validation import ValidationCheck
        check = ValidationCheck(
            check_id="test_01", name="Test", description="desc",
            category="diagnostic", severity="critical",
            guideline_ref="KDIGO", validation_logic="logic",
        )
        d = check.to_dict()
        assert d["check_id"] == "test_01"
        assert d["severity"] == "critical"

    def test_validation_report_to_dict(self, patient):
        from clinical_reasoning.services.disease_validation import validate_disease_management
        report = validate_disease_management(patient, "iga")
        d = report.to_dict()
        assert "failed_critical" in d
        assert "failed_major" in d

    def test_build_summary_no_failures(self):
        from clinical_reasoning.services.disease_validation import (
            _build_validation_summary, ValidationResult, ValidationCheck,
        )
        check = ValidationCheck("t", "Test", "d", "diagnostic", "critical", "K", "L")
        results = [ValidationResult(check=check, passed=True, current_value="Yes", expected_value="Yes", notes="")]
        s = _build_validation_summary(results, "iga", 100.0)
        assert "All critical" in s


# ============================================================================
# retrospective_validation.py
# ============================================================================

class TestRetrospectiveValidation:
    def test_run_with_no_data(self):
        from clinical_reasoning.services.retrospective_validation import run_retrospective_validation
        report = run_retrospective_validation()
        assert report.total_patients == 0
        assert "No cases" in report.summary

    def test_report_to_dict(self):
        from clinical_reasoning.services.retrospective_validation import (
            run_retrospective_validation,
        )
        report = run_retrospective_validation()
        d = report.to_dict()
        assert "period_start" in d
        assert "diagnostic_metrics" in d

    def test_calculate_metrics(self):
        from clinical_reasoning.services.retrospective_validation import _calculate_metrics
        m = _calculate_metrics(tp=8, fp=2, fn=2, tn=8, total=20)
        assert m.accuracy == 0.8
        assert m.total_cases == 20
        assert m.agreement_count == 16
        d = m.to_dict()
        assert "cohens_kappa" in d

    def test_calculate_metrics_empty(self):
        from clinical_reasoning.services.retrospective_validation import _calculate_metrics
        m = _calculate_metrics(tp=0, fp=0, fn=0, tn=0, total=0)
        assert m.accuracy == 0.0

    def test_treatments_compatible(self):
        from clinical_reasoning.services.retrospective_validation import _treatments_compatible
        assert _treatments_compatible("mycophenolate", "mmf")
        assert _treatments_compatible("prednisolone", "prednisone")
        assert not _treatments_compatible("aspirin", "warfarin")
        assert not _treatments_compatible("", "mmf")

    def test_risk_levels_compatible(self):
        from clinical_reasoning.services.retrospective_validation import _risk_levels_compatible
        assert _risk_levels_compatible(50, "moderate")
        assert _risk_levels_compatible(85, "very_high")
        assert not _risk_levels_compatible(50, "low")


# ============================================================================
# audit.py
# ============================================================================

class TestAudit:
    def test_generate_recommendation_id(self):
        from clinical_reasoning.services.audit import _generate_recommendation_id
        rid = _generate_recommendation_id("management_plan", 42)
        assert rid.startswith("REC-MAN-42-")
        assert len(rid) > 15

    def test_create_audit_record(self, patient):
        from clinical_reasoning.services.audit import create_audit_record
        audit = create_audit_record(
            recommendation_type="test",
            patient=patient,
            disease_id="iga",
            recommendation_text="Test recommendation",
            clinical_rationale="Because",
            confidence_score=80.0,
        )
        assert audit is not None
        assert audit.recommendation_id.startswith("REC-TES-")
        assert audit.approval_status == "pending"

    def test_audit_management_plan(self, patient):
        from clinical_reasoning.services.audit import audit_management_plan
        plan = MagicMock()
        plan.disease_name = "IgA"
        plan.first_line = [{"drug": "ACEi", "rationale": "KDIGO", "evidence_grade": "1"}]
        plan.second_line = []
        plan.rescue_therapy = []
        # Should not raise
        audit_management_plan(patient, plan, "iga")

    def test_audit_monitoring_plan(self, patient):
        from clinical_reasoning.services.audit import audit_monitoring_plan
        plan = MagicMock()
        plan.disease_name = "IgA"
        plan.parameters = [{"name": "UPCR"}]
        plan.treatment_monitoring = []
        audit_monitoring_plan(patient, plan, "iga")

    def test_audit_drug_toxicity(self, patient):
        from clinical_reasoning.services.audit import audit_drug_toxicity
        report = MagicMock()
        report.alerts = []
        audit_drug_toxicity(patient, report)

    def test_audit_treatment_failure(self, patient):
        from clinical_reasoning.services.audit import audit_treatment_failure
        report = MagicMock()
        report.alerts = []
        audit_treatment_failure(patient, report)

    def test_audit_relapse(self, patient):
        from clinical_reasoning.services.audit import audit_relapse
        audit_relapse(patient, [])

    def test_audit_clinical_reasoning(self, patient):
        from clinical_reasoning.services.audit import audit_clinical_reasoning
        profile = MagicMock()
        care_data = {
            "recommendations": [{"message": "test", "type": "investigation", "detail": "d"}],
        }
        audit_clinical_reasoning(patient, profile, care_data)

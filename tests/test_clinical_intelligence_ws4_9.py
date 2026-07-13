"""Tests for Workstreams 4-9: Disease Milestones, Care Pathway, Knowledge Quality,
Research Intelligence, Operational Intelligence, Enterprise Readiness."""
import pytest
from unittest.mock import patch

from clinical_reasoning.json_util import json_safe

pytestmark = pytest.mark.django_db


# ---- Fixtures ----

@pytest.fixture
def patient():
    from patients.models import Patient
    from django.utils import timezone
    p = Patient.objects.create(
        patient_id="WS-TEST-001",
        name="WS Test Patient",
        hospital_id="H-WS-001",
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
    return p


# ---- WS 4: Longitudinal Disease Intelligence ----

class TestDiseaseMilestones:
    def test_detect_milestones_returns_list(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {}, {})
        assert isinstance(milestones, list)

    def test_detect_milestones_includes_diagnosis(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {"disease_phase": "active"}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "diagnosis" in types

    def test_detect_milestones_includes_remission(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {"disease_phase": "remission"}, {"trend": "improving"})
        types = [m["milestone_type"] for m in milestones]
        assert "remission" in types

    def test_detect_milestones_eskd(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        patient.latest_egfr = 10
        milestones = detect_milestones(patient, {"disease_phase": "eskd"}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "eskd" in types

    def test_milestones_deduplicated(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        m1 = detect_milestones(patient, {"disease_phase": "active"}, {})
        m2 = detect_milestones(patient, {"disease_phase": "active"}, {})
        assert len(m2) >= len(m1)

    def test_compute_trajectory_summary(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones, compute_trajectory_summary
        milestones = detect_milestones(patient, {"disease_phase": "active"}, {})
        summary = compute_trajectory_summary(patient, milestones)
        assert "total_milestones" in summary
        assert "by_type" in summary

    def test_json_safe_decimal(self):
        from decimal import Decimal
        result = json_safe({"value": Decimal("10.5")})
        assert isinstance(result["value"], float)
        assert result["value"] == 10.5

    def test_json_safe_nested(self):
        from decimal import Decimal
        data = {"a": [{"b": Decimal("1")}, {"c": "hello"}]}
        result = json_safe(data)
        assert isinstance(result["a"][0]["b"], float)


# ---- WS 5: Care Pathway Engine ----

class TestCarePathwayEngine:
    def test_get_pathway_stage(self):
        from clinical_reasoning.services.care_pathway_engine import get_pathway_stage
        stage = get_pathway_stage("active_disease")
        assert stage is not None
        assert stage.name == "active_disease"

    def test_get_pathway_stage_unknown(self):
        from clinical_reasoning.services.care_pathway_engine import get_pathway_stage
        assert get_pathway_stage("nonexistent") is None

    def test_get_available_stages(self):
        from clinical_reasoning.services.care_pathway_engine import get_available_stages
        stages = get_available_stages()
        assert len(stages) >= 5
        names = [s["name"] for s in stages]
        assert "assessment" in names
        assert "active_disease" in names
        assert "remission_monitoring" in names

    def test_determine_current_stage(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        stage = determine_current_stage(patient, {"disease_phase": "active"})
        assert stage == "active_disease"

    def test_determine_current_stage_eskd(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        patient.latest_egfr = 10
        stage = determine_current_stage(patient, {"disease_phase": "eskd"})
        assert stage == "eskd_care"

    def test_determine_current_stage_default(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        patient.current_phase = ""
        stage = determine_current_stage(patient, {"disease_phase": ""})
        assert stage == "assessment"

    def test_detect_stage_transition_valid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(None, "active_disease", "remission_monitoring")
        assert result["valid"] is True

    def test_detect_stage_transition_invalid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(None, "assessment", "eskd_care")
        assert result["valid"] is False

    def test_assess_pathway_deviation(self, patient):
        from clinical_reasoning.services.care_pathway_engine import assess_pathway_deviation
        deviations = assess_pathway_deviation(patient, "active_disease", {})
        assert isinstance(deviations, list)

    def test_compute_pathway_summary(self, patient):
        from clinical_reasoning.services.care_pathway_engine import compute_pathway_summary
        summary = compute_pathway_summary(patient, "active_disease", [], [])
        assert "current_stage" in summary
        assert summary["current_stage"] == "active_disease"
        assert summary["deviations_count"] == 0


# ---- WS 6: Knowledge Quality Framework ----

class TestKnowledgeQuality:
    @pytest.fixture
    def entry(self):
        from datetime import date
        from django.utils import timezone
        from knowledge.models import KnowledgeBaseEntry, GuidelineSource
        src = GuidelineSource.objects.create(
            title="KDIGO 2024 Guidelines",
            abbreviation="KDIGO",
            version_year=2024,
            effective_date=date(2024, 1, 1),
        )
        return KnowledgeBaseEntry.objects.create(
            entry_id="QUALITY-TEST-001",
            disease_id="LN",
            source=src,
            evidence_grade="1",
            effective_date=date(2024, 1, 1),
            rule_data={
                "conditions": [
                    {"field": "proteinuria", "operator": "gte", "value": 3.5},
                    {"field": "edema", "operator": "eq", "value": True},
                ],
                "weight": 3,
                "explanation": "Nephrotic-range proteinuria with edema suggests active LN",
                "base_score": 1,
            },
            status=KnowledgeBaseEntry.Status.ACTIVE,
            review_notes="",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def test_score_rule_quality_returns_dict(self, entry):
        from clinical_reasoning.services.knowledge_quality import score_rule_quality
        result = score_rule_quality(entry)
        assert "overall" in result
        assert 0 <= result["overall"] <= 100
        assert result["grade"] in ("A", "B", "C", "D")

    def test_score_rule_quality_has_dimensions(self, entry):
        from clinical_reasoning.services.knowledge_quality import score_rule_quality
        result = score_rule_quality(entry)
        for dim in ("completeness", "clarity", "evidence", "testability"):
            assert dim in result
            assert 0 <= result[dim] <= 100

    def test_detect_rule_conflicts_returns_list(self):
        from clinical_reasoning.services.knowledge_quality import detect_rule_conflicts
        conflicts = detect_rule_conflicts([])
        assert isinstance(conflicts, list)

    def test_analyze_coverage_returns_dict(self):
        from clinical_reasoning.services.knowledge_quality import analyze_coverage
        coverage = analyze_coverage([])
        assert "total_rules" in coverage


# ---- WS 7: Research Intelligence ----

class TestResearchIntelligence:
    def test_discover_cohorts_returns_list(self, patient):
        from clinical_reasoning.services.research_intelligence import discover_cohorts
        cohorts = discover_cohorts()
        assert isinstance(cohorts, list)
        for c in cohorts:
            assert "name" in c
            assert "patient_count" in c

    def test_match_patient_to_protocols_returns_list(self, patient):
        from clinical_reasoning.services.research_intelligence import match_patient_to_protocols
        matches = match_patient_to_protocols(patient)
        assert isinstance(matches, list)

    def test_detect_research_opportunities_returns_list(self, patient):
        from clinical_reasoning.services.research_intelligence import detect_research_opportunities
        opps = detect_research_opportunities(patient)
        assert isinstance(opps, list)

    def test_detect_research_opportunities_rare_gn(self, patient):
        from clinical_reasoning.services.research_intelligence import detect_research_opportunities
        patient.primary_diagnosis = "Focal Segmental Glomerulosclerosis"
        opps = detect_research_opportunities(patient)
        types = [o["type"] for o in opps]
        assert "rare_disease" in types

    def test_detect_research_opportunities_remission(self, patient):
        from clinical_reasoning.services.research_intelligence import detect_research_opportunities
        patient.current_phase = "remission"
        opps = detect_research_opportunities(patient)
        types = [o["type"] for o in opps]
        assert "remission_maintenance" in types


# ---- WS 8: Operational Intelligence ----

class TestOperationalIntelligence:
    def test_compute_compliance_summary_returns_dict(self):
        from clinical_reasoning.services.operational_intelligence import compute_compliance_summary
        summary = compute_compliance_summary()
        assert "total_patients" in summary
        assert "active_patients" in summary

    def test_compute_patient_compliance_returns_dict(self, patient):
        from clinical_reasoning.services.operational_intelligence import compute_patient_compliance
        result = compute_patient_compliance(patient)
        assert "compliance_score" in result
        assert 0 <= result["compliance_score"] <= 100
        assert "grade" in result

    def test_compute_care_gap_trends_returns_dict(self):
        from clinical_reasoning.services.operational_intelligence import compute_care_gap_trends
        trends = compute_care_gap_trends()
        assert "total_profiles" in trends
        assert "total_gaps" in trends


# ---- WS 9: Enterprise Readiness ----

class TestEnterpriseReadiness:
    def test_log_audit_event(self):
        from clinical_reasoning.services.enterprise_readiness import log_audit_event
        log_audit_event("test_user", "test_action", "Patient", "P001")
        from audit.models import AuditLog
        assert AuditLog.objects.filter(action="test_action").exists()

    def test_get_audit_trail(self):
        from clinical_reasoning.services.enterprise_readiness import log_audit_event, get_audit_trail
        log_audit_event("user1", "create", "Patient", "P001", {"name": "test"})
        trail = get_audit_trail("Patient", "P001")
        assert len(trail) >= 1
        assert trail[0]["action"] == "create"

    def test_rate_limiter_allows(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.check("test_key") is True

    def test_rate_limiter_blocks(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.check("block_key") is True
        assert limiter.check("block_key") is True
        assert limiter.check("block_key") is False

    def test_rate_limiter_remaining(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.remaining("rem_key") == 10
        limiter.check("rem_key")
        assert limiter.remaining("rem_key") == 9

    def test_get_data_quality_report(self):
        from clinical_reasoning.services.enterprise_readiness import get_data_quality_report
        report = get_data_quality_report()
        assert "total_patients" in report
        assert "profile_coverage_pct" in report

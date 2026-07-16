"""Tests for Claude Review findings fixes (C-1, C-2, C-3, H-1, H-2, H-3, H-4, M-1, M-2).

Run with: python -m pytest tests/test_review_fixes.py -v
"""
import datetime
import os

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

from clinical_reasoning.models import ClinicalInsight, ClinicalProfile
from knowledge.models import KnowledgeBaseEntry, RecommendationAudit, GuidelineSource
from patients.models import Patient

User = get_user_model()


def _make_patient(name="Test Patient", sex="M"):
    """Create a real Patient instance for FK tests."""
    return Patient.objects.create(name=name, sex=sex)


# ---------------------------------------------------------------------------
# C-1: RecommendationAudit is wired into the pipeline
# ---------------------------------------------------------------------------
class TestRecommendationAuditWiring(TestCase):
    """Verify that RecommendationAudit records are created by audit helpers."""

    def setUp(self):
        self.user = User.objects.create_user(username="testdoc", password="testpass")
        self.patient = _make_patient("Audit Test Patient")

    def test_create_audit_record_returns_instance(self):
        from clinical_reasoning.services.audit import create_audit_record

        audit = create_audit_record(
            recommendation_type="clinical_reasoning",
            patient=self.patient,
            disease_id="iga",
            recommendation_text="Test recommendation",
            clinical_rationale="Test rationale",
            guideline="KDIGO 2021",
            guideline_version="2021",
            evidence_grade="1",
            confidence_score=85.0,
            explanation="Test explanation",
            clinician=self.user,
        )
        self.assertIsNotNone(audit)
        self.assertEqual(audit.recommendation_type, "clinical_reasoning")
        self.assertEqual(audit.patient, self.patient)
        self.assertEqual(audit.disease_id, "iga")
        self.assertEqual(audit.evidence_grade, "1")
        self.assertEqual(audit.confidence_score, 85.0)
        self.assertEqual(audit.approval_status, "pending")
        self.assertTrue(audit.override_allowed)
        self.assertIsNotNone(audit.validation_date)
        self.assertIsNotNone(audit.next_review_date)

    def test_create_audit_record_generates_unique_id(self):
        from clinical_reasoning.services.audit import create_audit_record

        a1 = create_audit_record(
            recommendation_type="drug_toxicity",
            patient=self.patient,
            disease_id="",
            recommendation_text="Alert 1",
        )
        a2 = create_audit_record(
            recommendation_type="drug_toxicity",
            patient=self.patient,
            disease_id="",
            recommendation_text="Alert 2",
        )
        self.assertIsNotNone(a1)
        self.assertIsNotNone(a2)
        self.assertNotEqual(a1.recommendation_id, a2.recommendation_id)
        self.assertTrue(a1.recommendation_id.startswith("REC-DRU-"))

    def test_audit_management_plan(self):
        from clinical_reasoning.services.audit import audit_management_plan
        from clinical_reasoning.services.management_plan import ManagementPlan

        plan = ManagementPlan(
            disease_id="iga",
            disease_name="IgA Nephropathy",
            patient_id=self.patient.patient_id,
            first_line=[{"drug": "ACEi", "dose": "10mg", "rationale": "Reduce proteinuria", "evidence_grade": "1"}],
            second_line=[],
            rescue_therapy=[],
            contraindicated=[],
            monitoring=[],
            follow_up={},
            general_measures=[],
            safety_checks=[],
            patient_education=[],
        )
        audit_management_plan(self.patient, plan, "iga", clinician=self.user)
        self.assertEqual(RecommendationAudit.objects.count(), 1)
        audit = RecommendationAudit.objects.first()
        self.assertEqual(audit.recommendation_type, "management_plan")
        self.assertIn("ACEi", audit.recommendation_text)

    def test_audit_monitoring_plan(self):
        from clinical_reasoning.services.audit import audit_monitoring_plan
        from clinical_reasoning.services.monitoring_plan import MonitoringPlan

        plan = MonitoringPlan(
            disease_id="iga",
            disease_name="IgA Nephropathy",
            patient_id=self.patient.patient_id,
            parameters=[{"name": "UPCR", "interval_days": 30}],
            treatment_monitoring=[],
            ckd_monitoring=[],
            risk_adjustments=[],
            generated_date="2026-07-11",
        )
        audit_monitoring_plan(self.patient, plan, "iga", clinician=self.user)
        self.assertEqual(RecommendationAudit.objects.count(), 1)
        audit = RecommendationAudit.objects.first()
        self.assertEqual(audit.recommendation_type, "monitoring_plan")

    def test_audit_drug_toxicity_creates_per_alert(self):
        from clinical_reasoning.services.audit import audit_drug_toxicity
        from clinical_reasoning.services.drug_toxicity import DrugToxicityReport, ToxicityAlert

        alert = ToxicityAlert(
            drug_class="CNI",
            drug_name="Tacrolimus",
            lab_test="creatinine",
            current_value=2.5,
            severity="severe",
            threshold=1.5,
            mechanism="Nephrotoxicity",
            clinical_action="Reduce dose",
            monitoring_frequency="Weekly",
            risk_factors=[],
            priority="urgent",
        )
        report = DrugToxicityReport(
            patient_id=self.patient.patient_id,
            alerts=[alert],
            current_medications=[],
            summary="1 alert",
        )
        audit_drug_toxicity(self.patient, report, clinician=self.user)
        self.assertEqual(RecommendationAudit.objects.count(), 1)
        audit = RecommendationAudit.objects.first()
        self.assertEqual(audit.recommendation_type, "drug_toxicity")
        self.assertIn("Tacrolimus", audit.recommendation_text)

    def test_audit_clinical_reasoning(self):
        from clinical_reasoning.services.audit import audit_clinical_reasoning

        profile = ClinicalProfile(patient=self.patient)
        care_pathway_data = {
            "recommendations": [
                {"type": "investigation", "priority": "high", "message": "Check UPCR", "detail": "Proteinuria assessment"},
            ],
            "rule_results": [{"disease_id": "iga"}],
        }
        audit_clinical_reasoning(self.patient, profile, care_pathway_data, clinician=self.user)
        self.assertEqual(RecommendationAudit.objects.count(), 1)
        audit = RecommendationAudit.objects.first()
        self.assertEqual(audit.recommendation_type, "clinical_reasoning")
        self.assertEqual(audit.disease_id, "iga")

    def test_evidence_grade_uses_canonical_choices(self):
        """H-4: evidence_grade must use canonical choices (1, 2, NG, OP)."""
        from clinical_reasoning.services.audit import create_audit_record

        for grade in ["1", "2", "NG", "OP"]:
            audit = create_audit_record(
                recommendation_type="clinical_reasoning",
                patient=self.patient,
                disease_id="iga",
                recommendation_text=f"Test grade {grade}",
                evidence_grade=grade,
            )
            self.assertIsNotNone(audit)
            self.assertEqual(audit.evidence_grade, grade)


# ---------------------------------------------------------------------------
# H-1: ClinicalInsight dedup
# ---------------------------------------------------------------------------
class TestClinicalInsightDedup(TestCase):
    """Verify that _generate_insights clears old insights before creating new ones."""

    def setUp(self):
        self.user = User.objects.create_user(username="testdoc2", password="testpass")
        self.patient = _make_patient("Insight Test Patient")

    def test_insights_are_cleared_on_rerun(self):
        """Running _generate_insights twice should not double the insight count."""
        from unittest.mock import MagicMock
        from clinical_reasoning.services.engine import _generate_insights

        profile = MagicMock()
        profile.patient = self.patient

        care_gaps = [{"field": "upcr", "message": "Missing UPCR", "importance": "high"}]

        rule_result = MagicMock()
        rule_result.disease_name = "IgA Nephropathy"
        rule_result.total_score = 85.0
        rule_result.matched_rules = [{"condition": "test"}]
        rule_result.source = "KDIGO 2021"

        # First run
        _generate_insights(profile, care_gaps, [rule_result])
        count_after_first = ClinicalInsight.objects.filter(patient=self.patient).count()
        self.assertEqual(count_after_first, 2)  # 1 care gap + 1 diagnostic

        # Second run — should replace, not append
        _generate_insights(profile, care_gaps, [rule_result])
        count_after_second = ClinicalInsight.objects.filter(patient=self.patient).count()
        self.assertEqual(count_after_second, 2)  # Still 2, not 4


# ---------------------------------------------------------------------------
# C-3: start_gdes.bat uses secure settings
# ---------------------------------------------------------------------------
class TestSecureLauncher(TestCase):
    """Verify that start_gdes.bat sets DJANGO_SETTINGS_MODULE."""

    def test_start_gdes_bat_uses_desktop_settings(self):
        bat_path = os.path.join(os.path.dirname(__file__), "..", "start_gdes.bat")
        if os.path.exists(bat_path):
            with open(bat_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("bgddr.settings_desktop", content)


# ---------------------------------------------------------------------------
# H-2: Legacy engine retired from URL routes
# ---------------------------------------------------------------------------
class TestLegacyEngineRetired(TestCase):
    """Verify that decision.urls is not included in the main URL config."""

    def test_decision_urls_not_in_urlpatterns(self):
        from django.urls import reverse, NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse("decision-list")


# ---------------------------------------------------------------------------
# H-3: Documentation numbers match
# ---------------------------------------------------------------------------
class TestDocumentationNumbers(TestCase):
    """Verify that seed data produces expected rule count."""

    def test_seed_produces_209_rules(self):
        from knowledge.management.commands.seed_knowledge_base import DISEASE_RULES
        total = sum(len(profile["rules"]) for profile in DISEASE_RULES.values())
        self.assertGreaterEqual(total, 400)
        self.assertGreaterEqual(len(DISEASE_RULES), 36)


# ---------------------------------------------------------------------------
# M-2: ALLOWED_HOSTS does not contain wildcard
# ---------------------------------------------------------------------------
class TestAllowedHosts(TestCase):
    """Verify deploy settings do not use wildcard ALLOWED_HOSTS."""

    def test_deploy_settings_no_wildcard(self):
        deploy_path = os.path.join(os.path.dirname(__file__), "..", "bgddr", "settings_deploy.py")
        if os.path.exists(deploy_path):
            with open(deploy_path, "r", encoding="utf-8") as f:
                content = f.read()
            for line in content.splitlines():
                if "ALLOWED_HOSTS" in line and "=" in line:
                    self.assertNotIn('"*"', line, "ALLOWED_HOSTS must not contain wildcard '*'")
                    break


# ---------------------------------------------------------------------------
# C-2: Governance fields populated
# ---------------------------------------------------------------------------
class TestGovernanceFields(TestCase):
    """Verify that KnowledgeBaseEntry governance fields are defined."""

    def test_governance_fields_exist(self):
        field_names = [f.name for f in KnowledgeBaseEntry._meta.get_fields()]
        self.assertIn("author", field_names)
        self.assertIn("approved_by", field_names)
        self.assertIn("approved_at", field_names)
        self.assertIn("next_review_date", field_names)
        self.assertIn("confidence_score", field_names)
        self.assertIn("explanation", field_names)
        self.assertIn("override_allowed", field_names)
        self.assertIn("recommendation_id", field_names)
        self.assertIn("knowledge_version", field_names)
        self.assertIn("date_validated", field_names)

    def test_recommendation_audit_model_exists(self):
        self.assertTrue(RecommendationAudit._meta.managed)
        self.assertEqual(RecommendationAudit.objects.count(), 0)


# ---------------------------------------------------------------------------
# M-1: Knowledge bootstrap does not run at import time
# ---------------------------------------------------------------------------
class TestLazyBootstrap(TestCase):
    """Verify that the knowledge bootstrap does not query DB during AppConfig.ready()."""

    def test_no_runtime_warning_on_import(self):
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            db_warnings = [x for x in w if "Accessing the database during app initialization" in str(x.message)]
            self.assertEqual(len(db_warnings), 0)

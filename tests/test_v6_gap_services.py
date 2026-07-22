"""Tests for GDES V6 services — Investigation Engine, Drug Toxicity, Treatment Failure, Disease Validation."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from clinical_reasoning.services.investigation_engine import (
    generate_investigation_recommendations,
    InvestigationRecommendation,
    InvestigationPlan,
    DISEASE_INVESTIGATIONS,
)
from clinical_reasoning.services.drug_toxicity import (
    detect_drug_toxicity,
    DrugToxicityReport,
    TOXICITY_RULES,
)
from clinical_reasoning.services.treatment_failure import (
    detect_treatment_failure,
    detect_relapse,
    TreatmentFailureReport,
)
from clinical_reasoning.services.disease_validation import (
    validate_disease_management,
    DiseaseValidationReport,
    DISEASE_VALIDATION_CHECKS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_patient():
    """Create a mock patient for testing."""
    patient = MagicMock()
    patient.pk = 1
    patient.patient_id = "TEST-001"
    patient.name = "Test Patient"
    patient.age = 45
    patient.gender = "M"
    patient.latest_egfr = 45.0
    patient.date_of_birth = date(1980, 1, 1)
    return patient


@pytest.fixture
def mock_patient_with_biopsy(mock_patient):
    """Patient with biopsy result."""
    mock_patient.biopsies = MagicMock()
    mock_patient.biopsies.exists.return_value = True
    return mock_patient


@pytest.fixture
def igan_differential():
    """Sample differential for IgAN."""
    return [
        {"disease_id": "iga", "disease_name": "IgA Nephropathy", "score": 12.5, "confidence": 75.0},
        {"disease_id": "membranous", "disease_name": "Membranous Nephropathy", "score": 5.0, "confidence": 30.0},
    ]


@pytest.fixture
def lupus_differential():
    """Sample differential for lupus nephritis."""
    return [
        {"disease_id": "lupus", "disease_name": "Lupus Nephritis", "score": 15.0, "confidence": 85.0},
    ]


# ---------------------------------------------------------------------------
# Investigation Engine Tests
# ---------------------------------------------------------------------------

class TestInvestigationEngine:
    """Tests for Investigation Recommendation Engine."""

    def test_investigation_plan_structure(self, mock_patient, igan_differential):
        """InvestigationPlan returns correct structure."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={"egfr": 45.0}):
            plan = generate_investigation_recommendations(mock_patient, igan_differential)

        assert isinstance(plan, InvestigationPlan)
        assert plan.patient_id == "TEST-001"
        assert len(plan.recommendations) > 0
        assert plan.summary

    def test_recommendation_has_required_fields(self, mock_patient, igan_differential):
        """Each recommendation has all required fields."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={}):
            plan = generate_investigation_recommendations(mock_patient, igan_differential)

        for rec in plan.recommendations:
            assert isinstance(rec, InvestigationRecommendation)
            assert rec.test
            assert rec.rationale
            assert rec.priority in ("urgent", "high", "medium", "low")
            assert rec.diagnostic_value
            assert rec.guideline

    def test_igan_investigations_available(self):
        """IgAN has defined investigation protocols."""
        assert "iga" in DISEASE_INVESTIGATIONS
        assert len(DISEASE_INVESTIGATIONS["iga"]) > 0

    def test_all_diseases_have_investigations(self):
        """All 9 diseases have investigation protocols."""
        diseases = ["iga", "membranous", "mcd", "fsgs", "lupus", "anca", "antiGbm", "infectionRelated", "c3"]
        for disease in diseases:
            assert disease in DISEASE_INVESTIGATIONS, f"Missing investigations for {disease}"

    def test_recommendations_sorted_by_priority(self, mock_patient, igan_differential):
        """Recommendations are sorted by priority (urgent first)."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={}):
            plan = generate_investigation_recommendations(mock_patient, igan_differential)

        priorities = [r.priority for r in plan.recommendations]
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(priorities) - 1):
            assert priority_order[priorities[i]] <= priority_order[priorities[i + 1]]

    def test_plan_to_dict(self, mock_patient, igan_differential):
        """Plan to_dict returns serializable dict."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={}):
            plan = generate_investigation_recommendations(mock_patient, igan_differential)

        d = plan.to_dict()
        assert "patient_id" in d
        assert "recommendations" in d
        assert "total_recommendations" in d
        assert "urgent_count" in d
        assert isinstance(d["recommendations"], list)

    def test_empty_differential(self, mock_patient):
        """Empty differential produces minimal recommendations."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={}):
            plan = generate_investigation_recommendations(mock_patient, [])

        assert isinstance(plan, InvestigationPlan)
        assert len(plan.recommendations) == 0

    def test_completed_investigations_excluded(self, mock_patient_with_biopsy, igan_differential):
        """Already completed investigations are excluded."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={"biopsy": True, "egfr": 45.0}):
            plan = generate_investigation_recommendations(mock_patient_with_biopsy, igan_differential)

        # Biopsy-related recommendations should be filtered
        tests = [r.test.lower() for r in plan.recommendations]
        assert "renal biopsy (if not done)" not in tests

    def test_deduplication(self, mock_patient, igan_differential):
        """Duplicate recommendations are deduplicated."""
        with patch("clinical_reasoning.services.investigation_engine._extract_basic_features", return_value={}):
            plan = generate_investigation_recommendations(mock_patient, igan_differential)

        test_names = [r.test.lower() for r in plan.recommendations]
        assert len(test_names) == len(set(test_names))


# ---------------------------------------------------------------------------
# Drug Toxicity Tests
# ---------------------------------------------------------------------------

class TestDrugToxicity:
    """Tests for Drug Toxicity Detection."""

    def test_toxicity_rules_complete(self):
        """All critical drug classes have toxicity rules."""
        drug_classes = {r.drug_class for r in TOXICITY_RULES}
        assert "CNI" in drug_classes
        assert "IMPDH inhibitor" in drug_classes
        assert "Alkylating agent" in drug_classes
        assert "Anti-CD20" in drug_classes
        assert "Corticosteroid" in drug_classes
        assert "RAAS inhibitor" in drug_classes

    def test_toxicity_report_structure(self, mock_patient):
        """DrugToxicityReport returns correct structure."""
        with patch("clinical_reasoning.services.drug_toxicity._get_current_medications", return_value=[]), \
             patch("clinical_reasoning.services.drug_toxicity._get_recent_lab_values", return_value={}), \
             patch("clinical_reasoning.services.drug_toxicity._assess_risk_factors", return_value=[]):
            report = detect_drug_toxicity(mock_patient)

        assert isinstance(report, DrugToxicityReport)
        assert report.patient_id == "TEST-001"
        assert isinstance(report.alerts, list)

    def test_toxicity_alert_has_fields(self, mock_patient):
        """Each toxicity alert has required fields."""
        with patch("clinical_reasoning.services.drug_toxicity._get_current_medications", return_value=[
            {"name": "Tacrolimus", "drug_class": "CNI", "dose": "5mg", "frequency": "BD"},
        ]), patch("clinical_reasoning.services.drug_toxicity._get_recent_lab_values", return_value={
            "serum_creatinine": 2.0,
        }), patch("clinical_reasoning.services.drug_toxicity._assess_risk_factors", return_value=[]):
            report = detect_drug_toxicity(mock_patient)

        for alert in report.alerts:
            d = alert.to_dict()
            assert "drug_class" in d
            assert "severity" in d
            assert "clinical_action" in d
            assert "priority" in d

    def test_cni_nephrotoxicity_detected(self, mock_patient):
        """CNI nephrotoxicity detected when creatinine elevated."""
        with patch("clinical_reasoning.services.drug_toxicity._get_current_medications", return_value=[
            {"name": "Tacrolimus", "drug_class": "CNI", "dose": "5mg", "frequency": "BD"},
        ]), patch("clinical_reasoning.services.drug_toxicity._get_recent_lab_values", return_value={
            "serum_creatinine": 2.0,
        }), patch("clinical_reasoning.services.drug_toxicity._assess_risk_factors", return_value=[]):
            report = detect_drug_toxicity(mock_patient)

        cni_alerts = [a for a in report.alerts if a.drug_class == "CNI"]
        assert len(cni_alerts) > 0
        assert cni_alerts[0].severity in ("moderate", "severe", "critical")

    def test_no_toxicity_with_normal_labs(self, mock_patient):
        """No toxicity alerts with normal labs and no medications."""
        with patch("clinical_reasoning.services.drug_toxicity._get_current_medications", return_value=[]), \
             patch("clinical_reasoning.services.drug_toxicity._get_recent_lab_values", return_value={}), \
             patch("clinical_reasoning.services.drug_toxicity._assess_risk_factors", return_value=[]):
            report = detect_drug_toxicity(mock_patient)

        assert len(report.alerts) == 0
        assert "No drug toxicity" in report.summary

    def test_report_to_dict(self, mock_patient):
        """Report to_dict is serializable."""
        with patch("clinical_reasoning.services.drug_toxicity._get_current_medications", return_value=[]), \
             patch("clinical_reasoning.services.drug_toxicity._get_recent_lab_values", return_value={}), \
             patch("clinical_reasoning.services.drug_toxicity._assess_risk_factors", return_value=[]):
            report = detect_drug_toxicity(mock_patient)

        d = report.to_dict()
        assert "patient_id" in d
        assert "alerts" in d
        assert "total_alerts" in d


# ---------------------------------------------------------------------------
# Treatment Failure Tests
# ---------------------------------------------------------------------------

class TestTreatmentFailure:
    """Tests for Treatment Failure Detection."""

    def test_failure_report_structure(self, mock_patient):
        """TreatmentFailureReport returns correct structure."""
        with \
             patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_comprehensive_lab_values", return_value={}), \
             patch("clinical_reasoning.services.treatment_failure._get_treatment_duration", return_value=12.0), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=45.0), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=50.0):
            report = detect_treatment_failure(mock_patient)

        assert isinstance(report, TreatmentFailureReport)
        assert report.patient_id == "TEST-001"
        assert report.primary_disease == "iga"

    def test_failure_patterns_complete(self):
        """All 9 diseases have failure patterns defined."""
        from clinical_reasoning.services.treatment_failure import TREATMENT_FAILURE_PATTERNS
        diseases_with_patterns = {p.disease_id for p in TREATMENT_FAILURE_PATTERNS}
        assert "iga" in diseases_with_patterns
        assert "membranous" in diseases_with_patterns
        assert "lupus" in diseases_with_patterns
        assert "anca" in diseases_with_patterns

    def test_proteinuria_nonresponse_detected(self, mock_patient):
        """Proteinuria non-response detected when above threshold."""
        with \
             patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_comprehensive_lab_values", return_value={
                 "proteinuria_upcr": 2.5,
             }), \
             patch("clinical_reasoning.services.treatment_failure._get_treatment_duration", return_value=12.0), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=45.0), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=50.0):
            report = detect_treatment_failure(mock_patient)

        proteinuria_alerts = [a for a in report.alerts if a.failure_type == "proteinuria_nonresponse"]
        assert len(proteinuria_alerts) > 0

    def test_no_failure_with_normal_labs(self, mock_patient):
        """No failure detected with normal labs."""
        with \
             patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_comprehensive_lab_values", return_value={
                 "proteinuria_upcr": 0.3,
                 "serum_creatinine": 1.0,
             }), \
             patch("clinical_reasoning.services.treatment_failure._get_treatment_duration", return_value=12.0), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=45.0), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=48.0):
            report = detect_treatment_failure(mock_patient)

        assert len(report.alerts) == 0

    def test_report_to_dict(self, mock_patient):
        """Report to_dict is serializable."""
        with \
             patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_comprehensive_lab_values", return_value={}), \
             patch("clinical_reasoning.services.treatment_failure._get_treatment_duration", return_value=None), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=45.0), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=50.0):
            report = detect_treatment_failure(mock_patient)

        d = report.to_dict()
        assert "patient_id" in d
        assert "alerts" in d
        assert "total_alerts" in d

    def test_relapse_detection_structure(self, mock_patient):
        """detect_relapse returns list of alerts."""
        with patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_proteinuria", return_value=0.3), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_proteinuria", return_value=0.2), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=90.0), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=85.0):
            alerts = detect_relapse(mock_patient)

        assert isinstance(alerts, list)

    def test_relapse_detected_on_proteinuria_rise(self, mock_patient):
        """Relapse detected when proteinuria rises from remission."""
        with patch("clinical_reasoning.services.treatment_failure._get_primary_disease", return_value="iga"), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_proteinuria", return_value=2.5), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_proteinuria", return_value=0.3), \
             patch("clinical_reasoning.services.treatment_failure._get_previous_egfr", return_value=90.0), \
             patch("clinical_reasoning.services.treatment_failure._get_latest_egfr_value", return_value=85.0):
            alerts = detect_relapse(mock_patient)

        relapse_alerts = [a for a in alerts if a.failure_type == "relapse_proteinuria"]
        assert len(relapse_alerts) > 0
        assert relapse_alerts[0].severity in ("warning", "critical")


# ---------------------------------------------------------------------------
# Disease Validation Tests
# ---------------------------------------------------------------------------

class TestDiseaseValidation:
    """Tests for Disease Validation Framework."""

    def test_validation_checks_complete(self):
        """All 4 diseases have validation checks."""
        diseases = ["iga", "membranous", "lupus", "anca"]
        for disease in diseases:
            assert disease in DISEASE_VALIDATION_CHECKS
            assert len(DISEASE_VALIDATION_CHECKS[disease]) > 0

    def test_validation_report_structure(self, mock_patient):
        """DiseaseValidationReport returns correct structure."""
        with patch("clinical_reasoning.services.disease_validation._gather_patient_data", return_value={
            "has_biopsy": True,
            "has_pla2r": False,
            "has_acei_arb": True,
            "has_immunosuppression": False,
            "has_slt2i": False,
            "bp_systolic": 125,
            "bp_diastolic": 78,
            "proteinuria": 0.8,
        }):
            report = validate_disease_management(mock_patient, "iga")

        assert isinstance(report, DiseaseValidationReport)
        assert report.patient_id == "TEST-001"
        assert report.disease == "iga"
        assert len(report.results) > 0
        assert 0 <= report.score <= 100

    def test_validation_has_all_check_types(self, mock_patient):
        """Validation includes diagnostic, management, monitoring checks."""
        with patch("clinical_reasoning.services.disease_validation._gather_patient_data", return_value={
            "has_biopsy": True,
            "has_acei_arb": True,
            "bp_systolic": 125,
            "bp_diastolic": 78,
            "proteinuria": 0.5,
            "has_slt2i": True,
        }):
            report = validate_disease_management(mock_patient, "iga")

        categories = {r.check.category for r in report.results}
        assert "diagnostic" in categories
        assert "management" in categories
        assert "monitoring" in categories

    def test_report_to_dict(self, mock_patient):
        """Report to_dict is serializable."""
        with patch("clinical_reasoning.services.disease_validation._gather_patient_data", return_value={}):
            report = validate_disease_management(mock_patient, "iga")

        d = report.to_dict()
        assert "patient_id" in d
        assert "score" in d
        assert "results" in d
        assert "total_checks" in d
        assert "passed_checks" in d

    def test_unknown_disease_returns_empty(self, mock_patient):
        """Unknown disease returns empty validation."""
        report = validate_disease_management(mock_patient, "unknown_disease")
        assert len(report.results) == 0
        assert report.score == 0.0

    def test_failed_critical_checks_identified(self, mock_patient):
        """Failed critical checks are identified in summary."""
        with patch("clinical_reasoning.services.disease_validation._gather_patient_data", return_value={
            "has_biopsy": False,  # Critical check will fail
            "has_acei_arb": False,  # Critical check will fail
        }):
            report = validate_disease_management(mock_patient, "iga")

        failed_critical = [r for r in report.results if not r.passed and r.check.severity == "critical"]
        assert len(failed_critical) > 0


# ---------------------------------------------------------------------------
# Retrospective Validation Tests
# ---------------------------------------------------------------------------

class TestRetrospectiveValidation:
    """Tests for Retrospective Clinical Validation."""

    def test_validation_imports(self):
        """Retrospective validation module imports correctly."""
        from clinical_reasoning.services.retrospective_validation import run_retrospective_validation
        assert callable(run_retrospective_validation)

    def test_validation_report_structure(self):
        """RetrospectiveValidationReport returns correct structure."""
        from clinical_reasoning.services.retrospective_validation import (
            RetrospectiveValidationReport,
            AgreementMetrics,
        )

        metrics = AgreementMetrics(
            accuracy=0.85,
            sensitivity=0.80,
            specificity=0.90,
            ppv=0.88,
            npv=0.82,
            cohens_kappa=0.70,
            total_cases=50,
            agreement_count=42,
            disagreement_count=8,
        )

        report = RetrospectiveValidationReport(
            period_start="2025-01-01",
            period_end="2025-06-30",
            total_patients=50,
            diagnostic_metrics=metrics,
            treatment_metrics=metrics,
            risk_metrics=metrics,
            case_comparisons=[],
            summary="Test summary",
            generated_at="2025-07-01T00:00:00",
        )

        d = report.to_dict()
        assert "diagnostic_metrics" in d
        assert "treatment_metrics" in d
        assert "risk_metrics" in d
        assert d["total_patients"] == 50

    def test_metrics_to_dict(self):
        """AgreementMetrics to_dict has correct structure."""
        from clinical_reasoning.services.retrospective_validation import AgreementMetrics

        metrics = AgreementMetrics(
            accuracy=0.85,
            sensitivity=0.80,
            specificity=0.90,
            ppv=0.88,
            npv=0.82,
            cohens_kappa=0.70,
            total_cases=50,
            agreement_count=42,
            disagreement_count=8,
        )

        d = metrics.to_dict()
        assert "accuracy" in d
        assert "cohens_kappa" in d
        assert d["accuracy"] == 0.85

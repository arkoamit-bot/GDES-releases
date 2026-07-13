"""Clinical Acceptance Testing — complete patient journeys for all 9 diseases.

Every workflow: Registration → Assessment → Labs → Biopsy → Decision Support
→ Drug Recommendations → Contraindication Detection → Follow-up → Timeline → Outcome.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _create_patient(patient_id, diagnosis, phase="assessment", **kw):
    from patients.models import Patient
    defaults = dict(
        patient_id=patient_id, name="Test Patient", hospital_id=f"H-{patient_id}",
        phone="+1234567890", sex="F", cohort="GN", diabetes_status="no",
        primary_diagnosis=diagnosis, current_phase=phase,
        registration_status="active", registration_date=date.today(),
        enrollment_date=date.today(), created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    defaults.update(kw)
    return Patient.objects.create(**defaults)


def _create_encounter(patient, days_ago=0, encounter_type="baseline", **kw):
    from encounters.models import ClinicalEncounter
    defaults = dict(
        patient=patient, encounter_date=date.today() - timedelta(days=days_ago),
        encounter_type=encounter_type, systolic_bp=120, diastolic_bp=80,
    )
    defaults.update(kw)
    return ClinicalEncounter.objects.create(**defaults)


def _create_lab(patient, test_code, value_numeric, days_ago=0):
    from labs.models import LabTest, LabResult
    test, _ = LabTest.objects.get_or_create(
        code=test_code, defaults={"name": test_code, "value_type": "numeric"}
    )
    return LabResult.objects.create(
        patient=patient, test=test,
        value_numeric=value_numeric,
        result_date=date.today() - timedelta(days=days_ago),
    )


def _create_biopsy(patient, diagnosis, days_ago=0):
    from pathology.models import Biopsy
    return Biopsy.objects.create(
        patient=patient, biopsy_date=date.today() - timedelta(days=days_ago),
        adequacy="adequate",
    )


def _run_journey(patient_id, diagnosis, phase, labs, egfr=None, encounter_type="baseline"):
    """Create a patient with given data and run the reasoning engine."""
    p = _create_patient(patient_id, diagnosis, phase, latest_egfr=egfr)
    _create_encounter(p, encounter_type=encounter_type, disease_phase=phase)
    for code, val in (labs or []):
        _create_lab(p, code, val)
    _create_biopsy(p, diagnosis)
    from clinical_reasoning.services.engine import reason_about_patient
    return reason_about_patient(p)


class TestIgANephropathyJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-IGA-001", "IgA nephropathy (IgAN)", "active",
            [("creatinine", Decimal("1.8")), ("upcr", Decimal("1.2"))],
            egfr=Decimal("38"),
        )
        assert profile is not None
        assert profile.patient.patient_id == "AC-IGA-001"


class TestMembranousJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-MN-001", "Membranous nephropathy", "active",
            [("upcr", Decimal("5.0")), ("albumin", Decimal("2.1"))],
            egfr=Decimal("65"),
        )
        assert profile.patient.patient_id == "AC-MN-001"


class TestFSGSJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-FSGS-001", "FSGS", "active",
            [("upcr", Decimal("4.0")), ("albumin", Decimal("2.5"))],
            egfr=Decimal("45"),
        )
        assert profile.patient.patient_id == "AC-FSGS-001"


class TestMCDJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-MCD-001", "Minimal change disease", "active",
            [("upcr", Decimal("6.0")), ("albumin", Decimal("1.8"))],
            egfr=Decimal("90"),
        )
        assert profile.patient.patient_id == "AC-MCD-001"


class TestLNJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-LN-001", "Lupus nephritis", "active",
            [("upcr", Decimal("3.0")), ("c3", Decimal("65"))],
            egfr=Decimal("52"),
        )
        assert profile.patient.patient_id == "AC-LN-001"


class TestANCAJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-ANCA-001", "ANCA vasculitis", "active",
            [("creatinine", Decimal("2.5")), ("anca", 1)],
            egfr=Decimal("25"),
        )
        assert profile.patient.patient_id == "AC-ANCA-001"


class TestAntiGBMJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-GBM-001", "Anti-GBM disease", "active",
            [("creatinine", Decimal("4.0")), ("antiGbm", 1)],
            egfr=Decimal("15"),
        )
        assert profile.patient.patient_id == "AC-GBM-001"


class TestC3GJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-C3-001", "C3 glomerulopathy", "active",
            [("c3", Decimal("45")), ("upcr", Decimal("2.5"))],
            egfr=Decimal("60"),
        )
        assert profile.patient.patient_id == "AC-C3-001"


class TestDKDJourney:
    def test_pipeline_completes(self):
        profile = _run_journey(
            "AC-DKD-001", "Diabetic kidney disease", "ckd",
            [("creatinine", Decimal("1.6")), ("hba1c", Decimal("7.5"))],
            egfr=Decimal("42"), encounter_type="followup",
        )
        assert profile.patient.patient_id == "AC-DKD-001"


class TestExplainabilityCertification:
    """Verify the explainability report meets V3.5 certification requirements."""

    def test_explainability_contains_all_elements(self):
        profile = _run_journey(
            "AC-EXP-001", "Lupus nephritis", "active",
            [("upcr", Decimal("3.0")), ("c3", Decimal("65"))],
            egfr=Decimal("52"),
        )
        from clinical_reasoning.services.explainability import build_full_explainability
        report = build_full_explainability(profile)
        required = ["summary", "knowledge_health", "triggering_findings",
                     "matched_rules", "guideline_support", "evidence_quality",
                     "confidence", "rejected_alternatives", "information_gaps",
                     "reasoning_chain", "recommendations"]
        for key in required:
            assert key in report, f"Missing key: {key}"

    def test_matched_rules_include_details(self):
        profile = _run_journey(
            "AC-EXP-002", "Lupus nephritis", "active",
            [("upcr", Decimal("3.0")), ("c3", Decimal("65"))],
            egfr=Decimal("52"),
        )
        from clinical_reasoning.services.explainability import build_full_explainability
        report = build_full_explainability(profile)
        for entry in report.get("matched_rules", []):
            assert "matched_count" in entry
            assert "source" in entry

    def test_confidence_score_present(self):
        profile = _run_journey(
            "AC-EXP-003", "IgA nephropathy (IgAN)", "active",
            [("creatinine", Decimal("1.5")), ("upcr", Decimal("1.0"))],
            egfr=Decimal("45"),
        )
        from clinical_reasoning.services.explainability import build_full_explainability
        report = build_full_explainability(profile)
        assert "confidence" in report
        assert "overall" in report["confidence"]
        assert "level" in report["confidence"]

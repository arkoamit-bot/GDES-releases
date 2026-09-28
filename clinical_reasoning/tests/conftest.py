"""Shared fixtures for clinical_reasoning tests."""
import os
import tempfile

import pytest
from django.utils import timezone

# ---------------------------------------------------------------------------
# Fix the SQLite "init_command" incompatibility (Django 5.0 vs 5.1+ setting).
# We must patch DATABASES *before* pytest-django tries to create the test DB.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _fix_sqlite_options():
    """Remove 'init_command' from SQLite OPTIONS if present (Django 5.0 compat)."""
    from django.conf import settings
    db_opts = settings.DATABASES.get("default", {}).get("OPTIONS", {})
    if "init_command" in db_opts:
        del db_opts["init_command"]


@pytest.fixture
def patient(db):
    """Create a test patient for unit/integration tests."""
    from patients.models import Patient

    return Patient.objects.create(
        patient_id="TEST-001",
        name="Test Patient",
        hospital_id="H001",
        phone="+1234567890",
        sex="M",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="iga",
        current_phase="active",
        registration_status="active",
        enrollment_date=timezone.now().date(),
    )


@pytest.fixture
def patient_f(db):
    """Create a female test patient."""
    from patients.models import Patient

    return Patient.objects.create(
        patient_id="TEST-F01",
        name="Female Test Patient",
        hospital_id="H002",
        sex="F",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="lupus",
        current_phase="active",
        registration_status="active",
    )


@pytest.fixture
def clinical_profile(patient):
    """Get or create a ClinicalProfile for the test patient.

    The event_handlers auto-create a profile on Patient creation, so we
    use get_or_create and update it to have the desired test data.
    """
    from clinical_reasoning.models import ClinicalProfile

    profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
    profile.features_snapshot = {"egfr": 45, "proteinuria": "nephrotic", "features": ["edema", "hypertension"]}
    profile.differential = [
        {
            "disease_id": "iga",
            "disease_name": "IgA Nephropathy",
            "score": 12.5,
            "confidence": 65,
            "matched_rules_count": 4,
            "source": "KDIGO 2021",
            "evidence_grade": "1",
        },
        {
            "disease_id": "membranous",
            "disease_name": "Membranous Nephropathy",
            "score": 5.0,
            "confidence": 35,
            "matched_rules_count": 2,
            "source": "KDIGO 2021",
            "evidence_grade": "2",
        },
    ]
    profile.disease_trajectory = {
        "trend": "stable",
        "detail": "No significant change",
        "confidence": "moderate",
    }
    profile.care_pathway = {
        "stage": "active_disease",
        "stage_label": "Active Disease",
        "care_gaps": [],
        "recommendations": [
            {"type": "investigation", "priority": "high", "message": "Order biopsy"},
        ],
    }
    profile.risk_assessment = {"overall": "moderate", "factors": []}
    profile.evidence_summary = {"grade_distribution": {"1": 1, "2": 1}, "total_diseases": 2}
    profile.reasoning_chain = [
        {
            "step": "rule_evaluation",
            "finding": "Top differential: IgA Nephropathy",
            "detail": "4 matching criteria",
            "confidence": "moderate",
        }
    ]
    profile.information_gaps = [
        {"field": "biopsy", "importance": "high", "message": "No biopsy findings"},
    ]
    profile.milestones = []
    profile.version = 1
    profile.save()
    return profile


@pytest.fixture
def clinical_insight(patient):
    """Create a ClinicalInsight for the test patient."""
    from clinical_reasoning.models import ClinicalInsight

    return ClinicalInsight.objects.create(
        patient=patient,
        category=ClinicalInsight.InsightCategory.DIAGNOSTIC,
        priority=ClinicalInsight.Priority.HIGH,
        title="Leading differential: IgA Nephropathy",
        description="Score 12.5 from 4 matching criteria",
        reasoning="Evaluated against KnowledgeBaseEntry rules",
        actionable=True,
    )

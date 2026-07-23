"""End-to-end clinical scenario tests — full patient journey.

Each scenario tests the pipeline: patient registration -> clinical profile
-> care gaps -> treatment failure detection -> management plan.
"""
import datetime as dt

import pytest
from django.test import TestCase
from django.core.management import call_command

from patients.models import Patient
from labs.services.results import record_result


@pytest.mark.django_db
class TestIgAWorkup:
    """Full IgA nephropathy workup."""

    def setup_method(self):
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="SCN-IGA-1",
            name="IgA Patient",
            sex="M", dob=dt.date(1985, 3, 15),
            enrollment_date=dt.date(2025, 1, 10),
            primary_diagnosis="IgA nephropathy",
        )

    def test_care_gaps_detected_for_iga(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(self.p, {"disease_phase": "active"})
        gap_messages = [g["message"] for g in gaps]
        assert any("monitoring" in m.lower() for m in gap_messages), (
            f"Expected monitoring gaps, got: {gap_messages}"
        )

    def test_treatment_failure_egfr_decline_fires(self):
        from clinical_reasoning.services.treatment_failure import (
            detect_treatment_failure, FailurePattern, TreatmentFailureAlert,
            _evaluate_failure_pattern,
        )
        pattern = FailurePattern(
            disease_id="iga",
            failure_type="egfr_decline",
            description="eGFR decline in IgA",
            criteria={"egfr_decline_rate": 5.0, "assessment_period_months": 12},
            clinical_significance="Test",
            next_steps="Test",
            guideline_ref="KDIGO 2021 GN 4.1.5",
        )
        alert = _evaluate_failure_pattern(
            pattern,
            {"egfr_decline_rate": 8.0, "egfr_value": 42.0, "egfr_baseline": 50.0},
            treatment_duration=12.0,
        )
        assert alert is not None
        assert alert.failure_type == "egfr_decline"
        assert alert.severity in ("warning", "critical")

    def test_management_plan_has_first_line(self):
        from clinical_reasoning.services.management_plan import generate_management_plan
        plan = generate_management_plan(self.p, "iga")
        assert len(plan.first_line) > 0, "IgA plan should have first-line recommendations"
        drugs = [item["drug"] if isinstance(item, dict) else item for item in plan.first_line]
        drug_text = " ".join(drugs).lower()
        assert any(kw in drug_text for kw in ("raas", "ace", "arb", "acei")), (
            f"Expected RAAS blockade in IgA first-line, got drugs: {drugs}"
        )


@pytest.mark.django_db
class TestDiabeticNephropathy:
    """Diabetic kidney disease with eGFR decline."""

    def setup_method(self):
        call_command("seed_labs", verbosity=0)
        self.p = Patient.objects.create(
            patient_id="SCN-DKD-1",
            name="DKD Patient",
            sex="M", dob=dt.date(1960, 7, 20),
            enrollment_date=dt.date(2024, 6, 1),
            primary_diagnosis="Diabetic nephropathy",
            latest_egfr=45.0,
        )

    def test_care_gaps_include_glycemic_control(self):
        from clinical_reasoning.services.care_pathway import detect_care_gaps
        gaps = detect_care_gaps(self.p, {"disease_phase": "active"})
        messages = " ".join(g["message"] for g in gaps)
        assert "glycemic" in messages.lower() or "hba1c" in messages.lower(), (
            f"Expected glycemic control gap for DKD, got: {messages}"
        )

    def test_treatment_failure_detected(self):
        from clinical_reasoning.services.treatment_failure import (
            detect_treatment_failure,
        )
        from unittest.mock import patch
        with patch(
            "clinical_reasoning.services.treatment_failure._get_primary_disease",
            return_value="diabeticNephropathy",
        ), patch(
            "clinical_reasoning.services.treatment_failure._get_comprehensive_lab_values",
            return_value={"proteinuria_upcr": 2.0},
        ), patch(
            "clinical_reasoning.services.treatment_failure._get_treatment_duration",
            return_value=12.0,
        ), patch(
            "clinical_reasoning.services.treatment_failure._get_latest_egfr_value",
            return_value=45.0,
        ), patch(
            "clinical_reasoning.services.treatment_failure._get_previous_egfr",
            return_value=48.0,
        ):
            report = detect_treatment_failure(self.p)
        assert report is not None
        assert report.primary_disease == "diabeticNephropathy"

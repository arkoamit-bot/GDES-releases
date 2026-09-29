"""Tests for Vera Health services — production integration."""
import pytest
from unittest.mock import MagicMock, patch


class TestVeraMapper:
    def test_map_patient_basic(self):
        from clinical_evidence.services.vera_mapper import map_patient_for_vera
        patient = MagicMock()
        patient.sex = "M"
        patient.dob = None
        patient.smoking_status = "Never"
        patient.latest_egfr = 45
        patient.primary_diagnosis = "IgA Nephropathy"
        patient.biopsy_diagnosis = ""
        patient.gn_broad_group = ""
        patient.current_phase = "active"
        patient.transplant_status = "none"
        patient.diabetes_status = "none"
        patient.hypertension = True
        patient.autoimmune_disease = False
        patient.chronic_infection = False
        patient.hepatitis_status = ""
        patient.hiv_status = ""
        patient.patient_id = "T-001"
        patient.biopsies = MagicMock()
        patient.biopsies.order_by.return_value.first.return_value = None

        with patch("clinical_evidence.services.vera_mapper._get_baseline_height", return_value=None), \
             patch("clinical_evidence.services.vera_mapper._get_latest_weight", return_value=None), \
             patch("clinical_evidence.services.vera_mapper._map_labs", return_value={}), \
             patch("clinical_evidence.services.vera_mapper._map_vitals", return_value={}), \
             patch("clinical_evidence.services.vera_mapper._map_medications", return_value=[]), \
             patch("clinical_evidence.services.vera_mapper._map_comorbidities", return_value={"hypertension": True}), \
             patch("clinical_evidence.services.vera_mapper._map_pathology", return_value={}):
            data = map_patient_for_vera(patient, None)

        assert "demographics" in data
        assert "kidney_disease" in data
        assert data["demographics"]["sex"] == "M"
        assert data["kidney_disease"]["egfr"] == 45
        assert data["kidney_disease"]["ckd_stage"] == 3

    def test_egfr_to_ckd_stage(self):
        from clinical_evidence.services.vera_mapper import _egfr_to_ckd_stage
        assert _egfr_to_ckd_stage(120) == 1
        assert _egfr_to_ckd_stage(70) == 2
        assert _egfr_to_ckd_stage(50) == 3
        assert _egfr_to_ckd_stage(35) == 4
        assert _egfr_to_ckd_stage(15) == 5


class TestVeraClient:
    def test_no_provider_raises_error(self):
        from clinical_evidence.services.vera_client import VeraClient, VeraClientError
        with patch("clinical_evidence.services.orchestrator.get_vera_reviewer", return_value=None):
            client = VeraClient()
            assert not client.is_production

            patient_data = {
                "demographics": {"age": 50, "sex": "M"},
                "kidney_disease": {
                    "primary_diagnosis": "IgA Nephropathy",
                    "egfr": 45,
                    "ckd_stage": 3,
                    "risk_assessment": {"risk_category": "moderate"},
                },
                "laboratory_data": {},
                "vital_signs": {},
                "current_medications": [],
                "comorbidities": {},
                "pathology": {},
            }
            with pytest.raises(VeraClientError, match="Unable to contact Vera Health"):
                client.analyze(patient_data)

    def test_with_mock_provider(self):
        from clinical_evidence.services.vera_client import VeraClient
        from clinical_evidence.providers.base import AIReviewResult

        mock_provider = MagicMock()
        mock_provider.health_check.return_value = {"available": True, "latency_ms": 50, "error": None}
        mock_provider.review_clinical_question.return_value = AIReviewResult(
            summary="Vera recommends ACE inhibitor therapy for IgA Nephropathy.",
            key_findings=["Diagnosis: IgA Nephropathy", "CKD Stage 3"],
            confidence_score=88.0,
            recommendation_alignment="High Agreement",
            structured_data={
                "diagnosis": "IgA Nephropathy",
                "diagnosis_confidence": 90,
                "disease_severity": "moderate",
                "risk_category": "moderate",
                "ckd_stage": 3,
                "prognosis": "Fair",
                "treatment_rationale": "Based on KDIGO 2024 guidelines for IgAN management.",
                "medications": [
                    {"drug": "Losartan", "recommended_dose": "100 mg daily", "monitoring": ["K+", "Cr"]}
                ],
                "monitoring": [
                    {"parameter": "eGFR", "interval": "3 months", "target": ">45", "action_threshold": "<30"}
                ],
                "follow_up": {"next_visit": "1 month"},
                "safety_checks": [],
                "guideline_references": [{"source": "KDIGO", "version": "2024", "title": "Glomerular Diseases", "recommendation": "ACEi/ARB", "evidence_level": "1A"}],
                "confidence": {"overall": 88, "diagnosis": 90, "treatment": 85},
                "key_findings": ["Diagnosis confirmed", "CKD Stage 3"],
                "supporting_evidence": ["KDIGO 2024 Glomerular Disease Guidelines"],
                "clinical_notes": ["Patient-specific dosing applied"],
            },
            raw_response="{}",
            provider_type="mock",
        )

        with patch("clinical_evidence.services.orchestrator.get_vera_reviewer", return_value=mock_provider):
            client = VeraClient()
            assert client.is_production

            patient_data = {
                "demographics": {"age": 50, "sex": "M", "weight_kg": 75},
                "kidney_disease": {
                    "primary_diagnosis": "IgA Nephropathy",
                    "egfr": 45,
                    "ckd_stage": 3,
                    "risk_assessment": {"risk_category": "moderate"},
                },
                "laboratory_data": {},
                "vital_signs": {},
                "current_medications": [],
                "comorbidities": {},
                "pathology": {},
            }
            rec = client.analyze(patient_data)
            assert rec.diagnosis == "IgA Nephropathy"
            assert len(rec.medications) == 1
            assert rec.medications[0]["drug"] == "Losartan"
            assert rec.overall_confidence == 88
            assert rec.is_production
            assert "mock" in rec.verification_engine.lower()
            assert len(rec.key_findings) == 2
            assert len(rec.supporting_evidence) == 1

    def test_health_check_no_provider(self):
        from clinical_evidence.services.vera_client import VeraClient
        with patch("clinical_evidence.services.orchestrator.get_vera_reviewer", return_value=None):
            client = VeraClient()
            result = client.health_check()
            assert not result["available"]
            assert "not configured" in result["error"].lower() or "no vera" in result["error"].lower()

    def test_build_patient_summary(self):
        from clinical_evidence.services.vera_client import _build_patient_summary
        data = {
            "demographics": {"age": 50, "sex": "M", "weight_kg": 75},
            "kidney_disease": {"primary_diagnosis": "IgA Nephropathy", "egfr": 45, "ckd_stage": 3},
            "current_medications": [{"drug": "Losartan", "dose": "50mg"}],
            "comorbidities": {"diabetes": True, "hypertension": True},
        }
        summary = _build_patient_summary(data)
        assert "IgA Nephropathy" in summary
        assert "50" in summary
        assert "Losartan" in summary
        assert "diabetes" in summary

    def test_recommendation_to_dict(self):
        from clinical_evidence.services.vera_client import VeraRecommendation
        rec = VeraRecommendation(
            diagnosis="IgA Nephropathy",
            diagnosis_confidence=90,
            medications=[{"drug": "Losartan"}],
            clinical_summary="Test summary",
        )
        d = rec.to_dict()
        assert d["diagnosis"] == "IgA Nephropathy"
        assert len(d["medications"]) == 1
        assert d["clinical_summary"] == "Test summary"


class TestVeraComparison:
    def test_comparison_with_structured_data(self):
        from clinical_evidence.services.vera_comparison import compare_recommendations
        from clinical_evidence.services.vera_client import VeraRecommendation
        from dataclasses import dataclass

        @dataclass
        class MockPlan:
            disease_name: str = "IgA Nephropathy"
            first_line: list = None
            second_line: list = None
            rescue_therapy: list = None
            monitoring: list = None

            def __post_init__(self):
                if self.first_line is None:
                    self.first_line = [
                        {"drug": "Losartan", "dose": "50 mg daily"}
                    ]
                if self.second_line is None:
                    self.second_line = []
                if self.rescue_therapy is None:
                    self.rescue_therapy = []
                if self.monitoring is None:
                    self.monitoring = [
                        {"parameter": "Serum Creatinine/eGFR"},
                    ]

        vera_rec = VeraRecommendation(
            diagnosis="IgA Nephropathy",
            medications=[
                {"drug": "Losartan", "recommended_dose": "50 mg daily"},
                {"drug": "SGLT2 Inhibitor (Dapagliflozin)", "recommended_dose": "10 mg daily"},
            ],
            monitoring=[
                {"parameter": "Serum Creatinine/eGFR", "interval": "Every 3 months"},
                {"parameter": "Blood Pressure", "interval": "Every visit"},
            ],
        )

        result = compare_recommendations(MockPlan(), vera_rec, "IgA Nephropathy")
        assert "overall_score" in result
        assert result["overall_score"] is not None
        assert result["vera_has_structured_data"] is True

    def test_comparison_without_structured_data(self):
        from clinical_evidence.services.vera_comparison import compare_recommendations
        from clinical_evidence.services.vera_client import VeraRecommendation
        from dataclasses import dataclass

        @dataclass
        class MockPlan:
            disease_name: str = "IgA Nephropathy"
            first_line: list = None
            second_line: list = None
            rescue_therapy: list = None
            monitoring: list = None

            def __post_init__(self):
                if self.first_line is None:
                    self.first_line = [{"drug": "Losartan", "dose": "50 mg daily"}]
                if self.second_line is None:
                    self.second_line = []
                if self.rescue_therapy is None:
                    self.rescue_therapy = []
                if self.monitoring is None:
                    self.monitoring = [{"parameter": "eGFR"}]

        vera_rec = VeraRecommendation(
            diagnosis="IgA Nephropathy",
            clinical_summary="Vera recommends ACE inhibitor therapy.",
        )

        result = compare_recommendations(MockPlan(), vera_rec, "IgA Nephropathy")
        assert result["vera_has_structured_data"] is False
        assert result["vera_has_clinical_summary"] is True
        assert result["overall_score"] is not None
        assert result["agreement_level"] == "High Agreement"

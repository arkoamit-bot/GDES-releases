"""Unit tests for ClinicalIntelligenceService — complexity scoring and pipeline."""

from unittest.mock import MagicMock, patch

from clinical_reasoning.services.clinical_intelligence import (
    ClinicalIntelligenceService,
    SIMPLE_DISEASES,
    MODERATE_DISEASES,
    COMPLEX_DISEASES,
    RARE_DISEASES,
)


# ---------------------------------------------------------------------------
# _score_case_complexity
# ---------------------------------------------------------------------------

class TestScoreCaseComplexity:
    def _make_profile(self, differential=None, features_snapshot=None):
        profile = MagicMock()
        profile.differential = differential or []
        profile.features_snapshot = features_snapshot or {}
        return profile

    def test_simple_disease_returns_low_score(self):
        profile = self._make_profile(
            differential=[{"disease_id": "diabetic_nephropathy", "confidence": 80, "evidence_grade": "1"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["level"] == "simple"
        assert result["score"] < 1.0

    def test_moderate_disease_returns_moderate_score(self):
        profile = self._make_profile(
            differential=[{"disease_id": "iga_nephropathy", "confidence": 70, "evidence_grade": "2"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["level"] == "moderate"
        assert 1.0 <= result["score"] < 2.0

    def test_complex_disease_returns_high_score(self):
        profile = self._make_profile(
            differential=[{"disease_id": "anca_associated_vasculitis", "confidence": 60, "evidence_grade": "OP"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["level"] == "complex"
        assert 2.0 <= result["score"] < 3.0

    def test_rare_disease_returns_highest_score(self):
        profile = self._make_profile(
            differential=[{"disease_id": "fabry_disease", "confidence": 50, "evidence_grade": "NG"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["level"] == "rare"
        assert result["score"] >= 3.0

    def test_unknown_disease_gets_moderate_penalty(self):
        profile = self._make_profile(
            differential=[{"disease_id": "rare_unknown_disease", "confidence": 60, "evidence_grade": "2"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["score"] >= 1.5

    def test_no_guideline_evidence_adds_penalty(self):
        profile = self._make_profile(
            differential=[{"disease_id": "iga_nephropathy", "confidence": 70, "evidence_grade": "NG"}],
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["score"] > 1.0

    def test_biopsy_data_adds_penalty(self):
        profile = self._make_profile(
            differential=[{"disease_id": "iga_nephropathy", "confidence": 70, "evidence_grade": "2"}],
            features_snapshot={"biopsy": ["mesangial proliferation"]},
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert "Biopsy data present" in result["reasons"]

    def test_severe_ckd_adds_penalty(self):
        profile = self._make_profile(
            differential=[{"disease_id": "iga_nephropathy", "confidence": 70, "evidence_grade": "2"}],
            features_snapshot={"latest_egfr": 20},
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert "Severe CKD (eGFR < 30)" in result["reasons"]

    def test_autoantibody_positive_adds_penalty(self):
        profile = self._make_profile(
            differential=[{"disease_id": "iga_nephropathy", "confidence": 70, "evidence_grade": "2"}],
            features_snapshot={"labs": ["anca", "creatinine"]},
        )
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert "Autoantibody-positive disease" in result["reasons"]

    def test_wide_differential_adds_penalty(self):
        differential = [
            {"disease_id": "iga_nephropathy", "confidence": 40, "evidence_grade": "2"},
            {"disease_id": "fsgs", "confidence": 30, "evidence_grade": "OP"},
            {"disease_id": "membranous_nephropathy", "confidence": 25, "evidence_grade": "OP"},
        ]
        profile = self._make_profile(differential=differential)
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert any("Wide differential" in r for r in result["reasons"])

    def test_empty_differential_returns_simple(self):
        profile = self._make_profile(differential=[])
        result = ClinicalIntelligenceService._score_case_complexity(profile)
        assert result["level"] == "simple"

    def test_all_simple_diseases_are_simple(self):
        for disease_id in SIMPLE_DISEASES:
            profile = self._make_profile(
                differential=[{"disease_id": disease_id, "confidence": 80, "evidence_grade": "1"}],
            )
            result = ClinicalIntelligenceService._score_case_complexity(profile)
            assert result["level"] == "simple", f"{disease_id} should be simple"

    def test_all_moderate_diseases_are_moderate_or_higher(self):
        for disease_id in MODERATE_DISEASES:
            profile = self._make_profile(
                differential=[{"disease_id": disease_id, "confidence": 70, "evidence_grade": "2"}],
            )
            result = ClinicalIntelligenceService._score_case_complexity(profile)
            assert result["level"] in ("moderate", "complex", "rare"), f"{disease_id} should be moderate+"


# ---------------------------------------------------------------------------
# _summarize_features
# ---------------------------------------------------------------------------

class TestSummarizeFeatures:
    def test_returns_default_when_none(self):
        result = ClinicalIntelligenceService._summarize_features(None)
        assert "No clinical features" in result

    def test_returns_default_when_empty(self):
        result = ClinicalIntelligenceService._summarize_features({})
        assert "No clinical features" in result

    def test_includes_egfr(self):
        result = ClinicalIntelligenceService._summarize_features({"latest_egfr": 45})
        assert "eGFR 45" in result

    def test_includes_proteinuria(self):
        result = ClinicalIntelligenceService._summarize_features({"proteinuria": "3.5g"})
        assert "Proteinuria 3.5g" in result

    def test_skips_proteinuria_none(self):
        result = ClinicalIntelligenceService._summarize_features({"proteinuria": "none"})
        assert "Proteinuria" not in result

    def test_includes_biopsy(self):
        result = ClinicalIntelligenceService._summarize_features({"biopsy": ["FSGS", "Minimal change"]})
        assert "Biopsy: FSGS" in result

    def test_includes_labs(self):
        result = ClinicalIntelligenceService._summarize_features({"labs": ["anca", "creatinine"]})
        assert "Lab: anca" in result

    def test_includes_disease_phase(self):
        result = ClinicalIntelligenceService._summarize_features({"disease_phase": "progressive"})
        assert "Phase: progressive" in result

    def test_caps_at_six_features(self):
        features = {
            "latest_egfr": 30,
            "proteinuria": "2g",
            "biopsy": ["A", "B", "C"],
            "labs": ["D", "E", "F"],
            "disease_phase": "chronic",
        }
        result = ClinicalIntelligenceService._summarize_features(features)
        parts = [p.strip() for p in result.split(";")]
        assert len(parts) <= 6


# ---------------------------------------------------------------------------
# _build_evidence_queries (module-level helper)
# ---------------------------------------------------------------------------

class TestBuildEvidenceQueries:
    def test_returns_at_least_one_query(self):
        from clinical_reasoning.services.clinical_intelligence import _build_evidence_queries
        queries = _build_evidence_queries("IgA Nephropathy", "iga_nephropathy", {})
        assert len(queries) >= 1

    def test_includes_biopsy_context(self):
        from clinical_reasoning.services.clinical_intelligence import _build_evidence_queries
        queries = _build_evidence_queries(
            "IgA Nephropathy", "iga_nephropathy",
            {"biopsy": ["mesangial proliferation"]},
        )
        assert any("mesangial" in q.lower() for q in queries)

    def test_includes_autoantibody_context(self):
        from clinical_reasoning.services.clinical_intelligence import _build_evidence_queries
        queries = _build_evidence_queries(
            "ANCA vasculitis", "anca_associated_vasculitis",
            {"labs": ["anca"]},
        )
        assert any("anca" in q.lower() for q in queries)

    def test_capped_at_three_queries(self):
        from clinical_reasoning.services.clinical_intelligence import _build_evidence_queries
        queries = _build_evidence_queries(
            "Some Disease", "some_disease",
            {"biopsy": ["Finding"], "labs": ["test"]},
        )
        assert len(queries) <= 3


# ---------------------------------------------------------------------------
# _evidence_source_names (module-level helper)
# ---------------------------------------------------------------------------

class TestEvidenceSourceNames:
    def test_empty_returns_default(self):
        from clinical_reasoning.services.clinical_intelligence import _evidence_source_names
        result = _evidence_source_names([])
        assert result == "published databases"

    def test_pubmed_detected(self):
        from clinical_reasoning.services.clinical_intelligence import _evidence_source_names
        result = _evidence_source_names([{"source_type": "pubmed"}])
        assert "PubMed" in result

    def test_multiple_sources(self):
        from clinical_reasoning.services.clinical_intelligence import _evidence_source_names
        result = _evidence_source_names([
            {"source_type": "pubmed"},
            {"source_type": "openalex"},
        ])
        assert "PubMed" in result
        assert "OpenAlex" in result

    def test_vera_detected(self):
        from clinical_reasoning.services.clinical_intelligence import _evidence_source_names
        result = _evidence_source_names([{"source_type": "vera_web"}])
        assert "Vera Health" in result

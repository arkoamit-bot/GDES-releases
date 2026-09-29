from django.test import TestCase

from clinical_evidence.constants import (
    AlertType,
    CacheTTL,
    CitationFormat,
    ConfidenceScore,
    ConflictSeverity,
    EvidenceLevel,
    ProviderStatus,
    ProviderType,
    StudyDesign,
    ValidationOutcome,
    VALIDATION_SOURCES,
)


class ConstantsTest(TestCase):
    def test_provider_type_choices(self):
        choices = dict(ProviderType.choices)
        self.assertIn("pubmed", choices)
        self.assertIn("vera", choices)
        self.assertIn("openai", choices)

    def test_validation_outcome_choices(self):
        choices = dict(ValidationOutcome.choices)
        self.assertIn("verified", choices)
        self.assertIn("conflicting", choices)

    def test_conflict_severity_choices(self):
        choices = dict(ConflictSeverity.choices)
        self.assertIn("low", choices)
        self.assertIn("critical", choices)

    def test_confidence_score_choices(self):
        choices = dict(ConfidenceScore.choices)
        self.assertIn(95, choices)
        self.assertIn(5, choices)

    def test_cache_ttl_values(self):
        self.assertEqual(CacheTTL.SEARCH, 3600)
        self.assertEqual(CacheTTL.SUMMARY, 86400)
        self.assertEqual(CacheTTL.AI_RESPONSE, 43200)
        self.assertEqual(CacheTTL.GUIDELINE, 604800)

    def test_evidence_level_choices(self):
        choices = dict(EvidenceLevel.choices)
        self.assertIn("1a", choices)
        self.assertIn("5", choices)

    def test_study_design_choices(self):
        choices = dict(StudyDesign.choices)
        self.assertIn("rct", choices)
        self.assertIn("meta_analysis", choices)
        self.assertIn("narrative_review", choices)

    def test_validation_sources(self):
        source_keys = [s[0] for s in VALIDATION_SOURCES]
        self.assertIn("KDIGO", source_keys)
        self.assertIn("ERA", source_keys)

    def test_alert_type_choices(self):
        choices = dict(AlertType.choices)
        self.assertIn("new_rct", choices)
        self.assertIn("guideline_update", choices)
        self.assertIn("knowledge_gap", choices)

    def test_provider_status_choices(self):
        choices = dict(ProviderStatus.choices)
        self.assertIn("active", choices)
        self.assertIn("degraded", choices)
        self.assertIn("disabled", choices)

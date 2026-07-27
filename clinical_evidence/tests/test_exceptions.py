from django.test import TestCase

from clinical_evidence.exceptions import (
    CacheError,
    CitationError,
    ClinicalEvidenceError,
    ConfigurationError,
    ContradictionError,
    GovernanceError,
    OrchestrationError,
    ProviderAuthError,
    ProviderError,
    ProviderQuotaError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ValidationError,
)


class ExceptionsTest(TestCase):
    def test_base_exception(self):
        exc = ClinicalEvidenceError("test")
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), "test")

    def test_provider_error(self):
        exc = ProviderError("API unavailable")
        self.assertIn("API unavailable", str(exc))

    def test_provider_auth_error(self):
        exc = ProviderAuthError("Auth failed")
        self.assertIn("Auth failed", str(exc))

    def test_provider_quota_error(self):
        exc = ProviderQuotaError("Quota exceeded")
        self.assertIn("Quota exceeded", str(exc))

    def test_provider_timeout_error(self):
        exc = ProviderTimeoutError("Timeout")
        self.assertIn("Timeout", str(exc))

    def test_provider_unavailable_error(self):
        exc = ProviderUnavailableError("Unavailable")
        self.assertIn("Unavailable", str(exc))

    def test_validation_error(self):
        exc = ValidationError("Validation failed")
        self.assertIn("Validation failed", str(exc))

    def test_contradiction_error(self):
        exc = ContradictionError("Contradiction detection failed")
        self.assertIn("Contradiction detection failed", str(exc))

    def test_cache_error(self):
        exc = CacheError("Cache operation failed")
        self.assertIn("Cache operation failed", str(exc))

    def test_governance_error(self):
        exc = GovernanceError("Governance recording failed")
        self.assertIn("Governance recording failed", str(exc))

    def test_citation_error(self):
        exc = CitationError("Citation generation failed")
        self.assertIn("Citation generation failed", str(exc))

    def test_orchestration_error(self):
        exc = OrchestrationError("Orchestration failed")
        self.assertIn("Orchestration failed", str(exc))

    def test_configuration_error(self):
        exc = ConfigurationError("Missing API key")
        self.assertIn("Missing API key", str(exc))

    def test_inheritance(self):
        self.assertTrue(issubclass(ProviderAuthError, ProviderError))
        self.assertTrue(issubclass(ProviderQuotaError, ProviderError))
        self.assertTrue(issubclass(ProviderTimeoutError, ProviderError))
        self.assertTrue(issubclass(ProviderUnavailableError, ProviderError))
        self.assertTrue(issubclass(ProviderError, ClinicalEvidenceError))
        self.assertTrue(issubclass(ValidationError, ClinicalEvidenceError))
        self.assertTrue(issubclass(ContradictionError, ClinicalEvidenceError))
        self.assertTrue(issubclass(CacheError, ClinicalEvidenceError))
        self.assertTrue(issubclass(GovernanceError, ClinicalEvidenceError))
        self.assertTrue(issubclass(CitationError, ClinicalEvidenceError))
        self.assertTrue(issubclass(OrchestrationError, ClinicalEvidenceError))
        self.assertTrue(issubclass(ConfigurationError, ClinicalEvidenceError))

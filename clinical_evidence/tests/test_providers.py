"""Tests for provider base class and known adapters."""

from django.test import TestCase

from clinical_evidence.providers.base import (
    AIReviewResult,
    BaseEvidenceProvider,
    EvidenceItem,
    ProviderCapabilities,
)
from clinical_evidence.providers.pubmed import PubMedProvider


class EvidenceItemTest(TestCase):
    def test_defaults(self):
        item = EvidenceItem(source_type="pubmed", title="Test Study")
        self.assertEqual(item.title, "Test Study")
        self.assertEqual(item.source_type, "pubmed")
        self.assertEqual(item.authors, "")
        self.assertEqual(item.pmid, "")

    def test_with_all_fields(self):
        item = EvidenceItem(
            source_type="pubmed",
            title="RCT of Drug X",
            authors="Smith J",
            pmid="12345678",
            doi="10.1000/test",
            relevance_score=0.95,
        )
        self.assertEqual(item.pmid, "12345678")
        self.assertEqual(item.relevance_score, 0.95)


class AIReviewResultTest(TestCase):
    def test_review_defaults(self):
        review = AIReviewResult(summary="Effective", recommendation_alignment="aligns")
        self.assertEqual(review.summary, "Effective")
        self.assertEqual(review.recommendation_alignment, "aligns")
        self.assertIsNone(review.confidence_score)
        self.assertEqual(review.key_findings, [])
        self.assertEqual(review.supporting_evidence, [])
        self.assertEqual(review.contradictory_evidence, [])


class ProviderCapabilitiesTest(TestCase):
    def test_capabilities_default(self):
        caps = ProviderCapabilities()
        self.assertTrue(caps.supports_search)
        self.assertTrue(caps.supports_retrieve)
        self.assertFalse(caps.supports_ai_summary)

    def test_requires_auth_requires_search(self):
        with self.assertRaises(ValueError):
            ProviderCapabilities(requires_authentication=True, supports_search=False)


class PubMedProviderTest(TestCase):
    def test_provider_type(self):
        provider = PubMedProvider(config={"api_key": ""})
        self.assertEqual(provider.provider_type, "pubmed")

    def test_health_check_no_key(self):
        provider = PubMedProvider(config={"api_key": ""})
        result = provider.health_check()
        self.assertIsInstance(result, dict)
        self.assertIn("available", result)


class BaseProviderContract(TestCase):
    def test_abstract_methods(self):
        expected = {"search", "retrieve", "normalize", "authenticate", "health_check"}
        methods = {m for m in dir(BaseEvidenceProvider) if not m.startswith("_")}
        abstract = {
            "search", "retrieve", "normalize",
            "authenticate", "health_check", "version", "capabilities",
        }
        self.assertTrue(
            abstract.issubset(methods),
            f"Missing abstract methods: {abstract - methods}",
        )

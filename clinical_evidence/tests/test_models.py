from django.test import TestCase

from clinical_evidence.models import (
    EvidenceQuery,
    ProviderConfiguration,
)


class EvidenceQueryTest(TestCase):
    def test_query_id_default(self):
        q = EvidenceQuery.objects.create(query_text="test query")
        self.assertTrue(q.query_id.startswith("Q"))
        self.assertEqual(len(q.query_id), 13)

    def test_query_str(self):
        q = EvidenceQuery.objects.create(query_text="ACE inhibitors in CKD")
        self.assertIn("ACE inhibitors", str(q))


class ProviderConfigurationTest(TestCase):
    def test_provider_creation(self):
        p = ProviderConfiguration.objects.create(
            provider_type="pubmed",
            is_enabled=True,
            priority=10,
        )
        self.assertIn("PubMed", str(p))
        self.assertTrue(p.is_enabled)

    def test_provider_defaults(self):
        p = ProviderConfiguration.objects.create(provider_type="vera")
        self.assertEqual(p.max_retries, 3)
        self.assertEqual(p.timeout_seconds, 30)
        self.assertEqual(p.rate_limit_per_minute, 30)

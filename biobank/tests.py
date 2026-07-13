import datetime as dt
import unittest

from django.apps import apps

# The biobank app is disabled (GN Master Protocol v2 removed biobanking). Skip
# its tests cleanly until it is re-enabled via a future amendment.
if not apps.is_installed("biobank"):
    raise unittest.SkipTest("biobank app disabled (protocol v2)")

from django.core.exceptions import ValidationError
from django.test import TestCase

from audit.models import Consent
from audit.services.consent import grant_consent, withdraw_consent
from patients.models import Patient

from .models import Sample
from .services.storage import BiobankConsentRequired, store_sample


class BiobankConsentGateTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="BK1", name="x", sex="M")

    def test_store_blocked_without_consent(self):
        with self.assertRaises(BiobankConsentRequired):
            store_sample(self.p, Sample.Type.SERUM, dt.date(2026, 1, 1))

    def test_store_allowed_with_consent(self):
        grant_consent(self.p, Consent.Type.BIOBANK, "BIO-v1",
                      consent_date=dt.date(2026, 1, 1))
        s = store_sample(self.p, Sample.Type.SERUM, dt.date(2026, 1, 1),
                         volume_ml=2, aliquots=4, storage_location="-80C/A1")
        self.assertEqual(s.status, Sample.Status.STORED)
        self.assertEqual(Sample.objects.count(), 1)

    def test_clean_enforces_gate_after_withdrawal(self):
        grant_consent(self.p, Consent.Type.BIOBANK, "BIO-v1",
                      consent_date=dt.date(2026, 1, 1))
        store_sample(self.p, Sample.Type.PLASMA, dt.date(2026, 1, 1))
        withdraw_consent(self.p, Consent.Type.BIOBANK,
                         withdrawn_date=dt.date(2026, 6, 1))
        # New samples are now refused (model-level clean()).
        with self.assertRaises(ValidationError):
            Sample(patient=self.p, sample_type=Sample.Type.DNA,
                   collection_date=dt.date(2026, 7, 1)).full_clean()

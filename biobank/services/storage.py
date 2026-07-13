"""Programmatic sample storage with the consent gate enforced."""
from django.core.exceptions import ValidationError

from audit.models import Consent
from audit.services.consent import has_consent

from biobank.models import Sample


class BiobankConsentRequired(Exception):
    pass


def store_sample(patient, sample_type, collection_date, **fields):
    if not has_consent(patient, Consent.Type.BIOBANK):
        raise BiobankConsentRequired(
            f"Biobank consent not on file for {patient.patient_id}.")
    sample = Sample(patient=patient, sample_type=sample_type,
                    collection_date=collection_date, **fields)
    sample.full_clean()
    sample.save()
    return sample

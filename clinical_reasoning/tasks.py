"""Celery tasks for async clinical reasoning event processing."""
from __future__ import annotations

import logging

from bgddr.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_reason_about_patient(self, patient_id: str) -> dict | None:
    """Recompute clinical profile for a patient in a background task."""
    from patients.models import Patient
    from .services.engine import reason_about_patient
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        try:
            patient = Patient.objects.get(pk=int(patient_id))
        except (ValueError, TypeError, Patient.DoesNotExist):
            logger.warning("Patient %s not found for async reasoning", patient_id)
            return None
    try:
        profile = reason_about_patient(patient)
        return {"patient_id": patient.patient_id, "version": profile.version}
    except Exception as exc:
        logger.exception("Async reasoning failed for patient %s", patient_id)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_compute_outcome(self, patient_id: str) -> dict | None:
    """Recompute outcome for a patient in a background task."""
    from patients.models import Patient
    from analytics.services.outcomes import compute_patient_outcome
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        try:
            patient = Patient.objects.get(pk=int(patient_id))
        except (ValueError, TypeError, Patient.DoesNotExist):
            logger.warning("Patient %s not found for async outcome", patient_id)
            return None
    try:
        compute_patient_outcome(patient)
        return {"patient_id": patient.patient_id}
    except Exception as exc:
        logger.exception("Async outcome computation failed for patient %s", patient_id)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_reason_and_outcome(self, patient_id: str) -> dict | None:
    """Recompute both profile and outcome in sequence."""
    result = async_reason_about_patient(patient_id)
    async_compute_outcome(patient_id)
    return result

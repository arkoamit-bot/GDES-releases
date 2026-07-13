"""Event handlers that connect the event bus to clinical reasoning operations."""
import logging

from events.dispatcher import subscribe
from events import event_types as et

logger = logging.getLogger(__name__)


def _resolve_patient(patient_id):
    """Resolve a patient by patient_id string, falling back to pk."""
    from patients.models import Patient
    try:
        return Patient.objects.get(patient_id=patient_id)
    except (Patient.DoesNotExist, ValueError):
        try:
            return Patient.objects.get(pk=int(patient_id))
        except (ValueError, TypeError, Patient.DoesNotExist):
            return None


def _on_patient_event(event_type, source_model, source_pk, payload, **kwargs):
    """Recompute clinical profile when patient data changes."""
    from .services.engine import reason_about_patient

    patient_id = payload.get("patient_id") or source_pk
    if not patient_id:
        return
    patient = _resolve_patient(patient_id)
    if patient is None:
        logger.warning("Patient %s not found for event %s", patient_id, event_type)
        return
    try:
        reason_about_patient(patient)
        logger.info("Recomputed profile for patient %s after %s", patient.patient_id, event_type)
    except Exception:
        logger.exception("Failed to recompute profile for patient %s", patient_id)


def _on_lab_event(event_type, source_model, source_pk, payload, **kwargs):
    """Recompute outcome + profile when lab results change."""
    from analytics.services.outcomes import compute_patient_outcome

    patient_id = payload.get("patient_id")
    if not patient_id:
        return
    patient = _resolve_patient(patient_id)
    if patient is not None:
        try:
            compute_patient_outcome(patient)
            logger.info("Recomputed outcome for patient %s after lab event", patient.patient_id)
        except Exception:
            logger.exception("Failed to recompute outcome for patient %s", patient_id)
    _on_patient_event(event_type, source_model, source_pk, payload)


def _on_clinical_event(event_type, source_model, source_pk, payload, **kwargs):
    """Recompute outcome + profile on clinical events (remission, ESKD, death)."""
    from analytics.services.outcomes import compute_patient_outcome

    patient_id = payload.get("patient_id")
    if not patient_id:
        return
    patient = _resolve_patient(patient_id)
    if patient is not None:
        try:
            compute_patient_outcome(patient)
            logger.info("Recomputed outcome for patient %s after clinical event", patient.patient_id)
        except Exception:
            logger.exception("Failed to recompute outcome for patient %s", patient_id)
    _on_patient_event(event_type, source_model, source_pk, payload)


def connect_handlers():
    """Register all clinical reasoning event handlers with async dispatch support."""
    from events.dispatcher import mark_async

    subscribe(et.PATIENT_REGISTERED, _on_patient_event)
    subscribe(et.PATIENT_UPDATED, _on_patient_event)
    subscribe(et.ENCOUNTER_CREATED, _on_patient_event)
    subscribe(et.ENCOUNTER_UPDATED, _on_patient_event)
    subscribe(et.LAB_RESULT_CREATED, _on_lab_event)
    subscribe(et.LAB_RESULT_UPDATED, _on_lab_event)
    subscribe(et.BIOPSY_CREATED, _on_patient_event)
    subscribe(et.CLINICAL_EVENT_CREATED, _on_clinical_event)
    subscribe(et.CLINICAL_ASSESSMENT_CREATED, _on_clinical_event)
    subscribe(et.CLINICAL_ASSESSMENT_UPDATED, _on_clinical_event)
    subscribe(et.TREATMENT_EXPOSURE_CREATED, _on_patient_event)
    subscribe(et.TREATMENT_EXPOSURE_UPDATED, _on_patient_event)

    # Mark high-volume event types for async dispatch via Celery
    mark_async(et.LAB_RESULT_CREATED)
    mark_async(et.LAB_RESULT_UPDATED)
    mark_async(et.ENCOUNTER_CREATED)
    mark_async(et.ENCOUNTER_UPDATED)
    mark_async(et.CLINICAL_ASSESSMENT_CREATED)
    mark_async(et.CLINICAL_ASSESSMENT_UPDATED)

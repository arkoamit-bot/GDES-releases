"""Connect the domain-event bus to automatic study eligibility screening.

Registered from StudiesConfig.ready(). Re-screens a patient whenever the data
that drives eligibility changes: registration, patient updates (diagnosis /
diabetes status), lab results (eGFR), and clinical assessments.
"""
import logging

from events import event_types as et
from events.dispatcher import subscribe

logger = logging.getLogger(__name__)


def _resolve_patient(patient_id):
    from patients.models import Patient
    try:
        return Patient.objects.get(patient_id=patient_id)
    except (Patient.DoesNotExist, ValueError):
        try:
            return Patient.objects.get(pk=int(patient_id))
        except (ValueError, TypeError, Patient.DoesNotExist):
            return None


def _on_patient_data_event(event_type, source_model, source_pk, payload, **kwargs):
    from studies.services.auto_screen import auto_screen_patient

    patient_id = payload.get("patient_id") or source_pk
    if not patient_id:
        return
    patient = _resolve_patient(patient_id)
    if patient is None:
        return
    try:
        summary = auto_screen_patient(patient)
        if summary["created"] or summary["updated"]:
            logger.info(
                "Auto-screened %s after %s: %s", patient.patient_id, event_type, summary
            )
    except Exception:
        logger.exception("Auto-screen failed for patient %s", patient_id)


def connect_handlers():
    """Subscribe eligibility screening to the events that affect it."""
    subscribe(et.PATIENT_REGISTERED, _on_patient_data_event)
    subscribe(et.PATIENT_UPDATED, _on_patient_data_event)
    subscribe(et.LAB_RESULT_CREATED, _on_patient_data_event)
    subscribe(et.LAB_RESULT_UPDATED, _on_patient_data_event)
    subscribe(et.CLINICAL_ASSESSMENT_CREATED, _on_patient_data_event)
    subscribe(et.CLINICAL_ASSESSMENT_UPDATED, _on_patient_data_event)
    subscribe(et.BIOPSY_CREATED, _on_patient_data_event)

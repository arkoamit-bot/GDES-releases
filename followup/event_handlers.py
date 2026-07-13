"""Event handlers that connect the event bus to the follow-up engine.

Subscribes to data-change events that trigger follow-up plan recomputation:
- Patient registered/updated
- Encounter created/updated
- Lab result created/updated
- Biopsy created
- Clinical assessment created/updated
- Treatment exposure created/updated (started/changed/stopped)
- Outcome recorded/recomputed
- Clinical reasoning updated
- Clinical event created
"""

import logging

from events.dispatcher import subscribe
from events import event_types as et

logger = logging.getLogger(__name__)


def _on_data_event(event_type, source_model, source_pk, payload, **kwargs):
    """Recompute follow-up plan when any patient data changes."""
    patient_id = payload.get("patient_id") if payload else None
    if not patient_id:
        logger.debug("No patient_id in event %s — skipping", event_type)
        return

    from patients.models import Patient
    try:
        patient = Patient.objects.get(pk=int(patient_id))
    except (Patient.DoesNotExist, ValueError, TypeError):
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except (Patient.DoesNotExist, ValueError):
            logger.warning("Patient %s not found for event %s", patient_id, event_type)
            return

    if patient.registration_status != "registered":
        return

    from followup.services.engine import compute_followup_plan
    try:
        compute_followup_plan(patient)
        logger.info(
            "Follow-up plan recomputed for %s after %s",
            patient.patient_id, event_type,
        )
    except Exception:
        logger.exception(
            "Failed to recompute follow-up plan for %s after %s",
            patient.patient_id, event_type,
        )


def connect_handlers():
    """Register all follow-up engine event handlers."""
    DATA_EVENTS = [
        et.PATIENT_REGISTERED,
        et.PATIENT_UPDATED,
        et.ENCOUNTER_CREATED,
        et.ENCOUNTER_UPDATED,
        et.LAB_RESULT_CREATED,
        et.LAB_RESULT_UPDATED,
        et.BIOPSY_CREATED,
        et.CLINICAL_ASSESSMENT_CREATED,
        et.CLINICAL_ASSESSMENT_UPDATED,
        et.TREATMENT_EXPOSURE_CREATED,
        et.TREATMENT_EXPOSURE_UPDATED,
        et.CLINICAL_EVENT_CREATED,
        et.OUTCOME_RECORDED,
        et.OUTCOME_RECOMPUTED,
        et.CLINICAL_PROFILE_UPDATED,
        et.CARE_PATHWAY_UPDATED,
        et.REASONING_COMPLETED,
    ]
    for event_type in DATA_EVENTS:
        subscribe(event_type, _on_data_event)
        logger.debug("Subscribed follow-up handler to %s", event_type)

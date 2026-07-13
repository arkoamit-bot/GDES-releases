"""Bridge Django model signals → domain events.

Auto-wires signals from key models to domain event dispatch.
"""
from django.db.models.signals import post_save

from . import event_types as et
from .dispatcher import dispatch

# Map: model_label -> (event_type_on_create, event_type_on_update)
_MODEL_EVENT_MAP = {
    "patients.Patient": (et.PATIENT_REGISTERED, et.PATIENT_UPDATED),
    "encounters.ClinicalEncounter": (et.ENCOUNTER_CREATED, et.ENCOUNTER_UPDATED),
    "labs.LabResult": (et.LAB_RESULT_CREATED, et.LAB_RESULT_UPDATED),
    "pathology.Biopsy": (et.BIOPSY_CREATED, None),
    "encounters.ClinicalEvent": (et.CLINICAL_EVENT_CREATED, None),
    "clinical.ClinicalAssessment": (et.CLINICAL_ASSESSMENT_CREATED, et.CLINICAL_ASSESSMENT_UPDATED),
    "prescriptions.Prescription": (et.PRESCRIPTION_CREATED, None),
    "treatments.TreatmentExposure": (et.TREATMENT_EXPOSURE_CREATED, et.TREATMENT_EXPOSURE_UPDATED),
}


def _model_post_save(sender, instance, created, **kwargs):
    label = f"{sender._meta.app_label}.{sender.__name__}"
    mapping = _MODEL_EVENT_MAP.get(label)
    if mapping is None:
        return
    event_type = mapping[0] if created else mapping[1]
    if event_type is None:
        return

    payload = {"pk": str(instance.pk), "repr": str(instance)[:200]}
    if hasattr(instance, "patient_id"):
        payload["patient_id"] = str(instance.patient_id)
    elif hasattr(instance, "patient"):
        payload["patient_id"] = str(instance.patient.pk)
    elif hasattr(instance, "encounter") and hasattr(instance.encounter, "patient_id"):
        payload["patient_id"] = str(instance.encounter.patient_id)

    dispatch(
        event_type,
        source_model=label,
        source_pk=str(instance.pk),
        payload=payload,
    )


def connect_all():
    """Connect signal handlers for all registered models.
    Called from apps.py ready().
    """
    from django.apps import apps

    for model_label in _MODEL_EVENT_MAP:
        try:
            model = apps.get_model(model_label)
            post_save.connect(
                _model_post_save,
                sender=model,
                dispatch_uid=f"events:{model_label}",
            )
        except LookupError:
            pass

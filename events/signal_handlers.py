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
    "encounters.ClinicalEvent": (et.CLINICAL_EVENT_CREATED, None),
    "clinical.ClinicalAssessment": (et.CLINICAL_ASSESSMENT_CREATED, et.CLINICAL_ASSESSMENT_UPDATED),
    "prescriptions.Prescription": (et.PRESCRIPTION_CREATED, None),
    "treatments.TreatmentExposure": (et.TREATMENT_EXPOSURE_CREATED, et.TREATMENT_EXPOSURE_UPDATED),
}


# A biopsy is an aggregate saved in several steps (biopsy, diagnosis, score
# panels, reviews, report, findings). Its Biopsy post_save used to fire before
# the diagnosis existed, and later steps fired nothing. Every step now asks for
# one PATHOLOGY_REPORT_CHANGED per biopsy, sent after the transaction commits.
_PATHOLOGY_PARTS = {
    "pathology.Biopsy": lambda i: i,
    "pathology.GNDiagnosis": lambda i: i.biopsy,
    "pathology.IgANScore": lambda i: i.biopsy,
    "pathology.LupusPathology": lambda i: i.biopsy,
    "pathology.FSGSPathology": lambda i: i.biopsy,
    "pathology.MembranousPathology": lambda i: i.biopsy,
    "pathology.PathologyReview": lambda i: i.biopsy,
    "pathology.PathologyReport": lambda i: i.biopsy,
}


def _pathology_post_save(sender, instance, created=False, **kwargs):
    from .dispatcher import dispatch_on_commit
    label = f"{sender._meta.app_label}.{sender.__name__}"
    biopsy = _PATHOLOGY_PARTS[label](instance)
    payload = {"patient_id": str(biopsy.patient_id), "biopsy_id": biopsy.pk}
    if label == "pathology.Biopsy" and created:
        dispatch_on_commit(et.BIOPSY_CREATED, key=f"biopsy:{biopsy.pk}",
                           source_model=label, source_pk=str(biopsy.pk),
                           payload=dict(payload, pk=str(biopsy.pk)))
    dispatch_on_commit(et.PATHOLOGY_REPORT_CHANGED, key=f"biopsy:{biopsy.pk}",
                       source_model="pathology.Biopsy", source_pk=str(biopsy.pk),
                       payload=payload)


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
    for model_label in _PATHOLOGY_PARTS:
        try:
            model = apps.get_model(model_label)
        except LookupError:
            continue
        post_save.connect(_pathology_post_save, sender=model,
                          dispatch_uid=f"events:pathology:{model_label}")

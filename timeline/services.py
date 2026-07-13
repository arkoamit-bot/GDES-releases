from datetime import datetime
from django.utils import timezone
from .models import TimelineEvent


def record_event(patient, domain, event_type, event_date, summary, details=None, source_id="", source_url=""):
    return TimelineEvent.objects.create(
        patient=patient,
        domain=domain,
        event_type=event_type,
        event_date=event_date,
        summary=summary,
        details=details or {},
        source_id=str(source_id) if source_id else "",
        source_url=source_url,
    )


def get_patient_timeline(patient, domain=None, limit=100):
    qs = TimelineEvent.objects.filter(patient=patient)
    if domain:
        qs = qs.filter(domain=domain)
    return qs[:limit]


def rebuild_patient_timeline(patient):
    from encounters.models import ClinicalEncounter
    from clinical.models import ClinicalAssessment
    from pathology.models import Biopsy

    TimelineEvent.objects.filter(patient=patient).delete()

    events = []

    # Patient registration
    events.append(TimelineEvent(
        patient=patient, domain="patient", event_type="patient.registered",
        event_date=patient.created_at,
        summary=f"Patient {patient.name} registered (ID: {patient.patient_id})",
        details={"patient_id": patient.patient_id},
        source_id=str(patient.id),
    ))

    # Encounters
    for enc in ClinicalEncounter.objects.filter(patient=patient):
        events.append(TimelineEvent(
            patient=patient, domain="encounter", event_type="encounter.created",
            event_date=timezone.make_aware(datetime.combine(enc.encounter_date, datetime.min.time())),
            summary=f"Encounter on {enc.encounter_date} ({enc.get_encounter_type_display()})",
            details={"encounter_type": enc.encounter_type, "encounter_id": str(enc.id)},
            source_id=str(enc.id),
        ))

    # Biopsies
    for bx in Biopsy.objects.filter(patient=patient):
        events.append(TimelineEvent(
            patient=patient, domain="biopsy", event_type="biopsy.performed",
            event_date=timezone.make_aware(datetime.combine(bx.biopsy_date, datetime.min.time())),
            summary=f"Kidney biopsy performed ({bx.total_glomeruli} glomeruli)",
            details={"total_glomeruli": bx.total_glomeruli, "biopsy_id": str(bx.id)},
            source_id=str(bx.id),
        ))

    return TimelineEvent.objects.bulk_create(events)

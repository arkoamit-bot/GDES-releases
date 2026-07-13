"""Core follow-up rules engine (Workstream 1).

Generates a per-patient follow-up plan deterministically from:
- Disease-specific protocol (Workstream 2)
- Risk assessment (Workstream 5)
- Last encounter date and outcome data

Triggered automatically by any relevant data change (via signals/events).
"""

import logging
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from followup.protocols import get_protocol_for_patient
from followup.services.risk import assess_risk_category

logger = logging.getLogger(__name__)


def compute_followup_plan(patient):
    """Compute or recompute a patient's follow-up plan.

    Returns dict with plan details. Creates/updates FollowUpTask rows.
    """
    from followup.protocols.base import FollowUpProtocol
    from followup.services.task_generator import generate_tasks

    protocol_cls = get_protocol_for_patient(patient)
    if protocol_cls is None:
        raise RuntimeError(f"No follow-up protocol found for patient {patient.patient_id}")
    protocol = protocol_cls()

    risk = assess_risk_category(patient, protocol)
    interval_days = protocol.get_visit_interval(patient, risk["category"])

    last_encounter = patient.encounters.order_by("-encounter_date").first()
    today = timezone.now().date()

    if last_encounter and last_encounter.next_due_date:
        next_visit = last_encounter.next_due_date
    elif last_encounter:
        next_visit = last_encounter.encounter_date + timedelta(days=interval_days)
    else:
        enrollment = getattr(patient, "enrollment_date", None) or today
        next_visit = enrollment + timedelta(days=interval_days)

    plan = {
        "patient_id": patient.pk,
        "protocol": protocol_cls.disease_id,
        "protocol_name": protocol_cls.disease_name,
        "risk_category": risk["category"],
        "risk_score": risk["score"],
        "visit_interval_days": interval_days,
        "next_visit_date": next_visit.isoformat() if isinstance(next_visit, date) else str(next_visit),
        "last_computed": timezone.now().isoformat(),
    }

    with transaction.atomic():
        existing = patient.followup_tasks.filter(status__in=["pending", "overdue"])
        cancelled = existing.update(status="cancelled")
        if cancelled:
            logger.info("Cancelled %d stale tasks for %s", cancelled, patient.patient_id)

        generate_tasks(patient, protocol, risk, next_visit)
        logger.info(
            "Follow-up plan for %s: protocol=%s risk=%s interval=%dd next_visit=%s",
            patient.patient_id, protocol_cls.disease_id, risk["category"],
            interval_days, next_visit,
        )

    # Dispatch follow-up event.
    from events.dispatcher import dispatch
    from events import event_types as et
    dispatch(
        et.FOLLOW_UP_PLAN_UPDATED,
        source_model="followup.FollowUpPlan",
        source_pk=str(patient.pk),
        payload=plan,
    )

    return plan


def compute_all_plans():
    """Recompute follow-up plans for all registered patients."""
    from patients.models import Patient
    patients = Patient.objects.filter(registration_status="registered")
    results = []
    for patient in patients:
        try:
            plan = compute_followup_plan(patient)
            results.append((patient.patient_id, "ok"))
        except Exception as e:
            logger.exception("Failed to compute plan for %s", patient.patient_id)
            results.append((patient.patient_id, str(e)))
    return results


def connect_signals():
    """Connect Django signal handlers that trigger plan recomputation."""
    from django.db.models.signals import post_save

    from events.signal_handlers import _MODEL_EVENT_MAP

    TRIGGER_MODELS = [
        "patients.Patient",
        "encounters.ClinicalEncounter",
        "labs.LabResult",
        "pathology.Biopsy",
        "treatments.TreatmentExposure",
        "clinical.ClinicalAssessment",
        "clinical_reasoning.ClinicalProfile",
    ]
    for label in TRIGGER_MODELS:
        if label in _MODEL_EVENT_MAP:
            continue
        try:
            from django.apps import apps
            app_label, model_name = label.split(".")
            model = apps.get_model(app_label, model_name)
            uid = f"followup:post_save:{label}"
            post_save.connect(_on_data_change, sender=model, dispatch_uid=uid)
        except LookupError:
            pass


def _on_data_change(sender, instance, **kwargs):
    """Recompute follow-up plan when patient data changes."""
    from patients.models import Patient

    if isinstance(instance, Patient):
        patient = instance
    elif hasattr(instance, "patient_id"):
        try:
            patient = Patient.objects.get(pk=instance.patient_id)
        except Patient.DoesNotExist:
            return
    elif hasattr(instance, "patient"):
        patient = instance.patient
    else:
        return

    if patient.registration_status != "registered":
        return

    try:
        compute_followup_plan(patient)
    except Exception:
        logger.exception("Signal-triggered plan recomputation failed for %s", patient.patient_id)

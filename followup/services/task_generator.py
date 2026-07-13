"""Structured follow-up task generation (Workstream 6).

Creates FollowUpTask rows for:
- Visit Due (from protocol schedule)
- Laboratory Due (required labs / interval labs)
- Drug Monitoring Due (drug-specific monitoring)
- Vaccination Due
- Biopsy Review Due
- Safety Review Due
- Research Visit Due
"""

import logging
from datetime import date, timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_tasks(patient, protocol, risk, next_visit_date):
    """Generate all follow-up tasks for a patient."""
    from followup.models import FollowUpTask, TaskPriority

    today = timezone.now().date()
    risk_cat = risk["category"]
    should_create_urgent = risk_cat in ("very_high", "high")

    _create_visit_task(patient, protocol, next_visit_date, today, should_create_urgent)
    _create_lab_tasks(patient, protocol, today, should_create_urgent)
    _create_drug_monitoring_tasks(patient, protocol, today, risk_cat)
    _create_vaccination_tasks(patient, today)
    _create_biopsy_review_task(patient, today)


def _get_base_priority(risk_cat):
    from followup.models import TaskPriority
    if risk_cat in ("very_high",):
        return TaskPriority.EMERGENT
    elif risk_cat in ("high",):
        return TaskPriority.URGENT
    return TaskPriority.ROUTINE


def _create_visit_task(patient, protocol, next_visit_date, today, urgent):
    from followup.models import FollowUpTask, TaskPriority, TaskType

    priority = TaskPriority.URGENT if urgent else TaskPriority.ROUTINE
    overdue_date = next_visit_date + timedelta(days=14)

    FollowUpTask.objects.create(
        patient=patient,
        task_type=TaskType.VISIT_DUE,
        priority=priority,
        reason=f"{protocol.disease_name} follow-up visit due",
        clinical_reason=f"Protocol: {protocol.disease_name} interval = {protocol.base_visit_interval_days}d",
        due_date=next_visit_date,
        overdue_date=overdue_date,
        protocol_label=f"{protocol.disease_id} visit",
    )
    logger.debug(
        "Visit task for %s: due %s priority=%s",
        patient.patient_id, next_visit_date, priority,
    )


def _create_lab_tasks(patient, protocol, today, urgent):
    from followup.models import FollowUpTask, TaskPriority, TaskType

    days_since_index = _days_since_index(patient)
    labs_due = protocol.get_labs_for_interval(days_since_index)
    seen_lab_codes = set()

    for lab_req in labs_due:
        if lab_req.code in seen_lab_codes:
            continue
        seen_lab_codes.add(lab_req.code)
        last_result = patient.lab_results.filter(
            test__code=lab_req.code).order_by("-result_date").first()
        due_date = today
        if last_result and lab_req.interval_days:
            due_date = max(
                due_date,
                last_result.result_date + timedelta(days=lab_req.interval_days) if last_result.result_date else due_date
            )

        priority = _get_priority_for_lab(lab_req, urgent)
        reason = lab_req.clinical_reason or f"Routine {lab_req.name} monitoring"
        FollowUpTask.objects.create(
            patient=patient,
            task_type=TaskType.LAB_DUE,
            priority=priority,
            reason=f"{lab_req.name} due",
            clinical_reason=reason,
            due_date=due_date,
            overdue_date=due_date + timedelta(days=7),
            protocol_label=f"{protocol.disease_id} lab",
        )


def _create_drug_monitoring_tasks(patient, protocol, today, risk_cat):
    from followup.models import FollowUpTask, TaskPriority, TaskType

    ongoing_exposures = patient.exposures.filter(ongoing=True).select_related("drug")
    seen_classes = set()

    for exposure in ongoing_exposures:
        dc = exposure.drug.drug_class
        if dc in seen_classes:
            continue
        seen_classes.add(dc)
        dm = protocol.get_drug_monitoring(dc)
        if dm is None:
            continue

        due_date = today
        if dm.interval_days:
            last_result = patient.lab_results.filter(
                test__code__in=dm.lab_codes,
            ).order_by("-result_date").first()
            if last_result and last_result.result_date:
                due_date = max(
                    today,
                    last_result.result_date + timedelta(days=dm.interval_days),
                )

        priority = _get_base_priority(risk_cat)
        reason = dm.clinical_reason or f"{exposure.drug.generic_name} monitoring"
        FollowUpTask.objects.create(
            patient=patient,
            task_type=TaskType.DRUG_MONITORING_DUE,
            priority=priority,
            reason=f"{exposure.drug.generic_name} labs due",
            clinical_reason=reason,
            due_date=due_date,
            overdue_date=due_date + timedelta(days=7),
            protocol_label=f"{protocol.disease_id} drug_monitoring",
        )


def _create_vaccination_tasks(patient, today):
    """Flag vaccination needs for patients on immunosuppression."""
    from followup.models import FollowUpTask, TaskPriority, TaskType

    ongoing = patient.exposures.filter(ongoing=True).select_related("drug")
    on_immunosuppression = any(
        e.drug.drug_class in (
            "steroid", "mmf", "cyclophosphamide",
            "rituximab", "cni", "azathioprine",
        )
        for e in ongoing
    )
    if not on_immunosuppression:
        return

    FollowUpTask.objects.create(
        patient=patient,
        task_type=TaskType.VACCINATION_DUE,
        priority=TaskPriority.ROUTINE,
        reason="Immunization review due",
        clinical_reason="On immunosuppression: review influenza, pneumococcal, COVID-19, HBV status",
        due_date=today + timedelta(days=30),
        overdue_date=today + timedelta(days=60),
        protocol_label="immunosuppression vaccination",
    )


def _create_biopsy_review_task(patient, today):
    """Create a biopsy review task if a biopsy needs clinical follow-up."""
    from followup.models import FollowUpTask, TaskPriority, TaskType

    pending_biopsy = patient.biopsies.filter(
        review_status__in=("preliminary", "pending", "awaiting_review"),
    ).first()
    if not pending_biopsy:
        return

    due_date = pending_biopsy.biopsy_date + timedelta(days=14)
    if due_date < today:
        due_date = today

    FollowUpTask.objects.create(
        patient=patient,
        task_type=TaskType.BIOPSY_REVIEW_DUE,
        priority=TaskPriority.URGENT,
        reason=f"Biopsy review: {pending_biopsy.biopsy_date}",
        clinical_reason=f"Pending biopsy result review ({pending_biopsy.get_indication_display()})",
        due_date=due_date,
        overdue_date=due_date + timedelta(days=7),
        protocol_label="biopsy review",
    )


def _days_since_index(patient):
    outcome = getattr(patient, "outcome", None)
    if outcome and outcome.index_date:
        today = timezone.now().date()
        return (today - outcome.index_date).days
    return 0


def _get_priority_for_lab(lab_req, urgent):
    from followup.models import TaskPriority
    if lab_req.priority == "high" or urgent:
        return TaskPriority.URGENT
    return TaskPriority.ROUTINE

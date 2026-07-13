"""Automated Follow-up Schedule Generator — Phase 11 of GDES transformation.

DEPRECATED: Use followup.services.engine + followup/protocols/ instead.

This module uses hardcoded intervals and generates duplicate tasks.
The followup/ app provides disease-specific protocol classes with richer
monitoring rules, drug-specific lab schedules, and signal-based triggering.

Kept for backward compatibility during pilot transition.
Will be removed post-pilot.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Any

from django.db import transaction

logger = logging.getLogger(__name__)


# Standard follow-up intervals by risk category and disease phase
FOLLOW_UP_INTERVALS: dict[str, dict[str, dict[str, int]]] = {
    "very_high": {
        "active": {"initial": 14, "routine": 14},
        "relapse": {"initial": 14, "routine": 14},
        "remission": {"initial": 28, "routine": 42},
        "ckd": {"initial": 28, "routine": 42},
    },
    "high": {
        "active": {"initial": 14, "routine": 28},
        "relapse": {"initial": 14, "routine": 28},
        "remission": {"initial": 42, "routine": 84},
        "ckd": {"initial": 42, "routine": 84},
    },
    "moderate": {
        "active": {"initial": 28, "routine": 42},
        "relapse": {"initial": 28, "routine": 42},
        "remission": {"initial": 84, "routine": 84},
        "ckd": {"initial": 84, "routine": 120},
    },
    "low": {
        "active": {"initial": 42, "routine": 84},
        "relapse": {"initial": 28, "routine": 56},
        "remission": {"initial": 84, "routine": 180},
        "ckd": {"initial": 120, "routine": 180},
    },
}

# Lab monitoring schedules by treatment class
TREATMENT_LAB_SCHEDULES: dict[str, list[dict[str, Any]]] = {
    "immunosuppression_induction": [
        {"test_code": "creatinine", "interval_days": 14, "label": "Renal function"},
        {"test_code": "egfr_calc", "interval_days": 14, "label": "eGFR"},
        {"test_code": "upcr", "interval_days": 28, "label": "Proteinuria"},
        {"test_code": "cbc", "interval_days": 14, "label": "CBC for immunosuppression safety"},
        {"test_code": "lft", "interval_days": 28, "label": "Liver function"},
    ],
    "rituximab": [
        {"test_code": "cbc", "interval_days": 14, "label": "CBC (lymphocyte count)"},
        {"test_code": "immunoglobulins", "interval_days": 90, "label": "Immunoglobulin levels"},
        {"test_code": "cd19_cd20", "interval_days": 90, "label": "B-cell count (if available)"},
    ],
    "mycophenolate": [
        {"test_code": "cbc", "interval_days": 14, "label": "CBC (WBC monitoring)"},
        {"test_code": "lft", "interval_days": 28, "label": "Liver function"},
    ],
    "calcineurin_inhibitor": [
        {"test_code": "drug_level", "interval_days": 14, "label": "Trough level"},
        {"test_code": "creatinine", "interval_days": 14, "label": "Renal function"},
        {"test_code": "potassium", "interval_days": 14, "label": "Electrolytes"},
    ],
    "corticosteroid_high_dose": [
        {"test_code": "glucose", "interval_days": 7, "label": "Blood glucose (steroid diabetes)"},
        {"test_code": "blood_pressure", "interval_days": 14, "label": "Blood pressure"},
    ],
    "cyclophosphamide": [
        {"test_code": "cbc", "interval_days": 10, "label": "CBC (neutrophil count)"},
        {"test_code": "urinalysis", "interval_days": 7, "label": "Hemorrhagic cystitis screening"},
    ],
}


@transaction.atomic
def generate_follow_up_schedule(
    patient,
    risk_category: str = "moderate",
    disease_phase: str = "active",
    treatment_phase: str = "induction",
    disease_id: str | None = None,
    start_date: dt.date | None = None,
    num_visits: int = 6,
) -> list[dict]:
    """Generate a personalized follow-up schedule for a patient.

    Creates ScheduledVisit records and FollowUpTask records.

    Args:
        patient: Patient model instance
        risk_category: "low", "moderate", "high", "very_high"
        disease_phase: "active", "relapse", "remission", "ckd"
        treatment_phase: "induction", "maintenance", "remission"
        disease_id: Optional disease identifier for protocol-specific scheduling
        start_date: Override start date (default: today + initial interval)
        num_visits: Number of visits to schedule (default: 6)

    Returns:
        List of created visit dicts
    """
    from scheduling.models import ScheduledVisit
    from followup.models import FollowUpTask, TaskType, TaskPriority, TaskStatus

    intervals = FOLLOW_UP_INTERVALS.get(
        risk_category, FOLLOW_UP_INTERVALS["moderate"]
    ).get(disease_phase, FOLLOW_UP_INTERVALS["moderate"]["active"])

    initial_interval = intervals["initial"]
    routine_interval = intervals["routine"]

    if start_date is None:
        start_date = dt.date.today()

    visits = []
    current_date = start_date + dt.timedelta(days=initial_interval)

    for i in range(num_visits):
        window_start = current_date - dt.timedelta(days=7)
        window_end = current_date + dt.timedelta(days=7)
        label = _generate_visit_label(i, treatment_phase)

        # Determine visit type
        if i == 0:
            kind = ScheduledVisit.Kind.EARLY_SAFETY
        else:
            kind = ScheduledVisit.Kind.ROUTINE

        # Create (or reuse) the ScheduledVisit. get_or_create keyed on the
        # unique (patient, label) makes the generator idempotent: re-running it
        # (e.g. on every patient-page load) neither crashes on the unique
        # constraint nor duplicates visits/tasks. An existing visit is left
        # untouched, so a clinician's changes / completion are preserved.
        visit, _ = ScheduledVisit.objects.get_or_create(
            patient=patient,
            label=label,
            defaults={
                "kind": kind,
                "target_date": current_date,
                "window_start": window_start,
                "window_end": window_end,
                "status": ScheduledVisit.Status.SCHEDULED,
            },
        )
        # Use the PERSISTED dates downstream so the schedule is fixed on first
        # generation and does not drift when the page is reopened on a later day.
        visit_date = visit.target_date

        # Create (or reuse) the matching visit-due follow-up task.
        task, _ = FollowUpTask.objects.get_or_create(
            patient=patient,
            task_type=TaskType.VISIT_DUE,
            protocol_label=label,
            defaults={
                "priority": _priority_from_risk(risk_category),
                "reason": f"{treatment_phase.title()} phase follow-up for {disease_id or 'GN'}",
                "clinical_reason": _clinical_reason(i, risk_category, disease_phase),
                "due_date": visit_date,
                "overdue_date": visit.window_end,
            },
        )

        visits.append({
            "visit_id": visit.id,
            "task_id": task.id,
            "label": label,
            "target_date": str(visit_date),
            "window": f"{visit.window_start} to {visit.window_end}",
            "kind": visit.kind,
        })

        # Schedule lab tasks around the (persisted) visit date
        _schedule_lab_tasks(patient, visit_date, treatment_phase, risk_category)

        # Advance to next visit based on the persisted date (stable across runs)
        if i < 2 and treatment_phase == "induction":
            # More frequent visits during induction
            current_date = visit_date + dt.timedelta(days=initial_interval)
        else:
            current_date = visit_date + dt.timedelta(days=routine_interval)

    return visits


def _generate_visit_label(index: int, treatment_phase: str) -> str:
    """Generate a descriptive label for the visit."""
    labels = {
        "induction": [
            "Week 2 safety", "Week 4 safety", "Month 2 review",
            "Month 3 review", "Month 4 review", "Month 6 review",
        ],
        "maintenance": [
            "Month 1 review", "Month 3 review", "Month 6 review",
            "Month 9 review", "Month 12 review", "Month 15 review",
        ],
        "remission": [
            "Month 3 review", "Month 6 review", "Month 9 review",
            "Month 12 review", "Month 18 review", "Month 24 review",
        ],
    }
    phase_labels = labels.get(treatment_phase, labels["maintenance"])
    if index < len(phase_labels):
        return phase_labels[index]
    return f"Visit {index + 1}"


def _priority_from_risk(risk_category: str) -> str:
    """Map risk category to task priority."""
    from followup.models import TaskPriority
    mapping = {
        "very_high": TaskPriority.URGENT,
        "high": TaskPriority.URGENT,
        "moderate": TaskPriority.ROUTINE,
        "low": TaskPriority.ROUTINE,
    }
    return mapping.get(risk_category, TaskPriority.ROUTINE)


def _clinical_reason(visit_index: int, risk_category: str, disease_phase: str) -> str:
    """Generate clinical reasoning for the visit."""
    if visit_index == 0:
        return f"First follow-up after {disease_phase} phase — safety check and early response assessment"
    if visit_index < 3 and disease_phase in ("active", "relapse"):
        return f"Active disease monitoring — assess treatment response and adjust therapy"
    if disease_phase in ("remission",):
        return "Remission monitoring — confirm sustained response"
    return "Routine follow-up — assess disease stability"


def _schedule_lab_tasks(
    patient,
    visit_date: dt.date,
    treatment_phase: str,
    risk_category: str,
) -> None:
    """Schedule lab monitoring tasks around a visit date."""
    from followup.models import FollowUpTask, TaskType as _TaskType

    schedule_key = "immunosuppression_induction" if treatment_phase == "induction" else "immunosuppression_induction"
    labs = TREATMENT_LAB_SCHEDULES.get(schedule_key, [])

    for lab in labs:
        lab_date = visit_date - dt.timedelta(days=min(lab["interval_days"], 3))
        if lab_date < dt.date.today():
            continue

        # Idempotent: keyed on (patient, task_type, protocol_label, due_date) so
        # re-running the generator does not accumulate duplicate lab tasks.
        FollowUpTask.objects.get_or_create(
            patient=patient,
            task_type=_TaskType.LAB_DUE,
            protocol_label=lab["label"],
            due_date=lab_date,
            defaults={
                "priority": _priority_from_risk(risk_category),
                "reason": lab["label"],
                "clinical_reason": f"Required before visit on {visit_date}: {lab['label']}",
                "overdue_date": visit_date,
            },
        )


@transaction.atomic
def auto_schedule_on_phase_change(patient, old_phase: str, new_phase: str) -> list[dict]:
    """Automatically reschedule when disease phase changes.

    Cancels existing future visits and creates new ones based on the new phase.
    """
    from scheduling.models import ScheduledVisit
    from followup.models import FollowUpTask, TaskType, TaskStatus

    today = dt.date.today()

    # Cancel existing future scheduled visits
    cancelled = ScheduledVisit.objects.filter(
        patient=patient,
        status=ScheduledVisit.Status.SCHEDULED,
        target_date__gte=today,
    ).update(status=ScheduledVisit.Status.CANCELLED)

    # Cancel related pending tasks
    FollowUpTask.objects.filter(
        patient=patient,
        status=TaskStatus.PENDING,
        due_date__gte=today,
    ).update(status=TaskStatus.CANCELLED)

    # Determine risk category
    from followup.services.risk import assess_risk_category
    risk = assess_risk_category(patient)
    risk_category = risk["category"]

    # Determine treatment phase
    treatment_phase = "induction" if new_phase in ("active", "relapse") else "maintenance"

    # Generate new schedule
    return generate_follow_up_schedule(
        patient=patient,
        risk_category=risk_category,
        disease_phase=new_phase,
        treatment_phase=treatment_phase,
        start_date=today,
    )


@transaction.atomic
def generate_monitoring_tasks(
    patient,
    monitoring_params: list[dict],
    visit_date: dt.date,
) -> list[dict]:
    """Generate monitoring tasks from a management plan's monitoring parameters.

    Creates FollowUpTask records for each monitoring parameter.
    """
    from followup.models import FollowUpTask, TaskType as _TaskType, TaskPriority as _TaskPriority

    tasks = []
    for param in monitoring_params:
        interval_str = param.get("interval", "monthly")
        interval_days = _parse_interval_to_days(interval_str)
        task_date = visit_date + dt.timedelta(days=interval_days)

        if task_date < dt.date.today():
            continue

        task = FollowUpTask.objects.create(
            patient=patient,
            task_type=_TaskType.DRUG_MONITORING_DUE,
            priority=_TaskPriority.URGENT,
            reason=f"Monitor: {param.get('parameter', 'unknown')}",
            clinical_reason=f"Target: {param.get('target', 'N/A')}. Action threshold: {param.get('action_threshold', 'N/A')}",
            due_date=task_date,
            overdue_date=task_date + dt.timedelta(days=7),
            protocol_label=f"Monitoring: {param.get('parameter', '')}",
        )
        tasks.append({
            "task_id": task.id,
            "parameter": param.get("parameter", ""),
            "due_date": str(task_date),
        })

    return tasks


def _parse_interval_to_days(interval_str: str) -> int:
    """Parse an interval string to approximate days."""
    s = interval_str.lower()
    if "week" in s:
        return 7
    if "2 week" in s or "biweekly" in s:
        return 14
    if "month" in s and "2" in s:
        return 60
    if "month" in s:
        return 30
    if "3 month" in s or "quarterly" in s:
        return 90
    if "6 month" in s:
        return 180
    if "day" in s and "2" in s:
        return 2
    if "day" in s:
        return 1
    return 30  # Default: monthly

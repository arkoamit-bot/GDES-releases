"""Escalation rules for overdue follow-up tasks (Workstream 7).

Escalation chain:
1. Task overdue → generate warning
2. Warning ignored → notify responsible clinician
3. Clinician unresponsive → notify coordinator
4. Coordinator unresponsive → escalate to department dashboard

No patient should silently disappear from follow-up.
"""

import logging
from datetime import date, timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def run_escalation():
    """Check all overdue tasks and escalate as needed.

    Called periodically (e.g. every 6 hours via Celery beat).
    """
    from followup.models import FollowUpTask, TaskStatus, EscalationLevel
    now = timezone.now()
    today = now.date()

    overdue_tasks = FollowUpTask.objects.filter(
        status=TaskStatus.PENDING,
        due_date__lt=today,
    ).select_related("patient")

    escalated_count = 0
    for task in overdue_tasks:
        task.status = TaskStatus.OVERDUE
        days_overdue = (today - task.due_date).days

        new_level = _determine_escalation_level(days_overdue, task.escalation_level)
        if new_level > task.escalation_level:
            task.escalation_level = new_level
            task.escalated_at = now
            _perform_escalation_action(task, new_level, days_overdue)
            escalated_count += 1

        task.save()

    if escalated_count:
        logger.info("Escalated %d overdue tasks", escalated_count)
    return escalated_count


def _determine_escalation_level(days_overdue, current_level):
    """Determine escalation level based on how overdue a task is.

    Level 1: 7 days overdue → Warning
    Level 2: 14 days overdue → Notify clinician
    Level 3: 30 days overdue → Notify coordinator
    Level 4: 60 days overdue → Department dashboard

    Returns the highest applicable level.
    """
    thresholds = [
        (7, 1),
        (14, 2),
        (30, 3),
        (60, 4),
    ]
    max_level = current_level
    for threshold, level in thresholds:
        if days_overdue >= threshold and level > max_level:
            max_level = level
    return max_level


def _perform_escalation_action(task, level, days_overdue):
    """Execute the escalation action for the given level."""
    from events.dispatcher import dispatch
    from events import event_types as et

    payload = {
        "task_id": task.pk,
        "patient_id": task.patient.patient_id,
        "task_type": task.task_type,
        "reason": task.reason,
        "due_date": task.due_date.isoformat(),
        "days_overdue": days_overdue,
        "escalation_level": level,
    }

    dispatch(
        et.FOLLOW_UP_TASK_OVERDUE,
        source_model="followup.FollowUpTask",
        source_pk=str(task.pk),
        payload=payload,
    )

    if level >= 2:
        logger.warning(
            "ESCALATION level %d: %s task %s for %s (%d days overdue)",
            level, task.task_type, task.pk, task.patient.patient_id, days_overdue,
        )


def get_overdue_summary():
    """Return summary counts of overdue tasks by escalation level."""
    from followup.models import FollowUpTask, TaskStatus
    from django.db.models import Count

    return list(
        FollowUpTask.objects
        .filter(status=TaskStatus.OVERDUE)
        .values("escalation_level")
        .annotate(count=Count("id"))
        .order_by("escalation_level")
    )

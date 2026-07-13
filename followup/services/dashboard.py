"""Clinician worklist dashboard (Workstream 8).

Generates daily worklist views:
- Patients due today
- Patients overdue
- High-risk patients
- Drug monitoring due
- Laboratory monitoring due
- Missed appointments
- Recent relapse
- Recent AKI
- Rapid eGFR decline
"""

import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def get_daily_worklist(as_of=None):
    """Generate the full clinician worklist for a given date."""
    from patients.models import Patient
    as_of = as_of or timezone.now().date()
    week_ago = as_of - timedelta(days=7)
    month_ago = as_of - timedelta(days=30)
    quarter_ago = as_of - timedelta(days=90)

    return {
        "as_of": as_of.isoformat(),
        "patients_due_today": _patients_due_today(as_of),
        "patients_overdue": _patients_overdue(as_of),
        "high_risk_patients": _high_risk_patients(as_of),
        "drug_monitoring_due": _drug_monitoring_due(as_of),
        "lab_monitoring_due": _lab_monitoring_due(as_of),
        "missed_appointments": _missed_appointments(as_of),
        "recent_relapses": _recent_events(as_of, quarter_ago, "relapse"),
        "recent_aki": _recent_aki(as_of, month_ago),
        "rapid_egfr_decline": _rapid_egfr_decline(as_of, quarter_ago),
        "summary": {},
    }


def get_daily_summary(as_of=None):
    """Return a lightweight count summary for the dashboard header."""
    as_of = as_of or timezone.now().date()
    data = get_daily_worklist(as_of)
    data["summary"] = {
        "due_today": len(data["patients_due_today"]),
        "overdue": len(data["patients_overdue"]),
        "high_risk": len(data["high_risk_patients"]),
        "missed": len(data["missed_appointments"]),
        "drug_monitoring": len(data["drug_monitoring_due"]),
        "lab_monitoring": len(data["lab_monitoring_due"]),
    }
    return data


def _patients_due_today(as_of):
    """Patients with scheduled visits today."""
    from scheduling.models import ScheduledVisit
    visits = ScheduledVisit.objects.filter(
        status="scheduled",
        window_start__lte=as_of,
        window_end__gte=as_of,
    ).select_related("patient")
    return [
        {
            "patient_id": v.patient.patient_id,
            "name": v.patient.name,
            "label": v.label,
            "clinic_date": v.clinic_date,
        }
        for v in visits
    ]


def _patients_overdue(as_of):
    """Patients with overdue scheduled visits."""
    from scheduling.models import ScheduledVisit
    visits = ScheduledVisit.objects.filter(
        status="scheduled",
        window_end__lt=as_of,
    ).select_related("patient")
    return [
        {
            "patient_id": v.patient.patient_id,
            "name": v.patient.name,
            "label": v.label,
            "target_date": v.target_date.isoformat(),
            "days_overdue": (as_of - v.window_end).days,
        }
        for v in visits
    ]


def _high_risk_patients(as_of):
    """Patients currently classified as high or very high risk."""
    from followup.models import FollowUpTask, TaskPriority, TaskType, TaskStatus
    overdue_high_risk = FollowUpTask.objects.filter(
        status__in=[TaskStatus.PENDING, TaskStatus.OVERDUE],
        priority__in=[TaskPriority.URGENT, TaskPriority.EMERGENT],
        due_date__lte=as_of,
    ).values_list("patient_id", flat=True).distinct()

    from patients.models import Patient
    patients = Patient.objects.filter(pk__in=set(overdue_high_risk))
    return [
        {
            "patient_id": p.patient_id,
            "name": p.name,
        }
        for p in patients
    ]


def _drug_monitoring_due(as_of):
    """Patients with drug monitoring tasks due."""
    from followup.models import FollowUpTask, TaskType, TaskStatus
    tasks = FollowUpTask.objects.filter(
        task_type=TaskType.DRUG_MONITORING_DUE,
        status=TaskStatus.PENDING,
        due_date__lte=as_of,
    ).select_related("patient")
    return [
        {
            "patient_id": t.patient.patient_id,
            "name": t.patient.name,
            "reason": t.reason,
            "due_date": t.due_date.isoformat(),
        }
        for t in tasks
    ]


def _lab_monitoring_due(as_of):
    """Patients with lab monitoring tasks due."""
    from followup.models import FollowUpTask, TaskType, TaskStatus
    tasks = FollowUpTask.objects.filter(
        task_type=TaskType.LAB_DUE,
        status=TaskStatus.PENDING,
        due_date__lte=as_of,
    ).select_related("patient")
    return [
        {
            "patient_id": t.patient.patient_id,
            "name": t.patient.name,
            "reason": t.reason,
            "due_date": t.due_date.isoformat(),
        }
        for t in tasks
    ]


def _missed_appointments(as_of):
    """Patients who missed scheduled appointments."""
    from scheduling.models import ScheduledVisit
    visits = ScheduledVisit.objects.filter(
        status="missed",
        window_end__gte=as_of - timedelta(days=30),
    ).select_related("patient")
    return [
        {
            "patient_id": v.patient.patient_id,
            "name": v.patient.name,
            "label": v.label,
            "target_date": v.target_date.isoformat(),
        }
        for v in visits
    ]


def _recent_events(as_of, since, event_type):
    """Patients with recent clinical events of a given type."""
    from patients.models import Patient
    patients = Patient.objects.filter(
        events__event_type=event_type,
        events__event_date__gte=since,
    ).distinct()
    return [
        {"patient_id": p.patient_id, "name": p.name}
        for p in patients
    ]


def _recent_aki(as_of, since):
    """Patients with recent AKI (from clinical events)."""
    return _recent_events(as_of, since, "hard_kidney_endpoint")


def _rapid_egfr_decline(as_of, since):
    """Patients with rapid eGFR decline from outcome data."""
    from analytics.models import PatientOutcome
    patients = PatientOutcome.objects.filter(
        sustained_40_decline=True,
        sustained_40_date__gte=since,
    ).select_related("patient")
    return [
        {
            "patient_id": o.patient.patient_id,
            "name": o.patient.name,
            "decline_date": o.sustained_40_date.isoformat(),
            "latest_egfr": float(o.latest_egfr) if o.latest_egfr else None,
        }
        for o in patients
    ]

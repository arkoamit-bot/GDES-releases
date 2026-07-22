"""Data collection functions for real-time dashboards.

Each function returns a dict suitable for JSON serialisation or template context.
Every query is wrapped defensively so dashboards always render.
"""

from __future__ import annotations

import datetime as dt


from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


# ── Enrollment ────────────────────────────────────────────────────────────

def enrollment_summary():
    from patients.models import Patient

    patients = Patient.objects.all()
    total = _safe(patients.count, 0)

    today = dt.date.today()
    month_start = today.replace(day=1)

    return {
        "total": total,
        "new_this_month": _safe(patients.filter(
            enrollment_date__gte=month_start).count, 0),
        "by_cohort": dict(
            patients.values("cohort").annotate(c=Count("pk"))
            .order_by("-c").values_list("cohort", "c")[:8]
        ),
        "by_diabetes": dict(
            patients.values("diabetes_status").annotate(c=Count("pk"))
            .order_by("-c").values_list("diabetes_status", "c")
        ),
        "by_sex": dict(
            patients.values("sex").annotate(c=Count("pk"))
            .order_by("-c").values_list("sex", "c")
        ),
    }


def enrollment_trend(months: int = 12):
    from patients.models import Patient

    cutoff = dt.date.today() - dt.timedelta(days=months * 31)
    rows = (Patient.objects
            .filter(enrollment_date__gte=cutoff)
            .annotate(m=TruncMonth("enrollment_date"))
            .values("m")
            .annotate(c=Count("pk"))
            .order_by("m"))

    labels = []
    counts = []
    for r in rows:
        if r["m"]:
            labels.append(r["m"].strftime("%Y-%m"))
            counts.append(r["c"])

    return {"labels": labels, "counts": counts, "has": bool(labels)}


# ── Outcomes ──────────────────────────────────────────────────────────────

def outcomes_summary():
    from analytics.models import PatientOutcome

    outcomes = PatientOutcome.objects.all()
    total = _safe(outcomes.count, 0)
    if not total:
        return {"total": 0}

    rem_status = dict(
        outcomes.values("remission_status")
        .annotate(c=Count("pk"))
        .values_list("remission_status", "c")
    )

    return {
        "total": total,
        "complete_remission": _safe(
            outcomes.filter(complete_remission__isnull=False).count, 0),
        "partial_remission": _safe(
            outcomes.filter(partial_remission__isnull=False).count, 0),
        "any_remission": _safe(
            outcomes.filter(any_remission_date__isnull=False).count, 0),
        "relapse": _safe(
            outcomes.filter(proteinuria_relapse__isnull=False,
                            any_relapse=True).count, 0),
        "decline_40": _safe(
            outcomes.filter(sustained_40_decline__isnull=False).count, 0),
        "decline_50": _safe(
            outcomes.filter(sustained_50_decline__isnull=False).count, 0),
        "eskd": _safe(outcomes.filter(eskd__isnull=False).count, 0),
        "death": _safe(outcomes.filter(death__isnull=False).count, 0),
        "composite": _safe(
            outcomes.filter(composite_kidney_event__isnull=False).count, 0),
        "remission_status": rem_status,
        "mean_latest_egfr": _safe(
            outcomes.filter(latest_egfr__isnull=False)
            .aggregate(a=Avg("latest_egfr"))["a"], 0),
    }


# ── Protocol Compliance ───────────────────────────────────────────────────

def compliance_summary():
    from patients.models import Patient
    from encounters.models import ClinicalEncounter
    from scheduling.models import ScheduledVisit
    from labs.models import LabResult

    total_patients = _safe(Patient.objects.count, 0)
    if not total_patients:
        return {"total_patients": 0}

    today = dt.date.today()
    three_months_ago = today - dt.timedelta(days=90)
    six_months_ago = today - dt.timedelta(days=180)

    # Visit compliance
    total_visits = _safe(ScheduledVisit.objects.count, 0)
    completed_visits = _safe(
        ScheduledVisit.objects.filter(status="completed").count, 0)
    overdue_count = _safe(
        ScheduledVisit.objects.filter(
            status="scheduled", target_date__lt=today).count, 0)

    # Lab compliance: patients without recent eGFR
    patients_with_recent_egfr = set(
        LabResult.objects.filter(
            test__code="egfr",
            result_date__gte=six_months_ago)
        .values_list("patient_id", flat=True).distinct()
    )
    all_patient_ids = set(
        Patient.objects.values_list("pk", flat=True)
    )

    return {
        "total_patients": total_patients,
        "scheduled_visits": total_visits,
        "completed_visits": completed_visits,
        "overdue_visits": overdue_count,
        "visit_completion_pct": _safe(
            lambda: round(completed_visits / total_visits * 100, 1)
            if total_visits else 0, 0),
        "patients_missing_egfr_6mo": len(all_patient_ids - patients_with_recent_egfr),
        "patients_with_egfr_6mo": len(patients_with_recent_egfr),
        "no_enrollment_date": _safe(
            Patient.objects.filter(enrollment_date__isnull=True).count, 0),
    }


# ── Dashboard overview (combines all for main dashboard) ──────────────────

def overview_stats():
    """Extended stats with monthly deltas for the dashboard grid."""
    from patients.models import Patient
    from encounters.models import ClinicalEncounter
    from prescriptions.models import Prescription
    from labs.models import LabResult
    from pathology.models import Biopsy
    from safety.models import AdverseEvent
    from studies.models import Study

    today = dt.date.today()
    month_start = today.replace(day=1)

    def delta(model_cls, date_field="created_at"):
        total_c = _safe(model_cls.objects.count, 0)
        month_c = _safe(
            model_cls.objects.filter(**{f"{date_field}__gte": month_start}).count, 0)
        return total_c, month_c

    patients_total, patients_month = delta(Patient, "enrollment_date")
    enc_total, enc_month = delta(ClinicalEncounter)
    rx_total, rx_month = delta(Prescription)
    lab_total, lab_month = delta(LabResult)

    return {
        "patients": {"total": patients_total, "this_month": patients_month},
        "encounters": {"total": enc_total, "this_month": enc_month},
        "prescriptions": {"total": rx_total, "this_month": rx_month},
        "lab_results": {"total": lab_total, "this_month": lab_month},
    }

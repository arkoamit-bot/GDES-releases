"""Application views — dashboard and health checks."""
from __future__ import annotations

import datetime
import logging
from collections import Counter, OrderedDict

from django.db import connection
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from patients.models import Patient

logger = logging.getLogger(__name__)


def _enroll_date(p):
    """Best-available enrollment date for a patient (enrollment → registration → created)."""
    d = p.enrollment_date or p.registration_date
    if d:
        return d
    return p.created_at.date() if getattr(p, "created_at", None) else None


def dashboard(request):
    """Main registry dashboard."""
    context = {
        "total_patients": Patient.objects.count(),
        "active_patients": Patient.objects.exclude(registration_status="inactive").count(),
    }
    try:
        from followup.models import FollowUpTask
        context["followup_tasks_pending"] = FollowUpTask.objects.filter(status="pending").count()
        context["followup_tasks_overdue"] = FollowUpTask.objects.filter(status="overdue").count()
        context["followup_high_risk"] = FollowUpTask.objects.filter(
            status__in=("pending", "overdue"), priority__in=("urgent", "emergent")
        ).count()
    except Exception:
        logger.exception("dashboard: follow-up task counts unavailable")
    return render(request, "dashboard.html", context)


def partial_overview_stats(request):
    return _render_partial(request, "dashboard/partials/_overview_stats.html")


def partial_worklist(request):
    return _render_partial(request, "dashboard/partials/_worklist.html")


def partial_enrollment_summary(request):
    qs = Patient.objects.all()
    total = qs.count()
    today = timezone.now().date()
    new_this_month = sum(
        1 for p in qs
        if (d := _enroll_date(p)) and d.year == today.year and d.month == today.month
    )
    by_cohort = OrderedDict()
    for row in qs.values("cohort").annotate(n=Count("id")).order_by("-n"):
        by_cohort[row["cohort"] or "Unspecified"] = row["n"]
    data = {"total": total, "new_this_month": new_this_month, "by_cohort": by_cohort} if total else None
    return _render_partial(request, "dashboard/partials/_enrollment_summary.html", {"data": data})


def partial_cohort_breakdown(request):
    pairs = [
        (row["cohort"] or "Unspecified", row["n"])
        for row in Patient.objects.values("cohort").annotate(n=Count("id")).order_by("-n")
    ]
    data = None
    if pairs:
        data = {
            "labels": ",".join(str(label) for label, _ in pairs),
            "values": ",".join(str(n) for _, n in pairs),
        }
    return _render_partial(request, "dashboard/partials/_cohort_breakdown.html", {"data": data})


def partial_enrollment_trend(request):
    months: Counter = Counter()
    for p in Patient.objects.all():
        d = _enroll_date(p)
        if d:
            months[(d.year, d.month)] += 1
    ordered = sorted(months)
    labels = [datetime.date(y, m, 1).strftime("%b %Y") for (y, m) in ordered]
    counts = [months[k] for k in ordered]
    data = {"has": bool(labels), "labels": labels, "counts": counts}
    return _render_partial(request, "dashboard/partials/_enrollment_trend.html", {"data": data})


def partial_demographics(request):
    qs = Patient.objects.all()
    by_sex = {"M": 0, "F": 0, "O": 0}
    for row in qs.values("sex").annotate(n=Count("id")):
        by_sex[row["sex"] or "O"] = by_sex.get(row["sex"] or "O", 0) + row["n"]
    by_diabetes = OrderedDict()
    for row in qs.values("diabetes_status").annotate(n=Count("id")).order_by("-n"):
        by_diabetes[row["diabetes_status"] or "unknown"] = row["n"]
    data = {"by_sex": by_sex, "by_diabetes": by_diabetes} if qs.exists() else None
    return _render_partial(request, "dashboard/partials/_demographics.html", {"data": data})


def partial_outcomes_summary(request):
    from django.db.models import Avg, Q

    from analytics.models import PatientOutcome

    agg = PatientOutcome.objects.aggregate(
        total=Count("id"),
        complete_remission=Count("id", filter=Q(complete_remission=True)),
        partial_remission=Count("id", filter=Q(partial_remission=True)),
        relapse=Count("id", filter=Q(any_relapse=True)),
        decline_40=Count("id", filter=Q(sustained_40_decline=True)),
        decline_50=Count("id", filter=Q(sustained_50_decline=True)),
        eskd=Count("id", filter=Q(eskd=True)),
        death=Count("id", filter=Q(death=True)),
        composite=Count("id", filter=Q(composite_kidney_event=True)),
        any_remission=Count("id", filter=Q(any_remission_date__isnull=False)),
        mean_latest_egfr=Avg("latest_egfr"),
    )
    data = agg if agg["total"] else None
    return _render_partial(request, "dashboard/partials/_outcomes_summary.html", {"data": data})


def partial_compliance(request):
    from datetime import timedelta

    from labs.models import LabResult

    total_patients = Patient.objects.count()
    data = None
    if total_patients:
        six_mo = timezone.now().date() - timedelta(days=183)

        scheduled = completed = overdue = 0
        try:
            from followup.models import FollowUpTask, TaskStatus
            scheduled = FollowUpTask.objects.exclude(status=TaskStatus.CANCELLED).count()
            completed = FollowUpTask.objects.filter(status=TaskStatus.COMPLETED).count()
            overdue = FollowUpTask.objects.filter(status=TaskStatus.OVERDUE).count()
        except Exception:
            logger.exception("compliance dashboard: follow-up task counts unavailable")

        with_egfr = (
            LabResult.objects.filter(test__code="egfr", result_date__gte=six_mo)
            .values("patient").distinct().count()
        )
        data = {
            "total_patients": total_patients,
            "scheduled_visits": scheduled,
            "completed_visits": completed,
            "overdue_visits": overdue,
            "visit_completion_pct": round(completed / scheduled * 100) if scheduled else 0,
            "patients_with_egfr_6mo": with_egfr,
            "patients_missing_egfr_6mo": total_patients - with_egfr,
            "no_enrollment_date": Patient.objects.filter(enrollment_date__isnull=True).count(),
        }
    return _render_partial(request, "dashboard/partials/_compliance.html", {"data": data})


def dashboard_enrollment(request):
    return render(request, "dashboard/enrollment.html")


def dashboard_outcomes(request):
    return render(request, "dashboard/outcomes.html")


def dashboard_compliance(request):
    return render(request, "dashboard/compliance.html")


def _render_partial(request, template, context=None):
    return render(request, template, context or {})


def health_check(request):
    """Health check endpoint for Docker/K8s readiness and liveness probes."""
    result = {
        "status": "ok",
        "version": 3,
    }
    status_code = 200

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result["database"] = "ok"
    except Exception as e:
        result["database"] = "error"
        result["database_detail"] = str(e)
        result["status"] = "degraded"
        status_code = 503

    # Patient count (basic data integrity check)
    try:
        result["patient_count"] = Patient.objects.count()
    except Exception as e:
        result["patient_count"] = -1
        result["status"] = "degraded"
        status_code = 503

    result["environment"] = "production" if not __debug__ else "development"

    return JsonResponse(result, status=status_code)

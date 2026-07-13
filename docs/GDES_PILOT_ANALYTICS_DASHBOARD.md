# GDES Pilot Analytics Dashboard — Design Document

**Version:** 1.0  
**Date:** 2026-07-12  
**Status:** Proposed  
**Target Release:** V7.2  
**Author:** GDES Engineering & Clinical Informatics  

---

## 1. Executive Summary

GDES currently provides a single general-purpose dashboard (`bgddr/views.py:15-30`) with overview statistics and partial HTMX views for enrollment, outcomes, and compliance. The analytics layer (`analytics/`) offers powerful cohort-level statistical endpoints (Kaplan-Meier, Cox regression, competing risks, eGFR slope) but no operational pilot monitoring views — the daily, weekly, and monthly metrics a nephrology pilot program needs to manage patient care, track quality, and report to stakeholders.

This document proposes a three-tiered pilot monitoring dashboard (Daily / Weekly / Monthly) with purpose-built data collection functions, HTMX partial architecture for real-time updates, Chart.js visualizations, comprehensive filtering, and integration with the existing analytics engine. The design transforms GDES from a retrospective analytics platform into a prospective operational management tool.

---

## 2. Current State Analysis

### 2.1 Existing Dashboard Capabilities

| Component | Location | Capability | Limitation |
|---|---|---|---|
| Main dashboard | `bgddr/views.py:15-30` | Total patients, active patients, followup task counts | No operational metrics; no time-series |
| Overview stats | `bgddr/views.py:33-35` | HTMX partial for basic counts | Single stat card; no trends |
| Enrollment summary | `analytics/dashboard_data.py:25-50` | Total, new this month, by cohort/diabetes/sex | No daily granularity; no diagnostic category |
| Enrollment trend | `analytics/dashboard_data.py:53-71` | Monthly enrollment trend (12 months) | No configurable range |
| Outcomes summary | `analytics/dashboard_data.py:76-113` | Remission rates, relapse, ESKD, death counts | Aggregate only; no time-filtering |
| Compliance summary | `analytics/dashboard_data.py:118-163` | Visit completion, overdue visits, eGFR gap | Basic; no per-disease breakdown |
| Patient outcome | `analytics/views.py:28-74` | Individual patient JSON endpoint | API only; no dashboard visualization |
| Cohort survival | `analytics/views.py:92-106` | KM curves, log-rank, Cox regression | Research-focused; not operational |
| eGFR slope | `analytics/views.py:125-128` | Per-group eGFR slope | Aggregate; no patient-level drill-down |
| Competing risks | `analytics/views.py:132-140` | CIF analysis | Research endpoint; no operational use |

### 2.2 Key Gaps for Pilot Operations

1. **No daily operational view.** Clinic coordinators need to know each morning: how many patients are scheduled, how many new diagnoses this week, pending biopsies, pending pathology reports. The current system has no daily snapshot capability.

2. **No weekly quality view.** Program managers need weekly: missed visits, overdue investigations, SMS reminders sent, AI overrides, new research enrollments. These metrics are scattered across models with no aggregation layer.

3. **No monthly outcomes view.** Clinical leads need monthly: remission rates, CKD progression, ESKD transitions, mortality, registry completeness, missing data, guideline adherence. The `outcomes_summary()` provides raw counts but no rate calculations, no time-filtering, and no disease-stratified breakdowns.

4. **No filtering.** All current dashboard functions operate on the full registry. There is no way to filter by date range, disease, cohort, or site.

5. **No chart visualizations.** The current dashboard is entirely number-based cards. There are no trend lines, no bar charts, no survival curves rendered in the dashboard templates.

---

## 3. Proposed Design

### 3.1 Daily Dashboard

**Purpose:** Real-time operational snapshot for clinic coordinators.  
**Refresh:** Every 5 minutes via HTMX polling.  
**Primary audience:** Clinic coordinators, nursing staff.

#### Metrics

| Metric | Data Source | Computation | Alert Threshold |
|---|---|---|---|
| New patients today | `Patient.objects.filter(enrollment_date=today)` | Count | — |
| Follow-up patients today | `ScheduledVisit.objects.filter(target_date=today, status="scheduled")` | Count | — |
| New GN diagnoses this week | `ClinicalEvent.objects.filter(event_type="diagnosis", event_date__gte=week_start)` | Count | — |
| Active relapses | `ClinicalProfile.objects.filter(care_pathway__current_stage__contains="relapse")` or `PatientOutcome.objects.filter(any_relapse=True, proteinuria_relapse_date__gte=week_start)` | Count | >5 |
| Pending biopsies | `Biopsy.objects.filter(status__in=("scheduled", "pending_report"))` | Count | >10 |
| Pending pathology reports | `Biopsy.objects.filter(status="pending_report", biopsy_date__lte=today - 7)` | Count, list | >0 with >7 days |
| Clinic capacity today | `ScheduledVisit.objects.filter(target_date=today, status="scheduled").count()` vs max | Percentage | >90% |
| Overdue tasks | `FollowUpTask.objects.filter(status="overdue")` | Count by priority | >5 urgent |

#### Data Collection Function

```python
# analytics/dashboard_data.py — new function

def daily_dashboard(date_override: dt.date = None) -> dict:
    """Daily operational snapshot for clinic coordinators."""
    today = date_override or dt.date.today()
    week_start = today - dt.timedelta(days=today.weekday())
    yesterday = today - dt.timedelta(days=1)

    from patients.models import Patient
    from encounters.models import ClinicalEncounter
    from scheduling.models import ScheduledVisit
    from followup.models import FollowUpTask
    from pathology.models import Biopsy
    from labs.models import LabResult

    return {
        "date": str(today),
        "new_patients_today": _safe(Patient.objects.filter(
            enrollment_date=today).count, 0),
        "new_patients_week": _safe(Patient.objects.filter(
            enrollment_date__gte=week_start).count, 0),
        "followup_today": _safe(ScheduledVisit.objects.filter(
            target_date=today, status="scheduled").count, 0),
        "encounters_yesterday": _safe(ClinicalEncounter.objects.filter(
            encounter_date=yesterday).count, 0),
        "new_gn_diagnoses_week": _safe(ClinicalEncounter.objects.filter(
            encounter_date__gte=week_start,
            encounter_type="diagnosis").count, 0),
        "active_relapses": _safe(_count_active_relapses(), 0),
        "pending_biopsies": _safe(Biopsy.objects.filter(
            status__in=("scheduled", "in_progress")).count, 0),
        "pending_pathology_reports": _safe(_pending_pathology_list(), []),
        "clinic_capacity_pct": _safe(_clinic_capacity_pct(today), 0),
        "overdue_tasks": {
            "total": _safe(FollowUpTask.objects.filter(
                status="overdue").count, 0),
            "urgent": _safe(FollowUpTask.objects.filter(
                status="overdue", priority__in=("urgent", "emergent")).count, 0),
        },
        "labs_completed_yesterday": _safe(LabResult.objects.filter(
            result_date=yesterday).count, 0),
    }


def _pending_pathology_list() -> list[dict]:
    """List biopsies waiting for pathology reports >7 days."""
    from datetime import date as _date
    threshold = _date.today() - dt.timedelta(days=7)
    from pathology.models import Biopsy
    pending = Biopsy.objects.filter(
        status="pending_report",
        biopsy_date__lte=threshold
    ).select_related("patient").order_by("biopsy_date")
    return [
        {
            "patient_id": b.patient.patient_id,
            "biopsy_date": str(b.biopsy_date),
            "days_waiting": (_date.today() - b.biopsy_date).days,
        }
        for b in pending[:20]
    ]


def _clinic_capacity_pct(today: dt.date) -> float:
    """Percentage of clinic slots filled for today."""
    from scheduling.models import ScheduledVisit
    total_slots = 15  # Max per GN clinic session
    booked = ScheduledVisit.objects.filter(
        target_date=today, status="scheduled").count()
    return round(booked / total_slots * 100, 1) if total_slots else 0


def _count_active_relapses() -> int:
    """Count patients with active relapse status."""
    from patients.models import Patient
    from analytics.models import PatientOutcome
    return Patient.objects.filter(
        current_phase="relapse"
    ).count() + PatientOutcome.objects.filter(
        proteinuria_relapse=True,
        proteinuria_relapse_date__gte=dt.date.today() - dt.timedelta(days=90),
        eskd__isnull=True,
        death__isnull=True,
    ).exclude(
        patient__in=Patient.objects.filter(current_phase="remission")
    ).count()
```

### 3.2 Weekly Dashboard

**Purpose:** Quality metrics for program managers.  
**Refresh:** Every hour via HTMX polling, or on-demand.  
**Primary audience:** Program managers, clinical leads.

#### Metrics

| Metric | Data Source | Computation | Target |
|---|---|---|---|
| Missed visits this week | `ScheduledVisit.objects.filter(status="missed", target_date__range=...)` | Count, rate | <5% |
| Overdue investigations | `FollowUpTask.objects.filter(task_type="lab_due", status="overdue")` | Count by type | <10 |
| SMS reminders sent | `CommunicationLog.objects.filter(type="sms_reminder", sent_date__range=...)` | Count | Track only |
| AI overrides this week | `RecommendationAudit.objects.filter(approval_status="overridden", issued_at__range=...)` | Count, list | <10% override rate |
| New research enrollments | `StudyEnrollment.objects.filter(enrolled_date__range=...)` | Count by study | Track only |
| Guideline adherence rate | Adherent recommendations / total recommendations | Percentage | >90% |
| Task completion rate | Completed tasks / total tasks due this week | Percentage | >85% |
| eGFR monitoring compliance | Patients with eGFR in last 90 days / total active patients | Percentage | >95% |
| Protocol deviations | `ClinicalEncounter.objects.filter(protocol_deviation=True)` | Count | <5% |

#### Data Collection Function

```python
# analytics/dashboard_data.py — new function

def weekly_dashboard(week_end: dt.date = None) -> dict:
    """Weekly quality metrics for program management."""
    end = week_end or dt.date.today()
    start = end - dt.timedelta(days=7)
    month_start = end.replace(day=1)

    from scheduling.models import ScheduledVisit
    from followup.models import FollowUpTask
    from knowledge.models import RecommendationAudit
    from studies.models import StudyEnrollment
    from labs.models import LabResult
    from patients.models import Patient

    # Missed visits
    missed = ScheduledVisit.objects.filter(
        status="missed", target_date__range=(start, end))
    total_scheduled = ScheduledVisit.objects.filter(
        target_date__range=(start, end))

    # Overdue investigations by type
    overdue_by_type = dict(
        FollowUpTask.objects.filter(status="overdue", due_date__lte=end)
        .values("task_type").annotate(c=Count("pk")).values_list("task_type", "c")
    )

    # AI override rate
    total_recs = RecommendationAudit.objects.filter(
        issued_at__date__range=(start, end)).count()
    overrides = RecommendationAudit.objects.filter(
        issued_at__date__range=(start, end),
        approval_status="overridden").count()

    # eGFR compliance
    patients_with_egfr = set(
        LabResult.objects.filter(
            test__code="egfr",
            result_date__gte=end - dt.timedelta(days=90))
        .values_list("patient_id", flat=True))
    active_patients = Patient.objects.exclude(
        registration_status="inactive").count()

    return {
        "week_start": str(start),
        "week_end": str(end),
        "missed_visits": {
            "count": _safe(missed.count, 0),
            "rate": _safe(lambda: round(
                missed.count() / total_scheduled.count() * 100, 1
            ) if total_scheduled.exists() else 0, 0),
        },
        "overdue_investigations": {
            "total": sum(overdue_by_type.values()),
            "by_type": overdue_by_type,
        },
        "sms_reminders_sent": _safe(_count_sms_reminders(start, end), 0),
        "ai_overrides": {
            "count": overrides,
            "rate": round(overrides / total_recs * 100, 1) if total_recs else 0,
        },
        "new_research_enrollments": _safe(
            StudyEnrollment.objects.filter(
                enrolled_date__range=(start, end)).count, 0),
        "egfr_monitoring_compliance": round(
            len(patients_with_egfr) / active_patients * 100, 1
        ) if active_patients else 0,
        "task_completion_rate": _safe(_task_completion_rate(start, end), 0),
    }


def _count_sms_reminders(start, end) -> int:
    try:
        from communication.models import CommunicationLog
        return CommunicationLog.objects.filter(
            message_type="sms_reminder",
            sent_date__range=(start, end)).count()
    except Exception:
        return 0


def _task_completion_rate(start, end) -> float:
    from followup.models import FollowUpTask
    due = FollowUpTask.objects.filter(due_date__range=(start, end))
    if not due.exists():
        return 0.0
    completed = due.filter(status="completed").count()
    return round(completed / due.count() * 100, 1)
```

### 3.3 Monthly Dashboard

**Purpose:** Comprehensive clinical outcomes and quality report for clinical leads and regulatory reporting.  
**Refresh:** On-demand or monthly (first of month).  
**Primary audience:** Clinical leads, principal investigators, regulatory.

#### Metrics

| Category | Metric | Data Source | Computation |
|---|---|---|---|
| **Remission** | Complete remission rate | `PatientOutcome.complete_remission` | CR count / total with ≥6mo follow-up |
| | Partial remission rate | `PatientOutcome.partial_remission` | PR count / total |
| | Time to CR (median days) | `PatientOutcome.complete_remission_date - index_date` | Median |
| **Progression** | CKD progression rate | Patients with sustained ≥40% eGFR decline | Count / total |
| | eGFR slope (mean) | `PatientOutcome.egfr_slope` | Mean ± SD |
| | ESKD transition rate | `PatientOutcome.eskd` | Count / total |
| **Mortality** | All-cause mortality | `PatientOutcome.death` | Rate per 100 patient-years |
| | Kidney-specific mortality | Death with ESKD as cause | Rate per 100 py |
| **Research** | Active study enrollments | `StudyEnrollment` by status | Count by study |
| | Research visit compliance | Completed research visits / total due | Percentage |
| **Registry** | Overall completeness score | All required fields present / total | Percentage |
| | Per-category completeness | demographics, labs, biopsy, treatment, outcomes | Percentage each |
| | Missing data report | Fields with <80% completeness | List |
| **Guideline** | Adherence to KDIGO recommendations | RecommendationAudit approved / total | Percentage |
| | Override rate by type | Overrides / recommendations by type | Percentage per type |
| | Time to recommendation <24h | Recommendations issued within 24h / total | Percentage |

#### Data Collection Function

```python
# analytics/dashboard_data.py — new function

def monthly_dashboard(month: dt.date = None) -> dict:
    """Comprehensive monthly clinical outcomes and quality report."""
    ref = month or dt.date.today().replace(day=1)
    month_start = ref
    if ref.month == 12:
        month_end = ref.replace(year=ref.year + 1, month=1, day=1) - dt.timedelta(days=1)
    else:
        month_end = ref.replace(month=ref.month + 1, day=1) - dt.timedelta(days=1)

    prev_month_start = (month_start - dt.timedelta(days=1)).replace(day=1)

    from analytics.models import PatientOutcome
    from patients.models import Patient
    from knowledge.models import RecommendationAudit
    from studies.models import StudyEnrollment

    # Outcomes cohort: patients with ≥6 months follow-up
    six_mo_patients = Patient.objects.filter(
        enrollment_date__gte=month_start - dt.timedelta(days=180))
    outcomes = PatientOutcome.objects.filter(patient__in=six_mo_patients)

    total_with_outcomes = outcomes.count()
    cr_count = outcomes.filter(complete_remission=True).count()
    pr_count = outcomes.filter(partial_remission=True).count()
    eskd_count = outcomes.filter(eskd=True).count()
    death_count = outcomes.filter(death=True).count()
    decline_40 = outcomes.filter(sustained_40_decline=True).count()

    # Recommendation audit
    recs_month = RecommendationAudit.objects.filter(
        issued_at__date__range=(month_start, month_end))
    total_recs = recs_month.count()
    approved = recs_month.filter(approval_status="approved").count()
    overridden = recs_month.filter(approval_status="overridden").count()

    # Research
    enrollments = StudyEnrollment.objects.filter(
        enrolled_date__range=(month_start, month_end))

    return {
        "month": ref.strftime("%Y-%m"),
        "remission": {
            "complete_remission_rate": _safe(lambda: round(
                cr_count / total_with_outcomes * 100, 1), 0) if total_with_outcomes else 0,
            "partial_remission_rate": _safe(lambda: round(
                pr_count / total_with_outcomes * 100, 1), 0) if total_with_outcomes else 0,
            "median_time_to_cr_days": _safe(lambda: _median_time_to_event(
                outcomes, "complete_remission", "complete_remission_date"), None),
        },
        "progression": {
            "ckd_progression_rate": _safe(lambda: round(
                decline_40 / total_with_outcomes * 100, 1), 0) if total_with_outcomes else 0,
            "mean_egfr_slope": _safe(lambda: round(float(
                outcomes.filter(egfr_slope__isnull=False).aggregate(
                    m=Avg("egfr_slope"))["m"]), 2), None),
            "eskd_transition_rate": _safe(lambda: round(
                eskd_count / total_with_outcomes * 100, 1), 0) if total_with_outcomes else 0,
        },
        "mortality": {
            "all_cause_rate": _safe(lambda: round(
                death_count / total_with_outcomes * 100, 1), 0) if total_with_outcomes else 0,
        },
        "research": {
            "new_enrollments": enrollments.count(),
            "by_study": dict(
                enrollments.values("study__code").annotate(
                    c=Count("pk")).values_list("study__code", "c")),
        },
        "guideline_adherence": {
            "approval_rate": round(approved / total_recs * 100, 1) if total_recs else 0,
            "override_rate": round(overridden / total_recs * 100, 1) if total_recs else 0,
            "overrides_by_type": dict(
                recs_month.filter(approval_status="overridden")
                .values("recommendation_type").annotate(
                    c=Count("pk")).values_list("recommendation_type", "c")),
        },
        "registry_completeness": _safe(_monthly_completeness, {}),
    }


def _median_time_to_event(outcomes, flag_field, date_field) -> int | None:
    """Median time in days from index to event."""
    events = outcomes.filter(**{flag_field: True, f"{date_field}__isnull": False})
    if not events.exists():
        return None
    times = [
        (getattr(e, date_field) - e.index_date).days
        for e in events
        if e.index_date and getattr(e, date_field)
    ]
    if not times:
        return None
    times.sort()
    n = len(times)
    return times[n // 2] if n % 2 else (times[n // 2 - 1] + times[n // 2]) // 2


def _monthly_completeness() -> dict:
    """Registry completeness scorecard."""
    from patients.models import Patient
    REQUIRED = {
        "demographics": ["dob", "sex", "enrollment_date", "primary_diagnosis"],
        "labs": ["latest_egfr", "latest_upcr"],
        "biopsy": ["has_biopsy"],
    }
    total = Patient.objects.count()
    if not total:
        return {"overall": 0}
    scores = {}
    for cat, fields in REQUIRED.items():
        present = 0
        for patient in Patient.objects.all():
            for f in fields:
                if _field_present(patient, f):
                    present += 1
        scores[cat] = round(present / (total * len(fields)) * 100, 1)
    scores["overall"] = round(sum(scores.values()) / len(scores), 1)
    return scores


def _field_present(patient, field_name: str) -> bool:
    """Check if a field is present and non-empty on a patient."""
    if field_name == "has_biopsy":
        return hasattr(patient, "biopsies") and patient.biopsies.exists()
    val = getattr(patient, field_name, None)
    return val is not None and val != ""
```

### 3.4 Filtering Architecture

All dashboard functions accept an optional `filters` parameter:

```python
@dataclass
class DashboardFilters:
    """Reusable filter set for all dashboard views."""
    date_from: dt.date | None = None
    date_to: dt.date | None = None
    diseases: list[str] | None = None
    cohorts: list[str] | None = None
    phases: list[str] | None = None
    sites: list[str] | None = None  # For multi-site pilots

    def apply_to_patient_queryset(self, qs):
        """Apply filters to a Patient queryset."""
        if self.diseases:
            qs = qs.filter(primary_diagnosis__in=self.diseases)
        if self.cohorts:
            qs = qs.filter(cohort__in=self.cohorts)
        if self.phases:
            qs = qs.filter(current_phase__in=self.phases)
        if self.sites:
            qs = qs.filter(site__in=self.sites)
        if self.date_from:
            qs = qs.filter(enrollment_date__gte=self.date_from)
        if self.date_to:
            qs = qs.filter(enrollment_date__lte=self.date_to)
        return qs

    @classmethod
    def from_request(cls, request) -> "DashboardFilters":
        """Extract filters from GET parameters."""
        return cls(
            date_from=_parse_date(request.GET.get("from")),
            date_to=_parse_date(request.GET.get("to")),
            diseases=request.GET.getlist("disease") or None,
            cohorts=request.GET.getlist("cohort") or None,
            phases=request.GET.getlist("phase") or None,
            sites=request.GET.getlist("site") or None,
        )
```

---

## 4. Visualization Designs

### 4.1 Chart.js Configurations

All charts use Chart.js loaded via CDN. Each chart has a dedicated HTMX partial with an inline `<canvas>` and a `<script>` block that initializes the chart from JSON data attributes.

#### Daily Dashboard Charts

| Chart | Type | Data | Purpose |
|---|---|---|---|
| Clinic capacity gauge | Doughnut | booked / remaining slots | Visual capacity indicator |
| Task priority breakdown | Doughnut | overdue by priority level | Triage urgent vs. routine |
| Weekly patient flow | Bar | new patients, encounters, tasks per day | Activity trend |

#### Weekly Dashboard Charts

| Chart | Type | Data | Purpose |
|---|---|---|---|
| Missed visits trend | Line | daily missed visits over 4 weeks | Identify patterns |
| Overdue investigations by type | Horizontal bar | lab_due, visit_due, vaccination_due, etc. | Prioritize follow-up |
| AI override rate trend | Line | daily override rate over 4 weeks | Monitor clinician trust |
| Task completion funnel | Bar | pending → completed → overdue | Workflow efficiency |

#### Monthly Dashboard Charts

| Chart | Type | Data | Purpose |
|---|---|---|---|
| Remission rates trend | Line (multi) | CR rate, PR rate over 12 months | Outcomes trajectory |
| eGFR slope distribution | Histogram | patient-level eGFR slopes | Cohort kidney health |
| CKD stage transition Sankey | Sankey | patients moving between stages | Disease trajectory |
| Guideline adherence by type | Grouped bar | approval/override per recommendation type | Quality indicator |
| Registry completeness heatmap | Heatmap | completeness % per field × disease | Data quality |
| Research enrollment | Stacked bar | new enrollments per study per month | Recruitment progress |
| Mortality & ESKD Kaplan-Meier | Line | cumulative incidence over time | Hard endpoint tracking |

### 4.2 Chart Template Pattern

```html
<!-- dashboard/partials/_monthly_remission_trend.html -->
<div class="card">
  <div class="card-header">
    <h5>Remission Rates (12-month trend)</h5>
    <select hx-get="/dashboard/monthly/remission-trend/"
            hx-target="#remission-chart" hx-trigger="change"
            name="disease" class="form-select form-select-sm">
      <option value="">All diseases</option>
      {% for d in diseases %}<option value="{{ d.id }}">{{ d.name }}</option>{% endfor %}
    </select>
  </div>
  <div class="card-body">
    <canvas id="remission-trend-canvas" width="400" height="200"></canvas>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('remission-trend-canvas');
    const labels = JSON.parse(canvas.dataset.labels || '[]');
    const crData = JSON.parse(canvas.dataset.cr || '[]');
    const prData = JSON.parse(canvas.dataset.pr || '[]');

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                { label: 'Complete Remission %', data: crData,
                  borderColor: '#28a745', tension: 0.3, fill: false },
                { label: 'Partial Remission %', data: prData,
                  borderColor: '#ffc107', tension: 0.3, fill: false },
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, max: 100 } },
            plugins: { legend: { position: 'bottom' } }
        }
    });
});
</script>
```

---

## 5. Views and URL Architecture

### 5.1 New Views

```python
# analytics/views.py — additions

@login_required
def daily_dashboard_view(request):
    """Daily operational dashboard."""
    from analytics.dashboard_data import daily_dashboard
    context = {
        "daily": daily_dashboard(),
        "filters": DashboardFilters.from_request(request),
    }
    return render(request, "dashboard/daily.html", context)


@login_required
def weekly_dashboard_view(request):
    """Weekly quality dashboard."""
    from analytics.dashboard_data import weekly_dashboard
    context = {
        "weekly": weekly_dashboard(),
        "filters": DashboardFilters.from_request(request),
    }
    return render(request, "dashboard/weekly.html", context)


@login_required
def monthly_dashboard_view(request):
    """Monthly outcomes dashboard."""
    from analytics.dashboard_data import monthly_dashboard
    context = {
        "monthly": monthly_dashboard(),
        "filters": DashboardFilters.from_request(request),
        "diseases": Disease.objects.filter(is_active=True),
    }
    return render(request, "dashboard/monthly.html", context)
```

### 5.2 HTMX Partial Endpoints

```python
# analytics/views.py — HTMX partials

@login_required
def partial_daily_summary(request):
    from analytics.dashboard_data import daily_dashboard
    return render(request, "dashboard/partials/_daily_summary.html",
                  {"daily": daily_dashboard()})

@login_required
def partial_daily_pathology(request):
    from analytics.dashboard_data import daily_dashboard
    return render(request, "dashboard/partials/_daily_pathology.html",
                  {"daily": daily_dashboard()})

@login_required
def partial_weekly_missed(request):
    from analytics.dashboard_data import weekly_dashboard
    return render(request, "dashboard/partials/_weekly_missed.html",
                  {"weekly": weekly_dashboard()})

@login_required
def partial_weekly_overdue(request):
    from analytics.dashboard_data import weekly_dashboard
    return render(request, "dashboard/partials/_weekly_overdue.html",
                  {"weekly": weekly_dashboard()})

@login_required
def partial_monthly_remission(request):
    from analytics.dashboard_data import monthly_dashboard
    return render(request, "dashboard/partials/_monthly_remission.html",
                  {"monthly": monthly_dashboard()})

@login_required
def partial_monthly_progression(request):
    from analytics.dashboard_data import monthly_dashboard
    return render(request, "dashboard/partials/_monthly_progression.html",
                  {"monthly": monthly_dashboard()})

@login_required
def partial_monthly_research(request):
    from analytics.dashboard_data import monthly_dashboard
    return render(request, "dashboard/partials/_monthly_research.html",
                  {"monthly": monthly_dashboard()})
```

### 5.3 URL Configuration

```python
# analytics/urls.py — additions

urlpatterns = [
    # ... existing patterns ...

    # Pilot dashboards
    path("dashboard/daily/", views.daily_dashboard_view, name="daily_dashboard"),
    path("dashboard/weekly/", views.weekly_dashboard_view, name="weekly_dashboard"),
    path("dashboard/monthly/", views.monthly_dashboard_view, name="monthly_dashboard"),

    # HTMX partials
    path("dashboard/daily/partial/summary/", views.partial_daily_summary, name="partial_daily_summary"),
    path("dashboard/daily/partial/pathology/", views.partial_daily_pathology, name="partial_daily_pathology"),
    path("dashboard/weekly/partial/missed/", views.partial_weekly_missed, name="partial_weekly_missed"),
    path("dashboard/weekly/partial/overdue/", views.partial_weekly_overdue, name="partial_weekly_overdue"),
    path("dashboard/monthly/partial/remission/", views.partial_monthly_remission, name="partial_monthly_remission"),
    path("dashboard/monthly/partial/progression/", views.partial_monthly_progression, name="partial_monthly_progression"),
    path("dashboard/monthly/partial/research/", views.partial_monthly_research, name="partial_monthly_research"),
]
```

---

## 6. Template Architecture

### 6.1 Base Layout

```
templates/dashboard/
├── daily.html              # Full daily page
├── weekly.html             # Full weekly page
├── monthly.html            # Full monthly page
├── partials/
│   ├── _daily_summary.html         # KPI cards (auto-refresh every 5 min)
│   ├── _daily_pathology.html       # Pending pathology list
│   ├── _daily_capacity.html        # Clinic capacity gauge
│   ├── _daily_tasks.html           # Task priority breakdown
│   ├── _weekly_missed.html         # Missed visits trend chart
│   ├── _weekly_overdue.html        # Overdue investigations chart
│   ├── _weekly_overrides.html      # AI override trend chart
│   ├── _weekly_compliance.html     # Task completion funnel
│   ├── _monthly_remission.html     # Remission rates trend chart
│   ├── _monthly_progression.html   # CKD progression chart
│   ├── _monthly_mortality.html     # KM survival chart
│   ├── _monthly_research.html      # Research enrollment chart
│   ├── _monthly_guideline.html     # Guideline adherence chart
│   ├── _monthly_completeness.html  # Registry completeness heatmap
│   └── _filter_bar.html            # Shared filter component
```

### 6.2 Auto-Refresh Pattern

```html
<!-- daily.html -->
<div class="container-fluid">
    {% include "dashboard/partials/_filter_bar.html" %}

    <div id="daily-summary"
         hx-get="{% url 'partial_daily_summary' %}"
         hx-trigger="every 300s"
         hx-swap="innerHTML">
        {% include "dashboard/partials/_daily_summary.html" %}
    </div>

    <div class="row">
        <div class="col-md-6">
            <div id="daily-pathology"
                 hx-get="{% url 'partial_daily_pathology' %}"
                 hx-trigger="every 300s">
                {% include "dashboard/partials/_daily_pathology.html" %}
            </div>
        </div>
        <div class="col-md-6">
            <div id="daily-tasks"
                 hx-get="{% url 'partial_daily_tasks' %}"
                 hx-trigger="every 300s">
                {% include "dashboard/partials/_daily_tasks.html" %}
            </div>
        </div>
    </div>
</div>
```

---

## 7. Implementation Plan

### Phase 1: Data Collection Layer (Week 1-2)

| Task | Files | Depends On |
|---|---|---|
| Implement `daily_dashboard()` | `analytics/dashboard_data.py` | — |
| Implement `weekly_dashboard()` | `analytics/dashboard_data.py` | — |
| Implement `monthly_dashboard()` | `analytics/dashboard_data.py` | — |
| Implement `DashboardFilters` | `analytics/filters.py` | — |
| Unit tests for all data functions (30+ tests) | `analytics/tests/test_dashboard_data.py` | — |
| Performance benchmarks | `analytics/tests/test_performance.py` | — |

### Phase 2: Views and URLs (Week 2-3)

| Task | Files | Depends On |
|---|---|---|
| Add dashboard views | `analytics/views.py` | Phase 1 |
| Add HTMX partial views | `analytics/views.py` | Phase 1 |
| URL configuration | `analytics/urls.py` | Phase 1-2 |
| View tests (15+ tests) | `analytics/tests/test_views.py` | Phase 1-2 |

### Phase 3: Templates — Daily Dashboard (Week 3-4)

| Task | Files | Depends On |
|---|---|---|
| `daily.html` base template | `templates/dashboard/` | Phase 2 |
| `_daily_summary.html` partial | `templates/dashboard/partials/` | Phase 2 |
| `_daily_pathology.html` partial | `templates/dashboard/partials/` | Phase 2 |
| `_daily_capacity.html` partial | `templates/dashboard/partials/` | Phase 2 |
| `_daily_tasks.html` partial | `templates/dashboard/partials/` | Phase 2 |
| `_filter_bar.html` component | `templates/dashboard/partials/` | Phase 2 |
| Chart.js doughnut (capacity) | Embedded in partial | Phase 3 |
| HTMX auto-refresh integration | `daily.html` | Phase 3 |

### Phase 4: Templates — Weekly Dashboard (Week 4-5)

| Task | Files | Depends On |
|---|---|---|
| `weekly.html` base template | `templates/dashboard/` | Phase 2 |
| `_weekly_missed.html` partial + line chart | `templates/dashboard/partials/` | Phase 2 |
| `_weekly_overdue.html` partial + bar chart | `templates/dashboard/partials/` | Phase 2 |
| `_weekly_overrides.html` partial + line chart | `templates/dashboard/partials/` | Phase 2 |
| `_weekly_compliance.html` partial + bar chart | `templates/dashboard/partials/` | Phase 2 |
| HTMX integration | `weekly.html` | Phase 4 |

### Phase 5: Templates — Monthly Dashboard (Week 5-6)

| Task | Files | Depends On |
|---|---|---|
| `monthly.html` base template | `templates/dashboard/` | Phase 2 |
| `_monthly_remission.html` partial + multi-line chart | `templates/dashboard/partials/` | Phase 2 |
| `_monthly_progression.html` partial + histogram | `templates/dashboard/partials/` | Phase 2 |
| `_monthly_mortality.html` partial + KM chart | `templates/dashboard/partials/` | Phase 2 |
| `_monthly_research.html` partial + stacked bar | `templates/dashboard/partials/` | Phase 2 |
| `_monthly_guideline.html` partial + grouped bar | `templates/dashboard/partials/` | Phase 2 |
| `_monthly_completeness.html` partial + heatmap | `templates/dashboard/partials/` | Phase 2 |
| Chart.js integration for all monthly charts | Embedded in partials | Phase 5 |

### Phase 6: Integration and Polish (Week 6-7)

| Task | Files | Depends On |
|---|---|---|
| Dashboard navigation sidebar | `templates/base.html` | Phase 3-5 |
| Filter bar HTMX integration (disease, date, cohort) | `_filter_bar.html`, views | Phase 1-5 |
| Responsive design verification | All templates | Phase 3-5 |
| Accessibility audit (WCAG 2.1 AA) | All templates | Phase 3-5 |
| Integration tests: full page loads + HTMX | `analytics/tests/test_integration.py` | Phase 1-5 |

---

## 8. Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Daily dashboard load time | <2 seconds | Browser performance audit |
| HTMX partial refresh | <1 second | Network waterfall analysis |
| Chart render time | <500ms for all charts | Browser console timing |
| Data accuracy | 100% concordance with manual query | Validate 20 random metrics against raw SQL |
| Filter responsiveness | <3 seconds with all filters applied | Performance test |
| Auto-refresh reliability | >99% successful HTMX polls | Server-side monitoring |
| User coverage | 100% of daily/weekly/monthly metrics implemented | Checklist against design spec |
| Chart.js bundle size | <200KB gzipped | Build analysis |
| Template coverage | All partials render without error | Automated render tests |
| Mobile responsiveness | All dashboards usable on tablet (768px) | Manual QA |

---

## 9. Risk Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Dashboard queries slow on large cohorts (>1000 patients) | High | Pre-aggregate daily snapshots; use `select_related`/`prefetch`; index critical date fields |
| Chart.js conflicts with existing JS | Medium | Use `Chart.js` v4 with `defer` loading; namespace all chart instances |
| HTMX polling creates server load | Medium | 5-minute minimum interval for daily; hourly for weekly; no auto-refresh for monthly |
| Filter combinations produce empty charts | Low | Graceful empty state with "No data for selected filters" message |
| Chart.js CDN availability | Low | Bundle Chart.js locally as fallback |
| Timezone issues with date boundaries | Medium | All date operations use `dt.date` (not datetime); server timezone configured in Django settings |

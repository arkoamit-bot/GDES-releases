"""Analytics, export, quality assessment, and advanced statistics views."""
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ._common import LOGIN, Patient, login_required


# --- Quality assessment (workflow steps 6-7) ---------------------------------

@login_required(login_url=LOGIN)
def quality_page(request):
    """Biopsy yield, predictors of a positive biopsy, phase/response/relapse
    snapshots, and the between-group comparison the clinic uses for insight."""
    from analytics.services import quality
    group_by = request.GET.get("group_by", "diagnosis")
    if group_by not in quality.GROUPERS:
        group_by = "diagnosis"
    ctx = {
        "active": "quality",
        "yield": quality.biopsy_yield(),
        "phases": quality.phase_distribution(),
        "relapse": quality.relapse_rate(),
        "concordance": quality.remission_concordance(),
        "comparison": quality.group_comparison(group_by),
        "group_by": group_by,
        "groupers": [(k, v[0]) for k, v in quality.GROUPERS.items()],
    }
    return render(request, "clinic/quality.html", ctx)


# --- Analytics & Export landing pages ----------------------------------------

@login_required(login_url=LOGIN)
def analytics_page(request):
    """Cohort analytics rendered as tables."""
    group_by = request.GET.get("group_by", "diagnosis")
    endpoint = request.GET.get("endpoint", "composite_kidney_event")
    ctx = {
        "active": "analytics", "group_by": group_by, "endpoint": endpoint,
        "group_options": ["diabetes", "diagnosis", "cohort"],
        "endpoint_options": [
            "composite_kidney_event", "eskd", "death",
            "sustained_40_decline", "sustained_50_decline",
            "complete_remission", "partial_remission", "any_remission",
            "igan_proteinuria_response",
        ],
    }
    qs = Patient.objects.all()

    try:
        from analytics.services.cohort import cohort_summary
        rows = cohort_summary(qs, group_by) or []
        cols = list(rows[0].keys()) if rows else []
        ctx["summary_cols"] = [c.replace("_", " ") for c in cols]
        ctx["summary_rows"] = [[r.get(c) for c in cols] for r in rows]
    except Exception as exc:
        ctx["summary_error"] = str(exc)

    try:
        from analytics.services.cohort import cohort_survival
        cohort = cohort_survival(qs, group_by, endpoint)
        ctx["surv_groups"] = cohort.groups
        ctx["surv_logrank"] = cohort.logrank
    except Exception as exc:
        ctx["surv_error"] = str(exc)

    return render(request, "clinic/analytics.html", ctx)


@login_required(login_url=LOGIN)
def export_page(request):
    from studies.models import Study
    studies = (Study.objects.exclude(status=Study.Status.CLOSED)
               .order_by("code").values_list("code", "title"))
    return render(request, "clinic/export.html",
                  {"active": "export", "studies": list(studies)})


# --- Outcomes ---------------------------------------------------------------

@login_required(login_url=LOGIN)
def outcome_recompute(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    try:
        from analytics.services.outcomes import compute_patient_outcome
        compute_patient_outcome(patient)
        messages.success(request, "Outcomes recomputed from current data.")
    except Exception as exc:
        messages.error(request, f"Could not compute outcomes: {exc}")
    return redirect("clinic:patient_detail", pk=patient.pk)


# --- Advanced analytics results (HTML wrappers for JSON endpoints) ----------

@login_required(login_url=LOGIN)
def cox_results(request):
    """Multivariable Cox PH rendered as a table instead of raw JSON."""
    endpoint = request.GET.get("endpoint", "composite_kidney_event")
    raw = request.GET.get("covariates", "age,diabetes,baseline_egfr")
    covariates = [c.strip() for c in raw.split(",") if c.strip()]
    ctx = {
        "active": "analytics", "endpoint": endpoint, "covariates": raw,
        "endpoint_options": [
            "composite_kidney_event", "eskd", "death",
            "sustained_40_decline", "sustained_50_decline",
            "complete_remission", "partial_remission", "any_remission",
            "igan_proteinuria_response",
        ],
    }
    try:
        from analytics.services.cohort import cox_regression
        result, meta = cox_regression(Patient.objects.all(), covariates, endpoint)
        ctx["result"] = {**result, **meta}
    except ValueError as exc:
        ctx["error"] = str(exc)
    except Exception as exc:
        ctx["error"] = f"Could not compute: {exc}"
    return render(request, "clinic/cox_results.html", ctx)


@login_required(login_url=LOGIN)
def egfr_slope_results(request):
    """Linear mixed-effects eGFR slope per group."""
    group_by = request.GET.get("group_by", "diabetes")
    ctx = {"active": "analytics", "group_by": group_by,
           "group_options": ["diabetes", "diagnosis", "cohort"]}
    try:
        from analytics.services.cohort import cohort_egfr_slope
        data = cohort_egfr_slope(Patient.objects.all(), group_by)
        if data and "groups" in data:
            rows = []
            for g in data["groups"]:
                rows.append({
                    "label": g,
                    "slope": data.get(f"slope_{g}"),
                    "n_patients": data.get("n_patients"),
                })
            ctx["data"] = {
                "rows": rows,
                "slope_difference": data.get("slope_difference"),
                "difference_se": data.get("difference_se"),
                "p_value": data.get("p_value"),
                "converged": data.get("converged"),
            }
        elif data and "error" in data:
            ctx["error"] = data["error"]
        else:
            ctx["data"] = data
    except Exception as exc:
        ctx["error"] = str(exc)
    return render(request, "clinic/egfr_slope_results.html", ctx)


@login_required(login_url=LOGIN)
def cif_results(request):
    """Competing-risks CIF at a specified timepoint."""
    group_by = request.GET.get("group_by", "diabetes")
    try:
        at_days = int(request.GET.get("at_days", 365))
    except ValueError:
        at_days = 365
    ctx = {"active": "analytics", "group_by": group_by, "at_days": at_days,
           "group_options": ["diabetes", "diagnosis", "cohort"]}
    try:
        from analytics.services.cohort import cohort_competing_risks
        data = cohort_competing_risks(Patient.objects.all(), group_by, at_days=at_days)
        cif_key = f"cif_at_{at_days}d"
        rows = []
        for g in data.get("groups", []):
            rows.append({
                "label": g.get("label"),
                "n": g.get("n"),
                "n_kidney_events": g.get("n_kidney_events"),
                "n_competing_deaths": g.get("n_competing_deaths"),
                "cif": g.get(cif_key),
                "final_cif": g.get("final_cif"),
            })
        ctx["data"] = {
            "rows": rows,
            "comparison": data.get("comparison"),
        }
    except Exception as exc:
        ctx["error"] = str(exc)
    return render(request, "clinic/cif_results.html", ctx)

"""
Analytics endpoints:

  /analytics/patient/<patient_id>/outcome/   -> individual patient outcome (JSON)
  /analytics/cohort/survival/                -> KM + log-rank for a grouping (JSON)
       ?group_by=drug:sglt2i&endpoint=composite_kidney_event
  /analytics/cohort/survival/plot/           -> same, rendered as an SVG KM plot
  /analytics/cohort/summary/                 -> per-group baseline/outcome counts
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from labs.models import LabResult
from patients.models import Patient

from .models import PatientOutcome
from .services.cohort import (cohort_competing_risks, cohort_egfr_slope,
                              cohort_summary, cohort_survival, cox_regression)
from .services.outcomes import compute_patient_outcome
from .services.km_plot import render_km_svg

DEFAULT_ENDPOINT = "composite_kidney_event"
DEFAULT_GROUP_BY = "diabetes"


@login_required
def patient_outcome(request, patient_id):
    patient = get_object_or_404(Patient, patient_id=patient_id)
    if request.GET.get("recompute") == "1" or not hasattr(patient, "outcome"):
        compute_patient_outcome(patient)
    o = PatientOutcome.objects.filter(patient=patient).first()
    if o is None:
        raise Http404("No outcome computed.")
    egfr_series = [
        {"date": str(r.result_date), "egfr": float(r.value_numeric)}
        for r in LabResult.series(patient, "egfr") if r.value_numeric is not None]
    return JsonResponse({
        "patient": patient.patient_id, "name": patient.name,
        "index_date": str(o.index_date) if o.index_date else None,
        "followup_days": o.followup_days,
        "baseline_egfr": _f(o.baseline_egfr), "latest_egfr": _f(o.latest_egfr),
        "egfr_slope_per_year": _f(o.egfr_slope), "n_egfr": o.n_egfr,
        "endpoints": {
            "sustained_40_decline": _ev(o.sustained_40_decline, o.sustained_40_date),
            "sustained_50_decline": _ev(o.sustained_50_decline, o.sustained_50_date),
            "doubling_creatinine": _ev(o.doubling_creatinine, o.doubling_date),
            "eskd": _ev(o.eskd, o.eskd_date),
            "death": _ev(o.death, o.death_date),
            "composite_kidney_event": _ev(o.composite_kidney_event, o.composite_date,
                                          o.composite_cause),
        },
        "proteinuria": {
            "measure": "g/day (24-h UTP preferred, spot UPCR fallback)",
            "source": o.proteinuria_source,
            "remission_definition": o.remission_definition,
            "baseline": _f(o.baseline_upcr), "nadir": _f(o.nadir_upcr),
            "latest": _f(o.latest_upcr),
            "best_reduction_pct": _f(o.best_proteinuria_reduction_pct),
            "remission_status": o.remission_status,
            "complete_remission": _ev(o.complete_remission, o.complete_remission_date),
            "partial_remission": _ev(o.partial_remission, o.partial_remission_date),
            "igan_proteinuria_response": _ev(o.igan_proteinuria_response,
                                             o.igan_proteinuria_response_date),
            "relapse": _ev(o.proteinuria_relapse, o.proteinuria_relapse_date),
        },
        "any_relapse": o.any_relapse,
        "egfr_series": egfr_series,
        "proteinuria_series": [
            {"date": str(r.result_date), "value": float(r.value_numeric),
             "test": r.test.code}
            for code in ("utp_24h", "upcr")
            for r in LabResult.series(patient, code) if r.value_numeric is not None],
    }, json_dumps_params={"indent": 2})


def _serialize_cohort(cohort):
    return {
        "endpoint": cohort.endpoint, "group_by": cohort.group_by,
        "logrank": cohort.logrank,
        "groups": [{
            "label": g.label, "n": g.n, "n_events": g.n_events,
            "person_years": g.person_years,
            "incidence_per_100py": g.incidence_per_100py,
            "median_survival_days": g.median_survival_days,
            "km": g.km_as_dicts(),
        } for g in cohort.groups],
    }


@login_required
def cohort_survival_view(request):
    group_by = request.GET.get("group_by", DEFAULT_GROUP_BY)
    endpoint = request.GET.get("endpoint", DEFAULT_ENDPOINT)
    cohort = cohort_survival(Patient.objects.all(), group_by, endpoint)
    return JsonResponse(_serialize_cohort(cohort),
                        json_dumps_params={"indent": 2})


@login_required
def cohort_survival_plot(request):
    group_by = request.GET.get("group_by", DEFAULT_GROUP_BY)
    endpoint = request.GET.get("endpoint", DEFAULT_ENDPOINT)
    cohort = cohort_survival(Patient.objects.all(), group_by, endpoint)
    return HttpResponse(render_km_svg(cohort), content_type="image/svg+xml")


@login_required
def cohort_cox_view(request):
    """Multivariable Cox PH. e.g.
    /analytics/cohort/cox/?covariates=age,diabetes,drug:sglt2i&endpoint=composite_kidney_event
    """
    endpoint = request.GET.get("endpoint", DEFAULT_ENDPOINT)
    raw = request.GET.get("covariates", "age,diabetes,baseline_egfr")
    covariates = [c.strip() for c in raw.split(",") if c.strip()]
    try:
        result, meta = cox_regression(Patient.objects.all(), covariates, endpoint)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({**meta, "model": result},
                        json_dumps_params={"indent": 2})


@login_required
def cohort_egfr_slope_view(request):
    group_by = request.GET.get("group_by", DEFAULT_GROUP_BY)
    return JsonResponse(cohort_egfr_slope(Patient.objects.all(), group_by),
                        json_dumps_params={"indent": 2})


@login_required
def cohort_cif_view(request):
    group_by = request.GET.get("group_by", DEFAULT_GROUP_BY)
    try:
        at_days = int(request.GET.get("at_days", 365))
    except (TypeError, ValueError):
        return JsonResponse({"error": "at_days must be an integer."}, status=400)
    return JsonResponse(
        cohort_competing_risks(Patient.objects.all(), group_by, at_days=at_days),
        json_dumps_params={"indent": 2})


@login_required
def cohort_summary_view(request):
    group_by = request.GET.get("group_by", DEFAULT_GROUP_BY)
    return JsonResponse(
        {"group_by": group_by,
         "rows": cohort_summary(Patient.objects.all(), group_by)},
        json_dumps_params={"indent": 2})


def _f(d):
    return float(d) if d is not None else None


def _ev(flag, date, cause=None):
    out = {"occurred": bool(flag), "date": str(date) if date else None}
    if cause is not None:
        out["cause"] = cause
    return out

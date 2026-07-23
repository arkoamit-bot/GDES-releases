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

from .dashboard_data import (compliance_summary, outcomes_summary,
                             overview_stats)
from .models import PatientOutcome
from .services.cohort import (cohort_competing_risks, cohort_egfr_slope,
                              cohort_summary, cohort_survival, cox_regression)
from .services.outcomes import compute_patient_outcome
from .services.km_plot import render_km_svg
from .services.prediction import predict_from_patient
from .services.quality import (biopsy_yield, phase_distribution,
                               remission_concordance, relapse_rate)

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


# ---------------------------------------------------------------------------
# Sprint 3 — Dashboard & patient-level endpoints
# ---------------------------------------------------------------------------


@login_required
def dashboard(request):
    """Consolidated clinical dashboard — overview, disease distribution,
    outcome summaries, quality metrics, and compliance snapshot."""
    from clinical_reasoning.models import ClinicalProfile
    from django.db.models import Count

    # Disease distribution from ClinicalProfile (via Patient primary_diagnosis)
    disease_qs = (
        Patient.objects
        .exclude(primary_diagnosis="")
        .values("primary_diagnosis")
        .annotate(count=Count("pk"))
        .order_by("-count")
    )
    disease_distribution = [
        {"diagnosis": row["primary_diagnosis"], "count": row["count"]}
        for row in disease_qs
    ]

    return JsonResponse({
        "overview": overview_stats(),
        "disease_distribution": disease_distribution,
        "outcomes": outcomes_summary(),
        "quality_metrics": {
            "remission_concordance": remission_concordance(),
            "biopsy_yield": biopsy_yield(),
            "relapse_rate": relapse_rate(),
            "phase_distribution": phase_distribution(),
        },
        "compliance": compliance_summary(),
    }, json_dumps_params={"indent": 2})


@login_required
def patient_trajectory(request, patient_id):
    """Longitudinal patient trajectory — eGFR, proteinuria, treatment
    timeline, care gaps, and current pathway stage."""
    import datetime as dt

    patient = get_object_or_404(Patient, patient_id=patient_id)

    # 24-month lookback
    cutoff = dt.date.today() - dt.timedelta(days=730)

    # eGFR values (last 24 months)
    egfr_values = [
        {"date": str(r.result_date), "egfr": float(r.value_numeric)}
        for r in LabResult.series(patient, "egfr")
        if r.value_numeric is not None and r.result_date >= cutoff
    ]

    # Proteinuria values (last 24 months via utp_24h or upcr)
    proteinuria_values = [
        {"date": str(r.result_date), "value": float(r.value_numeric),
         "test": r.test.code}
        for code in ("utp_24h", "upcr")
        for r in LabResult.series(patient, code)
        if r.value_numeric is not None and r.result_date >= cutoff
    ]

    # Treatment timeline (from prescriptions)
    from prescriptions.models import Prescription

    rx_qs = (
        Prescription.objects
        .filter(encounter__patient=patient, status="final")
        .select_related("encounter")
        .order_by("encounter__encounter_date")
    )
    treatment_timeline = []
    for rx in rx_qs:
        items = [
            {
                "drug": str(i.drug.generic_name),
                "dose": i.dose,
                "frequency": i.frequency,
                "route": i.route,
            }
            for i in rx.items.all()
        ]
        treatment_timeline.append({
            "encounter_date": str(rx.encounter.encounter_date),
            "version": rx.version,
            "diagnosis": rx.diagnosis_text,
            "items": items,
        })

    # Care gaps (using clinical_reasoning cares pathway)
    from clinical_reasoning.models import ClinicalProfile
    from clinical_reasoning.services.care_pathway import detect_care_gaps

    # Build features dict from patient data and optional profile
    features = {
        "disease_phase": patient.current_phase if hasattr(patient, "current_phase") else "",
        "latest_egfr": None,
        "proteinuria": "none",
        "biopsy": [],
    }
    outcome = getattr(patient, "outcome", None)
    if outcome:
        features["latest_egfr"] = (
            float(outcome.latest_egfr) if outcome.latest_egfr else None
        )
        prot = outcome.baseline_upcr or outcome.latest_upcr
        if prot and float(prot) > 0:
            features["proteinuria"] = "present"
    try:
        profile = ClinicalProfile.objects.get(patient=patient)
        features["features"] = list(profile.features_snapshot.keys())
    except ClinicalProfile.DoesNotExist:
        pass

    care_gaps = detect_care_gaps(patient, features)

    # Pathway stage (using cares pathway engine)
    from clinical_reasoning.services.care_pathway_engine import (
        determine_current_stage,
    )

    pathway_stage = determine_current_stage(
        patient, features, disease_id=patient.primary_diagnosis or None,
    )

    return JsonResponse({
        "patient_id": patient.patient_id,
        "egfr": egfr_values,
        "proteinuria": proteinuria_values,
        "treatment_timeline": treatment_timeline,
        "care_gaps": care_gaps,
        "pathway_stage": pathway_stage,
    }, json_dumps_params={"indent": 2})


@login_required
def predict_survival(request, patient_id):
    """Predict kidney survival for a given patient."""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    result = predict_from_patient(patient)
    return JsonResponse(result, json_dumps_params={"indent": 2})


def _f(d):
    return float(d) if d is not None else None


def _ev(flag, date, cause=None):
    out = {"occurred": bool(flag), "date": str(date) if date else None}
    if cause is not None:
        out["cause"] = cause
    return out

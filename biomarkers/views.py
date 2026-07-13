"""
Biomarker endpoints:

  /biomarkers/patient/<patient_id>/    -> a patient's biomarker kinetics (JSON)
  /biomarkers/pla2r-predictor/         -> Study 6 predictor analysis (JSON)
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404

from patients.models import Patient

from .models import BiomarkerKinetics
from .services.kinetics import compute_biomarker_kinetics
from .services.predictor import pla2r_remission_predictor


def _f(d):
    return float(d) if d is not None else None


@login_required
def patient_biomarkers(request, patient_id):
    p = get_object_or_404(Patient, patient_id=patient_id)
    if request.GET.get("recompute") == "1" or not hasattr(p, "biomarker_kinetics"):
        compute_biomarker_kinetics(p)
    bk = BiomarkerKinetics.objects.filter(patient=p).first()
    if bk is None:
        raise Http404("No biomarker kinetics.")
    return JsonResponse({
        "patient": p.patient_id,
        "anti_pla2r": {
            "baseline": _f(bk.pla2r_baseline), "nadir": _f(bk.pla2r_nadir),
            "latest": _f(bk.pla2r_latest), "pct_decline": _f(bk.pla2r_pct_decline),
            "decline_50pct": {"reached": bk.pla2r_50pct_decline,
                              "date": str(bk.pla2r_50pct_date) if bk.pla2r_50pct_date else None,
                              "days_from_baseline": bk.pla2r_50pct_days},
            "immunological_remission": {
                "reached": bk.pla2r_immunological_remission,
                "date": str(bk.pla2r_remission_date) if bk.pla2r_remission_date else None},
            "early_responder_90d": bk.early_pla2r_responder(),
        },
        "complement_recovery": {
            "c3": {"recovered": bk.c3_recovered,
                   "date": str(bk.c3_recovered_date) if bk.c3_recovered_date else None},
            "c4": {"recovered": bk.c4_recovered,
                   "date": str(bk.c4_recovered_date) if bk.c4_recovered_date else None}},
        "anti_dsdna": {"baseline": _f(bk.dsdna_baseline), "latest": _f(bk.dsdna_latest),
                       "normalized": bk.dsdna_normalized,
                       "date": str(bk.dsdna_normalized_date) if bk.dsdna_normalized_date else None},
    }, json_dumps_params={"indent": 2})


@login_required
def pla2r_predictor(request):
    try:
        within = int(request.GET.get("within_days", 90))
    except (TypeError, ValueError):
        return JsonResponse({"error": "within_days must be an integer."}, status=400)
    return JsonResponse(
        pla2r_remission_predictor(Patient.objects.all(), within_days=within),
        json_dumps_params={"indent": 2})

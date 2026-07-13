"""
Pathology review endpoints:

  /pathology/biopsy/<id>/review/      -> review status + concordance (JSON)
  /pathology/discordant/              -> biopsies needing adjudication
  /pathology/agreement/               -> inter-observer kappa (§11.3)
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Biopsy, PathologyReview
from .services.agreement import interobserver_agreement
from .services.review import concordance


def _review_dict(r):
    return {"role": r.role, "diagnosis": r.diagnosis, "broad_group": r.broad_group,
            "mest": {"M": r.mest_m, "E": r.mest_e, "S": r.mest_s,
                     "T": r.mest_t, "C": r.mest_c},
            "isn_rps_class": r.isn_rps_class, "fsgs_variant": r.fsgs_variant,
            "reviewer": str(r.reviewer) if r.reviewer else None,
            "is_final": r.is_final}


@login_required
def biopsy_review(request, pk):
    b = get_object_or_404(Biopsy, pk=pk)
    return JsonResponse({
        "biopsy": b.pk, "patient": b.patient.patient_id,
        "review_status": b.review_status,
        "reviews": [_review_dict(r) for r in b.reviews.all()],
        "concordance": concordance(b),
    }, json_dumps_params={"indent": 2})


@login_required
def discordant(request):
    qs = Biopsy.objects.filter(review_status=Biopsy.ReviewStatus.DISCORDANT)
    return JsonResponse({
        "n": qs.count(),
        "biopsies": [{"biopsy": b.pk, "patient": b.patient.patient_id,
                      "discordant_fields": concordance(b)["discordant_fields"]}
                     for b in qs.select_related("patient")],
    }, json_dumps_params={"indent": 2})


@login_required
def agreement(request):
    return JsonResponse(interobserver_agreement(), json_dumps_params={"indent": 2})

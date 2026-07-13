"""
Safety endpoints:

  /safety/summary/?group_by=...            -> adverse-event summary (JSON)
  /safety/infection-incidence/?group_by=diabetes   -> infection rate by group
  /safety/study/<code>/                    -> per-arm SAE counts for the DSMB
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from patients.models import Patient
from studies.models import Study

from .services.summary import infection_incidence, safety_summary, study_safety


@login_required
def summary(request):
    return JsonResponse(safety_summary(Patient.objects.all()),
                        json_dumps_params={"indent": 2})


@login_required
def infection_incidence_view(request):
    group_by = request.GET.get("group_by", "diabetes")
    return JsonResponse(infection_incidence(Patient.objects.all(), group_by),
                        json_dumps_params={"indent": 2})


@login_required
def study_safety_view(request, code):
    study = get_object_or_404(Study, code=code)
    return JsonResponse(study_safety(study), json_dumps_params={"indent": 2})

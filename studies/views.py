"""
Study endpoints:

  /studies/<code>/dashboard/   -> CONSORT-style enrollment funnel + arm balance (JSON)

Outcome analysis by arm is handled by the analytics app, e.g.
  /analytics/cohort/survival/plot/?group_by=study:ADVANCED-DKD-IGAN&endpoint=composite_kidney_event
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Study
from .services.randomization import study_dashboard


@login_required
def dashboard(request, code):
    study = get_object_or_404(Study, code=code)
    return JsonResponse(study_dashboard(study), json_dumps_params={"indent": 2})

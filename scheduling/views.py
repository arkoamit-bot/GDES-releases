"""
Scheduling endpoints:

  /scheduling/due/?as_of=YYYY-MM-DD        -> visits currently due (in window)
  /scheduling/overdue/                     -> scheduled visits past their window
  /scheduling/roster/?date=YYYY-MM-DD      -> a clinic day's roster + capacity
  /scheduling/monitoring/<patient_id>/     -> immunosuppression monitoring labs due
"""
from django.contrib.auth.decorators import login_required
import datetime as dt

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from patients.models import Patient

from .services.monitoring import (is_on_active_immunosuppression,
                                  monitoring_requirements)
from .services.schedule import clinic_roster, due_visits, overdue_visits


def _parse(d):
    """Parse an ISO date query param; ignore malformed input (treat as absent)."""
    if not d:
        return None
    try:
        return dt.date.fromisoformat(d)
    except ValueError:
        return None


def _visit_dict(v):
    return {"patient": v.patient.patient_id, "label": v.label, "kind": v.kind,
            "target_date": str(v.target_date), "clinic_date": str(v.clinic_date),
            "window": [str(v.window_start), str(v.window_end)]}


@login_required
def due(request):
    as_of = _parse(request.GET.get("as_of"))
    return JsonResponse({"as_of": str(as_of or dt.date.today()),
                         "visits": [_visit_dict(v) for v in due_visits(as_of)]},
                        json_dumps_params={"indent": 2})


@login_required
def overdue(request):
    as_of = _parse(request.GET.get("as_of"))
    return JsonResponse({"as_of": str(as_of or dt.date.today()),
                         "visits": [_visit_dict(v) for v in overdue_visits(as_of)]},
                        json_dumps_params={"indent": 2})


@login_required
def roster(request):
    d = _parse(request.GET.get("date")) or dt.date.today()
    return JsonResponse(clinic_roster(d), json_dumps_params={"indent": 2})


@login_required
def monitoring(request, patient_id):
    p = get_object_or_404(Patient, patient_id=patient_id)
    return JsonResponse({
        "patient": p.patient_id,
        "on_active_immunosuppression": is_on_active_immunosuppression(p),
        "monitoring": monitoring_requirements(p),
    }, json_dumps_params={"indent": 2})

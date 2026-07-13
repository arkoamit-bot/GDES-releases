"""
Schedule generation and clinic management (protocol §7.6).

Routine timepoints: months 1, 3, 6, 9, 12, then 6-monthly to 5 years.
Early safety visits (weeks 1, 2, 4): only for patients on active immunosuppression
at enrolment. Each visit is snapped to the nearest Tuesday GN clinic within its
±7-day window, respecting the per-session capacity (default 15).
"""
from __future__ import annotations

import calendar
import datetime as dt

from django.conf import settings
from django.db import transaction

from scheduling.models import ScheduledVisit

ROUTINE_MONTHS = [1, 3, 6, 9, 12, 18, 24, 30, 36, 42, 48, 54, 60]
EARLY_SAFETY_WEEKS = [1, 2, 4]


def _cfg(key, default):
    return getattr(settings, "SCHEDULING", {}).get(key, default)


def _add_months(d, months):
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return dt.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def nearest_clinic_day(d):
    """Nearest clinic weekday (default Tuesday) to a date."""
    weekday = _cfg("clinic_weekday", 1)   # Mon=0 ... Tue=1
    offset = (d.weekday() - weekday) % 7
    prev_day = d - dt.timedelta(days=offset)
    next_day = prev_day + dt.timedelta(days=7)
    return prev_day if (d - prev_day) <= (next_day - d) else next_day


def _session_count(clinic_date):
    return ScheduledVisit.objects.filter(
        clinic_date=clinic_date,
        status__in=[ScheduledVisit.Status.SCHEDULED,
                    ScheduledVisit.Status.COMPLETED]).count()


def _assign_clinic_day(target, window_start, window_end):
    """Pick a clinic day in the window with spare capacity, closest to target."""
    capacity = _cfg("session_capacity", 15)
    # Candidate clinic days are the weekly clinic weekdays within the window.
    first = nearest_clinic_day(window_start)
    if first < window_start:
        first += dt.timedelta(days=7)
    candidates = []
    d = first
    while d <= window_end:
        candidates.append(d)
        d += dt.timedelta(days=7)
    if not candidates:
        candidates = [nearest_clinic_day(target)]
    # Prefer in-capacity days, ordered by closeness to the target timepoint.
    candidates.sort(key=lambda c: abs((c - target).days))
    for c in candidates:
        if _session_count(c) < capacity:
            return c
    return candidates[0]   # all full — overbook the closest (coordinator resolves)


@transaction.atomic
def generate_schedule(patient, anchor_date, *, immunosuppressed=False,
                      horizon_months=60):
    """Create the protocol-mandated ScheduledVisit rows for a patient."""
    window = _cfg("window_days", 7)
    created = []

    def _make(kind, label, target):
        ws = target - dt.timedelta(days=window)
        we = target + dt.timedelta(days=window)
        clinic = _assign_clinic_day(target, ws, we)
        visit, was_new = ScheduledVisit.objects.get_or_create(
            patient=patient, label=label,
            defaults=dict(kind=kind, target_date=target, window_start=ws,
                          window_end=we, clinic_date=clinic))
        if was_new:
            created.append(visit)

    if immunosuppressed:
        for w in EARLY_SAFETY_WEEKS:
            _make(ScheduledVisit.Kind.EARLY_SAFETY, f"Week {w}",
                  anchor_date + dt.timedelta(weeks=w))
    for m in ROUTINE_MONTHS:
        if m <= horizon_months:
            _make(ScheduledVisit.Kind.ROUTINE, f"Month {m}", _add_months(anchor_date, m))
    return created


def due_visits(as_of=None):
    as_of = as_of or dt.date.today()
    return [v for v in ScheduledVisit.objects.filter(status=ScheduledVisit.Status.SCHEDULED)
            if v.is_due(as_of)]


def overdue_visits(as_of=None):
    as_of = as_of or dt.date.today()
    return list(ScheduledVisit.objects.filter(
        status=ScheduledVisit.Status.SCHEDULED, window_end__lt=as_of))


def clinic_roster(clinic_date):
    """All visits booked into a given clinic day, with capacity headroom."""
    visits = list(ScheduledVisit.objects.filter(clinic_date=clinic_date)
                  .exclude(status=ScheduledVisit.Status.CANCELLED)
                  .select_related("patient"))
    capacity = _cfg("session_capacity", 15)
    return {"clinic_date": str(clinic_date), "capacity": capacity,
            "booked": len(visits), "over_capacity": len(visits) > capacity,
            "patients": [{"patient": v.patient.patient_id, "label": v.label,
                          "kind": v.kind, "status": v.status} for v in visits]}


def complete_visit(visit, encounter):
    visit.status = ScheduledVisit.Status.COMPLETED
    visit.encounter = encounter
    if encounter.encounter_date:
        visit.clinic_date = encounter.encounter_date
    visit.save(update_fields=["status", "encounter", "clinic_date"])
    return visit


def mark_missed(as_of=None):
    """Flag scheduled visits whose window has fully passed as missed."""
    as_of = as_of or dt.date.today()
    qs = ScheduledVisit.objects.filter(
        status=ScheduledVisit.Status.SCHEDULED, window_end__lt=as_of)
    return qs.update(status=ScheduledVisit.Status.MISSED)

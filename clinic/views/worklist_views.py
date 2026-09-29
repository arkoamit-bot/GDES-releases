"""Worklist / scheduling views.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    LOGIN,
    login_required,
    render,
)


@login_required(login_url=LOGIN)
def worklist_page(request):
    """Coordinator worklist: overdue + due follow-up visits and today's clinic
    roster — the scheduling engine's output rendered as a page instead of JSON.
    Every query is defensive so a sparse DB never 500s the page."""
    import datetime as _dt
    from scheduling.services.schedule import due_visits, overdue_visits, clinic_roster

    as_of = request.GET.get("as_of")
    try:
        today = _dt.date.fromisoformat(as_of) if as_of else _dt.date.today()
    except ValueError:
        today = _dt.date.today()

    def _safe(fn, default):
        try:
            return fn()
        except Exception:
            return default

    due = _safe(lambda: list(due_visits(today)), [])
    overdue = _safe(lambda: list(overdue_visits(today)), [])
    roster = _safe(lambda: clinic_roster(today), None)
    return render(request, "clinic/worklist.html", {
        "active": "worklist", "today": today,
        "due": due, "overdue": overdue, "roster": roster,
    })

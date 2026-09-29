"""The selected next appointment: one command, whichever screen sets it.

The visit's ``next_due_date`` is the clinician's selected next appointment.
The follow-up engine (followup.services.engine) regenerates the VISIT_DUE
task and its reminders from it whenever the encounter changes, and the
prescription prints it -- so there is one date, and every consumer agrees.

It is distinct from the research protocol's target dates and windows
(scheduling.ScheduledVisit), which this command never touches, and from a
suggestion (e.g. "4 weeks from today") that has not been chosen.

Previously the prescription screen always proposed today + 4 weeks and wrote
whatever came back onto the visit, so opening and saving a prescription
silently replaced a date chosen on the follow-up form.
"""
from __future__ import annotations

import datetime as dt

DEFAULT_SUGGESTION_WEEKS = 4


def _as_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def suggested_next_visit(today=None):
    return (today or dt.date.today()) + dt.timedelta(weeks=DEFAULT_SUGGESTION_WEEKS)


def set_next_visit(encounter, new_date, *, user=None, reason="", source="") -> bool:
    """Set (or clear) the selected next appointment. Returns True if changed.

    The change is audited with the actor and a reason; the encounter save
    triggers the follow-up engine, which moves the reminder with it.
    """
    from audit.local import acting_as, current_actor

    new_date = _as_date(new_date)
    if encounter.next_due_date == new_date:
        return False
    old = encounter.next_due_date
    why = (reason or "").strip() or (
        f"Next visit {'set' if old is None else 'changed'} from "
        f"{source or 'visit'}: {old or '-'} -> {new_date or '-'}")
    encounter.next_due_date = new_date
    with acting_as(user or current_actor(), reason=why[:240]):
        encounter.save(update_fields=["next_due_date"])
    return True

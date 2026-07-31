"""What to show of the differential, and when to show nothing.

The rule engine always produces a full ranking -- every disease with a non-zero
score, which for a typical patient is ten entries running down to 1-2%. Two
things made that useless on the patient page:

1. Once a biopsy has established the diagnosis, a ranked list of alternatives
   is not a differential any more. Showing "FSGS 21%" above nine other
   possibilities, for a patient whose histology says FSGS, understates a
   confirmed finding and invites doubt where there is none. This is the mirror
   of not asking for a histological class before the biopsy exists.

2. Below a few percent the entries are scoring noise -- a single weak rule
   firing -- and they crowd out the two or three candidates worth weighing.

So: suppress the ranking once the diagnosis is confirmed, and otherwise show
the candidates that are actually in contention. Nothing is deleted; the full
ranking stays in ClinicalProfile.differential for audit and export.
"""
from __future__ import annotations

# Below this the entry reflects one weak rule firing, not a real candidate.
MIN_CONFIDENCE = 5
# More than this and it is a list to scroll, not a differential to weigh.
MAX_ENTRIES = 5


def biopsy_diagnosis(patient) -> str:
    """The histological diagnosis, or "" when no biopsy establishes one."""
    if patient is None:
        return ""
    try:
        biopsy = (patient.biopsies.select_related("diagnosis")
                  .order_by("-biopsy_date").first())
    except Exception:  # pragma: no cover - relation unavailable
        return ""
    if biopsy is None:
        return ""
    diagnosis = getattr(biopsy, "diagnosis", None)
    name = getattr(diagnosis, "diagnosis", "") if diagnosis else ""
    if name:
        return name
    # Level 2 mirror, for biopsies recorded before the diagnosis was structured.
    return (getattr(patient, "biopsy_diagnosis", "") or "").strip()


def differential_for_display(patient, differential) -> dict:
    """Decide what the patient page should show.

    Returns:
        confirmed      histological diagnosis, or "" if the case is undiagnosed
        entries        candidates worth weighing (empty once confirmed)
        hidden_count   how many entries were left out
        note           one line explaining the omission, or ""
    """
    entries = list(differential or [])
    total = len(entries)

    confirmed = biopsy_diagnosis(patient)
    if confirmed:
        return {
            "confirmed": confirmed,
            "entries": [],
            "hidden_count": total,
            "note": ("Diagnosis established on biopsy — the pre-biopsy "
                     "differential is no longer clinically relevant."),
        }

    ranked = [d for d in entries if (d.get("confidence") or 0) >= MIN_CONFIDENCE]
    shown = ranked[:MAX_ENTRIES]
    hidden = total - len(shown)
    note = ""
    if hidden > 0:
        note = f"{hidden} lower-scoring possibilit{'y' if hidden == 1 else 'ies'} not shown."
    return {
        "confirmed": "",
        "entries": shown,
        "hidden_count": hidden,
        "note": note,
    }

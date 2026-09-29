"""
Taper support for finite drug courses — systemic corticosteroids above all.

Why this exists: an oral steroid course stopped abruptly can suppress or
trigger adrenal crisis, and nephrology patients on long courses (prednisolone,
methylprednisolone) are exactly the group that gets them. So the prescription
has to carry the step-down plan, not leave it in the prescriber's head.

Design rules, deliberately conservative:

*   The SCHEDULE is always clinician-authored. Taper templates
    (`prescriptions.TaperTemplate`, managed in Admin) are editable starting
    points, never an auto-computed dose ladder — taper steps depend on
    indication, dose, duration and prior exposure, so the prescriber stays in
    control and the printed text is always something a human approved.
*   Only SYSTEMIC steroids are flagged. Many formulary rows are
    `drug_class == "steroid"` but are really topical/ophthalmic combination
    drops (e.g. "Dexamethasone + Neomycin"), where tapering is meaningless.
    A combination product ("+") or a non-systemic route is excluded.
*   Courses marked "continue" (maintenance) are not taper candidates.
"""
from __future__ import annotations

import re

from treatments.models import DrugClass

# Routes that put a corticosteroid into the systemic circulation. Anything
# else (TOP, INH, SL, ...) is local therapy and has no HPA axis to protect.
SYSTEMIC_STEROID_ROUTES = frozenset({"PO", "IV", "IM", "SC"})

# Rows whose generic name joins agents with "+" are combination products —
# fixed-ratio drops/creams, not a single titratable steroid.
_COMBINATION = re.compile(r"\s*\+\s*")


def is_systemic_steroid(drug) -> bool:
    """True for a single-agent corticosteroid given by a systemic route.

    Guards against the formulary's combination eye drops / creams that carry
    `drug_class == "steroid"` but must never be taper candidates. A missing
    default route is treated as oral, matching PrescriptionItem.route_value —
    forgetting the route on a new steroid must not silently hide its taper
    panel, and the panel is opt-in anyway.
    """
    if drug is None or drug.drug_class != DrugClass.STEROID:
        return False
    if _COMBINATION.search(drug.generic_name or ""):
        return False
    route = (getattr(drug, "default_route", "") or "PO").strip().upper()
    return route in SYSTEMIC_STEROID_ROUTES


def course_length_days(duration: str) -> int | None:
    """Best-effort course length from a free-text duration.

    Returns None when the duration is open-ended ("continue", "long term") or
    too vague to convert. Deliberately conservative: unknown -> no warning, so
    the safety check never nags on a maintenance drug.
    """
    text = (duration or "").strip().lower()
    if not text:
        return None
    if "continu" in text or "long" in text or "indefinite" in text or "ongoing" in text:
        return None
    number = re.search(r"(\d+(?:\.\d+)?)", text)
    if not number:
        return None
    value = float(number.group(1))
    if "day" in text:
        return int(round(value))
    if "week" in text:
        return int(round(value * 7))
    if "month" in text:
        return int(round(value * 30))
    return None


# Courses longer than this generally need a documented step-down.
TAPER_COURSE_DAYS = 21


def needs_taper(item) -> bool:
    """A steroid line that should carry taper instructions but has none.

    Requires a systemic single-agent steroid on a finite course longer than
    three weeks. Everything else (short courses, maintenance therapy, topical
    or combination products) is left alone.
    """
    if not is_systemic_steroid(item.drug):
        return False
    if (item.taper_notes or "").strip():
        return False
    route = item.route_value
    if route not in SYSTEMIC_STEROID_ROUTES:
        return False
    days = course_length_days(item.duration)
    return days is not None and days > TAPER_COURSE_DAYS

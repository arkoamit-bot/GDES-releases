"""The ISN/RPS class is stated once, on the diagnosis.

The biopsy form asked for it twice: the diagnosis dropdown carries the class
("Lupus nephritis class III") and the lupus panel has its own ISN/RPS class
select. Two selects for one fact, so a mis-click produced a record that said
class III in one place and class IV in another -- with no way to tell which the
pathologist meant, and with Patient.isn_rps_class and the CDS disease mapping
each reading a different one.

The diagnosis wins, because it is the field the rest of the system keys off
(GNDiagnosis.diagnosis drives the remission rules, the management plan and the
analytics). The panel's class is derived from it. When the diagnosis is
unqualified ("Lupus nephritis") the panel is the one place the class is stated,
and the diagnosis is upgraded to match -- so the two can never disagree in
either direction.
"""
from __future__ import annotations

import re

BASE_DIAGNOSIS = "Lupus nephritis"

# Every class the diagnosis list can express, including the mixed lesions.
# Ordered longest-first so "III+V" is matched before "III".
CLASSES: list[str] = ["III+V", "IV+V", "III", "IV", "VI", "II", "I", "V"]

_CLASS_RE = re.compile(
    r"lupus nephritis\s+class\s+(?P<cls>[IV]+(?:\s*\+\s*[IV]+)?)\s*$",
    re.IGNORECASE)


def is_lupus(diagnosis: str) -> bool:
    return BASE_DIAGNOSIS.lower() in (diagnosis or "").lower()


def class_from_diagnosis(diagnosis: str) -> str:
    """"Lupus nephritis class III+V" -> "III+V"; "" when the diagnosis does not
    state a class (including non-lupus diagnoses)."""
    match = _CLASS_RE.search((diagnosis or "").strip())
    if not match:
        return ""
    cls = re.sub(r"\s*", "", match.group("cls")).upper()
    return cls if cls in CLASSES else ""


def diagnosis_for_class(cls: str) -> str:
    """"III" -> "Lupus nephritis class III"; "" when the class is unknown."""
    cls = (cls or "").strip().upper()
    return f"{BASE_DIAGNOSIS} class {cls}" if cls in CLASSES else ""


def reconcile(diagnosis: str, panel_class: str) -> tuple[str, str, str]:
    """Return (diagnosis, isn_rps_class, error).

    * diagnosis states a class -> it is copied to the panel.
    * diagnosis unqualified, panel states one -> the diagnosis is upgraded.
    * both state a class and they differ -> error, and nothing is changed.
      A contradiction is never resolved silently: only the pathologist knows
      which reading is right.
    """
    diagnosis = (diagnosis or "").strip()
    panel_class = (panel_class or "").strip().upper()

    if not is_lupus(diagnosis):
        return diagnosis, panel_class, ""

    from_dx = class_from_diagnosis(diagnosis)

    if from_dx and panel_class and from_dx != panel_class:
        return diagnosis, panel_class, (
            f"The diagnosis says ISN/RPS class {from_dx} but the lupus panel "
            f"says class {panel_class}. Correct one of them — the class must be "
            f"stated once."
        )

    if from_dx:
        return diagnosis, from_dx, ""

    if panel_class:
        upgraded = diagnosis_for_class(panel_class)
        return (upgraded or diagnosis), panel_class, ""

    return diagnosis, panel_class, ""

"""
Eligibility screening — a pluggable registry of per-study criteria functions.

A criteria function takes a Patient and returns a list of failure reasons
(empty list == eligible). Register one per study code; studies without a
registered function are treated as open (eligible) and rely on manual screening.

The flagship ADVANCED-DKD-IgAN criteria are encoded as a worked example; add
more the same way as protocols are finalised.
"""
from __future__ import annotations

ELIGIBILITY: dict = {}


def register_eligibility(study_code):
    def deco(fn):
        ELIGIBILITY[study_code] = fn
        return fn
    return deco


def _master_reasons(patient):
    """Master-protocol criteria applied to every study (protocol §6.1).
    Strictly adult-only: age >= 18 at screening."""
    reasons = []
    if patient.dob:
        import datetime as dt
        today = dt.date.today()
        age = (today.year - patient.dob.year
               - ((today.month, today.day) < (patient.dob.month, patient.dob.day)))
        if age < 18:
            reasons.append("Age < 18 (strictly adult-only protocol)")
    return reasons


def screen(study, patient):
    """Return (eligible: bool, reasons: list[str]). Applies the adult-only master
    criteria plus any study-specific criteria."""
    reasons = _master_reasons(patient)
    fn = ELIGIBILITY.get(study.code)
    if fn:
        reasons += list(fn(patient))
    return (len(reasons) == 0, reasons)


# --- worked examples from the BGDDR portfolio --------------------------------
@register_eligibility("ADVANCED-DKD-IGAN")
def _advanced_dkd_igan(patient):
    """Study 25: biopsy-proven IgAN + diabetes + eGFR < 30."""
    reasons = []
    if "iga" not in (patient.primary_diagnosis or "").lower():
        reasons.append("Not biopsy-proven IgA nephropathy")
    if patient.diabetes_status == "none":
        reasons.append("No diabetes")
    if patient.latest_egfr is None or patient.latest_egfr >= 30:
        reasons.append("eGFR not < 30 mL/min/1.73m2")
    return reasons


@register_eligibility("HCQ-IGAN-ADVANCED")
def _hcq_igan_advanced(patient):
    """Study 1: IgAN with eGFR 15-30."""
    reasons = []
    if "iga" not in (patient.primary_diagnosis or "").lower():
        reasons.append("Not IgA nephropathy")
    egfr = patient.latest_egfr
    if egfr is None or not (15 <= egfr < 30):
        reasons.append("eGFR not in 15-30 range")
    return reasons

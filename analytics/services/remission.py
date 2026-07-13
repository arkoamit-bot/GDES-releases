"""
Proteinuria-remission definitions — disease-specific, per the GN Master Protocol
(§9.1) and KDIGO 2021/2025. Proteinuria is in g/day (24-h UTP preferred; spot
UPCR g/g used as a ~g/day-equivalent fallback).

Thresholds (all g/day unless noted), centralised so they can be frozen/reviewed:

  complete remission      < 0.3 g/day                         (KDIGO 2021, all GN)
  lupus complete response < 0.5 g/day + eGFR within 10% of    (KDIGO LN)
                          baseline (15% if baseline reduced),
                          assessed at the remission timepoint
  partial remission       >= 50% reduction from baseline AND  (KDIGO 2021)
                          < 3.5 g/day (sub-nephrotic)
  IgAN proteinuria        >= 30% relative reduction OR < 0.3  (protocol §9.1,
   response               g/day                                KDIGO 2025; 0.5 target)
  relapse                 >= 1.0 g/day after remission         (loss of remission)
"""
from __future__ import annotations

COMPLETE = 0.3
LUPUS_COMPLETE = 0.5
NEPHROTIC = 3.5
PARTIAL_REDUCTION = 0.50
IGAN_RESPONSE_REDUCTION = 0.30
IGAN_TARGET = 0.5
RELAPSE = 1.0

# Lupus complete renal response also requires preserved kidney function: eGFR at
# the remission timepoint within 10% of baseline (15% if baseline eGFR was
# already reduced), per KDIGO.
LUPUS_EGFR_TOL_NORMAL = 0.10
LUPUS_EGFR_TOL_REDUCED = 0.15
EGFR_NORMAL_CUTOFF = 60


def egfr_preserved(baseline_egfr, egfr_value):
    """eGFR within KDIGO tolerance of baseline (10% if baseline normal, 15% if
    reduced). Missing values do not block (cannot assess)."""
    if baseline_egfr is None or egfr_value is None:
        return True
    tol = (LUPUS_EGFR_TOL_REDUCED if baseline_egfr < EGFR_NORMAL_CUTOFF
           else LUPUS_EGFR_TOL_NORMAL)
    return egfr_value >= baseline_egfr * (1 - tol)


def disease_key(diagnosis_text: str) -> str:
    """Map a free-text GN diagnosis to a remission-rule key."""
    d = (diagnosis_text or "").lower()
    if "lupus" in d or d.strip() in {"ln"}:
        return "lupus"
    if "iga" in d:                       # IgA nephropathy / IgA vasculitis nephritis
        return "igan"
    if "membranous" in d or "pla2r" in d:
        return "mn"
    if "fsgs" in d or "focal segmental" in d:
        return "fsgs"
    if "minimal change" in d or d.strip() in {"mcd"}:
        return "mcd"
    if "anca" in d or "vasculitis" in d or "aav" in d:
        return "aav"
    return "other"


def complete_predicate(disease, baseline):
    """Value predicate for sustained complete remission of proteinuria
    (non-lupus). Lupus uses lupus_complete_predicate (date-aware)."""
    return lambda v: v < COMPLETE


def lupus_complete_predicate(baseline_egfr, egfr_at):
    """Date-aware predicate(date, value) for lupus complete renal response:
    proteinuria < 0.5 g/day AND eGFR at that date preserved vs baseline.
    ``egfr_at(date)`` returns the contemporaneous eGFR."""
    def pred(date, value):
        return value < LUPUS_COMPLETE and egfr_preserved(baseline_egfr, egfr_at(date))
    return pred


def partial_predicate(disease, baseline):
    """Predicate for sustained partial remission (>=50% reduction & sub-nephrotic)."""
    if not baseline or baseline <= 0:
        return lambda v: False
    return lambda v: (v < NEPHROTIC) and (v <= (1 - PARTIAL_REDUCTION) * baseline)


def igan_response_predicate(baseline):
    """IgAN proteinuria response: >=30% relative reduction OR complete (<0.3)."""
    def pred(v):
        if v < COMPLETE:
            return True
        return bool(baseline) and v <= (1 - IGAN_RESPONSE_REDUCTION) * baseline
    return pred

"""
Study 6 — does an early (>=50%) anti-PLA2R decline predict later remission in
membranous nephropathy? Builds the 2x2 table of early-responder vs 12-month
complete (proteinuria) remission and reports sensitivity/specificity/PPV/NPV and
the relative risk of remission.
"""
from __future__ import annotations

from analytics.models import PatientOutcome
from biomarkers.models import BiomarkerKinetics


def _had_remission(outcome, window_days):
    if not outcome or not outcome.complete_remission:
        return False
    if outcome.complete_remission_date and outcome.index_date:
        return (outcome.complete_remission_date - outcome.index_date).days <= window_days
    return True   # remission achieved but dates incomplete


def _ratio(a, b):
    return round(a / b, 3) if b else None


def pla2r_remission_predictor(queryset, *, within_days=90, remission_window_days=395):
    tp = fp = fn = tn = 0
    bks = {bk.patient_id: bk for bk in BiomarkerKinetics.objects
           .filter(patient__in=queryset, pla2r_baseline__isnull=False)}
    outcomes = {o.patient_id: o for o in PatientOutcome.objects.filter(patient__in=queryset)}

    for pid, bk in bks.items():
        predictor = bk.early_pla2r_responder(within_days=within_days)
        remission = _had_remission(outcomes.get(pid), remission_window_days)
        if predictor and remission:
            tp += 1
        elif predictor and not remission:
            fp += 1
        elif (not predictor) and remission:
            fn += 1
        else:
            tn += 1

    n = tp + fp + fn + tn
    rr_exposed = _ratio(tp, tp + fp)        # remission rate in early responders
    rr_unexposed = _ratio(fn, fn + tn)      # remission rate in non-responders
    rr = round(rr_exposed / rr_unexposed, 2) if (rr_exposed and rr_unexposed) else None

    return {
        "predictor": f">=50% anti-PLA2R decline within {within_days} days",
        "outcome": f"complete remission within {remission_window_days} days",
        "n_with_pla2r": n,
        "table": {"TP": tp, "FP": fp, "FN": fn, "TN": tn},
        "sensitivity": _ratio(tp, tp + fn),
        "specificity": _ratio(tn, tn + fp),
        "ppv": _ratio(tp, tp + fp),
        "npv": _ratio(tn, tn + fn),
        "remission_rate_responders": rr_exposed,
        "remission_rate_nonresponders": rr_unexposed,
        "relative_risk": rr,
    }

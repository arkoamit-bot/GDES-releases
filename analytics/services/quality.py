"""
Quality-assessment & clinical-insight analytics (workflow steps 6–7).

Everything here is derived on read from the registry tables — biopsy yield,
predictors of a positive biopsy, response rates, relapse rates, and a
between-group comparison (response · complications · long-term remission ·
relapse patterns). No new state; safe to call any time.
"""
from __future__ import annotations

from collections import defaultdict

from django.db.models import Count

from patients.models import Patient
from patients.workflow import BiopsyResult, DiseasePhase


def _pct(num, den):
    return round(100.0 * num / den, 1) if den else 0.0


# --------------------------------------------------------------------------- #
# Clinical vs biochemical remission concordance
# --------------------------------------------------------------------------- #
# The 3-level remission scale, worst → best, shared by both assessments.
_REM_CATS = ["none", "partial", "complete"]
_REM_LABEL = {"none": "No remission", "partial": "Partial", "complete": "Complete"}
_RESP_RANK = {"none": 0, "partial": 1, "complete": 2}  # clinician response → scale


def remission_concordance():
    """Agreement between the clinician's per-visit response assessment and the
    lab-derived remission (the hybrid model's payoff). Builds the 3×3 matrix,
    the raw agreement, and Cohen's κ over registered patients where BOTH are
    assessable."""
    from encounters.models import ClinicalEncounter

    patients = list(Patient.objects.filter(registration_status="registered")
                    .select_related("outcome"))
    # Best clinician-assessed remission per patient (complete > partial > none).
    best_resp = {}
    for e in ClinicalEncounter.objects.filter(
            patient__in=patients, clinician_response__in=_RESP_RANK).values(
            "patient", "clinician_response"):
        r = _RESP_RANK[e["clinician_response"]]
        if r > best_resp.get(e["patient"], -1):
            best_resp[e["patient"]] = r
    rank_to_cat = {v: k for k, v in _RESP_RANK.items()}

    # 3×3 count matrix, rows = clinician, cols = lab.
    idx = {c: i for i, c in enumerate(_REM_CATS)}
    mat = [[0, 0, 0] for _ in _REM_CATS]
    n = 0
    for p in patients:
        o = getattr(p, "outcome", None)
        if o is None or p.pk not in best_resp:
            continue
        clin = rank_to_cat[best_resp[p.pk]]
        lab = o.remission_status or "none"
        if lab not in idx:
            continue
        mat[idx[clin]][idx[lab]] += 1
        n += 1

    agree = sum(mat[i][i] for i in range(3))
    row_tot = [sum(mat[i]) for i in range(3)]
    col_tot = [sum(mat[i][j] for i in range(3)) for j in range(3)]
    po = agree / n if n else 0.0
    pe = sum((row_tot[i] / n) * (col_tot[i] / n) for i in range(3)) if n else 0.0
    kappa = round((po - pe) / (1 - pe), 3) if n and pe != 1 else None

    rows = [{"label": _REM_LABEL[c], "cells": mat[i], "total": row_tot[i]}
            for i, c in enumerate(_REM_CATS)]
    return {
        "n": n,
        "col_labels": [_REM_LABEL[c] for c in _REM_CATS],
        "rows": rows,
        "col_totals": col_tot,
        "agreement_pct": _pct(agree, n),
        "kappa": kappa,
        "kappa_strength": _kappa_strength(kappa),
    }


def _kappa_strength(k):
    """Landis & Koch interpretation of Cohen's κ."""
    if k is None:
        return "—"
    if k < 0.0:
        return "poor (< chance)"
    if k < 0.20:
        return "slight"
    if k < 0.40:
        return "fair"
    if k < 0.60:
        return "moderate"
    if k < 0.80:
        return "substantial"
    return "almost perfect"


# --------------------------------------------------------------------------- #
# Biopsy yield  (step 7: diagnostic efficiency)
# --------------------------------------------------------------------------- #
def biopsy_yield():
    """Overall biopsy yield + a breakdown by clinical indication (which
    indications are the best predictors of a positive biopsy)."""
    from pathology.models import Biopsy

    qs = Biopsy.objects.all()
    total = qs.count()
    scored = qs.exclude(result_category="")
    n_scored = scored.count()
    counts = {k: 0 for k, _ in BiopsyResult.choices}
    for row in scored.values("result_category").annotate(n=Count("id")):
        counts[row["result_category"]] = row["n"]
    positive = counts.get(BiopsyResult.POSITIVE, 0)

    # Predictor table: yield per indication.
    by_ind = defaultdict(lambda: {"total": 0, "positive": 0})
    for b in scored.values("indication", "result_category"):
        row = by_ind[b["indication"] or "—"]
        row["total"] += 1
        if b["result_category"] == BiopsyResult.POSITIVE:
            row["positive"] += 1
    from patients.workflow import BiopsyIndication
    ind_label = dict(BiopsyIndication.choices)
    indications = sorted(
        ({"indication": ind_label.get(k, k or "Unspecified"),
          "total": v["total"], "positive": v["positive"],
          "yield_pct": _pct(v["positive"], v["total"])}
         for k, v in by_ind.items()),
        key=lambda r: (-r["yield_pct"], -r["total"]))

    return {
        "total_biopsies": total,
        "scored": n_scored,
        "unscored": total - n_scored,
        "positive": positive,
        "negative": counts.get(BiopsyResult.NEGATIVE, 0),
        "inconclusive": counts.get(BiopsyResult.INCONCLUSIVE, 0),
        "yield_pct": _pct(positive, n_scored),
        "indications": indications,
    }


# --------------------------------------------------------------------------- #
# Phase / response / relapse snapshots
# --------------------------------------------------------------------------- #
def phase_distribution():
    """Registered patients by current disease phase."""
    label = dict(DiseasePhase.choices)
    rows = (Patient.objects.filter(registration_status="registered")
            .exclude(current_phase="")
            .values("current_phase").annotate(n=Count("id")))
    out = [{"phase": label.get(r["current_phase"], r["current_phase"]),
            "n": r["n"]} for r in rows]
    return sorted(out, key=lambda r: -r["n"])


def _person_years(patients):
    days = 0
    for p in patients:
        o = getattr(p, "outcome", None)
        if o and o.followup_days:
            days += o.followup_days
    return days / 365.25 if days else 0.0


def relapse_rate(patients=None):
    """Relapse burden: patients with ≥1 relapse, total relapses, and the rate
    per 100 patient-years of follow-up."""
    from encounters.models import RelapseEpisode

    if patients is None:
        patients = list(Patient.objects.filter(registration_status="registered")
                        .select_related("outcome"))
    ids = [p.pk for p in patients]
    rel = RelapseEpisode.objects.filter(patient_id__in=ids)
    total = rel.count()
    with_relapse = rel.values("patient").distinct().count()
    py = _person_years(patients)
    return {
        "patients": len(patients),
        "with_relapse": with_relapse,
        "with_relapse_pct": _pct(with_relapse, len(patients)),
        "total_relapses": total,
        "person_years": round(py, 1),
        "rate_per_100py": round(100.0 * total / py, 1) if py else 0.0,
    }


# --------------------------------------------------------------------------- #
# Between-group comparison  (response · complications · remission · relapse)
# --------------------------------------------------------------------------- #
GROUPERS = {
    "diagnosis": ("Diagnosis", lambda p: p.get_primary_diagnosis_display() or "—"),
    "diabetes": ("Diabetes", lambda p: p.get_diabetes_status_display()),
    "phase": ("Phase", lambda p: p.get_current_phase_display() or "—"),
    "sex": ("Sex", lambda p: p.get_sex_display()),
}


def group_comparison(group_by="diagnosis"):
    """One row per group with the headline metrics the clinic compares."""
    from encounters.models import RelapseEpisode
    from safety.models import AdverseEvent

    label, keyfn = GROUPERS.get(group_by, GROUPERS["diagnosis"])
    patients = list(
        Patient.objects.filter(registration_status="registered")
        .select_related("outcome"))

    # Pre-count relapses & AEs per patient in two queries.
    rel_by_pt = defaultdict(int)
    for r in RelapseEpisode.objects.filter(
            patient__in=patients).values("patient").annotate(n=Count("id")):
        rel_by_pt[r["patient"]] = r["n"]
    ae_by_pt = defaultdict(lambda: [0, 0])  # [all, serious]
    for a in AdverseEvent.objects.filter(patient__in=patients).values(
            "patient", "serious"):
        ae_by_pt[a["patient"]][0] += 1
        if a["serious"]:
            ae_by_pt[a["patient"]][1] += 1

    groups = defaultdict(list)
    for p in patients:
        groups[keyfn(p)].append(p)

    rows = []
    for name, members in groups.items():
        n = len(members)
        any_rem = sum(1 for p in members
                      if getattr(p, "outcome", None) and p.outcome.any_remission)
        complete = sum(1 for p in members
                       if getattr(p, "outcome", None) and p.outcome.complete_remission)
        relapses = sum(rel_by_pt.get(p.pk, 0) for p in members)
        with_rel = sum(1 for p in members if rel_by_pt.get(p.pk, 0))
        aes = sum(ae_by_pt.get(p.pk, [0, 0])[0] for p in members)
        saes = sum(ae_by_pt.get(p.pk, [0, 0])[1] for p in members)
        py = _person_years(members)
        rows.append({
            "group": name, "n": n,
            "any_remission_pct": _pct(any_rem, n),
            "complete_remission_pct": _pct(complete, n),
            "with_relapse_pct": _pct(with_rel, n),
            "relapse_per_100py": round(100.0 * relapses / py, 1) if py else 0.0,
            "ae_per_patient": round(aes / n, 2) if n else 0.0,
            "sae": saes,
            "person_years": round(py, 1),
        })
    return {
        "group_label": label,
        "rows": sorted(rows, key=lambda r: -r["n"]),
    }

"""
The outcome engine — derive a PatientOutcome from raw longitudinal data with
operational endpoint definitions fixed in code.

Operational definitions (the registry's section-2.2 principle, encoded here):

  index date          enrollment_date, else earliest lab/encounter date
  baseline eGFR/Cr    first value on/after index
  sustained >=40%     first eGFR <= 60% of baseline that stays <= that level on
                      every subsequent measurement (i.e. a confirmed, sustained
                      drop, not a single transient dip)
  sustained >=50%     same, threshold 50% of baseline
  doubling Cr         first creatinine >= 2x baseline that stays >= on all later
  ESKD / death        from dated ClinicalEvent rows
  composite kidney    earliest of {ESKD, sustained >=40% decline, death}
  proteinuria         g/day; 24-h UTP preferred, spot UPCR (g/g) as fallback
  remission           DISEASE-SPECIFIC (services/remission.py, per protocol
                      §9.1 + KDIGO 2021/2025): complete < 0.3 g/day (lupus
                      < 0.5 + preserved eGFR); partial >=50% reduction & < 3.5;
                      IgAN response >=30% reduction or < 0.3. Sustained, with
                      FIRST-achieved dates -> true time-to-event endpoints.
  composite kidney    earliest of {ESKD (dialysis/transplant or eGFR < 15),
                      >=50% eGFR decline, renal death}  (protocol §9.2)
  proteinuria relapse first proteinuria >= 1.0 g/day after remission achieved
  last contact        latest of any lab / encounter / event date

These thresholds are intentionally simple and centralised so they can be
reviewed and frozen before enrolment — change them here, re-run, done.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from encounters.models import ClinicalEncounter, ClinicalEvent
from labs.models import LabResult
from labs.services.results import egfr_slope
from patients.models import Patient

from analytics.models import PatientOutcome
from analytics.services import remission as R

ESKD_EGFR = 15   # eGFR < 15 mL/min/1.73m2 counts as kidney failure (KDIGO / protocol)


def _series(patient, code):
    return [(r.result_date, float(r.value_numeric))
            for r in LabResult.series(patient, code)
            if r.value_numeric is not None]


def _index_date(patient, egfr, creat):
    if patient.enrollment_date:
        return patient.enrollment_date
    candidates = [d for d, _ in egfr] + [d for d, _ in creat]
    enc = (ClinicalEncounter.objects.filter(patient=patient)
           .order_by("encounter_date").values_list("encounter_date", flat=True).first())
    if enc:
        candidates.append(enc)
    return min(candidates) if candidates else None


def _sustained_drop(series, baseline, frac):
    """First date value <= baseline*frac that stays <= on all later points."""
    threshold = baseline * frac
    for i, (d, v) in enumerate(series):
        if v <= threshold and all(vv <= threshold for _, vv in series[i:]):
            return d
    return None


def _sustained_rise(series, baseline, mult):
    threshold = baseline * mult
    for i, (d, v) in enumerate(series):
        if v >= threshold and all(vv >= threshold for _, vv in series[i:]):
            return d
    return None


def _proteinuria_series(patient, prefer_upcr=False):
    """Merged proteinuria series in g/day. Returns (series, source).

    Preference is disease-specific: most GN use **24-h UTP** as the primary
    measure (UPCR fills the gaps), but **lupus nephritis** is assessed on
    **UPCR** per KDIGO LN — so when ``prefer_upcr`` is set, spot UPCR (g/g,
    ~g/day-equivalent) is used whenever present and 24-h UTP fills the gaps."""
    utp = {d: v for d, v in _series(patient, "utp_24h")}
    upcr = {d: v for d, v in _series(patient, "upcr")}
    primary, primary_src = (upcr, "upcr") if prefer_upcr else (utp, "utp")
    backup, backup_src = (utp, "utp") if prefer_upcr else (upcr, "upcr")
    series, sources = [], set()
    for d in sorted(set(utp) | set(upcr)):
        if d in primary:
            series.append((d, primary[d])); sources.add(primary_src)
        else:
            series.append((d, backup[d])); sources.add(backup_src)
    source = "mixed" if len(sources) > 1 else (next(iter(sources)) if sources else "")
    return series, source


def _disease_key(patient):
    """Resolve the GN diagnosis (latest biopsy, else patient.primary_diagnosis)
    to a remission-rule key (igan / mn / fsgs / mcd / lupus / aav / other)."""
    from pathology.models import GNDiagnosis
    gd = (GNDiagnosis.objects.filter(biopsy__patient=patient)
          .select_related("biopsy").order_by("-biopsy__biopsy_date").first())
    text = gd.diagnosis if gd else patient.primary_diagnosis
    return R.disease_key(text or "")


def _egfr_at(egfr, date):
    """Contemporaneous eGFR for a date: the measurement nearest in time on either
    side. Ties prefer the value on/before the date. ``egfr`` is the (date, value)
    series."""
    if not egfr:
        return None
    # Sort key: closest by absolute day distance, then prefer on/before on ties.
    nearest = min(egfr, key=lambda dv: (abs((dv[0] - date).days), dv[0] > date))
    return nearest[1]


def _proteinuria_outcome(series, baseline, disease, egfr):
    """Disease-specific sustained remission dates, nadir, and best % reduction."""
    out = {"complete_date": None, "partial_date": None, "igan_date": None,
           "nadir": None, "best_reduction_pct": None}
    if not series:
        return out
    out["nadir"] = min(v for _, v in series)
    if baseline and baseline > 0:
        out["best_reduction_pct"] = max(
            0.0, (baseline - out["nadir"]) / baseline * 100.0)

    if disease == "lupus":
        # Complete renal response is date-aware: needs preserved eGFR at the
        # remission timepoint (KDIGO within 10-15% of baseline).
        baseline_egfr = egfr[0][1] if egfr else None
        pred = R.lupus_complete_predicate(baseline_egfr, lambda d: _egfr_at(egfr, d))
        out["complete_date"] = _first_sustained_dated(series, pred)
    else:
        out["complete_date"] = _first_sustained(
            series, R.complete_predicate(disease, baseline))
    out["partial_date"] = _first_sustained(
        series, R.partial_predicate(disease, baseline))
    if disease == "igan":
        out["igan_date"] = _first_sustained(
            series, R.igan_response_predicate(baseline))
    return out


def _first_sustained(series, predicate):
    """First date the predicate holds and continues to hold on every later
    measurement (a confirmed, sustained achievement — not a transient dip)."""
    for i, (d, v) in enumerate(series):
        if predicate(v) and all(predicate(vv) for _, vv in series[i:]):
            return d
    return None


def _first_sustained_dated(series, predicate):
    """Like _first_sustained but the predicate takes (date, value) — used where
    the rule depends on contemporaneous data (e.g. lupus eGFR preservation)."""
    for i, (d, v) in enumerate(series):
        if predicate(d, v) and all(predicate(dd, vv) for dd, vv in series[i:]):
            return d
    return None


def _proteinuria_relapse(series, after_date):
    """First proteinuria >= relapse threshold strictly after remission."""
    if not after_date:
        return None
    for d, v in series:
        if d > after_date and v >= R.RELAPSE:
            return d
    return None


def _last_contact(patient, *date_lists):
    dates = []
    for lst in date_lists:
        dates.extend(lst)
    enc = (ClinicalEncounter.objects.filter(patient=patient)
           .order_by("-encounter_date").values_list("encounter_date", flat=True).first())
    if enc:
        dates.append(enc)
    evt = (ClinicalEvent.objects.filter(patient=patient)
           .order_by("-event_date").values_list("event_date", flat=True).first())
    if evt:
        dates.append(evt)
    return max(dates) if dates else None


def _earliest(*pairs):
    """pairs: (date, cause) tuples; return (date, cause) with the min date."""
    present = [(d, c) for d, c in pairs if d]
    return min(present, key=lambda x: x[0]) if present else (None, "")


@transaction.atomic
def compute_patient_outcome(patient) -> PatientOutcome:
    egfr = _series(patient, "egfr")
    creat = _series(patient, "creatinine")
    # Lupus nephritis is assessed on UPCR (KDIGO LN); other GN prefer 24-h UTP.
    disease = _disease_key(patient)
    prot, prot_source = _proteinuria_series(patient, prefer_upcr=(disease == "lupus"))

    index_date = _index_date(patient, egfr, creat)
    baseline_egfr = egfr[0][1] if egfr else None
    baseline_creat = creat[0][1] if creat else None
    baseline_prot = prot[0][1] if prot else None

    # Kidney-function endpoints from the eGFR / creatinine trajectories.
    s40 = _sustained_drop(egfr, baseline_egfr, 0.60) if baseline_egfr else None
    s50 = _sustained_drop(egfr, baseline_egfr, 0.50) if baseline_egfr else None
    dbl = _sustained_rise(creat, baseline_creat, 2.0) if baseline_creat else None

    # Hard endpoints. ESKD = dialysis/transplant event OR sustained eGFR < 15.
    events = ClinicalEvent.objects.filter(patient=patient)
    eskd_evt = (events.filter(event_type__in=ClinicalEvent.HARD_KIDNEY)
                .order_by("event_date").first())
    death_evt = events.filter(event_type=ClinicalEvent.Type.DEATH).order_by("event_date").first()
    relapse = events.filter(event_type=ClinicalEvent.Type.RELAPSE).exists()
    eskd_egfr_date = _first_sustained(egfr, lambda v: v < ESKD_EGFR)
    eskd_date = _earliest(
        (eskd_evt.event_date if eskd_evt else None, "e"),
        (eskd_egfr_date, "g"))[0]
    death_date = death_evt.event_date if death_evt else None

    # Composite kidney endpoint = earliest of {ESKD, >=50% eGFR decline, renal
    # death} (protocol §9.2 / KDIGO).
    comp_date, comp_cause = _earliest(
        (eskd_date, "eskd"), (s50, "egfr_decline_50"), (death_date, "death"))

    last_contact = _last_contact(
        patient, [d for d, _ in egfr], [d for d, _ in creat], [d for d, _ in prot])

    # --- Proteinuria regression (the primary disease-activity outcome) -------
    # Disease-specific, sustained, with FIRST-achieved dates (so time-to-event).
    # (`disease` was resolved above to pick the right proteinuria measure.)
    pr = _proteinuria_outcome(prot, baseline_prot, disease, egfr)
    remission = (PatientOutcome.Remission.COMPLETE if pr["complete_date"]
                 else PatientOutcome.Remission.PARTIAL if pr["partial_date"]
                 else PatientOutcome.Remission.NONE)
    any_remission_date = _earliest(
        (pr["complete_date"], "c"), (pr["partial_date"], "p"))[0]
    relapse_date = _proteinuria_relapse(prot, any_remission_date)
    any_relapse = bool(relapse_date) or relapse

    followup_days = ((last_contact - index_date).days
                     if (index_date and last_contact) else None)

    defaults = dict(
        index_date=index_date,
        baseline_egfr=_dec(baseline_egfr, 1),
        baseline_creatinine=_dec(baseline_creat, 2),
        baseline_upcr=_dec(baseline_prot, 3),
        last_contact_date=last_contact,
        followup_days=followup_days,
        n_egfr=len(egfr),
        latest_egfr=_dec(egfr[-1][1], 1) if egfr else None,
        egfr_slope=_dec(egfr_slope(patient), 2),
        sustained_40_decline=bool(s40), sustained_40_date=s40,
        sustained_50_decline=bool(s50), sustained_50_date=s50,
        doubling_creatinine=bool(dbl), doubling_date=dbl,
        eskd=bool(eskd_date), eskd_date=eskd_date,
        death=bool(death_date), death_date=death_date,
        composite_kidney_event=bool(comp_date), composite_date=comp_date,
        composite_cause=comp_cause,
        remission_definition=disease, proteinuria_source=prot_source,
        latest_upcr=_dec(prot[-1][1], 3) if prot else None,
        nadir_upcr=_dec(pr["nadir"], 3),
        best_proteinuria_reduction_pct=_dec(pr["best_reduction_pct"], 1),
        complete_remission=bool(pr["complete_date"]), complete_remission_date=pr["complete_date"],
        partial_remission=bool(pr["partial_date"]), partial_remission_date=pr["partial_date"],
        any_remission_date=any_remission_date,
        igan_proteinuria_response=bool(pr["igan_date"]),
        igan_proteinuria_response_date=pr["igan_date"],
        proteinuria_relapse=bool(relapse_date), proteinuria_relapse_date=relapse_date,
        remission_status=remission, any_relapse=any_relapse,
    )
    outcome, _ = PatientOutcome.objects.update_or_create(
        patient=patient, defaults=defaults)
    return outcome


def _dec(value, places):
    if value is None:
        return None
    return Decimal(str(round(float(value), places)))


def compute_all_outcomes():
    n = 0
    for patient in Patient.objects.all():
        compute_patient_outcome(patient)
        n += 1
    return n

"""
Compute biomarker kinetics from the longitudinal LabResult series.

Thresholds (negative cut-offs / reference ranges) are read from the LabTest
catalog where possible, with sensible fallbacks.
"""
from __future__ import annotations

from decimal import Decimal

from labs.models import LabResult, LabTest
from patients.models import Patient

from biomarkers.models import BiomarkerKinetics

PLA2R_NEGATIVE_DEFAULT = 20.0     # RU/mL; below this = seronegative
DSDNA_NEGATIVE_DEFAULT = 30.0     # IU/mL


def _series(patient, code):
    return [(r.result_date, float(r.value_numeric))
            for r in LabResult.series(patient, code) if r.value_numeric is not None]


def _ref(code, attr, default):
    t = LabTest.objects.filter(code=code).first()
    val = getattr(t, attr, None) if t else None
    return float(val) if val is not None else default


def _first_date(series, predicate):
    for d, v in series:
        if predicate(v):
            return d
    return None


def antibody_kinetics(series, negative_threshold):
    """Return kinetics dict for a declining antibody, or None if no data."""
    if not series:
        return None
    baseline_date, baseline = series[0]
    latest = series[-1][1]
    nadir = min(v for _, v in series)
    pct = ((baseline - nadir) / baseline * 100.0) if baseline > 0 else None

    date50 = (_first_date(series, lambda v: v <= 0.5 * baseline)
              if baseline > 0 else None)
    days50 = (date50 - baseline_date).days if date50 else None
    neg_date = _first_date(series, lambda v: v < negative_threshold)
    return {
        "baseline": baseline, "baseline_date": baseline_date, "latest": latest,
        "nadir": nadir, "pct_decline": pct, "date50": date50, "days50": days50,
        "negative_date": neg_date,
    }


def _recovery_date(patient, code, ref_low):
    """First date a (typically low) complement value rises to/above its reference
    low — i.e. normalises."""
    series = _series(patient, code)
    if not series:
        return None
    return _first_date(series, lambda v: v >= ref_low)


def compute_biomarker_kinetics(patient) -> BiomarkerKinetics:
    pla2r = antibody_kinetics(_series(patient, "anti_pla2r"),
                              _ref("anti_pla2r", "ref_high", PLA2R_NEGATIVE_DEFAULT))
    dsdna = antibody_kinetics(_series(patient, "anti_dsdna"),
                              _ref("anti_dsdna", "ref_high", DSDNA_NEGATIVE_DEFAULT))
    c3_date = _recovery_date(patient, "c3", _ref("c3", "ref_low", 90.0))
    c4_date = _recovery_date(patient, "c4", _ref("c4", "ref_low", 10.0))

    defaults = dict(
        c3_recovered=bool(c3_date), c3_recovered_date=c3_date,
        c4_recovered=bool(c4_date), c4_recovered_date=c4_date,
    )
    if pla2r:
        defaults.update(
            pla2r_baseline=_d(pla2r["baseline"]), pla2r_baseline_date=pla2r["baseline_date"],
            pla2r_latest=_d(pla2r["latest"]), pla2r_nadir=_d(pla2r["nadir"]),
            pla2r_pct_decline=_d(pla2r["pct_decline"]),
            pla2r_50pct_decline=bool(pla2r["date50"]), pla2r_50pct_date=pla2r["date50"],
            pla2r_50pct_days=pla2r["days50"],
            pla2r_immunological_remission=bool(pla2r["negative_date"]),
            pla2r_remission_date=pla2r["negative_date"])
    if dsdna:
        defaults.update(
            dsdna_baseline=_d(dsdna["baseline"]), dsdna_latest=_d(dsdna["latest"]),
            dsdna_normalized=bool(dsdna["negative_date"]),
            dsdna_normalized_date=dsdna["negative_date"])

    obj, _ = BiomarkerKinetics.objects.update_or_create(
        patient=patient, defaults=defaults)
    return obj


def _d(value):
    return None if value is None else Decimal(str(round(float(value), 1)))


def compute_all_biomarkers():
    n = 0
    for patient in Patient.objects.all():
        compute_biomarker_kinetics(patient)
        n += 1
    return n

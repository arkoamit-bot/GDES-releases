"""
Recording lab results, the longitudinal way — plus the two automatic effects the
registry needs:

  1. Entering a creatinine auto-derives an eGFR result (CKD-EPI 2021, versioned).
  2. The patient's cached `latest_egfr` is refreshed from the newest eGFR, which
     is exactly what the prescription renal-safety check reads. Labs → safer Rx,
     closing the loop with no manual step.
"""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db import transaction

from labs.models import LabResult, LabTest
from .egfr import ckd_epi_2021

CREATININE_CODE = "creatinine"
EGFR_CODE = "egfr"


def _compute_flag(test: LabTest, value: Decimal) -> str:
    if value is None:
        return ""
    if test.ref_low is not None and value < test.ref_low:
        return LabResult.Flag.LOW
    if test.ref_high is not None and value > test.ref_high:
        return LabResult.Flag.HIGH
    return LabResult.Flag.NORMAL


def _patient_age(patient, on_date: dt.date) -> float | None:
    if not patient.dob:
        return None
    d = on_date
    return (d.year - patient.dob.year
            - ((d.month, d.day) < (patient.dob.month, patient.dob.day)))


def refresh_latest_egfr(patient):
    """Set patient.latest_egfr to the most recent eGFR result."""
    latest = (LabResult.objects
              .filter(patient=patient, test__code=EGFR_CODE,
                      value_numeric__isnull=False)
              .order_by("-result_date", "-created_at")
              .first())
    if latest:
        patient.latest_egfr = latest.value_numeric
        patient.save(update_fields=["latest_egfr", "updated_at"])
    return latest


@transaction.atomic
def record_result(patient, test_code, *, result_date, value_numeric=None,
                  value_text="", unit="", sample_date=None, order_item=None,
                  source=LabResult.Source.LAB, age_years=None):
    """Record one result. If it's a creatinine, also derive & store eGFR and
    refresh the patient's cached eGFR."""
    test = LabTest.objects.get(code=test_code)
    value = Decimal(str(value_numeric)) if value_numeric is not None else None

    result = LabResult.objects.create(
        patient=patient, test=test, order_item=order_item,
        value_numeric=value, value_text=value_text,
        unit=unit or test.default_unit, sample_date=sample_date,
        result_date=result_date, source=source,
        flag=_compute_flag(test, value) if value is not None else "",
    )

    if order_item is not None:
        order_item.order.refresh_status()

    if test_code == CREATININE_CODE and value is not None:
        _derive_egfr(patient, result, age_years=age_years)

    return result


def _derive_egfr(patient, creatinine_result, *, age_years=None):
    age = age_years if age_years is not None else _patient_age(
        patient, creatinine_result.result_date)
    if age is None:
        return None  # cannot compute without age; creatinine still recorded

    scr = float(creatinine_result.value_numeric)
    egfr_value, version = ckd_epi_2021(scr, age, patient.sex)
    egfr_test = LabTest.objects.get(code=EGFR_CODE)

    egfr_result = LabResult.objects.create(
        patient=patient, test=egfr_test,
        value_numeric=Decimal(str(egfr_value)),
        unit=egfr_test.default_unit, result_date=creatinine_result.result_date,
        sample_date=creatinine_result.sample_date,
        source=LabResult.Source.DERIVED,
        derived_from=creatinine_result, formula_version=version,
        flag=_compute_flag(egfr_test, Decimal(str(egfr_value))),
    )
    refresh_latest_egfr(patient)
    return egfr_result


def egfr_slope(patient, *, min_points=2):
    """Annualized eGFR slope (mL/min/1.73m^2 per year) via least-squares over the
    eGFR series. Returns None if too few points. A first cut at the auto-computed
    outcome the portfolio specifies — refine (e.g. mixed models) in analytics."""
    points = [(r.result_date, float(r.value_numeric))
              for r in LabResult.series(patient, EGFR_CODE)
              if r.value_numeric is not None]
    if len(points) < min_points:
        return None

    t0 = points[0][0]
    xs = [(d - t0).days / 365.25 for d, _ in points]
    ys = [v for _, v in points]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    return round(slope, 2)

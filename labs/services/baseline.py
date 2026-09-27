"""Which laboratory observation a baseline reports.

HbA1c used to be a number typed into the baseline form and stored on the
baseline row, unrelated to the longitudinal LabResult table: the same test
could hold two different values for the same day, and the export reported the
baseline copy. Now HbA1c is recorded through the laboratory service like any
other result, and the baseline LINKS the observation it reports
(BaselineAssessment.hba1c_result).

Enrollment window
-----------------
When no observation is linked explicitly, the baseline value is the current
result closest to the anchor date (the baseline assessment date, else the
enrollment date) within ENROLLMENT_WINDOW_BEFORE days before to
ENROLLMENT_WINDOW_AFTER days after it; on equal distance the earlier result
wins (a pre-treatment value). A result outside the window is never used, so a
recent result does not masquerade as the enrollment value. The selected
result's own date is always shown with it.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from labs.models import LabResult

ENROLLMENT_WINDOW_BEFORE = 90
ENROLLMENT_WINDOW_AFTER = 30


@dataclass
class BaselineValue:
    value: object = None
    date: dt.date | None = None
    source: str = ""            # "linked" | "window" | "legacy_field" | ""
    result: LabResult | None = None

    @property
    def label(self):
        return {"linked": "recorded at baseline", "window": "nearest to enrollment",
                "legacy_field": "legacy baseline field (not a lab record)"}.get(self.source, "")


def anchor_date(baseline=None, patient=None):
    if baseline is not None and baseline.assessment_date:
        return baseline.assessment_date
    patient = patient or getattr(baseline, "patient", None)
    return getattr(patient, "enrollment_date", None)


def select_baseline_observation(patient, code, anchor, *,
                                before=ENROLLMENT_WINDOW_BEFORE,
                                after=ENROLLMENT_WINDOW_AFTER):
    if anchor is None:
        return None
    lo, hi = anchor - dt.timedelta(days=before), anchor + dt.timedelta(days=after)
    candidates = list(LabResult.objects.filter(
        patient=patient, test__code=code, result_date__gte=lo, result_date__lte=hi)
        .order_by("result_date", "created_at", "id"))
    if not candidates:
        return None
    return min(candidates, key=lambda r: (abs((r.result_date - anchor).days),
                                          r.result_date > anchor))


def current_version(result):
    """Follow corrections forward to the current version of a result."""
    node = result
    while node is not None and not node.is_current:
        node = LabResult.all_objects.filter(supersedes=node).first()
    return node


def baseline_hba1c(baseline) -> BaselineValue:
    if baseline is None:
        return BaselineValue()
    linked = baseline.hba1c_result
    if linked is not None:
        cur = current_version(linked)
        if cur is not None:
            return BaselineValue(cur.value_numeric, cur.result_date, "linked", cur)
    picked = select_baseline_observation(baseline.patient, "hba1c",
                                         anchor_date(baseline))
    if picked is not None:
        return BaselineValue(picked.value_numeric, picked.result_date, "window", picked)
    if baseline.hba1c is not None:
        return BaselineValue(baseline.hba1c, baseline.assessment_date, "legacy_field", None)
    return BaselineValue()

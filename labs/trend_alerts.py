"""Lab trend alerts — detects concerning lab trajectories."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List

from django.db.models import QuerySet


@dataclass
class LabTrendAlert:
    code: str
    test_name: str
    severity: str  # "warning" | "critical"
    message: str
    current_value: float
    previous_value: float
    change_pct: float
    direction: str  # "rising" | "falling"


def detect_egfr_trends(patient, window_days: int = 90) -> List[LabTrendAlert]:
    """Detect concerning eGFR trends over the specified window."""
    from labs.models import LabResult
    alerts = []

    egfr_results = (
        LabResult.objects.filter(patient=patient, test__code__in=("egfr", "egfr_calc"))
        .order_by("-sample_date")[:10]
    )
    if len(egfr_results) < 2:
        return alerts

    latest = float(egfr_results[0].value_numeric or 0)
    previous = float(egfr_results[1].value_numeric or 0)
    if previous == 0:
        return alerts

    change_pct = ((latest - previous) / previous) * 100
    days_between = (egfr_results[0].result_date - egfr_results[1].result_date).days or 1

    # Rapid decline: >5 mL/min within 90 days
    if change_pct < -5 and days_between <= window_days:
        alerts.append(LabTrendAlert(
            code="egfr_rapid_decline",
            test_name="eGFR",
            severity="critical" if change_pct < -20 else "warning",
            message=f"eGFR declined {abs(change_pct):.1f}% over {days_between} days ({previous:.0f} → {latest:.0f})",
            current_value=latest,
            previous_value=previous,
            change_pct=change_pct,
            direction="falling",
        ))

    # CKD stage progression
    stages = [(90, "G1"), (60, "G2"), (45, "G3a"), (30, "G3b"), (15, "G4"), (0, "G5")]
    prev_stage = next((label for threshold, label in stages if previous >= threshold), "G5")
    curr_stage = next((label for threshold, label in stages if latest >= threshold), "G5")
    prev_idx = next(i for i, (_, label) in enumerate(stages) if label == prev_stage)
    curr_idx = next(i for i, (_, label) in enumerate(stages) if label == curr_stage)
    if curr_idx > prev_idx:
        alerts.append(LabTrendAlert(
            code="ckd_stage_progression",
            test_name="eGFR",
            severity="critical",
            message=f"CKD stage progressed from {prev_stage} to {curr_stage}",
            current_value=latest,
            previous_value=previous,
            change_pct=change_pct,
            direction="falling",
        ))

    return alerts


def detect_creatinine_trends(patient, window_days: int = 7) -> List[LabTrendAlert]:
    """Detect acute creatinine spikes (possible AKI)."""
    from labs.models import LabResult
    alerts = []

    cr_results = (
        LabResult.objects.filter(patient=patient, test__code__in=("creatinine", "scr"))
        .order_by("-sample_date")[:5]
    )
    if len(cr_results) < 2:
        return alerts

    latest = float(cr_results[0].value_numeric or 0)
    baseline = float(cr_results[1].value_numeric or 0)
    if baseline == 0:
        return alerts

    change_pct = ((latest - baseline) / baseline) * 100
    days_between = (cr_results[0].result_date - cr_results[1].result_date).days or 1

    # AKI criterion: >26.5 umol/L or >50% rise within 7 days
    if change_pct > 50 and days_between <= window_days:
        alerts.append(LabTrendAlert(
            code="creatinine_spike",
            test_name="Creatinine",
            severity="critical",
            message=f"Creatinine rose {change_pct:.1f}% in {days_between} days ({baseline:.1f} → {latest:.1f}) — possible AKI",
            current_value=latest,
            previous_value=baseline,
            change_pct=change_pct,
            direction="rising",
        ))

    return alerts


def detect_proteinuria_trends(patient) -> List[LabTrendAlert]:
    """Detect significant proteinuria changes."""
    from labs.models import LabResult
    alerts = []

    upcr_results = (
        LabResult.objects.filter(patient=patient, test__code__in=("upcr", "acr", "proteinuria"))
        .order_by("-sample_date")[:5]
    )
    if len(upcr_results) < 2:
        return alerts

    latest = float(upcr_results[0].value_numeric or 0)
    previous = float(upcr_results[1].value_numeric or 0)
    if previous == 0:
        return alerts

    change_pct = ((latest - previous) / previous) * 100

    # Nephrotic-range proteinuria appearing
    if latest >= 3.5 and previous < 3.5:
        alerts.append(LabTrendAlert(
            code="nephrotic_proteinuria_new",
            test_name="UPCR",
            severity="warning",
            message=f"Proteinuria reached nephrotic range ({latest:.2f} g/g, was {previous:.2f})",
            current_value=latest,
            previous_value=previous,
            change_pct=change_pct,
            direction="rising",
        ))

    # Significant proteinuria increase (>50%)
    if change_pct > 50 and latest >= 1.0:
        alerts.append(LabTrendAlert(
            code="proteinuria_increasing",
            test_name="UPCR",
            severity="warning",
            message=f"Proteinuria increased {change_pct:.1f}% ({previous:.2f} → {latest:.2f} g/g)",
            current_value=latest,
            previous_value=previous,
            change_pct=change_pct,
            direction="rising",
        ))

    return alerts


def detect_all_trends(patient) -> List[LabTrendAlert]:
    """Run all trend detectors and return combined alerts."""
    alerts = []
    alerts.extend(detect_egfr_trends(patient))
    alerts.extend(detect_creatinine_trends(patient))
    alerts.extend(detect_proteinuria_trends(patient))
    alerts.sort(key=lambda a: (0 if a.severity == "critical" else 1))
    return alerts

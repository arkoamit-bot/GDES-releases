"""Operational Intelligence — compliance analytics, gap trends, and operational dashboards."""
from __future__ import annotations

import logging
from collections import Counter
from datetime import date, timedelta
from typing import Any

from django.db.models import Count, Exists, OuterRef, Q

logger = logging.getLogger(__name__)


def compute_compliance_summary() -> dict:
    """Compute registry-wide compliance metrics using annotated aggregates."""
    from patients.models import Patient
    from pathology.models import Biopsy
    from treatments.models import TreatmentExposure
    from encounters.models import ClinicalEncounter

    total = Patient.objects.count()
    active = Patient.objects.exclude(registration_status="inactive").count()
    cutoff = date.today() - timedelta(days=180)

    has_biopsy = Exists(Biopsy.objects.filter(patient=OuterRef("pk")))
    has_active_tx = Exists(
        TreatmentExposure.objects.filter(patient=OuterRef("pk"), ongoing=True)
    )
    latest_encounter = (
        ClinicalEncounter.objects.filter(patient=OuterRef("pk"))
        .order_by("-encounter_date")
        .values("encounter_date")[:1]
    )
    has_recent_encounter = Exists(
        ClinicalEncounter.objects.filter(
            patient=OuterRef("pk"), encounter_date__gte=cutoff
        )
    )

    annotated = Patient.objects.annotate(
        has_biopsy=has_biopsy,
        has_active_tx=has_active_tx,
        latest_encounter_date=latest_encounter,
        has_recent_encounter=has_recent_encounter,
    )

    missing_biopsy_count = annotated.filter(has_biopsy=False).count()
    missing_egfr_count = annotated.filter(latest_egfr__isnull=True).count()
    active_without_tx_count = annotated.filter(
        current_phase="active", has_active_tx=False
    ).count()
    overdue_count = annotated.filter(
        Q(has_recent_encounter=False)
        | Q(latest_encounter_date__isnull=True)
    ).count()

    return {
        "total_patients": total,
        "active_patients": active,
        "lost_to_follow_up": _count_lost_to_follow_up(),
        "missing_biopsy": {"count": missing_biopsy_count, "pct": _pct(missing_biopsy_count, total)},
        "missing_egfr": {"count": missing_egfr_count, "pct": _pct(missing_egfr_count, total)},
        "active_without_treatment": {"count": active_without_tx_count, "pct": _pct(active_without_tx_count, total)},
        "overdue_visits": {"count": overdue_count, "pct": _pct(overdue_count, total)},
    }


def _count_lost_to_follow_up() -> dict:
    from patients.models import Patient
    count = Patient.objects.filter(registration_status="inactive").count()
    return {"count": count, "pct": _pct(count, Patient.objects.count())}


def _pct(n: int, total: int) -> float:
    return round(n / total * 100, 1) if total else 0.0


def compute_patient_compliance(patient) -> dict:
    """Compute individual patient compliance score."""
    score = 100
    reasons = []

    try:
        if not patient.biopsies.exists():
            score -= 15
            reasons.append("Missing renal biopsy")
    except Exception:
        pass

    if patient.latest_egfr is None:
        score -= 10
        reasons.append("Missing eGFR")

    try:
        latest = patient.encounters.order_by("-encounter_date").first()
        if latest is None:
            score -= 20
            reasons.append("No encounters recorded")
        elif latest.encounter_date and latest.encounter_date < date.today() - timedelta(days=180):
            score -= 15
            reasons.append("No encounter in last 6 months")
    except Exception:
        pass

    return {
        "patient_id": patient.patient_id,
        "compliance_score": max(0, score),
        "deductions": reasons,
        "deduction_count": len(reasons),
        "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 50 else "D",
    }


def compute_care_gap_trends() -> dict:
    """Analyze care gap trends across the registry."""
    from patients.models import Patient
    from clinical_reasoning.models import ClinicalProfile

    profiles = ClinicalProfile.objects.select_related("patient").all()
    gap_counts: Counter = Counter()
    disease_gaps: dict[str, Counter] = {}

    for profile in profiles:
        gaps = profile.care_pathway.get("care_gaps", []) if profile.care_pathway else []
        diagnosis = getattr(profile.patient, "primary_diagnosis", "unknown") or "unknown"

        if diagnosis not in disease_gaps:
            disease_gaps[diagnosis] = Counter()

        for gap in gaps:
            field = gap.get("field", "unknown")
            gap_counts[field] += 1
            disease_gaps[diagnosis][field] += 1

    return {
        "total_profiles": profiles.count(),
        "total_gaps": sum(gap_counts.values()),
        "gaps_per_field": dict(gap_counts.most_common()),
        "gaps_by_disease": {
            d: dict(c.most_common()) for d, c in disease_gaps.items()
        },
        "avg_gaps_per_patient": round(sum(gap_counts.values()) / max(profiles.count(), 1), 1),
    }

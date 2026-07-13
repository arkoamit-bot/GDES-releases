"""Disease trajectory assessment — evaluate disease course over time.

Replaces encounter-centric thinking with disease-centric longitudinal intelligence.
"""
from __future__ import annotations

from typing import Any


def assess_trajectory(patient, features: dict) -> dict:
    """Assess the overall disease trajectory for a patient.

    Combines eGFR trend, proteinuria trend, disease phase, and treatment
    response into a structured trajectory assessment.
    """
    egfr_trend = features.get("egfrTrend", "normal")
    proteinuria = features.get("proteinuria", "none")
    disease_phase = features.get("disease_phase", "")
    latest_egfr = features.get("latest_egfr") or getattr(patient, "latest_egfr", None)

    trajectory: dict[str, Any] = {
        "trend": "stable",
        "detail": "No significant change in disease status",
        "confidence": "low",
        "kidney_survival_estimate": _estimate_kidney_survival(latest_egfr),
    }

    # eGFR-based trajectory
    if egfr_trend == "rapidDecline":
        trajectory["trend"] = "declining"
        trajectory["detail"] = "Rapid eGFR decline — suggests active or progressive disease"
        trajectory["confidence"] = "moderate"
    elif egfr_trend == "reduced" and disease_phase not in ("remission", "eskd"):
        if proteinuria in ("nephrotic",):
            trajectory["trend"] = "declining"
            trajectory["detail"] = "Reduced eGFR with nephrotic-range proteinuria — active disease"
            trajectory["confidence"] = "high"
        else:
            trajectory["trend"] = "stable_but_compromised"
            trajectory["detail"] = "Stable but reduced kidney function — requires ongoing monitoring"
            trajectory["confidence"] = "moderate"

    # Remission detection
    if disease_phase == "remission":
        trajectory["trend"] = "improving"
        trajectory["detail"] = "Patient in remission phase — favourable trajectory"
        trajectory["confidence"] = "high"

    # ESKD detection
    if disease_phase == "eskd" or (latest_egfr is not None and latest_egfr < 15):
        trajectory["trend"] = "end_stage"
        trajectory["detail"] = "End-stage kidney disease — renal replacement therapy indicated"
        trajectory["confidence"] = "high"

    return trajectory


def estimate_remission_probability(features: dict) -> dict:
    """Estimate probability of achieving/maintaining remission."""
    disease_phase = features.get("disease_phase", "")
    proteinuria = features.get("proteinuria", "none")
    egfr_trend = features.get("egfrTrend", "normal")

    if disease_phase == "remission":
        relapse_risk = "low"
        if egfr_trend == "rapidDecline":
            relapse_risk = "moderate"
        if proteinuria == "nephrotic":
            relapse_risk = "high"
        return {
            "current_status": "in_remission",
            "relapse_risk": relapse_risk,
            "monitoring_interval": "3_months" if relapse_risk == "low" else "1_month",
        }

    if disease_phase == "active":
        remission_potential = "good"
        if egfr_trend == "rapidDecline":
            remission_potential = "guarded"
        if latest_egfr := features.get("latest_egfr") and features["latest_egfr"] < 30:
            remission_potential = "poor"
        return {
            "current_status": "active_disease",
            "remission_potential": remission_potential,
            "factors": ["Response to immunosuppression", "Baseline kidney function", "Proteinuria reduction"],
        }

    return {
        "current_status": "unknown",
        "remission_potential": "unknown",
    }


def _estimate_kidney_survival(latest_egfr) -> dict:
    """Estimate kidney survival based on current eGFR."""
    if latest_egfr is None:
        return {"status": "unknown", "message": "eGFR not available for survival estimation"}

    if latest_egfr >= 60:
        years_to_eskd = max(1, (latest_egfr - 15) / 3)
        return {
            "status": "favorable",
            "estimated_years_to_eskd": round(years_to_eskd, 1),
            "message": "Low risk of progression to ESKD in the near term",
        }
    elif latest_egfr >= 30:
        years_to_eskd = max(1, (latest_egfr - 15) / 4)
        return {
            "status": "moderate",
            "estimated_years_to_eskd": round(years_to_eskd, 1),
            "message": "Moderate risk — monitor eGFR trajectory closely",
        }
    elif latest_egfr >= 15:
        return {
            "status": "guarded",
            "estimated_years_to_eskd": 1.0,
            "message": "Advanced CKD — prepare for renal replacement therapy",
        }
    else:
        return {
            "status": "critical",
            "estimated_years_to_eskd": 0,
            "message": "ESKD — RRT indicated",
        }

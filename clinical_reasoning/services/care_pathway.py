"""Care Pathway Engine — actively determine care stage, gaps, and recommendations.

Automatically determines current stage of care, missing investigations,
pending labs, required vaccinations, monitoring schedule, and guideline deviations.
"""
from __future__ import annotations

import datetime as dt
from typing import Any


def detect_care_gaps(patient, features: dict) -> list[dict]:
    """Detect gaps in care for a patient.

    Returns a list of care gap dicts with field, importance, and message.
    """
    gaps = []
    disease_phase = features.get("disease_phase", "")

    # Core investigations
    gaps.extend(_check_core_investigations(features))

    # Monitoring gaps
    gaps.extend(_check_monitoring_gaps(patient, features, disease_phase))

    # Treatment-related gaps
    gaps.extend(_check_treatment_gaps(patient, features))

    return gaps


def _check_core_investigations(features: dict) -> list[dict]:
    """Check for missing core diagnostic investigations."""
    gaps = []
    if features.get("proteinuria") == "none":
        gaps.append({
            "field": "proteinuria",
            "importance": "high",
            "category": "investigation",
            "message": "Proteinuria not quantified — obtain UPCR or ACR",
            "recommendation": "Order spot UPCR or 24h urine protein",
        })
    if features.get("egfrTrend") == "normal" and features.get("latest_egfr") is None:
        gaps.append({
            "field": "egfr",
            "importance": "high",
            "category": "investigation",
            "message": "eGFR not available — essential for staging",
            "recommendation": "Order serum creatinine for eGFR calculation",
        })
    if "biopsy" not in features or not features.get("biopsy"):
        gaps.append({
            "field": "biopsy",
            "importance": "high",
            "category": "investigation",
            "message": "No biopsy findings — histology essential for definitive GN diagnosis",
            "recommendation": "Consider renal biopsy if not contraindicated",
        })
    return gaps


def _check_monitoring_gaps(patient, features: dict, disease_phase: str) -> list[dict]:
    """Check for monitoring gaps based on disease phase and activity."""
    gaps = []

    if disease_phase in ("active", "relapse"):
        # Active disease needs frequent monitoring
        gaps.append({
            "field": "monitoring_frequency",
            "importance": "high",
            "category": "monitoring",
            "message": "Active disease — monthly monitoring recommended",
            "recommendation": "Schedule monthly eGFR, proteinuria, and clinical assessment",
        })

    if features.get("egfrTrend") == "rapidDecline":
        gaps.append({
            "field": "egfr_monitoring",
            "importance": "high",
            "category": "monitoring",
            "message": "Rapid eGFR decline — close monitoring required",
            "recommendation": "Increase monitoring frequency to 2-4 weeks",
        })

    if features.get("proteinuria") == "nephrotic":
        gaps.append({
            "field": "nephrotic_monitoring",
            "importance": "high",
            "category": "monitoring",
            "message": "Nephrotic-range proteinuria — monitor for complications",
            "recommendation": "Monitor albumin, cholesterol, and screen for thrombosis",
        })

    # Check for overdue follow-up
    _check_follow_up_gap(patient, gaps)

    return gaps


def _check_follow_up_gap(patient, gaps: list) -> None:
    """Check if the patient is overdue for follow-up."""
    try:
        latest_encounter = patient.encounters.order_by("-encounter_date").first()
        if latest_encounter and latest_encounter.encounter_date:
            days_since = (dt.date.today() - latest_encounter.encounter_date).days
            if days_since > 180:
                gaps.append({
                    "field": "follow_up",
                    "importance": "high",
                    "category": "monitoring",
                    "message": f"No encounter in {days_since} days — patient may be lost to follow-up",
                    "recommendation": "Attempt to contact patient and schedule follow-up",
                })
            elif days_since > 90:
                gaps.append({
                    "field": "follow_up",
                    "importance": "medium",
                    "category": "monitoring",
                    "message": f"Last encounter {days_since} days ago — routine follow-up due",
                    "recommendation": "Schedule routine follow-up visit",
                })
    except Exception:
        pass


def _check_treatment_gaps(patient, features: dict) -> list[dict]:
    """Detect treatment-related gaps."""
    gaps = []
    disease_phase = features.get("disease_phase", "")

    if disease_phase == "active":
        try:
            from treatments.models import TreatmentExposure
            active_treatments = TreatmentExposure.objects.filter(
                patient=patient,
                end_date__isnull=True,
            )
            if not active_treatments.exists() and features.get("proteinuria") != "none":
                gaps.append({
                    "field": "treatment",
                    "importance": "high",
                    "category": "treatment",
                    "message": "Active disease without documented treatment",
                    "recommendation": "Review and initiate appropriate immunosuppression",
                })
        except Exception:
            pass

    # Vaccination gap
    gaps.append({
        "field": "vaccination",
        "importance": "medium",
        "category": "preventive",
        "message": "Check immunization status: pneumococcal, influenza, hepatitis B recommended in CKD",
        "recommendation": "Review and update vaccination history",
    })

    return gaps


def compute_monitoring_schedule(features: dict) -> dict:
    """Compute the recommended monitoring schedule based on patient status."""
    schedule = {
        "visits": "every_3_months",
        "labs": ["creatinine", "egfr", "upcr"],
        "next_visit": "3_months",
    }

    disease_phase = features.get("disease_phase", "")
    egfr_trend = features.get("egfrTrend", "normal")
    proteinuria = features.get("proteinuria", "none")

    if disease_phase in ("active", "relapse") or egfr_trend == "rapidDecline":
        schedule["visits"] = "every_2_4_weeks"
        schedule["labs"].extend(["c3", "c4", "ana", "dsdna"] if "lupus" in str(features.get("features", "")) else [])
        schedule["next_visit"] = "2_weeks"
    elif proteinuria == "nephrotic":
        schedule["visits"] = "every_1_2_months"
        schedule["labs"].extend(["albumin", "cholesterol"])
        schedule["next_visit"] = "1_month"

    return schedule

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
    gaps.extend(_check_core_investigations(patient, features))

    # Monitoring gaps
    gaps.extend(_check_monitoring_gaps(patient, features, disease_phase))

    # Treatment-related gaps
    gaps.extend(_check_treatment_gaps(patient, features))

    # Disease-specific gaps
    primary_disease = (getattr(patient, "primary_diagnosis", "") or "").lower()
    gaps.extend(_check_disease_specific_gaps(patient, features, primary_disease))

    return gaps


def _check_core_investigations(patient, features: dict) -> list[dict]:
    """Check for missing core diagnostic investigations."""
    gaps = []
    if features.get("proteinuria") == "none":
        # Only flag proteinuria quantification for suspected lupus nephritis,
        # where UTP is specifically recommended for remission evaluation.
        biopsy_flags = features.get("biopsy", [])
        disease_features = features.get("features", [])
        diagnosis = (getattr(patient, "primary_diagnosis", "") or "").lower()
        is_lupus = (
            "fullHouse" in biopsy_flags
            or "lupus" in diagnosis
            or "sle" in diagnosis
            or "lupus" in str(disease_features).lower()
        )
        if is_lupus:
            gaps.append({
                "field": "proteinuria",
                "importance": "high",
                "category": "investigation",
                "message": "Proteinuria not quantified — obtain UPCR or UTP for lupus nephritis remission assessment",
                "recommendation": "Order spot UPCR or 24h urine protein",
            })
    if features.get("latest_egfr") is None:
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


# ============================================================================
# Disease-Specific Care Gaps
# ============================================================================

DISEASE_SPECIFIC_GAPS: dict[str, list[dict]] = {
    "iga": [
        {
            "field": "tonsillectomy",
            "importance": "medium",
            "category": "treatment",
            "message": "Consider tonsillectomy if recurrent tonsillitis triggers hematuria flares",
            "recommendation": "Refer for ENT evaluation for tonsillectomy if recurrent tonsillitis",
        },
        {
            "field": "hematuria_monitoring",
            "importance": "medium",
            "category": "monitoring",
            "message": "Screen for hematuria flares — microscopic hematuria is a hallmark of IgA activity",
            "recommendation": "Include urinalysis with microscopy at each visit",
        },
    ],
    "membranous": [
        {
            "field": "pla2r_monitoring",
            "importance": "high",
            "category": "monitoring",
            "message": "Monitor PLA2R antibody titers every 3 months to assess disease activity and treatment response",
            "recommendation": "Order serum anti-PLA2R antibodies every 3 months",
        },
        {
            "field": "thromboembolism_screening",
            "importance": "high",
            "category": "monitoring",
            "message": "Screen for thromboembolism — membranous nephropathy carries high thrombotic risk",
            "recommendation": "Assess for DVT/PE symptoms and consider prophylactic anticoagulation if albumin <2.5 g/dL",
        },
    ],
    "lupus": [
        {
            "field": "complement_monitoring",
            "importance": "high",
            "category": "monitoring",
            "message": "Monitor complement C3/C4 levels — low complements indicate active lupus nephritis",
            "recommendation": "Order C3, C4 with each disease activity assessment",
        },
        {
            "field": "extra_renal_lupus",
            "importance": "medium",
            "category": "monitoring",
            "message": "Screen for extra-renal lupus activity (skin, joints, serositis, CNS)",
            "recommendation": "Perform comprehensive SLE activity assessment (e.g. SLEDAI)",
        },
    ],
    "anca": [
        {
            "field": "anca_titers",
            "importance": "high",
            "category": "monitoring",
            "message": "Monitor ANCA titers — rising titers may predict relapse",
            "recommendation": "Order ANCA serology (MPO/PR3) every 1-3 months",
        },
        {
            "field": "ent_involvement",
            "importance": "medium",
            "category": "monitoring",
            "message": "Check for ENT involvement — common in granulomatosis with polyangiitis",
            "recommendation": "Refer for ENT evaluation if sinonasal symptoms present",
        },
    ],
    "diabetic_nephropathy": [
        {
            "field": "glycemic_control",
            "importance": "high",
            "category": "treatment",
            "message": "Optimize glycemic control (HbA1c target <7% or individualized)",
            "recommendation": "Review HbA1c, adjust hypoglycemic agents, consider SGLT2i/GLP-1 RA",
        },
        {
            "field": "foot_exam",
            "importance": "medium",
            "category": "preventive",
            "message": "Annual foot exam recommended for diabetic nephropathy patients",
            "recommendation": "Schedule annual comprehensive foot examination",
        },
    ],
    "fsgs": [
        {
            "field": "genetic_testing",
            "importance": "medium",
            "category": "investigation",
            "message": "Assess for genetic causes if family history of FSGS or steroid resistance",
            "recommendation": "Consider genetic testing (e.g. podocyte-related genes)",
        },
        {
            "field": "nephrotic_complications",
            "importance": "high",
            "category": "monitoring",
            "message": "Monitor for nephrotic syndrome complications (thrombosis, infection, AKI)",
            "recommendation": "Monitor albumin, cholesterol, screen for thrombosis, vaccinate",
        },
    ],
    "mcd": [
        {
            "field": "steroid_taper",
            "importance": "high",
            "category": "treatment",
            "message": "Taper steroids slowly over 4-6 months to reduce relapse risk",
            "recommendation": "Develop gradual steroid taper schedule",
        },
        {
            "field": "relapse_monitoring",
            "importance": "medium",
            "category": "monitoring",
            "message": "Monitor for relapse — MCD has high relapse rate (40-60%)",
            "recommendation": "Urinalysis and proteinuria monitoring every 1-2 months",
        },
    ],
    "c3_glomerulopathy": [
        {
            "field": "complement_levels",
            "importance": "high",
            "category": "monitoring",
            "message": "Monitor complement levels (C3, C4, CH50) to assess disease activity",
            "recommendation": "Order complement panel at each assessment",
        },
        {
            "field": "lipodystrophy_screening",
            "importance": "medium",
            "category": "monitoring",
            "message": "Screen for acquired partial lipodystrophy — associated with C3 glomerulopathy",
            "recommendation": "Clinical examination for fat loss distribution",
        },
    ],
}

# Map diagnosis substrings to disease keys
DISEASE_KEYWORDS: dict[str, list[str]] = {
    "iga": ["iga", "igan", "berger"],
    "membranous": ["membranous", "mn", "mgn"],
    "lupus": ["lupus", "sle", "ln"],
    "anca": ["anca", "vasculitis", "gpa", "mpa", "egpa"],
    "diabetic_nephropathy": ["diabetic", "dn", "dkn"],
    "fsgs": ["fsgs", "focal segmental"],
    "mcd": ["mcd", "minimal change", "lipoid nephrosis"],
    "c3_glomerulopathy": ["c3", "c3g", "dense deposit", "ddg", "membranoproliferative", "mpgn"],
}


def _check_disease_specific_gaps(patient, features: dict, primary_disease: str) -> list[dict]:
    """Check for disease-specific care gaps based on the patient's primary diagnosis.

    Covers at least 8 diseases: IgA, Membranous, Lupus, ANCA, Diabetic Nephropathy,
    FSGS, MCD, C3 Glomerulopathy.
    """
    gaps = []

    if not primary_disease:
        return gaps

    # Determine which disease key matches
    disease_key = _match_disease_key(primary_disease)
    if not disease_key:
        return gaps

    specific_gaps = DISEASE_SPECIFIC_GAPS.get(disease_key, [])
    for gap_def in specific_gaps:
        gap = dict(gap_def)  # copy
        gap["disease"] = disease_key
        gaps.append(gap)

    return gaps


def _match_disease_key(primary_disease: str) -> str | None:
    """Match a primary_disease string (lowercase) to a disease key."""
    for key, keywords in DISEASE_KEYWORDS.items():
        for kw in keywords:
            if kw in primary_disease:
                return key
    return None

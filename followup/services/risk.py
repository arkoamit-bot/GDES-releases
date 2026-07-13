"""Risk stratification engine for follow-up scheduling (Workstream 5)."""

import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def assess_risk_category(patient, protocol=None):
    """Assign patient to one of: very_high, high, moderate, low.

    Combines disease activity, treatment intensity, kidney function,
    proteinuria, recent events, and transplant status.
    """
    score = 0
    factors = {"very_high": [], "high": [], "moderate": [], "reducing": []}

    outcome = getattr(patient, "outcome", None)
    clinical_profile = getattr(patient, "clinical_profile", None)
    now = timezone.now().date()

    # 1. Kidney function.
    if outcome and outcome.latest_egfr is not None:
        egfr = float(outcome.latest_egfr)
        if egfr < 15:
            score += 50
            factors["very_high"].append("eGFR < 15 (ESKD)")
        elif egfr < 30:
            score += 30
            factors["very_high"].append("eGFR 15-29 (severe CKD)")
        elif egfr < 45:
            score += 15
            factors["high"].append("eGFR 30-44 (moderate-severe CKD)")
        elif egfr < 60:
            score += 5
            factors["moderate"].append("eGFR 45-59 (mild-moderate CKD)")

        # Rapid decline.
        if outcome.sustained_40_decline:
            score += 40
            factors["very_high"].append("Sustained >=40% eGFR decline")

    # 2. Proteinuria.
    if outcome and outcome.latest_upcr is not None:
        upcr = float(outcome.latest_upcr)
        if upcr > 3.5:
            score += 50
            factors["very_high"].append("Nephrotic-range proteinuria (>3.5 g/g)")
        elif upcr > 1.0:
            score += 20
            factors["high"].append("Proteinuria 1.0-3.5 g/g")
        elif upcr > 0.3:
            score += 5
            factors["moderate"].append("Mild proteinuria 0.3-1.0 g/g")
    elif clinical_profile:
        features = clinical_profile.features_snapshot or {}
        if features.get("nephrotic_range_proteinuria"):
            score += 35
            factors["very_high"].append("Nephrotic-range proteinuria (feature)")

    # 3. Disease activity from clinical profile trajectory.
    if clinical_profile and clinical_profile.disease_trajectory:
        trend = clinical_profile.disease_trajectory.get("trend", "stable")
        if trend == "declining":
            score += 25
            factors["very_high"].append("Declining disease trajectory")
        elif trend in ("relapse", "relapsing"):
            score += 30
            factors["very_high"].append("Relapse detected in trajectory")

    # 4. Recent relapse.
    recent_relapse = patient.relapses.filter(
        relapse_date__gte=now - timezone.timedelta(days=180)).exists()
    if recent_relapse:
        score += 30
        factors["very_high"].append("Relapse within 6 months")

    # 5. Recent hospitalization.
    recent_admit = patient.admissions.filter(
        admit_date__gte=now - timezone.timedelta(days=90)).exists()
    if recent_admit:
        score += 20
        factors["high"].append("Hospitalization within 3 months")

    # 6. Recent biopsy.
    recent_biopsy = patient.biopsies.filter(
        biopsy_date__gte=now - timezone.timedelta(days=90)).exists()
    if recent_biopsy:
        score += 10
        factors["moderate"].append("Recent biopsy (within 3 months)")

    # 7. Treatment intensity.
    ongoing_tx = patient.exposures.filter(ongoing=True)
    immunosuppressants = ["steroid", "mmf", "cyclophosphamide",
                          "rituximab", "cni", "azathioprine"]
    for exposure in ongoing_tx:
        dc = exposure.drug.drug_class
        if dc in ("cyclophosphamide", "rituximab"):
            score += 25
            factors["high"].append(f"On {dc} (intense immunosuppression)")
        elif dc in immunosuppressants:
            score += 10
            factors["moderate"].append(f"On {dc} (maintenance immunosuppression)")

    # 8. Transplant status.
    if hasattr(patient, "clinical_profile") and clinical_profile:
        milestones = clinical_profile.milestones or []
        for m in milestones:
            if isinstance(m, dict) and m.get("milestone") == "transplant":
                score += 25
                factors["high"].append("Post-transplant")
                break

    # 9. Pregnancy (from features snapshot).
    if clinical_profile:
        features = clinical_profile.features_snapshot or {}
        if features.get("pregnancy") or features.get("pregnant"):
            score += 40
            factors["very_high"].append("Pregnancy")

    # 10. Hard kidney endpoint.
    if outcome:
        if outcome.eskd or outcome.composite_kidney_event:
            score += 50
            factors["very_high"].append("ESKD / composite kidney endpoint reached")

    # 11. Recent clinical event.
    recent_event = patient.events.filter(
        event_date__gte=now - timezone.timedelta(days=90)).exists()
    if recent_event:
        score += 15
        factors["high"].append("Recent clinical event (< 3 months)")

    # Determine category.
    if score >= 50:
        category = "very_high"
    elif score >= 25:
        category = "high"
    elif score >= 10:
        category = "moderate"
    else:
        category = "low"

    logger.debug(
        "Risk score %d for %s → %s: %s",
        score, patient.patient_id, category, factors,
    )
    return {
        "category": category,
        "score": score,
        "factors": factors,
    }

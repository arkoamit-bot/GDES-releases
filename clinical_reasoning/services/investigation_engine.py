"""Investigation Recommendation Engine — Obj 3 of GDES V6.

Generates differential-specific investigation recommendations based on
the current clinical picture and differential diagnosis.

Each recommendation includes:
- Clinical rationale
- Priority (urgent/high/medium/low)
- Expected diagnostic value
- Guideline reference (KDIGO/RKD)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Disease-specific investigation protocols
# ---------------------------------------------------------------------------

DISEASE_INVESTIGATIONS: dict[str, list[dict[str, Any]]] = {
    "iga": [
        {"test": "Renal biopsy (if not done)", "rationale": "Confirm IgAN diagnosis and assess MEST-C score", "priority": "urgent", "diagnostic_value": "Definitive diagnosis and prognostication", "guideline": "KDIGO 2021 GN 4.1", "when_missing": ["biopsy"]},
        {"test": "Serum IgA level", "rationale": "Elevated in ~50% of IgAN; supports diagnosis", "priority": "medium", "diagnostic_value": "Supportive", "guideline": "KDIGO 2021", "when_missing": []},
        {"test": "Urine protein quantification (UPCR or 24h)", "rationale": "Essential for disease activity assessment and treatment response", "priority": "high", "diagnostic_value": "Core monitoring variable", "guideline": "KDIGO 2021 GN 4.1.3", "when_missing": ["proteinuria"]},
        {"test": "Serum creatinine + eGFR", "rationale": "Baseline kidney function for staging and trajectory", "priority": "high", "diagnostic_value": "Core staging", "guideline": "KDIGO 2021", "when_missing": ["egfr"]},
        {"test": "Complement C3, C4", "rationale": "Low C3 may suggest post-infectious GN or MPGN; helps exclude lupus", "priority": "medium", "diagnostic_value": "Differential exclusion", "guideline": "KDIGO 2021", "when_missing": ["lowC3", "lowC4"]},
    ],
    "membranous": [
        {"test": "PLA2R antibody (serum)", "rationale": "Positive in ~70% of primary MN; biomarker for diagnosis and treatment response", "priority": "urgent", "diagnostic_value": "Diagnostic + prognostic", "guideline": "KDIGO 2021 GN 4.2", "when_missing": ["pla2r"]},
        {"test": "THSD7A antibody", "rationale": "Alternative autoantigen in PLA2R-negative MN; may indicate malignancy association", "priority": "high", "diagnostic_value": "Alternative diagnosis", "guideline": "KDIGO 2021", "when_missing": []},
        {"test": "Renal biopsy with IgG subclass staining", "rationale": "Confirm MN stage and IgG4 pattern (primary vs secondary)", "priority": "urgent", "diagnostic_value": "Definitive diagnosis", "guideline": "KDIGO 2021 GN 4.2", "when_missing": ["biopsy"]},
        {"test": "Malignancy screening (age-appropriate)", "rationale": "MN associated with solid organ malignancy; age-appropriate screening required", "priority": "high", "diagnostic_value": "Exclude secondary cause", "guideline": "KDIGO 2021 GN 4.2.2", "when_missing": []},
        {"test": "Serum albumin", "rationale": "Assess nephrotic syndrome severity and nutritional status", "priority": "high", "diagnostic_value": "Disease severity", "guideline": "KDIGO 2021", "when_missing": []},
    ],
    "mcd": [
        {"test": "Renal biopsy (if not done)", "rationale": "MCD is diagnosis of exclusion after biopsy shows normal light microscopy with foot process effacement", "priority": "high", "diagnostic_value": "Definitive diagnosis", "guideline": "KDIGO 2021 GN 4.3", "when_missing": ["biopsy"]},
        {"test": "Urine protein quantification", "rationale": "Essential for confirming nephrotic-range proteinuria and monitoring response", "priority": "high", "diagnostic_value": "Core monitoring", "guideline": "KDIGO 2021", "when_missing": ["proteinuria"]},
        {"test": "Serum albumin", "rationale": "Assess nephrotic syndrome severity", "priority": "high", "diagnostic_value": "Disease severity", "guideline": "KDIGO 2021", "when_missing": []},
    ],
    "fsgs": [
        {"test": "Renal biopsy with adequate glomeruli", "rationale": "FSGS is a histological diagnosis; ensure adequate sampling to avoid sampling error", "priority": "urgent", "diagnostic_value": "Definitive diagnosis", "guideline": "KDIGO 2021 GN 4.4", "when_missing": ["biopsy"]},
        {"test": "Urine protein quantification", "rationale": "Monitor treatment response and relapse", "priority": "high", "diagnostic_value": "Core monitoring", "guideline": "KDIGO 2021", "when_missing": ["proteinuria"]},
        {"test": "Genetic testing (podocyte genes: NPHS1, NPHS2, ACTN4, TRPC6)", "rationale": "Hereditary FSGS suggested by family history, early onset, or steroid resistance", "priority": "medium", "diagnostic_value": "Etiological diagnosis", "guideline": "KDIGO 2021 GN 4.4", "when_missing": []},
        {"test": "Serum creatinine + eGFR", "rationale": "Baseline kidney function and staging", "priority": "high", "diagnostic_value": "Core staging", "guideline": "KDIGO 2021", "when_missing": ["egfr"]},
    ],
    "lupus": [
        {"test": "Renal biopsy (ISN/RPS classification)", "rationale": "Essential for lupus nephritis class determination and treatment guidance", "priority": "urgent", "diagnostic_value": "Definitive classification", "guideline": "KDIGO 2024 LN", "when_missing": ["biopsy"]},
        {"test": "Anti-dsDNA antibody", "rationale": "Disease activity marker; rising titers predict flare", "priority": "high", "diagnostic_value": "Activity biomarker", "guideline": "KDIGO 2024 LN", "when_missing": ["anaDsDna"]},
        {"test": "Complement C3, C4", "rationale": "Low complements indicate active LN; C4 particularly low in active disease", "priority": "high", "diagnostic_value": "Activity biomarker", "guideline": "KDIGO 2024 LN", "when_missing": ["lowC3", "lowC4"]},
        {"test": "ANA screening", "rationale": "Required for SLE classification; high sensitivity", "priority": "high", "diagnostic_value": "Classification", "guideline": "KDIGO 2024 LN", "when_missing": ["ana"]},
        {"test": "CBC with differential", "rationale": "Cytopenias common in active LN; monitor for drug toxicity", "priority": "medium", "diagnostic_value": "Activity + safety", "guideline": "KDIGO 2024 LN", "when_missing": []},
        {"test": "Antiphospholipid antibodies", "rationale": "Risk stratification for thrombosis in nephrotic LN", "priority": "medium", "diagnostic_value": "Risk stratification", "guideline": "KDIGO 2024 LN", "when_missing": []},
    ],
    "anca": [
        {"test": "ANCA (MPO-ANCA / PR3-ANCA)", "rationale": "Confirm AAV diagnosis; MPO vs PR3 has prognostic and treatment implications", "priority": "urgent", "diagnostic_value": "Diagnostic + prognostic", "guideline": "KDIGO 2024 AAV", "when_missing": ["anca"]},
        {"test": "Renal biopsy", "rationale": "Confirm pauci-immune GN and assess chronicity (fibrosis percentage)", "priority": "urgent", "diagnostic_value": "Definitive diagnosis + prognosis", "guideline": "KDIGO 2024 AAV", "when_missing": ["biopsy"]},
        {"test": "Complement C3, C4", "rationale": "Normal in AAV; helps exclude lupus and cryoglobulinemic GN", "priority": "medium", "diagnostic_value": "Differential exclusion", "guideline": "KDIGO 2024 AAV", "when_missing": ["lowC3", "lowC4"]},
        {"test": "Serum creatinine + eGFR", "rationale": "Critical for Birmingham Vasculitis Activity Score (BVAS)", "priority": "high", "diagnostic_value": "Activity scoring", "guideline": "KDIGO 2024 AAV", "when_missing": ["egfr"]},
        {"test": "Urinalysis with microscopy", "rationale": "Active sediment (RBC casts) indicates renal involvement", "priority": "high", "diagnostic_value": "Activity assessment", "guideline": "KDIGO 2024 AAV", "when_missing": []},
    ],
    "antiGbm": [
        {"test": "Anti-GBM antibody (serum)", "rationale": "Rapid confirmation required — emergency treatment must not be delayed", "priority": "urgent", "diagnostic_value": "Diagnostic + emergency", "guideline": "KDIGO 2024 Anti-GBM", "when_missing": ["antiGbm"]},
        {"test": "Renal biopsy (if not contraindicated)", "rationale": "Confirm crescentic GN; assess percentage of crescents and fibrosis for prognosis", "priority": "urgent", "diagnostic_value": "Definitive diagnosis + prognosis", "guideline": "KDIGO 2024 Anti-GBM", "when_missing": ["biopsy"]},
        {"test": "ANCA (to exclude dual-positive)", "rationale": "~30% of anti-GBM are ANCA-positive (dual-positive); may relapse", "priority": "high", "diagnostic_value": "Prognostic", "guideline": "KDIGO 2024 Anti-GBM", "when_missing": ["anca"]},
        {"test": "CBC with differential", "rationale": "Baseline before cyclophosphamide; monitor leukopenia", "priority": "high", "diagnostic_value": "Safety", "guideline": "KDIGO 2024 Anti-GBM", "when_missing": []},
    ],
    "infectionRelated": [
        {"test": "Throat swab / ASO titer", "rationale": "Confirm streptococcal infection as trigger", "priority": "medium", "diagnostic_value": "Etiological", "guideline": "KDIGO 2021 GN 4.6", "when_missing": []},
        {"test": "Blood cultures", "rationale": "Exclude endocarditis-associated GN", "priority": "medium", "diagnostic_value": "Etiological", "guideline": "KDIGO 2021 GN 4.6", "when_missing": []},
        {"test": "Hepatitis B, C serology", "rationale": "Viral GN must be excluded", "priority": "high", "diagnostic_value": "Etiological", "guideline": "KDIGO 2021 GN 4.6", "when_missing": []},
        {"test": "Complement C3, C4", "rationale": "Low C3 classic in post-streptococcal GN; normalize with resolution", "priority": "high", "diagnostic_value": "Activity biomarker", "guideline": "KDIGO 2021 GN 4.6", "when_missing": ["lowC3"]},
    ],
    "c3": [
        {"test": "Complement C3 level", "rationale": "Persistent low C3 is the hallmark of C3 glomerulopathy", "priority": "urgent", "diagnostic_value": "Core diagnostic", "guideline": "KDIGO 2021 GN 4.7", "when_missing": ["lowC3"]},
        {"test": "Complement pathway testing (CH50, AP50, Factor H, Factor I, C3 nephritic factor)", "rationale": "Identify underlying complement dysregulation for targeted therapy", "priority": "high", "diagnostic_value": "Pathophysiological", "guideline": "KDIGO 2021 GN 4.7", "when_missing": []},
        {"test": "Renal biopsy with C3 staining", "rationale": "Confirm dominant C3 deposition (C3 glomerulopathy vs post-infectious)", "priority": "urgent", "diagnostic_value": "Definitive classification", "guideline": "KDIGO 2021 GN 4.7", "when_missing": ["biopsy"]},
    ],
}


# ---------------------------------------------------------------------------
# Investigation Recommendation Engine
# ---------------------------------------------------------------------------

@dataclass
class InvestigationRecommendation:
    """A single investigation recommendation."""
    test: str
    rationale: str
    priority: str  # "urgent", "high", "medium", "low"
    diagnostic_value: str
    guideline: str
    category: str  # "diagnostic", "monitoring", "safety", "prognostic"

    def to_dict(self) -> dict:
        return {
            "test": self.test,
            "rationale": self.rationale,
            "priority": self.priority,
            "diagnostic_value": self.diagnostic_value,
            "guideline": self.guideline,
            "category": self.category,
        }


@dataclass
class InvestigationPlan:
    """Complete investigation recommendation plan for a patient."""
    patient_id: str
    differential: list[dict]
    recommendations: list[InvestigationRecommendation]
    completed_investigations: list[str]
    summary: str

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "differential": self.differential[:5],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "completed_investigations": self.completed_investigations,
            "summary": self.summary,
            "total_recommendations": len(self.recommendations),
            "urgent_count": sum(1 for r in self.recommendations if r.priority == "urgent"),
            "high_count": sum(1 for r in self.recommendations if r.priority == "high"),
        }


def generate_investigation_recommendations(
    patient,
    differential: list[dict],
    features: dict | None = None,
) -> InvestigationPlan:
    """Generate investigation recommendations based on differential and patient data.

    Args:
        patient: Patient model instance
        differential: Ranked differential from clinical reasoning
        features: Patient features dict (optional)

    Returns:
        InvestigationPlan with prioritized recommendations
    """
    features = features or _extract_basic_features(patient)
    completed = _identify_completed_investigations(features)
    all_recommendations: list[InvestigationRecommendation] = []

    # Generate recommendations for top differential entries
    for dx in differential[:3]:  # Top 3 diagnoses
        disease_id = dx.get("disease_id", "")
        score = dx.get("score", 0)
        disease_investigations = DISEASE_INVESTIGATIONS.get(disease_id, [])

        for inv in disease_investigations:
            # Check if this investigation is needed based on missing data
            when_missing = inv.get("when_missing", [])
            already_done = any(m not in completed for m in when_missing) if when_missing else True

            # Only recommend if relevant (either something is missing, or always needed)
            if when_missing and not already_done:
                continue

            # Determine category
            category = _categorize_investigation(inv["test"])

            # Weight priority by differential score
            adjusted_priority = _adjust_priority(inv["priority"], score, dx.get("confidence", 0))

            rec = InvestigationRecommendation(
                test=inv["test"],
                rationale=f"[{dx.get('disease_name', disease_id)}] {inv['rationale']}",
                priority=adjusted_priority,
                diagnostic_value=inv["diagnostic_value"],
                guideline=inv["guideline"],
                category=category,
            )
            all_recommendations.append(rec)

    # Deduplicate and sort
    all_recommendations = _deduplicate_recommendations(all_recommendations)
    all_recommendations.sort(key=lambda r: _priority_order(r.priority))

    summary = _build_summary(all_recommendations, differential, completed)

    return InvestigationPlan(
        patient_id=patient.patient_id,
        differential=differential,
        recommendations=all_recommendations,
        completed_investigations=completed,
        summary=summary,
    )


def _extract_basic_features(patient) -> dict:
    """Extract basic features from patient for investigation checking."""
    features = {}
    try:
        latest_egfr = getattr(patient, "latest_egfr", None)
        if latest_egfr is not None:
            features["latest_egfr"] = latest_egfr
        else:
            features["egfr"] = None
    except Exception:
        pass

    # Check for biopsy
    try:
        if patient.biopsies.exists():
            features["biopsy"] = True
    except Exception:
        pass

    # Check for serology results
    try:
        from labs.models import LabResult
        serology_codes = LabResult.objects.filter(
            patient=patient,
            test__code__in=("pla2r", "anca", "anti_gbm", "c3", "c4", "ana", "anti_dsDNA"),
        ).values_list("test__code", flat=True).distinct()
        for code in serology_codes:
            features[code] = True
    except Exception:
        pass

    return features


def _identify_completed_investigations(features: dict) -> list[str]:
    """Identify which investigations have already been completed."""
    completed = []
    if features.get("biopsy"):
        completed.append("biopsy")
    if features.get("latest_egfr") is not None:
        completed.append("egfr")
    if features.get("proteinuria") not in (None, "none"):
        completed.append("proteinuria")
    if features.get("pla2r"):
        completed.append("pla2r")
    if features.get("anca"):
        completed.append("anca")
    if features.get("antiGbm"):
        completed.append("antiGbm")
    if features.get("ana"):
        completed.append("ana")
    if features.get("anaDsDna"):
        completed.append("anaDsDna")
    if features.get("lowC3"):
        completed.append("lowC3")
    if features.get("lowC4"):
        completed.append("lowC4")
    return completed


def _categorize_investigation(test_name: str) -> str:
    """Categorize an investigation by its primary purpose."""
    name_lower = test_name.lower()
    if "biopsy" in name_lower:
        return "diagnostic"
    if any(kw in name_lower for kw in ("creatinine", "egfr", "upcr", "urine protein", "albumin")):
        return "monitoring"
    if any(kw in name_lower for kw in ("cbc", "lft", "glucose", "potassium")):
        return "safety"
    if any(kw in name_lower for kw in ("genetic", "screening")):
        return "prognostic"
    return "diagnostic"


def _adjust_priority(base_priority: str, score: float, confidence: float) -> str:
    """Adjust priority based on differential score and confidence."""
    order = ["urgent", "high", "medium", "low"]
    idx = order.index(base_priority) if base_priority in order else 2

    # Boost priority for high-confidence diagnoses
    if confidence and confidence > 70 and idx > 0:
        idx = max(0, idx - 1)
    elif score and score > 10 and idx > 0:
        idx = max(0, idx - 1)

    return order[idx]


def _priority_order(priority: str) -> int:
    """Sort key for priority ordering."""
    return {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 4)


def _deduplicate_recommendations(recs: list[InvestigationRecommendation]) -> list[InvestigationRecommendation]:
    """Remove duplicate recommendations, keeping highest priority."""
    seen = {}
    for rec in recs:
        key = rec.test.lower().strip()
        if key not in seen or _priority_order(rec.priority) < _priority_order(seen[key].priority):
            seen[key] = rec
    return list(seen.values())


def _build_summary(
    recommendations: list[InvestigationRecommendation],
    differential: list[dict],
    completed: list[str],
) -> str:
    """Build a human-readable summary of investigation recommendations."""
    if not recommendations:
        return "No additional investigations recommended at this time."

    top_dx = differential[0].get("disease_name", "Unknown") if differential else "Unknown"
    urgent = [r for r in recommendations if r.priority == "urgent"]
    high = [r for r in recommendations if r.priority == "high"]

    parts = [f"Based on differential ({top_dx}), "]

    if urgent:
        parts.append(f"{len(urgent)} urgent investigation(s) recommended. ")
    if high:
        parts.append(f"{len(high)} high-priority investigation(s) recommended. ")

    missing_count = sum(1 for r in recommendations if any(
        m in " ".join([r.test, r.rationale]).lower()
        for m in completed
    ) is False)

    parts.append(f"Total: {len(recommendations)} investigation(s) to consider.")

    return "".join(parts)

"""
Knowledge rule engine — evaluates KnowledgeBaseEntry rules against patient data.

Each KnowledgeBaseEntry.rule_data contains a structured rule definition:
{
    "conditions": [
        {"field": "proteinuria", "operator": "gte", "value": 3.5},
        {"field": "albumin", "operator": "lte", "value": 3.0},
    ],
    "weight": 3,
    "explanation": "Nephrotic-range proteinuria with hypoalbuminemia",
    "evidence_grade": "1"
}

The engine extracts patient features from the database and evaluates conditions
to produce scored recommendations.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

from django.db.models import Q, Max

from patients.models import Patient
from patients.workflow import DiseasePhase, RegistrationStatus

from .models import KnowledgeBaseEntry, GuidelineSource


# ---------------------------------------------------------------------------
# Feature extraction — pull clinical features from the patient's records
# ---------------------------------------------------------------------------

def extract_patient_features(patient: Patient) -> dict:
    """Extract a feature dict from the patient's clinical data for rule evaluation.

    Returns a dict with keys matching the condition fields in KnowledgeBaseEntry.rule_data:
        - features: list of clinical feature codes
        - labs: list of lab finding codes
        - biopsy: list of biopsy finding codes
        - proteinuria: "nephrotic" | "subnephrotic" | "none"
        - albumin: "low" | "normal"
        - sediment: "casts" | "hematuria" | "bland"
        - egfrTrend: "rapidDecline" | "reduced" | "normal"
        - ageGroup: "child" | "adult"
        - disease_phase: current phase
        - registration_status: current status
    """
    features = {
        "features": [],
        "labs": [],
        "biopsy": [],
        "proteinuria": "none",
        "albumin": "normal",
        "sediment": "bland",
        "egfrTrend": "normal",
        "ageGroup": "adult",
        "disease_phase": patient.current_phase or "",
        "registration_status": patient.registration_status or "",
    }

    # --- Age group ---
    if patient.dob:
        age_years = (dt.date.today() - patient.dob).days / 365.25
        if age_years < 18:
            features["ageGroup"] = "child"

    # --- Level 2: persistent clinical features from Patient (single source) ---
    # Ensures reasoning always has access to comorbidity data even if
    # encounter-level data is missing.
    if patient.hypertension and "hypertension" not in features["features"]:
        features["features"].append("hypertension")
    if patient.autoimmune_disease and "autoimmune" not in features["features"]:
        features["features"].append("autoimmune")
    if patient.chronic_infection and "chronicInfection" not in features["features"]:
        features["features"].append("chronicInfection")

    # --- Clinical features from latest encounter ---
    latest_encounter = (
        patient.encounters.order_by("-encounter_date").first()
    )
    if latest_encounter:
        if latest_encounter.edema_grade and latest_encounter.edema_grade > 0:
            features["features"].append("edema")
        if latest_encounter.systolic_bp and latest_encounter.systolic_bp >= 140:
            features["features"].append("hypertension")

        # Get clinical assessment features
        assessment = getattr(latest_encounter, "clinical_assessment", None)
        if assessment and assessment.features:
            features["features"].extend(assessment.features)

    # --- Lab findings from latest results ---
    try:
        from labs.models import LabResult
        latest_results = (
            LabResult.objects.filter(patient=patient)
            .select_related("test")
            .order_by("-sample_date")
        )

        for result in latest_results[:20]:  # Last 20 results
            code = result.test.code.lower() if result.test else ""

            # Proteinuria assessment
            if code in ("upcr", "acr", "proteinuria"):
                try:
                    val = float(result.value_numeric)
                    if val >= 3.5:
                        features["proteinuria"] = "nephrotic"
                    elif val >= 0.5 and features["proteinuria"] == "none":
                        features["proteinuria"] = "subnephrotic"
                except (ValueError, TypeError):
                    pass

            # Albumin
            if code in ("albumin", "alb"):
                try:
                    val = float(result.value_numeric)
                    if val < 3.0:
                        features["albumin"] = "low"
                except (ValueError, TypeError):
                    pass

            # Urine sediment
            if code in ("urine_rbc_casts", "rbc_casts"):
                features["sediment"] = "casts"
            elif code in ("urine_rbc", "hematuria") and features["sediment"] != "casts":
                try:
                    val = float(result.value_numeric)
                    if val > 5:
                        features["sediment"] = "hematuria"
                except (ValueError, TypeError):
                    pass

            # Complement
            if code in ("c3", "complement_c3"):
                try:
                    val = float(result.value_numeric)
                    if val < 90:
                        features["labs"].append("lowC3")
                except (ValueError, TypeError):
                    pass
            if code in ("c4", "complement_c4"):
                try:
                    val = float(result.value_numeric)
                    if val < 10:
                        features["labs"].append("lowC4")
                except (ValueError, TypeError):
                    pass

            # ANCA
            if code in ("anca", "anca_typing"):
                features["labs"].append("anca")

            # Anti-GBM
            if code in ("anti_gbm", "antigbm"):
                features["labs"].append("antiGbm")

            # PLA2R
            if code in ("pla2r", "anti_pla2r"):
                features["labs"].append("pla2r")

            # ANA / anti-dsDNA
            if code in ("ana", "anti_dsDNA", "dsdna"):
                features["labs"].append("anaDsDna")

            # Hepatitis
            if code in ("hbv", "hepatitis_b", "hcv", "hepatitis_c"):
                features["labs"].append("hepatitis")

    except ImportError:
        pass

    # --- Biopsy findings ---
    try:
        from pathology.models import Biopsy, GNDiagnosis, IgANScore
        biopsy = patient.biopsies.order_by("-biopsy_date").first()
        if biopsy:
            features["biopsy"].append("biopsy_done")
            # Check GN diagnosis
            gn_dx = getattr(biopsy, "diagnosis", None)
            if gn_dx:
                dx_lower = gn_dx.diagnosis.lower() if gn_dx.diagnosis else ""
                if "iga" in dx_lower:
                    features["biopsy"].append("mesangialIga")
                if "membranous" in dx_lower:
                    features["biopsy"].append("subepithelial")
                if "fsgs" in dx_lower or "focal segmental" in dx_lower:
                    features["biopsy"].append("segmentalSclerosis")
                if "lupus" in dx_lower:
                    features["biopsy"].append("fullHouse")
                if "c3" in dx_lower:
                    features["biopsy"].append("c3Dominant")

            # Check for crescents
            if biopsy.crescent_pct and biopsy.crescent_pct > 0:
                features["biopsy"].append("crescents")

            # Check for podocyte effacement (from EM findings text)
            if biopsy.em_findings and "podocyte" in biopsy.em_findings.lower():
                features["biopsy"].append("podocyteEffacement")

    except (ImportError, AttributeError):
        pass

    # --- eGFR trend ---
    if patient.latest_egfr:
        if patient.latest_egfr < 30:
            features["egfrTrend"] = "rapidDecline"
        elif patient.latest_egfr < 60:
            features["egfrTrend"] = "reduced"

    # --- Disease-specific features ---
    diagnosis = (patient.primary_diagnosis or "").lower()
    if "sle" in diagnosis or "lupus" in diagnosis:
        features["features"].append("sle")
    if "diabetes" in diagnosis or "dkd" in diagnosis:
        features["features"].append("diabetes")

    # Deduplicate lists
    for key in ("features", "labs", "biopsy"):
        features[key] = list(set(features[key]))

    return features


# ---------------------------------------------------------------------------
# Rule evaluation
# ---------------------------------------------------------------------------

@dataclass
class MatchedRule:
    entry_id: str
    disease_id: str
    disease_name: str
    condition_text: str
    weight: float
    explanation: str
    source: str
    evidence_grade: str


@dataclass
class DiseaseScore:
    disease_id: str
    disease_name: str
    total_score: float
    matched_rules: list = field(default_factory=list)
    source: str = ""
    evidence_grade: str = ""


def _evaluate_condition(condition: dict, features: dict) -> bool:
    """Evaluate a single condition against patient features.

    Condition format:
        {"field": "proteinuria", "operator": "eq", "value": "nephrotic"}
        {"field": "features", "operator": "contains", "value": "edema"}
        {"field": "latest_egfr", "operator": "lt", "value": 30}
    """
    field_name = condition.get("field", "")
    operator = condition.get("operator", "eq")
    value = condition.get("value")

    # Get the patient value
    if field_name in features:
        patient_value = features[field_name]
    else:
        patient_value = None

    # Evaluate based on operator
    if operator == "eq":
        if isinstance(patient_value, list):
            return value in patient_value
        return patient_value == value
    elif operator == "neq":
        if isinstance(patient_value, list):
            return value not in patient_value
        return patient_value != value
    elif operator == "contains":
        if isinstance(patient_value, list):
            return value in patient_value
        return False
    elif operator == "not_contains":
        if isinstance(patient_value, list):
            return value not in patient_value
        return True
    elif operator == "gt":
        try:
            return float(patient_value) > float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "gte":
        try:
            return float(patient_value) >= float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "lt":
        try:
            return float(patient_value) < float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "lte":
        try:
            return float(patient_value) <= float(value)
        except (ValueError, TypeError):
            return False
    elif operator == "in":
        if isinstance(value, list):
            return patient_value in value
        return False
    elif operator == "exists":
        return patient_value is not None and patient_value != ""
    elif operator == "not_exists":
        return patient_value is None or patient_value == ""

    return False


def evaluate_entry(entry: KnowledgeBaseEntry, features: dict) -> DiseaseScore:
    """Evaluate a single KnowledgeBaseEntry against patient features."""
    rule_data = entry.rule_data
    conditions = rule_data.get("conditions", [])
    weight = rule_data.get("weight", 1)
    explanation = rule_data.get("explanation", "")
    base_score = rule_data.get("base_score", 0)

    matched = []
    for condition in conditions:
        if _evaluate_condition(condition, features):
            matched.append({
                "condition": condition,
                "explanation": explanation,
                "weight": weight,
            })

    # A rule contributes to the differential ONLY when it actually fires — i.e.
    # at least one of its conditions matches the patient. Otherwise its base
    # prior must NOT be counted: summing base_score across every (mostly
    # non-matching) rule of a disease made the ranking reflect how MANY rules a
    # disease has rather than how well the patient fits it (H-1). A non-firing
    # rule now scores 0; a firing rule scores its base prior plus the weight of
    # each matched condition.
    if matched:
        total_score = base_score + weight * len(matched)
    else:
        total_score = 0

    source_str = ""
    if entry.source:
        source_str = f"{entry.source.abbreviation} {entry.source.version_year}"

    disease_name = entry.disease_id
    try:
        from .models import Disease
        disease_obj = Disease.objects.get(pk=entry.disease_id)
        if disease_obj.name:
            disease_name = disease_obj.name
    except Exception:
        pass

    return DiseaseScore(
        disease_id=entry.disease_id,
        disease_name=disease_name,
        total_score=max(0, total_score),
        matched_rules=matched,
        source=source_str,
        evidence_grade=entry.evidence_grade,
    )


def evaluate_patient_rules(
    patient: Patient,
    disease_id: str | None = None,
) -> list[DiseaseScore]:
    """Evaluate all active KnowledgeBaseEntry rules against a patient.

    Args:
        patient: The patient to evaluate
        disease_id: Optional filter to evaluate only rules for a specific disease

    Returns:
        List of DiseaseScore objects, sorted by total_score descending
    """
    features = extract_patient_features(patient)

    # Get active rules
    queryset = KnowledgeBaseEntry.objects.filter(
        status=KnowledgeBaseEntry.Status.ACTIVE
    ).select_related("source")

    if disease_id:
        queryset = queryset.filter(disease_id=disease_id)

    # Group entries by disease_id and aggregate scores
    disease_scores: dict[str, DiseaseScore] = {}

    for entry in queryset:
        result = evaluate_entry(entry, features)

        if result.disease_id not in disease_scores:
            disease_scores[result.disease_id] = DiseaseScore(
                disease_id=result.disease_id,
                disease_name=result.disease_name,
                total_score=0,
                source=result.source,
                evidence_grade=result.evidence_grade,
            )

        ds = disease_scores[result.disease_id]
        ds.total_score += result.total_score
        ds.matched_rules.extend(result.matched_rules)

    # Sort by score descending
    scored_list = sorted(disease_scores.values(), key=lambda d: -d.total_score)

    return scored_list

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
        "biopsy_inferred": [],
        "biopsy_absent": [],
        "proteinuria": "none",
        "albumin": "normal",
        "sediment": "bland",
        "egfrTrend": "normal",
        "latest_egfr": None,
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

    # --- Lab findings: the newest CURRENT result of each test, read for what
    # it says (labs.codes), not merely for being present. Each measure keeps its
    # own variable: UPCR (g/g), 24-h protein (g/day) and UACR (mg/g) are not
    # interchangeable.
    try:
        from labs.codes import interpret, is_positive, latest_by_code
        from labs.models import LabResult
        latest = latest_by_code(
            LabResult.objects.filter(patient=patient).select_related("test"))
        features["lab_values"] = {}
        features["lab_interpretations"] = {}
        for code, result in latest.items():
            features["lab_interpretations"][code] = interpret(result)
            if result.value_numeric is not None:
                features["lab_values"][code] = {
                    "value": float(result.value_numeric), "unit": result.unit,
                    "date": result.result_date.isoformat() if result.result_date else None,
                    "result_id": result.pk}

        def num(code):
            r = latest.get(code)
            return float(r.value_numeric) if r is not None and r.value_numeric is not None else None

        for code in ("upcr", "utp_24h"):
            val = num(code)
            if val is None:
                continue
            if val >= 3.5:
                features["proteinuria"] = "nephrotic"
            elif val >= 0.5 and features["proteinuria"] == "none":
                features["proteinuria"] = "subnephrotic"
        features["upcr"] = num("upcr")
        features["utp_24h"] = num("utp_24h")
        features["uacr"] = num("uacr")

        alb = num("albumin")
        if alb is not None and alb < 3.0:
            features["albumin"] = "low"

        casts = latest.get("urine_rbc_casts")
        if casts is not None and (is_positive(casts) or (casts.value_numeric or 0) > 0):
            features["sediment"] = "casts"
        rbc = num("urine_rbc")
        if features["sediment"] != "casts" and rbc is not None and rbc > 5:
            features["sediment"] = "hematuria"

        c3 = latest.get("c3")
        if c3 is not None and (interpret(c3) == "low" or (c3.value_numeric is not None
                                                           and c3.value_numeric < 90)):
            features["labs"].append("lowC3")
        c4 = latest.get("c4")
        if c4 is not None and (interpret(c4) == "low" or (c4.value_numeric is not None
                                                           and c4.value_numeric < 10)):
            features["labs"].append("lowC4")

        for codes, feature in ((("anca", "mpo_anca", "pr3_anca"), "anca"),
                               (("anti_gbm",), "antiGbm"),
                               (("anti_pla2r",), "pla2r"),
                               (("ana", "anti_dsdna"), "anaDsDna"),
                               (("hbsag", "anti_hcv"), "hepatitis")):
            if any(latest.get(c) is not None and is_positive(latest[c]) for c in codes):
                features["labs"].append(feature)
    except ImportError:
        pass

    # --- Biopsy: OBSERVED findings from the current report of the biopsy the
    # patient's pathology summary is projected from, kept apart from
    # expectations INFERRED from the diagnosis label (biopsy_inferred), which
    # the rule engine reports as inferences.
    try:
        from pathology.services.projection import select_source
        from pathology.services.reasoning import biopsy_features
        sel = select_source(patient)
        biopsy = sel.biopsy or patient.biopsies.order_by("-biopsy_date", "-id").first()
        if biopsy:
            observed, absent, inferred = biopsy_features(biopsy)
            features["biopsy"].append("biopsy_done")
            features["biopsy"].extend(observed)
            features["biopsy_absent"] = sorted(absent)
            features["biopsy_inferred"] = sorted(set(inferred) - set(observed) - set(absent))
    except (ImportError, AttributeError):
        pass

    # --- eGFR trend ---
    if patient.latest_egfr:
        features["latest_egfr"] = float(patient.latest_egfr)
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
    for key in ("features", "labs", "biopsy", "biopsy_inferred", "biopsy_absent"):
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

    # Map legacy singular field names to the actual features dict keys.
    _FIELD_ALIASES = {
        "feature": "features",
        "lab": "labs",
    }
    field_name = _FIELD_ALIASES.get(field_name, field_name)

    # Get the patient value
    patient_value = features.get(field_name)

    # "genetic" rules: map the value to a features-list check
    if field_name == "genetic" and patient_value is None:
        genetic = value  # e.g. "col4aMutation"
        patient_value = [v for v in features.get("features", []) if "genetic" in str(v).lower() or str(v) == genetic]
        if not patient_value:
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
        elif (condition.get("field") == "biopsy"
              and condition.get("operator", "eq") in ("eq", "contains")
              and condition.get("value") in (features.get("biopsy_inferred") or [])):
            # Matched only by an expectation derived from the diagnosis label,
            # not an observed finding: counted, but labelled as an inference.
            matched.append({
                "condition": condition,
                "explanation": (f"{explanation} (inferred from the biopsy diagnosis; "
                                f"not an observed finding)").strip(),
                "weight": weight,
                "inferred": True,
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

    # Name resolution, best source first. Seven disease_ids used by active rules
    # have no Disease row ("hypertensiveNephrosclerosis", "infectionRelated",
    # ...), and the raw camelCase id was being shown to clinicians in the
    # differential. The rule itself carries a proper name, so use it before
    # falling back to the id.
    disease_name = ""
    try:
        from .models import Disease
        disease_obj = Disease.objects.get(pk=entry.disease_id)
        disease_name = disease_obj.name or ""
    except Exception:
        pass
    if not disease_name:
        disease_name = (entry.rule_data or {}).get("disease_name") or ""
    if not disease_name:
        disease_name = entry.disease_id

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

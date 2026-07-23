"""Care Pathway Engine — dynamic stage transitions, pathway definitions, and deviation detection."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from clinical_reasoning.json_util import json_safe

logger = logging.getLogger(__name__)


@dataclass
class PathwayStage:
    name: str
    label: str
    description: str
    typical_duration_days: int | None = None
    required_actions: list[str] = None
    next_stages: list[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "typical_duration_days": self.typical_duration_days,
            "required_actions": self.required_actions or [],
            "next_stages": self.next_stages or [],
        }


# Standard GN care pathway definition
PATHWAY_DEFINITION: dict[str, PathwayStage] = {
    "assessment": PathwayStage(
        name="assessment",
        label="Initial Assessment",
        description="Diagnostic workup: biopsy, labs, imaging",
        typical_duration_days=30,
        required_actions=["biopsy", "serology", "urinalysis", "egfr"],
        next_stages=["active_disease", "remission_monitoring", "ckd_management"],
    ),
    "active_disease": PathwayStage(
        name="active_disease",
        label="Active Disease / Induction",
        description="Active disease requiring immunosuppression",
        typical_duration_days=180,
        required_actions=["immunosuppression", "monthly_monitoring", "counseling"],
        next_stages=["remission_monitoring", "relapse", "ckd_management"],
    ),
    "remission_monitoring": PathwayStage(
        name="remission_monitoring",
        label="Remission / Maintenance",
        description="Disease in remission on maintenance therapy",
        typical_duration_days=730,
        required_actions=["maintenance_tx", "quarterly_monitoring", "vaccination"],
        next_stages=["relapse", "ckd_management", "eskd_care"],
    ),
    "relapse": PathwayStage(
        name="relapse",
        label="Relapse",
        description="Disease relapse after remission",
        typical_duration_days=180,
        required_actions=["reinduction", "intensified_monitoring", "adherence_check"],
        next_stages=["remission_monitoring", "ckd_management"],
    ),
    "ckd_management": PathwayStage(
        name="ckd_management",
        label="CKD Management",
        description="Chronic kidney disease without active GN",
        typical_duration_days=1825,
        required_actions=["nephroprotection", "bp_control", "cardiovascular_screening"],
        next_stages=["eskd_care", "post_transplant", "conservative_care"],
    ),
    "eskd_care": PathwayStage(
        name="eskd_care",
        label="ESKD / RRT",
        description="End-stage kidney disease on renal replacement therapy",
        typical_duration_days=None,
        required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
        next_stages=["post_transplant"],
    ),
    "post_transplant": PathwayStage(
        name="post_transplant",
        label="Post-Transplant",
        description="Post-kidney transplant care",
        typical_duration_days=None,
        required_actions=["immunosuppression", "rejection_monitoring", "infection_prophylaxis"],
        next_stages=["ckd_management"],
    ),
    "conservative_care": PathwayStage(
        name="conservative_care",
        label="Conservative Care",
        description="Non-dialysis supportive care",
        typical_duration_days=None,
        required_actions=["symptom_management", "advance_care_planning", "palliative_referral"],
        next_stages=[],
    ),
}


def get_pathway_stage(stage_name: str) -> PathwayStage | None:
    return PATHWAY_DEFINITION.get(stage_name)


def get_available_stages() -> list[dict]:
    return [s.to_dict() for s in PATHWAY_DEFINITION.values()]


def determine_current_stage(patient, features: dict, disease_id: str | None = None) -> str:
    """Determine the current care pathway stage from patient data.

    Uses disease_id for disease-specific stage logic if available,
    otherwise falls back to the generic stage determination.
    """
    phase = features.get("disease_phase", "")
    egfr = getattr(patient, "latest_egfr", None)

    eskd = egfr is not None and float(egfr) < 15
    if phase == "eskd" or eskd:
        return "eskd_care"

    # Disease-specific stage overrides
    if disease_id:
        ds_map = _disease_specific_stage_map(disease_id, features)
        if ds_map and phase in ds_map:
            return ds_map[phase]

    phase_map = {
        "active": "active_disease",
        "relapse": "relapse",
        "remission": "remission_monitoring",
        "ckd": "ckd_management",
        "post_transplant": "post_transplant",
        "conservative": "conservative_care",
    }
    return phase_map.get(phase, "assessment")


def detect_stage_transition(patient, old_stage: str, new_stage: str) -> dict | None:
    """Detect whether a stage transition is valid and log it."""
    if old_stage == new_stage:
        return None

    stage = PATHWAY_DEFINITION.get(old_stage)
    if stage and new_stage in stage.next_stages:
        return {
            "from_stage": old_stage,
            "to_stage": new_stage,
            "valid": True,
            "message": f"Transition from {old_stage} to {new_stage} is clinically valid",
        }

    valid_transitions = {old_stage: stage.next_stages} if stage else []
    return {
        "from_stage": old_stage,
        "to_stage": new_stage,
        "valid": False,
        "message": f"Unexpected transition from {old_stage} to {new_stage}",
        "expected_next": valid_transitions,
    }


def assess_pathway_deviation(patient, current_stage: str, features: dict) -> list[dict]:
    """Detect deviations from the expected care pathway."""
    deviations = []
    stage = PATHWAY_DEFINITION.get(current_stage)
    if not stage:
        return deviations

    required = stage.required_actions or []

    if "biopsy" in required:
        try:
            if not patient.biopsies.exists():
                deviations.append({
                    "stage": current_stage,
                    "issue": "missing_biopsy",
                    "severity": "high",
                    "message": "Required renal biopsy not performed",
                })
        except Exception:
            pass

    if "egfr" in required and getattr(patient, "latest_egfr", None) is None:
        deviations.append({
            "stage": current_stage,
            "issue": "missing_egfr",
            "severity": "high",
            "message": "eGFR not available for staging",
        })

    return deviations


def compute_pathway_summary(patient, current_stage: str, deviations: list, milestones: list) -> dict:
    """Build a comprehensive summary of the patient's pathway status."""
    stage = PATHWAY_DEFINITION.get(current_stage)
    return {
        "current_stage": current_stage,
        "stage_label": stage.label if stage else current_stage,
        "stage_description": stage.description if stage else "",
        "days_in_stage": _days_in_stage(patient, current_stage),
        "deviations": deviations,
        "deviations_count": len(deviations),
        "milestones_in_pathway": len(milestones),
    }


def _days_in_stage(patient, current_stage: str) -> int | None:
    """Estimate days in current stage from milestones or phase changes."""
    try:
        phase = getattr(patient, "current_phase", "")
        reg_date = getattr(patient, "registration_date", None) or getattr(patient, "enrollment_date", None)
        if reg_date and phase:
            return (date.today() - reg_date).days
    except Exception:
        pass
    return None


def _disease_specific_stage_map(disease_id: str, features: dict) -> dict[str, str] | None:
    """Return a disease-specific phase-to-stage mapping if available.

    Covers at least 5 diseases: IgA, Membranous, Lupus, ANCA, Diabetic Nephropathy.
    """
    specific_maps: dict[str, dict[str, str]] = {
        "iga": {
            "active": "induction",
            "remission": "maintenance",
            "relapse": "relapse",
            "ckd": "ckd_progression",
            "eskd": "esrd",
        },
        "membranous": {
            "active": "induction",
            "remission": "maintenance",
            "relapse": "relapse",
            "ckd": "ckd_progression",
            "eskd": "esrd",
        },
        "lupus": {
            "active": "induction",
            "remission": "maintenance",
            "relapse": "relapse",
            "ckd": "ckd_progression",
            "eskd": "esrd",
        },
        "anca": {
            "active": "induction",
            "remission": "maintenance",
            "relapse": "relapse",
            "ckd": "ckd_progression",
            "eskd": "esrd",
        },
        "diabetic_nephropathy": {
            "active": "established_dn",
            "remission": "early_dn",
            "relapse": "established_dn",
            "ckd": "ckd_progression",
            "eskd": "esrd",
        },
    }
    return specific_maps.get(disease_id)


# ============================================================================
# Disease-Specific Pathway Stages
# ============================================================================

PATHWAY_STAGES: dict[str, list[PathwayStage]] = {
    "iga": [
        PathwayStage(
            name="diagnosis",
            label="IgA Diagnosis / Biopsy",
            description="IgA nephropathy confirmed by renal biopsy with mesangial IgA deposits",
            typical_duration_days=30,
            required_actions=["biopsy", "serology", "urinalysis", "egfr"],
            next_stages=["induction", "observation"],
        ),
        PathwayStage(
            name="induction",
            label="IgA Induction Therapy",
            description="Active IgA with proteinuria >1g/day — RAAS blockade ± immunosuppression",
            typical_duration_days=180,
            required_actions=["acei_arb", "proteinuria_monitoring", "bp_control"],
            next_stages=["maintenance", "relapse", "ckd_progression"],
        ),
        PathwayStage(
            name="maintenance",
            label="IgA Maintenance / Remission",
            description="Proteinuria <1g/day, stable eGFR on maintenance therapy",
            typical_duration_days=730,
            required_actions=["acei_arb", "quarterly_monitoring", "vaccination"],
            next_stages=["relapse", "ckd_progression", "esrd"],
        ),
        PathwayStage(
            name="relapse",
            label="IgA Relapse",
            description="Recurrent hematuria or rising proteinuria after remission",
            typical_duration_days=90,
            required_actions=["rebiopsy_consideration", "immunosuppression_review", "adherence_check"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="ckd_progression",
            label="IgA CKD Progression",
            description="Progressive eGFR decline despite therapy",
            typical_duration_days=1095,
            required_actions=["nephroprotection", "rrt_planning", "cardiovascular_screening"],
            next_stages=["esrd", "conservative_care"],
        ),
        PathwayStage(
            name="esrd",
            label="ESRD / RRT",
            description="End-stage renal disease from IgA nephropathy",
            typical_duration_days=None,
            required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
            next_stages=["post_transplant"],
        ),
    ],
    "membranous": [
        PathwayStage(
            name="diagnosis",
            label="Membranous Diagnosis",
            description="Membranous nephropathy confirmed by biopsy ± anti-PLA2R serology",
            typical_duration_days=30,
            required_actions=["biopsy", "pla2r_testing", "egfr", "proteinuria"],
            next_stages=["induction", "observation"],
        ),
        PathwayStage(
            name="induction",
            label="Membranous Induction",
            description="Active MN with nephrotic syndrome — immunosuppression (rituximab/CNI/cyclophosphamide)",
            typical_duration_days=180,
            required_actions=["immunosuppression", "pla2r_monitoring", "anticoagulation_assessment"],
            next_stages=["maintenance", "relapse", "ckd_progression"],
        ),
        PathwayStage(
            name="maintenance",
            label="Membranous Remission / Maintenance",
            description="Partial or complete remission on maintenance therapy",
            typical_duration_days=1095,
            required_actions=["quarterly_pla2r", "proteinuria_monitoring", "vaccination"],
            next_stages=["relapse", "ckd_progression", "esrd"],
        ),
        PathwayStage(
            name="relapse",
            label="Membranous Relapse",
            description="Rising PLA2R titers or proteinuria after remission",
            typical_duration_days=90,
            required_actions=["reinduction", "pla2r_trending", "adherence_check"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="ckd_progression",
            label="Membranous CKD Progression",
            description="Progressive kidney function decline",
            typical_duration_days=1095,
            required_actions=["nephroprotection", "rrt_planning", "cvd_screening"],
            next_stages=["esrd", "conservative_care"],
        ),
        PathwayStage(
            name="esrd",
            label="ESRD / RRT",
            description="End-stage renal disease from membranous nephropathy",
            typical_duration_days=None,
            required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
            next_stages=["post_transplant"],
        ),
    ],
    "lupus": [
        PathwayStage(
            name="diagnosis",
            label="Lupus Nephritis Diagnosis",
            description="SLE with renal involvement confirmed by biopsy",
            typical_duration_days=30,
            required_actions=["biopsy", "complement_c3_c4", "anti_dsdna", "urinalysis"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="induction",
            label="LN Induction Therapy",
            description="Active class III/IV LN — high-dose immunosuppression",
            typical_duration_days=180,
            required_actions=["mycophenolate_or_cyclophosphamide", "steroids", "complement_monitoring"],
            next_stages=["maintenance", "relapse", "ckd_progression"],
        ),
        PathwayStage(
            name="maintenance",
            label="LN Maintenance",
            description="Stable renal function on maintenance immunosuppression",
            typical_duration_days=730,
            required_actions=["mmf_or_aza", "quarterly_monitoring", "hcq_continuation"],
            next_stages=["relapse", "ckd_progression", "esrd"],
        ),
        PathwayStage(
            name="relapse",
            label="LN Relapse",
            description="Rising proteinuria, falling complements, or increasing anti-dsDNA",
            typical_duration_days=90,
            required_actions=["rebiopsy_consideration", "reinduction", "adherence_check"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="ckd_progression",
            label="LN CKD Progression",
            description="Chronic kidney damage from lupus nephritis",
            typical_duration_days=1095,
            required_actions=["nephroprotection", "bp_control", "cvd_screening"],
            next_stages=["esrd", "conservative_care"],
        ),
        PathwayStage(
            name="esrd",
            label="ESRD / RRT",
            description="End-stage renal disease from lupus nephritis",
            typical_duration_days=None,
            required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
            next_stages=["post_transplant"],
        ),
    ],
    "anca": [
        PathwayStage(
            name="diagnosis",
            label="ANCA Vasculitis Diagnosis",
            description="ANCA-associated vasculitis with renal involvement confirmed by biopsy",
            typical_duration_days=30,
            required_actions=["biopsy", "anca_serology", "ent_assessment", "chest_imaging"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="induction",
            label="ANCA Induction Therapy",
            description="Active vasculitis — high-dose steroids + cyclophosphamide or rituximab",
            typical_duration_days=180,
            required_actions=["rituximab_or_cyclophosphamide", "steroid_taper", "pjp_prophylaxis"],
            next_stages=["maintenance", "relapse", "ckd_progression"],
        ),
        PathwayStage(
            name="maintenance",
            label="ANCA Maintenance",
            description="In remission on maintenance immunosuppression",
            typical_duration_days=730,
            required_actions=["rituximab_or_aza", "anca_titer_monitoring", "vaccination"],
            next_stages=["relapse", "ckd_progression", "esrd"],
        ),
        PathwayStage(
            name="relapse",
            label="ANCA Relapse",
            description="Rising ANCA titers with clinical activity",
            typical_duration_days=90,
            required_actions=["reinduction", "anca_trending", "ent_reassessment"],
            next_stages=["induction", "maintenance"],
        ),
        PathwayStage(
            name="ckd_progression",
            label="ANCA CKD Progression",
            description="Chronic kidney damage from vasculitis",
            typical_duration_days=1095,
            required_actions=["nephroprotection", "bp_control", "cvd_screening"],
            next_stages=["esrd", "conservative_care"],
        ),
        PathwayStage(
            name="esrd",
            label="ESRD / RRT",
            description="End-stage renal disease from ANCA vasculitis",
            typical_duration_days=None,
            required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
            next_stages=["post_transplant"],
        ),
    ],
    "diabetic_nephropathy": [
        PathwayStage(
            name="diagnosis",
            label="DN Diagnosis / Screening",
            description="Diabetic nephropathy — microalbuminuria or reduced eGFR in diabetic patient",
            typical_duration_days=30,
            required_actions=["acr", "egfr", "fundoscopy", "glycemic_assessment"],
            next_stages=["early_dn", "established_dn", "ckd_progression"],
        ),
        PathwayStage(
            name="early_dn",
            label="Early Diabetic Nephropathy",
            description="Microalbuminuria with preserved eGFR — intensive risk factor control",
            typical_duration_days=730,
            required_actions=["acei_arb", "sglt2i", "glycemic_control", "bp_control"],
            next_stages=["established_dn", "ckd_progression"],
        ),
        PathwayStage(
            name="established_dn",
            label="Established Diabetic Nephropathy",
            description="Macroalbuminuria or eGFR <60 — comprehensive CKD care",
            typical_duration_days=1095,
            required_actions=["acei_arb", "sglt2i_or_glp1", "multidisciplinary_care", "foot_care"],
            next_stages=["ckd_progression", "esrd"],
        ),
        PathwayStage(
            name="ckd_progression",
            label="DN CKD Progression",
            description="Progressive eGFR decline in diabetic kidney disease",
            typical_duration_days=730,
            required_actions=["nephroprotection", "rrt_planning", "cardiovascular_screening"],
            next_stages=["esrd", "conservative_care"],
        ),
        PathwayStage(
            name="esrd",
            label="ESRD / RRT",
            description="End-stage renal disease from diabetic nephropathy",
            typical_duration_days=None,
            required_actions=["rrt_access", "transplant_evaluation", "palliative_care"],
            next_stages=["post_transplant"],
        ),
    ],
}


def get_pathway_stages(disease_id: str) -> list[dict]:
    """Return disease-specific pathway stages as a list of dicts."""
    stages = PATHWAY_STAGES.get(disease_id)
    if stages:
        return [s.to_dict() for s in stages]
    # Fall back to generic stages
    return get_available_stages()

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


def determine_current_stage(patient, features: dict) -> str:
    """Determine the current care pathway stage from patient data."""
    phase = features.get("disease_phase", "")
    egfr = getattr(patient, "latest_egfr", None)

    eskd = egfr is not None and float(egfr) < 15
    if phase == "eskd" or eskd:
        return "eskd_care"

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

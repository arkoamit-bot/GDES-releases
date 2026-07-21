"""Shared logic for management plan generation.

Contains the ``ManagementPlan`` dataclass, the public ``generate_management_plan``
function, and all helper functions used by the generation pipeline.  Individual
disease profiles live in the ``profiles/`` sub-package and register themselves
with the :class:`ProfileRegistry`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .registry import ProfileRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ManagementPlan dataclass
# ---------------------------------------------------------------------------

@dataclass
class ManagementPlan:
    """Structured output of the management plan generator."""
    disease_id: str
    disease_name: str
    patient_id: str
    first_line: list[dict]
    second_line: list[dict]
    rescue_therapy: list[dict]
    contraindicated: list[str]
    monitoring: list[dict]
    follow_up: dict
    general_measures: list[dict]
    safety_checks: list[dict]
    patient_education: list[dict]

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "disease_name": self.disease_name,
            "patient_id": self.patient_id,
            "first_line": self.first_line,
            "second_line": self.second_line,
            "rescue_therapy": self.rescue_therapy,
            "contraindicated": self.contraindicated,
            "monitoring": self.monitoring,
            "follow_up": self.follow_up,
            "general_measures": self.general_measures,
            "safety_checks": self.safety_checks,
            "patient_education": self.patient_education,
        }


# ---------------------------------------------------------------------------
# Public generation function
# ---------------------------------------------------------------------------

def generate_management_plan(
    patient,
    disease_id: str,
    features: dict | None = None,
    risk_category: str = "moderate",
) -> ManagementPlan:
    """Generate a personalized management plan for a patient.

    Args:
        patient: Patient model instance
        disease_id: Disease identifier (e.g., "iga", "membranous")
        features: Optional pre-extracted patient features
        risk_category: Risk level from risk assessment
            ("low", "moderate", "high", "very_high")

    Returns:
        ManagementPlan dataclass with all recommendations
    """
    profile = ProfileRegistry.get(disease_id)
    if not profile:
        return _build_default_plan(patient, disease_id)

    plan = ManagementPlan(
        disease_id=disease_id,
        disease_name=profile["disease_name"],
        patient_id=patient.patient_id,
        first_line=profile.get("first_line", []),
        second_line=profile.get("second_line", []),
        rescue_therapy=profile.get("rescue_therapy", []),
        contraindicated=profile.get("contraindicated", []),
        monitoring=profile.get("monitoring", []),
        follow_up=profile.get("follow_up", {}),
        general_measures=_build_general_measures(disease_id, features or {}),
        safety_checks=_build_safety_checks(patient, disease_id, features or {}),
        patient_education=_build_patient_education(disease_id),
    )

    # Adjust monitoring intensity based on risk category
    if risk_category in ("high", "very_high"):
        plan = _intensify_monitoring(plan, risk_category)

    # Add CKD-specific modifications
    if features and features.get("egfrTrend") == "reduced":
        plan = _add_ckd_modifications(plan, features)

    return plan


# ---------------------------------------------------------------------------
# Helper functions (private)
# ---------------------------------------------------------------------------

def _build_general_measures(disease_id: str, features: dict) -> list[dict]:
    """Build general non-pharmacological measures."""
    measures = [
        {
            "category": "Blood pressure",
            "recommendation": "Target <130/80 mmHg (KDIGO 2021)",
            "rationale": "RAAS blockade is preferred antihypertensive in proteinuric GN",
        },
        {
            "category": "Dietary sodium",
            "recommendation": "Restrict to <2g/day sodium (5g/day salt)",
            "rationale": "Reduces proteinuria and blood pressure",
        },
        {
            "category": "Protein intake",
            "recommendation": "0.8-1.0 g/kg/day (avoid high protein)",
            "rationale": "High protein accelerates kidney disease progression",
        },
        {
            "category": "Vaccination",
            "recommendation": "Update pneumococcal, influenza, hepatitis B, COVID-19 vaccines before immunosuppression",
            "rationale": "Immunosuppressed patients at high risk; live vaccines contraindicated on treatment",
        },
    ]

    if features.get("edema") or features.get("proteinuria") == "nephrotic":
        measures.append({
            "category": "Edema management",
            "recommendation": "Salt restriction, loop diuretics as needed, leg elevation",
            "rationale": "Nephrotic edema requires both dietary and pharmacological management",
        })

    return measures


def _build_safety_checks(patient, disease_id: str, features: dict) -> list[dict]:
    """Build safety checks and contraindication warnings."""
    checks = []

    # Check for existing contraindications
    profile = ProfileRegistry.get(disease_id) or {}
    contraindicated = profile.get("contraindicated", [])
    if contraindicated:
        checks.append({
            "type": "contraindication",
            "level": "critical",
            "message": f"Contraindicated medications for {profile.get('disease_name', disease_id)}: {', '.join(contraindicated)}",
        })

    # Pregnancy check
    if hasattr(patient, "sex") and patient.sex == "F":
        checks.append({
            "type": "pregnancy_screening",
            "level": "moderate",
            "message": "If pregnancy is possible, avoid mycophenolate, cyclophosphamide, ACEi/ARBs, and statins. Consult maternal-fetal medicine.",
        })

    # Drug interaction warning (if on multiple immunosuppressants)
    if disease_id in ("lupus", "anca", "antiGbm"):
        checks.append({
            "type": "infection_risk",
            "level": "high",
            "message": "Active immunosuppression: monitor for infection. PJP prophylaxis (trimethoprim-sulfamethoxazole) if on high-dose steroids or combination immunosuppression.",
        })

    return checks


def _build_patient_education(disease_id: str) -> list[dict]:
    """Build patient education points."""
    education = [
        {
            "topic": "Medication adherence",
            "message": "Take medications as prescribed. Do not stop steroids abruptly without medical advice.",
        },
        {
            "topic": "Infection prevention",
            "message": "Report fever, cough, or signs of infection immediately. Avoid crowds during immunosuppression.",
        },
        {
            "topic": "Dietary compliance",
            "message": "Follow salt and protein restrictions. Maintain adequate hydration.",
        },
    ]

    if disease_id in ("iga", "membranous", "fsgs"):
        education.append({
            "topic": "Proteinuria monitoring",
            "message": "Regular urine tests are essential to monitor disease activity. Bring a fresh urine sample to each visit.",
        })

    if disease_id in ("lupus", "anca"):
        education.append({
            "topic": "Disease flare recognition",
            "message": "Know the signs of relapse: increased swelling, reduced urine output, rash, joint pain, or fever. Contact your nephrologist immediately.",
        })

    return education


def _intensify_monitoring(plan: ManagementPlan, risk_category: str) -> ManagementPlan:
    """Intensify monitoring for high-risk patients."""
    for monitor in plan.monitoring:
        interval = monitor.get("interval", "")
        if "quarterly" in interval:
            monitor["interval"] = interval.replace("quarterly", "monthly")
        elif "monthly" in interval and risk_category == "very_high":
            monitor["interval"] = "every 2 weeks"

    # Add high-risk specific monitoring
    if risk_category == "very_high":
        plan.monitoring.append({
            "parameter": "Urgent nephrology review",
            "interval": "every 2 weeks",
            "target": "Clinical stability",
            "action_threshold": "Any clinical deterioration",
        })

    return plan


def _add_ckd_modifications(plan: ManagementPlan, features: dict) -> ManagementPlan:
    """Add CKD-specific modifications to the plan."""
    plan.monitoring.append({
        "parameter": "CKD-MBD screening (calcium, phosphate, PTH, vitamin D)",
        "interval": "every 3-6 months (eGFR <45)",
        "target": "Calcium 8.5-10.5, phosphate <4.5, PTH 2-9× ULN",
        "action_threshold": "CKD-MBD detected",
    })
    plan.monitoring.append({
        "parameter": "Anemia screening (hemoglobin, iron studies)",
        "interval": "every 3 months (eGFR <60)",
        "target": "Hb >11 g/dL",
        "action_threshold": "Anemia (Hb <11)",
    })
    return plan


def _build_default_plan(patient, disease_id: str) -> ManagementPlan:
    """Build a default plan for diseases not in the protocol database."""
    return ManagementPlan(
        disease_id=disease_id,
        disease_name=disease_id.replace("_", " ").title(),
        patient_id=patient.patient_id,
        first_line=[{
            "drug": "Nephrology consultation",
            "dose": "Per specialist recommendation",
            "duration": "As determined by nephrologist",
            "target": "Disease-specific goals",
            "rationale": "No specific protocol available; individualize treatment plan",
            "evidence_grade": "OP",
        }],
        second_line=[],
        rescue_therapy=[],
        contraindicated=[],
        monitoring=[{
            "parameter": "Serum creatinine/eGFR",
            "interval": "monthly",
            "target": "Stable",
            "action_threshold": ">20% decline",
        }],
        follow_up={"induction_phase": "Every 2-4 weeks", "maintenance_phase": "Every 3 months"},
        general_measures=_build_general_measures(disease_id, {}),
        safety_checks=_build_safety_checks(patient, disease_id, {}),
        patient_education=_build_patient_education(disease_id),
    )

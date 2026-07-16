"""Monitoring Plan Generator â€” generates disease-specific and treatment-specific
monitoring protocols with risk-adjusted intervals.

Aligns with GDES vision: "automated monitoring plan generation based on disease
type, treatment, and individual risk factors."
"""
from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Disease-specific monitoring protocols (KDIGO-aligned)
# ---------------------------------------------------------------------------

DISEASE_MONITORING_PROTOCOLS: dict[str, dict[str, Any]] = {
    "iga": {
        "disease_name": "IgA Nephropathy",
        "parameters": [
            {"name": "24h UTP (g/day)", "interval_days": 30, "target": "<0.5 g/day", "alert_above": 1.0, "unit": "g/day"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "Blood pressure", "interval_days": 14, "target": "<130/80 mmHg", "alert_above": "140/90", "unit": "mmHg"},
            {"name": "Serum potassium", "interval_days": 30, "target": "3.5-5.0 mEq/L", "alert_above": 5.5, "unit": "mEq/L"},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "mL/min/1.73mÂ²"},
        ],
        "treatment_monitoring": {
            "acei_arb": [
                {"name": "Potassium", "interval_days": 14, "target": "3.5-5.0", "alert_above": 5.5},
                {"name": "Creatinine", "interval_days": 14, "target": "Stable", "alert_pct_decline": 30},
            ],
            "sglt2_inhibitor": [
                {"name": "eGFR", "interval_days": 14, "target": "Stable", "alert_pct_decline": 30},
                {"name": "HbA1c", "interval_days": 90, "target": "<7%", "alert_above": 9},
            ],
            "corticosteroid": [
                {"name": "Blood glucose", "interval_days": 7, "target": "<200 mg/dL", "alert_above": 250},
                {"name": "Blood pressure", "interval_days": 14, "target": "<140/90", "alert_above": 160/100},
            ],
        },
    },
    "membranous": {
        "disease_name": "Membranous Nephropathy",
        "parameters": [
            {"name": "PLA2R antibody", "interval_days": 90, "target": "Undetectable", "alert_if_persistent": True, "unit": "EU/mL"},
            {"name": "24h UTP (g/day)", "interval_days": 30, "target": "<0.3 g/day", "alert_above": 3.5, "unit": "g/day"},
            {"name": "Serum albumin", "interval_days": 30, "target": ">3.0 g/dL", "alert_below": 2.5, "unit": "g/dL"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "mL/min/1.73mÂ²"},
        ],
        "treatment_monitoring": {
            "rituximab": [
                {"name": "CD19+ B-cells", "interval_days": 90, "target": "<5 cells/ÂµL", "alert_above": 10},
                {"name": "Immunoglobulins", "interval_days": 180, "target": "Normal", "alert_below": 400},
            ],
            "cyclophosphamide": [
                {"name": "CBC with differential", "interval_days": 14, "target": "WBC >3000", "alert_below": 2500},
            ],
        },
    },
    "mcd": {
        "disease_name": "Minimal Change Disease",
        "parameters": [
            {"name": "24h UTP (g/day)", "interval_days": 14, "target": "<0.3 g/day", "alert_above": 3.5, "unit": "g/day"},
            {"name": "Serum albumin", "interval_days": 30, "target": ">3.5 g/dL", "alert_below": 3.0, "unit": "g/dL"},
            {"name": "Blood glucose", "interval_days": 7, "target": "<200 mg/dL", "alert_above": 250, "unit": "mg/dL"},
            {"name": "Blood pressure", "interval_days": 14, "target": "<130/80 mmHg", "alert_above": "140/90", "unit": "mmHg"},
        ],
        "treatment_monitoring": {
            "corticosteroid": [
                {"name": "Blood glucose", "interval_days": 7, "target": "<200 mg/dL", "alert_above": 250},
                {"name": "Blood pressure", "interval_days": 14, "target": "<140/90", "alert_above": 160/100},
            ],
            "rituximab": [
                {"name": "CD19+ B-cells", "interval_days": 90, "target": "<5 cells/ÂµL", "alert_above": 10},
            ],
        },
    },
    "fsgs": {
        "disease_name": "Focal Segmental Glomerulosclerosis",
        "parameters": [
            {"name": "24h UTP (g/day)", "interval_days": 30, "target": "<0.3 g/day", "alert_above": 3.5, "unit": "g/day"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "Blood pressure", "interval_days": 14, "target": "<130/80 mmHg", "alert_above": "140/90", "unit": "mmHg"},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "mL/min/1.73mÂ²"},
        ],
        "treatment_monitoring": {
            "calcineurin_inhibitor": [
                {"name": "Drug trough level", "interval_days": 14, "target": "4-8 ng/mL", "alert_above": 10, "unit": "ng/mL"},
                {"name": "Serum creatinine", "interval_days": 14, "target": "Stable", "alert_pct_decline": 20},
                {"name": "Serum potassium", "interval_days": 14, "target": "3.5-5.0", "alert_above": 5.5},
            ],
            "corticosteroid": [
                {"name": "Blood glucose", "interval_days": 7, "target": "<200 mg/dL", "alert_above": 250},
            ],
        },
    },
    "lupus": {
        "disease_name": "Lupus Nephritis",
        "parameters": [
            {"name": "Anti-dsDNA", "interval_days": 60, "target": "Declining", "alert_if_rising": True, "unit": "IU/mL"},
            {"name": "Complement C3", "interval_days": 60, "target": "Normal range", "alert_below": 70, "unit": "mg/dL"},
            {"name": "Complement C4", "interval_days": 60, "target": "Normal range", "alert_below": 10, "unit": "mg/dL"},
            {"name": "UPCR", "interval_days": 30, "target": "<0.5 g/day", "alert_above": 1.0, "unit": "g/day"},
            {"name": "CBC with differential", "interval_days": 30, "target": "WBC >3000", "alert_below": 2500, "unit": "cells/ÂµL"},
            {"name": "Liver function (ALT)", "interval_days": 30, "target": "Normal", "alert_above": 120, "unit": "U/L"},
        ],
        "treatment_monitoring": {
            "mycophenolate": [
                {"name": "CBC with differential", "interval_days": 14, "target": "WBC >3000", "alert_below": 2500},
                {"name": "Liver function", "interval_days": 30, "target": "Normal", "alert_above": 120},
            ],
            "cyclophosphamide": [
                {"name": "CBC with differential", "interval_days": 14, "target": "WBC >2000", "alert_below": 1500},
            ],
        },
    },
    "anca": {
        "disease_name": "ANCA-Associated Vasculitis",
        "parameters": [
            {"name": "ANCA titer", "interval_days": 90, "target": "Declining", "alert_if_rising": True, "unit": "EU/mL"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "mL/min/1.73mÂ²"},
            {"name": "CBC with differential", "interval_days": 30, "target": "Normal", "alert_below": 2500, "unit": "cells/ÂµL"},
            {"name": "Urine dipstick", "interval_days": 30, "target": "No active sediment", "alert_if_abnormal": True},
        ],
        "treatment_monitoring": {
            "rituximab": [
                {"name": "CD19+ B-cells", "interval_days": 90, "target": "<5 cells/ÂµL", "alert_above": 10},
                {"name": "Immunoglobulins", "interval_days": 180, "target": "Normal", "alert_below": 400},
            ],
            "cyclophosphamide": [
                {"name": "CBC with differential", "interval_days": 14, "target": "WBC >3000", "alert_below": 2000},
            ],
        },
    },
    "antiGbm": {
        "disease_name": "Anti-GBM Disease",
        "parameters": [
            {"name": "Anti-GBM antibody", "interval_days": 14, "target": "Undetectable", "alert_if_persistent": True, "unit": "U/mL"},
            {"name": "Serum creatinine", "interval_days": 7, "target": "Stabilization", "alert_pct_decline": 50, "unit": "Âµmol/L"},
            {"name": "CBC with differential", "interval_days": 7, "target": "Normal", "alert_below": 2000, "unit": "cells/ÂµL"},
        ],
        "treatment_monitoring": {
            "plasma_exchange": [
                {"name": "Fibrinogen", "interval_days": 1, "target": ">100 mg/dL", "alert_below": 100},
                {"name": "Albumin", "interval_days": 1, "target": ">3.0 g/dL", "alert_below": 2.5},
            ],
        },
    },
    "infectionRelated": {
        "disease_name": "Infection-Related Glomerulonephritis",
        "parameters": [
            {"name": "24h UTP (g/day)", "interval_days": 30, "target": "<0.5 g/day", "alert_above": 1.0, "unit": "g/day"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Improving", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "Complement C3", "interval_days": 30, "target": "Normalizing", "alert_if_persistent_low": True, "unit": "mg/dL"},
        ],
        "treatment_monitoring": {},
    },
    "c3": {
        "disease_name": "C3 Glomerulopathy",
        "parameters": [
            {"name": "C3 level", "interval_days": 30, "target": "Normal range", "alert_below": 70, "unit": "mg/dL"},
            {"name": "24h UTP (g/day)", "interval_days": 30, "target": "<0.5 g/day", "alert_above": 1.0, "unit": "g/day"},
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "Âµmol/L"},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20, "unit": "mL/min/1.73mÂ²"},
        ],
        "treatment_monitoring": {
            "complement_inhibitor": [
                {"name": "CH50", "interval_days": 30, "target": "Normal", "alert_below": 10},
                {"name": "C3 level", "interval_days": 30, "target": "Normal", "alert_below": 70},
            ],
        },
    },
}


# CKD stage-specific additional monitoring
CKD_STAGE_MONITORING: dict[int, list[dict[str, Any]]] = {
    3: [
        {"name": "CKD-MBD panel (Ca/PO4/PTH)", "interval_days": 180, "target": "Normal range", "alert_if_abnormal": True},
        {"name": "Hemoglobin", "interval_days": 90, "target": ">11 g/dL", "alert_below": 11, "unit": "g/dL"},
    ],
    4: [
        {"name": "CKD-MBD panel (Ca/PO4/PTH)", "interval_days": 90, "target": "Normal range", "alert_if_abnormal": True},
        {"name": "Hemoglobin", "interval_days": 90, "target": ">11 g/dL", "alert_below": 11, "unit": "g/dL"},
        {"name": "Serum potassium", "interval_days": 30, "target": "3.5-5.0", "alert_above": 5.5, "unit": "mEq/L"},
        {"name": "Bicarbonate", "interval_days": 90, "target": ">22 mEq/L", "alert_below": 20, "unit": "mEq/L"},
    ],
    5: [
        {"name": "CKD-MBD panel (Ca/PO4/PTH)", "interval_days": 60, "target": "Normal range", "alert_if_abnormal": True},
        {"name": "Hemoglobin", "interval_days": 60, "target": ">11 g/dL", "alert_below": 11, "unit": "g/dL"},
        {"name": "Serum potassium", "interval_days": 14, "target": "3.5-5.0", "alert_above": 5.5, "unit": "mEq/L"},
        {"name": "Bicarbonate", "interval_days": 60, "target": ">22 mEq/L", "alert_below": 20, "unit": "mEq/L"},
        {"name": "Volume status (weight/edema)", "interval_days": 7, "target": "Dry weight", "alert_if_gain": ">2kg/week"},
    ],
}


@dataclass
class MonitoringPlan:
    """Structured output of the monitoring plan generator."""
    disease_id: str
    disease_name: str
    patient_id: str
    parameters: list[dict[str, Any]]
    treatment_monitoring: list[dict[str, Any]]
    ckd_monitoring: list[dict[str, Any]]
    risk_adjustments: list[str]
    generated_date: str

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "disease_name": self.disease_name,
            "patient_id": self.patient_id,
            "parameters": self.parameters,
            "treatment_monitoring": self.treatment_monitoring,
            "ckd_monitoring": self.ckd_monitoring,
            "risk_adjustments": self.risk_adjustments,
            "generated_date": self.generated_date,
        }


def generate_monitoring_plan(
    patient,
    disease_id: str,
    active_treatments: list[str] | None = None,
    ckd_stage: int | None = None,
    risk_category: str = "moderate",
) -> MonitoringPlan:
    """Generate a personalized monitoring plan.

    Args:
        patient: Patient model instance
        disease_id: Disease identifier
        active_treatments: List of treatment class keys (e.g., ["acei_arb", "rituximab"])
        ckd_stage: CKD stage (3-5) for additional monitoring
        risk_category: Risk level for interval adjustment

    Returns:
        MonitoringPlan dataclass
    """
    protocol = DISEASE_MONITORING_PROTOCOLS.get(disease_id)
    if not protocol:
        return _build_default_monitoring_plan(patient, disease_id)

    parameters = [dict(p) for p in protocol.get("parameters", [])]
    risk_adjustments = []

    # Collect treatment-specific monitoring
    treatment_mon = []
    treatment_protocols = protocol.get("treatment_monitoring", {})
    for tx_key in (active_treatments or []):
        if tx_key in treatment_protocols:
            for tm in treatment_protocols[tx_key]:
                treatment_mon.append({**dict(tm), "for_treatment": tx_key})

    # Collect CKD-specific monitoring
    ckd_mon = []
    if ckd_stage and ckd_stage in CKD_STAGE_MONITORING:
        ckd_mon = [dict(m) for m in CKD_STAGE_MONITORING[ckd_stage]]
        # Remove duplicate parameters
        existing_names = {p["name"].lower() for p in parameters} | {t["name"].lower() for t in treatment_mon}
        ckd_mon = [m for m in ckd_mon if m["name"].lower() not in existing_names]

    # Apply risk-based interval adjustments
    if risk_category in ("high", "very_high"):
        intensity = "very_high" if risk_category == "very_high" else "high"
        parameters, adj = _adjust_intervals(parameters, intensity)
        risk_adjustments.extend(adj)
        treatment_mon, adj2 = _adjust_intervals(treatment_mon, intensity)
        risk_adjustments.extend(adj2)
        ckd_mon, adj3 = _adjust_intervals(ckd_mon, intensity)
        risk_adjustments.extend(adj3)

    return MonitoringPlan(
        disease_id=disease_id,
        disease_name=protocol["disease_name"],
        patient_id=patient.patient_id,
        parameters=parameters,
        treatment_monitoring=treatment_mon,
        ckd_monitoring=ckd_mon,
        risk_adjustments=risk_adjustments,
        generated_date=str(dt.date.today()),
    )


def _adjust_intervals(
    params: list[dict[str, Any]], intensity: str
) -> tuple[list[dict[str, Any]], list[str]]:
    """Adjust monitoring intervals based on risk intensity.

    Returns the adjusted params and a list of adjustment descriptions.
    """
    multiplier = 0.5 if intensity == "very_high" else 0.7
    adjustments = []

    for p in params:
        if "interval_days" in p:
            old_interval = p["interval_days"]
            new_interval = max(1, int(old_interval * multiplier))
            if new_interval != old_interval:
                p["interval_days"] = new_interval
                adjustments.append(
                    f"{p['name']}: {old_interval} â†’ {new_interval} days ({intensity} risk)"
                )

    return params, adjustments


def _build_default_monitoring_plan(patient, disease_id: str) -> MonitoringPlan:
    """Build a default monitoring plan for unknown diseases."""
    return MonitoringPlan(
        disease_id=disease_id,
        disease_name=disease_id.replace("_", " ").title(),
        patient_id=patient.patient_id,
        parameters=[
            {"name": "Serum creatinine", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20},
            {"name": "eGFR", "interval_days": 30, "target": "Stable", "alert_pct_decline": 20},
            {"name": "Blood pressure", "interval_days": 14, "target": "<130/80", "alert_above": "140/90"},
        ],
        treatment_monitoring=[],
        ckd_monitoring=[],
        risk_adjustments=[],
        generated_date=str(dt.date.today()),
    )


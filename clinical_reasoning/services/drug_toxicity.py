"""Drug Toxicity Detection — Obj 6a of GDES V6.

Auto-detects potential drug toxicity from lab values, including:
- CNI nephrotoxicity (tacrolimus, cyclosporine)
- MMF/MPA myelotoxicity and hepatotoxicity
- Steroid complications (hyperglycemia, osteoporosis)
- Rituximab-related hypogammaglobulinemia
- Cyclophosphamide leukopenia
- ACEi/ARB hyperkalemia
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Drug Toxicity Profiles
# ---------------------------------------------------------------------------

@dataclass
class ToxicityRule:
    """Defines a toxicity detection rule for a specific drug."""
    drug_class: str
    drug_name: str
    lab_test: str
    severity_thresholds: dict[str, float]  # mild, moderate, severe, critical
    mechanism: str
    clinical_action: str
    monitoring_frequency: str
    risk_factors: list[str] = field(default_factory=list)
    contraindication_check: str = ""
    direction: str = "high"  # "high" = higher is worse (default); "low" = lower is worse (leukopenia, hypo-IgG)


# Core toxicity rules
TOXICITY_RULES: list[ToxicityRule] = [
    # CNI Nephrotoxicity
    ToxicityRule(
        drug_class="CNI",
        drug_name="Tacrolimus",
        lab_test="serum_creatinine",
        severity_thresholds={"mild": 1.3, "moderate": 1.8, "severe": 2.5, "critical": 3.5},
        mechanism="Afferent arteriolar vasoconstriction, TMA, chronic interstitial fibrosis",
        clinical_action="Trough level check, dose reduction, consider conversion to belatacept/mTORi",
        monitoring_frequency="Trough levels q2-3 months",
        risk_factors=["dehydration", "nephrotoxic_drugs", "diabetes"],
        contraindication_check="",
    ),
    ToxicityRule(
        drug_class="CNI",
        drug_name="Cyclosporine",
        lab_test="serum_creatinine",
        severity_thresholds={"mild": 1.3, "moderate": 1.8, "severe": 2.5, "critical": 3.5},
        mechanism="Afferent arteriolar vasoconstriction, chronic nephrotoxicity",
        clinical_action="Trough level check, dose reduction, monitor blood pressure",
        monitoring_frequency="Trough levels q2-3 months",
        risk_factors=["hypertension", "hyperlipidemia"],
        contraindication_check="",
    ),
    # MMF/MPA Hepatotoxicity
    ToxicityRule(
        drug_class="IMPDH inhibitor",
        drug_name="Mycophenolate mofetil",
        lab_test="ALT",
        severity_thresholds={"mild": 60, "moderate": 120, "severe": 240, "critical": 500},
        mechanism="Hepatocellular injury, dose-dependent",
        clinical_action="Dose reduction, LFT monitoring q2 weeks, consider switching to azathioprine",
        monitoring_frequency="LFT q2 weeks during initiation",
        risk_factors=["pre-existing liver disease", "viral hepatitis"],
        contraindication_check="pregnancy",
    ),
    # MMF/MPA Myelotoxicity
    ToxicityRule(
        drug_class="IMPDH inhibitor",
        drug_name="Mycophenolate mofetil",
        lab_test="WBC",
        severity_thresholds={"mild": 3.5, "moderate": 2.5, "severe": 1.5, "critical": 0.8},
        mechanism="Bone marrow suppression via IMPDH inhibition",
        clinical_action="Dose reduction, growth factor support, consider switching to azathioprine",
        monitoring_frequency="CBC q2 weeks during initiation, then monthly",
        risk_factors=["renal impairment", "concomitant TMP-SMX", "CMV infection"],
        contraindication_check="pregnancy",
        direction="low",
    ),
    # Cyclophosphamide Leukopenia
    ToxicityRule(
        drug_class="Alkylating agent",
        drug_name="Cyclophosphamide",
        lab_test="WBC",
        severity_thresholds={"mild": 3.0, "moderate": 2.0, "severe": 1.0, "critical": 0.5},
        mechanism="Dose-dependent bone marrow suppression, nadir at 10-14 days",
        clinical_action="Hold dose, G-CSF support, infection prophylaxis",
        monitoring_frequency="CBC weekly during treatment, q2 weeks after",
        risk_factors=["renal impairment", "age>60", "concomitant myelosuppressive agents"],
        contraindication_check="pregnancy_desire",
        direction="low",
    ),
    # Rituximab Hypogammaglobulinemia
    ToxicityRule(
        drug_class="Anti-CD20",
        drug_name="Rituximab",
        lab_test="immunoglobulin_g",
        severity_thresholds={"mild": 600, "moderate": 400, "severe": 200, "critical": 100},
        mechanism="B-cell depletion reduces immunoglobulin production",
        clinical_action="IVIG replacement if recurrent infections, avoid live vaccines",
        monitoring_frequency="Ig levels q6 months, immunoglobulins q3 months",
        risk_factors=["concomitant steroids", "prior hypogammaglobulinemia", "age>65"],
        contraindication_check="",
        direction="low",
    ),
    # Steroid Hyperglycemia
    ToxicityRule(
        drug_class="Corticosteroid",
        drug_name="Prednisolone",
        lab_test="glucose_fasting",
        severity_thresholds={"mild": 7.0, "moderate": 10.0, "severe": 15.0, "critical": 22.0},
        mechanism="Insulin resistance, hepatic gluconeogenesis",
        clinical_action="Diabetes management, steroid dose reduction, glucose monitoring",
        monitoring_frequency="Fingerstick glucose daily during high-dose, q1-2 weeks during taper",
        risk_factors=["obesity", "family history diabetes", "PCOS"],
        contraindication_check="",
    ),
    # ACEi/ARB Hyperkalemia
    ToxicityRule(
        drug_class="RAAS inhibitor",
        drug_name="ACEi/ARB",
        lab_test="potassium",
        severity_thresholds={"mild": 5.5, "moderate": 6.0, "severe": 6.5, "critical": 7.0},
        mechanism="Reduced aldosterone secretion, decreased renal K+ excretion",
        clinical_action="K+ monitoring, dietary K+ restriction, consider adding loop diuretic or K+ binder",
        monitoring_frequency="K+ at 1 week, 1 month, then q3 months",
        risk_factors=["CKD stage 4-5", "diabetes", "concomitant K+ sparing diuretic", "NSAIDs"],
        contraindication_check="pregnancy",
    ),
    # mTOR Inhibitor Proteinuria
    ToxicityRule(
        drug_class="mTOR inhibitor",
        drug_name="Sirolimus/Everolimus",
        lab_test="proteinuria_upcr",
        severity_thresholds={"mild": 0.5, "moderate": 1.0, "severe": 2.0, "critical": 3.5},
        mechanism="Podocyte injury, foot process effacement",
        clinical_action="Dose reduction or discontinuation, switch to CNI or belatacept",
        monitoring_frequency="UPCR q1-2 months",
        risk_factors=["pre-existing proteinuria", "concomitant CNI", "poorly controlled BP"],
        contraindication_check="",
    ),
]


# ---------------------------------------------------------------------------
# Drug Toxicity Detection Engine
# ---------------------------------------------------------------------------

@dataclass
class ToxicityAlert:
    """A single toxicity alert."""
    drug_class: str
    drug_name: str
    lab_test: str
    current_value: float
    severity: str  # mild, moderate, severe, critical
    threshold: float
    mechanism: str
    clinical_action: str
    monitoring_frequency: str
    risk_factors: list[str]
    priority: str  # urgent, high, medium, low

    def to_dict(self) -> dict:
        return {
            "drug_class": self.drug_class,
            "drug_name": self.drug_name,
            "lab_test": self.lab_test,
            "current_value": self.current_value,
            "severity": self.severity,
            "threshold": self.threshold,
            "mechanism": self.mechanism,
            "clinical_action": self.clinical_action,
            "monitoring_frequency": self.monitoring_frequency,
            "risk_factors": self.risk_factors,
            "priority": self.priority,
        }


@dataclass
class DrugToxicityReport:
    """Complete drug toxicity report for a patient."""
    patient_id: str
    alerts: list[ToxicityAlert]
    current_medications: list[dict]
    summary: str

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "alerts": [a.to_dict() for a in self.alerts],
            "current_medications": self.current_medications,
            "summary": self.summary,
            "total_alerts": len(self.alerts),
            "critical_count": sum(1 for a in self.alerts if a.severity == "critical"),
            "severe_count": sum(1 for a in self.alerts if a.severity == "severe"),
        }


def detect_drug_toxicity(patient) -> DrugToxicityReport:
    """Detect potential drug toxicity from current medications and lab values.

    Args:
        patient: Patient model instance

    Returns:
        DrugToxicityReport with alerts for any detected toxicity
    """
    current_meds = _get_current_medications(patient)
    lab_values = _get_recent_lab_values(patient)
    risk_factors = _assess_risk_factors(patient)
    alerts: list[ToxicityAlert] = []

    for med in current_meds:
        med_name = med.get("name", "")
        med_class = med.get("drug_class", "")

        for rule in TOXICITY_RULES:
            if _medication_matches_rule(med_name, med_class, rule):
                lab_val = lab_values.get(rule.lab_test)
                if lab_val is not None:
                    alert = _evaluate_toxicity_rule(rule, lab_val, risk_factors)
                    if alert:
                        alerts.append(alert)

    alerts.sort(key=lambda a: _severity_order(a.severity))
    summary = _build_toxicity_summary(alerts, current_meds)

    return DrugToxicityReport(
        patient_id=patient.patient_id,
        alerts=alerts,
        current_medications=current_meds,
        summary=summary,
    )


def _get_current_medications(patient) -> list[dict]:
    """Current (ongoing) medications for the patient.

    Source of truth is TreatmentExposure, which the reconciliation engine
    keeps up to date from finalized prescriptions. It has a direct patient FK,
    an `ongoing` flag, and denormalized drug/dose/frequency.
    """
    from treatments.models import TreatmentExposure

    meds = []
    exposures = (
        TreatmentExposure.objects
        .filter(patient=patient, ongoing=True)
        .select_related("drug")
    )
    for e in exposures:
        meds.append({
            "name": e.drug_name or getattr(e.drug, "generic_name", ""),
            "drug_class": getattr(e.drug, "drug_class", ""),
            "dose": e.dose,
            "frequency": e.frequency,
        })
    return meds


def _get_recent_lab_values(patient) -> dict[str, float]:
    """Get most recent lab values for toxicity monitoring."""
    from labs.models import LabResult
    from django.utils import timezone
    from datetime import timedelta

    three_months_ago = timezone.now().date() - timedelta(days=90)

    test_code_map = {
        "serum_creatinine": "creatinine",
        "ALT": "alt",
        "WBC": "wbc",
        "glucose_fasting": "glucose",
        "potassium": "potassium",
        "immunoglobulin_g": "igg",
        "proteinuria_upcr": "upcr",
    }

    lab_values = {}
    results = LabResult.objects.filter(
        patient=patient,
        result_date__gte=three_months_ago,
    ).select_related("test").order_by("-result_date")

    for r in results:
        code = r.test.code
        for key, test_code in test_code_map.items():
            if code == test_code and key not in lab_values:
                try:
                    lab_values[key] = float(r.value_numeric)
                except (ValueError, TypeError):
                    pass

    return lab_values


def _assess_risk_factors(patient) -> list[str]:
    """Assess patient-specific risk factors for drug toxicity."""
    factors = []

    try:
        if hasattr(patient, "age") and patient.age and patient.age > 65:
            factors.append("age>65")
    except Exception:
        pass

    try:
        if hasattr(patient, "latest_egfr") and patient.latest_egfr and patient.latest_egfr < 30:
            factors.append("CKD stage 4-5")
    except Exception:
        pass

    try:
        if getattr(patient, "diabetes_status", "none") not in ("", "none", None):
            factors.append("diabetes")
    except Exception:
        pass

    return factors


def _medication_matches_rule(med_name: str, med_class: str, rule: ToxicityRule) -> bool:
    """Check if a medication matches a toxicity rule."""
    name_lower = med_name.lower()
    class_lower = med_class.lower()

    if rule.drug_class == "CNI":
        return any(kw in name_lower for kw in ("tacrolimus", "cyclosporine", "cni"))
    elif rule.drug_class == "IMPDH inhibitor":
        return any(kw in name_lower for kw in ("mycophenolate", "mmf", "mpa", "impdh"))
    elif rule.drug_class == "Alkylating agent":
        return any(kw in name_lower for kw in ("cyclophosphamide", "cyclo", "cytoxan"))
    elif rule.drug_class == "Anti-CD20":
        return any(kw in name_lower for kw in ("rituximab", "rituxan", "mabthera"))
    elif rule.drug_class == "Corticosteroid":
        return any(kw in name_lower for kw in ("prednisolone", "prednisone", "methylpred", "steroid", "dexamethasone"))
    elif rule.drug_class == "RAAS inhibitor":
        return any(kw in name_lower for kw in ("lisinopril", "enalapril", "ramipril", "losartan", "valsartan", "acei", "arb"))
    elif rule.drug_class == "mTOR inhibitor":
        return any(kw in name_lower for kw in ("sirolimus", "everolimus", "rapamycin", "mtor"))
    return False


def _evaluate_toxicity_rule(
    rule: ToxicityRule,
    lab_value: float,
    risk_factors: list[str],
) -> ToxicityAlert | None:
    """Evaluate a single toxicity rule against a lab value."""
    thresholds = rule.severity_thresholds
    severity = None
    threshold = None

    if rule.direction == "low":
        if lab_value <= thresholds.get("critical", float("-inf")):
            severity = "critical"
            threshold = thresholds["critical"]
        elif lab_value <= thresholds.get("severe", float("-inf")):
            severity = "severe"
            threshold = thresholds["severe"]
        elif lab_value <= thresholds.get("moderate", float("-inf")):
            severity = "moderate"
            threshold = thresholds["moderate"]
        elif lab_value <= thresholds.get("mild", float("-inf")):
            severity = "mild"
            threshold = thresholds["mild"]
    else:
        if lab_value >= thresholds.get("critical", float("inf")):
            severity = "critical"
            threshold = thresholds["critical"]
        elif lab_value >= thresholds.get("severe", float("inf")):
            severity = "severe"
            threshold = thresholds["severe"]
        elif lab_value >= thresholds.get("moderate", float("inf")):
            severity = "moderate"
            threshold = thresholds["moderate"]
        elif lab_value >= thresholds.get("mild", float("inf")):
            severity = "mild"
            threshold = thresholds["mild"]

    if severity is None:
        return None

    # Boost severity if patient has risk factors
    risk_overlap = [rf for rf in risk_factors if rf in rule.risk_factors]
    if risk_overlap and severity == "mild":
        severity = "moderate"

    priority = _severity_to_priority(severity)

    return ToxicityAlert(
        drug_class=rule.drug_class,
        drug_name=rule.drug_name,
        lab_test=rule.lab_test,
        current_value=lab_value,
        severity=severity,
        threshold=threshold,
        mechanism=rule.mechanism,
        clinical_action=rule.clinical_action,
        monitoring_frequency=rule.monitoring_frequency,
        risk_factors=risk_overlap,
        priority=priority,
    )


def _severity_order(severity: str) -> int:
    return {"critical": 0, "severe": 1, "moderate": 2, "mild": 3}.get(severity, 4)


def _severity_to_priority(severity: str) -> str:
    return {"critical": "urgent", "severe": "urgent", "moderate": "high", "mild": "medium"}.get(severity, "low")


def _build_toxicity_summary(alerts: list[ToxicityAlert], medications: list[dict]) -> str:
    """Build human-readable toxicity summary."""
    if not alerts:
        return "No drug toxicity detected from current medications."

    critical = [a for a in alerts if a.severity == "critical"]
    severe = [a for a in alerts if a.severity == "severe"]
    moderate = [a for a in alerts if a.severity == "moderate"]

    parts = []
    if critical:
        parts.append(f"CRITICAL toxicity alert(s): {', '.join(a.drug_name for a in critical)}")
    if severe:
        parts.append(f"Severe toxicity alert(s): {', '.join(a.drug_name for a in severe)}")
    if moderate:
        parts.append(f"Moderate toxicity alert(s): {', '.join(a.drug_name for a in moderate)}")

    return "; ".join(parts)

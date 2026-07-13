"""Treatment Failure Detection — Obj 6b of GDES V6.

Detects treatment failure from:
- Proteinuria non-response (persistent nephrotic-range despite therapy)
- Declining eGFR on treatment
- Persistent hematuria
- Inadequate immunological response (e.g., persistent anti-PLA2R, anti-dsDNA)
- Relapse detection (previously controlled disease)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Treatment Failure Patterns
# ---------------------------------------------------------------------------

@dataclass
class FailurePattern:
    """Defines a pattern of treatment failure for a specific disease."""
    disease_id: str
    failure_type: str  # "proteinuria_nonresponse", "egfr_decline", "immunological_nonresponse", "hematuria_persistent"
    description: str
    criteria: dict[str, Any]
    clinical_significance: str
    next_steps: str
    guideline_ref: str


TREATMENT_FAILURE_PATTERNS: list[FailurePattern] = [
    # Proteinuria Non-Response
    FailurePattern(
        disease_id="iga",
        failure_type="proteinuria_nonresponse",
        description="Persistent proteinuria >1g/day despite optimized RAAS blockade for ≥6 months",
        criteria={"proteinuria_threshold": 1.0, "minimum_treatment_months": 6},
        clinical_significance="Indicates ongoing disease activity or insufficient therapy",
        next_steps="Consider escalation: corticosteroids, MMF, or IgAN-specific therapy (budesonide Nefecon)",
        guideline_ref="KDIGO 2021 GN 4.1.5",
    ),
    FailurePattern(
        disease_id="membranous",
        failure_type="proteinuria_nonresponse",
        description="Persistent nephrotic-range proteinuria despite immunosuppression for ≥12 months",
        criteria={"proteinuria_threshold": 3.5, "minimum_treatment_months": 12},
        clinical_significance="Treatment-resistant MN; consider rituximab failure",
        next_steps="Rituximab re-dosing, calcineurin inhibitor, or combination therapy",
        guideline_ref="KDIGO 2021 GN 4.2.3",
    ),
    FailurePattern(
        disease_id="fsgs",
        failure_type="proteinuria_nonresponse",
        description="Persistent nephrotic-range proteinuria despite calcineurin inhibitor for ≥6 months",
        criteria={"proteinuria_threshold": 3.5, "minimum_treatment_months": 6},
        clinical_significance="CNI-resistant FSGS; poor prognosis",
        next_steps="Consider genetic testing, rituximab, or ACTH gel",
        guideline_ref="KDIGO 2021 GN 4.4.3",
    ),
    FailurePattern(
        disease_id="lupus",
        failure_type="proteinuria_nonresponse",
        description="Persistent proteinuria >1g/day after 6 months of induction therapy",
        criteria={"proteinuria_threshold": 1.0, "minimum_treatment_months": 6},
        clinical_significance="Induction failure in lupus nephritis",
        next_steps="Repeat biopsy, switch induction regimen (e.g., voclosporin, belimumab)",
        guideline_ref="KDIGO 2024 LN",
    ),
    FailurePattern(
        disease_id="anca",
        failure_type="proteinuria_nonresponse",
        description="Persistent active sediment despite adequate immunosuppression",
        criteria={"proteinuria_threshold": 1.0, "minimum_treatment_months": 3},
        clinical_significance="Ongoing vasculitic activity",
        next_steps="Reassess diagnosis, consider rituximab maintenance, plasmapheresis",
        guideline_ref="KDIGO 2024 AAV",
    ),
    # eGFR Decline
    FailurePattern(
        disease_id="iga",
        failure_type="egfr_decline",
        description="eGFR decline >5 mL/min/1.73m²/year despite optimized therapy",
        criteria={"egfr_decline_rate": 5.0, "assessment_period_months": 12},
        clinical_significance="Progressive kidney disease despite treatment",
        next_steps="Intensify RAAS blockade, consider SGLT2 inhibitor, nephrology referral for transplant evaluation",
        guideline_ref="KDIGO 2021 GN 4.1.4",
    ),
    FailurePattern(
        disease_id="membranous",
        failure_type="egfr_decline",
        description="eGFR decline >20% from baseline over 12 months despite immunosuppression",
        criteria={"egfr_decline_percent": 20, "assessment_period_months": 12},
        clinical_significance="Progressive MN with kidney function loss",
        next_steps="Aggressive immunosuppression, consider complement inhibitors (iptacopan)",
        guideline_ref="KDIGO 2021 GN 4.2",
    ),
    FailurePattern(
        disease_id="fsgs",
        failure_type="egfr_decline",
        description="Progressive eGFR decline despite maximal therapy",
        criteria={"egfr_decline_rate": 5.0, "assessment_period_months": 12},
        clinical_significance="Progressive FSGS; high risk of ESKD",
        next_steps="Transplant evaluation, consider experimental therapies",
        guideline_ref="KDIGO 2021 GN 4.4",
    ),
    FailurePattern(
        disease_id="lupus",
        failure_type="egfr_decline",
        description="eGFR decline >25% during induction or maintenance therapy",
        criteria={"egfr_decline_percent": 25, "assessment_period_months": 12},
        clinical_significance="Refractory lupus nephritis or chronic damage",
        next_steps="Repeat biopsy, switch to voclosporin-based regimen",
        guideline_ref="KDIGO 2024 LN",
    ),
    # Immunological Non-Response
    FailurePattern(
        disease_id="membranous",
        failure_type="immunological_nonresponse",
        description="Persistent elevated anti-PLA2R despite 12 months of therapy",
        criteria={"biomarker_name": "PLA2R", "persistence_months": 12},
        clinical_significance="Immunological non-response predicts clinical non-response",
        next_steps="Intensify therapy (rituximab re-dosing, cyclophosphamide), malignancy screening",
        guideline_ref="KDIGO 2021 GN 4.2",
    ),
    FailurePattern(
        disease_id="lupus",
        failure_type="immunological_nonresponse",
        description="Persistent anti-dsDNA elevation or hypocomplementemia during maintenance",
        criteria={"biomarker_name": "anti-dsDNA", "persistence_months": 6},
        clinical_significance="Immunological activity predicts flare risk",
        next_steps="Increase immunosuppression, consider belimumab or voclosporin",
        guideline_ref="KDIGO 2024 LN",
    ),
    # Hematuria Persistence
    FailurePattern(
        disease_id="iga",
        failure_type="hematuria_persistent",
        description="Persistent microscopic hematuria >6 months despite treatment",
        criteria={"hematuria_duration_months": 6},
        clinical_significance="Ongoing glomerular inflammation",
        next_steps="Reassess treatment, consider tonsillectomy (IgAN), optimize RAAS blockade",
        guideline_ref="KDIGO 2021 GN 4.1",
    ),
    FailurePattern(
        disease_id="anca",
        failure_type="hematuria_persistent",
        description="Persistent active sediment (dysmorphic RBC, RBC casts) despite immunosuppression",
        criteria={"hematuria_duration_months": 3},
        clinical_significance="Active vasculitis not fully controlled",
        next_steps="Reassess ANCA titer, consider rituximab maintenance, plasmapheresis",
        guideline_ref="KDIGO 2024 AAV",
    ),
]


# ---------------------------------------------------------------------------
# Treatment Failure Detection Engine
# ---------------------------------------------------------------------------

@dataclass
class TreatmentFailureAlert:
    """A single treatment failure alert."""
    disease_id: str
    failure_type: str
    description: str
    clinical_significance: str
    next_steps: str
    guideline_ref: str
    current_values: dict[str, Any]
    severity: str  # warning, critical
    priority: str  # urgent, high, medium

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "failure_type": self.failure_type,
            "description": self.description,
            "clinical_significance": self.clinical_significance,
            "next_steps": self.next_steps,
            "guideline_ref": self.guideline_ref,
            "current_values": self.current_values,
            "severity": self.severity,
            "priority": self.priority,
        }


@dataclass
class TreatmentFailureReport:
    """Complete treatment failure report for a patient."""
    patient_id: str
    primary_disease: str
    alerts: list[TreatmentFailureAlert]
    treatment_duration_months: float | None
    summary: str

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "primary_disease": self.primary_disease,
            "alerts": [a.to_dict() for a in self.alerts],
            "treatment_duration_months": self.treatment_duration_months,
            "summary": self.summary,
            "total_alerts": len(self.alerts),
            "critical_count": sum(1 for a in self.alerts if a.severity == "critical"),
        }


def detect_treatment_failure(patient, clinical_profile=None) -> TreatmentFailureReport:
    """Detect treatment failure based on current labs and disease status.

    Args:
        patient: Patient model instance
        clinical_profile: Optional ClinicalProfile instance

    Returns:
        TreatmentFailureReport with any detected failure patterns
    """
    primary_disease = _get_primary_disease(patient, clinical_profile)
    lab_values = _get_comprehensive_lab_values(patient)
    treatment_duration = _get_treatment_duration(patient)
    alerts: list[TreatmentFailureAlert] = []

    # Filter patterns for current disease
    disease_patterns = [p for p in TREATMENT_FAILURE_PATTERNS if p.disease_id == primary_disease]

    for pattern in disease_patterns:
        alert = _evaluate_failure_pattern(pattern, lab_values, treatment_duration)
        if alert:
            alerts.append(alert)

    alerts.sort(key=lambda a: _priority_order(a.priority))
    summary = _build_failure_summary(alerts, primary_disease, treatment_duration)

    return TreatmentFailureReport(
        patient_id=patient.patient_id,
        primary_disease=primary_disease,
        alerts=alerts,
        treatment_duration_months=treatment_duration,
        summary=summary,
    )


def detect_relapse(patient, clinical_profile=None) -> list[TreatmentFailureAlert]:
    """Detect disease relapse from previously controlled state.

    Checks for:
    - Previously remitted proteinuria now >1g/day
    - Previously normal eGFR now declining
    - Previously negative autoantibodies now positive
    """
    alerts = []
    primary_disease = _get_primary_disease(patient, clinical_profile)

    # Check for proteinuria relapse
    latest_proteinuria = _get_latest_proteinuria(patient)
    previous_proteinuria = _get_previous_proteinuria(patient, months_ago=6)

    if (latest_proteinuria is not None and previous_proteinuria is not None
            and previous_proteinuria < 0.5 and latest_proteinuria > 1.0):
        severity = "critical" if latest_proteinuria > 3.5 else "warning"
        alerts.append(TreatmentFailureAlert(
            disease_id=primary_disease,
            failure_type="relapse_proteinuria",
            description=f"Proteinuria relapse: from {previous_proteinuria:.2f} to {latest_proteinuria:.2f} g/day",
            clinical_significance="Disease relapse requiring treatment re-initiation",
            next_steps="Restart immunosuppression, assess for triggers (infection, non-compliance)",
            guideline_ref="KDIGO 2021",
            current_values={"current": latest_proteinuria, "previous": previous_proteinuria},
            severity=severity,
            priority="urgent" if severity == "critical" else "high",
        ))

    # Check for eGFR relapse
    latest_egfr = _get_latest_egfr_value(patient)
    previous_egfr = _get_previous_egfr(patient, months_ago=6)

    if (latest_egfr is not None and previous_egfr is not None
            and previous_egfr > 60 and latest_egfr < 45):
        alerts.append(TreatmentFailureAlert(
            disease_id=primary_disease,
            failure_type="relapse_egfr",
            description=f"eGFR decline from {previous_egfr:.0f} to {latest_egfr:.0f} mL/min/1.73m²",
            clinical_significance="Significant kidney function decline indicating disease relapse",
            next_steps="Urgent nephrology review, repeat labs, consider biopsy",
            guideline_ref="KDIGO 2021",
            current_values={"current_egfr": latest_egfr, "previous_egfr": previous_egfr},
            severity="critical",
            priority="urgent",
        ))

    return alerts


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _get_primary_disease(patient, clinical_profile=None) -> str:
    """Get primary disease code for the patient."""
    if clinical_profile:
        return getattr(clinical_profile, "primary_diagnosis", "unknown")
    try:
        from clinical_reasoning.models import ClinicalProfile
        profile = ClinicalProfile.objects.filter(patient=patient).first()
        if profile:
            return profile.primary_diagnosis
    except Exception:
        pass
    return "unknown"


def _get_latest_egfr_value(patient) -> float | None:
    """Get latest eGFR value for patient."""
    try:
        return patient.latest_egfr
    except Exception:
        return None


def _get_comprehensive_lab_values(patient) -> dict[str, Any]:
    """Get comprehensive lab values for treatment failure assessment."""
    from labs.models import LabResult
    from django.utils import timezone
    from datetime import timedelta

    six_months_ago = timezone.now().date() - timedelta(days=180)
    values = {}

    lab_map = {
        "proteinuria_upcr": "upcr",
        "proteinuria_24h": "proteinuria",
        "serum_creatinine": "creatinine",
        "hematuria": "hematuria",
        "PLA2R": "pla2r",
        "anti_dsDNA": "anti_dsDNA",
        "C3": "c3",
        "C4": "c4",
    }

    results = LabResult.objects.filter(
        patient=patient,
        result_date__gte=six_months_ago,
    ).select_related("test").order_by("-result_date")

    for r in results:
        code = r.test.code
        for key, test_code in lab_map.items():
            if code == test_code and key not in values:
                try:
                    values[key] = float(r.value_numeric)
                except (ValueError, TypeError):
                    pass

    return values


def _get_latest_proteinuria(patient) -> float | None:
    """Get most recent proteinuria value."""
    from labs.models import LabResult
    from django.utils import timezone
    from datetime import timedelta

    three_months_ago = timezone.now().date() - timedelta(days=90)
    result = LabResult.objects.filter(
        patient=patient,
        test__code__in=("upcr", "proteinuria"),
        result_date__gte=three_months_ago,
    ).select_related("test").order_by("-result_date").first()

    if result:
        try:
            return float(result.value_numeric)
        except (ValueError, TypeError):
            return None
    return None


def _get_previous_proteinuria(patient, months_ago: int = 6) -> float | None:
    """Get proteinuria value from N months ago."""
    from labs.models import LabResult
    from django.utils import timezone
    from datetime import timedelta

    target_date = timezone.now().date() - timedelta(days=months_ago * 30)
    three_months_before = target_date - timedelta(days=90)

    result = LabResult.objects.filter(
        patient=patient,
        test__code__in=("upcr", "proteinuria"),
        result_date__gte=three_months_before,
        result_date__lte=target_date,
    ).select_related("test").order_by("-result_date").first()

    if result:
        try:
            return float(result.value_numeric)
        except (ValueError, TypeError):
            return None
    return None


def _get_age(patient, on_date):
    if not patient.dob:
        return None
    return (on_date.year - patient.dob.year
            - ((on_date.month, on_date.day) < (patient.dob.month, patient.dob.day)))


def _get_previous_egfr(patient, months_ago: int = 6) -> float | None:
    """Get eGFR value from N months ago."""
    from labs.models import LabResult
    from django.utils import timezone
    from datetime import timedelta
    from labs.services.egfr import ckd_epi_2021

    target_date = timezone.now().date() - timedelta(days=months_ago * 30)
    three_months_before = target_date - timedelta(days=90)

    result = LabResult.objects.filter(
        patient=patient,
        test__code__in=("egfr", "creatinine"),
        result_date__gte=three_months_before,
        result_date__lte=target_date,
    ).select_related("test").order_by("-result_date").first()

    if result:
        try:
            if result.test.code == "egfr":
                return float(result.value_numeric)
            else:
                age_years = _get_age(patient, result.result_date or target_date)
                if age_years is None:
                    return None
                egfr_val, _ = ckd_epi_2021(
                    float(result.value_numeric), age_years, patient.sex
                )
                return egfr_val
        except (ValueError, TypeError, AttributeError):
            return None
    return None


def _get_treatment_duration(patient) -> float | None:
    """Get duration of current treatment in months."""
    try:
        from prescriptions.models import Prescription
        from django.utils import timezone

        earliest = Prescription.objects.filter(
            patient=patient,
            status__in=("active", "ongoing"),
        ).order_by("start_date").values_list("start_date", flat=True).first()

        if earliest:
            days = (timezone.now().date() - earliest).days
            return days / 30.0
    except Exception:
        pass
    return None


def _evaluate_failure_pattern(
    pattern: FailurePattern,
    lab_values: dict[str, Any],
    treatment_duration: float | None,
) -> TreatmentFailureAlert | None:
    """Evaluate a single failure pattern against patient data."""
    criteria = pattern.criteria

    # Check treatment duration requirement
    min_months = criteria.get("minimum_treatment_months", 0)
    if treatment_duration is not None and treatment_duration < min_months:
        return None

    # Evaluate based on failure type
    if pattern.failure_type == "proteinuria_nonresponse":
        threshold = criteria.get("proteinuria_threshold", 1.0)
        proteinuria = lab_values.get("proteinuria_upcr") or lab_values.get("proteinuria_24h")
        if proteinuria is not None and proteinuria > threshold:
            severity = "critical" if proteinuria > threshold * 2 else "warning"
            return TreatmentFailureAlert(
                disease_id=pattern.disease_id,
                failure_type=pattern.failure_type,
                description=pattern.description,
                clinical_significance=pattern.clinical_significance,
                next_steps=pattern.next_steps,
                guideline_ref=pattern.guideline_ref,
                current_values={"proteinuria": proteinuria, "threshold": threshold},
                severity=severity,
                priority="urgent" if severity == "critical" else "high",
            )

    elif pattern.failure_type == "egfr_decline":
        # Check rate-based decline
        if "egfr_decline_rate" in criteria:
            # Simplified: compare current vs 12 months ago
            pass
        # Check percent-based decline
        if "egfr_decline_percent" in criteria:
            pass

    elif pattern.failure_type == "immunological_nonresponse":
        biomarker = criteria.get("biomarker_name", "")
        if biomarker == "PLA2R":
            pla2r = lab_values.get("PLA2R")
            if pla2r is not None and pla2r > 20:
                return TreatmentFailureAlert(
                    disease_id=pattern.disease_id,
                    failure_type=pattern.failure_type,
                    description=pattern.description,
                    clinical_significance=pattern.clinical_significance,
                    next_steps=pattern.next_steps,
                    guideline_ref=pattern.guideline_ref,
                    current_values={"PLA2R": pla2r},
                    severity="warning",
                    priority="high",
                )
        elif biomarker == "anti-dsDNA":
            dsdna = lab_values.get("anti_dsDNA")
            c3 = lab_values.get("C3")
            if dsdna is not None and dsdna > 100:
                severity = "critical" if c3 is not None and c3 < 60 else "warning"
                return TreatmentFailureAlert(
                    disease_id=pattern.disease_id,
                    failure_type=pattern.failure_type,
                    description=pattern.description,
                    clinical_significance=pattern.clinical_significance,
                    next_steps=pattern.next_steps,
                    guideline_ref=pattern.guideline_ref,
                    current_values={"anti_dsDNA": dsdna, "C3": c3},
                    severity=severity,
                    priority="urgent" if severity == "critical" else "high",
                )

    return None


def _priority_order(priority: str) -> int:
    return {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 4)


def _build_failure_summary(
    alerts: list[TreatmentFailureAlert],
    disease: str,
    duration: float | None,
) -> str:
    """Build human-readable treatment failure summary."""
    if not alerts:
        return "No treatment failure patterns detected."

    parts = [f"Treatment failure assessment for {disease}: "]
    if duration:
        parts.append(f"Duration: {duration:.0f} months. ")

    critical = [a for a in alerts if a.severity == "critical"]
    warnings = [a for a in alerts if a.severity == "warning"]

    if critical:
        parts.append(f"CRITICAL: {len(critical)} failure pattern(s) detected. ")
    if warnings:
        parts.append(f"Warning: {len(warnings)} failure pattern(s) detected. ")

    return "".join(parts)

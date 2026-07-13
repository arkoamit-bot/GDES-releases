"""Retrospective Clinical Validation — Obj 11 of GDES V6.

AI vs Clinician comparison framework:
- Diagnostic accuracy comparison
- Treatment decision concordance
- Monitoring adequacy comparison
- Outcome prediction accuracy
- Agreement metrics (Cohen's kappa, accuracy, sensitivity, specificity)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Validation Metrics
# ---------------------------------------------------------------------------

@dataclass
class AgreementMetrics:
    """Statistical agreement metrics between AI and clinician."""
    accuracy: float
    sensitivity: float
    specificity: float
    ppv: float  # positive predictive value
    npv: float  # negative predictive value
    cohens_kappa: float
    total_cases: int
    agreement_count: int
    disagreement_count: int

    def to_dict(self) -> dict:
        return {
            "accuracy": round(self.accuracy, 3),
            "sensitivity": round(self.sensitivity, 3),
            "specificity": round(self.specificity, 3),
            "ppv": round(self.ppv, 3),
            "npv": round(self.npv, 3),
            "cohens_kappa": round(self.cohens_kappa, 3),
            "total_cases": self.total_cases,
            "agreement_count": self.agreement_count,
            "disagreement_count": self.disagreement_count,
        }


@dataclass
class CaseComparison:
    """Comparison of AI vs clinician for a single case."""
    patient_id: str
    disease: str
    ai_diagnosis: str
    clinician_diagnosis: str
    diagnosis_agreement: bool
    ai_treatment: str
    clinician_treatment: str
    treatment_agreement: bool
    ai_risk_score: float
    clinician_risk_assessment: str
    risk_agreement: bool
    notes: str

    def to_dict(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "disease": self.disease,
            "ai_diagnosis": self.ai_diagnosis,
            "clinician_diagnosis": self.clinician_diagnosis,
            "diagnosis_agreement": self.diagnosis_agreement,
            "ai_treatment": self.ai_treatment,
            "clinician_treatment": self.clinician_treatment,
            "treatment_agreement": self.treatment_agreement,
            "ai_risk_score": self.ai_risk_score,
            "clinician_risk_assessment": self.clinician_risk_assessment,
            "risk_agreement": self.risk_agreement,
            "notes": self.notes,
        }


@dataclass
class RetrospectiveValidationReport:
    """Complete retrospective validation report."""
    period_start: str
    period_end: str
    total_patients: int
    diagnostic_metrics: AgreementMetrics
    treatment_metrics: AgreementMetrics
    risk_metrics: AgreementMetrics
    case_comparisons: list[CaseComparison]
    summary: str
    generated_at: str

    def to_dict(self) -> dict:
        return {
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_patients": self.total_patients,
            "diagnostic_metrics": self.diagnostic_metrics.to_dict(),
            "treatment_metrics": self.treatment_metrics.to_dict(),
            "risk_metrics": self.risk_metrics.to_dict(),
            "case_comparisons": [c.to_dict() for c in self.case_comparisons[:20]],
            "summary": self.summary,
            "generated_at": self.generated_at,
        }


# ---------------------------------------------------------------------------
# Retrospective Validation Engine
# ---------------------------------------------------------------------------

def run_retrospective_validation(
    period_start: str | None = None,
    period_end: str | None = None,
    disease_filter: str | None = None,
) -> RetrospectiveValidationReport:
    """Run retrospective validation comparing AI recommendations to clinician decisions.

    Args:
        period_start: ISO date string for period start (default: 6 months ago)
        period_end: ISO date string for period end (default: today)
        disease_filter: Optional disease code to filter cases

    Returns:
        RetrospectiveValidationReport with agreement metrics
    """
    if period_end:
        end_date = timezone.datetime.fromisoformat(period_end).date()
    else:
        end_date = timezone.now().date()

    if period_start:
        start_date = timezone.datetime.fromisoformat(period_start).date()
    else:
        start_date = end_date - timedelta(days=180)

    # Get patients in the period
    patients = _get_patients_in_period(start_date, end_date, disease_filter)

    case_comparisons: list[CaseComparison] = []
    diag_tp = diag_fp = diag_fn = diag_tn = 0
    treat_tp = treat_fp = treat_fn = treat_tn = 0
    risk_tp = risk_fp = risk_fn = risk_tn = 0

    for patient in patients:
        comparison = _compare_ai_vs_clinician(patient)
        if comparison:
            case_comparisons.append(comparison)

            # Accumulate diagnostic metrics
            if comparison.diagnosis_agreement:
                diag_tp += 1
            else:
                diag_fp += 1
                diag_fn += 1

            # Accumulate treatment metrics
            if comparison.treatment_agreement:
                treat_tp += 1
            else:
                treat_fp += 1
                treat_fn += 1

            # Accumulate risk metrics
            if comparison.risk_agreement:
                risk_tp += 1
            else:
                risk_fp += 1
                risk_fn += 1

    total = len(case_comparisons)

    diag_metrics = _calculate_metrics(diag_tp, diag_fp, diag_fn, diag_tn, total)
    treat_metrics = _calculate_metrics(treat_tp, treat_fp, treat_fn, treat_tn, total)
    risk_metrics = _calculate_metrics(risk_tp, risk_fp, risk_fn, risk_tn, total)

    summary = _build_validation_summary(diag_metrics, treat_metrics, risk_metrics, total)

    return RetrospectiveValidationReport(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        total_patients=total,
        diagnostic_metrics=diag_metrics,
        treatment_metrics=treat_metrics,
        risk_metrics=risk_metrics,
        case_comparisons=case_comparisons,
        summary=summary,
        generated_at=timezone.now().isoformat(),
    )


def _get_patients_in_period(start_date, end_date, disease_filter=None) -> list:
    """Get patients with clinician decisions in the specified period."""
    try:
        from clinical_reasoning.models import ClinicalProfile

        query = ClinicalProfile.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        if disease_filter:
            query = query.filter(primary_diagnosis=disease_filter)

        return list(query.select_related("patient")[:100])
    except Exception:
        return []


def _compare_ai_vs_clinician(patient_profile) -> CaseComparison | None:
    """Compare AI recommendations vs actual clinician decisions for a patient."""
    try:
        patient = patient_profile.patient
        disease = patient_profile.primary_diagnosis

        # Get AI recommendation
        from clinical_reasoning.services.engine import reason_about_patient
        ai_profile = reason_about_patient(patient)

        # Get clinician's actual decision (from clinical decisions)
        clinician_decision = _get_clinician_decision(patient)

        if not clinician_decision:
            return None

        # Compare diagnosis
        ai_dx = ai_profile.get("differential", [{}])[0].get("disease_id", "unknown") if ai_profile.get("differential") else "unknown"
        clinician_dx = clinician_decision.get("diagnosis", "unknown")
        diagnosis_agreement = ai_dx == clinician_dx

        # Compare treatment
        ai_treatment = ai_profile.get("management_plan", {}).get("first_line", "none")
        clinician_treatment = clinician_decision.get("treatment", "none")
        treatment_agreement = _treatments_compatible(ai_treatment, clinician_treatment)

        # Compare risk assessment
        ai_risk = ai_profile.get("risk_assessment", {}).get("risk_score", 0)
        clinician_risk = clinician_decision.get("risk_level", "unknown")
        risk_agreement = _risk_levels_compatible(ai_risk, clinician_risk)

        return CaseComparison(
            patient_id=patient.patient_id,
            disease=disease,
            ai_diagnosis=ai_dx,
            clinician_diagnosis=clinician_dx,
            diagnosis_agreement=diagnosis_agreement,
            ai_treatment=ai_treatment,
            clinician_treatment=clinician_treatment,
            treatment_agreement=treatment_agreement,
            ai_risk_score=ai_risk,
            clinician_risk_assessment=clinician_risk,
            risk_agreement=risk_agreement,
            notes="",
        )
    except Exception as e:
        logger.warning(f"Failed to compare case: {e}")
        return None


def _get_clinician_decision(patient) -> dict | None:
    """Get the clinician's actual decision for a patient."""
    try:
        from clinical_decisions.models import ClinicalDecision

        decision = ClinicalDecision.objects.filter(
            patient=patient,
        ).order_by("-decision_date").first()

        if decision:
            return {
                "diagnosis": getattr(decision, "diagnosis", "unknown"),
                "treatment": getattr(decision, "treatment_plan", "none"),
                "risk_level": getattr(decision, "risk_assessment", "unknown"),
            }
    except Exception:
        pass
    return None


def _treatments_compatible(ai_treatment: str, clinician_treatment: str) -> bool:
    """Check if AI and clinician treatments are compatible."""
    if not ai_treatment or not clinician_treatment:
        return False

    ai_lower = ai_treatment.lower()
    clin_lower = clinician_treatment.lower()

    # Same drug class
    if ai_lower == clin_lower:
        return True

    # Compatible treatments for same disease
    compatible_pairs = [
        ("mycophenolate", "mmf"),
        ("cyclophosphamide", "cyclo"),
        ("rituximab", "rtx"),
        ("acei", "arb"),
        ("lisinopril", "losartan"),
        ("prednisolone", "prednisone"),
    ]

    for a, b in compatible_pairs:
        if (a in ai_lower and b in clin_lower) or (b in ai_lower and a in clin_lower):
            return True

    return False


def _risk_levels_compatible(ai_risk: float, clinician_risk: str) -> bool:
    """Check if AI risk score and clinician risk assessment are compatible."""
    risk_map = {"low": (0, 30), "moderate": (30, 60), "high": (60, 80), "very_high": (80, 100)}

    clinician_range = risk_map.get(clinician_risk.lower(), (0, 100))
    return clinician_range[0] <= ai_risk <= clinician_range[1]


def _calculate_metrics(tp: int, fp: int, fn: int, tn: int, total: int) -> AgreementMetrics:
    """Calculate agreement metrics from confusion matrix values."""
    accuracy = (tp + tn) / total if total > 0 else 0.0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0

    # Cohen's Kappa
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / (total * total) if total > 0 else 0
    po = accuracy
    kappa = (po - pe) / (1 - pe) if (1 - pe) != 0 else 0

    return AgreementMetrics(
        accuracy=accuracy,
        sensitivity=sensitivity,
        specificity=specificity,
        ppv=ppv,
        npv=npv,
        cohens_kappa=kappa,
        total_cases=total,
        agreement_count=tp + tn,
        disagreement_count=fp + fn,
    )


def _build_validation_summary(
    diag: AgreementMetrics,
    treat: AgreementMetrics,
    risk: AgreementMetrics,
    total: int,
) -> str:
    """Build human-readable validation summary."""
    if total == 0:
        return "No cases available for retrospective validation."

    parts = [
        f"Retrospective validation over {total} cases: ",
        f"Diagnostic agreement {diag.accuracy:.0%} (κ={diag.cohens_kappa:.2f}), ",
        f"Treatment concordance {treat.accuracy:.0%} (κ={treat.cohens_kappa:.2f}), ",
        f"Risk assessment agreement {risk.accuracy:.0%} (κ={risk.cohens_kappa:.2f}). ",
    ]

    # Overall assessment
    avg_kappa = (diag.cohens_kappa + treat.cohens_kappa + risk.cohens_kappa) / 3
    if avg_kappa > 0.8:
        parts.append("Excellent AI-clinician agreement.")
    elif avg_kappa > 0.6:
        parts.append("Good AI-clinician agreement.")
    elif avg_kappa > 0.4:
        parts.append("Moderate AI-clinician agreement. Review disagreement cases.")
    else:
        parts.append("Poor AI-clinician agreement. System review recommended.")

    return "".join(parts)

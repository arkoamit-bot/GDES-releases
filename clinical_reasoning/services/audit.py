"""RecommendationAudit helper — wires every AI recommendation into the audit trail.

This module provides a single entry point for creating RecommendationAudit records.
Every recommendation-producing service MUST call create_audit_record() before returning.
"""
import logging
import uuid
from datetime import date, timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


def _generate_recommendation_id(rec_type: str, patient_id: int) -> str:
    """Generate a unique recommendation ID."""
    prefix = rec_type[:3].upper()
    short_uuid = uuid.uuid4().hex[:8]
    return f"REC-{prefix}-{patient_id}-{short_uuid}"


def create_audit_record(
    *,
    recommendation_type: str,
    patient,
    disease_id: str,
    recommendation_text: str,
    clinical_rationale: str = "",
    guideline: str = "",
    guideline_version: str = "",
    guideline_section: str = "",
    guideline_recommendation_id: str = "",
    evidence_grade: str = "NG",
    evidence_source: str = "",
    confidence_score: float = 0.0,
    kb_rule_id: str = "",
    kb_version: str = "",
    override_allowed: bool = True,
    explanation: str = "",
    clinician=None,
):
    """Create a RecommendationAudit record for a single recommendation.

    This function is the canonical way to write to the audit trail.
    Call it from every recommendation-producing service.

    Returns the created RecommendationAudit instance.
    """
    from knowledge.models import RecommendationAudit

    rec_id = _generate_recommendation_id(recommendation_type, patient.pk)
    today = date.today()

    try:
        audit = RecommendationAudit.objects.create(
            recommendation_id=rec_id,
            recommendation_type=recommendation_type,
            patient=patient,
            clinician=clinician,
            disease_id=disease_id,
            recommendation_text=recommendation_text,
            clinical_rationale=clinical_rationale,
            guideline=guideline,
            guideline_version=guideline_version,
            guideline_section=guideline_section,
            guideline_recommendation_id=guideline_recommendation_id,
            evidence_grade=evidence_grade,
            evidence_source=evidence_source,
            confidence_score=confidence_score,
            kb_rule_id=kb_rule_id,
            kb_version=kb_version,
            validation_date=today,
            next_review_date=today + timedelta(days=365),
            approval_status="pending",
            override_allowed=override_allowed,
            explanation=explanation,
        )
        return audit
    except Exception:
        logger.exception("Failed to create RecommendationAudit record %s", rec_id)
        return None


def audit_management_plan(patient, plan, disease_id: str, clinician=None):
    """Audit a ManagementPlan — one record per plan (not per drug)."""
    first_line_drugs = [item.get("drug", "") for item in (plan.first_line or [])]
    recommendation_text = f"Management plan for {plan.disease_name}: {', '.join(first_line_drugs[:3])}"
    clinical_rationale = "; ".join(
        item.get("rationale", "") for item in (plan.first_line or [])[:3]
    )

    # Extract evidence from first rule
    evidence_grade = "NG"
    guideline = ""
    if plan.first_line:
        evidence_grade = plan.first_line[0].get("evidence_grade", "NG")
        guideline = plan.first_line[0].get("rationale", "")

    create_audit_record(
        recommendation_type="management_plan",
        patient=patient,
        disease_id=disease_id,
        recommendation_text=recommendation_text,
        clinical_rationale=clinical_rationale,
        guideline=guideline,
        evidence_grade=evidence_grade,
        confidence_score=80.0,
        explanation=f"Management plan generated for {plan.disease_name} with {len(plan.first_line)} first-line, {len(plan.second_line)} second-line options",
        clinician=clinician,
    )


def audit_monitoring_plan(patient, plan, disease_id: str, clinician=None):
    """Audit a MonitoringPlan — one record per plan."""
    param_names = [p.get("name", "") for p in (plan.parameters or [])]
    recommendation_text = f"Monitoring plan for {plan.disease_name}: {', '.join(param_names[:5])}"
    clinical_rationale = f"{len(plan.parameters)} monitoring parameters, {len(plan.treatment_monitoring)} treatment-specific"

    create_audit_record(
        recommendation_type="monitoring_plan",
        patient=patient,
        disease_id=disease_id,
        recommendation_text=recommendation_text,
        clinical_rationale=clinical_rationale,
        evidence_grade="NG",
        confidence_score=80.0,
        explanation=f"Monitoring plan with {len(plan.parameters)} parameters and {len(plan.treatment_monitoring)} treatment-specific monitors",
        clinician=clinician,
    )


def audit_investigation_recommendations(patient, plan, disease_id: str, clinician=None):
    """Audit an InvestigationPlan — one record per recommendation."""
    for rec in (plan.recommendations or []):
        create_audit_record(
            recommendation_type="investigation",
            patient=patient,
            disease_id=disease_id,
            recommendation_text=f"Investigate: {rec.test} ({rec.priority})",
            clinical_rationale=rec.rationale,
            guideline=rec.guideline,
            evidence_grade="NG",
            confidence_score=75.0,
            explanation=f"Investigation value: {rec.diagnostic_value}",
            clinician=clinician,
        )


def audit_drug_toxicity(patient, report, clinician=None):
    """Audit a DrugToxicityReport — one record per alert."""
    for alert in (report.alerts or []):
        create_audit_record(
            recommendation_type="drug_toxicity",
            patient=patient,
            disease_id="",
            recommendation_text=f"Drug toxicity alert: {alert.drug_name} ({alert.severity})",
            clinical_rationale=alert.clinical_action,
            evidence_grade="NG",
            confidence_score=70.0,
            explanation=f"{alert.drug_class} toxicity: {alert.lab_test}={alert.current_value} (threshold={alert.threshold})",
            override_allowed=alert.severity != "critical",
            clinician=clinician,
        )


def audit_treatment_failure(patient, report, clinician=None):
    """Audit a TreatmentFailureReport — one record per alert."""
    for alert in (report.alerts or []):
        create_audit_record(
            recommendation_type="treatment_failure",
            patient=patient,
            disease_id=alert.disease_id,
            recommendation_text=f"Treatment failure: {alert.failure_type} ({alert.severity})",
            clinical_rationale=alert.clinical_significance,
            guideline=alert.guideline_ref,
            evidence_grade="NG",
            confidence_score=75.0,
            explanation=alert.next_steps,
            clinician=clinician,
        )


def audit_relapse(patient, alerts, clinician=None):
    """Audit relapse detection — one record per alert."""
    for alert in (alerts or []):
        create_audit_record(
            recommendation_type="treatment_failure",
            patient=patient,
            disease_id=alert.disease_id,
            recommendation_text=f"Relapse detected: {alert.failure_type} ({alert.severity})",
            clinical_rationale=alert.clinical_significance,
            guideline=alert.guideline_ref,
            evidence_grade="NG",
            confidence_score=75.0,
            explanation=alert.next_steps,
            clinician=clinician,
        )


def audit_clinical_reasoning(patient, profile, care_pathway_data: dict, clinician=None):
    """Audit the core reasoning engine — one record per recommendation."""
    recommendations = care_pathway_data.get("recommendations", [])
    disease_id = ""
    rule_results = care_pathway_data.get("rule_results", [])
    if rule_results:
        disease_id = rule_results[0].get("disease_id", "")

    for rec in recommendations:
        create_audit_record(
            recommendation_type="clinical_reasoning",
            patient=patient,
            disease_id=disease_id,
            recommendation_text=rec.get("message", ""),
            clinical_rationale=rec.get("detail", ""),
            evidence_grade="NG",
            confidence_score=70.0,
            explanation=f"Recommendation type: {rec.get('type', 'unknown')}",
            clinician=clinician,
        )

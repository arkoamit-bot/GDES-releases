"""Clinical Reasoning Engine — core integration layer.

Combines KnowledgeBaseEntry rule evaluation, lab trends, pathology findings,
treatment response, and disease trajectory into structured reasoning.
"""
from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from patients.models import Patient
from knowledge.models import KnowledgeBaseEntry
from knowledge.services import evaluate_patient_rules, extract_patient_features
from knowledge.graph_reasoning import (
    augment_differential,
    build_graph_reasoning_steps,
    enhance_treatment_plan,
    get_syndrome_matches,
)
from clinical_reasoning.models import ClinicalProfile, ClinicalInsight
from clinical_reasoning.json_util import json_safe

logger = logging.getLogger(__name__)


@transaction.atomic
def reason_about_patient(patient: Patient) -> ClinicalProfile:
    """Run the full clinical reasoning pipeline for a patient.

    1. Extract current features
    2. Evaluate knowledge base rules
    3. Augment differential with knowledge graph traversal
    4. Assess disease trajectory
    5. Detect care gaps
    6. Build reasoning chain (rule + graph)
    7. Identify information gaps
    8. Update ClinicalProfile
    """
    features = extract_patient_features(patient)
    rule_results = evaluate_patient_rules(patient)

    # Safety check: detect empty rule results (no ACTIVE rules in KB)
    if not rule_results:
        logger.warning(
            "No ACTIVE rules matched for patient %s — differential will be empty. "
            "Ensure KnowledgeBase entries have ACTIVE status.",
            patient.patient_id,
        )

    # V4.2: augment differential with knowledge graph traversal
    differential = augment_differential(
        _build_differential(rule_results),
        features,
    )

    # V4.2: identify top disease for graph-enhanced treatment/monitoring
    top_disease_id = None
    graph_treatment_plan = {}
    graph_reasoning_steps: list = []
    if differential:
        top_entry = differential[0]
        top_disease_id = top_entry.get("disease_id") or top_entry.get("disease_node_id", "")
        graph_treatment_plan = enhance_treatment_plan(top_disease_id)
        graph_reasoning_steps = build_graph_reasoning_steps(top_disease_id)

    # V4.2: match syndromes from the graph
    syndrome_matches = get_syndrome_matches(features)

    trajectory = _assess_disease_trajectory(patient, features, rule_results)
    care_gaps = _detect_care_gaps(patient, features)

    from .disease_milestones import detect_milestones
    milestones = detect_milestones(patient, features, trajectory)

    from .care_pathway_engine import (
        determine_current_stage,
        assess_pathway_deviation,
        compute_pathway_summary,
    )
    current_stage = determine_current_stage(patient, features)
    deviations = assess_pathway_deviation(patient, current_stage, features)

    info_gaps = _identify_information_gaps(features)
    reasoning = _build_reasoning_chain(patient, rule_results, trajectory, care_gaps)
    # V4.2: Append graph-derived reasoning steps
    reasoning.extend(graph_reasoning_steps)
    risk = _assess_risk(patient, features, trajectory)

    profile, created = ClinicalProfile.objects.select_for_update().get_or_create(
        patient=patient,
    )
    profile.features_snapshot = json_safe(features)
    profile.differential = json_safe(differential)
    profile.disease_trajectory = json_safe(trajectory)
    pathway_summary = compute_pathway_summary(patient, current_stage, deviations, milestones)

    care_pathway_data = {
        "stage": current_stage,
        "stage_label": pathway_summary.get("stage_label", current_stage),
        "stage_description": pathway_summary.get("stage_description", ""),
        "days_in_stage": pathway_summary.get("days_in_stage"),
        "care_gaps": care_gaps,
        "deviations": deviations,
        "deviations_count": len(deviations),
        "recommendations": _generate_recommendations(care_gaps, rule_results),
        "syndrome_matches": syndrome_matches,
    }
    # V4.2: add graph-derived treatment plan
    if graph_treatment_plan:
        care_pathway_data["graph_treatment_plan"] = {
            "treatments": graph_treatment_plan.get("treatments", []),
            "monitoring": graph_treatment_plan.get("monitoring", []),
            "complication_risks": graph_treatment_plan.get("complication_risks", []),
        }

    profile.care_pathway = json_safe(care_pathway_data)
    profile.risk_assessment = json_safe(risk)
    profile.evidence_summary = json_safe(_gather_evidence_summary(rule_results))
    profile.reasoning_chain = json_safe(reasoning)
    profile.information_gaps = json_safe(info_gaps)
    profile.milestones = json_safe(milestones)
    profile.version += 1
    profile.save()

    _generate_insights(profile, care_gaps, rule_results)

    return profile


def _build_differential(rule_results: list) -> list[dict]:
    """Build a ranked differential from rule evaluation results.

    Only diseases whose rules actually fired (score > 0) enter the differential;
    the raw score is normalized to a relative confidence (each disease's share of
    the total fired-rule weight) so the UI can show an interpretable percentage
    instead of an arbitrary magnitude. Graph-derived suggestions are appended
    later by augment_differential with source="knowledge_graph".
    """
    fired = [r for r in rule_results if r.total_score > 0]
    total = sum(r.total_score for r in fired) or 1
    return [
        {
            "disease_id": r.disease_id,
            "disease_name": r.disease_name,
            "score": round(r.total_score, 2),
            "confidence": round(r.total_score / total * 100),
            "matched_rules_count": len(r.matched_rules),
            "source": r.source,
            "evidence_grade": r.evidence_grade,
        }
        for r in fired
    ]


def _assess_disease_trajectory(patient, features, rule_results) -> dict:
    """Assess disease trajectory based on available data."""
    from .disease_trajectory import assess_trajectory
    return assess_trajectory(patient, features)


def _detect_care_gaps(patient, features) -> list[dict]:
    """Detect missing investigations, labs, or monitoring."""
    from .care_pathway import detect_care_gaps
    return detect_care_gaps(patient, features)


def _identify_information_gaps(features: dict) -> list[dict]:
    """Identify missing data that would improve diagnostic confidence."""
    gaps = []
    if "biopsy" not in features or not features.get("biopsy"):
        gaps.append({
            "field": "biopsy",
            "importance": "high",
            "message": "No biopsy findings — histology is essential for definitive diagnosis",
        })
    if features.get("proteinuria") == "none":
        # Only flag proteinuria quantification for suspected lupus nephritis,
        # where UPCR is specifically recommended for remission evaluation.
        biopsy_flags = features.get("biopsy", [])
        disease_features = features.get("features", [])
        is_lupus = (
            "fullHouse" in biopsy_flags
            or "lupus" in str(disease_features).lower()
        )
        if is_lupus:
            gaps.append({
                "field": "proteinuria",
                "importance": "high",
                "message": "Proteinuria not quantified — UPCR/ACR essential for lupus nephritis assessment and remission monitoring",
            })
    if features.get("latest_egfr") is None:
        gaps.append({
            "field": "egfr",
            "importance": "high",
            "message": "eGFR not available — kidney function is a core assessment variable",
        })
    if "labs" not in features or not any(
        lab in features.get("labs", []) for lab in ("lowC3", "lowC4", "anca", "anaDsDna", "pla2r", "antiGbm")
    ):
        gaps.append({
            "field": "serology",
            "importance": "medium",
            "message": "Limited serological data — complement, autoantibodies help narrow differential",
        })
    return gaps


def _build_reasoning_chain(patient, rule_results, trajectory, care_gaps) -> list[dict]:
    """Build a structured reasoning chain explaining the clinical assessment."""
    chain = []
    if rule_results:
        top = rule_results[0]
        chain.append({
            "step": "rule_evaluation",
            "finding": f"Top differential: {top.disease_name} (score {top.total_score})",
            "detail": f"{len(top.matched_rules)} matching criteria from {top.source}",
            "confidence": "high" if top.total_score > 10 else "moderate" if top.total_score > 5 else "low",
        })
    if trajectory.get("trend"):
        chain.append({
            "step": "trajectory_assessment",
            "finding": f"Disease trajectory: {trajectory['trend']}",
            "detail": trajectory.get("detail", ""),
            "confidence": trajectory.get("confidence", "moderate"),
        })
    if care_gaps:
        chain.append({
            "step": "care_gaps",
            "finding": f"{len(care_gaps)} care gap(s) identified",
            "detail": [g["message"] for g in care_gaps[:3]],
            "confidence": "high",
        })
    return chain


def _assess_risk(patient, features, trajectory) -> dict:
    """Assess risks: progression, relapse, kidney survival."""
    latest_egfr = features.get("latest_egfr") or getattr(patient, "latest_egfr", None)
    risk = {"overall": "unknown", "factors": []}

    if latest_egfr is not None:
        if latest_egfr < 30:
            risk["overall"] = "high"
            risk["factors"].append({
                "factor": "ckd_stage",
                "value": f"eGFR {latest_egfr} — Stage 4-5 CKD",
                "impact": "high_progression_risk",
            })
        elif latest_egfr < 60:
            risk["overall"] = "moderate"
            risk["factors"].append({
                "factor": "ckd_stage",
                "value": f"eGFR {latest_egfr} — Stage 3 CKD",
                "impact": "moderate_progression_risk",
            })
        else:
            risk["overall"] = "low" if risk.get("overall") == "unknown" else risk["overall"]

    if "edema" in features.get("features", []):
        risk["factors"].append({
            "factor": "active_disease",
            "value": "Active edema — suggests nephrotic syndrome",
            "impact": "relapse_or_active_disease",
        })

    if trajectory.get("trend") == "declining":
        risk["overall"] = "high"
        risk["factors"].append({
            "factor": "declining_trajectory",
            "value": "eGFR in sustained decline",
            "impact": "high_progression_risk",
        })

    return risk


def _generate_recommendations(care_gaps, rule_results) -> list[dict]:
    """Generate actionable recommendations from care gaps and rule results."""
    recommendations = []
    for gap in care_gaps:
        recommendations.append({
            "type": "investigation",
            "priority": gap.get("importance", "medium"),
            "message": gap["message"],
        })
    if rule_results:
        top = rule_results[0]
        recommendations.append({
            "type": "diagnostic_impression",
            "priority": "high",
            "message": f"Leading differential: {top.disease_name}",
            "detail": f"Score {top.total_score} from {top.source}",
        })
    return recommendations


def _gather_evidence_summary(rule_results) -> dict:
    """Summarize evidence grades across the differential."""
    grades = {}
    for r in rule_results:
        grade = r.evidence_grade or "NG"
        grades.setdefault(grade, 0)
        grades[grade] += 1
    return {"grade_distribution": grades, "total_diseases": len(rule_results)}


def _generate_insights(profile: ClinicalProfile, care_gaps: list, rule_results: list) -> None:
    """Generate ClinicalInsight objects from the reasoning output.

    Clears prior engine-generated insights to prevent duplicate accumulation
    on repeated reasoning runs (fixes H-1: ClinicalInsight duplicate bug).
    """
    patient = profile.patient

    # Remove prior engine-generated insights to prevent unbounded growth
    ClinicalInsight.objects.filter(patient=patient).delete()

    for gap in care_gaps:
        ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.CARE_GAP,
            priority=ClinicalInsight.Priority.HIGH if gap.get("importance") == "high" else ClinicalInsight.Priority.MEDIUM,
            title=f"Missing: {gap['field']}",
            description=gap["message"],
            reasoning="Care gap detected by clinical reasoning engine",
        )

    if rule_results:
        top = rule_results[0]
        ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.DIAGNOSTIC,
            priority=ClinicalInsight.Priority.HIGH,
            title=f"Leading differential: {top.disease_name}",
            description=f"Score {top.total_score} from {len(top.matched_rules)} matching criteria",
            reasoning=f"Evaluated against KnowledgeBaseEntry rules from {top.source}",
        )


def recompute_all_profiles() -> dict:
    """Recompute ClinicalProfile for all patients. Returns summary."""
    from patients.models import Patient

    total = 0
    errors = 0
    for patient in Patient.objects.iterator():
        try:
            reason_about_patient(patient)
            total += 1
        except Exception:
            logger.exception("Failed to reason about patient %s", patient.patient_id)
            errors += 1
    return {"total": total, "errors": errors}

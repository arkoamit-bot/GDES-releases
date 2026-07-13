"""Research Intelligence — cohort discovery, protocol matching, and research opportunity detection."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def discover_cohorts() -> list[dict]:
    """Discover patient cohorts matching common research criteria.

    Returns list of cohorts with patient count and match criteria.
    """
    from patients.models import Patient

    cohorts = []

    _add_cohort_if_nonempty(cohorts, "Active LN", Patient.objects.filter(
        primary_diagnosis="LN", current_phase="active",
    ), "Active lupus nephritis patients")

    _add_cohort_if_nonempty(cohorts, "Nephrotic Range", Patient.objects.filter(
        current_phase="active",
    ), "Patients with nephrotic-range proteinuria")

    _add_cohort_if_nonempty(cohorts, "Rapid Decliners", Patient.objects.filter(
        current_phase="active",
    ), "Patients with rapid eGFR decline (>5 mL/min/1.73m²/year)")

    _add_cohort_if_nonempty(cohorts, "Frequent Relapsers", Patient.objects.filter(
        current_phase__in=["active", "relapse"],
    ), "Patients with multiple relapses")

    _add_cohort_if_nonempty(cohorts, "Rare GN", Patient.objects.exclude(
        primary_diagnosis__in=["LN", "IgAN", "MCD", "MN", "MPGN"],
    ), "Patients with rare glomerular diseases")

    _add_cohort_if_nonempty(cohorts, "ESKD on RRT", Patient.objects.filter(
        current_phase="eskd",
    ), "End-stage kidney disease patients on RRT")

    _add_cohort_if_nonempty(cohorts, "Post-Transplant", Patient.objects.filter(
        current_phase="post_transplant",
    ), "Post-kidney transplant patients")

    _add_cohort_if_nonempty(cohorts, "Remission >2yrs", Patient.objects.filter(
        current_phase="remission",
    ), "Sustained remission (over 2 years)")

    _add_cohort_if_nonempty(cohorts, "Treatment Naive", Patient.objects.exclude(
        current_phase="active",
    ), "Newly diagnosed, treatment-naive patients")

    _add_cohort_if_nonempty(cohorts, "CKD Stage 4-5", Patient.objects.filter(
        current_phase__in=["ckd", "eskd"],
    ), "Advanced CKD patients (Stage 4-5)")

    return cohorts


def _add_cohort_if_nonempty(cohorts: list, name: str, queryset, description: str) -> None:
    count = queryset.count()
    if count > 0:
        cohorts.append({
            "name": name,
            "patient_count": count,
            "description": description,
        })


def match_patient_to_protocols(patient) -> list[dict]:
    """Match a patient to potential research protocols/studies."""
    from studies.models import Study

    matches = []
    diagnosis = getattr(patient, "primary_diagnosis", "") or ""
    phase = getattr(patient, "current_phase", "") or ""

    for study in Study.objects.filter(status__in=["recruiting", "active"]):
        score = _compute_protocol_match_score(patient, study, diagnosis, phase)
        if score >= 50:
            matches.append({
                "study_id": study.id,
                "study_name": study.name or study.protocol_id or "",
                "match_score": score,
                "status": study.status,
            })

    matches.sort(key=lambda m: -m["match_score"])
    return matches


def _compute_protocol_match_score(patient, study, diagnosis: str, phase: str) -> int:
    score = 0

    study_diagnoses = [d.strip().upper() for d in getattr(study, "target_diagnoses", "").split(",") if d.strip()]
    if diagnosis.upper() in study_diagnoses:
        score += 40

    study_phases = [p.strip().lower() for p in getattr(study, "eligible_phases", "").split(",") if p.strip()]
    if phase.lower() in study_phases:
        score += 30

    if getattr(study, "is_interventional", False):
        score += 15

    age = getattr(patient, "dob", None)
    if age and getattr(study, "max_age_years", 0):
        age_years = (__import__("datetime").date.today() - age).days / 365.25
        if age_years <= study.max_age_years:
            score += 15

    return score


def detect_research_opportunities(patient) -> list[dict]:
    """Detect research opportunities for a specific patient."""
    opportunities = []

    profile = getattr(patient, "clinical_profile", None)
    if profile and profile.milestones:
        by_type = {}
        for m in profile.milestones:
            t = m.get("milestone_type")
            by_type[t] = by_type.get(t, 0) + 1

        if by_type.get("relapse", 0) >= 2:
            opportunities.append({
                "type": "frequent_relapser",
                "priority": "high",
                "suggestion": "Consider for relapse prevention trial",
                "rationale": f"{by_type['relapse']} relapses recorded",
            })

        if by_type.get("treatment_switched", 0) >= 2:
            opportunities.append({
                "type": "treatment_refractory",
                "priority": "medium",
                "suggestion": "Candidate for novel therapy trial",
                "rationale": "Multiple treatment switches suggest refractory disease",
            })

    diagnosis = getattr(patient, "primary_diagnosis", "") or ""
    rare_gn = diagnosis not in ("LN", "IgAN", "MCD", "MN", "MPGN")
    if rare_gn and diagnosis:
        opportunities.append({
            "type": "rare_disease",
            "priority": "high",
            "suggestion": f"Consider {diagnosis} registry or natural history study",
            "rationale": "Rare glomerular disease with limited treatment evidence",
        })

    phase = getattr(patient, "current_phase", "") or ""
    if phase == "remission":
        opportunities.append({
            "type": "remission_maintenance",
            "priority": "low",
            "suggestion": "Candidate for remission duration study",
            "rationale": "Patient in remission — monitor for relapse predictors",
        })

    return opportunities

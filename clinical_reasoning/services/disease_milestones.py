"""Longitudinal Disease Intelligence — milestone detection and trajectory tracking."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

from clinical_reasoning.json_util import json_safe

logger = logging.getLogger(__name__)


@dataclass
class DiseaseMilestone:
    milestone_type: str
    label: str
    date_identified: date | None
    details: dict | None = None
    confidence: str = "moderate"

    def to_dict(self) -> dict:
        return {
            "milestone_type": self.milestone_type,
            "label": self.label,
            "date_identified": self.date_identified.isoformat() if self.date_identified else None,
            "details": self.details or {},
            "confidence": self.confidence,
        }


def detect_milestones(patient, features: dict, trajectory: dict) -> list[dict]:
    """Detect disease milestones from patient data.

    Milestones tracked:
      - initial_diagnosis     — first recorded diagnosis
      - biopsy_performed      — renal biopsy completed
      - remission_achieved    — first remission
      - relapse_detected      — disease relapse
      - eskd_reached          — end-stage kidney disease
      - treatment_started     — first immunosuppression
      - treatment_switched    — therapy change
    """
    milestones = []

    _check_diagnosis_milestone(patient, milestones)
    _check_biopsy_milestone(patient, milestones)
    _check_remission_milestone(patient, features, trajectory, milestones)
    _check_eskd_milestone(patient, features, milestones)
    _check_treatment_milestones(patient, milestones)

    existing = _load_existing_milestones(patient)
    merged = _merge_milestones(existing, milestones)
    _save_milestones(patient, merged)

    return merged


def _check_diagnosis_milestone(patient, milestones: list) -> None:
    diagnosis = getattr(patient, "primary_diagnosis", "") or ""
    reg_date = getattr(patient, "registration_date", None) or getattr(patient, "enrollment_date", None)
    if diagnosis:
        milestones.append(DiseaseMilestone(
            milestone_type="diagnosis",
            label=f"Diagnosed with {diagnosis}",
            date_identified=reg_date,
            details={"diagnosis": diagnosis},
            confidence="high",
        ).to_dict())


def _check_biopsy_milestone(patient, milestones: list) -> None:
    try:
        biopsy = patient.biopsies.order_by("biopsy_date").first()
        if biopsy:
            milestones.append(DiseaseMilestone(
                milestone_type="biopsy",
                label="Renal biopsy performed",
                date_identified=biopsy.biopsy_date,
                details={"histology": biopsy.histological_diagnosis or ""},
                confidence="high",
            ).to_dict())
    except Exception:
        pass


def _check_remission_milestone(patient, features: dict, trajectory: dict, milestones: list) -> None:
    phase = features.get("disease_phase", "")
    if phase == "remission":
        milestones.append(DiseaseMilestone(
            milestone_type="remission",
            label="Remission achieved",
            date_identified=None,
            details={"trend": trajectory.get("trend", "")},
            confidence="high",
        ).to_dict())


def _check_eskd_milestone(patient, features: dict, milestones: list) -> None:
    phase = features.get("disease_phase", "")
    latest_egfr = getattr(patient, "latest_egfr", None)
    if phase == "eskd" or (latest_egfr is not None and float(latest_egfr) < 15):
        milestones.append(DiseaseMilestone(
            milestone_type="eskd",
            label="End-stage kidney disease reached",
            date_identified=None,
            details={"latest_egfr": float(latest_egfr) if latest_egfr else None},
            confidence="high",
        ).to_dict())


def _check_treatment_milestones(patient, milestones: list) -> None:
    try:
        from treatments.models import TreatmentExposure
        treatments = TreatmentExposure.objects.filter(patient=patient).order_by("start_date")
        first = treatments.first()
        if first:
            first_name = first.drug_name or getattr(first.drug, "generic_name", "")
            milestones.append(DiseaseMilestone(
                milestone_type="treatment_started",
                label=f"Treatment started: {first_name}",
                date_identified=first.start_date,
                details={"treatment": first_name},
                confidence="high",
            ).to_dict())

        if treatments.count() > 1:
            second = treatments[1]
            second_name = second.drug_name or getattr(second.drug, "generic_name", "")
            prev_name = (first.drug_name or getattr(first.drug, "generic_name", "")) if first else ""
            milestones.append(DiseaseMilestone(
                milestone_type="treatment_switched",
                label=f"Treatment switched to: {second_name}",
                date_identified=second.start_date,
                details={"previous": prev_name,
                         "current": second_name},
                confidence="moderate",
            ).to_dict())
    except Exception:
        pass


def _load_existing_milestones(patient) -> list[dict]:
    try:
        profile = patient.clinical_profile
        return profile.milestones or []
    except Exception:
        return []


def _merge_milestones(existing: list[dict], detected: list[dict]) -> list[dict]:
    seen_types = {m["milestone_type"] for m in existing}
    merged = list(existing)
    for m in detected:
        if m["milestone_type"] not in seen_types:
            merged.append(m)
            seen_types.add(m["milestone_type"])
    merged.sort(key=lambda x: x.get("date_identified") or "")
    return merged


def _save_milestones(patient, milestones: list[dict]) -> None:
    # Persist onto the ClinicalProfile if one already exists. On the very first
    # reasoning pass the profile is created later in the pipeline (engine
    # get_or_create), which stores the same milestones — so a no-op here (0 rows
    # updated) is correct, not an error. A filtered update avoids the reverse
    # OneToOne accessor raising RelatedObjectDoesNotExist and logging spurious
    # error tracebacks on every first pass for a new patient.
    from clinical_reasoning.models import ClinicalProfile

    ClinicalProfile.objects.filter(patient=patient).update(
        milestones=json_safe(milestones)
    )


def compute_trajectory_summary(patient, milestones: list[dict]) -> dict:
    """Compute a summary of the patient's disease course from milestones."""
    total = len(milestones)
    by_type: dict[str, int] = {}
    for m in milestones:
        t = m["milestone_type"]
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total_milestones": total,
        "by_type": by_type,
        "has_diagnosis": "diagnosis" in by_type,
        "has_biopsy": "biopsy" in by_type,
        "has_remission": "remission" in by_type,
        "has_eskd": "eskd" in by_type,
        "treatment_changes": by_type.get("treatment_switched", 0),
    }

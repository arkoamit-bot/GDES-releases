"""Base class for disease-specific follow-up protocols.

Each subclass defines:
- disease_id: machine key matching ClinicalProfile differential entries
- disease_name: human-readable label
- visit_schedule: list of (label, days_from_index) timepoints
- required_labs: list of LabTest codes needed at each visit
- monitoring_parameters: clinical parameters to track
- drug_monitoring: mapping drug_class -> list of lab codes + intervals
- escalation_criteria: conditions that trigger escalation
- discharge_criteria: conditions for protocol discharge
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LabRequirement:
    code: str
    name: str = ""
    interval_days: int = 0
    priority: str = "routine"
    clinical_reason: str = ""


@dataclass
class DrugMonitoring:
    drug_class: str
    lab_codes: list = field(default_factory=list)
    interval_days: int = 90
    clinical_reason: str = ""


@dataclass
class VisitTimepoint:
    label: str
    days_from_index: int
    window_days: int = 7
    required_labs: list = field(default_factory=list)
    is_early_safety: bool = False


class FollowUpProtocol:
    disease_id = "general"
    disease_name = "General Follow-up"
    description = ""

    # Base visit interval for routine follow-up (days).
    base_visit_interval_days: int = 90

    # Protocol visit schedule: timepoints relative to index/enrollment date.
    visit_schedule: list[VisitTimepoint] = []

    # Labs required at each routine visit.
    required_labs: list[LabRequirement] = []

    # Labs that should be checked at defined intervals regardless of visits.
    interval_labs: list[LabRequirement] = []

    # Drug-specific monitoring.
    drug_monitoring: list[DrugMonitoring] = []

    # Escalation triggers.
    escalation_criteria: list[str] = []

    # Discharge criteria.
    discharge_criteria: list[str] = []

    # Risk factors that shorten intervals.
    high_risk_multiplier: float = 0.5
    moderate_risk_multiplier: float = 0.75

    def get_visit_interval(self, patient, risk_category="moderate"):
        base = self.base_visit_interval_days
        multipliers = {
            "very_high": self.high_risk_multiplier,
            "high": 0.6,
            "moderate": self.moderate_risk_multiplier,
            "low": 1.0,
        }
        return max(14, int(base * multipliers.get(risk_category, 1.0)))

    def get_labs_for_interval(self, days_since_index: int) -> list[LabRequirement]:
        due = []
        for lab in self.required_labs:
            due.append(lab)
        for lab in self.interval_labs:
            if lab.interval_days and days_since_index % lab.interval_days < 30:
                due.append(lab)
        return due

    def get_drug_monitoring(self, drug_class: str) -> Optional[DrugMonitoring]:
        for dm in self.drug_monitoring:
            if dm.drug_class == drug_class:
                return dm
        return None

    def get_timepoints(self) -> list[VisitTimepoint]:
        return self.visit_schedule

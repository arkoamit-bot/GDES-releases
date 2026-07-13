"""ANCA Vasculitis follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class ANCAFollowUp(FollowUpProtocol):
    disease_id = "anca_vasculitis"
    disease_name = "ANCA Vasculitis"
    description = "KDIGO 2024 guideline-based follow-up for ANCA-associated Vasculitis"

    base_visit_interval_days = 60

    visit_schedule = [
        VisitTimepoint("Week 1", 7, is_early_safety=True),
        VisitTimepoint("Week 2", 14, is_early_safety=True),
        VisitTimepoint("Week 4", 28, is_early_safety=True),
        VisitTimepoint("Month 2", 60),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 4", 120),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 9", 270),
        VisitTimepoint("Month 12", 365),
        VisitTimepoint("Month 15", 455),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
        VisitTimepoint("Year 3", 1095),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR"),
        LabRequirement("upcr", "Spot UPCR"),
        LabRequirement("urine_analysis", "Urine Analysis"),
        LabRequirement("cbc", "Complete Blood Count"),
        LabRequirement("crp", "C-Reactive Protein"),
        LabRequirement("esr", "ESR"),
    ]

    interval_labs = [
        LabRequirement("anca", "ANCA Serology", interval_days=90,
                       clinical_reason="ANCA titre monitoring for relapse prediction"),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
        LabRequirement("glucose", "Fasting Blood Glucose", interval_days=90),
    ]

    drug_monitoring = [
        DrugMonitoring("rituximab", ["cbc", "cd19", "immunoglobulins", "anca"], 90,
                       clinical_reason="Rituximab: monitor CD19 count q3mo, pre-emptive dosing at B-cell return"),
        DrugMonitoring("cyclophosphamide", ["cbc", "lft", "urine_analysis"], 14),
        DrugMonitoring("steroid", ["cbc", "glucose", "hba1c", "bone_density"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("azathioprine", ["cbc", "lft", "tpmt"], 30),
    ]

    escalation_criteria = [
        "Rising ANCA titre with clinical symptoms",
        "New organ involvement (pulmonary hemorrhage, mononeuritis)",
        "Rapidly progressive glomerulonephritis",
        "eGFR decline > 30%",
        "Relapse while on maintenance therapy",
    ]

    discharge_criteria = [
        "Sustained remission for 3 years",
        "Off immunosuppression for 2 years",
        "ANCA negative for 1 year",
        "No relapse during steroid taper",
    ]

"""Anti-GBM Disease follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class AntiGBMFollowUp(FollowUpProtocol):
    disease_id = "anti_gbm_disease"
    disease_name = "Anti-GBM Disease"
    description = "KDIGO 2024 guideline-based follow-up for Anti-GBM (Goodpasture's) Disease"

    base_visit_interval_days = 60

    visit_schedule = [
        VisitTimepoint("Week 1", 7, is_early_safety=True),
        VisitTimepoint("Week 2", 14, is_early_safety=True),
        VisitTimepoint("Week 3", 21, is_early_safety=True),
        VisitTimepoint("Month 1", 30),
        VisitTimepoint("Month 2", 60),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 9", 270),
        VisitTimepoint("Month 12", 365),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR"),
        LabRequirement("upcr", "Spot UPCR"),
        LabRequirement("urine_analysis", "Urine Analysis"),
        LabRequirement("cbc", "Complete Blood Count"),
        LabRequirement("anti_gbm", "Anti-GBM Antibody"),
    ]

    interval_labs = [
        LabRequirement("anti_gbm", "Anti-GBM Antibody", interval_days=90,
                       clinical_reason="Anti-GBM titre monitoring for relapse"),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
        LabRequirement("glucose", "Fasting Blood Glucose", interval_days=90),
    ]

    drug_monitoring = [
        DrugMonitoring("cyclophosphamide", ["cbc", "lft", "urine_analysis"], 14),
        DrugMonitoring("steroid", ["cbc", "glucose", "hba1c"], 30),
        DrugMonitoring("rituximab", ["cbc", "cd19"], 90),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
    ]

    escalation_criteria = [
        "Rising anti-GBM titre",
        "Pulmonary hemorrhage",
        "Rapidly progressive GN with crescents",
        "Oliguric or dialysis-dependent AKI",
    ]

    discharge_criteria = [
        "Anti-GBM negative for 2 years",
        "Off immunosuppression for 1 year",
        "Stable kidney function for 2 years",
    ]

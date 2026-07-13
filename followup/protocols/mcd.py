"""Minimal Change Disease follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class MCDFollowUp(FollowUpProtocol):
    disease_id = "minimal_change_disease"
    disease_name = "Minimal Change Disease"
    description = "KDIGO 2024 guideline-based follow-up for Minimal Change Disease"

    base_visit_interval_days = 90

    visit_schedule = [
        VisitTimepoint("Week 1", 7, is_early_safety=True),
        VisitTimepoint("Week 2", 14, is_early_safety=True),
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
        LabRequirement("albumin", "Serum Albumin"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
        LabRequirement("glucose", "Fasting Blood Glucose", interval_days=180),
        LabRequirement("hba1c", "HbA1c", interval_days=180),
    ]

    drug_monitoring = [
        DrugMonitoring("steroid", ["cbc", "glucose", "hba1c"], 30, "Steroid: monitor blood glucose, bone density"),
        DrugMonitoring("mmf", ["cbc", "lft"], 30, "MMF: monitor CBC and LFT monthly"),
        DrugMonitoring("cni", ["cbc", "creatinine", "tacrolimus_level", "cyclosporine_level"], 30, "CNI: monitor trough levels q3mo, Cr monthly"),
        DrugMonitoring("rituximab", ["cbc", "cd19"], 90, "Rituximab: monitor CD19 count q3mo"),
    ]

    escalation_criteria = [
        "Steroid-dependent relapsing course",
        "Frequent relapses (> 2/year)",
        "CNI toxicity (eGFR decline > 30%)",
        "Infection on immunosuppression",
    ]

    discharge_criteria = [
        "Complete remission for 2 years",
        "Off all immunosuppression for 1 year",
        "No relapses for 2 years",
    ]

"""FSGS follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class FSGSFollowUp(FollowUpProtocol):
    disease_id = "focal_segmental_glomerulosclerosis"
    disease_name = "FSGS"
    description = "KDIGO 2024 guideline-based follow-up for Focal Segmental Glomerulosclerosis"

    base_visit_interval_days = 90

    visit_schedule = [
        VisitTimepoint("Week 2", 14, is_early_safety=True),
        VisitTimepoint("Month 1", 30),
        VisitTimepoint("Month 2", 60),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 9", 270),
        VisitTimepoint("Month 12", 365),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
        VisitTimepoint("Year 3", 1095),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR"),
        LabRequirement("upcr", "Spot UPCR"),
        LabRequirement("urine_protein", "Urine Protein (24h)", priority="high"),
        LabRequirement("albumin", "Serum Albumin"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30),
        DrugMonitoring("steroid", ["cbc", "glucose"], 30),
        DrugMonitoring("cni", ["creatinine", "tacrolimus_level", "cyclosporine_level"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("rituximab", ["cbc", "cd19"], 90),
    ]

    escalation_criteria = [
        "Nephrotic syndrome despite 16 weeks of immunosuppression",
        "eGFR decline > 30% over 3 months",
        "CNI nephrotoxicity suspected",
        "Recurrent FSGS after transplant",
    ]

    discharge_criteria = [
        "Partial remission for 2 years",
        "eGFR stable > 45 for 3 years",
        "Off immunosuppression > 2 years",
    ]

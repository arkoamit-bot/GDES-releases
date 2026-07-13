"""Generic follow-up protocol for unmatched/unclassified kidney disease."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint
from . import register


@register
class GeneralFollowUp(FollowUpProtocol):
    disease_id = "general"
    disease_name = "General Kidney Disease"
    description = "Standard follow-up for chronic kidney disease without a specific GN diagnosis"

    base_visit_interval_days = 180

    visit_schedule = [
        VisitTimepoint("Month 1", 30),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 12", 365),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR"),
        LabRequirement("urine_protein", "Urine Protein (24h)"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=180),
        LabRequirement("lft", "Liver Function Test", interval_days=180),
    ]

    escalation_criteria = [
        "eGFR decline > 30% in 3 months",
        "New nephrotic-range proteinuria",
        "Hospitalization for AKI",
    ]

    discharge_criteria = [
        "eGFR stable > 60 for 2 years",
        "No proteinuria for 1 year",
        "Transferred to general CKD clinic",
    ]

"""IgA Nephropathy follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class IgANFollowUp(FollowUpProtocol):
    disease_id = "iga_nephropathy"
    disease_name = "IgA Nephropathy"
    description = "KDIGO 2024 guideline-based follow-up for IgA Nephropathy"

    base_visit_interval_days = 90

    visit_schedule = [
        VisitTimepoint("Month 1", 30),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 9", 270),
        VisitTimepoint("Month 12", 365, required_labs=["creatinine", "egfr", "upcr"]),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
        VisitTimepoint("Year 3", 1095),
        VisitTimepoint("Year 4", 1460),
        VisitTimepoint("Year 5", 1825),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR (CKD-EPI)"),
        LabRequirement("upcr", "Spot UPCR"),
        LabRequirement("urine_protein", "Urine Protein (24h)", priority="high"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=180),
        LabRequirement("lft", "Liver Function Test", interval_days=180),
        LabRequirement("albumin", "Serum Albumin", interval_days=180),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30, "RAASi: check Cr/K+ 2 weeks after dose change, then q3mo"),
        DrugMonitoring("sglt2i", ["creatinine"], 90, "SGLT2i: monitor eGFR at follow-up visits"),
        DrugMonitoring("finerenone", ["creatinine", "potassium"], 30, "Finerenone: check Cr/K+ 4 weeks after initiation"),
    ]

    escalation_criteria = [
        "eGFR decline > 30% in 3 months",
        "Proteinuria > 1 g/day despite optimized RAASi",
        "Nephrotic-range proteinuria (> 3.5 g/day)",
        "Rapidly progressive course with crescents",
    ]

    discharge_criteria = [
        "No proteinuria (< 0.3 g/day) for 2 years",
        "eGFR stable > 60 for 3 years",
        "Off immunosuppression for 2 years",
        "Transferred to primary care nephrology",
    ]

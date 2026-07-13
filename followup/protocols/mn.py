"""Membranous Nephropathy follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class MembranousFollowUp(FollowUpProtocol):
    disease_id = "membranous_nephropathy"
    disease_name = "Membranous Nephropathy"
    description = "KDIGO 2024 guideline-based follow-up for Membranous Nephropathy"

    base_visit_interval_days = 90

    visit_schedule = [
        VisitTimepoint("Month 1", 30),
        VisitTimepoint("Month 3", 90),
        VisitTimepoint("Month 6", 180),
        VisitTimepoint("Month 9", 270),
        VisitTimepoint("Month 12", 365),
        VisitTimepoint("Month 18", 545),
        VisitTimepoint("Month 24", 730),
        VisitTimepoint("Year 3", 1095),
        VisitTimepoint("Year 4", 1460),
        VisitTimepoint("Year 5", 1825),
    ]

    required_labs = [
        LabRequirement("creatinine", "Serum Creatinine"),
        LabRequirement("egfr", "eGFR"),
        LabRequirement("upcr", "Spot UPCR"),
        LabRequirement("urine_protein", "Urine Protein (24h)", priority="high"),
        LabRequirement("albumin", "Serum Albumin"),
        LabRequirement("pla2r", "Anti-PLA2R Ab", priority="high"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
        LabRequirement("pla2r", "Anti-PLA2R Ab", interval_days=180,
                       clinical_reason="Serological monitoring of disease activity"),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30),
        DrugMonitoring("steroid", ["cbc", "glucose", "hba1c"], 30),
        DrugMonitoring("cni", ["creatinine", "tacrolimus_level", "cyclosporine_level"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("rituximab", ["cbc", "cd19", "pla2r"], 90),
        DrugMonitoring("cyclophosphamide", ["cbc", "lft", "urine_analysis"], 14,
                       clinical_reason="Cyclophosphamide: monitor CBC weekly during pulse therapy"),
    ]

    escalation_criteria = [
        "Rising anti-PLA2R with worsening proteinuria",
        "Nephrotic syndrome > 12 months",
        "eGFR decline > 30%",
        "Thromboembolic complication",
    ]

    discharge_criteria = [
        "Anti-PLA2R negative for 2 years",
        "Complete remission for 2 years",
        "Off immunosuppression for 2 years",
    ]

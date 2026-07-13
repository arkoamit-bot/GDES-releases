"""C3 Glomerulopathy follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class C3GFollowUp(FollowUpProtocol):
    disease_id = "c3_glomerulopathy"
    disease_name = "C3 Glomerulopathy"
    description = "KDIGO 2024 guideline-based follow-up for C3 Glomerulopathy"

    base_visit_interval_days = 60

    visit_schedule = [
        VisitTimepoint("Month 1", 30),
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
        LabRequirement("urine_protein", "Urine Protein (24h)", priority="high"),
        LabRequirement("c3", "Complement C3"),
        LabRequirement("c4", "Complement C4"),
        LabRequirement("c5b9", "Complement sC5b-9"),
    ]

    interval_labs = [
        LabRequirement("c3", "Complement C3", interval_days=90,
                       clinical_reason="C3 monitoring for disease activity"),
        LabRequirement("c5b9", "Complement sC5b-9", interval_days=180),
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=180),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30),
        DrugMonitoring("steroid", ["cbc", "glucose"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("rituximab", ["cbc", "cd19"], 90),
        DrugMonitoring("eculizumab", ["cbc", "ldh", "meningococcal_vaccination"], 30,
                       clinical_reason="Eculizumab: monitor for hemolysis, ensure meningococcal vaccination"),
    ]

    escalation_criteria = [
        "Persistent low C3 with high sC5b-9 levels",
        "Nephrotic-range proteinuria despite therapy",
        "eGFR decline > 25% over 3 months",
        "Crescentic transformation on repeat biopsy",
    ]

    discharge_criteria = [
        "Normal C3 levels for 2 years",
        "Proteinuria < 0.5 g/day for 2 years",
        "Stable eGFR > 60 for 3 years",
    ]

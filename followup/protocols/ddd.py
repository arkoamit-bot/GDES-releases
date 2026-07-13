"""Dense Deposit Disease follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class DDDFollowUp(FollowUpProtocol):
    disease_id = "dense_deposit_disease"
    disease_name = "Dense Deposit Disease"
    description = "KDIGO 2024 guideline-based follow-up for Dense Deposit Disease (DDD)"

    base_visit_interval_days = 60

    visit_schedule = [
        VisitTimepoint("Month 1", 30),
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
        LabRequirement("c3", "Complement C3"),
        LabRequirement("c4", "Complement C4"),
        LabRequirement("c5b9", "Complement sC5b-9"),
    ]

    interval_labs = [
        LabRequirement("c3", "Complement C3", interval_days=90),
        LabRequirement("c5b9", "Complement sC5b-9", interval_days=90),
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=180),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30),
        DrugMonitoring("steroid", ["cbc", "glucose"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("eculizumab", ["cbc", "ldh", "meningococcal_vaccination"], 30),
    ]

    escalation_criteria = [
        "Persistent low C3 with nephrotic-range proteinuria",
        "eGFR decline > 25% over 3 months",
        "Crescentic transformation on biopsy",
        "Optic fundus drusen (acquired partial lipodystrophy)",
    ]

    discharge_criteria = [
        "Normal C3 levels for 2 years",
        "Proteinuria < 0.5 g/day for 2 years",
        "Stable eGFR > 45 for 3 years",
    ]

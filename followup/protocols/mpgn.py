"""MPGN / Immune Complex MPGN follow-up protocol (KDIGO 2024)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class MPGNFollowUp(FollowUpProtocol):
    disease_id = "mpgn"
    disease_name = "MPGN / Immune Complex MPGN"
    description = "KDIGO 2024 guideline-based follow-up for Membranoproliferative GN"

    base_visit_interval_days = 90

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
        LabRequirement("albumin", "Serum Albumin"),
        LabRequirement("c3", "Complement C3"),
        LabRequirement("c4", "Complement C4"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=90),
        LabRequirement("lft", "Liver Function Test", interval_days=180),
        LabRequirement("c3", "Complement C3", interval_days=90),
        LabRequirement("c4", "Complement C4", interval_days=90),
        LabRequirement("hepatitis_serology", "Hepatitis B/C Serology", interval_days=365,
                       clinical_reason="Annual screening for infection-associated MPGN"),
    ]

    drug_monitoring = [
        DrugMonitoring("raasi", ["creatinine", "potassium"], 30),
        DrugMonitoring("steroid", ["cbc", "glucose"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30),
        DrugMonitoring("rituximab", ["cbc", "cd19"], 90),
    ]

    escalation_criteria = [
        "Nephrotic-range proteinuria despite treatment",
        "eGFR decline > 25%",
        "Active urinary sediment",
        "Infection-associated relapse",
    ]

    discharge_criteria = [
        "Remission for 2 years",
        "Normal complement levels for 1 year",
        "Stable eGFR > 45 for 2 years",
    ]

"""Lupus Nephritis follow-up protocol (KDIGO 2024 / EULAR-ERA 2023)."""

from .base import FollowUpProtocol, LabRequirement, VisitTimepoint, DrugMonitoring
from . import register


@register
class LupusNephritisFollowUp(FollowUpProtocol):
    disease_id = "lupus_nephritis"
    disease_name = "Lupus Nephritis"
    description = "KDIGO 2024 / EULAR-ERA 2023 guideline-based follow-up for Lupus Nephritis"

    base_visit_interval_days = 60

    visit_schedule = [
        VisitTimepoint("Week 2", 14, is_early_safety=True),
        VisitTimepoint("Month 1", 30),
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
        LabRequirement("urine_protein", "Urine Protein (24h)", priority="high"),
        LabRequirement("albumin", "Serum Albumin"),
        LabRequirement("c3", "Complement C3"),
        LabRequirement("c4", "Complement C4"),
        LabRequirement("anti_dsdna", "Anti-dsDNA Ab"),
    ]

    interval_labs = [
        LabRequirement("cbc", "Complete Blood Count", interval_days=30),
        LabRequirement("lft", "Liver Function Test", interval_days=90),
        LabRequirement("c3", "Complement C3", interval_days=90),
        LabRequirement("c4", "Complement C4", interval_days=90),
        LabRequirement("anti_dsdna", "Anti-dsDNA Ab", interval_days=90),
    ]

    drug_monitoring = [
        DrugMonitoring("hcq", ["eye_exam"], 365, "HCQ: annual ophthalmology screening after 5 years"),
        DrugMonitoring("steroid", ["cbc", "glucose", "hba1c"], 30),
        DrugMonitoring("mmf", ["cbc", "lft"], 30, "MMF: monitor CBC monthly for first 6 months"),
        DrugMonitoring("cyclophosphamide", ["cbc", "lft", "urine_analysis"], 14),
        DrugMonitoring("rituximab", ["cbc", "cd19", "immunoglobulins"], 90),
        DrugMonitoring("cni", ["creatinine", "tacrolimus_level"], 30),
        DrugMonitoring("azathioprine", ["cbc", "lft", "tpmt"], 30,
                       clinical_reason="AZA: check TPMT before starting, monitor CBC monthly"),
    ]

    escalation_criteria = [
        "Rising anti-dsDNA with falling C3/C4",
        "Worsening proteinuria > 1 g/day increase",
        "eGFR decline > 25%",
        "Active urinary sediment (RBC casts)",
        "Extra-renal lupus flare",
    ]

    discharge_criteria = [
        "Complete renal remission for 3 years",
        "Off immunosuppression for 2 years",
        "Stable on HCQ alone",
        "No extra-renal activity for 2 years",
    ]

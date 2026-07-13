"""
Prescription safety checks — enhanced with drug-drug interaction and
drug-disease contraindication engines from Phase 3.2.

     1. Renal dosing       — drug flagged for renal caution below eGFR
     2. Prior intolerance   — re-prescribing a drug stopped for intolerance/AE
     3. Duplicate therapy   — two drugs of same research class on one Rx
     4. Glycaemic effect    — steroid/CNI hyperglycaemia monitoring
     5. Drug interactions   — nephrology DDI check (Phase 3.2)
     6. Contraindications   — drug-disease check (Phase 3.2)
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from treatments.models import DrugClass, StopReason, TreatmentExposure


@dataclass
class SafetyWarning:
    level: str        # "warning" | "block"
    code: str
    message: str


def check_prescription(prescription) -> list[SafetyWarning]:
    warnings: list[SafetyWarning] = []
    patient = prescription.patient
    items = list(prescription.items.select_related("drug").all())

    # 1. Renal dosing -------------------------------------------------------
    egfr = patient.latest_egfr
    if egfr is not None:
        for it in items:
            threshold = it.drug.egfr_caution_below
            if threshold is not None and egfr < threshold:
                warnings.append(SafetyWarning(
                    "warning", "renal_dose",
                    f"{it.drug.generic_name}: eGFR {egfr} is below the caution "
                    f"threshold ({threshold}). Review dose / contraindication."))

    # 2. Prior intolerance --------------------------------------------------
    intolerant_drug_ids = set(
        TreatmentExposure.objects
        .filter(patient=patient,
                stop_reason__in=[StopReason.INTOLERANCE, StopReason.ADVERSE_EVENT])
        .values_list("drug_id", flat=True))
    for it in items:
        if it.drug_id in intolerant_drug_ids:
            warnings.append(SafetyWarning(
                "block", "prior_intolerance",
                f"{it.drug.generic_name} was previously stopped for intolerance "
                f"/ adverse event for this patient."))

    # 3. Duplicate therapy --------------------------------------------------
    no_dup = {DrugClass.OTHER, DrugClass.INSULIN}
    by_class: dict[str, list[str]] = defaultdict(list)
    for it in items:
        if it.drug.drug_class not in no_dup:
            by_class[it.drug.drug_class].append(it.drug.generic_name)
    for cls, names in by_class.items():
        if len(names) > 1:
            label = dict(DrugClass.choices)[cls]
            warnings.append(SafetyWarning(
                "warning", "duplicate_therapy",
                f"Multiple {label} agents on one prescription: {', '.join(names)}."))

    # 4. Glycaemic effect of steroids / CNIs -------------------------------
    hyperglyc = sorted({
        it.drug.generic_name for it in items
        if it.drug.drug_class in (DrugClass.STEROID, DrugClass.CNI)})
    if hyperglyc:
        agents = ", ".join(hyperglyc)
        is_diabetic = getattr(patient, "diabetes_status", "none") not in ("", "none", None)
        if is_diabetic:
            warnings.append(SafetyWarning(
                "warning", "antidiabetic_intensification",
                f"{agents} raise blood glucose — review/intensify antidiabetic "
                f"therapy and monitor glucose (this patient is diabetic)."))
        else:
            warnings.append(SafetyWarning(
                "warning", "steroid_hyperglycaemia",
                f"{agents} can cause hyperglycaemia — monitor blood glucose for "
                f"steroid/CNI-induced diabetes."))

    # 5. Drug-drug interactions (Phase 3.2) ---------------------------------
    drug_names = [it.drug.generic_name for it in items if it.drug_id]
    if len(drug_names) >= 2:
        try:
            from treatments.interactions import check_interactions
            interactions = check_interactions(drug_names)
            for interaction in interactions:
                level = "block" if interaction.severity == "major" else "warning"
                warnings.append(SafetyWarning(
                    level, f"ddi_{interaction.severity}",
                    f"Interaction: {interaction.drug_a} + {interaction.drug_b}: "
                    f"{interaction.severity.upper()}. {interaction.mechanism}. "
                    f"Management: {interaction.management}"))
        except ImportError:
            pass

    # 6. Drug-disease contraindications (Phase 3.2) ------------------------
    if patient.primary_diagnosis:
        try:
            from treatments.contraindications import check_contraindications
            patient_diseases = [patient.primary_diagnosis]
            if patient.diabetes_status and patient.diabetes_status != "none":
                patient_diseases.append("diabetes")
            if patient.latest_egfr is not None:
                if patient.latest_egfr < 30:
                    patient_diseases.append("ckd_stage_4_5")
                elif patient.latest_egfr < 60:
                    patient_diseases.append("ckd_stage_3_5")

            for it in items:
                results = check_contraindications(
                    it.drug.generic_name, patient_diseases)
                for ctr in results:
                    level = "block" if ctr.severity == "absolute" else "warning"
                    alt_text = f" Alternative: {ctr.alternative}" if ctr.alternative else ""
                    warnings.append(SafetyWarning(
                        level, f"contraindication_{ctr.severity}",
                        f"{it.drug.generic_name} — {ctr.reason}.{alt_text}"))
        except ImportError:
            pass

    return warnings

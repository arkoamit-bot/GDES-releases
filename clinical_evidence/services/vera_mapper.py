"""Vera Health Patient Data Mapper.

Serializes GDES patient data into a structured dict suitable for
the Vera Health clinical reasoning API. Handles demographics, kidney
disease data, laboratory results, vital signs, current medications,
comorbidities, and pathology findings.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)


def map_patient_for_vera(patient, profile=None) -> dict[str, Any]:
    """Serialize a Patient into a Vera-compatible data payload.

    Args:
        patient: clinic.models.Patient instance.
        profile: clinical_reasoning.models.ClinicalProfile (optional).

    Returns:
        Nested dict with demographics, disease, labs, vitals,
        medications, comorbidities, and pathology sections.
    """
    data = {
        "demographics": _map_demographics(patient),
        "kidney_disease": _map_kidney_disease(patient, profile),
        "laboratory_data": _map_labs(patient),
        "vital_signs": _map_vitals(patient),
        "current_medications": _map_medications(patient),
        "comorbidities": _map_comorbidities(patient),
        "pathology": _map_pathology(patient),
    }
    return data


def _map_demographics(patient) -> dict[str, Any]:
    age = None
    if patient.dob:
        today = date.today()
        age = today.year - patient.dob.year - (
            (today.month, today.day) < (patient.dob.month, patient.dob.day)
        )

    height_cm = _get_baseline_height(patient)
    weight_kg = _get_latest_weight(patient)
    bmi = None
    bsa = None
    if height_cm and weight_kg:
        try:
            h = float(height_cm)
            w = float(weight_kg)
            if h > 0:
                bmi = round(w / ((h / 100) ** 2), 1)
                bsa = round(0.007184 * (w ** 0.425) * (h ** 0.725), 2)
        except (ValueError, ZeroDivisionError):
            pass

    return {
        "age": age,
        "sex": patient.sex or None,
        "weight_kg": float(weight_kg) if weight_kg else None,
        "height_cm": float(height_cm) if height_cm else None,
        "bmi": bmi,
        "body_surface_area": bsa,
        "smoking_status": patient.smoking_status or None,
        "ethnicity": None,
        "pregnancy_status": None,
    }


def _map_kidney_disease(patient, profile=None) -> dict[str, Any]:
    ckd_stage = None
    egfr = float(patient.latest_egfr) if patient.latest_egfr else None
    if egfr is not None:
        ckd_stage = _egfr_to_ckd_stage(egfr)

    diagnosis = patient.primary_diagnosis or patient.biopsy_diagnosis or ""
    broad_group = patient.gn_broad_group or ""

    differential = []
    if profile and profile.differential:
        for d in profile.differential[:5]:
            differential.append({
                "disease_name": d.get("disease_name", ""),
                "confidence": d.get("confidence", 0),
                "disease_id": d.get("disease_id", ""),
            })

    risk = {}
    if profile and profile.risk_assessment:
        risk = profile.risk_assessment

    return {
        "primary_diagnosis": diagnosis,
        "disease_subtype": broad_group,
        "disease_phase": patient.current_phase or None,
        "biopsy_findings": _get_biopsy_summary(patient),
        "disease_duration": None,
        "ckd_stage": ckd_stage,
        "egfr": egfr,
        "aki_status": None,
        "dialysis_status": None,
        "transplant_status": patient.transplant_status or "none",
        "differential": differential,
        "risk_assessment": risk,
    }


def _map_labs(patient) -> dict[str, Any]:
    labs: dict[str, Any] = {}
    try:
        from labs.models import LabResult
        test_map = {
            "creatinine": "serum_creatinine",
            "egfr": "egfr",
            "uacr": "uacr",
            "upcr": "upcr",
            "24h_uprotein": "urine_protein_24h",
            "albumin": "serum_albumin",
            "potassium": "potassium",
            "sodium": "sodium",
            "bicarbonate": "bicarbonate",
            "calcium": "calcium",
            "phosphate": "phosphate",
            "magnesium": "magnesium",
            "hemoglobin": "hemoglobin",
            "wbc": "wbc",
            "platelets": "platelets",
            "hba1c": "hba1c",
            "glucose": "glucose",
            "crp": "crp",
            "esr": "esr",
            "alt": "alt",
            "ast": "ast",
            "bilirubin": "bilirubin",
            "ldl": "ldl",
            "hdl": "hdl",
            "triglycerides": "triglycerides",
            "complement_c3": "complement_c3",
            "complement_c4": "complement_c4",
            "ana": "ana",
            "anca": "anca",
            "anti_gbm": "anti_gbm",
            "pla2r": "pla2r",
            "anti_ds_dna": "anti_ds_dna",
        }
        for test_code, field_name in test_map.items():
            result = LabResult.series(patient, test_code).order_by(
                "-result_date"
            ).first()
            if result:
                labs[field_name] = {
                    "value": (
                        float(result.value_numeric)
                        if result.value_numeric is not None
                        else result.value_text
                    ),
                    "unit": result.unit or "",
                    "date": (
                        result.result_date.isoformat()
                        if result.result_date
                        else None
                    ),
                    "flag": result.flag or "",
                }
    except Exception:
        logger.debug("Could not map lab results for patient %s", patient.patient_id)

    return labs


def _map_vitals(patient) -> dict[str, Any]:
    vitals: dict[str, Any] = {}
    try:
        from baseline.models import BaselineAssessment
        baseline = BaselineAssessment.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
        if baseline:
            if baseline.systolic_bp:
                vitals["systolic_bp"] = baseline.systolic_bp
            if baseline.diastolic_bp:
                vitals["diastolic_bp"] = baseline.diastolic_bp
            if baseline.pulse_bpm:
                vitals["heart_rate"] = baseline.pulse_bpm
            if baseline.temperature_c:
                vitals["temperature"] = float(baseline.temperature_c)
            if baseline.weight_kg:
                vitals["weight_kg"] = float(baseline.weight_kg)
            if baseline.height_cm:
                vitals["height_cm"] = float(baseline.height_cm)
    except Exception:
        pass

    try:
        from clinical.models import VitalSign
        latest = VitalSign.objects.filter(
            encounter__patient=patient
        ).order_by("-recorded_at").first()
        if latest:
            if latest.bp_systolic and "systolic_bp" not in vitals:
                vitals["systolic_bp"] = latest.bp_systolic
            if latest.bp_diastolic and "diastolic_bp" not in vitals:
                vitals["diastolic_bp"] = latest.bp_diastolic
            if latest.heart_rate and "heart_rate" not in vitals:
                vitals["heart_rate"] = latest.heart_rate
            if latest.weight_kg and "weight_kg" not in vitals:
                vitals["weight_kg"] = float(latest.weight_kg)
            if latest.height_cm and "height_cm" not in vitals:
                vitals["height_cm"] = float(latest.height_cm)
    except Exception:
        pass

    return vitals


def _map_medications(patient) -> list[dict[str, Any]]:
    meds: list[dict[str, Any]] = []
    try:
        from treatments.models import TreatmentExposure
        exposures = TreatmentExposure.objects.filter(
            patient=patient, ongoing=True
        ).select_related("drug")
        for exp in exposures:
            meds.append({
                "medication": exp.drug_name or (
                    exp.drug.generic_name if exp.drug else ""
                ),
                "dose": exp.dose or "",
                "dose_unit": exp.dose_unit or "",
                "frequency": exp.frequency or "",
                "route": exp.route or "PO",
                "start_date": (
                    exp.start_date.isoformat() if exp.start_date else None
                ),
                "indication": "",
            })
    except Exception:
        pass
    return meds


def _map_comorbidities(patient) -> dict[str, Any]:
    comorbidities: dict[str, Any] = {
        "diabetes": patient.diabetes_status not in ("none", ""),
        "diabetes_type": patient.diabetes_status or None,
        "hypertension": patient.hypertension,
        "autoimmune_disease": patient.autoimmune_disease,
        "chronic_infection": patient.chronic_infection,
        "hepatitis": patient.hepatitis_status or None,
        "hiv": patient.hiv_status or None,
        "heart_failure": False,
        "coronary_disease": False,
        "liver_disease": False,
        "cancer": False,
        "active_infection": False,
    }
    try:
        from baseline.models import BaselineAssessment
        baseline = BaselineAssessment.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
        if baseline:
            comorbidities["heart_failure"] = getattr(
                baseline, "heart_failure", False
            )
            comorbidities["coronary_disease"] = getattr(
                baseline, "coronary_disease", False
            )
    except Exception:
        pass

    try:
        from baseline.models import BaselineAssessment
        baseline = BaselineAssessment.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
        if baseline and baseline.drug_history:
            # This field is a MEDICATION history, not an allergy list — it used
            # to be sent as "drug_allergies_note", which told the AI a patient
            # was allergic to drugs they were merely taking. Current medication
            # goes out structured under "current_medications"; this carries only
            # whatever free text legacy baselines still hold.
            comorbidities["prior_drug_history_note"] = baseline.drug_history
    except Exception:
        pass

    return comorbidities


def _map_pathology(patient) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        from pathology.models import Biopsy
        biopsy = patient.biopsies.order_by("-biopsy_date").first()
        if not biopsy:
            return result

        result["biopsy_date"] = (
            biopsy.biopsy_date.isoformat() if biopsy.biopsy_date else None
        )
        result["adequacy"] = biopsy.adequacy or None
        result["total_glomeruli"] = biopsy.total_glomeruli
        result["global_sclerosis_pct"] = (
            float(biopsy.global_sclerosis_pct)
            if biopsy.global_sclerosis_pct is not None
            else None
        )
        result["ifta_pct"] = (
            float(biopsy.ifta_pct) if biopsy.ifta_pct is not None else None
        )
        result["crescents_present"] = biopsy.crescents_present
        result["necrosis_present"] = biopsy.necrosis_present
        result["if_pattern"] = biopsy.if_pattern or None

        try:
            if hasattr(biopsy, "diagnosis") and biopsy.diagnosis:
                result["diagnosis"] = biopsy.diagnosis.diagnosis
                result["broad_group"] = biopsy.diagnosis.broad_group
        except Exception:
            pass

        try:
            if hasattr(biopsy, "igan_score") and biopsy.igan_score:
                s = biopsy.igan_score
                result["oxford_mestc"] = f"M{s.M}E{s.E}S{s.S}T{s.T}C{s.C}"
        except Exception:
            pass

        try:
            if hasattr(biopsy, "lupus") and biopsy.lupus:
                result["isn_rps_class"] = biopsy.lupus.isn_rps_class
                result["activity_index"] = biopsy.lupus.activity_index
                result["chronicity_index"] = biopsy.lupus.chronicity_index
        except Exception:
            pass

        try:
            if hasattr(biopsy, "membranous") and biopsy.membranous:
                result["pla2r_tissue"] = biopsy.membranous.pla2r_tissue
                result["mn_stage"] = biopsy.membranous.mn_stage
        except Exception:
            pass

        try:
            if hasattr(biopsy, "fsgs") and biopsy.fsgs:
                result["fsgs_variant"] = biopsy.fsgs.variant
                result["fsgs_primary_secondary"] = biopsy.fsgs.primary_secondary
        except Exception:
            pass
    except Exception:
        pass

    return result


def _get_baseline_height(patient):
    try:
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
        if b and b.height_cm:
            return b.height_cm
    except Exception:
        pass
    return None


def _get_latest_weight(patient):
    try:
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.filter(
            patient=patient
        ).order_by("-created_at").first()
        if b and b.weight_kg:
            return b.weight_kg
    except Exception:
        pass
    try:
        from clinical.models import VitalSign
        v = VitalSign.objects.filter(
            encounter__patient=patient
        ).order_by("-recorded_at").first()
        if v and v.weight_kg:
            return v.weight_kg
    except Exception:
        pass
    return None  # no weight data available


def _get_biopsy_summary(patient) -> str:
    try:
        from pathology.models import Biopsy
        biopsy = patient.biopsies.order_by("-biopsy_date").first()
        if biopsy and biopsy.notes:
            return biopsy.notes[:500]
    except Exception:
        pass
    return ""


def _egfr_to_ckd_stage(egfr: float) -> int:
    if egfr >= 90:
        return 1
    if egfr >= 60:
        return 2
    if egfr >= 45:
        return 3
    if egfr >= 30:
        return 4
    return 5

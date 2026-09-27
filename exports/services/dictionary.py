"""
Data dictionary (codebook) for the research dataset — protocol Appendix C / §11.1.

One entry per export column: type, units / allowed values, and a description, so
a de-identified dataset can be shared and used without re-deriving what each
field means. Kept in sync with services/dataset.columns().
"""
from __future__ import annotations

from .dataset import columns

# column -> (type, units_or_values, description)
_DEFS = {
    "patient_id": ("string", "Study ID", "Pseudonymous unique participant identifier"),
    "name": ("string", "", "Full name (identified export only)"),
    "phone": ("string", "", "Phone number (identified export only)"),
    "hospital_id": ("string", "", "Hospital registration / NID (identified export only)"),
    "sex": ("category", "M/F/O", "Sex"),
    "age_at_enrollment": ("integer", "years", "Age at enrolment"),
    "enrollment_date": ("date", "ISO-8601", "Date of registry enrolment"),
    "cohort": ("category", "", "Registry cohort"),
    "diabetes_status": ("category", "none/t1/t2/other", "Diabetes status"),
    "primary_diagnosis": ("string", "", "Working clinical diagnosis (clinician-owned; may differ from pathology_diagnosis)"),
    "bmi": ("float", "kg/m^2", "Body mass index (auto-computed)"),
    "bmi_category": ("category", "underweight/normal/overweight/obese", "Asian BMI category"),
    "systolic_bp": ("integer", "mmHg", "Baseline systolic BP"),
    "diastolic_bp": ("integer", "mmHg", "Baseline diastolic BP"),
    "hba1c": ("float", "%", "Baseline HbA1c: the linked baseline lab result, else the nearest result within -90/+30 days of the baseline date, else the legacy baseline field"),
    "hba1c_date": ("date", "ISO-8601", "Date of the HbA1c value reported"),
    "hba1c_source": ("category", "linked/window/legacy_field", "Where the baseline HbA1c came from"),
    "dm_duration_years": ("float", "years", "Diabetes duration"),
    "presentation_syndrome": ("category", "nephrotic/nephritic/rpgn/...", "Clinical presentation"),
    "diabetic_retinopathy": ("boolean", "0/1", "Diabetic retinopathy present"),
    "cvd_history": ("boolean", "0/1", "Cardiovascular disease history"),
    "alcohol_use": ("category", "never/former/current", "Alcohol use"),
    "previous_kidney_disease": ("boolean", "0/1", "Previous kidney disease"),
    "autoimmune_disease": ("boolean", "0/1", "Autoimmune disease"),
    "chronic_infection": ("boolean", "0/1", "Chronic infection (HBV/HCV/HIV/TB)"),
    "malignancy": ("boolean", "0/1", "Malignancy history"),
    "prior_immunosuppression": ("boolean", "0/1", "Previous immunosuppressive therapy"),
    "pulse_bpm": ("integer", "bpm", "Pulse rate"),
    "respiratory_rate": ("integer", "/min", "Respiratory rate"),
    "temperature_c": ("float", "°C", "Temperature"),
    "volume_status": ("category", "euvolemic/hypervolemic/hypovolemic", "Volume status"),
    "presenting_syndromes": ("string", ";-joined", "Presenting syndrome(s), multi-select"),
    "presenting_symptoms": ("string", ";-joined", "Presenting symptom(s), multi-select"),
    "comorbidity_snapshot_source": ("category", "enrollment/legacy_mirror/correction", "Provenance of the baseline comorbidity columns (enrollment snapshot; legacy_mirror = pre-2026-09-27 values copied from the patient record)"),
    "pathology_diagnosis": ("string", "", "Diagnosis of the selected biopsy (final review preferred)"),
    "pathology_biopsy_date": ("date", "ISO-8601", "Date of the biopsy all pathology columns come from"),
    "pathology_state": ("category", "final/provisional", "final = reviewed; provisional = local read pending central review"),
    "baseline_creatinine": ("float", "mg/dL", "Baseline serum creatinine"),
    "baseline_egfr": ("float", "mL/min/1.73m^2", "Baseline eGFR (CKD-EPI 2021)"),
    "baseline_upcr": ("float", "g/day-equiv", "Baseline proteinuria (24-h UTP preferred)"),
    "baseline_albumin": ("float", "g/dL", "Baseline serum albumin"),
    "baseline_hemoglobin": ("float", "g/dL", "Baseline haemoglobin"),
    "baseline_c3": ("float", "mg/dL", "Baseline complement C3"),
    "baseline_c4": ("float", "mg/dL", "Baseline complement C4"),
    "baseline_anti_pla2r": ("float", "RU/mL", "Baseline anti-PLA2R titre"),
    "broad_group": ("string", "", "GN broad group of the selected biopsy"),
    "mest_m": ("ordinal", "0/1", "Oxford MEST-C: mesangial hypercellularity"),
    "mest_e": ("ordinal", "0/1", "Oxford MEST-C: endocapillary hypercellularity"),
    "mest_s": ("ordinal", "0/1", "Oxford MEST-C: segmental sclerosis"),
    "mest_t": ("ordinal", "0/1/2", "Oxford MEST-C: tubular atrophy/interstitial fibrosis"),
    "mest_c": ("ordinal", "0/1/2", "Oxford MEST-C: crescents"),
    "isn_rps_class": ("category", "I-VI", "Lupus nephritis ISN/RPS class"),
    "fsgs_variant": ("category", "nos/perihilar/cellular/tip/collapsing", "FSGS variant"),
    "review_status": ("category", "pending/.../adjudicated", "Central pathology review status"),
    "followup_days": ("integer", "days", "Follow-up duration from index"),
    "latest_egfr": ("float", "mL/min/1.73m^2", "Most recent eGFR"),
    "egfr_slope": ("float", "mL/min/1.73m^2/yr", "Annualised eGFR slope"),
    "remission_status": ("category", "none/partial/complete", "Best sustained proteinuria remission"),
    "complete_remission": ("boolean", "0/1", "Sustained complete remission achieved"),
    "time_to_complete_remission_days": ("integer", "days", "Index to complete remission"),
    "sustained_50_decline": ("boolean", "0/1", "Sustained >=50% eGFR decline"),
    "eskd": ("boolean", "0/1", "Kidney failure (dialysis/transplant or eGFR<15)"),
    "death": ("boolean", "0/1", "Death"),
    "composite_kidney_event": ("boolean", "0/1", "ESKD / >=50% eGFR decline / renal death"),
    "composite_date": ("date", "ISO-8601", "Date of composite kidney event"),
    "pla2r_baseline": ("float", "RU/mL", "Baseline anti-PLA2R (kinetics)"),
    "pla2r_pct_decline": ("float", "%", "Best anti-PLA2R % decline from baseline"),
    "pla2r_50pct_decline": ("boolean", "0/1", "Reached >=50% anti-PLA2R decline"),
    "pla2r_immunological_remission": ("boolean", "0/1", "Anti-PLA2R seroconversion to negative"),
    "c3_recovered": ("boolean", "0/1", "C3 normalisation"),
    "n_adverse_events": ("integer", "count", "Total adverse events"),
    "n_serious_ae": ("integer", "count", "Serious adverse events"),
    "n_infections": ("integer", "count", "Infection adverse events"),
}
# Drug-exposure flags share a pattern.
for _name in ("ever_raasi", "ever_sglt2i", "ever_finerenone", "ever_hcq",
              "ever_steroid", "ever_mmf", "ever_rituximab", "ever_cni",
              "ever_cyclophosphamide", "ever_azathioprine", "ever_budesonide"):
    _DEFS[_name] = ("boolean", "0/1", f"Ever exposed to {_name[5:]} drug class")

# Time-to-event + additional efficacy outcomes (protocol study endpoints).
_DEFS.update({
    "partial_remission": ("boolean", "0/1", "Sustained partial proteinuria remission achieved"),
    "time_to_partial_remission_days": ("integer", "days", "Index to partial remission"),
    "igan_proteinuria_response": ("boolean", "0/1", "IgAN proteinuria response (>=30% reduction or <0.3 g/day)"),
    "time_to_igan_response_days": ("integer", "days", "Index to IgAN proteinuria response"),
    "sustained_40_decline": ("boolean", "0/1", "Sustained >=40% eGFR decline (KDIGO surrogate)"),
    "doubling_creatinine": ("boolean", "0/1", "Doubling of serum creatinine"),
    "time_to_eskd_days": ("integer", "days", "Index to kidney failure / KRT"),
    "time_to_death_days": ("integer", "days", "Index to death"),
    "time_to_composite_days": ("integer", "days", "Index to composite kidney event"),
    "n_relapses": ("integer", "count", "Number of documented relapse episodes"),
    "time_to_first_relapse_days": ("integer", "days", "Index to first relapse"),
})

# Definitions for the per-study export columns (appended when ?study=<CODE>).
_STUDY_DEFS = {
    "study_code": ("category", "", "Embedded study the patient is enrolled in"),
    "arm": ("category", "", "Randomized treatment arm (ITT)"),
    "stratum": ("category", "", "Randomization stratum"),
    "enrolled_date": ("date", "ISO-8601", "Date enrolled into the study"),
    "itt": ("boolean", "0/1", "In the intention-to-treat set"),
}
_DEFS.update(_STUDY_DEFS)
STUDY_COLUMNS = list(_STUDY_DEFS.keys())

DICTIONARY_COLUMNS = ["column", "type", "units_or_values", "description"]


def data_dictionary(identified=False):
    """List of dict rows describing each export column, in dataset column order."""
    out = []
    for col in columns(identified):
        t, u, d = _DEFS.get(col, ("", "", ""))
        out.append({"column": col, "type": t, "units_or_values": u, "description": d})
    return out


def column_defs(identified=False, study=False):
    """Map column -> (type, units_or_values, description), in dataset order.

    Used by the SPSS .sav writer to set variable labels, measurement levels and
    value labels from the same single source of truth as the codebook. When
    ``study`` is true the per-study columns (arm, stratum, …) are included."""
    cols = list(columns(identified)) + (STUDY_COLUMNS if study else [])
    return {col: _DEFS.get(col, ("", "", "")) for col in cols}


# Codebook for the repeated-findings child table (build_findings_table).
FINDING_DEFS = {
    "patient_id": ("string", "Study ID", "Join key to the patient-level dataset"),
    "biopsy_id": ("integer", "", "Biopsy (procedure/specimen) identifier"),
    "biopsy_date": ("date", "ISO-8601", "Biopsy date"),
    "is_pathology_source": ("boolean", "0/1", "This biopsy feeds the patient-level pathology columns"),
    "report_id": ("integer", "", "Report revision identifier"),
    "report_role": ("category", "local/central/adjudication", "Which read"),
    "report_revision": ("integer", "", "Revision number within the read (amendments/addenda)"),
    "report_status": ("category", "draft/pending/preliminary/final/inadequate", "Report state"),
    "report_is_current": ("boolean", "0/1", "Current revision (0 = superseded, kept for history)"),
    "report_origin": ("category", "guided/amendment/addendum/api/admin/legacy", "How the revision was entered"),
    "finding_id": ("integer", "", "Finding identifier"),
    "section": ("category", "lm_glomerular/tubulointerstitial/vascular/if_marker/if_interpretation/em/special_stain", "Report section"),
    "code": ("category", "pathology.findings vocabulary", "Coded finding ('marker' for IF/IHC rows, 'other' + description)"),
    "finding": ("string", "", "Readable finding label"),
    "presence": ("category", "present/absent/indeterminate", "Observed presence"),
    "severity": ("category", "minimal/mild/moderate/severe", "Severity, when reported"),
    "extent": ("category", "focal/diffuse/segmental/global", "Extent, when reported"),
    "extent_pct": ("float", "%", "Extent as reported (0-100)"),
    "count": ("integer", "count", "Count, when reported"),
    "denominator": ("integer", "count", "Denominator of count (e.g. glomeruli examined)"),
    "site": ("category", "", "Site / compartment"),
    "marker": ("category", "IgG/IgA/IgM/C3/C1q/kappa/lambda/fibrinogen/...", "IF/IHC marker"),
    "intensity": ("category", "0/trace/1+/2+/3+", "IF intensity"),
    "distribution": ("category", "granular/linear/pseudolinear/smudgy", "IF distribution"),
    "detail": ("string", "", "Free-text elaboration"),
    "finding_origin": ("category", "entered/legacy", "legacy = converted from an old single-choice field"),
    "legacy_value": ("string", "", "Original legacy value, when converted"),
}


def findings_dictionary():
    from .dataset import FINDING_COLUMNS
    return [{"column": c, "type": FINDING_DEFS[c][0], "units_or_values": FINDING_DEFS[c][1],
             "description": FINDING_DEFS[c][2]} for c in FINDING_COLUMNS]

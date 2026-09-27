"""
The research dataset — one denormalized row per patient, assembled from every
domain (baseline, labs, pathology, treatment exposure, outcomes, biomarkers,
safety). This is the portfolio's "PatientResearchDataset": the ML/analysis-ready
table that lets you find structured outcomes without re-abstracting charts.

De-identified by default (Study ID only, no name/phone/hospital reg), per
§13.5 / §11.5. Identified export is gated to data managers in the view.

Columns are declared once, in research-logical order, so the export is stable
and self-documenting.
"""
from __future__ import annotations

import datetime as dt

from analytics.models import PatientOutcome
from biomarkers.models import BiomarkerKinetics
from pathology.models import GNDiagnosis
from safety.models import AdverseEvent
from treatments.models import DrugClass, TreatmentExposure

# Direct-identifier columns, only included when identified=True.
IDENTIFIER_COLUMNS = ["name", "phone", "hospital_id"]

# Drug-exposure flag columns -> drug_class. These cover every arm/comparator of
# the embedded protocol studies (CNI/cyclophosphamide/azathioprine were added so
# the tacrolimus and CNI arms of MN-RTX-CNI / FSGS-STEROID-CNI have an exposure
# variable, and budesonide is flagged separately from systemic steroid).
EXPOSURE_FLAGS = [
    ("ever_raasi", DrugClass.RAASI), ("ever_sglt2i", DrugClass.SGLT2I),
    ("ever_finerenone", DrugClass.FINERENONE), ("ever_hcq", DrugClass.HCQ),
    ("ever_steroid", DrugClass.STEROID), ("ever_mmf", DrugClass.MMF),
    ("ever_rituximab", DrugClass.RITUXIMAB), ("ever_cni", DrugClass.CNI),
    ("ever_cyclophosphamide", DrugClass.CYCLOPHOSPHAMIDE),
    ("ever_azathioprine", DrugClass.AZATHIOPRINE),
]

COLUMNS = (
    # Identity / demographics
    ["patient_id", "sex", "age_at_enrollment", "enrollment_date", "cohort",
     "diabetes_status", "primary_diagnosis"]
    # Baseline clinical
    + ["bmi", "bmi_category", "systolic_bp", "diastolic_bp", "hba1c",
       "dm_duration_years", "presentation_syndrome", "diabetic_retinopathy",
       "cvd_history",
       # Baseline A–E expansion
       "alcohol_use", "previous_kidney_disease", "autoimmune_disease",
       "chronic_infection", "malignancy", "prior_immunosuppression",
       "pulse_bpm", "respiratory_rate", "temperature_c", "volume_status",
       "presenting_syndromes", "presenting_symptoms"]
    # Baseline labs
    + ["baseline_creatinine", "baseline_egfr", "baseline_upcr", "baseline_albumin",
       "baseline_hemoglobin", "baseline_c3", "baseline_c4", "baseline_anti_pla2r"]
    # Pathology
    + ["broad_group", "mest_m", "mest_e", "mest_s", "mest_t", "mest_c",
       "isn_rps_class", "fsgs_variant", "review_status"]
    # Treatment exposure flags
    + [name for name, _ in EXPOSURE_FLAGS] + ["ever_budesonide"]
    # Outcomes (each event carries a time-to-event in days for survival analysis)
    + ["followup_days", "latest_egfr", "egfr_slope", "remission_status",
       "complete_remission", "time_to_complete_remission_days",
       "partial_remission", "time_to_partial_remission_days",
       "igan_proteinuria_response", "time_to_igan_response_days",
       "sustained_40_decline", "sustained_50_decline", "doubling_creatinine",
       "eskd", "time_to_eskd_days", "death", "time_to_death_days",
       "composite_kidney_event", "composite_date", "time_to_composite_days",
       "n_relapses", "time_to_first_relapse_days"]
    # Biomarkers
    + ["pla2r_baseline", "pla2r_pct_decline", "pla2r_50pct_decline",
       "pla2r_immunological_remission", "c3_recovered"]
    # Safety
    + ["n_adverse_events", "n_serious_ae", "n_infections"]
)


def columns(identified=False):
    return (IDENTIFIER_COLUMNS + COLUMNS) if identified else COLUMNS


def _age(dob, ref):
    if not dob or not ref:
        return None
    return ref.year - dob.year - ((ref.month, ref.day) < (dob.month, dob.day))


def _latest_lab(patient, code):
    from labs.models import LabResult
    s = LabResult.series(patient, code)
    first = s.first()
    return float(first.value_numeric) if first and first.value_numeric is not None else None


def build_row(patient, *, identified=False):
    row = {"patient_id": patient.patient_id, "sex": patient.sex,
           "age_at_enrollment": _age(patient.dob, patient.enrollment_date),
           "enrollment_date": patient.enrollment_date, "cohort": patient.cohort,
           "diabetes_status": patient.diabetes_status,
           "primary_diagnosis": patient.primary_diagnosis}
    if identified:
        row.update(name=patient.name, phone=patient.phone, hospital_id=patient.hospital_id)

    base = getattr(patient, "baseline", None)
    if base:
        row.update(bmi=base.bmi, bmi_category=base.bmi_category,
                   systolic_bp=base.systolic_bp, diastolic_bp=base.diastolic_bp,
                   hba1c=base.hba1c, dm_duration_years=base.dm_duration_years,
                   presentation_syndrome=base.presentation_syndrome,
                   diabetic_retinopathy=base.diabetic_retinopathy,
                   cvd_history=base.cvd_history,
                   alcohol_use=base.alcohol_use,
                   previous_kidney_disease=base.previous_kidney_disease,
                   autoimmune_disease=base.autoimmune_disease,
                   chronic_infection=base.chronic_infection,
                   malignancy=base.malignancy,
                   prior_immunosuppression=base.prior_immunosuppression,
                   pulse_bpm=base.pulse_bpm, respiratory_rate=base.respiratory_rate,
                   temperature_c=base.temperature_c, volume_status=base.volume_status,
                   presenting_syndromes=";".join(base.presentation_syndromes or []),
                   presenting_symptoms=";".join(base.presenting_symptoms or []))

    row.update(baseline_albumin=_latest_lab(patient, "albumin"),
               baseline_hemoglobin=_latest_lab(patient, "hemoglobin"),
               baseline_c3=_latest_lab(patient, "c3"),
               baseline_c4=_latest_lab(patient, "c4"),
               baseline_anti_pla2r=_latest_lab(patient, "anti_pla2r"))

    # Pathology: latest biopsy diagnosis + MEST-C.
    gd = (GNDiagnosis.objects.filter(biopsy__patient=patient)
          .select_related("biopsy").order_by("-biopsy__biopsy_date").first())
    if gd:
        b = gd.biopsy
        row.update(broad_group=gd.broad_group, review_status=b.review_status)
        ig = getattr(b, "igan_score", None)
        if ig:
            row.update(mest_m=ig.M, mest_e=ig.E, mest_s=ig.S, mest_t=ig.T, mest_c=ig.C)
        ln = getattr(b, "lupus", None)
        if ln:
            row["isn_rps_class"] = ln.isn_rps_class
        fs = getattr(b, "fsgs", None)
        if fs:
            row["fsgs_variant"] = fs.variant

    exposures = list(TreatmentExposure.objects.filter(patient=patient)
                     .values_list("drug__drug_class", "drug__generic_name"))
    exposed = {cls for cls, _ in exposures}
    for name, cls in EXPOSURE_FLAGS:
        row[name] = cls in exposed
    # Budesonide is stored under the STEROID class; flag it separately so the
    # IGAN-BUDESONIDE intervention arm is distinguishable from systemic steroid.
    row["ever_budesonide"] = any("budesonide" in (g or "").lower()
                                 for _, g in exposures)

    o = getattr(patient, "outcome", None) or PatientOutcome.objects.filter(patient=patient).first()
    if o:
        def _tt(d):  # days from index date to an event date (None-safe)
            return (d - o.index_date).days if (d and o.index_date) else None
        n_relapses = patient.relapses.count()
        first_relapse = (patient.relapses.order_by("relapse_date").first())
        row.update(followup_days=o.followup_days, latest_egfr=o.latest_egfr,
                   egfr_slope=o.egfr_slope, remission_status=o.remission_status,
                   complete_remission=o.complete_remission,
                   time_to_complete_remission_days=_tt(o.complete_remission_date),
                   partial_remission=o.partial_remission,
                   time_to_partial_remission_days=_tt(o.partial_remission_date),
                   igan_proteinuria_response=o.igan_proteinuria_response,
                   time_to_igan_response_days=_tt(o.igan_proteinuria_response_date),
                   sustained_40_decline=o.sustained_40_decline,
                   sustained_50_decline=o.sustained_50_decline,
                   doubling_creatinine=bool(o.doubling_date),
                   eskd=o.eskd, time_to_eskd_days=_tt(o.eskd_date),
                   death=o.death, time_to_death_days=_tt(o.death_date),
                   composite_kidney_event=o.composite_kidney_event,
                   composite_date=o.composite_date,
                   time_to_composite_days=_tt(o.composite_date),
                   n_relapses=n_relapses,
                   time_to_first_relapse_days=_tt(first_relapse.relapse_date) if first_relapse else None,
                   baseline_creatinine=o.baseline_creatinine,
                   baseline_egfr=o.baseline_egfr, baseline_upcr=o.baseline_upcr)

    bk = getattr(patient, "biomarker_kinetics", None) or \
        BiomarkerKinetics.objects.filter(patient=patient).first()
    if bk:
        row.update(pla2r_baseline=bk.pla2r_baseline, pla2r_pct_decline=bk.pla2r_pct_decline,
                   pla2r_50pct_decline=bk.pla2r_50pct_decline,
                   pla2r_immunological_remission=bk.pla2r_immunological_remission,
                   c3_recovered=bk.c3_recovered)

    aes = AdverseEvent.objects.filter(patient=patient)
    row.update(n_adverse_events=aes.count(),
               n_serious_ae=aes.filter(serious=True).count(),
               n_infections=aes.filter(category=AdverseEvent.Category.INFECTION).count())
    return row


# Extra columns appended when exporting for a specific embedded study, so the
# data can be analysed by treatment arm (ITT) directly in SPSS/R.
STUDY_COLUMNS = ["study_code", "arm", "stratum", "enrolled_date", "itt"]


def build_dataset(queryset, *, identified=False, study=None):
    """Return (columns, rows) for the research dataset.

    When ``study`` (a Study.code) is given, the dataset is restricted to that
    study's ENROLLED patients and gains the STUDY_COLUMNS — most importantly the
    randomized ``arm`` — so a per-study, arm-vs-arm analysis works from the file.
    """
    cols = columns(identified)
    enrol_by_patient = {}
    if study:
        from studies.models import StudyEnrollment
        cols = cols + STUDY_COLUMNS
        enrol_by_patient = {
            e.patient_id: e for e in
            StudyEnrollment.objects
            .filter(study__code=study, status=StudyEnrollment.Status.ENROLLED)
            .select_related("arm")}
        queryset = queryset.filter(pk__in=list(enrol_by_patient.keys()))

    rows = []
    for p in queryset:
        row = build_row(p, identified=identified)
        if study:
            e = enrol_by_patient.get(p.pk)
            row.update(
                study_code=study,
                arm=(e.arm.code if e and e.arm else None),
                stratum=(e.stratum if e else None),
                enrolled_date=(e.enrolled_date if e else None),
                itt=bool(e))
        rows.append(row)
    return cols, rows

# Data Quality Audit
## GDES Version 5.0 — Workstream 8

**Date:** 2026-07-11
**Status:** Complete

---

## Audit Methodology

Each data quality dimension was evaluated against production readiness standards for a clinical registry and research platform.

---

## 1. Missing Values

| Field/Model | Prevention | Enforcement | Quality |
|------------|-----------|-------------|---------|
| `Patient.patient_id` | Auto-generated | NOT NULL | ✅ Guaranteed |
| `Patient.name` | Form validation | NOT NULL | ✅ |
| `Patient.sex` | Form validation (M/F/Other) | NOT NULL | ✅ |
| `Patient.dob` | Form validation | NOT NULL | ✅ |
| `Patient.enrollment_date` | Auto-set | NOT NULL | ✅ |
| `Patient.primary_diagnosis` | Biopsy-driven | Nullable | ⚠️ May be empty until biopsy |
| `Patient.latest_egfr` | Auto-derived | Nullable | ⚠️ May be null until first lab |
| `Patient.current_phase` | Auto-set by state machine | Nullable | ⚠️ May be null if never assessed |
| `ClinicalAssessment` fields | Form validation | Most nullable | ⚠️ Baseline forms have many optional fields |
| `Biopsy.biopsy_date` | Form validation | NOT NULL | ✅ |
| `Biopsy.histological_diagnosis` | Form validation | NOT NULL | ✅ |
| `LabResult.value` | Form validation | NOT NULL | ✅ |
| `PrescriptionItem` fields | JS validation | NOT NULL | ✅ |
| `TreatmentExposure` fields | Auto-derived | Most NOT NULL | ✅ |
| `ClinicalProfile.features_snapshot` | Auto-derived | Auto-set | ✅ |
| `ClinicalProfile.differential` | Auto-derived | Auto-set | ✅ |

**Key finding**: Core registry fields (patient identity, demographics) are well-enforced. Clinical data has more optionality, which is appropriate for real-world clinical practice where not all data is available at registration.

---

## 2. Duplicate Patients

| Check | Status | Detail |
|-------|--------|--------|
| Duplicate check at registration | ✅ | `_dupcheck.html` HTMX partial checks name + phone + hospital_no live |
| Unique constraint on `patient_id` | ✅ | Auto-generated, unique |
| Unique constraint on `hospital_no` | ✅ | Unique if provided |
| Duplicate detection for existing patients | ✅ | `dupcheck` view checks across all patients |
| **✅ Verdict** | Duplicate prevention is robust at registration. No known duplicate routes. |

---

## 3. Duplicate Encounters

| Check | Status | Detail |
|-------|--------|--------|
| Unique constraint on encounter | ❌ | No uniqueness constraint on `(patient, encounter_date, encounter_type)` |
| **⚠️ Issue** | A clinician could theoretically enter two follow-up visits for the same patient on the same date. The carry-forward feature in the follow-up form reduces this risk but does not prevent it. |
| **Priority** | Low |

---

## 4. Conflicting Diagnoses

| Check | Status | Detail |
|-------|--------|--------|
| Single primary diagnosis | ✅ | `Patient.primary_diagnosis` is a single CharField |
| Biopsy diagnosis versioning | ✅ | Central review tracks concordance/discordance |
| Multiple biopsies reconciled | ✅ | `apply_biopsy()` updates diagnosis on each positive biopsy |
| **⚠️ Issue** | The system assumes sequential diagnosis refinement (local → central review adjudication). It does not track multiple concurrent diagnoses (e.g., IgAN + DKD in the same patient). Comorbid GN patterns are not modeled. |
| **Priority** | Low |

---

## 5. Invalid Laboratory Values

| Check | Status | Detail |
|-------|--------|--------|
| eGFR range validation | ✅ | Auto-derived from creatinine via CKD-EPI 2021 formula. Out-of-range values produce NaN rather than invalid eGFR. |
| Proteinuria validation | ✅ | 0-30 g/day range expected |
| C3/C4 normal ranges | ⚠️ | Stored as qualitative (Low/Normal) rather than quantitative + reference range |
| **✅ Verdict** | Lab range validation is adequate. |
| **⚠️ Issue** | Serology results (C3, C4, anti-PLA2R, ANA, dsDNA, ANCA) are stored as paired numeric + qualitative fields. The reference ranges are not stored, making longitudinal comparison across laboratories unreliable. |
| **Priority** | Medium |

---

## 6. Broken Relationships

| Relationship | Enforcement | Quality |
|-------------|-------------|---------|
| Patient → Encounters | FK with CASCADE | ✅ |
| Patient → ClinicalProfile | OneToOneField | ✅ |
| Patient → LabResult | FK with CASCADE | ✅ |
| Patient → Biopsy | FK with CASCADE | ✅ |
| Patient → Prescription | FK with CASCADE | ✅ |
| Patient → TreatmentExposure | FK with CASCADE | ✅ |
| Patient → ScheduledVisit | FK with CASCADE | ✅ |
| Patient → AdverseEvent | FK with CASCADE | ✅ |
| Patient → StudyEnrollment | FK with CASCADE | ✅ |
| Biopsy → GNDiagnosis | FK | ✅ |
| Biopsy → Disease-specific scores | FK | ✅ |
| Prescription → PrescriptionItem | FK | ✅ |
| **✅ Verdict** | All foreign key relationships are enforced at the database level. No orphan records possible. |

---

## 7. Incomplete Follow-up

| Check | Status | Detail |
|-------|--------|--------|
| Overdue visit detection | ✅ | 180-day window for stable patients |
| Missing eGFR detection | ✅ | `patients_missing_egfr_queryset()` |
| Missing biopsy detection | ✅ | `patients_missing_biopsy_queryset()` |
| Active without treatment detection | ✅ | `_check_treatment_gaps()` |
| **✅ Verdict** | Follow-up completeness tracking is implemented. Missing data is detectable and reported on the quality page. |

---

## 8. Incomplete Pathology

| Check | Status | Detail |
|-------|--------|--------|
| Missing biopsy detection | ✅ | Per-patient and cohort-wide |
| Missing central review | ✅ | Central review status tracked (pending/concordant/discordant/adjudicated) |
| Missing immunohistochemistry | ❌ | No field for IHC results (IgG, IgA, IgM, C3, C1q, kappa, lambda) |
| Missing electron microscopy | ❌ | No field for EM findings (deposits, podocyte foot process effacement) |
| **⚠️ Issue** | The `Biopsy` model captures histological diagnosis and disease-specific scores but does not have structured fields for immunohistochemistry findings or electron microscopy details. These are likely captured in unstructured clinical notes or external pathology reports. |
| **Priority** | Medium |

---

## 9. Data Completeness Metrics (Computed)

| Metric | Status | How to Access |
|--------|--------|--------------|
| Total patients | ✅ | Dashboard overview |
| Patients with eGFR | ✅ | Quality page |
| Patients with biopsy | ✅ | Quality page |
| Active without treatment % | ✅ | Quality page |
| Overdue visits % | ✅ | Dashboard worklist |
| Phase distribution | ✅ | Quality page |
| Relapse rate per 100 patient-years | ✅ | Quality page |
| Remission concordance (clinician vs. lab) | ✅ | Quality page (Cohen's kappa) |
| Biopsy yield by indication | ✅ | Quality page |

**✅ Verdict**: Data quality metrics are comprehensive and accessible.

---

## 10. Quality-Limitng Issues

| Issue | Impact | Priority |
|-------|--------|----------|
| Serology reference ranges not stored | Cross-laboratory comparison unreliable | Medium |
| Immunohistochemistry fields missing | Incomplete pathology data model | Medium |
| Electron microscopy fields missing | Incomplete pathology data model | Medium |
| Duplicate encounters possible on same date | Minor data quality issue | Low |
| Concurrent diagnoses not modeled | Comorbid GN patterns not tracked | Low |

**Overall data quality rating: GOOD (clinical-grade).** Core registry data is well-structured and validated. Pathology data model has gaps in structured IHC/EM fields, which may require external system integration for complete data.

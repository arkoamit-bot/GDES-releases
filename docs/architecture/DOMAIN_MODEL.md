# BGDDR — Domain Model

## Entity-Relationship Overview

```
Patient (1) ────── (1) BaselineAssessment
    │
    ├── (N) ClinicalEncounter
    │       ├── (N) LabOrder ──── (N) LabOrderItem ──── (N) LabResult
    │       ├── (N) Prescription ── (N) PrescriptionItem
    │       ├── (N) ClinicalEvent
    │       ├── (N) RelapseEpisode
    │       ├── (N) AdverseEvent
    │       └── (1) ClinicalAssessment
    │               └── (N) VitalSign
    │
    ├── (N) Biopsy
    │       ├── (1) GNDiagnosis
    │       ├── (1) IgANScore
    │       ├── (1) LupusPathology
    │       ├── (1) FSGSPathology
    │       ├── (1) MembranousPathology
    │       ├── (N) BiopsyImage
    │       └── (N) PathologyReview
    │
    ├── (N) TreatmentExposure ──── DrugMaster
    ├── (N) LabResult ──── LabTest
    ├── (N) Admission
    ├── (N) ScheduledVisit
    ├── (N) StudyEnrollment ──── Study ──── StudyArm
    ├── (N) AuditLog
    ├── (N) Consent
    │
    ├── (1) PatientOutcome [computed]
    ├── (1) BiomarkerKinetics [computed]
    │
    ├── (N) DecisionRequest ──── (1) DecisionResult
    └── (N) TimelineEvent
```

---

## Models by App

### patients

#### Patient
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient_id` | CharField(32) | unique, blank | Auto-generated BGD-NNNNN |
| `hospital_id` | CharField(64) | blank, indexed | Hospital registration number |
| `name` | CharField(200) | required | Patient full name |
| `phone` | CharField(32) | blank, indexed | Contact number |
| `sex` | CharField(1) | choices: M/F/O | Biological sex |
| `dob` | DateField | null, blank | Date of birth |
| `enrollment_date` | DateField | null, blank | Registry enrollment date |
| `cohort` | CharField(32) | blank, choices | PATIENT_CATEGORY |
| `diabetes_status` | CharField(8) | choices | none/t1/t2/other |
| `primary_diagnosis` | CharField(120) | blank, choices | SPECIFIC_GN_DIAGNOSIS |
| `latest_egfr` | DecimalField(5,1) | null, blank | Cached from labs |
| `registration_status` | CharField(16) | choices, indexed | suspected/registered/not_registered/excluded |
| `registration_date` | DateField | null, blank | When registered |
| `current_phase` | CharField(16) | choices, blank, indexed | active/remission/post_remission/relapse |
| `created_at` | DateTimeField | auto_now_add | |
| `updated_at` | DateTimeField | auto_now | |

---

### encounters

#### ClinicalEncounter
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | PROTECT, indexed | |
| `encounter_date` | DateField | required | |
| `encounter_type` | CharField(16) | choices | baseline/followup/unscheduled |
| `seen_by` | FK(User) | PROTECT, null | Clinician |
| `clinic_location` | CharField(120) | blank | |
| `systolic_bp` | PositiveSmallInt | null | mmHg |
| `diastolic_bp` | PositiveSmallInt | null | mmHg |
| `weight_kg` | DecimalField(5,1) | null | |
| `edema_grade` | PositiveSmallInt | null | 0-4 |
| `symptoms` | CharField(240) | blank | Free text |
| `clinician_response` | CharField(16) | choices | not_assessed/complete/partial/none/stable |
| `disease_phase` | CharField(16) | choices, blank | Per-visit phase |
| `treatment_adjusted` | BooleanField | default=False | |
| `advice` | TextField | blank | |
| `next_due_date` | DateField | null | |
| `created_at` | DateTimeField | auto_now_add | |

#### Admission
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `admit_date` | DateField | required | |
| `discharge_date` | DateField | null | |
| `ward` | CharField(80) | blank | |
| `reason` | CharField(240) | blank | |
| `biopsy` | FK(Biopsy) | SET_NULL, null | |
| `baseline_captured` | BooleanField | default=False | |
| `discharge_advice` | TextField | blank | |

#### RelapseEpisode
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `encounter` | FK(ClinicalEncounter) | SET_NULL, null | |
| `relapse_date` | DateField | required | |
| `relapse_type` | CharField(16) | choices | proteinuric/nephrotic/nephritic/functional/serologic |
| `criteria` | CharField(240) | blank | |
| `action_taken` | CharField(240) | blank | |

#### ClinicalEvent
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `event_type` | CharField(20) | choices | eskd/dialysis_start/transplant/death/complete_remission/partial_remission/relapse/major_cv |
| `event_date` | DateField | required | |
| `encounter` | FK(ClinicalEncounter) | SET_NULL, null | |
| `notes` | CharField(240) | blank | |

---

### baseline

#### BaselineAssessment
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | OneToOne(Patient) | CASCADE | |
| `assessment_date` | DateField | null | |
| `division_residence` | CharField(60) | blank | Bangladesh division |
| `socioeconomic_status` | CharField(30) | blank | Low/Middle/High |
| `monthly_income_bdt` | PositiveInt | null | BDT |
| `education` | CharField(40) | blank | |
| `occupation` | CharField(60) | blank | |
| `smoking` | CharField(20) | blank | Never/Current/Former |
| `alcohol_use` | CharField(10) | blank | never/former/current |
| `previous_kidney_disease` | BooleanField | default=False | |
| `autoimmune_disease` | BooleanField | default=False | |
| `chronic_infection` | BooleanField | default=False | |
| `malignancy` | BooleanField | default=False | |
| `prior_immunosuppression` | BooleanField | default=False | |
| `drug_history` | TextField | blank | |
| `height_cm` | DecimalField(5,1) | null | |
| `weight_kg` | DecimalField(5,1) | null | |
| `bmi` | DecimalField(4,1) | null, computed | Auto-derived |
| `bmi_category` | CharField(12) | blank, computed | WHO Asian cut-offs |
| `systolic_bp` | PositiveSmallInt | null | |
| `diastolic_bp` | PositiveSmallInt | null | |
| `dm_duration_years` | DecimalField(4,1) | null | |
| `hba1c` | DecimalField(4,1) | null | |
| `diabetic_retinopathy` | BooleanField | default=False | |
| `neuropathy` | BooleanField | default=False | |
| `diabetic_foot_history` | BooleanField | default=False | |
| `hypertension` | BooleanField | default=False | |
| `cvd_history` | BooleanField | default=False | |
| `presentation_syndrome` | CharField(14) | blank | Legacy single-select |
| `presentation_syndromes` | JSONField | default=list | Multi-select |
| `presenting_symptoms` | JSONField | default=list | Multi-select |
| `oedema_grade` | PositiveSmallInt | null | 0-4 |
| `active_urinary_sediment` | BooleanField | default=False | |
| `rbc_casts` | BooleanField | default=False | |
| `family_history_kidney` | BooleanField | default=False | |
| `pulse_bpm` | PositiveSmallInt | null | |
| `temperature_c` | DecimalField(3,1) | null | |
| `respiratory_rate` | PositiveSmallInt | null | |
| `volume_status` | CharField(12) | blank | euvolemic/hypervolemic/hypovolemic |
| `skin_findings` | CharField(200) | blank | |
| `joint_findings` | CharField(200) | blank | |
| `fundoscopy` | CharField(200) | blank | |
| `notes` | TextField | blank | |

---

### labs

#### LabTest
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `code` | SlugField(40) | unique | e.g. "creatinine" |
| `name` | CharField(120) | required | |
| `loinc` | CharField(20) | blank | LOINC code |
| `default_unit` | CharField(20) | blank | |
| `value_type` | CharField(12) | choices | numeric/qualitative |
| `ref_low` | DecimalField(10,3) | null | |
| `ref_high` | DecimalField(10,3) | null | |
| `is_derived` | BooleanField | default=False | eGFR computed, not entered |
| `is_active` | BooleanField | default=True | |

#### LabPanel
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `code` | SlugField(40) | unique | |
| `name` | CharField(120) | required | |
| `tests` | M2M(LabTest) | | |

#### LabOrder
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `encounter` | FK(ClinicalEncounter) | PROTECT | |
| `patient` | FK(Patient) | CASCADE, indexed | Denormalized |
| `ordered_date` | DateField | required | |
| `status` | CharField(12) | choices | ordered/collected/resulted/cancelled |
| `notes` | CharField(240) | blank | |

#### LabOrderItem
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `order` | FK(LabOrder) | CASCADE | |
| `test` | FK(LabTest) | PROTECT | |
| | | UniqueConstraint(order, test) | |

#### LabResult
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `test` | FK(LabTest) | PROTECT | |
| `order_item` | FK(LabOrderItem) | SET_NULL, null | Optional link |
| `value_numeric` | DecimalField(12,4) | null | |
| `value_text` | CharField(120) | blank | For qualitative results |
| `unit` | CharField(20) | blank | |
| `sample_date` | DateField | null | |
| `result_date` | DateField | required | |
| `flag` | CharField(1) | blank | "" / "L" / "H" |
| `source` | CharField(8) | choices | lab/manual/derived |
| `derived_from` | FK(self) | SET_NULL, null | For computed values |
| `formula_version` | CharField(40) | blank | e.g. "CKD-EPI-2021-creatinine" |

---

### pathology

#### Biopsy
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `biopsy_date` | DateField | required | |
| `adequacy` | CharField(12) | choices | adequate/borderline/inadequate |
| `indication` | CharField(20) | choices | BiopsyIndication |
| `result_category` | CharField(14) | choices, indexed | BiopsyResult |
| `review_status` | CharField(20) | choices | pending/awaiting_central/concordant/discordant/adjudicated |
| `total_glomeruli` | PositiveSmallInt | null | |
| `global_sclerosis_pct` | DecimalField(5,1) | null | |
| `ifta_pct` | DecimalField(5,1) | null | |
| `arteriosclerosis` | CharField(8) | choices | none/mild/moderate/severe |
| `arteriolar_hyalinosis` | BooleanField | default=False | |
| `dkd_lesion_present` | BooleanField | default=False | |
| `crescents_present` | BooleanField | default=False | |
| `crescent_pct` | DecimalField(5,1) | null | |
| `necrosis_present` | BooleanField | default=False | |
| `if_pattern` | CharField(120) | blank | |
| `em_findings` | TextField | blank | |

#### GNDiagnosis
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | OneToOne(Biopsy) | CASCADE | |
| `diagnosis` | CharField(120) | choices | SPECIFIC_GN_DIAGNOSIS |
| `broad_group` | CharField(80) | blank | GN_BROAD_GROUP |
| `pathogenesis_group` | CharField(80) | blank | GN_PATHOGENESIS_GROUP |
| `primary_secondary` | CharField(10) | choices | |
| `secondary_cause` | CharField(120) | blank | |

#### IgANScore (Oxford MEST-C)
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | OneToOne(Biopsy) | CASCADE | |
| `M` | PositiveSmallInt | 0-1 | Mesangial hypercellularity |
| `E` | PositiveSmallInt | 0-1 | Endocapillary hypercellularity |
| `S` | PositiveSmallInt | 0-1 | Segmental sclerosis |
| `T` | PositiveSmallInt | 0-2 | Tubular atrophy/IF |
| `C` | PositiveSmallInt | 0-2 | Crescents |

#### LupusPathology (ISN/RPS)
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | OneToOne(Biopsy) | CASCADE | |
| `isn_rps_class` | CharField(4) | choices | I-VI |
| `activity_index` | PositiveSmallInt | 0-24 | NIH |
| `chronicity_index` | PositiveSmallInt | 0-12 | NIH |

#### FSGSPathology
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | OneToOne(Biopsy) | CASCADE | |
| `primary_secondary` | CharField(10) | choices | |
| `variant` | CharField(10) | choices | nos/perihilar/cellular/tip/collapsing |

#### MembranousPathology
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | OneToOne(Biopsy) | CASCADE | |
| `pla2r_tissue` | CharField(4) | choices | pos/neg/nd |
| `thsd7a_tissue` | CharField(4) | choices | pos/neg/nd |
| `mn_stage` | PositiveSmallInt | 0-4 | Ehrenreich-Churg I-IV |

#### BiopsyImage
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | FK(Biopsy) | CASCADE | |
| `image` | FileField | | upload_to="biopsy_images/%Y/%m/" |
| `stain` | CharField(10) | choices | he/pas/silver/trichrome/if/em |
| `description` | CharField(240) | blank | |

#### PathologyReview
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `biopsy` | FK(Biopsy) | CASCADE | |
| `role` | CharField(12) | choices | local/central/adjudication |
| `reviewer` | FK(User) | SET_NULL, null | |
| `review_date` | DateField | null | |
| `diagnosis` | CharField(120) | choices | |
| `broad_group` | CharField(80) | blank | |
| `mest_m` through `mest_c` | PositiveSmallInt | null | Oxford MEST-C |
| `isn_rps_class` | CharField(4) | blank | |
| `fsgs_variant` | CharField(10) | blank | |
| `is_final` | BooleanField | default=False | |
| | | UniqueConstraint(biopsy, role) | |

---

### treatments

#### DrugMaster
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `generic_name` | CharField(120) | unique | |
| `brand_names` | JSONField | default=list | Bangladeshi brands |
| `drug_class` | CharField(20) | choices | DrugClass enum |
| `available_strengths` | JSONField | default=list | |
| `default_frequency` | CharField(40) | blank | |
| `default_route` | CharField(20) | blank, default="PO" | |
| `available_routes` | JSONField | default=list | |
| `strengths_by_route` | JSONField | default=dict | |
| `renal_dose_adjust` | BooleanField | default=False | |
| `egfr_caution_below` | DecimalField(4,0) | null | |
| `is_active` | BooleanField | default=True | |

#### TreatmentExposure
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `drug` | FK(DrugMaster) | PROTECT | |
| `drug_name` | CharField(120) | | Denormalized snapshot |
| `dose` | CharField(40) | blank | |
| `dose_unit` | CharField(20) | blank | |
| `frequency` | CharField(40) | blank | |
| `route` | CharField(20) | blank | |
| `start_date` | DateField | required | |
| `stop_date` | DateField | null | |
| `ongoing` | BooleanField | default=True | |
| `stop_reason` | CharField(20) | choices | StopReason enum |
| `opened_by_encounter` | FK(ClinicalEncounter) | SET_NULL, null | |
| `closed_by_encounter` | FK(ClinicalEncounter) | SET_NULL, null | |

---

### prescriptions

#### Prescription
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `encounter` | FK(ClinicalEncounter) | PROTECT | |
| `version` | PositiveSmallInt | default=1 | |
| `status` | CharField(8) | choices | draft/final |
| `diagnosis_text` | CharField(240) | blank | |
| `comorbidities` | CharField(240) | blank | |
| `investigations_advised` | TextField | blank | |
| `advice` | TextField | blank | |
| `stop_notes` | TextField | blank | |
| `printed_at` | DateTimeField | null | |
| `printed_by` | FK(User) | PROTECT, null | |
| `pdf_file` | FileField | blank | |
| `content_hash` | CharField(64) | blank | SHA-256 |
| `reconciled_at` | DateTimeField | null | |
| | | UniqueConstraint(encounter, version) | |

#### PrescriptionItem
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `prescription` | FK(Prescription) | CASCADE | |
| `drug` | FK(DrugMaster) | PROTECT | |
| `brand` | CharField(120) | blank | |
| `strength` | CharField(40) | blank | |
| `dose` | CharField(40) | blank | |
| `dose_unit` | CharField(20) | blank | |
| `route` | CharField(20) | blank | |
| `frequency` | CharField(40) | blank | |
| `timing` | CharField(8) | choices | before/after/empty/any |
| `duration` | CharField(40) | blank | |
| `instruction_bn` | CharField(240) | blank | Bengali |
| `sort_order` | PositiveSmallInt | default=0 | |

#### AdviceTemplate
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `title` | CharField(100) | unique | |
| `body` | TextField | required | |
| `is_active` | BooleanField | default=True | |
| `sort_order` | PositiveSmallInt | default=0 | |

---

### analytics

#### PatientOutcome (Computed)
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | OneToOne(Patient) | CASCADE | |
| `index_date` | DateField | null | |
| `baseline_egfr` | DecimalField(6,1) | null | |
| `baseline_creatinine` | DecimalField(6,2) | null | |
| `baseline_upcr` | DecimalField(8,3) | null | |
| `last_contact_date` | DateField | null | |
| `followup_days` | IntegerField | null | |
| `n_egfr` | IntegerField | default=0 | |
| `latest_egfr` | DecimalField(6,1) | null | |
| `egfr_slope` | DecimalField(7,2) | null | mL/min/1.73m²/year |
| `sustained_40_decline` | BooleanField | default=False | |
| `sustained_40_date` | DateField | null | |
| `sustained_50_decline` | BooleanField | default=False | |
| `sustained_50_date` | DateField | null | |
| `doubling_creatinine` | BooleanField | default=False | |
| `doubling_date` | DateField | null | |
| `eskd` | BooleanField | default=False | |
| `eskd_date` | DateField | null | |
| `death` | BooleanField | default=False | |
| `death_date` | DateField | null | |
| `composite_kidney_event` | BooleanField | default=False | |
| `composite_date` | DateField | null | |
| `composite_cause` | CharField(40) | blank | |
| `remission_definition` | CharField(10) | blank | igan/mn/lupus/fsgs/mcd/aav/other |
| `proteinuria_source` | CharField(8) | blank | utp/upcr/mixed |
| `latest_upcr` | DecimalField(8,3) | null | |
| `nadir_upcr` | DecimalField(8,3) | null | |
| `best_proteinuria_reduction_pct` | DecimalField(5,1) | null | |
| `igan_proteinuria_response` | BooleanField | default=False | |
| `igan_proteinuria_response_date` | DateField | null | |
| `complete_remission` | BooleanField | default=False | |
| `complete_remission_date` | DateField | null | |
| `partial_remission` | BooleanField | default=False | |
| `partial_remission_date` | DateField | null | |
| `any_remission_date` | DateField | null | |
| `proteinuria_relapse` | BooleanField | default=False | |
| `proteinuria_relapse_date` | DateField | null | |
| `remission_status` | CharField(10) | choices | none/partial/complete |
| `any_relapse` | BooleanField | default=False | |

---

### safety

#### AdverseEvent
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `onset_date` | DateField | required | |
| `category` | CharField(20) | choices | infection/steroid_toxicity/hematologic/... |
| `infection_type` | CharField(16) | blank | tb/pjp/cmv/zoster/... |
| `description` | CharField(240) | blank | |
| `severity` | CharField(18) | choices | mild/moderate/severe/life_threatening/fatal |
| `serious` | BooleanField | default=False | Auto-set if G4/G5 or hospitalized |
| `hospitalization` | BooleanField | default=False | |
| `outcome` | CharField(12) | blank | recovered/recovering/ongoing/fatal |
| `suspected_drug` | FK(DrugMaster) | SET_NULL, null | |
| `relatedness` | CharField(14) | choices | unrelated/unlikely/possible/probable/definite |
| `encounter` | FK(ClinicalEncounter) | SET_NULL, null | |
| `notes` | CharField(240) | blank | |

---

### studies

#### Study
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `code` | SlugField(40) | unique | e.g. "ADVANCED-DKD-IGAN" |
| `title` | CharField(240) | required | |
| `study_type` | CharField(20) | choices | observational/quasi_experimental/rct |
| `status` | CharField(12) | choices | planning/recruiting/active/closed |
| `target_enrollment` | PositiveInt | null | |
| `primary_endpoint` | CharField(60) | blank | |
| `randomization_scheme` | CharField(20) | choices | none/simple/block/stratified_block |
| `block_multipliers` | JSONField | default=list | |
| `stratify_by` | JSONField | default=list | |
| `random_seed` | BigIntegerField | default=20260101 | |
| `requires_trial_consent` | BooleanField | default=True | |

#### StudyArm
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `study` | FK(Study) | CASCADE | |
| `code` | SlugField(40) | | |
| `name` | CharField(120) | required | |
| `ratio` | PositiveSmallInt | default=1 | Allocation weight |
| `order` | PositiveSmallInt | default=0 | |
| `is_control` | BooleanField | default=False | |
| | | UniqueConstraint(study, code) | |

#### StudyEnrollment
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `study` | FK(Study) | CASCADE | |
| `patient` | FK(Patient) | CASCADE | |
| `status` | CharField(12) | choices | screened/ineligible/enrolled/withdrawn/completed |
| `screened_date` | DateField | null | |
| `eligible` | BooleanField | default=False | |
| `ineligibility_reasons` | JSONField | default=list | |
| `enrolled_date` | DateField | null | |
| `arm` | FK(StudyArm) | PROTECT, null | |
| `stratum` | CharField(120) | blank | |
| `sequence_position` | IntegerField | null | |
| `randomized_by` | FK(User) | SET_NULL, null | |
| `randomized_at` | DateTimeField | null | |
| `withdrawn_date` | DateField | null | |
| `completion_date` | DateField | null | |
| | | UniqueConstraint(study, patient) | |

---

### scheduling

#### ScheduledVisit
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `kind` | CharField(12) | choices | routine/early_safety |
| `label` | CharField(20) | required | e.g. "Month 3" |
| `target_date` | DateField | required | Protocol timepoint |
| `window_start` | DateField | required | target - 7 days |
| `window_end` | DateField | required | target + 7 days |
| `clinic_date` | DateField | null | Assigned Tuesday |
| `status` | CharField(10) | choices | scheduled/completed/missed/cancelled |
| `encounter` | FK(ClinicalEncounter) | SET_NULL, null | |
| | | UniqueConstraint(patient, label) | |

---

### biomarkers

#### BiomarkerKinetics (Computed)
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | OneToOne(Patient) | CASCADE | |
| `pla2r_baseline` | DecimalField(8,1) | null | |
| `pla2r_latest` | DecimalField(8,1) | null | |
| `pla2r_nadir` | DecimalField(8,1) | null | |
| `pla2r_baseline_date` | DateField | null | |
| `pla2r_pct_decline` | DecimalField(5,1) | null | |
| `pla2r_50pct_decline` | BooleanField | default=False | |
| `pla2r_50pct_date` | DateField | null | |
| `pla2r_50pct_days` | IntegerField | null | |
| `pla2r_immunological_remission` | BooleanField | default=False | |
| `pla2r_remission_date` | DateField | null | |
| `c3_recovered` | BooleanField | default=False | |
| `c3_recovered_date` | DateField | null | |
| `c4_recovered` | BooleanField | default=False | |
| `c4_recovered_date` | DateField | null | |
| `dsdna_baseline` | DecimalField(8,1) | null | |
| `dsdna_latest` | DecimalField(8,1) | null | |
| `dsdna_normalized` | BooleanField | default=False | |
| `dsdna_normalized_date` | DateField | null | |

---

### audit

#### AuditLog
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `model_label` | CharField(100) | required | e.g. "prescriptions.Prescription" |
| `object_pk` | CharField(64) | required | |
| `object_repr` | CharField(200) | blank | |
| `action` | CharField(8) | choices | create/update/delete |
| `field_name` | CharField(80) | blank | |
| `old_value` | TextField | null | |
| `new_value` | TextField | null | |
| `changed_by` | FK(User) | SET_NULL, null | |
| `change_reason` | CharField(240) | blank | |

#### Consent
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `consent_type` | CharField(12) | choices | registry/biobank/genetic/imaging/trial |
| `form_version` | CharField(40) | required | e.g. "BGDDR-ICF-v2.1" |
| `status` | CharField(10) | choices | granted/withdrawn/refused |
| `consent_date` | DateField | required | |
| `withdrawn_date` | DateField | null | |
| `obtained_by` | FK(User) | SET_NULL, null | |
| `scope` | TextField | blank | |
| `document` | FileField | blank | |
| `supersedes` | OneToOne(self) | SET_NULL, null | Version chain |
| `is_current` | BooleanField | default=False | |
| | | UniqueConstraint(patient, consent_type) WHERE is_current=True | |

---

### users

#### UserProfile
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `user` | OneToOne(User) | CASCADE | |
| `role` | CharField(30) | blank, choices | data_manager/statistician/readonly/coordinator/investigator/pathologist |
| `department` | CharField(80) | blank | |
| `phone` | CharField(30) | blank | |
| `is_clinician` | BooleanField | default=False | |

#### Invitation
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `email` | EmailField | required | |
| `role` | CharField(30) | blank | |
| `token` | CharField(64) | unique, indexed | |
| `created_by` | FK(User) | SET_NULL, null | |
| `created_at` | DateTimeField | auto_now_add | |
| `used_at` | DateTimeField | null | |
| `used_by` | FK(User) | SET_NULL, null | |

---

### clinical (GDES)

#### ClinicalAssessment
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `encounter` | OneToOne(ClinicalEncounter) | CASCADE | |
| `chief_complaint` | TextField | blank | |
| `time_course` | CharField(20) | choices | acute/subacute/chronic/relapsing |
| `features` | JSONField | default=list | Clinical feature codes |
| `syndrome_classification` | CharField(100) | blank | |
| `severity_flags` | JSONField | default=list | |

#### VitalSign
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `encounter` | FK(ClinicalEncounter) | CASCADE | |
| `bp_systolic` | PositiveSmallInt | null | |
| `bp_diastolic` | PositiveSmallInt | null | |
| `heart_rate` | PositiveSmallInt | null | |
| `weight_kg` | DecimalField(5,1) | null | |
| `height_cm` | DecimalField(5,1) | null | |

---

### knowledge (GDES)

#### GuidelineSource
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `title` | CharField(500) | required | |
| `abbreviation` | CharField(50) | required | e.g. "KDIGO" |
| `version_year` | PositiveSmallInt | required | |
| `url` | URLField(500) | blank | |
| `effective_date` | DateField | required | |
| `retired_date` | DateField | null | |

#### KnowledgeBaseEntry
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `entry_id` | CharField(50) | unique | e.g. "KB-IGA-001" |
| `disease_id` | CharField(50) | indexed | iga/membranous/mcd/fsgs/lupus/anca/antiGbm/infectionRelated/c3 |
| `rule_data` | JSONField | required | {conditions, weight, explanation} |
| `source` | FK(GuidelineSource) | PROTECT | |
| `evidence_grade` | CharField(2) | choices | 1/2/NG/OP |
| `status` | CharField(10) | choices | draft/reviewed/active/retired |
| `effective_date` | DateField | required | |
| `retired_date` | DateField | null | |

---

### decision (GDES)

#### DecisionRequest
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `encounter` | FK(ClinicalEncounter) | CASCADE | |
| `input_snapshot` | JSONField | required | Patient data at time of request |

#### DecisionResult
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `request` | OneToOne(DecisionRequest) | CASCADE | |
| `phenotype` | CharField(200) | blank | |
| `urgency_level` | CharField(100) | blank | |
| `urgency_tone` | CharField(20) | blank | urgent/nephrotic/nephritic |
| `urgency_reasons` | JSONField | default=list | |
| `ranked_differential` | JSONField | default=list | |
| `next_steps` | JSONField | default=dict | |
| `traceability` | JSONField | default=list | KB entries applied |
| `explanation` | TextField | blank | |

---

### timeline (GDES)

#### TimelineEvent
| Field | Type | Constraints | Notes |
|---|---|---|---|
| `patient` | FK(Patient) | CASCADE | |
| `domain` | CharField(20) | choices | patient/encounter/clinical/lab/biopsy/decision |
| `event_type` | CharField(100) | indexed | |
| `event_date` | DateTimeField | indexed | |
| `summary` | CharField(500) | required | |
| `details` | JSONField | default=dict | |
| `source_id` | CharField(100) | blank | |
| `source_url` | CharField(500) | blank | |

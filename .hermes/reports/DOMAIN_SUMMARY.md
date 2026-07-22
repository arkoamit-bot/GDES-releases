# BGDDR / GDES — Clinical Domain Summary

> **Generated**: 2026-07-21
> **Source**: GDES repository at `C:\Users\User\Documents\GitHub\GDES`
> **System**: Bangladesh Glomerular Disease & Diabetes Registry / Glomerular Disease Expert System

---

## Table of Contents

1. [Clinical Domain Overview](#1-clinical-domain-overview)
2. [Patient Demographics & Enrollment](#2-patient-demographics--enrollment)
3. [Clinical Encounters & Workflows](#3-clinical-encounters--workflows)
4. [Baseline Assessment](#4-baseline-assessment)
5. [Laboratory Medicine](#5-laboratory-medicine)
6. [Pathology & Biopsy](#6-pathology--biopsy)
7. [Treatments & Prescriptions](#7-treatments--prescriptions)
8. [Renal Function & eGFR](#8-renal-function--egfr)
9. [Disease-Specific Scoring Systems](#9-disease-specific-scoring-systems)
10. [Clinical Outcomes & Remission](#10-clinical-outcomes--remission)
11. [Biostatistics & Survival Analysis](#11-biostatistics--survival-analysis)
12. [Biomarker Kinetics](#12-biomarker-kinetics)
13. [Safety & Adverse Events](#13-safety--adverse-events)
14. [Clinical Decision Support](#14-clinical-decision-support)
15. [Study Design & Randomization](#15-study-design--randomization)
16. [Scheduling & Follow-Up](#16-scheduling--follow-up)
17. [Audit Trail & Consent](#17-audit-trail--consent)
18. [Research Data Export](#18-research-data-export)
19. [Glomerular Disease Taxonomy](#19-glomerular-disease-taxonomy)
20. [Protocol Alignment](#20-protocol-alignment)

---

## 1. Clinical Domain Overview

GDES is a **multi-disease glomerular disease registry** with integrated clinical decision support. It covers the complete nephrology workflow from enrollment through longitudinal follow-up, embedded clinical trials, and outcome analysis.

### Primary Disease Domains

| Disease | ICD/Category | Scoring System | Remission Criteria |
|---------|-------------|----------------|-------------------|
| **IgA Nephropathy (IgAN)** | Primary GN | Oxford MEST-C | Response: ≥30% reduction or <0.3 g/day; target <0.5 g/day |
| **Membranous Nephropathy (MN)** | Primary GN | Ehrenreich-Churg Stage I-IV | Complete: <0.3 g/day; Partial: ≥50% reduction & <3.5 |
| **Focal Segmental Glomerulosclerosis (FSGS)** | Primary GN | Columbia Classification | Complete: <0.3 g/day; Partial: ≥50% & <3.5 |
| **Minimal Change Disease (MCD)** | Primary GN | — | Complete: <0.3 g/day; Partial: ≥50% & <3.5 |
| **Lupus Nephritis (LN)** | Secondary GN | ISN/RPS Class I-VI, NIH Activity/Chronicity | Complete: <0.5 g/day + eGFR within 10% of baseline |
| **ANCA-Associated Vasculitis (AAV)** | Secondary GN | — | Disease-specific |
| **Anti-GBM Disease** | Secondary GN | — | Disease-specific |
| **Infection-Related GN** | Secondary GN | — | Disease-specific |
| **C3 Glomerulopathy** | Complement-mediated | — | C3/C4 normalization |

### Disease Classification System

The system uses a hierarchical classification:

```
SPECIFIC_GN_DIAGNOSIS → GN_BROAD_GROUP → GN_PATHOGENESIS_GROUP
     ↓                       ↓                    ↓
  IgAN, MN, FSGS,       Primary,              Immune-complex,
  Lupus, AAV, etc.       Secondary             Pauci-immune, etc.
```

---

## 2. Patient Demographics & Enrollment

### Patient Model Fields

| Field | Type | Clinical Purpose |
|-------|------|-----------------|
| `patient_id` | Auto-generated (BGD-NNNNN) | Registry identifier |
| `hospital_id` | String | Hospital registration cross-reference |
| `name` | String | Full name |
| `phone` | String | Contact for reminders/follow-up |
| `sex` | M/F/O | Biological sex (affects eGFR formula) |
| `dob` | Date | Age calculation |
| `enrollment_date` | Date | Registry start; index date for outcomes |
| `cohort` | PATIENT_CATEGORY | Research cohort assignment |
| `diabetes_status` | none/t1/t2/other | Diabetes co-morbidity (key stratification) |
| `primary_diagnosis` | SPECIFIC_GN_DIAGNOSIS | Primary glomerular disease |
| `latest_egfr` | Decimal | Cached; updated by lab results |
| `registration_status` | suspected/registered/not_registered/excluded | Registry workflow state |
| `current_phase` | active/remission/post_remission/relapse | Disease phase (state machine) |

### Eligibility Criteria

- **Adult-only**: ≥18 years per GN Master Protocol v2
- **Diabetes stratification**: none / type 1 / type 2 / other
- **Registration statuses**: suspected → registered (or excluded)

---

## 3. Clinical Encounters & Workflows

### ClinicalEncounter (Visit Hub)

Every clinical visit creates a `ClinicalEncounter` — the central entity that links all clinical activities.

| Field | Purpose |
|-------|---------|
| `encounter_type` | baseline / followup / unscheduled |
| `seen_by` | Clinician (FK→User) |
| `systolic_bp` / `diastolic_bp` | Blood pressure |
| `weight_kg` | Weight tracking |
| `edema_grade` | 0-4 edema grading |
| `symptoms` | Free-text symptom description |
| `clinician_response` | not_assessed / complete / partial / none / stable |
| `disease_phase` | Per-visit disease phase assessment |
| `treatment_adjusted` | Whether treatment was modified |

### Admission Tracking

Tracks hospital admissions linked to the patient record:
- Ward, reason, dates, discharge advice
- Linked biopsy if performed during admission

### Relapse Episodes

| Relapse Type | Description |
|-------------|-------------|
| `proteinuric` | Proteinuria recurrence |
| `nephrotic` | Nephrotic syndrome return |
| `nephritic` | Nephritic flare |
| `functional` | Functional decline |
| `serologic` | Serological relapse |

### Clinical Events (Endpoints)

| Event Type | Clinical Meaning |
|-----------|-----------------|
| `eskd` | End-stage kidney disease |
| `dialysis_start` | Dialysis initiation |
| `transplant` | Kidney transplant |
| `death` | Mortality |
| `complete_remission` | Complete proteinuria remission |
| `partial_remission` | Partial proteinuria remission |
| `relapse` | Disease relapse |
| `major_cv` | Major cardiovascular event |

### Disease Phase State Machine

```
ACTIVE ──complete──► REMISSION ──stable──► POST_REMISSION
  ▲                                              │
  └──────────────── RELAPSE ◄────────────────────┘
```

Transitions are derived from clinician response and treatment adjustments.

---

## 4. Baseline Assessment

The `BaselineAssessment` captures a comprehensive enrollment snapshot:

### Demographics & Social
- Division of residence (Bangladesh administrative divisions)
- Socioeconomic status (Low/Middle/High)
- Monthly income (BDT)
- Education, occupation
- Smoking status, alcohol use

### Medical History
| Category | Fields |
|----------|--------|
| **Kidney Disease** | Previous kidney disease, family history |
| **Autoimmune** | Autoimmune disease history |
| **Infection** | Chronic infection status |
| **Malignancy** | Cancer history |
| **Immunosuppression** | Prior immunosuppression use |
| **Drug History** | Previous medications (free text) |

### Physical Examination
- Height, weight → **auto-derived BMI** with WHO Asian category cutoffs
- Blood pressure (systolic/diastolic)
- Pulse, temperature, respiratory rate
- Edema grade (0-4)
- Volume status (euvolemic/hypervolemic/hypovolemic)
- Skin findings, joint findings, fundoscopy

### Diabetes-Specific
| Field | Purpose |
|-------|---------|
| `dm_duration_years` | Duration of diabetes |
| `hba1c` | Glycemic control |
| `diabetic_retinopathy` | Retinopathy screening |
| `neuropathy` | Neuropathy assessment |
| `diabetic_foot_history` | Foot disease history |

### Cardiovascular
- Hypertension history
- CVD history

### Presentation
- Presentation syndromes (multi-select JSON)
- Presenting symptoms (multi-select JSON)
- Active urinary sediment
- RBC casts (active nephritic sediment marker)

---

## 5. Laboratory Medicine

### Lab Test Catalog

Each `LabTest` has:
- `code` (e.g., "creatinine", "egfr", "utp_24h", "upcr")
- `name`, `loinc` code, `default_unit`
- `value_type` (numeric/qualitative)
- Reference ranges (`ref_low`, `ref_high`)
- `is_derived` flag (eGFR is computed, not entered)

### Lab Panels

Pre-defined panels (M2M→LabTest) for ordering convenience (e.g., renal panel, immunosuppression monitoring panel).

### Lab Order Workflow

```
LabOrder (per encounter) → LabOrderItem (per test) → LabResult (per patient/test)
```

Status flow: ordered → collected → resulted (or cancelled)

### LabResult Fields

| Field | Purpose |
|-------|---------|
| `value_numeric` | Numeric result |
| `value_text` | Qualitative result |
| `flag` | L (low) / H (high) |
| `source` | lab / manual / derived |
| `derived_from` | FK→self for computed values (eGFR from creatinine) |
| `formula_version` | e.g., "CKD-EPI-2021-creatinine" |

### Key Lab Tests in Registry

| Test Code | Description | Usage |
|-----------|------------|-------|
| `creatinine` | Serum creatinine | eGFR derivation |
| `egfr` | Estimated GFR | Auto-derived from creatinine |
| `utp_24h` | 24-hour urine total protein | Primary proteinuria measure |
| `upcr` | Urine protein-to-creatinine ratio | Fallback for UTP |
| `hba1c` | HbA1c | Diabetes control |
| `anti_pla2r` | Anti-PLA2R antibodies | MN disease activity |
| `complement_c3` | Serum C3 | LN/C3G activity |
| `complement_c4` | Serum C4 | LN activity |
| `anti_dsDNA` | Anti-dsDNA antibodies | LN activity |
| `albumin` | Serum albumin | Nephrotic assessment |

---

## 6. Pathology & Biopsy

### Biopsy Record

| Field | Purpose |
|-------|---------|
| `adequacy` | adequate / borderline / inadequate |
| `indication` | Biopsy indication (enum) |
| `result_category` | Primary finding category |
| `total_glomeruli` | Glomerular count |
| `global_sclerosis_pct` | Chronicity marker |
| `ifta_pct` | Interstitial fibrosis & tubular atrophy |
| `arteriosclerosis` | none/mild/moderate/severe |
| `arteriolar_hyalinosis` | Boolean |
| `crescents_present` / `crescent_pct` | Active crescents (critical for prognosis) |
| `necrosis_present` | Necrosis |
| `if_pattern` | Immunofluorescence pattern |
| `em_findings` | Electron microscopy findings |

### Disease-Specific Pathology Scores

#### Oxford MEST-C Score (IgAN)

| Component | Range | Description |
|-----------|-------|-------------|
| **M** (Mesangial) | 0-1 | Mesangial hypercellularity |
| **E** (Endocapillary) | 0-1 | Endocapillary hypercellularity |
| **S** (Segmental) | 0-1 | Segmental sclerosis |
| **T** (Tubular) | 0-2 | Tubular atrophy/interstitial fibrosis |
| **C** (Crescents) | 0-2 | Crescent formation |

#### ISN/RPS Classification (Lupus Nephritis)

| Class | Description |
|-------|-------------|
| I | Minimal mesangial |
| II | Mesangial proliferative |
| III | Focal proliferative |
| IV | Diffuse proliferative |
| V | Membranous |
| VI | Sclerotic |

Plus NIH Activity Index (0-24) and Chronicity Index (0-12).

#### Columbia Classification (FSGS)

| Variant | Significance |
|---------|-------------|
| NOS | Not otherwise specified (most common) |
| Perihilar | Tip of hilum |
| Cellular | Cellular lesions |
| Tip | Tip lesion |
| Collapsing | Collapsing variant (worst prognosis) |

#### Ehrenreich-Churg Staging (Membranous Nephropathy)

| Stage | Description |
|-------|-------------|
| I | Subepithelial deposits |
| II | Spikes |
| III | Chain-link formation |
| IV | Dissolution |

Plus PLA2R and THSD7A tissue staining (pos/neg/not done).

### Central Review Workflow

```
1. LOCAL read → PathologyReview(role=LOCAL)
2. CENTRAL read → PathologyReview(role=CENTRAL)
3. Field-by-field comparison:
   a. CONCORDANT → auto-finalize GNDiagnosis + scoring
   b. DISCORDANT → ADJUDICATION required
4. ADJUDICATION → PathologyReview(role=ADJUDICATION) → finalize
5. Inter-observer agreement → Cohen's κ per field
```

### Biopsy Images

| Stain | Code |
|-------|------|
| Hematoxylin & Eosin | he |
| Periodic Acid-Schiff | pas |
| Silver | silver |
| Trichrome | trichrome |
| Immunofluorescence | if |
| Electron Microscopy | em |

Images are **consent-gated** (biobank/registry consent required).

---

## 7. Treatments & Prescriptions

### Drug Master (Formulary)

| Field | Purpose |
|-------|---------|
| `generic_name` | Unique generic identifier |
| `brand_names` | Bangladeshi brand names (JSON) |
| `drug_class` | Research drug class (enum) |
| `available_strengths` | Available formulations |
| `default_frequency` / `default_route` | Standard dosing |
| `strengths_by_route` | Route-specific strengths |
| `renal_dose_adjust` | Whether renal adjustment needed |
| `egfr_caution_below` | eGFR threshold for caution |

### Drug Classes (for research grouping)

The system tracks drug classes for cohort analysis (e.g., `drug:sglt2i`, `drug:hcq`, `drug:finerenone`, `drug:steroid`). Grouping dimensions include:
- `drug:<class>` — by drug class
- `study:<code>` — by trial arm

### Treatment Exposure (Research Episodes)

Auto-maintained by the reconciliation engine:

| State | Trigger | Action |
|-------|---------|--------|
| **OPEN** | New drug in Rx, no open episode | Start new episode |
| **CLOSE** | Open episode, drug absent from Rx | Stop with reason |
| **CHANGE** | Same drug, dose/regimen changed | Close old + open new (episode split) |
| **CONTINUE** | Same drug, identical regimen | No-op |

### Prescription Workflow

```
1. Clinician creates Prescription (DRAFT)
2. Add PrescriptionItem entries (drug, dose, frequency, route, instructions in Bengali)
3. Preview: /prescriptions/{id}/preview/ (HTML)
4. Safety check: /prescriptions/{id}/safety/ (JSON warnings)
5. Reconciliation preview: /prescriptions/{id}/reconcile/preview/ (diff)
6. Finalize: POST /prescriptions/{id}/finalize/
   a. Safety checks run (4 categories)
   b. Prescription frozen (status=FINAL, SHA-256 content hash)
   c. TreatmentExposure episodes reconciled
7. Print: /prescriptions/{id}/pdf/ (bilingual English+Bangla)
```

### Safety Checks

| Check | Description |
|-------|-------------|
| **Renal Dosing** | Drug flagged for adjustment + patient eGFR below threshold |
| **Prior Intolerance** | Re-prescribing drug previously stopped for AE/intolerance |
| **Duplicate Therapy** | Two drugs of same DrugClass on one prescription |
| **Glycaemic Effect** | Steroid/CNI in diabetic → intensification warning |

### Bilingual Prescription Template

- English: Drug names, doses, frequencies
- Bangla: Patient instructions, advice
- Letterhead: BIRDEM General Hospital, Department of Nephrology

---

## 8. Renal Function & eGFR

### CKD-EPI 2021 Equation

```
eGFR = f(serum creatinine, age, sex)
```

- **Race-free** equation (CKD-EPI 2021 standard)
- Formula version stored on every LabResult for reproducibility
- Auto-derived when creatinine is entered: `record_result_with_derivation()`

### eGFR Tracking

| Feature | Implementation |
|---------|---------------|
| **Versioned eGFR** | Each creatinine entry derives a new eGFR with formula version |
| **Slope calculation** | Simple linear regression (mL/min/1.73m²/year) |
| **LMM eGFR slope** | Laird-Ware EM mixed-effects model for group comparisons |
| **Patient caching** | `Patient.latest_egfr` auto-updated from lab results |

### eGFR-Linked Safety

The labs → prescription loop ensures:
1. Entering creatinine auto-derives eGFR
2. eGFR feeds into prescription safety checks
3. Renal dosing warnings triggered when eGFR drops below drug thresholds

---

## 9. Disease-Specific Scoring Systems

### Oxford MEST-C (IgA Nephropathy)

Used for histopathological grading of IgAN biopsies. Each component independently predicts prognosis:
- **M**: Mesangial hypercellularity (>50% of glomeruli)
- **E**: Endocapillary hypercellularity
- **S**: Segmental sclerosis
- **T**: Tubular atrophy / interstitial fibrosis (0-2 scale, most powerful predictor)
- **C**: Crescents (>25% of glomeruli → poor prognosis)

### ISN/RPS (Lupus Nephritis)

WHO/ISN/RPS 2003 revision classification:
- Classes I-VI from minimal mesangial to sclerotic
- NIH Activity Index: measures active inflammation (max 24)
- NIH Chronicity Index: measures irreversible damage (max 12)
- Guides treatment intensity (e.g., class IV requires aggressive immunosuppression)

### Columbia Classification (FSGS)

MesoAmerican classification of FSGS variants with prognostic implications:
- **Collapsing variant**: Worst prognosis, HIV-associated
- **Tip lesion**: Best prognosis
- **NOS**: Most common, intermediate

### Ehrenreich-Churg (Membranous Nephropathy)

Stage I-IV classification based on electron microscopy findings (subepithelial deposit evolution).

### Biomarker-Enhanced Scoring

| Biomarker | Disease | Actionable Threshold |
|-----------|---------|---------------------|
| Anti-PLA2R | MN | ≥50% decline → early response predictor |
| Anti-PLA2R seroconversion | MN | Negative → immunological remission |
| Complement C3/C4 | LN/C3G | Normalization → complement recovery |
| Anti-dsDNA | LN | Normalization → disease control |

---

## 10. Clinical Outcomes & Remission

### PatientOutcome (Computed Model)

A denormalized row computed from longitudinal data — not entered by clinicians.

#### Renal Function Outcomes

| Field | Definition |
|-------|-----------|
| `baseline_egfr` | eGFR at enrollment |
| `latest_egfr` | Most recent eGFR |
| `egfr_slope` | mL/min/1.73m²/year |
| `sustained_40_decline` | ≥40% eGFR decline (sustained) |
| `sustained_50_decline` | ≥50% eGFR decline (sustained) |
| `doubling_creatinine` | Serum creatinine doubled |

#### Hard Endpoints

| Endpoint | Definition |
|----------|-----------|
| `eskd` | Dialysis/transplant OR eGFR < 15 |
| `death` | All-cause mortality |
| `composite_kidney_event` | Earliest of: ESKD, ≥50% eGFR decline, renal death |

#### Proteinuria Remission (Disease-Specific)

| Disease | Complete Remission | Partial Remission | Response |
|---------|-------------------|-------------------|----------|
| **IgAN** | < 0.3 g/day | n/a | ≥30% reduction OR <0.3; target <0.5 |
| **MN / FSGS / MCD** | < 0.3 g/day | ≥50% reduction AND < 3.5 g/day | — |
| **Lupus** | < 0.5 g/day + eGFR within 10% of baseline (15% if reduced) | ≥50% reduction & < 3.5 | — |

**Key rules**:
- All remissions must be **sustained** (transient dips don't count)
- Stamped with **first date achieved** (time-to-event endpoint)
- `proteinuria_relapse`: first ≥ 1.0 g/day after remission

### Outcome Computation Pipeline

```
compute_patient_outcome(patient):
  1. Extract longitudinal series: eGFR, creatinine, proteinuria
  2. Determine index date (enrollment or earliest lab/encounter)
  3. Compute sustained declines (>40%, >50%, doubling creatinine)
  4. Check hard endpoints from ClinicalEvent (ESKD, death, etc.)
  5. Apply disease-specific remission rules
  6. Detect proteinuria relapse
  7. Update PatientOutcome (denormalized row)
```

---

## 11. Biostatistics & Survival Analysis

### All Implemented in Pure Python (No External Libraries)

#### Kaplan-Meier Survival Analysis

- Survival estimates with **Greenwood confidence intervals**
- Median survival calculation
- S(t) at any time point
- **Incidence rate** (person-time method)
- **SVG plot generation** for visual Kaplan-Meier curves
- **Validated against the Freireich 6-MP dataset** (published benchmark)

#### Nelson-Aalen Cumulative Hazard

- Non-parametric cumulative hazard estimator
- Complementary to KM survival estimates

#### Log-Rank Test

- Two-group comparison of survival curves
- Chi-square statistic + p-value
- **Validated via score-test / log-rank identity**

#### Cox Proportional Hazards Regression

- Multivariable Cox PH model
- **Newton-Raphson** optimization on Breslow partial likelihood
- Mean-centered covariates
- Hazard ratios with 95% CI + p-values
- Global score test at beta=0
- **Covariate specs**: age, female, diabetes, baseline_egfr, baseline_upcr, drug:<class>

#### Competing Risks (CIF)

- **Aalen-Johansen** cause-specific cumulative incidence
- Variance estimation
- Pointwise z-test of CIF difference between groups
- Validated to reduce to 1-KM when no competing events present

#### Linear Mixed-Effects Model (eGFR Slope)

- **Laird-Ware EM** algorithm
- Random intercept + random slope
- Between-group comparison of eGFR trajectories
- Individual patient slope estimation

#### Multiple Imputation (MICE)

- **Predictive Mean Matching** (PMM)
- M imputations with configurable iterations
- **Rubin's rules** for pooling estimates and variances

#### Linear Algebra Library

Custom pure-Python matrix operations:
- Matrix multiplication, transpose, inverse (Gauss-Jordan)
- Outer product, scalar multiplication
- Matrix addition, identity, zeros

### Cohort Analysis Dimensions

| Dimension | Example | Description |
|-----------|---------|-------------|
| `diabetes` | yes/no/t1/t2 | By diabetes status |
| `diagnosis` | igan/mn/fsgs/etc. | By GN diagnosis |
| `cohort` | By patient category | By research cohort |
| `drug:<class>` | drug:sglt2i | By drug class exposure |
| `biomarker:pla2r_response` | early/late | By PLA2R response |
| `study:<code>` | study:ADVANCED-DKD | By trial arm |

### Analysis Endpoints

| Endpoint | Type |
|----------|------|
| `composite_kidney_event` | "Bad" event (higher = worse) |
| `eskd` | Hard endpoint |
| `death` | All-cause mortality |
| `sustained_40_decline` | Function decline |
| `sustained_50_decline` | Function decline |
| `complete_remission` | "Good" event (1-KM = cumulative incidence) |
| `partial_remission` | "Good" event |
| `any_remission` | "Good" event |
| `igan_proteinuria_response` | IgAN-specific |

---

## 12. Biomarker Kinetics

### PLA2R Kinetics (Membranous Nephropathy)

| Field | Description |
|-------|-------------|
| `pla2r_baseline` | Baseline anti-PLA2R level |
| `pla2r_latest` | Most recent level |
| `pla2r_nadir` | Lowest level |
| `pla2r_pct_decline` | Percentage decline from baseline |
| `pla2r_50pct_decline` | Boolean: ≥50% decline achieved |
| `pla2r_50pct_date` / `_days` | Date and days from baseline |
| `pla2r_immunological_remission` | Seroconversion to negative |
| `pla2r_remission_date` | Date of seroconversion |

**Clinical Significance (Study 6)**:
- Early ≥50% anti-PLA2R decline predicts 12-month complete remission
- Immunological remission (seroconversion) precedes proteinuria remission
- Analysis: 2×2 table with sensitivity/specificity/PPV/NPV/relative risk

### Complement Recovery (LN/C3G)

| Field | Description |
|-------|-------------|
| `c3_recovered` | C3 returned to normal |
| `c3_recovered_date` | Date of normalization |
| `c4_recovered` | C4 returned to normal |
| `c4_recovered_date` | Date of normalization |

### Anti-dsDNA (Lupus Nephritis)

| Field | Description |
|-------|-------------|
| `dsdna_baseline` | Baseline anti-dsDNA |
| `dsdna_latest` | Most recent level |
| `dsdna_normalized` | Returned to normal range |
| `dsdna_normalized_date` | Date of normalization |

---

## 13. Safety & Adverse Events

### Adverse Event Categories

| Category | Subtypes |
|----------|----------|
| **Infection** | TB, PJP, CMV, zoster, pneumonia, sepsis, fungal, bacterial |
| **Steroid Toxicity** | Hyperglycemia, osteoporosis, AVN, cataract, Cushingoid |
| **Hematologic** | Leukopenia, thrombocytopenia, anemia |
| **Hepatic** | Drug-induced liver injury |
| **Other** | Nausea, GI, dermatologic, neurological |

### Severity Grading

| Grade | Severity |
|-------|----------|
| G1 | Mild |
| G2 | Moderate |
| G3 | Severe |
| G4 | Life-threatening |
| G5 | Fatal |

### Serious Adverse Event (SAE) Criteria

Auto-flagged when:
- Hospitalization required, OR
- Grade 4 or Grade 5 severity

### Drug Attribution

Each AE can be attributed to a suspected drug with relatedness assessment:
- unrelated / unlikely / possible / probable / definite

### Safety Analytics

| Endpoint | Description |
|----------|-------------|
| `/safety/summary/` | Counts by category/severity/infection type |
| `/safety/infection-incidence/` | Incidence density per 100 patient-years by group |
| `/safety/study/<code>/` | Per-arm SAE/infection/death counts for DSMB |

---

## 14. Clinical Decision Support

### Knowledge Base (Rule Engine)

| Component | Description |
|-----------|-------------|
| `GuidelineSource` | Reference guidelines (KDIGO, etc.) with versioning |
| `KnowledgeBaseEntry` | Structured rules with conditions, weights, explanations |

**Rule Structure**:
```json
{
  "conditions": [{"field": "...", "operator": "...", "value": "..."}],
  "weight": 0.8,
  "explanation": "Clinical rationale"
}
```

**Evidence Grades**: 1 (highest), 2, NG (not graded), OP (expert opinion)

### Disease Profiles (9 Profiles)

The decision engine evaluates patients against 9 glomerular disease profiles:

1. **IgA Nephropathy (iga)**
2. **Membranous Nephropathy (membranous)**
3. **Minimal Change Disease (mcd)**
4. **Focal Segmental Glomerulosclerosis (fsgs)**
5. **Lupus Nephritis (lupus)**
6. **ANCA-Associated Vasculitis (anca)**
7. **Anti-GBM Disease (antiGbm)**
8. **Infection-Related GN (infectionRelated)**
9. **C3 Glomerulopathy (c3)**

### Decision Output

| Field | Description |
|-------|-------------|
| `phenotype` | Classified clinical pattern |
| `urgency_level` | Urgency assessment |
| `urgency_tone` | urgent / nephrotic / nephritic |
| `urgency_reasons` | Reasons for urgency (JSON) |
| `ranked_differential` | Ranked differential diagnosis |
| `next_steps` | Suggested clinical actions |
| `traceability` | KB entries applied (explainability) |
| `explanation` | Human-readable explanation |

### Timeline (Cross-Domain Aggregation)

`TimelineEvent` aggregates events from all domains:
- **Domains**: patient, encounter, clinical, lab, biopsy, decision
- Chronological view with details and source links

---

## 15. Study Design & Randomization

### Embedded Trial Platform

The registry doubles as a clinical trial platform:

#### Study Configuration

| Field | Description |
|-------|-------------|
| `code` | Study identifier (e.g., "ADVANCED-DKD-IGAN") |
| `study_type` | observational / quasi_experimental / rct |
| `status` | planning / recruiting / active / closed |
| `randomization_scheme` | none / simple / block / stratified_block |
| `block_multipliers` | Block size multipliers |
| `stratify_by` | Stratification factors |
| `random_seed` | Reproducible allocation sequence seed |
| `requires_trial_consent` | Consent gate for enrollment |

#### Randomization Schemes

| Scheme | Description |
|--------|-------------|
| **Simple** | Pure random allocation |
| **Block** | Permuted blocks of fixed size |
| **Stratified Block** | Blocks within strata (stratified permuted-block) |

#### Stratification Factors

| Factor | Values |
|--------|--------|
| `diabetes` | yes / no |
| `egfr_stratum` | ≥30 / <30 |
| `proteinuria_range` | nephrotic / non-nephrotic |
| `gn_subtype` | disease-specific |
| `sex` | M / F |

#### Eligibility Screening

Pluggable per study code:
- `ADVANCED-DKD-IGAN`: IgAN-specific criteria
- `HCQ-IgAN-advanced`: HCQ trial criteria

#### Study Arms

- Multiple arms per study with allocation ratios
- `is_control` flag for reference arm
- CONSORT-style funnel visualization at `/studies/<code>/dashboard/`

#### Enrollment Workflow

```
enroll(study, patient):
  1. Screen eligibility → (eligible, reasons)
  2. Gate on trial consent → has_consent(patient, "trial")
  3. Compute stratification stratum
  4. Generate deterministic allocation sequence
  5. Assign arm with provenance (stratum, position, who/when)
  6. Audit enrollment
```

### Analysis by Study Arm

```bash
# Intention-to-treat KM + log-rank
/analytics/cohort/survival/?group_by=study:<code>&endpoint=composite_kidney_event

# Adjusted hazard ratios
/analytics/cohort/cox/?group_by=study:<code>&covariates=age,diabetes,drug:sglt2i

# Per-arm DSMB safety tabulation
/safety/study/<code>/
```

---

## 16. Scheduling & Follow-Up

### Protocol Visit Schedule

| Timepoint | Kind | Description |
|-----------|------|-------------|
| Week 1 | Early safety | Immunosuppression safety check |
| Week 2 | Early safety | Immunosuppression safety check |
| Week 4 | Early safety | Immunosuppression safety check |
| Month 1 | Routine | First scheduled follow-up |
| Month 3 | Routine | |
| Month 6 | Routine | |
| Month 9 | Routine | |
| Month 12 | Routine | |
| Month 18, 24, 30, 36, 42, 48, 54, 60 | Routine | 6-monthly to 5 years |

### Scheduling Logic

- **Clinic day**: Tuesday (configurable)
- **Session capacity**: 15 patients per session
- **Visit window**: ±7 days from target date
- **Overflow**: If Tuesday is full, assign next available clinic day in-window
- **Immunosuppression monitoring**: Additional early safety visits

### Visit Worklists

| Endpoint | Purpose |
|----------|---------|
| `/scheduling/due/` | Visits due today |
| `/scheduling/overdue/` | Overdue visits |
| `/scheduling/roster/?date=` | Clinic day roster + capacity headroom |
| `/scheduling/monitoring/<patient_id>/` | Agent-specific monitoring labs |

### Lab Monitoring Schedule

For patients on active immunosuppression:
- Drug-specific monitoring requirements
- Automated alerts for overdue monitoring

---

## 17. Audit Trail & Consent

### Audit Log

Every create/update/delete of clinical models is captured:

| Field | Description |
|-------|-------------|
| `model_label` | e.g., "prescriptions.Prescription" |
| `object_pk` | Record ID |
| `action` | create / update / delete |
| `field_name` | Changed field (updates only) |
| `old_value` / `new_value` | Per-field diff |
| `changed_by` | Authenticated user |
| `change_reason` | Optional reason (from X-Change-Reason header) |

**Attribution**:
- Web requests: Automatic via `AuditMiddleware`
- Scripts/shells: Manual via `acting_as(user, reason="...")` context manager

### Consent Management

| Type | Purpose | Gate |
|------|---------|------|
| `registry` | Standard enrollment | General participation |
| `biobank` | Sample storage | Biopsy sample use (disabled v2) |
| `genetic` | Genetic testing | Future use |
| `imaging` | Image sharing | Biopsy image access |
| `trial` | Clinical trial | Study enrollment + randomization |

**Versioning**:
- `grant_consent()` supersedes prior current consent of same type
- DB constraint: one current consent per type per patient
- `withdraw_consent()` revokes current consent
- Full consent history preserved

### Exclusion from Audit

Append-only tables are intentionally **not** audited:
- `LabResult` — provenance in rows themselves
- `PatientOutcome` — computed, not entered

---

## 18. Research Data Export

### Denormalized Dataset

One-row-per-patient dataset pulling from all domains:

| Domain | Columns |
|--------|---------|
| Demographics | patient_id, sex, age, enrollment_date |
| Baseline | BMI, diabetes, BP, presentation |
| Baseline Labs | creatinine, eGFR, proteinuria, HbA1c |
| Pathology | diagnosis, MEST-C, ISN/RPS, FSGS variant |
| Drug Exposure | Ever-exposed drug-class flags (0/1) |
| Outcomes | eGFR slope, remission, time-to-remission, ESKD/death/composite |
| Biomarkers | PLA2R kinetics, complement, anti-dsDNA |
| Safety | AE counts by category |

### Export Formats

| Format | Library | Notes |
|--------|---------|-------|
| CSV | Python csv | Simple text export |
| Excel (.xlsx) | openpyxl | With formatting + data dictionary sheet |
| SPSS (.sav) | pyreadstat | Variable labels, value labels, measurement levels |

### Data Dictionary

Excel export includes a `data_dictionary` sheet (Appendix C) with:
- Column name, data type, units, description
- Makes shared datasets self-documenting

### De-identification

- **Default**: De-identified (Study ID only; no name/phone/reg)
- **Identified**: Gated to `data_manager` role
- CLI: `python manage.py export_dataset --format xlsx --out research.xlsx`

---

## 19. Glomerular Disease Taxonomy

### Primary Glomerular Diseases

| Disease | Key Features | Treatment Paradigm |
|---------|-------------|-------------------|
| **IgA Nephropathy** | Mesangial IgA deposits; hematuria + proteinuria | Supportive + SGLT2i + ± steroids (Oxford-guided) |
| **Membranous Nephropathy** | Subepithelial deposits; anti-PLA2R antibodies | Rituximab / cyclophosphamide + steroids |
| **FSGS** | Segmental sclerosis; nephrotic syndrome | Calcineurin inhibitors / steroids |
| **MCD** | Minimal changes on LM; nephrotic syndrome | Steroids (excellent response) |

### Secondary Glomerular Diseases

| Disease | Key Features | Treatment Paradigm |
|---------|-------------|-------------------|
| **Lupus Nephritis** | Immune complex GN; ISN/RPS classification | Mycophenolate / cyclophosphamide + steroids |
| **ANCA Vasculitis** | Pauci-immune GN; c-ANCA/p-ANCA | Rituximab / cyclophosphamide + steroids |
| **Anti-GBM Disease** | Linear IgG on IF; Goodpasture's | Plasma exchange + cyclophosphamide + steroids |
| **Infection-Related GN** | Post-infectious; hump-shaped deposits | Treat underlying infection |
| **C3 Glomerulopathy** | Complement-mediated; C3 dominant | Complement inhibitors (emerging) |

### Presentation Syndromes

| Syndrome | Key Features |
|----------|-------------|
| Nephrotic | Proteinuria >3.5 g/day, edema, hypoalbuminemia, hyperlipidemia |
| Nephritic | Hematuria, RBC casts, hypertension, reduced GFR |
| Rapidly Progressive | Rapid GFR decline, crescents on biopsy |
| Mixed | Overlapping nephrotic + nephritic features |

---

## 20. Protocol Alignment

### GN Master Protocol v2 (Bangladesh)

The system is aligned to `GN_Master_Protocol_v3_Bangladesh_revised.docx`:

| Protocol Section | GDES Implementation |
|-----------------|---------------------|
| §7.3 Central pathology review | `pathology` app with local/central/adjudication workflow |
| §7.6 Follow-up scheduling | `scheduling` app: Tuesday clinics, ±7-day windows, 15 slots |
| §7.7 Immunosuppression monitoring | `scheduling/services/monitoring.py` |
| §9.1 Disease-specific remission | `analytics/services/remission.py` |
| §9.3 Biomarker kinetics | `biomarkers` app: PLA2R, complement, anti-dsDNA |
| §9.4 Adverse events | `safety` app: infection, steroid toxicity, SAE tracking |
| §10.3 eGFR slope | `analytics/services/mixed_model.py`: Laird-Ware EM |
| §10.4 Competing risks | `analytics/services/competing_risks.py`: Aalen-Johansen |
| §11.3 Inter-observer agreement | `pathology/services/agreement.py`: Cohen's κ |
| §11.5 Data governance | De-identified by default; identified export gated |
| §13.5 Data protection | Role-based access; audit trail; consent gating |

### Randomization Stratification (Protocol §10.1)

- `egfr_30`: ≥30 vs <30 mL/min/1.73m²
- `proteinuria_range`: nephrotic vs non-nephrotic

### Protocol Changes

- **Biobanking removed in v2**: `biobank` app disabled (code retained)
- **Adult-only eligibility**: ≥18 years
- **Disease-specific remission**: Different thresholds per GN subtype
- **24-h UTP preferred**: Spot UPCR as ~g/day fallback

---

*End of DOMAIN_SUMMARY.md*

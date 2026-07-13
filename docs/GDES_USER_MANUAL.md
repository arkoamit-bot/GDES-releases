# GDES Version 5.0

## Comprehensive User Manual & End-to-End Clinical Workflow Guide

**Glomerular Disease Expert System**

BIRDEM Nephrology · Dhaka, Bangladesh

---

# What's New in GDES Version 5.1

GDES 5.1 delivers a **fully reliable Clinical Decision Support (CDS) layer** — all P0-critical bugs resolved, field-name schema drifts corrected, and the entire CDS pipeline validated through a new integration test suite.

## Key Improvements

### Clinical Decision Support Now Reliable

The three CDS engines — drug toxicity monitoring, treatment failure detection, and relapse detection — are now fully operational. Previously, these modules could silently fail or produce incorrect results due to:

- **Wrong field names:** `numeric_value` → `value_numeric` (the correct field) across 7 query locations
- **Wrong medication source:** The toxicity engine now reads from `TreatmentExposure` (research-grade medication episodes) instead of the broken `Prescription` model query
- **Inverted alert logic:** Low-value-is-worse tests (WBC for MMF/cyclophosphamide, IgG for rituximab) now use `≤` thresholds instead of `≥`, eliminating false negatives for cytopenias and hypogammaglobulinemia
- **Missing disease source:** The diagnosis passed to CDS now reads from the `differential[0].disease_id` field instead of the non-existent `disease_trajectory.get("disease_id")`

Clinicians can now trust the toxicity, failure, and relapse alerts presented on the patient management page.

### Human-Readable Disease Names

The differential diagnosis view now shows proper disease names (e.g. "IgA Nephropathy / IgA Vasculitis Nephritis") instead of raw rule IDs (e.g. "TEST-IGA-001"). This fix applies across all CDS output — no more confusing internal identifiers in clinical context.

### Cleaner UI — No More Zero-Confidence Clutter

Diagnoses with a 0.0 confidence score are now hidden from the patient detail page. Only rules with meaningful evidence are displayed, reducing visual noise.

### Error Transparency

CDS failures are no longer silently swallowed. Each CDS generator block logs exceptions to the Django error log with full tracebacks, and errors are surfaced in a `cds_errors` list passed to the template context — enabling the UI to show meaningful error states instead of blank panels.

### Integration Test Validation

A new `test_cds_integration.py` suite (10 tests) validates every CDS pathway against real ORM data — no mocks. The full test suite runs **205 tests passing** with zero regressions.

## Summary for Clinicians

The CDS tools you see on the patient detail page — Management Plan, Monitoring Plan, and Follow-up Plan — now produce **accurate, reliable output** backed by automated test validation. If a CDS module encounters an error, it is logged for rapid investigation rather than silently dropped.

---

---

# Table of Contents

- [Chapter 1 – Introduction](#chapter-1--introduction)
- [Chapter 2 – System Overview](#chapter-2--system-overview)
- [Chapter 3 – Complete Patient Journey](#chapter-3--complete-patient-journey)
  - [Step 1 – Patient Registration](#step-1--patient-registration)
  - [Step 2 – Baseline Assessment](#step-2--baseline-assessment)
  - [Step 3 – Laboratory Entry](#step-3--laboratory-entry)
  - [Step 4 – Biopsy](#step-4--biopsy)
  - [Step 5 – Clinical Reasoning](#step-5--clinical-reasoning)
  - [Step 6 – Treatment Planning](#step-6--treatment-planning)
  - [Step 7 – Automatic Follow-up Planning](#step-7--automatic-follow-up-planning)
  - [Step 8 – Automatic Patient Management](#step-8--automatic-patient-management)
  - [Step 9 – Relapse Scenario](#step-9--relapse-scenario)
  - [Step 10 – Long-term Follow-up](#step-10--long-term-follow-up)
- [Automated Management](#automated-management)
- [Automated Follow-up Engine](#automated-follow-up-engine)
- [Research Workflow](#research-workflow)
- [Clinical Decision Support](#clinical-decision-support)
- [Practical Examples](#practical-examples)
- [Appendices](#appendices)

---

# Chapter 1 – Introduction

## What is GDES?

The **Glomerular Disease Expert System (GDES)** is a comprehensive clinical information platform purpose-built for the management of glomerular diseases. Developed at BIRDEM Nephrology in Dhaka, Bangladesh, GDES integrates patient registry, clinical decision support, automated follow-up, and research capabilities into a single, unified workflow.

GDES is not merely a database where patient information is stored. It is an **intelligent clinical platform** that:

- Guides clinicians through structured data collection
- Provides real-time diagnostic decision support
- Automatically generates follow-up plans based on disease and risk
- Detects clinical deterioration and escalates care
- Continuously updates research-quality datasets without duplicate data entry

## Purpose of the Platform

The primary purpose of GDES is to improve clinical outcomes for patients with glomerular disease through:

1. **Structured, guideline-driven care** — ensuring every patient receives consistent, evidence-based management
2. **Automated clinical reasoning** — helping clinicians recognise disease patterns and avoid diagnostic delays
3. **Systematic follow-up** — reducing loss to follow-up through automated scheduling and escalation
4. **Seamless research integration** — enabling high-quality observational research without additional data collection burden

## Target Users

| User Role | Primary Activities |
|-----------|-------------------|
| Nephrologist | Clinical assessment, treatment decisions, interpretation of clinical reasoning output |
| Fellow / Resident | Daily patient management, data entry, follow-up visits |
| Medical Officer | Initial assessment, laboratory entry, prescription generation |
| Research Coordinator | Study enrolment, data quality monitoring, research dataset export |
| Nurse | Vital signs, medication administration, patient communication |
| Data Manager | Data quality, audit trail review, system administration |
| Hospital Administrator | Dashboard oversight, compliance monitoring, reporting |

## Clinical Objectives

- Standardise the assessment and management of glomerular diseases
- Provide real-time decision support at the point of care
- Ensure timely follow-up through automated scheduling
- Detect disease progression and relapse early
- Maintain a complete, auditable clinical record for every patient

## Research Objectives

- Generate research-quality datasets as a byproduct of clinical care
- Enable survival analysis, Cox regression, and longitudinal outcome studies
- Support registry-embedded clinical trials with randomisation and eligibility screening
- Provide publication-ready data exports for multicentre collaboration

## How GDES Differs from a Traditional Registry

| Feature | Traditional Registry | GDES |
|---------|---------------------|------|
| Data entry | Separate research entry | Captured during clinical care |
| Decision support | None | Real-time reasoning engine |
| Follow-up | Manual tracking | Automated scheduling with escalation |
| Prescriptions | Not included | Integrated bilingual prescription printing |
| Audit trail | Limited | Per-field change history |
| Trial platform | Separate system | Built-in randomisation and eligibility |
| Knowledge integration | None | Knowledge base with active rules |

GDES combines five capabilities into a single platform:

```
┌─────────────────────────────────────────────────────┐
│                    GDES Platform                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Clinical  │  │ Decision │  │   Knowledge      │  │
│  │ Registry  │  │ Support  │  │    Engine        │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │ Patient   │  │ Clinical │  │ Rule matching    │  │
│  │ data      │  │ reasoning│  │ Differential     │  │
│  │ Encounters│  │ Risk     │  │ Treatment recs   │  │
│  │ Labs      │  │ assessment│ │ Information gaps │  │
│  │ Pathology │  │ Care     │  │                  │  │
│  │           │  │ pathway  │  │                  │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │ Automated │  │ Research  │  │   Prescription   │  │
│  │ Follow-up │  │ Platform │  │    Engine        │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │ Scheduling│  │ Analytics│  │ Reconciliation   │  │
│  │ Escalation│  │ Exports  │  │ Safety checks    │  │
│  │ Worklist  │  │ Trials   │  │ Bilingual PDF    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

# Chapter 2 – System Overview

## Dashboard

The dashboard is the home screen of GDES. It provides:

- **Registry at a glance** — total patients, active patients, recent registrations, pending baseline assessments
- **Follow-up Engine** — pending tasks, overdue items, high-priority alerts
- **Follow-up worklist** — visits due now and overdue, updated automatically every 60 seconds
- **Cohort kidney trend** — mean eGFR and proteinuria by month across the entire registry
- **Quick actions** — register a patient, open analytics, export data

> **Clinical Tip:** Check the Follow-up worklist at the start of each clinic day. It shows every patient who is due or overdue for a visit, prioritised by urgency.

## Patient Registry

The patient registry is the central hub of GDES. Every patient has a unique Study ID and a permanent record that accumulates all clinical data over time.

**Key features:**
- Patient search by ID, name, or phone number
- Registration with demographics, comorbidities, and consent
- Automatic calculation of age, CKD-EPI eGFR, and KDIGO stage
- Visual workflow progress strip showing completion status

**Automatic processes on registration:**
- Audit log entry created
- Research eligibility checked
- Timeline entry generated
- Follow-up engine initialised

## Clinical Encounters

Every patient contact is recorded as a Clinical Encounter. This is the central data structure around which all other modules are organised.

**Types of encounters:**
- Initial consultation
- Follow-up visit
- Unscheduled visit (for acute issues)
- Telephone consultation

Each encounter captures:
- Date and type
- Blood pressure, weight, edema grade
- Clinician response assessment (complete remission, partial remission, stable disease, no response)
- Disease phase (active disease, remission, relapse, etc.)
- Next scheduled visit date

**Automatic processes:**
- eGFR and proteinuria trend chart updated
- Disease phase may be automatically updated
- Clinical reasoning triggered
- Follow-up plan reassessed

## Clinical Assessment

The baseline assessment is completed at enrolment and captures:
- Chief complaint and presenting symptoms
- Syndrome classification (nephrotic syndrome, nephritic syndrome, rapidly progressive GN, etc.)
- Full vital signs and anthropometrics
- Comorbidity assessment

**Automatic calculations:**
- BMI (with Asian-specific categories)
- Body surface area (BSA)
- CKD-EPI 2021 eGFR
- KDIGO stage (G1–G5)
- Proteinuria category

### Laboratory

GDES captures all laboratory data relevant to glomerular disease management.

**Key tests:**
- Creatinine and eGFR
- Albumin
- 24-hour urine protein (UTP)
- Urine protein-to-creatinine ratio (UPCR)
- Urine albumin-to-creatinine ratio (UACR)
- Complete blood count (CBC)
- Complement C3, C4
- Autoantibodies (ANA, anti-dsDNA, ANCA, anti-PLA2R)
- Gd-IgA1
- HbA1c (for diabetic patients)

**Automatic actions:**
- Reference range checking with critical value alerts
- Longitudinal trend chart updated
- eGFR slope computed after sufficient data points
- AKI detection (KDIGO criteria)
- CKD progression detection
- Timeline updated
- Research dataset synchronised

> **Clinical Tip:** Trends matter more than single values. The lab trend chart on the patient overview shows eGFR and proteinuria together, making it easy to assess disease trajectory at a glance.

### Pathology

GDES supports structured entry of kidney biopsy pathology.

**Key features:**
- Biopsy date, laterality, adequacy assessment
- Light microscopy, immunofluorescence, and electron microscopy findings
- Disease-specific scoring systems:
  - Oxford MEST-C for IgA Nephropathy
  - ISN/RPS classification for Lupus Nephritis
  - Columbia classification for FSGS
  - PLA2R staining for Membranous Nephropathy
- Central review workflow with concordance tracking

**Automatic actions on biopsy entry:**
- Disease classification assigned
- Knowledge engine activated with disease-specific rules
- Clinical reasoning triggered
- Timeline updated
- Research dataset updated

## Clinical Reasoning

The Clinical Reasoning module is one of GDES's most powerful features. It automatically analyses every patient's complete data profile and generates:

- **Differential diagnosis** — ranked list of possible diagnoses with confidence scores
- **Risk assessment** — progression risk, relapse risk, kidney survival estimate
- **Care pathway** — current disease stage, treatment recommendations, care gaps
- **Information gaps** — missing data that would improve diagnostic accuracy

The reasoning engine is rule-based, drawing on a curated knowledge base of glomerular disease patterns. Each rule is evidence-graded and linked to guideline references.

> **Clinical Tip:** The Clinical Reasoning tab is available for every registered patient. Check it after each data entry to see if new information has changed the differential or risk assessment.

## Decision Support

The Decision Support module extends Clinical Reasoning by providing:

- Evidence grades for each recommendation
- Specific guideline references (KDIGO, ISN, etc.)
- Treatment suggestions linked to disease type and phase
- Drug monitoring requirements based on active therapy
- Drug-drug interaction warnings
- Contraindication alerts

**How it works:**
1. Patient data is analysed
2. Knowledge base rules are matched
3. Recommendations are generated with confidence levels
4. Clinician reviews and accepts, modifies, or overrides
5. Overrides are recorded in the audit log with reason

## Treatment

GDES tracks treatment through two complementary systems:

**Treatment Exposures** — Research-grade medication episodes with start/stop dates, dose, regimen, and stop reason. These are automatically reconciled whenever a prescription is finalised.

**Prescriptions** — Clinical prescription documents that are printed for the patient. Each prescription can have multiple items with dose, frequency, and duration.

**Key features:**
- Drug selection from a curated formulary
- Dose calculation assistance
- Contraindication checking
- Drug interaction warnings
- Monitoring requirements display

**Automatic reconciliation on prescription finalisation:**
- New drug without existing exposure → episode opened
- Drug dropped from regimen → episode closed with stop reason
- Dose or regimen changed → old episode closed, new one opened (episode split)
- Unchanged drug → episode continued

## Prescriptions

GDES generates bilingual (English and Bengali) prescription PDFs suitable for printing and direct patient use.

**Prescription features:**
- Versioned (each modification creates a new version)
- Immutable once finalised (medico-legal)
- Cryptographic hash for tamper detection
- Drug name, dose, frequency, duration, and indications
- Clinician name and signature line
- Hospital header and patient identification

**Workflow:**
1. Create prescription with items
2. Review and modify as needed
3. Finalise (makes immutable and triggers reconciliation)
4. Preview on screen
5. Download PDF for printing

> **Clinical Tip:** The prescription *is* the follow-up visit record. Finalising a prescription simultaneously generates the visit note, updates the medication list, and triggers the follow-up engine.

## Follow-up

The Follow-up module is an automated engine that manages every patient's long-term care schedule.

**Key capabilities:**
- Disease-specific follow-up protocols (IgAN, MCD, FSGS, MN, LN, ANCA vasculitis, anti-GBM, C3G, MPGN, DDD)
- Risk-stratified follow-up intervals (high risk → shorter interval)
- Automated task generation (visit due, lab due, medication monitoring, safety monitoring, research visit, referral due, patient contact)
- Multi-level escalation for overdue tasks
- Clinician worklist dashboard

**For a detailed explanation, see [Automated Follow-up Engine](#automated-follow-up-engine).**

## Timeline

Every patient has a chronological timeline of all significant events:

- Registration and consent
- Baseline assessment
- Follow-up visits
- Laboratory results
- Biopsies
- Hospital admissions
- Relapses
- Medication changes
- Outcome computations

The timeline is automatically populated and updated — no manual entry required.

## Knowledge Base

The Knowledge Base is the curated repository of glomerular disease knowledge that powers the Clinical Reasoning engine.

**Contents:**
- Disease definitions and diagnostic criteria
- Clinical feature-disease associations
- Diagnostic rules with evidence grading
- Treatment guidelines
- Follow-up protocol definitions

The Knowledge Base is accessible via the admin interface and can be extended by authorised users as new evidence emerges.

## Research

GDES treats research as a byproduct of clinical care. Every data point entered during routine clinical work is automatically available for research.

**Research capabilities:**
- **Outcome computation** — eGFR slope, remission status, time to remission, ESKD, death, composite endpoints
- **Survival analysis** — Kaplan-Meier curves with Greenwood confidence intervals, log-rank testing, incidence rates
- **Cox proportional hazards** — multivariable regression
- **Competing risks analysis** — cumulative incidence functions
- **eGFR slope analysis** — mixed-effects models
- **Research dataset export** — one-row-per-patient denormalised dataset in CSV or Excel
- **Registry-embedded trials** — study definition, arm randomisation, eligibility screening, DSMB reporting

> **Clinical Tip:** To compute outcomes for a patient, open their record and click "Compute now" on the Outcomes card. This triggers the full outcome engine and updates the research dataset.

## Administration

The Administration section provides:

- User management (invite, roles, permissions)
- Audit log review
- System configuration
- Backup management
- Knowledge base management (for authorised users)

---

# Chapter 3 – Complete Patient Journey

This chapter follows a realistic patient through the entire GDES workflow from first presentation to long-term follow-up.

## Case Introduction

**Mr. Rahman** is a 35-year-old male who presents to the BIRDEM Nephrology clinic with:

- Progressive bilateral lower limb edema over 3 weeks
- Fatigue and reduced exercise tolerance
- Foamy urine noticed by the patient
- Blood pressure of 148/92 mmHg at presentation
- No prior kidney disease
- No diabetes, no hypertension history
- No family history of kidney disease

Initial investigations ordered by the referring physician show:
- Serum creatinine: 1.6 mg/dL (eGFR 48 mL/min/1.73m²)
- Serum albumin: 2.8 g/dL
- 24-hour urine protein: 3.8 g/day
- Urinalysis: 2+ protein, 3+ blood, dysmorphic RBCs
- HbA1c: 5.2% (non-diabetic)

---

## Step 1 – Patient Registration

### Creating the Patient Record

1. From the Dashboard, click **"Register New Patient"** in the task cards.
2. The registration form opens with the following fields:

**Demographics Section:**
- Full name: *Md. Rahman*
- Age / Date of birth: *15-Jan-1991*
- Sex: *Male*
- Phone number: *017XXXXXXXX*
- Address: *Dhaka, Bangladesh*
- Hospital registration number (if available)

**Medical History Section:**
- Diabetes status: *None*
- Hypertension status: *Yes (newly diagnosed)*
- Prior kidney disease: *No*
- Family history of kidney disease: *No*

3. Click **Save** to create the record.

### Automatic Actions on Registration

Once the patient is saved, GDES performs several actions automatically:

```
Registration Saved
│
├─► Audit Log: "Patient registered by Dr. Khan"
│
├─► Research Eligibility: Checked against active studies
│
├─► Timeline: "Patient registered" entry created
│
├─► Follow-up Engine: Initialised (default protocol)
│
├─► Clinical Reasoning: Pending (waiting for baseline data)
│
└─► Patient ID: A1-001 assigned
```

### Consent

After registration, navigate to the **Consent** tab to manage consent:

1. Click **"Manage"** in the Consent tab.
2. Review each consent type:
   - Registry participation
   - Biobank sample storage
   - Study enrolment (separate for each study)
3. For each, select **"Granted"** and enter the consent date.
4. Click **Save**.

> **Clinical Tip:** Consent can be withdrawn at any time. Withdrawn consents are recorded in the audit log. For biobank consent, withdrawal means existing samples are retained but no new samples are collected.

### Patient Record After Registration

After registration, the patient detail page shows:

- **Workflow progress:** Registration ✅ complete
- **Status badge:** "Registered"
- **Summary cards:** Demographics, baseline (pending), outcomes (pending)
- **Tabs:** Overview, Clinical Reasoning, Visits, Prescriptions, Labs, Safety, Biopsies, Research, Consent, Audit Log

---

## Step 2 – Baseline Assessment

### Completing the Baseline Form

From the patient detail page, click **"Baseline"** in the Stage 1 actions bar.

The baseline assessment form captures:

**Clinical Examination:**
- Date of assessment
- Systolic BP: *148 mmHg*
- Diastolic BP: *92 mmHg*
- Weight: *68 kg*
- Height: *168 cm*
- Edema grade: *2+ (moderate, bilateral lower limb)*
- Chief complaint: *Progressive edema*

**Syndrome Classification:**
- Presentation syndrome: *Nephrotic syndrome*

**Comorbidities:**
- Hypertension: *Yes (newly diagnosed)*
- Diabetes: *No*
- Other: *None*

### Automatic Calculations

When the form is saved, GDES automatically computes:

| Calculation | Result | Interpretation |
|------------|--------|----------------|
| BMI | 24.1 kg/m² | Overweight (Asian criteria) |
| BSA | 1.77 m² | Normal |
| eGFR (CKD-EPI 2021) | 48 mL/min/1.73m² | CKD G3b |
| KDIGO stage | G3b A3 | High risk |
| Proteinuria category | 3.8 g/day | Nephrotic range |

### What Happens Next

```
Baseline Assessment Saved
│
├─► Audit Log: "Baseline assessment recorded by Dr. Khan"
│
├─► eGFR: Automatically calculated and stored
├─► CKD Stage: G3b assigned
├─► KDIGO Risk: "High risk" assigned
│
├─► Timeline: "Baseline assessment" entry created
│
├─► Clinical Reasoning: Triggered (partial data available)
├─► Differential: Preliminary evaluation
├─► Information gaps: Identified
│
├─► Follow-up Engine: Risk assessed for interval determination
├─► Follow-up interval: 90 days (high risk, new patient)
│
└─► Research Dataset: Updated with baseline values
```

The workflow progress now shows:
- Registration ✅
- Baseline ✅
- Prescription ❌ pending
- Follow-up ❌ pending
- Outcomes ❌ pending

---

## Step 3 – Laboratory Entry

Laboratory results can be entered in two ways:

1. **At a baseline or follow-up visit** — using the lab section of the visit form
2. **Standalone** — using the "Enter results" link in the Follow-up stage bar

### Entering Initial Labs

For Mr. Rahman's initial presentation, the following labs were ordered and are now being entered:

**Core labs (at baseline visit):**
| Test | Result | Unit | Reference Range |
|------|--------|------|----------------|
| Creatinine | 1.6 | mg/dL | 0.7–1.2 |
| eGFR | 48 | mL/min/1.73m² | >90 |
| Albumin | 2.8 | g/dL | 3.5–5.0 |
| 24h UTP | 3.8 | g/day | <0.15 |
| UPCR | 3.2 | g/g | <0.2 |
| Hemoglobin | 12.5 | g/dL | 13–17 |
| Potassium | 4.2 | mmol/L | 3.5–5.0 |

**Autoimmune workup:**
| Test | Result | Interpretation |
|------|--------|----------------|
| C3 | 85 | Normal (80–160 mg/dL) |
| C4 | 28 | Normal (15–45 mg/dL) |
| ANA | Negative | — |
| ANCA | Negative | — |
| Anti-PLA2R | Pending | — |
| Gd-IgA1 | Pending | — |

### Automatic Actions on Lab Entry

```
Lab Results Saved
│
├─► Reference Range Check: All values within range
├─► No critical alerts triggered
│
├─► Trend Chart: First data point added
├─► Future trends will show progression
│
├─► eGFR Slope: Insufficient data (only 1 point)
├─► Will compute after 3+ readings
│
├─► Timeline: "Lab results recorded" entry created
│
├─► Clinical Reasoning: Retriggered with lab data
├─► Differential: Narrowing (low C3 diseases ruled out)
│
├─► Research Dataset: Updated with lab values
│
└─► Follow-up Engine: No change to interval yet
```

> **Clinical Tip:** Lab results are automatically plotted in the trend chart. Access it from the Overview tab of any patient. The chart shows eGFR on the left axis and proteinuria on the right axis, making it easy to see both trends simultaneously.

---

## Step 4 – Biopsy

The clinical presentation (nephrotic syndrome with hematuria, reduced eGFR, negative autoimmune serology) strongly suggests primary glomerulonephritis. Mr. Rahman undergoes a kidney biopsy.

### Entering Biopsy Results

From the patient detail page, click **"Add biopsy"** in the Biopsies tab.

**Biopsy details:**
- Biopsy date: *7 days after registration*
- Laterality: *Left kidney*
- Needle passes: *2*
- Cortex contains: *>10 glomeruli (adequate)*
- Biopsy adequacy: *Adequate*

**Light Microscopy:**
- Glomeruli: *10 of 12 show mesangial hypercellularity*
- Tubules: *Mild tubular atrophy (<25%)*
- Interstitium: *Mild interstitial fibrosis (<25%)*
- Vessels: *Mild arteriosclerosis*

**Oxford MEST-C Scoring:**
| Component | Score | Description |
|-----------|-------|-------------|
| M (Mesangial hypercellularity) | M1 | >50% of glomeruli |
| E (Endocapillary hypercellularity) | E0 | Absent |
| S (Segmental sclerosis) | S0 | Absent |
| T (Tubular atrophy/interstitial fibrosis) | T1 | 25–50% |
| C (Crescents) | C0 | Absent |

**Immunofluorescence:**
- IgA: *3+ (dominant, mesangial)*
- IgG: *Negative*
- IgM: *Trace*
- C3: *2+*
- C1q: *Negative*

**Electron Microscopy:**
- Mesangial electron-dense deposits
- No subepithelial or subendothelial deposits

**Final Diagnosis:**
- Diagnosis: *IgA Nephropathy (Primary)*

### Automatic Actions on Biopsy Entry

```
Biopsy Saved
│
├─► Audit Log: "Biopsy recorded by Dr. Khan"
│
├─► Diagnosis: "IgA Nephropathy, Primary" assigned
│
├─► Disease Classification: Updated to IgA Nephropathy
│
├─► Knowledge Engine: Activated with IgAN-specific rules
├─► IgAN protocol selected for follow-up
│
├─► Timeline: "Biopsy result: IgAN (M1 E0 S0 T1 C0)" entry
│
├─► Clinical Reasoning: Full retrigger with biopsy data
├─► Differential: IgAN confirmed
├─► Risk: IgAN-specific risk assessment
│
├─► Follow-up Engine: Protocol switched to IgAN-specific
├─► Follow-up interval: Recalculated per IgAN protocol
│
└─► Research Dataset: Updated with histopathology data
```

### Workflow Status After Biopsy

The workflow progress strip now shows:
- Registration ✅
- Baseline ✅
- Prescription ❌ (pending)
- Follow-up ❌ (pending)
- Outcomes ❌ (pending)

The Clinical Reasoning tab is now populated with a full analysis.

---

## Step 5 – Clinical Reasoning

After the biopsy, Mr. Rahman's Clinical Reasoning tab is fully populated. Here is what GDES displays:

### Differential Diagnosis

| Disease | Score | Confidence | Source |
|---------|-------|------------|--------|
| **IgA Nephropathy** | 95.0 | 98% | Biopsy confirmed |
| IgA Vasculitis (Henoch-Schönlein) | 45.0 | 40% | No extrarenal features |
| Thin Basement Membrane Nephropathy | 20.0 | 15% | Not consistent with presentation |
| Lupus Nephritis | 10.0 | 5% | ANA negative, C3/C4 normal |

### Risk Assessment

| Risk Factor | Value |
|-------------|-------|
| **Progression Risk** | 35% (5-year) |
| MEST-C T1 score predicts higher risk |
| **Relapse Risk** | Not applicable (new diagnosis) |
| **Kidney Survival Estimate** | 85% at 10 years |

### Information Gaps

- Gd-IgA1 level (not yet resulted)
- Anti-PLA2R (not yet resulted — useful to rule out MN)
- 24-hour BP monitoring (home BP readings)
- Family history of IgAN (specific query)

### Care Pathway

- **Current Stage:** Active disease, newly diagnosed
- **Treatment Recommendations:** 2 recommendations available
- **Care Gaps:** 1 (start RAAS inhibition, assess indication for immunosuppression)

### Disease Trajectory

- **Trend:** Newly diagnosed (insufficient follow-up data for trajectory)
- **Next assessment:** 90 days

> **Clinical Tip:** The Clinical Reasoning analysis updates automatically every time new data is entered. Check it after each visit to see how the risk assessment and recommendations evolve over time.

---

## Step 6 – Treatment Planning

### Reviewing Decision Support Recommendations

Based on Mr. Rahman's clinical profile, GDES generates the following recommendations:

**Recommendation 1 — RAAS Inhibition**
- Agent: *Ramipril 5 mg daily*
- Evidence: *KDIGO 2021, Grade 1B*
- Rationale: *Proteinuria >1 g/day, hypertension, eGFR <60*
- Monitoring: *Creatinine and potassium at 2 weeks*

**Recommendation 2 — Immunosuppression Assessment**
- Indication: *T1 score (tubular atrophy >25%) increases risk of progression*
- Current proteinuria: *3.8 g/day despite optimal RAAS blockade*
- Suggestion: *Consider glucocorticoids*
- Evidence: *TESTING trial (reduced risk of kidney failure)*
- Caution: *Discuss risks (infection, diabetes, bone health)*

### Entering Medications

**Step 1:** Click **"Prescription"** in the Stage 3 actions bar.

**Step 2:** Add prescription items:
| Drug | Dose | Frequency | Duration | Indication |
|------|------|-----------|----------|------------|
| Ramipril | 5 mg | Once daily | Ongoing | Proteinuria, hypertension |
| Atorvastatin | 20 mg | Once daily | Ongoing | Hyperlipidemia (nephrotic) |

**Step 3:** Click **"Finalise"** to complete the prescription.

### Automatic Actions on Prescription Finalisation

```
Prescription Finalised
│
├─► Audit Log: "Prescription v1 finalised by Dr. Khan"
│
├─► Treatment Reconciliation:
├─► Ramipril → New exposure created (start: today)
├─► Atorvastatin → New exposure created (start: today)
│
├─► Safety Checks:
├─► No drug-drug interactions detected
├─► Monitoring requirements noted
│
├─► Follow-up Engine:
├─► Monitoring tasks created:
│   ├─► Serum creatinine + potassium (2 weeks)
│   └─► Lipid profile (3 months)
├─► Next visit scheduled (90 days)
│
├─► Timeline: "Prescription v1: Ramipril, Atorvastatin" entry
│
└─► Research Dataset: Updated with treatment exposure
```

### Prior Medications (Optional)

The **"Prior meds"** button in Stage 3 allows entry of medications the patient was taking before the first GDES prescription. This is important for research-grade exposure history.

For Mr. Rahman, no prior GN-specific medications were taken.

---

## Step 7 – Automatic Follow-up Planning

The Follow-up Engine is one of GDES's most powerful automation features. After Mr. Rahman's data is complete (registration, baseline, labs, biopsy, prescription), the engine generates a comprehensive follow-up plan.

### How the Follow-up Plan is Generated

```
Patient Data → Clinical Profile
│
├─► Disease: IgA Nephropathy
├─► Risk Stratification:
│   ├─► eGFR <60 → +1 point
│   ├─► Proteinuria >1 g/day → +2 points
│   ├─► Hypertension → +1 point
│   ├─► MEST-C T1 → +2 points
│   └─► Total: 6 points → HIGH risk
│
├─► Protocol Selection:
│   ├─► Disease: IgAN-specific protocol selected
│   └─► Risk: HIGH → shorter interval
│
├─► Generated Tasks:
│   ├─► Visit due (108 days)
│   ├─► Lab: creatinine, eGFR, UPCR (2 weeks for safety monitoring)
│   ├─► Lab: full panel (108 days)
│   └─► Medication monitoring: creatinine + K+ (2 weeks)
│
└─► Output → Patient Follow-up Plan
```

### The Follow-up Plan

Mr. Rahman's generated follow-up plan:

| Task | Due Date | Priority | Status |
|------|----------|----------|--------|
| **Safety labs** (creatinine, K+) | 14 days | High | Pending |
| **Follow-up visit** | 108 days | Medium | Pending |
| **Full lab panel** | 108 days | Medium | Pending |
| **Lipid profile** | 3 months | Low | Pending |

### Viewing the Follow-up Plan

The follow-up plan is visible in two places:

1. **Patient Overview** — A "Follow-up Plan" card shows all tasks in a table
2. **Dashboard** — The Follow-up worklist aggregates all pending tasks across all patients

### What If a Visit is Missed?

The escalation engine monitors all tasks. If Mr. Rahman misses his 108-day visit:

| Days Overdue | Escalation Level | Action |
|-------------|------------------|--------|
| 1–14 | Level 1 (Notice) | Task marked overdue, visible in worklist |
| 15–30 | Level 2 (Alert) | Notification to clinician dashboard |
| 31–60 | Level 3 (Warning) | Escalation to clinic coordinator |
| >60 | Level 4 (Critical) | Escalation to department head |

> **Clinical Tip:** Check the Follow-up worklist on the dashboard at the start of each day. Overdue tasks are prioritised by severity. High-risk patients with overdue visits appear at the top of the list.

---

## Step 8 – Automatic Patient Management

This section demonstrates how GDES continuously manages the patient between visits.

### Scenario: New Lab Results Arrive

Mr. Rahman returns for safety labs at 2 weeks. The results show:

| Test | Baseline | 2 Weeks | Change |
|------|----------|---------|--------|
| Creatinine | 1.6 | 1.55 | Slight improvement |
| eGFR | 48 | 50 | Slight improvement |
| Potassium | 4.2 | 4.3 | Stable |
| Blood pressure | 148/92 | 132/84 | Improved (on ramipril) |

### Automatic Processing Chain

```
New Lab Results Entered
│
└─► Step 1: Trend Analysis
    ├─► eGFR: 48 → 50 (stable, no decline detected)
    ├─► Potassium: 4.2 → 4.3 (stable, no hyperkalemia)
    └─► Result: No critical alerts
│
└─► Step 2: Risk Recalculation
    ├─► Progression risk: Stable (no change)
    ├─► Follow-up interval: Unchanged (108 days)
    └─► Result: No change to plan
│
└─► Step 3: Clinical Reasoning
    ├─► Triggers: "Lab results updated"
    ├─► Engine: Reruns with new data
    ├─► Assessment: "Preserved eGFR on RAAS blockade"
    └─► Result: No change to differential
│
└─► Step 4: Follow-up Engine
    ├─► Monitors: All existing tasks
    ├─► Safety lab task: ✓ Completed
    └─► Result: Task marked complete, new tasks generated if needed
│
└─► Step 5: Dashboard Update
    ├─► Overview stats: Recalculated
    ├─► Worklist: Updated
    ├─► Patient trend chart: Updated with new data point
    └─► Result: Dashboard reflects latest status
│
└─► Step 6: Timeline Update
    ├─► Entry: "Lab results recorded"
    └─► Result: Timeline updated
│
└─► Step 7: Research Dataset
    ├─► Outcome engine: May trigger if sufficient data
    ├─► Research dataset: Updated with new values
    └─► Result: Research data always current
```

### 108-Day Follow-up Visit

Mr. Rahman returns for his scheduled follow-up visit. The results show:

| Parameter | Baseline | 108 Days | Change |
|-----------|----------|----------|--------|
| Creatinine | 1.6 | 1.7 | Slight rise |
| eGFR | 48 | 44 | Decline of 4 mL/min |
| 24h UTP | 3.8 g | 2.1 g | Improved (on RAAS blockade) |
| BP | 148/92 | 128/80 | Well controlled |
| Albumin | 2.8 | 3.2 | Improved |
| Weight | 68 kg | 65 kg | Edema resolved |

### Clinical Reasoning Update

- **eGFR slope:** −5.5 mL/min/year (computed from 3 data points)
- **Response:** Partial (proteinuria reduced >50%, but eGFR declining)
- **Assessment:** Consider immunosuppression (proteinuria still >1 g/day despite RAAS blockade, with evidence of progression)

### Updated Follow-up Plan

| Parameter | Before Visit | After Visit |
|-----------|-------------|-------------|
| Follow-up interval | 108 days | 90 days (increased risk) |
| Immunosuppression | Not started | Consider glucocorticoids |
| Next visit | — | 90 days |
| Safety monitoring | Completed | New schedule for immunosuppression |

---

## Step 9 – Relapse Scenario

Mr. Rahman is started on glucocorticoids (prednisolone 0.8 mg/kg/day) after discussion of risks and benefits. He achieves partial remission over the next 6 months.

### The Relapse

At 18 months after diagnosis, Mr. Rahman presents with:

- Recurrent bilateral leg edema (1 week)
- Foamy urine (reported by patient)
- Weight gain of 3 kg
- BP 136/84 mmHg (well controlled on ramipril)

**Lab results:**
| Test | 3 Months Ago | Today | Change |
|------|-------------|-------|--------|
| eGFR | 46 | 38 | **Decline** |
| 24h UTP | 0.8 g | 3.5 g | **Relapse** |
| Albumin | 3.6 | 2.9 | **Decline** |
| Creatinine | 1.6 | 2.0 | **Rise** |

### Automatic Detection

```
New Lab Results Entered
│
└─► Step 1: Proteinuria Trend Analysis
    ├─► Previous: 3.8 → 2.1 → 0.8 (improving)
    ├─► Now: 3.5 (sudden rise)
    └─► Detection: Relapse likely
│
└─► Step 2: eGFR Trend Analysis
    ├─► Previous: Stable at 44–46
    ├─► Now: 38 (decline)
    └─► Detection: Acute kidney function decline
│
└─► Step 3: Clinical Reasoning
    ├─► Triggers: "Relapse detected"
    ├─► Engine: Full retrigger
    ├─► Disease phase: Active disease → Relapse
    ├─► Assessment: "IgAN relapse with AKI"
    └─► Updated risk: High
│
└─► Step 4: Follow-up Engine
    ├─► Interval: Shortened to 30 days
    ├─► New tasks:
    │   ├─► Urgent visit (within 1 week)
    │   ├─► Repeat labs (2 weeks)
    │   └─► Safety monitoring (glucocorticoid toxicity)
    └─► Escalation: Level 1 (clinician dashboard alert)
│
└─► Step 5: Disease Phase Update
    ├─► Previous: "Remission"
    ├─► New: "Relapse"
    └─► Timeline: "Relapse documented" entry
```

### Clinical Assessment at Relapse Visit

At the urgent visit:

**Encounter details:**
- Type: *Unscheduled (relapse)*
- BP: *136/84 mmHg*
- Weight: *68 kg (+3 kg)*
- Edema: *2+*
- Clinician response: *Relapse*

**Treatment adjustment:**
- Glucocorticoids: Restarted at previous dose
- Consider: Second-line immunosuppression (discussed with patient)
- Plan: Recheck labs at 2 weeks, if inadequate response consider MMF or cyclophosphamide

### Updated Follow-up Plan

| Task | Due | Priority |
|------|-----|----------|
| **Urgent labs** (creatinine, eGFR, UTP) | 2 weeks | High |
| **Follow-up visit** | 30 days | High |
| **Safety monitoring** (glucocorticoid toxicity) | 2 weeks | High |
| **Full lab panel** | 30 days | Medium |

---

## Step 10 – Long-term Follow-up

GDES manages Mr. Rahman over several years. Here is the summary of his journey:

| Time | eGFR | Proteinuria | Phase | Treatment |
|------|------|-------------|-------|-----------|
| Baseline | 48 | 3.8 g | Active | Ramipril started |
| 3 months | 44 | 2.1 g | Active | Prednisolone started |
| 6 months | 46 | 0.8 g | Partial remission | Prednisolone tapering |
| 12 months | 48 | 0.3 g | Complete remission | Prednisolone 5 mg |
| 18 months | 38 | 3.5 g | **Relapse** | Prednisolone increased |
| 21 months | 42 | 1.2 g | Improving | MMF added |
| 24 months | 44 | 0.4 g | Remission | MMF maintenance |
| 36 months | 42 | 0.3 g | Remission | Stable on MMF |
| 48 months | 40 | 0.2 g | Remission | Stable |

### Research Output

After 5 years of follow-up, Mr. Rahman's data contributes to the research dataset:

- **eGFR slope:** −1.6 mL/min/year (over 5 years)
- **Remission status:** Achieved complete remission after first relapse
- **Time to first remission:** 6 months
- **Time to relapse:** 18 months
- **Treatment episodes:** Ramipril, prednisolone (2 courses), MMF
- **Outcome:** Alive, no ESKD, stable kidney function

### GDES's Long-term Value

After 5 years, GDES has maintained without any manual effort:

- A complete longitudinal clinical record
- An auditable trail of every decision and data change
- A continuously updated research dataset
- An automated follow-up schedule that prevented loss to follow-up
- A comprehensive outcome assessment ready for analysis

---

# Automated Management

This chapter describes every automatic process in GDES, organised by trigger type.

## Clinical Data Entry Automations

| Trigger | Automation | Clinical Benefit |
|---------|-----------|-----------------|
| Patient registered | Audit log, timeline, research eligibility, follow-up initialisation | Complete record from first contact |
| Baseline saved | eGFR, BMI, BSA, KDIGO stage, CKD risk category computed | Risk stratification at enrolment |
| Lab result entered | Reference range checked, trend updated, critical alerts | Immediate recognition of abnormal values |
| Biopsy result entered | Disease classification, knowledge engine activated, protocol assigned | Guideline-based disease management |
| Prescription finalised | Treatment reconciliation, safety checks, monitoring tasks created | Medication management without extra work |
| Encounter saved | Disease phase assessed, visit recorded, next visit scheduled | Seamless visit-to-visit transitions |

## Monitoring and Detection Automations

| Automation | Frequency | Description |
|-----------|-----------|-------------|
| eGFR slope computation | Every new lab result | Mixed-model slope estimation after 3+ results |
| AKI detection | Every new creatinine | KDIGO creatinine criteria (≥0.3 mg/dL in 48h or ≥1.5× baseline in 7 days) |
| CKD progression detection | Every new eGFR | KDIGO category change assessment |
| Proteinuria trend | Every new UTP/UPCR | Categorical change detection |
| Disease phase update | Every encounter | Active, remission, relapse, post-remission |
| Risk assessment | Every new clinical data | Progression risk, relapse risk, kidney survival |

## Scheduling Automations

| Automation | Trigger | Description |
|-----------|---------|-------------|
| Follow-up visit scheduled | Encounter saved, protocol assigned | Disease- and risk-appropriate interval |
| Lab schedule generated | Follow-up plan generated | Disease-specific lab panel timing |
| Medication monitoring | Active prescription | Drug-specific safety monitoring tasks |
| Safety monitoring | Immunosuppression | Infection surveillance, toxicity monitoring |
| Research visit | Study enrolment | Protocol-specific research visit schedule |
| Escalation trigger | Overdue task | Multi-level escalation chain |

## Continuous Automations

| Automation | Description |
|-----------|-------------|
| Clinical reasoning | Reruns after every data change |
| Follow-up engine | Recomputes plan after every data change |
| Research dataset | Updated in real-time |
| Timeline | Every event automatically recorded |
| Audit log | Every change automatically recorded |
| Dashboard statistics | Recalculated periodically |
| Clinician worklist | Updated in real-time |

---

# Automated Follow-up Engine

The Follow-up Engine is the heart of GDES's automated patient management. It ensures no patient is lost to follow-up and that every patient receives the right care at the right time.

## Architecture

```
┌──────────────┐
│  Patient     │
│  Data        │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────────┐
│  Risk        │────►│  Protocol         │
│  Stratifier  │     │  Selector         │
└──────────────┘     └────────┬─────────┘
                              │
                              ▼
┌──────────────┐     ┌──────────────────┐
│  Task        │◄────│  Schedule         │
│  Generator   │     │  Calculator       │
└──────────────┘     └──────────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────────┐
│  Worklist    │     │  Escalation      │
│  (Dashboard) │     │  Engine          │
└──────────────┘     └──────────────────┘
```

## Risk Stratification

The risk stratifier evaluates 11 factors to determine follow-up intensity:

| Factor | Low Risk | High Risk |
|--------|----------|-----------|
| eGFR | >60 | <30 |
| Proteinuria | <0.5 g/day | >3.5 g/day |
| Blood pressure | <130/80 | >160/100 |
| Histology (if available) | M0, S0, T0 | M1, T1-2, crescents |
| Diabetes | No | Uncontrolled |
| Immunosuppression | None | High-dose steroids |
| Response to therapy | Complete remission | No response |
| Relapse history | First presentation | Multiple relapses |
| Comorbidities | None | Multiple |
| Adherence | Good | Poor |
| Social factors | Stable | Unstable |

## Disease-Specific Protocols

GDES includes 10 disease-specific follow-up protocols:

| Disease | Default Interval (Low Risk) | Default Interval (High Risk) |
|---------|---------------------------|-----------------------------|
| IgA Nephropathy | 180 days | 90 days |
| Minimal Change Disease | 180 days | 90 days |
| FSGS | 90 days | 60 days |
| Membranous Nephropathy | 120 days | 60 days |
| Lupus Nephritis | 90 days | 30 days |
| ANCA Vasculitis | 90 days | 30 days |
| Anti-GBM Disease | 90 days | 30 days |
| C3 Glomerulopathy | 120 days | 60 days |
| MPGN | 120 days | 60 days |
| Dense Deposit Disease | 120 days | 60 days |

## Task Types

The generator creates 7 types of follow-up tasks:

| Task Type | Description | Example |
|-----------|-------------|---------|
| Visit due | Clinical follow-up appointment | "Follow-up visit in 90 days" |
| Lab due | Laboratory investigation | "Serum creatinine, UTP" |
| Medication monitoring | Drug safety check | "CBC, LFT for MMF" |
| Safety monitoring | Adverse event surveillance | "Infection monitoring on steroids" |
| Research visit | Study protocol visit | "Study A: 6-month visit" |
| Referral due | Subspecialty referral | "Refer to ophthalmology for HCQ" |
| Patient contact | Phone call or reminder | "Remind patient of upcoming visit" |

## Escalation Chain

Missed tasks trigger a 4-level escalation:

```
Task Overdue
│
└─► Level 1 (1-14 days overdue)
    ├── Task marked "overdue" in worklist
    └── Visible on clinician dashboard
│
└─► Level 2 (15-30 days overdue)
    ├── Clinician notification sent
    └── Dashboard alert
│
└─► Level 3 (31-60 days overdue)
    ├── Clinic coordinator notified
    └── Patient contact initiated
│
└─► Level 4 (>60 days overdue)
    ├── Department head notified
    └── Case review triggered
```

> **Clinical Tip:** The escalation chain is your safety net. Even if you forget to schedule a follow-up, GDES will not let a high-risk patient fall through the cracks. Check the worklist daily to catch Level 1 escalations early.

## How GDES Reduces Loss to Follow-up

1. **Automatic scheduling** — every patient has a follow-up plan from day one
2. **Risk-appropriate intervals** — high-risk patients are seen more frequently
3. **Centralised worklist** — all pending tasks visible in one place
4. **Multi-level escalation** — missed visits trigger increasingly urgent alerts
5. **Clinician dashboard** — overdue tasks are prominently displayed
6. **Timeline tracking** — complete visit history enables pattern recognition
7. **Outcome monitoring** — patients lost to follow-up are flagged in research analyses

---

# Research Workflow

GDES is designed so that clinical care automatically contributes to research. This section explains how.

## Automatic Cohort Inclusion

Every registered patient is automatically included in the research cohort. No separate enrolment process is required. If a patient withdraws consent, their data is flagged but retained for existing analyses.

## Outcome Tracking

The outcome engine automatically computes:

| Outcome | Definition | Data Required |
|---------|-----------|---------------|
| Complete remission | Proteinuria <0.3 g/g, stable eGFR | Labs + clinical assessment |
| Partial remission | Proteinuria reduction >50% | Labs |
| No response | Does not meet remission criteria | Labs + clinical assessment |
| Relapse | Recurrence after remission | Labs + clinical assessment |
| ESKD | eGFR <15, dialysis, or transplant | Labs + events |
| Death | All-cause mortality | Events |
| Composite | ESKD, death, or sustained eGFR decline >40% | Labs + events |

## Research Data Export

GDES generates a denormalised one-row-per-patient research dataset.

**To export:**
1. From the Dashboard, click **"Export"** in the navigation sidebar.
2. Select format (CSV or Excel).
3. Optionally select identified (requires data manager role).
4. Click **"Export"**.

The Excel export includes a data dictionary sheet with column descriptions, types, and units.

## Survival Analysis

From the Analytics module:

1. Select **"Survival Analysis"** from the Research page.
2. Choose outcome (ESKD, death, composite).
3. Optionally stratify by diagnosis, treatment, or other variables.
4. View Kaplan-Meier curves with confidence intervals.
5. View log-rank test results.
6. Export curves for publication.

**Available analyses:**
- Kaplan-Meier survival curves
- Nelson-Aalen cumulative hazard
- Log-rank test
- Incidence rate calculation
- Competing risks (cumulative incidence function)

## Cox Regression

From the Analytics module:

1. Select **"Cox PH"** from the Research page.
2. Choose outcome and covariates.
3. View hazard ratios with confidence intervals.
4. View proportional hazards test.
5. Export results for publication.

## Registry-Embedded Trials

GDES supports the full lifecycle of registry-embedded clinical trials:

1. **Study definition** — Define study, arms, eligibility criteria
2. **Eligibility screening** — GDES automatically identifies eligible patients
3. **Randomisation** — Stratified permuted-block randomisation
4. **Data collection** — Standard GDES data collection serves as trial data
5. **DSMB reporting** — Automatic safety tabulation by arm
6. **Analysis** — Standard GDES analytics applicable to trial data

## Publication-Quality Datasets

The research dataset is designed to meet publication standards:

- Complete audit trail for every data point
- Standardised coding (diagnosis, medications, outcomes)
- Missing data explicitly coded
- Longitudinal structure supports time-to-event analysis
- De-identified by default (identified export gated to data managers)

---

# Clinical Decision Support

GDES provides clinical decision support at every stage of patient management.

## Evidence Grades

Each recommendation in GDES is assigned an evidence grade:

| Grade | Meaning |
|-------|---------|
| **Grade 1A** | Strong recommendation, high-quality evidence |
| **Grade 1B** | Strong recommendation, moderate-quality evidence |
| **Grade 1C** | Strong recommendation, low-quality evidence |
| **Grade 2A** | Weak recommendation, high-quality evidence |
| **Grade 2B** | Weak recommendation, moderate-quality evidence |
| **Grade 2C** | Weak recommendation, low-quality evidence |
| **No Grade** | Consensus-based or expert opinion |

## Guideline References

Recommendations include specific references:

- KDIGO 2021 Glomerular Diseases Guideline
- ISN/RPS Lupus Nephritis Classification
- KDIGO Diabetes in CKD Guideline
- Local BIRDEM protocols
- Published trial results (TESTING, STOP-IgAN, etc.)

## Reasoning Chain

The reasoning chain shows how GDES arrived at a conclusion:

```
Example — IgA Nephropathy diagnosis:
1. Patient feature: Nephrotic syndrome (score: 15)
2. Patient feature: Microscopic hematuria (score: 10)
3. Patient feature: Reduced eGFR (score: 8)
4. Patient feature: Negative ANA (score: +5 toward primary GN)
5. Patient feature: Normal C3/C4 (score: +10 toward primary GN)
6. Knowledge rule: IgA dominant IF in biopsy (score: 60)
   Source: KDIGO 2021, Rule IG-01
   -------------------------------------------------
   Total score: 98/100 → IgA Nephropathy (98% confidence)
```

## Confidence

Confidence scores reflect how well the patient's data matches the knowledge base rules:

| Confidence | Meaning |
|-----------|---------|
| >90% | Very likely — biopsy confirmation or strong syndromic match |
| 70–90% | Likely — suggestive pattern with minor inconsistencies |
| 40–70% | Possible — partial match, more data needed |
| <40% | Unlikely — weak match, alternative diagnoses more probable |

## Limitations

GDES decision support has limitations that clinicians should understand:

- **Knowledge base currency** — Rules reflect published evidence at the time of knowledge base update. Rare or newly described presentations may not be covered.
- **Data completeness** — Clinical reasoning is only as good as the data entered. Missing data reduces confidence and may produce less specific results.
- **Clinical judgment required** — GDES is a decision support tool, not a replacement for clinical judgment. All recommendations should be reviewed and contextualised by the treating clinician.
- **Local population considerations** — Knowledge base rules are derived from international evidence. Local disease patterns may differ.

## Override Workflow

When a clinician disagrees with a GDES recommendation:

1. Document the override reason in the patient record
2. The override is recorded in the audit log
3. The clinical reasoning engine notes the override in future analyses
4. Override patterns can be reviewed for quality improvement

---

# Practical Examples

This section provides additional case studies illustrating GDES use across different disease types.

## Case 1 — Membranous Nephropathy

**Presentation:** 45-year-old female with nephrotic syndrome (UTP 6.2 g/day, albumin 2.2 g/dL), positive anti-PLA2R.

**GDES workflow:**
1. Registration → Baseline → Labs (positive anti-PLA2R)
2. Biopsy → PLA2R staining positive → MN confirmed
3. Clinical Reasoning → MN with high anti-PLA2R titre → risk assessed
4. Treatment → RAAS blockade + immunosuppression discussion
5. Follow-up → 60-day interval (high risk)

**Monitoring:**
- Anti-PLA2R titres serial monitoring
- Immunological remission (50% decline) detected at 6 months
- Clinical remission at 9 months

## Case 2 — Lupus Nephritis

**Presentation:** 28-year-old female with malar rash, arthritis, proteinuria 2.8 g/day, positive ANA, anti-dsDNA, low C3.

**GDES workflow:**
1. Registration → Baseline → Labs (ANA+, dsDNA+, C3↓)
2. Biopsy → Class IV (diffuse proliferative) LN confirmed
3. Clinical Reasoning → Active LN with high activity score
4. Treatment → Methylprednisolone + MMF
5. Follow-up → 30-day interval (very high risk)

**Monitoring:**
- Complement recovery tracked
- Anti-dsDNA titres monitored
- Renal response at 6 months

## Case 3 — ANCA Vasculitis

**Presentation:** 60-year-old male with rapidly progressive GN (creatinine 3.2 mg/dL, eGFR 18), positive MPO-ANCA, hematuria.

**GDES workflow:**
1. Registration → Baseline (urgent) → Labs (positive MPO-ANCA)
2. Biopsy → Pauci-immune crescentic GN
3. Clinical Reasoning → ANCA vasculitis with high-risk features
4. Treatment → Induction with cyclophosphamide + steroids
5. Follow-up → 30-day interval

**Outcome:**
- eGFR improved to 38 at 6 months
- ANCA negative at 12 months
- Maintenance azathioprine

## Case 4 — Minimal Change Disease

**Presentation:** 22-year-old male with abrupt onset nephrotic syndrome (UTP 8.5 g/day, albumin 1.8 g/dL), normal eGFR, no hematuria.

**GDES workflow:**
1. Registration → Baseline
2. Biopsy → Minimal change disease (MCD)
3. Clinical Reasoning → MCD with high relapse risk identified
4. Treatment → Prednisolone 1 mg/kg/day
5. Follow-up → 90-day interval

**Outcome:**
- Complete remission at 4 weeks
- Steroid taper started
- Relapse at 12 months → second course

## Case 5 — FSGS

**Presentation:** 38-year-old male with nephrotic syndrome (UTP 5.1 g/day), normal eGFR, no hematuria.

**GDES workflow:**
1. Registration → Baseline
2. Biopsy → FSGS, not otherwise specified
3. Clinical Reasoning → FSGS with high progression risk (Columbia classification)
4. Treatment → Prednisolone + RAAS blockade
5. Follow-up → 60-day interval

## Case 6 — C3 Glomerulopathy

**Presentation:** 32-year-old female with hematuria, proteinuria 1.2 g/day, low C3.

**GDES workflow:**
1. Registration → Baseline → Labs (low C3, normal C4)
2. Biopsy → C3 dominant staining → C3 glomerulopathy
3. Clinical Reasoning → C3G differential (DDD vs C3GN)
4. Follow-up → 120-day interval

## Case 7 — Kidney Transplant Recipient

**Presentation:** 42-year-old male with kidney transplant, new proteinuria 0.8 g/day.

**GDES workflow:**
1. Registration as transplant patient
2. Baseline assessment with transplant history
3. Labs → Screen for rejection, recurrence of primary disease
4. Biopsy if indicated
5. Follow-up → Individualised schedule

---

# Appendices

## Appendix A — Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search bar |
| `Ctrl+N` | New patient registration |
| `Alt+D` | Dashboard |
| `Alt+P` | Patient list |
| `Alt+A` | Analytics |
| `Alt+W` | Worklist |

## Appendix B — Dashboard Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 **Live** | System operating normally |
| 🟡 **Degraded** | Partial functionality |
| 🔴 **Down** | System unavailable |
| **Badge (green)** | Complete / Normal |
| **Badge (yellow)** | Pending / Warning |
| **Badge (red)** | Overdue / Critical |

## Appendix C — Common Clinical Codes

| Code | Meaning |
|------|---------|
| G1 | eGFR ≥90 |
| G2 | eGFR 60–89 |
| G3a | eGFR 45–59 |
| G3b | eGFR 30–44 |
| G4 | eGFR 15–29 |
| G5 | eGFR <15 |
| A1 | Albuminuria <30 mg/g |
| A2 | Albuminuria 30–300 mg/g |
| A3 | Albuminuria >300 mg/g |

## Appendix D — Glossary

| Term | Definition |
|------|------------|
| **AKI** | Acute Kidney Injury |
| **BSA** | Body Surface Area |
| **CKD** | Chronic Kidney Disease |
| **CKD-EPI** | Chronic Kidney Disease Epidemiology Collaboration (eGFR formula) |
| **DSMB** | Data Safety Monitoring Board |
| **eGFR** | Estimated Glomerular Filtration Rate |
| **ESKD** | End-Stage Kidney Disease |
| **GN** | Glomerulonephritis |
| **KDIGO** | Kidney Disease: Improving Global Outcomes |
| **MEST-C** | Oxford classification scores for IgAN |
| **MMF** | Mycophenolate Mofetil |
| **RAAS** | Renin-Angiotensin-Aldosterone System |
| **UPCR** | Urine Protein-to-Creatinine Ratio |
| **UTP** | 24-hour Urine Total Protein |

## Appendix E — Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.1 | July 2026 | CDS reliability fixes (drug toxicity, treatment failure, relapse detection); human-readable disease names in CDS output; zero-confidence UI cleanup; CDS error logging; integration test suite (205 tests) |
| 5.0 | July 2026 | Follow-up engine, clinical reasoning tab, audit log tab, GDES branding |
| 4.0 | April 2026 | Clinical reasoning engine, knowledge base, decision support |
| 3.0 | January 2026 | Biopsy module, central pathology review, research dataset export |
| 2.0 | October 2025 | Prescription engine, treatment reconciliation, bilingual PDF |
| 1.0 | June 2025 | Initial patient registry, baseline assessment, lab tracking |

---

*GDES Version 5.1 — BIRDEM Nephrology, Dhaka, Bangladesh*

*For support: Contact the BIRDEM Nephrology IT Help Desk*

*This manual is intended for clinical users. No software engineering knowledge is required.*

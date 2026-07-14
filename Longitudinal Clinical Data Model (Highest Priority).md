# Longitudinal Clinical Data Model (Highest Priority)

## Objective

GDES is a longitudinal clinical registry and decision support system.

The same permanent clinical information must NEVER be entered repeatedly in multiple forms.

Instead, the system should maintain a single source of truth and automatically carry forward clinically persistent information throughout the patient's journey.

This reduces clinician workload, prevents inconsistencies, and improves data quality.

---

# Clinical Data Classification

All patient data must be classified into three categories.

## Level 1 — Permanent Data

Entered once.

Never entered again.

Examples

- Patient ID
- Name
- Date of Birth
- Sex
- Blood Group
- Ethnicity
- Family History
- Genetic Diagnosis

These should be read-only after creation unless edited through a dedicated correction workflow.

---

## Level 2 — Persistent Clinical Data

These remain valid until intentionally changed.

Examples

- Primary GN Diagnosis
- Secondary Diagnosis
- Kidney Biopsy Diagnosis
- Histopathological Classification
- Oxford MEST-C Score
- ISN/RPS Class
- Transplant Status
- Hepatitis Status
- HIV Status
- Autoimmune Disease
- Diabetes Mellitus
- Hypertension
- Smoking Status
- CKD Etiology

These must be entered only once.

All future encounters must automatically display the current value.

Clinicians should only update them when clinically necessary.

---

## Level 3 — Time-Dependent Data

These belong to a specific encounter.

Examples

- Blood Pressure
- Weight
- Height (if appropriate)
- Serum Creatinine
- eGFR
- UPCR
- Proteinuria
- Medications
- Adverse Events
- Symptoms
- Physical Examination
- Laboratory Results

These are entered at each visit.

---

# Remove Duplicate Data Entry

Review the entire application.

If the same clinical information appears in multiple modules, redesign it.

Example

Current

Baseline

Primary GN Diagnosis

↓

Follow-up

Primary GN Diagnosis

↓

Outcome

Primary GN Diagnosis

Three independent copies.

This is incorrect.

Correct design

Baseline

Primary GN Diagnosis

↓

Patient Longitudinal Record

↓

Automatically displayed everywhere

↓

Follow-up

↓

Prescription

↓

Clinical Reasoning

↓

Outcome

↓

Research

Only one stored value.

---

# Auto-Carry Forward

When opening any follow-up encounter, automatically populate:

- Primary GN Diagnosis
- Secondary Diagnosis
- Biopsy Diagnosis
- Histopathology
- CKD Etiology
- Diabetes
- Hypertension
- Smoking Status
- Transplant Status
- Autoimmune Disease
- Hepatitis
- HIV

The clinician should only confirm or modify these values when a true clinical change occurs.

---

# Exposure Variables for Research

Persistent clinical variables should automatically be available as exposure variables for research and outcome analysis.

Examples

Exposure Variables

- Primary GN Diagnosis
- Biopsy Diagnosis
- Oxford MEST-C
- ISN/RPS Class
- Disease Category
- Diabetes
- Hypertension
- Smoking
- Hepatitis
- HIV
- Initial Immunosuppressive Therapy
- Genetic Disease

Outcome Variables

- eGFR Decline
- Complete Remission
- Partial Remission
- Relapse
- ESRD
- Dialysis
- Kidney Transplantation
- Death
- Hospitalization
- Serious Adverse Events

The system should automatically link baseline exposures with longitudinal outcomes to support registry-based clinical research without requiring duplicate data entry.

---

# Design Principle

There must be a single source of truth for every persistent clinical concept.

The same diagnosis, biopsy result, or chronic comorbidity should never exist as multiple independent records across different modules.

All modules (Baseline, Follow-up, Prescription, Clinical Decision Support, Outcome, Research, and Reports) must reference the same underlying clinical data while maintaining a complete audit trail of any changes.
# BGDDR — Clinical Workflow Documentation

## Master Workflow (GN Management Protocol)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     GN MANAGEMENT WORKFLOW                               │
│                                                                         │
│  1. SUSPECTED GN                                                        │
│     │  Patient presents with nephrotic/nephritic syndrome, AKI,        │
│     │  or asymptomatic urinary abnormality                              │
│     ▼                                                                   │
│  2. ADMISSION + WORKUP                                                  │
│     │  Create Admission record                                          │
│     │  → admit_date, ward, reason                                       │
│     ▼                                                                   │
│  3. RENAL BIOPSY                                                        │
│     │  Create Biopsy record                                             │
│     │  → biopsy_date, adequacy, indication                              │
│     │  → PathologyReview(role=LOCAL)                                    │
│     │  → PathologyReview(role=CENTRAL)                                  │
│     │  → concordance check → adjudication if discordant                 │
│     │  → _finalize() writes GNDiagnosis + IgANScore                    │
│     ▼                                                                   │
│  4. BASELINE ASSESSMENT                                                 │
│     │  Create BaselineAssessment (OneToOne with Patient)                │
│     │  → demographics, medical history, vitals, diabetes burden         │
│     │  → presentation syndrome (multi-select)                          │
│     │  → BMI auto-derived                                               │
│     ▼                                                                   │
│  5. GN CLINIC REGISTRATION                                              │
│     │  register_patient(patient)                                        │
│     │  → registration_status = "registered"                             │
│     │  → current_phase = "active"                                       │
│     │  → generate_schedule() creates ScheduledVisit rows                │
│     ▼                                                                   │
│  6. LONGITUDINAL FOLLOW-UP                                              │
│     │  ┌─────────────────────────────────────────────────┐              │
│     │  │  VISIT WORKFLOW (repeat at each scheduled visit)│              │
│     │  │                                                  │              │
│     │  │  a. Clinical Encounter                           │              │
│     │  │     → BP, weight, edema, symptoms               │              │
│     │  │     → clinician_response assessment              │              │
│     │  │                                                  │              │
│     │  │  b. Clinical Assessment (GDES)                  │              │
│     │  │     → chief_complaint, features, syndrome        │              │
│     │  │                                                  │              │
│     │  │  c. Vital Signs                                 │              │
│     │  │     → bp, heart_rate, weight, height            │              │
│     │  │                                                  │              │
│     │  │  d. Lab Orders                                  │              │
│     │  │     → LabOrder → LabOrderItem                   │              │
│     │  │     → Results entered later → LabResult          │              │
│     │  │     → eGFR auto-derived from creatinine          │              │
│     │  │                                                  │              │
│     │  │  e. Prescription                                │              │
│     │  │     → PrescriptionItem (full medication list)    │              │
│     │  │     → Safety checks (renal, intolerance, dup)   │              │
│     │  │     → Finalize → PDF + reconciliation            │              │
│     │  │                                                  │              │
│     │  │  f. Treatment Exposure (auto)                   │              │
│     │  │     → Reconciliation engine opens/closes episodes│              │
│     │  │                                                  │              │
│     │  │  g. Phase Advancement                           │              │
│     │  │     → apply_visit() updates disease phase        │              │
│     │  │                                                  │              │
│     │  │  h. Outcome Computation                         │              │
│     │  │     → compute_patient_outcome()                  │              │
│     │  │     → PatientOutcome row updated                 │              │
│     │  └─────────────────────────────────────────────────┘              │
│     │                                                                   │
│     ├──► REMISSION (complete response)                                  │
│     │       → current_phase = "remission"                               │
│     │       → continue monitoring                                       │
│     │                                                                   │
│     ├──► POST_REMISSION                                                 │
│     │       → stable in remission                                       │
│     │       → current_phase = "post_remission"                          │
│     │                                                                   │
│     └──► RELAPSE (step 5E)                                              │
│             → RelapseEpisode created                                    │
│             → ClinicalEvent(RELAPSE) emitted                            │
│             → current_phase = "relapse"                                 │
│             → re-enter active management                                │
│                                                                         │
│  7. OUTCOMES (computed, not entered)                                    │
│     → PatientOutcome row per patient                                    │
│     → eGFR slope, sustained declines, ESKD, death                      │
│     → Disease-specific proteinuria remission                            │
│     → Composite kidney endpoint                                         │
│     → Time-to-event endpoints for survival analysis                     │
│                                                                         │
│  8. RESEARCH EXPORT                                                     │
│     → De-identified dataset (CSV/XLSX/SPSS)                            │
│     → One row per patient, all domains denormalized                     │
│     → Optional per-study ITT dataset with arm assignment                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Patient Registration Workflow

```
New patient presents
    │
    ▼
Create Patient record
    │  patient_id = auto-generated (BGD-NNNNN)
    │  hospital_id, name, phone, sex, dob
    │  enrollment_date = today
    │
    ├── Duplicate check (hospital_id, name, phone)
    │   → If duplicate found: alert user
    │
    ├── Baseline Assessment (OneToOne)
    │   → demographics, history, vitals, diabetes
    │   → BMI auto-derived
    │
    ├── Consent Management
    │   → Consent(type="registry") — required
    │   → Consent(type="imaging") — for biopsy images
    │   → Consent(type="trial") — for embedded RCTs
    │
    └── Registration Status = "suspected"
        → Awaiting biopsy report
```

---

## Prescription Workflow

```
Clinician opens prescription for patient
    │
    ▼
PrescriptionCreate view
    │  → Copy previous prescription items (if exists)
    │  → Pre-fill diagnosis, comorbidities from baseline
    │
    ├── Clinician edits medication list
    │   → Add/remove/edit PrescriptionItem
    │   → Each item: drug, brand, strength, dose, route, frequency, timing
    │   → Bengali instructions for patient
    │
    ├── Safety Checks (live)
    │   → check_prescription(prescription)
    │   ├── Renal dosing: eGFR vs drug threshold
    │   ├── Prior intolerance: AE/intolerance history
    │   ├── Duplicate therapy: same DrugClass
    │   └── Glycaemic effect: steroid/CNI warning
    │
    ├── Finalize
    │   → finalize_prescription(prescription, user)
    │   ├── If blocking warnings: raise FinalizeBlocked
    │   ├── prescription.status = FINAL (immutable)
    │   ├── prescription.content_hash = SHA-256
    │   ├── Generate PDF (WeasyPrint / xhtml2pdf)
    │   └── apply_reconciliation()
    │           │
    │           ├── Diff: PrescriptionItem vs open TreatmentExposure
    │           │
    │           ├── NEW drug → OPEN new episode
    │           │   TreatmentExposure(drug, dose, frequency, route,
    │           │                     start_date=today, ongoing=True)
    │           │
    │           ├── OPEN episode, drug absent → CLOSE
    │           │   TreatmentExposure(ongoing=False, stop_date=today,
    │           │                     stop_reason=reason)
    │           │
    │           ├── SAME drug, dose changed → SPLIT
    │           │   Close old episode + Open new episode
    │           │
    │           └── SAME drug, same regimen → CONTINUE (no-op)
    │
    └── Print PDF
        → Letterhead: BIRDEM General Hospital
        → Bengali drug names/instructions
        → Content hash for audit
```

---

## Biopsy & Pathology Workflow

```
Biopsy performed
    │
    ▼
Create Biopsy record
    │  → biopsy_date, adequacy, indication
    │  → total_glomeruli, sclerosis%, IFTA%
    │  → crescents, necrosis, IF pattern, EM findings
    │
    ├── LOCAL Pathologist Review
    │   → PathologyReview(role=LOCAL)
    │   → diagnosis, broad_group, MEST-C scores
    │   → submit_review() → status = AWAITING_CENTRAL
    │
    ├── CENTRAL Expert Review
    │   → PathologyReview(role=CENTRAL)
    │   → submit_review() → _recompute_status()
    │       │
    │       ├── concordance() field-by-field comparison
    │       │   KEY_FIELDS = [diagnosis, broad_group, mest_m, mest_e,
    │       │                 mest_s, mest_t, mest_c, isn_rps_class,
    │       │                 fsgs_variant]
    │       │
    │       ├── CONCORDANT → _finalize()
    │       │   → Mark final read as is_final=True
    │       │   → GNDiagnosis ← from final read
    │       │   → IgANScore ← from final read (if applicable)
    │       │
    │       └── DISCORDANT → await adjudication
    │
    └── ADJUDICATION (if discordant)
        → PathologyReview(role=ADJUDICATION)
        → adjudicate() → _recompute_status() → ADJUDICATED
        → _finalize() writes GNDiagnosis + IgANScore
```

---

## Lab Ordering & Results Workflow

```
Clinician orders labs at visit
    │
    ▼
Create LabOrder
    │  → encounter, patient, ordered_date
    │
    ├── Add LabOrderItems
    │   → test (from LabTest catalog)
    │   → Can also order by LabPanel (bundle of tests)
    │
    ├── Sample Collection
    │   → LabOrder.status = "collected"
    │
    └── Results Entry
        → Create LabResult for each item
        │  → patient, test, value_numeric/value_text, unit
        │  → sample_date, result_date
        │  → flag (L/H/normal)
        │  → source (lab/manual/derived)
        │
        ├── Auto-derivation
        │   → If test = "creatinine":
        │       → Compute eGFR via CKD-EPI 2021
        │       → Create LabResult(test=egfr, source="derived")
        │       → derived_from = creatinine result
        │       → formula_version = "CKD-EPI-2021-creatinine"
        │
        ├── Update Patient.latest_egfr (cached)
        │
        └── LabOrder.status auto-updates to "resulted"
            → refresh_status() checks all items
```

---

## Study Enrollment & Randomization Workflow

```
Study defined (Study + StudyArm records)
    │
    ▼
Patient enrollment
    │
    ├── Eligibility Screening
    │   → screen(study, patient) → (eligible, reasons)
    │   → If ineligible: status = "ineligible"
    │
    ├── Trial Consent Check
    │   → If study.requires_trial_consent:
    │       → has_consent(patient, Consent.Type.TRIAL)
    │       → If no consent: raise ConsentRequired
    │
    ├── Randomization (if study.is_randomized)
    │   │
    │   ├── Compute Stratum
    │   │   → stratify_by factors: diabetes, egfr_stratum, etc.
    │   │   → stratum = "diabetes=DM|egfr_stratum=30to59"
    │   │
    │   ├── Generate Sequence
    │   │   → _stratum_rng(study, stratum) — seeded RNG
    │   │   → generate_sequence(study, arms, stratum, n)
    │   │   → Permuted blocks with configurable multipliers
    │   │
    │   └── Allocate Arm
    │       → position = count of existing allocations in stratum
    │       → arm_code = sequence[position]
    │       → Record: stratum, sequence_position, randomized_by, randomized_at
    │
    └── Enrollment Complete
        → status = "enrolled"
        → enrolled_date = today
```

---

## Follow-Up Scheduling Workflow

```
Patient registered into GN follow-up
    │
    ▼
generate_schedule(patient, anchor_date)
    │
    ├── Routine Visits
    │   → Months: 1, 3, 6, 9, 12, 18, 24, 30, 36, 42, 48, 54, 60
    │   → Each visit: target_date ± 7 days
    │   → Snapped to nearest Tuesday (configurable)
    │
    ├── Early Safety Visits (if immunosuppressed)
    │   → Weeks: 1, 2, 4
    │
    └── Capacity Management
        → session_capacity = 15 (configurable)
        → _assign_clinic_day() picks Tuesday in window with spare capacity
        → If all full: overbook closest day (coordinator resolves)

Clinic Day Management
    │
    ├── due_visits(today) → visits within window
    ├── overdue_visits(today) → visits past window_end
    ├── clinic_roster(date) → all visits for a day
    ├── complete_visit(visit, encounter) → mark done
    └── mark_missed() → flag expired windows as missed
```

---

## Outcome Computation Workflow

```
compute_patient_outcome(patient)
    │
    ├── 1. Extract longitudinal data
    │   → eGFR series: LabResult.series(patient, "egfr")
    │   → Creatinine series: LabResult.series(patient, "creatinine")
    │   → Proteinuria series: merged UTP/UPCR
    │
    ├── 2. Determine index date
    │   → enrollment_date, else earliest lab/encounter date
    │
    ├── 3. Compute kidney-function endpoints
    │   → sustained_40_decline: first eGFR ≤ 60% of baseline (sustained)
    │   → sustained_50_decline: first eGFR ≤ 50% of baseline (sustained)
    │   → doubling_creatinine: first Cr ≥ 2x baseline (sustained)
    │
    ├── 4. Hard endpoints from ClinicalEvent
    │   → ESKD: dialysis/transplant event OR sustained eGFR < 15
    │   → death: from ClinicalEvent(Type=DEATH)
    │   → composite_kidney_event: earliest of {ESKD, ≥50% decline, death}
    │
    ├── 5. Proteinuria remission (disease-specific)
    │   → disease_key() maps diagnosis to rule set
    │   ├── igan: < 0.3 (complete) or ≥30% reduction (response)
    │   ├── mn: < 0.3 (complete), ≥50% & < 3.5 (partial)
    │   ├── lupus: < 0.5 + eGFR preserved (complete)
    │   ├── fsgs: < 0.3 (complete), ≥50% & < 3.5 (partial)
    │   ├── mcd: < 0.3 (complete), ≥50% & < 3.5 (partial)
    │   ├── aav: < 0.3 (complete), ≥50% & < 3.5 (partial)
    │   └── other: < 0.3 (complete), ≥50% & < 3.5 (partial)
    │   → Sustained achievement (not transient dip)
    │   → First-achieved dates → time-to-event endpoints
    │
    ├── 6. Proteinuria relapse
    │   → First UPCR ≥ 1.0 g/day after any remission achieved
    │
    ├── 7. Biomarker kinetics (if applicable)
    │   → Anti-PLA2R ≥50% decline, seroconversion
    │   → Complement recovery (C3/C4)
    │   → Anti-dsDNA normalization
    │
    └── 8. Write PatientOutcome
        → update_or_create(patient=patient, defaults={...})
        → Re-runnable at any time via compute_outcomes()
```

---

## Safety Monitoring Workflow

```
Adverse Event Reporting
    │
    ├── Create AdverseEvent
    │   → patient, onset_date, category, severity
    │   → infection_type (if infection)
    │   → suspected_drug, relatedness
    │   → hospitalization, outcome
    │
    ├── Auto-classify SAE
    │   → serious = True if:
    │       hospitalization = True, OR
    │       severity in {life_threatening, fatal}
    │
    └── Safety Analytics
        → safety_summary(queryset): counts by category/severity
        → infection_incidence(queryset, group_by): incidence density
        → study_safety(study): per-arm SAE tabulation for DSMB
```

---

## Consent Lifecycle Workflow

```
Consent Management
    │
    ├── Grant Consent
    │   → grant_consent(patient, type, form_version)
    │   → Previous current consent → is_current=False
    │   → New consent → is_current=True, status=GRANTED
    │   → Version chain: new.supersedes = previous
    │
    ├── Check Consent
    │   → has_consent(patient, type) → bool
    │   → Gates: imaging uploads, trial enrollment, biobanking
    │
    ├── Withdraw Consent
    │   → withdraw_consent(patient, type)
    │   → status = WITHDRAWN, withdrawn_date = today
    │
    └── History
        → consent_history(patient, type) → full version chain
```

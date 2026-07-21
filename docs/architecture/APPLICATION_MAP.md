# BGDDR — Application Map

## Inter-App Relationship Diagram

```
                                    ┌─────────────────────┐
                                    │      PATIENTS        │
                                    │  (root model)        │
                                    │  Patient.patient_id  │
                                    └──────────┬──────────┘
                                               │
              ┌────────────────────────────────┼────────────────────────────────┐
              │                                │                                │
              ▼                                ▼                                ▼
    ┌─────────────────┐            ┌─────────────────────┐           ┌─────────────────┐
    │   ENCOUNTERS     │            │     BASELINE         │           │    AUDIT         │
    │  ClinicalEncounter│           │  BaselineAssessment  │           │  AuditLog        │
    │  Admission        │           │  (OneToOne→Patient)  │           │  Consent         │
    │  RelapseEpisode   │           └─────────────────────┘           │  (OneToOne→      │
    │  ClinicalEvent    │                                             │   Patient)       │
    └────────┬──────────┘                                             └─────────────────┘
             │
    ┌────────┼──────────────────┬───────────────────┬───────────────────┐
    │        │                  │                   │                   │
    ▼        ▼                  ▼                   ▼                   ▼
┌────────┐┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│  LABS  ││PRESCRIPS │  │ PATHOLOGY   │  │  SCHEDULING  │  │    SAFETY        │
│LabTest ││Prescript.│  │ Biopsy      │  │ ScheduledVisit│  │  AdverseEvent    │
│LabOrder││PrescItem │  │ GNDiagnosis │  └──────────────┘  └──────────────────┘
│LabResult││AdviceTmp │  │ IgANScore   │
└───┬────┘└────┬─────┘  │ LupusPath.  │
    │          │        │ FSGSPath.   │
    │          │        │ Membranous  │
    │          │        │ BiopsyImage │
    │          │        │ PathReview  │
    │          │        └──────┬──────┘
    │          │               │
    │          ▼               │
    │  ┌─────────────┐        │
    │  │ TREATMENTS   │        │
    │  │ DrugMaster   │◄───────┘
    │  │ TreatmentExp │
    │  └──────┬──────┘
    │         │
    ▼         ▼
┌──────────────────────────────────────────────────────────────────┐
│                        ANALYTICS                                 │
│  PatientOutcome (computed from labs + encounters + treatments)   │
│  ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌────────────────┐  │
│  │ survival.py│ │ cox.py   │ │cohort.py  │ │outcomes.py     │  │
│  │ KM, logrank│ │ Cox PH   │ │ grouping  │ │ endpoint calc  │  │
│  └────────────┘ └──────────┘ └───────────┘ └────────────────┘  │
│  ┌────────────────┐ ┌──────────────┐ ┌────────────────────────┐│
│  │competing_risks │ │mixed_model.py│ │ imputation.py (MICE)   ││
│  │ CIF (Aalen-Joh)│ │ LMM eGFR     │ │ Rubin's rules pooling  ││
│  └────────────────┘ └──────────────┘ └────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        EXPORTS                                    │
│  dataset.py → CSV / XLSX / SPSS .sav                             │
│  dictionary.py → Data dictionary                                  │
│  writers.py → Format-specific writers                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    STUDIES (Embedded Trials)                      │
│  Study → StudyArm → StudyEnrollment                              │
│  randomization.py (simple/block/stratified_block)                │
│  eligibility.py (screening)                                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    BIOMARKERS                                      │
│  BiomarkerKinetics (OneToOne→Patient)                             │
│  kinetics.py (PLA2R, complement, anti-dsDNA)                     │
│  predictor.py (remission predictor)                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    USERS                                           │
│  UserProfile (OneToOne→auth.User)                                │
│  Invitation (token-based signup)                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              GDES CLINICAL DECISION SUPPORT                       │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ clinical  │  │ knowledge  │  │ decision  │  │   timeline    │  │
│  │ Clinical  │  │ Guideline  │  │ Decision  │  │ TimelineEvent │  │
│  │ Assessment│  │ Source     │  │ Request   │  │ (cross-domain │  │
│  │ VitalSign │  │ Knowledge  │  │ Decision  │  │  aggregation) │  │
│  │           │  │ BaseEntry  │  │ Result    │  │               │  │
│  └──────────┘  └───────────┘  └──────────┘  └───────────────┘  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    CLINIC (Workflow UI)                           │
│  No models — template views + JS charting                        │
│  patients hub, baseline, follow-up, prescriptions, worklist      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Between Apps

### Patient Lifecycle

```
patient created
    │
    ├──► baseline/BaselineAssessment (OneToOne)
    ├──► encounters/ClinicalEncounter (per visit)
    │       ├──► labs/LabOrder → LabOrderItem → LabResult
    │       ├──► prescriptions/Prescription → PrescriptionItem
    │       │       └──► treatments/TreatmentExposure (via reconciliation)
    │       ├──► pathology/Biopsy → GNDiagnosis + IgANScore
    │       ├──► safety/AdverseEvent
    │       ├──► scheduling/ScheduledVisit (fulfilled)
    │       └──► clinical/ClinicalAssessment + VitalSign
    ├──► encounters/RelapseEpisode
    ├──► encounters/ClinicalEvent (hard/soft endpoints)
    ├──► studies/StudyEnrollment → StudyArm (randomization)
    ├──► audit/Consent (versioned)
    ├──► audit/AuditLog (all changes)
    │
    ├──► analytics/PatientOutcome (COMPUTED, not entered)
    ├──► biomarkers/BiomarkerKinetics (COMPUTED)
    │
    └──► exports/dataset (CSV/XLSX/SPSS)
```

### Prescription → Treatment Exposure Bridge

```
Clinician writes Prescription
    │
    ├── PrescriptionItem (drug, dose, frequency, route)
    │
    └── finalize_prescription()
            │
            ├── check_prescription() → SafetyWarning[]
            │       ├── renal dosing check
            │       ├── prior intolerance check
            │       ├── duplicate therapy check
            │       └── glycaemic effect check
            │
            ├── prescription.status = FINAL (immutable)
            ├── prescription.content_hash = SHA-256
            │
            └── apply_reconciliation()
                    │
                    ├── PrescriptionItem vs open TreatmentExposure
                    │
                    ├── NEW drug, no open episode → OPEN new episode
                    ├── OPEN episode, drug absent → CLOSE (stop_reason)
                    ├── SAME drug, dose changed → CLOSE old + OPEN new
                    └── SAME drug, same regimen → CONTINUE (no-op)
```

### Pathology Review Workflow

```
Biopsy created
    │
    ├── PathologyReview(role=LOCAL)
    │       └── submit_review()
    │               └── _recompute_status() → AWAITING_CENTRAL
    │
    ├── PathologyReview(role=CENTRAL)
    │       └── submit_review()
    │               └── _recompute_status()
    │                       ├── concordance() field-by-field comparison
    │                       ├── CONCORDANT → _finalize()
    │                       └── DISCORDANT → await adjudication
    │
    ├── PathologyReview(role=ADJUDICATION) [if discordant]
    │       └── adjudicate()
    │               └── _recompute_status() → ADJUDICATED → _finalize()
    │
    └── _finalize()
            ├── Mark authoritative read as is_final=True
            ├── GNDiagnosis ← from final read
            └── IgANScore ← from final read (if applicable)
```

### Outcome Computation Pipeline

```
compute_patient_outcome(patient)
    │
    ├── LabResult.series("egfr") → eGFR trajectory
    ├── LabResult.series("creatinine") → creatinine trajectory
    ├── LabResult.series("utp_24h"/"upcr") → proteinuria trajectory
    │
    ├── _index_date() → enrollment_date or earliest lab/encounter
    ├── _sustained_drop() → sustained ≥40% and ≥50% eGFR decline
    ├── _sustained_rise() → doubling creatinine
    │
    ├── ClinicalEvent → ESKD, dialysis, transplant, death
    ├── _proteinuria_outcome() → disease-specific remission
    │       ├── complete_predicate() → < 0.3 g/day
    │       ├── lupus_complete_predicate() → < 0.5 + eGFR preserved
    │       ├── partial_predicate() → ≥50% reduction & < 3.5
    │       └── igan_response_predicate() → ≥30% reduction or < 0.3
    │
    ├── _proteinuria_relapse() → first ≥ 1.0 g/day after remission
    │
    └── PatientOutcome.update_or_create() → denormalized row
```

---

## Cross-App Dependencies

```
patients ────────────────────────────────────────────── (everything depends on this)
    │
    ├── encounters depends on: patients
    ├── baseline depends on: patients
    ├── labs depends on: patients, encounters
    ├── pathology depends on: patients
    ├── treatments depends on: patients
    ├── prescriptions depends on: encounters, treatments
    ├── analytics depends on: patients, encounters, labs, pathology, treatments
    ├── safety depends on: patients, treatments, encounters
    ├── studies depends on: patients, audit
    ├── scheduling depends on: patients, encounters
    ├── biomarkers depends on: patients, labs
    ├── audit depends on: patients
    ├── users depends on: (auth only)
    ├── clinical depends on: patients, encounters
    ├── knowledge depends on: patients, labs, pathology
    ├── decision depends on: patients, encounters, knowledge
    ├── timeline depends on: patients, encounters, clinical, labs, pathology, decision
    ├── exports depends on: ALL (denormalized dataset)
    └── clinic depends on: ALL (workflow UI)
```

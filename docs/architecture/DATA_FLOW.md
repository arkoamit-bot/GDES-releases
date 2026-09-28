# BGDDR — Data Flow Diagrams

## Overview

Data in BGDDR flows through four primary pathways:
1. **Clinical Entry** → Patient data enters via admin/clinic UI
2. **Computed Derivation** → Analytics engines derive outcomes/biomarkers
3. **Research Export** → Denormalized dataset for analysis
4. **Decision Support** → Knowledge rules evaluate patient features

---

## Data Flow: Patient Registration to Research Export

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA ENTRY LAYER                                  │
│                                                                         │
│  Clinician/Coordinator                                                  │
│       │                                                                 │
│       ├──► Patient record                                               │
│       │      patient_id (auto), name, sex, dob, enrollment_date         │
│       │                                                                 │
│       ├──► BaselineAssessment                                           │
│       │      demographics, history, vitals, diabetes, presentation      │
│       │                                                                 │
│       ├──► ClinicalEncounter (per visit)                                │
│       │      BP, weight, edema, clinician_response, disease_phase       │
│       │                                                                 │
│       ├──► LabOrder → LabOrderItem → LabResult                          │
│       │      creatinine, UPCR, albumin, complement, serology            │
│       │      (eGFR auto-derived from creatinine)                        │
│       │                                                                 │
│       ├──► Biopsy → GNDiagnosis + IgANScore                             │
│       │      diagnosis, MEST-C, ISN/RPS, FSGS variant                  │
│       │      (via PathologyReview workflow)                              │
│       │                                                                 │
│       ├──► Prescription → PrescriptionItem                               │
│       │      drug, dose, frequency, route                               │
│       │      → finalize() → TreatmentExposure (auto-reconciliation)     │
│       │                                                                 │
│       ├──► ClinicalEvent                                                │
│       │      ESKD, dialysis, transplant, death, remission, relapse      │
│       │                                                                 │
│       ├──► AdverseEvent                                                 │
│       │      category, severity, infection type, drug attribution       │
│       │                                                                 │
│       ├──► StudyEnrollment                                              │
│       │      screening, eligibility, randomization (arm assignment)     │
│       │                                                                 │
│       ├──► Consent                                                      │
│       │      registry, biobank, genetic, imaging, trial                 │
│       │                                                                 │
│       └──► AuditLog (all changes tracked)                               │
│              who/when/old→new per field                                  │
│                                                                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     COMPUTATION LAYER                                    │
│                                                                         │
│  Automated Engines (triggered on demand or save)                        │
│       │                                                                 │
│       ├──► eGFR Auto-Derivation                                         │
│       │      creatinine → CKD-EPI 2021 → LabResult(source=derived)      │
│       │      Patient.latest_egfr updated                                │
│       │                                                                 │
│       ├──► PatientOutcome (compute_patient_outcome)                     │
│       │      ├── eGFR slope (linear regression)                         │
│       │      ├── Sustained ≥40%/50% eGFR decline                        │
│       │      ├── Doubling creatinine                                    │
│       │      ├── ESKD / death (from ClinicalEvent)                      │
│       │      ├── Composite kidney endpoint                              │
│       │      ├── Proteinuria remission (disease-specific)               │
│       │      │   ├── IgAN: < 0.3 or ≥30% reduction                     │
│       │      │   ├── MN: < 0.3, ≥50% & < 3.5                           │
│       │      │   ├── Lupus: < 0.5 + eGFR preserved                     │
│       │      │   ├── FSGS/MCD/AAV: < 0.3, ≥50% & < 3.5                │
│       │      │   └── Sustained (not transient)                          │
│       │      ├── Proteinuria relapse (≥ 1.0 after remission)            │
│       │      └── Last contact date                                      │
│       │                                                                 │
│       ├──► BiomarkerKinetics (compute_biomarkers)                       │
│       │      ├── Anti-PLA2R: baseline, nadir, ≥50% decline             │
│       │      ├── PLA2R seroconversion (immunological remission)         │
│       │      ├── Complement recovery (C3/C4 normalization)              │
│       │      └── Anti-dsDNA normalization                                │
│       │                                                                 │
│       └──► Disease Phase State Machine                                  │
│              ACTIVE → REMISSION → POST_REMISSION ↔ RELAPSE              │
│              (applied at each visit via apply_visit())                   │
│                                                                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ANALYSIS LAYER                                       │
│                                                                         │
│  Research Analytics (on-demand queries)                                 │
│       │                                                                 │
│       ├──► Cohort Analysis                                              │
│       │      split_patients(queryset, group_by)                         │
│       │      → diabetes, diagnosis, drug exposure, study arm            │
│       │                                                                 │
│       ├──► Survival Analysis                                            │
│       │      Kaplan-Meier + log-rank test                               │
│       │      → composite_kidney_event, eskd, death, remission          │
│       │                                                                 │
│       ├──► Cox Regression                                               │
│       │      Multivariable Cox PH model                                 │
│       │      → hazard ratios, 95% CI, p-values                         │
│       │                                                                 │
│       ├──► Competing Risks                                              │
│       │      Aalen-Johansen CIF                                         │
│       │      → kidney events with death as competing risk               │
│       │                                                                 │
│       ├──► eGFR Slope (LMM)                                            │
│       │      Mixed-effects model comparison                             │
│       │      → between-group slope difference + p-value                 │
│       │                                                                 │
│       ├──► MICE Imputation                                              │
│       │      Multiple imputation for missing lab values                  │
│       │      → Rubin's rules pooling                                    │
│       │                                                                 │
│       └──► Safety Analytics                                             │
│              AE summaries, infection incidence density                   │
│              per-arm SAE tabulation for DSMB                            │
│                                                                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXPORT LAYER                                         │
│                                                                         │
│  Research Dataset (one row per patient)                                 │
│       │                                                                 │
│       ├──► De-identified by default                                     │
│       │      patient_id, sex, age, enrollment_date, cohort              │
│       │      (no name, phone, hospital_id)                              │
│       │                                                                 │
│       ├──► Columns from all domains                                     │
│       │      ├── Baseline: demographics, vitals, diabetes               │
│       │      ├── Labs: baseline creatinine, eGFR, UPCR, albumin        │
│       │      ├── Pathology: diagnosis, MEST-C, ISN/RPS, review status  │
│       │      ├── Treatment: drug exposure flags (ever_*)                │
│       │      ├── Outcomes: followup_days, eGFR slope, remission,       │
│       │      │   ESKD, death, composite kidney, time-to-event days     │
│       │      ├── Biomarkers: PLA2R, complement, anti-dsDNA             │
│       │      └── Safety: n_AE, n_SAE, n_infections                     │
│       │                                                                 │
│       ├──► Per-study ITT dataset                                        │
│       │      + study_code, arm, stratum, enrolled_date, itt             │
│       │                                                                 │
│       └──► Output formats                                               │
│              ├── CSV (writers.write_csv)                                │
│              ├── XLSX (openpyxl)                                        │
│              └── SPSS .sav (pyreadstat)                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Prescription → Treatment Exposure

```
Clinician writes Prescription
    │
    ├── PrescriptionItem[] (drug, dose, frequency, route)
    │
    └── finalize_prescription()
            │
            ├── check_prescription() → SafetyWarning[]
            │       ├── renal dosing: eGFR vs drug threshold
            │       ├── prior intolerance: AE/intolerance history
            │       ├── duplicate therapy: same DrugClass
            │       └── glycaemic effect: steroid/CNI
            │
            ├── prescription.status = FINAL (immutable)
            ├── prescription.content_hash = SHA-256
            │
            └── apply_reconciliation()
                    │
                    ├── Get open TreatmentExposure episodes
                    │   open_by_drug = {drug_id: exposure}
                    │
                    ├── For each PrescriptionItem:
                    │   ├── No open episode → OPEN new
                    │   │   TreatmentExposure(
                    │   │     patient, drug, drug_name,
                    │   │     dose, dose_unit, frequency, route,
                    │   │     start_date=encounter_date,
                    │   │     ongoing=True,
                    │   │     opened_by_encounter=encounter)
                    │   │
                    │   ├── Open episode, same signature → CONTINUE
                    │   │   (no-op)
                    │   │
                    │   └── Open episode, different signature → SPLIT
                    │       Close old: ongoing=False, stop_date, reason=DOSE_CHANGE
                    │       Open new: start_date=today, ongoing=True
                    │
                    └── For open episodes not on Rx → CLOSE
                        TreatmentExposure(
                          ongoing=False,
                          stop_date=encounter_date,
                          stop_reason=reason,
                          closed_by_encounter=encounter)
```

---

## Data Flow: Lab Result → eGFR Auto-Derivation

```
LabResult entered (test=creatinine)
    │
    ├── Record creatinine result
    │   LabResult(patient, test=creatinine, value_numeric, result_date)
    │
    ├── Auto-derive eGFR
    │   ├── Get patient.age, patient.sex
    │   ├── ckd_epi_2021(creatinine_mg_dl, age, sex)
    │   │   Returns (eGFR, formula_version="CKD-EPI-2021-creatinine")
    │   │
    │   └── Create derived result
    │       LabResult(
    │         patient, test=egfr,
    │         value_numeric=eGFR,
    │         result_date=result_date,
    │         source="derived",
    │         derived_from=creatinine_result,
    │         formula_version="CKD-EPI-2021-creatinine")
    │
    └── Update patient cache
        Patient.latest_egfr = eGFR
        (used by prescription safety checks)
```

---

## Data Flow: Clinical Decision Support

```
Patient data available
    │
    ├── Knowledge Rule Engine (knowledge/services.py)
    │   │
    │   ├── extract_patient_features(patient)
    │   │   → features: [edema, hypertension, sle, diabetes, ...]
    │   │   → labs: [lowC3, lowC4, anca, antiGbm, pla2r, ...]
    │   │   → biopsy: [mesangialIga, subepithelial, crescents, ...]
    │   │   → proteinuria: nephrotic/subnephrotic/none
    │   │   → albumin: low/normal
    │   │   → sediment: casts/hematuria/bland
    │   │   → egfrTrend: rapidDecline/reduced/normal
    │   │
    │   ├── evaluate_patient_rules(patient)
    │   │   → For each active KnowledgeBaseEntry:
    │   │       → Evaluate conditions against features
    │   │       → Score = sum of matched rule weights
    │   │   → Group by disease_id, aggregate scores
    │   │   → Return sorted DiseaseScore list
    │   │
    │   └── 87 rules across 9 diseases
    │       iga, membranous, mcd, fsgs, lupus, anca,
    │       antiGbm, infectionRelated, c3
    │
    └── Clinical Decision Support (decision/services.py)
        │
        ├── evaluate_case(patient_features)
        │   → Score patient against 9 DISEASE_PROFILES
        │   → Each profile: base score + weighted rules
        │   → Top 5 scored diseases with confidence%
        │
        ├── classify_phenotype(features)
        │   → "Nephrotic syndrome"
        │   → "Rapidly progressive nephritic syndrome"
        │   → "Mixed nephrotic-nephritic syndrome"
        │   → etc.
        │
        ├── classify_urgency(features, ranked)
        │   → "Urgent nephrology assessment"
        │   → "Prompt nephrology referral"
        │   → "Structured outpatient workup"
        │
        └── build_next_steps(features, ranked, urgency)
            → Confirm Pattern (labs to order)
            → Clinical Actions (biopsy, referrals)
            → Safety Checks (drug contraindications)
```

---

## Data Flow: Outcome Computation Pipeline

```
compute_patient_outcome(patient)
    │
    ├── 1. Extract Time Series
    │   ├── eGFR: LabResult.series(patient, "egfr")
    │   │   → [(date, value), ...] sorted by date
    │   ├── Creatinine: LabResult.series(patient, "creatinine")
    │   └── Proteinuria: merged UTP_24h + UPCR
    │       → prefer_upcr=True for lupus (KDIGO LN)
    │
    ├── 2. Determine Index Date
    │   ├── enrollment_date (if set)
    │   └── else: min(earliest lab date, earliest encounter date)
    │
    ├── 3. Compute Baseline Values
    │   ├── baseline_egfr = first eGFR value
    │   ├── baseline_creatinine = first creatinine value
    │   └── baseline_proteinuria = first UTP/UPCR value
    │
    ├── 4. Kidney-Function Endpoints
    │   ├── sustained_40_decline: first eGFR ≤ 60% baseline (sustained on all later)
    │   ├── sustained_50_decline: first eGFR ≤ 50% baseline (sustained on all later)
    │   └── doubling_creatinine: first Cr ≥ 2x baseline (sustained on all later)
    │
    ├── 5. Hard Endpoints (from ClinicalEvent)
    │   ├── ESKD: dialysis/transplant event OR sustained eGFR < 15
    │   ├── death: ClinicalEvent(Type=DEATH)
    │   └── composite_kidney_event: earliest of {ESKD, ≥50% decline, death}
    │
    ├── 6. Proteinuria Remission (disease-specific)
    │   ├── disease_key() → igan/mn/lupus/fsgs/mcd/aav/other
    │   ├── complete_remission: sustained < 0.3 (or < 0.5 + eGFR preserved for lupus)
    │   ├── partial_remission: sustained ≥50% reduction & < 3.5
    │   ├── igan_proteinuria_response: sustained ≥30% reduction or < 0.3
    │   └── First-achieved dates → time-to-event endpoints
    │
    ├── 7. Proteinuria Relapse
    │   └── First UPCR ≥ 1.0 g/day strictly after any remission date
    │
    ├── 8. Last Contact Date
    │   └── max(latest lab date, latest encounter date, latest event date)
    │
    └── 9. Write PatientOutcome
        └── update_or_create(patient, defaults={...})
            → Re-runnable at any time
            → Denormalized "one row per patient" for ML/analysis
```

---

## Data Flow: Research Export Assembly

```
build_dataset(queryset, identified=False, study=None)
    │
    ├── For each patient in queryset:
    │   │
    │   ├── Demographics (from Patient)
    │   │   patient_id, sex, age_at_enrollment, enrollment_date, cohort
    │   │
    │   ├── Baseline (from BaselineAssessment)
    │   │   bmi, bp, hba1c, dm_duration, presentation, retinopathy
    │   │
    │   ├── Baseline Labs (from LabResult, first values)
    │   │   creatinine, egfr, upcr, albumin, hemoglobin, c3, c4, pla2r
    │   │
    │   ├── Pathology (from GNDiagnosis + IgANScore + LupusPathology)
    │   │   broad_group, MEST-C, ISN/RPS, FSGS variant, review_status
    │   │
    │   ├── Treatment Exposure Flags (from TreatmentExposure)
    │   │   ever_raasi, ever_sglt2i, ever_finerenone, ever_hcq,
    │   │   ever_steroid, ever_mmf, ever_rituximab, ever_cni,
    │   │   ever_cyclophosphamide, ever_azathioprine, ever_budesonide
    │   │
    │   ├── Outcomes (from PatientOutcome)
    │   │   followup_days, latest_egfr, egfr_slope, remission_status,
    │   │   complete_remission, partial_remission, igan_response,
    │   │   sustained_40/50_decline, eskd, death, composite_kidney,
    │   │   time-to-event days for each endpoint
    │   │
    │   ├── Biomarkers (from BiomarkerKinetics)
    │   │   pla2r_baseline, pla2r_pct_decline, pla2r_50pct_decline,
    │   │   pla2r_immunological_remission, c3_recovered
    │   │
    │   └── Safety (from AdverseEvent)
    │       n_adverse_events, n_serious_ae, n_infections
    │
    ├── If study specified:
    │   └── Add: study_code, arm, stratum, enrolled_date, itt
    │
    └── Output: (columns, rows)
        → writers.write_csv() / write_xlsx() / write_sav()
```

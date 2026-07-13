# Data Lineage & Flow Tracing

## Patient Data Lifecycle

```
Registration → Encounters → Labs → Biopsy → Treatment → Outcomes → Clinical Profile
```

### 1. Patient Registration Data

**Source:** `patients/models.py:46` (Patient model)  
**Fields:** patient_id, name, phone, sex, dob, enrollment_date, site, cohort, diabetes_status, primary_diagnosis  
**Consumed by:** All clinical modules via FK  
**API:** `POST/GET/PATCH /api/v1/patients/` (PatientViewSet, `api/views.py:32`)  
**Events emitted:** `patient.registered`, `patient.updated`  
**Profile impact:** Sets `features_snapshot` base fields, triggers differential computation

### 2. Encounter Data Flow

**Source:** `encounters/` app (ClinicalEncounter model)  
**Relationship:** FK → Patient  
**Consumed by:** `analytics/services/outcomes.py` (index_date, last_contact), `operational_intelligence.py` (overdue visits), `care_pathway.py` (follow-up gaps)  
**Events:** `encounter.created` → `_on_patient_event` → `reason_about_patient()`  
**Profile fields impacted:** `care_pathway.deviations` (if overdue), `milestones` (indirect via phase changes)

### 3. Lab Result Data Flow

**Source:** `labs/` app (LabResult model)  
**Relationship:** FK → Patient  
**Consumed by:**
- `analytics/services/outcomes.py`: `_series()` fetches eGFR/Cr/proteinuria series, computes remission/relapse/ESKD dates
- `knowledge/services.py`: `extract_patient_features()` reads latest_egfr, proteinuria levels, serology markers
- `clinical_reasoning/services/engine.py`: eGFR trend in trajectory assessment, risk assessment
  
**Events:** `lab_result.created` → `_on_lab_event` → `compute_patient_outcome()` + `reason_about_patient()`  
**Profile fields impacted:** `features_snapshot.latest_egfr`, `features_snapshot.proteinuria`, `disease_trajectory.trend`, `risk_assessment`

### 4. Biopsy Data Flow

**Source:** `pathology/` app (Biopsy model)  
**Relationship:** FK → Patient  
**Consumed by:**
- `clinical_reasoning/services/disease_milestones.py:72` → `_check_biopsy_milestone()` adds "biopsy" milestone
- `care_pathway_engine.py:164` → deviation detection if biopsy missing
- `engine.py:114` → information gap detection if no biopsy
- `explainability.py:89` → triggering findings

**Events:** `biopsy.created` → `_on_patient_event` → `reason_about_patient()`  
**Profile fields impacted:** `milestones[]`, `care_pathway.deviations`, `information_gaps[]`, `differential`

### 5. Treatment Data Flow

**Source:** `treatments/` app (TreatmentExposure model)  
**Relationship:** FK → Patient  
**Consumed by:**
- `disease_milestones.py:112` → `_check_treatment_milestones()` detects treatment_started / treatment_switched
- `care_pathway.py` → treatment gaps (active disease without immunosuppression)
- `operational_intelligence.py` → `_count_active_without_tx()`

**Events:** `treatment_exposure.created/updated` → `_on_patient_event` → `reason_about_patient()`  
**Profile fields impacted:** `milestones[]`, `care_pathway.care_gaps[]`

### 6. Outcome Data Flow

**Source:** `analytics/services/outcomes.py` → `compute_patient_outcome()` → `PatientOutcome` model  
**Relationship:** FK → Patient  
**Consumed by:** Event handlers on lab/clinical events → profile trajectory  
**Key computation:** `_proteinuria_outcome()` determines remission dates per disease-specific rules (LN/MCD complete vs partial remission thresholds)

### 7. ClinicalProfile Aggregation

**Source:** `clinical_reasoning/models.py:11`  
**Fields populated by reasoning pipeline** (`engine.py:23`):
| Profile Field | Source Module | Service Function |
|---|---|---|
| `features_snapshot` | knowledge | `extract_patient_features()` |
| `differential` | knowledge | `_build_differential(rule_results)` |
| `disease_trajectory` | disease_trajectory | `assess_trajectory()` |
| `care_pathway` | care_pathway_engine | `compute_pathway_summary()` |
| `risk_assessment` | engine | `_assess_risk()` |
| `evidence_summary` | engine | `_gather_evidence_summary()` |
| `reasoning_chain` | engine | `_build_reasoning_chain()` |
| `information_gaps` | engine | `_identify_information_gaps()` |
| `milestones` | disease_milestones | `detect_milestones()` |

### 8. Analytics Outcome Computation

**Source:** `analytics/services/outcomes.py`  
**Data inputs:**
- `_series()` → LabResult queryset filtered by patient + test code
- `_proteinuria_series()` → merged UPCR + UTP + dipstick series
- `_disease_key()` → maps primary_diagnosis → remission rule key
- `last_contact()` → latest of enrollment, any lab, any encounter

**Key logic:** Disease-specific remission criteria, sustained eGFR drop detection, proteinuria relapse detection

---

## Data Quality Metrics (from enterprise_readiness.py:111)

| Metric | Source |
|---|---|
| profile_coverage_pct | ClinicalProfile count vs Patient count |
| patients_with_egfr | Patient.objects.filter(latest_egfr__isnull=False) |
| incomplete_patients | Total - patients_with_egfr |
| last_profile_update | ClinicalProfile.objects.latest("last_updated") |

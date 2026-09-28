# Aggregate Catalog

**Version:** 2.5  
**Pattern:** Each aggregate has a single Aggregate Root; all external access goes through the root

---

## Aggregate 1: Patient

**Root Entity:** `Patient`  
**Repository:** `Patient.objects` (Django ORM)  
**Consistency Boundary:** All direct Patient attributes + related clinical data queried through Patient

### Composition

| Child | Type | Relationship | Invariant |
|---|---|---|---|
| Site | Reference via FK | N:1 (shared reference) | Site must be active |
| Consent | Conceptually owned | 1:N | One active consent per consent_type |
| ClinicalProfile | Owned (1:1) | 1:1 | Created automatically on first reasoning |
| ClinicalInsight | Owned | 1:N | Must reference valid Patient |
| DecisionRequest | Reference via FK | 1:N | DecisionRequest is its own aggregate |
| PatientOutcome | Reference via FK | 1:N | Outcome is its own aggregate |

### Invariants
1. `patient_id` must be globally unique and follow BGD-NNNNN pattern
2. `registration_status` transitions must be valid (Suspected → Confirmed → Inactive)
3. `current_phase` must be a valid DiseasePhase value
4. If `registration_status` is inactive, the patient should not generate new clinical events

### Commands
- `registerPatient(name, sex, dob, ...)` → PatientRegistered
- `updateDemographics(patientId, fields)` → PatientUpdated
- `changeRegistrationStatus(patientId, newStatus)` → PatientStatusChanged

### Events Emitted
- `patient.registered`
- `patient.updated`

---

## Aggregate 2: ClinicalProfile

**Root Entity:** `ClinicalProfile`  
**Repository:** `ClinicalProfile.objects`  
**Consistency Boundary:** All JSON fields are updated atomically within a single transaction

### Composition

| Child | Type | Relationship | Invariant |
|---|---|---|---|
| features_snapshot | Value Object (JSON) | Owned | Must be json_safe |
| differential | Value Object (JSON list) | Owned | Sorted by score descending |
| disease_trajectory | Value Object (JSON) | Owned | Must include trend field |
| care_pathway | Value Object (JSON) | Owned | Must include stage field |
| risk_assessment | Value Object (JSON) | Owned | Must include overall field |
| evidence_summary | Value Object (JSON) | Owned | Must include grade_distribution |
| reasoning_chain | Value Object (JSON list) | Owned | Steps ordered sequentially |
| information_gaps | Value Object (JSON list) | Owned | Deduplicated by field |
| milestones | Value Object (JSON list) | Owned | Merged with existing; no duplicate milestone_types |

### Invariants
1. Version must increment monotonically with each save
2. Last_updated must reflect the most recent recompute
3. Differential must be sorted by score descending
4. Milestones must not contain duplicate milestone_type entries
5. Patient FK must be unique (OneToOne constraint)

### Commands
- `recompute(patient)` → ClinicalProfileUpdated, ReasoningCompleted
- `getExplainability(profileId)` → ExplainabilityReport (read-only query)

### Events Emitted
- `clinical_profile.updated`
- `care_pathway.updated`
- `reasoning.completed`

---

## Aggregate 3: KnowledgeBaseEntry

**Root Entity:** `KnowledgeBaseEntry`  
**Repository:** `KnowledgeBaseEntry.objects`  
**Consistency Boundary:** The rule definition + all versioning + review history

### Composition

| Child | Type | Relationship | Invariant |
|---|---|---|---|
| KnowledgeBaseVersion | Entity | 1:N | Version numbers must be sequential and unique per entry |
| RuleReview | Entity | 1:N | Only one review can be PENDING at a time |
| RuleTestResult | Entity | 1:N | Must include expected vs actual score |
| EvidenceEntry | Entity | 1:N | Evidence references must have DOI or PMID |

### Invariants
1. `entry_id` must be globally unique (KB-DISEASE-NNN)
2. Only ACTIVE status rules are evaluated against patients
3. Rule must belong to a valid GuidelineSource
4. Status transitions: DRAFT → REVIEWED → ACTIVE → RETIRED (no skipping)
5. Version history is append-only (never delete)

### Commands
- `createRule(entryId, diseaseId, ruleData, ...)` → RuleCreated
- `activateRule(entryId)` → RuleActivated
- `retireRule(entryId)` → RuleRetired
- `testRule(entryId, testCase)` → RuleTested

### Events Emitted
- (via event system, currently manual dispatch)

---

## Aggregate 4: DecisionRequest

**Root Entity:** `DecisionRequest`  
**Repository:** `DecisionRequest.objects`  
**Consistency Boundary:** Request + Result are created atomically

### Composition

| Child | Type | Relationship | Invariant |
|---|---|---|---|
| DecisionResult | Entity | 1:1 | Created atomically with the request |
| traceability | Value Object (JSON list) | Owned | Must reference valid KB entry_ids |

### Invariants
1. Each DecisionRequest must produce exactly one DecisionResult
2. Override can only be set on an existing DecisionResult
3. Input_snapshot captures the state at time of request (immutable)

### Commands
- `requestDecision(patient, encounter, inputs)` → DecisionRequested, RecommendationGenerated
- `overrideDecision(requestId, clinicianOverride)` → RecommendationOverridden

---

## Aggregate 5: ClinicalEncounter

**Root Entity:** `ClinicalEncounter`  
**Repository:** `ClinicalEncounter.objects`  
**Consistency Boundary:** Encounter attributes + related encounters for the same patient

### Invariants
1. Must reference an existing Patient
2. Encounter date must not be in the future (validation)
3. Encounter status transitions: Created → Updated → Completed

---

## Aggregate 6: Biopsy

**Root Entity:** `Biopsy`  
**Repository:** `Biopsy.objects`  
**Consistency Boundary:** Biopsy + all pathology reviews

### Composition

| Child | Type | Relationship | Invariant |
|---|---|---|---|
| PathologyReview | Entity | 1:N | Only one review can be is_final |

### Invariants
1. Once review_status is finalized, no new reviews can be added
2. At least one pathology review must be marked is_final for the biopsy to be finalized

---

## Aggregate 7: TreatmentExposure

**Root Entity:** `TreatmentExposure`  
**Repository:** `TreatmentExposure.objects`  
**Invariants:**
1. Start_date must be before end_date
2. Cannot have overlapping active TreatmentExposures for the same drug class (clinical rule)

---

## Aggregate 8: Study

**Root Entity:** `Study`  
**Repository:** `Study.objects`  
**Invariants:**
1. Status transitions: Planned → Recruiting → Active → Completed → Closed
2. Patient can only be enrolled if study is Recruiting or Active

---

## Aggregate 9: LabResult

**Root Entity:** `LabResult`  
**Repository:** `LabResult.objects`  
**Invariants:**
1. Must reference an existing Patient
2. Must have either value_numeric or value_text populated
3. Sample_date must not be after result_date

---

## Aggregate 10: Prescription

**Root Entity:** `Prescription`  
**Repository:** `Prescription.objects`  
**Invariants:**
1. Status transitions: Draft → Finalized → Reconciled
2. Each version must increment

---

## Aggregate Ownership Summary

| Aggregate Root | Owns | References | Referenced By |
|---|---|---|---|
| Patient | ClinicalInsight (owned), Consent (owned) | Site | All aggregates |
| ClinicalProfile | (9 value object collections) | Patient | Explainability queries |
| KnowledgeBaseEntry | KnowledgeBaseVersion, RuleReview, RuleTestResult, EvidenceEntry | GuidelineSource | DecisionRequest, ClinicalProfile |
| DecisionRequest | DecisionResult | Patient, ClinicalEncounter | — |
| ClinicalEncounter | — | Patient | DecisionRequest, Prescription |
| Biopsy | PathologyReview | Patient | ClinicalProfile (milestones) |
| TreatmentExposure | — | Patient | ClinicalProfile (milestones) |
| Study | StudyEnrollment | — | ClinicalProfile (through matching) |
| LabResult | — | Patient | PatientOutcome, ClinicalProfile |
| Prescription | — | Patient, ClinicalEncounter | — |
| Site | — | — | Patient, UserSiteRole |
| Event | — | — | ClinicalProfile (through handlers) |

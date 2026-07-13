# GDES Module Integration Report

## Cross-Module Consistency Audit & Domain Model Audit

Covers: GDES V3.8 Objectives 2 & 6

---

## 1. Data Ownership Boundaries

| Domain | Aggregate Root | Owned By | Shared (read-only) With |
|--------|---------------|----------|------------------------|
| Patient Registry | `Patient` | `patients` | All apps |
| Encounters | `ClinicalEncounter` | `encounters` | `clinical`, `labs`, `prescriptions` |
| Labs | `LabResult` | `labs` | `analytics`, `biomarkers`, `knowledge`, `clinical_reasoning` |
| Pathology | `Biopsy` | `pathology` | `knowledge` (feature extraction), `clinical_reasoning` |
| Treatments | `DrugMaster` + `TreatmentExposure` | `treatments` | `prescriptions`, `knowledge`, `clinical_reasoning` |
| Prescriptions | `Prescription` | `prescriptions` | `encounters` (PROTECT FK) |
| Knowledge | `KnowledgeBaseEntry` | `knowledge` | `clinical_reasoning` (read-only) |
| Decision | `DecisionRequest` / `DecisionResult` | `decision` | `clinical_reasoning` |
| Clinical Reasoning | `ClinicalProfile` + `ClinicalInsight` | `clinical_reasoning` | — |
| Analytics | `PatientOutcome` | `analytics` | `clinical_reasoning` (read-only) |
| Scheduling | `ScheduledVisit` | `scheduling` | `reminders` |

## 2. Event Ownership

| Domain | Events Emitted | Events Consumed | Health |
|--------|---------------|-----------------|--------|
| Patient | `patient.registered`, `patient.updated` | — | ✓ |
| Encounters | `encounter.created`, `encounter.updated`, `clinical_event.created` | — | ✓ |
| Labs | `lab_result.created`, `lab_result.updated` | — | ✓ |
| Pathology | `biopsy.created` | — | ✓ |
| Treatments | `treatment_exposure.created`, `treatment_exposure.updated` | — | ✓ |
| Prescriptions | `prescription.created` | — | ✓ |
| Clinical Reasoning | — | All of the above | ✓ (10 handlers) |
| Safety | `safety_alert.raised` (defined, **never emitted**) | — | ❌ Orphan |
| Scheduling | `follow_up.scheduled`, `visit.overdue` (defined, **never emitted**) | — | ❌ Orphan |
| Reminders | `reminder.sent` (defined, **never emitted**) | — | ❌ Orphan |
| Decision | `decision.requested`, `recommendation.generated` (defined, **never emitted**) | — | ❌ Orphan |
| Others | `death.recorded`, `prescription.finalized`, `medication.started`, `outcome.*`, `disease_trajectory.*`, `clinical_profile.*`, `care_pathway.*`, `reasoning.completed` (defined, **never emitted**) | — | ❌ Orphan |

**18 of 31 event types are orphans** — defined in `event_types.py` but never dispatched by any code.

## 3. Duplicated Business Logic

### Finding 1: Two independent scoring engines

| Engine | File | Source | Scope |
|--------|------|--------|-------|
| Knowledge Engine | `knowledge/services.py:evaluate_patient_rules()` | DB-backed `KnowledgeBaseEntry` rules | 200+ rules across 17 diseases |
| Decision Engine | `decision/services.py:evaluate_case()` | Hardcoded `DISEASE_PROFILES` list | 9 disease profiles, static |

**Risk:** The two engines can (and will) diverge. The decision engine has no connection to the knowledge platform. If a KB rule is updated, the decision engine's static copy is stale. The decision engine is only used by the `DecisionViewSet` API endpoint which snapshots the patient dict at request time — it never sees live KB updates.

### Finding 2: Two independent eGFR calculations

| Function | File | Formula |
|----------|------|---------|
| `ckd_epi_2021()` | `labs/services/egfr.py:15-36` | CKD-EPI 2021 race-free |
| `egfr_ckd_epi_2021()` | `decision/services.py:12-32` | CKD-EPI 2021 race-free |

Both implement the same formula independently. They are mathematically identical but a bug fix in one could leave the other stale. The lab-derived eGFR is authoritative (auto-computed on creatinine entry); the decision engine version is used only for the static `evaluate_case()`.

### Finding 3: Two proteinuria-to-category mappings

| Function | File | Output |
|----------|------|--------|
| `_classify_proteinuria()` | `knowledge/services.py:220-240` | `"nephrotic"` / `"subnephrotic"` / `"none"` |
| `proteinuria_category()` | `decision/services.py:68-74` | `"nephrotic"` / `"subnephrotic"` / `"normal"` |

Different naming for the same clinical concept (`"none"` vs `"normal"`). This is a data inconsistency risk — the same patient could show "none" in one view and "normal" in another.

## 4. Circular Dependency Analysis

**No circular imports detected at module import level.** All deferred imports (inside functions) prevent circularity:
- `knowledge/services.py` uses deferred `from labs.models import LabResult` (inside `extract_patient_features`)
- `patients/services.py` uses deferred `from prescriptions.models import Prescription`
- `timeline/services.py` uses deferred imports for encounters, clinical, pathology

The `patients.workflow` module is the shared enum hub — it's intentionally placed here so all apps can import `DiseasePhase`, `RegistrationStatus` etc. without circularity.

## 5. Transaction Consistency

### Wrapped in `@transaction.atomic`

| Function | File:Line | Domain |
|----------|-----------|--------|
| `reason_about_patient()` | `engine.py:22` | Clinical reasoning |
| `finalize_prescription()` | `finalize.py:23` | Prescriptions |
| `apply_reconciliation()` | `reconciliation.py:122` | Treatments |
| `record_result()` | `results.py:55` | Labs |
| `order_tests()` | `ordering.py:25` | Labs |
| `order_panel()` | `ordering.py:14` | Labs |
| `record_review()` | `review.py:25` | Pathology |
| `generate_schedule()` | `schedule.py:72` | Scheduling |
| `delete_patient_cascade()` | `services.py:14` | Patients |

### NOT wrapped — potential partial-save risk

| Function | File:Line | Risk |
|----------|-----------|------|
| `followup_create()` | `views.py:342-374` | Encounter saved, then labs saved one-by-one. Crash after `enc.save()` loses labs |
| `baseline_edit()` | `views.py:322-336` | Same: baseline saved, then labs saved one-by-one |
| `biopsy_create()` | `views.py:462-521` | Biopsy saved, then diagnosis saved, then score forms saved. Crash after `biopsy.save()` loses diagnosis/scores |
| `patient_create()` | `views.py:126-135` | Patient saved; no follow-up data yet (design: separate request) |

## 6. Repository Boundary Violations

| Violation | Location | Details |
|-----------|----------|---------|
| `knowledge` queries `LabResult` directly | `knowledge/services.py:88-89` | `LabResult.objects.filter(patient=patient)` — bypasses labs repository |
| `knowledge` queries `Biopsy` directly | `knowledge/services.py:169` | `patient.biopsies.order_by("-biopsy_date")` — bypasses pathology repository |
| `clinical_reasoning` imports from `knowledge` | `engine.py` | `evaluate_patient_rules()` is a direct function call, not an event |
| `clinical_reasoning` imports from `analytics` | `event_handlers.py:42` | `compute_patient_outcome()` — direct call; no event-driven interface between these domains |
| `knowledge` imports from `patients.workflow` | `services.py` | Imports `DiseasePhase`, `RegistrationStatus` — low risk, they're enums |

**Assessment:** These are acceptable within a Django monolith. The repository boundaries are logical rather than physical. The primary risk is that changes to `LabResult` or `Biopsy` models could break `knowledge/services.py` without an explicit interface contract.

## 7. Aggregate Root Analysis

| Aggregate | Root | Entities | Invariants Enforced? |
|-----------|------|----------|---------------------|
| **Patient** | `Patient` | `Site`, `UserSiteRole`, `BaselineAssessment`, `PatientOutcome`, `BiomarkerKinetics`, `ClinicalProfile` | Partial — baseline is OneToOne (enforced at DB level); outcomes/biomarkers/profile are computed; no invariant requiring them for all registered patients |
| **Encounter** | `ClinicalEncounter` | `Admission`, `RelapseEpisode`, `ClinicalEvent`, `ClinicalAssessment`, `VitalSign` | Weak — no invariant preventing an encounter without an assessment; `RelapseEpisode` can reference any encounter |
| **Biopsy** | `Biopsy` | `GNDiagnosis`, `IgANScore`, `LupusPathology`, `FSGSPathology`, `MembranousPathology`, `BiopsyImage`, `PathologyReview` | Weak — diagnosis is expected but no DB constraint enforces it; score models are OneToOne (enforced) |
| **Labs** | `LabResult` | `LabOrder`, `LabOrderItem`, `LabTest` | Order → Items → Results chain is enforced; `LabOrderItem` has `UniqueConstraint` |
| **Prescription** | `Prescription` | `PrescriptionItem` | Version uniqueness is enforced; status (draft→final) is application-level |
| **Knowledge** | `KnowledgeBaseEntry` | `KnowledgeBaseVersion`, `RuleReview`, `RuleTestResult`, `EvidenceEntry` | Version sequence enforced; lifecycle state transitions enforced via `transition_to()` |
| **Decision** | `DecisionRequest` | `DecisionResult` | OneToOne, enforced at DB level |
| **ClinicalProfile** | `ClinicalProfile` | `ClinicalInsight` | OneToOne to patient, enforced; version increments; insights are dependent entities |

## 8. Summary of Issues Found

| # | Severity | Issue | Location |
|---|----------|-------|----------|
| 1 | 🔴 | `Patient.clean()` has NameError — `date` not imported | `patients/models.py:106` |
| 2 | 🔴 | `delete_patient_cascade()` crashes — `patient.delete()` raises PermissionDenied | `patients/services.py:31` |
| 3 | 🟠 | Two independent scoring engines with no syncing mechanism | `decision/services.py` vs `knowledge/services.py` |
| 4 | 🟠 | N+1 on `biopsy.diagnosis` in feature extraction | `knowledge/services.py:170` |
| 5 | 🟠 | N+1 on `encounter.clinical_assessment` in feature extraction | `knowledge/services.py:81` |
| 6 | 🟠 | Inconsistent proteinuria category labels: "none" vs "normal" | `knowledge/services.py:240` vs `decision/services.py:74` |
| 7 | 🟠 | 18 orphan event types defined but never emitted | `events/event_types.py` |
| 8 | 🟡 | No `@transaction.atomic` on biopsy_create view | `clinic/views.py:462-521` |
| 9 | 🟡 | No `@transaction.atomic` on followup_create view | `clinic/views.py:342-374` |
| 10 | 🟡 | Lab saves silently swallow exceptions in `_save_labs` | `clinic/views.py:55-56` |
| 11 | 🟢 | EventSubscription model exists but is never read by dispatcher | `events/models.py`, `events/dispatcher.py` |
| 12 | 🟢 | `Event.processed` field never transitions to True | `events/dispatcher.py` |

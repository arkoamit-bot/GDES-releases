# GDES System Integration Map

> Part of GDES V3.7 System Certification (Objective 1)
> Documents every Django app, its purpose, models, dependencies, events, APIs, commands, services, and background tasks.

---

## Table of Contents

1. [Patient Domain](#1-patient-domain)
2. [Clinical Domain](#2-clinical-domain)
3. [Laboratory Domain](#3-laboratory-domain)
4. [Pathology Domain](#4-pathology-domain)
5. [Treatment Domain](#5-treatment-domain)
6. [Prescription Domain](#6-prescription-domain)
7. [Knowledge Platform](#7-knowledge-platform)
8. [Decision Engine](#8-decision-engine)
9. [Clinical Reasoning](#9-clinical-reasoning)
10. [Analytics Domain](#10-analytics-domain)
11. [Monitoring & Outcomes](#11-monitoring--outcomes)
12. [Safety Domain](#12-safety-domain)
13. [Scheduling Domain](#13-scheduling-domain)
14. [Reminders Domain](#14-reminders-domain)
15. [Study Domain](#15-study-domain)
16. [Audit Domain](#16-audit-domain)
17. [Users & Auth](#17-users--auth)
18. [Timeline Domain](#18-timeline-domain)
19. [Events Bus](#19-events-bus)
20. [Export Layer](#20-export-layer)
21. [API Layer](#21-api-layer)
22. [FHIR Layer](#22-fhir-layer)
23. [Clinic Dashboard](#23-clinic-dashboard)
24. [System Dependencies Diagram](#24-system-dependencies-diagram)

---

## 1. Patient Domain

### App: `patients`

**Purpose:** Core registry — patient enrollment, site management, and patient lifecycle (registration, status tracking, phase transitions).

### Models

| Model | Key Fields | FKs (external) | Constraints |
|-------|-----------|----------------|-------------|
| `Site` | `code` (unique), `name`, `config` (JSON) | — | ordering: `["code"]` |
| `Patient` | `patient_id` (unique, auto), `hospital_id`, `name`, `phone`, `sex`, `dob`, `primary_diagnosis`, `latest_egfr`, `registration_status`, `current_phase` | `site` → `Site` (PROTECT, nullable) | ordering: `["patient_id"]` |
| `UserSiteRole` | `role` (choices), `is_primary` | `user` → `auth.User` (CASCADE), `site` → `Site` (CASCADE) | `unique_together = [("user", "site")]` |

### Dependencies (imports from other apps)

- None (self-contained; `Site` and `Patient` are foundational)

### Services

- `patients/services.py:delete_patient_cascade(patient)` — FK-safe deletion of a patient and all clinical records (deferred imports: `prescriptions.Prescription`, `labs.LabOrder`)

### Events

- **Emits:** `patient.registered` (on create), `patient.updated` (on update) — via `events/signal_handlers.py` post_save bridge
- **Subscribes to:** None

### API

- `SiteViewSet` — `/api/sites/` (CRUD, search: code/name)
- `PatientViewSet` — `/api/patients/` (CRUD, search: id/name/hospital_id, site-filtered)
- `UserSiteRoleViewSet` — `/api/user-site-roles/` (CRUD, filter by user/site/role, select_related)

### Management Commands

| Command | Purpose |
|---------|---------|
| `validate_patients` | Scan for duplicates, missing fields, coverage gaps (--csv, --threshold) |
| `backup_db` | Timestamped SQLite backup to Backups/ (--reason, --list) |
| `restore_db` | Restore from backup with pre-restore snapshot (--list, --yes) |
| `delete_patient` | Delete single patient + data (-yes to execute) |
| `reset_demo_data` | Remove demo/synthetic patients (--all, --prefixes, --yes) |
| `check_data_integrity` | 8-category integrity scan across all clinical models |

### Admin

- `PatientAdmin` — list/search/filter/fieldsets, custom action: `delete_patient_and_all_data` (superuser-only)

---

## 2. Clinical Domain

### App: `encounters`

**Purpose:** Patient visits — encounter tracking, admissions, relapses, and clinical milestone events.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `ClinicalEncounter` | `encounter_date`, `encounter_type`, `systolic_bp`, `diastolic_bp`, `disease_phase`, `treatment_adjusted`, `next_due_date` | `patient` → `Patient` (PROTECT); `seen_by` → `auth.User` (PROTECT) | Index: `[patient, encounter_date]` |
| `Admission` | `admit_date`, `discharge_date`, `ward`, `reason`, `baseline_captured` | `patient` → `Patient` (CASCADE); `biopsy` → `pathology.Biopsy` (SET_NULL) | Index: `[patient, admit_date]` |
| `RelapseEpisode` | `relapse_date`, `relapse_type`, `criteria`, `action_taken` | `patient` → `Patient` (CASCADE); `encounter` → `ClinicalEncounter` (SET_NULL) | Index: `[patient, relapse_date]` |
| `ClinicalEvent` | `event_type`, `event_date`, `notes` | `patient` → `Patient` (CASCADE); `encounter` → `ClinicalEncounter` (SET_NULL) | Index: `[patient, event_type, event_date]` |

### Dependencies

- `patients.Patient`
- `pathology.Biopsy` (through `Admission`)

### Services

- No dedicated `services.py` — business logic in admin and views

### Events

- **Emits:** `encounter.created`, `encounter.updated` (on save), `clinical_event.created` (on ClinicalEvent create), `hard_kidney_endpoint.reached` (defined, not emitted), `death.recorded` (defined, not emitted)
- **Subscribes to:** None

### API

- `ClinicalEncounterViewSet` — `/api/encounters/` (CRUD)
- `ClinicalEventViewSet` — `/api/events/` (CRUD)

### Admin

- `ClinicalEncounterAdmin` — search/filter/fieldsets/date_hierarchy
- `ClinicalEventAdmin` — search/filter/date_hierarchy

---

### App: `baseline`

**Purpose:** One-time baseline assessment at enrollment — demographics, medical history, anthropometry, vitals, diabetes profile, presentation.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `BaselineAssessment` | `assessment_date`, `division_residence`, `socioeconomic_status`, `education`, `occupation`, `height_cm`, `weight_kg`, `bmi` (auto), `bmi_category` (auto), `systolic_bp`, `diastolic_bp`, `dm_duration_years`, `hba1c`, `presentation_syndrome`, `presentation_syndromes` (JSON), `oedema_grade`, `pulse_bpm`, `temperature_c`, `fundoscopy` | `patient` → `Patient` (OneToOne, CASCADE) | ordering: `["patient"]` |

### Dependencies

- `patients.Patient`

### Events

- None

### Admin

- `BaselineAssessmentAdmin` — search/filter/autocomplete/readonly (bmi auto-derived)

---

## 3. Laboratory Domain

### App: `labs`

**Purpose:** Lab test catalog, ordering panels, order management, and result recording with auto-flagging.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `LabTest` | `code` (unique), `name`, `loinc`, `default_unit`, `value_type`, `ref_low`, `ref_high`, `is_derived`, `is_active` | — | ordering: `["name"]` |
| `LabPanel` | `code` (unique), `name` | `tests` → `LabTest` (M2M) | — |
| `LabOrder` | `ordered_date`, `status` (choices) | `encounter` → `ClinicalEncounter` (PROTECT); `patient` → `Patient` (CASCADE) | Index: `[patient, ordered_date]` |
| `LabOrderItem` | — | `order` → `LabOrder` (CASCADE); `test` → `LabTest` (PROTECT) | `UniqueConstraint(["order", "test"], name="uniq_order_test")` |
| `LabResult` | `value_numeric`, `value_text`, `unit`, `sample_date`, `result_date`, `flag` (auto), `source`, `formula_version` | `patient` → `Patient` (CASCADE); `test` → `LabTest` (PROTECT); `order_item` → `LabOrderItem` (SET_NULL); `derived_from` → `self` (SET_NULL) | Index: `[patient, test, result_date]` |

### Dependencies

- `patients.Patient`
- `encounters.ClinicalEncounter`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `lab_result.created`, `lab_result.updated` (on save)
- **Subscribes to:** None

### API

- `LabResultViewSet` — `/api/lab-results/` (CRUD, select_related test)

### Management Commands

| Command | Purpose |
|---------|---------|
| `seed_labs` | Idempotently populate 23 lab tests + 4 panels |

### Admin

- `LabTestAdmin`, `LabPanelAdmin`, `LabOrderAdmin` (with `LabOrderItemInline`), `LabResultAdmin` — full CRUD

---

## 4. Pathology Domain

### App: `pathology`

**Purpose:** Kidney biopsy documentation — biopsy data, GN-specific diagnoses (IgAN, lupus, FSGS, membranous), scoring systems (Oxford MEST-C, ISN/RPS), and pathology review workflow.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `Biopsy` | `biopsy_date`, `adequacy`, `indication`, `result_category`, `review_status`, `total_glomeruli`, `global_sclerosis_pct`, `ifta_pct`, `crescent_pct`, `crescents_present`, `dkd_lesion_present` | `patient` → `Patient` (CASCADE) | ordering: `["patient", "-biopsy_date"]` |
| `GNDiagnosis` | `diagnosis` (choices), `broad_group`, `pathogenesis_group`, `primary_secondary` | `biopsy` → `Biopsy` (OneToOne, CASCADE) | — |
| `IgANScore` | `M`, `E`, `S` (0-1), `T`, `C` (0-2) | `biopsy` → `Biopsy` (OneToOne, CASCADE) | — |
| `LupusPathology` | `isn_rps_class` (I-VI), `activity_index` (0-24), `chronicity_index` (0-12) | `biopsy` → `Biopsy` (OneToOne, CASCADE) | — |
| `FSGSPathology` | `variant` (NOS/perihilar/cellular/tip/collapsing), `primary_secondary` | `biopsy` → `Biopsy` (OneToOne, CASCADE) | — |
| `MembranousPathology` | `pla2r_tissue`, `thsd7a_tissue`, `mn_stage` (0-4) | `biopsy` → `Biopsy` (OneToOne, CASCADE) | — |
| `BiopsyImage` | `image` (FileField), `stain`, `description` | `biopsy` → `Biopsy` (CASCADE) | — |
| `PathologyReview` | `role` (local/central/adjudication), `review_date`, `diagnosis`, `M/E/S/T/C`, `isn_rps_class`, `fsgs_variant`, `is_final` | `biopsy` → `Biopsy` (CASCADE); `reviewer` → `auth.User` (SET_NULL) | `UniqueConstraint(["biopsy", "role"], name="uniq_biopsy_review_role")` |

### One-to-One Detail Models

The five pathology detail models (`GNDiagnosis`, `IgANScore`, `LupusPathology`, `FSGSPathology`, `MembranousPathology`) are each OneToOne to `Biopsy`. This creates an **entity-attribute-value-like polymorphism** — only the relevant detail model(s) are populated per biopsy.

### Dependencies

- `patients.Patient`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `biopsy.created` (on Biopsy create); `biopsy.finalized` (defined, not emitted)
- **Subscribes to:** None

### API

- `BiopsyViewSet` — `/api/biopsies/` (CRUD, read-only: `review_status`)
- `PathologyReviewViewSet` — `/api/pathology-reviews/` (CRUD, read-only: `is_final`)

### Admin

- `BiopsyAdmin` — 7 inlines (all detail models + reviews + images), search/filter/date_hierarchy

---

## 5. Treatment Domain

### App: `treatments`

**Purpose:** Drug formulary (DrugMaster) and patient-level treatment exposure tracking.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `DrugMaster` | `generic_name` (unique), `brand_names` (JSON), `drug_class`, `available_strengths` (JSON), `default_frequency`, `default_route`, `available_routes` (JSON), `renal_dose_adjust`, `egfr_caution_below`, `nephrotoxic`, `pregnancy_category`, `lactation_safety`, `indications` (JSON), `is_active` | — | ordering: `["generic_name"]` |
| `TreatmentExposure` | `drug_name` (snapshot), `dose`, `dose_unit`, `frequency`, `route`, `start_date`, `stop_date`, `ongoing`, `stop_reason` | `patient` → `Patient` (CASCADE); `drug` → `DrugMaster` (PROTECT); `opened_by_encounter` → `encounters.ClinicalEncounter` (SET_NULL); `closed_by_encounter` → `encounters.ClinicalEncounter` (SET_NULL) | Indexes: `[patient, ongoing]`, `[drug, ongoing]` |

### Dependencies

- `patients.Patient`
- `encounters.ClinicalEncounter`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `treatment_exposure.created`, `treatment_exposure.updated`
- **Subscribes to:** None

### API

- `TreatmentExposureViewSet` — `/api/treatment-exposures/` (CRUD)
- `DrugMasterViewSet` — `/api/drugs/` (CRUD, read-only: `is_active`)

### Admin

- `DrugMasterAdmin` — search/filter by class/renal_adjust
- `TreatmentExposureAdmin` — search/filter/date_hierarchy/readonly

---

## 6. Prescription Domain

### App: `prescriptions`

**Purpose:** Encounter-linked prescription writing with versioning, PDF generation, and Bengali language support.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `Prescription` | `version`, `status` (draft/final), `diagnosis_text`, `comorbidities`, `printed_at`, `pdf_file`, `content_hash`, `reconciled_at` | `encounter` → `ClinicalEncounter` (PROTECT); `printed_by` → `auth.User` (PROTECT, nullable) | `UniqueConstraint(["encounter", "version"], name="uniq_encounter_version")` |
| `PrescriptionItem` | `brand`, `strength`, `dose`, `dose_unit`, `route`, `frequency`, `timing`, `duration`, `instruction_bn`, `sort_order` | `prescription` → `Prescription` (CASCADE); `drug` → `DrugMaster` (PROTECT) | ordering: `["sort_order", "id"]` |
| `AdviceTemplate` | `title` (unique), `body`, `is_active`, `sort_order` | — | ordering: `["sort_order", "title"]` |

### Dependencies

- `treatments.DrugMaster`
- `encounters.ClinicalEncounter`

### Services

- No dedicated `services.py` (PDF generation in views / utils)

### Events

- **Emits:** `prescription.created` (on Prescription create); `prescription.finalized`, `medication.started` (defined, not emitted)
- **Subscribes to:** None

### API

- `PrescriptionViewSet` — `/api/prescriptions/` **(read-only)**, selective fields only

### Management Commands

| Command | Purpose |
|---------|---------|
| `seed_drugs` | Idempotently populate DrugMaster with ~60 nephrology drugs (Bangladeshi brands) |

### Admin

- `PrescriptionAdmin` — with `PrescriptionItemInline`, dynamic readonly on finalization, link preview
- `AdviceTemplateAdmin` — inline editing

---

## 7. Knowledge Platform

### App: `knowledge`

**Purpose:** Clinical knowledge base — guideline-sourced rule storage, versioning, lifecycle management (7 states: draft→under_review→active→retired), rule evaluation engine, evidence linking.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `GuidelineSource` | `title`, `abbreviation`, `version_year`, `url` | — |
| `KnowledgeBaseEntry` | `entry_id` (unique), `disease_id`, `rule_data` (JSON), `evidence_grade`, `rule_type`, `status` (7-state lifecycle), `effective_date`, `retired_date`, `tags`, `guideline_chapter`, `guideline_quote` | `source` → `GuidelineSource` (PROTECT) |
| `KnowledgeBaseVersion` | `version_number`, `rule_data`, `rule_data_diff`, `evidence_grade`, `change_summary` | `entry` → `KnowledgeBaseEntry` (CASCADE); `changed_by` → `auth.User` (SET_NULL) |
| `RuleTemplate` | `template_id` (unique), `name`, `condition_schema` (JSON) | — |
| `RuleReview` | `status` (pending/approved/changes_requested/rejected), `review_notes` | `entry` → `KnowledgeBaseEntry` (CASCADE); `version` → `KnowledgeBaseVersion` (SET_NULL); `reviewer` → `auth.User` (SET_NULL) |
| `RuleTestResult` | `test_name`, `expected_score`, `actual_score`, `matched` | `entry` → `KnowledgeBaseEntry` (CASCADE); `patient` → `Patient` (SET_NULL) |
| `GuidelineDocument` | `title`, `document_type`, `content`, `import_status`, `parsed_rules` (JSON) | `source` → `GuidelineSource` (CASCADE) |
| `EvidenceEntry` | `title`, `authors`, `journal`, `year`, `doi`, `pmid`, `evidence_level` | `entry` → `KnowledgeBaseEntry` (CASCADE) |

### Dependencies

- `patients.Patient` (in services.py for feature extraction)
- `labs.LabResult` (deferred in services.py)
- `pathology.Biopsy`, `GNDiagnosis`, `IgANScore` (deferred in services.py)

### Services

- `knowledge/services.py:extract_patient_features(patient)` — extracts structured feature dict from all clinical records
- `knowledge/services.py:evaluate_entry(entry, features)` — scores a single rule against patient features
- `knowledge/services.py:evaluate_patient_rules(patient, disease_id)` — evaluates all active rules against a patient, returns sorted `DiseaseScore` list
- `knowledge/bootstrap.py:run_bootstrap_checks()` — 7 startup validation checks (status distribution, duplicate conditions, evidence coverage, retired rules, empty rules, test KB, orphan evidence)

### Events

- **Emits:** None (no signal handlers)
- **Subscribes to:** None (no event handlers)

### API

- None (no REST endpoints — knowledge is consumed internally via services or through the Decision/ClinicalReasoning apps)

### Management Commands (8 commands — most of any app)

| Command | Purpose |
|---------|---------|
| `validate_rules` | Validate KB entries for data integrity (--disease-id, --entry-id) |
| `seed_knowledge_base` | Seed 200+ rules across 17 disease profiles from KDIGO |
| `run_rule_tests` | Run tests against active rules (--disease-id, --test-cases, --entry-id) |
| `load_test_knowledge` | Load deterministic test KB for integration testing (--force) |
| `knowledge_dashboard` | Quality dashboard: health score, coverage, gaps (--json) |
| `import_guideline` | Import rules from JSON/YAML/CSV/markdown |
| `export_knowledge_base` | Export KB entries to JSON (--disease-id, --status, --pretty) |
| `activate_entries` | Promote DRAFT entries to ACTIVE (--disease_id, --all) |

### Admin

- 8 ModelAdmin classes — full lifecycle management with custom admin actions (`transition_to_under_review`, `transition_to_active`, `transition_to_retired`)

---

## 8. Decision Engine

### App: `decision`

**Purpose:** Diagnostic decision support — hard-coded disease profiles (9 GN types), scoring engine, phenotype classification, urgency triage, next-step recommendations.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `DecisionRequest` | `input_snapshot` (JSON) | `patient` → `Patient` (CASCADE); `encounter` → `ClinicalEncounter` (CASCADE) |
| `DecisionResult` | `phenotype`, `urgency_level`, `urgency_tone`, `ranked_differential` (JSON), `next_steps` (JSON), `traceability` (JSON), `explanation`, `override_reason`, `alternative_diagnosis` | `request` → `DecisionRequest` (OneToOne, CASCADE); `overridden_by` → `auth.User` (SET_NULL) |

### Dependencies (services.py)

- **No external dependencies** — pure-logic module with 9 hard-coded disease profiles:
  - IgA nephropathy, Membranous nephropathy, Minimal change disease, FSGS, Lupus nephritis, ANCA-associated GN, Anti-GBM disease, Infection-related GN, C3 glomerulopathy

### Services

- `decision/services.py:evaluate_case(patient_dict)` — runs full scoring engine, returns ranked differential + phenotype + urgency + next steps
- `decision/services.py:classify_phenotype(patient)` — nephrotic/nephritic/mixed/RPGN
- `decision/services.py:classify_urgency(patient, ranked)` — urgent/prompt_referral/structured_outpatient
- `decision/services.py:kdigo_heatmap_point(egfr, upcr)` — KDIGO risk map
- `decision/services.py:renal_dose_adjustment(drug_class, egfr)` — simplified renal dose adjustment

### Events

- **Emits:** None (no signal handlers)
- **Subscribes to:** None

### API

- None

### Admin

- `DecisionRequestAdmin`, `DecisionResultAdmin`

---

## 9. Clinical Reasoning

### App: `clinical_reasoning`

**Purpose:** Continuous patient-level clinical reasoning — aggregates all data feeds, maintains a `ClinicalProfile` (features + differential + trajectory + care pathway + risk + evidence), generates actionable `ClinicalInsight` items (diagnostic/prognostic/therapeutic/monitoring/safety/care_gap/research).

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `ClinicalProfile` | `features_snapshot`, `differential`, `disease_trajectory`, `care_pathway`, `risk_assessment`, `evidence_summary`, `reasoning_chain`, `information_gaps`, `milestones` — all JSON, `version` | `patient` → `Patient` (OneToOne, CASCADE) |
| `ClinicalInsight` | `category` (choices), `priority` (critical/high/medium/low/info), `title`, `description`, `evidence` (JSON), `guidelines` (JSON), `reasoning`, `actionable`, `dismissed`, `expires_at` | `patient` → `Patient` (CASCADE) |

### Dependencies

- `patients.Patient`
- `knowledge.KnowledgeBaseEntry` (through reasoning pipeline)
- `labs.LabResult` (through compute_patient_outcome)
- `analytics.PatientOutcome` (through compute_patient_outcome)
- `events.dispatcher` (for subscribing to events)
- `decision.services` (through evaluate_case)

### Event Handlers

| Event | Handler | Action |
|-------|---------|--------|
| `patient.registered`, `patient.updated` | `_on_patient_event` | `reason_about_patient(patient)` |
| `encounter.created`, `encounter.updated` | `_on_patient_event` | `reason_about_patient(patient)` |
| `lab_result.created`, `lab_result.updated` | `_on_lab_event` | `compute_patient_outcome(patient)` then `reason_about_patient(patient)` |
| `biopsy.created` | `_on_patient_event` | `reason_about_patient(patient)` |
| `clinical_event.created` | `_on_clinical_event` | `compute_patient_outcome(patient)` then `reason_about_patient(patient)` |
| `treatment_exposure.created`, `treatment_exposure.updated` | `_on_patient_event` | `reason_about_patient(patient)` |

### Connection Method

- `ClinicalReasoningConfig.ready()` calls `event_handlers.connect_handlers()`
- 4 event types marked async: `lab_result.created`, `lab_result.updated`, `encounter.created`, `encounter.updated`

### Celery Tasks

| Task | Retry | Calls |
|------|-------|-------|
| `async_reason_about_patient(patient_id)` | 3×60s | `reason_about_patient()` |
| `async_compute_outcome(patient_id)` | 3×60s | `compute_patient_outcome()` |
| `async_reason_and_outcome(patient_id)` | 3×60s | both above in sequence |

### API

- None (internal reasoning engine; results consumed via admin or clinic views)

### Admin

- `ClinicalProfileAdmin` — list/search/date_hierarchy
- `ClinicalInsightAdmin` — list/filter/search/date_hierarchy, custom action: `dismiss_selected`

---

## 10. Analytics Domain

### App: `analytics`

**Purpose:** Outcome computation — patient-level aggregate outcomes (eGFR slopes, proteinuria endpoints, composite kidney events, remission tracking).

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `PatientOutcome` | `index_date`, `baseline_egfr`, `baseline_creatinine`, `baseline_upcr`, `followup_days`, `latest_egfr`, `egfr_slope`, `sustained_40_decline` (+date), `sustained_50_decline` (+date), `doubling_creatinine` (+date), `eskd` (+date), `death` (+date), `composite_kidney_event` (+date + cause), `complete_remission` (+date), `partial_remission` (+date), `best_proteinuria_reduction_pct`, `remission_status` | `patient` → `Patient` (OneToOne, CASCADE) |

### Dependencies

- `patients.Patient`
- `labs.LabResult` (for eGFR/proteinuria computation)
- `encounters.ClinicalEvent` (for endpoint detection)

### Services

- No dedicated `services.py` (outcome logic in `apps.py` / management command)

### Events

- **Emits:** None (no signal handlers)
- **Subscribes to:** None (called directly via event handlers in clinical_reasoning)

### API

- `PatientOutcomeViewSet` — `/api/outcomes/` **(read-only)**

### Management Commands

| Command | Purpose |
|---------|---------|
| `compute_outcomes` | Recompute all PatientOutcome rows |

### Admin

- `PatientOutcomeAdmin` — read-only (computed), filter/search

---

## 11. Monitoring & Outcomes

### App: `biomarkers`

**Purpose:** Biomarker kinetics — anti-PLA2R, complement (C3/C4), anti-dsDNA trajectory tracking.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `BiomarkerKinetics` | `pla2r_baseline`, `pla2r_latest`, `pla2r_nadir`, `pla2r_pct_decline`, `pla2r_50pct_decline` (+date +days), `pla2r_immunological_remission` (+date), `c3_recovered` (+date), `c4_recovered` (+date), `dsdna_baseline`, `dsdna_latest`, `dsdna_normalized` (+date) | `patient` → `Patient` (OneToOne, CASCADE) |

### Dependencies

- `patients.Patient`
- `labs.LabResult`

### Management Commands

| Command | Purpose |
|---------|---------|
| `compute_biomarkers` | Recompute all BiomarkerKinetics rows from lab series |

### Admin

- `BiomarkerKineticsAdmin` — read-only (computed), filter/search

### API

- `BiomarkerKineticsViewSet` — `/api/biomarkers/` **(read-only)**

---

## 12. Safety Domain

### App: `safety`

**Purpose:** Adverse event monitoring — drug safety surveillance with severity/relatedness grading.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `AdverseEvent` | `onset_date`, `category`, `infection_type`, `description`, `severity` (mild–fatal), `serious`, `hospitalization`, `outcome`, `relatedness` | `patient` → `Patient` (CASCADE); `suspected_drug` → `DrugMaster` (SET_NULL); `encounter` → `ClinicalEncounter` (SET_NULL) |

### Dependencies

- `patients.Patient`
- `treatments.DrugMaster`
- `encounters.ClinicalEncounter`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `safety_alert.raised` (defined, not emitted)
- **Subscribes to:** None

### API

- `AdverseEventViewSet` — `/api/adverse-events/` (CRUD)

### Admin

- `AdverseEventAdmin` — search/filter/date_hierarchy/autocomplete

---

## 13. Scheduling Domain

### App: `scheduling`

**Purpose:** Visit scheduling — automated follow-up scheduling with clinic session management.

### Models

| Model | Key Fields | FKs | Constraints |
|-------|-----------|-----|-------------|
| `ScheduledVisit` | `kind` (routine/early_safety), `label`, `target_date`, `window_start`, `window_end`, `clinic_date`, `status` | `patient` → `Patient` (CASCADE); `encounter` → `ClinicalEncounter` (SET_NULL) | `UniqueConstraint(["patient", "label"], name="uniq_patient_visit_label")`; Indexes: `[status, window_end]`, `[clinic_date]` |

### Dependencies

- `patients.Patient`
- `encounters.ClinicalEncounter`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `follow_up.scheduled`, `visit.overdue` (defined, not emitted)
- **Subscribes to:** None

### API

- `ScheduledVisitViewSet` — `/api/scheduled-visits/` (CRUD)

### Admin

- `ScheduledVisitAdmin` — search/filter/date_hierarchy/autocomplete

---

## 14. Reminders Domain

### App: `reminders`

**Purpose:** Patient communication — appointment reminders, lab test reminders, medication reminders, with multi-channel support (SMS/WhatsApp/Email/App).

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `ReminderSchedule` | `reminder_type`, `channel`, `title`, `message`, `scheduled_at`, `sent_at`, `status`, `retry_count` | `patient` → `Patient` (CASCADE); `scheduled_visit` → `ScheduledVisit` (SET_NULL) |
| `ReminderTemplate` | `reminder_type`, `channel`, `name`, `subject`, `template_body`, `is_active` | — |
| `PatientCommunicationPreference` | `preferred_channel`, `phone`, `email`, opt-in booleans, `quiet_hours_start/end` | `patient` → `Patient` (OneToOne, CASCADE) |

### Dependencies

- `patients.Patient`
- `scheduling.ScheduledVisit`

### Services

- No dedicated `services.py`

### Events

- **Emits:** `reminder.sent` (defined, not emitted)
- **Subscribes to:** None

### Admin

- `ReminderScheduleAdmin`, `ReminderTemplateAdmin`, `PatientCommunicationPreferenceAdmin` — full CRUD

---

## 15. Study Domain

### App: `studies`

**Purpose:** Research study management — study definitions, randomization arms, enrollment tracking for the BGDDR research portfolio.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `Study` | `code` (unique), `title`, `study_type`, `status`, `target_enrollment`, `primary_endpoint`, `randomization_scheme`, `block_multipliers` (JSON), `stratify_by` (JSON) | — |
| `StudyArm` | `code`, `name`, `ratio`, `is_control` | `study` → `Study` (CASCADE) |
| `StudyEnrollment` | `status`, `screened_date`, `eligible`, `enrolled_date`, `stratum`, `sequence_position`, `withdrawn_date` | `study` → `Study` (CASCADE); `patient` → `Patient` (CASCADE); `arm` → `StudyArm` (PROTECT) |

### Dependencies

- `patients.Patient`

### Services

- No dedicated `services.py`

### Events

- None

### Management Commands

| Command | Purpose |
|---------|---------|
| `seed_studies` | Idempotently seed 13 study records + arms |

### Admin

- `StudyAdmin` (with `StudyArmInline`), `StudyEnrollmentAdmin` — full CRUD with readonly fields for randomized data

---

## 16. Audit Domain

### App: `audit`

**Purpose:** Append-only audit trail — per-field change tracking for all models via Django signals, plus patient consent management.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `AuditLog` | `model_label`, `object_pk`, `object_repr`, `action` (create/update/delete), `field_name`, `old_value`, `new_value`, `change_reason` | `changed_by` → `auth.User` (SET_NULL, nullable) |
| `Consent` | `consent_type`, `form_version`, `status`, `consent_date`, `withdrawn_date`, `scope`, `document`, `is_current` | `patient` → `Patient` (CASCADE); `obtained_by` → `auth.User` (SET_NULL); `supersedes` → `self` (SET_NULL) |

### Dependencies

- `patients.Patient`

### Services

- `audit/recording.py` — Django signal-based audit recording (separate from event bus)

### Events

- None (uses Django signals directly, not the domain event bus)

### API

- None

### Admin

- `AuditLogAdmin` — **append-only** (add/change/delete all return False), search/filter
- `ConsentAdmin` — search/filter, readonly for supersedes

---

## 17. Users & Auth

### App: `users`

**Purpose:** User management — extended user profiles with clinical roles, invitation system for controlled registration.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `UserProfile` | `role`, `department`, `phone`, `is_clinician` | `user` → `auth.User` (OneToOne, CASCADE) |
| `Invitation` | `email`, `role`, `token` (unique), `used_by` | `created_by` → `auth.User` (SET_NULL); `used_by` → `auth.User` (SET_NULL) |

### Dependencies

- `django.contrib.auth`

### Services

- No dedicated `services.py`

### Events

- None

### API

- `/api/auth/token/` — token-based login (DRF `obtain_auth_token`)

### Management Commands

| Command | Purpose |
|---------|---------|
| `invite_user` | Create invitation for email + role |

### Admin

- `CustomUserAdmin` (replaces default UserAdmin with `UserProfileInline`) — adds role display, profile editing
- `InvitationAdmin`

---

## 18. Timeline Domain

### App: `timeline`

**Purpose:** Patient timeline — chronological event stream across all domains (encounters, labs, biopsies, decisions).

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `TimelineEvent` | `domain` (patient/encounter/clinical/lab/biopsy/decision), `event_type`, `event_date`, `summary`, `details` (JSON), `source_id`, `source_url` | `patient` → `Patient` (CASCADE) |

### Dependencies

- `patients.Patient`
- `encounters.ClinicalEncounter` (deferred in services.py)
- `clinical.ClinicalAssessment` (deferred in services.py)
- `pathology.Biopsy` (deferred in services.py)

### Services

- `timeline/services.py:record_event(patient, domain, event_type, ...)` — creates TimelineEvent
- `timeline/services.py:get_patient_timeline(patient, domain, limit)` — filtered query
- `timeline/services.py:rebuild_patient_timeline(patient)` — bulk rebuild from all source records

### Events

- None (consumes from other apps' data, does not emit)

### API

- None

### Admin

- `TimelineEventAdmin` — search/filter

---

## 19. Events Bus

### App: `events`

**Purpose:** In-process domain event bus with optional Celery async dispatch — the nervous system connecting all domains.

### Models

| Model | Key Fields | FKs |
|-------|-----------|-----|
| `Event` | `event_type` (31 types defined), `source_model`, `source_pk`, `payload` (JSON), `occurred_at`, `processed` | — |
| `EventSubscription` | `event_type`, `handler_path` (dotted path), `active` | — |

### Core Components

| Component | Purpose |
|-----------|---------|
| `event_types.py` | 31 event type string constants (see [Events Reference](#event-reference)) |
| `dispatcher.py` | In-process `dispatch()`, `subscribe()`, `unsubscribe()`, `mark_async()` — purely in-memory handler registry |
| `signal_handlers.py` | Bridges Django `post_save` from 7 model classes → `dispatch()` |
| `celery_tasks.py` | `dispatch_event_task` — Celery task, 3 retries × 60s, `acks_late=True` |
| `apps.py` | `EventsConfig.ready()` calls `connect_all()` to wire signal bridge |

### Event Reference

| # | Event Type | Emitter Model | Handler |
|---|-----------|---------------|---------|
| 1 | `patient.registered` | `Patient` (create) | → `_on_patient_event` → `reason_about_patient()` |
| 2 | `patient.updated` | `Patient` (update) | → `_on_patient_event` → `reason_about_patient()` |
| 3 | `encounter.created` | `ClinicalEncounter` (create) | → `_on_patient_event` → `reason_about_patient()` |
| 4 | `encounter.updated` | `ClinicalEncounter` (update) | → `_on_patient_event` → `reason_about_patient()` |
| 5 | `lab_result.created` | `LabResult` (create) | → `_on_lab_event` → `compute_outcome()` + `reason_about_patient()` |
| 6 | `lab_result.updated` | `LabResult` (update) | → `_on_lab_event` → `compute_outcome()` + `reason_about_patient()` |
| 7 | `biopsy.created` | `Biopsy` (create) | → `_on_patient_event` → `reason_about_patient()` |
| 8 | `clinical_event.created` | `ClinicalEvent` (create) | → `_on_clinical_event` → `compute_outcome()` + `reason_about_patient()` |
| 9 | `treatment_exposure.created` | `TreatmentExposure` (create) | → `_on_patient_event` → `reason_about_patient()` |
| 10-31 | 22 additional types | Defined but **not yet emitted** (future: `death.recorded`, `decision.requested`, `reminder.sent`, etc.) | No handlers |

### Async Events (4 types, Celery when broker configured)

- `lab_result.created`, `lab_result.updated`, `encounter.created`, `encounter.updated`

### Configuration

- `CELERY_BROKER_URL` — empty by default → all dispatch is synchronous in-process
- `CELERY_RESULT_BACKEND` — defaults to `redis://localhost:6379/0`

### Gaps Identified

1. **`EventSubscription` model is unused** — the dispatcher uses an in-memory `_handlers` dict, not the DB table
2. **`Event.processed` field never set to True** — always defaults to False
3. **No dead-letter queue** — after 3 failed Celery retries, task is permanently lost
4. **18 of 31 event types have no emitter** — defined as future extension points
5. **No idempotency** — same event dispatched twice runs handlers twice

### Dependencies

- Celery (optional, for async dispatch)
- Redis (optional, for Celery broker/backend)

---

## 20. Export Layer

### App: `exports`

**Purpose:** Research data export — one-row-per-patient dataset with de-identification, multiple formats (CSV/XLSX/SPSS).

### Models

- None (stateless export service)

### Dependencies

- All clinical models (for building the flat dataset)

### Services

- `exports/services.py` — dataset builder, format writers, de-identification

### Events

- None

### API

- None (CLI-only)

### Management Commands

| Command | Purpose |
|---------|---------|
| `export_dataset` | Export research dataset (--format, --out, --identified, --study) |

---

## 21. API Layer

### App: `api`

**Purpose:** REST API gateway — 16 endpoints, DRF with Token + Session auth, DjangoModelPermissions, page-based pagination, site-scoped queryset filtering.

### Models

- None (serialization-only)

### Key Files

| File | Purpose |
|------|---------|
| `urls.py` | 16 route registrations (DefaultRouter: 15 ViewSets + auth token) |
| `views.py` | 15 ViewSets (12 CRUD + 3 read-only) |
| `serializers.py` | 15 ModelSerializers |
| `base.py` | `AuditedModelViewSet` base class with audit actor attribution |
| `permissions.py` | `IsSiteScoped` permission (defined, unused) + site-filtering helpers |

### Endpoint Summary

| ViewSet | Prefix | Mode | Notes |
|---------|--------|------|-------|
| `SiteViewSet` | `/api/sites/` | CRUD | search: code/name |
| `UserSiteRoleViewSet` | `/api/user-site-roles/` | CRUD | filter: user/site/role |
| `PatientViewSet` | `/api/patients/` | CRUD | search, site-filtered |
| `ClinicalEncounterViewSet` | `/api/encounters/` | CRUD | — |
| `ClinicalEventViewSet` | `/api/events/` | CRUD | — |
| `LabResultViewSet` | `/api/lab-results/` | CRUD | select_related test |
| `TreatmentExposureViewSet` | `/api/treatment-exposures/` | CRUD | — |
| `BiopsyViewSet` | `/api/biopsies/` | CRUD | read-only: review_status |
| `PathologyReviewViewSet` | `/api/pathology-reviews/` | CRUD | read-only: is_final |
| `AdverseEventViewSet` | `/api/adverse-events/` | CRUD | — |
| `ScheduledVisitViewSet` | `/api/scheduled-visits/` | CRUD | — |
| `PrescriptionViewSet` | `/api/prescriptions/` | **RO** | selective fields |
| `PatientOutcomeViewSet` | `/api/outcomes/` | **RO** | — |
| `BiomarkerKineticsViewSet` | `/api/biomarkers/` | **RO** | — |
| `DrugMasterViewSet` | `/api/drugs/` | CRUD | read-only: is_active |
| — | `/api/auth/token/` | POST | token login |

### Auth & Permissions

- Authentication: TokenAuthentication + SessionAuthentication
- Default: `[IsAuthenticated, DjangoModelPermissions]`
- Audit viewsets override with `[DjangoModelPermissions]` explicitly
- 3 read-only viewsets use global defaults (`Prescription`, `PatientOutcome`, `BiomarkerKinetics`)

### Configuration

- Pagination: PageNumberPagination, page_size=50
- No throttling configured
- No custom filter backends (relies on DRF defaults)

---

## 22. FHIR Layer

### App: `fhir`

**Purpose:** FHIR interoperability — import/export of patient data in FHIR R4 format.

### Models

- None (transform layer)

### Dependencies

- All clinical models

### Services

- FHIR conversion logic (views/urls)

### Events

- None

### API

- FHIR endpoints (from `fhir/urls.py`)

### Admin

- None

---

## 23. Clinic Dashboard

### App: `clinic`

**Purpose:** Clinic workflow UI — guided clinical dashboard with chart library. No models.

### Models

- None (presentation layer, registered for static assets + management commands)

### Dependencies

- All clinical apps (by viewing their data)

### Services

- Template views and forms

---

## 24. System Dependencies Diagram

```
                         ┌──────────────────┐
                         │   patients.Site   │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  patients.Patient │◄─────────── Foundation Entity
                         └────────┬─────────┘
                    ┌──────────────┼──────────────────────┐
                    │              │                       │
           ┌────────▼───┐  ┌──────▼──────┐  ┌────────────▼──────────┐
           │  encounters │  │  baseline   │  │       labs           │
           │  (visits)   │  │ (assessment)│  │  (tests, results)    │
           └────────┬────┘  └─────────────┘  └────────────┬─────────┘
                    │                                      │
           ┌────────▼────┐                      ┌─────────▼──────────┐
           │  pathology  │                      │   analytics        │
           │  (biopsy)   │                      │  (PatientOutcome)  │
           └────────┬────┘                      └─────────┬──────────┘
                    │                                      │
                    │              ┌───────────────────────┘
                    │              │
           ┌────────▼────┐  ┌──────▼──────────┐
           │  treatments │  │   scheduling    │
           │  (drugs,    │  │  (visit plan)   │
           │  exposures) │  └──────┬──────────┘
           └────────┬────┘         │
                    │              │
           ┌────────▼────┐  ┌──────▼──────────┐
           │prescriptions│  │   reminders     │
           │  (PDF gen)  │  │  (comms)        │
           └─────────────┘  └─────────────────┘

                    │
                    │               KNOWLEDGE PLATFORM
                    │         ┌──────────────────────────┐
                    │         │   knowledge              │
                    │         │  (KB entries, rules,     │
                    │         │   lifecycle, bootstrap)  │
                    │         └───────────┬──────────────┘
                    │                     │
                    │         ┌───────────▼──────────────┐
                    │         │   decision               │
                    │         │  (9 disease profiles,    │
                    │         │   scoring engine)        │
                    │         └───────────┬──────────────┘
                    │                     │
           ┌────────▼─────────────────────▼──────────────────┐
           │              clinical_reasoning                 │
           │  ClinicalProfile + ClinicalInsight generation   │
           │  Subscribes to events from: patient, encounter, │
           │  lab, biopsy, treatment_exposure                │
           └────────┬────────────────────────────────────────┘
                    │
           ┌────────▼────────────────────────────────────────┐
           │              timeline                           │
           │  Chronological event stream (read-only view)   │
           └─────────────────────────────────────────────────┘

                    INFRASTRUCTURE / CROSS-CUTTING
           ┌────────────────────────────────────────────────┐
           │   events (in-process event bus + Celery)       │
           │   audit (append-only change log via signals)   │
           │   api (REST gateway, 16 endpoints)             │
           │   users (profiles, invitations, auth)          │
           │   exports (research dataset builder)           │
           │   fhir (FHIR R4 interop)                       │
           │   studies (research study + enrollment mgmt)   │
           │   safety (adverse event surveillance)          │
           │   biomarkers (anti-PLA2R, complement, dsDNA)   │
           │   clinic (dashboard UI, no models)             │
           └────────────────────────────────────────────────┘
```

### Legend

- **Foundation** → `patients.Patient` (central entity, referenced by 17+ models via FK)
- **Clinical data** → `encounters`, `baseline`, `labs`, `pathology` (data producers)
- **Treatment** → `treatments` (formulary + exposure), `prescriptions` (PDF)
- **Knowledge** → `knowledge` (rules), `decision` (scoring), `clinical_reasoning` (reasoning)
- **Monitoring** → `analytics`, `biomarkers`, `safety`, `scheduling`, `reminders`
- **Infrastructure** → `events`, `audit`, `api`, `users`, `exports`, `fhir`, `studies`, `clinic`

---

## Certification Status

| Check | Status |
|-------|--------|
| All apps documented with purpose | ✓ |
| All models listed with key fields and FKs | ✓ |
| All cross-app dependencies identified | ✓ |
| Event architecture mapped (31 types, 9 active emitters) | ✓ |
| API endpoints documented (16 routes) | ✓ |
| Management commands catalogued (22 across 10 apps) | ✓ |
| Services identified and scoped | ✓ |
| Gaps documented (Event.processed, unused EventSubscription, 18 unemitted types) | ✓ |

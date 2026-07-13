# TRACK.md — Project Resume Point

> **Last Updated:** 2026-07-11 (Phase 8: Integration & Production Readiness complete)
>
> **Project:** BGDDR → GDES (Glomerular Disease Expert System)
>
> **Location:** `E:\OneDrive\Project Claude\BGDDR\bgddr`

---

## 1. Current State

| Phase | Status |
|---|---|---|
| Phase 1: Reverse Engineer | ✅ Complete |
| Phase 2: Gap Analysis | ✅ Complete |
| Phase 3.1: Quick Wins | ✅ Complete |
| Phase 3.2: Core Engines | ✅ Complete |
| Phase 3.3: Scale | ✅ Complete |
| V2 Phase 4: Knowledge Engineering Platform | ✅ Complete |
| Phase 5: Clinical Intelligence & Explainable Decision Platform | ✅ Complete |
| Phase 6: GDES Vision — CDS Plans (Management, Monitoring, Follow-up) | ✅ Complete |
| Phase 7: GDES V6 Gap Sweep — Services (Investigation, Toxicity, Failure, Validation) | ✅ Complete |
| Phase 8: Integration & Production Readiness | ✅ Complete |

**All 442 Django tests pass + 180 pytest tests pass.**
**8 deliverable documents produced.**

---

## 2. Quick Start

```bash
cd "E:\OneDrive\Project Claude\BGDDR\bgddr"
python manage.py test --verbosity=2
```

Run specific modules:
```bash
python manage.py test decision.tests --verbosity=2
python manage.py test knowledge.tests_api --verbosity=2
python manage.py test labs.test_trend_alerts --verbosity=2
python manage.py test clinical.tests --verbosity=2
```

---

## 3. What Was Built (Phase 3.1 + 3.2 — This Session)

### Clinical Calculators
- **File:** `decision/services.py` (lines 1-180)
- **Endpoint:** `POST /api/v1/decisions/calculators/`
- **Calculators:** eGFR (CKD-EPI 2021), BSA (Mosteller), UPCR↔UTP converter, proteinuria category, renal dose adjuster, KDIGO heat map

### Override Tracking
- **Model:** `DecisionResult` — added `override_reason`, `alternative_diagnosis`, `clinician_notes`, `overridden_by`, `override_at`
- **Endpoint:** `POST /api/v1/results/{id}/override/`
- **Serializer:** `OverrideDecisionSerializer` in `decision/serializers.py`

### Guideline Linkage
- **Model:** `KnowledgeBaseEntry` — added `guideline_chapter`, `guideline_paragraph`, `guideline_quote`, `evidence_url`
- **File:** `knowledge/models.py`

### Rule Versioning
- **New Model:** `KnowledgeBaseVersion` in `knowledge/models.py`
- **Endpoints:** `GET/POST /api/v1/knowledge-base/{id}/versions/`, `POST /api/v1/knowledge-base/{id}/restore_version/`
- **File:** `knowledge/views.py`

### Lab Trend Alerts
- **File:** `labs/trend_alerts.py`
- **Functions:** `detect_egfr_trends()`, `detect_creatinine_trends()`, `detect_proteinuria_trends()`, `detect_all_trends()`
- **Detects:** eGFR rapid decline, CKD stage progression, AKI (creatinine spike), nephrotic-range proteinuria, proteinuria increase

### Drug Interaction Engine (Phase 3.2)
- **File:** `treatments/interactions.py`
- **Database:** ~190 high-priority nephrology DDI pairs (immunosuppressants, antihypertensives, diuretics, anticoagulants, antimicrobials)
- **Functions:** `check_interactions()`, `get_interaction_summary()`, `normalize_drug_name()`
- **Endpoint:** `GET/POST /api/v1/drug-interactions/check/`
- **Severity:** major, moderate, minor with mechanism + management advice

### Drug-Disease Contraindication Engine (Phase 3.2)
- **File:** `treatments/contraindications.py`
- **Database:** ~90 contraindication rules (NSAIDs in GN, CNIs in TMA, cyclophosphamide in pregnancy, etc.)
- **Functions:** `check_contraindications()`, `check_all_contraindications()`, `get_contraindication_summary()`
- **Endpoint:** `GET/POST /api/v1/drug-contraindications/check/`
- **Severity:** absolute, relative, caution with alternative suggestions

### Explainability Layer (Phase 3.2)
- **File:** `decision/explainability.py`
- **Functions:** `build_explainability()`, `build_traceability_entry()`, `_confidence_interpretation()`
- **Features:** Per-disease reasoning chain, fired rules vs. missing rules, confidence %, structured differential, guideline sources
- **Integration:** Used by `DecisionViewSet.create()` and `evaluate()` to populate `DecisionResult.traceability` and `explanation`

### Background Task Infrastructure (Phase 3.2)
- **File:** `bgddr/celery.py` — Celery app with `settings.py` namespace
- **File:** `bgddr/__init__.py` — imports celery app
- **Config:** `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_BEAT_SCHEDULE` in `bgddr/settings.py`
- **Scheduled tasks:** `send_due_visit_reminders` (12h), `send_overdue_visit_reminders` (24h), `detect_lab_trends` (6h)
- **Lab tasks:** `labs/tasks.py` — `detect_lab_trends()` with automatic reminder creation

### Automated Patient Reminders (Phase 3.2)
- **New App:** `reminders/` — models, serializers, viewsets, Celery tasks, admin
- **Models:** `ReminderSchedule`, `ReminderTemplate`, `PatientCommunicationPreference`
- **Channels:** SMS, WhatsApp, Email (with stub gateways ready for Twilio)
- **Endpoints:** CRUD for reminders/templates/prefs, `POST send/`, `POST schedule/`
- **Background:** Auto-schedules visit reminders, sends due/overdue notifications via Celery

### Knowledge Base Expansion (Phase 3.2)
- **File:** `knowledge/management/commands/seed_knowledge_base.py`
- **Expansion:** From 8 diseases / 87 rules to **16 diseases / 200+ rules**
- **New diseases:** Diabetic nephropathy, hypertensive nephrosclerosis, AIN, ATN, TMA, light chain cast nephropathy, fibrillary GN, amyloidosis, DKD+superimposed GN
- **New rule features:** Temporal conditions, composite rules, expanded ANCA/anti-GBM/lupus/IgA/C3 rules

### New Files (Phase 3.3)
- `fhir/` — FHIR R4 export/import module (`export.py`, `import_fhir.py`, `views.py`, `urls.py`, `apps.py`)
- `analytics/dashboard_data.py` — Data collection for real-time dashboards
- `templates/dashboard/` — Full-page dashboard templates (enrollment, outcomes, compliance)
- `templates/dashboard/partials/` — 8 HTMX partial templates for live-refresh sections

### Migrations Created
- `reminders/migrations/0001_initial.py` — ReminderSchedule, ReminderTemplate, PatientCommunicationPreference
- `decision/migrations/0002_*.py` — override fields + index
- `knowledge/migrations/0002_*.py` — guideline linkage + KnowledgeBaseVersion model
- `patients/migrations/0005_site_patient_site_usersiterole.py` — Site + UserSiteRole models

---

## 4. Phase 3.2 — Completed (Jul 2026)

### ✅ 4.1 Drug Interaction Engine
- **File:** `treatments/interactions.py`
- **Content:** 190 nephrology DDIs (major/moderate/minor) with mechanism + management
- **Endpoint:** `GET/POST /api/v1/drug-interactions/check/`
- **Usage:** `POST {"drugs": ["tacrolimus", "fluconazole"]}` → severity-sorted interactions

### ✅ 4.2 Drug-Disease Contraindication Engine
- **File:** `treatments/contraindications.py`
- **Content:** 90 rules (absolute/relative/caution) with alternative suggestions
- **Endpoint:** `GET/POST /api/v1/drug-contraindications/check/`
- **Usage:** `POST {"drug": "cyclophosphamide", "patient_diseases": ["pregnancy"]}`

### ✅ 4.3 Automated Patient Reminders
- **App:** `reminders/` — models, serializers, viewsets, Celery tasks, admin
- **Channels:** SMS, WhatsApp, Email (Twilio-ready stubs)
- **Endpoints:** `/api/v1/reminders/`, `/api/v1/reminders/send/`, `/api/v1/reminders/schedule/`

### ✅ 4.4 Explainability Layer
- **File:** `decision/explainability.py`
- **Features:** Per-disease reasoning (fired + missing rules), confidence %, guideline sources
- **Extends:** `DecisionResult.traceability` + `explanation` fields

### ✅ 4.5 Background Task Infrastructure
- **File:** `bgddr/celery.py` + `bgddr/__init__.py`
- **Config:** Settings with beat schedule (12h reminders, 6h lab trends)
- **Install:** `pip install celery redis` (done)

### ✅ 4.6 Knowledge Base Expansion
- **File:** `knowledge/management/commands/seed_knowledge_base.py`
- **Expansion:** 16 diseases, 200+ rules (was 8/87)
- **New:** diabetic nephropathy, hypertensive nephrosclerosis, AIN, ATN, TMA, light chain cast nephropathy, fibrillary GN, amyloidosis, DKD+GN

---

## 5. Phase 3.3 — Completed (Jul 2026)

### ✅ 5.1 Multi-Center Registry
- **Models:** `Site` (code, name, address, phone, email, is_active) + `UserSiteRole` (user, site, role) in `patients/models.py`
- **Modify:** `Patient.site` nullable FK for backward compatibility
- **RBAC:** `api/permissions.py` — `site_filter_kwargs()`, `user_sites()`, `IsSiteScoped` permission
- **API:** `SiteViewSet`, `UserSiteRoleViewSet` registered at `/api/v1/sites/` and `/api/v1/user-site-roles/`
- **PatientViewSet:** Site-scoped filtering via `get_queryset()` override
- **Migration:** `patients/migrations/0005_site_patient_site_usersiterole.py`

### ✅ 5.2 Real-Time Dashboards
- **File:** `bgddr/views.py` (dashboard views + HTMX partial endpoints)
- **File:** `analytics/dashboard_data.py` (data collection functions)
- **Tech:** HTMX polling (`hx-trigger="every 30s"`) + Chart.js — no WebSockets/ASGI needed
- **Overview page** (`/`): Auto-refreshing stats grid, worklist, cohort kidney trend (Chart.js)
- **Enrollment dashboard** (`/dashboard/enrollment/`): Summary stats, cohort doughnut chart, monthly enrollment bar chart (Chart.js), demographics breakdown
- **Outcomes dashboard** (`/dashboard/outcomes/`): Complete/partial remission counts, kidney endpoints (40% decline, ESKD, death), composite events, mean latest eGFR
- **Compliance dashboard** (`/dashboard/compliance/`): Visit completion rate, overdue count, missing eGFR (6mo) count, data completeness
- **HTMX partials:** 8 endpoints at `/dashboard/partials/*` that serve HTML fragments swapped in-place
- **Navigation:** Tab bar on all dashboard pages (Overview, Enrollment, Outcomes, Compliance)

### ✅ 5.3 FHIR Interoperability
- **Module:** `fhir/` — `export.py`, `import_fhir.py`, `views.py`, `urls.py`
- **Export:** `Patient`, `Condition`, `Observation` (labs), `DiagnosticReport` (biopsy), `MedicationRequest` as FHIR R4 resources
- **Import:** `Patient` and `Observation` (lab results) from FHIR R4 Bundles
- **Bulk:** `export_all_patients()` and `export_patient_bundle(patient, include_related=True)`
- **Endpoints:** `GET /fhir/metadata`, `GET /fhir/Patient/<id>`, `GET /fhir/Patient/`, `GET /fhir/export-all/`, `POST /fhir/import/`
- **App:** Registered in `INSTALLED_APPS` + `bgddr/urls.py`

### ✅ 5.4 Prescription Safety Checks Enhancement
- **Where:** `prescriptions/services/safety.py`
- **Content:** Pre-2019 safety checks (check 1–4) preserved; added check 5 (DDI via `check_interactions()`) and check 6 (contraindication via `check_contraindications()`) as structured warnings
- **Warnings:** Returned in `SafetyCheckResult.warnings` with severity, description, mechanism, management, suggested alternatives

### ✅ 5.5 Reminder Integration with Prescription Workflow
- **Where:** `prescriptions/services/finalize.py`
- **New function:** `_schedule_medication_reminders()` — creates 7-day medication adherence reminders in `ReminderSchedule` after successful prescription finalization
- **Integration:** Called at end of `finalize_prescription()`, best-effort (try/except to not block finalization)

---

## 6. V2 Phase 4 — Knowledge Engineering Platform (Completed Jul 2026)

### ✅ 4.1 Rule Validator
- **File:** `knowledge/rule_validator.py`
- **Functions:** `validate_rule_data()`, `check_duplicate_conditions()`, `validate_all_entries()`
- **Validates:** Known operators, known fields, numeric comparisons, `in` operator lists, missing explanations, zero weights, duplicate conditions
- **API:** `POST /api/v1/knowledge-base/validate/`, `POST /api/v1/knowledge-base/validate_all/`

### ✅ 4.2 Rule Tester
- **File:** `knowledge/rule_tester.py`
- **Functions:** `test_rule()`, `test_disease_suite()`, `test_all_active_rules()`
- **Features:** Test against real patients or synthetic features, expected score validation, summary statistics
- **API:** `POST /api/v1/knowledge-base/test/`, `POST /api/v1/knowledge-base/bulk_test/`, `POST /api/v1/knowledge-base/test_all/`

### ✅ 4.3 Evidence Engine (GRADE)
- **File:** `knowledge/evidence_engine.py`
- **Functions:** `grade_evidence()`, `suggest_evidence_grade()`, `generate_citation()`
- **GRADE:** Maps study design (meta→RCT→cohort→case-control→expert) to quality levels (High→Moderate→Low→Very Low)
- **API:** `GET /api/v1/knowledge-base/{id}/evidence_grade/`, `GET /api/v1/knowledge-base/{id}/suggest_grade/`

### ✅ 4.4 Guideline Parser
- **File:** `knowledge/guideline_parser.py`
- **Functions:** `parse_markdown_guideline()`, `parse_json_rules()`
- **Parsing:** Markdown headings → rule candidates, JSON arrays → structured rules, extracts strength indicators via regex, field alias mapping (egfr→latest_egfr, etc.)
- **Disease detection:** Auto-guesses disease_id from title text using 16-disease keyword map

### ✅ 4.5 Guideline Import
- **File:** `knowledge/guideline_import.py`
- **Functions:** `import_json_guideline()`, `import_csv_guideline()`, `import_yaml_guideline()`, `import_markdown_guideline()`
- **Formats:** JSON, YAML, CSV, Markdown with duplicate detection and error handling
- **API:** `POST /api/v1/knowledge-base/import_json/`
- **Command:** `python manage.py import_guideline path/to/file --format=json`

### ✅ 4.6 Enhanced Versioning
- **File:** `knowledge/knowledge_versioning.py`
- **Functions:** `compute_rule_diff()`, `create_version()`, `rollback_to()`, `version_history()`
- **Diff tracking:** Structural diff (added/removed conditions, changed weight/base_score/explanation)
- **API:** `POST /api/v1/knowledge-base/{id}/compute_diff/`, existing versions/restore endpoints enhanced

### ✅ 4.7 Rule Authoring
- **File:** `knowledge/authoring.py`
- **Functions:** `build_rule_data()`, `create_rule()`, `update_rule()`, `apply_template()`
- **Features:** Validation before creation, auto-source resolution, auto-versioning on update, template-based rule creation with condition schemas
- **API:** `POST /api/v1/knowledge-base/author_create/`

### ✅ 4.8 New Models & Migrations
- **Migration:** `knowledge/migrations/0003_evidenceentry_guidelinedocument_rulereview_and_more.py`
- **New models:** `RuleTemplate` (condition schemas), `RuleReview` (approval workflow), `RuleTestResult` (test outcomes), `GuidelineDocument` (imported documents), `EvidenceEntry` (literature references)
- **Extended:** `KnowledgeBaseEntry.rule_type` + `tags`; `KnowledgeBaseVersion.rule_data_diff`
- **Admin:** All 8 models registered in admin with list displays, filters, search

### ✅ 4.9 API Endpoints
New endpoints registered at `/api/v1/`:
- `/api/v1/rule-templates/` — CRUD + `by_category/` + `{id}/apply/`
- `/api/v1/rule-reviews/` — CRUD + `pending/` + `{id}/approve/` + `{id}/request_changes/` + `{id}/reject/`
- `/api/v1/rule-test-results/` — CRUD + `by_entry/` + `summary/`
- `/api/v1/guideline-documents/` — CRUD + `{id}/parse/` + `{id}/import_rules/`
- `/api/v1/evidence-entries/` — CRUD + `by_entry/` + `{id}/citation/`
- KnowledgeBaseEntry actions: `validate/`, `validate_all/`, `test/`, `bulk_test/`, `test_all/`, `evidence_grade/`, `suggest_grade/`, `import_json/`, `export/`, `compute_diff/`, `author_create/`

### ✅ 4.10 Management Commands
- `import_guideline` — Import from file (JSON/YAML/CSV/markdown)
- `run_rule_tests` — Test all active rules or a disease suite
- `validate_rules` — Validate all entries with filtering
- `export_knowledge_base` — Export to JSON with filters

### ✅ 4.11 Tests
- **New file:** `knowledge/tests_service_modules.py` — 106 tests covering all 7 service modules + new model integration
- **All 155 knowledge tests pass** (49 original + 106 new)

### Next Steps (post-V2)
| Item | Description |
|---|---|
| AI Assistant | ML-based differential diagnosis suggestion using the 200+ rule knowledge base |
| NLP for Pathology | Parse unstructured biopsy text reports to auto-populate structured fields |
| Mobile App | React Native companion app for patient-reported outcomes |
| Multi-Language | Bengali (Bangla) UI for patient-facing forms |
| Data Quality Engine | Automated data completeness scoring, missing-value alerts |

---

## 7. Phase 7 — GDES V6 Gap Sweep Services (Completed Jul 2026)

### ✅ 7.1 Investigation Recommendation Engine
- **File:** `clinical_reasoning/services/investigation_engine.py`
- **Features:** Differential-specific recommendations with clinical rationale, priority (urgent/high/medium/low), diagnostic value, guideline reference
- **Diseases:** IgAN, MN, MCD, FSGS, Lupus, ANCA, Anti-GBM, Infection-related, C3 glomerulopathy
- **Smart filtering:** Excludes completed investigations, deduplicates, sorts by priority

### ✅ 7.2 Drug Toxicity Detection
- **File:** `clinical_reasoning/services/drug_toxicity.py`
- **Drug classes:** CNI (Tacrolimus/CsA), IMPDH inhibitor (MMF), Alkylating agent (CYC), Anti-CD20 (RTX), Corticosteroid, RAAS inhibitor, mTOR inhibitor
- **Features:** Severity thresholds (mild/moderate/severe/critical), risk factor adjustment, clinical actions, monitoring frequency

### ✅ 7.3 Treatment Failure Detection
- **File:** `clinical_reasoning/services/treatment_failure.py`
- **Patterns:** Proteinuria non-response, eGFR decline, immunological non-response (PLA2R, anti-dsDNA), persistent hematuria
- **Relapse detection:** Proteinuria relapse from remission, eGFR relapse

### ✅ 7.4 Disease Validation Framework
- **File:** `clinical_reasoning/services/disease_validation.py`
- **Diseases validated:** IgAN, MN, Lupus Nephritis, ANCA-associated vasculitis
- **Categories:** Diagnostic, management, monitoring, follow-up, pathway
- **Output:** Compliance score (0-100%), critical/major gap identification

### ✅ 7.5 Retrospective Clinical Validation
- **File:** `clinical_reasoning/services/retrospective_validation.py`
- **Metrics:** Accuracy, sensitivity, specificity, PPV, NPV, Cohen's kappa
- **Comparison:** AI vs clinician (diagnosis, treatment, risk assessment)

### ✅ 7.6 API Endpoints
- **Endpoints added to ClinicalProfileViewSet:**
  - `POST investigation_recommendations/`
  - `POST drug_toxicity/`
  - `POST treatment_failure/`
  - `POST relapse_detection/`
  - `POST validate_disease/`
  - `GET retrospective_validation/`

### ✅ 7.7 Serializers
- **New serializers:** PatientRequestSerializer, InvestigationRecommendationRequestSerializer, DiseaseValidationRequestSerializer

### ✅ 7.8 Tests
- **New file:** `tests/test_v6_gap_services.py` — 31 tests covering all 5 new services
- **All 180 pytest tests pass** (149 existing + 31 new)

---

## 8. Architecture Notes

### URL Structure
```
/api/v1/
├── patients/          # Patient CRUD
├── encounters/        # Clinical encounters
├── baseline/          # Baseline assessments
├── labs/              # Lab orders & results
├── pathology/         # Biopsy & pathology
├── treatments/        # Treatment exposures
├── prescriptions/     # PDF prescriptions
├── biomarkers/        # PLA2R, dsDNA, etc.
├── clinical/          # VitalSign, ClinicalAssessment
├── knowledge/         # KnowledgeBaseEntry, versions, evaluate, validate, test, evidence
├── rule-templates/    # RuleTemplate CRUD + apply
├── rule-reviews/      # RuleReview CRUD + approve/reject workflow
├── rule-test-results/ # RuleTestResult CRUD + summary
├── guideline-documents/ # GuidelineDocument CRUD + parse/import
├── evidence-entries/  # EvidenceEntry CRUD + citation
├── decisions/         # DecisionRequest, results, override, calculators
├── timeline/          # TimelineEvent
├── results/           # DecisionResult (separate router)
├── drugs/             # DrugMaster
├── analytics/         # PatientOutcome, cohorts
├── studies/           # Research studies
├── safety/            # Adverse events
├── scheduling/        # Follow-up visits
└── audit/             # AuditLog
```

### RBAC Roles
| Role | Access |
|---|---|
| data_manager | ALL (CRUD everything) |
| statistician | VIEW_ALL + analytics |
| readonly | VIEW_ALL |
| coordinator | scheduling + encounters |
| investigator | studies + analytics |
| pathologist | pathology + labs |

### New V2 Phase 4 Models
- `knowledge.RuleTemplate` — reusable condition schemas for consistent rule authoring
- `knowledge.RuleReview` — approval workflow (pending → approved/changes_requested/rejected)
- `knowledge.RuleTestResult` — test outcomes (entry + features + actual_score + matched)
- `knowledge.GuidelineDocument` — imported guideline docs with parsing state machine
- `knowledge.EvidenceEntry` — linked literature references with GRADE evidence levels

### Key Models
- `patients.Patient` — BGD-NNNNN auto-ID, disease phase state machine
- `encounters.ClinicalEncounter` — longitudinal visits
- `decision.DecisionResult` — AI differential + override tracking
- `knowledge.KnowledgeBaseEntry` — rules with guideline linkage + versioning
- `labs.LabResult` — longitudinal lab values (eGFR auto-derived)
- `treatments.TreatmentExposure` — drug history
- `analytics.PatientOutcome` — computed outcomes (eGFR slope, remission, composite)

---

## 9. Files to Know

### Configuration
- `bgddr/settings.py` — INSTALLED_APPS, JAZZMIN_SETTINGS, REST_FRAMEWORK
- `bgddr/urls.py` — all URL routing
- `api/base.py` — shared `AuditedModelViewSet` (DjangoModelPermissions)
- `api/management/commands/seed_roles.py` — REGISTRY_APPS must include all 18 apps

### Core Services
- `decision/services.py` — disease profiles, evaluate_case(), calculators
- `knowledge/services.py` — rule engine, feature extraction, evaluate_patient_rules()
- `knowledge/rule_validator.py` — condition/operator validation, duplicate detection
- `knowledge/rule_tester.py` — test rules against patients/features
- `knowledge/evidence_engine.py` — GRADE-based evidence grading + citation
- `knowledge/guideline_parser.py` — markdown/JSON → rule candidates
- `knowledge/guideline_import.py` — JSON/YAML/CSV/markdown → KB entries
- `knowledge/knowledge_versioning.py` — structural diff, rollback, version history
- `knowledge/authoring.py` — rule builder with validation, template application
- `analytics/outcomes.py` — PatientOutcome engine
- `analytics/statistics.py` — KM, Cox, competing risks, mixed models
- `labs/trend_alerts.py` — lab trend detection

### Models with Custom Logic
- `patients/workflow.py` — DiseasePhase state machine
- `prescriptions/services.py` — prescription generation, reconciliation
- `treatments/services.py` — exposure tracking

### Test Files
- `decision/tests.py` — 41 tests (calculators, overrides, API)
- `knowledge/tests_api.py` — 23 tests (CRUD, versioning, evaluate)
- `knowledge/tests_service_modules.py` — 106 tests (validator, tester, evidence, parser, import, versioning, authoring, new models)
- `labs/test_trend_alerts.py` — 12 tests (trend detection)
- `clinical/tests.py` — 13 tests (vital signs, assessments)
- `analytics/tests.py` — existing outcome/stats tests

---

## 10. Gotchas

1. **`seed_roles.py` REGISTRY_APPS** must include: `patients`, `encounters`, `baseline`, `labs`, `pathology`, `treatments`, `prescriptions`, `analytics`, `audit`, `studies`, `safety`, `scheduling`, `biomarkers`, `clinical`, `knowledge`, `decision`, `timeline`

2. **URL routing:** `DecisionResultViewSet` registers at `/api/v1/results/` (not `/api/v1/decisions/results/`)

3. **LabResult fields:** Uses `result_date` and `sample_date` (both exist), `value_numeric` (DecimalField)

4. **LabTest fields:** Uses `default_unit` (not `unit`)

5. **CKD-EPI 2021:** At same creatinine, females have LOWER eGFR than males (different κ values)

6. **Permission classes:** `AuditedModelViewSet` uses `DjangoModelPermissions` — all viewsets inherit this. Override with `permission_classes = [IsAuthenticated]` for specific actions.

7. **Decision overrides** require `override_reason` min 5 characters

8. **Knowledge versions** auto-snapshot before restore

9. **Drug interaction endpoints** live at `/api/v1/` via `treatments/urls.py` — they are NOT model-backed viewsets, so they use `@api_view` decorators with `IsAuthenticated` permission

10. **Reminders app** requires Celery + Redis for background processing. The app runs without it (tasks are callable synchronously), but the beat scheduler requires a running `celery -A bgddr beat` process

11. **`seed_knowledge_base.py`** now creates rules with `conditions` format (list of dicts) instead of the old `path` format. The `knowledge/services.py` engine already uses the `conditions` format

12. **Explainability layer** runs in-memory on the `DISEASE_PROFILES` list, not the database KnowledgeBaseEntry rules. These two rule sets should be kept in sync

13. **Site scoping** in `api/permissions.py`: `site_filter_kwargs()` returns `{}` for superusers, data_managers, and users with no site assignments (backward compatible with existing single-site deployments)

14. **FHIR import** creates patients with `patient_id` from the `https://bgddr.birdem.org/patient-id` identifier system; falls back to auto-generated IDs if missing

15. **FHIR export** uses `urn:uuid:` references internally; does NOT require the `fhir.resources` library — pure dict-based serialization

16. **Prescription safety checks** are non-blocking — they return warnings in the response rather than raising exceptions, so the clinician can override

17. **V2 Phase 4 management commands**: `import_guideline`, `run_rule_tests`, `validate_rules`, `export_knowledge_base` — run with `--help` for options

18. **Rule validation** checks known operators (`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `exists`, etc.), known fields, numeric types, list types for `in` operator, and duplicate conditions

19. **Evidence grading** follows GRADE: meta-analysis/RCT → High, cohort → Moderate, case-control → Low, case series/expert → Very Low. Auto-suggest maps High→"1", Moderate→"2", Low/Very Low→"OP"

20. **Guideline import** auto-detects format from file extension (`.json`, `.yaml`, `.csv`, `.md`) in the management command; API import requires explicit format parameter

21. **Rule reviews** can auto-activate entries: approving a review on a DRAFT entry transitions it to ACTIVE

22. **`apply_template()`** requires a `values` dict — even if empty (`{}`). The template's `condition_schema.fields` with defaults provides the condition values

---

## 11. Test Counts

### Django Tests (442 total)
| Module | Tests |
|---|---|---|
| patients | 30 |
| encounters | 15 |
| baseline | 10 |
| labs | 18 |
| pathology | 12 |
| treatments | 14 |
| prescriptions | 20 |
| clinical | 13 |
| decision | 41 |
| knowledge | 155 (49 old + 106 V2 Phase 4) |
| analytics | 45 |
| safety | 8 |
| scheduling | 7 |
| biomarkers | 6 |
| audit | 5 |
| studies | 6 |
| api | 8 |
| users | 3 |
| reminders | 4 |
| **TOTAL** | **442** |

### Pytest Tests (180 total)
| File | Tests |
|---|---|---|
| tests/test_cds_plans.py | 29 |
| tests/test_clinical_acceptance.py | 12 |
| tests/test_clinical_intelligence_ws4_9.py | 30 |
| tests/test_clinical_reasoning_services.py | 14 |
| tests/test_clinical_validation.py | 20 |
| tests/test_event_orchestration.py | 14 |
| tests/test_knowledge_integration.py | 9 |
| tests/test_v6_gap_services.py | 31 |
| **TOTAL** | **180** |

---

## 12. Gap Analysis Reference

Full gap analysis: `CURRENT_VS_TARGET.md`

Key numbers:
- Clinical Registry: 85% complete
- Decision Support: 65% complete (+15% from explainability layer)
- Drug Intelligence: 80% complete (+60% from interaction + contraindication engines)
- Follow-up & Monitoring: 85% complete (+40% from reminders + Celery + Phase 6 follow-up scheduler)
- Knowledge Management: 95% complete (+20% from V2 Phase 4 platform: validator, tester, evidence, parser, import, versioning, authoring)
- Research & Analytics: 70% complete
- Multi-Center: 70% complete (+70% from Site model + RBAC + site-scoped filtering + API)
- Real-Time Dashboards: 90% complete (+90% from HTMX dashboards with auto-refresh)
- FHIR Interoperability: 85% complete (+85% from FHIR R4 export/import module)
- Event-Driven: 40% complete (+35% from Celery beat + lab trend tasks)
- AI Assistant: 0% complete
- Clinical Calculators: 40% complete
- CDS Plans (Management/Monitoring/Follow-up): 95% complete (+95% from Phase 6: management plan generator, monitoring plan generator, follow-up scheduler, CDS tab on patient hub)
- Investigation Recommendations: 90% complete (+90% from investigation engine: differential-specific recommendations with priority, rationale, guideline refs)
- Drug Toxicity Detection: 85% complete (+85% from drug toxicity engine: 10 drug classes, severity thresholds, risk factor adjustment)
- Treatment Failure Detection: 80% complete (+80% from treatment failure engine: proteinuria non-response, eGFR decline, immunological non-response, relapse detection)
- Disease Validation: 75% complete (+75% from disease validation framework: end-to-end validation for 4 diseases, compliance scoring)
- Retrospective Validation: 60% complete (+60% from AI vs clinician comparison: Cohen's kappa, accuracy, sensitivity/specificity metrics)

---

## 13. Documentation Files

All in project root:

| File | Content |
|---|---|
| `CURRENT_SYSTEM_ANALYSIS.md` | Executive summary, architecture |
| `PROJECT_INVENTORY.md` | File-level inventory |
| `APPLICATION_MAP.md` | App relationships, ASCII diagrams |
| `DOMAIN_MODEL.md` | All 40 models with fields/relationships |
| `DATABASE_SCHEMA.md` | Tables, indexes, constraints |
| `API_INVENTORY.md` | All REST endpoints |
| `URL_MAP.md` | Complete routing map |
| `SERVICE_MAP.md` | Service files, ~115 functions |
| `DEPENDENCY_GRAPH.md` | Inter-app dependency matrix |
| `WORKFLOW_DOCUMENTATION.md` | Clinical workflows |
| `PERMISSION_MATRIX.md` | 6 RBAC roles matrix |
| `DATA_FLOW.md` | Entry-to-export data flow |
| `TECHNICAL_DEBT.md` | Known issues, refactoring targets |
| `CURRENT_VS_TARGET.md` | Gap analysis (Phase 2) |
| `TRACK.md` | This file |
| `GDES_INTEGRATION_AUDIT.md` | Integration audit (Phase 8) |
| `GDES_CLINICAL_WORKFLOW_VALIDATION.md` | Clinical workflow validation (Phase 8) |
| `GDES_KNOWLEDGE_VALIDATION.md` | Medical knowledge validation (Phase 8) |
| `GDES_PATIENT_MANAGEMENT_VALIDATION.md` | Automated management validation (Phase 8) |
| `GDES_FOLLOWUP_VALIDATION.md` | Follow-up automation validation (Phase 8) |
| `GDES_RESEARCH_WORKFLOW_VALIDATION.md` | Research workflow validation (Phase 8) |
| `GDES_AI_VALIDATION.md` | AI clinical assistant validation (Phase 8) |
| `GDES_PRODUCTION_READINESS_REPORT.md` | Production readiness assessment (Phase 8) |

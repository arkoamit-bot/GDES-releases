# GDES Repository Inventory Report

**Project:** GDES — Glomerular Disease Expert System
**Framework:** Django 5.0+ / Django REST Framework 3.15+
**Settings Module:** `bgddr.settings`
**Inventory Date:** 2026-07-21

## Summary Statistics

| Metric | Count |
|--------|-------|
| Django Apps | 30 |
| Django Models | 86 |
| Function-Based Views | 129 |
| Class-Based Views | 1 |
| ViewSets (DRF) | 58 |
| Serializers (DRF) | 86 |
| Forms | 22 |
| Admin Classes | 73 |
| Management Commands | 35 |
| Templates | 9 |
| Migrations | 64 |
| Test Files | 23 |
| Celery Tasks | 11 |
| Signal Receivers | 0 |
| Static Files | 1 |

## Installed Apps

- `jazzmin`
- `rest_framework`
- `patients`
- `encounters`
- `baseline`
- `labs`
- `pathology`
- `treatments`
- `prescriptions`
- `biobank`
- `analytics`
- `audit`
- `studies`
- `safety`
- `scheduling`
- `biomarkers`
- `exports`
- `api`
- `users`
- `clinic`
- `clinical`
- `knowledge`
- `timeline`
- `reminders`
- `fhir`
- `events`
- `clinical_reasoning`
- `followup`
- `feedback`

## Middleware Stack

- `django.middleware.security.SecurityMiddleware`
- `whitenoise.middleware.WhiteNoiseMiddleware`
- `django.contrib.sessions.middleware.SessionMiddleware`
- `django.middleware.common.CommonMiddleware`
- `django.middleware.csrf.CsrfViewMiddleware`
- `django.contrib.auth.middleware.AuthenticationMiddleware`
- `django.contrib.messages.middleware.MessageMiddleware`
- `django.middleware.clickjacking.XFrameOptionsMiddleware`
- `audit.middleware.AuditMiddleware`
- `feedback.middleware.FeedbackMiddleware`

---
## App-by-App Inventory

### `analytics`

**Models (1):**

- **PatientOutcome** — `patient`, `index_date`, `baseline_egfr`, `baseline_creatinine`, `baseline_upcr`, `last_contact_date`, `followup_days`, `n_egfr`, `latest_egfr`, `egfr_slope` (+30 more)

**Views (10):**

- Functions: `patient_outcome`, `_serialize_cohort`, `cohort_survival_view`, `cohort_survival_plot`, `cohort_cox_view`, `cohort_egfr_slope_view`, `cohort_cif_view`, `cohort_summary_view`, `_f`, `_ev`

**Admin (1 classes, 1 registrations):**

- Class: `PatientOutcomeAdmin`
- Registered: `PatientOutcome`

**URLs:**

- Namespace: `analytics`
- `views.patient_outcome`
- `views.cohort_survival_view`
- `views.cohort_survival_plot`
- `views.cohort_cox_view`
- `views.cohort_egfr_slope_view`
- `views.cohort_cif_view`
- `views.cohort_summary_view`

**Management Commands (1):**

- `compute_outcomes` — Recompute PatientOutcome rows (the outcome engine).

**Migrations (3):** `0001_initial.py`, `0002_patientoutcome_any_remission_date_and_more.py`, `0003_patientoutcome_igan_proteinuria_response_and_more.py`

**Tests (2 files):**

- `analytics\tests.py`
- `analytics\tests_stats.py`

**Python Files (8):** `analytics\__init__.py`, `analytics\admin.py`, `analytics\dashboard_data.py`, `analytics\models.py`, `analytics\tests.py`, `analytics\tests_stats.py`, `analytics\urls.py`, `analytics\views.py`

---

### `api`

**Views (15):**

- ViewSets: `SiteViewSet`, `UserSiteRoleViewSet`, `PatientViewSet`, `ClinicalEncounterViewSet`, `ClinicalEventViewSet`, `LabResultViewSet`, `TreatmentExposureViewSet`, `BiopsyViewSet`, `PathologyReviewViewSet`, `AdverseEventViewSet`, `ScheduledVisitViewSet`, `PrescriptionViewSet`, `PatientOutcomeViewSet`, `BiomarkerKineticsViewSet`, `DrugMasterViewSet`

**Serializers (15):**

- `SiteSerializer`
- `UserSiteRoleSerializer`
- `PatientSerializer`
- `ClinicalEncounterSerializer`
- `ClinicalEventSerializer`
- `LabResultSerializer`
- `TreatmentExposureSerializer`
- `BiopsySerializer`
- `PathologyReviewSerializer`
- `AdverseEventSerializer`
- `ScheduledVisitSerializer`
- `PrescriptionSerializer`
- `PatientOutcomeSerializer`
- `BiomarkerKineticsSerializer`
- `DrugMasterSerializer`

**URLs:**

- Namespace: `api`
- `views.SiteViewSet`
- `views.UserSiteRoleViewSet`
- `views.PatientViewSet`
- `views.ClinicalEncounterViewSet`
- `views.ClinicalEventViewSet`
- `views.LabResultViewSet`
- `views.TreatmentExposureViewSet`
- `views.BiopsyViewSet`
- `views.PathologyReviewViewSet`
- `views.AdverseEventViewSet`
- `views.ScheduledVisitViewSet`
- `views.PrescriptionViewSet`
- `views.PatientOutcomeViewSet`
- `views.BiomarkerKineticsViewSet`
- `views.DrugMasterViewSet`

**Management Commands (1):**

- `seed_roles` — Create roles (Groups) and assign per-model permissions.

**Tests (1 files):**

- `api\tests.py`

**Python Files (8):** `api\__init__.py`, `api\base.py`, `api\permissions.py`, `api\renderers.py`, `api\serializers.py`, `api\tests.py`, `api\urls.py`, `api\views.py`

---

### `audit`

**App Config:** `audit`

**Models (2):**

- **AuditLog** — `model_label`, `object_pk`, `object_repr`, `action`, `field_name`, `old_value`, `new_value`, `changed_by`, `change_reason`, `changed_at`
- **Consent** — `patient`, `consent_type`, `form_version`, `status`, `consent_date`, `withdrawn_date`, `obtained_by`, `scope`, `document`, `notes` (+4 more)

**Admin (2 classes, 2 registrations):**

- Class: `AuditLogAdmin`
- Class: `ConsentAdmin`
- Registered: `AuditLog`
- Registered: `Consent`

**Management Commands (1):**

- `restore_backup` — Restore the database from a backup ZIP (or legacy .sqlite3 snapshot).

**Middleware:** `AuditMiddleware`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `audit\tests.py`

**Python Files (8):** `audit\__init__.py`, `audit\admin.py`, `audit\apps.py`, `audit\local.py`, `audit\middleware.py`, `audit\models.py`, `audit\recording.py`, `audit\tests.py`

---

### `baseline`

**App Config:** `baseline`

**Models (1):**

- **BaselineAssessment** — `patient`, `assessment_date`, `division_residence`, `socioeconomic_status`, `monthly_income_bdt`, `education`, `occupation`, `smoking`, `alcohol_use`, `previous_kidney_disease` (+36 more)

**Admin (1 classes, 1 registrations):**

- Class: `BaselineAssessmentAdmin`
- Registered: `BaselineAssessment`

**Migrations (3):** `0001_initial.py`, `0002_alter_baselineassessment_education_and_more.py`, `0003_baselineassessment_alcohol_use_and_more.py`

**Tests (1 files):**

- `baseline\tests.py`

**Python Files (5):** `baseline\__init__.py`, `baseline\admin.py`, `baseline\apps.py`, `baseline\models.py`, `baseline\tests.py`

---

### `bgddr`

**Views (15):**

- Functions: `_enroll_date`, `dashboard`, `partial_overview_stats`, `partial_worklist`, `partial_enrollment_summary`, `partial_cohort_breakdown`, `partial_enrollment_trend`, `partial_demographics`, `partial_outcomes_summary`, `partial_compliance`, `dashboard_enrollment`, `dashboard_outcomes`, `dashboard_compliance`, `_render_partial`, `health_check`

**URLs:**

- `views.dashboard`
- `views.health_check`
- `views.partial_overview_stats`
- `views.partial_worklist`
- `views.partial_enrollment_summary`
- `views.partial_cohort_breakdown`
- `views.partial_enrollment_trend`
- `views.partial_demographics`
- `views.partial_outcomes_summary`
- `views.partial_compliance`
- `views.dashboard_enrollment`
- `views.dashboard_outcomes`
- `views.dashboard_compliance`
- `include: clinic.urls`
- `include: users.urls`
- `include: api.urls`
- `include: prescriptions.urls`
- `include: analytics.urls`
- `include: studies.urls`
- `include: safety.urls`
- `include: scheduling.urls`
- `include: reminders.urls`
- `include: pathology.urls`
- `include: biomarkers.urls`
- `include: exports.urls`

**Python Files (15):** `bgddr\__init__.py`, `bgddr\admin_backup.py`, `bgddr\backup.py`, `bgddr\celery.py`, `bgddr\context_processors.py`, `bgddr\settings.py`, `bgddr\settings_deploy.py`, `bgddr\settings_desktop.py`, `bgddr\settings_prod.py`, `bgddr\updater.py`, `bgddr\urls.py`, `bgddr\version-Dr-Wasim.py`, `bgddr\version.py`, `bgddr\views.py`, `bgddr\wsgi.py`

---

### `biobank`

**App Config:** `biobank`

**Models (1):**

- **Sample** — `patient`, `sample_type`, `collection_date`, `volume_ml`, `aliquots`, `storage_location`, `status`, `notes`, `created_at`

**Admin (1 classes, 1 registrations):**

- Class: `SampleAdmin`
- Registered: `Sample`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `biobank\tests.py`

**Python Files (5):** `biobank\__init__.py`, `biobank\admin.py`, `biobank\apps.py`, `biobank\models.py`, `biobank\tests.py`

---

### `biomarkers`

**App Config:** `biomarkers`

**Models (1):**

- **BiomarkerKinetics** — `patient`, `pla2r_baseline`, `pla2r_latest`, `pla2r_nadir`, `pla2r_baseline_date`, `pla2r_pct_decline`, `pla2r_50pct_decline`, `pla2r_50pct_date`, `pla2r_50pct_days`, `pla2r_immunological_remission` (+10 more)

**Views (3):**

- Functions: `_f`, `patient_biomarkers`, `pla2r_predictor`

**Admin (1 classes, 1 registrations):**

- Class: `BiomarkerKineticsAdmin`
- Registered: `BiomarkerKinetics`

**URLs:**

- Namespace: `biomarkers`
- `views.patient_biomarkers`
- `views.pla2r_predictor`

**Management Commands (1):**

- `compute_biomarkers` — Recompute BiomarkerKinetics rows from the lab series.

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `biomarkers\tests.py`

**Python Files (7):** `biomarkers\__init__.py`, `biomarkers\admin.py`, `biomarkers\apps.py`, `biomarkers\models.py`, `biomarkers\tests.py`, `biomarkers\urls.py`, `biomarkers\views.py`

---

### `clinic`

**Views (45):**

- Functions: `_save_labs`, `patients_list`, `quicksearch`, `patient_dupcheck`, `patient_create`, `patient_delete`, `patient_edit`, `_get_recommendation_audit_records`, `patient_detail`, `baseline_edit`, `_sync_level2_from_followup`, `followup_create`, `patient_register`, `relapse_create`, `admission_create`, `adverse_event_create`, `_sync_biopsy_to_patient`, `biopsy_create`, `study_enroll`, `consent_manage`, `treatment_add`, `prescription_create`, `outcome_recompute`, `prescriptions_list`, `quality_page` ... +20 more

**Forms (18):**

- `PatientForm`
- `BaselineForm`
- `AdverseEventForm`
- `BiopsyForm`
- `GNDiagnosisForm`
- `IgANScoreForm`
- `LupusPathologyForm`
- `FSGSPathologyForm`
- `MembranousPathologyForm`
- `StudyEnrollmentForm`
- `TreatmentExposureForm`
- `ConsentForm`
- `FollowupForm`
- `RelapseForm`
- `AdmissionForm`
- `RegisterForm`
- `LabResultsForm`
- `LabOrderForm`

**URLs:**

- Namespace: `clinic`
- `views.patients_list`
- `views.quicksearch`
- `views.patient_dupcheck`
- `views.patient_create`
- `views.patient_detail`
- `views.patient_edit`
- `views.patient_delete`
- `views.baseline_edit`
- `views.followup_create`
- `views.prescription_create`
- `views.adverse_event_create`
- `views.patient_register`
- `views.relapse_create`
- `views.admission_create`
- `views.biopsy_create`
- `views.study_enroll`
- `views.consent_manage`
- `views.treatment_add`
- `views.lab_order_create`
- `views.lab_results_entry`
- `views.outcome_recompute`
- `views.worklist_page`
- `views.quality_page`
- `views.prescriptions_list`
- `views.analytics_page`

**Template Tags:** `asset_tags`

**Static Files (1):**

- `clinic\static\clinic\chart.umd.min.js`

**Python Files (4):** `clinic\__init__.py`, `clinic\forms.py`, `clinic\urls.py`, `clinic\views.py`

---

### `clinical`

**App Config:** `clinical`

**Models (2):**

- **ClinicalAssessment** — `encounter`, `chief_complaint`, `time_course`, `features`, `syndrome_classification`, `syndrome_classified_at`, `severity_flags`, `created_at`, `updated_at`
- **VitalSign** — `encounter`, `bp_systolic`, `bp_diastolic`, `heart_rate`, `weight_kg`, `height_cm`, `recorded_at`

**Views (2):**

- ViewSets: `ClinicalAssessmentViewSet`, `VitalSignViewSet`

**Serializers (2):**

- `ClinicalAssessmentSerializer`
- `VitalSignSerializer`

**Admin (2 classes, 2 registrations):**

- Class: `ClinicalAssessmentAdmin`
- Class: `VitalSignAdmin`
- Registered: `ClinicalAssessment`
- Registered: `VitalSign`

**URLs:**

- Namespace: `clinical`
- `views.ClinicalAssessmentViewSet`
- `views.VitalSignViewSet`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `clinical\tests.py`

**Python Files (8):** `clinical\__init__.py`, `clinical\admin.py`, `clinical\apps.py`, `clinical\models.py`, `clinical\serializers.py`, `clinical\tests.py`, `clinical\urls.py`, `clinical\views.py`

---

### `clinical_reasoning`

**App Config:** `clinical_reasoning`

**Models (2):**

- **ClinicalProfile** — `patient`, `features_snapshot`, `differential`, `disease_trajectory`, `care_pathway`, `risk_assessment`, `evidence_summary`, `reasoning_chain`, `information_gaps`, `milestones` (+2 more)
- **ClinicalInsight** — `patient`, `category`, `priority`, `title`, `description`, `evidence`, `guidelines`, `reasoning`, `actionable`, `dismissed` (+2 more)

**Views (3):**

- ViewSets: `ClinicalProfileViewSet`, `ClinicalInsightViewSet`, `RecommendationAuditViewSet`

**Serializers (12):**

- `ClinicalProfileSerializer`
- `ClinicalInsightSerializer`
- `ReasoningRequestSerializer`
- `RecommendationAuditSerializer`
- `ReviewRecommendationSerializer`
- `ExplainabilityRequestSerializer`
- `ManagementPlanRequestSerializer`
- `MonitoringPlanRequestSerializer`
- `FollowUpScheduleRequestSerializer`
- `PatientRequestSerializer`
- `InvestigationRecommendationRequestSerializer`
- `DiseaseValidationRequestSerializer`

**Admin (2 classes, 2 registrations):**

- Class: `ClinicalProfileAdmin`
- Class: `ClinicalInsightAdmin`
- Registered: `ClinicalProfile`
- Registered: `ClinicalInsight`

**URLs:**

- Namespace: `clinical_reasoning`
- `views.ClinicalProfileViewSet`
- `views.ClinicalInsightViewSet`
- `views.RecommendationAuditViewSet`

**Management Commands (1):**

- `deactivate_test_rules` — Deactivate all TEST-* knowledge base rules to draft status

**Celery Tasks (3):**

- `async_reason_about_patient`
- `async_compute_outcome`
- `async_reason_and_outcome`

**Migrations (2):** `0001_initial.py`, `0002_clinicalprofile_milestones.py`

**Python Files (11):** `clinical_reasoning\__init__.py`, `clinical_reasoning\admin.py`, `clinical_reasoning\apps.py`, `clinical_reasoning\checks.py`, `clinical_reasoning\event_handlers.py`, `clinical_reasoning\json_util.py`, `clinical_reasoning\models.py`, `clinical_reasoning\serializers.py`, `clinical_reasoning\tasks.py`, `clinical_reasoning\urls.py`, `clinical_reasoning\views.py`

---

### `decision`

**App Config:** `decision`

**Models (2):**

- **DecisionRequest** — `patient`, `encounter`, `input_snapshot`, `created_at`
- **DecisionResult** — `request`, `phenotype`, `urgency_level`, `urgency_tone`, `urgency_reasons`, `ranked_differential`, `next_steps`, `traceability`, `explanation`, `created_at` (+5 more)

**Views (2):**

- ViewSets: `DecisionViewSet`, `DecisionResultViewSet`

**Serializers (9):**

- `DecisionRequestSerializer`
- `DecisionResultSerializer`
- `OverrideDecisionSerializer`
- `CalculatorRequestSerializer`
- `EGFRCalculatorSerializer`
- `BSACalculatorSerializer`
- `ProteinuriaConverterSerializer`
- `RenalDoseSerializer`
- `KDIGOHeatmapSerializer`

**Admin (2 classes, 2 registrations):**

- Class: `DecisionRequestAdmin`
- Class: `DecisionResultAdmin`
- Registered: `DecisionRequest`
- Registered: `DecisionResult`

**Migrations (2):** `0001_initial.py`, `0002_decisionresult_alternative_diagnosis_and_more.py`

**Python Files (9):** `decision\__init__.py`, `decision\admin.py`, `decision\apps.py`, `decision\explainability.py`, `decision\models.py`, `decision\serializers.py`, `decision\services.py`, `decision\urls.py`, `decision\views.py`

---

### `desktop`

**Python Files (6):** `desktop\__init__.py`, `desktop\hardening.py`, `desktop\launcher-Dr-Wasim-2.py`, `desktop\launcher-Dr-Wasim.py`, `desktop\launcher.py`, `desktop\safe_migrate.py`

---

### `encounters`

**App Config:** `encounters`

**Models (4):**

- **ClinicalEncounter** — `patient`, `encounter_date`, `encounter_type`, `seen_by`, `clinic_location`, `systolic_bp`, `diastolic_bp`, `weight_kg`, `edema_grade`, `symptoms` (+6 more)
- **Admission** — `patient`, `admit_date`, `discharge_date`, `ward`, `reason`, `biopsy`, `baseline_captured`, `discharge_advice`, `created_at`
- **RelapseEpisode** — `patient`, `encounter`, `relapse_date`, `relapse_type`, `criteria`, `action_taken`, `created_at`
- **ClinicalEvent** — `HARD_KIDNEY`, `patient`, `event_type`, `event_date`, `encounter`, `notes`, `created_at`

**Admin (2 classes, 2 registrations):**

- Class: `ClinicalEventAdmin`
- Class: `ClinicalEncounterAdmin`
- Registered: `ClinicalEvent`
- Registered: `ClinicalEncounter`

**Migrations (3):** `0001_initial.py`, `0002_clinicalevent.py`, `0003_clinicalencounter_clinician_response_and_more.py`

**Python Files (4):** `encounters\__init__.py`, `encounters\admin.py`, `encounters\apps.py`, `encounters\models.py`

---

### `events`

**App Config:** `events`

**Models (2):**

- **Event** — `event_type`, `source_model`, `source_pk`, `payload`, `occurred_at`, `processed`
- **EventSubscription** — `event_type`, `handler_path`, `active`, `created_at`

**Admin (2 classes, 2 registrations):**

- Class: `EventAdmin`
- Class: `EventSubscriptionAdmin`
- Registered: `Event`
- Registered: `EventSubscription`

**Migrations (1):** `0001_initial.py`

**Python Files (8):** `events\__init__.py`, `events\admin.py`, `events\apps.py`, `events\celery_tasks.py`, `events\dispatcher.py`, `events\event_types.py`, `events\models.py`, `events\signal_handlers.py`

---

### ⚠️ `exports` — NOT FOUND

### `feedback`

**App Config:** `feedback`

**Models (15):**

- **FeedbackConfig** — `key`, `value`
- **ErrorLog** — `SEVERITY_CHOICES`, `timestamp`, `app_version`, `knowledge_version`, `os_version`, `db_version`, `user`, `module`, `page`, `action` (+5 more)
- **CrashReport** — `timestamp`, `exception_type`, `exception_message`, `stack_trace`, `module`, `patient_id_hash`, `encounter_id_hash`, `url`, `workflow`, `memory_usage_mb` (+3 more)
- **ClinicalConflict** — `timestamp`, `patient_id_hash`, `disease`, `ai_recommendation`, `clinician_decision`, `difference`, `reason`, `ai_confidence`, `guideline_ref`, `knowledge_rule_id` (+1 more)
- **KnowledgeConflict** — `CONFLICT_TYPES`, `SEVERITY_CHOICES`, `timestamp`, `conflict_type`, `patient_id_hash`, `disease`, `description`, `rule_id_a`, `rule_id_b`, `severity` (+1 more)
- **AIFailureLog** — `FAILURE_TYPES`, `timestamp`, `failure_type`, `patient_id_hash`, `disease`, `missing_data`, `reasoning_chain`, `rules_evaluated`, `confidence`, `knowledge_version` (+2 more)
- **RuleFailureLog** — `timestamp`, `rule_id`, `disease`, `condition`, `missing_feature`, `exception_message`, `knowledge_version`, `patient_feature_summary`
- **UserFeedback** — `FEEDBACK_TYPES`, `created_at`, `user`, `feedback_type`, `title`, `description`, `screenshot`, `page_url`, `resolved`, `resolution_notes`
- **WorkflowFeedback** — `FEEDBACK_TYPES`, `created_at`, `user`, `patient`, `feedback_type`, `rating`, `ACTION_CHOICES`, `action`, `recommendation_ref`, `comments` (+1 more)
- **PerformanceLog** — `METRIC_CHOICES`, `timestamp`, `metric_name`, `duration_ms`, `value`, `module`, `page`, `url`, `user`, `metadata`
- **KnowledgeImprovementSuggestion** — `STATUS_CHOICES`, `created_at`, `rule_id`, `disease`, `override_count`, `common_override_reason`, `current_recommendation`, `suggested_change`, `supporting_evidence`, `status` (+3 more)
- **FeedbackExport** — `exported_at`, `exported_by`, `filename`, `size_bytes`, `date_from`, `date_to`, `included_sections`, `export_hash`
- **TelemetrySettings** — `SYNC_CHOICES`, `enabled`, `sync_interval`, `auto_crash_reporting`, `auto_performance_reporting`, `github_repo`, `github_token`, `last_upload`, `pending_count`
- **ErrorOccurrence** — `SEVERITY_CHOICES`, `QUEUE_STATE_CHOICES`, `fingerprint`, `exception_type`, `exception_message`, `module`, `function_name`, `line_number`, `stack_trace`, `stack_hash` (+14 more)
- **UploadBatch** — `STATE_CHOICES`, `started_at`, `finished_at`, `state`, `errors_uploaded`, `errors_failed`, `errors_skipped`, `trigger`, `log_output`

**Views (26):**

- Functions: `report_clinical_conflict`, `report_knowledge_conflict`, `log_ai_failure`, `log_rule_failure`, `generate_suggestions`, `summary_report`, `export_package`, `submit_workflow_feedback`, `feedback_dashboard`, `report_problem`, `conflict_list`, `resolve_conflict`, `workflow_feedback_page`, `improvement_suggestions`, `summary_report_view`
- ViewSets: `FeedbackViewSet`, `ErrorLogViewSet`, `CrashReportViewSet`, `ClinicalConflictViewSet`, `KnowledgeConflictViewSet`, `AIFailureLogViewSet`, `RuleFailureLogViewSet`, `UserFeedbackViewSet`, `WorkflowFeedbackViewSet`, `PerformanceLogViewSet`, `KnowledgeImprovementSuggestionViewSet`

**Serializers (10):**

- `ErrorLogSerializer`
- `CrashReportSerializer`
- `ClinicalConflictSerializer`
- `KnowledgeConflictSerializer`
- `AIFailureLogSerializer`
- `RuleFailureLogSerializer`
- `UserFeedbackSerializer`
- `WorkflowFeedbackSerializer`
- `PerformanceLogSerializer`
- `KnowledgeImprovementSuggestionSerializer`

**Admin (15 classes, 15 registrations):**

- Class: `ErrorLogAdmin`
- Class: `CrashReportAdmin`
- Class: `ClinicalConflictAdmin`
- Class: `KnowledgeConflictAdmin`
- Class: `AIFailureLogAdmin`
- Class: `RuleFailureLogAdmin`
- Class: `UserFeedbackAdmin`
- Class: `WorkflowFeedbackAdmin`
- Class: `PerformanceLogAdmin`
- Class: `KnowledgeImprovementSuggestionAdmin`
- Class: `FeedbackExportAdmin`
- Class: `FeedbackConfigAdmin`
- Class: `TelemetrySettingsAdmin`
- Class: `ErrorOccurrenceAdmin`
- Class: `UploadBatchAdmin`
- Registered: `ErrorLog`
- Registered: `CrashReport`
- Registered: `ClinicalConflict`
- Registered: `KnowledgeConflict`
- Registered: `AIFailureLog`
- Registered: `RuleFailureLog`
- Registered: `UserFeedback`
- Registered: `WorkflowFeedback`
- Registered: `PerformanceLog`
- Registered: `KnowledgeImprovementSuggestion`
- Registered: `FeedbackExport`
- Registered: `FeedbackConfig`
- Registered: `TelemetrySettings`
- Registered: `ErrorOccurrence`
- Registered: `UploadBatch`

**URLs:**

- `views.ErrorLogViewSet`
- `views.CrashReportViewSet`
- `views.ClinicalConflictViewSet`
- `views.KnowledgeConflictViewSet`
- `views.AIFailureLogViewSet`
- `views.RuleFailureLogViewSet`
- `views.UserFeedbackViewSet`
- `views.WorkflowFeedbackViewSet`
- `views.PerformanceLogViewSet`
- `views.KnowledgeImprovementSuggestionViewSet`
- `views.report_clinical_conflict`
- `views.report_knowledge_conflict`
- `views.log_ai_failure`
- `views.log_rule_failure`
- `views.generate_suggestions`
- `views.export_package`
- `views.submit_workflow_feedback`
- `views.summary_report`
- HTML URL routes: 7 patterns

**Management Commands (3):**

- `export_feedback_package` — Export a de-identified feedback package ZIP
- `import_feedback` — Import feedback packages for analysis (developer PC)
- `upload_logs` — Upload pending error reports to GitHub

**Middleware:** `FeedbackMiddleware`

**Migrations (4):** `0001_initial.py`, `0002_telemetrysettings_uploadbatch_erroroccurrence.py`, `0003_workflowfeedback_action_and_more.py`, `0004_fix_github_repo_default.py`

**Tests (1 files):**

- `feedback\tests.py`

**Python Files (11):** `feedback\__init__.py`, `feedback\admin.py`, `feedback\apps.py`, `feedback\html_urls.py`, `feedback\middleware.py`, `feedback\models.py`, `feedback\serializers.py`, `feedback\services.py`, `feedback\tests.py`, `feedback\urls.py`, `feedback\views.py`

---

### `fhir`

**App Config:** `fhir`

**Views (4):**

- Functions: `fhir_capabilities`, `fhir_export_patient`, `fhir_export_all`, `fhir_import`

**URLs:**

- Namespace: `fhir`
- `views.fhir_capabilities`
- `views.fhir_export_patient`
- `views.fhir_export_all`
- `views.fhir_import`
- `views.fhir_export_all`

**Python Files (6):** `fhir\__init__.py`, `fhir\apps.py`, `fhir\export.py`, `fhir\import_fhir.py`, `fhir\urls.py`, `fhir\views.py`

---

### `followup`

**App Config:** `followup`

**Models (1):**

- **FollowUpTask** — `patient`, `task_type`, `priority`, `reason`, `clinical_reason`, `due_date`, `overdue_date`, `status`, `assigned_to`, `completed_at` (+7 more)

**Views (3):**

- Classes: `FollowUpTaskSerializer`
- ViewSets: `FollowUpTaskViewSet`, `FollowUpPlanViewSet`

**Admin (1 classes, 1 registrations):**

- Class: `FollowUpTaskAdmin`
- Registered: `FollowUpTask`

**URLs:**

- Namespace: `followup`
- `views.FollowUpTaskViewSet`
- `views.FollowUpPlanViewSet`

**Management Commands (1):**

- `followup_engine` — Interact with the follow-up engine

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `followup\tests.py`

**Python Files (8):** `followup\__init__.py`, `followup\admin.py`, `followup\apps.py`, `followup\event_handlers.py`, `followup\models.py`, `followup\tests.py`, `followup\urls.py`, `followup\views.py`

---

### `knowledge`

**App Config:** `knowledge`

**Models (20):**

- **GuidelineSource** — `title`, `abbreviation`, `version_year`, `url`, `effective_date`, `retired_date`
- **KnowledgeBaseEntry** — `entry_id`, `disease_id`, `rule_data`, `source`, `evidence_grade`, `rule_type`, `status`, `effective_date`, `retired_date`, `tags` (+17 more)
- **KnowledgeBaseVersion** — `entry`, `version_number`, `rule_data`, `rule_data_diff`, `evidence_grade`, `guideline_chapter`, `guideline_paragraph`, `guideline_quote`, `change_summary`, `changed_by` (+1 more)
- **RuleTemplate** — `template_id`, `name`, `description`, `category`, `condition_schema`, `created_at`
- **RuleReview** — `entry`, `version`, `status`, `reviewer`, `review_notes`, `created_at`
- **RuleTestResult** — `entry`, `patient`, `test_name`, `expected_score`, `actual_score`, `matched`, `test_input`, `test_output`, `created_at`
- **GuidelineDocument** — `title`, `source`, `document_type`, `content`, `import_status`, `parsed_rules`, `import_log`, `imported_at`
- **EvidenceEntry** — `entry`, `title`, `authors`, `journal`, `year`, `doi`, `pmid`, `evidence_level`, `summary`, `url` (+1 more)
- **Disease** — `id`, `name`, `category`, `parent_disease`, `definition`, `epidemiology`, `etiology`, `pathophysiology`, `clinical_presentation`, `diagnostic_criteria` (+18 more)
- **ClinicalCase** — `case_id`, `title`, `disease`, `presentation_type`, `history`, `examination`, `lab_data`, `biopsy_data`, `diagnosis`, `expected_differential` (+14 more)
- **ClinicalPathway** — `disease`, `stage_id`, `stage_name`, `stage_order`, `description`, `required_actions`, `expected_duration_days`, `next_stages`, `criteria_to_proceed`, `warnings` (+1 more)
- **Syndrome** — `id`, `name`, `definition`, `diagnostic_criteria`, `common_causes`, `rare_causes`, `clinical_clues`, `lab_clues`, `biopsy_clues`, `recommended_investigations` (+7 more)
- **PathologyEntity** — `id`, `name`, `definition`, `histological_appearance`, `clinical_significance`, `associated_diseases`, `prognostic_value`, `treatment_implications`, `guideline_references`, `is_active` (+2 more)
- **LabEntity** — `id`, `name`, `reference_ranges`, `interpretation`, `clinical_implications`, `associated_diseases`, `false_positives`, `false_negatives`, `repeat_testing`, `monitoring_recommendations` (+3 more)
- **DrugIntelligence** — `id`, `name`, `drug_class`, `mechanism_of_action`, `indications`, `contraindications`, `renal_dosing`, `dialysis_dosing`, `transplant_considerations`, `pregnancy` (+12 more)
- **MonitoringProtocol** — `id`, `name`, `drug`, `associated_diseases`, `baseline_investigations`, `monitoring_schedule`, `safety_monitoring`, `response_assessment`, `dose_adjustment`, `treatment_discontinuation` (+4 more)
- **Complication** — `id`, `name`, `risk_factors`, `clinical_features`, `prevention`, `early_detection`, `treatment`, `monitoring`, `long_term_consequences`, `associated_diseases` (+4 more)
- **KnowledgeGraphNode** — `node_id`, `node_type`, `label`, `description`, `metadata`, `is_active`, `created_at`, `updated_at`
- **KnowledgeGraphEdge** — `source`, `target`, `edge_type`, `weight`, `metadata`, `is_active`, `created_at`
- **RecommendationAudit** — `recommendation_id`, `recommendation_type`, `patient`, `clinician`, `disease_id`, `recommendation_text`, `clinical_rationale`, `guideline`, `guideline_version`, `guideline_section` (+15 more)

**Views (19):**

- ViewSets: `GuidelineSourceViewSet`, `RuleTemplateViewSet`, `RuleReviewViewSet`, `RuleTestResultViewSet`, `GuidelineDocumentViewSet`, `EvidenceEntryViewSet`, `KnowledgeBaseEntryViewSet`, `DiseaseViewSet`, `ClinicalCaseViewSet`, `ClinicalPathwayViewSet`, `SyndromeViewSet`, `PathologyEntityViewSet`, `LabEntityViewSet`, `DrugIntelligenceViewSet`, `MonitoringProtocolViewSet`, `ComplicationViewSet`, `KnowledgeGraphNodeViewSet`, `KnowledgeGraphEdgeViewSet`, `GraphReasoningViewSet`

**Serializers (29):**

- `GuidelineSourceSerializer`
- `KnowledgeBaseEntrySerializer`
- `KnowledgeBaseVersionSerializer`
- `RuleTemplateSerializer`
- `RuleReviewSerializer`
- `RuleTestResultSerializer`
- `GuidelineDocumentSerializer`
- `EvidenceEntrySerializer`
- `RuleEvaluationRequestSerializer`
- `RuleResultSerializer`
- `ValidationRequestSerializer`
- `ValidationResultSerializer`
- `TestRuleRequestSerializer`
- `BulkTestRequestSerializer`
- `ImportGuidelineRequestSerializer`
- `RollbackRequestSerializer`
- `DiseaseSerializer`
- `ClinicalCaseSerializer`
- `ClinicalPathwaySerializer`
- `SyndromeSerializer`
- `PathologyEntitySerializer`
- `LabEntitySerializer`
- `DrugIntelligenceSerializer`
- `MonitoringProtocolSerializer`
- `ComplicationSerializer`
- `KnowledgeGraphNodeSerializer`
- `KnowledgeGraphEdgeSerializer`
- `ReasoningChainSerializer`
- `PathResultSerializer`

**Admin (20 classes, 20 registrations):**

- Class: `GuidelineSourceAdmin`
- Class: `KnowledgeBaseEntryAdmin`
- Class: `KnowledgeBaseVersionAdmin`
- Class: `RuleTemplateAdmin`
- Class: `RuleReviewAdmin`
- Class: `RuleTestResultAdmin`
- Class: `GuidelineDocumentAdmin`
- Class: `EvidenceEntryAdmin`
- Class: `DiseaseAdmin`
- Class: `ClinicalCaseAdmin`
- Class: `ClinicalPathwayAdmin`
- Class: `SyndromeAdmin`
- Class: `PathologyEntityAdmin`
- Class: `LabEntityAdmin`
- Class: `DrugIntelligenceAdmin`
- Class: `MonitoringProtocolAdmin`
- Class: `ComplicationAdmin`
- Class: `KnowledgeGraphNodeAdmin`
- Class: `KnowledgeGraphEdgeAdmin`
- Class: `RecommendationAuditAdmin`
- Registered: `GuidelineSource`
- Registered: `KnowledgeBaseEntry`
- Registered: `KnowledgeBaseVersion`
- Registered: `RuleTemplate`
- Registered: `RuleReview`
- Registered: `RuleTestResult`
- Registered: `GuidelineDocument`
- Registered: `EvidenceEntry`
- Registered: `Disease`
- Registered: `ClinicalCase`
- Registered: `ClinicalPathway`
- Registered: `Syndrome`
- Registered: `PathologyEntity`
- Registered: `LabEntity`
- Registered: `DrugIntelligence`
- Registered: `MonitoringProtocol`
- Registered: `Complication`
- Registered: `KnowledgeGraphNode`
- Registered: `KnowledgeGraphEdge`
- Registered: `RecommendationAudit`

**URLs:**

- Namespace: `knowledge`
- `views.GuidelineSourceViewSet`
- `views.KnowledgeBaseEntryViewSet`
- `views.RuleTemplateViewSet`
- `views.RuleReviewViewSet`
- `views.RuleTestResultViewSet`
- `views.GuidelineDocumentViewSet`
- `views.EvidenceEntryViewSet`
- `views.DiseaseViewSet`
- `views.ClinicalCaseViewSet`
- `views.ClinicalPathwayViewSet`
- `views.SyndromeViewSet`
- `views.PathologyEntityViewSet`
- `views.LabEntityViewSet`
- `views.DrugIntelligenceViewSet`
- `views.MonitoringProtocolViewSet`
- `views.ComplicationViewSet`
- `views.KnowledgeGraphNodeViewSet`
- `views.KnowledgeGraphEdgeViewSet`
- `views.GraphReasoningViewSet`

**Management Commands (14):**

- `activate_entries` — Activate DRAFT knowledge base entries
- `backfill_governance` — Backfill missing governance metadata on KB entries
- `export_knowledge_base` — Export knowledge base entries to a JSON file
- `import_guideline` — Import rules from a guideline file (JSON, YAML, CSV, markdown)
- `knowledge_dashboard` — Display the Knowledge Quality Dashboard
- `load_test_knowledge` — Load deterministic test knowledge base for integration testing
- `run_rule_tests` — Run tests against active knowledge base rules
- `seed_clinical_cases` — Seed V4.0 clinical case library for validation
- `seed_drug_intelligence` — Seed/refresh the DrugIntelligence knowledge base for GN drugs (idempotent).
- `seed_knowledge_base` — Seed the knowledge base with expanded disease profiles (200+ rules)
- `seed_missing_diseases` — Scaffold missing diseases + DRAFT rules (for expert authoring).
- `seed_v4_knowledge` — Seed V4.0 medical knowledge expansion: diseases, guidelines, pathways, drugs
- `validate_governance` — Validate governance metadata on ACTIVE knowledge base entries
- `validate_rules` — Validate knowledge base entries for data integrity

**Migrations (9):** `0001_initial.py`, `0002_knowledgebaseentry_evidence_url_and_more.py`, `0003_evidenceentry_guidelinedocument_rulereview_and_more.py`, `0004_alter_knowledgebaseentry_status_disease_and_more.py`, `0005_v42_reusable_knowledge_objects.py`, `0006_v42_knowledge_graph.py`, `0007_knowledgebaseentry_approved_at_and_more.py`, `0008_recommendationaudit.py`, `0009_alter_recommendationaudit_evidence_grade.py`

**Tests (3 files):**

- `knowledge\tests.py`
- `knowledge\tests_api.py`
- `knowledge\tests_service_modules.py`

**Python Files (24):** `knowledge\__init__.py`, `knowledge\admin.py`, `knowledge\apps.py`, `knowledge\authoring.py`, `knowledge\bootstrap.py`, `knowledge\evidence_engine.py`, `knowledge\graph_reasoning.py`, `knowledge\graph_service.py`, `knowledge\guideline_import.py`, `knowledge\guideline_parser.py`, `knowledge\guideline_reference.py`, `knowledge\kb_update.py`, `knowledge\kb_version.py`, `knowledge\knowledge_versioning.py`, `knowledge\models.py`, `knowledge\rule_tester.py`, `knowledge\rule_validator.py`, `knowledge\serializers.py`, `knowledge\services.py`, `knowledge\tests.py`

---

### `labs`

**App Config:** `labs`

**Models (5):**

- **LabTest** — `code`, `name`, `loinc`, `default_unit`, `value_type`, `ref_low`, `ref_high`, `is_derived`, `is_active`
- **LabPanel** — `code`, `name`, `tests`
- **LabOrder** — `encounter`, `patient`, `ordered_date`, `status`, `notes`, `created_at`
- **LabOrderItem** — `order`, `test`
- **LabResult** — `patient`, `test`, `order_item`, `value_numeric`, `value_text`, `unit`, `sample_date`, `result_date`, `flag`, `source` (+3 more)

**Admin (4 classes, 4 registrations):**

- Class: `LabTestAdmin`
- Class: `LabPanelAdmin`
- Class: `LabOrderAdmin`
- Class: `LabResultAdmin`
- Registered: `LabTest`
- Registered: `LabPanel`
- Registered: `LabOrder`
- Registered: `LabResult`

**Management Commands (1):**

- `seed_labs` — Seed lab test catalog and ordering panels.

**Celery Tasks (2):**

- `detect_lab_trends`
- `_create_trend_reminders`

**Migrations (1):** `0001_initial.py`

**Tests (2 files):**

- `labs\test_trend_alerts.py`
- `labs\tests.py`

**Python Files (8):** `labs\__init__.py`, `labs\admin.py`, `labs\apps.py`, `labs\models.py`, `labs\tasks.py`, `labs\test_trend_alerts.py`, `labs\tests.py`, `labs\trend_alerts.py`

---

### `pathology`

**App Config:** `pathology`

**Models (8):**

- **Biopsy** — `patient`, `biopsy_date`, `adequacy`, `indication`, `result_category`, `review_status`, `total_glomeruli`, `global_sclerosis_pct`, `ifta_pct`, `arteriosclerosis` (+10 more)
- **GNDiagnosis** — `biopsy`, `diagnosis`, `broad_group`, `pathogenesis_group`, `primary_secondary`, `secondary_cause`
- **IgANScore** — `biopsy`, `M`, `E`, `S`, `T`, `C`
- **LupusPathology** — `biopsy`, `isn_rps_class`, `activity_index`, `chronicity_index`
- **FSGSPathology** — `biopsy`, `primary_secondary`, `variant`
- **MembranousPathology** — `biopsy`, `pla2r_tissue`, `thsd7a_tissue`, `mn_stage`
- **BiopsyImage** — `biopsy`, `image`, `stain`, `description`, `uploaded_at`
- **PathologyReview** — `KEY_FIELDS`, `biopsy`, `role`, `reviewer`, `review_date`, `diagnosis`, `broad_group`, `mest_m`, `mest_e`, `mest_s` (+7 more)

**Views (4):**

- Functions: `_review_dict`, `biopsy_review`, `discordant`, `agreement`

**Admin (3 classes, 3 registrations):**

- Class: `PathologyReviewAdmin`
- Class: `BiopsyAdmin`
- Class: `GNDiagnosisAdmin`
- Registered: `PathologyReview`
- Registered: `Biopsy`
- Registered: `GNDiagnosis`

**URLs:**

- Namespace: `pathology`
- `views.biopsy_review`
- `views.discordant`
- `views.agreement`

**Migrations (7):** `0001_initial.py`, `0002_biopsy_review_status_pathologyreview.py`, `0003_alter_gndiagnosis_broad_group_and_more.py`, `0004_alter_pathologyreview_fsgs_variant_and_more.py`, `0005_biopsy_indication_biopsy_result_category.py`, `0006_if_pattern_choices.py`, `0007_em_findings_choices.py`

**Tests (1 files):**

- `pathology\tests.py`

**Python Files (7):** `pathology\__init__.py`, `pathology\admin.py`, `pathology\apps.py`, `pathology\models.py`, `pathology\tests.py`, `pathology\urls.py`, `pathology\views.py`

---

### `patients`

**App Config:** `patients`

**Models (3):**

- **Site** — `code`, `name`, `address`, `phone`, `email`, `config`, `is_active`, `created_at`
- **Patient** — `patient_id`, `hospital_id`, `name`, `phone`, `sex`, `dob`, `enrollment_date`, `site`, `cohort`, `diabetes_status` (+20 more)
- **UserSiteRole** — `user`, `site`, `role`, `is_primary`, `created_at`

**Admin (1 classes, 1 registrations):**

- Class: `PatientAdmin`
- Registered: `Patient`

**Management Commands (6):**

- `backup_db` — Create a timestamped backup of the database (or list existing backups).
- `check_data_integrity` — Run comprehensive data integrity checks across all clinical models.
- `delete_patient` — Delete a patient and all their clinical data.
- `reset_demo_data` — Remove demo/synthetic patient data (preview unless --yes).
- `restore_db` — Restore the database from a backup file (overwrites the current DB).
- `validate_patients` — Validate patient registry: dedupe, missing fields, coverage gaps.

**Migrations (7):** `0001_initial.py`, `0002_alter_patient_cohort_alter_patient_patient_id_and_more.py`, `0003_alter_patient_hospital_id_alter_patient_phone.py`, `0004_patient_current_phase_patient_registration_date_and_more.py`, `0005_site_patient_site_usersiterole.py`, `0006_longitudinal_level2_fields.py`, `0007_longitudinal_gn_category.py`

**Tests (1 files):**

- `patients\tests_e2e.py`

**Python Files (8):** `patients\__init__.py`, `patients\admin.py`, `patients\apps.py`, `patients\choices.py`, `patients\models.py`, `patients\services.py`, `patients\tests_e2e.py`, `patients\workflow.py`

---

### `prescriptions`

**App Config:** `prescriptions`

**Models (3):**

- **Prescription** — `encounter`, `version`, `status`, `diagnosis_text`, `comorbidities`, `investigations_advised`, `advice`, `stop_notes`, `printed_at`, `printed_by` (+5 more)
- **PrescriptionItem** — `prescription`, `drug`, `brand`, `strength`, `dose`, `dose_unit`, `route`, `frequency`, `timing`, `duration` (+2 more)
- **AdviceTemplate** — `title`, `body`, `is_active`, `sort_order`, `created_at`

**Views (6):**

- Functions: `_wants_json`, `preview`, `html_download`, `reconcile_preview`, `finalize`, `pdf`

**Admin (2 classes, 2 registrations):**

- Class: `AdviceTemplateAdmin`
- Class: `PrescriptionAdmin`
- Registered: `AdviceTemplate`
- Registered: `Prescription`

**URLs:**

- Namespace: `prescriptions`
- `views.preview`
- `views.html_download`
- `views.reconcile_preview`
- `views.finalize`
- `views.pdf`

**Management Commands (1):**

- `seed_drugs` — Seed the nephrology DrugMaster formulary (Bangladeshi brands).

**Templates (2):**

- `prescriptions\templates\prescriptions\prescription.html`
- `prescriptions\templates\prescriptions\preview_wrapper.html`

**Migrations (5):** `0001_initial.py`, `0002_prescription_advice.py`, `0003_prescriptionitem_route.py`, `0004_advicetemplate_prescription_stop_notes.py`, `0005_prescription_comorbidities.py`

**Tests (1 files):**

- `prescriptions\tests.py`

**Python Files (8):** `prescriptions\__init__.py`, `prescriptions\admin.py`, `prescriptions\apps.py`, `prescriptions\models.py`, `prescriptions\pdf.py`, `prescriptions\tests.py`, `prescriptions\urls.py`, `prescriptions\views.py`

---

### `reminders`

**App Config:** `reminders`

**Models (3):**

- **ReminderSchedule** — `patient`, `reminder_type`, `channel`, `title`, `message`, `scheduled_at`, `sent_at`, `status`, `scheduled_visit`, `error_message` (+2 more)
- **ReminderTemplate** — `reminder_type`, `channel`, `name`, `subject`, `template_body`, `is_active`, `created_at`, `updated_at`
- **PatientCommunicationPreference** — `patient`, `preferred_channel`, `phone`, `email`, `reminder_follow_up`, `reminder_lab`, `reminder_medication`, `quiet_hours_start`, `quiet_hours_end`, `created_at`

**Views (8):**

- Functions: `reminder_log`, `reminder_done`, `reminder_cancel`, `send_custom_reminder`, `schedule_reminders`
- ViewSets: `ReminderScheduleViewSet`, `ReminderTemplateViewSet`, `PatientCommunicationPreferenceViewSet`

**Serializers (5):**

- `ReminderScheduleSerializer`
- `ReminderTemplateSerializer`
- `PatientCommunicationPreferenceSerializer`
- `SendCustomReminderSerializer`
- `ScheduleVisitRemindersSerializer`

**Admin (3 classes, 3 registrations):**

- Class: `ReminderScheduleAdmin`
- Class: `ReminderTemplateAdmin`
- Class: `PatientCommunicationPreferenceAdmin`
- Registered: `ReminderSchedule`
- Registered: `ReminderTemplate`
- Registered: `PatientCommunicationPreference`

**URLs:**

- `views.ReminderScheduleViewSet`
- `views.ReminderTemplateViewSet`
- `views.PatientCommunicationPreferenceViewSet`
- `views.send_custom_reminder`
- `views.schedule_reminders`
- HTML URL routes: 3 patterns

**Celery Tasks (6):**

- `send_sms`
- `send_whatsapp`
- `send_reminder`
- `send_due_visit_reminders`
- `send_overdue_visit_reminders`
- `schedule_visit_reminders`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `reminders\tests.py`

**Python Files (10):** `reminders\__init__.py`, `reminders\admin.py`, `reminders\apps.py`, `reminders\html_urls.py`, `reminders\models.py`, `reminders\serializers.py`, `reminders\tasks.py`, `reminders\tests.py`, `reminders\urls.py`, `reminders\views.py`

---

### `safety`

**App Config:** `safety`

**Models (1):**

- **AdverseEvent** — `SERIOUS_SEVERITIES`, `patient`, `onset_date`, `category`, `infection_type`, `description`, `severity`, `serious`, `hospitalization`, `outcome` (+5 more)

**Views (3):**

- Functions: `summary`, `infection_incidence_view`, `study_safety_view`

**Admin (1 classes, 1 registrations):**

- Class: `AdverseEventAdmin`
- Registered: `AdverseEvent`

**URLs:**

- Namespace: `safety`
- `views.summary`
- `views.infection_incidence_view`
- `views.study_safety_view`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `safety\tests.py`

**Python Files (7):** `safety\__init__.py`, `safety\admin.py`, `safety\apps.py`, `safety\models.py`, `safety\tests.py`, `safety\urls.py`, `safety\views.py`

---

### `scheduling`

**App Config:** `scheduling`

**Models (1):**

- **ScheduledVisit** — `patient`, `kind`, `label`, `target_date`, `window_start`, `window_end`, `clinic_date`, `status`, `encounter`, `created_at`

**Views (6):**

- Functions: `_parse`, `_visit_dict`, `due`, `overdue`, `roster`, `monitoring`

**Admin (1 classes, 1 registrations):**

- Class: `ScheduledVisitAdmin`
- Registered: `ScheduledVisit`

**URLs:**

- Namespace: `scheduling`
- `views.due`
- `views.overdue`
- `views.roster`
- `views.monitoring`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `scheduling\tests.py`

**Python Files (7):** `scheduling\__init__.py`, `scheduling\admin.py`, `scheduling\apps.py`, `scheduling\models.py`, `scheduling\tests.py`, `scheduling\urls.py`, `scheduling\views.py`

---

### `studies`

**App Config:** `studies`

**Models (3):**

- **Study** — `code`, `title`, `study_type`, `status`, `target_enrollment`, `primary_endpoint`, `randomization_scheme`, `block_multipliers`, `stratify_by`, `random_seed` (+2 more)
- **StudyArm** — `study`, `code`, `name`, `ratio`, `order`, `is_control`
- **StudyEnrollment** — `study`, `patient`, `status`, `screened_date`, `eligible`, `ineligibility_reasons`, `enrolled_date`, `arm`, `stratum`, `sequence_position` (+4 more)

**Views (1):**

- Functions: `dashboard`

**Admin (2 classes, 2 registrations):**

- Class: `StudyAdmin`
- Class: `StudyEnrollmentAdmin`
- Registered: `Study`
- Registered: `StudyEnrollment`

**URLs:**

- Namespace: `studies`
- `views.dashboard`

**Management Commands (2):**

- `auto_screen_patients` — Run automatic study eligibility screening across all patients.
- `seed_studies` — Seed the BGDDR research portfolio as selectable studies.

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `studies\tests.py`

**Python Files (8):** `studies\__init__.py`, `studies\admin.py`, `studies\apps.py`, `studies\event_handlers.py`, `studies\models.py`, `studies\tests.py`, `studies\urls.py`, `studies\views.py`

---

### `timeline`

**App Config:** `timeline`

**Models (1):**

- **TimelineEvent** — `patient`, `domain`, `event_type`, `event_date`, `summary`, `details`, `source_id`, `source_url`, `created_at`

**Views (1):**

- ViewSets: `TimelineEventViewSet`

**Serializers (1):**

- `TimelineEventSerializer`

**Admin (1 classes, 1 registrations):**

- Class: `TimelineEventAdmin`
- Registered: `TimelineEvent`

**Migrations (1):** `0001_initial.py`

**Tests (1 files):**

- `timeline\tests.py`

**Python Files (9):** `timeline\__init__.py`, `timeline\admin.py`, `timeline\apps.py`, `timeline\models.py`, `timeline\serializers.py`, `timeline\services.py`, `timeline\tests.py`, `timeline\urls.py`, `timeline\views.py`

---

### `treatments`

**App Config:** `treatments`

**Models (2):**

- **DrugMaster** — `generic_name`, `brand_names`, `drug_class`, `available_strengths`, `default_frequency`, `default_route`, `available_routes`, `strengths_by_route`, `renal_dose_adjust`, `egfr_caution_below` (+17 more)
- **TreatmentExposure** — `patient`, `drug`, `drug_name`, `dose`, `dose_unit`, `frequency`, `route`, `start_date`, `stop_date`, `ongoing` (+4 more)

**Views (2):**

- Functions: `drug_interactions_check`, `drug_contraindications_check`

**Serializers (3):**

- `DrugInteractionCheckSerializer`
- `DrugContraindicationCheckSerializer`
- `MultiDrugContraindicationCheckSerializer`

**Admin (2 classes, 2 registrations):**

- Class: `DrugMasterAdmin`
- Class: `TreatmentExposureAdmin`
- Registered: `DrugMaster`
- Registered: `TreatmentExposure`

**URLs:**

- Namespace: `treatments`
- `views.drug_interactions_check`
- `views.drug_contraindications_check`

**Management Commands (1):**

- `seed_drug_knowledge` — Seed V4.0 drug knowledge: mechanism, side effects, monitoring, dosage

**Migrations (5):** `0001_initial.py`, `0002_drugmaster_available_routes_and_more.py`, `0003_alter_drugmaster_drug_class.py`, `0004_v35_drug_certification_fields.py`, `0005_drugmaster_common_side_effects_and_more.py`

**Python Files (9):** `treatments\__init__.py`, `treatments\admin.py`, `treatments\apps.py`, `treatments\contraindications.py`, `treatments\interactions.py`, `treatments\models.py`, `treatments\serializers.py`, `treatments\urls.py`, `treatments\views.py`

---

### `users`

**Models (2):**

- **UserProfile** — `user`, `role`, `department`, `phone`, `is_clinician`, `created_at`, `updated_at`
- **Invitation** — `email`, `role`, `token`, `created_by`, `created_at`, `used_at`, `used_by`, `EXPIRY_DAYS`

**Views (10):**

- Functions: `_is_admin`, `_ensure_profile`, `login_view`, `logout_view`, `password_reset_request`, `password_reset_confirm`, `invitation_accept`, `profile_view`, `user_list`, `invite_user`

**Forms (4):**

- `LoginForm`
- `InvitationAcceptForm`
- `ProfileForm`
- `InviteUserForm`

**Admin (1 classes, 2 registrations):**

- Class: `InvitationAdmin`
- Registered: `User` → `CustomUserAdmin`
- Registered: `Invitation`

**URLs:**

- Namespace: `users`
- `views.login_view`
- `views.logout_view`
- `views.password_reset_request`
- `views.password_reset_confirm`
- `views.invitation_accept`
- `views.profile_view`
- `views.user_list`
- `views.invite_user`

**Management Commands (1):**

- `invite_user` — Invite a user to the BGDDR registry by email.

**Templates (7):**

- `users\templates\users\invitation_accept.html`
- `users\templates\users\invite_user.html`
- `users\templates\users\login.html`
- `users\templates\users\password_reset_confirm.html`
- `users\templates\users\password_reset_request.html`
- `users\templates\users\profile.html`
- `users\templates\users\user_list.html`

**Migrations (2):** `0001_initial.py`, `0002_alter_invitation_role_alter_userprofile_role.py`

**Python Files (6):** `users\__init__.py`, `users\admin.py`, `users\forms.py`, `users\models.py`, `users\urls.py`, `users\views.py`

---

## Project-Level Files

### Python & Config Files

- `ROADMAP.md.txt`
- `Start-BGDDR.bat`
- `_tmp_ms_test.py`
- `bgddr/admin_backup.py`
- `bgddr/backup.py`
- `bgddr/context_processors.py`
- `bgddr/settings_deploy.py`
- `bgddr/settings_desktop.py`
- `bgddr/settings_prod.py`
- `bgddr/updater.py`
- `bgddr/version-Dr-Wasim.py`
- `bgddr/version.py`
- `bgddr/views.py`
- `bgddr/wsgi.py`
- `check_patient_221.py`
- `conftest.py`
- `docker-compose.yml`
- `find_dups.py`
- `inspect_db.py`
- `manage.py`
- `migrate_to_postgres.py`
- `package-lock.json`
- `package.json`
- `pytest.ini`
- `requirements.txt`
- `setup_production.ps1`
- `sources.txt`
- `start_gdes.bat`
- `tailwind.config.js`
- `tmp_audit_c3.py`

### Documentation Files

- `API_INVENTORY.md`
- `APPLICATION_MAP.md`
- `AUTOMATION_AUDIT.md`
- `BUGLOG.md`
- `CHANGELOG_2026-07-16.md`
- `CLAUDECODE_DESKTOP_DEPLOYMENT_TASKS.md`
- `CLAUDE_FINAL_INDEPENDENT_AUDIT_REQUEST.md`
- `CLINICAL_RECOMMENDATION_VALIDATION.md`
- `CLINICAL_USABILITY_REVIEW.md`
- `CODE_REVIEW.md`
- `CURRENT_SYSTEM_ANALYSIS.md`
- `CURRENT_VS_TARGET.md`
- `DATABASE_SCHEMA.md`
- `DATA_FLOW.md`
- `DATA_QUALITY_AUDIT.md`
- `DEPENDENCY_GRAPH.md`
- `DEPLOYMENT.md`
- `DEPLOYMENT_RUNBOOK.md`
- `DESKTOP_DEPLOYMENT.md`
- `DOMAIN_MODEL.md`
- `FOLLOWUP_ENGINE_ARCHITECTURE.md`
- `FOLLOWUP_PROTOCOL_LIBRARY.md`
- `FOLLOWUP_VALIDATION_REPORT.md`
- `FOLLOW_UP_VALIDATION.md`
- `GDES Version 7.2 – Final Independent Clinical & Technical Review.md`
- `GDES_AI_CLINICAL_DECISION_SUPPORT_VISION.md`
- `GDES_AI_VALIDATION.md`
- `GDES_ARCHITECTURE_STABILIZATION_AND_DOMAIN_CONSOLIDATION_V2_5.md`
- `GDES_BGDDR_UI_INTEGRATION.md`
- `GDES_CLAUDE_REVIEW_REQUEST.md`
- `GDES_CLAUDE_REVIEW_RESOLUTION_REPORT.md`
- `GDES_CLINICAL_ACCEPTANCE_REPORT.md`
- `GDES_CLINICAL_GOVERNANCE.md`
- `GDES_CLINICAL_WORKFLOW_VALIDATION.md`
- `GDES_CONTINUOUS_KNOWLEDGE_IMPROVEMENT.md`
- `GDES_DESKTOP_PACKAGE_COMPLETENESS.md`
- `GDES_FINAL_ARCHITECTURE_AUDIT.md`
- `GDES_FINAL_CLINICAL_SAFETY_AUDIT.md`
- `GDES_FINAL_CODE_QUALITY_REPORT.md`
- `GDES_FINAL_KNOWLEDGE_AUDIT.md`
- `GDES_FINAL_PILOT_READINESS_REPORT.md`
- `GDES_FINAL_RECOMMENDATIONS.md`
- `GDES_FINAL_WORKFLOW_AUDIT.md`
- `GDES_FIX_INSTRUCTIONS.md`
- `GDES_FOLLOWUP_VALIDATION.md`
- `GDES_GITHUB_ERROR_REPORTING_SYSTEM.md`
- `GDES_INTEGRATION_AUDIT.md`
- `GDES_INTEGRATION_AUDIT_MISSION.md`
- `GDES_KNOWLEDGE_GOVERNANCE.md`
- `GDES_KNOWLEDGE_VALIDATION.md`
- `GDES_PATIENT_MANAGEMENT_VALIDATION.md`
- `GDES_PILOT_DEPLOYMENT_GUIDE.md`
- `GDES_PILOT_METRICS_FRAMEWORK.md`
- `GDES_PILOT_VALIDATION_REPORT.md`
- `GDES_PRODUCTION_READINESS_REPORT.md`
- `GDES_RECOMMENDATION_TRACEABILITY.md`
- `GDES_RELEASE_CANDIDATE_REPORT.md`
- `GDES_RESEARCH_WORKFLOW_VALIDATION.md`
- `GDES_SYSTEM_CONSISTENCY_AUDIT.md`
- `GDES_USER_MANUAL_AND_PATIENT_JOURNEY.md`
- `GDES_V1_RELEASE_READINESS.md`
- `GDES_V2_NEXT_MISSION.md`
- `GDES_V2_PHASE5_NEXT_MISSION.md`
- `GDES_V3_5_RELEASE_CERTIFICATION.md`
- `GDES_V3_6_KNOWLEDGE_PLATFORM_CERTIFICATION.md`
- `GDES_V3_7_SYSTEM_CERTIFICATION.md`
- `GDES_V3_8_CLINICAL_PLATFORM_VERIFICATION.md`
- `GDES_V3_8_VERIFICATION_REPORT.md`
- `GDES_V3_PRODUCTION_RELEASE_MISSION.md`
- `GDES_V4_0_MEDICAL_KNOWLEDGE_EXPANSION.md`
- `GDES_V4_1_MEDICAL_KNOWLEDGE_ENGINEERING.md`
- `GDES_V4_2_CLINICAL_KNOWLEDGE_INTEGRATION.md`
- `GDES_V5_0_PHASE2_FOLLOWUP_AUTOMATION.md`
- `GDES_V5_0_RELEASE_BLOCKER_RESOLUTION.md`
- `GDES_V5_0_SYSTEM_INTEGRATION_AND_CLINICAL_VALIDATION.md`
- `GDES_V6_5_CLAUDE_REVIEW_PREPARATION.md`
- `GDES_V6_5_INDEPENDENT_REVIEW.md`
- `GDES_V6_DEVELOPMENT_ROADMAP.md`
- `GDES_V6_NEXT_PHASE_INTEGRATION_AND_CLINICAL_VALIDATION.md`
- `GDES_V7.2_INDEPENDENT_REVIEW.md`
- `GDES_V7_1_DESKTOP_REVIEW_AND_REBUILD.md`
- `GDES_V7_1_LONGITUDINAL_CLINICAL_MANAGEMENT_AND_PILOT_VALIDATION.md`
- `GDES_V7_3_READINESS_REPORT.md`
- `GDES_V7_CLINICAL_PILOT_PREPARATION.md`
- `GDES_V8_1_CLINICAL_LEARNING_ENGINE.md`
- `GDES_V8_AI_KNOWLEDGE_ENGINE_ROADMAP.md`
- `GDES_V8_FIELD_ERROR_REPORTING_AND_FEEDBACK_SYSTEM.md`
- `GDES_V8_GAP_ANALYSIS_AND_IMPLEMENTATION.md`
- `GDES_WORKFLOW_OPTIMIZATION_REPORT.md`
- `Longitudinal Clinical Data Model (Highest Priority).md`
- `MEDICAL_KNOWLEDGE_CERTIFICATION_REPORT.md`
- `NEXT_PHASE_MISSION.md`
- `OPENCODE_BUILD_INSTALLER.md`
- `OPENCODE_REVIEW_INSTRUCTIONS.md`
- `PATIENT_CLEANUP_REPORT.md`
- `PERMISSION_MATRIX.md`
- `PROJECT_CONSTITUTION.md`
- `PROJECT_INVENTORY.md`
- `README.md`
- `RESEARCH_PLATFORM_VALIDATION.md`
- `SERVICE_MAP.md`
- `STATUS_REPORT.md`
- `SYSTEM_CERTIFICATION_REPORT.md`
- `SYSTEM_INTEGRATION_REPORT.md`
- `TECHNICAL_DEBT.md`
- `TRACK.md`
- `URL_MAP.md`
- `USER_MANUAL.md`
- `WORKFLOW_DOCUMENTATION.md`
- `WORKFLOW_GAP_ANALYSIS.md`
- `WORKFLOW_VALIDATION_REPORT.md`

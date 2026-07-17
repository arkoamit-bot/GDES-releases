# Changelog — 2026-07-16

## V8 Field Error Reporting & Feedback System

Implemented the complete V8 feedback subsystem per `GDES_V8_FIELD_ERROR_REPORTING_AND_FEEDBACK_SYSTEM.md`.

### New app: `feedback/`

```
feedback/
├── __init__.py
├── apps.py                       # AppConfig: "Field Error Reporting & Continuous Improvement"
├── models.py                     # 11 models (see below)
├── admin.py                      # All models registered with tailored list_display/filter
├── middleware.py                 # FeedbackMiddleware: crash capture + performance monitoring
├── views.py                      # 10 ViewSets (API) + 6 HTML views
├── urls.py                       # DRF router + 8 action endpoints
├── html_urls.py                  # 7 HTML page routes (namespace: feedback:)
├── serializers.py                # 10 DRF serializers
├── services.py                   # Export, suggestion engine, summary report, PII stripping
├── tests.py                      # 20 tests (models + views)
├── management/commands/
│   ├── export_feedback_package.py  # CLI export to ZIP
│   └── import_feedback.py          # CLI import + dedup + stats
└── migrations/
    └── 0001_initial.py           # 12 tables created
templates/feedback/
├── dashboard.html                # Analytics dashboard with counts/charts
├── report_problem.html           # User feedback form (8 categories)
├── workflow_feedback.html        # Star rating form (★1-5)
├── conflict_list.html            # AI + knowledge conflict list with resolve
├── improvement_suggestions.html  # Pending suggestions with approve/reject
└── summary_report.html           # Release planning summary
```

### Models (11)

| Model | Purpose | Key fields |
|-------|---------|------------|
| `FeedbackConfig` | App configuration KV store | key, value |
| `ErrorLog` | Auto-logged software errors | severity, error_type, stack_trace, module, recovered_automatically |
| `CrashReport` | Unhandled exception capture | exception_type, stack_trace, patient_id_hash, memory_usage_mb |
| `ClinicalConflict` | AI vs clinician disagreement | disease, ai_recommendation, clinician_decision, reason, ai_confidence |
| `KnowledgeConflict` | Auto-detected knowledge inconsistencies | conflict_type (9 types), severity, rule_id_a, rule_id_b |
| `AIFailureLog` | Low-confidence / can't-determine events | failure_type, missing_data, reasoning_chain, confidence |
| `RuleFailureLog` | KB entry evaluation failures | rule_id, condition, missing_feature, exception_message |
| `UserFeedback` | Help > Report Problem submissions | feedback_type (8 types), title, description, screenshot |
| `WorkflowFeedback` | Star ratings for AI suggestions | feedback_type, rating (1-5), comments |
| `PerformanceLog` | Auto-logged timing metrics | metric_name (8 types), duration_ms, page, url |
| `KnowledgeImprovementSuggestion` | Auto-generated when 3+ overrides | rule_id, disease, override_count, common_reason, status |
| `FeedbackExport` | Export history tracking | filename, size_bytes, date_from, date_to, sections |

### Middleware: `FeedbackMiddleware`

Registered in `settings.MIDDLEWARE` after `AuditMiddleware`. On every request:
- **Crash capture**: `try/except` wraps `get_response`; on exception records `CrashReport` with stack trace, hashed patient/encounter IDs, memory, workflow, app version
- **Performance monitoring**: logs any request taking >2s as `slow_page` metric with duration, module, URL, user

### API Endpoints (under `/api/v1/feedback/`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `errors/` | Error log CRUD (admin) |
| GET/POST | `crashes/` | Crash report list (admin) |
| GET/POST | `conflicts/` | Clinical conflict CRUD (auth) |
| POST | `conflicts/{id}/resolve/` | Mark conflict resolved |
| GET/POST | `knowledge-conflicts/` | Knowledge conflict CRUD (auth) |
| GET/POST | `feedback/` | User feedback CRUD (auth) |
| GET/POST | `workflow-feedback/` | Workflow feedback CRUD (auth) |
| GET | `performance/` | Performance logs (admin) |
| GET/POST | `improvements/` | Improvement suggestions (admin) |
| POST | `report-conflict/` | Submit clinical conflict |
| POST | `submit-workflow-feedback/` | Submit star rating |
| GET | `export-package/` | Download de-identified ZIP (admin) |
| GET | `summary-report/` | Release planning report JSON (admin) |

### HTML Pages

| URL | View | Purpose |
|-----|------|---------|
| `/feedback/` | Dashboard | Aggregate stats, error/conflict/failure breakdowns, slow pages |
| `/feedback/report/` | Report Problem | Dropdown category + title + description form |
| `/feedback/conflicts/` | Conflict List | AI + knowledge conflicts table with resolve button |
| `/feedback/workflow/` | Rate Suggestions | Star rating (1-5) + comments form |
| `/feedback/improvements/` | Improvement Suggestions | List with Approve/Reject actions |
| `/feedback/summary/` | Summary Report | Release planning: bugs, disagreements, gaps, suggestions |

### Privacy

- `strip_pii()` recursively removes patient_name, MRN, phone, address, NID, DOB, email, SSN from all exported data
- Patient/encounter IDs hashed with SHA-256 (16-char truncation) in crash reports and conflict logs
- Export ZIP contains zero patient-identifiable information by design
- `model_to_safe_dict()` skips all relation/FK fields

### Export Format (`GDES_Feedback_YYYYMMDD.zip`)

```
logs/errors.json
logs/conflicts.json
logs/performance.json
logs/ai_failures.json
logs/knowledge_conflicts.json
logs/user_feedback.json
logs/rule_failures.json
logs/improvement_suggestions.json
environment.json           # app_version, kb_version, python, platform
system_information.json    # loaded Python modules
manifest.json              # version, build, guideline_version, record counts
```

### Sidebar

- New **Feedback** section (nav links): Feedback Dashboard, AI Conflicts, Improvements, Rate Suggestions
- **Report Problem** link under **System** section

### Tests

- 20 new tests (8 model tests + 12 view/API tests)
- Full suite: **270/270 passing** (was 250)
- `manage.py check` — clean

---

## KB Governance Metadata Backfill

- Created `knowledge/management/commands/backfill_governance.py` — populates `guideline_chapter`, `evidence_url`, `author`, `approved_by`, `approved_at` on all 209 active KB entries (dry-run by default, `--apply` to persist)
- Updated `seed_knowledge_base.py` to set the same fields on future seeds
- All 209 active entries now have complete governance metadata
- Updated docstring in `management_plan.py` reflecting resolved items (✓ governance populated, ✓ feedback system live, ✗ clinical validation still pending nephrologist)

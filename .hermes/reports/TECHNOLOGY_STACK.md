# BGDDR / GDES — Comprehensive Technology Stack Report

> **Generated**: 2026-07-21
> **Source**: GDES repository at `C:\Users\User\Documents\GitHub\GDES`
> **System**: Bangladesh Glomerular Disease & Diabetes Registry (BGDDR) / Glomerular Disease Expert system (GDES)

---

## 1. System Overview

BGDDR/GDES is a **clinical expert system for glomerular diseases** — a Django-based registry and clinical decision support platform designed for point-of-care data collection that doubles as a research platform. It covers the full patient lifecycle: enroll → consent → (randomize) → follow-up (prescription + labs + biopsy) → compute outcomes → analyse by cohort or trial arm.

**Core Design Principle**: The prescription *is* the follow-up visit. A single `ClinicalEncounter` per visit is the hub; finalizing a prescription simultaneously freezes an immutable medico-legal document and reconciles the medication history for research.

---

## 2. Technology Stack

### 2.1 Backend Framework

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.12 (Docker), 3.11/3.13 (local) |
| **Web Framework** | Django | ≥5.0 |
| **REST API** | Django REST Framework (DRF) | ≥3.15 |
| **WSGI Server (dev)** | Django dev server | Built-in |
| **WSGI Server (desktop)** | Waitress | ≥3.0 |
| **WSGI Server (production)** | Gunicorn | ≥22.0 |
| **Admin Theme** | django-jazzmin | ≥3.0 |

### 2.2 Database

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Default DB** | SQLite | — | Desktop/single-user; WAL mode enabled, 30s busy timeout |
| **Production DB** | PostgreSQL | 16-alpine | Docker image; psycopg3 adapter (≥3.1) |
| **ORM** | Django ORM | — | No raw SQL; database-agnostic design |
| **Auto-field** | BigAutoField | — | Default across all models |
| **Migration** | Django migrations | — | All apps have `0001_initial.py` |

### 2.3 Frontend

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **CSS Framework** | Tailwind CSS | ≥3.4.0 | Build via CLI (`tailwindcss` npm) |
| **UI Components** | Flowbite | ≥2.3.0 | Tailwind component library |
| **JS Library** | htmx.org | ≥1.9.12 | HTML-over-the-wire interactions |
| **Admin UI** | django-jazzmin | ≥3.0 | AdminLTE-based; FontAwesome icons |
| **Static Files** | WhiteNoise | ≥6.6 | Served from WSGI app |
| **Charting** | Client-side JS | — | Clinic workflow views |

### 2.4 Background Tasks & Async

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Task Queue** | Celery | ≥5.4 | Background task processing |
| **Message Broker** | Redis | ≥5.0 | Also Docker image `redis:7-alpine` |
| **Beat Scheduler** | django-celery-beat | — | DatabaseScheduler |
| **Scheduled Tasks** | Celery Beat | — | Due visit reminders (12h), overdue (24h), lab trends (6h) |

### 2.5 PDF & Document Generation

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Primary PDF** | WeasyPrint | ≥60 | Requires GTK3 + cairo/pango (native libs) |
| **Fallback PDF** | xhtml2pdf | ≥0.2.15 | Pure-Python fallback; uses reportlab |
| **Bilingual Support** | NotoSansBengali TTF | — | Bengali text in prescriptions |

### 2.6 Data Export & Analytics

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| **Excel Export** | openpyxl | ≥3.1 | Research datasets + data dictionary sheet |
| **SPSS Export** | pyreadstat | ≥1.2 | `.sav` format with variable/value labels |
| **Data Processing** | pandas | ≥2.0 | Required by pyreadstat |
| **Statistical Methods** | Pure Python | — | No external stat libraries |

### 2.7 Containerization & Deployment

| Component | Technology | Image/Version |
|-----------|-----------|---------------|
| **Container Runtime** | Docker Compose | v3.9 |
| **App Base Image** | Python | 3.12-slim-bookworm |
| **Web Server** | Nginx | 1.25-alpine |
| **Database** | PostgreSQL | 16-alpine |
| **Cache/Broker** | Redis | 7-alpine |
| **SSL Termination** | Nginx | Configurable |

### 2.8 Desktop Deployment (Windows)

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Packager** | PyInstaller | ≥6.0 (build-time; `.spec` files in `desktop/`) |
| **WSGI** | Waitress | Pure-Python; serves on 127.0.0.1:8000 |
| **Launcher** | Python script | `desktop/launcher.py`; auto-migration, hardening |
| **Installer** | PowerShell scripts | `desktop/build_exe.ps1`, `setup_production.ps1` |
| **Data Dir** | Configurable | `BGDDR_DATA_DIR` env var; local disk only for SQLite |

### 2.9 Testing

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Test Framework** | Django test runner | `python manage.py test` |
| **Test Config** | pytest.ini | `testpaths = tests feedback/tests.py` |
| **Test Count** | 56+ tests | Including validation against published datasets |
| **Validations** | Freireich 6-MP dataset | KM + log-rank verified |
| **Validation** | Textbook κ=0.40 | Cohen's kappa verified |

### 2.10 External Integrations

| Component | Technology | Notes |
|-----------|-----------|-------|
| **FHIR** | FHIR API (Phase 3.3) | `fhir` app for HL7 FHIR export/import |
| **SMS** | Twilio (planned) | Reminders; commented out in requirements |
| **Email** | Django SMTP / SendGrid | Reminder notifications |
| **Evidence Lookup** | NCBI E-utilities | PubMed; opt-in only (`GDES_AI_ONLINE_EVIDENCE=1`) |

---

## 3. Application Architecture

### 3.1 Django Settings Modules

| Module | Purpose |
|--------|---------|
| `bgddr.settings` | Base settings (SQLite, DEBUG=True) |
| `bgddr.settings_prod` | Production (PostgreSQL, DEBUG=False, security hardening) |

### 3.2 Installed Apps (27 active + 1 disabled)

#### Core Registry Apps
1. **patients** — `Patient` model (root entity); registry spine
2. **encounters** — `ClinicalEncounter`, `ClinicalEvent`, `Admission`, `RelapseEpisode`; visit hub
3. **baseline** — `BaselineAssessment` (OneToOne→Patient); enrollment snapshot
4. **labs** — `LabTest`, `LabPanel`, `LabOrder`, `LabOrderItem`, `LabResult`; longitudinal labs
5. **pathology** — `Biopsy`, `GNDiagnosis`, `IgANScore`, `LupusPathology`, `FSGSPathology`, `MembranousPathology`, `BiopsyImage`, `PathologyReview`; central review workflow
6. **treatments** — `DrugMaster`, `TreatmentExposure`; research episodes
7. **prescriptions** — `Prescription`, `PrescriptionItem`, `AdviceTemplate`; reconciliation engine

#### Analytics & Research
8. **analytics** — `PatientOutcome` (computed); survival, Cox PH, eGFR slope, competing risks, MICE imputation
9. **exports** — Research dataset (CSV/XLSX/SPSS .sav); one-row-per-patient denormalized

#### Clinical Decision Support (GDES)
10. **clinical** — `ClinicalAssessment`, `VitalSign`; structured assessment
11. **knowledge** — `GuidelineSource`, `KnowledgeBaseEntry`; rule engine
12. **decision** — `DecisionRequest`, `DecisionResult`; differential diagnosis, urgency classification
13. **timeline** — `TimelineEvent`; cross-domain event aggregation

#### Operational
14. **safety** — `AdverseEvent`; infection/SAE tracking
15. **studies** — `Study`, `StudyArm`, `StudyEnrollment`; embedded trial platform
16. **scheduling** — `ScheduledVisit`; protocol follow-up scheduling
17. **biomarkers** — `BiomarkerKinetics` (computed); PLA2R, complement, anti-dsDNA

#### Compliance & Access
18. **audit** — `AuditLog`, `Consent`; per-field change history, versioned consent
19. **users** — `UserProfile`, `Invitation`; role-based access control

#### Infrastructure
20. **api** — DRF ViewSets; REST API at `/api/v1/`
21. **clinic** — Workflow UI (no models); patient hub, worklist, charts
22. **reminders** — Celery tasks for visit/lab reminders
23. **fhir** — HL7 FHIR integration
24. **events** — Event dispatcher, signal handlers
25. **clinical_reasoning** — Clinical intelligence platform
26. **followup** — Follow-up engine with protocol library
27. **feedback** — Field error reporting & continuous improvement

#### Disabled
28. ~~**biobank**~~ — Disabled in protocol v2; code retained for future amendment

### 3.3 Model Count

| Category | Count |
|----------|-------|
| **Total Django models** | 42 tables across 21+ apps |
| **Active DB tables** | 42 (including Django auth/session) |
| **Service functions** | ~102 public functions across 39 service files |
| **Dataclasses** | 10+ for structured return types |

---

## 4. Architecture Patterns

### 4.1 Dependency Graph (DAG — No Circular Dependencies)

```
patients (ROOT)
  ├── encounters
  │     ├── labs
  │     │     └── analytics
  │     ├── prescriptions
  │     │     └── treatments (DrugMaster)
  │     └── clinical
  ├── pathology
  ├── baseline
  ├── safety → analytics (cohort splitting)
  ├── studies → audit (consent gate)
  ├── scheduling
  ├── biomarkers → labs
  ├── audit
  ├── users
  ├── knowledge → patients, labs, pathology
  ├── decision → patients, encounters
  ├── timeline → patients, encounters, clinical, labs, pathology, decision
  ├── clinic → ALL (workflow UI)
  ├── exports → ALL (denormalized dataset)
  └── api → ALL (REST endpoints)
```

### 4.2 Key Architecture Patterns

| Pattern | Implementation |
|---------|---------------|
| **Hub-and-Spoke** | `ClinicalEncounter` as the visit hub connecting labs, prescriptions, events, safety |
| **Computed Models** | `PatientOutcome` and `BiomarkerKinetics` computed from longitudinal data, not entered |
| **Reconciliation Engine** | Prescription finalization auto-maintains `TreatmentExposure` episodes (open/close/split/continue) |
| **Central Review** | Pathology local → central → adjudication workflow with concordance checking |
| **Per-Field Audit** | `AuditLog` captures who/when/old→new on every clinical edit via Django signals |
| **Versioned Consent** | `Consent` supersedes prior; `has_consent()` gates biobank/trial actions |
| **Plugin Eligibility** | Study eligibility criteria are pluggable per study code |
| **Pure-Python Stats** | All statistical methods (KM, Cox, LMM, CIF, MICE) implemented from scratch |

### 4.3 State Machines

**Patient Phase** (encounters/workflow.py):
```
ACTIVE ──complete──► REMISSION ──stable──► POST_REMISSION
  ▲                                              │
  └──────────────── RELAPSE ◄────────────────────┘
```

**Pathology Review** (pathology/services/review.py):
```
LOCAL → CENTRAL → CONCORDANT → _finalize()
                   │
                   └→ DISCORDANT → ADJUDICATION → _finalize()
```

**Prescription Lifecycle**:
```
draft → finalize() → FINAL (immutable, SHA-256 hashed)
         │
         ├── safety checks (renal dosing, intolerance, duplicate, glycaemic)
         └── reconciliation → TreatmentExposure episodes updated
```

---

## 5. Service Layer (39 files, ~102 functions)

### 5.1 Pure-Python Statistical Engine

| Module | Algorithms | Validation |
|--------|-----------|------------|
| `analytics/services/survival.py` | Kaplan-Meier (Greenwood CI), Nelson-Aalen, log-rank test, incidence rate | Freireich 6-MP dataset |
| `analytics/services/cox.py` | Cox PH (Newton-Raphson, Breslow partial likelihood) | Score-test/log-rank identity + Freireich data |
| `analytics/services/competing_risks.py` | Aalen-Johansen CIF with variance | Reduces to 1-KM without competing events |
| `analytics/services/mixed_model.py` | Laird-Ware EM linear mixed-effects | — |
| `analytics/services/imputation.py` | MICE (PMM) + Rubin's rules pooling | — |
| `analytics/services/linalg.py` | Matrix ops (Gauss-Jordan inverse, matmul, etc.) | — |
| `analytics/services/stats_utils.py` | Normal SF (two-sided) | — |

### 5.2 Clinical Services

| Module | Key Functions |
|--------|--------------|
| `prescriptions/services/safety.py` | `check_prescription()` — 4 safety checks (renal dosing, intolerance, duplicate, glycaemic) |
| `prescriptions/services/reconciliation.py` | `plan_reconciliation()`, `apply_reconciliation()` — diff + apply |
| `prescriptions/services/finalize.py` | `finalize_prescription()` — freeze + reconcile |
| `analytics/services/outcomes.py` | `compute_patient_outcome()` — disease-specific remission |
| `analytics/services/remission.py` | Disease-specific remission predicates (IgAN, MN, FSGS, MCD, Lupus) |
| `analytics/services/cohort.py` | `split_patients()`, `cohort_survival()`, `cox_regression()` |
| `pathology/services/review.py` | `submit_review()`, `concordance()`, `adjudicate()` |
| `pathology/services/agreement.py` | `cohens_kappa()`, `fleiss_kappa()` |
| `studies/services/randomization.py` | `enroll()` — screen + consent gate + stratified permuted-block randomization |
| `studies/services/eligibility.py` | `screen()` — pluggable per-study criteria |
| `scheduling/services/schedule.py` | `generate_schedule()`, `due_visits()`, `overdue_visits()` |
| `audit/services/consent.py` | `grant_consent()`, `withdraw_consent()`, `has_consent()` |
| `knowledge/services.py` | `evaluate_patient_rules()` — rule engine |
| `decision/services.py` | `evaluate_case()` — 9 disease profile scoring |
| `biomarkers/services/kinetics.py` | PLA2R, complement, anti-dsDNA kinetics |
| `exports/services/dataset.py` | Denormalized one-row-per-patient dataset |

---

## 6. Security & Compliance

### 6.1 Authentication & Authorization

| Feature | Implementation |
|---------|---------------|
| **Auth** | Django auth + Token + Session auth |
| **RBAC** | Django Groups: `data_manager`, `coordinator`, `investigator`, `pathologist`, `statistician`, `readonly` |
| **Permissions** | `DjangoModelPermissions` on DRF; per-model write gating |
| **API Tokens** | DRF `TokenAuthentication` |
| **Audit Trail** | Per-field `AuditLog` with `AuditMiddleware` (request.user attribution) |
| **X-Change-Reason** | Optional header for audit reason |

### 6.2 Consent Management

| Type | Gating |
|------|--------|
| `registry` | Standard enrollment |
| `biobank` | Sample storage (disabled in v2) |
| `genetic` | Genetic testing |
| `imaging` | Image sharing |
| `trial` | Study enrollment (randomization gate) |

### 6.3 Data Protection

- **De-identified by default** for research exports (Study ID only; no name/phone/reg)
- **Identified export** gated to `data_manager` role
- **SQLite WAL mode** for corruption resilience
- **Backup strategy**: Tiered ZIP retention (Daily 7, Weekly 8, Monthly 12)
- **No cloud-synced live DB** enforced by launcher hardening

---

## 7. REST API Endpoints

| Category | Count |
|----------|-------|
| DRF router (CRUD) | 78 patterns |
| DRF custom actions | ~10 |
| Clinic workflow views | 33 |
| App-specific JSON endpoints | ~40 |
| GDES decision support | 4 |
| **Total unique URL patterns** | **~162** |

### Key API Resources

- `patients`, `encounters`, `events`, `lab-results`, `treatment-exposures`
- `biopsies`, `pathology-reviews`, `adverse-events`, `scheduled-visits`
- `prescriptions`, `outcomes`, `biomarkers`, `drugs`
- `clinical/assess/`, `knowledge/evaluate/`, `decision/evaluate/`, `timeline/{pk}/`

---

## 8. Deployment Modes

### 8.1 Desktop (Single-User Windows)

```
PyInstaller → BGDDR.exe
  └── Waitress (127.0.0.1:8000)
      └── SQLite (local disk, WAL mode)
      └── WhiteNoise (static files)
      └── Backup (tiered ZIP rotation)
```

### 8.2 Production (Docker Compose)

```
Nginx (80/443) → Gunicorn (8000, 4 workers)
  ├── PostgreSQL 16 (persistent volume)
  ├── Redis 7 (persistent volume)
  ├── Celery Worker (concurrency=4)
  └── Celery Beat (DatabaseScheduler)
```

### 8.3 Cloud/Hybrid

- PostgreSQL for analytics layer + pgaudit
- Materialized views available for analytics
- FHIR integration for EHR interoperability
- Celery + Redis for async tasks (reminders, lab alerts, reports)

---

## 9. Key Configuration

### 9.1 Timezone & Locale

| Setting | Value |
|---------|-------|
| `TIME_ZONE` | `Asia/Dhaka` |
| `LANGUAGE_CODE` | `en-us` |
| `USE_TZ` | `True` |
| `USE_I18N` | `True` |

### 9.2 Clinic Configuration

```python
CLINIC = {
    "name_en": "BIRDEM General Hospital — Department of Nephrology",
    "name_bn": "বারডেম জেনারেল হাসপাতাল — নেফ্রোলজি বিভাগ",
    "address": "122 Kazi Nazrul Islam Avenue, Shahbag, Dhaka 1000",
}

SCHEDULING = {
    "clinic_weekday": 1,      # Tuesday
    "session_capacity": 15,
    "window_days": 7,
}
```

### 9.3 Celery Beat Schedule

| Task | Interval | Purpose |
|------|----------|---------|
| `send-due-visit-reminders` | 12 hours | Upcoming visit notifications |
| `send-overdue-visit-reminders` | 24 hours | Overdue visit alerts |
| `detect-lab-trends` | 6 hours | Lab value trend detection |

### 9.4 Data Directories

```
<BGDDR_DATA_DIR>/
├── db.sqlite3        # LIVE database (MUST be local disk)
├── Backups/          # Tiered ZIP archives (cloud-sync safe)
├── Exports/          # CSV/Excel research datasets
├── Media/            # Prescription PDFs, uploads
├── Logs/             # Rotating log files
├── Imports/          # Data ingest scratch
└── Temp/             # Temporary files
```

---

## 10. Package Dependencies

### 10.1 Python (requirements.txt)

```
Django>=5.0
djangorestframework>=3.15
django-jazzmin>=3.0
WeasyPrint>=60
openpyxl>=3.1
pyreadstat>=1.2
pandas>=2.0
waitress>=3.0
whitenoise>=6.6
xhtml2pdf>=0.2.15
celery>=5.4
redis>=5.0
```

### 10.2 Production-only (not in requirements.txt by default)

```
psycopg>=3.1         # PostgreSQL adapter
gunicorn>=22.0       # Production WSGI server
pyinstaller>=6.0     # Desktop build (build-time only)
```

### 10.3 JavaScript (package.json)

```json
{
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "flowbite": "^2.3.0",
    "htmx.org": "^1.9.12"
  }
}
```

---

## 11. Logging Architecture

| Log File | Logger | Rotation |
|----------|--------|----------|
| `application.log` | Root + django | 5MB × 5 |
| `startup.log` | `bgddr` (launcher) | 5MB × 5 |
| `backup.log` | `bgddr.backup` | 5MB × 5 |
| `migration.log` | `safe_migrate.py` | Own rotation |

---

## 12. Documentation Artifacts

The repository contains **50+ markdown documentation files** covering:
- Architecture audits, clinical safety audits, code quality reports
- Clinical workflow validation, knowledge governance
- Pilot deployment guides, production readiness reports
- Version-specific certification reports (V1 through V8)
- Clinical recommendation validation, follow-up engine architecture
- Field error reporting system, continuous knowledge improvement

---

*End of TECHNOLOGY_STACK.md*

# PROJECT_CONTEXT.md — GDES Engineering Knowledge Base

> **Single source of truth** for the GDES (Glomerular Disease Expert System) project.
> Last updated: 2026-07-22
> Repository: `C:\Users\User\Documents\GitHub\GDES`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Directory Structure & Django Apps](#4-directory-structure--django-apps)
5. [Coding Standards](#5-coding-standards)
6. [Naming Standards](#6-naming-standards)
7. [Testing Strategy](#7-testing-strategy)
8. [Deployment Strategy](#8-deployment-strategy)
9. [Dependencies](#9-dependencies)
10. [Clinical Modules — Disease Profiles](#10-clinical-modules--disease-profiles)
11. [Service Layer](#11-service-layer)
12. [REST API Surface](#12-rest-api-surface)
13. [Known Risks](#13-known-risks)
14. [Technical Debt](#14-technical-debt)
15. [Roadmap](#15-roadmap)

---

## 1. Project Overview

### What Is GDES?

**GDES** (Glomerular Disease Expert System) is a clinical expert system and multi-disease
glomerular disease registry built on Django. It is developed at **BIRDEM General Hospital,
Department of Nephrology** in Dhaka, Bangladesh, as part of the **Bangladesh Glomerular
Disease & Diabetes Registry (BGDDR)**.

GDES covers the complete nephrology patient lifecycle:

```
Enroll → Consent → (Randomize) → Follow-up (Prescription + Labs + Biopsy)
      → Compute Outcomes → Analyze by Cohort or Trial Arm
```

### Core Design Principle

> The prescription *is* the follow-up visit.

A single `ClinicalEncounter` per visit is the hub; finalizing a prescription
simultaneously freezes an immutable medico-legal document and reconciles the
medication history for research.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Python LOC | ~47,000 (516 .py files) |
| Django Apps | 30 (28 active + 1 disabled) |
| Django Models | 86 |
| DRF ViewSets | 58 |
| DRF Serializers | 86 |
| Forms | 22 |
| Management Commands | 35 |
| Celery Tasks | 11 |
| URL Patterns | ~162 |
| Documentation Files | 111+ Markdown at root, 230 in docs/ |

### Version History

The project has progressed through versions V1–V8, with each version adding
clinical decision support layers, knowledge base expansion, longitudinal
clinical management, and desktop deployment capabilities.

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Django Admin  │  │  Clinic UI   │  │  REST API (DRF)  │  │
│  │ (Jazzmin)    │  │  (htmx)      │  │  /api/v1/        │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Service Layer (39 files, ~102 functions) │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │
│  │ Analytics  │ │ Knowledge  │ │ Prescription│ │ Decision │  │
│  │ (stats)    │ │ (CDS)      │ │ (safety/    │ │ (disease │  │
│  │            │ │            │ │ reconcile)  │ │ scoring) │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                               │
│  ┌────────────────────────┐  ┌──────────────────────────┐   │
│  │ PostgreSQL (prod)      │  │ SQLite (desktop/WAL)     │   │
│  │ PostgreSQL 16-alpine   │  │ Local disk, 30s timeout  │   │
│  └────────────────────────┘  └──────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     Background / Async                        │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐    │
│  │ Celery   │  │ Redis 7  │  │ Celery Beat (scheduler)│    │
│  │ Worker   │  │ broker   │  │                        │    │
│  └──────────┘  └──────────┘  └────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Dependency Graph (DAG — No Circular Dependencies)

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

### 2.3 Key Architecture Patterns

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

### 2.4 State Machines

**Patient Phase** (`encounters/workflow.py`):
```
ACTIVE ──complete──► REMISSION ──stable──► POST_REMISSION
  ▲                                              │
  └──────────────── RELAPSE ◄────────────────────┘
```

**Pathology Review** (`pathology/services/review.py`):
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

### 2.5 Middleware Stack

1. `SecurityMiddleware`
2. `RatelimitMiddleware` (django-ratelimit)
3. `WhiteNoiseMiddleware` (static file serving)
4. `SessionMiddleware`
5. `CommonMiddleware`
6. `CsrfViewMiddleware`
7. `AuthenticationMiddleware`
8. `MessageMiddleware`
9. `XFrameOptionsMiddleware`
10. `AuditMiddleware` (per-field change tracking)
11. `FeedbackMiddleware` (error reporting & performance monitoring)

---

## 3. Technology Stack

### 3.1 Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.12 (Docker), 3.11/3.13 (local) |
| **Web Framework** | Django | ≥5.0 (5.0.7 pinned) |
| **REST API** | Django REST Framework | ≥3.15 (3.15.2 pinned) |
| **WSGI (dev)** | Django dev server | Built-in |
| **WSGI (desktop)** | Waitress | ≥3.0 (3.0.2 pinned) |
| **WSGI (production)** | Gunicorn | ≥22.0 |
| **Admin Theme** | django-jazzmin | ≥3.0 (3.0.1 pinned) |

### 3.2 Database

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Default DB** | SQLite | Desktop/single-user; WAL mode, 30s busy timeout |
| **Production DB** | PostgreSQL | 16-alpine; psycopg3 adapter (≥3.1) |
| **ORM** | Django ORM | No raw SQL; database-agnostic design |
| **Auto-field** | BigAutoField | Default across all models |

### 3.3 Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| **CSS Framework** | Tailwind CSS | ≥3.4.0 |
| **UI Components** | Flowbite | ≥2.3.0 |
| **JS Library** | htmx.org | ≥1.9.12 |
| **Admin UI** | django-jazzmin | AdminLTE-based with FontAwesome icons |
| **Static Files** | WhiteNoise | ≥6.6 (6.8.2 pinned) |

### 3.4 Background Tasks

| Component | Technology | Version |
|-----------|-----------|---------|
| **Task Queue** | Celery | ≥5.4 (5.4.0 pinned) |
| **Message Broker** | Redis | ≥5.0 (5.2.1 pinned) |
| **Beat Scheduler** | Celery Beat | DatabaseScheduler |

### 3.5 PDF Generation

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Primary PDF** | WeasyPrint | ≥60 (62.3 pinned); requires GTK3+cairo/pango |
| **Fallback PDF** | xhtml2pdf | ≥0.2.15; pure-Python fallback using reportlab |
| **Bilingual Support** | NotoSansBengali TTF | Bengali text in prescriptions |

### 3.6 Data Export & Analytics

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Excel Export** | openpyxl | ≥3.1 (3.1.5 pinned) |
| **SPSS Export** | pyreadstat | ≥1.2 (1.2.7 pinned); .sav format |
| **Data Processing** | pandas | ≥2.0 (2.2.3 pinned) |
| **Statistical Methods** | Pure Python | No external stat libraries — all from scratch |

### 3.7 Containerization (Production)

| Component | Image/Version |
|-----------|---------------|
| **Docker Compose** | v3.9 |
| **App Base Image** | Python 3.12-slim-bookworm |
| **Web Server** | Nginx 1.25-alpine |
| **Database** | PostgreSQL 16-alpine |
| **Cache/Broker** | Redis 7-alpine |

### 3.8 Desktop Deployment (Windows)

| Component | Notes |
|-----------|-------|
| **Packager** | PyInstaller ≥6.0 (`.spec` files in `desktop/`) |
| **WSGI** | Waitress (pure-Python; serves on 127.0.0.1:8000) |
| **Launcher** | `desktop/launcher.py`; auto-migration, hardening |
| **Installer** | PowerShell scripts (`build_exe.ps1`, `setup_production.ps1`) |
| **Data Dir** | Configurable via `BGDDR_DATA_DIR` env var |

---

## 4. Directory Structure & Django Apps

### 4.1 Top-Level Layout

```
GDES/
├── bgddr/                   # Django project (settings, URLs, WSGI)
│   ├── settings.py          # Base settings (SQLite, DEBUG=True)
│   ├── settings_prod.py     # Production (PostgreSQL, DEBUG=False)
│   ├── settings_deploy.py   # Deployment variant
│   ├── settings_desktop.py  # Desktop variant
│   ├── urls.py              # Root URL configuration
│   ├── views.py             # Dashboard views
│   ├── backup.py            # Automatic backup system
│   ├── updater.py           # Auto-updater
│   ├── celery.py            # Celery app configuration
│   └── context_processors.py
│
├── patients/                # ROOT entity — Patient model, Site, UserSiteRole
├── encounters/              # ClinicalEncounter, Admission, RelapseEpisode, ClinicalEvent
├── baseline/                # BaselineAssessment (OneToOne→Patient)
├── labs/                    # LabTest, LabPanel, LabOrder, LabOrderItem, LabResult
├── pathology/               # Biopsy, GNDiagnosis, IgANScore, LupusPathology, etc.
├── treatments/              # DrugMaster, TreatmentExposure
├── prescriptions/           # Prescription, PrescriptionItem, AdviceTemplate
├── analytics/               # PatientOutcome (computed), survival/Cox/eGFR stats
├── exports/                 # Research dataset (CSV/XLSX/SPSS .sav)
│
├── clinical/                # ClinicalAssessment, VitalSign
├── knowledge/               # GuidelineSource, KnowledgeBaseEntry, Disease, etc. (20 models)
├── decision/                # DecisionRequest, DecisionResult (9 disease profiles)
├── timeline/                # TimelineEvent (cross-domain aggregation)
│
├── safety/                  # AdverseEvent (infection/SAE tracking)
├── studies/                 # Study, StudyArm, StudyEnrollment (embedded trials)
├── scheduling/              # ScheduledVisit (protocol follow-up)
├── biomarkers/              # BiomarkerKinetics (PLA2R, complement, anti-dsDNA)
│
├── audit/                   # AuditLog, Consent (per-field change history)
├── users/                   # UserProfile, Invitation (RBAC)
│
├── api/                     # DRF ViewSets at /api/v1/
├── clinic/                  # Workflow UI (no models — patient hub, worklist, charts)
├── reminders/               # Celery tasks for visit/lab reminders
├── fhir/                    # HL7 FHIR export/import
├── events/                  # Event dispatcher, signal handlers
├── clinical_reasoning/      # Clinical intelligence platform (8,885 LOC)
├── followup/                # Follow-up engine with protocol library
├── feedback/                # Field error reporting & continuous improvement (15 models)
│
├── desktop/                 # Desktop launcher scripts, hardening, safe migration
│
├── tests/                   # Central test suite (19 files, 311+ test functions)
├── templates/               # Project-level templates
├── static/                  # Project-level static assets (compiled Tailwind CSS)
│
├── requirements.txt         # Python dependencies
├── package.json             # JS dev dependencies (Tailwind, Flowbite, htmx)
├── docker-compose.yml       # Production Docker Compose
├── pytest.ini               # Test configuration
├── manage.py                # Django management
├── conftest.py              # Pytest configuration
├── tailwind.config.js       # Tailwind CSS configuration
│
├── .hermes/                 # AI agent knowledge base (this file lives here)
│   ├── PROJECT_CONTEXT.md   # ← THIS FILE
│   ├── reports/             # Automated analysis reports
│   └── skills/              # Agent skills
│
├── docs/                    # Documentation (230 files)
└── *.md                     # 111+ Markdown docs at root (see §14 for sprawl)
```

### 4.2 Installed Apps (28 Active)

Organized by functional domain:

#### Core Registry (7 apps)
1. **patients** — `Patient` model (root entity); `Site`, `UserSiteRole`
2. **encounters** — `ClinicalEncounter`, `ClinicalEvent`, `Admission`, `RelapseEpisode`
3. **baseline** — `BaselineAssessment` (OneToOne→Patient)
4. **labs** — `LabTest`, `LabPanel`, `LabOrder`, `LabOrderItem`, `LabResult`
5. **pathology** — `Biopsy`, `GNDiagnosis`, `IgANScore`, `LupusPathology`, `FSGSPathology`, `MembranousPathology`, `BiopsyImage`, `PathologyReview`
6. **treatments** — `DrugMaster`, `TreatmentExposure`
7. **prescriptions** — `Prescription`, `PrescriptionItem`, `AdviceTemplate`

#### Analytics & Research (2 apps)
8. **analytics** — `PatientOutcome` (computed); survival, Cox PH, eGFR slope, CIF, MICE
9. **exports** — Research dataset (CSV/XLSX/SPSS .sav)

#### Clinical Decision Support — GDES (4 apps)
10. **clinical** — `ClinicalAssessment`, `VitalSign`
11. **knowledge** — 20 models (guidelines, rules, diseases, drugs, pathways)
12. **decision** — `DecisionRequest`, `DecisionResult`
13. **timeline** — `TimelineEvent`

#### Operational (4 apps)
14. **safety** — `AdverseEvent`
15. **studies** — `Study`, `StudyArm`, `StudyEnrollment`
16. **scheduling** — `ScheduledVisit`
17. **biomarkers** — `BiomarkerKinetics`

#### Compliance & Access (2 apps)
18. **audit** — `AuditLog`, `Consent`
19. **users** — `UserProfile`, `Invitation`

#### Infrastructure (9 apps)
20. **api** — DRF ViewSets; REST API at `/api/v1/`
21. **clinic** — Workflow UI (no models)
22. **reminders** — Celery tasks for visit/lab reminders
23. **fhir** — HL7 FHIR integration
24. **events** — Event dispatcher, signal handlers
25. **clinical_reasoning** — Clinical intelligence platform
26. **followup** — Follow-up engine with protocol library
27. **feedback** — Field error reporting & continuous improvement (15 models)
28. **bgddr** — Project-level (dashboard views, settings, URL root)

#### Disabled
29. ~~**biobank**~~ — Disabled in protocol v2; code retained for future amendment

---

## 5. Coding Standards

### 5.1 Python Style

- **Formatter/Linter**: `ruff` (0.7.4 in dev dependencies)
- **Type Checking**: `mypy` (1.13.0 in dev dependencies)
- **Target**: Python 3.12 (Docker), 3.11–3.13 (local)
- **Imports**: Standard library → third-party → local; alphabetical within groups
- **Docstrings**: Module-level for all service files; function-level for public APIs

### 5.2 Django Patterns

- **Models**: Always use `BigAutoField` as default (configured globally)
- **Views**: Prefer function-based views for page views; ViewSets for API
- **Forms**: Django ModelForms for data entry
- **Admin**: Register all models; use django-jazzmin for UI
- **Migrations**: Each app has `0001_initial.py`; no raw SQL
- **Signals**: Signal receivers are NOT used (0 found); prefer explicit service calls

### 5.3 Service Layer

- All business logic lives in `services/` subdirectories or `services.py` files
- Pure functions preferred; side effects clearly documented
- Service functions return dataclasses or dicts for structured return types
- 39 service files with ~102 public functions

### 5.4 Security Practices

- **Secrets**: All via environment variables; dev fallback is insecure but documented
- **Auth**: Django auth + Token + Session auth (DRF)
- **RBAC**: Django Groups: `data_manager`, `coordinator`, `investigator`, `pathologist`, `statistician`, `readonly`
- **Audit**: Per-field `AuditLog` via `AuditMiddleware`
- **X-Change-Reason**: Optional header for audit reason attribution
- **No eval/exec/pickle**: Zero instances in codebase
- **Subprocess**: All calls without `shell=True` (safe)

### 5.5 Database Patterns

- **ORM only**: No raw SQL anywhere in the codebase
- **SQLite-specific features avoided**: WAL PRAGMA is the only exception
- **Database-agnostic**: Same ORM schema runs on SQLite (desktop) and PostgreSQL (prod)
- **Computed models**: `PatientOutcome` and `BiomarkerKinetics` are computed, not entered

### 5.6 Frontend Patterns

- **No React/Vue**: Server-rendered HTML with htmx for interactivity
- **Tailwind CSS**: All styling via utility classes
- **Flowbite**: UI component library (modals, dropdowns, etc.)
- **Django Templates**: `{% extends %}` / `{% include %}` inheritance
- **Chart.js**: Client-side charting (vendored in clinic static)

---

## 6. Naming Standards

### 6.1 Models

- **Singular PascalCase**: `Patient`, `ClinicalEncounter`, `LabResult`, `BiopsyImage`
- **FK fields**: `snake_case` + `_id` suffix implicit: `patient`, `encounter`, `biopsy`
- **Boolean fields**: Prefixed with `is_`, `has_`, `contains_`, `ongoing`
- **Choice fields**: `_TYPE`, `_STATUS` suffixes; choices defined as class-level constants
- **Computed fields**: Prefixed with `latest_`, `baseline_`, `first_`
- **Date fields**: `_date` suffix: `enrollment_date`, `collection_date`

### 6.2 Views

- **Function-based**: `snake_case` verb-noun: `patient_detail`, `followup_create`
- **ViewSets**: `PascalCase` + `ViewSet` suffix: `PatientViewSet`, `ClinicalProfileViewSet`
- **Private helpers**: Underscore prefix: `_serialize_cohort`, `_parse`, `_f`

### 6.3 URLs

- **Namespace**: App name: `clinic`, `analytics`, `api`, `knowledge`
- **Path segments**: Kebab-case: `/patient-create/`, `/cohort-survival/`
- **API paths**: RESTful: `/api/v1/patients/`, `/api/v1/biopsies/`

### 6.4 Files

- **Modules**: `snake_case.py`: `services.py`, `models.py`, `tests.py`
- **Services**: Subdirectory pattern: `app/services/module.py`
- **Tests**: `tests.py` for in-app; `tests/` directory for central suite
- **Management commands**: `snake_case.py`: `seed_knowledge_base.py`

### 6.5 Knowledge Base Entries

- **Entry IDs**: `KN-{DISEASE}-{SEQUENCE}` format (e.g., `KN-IGAN-001`)
- **Disease IDs**: Lowercase abbreviated: `iga`, `membranous`, `mcd`, `fsgs`, `lupus`, `anca`, `antiGbm`, `infectionRelated`, `c3`
- **Rule templates**: `TEMPLATE-{TYPE}-{SEQUENCE}`

### 6.6 Settings Modules

- `bgddr/settings.py` — Base (SQLite, DEBUG=True)
- `bgddr/settings_prod.py` — Production (PostgreSQL, DEBUG=False)
- `bgddr/settings_deploy.py` — Deployment variant
- `bgddr/settings_desktop.py` — Desktop variant (auto-generated key)

---

## 7. Testing Strategy

### 7.1 Test Infrastructure

| Component | Status | Notes |
|-----------|--------|-------|
| **Framework** | Django test runner + pytest | `python manage.py test` or `pytest` |
| **Config** | `pytest.ini` | `testpaths = tests feedback/tests.py` |
| **conftest.py (root)** | ✅ | Sets Django settings, calls `django.setup()` |
| **conftest.py (tests/)** | ✅ | Session-scoped DB fixture with `load_test_knowledge` |
| **pytest-django** | ✅ | Implied by `django_find_project` |
| **pytest-cov** | 6.0.0 in dev deps | Not yet configured in pytest.ini |

### 7.2 Test Files by App

| App | Test Files | LOC | Functions | Status |
|-----|-----------|-----|-----------|--------|
| `tests/` (central) | 19 files | 3,800+ | 311+ | ✅ Primary suite |
| `knowledge` | 3 files | 2,474 | ~60 | ✅ Well tested |
| `analytics` | 2 files | ~400 | ~15 | ⚠️ Moderate |
| `labs` | 2 files | ~200 | ~8 | ⚠️ Moderate |
| `feedback` | 1 file | ~300 | ~12 | ⚠️ Moderate |
| `studies` | 1 file | ~150 | 10 | ⚠️ Minimal |

### 7.3 Apps with ZERO Test Files (10 apps, ~18,000 LOC untested)

| App | LOC | Risk |
|-----|-----|------|
| **clinical_reasoning** | 8,885 | 🔴 CRITICAL |
| **clinic** | 2,276 | 🔴 HIGH |
| **decision** | 1,150 | 🔴 HIGH |
| **users** | 573 | 🟡 MEDIUM |
| **treatments** | 1,730 | 🟡 MEDIUM |
| **bgddr** | 1,846 | 🟡 MEDIUM |
| **desktop** | 3,130 | 🟡 MEDIUM |
| **encounters** | 454 | 🟡 MEDIUM |
| **events** | 370 | 🟡 MEDIUM |
| **fhir** | 578 | 🟡 MEDIUM |

### 7.4 Coverage Estimates

| Domain | Estimated Coverage |
|--------|-------------------|
| Knowledge management | ~70% |
| Desktop/backup | ~50% |
| Drug interactions | ~40% |
| Clinical reasoning/CDS | ~30% |
| Event system | ~30% |
| Patient management | ~20% |
| **Overall** | **~20–25%** |

### 7.5 Validation Tests

- **Freireich 6-MP dataset**: KM + log-rank verified against published benchmark
- **Cohen's kappa**: Textbook κ=0.40 verification in agreement module
- **Score-test/log-rank identity**: Cox PH validated

### 7.6 Test Gaps & Recommendations

| Priority | Action |
|----------|--------|
| 🔴 Critical | Fix `pytest.ini` testpaths to include ALL app-level test files |
| 🔴 Critical | Add tests for clinical_reasoning, clinic, decision, users, treatments |
| 🔴 Critical | Enable `pytest-cov` and generate coverage reports |
| 🔴 Critical | Set up CI pipeline (GitHub Actions) |
| 🟡 High | Add `factory_boy` or `model_bakery` for test fixtures |
| 🟡 High | Split monolithic test files (knowledge/tests.py) |
| 🟢 Low | Add mutation testing (`mutmut`) for critical CDS logic |

---

## 8. Deployment Strategy

### 8.1 Desktop (Single-User Windows)

```
PyInstaller → BGDDR.exe
  └── Waitress (127.0.0.1:8000)
      ├── SQLite (local disk, WAL mode)
      ├── WhiteNoise (static files from WSGI app)
      └── Backup (tiered ZIP rotation: Daily 7, Weekly 8, Monthly 12)
```

- **Launcher**: `desktop/launcher.py` (1,099 LOC) handles:
  - Auto-migration on startup
  - Database hardening (cloud-sync detection)
  - Waitress server launch
  - First-run folder wizard
- **Data safety**: Live SQLite MUST NOT live in cloud-synced folders
- **Settings**: `settings_desktop.py` generates random SECRET_KEY, persists to file

### 8.2 Production (Docker Compose)

```
Nginx (80/443) → Gunicorn (8000, 4 workers)
  ├── PostgreSQL 16 (persistent volume)
  ├── Redis 7 (persistent volume)
  ├── Celery Worker (concurrency=4)
  └── Celery Beat (DatabaseScheduler)
```

- **Settings**: `settings_prod.py` (DEBUG=False, requires DJANGO_SECRET_KEY)
- **SSL**: Configurable via Nginx
- **Static files**: WhiteNoise (compressed, non-manifest)
- **Database**: PostgreSQL with pgaudit for materialized-view analytics layer

### 8.3 Data Directory Layout

```
<BGDDR_DATA_DIR>/
├── db.sqlite3        # LIVE database (MUST be local disk)
├── Backups/          # Tiered ZIP archives (cloud-sync safe)
├── Exports/          # CSV/Excel research datasets
├── Media/            # Prescription PDFs, uploads
│   └── prescriptions/
├── Logs/             # Rotating log files (5MB × 5)
├── Imports/          # Data ingest scratch
├── Temp/             # Temporary files
└── staticfiles/      # Collected static assets
```

### 8.4 Celery Beat Schedule

| Task | Interval | Purpose |
|------|----------|---------|
| `send-due-visit-reminders` | 12 hours | Upcoming visit notifications |
| `send-overdue-visit-reminders` | 24 hours | Overdue visit alerts |
| `detect-lab-trends` | 6 hours | Lab value trend detection |

### 8.5 Logging

| Log File | Logger | Rotation |
|----------|--------|----------|
| `application.log` | Root + django | 5MB × 5 |
| `startup.log` | `bgddr` (launcher) | 5MB × 5 |
| `backup.log` | `bgddr.backup` | 5MB × 5 |
| `migration.log` | `safe_migrate.py` | Own rotation |

---

## 9. Dependencies

### 9.1 Python (requirements.txt — Exact Pinned Versions)

```
Django~=5.0.7
djangorestframework~=3.15.2
django-jazzmin~=3.0.1
WeasyPrint~=62.3
openpyxl~=3.1.5
pyreadstat~=1.2.7
pandas~=2.2.3
waitress~=3.0.2
whitenoise~=6.8.2
xhtml2pdf~=0.2.16
celery~=5.4.0
redis~=5.2.1
django-csp~=3.8.0
django-ratelimit~=4.1.0
pytest~=8.3.4
pytest-cov~=6.0.0
ruff~=0.7.4
mypy~=1.13.0
```

### 9.2 Production-Only (Commented Out by Default)

```
# psycopg~=3.2.3           # PostgreSQL adapter
# gunicorn~=22.0.0         # Production WSGI server
# pyinstaller~=6.10.0      # Desktop build (build-time only)
```

### 9.3 Commented-Out / Planned

```
# twilio~=9.0.0            # SMS / WhatsApp Business API
# django-csp~=3.8.0        # NOTE: now uncommented and active in settings
# django-ratelimit~=4.1.0  # NOTE: now uncommented and active in settings
```

### 9.4 JavaScript (package.json)

```json
{
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "flowbite": "^2.3.0",
    "htmx.org": "^1.9.12"
  }
}
```

### 9.5 Docker Images

| Service | Image |
|---------|-------|
| App | `python:3.12-slim-bookworm` |
| Database | `postgres:16-alpine` |
| Cache | `redis:7-alpine` |
| Web | `nginx:1.25-alpine` |

---

## 10. Clinical Modules — Disease Profiles

### 10.1 Nine Disease Profiles

The decision engine (`decision/services.py`) evaluates patients against 9
glomerular disease profiles. Each profile has specific scoring criteria,
remission definitions, and biomarker thresholds.

| # | Disease | ID | Category | Scoring System | Key Biomarker |
|---|---------|----|----------|---------------|---------------|
| 1 | **IgA Nephropathy (IgAN)** | `iga` | Primary GN | Oxford MEST-C | — |
| 2 | **Membranous Nephropathy (MN)** | `membranous` | Primary GN | Ehrenreich-Churg I–IV | Anti-PLA2R |
| 3 | **Focal Segmental Glomerulosclerosis (FSGS)** | `fsgs` | Primary GN | Columbia Classification | — |
| 4 | **Minimal Change Disease (MCD)** | `mcd` | Primary GN | — | — |
| 5 | **Lupus Nephritis (LN)** | `lupus` | Secondary GN | ISN/RPS I–VI + NIH AI/CI | Anti-dsDNA, C3/C4 |
| 6 | **ANCA-Associated Vasculitis (AAV)** | `anca` | Secondary GN | — | ANCA |
| 7 | **Anti-GBM Disease** | `antiGbm` | Secondary GN | — | Anti-GBM Ab |
| 8 | **Infection-Related GN** | `infectionRelated` | Secondary GN | — | — |
| 9 | **C3 Glomerulopathy** | `c3` | Complement-mediated | — | C3/C4 |

### 10.2 Disease-Specific Pathology Scores

#### Oxford MEST-C Score (IgAN)

| Component | Range | Description |
|-----------|-------|-------------|
| **M** (Mesangial) | 0–1 | Mesangial hypercellularity (>50% glomeruli) |
| **E** (Endocapillary) | 0–1 | Endocapillary hypercellularity |
| **S** (Segmental) | 0–1 | Segmental sclerosis |
| **T** (Tubular) | 0–2 | Tubular atrophy/interstitial fibrosis (most powerful predictor) |
| **C** (Crescents) | 0–2 | Crescent formation (>25% → poor prognosis) |

#### ISN/RPS Classification (Lupus Nephritis)

| Class | Description |
|-------|-------------|
| I | Minimal mesangial |
| II | Mesangial proliferative |
| III | Focal proliferative |
| IV | Diffuse proliferative (most common, most aggressive) |
| V | Membranous |
| VI | Sclerotic |

Plus NIH Activity Index (0–24) and Chronicity Index (0–12).

#### Columbia Classification (FSGS)

| Variant | Prognosis |
|---------|-----------|
| NOS | Most common, intermediate |
| Perihilar | — |
| Cellular | — |
| Tip | Best prognosis |
| Collapsing | Worst prognosis (HIV-associated) |

#### Ehrenreich-Churg Staging (Membranous Nephropathy)

| Stage | Description |
|-------|-------------|
| I | Subepithelial deposits |
| II | Spikes |
| III | Chain-link formation |
| IV | Dissolution |

### 10.3 Remission Criteria

| Disease | Complete Remission | Partial Remission | Response |
|---------|-------------------|-------------------|----------|
| **IgAN** | < 0.3 g/day | — | ≥30% reduction OR <0.3; target <0.5 |
| **MN** | < 0.3 g/day | ≥50% reduction & < 3.5 g/day | — |
| **FSGS** | < 0.3 g/day | ≥50% reduction & < 3.5 g/day | — |
| **MCD** | < 0.3 g/day | ≥50% reduction & < 3.5 g/day | — |
| **Lupus** | < 0.5 g/day + eGFR within 10% of baseline | ≥50% reduction & < 3.5 | — |

### 10.4 Biomarker Thresholds

| Biomarker | Disease | Actionable Threshold |
|-----------|---------|---------------------|
| Anti-PLA2R | MN | ≥50% decline → early response predictor |
| Anti-PLA2R seroconversion | MN | Negative → immunological remission |
| Complement C3/C4 | LN/C3G | Normalization → complement recovery |
| Anti-dsDNA | LN | Normalization → disease control |

### 10.5 Knowledge Base Structure

The `knowledge` app (20 models, 24 Python files) provides:

- **GuidelineSource**: Reference guidelines (KDIGO, etc.) with versioning
- **KnowledgeBaseEntry**: Structured rules with conditions, weights, explanations
- **KnowledgeBaseVersion**: Versioned rule snapshots with diffs
- **Disease**: 9 disease profiles with epidemiology, etiology, diagnostic criteria
- **ClinicalPathway**: Stage-based treatment pathways per disease
- **Syndrome**: Presentation patterns (nephrotic, nephritic, RPGN, mixed)
- **PathologyEntity**: Histological findings and their significance
- **LabEntity**: Lab test interpretation and clinical implications
- **DrugIntelligence**: Drug properties, dosing, contraindications
- **MonitoringProtocol**: Drug-specific monitoring schedules
- **Complication**: Disease-specific complications and management
- **KnowledgeGraphNode/Edge**: Graph-based medical knowledge representation

**Evidence Grades**: 1 (highest), 2, NG (not graded), OP (expert opinion)

---

## 11. Service Layer

### 11.1 Pure-Python Statistical Engine

| Module | Algorithms | Validation |
|--------|-----------|------------|
| `analytics/services/survival.py` | Kaplan-Meier (Greenwood CI), Nelson-Aalen, log-rank, incidence rate | Freireich 6-MP dataset |
| `analytics/services/cox.py` | Cox PH (Newton-Raphson, Breslow partial likelihood) | Score-test/log-rank identity |
| `analytics/services/competing_risks.py` | Aalen-Johansen CIF with variance | Reduces to 1-KM without competing events |
| `analytics/services/mixed_model.py` | Laird-Ware EM linear mixed-effects | — |
| `analytics/services/imputation.py` | MICE (PMM) + Rubin's rules pooling | — |
| `analytics/services/linalg.py` | Matrix ops (Gauss-Jordan inverse, matmul, etc.) | — |
| `analytics/services/stats_utils.py` | Normal SF (two-sided) | — |

### 11.2 Clinical Services

| Module | Key Functions |
|--------|--------------|
| `prescriptions/services/safety.py` | `check_prescription()` — 4 safety checks |
| `prescriptions/services/reconciliation.py` | `plan_reconciliation()`, `apply_reconciliation()` |
| `prescriptions/services/finalize.py` | `finalize_prescription()` — freeze + reconcile |
| `analytics/services/outcomes.py` | `compute_patient_outcome()` — disease-specific remission |
| `analytics/services/remission.py` | Disease-specific remission predicates (IgAN, MN, FSGS, MCD, Lupus) |
| `analytics/services/cohort.py` | `split_patients()`, `cohort_survival()`, `cox_regression()` |
| `pathology/services/review.py` | `submit_review()`, `concordance()`, `adjudicate()` |
| `pathology/services/agreement.py` | `cohens_kappa()`, `fleiss_kappa()` |
| `studies/services/randomization.py` | `enroll()` — screen + consent + stratified permuted-block randomization |
| `studies/services/eligibility.py` | `screen()` — pluggable per-study criteria |
| `scheduling/services/schedule.py` | `generate_schedule()`, `due_visits()`, `overdue_visits()` |
| `audit/services/consent.py` | `grant_consent()`, `withdraw_consent()`, `has_consent()` |
| `knowledge/services.py` | `evaluate_patient_rules()` — rule engine |
| `decision/services.py` | `evaluate_case()` — 9 disease profile scoring |
| `biomarkers/services/kinetics.py` | PLA2R, complement, anti-dsDNA kinetics |
| `exports/services/dataset.py` | Denormalized one-row-per-patient dataset |

### 11.3 Key Feature: Prescription Safety Checks

| Check | Description |
|-------|-------------|
| **Renal Dosing** | Drug flagged for adjustment + patient eGFR below threshold |
| **Prior Intolerance** | Re-prescribing drug previously stopped for AE/intolerance |
| **Duplicate Therapy** | Two drugs of same DrugClass on one prescription |
| **Glycaemic Effect** | Steroid/CNI in diabetic → intensification warning |

### 11.4 Key Feature: Outcome Computation Pipeline

```
compute_patient_outcome(patient):
  1. Extract longitudinal series: eGFR, creatinine, proteinuria
  2. Determine index date (enrollment or earliest lab/encounter)
  3. Compute sustained declines (>40%, >50%, doubling creatinine)
  4. Check hard endpoints from ClinicalEvent (ESKD, death, etc.)
  5. Apply disease-specific remission rules
  6. Detect proteinuria relapse
  7. Update PatientOutcome (denormalized row)
```

---

## 12. REST API Surface

### 12.1 API Endpoints Summary

| Category | Count |
|----------|-------|
| DRF router (CRUD) | 78 patterns |
| DRF custom actions | ~10 |
| Clinic workflow views | 33 |
| App-specific JSON endpoints | ~40 |
| GDES decision support | 4 |
| **Total unique URL patterns** | **~162** |

### 12.2 Key API Resources

- `patients`, `encounters`, `events`, `lab-results`, `treatment-exposures`
- `biopsies`, `pathology-reviews`, `adverse-events`, `scheduled-visits`
- `prescriptions`, `outcomes`, `biomarkers`, `drugs`
- `clinical/assess/`, `knowledge/evaluate/`, `decision/evaluate/`, `timeline/{pk}/`

### 12.3 Authentication & Permissions

- **Read**: Any authenticated user
- **Write**: Gated per-model via `DjangoModelPermissions` (user's Group determines access)
- **Token auth**: DRF `TokenAuthentication`
- **Session auth**: `SessionAuthentication`
- **Pagination**: `PageNumberPagination`, PAGE_SIZE=50

### 12.4 RBAC Groups

| Group | Purpose |
|-------|---------|
| `data_manager` | Full data access + identified exports |
| `coordinator` | Clinical coordination |
| `investigator` | Research access |
| `pathologist` | Pathology review |
| `statistician` | Analytics access |
| `readonly` | Read-only access |

---

## 13. Known Risks

### 13.1 Security Risks

| Severity | Risk | Status |
|----------|------|--------|
| 🔴 CRITICAL | Hardcoded admin credentials (`admin`/`bgddr-admin`) in 3 launcher files | Open |
| 🔴 HIGH | CSP headers — `django-csp` enabled in code but verify headers are rendering | Enabled |
| 🔴 HIGH | Rate limiting — `django-ratelimit` enabled in code but verify middleware is active | Enabled |
| 🟡 HIGH | Dev SECRET_KEY fallback `"dev-only-insecure-change-me"` | Open |
| 🟡 MEDIUM | No data encryption at rest (SQLite unencrypted) | Open |
| 🟡 MEDIUM | No HIPAA-specific security controls | Open |
| 🟡 MEDIUM | No HSTS or SSL redirect configured in base settings | Open |

### 13.2 Data Integrity Risks

| Severity | Risk | Mitigation |
|----------|------|------------|
| 🔴 HIGH | SQLite cloud-sync corruption | Launcher hardening + `BGDDR_ALLOW_SYNCED_DB` guard |
| 🟡 MEDIUM | No database encryption | PostgreSQL recommended for production |
| 🟡 MEDIUM | Backup without verification | Tiered ZIP retention (Daily 7, Weekly 8, Monthly 12) |

### 13.3 Clinical Safety Risks

| Severity | Risk | Mitigation |
|----------|------|------------|
| 🔴 HIGH | No test coverage for `clinical_reasoning` (8,885 LOC) | Add tests |
| 🔴 HIGH | No test coverage for `decision` (1,150 LOC) | Add tests |
| 🟡 MEDIUM | Pure-Python stats not validated against external packages | Freireich validation |
| 🟡 MEDIUM | Knowledge base seeded via code — difficult to audit | `load_test_knowledge` for testing |

### 13.4 Operational Risks

| Severity | Risk | Notes |
|----------|------|-------|
| 🟡 MEDIUM | All deps use `>=` without upper bounds | Pin versions |
| 🟡 MEDIUM | No CI/CD pipeline | No automated testing on push |
| 🟡 MEDIUM | No coverage measurement | `pytest-cov` available but not configured |
| 🟢 LOW | WeasyPrint requires native GTK3+cairo libs | xhtml2pdf fallback available |

---

## 14. Technical Debt

### 14.1 Debt Score

| Dimension | Score (1–10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Code Duplication | 7 | 15% | 1.05 |
| Dead Code | 8 | 10% | 0.80 |
| Documentation Sprawl | 7 | 10% | 0.70 |
| God Files | 8 | 20% | 1.60 |
| Test Coverage | 6 | 25% | 1.50 |
| Migration Cleanliness | 4 | 5% | 0.20 |
| Dependency Management | 6 | 10% | 0.60 |
| Security Gaps | 7 | 5% | 0.35 |
| **TOTAL** | | **100%** | **6.8 / 10** |

### 14.2 God Files (Top 10 — 16% of All Code)

| File | LOC | Issue |
|------|-----|-------|
| `clinical_reasoning/services/management_plan.py` | **2,196** | 9 disease-specific protocol generators in one file |
| `clinic/views.py` | **1,507** | 58 view functions in one file |
| `knowledge/tests.py` | **1,235** | Monolithic test file |
| `knowledge/management/commands/seed_v4_knowledge.py` | **1,101** | Data seeding as code |
| `desktop/launcher.py` | **1,099** | Desktop launcher monolith |
| `knowledge/management/commands/seed_knowledge_base.py` | **1,021** | More seeding as code |
| `knowledge/views.py` | **989** | 102 view functions (actually 19 ViewSets + 2 viewsets) |
| `desktop/launcher-Dr-Wasim-2.py` | **901** | Duplicate launcher |
| `knowledge/models.py` | **841** | 15+ models in one file |
| `desktop/launcher-Dr-Wasim.py` | **763** | Duplicate launcher |

### 14.3 Dead Code & Temp Files

| File | Action |
|------|--------|
| `_tmp_ms_test.py` | DELETE |
| `check_patient_221.py` | DELETE or move to `scripts/` |
| `find_dups.py` | Move to `scripts/` |
| `inspect_db.py` | Move to `scripts/` |
| `tmp_audit_c3.py` | DELETE |
| `cleanup_dups.sql` | Move to `scripts/` |
| `desktop/launcher-Dr-Wasim.py` | Consolidate into main launcher |
| `desktop/launcher-Dr-Wasim-2.py` | Consolidate into main launcher |
| `bgddr/version-Dr-Wasim.py` | Consolidate |

### 14.4 Documentation Sprawl

- **111+ Markdown files at root**: Many are version-specific (V1–V8) and no longer actionable
- **230 files in `docs/`**: Additional documentation
- **Categories**: ~20 version mission docs, ~15 audit reports, ~10 validation reports, ~8 architecture docs, ~50+ other

### 14.5 Migration Debt

| App | Migrations | Concern |
|-----|-----------|---------|
| knowledge | 9 | 🔴 Heaviest — consider squashing |
| pathology | 7 | ⚠️ Multiple schema changes |
| patients | 7 | ⚠️ Complex evolution |
| prescriptions | 5 | ⚠️ Evolved over time |
| treatments | 5 | ⚠️ Multiple changes |
| All others | 1–4 each | ✅ Clean |
| **Total** | **64** | No evidence of migration squash ever performed |

### 14.6 Coupling Issues

- **`clinic/forms.py`**: Imports from 8 different apps (maximum coupling)
- **`clinical_reasoning` → `knowledge`**: 5 files with tight coupling
- **`feedback` → `knowledge` + `bgddr`**: Cross-cutting concerns

### 14.7 Prioritized Recommendations

#### 🔴 Critical (Immediate)
1. Remove all temp/debug scripts from root
2. Remove hardcoded credentials from launcher files
3. Consolidate 3 launcher files into 1 with configuration profiles

#### 🟡 High (Current Sprint)
4. Split `management_plan.py` into per-disease modules
5. Decompose `clinic/views.py` into view modules
6. Add test coverage for critical untested apps
7. Archive or remove stale version docs from root
8. Enable CI pipeline

#### 🟢 Medium (Next Sprint)
9. Squash knowledge migrations (9 → 1)
10. Split `knowledge/models.py` into model modules
11. Reduce `clinic/forms.py` coupling via service layer
12. Add coverage reporting
13. Create `scripts/` directory and move utilities there

---

## 15. Roadmap

### 15.1 Version History & Milestones

| Version | Milestone | Key Features |
|---------|-----------|-------------|
| V1 | Initial Release | Core registry, patient management, encounters |
| V2 | Knowledge Platform | Clinical decision support, knowledge base, disease profiles |
| V3 | Production Release | Security hardening, audit trail, consent management |
| V4 | Medical Knowledge Expansion | 200+ rules, drug intelligence, clinical pathways, guidelines |
| V5 | Follow-up Automation | Follow-up engine, scheduling, reminders, Celery |
| V6 | Clinical Validation | Desktop deployment, backup system, PyInstaller |
| V7 | Longitudinal Management | Biomarker kinetics, outcome computation, eGFR slope |
| V8 | Continuous Improvement | Field error reporting, feedback system, performance monitoring |

### 15.2 Current Phase (V8 / Post-V8)

- **Field Error Reporting**: `feedback` app with 15 models for crash reports, clinical conflicts, knowledge conflicts, AI failures
- **Continuous Knowledge Improvement**: `KnowledgeImprovementSuggestion` model for clinician-driven rule refinement
- **Performance Monitoring**: `PerformanceLog` for timing metrics
- **Telemetry**: Opt-in upload to GitHub for error tracking

### 15.3 Future Directions (Planned)

| Priority | Feature | Notes |
|----------|---------|-------|
| 🔴 High | CI/CD Pipeline | GitHub Actions for automated testing |
| 🔴 High | Test Coverage | Reach 60%+ for critical clinical apps |
| 🟡 High | FHIR Full Implementation | `fhir` app currently has skeleton (no models) |
| 🟡 Medium | Data Encryption | SQLCipher for SQLite or mandatory PostgreSQL |
| 🟡 Medium | HIPAA Controls | Audit logging, access controls, encryption |
| 🟡 Medium | SMS Integration | Twilio (commented out in requirements) |
| 🟢 Low | Mutation Testing | `mutmut` for CDS logic validation |
| 🟢 Low | Documentation Cleanup | Archive V1–V6 docs, consolidate to .hermes/ |

### 15.4 Alignment with GN Master Protocol v3 (Bangladesh)

| Protocol Section | GDES Implementation |
|-----------------|---------------------|
| §7.3 Central pathology review | `pathology` app: local → central → adjudication |
| §7.6 Follow-up scheduling | `scheduling` app: Tuesday clinics, ±7-day windows, 15 slots |
| §7.7 Immunosuppression monitoring | `scheduling/services/monitoring.py` |
| §9.1 Disease-specific remission | `analytics/services/remission.py` |
| §9.3 Biomarker kinetics | `biomarkers` app: PLA2R, complement, anti-dsDNA |
| §9.4 Adverse events | `safety` app: infection, steroid toxicity, SAE tracking |
| §10.3 eGFR slope | `analytics/services/mixed_model.py`: Laird-Ware EM |
| §10.4 Competing risks | `analytics/services/competing_risks.py`: Aalen-Johansen |
| §11.3 Inter-observer agreement | `pathology/services/agreement.py`: Cohen's κ |
| §11.5 Data governance | De-identified by default; identified export gated |
| §13.5 Data protection | Role-based access; audit trail; consent gating |

### 15.5 Clinic Configuration

```python
CLINIC = {
    "name_en": "BIRDEM General Hospital — Department of Nephrology",
    "name_bn": "বারডেম জেনারেল হাসপাতাল — নেফ্রোলজি বিভাগ",
    "address": "122 Kazi Nazrul Islam Avenue, Shahbag, Dhaka 1000",
    "registry": "Bangladesh Glomerular Disease & Diabetes Registry (BGDDR)",
}

SCHEDULING = {
    "clinic_weekday": 1,      # Tuesday (Monday=0)
    "session_capacity": 15,
    "window_days": 7,
}

TIME_ZONE = "Asia/Dhaka"
```

---

## Appendix A: Model Count by App

| App | Models | Key Models |
|-----|--------|-----------|
| knowledge | 20 | KnowledgeBaseEntry, Disease, ClinicalPathway, DrugIntelligence, etc. |
| feedback | 15 | ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict, etc. |
| pathology | 8 | Biopsy, GNDiagnosis, IgANScore, LupusPathology, PathologyReview, etc. |
| labs | 5 | LabTest, LabPanel, LabOrder, LabOrderItem, LabResult |
| encounters | 4 | ClinicalEncounter, ClinicalEvent, Admission, RelapseEpisode |
| patients | 3 | Patient, Site, UserSiteRole |
| prescriptions | 3 | Prescription, PrescriptionItem, AdviceTemplate |
| studies | 3 | Study, StudyArm, StudyEnrollment |
| reminders | 3 | ReminderSchedule, ReminderTemplate, PatientCommunicationPreference |
| clinical_reasoning | 2 | ClinicalProfile, ClinicalInsight |
| clinical | 2 | ClinicalAssessment, VitalSign |
| decision | 2 | DecisionRequest, DecisionResult |
| treatments | 2 | DrugMaster, TreatmentExposure |
| events | 2 | Event, EventSubscription |
| audit | 2 | AuditLog, Consent |
| users | 2 | UserProfile, Invitation |
| analytics | 1 | PatientOutcome |
| biomarkers | 1 | BiomarkerKinetics |
| safety | 1 | AdverseEvent |
| scheduling | 1 | ScheduledVisit |
| timeline | 1 | TimelineEvent |
| followup | 1 | FollowUpTask |
| **Total** | **86** | |

## Appendix B: Management Commands (35 total)

| App | Commands | Purpose |
|-----|----------|---------|
| knowledge | 14 | Seed, validate, import, export knowledge base |
| patients | 6 | Backup, restore, integrity, delete, reset, validate |
| feedback | 3 | Export/import feedback packages, upload logs |
| studies | 2 | Auto-screen patients, seed studies |
| analytics | 1 | Compute patient outcomes |
| api | 1 | Seed roles and permissions |
| audit | 1 | Restore backup |
| biomarkers | 1 | Compute biomarkers |
| clinics | 0 | — |
| clinical_reasoning | 1 | Deactivate test rules |
| encounters | 0 | — |
| exports | 0 | — |
| fhir | 0 | — |
| followup | 1 | Follow-up engine CLI |
| labs | 1 | Seed lab test catalog |
| prescriptions | 1 | Seed drug formulary |
| treatments | 1 | Seed drug knowledge |

---

*This document is maintained by the AI agent system under `.hermes/`. It is the single
engineering knowledge base for the GDES project. Update it whenever significant
architectural changes occur.*

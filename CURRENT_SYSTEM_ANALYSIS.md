# BGDDR — Current System Analysis

## Executive Summary

The **Bangladesh Glomerular Disease & Diabetes Registry (BGDDR)** is a clinical research registry built at BIRDEM General Hospital, Department of Nephrology (Dhaka, Bangladesh). It is a Django 5.x monolithic application with a REST API layer, designed to run as both a **multi-user web application** (PostgreSQL-backed) and a **single-user Windows desktop application** (SQLite-backed, OneDrive-syncable).

The system captures the full lifecycle of glomerular disease (GN) patients — from suspected GN through biopsy, treatment, longitudinal follow-up, and research outcome analysis — with a parallel capability for embedded randomized controlled trials.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Backend framework | Django | ≥5.0 |
| REST API | Django REST Framework | ≥3.15 |
| Admin UI theme | django-jazzmin | ≥3.0 |
| Database (dev/desktop) | SQLite | (bundled) |
| Database (production) | PostgreSQL | (via psycopg3, optional) |
| PDF generation | WeasyPrint / xhtml2pdf | ≥60 / ≥0.2.15 |
| Excel export | openpyxl | ≥3.1 |
| SPSS export | pyreadstat + pandas | ≥1.2 / ≥2.0 |
| Desktop WSGI server | waitress | ≥3.0 |
| Static file serving | WhiteNoise | ≥6.6 |
| Frontend | Tailwind CSS (compiled) | (via Node.js) |
| Desktop packaging | PyInstaller | (build-time) |

---

## Deployment Model

The system supports two deployment modes:

### 1. Desktop / Single-User (Primary)
- Runs on Windows via `Start-BGDDR.bat` → `desktop/launcher.py` → waitress on 127.0.0.1:8000
- SQLite database stored in `BGDDR_DATA_DIR` (defaults to project root)
- All mutable data (DB, Backups, Exports, Media, Logs) lives under `BGDDR_DATA_DIR` for OneDrive sync
- WhiteNoise serves compiled static files directly from WSGI (no nginx needed)
- PyInstaller builds a standalone `BGDDR.exe` for distribution

### 2. Multi-User / Production (PostgreSQL)
- Environment-driven: `DJANGO_DB_ENGINE=postgres` switches the ORM to PostgreSQL
- gunicorn for WSGI serving behind nginx/reverse proxy
- Token + session authentication for API and UI

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Browser UI  │  │  REST API    │  │  Desktop (BGDDR.exe)   │ │
│  │  (Admin +    │  │  (DRF)       │  │  (waitress on          │ │
│  │   clinic)    │  │              │  │   127.0.0.1:8000)      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘ │
└─────────┼──────────────────┼────────────────────┼───────────────┘
          │                  │                    │
┌─────────┼──────────────────┼────────────────────┼───────────────┐
│         ▼                  ▼                    ▼               │
│                    DJANGO URL ROUTER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  bgddr/urls.py  →  app URLs                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                    MIDDLEWARE                                    │
│  SecurityMiddleware → WhiteNoise → Session → CSRF → Auth →      │
│  AuditMiddleware                                        Audit  │
│                           │                                     │
│                    VIEW LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Admin (Jazzmin)│ │ Clinic Views │  │ API ViewSets (DRF)   │  │
│  │ 38 model      │ │ 38 views     │  │ 18 viewsets +        │  │
│  │ admin classes │ │ (workflow)   │  │ 5 custom actions     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                           │                                     │
│                    SERVICE LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  39 service files │ ~102 public functions │ 10 dataclasses  │ │
│  │  workflows, analytics, safety, prescriptions, exports      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                    MODEL LAYER                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  38 Django models across 18 apps                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                    DATABASE                                     │
│  ┌──────────────┐  ┌────────────────────────────────────────┐  │
│  │  SQLite       │  │  PostgreSQL (production)               │  │
│  │  (desktop)    │  │                                        │  │
│  └──────────────┘  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Capabilities

### Clinical Workflow
- **Patient Registration**: Auto-generated BGD-NNNNN IDs, duplicate detection, disease-phase tracking
- **Encounter Management**: Baseline, follow-up, unscheduled visits with clinical findings
- **Prescription Engine**: Printable prescriptions (PDF), medication reconciliation, safety checks (renal dosing, prior intolerance, duplicate therapy, glycaemic monitoring)
- **Biopsy Pathology**: Local → Central → Adjudication review workflow with Oxford MEST-C (IgAN), ISN/RPS (LN), FSGS variant, and membranous staging
- **Lab Management**: Ordering → Resulting with auto-derivation of eGFR (CKD-EPI 2021)
- **Follow-up Scheduling**: Protocol-driven visit scheduling (±7-day windows, Tuesday GN clinic, capacity management)
- **Clinical Decision Support**: Rule engine (87 rules, 9 diseases) and clinical decision support profiles

### Research & Analytics
- **Outcome Engine**: Computed PatientOutcome (not hand-entered) — eGFR slope, sustained declines, doubling creatinine, ESKD, death, composite kidney endpoint, disease-specific proteinuria remission (KDIGO 2021/2025)
- **Survival Analysis**: Kaplan-Meier, log-rank test, Nelson-Aalen — all pure-Python, no R/scipy dependency
- **Cox Regression**: Multivariable Cox proportional-hazards (Newton-Raphson, Breslow ties)
- **Competing Risks**: Aalen-Johansen CIF (kidney events with death as competing risk)
- **Mixed Models**: Linear mixed-effects eGFR slope comparison (Laird-Ware EM algorithm)
- **Multiple Imputation**: MICE with predictive mean matching + Rubin's rules pooling
- **Biomarker Kinetics**: Anti-PLA2R seroconversion, complement recovery, anti-dsDNA normalization
- **Cohort Analysis**: Stratified by diabetes, diagnosis, drug exposure, study arm
- **Research Export**: CSV/XLSX/SPSS .sav with de-identified datasets and data dictionary

### Trial Platform
- **Embedded RCTs**: Study definitions (observational/quasi-experimental/RCT), arms, enrollment
- **Randomization**: Simple, permuted block, stratified permuted block (deterministic, seeded, auditable)
- **Eligibility Screening**: Automated screening against study criteria
- **Safety Monitoring**: Adverse event summaries, infection incidence by drug/diabetes, per-study SAE tabulation

### Governance
- **Audit Trail**: Per-field change history (who/when/old→new)
- **Consent Management**: Versioned, withdrawable consent (registry, biobank, genetic, imaging, trial)
- **RBAC**: 6 roles (data_manager, statistician, readonly, coordinator, investigator, pathologist)
- **Automatic Backups**: Timestamped SQLite snapshots, configurable retention

---

## Clinical Workflow State Machine

```
Patient enters registry
        │
        ▼
  SUSPECTED ──────► ADMISSION + BIOPSY
        │                  │
        │                  ▼
        │           BASELINE FORM
        │                  │
        │                  ▼
        │          BIOPSY REPORT
        │           (central review)
        │                  │
        ▼                  ▼
  REGISTERED ──────► ACTIVE DISEASE
        │                  │
        │         ┌────────┴────────┐
        │         │                 │
        │         ▼                 ▼
        │    REMISSION ────► POST_REMISSION
        │         │                 │
        │         │                 │
        │         └──── RELAPSE ◄───┘
        │                  │
        │                  ▼
        │             ACTIVE DISEASE
        │             (re-entry)
        │
        ▼
   OUTCOMES ENGINE (computed)
   • eGFR slope (LMM)
   • Proteinuria remission (KDIGO)
   • Composite kidney endpoint
   • Survival analysis (KM/Cox)
```

---

## Application Map (18 Active Apps)

| App | Purpose | Models |
|---|---|---|
| `patients` | Core patient registry | Patient |
| `encounters` | Clinical visits & events | ClinicalEncounter, Admission, RelapseEpisode, ClinicalEvent |
| `baseline` | Enrollment clinical snapshot | BaselineAssessment |
| `labs` | Lab ordering & results | LabTest, LabPanel, LabOrder, LabOrderItem, LabResult |
| `pathology` | Biopsy & pathology review | Biopsy, GNDiagnosis, IgANScore, LupusPathology, FSGSPathology, MembranousPathology, BiopsyImage, PathologyReview |
| `treatments` | Drug formulary & exposure | DrugMaster, TreatmentExposure |
| `prescriptions` | Printable prescriptions | Prescription, PrescriptionItem, AdviceTemplate |
| `analytics` | Outcomes & statistics | PatientOutcome |
| `safety` | Adverse events | AdverseEvent |
| `studies` | Embedded trials | Study, StudyArm, StudyEnrollment |
| `scheduling` | Visit scheduling | ScheduledVisit |
| `biomarkers` | Biomarker kinetics | BiomarkerKinetics |
| `audit` | Audit trail & consent | AuditLog, Consent |
| `users` | User profiles & invitations | UserProfile, Invitation |
| `clinical` | Clinical assessments (GDES) | ClinicalAssessment, VitalSign |
| `knowledge` | Guideline knowledge base | GuidelineSource, KnowledgeBaseEntry |
| `decision` | Clinical decision support | DecisionRequest, DecisionResult |
| `timeline` | Cross-domain event timeline | TimelineEvent |
| `clinic` | Guided workflow UI (no models) | — |
| `exports` | Research dataset export | — (service-only) |

---

## Key Design Principles

1. **Outcomes are computed, not entered**: The `PatientOutcome` model is derived from longitudinal labs, treatment exposures, and clinical events. It can be re-computed at any time via `compute_outcomes()`.

2. **Prescription drives exposure**: The medication reconciliation engine diffs the prescription against open `TreatmentExposure` episodes, maintaining a research-grade new-user cohort history with zero extra data entry.

3. **Central review workflow**: Every index biopsy gets LOCAL + CENTRAL reads with field-by-field concordance checking and adjudication for discordant cases.

4. **Disease-specific remission**: Proteinuria remission definitions are disease-specific (KDIGO 2021/2025), with sustained-achievement criteria producing true time-to-event endpoints.

5. **Pure-Python analytics**: All statistical methods (KM, Cox, competing risks, LMM, MICE) are implemented without R/scipy dependency, making them auditable and portable.

6. **OneDrive-safe desktop**: All mutable data lives under `BGDDR_DATA_DIR`, making the entire folder syncable via OneDrive with SQLite busy-timeout protection.

7. **Audit everything**: Every data change is tracked in `AuditLog` with per-field granularity. Prescriptions are immutable once finalized (SHA-256 content hash).

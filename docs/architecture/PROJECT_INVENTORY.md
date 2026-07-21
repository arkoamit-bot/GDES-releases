# BGDDR — Complete Project Inventory

## Root-Level Files

```
bgddr/
├── .gitignore
├── .initialized
├── .secret_key
├── README.md
├── requirements.txt
├── manage.py
├── Start-BGDDR.bat
├── setup_production.ps1
├── package.json
├── package-lock.json
├── tailwind.config.js
├── db.sqlite3
├── db-Dr-Wasim.sqlite3
├── migrate_to_postgres.py
├── inspect_db.py
├── find_dups.py
├── check_patient_221.py
├── test_pdf.py
├── cleanup_dups.sql
├── patient_issues.csv
├── DEPLOYMENT.md
├── DESKTOP_DEPLOYMENT.md
├── STATUS_REPORT.md
├── CODE_REVIEW.md
├── USER_MANUAL.md
├── USER_MANUAL.pdf
├── PATIENT_CLEANUP_REPORT.md
├── km_demo.svg
└── .Rhistory
```

---

## App Directory Structure

### patients/
```
patients/
├── __init__.py
├── admin.py
├── apps.py
├── choices.py              # Curated CRF code lists (~436 lines)
├── models.py               # Patient model (root model)
├── services.py             # delete_patient_cascade()
├── tests.py
├── urls.py
├── views.py
├── workflow.py             # DiseasePhase, RegistrationStatus, ClinicianResponse enums
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### encounters/
```
encounters/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # ClinicalEncounter, Admission, RelapseEpisode, ClinicalEvent
├── services/
│   ├── __init__.py
│   └── workflow.py         # Disease phase state machine (84 lines)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### baseline/
```
baseline/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # BaselineAssessment (OneToOne with Patient)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### labs/
```
labs/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # LabTest, LabPanel, LabOrder, LabOrderItem, LabResult
├── services/
│   ├── __init__.py
│   ├── egfr.py             # CKD-EPI 2021 creatinine equation
│   ├── ordering.py         # Lab order management
│   └── results.py          # Result recording with auto-derivation
├── management/
│   └── commands/
│       └── seed_labs.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### pathology/
```
pathology/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # Biopsy, GNDiagnosis, IgANScore, LupusPathology,
│                           # FSGSPathology, MembranousPathology, BiopsyImage,
│                           # PathologyReview
├── services/
│   ├── __init__.py
│   ├── review.py           # Central review workflow (104 lines)
│   └── agreement.py        # Inter-observer kappa
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### treatments/
```
treatments/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # DrugMaster, TreatmentExposure (171 lines)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### prescriptions/
```
prescriptions/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # Prescription, PrescriptionItem, AdviceTemplate
├── services/
│   ├── __init__.py
│   ├── finalize.py         # Prescription finalization + reconciliation trigger
│   ├── reconciliation.py   # Medication reconciliation engine (173 lines)
│   └── safety.py           # Safety checks (renal dosing, intolerance, duplicates)
├── static/
│   └── prescriptions/
│       └── fonts/          # NotoSansBengali-Regular.ttf (optional)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### analytics/
```
analytics/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # PatientOutcome (OneToOne with Patient, 127 lines)
├── services/
│   ├── __init__.py
│   ├── cohort.py           # Cohort analysis & grouping (299 lines)
│   ├── competing_risks.py  # Aalen-Johansen CIF (121 lines)
│   ├── cox.py              # Cox PH regression (233 lines)
│   ├── imputation.py       # MICE with PMM + Rubin's rules (79 lines)
│   ├── km_plot.py          # Kaplan-Meier plotting
│   ├── linalg.py           # Pure-Python linear algebra
│   ├── mixed_model.py      # LMM eGFR slope (144 lines)
│   ├── outcomes.py         # Outcome engine (299 lines)
│   ├── quality.py          # Data quality metrics
│   ├── remission.py        # Disease-specific remission definitions (92 lines)
│   ├── stats_utils.py      # Normal distribution utilities
│   └── survival.py         # KM, log-rank, Nelson-Aalen (184 lines)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### safety/
```
safety/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # AdverseEvent (110 lines)
├── services/
│   ├── __init__.py
│   └── summary.py          # AE summaries, infection incidence, per-study SAE
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### studies/
```
studies/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # Study, StudyArm, StudyEnrollment (135 lines)
├── services/
│   ├── __init__.py
│   ├── eligibility.py      # Eligibility screening
│   └── randomization.py    # Randomization engine (209 lines)
├── management/
│   └── commands/
│       └── seed_studies.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### scheduling/
```
scheduling/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # ScheduledVisit (65 lines)
├── services/
│   ├── __init__.py
│   ├── schedule.py         # Visit scheduling & capacity management (138 lines)
│   └── monitoring.py       # Immunosuppression monitoring
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### biomarkers/
```
biomarkers/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # BiomarkerKinetics (OneToOne with Patient, 62 lines)
├── services/
│   ├── __init__.py
│   ├── kinetics.py         # PLA2R kinetics, complement recovery
│   └── predictor.py        # Remission predictor
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### audit/
```
audit/
├── __init__.py
├── admin.py
├── apps.py
├── middleware.py           # AuditMiddleware (tracks request.user)
├── models.py               # AuditLog, Consent (109 lines)
├── services/
│   ├── __init__.py
│   └── consent.py          # Consent lifecycle (64 lines)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### users/
```
users/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # UserProfile, Invitation (108 lines)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_alter_invitation_role_alter_userprofile_role.py
```

### clinical/
```
clinical/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # ClinicalAssessment, VitalSign (35 lines)
├── serializers.py
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### knowledge/
```
knowledge/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # GuidelineSource, KnowledgeBaseEntry (49 lines)
├── serializers.py
├── services.py             # Rule engine (391 lines, 87 rules, 9 diseases)
├── management/
│   └── commands/
│       ├── seed_knowledge_base.py
│       └── activate_entries.py
├── tests.py
├── tests_api.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### decision/
```
decision/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # DecisionRequest, DecisionResult (31 lines)
├── serializers.py
├── services.py             # Clinical decision support (278 lines, 9 disease profiles)
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### timeline/
```
timeline/
├── __init__.py
├── admin.py
├── apps.py
├── models.py               # TimelineEvent (32 lines)
├── services.py             # Cross-domain event aggregation
├── tests.py
├── urls.py
├── views.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### clinic/
```
clinic/
├── __init__.py
├── apps.py
├── views.py                # 38 views (workflow UI)
├── urls.py                 # 46 URL patterns
├── templates/
│   └── clinic/
│       ├── patients.html
│       ├── patient_detail.html
│       ├── worklist.html
│       ├── prescriptions.html
│       ├── analytics.html
│       ├── studies.html
│       ├── safety.html
│       ├── pathology.html
│       ├── biomarkers.html
│       ├── export.html
│       ├── cox_results.html
│       ├── egfr_slope_results.html
│       └── cif_results.html
└── static/
    └── clinic/
        └── js/
            └── (chart library files)
```

### exports/
```
exports/
├── __init__.py
├── apps.py
├── services/
│   ├── __init__.py
│   ├── dataset.py          # Research dataset builder (232 lines)
│   ├── dictionary.py       # Data dictionary
│   └── writers.py          # CSV/XLSX/SPSS writers
├── management/
│   └── commands/
│       └── export_dataset.py
├── tests.py
├── urls.py
└── views.py
```

### api/
```
api/
├── __init__.py
├── apps.py
├── urls.py                 # DRF router (18 viewsets)
├── views.py                # ViewSets for all major models
├── serializers.py
└── tests.py
```

### bgddr/ (project config)
```
bgddr/
├── __init__.py
├── settings.py             # Main settings (370 lines)
├── settings_prod.py        # Production settings (enforces DEBUG=False)
├── settings_desktop.py     # Desktop settings
├── settings_deploy.py      # Deployment settings
├── urls.py                 # Root URL configuration
├── views.py                # Dashboard view (130 lines)
├── wsgi.py
├── admin_backup.py         # Backup & Restore console
└── backup.py               # Automatic backup engine
```

### desktop/
```
desktop/
└── launcher.py             # Windows desktop launcher (waitress)
```

### biobank/ (DISABLED)
```
biobank/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── services/
│   ├── __init__.py
│   └── storage.py
├── tests.py
├── urls.py
└── views.py
```

### Templates (project-level)
```
templates/
├── admin/
│   └── (admin template overrides)
├── base.html
├── dashboard.html
└── (other shared templates)
```

### Static Files
```
static/
├── css/
│   └── admin_sky.css       # Jazzmin admin theme override
├── js/
│   └── (application JS)
└── (other static assets)

static_src/                  # Tailwind CSS source
staticfiles/                 # Collected static files (output)
```

---

## Management Commands

| Command | App | Purpose |
|---|---|---|
| `seed_labs` | labs | Populate the LabTest catalog |
| `seed_studies` | studies | Populate Study definitions |
| `seed_knowledge_base` | knowledge | Load clinical knowledge rules |
| `activate_entries` | knowledge | Activate knowledge base entries |
| `export_dataset` | exports | CLI research dataset export |

---

## File Counts

| Category | Count |
|---|---|
| Python files (app code) | ~120 |
| Template files | ~15 |
| Static files | ~10 |
| Migration files | ~20 |
| Configuration files | ~8 |
| Documentation files | ~6 |
| **Total source files** | **~180** |

# BGDDR — Inter-App Dependency Graph

## Dependency Matrix

```
                        patients encounters baseline labs pathology treatments prescriptions analytics safety studies scheduling biomarkers audit users clinical knowledge decision timeline
patients                   -                                                           
encounters                 ●                                                           
baseline                   ●                                                           
labs                       ●        ●                                                   
pathology                  ●                                                           
treatments                 ●                                                           
prescriptions                       ●                       ●                           
analytics                  ●        ●        ●      ●       ●        ●                  
safety                     ●        ●                       ●                           
studies                    ●                                                           
scheduling                 ●                                                           
biomarkers                 ●                ●                                           
audit                      ●                                                           
users                                                                                  
clinical                   ●        ●                                                   
knowledge                  ●                ●      ●       ●                           
decision                   ●        ●                                                   
timeline                   ●        ●              ●       ●              ●      ●      
```

**Legend**: ● = depends on (imports models or services from)

---

## Detailed Dependencies

### patients (ROOT — no app dependencies)
```
patients/
├── models.py         → (none — root model)
├── workflow.py       → (none — shared enums)
├── choices.py        → (none — curated code lists)
├── services.py       → prescriptions.LabOrder, prescriptions.Prescription (lazy imports)
└── admin.py          → patients.models
```

### encounters
```
encounters/
├── models.py         → patients.models.Patient
│                       patients.workflow (DiseasePhase, ClinicianResponse, RelapseType)
├── services/workflow.py → patients.workflow
│                          encounters.models (ClinicalEvent, RelapseEpisode)
└── admin.py          → encounters.models
```

### baseline
```
baseline/
├── models.py         → patients.models.Patient
│                       patients.choices
└── admin.py          → baseline.models
```

### labs
```
labs/
├── models.py         → encounters.models.ClinicalEncounter
│                       patients.models.Patient
├── services/egfr.py  → (none — pure math)
├── services/ordering.py → labs.models
├── services/results.py  → labs.models, labs.services.egfr
└── admin.py          → labs.models
```

### pathology
```
pathology/
├── models.py         → patients.models.Patient
│                       patients.choices
│                       patients.workflow
├── services/review.py  → pathology.models
├── services/agreement.py → (none — pure math)
└── admin.py          → pathology.models
```

### treatments
```
treatments/
├── models.py         → patients.models.Patient
└── admin.py          → treatments.models
```

### prescriptions
```
prescriptions/
├── models.py         → encounters.models.ClinicalEncounter
│                       treatments.models.DrugMaster
├── services/safety.py    → treatments.models (DrugClass, StopReason, TreatmentExposure)
├── services/reconciliation.py → treatments.models (TreatmentExposure, StopReason)
├── services/finalize.py  → prescriptions.services.reconciliation
│                           prescriptions.services.safety
└── admin.py          → prescriptions.models
```

### analytics
```
analytics/
├── models.py         → patients.models.Patient
├── services/outcomes.py  → encounters.models, labs.models, patients.models
│                           analytics.models, analytics.services.remission
├── services/remission.py → (none — pure predicates)
├── services/survival.py  → (none — pure math)
├── services/cox.py       → analytics.services.stats_utils
├── services/competing_risks.py → (none — pure math)
├── services/mixed_model.py → analytics.services.linalg
├── services/imputation.py  → analytics.services.linalg
├── services/linalg.py      → (none — pure math)
├── services/stats_utils.py → (none — pure math)
├── services/cohort.py      → treatments.models, patients.models
│                             analytics.models, analytics.services.survival
│                             analytics.services.cox, analytics.services.competing_risks
│                             analytics.services.mixed_model
├── services/km_plot.py     → analytics.services.survival
├── services/quality.py     → analytics.models
└── admin.py          → analytics.models
```

### safety
```
safety/
├── models.py         → patients.models.Patient
│                       treatments.models.DrugMaster
├── services/summary.py → analytics.models, analytics.services.cohort
│                         safety.models
└── admin.py          → safety.models
```

### studies
```
studies/
├── models.py         → patients.models.Patient
├── services/randomization.py → audit.models, audit.services.consent
│                                studies.models, studies.services.eligibility
├── services/eligibility.py → patients.models, studies.models
└── admin.py          → studies.models
```

### scheduling
```
scheduling/
├── models.py         → patients.models.Patient
├── services/schedule.py → scheduling.models
├── services/monitoring.py → scheduling.models
└── admin.py          → scheduling.models
```

### biomarkers
```
biomarkers/
├── models.py         → patients.models.Patient
├── services/kinetics.py → biomarkers.models, labs.models
├── services/predictor.py → biomarkers.models
└── admin.py          → biomarkers.models
```

### audit
```
audit/
├── models.py         → patients.models.Patient
├── middleware.py      → (Django middleware — tracks request.user)
├── services/consent.py → audit.models
└── admin.py          → audit.models
```

### users
```
users/
├── models.py         → (Django auth.User, auth.Group only)
└── admin.py          → users.models
```

### clinical
```
clinical/
├── models.py         → patients.models.Patient
│                       encounters.models.ClinicalEncounter
├── serializers.py    → clinical.models
└── admin.py          → clinical.models
```

### knowledge
```
knowledge/
├── models.py         → (none — standalone)
├── services.py       → patients.models, patients.workflow
│                       labs.models, pathology.models
│                       knowledge.models
├── serializers.py    → knowledge.models
└── admin.py          → knowledge.models
```

### decision
```
decision/
├── models.py         → patients.models.Patient
│                       encounters.models.ClinicalEncounter
├── services.py       → (none — pure scoring with DISEASE_PROFILES)
├── serializers.py    → decision.models
└── admin.py          → decision.models
```

### timeline
```
timeline/
├── models.py         → patients.models.Patient
├── services.py       → patients.models, encounters.models
│                       clinical.models, labs.models
│                       pathology.models, decision.models
└── admin.py          → timeline.models
```

### clinic (no models)
```
clinic/
├── views.py          → ALL app models (workflow UI)
└── urls.py           → clinic.views
```

### exports (no models)
```
exports/
├── services/dataset.py   → ALL app models (denormalized dataset)
├── services/writers.py   → (none — file I/O)
├── services/dictionary.py → (none — metadata)
└── views.py              → exports.services
```

### api (no models)
```
api/
├── views.py          → ALL app models (DRF ViewSets)
├── serializers.py    → ALL app models
└── urls.py           → api.views
```

---

## Circular Dependency Check

**No circular dependencies exist.** The dependency graph is a DAG:

```
patients (root)
    │
    ├── encounters
    │       │
    │       ├── labs
    │       │       │
    │       │       └── analytics (imports labs for eGFR series)
    │       │
    │       ├── prescriptions
    │       │       │
    │       │       └── treatments (DrugMaster)
    │       │
    │       └── clinical
    │
    ├── pathology
    │
    ├── baseline
    │
    ├── safety
    │       │
    │       └── analytics (imports for cohort splitting)
    │
    ├── studies
    │       │
    │       └── audit (consent check)
    │
    ├── scheduling
    │
    ├── biomarkers
    │
    ├── audit
    │
    ├── users
    │
    ├── knowledge (imports patients, labs, pathology for feature extraction)
    │
    ├── decision (imports patients, encounters)
    │
    ├── timeline (imports patients, encounters, clinical, labs, pathology, decision)
    │
    ├── clinic (imports ALL)
    │
    ├── exports (imports ALL)
    │
    └── api (imports ALL)
```

---

## Import Order for Fresh Setup

1. `patients` (no dependencies)
2. `encounters` (depends on patients)
3. `baseline` (depends on patients)
4. `treatments` (depends on patients)
5. `labs` (depends on patients, encounters)
6. `pathology` (depends on patients)
7. `prescriptions` (depends on encounters, treatments)
8. `analytics` (depends on patients, encounters, labs, pathology, treatments)
9. `safety` (depends on patients, treatments)
10. `studies` (depends on patients, audit)
11. `scheduling` (depends on patients)
12. `biomarkers` (depends on patients, labs)
13. `audit` (depends on patients)
14. `users` (no app dependencies)
15. `clinical` (depends on patients, encounters)
16. `knowledge` (depends on patients, labs, pathology)
17. `decision` (depends on patients, encounters)
18. `timeline` (depends on patients, encounters, clinical, labs, pathology, decision)
19. `clinic` (imports ALL)
20. `exports` (imports ALL)
21. `api` (imports ALL)

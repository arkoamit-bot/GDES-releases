# BGDDR — API Inventory

## REST API Overview

- **Base URL**: `/api/v1/`
- **Authentication**: Token + Session (DRF defaults)
- **Permissions**: `IsAuthenticated` + `DjangoModelPermissions`
- **Pagination**: `PageNumberPagination`, PAGE_SIZE=50
- **Format**: JSON (default)

---

## DRF ViewSets (Router-Registered)

| # | ViewSet | Model | Base Path | Actions |
|---|---|---|---|---|
| 1 | `PatientViewSet` | Patient | `/api/v1/patients/` | list, create, retrieve, update, partial_update, destroy |
| 2 | `ClinicalEncounterViewSet` | ClinicalEncounter | `/api/v1/encounters/` | list, create, retrieve, update, partial_update, destroy |
| 3 | `ClinicalEventViewSet` | ClinicalEvent | `/api/v1/events/` | list, create, retrieve, update, partial_update, destroy |
| 4 | `LabResultViewSet` | LabResult | `/api/v1/lab-results/` | list, create, retrieve, update, partial_update, destroy |
| 5 | `TreatmentExposureViewSet` | TreatmentExposure | `/api/v1/treatment-exposures/` | list, create, retrieve, update, partial_update, destroy |
| 6 | `BiopsyViewSet` | Biopsy | `/api/v1/biopsies/` | list, create, retrieve, update, partial_update, destroy |
| 7 | `PathologyReviewViewSet` | PathologyReview | `/api/v1/pathology-reviews/` | list, create, retrieve, update, partial_update, destroy |
| 8 | `AdverseEventViewSet` | AdverseEvent | `/api/v1/adverse-events/` | list, create, retrieve, update, partial_update, destroy |
| 9 | `ScheduledVisitViewSet` | ScheduledVisit | `/api/v1/scheduled-visits/` | list, create, retrieve, update, partial_update, destroy |
| 10 | `PrescriptionViewSet` | Prescription | `/api/v1/prescriptions/` | list, create, retrieve, update, partial_update, destroy |
| 11 | `PatientOutcomeViewSet` | PatientOutcome | `/api/v1/outcomes/` | list, retrieve (read-only) |
| 12 | `BiomarkerKineticsViewSet` | BiomarkerKinetics | `/api/v1/biomarkers/` | list, retrieve (read-only) |
| 13 | `DrugMasterViewSet` | DrugMaster | `/api/v1/drugs/` | list, create, retrieve, update, partial_update, destroy |

### Standard CRUD Endpoints (per ViewSet)

For each ViewSet at `<base>/`:

| Method | Path | Description | Permissions |
|---|---|---|---|
| GET | `/` | List (paginated) | VIEW permission |
| POST | `/` | Create | ADD permission |
| GET | `/{id}/` | Retrieve | VIEW permission |
| PUT | `/{id}/` | Full update | CHANGE permission |
| PATCH | `/{id}/` | Partial update | CHANGE permission |
| DELETE | `/{id}/` | Delete | DELETE permission |

---

## Custom API Actions

### Patient Actions

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/patients/{id}/outcome/` | Compute/retrieve patient outcome |
| POST | `/api/v1/patients/{id}/outcome/recompute/` | Force recompute outcome |

### Prescription Actions

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/prescriptions/{id}/finalize/` | Finalize (freeze + reconcile) |
| GET | `/api/v1/prescriptions/{id}/safety-checks/` | Run safety checks |
| GET | `/api/v1/prescriptions/{id}/reconciliation-preview/` | Preview reconciliation plan |

### Study Actions

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/studies/{id}/enroll/` | Screen + enroll patient |
| GET | `/api/v1/studies/{id}/dashboard/` | CONSORT-style counts |
| POST | `/api/v1/studies/{id}/enrollments/{eid}/withdraw/` | Withdraw enrollment |

---

## Authentication Endpoint

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/token/` | Obtain auth token |

**Request**:
```json
{"username": "user", "password": "pass"}
```

**Response**:
```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

---

## Template-Based Clinic Workflow URLs

Base: `/clinic/` (from `clinic/urls.py`)

### Patient Workflow

| # | Path | View | Name | Description |
|---|---|---|---|---|
| 1 | `/patients/` | `patients_list` | `patients` | Patient list |
| 2 | `/patients/quicksearch/` | `quicksearch` | `quicksearch` | AJAX quick search |
| 3 | `/patients/dup-check/` | `patient_dupcheck` | `patient_dupcheck` | Duplicate check |
| 4 | `/patients/add/` | `patient_create` | `patient_create` | New patient form |
| 5 | `/patients/<int:pk>/` | `patient_detail` | `patient_detail` | Patient detail |
| 6 | `/patients/<int:pk>/edit/` | `patient_edit` | `patient_edit` | Edit patient |
| 7 | `/patients/<int:pk>/delete/` | `patient_delete` | `patient_delete` | Delete patient |
| 8 | `/patients/<int:pk>/baseline/` | `baseline_edit` | `baseline` | Baseline assessment |
| 9 | `/patients/<int:pk>/followup/` | `followup_create` | `followup` | New follow-up visit |
| 10 | `/patients/<int:pk>/prescription/` | `prescription_create` | `prescription` | New prescription |
| 11 | `/patients/<int:pk>/adverse-event/` | `adverse_event_create` | `adverse_event` | Report AE |
| 12 | `/patients/<int:pk>/register/` | `patient_register` | `register` | Register in GN clinic |
| 13 | `/patients/<int:pk>/relapse/` | `relapse_create` | `relapse` | Document relapse |
| 14 | `/patients/<int:pk>/admission/` | `admission_create` | `admission` | Record admission |
| 15 | `/patients/<int:pk>/biopsy/` | `biopsy_create` | `biopsy` | Record biopsy |
| 16 | `/patients/<int:pk>/enroll/` | `study_enroll` | `study_enroll` | Enroll in study |
| 17 | `/patients/<int:pk>/consent/` | `consent_manage` | `consent` | Manage consent |
| 18 | `/patients/<int:pk>/treatment/` | `treatment_add` | `treatment` | Add treatment |
| 19 | `/patients/<int:pk>/lab-order/` | `lab_order_create` | `lab_order` | Create lab order |
| 20 | `/patients/<int:pk>/lab-results/` | `lab_results_entry` | `lab_results` | Enter lab results |
| 21 | `/patients/<int:pk>/outcome/recompute/` | `outcome_recompute` | `outcome_recompute` | Recompute outcome |

### Section Landing Pages

| # | Path | View | Name |
|---|---|---|---|
| 22 | `/clinic/worklist/` | `worklist_page` | `worklist` |
| 23 | `/clinic/quality/` | `quality_page` | `quality` |
| 24 | `/clinic/prescriptions/` | `prescriptions_list` | `prescriptions` |
| 25 | `/clinic/analytics/` | `analytics_page` | `analytics` |
| 26 | `/clinic/studies/` | `studies_page` | `studies` |
| 27 | `/clinic/safety/` | `safety_page` | `safety` |
| 28 | `/clinic/pathology/` | `pathology_page` | `pathology` |
| 29 | `/clinic/biomarkers/` | `biomarkers_page` | `biomarkers` |
| 30 | `/clinic/export/` | `export_page` | `export` |

### Analytics Results Pages

| # | Path | View | Name |
|---|---|---|---|
| 31 | `/clinic/analytics/cox/` | `cox_results` | `cox_results` |
| 32 | `/clinic/analytics/egfr-slope/` | `egfr_slope_results` | `egfr_slope_results` |
| 33 | `/clinic/analytics/cif/` | `cif_results` | `cif_results` |

---

## App-Specific JSON/API Endpoints

### Analytics (`/analytics/`)

| Method | Path | Description |
|---|---|---|
| GET | `/analytics/survival/?endpoint=...&group_by=...` | KM survival analysis |
| GET | `/analytics/cox/?endpoint=...&covariates=...` | Cox regression |
| GET | `/analytics/egfr-slope/?group_by=...` | eGFR slope comparison |
| GET | `/analytics/competing-risks/?group_by=...` | CIF analysis |
| GET | `/analytics/cohort-summary/?group_by=...` | Baseline + outcome summary |

### Safety (`/safety/`)

| Method | Path | Description |
|---|---|---|
| GET | `/safety/summary/?group_by=...` | AE summary |
| GET | `/safety/infection-incidence/?group_by=...` | Infection incidence density |
| GET | `/safety/study-safety/{study_id}/` | Per-arm SAE tabulation |

### Scheduling (`/scheduling/`)

| Method | Path | Description |
|---|---|---|
| GET | `/scheduling/due/` | Due visits |
| GET | `/scheduling/overdue/` | Overdue visits |
| GET | `/scheduling/roster/?date=...` | Clinic roster |
| POST | `/scheduling/generate/{patient_id}/` | Generate schedule |
| POST | `/scheduling/complete/{visit_id}/` | Complete a visit |

### Pathology (`/pathology/`)

| Method | Path | Description |
|---|---|---|
| POST | `/pathology/submit-review/` | Submit pathology review |
| GET | `/pathology/concordance/{biopsy_id}/` | Check concordance |
| POST | `/pathology/adjudicate/{biopsy_id}/` | Adjudicate discordant |

### Biomarkers (`/biomarkers/`)

| Method | Path | Description |
|---|---|---|
| GET | `/biomarkers/kinetics/{patient_id}/` | Get PLA2R kinetics |
| POST | `/biomarkers/compute/{patient_id}/` | Compute biomarker kinetics |

### Prescriptions (`/prescriptions/`)

| Method | Path | Description |
|---|---|---|
| GET | `/prescriptions/{id}/preview/` | Preview prescription |
| POST | `/prescriptions/{id}/print/` | Finalize + generate PDF |
| GET | `/prescriptions/{id}/safety/` | Safety check results |
| GET | `/prescriptions/{id}/reconciliation/` | Reconciliation preview |

### Exports (`/exports/`)

| Method | Path | Description |
|---|---|---|
| GET | `/exports/research-dataset/?fmt=csv` | CSV export |
| GET | `/exports/research-dataset/?fmt=xlsx` | Excel export |
| GET | `/exports/research-dataset/?fmt=sav` | SPSS export |
| GET | `/exports/data-dictionary/` | Data dictionary |

### GDES Clinical Decision Support (under `/api/v1/`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/clinical/assess/` | Clinical assessment |
| POST | `/api/v1/knowledge/evaluate/` | Evaluate KB rules |
| POST | `/api/v1/decision/evaluate/` | CDS evaluation |
| GET | `/api/v1/timeline/{patient_id}/` | Patient timeline |

---

## Admin Backup Console

| # | Path | Description |
|---|---|---|
| 1 | `/admin/backups/` | Backup & Restore console (superuser) |
| 2 | `/admin/backups/create/` | Create backup |
| 3 | `/admin/backups/restore/{filename}/` | Restore backup |
| 4 | `/admin/backups/download/{filename}/` | Download backup file |

---

## URL Count Summary

| Category | Count |
|---|---|
| DRF API (router) | 78 (13 viewsets × 6 endpoints) |
| DRF custom actions | ~10 |
| Clinic workflow views | 33 |
| Analytics JSON endpoints | ~5 |
| Safety JSON endpoints | ~3 |
| Scheduling JSON endpoints | ~5 |
| Pathology JSON endpoints | ~3 |
| Biomarkers JSON endpoints | ~2 |
| Prescriptions workflow | ~4 |
| Exports | ~4 |
| GDES endpoints | ~4 |
| Admin backup | ~4 |
| Authentication | 1 |
| **Total** | **~156+** |

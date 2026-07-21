# BGDDR — Complete URL Routing Map

## Root URL Configuration (`bgddr/urls.py`)

```python
urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("", include("clinic.urls")),
    path("", include("users.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("prescriptions/", include("prescriptions.urls")),
    path("analytics/", include("analytics.urls")),
    path("studies/", include("studies.urls")),
    path("safety/", include("safety.urls")),
    path("scheduling/", include("scheduling.urls")),
    path("pathology/", include("pathology.urls")),
    path("biomarkers/", include("biomarkers.urls")),
    path("exports/", include("exports.urls")),
    path("api/v1/", include("clinical.urls")),
    path("api/v1/", include("knowledge.urls")),
    path("api/v1/", include("decision.urls")),
    path("api/v1/", include("timeline.urls")),
]
```

---

## Complete URL Patterns

### Dashboard
| Pattern | View | Name | Permissions |
|---|---|---|---|
| `^$` | `bgddr.views.dashboard` | `dashboard` | `@login_required` |

### DRF API (`api/v1/`)
| Pattern | View | Name | Permissions |
|---|---|---|---|
| `api/v1/auth/token/` | `obtain_auth_token` | `token` | AllowAny |
| `api/v1/patients/` | `PatientViewSet` | `patient-list` | DjangoModelPermissions |
| `api/v1/patients/{pk}/` | `PatientViewSet` | `patient-detail` | DjangoModelPermissions |
| `api/v1/encounters/` | `ClinicalEncounterViewSet` | `clinicalencounter-list` | DjangoModelPermissions |
| `api/v1/encounters/{pk}/` | `ClinicalEncounterViewSet` | `clinicalencounter-detail` | DjangoModelPermissions |
| `api/v1/events/` | `ClinicalEventViewSet` | `clinicalevent-list` | DjangoModelPermissions |
| `api/v1/events/{pk}/` | `ClinicalEventViewSet` | `clinicalevent-detail` | DjangoModelPermissions |
| `api/v1/lab-results/` | `LabResultViewSet` | `labresult-list` | DjangoModelPermissions |
| `api/v1/lab-results/{pk}/` | `LabResultViewSet` | `labresult-detail` | DjangoModelPermissions |
| `api/v1/treatment-exposures/` | `TreatmentExposureViewSet` | `treatmentexposure-list` | DjangoModelPermissions |
| `api/v1/treatment-exposures/{pk}/` | `TreatmentExposureViewSet` | `treatmentexposure-detail` | DjangoModelPermissions |
| `api/v1/biopsies/` | `BiopsyViewSet` | `biopsy-list` | DjangoModelPermissions |
| `api/v1/biopsies/{pk}/` | `BiopsyViewSet` | `biopsy-detail` | DjangoModelPermissions |
| `api/v1/pathology-reviews/` | `PathologyReviewViewSet` | `pathologyreview-list` | DjangoModelPermissions |
| `api/v1/pathology-reviews/{pk}/` | `PathologyReviewViewSet` | `pathologyreview-detail` | DjangoModelPermissions |
| `api/v1/adverse-events/` | `AdverseEventViewSet` | `adverseevent-list` | DjangoModelPermissions |
| `api/v1/adverse-events/{pk}/` | `AdverseEventViewSet` | `adverseevent-detail` | DjangoModelPermissions |
| `api/v1/scheduled-visits/` | `ScheduledVisitViewSet` | `scheduledvisit-list` | DjangoModelPermissions |
| `api/v1/scheduled-visits/{pk}/` | `ScheduledVisitViewSet` | `scheduledvisit-detail` | DjangoModelPermissions |
| `api/v1/prescriptions/` | `PrescriptionViewSet` | `prescription-list` | DjangoModelPermissions |
| `api/v1/prescriptions/{pk}/` | `PrescriptionViewSet` | `prescription-detail` | DjangoModelPermissions |
| `api/v1/outcomes/` | `PatientOutcomeViewSet` | `patientoutcome-list` | DjangoModelPermissions |
| `api/v1/outcomes/{pk}/` | `PatientOutcomeViewSet` | `patientoutcome-detail` | DjangoModelPermissions |
| `api/v1/biomarkers/` | `BiomarkerKineticsViewSet` | `biomarkerkinetics-list` | DjangoModelPermissions |
| `api/v1/biomarkers/{pk}/` | `BiomarkerKineticsViewSet` | `biomarkerkinetics-detail` | DjangoModelPermissions |
| `api/v1/drugs/` | `DrugMasterViewSet` | `drugmaster-list` | DjangoModelPermissions |
| `api/v1/drugs/{pk}/` | `DrugMasterViewSet` | `drugmaster-detail` | DjangoModelPermissions |

### Clinic Workflow (`clinic/urls.py`)
| Pattern | View | Name | Permissions |
|---|---|---|---|
| `patients/` | `patients_list` | `patients` | `@login_required` |
| `patients/quicksearch/` | `quicksearch` | `quicksearch` | `@login_required` |
| `patients/dup-check/` | `patient_dupcheck` | `patient_dupcheck` | `@login_required` |
| `patients/add/` | `patient_create` | `patient_create` | `@login_required` |
| `patients/{pk}/` | `patient_detail` | `patient_detail` | `@login_required` |
| `patients/{pk}/edit/` | `patient_edit` | `patient_edit` | `@login_required` |
| `patients/{pk}/delete/` | `patient_delete` | `patient_delete` | `@login_required` |
| `patients/{pk}/baseline/` | `baseline_edit` | `baseline` | `@login_required` |
| `patients/{pk}/followup/` | `followup_create` | `followup` | `@login_required` |
| `patients/{pk}/prescription/` | `prescription_create` | `prescription` | `@login_required` |
| `patients/{pk}/adverse-event/` | `adverse_event_create` | `adverse_event` | `@login_required` |
| `patients/{pk}/register/` | `patient_register` | `register` | `@login_required` |
| `patients/{pk}/relapse/` | `relapse_create` | `relapse` | `@login_required` |
| `patients/{pk}/admission/` | `admission_create` | `admission` | `@login_required` |
| `patients/{pk}/biopsy/` | `biopsy_create` | `biopsy` | `@login_required` |
| `patients/{pk}/enroll/` | `study_enroll` | `study_enroll` | `@login_required` |
| `patients/{pk}/consent/` | `consent_manage` | `consent` | `@login_required` |
| `patients/{pk}/treatment/` | `treatment_add` | `treatment` | `@login_required` |
| `patients/{pk}/lab-order/` | `lab_order_create` | `lab_order` | `@login_required` |
| `patients/{pk}/lab-results/` | `lab_results_entry` | `lab_results` | `@login_required` |
| `patients/{pk}/outcome/recompute/` | `outcome_recompute` | `outcome_recompute` | `@login_required` |
| `clinic/worklist/` | `worklist_page` | `worklist` | `@login_required` |
| `clinic/quality/` | `quality_page` | `quality` | `@login_required` |
| `clinic/prescriptions/` | `prescriptions_list` | `prescriptions` | `@login_required` |
| `clinic/analytics/` | `analytics_page` | `analytics` | `@login_required` |
| `clinic/studies/` | `studies_page` | `studies` | `@login_required` |
| `clinic/safety/` | `safety_page` | `safety` | `@login_required` |
| `clinic/pathology/` | `pathology_page` | `pathology` | `@login_required` |
| `clinic/biomarkers/` | `biomarkers_page` | `biomarkers` | `@login_required` |
| `clinic/export/` | `export_page` | `export` | `@login_required` |
| `clinic/analytics/cox/` | `cox_results` | `cox_results` | `@login_required` |
| `clinic/analytics/egfr-slope/` | `egfr_slope_results` | `egfr_slope_results` | `@login_required` |
| `clinic/analytics/cif/` | `cif_results` | `cif_results` | `@login_required` |

### App-Specific URL Patterns

#### Prescriptions (`prescriptions/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `prescriptions/{pk}/preview/` | `prescription_preview` | `prescription_preview` |
| `prescriptions/{pk}/print/` | `prescription_print` | `prescription_print` |
| `prescriptions/{pk}/safety/` | `prescription_safety` | `prescription_safety` |
| `prescriptions/{pk}/reconciliation/` | `prescription_reconciliation` | `prescription_reconciliation` |

#### Analytics (`analytics/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `analytics/survival/` | `survival_analysis` | `survival_analysis` |
| `analytics/cox/` | `cox_analysis` | `cox_analysis` |
| `analytics/egfr-slope/` | `egfr_slope_analysis` | `egfr_slope_analysis` |
| `analytics/competing-risks/` | `competing_risks_analysis` | `competing_risks_analysis` |
| `analytics/cohort-summary/` | `cohort_summary` | `cohort_summary` |

#### Studies (`studies/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `studies/{pk}/dashboard/` | `study_dashboard` | `study_dashboard` |
| `studies/{pk}/enroll/` | `study_enroll` | `study_enroll` |
| `studies/{pk}/enrollments/{eid}/withdraw/` | `enrollment_withdraw` | `enrollment_withdraw` |

#### Safety (`safety/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `safety/summary/` | `safety_summary` | `safety_summary` |
| `safety/infection-incidence/` | `infection_incidence` | `infection_incidence` |
| `safety/study-safety/{pk}/` | `study_safety` | `study_safety` |

#### Scheduling (`scheduling/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `scheduling/due/` | `due_visits` | `due_visits` |
| `scheduling/overdue/` | `overdue_visits` | `overdue_visits` |
| `scheduling/roster/` | `clinic_roster` | `clinic_roster` |
| `scheduling/generate/{pk}/` | `generate_schedule` | `generate_schedule` |
| `scheduling/complete/{pk}/` | `complete_visit` | `complete_visit` |

#### Pathology (`pathology/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `pathology/submit-review/` | `submit_review` | `submit_review` |
| `pathology/concordance/{pk}/` | `concordance` | `concordance` |
| `pathology/adjudicate/{pk}/` | `adjudicate` | `adjudicate` |

#### Biomarkers (`biomarkers/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `biomarkers/kinetics/{pk}/` | `biomarker_kinetics` | `biomarker_kinetics` |
| `biomarkers/compute/{pk}/` | `compute_biomarkers` | `compute_biomarkers` |

#### Exports (`exports/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `exports/research-dataset/` | `research_dataset` | `research_dataset` |
| `exports/data-dictionary/` | `data_dictionary` | `data_dictionary` |

#### GDES Endpoints (under `api/v1/`)
| Pattern | View | Name |
|---|---|---|
| `api/v1/clinical/assess/` | `clinical_assess` | `clinical_assess` |
| `api/v1/knowledge/evaluate/` | `knowledge_evaluate` | `knowledge_evaluate` |
| `api/v1/decision/evaluate/` | `decision_evaluate` | `decision_evaluate` |
| `api/v1/timeline/{pk}/` | `patient_timeline` | `patient_timeline` |

---

## URL Count by Category

| Category | Count |
|---|---|
| Root dashboard | 1 |
| DRF router (CRUD) | 78 |
| DRF custom actions | ~10 |
| Clinic workflow | 33 |
| App-specific JSON | ~40 |
| Admin | (Django admin built-in) |
| **Total unique patterns** | **~162** |

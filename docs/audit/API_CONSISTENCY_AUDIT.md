# API Consistency Audit

## Endpoint Inventory

### `/api/v1/` Endpoints (Consistent)

| Prefix | ViewSet | Methods | Custom Actions |
|---|---|---|---|
| `/api/v1/auth/token/` | obtain_auth_token | POST | — |
| `/api/v1/sites/` | SiteViewSet | CRUD | — |
| `/api/v1/user-site-roles/` | UserSiteRoleViewSet | CRUD | — |
| `/api/v1/patients/` | PatientViewSet | CRUD | — |
| `/api/v1/encounters/` | ClinicalEncounterViewSet | CRUD | — |
| `/api/v1/events/` | ClinicalEventViewSet | CRUD | — |
| `/api/v1/lab-results/` | LabResultViewSet | CRUD | — |
| `/api/v1/treatment-exposures/` | TreatmentExposureViewSet | CRUD | — |
| `/api/v1/biopsies/` | BiopsyViewSet | CRUD | — |
| `/api/v1/pathology-reviews/` | PathologyReviewViewSet | CRUD | — |
| `/api/v1/adverse-events/` | AdverseEventViewSet | CRUD | — |
| `/api/v1/scheduled-visits/` | ScheduledVisitViewSet | CRUD | — |
| `/api/v1/prescriptions/` | PrescriptionViewSet | Read-only | — |
| `/api/v1/outcomes/` | PatientOutcomeViewSet | Read-only | — |
| `/api/v1/biomarkers/` | BiomarkerKineticsViewSet | Read-only | — |
| `/api/v1/drugs/` | DrugMasterViewSet | CRUD | — |

Source: `api/urls.py`

### GDES Endpoints (`/api/v1/` but separate viewset registrations)

| Prefix | ViewSet | Custom Actions | Source |
|---|---|---|---|
| `/api/v1/guideline-sources/` | GuidelineSourceViewSet | — | `knowledge/urls.py` |
| `/api/v1/knowledge-base/` | KnowledgeBaseEntryViewSet | — | `knowledge/urls.py` |
| `/api/v1/rule-templates/` | RuleTemplateViewSet | — | `knowledge/urls.py` |
| `/api/v1/rule-reviews/` | RuleReviewViewSet | — | `knowledge/urls.py` |
| `/api/v1/rule-test-results/` | RuleTestResultViewSet | — | `knowledge/urls.py` |
| `/api/v1/guideline-documents/` | GuidelineDocumentViewSet | — | `knowledge/urls.py` |
| `/api/v1/evidence-entries/` | EvidenceEntryViewSet | — | `knowledge/urls.py` |
| `/api/v1/decisions/` | DecisionViewSet | evaluate, calculators | `decision/urls.py` |
| `/api/v1/results/` | DecisionResultViewSet | override | `decision/urls.py` |
| `/api/v1/profiles/` | ClinicalProfileViewSet | by_patient, reason, reason_all, explain, recent, with_gaps | `clinical_reasoning/urls.py` |
| `/api/v1/insights/` | ClinicalInsightViewSet | by_patient, active_alerts, dismiss | `clinical_reasoning/urls.py` |

Source: `bgddr/urls.py:55-60`

### Root-Level Prefix Endpoints (Inconsistent)

| Prefix | Source | Notes |
|---|---|---|
| `/` | `clinic/urls.py` | Guided clinical-workflow UI |
| `/` | `users/urls.py` | User management |
| `/admin/` | django.contrib.admin | Admin interface |
| `/prescriptions/` | `prescriptions/urls.py` | Separate from `/api/v1/prescriptions/` |
| `/analytics/` | `analytics/urls.py` | HTML dashboard routes |
| `/studies/` | `studies/urls.py` | Study management |
| `/safety/` | `safety/urls.py` | Safety monitoring |
| `/scheduling/` | `scheduling/urls.py` | Visit scheduling |
| `/pathology/` | `pathology/urls.py` | Pathology-specific views |
| `/biomarkers/` | `biomarkers/urls.py` | Biomarker views |
| `/exports/` | `exports/urls.py` | Data export |
| `/fhir/` | `fhir/urls.py` | FHIR R4 interop |

---

## Consistency Assessment

### Naming Conventions

| Rule | Status | Violations |
|---|---|---|
| kebab-case for endpoints | 🟢 Consistent | All endpoints use hyphens: `lab-results`, `treatment-exposures`, `pathology-reviews`, etc. |
| Plural nouns for collections | 🟢 Consistent | All collections are plural: `patients`, `encounters`, `results`, `profiles` |
| /api/v1/ prefix for machine API | ⚠️ Mixed | 11 apps use root-level prefixes instead of /api/v1/ |
| Consistent versioning | ⚠️ Partial | /api/v1/ versioned; root-level endpoints are unversioned |

### HTTP Method Usage

| Method | Usage | Status |
|---|---|---|
| GET | List/retrieve | 🟢 Consistent |
| POST | Create (+ custom actions) | 🟢 Consistent |
| PUT | Not used | 🟡 Acceptable (PATCH preferred) |
| PATCH | Partial update | 🟢 Consistent |
| DELETE | Delete resource | 🟢 Consistent |

### Response Format

| Aspect | Status | Evidence |
|---|---|---|
| DRF pagination wrapper | 🟢 Consistent | `{count, next, previous, results}` wrapper for all list endpoints |
| Error format | ⚠️ Inconsistent | Inline error strings vs. `{error: "..."}` vs. DRF default validation errors |
| Hypermedia | 🔴 Absent | No HATEOAS links |

### Authentication

| Required Auth | Endpoints | Notes |
|---|---|---|
| Token + Session | All /api/v1/ endpoints | `DEFAULT_AUTHENTICATION_CLASSES` in settings |
| IsAuthenticated | Custom actions (reason, reason_all, explain, evaluate) | Explicit permission_classes |
| DjangoModelPermissions | All CRUD viewsets | Via `AuditedModelViewSet` base |

### Recommendations

1. **Move root-level endpoints under `/api/v1/`** for consistency
2. **Standardize error format** across all endpoints
3. **Add HATEOAS links** for discoverable navigation
4. **Document permission requirements per endpoint** in OpenAPI/Swagger
5. **Add version header** (Accept: application/vnd.bgddr.v1+json) for evolutions

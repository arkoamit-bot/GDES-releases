# BGDDR — RBAC Permission Matrix

## Roles Overview

| Role | Description | Typical User |
|---|---|---|
| `data_manager` | Full access to all models and operations | Registry administrator |
| `statistician` | View-only access to all data, full analytics | Research analyst |
| `readonly` | View-only access to all data | Auditor, external reviewer |
| `coordinator` | Patient management, scheduling, prescriptions | Clinic coordinator |
| `investigator` | Clinical data entry, prescriptions, studies | Nephrologist |
| `pathologist` | Pathology review and biopsy data | Pathologist |

---

## Model-Level Permissions

### CRUD Permissions by Role

| Model | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| **patients.Patient** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **encounters.ClinicalEncounter** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **encounters.Admission** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **encounters.RelapseEpisode** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **encounters.ClinicalEvent** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **baseline.BaselineAssessment** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **labs.LabTest** | ALL | VIEW | VIEW | ALL | VIEW | VIEW |
| **labs.LabPanel** | ALL | VIEW | VIEW | ALL | VIEW | VIEW |
| **labs.LabOrder** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **labs.LabOrderItem** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **labs.LabResult** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **pathology.Biopsy** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.GNDiagnosis** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.IgANScore** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.LupusPathology** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.FSGSPathology** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.MembranousPathology** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.BiopsyImage** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **pathology.PathologyReview** | ALL | VIEW | VIEW | VIEW | VIEW | ALL |
| **treatments.DrugMaster** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **treatments.TreatmentExposure** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **prescriptions.Prescription** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **prescriptions.PrescriptionItem** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **prescriptions.AdviceTemplate** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **analytics.PatientOutcome** | ALL | VIEW | VIEW | VIEW | VIEW | VIEW |
| **safety.AdverseEvent** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **studies.Study** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **studies.StudyArm** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **studies.StudyEnrollment** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **scheduling.ScheduledVisit** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **biomarkers.BiomarkerKinetics** | ALL | VIEW | VIEW | VIEW | VIEW | VIEW |
| **audit.AuditLog** | ALL | VIEW | VIEW | VIEW | VIEW | VIEW |
| **audit.Consent** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **users.UserProfile** | ALL | VIEW | VIEW | ALL | VIEW | VIEW |
| **users.Invitation** | ALL | VIEW | VIEW | ALL | VIEW | VIEW |
| **clinical.ClinicalAssessment** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **clinical.VitalSign** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **knowledge.GuidelineSource** | ALL | VIEW | VIEW | VIEW | VIEW | VIEW |
| **knowledge.KnowledgeBaseEntry** | ALL | VIEW | VIEW | VIEW | VIEW | VIEW |
| **decision.DecisionRequest** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **decision.DecisionResult** | ALL | VIEW | VIEW | ALL | ALL | VIEW |
| **timeline.TimelineEvent** | ALL | VIEW | VIEW | ALL | ALL | VIEW |

**Legend**: ALL = add/change/delete, VIEW = view-only

---

## Endpoint-Level Permissions

### DRF API Endpoints

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `POST /api/v1/auth/token/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /api/v1/patients/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /api/v1/patients/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `PUT/PATCH /api/v1/patients/{id}/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `DELETE /api/v1/patients/{id}/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `GET /api/v1/encounters/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /api/v1/encounters/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `GET /api/v1/biopsies/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /api/v1/biopsies/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| `POST /api/v1/pathology-reviews/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| `GET /api/v1/prescriptions/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /api/v1/prescriptions/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `POST /api/v1/prescriptions/{id}/finalize/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `GET /api/v1/outcomes/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /api/v1/biomarkers/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /api/v1/drugs/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /api/v1/drugs/` | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ |

### Clinic Workflow Views

| View | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| Patient list | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Patient detail | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create patient | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Edit patient | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Delete patient | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Baseline assessment | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Follow-up visit | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Create prescription | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Finalize prescription | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Adverse event | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Register patient | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Document relapse | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Record biopsy | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Pathology review | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Lab order | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Lab results entry | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Study enrollment | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Consent management | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Treatment add | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Worklist | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Analytics page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cox results | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| eGFR slope results | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| CIF results | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Safety page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Studies page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Pathology page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Biomarkers page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Export page | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Recompute outcome | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |

### Analytics JSON Endpoints

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `GET /analytics/survival/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /analytics/cox/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /analytics/egfr-slope/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /analytics/competing-risks/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /analytics/cohort-summary/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Safety JSON Endpoints

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `GET /safety/summary/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /safety/infection-incidence/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /safety/study-safety/{id}/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Scheduling JSON Endpoints

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `GET /scheduling/due/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /scheduling/overdue/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `GET /scheduling/roster/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `POST /scheduling/generate/{id}/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| `POST /scheduling/complete/{id}/` | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |

### Export Endpoints

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `GET /exports/research-dataset/` | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `GET /exports/data-dictionary/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Admin Backup Console

| Endpoint | data_manager | statistician | readonly | coordinator | investigator | pathologist |
|---|---|---|---|---|---|---|
| `GET /admin/backups/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `POST /admin/backups/create/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `POST /admin/backups/restore/{file}/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `GET /admin/backups/download/{file}/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

---

## Permission Implementation

### Django Groups

Roles are implemented as Django `auth.Group` objects. When a `UserProfile.role` is set, the user is automatically added to the corresponding group:

```python
# users/models.py
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    if self.role:
        group, _ = Group.objects.get_or_create(name=self.role)
        self.user.groups.set([group])
    else:
        self.user.groups.clear()
```

### DRF Permission Classes

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.DjangoModelPermissions",
    ],
}
```

`DjangoModelPermissions` maps Django model permissions to DRF:
- `view` → GET, HEAD, OPTIONS
- `add` → POST
- `change` → PUT, PATCH
- `delete` → DELETE

### Admin Permissions

The Django admin uses the same permission system. The Jazzmin theme customizes the sidebar order but does not change permission logic.

---

## Role Assignment Workflow

```
Admin creates Invitation
    │  → email + role
    │  → token generated (secrets.token_urlsafe)
    │
    ├── Email sent with invite link
    │   → /users/accept-invitation/<token>/
    │
    ├── User clicks link
    │   → Sets password
    │   → Account created
    │   → UserProfile.role = invited role
    │   → User added to Django Group
    │
    └── Role permissions active
        → DjangoModelPermissions enforce access
```

---

## Special Cases

### Data Export Identifiers
- `data_manager` and `statistician` can export with `identified=True` (includes name, phone, hospital_id)
- All other roles get de-identified exports only

### Prescription Finalization
- Only users with prescription permissions can finalize
- `coordinator` and `investigator` can finalize
- `pathologist`, `statistician`, `readonly` cannot

### Pathology Review
- Only `pathologist` role can submit pathology reviews
- `data_manager` can also submit (for administrative overrides)
- Other roles have view-only access

### Patient Deletion
- Only `data_manager` can delete patients
- Uses `delete_patient_cascade()` for FK-safe deletion
- `coordinator`, `investigator` cannot delete patients

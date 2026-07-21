# BGDDR — Database Schema

## Overview

- **38 Django models** across **18 active apps**
- **Default database**: SQLite (desktop) / PostgreSQL (production)
- **ORM only**: No raw SQL, no SQLite-specific features — database-agnostic
- **Auto-field**: BigAutoField (default)

---

## Table Inventory

| # | Table | App | Key Relationships |
|---|---|---|---|
| 1 | `patients_patient` | patients | Root model |
| 2 | `encounters_clinicalencounter` | encounters | FK → Patient |
| 3 | `encounters_admission` | encounters | FK → Patient, FK → Biopsy |
| 4 | `encounters_relapsepisode` | encounters | FK → Patient, FK → ClinicalEncounter |
| 5 | `encounters_clinicalevent` | encounters | FK → Patient, FK → ClinicalEncounter |
| 6 | `baseline_baselineassessment` | baseline | OneToOne → Patient |
| 7 | `labs_labtest` | labs | — |
| 8 | `labs_labpanel` | labs | M2M → LabTest |
| 9 | `labs_laborder` | labs | FK → ClinicalEncounter, FK → Patient |
| 10 | `labs_laborderitem` | labs | FK → LabOrder, FK → LabTest |
| 11 | `labs_labresult` | labs | FK → Patient, FK → LabTest, FK → LabOrderItem, FK → self |
| 12 | `pathology_biopsy` | pathology | FK → Patient |
| 13 | `pathology_gndiagnosis` | pathology | OneToOne → Biopsy |
| 14 | `pathology_iganscore` | pathology | OneToOne → Biopsy |
| 15 | `pathology_lupuspathology` | pathology | OneToOne → Biopsy |
| 16 | `pathology_fsgspathology` | pathology | OneToOne → Biopsy |
| 17 | `pathology_membranouspathology` | pathology | OneToOne → Biopsy |
| 18 | `pathology_biopsyimage` | pathology | FK → Biopsy |
| 19 | `pathology_pathologyreview` | pathology | FK → Biopsy, FK → User |
| 20 | `treatments_drugmaster` | treatments | — |
| 21 | `treatments_treatmentexposure` | treatments | FK → Patient, FK → DrugMaster, FK → ClinicalEncounter ×2 |
| 22 | `prescriptions_prescription` | prescriptions | FK → ClinicalEncounter, FK → User |
| 23 | `prescriptions_prescriptionitem` | prescriptions | FK → Prescription, FK → DrugMaster |
| 24 | `prescriptions_advicetemplate` | prescriptions | — |
| 25 | `analytics_patientoutcome` | analytics | OneToOne → Patient |
| 26 | `safety_adverseevent` | safety | FK → Patient, FK → DrugMaster, FK → ClinicalEncounter |
| 27 | `studies_study` | studies | — |
| 28 | `studies_studyarm` | studies | FK → Study |
| 29 | `studies_studyenrollment` | studies | FK → Study, FK → Patient, FK → StudyArm, FK → User |
| 30 | `scheduling_scheduledvisit` | scheduling | FK → Patient, FK → ClinicalEncounter |
| 31 | `biomarkers_biomarkerkinetics` | biomarkers | OneToOne → Patient |
| 32 | `audit_auditlog` | audit | FK → User |
| 33 | `audit_consent` | audit | FK → Patient, FK → User, OneToOne → self |
| 34 | `users_userprofile` | users | OneToOne → User |
| 35 | `users_invitation` | users | FK → User ×2 |
| 36 | `clinical_clinicalassessment` | clinical | OneToOne → ClinicalEncounter |
| 37 | `clinical_vitalsign` | clinical | FK → ClinicalEncounter |
| 38 | `knowledge_guidelinesource` | knowledge | — |
| 39 | `knowledge_knowledgebaseentry` | knowledge | FK → GuidelineSource |
| 40 | `decision_decisionrequest` | decision | FK → Patient, FK → ClinicalEncounter |
| 41 | `decision_decisionresult` | decision | OneToOne → DecisionRequest |
| 42 | `timeline_timelinetimeline` | timeline | FK → Patient |

---

## Indexes

### Explicitly Declared Indexes

| Table | Fields | Type |
|---|---|---|
| `patients_patient` | `patient_id` | unique |
| `patients_patient` | `hospital_id` | btree |
| `patients_patient` | `phone` | btree |
| `patients_patient` | `registration_status` | btree |
| `patients_patient` | `current_phase` | btree |
| `encounters_clinicalencounter` | `patient`, `encounter_date` | composite btree |
| `encounters_admission` | `patient`, `admit_date` | composite btree |
| `encounters_relapsepisode` | `patient`, `relapse_date` | composite btree |
| `encounters_clinicalevent` | `patient`, `event_type`, `event_date` | composite btree |
| `labs_laborder` | `patient`, `ordered_date` | composite btree |
| `labs_labresult` | `patient`, `test`, `result_date` | composite btree |
| `pathology_biopsy` | `result_category` | btree |
| `treatments_treatmentexposure` | `patient`, `ongoing` | composite btree |
| `treatments_treatmentexposure` | `drug`, `ongoing` | composite btree |
| `safety_adverseevent` | `patient`, `onset_date` | composite btree |
| `safety_adverseevent` | `category`, `onset_date` | composite btree |
| `scheduling_scheduledvisit` | `status`, `window_end` | composite btree |
| `scheduling_scheduledvisit` | `clinic_date` | btree |
| `audit_auditlog` | `model_label`, `object_pk` | composite btree |
| `audit_auditlog` | `changed_at` | btree |
| `audit_consent` | `patient`, `consent_type`, `is_current` | composite btree |
| `knowledge_knowledgebaseentry` | `disease_id`, `status` | composite btree |
| `knowledge_guidelinesource` | `abbreviation`, `version_year` | composite btree |
| `clinical_clinicalassessment` | `encounter` | btree |
| `timeline_timelinetimeline` | `patient`, `domain` | composite btree |
| `timeline_timelinetimeline` | `patient`, `-event_date` | composite btree |
| `timeline_timelinetimeline` | `event_type` | btree |
| `timeline_timelinetimeline` | `event_date` | btree |

### Unique Constraints

| Table | Fields | Constraint Name |
|---|---|---|
| `labs_laborderitem` | `order`, `test` | `uniq_order_test` |
| `prescriptions_prescription` | `encounter`, `version` | `uniq_encounter_version` |
| `pathology_pathologyreview` | `biopsy`, `role` | `uniq_biopsy_review_role` |
| `studies_studyarm` | `study`, `code` | `uniq_study_arm_code` |
| `studies_studyenrollment` | `study`, `patient` | `uniq_study_patient` |
| `scheduling_scheduledvisit` | `patient`, `label` | `uniq_patient_visit_label` |
| `audit_consent` | `patient`, `consent_type` (WHERE is_current=True) | `uniq_current_consent_per_type` |

---

## Foreign Key Relationships

### Patient → (all child tables)

```
patients_patient.id
    │
    ├── encounters_clinicalencounter.patient_id       (PROTECT)
    ├── encounters_admission.patient_id               (CASCADE)
    ├── encounters_relapsepisode.patient_id            (CASCADE)
    ├── encounters_clinicalevent.patient_id            (CASCADE)
    ├── baseline_baselineassessment.patient_id         (CASCADE, OneToOne)
    ├── labs_laborder.patient_id                       (CASCADE)
    ├── labs_labresult.patient_id                      (CASCADE)
    ├── pathology_biopsy.patient_id                    (CASCADE)
    ├── treatments_treatmentexposure.patient_id        (CASCADE)
    ├── safety_adverseevent.patient_id                 (CASCADE)
    ├── studies_studyenrollment.patient_id             (CASCADE)
    ├── scheduling_scheduledvisit.patient_id           (CASCADE)
    ├── biomarkers_biomarkerkinetics.patient_id        (CASCADE, OneToOne)
    ├── audit_consent.patient_id                       (CASCADE)
    ├── analytics_patientoutcome.patient_id            (CASCADE, OneToOne)
    ├── decision_decisionrequest.patient_id            (CASCADE)
    ├── timeline_timelinetimeline.patient_id           (CASCADE)
    └── clinical_clinicalassessment (via encounter)
```

### ClinicalEncounter → (visit-scoped children)

```
encounters_clinicalencounter.id
    │
    ├── labs_laborder.encounter_id                    (PROTECT)
    ├── prescriptions_prescription.encounter_id       (PROTECT)
    ├── encounters_clinicalevent.encounter_id         (SET_NULL)
    ├── encounters_relapsepisode.encounter_id         (SET_NULL)
    ├── safety_adverseevent.encounter_id              (SET_NULL)
    ├── scheduling_scheduledvisit.encounter_id        (SET_NULL)
    ├── clinical_clinicalassessment.encounter_id      (CASCADE, OneToOne)
    ├── clinical_vitalsign.encounter_id               (CASCADE)
    ├── decision_decisionrequest.encounter_id         (CASCADE)
    └── treatments_treatmentexposure.opened_by_encounter_id / closed_by_encounter_id (SET_NULL)
```

### Biopsy → (pathology children)

```
pathology_biopsy.id
    │
    ├── pathology_gndiagnosis.biopsy_id               (CASCADE, OneToOne)
    ├── pathology_iganscore.biopsy_id                 (CASCADE, OneToOne)
    ├── pathology_lupuspathology.biopsy_id            (CASCADE, OneToOne)
    ├── pathology_fsgspathology.biopsy_id             (CASCADE, OneToOne)
    ├── pathology_membranouspathology.biopsy_id       (CASCADE, OneToOne)
    ├── pathology_biopsyimage.biopsy_id               (CASCADE)
    ├── pathology_pathologyreview.biopsy_id           (CASCADE)
    └── encounters_admission.biopsy_id                (SET_NULL)
```

### DrugMaster → (drug references)

```
treatments_drugmaster.id
    │
    ├── prescriptions_prescriptionitem.drug_id        (PROTECT)
    ├── treatments_treatmentexposure.drug_id          (PROTECT)
    └── safety_adverseevent.suspected_drug_id         (SET_NULL)
```

### User → (auth references)

```
auth_user.id
    │
    ├── encounters_clinicalencounter.seen_by_id       (PROTECT)
    ├── prescriptions_prescription.printed_by_id      (PROTECT)
    ├── pathology_pathologyreview.reviewer_id         (SET_NULL)
    ├── studies_studyenrollment.randomized_by_id      (SET_NULL)
    ├── audit_auditlog.changed_by_id                  (SET_NULL)
    ├── audit_consent.obtained_by_id                  (SET_NULL)
    ├── users_invitation.created_by_id                (SET_NULL)
    ├── users_invitation.used_by_id                   (SET_NULL)
    └── users_userprofile.user_id                     (CASCADE, OneToOne)
```

---

## Cascade Behavior Summary

| On Delete | Models |
|---|---|
| **CASCADE** | Most FK from Patient; PrescriptionItem→Prescription; LabOrderItem→LabOrder; StudyArm→Study; BiopsyImage→Biopsy; PathologyReview→Biopsy; GNDiagnosis→Biopsy; IgANScore→Biopsy; LupusPathology→Biopsy; FSGSPathology→Biopsy; MembranousPathology→Biopsy; Consent→Patient; ClinicalAssessment→ClinicalEncounter; VitalSign→ClinicalEncounter; DecisionRequest→Patient; DecisionResult→DecisionRequest; TimelineEvent→Patient; UserProfile→User |
| **PROTECT** | ClinicalEncounter→Patient; Prescription→ClinicalEncounter; LabOrder→ClinicalEncounter; LabTest→(in LabOrderItem, LabResult); DrugMaster→(in PrescriptionItem, TreatmentExposure); StudyArm→(in StudyEnrollment); GuidelineSource→(in KnowledgeBaseEntry); Prescription→User (printed_by) |
| **SET_NULL** | LabResult→LabOrderItem; LabResult→self (derived_from); Admission→Biopsy; ClinicalEvent→ClinicalEncounter; RelapseEpisode→ClinicalEncounter; AdverseEvent→ClinicalEncounter; AdverseEvent→DrugMaster; ScheduledVisit→ClinicalEncounter; TreatmentExposure→ClinicalEncounter (opened/closed); AuditLog→User; Consent→User; StudyEnrollment→User; Invitation→User |

---

## SQLite-Specific Configuration

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BGDDR_DATA_DIR / "db.sqlite3",
        "OPTIONS": {"timeout": 30},  # 30s busy-timeout for OneDrive
    }
}
```

- **Busy timeout**: 30 seconds to avoid "database is locked" during OneDrive sync
- **No WAL mode** explicitly configured (SQLite default)
- **No SQLite-specific features** used in ORM queries

---

## PostgreSQL Production Configuration

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "bgddr"),
        "USER": os.environ.get("POSTGRES_USER", "bgddr"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}
```

- **Connection pooling**: 600s persistent connections
- **Materialized views**: Available for analytics layer
- **pgaudit**: Available for compliance auditing

---

## Migration History

All apps have `0001_initial.py` migrations. The `users` app has a second migration:
- `0001_initial.py` — Creates UserProfile and Invitation
- `0002_alter_invitation_role_alter_userprofile_role.py` — Updates role choices

Migration commands:
```bash
python manage.py migrate          # Apply all migrations
python manage.py showmigrations   # View migration status
python manage.py sqlmigrate <app> <number>  # View SQL
```

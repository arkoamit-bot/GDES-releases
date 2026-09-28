# Bounded Contexts

**Version:** 2.5  
**Pattern:** Each context has clear ownership, public interfaces, and anti-corruption layers

---

## Context Map

```
┌──────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│   Identity & Security │     │       Registry           │     │  Patient Management  │
│   (auth, users, roles)│────▶│  (patients, sites)       │────▶│  (encounters, events)│
└──────────────────────┘     └──────────────────────────┘     └──────────┬───────────┘
                                                                         │
                                                                         ▼
┌──────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│   Knowledge Platform  │◀────│   Clinical Reasoning     │◀────│    Laboratory        │
│   (guidelines, rules) │     │   (profiles, insights)   │     │   (lab results)      │
└──────────────────────┘     └──────────────────────────┘     └──────────────────────┘
         │                            │                                │
         ▼                            ▼                                ▼
┌──────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│   Decision Support   │     │  Analytics & Outcomes    │     │     Pathology        │
│   (decisions, calc)  │     │  (outcomes, trends)      │     │   (biopsies, review) │
└──────────────────────┘     └──────────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│  Drug Intelligence   │     │    Prescription          │     │ Follow-up & Schedule │
│  (treatments, drugs) │     │    (rx management)       │     │   (visits, reminders)│
└──────────────────────┘     └──────────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│      Research        │     │   Administration         │     │  Event Orchestration │
│   (studies, cohorts) │     │   (audit, consent,       │     │  (dispatch, events)  │
│                      │     │    export, admin)        │     │                      │
└──────────────────────┘     └──────────────────────────┘     └──────────────────────┘
```

---

## Context 1: Identity & Security

| Aspect | Detail |
|---|---|
| **App(s)** | `users`, `api/permissions.py` |
| **Responsibilities** | User authentication, role-based access control, site-scoped permissions |
| **Owned Data** | User, Group, Permission, UserSiteRole |
| **Aggregates** | — (Django auth models) |
| **Public Interface** | Token auth endpoint, DjangoModelPermissions, site_filter_kwargs() |
| **Dependencies** | Django auth framework |
| **Shared Kernel** | User model referenced by AuditLog, DecisionResult, Consent |
| **Anti-Corruption Layer** | `AuditedModelViewSet` wraps DRF views with audit attribution |

**Events:** None emitted

---

## Context 2: Registry

| Aspect | Detail |
|---|---|
| **App(s)** | `patients`, `baseline` |
| **Responsibilities** | Patient registration, site management, cohort assignment, enrollment tracking |
| **Owned Data** | Patient, Site, DiseasePhase, RegistrationStatus |
| **Aggregates** | Patient (root), Site (root) |
| **Public Interface** | `Patient.objects`, API `/api/v1/patients/`, `/api/v1/sites/` |
| **Dependencies** | Identity & Security (for site access control) |
| **Shared Kernel** | Patient is the central entity shared across all contexts |
| **Published Events** | `patient.registered`, `patient.updated` |

---

## Context 3: Patient Management

| Aspect | Detail |
|---|---|
| **App(s)** | `encounters`, `clinic` |
| **Responsibilities** | Clinical encounter tracking, clinical event logging, vital signs |
| **Owned Data** | ClinicalEncounter, ClinicalEvent |
| **Aggregates** | ClinicalEncounter (root) |
| **Public Interface** | API `/api/v1/encounters/`, `/api/v1/events/` |
| **Dependencies** | Registry (Patient) |
| **Published Events** | `encounter.created`, `encounter.updated`, `clinical_event.created` |

---

## Context 4: Laboratory

| Aspect | Detail |
|---|---|
| **App(s)** | `labs`, `biomarkers` |
| **Responsibilities** | Lab result entry, test catalog management, biomarker kinetics, eGFR computation |
| **Owned Data** | LabResult, LabTest, BiomarkerKinetics |
| **Aggregates** | LabResult (root), BiomarkerKinetics (computed root) |
| **Public Interface** | API `/api/v1/lab-results/`, `/api/v1/biomarkers/` |
| **Dependencies** | Registry (Patient) |
| **Published Events** | `lab_result.created`, `lab_result.updated` |

---

## Context 5: Pathology

| Aspect | Detail |
|---|---|
| **App(s)** | `pathology` |
| **Responsibilities** | Biopsy recording, pathology review workflow, histological diagnosis |
| **Owned Data** | Biopsy, PathologyReview, GNDiagnosis |
| **Aggregates** | Biopsy (root, with PathologyReview children) |
| **Public Interface** | API `/api/v1/biopsies/`, `/api/v1/pathology-reviews/` |
| **Dependencies** | Registry (Patient) |
| **Published Events** | `biopsy.created` (→ triggers milestone detection in Clinical Reasoning) |

---

## Context 6: Drug Intelligence

| Aspect | Detail |
|---|---|
| **App(s)** | `treatments` |
| **Responsibilities** | Treatment exposure tracking, drug master catalog, renal dose adjustment |
| **Owned Data** | TreatmentExposure, DrugMaster |
| **Aggregates** | TreatmentExposure (root) |
| **Public Interface** | API `/api/v1/treatment-exposures/`, `/api/v1/drugs/` |
| **Dependencies** | Registry (Patient) |
| **Published Events** | `treatment_exposure.created`, `treatment_exposure.updated` |

---

## Context 7: Prescription

| Aspect | Detail |
|---|---|
| **App(s)** | `prescriptions` |
| **Responsibilities** | Prescription creation, versioning, reconciliation |
| **Owned Data** | Prescription |
| **Aggregates** | Prescription (root) |
| **Public Interface** | API `/api/v1/prescriptions/` (read-only), `/prescriptions/` (UI views) |
| **Dependencies** | Registry (Patient), Patient Management (Encounter) |
| **Published Events** | `prescription.created` |

---

## Context 8: Knowledge Platform

| Aspect | Detail |
|---|---|
| **App(s)** | `knowledge` |
| **Responsibilities** | Guideline source management, clinical rule authoring, rule versioning, review workflow, evidence management, rule testing |
| **Owned Data** | GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion, RuleReview, RuleTestResult, GuidelineDocument, EvidenceEntry, RuleTemplate |
| **Aggregates** | KnowledgeBaseEntry (root, with versions/reviews/tests/evidence children), GuidelineSource (root) |
| **Public Interface** | API endpoints for all models; `evaluate_patient_rules()`, `extract_patient_features()` service functions |
| **Dependencies** | Registry (Patient, for feature extraction) |
| **Published Events** | (defined but not yet wired: `decision.requested`, `recommendation.generated`, `safety_alert.raised`) |

**Business Rules:**
- Only ACTIVE rules are evaluated against patients
- Rule quality is scored on completeness, clarity, evidence, testability
- Conflicting rules for the same disease are flagged

---

## Context 9: Decision Support

| Aspect | Detail |
|---|---|
| **App(s)** | `decision`, `clinical` |
| **Responsibilities** | Clinical decision requests, case evaluation, clinical calculators (eGFR, BSA, UPCR), recommendation generation, override tracking |
| **Owned Data** | DecisionRequest, DecisionResult |
| **Aggregates** | DecisionRequest (root, with DecisionResult child) |
| **Public Interface** | API `/api/v1/decisions/`, `/api/v1/results/`; `evaluate` custom action, `calculators` custom action |
| **Dependencies** | Registry (Patient), Patient Management (Encounter), Knowledge Platform (rules for traceability) |
| **Published Events** | (defined: `decision.requested`, `recommendation.generated`) |

---

## Context 10: Clinical Reasoning

| Aspect | Detail |
|---|---|
| **App(s)** | `clinical_reasoning`, `timeline` |
| **Responsibilities** | Clinical profile computation, insight generation, milestone detection, care pathway determination, trajectory assessment, risk assessment, explainability, gap detection |
| **Owned Data** | ClinicalProfile, ClinicalInsight |
| **Aggregates** | ClinicalProfile (root, with value object collections) |
| **Public Interface** | API `/api/v1/profiles/`, `/api/v1/insights/`; event handlers subscribed to 7 event types |
| **Dependencies** | Registry (Patient), Laboratory (lab data via features), Pathology (biopsy via milestones), Drug Intelligence (treatment via milestones), Knowledge Platform (rule evaluation), Analytics (outcome computation) |
| **Published Events** | `clinical_profile.updated`, `care_pathway.updated`, `reasoning.completed` (defined but not yet wired to dispatch) |

**This is the Core Domain.** The most complex and differentiating business logic lives here.

---

## Context 11: Analytics & Outcomes

| Aspect | Detail |
|---|---|
| **App(s)** | `analytics` |
| **Responsibilities** | Outcome computation (remission, relapse, ESKD), operational intelligence (compliance, gaps), trend analysis |
| **Owned Data** | PatientOutcome |
| **Aggregates** | PatientOutcome (root) |
| **Public Interface** | `compute_patient_outcome()` service function; API `/api/v1/outcomes/`; HTML dashboard routes |
| **Dependencies** | Registry (Patient), Laboratory (lab result series), Patient Management (encounters), Drug Intelligence (treatment exposure) |
| **Published Events** | `outcome.recorded`, `outcome.recomputed`, `disease_trajectory.updated` (defined) |

---

## Context 12: Follow-up & Scheduling

| Aspect | Detail |
|---|---|
| **App(s)** | `scheduling`, `reminders` |
| **Responsibilities** | Visit scheduling, reminder generation, overdue visit detection |
| **Owned Data** | ScheduledVisit, Reminder |
| **Aggregates** | ScheduledVisit (root) |
| **Dependencies** | Registry (Patient) |
| **Published Events** | `reminder.sent`, `follow_up.scheduled`, `visit.overdue` (defined) |

---

## Context 13: Research

| Aspect | Detail |
|---|---|
| **App(s)** | `studies` |
| **Responsibilities** | Study management, patient enrollment, cohort discovery, protocol matching |
| **Owned Data** | Study, StudyEnrollment |
| **Aggregates** | Study (root) |
| **Public Interface** | Study management views; `discover_cohorts()`, `match_patient_to_protocols()` service functions |
| **Dependencies** | Registry (Patient, diagnosis/phase) |

---

## Context 14: Administration

| Aspect | Detail |
|---|---|
| **App(s)** | `audit`, `exports`, `admin` (Django) |
| **Responsibilities** | Audit logging, consent management, data export, admin interface |
| **Owned Data** | AuditLog, Consent |
| **Aggregates** | AuditLog (root), Consent (conceptually owned by Patient) |
| **Dependencies** | Registry (Patient for consent), Identity & Security (User for audit) |

---

## Context 15: Event Orchestration

| Aspect | Detail |
|---|---|
| **App(s)** | `events` |
| **Responsibilities** | Domain event dispatch, handler registration, event persistence, signal-to-event bridge |
| **Owned Data** | Event, EventSubscription |
| **Aggregates** | Event (root) |
| **Public Interface** | `dispatch()`, `subscribe()`, `unsubscribe()` functions; signal handlers in `signal_handlers.py` |
| **Dependencies** | All other contexts (as event publishers) |

---

## Context 16: FHIR Interoperability

| Aspect | Detail |
|---|---|
| **App(s)** | `fhir` |
| **Responsibilities** | FHIR R4 API exposure for external EHR integration |
| **Owned Data** | None (maps to existing models) |
| **Public Interface** | `/fhir/` endpoint |
| **Dependencies** | Registry (Patient), all clinical data contexts |

---

## Context Dependency Summary

| Context | Upstream Dependencies | Downstream Consumers | Coupling Level |
|---|---|---|---|
| Identity & Security | — | Registry, Administration | Low (auth check) |
| Registry | Identity | All clinical contexts | High (shared Patient) |
| Patient Management | Registry | Analytics, Clinical Reasoning, Decision | Medium |
| Laboratory | Registry | Analytics, Clinical Reasoning | Medium |
| Pathology | Registry | Clinical Reasoning | Low (milestone only) |
| Drug Intelligence | Registry | Clinical Reasoning, Analytics | Low |
| Prescription | Registry, Patient Mgmt | Analytics | Low |
| Knowledge Platform | Registry | Clinical Reasoning, Decision | Medium |
| Decision Support | Registry, Patient Mgmt, Knowledge | — | Low |
| Clinical Reasoning | Registry, Lab, Pathology, Drugs, Knowledge, Analytics | — | High (most complex) |
| Analytics | Registry, Lab, Patient Mgmt, Drugs | Clinical Reasoning | Medium |
| Follow-up | Registry | — | Low |
| Research | Registry | — | Low |
| Administration | Registry, Identity | — | Low |
| Event Orchestration | All (as publisher) | Clinical Reasoning | Low (event-driven) |
| FHIR | Registry, all clinical | — | Low |

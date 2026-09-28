# Domain Model Overview

**Version:** 2.5  
**Project:** Glomerular Disease Expert System (GDES)  
**Style:** Domain-Driven Design (DDD) — Django-independent domain model

---

## Domain Map

```
┌─────────────────────────────────────────────────────────────┐
│                   Identity & Security Context               │
│  User ──1:N── UserSiteRole ──N:1── Site                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Registry Context                        │
│  Site ──1:N── Patient ──1:N──┐                              │
│                              │                              │
│  DiseasePhase, RegistrationStatus (value objects)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Patient Management Context                 │
│  Patient ──1:N── ClinicalEncounter                          │
│  Patient ──1:N── ClinicalEvent                              │
│  ClinicalEncounter ──1:N── (VitalSigns, encounter notes)    │
│                                                             │
│  EncounterType, VitalSigns (value objects)                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Laboratory Context                      │
│  Patient ──1:N── LabResult                                   │
│  Patient ──1:N── BiomarkerKinetics                          │
│                                                             │
│  LabValue, ReferenceRange, LabFlag (value objects)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Pathology Context                       │
│  Patient ──1:N── Biopsy                                      │
│  Biopsy ──1:N── PathologyReview                             │
│                                                             │
│  HistologicalDiagnosis, GNPattern (value objects)            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Decision Support Context                  │
│  Patient ──1:N── DecisionRequest ──1:1── DecisionResult     │
│  DecisionRequest ──N:1── ClinicalEncounter                  │
│                                                             │
│  RankedDifferential, UrgencyLevel, CalculatorType (VOs)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Knowledge Platform Context               │
│  GuidelineSource ──1:N── KnowledgeBaseEntry                 │
│  KnowledgeBaseEntry ──1:N── KnowledgeBaseVersion            │
│  KnowledgeBaseEntry ──1:N── RuleReview                      │
│  KnowledgeBaseEntry ──1:N── RuleTestResult                  │
│  KnowledgeBaseEntry ──1:N── EvidenceEntry                   │
│  GuidelineSource ──1:N── GuidelineDocument                  │
│                                                             │
│  RuleData, Condition, EvidenceGrade (value objects)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Drug Intelligence Context                  │
│  Patient ──1:N── TreatmentExposure                           │
│  DrugMaster (reference data)                                │
│                                                             │
│  DrugDose, TreatmentRegimen, DrugClass (value objects)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Prescription Context                       │
│  Patient ──1:N── Prescription                                │
│  Prescription ──N:1── ClinicalEncounter                     │
│                                                             │
│  Dosage, PrescriptionStatus, PrescriptionLine (VOs)         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Clinical Reasoning Context                │
│  Patient ──1:1── ClinicalProfile                             │
│  Patient ──1:N── ClinicalInsight                            │
│                                                             │
│  Differential, DiseaseTrajectory, RiskAssessment,            │
│  CarePathway, EvidenceSummary, ReasoningChain,               │
│  InformationGap, DiseaseMilestone, CareStage (VOs)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Analytics & Outcomes Context              │
│  Patient ──1:N── PatientOutcome                              │
│                                                             │
│  RemissionStatus, OutcomeEvent (value objects)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Follow-up & Scheduling Context             │
│  Patient ──1:N── ScheduledVisit                              │
│  Patient ──1:N── Reminder                                   │
│                                                             │
│  VisitStatus, ScheduleWindow (value objects)                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Research Context                       │
│  Study ──1:N── StudyEnrollment ──N:1── Patient              │
│                                                             │
│  CohortDefinition, EligibilityCriterion (value objects)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Administration Context                  │
│  AuditLog, Consent, Export                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      Event Orchestration                     │
│  Event, EventSubscription                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Domain Layers

### Core Domain (Differentiating Value)
- Clinical Reasoning & Explainability Pipeline
- Knowledge-Based Rule Evaluation & Conflict Detection
- Care Pathway Engine with Stage Transitions
- Disease Milestone & Trajectory Tracking
- Drug Safety & Interaction Detection

### Supporting Domain (Essential but not differentiating)
- Patient Registration & Identity
- Encounter & Clinical Event Management
- Laboratory Result Management
- Biopsy & Pathology Management
- Prescription Management
- Treatment Exposure Tracking
- Outcome Computation

### Generic Domain (Off-the-shelf solutions)
- Authentication & Authorization (Django auth + DRF Token)
- Audit Logging
- FHIR Interoperability
- Data Export
- Administration Interface (Django Admin)

---

## Key Business Concepts

| Concept | Description | Domain Layer |
|---|---|---|
| Patient | Person with suspected/diagnosed GN | Supporting |
| ClinicalProfile | Computed intelligence summary for a patient | Core |
| KnowledgeBaseEntry | Clinical rule with conditions, weights, evidence | Core |
| ClinicalEncounter | Patient visit/consultation | Supporting |
| LabResult | Laboratory test result | Supporting |
| Biopsy | Renal biopsy findings | Supporting |
| TreatmentExposure | Drug treatment episode | Supporting |
| DecisionResult | AI-generated clinical recommendation | Core |
| ClinicalInsight | Individual actionable insight | Core |
| DiseaseMilestone | Key event in disease trajectory | Core |
| CarePathway | 8-stage disease management pathway | Core |

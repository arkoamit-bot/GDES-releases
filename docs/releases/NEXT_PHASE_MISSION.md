# NEXT_PHASE_MISSION.md

# GDES Next Development Mission (Phase 3.2)

> **Project:** Glomerular Disease Expert System (GDES)
>
> **Current Status:** Phase 3.1 Complete
>
> **Tests:** 269 Passing
>
> **Priority:** Highest

---

# Current State

The existing BGDDR platform has successfully evolved into the foundation of GDES.

Current achievements include:

- Complete clinical registry
- Longitudinal patient management
- Clinical decision support
- Knowledge-based rule engine
- Clinical calculators
- Guideline versioning
- Override tracking
- Laboratory trend intelligence
- Research analytics
- Comprehensive REST API
- Excellent automated test coverage

The system is now a mature **Clinical Registry + Decision Support Platform**.

The next objective is to transform it into a true **Clinical Intelligence Platform**.

---

# Mission

Do **NOT** build random new features.

Build the remaining core intelligence engines in a logical order.

Every new module must integrate with the existing architecture.

---

# Development Roadmap

Complete the following phases sequentially.

---

# Phase 3.2 — Drug Intelligence Engine (Highest Priority)

Create a new application:

```
drug_engine/
```

Implement:

- Drug interaction engine
- Drug–drug interaction database
- Drug–disease contraindications
- Renal dose adjustment
- Dialysis dose adjustment
- eGFR-based dosing
- Pregnancy safety
- Lactation safety
- Vaccination requirements
- Infection screening requirements
- Required laboratory monitoring
- Black-box warnings
- Alternative medications
- Cost category
- Evidence level
- Guideline references

Every recommendation must include an explanation.

---

# Phase 3.3 — Follow-up & Reminder Engine

Create:

```
followup_engine/
```

Support:

- Automatic follow-up scheduling
- Missed appointment detection
- Laboratory reminders
- Drug monitoring reminders
- Vaccination reminders
- Relapse surveillance
- SMS reminders
- Email reminders
- In-app notifications

Scheduling rules must be configurable through the database.

---

# Phase 3.4 — Explainability Engine

Create:

```
explainability/
```

Every clinical recommendation should answer:

- Why was this diagnosis suggested?
- Which patient findings contributed?
- Which rules matched?
- Which guideline supports the recommendation?
- What evidence grade applies?
- What confidence score was calculated?
- Which alternative diagnoses were considered?

The clinician must always understand the reasoning.

---

# Phase 3.5 — Knowledge Base Expansion

Expand the knowledge base from:

```
87 rules
```

toward

```
500–1000+ structured rules
```

Organize by domains:

- IgA Nephropathy
- Lupus Nephritis
- Membranous Nephropathy
- FSGS
- Minimal Change Disease
- ANCA Vasculitis
- Anti-GBM Disease
- C3 Glomerulopathy
- Infection-related GN
- Diabetic Kidney Disease
- CKD
- AKI
- Hypertension
- Transplant Nephrology
- Dialysis
- Pregnancy
- Vaccination
- Drug Monitoring

Rules must remain completely database-driven.

---

# Phase 3.6 — Event-Driven Architecture

Introduce domain events.

Examples:

```
PatientRegistered

EncounterCompleted

LabResultReceived

BiopsyReported

DiagnosisConfirmed

TreatmentStarted

DrugChanged

FollowUpScheduled

ReminderSent

RecommendationGenerated
```

Use Celery and asynchronous task processing where appropriate.

---

# Phase 3.7 — Multi-Center Registry

Refactor the platform to support:

```
Country
    ↓
Division
    ↓
District
    ↓
Hospital
    ↓
Department
    ↓
Registry
```

Support:

- Multiple hospitals
- Multiple laboratories
- Multiple nephrology units
- Multi-tenant data separation
- Cross-center analytics

No assumptions should limit the platform to a single institution.

---

# Phase 3.8 — Real-Time Analytics

Develop operational dashboards for:

- Patient registry
- Disease distribution
- Treatment utilization
- Laboratory trends
- Follow-up compliance
- Outcomes
- Drug safety
- Research metrics
- Hospital performance

Dashboards should support filtering by center, diagnosis, and time period.

---

# Engineering Rules

For every module:

- Follow Clean Architecture.
- Follow Domain-Driven Design.
- Preserve backward compatibility.
- Generate migrations.
- Generate automated tests.
- Update API documentation.
- Update architecture documentation.

Never bypass the existing service layer.

Never hardcode clinical rules.

---

# Quality Requirements

Every completed module must:

- Pass all existing tests
- Add new automated tests
- Maintain ≥90% overall coverage
- Maintain near-100% coverage for clinical logic
- Generate OpenAPI documentation
- Include audit logging where applicable

No feature is complete without documentation and tests.

---

# Long-Term Vision

The final GDES platform should provide:

- National GN Registry
- Clinical Decision Support
- Explainable AI Recommendations
- Drug Intelligence
- Automated Follow-up
- Clinical Knowledge Management
- Research Platform
- Multi-Center Collaboration
- Population Analytics
- AI-Ready Clinical Infrastructure

---

# Final Instruction

Build the platform incrementally.

Preserve existing functionality.

Prefer extension over replacement.

Every architectural decision should move GDES closer to becoming the world's leading AI-assisted Glomerular Disease Expert System.
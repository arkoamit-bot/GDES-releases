# GDES_V6_DEVELOPMENT_ROADMAP.md

# GDES Version 6.0
## Clinical Intelligence, Automated Patient Management, Follow-up & Research Roadmap

**Status:** Next Major Development Phase

**Audience:** OpenCode Development Team

**Purpose:**
This document defines the development priorities for the next phase of GDES. The software infrastructure is considered mature; future development should focus on enhancing clinical value by improving AI-assisted diagnosis, evidence-based management, automated patient follow-up, and research capabilities. Every new feature should directly contribute to better patient care, improved clinician workflow, or stronger research outcomes.


**Priority:** Highest

**Status:** Next Major Development Phase

---

# Mission

The software platform is now largely complete.

The registry, decision support, knowledge engine, clinical reasoning, pathways, timeline, and research framework are operational.

The next phase is **not** to add more software modules.

The next phase is to transform GDES into a clinically intelligent system that actively assists nephrologists in diagnosis, management, follow-up, and research.

From this point onward, every development task must answer one question:

> **Does this make GDES more useful for clinicians and improve patient care?**

If the answer is **yes**, proceed.

If the answer is **no**, defer it to a future version.

---

# Primary Objectives

The next development phase focuses on four pillars:

1. AI-Assisted Clinical Decision Support
2. Automated Patient Management
3. Intelligent Follow-up
4. Research Automation

These are now the highest priorities.

---

# Objective 1 – Complete the Clinical Workflow

Implement a seamless clinical workflow from first presentation to long-term follow-up.

Target workflow:

```
Patient Registration

↓

Clinical Assessment

↓

Laboratory Review

↓

Imaging

↓

Biopsy

↓

AI Clinical Analysis

↓

Ranked Differential Diagnosis

↓

Suggested Investigations

↓

Clinician Confirms Diagnosis

↓

Evidence-Based Management Plan

↓

Treatment Recommendation

↓

Prescription

↓

Monitoring Plan

↓

Automated Follow-up Schedule

↓

SMS / Email Reminder

↓

Risk Reassessment

↓

Treatment Modification

↓

Outcome Tracking

↓

Research Integration
```

The clinician should never need to switch between disconnected modules.

---

# Objective 2 – AI Differential Diagnosis

After entering demographic, clinical, laboratory, imaging, and biopsy data, GDES should automatically:

- Analyze all available information
- Generate a ranked differential diagnosis
- Display confidence scores
- Explain supporting evidence
- Highlight contradictory findings
- Identify missing information
- Suggest additional investigations

Each recommendation must reference the supporting guideline or evidence source.

---

# Objective 3 – Investigation Recommendation Engine

Based on the current clinical picture and differential diagnosis, automatically recommend additional investigations.

Examples:

- Serology
- Complement studies
- Autoimmune profile
- Viral screening
- Genetic testing
- Repeat biopsy
- Imaging

Each investigation should include:

- Clinical rationale
- Priority
- Expected diagnostic value
- Guideline reference

---

# Objective 4 – Management Engine

After the clinician confirms the diagnosis, GDES should automatically generate a personalized management plan.

Include:

- General supportive care
- Disease-specific therapy
- Immunosuppression recommendations
- Drug doses
- Contraindications
- Monitoring requirements
- Safety precautions
- Vaccination advice
- Lifestyle recommendations

Recommendations must be patient-specific and evidence-based.

---

# Objective 5 – Intelligent Follow-up Engine

Develop a disease-specific follow-up engine.

Automatically generate:

- Next clinic visit
- Laboratory schedule
- Imaging schedule
- Drug monitoring
- Safety monitoring
- Relapse surveillance
- Kidney function monitoring

The interval should adapt according to:

- Disease
- Disease activity
- CKD stage
- Current treatment
- Risk category
- Previous response

---

# Objective 6 – Automated Patient Management

Continuously monitor patient data.

Automatically detect:

- AKI
- CKD progression
- Increasing proteinuria
- Declining eGFR
- Drug toxicity
- Missed appointments
- Overdue laboratory tests
- High-risk patients
- Possible relapse
- Treatment failure

Generate alerts for clinicians without requiring manual review.

---

# Objective 7 – SMS Reminder System

Integrate automated patient reminders.

Examples:

Clinic appointment reminders

Laboratory reminders

Medication monitoring reminders

Missed appointment reminders

Urgent recall notifications

Support multiple communication channels:

- SMS
- Email
- WhatsApp (future)

Messages should be generated automatically from the follow-up engine.

---

# Objective 8 – AI Clinical Assistant

Implement an explainable AI assistant.

The AI should answer questions such as:

- What is the most likely diagnosis?
- Why?
- Which diagnoses should still be considered?
- Which investigations are missing?
- What treatment is recommended?
- What should be monitored?
- When should this patient return?
- What complications are likely?
- Is this patient eligible for research?

Every recommendation must include:

- Clinical reasoning
- Evidence
- Guideline reference
- Confidence score

The clinician always retains final responsibility for decision-making.

---

# Objective 9 – Research Automation

Routine clinical care should automatically populate research datasets.

Automatically generate:

- Longitudinal outcomes
- Disease activity
- Remission status
- Relapse events
- Drug exposure
- Biopsy data
- Survival analyses
- Export-ready datasets

The clinician should not need to enter research data separately.

---

# Objective 10 – Disease Validation

Perform complete validation for every supported disease.

For each disease verify:

- Differential diagnosis
- Suggested investigations
- Management recommendations
- Follow-up schedule
- Monitoring plan
- Relapse pathway
- Remission pathway
- Research variables

Every disease should undergo end-to-end clinical validation.

---

# Objective 11 – Retrospective Clinical Validation

Validate GDES using real historical patient records.

Compare:

- AI diagnosis vs clinician diagnosis
- AI management vs actual management
- AI follow-up vs actual follow-up

Measure:

- Diagnostic agreement
- Treatment agreement
- Follow-up agreement
- Missed diagnoses
- Missed investigations

Document discrepancies and improve the knowledge base.

---

# Objective 12 – Pilot Deployment Readiness

Prepare GDES for clinical use.

Verify:

- End-to-end workflow
- Automated management
- Automated follow-up
- SMS reminders
- Research integration
- Dashboard usability
- Clinical performance

The system should be ready for pilot implementation in a nephrology clinic.

---

# Development Principles

Before implementing any new feature, ask:

- Does this improve clinical decision-making?
- Does this reduce clinician workload?
- Does this improve patient safety?
- Does this improve follow-up?
- Does this improve adherence to guidelines?
- Does this improve research quality?

If the answer is **yes**, implement it.

If the answer is **no**, postpone it.

---

# Success Criteria

This phase will be considered complete when GDES can:

- Accept structured clinical data.
- Generate AI-supported differential diagnoses.
- Recommend appropriate investigations.
- Assist clinicians in confirming diagnoses.
- Produce personalized evidence-based management plans.
- Automatically generate monitoring and follow-up schedules.
- Send automated patient reminders.
- Continuously reassess patients as new data become available.
- Identify research opportunities automatically.
- Demonstrate measurable improvement in clinician workflow and patient management.

The goal is to establish GDES as an integrated Clinical Decision Support and Disease Management Platform that combines a longitudinal registry, explainable AI, automated follow-up, and research intelligence into a single seamless system for glomerular diseases.
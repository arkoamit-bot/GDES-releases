# GDES_BGDDR_UI_INTEGRATION.md

# GDES + BGDDR Unified Clinical Platform
## Complete System Integration Under a Single User Interface

**Project:** Glomerular Disease Expert System (GDES)

**Priority:** Critical

**Status:** Architecture Integration

---

# Objective

The project currently contains two mature systems:

1. BGDDR
   (Registry, encounters, laboratory, pathology, treatment, research)

2. GDES
   (Knowledge base, clinical reasoning, decision support, pathways, follow-up)

These systems must no longer appear as separate applications.

The objective is to transform them into **one seamless clinical platform**.

The clinician should never think:

"I am using BGDDR."

or

"I am using GDES."

Instead, they should simply use

**GDES — Glomerular Disease Expert System**

where the registry, knowledge engine, decision support, follow-up, and research function as one integrated workflow.

---

# Guiding Principle

BGDDR is the operational clinical registry.

GDES is the clinical intelligence layer.

They are not competitors.

They are complementary components of the same platform.

The registry captures data.

The intelligence layer interprets data.

The follow-up engine manages patients.

The research engine learns from data.

Everything must appear as one product.

---

# Integration Philosophy

Never duplicate information.

Never duplicate screens.

Never duplicate workflows.

Never create parallel modules.

Reuse existing BGDDR components whenever possible.

Enhance them with GDES intelligence.

---

# Unified Branding

Throughout the application:

Replace visible references to:

BGDDR

with

GDES

except where historical compatibility requires otherwise.

Window title

Application title

Navigation

Documentation

PDF reports

Export headers

Login page

Dashboard

All should consistently use:

Glomerular Disease Expert System (GDES)

---

# Single Navigation Structure

Create one unified navigation menu.

Example:

Dashboard

Patients

Clinical Encounters

Clinical Assessment

Laboratory

Biopsy & Pathology

Clinical Reasoning

Treatment

Prescriptions

Follow-up

Timeline

Research

Knowledge Base

Administration

No separate "BGDDR" menu.

No separate "GDES" menu.

Everything belongs to one workflow.

---

# Unified Patient Workspace

Every patient should have one integrated workspace.

Suggested tabs:

Overview

Clinical Summary

Timeline

Laboratory

Pathology

Treatments

Clinical Reasoning

Decision Support

Follow-up

Research

Audit

No duplicate patient pages.

No duplicate patient dashboards.

Everything should reference the same Patient model.

---

# Clinical Workflow Integration

A clinician should be able to complete an entire consultation without switching modules.

Workflow:

Patient

↓

Encounter

↓

Clinical Assessment

↓

Laboratory Review

↓

Biopsy Review

↓

Clinical Reasoning

↓

Treatment Recommendation

↓

Prescription

↓

Follow-up Plan

↓

Research Update

Every step should occur inside the same patient workspace.

---

# Registry Integration

The registry remains the single source of truth.

Patient

Encounter

Laboratory

Biopsy

Treatment

Outcome

Research

should continue to live in the registry.

The GDES engine should read these objects.

It should not create duplicate copies.

---

# Clinical Reasoning Integration

When new data are entered:

Automatically:

Update Clinical Profile

Update Differential Diagnosis

Update Risk Assessment

Update Follow-up Plan

Update Timeline

Update Research Dataset

The clinician should never manually press:

"Run GDES"

Reasoning should occur automatically.

---

# Unified Dashboard

Create one dashboard.

Display:

Today's patients

Patients requiring review

High-risk patients

Overdue follow-up

Recent laboratory alerts

Drug monitoring

Clinical recommendations

Pending pathology

Research recruitment

Knowledge alerts

The dashboard should combine information from every subsystem.

---

# Unified Timeline

The timeline should include:

Registration

Encounter

Laboratory

Biopsy

Diagnosis

Clinical reasoning

Treatment

Prescription

Outcome

Research events

Notification events

Everything should appear chronologically.

---

# Unified Search

Searching a patient should immediately expose:

Demographics

Diagnosis

Current disease phase

Risk level

Latest laboratory results

Current treatment

Pending follow-up

Clinical alerts

Research eligibility

The user should never search multiple systems.

---

# Remove Duplicate Screens

Audit the application.

Identify every duplicated page.

Examples:

Duplicate patient lists

Duplicate dashboards

Duplicate encounter summaries

Duplicate laboratory viewers

Duplicate pathology displays

Replace with one authoritative screen.

---

# Remove Duplicate Logic

Review services.

If BGDDR and GDES perform similar calculations:

Merge them.

Examples:

eGFR

Proteinuria calculations

Disease activity

Risk scoring

Follow-up interval

Outcome calculation

Maintain one implementation.

---

# Remove Duplicate APIs

If duplicate REST endpoints exist:

Consolidate them.

Maintain backwards compatibility where necessary.

Future development should target one endpoint.

---

# UI Consistency

Use one visual language.

Consistent:

Colors

Icons

Typography

Cards

Buttons

Tables

Forms

Alerts

Charts

Spacing

Dark/light themes

The application should feel like a single product.

---

# Event Integration

All modules should communicate through the same event architecture.

Examples:

EncounterCreated

↓

ClinicalAssessmentUpdated

↓

LabResultReceived

↓

BiopsyReviewed

↓

ClinicalReasoningUpdated

↓

TreatmentChanged

↓

FollowUpGenerated

↓

TimelineUpdated

↓

ResearchUpdated

↓

NotificationQueued

No isolated workflows.

---

# Documentation

Produce:

SYSTEM_INTEGRATION_REPORT.md

UI_INTEGRATION_REPORT.md

DUPLICATE_COMPONENT_AUDIT.md

EVENT_INTEGRATION_REPORT.md

WORKFLOW_VALIDATION_REPORT.md

Every integration decision should be documented.

---

# Acceptance Criteria

The integration is complete only when:

✓ There is one patient workspace.

✓ There is one navigation system.

✓ There is one dashboard.

✓ Registry and decision support operate together.

✓ Clinical reasoning runs automatically.

✓ Timeline is unified.

✓ Duplicate screens are eliminated.

✓ Duplicate services are consolidated.

✓ Duplicate APIs are removed or deprecated.

✓ Clinicians never perceive BGDDR and GDES as separate systems.

---

# Final Instruction to OpenCode

Treat BGDDR and GDES as two layers of the same platform.

BGDDR provides structured clinical data.

GDES provides clinical intelligence.

Your objective is **not** to merge code indiscriminately.

Your objective is to integrate workflows, reuse existing components, eliminate duplication, and present a single, coherent clinical application.

At every step ask:

- Does this reduce duplication?
- Does this simplify the clinician's workflow?
- Does this preserve a single source of truth?
- Does this improve maintainability?

If the answer is yes, proceed.

If the answer is no, redesign the approach before implementing.

The final result should be a seamless Glomerular Disease Expert System where clinicians experience one integrated product rather than two connected applications.
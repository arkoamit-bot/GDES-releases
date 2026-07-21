# GDES_V7_1_DESKTOP_REVIEW_AND_REBUILD.md

# GDES V7.1 Desktop Review and Rebuild

## Objective

The current desktop installer and executable do not faithfully reproduce the original BGDDR/GDES application. Several important clinical workflows and UI behaviors have regressed.

This task is **NOT** to add new features.

This is a **quality assurance, regression review, and production rebuild**.

The goal is to produce a new production-quality executable named **GDES.exe** that behaves exactly like the original validated application while preserving all new GDES capabilities.

---

# Primary Objectives

1. Perform a complete regression review of the desktop application.
2. Compare every workflow against the original validated BGDDR build.
3. Restore all missing functionality.
4. Remove duplicate data entry.
5. Preserve all clinical information across the patient journey.
6. Build a completely new executable named:

```
GDES.exe
```

and a new installer

```
Setup_GDES_7.1.exe
```

Only after every issue has been verified and corrected.

---

# Part 1 — Full Functional Regression Review

Perform a page-by-page comparison with the original validated application.

Review every module including:

- Dashboard
- Registration
- Baseline
- Clinical Assessment
- Investigations
- Pathology
- GN Diagnosis
- Treatment
- Follow-up
- Prescription
- Clinical Reasoning
- Research
- Reports
- Knowledge Base

Nothing should be accepted until behavior matches the original validated workflow.

---

# Part 2 — Fix Clinical Data Errors

## Height displayed as Weight

Current issue

Baseline Height is being displayed as Weight on:

- Dashboard
- Prescription

This is a critical clinical bug.

Requirements

- Verify all field mappings.
- Verify model → serializer → template → UI mapping.
- Confirm Height always displays Height.
- Confirm Weight always displays Weight.
- Review every template and report for similar mapping errors.

---

## Biopsy Status Incorrect

Current issue

Patients with biopsy completed are still displayed as:

```
Biopsy: Not Done
```

Requirements

Review:

- biopsy model
- pathology model
- encounter linkage
- dashboard
- patient summary
- clinical reasoning
- reports

The displayed biopsy status must always reflect the actual stored clinical data.

---

# Part 3 — Restore Original Clinical Workflow

The current executable does not fully represent the original validated BGDDR application.

Review the original implementation and verify that all of the following are preserved:

- patient registration workflow
- baseline workflow
- diagnosis workflow
- pathology workflow
- prescription workflow
- follow-up workflow
- dashboard summaries
- reports
- registry functionality

Any missing functionality must be restored.

---

# Part 4 — Remove Duplicate Clinical Data Entry

Current problem

Some information must be entered multiple times.

Example

GN Diagnosis exists in:

- Baseline
- Follow-up

This is incorrect.

Clinical diagnosis should be entered once and reused throughout the system.

---

## Required Design Rule

Clinical information should follow the patient longitudinally.

Example

Baseline

```
Diagnosis

↓

IgA Nephropathy
```

Follow-up

Automatically display

```
Current Diagnosis

IgA Nephropathy
```

unless changed by the clinician.

The clinician should only update the diagnosis when clinically appropriate.

Never force duplicate entry.

---

## Apply This Rule To

Review every duplicated field including:

- GN diagnosis
- CKD stage
- biopsy status
- pathology diagnosis
- diabetes
- hypertension
- smoking
- hepatitis status
- autoimmune disease
- transplant status

Any information that remains valid across visits should automatically populate future encounters.

Follow-up forms should inherit baseline information and allow updates only when necessary.

---

# Part 5 — Longitudinal Clinical Model

Review the entire patient journey.

Clinical data should be classified as either:

## Static

Entered once

Examples

- sex
- DOB
- blood group
- ethnicity

---

## Semi-static

Rarely changes

Examples

- GN diagnosis
- biopsy diagnosis
- transplant history
- genetic diagnosis

Should automatically appear in every future encounter.

---

## Dynamic

Changes every visit

Examples

- blood pressure
- weight
- serum creatinine
- eGFR
- proteinuria
- medications
- adverse events

Only these should require routine follow-up entry.

---

# Part 6 — UI Consistency

Review every screen.

Verify

- field labels
- field order
- navigation
- dashboard summaries
- colors
- icons
- patient timeline
- clinical cards

The desktop application should feel like one integrated clinical system.

---

# Part 7 — Build Verification

Before building the new executable verify

- all migrations
- all templates
- all URLs
- all serializers
- all APIs
- all Knowledge Base loading
- all management commands
- all desktop startup checks

No missing assets.

No broken templates.

No placeholder pages.

No duplicate menu items.

---

# Part 8 — Desktop Acceptance Testing

Test complete patient workflow.

Create a new patient.

Perform

Registration

↓

Baseline

↓

Biopsy

↓

GN Diagnosis

↓

Clinical Reasoning

↓

Treatment

↓

Prescription

↓

Follow-up

↓

Second Follow-up

↓

Reports

↓

Knowledge Traceability

Confirm

- diagnosis carries forward
- biopsy carries forward
- prescriptions work
- dashboard updates correctly
- follow-up reflects previous data
- no duplicate data entry
- no incorrect field mapping

---

# Part 9 — Final Build

Only after all issues are resolved.

Build

```
GDES.exe
```

using the approved desktop architecture.

Create

```
Setup_GDES_7.1.exe
```

using the existing installer framework.

---

# Deliverables

Provide:

1. GDES.exe
2. Setup_GDES_7.1.exe
3. Regression Review Report
4. Clinical Workflow Validation Report
5. List of all bugs fixed
6. Screenshots comparing original vs rebuilt application
7. Final Desktop Release Report

---

# Success Criteria

The rebuilt desktop application must:

- Faithfully reproduce the original validated BGDDR functionality.
- Preserve all new GDES Clinical Decision Support features.
- Eliminate duplicate clinical data entry.
- Correct all clinical data mapping errors.
- Support a true longitudinal patient record.
- Be suitable for real-world clinical pilot deployment.


# Version Information

Current Release

```
GDES Desktop v6.6.1
```

Target Release

```
GDES Desktop v6.6.2
```

This is a maintenance and stabilization release.

No new clinical functionality should be added unless required to restore the original validated behavior.

The primary objective is to eliminate regressions and ensure that the desktop executable faithfully reproduces the validated BGDDR/GDES workflow.

After all issues are resolved:

- Rename the executable to:

```
GDES.exe
```

- Produce the installer:

```
Setup_GDES_6.6.2.exe
```

Update all version information consistently in:

- Application About dialog
- Desktop launcher
- Installer
- Release notes
- Build scripts
- Version metadata
- File properties

# Mandatory Regression Checklist

Before creating GDES.exe, verify every module against the original validated application.

Checklist:

- Registration
- Dashboard
- Baseline Assessment
- GN Diagnosis
- Pathology/Biopsy
- Investigations
- Clinical Reasoning
- Management Plan
- Prescription
- Follow-up
- Reports
- Research
- Knowledge Base
- Clinical Governance
- Desktop Startup
- Backup
- Restore
- Printing
- Export

No module should regress from the original implementation.

The executable should only be rebuilt after every checklist item is verified.
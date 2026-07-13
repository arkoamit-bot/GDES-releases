# GDES_USER_MANUAL_AND_PATIENT_JOURNEY.md

# GDES Version 5.0
## Comprehensive User Manual & End-to-End Clinical Workflow Guide

**Priority:** High

**Objective**

Develop a comprehensive, clinician-oriented User Manual that explains how to use every major module of the Glomerular Disease Expert System (GDES) in routine clinical practice.

This document is intended for nephrologists, fellows, residents, nurses, research coordinators, data managers, and hospital administrators. It should be written as a practical guide rather than a technical document.

The manual must demonstrate how GDES supports clinical decision-making, automates patient management, improves follow-up, and strengthens research.

---

# Primary Deliverable

Create:

```
docs/GDES_USER_MANUAL.md
```

and, if appropriate,

```
docs/GDES_USER_MANUAL.pdf
```

The document should be professionally formatted with:

- Table of contents
- Figures/screenshots placeholders
- Clinical tips
- Workflow diagrams (Markdown or Mermaid)
- Tables
- Call-out boxes for important notes
- Cross-references between sections

---

# Overall Structure

## Chapter 1 – Introduction

Describe:

- What GDES is
- Purpose of the platform
- Target users
- Clinical objectives
- Research objectives
- How GDES differs from a traditional registry

Explain that GDES integrates:

- Clinical Registry
- Decision Support
- Knowledge Engine
- Automated Follow-up
- Research Platform

into a single clinical workflow.

---

## Chapter 2 – System Overview

Describe each major module.

Examples:

Dashboard

Patient Registry

Clinical Encounters

Clinical Assessment

Laboratory

Pathology

Clinical Reasoning

Decision Support

Treatment

Prescriptions

Follow-up

Timeline

Knowledge Base

Research

Administration

For each module explain:

Purpose

Inputs

Outputs

Automatic processes

Interactions with other modules

---

## Chapter 3 – Complete Patient Journey

This chapter should become the centerpiece of the manual.

Use one realistic patient from first presentation until long-term follow-up.

Example:

35-year-old male

Progressive edema

Hypertension

Proteinuria

Microscopic hematuria

Reduced eGFR

Ultimately diagnosed with IgA Nephropathy

Follow the patient through every stage.

---

### Step 1

Patient Registration

Demographics

Medical history

Comorbidities

Family history

Consent

Automatic actions

Research eligibility

Timeline entry

Audit log

---

### Step 2

Baseline Assessment

Clinical examination

Blood pressure

Weight

BMI

Chief complaint

Syndrome classification

Automatic calculations

eGFR

BSA

KDIGO stage

Proteinuria

Risk score

---

### Step 3

Laboratory Entry

Describe entering:

Creatinine

Albumin

UPCR

Urinalysis

CBC

Complement

ANA

ANCA

Automatic actions:

Reference ranges

Trend analysis

Critical alerts

Timeline updates

Research dataset updates

---

### Step 4

Biopsy

Describe:

Entering pathology

Oxford MEST-C

Diagnosis

Automatic actions:

Disease classification

Knowledge engine activation

Timeline update

Clinical reasoning trigger

---

### Step 5

Clinical Reasoning

Show how GDES automatically:

Extracts patient features

Matches knowledge base rules

Calculates differential diagnosis

Computes confidence

Identifies information gaps

Produces reasoning chain

Assigns phenotype

Assigns urgency

Recommends investigations

Produces treatment suggestions

Explain every automatically generated output.

---

### Step 6

Treatment Planning

Describe:

Selecting medications

Dose adjustments

Contraindications

Drug monitoring

Decision support recommendations

Explain how clinician overrides are recorded.

---

### Step 7

Automatic Follow-up Planning

This chapter should be extremely detailed.

Describe exactly how GDES generates:

Next visit

Laboratory schedule

Medication monitoring

Safety monitoring

Research visits

Timeline updates

Escalation rules

Risk-based follow-up intervals

Explain every automatically generated task.

---

### Step 8

Automatic Patient Management

Demonstrate how GDES continuously manages the patient.

Examples:

New creatinine result arrives

↓

Trend analysis runs

↓

eGFR decline detected

↓

Risk recalculated

↓

Clinical reasoning reruns

↓

Follow-up interval shortened

↓

Clinician dashboard updated

↓

Notification queued

↓

Timeline updated

↓

Research dataset updated

This workflow should be illustrated step-by-step.

---

### Step 9

Relapse Scenario

Create a realistic relapse.

Show:

New proteinuria

Worsening renal function

Clinical reassessment

Updated reasoning

Treatment adjustment

Automatic follow-up changes

Escalation

Outcome tracking

---

### Step 10

Long-term Follow-up

Illustrate management over several years.

Include:

Routine monitoring

Medication changes

Remission

Relapse

Research participation

Outcome reporting

Demonstrate how GDES maintains a complete longitudinal record.

---

# Automated Management Section

Provide a dedicated chapter explaining every automated process.

Examples:

Automatic eGFR calculation

Automatic BMI

Automatic KDIGO staging

Automatic CKD progression detection

Automatic AKI detection

Automatic proteinuria trend

Automatic disease phase update

Automatic risk assessment

Automatic reasoning

Automatic treatment recommendation

Automatic follow-up scheduling

Automatic clinician worklist generation

Automatic timeline updates

Automatic research synchronization

Automatic audit logging

Automatic event generation

Automatic reminders

For every automation explain:

Trigger

Processing

Output

Clinical benefit

---

# Automated Follow-up Section

Describe in detail how the follow-up engine works.

Include:

Disease-specific schedules

Risk-based intervals

Medication monitoring

Laboratory monitoring

Missed visit detection

Escalation rules

Notification generation

Clinician dashboard integration

Patient communication workflow

Explain exactly how the system reduces loss to follow-up.

---

# Research Workflow

Describe how clinical care automatically contributes to research.

Examples:

Automatic cohort inclusion

Outcome tracking

Research exports

Survival analysis

Longitudinal data collection

Audit trail

Publication-quality datasets

---

# Clinical Decision Support

Explain:

Evidence grades

Guideline references

Reasoning chain

Confidence

Limitations

Clinician responsibility

Override workflow

---

# Practical Examples

Include multiple case studies.

Examples:

IgA Nephropathy

Membranous Nephropathy

FSGS

Minimal Change Disease

Lupus Nephritis

ANCA Vasculitis

MPGN

C3 Glomerulopathy

Kidney Transplant Recipient

For each case explain:

Presentation

Data entry

Reasoning

Treatment

Follow-up

Outcome

---

# Illustrations

Include placeholders for screenshots of:

Dashboard

Patient Summary

Clinical Assessment

Laboratory Entry

Pathology Entry

Clinical Reasoning

Treatment Recommendation

Follow-up Plan

Timeline

Research Dashboard

---

# Audience

The manual should be understandable by:

Nephrologists

Residents

Medical Officers

Research Coordinators

Nurses

Data Managers

Hospital Administrators

No software engineering knowledge should be required.

---

# Writing Style

The document should read like the user manual of a commercial clinical information system.

Avoid code.

Avoid implementation details.

Focus on:

Clinical workflow

Ease of use

Automation

Patient safety

Research integration

Decision support

---

# Final Deliverable

Produce a polished manual of approximately 150–250 pages (or equivalent Markdown content) that can serve as the official user guide for GDES.

The manual should clearly demonstrate that GDES is not merely a patient registry, but an intelligent clinical platform that supports diagnosis, automated patient management, structured follow-up, and research throughout the entire patient journey.
# GDES_V6_5_CLAUDE_REVIEW_PREPARATION.md

# GDES Version 6.5
## Claude Review Preparation & Clinical Governance

**Project:** Glomerular Disease Expert System (GDES)

**Audience:** OpenCode Development Team

**Priority:** CRITICAL

**Objective:** Prepare GDES for an independent architecture and clinical review by Claude Code before initiating the real-world pilot.

---

# Background

The software platform has now reached a mature stage.

Major milestones have been completed:

- Registry platform
- Clinical workflow
- Decision support
- Knowledge platform
- Clinical reasoning engine
- Automated management
- Follow-up engine
- Research framework
- Integration
- Production readiness

The next step is **not further feature development.**

Before beginning pilot implementation, the entire system should undergo one final stabilization and governance phase.

The goal is to present Claude Code with a clean, coherent, well-documented project that represents the best possible version of GDES.

Claude should function as an **independent software architect and technical reviewer**, not as the primary developer.

---

# Development Freeze

Effective immediately:

## No New Features

Do not add:

- new diseases
- new modules
- UI redesigns
- infrastructure changes
- experimental AI features

Only perform:

- bug fixes
- consistency improvements
- documentation
- governance implementation
- architectural cleanup

This release should become:

**GDES Version 6.5 Release Candidate (RC1)**

---

# Objective 1 — Complete Clinical Governance Layer

This is now the highest priority.

Every AI-generated recommendation must become completely transparent and auditable.

For every recommendation, provide:

| Field | Description |
|--------|-------------|
| Guideline | Supporting clinical guideline |
| Guideline Version | Version/year |
| Section | Chapter or section number |
| Recommendation ID | Guideline recommendation identifier |
| Evidence Grade | GRADE recommendation |
| Evidence Source | Trial, review or publication |
| Confidence Score | AI confidence |
| Knowledge Rule ID | Internal KB identifier |
| Knowledge Version | Knowledge base version |
| Date Validated | Last validation date |
| Next Review Date | Scheduled review |
| Expert Reviewer | Clinical reviewer |
| Approval Status | Draft / Approved / Retired |
| Explanation | Human-readable reasoning |
| Override Allowed | Yes/No |

Every recommendation should expose this information.

No recommendation should function as a black box.

---

# Objective 2 — Knowledge Governance Dashboard

Create a governance dashboard for the knowledge platform.

Display:

- Active rules
- Draft rules
- Retired rules
- Rules awaiting review
- Rules lacking evidence
- Rules lacking guideline linkage
- Disease completeness
- Knowledge version
- Last validation date
- Reviewer assignments
- Rule usage statistics
- Clinician override statistics

The dashboard should support continuous quality improvement.

---

# Objective 3 — Final System Consistency Audit

Perform one final architecture-wide audit.

Verify:

## Domain

- no duplicated entities
- no duplicated calculations
- one source of truth
- consistent naming

## Services

- one reasoning engine
- one follow-up engine
- one management engine

## Database

- no orphan tables
- no unused models
- no dead migrations

## API

- no duplicated endpoints
- consistent responses
- proper versioning

## UI

- unified navigation
- patient dashboard as primary workspace
- no isolated pages

## Code

- remove dead code
- remove obsolete utilities
- remove deprecated services

Document every finding.

---

# Objective 4 — Validate Complete Patient Journey

Using representative patients, verify the complete workflow.

For each disease:

- Registration
- Clinical assessment
- Laboratory review
- Imaging
- Biopsy
- AI differential diagnosis
- Suggested investigations
- Diagnosis confirmation
- Management plan
- Prescription
- Monitoring
- Follow-up schedule
- SMS generation
- Follow-up visit
- Outcome recording
- Research integration

Suggested validation diseases:

- IgA Nephropathy
- Membranous Nephropathy
- FSGS
- Minimal Change Disease
- Lupus Nephritis
- ANCA Vasculitis

The workflow must be seamless.

---

# Objective 5 — Single-PC Pilot Optimization

The first pilot will run on a **single Windows PC**.

Therefore:

Keep SQLite as the production database.

Do NOT migrate to PostgreSQL during the pilot.

Disable unnecessary enterprise infrastructure where appropriate.

Optimize for:

- stability
- simplicity
- reliability
- minimal installation
- automatic backup
- automatic restore
- offline operation

Enterprise deployment can be addressed after successful pilot validation.

---

# Objective 6 — Documentation Cleanup

Ensure documentation accurately reflects the implemented system.

Required documents:

- PROJECT_STATUS.md
- SYSTEM_ARCHITECTURE.md
- CLINICAL_GOVERNANCE.md
- PILOT_DEPLOYMENT_GUIDE.md
- USER_MANUAL.md
- KNOWN_LIMITATIONS.md
- RELEASE_NOTES.md

Documentation should be internally consistent.

---

# Objective 7 — Prepare Claude Review Package

Prepare a review package for Claude Code.

Include:

## Project Overview

- objectives
- architecture
- workflow
- technology stack

## Current Status

- completed work
- known limitations
- pilot scope

## Review Expectations

Request Claude to review:

- architecture
- domain model
- software quality
- maintainability
- technical debt
- security
- workflow integration
- AI reasoning
- knowledge governance
- follow-up engine
- research automation

Claude should identify:

- hidden defects
- architectural weaknesses
- scalability concerns
- maintainability issues
- workflow inconsistencies
- unnecessary complexity

Claude should NOT introduce unnecessary redesigns.

---

# Objective 8 — Pilot Success Criteria

Define measurable success before the first patient.

## Clinical

- Diagnostic agreement
- Guideline adherence
- Treatment agreement
- Follow-up compliance

## Operational

- Consultation time
- Ease of use
- Clinician satisfaction
- System stability

## Research

- Registry completeness
- Missing data rate
- Automatic dataset generation
- Study recruitment support

These metrics should be collected throughout the pilot.

---

# Deliverables

Produce:

- GDES_SYSTEM_CONSISTENCY_AUDIT.md
- GDES_CLINICAL_GOVERNANCE.md
- GDES_KNOWLEDGE_GOVERNANCE.md
- GDES_PILOT_DEPLOYMENT_GUIDE.md
- GDES_RELEASE_CANDIDATE_REPORT.md
- GDES_CLAUDE_REVIEW_REQUEST.md

---

# Important Pilot Decision

The initial pilot is intentionally designed as a **single-site, single-PC deployment**.

During this phase:

- SQLite remains the production database.
- Desktop deployment remains the primary target.
- PostgreSQL, Redis, distributed services, and multi-center synchronization are deferred to a later version after successful pilot validation.

The objective is to validate clinical usefulness rather than enterprise scalability.

---

# Definition of Success

Version 6.5 will be considered complete when:

- Clinical Governance is fully implemented.
- Every AI recommendation is transparent and evidence-linked.
- The knowledge platform is governed and auditable.
- The system has passed a final consistency audit.
- The complete patient journey has been validated.
- Documentation is complete and internally consistent.
- The codebase is frozen as Version 6.5 RC1.
- Claude Code can perform an independent review without requiring architectural clarification.
- The system is ready for a real-world pilot in the nephrology clinic.

---

# Guiding Principle

The objective is **not to make GDES larger**.

The objective is to make GDES **clinically trustworthy, internally consistent, transparent, maintainable, and ready for real-world patient care.**

Every change during this phase must improve one or more of the following:

- Clinical safety
- Clinical transparency
- Guideline adherence
- Knowledge governance
- Software quality
- Pilot readiness

If a proposed change does not contribute to these goals, defer it to a future version.
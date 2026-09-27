# OPENCODE_AUTONOMOUS_DEVELOPMENT_PROTOCOL.md

**Project:** Glomerular Disease Expert System (GDES)

**Version:** 2.0

**Status:** Master Development Protocol

**Target:** OpenCode Autonomous Development

**Priority:** Mandatory

---

# Mission

OpenCode is not merely a code generator.

OpenCode acts as the **Technical Lead**, **Software Architect**, **Quality Assurance Lead**, and **Continuous Improvement Engineer** for GDES.

Every implementation decision must improve the long-term quality of the project.

The objective is to build **the world's most intelligent nephrology clinical decision support platform**, while keeping the codebase simple, maintainable, and clinically trustworthy.

---

# Core Philosophy

## Build Better Intelligence, Not Bigger Software

Success is measured by

- Better clinical recommendations
- Better evidence
- Better explainability
- Better clinician workflow
- Better maintainability
- Better patient safety

Never measure success by

- Number of modules
- Number of models
- Number of files
- Lines of code

---

# Golden Rules

Before implementing anything, ask:

1. Does this improve clinical intelligence?
2. Does this improve patient safety?
3. Does this simplify the architecture?
4. Can existing code be reused?
5. Will another developer understand this in six months?
6. Does it reduce technical debt?

If any answer is **No**, redesign before implementation.

---

# Development Lifecycle

Every task shall follow this lifecycle.

```
Request

↓

Understand

↓

Analyze Existing Code

↓

Architecture Review

↓

Implementation Plan

↓

Risk Assessment

↓

Implementation

↓

Refactoring

↓

Testing

↓

Self Review

↓

Clinical Review

↓

Documentation

↓

Repository Health Check

↓

Await Approval
```

No phase may be skipped.

---

# STEP 1 — Understand the Problem

Before coding determine

- What is the actual problem?
- Which clinical workflow is affected?
- Which users benefit?
- Which modules are involved?
- Is this solving a real clinical need?

Never implement features without understanding the clinical objective.

---

# STEP 2 — Analyze Existing Code

Before creating

- New app
- New model
- New service
- New API
- New utility
- New background task

Search the repository.

Questions

- Can existing code solve this?
- Can an existing service be extended?
- Can an existing model be expanded?
- Can duplicate logic be removed?
- Can this be implemented with less complexity?

Refactor first.

Build second.

---

# STEP 3 — Architecture Review

Evaluate

- DDD compliance
- Clean Architecture compliance
- SOLID principles
- Separation of concerns
- Reusability
- Maintainability

Reject designs that increase unnecessary complexity.

---

# STEP 4 — Self Planning

Produce an internal implementation plan before coding.

The plan must include

- Objectives
- Files affected
- Existing components to reuse
- Database impact
- API impact
- Security impact
- Performance impact
- Clinical impact
- Testing strategy
- Rollback strategy
- Estimated complexity

Do not begin implementation until the plan is complete.

---

# STEP 5 — Simplicity Check

Ask repeatedly

> Can this solution be simpler?

Continue simplifying until no further simplification is possible.

---

# STEP 6 — Clinical Intelligence Check

Every implementation must improve one or more of

- Clinical reasoning
- Evidence quality
- Explainability
- Guideline compliance
- Patient safety
- Workflow efficiency
- Knowledge evolution

If not, reject the implementation.

---

# STEP 7 — Cost Analysis

Estimate

- Database growth
- CPU usage
- Memory usage
- API costs
- Token usage
- Storage
- Background jobs
- Long-term maintenance

Choose the most efficient solution.

---

# STEP 8 — Implementation

Code must be

- Small
- Modular
- Reusable
- Type hinted
- Documented
- Tested

Avoid large commits.

---

# STEP 9 — Immediate Refactoring

Immediately after implementation

Search for

- Duplicate code
- Dead code
- Unused imports
- Unused models
- Duplicate SQL
- Duplicate serializers
- Duplicate utilities
- Large methods
- Complex logic

Refactor before continuing.

---

# STEP 10 — Automated Testing

Every feature requires

- Unit tests
- Integration tests
- Failure tests
- Regression tests
- Performance tests
- Security tests

Target

**95%+ coverage**

No feature is complete without tests.

---

# STEP 11 — Self Review

Review the implementation as an independent senior software architect.

Questions

- Is this over-engineered?
- Can it be simplified?
- Is the architecture clean?
- Is the code readable?
- Is technical debt reduced?
- Is reuse maximized?

Refactor if necessary.

---

# STEP 12 — Clinical Review

Review as a nephrologist.

Questions

- Does this improve clinical decision-making?
- Does it improve patient safety?
- Is it evidence-based?
- Is it explainable?
- Does it reduce clinician workload?
- Would I trust this in clinical practice?

If not, improve it.

---

# AI Usage Policy

GPT is

- Evidence reviewer
- Clinical reasoning assistant
- Explanation generator
- Summarization engine

GPT is **NOT**

- Primary decision maker
- Replacement for clinical guidelines
- Replacement for the Knowledge Engine

---

# Evidence Priority

Always prioritize

1. GDES Knowledge Base
2. KDIGO
3. ERA
4. ASN
5. ISN
6. NKF/KDOQI
7. PubMed
8. Europe PMC
9. OpenAlex
10. CrossRef
11. GPT Review

External AI validates.

Internal knowledge decides.

---

# Vera Policy

Vera is an optional expert consultant.

Never make GDES dependent upon Vera.

Use Vera only for

- Rare diseases
- Complex GN
- Conflicting evidence
- Difficult clinical decisions

GDES must function fully without Vera.

---

# Repository Health

Every sprint shall improve

- Maintainability
- Test coverage
- Performance
- Documentation
- Clinical intelligence

Technical debt should continuously decrease.

---

# Sprint Planning

Before every sprint

Review

- Outstanding bugs
- Technical debt
- Performance bottlenecks
- Clinical feedback
- Knowledge gaps
- User workflow
- Architecture

Feature requests alone must never determine sprint priorities.

---

# Success Metrics

Measure

- Clinical accuracy
- Recommendation quality
- Guideline compliance
- Clinician trust
- Evidence quality
- Maintainability
- Performance
- Repository health

Never measure

- Number of files
- Number of models
- Number of apps
- Lines of code

---

# ======================================================================
# ARCHITECTURE CONSOLIDATION SPRINT (MANDATORY)
# ======================================================================

## Purpose

To prevent uncontrolled architectural growth.

To continuously simplify the codebase.

To reduce technical debt.

To improve long-term maintainability.

Feature development pauses during this sprint except for critical bug fixes.

---

# Frequency

Run an Architecture Consolidation Sprint

- Every 5–10 development sprints

OR

- Before every major release

OR

- After significant architectural changes

---

# Primary Objectives

- Reduce technical debt
- Simplify architecture
- Improve maintainability
- Increase performance
- Improve testing
- Improve clinical intelligence
- Improve repository health

---

# Repository Audit

Review the entire repository.

Evaluate

- Django apps
- Models
- Services
- APIs
- Templates
- JavaScript
- Background jobs
- Utilities
- Tests
- Documentation

Generate a Repository Health Report.

---

# Architecture Review

Review every application.

Questions

- Does this app still have a clear responsibility?
- Can it be merged?
- Can duplicated logic be removed?
- Does it still comply with DDD?

Recommend consolidation where appropriate.

---

# Model Review

Review every model.

Identify

- Unused fields
- Duplicate entities
- Incorrect relationships
- Missing indexes
- Poor constraints
- Migration opportunities

Prefer extending existing models.

Avoid unnecessary new models.

---

# Service Review

Review every service.

Detect

- Duplicate business logic
- Circular dependencies
- Large service classes
- Low cohesion
- Tight coupling

Refactor aggressively.

---

# API Review

Review every endpoint.

Identify

- Duplicate APIs
- Slow queries
- Large payloads
- Security improvements
- Missing validation
- Unused endpoints

---

# Performance Review

Measure

- Query count
- N+1 queries
- Memory usage
- Cache effectiveness
- API latency
- Background job duration
- Provider latency

Generate optimization recommendations.

---

# AI Review

Review

- Prompt quality
- Token usage
- Cost
- Latency
- Hallucination risk

Remove unnecessary AI calls.

Only use AI where measurable clinical value exists.

---

# Clinical Intelligence Review

Evaluate

- Recommendation quality
- Explainability
- Evidence quality
- Confidence calculation
- Learning effectiveness
- Guideline compliance
- Patient safety

Prioritize reasoning improvements.

---

# Evidence Review

Audit

- Knowledge freshness
- Evidence age
- Guideline versions
- Literature coverage
- Knowledge gaps

Automatically identify recommendations requiring review.

---

# Code Quality Review

Automatically detect

- Dead code
- Duplicate logic
- Unused imports
- Large methods
- Complex functions
- Duplicate serializers
- Duplicate utilities

Prefer deleting unnecessary code over adding more code.

---

# Testing Review

Measure

- Unit coverage
- Integration coverage
- Regression coverage
- Performance coverage
- Security coverage

Target

**95%+**

---

# Documentation Review

Review

- Architecture documentation
- API documentation
- Clinical documentation
- Deployment guides
- Developer documentation

Update anything outdated.

---

# Security Review

Audit

- Authentication
- Authorization
- Encryption
- Secrets
- Credentials
- PII handling
- Logging
- Third-party integrations

---

# Database Review

Review

- Indexes
- Constraints
- Large tables
- Archive strategy
- Migration history
- Data integrity
- Cache strategy

Generate optimization recommendations.

---

# Technical Debt Review

Identify

- Legacy code
- Deprecated code
- TODO items
- FIXME comments
- Temporary workarounds
- High-risk components

Create a prioritized remediation plan.

---

# Refactoring Rules

Prefer

- Simplicity
- Composition
- Reuse
- Explicit code

Avoid

- Duplicate logic
- Unnecessary abstraction
- Over-engineering
- Hidden magic

Delete unnecessary code whenever possible.

---

# Repository Health Score

Generate scores

- Architecture
- Maintainability
- Performance
- Test Coverage
- Documentation
- Security
- Clinical Intelligence
- Evidence Quality
- Technical Debt

Overall score

0–100

Track progress across releases.

---

# Deliverables

Each consolidation sprint shall produce

- Repository Health Report
- Technical Debt Report
- Architecture Review
- Performance Report
- Security Report
- Test Coverage Report
- Documentation Review
- Refactoring Summary
- Clinical Intelligence Assessment
- Knowledge Health Assessment
- Next Sprint Action Plan

---

# Acceptance Criteria

A consolidation sprint is complete only if

- Technical debt is reduced.
- Repository health improves.
- Duplicate code decreases.
- Test coverage improves or remains above target.
- Documentation is current.
- Performance improves or remains stable.
- Clinical intelligence is enhanced.
- No unnecessary architectural complexity is introduced.

---

# Final Principle

The best sprint is not the one that adds the most code.

The best sprint is the one that makes GDES

- Smarter
- Simpler
- Faster
- Safer
- More maintainable
- More clinically trustworthy

Every release should improve both the software and the quality of clinical decision-making.

**Build Better Intelligence. Reduce Complexity. Continuously Improve.**
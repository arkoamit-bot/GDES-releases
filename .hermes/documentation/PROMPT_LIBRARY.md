# Prompt Library — Reusable Prompt Templates

**Location:** `.hermes/prompts/`  
**Count:** 12 production-quality prompts

---

## Overview

The GDES AI Factory maintains a library of 12 reusable prompt templates. Each
prompt is designed for a specific task type and includes context, instructions,
placeholder variables (denoted by `[VARIABLE_NAME]`), quality requirements, and
expected output format.

Prompts are used by agents (primarily OpenCode and Hermes) to ensure consistency
and completeness across similar tasks.

---

## Prompt Inventory

| # | Prompt | File | Primary Agent |
|---|--------|------|---------------|
| 1 | Implement Feature | `implement-feature.md` | OpenCode |
| 2 | Fix Bug | `fix-bug.md` | OpenCode |
| 3 | Repository Review | `repository-review.md` | Hermes/Claude Code |
| 4 | Architecture Review | `architecture-review.md` | Claude Code |
| 5 | Generate Tests | `generate-tests.md` | OpenCode/Testing Agent |
| 6 | Generate Documentation | `generate-documentation.md` | Docs Agent |
| 7 | Refactor Module | `refactor-module.md` | OpenCode |
| 8 | Performance Review | `performance-review.md` | Claude Code |
| 9 | Release Preparation | `release-preparation.md` | Release Agent |
| 10 | Daily Startup | `daily-startup.md` | Hermes |
| 11 | Daily Shutdown | `daily-shutdown.md` | Hermes |
| 12 | Knowledge Update | `knowledge-update.md` | Hermes/User |

---

## Prompt Details

### 1. Implement Feature (`implement-feature.md`)

**Purpose:** Guide implementation of a new feature in the GDES clinical system.

**Placeholder:** `[FEATURE_DESCRIPTION]` — Replace with the feature specification.

**Requirements checklist:**
- Follow existing Django patterns
- Create/update models with proper migrations
- Implement views (prefer class-based views)
- Create serializers for API endpoints
- Add URL routing and admin configuration
- Write tests (minimum 80% coverage for new code)
- Ensure clinical safety validation
- Follow PEP 8 / ruff standards

**Quality gates:** All existing tests pass, new tests written, ruff clean,
mypy clean, migration created, docs updated.

---

### 2. Fix Bug (`fix-bug.md`)

**Purpose:** Guide systematic bug resolution.

**Placeholder:** `[BUG_DESCRIPTION]` — Replace with the bug report.

**Steps:** Reproduce → Root cause analysis → Minimal fix → Regression test →
Verify no side effects → Update documentation.

**Clinical safety:** Always assess whether the bug has clinical safety implications.
If yes, escalate for immediate review.

---

### 3. Repository Review (`repository-review.md`)

**Purpose:** Comprehensive review of repository health, architecture, and readiness.

**Output format:** Executive Summary, Architecture Assessment (1-10 score),
Findings by severity, Recommendations with priority ordering, Risk assessment.

**Review areas:** Directory structure, domain models, URL configurations,
serializer patterns, test coverage, documentation currency, anti-patterns.

---

### 4. Architecture Review (`architecture-review.md`)

**Purpose:** Evaluate proposed architectural changes.

**Placeholder:** `[ARCHITECTURE_CHANGE]` — Replace with the change description.

**Review criteria:** DDD alignment, scalability, performance, security, clinical
safety, backward compatibility, testing implications, maintenance burden.

**Output:** Approval/Rejection with reasoning, required modifications, risk
assessment, migration plan.

---

### 5. Generate Tests (`generate-tests.md`)

**Purpose:** Generate comprehensive test suites for a module.

**Placeholder:** `[MODULE_PATH]` — Replace with the module path.

**Requirements:** Unit tests for models, view/API tests, serializer validation
tests, form validation tests, edge cases, error handling, clinical data
validation, minimum 80% coverage.

**Test patterns:** pytest fixtures, factory_boy for test data, mock external
dependencies, test both success and failure paths, test permissions.

---

### 6. Generate Documentation (`generate-documentation.md`)

**Purpose:** Generate or update project documentation.

**Placeholder:** `[DOCUMENTATION_SCOPE]` — Replace with the scope.

**Types:** API docs (DRF-YASG), architecture decision records, clinical
workflow docs, developer onboarding guide, deployment guide, user manual.

**Standards:** Markdown format, code examples, diagrams where helpful,
accurate clinical terminology, versioned.

---

### 7. Refactor Module (`refactor-module.md`)

**Purpose:** Improve code quality through targeted refactoring.

**Placeholder:** `[MODULE_PATH]` — Replace with the module path.

**Goals:** Improve readability, reduce complexity, extract common patterns,
improve coverage, remove dead code, fix code smells.

**Constraints:** All existing tests must pass, no API changes without approval,
no schema changes without migration plan, clinical logic must remain identical.

---

### 8. Performance Review (`performance-review.md`)

**Purpose:** Identify and resolve performance bottlenecks.

**Placeholder:** `[PERFORMANCE_AREA]` — Replace with the area to review.

**Checklist:** N+1 query detection, index analysis, caching strategy, template
rendering, API response time, background tasks, memory usage, static assets.

**Output:** Performance profile, identified bottlenecks, optimization
recommendations with estimated impact, implementation priority.

---

### 9. Release Preparation (`release-preparation.md`)

**Purpose:** Prepare the system for release.

**Placeholder:** `[VERSION_NUMBER]` — Replace with the version number.

**Checklist:** Quality gates pass, changelog updated, version bumped,
migrations verified, docs reviewed, clinical safety verified, breaking changes
documented, rollback plan prepared, release notes drafted.

---

### 10. Daily Startup (`daily-startup.md`)

**Purpose:** Initialize a productive development session.

**Sequence:** Check git status → Review issues/TODOs → Run quality gates →
Check migrations → Read project memory → Identify priorities → Suggest work plan.

**Output:** Repository status summary, quality gate results, recommended
priorities, blocking issues.

---

### 11. Daily Shutdown (`daily-shutdown.md`)

**Purpose:** Preserve state and prepare for handoff at end of session.

**Sequence:** Run test suite → Commit WIP with descriptive messages → Update
project memory → Document issues/debt → Prepare handoff notes → Generate report.

**Output:** Commit summary, updated project memory, session report,
tomorrow's priorities.

---

### 12. Knowledge Update (`knowledge-update.md`)

**Purpose:** Update the medical knowledge base with new clinical information.

**Placeholder:** `[CLINICAL_DATA]` — Replace with the clinical data.

**Requirements:** Validate clinical accuracy, check against guidelines (KDIGO,
ADA, BIRDEM, BADAS), ensure proper coding, update knowledge base files,
verify integration with CDS, document for audit trail.

---

## Using Prompts

### In an AI Session
When delegating to an agent, include the relevant prompt as context:

```
Use the "Implement Feature" prompt from .hermes/prompts/implement-feature.md.
Feature: [description]
```

### As Templates
Fill in the placeholder variables and pass the complete prompt to an agent.
The prompt structure ensures nothing is overlooked.

### Customization
Prompts can be extended for specific use cases. Add project-specific constraints
or domain-specific requirements as needed.

---

## Prompt Design Principles

1. **Complete context** — Each prompt provides sufficient context for the agent
   to work independently
2. **Placeholder variables** — `[VARIABLE]` syntax makes prompts template-ready
3. **Quality gates** — Every prompt includes a quality checklist
4. **Clinical safety** — Clinical prompts always include safety considerations
5. **Output format** — Expected output is clearly specified

---

## References

- `.hermes/agents/` — Agent role definitions that use these prompts
- `.hermes/workflows/` — Workflows that reference specific prompts
- `.hermes/config/FACTORY_CONFIG.md` — Quality standards applied to all prompts

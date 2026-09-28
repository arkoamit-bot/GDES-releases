# Quality Gates — GDES AI Factory

## Overview

Every workflow in the GDES AI Factory must pass the following quality gates before completion. These gates ensure code quality, maintainability, and clinical safety.

---

## Mandatory Quality Gates

### 1. Ruff — Linting

**Purpose:** Enforce PEP 8 coding standards and code quality  
**Tool:** Ruff (Python linter)  
**Command:** `ruff check .`

#### Pass Criteria
- Zero linting errors
- Zero warnings (or approved exceptions)
- Consistent code style

#### Failure Action
- Stop execution
- Generate linting report
- Recommend corrective actions
- Re-run after fixes

---

### 2. mypy — Type Checking

**Purpose:** Ensure type safety and code reliability  
**Tool:** mypy (static type checker)  
**Command:** `mypy .`

#### Pass Criteria
- Zero type errors
- Type annotations present for critical functions
- Gradual typing compliance

#### Failure Action
- Stop execution
- Generate type error report
- Recommend type annotation improvements
- Re-run after fixes

---

### 3. pytest — Testing

**Purpose:** Validate code functionality and prevent regressions  
**Tool:** pytest (testing framework)  
**Command:** `pytest`

#### Pass Criteria
- All tests pass
- Test coverage meets minimum threshold (80% target)
- No flaky tests

#### Failure Action
- Stop execution
- Generate test failure report
- Identify root causes
- Recommend test improvements
- Re-run after fixes

---

### 4. Migration Consistency

**Purpose:** Ensure database schema changes are valid and reversible  
**Tool:** Django migration system  
**Command:** `python manage.py migrate --check`

#### Pass Criteria
- No pending migrations
- Migration files are consistent
- Migrations are reversible
- Schema changes are backward compatible

#### Failure Action
- Stop execution
- Generate migration status report
- Review migration files
- Ensure migration consistency
- Re-run after fixes

---

### 5. Documentation Completeness

**Purpose:** Ensure all required documentation is present and accurate  
**Tool:** Manual review + automated checks  
**Command:** Documentation validation scripts

#### Pass Criteria
- All required documentation files present
- Documentation reflects current codebase
- No outdated documentation
- Clinical terminology used appropriately

#### Required Documentation
- AI_FACTORY.md — System overview
- ARCHITECTURE.md — Technical architecture
- DEVELOPMENT_GUIDE.md — Development setup
- WORKFLOW_GUIDE.md — Engineering workflows
- QUALITY_GATES.md — Validation requirements
- RELEASE_PROCESS.md — Release procedures
- AGENT_ROLES.md — Agent definitions
- ONBOARDING.md — New developer guide
- PROJECT_MEMORY.md — Project knowledge base

#### Failure Action
- Stop execution
- Identify missing or outdated documentation
- Generate documentation gap report
- Update documentation
- Re-validate

---

### 6. Architecture Consistency

**Purpose:** Ensure changes align with established architecture patterns  
**Tool:** Architecture review + code analysis  
**Command:** Architecture validation

#### Pass Criteria
- Changes follow Clean Architecture principles
- Domain Driven Design patterns maintained
- Component boundaries respected
- No circular dependencies introduced

#### Failure Action
- Stop execution
- Generate architecture violation report
- Recommend architectural corrections
- Consult Architecture Agent (Claude Code)
- Re-validate after changes

---

### 7. Coding Standards

**Purpose:** Ensure consistent coding practices across the codebase  
**Tool:** Code review + automated checks  
**Command:** Coding standards validation

#### Pass Criteria
- Consistent naming conventions
- Proper code organization
- Appropriate comments and documentation
- No code smells or anti-patterns

#### Failure Action
- Stop execution
- Identify coding standard violations
- Generate coding standards report
- Recommend improvements
- Re-validate after fixes

---

## Validation Workflow

```
Task Completed
    ↓
Ruff (Linting)
    ↓
mypy (Type Checking)
    ↓
pytest (Testing)
    ↓
Migration Consistency
    ↓
Documentation Completeness
    ↓
Architecture Consistency
    ↓
Coding Standards
    ↓
✅ Quality Gates Passed
    ↓
Task Approved
```

---

## Failure Protocol

When any quality gate fails:

1. **Stop execution** — Do not proceed
2. **Generate detailed report** — Identify specific failures
3. **Recommend corrective actions** — Provide clear guidance
4. **Re-run validation** — After fixes are applied
5. **Document resolution** — Update project memory

---

## Quality Metrics

| Gate | Target | Current | Status |
|------|--------|---------|--------|
| Ruff | 0 errors | TBD | ⏳ |
| mypy | 0 errors | TBD | ⏳ |
| pytest | 100% pass | TBD | ⏳ |
| Coverage | 80% | ~20-25% | 🔴 |
| Migrations | 0 pending | TBD | ⏳ |
| Documentation | 100% complete | TBD | ⏳ |

---

## Exceptions

Exceptions to quality gates may be granted only:

1. **Emergency hotfixes** — With Project Owner approval
2. **Temporary waivers** — With documented justification
3. **Experimental features** — In feature branches only

**Rule:** All exceptions must be documented and tracked in project memory.

---

## Continuous Improvement

Quality gates are regularly reviewed and updated:

- **Monthly:** Review gate effectiveness
- **Quarterly:** Update thresholds based on project maturity
- **As needed:** Add new gates for emerging risks

---

## Related Documents

- HERMES_SYSTEM.md — System operating instructions
- AI_FACTORY.md — System overview
- WORKFLOW_GUIDE.md — Engineering workflows
- DEVELOPMENT_GUIDE.md — Development setup

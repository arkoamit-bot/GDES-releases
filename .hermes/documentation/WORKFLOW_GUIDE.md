# Workflow Guide — Using GDES AI Factory Workflows

**Location:** `.hermes/workflows/`

---

## Overview

The GDES AI Factory provides 12 standardized workflows that cover the complete
software development lifecycle. Each workflow defines a clear objective, required
agents, step-by-step execution order, quality gates, expected deliverables, and
failure recovery procedures.

---

## Workflow Inventory

| # | Workflow | File | Purpose |
|---|----------|------|---------|
| 1 | Feature Development | `feature-development.md` | Implement new features |
| 2 | Bug Fix | `bug-fix.md` | Diagnose and resolve defects |
| 3 | Daily Startup | `daily-startup.md` | Initialize a dev session |
| 4 | Daily Shutdown | *(via prompts)* | Preserve session state |
| 5 | Release | `release.md` | Prepare and deploy releases |
| 6 | Architecture Review | `architecture-review.md` | Validate architecture changes |
| 7 | Emergency Hotfix | `emergency-hotfix.md` | Rapid critical fixes |
| 8 | Clinical Rule Update | `clinical-rule-update.md` | Update CDS rules |
| 9 | Knowledge Update | `knowledge-update.md` | Update medical knowledge base |
| 10 | Regression Testing | `regression-testing.md` | Verify no regressions |
| 11 | Documentation Update | `documentation-update.md` | Sync docs with code |
| 12 | Repository Health | `repository-health.md` | Comprehensive health check |

Plus `QUALITY_GATES.md` — the centralized validation configuration.

---

## Workflow Structure

Every workflow follows this consistent template:

```
# Workflow: [Name]
## Objective         — What this workflow achieves
## Required Agents   — Which agents participate
## Execution Order   — Step-by-step procedure
## Quality Gates     — Mandatory checklist
## Expected Deliverables — What the workflow produces
## Failure Recovery  — What to do when things go wrong
```

---

## Using Workflows

### Daily Development Cycle

**Morning:**
1. Run the **Daily Startup** workflow
2. Review the output and priority list
3. Select tasks based on the AI Factory's recommendations

**During the Day:**
- Use **Feature Development** for new features
- Use **Bug Fix** for defect resolution
- Use **Clinical Rule Update** for clinical logic changes
- Use **Emergency Hotfix** only for production-critical issues

**End of Day:**
- Run the **Daily Shutdown** workflow (via the prompt)
- Ensure all work is committed and memory is updated

### Quality Validation

After any code change, run the quality gates:

```bash
# Full validation
bash .hermes/scripts/validate_repository.sh

# Or run individual gates
python -m pytest --tb=short --verbose
ruff check .
mypy . --ignore-missing-imports
python manage.py makemigrations --check
```

### Release Cycle

1. Run the **Release** workflow
2. Follow the checklist: feature freeze → quality gates → release candidate →
   clinical safety verification → user approval → deployment → post-deployment
3. Use `bash .hermes/scripts/prepare_release.sh` for automation

---

## Workflow Execution Details

### Feature Development (Most Common)

This is the primary workflow, used for all new functionality:

1. **Requirements Analysis** — Understand what's needed, check existing patterns
2. **Architecture Planning** — Design the solution; escalate to Claude Code if complex
3. **Implementation** — OpenCode creates models, views, serializers, tests, etc.
4. **Testing** — Write and run unit + integration tests
5. **Documentation** — Update API docs, code comments, guides
6. **Quality Gates** — pytest, ruff, mypy, migration check, clinical review
7. **Commit & Report** — Descriptive commit, memory update, completion report

**Agents involved:** Hermes (planner), OpenCode (implementer), Claude Code (reviewer),
Testing Agent (validator)

### Bug Fix

1. **Triage** — Understand severity and clinical safety impact
2. **Reproduction** — Create minimal reproduction case
3. **Root Cause Analysis** — Systematic debugging
4. **Fix Implementation** — Minimal, targeted fix
5. **Regression Testing** — Ensure fix doesn't break other functionality
6. **Review & Commit** — Code review, descriptive commit

**Agents involved:** Hermes (coordinator), OpenCode (fixer), Testing Agent (validator)

### Emergency Hotfix

Accelerated process for production-critical issues:

1. **Triage** — Assess severity and clinical safety impact
2. **Immediate Fix** — Minimal fix + regression test
3. **Emergency Review** — Accelerated code review
4. **Emergency Deployment** — Deploy and verify
5. **Post-Incident** — Root cause analysis and prevention

**Quality gates are accelerated, not skipped.** Clinical safety gate still required.

### Clinical Rule Update

The most sensitive workflow — always requires user approval:

1. **Rule Specification** — Define the clinical change with evidence basis
2. **Impact Analysis** — Check affected patients, rule conflicts
3. **Implementation** — Update clinical reasoning module and knowledge base
4. **Clinical Validation** — Test with sample cases, user clinical review
5. **Deployment** — Apply changes and monitor

---

## Quality Gates Reference

Defined in `workflows/QUALITY_GATES.md`, enforced in all workflows:

| Gate | Tool | Pass Criteria |
|------|------|---------------|
| 1. Testing | pytest | All tests pass, ≥80% coverage for new code |
| 2. Linting | ruff | Zero errors, consistent formatting |
| 3. Type Checking | mypy | No new type errors |
| 4. Migrations | Django | No pending/missing migrations |
| 5. Documentation | Manual | All items verified, no stale docs |
| 6. Architecture | Review | DDD patterns, no anti-patterns |
| 7. Security | Audit | No hardcoded secrets, proper auth |
| 8. Clinical Safety | Review | Rules validated, user approval |

**Execution order:** Gates 1-7 must pass. Gate 8 (clinical) has highest priority
and cannot be bypassed under any circumstance.

---

## Failure Recovery

Each workflow includes failure recovery procedures:

- **Test failures** → Diagnose and fix before proceeding
- **Architecture concerns** → Escalate to Claude Code
- **Clinical safety issues** → STOP everything, escalate to user
- **Migration conflicts** → Resolve and re-test
- **Deployment failures** → Execute rollback plan

---

## Workflow Selection Guide

| Situation | Use This Workflow |
|-----------|-------------------|
| New feature request | Feature Development |
| Bug reported | Bug Fix |
| Production critical issue | Emergency Hotfix |
| Clinical rule needs updating | Clinical Rule Update |
| Medical knowledge update needed | Knowledge Update |
| Architecture change proposed | Architecture Review |
| After significant changes | Regression Testing |
| Docs are out of date | Documentation Update |
| Health assessment needed | Repository Health |
| Preparing a release | Release |
| Starting a work day | Daily Startup |
| Ending a work day | Daily Shutdown (prompt) |

---

## References

- `.hermes/workflows/QUALITY_GATES.md` — Full quality gate specification
- `.hermes/config/AGENT_ROLES.md` — Agent delegation matrix
- `.hermes/prompts/` — Reusable prompt templates for each workflow
- `.hermes/scripts/` — Automation scripts that support workflows

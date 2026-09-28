# Dashboard Guide — Using the Engineering Dashboard

**File:** `.hermes/DASHBOARD.md`  
**Last Updated:** 2026-07-21

---

## Overview

The GDES AI Factory Dashboard (`DASHBOARD.md`) provides a real-time snapshot of
the project's health, agent status, critical findings, and recommended priorities.
It's the single source of truth for understanding the current state of the project.

---

## Reading the Dashboard

The dashboard is organized into these sections:

### 1. Header Metrics
```
Repository Health Score | Technical Debt Score | Test Coverage
     4.15/10           |       6.8/10         |   ~20-25%
```

- **Repository Health Score** (0-10): Overall code quality and maintainability
- **Technical Debt Score** (0-10): Amount of accumulated technical debt
- **Test Coverage**: Percentage of code covered by tests

### 2. Critical Findings
A table of the most pressing issues, sorted by severity:

| Severity | Symbol | Meaning |
|----------|--------|---------|
| 🔴 CRITICAL | Must fix immediately | Security vulnerability, startup failure |
| 🟡 HIGH | Should fix soon | Significant risk or quality issue |
| 🟢 MEDIUM | Fix when convenient | Improvement opportunity |

### 3. Repository Intelligence
Detailed statistics about the codebase:
- Application statistics (apps, models, views, etc.)
- Most complex apps (by LOC, models, views)
- Technology stack summary

### 4. Agent Status
Current status of all 7 AI agents:
- Hermes (Orchestrator) — Always active
- OpenCode (Implementation) — Available
- Claude Code (Architecture) — Available
- GitHub Agent (Version Control) — Available
- Testing Agent (Quality) — Available
- Documentation Agent (Docs) — Available
- Release Agent (Releases) — Available

### 5. AI Factory Components
Status of all AI Factory infrastructure:
- Agent definitions, prompts, workflows, scripts, memory, reports, config

### 6. Quality Assessment
Dimensional quality scores:
- Repository Health, Technical Debt, Test Coverage
- Documentation, Security, AI Factory Readiness

### 7. Recommended Priorities
Organized by timeframe:
- 🔴 **Immediate** (This week)
- 🟡 **Short-term** (This month)
- 🟢 **Medium-term** (This quarter)

### 8. Available Reports
Links to all analysis reports in `.hermes/reports/`

### 9. Quick Commands
Essential commands for common operations

---

## Current Dashboard Summary

### Critical Findings (as of 2026-07-21)

| # | Issue | Severity | Impact |
|---|-------|----------|--------|
| 1 | Hardcoded admin credentials in 3 launcher files | 🔴 CRITICAL | Security vulnerability |
| 2 | Missing `exports` app in INSTALLED_APPS | 🔴 CRITICAL | ModuleNotFoundError |
| 3 | Zero CI/CD pipeline | 🔴 CRITICAL | No automated quality validation |
| 4 | 10/29 apps have NO tests | 🔴 CRITICAL | High regression risk |
| 5 | All dependencies unpinned | 🔴 HIGH | Breaking change vulnerability |
| 6 | No CSP headers or rate limiting | 🟡 HIGH | Security exposure |
| 7 | 111+ docs at root | 🟡 MEDIUM | Documentation sprawl |
| 8 | 6 god files > 1,000 LOC | 🟡 MEDIUM | Maintenance complexity |

### Quality Assessment

| Dimension | Score | Status |
|-----------|-------|--------|
| Repository Health | 4.15/10 | ⚠️ Needs Improvement |
| Technical Debt | 6.8/10 | ⚠️ Significant |
| Test Coverage | ~20-25% | 🔴 Critically Low |
| Documentation | 75% | 🟡 Sprawl needs consolidation |
| Security | 40% | 🔴 Hardcoded creds, no CSP |
| AI Factory Readiness | 82.5% | ✅ Ready |

### Recommended Priorities

**Immediate (This Week):**
1. Remove hardcoded credentials from launcher files
2. Fix missing `exports` app
3. Run full test suite to establish baseline
4. Pin all dependencies in requirements.txt

**Short-term (This Month):**
1. Set up CI/CD pipeline (GitHub Actions)
2. Create tests for clinical_reasoning (8,885 LOC, zero tests)
3. Create tests for clinic (2,276 LOC, zero tests)
4. Consolidate documentation
5. Enable CSP headers and rate limiting

**Medium-term (This Quarter):**
1. Refactor god files (management_plan.py: 2,196 LOC)
2. Reduce coupling in clinic/forms.py
3. Clean up temp/debug scripts
4. Establish test coverage tracking (target: 80%)

---

## Using the Dashboard

### Daily Workflow
1. **Morning:** Open `DASHBOARD.md` to see current state
2. **Prioritize:** Focus on the highest-severity items first
3. **Work:** Use workflows to address issues
4. **Update:** Dashboard reflects changes after memory updates

### For Specific Tasks

**If you're fixing bugs:**
- Check "Critical Findings" for the highest-priority bug
- Check `KNOWN_ISSUES.md` for details and workarounds
- Use the Bug Fix workflow

**If you're starting a new feature:**
- Check "Recommended Priorities" for what's most needed
- Check "Quality Assessment" to understand current standards
- Use the Feature Development workflow

**If you're reviewing code:**
- Check "Repository Intelligence" for app complexity
- Check "Quality Assessment" for current standards
- Use the Architecture Review workflow

**If you're preparing a release:**
- Check all critical findings are resolved
- Check quality assessment meets thresholds
- Use the Release workflow

---

## Refreshing the Dashboard

The dashboard is updated when:
1. `python .hermes/scripts/update_project_memory.py` is run
2. Memory files are manually updated
3. A daily startup or shutdown workflow is executed

To manually refresh:
```bash
python .hermes/scripts/update_project_memory.py
```

---

## Interpreting Scores

### Repository Health (4.15/10)
- 0-3: Critical issues, major rewrite needed
- 4-5: Significant issues, focused improvement needed
- 6-7: Decent, some areas need attention
- 8-10: Healthy, well-maintained

### Technical Debt (6.8/10)
- 0-2: Minimal debt, well-maintained
- 3-5: Moderate debt, manageable
- 6-7: Significant debt, needs planned reduction
- 8-10: Severe debt, major refactoring needed

### Test Coverage (~20-25%)
- 0-30%: Critically low — high regression risk
- 30-60%: Below target — needs improvement
- 60-80%: Acceptable for most projects
- 80-100%: Good coverage, production-ready

---

## Reports Reference

The dashboard links to these analysis reports in `.hermes/reports/`:

| Report | File | Content |
|--------|------|---------|
| Repository Inventory | `REPOSITORY_INVENTORY.md` / `.json` | Full app inventory |
| Technology Stack | `TECHNOLOGY_STACK.md` | Tech stack analysis |
| Domain Summary | `DOMAIN_SUMMARY.md` | Clinical domain details |
| Technical Debt | `TECHNICAL_DEBT_REPORT.md` | Debt analysis |
| Security Audit | `SECURITY_AUDIT.md` | Security findings |
| Test Coverage | `TEST_COVERAGE_REPORT.md` | Coverage analysis |
| Dependency Analysis | `DEPENDENCY_ANALYSIS.md` | Dependency review |
| Code Complexity | `CODE_COMPLEXITY_REPORT.md` | Complexity metrics |
| Repository Health | `REPOSITORY_HEALTH_REPORT.md` | Health assessment |

---

## References

- `.hermes/DASHBOARD.md` — The dashboard itself
- `.hermes/AI_FACTORY_STATUS.md` — Bootstrap status report
- `.hermes/memory/PROJECT_MEMORY.md` — Core project knowledge
- `.hermes/memory/KNOWN_ISSUES.md` — Detailed issue tracker
- `.hermes/scripts/update_project_memory.py` — Dashboard update script
- `.hermes/reports/` — Analysis reports directory

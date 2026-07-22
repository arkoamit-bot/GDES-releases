# Quality Gates — Validation Procedures

**Location:** `.hermes/workflows/QUALITY_GATES.md`  
**Count:** 8 mandatory gates  
**Enforcement:** All workflows

---

## Overview

Every code change in the GDES project must pass 8 mandatory quality gates before
completion. If any gate fails, the workflow stops, a report is generated, and
corrective actions are recommended. The clinical safety gate (Gate 8) has the
highest priority and **cannot be bypassed under any circumstance**.

---

## Gate Execution Order

```
Gate 1: Testing (pytest)        → Must pass
Gate 2: Linting (ruff)          → Must pass
Gate 3: Type Checking (mypy)    → Must pass
Gate 4: Migration Validation    → Must pass
Gate 5: Documentation           → Must pass
Gate 6: Architecture Consistency → Must pass
Gate 7: Security                → Must pass
Gate 8: Clinical Safety         → Must pass (HIGHEST PRIORITY)
```

---

## Gate 1: Testing (pytest)

**Tool:** `python -m pytest`

**Commands:**
```bash
cd /c/Users/User/Documents/GitHub/GDES
python -m pytest --tb=short --verbose
python -m pytest --cov=. --cov-report=html --cov-report=term
```

**Pass Criteria:**
- All tests pass
- Coverage ≥ 80% for new code
- No test warnings related to clinical logic

**Failure Actions:**
1. Identify failing tests
2. Classify: new bug / pre-existing / flaky
3. Fix or document known issues
4. Re-run until clean

**Current Status:** ~20-25% overall coverage (10 of 29 apps have zero tests)

---

## Gate 2: Linting (ruff)

**Tool:** `ruff`

**Commands:**
```bash
ruff check .
ruff check --fix .
ruff format --check .
```

**Pass Criteria:**
- Zero errors (`ruff check` returns 0)
- Formatting consistent (`ruff format` clean)

**Failure Actions:**
1. Run `ruff check --fix .` for auto-fixable issues
2. Manually resolve remaining issues
3. Re-check until clean

---

## Gate 3: Type Checking (mypy)

**Tool:** `mypy`

**Commands:**
```bash
mypy . --ignore-missing-imports
```

**Pass Criteria:**
- No new type errors
- Known issues documented and tracked

**Failure Actions:**
1. Fix new type errors
2. Add type stubs for missing imports
3. Document accepted type ignores with justification

---

## Gate 4: Migration Validation

**Tool:** Django management commands

**Commands:**
```bash
python manage.py makemigrations --check
python manage.py migrate --run-syncdb --check
python manage.py migrate --plan
```

**Pass Criteria:**
- No unapplied migrations
- No missing migrations detected
- Migration plan is clean

**Failure Actions:**
1. Create missing migrations
2. Resolve migration conflicts
3. Test migrations on clean database

---

## Gate 5: Documentation Completeness

**Tool:** Manual checklist

**Checklist:**
- [ ] README.md is current and accurate
- [ ] API documentation generated (DRF-YASG)
- [ ] All new features documented
- [ ] Clinical protocols documented
- [ ] Deployment guide current
- [ ] CHANGELOG updated

**Pass Criteria:**
- All items verified
- No stale documentation
- Clinical terminology accurate

**Failure Actions:**
1. Update missing documentation
2. Remove or archive stale docs
3. Verify clinical terminology

---

## Gate 6: Architecture Consistency

**Tool:** Manual review (Claude Code for complex changes)

**Checklist:**
- [ ] Models follow DDD patterns
- [ ] APIs follow REST conventions
- [ ] No circular dependencies
- [ ] Service boundaries respected
- [ ] Clinical logic isolated from UI

**Pass Criteria:**
- Architecture patterns consistent
- No anti-patterns introduced
- Domain model integrity maintained

**Failure Actions:**
1. Refactor to match patterns
2. Request Claude Code review
3. Document deviations

---

## Gate 7: Security

**Tool:** Manual audit + automated checks

**Checklist:**
- [ ] No hardcoded secrets
- [ ] .env properly handled
- [ ] Authentication required on sensitive endpoints
- [ ] Input validation on all forms
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS prevention (template auto-escaping)

**Pass Criteria:**
- All security checks pass
- No vulnerabilities in dependencies
- Proper access controls

**Failure Actions:**
1. Fix security issues immediately
2. Rotate any exposed credentials
3. Document and track

**Known Issues:** No CSP headers or rate limiting configured (django-csp and
django-ratelimit commented out in settings).

---

## Gate 8: Clinical Safety

**Tool:** User (clinical expert) review

**Checklist:**
- [ ] Clinical rules validated
- [ ] Drug interactions checked
- [ ] Diagnostic criteria verified
- [ ] Patient data handling compliant
- [ ] Clinical audit trail maintained

**Pass Criteria:**
- All clinical safety checks pass
- No breaking clinical logic changes
- User (clinical expert) approval obtained

**Failure Actions:**
1. **STOP all deployment**
2. Escalate to user immediately
3. Document clinical safety concern
4. Resolve before proceeding

**This gate CANNOT be bypassed.** Clinical safety is the highest priority
in the GDES system.

---

## Enforcement Rules

1. **All workflows** enforce quality gates — no exceptions
2. **No feature** can be merged without passing all gates
3. **Emergency hotfixes** have accelerated (not skipped) gates
4. **Clinical safety gate** cannot be bypassed under any circumstance
5. **Gate results** are logged and tracked for trend analysis

---

## Reporting

After each gate execution:
- Generate results summary
- Track pass/fail history
- Update quality dashboard (`.hermes/DASHBOARD.md`)
- Alert on repeated failures

---

## Quick Validation Script

```bash
# Run all automated quality gates
bash .hermes/scripts/validate_repository.sh

# Or run individual gates manually
python -m pytest --tb=short --verbose       # Gate 1
ruff check .                                # Gate 2
mypy . --ignore-missing-imports             # Gate 3
python manage.py makemigrations --check     # Gate 4
```

---

## Current Quality Status

| Gate | Status | Notes |
|------|--------|-------|
| pytest | ⚠️ ~20-25% coverage | 10 apps have zero tests |
| ruff | ✅ Clean | |
| mypy | ⚠️ Some warnings | Known issues documented |
| Migrations | ✅ Clean | |
| Documentation | ⚠️ 111+ root files | Sprawl needs consolidation |
| Architecture | ⚠️ Some god files | management_plan.py: 2,196 LOC |
| Security | 🔴 Hardcoded creds | 3 launcher files affected |
| Clinical Safety | ✅ User required | Non-bypassable |

---

## References

- `.hermes/workflows/QUALITY_GATES.md` — Full gate specification with commands
- `.hermes/workflows/` — Each workflow references these gates
- `.hermes/scripts/validate_repository.sh` — Automated gate runner
- `.hermes/config/FACTORY_CONFIG.md` — Quality standards and targets
- `.hermes/DASHBOARD.md` — Current quality metrics

# Quality Gates — Centralized Validation Configuration

## Overview
All GDES workflows must pass these quality gates before completion.
If any gate fails, the workflow stops, generates a report, and recommends corrective actions.

---

## Gate 1: Testing (pytest)

```bash
# Run full test suite
cd /c/Users/User/Documents/GitHub/GDES
python -m pytest --tb=short --verbose

# With coverage
python -m pytest --cov=. --cov-report=html --cov-report=term
```

**Pass Criteria:**
- All tests pass
- Coverage ≥ 80% for new code
- No test warnings related to clinical logic

**Failure Actions:**
1. Identify failing tests
2. Classify as: new bug / pre-existing / flaky
3. Fix or document known issues
4. Re-run until clean

---

## Gate 2: Linting (ruff)

```bash
# Check for linting errors
ruff check .

# Auto-fix safe issues
ruff check --fix .

# Check formatting
ruff format --check .
```

**Pass Criteria:**
- Zero errors (ruff check returns 0)
- Formatting consistent (ruff format clean)

**Failure Actions:**
1. Run `ruff check --fix .` for auto-fixable issues
2. Manually resolve remaining issues
3. Re-check until clean

---

## Gate 3: Type Checking (mypy)

```bash
# Run type checker
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

```bash
# Check for pending migrations
python manage.py makemigrations --check

# Verify migrations apply cleanly
python manage.py migrate --run-syncdb --check

# Dry run migrations
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

**Checklist:**
- [ ] README.md is current and accurate
- [ ] API documentation generated (DRF-YASG)
- [ ] All new features documented
- [ ] Clinical protocols documented
- [ ] Deployment guide current
- [ ] CHANGELOG updated

**Pass Criteria:**
- All documentation items verified
- No stale documentation
- Clinical terminology accurate

**Failure Actions:**
1. Update missing documentation
2. Remove or archive stale docs
3. Verify clinical terminology

---

## Gate 6: Architecture Consistency

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

---

## Gate 8: Clinical Safety

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
1. STOP all deployment
2. Escalate to user immediately
3. Document clinical safety concern
4. Resolve before proceeding

---

## Gate Execution Order

```
1. pytest         → Must pass
2. ruff check     → Must pass
3. mypy           → Must pass
4. migrations     → Must pass
5. documentation  → Must pass
6. architecture   → Must pass
7. security       → Must pass
8. clinical       → Must pass (highest priority)
```

## Enforcement

- Gates are enforced in all workflows
- No feature can be merged without passing all gates
- Emergency hotfixes have accelerated (not skipped) gates
- Clinical safety gate CANNOT be bypassed

## Reporting

After each gate execution:
- Generate results summary
- Track pass/fail history
- Update quality dashboard
- Alert on repeated failures

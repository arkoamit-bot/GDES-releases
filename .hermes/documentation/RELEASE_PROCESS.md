# Release Process — Preparation and Deployment

**Workflow:** `.hermes/workflows/release.md`  
**Agent:** Release Agent  
**Automation:** `.hermes/scripts/prepare_release.sh`

---

## Overview

The GDES release process follows a structured pipeline from feature freeze through
deployment and post-verification. Clinical safety is verified at every stage, and
the user (clinical expert) must approve all releases.

---

## Release Pipeline

```
1. Feature Freeze
   │
2. Quality Validation ─────── All 8 quality gates
   │
3. Release Candidate ──────── Version bump, changelog, notes
   │
4. Clinical Safety ────────── Verify clinical logic unchanged
   │
5. User Approval ──────────── Clinical expert signs off
   │
6. Deployment ─────────────── Execute deployment
   │
7. Post-Deployment ────────── Verify and monitor
   │
8. Publication ────────────── Release notes, stakeholder notification
```

---

## Phase 1: Feature Freeze

1. No new features after this point
2. Only bug fixes and critical patches allowed
3. All branches merged or deferred
4. Codebase stabilized

**Commands:**
```bash
# Check for open branches
git branch -a

# Verify clean working tree
git status

# Check for open PRs
gh pr list --state open
```

---

## Phase 2: Quality Validation

Run all 8 quality gates (defined in `.hermes/workflows/QUALITY_GATES.md`):

```bash
# Automated validation
bash .hermes/scripts/validate_repository.sh

# Or run individually
python -m pytest --tb=short --verbose     # Gate 1: Testing
ruff check .                              # Gate 2: Linting
mypy . --ignore-missing-imports           # Gate 3: Type checking
python manage.py makemigrations --check   # Gate 4: Migrations
```

**Manual gates:**
- Gate 5: Documentation completeness
- Gate 6: Architecture consistency
- Gate 7: Security audit
- Gate 8: Clinical safety verification

**All gates must pass before proceeding.**

---

## Phase 3: Release Candidate

### Version Management
- Update version number in `bgddr/settings.py`
- Follow semantic versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking clinical changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes only

### Changelog
- Compile all changes since last release
- Categorize: Features, Fixes, Breaking Changes, Clinical Updates
- Include issue/PR references

### Release Notes
- User-facing changes
- Migration instructions
- Known issues
- Upgrade guide

### Git Tag
```bash
git tag -a v[VERSION] -m "Release v[VERSION]"
git push origin v[VERSION]
```

---

## Phase 4: Clinical Safety Verification

**This phase is mandatory and cannot be skipped.**

Checklist:
- [ ] Clinical rules validated against knowledge base
- [ ] Drug interaction logic verified
- [ ] Diagnostic criteria unchanged (or intentionally modified with approval)
- [ ] Patient data handling compliant
- [ ] Audit trail maintained
- [ ] No unintended clinical logic changes

**If any clinical safety concern is found → STOP release, escalate to user.**

---

## Phase 5: User Approval

Present release package to user for approval:
- Release notes
- Changelog
- Clinical safety verification report
- Quality gate results
- Deployment plan
- Rollback plan

**User must explicitly approve before proceeding to deployment.**

---

## Phase 6: Deployment

### Desktop Deployment
```bash
# Build PyInstaller package
bash .hermes/scripts/prepare_release.sh
```

### Production Deployment (Docker)
```bash
# Build and deploy
docker-compose build
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs --tail=50
```

### Deployment Checklist
- [ ] Migrations applied successfully
- [ ] Static files collected
- [ ] Configuration updated
- [ ] Services started and healthy
- [ ] SSL/TLS certificates valid
- [ ] Database backups completed

---

## Phase 7: Post-Deployment Verification

1. **Functional verification** — Test critical paths
2. **Performance verification** — Response times acceptable
3. **Error monitoring** — No new errors in logs
4. **Clinical verification** — CDS rules working correctly
5. **User feedback** — Collect initial feedback

**If issues found → Emergency Hotfix workflow**

---

## Phase 8: Publication

1. Update CHANGELOG.md in repository root
2. Publish release notes on GitHub
3. Notify stakeholders
4. Update project memory
5. Archive release artifacts

---

## Rollback Plan

Every release must have a documented rollback plan:

1. **Identify the issue** — What went wrong?
2. **Assess impact** — Is it critical enough to roll back?
3. **Execute rollback** — Restore previous version
4. **Verify rollback** — Confirm system is functional
5. **Communicate** — Notify users of the rollback
6. **Root cause** — Investigate and fix before next release

### Rollback Commands
```bash
# Docker rollback
docker-compose down
git checkout v[PREVIOUS_VERSION]
docker-compose build
docker-compose up -d

# Database rollback (if migrations need reverting)
python manage.py migrate [app_name] [previous_migration]
```

---

## Emergency Hotfix Process

For production-critical issues that cannot wait for the full release cycle:

1. **Triage** — Assess severity and clinical safety impact
2. **Fix** — Minimal targeted fix + regression test
3. **Accelerated review** — Code review (expedited)
4. **Deploy** — Emergency deployment
5. **Verify** — Confirm fix in production
6. **Post-incident** — Root cause analysis, prevention measures

**Quality gates are accelerated, not skipped. Clinical safety gate still required.**

See `.hermes/workflows/emergency-hotfix.md` for the full workflow.

---

## Release History

Track all releases in the CHANGELOG.md and git tags:
```bash
# List all releases
git tag -l "v*"

# View release details
git show v[VERSION]
```

---

## References

- `.hermes/workflows/release.md` — Full release workflow
- `.hermes/workflows/emergency-hotfix.md` — Emergency hotfix workflow
- `.hermes/workflows/QUALITY_GATES.md` — Quality gate specifications
- `.hermes/scripts/prepare_release.sh` — Release automation
- `.hermes/agents/release-agent.md` — Release agent role
- `.hermes/config/AGENT_ROLES.md` — Delegation matrix

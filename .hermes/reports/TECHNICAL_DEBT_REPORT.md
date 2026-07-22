# GDES Technical Debt Report

**Generated:** 2026-07-21  
**Repository:** C:\Users\User\Documents\GitHub\GDES  
**Total Python LOC:** ~47,000 (516 .py files)  
**Apps:** 29 (28 active in INSTALLED_APPS + 1 disabled)

---

## 1. Executive Summary

| Category | Debt Level | Items |
|----------|-----------|-------|
| Dead Code & Temp Files | 🔴 High | 8 temp/debug scripts, 3 duplicate launchers |
| Documentation Sprawl | 🔴 High | 111 markdown files at root level |
| Large God Files | 🔴 High | 6 files exceeding 1,000 LOC |
| Unpinned Dependencies | 🟡 Medium | All deps use `>=` without upper bounds |
| Missing Test Coverage | 🔴 High | 10 apps with zero test files |
| Migration Debt | 🟡 Medium | 64 migration files, some redundant |
| Circular Dependencies | 🟡 Medium | `clinic` imports from 8 apps; `feedback→knowledge` coupling |
| Incomplete Features | 🟡 Medium | Commented-out deps (CSP, rate-limiting, Twilio) |

## 2. Dead Code & Temp Files

### 🔴 Temporary/Debug Scripts at Root

| File | Size | Purpose | Action |
|------|------|---------|--------|
| `_tmp_ms_test.py` | 199B | Temporary test | DELETE |
| `check_patient_221.py` | 1.3KB | One-off data check | DELETE or move to scripts/ |
| `find_dups.py` | 1.8KB | Duplicate finder utility | Move to scripts/ |
| `inspect_db.py` | 6.3KB | DB inspection utility | Move to scripts/ |
| `tmp_audit_c3.py` | 1.3KB | Temporary audit script | DELETE |
| `cleanup_dups.sql` | 1.7KB | SQL cleanup script | Move to scripts/ |

### 🔴 Duplicate Launcher Files

| File | LOC | Size | Purpose |
|------|-----|------|---------|
| `desktop/launcher.py` | 1,099 | 44KB | Main desktop launcher |
| `desktop/launcher-Dr-Wasim-2.py` | 901 | 36KB | Doctor-specific launcher v2 |
| `desktop/launcher-Dr-Wasim.py` | 763 | 30KB | Doctor-specific launcher v1 |

**Issue:** Three near-duplicate launcher files with overlapping functionality. The doctor-specific files appear to be forks of the main launcher with hardcoded credentials. These should be consolidated using configuration/profiles.

### 🟡 Commented-Out Code in requirements.txt

```python
# psycopg>=3.1           # 6 commented-out deps
# gunicorn>=22.0
# twilio>=9.0
# django-csp>=3.8
# django-ratelimit>=4.1
# pyinstaller>=6.0
```

### 🟡 Unused App Directory
- `desktop/` — Present as a directory but NOT in `INSTALLED_APPS` (contains only launcher scripts, not a Django app)

## 3. Documentation Sprawl

### 111 Markdown Files at Repository Root

The root directory contains **111 `.md` files** plus a `docs/` directory with **230 files**. Major categories:

| Category | Count | Examples |
|----------|-------|---------|
| Version Mission Docs | ~20 | GDES_V2_NEXT_MISSION.md through GDES_V8_* |
| Audit/Review Reports | ~15 | GDES_FINAL_*, *_AUDIT.md, *_REVIEW.md |
| Validation Reports | ~10 | *_VALIDATION.md, *_VALIDATION_REPORT.md |
| Architecture Docs | ~8 | DEPENDENCY_GRAPH.md, SERVICE_MAP.md, etc. |
| Workflow Documentation | ~5 | WORKFLOW_*.md, WORKFLOW_VALIDATION_REPORT.md |
| Other | ~50+ | Various analysis and planning docs |

**Issue:** This creates confusion about what is current vs. outdated documentation. Many version-specific docs (V2, V3, V4, V5, V6) reference completed milestones and are no longer actionable.

## 4. Large Files (God Files)

| File | LOC | Issue |
|------|-----|-------|
| `clinical_reasoning/services/management_plan.py` | **2,196** | Contains 9 disease-specific protocol generators in one file |
| `clinic/views.py` | **1,507** | 58 view functions in one file |
| `knowledge/tests.py` | **1,235** | Monolithic test file |
| `knowledge/management/commands/seed_v4_knowledge.py` | **1,101** | Data seeding as code |
| `desktop/launcher.py` | **1,099** | Desktop launcher monolith |
| `knowledge/management/commands/seed_knowledge_base.py` | **1,021** | More seeding as code |
| `knowledge/views.py` | **989** | 102 view functions |
| `desktop/launcher-Dr-Wasim-2.py` | **901** | Duplicate launcher |
| `knowledge/models.py` | **841** | 15+ models in one file |
| `desktop/launcher-Dr-Wasim.py` | **763** | Duplicate launcher |

**Total in top 10 files:** 10,667 LOC — **16% of all non-migration Python code** is in just 10 files.

## 5. Migration Status

### Migration Count by App

| App | Migrations | Status |
|-----|-----------|--------|
| knowledge | 9 | 🔴 Heaviest — 9 migrations with schema evolution |
| pathology | 7 | ⚠️ Multiple schema changes |
| patients | 7 | ⚩ Complex schema evolution |
| feedback | 4 | ⚠️ Multiple additions |
| prescriptions | 5 | ⚠️ Evolved over time |
| treatments | 5 | ⚠️ Multiple schema changes |
| clinical_reasoning | 2 | ✅ Clean |
| encounters | 3 | ✅ Moderate |
| analytics | 3 | ✅ Moderate |
| baseline | 3 | ✅ Moderate |
| decision | 2 | ✅ Clean |
| users | 2 | ✅ Clean |
| All others (14 apps) | 1 each | ✅ Initial only |

**Total migration files: 64** (excluding `__init__.py`)

### Concerns
- ⚠️ `knowledge` has 9 migrations — consider squashing
- ⚠️ `pathology` has 7 migrations with multiple schema changes
- ⚠️ No evidence of migration squash ever performed

## 6. Incomplete Features & Tech Debt

### Commented-Out Security Features
- `django-csp` — Content-Security-Policy headers (security gap)
- `django-ratelimit` — Rate limiting (security gap)
- `psycopg` — PostgreSQL adapter (migration path incomplete)

### Commented-Out Apps
- `biobank` — Disabled in INSTALLED_APPS (GN Master Protocol v2 removal)
  - Code retained for potential future use

### Placeholder Values
- `desktop/launcher-Dr-Wasim.py:263` — `_GITHUB_REPO = "YOUR_USERNAME/GDES"  # TODO: set after creating the repo`

### Hardcoded Values
- `clinical_reasoning/services/followup_scheduler.py` — Uses hardcoded intervals
- `decision/services.py:391` — Uses hardcoded `DISEASE_PROFILES` (9 diseases), noted as superseded

## 7. Dependency Graph Issues

### `clinic/forms.py` — Maximum Coupling
Imports from 8 different apps simultaneously:
```
patients, baseline, encounters, safety, treatments, pathology, studies, audit
```

This makes the clinic module the most fragile — a breaking change in ANY of these 8 apps can break clinic forms.

### `clinical_reasoning` → `knowledge` Tightly Coupled
5 files in clinical_reasoning directly import from knowledge, creating a tight coupling between the two most complex apps.

### `feedback` → `knowledge` + `bgddr`
The feedback app depends on version information from both knowledge and bgddr, creating cross-cutting concerns.

## 8. Technical Debt Score

| Dimension | Score (1-10) | Weight | Weighted |
|-----------|-------------|--------|----------|
| Code Duplication | 7 | 15% | 1.05 |
| Dead Code | 8 | 10% | 0.80 |
| Documentation Sprawl | 7 | 10% | 0.70 |
| God Files | 8 | 20% | 1.60 |
| Test Coverage | 6 | 25% | 1.50 |
| Migration Cleanliness | 4 | 5% | 0.20 |
| Dependency Management | 6 | 10% | 0.60 |
| Security Gaps | 7 | 5% | 0.35 |
| **TOTAL** | | **100%** | **6.8 / 10** |

**Interpretation:** The codebase has significant technical debt (6.8/10). The primary concerns are god files, dead code/duplication, and missing test coverage.

## 9. Recommendations (Prioritized)

### 🔴 Critical (Immediate)
1. Remove all temp/debug scripts from root (`_tmp_ms_test.py`, `tmp_audit_c3.py`, etc.)
2. Remove hardcoded credentials from launcher files
3. Consolidate 3 launcher files into 1 with configuration profiles
4. Enable `django-csp` and `django-ratelimit`

### 🟡 High (This Sprint)
5. Split `management_plan.py` into per-disease modules
6. Decompose `clinic/views.py` into view modules
7. Pin all dependencies in requirements.txt
8. Add test coverage for 10 untested apps
9. Archive or remove stale version docs from root

### 🟢 Medium (Next Sprint)
10. Squash knowledge migrations (9 → 1)
11. Split `knowledge/models.py` into model modules
12. Reduce `clinic/forms.py` coupling via service layer
13. Add coverage reporting and CI pipeline
14. Create `scripts/` directory and move utilities there

---

*Report generated by automated static analysis.*

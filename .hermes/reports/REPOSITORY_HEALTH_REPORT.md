# GDES Repository Health Report

**Generated:** 2026-07-21  
**Repository:** C:\Users\User\Documents\GitHub\GDES  
**Framework:** Django 5.x + DRF  
**Version:** V8.x Clinical Intelligence Platform

---

## 1. Repository Overview

| Metric | Value |
|--------|-------|
| Total Python Files | 516 |
| Total Python LOC | ~47,000 |
| Non-Migration Python LOC | ~47,000 (migration code is ~5,700 of total) |
| Django Apps | 29 (28 active + 1 disabled) |
| Management Commands | 35 |
| Test Files | 27 (in tests/ + app-level) |
| Test Functions | ~370+ |
| Migration Files | 64 |
| Markdown Docs (root) | 111 |
| Docs Directory Files | 230 |
| JavaScript Files | ~10 (vendored) |
| Docker Support | ✅ Dockerfile + docker-compose.yml |
| Desktop Support | ✅ Waitress WSGI + launcher scripts |
| Tailwind CSS | ✅ static_src/ |

## 2. Architecture Health

### App Distribution
```
Knowledge-heavy (clinical intelligence):
  knowledge .............. 12,392 LOC  🔴
  clinical_reasoning .....  8,885 LOC  🔴
  feedback ...............  3,400 LOC  ⚠️

UI/Application layer:
  desktop ................  3,130 LOC  ⚠️
  clinic .................  2,276 LOC  ⚠️
  analytics ..............  3,016 LOC  ⚠️

Domain models:
  followup ...............  2,359 LOC  ⚠️
  patients ...............  1,754 LOC  ✅
  treatments .............  1,730 LOC  ✅
  prescriptions ..........  1,301 LOC  ✅
  decision ...............  1,150 LOC  ✅

Infrastructure:
  bgddr (project) ........  1,846 LOC  ⚠️
  labs ...................  1,016 LOC  ✅
  studies ................    992 LOC  ✅
  pathology ..............    956 LOC  ✅

Small apps (< 800 LOC each):
  reminders, audit, fhir, users, api, scheduling,
  biomarkers, encounters, safety, baseline, events,
  clinical, timeline, biobank
  Total .................. ~6,200 LOC  ✅
```

### Key Finding
The **top 2 apps (knowledge + clinical_reasoning) account for 30% of all code** and contain the most complex logic. This is both the project's core value and its primary maintenance risk.

## 3. Code Quality Metrics

| Metric | Value | Rating |
|--------|-------|--------|
| Average file size | ~91 LOC | ✅ Good (excluding outliers) |
| Median file size | ~150 LOC | ✅ Good |
| Largest file | 2,196 LOC | 🔴 Excessive |
| Files > 500 LOC | 15 | ⚠️ 15 files need decomposition |
| Files > 1000 LOC | 6 | 🔴 God files |
| Functions per view file | avg 12 | ⚠️ Some have 58+ |
| Total management commands | 35 | ⚠️ High; consider consolidation |
| Imports per file (avg) | ~15 | ✅ Acceptable |

## 4. Testing Health

| Metric | Value | Rating |
|--------|-------|--------|
| Test files in tests/ | 19 | ✅ Good central suite |
| Test functions (central) | 311 | ✅ Reasonable |
| Apps with tests | 19/29 | ⚠️ 66% coverage |
| Apps without tests | 10/29 | 🔴 34% untested |
| Test LOC | ~6,300 | ⚠️ Moderate |
| Estimated coverage | ~20-25% | 🔴 Low |
| CI pipeline | None detected | 🔴 Critical gap |
| Coverage tool | None configured | 🔴 Critical gap |

### Test Coverage by Criticality

| App | Criticality | Tested? | Risk |
|-----|-------------|---------|------|
| clinical_reasoning | 🔴 Critical (CDS) | ⚠️ Via central tests only | HIGH |
| knowledge | 🔴 Critical (KB) | ✅ 3 test files | LOW |
| clinic | 🔴 Critical (UI) | ❌ No tests | HIGH |
| decision | 🔴 Critical (CDS) | ❌ No tests | HIGH |
| patients | 🔴 Critical (PHI) | ⚠️ Via central tests only | MEDIUM |
| treatments | 🟡 High | ❌ No tests | MEDIUM |
| users | 🟡 High (auth) | ❌ No tests | MEDIUM |
| feedback | 🟡 High | ⚠️ Minimal | MEDIUM |
| bgddr | 🟡 Medium | ❌ No tests | LOW |

## 5. Security Health

| Check | Status | Detail |
|-------|--------|--------|
| Secrets in env vars | ✅ | All production settings use env vars |
| .env gitignored | ✅ | `.env` in `.gitignore` line 35 |
| No .env committed | ✅ | No `.env` file found in repo |
| Hardcoded credentials | 🔴 | `"admin"/"bgddr-admin"` in 3 launcher files |
| DEBUG default | ⚠️ | ON in dev settings |
| CSP headers | 🔴 | `django-csp` commented out |
| Rate limiting | 🔴 | `django-ratelimit` commented out |
| eval/exec | ✅ | None detected |
| shell=True | ✅ | None in subprocess calls |
| SQL injection | ✅ | Django ORM used throughout |

## 6. Documentation Health

| Category | Count | Health |
|----------|-------|--------|
| Root-level .md files | 111 | 🔴 Excessive — creates confusion |
| docs/ directory | 230 files | ✅ Organized by version |
| Total documentation | 341 files | ⚠️ Likely contains many outdated docs |

### Documentation Concerns
- 111 files at root makes it hard to find current information
- Multiple version-specific docs (V2 through V8) may contain outdated info
- Many "audit" and "review" documents that are point-in-time snapshots
- No clear index or navigation between documents

## 7. Migration Health

| App | Migrations | Health |
|-----|-----------|--------|
| knowledge | 9 | 🔴 Should squash |
| pathology | 7 | ⚠️ Multiple schema changes |
| patients | 7 | ⚠️ Complex evolution |
| feedback | 4 | ⚠️ Multiple additions |
| prescriptions | 5 | ⚠️ Evolved over time |
| treatments | 5 | ⚠️ Evolved over time |
| All other apps | 1-3 each | ✅ Clean |

**Total: 64 migration files** — recommend squashing knowledge (9→1), pathology (7→1), patients (7→1).

## 8. Infrastructure Health

| Component | Status | Notes |
|-----------|--------|-------|
| Dockerfile | ✅ Present | Base image not pinned |
| docker-compose.yml | ✅ Present | Full stack (Django, PostgreSQL, Redis, nginx) |
| Waitress (desktop) | ✅ Used | Good for Windows desktop deployment |
| WhiteNoise | ✅ Used | Static file serving |
| Celery | ⚠️ In deps | Not visibly used in code (Phase 3.2) |
| Redis | ⚠️ In deps | Required for Celery, not visibly used |
| PostgreSQL | ⚠️ Commented out | psycopg in requirements.txt, not active |
| WeasyPrint | ✅ Used | PDF generation |
| xhtml2pdf | ✅ Used | PDF fallback |

## 9. Repository Smells

| Smell | Severity | Details |
|-------|----------|---------|
| God files | 🔴 High | 6 files > 1,000 LOC |
| Dead code | 🔴 High | 8 temp scripts + 3 duplicate launchers |
| Documentation bloat | ⚠️ Medium | 111 docs at root |
| Unpinned deps | ⚠️ Medium | All `>=` with no upper bounds |
| No CI | 🔴 High | No automated testing |
| No coverage | 🔴 High | No coverage measurement |
| Seed command sprawl | ⚠️ Medium | 10+ seed commands; should use fixtures |
| Disabled app retained | 🟢 Low | biobank code kept for future |
| Vendored JS | 🟢 Low | No update mechanism |

## 10. Overall Health Score

| Dimension | Score (/10) | Weight | Contribution |
|-----------|-------------|--------|-------------|
| Code Organization | 6 | 15% | 0.90 |
| Test Coverage | 3 | 25% | 0.75 |
| Security | 5 | 20% | 1.00 |
| Documentation | 4 | 10% | 0.40 |
| Dependency Management | 4 | 10% | 0.40 |
| Migration Health | 5 | 5% | 0.25 |
| Dead Code/Cleanliness | 4 | 10% | 0.40 |
| CI/CD | 1 | 5% | 0.05 |
| **OVERALL** | | **100%** | **4.15 / 10** |

### Health Verdict: ⚠️ NEEDS IMPROVEMENT

The GDES codebase has strong clinical domain logic and good architectural intent, but suffers from significant testing gaps, security header omissions, documentation sprawl, and dead code accumulation. The core clinical reasoning engine is well-tested via the central test suite, but many supporting apps have zero coverage.

## 11. Top 10 Actions to Improve Health

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Set up CI with pytest + coverage | 🔴 Critical | Low |
| 2 | Remove hardcoded credentials | 🔴 Critical | Low |
| 3 | Enable CSP + rate limiting | 🔴 Critical | Low |
| 4 | Pin all dependencies | 🟡 High | Low |
| 5 | Add tests for 10 untested apps | 🟡 High | Medium |
| 6 | Remove temp scripts + consolidate launchers | 🟡 High | Medium |
| 7 | Split god files (top 3) | 🟡 High | High |
| 8 | Archive/archive stale root docs | 🟢 Medium | Low |
| 9 | Squash migrations (knowledge, pathology, patients) | 🟢 Medium | Low |
| 10 | Set up `pip-audit` for vulnerability scanning | 🟢 Medium | Low |

---

*Report generated by automated static analysis of the GDES repository.*

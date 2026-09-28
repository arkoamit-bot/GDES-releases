# GDES Project Memory & Context
Generated: AI Factory v1.0 Master Bootstrap

## 1. Project Overview
- **Name:** Glomerular Disease Expert System (GDES) / Bangladesh Glomerular Disease Data Registry (BGDDR)
- **Institution:** BIRDEM / BADAS, Bangladesh
- **Core Purpose:** Clinical expert system and data registry for glomerular diseases (DKD, 9 disease profiles), supporting clinical decision making, research, and patient management.
- **Current Version:** V8.x Clinical Intelligence Platform
- **AI Factory Version:** v1.0

## 2. Technology Stack
- **Backend:** Django 5.0+, Django REST Framework (DRF)
- **Database:** PostgreSQL (Production) / SQLite (Desktop)
- **Frontend:** Tailwind CSS, HTML templates, JavaScript
- **Compute / Analytics:** NumPy, Pandas, SciPy, statsmodels (survival analysis, LMM, Cox PH)
- **Deployment:** Docker, PyInstaller + Waitress (Desktop)
- **AI Factory:** Hermes, OpenCode, Claude Code

## 3. Architecture & Apps
- **Total Django Apps:** 30
- **Active Apps:** 29 (1 disabled: biobank)
- **Models:** 86
- **Views (FBV):** 129
- **DRF ViewSets:** 58
- **Serializers:** 86
- **Forms:** 22
- **Admin Classes:** 73
- **Management Commands:** 35
- **Test Files:** 27
- **Migrations:** 64
- **Repository Health Score:** 4.15/10

### App Categories
**Knowledge-heavy (clinical intelligence):**
- knowledge: 12,392 LOC 🔴
- clinical_reasoning: 8,885 LOC 🔴
- feedback: 3,400 LOC ⚠️

**UI/Application layer:**
- desktop: 3,130 LOC ⚠️
- clinic: 2,276 LOC ⚠️
- analytics: 3,016 LOC ⚠️

**Domain models:**
- followup: 2,359 LOC ⚠️
- patients: 1,754 LOC ✅
- treatments: 1,730 LOC ✅
- prescriptions: 1,301 LOC ✅
- decision: 1,150 LOC ✅

**Infrastructure:**
- bgddr (project): 1,846 LOC ⚠️
- labs: 1,016 LOC ✅
- studies: 992 LOC ✅
- pathology: 956 LOC ✅

## 4. Dependencies
- **Total Packages:** 18+
- **Key Libraries:** Django~=5.0.7, djangorestframework~=3.15.2, django-jazzmin~=3.0.1, WeasyPrint~=62.3, openpyxl~=3.1.5, pyreadstat~=1.2.7, pandas~=2.2.3, waitress~=3.0.2, whitenoise~=6.8.2, xhtml2pdf~=0.2.16, celery~=5.4.0, redis~=5.2.1, django-csp~=3.8.0, django-ratelimit~=4.1.0, pytest~=8.3.4, pytest-cov~=6.0.0, ruff~=0.7.4, mypy~=1.13.0

## 5. Engineering Standards
- **AI Factory Orchestrator:** Hermes Agent (Engineering Director)
- **Primary Implementation Agent:** OpenCode (Principal Software Engineer)
- **Architecture Review Agent:** Claude Code (Chief Software Architect)
- **Version Control:** Branch strategy (`ai-factory-v1`, feature branches)
- **Quality Gates:** pytest, ruff, mypy, migration validation, documentation completeness, architecture consistency, coding standards

## 6. AI Factory v1.0 Status
**Status:** ✅ COMPLETE

All 15 steps from HERMES_MASTER_BOOTSTRAP.md implemented:
1. ✅ Repository Analysis — 22 reports generated
2. ✅ AI Factory Structure — Complete `.hermes/` directory
3. ✅ Documentation — 11+ documentation files
4. ✅ Project Memory — 4 memory files
5. ✅ Prompt Library — 15 production-ready prompts
6. ✅ Workflow Library — 15 reusable workflows
7. ✅ Implementation Delegation — OpenCode agent ready
8. ✅ Architecture Review Delegation — Claude Code agent ready
9. ✅ Quality Assurance — 7 mandatory quality gates
10. ✅ GitHub Integration — 6 GitHub Actions workflows
11. ✅ Reports — 22 intelligence reports
12. ✅ Scripts — 8 automation scripts
13. ✅ Daily Startup — Workflow and script ready
14. ✅ Continuous Improvement — Process established
15. ✅ Definition of Done — All criteria met

## 7. Known Issues & Technical Debt
**Repository Health:** 4.15/10
**Test Coverage:** ~20-25% (target: 80%)
**Critical Issues:**
- 10 untested apps (including clinical_reasoning)
- 6 god files >1,000 LOC
- Hardcoded credentials in launcher files (marked RESOLVED)
- No CSP headers or rate limiting (django-csp/ratelimit commented out)

**High-Priority Issues:**
- Documentation sprawl (111+ root docs)
- Temp/debug scripts at root
- High coupling in clinic app
- Zero CI/CD pipeline (GitHub Actions created but PR #14 not merged)

## 8. AI Factory Components

### Agents (`.hermes/agents/`)
- hermes.md — Project Manager & Orchestrator
- implementation-agent.md — OpenCode (Principal Software Engineer)
- architecture-agent.md — Claude Code (Chief Software Architect)
- testing-agent.md — Quality Validation
- docs-agent.md — Knowledge Management
- release-agent.md — Release Coordination
- repo-intelligence-agent.md — Repository Analysis

### Workflows (`.hermes/workflows/`)
- daily-startup.md — Session initialization
- feature-development.md — Feature implementation
- bug-fix.md — Bug resolution
- regression-testing.md — Quality validation
- architecture-review.md — Design review
- release.md — Release preparation
- documentation-update.md — Docs maintenance
- emergency-hotfix.md — Critical fixes
- repository-health.md — Health monitoring
- repository-audit.md — Comprehensive audit
- technical-debt-review.md — Debt reduction
- dependency-review.md — Dependency management
- knowledge-update.md — Knowledge base updates
- clinical-rule-update.md — Clinical logic changes
- QUALITY_GATES.md — Validation requirements

### Prompts (`.hermes/prompts/`)
- implement-feature.md — Feature development
- fix-bug.md — Bug fixing
- architecture-review.md — Design review
- repository-review.md — Code review
- performance-review.md — Performance analysis
- knowledge-update.md — Knowledge base updates
- release-preparation.md — Release preparation
- regression-testing.md — Regression testing
- generate-documentation.md — Documentation generation
- migration.md — Database migrations
- generate-tests.md — Test generation
- refactor-module.md — Code refactoring
- repository-analysis.md — Repository analysis

### Memory (`.hermes/memory/`)
- PROJECT_MEMORY.md — Project knowledge base
- KNOWN_ISSUES.md — Issue tracking
- DECISIONS.md — Architecture decisions
- MEMORY_INDEX.md — Memory structure

### Reports (`.hermes/reports/`)
- 22 intelligence reports covering repository health, security, complexity, dependencies, and more

### Scripts (`.hermes/scripts/`)
- daily_startup.sh — Session initialization
- daily_shutdown.sh — Session cleanup
- validate_repository.sh — Quality validation
- generate_reports.sh — Report generation
- update_project_memory.py — Memory refresh
- prepare_release.sh — Release preparation
- repository_scan.py — Repository analysis
- bootstrap_ai_factory.py — Factory initialization

### Documentation (`.hermes/documentation/`)
- AI_FACTORY.md — System overview
- HERMES_SYSTEM.md — Operating instructions
- HERMES_MASTER_BOOTSTRAP.md — Master bootstrap
- ARCHITECTURE.md — Technical architecture
- DEVELOPMENT_GUIDE.md — Development setup
- WORKFLOW_GUIDE.md — Engineering workflows
- QUALITY_GATES.md — Validation requirements
- RELEASE_PROCESS.md — Release procedures
- AGENT_ROLES.md — Agent definitions
- ONBOARDING.md — New developer guide
- PROJECT_MEMORY.md — Project knowledge base

## 9. Git Workflow
- **Current Branch:** `ai-factory-v1`
- **Remote:** `origin` → `https://github.com/arkoamit-bot/GDES-releases`
- **PR Status:** #14 OPEN (AI Factory v1.0 — 12K additions)
- **Last Commit:** `677e0f6` — feat: implement HERMES_SYSTEM.md and update agent definitions

## 10. Next Phase
**Phase 2: Security Hardening & Test Coverage**
1. Merge PR #14 — Activates CI/CD pipelines
2. Enable CSP headers and rate limiting
3. Address test coverage gaps (10 untested apps)
4. Clean up documentation sprawl
5. Remove dead code and temp scripts

## 11. Long-Term Vision
Continuously evolve GDES using an AI-first software engineering process. The Project Owner should primarily provide clinical knowledge and approve significant decisions. All feasible engineering work should be performed, coordinated, validated, documented, and continuously improved by the AI Factory.

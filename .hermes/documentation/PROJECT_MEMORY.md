# Project Memory — How It Works

**Location:** `.hermes/memory/`  
**Core File:** `PROJECT_MEMORY.md`  
**Last Updated:** 2026-07-21

---

## Overview

Project Memory is the AI Factory's persistent knowledge base. It captures the
current state of the GDES project — technology stack, architecture, metrics,
known issues, and decisions — so that agents and developers can quickly understand
the project without re-scanning the entire codebase.

---

## Memory Files

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `PROJECT_MEMORY.md` | Core project knowledge (metrics, stack, architecture) | Daily + after major changes |
| `MEMORY_INDEX.md` | Index and guide to all memory files | As needed |
| `KNOWN_ISSUES.md` | Tracked issues with severity, status, and workarounds | When issues discovered |
| `DECISIONS.md` | Architecture and design decision log | When decisions made |

---

## PROJECT_MEMORY.md — Core Memory

The primary memory file contains:

### Repository Overview
- Project name, aliases, locations
- Repository health and technical debt scores

### Technology Stack
- Complete technology stack table (backend, database, frontend, deployment, etc.)
- Package management details

### Architecture
- Deployment modes (Desktop vs Production)
- Key architecture patterns (DDD, service layer, middleware, Celery)
- Django application map (30 apps categorized by domain)

### Clinical Domain
- 9 disease profiles
- Statistical engine capabilities
- Referenced clinical guidelines

### Key Metrics
- Django app counts, models, views, serializers
- Test files, documentation files
- Service functions, URL patterns, middleware

### Git Status
- Current branch, CI/CD status
- Configuration files present

### Quick Reference
- Common commands
- Key settings locations

### AI Factory Status
- Bootstrap completion status
- Component counts (agents, prompts, workflows, etc.)

---

## KNOWN_ISSUES.md — Issue Tracker

Maintains a prioritized list of known issues:

### Issue Categories
- 🔴 **CRITICAL** — Must be fixed immediately
- 🟡 **HIGH-PRIORITY** — Should be fixed soon
- 🟢 **MEDIUM** — Fix when convenient

### Current Critical Issues (as of 2026-07-21)

1. ~~Hardcoded admin credentials~~ ✅ FIXED
2. Missing `exports` app in INSTALLED_APPS
3. Zero CI/CD pipeline
4. Critically low test coverage (~20-25%)
5. ~~All dependencies unpinned~~ ✅ FIXED

### High-Priority Issues
6. No CSP headers or rate limiting
7. Documentation sprawl (111+ root files)
8. God files (6 files > 1,000 LOC)
9. Temp/debug scripts at root
10. High coupling in clinic app (imports from 8 apps)

### Repository Metrics (from analysis)
| Metric | Value |
|--------|-------|
| Repository Health Score | 4.15/10 |
| Technical Debt Score | 6.8/10 |
| Estimated Test Coverage | ~20-25% |
| Django Apps | 30 (27 active) |
| Models | 86 |
| Views (FBV) | 129 |

---

## DECISIONS.md — Decision Log

Records architecture and design decisions with:
- **Date** of decision
- **Decision** made
- **Rationale** behind it
- **Status** (implemented, pending, superseded)

### Current Decisions

**D1: AI Factory Architecture**
- Implement Hermes as orchestrator with OpenCode (implementation) and
  Claude Code (review)
- Clear separation of concerns, maximum automation

**D2: Documentation Location**
- AI Factory documentation in `.hermes/` directory, separate from repo root
- Keep AI Factory infrastructure clean

**D3: Quality Gates**
- 8 mandatory quality gates with clinical safety as highest priority
- Comprehensive quality assurance

**D4: Workflow Standardization**
- Standardized workflows for all common development tasks
- Consistency, reproducibility, auditability

---

## MEMORY_INDEX.md — Navigation Guide

Simple index of all memory files with:
- File descriptions
- Update schedules
- Usage instructions

---

## How Memory Is Used

### By Hermes (Orchestrator)
1. Read `PROJECT_MEMORY.md` before planning any task
2. Check `KNOWN_ISSUES.md` to avoid known pitfalls
3. Reference `DECISIONS.md` for architectural consistency
4. Update memory after completing significant work

### By OpenCode (Implementer)
1. Read `PROJECT_MEMORY.md` to understand the codebase
2. Check `KNOWN_ISSUES.md` before investigating new bugs
3. Reference architecture patterns from memory

### By Claude Code (Reviewer)
1. Read `DECISIONS.md` to ensure consistency with past decisions
2. Read `PROJECT_MEMORY.md` for architecture context
3. Update `DECISIONS.md` when new decisions are made

### By Developers
1. Always read `PROJECT_MEMORY.md` before starting work
2. Record significant decisions in `DECISIONS.md`
3. Track known issues in `KNOWN_ISSUES.md`
4. Update `PROJECT_MEMORY.md` when metrics change

---

## Updating Memory

### Automated Updates
```bash
# Update project memory from live codebase data
python .hermes/scripts/update_project_memory.py
```

### Manual Updates
- Edit `PROJECT_MEMORY.md` directly when metrics change
- Add entries to `DECISIONS.md` when decisions are made
- Add entries to `KNOWN_ISSUES.md` when issues are discovered
- Update `MEMORY_INDEX.md` when files are added/removed

### When to Update
- After completing a feature or significant change
- After making an architectural decision
- After discovering a new issue
- During daily startup/shutdown
- When metrics change significantly

---

## Memory Maintenance Rules

1. **Accuracy** — All data in memory must reflect current reality
2. **Timeliness** — Update memory within the same session as changes
3. **Completeness** — Record all significant decisions and issues
4. **Conciseness** — Keep entries focused and actionable
5. **Traceability** — Link memory entries to source files/commits

---

## Auto-Update Script

The `update_project_memory.py` script:
1. Scans the repository for current metrics
2. Counts Django apps, models, views, serializers
3. Checks test coverage
4. Updates `PROJECT_MEMORY.md` with fresh data
5. Logs changes for audit trail

```bash
python .hermes/scripts/update_project_memory.py
```

---

## References

- `.hermes/memory/PROJECT_MEMORY.md` — Core memory (read this first)
- `.hermes/memory/KNOWN_ISSUES.md` — Known issues tracker
- `.hermes/memory/DECISIONS.md` — Decision log
- `.hermes/memory/MEMORY_INDEX.md` — Navigation guide
- `.hermes/scripts/update_project_memory.py` — Auto-update script

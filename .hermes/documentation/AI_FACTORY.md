# GDES AI Factory — System Overview

**Version:** 1.0  
**Status:** Bootstrap Complete  
**Last Updated:** 2026-07-21

---

## What Is the AI Factory?

The GDES AI Factory is an automated software engineering orchestration system built
around the GDES (Glomerular Disease Expert System) / BGDDR (Bangladesh Glomerular
Disease Data Registry) project. It coordinates multiple AI agents, standardized
workflows, reusable prompts, mandatory quality gates, and automation scripts to
manage the full development lifecycle of a clinical-grade Django application.

---

## Core Principles

1. **Separation of Concerns** — Different agents handle planning, implementation,
   review, testing, and release. No single agent does everything.
2. **Clinical Safety First** — Every workflow enforces a clinical safety quality gate
   that cannot be bypassed. Patient data handling follows HIPAA-compliant patterns.
3. **Automation Over Manual Work** — Daily startup/shutdown, repository scanning,
   report generation, and project memory updates are all scripted.
4. **Auditability** — All decisions, issues, and changes are logged in structured
   memory files for traceability.

---

## System Components

```
.hermes/
├── agents/          7 agent role definitions
├── config/          Factory configuration & delegation matrix
├── documentation/   This documentation set (11 guides)
├── memory/          Project memory, decisions, known issues
├── prompts/         12 reusable prompt templates
├── reports/         Generated analysis reports (8+)
├── scripts/         7 automation scripts
└── workflows/       12 standardized workflows
```

---

## Agent Roster

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Hermes** | Project Manager & Orchestrator | Plans, delegates, validates, reports |
| **OpenCode** | Primary Implementation | 90-95% of all coding work |
| **Claude Code** | Architecture & Expert Review | Design decisions, complex debugging |
| **GitHub Agent** | Version Control & CI/CD | Branches, PRs, releases, issues |
| **Testing Agent** | Quality Validation | pytest, ruff, mypy, coverage |
| **Documentation Agent** | Knowledge Management | API docs, guides, changelogs |
| **Release Agent** | Release Coordination | Versioning, changelogs, deployment |

---

## How It Works

### 1. Task Arrives
A feature request, bug report, or clinical rule update enters the system through
the user (project owner) or is identified during daily startup.

### 2. Hermes Plans & Delegates
Hermes reads project memory, analyzes the request, and creates an implementation
plan. Tasks are delegated to the appropriate agent(s) based on the delegation
matrix in `config/AGENT_ROLES.md`.

### 3. Implementation
OpenCode performs the actual coding. For architecture-level changes, Claude Code
reviews the design first. All agents report back to Hermes.

### 4. Quality Gates
Every change must pass 8 mandatory quality gates (defined in
`workflows/QUALITY_GATES.md`):

1. **pytest** — All tests pass
2. **ruff** — Linting clean
3. **mypy** — Type checking clean
4. **Migrations** — All apply cleanly
5. **Documentation** — Complete and current
6. **Architecture** — Patterns consistent
7. **Security** — No vulnerabilities
8. **Clinical Safety** — Validated (highest priority, non-bypassable)

### 5. Memory & Reporting
Project memory (`memory/PROJECT_MEMORY.md`) is updated after significant changes.
Reports are generated in `reports/`. The dashboard (`DASHBOARD.md`) reflects
current status.

---

## Configuration

Key settings live in `config/FACTORY_CONFIG.md`:

- **Primary Repository:** `C:\Users\User\Documents\GitHub\GDES`
- **AI Factory Root:** `E:\OneDrive\Project Hermes\.hermes`
- **Default Branch:** `main`
- **Commit Style:** Conventional Commits
- **Test Coverage Target:** 80%
- **Linting:** ruff (PEP 8)
- **Type Checking:** mypy (gradual)

---

## Clinical Safety

GDES handles clinical data for 9 glomerular disease profiles (IgAN, MN, FSGS,
MCD, Lupus Nephritis, AAV, Anti-GBM, Infection-related GN, C3G). The AI Factory
enforces:

- **Clinical rule changes** always require user (clinical expert) approval
- **Patient data** follows HIPAA-compliant patterns
- **Drug interaction** logic is validated against the knowledge base
- **Audit trail** is mandatory for all clinical operations
- **Patient safety** issues trigger immediate escalation and halt all other work

---

## Automation Scripts

| Script | Purpose |
|--------|---------|
| `daily_startup.sh` | Initialize a development session |
| `daily_shutdown.sh` | Preserve state at end of session |
| `repository_scan.py` | Scan and inventory the entire codebase |
| `update_project_memory.py` | Refresh project memory from live data |
| `validate_repository.sh` | Run all quality gates |
| `generate_reports.sh` | Generate analysis reports |
| `prepare_release.sh` | Prepare release artifacts |

---

## Getting Started

1. Run `bash .hermes/scripts/daily_startup.sh` to initialize
2. Read `.hermes/memory/PROJECT_MEMORY.md` for current state
3. Check `.hermes/DASHBOARD.md` for critical findings and priorities
4. Follow workflows in `.hermes/workflows/` for standardized procedures

---

## File Inventory

- **54+ files** across 8 directories
- **7 agents** with full role specifications
- **12 prompts** for common tasks
- **12 workflows** covering all development scenarios
- **8 quality gates** enforced on every change
- **7 automation scripts** for daily operations
- **8+ analysis reports** for repository intelligence

---

## References

- `config/FACTORY_CONFIG.md` — Factory settings and standards
- `config/AGENT_ROLES.md` — Delegation matrix and escalation paths
- `AI_FACTORY_STATUS.md` — Bootstrap status report
- `DASHBOARD.md` — Real-time metrics dashboard
- `memory/PROJECT_MEMORY.md` — Core project knowledge base

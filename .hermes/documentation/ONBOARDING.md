# Onboarding Guide — New Developer Guide

**Target Audience:** New developers and AI agents joining the GDES project  
**Time to Productive:** ~30 minutes with this guide

---

## Welcome to GDES

**GDES** (Glomerular Disease Expert System), also known as **BGDDR** (Bangladesh
Glomerular Disease Data Registry), is a Django-based clinical decision support
system for managing glomerular diseases. It supports 9 disease profiles and
includes a statistical analysis engine, medical knowledge base, and FHIR
interoperability.

---

## Quick Start

### 1. Understand the Project

Read these files in order:
1. `.hermes/documentation/AI_FACTORY.md` — System overview (5 min)
2. `.hermes/documentation/ARCHITECTURE.md` — Technical architecture (5 min)
3. `.hermes/memory/PROJECT_MEMORY.md` — Current project state (5 min)
4. `.hermes/DASHBOARD.md` — Critical findings and priorities (2 min)

### 2. Set Up Your Environment

```bash
# Clone the repository
git clone https://github.com/[org]/GDES.git
cd GDES

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Verify everything works
python manage.py runserver
python -m pytest
```

### 3. Run the AI Factory Startup

```bash
bash .hermes/scripts/daily_startup.sh
```

This initializes your session and gives you current priorities.

---

## Project Structure

### Repository Layout
```
GDES/
├── bgddr/              Django project settings
│   ├── settings.py     Main settings
│   ├── settings_prod   Production settings
│   ├── urls.py         Root URL configuration
│   ├── wsgi.py         WSGI entry point
│   └── asgi.py         ASGI entry point
├── [30 Django apps]    Clinical and support applications
├── .hermes/            AI Factory infrastructure
│   ├── agents/         7 agent definitions
│   ├── config/         Configuration files
│   ├── documentation/  This documentation set
│   ├── memory/         Project memory
│   ├── prompts/        12 reusable prompts
│   ├── reports/        Analysis reports
│   ├── scripts/        7 automation scripts
│   └── workflows/      12 standardized workflows
├── requirements.txt    Python dependencies
├── package.json        npm dependencies (Tailwind)
├── Dockerfile          Docker configuration
├── docker-compose.yml  Docker Compose config
└── manage.py           Django management
```

### Django Apps (by domain)

**Core Clinical (11 apps):**
patients, clinic, encounters, clinical, clinical_reasoning, treatments,
prescriptions, followup, scheduling, timeline, baseline

**Data & Analytics (6 apps):**
labs, biomarkers, biobank, pathology, analytics, studies

**Knowledge & Decision (3 apps):**
knowledge (most complex: 20 models, 29 serializers), decision, safety

**Support (9 apps):**
users, audit, feedback, reminders, events, bgddr, fhir, desktop

---

## Key Concepts

### Clinical Domain
GDES manages 9 glomerular disease profiles:
1. IgAN — IgA Nephropathy
2. MN — Membranous Nephropathy
3. FSGS — Focal Segmental Glomerulosclerosis
4. MCD — Minimal Change Disease
5. Lupus — Lupus Nephritis
6. AAV — ANCA-Associated Vasculitis
7. Anti-GBM — Anti-Glomerular Basement Membrane Disease
8. Infection-related — Infection-Related GN
9. C3G — C3 Glomerulopathy

### AI Factory
The AI Factory is the orchestration system you'll use to develop features.
Key components:
- **7 agents** — Specialized AI roles for different tasks
- **12 workflows** — Standardized procedures for common tasks
- **8 quality gates** — Mandatory validation before any change
- **12 prompts** — Reusable templates for consistent output
- **7 scripts** — Automation for daily operations

### Clinical Safety
**This is the most important rule:** Clinical safety is the highest priority.
- Clinical rule changes always require user (clinical expert) approval
- Patient data follows HIPAA-compliant patterns
- Patient safety issues trigger immediate escalation and halt all other work

---

## Essential Workflows

| When to Use | Workflow | File |
|-------------|----------|------|
| Starting work | Daily Startup | `workflows/daily-startup.md` |
| New feature | Feature Development | `workflows/feature-development.md` |
| Bug found | Bug Fix | `workflows/bug-fix.md` |
| Clinical change | Clinical Rule Update | `workflows/clinical-rule-update.md` |
| Architecture change | Architecture Review | `workflows/architecture-review.md` |
| Emergency | Emergency Hotfix | `workflows/emergency-hotfix.md` |
| Ending work | Daily Shutdown | `prompts/daily-shutdown.md` |

---

## Common Commands

```bash
# Development
python manage.py runserver              # Start dev server
python manage.py createsuperuser        # Create admin user

# Quality Checks
python -m pytest                        # Run tests
python -m pytest --cov=.               # Tests with coverage
ruff check .                            # Lint check
ruff check --fix .                      # Auto-fix linting
mypy . --ignore-missing-imports         # Type check

# Database
python manage.py migrate                # Apply migrations
python manage.py makemigrations         # Create migrations

# AI Factory
bash .hermes/scripts/daily_startup.sh   # Initialize session
bash .hermes/scripts/validate_repository.sh  # Run quality gates
bash .hermes/scripts/generate_reports.sh     # Generate reports
python .hermes/scripts/update_project_memory.py  # Update memory
```

---

## Where to Find Things

| You Need | Go To |
|----------|-------|
| Project overview | `.hermes/documentation/AI_FACTORY.md` |
| Architecture details | `.hermes/documentation/ARCHITECTURE.md` |
| Current project state | `.hermes/memory/PROJECT_MEMORY.md` |
| Known bugs/issues | `.hermes/memory/KNOWN_ISSUES.md` |
| Decision history | `.hermes/memory/DECISIONS.md` |
| Agent roles | `.hermes/agents/` and `.hermes/documentation/AGENT_ROLES.md` |
| Workflows | `.hermes/workflows/` and `.hermes/documentation/WORKFLOW_GUIDE.md` |
| Quality gates | `.hermes/workflows/QUALITY_GATES.md` |
| Analysis reports | `.hermes/reports/` |
| Dashboard | `.hermes/DASHBOARD.md` |
| Automation scripts | `.hermes/scripts/` |

---

## What to Know Before Contributing

### Do's
- ✅ Read project memory before starting work
- ✅ Follow existing Django patterns in the codebase
- ✅ Run quality gates before committing
- ✅ Write tests for new code (80% coverage target)
- ✅ Update documentation with code changes
- ✅ Use conventional commit messages
- ✅ Escalate clinical safety concerns immediately

### Don'ts
- ❌ Don't modify clinical rules without user approval
- ❌ Don't skip quality gates
- ❌ Don't push directly to main without a PR
- ❌ Don't ignore failing tests
- ❌ Don't hardcode credentials or secrets
- ❌ Don't make architecture decisions without review

---

## Getting Help

1. **Check existing docs** — `.hermes/documentation/` has 11 guides
2. **Read project memory** — `.hermes/memory/PROJECT_MEMORY.md`
3. **Check known issues** — `.hermes/memory/KNOWN_ISSUES.md`
4. **Ask the AI Factory** — Hermes can answer questions about the project
5. **Escalate clinical questions** — Always go to the user (clinical expert)

---

## References

- `.hermes/documentation/` — Complete documentation set (11 guides)
- `.hermes/memory/PROJECT_MEMORY.md` — Project knowledge base
- `.hermes/DASHBOARD.md` — Current status and priorities
- `.hermes/README.md` or `AI_FACTORY_STATUS.md` — Bootstrap status

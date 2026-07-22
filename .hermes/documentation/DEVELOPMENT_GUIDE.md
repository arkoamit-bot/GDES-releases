# Development Guide — Building Features for GDES

**Target Audience:** Developers and AI agents contributing to GDES  
**Prerequisites:** Python 3.11+, Django 5.0+, familiarity with DDD patterns

---

## Getting Started

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/[org]/GDES.git
cd GDES

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Desktop Mode (Windows)

```bash
# Desktop uses SQLite + Waitress
# Run via launcher scripts or:
python manage.py runserver 0.0.0.0:8000
```

---

## Development Workflow

### 1. Start Your Session

Use the Daily Startup prompt or script:
```bash
bash .hermes/scripts/daily_startup.sh
```

This will:
- Check git status and recent changes
- Run quality gates (pytest, ruff, mypy)
- Check for pending migrations
- Review project memory
- Suggest daily priorities

### 2. Create a Feature Branch

```bash
git checkout -b feature/[feature-name]
```

### 3. Implement Your Feature

Follow the Feature Development workflow in `.hermes/workflows/feature-development.md`:

**Step 1: Requirements Analysis**
- Understand the feature request
- Identify affected modules (check the 30 Django apps)
- Check existing patterns in the codebase
- Estimate complexity

**Step 2: Architecture Planning**
- Design the solution
- Identify model changes
- Plan API endpoints and UI changes
- For complex changes, request Claude Code review

**Step 3: Implementation**
- Create/update Django models in the appropriate app
- Create migrations: `python manage.py makemigrations`
- Implement views (prefer DRF ViewSets for API, FBV for UI)
- Create serializers for API endpoints
- Add URL routing
- Add admin configuration
- Create templates/JS as needed

**Step 4: Testing**
- Write unit tests using pytest
- Write integration tests
- Run full test suite: `python -m pytest`
- Verify edge cases

**Step 5: Quality Gates**
- Run `ruff check .` — fix any linting issues
- Run `mypy . --ignore-missing-imports` — fix type errors
- Verify migrations: `python manage.py makemigrations --check`
- Update documentation

---

## Project Structure

### Django Apps (by domain)

**Core Clinical:** patients, clinic, encounters, clinical, clinical_reasoning,
treatments, prescriptions, followup, scheduling, timeline, baseline

**Data & Analytics:** labs, biomarkers, biobank, pathology, analytics, studies

**Knowledge & Decision:** knowledge, decision, safety

**Support:** users, audit, feedback, reminders, events, bgddr, fhir, desktop

**API Layer:** api

### AI Factory Structure

```
.hermes/
├── agents/          Agent role definitions (7 files)
├── config/          Configuration (FACTORY_CONFIG.md, AGENT_ROLES.md)
├── documentation/   This documentation set (11 guides)
├── memory/          Project memory (4 files)
├── prompts/         Reusable prompts (12 files)
├── reports/         Analysis reports (8+ files)
├── scripts/         Automation scripts (7 files)
└── workflows/       Standardized workflows (12 files)
```

---

## Coding Standards

### Python / Django
- **PEP 8** compliance enforced by ruff
- **Type hints** encouraged (mypy in gradual mode)
- **Docstrings** for all public functions
- **Conventional Commits** for git messages

### Model Design
- Follow DDD patterns
- Use meaningful field names
- Add `__str__` methods to all models
- Include `Meta` classes with `verbose_name` and `ordering`
- Create migrations for all model changes

### View Design
- **DRF ViewSets** for API endpoints
- **Function-based views** for UI (existing pattern in clinic app)
- Include proper error handling
- Use Django's permission system

### Testing
- Use pytest (not unittest)
- Use fixtures for test data
- Minimum 80% coverage for new code
- Test both success and failure paths
- Mock external dependencies

### Documentation
- Markdown format for all documentation
- Include code examples
- Keep clinical terminology accurate
- Update relevant docs with any code changes

---

## Common Commands

```bash
# Development
python manage.py runserver              # Start dev server
python manage.py createsuperuser        # Create admin user
python manage.py collectstatic          # Collect static files

# Database
python manage.py migrate                # Apply migrations
python manage.py makemigrations         # Create migrations
python manage.py makemigrations --check # Verify no pending migrations

# Quality
python -m pytest                        # Run tests
python -m pytest --cov=.               # Run with coverage
ruff check .                            # Lint check
ruff check --fix .                      # Auto-fix linting
mypy . --ignore-missing-imports         # Type check

# AI Factory
bash .hermes/scripts/daily_startup.sh   # Initialize session
bash .hermes/scripts/validate_repository.sh  # Run quality gates
bash .hermes/scripts/generate_reports.sh     # Generate reports
python .hermes/scripts/update_project_memory.py  # Update memory
```

---

## Delegation Matrix

| Task Type | Primary Agent | Review Agent | Approval |
|-----------|---------------|--------------|----------|
| Feature Implementation | OpenCode | Hermes | User (if clinical) |
| Bug Fix | OpenCode | Hermes | Auto |
| Architecture Change | Claude Code | Hermes | User |
| Clinical Rule Update | OpenCode | Claude Code | User (required) |
| Documentation | OpenCode/Hermes | Self-review | Auto |
| Testing | Testing Agent | Hermes | Auto |
| Release | Release Agent | Hermes | User |

---

## Clinical Safety Rules

1. **Clinical rule changes** always require user (clinical expert) approval
2. **Patient data handling** follows HIPAA-compliant patterns
3. **Drug interactions** are validated against the knowledge base
4. **Audit trail** is mandatory for all clinical operations
5. **Patient safety issues** trigger immediate escalation and halt all other work

---

## Debugging Tips

1. Read `.hermes/memory/KNOWN_ISSUES.md` before investigating new bugs
2. Use the Bug Fix workflow in `.hermes/workflows/bug-fix.md`
3. Check `.hermes/reports/` for existing analysis
4. For architecture issues, escalate to Claude Code
5. For clinical domain questions, escalate to the user

---

## References

- `.hermes/workflows/feature-development.md` — Feature development workflow
- `.hermes/prompts/` — Reusable prompt templates
- `.hermes/config/FACTORY_CONFIG.md` — Project configuration
- `.hermes/memory/PROJECT_MEMORY.md` — Current project state
- `.hermes/reports/REPOSITORY_INVENTORY.md` — Full codebase inventory

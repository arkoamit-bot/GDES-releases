# System Architecture — GDES / BGDDR

**Last Updated:** 2026-07-21  
**Repository Health Score:** 4.15/10  
**Technical Debt Score:** 6.8/10

---

## Project Identity

- **Name:** GDES — Glomerular Disease Expert System
- **Also Known As:** BGDDR — Bangladesh Glomerular Disease Data Registry
- **Repository:** `C:\Users\User\Documents\GitHub\GDES`
- **AI Factory:** `E:\OneDrive\Project Hermes\.hermes`

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11+, Django 5.0+, Django REST Framework |
| **Database** | PostgreSQL (production), SQLite (desktop/dev) |
| **Frontend** | Django Templates, Tailwind CSS, vanilla JavaScript |
| **Deployment** | Docker + Docker Compose, Nginx, Gunicorn |
| **Desktop** | Waitress WSGI, PyInstaller, Windows batch scripts |
| **Task Queue** | Celery + Redis |
| **Testing** | pytest |
| **Statistical Engine** | Pure Python (KM, Cox PH, LMM, Aalen-Johansen, MICE) |
| **Package Management** | pip (requirements.txt), npm (package.json for Tailwind) |

---

## Deployment Modes

### Desktop Mode
```
SQLite + Waitress WSGI + PyInstaller (Windows)
```
- Self-contained desktop application
- Single-user deployment
- No external dependencies beyond Python

### Production Mode
```
PostgreSQL + Gunicorn + Nginx + Redis/Celery (Docker)
```
- Multi-user web application
- Docker Compose orchestration
- Background task processing via Celery

---

## Application Architecture

### Django Application Map (30 apps, 27 active)

#### Core Clinical Apps (11)
| App | Models | Views | Serializers | Purpose |
|-----|--------|-------|-------------|---------|
| **patients** | ✅ | ✅ | ✅ | Patient management & demographics |
| **clinic** | ❌ | 45 FBV | ❌ | UI-only app, 18 forms |
| **encounters** | ✅ | ✅ | ✅ | Clinical encounters & visits |
| **clinical** | ✅ | ✅ | ✅ | Clinical data & assessments |
| **clinical_reasoning** | 2 | 3 | 12 | AI-powered CDS (8,885 LOC) |
| **treatments** | ✅ | ✅ | ✅ | Treatment plans & protocols |
| **prescriptions** | ✅ | ✅ | ✅ | Medication management |
| **followup** | ✅ | ✅ | ✅ | Follow-up scheduling & tracking |
| **scheduling** | ✅ | ✅ | ✅ | Appointment scheduling |
| **timeline** | ✅ | ✅ | ✅ | Patient timeline view |
| **baseline** | ✅ | ✅ | ✅ | Baseline data management |

#### Data & Analytics Apps (6)
| App | Models | Views | Serializers | Purpose |
|-----|--------|-------|-------------|---------|
| **labs** | ✅ | ✅ | ✅ | Laboratory results & orders |
| **biomarkers** | ✅ | ✅ | ✅ | Biomarker tracking |
| **biobank** | ✅ | ✅ | ✅ | Biological sample management |
| **pathology** | 8 | ✅ | ✅ | Biopsy + GN/IgAN/Lupus/FSGS/Membranous |
| **analytics** | ✅ | ✅ | ✅ | Data analytics & reporting |
| **studies** | ✅ | ✅ | ✅ | Research study management |

#### Knowledge & Decision Apps (3)
| App | Models | Views | Serializers | Purpose |
|-----|--------|-------|-------------|---------|
| **knowledge** | 20 | 19 | 29 | Medical knowledge base (most complex) |
| **decision** | ✅ | ✅ | ✅ | Clinical decision support (legacy) |
| **safety** | ✅ | ✅ | ✅ | Clinical safety monitoring |

#### Support Apps (9)
| App | Models | Views | Serializers | Purpose |
|-----|--------|-------|-------------|---------|
| **users** | ✅ | ✅ | ✅ | User management & authentication |
| **audit** | ✅ | ✅ | ✅ | Audit trail & logging |
| **feedback** | 15 | 26 | 10 | User feedback system |
| **reminders** | ✅ | ✅ | ✅ | Reminder & notification system |
| **events** | ✅ | ✅ | ✅ | Event tracking |
| **bgddr** | ✅ | ✅ | ✅ | Bangladesh GDR registry (settings) |
| **fhir** | ✅ | ✅ | ✅ | FHIR interoperability |
| **desktop** | ✅ | ✅ | ✅ | Desktop deployment support |

#### API Layer
| App | Models | Views | Serializers | Purpose |
|-----|--------|-------|-------------|---------|
| **api** | ❌ | ❌ | ✅ | REST API layer |

---

## Architecture Patterns

### Domain-Driven Design (DDD)
- Django apps organized by clinical domain
- Domain models reflect real-world clinical entities
- Service layer pattern (39 service files, ~102 functions)

### API Layer
- DRF ViewSets for RESTful API (58 ViewSets, 86 Serializers)
- URL patterns: ~162 total
- DRF-YASG for OpenAPI documentation

### Middleware Stack
- 10 middleware components
- Audit logging middleware
- Feedback capture middleware
- Clinical safety middleware

### Background Processing
- Celery for async tasks (11 task modules)
- Redis as message broker (production)
- Desktop mode: synchronous processing

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Django Applications | 30 (27 active) |
| Database Models | 86 |
| Function-Based Views | 129 |
| DRF ViewSets | 58 |
| Serializers | 86 |
| Admin Classes | 73 |
| Management Commands | 35 |
| URL Patterns | ~162 |
| Service Functions | ~102 |
| Database Tables | 42 |
| Disease Profiles | 9 |
| Test Files | 23 |
| Documentation Files | 111+ |
| Middleware | 10 |

---

## Clinical Domain

### Disease Profiles (9)
1. **IgAN** — IgA Nephropathy
2. **MN** — Membranous Nephropathy
3. **FSGS** — Focal Segmental Glomerulosclerosis
4. **MCD** — Minimal Change Disease
5. **Lupus** — Lupus Nephritis
6. **AAV** — ANCA-Associated Vasculitis
7. **Anti-GBM** — Anti-Glomerular Basement Membrane Disease
8. **Infection-related** — Infection-Related GN
9. **C3G** — C3 Glomerulopathy

### Statistical Engine
- Kaplan-Meier survival analysis
- Cox Proportional Hazards
- Linear Mixed Models
- Competing Risks (Aalen-Johansen)
- MICE Imputation
- All validated against published datasets

### Referenced Guidelines
- KDIGO 2021/2025
- ADA Standards of Care
- BIRDEM Clinical Protocols
- BADAS Guidelines

---

## AI Factory Architecture

```
User (Clinical Expert & Project Owner)
    │
    ▼
Hermes (Project Manager & Orchestrator)
    │
    ├── OpenCode (90-95% implementation)
    ├── Claude Code (architecture review)
    ├── GitHub Agent (version control)
    ├── Testing Agent (quality validation)
    ├── Documentation Agent (knowledge mgmt)
    └── Release Agent (release coordination)
```

### Data Flow
1. User provides requirements → Hermes plans
2. Hermes delegates to OpenCode → OpenCode implements
3. For architecture changes → Claude Code reviews
4. Testing Agent validates → Quality gates enforced
5. Memory updated → Dashboard refreshed

---

## Known Architecture Issues

1. **God Files:** 6 files > 1,000 LOC (management_plan.py at 2,196 LOC)
2. **High Coupling:** clinic/forms.py imports from 8 different apps
3. **No CI/CD Pipeline:** No automated test runner configured
4. **Low Test Coverage:** ~20-25%, 10 apps have zero tests
5. **Documentation Sprawl:** 111+ markdown files at repository root

---

## Configuration Reference

- **Settings module:** `bgddr.settings`
- **Production settings:** `bgddr.settings_prod`
- **WSGI entry:** `bgddr.wsgi`
- **ASGI entry:** `bgddr.asgi`

---

## References

- `.hermes/reports/REPOSITORY_INVENTORY.md` — Full app inventory
- `.hermes/reports/TECHNOLOGY_STACK.md` — Tech stack analysis
- `.hermes/reports/CODE_COMPLEXITY_REPORT.md` — Complexity metrics
- `.hermes/reports/TECHNICAL_DEBT_REPORT.md` — Debt analysis
- `.hermes/memory/PROJECT_MEMORY.md` — Core project knowledge

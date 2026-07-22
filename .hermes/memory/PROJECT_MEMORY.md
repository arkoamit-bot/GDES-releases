# GDES Project Memory
## Last Updated: 2026-07-21 14:26:22

---

## Repository Overview

**Name:** GDES — Glomerular Disease Expert System
**Also Known As:** BGDDR (Bangladesh Glomerular Disease Data Registry)
**Location:** C:\Users\User\Documents\GitHub\GDES
**AI Factory:** E:\OneDrive\Project Hermes\.hermes
**Repository Health Score:** 4.15/10
**Technical Debt Score:** 6.8/10

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
| **Package Mgmt** | pip (requirements.txt), npm (package.json for Tailwind) |

---

## Architecture

### Deployment Modes
1. **Desktop Mode:** SQLite + Waitress + PyInstaller (Windows)
2. **Production Mode:** PostgreSQL + Gunicorn + Nginx + Redis/Celery (Docker)

### Key Architecture Patterns
- Django apps organized by clinical domain
- DRF ViewSets for API layer
- Service layer pattern (39 service files, ~102 functions)
- Middleware for audit logging, feedback capture
- Celery for background tasks (11 task modules)

---

## Django Application Map (30 apps)

### Core Clinical (11 apps)
| App | Models | Views | Serializers | Notes |
|-----|--------|-------|-------------|-------|
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

### Data & Analytics (6 apps)
| App | Models | Views | Serializers | Notes |
|-----|--------|-------|-------------|-------|
| **labs** | ✅ | ✅ | ✅ | Laboratory results & orders |
| **biomarkers** | ✅ | ✅ | ✅ | Biomarker tracking |
| **biobank** | ✅ | ✅ | ✅ | Biological sample management |
| **pathology** | 8 | ✅ | ✅ | Biopsy + GN/IgAN/Lupus/FSGS/Membranous |
| **analytics** | ✅ | ✅ | ✅ | Data analytics & reporting |
| **studies** | ✅ | ✅ | ✅ | Research study management |

### Knowledge & Decision (3 apps)
| App | Models | Views | Serializers | Notes |
|-----|--------|-------|-------------|-------|
| **knowledge** | 20 | 19 | 29 | Medical knowledge base (most complex) |
| **decision** | ✅ | ✅ | ✅ | Clinical decision support (legacy) |
| **safety** | ✅ | ✅ | ✅ | Clinical safety monitoring |

### Support (9 apps)
| App | Models | Views | Serializers | Notes |
|-----|--------|-------|-------------|-------|
| **users** | ✅ | ✅ | ✅ | User management & authentication |
| **audit** | ✅ | ✅ | ✅ | Audit trail & logging |
| **feedback** | 15 | 26 | 10 | User feedback system |
| **reminders** | ✅ | ✅ | ✅ | Reminder & notification system |
| **events** | ✅ | ✅ | ✅ | Event tracking |
| **baseline** | ✅ | ✅ | ✅ | Baseline data management |
| **bgddr** | ✅ | ✅ | ✅ | Bangladesh GDR registry (settings) |
| **fhir** | ✅ | ✅ | ✅ | FHIR interoperability |
| **desktop** | ✅ | ✅ | ✅ | Desktop deployment support |

### API Layer
| App | Models | Views | Serializers | Notes |
|-----|--------|-------|-------------|-------|
| **api** | ❌ | ❌ | ✅ | REST API layer |

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

### Guidelines Referenced
- KDIGO 2021/2025
- ADA Standards of Care
- BIRDEM Clinical Protocols
- BADAS Guidelines

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Django Apps | 30 (27 active) |
| Database Models | 86 |
| Function-Based Views | 129 |
| DRF ViewSets | 58 |
| Serializers | 86 |
| Admin Classes | 73 |
| Management Commands | 35 |
| URL Patterns | ~162 |
| Service Functions | ~102 |
| Service Files | 39 |
| Database Tables | 42 |
| Celery Task Modules | 11 |
| Test Files | 23 |
| Documentation Files | 111+ |
| Middleware | 10 |

---

## Git Status
- Current Branch: main (or latest)
- Repository has .claude and .opencode configs
- Docker Compose + Dockerfile for production
- No CI/CD pipeline configured

---

## Quick Reference

### Common Commands
```bash
# Run development server
python manage.py runserver

# Run tests
python -m pytest

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Key Settings
- Settings module: bgddr.settings
- Production settings: bgddr.settings_prod
- WSGI: bgddr.wsgi
- ASGI: bgddr.asgi

---

## AI Factory Status
- **Bootstrap:** COMPLETE (v1.0)
- **Agents:** 7 defined
- **Prompts:** 12 reusable
- **Workflows:** 11 standardized
- **Quality Gates:** 8 mandatory
- **Automation Scripts:** 7 ready
- **Reports:** 8 generated

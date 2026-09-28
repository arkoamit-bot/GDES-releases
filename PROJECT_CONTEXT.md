# GDES Project Memory & Context
Generated: AI Factory v1.0 Bootstrap

## 1. Project Overview
- **Name:** Glomerular Disease Expert System (GDES) / Bangladesh Glomerular Disease Data Registry (BGDDR)
- **Institution:** BIRDEM / BADAS, Bangladesh
- **Core Purpose:** Clinical expert system and data registry for glomerular diseases (DKD, 9 disease profiles), supporting clinical decision making, research, and patient management.

## 2. Technology Stack
- **Backend:** Django 5.0+, Django REST Framework (DRF)
- **Database:** PostgreSQL (Production) / SQLite (Desktop)
- **Frontend:** Tailwind CSS, HTML templates, JavaScript
- **Compute / Analytics:** NumPy, Pandas, SciPy, statsmodels (survival analysis, LMM, Cox PH)
- **Deployment:** Docker, PyInstaller + Waitress (Desktop)

## 3. Architecture & Apps
Total Django Apps: 30
Apps List: analytics, api, audit, baseline, bgddr, biobank, biomarkers, clinic, clinical, clinical_reasoning, decision, desktop, encounters, events, exports, feedback, fhir, followup, knowledge, labs, pathology, patients, prescriptions, reminders, safety, scheduling, studies, timeline, treatments, users

## 4. Dependencies
Total Packages: 18
Key Libraries: Django~=5.0.7, djangorestframework~=3.15.2, django-jazzmin~=3.0.1, WeasyPrint~=62.3, openpyxl~=3.1.5, pyreadstat~=1.2.7, pandas~=2.2.3, waitress~=3.0.2, whitenoise~=6.8.2, xhtml2pdf~=0.2.16, celery~=5.4.0, redis~=5.2.1, django-csp~=3.8.0        # Content-Security-Policy headers, django-ratelimit~=4.1.0  # Rate-limiting on auth endpoints, pytest~=8.3.4, pytest-cov~=6.0.0, ruff~=0.7.4, mypy~=1.13.0 ...

## 5. Engineering Standards
- **AI Factory Orchestrator:** Hermes Agent
- **Primary Implementation Agent:** OpenCode
- **Architecture Review Agent:** Claude Code
- **Version Control:** Branch strategy (`ai-factory-v1`, feature branches)
- **Quality Gates:** pytest, ruff, mypy, migration validation, clinical safety

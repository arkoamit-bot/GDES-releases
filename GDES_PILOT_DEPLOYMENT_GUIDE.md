# GDES Pilot Deployment Guide

**Version:** 6.5 Release Candidate  
**Date:** 2026-07-11  
**Target:** Single PC deployment for clinical pilot

---

## 1. System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10/11 (64-bit) | Windows 11 |
| Python | 3.12+ | 3.12+ |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB free | 2 GB free |
| Display | 1920x1080 | 1920x1080 |
| Database | SQLite (bundled) | SQLite (bundled) |
| Browser | Chrome / Edge / Firefox (latest) | Chrome (latest) |

No separate database server, web server, or message broker is required.

---

## 2. Installation Steps

Open PowerShell as Administrator and run:

```powershell
# 1. Extract GDES-v6.5-pilot.zip to C:\GDES
# 2. Open PowerShell as Administrator
# 3. Navigate to project root
cd C:\GDES\bgddr

# 4. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run database migrations
python manage.py migrate

# 7. Seed the knowledge base (104 clinical rules)
python manage.py seed_knowledge_base

# 8. Create an admin superuser
python manage.py createsuperuser

# 9. Start the development server
python manage.py runserver 0.0.0.0:8000
```

The application will be available at `http://localhost:8000`.

---

## 3. First-Time Setup

1. **Access the admin panel** at `http://localhost:8000/admin/`
2. **Login** with the superuser credentials created in Step 8 above.
3. **Verify the Knowledge Base:** navigate to `/admin/knowledge/knowledgebaseentry/` — it should show **209 rules**. If empty, re-run the seed command:
   ```
   python manage.py seed_knowledge_base
   ```
4. **Create pilot clinician accounts** with appropriate roles through the admin panel.

---

## 4. Architecture (Single-PC Pilot)

| Component | Pilot Configuration |
|-----------|-------------------|
| Database | SQLite (`db.sqlite3`) — no PostgreSQL |
| Web Server | Django dev server — no nginx/gunicorn |
| Background Tasks | Synchronous — no Celery/Redis |
| FHIR Server | Not configured — internal data only |
| Desktop | Optional PyInstaller `.exe` available |

---

## 5. Key Entry Points

### Clinical Views
| Endpoint | URL |
|----------|-----|
| Patient list | `/clinic/patients/` |
| Patient detail (11 tabs) | `/clinic/patients/{id}/` |

### Clinical Reasoning API (POST)
| Endpoint | Path |
|----------|------|
| Reasoning engine | `/api/v1/clinical_reasoning/profiles/reason/` |
| Explainability | `/api/v1/clinical_reasoning/profiles/explain/` |
| Management plan | `/api/v1/clinical_reasoning/profiles/management_plan/` |
| Monitoring plan | `/api/v1/clinical_reasoning/profiles/monitoring_plan/` |
| Follow-up schedule | `/api/v1/clinical_reasoning/profiles/followup_schedule/` |
| Investigation recommendations | `/api/v1/clinical_reasoning/profiles/investigation_recommendations/` |
| Drug toxicity | `/api/v1/clinical_reasoning/profiles/drug_toxicity/` |
| Treatment failure | `/api/v1/clinical_reasoning/profiles/treatment_failure/` |
| Disease validation | `/api/v1/clinical_reasoning/profiles/validate_disease/` |

### Administration
| Endpoint | URL |
|----------|-----|
| Admin dashboard | `/admin/knowledge-dashboard/` |
| Knowledge governance stats | `/api/v1/knowledge-base/governance_stats/` |

---

## 6. Data Backup

**Manual daily backup:**
```powershell
Copy-Item C:\GDES\bgddr\db.sqlite3 "C:\GDES\backups\db_$(Get-Date -Format yyyyMMdd).sqlite3"
```

**JSON dump backup:**
```powershell
python manage.py dumpdata > backup.json
```

**Recommended schedule:** Back up `db.sqlite3` daily before clinic hours.

---

## 7. Known Limitations (Pilot)

- No multi-user concurrent access (SQLite file-locking)
- No real-time SMS notifications (Twilio not configured)
- No FHIR interoperability (internal data only)
- No desktop auto-update
- Background tasks run synchronously (no Celery)
- Single institution only

---

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| Migration errors | Delete `db.sqlite3`, re-run `python manage.py migrate`, then `python manage.py seed_knowledge_base` |
| Port 8000 in use | `python manage.py runserver 8001` |
| Import errors | Ensure `.venv` is activated (`.\.venv\Scripts\Activate.ps1`) |
| Permission errors | Run PowerShell as Administrator |

---

## 9. Support

| Resource | Path |
|----------|------|
| Log files | `C:\GDES\bgddr\logs\` |
| Admin dashboard | `/admin/knowledge-dashboard/` |
| Knowledge governance stats | `/api/v1/knowledge-base/governance_stats/` |

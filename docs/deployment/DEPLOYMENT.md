# BGDDR — Production Deployment Guide

This document explains how to deploy the BGDDR registry from the development
scaffold to a production-like environment.

---

## 1. Pre-flight checklist

- [ ] PostgreSQL installed and a database created (`CREATE DATABASE bgddr;`)
- [ ] A dedicated Linux user or Windows service account for the app
- [ ] `DJANGO_SECRET_KEY` generated (≥ 50 random chars)
- [ ] Domain / IP decided (for `ALLOWED_HOSTS`)
- [ ] Reverse proxy or SSL terminator configured (nginx / Caddy / AWS ALB / Cloudflare)

---

## 2. Install dependencies

```bash
# Core + production
pip install -r requirements.txt

# PostgreSQL adapter (required for production)
pip install psycopg

# WSGI server (required for production)
pip install gunicorn
```

> **Windows shortcut:** run `setup_production.ps1` (PowerShell as Administrator)
> to install dependencies, set environment variables, create the PostgreSQL
> database, run migrations, and optionally migrate data from SQLite:
>
> ```powershell
> .\setup_production.ps1 -DbPassword "your_password" -SecretKey "optional_custom_key"
> ```

---

## 3. Environment variables

Create a `.env` file or export these in your process manager:

| Variable | Example | Required |
|----------|---------|----------|
| `DJANGO_SETTINGS_MODULE` | `bgddr.settings_prod` | Yes |
| `DJANGO_SECRET_KEY` | `change-me-50-char-random...` | Yes |
| `DJANGO_ALLOWED_HOSTS` | `bgddr.birdem.org,localhost` | Yes |
| `POSTGRES_DB` | `bgddr` | Yes |
| `POSTGRES_USER` | `bgddr_app` | Yes |
| `POSTGRES_PASSWORD` | `strong-password` | Yes |
| `POSTGRES_HOST` | `localhost` | Yes |
| `POSTGRES_PORT` | `5432` | No (default 5432) |

On Windows (PowerShell):
```powershell
$env:DJANGO_SETTINGS_MODULE = "bgddr.settings_prod"
$env:DJANGO_SECRET_KEY = "..."
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:POSTGRES_DB = "bgddr"
$env:POSTGRES_USER = "bgddr_app"
$env:POSTGRES_PASSWORD = "..."
```

---

## 4. Database migration & seed

```bash
python manage.py migrate --settings=bgddr.settings_prod
python manage.py seed_drugs --settings=bgddr.settings_prod
python manage.py seed_labs --settings=bgddr.settings_prod
python manage.py seed_roles --settings=bgddr.settings_prod
python manage.py createsuperuser --settings=bgddr.settings_prod
```

### Migrate existing SQLite data to PostgreSQL
If you have data in the SQLite `db.sqlite3` from development:

1. Ensure `psycopg` is installed: `pip install psycopg`
2. Edit `migrate_to_postgres.py` and set `PG_PASSWORD`.
3. Run: `python migrate_to_postgres.py`

This copies all rows from SQLite to PostgreSQL and resets sequences.

---

## 5. Static files

Whitenoise serves static files in production. Collect them once:

```bash
python manage.py collectstatic --no-input
```

This writes to `staticfiles/`.

---

## 6. Validate imported data

If you bulk-imported patients, run the validation command before going live:

```bash
python manage.py validate_patients
# or with CSV output for review
python manage.py validate_patients --csv patient_issues.csv
```

Resolve any duplicate patients or missing critical fields before production.

---

## 7. Run the server

### Option A: gunicorn (Linux / macOS / WSL)

```bash
gunicorn bgddr.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Put nginx in front for SSL termination and static file caching.

### Option B: Windows IIS + HttpPlatformHandler

1. Install Python and the app dependencies on the server.
2. Install `HttpPlatformHandler` in IIS.
3. Create a `web.config`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*"
           modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="C:\Path\To\Python\python.exe"
                  arguments="-m gunicorn bgddr.wsgi:application --bind 127.0.0.1:8000"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\Path\To\Logs\python.log"
                  startupTimeLimit="60"/>
  </system.webServer>
</configuration>
```

### Option C: Single Windows PC (dev-like but hardened)

Use the dev settings but with a local PostgreSQL:

```powershell
$env:DJANGO_SETTINGS_MODULE = "bgddr.settings_prod"
$env:POSTGRES_HOST = "localhost"
python manage.py runserver 0.0.0.0:8000
```

---

## 8. PDF engines

| Engine | Install | Quality | Notes |
|--------|---------|---------|-------|
| **WeasyPrint** | `pip install WeasyPrint` + GTK3 runtime | Best | Needs native libs. Install GTK for Windows from the link in README. |
| **xhtml2pdf** | `pip install xhtml2pdf` | Good | Pure Python, no native deps. Automatically used as fallback. |
| **HTML download** | Built-in | OK | User opens in browser and prints. Always available. |

The PDF view tries WeasyPrint first, then xhtml2pdf, then falls back to an HTML
download with a print button. The HTML preview (`/preview/`) always works.

---

## 9. Backup & maintenance

### Database
```bash
# PostgreSQL dump
pg_dump -U bgddr_app -h localhost bgddr > bgddr_backup_$(date +%F).sql

# SQLite (dev only)
cp db.sqlite3 db.sqlite3.$(date +%F).bak
```

### Prescription PDFs
`media/prescriptions/` — back up this directory alongside the database.

### Recompute analytics
```bash
python manage.py compute_outcomes
python manage.py compute_biomarkers
```

---

## 10. Health checks

After deploying, verify:

- [ ] `https://your-domain/` → Dashboard loads
- [ ] `https://your-domain/admin/` → Admin login
- [ ] `https://your-domain/api/v1/` → DRF browsable API (with auth)
- [ ] `/prescriptions/<id>/pdf/` → PDF downloads (or HTML fallback)
- [ ] `/exports/research-dataset/?fmt=csv` → De-identified CSV download
- [ ] `python manage.py validate_patients` → passes with no critical dupes

---

## 11. Security notes

- `SECRET_KEY` must be random and never committed to version control.
- `DEBUG = False` in production (enforced by `settings_prod`).
- `ALLOWED_HOSTS` must match your domain exactly.
- HTTPS is strongly recommended; enable HSTS in `settings_prod` once SSL is confirmed.
- The admin is at `/admin/` — consider changing the URL or adding IP restriction.
- API tokens are at `/api/v1/auth/token/` — rate-limit this endpoint if public-facing.

---

## 12. What's next (not in this build)

- **LDAP/SSO integration** for hospital auth (replace `createsuperuser` with AD sync).
- **S3 / MinIO** for media file storage instead of local disk.
- **Celery** for async outcome recomputation and nightly report generation.
- **Materialized views** in PostgreSQL for fast analytics dashboards.
- **Fine-Gray subdistribution regression** and REML (validated against R/lme4).

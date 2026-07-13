# GDES Deployment Guide

## Deployment Models

GDES supports two deployment models:

| Model | Backend | Server | Use Case |
|-------|---------|--------|----------|
| **Desktop (v7.3+)** | SQLite | Waitress | Single-user Windows PC (pilot phase) |
| **Production (future)** | PostgreSQL | Gunicorn | Multi-user hospital deployment |

The remainder of this guide covers both models.

---

## Desktop Deployment (Pilot — Recommended for v7.3)

### Overview
The desktop mode runs on a single Windows PC with SQLite. No Docker, PostgreSQL,
Redis, or Celery required. CDS events run in-process (with async semantics preserved
via synchronous fallback — no behavioural change, just slightly higher latency on
lab entry).

### Prerequisites
- Windows 10/11
- Python 3.10+
- No OneDrive sync on the DB folder (SQLite + cloud sync = corruption risk)

### Quick Start

```batch
:: Option A: source mode
cd bgddr
set DJANGO_SETTINGS_MODULE=bgddr.settings_desktop
python manage.py runserver 127.0.0.1:8000

:: Option B: packaged build (double-click)
start_gdes.bat
```

### Architecture (Desktop)

```
User → Waitress (8000) → Django App
                            ↓
                     SQLite (single file)
```

### Startup Sequence
1. `settings_desktop.py` loads — DEBUG off, localhost-only, persisted SECRET_KEY
2. Migrations applied automatically
3. First-run seeds: roles, labs, drugs, studies
4. Admin account creation dialog (Tkinter)
5. Startup backup taken (`Backups/startup_*.zip`)
6. Periodic backups every 6 hours
7. Browser opens to http://127.0.0.1:8000
8. Status window with Stop button (tray-less)

### Important Notes
- **Single machine only**: SQLite must not be opened across machines. OneDrive
  causes silent corruption. Keep the working folder on a local drive or enforce
  single-machine access via SOP.
- **No async**: Celery/Redis not available; all events dispatch synchronously.
  Acceptable for single-user latency (~500ms per CDS pass).
- **SMS reminders**: UI framework exists but no gateway wired. Label reads
  "Manual reminder log" until integration.
- **Backup**: Automatic on startup + every 6 hours. Exports also available from
  the UI (SPSS .sav, CSV).

---

## Production Deployment (Future — Multi-User)

GDES V7.3 and later can be deployed on Django 5+ with PostgreSQL 16, Redis 7,
Celery 5, and Nginx 1.25. This guide covers production deployment via Docker Compose.

### Prerequisites (Production)
- Docker & Docker Compose v2
- Domain name with DNS pointing to the server
- SSL certificate (Let's Encrypt or self-signed for testing)

### Quick Start (Production)

```bash
# 1. Clone & configure
git clone <repo> bgddr
cd bgddr
cp .env.example .env
# Edit .env with your secrets (DJANGO_SECRET_KEY, POSTGRES_PASSWORD)

# 2. Generate self-signed SSL cert (testing)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"

# 3. Start services
docker compose up -d

# 4. Create superuser
docker compose exec app python manage.py createsuperuser --settings=bgddr.settings_prod

# 5. Open https://localhost
```

### Architecture (Production)

```
Client → Nginx (443 SSL) → Gunicorn (8000) → Django App
                            ↓
                    Celery Worker → Redis
                            ↓
                    PostgreSQL 16
```

### Environment Variables (Production)
| Variable | Required | Default | Description |
|---|---|---|---|
| DJANGO_SECRET_KEY | Yes | - | Django secret key |
| DJANGO_ALLOWED_HOSTS | Yes | - | Comma-separated hostnames |
| POSTGRES_PASSWORD | Yes | - | Database password |
| POSTGRES_DB | No | bgddr | Database name |
| POSTGRES_USER | No | bgddr | Database user |
| REDIS_URL | No | redis://redis:6379/0 | Redis connection |

### Scaling (Production)
- Increase `--workers 4` in docker-compose.yml for Gunicorn (2-4 per CPU core)
- Increase `--concurrency=4` for Celery worker
- Add `celery_worker` service replicas for high volume

---

## Backup & Restore

### Desktop (SQLite)
```bash
# Automatic: startup + every 6h via launcher
# Manual:
python manage.py create_backup --reason manual
# Exports: UI → Export → SPSS .sav / CSV
```

### Production (PostgreSQL)
```bash
# Manual backup
docker compose exec postgres pg_dump -U bgddr bgddr > backup.sql

# Automatic daily backup (via Celery Beat + django-dbbackup or cron)
```

## Monitoring

### Desktop
- Logs: `Logs/bgddr.log` in the data directory
- CDS errors: red banner on patient detail page if a module fails
- System checks: `python manage.py check` — warns on TEST-* rules, governance gaps
- Health check: `GET /health/` returns `{"status":"ok","database":"ok"}`

### Production
- Health check: `GET /health/` returns `{"status":"ok","database":"ok"}`
- Logs: `docker compose logs -f app` / `docker compose logs -f celery_worker`
- Sentry: Set `SENTRY_DSN` in `.env` for error tracking

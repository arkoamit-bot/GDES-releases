"""
Django settings for the BGDDR registry — prescription module scaffold.

Minimal, runnable configuration. SQLite by default so it starts with no
external services; switch DATABASES to PostgreSQL for production (recommended,
for the materialized-view analytics layer and pgaudit).
"""
import os
from pathlib import Path

import django
from packaging.version import Version

try:
    # Celery is optional: the single-user desktop build ships without a
    # broker, and settings must stay importable there. The numeric fallback
    # below is only used when celery is absent.
    from celery.schedules import crontab
except ImportError:  # pragma: no cover - desktop build without celery
    crontab = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Security-critical settings are read from the environment. The dev defaults keep
# `runserver` working locally; production MUST set DJANGO_SECRET_KEY and
# DJANGO_ALLOWED_HOSTS — bgddr/settings_prod.py enforces this and forces DEBUG off.
# Dev-only fallback. Production (settings_prod.py / settings_deploy.py) must
# set DJANGO_SECRET_KEY via environment; both raise RuntimeError if missing.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [h.strip() for h in
                 os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
                 if h.strip()]

# --- Data directory (single-user Windows desktop) ---------------------------
# All mutable data lives under BGDDR_DATA_DIR. Defaults to the project directory
# for local development, so existing behaviour is unchanged.
#
#   <BGDDR_DATA_DIR>/
#       db.sqlite3  (+ -wal / -shm sidecars)   <-- MUST stay on LOCAL DISK
#       Backups/    ZIP backup archives          (safe to point at a synced folder)
#       Exports/    CSV / Excel / research datasets
#       Media/      prescription PDFs and uploads
#       Logs/       application logs
#
# PATIENT-SAFETY RULE: the live db.sqlite3 and its -wal/-shm sidecars must NEVER
# live in a cloud-synced folder (OneDrive, Dropbox, Google Drive, iCloud). The
# sync client can copy a half-written WAL page and silently corrupt the database.
# Only the closed ZIP backups may sync. The desktop launcher enforces this at
# startup (see desktop/hardening.py) and refuses to run against a synced DB path
# unless BGDDR_ALLOW_SYNCED_DB=1 is set (developer escape hatch only).
BGDDR_DATA_DIR = Path(os.environ.get("BGDDR_DATA_DIR", BASE_DIR)).resolve()
# Backups and media can be pointed at a *different* location (e.g. a OneDrive-
# synced folder) independently of BGDDR_DATA_DIR, so the live db.sqlite3 can stay
# on local disk while snapshots/uploads sync to the cloud. Syncing closed backup
# files and write-once media is safe; syncing a live, actively-written SQLite
# file is a corruption risk. The desktop launcher sets these two env vars from
# its first-run folder wizard; an explicit env var always wins.
BACKUPS_DIR = Path(os.environ.get("BGDDR_BACKUP_DIR", str(BGDDR_DATA_DIR / "Backups"))).resolve()
MEDIA_DIR = Path(os.environ.get("BGDDR_MEDIA_DIR", str(BGDDR_DATA_DIR / "Media"))).resolve()
EXPORTS_DIR = BGDDR_DATA_DIR / "Exports"
LOGS_DIR = BGDDR_DATA_DIR / "Logs"
# Additional runtime dirs (P1-4): imports (data ingest) and temp (scratch).
IMPORTS_DIR = BGDDR_DATA_DIR / "Imports"
TEMP_DIR = BGDDR_DATA_DIR / "Temp"
for _d in (BACKUPS_DIR, EXPORTS_DIR, MEDIA_DIR, LOGS_DIR, IMPORTS_DIR, TEMP_DIR):
    _d.mkdir(parents=True, exist_ok=True)

INSTALLED_APPS = [
    # "jazzmin" must come BEFORE django.contrib.admin so it can override the
    # admin templates. It is a drop-in theme: no ModelAdmin code changes needed.
    # See JAZZMIN_SETTINGS / JAZZMIN_UI_TWEAKS near the end of this file.
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    # BGDDR registry apps
    "patients",
    "encounters",
    "baseline",
    "labs",
    "pathology",
    "treatments",
    "prescriptions",
    # "biobank",  # DISABLED: GN Master Protocol v2 removed biobanking (not
    #             # feasible). Code retained under biobank/ for a future
    #             # amendment if a -80C biorepository becomes available.
    "analytics",
    "audit",
    "studies",
    "safety",
    "scheduling",
    "biomarkers",
    "exports",
    "api",
    "users",
    # Guided clinical-workflow UI. No models — registered so its static assets
    # (chart library) and management commands are picked up.
    "clinic",
    # GDES clinical decision support
    "clinical",
    "knowledge",
    "timeline",
    # Phase 3.2
    "reminders",
    # Phase 3.3
    "fhir",
    # Phase 5 — Clinical Intelligence & Explainable Decision Platform
    "events",
    "clinical_reasoning",
    # Phase 5.1 — Follow-up Engine
    "followup",
    # V8 — Field Error Reporting & Continuous Improvement
    "feedback",
    # Phase 6 — Clinical Evidence Intelligence (CEI)
    "clinical_evidence",
]

# --- Django REST Framework --------------------------------------------------
# Reads are open to any authenticated user; writes are gated per-model by the
# user's role (Group permissions) via DjangoModelPermissions. Token + session auth.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves the compiled static files directly from the WSGI app so
    # the desktop build needs no separate web server. No-op in dev (runserver
    # serves static itself). Must sit right after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Attributes audited changes to request.user (must follow AuthenticationMiddleware).
    "audit.middleware.AuditMiddleware",
    # V8 — Field Error Reporting & Performance Monitoring
    "feedback.middleware.FeedbackMiddleware",
]

ROOT_URLCONF = "bgddr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bgddr.context_processors.app_version",
            ],
        },
    },
]

WSGI_APPLICATION = "bgddr.wsgi.application"

# --- Auth -------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# Env-driven so the SAME Django ORM schema runs on SQLite now and PostgreSQL
# later with NO code or migration change. To migrate: set DJANGO_DB_ENGINE=postgres
# and the POSTGRES_* variables, install psycopg, then `migrate` + load the data.
# (Everything below uses the ORM only — no SQLite-specific features, no raw SQL.)
if os.environ.get("DJANGO_DB_ENGINE", "sqlite").lower().startswith("postgres"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "bgddr"),
            "USER": os.environ.get("POSTGRES_USER", "bgddr"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(os.environ.get("BGDDR_DB_PATH", BGDDR_DATA_DIR / "db.sqlite3")),
            # 30s busy-timeout avoids transient "database is locked" if OneDrive
            # briefly touches the file. Connection-level only — ignored on Postgres.
            # WAL journal mode makes the local db file far more resilient to
            # corruption from an unclean shutdown/crash (the scenario the backup
            # strategy protects against). Django 5.1+ supports OPTIONS["init_command"]
            # which runs the PRAGMA on each new connection; the PRAGMA is persistent
            # and idempotent. On Django 5.0 we omit it (fall back to default journal).
            "OPTIONS": {
                "timeout": 30,
            },
        }
    }
    _opts = DATABASES["default"]["OPTIONS"]
    if Version(django.get_version()) >= Version("5.1"):
        _opts["init_command"] = "PRAGMA journal_mode=WAL;"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# Under the data dir so the packaged (read-only) app can still collectstatic
# into a writable location. Equals BASE_DIR/staticfiles in local development.
STATIC_ROOT = BGDDR_DATA_DIR / "staticfiles"
# Project-level static assets (compiled Tailwind CSS, vendored JS). App static
# dirs (e.g. clinic/static) are found automatically by the app-dirs finder.
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = MEDIA_DIR
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Prescription file storage ----------------------------------------------
PRESCRIPTION_PDF_DIR = MEDIA_ROOT / "prescriptions"

# --- Automatic backup (single-user desktop) ---------------------------------
# Consumed by bgddr/backup.py. Timestamped .sqlite3 snapshots in Backups/.
# --- V8 online evidence retrieval (Layer 5) --------------------------------
# OFF by default: the pilot is offline-first. When explicitly enabled, the
# evidence lookup queries ONLY approved sources (PubMed via NCBI E-utilities)
# with a clinician-entered text query — it never transmits patient data and is
# never invoked automatically. Enable with GDES_AI_ONLINE_EVIDENCE=1.
AI_ONLINE_EVIDENCE_ENABLED = os.environ.get("GDES_AI_ONLINE_EVIDENCE", "0") == "1"

# Vera Health Clinical AI Integration
# Set VERAHEALTH_API_KEY for the enterprise API (api.verahealth.ai).
# Alternatively, configure Vera Web credentials via ProviderConfiguration.
VERA_API_BASE_URL = os.environ.get("VERA_API_BASE_URL", "")
VERAHEALTH_API_KEY = os.environ.get("VERAHEALTH_API_KEY", "")
VERAHEALTH_MODEL = os.environ.get("VERAHEALTH_MODEL", "vera-clinical-1")

BACKUP_CONFIG = {
    "directory": str(BACKUPS_DIR),
    "max_backups": int(os.environ.get("BGDDR_MAX_BACKUPS", "60")),
    "interval_hours": int(os.environ.get("BGDDR_BACKUP_INTERVAL_HOURS", "6")),
    # P1-1 tiered ZIP retention (newest N kept per tier).
    "tiers": {"Daily": 7, "Weekly": 8, "Monthly": 12},
}

# --- Drug catalogue auto-update (medex.com.bd/brands) ------------------------
# A full refresh walks ~848 catalogue pages at 0.4s each (~6 min of traffic),
# and the catalogue changes slowly, so the default is weekly. Every knob is
# env-overridable so a deployment can retune without a code change.
#
# `min_row_ratio` is the safety gate: a scrape that returns far fewer rows
# than the last good run means MedEx changed its markup, the site is serving
# a partial page, or the run was cut short. Rather than import a truncated
# catalogue, the run is rejected and the database is left alone.
DRUG_SYNC_CONFIG = {
    "enabled": os.environ.get("BGDDR_DRUG_SYNC_ENABLED", "1") == "1",
    # 168h = weekly. 0 disables the interval check (manual/--force only).
    "interval_hours": int(os.environ.get("BGDDR_DRUG_SYNC_INTERVAL_HOURS", "168")),
    "delay": float(os.environ.get("BGDDR_DRUG_SYNC_DELAY", "0.4")),
    # Reject a scrape below this fraction of the last good row count.
    "min_row_ratio": float(os.environ.get("BGDDR_DRUG_SYNC_MIN_ROW_RATIO", "0.5")),
    # Take a DB backup before an unattended (scheduled) import.
    "backup_before_import": os.environ.get(
        "BGDDR_DRUG_SYNC_BACKUP", "1") == "1",
    "csv_path": str(IMPORTS_DIR / "medex_brands.csv"),
}

# Default output folder for `export_dataset` / UI exports.
EXPORT_DIR = EXPORTS_DIR

# WhiteNoise: compress static at collectstatic time. Non-manifest variant so a
# missing asset never 500s the page (robustness over cache-busting for desktop).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# --- Logging (P1-4: split, rotated logs under Logs/) ------------------------
# Four subsystem logs, each RotatingFileHandler (5 MB x 5):
#   application.log  general app + django (root)
#   startup.log      launcher / boot narrative (the "bgddr" logger)
#   backup.log       backup subsystem (the "bgddr.backup" logger)
#   migration.log    written directly by desktop/safe_migrate.py (own rotation)
def _rotating(filename):
    return {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOGS_DIR / filename),
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 5,
        "encoding": "utf-8",
        "formatter": "verbose",
    }


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "application": _rotating("application.log"),
        "startup": _rotating("startup.log"),
        "backup": _rotating("backup.log"),
    },
    "root": {"handlers": ["console", "application"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console", "application"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console", "application"], "level": "ERROR", "propagate": False},
        # Launcher / boot narrative → startup.log (also mirrored to console).
        "bgddr": {"handlers": ["console", "startup", "application"], "level": "INFO", "propagate": False},
        "bgddr.backup": {"handlers": ["console", "backup"], "level": "INFO", "propagate": False},
    },
}

# --- Prescription / clinic configuration -----------------------------------
# Letterhead shown on the printed prescription.
CLINIC = {
    "name_en": "BIRDEM General Hospital — Department of Nephrology",
    "name_bn": "বারডেম জেনারেল হাসপাতাল — নেফ্রোলজি বিভাগ",
    "address": "122 Kazi Nazrul Islam Avenue, Shahbag, Dhaka 1000",
    "registry": "Bangladesh Glomerular Disease & Diabetes Registry (BGDDR)",
}

# Follow-up scheduling (protocol §7.6): weekly Tuesday GN clinic, 15 slots,
# ±7-day visit windows.
SCHEDULING = {
    "clinic_weekday": 1,      # Monday=0 ... Tuesday=1
    "session_capacity": 15,
    "window_days": 7,
}

# --- Celery Background Task Configuration (Phase 3.2) -----------------------
# Enables async processing for reminders, lab alerts, report generation.
# Requires a running Redis server (localhost:6379 by default).
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Dhaka"
CELERY_BEAT_SCHEDULE = {
    "send-due-visit-reminders": {
        "task": "reminders.tasks.send_due_visit_reminders",
        "schedule": 43200,  # every 12 hours
    },
    "send-overdue-visit-reminders": {
        "task": "reminders.tasks.send_overdue_visit_reminders",
        "schedule": 86400,  # every 24 hours
    },
    "detect-lab-trends": {
        "task": "labs.tasks.detect_lab_trends",
        "schedule": 21600,  # every 6 hours
    },
    # Drug catalogue refresh. Weekly: the MedEx catalogue is ~848 pages and
    # changes slowly, so this costs ~6 min of traffic per week. The task
    # itself re-checks DRUG_SYNC_CONFIG and no-ops when not due, so a beat
    # that fires early is harmless.
    "sync-medex-drugs": {
        "task": "prescriptions.tasks.sync_medex_drugs",
        # Mon 03:17 Asia/Dhaka. Falls back to a plain 7-day interval where
        # celery isn't installed.
        "schedule": (crontab(hour=3, minute=17, day_of_week=1)
                     if crontab else 604800),
    },
}

# Path to a Bengali Unicode TTF for PDF embedding. Drop e.g.
# NotoSansBengali-Regular.ttf into prescriptions/static/prescriptions/fonts/.
# If the file is absent the PDF still renders (system font fallback).
BENGALI_FONT_PATH = (
    BASE_DIR / "prescriptions" / "static" / "prescriptions" / "fonts"
    / "NotoSansBengali-Regular.ttf"
)

# --- Admin UI theme (django-jazzmin) ---------------------------------------
# A drop-in skin for the Django admin — the interface clinicians and
# coordinators use for all data entry. Pure configuration: no ModelAdmin code
# changes are required (unlike Tailwind-based themes that need a new base
# class). Branding follows the prescription letterhead (deep indigo #26215C).
JAZZMIN_SETTINGS = {
    "site_title": "BGDDR Registry",
    "site_header": "BGDDR",
    "site_brand": "BGDDR Registry",
    # The admin "View site" link and brand point back to the app dashboard.
    "site_url": "/",
    "site_logo": None,                       # drop a logo at static/ and set its path
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "BGDDR — Glomerular Disease & Diabetes Registry",
    "copyright": "BIRDEM General Hospital — Dept. of Nephrology",
    # Global search box in the top bar searches patients first.
    "search_model": ["patients.Patient", "encounters.ClinicalEncounter"],
    # Top navigation bar — quick links to the things people open most.
    "topmenu_links": [
        {"name": "← Back to Registry", "url": "/"},
        {"name": "Due visits", "url": "/clinic/worklist/#due"},
        {"name": "Overdue", "url": "/clinic/worklist/#overdue"},
        {"name": "Research export", "url": "/exports/research-dataset/?fmt=csv"},
        {"app": "patients"},
    ],
    "usermenu_links": [
        {"name": "Registry home", "url": "/", "icon": "fas fa-house"},
        {"name": "Backups & restore", "url": "admin:backups", "icon": "fas fa-database"},
        {"name": "API tokens", "url": "/admin/authtoken/tokenproxy/"},
    ],
    # Left sidebar: show as a tree, ordered for the clinical workflow.
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "patients", "encounters", "baseline", "labs", "pathology",
        "prescriptions", "treatments", "scheduling", "biomarkers",
        "analytics", "safety", "studies", "exports", "audit",
        "clinical", "knowledge", "decision", "timeline",
        "auth", "authtoken", "api",
    ],
    # FontAwesome 5 icons per app/model (sidebar + breadcrumbs).
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "authtoken": "fas fa-key",
        "patients": "fas fa-user-injured",
        "encounters": "fas fa-notes-medical",
        "baseline": "fas fa-clipboard-list",
        "labs": "fas fa-flask",
        "pathology": "fas fa-microscope",
        "treatments": "fas fa-pills",
        "prescriptions": "fas fa-prescription",
        "scheduling": "fas fa-calendar-check",
        "biomarkers": "fas fa-dna",
        "analytics": "fas fa-chart-line",
        "safety": "fas fa-triangle-exclamation",
        "studies": "fas fa-vials",
        "exports": "fas fa-file-export",
        "audit": "fas fa-history",
        "clinical": "fas fa-stethoscope",
        "knowledge": "fas fa-book-medical",
        "timeline": "fas fa-timeline",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    # Detail views: render related inlines as tabs to cut scrolling.
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    # Offline-capable: don't pull fonts from Google's CDN (render-blocking).
    "use_google_fonts_cdn": False,
    # Retint AdminLTE's "primary" colour to the BADAS sky accent.
    "custom_css": "css/admin_sky.css",
}

# Colour + layout. AdminLTE "primary" classes, retinted to BADAS sky via
# the custom_css above (static/css/admin_sky.css).
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    # Newer Jazzmin replaced "dark_mode_theme" with "default_theme_mode"
    # ("light" | "dark" | "auto"). "auto" follows the OS setting and matches the
    # behaviour the old dark_mode_theme=None was shimmed to, without the
    # deprecation warning that fired on every admin page load.
    "default_theme_mode": "auto",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

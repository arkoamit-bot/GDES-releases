"""
Production settings for BGDDR — SQLite single-user deployment.

This is the production settings file for the current Windows desktop deployment.
It keeps SQLite as the database backend while maintaining full PostgreSQL
compatibility for future migration.

Usage:
    set DJANGO_SETTINGS_MODULE=bgddr.settings_deploy
    python manage.py runserver

All PostgreSQL-compatible features are preserved:
- Django ORM only (no raw SQL)
- Standard ForeignKey, ManyToManyField, constraints
- No SQLite-specific features used
"""
import os

from .settings import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
DEBUG = False

# For single-user deployment, read from environment or use a secure fallback.
# In production multi-user mode, this MUST be set via env var.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable is required in production.")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# CSRF / session security (relaxed for single-user localhost; tighten for network)
# For single-user desktop deployment on localhost, setting these to False is
# acceptable since traffic never leaves the machine. Set to True if the app
# is served behind a reverse proxy (see .env.example).
#
# The transport-level settings below follow the same env-driven pattern. They
# default to off so the desktop launcher can serve plain HTTP on 127.0.0.1, but a
# LAN/TLS deployment MUST set DJANGO_SECURE_SSL=true (plus a reverse proxy
# terminating TLS) — otherwise session/CSRF cookies and BGDDR patient data cross
# the network in cleartext. `manage.py check --deploy` reports security.W004,
# W008, W012 and W016 for as long as these are off.
def _env_flag(name, default="False"):
    return os.environ.get(name, default).strip().lower() in ("true", "1", "yes", "on")


CSRF_COOKIE_SECURE = _env_flag("CSRF_COOKIE_SECURE")
SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE")
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable only once HTTPS is confirmed working end-to-end: HSTS is sticky and a
# misconfiguration here can lock every browser out of the app for a year.
SECURE_SSL_REDIRECT = _env_flag("DJANGO_SECURE_SSL")
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "0") or 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = bool(SECURE_HSTS_SECONDS)
SECURE_HSTS_PRELOAD = bool(SECURE_HSTS_SECONDS)

if SECURE_HSTS_SECONDS and not SECURE_SSL_REDIRECT:
    raise RuntimeError(
        "DJANGO_HSTS_SECONDS is set but DJANGO_SECURE_SSL is not. HSTS is only "
        "delivered over HTTPS, so this combination can never take effect. Enable "
        "DJANGO_SECURE_SSL=true once TLS terminates in front of the app."
    )

# ---------------------------------------------------------------------------
# Database — SQLite (single-user deployment)
# PostgreSQL-compatible: all Django ORM, no SQLite-specific features.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        # SQLite options for reliability
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# ---------------------------------------------------------------------------
# Application directories — production folder structure
# BGDDR/
#   ├── db.sqlite3
#   ├── Backups/
#   ├── Exports/
#   ├── Media/
#   └── Logs/
# ---------------------------------------------------------------------------
BACKUP_DIR = BASE_DIR / "Backups"  # noqa: F405
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

EXPORT_DIR = BASE_DIR / "Exports"  # noqa: F405
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MEDIA_ROOT = BASE_DIR / "Media"  # noqa: F405
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_URL = "media/"

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405

PRESCRIPTION_PDF_DIR = MEDIA_ROOT / "prescriptions"
PRESCRIPTION_PDF_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = BASE_DIR / "Logs"  # noqa: F405
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging — file + console
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "bgddr.log",
            "maxBytes": 10_485_760,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "backup_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "backup.log",
            "maxBytes": 5_242_880,  # 5 MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
    "loggers": {
        "bgddr.backup": {
            "handlers": ["backup_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Auto-backup configuration
# ---------------------------------------------------------------------------
BACKUP_CONFIG = {
    "enabled": True,
    "directory": str(BACKUP_DIR),
    "max_backups": 30,  # keep last 30 backups
    "backup_on_startup": True,
    "backup_interval_hours": 4,  # backup every 4 hours while running
}

# ---------------------------------------------------------------------------
# Export configuration
# ---------------------------------------------------------------------------
EXPORT_CONFIG = {
    "directory": str(EXPORT_DIR),
    "default_format": "xlsx",
    "de_identified_by_default": True,
}

# ---------------------------------------------------------------------------
# Clinic (same as base settings, preserved here for clarity)
# ---------------------------------------------------------------------------
CLINIC = {
    "name_en": "BIRDEM General Hospital — Department of Nephrology",
    "name_bn": "বারডেম জেনারেল হাসপাতাল — নেফ্রোলজি বিভাগ",
    "address": "122 Kazi Nazrul Islam Avenue, Shahbag, Dhaka 1000",
    "registry": "Bangladesh Glomerular Disease & Diabetes Registry (BGDDR)",
}

# ---------------------------------------------------------------------------
# Scheduling (same as base settings)
# ---------------------------------------------------------------------------
SCHEDULING = {
    "clinic_weekday": 1,      # Monday=0 ... Tuesday=1
    "session_capacity": 15,
    "window_days": 7,
}

# ---------------------------------------------------------------------------
# Bengali font for PDF (same as base settings)
# ---------------------------------------------------------------------------
BENGALI_FONT_PATH = (
    BASE_DIR / "prescriptions" / "static" / "prescriptions" / "fonts"  # noqa: F405
    / "NotoSansBengali-Regular.ttf"
)

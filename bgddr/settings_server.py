"""
GDES on a clinic LAN server: several clinicians at once, PostgreSQL, behind
Caddy. The Windows install lives in deploy/windows (see docs/WINDOWS_SERVER.md).

    DJANGO_SETTINGS_MODULE=bgddr.settings_server

Everything site-specific comes from the environment, or from a .env file
beside manage.py (GDES_ENV_FILE overrides the path). Nothing here is a secret.

Differences from the desktop profile (settings_deploy.py):
  * PostgreSQL is required, never SQLite.
  * ALLOWED_HOSTS must be set explicitly; there is no localhost fallback.
  * Session and CSRF cookies have their own names. Browsers do not separate
    cookies by port, so on a machine that also serves the DKD registry
    (http://<ip>/) GDES (http://<ip>:8080/) would otherwise overwrite DKD's
    login cookie and each app would keep logging the other one out.
  * Secure-only cookies follow GDES_HTTPS. Phase 1 is plain HTTP on the clinic
    LAN; forcing Secure cookies there makes every login silently fail.
  * The data directory must not be inside a cloud-synced folder.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def _load_env_file():
    path = Path(os.environ.get("GDES_ENV_FILE")
                or Path(__file__).resolve().parent.parent / ".env")
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _flag(name, default="0"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def _list(name):
    return [v.strip() for v in os.environ.get(name, "").split(",") if v.strip()]


_load_env_file()
# Read by the base settings at import time, so set before importing them.
os.environ["DJANGO_DB_ENGINE"] = "postgres"
os.environ["DJANGO_DEBUG"] = "0"

from .settings import *  # noqa: E402,F401,F403
from .settings import BGDDR_DATA_DIR, DATABASES, LOGS_DIR  # noqa: E402

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 40 or SECRET_KEY.startswith("dev-only"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set to a long random value.")

ALLOWED_HOSTS = _list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must list the addresses clinicians use "
        "(e.g. 192.168.7.55,dr-wasim,127.0.0.1,localhost).")
CSRF_TRUSTED_ORIGINS = _list("GDES_CSRF_TRUSTED_ORIGINS")

# --- Cookies and transport ----------------------------------------------------
SESSION_COOKIE_NAME = "gdes_sessionid"
CSRF_COOKIE_NAME = "gdes_csrftoken"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True

HTTPS = _flag("GDES_HTTPS")
SESSION_COOKIE_SECURE = HTTPS
CSRF_COOKIE_SECURE = HTTPS
if HTTPS:
    # TLS terminates at Caddy, which sets X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False            # Caddy redirects; Django never sees port 80
SECURE_HSTS_SECONDS = int(os.environ.get("GDES_HSTS_SECONDS", "0") or 0)

# --- Database -------------------------------------------------------------------
_db = DATABASES["default"]
if not _db.get("PASSWORD"):
    raise ImproperlyConfigured("POSTGRES_PASSWORD must be set (see .env).")
_db["HOST"] = os.environ.get("POSTGRES_HOST", "127.0.0.1")
_db["CONN_MAX_AGE"] = 60
_db["CONN_HEALTH_CHECKS"] = True

# --- Data location --------------------------------------------------------------
_synced = ("onedrive", "dropbox", "google drive", "googledrive", "icloud")
if any(s in str(BGDDR_DATA_DIR).lower() for s in _synced) and not _flag("GDES_ALLOW_SYNCED_DATA"):
    raise ImproperlyConfigured(
        f"BGDDR_DATA_DIR ({BGDDR_DATA_DIR}) is inside a cloud-synced folder. Server "
        f"data (uploads, exports) must live on a local disk.")

# --- Logging ----------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "{levelname} {asctime} {name} {message}",
                               "style": "{"}},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(Path(LOGS_DIR) / "gdes-server.log"),
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "console": {"level": "WARNING", "class": "logging.StreamHandler",
                    "formatter": "verbose"},
    },
    "root": {"handlers": ["file", "console"], "level": "INFO"},
    "loggers": {"django": {"handlers": ["file", "console"], "level": "INFO",
                           "propagate": False}},
}

"""
Production settings for BGDDR.

Import from base settings and override security, database, static files, and
logging for a real deployment.
"""
import os
from pathlib import Path
from .settings import *  # noqa: F401,F403

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ---------------------------------------------------------------
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "0"

# SECRET_KEY must be set via environment variable in production.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")  # noqa: F405
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable is required in production.")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = [
        "localhost", 
        "127.0.0.1",
        "gdes.dreamarray.com"
    ]

# CSRF Trusted Origins (Crucial for HTMX and Django POST forms on HTTP/HTTPS)
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost,http://127.0.0.1,http://gdes.dreamarray.com,https://gdes.dreamarray.com"
).split(",")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS if origin.strip()]

# CSRF / session security
# NOTE: Set to False if testing on http://localhost without SSL certificate
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "False").lower() in ("true", "1")
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS (Enable in .env once HTTPS is fully active on Nginx)
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 3600

# --- Database (MariaDB / MySQL) ---------------------------------------------
DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MYSQL_DATABASE", "bgddr"),
        'USER': os.environ.get("MYSQL_USER", "bgddr"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD", "bgddr_secure_password"),
        'HOST': os.environ.get("MYSQL_HOST", "mariadb"),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --- Middleware -------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serves static assets efficiently
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditMiddleware",
]

# --- Static & Media Files ----------------------------------------------------
STATIC_URL = "/static/"   # FIXED: Added leading slash to prevent broken assets on sub-routes
STATIC_ROOT = BASE_DIR / "staticfiles"

# Local source directory for custom assets (e.g. FontAwesome, HTMX, custom CSS)
STATIC_SOURCE_DIR = BASE_DIR / "static"
STATIC_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

STATICFILES_DIRS = [
    STATIC_SOURCE_DIR,
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = "/media/"   # FIXED: Added leading slash
MEDIA_ROOT = BASE_DIR / "media"

# Ensure runtime directories exist
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

# --- Logging ----------------------------------------------------------------
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "bgddr.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# --- Prescription File Storage ----------------------------------------------
PRESCRIPTION_PDF_DIR = MEDIA_ROOT / "prescriptions"
PRESCRIPTION_PDF_DIR.mkdir(parents=True, exist_ok=True)

# --- Jazzmin Admin Theming --------------------------------------------------
if "JAZZMIN_SETTINGS" in globals():
    JAZZMIN_SETTINGS["welcome_sign"] = "BGDDR — Production Registry"  # noqa: F405
    JAZZMIN_SETTINGS["copyright"] = "BIRDEM General Hospital — Dept. of Nephrology"  # noqa: F405
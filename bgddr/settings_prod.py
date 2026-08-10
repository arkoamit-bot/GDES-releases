"""
Production settings for BGDDR.

Import from base settings and override security, database, static files, and
logging for a real deployment. Usage:

    DJANGO_SETTINGS_MODULE=bgddr.settings_prod python manage.py ...

Prerequisites (install separately; not in requirements.txt by default):
    pip install psycopg gunicorn
"""
import os
from .settings import *  # noqa: F401,F403

# --- Security ---------------------------------------------------------------
DEBUG = False
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

# CSRF / session security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS (enable once HTTPS is confirmed working)
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# --- Database (PostgreSQL) --------------------------------------------------
DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MYSQL_DATABASE", "gdes"),
        'USER': os.environ.get("MYSQL_USER", "gdes"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD", "pass"),
        'HOST': os.environ.get("MYSQL_HOST", "127.0.0.1"), # or database host IP
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --- Static & media files ----------------------------------------------------
# Whitenoise serves static files in production.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # add after security
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditMiddleware",
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# Ensure media directories exist at runtime
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
(STATIC_ROOT).mkdir(parents=True, exist_ok=True)

# --- Logging ----------------------------------------------------------------
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
            "filename": BASE_DIR / "logs" / "bgddr.log",  # noqa: F405
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

# Create log directory
(BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)  # noqa: F405

# --- Prescription file storage ----------------------------------------------
# Where finalized prescription PDFs are saved.
PRESCRIPTION_PDF_DIR = MEDIA_ROOT / "prescriptions"
PRESCRIPTION_PDF_DIR.mkdir(parents=True, exist_ok=True)

# --- Jazzmin admin theming (production tweaks) -------------------------------
JAZZMIN_SETTINGS["welcome_sign"] = "BGDDR — Production Registry"  # noqa: F405
JAZZMIN_SETTINGS["copyright"] = "BIRDEM General Hospital — Dept. of Nephrology"  # noqa: F405

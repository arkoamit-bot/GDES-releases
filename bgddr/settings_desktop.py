"""
Desktop settings for the single-user Windows build of BGDDR.

Same schema, same ORM, SQLite backend — just hardened for a packaged localhost
app:  DEBUG off, a SECRET_KEY that persists across restarts, and localhost-only
hosts.  Data (db, Backups, Exports, Media, Logs) lives under BGDDR_DATA_DIR,
which the launcher points at the application folder so the whole thing syncs
through OneDrive.

    DJANGO_SETTINGS_MODULE=bgddr.settings_desktop

To move to the future PostgreSQL / multi-user deployment, nothing here needs to
change — set DJANGO_DB_ENGINE=postgres + POSTGRES_* and use settings_prod.py.
"""
import secrets

from .settings import *  # noqa: F401,F403
from .settings import BGDDR_DATA_DIR

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Persist the SECRET_KEY in the data folder so sessions/logins survive restarts
# (a fresh random key every launch would log the user out each time).
_key_file = BGDDR_DATA_DIR / ".secret_key"
if _key_file.exists():
    SECRET_KEY = _key_file.read_text(encoding="utf-8").strip()
else:
    SECRET_KEY = secrets.token_urlsafe(64)
    try:
        _key_file.write_text(SECRET_KEY, encoding="utf-8")
    except OSError:
        pass

# Localhost HTTP only — do NOT force secure cookies/redirects (would break the
# plain-HTTP desktop session). These get enabled later in settings_prod.py.
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]

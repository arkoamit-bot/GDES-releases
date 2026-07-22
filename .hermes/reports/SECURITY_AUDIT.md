# GDES Security Audit Report

**Generated:** 2026-07-21  
**Repository:** C:\Users\User\Documents\GitHub\GDES

---

## 1. Executive Summary

| Category | Rating | Findings |
|----------|--------|----------|
| Secret Management | ⚠️ Acceptable | Proper env-based secrets; dev fallback is insecure |
| Hardcoded Credentials | 🔴 HIGH | 3 files contain hardcoded admin credentials |
| Authentication | ✅ Good | Token auth + session auth via DRF |
| Debug Mode | ⚠️ Conditional | DEBUG defaults to ON in dev settings |
| Security Headers | 🔴 HIGH | CSP and rate-limiting disabled |
| File Security | ✅ Good | .env properly gitignored |
| Subprocess Usage | ⚠️ Medium | subprocess calls without shell=True (safe) |
| eval/exec | ✅ Good | No eval/exec detected |
| Input Validation | ⚠️ Unknown | Requires manual code review |

## 2. Hardcoded Credentials (CRITICAL)

### 🔴 Hardcoded Admin Password

Three launcher files contain hardcoded admin credentials:

| File | Line | Credential |
|------|------|------------|
| `desktop/launcher.py` | 684 | `username, password = "admin", "bgddr-admin"` |
| `desktop/launcher-Dr-Wasim.py` | 519 | `username, password = "admin", "bgddr-admin"` |
| `desktop/launcher-Dr-Wasim-2.py` | 563 | `username, password = "admin", "bgddr-admin"` |

**Risk:** The password `bgddr-admin` is committed to source control. Even though these are desktop-only launchers, any clone of the repository exposes these credentials. If the default admin user is created with this password in production, it's a severe vulnerability.

**Recommendation:** 
- Use environment variables or a first-run wizard that prompts for credentials
- Never commit default passwords to source control
- Force password change on first login

## 3. Secret Key Management

| Setting | File | Value | Risk |
|---------|------|-------|------|
| SECRET_KEY | settings.py | `os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-change-me")` | ⚠️ Weak default |
| SECRET_KEY | settings_prod.py | `os.environ.get("DJANGO_SECRET_KEY", "")` | ✅ Empty default, fails safe |
| SECRET_KEY | settings_deploy.py | `os.environ.get("DJANGO_SECRET_KEY", "")` | ✅ Empty default, fails safe |
| SECRET_KEY | settings_desktop.py | Reads from file or generates `secrets.token_urlsafe(64)` | ✅ Good |

### Assessment
- **Dev settings** use a well-known default string — acceptable for local dev only
- **Prod/Deploy settings** correctly fail if no secret is provided
- **Desktop settings** generate a random key and persist to file — good approach
- ⚠️ **Risk:** If anyone runs `manage.py runserver` without setting `DJANGO_SECRET_KEY`, the insecure default is used

## 4. Environment Configuration

### `.env.example` — Proper Template
```
✅ DJANGO_SECRET_KEY=change-this-to-a-long-random-string
✅ DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
✅ DJANGO_DEBUG=0
✅ POSTGRES_PASSWORD=change-this-to-a-strong-password
✅ CSRF_COOKIE_SECURE=True
✅ SESSION_COOKIE_SECURE=True
```

### `.gitignore` Coverage
```
✅ .env (line 35) — properly excluded
✅ db.sqlite3, db.sqlite3-wal, db.sqlite3-shm — database files excluded
✅ Backups/, Exports/, Media/, Logs/ — data dirs excluded
```

### `.env` File in Repo
**None found** — ✅ No actual .env file is committed.

## 5. Debug Mode Analysis

| Setting | DEBUG Default | Risk |
|---------|--------------|------|
| `settings.py` | `os.environ.get("DJANGO_DEBUG", "1") == "1"` — **ON by default** | ⚠️ |
| `settings_prod.py` | `DEBUG = False` | ✅ |
| `settings_deploy.py` | `DEBUG = False` | ✅ |
| `settings_desktop.py` | `DEBUG = False` | ✅ |

**Risk:** If `DJANGO_DEBUG` env var is not set, debug mode is ON in dev settings. Django debug mode exposes stack traces, SQL queries, and settings to any user.

## 6. Security Headers

### 🔴 Missing Security Headers

The following security packages are **commented out** in requirements.txt:

| Package | Purpose | Impact |
|---------|---------|--------|
| `django-csp>=3.8` | Content-Security-Policy headers | XSS vulnerability risk |
| `django-ratelimit>=4.1` | Rate limiting on auth endpoints | Brute-force attack risk |

### Current Security Settings (from settings.py)
From the INSTALLED_APPS and REST_FRAMEWORK config:
- ✅ Token authentication enabled
- ✅ Session authentication enabled
- ⚠️ No CSP headers
- ⚠️ No rate limiting
- ⚠️ No HSTS headers configured
- ⚠️ No X-Frame-Options explicitly set (Django defaults apply)

## 7. Subprocess Usage

All subprocess calls use `subprocess.Popen` or `subprocess.run` **without** `shell=True`:

| File | Usage | Safe? |
|------|-------|-------|
| `bgddr/updater.py` | `subprocess.Popen(...)` with detached process | ✅ No shell=True |
| `desktop/launcher-Dr-Wasim-2.py` | `subprocess.run(...)` with `CREATE_NO_WINDOW` | ✅ No shell=True |
| `desktop/launcher-Dr-Wasim.py` | `subprocess.run(...)` with `CREATE_NO_WINDOW` | ✅ No shell=True |
| `desktop/launcher.py` | `subprocess.Popen(...)` | ✅ No shell=True |

**Assessment:** ✅ All subprocess calls are safe from command injection.

## 8. Code Execution Risks

| Pattern | Count | Risk |
|---------|-------|------|
| `eval()` | 0 | ✅ None found |
| `exec()` | 0 | ✅ None found |
| `pickle.loads()` | 0 | ✅ None found |
| `yaml.load()` (unsafe) | 0 | ✅ None found |

## 9. Data Security Concerns

### SQLite Database Risk
The project uses SQLite as its primary database with explicit warnings about cloud-sync corruption:
- ✅ Settings docstrings warn against syncing live SQLite files
- ✅ Desktop launcher has hardening checks (`BGDDR_ALLOW_SYNCED_DB`)
- ⚠️ But the core concern is also about **data at rest encryption** — SQLite databases are unencrypted by default

### Patient Data (PHI)
This is a clinical registry containing patient health information. Additional concerns:
- ⚠️ No data encryption at rest configured
- ⚠️ No audit logging middleware visible (beyond the `audit` app's consent model)
- ⚠️ No HIPAA-specific security controls visible

## 10. TODO/FIXME Technical Debt

| File | Issue |
|------|-------|
| `desktop/launcher-Dr-Wasim.py:263` | `TODO: set after creating the repo` — placeholder GitHub repo |

## 11. Recommendations

| Priority | Action |
|----------|--------|
| 🔴 **CRITICAL** | Remove hardcoded `"admin"/"bgddr-admin"` credentials from all launcher files |
| 🔴 **CRITICAL** | Enable `django-csp` for Content-Security-Policy headers |
| 🔴 **CRITICAL** | Enable `django-ratelimit` on authentication endpoints |
| 🟡 **HIGH** | Change dev SECRET_KEY fallback to a random value that raises on use |
| 🟡 **HIGH** | Add `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT` for production |
| 🟡 **HIGH** | Add `X_FRAME_OPTIONS = 'DENY'` explicitly |
| 🟡 **MEDIUM** | Set `DEBUG = False` as the default in dev settings (require opt-in) |
| 🟡 **MEDIUM** | Add database encryption for SQLite (sqlcipher) or migrate to PostgreSQL |
| 🟡 **MEDIUM** | Implement HIPAA-aligned audit logging |
| 🟢 **LOW** | Add `SECURE_CONTENT_TYPE_NOSNIFF = True` |
| 🟢 **LOW** | Add `SESSION_COOKIE_HTTPONLY = True` |

---

*Report generated by automated static analysis. Manual penetration testing recommended for production deployment.*

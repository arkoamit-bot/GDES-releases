# Known Issues & Workarounds

## Tracked Issues

### 🔴 CRITICAL Issues

#### ~~1. Hardcoded Admin Credentials~~ ✅ FIXED (2026-07-21)
- **Issue:** Admin credentials ("admin"/"bgddr-admin") hardcoded in 3 launcher files
- **Fix:** Replaced with secure 16-char random password generation + clear logging
- **Status:** RESOLVED

#### ~~2. Missing `exports` App~~ 🔄 IN PROGRESS
- **Issue:** `exports` listed in INSTALLED_APPS but directory does not exist
- **Status:** Agent creating stub app

#### 3. Zero CI/CD Pipeline ~~🔴 CRITICAL~~ 🔄 IN PROGRESS
- **Issue:** No automated test runner or CI/CD pipeline configured
- **Status:** Agent creating GitHub Actions workflow

#### 4. Critically Low Test Coverage (~20-25%) 🔴 IN PROGRESS
- **Issue:** 10 of 29 apps have NO test files at all
- **Status:** Agent creating tests for clinical_reasoning (highest priority)

#### ~~5. All Dependencies Unpinned~~ ✅ FIXED (2026-07-21)
- **Issue:** Every dependency uses `>=` with no upper bounds; no lock file
- **Fix:** All dependencies pinned with ~= (compatible release) operators
- **Status:** RESOLVED

#### 1. Hardcoded Admin Credentials
- **Issue:** Admin credentials ("admin"/"bgddr-admin") hardcoded in 3 launcher files
- **Files:** 3 launcher files (~44KB, ~36KB, ~30KB each)
- **Impact:** Security vulnerability — credentials in source code
- **Workaround:** Remove credentials, use environment variables
- **Plan:** Immediate security fix required

#### 2. Missing `exports` App
- **Issue:** `exports` listed in INSTALLED_APPS but directory does not exist
- **Impact:** Will cause ModuleNotFoundError at startup
- **Workaround:** Create stub app or remove from INSTALLED_APPS
- **Plan:** Investigate and resolve

#### 3. Zero CI/CD Pipeline
- **Issue:** No automated test runner or CI/CD pipeline configured
- **Impact:** No automated quality validation
- **Workaround:** Manual quality gate execution
- **Plan:** Set up automated pipeline

#### 4. Critically Low Test Coverage (~20-25%)
- **Issue:** 10 of 29 apps have NO test files at all
- **Impact:** High regression risk, especially for clinical apps
- **Critical untested apps:** clinical_reasoning (8,885 LOC), clinic (2,276 LOC)
- **Workaround:** Priority test creation for clinical apps
- **Plan:** Systematic test coverage improvement

#### 5. All Dependencies Unpinned
- **Issue:** Every dependency uses `>=` with no upper bounds; no lock file
- **Impact:** Vulnerable to breaking changes in updates
- **Workaround:** Pin dependencies, generate lock file
- **Plan:** Dependency audit and pinning

### 🟡 HIGH-PRIORITY Issues

#### 6. No CSP Headers or Rate Limiting
- **Issue:** django-csp and django-ratelimit commented out in settings
- **Impact:** Security exposure for production deployment
- **Plan:** Enable and configure security middleware

#### 7. Documentation Sprawl
- **Issue:** 111+ markdown files at repository root
- **Impact:** Hard to find authoritative documentation
- **Plan:** Consolidate documentation into structured format

#### 8. God Files (6 files > 1,000 LOC)
- **Issue:** management_plan.py alone is 2,196 LOC with 9 disease profiles
- **Impact:** Maintenance complexity, testing difficulty
- **Plan:** Refactor into modular components

#### 9. Temp/Debug Scripts at Root
- **Issue:** 8 temp/debug scripts (_tmp_ms_test.py, tmp_audit_c3.py, etc.)
- **Impact:** Repository clutter, confusion
- **Plan:** Clean up and move to scripts/ directory

#### 10. High Coupling in Clinic App
- **Issue:** clinic/forms.py imports from 8 different apps
- **Impact:** Tight coupling makes changes risky
- **Plan:** Refactor to reduce inter-app dependencies

## Key Repository Metrics (from analysis agents)

| Metric | Value |
|--------|-------|
| Django Apps | 30 (27 active) |
| Models | 86 |
| Views (FBV) | 129 |
| Views (CBV) | 1 |
| DRF ViewSets | 58 |
| Serializers | 86 |
| Forms | 22 |
| Admin Classes | 73 |
| Management Commands | 35 |
| Templates | 9 |
| Migrations | 64 |
| Test Files | 23 |
| Celery Tasks | 11 |
| URL Patterns | ~162 |
| Service Functions | ~102 |
| Database Tables | 42 |
| Disease Profiles | 9 |
| Repository Health Score | 4.15/10 |
| Technical Debt Score | 6.8/10 |
| Estimated Test Coverage | ~20-25% |

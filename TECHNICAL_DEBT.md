# BGDDR — Technical Debt & Known Issues

## Overview

This document catalogs known technical debt, deprecated patterns, areas needing refactoring, and potential improvements identified during the Phase 1 codebase analysis.

---

## 1. Database & ORM

### 1.1 SQLite as Default
- **Issue**: SQLite is the default database even for multi-user scenarios
- **Impact**: "database is locked" errors under concurrent access, no materialized views, no pgaudit
- **Mitigation**: 30s busy-timeout configured; PostgreSQL available via environment variable
- **Refactor**: Consider making PostgreSQL the default for non-desktop deployments

### 1.2 No Migration for Biobank Disable
- **Issue**: `biobank` app is disabled in `INSTALLED_APPS` but code remains
- **Impact**: Dead code in `biobank/` directory, potential confusion
- **Refactor**: Either remove biobank entirely or document as future feature

### 1.3 Patient.latest_egfr Cache
- **Issue**: `Patient.latest_egfr` is a denormalized cache updated by labs app
- **Impact**: Can become stale if lab results are entered out of order or deleted
- **Mitigation**: Updated on every lab result entry
- **Refactor**: Consider computing on-the-fly or using a signal

---

## 2. Service Layer

### 2.1 Analytics Services - No External Dependencies
- **Issue**: All statistical methods (KM, Cox, LMM, MICE) are pure-Python implementations
- **Impact**: Less battle-tested than scipy/statsmodels; may have edge cases
- **Benefit**: Fully auditable, portable, no R/scipy dependency
- **Refactor**: Consider adding optional scipy-backed implementations for validation

### 2.2 Outcome Engine - Monolithic Function
- **Issue**: `compute_patient_outcome()` is a 299-line function with many internal helpers
- **Impact**: Hard to test individual components, difficult to extend
- **Refactor**: Break into smaller, testable functions; consider strategy pattern for disease-specific logic

### 2.3 Reconciliation Engine - Signature Comparison
- **Issue**: `TreatmentExposure.signature` and `PrescriptionItem.signature` compare strings
- **Impact**: Case-sensitive, whitespace-sensitive comparisons could miss equivalent regimens
- **Mitigation**: Both use `.strip().lower()` for normalization
- **Refactor**: Consider canonical form or regex-based comparison

### 2.4 Knowledge Rule Engine - Feature Extraction
- **Issue**: `extract_patient_features()` imports models lazily to avoid circular imports
- **Impact**: Runtime import overhead, potential ImportError caught silently
- **Refactor**: Consider a feature registry pattern or dependency injection

---

## 3. Prescriptions

### 3.1 PDF Generation - Dual Libraries
- **Issue**: Both WeasyPrint and xhtml2pdf are in requirements.txt
- **Impact**: WeasyPrint requires GTK/native libs; xhtml2pdf is pure-Python fallback
- **Mitigation**: Code tries WeasyPrint first, falls back to xhtml2pdf
- **Refactor**: Document which library is used in which context; consider removing one

### 3.2 Bengali Font Path
- **Issue**: `BENGALI_FONT_PATH` points to a specific font file that may not exist
- **Impact**: PDF renders without Bengali if font missing (graceful fallback)
- **Refactor**: Bundle the font or document installation steps

### 3.3 Prescription Versioning
- **Issue**: `new_version_from()` copies items by setting `pk=None` and saving
- **Impact**: Works but creates orphaned PKs; no version chain tracking
- **Refactor**: Consider `previous_version` FK for audit trail

---

## 4. Pathology

### 4.1 Review Status Computation
- **Issue**: `_recompute_status()` is called on every review submission
- **Impact**: O(n) field comparison for concordance check; acceptable for small n
- **Refactor**: Consider caching concordance result

### 4.2 PathologyReview.KEY_FIELDS
- **Issue**: KEY_FIELDS is a class constant listing fields to compare
- **Impact**: Must be manually updated if new fields are added to PathologyReview
- **Refactor**: Consider introspection or decorator-based field registration

---

## 5. Studies

### 5.1 Randomization Seed
- **Issue**: `random_seed` is a single integer per study
- **Impact**: Deterministic but simple; no per-stratum seeding
- **Mitigation**: Stratum-specific RNG derived from seed + CRC32 of stratum string
- **Refactor**: Document seed management protocol

### 5.2 Eligibility Screening
- **Issue**: `screen()` returns `(bool, list)` but criteria are not defined in the code shown
- **Impact**: Eligibility logic may be incomplete or hardcoded
- **Refactor**: Ensure criteria are configurable per study

---

## 6. Scheduling

### 6.1 Clinic Day Assignment
- **Issue**: `_assign_clinic_day()` prefers closest day with capacity
- **Impact**: Can overbook if all days in window are full
- **Mitigation**: Coordinator resolves overbooking manually
- **Refactor**: Consider waitlist or automatic rescheduling

### 6.2 Early Safety Visits
- **Issue**: `immunosuppressed` flag is passed to `generate_schedule()` but not stored
- **Impact**: Cannot retroactively determine why early safety visits were created
- **Refactor**: Store reason on ScheduledVisit or Patient model

---

## 7. Users

### 7.1 UserProfile Role Sync
- **Issue**: `UserProfile.save()` syncs Django Group membership
- **Impact**: Race condition if profile saved concurrently; group may be stale
- **Mitigation**: Acceptable for single-user desktop; multi-user needs review
- **Refactor**: Consider signal-based sync or transaction isolation

### 7.2 Invitation Token
- **Issue**: `Invitation.token` is generated via `secrets.token_urlsafe(32)`
- **Impact**: Secure but no rate limiting on token generation
- **Refactor**: Consider rate limiting or CAPTCHA for production

---

## 8. GDES (Clinical Decision Support)

### 8.1 Knowledge Base Rule Structure
- **Issue**: Rules are stored as JSON in `KnowledgeBaseEntry.rule_data`
- **Impact**: No schema validation; malformed rules silently fail
- **Refactor**: Add JSON schema validation or migration to structured models

### 8.2 Decision Service - Hardcoded Profiles
- **Issue**: `DISEASE_PROFILES` is a hardcoded list in `decision/services.py`
- **Impact**: Adding new diseases requires code changes
- **Refactor**: Move to database-driven configuration (KnowledgeBaseEntry)

### 8.3 Feature Extraction - Import Catches
- **Issue**: `extract_patient_features()` uses bare `except ImportError` and `except AttributeError`
- **Impact**: Silent failures if model structure changes
- **Refactor**: Use explicit model imports or dependency injection

---

## 9. Exports

### 9.1 Research Dataset - Column Order
- **Issue**: Column order is defined in `COLUMNS` list; must be maintained manually
- **Impact**: Breaking changes if columns are reordered
- **Refactor**: Consider ordered dict or schema definition

### 9.2 SPSS Export - Variable Labels
- **Issue**: SPSS export relies on pyreadstat for variable/value labels
- **Impact**: Labels must be maintained in code, not database
- **Refactor**: Consider label registry in database

---

## 10. Frontend

### 10.1 Tailwind CSS
- **Issue**: Tailwind is compiled via Node.js (`tailwind.config.js`)
- **Impact**: Requires Node.js for build; static output committed
- **Refactor**: Consider pre-built CSS or CDN for simpler deployment

### 10.2 Jazzmin Admin Theme
- **Issue**: `jazzmin` is a third-party admin theme with custom CSS
- **Impact**: Tied to AdminLTE; may not support Django admin changes
- **Mitigation**: Custom CSS override (`static/css/admin_sky.css`)
- **Refactor**: Monitor Django admin compatibility

---

## 11. Desktop Deployment

### 11.1 PyInstaller Packaging
- **Issue**: Desktop build uses PyInstaller (referenced in `build_exe.ps1`)
- **Impact**: Large bundle size; platform-specific builds needed
- **Refactor**: Document build process; consider alternative packagers

### 11.2 OneDrive Sync
- **Issue**: SQLite file can corrupt during OneDrive sync if write in progress
- **Mitigation**: 30s busy-timeout; single-user design
- **Refactor**: Consider WAL mode or file locking

---

## 12. Testing

### 12.1 Test Coverage
- **Issue**: Test files exist but coverage is unknown
- **Impact**: Regressions may go undetected
- **Refactor**: Add coverage reporting; target critical paths

### 12.2 Analytics Validation
- **Issue**: Cox, KM, LMM implementations validated against known datasets
- **Impact**: Good for core algorithms; edge cases may exist
- **Refactor**: Add more edge case tests; compare with R/scipy outputs

---

## 13. Documentation

### 13.1 Inline Comments
- **Issue**: Code has good docstrings but some complex functions lack inline comments
- **Impact**: New developers may struggle with analytics code
- **Refactor**: Add comments to analytics/services/ functions

### 13.2 API Documentation
- **Issue**: No auto-generated API docs (e.g., DRF browsable API or OpenAPI)
- **Impact**: API consumers must read code
- **Refactor**: Add drf-spectacular for OpenAPI schema generation

---

## 14. Security

### 14.1 SECRET_KEY
- **Issue**: Default `SECRET_KEY` is `"dev-only-insecure-change-me"`
- **Impact**: Must be overridden in production
- **Mitigation**: `settings_prod.py` enforces override
- **Refactor**: Add startup check for default key

### 14.2 DEBUG Mode
- **Issue**: `DEBUG` defaults to `True` (from `DJANGO_DEBUG` env var)
- **Impact**: Must be explicitly disabled in production
- **Mitigation**: `settings_prod.py` forces `DEBUG=False`
- **Refactor**: Default to False in non-desktop settings

### 14.3 CSRF Protection
- **Issue**: CSRF middleware is enabled; API uses Token auth
- **Impact**: Token-authenticated API requests bypass CSRF
- **Mitigation**: Token auth is stateless; CSRF only needed for session auth
- **Refactor**: Document API auth requirements

---

## 15. Logging

### 15.1 Log Rotation
- **Issue**: `RotatingFileHandler` with 2MB max, 5 backups
- **Impact**: Logs may be insufficient for debugging production issues
- **Mitigation**: Configurable via environment variables
- **Refactor**: Consider structured logging (JSON format)

### 15.2 Audit Log vs Application Log
- **Issue**: `AuditLog` (data changes) and `bgddr.log` (application) are separate
- **Impact**: Correlation between data changes and application errors requires manual work
- **Refactor**: Consider unified logging with request ID correlation

---

## Priority Refactoring Targets

| Priority | Area | Impact | Effort |
|---|---|---|---|
| **High** | Outcome engine modularization | Maintainability | Medium |
| **High** | Knowledge rule schema validation | Data integrity | Low |
| **High** | API documentation (OpenAPI) | Developer experience | Low |
| **Medium** | Prescription versioning audit trail | Compliance | Medium |
| **Medium** | Pathology review concordance caching | Performance | Low |
| **Medium** | Desktop build documentation | Deployment | Low |
| **Low** | Analytics edge case tests | Reliability | Medium |
| **Low** | Structured logging | Observability | Medium |
| **Low** | Biobank code cleanup | Code hygiene | Low |

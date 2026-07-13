# GDES_FINAL_ARCHITECTURE_AUDIT.md

**System:** GDES (Glomerular Disease Expert System)
**Reviewer:** Claude Code (independent)
**Date:** 2026-07-12
**Method:** Source inspection of ~1,200 Python modules across 26 Django apps + live DB.

---

## 1. Shape of the system

GDES is a single Django project (`bgddr/`) with **26 installed apps** and two
clearly distinct generations of code:

- **Generation 1 — Registry core** (`patients`, `encounters`, `baseline`,
  `labs`, `pathology`, `prescriptions`, `treatments`, `analytics`, `studies`,
  `safety`, `clinic` UI). Mature, schema-consistent, well-commented, and
  exercised by the HTML UI. This is the strongest part of the system.

- **Generation 2 — "AI / Clinical Intelligence" layer** (`knowledge` 9.9k LOC,
  `clinical_reasoning` 6.5k LOC, `decision`, `clinical`, `timeline`, `events`,
  `followup`, `fhir`). Ambitious and feature-rich, but **partially disconnected
  from the Generation-1 data model** (see A-2). It is largely reached through
  DRF API endpoints rather than the clinician UI.

Top modules by size: `knowledge` (9,861 LOC), `clinical_reasoning` (6,535),
`analytics` (2,869), `followup` (2,313), `clinic` (2,021).

---

## A-1 — Dead / deprecated code retained in the running system

| Item | Evidence | Impact |
|------|----------|--------|
| Legacy `decision` app (9-disease engine) | Still in `INSTALLED_APPS` (`settings.py`), but its URLs are commented out (`bgddr/urls.py:60`) and `decision/services.py:389` is a `DeprecationWarning` shim. | Ships migrations & admin for a superseded engine; invites accidental use. |
| `biobank` app | Commented out of `INSTALLED_APPS` with a note, but the directory, models, and migration remain. | Harmless but confusing. |
| Duplicate reasoning entry points | `decision.reason_about_patient` (deprecated) vs `clinical_reasoning.services.engine.reason_about_patient` (current). | Two code paths named identically. |

**Recommendation:** remove `decision` from `INSTALLED_APPS` (or delete the app)
before code freeze; it is explicitly deprecated and unused.

---

## A-2 — Schema drift between the CDS services and the real models (root cause)

The `clinical_reasoning/services/*` modules were written against a data model
that does not match the shipped one. This single mismatch is the root cause of
most Clinical Safety blockers (S-1…S-4):

| Service assumes | Reality | File |
|-----------------|---------|------|
| `LabResult.numeric_value` | field is `value_numeric` (`labs/models.py:131`) | `drug_toxicity.py:297`, `treatment_failure.py:357/379/403/428/431`, `disease_validation.py:252` |
| `Prescription.status in (active, ongoing)` + `Prescription.drug/dose/frequency` | statuses are `draft/final`; drug is on `PrescriptionItem` | `drug_toxicity.py:249-262` |
| `comorbidities` app, `allergies` app | neither exists | `drug_toxicity.py:321-339` |
| `disease_trajectory["disease_id"]` | trajectory dict never contains it (id is on `differential`) | `clinic/views.py:332` |

This is *hidden coupling*: the services depend on names that no test and no
runtime path validated, so the drift went unnoticed. The Generation-1 UI code
(`clinic/views.py:237-284`) uses the **correct** names, proving the model is
fine — only the newer service layer is out of sync.

**Recommendation:** introduce a single, tested accessor module (e.g.
`clinical_reasoning/services/patient_data.py`) that all services use to read
labs / meds / features, so the schema is referenced in exactly one place.

---

## A-3 — Fragile silent-failure pattern

Broad `except Exception: pass` / `= None` blocks appear throughout the CDS layer
(`drug_toxicity.py:264, 311-343`; `clinic/views.py:337-361`;
`knowledge/services.py:164, 195`). They convert programming errors (wrong field,
missing app) into silent no-ops, which is precisely why the safety defects
survived to a release candidate. For a clinical system, exceptions in the CDS
path should be logged and surfaced, not swallowed.

---

## A-4 — API surface vs. UI surface

`bgddr/urls.py` mounts many DRF routers (`clinical`, `knowledge`, `timeline`,
`clinical_reasoning`, `followup`, `treatments`, `fhir`). Several endpoints
(`drug_toxicity`, `treatment_failure`, `relapse_detection`,
`retrospective_validation`) are **API-only** — they are not called by any
template (verified by grep of `templates/` and `clinic/`). For a single-PC
pilot with no external API consumer, this is a large untested surface. Consider
either wiring them into the UI (after fixing them) or disabling their routes for
the pilot to reduce the attack/error surface.

---

## A-5 — Naming / organization observations (low)

- `knowledge` mixes rule storage, graph reasoning, evidence engine, authoring,
  versioning, and 4 different seed commands (`seed_knowledge_base`,
  `seed_v4_knowledge`, `seed_clinical_cases`, `load_test_knowledge`). It is not
  obvious which seed defines the *pilot* knowledge base. Document the canonical
  one.
- `evaluate_entry` sets `disease_name = entry.entry_id`
  (`knowledge/services.py:341`), so raw rule IDs (e.g. `KB-IGA-007`) can leak
  into a "disease name" field downstream. Cosmetic but user-visible.
- Test rules with `TEST-*` / `KB-*` entry IDs are mixed into the same ACTIVE set
  as production rules in the live DB (618 active). Separate test fixtures from
  the shipped knowledge base.

---

## A-6 — Deployment architecture (adequate for pilot)

- SQLite with a 30 s busy timeout, data under `BGDDR_DATA_DIR` (OneDrive-safe),
  PostgreSQL-ready settings. Reasonable for a single-PC single-user pilot.
- Auto-backup (`bgddr/backup.py`, 6 h interval, 60 snapshots) present.
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` read from env; prod settings enforce.
- **Risk:** OneDrive + SQLite concurrent access is fine for one user but will
  corrupt if two machines open the synced DB simultaneously. Document a hard
  "one machine at a time" rule for the pilot (see Pilot Readiness report).

---

## Architecture verdict

The **foundation is coherent and maintainable**; the problems are concentrated
in one generation of one layer and are wiring/schema issues, not design flaws.
No architectural redesign is warranted or recommended. The required work is:
remove dead code (A-1), centralize + fix the data-access drift (A-2), and stop
swallowing exceptions in the CDS path (A-3).

# GDES Version 6.5 RC1 — Independent Architecture & Clinical Review

**Reviewer role:** Independent software architect and clinical reviewer
**Review date:** 2026-07-11
**Subject:** Glomerular Disease Expert System (GDES), Version 6.5 Release Candidate 1
**Deployment target under review:** Single-site, single-PC Windows pilot on SQLite
**Review basis:** Direct inspection of source code and the live `db.sqlite3` database — **not** the self-produced `GDES_*` status documents

---

## 1. Executive Summary

GDES is a genuinely substantial platform: a coherent Django domain model, a knowledge-graph-driven reasoning engine, a large curated rule base (625 rules across 23 diseases), and a defensible single-PC deployment story. The engineering foundations are real.

However, the **flagship objective of this release — the transparent, auditable Clinical Governance Layer (Objective 1) — exists only as database schema. It is not populated and not wired into the recommendation pipeline.** The governance models are well-designed, but no code path writes to them, and the underlying knowledge-base governance fields are 0% populated.

**Verdict:** GDES is **not yet ready to be described as "clinically transparent and auditable,"** which is the release's own definition of success. It *may* be ready to pilot as a **registry + clinical decision-support tool** provided the governance/transparency guarantees are not advertised until the audit trail is actually wired in.

The corrective work is **integration and cleanup, not redesign**, and therefore fits within the stated development freeze.

### Severity summary

| Severity | Count | Theme |
|---|---|---|
| 🔴 Critical | 3 | Governance layer unwired; insecure launcher |
| 🟠 High | 4 | Insight duplication; duplicate live engine; doc/DB drift; evidence-grade inconsistency |
| 🟡 Medium | 3 | DB access at app init; wildcard ALLOWED_HOSTS (deferred path); unverified test pass |
| 🟢 Positive | 4 | No duplicate models; safe DRF defaults; clean engine decomposition; correct desktop hardening |

---

## 2. Methodology

Claims in the review package were treated as hypotheses and verified against ground truth:

- **Code:** static inspection and pattern search across the Python source tree (excluding `node_modules`).
- **Data:** direct SQL queries against the live `bgddr/db.sqlite3`.
- **Runtime:** the Django app was launched (`manage.py runserver`, port 8000) and confirmed to serve the dashboard (HTTP 200) with a 7/7 knowledge-platform bootstrap.
- **Tests:** the pytest suite was **collected** (180 tests) but **not executed** to completion; "all passing" is therefore unverified in this review.

Where a finding is backed by a live database count, that count is quoted.

---

## 3. Critical Findings

### 🔴 C-1 — `RecommendationAudit` is a phantom model; the audit trail is never written

**Objective violated:** Objective 1 ("Every AI-generated recommendation must become completely transparent and auditable"; "No recommendation should function as a black box").

**Evidence:**
- The only occurrence of `RecommendationAudit(` in the entire Python codebase is the class definition at `knowledge/models.py:759`. It is **never instantiated**.
- It is *read* (aggregated for the dashboard) at `knowledge/views.py:558`, but no service *creates* a record.
- No service under `clinical_reasoning/services/` (engine, management_plan, monitoring_plan, investigation_engine, drug_toxicity, treatment_failure, disease_validation) emits an audit record.
- **Live DB:** `knowledge_recommendationaudit` = **0 rows**.

**Impact:** The governance dashboard (`GET /api/v1/knowledge-base/governance_stats/`) will permanently report `total_recommendations: 0`, `avg_confidence_score: 0`, `override_rate_pct: 0`. The per-recommendation transparency table required by Objective 1 (guideline, version, section, evidence grade, confidence, reviewer, date validated, next review) cannot be produced for any real recommendation. The single most important feature of the release is a well-designed table that nothing fills.

**Recommendation:** Wire `RecommendationAudit` creation into each recommendation-producing service. Each service already carries most of the needed fields (guideline via the rule's `source`, `evidence_grade`, KB rule id, confidence, explanation); it needs to persist one audit row per recommendation issued. **This is the highest-value change in the release.**

---

### 🔴 C-2 — Knowledge-base governance fields are 0% populated

**Objective violated:** Objective 1 / Objective 2 (governance coverage metrics).

**Evidence (live DB, across 625 rules):**

| Governance field | Rules populated |
|---|---|
| `author` | **0 / 625** |
| `approved_by` | **0 / 625** |
| `confidence_score` (≠ 0) | **0 / 625** |
| `explanation` (non-empty) | **0 / 625** |
| `next_review_date` | **0 / 625** |
| `RuleReview` records | **0** |

Only `source` (guideline FK, 625/625) and `evidence_grade` are actually populated.

**Impact:** The governance-coverage panel and re-review alert logic in `knowledge/views.py` (`governance_stats`) will report 0% across author, approval, confidence, explanation, and next-review coverage. Even if C-1 is fixed, recommendations would inherit empty confidence/explanation/reviewer values from their source rules, so the transparency card would still render blank.

**Recommendation:** Backfill governance fields on the rule base — at minimum `author`, `confidence_score`, `explanation`, and `next_review_date` — before the pilot, or the governance dashboard is non-functional in practice.

---

### 🔴 C-3 — The simple launcher runs insecure development settings

**Objective affected:** Objective 5 (single-PC pilot: stability, reliability) and the Security review.

**Evidence:** There are two launch paths with divergent security posture:
- `desktop/launcher.py:47` sets `DJANGO_SETTINGS_MODULE=bgddr.settings_desktop` — hardened (DEBUG off, persistent SECRET_KEY, localhost-only). ✅
- `start_gdes.bat` runs `python manage.py runserver` with **no settings override**. `manage.py` defaults to `bgddr.settings`, which has `DEBUG = True` (`settings.py:19`) and the hardcoded `SECRET_KEY = "dev-only-insecure-change-me"` (`settings.py:18`).

`start_gdes.bat` is the newest launcher (dated 2026-07-11). Runtime logs confirmed the running server is on `bgddr.settings` (DEBUG on). Django's runserver with `DEBUG=True` renders full stack traces — including patient data in local variables — on any error.

**Impact:** If the pilot is started via `start_gdes.bat`, the clinic runs a debug server with a publicly known secret key over the session cookie.

**Recommendation:** Delete `start_gdes.bat`, or add `set DJANGO_SETTINGS_MODULE=bgddr.settings_desktop` to it. Standardize the pilot on `desktop/launcher.py` / `Start-BGDDR.bat` and document a single supported launch method in the pilot deployment guide.

---

## 4. High-Priority Findings

### 🟠 H-1 — `ClinicalInsight` accumulates duplicates on every reasoning run

**Evidence:** `_generate_insights()` (`clinical_reasoning/services/engine.py:290–313`) calls `ClinicalInsight.objects.create(...)` unconditionally, with no dedup, upsert, or "clear previous insights" step. `reason_about_patient` is `@transaction.atomic` and increments `profile.version`, so it is designed to be re-run — each run re-inserts the same insights.

**Live DB confirms it:** 46 `ClinicalInsight` rows but only **6 distinct titles** across **3 patients**; one patient has 22 near-duplicate insights.

**Impact:** Unbounded growth. In a live clinic the insight panel becomes unusable within weeks and repeated identical alerts erode clinician trust.

**Recommendation:** Before regenerating, delete/supersede the patient's prior engine-generated insights, or use `update_or_create` keyed on a stable (patient, category, title) signature.

---

### 🟠 H-2 — "One reasoning engine" is not met: the deprecated engine is still live

**Objective violated:** Objective 3 ("one reasoning engine").

**Evidence:** `decision.services.evaluate_case()` is documented as DEPRECATED and emits a `DeprecationWarning` (`decision/services.py:388–400`), but it remains the **active handler** for API endpoints at `decision/views.py:39` and `decision/views.py:62`. It uses a hardcoded 9-disease `DISEASE_PROFILES` set, parallel to (and capable of disagreeing with) the 625-rule KB engine.

**Impact:** Two diagnostic engines are reachable at runtime and may produce conflicting differentials. A `DeprecationWarning` is not deprecation while the URL route is live.

**Recommendation:** Either remove the `decision` route from URL configuration, or make `evaluate_case()` delegate to `clinical_reasoning.services.engine`. Objective 3 cannot be marked complete until one of these is done.

---

### 🟠 H-3 — Documentation numbers do not match the system

**Objective affected:** Objective 6 (documentation must accurately reflect the implemented system) and Objective 7 (Claude can review without clarification).

**Evidence:** The review package repeatedly states **"104 rules across 18 diseases"** (e.g. `GDES_CLAUDE_REVIEW_REQUEST.md`). The live DB has **625 rules across 23 diseases**. Similar drift appears across the `GDES_*` status documents, which describe an earlier, smaller system.

**Impact:** The documentation cannot be relied upon as a source of truth; ground truth had to be recovered from the database. This directly undercuts the "review without architectural clarification" success criterion.

**Recommendation:** Reconcile all counts and version statements in the documentation set against the live database and code. Treat the DB and code as authoritative and regenerate the numeric claims.

---

### 🟠 H-4 — Evidence grades use three incompatible schemes in one column

**Evidence (live DB, `evidence_grade` distribution):**
`1` (48), `1A` (10), `1B` (47), `1C` (16), `2` (294), `2B` (3), `2C` (35), `2D` (19), `A` (22), `B` (21), `C` (16), `NG` (40), `OP` (54).

This mixes a KDIGO 1/2 + letter scheme, a bare A/B/C scheme, and NG/OP tokens in a single field. `GDES_CLINICAL_GOVERNANCE.md` §5 claims a clean, uniform GRADE mapping.

**Impact:** The dashboard's "evidence grade distribution" produces fragmented, non-comparable buckets, and any recommendation card that surfaces the grade will show inconsistent notation to clinicians.

**Recommendation:** Normalize `evidence_grade` to a single documented scheme (e.g. KDIGO `1A`…`2D`, plus `NG`/`Not Graded`), with a data migration to remap the legacy `1`, `2`, `A`, `B`, `C`, `OP` values.

---

## 5. Medium-Priority Findings

### 🟡 M-1 — Database access during app initialization

pytest collection and server startup both emit `RuntimeWarning: Accessing the database during app initialization`. A `knowledge` app bootstrap (`knowledge.apps`, logs "Knowledge platform bootstrap: 7/7 checks passed") queries the DB in `AppConfig.ready()` or at import time. This is fragile: it can fail against a fresh or mid-migration database and slows every management command. **Recommendation:** make the bootstrap lazy (run on first request or via an explicit management command), not at app-ready.

### 🟡 M-2 — Wildcard `ALLOWED_HOSTS` in the deferred deploy settings

`bgddr/settings_deploy.py:33` sets `ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]`. The `"*"` defeats host-header validation. This is on the deferred (post-pilot) enterprise path, so it is not a pilot blocker, but it should be corrected before any networked deployment. **Recommendation:** remove `"*"` and drive `ALLOWED_HOSTS` from an explicit environment variable.

### 🟡 M-3 — Test pass rate unverified

The review package claims "180 pytest tests, all passing." This review confirmed **180 tests collect** cleanly but did **not** run them to completion. **Recommendation:** capture a full, green test run (with the exact command and environment) in `RELEASE_NOTES.md` so the claim is reproducible.

---

## 6. Positive Findings

- **🟢 No duplicate domain models.** `ClinicalProfile`, `ClinicalInsight`, `ClinicalEncounter`, `Prescription`, `FollowUpTask`, `ScheduledVisit`, and `LabResult` each have exactly one class definition. Objective 3's "no duplicated entities" holds at the model level.
- **🟢 Safe API defaults.** DRF is globally configured with `IsAuthenticated` + `DjangoModelPermissions` and Token/Session auth (`settings.py:99–110`); there are no open-by-default write endpoints.
- **🟢 Clean engine decomposition.** `clinical_reasoning/services/engine.py` is readable and well-separated (feature extraction → rule evaluation → graph augmentation → trajectory → care gaps → reasoning chain), and the knowledge-graph augmentation is a sound design.
- **🟢 Correct desktop hardening exists.** `settings_desktop.py` is a proper single-PC hardening profile (DEBUG off, persistent key, localhost-only) — the pilot simply needs to *use* it consistently (see C-3).

---

## 7. Recommended Path to a Defensible Release Candidate

The two critical governance findings (C-1, C-2) share one root cause: a designed-but-unwired governance layer. Closing it is integration work that fits the freeze.

**Priority order:**

1. **C-1 — Wire `RecommendationAudit` into the reasoning pipeline.** Highest-value change; makes Objective 1 real.
2. **C-2 — Backfill KB governance fields** (`author`, `confidence_score`, `explanation`, `next_review_date`) so audit records and dashboard coverage are non-empty.
3. **H-1 — Fix insight duplication** before any real patient data is entered.
4. **C-3 / H-2 — Retire the insecure launcher and the second live engine.**
5. **H-3 / H-4 — Reconcile documentation to the DB and normalize evidence grades.**
6. **M-1 — Make the knowledge bootstrap lazy.**

Until items 1–2 are complete, GDES should be piloted as a **registry + decision-support tool**, and the transparency/auditability guarantees in the governance documents should **not** be advertised, because the code cannot currently substantiate them.

---

## 8. Pilot Readiness Assessment

| Objective (from review brief) | Status | Note |
|---|---|---|
| 1 — Clinical Governance Layer | ❌ Not met | Schema present, unpopulated and unwired (C-1, C-2) |
| 2 — Knowledge Governance Dashboard | ⚠️ Partial | Endpoint exists but reports ~0% coverage against real data |
| 3 — System Consistency Audit | ⚠️ Partial | No duplicate models (good); two live engines remain (H-2) |
| 4 — Complete Patient Journey | ⚠️ Unverified | Engine runs end-to-end; not validated across all six named diseases in this review |
| 5 — Single-PC Pilot Optimization | ⚠️ Partial | Hardened profile exists but the simple launcher bypasses it (C-3) |
| 6 — Documentation Cleanup | ❌ Not met | Material numeric drift vs. the live system (H-3) |

**Overall:** The platform is pilot-capable as a registry/decision-support system after C-3 and H-1 are fixed. It is **not** ready to make the transparency/governance claims that define v6.5 success until C-1 and C-2 are closed.

---

## Appendix A — Evidence Index

| Finding | Primary evidence |
|---|---|
| C-1 | `knowledge/models.py:759` (only definition); `knowledge/views.py:558` (read-only); DB `knowledge_recommendationaudit` = 0 |
| C-2 | DB counts across 625 rules: author/approved_by/confidence/explanation/next_review = 0; `RuleReview` = 0 |
| C-3 | `start_gdes.bat`; `manage.py` default `bgddr.settings`; `settings.py:18–19`; runtime log confirms DEBUG on |
| H-1 | `clinical_reasoning/services/engine.py:290–313`; DB 46 insights / 6 distinct titles / 3 patients |
| H-2 | `decision/services.py:388–400`; `decision/views.py:39, 62` |
| H-3 | Docs "104 rules / 18 diseases" vs DB 625 rules / 23 diseases |
| H-4 | DB `evidence_grade` distribution (13 distinct tokens across 3 schemes) |
| M-1 | pytest/startup `RuntimeWarning`; `knowledge.apps` bootstrap log |
| M-2 | `settings_deploy.py:33` |
| M-3 | pytest `--collect-only` = 180 collected (not executed) |

## Appendix B — Scope and Limitations of This Review

- The full pytest suite was collected but not executed; correctness of the 180 tests is not asserted here.
- The complete 16-step patient journey was not run for each of the six suggested validation diseases; the engine was confirmed to run and the app to serve, but per-disease clinical accuracy of protocols was not independently re-derived.
- Clinical accuracy of individual treatment/monitoring protocols against KDIGO 2021/2025 was not line-by-line verified in this pass; it is recommended as a dedicated clinical-content review.
- Findings reflect the state of the code and `db.sqlite3` on 2026-07-11.

---

*Prepared as an independent review deliverable for GDES v6.5 RC1. Recommendations are scoped to stabilization and governance within the stated development freeze; no redesign is proposed.*

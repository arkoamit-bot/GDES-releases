# GDES Intelligence & Integration — Upgrade Work Plan

**Owner:** Maintainer (rebonto.haque)
**Prepared:** 2026-07-26
**App version at time of writing:** 7.3.10
**Status:** Draft plan — sequencing and clinical-content decisions pending

This plan closes the gaps identified while reviewing the Vera Health integration
and the clinical intelligence database. It is scoped to **stabilisation and
enrichment**, not new modules, in line with the pilot readiness goal.

---

## 1. Current state (verified 2026-07-26)

| Area | State | Note |
|---|---|---|
| KB entries | 209 active / 93 draft | 41 distinct `disease_id` values |
| KB governance fields | **Backfilled** ✅ | author/approved/confidence/explanation/next-review populated on active rules |
| Knowledge graph | **48 nodes / 88 edges** ✅ | Just built; previously 0. Disease (36) + Drug (12) only |
| Syndrome / Pathology / Lab / Monitoring / Complication | **Empty** ❌ | No nodes/edges of these types → graph is sparse |
| DrugIntelligence | 12 rows | Thin |
| RecommendationAudit | **0 rows** ❌ | Per-recommendation audit trail never written |
| RuleReview | 0 rows | Peer-review workflow unused |
| Vera integration | 2 paths | Manual copy-paste (works, no creds) + live API (`vera_client`, needs Vera auth) |
| CDS "Vera" buttons | Consolidated ✅ | Kept "Request Prescription from Vera"; removed "Copy Case Summary" |

### Already completed (this session)
- Consolidated the two CDS→Vera buttons to the richer one; removed dead JS.
- Added `knowledge/management/commands/build_knowledge_graph.py` and wired it into
  the launcher seed flow (`desktop/launcher.py`); ran it (graph now populated).
- **WS-1:** Wired `RecommendationAudit` into all 6 clinical reasoning services.
- **WS-5:** Fixed `build_exe.ps1` regex patterns for accurate release metrics; removed stray `_tmp_ms_test.py`.
- **WS-6:** Confirmed manual copy-paste as pilot Vera path; removed dead consultation page URL.

### 2026-07-28 — v7.3.12 packaging incident + fixes
The shipped 7.3.12 build **500'd on every request**: `bgddr/urls.py` does
`include("auth.urls")`, but the bare `auth` module was not in `LOCAL_APPS` in
`desktop/BGDDR.spec`, so PyInstaller omitted it and the URLconf failed to import
(`ModuleNotFoundError: No module named 'auth'`). Data was never at risk; the
update swap, 5 migrations and KB seeding all succeeded. Fixes:
- Added `auth` to `LOCAL_APPS` (the defect). `auth` is **not** in `INSTALLED_APPS`,
  so app-based checks could not catch it.
- **Build-time guard** in `BGDDR.spec`: parses `bgddr/urls.py` for every
  `include("<mod>.urls")` and fails the build if the module isn't bundled. It
  immediately caught a **second** omission, `decision`, now also added.
- **HTTP smoke test in `--check`**: the self-check now performs a real `GET /`
  and exits non-zero on 5xx. Binding the port alone could never detect a broken
  URLconf — which is exactly why this shipped.
- Build-script crash fix: `Get-Content -Raw` yields `$null` on an empty file and
  `[regex]::Matches` threw on it, aborting the build *after* a passing self-check.
  Guarded both occurrences; excluded `venv`/`site-packages` from the scan.
- **Release metrics now measured, not guessed** (closes the last WS-5 item): the
  self-check writes `selfcheck_stats.json` from its freshly-seeded DB via
  `kb_health_summary()`, and `build_exe.ps1` uses those counts. Previously
  regex-scraped source reported **43 diseases vs the real 22**. Also fixed
  `knowledge_version` (was the app version, now the real KB version) and
  relabelled "Test cases" → "Test functions in source" (1036 `def test_*`, which
  is not the 7 KB clinical cases). If the stats file is missing the counts stay
  **0 with a warning** rather than being guessed.
  Verified in the shipped artifacts: `version.json` / `RELEASE_REPORT.md` now read
  kb=7.3, **22 diseases**, 455/527 rules, 6 pathways, 7 cases, 13 guidelines —
  an exact match to the app's own startup health line.
- **Artifact encoding fix:** the three generated files were written with
  `Out-File -Encoding utf8`, which in PowerShell 5.1 emits a **BOM**; strict JSON
  parsers reject it (`json.load` → "Unexpected UTF-8 BOM"), a hazard for a
  machine-readable manifest. Now written via `File::WriteAllText` with
  `UTF8Encoding($false)` (BOM-free, verified: first bytes `7B 0D 0A`, strict
  `json.load` succeeds), and the report's em-dash replaced with ASCII to avoid
  mojibake. Lands on the next build.

---

## 2. Guiding constraints

1. **No fabricated clinical content.** Drug names, doses, monitoring intervals,
   evidence grades, and guideline citations must come from a cited source
   (KDIGO 2021/2024/2025, BIRDEM protocol, product labels). Anything unsourced is
   entered as **DRAFT** for clinician review, never ACTIVE.
2. **Back up before any DB mutation** — `python manage.py backup_db` (a snapshot
   is already automatic on launch).
3. **Idempotent seeds** — every loader uses `get_or_create`/`update_or_create`
   keyed on a stable natural key; re-running must not duplicate.
4. **Clinician sign-off** gates activation (`draft → active`) of any clinical rule.
5. Pilot stays on **SQLite / single PC**; no infra changes.

---

## 3. Workstreams

Each workstream lists: goal · tasks · files · acceptance criteria · verification ·
effort · whether it needs clinician-supplied content.

### WS-1 — Wire `RecommendationAudit` (governance closure) — **P0** ✅ DONE
*Needs clinical content: No. Highest value; pure integration.*

**Goal:** every AI recommendation writes a `RecommendationAudit` row so the
governance dashboard and per-recommendation transparency card become real.

**Tasks**
- [x] Added helper `create_audit_record(...)` + per-type wrappers in
      **`clinical_reasoning/services/audit.py`** (not `knowledge/audit.py`).
- [x] Called from all six services — `engine` (reasoning), `management_plan`,
      `monitoring_plan`, `investigation_engine`, `drug_toxicity`,
      `treatment_failure`/`audit_relapse` — and the DRF views in
      `clinical_reasoning/views.py`.
- [x] Guideline/evidence fields sourced from the plan/rule (evidence_grade, guideline).
- [~] Override flow: `override_allowed` set per alert severity; full
      `overridden` + `override_reason` capture still to wire when the UI override lands.

**Files:** `clinical_reasoning/services/audit.py` (new), the six
`clinical_reasoning/services/*.py`, `clinical_reasoning/views.py`.

**Acceptance criteria** — ✅ met
- Reasoning about a patient creates ≥1 `RecommendationAudit` row.
- `GET /api/v1/knowledge-base/governance_stats/` shows non-zero recommendation stats.

**Verification (2026-07-26):** `reason_about_patient(patient 1)` → RecommendationAudit
**0 → 3**; `tests/test_review_fixes.py` covers the audit helpers; **full suite 425 passed**.

**Fixed during review (2026-07-26):**
- `audit_clinical_reasoning` read `care_pathway_data["rule_results"]` (never set by
  the engine), giving those rows an empty `disease_id`; now falls back to
  `profile.differential[0]["disease_id"]`.
- Hardened `tests/test_review_fixes.py::TestRecommendationAuditWiring` — it asserted
  absolute `RecommendationAudit` counts that the patient-registration signal (now
  audited) polluted, so it passed in the full suite but failed in isolation; `setUp`
  now clears the table so per-test counts are order-independent.

---

### WS-2 — Enrich the knowledge graph (seed missing entity types) — **P1**
*Needs clinical content: Yes (syndromes, pathology, labs, monitoring, complications).*

**Goal:** move the graph from disease+drug only to a richly connected graph so
`augment_differential` / `enhance_treatment_plan` / graph reasoning add value.

**Tasks**
- [ ] Define the source tables (from KDIGO + BIRDEM GN protocol): Syndromes
      (nephrotic, nephritic, RPGN, …), key PathologyEntities, LabEntities
      (complement, ANCA, PLA2R, anti-GBM, …), MonitoringProtocols, Complications.
- [ ] Add/extend seed commands (`seed_v4_knowledge` or new `seed_entities`) to
      create these with `is_active=True` and the M2M links to diseases.
- [ ] Re-run `build_knowledge_graph`; confirm new node/edge types appear.

**Acceptance criteria**
- Graph contains syndrome/pathology/lab/monitoring/complication nodes and the
  corresponding edges (`diagnosed_by`, `found_in`, `monitored_by`, `complicated_by`).
- `build_graph_reasoning_steps(<disease>)` returns >1 step for major diseases.

**Verification:** `build_knowledge_graph` output shows the new node-type counts;
spot-check reasoning chain for IgAN, membranous, lupus, ANCA.

**Effort:** L (content-dependent). **Blocked on:** curated source content.

---

### WS-3 — Expand `DrugIntelligence` — **P1**
*Needs clinical content: Yes.*

**Goal:** cover the immunosuppression + supportive drug set used across the GN
protocols (steroids, MMF, CNI, cyclophosphamide, rituximab, RAASi, SGLT2i, …)
with mechanism, indications (M2M to diseases), renal dosing, and monitoring.

**Tasks**
- [ ] Extend `seed_drug_intelligence` from a cited source; link `indications`.
- [ ] Re-run `build_knowledge_graph` (drug↔disease edges refresh automatically).

**Acceptance criteria:** DrugIntelligence count reflects the protocol drug set;
each has ≥1 indication link. **Effort:** M. **Blocked on:** source content.

---

### WS-4 — Review & activate draft rules — **P2**
*Needs clinical content: clinician review only.*

**Goal:** resolve the 93 DRAFT entries (activate the sound ones, retire the rest)
so the rule base is intentional.

**Tasks**
- [ ] Generate a review list (`knowledge_dashboard` / `export_knowledge_base`).
- [ ] Clinician marks each `draft → active` (via `RuleReview`) or `retired`.
- [ ] Run `activate_entries` / lifecycle transitions accordingly.

**Acceptance criteria:** 0 stale drafts; every active rule has a `RuleReview`.
**Effort:** S–M (mostly clinician time).

---

### WS-5 — Build/release script polish — **P2** ✅
*Needs clinical content: No.*

**Goal:** make `desktop/build_exe.ps1` release artifacts truthful.

**Tasks**
- [x] Fixed the regex-scraped `version.json` / `RELEASE_REPORT.md` counts.
- [x] Removed the stray `_tmp_ms_test.py`.
- [x] **pip-install line fixed during review (2026-07-26)** — now
      `pip install -r requirements.txt pyinstaller` (requirements.txt includes
      `celery`), so a clean build machine can't silently produce a broken exe.
      *(This sub-item was still outstanding when WS-5 was first marked done.)*

**Acceptance criteria:** release report counts match `manage.py` reality; build
works on a machine with only Python + requirements. **Effort:** S.

---

### WS-6 — Vera integration verification — **P2** ✅
*Needs clinical content: No (needs Vera credentials/access).*

**Goal:** confirm which Vera path is actually used in the pilot and that it degrades safely.

**Tasks**
- [x] Decided: **manual copy-paste** is the pilot Vera path; consultation URL removed.
- [ ] If API is ever enabled: document `auth/vera_auth` setup + confirm
      `VeraClientError` surfaces a clear UI message.
- [x] **Dead-code cleanup done (2026-07-26):** removed the orphaned
      `vera_consultation` view + `templates/clinic/vera_consultation.html`, and the
      unused `case_summary` field + `_build_case_summary_text` from the
      `request-prescription` endpoint. `check` clean; **425 tests pass**.
- [x] **Orphaned service removed (2026-07-26):** deleted
      `clinical_reasoning/services/vera_consultation.py` (no callers, no tests).
      `check` clean; **425 tests pass**. Vera dead-code cleanup fully complete.

**Acceptance criteria:** the chosen path works end-to-end or fails gracefully with
a clear message. **Effort:** S–M.

---

## 4. Suggested sequencing

```
Milestone A (governance real):      WS-1  ──► RecommendationAudit populated
Milestone B (graph meaningful):     WS-2 + WS-3 (need clinical content) ──► rebuild graph
Milestone C (rule base clean):      WS-4
Milestone D (release trustworthy):  WS-5 + WS-6
```

- **WS-1 and WS-5 can start immediately** (no clinical content, no external deps).
- **WS-2 / WS-3** are the biggest lever but are **blocked on curated source content**
  (KDIGO tables / BIRDEM protocol) — supply the source and they become mechanical.
- Rebuild the knowledge graph (`python manage.py build_knowledge_graph`) after any
  WS-2/WS-3 content change; it is idempotent.

---

## 5. Definition of done

- [x] Reasoning produces `RecommendationAudit` rows (verified 0→3 on patient 1).
- [x] Governance dashboard shows non-zero recommendation stats (endpoint reads the rows).
- [ ] Knowledge graph includes all seven node types with sensible edges. *(graph built, but disease+drug only — WS-2 pending)*
- [ ] DrugIntelligence covers the protocol drug set with indication links. *(WS-3)*
- [ ] No stale DRAFT rules; each active rule peer-reviewed. *(WS-4; 93 drafts)*
- [x] `build_exe.ps1` release metrics accurate; clean-machine build robust (pip fix applied).
- [x] Vera path decided (manual copy-paste); orphaned consultation view still to remove.
- [x] Full `pytest` run green (**425 passed**); `manage.py check` clean. *(packaged `--check` exit 0 re-confirm on next build)*

---

## 6. Open decisions (need maintainer input)

1. **Clinical source** for WS-2/WS-3 — will you provide KDIGO/BIRDEM tables to load,
   or should these stay minimal for the pilot?
2. **Vera path** for the pilot — manual copy-paste only, or wire the live API?
3. **Priority order** — default is WS-1 → WS-5 first (no dependencies), then the
   content-dependent WS-2/WS-3. Adjust if the pilot needs the richer graph sooner.

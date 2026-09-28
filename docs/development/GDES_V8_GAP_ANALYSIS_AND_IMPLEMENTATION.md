# GDES V8 — Gap Analysis & Implementation (four roadmap docs)

**Date:** 2026-07-14 · **Reviewer:** Claude Code
**Scope:** the four attached documents — GitHub Error Reporting (GDES-OPS-012),
V8 AI Knowledge Engine Roadmap, V8.1 Disease Development Order, and Longitudinal
Clinical Data Model.

> **Headline:** these documents are **~80–95% already implemented** in the
> codebase. This pass filled the concrete, safe, in-scope gaps and scoped the
> rest (which need clinical authoring, credentials, or a scope decision).

---

## 1. Longitudinal Clinical Data Model ("Highest Priority") — ALREADY DONE

- Single source of truth: `patients.Patient` holds every persistent field
  (`primary_diagnosis`, `biopsy_diagnosis`, `oxford_mestc`, `isn_rps_class`,
  `ckd_etiology`, `diabetes_status`, `hypertension`, `smoking_status`,
  `hepatitis_status`, `hiv_status`, `transplant_status`).
- Baseline **promotes** these to the Patient (`baseline/models.py`).
- Follow-up **surfaces + syncs** them (`clinic/views.py:followup_create` →
  `_sync_level2_from_followup`), prescriptions **carry forward** comorbidities/
  investigations, and `patient_detail` displays them.
- Level 1 / 2 / 3 classification is real. **No action needed.**

## 2. GitHub Error Reporting (GDES-OPS-012) — ALREADY BUILT

- `feedback/` app (~3,000 LOC, 20 tests passing): models (ErrorLog,
  CrashReport, ClinicalConflict, KnowledgeConflict, AIFailureLog, RuleFailureLog,
  UserFeedback, WorkflowFeedback, PerformanceLog, KnowledgeImprovementSuggestion,
  TelemetrySettings, ErrorOccurrence, UploadBatch, FeedbackExport), a PHI
  **sanitizer**, **deduplicator**, GitHub **uploader**, **middleware**,
  **scheduler**, and dashboards.
- **To activate (no code needed):** Admin → *Telemetry settings* → set
  `github_repo` (`owner/repo`) and `github_token` (your PAT — you enter it; it is
  read from config, never hardcoded), and toggle `enabled`. The uploader then
  pushes **sanitized** reports; PHI never leaves the machine.
- Optional hardening (not done): encrypt `github_token` at rest (currently plain
  in the local SQLite — acceptable for single-user desktop).

## 3. V8 AI Knowledge Engine Roadmap — MOSTLY SCAFFOLDED

Implemented (in `clinical_reasoning/services/` + `knowledge/`):

| Layer | Where |
|---|---|
| L1 Clinical memory | `events/`, `ClinicalProfile` |
| L2 Expert learning (AI vs expert) | `retrospective_validation.py` |
| L3 Outcome learning | `analytics` outcomes, `disease_trajectory.py` |
| L4 Evidence validation | governance metadata, `disease_validation.py` |
| L8 Self-consistency | `clinical_checks.py` |
| L9 Knowledge-gap detection | `knowledge_quality.py`, engine info-gaps |
| L10 Feedback (Accept/Modify/Reject) | **added this pass** (below) |
| L12 Case-based reasoning | `ClinicalCase`, knowledge graph |
| L13 Research intelligence | `research_intelligence.py` |
| L14 Explainable AI | `explainability.py`, reasoning chain |
| L15 Performance dashboard | `operational_intelligence.py` (partial) |
| L16 Governance | RecommendationAudit, rule lifecycle, override |

**Not implemented — require internet + an LLM (out of the offline-pilot scope):**
- **L5 Online evidence retrieval** → *added this pass as a gated, no-LLM,
  approved-source-only lookup* (below).
- **L6 RAG**, **L7 Multi-agent LLM reasoning**, **L11 Guideline monitoring** →
  design only (see §6). These need an LLM API key, internet, and a governance
  decision; building them silently into an offline clinical desktop app would be
  inappropriate.

## 4. Disease Development Order — SCAFFOLDED to 36

Was 22/36. This pass added the 14 missing (IRGN, MGRS, Amyloidosis,
Immunotactoid, CFHR, Fabry, HBV-GN, HCV-GN, IgG4, Paraneoplastic, Sarcoidosis,
Recurrent IgA/FSGS/MN) as `Disease` records + **one DRAFT diagnostic rule each**.
The rules are **DRAFT only** — a nephrologist must author the criteria and
approve them before they can affect recommendations. **Active rule count is
unchanged (209).**

---

## 5. What I implemented this pass

1. **L10 nephrologist feedback loop.** Accept / Modify / Reject bar on the CDS
   recommendation in the patient page → writes `feedback.WorkflowFeedback`
   (`action`, `recommendation_ref`, rating, comment) as structured learning
   data. Never auto-applied to the knowledge base. `clinic/views.py`,
   `templates/clinic/patient_detail.html`, migration `feedback/0003`.
2. **14 missing diseases** as `Disease` + DRAFT rules:
   `python manage.py seed_missing_diseases` (idempotent).
3. **L5 gated evidence lookup** (`clinical_reasoning/services/evidence_retrieval.py`):
   OFF by default (`AI_ONLINE_EVIDENCE_ENABLED`, env `GDES_AI_ONLINE_EVIDENCE=1`),
   queries only PubMed (NCBI E-utilities), rejects identifier-like queries (PHI
   guard), no LLM, no recommendations generated. Tests included.

All changes ship with tests; the full suite stays green.

---

## 6. Remaining work (needs your decision / input)

| Item | Why it's not "just code" | To proceed |
|---|---|---|
| Author the 14 DRAFT diseases | Clinical content + patient safety | Nephrologist writes criteria; approve via the knowledge lifecycle |
| Activate GitHub upload | Needs your private repo + PAT | Enter them in Admin → Telemetry settings |
| L6 RAG / L7 multi-agent / L11 guideline monitoring | Need internet + an LLM API key; break offline-only scope; governance decision | Decide whether the pilot may call an LLM; then implement opt-in, prompted, with the same PHI guards as L5 |

**Recommendation:** keep the pilot offline (registry + rule-based CDS + the L5
PubMed lookup only). Defer the LLM layers (L6/7/11) until after the single-clinic
pilot, and only behind an explicit, audited, opt-in configuration.

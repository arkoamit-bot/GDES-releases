# GDES Version 6.5 Release Candidate Report

| Field  | Value                    |
|--------|--------------------------|
| Version | RC1                     |
| Date    | 2026-07-11              |
| Status  | Ready for Independent Review |

---

## 1. Release Summary

GDES (Glomerular Disease Expert System) Version 6.5 is a Release Candidate for clinical pilot deployment. This version adds clinical governance, knowledge governance, system consistency audit, and production readiness improvements to the existing clinical decision support system.

## 2. System Architecture

- **Pattern:** Clean Architecture + Domain-Driven Design
- **Framework:** Django ≥5.0, DRF ≥3.15
- **Database:** SQLite for pilot (NOT PostgreSQL)
- **Scale:** 30+ Django apps, 72 models
- **Tests:** 180 pytest tests (all passing)
- **RBAC:** 6 roles — `data_manager`, `statistician`, `readonly`, `coordinator`, `investigator`, `pathologist`

## 3. Clinical Capabilities

### 3.1 Disease Coverage (18 diseases)

**Core (9):** IgAN, MN, FSGS, MCD, LN, AAV, anti-GBM, infection-related GN, C3 glomerulopathy

**Additional (9):** Diabetic nephropathy, hypertensive nephrosclerosis, AIN, ATN, TMA, light chain cast nephropathy, fibrillary GN, amyloidosis, diabetic nephropathy with GN

### 3.2 Clinical Decision Support

| Capability | Detail |
|---|---|
| Differential diagnosis | 18 diseases, KnowledgeBase-driven |
| Management plans | Disease-specific treatment protocols |
| Monitoring plans | Structured intervals and alert thresholds |
| Follow-up scheduling | Disease-specific protocols with drug monitoring |
| Investigation recommendations | Disease-specific with priority and rationale |
| Drug toxicity detection | 7 drug classes |
| Treatment failure detection | Proteinuria non-response, eGFR decline, immunological non-response |
| Relapse detection | Disease-specific criteria |
| Disease validation | IgAN, MN, LN, AAV compliance scoring (0–100%) |
| Retrospective validation | AI vs clinician comparison with Cohen's kappa |
| Clinical calculators | eGFR, BSA, UPCR, renal dose, KDIGO heatmap |
| Explainability | Full reasoning chain, evidence quality, guideline support |

### 3.3 Knowledge Base

- 209 rules across 18 diseases
- Guideline-linked (KDIGO 2021, KDIGO 2024)
- Evidence-graded (Level 1 / Level 2 / Not Graded / Expert Opinion)
- 7-state lifecycle: Draft → Under Review → Approved → Active → Superseded / Retired / Archived
- Version control with diff and rollback
- Knowledge graph (nodes, edges, syndrome matching)
- Evidence engine (GRADE assessment, citation generation)

### 3.4 Clinical Governance (NEW in 6.5)

- **RecommendationAudit** model: full audit trail for every AI recommendation
- **Governance metadata** on KnowledgeBaseEntry: `author`, `approved_by`, `approved_at`, `next_review_date`, `confidence_score`, `explanation`, `override_allowed`
- **Override mechanism** with reason capture
- **Review workflow** (pending / approved / changes_requested / rejected)
- **Knowledge governance dashboard:** `GET /api/v1/knowledge-base/governance_stats/`

## 4. What's New in 6.5

| # | Feature |
|---|---------|
| 1 | **Clinical Governance Layer** — `RecommendationAudit` model, governance fields on KB entries |
| 2 | **Knowledge Governance Dashboard** — `/api/v1/knowledge-base/governance_stats/` |
| 3 | **System Consistency Audit** — deprecated legacy engine (`evaluate_case`), deprecated duplicate follow-up scheduler, identified monitoring data overlap |
| 4 | **RecommendationAuditAdmin** in Django admin with approve/reject/override actions |

## 5. Test Results

| Metric | Result |
|---|---|
| Total tests | 180 |
| Status | ALL PASSING |
| Regressions from 6.5 | 0 |
| Knowledge bootstrap | 7/7 checks passing |

## 6. Known Issues

| # | Issue | Severity |
|---|---|---|
| 1 | Legacy decision engine (`evaluate_case`) deprecated but retained for backward compatibility | Low |
| 2 | Duplicate follow-up scheduler (`followup_scheduler.py`) deprecated but retained | Low |
| 3 | Monitoring data in `management_plan.py` redundant with `monitoring_plan.py` | Medium |
| 4 | `care_pathway.py` naming confusion with `care_pathway_engine.py` | Low |
| 5 | No multi-user concurrent access (SQLite) | High (pilot OK) |
| 6 | No SMS notifications (Twilio deferred) | Medium |
| 7 | No FHIR interop | Medium |

## 7. Deployment

Single-PC pilot: SQLite, Django dev server, no external dependencies.

Refer to `GDES_PILOT_DEPLOYMENT_GUIDE.md` for installation steps.

## 8. Recommended Post-Pilot Actions

| Priority | Action |
|---|---|
| 1 | Remove `evaluate_case()`, `followup_scheduler.py`, `decision/explainability.py` |
| 2 | Rename `care_pathway.py` to `care_gap_detector.py` |
| 3 | Remove embedded monitoring from `management_plan.py` |
| 4 | Consolidate `DecisionResult` into `ClinicalProfile` |
| 5 | Add PostgreSQL support for multi-user |
| 6 | Add Celery + Redis for background tasks |
| 7 | Add FHIR R4 interop |
| 8 | Add Twilio SMS integration |

## 9. Approval

- [ ] Clinical review by independent clinician
- [ ] Architecture review by Claude Code
- [ ] Security review
- [ ] Pilot deployment approved

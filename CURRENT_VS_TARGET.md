# CURRENT_VS_TARGET.md — Gap Analysis

> **Project:** BGDDR → GDES Transformation
>
> **Date:** 2026-07-09
>
> **Purpose:** Compare current BGDDR implementation against the target Glomerular Disease Expert System (GDES) vision

---

## 1. Target Vision Summary

The GDES platform should become an **AI-native Glomerular Disease Expert System** capable of:

| # | Target Capability | Description |
|---|---|---|
| 1 | Clinical Registry | Multi-center patient registry with longitudinal follow-up |
| 2 | Clinical Decision Support | Diagnostic differential, urgency classification, next-step recommendations |
| 3 | Drug Recommendation | Intelligent drug selection based on patient profile, contraindications, guidelines |
| 4 | Automated Follow-up | Protocol-driven scheduling with intelligent reminders and monitoring |
| 5 | Knowledge Management | Scalable guideline platform with evidence grading and versioning |
| 6 | Research | Embedded RCTs, cohort analysis, survival analytics |
| 7 | National Multi-Center Registry | Federated data collection across multiple hospitals |
| 8 | Analytics | Advanced statistical methods, real-time dashboards |
| 9 | Explainable Clinical Intelligence | Every recommendation traceable to evidence and reasoning |

---

## 2. Capability Assessment Matrix

### Legend

| Status | Meaning |
|--------|---------|
| ✅ **Complete** | Fully implemented, tested, production-ready |
| 🟡 **Partial** | Core functionality exists but needs expansion or refinement |
| 🔴 **Missing** | Not implemented, requires new development |
| 🔧 **Needs Refactoring** | Exists but requires significant rework |
| ⚠️ **Deprecated** | Should be removed or replaced |

---

## 3. Detailed Gap Analysis

### 3.1 Clinical Registry

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Patient registration | ✅ Complete | Auto-generated BGD-NNNNN IDs, duplicate detection | Same + multi-center ID scheme | Low | Medium |
| Longitudinal follow-up | ✅ Complete | Encounters, phases, relapses | Same + automated follow-up triggers | Low | High |
| Disease phase tracking | ✅ Complete | State machine (ACTIVE→REMISSION→POST_REMISSION↔RELAPSE) | Same | — | — |
| Baseline assessment | ✅ Complete | 50+ field enrollment snapshot | Same | — | — |
| Lab management | ✅ Complete | Ordering, resulting, auto-eGFR (CKD-EPI 2021) | Same + trend alerts | Low | Medium |
| Pathology/biopsy | ✅ Complete | Oxford MEST-C, ISN/RPS, FSGS variant, membranous staging | Same | — | — |
| Treatment tracking | ✅ Complete | DrugMaster, TreatmentExposure, reconciliation | Same | — | — |
| Prescription engine | ✅ Complete | PDF, reconciliation, safety checks | Same | — | — |
| Adverse events | ✅ Complete | CTCAE grading, seriousness flags | Same | — | — |
| Consent management | ✅ Complete | Versioned, withdrawable, multi-type | Same | — | — |
| **Multi-center support** | 🔴 Missing | Single-site (BIRDEM) | Federated multi-hospital registry | **High** | **Critical** |
| **Patient demographics expansion** | 🔴 Missing | Basic (name, sex, DOB, phone) | Extended (occupation, education, insurance, ethnicity) | Medium | Medium |

**Registry Assessment: 85% Complete** — Core registry is production-ready. Multi-center is the critical gap.

---

### 3.2 Clinical Decision Support

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Disease profiling | ✅ Complete | 9 disease profiles with weighted rules | Same + expand to 20+ diseases | Medium | High |
| Diagnostic differential | ✅ Complete | Ranked list with confidence % | Same + explainability layer | Low | High |
| Urgency classification | ✅ Complete | 3-level (urgent/prompt/outpatient) | Same | — | — |
| Next-step recommendations | ✅ Complete | Tailored to differential | Same + guideline-linked | Low | Medium |
| Knowledge rule engine | 🟡 Partial | 87 rules, JSON-based, 9 diseases | 500+ rules, 20+ diseases, version-controlled | **High** | **Critical** |
| **Explainability** | 🔴 Missing | Score only | Full reasoning chain with evidence citations | **High** | **Critical** |
| **Confidence calibration** | 🔴 Missing | Raw scores | Calibrated probabilities with uncertainty | Medium | High |
| **Contradiction detection** | 🔴 Missing | None | Detect conflicting clinical findings | Medium | Medium |
| **Guideline linkage** | 🔴 Missing | Rules have source field | Every rule linked to specific guideline paragraph | Low | High |
| **Override tracking** | 🔴 Missing | None | Clinician can override with reason | Low | Medium |

**Decision Support Assessment: 40% Complete** — Core engine works. Explainability and scalability are critical gaps.

---

### 3.3 Drug Intelligence Engine

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Drug formulary | ✅ Complete | DrugMaster with classes, routes, strengths | Same + pharmacokinetics, interactions | Medium | High |
| Renal dose adjustment | 🟡 Partial | Binary flag + eGFR threshold | Full renal dosing table with multi-level adjustments | Medium | High |
| Drug interactions | 🔴 Missing | None | Drug-drug interaction checking | **High** | **Critical** |
| Drug-disease contraindications | 🔴 Missing | None | Contraindication checking per disease | **High** | **Critical** |
| **Drug recommendation engine** | 🔴 Missing | None | AI-assisted drug selection based on patient profile | **Very High** | **Critical** |
| Pregnancy safety | 🟡 Partial | Pregnancy category on DrugMaster | Full teratogenicity database | Medium | High |
| Drug monitoring | 🟡 Partial | Basic lab monitoring schedule | Intelligent monitoring with dose-dependent triggers | Medium | High |
| Prior intolerance checking | ✅ Complete | Checks TreatmentExposure.stop_reason | Same | — | — |
| Duplicate therapy detection | ✅ Complete | Same DrugClass check | Same + pharmacodynamic overlap | Low | Medium |
| **Pharmacogenomics** | 🔴 Missing | None | PGx-guided dosing (e.g., azathioprine TPMT) | Very High | Medium |

**Drug Intelligence Assessment: 20% Complete** — Basic formulary exists. Intelligent drug recommendation is entirely missing.

---

### 3.4 Follow-up & Monitoring Engine

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Visit scheduling | ✅ Complete | Protocol-driven, ±7-day windows, capacity | Same + intelligent rescheduling | Low | Medium |
| Due/overdue tracking | ✅ Complete | JSON endpoints for due/overdue | Same + push notifications | Low | High |
| Immunosuppression monitoring | 🟡 Partial | Basic lab schedule per drug class | Dose-aware, duration-aware monitoring | Medium | High |
| **Automated reminders** | 🔴 Missing | None | SMS/email/WhatsApp reminders for patients | **High** | **Critical** |
| **Smart scheduling** | 🔴 Missing | Fixed protocol | AI-adjusted based on disease activity | **High** | **High** |
| **Lab trend alerts** | 🔴 Missing | None | Auto-detect concerning lab trends | Medium | High |
| **Medication adherence tracking** | 🔴 Missing | None | Track fill rates, self-reported adherence | Medium | High |
| **Visit no-show prediction** | 🔴 Missing | None | ML model to predict no-shows | High | Medium |
| **Protocol compliance dashboard** | 🔴 Missing | None | Real-time protocol adherence metrics | Medium | High |

**Follow-up Assessment: 25% Complete** — Basic scheduling works. Intelligent/automated follow-up is missing.

---

### 3.5 Knowledge Management

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Guideline sources | ✅ Complete | GuidelineSource model (title, year, URL) | Same + full guideline text, paragraphs | Low | Medium |
| Rule storage | ✅ Complete | KnowledgeBaseEntry with JSON rule_data | Same + version control, A/B testing | Medium | High |
| Rule evaluation | ✅ Complete | Condition operators (eq, neq, gt, lt, contains, etc.) | Same + temporal conditions, composite rules | Medium | High |
| Rule seeding | ✅ Complete | Management command for 87 rules | Same + admin UI for rule management | Low | Medium |
| **Rule versioning** | 🔴 Missing | Single version per entry | Full version history with diff | Medium | High |
| **Rule authoring UI** | 🔴 Missing | Code-only | Visual rule builder for clinicians | Very High | High |
| **Evidence grading** | 🟡 Partial | Grade field (1/2/NG/OP) | Full GRADE evidence profile | Medium | High |
| **Guideline sync** | 🔴 Missing | Manual import | Auto-sync from guideline publishers | Very High | Medium |
| **Rule A/B testing** | 🔴 Missing | None | Compare rule performance across versions | High | Medium |
| **Rule performance metrics** | 🔴 Missing | None | Track rule accuracy, false positives/negatives | High | High |

**Knowledge Management Assessment: 35% Complete** — Basic rule engine works. Scalability and authoring are missing.

---

### 3.6 Research & Analytics

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| Outcome computation | ✅ Complete | PatientOutcome engine (eGFR slope, remission, composite) | Same | — | — |
| Kaplan-Meier survival | ✅ Complete | Pure-Python KM with log-rank test | Same + visualization dashboard | Low | Medium |
| Cox regression | ✅ Complete | Multivariable Cox (Newton-Raphson) | Same + time-varying covariates | Medium | High |
| Competing risks | ✅ Complete | Aalen-Johansen CIF | Same | — | — |
| Mixed models eGFR slope | ✅ Complete | Laird-Ware EM algorithm | Same | — | — |
| Multiple imputation | ✅ Complete | MICE with PMM + Rubin's rules | Same | — | — |
| Cohort analysis | ✅ Complete | Stratified by diagnosis, drug, study arm | Same + real-time dashboard | Low | Medium |
| Research export | ✅ Complete | CSV/XLSX/SPSS with data dictionary | Same + FHIR export | Medium | High |
| **Real-time dashboards** | 🔴 Missing | JSON endpoints only | Live dashboards with auto-refresh | **High** | **High** |
| **Predictive analytics** | 🔴 Missing | None | ML models for ESKD, relapse, treatment response | **Very High** | **Critical** |
| **Natural language reports** | 🔴 Missing | None | Auto-generated clinical summaries | High | Medium |
| **FHIR interoperability** | 🔴 Missing | None | FHIR R4 resource export/import | **High** | **High** |
| **Biomarker panels** | 🟡 Partial | PLA2R, dsDNA, C3/C4 | Full biomarker panel (IgA, complement, autoantibodies) | Medium | Medium |

**Research Assessment: 70% Complete** — Statistical engine is excellent. Predictive analytics and real-time dashboards are missing.

---

### 3.7 Multi-Center Registry

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| **Hospital/site management** | 🔴 Missing | Single-site | Multi-site with site-specific config | **High** | **Critical** |
| **Federated data collection** | 🔴 Missing | None | Data entry at each site, centralized analytics | **Very High** | **Critical** |
| **Site-level RBAC** | 🔴 Missing | Global roles | Site-scoped roles (coordinator at Site A sees only Site A) | **High** | **Critical** |
| **Data quality metrics** | 🔴 Missing | None | Per-site completeness, timeliness, accuracy | Medium | High |
| **Site comparison** | 🔴 Missing | None | Benchmark sites against each other | Medium | High |
| **Consent federation** | 🔴 Missing | Local consent | Cross-site consent management | High | High |
| **Data use agreements** | 🔴 Missing | None | Track DUA per site per study | Medium | Medium |
| **Central coordination** | 🔴 Missing | None | Central admin can monitor all sites | Medium | High |

**Multi-Center Assessment: 0% Complete** — Entirely single-site. This is the largest gap.

---

### 3.8 Event-Driven Architecture

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| **Event bus** | 🔴 Missing | Synchronous Django signals only | Async event bus (Redis/RabbitMQ) | **High** | **High** |
| **Event sourcing** | 🔴 Missing | AuditLog (imperative) | Event-sourced state changes | Very High | Medium |
| **Webhook notifications** | 🔴 Missing | None | Outbound webhooks for integrations | Medium | High |
| **Background tasks** | 🔴 Missing | None (synchronous) | Celery/django-rq for async jobs | **High** | **Critical** |
| **Real-time updates** | 🔴 Missing | None | WebSocket/SSE for live dashboards | High | High |
| **Event log** | 🟡 Partial | AuditLog tracks field changes | Full event stream with replay | High | Medium |

**Event-Driven Assessment: 5% Complete** — Only basic AuditLog. Entirely missing async/event-driven infrastructure.

---

### 3.9 AI Assistant Layer

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| **Clinical note generation** | 🔴 Missing | None | LLM-assisted note writing | Very High | High |
| **Diagnostic suggestions** | 🔴 Missing | Rule-based only | ML-enhanced diagnostic suggestions | Very High | Critical |
| **Treatment optimization** | 🔴 Missing | None | AI-optimized treatment plans | Very High | Critical |
| **Risk prediction** | 🔴 Missing | None | 5-year ESKD, relapse, AE risk | Very High | Critical |
| **Image analysis** | 🔴 Missing | None | Pathology slide AI analysis | Very High | Medium |
| **Chat interface** | 🔴 Missing | None | Natural language clinical queries | Very High | Medium |
| **Federated learning** | 🔴 Missing | None | Multi-center model training without data sharing | Very High | High |

**AI Assistant Assessment: 0% Complete** — Entirely missing. This is the long-term vision.

---

### 3.10 Clinical Calculators

| Sub-Capability | Status | Current State | Target State | Effort | Impact |
|---|---|---|---|---|---|
| eGFR calculator | ✅ Complete | CKD-EPI 2021 | Same + historical formulas | Low | Low |
| **KDIGO heat map** | 🔴 Missing | None | Visual eGFR/proteinuria progression | Medium | High |
| **MEST-C score calculator** | 🟡 Partial | Fields on IgANScore | Interactive calculator with risk stratification | Low | Medium |
| **ISN/RPS classifier** | 🟡 Partial | Fields on LupusPathology | Interactive classifier with activity/chronicity | Low | Medium |
| **CVD risk calculator** | 🔴 Missing | None | Framingham/QRISK for GN patients | Medium | Medium |
| **Pregnancy risk calculator** | 🔴 Missing | None | GN-specific pregnancy risk assessment | Medium | Medium |
| **Drug dose adjuster** | 🔴 Missing | Binary flag | Multi-level renal/hepatic dose adjustment | Medium | High |
| **Proteinuria converter** | 🔴 Missing | Manual | UPCR ↔ 24h UTP ↔ eGFR-adjusted | Low | Medium |
| **BSA calculator** | 🔴 Missing | None | Body surface area for dosing | Low | Low |

**Clinical Calculators Assessment: 15% Complete** — Basic eGFR exists. Interactive calculators are missing.

---

## 4. Summary Dashboard

| Capability | Status | Completeness | Priority | Effort |
|---|---|---|---|---|
| Clinical Registry | 🟡 Partial | 85% | High | Low |
| Clinical Decision Support | 🟡 Partial | 40% | **Critical** | High |
| Drug Intelligence | 🔴 Missing | 20% | **Critical** | Very High |
| Follow-up & Monitoring | 🔴 Missing | 25% | **Critical** | High |
| Knowledge Management | 🟡 Partial | 35% | **Critical** | High |
| Research & Analytics | 🟡 Partial | 70% | High | Medium |
| Multi-Center Registry | 🔴 Missing | 0% | **Critical** | Very High |
| Event-Driven Architecture | 🔴 Missing | 5% | High | High |
| AI Assistant Layer | 🔴 Missing | 0% | Low (long-term) | Very High |
| Clinical Calculators | 🔴 Missing | 15% | Medium | Low |

---

## 5. Implementation Priority Matrix

### Phase 3.1 — Quick Wins (1-2 weeks each)

| # | Task | Impact | Effort |
|---|---|---|---|
| 1 | Clinical calculators (KDIGO heat map, proteinuria converter, BSA) | High | Low |
| 2 | Guideline linkage (link rules to specific guideline paragraphs) | High | Low |
| 3 | Override tracking (clinician override with reason) | Medium | Low |
| 4 | Rule versioning (version history with diff) | High | Medium |
| 5 | Lab trend alerts (auto-detect concerning trends) | High | Medium |

### Phase 3.2 — Core Engines (1-2 months each)

| # | Task | Impact | Effort |
|---|---|---|---|
| 6 | Drug interaction engine | Critical | High |
| 7 | Drug-disease contraindication engine | Critical | High |
| 8 | Automated reminders (SMS/email) | Critical | High |
| 9 | Background task infrastructure (Celery) | Critical | High |
| 10 | Explainability layer for decisions | Critical | High |

### Phase 3.3 — Scale (2-4 months each)

| # | Task | Impact | Effort |
|---|---|---|---|
| 11 | Multi-center registry architecture | Critical | Very High |
| 12 | Site-scoped RBAC | Critical | High |
| 13 | Real-time dashboards | High | High |
| 14 | FHIR interoperability | High | High |
| 15 | Knowledge base expansion (87→500+ rules) | High | High |

### Phase 3.4 — Intelligence (3-6 months each)

| # | Task | Impact | Effort |
|---|---|---|---|
| 16 | Predictive analytics (ESKD, relapse risk) | Critical | Very High |
| 17 | Drug recommendation engine | Critical | Very High |
| 18 | Smart scheduling (AI-adjusted) | High | Very High |
| 19 | Natural language reports | Medium | Very High |
| 20 | Clinical note generation | Medium | Very High |

---

## 6. Architectural Impact Assessment

### Current Architecture Strengths
- ✅ Clean service layer with pure functions
- ✅ Pure-Python analytics (no R/scipy dependency)
- ✅ Outcome engine is computed, not entered
- ✅ Medication reconciliation is research-grade
- ✅ Desktop deployment is solid
- ✅ Audit trail is comprehensive

### Architectural Gaps
- 🔴 No event bus / async task infrastructure
- 🔴 No background job processing
- 🔴 No WebSocket/real-time capability
- 🔴 No multi-tenancy / site-scoping
- 🔴 No API versioning strategy
- 🔴 No OpenAPI/Swagger documentation
- 🔴 No feature flags for A/B testing
- 🔴 No metrics/observability stack

### Recommended Architectural Changes

```
Current:                    Target:
┌──────────────┐           ┌──────────────────────────────┐
│  Django ORM  │           │  Event Bus (Redis/RabbitMQ)   │
│  (sync)      │           │         │                     │
│              │           │         ▼                     │
│  Services    │           │  ┌─────────────┐             │
│  (sync)      │    →      │  │ Celery/     │             │
│              │           │  │ django-rq   │             │
│  Views       │           │  └──────┬──────┘             │
│  (sync)      │           │         │                     │
└──────────────┘           │         ▼                     │
                           │  Services (sync + async)      │
                           │         │                     │
                           │         ▼                     │
                           │  WebSocket (channels)         │
                           └──────────────────────────────┘
```

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Multi-center complexity overwhelms team | High | Critical | Phase rollout; start with 2-3 sites |
| AI/ML models not clinically validated | High | High | Require clinical validation before deployment |
| Drug interaction database incomplete | Medium | High | Start with nephrology-specific interactions |
| Event-driven migration breaks existing code | Medium | High | Strangler fig pattern; migrate incrementally |
| Desktop deployment incompatible with new features | Low | Medium | Maintain dual deployment; test both |
| Clinical users reject AI recommendations | Medium | High | Make AI optional; emphasize explainability |

---

## 8. Recommendation

### Do Not Rebuild

The existing BGDDR system is **production-quality** with excellent clinical workflow, research analytics, and decision support. The recommendation is to **extend, not replace**.

### Build in This Order

1. **Quick wins first** (Phase 3.1) — calculators, explainability, overrides
2. **Core engines** (Phase 3.2) — drug intelligence, reminders, background tasks
3. **Scale** (Phase 3.3) — multi-center, dashboards, FHIR
4. **Intelligence** (Phase 3.4) — AI/ML last, after infrastructure is solid

### Estimated Total Effort

| Phase | Duration | Dependencies |
|---|---|---|
| Phase 3.1 (Quick Wins) | 4-6 weeks | None |
| Phase 3.2 (Core Engines) | 3-4 months | Phase 3.1 |
| Phase 3.3 (Scale) | 4-6 months | Phase 3.2 |
| Phase 3.4 (Intelligence) | 6-12 months | Phase 3.3 |

**Total estimated: 14-24 months** for full GDES transformation.

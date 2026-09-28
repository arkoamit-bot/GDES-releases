# BK Virus Nephropathy — Clinical Pathway Specification
**Document ID:** BKV-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways
---
## 1. Document Purpose
6-stage clinical pathway for BKVN management.
---
## 2. Pathway Overview
```
STAGE 1: Screening and Early Detection (30d) -> STAGE 2: BK Viraemia Management — IS Reduction (56d) -> STAGE 3: BKVN Biopsy and Staging (14d) -> STAGE 4: Persistent BKVN — Second-Line Therapy (180d) -> STAGE 5: Stage C and Graft Failure Preparation (365d) -> STAGE 6: Long-Term Surveillance Post-BKVN (730d)
```

## 01. Screening and Early Detection
**Duration:** 30 days
**Goal:** Monthly plasma BKV PCR screening. Detect viraemia early before BKVN develops.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Monthly plasma BKV PCR for first 6 months post-transplant | KDIGO 2021 | BKV-MON-01 |
| D2 | Q3 months PCR months 6-24, then annually | KDIGO 2021 | BKV-MON-01 |
| D3 | If viraemia detected (any level): repeat in 1-2 weeks to confirm trend | KDIGO 2021 | BKV-DX-01 |
| D4 | Assess risk factors: tac/MMF intensity, ATG, rejection history | AST 2023 | BKV-PR-03 |
| D5 | Check tacrolimus trough, DSA, CMV/EBV PCR | KDIGO 2021 | BKV-MON-03 |
**Next stages:** BKV-PATH-02, BKV-PATH-03, BKV-PATH-06
**Criteria to proceed:** Screening initiated; viraemia detected or ruled out

## 02. BK Viraemia Management — IS Reduction
**Duration:** 56 days
**Goal:** Reduce immunosuppression for significant viraemia. Cornerstone of BKVN management.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Reduce tacrolimus target: 4-6 ng/mL (from 6-10) | AST 2023 | BKV-TX-01 |
| T2 | Reduce MMF: 1 g/day or discontinue. OR switch to mTOR inhibitor (sirolimus/everolimus) | AST 2023 | BKV-TX-01 |
| T3 | Maintain prednisone 5-10 mg/day | KDIGO 2021 | BKV-TX-01 |
| T4 | Weekly plasma BKV PCR — target <1000 copies/mL in 4-8 weeks | KDIGO 2021 | BKV-MON-02 |
| T5 | Biopsy if: BKV >10K, Cr rising, or viraemia >4 weeks despite IS reduction | KDIGO 2021 | BKV-TX-02 |
**Next stages:** BKV-PATH-03, BKV-PATH-04, BKV-PATH-05, BKV-PATH-06
**Criteria to proceed:** IS reduction initiated; monitor viral clearance

## 03. BKVN Biopsy and Staging
**Duration:** 14 days
**Goal:** Biopsy to confirm BKVN, stage, exclude concurrent rejection.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| B1 | Graft biopsy: H&E — viral cytopathic changes. SV40 IHC — confirm | AST 2023 | BKV-DX-02 |
| B2 | Staging: A (<25%, minimal IFTA), B (25-50%, IFTA 25-50%), C (>50%, IFTA >50%) | AST 2023 | BKV-DX-03 |
| B3 | C4d stain and DSA: exclude concurrent ABMR | KDIGO 2021 | BKV-EX-02 |
| B4 | Exclude TCMR: tubulitis pattern without SV40 = TCMR | KDIGO 2021 | BKV-EX-01 |
| B5 | Assess IFTA% — prognostic factor | KDIGO 2021 | BKV-PR-04 |
**Next stages:** BKV-PATH-02, BKV-PATH-04, BKV-PATH-05, BKV-PATH-06
**Criteria to proceed:** BKVN diagnosed and staged

## 04. Persistent BKVN — Second-Line Therapy
**Duration:** 180 days
**Goal:** Adjunctive therapy for BKVN persistent despite IS reduction for >4-8 weeks.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| A1 | Confirm persistent viraemia (>1000) despite >4-8 weeks of IS reduction | AST 2023 | BKV-PR-02 |
| A2 | Leflunomide: 100 mg load x3 days, then 20-40 mg daily. Target level 50-100 | AST 2023 | BKV-TX-03 |
| A3 | Monitor LFTs, Hb weekly x4 weeks for leflunomide toxicity | AST 2023 | BKV-TX-03 |
| A4 | Cidofovir 0.25-1 mg/kg IV q2-4 weeks if leflunomide fails | AST 2023 | BKV-TX-04 |
| A5 | Re-biopsy if persistent viraemia >12 weeks despite therapy | KDIGO 2021 | BKV-MON-02 |
| A6 | Monitor DSA at 3 and 6 months — IS reduction can trigger de novo DSA | KDIGO 2021 | BKV-MON-03 |
**Next stages:** BKV-PATH-05, BKV-PATH-06
**Criteria to proceed:** Second-line therapy initiated or planned

## 05. Stage C and Graft Failure Preparation
**Duration:** 365 days
**Goal:** Stage C BKVN: extensive IFTA, limited recovery potential. Prepare for graft failure.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | Stage C: IS reduction unlikely to improve — avoid over-immunosuppression | KDIGO 2021 | BKV-TX-01 |
| E2 | Manage as CKD: BP, anaemia, MBD as eGFR declines | KDIGO 2021 | BKV-PR-01 |
| E3 | RRT planning: eGFR <20 — prepare for dialysis | KDIGO 2021 | BKV-REF-01 |
| E4 | Re-transplant evaluation: safe after BKVN — ensure BKV PCR negative | AST 2023 | BKV-REF-01 |
| E5 | Avoid nephrotoxic agents (cidofovir) if eGFR <30 | AST 2023 | BKV-TX-04 |
**Next stages:** BKV-PATH-06
**Criteria to proceed:** ESKD management or re-transplant plan

## 06. Long-Term Surveillance Post-BKVN
**Duration:** 730 days
**Goal:** Monitor for BKV recurrence, de novo DSA, and graft function after BKVN clearance.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | If BKV cleared: monthly PCR x3, then quarterly x1 | KDIGO 2021 | BKV-MON-02 |
| L2 | Maintain lower IS targets: tac 4-6, MMF 1 g/day or alternative | AST 2023 | BKV-TX-01 |
| L3 | DSA at 6 and 12 months — monitor for de novo DSA from IS reduction | KDIGO 2021 | BKV-MON-03 |
| L4 | For-cause biopsy: Cr rise or new DSA or rising BKV | KDIGO 2021 | BKV-TX-02 |
| L5 | Cardiovascular risk management | KDIGO 2021 | BKV-TX-01 |
**Next stages:** N/A (final stage)
**Criteria to proceed:** N/A (final stage)

---

# Antibody-Mediated Rejection — Clinical Pathway Specification

**Document ID:** AMR-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways

---

## 1. Document Purpose

6-stage clinical pathway for ABMR management.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis and Classification (7d) -> STAGE 2: Acute ABMR — Active Treatment (30d) -> STAGE 3: Response Assessment (90d) -> STAGE 4: Chronic ABMR — Stabilisation (365d) -> STAGE 5: Graft Failure Preparation and Re-Transplant (365d) -> STAGE 6: Long-Term Surveillance (730d)
```

## 01. Diagnosis and Classification

**Duration:** 7 days
**Goal:** Confirm ABMR by Banff 2019 criteria: biopsy + DSA + C4d. Classify as acute, chronic, or mixed.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Graft biopsy: assess g, ptc, v, C4d, cg scores by Banff criteria — determine ABMR class | KDIGO 2021 | AMR-DX-01 |
| D2 | DSA testing: single-antigen bead assay, MFI, C1q binding, class I/II | KDIGO 2021 | AMR-DX-02 |
| D3 | Exclude BKVN: BK PCR plasma, SV40 stain on biopsy | AST 2023 | AMR-EX-01 |
| D4 | Exclude CNI toxicity: tacrolimus level, biopsy (arteriolar hyalinosis) | AST 2023 | AMR-EX-02 |
| D5 | Assess severity: creatinine trend, DSA MFI, Banff lesion scores (g+ptc), IFTA% | KDIGO 2021 | AMR-PR-04 |
| D6 | Exclude TCMR: assess tubulitis (t), interstitial infiltrate (i) — mixed rejection possible | KDIGO 2021 | AMR-DX-06 |
| D7 | Non-adherence assessment: tac variability >30%, MEMS caps, self-report | ERA/EDTA 2022 | AMR-TX-06 |

**Next stages:** AMR-PATH-02, AMR-PATH-04, AMR-PATH-06
**Criteria to proceed:** Diagnosis confirmed; classify ABMR type


## 02. Acute ABMR — Active Treatment

**Duration:** 30 days
**Goal:** Treat acute/active ABMR with PLEX + IVIG + steroids. Add Rituximab if severe/refractory.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Methylprednisolone 500 mg IV daily x3 | KDIGO 2021 | AMR-TX-01 |
| T2 | IVIG 2 g/kg divided over 2-5 days | KDIGO 2021 | AMR-TX-01 |
| T3 | PLEX 3-5 sessions (every other day) — 1.5 plasma volume exchange with albumin | KDIGO 2021 | AMR-TX-01 |
| T4 | Optimise tacrolimus target 5-8 ng/mL, MMF 2 g/day | KDIGO 2021 | AMR-TX-01 |
| T5 | Severe: add Rituximab 375 mg/m2 x1 (creatinine >2x, g+ptc >3, high MFI DSA) | AST 2023 | AMR-TX-02 |
| T6 | Refractory: Bortezomib 1.3 mg/m2 x4 doses (Days 1, 4, 8, 11) | AST 2023 | AMR-TX-03 |

**Next stages:** AMR-PATH-03, AMR-PATH-04, AMR-PATH-06
**Criteria to proceed:** Acute ABMR treatment initiated; monitor response


## 03. Response Assessment

**Duration:** 90 days
**Goal:** Assess response by creatinine, DSA MFI, and repeat biopsy at 3 months.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| R1 | Weekly creatinine x1 month, monthly DSA x3 months | KDIGO 2021 | AMR-MON-03 |
| R2 | Repeat biopsy at 3 months: assess histologic response (g+ptc, C4d) | KDIGO 2021 | AMR-MON-03 |
| R3 | If DSA persists despite therapy: consider Bortezomib or intensified therapy | AST 2023 | AMR-TX-03 |
| R4 | Address adherence: MEMS caps, social work referral, simplify regimen | ERA/EDTA 2022 | AMR-REF-01 |
| R5 | Assess for: CMV, BK, EBV — intensified immunosuppression increases infection risk | AST 2023 | AMR-MON-04 |

**Next stages:** AMR-PATH-04, AMR-PATH-05, AMR-PATH-06
**Criteria to proceed:** Response assessed; ongoing management


## 04. Chronic ABMR — Stabilisation

**Duration:** 365 days
**Goal:** Chronic ABMR: no proven reversal therapy. Optimise immunosuppression, slow progression.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Optimise tacrolimus 5-8 ng/mL, MMF 2 g/day — avoid under-immunosuppression | KDIGO 2021 | AMR-TX-04 |
| C2 | IVIG 2 g/kg monthly x3-6 months — may stabilise chronic ABMR | AST 2023 | AMR-TX-04 |
| C3 | RAASi for proteinuria: ACEi/ARB if UPCR >0.5 | KDIGO 2021 | AMR-TX-05 |
| C4 | BP target <130/80 — add CCB/thiazide if needed | KDIGO 2021 | AMR-TX-05 |
| C5 | DSA monitoring Q3 months — track MFI trend, C1q binding | KDIGO 2021 | AMR-MON-01 |
| C6 | CKD management: anaemia, MBD, nutrition as eGFR declines | KDIGO 2021 | AMR-TX-05 |

**Next stages:** AMR-PATH-05, AMR-PATH-06
**Criteria to proceed:** Chronic ABMR management established


## 05. Graft Failure Preparation and Re-Transplant

**Duration:** 365 days
**Goal:** Plan for graft failure. Re-transplantation evaluation with desensitisation if DSA persists.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RRT planning: eGFR <20 — prepare for dialysis | KDIGO 2021 | AMR-REF-02 |
| E2 | Re-transplant evaluation: DSA assessment, desensitisation if needed | AST 2023 | AMR-REF-02 |
| E3 | Desensitisation: PLEX/IVIG/Rituximab if DSA present pre-transplant | KDIGO 2021 | AMR-REF-02 |
| E4 | Counsel: 20-30% risk of recurrent ABMR in re-transplant | AST 2023 | AMR-REF-02 |

**Next stages:** AMR-PATH-06
**Criteria to proceed:** ESKD management or re-transplant


## 06. Long-Term Surveillance

**Duration:** 730 days
**Goal:** Lifelong DSA and graft function monitoring. Prevent ABMR recurrence.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Annual DSA, eGFR, UPCR, tacrolimus level — if stable | KDIGO 2021 | AMR-MON-01 |
| L2 | For-cause biopsy: new DSA, Cr rise, proteinuria — do not wait | KDIGO 2021 | AMR-MON-02 |
| L3 | Protocol biopsy at 12 months in high-risk patients | ERA/EDTA 2022 | AMR-MON-04 |
| L4 | Maintain tacrolimus target 4-8 ng/mL lifelong — do not reduce below 4 | KDIGO 2021 | AMR-TX-04 |
| L5 | Cardiovascular risk management — leading cause of death with functioning graft | KDIGO 2021 | AMR-TX-05 |

**Next stages:** N/A (final stage)
**Criteria to proceed:** N/A (final stage)


---

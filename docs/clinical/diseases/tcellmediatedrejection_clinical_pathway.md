# T-Cell Mediated Rejection — Clinical Pathway Specification
**Document ID:** TCMR-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways
---
## 1. Document Purpose
6-stage clinical pathway for TCMR management.
---
## 2. Pathway Overview
```
STAGE 1: Diagnosis and Classification (7d) -> STAGE 2: Type I TCMR — Steroid Therapy (14d) -> STAGE 3: Type II/III or Steroid-Resistant TCMR — ATG Therapy (21d) -> STAGE 4: Response Assessment (90d) -> STAGE 5: Late TCMR and Non-Adherence Management (365d) -> STAGE 6: Long-Term Surveillance (730d)
```

## 01. Diagnosis and Classification
**Duration:** 7 days
**Goal:** Confirm TCMR by biopsy: Banff i, t, v scores. Exclude ABMR and BKVN. Classify as Type I, II, or III.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Graft biopsy: assess i, t, v scores by Banff criteria — determine TCMR type | KDIGO 2021 | TCMR-DX-01 |
| D2 | C4d stain: must be negative for pure TCMR. If positive => check DSA for ABMR | KDIGO 2021 | TCMR-DX-05 |
| D3 | SV40 stain and BK PCR: exclude BK virus nephropathy (histologic mimic) | AST 2023 | TCMR-EX-01 |
| D4 | DSA testing: exclude mixed ABMR/TCMR | KDIGO 2021 | TCMR-EX-02 |
| D5 | Assess severity: Cr rise %, Banff scores, presence of arteritis | KDIGO 2021 | TCMR-PR-01 |
| D6 | Review tacrolimus trough levels and adherence history | AST 2023 | TCMR-TX-05 |
| D7 | Assess IFTA% on biopsy — determines recovery potential | Banff 2019 | TCMR-PR-04 |
**Next stages:** TCMR-PATH-02, TCMR-PATH-03, TCMR-PATH-05, TCMR-PATH-06
**Criteria to proceed:** Diagnosis confirmed; classify TCMR type

## 02. Type I TCMR — Steroid Therapy
**Duration:** 14 days
**Goal:** Pulse corticosteroids for Type I (tubulointerstitial) TCMR. Optimise baseline immunosuppression.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Methylprednisolone 500 mg IV daily x3-5 days | KDIGO 2021 | TCMR-TX-01 |
| T2 | Oral prednisone taper: start 60 mg/day, taper over 2-4 weeks | KDIGO 2021 | TCMR-TX-01 |
| T3 | Optimise tacrolimus target 5-8 ng/mL | KDIGO 2021 | TCMR-TX-04 |
| T4 | Optimise MMF: 2 g/day (reduce if leukopenia) | KDIGO 2021 | TCMR-TX-04 |
| T5 | Assess response at Day 5: Cr trend — if no improvement, consider ATG | AST 2023 | TCMR-TX-03 |
**Next stages:** TCMR-PATH-04, TCMR-PATH-05, TCMR-PATH-06
**Criteria to proceed:** Steroid pulse completed; assess response

## 03. Type II/III or Steroid-Resistant TCMR — ATG Therapy
**Duration:** 21 days
**Goal:** ATG for vascular TCMR (Type II/III) or any steroid-resistant TCMR.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| A1 | ATG (Thymoglobulin) 1.5 mg/kg IV daily — typically 5-14 days | AST 2023 | TCMR-TX-02 |
| A2 | Pre-medicate: MP 50 mg + diphenhydramine + acetaminophen before each dose | AST 2023 | TCMR-TX-02 |
| A3 | Monitor platelets and WBC daily — reduce dose if platelets <50K or WBC <2000 | AST 2023 | TCMR-TX-02 |
| A4 | Start CMV prophylaxis: valganciclovir 900 mg daily | KDIGO 2021 | TCMR-MON-04 |
| A5 | Start PJP prophylaxis: TMP-SMX DS 3x/week | KDIGO 2021 | TCMR-MON-04 |
| A6 | Repeat biopsy on Day 14 if no Cr improvement | AST 2023 | TCMR-MON-01 |
**Next stages:** TCMR-PATH-04, TCMR-PATH-05, TCMR-PATH-06
**Criteria to proceed:** ATG course completed; assess response

## 04. Response Assessment
**Duration:** 90 days
**Goal:** Assess treatment response by Cr, DSA, and repeat biopsy. Manage incomplete response.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| R1 | Weekly Cr x1 month: target — return to baseline or >50% improvement | KDIGO 2021 | TCMR-MON-01 |
| R2 | DSA at 1 and 3 months: TCMR treatment can trigger de novo DSA | KDIGO 2021 | TCMR-MON-02 |
| R3 | Repeat biopsy at 2-4 weeks if Cr not improving | KDIGO 2021 | TCMR-MON-01 |
| R4 | Infectious monitoring: CMV, BK, EBV during intensified immunosuppression | KDIGO 2021 | TCMR-MON-04 |
| R5 | Re-biopsy for suspected missed ABMR or BKVN if no response | AST 2023 | TCMR-EX-02 |
**Next stages:** TCMR-PATH-05, TCMR-PATH-06
**Criteria to proceed:** Response assessed; ongoing management

## 05. Late TCMR and Non-Adherence Management
**Duration:** 365 days
**Goal:** Late TCMR (>1 year) — treat as above PLUS address underlying non-adherence. Worse prognosis.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Same treatment: steroids for Type I, ATG for Type II/III or steroid-resistant | KDIGO 2021 | TCMR-TX-01 |
| L2 | Comprehensive adherence assessment: tac levels (CV), MEMS caps, self-report | AST 2023 | TCMR-REF-01 |
| L3 | Simplify regimen: once-daily LCP-tacrolimus if adherence issue | KDIGO 2021 | TCMR-TX-05 |
| L4 | Social work/psychology referral for barriers (cost, depression, side effects) | AST 2023 | TCMR-REF-01 |
| L5 | CKD management: BP, RAASi, anaemia, MBD as eGFR declines | KDIGO 2021 | TCMR-TX-04 |
**Next stages:** TCMR-PATH-06
**Criteria to proceed:** Late TCMR managed; adherence addressed

## 06. Long-Term Surveillance
**Duration:** 730 days
**Goal:** Prevent recurrence. Monitor for de novo DSA, chronic injury, and graft function.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| S1 | Q3-6 months: eGFR, UPCR, tacrolimus level, DSA — lifelong | KDIGO 2021 | TCMR-MON-01 |
| S2 | Maintain tacrolimus 5-8 ng/mL — do not reduce below 5 | KDIGO 2021 | TCMR-TX-04 |
| S3 | For-cause biopsy: any Cr rise >20% or new DSA | KDIGO 2021 | TCMR-MON-01 |
| S4 | Cardiovascular risk management — leading cause of death with graft | KDIGO 2021 | TCMR-TX-04 |
| S5 | Annual review of adherence, immunosuppression levels, and graft function | AST 2023 | TCMR-REF-01 |
**Next stages:** N/A (final stage)
**Criteria to proceed:** N/A (final stage)

---

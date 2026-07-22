# Minimal Change Disease (MCD) — Clinical Pathway Specification

**Document ID:** MCD-CP-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Clinical Pathways  

---

## 1. Document Purpose

This document defines the complete 6-stage clinical pathway for Minimal Change Disease management within the BGDDR v4.1 decision support framework. Each stage specifies duration, actions, decision points, and integration with KB rules. The pathway is steroid-first in emphasis and covers paediatric and adult populations.

---

## 2. Pathway Overview — Text Diagram

```
STAGE 1: Diagnosis & Classification (0-14 days)
   |   Actions: D1-D7
   v
STAGE 2: Initial Steroid Therapy (0-120 days)
   |   Actions: S1-S8
   v
STAGE 3: Response Assessment & Taper (0-90 days)
   |   Actions: R1-R8
   v
+----+----+----+----+----+
|                        |
FR/SD                Steroid-Resistant
   |                        |
STAGE 4:              STAGE 5:
FR/SD Management      Steroid-Resistant /
(365 days)            Refractory (180 days)
   |                        |
   +----+----+----+----+----+
              |
              v
STAGE 6: Long-Term Monitoring & Transition (730 days)
   Actions: M1-M8
```

---

## 3. Stage 1 — Diagnosis & Classification

**Duration:** 14 days  
**Goal:** Establish definitive MCD diagnosis, classify by steroid response expectation, exclude secondary causes.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| D1 | Clinical assessment | History, physical exam, nephrotic syndrome confirmation | KDIGO 2021 5.1 | MCD-DX-01 |
| D2 | Laboratory workup | UPCR/24h, albumin, Cr/eGFR, lipids, complement, ANA, serologies | KDIGO 2021 5.1.2 | MCD-DX-02 |
| D3 | Urine sediment exam | Fatty casts, oval fat bodies, Maltese crosses | IPNA 2023 | MCD-DX-03 |
| D4 | Renal biopsy | LM, IF (negative), EM (diffuse foot process effacement) | KDIGO 2021 5.2 | MCD-DX-04 |
| D5 | Secondary cause screen | Drugs, infections, malignancy, atopy, autoimmune | ASN 2022 | MCD-DX-05 |
| D6 | Steroid response prediction | Age, severity, biopsy features | ISN 2023 | MCD-PR-01 |
| D7 | Risk stratification | AKI risk, relapse risk, adult vs child | IPNA 2023 | MCD-PR-02 |

### Decision Point at 14 days

- **If MCD confirmed AND no contraindication to steroids:** proceed to Stage 2
- **If secondary cause identified:** treat underlying cause; may still use steroids
- **If biopsy equivocal (e.g., minimal change vs early FSGS):** initiate steroid trial with plan for re-biopsy if resistant

### Key KB Rules Active

- MCD-DX-01: Nephrotic syndrome definition (UPCR >3.5 g/g, albumin <2.5 g/dL)
- MCD-DX-02: Biopsy criteria for definitive diagnosis
- MCD-DX-03: IF negativity requirement
- MCD-DX-04: EM foot process effacement threshold (>80%)
- MCD-DX-05: Secondary cause exclusion checklist

---

## 4. Stage 2 — Initial Steroid Therapy

**Duration:** 120 days  
**Goal:** Achieve complete remission with minimal steroid toxicity.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| S1 | Start prednisone | 1 mg/kg/day (max 80 mg) or 60 mg/m2/day children | KDIGO 2021 5.3 | MCD-TX-01 |
| S2 | Supportive care | RAASi if proteinuria persists >1g; diuretics for oedema; statins | KDIGO 2021 5.7 | MCD-TX-02 |
| S3 | Steroid toxicity monitoring | BP, glucose, electrolytes, growth chart (children) | IPNA 2023 | MCD-MON-01 |
| S4 | Infection prophylaxis | Pneumococcal vaccination; PCP prophylaxis if prolonged high-dose | KDIGO 2021 5.8 | MCD-MON-02 |
| S5 | Daily urine dipstick | For proteinuria quantification; patient/caregiver training | ISN 2023 | MCD-MON-03 |
| S6 | Lab monitoring | Weekly: Cr, albumin, UPCR. Monthly: glucose, lipids | KDIGO 2021 5.3.2 | MCD-MON-04 |
| S7 | Oedema management | Sodium restriction (<2g/day), fluid balance, daily weights | ASN 2022 | MCD-TX-03 |
| S8 | Patient education | Relapse recognition, steroid side effects, infection signs | IPNA 2023 | MCD-REF-01 |

### Decision Point at 4 weeks

- **If urine protein negative (or trace) for 3 consecutive days:** complete remission achieved
- **If proteinuria reduced but persistent:** continue full-dose for additional 2-4 weeks
- **If no response at 4 weeks:** continue to full 8-week course before declaring resistance

---

## 5. Stage 3 — Response Assessment & Taper

**Duration:** 90 days  
**Goal:** Taper steroids safely while maintaining remission; identify FR/SD or resistant patterns.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| R1 | 4-week assessment | Determine CR (negative/trace 3 days) or PR (reduction >50%) | KDIGO 2021 5.4 | MCD-PR-01 |
| R2 | 8-week assessment | If CR: begin taper. If PR: continue full dose 4 more weeks | IPNA 2023 | MCD-PR-02 |
| R3 | Initiate steroid taper | Alternate-day taper over 3-6 months; slower in high-relapse risk | KDIGO 2021 5.4.2 | MCD-TX-04 |
| R4 | Relapse surveillance | Twice-weekly dipstick during taper; weekly after completion | ISN 2023 | MCD-MON-01 |
| R5 | Identify FR/SD pattern | FR: 2 relapses in 6 months or 4 in 12 months; SD: relapse during taper or within 2 weeks of cessation | KDIGO 2021 5.5 | MCD-DX-06 |
| R6 | Steroid-resistant declaration | No remission after 16 weeks of therapy (children) or 24 weeks (adults) | ASN 2022 | MCD-DX-07 |
| R7 | Re-biopsy indication | Resistance, atypical course, late relapse, or sudden change in response | IPNA 2023 | MCD-TX-05 |
| R8 | Transition planning | Proceed to Stage 4 (FR/SD), Stage 5 (resistant), or Stage 6 (remission) | — | — |

### Decision Points

| Scenario | Action |
|---|---|
| Complete remission, infrequent relapse | Proceed to Stage 6 (monitoring) |
| Complete remission, FR/SD pattern | Proceed to Stage 4 |
| Steroid-resistant | Proceed to Stage 5 (re-biopsy required) |

---

## 6. Stage 4 — Frequent Relapse / Steroid-Dependent Management

**Duration:** 365 days  
**Goal:** Maintain remission with steroid-sparing agents; minimise cumulative steroid exposure.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| F1 | Initiate steroid-sparing agent | MMF 1.5-2g/d or CNI (cyclosporine 3-5 mg/kg, tacrolimus 0.05-0.1 mg/kg) | KDIGO 2021 5.5 | MCD-TX-06 |
| F2 | Restart steroids for relapse | Prednisone 1 mg/kg/day until remission, then taper | IPNA 2023 | MCD-TX-07 |
| F3 | Rituximab consideration | For SD or CNI/MMF failure: 375 mg/m2 x 1-4 doses | RITURNS 2014 | MCD-TX-08 |
| F4 | Cyclophosphamide (alternative) | 2-2.5 mg/kg/day x 8-12 wks; second-line only | KDIGO 2021 5.5.3 | MCD-TX-09 |
| F5 | Drug level monitoring | CNI trough levels: cyclosporine 100-150 ng/mL, tacrolimus 5-10 ng/mL | ISN 2023 | MCD-MON-03 |
| F6 | Adverse effect monitoring | CNI: Cr, BP, K+, Mg. MMF: GI, cytopenias. Rituximab: CD19/20, IgG | ASN 2022 | MCD-MON-04 |
| F7 | Immunisation update | Pneumococcal, influenza, varicella; defer live vaccines | KDIGO 2021 5.8 | MCD-MON-02 |
| F8 | Growth and bone health | DEXA scan annually in adults; growth velocity in children | IPNA 2023 | MCD-MON-05 |
| F9 | Transition to adult care | Structured transition programme for adolescent patients | — | MCD-REF-01 |
| F10 | Taper steroid-sparing after 12mo | Gradual withdrawal if sustained remission; monitor for relapse | KDIGO 2021 5.6 | MCD-TX-06 |

### Decision Points

| Scenario | Action |
|---|---|
| Remission on MMF/CNI | Continue for 12 months, then consider taper |
| Rituximab responder | Monitor CD19 recovery; plan repeat dosing |
| Progression to resistance | Re-assess for FSGS (Stage 5) |
| End-stage renal disease (rare) | Renal replacement therapy planning |

---

## 7. Stage 5 — Steroid-Resistant / Refractory Management

**Duration:** 180 days  
**Goal:** Exclude FSGS, achieve remission with intensified immunosuppression, preserve renal function.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| P1 | Confirm steroid resistance | No remission after 16 wks (child) or 24 wks (adult) of prednisone | KDIGO 2021 5.4.3 | MCD-DX-07 |
| P2 | Re-biopsy | Exclude FSGS (segmental sclerosis, tubular atrophy, interstitial fibrosis) | IPNA 2023 | MCD-DX-04 |
| P3 | Check adherence | Drug levels, missed doses, psychosocial barriers | ISN 2023 | MCD-PR-03 |
| P4 | Intensify immunosuppression | CNI first-line (cyclosporine 5 mg/kg or tacrolimus 0.1 mg/kg) | KDIGO 2021 5.6 | MCD-TX-06 |
| P5 | Pulsed steroids | Methylprednisolone 0.5-1 g/day x 3 days (adults) | ASN 2022 | MCD-TX-10 |
| P6 | Rituximab trial | 375 mg/m2 weekly x 2-4 doses if CNI failure | RITURNS 2014 | MCD-TX-08 |
| P7 | Cyclophosphamide rescue | 2-2.5 mg/kg/day x 12 weeks (avoid in adolescents due to gonadal toxicity) | KDIGO 2021 5.6.3 | MCD-TX-09 |
| P8 | Supportive maximal care | RAASi maximisation, BP control, lipid management, nutrition | KDIGO 2021 5.7 | MCD-TX-02 |
| P9 | Assess for FSGS transition | Repeat biopsy at 6 months if no response; ~20% transition | ISN 2023 | MCD-PR-04 |
| P10 | Consider clinical trial | Novel agents (abatacept, adalimumab, ofatumumab) | — | — |

### Decision Points

| Scenario | Action |
|---|---|
| FSGS confirmed on re-biopsy | Transition to FSGS pathway |
| Remission achieved | Taper to lowest effective dose; long-term monitoring |
| No remission after 6 months | Discuss second-line options; genetic testing for podocyte mutations |

---

## 8. Stage 6 — Long-Term Monitoring & Transition

**Duration:** 730 days (ongoing)  
**Goal:** Maintain long-term remission, monitor for late relapse, manage treatment sequelae, transition care.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| M1 | Relapse surveillance | Monthly urine dipstick initially; then every 3 months | ISN 2023 | MCD-MON-01 |
| M2 | Steroid toxicity screening | Annual DEXA, glucose tolerance, cataract exam, growth (children) | KDIGO 2021 5.7 | MCD-MON-05 |
| M3 | Cardiovascular risk | Annual lipids, BP, diabetes screening | ASN 2022 | MCD-MON-01 |
| M4 | Immunosuppression withdrawal | Consider taper after 12-24 months of sustained remission | IPNA 2023 | MCD-TX-06 |
| M5 | Vaccination programme | Complete all vaccinations after immunosuppression minimisation | KDIGO 2021 5.8 | MCD-MON-02 |
| M6 | Pregnancy counselling | MCD typically good outcomes; plan for relapse management | — | MCD-REF-01 |
| M7 | Transition adolescent care | Structured: adult nephrologist introduction, education, self-management | IPNA 2023 | MCD-REF-01 |
| M8 | Long-term outcomes documentation | Renal function, proteinuria, treatment burden, quality of life | — | — |

### Decision Point at 24 months

- **Sustained remission off therapy:** discharge to primary care with annual renal check
- **Infrequent relapse:** treat with short steroid course; consider low-dose maintenance
- **Re-emergent FR/SD:** reassess for change in pathology; re-biopsy if >5 years from diagnosis

---

## 9. Pathway Integration with KB Rules

| Pathway Stage | KB Rules Active | Total |
|---|---|---|
| Stage 1: Diagnosis & Classification | MCD-DX-01 to MCD-DX-05, MCD-PR-01, MCD-PR-02 | 7 |
| Stage 2: Initial Steroid Therapy | MCD-TX-01 to MCD-TX-03, MCD-MON-01 to MCD-MON-04, MCD-REF-01 | 8 |
| Stage 3: Response Assessment & Taper | MCD-DX-06, MCD-DX-07, MCD-PR-01, MCD-PR-02, MCD-TX-04, MCD-TX-05 | 6 |
| Stage 4: FR/SD Management | MCD-TX-06 to MCD-TX-09, MCD-MON-02 to MCD-MON-05, MCD-REF-01 | 9 |
| Stage 5: Steroid-Resistant/Refractory | MCD-DX-04, MCD-DX-07, MCD-PR-03, MCD-PR-04, MCD-TX-02, MCD-TX-06, MCD-TX-08 to MCD-TX-10 | 9 |
| Stage 6: Long-Term Monitoring | MCD-MON-01, MCD-MON-02, MCD-MON-05, MCD-TX-06, MCD-REF-01 | 5 |

---

## 10. Pathway Performance Metrics

| Metric | Target | Measurement |
|---|---|---|
| Time to diagnosis | <14 days | Referral to biopsy report |
| Steroid initiation within 72h | >95% | Stage 2 entry |
| 4-week remission rate | >70% children, >60% adults | Urine dipstick negative |
| Complete remission at 16 weeks | >85% children, >75% adults | UPCR <0.3 g/g |
| Re-biopsy rate for resistance | 100% | Stage 5 entry |
| Steroid-sparing agent use in FR/SD | >80% | Stage 4 entry |
| Long-term renal survival | >90% at 10 years | eGFR >60 |

---

## 11. Exceptions and Special Populations

- **Elderly patients (>70 years):** Lower steroid doses; higher AKI risk; closer monitoring
- **Pregnant patients:** Steroids remain first-line; MMF contraindicated; CNI acceptable
- **Post-transplant:** Recurrence rare (<5%); CNI-based maintenance protective
- **HIV-associated MCD:** Steroids with antiretroviral therapy; avoid MMF
- **Malignancy-associated (Hodgkin lymphoma):** Treat malignancy first; MCD resolves concurrently

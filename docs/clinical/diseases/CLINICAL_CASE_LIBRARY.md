# IgA Nephropathy Clinical Case Library

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `knowledge.models.ClinicalCase`
**Total Cases:** 9 (all gold standard)
**Presentation Types Covered:** 10

---

## 1. Complete Case Inventory (9 Cases)

### Case 1: Classic IgA Nephropathy in Young Adult
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-TYP-001 |
| **Presentation Type** | `typical` |
| **Gold Standard** | Yes |
| **Source** | Seed file `seed_clinical_cases.py` |

**Summary:**
- 28-year-old male with macroscopic hematuria coinciding with URTIs
- BP 138/86, UPCR 1.2, eGFR 78
- Biopsy: M1E0S0T0C0, dominant mesangial IgA (3+)
- Treatment: Ramipril 5mg daily
- Outcome: Stable, UPCR improved to 0.6 at 3 months

**Key Teaching Points:**
- Classic infection-timed hematuria is pathognomonic for IgAN
- Low-risk MEST-C score predicts favorable outcome
- RAASi alone sufficient for low-risk disease

### Case 2: High-Risk IgA with Crescentic Disease
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-RISK-002 |
| **Presentation Type** | `rapid` |
| **Gold Standard** | Yes |

**Summary:**
- 35-year-old male with RPGN: rapid weight gain, frothy urine, edema
- BP 155/95, Cr 2.8 (eGFR 28), UPCR 3.5, albumin 2.9
- Biopsy: M1E1S1T0C2 (30% crescents)
- Treatment: Methylprednisolone 1g IV x3 + prednisolone + MMF
- Outcome: eGFR improved to 45, UPCR 1.2 at 3 months

**Key Teaching Points:**
- Crescentic IgAN requires urgent immunosuppression
- ANCA and anti-GBM serology needed to rule out dual disease
- MMF as adjunctive therapy in crescentic disease

### Case 3: Early IgA with Microscopic Hematuria in Young Woman
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-EAR-003 |
| **Presentation Type** | `early` |
| **Gold Standard** | Yes |

**Summary:**
- 24-year-old female with incidental microscopic hematuria found on routine screening
- Normal BP, eGFR >90, UPCR 0.3, no proteinuria
- Biopsy: M0E0S0T0C0, mesangial IgA (2+)
- Treatment: Observation with annual monitoring
- Outcome: Stable, no progression at 2 years

**Key Teaching Points:**
- Early disease may present asymptomatically
- When to biopsy vs observe in isolated microscopic hematuria
- Pregnancy counseling important for young women with IgAN

### Case 4: Advanced IgA with Progressive CKD
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-ADV-004 |
| **Presentation Type** | `advanced` |
| **Gold Standard** | Yes |

**Summary:**
- 52-year-old male with eGFR declining from 60 to 35 over 3 years
- BP 148/92, UPCR 2.1, Cr 2.2 (eGFR 32)
- Biopsy: M1E0S1T2C0 (significant tubular atrophy/interstitial fibrosis)
- Treatment: Maximized RAASi, added dapagliflozin, prepared for RRT
- Outcome: eGFR stabilized at 30 for 12 months then gradual decline

**Key Teaching Points:**
- T2 lesion (tubular atrophy >50%) predicts poor renal survival
- SGLT2i benefit even in advanced CKD
- Timing of RRT preparation in progressive IgAN

### Case 5: Relapsing IgA After Corticosteroid Withdrawal
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-REL-005 |
| **Presentation Type** | `relapse` |
| **Gold Standard** | Yes |

**Summary:**
- 32-year-old male initially treated with prednisolone for IgAN
- Achieved remission after 6 months, steroids tapered
- Relapsed 4 months after steroid cessation: UPCR 1.8, hematuria+
- Re-treated with corticosteroids; maintained on MMF for steroid-sparing

**Key Teaching Points:**
- Relapse rate ~30% after steroid withdrawal in high-risk IgAN
- MMF as steroid-sparing option (limited evidence)
- Re-biopsy may be indicated if atypical relapse pattern

### Case 6: Treatment-Resistant IgA with Crescentic Disease
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-RES-006 |
| **Presentation Type** | `resistant` |
| **Gold Standard** | Yes |

**Summary:**
- 40-year-old male with persistent proteinuria >3g/day despite full-dose RAASi and 6 months of corticosteroids
- eGFR declining from 55 to 40 over 8 months
- Repeat biopsy: active crescents (15%) plus chronic changes T1
- Sequential therapy: cyclophosphamide pulse, then rituximab

**Key Teaching Points:**
- Definition of treatment resistance in IgAN
- Role of repeat biopsy in treatment-resistant disease
- Cyclophosphamide and rituximab as rescue therapy

### Case 7: IgA in Pregnancy with Pre-Eclampsia Risk
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-PRE-007 |
| **Presentation Type** | `special` |
| **Gold Standard** | Yes |

**Summary:**
- 30-year-old female with known IgAN (diagnosed age 26, in remission)
- Planning pregnancy: UPCR 0.5, eGFR 85, BP on labetalol
- RAASi discontinued before conception, switched to labetalol/nifedipine
- Developed pre-eclampsia at 32 weeks, delivered at 34 weeks
- Postpartum: restarted RAASi, renal function returned to baseline

**Key Teaching Points:**
- Pre-conception counseling essential in IgAN patients
- RAASi must be discontinued before pregnancy
- High risk of pre-eclampsia in IgAN (15-25%)
- BP management in pregnancy differs (labetalol, nifedipine, methyldopa)

### Case 8: Pediatric IgA with Recurrent Macroscopic Hematuria
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-PED-008 |
| **Presentation Type** | `typical` (pediatric) |
| **Gold Standard** | Yes |

**Summary:**
- 10-year-old male with recurrent episodes of visible hematuria with febrile illnesses
- Normal BP, eGFR >90, UPCR 0.4 between episodes
- Biopsy: M1E0S0T0C0
- Treatment: Observation, avoid nephrotoxins, tonsillectomy discussion

**Key Teaching Points:**
- Pediatric IgAN is common and generally favorable
- Tonsillectomy role remains controversial
- Spontaneous remission rate higher in children than adults
- Long-term follow-up needed even after remission

### Case 9: Recurrent IgA in Kidney Transplant
| Property | Value |
|----------|-------|
| **Case ID** | CASE-IGA-TXP-009 |
| **Presentation Type** | `advanced` (transplant) |
| **Gold Standard** | Yes |

**Summary:**
- 45-year-old male with IgAN-related ESKD, received living-donor transplant 3 years ago
- New-onset hematuria and proteinuria (UPCR 1.2), eGFR 52
- Protocol biopsy: mesangial IgA deposits (2+), M1E0S0T0C0
- Treatment: Optimized RAASi, discussed recurrence with patient
- Stable at 12 months follow-up

**Key Teaching Points:**
- Recurrent IgAN in transplant: 10-50% at 5 years
- Protocol biopsies detect recurrence before clinical deterioration
- Graft loss from recurrence ~5-10%
- No proven therapy for transplant recurrence

---

## 2. Coverage Matrix Across Presentation Types

| Presentation Type | Cases | Covered | Case IDs |
|-------------------|-------|---------|----------|
| Typical | 2 of 9 | YES | CASE-IGA-TYP-001, CASE-IGA-PED-008 |
| Atypical | 0 of 9 | NO | -- |
| Early | 1 of 9 | YES | CASE-IGA-EAR-003 |
| Advanced | 2 of 9 | YES | CASE-IGA-ADV-004, CASE-IGA-TXP-009 |
| Rapid | 1 of 9 | YES | CASE-IGA-RISK-002 |
| Remission | 0 of 9 | NO | -- |
| Relapse | 1 of 9 | YES | CASE-IGA-REL-005 |
| Resistant | 1 of 9 | YES | CASE-IGA-RES-006 |
| Complications | 0 of 9 | NO | -- |
| Special | 1 of 9 | YES | CASE-IGA-PRE-007 |

**Coverage: 7 of 10 presentation types (70%)**

---

## 3. Case Validation Status

| Case ID | Gold Standard | Expected Diff | Expected Reasoning | Expected Recos | Expected Monitoring | Expected Followup |
|---------|---------------|---------------|-------------------|----------------|--------------------|-------------------|
| CASE-IGA-TYP-001 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-RISK-002 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-EAR-003 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-ADV-004 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-REL-005 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-RES-006 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-PRE-007 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-PED-008 | VALIDATED | Yes | Yes | Yes | Yes | Yes |
| CASE-IGA-TXP-009 | VALIDATED | Yes | Yes | Yes | Yes | Yes |

**All 9 cases have complete expected-reasoning-outputs (differential, reasoning, recommendations, monitoring, followup).**

---

## 4. Planned Case Expansions

### V4.2 Target Cases

| Priority | Presentation Type | Description |
|----------|-------------------|-------------|
| 1 | Atypical | IgAN with nephrotic-range proteinuria mimicking MCD |
| 2 | Complications | IgAN with malignant hypertension and TMA |
| 3 | Remission | Long-term complete remission after immunosuppression |
| 4 | Special | IgAN in elderly (>65 years) with comorbidities |
| 5 | Atypical | IgAN with ANCA positivity (dual disease) |

### Expansion Goals
- Achieve 100% presentation-type coverage (10/10 types) by V4.3
- Add 2-3 cases per major disease (membranous, lupus, FSGS)
- Include cases with multi-morbidity for complex reasoning validation

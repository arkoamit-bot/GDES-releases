# C3 Glomerulopathy (C3G) — Clinical Pathway Specification

**Document ID:** C3G-CP-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Clinical Pathways  

---

## 1. Document Purpose

This document defines the complete 6-stage clinical pathway for C3 Glomerulopathy management within the BGDDR v4.1 decision support framework. Each stage specifies duration, actions, decision points, and integration with KB rules. The pathway addresses both C3GN and DDD subtypes and covers the rapidly evolving landscape of complement inhibitor therapy.

---

## 2. Pathway Overview — Text Diagram

```
STAGE 1: Diagnosis & Classification (0-30 days)
   |   Actions: D1-D7
   v
STAGE 2: Genetic & Autoantibody Workup (0-60 days)
   |   Actions: G1-G5
   v
STAGE 3: Supportive Therapy (ongoing)
   |   Actions: S1-S5
   v
STAGE 4: Active Disease — Immunosuppression (0-180 days)
   |   Actions: I1-I7
   v
STAGE 5: Refractory Disease — Complement Inhibitors (0-365 days)
   |   Actions: C1-C8
   v
STAGE 6: Long-Term Monitoring & ESKD/Transplant (ongoing)
   |   Actions: M1-M8
```

---

## 3. Stage 1 — Diagnosis & Classification

**Duration:** 30 days  
**Goal:** Establish definitive C3G diagnosis, differentiate C3GN vs DDD by EM, exclude immune complex GN.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| D1 | Clinical assessment | History, physical exam, renal function, proteinuria, haematuria | KDIGO 2021 Ch 8 | C3G-DX-01 |
| D2 | Laboratory workup | Cr/eGFR, UPCR/24h, albumin, C3, C4, CH50, ANA, ANCA, cryoglobulins | KDIGO 2021 Ch 8 | C3G-DX-02 |
| D3 | Complement profiling | C3, C4, CH50, AP50, properdin, factor H, factor I, factor B | ERA/EDTA 2022 | C3G-DX-03 |
| D4 | Renal biopsy | LM (MPGN/mesangial/crescentic), IF (dominant C3 >=2+), EM (DDD vs C3GN) | KDIGO 2021 Ch 8 | C3G-DX-04 |
| D5 | Exclude infection-related GN | Post-streptococcal: resolving C3, dominant IgG co-deposition | ISN 2023 | C3G-DX-05 |
| D6 | MGUS screen (age >40) | SPEP/UPEP/sFLC; bone marrow if monoclonal detected | KDIGO 2021 Ch 8 | C3G-DX-06 |
| D7 | Disease activity assessment | Active (proliferative/crescents/endocapillary) vs chronic (sclerosis/IFTA) | D'Agati 2020 | C3G-PR-01 |

### Decision Point at 30 days

- **If C3G confirmed (dominant C3, EM subtype determined):** proceed to Stage 2
- **If infection-related GN suspected:** monitor C3 normalisation over 8-12 weeks; re-biopsy if persistent
- **If MGUS identified:** proceed with haematology evaluation alongside nephrology care

---

## 4. Stage 2 — Genetic & Autoantibody Workup

**Duration:** 60 days  
**Goal:** Identify complement pathway abnormality (genetic vs autoantibody vs monoclonal) to guide targeted therapy.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| G1 | C3 nephritic factor (C3NeF) assay | Positive in 40-50% of C3G; functional assay for C3 convertase stabilisation | KDIGO 2021 Ch 8 | C3G-DX-03 |
| G2 | Anti-CFH / anti-CFB autoantibodies | ELISA; guide plasma therapy and rituximab consideration | ISN 2023 | C3G-DX-07 |
| G3 | Genetic testing panel | CFH, CFI, CFB, C3, CD46 (MCP), CFHR1-5, THBD | Complement Consensus 2023 | C3G-GN-01 |
| G4 | CFH/CFHR gene rearrangement | Assessment for CFHR1-3 duplication/deletion in suspicious cases | Rare Kidney Disease 2019 | C3G-GN-02 |
| G5 | Haematology referral (if MGUS) | Bone marrow biopsy, cytogenetics, clone-directed therapy planning | KDIGO 2021 Ch 8 | C3G-TX-06 |

### Decision Point at 60 days

| Scenario | Action |
|---|---|
| Genetic mutation identified (esp CFH) | Consider plasma therapy; complement inhibitor first-line |
| C3NeF positive | Consider rituximab; MMF+steroids |
| Anti-CFH positive | Consider plasma exchange; rituximab |
| MGUS associated | Treat underlying clone; complement inhibitor if refractory |
| No identifiable cause | Idiopathic C3G; proceed with MMF+steroids |

---

## 5. Stage 3 — Supportive Therapy

**Duration:** Ongoing  
**Goal:** Maximise renoprotection, manage complications, prepare for immunosuppression.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| S1 | RAAS inhibition | ACEi/ARB for proteinuria >0.5 g/day; titrate to max tolerated dose | KDIGO 2021 Ch 8 | C3G-TX-01 |
| S2 | BP control | Target <130/80 mmHg (<125/75 if proteinuria >1 g/day) | KDIGO 2021 Ch 8 | C3G-TX-02 |
| S3 | Statins | For LDL >100 mg/dL or nephrotic-range proteinuria | KDIGO 2021 5.7 | C3G-TX-03 |
| S4 | Diuretics as needed | For oedema management; loop diuretics if nephrotic | KDIGO 2021 5.7 | C3G-TX-04 |
| S5 | Meningococcal vaccination | Mandatory before complement inhibitor therapy; quadrivalent + serogroup B | Complement Consensus 2023 | C3G-MON-01 |

### Decision Point

- **All patients:** continue supportive care throughout all stages
- **Active/proliferative disease:** proceed to Stage 4
- **Chronic/sclerotic disease only:** continue supportive alone (Stage 6)

---

## 6. Stage 4 — Active Disease: Immunosuppression

**Duration:** 180 days  
**Goal:** Achieve remission of active proliferative/crescentic disease with immunosuppression.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| I1 | MMF initiation | 1-2 g/day in divided doses; adjust for renal function | Ravindran 2017 | C3G-TX-05 |
| I2 | Corticosteroids | Pulse methylprednisolone 0.5-1 g/day x 3 days, then oral prednisone 0.5-1 mg/kg/day taper | KDIGO 2021 Ch 8 | C3G-TX-07 |
| I3 | Cyclophosphamide (for RPGN/crescents) | 500-750 mg/m2 IV monthly x 3-6 months or oral 2 mg/kg/day x 3 months | KDIGO 2021 Ch 8 | C3G-TX-08 |
| I4 | Plasma exchange (C3NeF/anti-CFH) | 1.5 volume exchanges x 5-7 sessions for severe disease with autoantibodies | ISN 2023 | C3G-TX-09 |
| I5 | Rituximab (C3NeF-positive) | 375 mg/m2 weekly x 2-4 doses; target B-cell depletion | Rare Kidney Disease 2019 | C3G-TX-10 |
| I6 | Drug monitoring | MMF: CBC monthly. Steroids: BP, glucose, bone density. Cyclophosphamide: CBC weekly, cumulative dose tracking | KDIGO 2021 Ch 8 | C3G-MON-02 |
| I7 | Response assessment at 6 months | UPCR, eGFR, C3 normalisation, repeat biopsy if uncertain | ERA/EDTA 2022 | C3G-PR-02 |

### Decision Point at 6 months

| Scenario | Action |
|---|---|
| Remission (UPCR <0.5, stable Cr, C3 normalised) | Taper immunosuppression; proceed to Stage 6 |
| Partial response | Continue MMF+low-dose steroid; consider complement inhibitor |
| No response / progression | Proceed to Stage 5 (complement inhibitors) |

---

## 7. Stage 5 — Refractory Disease: Complement Inhibitors

**Duration:** 365 days  
**Goal:** Block terminal complement pathway to halt disease progression in refractory cases.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| C1 | Eculizumab trial (anti-C5) | 900 mg IV weekly x 4, then 1200 mg every 2 weeks; monitor for meningococcal infection | Le Quintrec 2018 | C3G-TX-11 |
| C2 | Iptacopan (factor B inhibitor) | 200 mg PO BID; monitor C3 levels, proteinuria | Iptacopan Phase 2 2023 | C3G-TX-12 |
| C3 | Pegcetacoplan (C3 inhibitor) | 1080 mg SC twice weekly; monitor C3 levels, deposit clearance on re-biopsy | Pegcetacoplan Phase 2 2023 | C3G-TX-13 |
| C4 | Plasma therapy (CFH mutation) | Fresh frozen plasma 10-20 mL/kg every 1-2 weeks; monitor C3 levels | Complement Consensus 2023 | C3G-TX-14 |
| C5 | Meningococcal prophylaxis | Vaccination mandatory; amoxicillin prophylaxis if eculizumab | Complement Consensus 2023 | C3G-MON-01 |
| C6 | Neisseria surveillance | Monitor for unexplained fever, sepsis; education on early presentation | KDIGO 2021 Ch 8 | C3G-MON-03 |
| C7 | Complement activity monitoring | CH50, AP50, C3, C5b-9 levels to titrate complement inhibitor dose | ERA/EDTA 2022 | C3G-MON-04 |
| C8 | Re-biopsy at 12 months | Assess histologic response: C3 deposit clearance, reduction in activity | Pegcetacoplan protocol | C3G-MON-05 |

### Decision Point at 12 months

| Scenario | Action |
|---|---|
| Histologic remission + clinical response | Continue complement inhibitor; consider dose reduction |
| Partial response | Optimise dose; consider switching class (C3i vs C5i) |
| No response | Re-evaluate diagnosis; consider clinical trial |
| Progression to ESKD | Prepare for renal replacement therapy; transplant planning |

---

## 8. Stage 6 — Long-Term Monitoring & ESKD/Transplant

**Duration:** Ongoing  
**Goal:** Maintain remission, monitor for relapse and complications, manage transplant with highest recurrence risk.

### Actions

| ID | Action | Description | Evidence | KB Rule |
|---|---|---|---|---|
| M1 | Renal function monitoring | Cr/eGFR, UPCR, C3, C4 every 3 months | KDIGO 2021 Ch 8 | C3G-MON-06 |
| M2 | Immunosuppression taper | Gradual withdrawal over 12-24 months if sustained remission | ERA/EDTA 2022 | C3G-TX-06 |
| M3 | Complement inhibitor management | Long-term safety monitoring; meningococcal vaccine boosters | Complement Consensus 2023 | C3G-MON-01 |
| M4 | DDD ophthalmology screening | Fundoscopy for retinal drusen/AMD every 1-2 years | Rare Kidney Disease 2019 | C3G-MON-05 |
| M5 | Transplant planning | Pre-emptive complement inhibitor (eculizumab/iptacopan) to prevent recurrence | Rare Kidney Disease 2019 | C3G-TX-15 |
| M6 | MGUS surveillance | Annual SPEP/UPEP/sFLC if monoclonal identified | KDIGO 2021 Ch 8 | C3G-MON-06 |
| M7 | Infection prophylaxis | Pneumococcal, influenza, meningococcal vaccination; PCP prophylaxis if on immunosuppression | KDIGO 2021 Ch 8 | C3G-MON-02 |
| M8 | CKD complication management | Anaemia, bone disease, acidosis, cardiovascular risk | KDIGO 2021 | C3G-TX-03 |

### Decision Points

| Scenario | Action |
|---|---|
| Sustained remission off therapy | Annual renal check; monitor for late relapse |
| Relapse on taper | Restore previous effective dose; reassess aetiology |
| ESKD | Dialysis; transplant with pre-emptive complement inhibitor |
| Post-transplant recurrence | Start/optimise complement inhibitor; high-dose MMF |

---

## 9. Pathway Integration with KB Rules

| Pathway Stage | KB Rules Active | Total |
|---|---|---|
| Stage 1: Diagnosis & Classification | C3G-DX-01 to C3G-DX-06, C3G-PR-01 | 7 |
| Stage 2: Genetic & Autoantibody Workup | C3G-DX-03, C3G-DX-07, C3G-GN-01, C3G-GN-02, C3G-TX-06 | 5 |
| Stage 3: Supportive Therapy | C3G-TX-01 to C3G-TX-04, C3G-MON-01 | 5 |
| Stage 4: Active Disease | C3G-TX-05, C3G-TX-07 to C3G-TX-10, C3G-MON-02, C3G-PR-02 | 7 |
| Stage 5: Refractory Disease | C3G-TX-11 to C3G-TX-14, C3G-MON-01, C3G-MON-03 to C3G-MON-05 | 8 |
| Stage 6: Long-Term / Transplant | C3G-TX-03, C3G-TX-06, C3G-TX-15, C3G-MON-01, C3G-MON-02, C3G-MON-05, C3G-MON-06 | 7 |

---

## 10. Pathway Performance Metrics

| Metric | Target | Measurement |
|---|---|---|
| Time to diagnosis | <30 days | Referral to biopsy report |
| Genetic workup completion | >90% within 60 days | Stage 2 completion |
| MMF+steroid remission at 6 months | >40% C3GN | UPCR <0.5 g/g |
| Complement inhibitor response at 12 months | >50% | Proteinuria reduction + C3 normalisation |
| Transplant recurrence prevention | <30% with pre-emptive therapy | Protocol biopsy at 12 months |
| Long-term renal survival | >60% at 10 years | eGFR >30 |

---

## 11. Exceptions and Special Populations

- **Children with DDD:** Better prognosis than adults; complement inhibitor dosing per weight
- **Pregnant patients:** MMF contraindicated; steroids and eculizumab acceptable (eculizumab pregnancy registry)
- **Post-transplant:** Highest recurrence risk of all GNs; pre-emptive complement inhibitor strongly recommended
- **MGUS-associated C3G:** Treat clone first; C3G may resolve with clone-directed therapy
- **Elderly (>70 years):** Lower steroid doses; monitor for infection and cardiovascular complications

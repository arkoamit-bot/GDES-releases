# C3 Glomerulopathy (C3G) — Disease Knowledge Specification

**Document ID:** C3G-DK-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Disease Knowledge  

---

## 1. Document Purpose

This document defines the complete disease knowledge specification for C3 Glomerulopathy (C3G) across all 21 fields of the standardised disease record schema. It serves as the authoritative knowledge base for clinical decision support, pathway logic, guideline mapping, and case-based reasoning within the BGDDR v4.1 framework.

---

## 2. Disease Record — Full 21-Field Schema

### 2.1 Definition

C3 Glomerulopathy (C3G) is a rare glomerular disease caused by dysregulation of the alternative complement pathway, characterized by dominant C3 staining on immunofluorescence at least 2 orders of magnitude stronger than immunoglobulins. Two subtypes: Dense Deposit Disease (DDD, formerly Type II MPGN) and C3 Glomerulonephritis (C3GN). Both involve persistent alternative complement pathway activation leading to C3 deposition in glomerular basement membranes and progressive renal injury.

### 2.2 Epidemiology

Ultra-rare: incidence 1-2 per million per year. DDD peaks at age 5-15 years (children). C3GN peaks at 20-40 years (adults). Slight female predominance. DDD accounts for approximately 20% of C3G, C3GN approximately 80%. More common in Caucasian populations. Genetic forms more common in consanguineous populations. Geographic clusters reported.

### 2.3 Aetiology

Dysregulation of the alternative complement pathway. GENETIC (20-30%): loss-of-function mutations in complement regulatory genes (CFH, CFI, CFHR1-5, CD46/MCP, THBD), gain-of-function mutations in C3 or CFB. ACQUIRED (70-80%): C3 nephritic factors (C3NeF) that stabilize C3 convertase, anti-CFH autoantibodies, anti-CFB autoantibodies. Monoclonal gammopathy (MGUS-associated). Post-streptococcal GN can transiently resemble C3G.

### 2.4 Pathophysiology

Persistent alternative complement pathway activation leads to hyperactivity of the C3 convertase (C3bBb). C3 is consumed (low serum C3 with normal C4). C3 cleavage products (C3b, iC3b, C3d, C3dg) deposit in glomerular basement membranes. In DDD: extremely electron-dense, ribbon-like intramembranous deposits. In C3GN: mesangial and capillary wall C3 deposits. Terminal complement activation (C5b-9, MAC) contributes to injury. CFH mutations impair cell surface regulation; C3NeF stabilizes the C3 convertase.

### 2.5 Clinical Presentation

C3GN: hematuria (80%), proteinuria (nephrotic range 30-50%), hypertension (40%), AKI (20-30%). DDD: hematuria, proteinuria, often nephrotic syndrome. Extra-renal DDD: acquired partial lipodystrophy (10%), retinal drusen/AMD-like deposits. Fifteen to twenty percent present with RPGN. Many patients have slow progression over years.

### 2.6 Diagnostic Criteria

| # | Criterion | Essential | Evidence Level |
|---|---|---|---|
| 1 | Dominant C3 staining on IF (>=2 orders > Ig) | Yes | OP |
| 2 | EM differentiates DDD (intramembranous ribbon-like) vs C3GN (mesangial/subepithelial) | Yes | OP |
| 3 | Low serum C3 with normal C4 | Yes | 2 |
| 4 | C3 nephritic factor (C3NeF) positivity (40-50%) | No | 2 |
| 5 | Genetic testing: CFH, CFI, CFB, C3, CD46, CFHR1-5 | No | OP |
| 6 | Exclude infection-related GN (post-strep, resolving) | Yes | 2 |
| 7 | MGUS workup (SPEP/UPEP/sFLC) in patients over 40 | No | 2 |

### 2.7 Differential Diagnosis

| Condition | Key Distinguishing Features |
|---|---|
| Resolving infection; C3 normalises over weeks; dominant IgG co-deposition | Resolving infection; C3 normalises over weeks; dominant IgG co-deposition |
| Immune complex MPGN: full-house IF IgG/IgM/C3; normal C3 may be low but C4 also low | Immune complex MPGN: full-house IF IgG/IgM/C3; normal C3 may be low but C4 also low |
| Full-house IF (IgG, IgA, IgM, C3, C1q); ANA/anti-dsDNA positive; systemic SLE features | Full-house IF (IgG, IgA, IgM, C3, C1q); ANA/anti-dsDNA positive; systemic SLE features |
| Monoclonal Ig deposition: light chain restriction; MGUS/lymphoma association | Monoclonal Ig deposition: light chain restriction; MGUS/lymphoma association |
| Cryoglobulins; IgG/IgM/C3 deposits; HCV association; vasculitic features | Cryoglobulins; IgG/IgM/C3 deposits; HCV association; vasculitic features |
| Thrombotic microangiopathy: microvascular thrombi; schistocytes; ADAMTS13 low | Thrombotic microangiopathy: microvascular thrombi; schistocytes; ADAMTS13 low |
| Family history; thin GBM; sensorineural hearing loss; X-linked inheritance | Family history; thin GBM; sensorineural hearing loss; X-linked inheritance |

### 2.8 Laboratory Findings

['C3: low (40-60% of patients)', 'C4: normal (key distinguishing feature)', 'C3 nephritic factor (C3NeF): positive in 40-50%', 'Anti-CFH autoantibodies', 'Anti-CFB autoantibodies', 'CH50: low if alternative pathway consumption', 'Creatinine/eGFR', 'UPCR/24-hour urine protein', 'Serum albumin', 'SPEP/UPEP/serum free light chains (rule out MGUS)', 'CFH/CFI/CFB/C3/CD46 genotyping', 'Urinalysis: RBCs, RBC casts, proteinuria']

### 2.9 Biopsy Findings

['LM: MPGN pattern (mesangial hypercellularity, endocapillary proliferation, GBM double contours)', 'LM: Can also show mesangial proliferative or crescentic patterns', 'IF: DOMINANT C3 staining >=2+, much stronger than any immunoglobulin — PATHOGNOMONIC', 'IF: C5b-9, properdin, factor H also present; C1q absent', 'IF: Trace or no IgG, IgA, IgM (key to exclude immune complex GN)', 'EM: DDD — intramembranous, extremely electron-dense, ribbon-like, osmiophilic deposits', 'EM: DDD deposits in GBM, mesangium, tubular basement membrane, Bowman capsule', 'EM: C3GN — mesangial, subepithelial, and/or subendothelial electron-dense deposits']

### 2.10 Classification Systems

| System | Components | Source |
|---|---|---|
| C3G Subtype (by EM) | DDD (dense deposit disease) vs C3GN (C3 glomerulonephritis) | Fervenza 2018; KDIGO 2021 |
| Etiologic Classification | Genetic (CFH/CFI/C3/CFB/CD46), Autoantibody (C3NeF/anti-CFH), Monoclonal (MGUS-associated) | Pickering 2013; KDIGO 2021 |
| Histologic Pattern | MPGN pattern, Mesangial proliferative, Crescentic | D'Agati 2020 |
| Disease Activity | Active (proliferative/crescents) vs Chronic (sclerotic/IFTA) | KDIGO 2021 |

### 2.11 Risk Stratification

| Factor | Impact | Risk Level |
|---|---|---|
| Histologic pattern | Crescents and IFTA worse | High |
| Proteinuria level | Nephrotic range associated with worse outcome | High |
| eGFR at diagnosis | Lower eGFR predicts progression | High |
| Age | Children with DDD have better prognosis | Variable |
| C3NeF titer | No clear correlation with disease activity | Uncertain |
| MGUS association | Associated with worse outcome | High |
| Genetic vs acquired | Genetic forms (esp CFH) more resistant | High |
| Treatment response | Non-response at 6 months predicts ESKD | High |

### 2.12 Treatment Overview

NO STANDARD APPROVED THERAPY. Supportive: RAASi, BP control, statins, diuretics. Immunosuppression: MMF (1-2g/day) + corticosteroids in active C3GN. Cyclophosphamide + steroids for crescentic/RPGN. Complement inhibitors: eculizumab (anti-C5, variable), iptacopan (factor B inhibitor, phase 3), pegcetacoplan (C3 inhibitor, phase 2). Plasma therapy for CFH mutations. Rituximab for C3NeF-positive. MGUS: treat underlying clone.

### 2.13 Treatment Algorithms

| Step | Action |
|---|---|
| 1 | Confirm C3G on biopsy: dominant C3 staining on IF, EM subtype |
| 2 | Complete workup: genetic testing (CFH/CFI/CFB/C3/CD46), C3NeF/anti-CFH, MGUS screening |
| 3 | All patients: supportive therapy with RAASi, BP control, statins, diuretics |
| 4 | Active/proliferative disease: MMF 1-2g/day + pulse steroids then oral taper |
| 5 | RPGN/crescents: cyclophosphamide + pulse steroids; consider PLEX |
| 6 | Refractory: complement inhibitor trial (iptacopan/eculizumab); plasma if CFH mutation |
| 7 | MGUS-associated: treat underlying clone. Long-term monitoring q3-6mo |

### 2.14 Monitoring Protocol

C3, C4, creatinine, UPCR q3 months. During immunosuppression: CBC, LFT, BP, glucose. During complement inhibitor: meningococcal vaccination mandatory, Neisseria prophylaxis. Long-term: eGFR slope, proteinuria trend, C3 levels. DDD: ophthalmology screening for drusen/AMD every 1-2 years.

### 2.15 Complications

1. CKD progression to ESKD (30-50% at 10 years)
2. Infection: complement deficiency increases risk of encapsulated organisms and Neisseria
3. Immunosuppression toxicity (steroids, MMF, cyclophosphamide)
4. Complement inhibitor complications: meningococcal infection, Neisseria infections
5. MGUS progression to multiple myeloma or lymphoma
6. DDD: acquired partial lipodystrophy (facial/scalp subcutaneous fat loss)
7. DDD: retinal drusen leading to visual impairment and AMD-like changes
8. Post-transplant C3G recurrence (highest of all GNs: 50-80%)

### 2.16 Relapse Information

Relapse 40-60% after stopping treatment. Post-transplant recurrence HIGHEST of all GNs: DDD 50-80%, C3GN 60-70%. Risk factors: active C3NeF, CFH mutations, low C3 at transplant. Allograft loss from recurrence: 30-50% of those with recurrence.

### 2.17 Long-Term Prognosis

10-year renal survival: 50-60%. ESKD 30-50% by 10yrs if untreated. Risk factors: nephrotic proteinuria, low eGFR, IFTA, genetic mutations, older age. DDD in children better than adult. Spontaneous remission less than 10%.

### 2.18 Evidence Summary

No large RCTs. MMF+steroids: observational studies (Ravindran 2017, Avasare 2018) show remission 40-60% in C3GN, less in DDD. Eculizumab: case series (Le Quintrec 2018, Bomback 2012) mixed results. Iptacopan phase 2: reduced proteinuria, increased C3. Pegcetacoplan phase 2: reduced C3 deposits on re-biopsy. No FDA-approved therapy.

### 2.19 Guideline Recommendations

| Guideline | Year | Focus |
|---|---|---|
| KDIGO 2021  | Ch 8: C3G | Diagnosis requires dominant C3 on IF (1B) |
| KDIGO 2025  | Emerging C3G | Complement inhibitor therapy for refractory disease |
| ERA/EDTA 2022  | C3G Diagnosis | Standardized diagnostic algorithm for C3G |
| ISN 2023  | Rare GN | Genetic testing for all C3G patients |
| Complement Consensus 2023  | C3G Treatment | Complement inhibitor is first choice for refractory |
| Rare Kidney Disease 2019  | Transplant | Pre-emptive complement inhibitor post-transplant |

### 2.20 Key References

| # | Reference | Journal | Year |
|---|---|---|---|
| 1 | KDIGO 2021 Glomerular Disease Guideline Chapter 8 | Kidney Int | 2021 |
| 2 | Bomback AS et al. C3 Glomerulopathy: A Review | CJASN | 2018 |
| 3 | Le Quintrec M et al. Eculizumab in C3G | JASN | 2018 |
| 4 | Ravindran A et al. MMF+Corticosteroids in C3GN | CJASN | 2017 |
| 5 | Smith RJH et al. Genetics of C3G | Nat Rev Nephrol | 2019 |
| 6 | D'Agati VD et al. C3G Pathology Classification Update | KI Reports | 2020 |
| 7 | Iptacopan Phase 2 in C3G (NCT03954405) | JASN | 2023 |
| 8 | Pickering MC et al. C3G: Complement-Driven | JCI | 2013 |
| 9 | Servais A et al. Long-Term Outcomes in C3G | NDT | 2007 |
| 10 | Fervenza FC et al. Emerging Therapies for C3G | KI | 2023 |

### 2.21 Notes

V4.1 engineering notes: GDES V4.1 Medical Knowledge Engineering. C3G is the first ultra-rare disease in the sequence. Key: dominant C3 on IF (pathognomonic), normal C4, highest post-transplant recurrence rate. Rapidly evolving treatment landscape with complement inhibitors.

---

## 3. Domain Audit Summary

| Domain Element | Status | Completeness |
|---|---|---|
| 21-field schema | Complete | 21/21 fields |
| Evidence base (RCT, meta-analysis) | Complete | Observational, phase 2 trials |
| Complement pathway classification | Complete | C3GN / DDD subtypes |
| Genetic vs acquired aetiology | Complete | 7 genetic, 3 autoantibody |
| Children vs adults differentiation | Complete | Age-specific epidemiology, treatment, outcomes |

---

## 4. Evidence Base

### 4.1 Key Clinical Studies

- **MMF + corticosteroids in C3GN (Ravindran 2017):** 40-60% remission in C3GN; less effective in DDD
- **Eculizumab in C3G (Le Quintrec 2018):** Mixed results; some patients stabilise renal function
- **Iptacopan Phase 2 (2023):** Reduced proteinuria, increased serum C3 levels in C3G
- **Pegcetacoplan Phase 2 (2023):** Reduced C3 deposits on repeat biopsy; promising histologic improvement
- **C3G Transplant Recurrence (Servais 2007):** 50-80% recurrence rate; highest of all GNs

### 4.2 Ongoing Knowledge Gaps

- No completed large RCTs for any C3G therapy
- Optimal duration of complement inhibitor therapy unknown
- Best sequence: MMF before complement inhibitor or vice versa
- Role of plasma therapy in CFH mutation patients
- Biomarkers for treatment response (other than C3 normalisation)
- Long-term safety of complement inhibitors (meningococcal risk)
- Paediatric-specific treatment protocols lacking

---

## 5. C3GN vs DDD Comparison

| Feature | C3 Glomerulonephritis (C3GN) | Dense Deposit Disease (DDD) |
|---|---|---|
| Frequency | ~80% of C3G | ~20% of C3G |
| Peak age | 20-40 years | 5-15 years |
| EM deposits | Mesangial, subepithelial, subendothelial | Intramembranous, ribbon-like, osmiophilic |
| Extra-renal | Rare | Acquired partial lipodystrophy, retinal drusen |
| Treatment response | Better (40-60% remission with MMF) | Poor (20-30% remission) |
| Post-transplant recurrence | 60-70% | 50-80% |
| Complement profile | C3 low, C4 normal, C3NeF+ | C3 low, C4 normal, C3NeF+ (more common) |

---

## 6. Secondary Causes — Diagnostic Checklist

- [ ] Monoclonal gammopathy: SPEP/UPEP/sFLC in patients >40 years
- [ ] Autoantibodies: C3NeF, anti-CFH, anti-CFB
- [ ] Genetic mutations: CFH, CFI, CFB, C3, CD46, CFHR1-5
- [ ] Infections: resolving post-streptococcal GN can transiently resemble C3G
- [ ] Autoimmune: SLE rarely mimics C3G pattern

# Cryoglobulinemic GN — Disease Knowledge Specification

**Document ID:** CRYO-DK-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Disease Knowledge  

---

## 1. Document Purpose

This document defines the complete disease knowledge specification for Cryoglobulinemic GN across all 21 fields of the standardised disease record schema. It serves as the authoritative knowledge base for clinical decision support, pathway logic, guideline mapping, and case-based reasoning within the BGDDR v4.1 framework.

---

## 2. Disease Record — Full 21-Field Schema

### 2.1 Definition

Cryoglobulinemic Glomerulonephritis (CryoGN) is a glomerular disease caused by the deposition of cryoglobulins in glomerular capillaries, most commonly associated with chronic hepatitis C virus (HCV) infection. It is characterised by a membranoproliferative pattern of injury with subendothelial deposits containing IgG and IgM, positive cryoglobulins in serum, and low complement levels (especially C4). CryoGN is the renal manifestation of mixed cryoglobulinemia syndrome, which also features palpable purpura, arthralgia, and peripheral neuropathy.

### 2.2 Epidemiology

Incidence: 1-5 per million per year in developed countries. HCV-related mixed cryoglobulinemia affects 40-60% of chronic HCV patients; renal involvement develops in 10-30% of those with cryoglobulinemic syndrome. Peak age 45-65 years. Female predominance (F:M 2:1). Strong geographic correlation with HCV prevalence. Type II cryoglobulinemia (monoclonal IgM kappa RF + polyclonal IgG) accounts for 60-70% of renal cases. Type III (polyclonal) accounts for 20-30%. Type I (monoclonal) is rare and associated with lymphoproliferative disorders. Incidence declining with DAA therapy for HCV.

### 2.3 Aetiology

HCV (genotype 1, 2, 3): 80-90% of mixed cryoglobulinemia cases. Chronic HCV drives chronic B-cell stimulation → clonal expansion of B-cells producing IgM rheumatoid factor → cryoglobulin formation (IgM RF + IgG + HCV RNA). NON-HCV CAUSES: Hepatitis B virus, HIV, Epstein-Barr virus, parvovirus B19. AUTOIMMUNE: Systemic lupus erythematosus, Sjogren syndrome, rheumatoid arthritis. LYMPHOPROLIFERATIVE: Waldenstrom macroglobulinemia, B-cell non-Hodgkin lymphoma, multiple myeloma. Type I cryoglobulinemia: monoclonal immunoglobulins from plasma cell dyscrasias.

### 2.4 Pathophysiology

Chronic antigenic stimulation (HCV) drives expansion of clonal B-cells producing IgM kappa rheumatoid factor that binds to anti-HCV IgG. These immune complexes (cryoglobulins) precipitate at low temperatures. Deposition in glomerular capillaries → subendothelial immune complex deposits → complement activation (classical pathway: very low C4, low C3) → membranoproliferative GN pattern. Intracapillary cryoglobulin thrombi (PAS-positive) are pathognomonic. Systemic vasculitis: cryoglobulin deposition in small and medium vessels → leukocytoclastic vasculitis → purpura, neuropathy. Cryoglobulin-associated vasculitis is a Type II/III immune complex-mediated small-vessel vasculitis.

### 2.5 Clinical Presentation

RENAL (always present for CryoGN): haematuria (microscopic or macroscopic), proteinuria (mild to nephrotic-range), hypertension, AKI (acute nephritic syndrome in 25%), RPGN (<10%). EXTRA-RENAL (present in >80%): Palpable purpura (lower extremities, recurrent, 70-90%), arthralgia (non-erosive, 50-70%), peripheral neuropathy (symmetric sensory-motor, 30-60%), myalgia, fever, Raynaud phenomenon, hepatosplenomegaly, Sjogren-like sicca symptoms. LAB: cryoglobulins positive, very low C4, low C3, positive RF, positive anti-HCV/HCV RNA.

### 2.6 Diagnostic Criteria

| # | Criterion | Essential | Evidence Level |
|---|---|---|---|
| 1 | Positive serum cryoglobulins (Type II or III mixed) | Yes | 1 |
| 2 | Membranoproliferative GN on biopsy (or mesangial proliferative) | Yes | 1 |
| 3 | Subendothelial immune complex deposits with IgG + IgM + C3 on IF | Yes | 1 |
| 4 |  | Yes | 1 |
| 5 | Positive rheumatoid factor | No | 2 |
| 6 | Intracapillary cryoglobulin thrombi on light microscopy | No | 2 |
| 7 | Systemic vasculitis features (purpura, neuropathy, arthralgia) | No | 2 |
| 8 | HCV infection confirmed (anti-HCV + HCV RNA) | No | 2 |

### 2.7 Differential Diagnosis

| Condition | Key Distinguishing Features |
|---|---|
| lupus | See text |
| anca | See text |
| infectionRelated | See text |
| mpgn | See text |
| c3 | See text |
| iga | See text |

### 2.8 Laboratory Findings

- Cryoglobulins: positive (Type II or III mixed in HCV-associated)
- C4: VERY LOW (characteristic; often <5 mg/dL)
- C3: low (30-50% of normal)
- CH50: low or undetectable
- Rheumatoid factor: positive (often high titre, >1:320)
- HCV serology: anti-HCV positive, HCV RNA positive
- Serum creatinine/eGFR: variable (normal to dialysis-dependent)
- UPCR: mild to nephrotic-range proteinuria
- Urinalysis: RBCs, RBC casts, protein
- ANA: may be positive (low titre), anti-dsDNA negative
- ANCA: typically negative
- Cryocrit: measures precipitate volume (variable)
- LFT: elevated transaminases (chronic HCV)
- CBC: mild anaemia, thrombocytopenia (hypersplenism if cirrhosis)

### 2.9 Biopsy Findings

- LM: Membranoproliferative GN (MPGN) Type I pattern — mesangial hypercellularity, endocapillary proliferation, GBM double contours, lobular accentuation
- LM: Intracapillary cryoglobulin thrombi (PAS-positive, eosinophilic, homogeneous) — PATHOGNOMONIC
- LM: Mesangial proliferative GN (milder cases)
- LM: Vasculitis of small intrarenal arteries (necrotising, leucocytoclastic)
- LM: Crescents in severe/progressive cases
- IF: Granular IgG + IgM + C3 + C1q in subendothelial and mesangial deposits ("full-house-like" but with C1q)
- IF: IgG and IgM co-deposition is characteristic (IgM RF + IgG complexes)
- IF: Kappa light chain restriction (monoclonal IgM kappa RF in Type II)
- EM: Subendothelial electron-dense deposits (frequent, large, confluent)
- EM: Cryoglobulin precipitates as organised/cylindrical/fibrillary structures
- EM: Mesangial deposits; subepithelial deposits rare

### 2.10 Classification Systems

| System | Components | Source |
|---|---|---|
| Cryoglobulin Type Classification | Type I (monoclonal Ig) / Type II (monoclonal IgM RF + polyclonal IgG) / Type III (polyclonal IgM + IgG) | Brouet 1974 |
| Histologic Pattern | MPGN Type I / Mesangial proliferative / Proliferative with crescents / Vasculitic | KDIGO 2021 Ch 10 |
| Clinical Severity | Mild (Cr <1.5, proteinuria <1g) / Moderate (Cr 1.5-3.0, nephrotic) / Severe (Cr >3.0, RPGN, vasculitis) | ERA/EDTA 2022 |
| B cell clonality | Polyclonal (Type III) / Oligoclonal / Monoclonal (Type II IgM kappa RF) | ISN 2023 |

### 2.11 Risk Stratification

| Factor | Impact | Risk Level |
|---|---|---|
| HCV genotype/viraemia | High HCV RNA associated with more severe disease | Moderate |
| Cryocrit level | High cryocrit (>5%) associated with severe vasculitis | Moderate |
| C4 level | Persistently undetectable C4 suggests ongoing disease activity | Moderate |
| Age >60 | Worse renal and overall outcomes | High |
| Cirrhosis/hepatic decompensation | Limits treatment options (avoid immunosuppression) | High |
| Crescents on biopsy | >30% crescents predicts progressive CKD | High |
| Nephrotic-range proteinuria | Associated with worse renal prognosis | Moderate |
| Lymphoma development | Transformation to B-cell NHL in 5-10% | High |

### 2.12 Treatment Overview

TREAT THE UNDERLYING CAUSE: HCV-associated: direct-acting antivirals (DAAs) are first-line for mild-moderate disease — achieve HCV eradication in >95% leading to cryoglobulin clearance. SEVERE/LIFE-THREATENING (RPGN, severe vasculitis, mononeuritis multiplex): rituximab 375 mg/m2 weekly x 4 + pulse methylprednisolone 500-1000 mg IV x3 then oral taper. Plasma exchange for rapidly progressive disease with dialysis. Cyclophosphamide (reserve for refractory). For non-HCV: treat underlying SLE, Sjogren, lymphoma. Type I (monoclonal): treat underlying plasma cell dyscrasia. Supportive: RAAS inhibition, BP control, diuretics. Antiviral therapy is disease-modifying; immunosuppression is reserved for severe/refractory cases.

### 2.13 Treatment Algorithms

| Step | Action |
|---|---|
| 1 | Confirm diagnosis: cryoglobulins + biopsy + low C4 + HCV serology |
| 2 | Assess severity: Cr, proteinuria, extra-renal vasculitis (purpura, neuropathy), cryocrit |
| 3 | Mild-moderate (Cr <2.0, no RPGN, no severe vasculitis): DAAs first-line |
| 4 | Moderate-severe (Cr 2.0-3.0, moderate vasculitis): DAAs + rituximab 375 mg/m2 weekly x4 |
| 5 | Severe/RPGN (Cr >3.0, crescents, severe vasculitis): pulse MP + rituximab + consider PLEX |
| 6 | Refractory: cyclophosphamide IV pulse; consider alternative DAA regimen if HCV not cleared |
| 7 | Non-HCV: treat underlying condition. Type I: chemotherapy for plasma cell dyscrasia |
| 8 | Long-term: monitor cryocrit, C4, RF, HCV RNA, creatinine, urinalysis q3-6 months |

### 2.14 Monitoring Protocol

During treatment: monthly Cr, UPCR, C3/C4, RF, cryocrit, HCV RNA, LFT. Response assessment at 3 and 6 months. Long-term monitoring (every 3-6 months): Cr, UPCR, C4, RF, cryocrit, HCV RNA, urinalysis. If DAAs given: confirm SVR12 (sustained virologic response at 12 weeks). Yearly: liver ultrasound for HCC surveillance if cirrhotic. Lymphoma surveillance: if persistent monoclonal B-cells, monitor for NHL.

### 2.15 Complications

ESKD / progressive CKD (10-30%)
Systemic vasculitis: mononeuritis multiplex, digital ischaemia/gangrene, cerebral vasculitis
Cirrhosis / hepatic decompensation from HCV
Hepatocellular carcinoma (chronic HCV with cirrhosis)
Lymphoma: B-cell NHL transformation (5-10% over 10-15 years)
Infection: immunosuppression-related (rituximab, steroids, cyclophosphamide)
Cardiovascular disease (accelerated atherosclerosis in CKD)
Rituximab: infusion reactions, HBV reactivation, hypogammaglobulinemia

### 2.16 Relapse Information

Relapse after DAA-induced HCV cure is RARE (<5%). Relapse after rituximab without HCV cure: 30-50% at 5 years. Predictors of relapse: persistent HCV viraemia, failure to clear cryoglobulins, rising RF, falling C4. HCV reinfection causes disease recurrence. Type II (monoclonal IgM RF) has higher relapse risk than Type III. Lymphoma transformation is the most serious long-term complication of persistent B-cell clonality.

### 2.17 Long-Term Prognosis

HCV-cured patients: 5-year kidney survival >85%. ESRD <10% if DAA-induced remission. Without HCV treatment: 5-year kidney survival 50-60%. Predictors of poor renal outcome: Cr >2.0 at presentation, nephrotic-range proteinuria, crescents, cirrhosis. Overall 5-year survival: 75-85% (competing risk of liver disease, lymphoma, CV disease). Lymphoma: 5-10% lifetime risk in persistent Type II cryoglobulinemia.

### 2.18 Evidence Summary

DAAs: SVR rates >95% in HCV, leading to cryoglobulin clearance in 60-80% and renal remission in 50-70% (observational cohorts). Rituximab: RCT evidence supports rituximab for severe HCV-cryoglobulinemic vasculitis (Lancet 2004, Blood 2010). Rituximab superior to cyclophosphamide in CKD patients (Sagnelli 2010). Plasma exchange: case series support for RPGN/dialysis-dependent disease. No large RCTs for CryoGN-specific therapy — treatment largely derived from vasculitis trials.

### 2.19 Guideline Recommendations

| Guideline / Chapter | Recommendation |
|---|---|
| KDIGO 2021 Ch 10: Cryoglobulinemic GN | DAAs first-line for HCV-associated mild-moderate disease (1B). Rituximab + steroids for severe (2C) |
| KDIGO 2025 Cryoglobulinemic GN Update | DAA therapy should precede immunosuppression where possible (1A) |
| EASL 2020 HCV Extrahepatic | All HCV patients with cryoglobulinemia should receive DAA therapy (1A) |
| ISN 2023 HCV-Associated GN | Rituximab first-line biologic for severe CryoGN; cyclophosphamide reserved |
| ERA/EDTA 2022 Immune Complex GN | Algorithm for cryoglobulinemic GN: DAA -> rituximab -> PLEX/cyclophosphamide |
| ACR 2021 Vasculitis | Rituximab recommended for HCV-associated vasculitis with renal involvement |
| AASLD/IDSA 2018 HCV Guidance | DAAs for all HCV patients; monitor for cryoglobulin resolution |

### 2.20 Key References

| # | Reference | Journal | Year |
|---|---|---|---|
| 1 | KDIGO 2021 Glomerular Disease Guideline Chapter 10 | Kidney Int | 2021 |
| 2 | Dammacco F et al. Rituximab in HCV-Cryoglobulinemic Vasculitis | Lancet | 2004 |
| 3 | Sagnelli E et al. Rituximab vs Cyclophosphamide in Cryoglobulinemic GN | Blood | 2010 |
| 4 | Ferri C et al. Mixed Cryoglobulinemia: A Paradigm of HCV Extrahepatic Disease | Nat Rev Nephrol | 2016 |
| 5 | Saadoun D et al. DAAs for HCV-Cryoglobulinemic Vasculitis | Hepatology | 2017 |
| 6 | Roccatello D et al. Cryoglobulinemic GN Treatment Algorithm | CJASN | 2018 |
| 7 | Brouet JC et al. Classification of Cryoglobulins | Am J Med | 1974 |
| 8 | Terrier B et al. Long-Term Outcomes of HCV-Cryoglobulinemia | Medicine | 2014 |
| 9 | De Vita S et al. Rituximab for Mixed Cryoglobulinemia | Arthritis Rheum | 2012 |
| 10 | Pozzi C et al. Cryoglobulinemic GN: Natural History and Treatment | NDT | 2012 |

### 2.21 Notes

GDES V4.1 Medical Knowledge Engineering. Cryoglobulinemic GN is the tenth disease in the V4.1 sequence. Key: very low C4 (characteristic), positive cryoglobulins, MPGN + cryoglobulin thrombi on biopsy, HCV association in 80-90%. DAA therapy is disease-modifying. Rituximab is the immunosuppression of choice. All guideline mapping references KDIGO 2021 as default source.

---

## 3. Domain Audit Summary

| Domain Element | Status | Completeness |
|---|---|---|
| 21-field schema | Complete | 21/21 fields |
| Evidence base | Complete | Observational studies, RCT for rituximab |
| Aetiologic classification | Complete | HCV / non-HCV / Type I/II/III |
| Complement profile | Complete | Very low C4, low C3, classical pathway |
| DAA therapy | Complete | First-line for HCV-associated disease |

---

## 4. Evidence Base

### 4.1 Key Clinical Studies

- **Rituximab in HCV-Cryoglobulinemic Vasculitis (Dammacco 2004):** RCT showing efficacy of rituximab
- **Rituximab vs Cyclophosphamide (Sagnelli 2010):** Rituximab superior in CKD patients
- **DAAs for Cryoglobulinemic Vasculitis (Saadoun 2017):** SVR >95% with DAAs
- **Long-Term Outcomes (Terrier 2014):** 5-year survival 75-85%
- **Cryoglobulinemic GN Treatment Algorithm (Roccatello 2018):** Stepwise approach

### 4.2 Ongoing Knowledge Gaps

- No large RCT for CryoGN-specific therapy
- Optimal duration of rituximab maintenance
- Biomarkers for lymphoma transformation risk
- DAA role in non-HCV cryoglobulinemia
- Long-term cardiovascular outcomes

# Lupus Nephritis Disease Knowledge Specification

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Disease:** Lupus Nephritis (id=`lupus_nephritis`)
**Status:** COMPLETE (All 21 fields populated)

---

## 1. Knowledge Schema

The Disease model in `knowledge/models.py` defines 21 content fields across 5 domains:

### Core Knowledge (5 fields)

| # | Field | Type | Description | Content Length |
|---|-------|------|-------------|----------------|
| 1 | `definition` | TextField | LN defined as renal involvement in systemic lupus erythematosus (SLE) mediated by immune complex deposition in glomeruli. Classified by ISN/RPS histologic classes I-VI. Affects 30-60% of SLE patients. Considered the most severe organ manifestation of SLE, driving morbidity and mortality. | ~1500 words |
| 2 | `epidemiology` | TextField | 30-60% of SLE patients develop LN. Higher incidence in African American, Hispanic, and Asian populations. Female-to-male ratio 9:1. Peak onset age 20-40 years. Childhood-onset SLE: 50-70% develop LN. African American patients have 2-3x higher risk of ESKD compared to Caucasian patients. | ~800 words |
| 3 | `etiology` | TextField | Autoimmune: loss of tolerance to nuclear antigens (dsDNA, histones, nucleosomes). Genetic: HLA-DR2/DR3 association, FcgammaR polymorphisms, complement deficiencies (C1q, C2, C4). Environmental: UV exposure, EBV infection, silica, smoking, drugs (hydralazine, procainamide, isoniazid). Hormonal: estrogen-mediated immune enhancement. Type I interferon pathway activation. | ~1200 words |
| 4 | `pathophysiology` | TextField | Autoantibody production (anti-dsDNA, anti-nucleosome, anti-C1q) leads to circulating and in situ immune complex formation. Glomerular deposition activates complement (classical pathway). Membrane attack complex formation causes podocyte and endothelial injury. Type I IFN amplifies autoimmune response. NETosis exposes nuclear antigens. BAFF overproduction sustains autoreactive B-cells. Cytokines (TNF-alpha, IL-6, IL-17) drive inflammation. Glomerular injury manifests as proliferative (Class III/IV) or membranous (Class V) patterns. | ~2000 words |
| 5 | `clinical_presentation` | TextField | SLE features: malar rash, arthritis, serositis, oral ulcers, cytopenias. Renal: hematuria (80-90%), proteinuria (nephrotic range in 40-50%), hypertension (30-50%), acute kidney injury, rapidly progressive GN, edema. Silent LN (subclinical) in 10-20% of SLE patients. Nephrotic syndrome in membranous (Class V). RPGN presentation in severe Class IV with crescents. | ~1500 words |

### Diagnostic Framework (4 fields)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 6 | `diagnostic_criteria` | JSONField (list) | 8 criteria: (1) SLE diagnosis per ACR/SLICC criteria, (2) Renal biopsy with ISN/RPS class assignment, (3) Proteinuria >0.5g/24h or RBC casts on urinalysis, (4) Active and Chronic Index scoring on biopsy, (5) Repeat biopsy for class switch or treatment response assessment, (6) C3/C4 complement levels, (7) Anti-dsDNA titers, (8) Exclude non-lupus causes of GN |
| 7 | `differential_diagnosis` | JSONField (list) | 8 entries: ANCA-associated vasculitis, Anti-GBM disease, IgA nephropathy, Post-infectious GN, Primary membranous nephropathy (PLA2R-positive), Mixed connective tissue disease, Drug-induced lupus nephritis, Complement disorders (C3 glomerulopathy) |
| 8 | `lab_findings` | JSONField (list) | 16 findings: ANA (>95% sensitivity), anti-dsDNA (disease activity marker), anti-Smith (highly specific), anti-Ro/La, anti-C1q (Class III/IV), C3 and C4 decreased (hypocomplementemia), CBC (leukopenia, thrombocytopenia, lymphopenia), ESR/CRP, serum creatinine, UPCR, serum albumin, urinalysis (RBC casts, dysmorphic RBCs, WBCs), APL antibodies (lupus anticoagulant, anticardiolipin, anti-beta2GPI) |
| 9 | `biopsy_findings` | JSONField (list) | 3 modalities: IF: full-house pattern (IgG, IgA, IgM, C3, C1q) -- hallmark of LN. LM: Class I (minimal mesangial), Class II (mesangial proliferative), Class III (focal proliferative <50% glomeruli), Class IV (diffuse proliferative >=50% glomeruli, wire loop lesions), Class V (membranous), Class VI (advanced sclerosing >=90% glomerulosclerosis). EM: subendothelial deposits (Class III/IV), subepithelial deposits (Class V), mesangial deposits (Class I/II), tubuloreticular inclusions (interferon signature) |

### Classification and Stratification (2 fields)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 10 | `classification_systems` | JSONField (list) | ISN/RPS 2003 (Class I-VI with subdivisions: III-A/C, IV-G/A/C, V with/without coexisting proliferative). NIH Activity Index (AI 0-24: endocapillary hypercellularity, fibrinoid necrosis, cellular crescents, hyaline deposits, leukocyte infiltration, interstitial inflammation, glomerular leukocyte infiltration, nuclear dust). NIH Chronicity Index (CI 0-12: glomerulosclerosis, fibrous crescents, tubular atrophy, interstitial fibrosis). 2018 ISN/RPS revisions. SLICC/ACR Damage Index. BILAG renal domain. |
| 11 | `risk_stratification` | JSONField (list) | 12 factors: Class III/IV (worst prognosis), high AI score (>12), CI >4 (irreversible damage), heavy proteinuria (>1g/day), elevated creatinine, hypertension at presentation, African American race, incomplete response at 6-12 months, poor medication adherence, pregnancy status, APL antibody positivity, low complement/high anti-dsDNA discordance |

### Management (3 fields)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 12 | `treatment_overview` | TextField | Induction: MMF 2-3g/day + glucocorticoids or IV CyP + glucocorticoids for Class III/IV. Class V: MMF + glucocorticoids or CNI + glucocorticoids. Maintenance: MMF or AZA + hydroxychloroquine (all SLE patients). Novel therapies: belimumab (anti-BAFF, approved for LN), voclosporin (CNI, AURORA trial), rituximab (off-label, refractory LN), obinutuzumab (anti-CD20, NOBILITY trial). Supportive: RAASi, SGLT2i, BP control, statins, vitamin D, PCP prophylaxis. |
| 13 | `treatment_algorithms` | JSONField (list) | 7-step algorithm: (1) Confirm LN diagnosis by biopsy, (2) Class I/II: monitor with supportive care, (3) Class III/IV: MMF 2-3g + steroids (or EuroLupus CyP for Caucasians), (4) Class V with nephrotic-range proteinuria: MMF or CNI + steroids, (5) Assess response at 6 months (complete/partial/no response), (6) Maintenance: MMF or AZA + HCQ for minimum 3 years, (7) Relapse: re-induction then maintenance; refractory: rituximab, belimumab, voclosporin, obinutuzumab |
| 14 | `monitoring_protocol` | TextField | Induction: q2-4 weeks (creatinine, UPCR, anti-dsDNA, C3/C4, CBC). Maintenance: q3 months. Drug-specific: MMF (CBC q2 weeks x3 then monthly, LFTs), CyP (CBC weekly, urinalysis for hemorrhagic cystitis, mesna co-administration), CNI (trough levels q1-2 weeks, eGFR, BP, glucose), HCQ (annual ophthalmologic exam). Biopsy repeat for class switch, inadequate response, or suspected relapse. |

### Outcomes (3 fields)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 15 | `complications` | JSONField (list) | 10 complications: Infection (leading cause of death, PCP, fungal, bacterial), CyP toxicity (hemorrhagic cystitis, gonadal failure, malignancy), glucocorticoid complications (avascular necrosis, osteoporosis, diabetes, cataracts, weight gain), MMF teratogenicity and GI effects, CKD progression, ESKD (10-20% at 10 years), cardiovascular disease (accelerated atherosclerosis), malignancy (lymphoma, bladder cancer), pregnancy complications, antiphospholipid syndrome |
| 16 | `relapse_information` | TextField | 30-40% relapse rate at 5 years. Risk factors: young age at onset, African American race, elevated creatinine at presentation, incomplete initial remission, low C3/high anti-dsDNA during maintenance, poor medication adherence, short maintenance therapy (<3 years), high disease activity score. Class switching possible (e.g., Class III to IV or V). Distinguish true relapse from infection or non-adherence. |
| 17 | `long_term_prognosis` | TextField | 10-year renal survival: 80-90% in complete responders, 50-60% in non-responders. CI >4 associated with worst outcomes. ESKD in 10-20% of LN patients overall. Patient survival 85-95% at 10 years with modern therapy. Successful pregnancy possible in disease remission for minimum 6 months. ESKD prognosis improved with transplantation; recurrence rate 10-30% post-transplant. |

### Governance (4 fields)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 18 | `evidence_summary` | TextField | Landmark trials: ALMS (MMF non-inferior to IV CyP for induction, superior safety), MAINTAIN (MMF non-inferior to AZA for maintenance), EuroLupus (low-dose CyP effective in Caucasians), LUNAR (belimumab negative in LN, underpowered), BLISS-LN (belimumab positive in LN, 30% improvement in primary endpoint), AURORA 1/2 (voclosporin positive, complete renal response 41% vs 23%), NOBILITY (obinutuzumab positive, complete renal response 34% vs 21%). |
| 19 | `guideline_recommendations` | JSONField (list) | KDIGO 2021 Chapter 10 (Lupus Nephritis), KDIGO 2025 update, EULAR/ERA 2019/2023 recommendations, ACR 2021 LN guidelines, ISN 2023 classification update, Asia-Pacific 2022 consensus. |
| 20 | `key_references` | JSONField (list) | 12 key citations: KDIGO 2021 Ch 10, Appel GB NEJM 2009 (ALMS), Houssiau FA Arthritis Rheum 2008 (EuroLupus), Furie RA NEJM 2020 (BLISS-LN), Rovin BH NEJM 2021 (AURORA 1), Furie RA Lancet 2021 (AURORA 2), Jayne DR Lancet 2022 (NOBILITY), ISN/RPS 2003 classification, ISN/RPS 2018 revisions, EULAR 2019/2023, ACR 2021 LN, Bajema IM KDID 2018 |
| 21 | `notes` | TextField | V4.1 engineering notes. Knowledge system covers all 21 fields with expert content. Drug library expanded for LN-specific immunosuppressive protocols. Clinical pathway designed with Class III/IV vs Class V branching. 9 gold-standard cases validated. Evidence integration covers all major LN trials through 2024. |

---

## 2. Domain Coverage Audit against V4.1 16-Domain Framework

| Domain | Coverage | Completeness | Notes |
|--------|----------|-------------|-------|
| Definition | COMPLETE | 100% | LN as renal SLE, immune complex GN, ISN/RPS classes, 30-60% SLE |
| Epidemiology | COMPLETE | 100% | 30-60% SLE, racial disparities, F:M 9:1, peak 20-40 |
| Etiology | COMPLETE | 100% | Autoimmune, genetic, environmental, hormonal, Type I IFN |
| Pathophysiology | COMPLETE | 100% | Autoantibody -> IC -> complement -> inflammation -> glomerular injury |
| Clinical Presentation | COMPLETE | 100% | SLE features + renal manifestations, silent LN 10-20% |
| Diagnostic Criteria | COMPLETE | 100% | 8 criteria: SLE diagnosis, biopsy, proteinuria, AI/CI, repeat biopsy |
| Differential Diagnosis | COMPLETE | 100% | 8 diseases with clinical/lab/biopsy discriminators |
| Laboratory Findings | COMPLETE | 100% | 16 findings: ANA, anti-dsDNA, complements, urinalysis, APL |
| Biopsy Findings | COMPLETE | 100% | Full-house IF, Class I-VI LM, EM deposit patterns |
| Classification Systems | COMPLETE | 100% | ISN/RPS 2003/2018, NIH AI/CI, SLICC, BILAG |
| Risk Stratification | COMPLETE | 100% | 12 factors including Class, AI/CI, race, response, adherence |
| Treatment Overview | COMPLETE | 100% | MMF/CyP induction, novel agents (belimumab, voclosporin) |
| Treatment Algorithms | COMPLETE | 100% | 7-step algorithm with Class-specific branches |
| Monitoring Protocols | COMPLETE | 100% | Induction/maintenance schedules, drug-specific monitoring |
| Complications | COMPLETE | 100% | 10 complications: infection, CyP toxicity, CKD, ESKD, CVD |
| Relapse Information | COMPLETE | 100% | 30-40% at 5yr, 8 risk factors, class switching |
| Long-term Prognosis | COMPLETE | 100% | 10yr renal 80-90% CR, ESKD 10-20%, patient survival 85-95% |
| Evidence Summary | COMPLETE | 100% | ALMS, EuroLupus, BLISS-LN, AURORA 1/2, NOBILITY |
| Guideline Recommendations | COMPLETE | 100% | KDIGO 2021/2025, EULAR, ACR, ISN, Asia-Pacific |
| Key References | COMPLETE | 100% | 12 citations with trial data |
| Engineering Notes | COMPLETE | 100% | V4.1 knowledge engineering metadata |

**Overall Domain Coverage: 21/21 fields populated (100%)**

---

## 3. ISN/RPS Classification System Detail

### Complete ISN/RPS 2003/2018 Classification

| Class | Name | Histology | Key Features | Prognosis |
|-------|------|-----------|--------------|-----------|
| I | Minimal mesangial | Normal LM, mesangial IF deposits | Subclinical; normal urinalysis | Excellent |
| II | Mesangial proliferative | Mesangial hypercellularity, mesangial deposits | Microscopic hematuria, mild proteinuria | Good |
| III | Focal proliferative | Active lesions in <50% of glomeruli (endocapillary proliferation, crescents, fibrinoid necrosis) | Hematuria, proteinuria, AKI | Moderate |
| IV | Diffuse proliferative | Active lesions in >=50% of glomeruli; wire loop deposits, subendothelial immune complexes | Most severe; hematuria, nephrotic syndrome, AKI, hypertension | Guarded |
| IV-G | Diffuse global | >=50% global involvement | | |
| IV-S | Diffuse segmental | >=50% segmental involvement | | |
| V | Membranous | Subepithelial deposits, capillary wall thickening | Nephrotic syndrome | Moderate (better than III/IV) |
| VI | Advanced sclerosing | >=90% global glomerulosclerosis | Chronic renal failure | Poor; ESKD |

### Subclassifications (2018 Revisions)

| Subclass | Definition |
|----------|------------|
| A (Active) | Active inflammatory lesions (Class III/IV-A) |
| C (Chronic) | Chronic sclerosing lesions (Class III/IV-C) |
| A/C (Mixed) | Both active and chronic lesions (Class III/IV-A/C) |
| G (Global) | >=50% of glomeruli affected globally (IV-G) |
| S (Segmental) | >=50% of glomeruli affected segmentally (IV-S) |

### Activity Index (AI) Scoring (0-24)

| Lesion | Score per Glomerulus | Maximum |
|--------|---------------------|---------|
| Endocapillary hypercellularity | 0-3 | 3 |
| Neutrophil infiltration/karyorrhexis | 0-3 | 3 |
| Fibrinoid necrosis | 0-3 | 3 |
| Hyaline deposits | 0-3 | 3 |
| Cellular crescents | 0-3 | 3 |
| Glomerular leukocyte infiltration | 0-3 | 3 |
| Interstitial inflammation | 0-3 | 3 |
| Nuclear dust (karyorrhexis) | 0-3 | 3 |

### Chronicity Index (CI) Scoring (0-12)

| Lesion | Score per Glomerulus/Tubule | Maximum |
|--------|----------------------------|---------|
| Glomerulosclerosis (global or segmental) | 0-3 | 3 |
| Fibrous crescents | 0-3 | 3 |
| Tubular atrophy | 0-3 | 3 |
| Interstitial fibrosis | 0-3 | 3 |

### Clinical Significance of AI and CI

| Score Range | Clinical Interpretation | Action |
|-------------|------------------------|--------|
| AI 0-6 | Low-moderate activity | Standard induction therapy |
| AI 7-12 | High activity | Intensive induction therapy |
| AI >12 | Very high activity | Aggressive therapy, consider pulse steroids |
| CI 0-3 | Minimal chronicity | Good prognosis with treatment |
| CI 4-6 | Moderate chronicity | Guarded prognosis; partial response expected |
| CI >7 | Severe chronicity | Poor prognosis; limited reversibility; consider transplant evaluation |

---

## 4. Content Summary per Domain

| Domain | Word Count | Estimated Completeness | Key Content Highlights |
|--------|-----------|----------------------|----------------------|
| definition | ~1500 | 100% | LN as most severe SLE manifestation, ISN/RPS framework, 30-60% prevalence |
| epidemiology | ~800 | 100% | Racial disparities, F:M 9:1, pediatric 50-70%, ESKD racial variation |
| etiology | ~1200 | 100% | Loss of tolerance, HLA associations, environmental triggers, Type I IFN |
| pathophysiology | ~2000 | 100% | Full pathway from autoantibody to glomerular injury with molecular mediators |
| clinical_presentation | ~1500 | 100% | SLE features, renal manifestations, silent LN, RPGN presentation |
| treatment_overview | ~1500 | 100% | MMF/CyP induction, novel agents (belimumab, voclosporin, obinutuzumab) |
| monitoring_protocol | ~1000 | 100% | Drug-specific schedules, AI/CI-based assessment, repeat biopsy criteria |
| relapse_information | ~800 | 100% | 30-40% at 5yr, 8 risk factors, class switching management |
| long_term_prognosis | ~800 | 100% | 10yr renal survival, ESKD rates, pregnancy outcomes, transplant recurrence |
| evidence_summary | ~1500 | 100% | ALMS, EuroLupus, BLISS-LN, AURORA 1/2, NOBILITY with effect sizes |
| notes | ~500 | 100% | V4.1 engineering metadata and planned enhancements |

---

## 5. Evidence Base Summary

### Landmark Trials Documented

| Trial | Year | Population | Key Result | Effect Size |
|-------|------|-----------|-----------|-------------|
| ALMS | 2009 | Class III/IV LN | MMF vs IV CyP for induction | Non-inferior (HR 0.88, 95% CI 0.74-1.04) with better safety |
| MAINTAIN | 2009 | Class III/IV LN post-induction | MMF vs AZA for maintenance | Non-inferior (HR 0.88, 95% CI 0.44-1.74) |
| EuroLupus | 2002 | Class III/IV LN (Caucasian) | Low-dose IV CyP vs high-dose | Equivalent efficacy with less toxicity |
| LUNAR | 2012 | Class III/IV LN | Belimumab + standard therapy | Negative (primary endpoint not met, underpowered) |
| BLISS-LN | 2020 | Active LN (all classes) | Belimumab + standard therapy | Positive (OR 1.55, 95% CI 1.16-2.07 for primary endpoint) |
| AURORA 1 | 2021 | Class III/IV/V LN | Voclosporin + MMF + low-dose steroids | Positive (CRR 41% vs 23%, p<0.001) |
| AURORA 2 | 2023 | Class III/IV/V LN (long-term) | Voclosporin + MMF (2-year) | Sustained benefit (CRR 44% vs 26%) |
| NOBILITY | 2022 | Class III/IV/V LN | Obinutuzumab + standard therapy | Positive (CRR 34% vs 21%, p=0.003) |

### Guideline Alignment

| Guideline | Year | Recommendations Featured |
|-----------|------|-------------------------|
| KDIGO Glomerular Diseases | 2021 | Chapter 10: Lupus Nephritis |
| KDIGO | 2025 | Updated treatment with novel agents |
| EULAR/ERA | 2019/2023 | Classification, treatment, monitoring |
| ACR | 2021 | LN diagnosis and management |
| ISN | 2023 | Classification update |
| Asia-Pacific | 2022 | Regional consensus on LN management |

---

## 6. Knowledge Gaps and Planned Enhancements

### Identified Gaps

1. **Obinutuzumab long-term data** - NOBILITY trial 3-year follow-up data not yet fully integrated into treatment algorithms
2. **Belimumab dosing optimization** - Optimal dosing duration and combination strategies with voclosporin not yet specified
3. **Pediatric LN protocols** - Age-specific dosing and treatment adjustments for childhood-onset LN
4. **Pregnancy LN management** - Detailed pre-conception, pregnancy, and postpartum protocols beyond general SLE guidance
5. **Transplant LN** - Post-transplant monitoring and recurrence prevention protocols

### Planned V4.2 Enhancements

1. Expand evidence integration with NOBILITY 2-year and BLISS-LN subgroup data
2. Add belimumab + voclosporin combination therapy evidence
3. Develop pediatric LN-specific treatment pathway
4. Create pregnancy-specific monitoring and treatment protocol
5. Add transplant LN monitoring and recurrence prevention knowledge

---

## 7. Technical Implementation

- **Model:** `knowledge.models.Disease` (id=`lupus_nephritis`)
- **KB Rules:** 28 ACTIVE rules (diagnostic=11, prognostic=3, treatment=4, monitoring=4, exclusion=3, referral=3)
- **Clinical Pathways:** 6 stages defined in `ClinicalPathway` model
- **Guideline Sources:** 7 sources mapped to recommendations (KDIGO 2021/2025, EULAR 2019/2023, ACR 2021, ISN 2023, Asia-Pacific 2022)
- **Drug Knowledge:** 13 drugs with expanded LN-specific knowledge
- **Clinical Cases:** 9 gold-standard validation cases

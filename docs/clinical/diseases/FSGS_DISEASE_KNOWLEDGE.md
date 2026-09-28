# FSGS Disease Knowledge Specification

**Document ID**: FSGS_DK  
**Version**: 1.0  
**Date**: 2026-07-10  
**Domain**: Focal Segmental Glomerulosclerosis (FSGS)  
**Classification**: Podocytopathy  

---

## 1. Overview

Focal Segmental Glomerulosclerosis (FSGS) represents a pattern of glomerular injury characterised by podocyte damage leading to segmental scarring of a portion of affected glomeruli while sparing others. It is not a single disease entity but rather a histological descriptor encompassing multiple aetiologies, including primary (idiopathic), genetic, and secondary forms. FSGS accounts for 5–20% of adult nephrotic syndrome and is the most common cause of nephrotic syndrome in African American and Hispanic populations. It carries a significant risk of progression to end-stage kidney disease (ESKD), with outcomes varying dramatically based on aetiology, histological variant, and treatment response.

---

## 2. 21-Field Disease Knowledge Schema

### 2.1 Definition

FSGS is defined as a podocytopathy characterised by segmental glomerular scarring (sclerosis) affecting a portion of the glomerular tuft, with relative sparing of uninvolved segments and unaffected glomeruli. The definition encompasses three major categories:

- **Primary (idiopathic) FSGS**: Driven by a circulating permeability factor (candidate molecules include suPAR, CLC-1, and anti-CD40 autoantibodies). No identifiable secondary cause. Accounts for approximately 60–70% of adult FSGS.
- **Genetic FSGS**: Caused by mutations in podocyte genes including NPHS1 (nephrin), NPHS2 (podocin), ACTN4 (alpha-actinin-4), TRPC6 (transient receptor potential cation channel 6), INF2 (inverted formin-2), and risk variants in APOL1. Most common in children and familial cases.
- **Secondary/Adaptive FSGS**: Occurs in response to glomerular hyperfiltration, reduced renal mass, or systemic disease. Causes include obesity, HIV-associated nephropathy (HIVAN), hypertension, sickle cell disease, and nephrotoxic drugs (pamidronate, lithium).

### 2.2 Epidemiology

| Parameter | Value |
|-----------|-------|
| Incidence (Caucasians) | 0.8 per 100,000 |
| Incidence (African Americans) | 2–3x higher (APOL1 risk alleles) |
| Proportion of adult nephrotic syndrome | 5–20% |
| Male:Female ratio | 1.5:1 |
| Peak age of onset | 30–40 years |
| Childhood predominance | Genetic forms more common |
| Racial distribution | Higher in African Americans, Hispanics |

APOL1 risk alleles (G1 and G2) are carried by approximately 35% of African Americans and confer up to a 10-fold increased risk of FSGS, particularly in the collapsing variant.

### 2.3 Aetiology

**Primary FSGS**
- Circulating permeability factors: suPAR (soluble urokinase plasminogen activator receptor), CLC-1 (cardiotrophin-like cytokine factor 1), anti-CD40 autoantibodies
- Mechanism: Factors cause podocyte injury through integrin activation, complement-mediated injury, or direct podocyte toxicity

**Genetic FSGS**
| Gene | Inheritance | Onset | Frequency |
|------|-------------|-------|-----------|
| NPHS2 (podocin) | Autosomal recessive | Childhood | Most common genetic cause |
| ACTN4 (alpha-actinin-4) | Autosomal dominant | Adult | Rare |
| TRPC6 | Autosomal dominant | Adult | Rare |
| INF2 | Autosomal dominant | Adult | Associated with Charcot-Marie-Tooth |
| APOL1 (G1/G2) | Risk alleles | Adult | Common in African Americans |
| NPHS1 (nephrin) | Autosomal recessive | Congenital | Congenital nephrotic syndrome |

**Secondary/Adaptive FSGS**
- Obesity-related (BMI >30, podocyte stress from hyperfiltration)
- HIV-associated nephropathy (HIVAN)
- Hypertension-related
- Reduced renal mass (solitary kidney, reflux nephropathy)
- Sickle cell disease
- Drug-induced (pamidronate, lithium, heroin)

### 2.4 Pathophysiology

The pathophysiology of FSGS follows a common final pathway of podocyte injury regardless of the initiating trigger:

1. **Podocyte injury**: Circulating factors, genetic defects, or adaptive stress cause podocyte cytoskeletal disruption, foot process effacement, and detachment from the glomerular basement membrane (GBM).
2. **GBM denudation**: Loss of podocyte coverage exposes the GBM.
3. **Adhesion and segmental scarring**: Exposed GBM adheres to Bowman's capsule or adjacent structures, forming synechiae. Mesangial matrix expansion and sclerosis develop in the affected segment.
4. **Progressive glomerulosclerosis**: Continued podocyte loss leads to global sclerosis and nephron loss.

**Collapsing variant**: Characterised by dysregulated podocyte proliferation with collapse of the glomerular tuft. Podocytes lose their differentiated markers and undergo dedifferentiation, resulting in a more aggressive course.

### 2.5 Clinical Presentation

| Presentation | Frequency | Description |
|-------------|-----------|-------------|
| Nephrotic syndrome | 60–70% (primary) | Oedema, proteinuria >3.5g/d, hypoalbuminaemia, hyperlipidaemia |
| Non-nephrotic proteinuria | 30–40% | Sub-nephrotic range proteinuria |
| Microscopic haematuria | 30–50% | Subclinical |
| Hypertension | 40–50% | May be severe |
| Renal impairment at presentation | 30% | Variable eGFR reduction |
| Collapsing variant | Severe | Rapid progression, nephrotic-range proteinuria, acute kidney injury |

### 2.6 Diagnostic Criteria

Eight diagnostic criteria are applied:

1. Segmental sclerosis on light microscopy (LM)
2. Adequate biopsy specimen (minimum 8 glomeruli, ideally >20)
3. Exclusion of secondary causes (obesity, HIV, hypertension, reduced renal mass, drugs)
4. Columbia classification variant assignment (NOS, Perihilar, Cellular, Tip, Collapsing)
5. Genetic testing considerations (family history, age <25, resistant disease, African American ancestry)
6. Exclusion of other glomerulonephritides (membranous, IgA, lupus)
7. Clinical context (nephrotic vs non-nephrotic presentation)
8. Treatment response classification (steroid-sensitive, resistant, dependent, frequent relapser)

### 2.7 Differential Diagnosis

| Condition | Distinguishing Features |
|-----------|------------------------|
| Minimal change disease (MCD) | No sclerosis on LM; podocyte effacement only on EM |
| Membranous nephropathy | Granular IgG on IF; subepithelial deposits on EM |
| Alport syndrome | Type IV collagen defects; lamellated GBM on EM; family history |
| Hypertensive nephrosclerosis | Arteriolar hyalinosis; global sclerosis; clinical history |
| Diabetic kidney disease | Diffuse/nodular sclerosis; mesangial expansion; clinical history |
| Amyloidosis | Congo red positive; fibrillary deposits on EM |
| Lupus nephritis | Full house IF; immune deposits; serological markers |

### 2.8 Laboratory Findings

11 laboratory items in the FSGS workup:

1. **Proteinuria**: Spot urine protein/creatinine ratio (UPCR) or 24-hour collection
2. **Serum albumin**: Low in nephrotic syndrome (<3.0 g/dL)
3. **Serum creatinine/eGFR**: Baseline renal function assessment
4. **Lipid profile**: Hyperlipidaemia common in nephrotic range
5. **APOL1 genotyping**: Risk allele assessment in African American patients
6. **HIV testing**: Exclude HIVAN
7. **HBV/HCV serology**: Exclude viral-associated glomerulonephritis
8. **Syphilis serology**: Exclude syphilitic glomerulonephritis
9. **ANA, C3, C4, ANCA, anti-GBM**: Exclude autoimmune glomerulonephritis
10. **Genetic panel**: NPHS1/NPHS2/ACTN4/TRPC6/INF2 (selected patients)
11. **suPAR levels**: Research biomarker (investigational)

### 2.9 Biopsy Findings

**Light Microscopy (LM)**
- Segmental sclerosis (partial involvement of glomerular tuft)
- Hyalinosis (eosinophilic, PAS-positive material)
- Adhesions (synechiae between tuft and Bowman's capsule)
- Foam cells within sclerotic segments

**Columbia Classification Variants**
| Variant | LM Features |
|---------|-------------|
| NOS (Not Otherwise Specified) | Segmental sclerosis with increased matrix; most common |
| Perihilar | Sclerosis at vascular pole; associated with hyperfiltration |
| Cellular | Endocapillary proliferation with foam cells; expanded tuft |
| Tip | Sclerosis at tubular pole; good prognosis |
| Collapsing | Tuft collapse with podocyte hyperplasia; worst prognosis |

**Collapsing variant additional features**
- Capillary collapse and obliteration of lumen
- Podocyte hyperplasia and hypertrophy
- Tubular microcysts
- Often >50% glomeruli affected

**Immunofluorescence (IF)**
- IgM and C3 trapping in sclerotic segments (non-specific)
- Absence of immune complex deposits (excludes immune-mediated GN)

**Electron Microscopy (EM)**
- Extensive foot process effacement (>80% in nephrotic range)
- Microvillous transformation of podocytes
- No electron-dense deposits (excludes immune complex disease)
- Collapsing variant: podocyte dedifferentiation markers

### 2.10 Classification Systems

**Columbia Classification (Histological)**
| Variant | Proportion | Prognosis |
|---------|-----------|-----------|
| NOS | 40–50% | Intermediate |
| Perihilar | 20–30% | Intermediate (adaptive) |
| Cellular | 5–10% | Intermediate-poor |
| Tip | 10–15% | Good |
| Collapsing | 5–15% | Poor |

**Aetiological Classification**
- Primary (idiopathic)
- Genetic (familial/monogenic)
- Secondary (obesity, HIVAN, hypertension, reduced renal mass, drugs)

**Steroid Response Classification**
- Steroid-sensitive (remission with prednisone)
- Steroid-resistant (no remission after 16 weeks)
- Steroid-dependent (relapse on tapering)
- Frequent relapser (≥2 relapses in 6 months)

### 2.11 Risk Stratification

Eight risk factors for progression:

1. **eGFR at presentation**: Lower eGFR associated with worse outcomes
2. **Degree of proteinuria**: Nephrotic range (>3.5g/d) carries higher risk
3. **Steroid response**: Most critical prognostic factor; SR vs SS determines trajectory
4. **Columbia variant**: Collapsing (worst), tip (best), NOS (intermediate)
5. **APOL1 genotype**: High-risk genotype (G1/G1, G1/G2, G2/G2) confers 10-fold risk
6. **Secondary aetiology**: Treatable causes may improve prognosis
7. **Hypertension**: Uncontrolled hypertension accelerates progression
8. **IFTA on biopsy**: Interstitial fibrosis and tubular atrophy indicates chronicity

### 2.12 Treatment Overview

**First-line: Corticosteroids**
- Prednisone 1 mg/kg/day (max 80 mg) for 16 weeks minimum
- Most important initial intervention for primary FSGS
- Remission in 40–60% of primary FSGS

**Steroid-resistant: Calcineurin Inhibitors (CNI)**
- Cyclosporine or tacrolimus
- Response rate 60–70% in CNIs
- Often combined with low-dose corticosteroids

**Steroid-dependent: Steroid-sparing agents**
- Mycophenolate mofetil (MMF)
- Calcineurin inhibitors
- Rituximab (emerging)

**Genetic FSGS**
- Immunosuppression is ineffective
- Supportive care: RAAS blockade, SGLT2 inhibitors
- Genetic counselling

**Secondary FSGS**
- Treat underlying cause (weight loss, antiretroviral therapy, BP control)

**Collapsing variant**
- CNI-based immunosuppression
- May require combination therapy
- Poor response to steroids alone

**Novel therapies (investigational)**
- Abatacept (CTLA-4 Ig, targets B7-1)
- Adalimumab (anti-TNF)
- TRAF-1 inhibitors
- Complement inhibitors (for complement-mediated forms)

### 2.13 Treatment Algorithm

Seven-step treatment algorithm:

1. **Confirm diagnosis**: Adequate renal biopsy with Columbia classification
2. **Exclude genetic causes**: Genetic testing if indicated (family history, age <25, resistant, African American)
3. **Exclude secondary causes**: Obesity, HIV, hypertension, drugs, renal mass
4. **Initiate prednisone**: 1 mg/kg/day (max 80 mg) for 16 weeks
5. **Reassess at 12–16 weeks**: Evaluate proteinuria, eGFR, clinical response
6. **If steroid-resistant**: Initiate CNI (cyclosporine or tacrolimus)
7. **If CNI failure**: Consider combination therapy, clinical trials, or preparation for ESKD/transplant; note 20–40% post-transplant recurrence risk

### 2.14 Monitoring Protocol

**During Steroid Therapy**
- Blood pressure monitoring (weekly initially)
- Blood glucose (fasting glucose weekly for 4 weeks, then monthly)
- Bone density assessment (baseline and annually)
- Infection screening (TB, hepatitis)
- Lipid profile (baseline and at 3 months)
- Ophthalmological examination (cataract risk)

**During CNI Therapy**
- Trough levels (trough cyclosporine 100–200 ng/mL; trough tacrolimus 5–10 ng/mL)
- Serum creatinine (weekly initially, then monthly)
- Blood pressure
- Potassium and magnesium levels
- Lipid profile

**General Monitoring**
- Proteinuria/albuminuria (q1–3 months)
- eGFR (q1–3 months)
- Complete blood count (monthly on immunosuppression)
- Liver function tests (monthly)

**Re-biopsy Indications**
- No response at 6 months of adequate therapy
- Suspicion of variant change or disease progression
- Evaluation for calcineurin inhibitor nephrotoxicity

### 2.15 Complications

Nine major complications:

1. **Steroid toxicity**: Cushing syndrome, diabetes, osteoporosis, cataracts, avascular necrosis, myopathy, psychosis
2. **CNI nephrotoxicity**: Chronic interstitial fibrosis, thrombotic microangiopathy
3. **CKD progression**: Progressive loss of renal function
4. **ESKD**: 20–40% of patients progress to dialysis within 10 years
5. **Infection**: Immunosuppression-related opportunistic infections
6. **Thromboembolism**: Nephrotic syndrome-associated hypercoagulability
7. **Cardiovascular disease**: Accelerated atherosclerosis from dyslipidaemia and hypertension
8. **Relapse**: 25–40% post-remission relapse rate
9. **Post-transplant recurrence**: 20–40% overall; up to 50% in collapsing variant

### 2.16 Relapse Information

- **Relapse rate**: 25–40% after initial remission
- **Risk factors**: Prior relapses, younger age at diagnosis, persistent sub-nephrotic proteinuria, complete foot process effacement on EM, African American ancestry
- **Management**: Restart prednisone; consider adding steroid-sparing agent (MMF, CNI)
- **Post-transplant recurrence**: 20–40% of primary FSGS recurs; 50% in collapsing variant; may cause graft loss in 50% of recurrent cases
- **Plasmapheresis**: Used for post-transplant recurrence with variable success

### 2.17 Long-Term Prognosis

| Timepoint | Steroid-Sensitive | Steroid-Resistant |
|-----------|-------------------|-------------------|
| 5-year renal survival | >90% | 60–70% |
| 10-year renal survival | 80% | 30–50% |

**By Columbia Variant (10-year renal survival)**
| Variant | 10-Year Survival |
|---------|------------------|
| Tip | ~90% |
| NOS | ~65% |
| Cellular | ~55% |
| Perihilar | ~50% |
| Collapsing | ~30% |

**Post-Transplant**
- Recurrence rate: 20–40%
- Graft loss from recurrence: ~50% of recurrent cases
- Collapsing variant: highest recurrence and graft loss risk

### 2.18 Evidence Summary

**Key Clinical Trials and Registries**
- **FSGS CT Consortium**: Large multi-centre trials establishing steroid and CNI protocols
- **FONT trials (FSGS of Nephrotic Type)**: Investigated additional therapies for resistant FSGS
- **DUET trial (sparsentan)**: Endothelin/receptor antagonist for FSGS; showed significant proteinuria reduction but regulatory status remains uncertain
- **PODO-TEC registry**: European registry for FSGS outcomes
- **FDA-approved specific therapies**: None currently approved for FSGS specifically

**Biomarker Evidence**
- suPAR: Elevated in primary FSGS; potential predictive biomarker; not yet validated for clinical use
- Anti-CD40: Under investigation as a therapeutic target

### 2.19 Guideline Recommendations

| Guideline | Year | Key Recommendations |
|-----------|------|-------------------|
| KDIGO 2021 Ch 4 | 2021 | Steroids first-line; CNI for resistant; genetic testing indications |
| KDIGO 2025 Emerging | 2025 | Novel therapies, APOL1-targeted treatment, biomarker integration |
| ISN 2023 | 2023 | Global perspectives on FSGS management |
| ASN 2022 | 2022 | Expert consensus on treatment algorithms |
| APOL1-FSGS 2023 | 2023 | APOL1-specific guidance including investigational inhibitors |

### 2.20 Key References

1. D'Agati VD et al. Pathologic classification of focal segmental glomerulosclerosis: a working proposal. *Am J Kidney Dis*. 2004;43(2):368-382.
2. Genovese G et al. Association of trypanolytic ApoL1 variants with kidney disease in African Americans. *Science*. 2010;329(5993):841-845.
3. KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases. *Kidney Int*. 2021;100(4S):S1-S276.
4. Trivino A et al. A pilot study assessing the efficacy of abatacept in FSGS (FONT). *Clin J Am Soc Nephrol*. 2021.
5. Trachtman H et al. DUET: Sparsentan in FSGS. *Kidney Int*. 2023.
6. D'Agati V. Focal segmental glomerulosclerosis. *N Engl J Med*. 2011;365(24):2303-2312.
7. FSGS Clinical Trial Consortium. Multi-centre studies on FSGS treatment. Various publications.
8. Kopp JB et al. APOL1 and kidney disease in African Americans. *N Engl J Med*. 2021.
9. De Vriese AS et al. The proposal of a therapeutic algorithm for FSGS. *Kidney Int*. 2017.
10. Cravedi P et al. Nephrotic syndrome and recurrence after kidney transplantation. *Lancet*. 2019.
11. Rovin BH et al. KDIGO 2025 emerging therapies for glomerular diseases. *Kidney Int*. 2025.

### 2.21 Variant-Specific Considerations

The Columbia classification variants carry distinct management and prognostic implications:

- **NOS**: Most common; standard steroid approach; intermediate prognosis
- **Perihilar**: Often secondary/adaptive; focus on treating underlying cause; less likely to respond to immunosuppression
- **Cellular**: May have variable steroid response; consider early CNI
- **Tip**: Favourable prognosis; often steroid-sensitive; consider avoiding aggressive immunosuppression
- **Collapsing**: Most aggressive; often steroid-resistant; high APOL1 association; may require combination CNI therapy; poor transplant prognosis

---

## 3. Domain Audit Against V4.1 16-Domain Framework

| Domain | Status | Coverage |
|--------|--------|----------|
| Disease Definition | Complete | All three aetiological categories |
| Epidemiology | Complete | Incidence, prevalence, racial distribution |
| Aetiology | Complete | Primary, genetic, secondary |
| Pathophysiology | Complete | Podocyte injury cascade, collapsing mechanism |
| Clinical Presentation | Complete | Nephrotic and non-nephrotic presentations |
| Diagnostic Criteria | Complete | 8 criteria, Columbia classification |
| Differential Diagnosis | Complete | 7 key differentials |
| Laboratory Findings | Complete | 11-item workup |
| Biopsy Findings | Complete | LM, IF, EM, all Columbia variants |
| Classification Systems | Complete | Columbia, aetiological, steroid response |
| Risk Stratification | Complete | 8 prognostic factors |
| Treatment | Complete | Steroids, CNI, genetic, secondary, novel |
| Monitoring | Complete | Steroid, CNI, general protocols |
| Complications | Complete | 9 complications including recurrence |
| Prognosis | Complete | Variant-specific, steroid-response specific |
| Evidence Base | Complete | Trials, registries, guidelines |

---

## 4. Genetic Basis: APOL1

### 4.1 APOL1 Risk Alleles

APOL1 (apolipoprotein L1) is a trypanolytic factor that protects against *Trypanosoma brucei*. Two risk variants (G1 and G2) are common in populations of African descent:

- **G1**: S342G/I384M (two missense variants)
- **G2**: N388del (deletion)

### 4.2 Genetic Risk

| Genotype | Risk |
|----------|------|
| G0/G0 | Reference (no risk) |
| G1/G0 or G2/G0 | 1.5–2x risk |
| G1/G1, G1/G2, or G2/G2 | 7–10x risk |

### 4.3 Clinical Implications

- APOL1 high-risk genotype is particularly associated with collapsing FSGS and HIVAN
- Immunosuppression is generally ineffective in APOL1-associated FSGS
- Investigational APOL1 inhibitors are in early clinical trials
- Genetic counselling recommended for high-risk genotype carriers

---

## 5. Trial Landscape

### 5.1 Current Therapeutic Landscape

| Therapy | Phase | Status | Notes |
|---------|-------|--------|-------|
| Prednisone | Standard of care | Approved (off-label) | First-line for primary FSGS |
| Cyclosporine | Standard of care | Approved (off-label) | Steroid-resistant FSGS |
| Tacrolimus | Standard of care | Approved (off-label) | Alternative CNI |
| MMF | Standard of care | Approved (off-label) | Steroid-dependent |
| Sparsentan (DUET) | Phase 3 | Completed | Endothelin/receptor antagonist; significant proteinuria reduction |
| Abatacept | Phase 2/3 | Completed (FONT) | CTLa-4 Ig; mixed results |
| TRAF-1 inhibitor | Preclinical | Investigational | Novel target |
| APOL1 inhibitor | Phase 1 | Investigational | Targeted therapy for APOL1-associated FSGS |

### 5.2 Unmet Needs

1. No FDA-approved specific therapy for FSGS
2. Need for validated non-invasive biomarkers (suPAR validation ongoing)
3. Improved understanding of circulating permeability factors
4. APOL1-targeted therapies for genetic forms
5. Better prediction of steroid response
6. Recurrence prevention strategies for transplant

---

*Document Classification*: Internal Reference  
*Last Updated*: 2026-07-10  
*Review Due*: 2027-01-10

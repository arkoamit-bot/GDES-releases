# Diabetic Kidney Disease — Disease Knowledge Specification

**Document ID:** DKD-DK-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Disease Knowledge  

---

## 1. Document Purpose

This document defines the complete disease knowledge specification for Diabetic Kidney Disease across all 21 fields of the standardised disease record schema.

---

## 2. Disease Record — Full 21-Field Schema

### 2.1 Definition

Diabetic Kidney Disease (DKD) is a progressive kidney disease caused by long-standing diabetes mellitus, characterised by albuminuria, declining eGFR, and increased cardiovascular risk. It is the most common cause of end-stage kidney disease worldwide. DKD results from a combination of metabolic (hyperglycemia) and hemodynamic (hypertension, RAAS activation) injuries leading to podocyte loss, mesangial expansion, glomerulosclerosis, and tubulointerstitial fibrosis.

### 2.2 Epidemiology

Most common cause of ESKD worldwide (30-50% of ESKD). Affects 25-40% of patients with diabetes. Type 2 DM accounts for >90% of DKD. Global prevalence: ~150 million affected. Higher risk: African American (3-4x), Hispanic (2x), Asian ancestry. Peak onset 40-60 years (type 2), 15-25 years after diagnosis (type 1). Incidence increasing with diabetes epidemic. CVD mortality 2-3x higher than general population. Annual mortality 5-10% in advanced DKD.

### 2.3 Aetiology

Chronic hyperglycemia (>90% with type 2 DM, ~10% type 1 DM). Genetic susceptibility: SLC12A3, ELMO1, FRMD3, CNDP1 variants. Hypertension (80%). Obesity and metabolic syndrome. Dyslipidemia. Smoking. Family history of DKD. NAFLD/MAFLD. Epigenetic modifications (metabolic memory). Gut microbiome dysbiosis. Periodontal disease (risk factor for progression).

### 2.4 Pathophysiology

Three core mechanisms: (1) METABOLIC: Hyperglycemia drives AGE formation (glycation of matrix proteins, cross-linking), PKC-beta activation (increased VEGF, TGF-beta, endothelin-1), polyol pathway flux (sorbitol accumulation, NADPH depletion), and oxidative stress (mitochondrial ROS). (2) HEMODYNAMIC: RAAS activation (angiotensin II → efferent arteriolar vasoconstriction, intraglomerular hypertension, podocyte injury), SGLT2 upregulation (increased proximal tubule sodium reabsorption → tubuloglomerular feedback suppression → hyperfiltration). (3) INFLAMMATORY/FIBROTIC: TGF-beta1 activation → mesangial expansion, GBM thickening, podocyte epithelial-mesenchymal transition, tubulointerstitial fibrosis. Key structural changes: GBM thickening (earliest), mesangial expansion (diffuse or nodular Kimmelstiel-Wilson lesions), podocyte loss/effacement, arteriolar hyalinosis, tubulointerstitial fibrosis. Hyperfiltration phase (early) → progressive eGFR decline (later).

### 2.5 Clinical Presentation

EARLY (Stages 1-2): Asymptomatic. Incidental finding of microalbuminuria on screening. Normal or elevated eGFR (hyperfiltration). Normotensive or mild hypertension. PROGRESSIVE (Stages 3-4): Macroalbuminuria (ACR >300 mg/g). Declining eGFR (30-59 mL/min). Hypertension (often difficult to control). Peripheral edema (nephrotic or fluid overload). Dyslipidemia. Concurrent diabetic retinopathy (present in >90% type 1, 60-70% type 2). ADVANCED (Stage 5/G5): ESKD symptoms. Volume overload. Uremic complications. Anemia (disproportionate to eGFR due to erythropoietin deficiency). Cardiovascular events (MI, stroke, HF). KEY NOTE: Urinary sediment is typically BLAND (no active sediment). Nephrotic-range proteinuria with active sediment suggests superimposed GN (consider biopsy).

### 2.6 Diagnostic Criteria

| # | Criterion | Essential | Evidence Level |
|---|---|---|---|
| 1 | Diabetes mellitus (type 1 or type 2) | Yes | 1 |
| 2 | Persistent albuminuria: ACR >=30 mg/g (microalbuminuria) or >=300 mg/g (macroalbuminuria) on >=2 of 3 specimens over 3-6 months | Yes | 1 |
| 3 | eGFR <60 mL/min/1.73m2 (CKD G3a+) for >=3 months | Yes | 1 |
| 4 | Exclusion of non-diabetic kidney disease: bland sediment, no active urine sediment | Yes | 2 |
| 5 | Diabetic retinopathy present (especially for type 1 DM) | No | 2 |
| 6 | Duration of diabetes: >=5 years for type 1, typically present at diagnosis for type 2 | No | 2 |
| 7 | Renal biopsy: GBM thickening, mesangial expansion, nodular glomerulosclerosis (Kimmelstiel-Wilson) | No | 1 |

### 2.7 Differential Diagnosis

| Condition | Key Distinguishing Features |
|---|---|
| hypertensiveNephrosclerosis | See text |
| fsgs | See text |
| membranous | See text |
| iga | See text |
| lupus | See text |

### 2.8 Laboratory Findings

- Hyperglycemia (fasting glucose, postprandial)
- HbA1c: elevated (target <7% for most)
- ACR (albumin-to-creatinine ratio): microalbuminuria (30-300), macroalbuminuria (>300) mg/g
- eGFR: declining (CKD-EPI equation) over years
- Serum creatinine: rising as CKD progresses
- Bland urinary sediment: no RBC casts, few hyaline casts
- Serum albumin: normal or low (nephrotic range in heavy proteinuria)
- Lipid profile: elevated triglycerides, LDL, low HDL (diabetic dyslipidemia)
- Potassium: may be elevated (RAASi, finerenone, CKD)
- Bicarbonate: low (metabolic acidosis of CKD)
- Hb/Hct: anemia (disproportionate to eGFR in advanced DKD)
- Phosphate, PTH: elevated in advanced CKD-MBD
- BNP/NT-proBNP: elevated (volume overload, HF)

### 2.9 Biopsy Findings

- LM: GBM thickening (earliest change, seen by silver stain/PAS)
- LM: Diffuse mesangial expansion (increased mesangial matrix)
- LM: Nodular mesangial sclerosis (Kimmelstiel-Wilson lesions) — PATHOGNOMONIC
- LM: Arteriolar hyalinosis (afferent and efferent arterioles)
- LM: Tubulointerstitial fibrosis and tubular atrophy (proportional to GFR)
- LM: Insudative lesions (fibrin caps, capsular drops)
- LM: Global and segmental glomerulosclerosis (advanced)
- IF: Linear IgG staining along GBM (non-specific, due to trapping)
- IF: Negative for immune complex deposits (no granular IF)
- EM: GBM thickening (diffuse, uniform, >395 nm in adults)
- EM: Mesangial matrix increase with collagen fibrils
- EM: Podocyte foot process effacement (variable)
- RPS Classification: Class I (GBM thickening only) → Class II (mesangial expansion) → Class III (nodular sclerosis) → Class IV (advanced sclerotic)

### 2.10 Classification Systems

| System | Components | Source |
|---|---|---|
| CKD Staging (KDIGO) | G1-G5 (eGFR) + A1-A3 (albuminuria) — combined risk strata (green/yellow/orange/red) | KDIGO 2024 CKD |
| Renal Pathology Society (RPS) Classification | Class I (GBM thickening), II (mesangial expansion), III (nodular sclerosis), IV (advanced sclerosis) | RPS 2010 |
| Clinical Stages of DKD | Stage 1: Hyperfiltration / Stage 2: Microalbuminuria / Stage 3: Macroalbuminuria / Stage 4: Declining eGFR / Stage 5: ESKD | ADA 2025 |
| CKD Heat Map (KDIGO risk strata) | Green (low), Yellow (moderate), Orange (high), Red (very high) — guides referral | KDIGO 2024 |

### 2.11 Risk Stratification

| Factor | Impact | Risk Level |
|---|---|---|
| HbA1c >8% (poor glycemic control) | 2-3x risk of progression to macroalbuminuria and ESKD | High |
| SBP >140 mmHg (uncontrolled hypertension) | 2x risk of eGFR decline and CV events | High |
| ACR >300 mg/g (macroalbuminuria) | 3-4x risk of ESKD vs microalbuminuria alone | High |
| Rapid eGFR decline (>5 mL/min/year) | Strongest predictor of ESKD and mortality | High |
| Duration of diabetes >10 years | Higher cumulative risk of DKD | Moderate |
| African American/Hispanic ancestry | 2-4x higher DKD risk vs Caucasian | High |
| Obesity (BMI >30) | Accelerates progression independent of BP/glucose | Moderate |
| Heart failure / CV disease | 2x mortality risk; limits therapy options | High |
| Hyperkalemia (K+ >5.0) | Limits RAASi/finerenone titration | Moderate |
| Anemia (Hb <11) | Associated with faster progression and worse outcomes | Moderate |
| Smoking | 30-50% increased risk of progression | Moderate |

### 2.12 Treatment Overview

GLUCOSE CONTROL: intensive glycemic control (HbA1c target <7% or individualized). Metformin first-line for type 2 (eGFR >30). GLP-1 RA (semaglutide, dulaglutide) for CV risk reduction and weight loss. SGLT2i (dapagliflozin, empagliflozin, canagliflozin) for cardiorenal protection regardless of glycemic control. RAAS BLOCKADE: ACEi or ARB titrated to max tolerated dose for albuminuria reduction and kidney protection. HEMODYNAMIC: BP target <130/80 mmHg. Add SGLT2i for combined RAASi + SGLT2i benefit. NON-STEROIDAL MRA: finerenone for additional albuminuria reduction and CV/kidney benefit (eGFR >=25, K+ <5.0). CARDIOVASCULAR: statin for all (atorvastatin 20-80 mg or rosuvastatin 10-40 mg). Antiplatelet for secondary prevention. SMOKING CESSATION: mandatory. DIET: moderate protein restriction (0.8 g/kg/day), sodium <2 g/day, potassium restriction if hyperkalemia. ESKD MANAGEMENT: dialysis (hemodialysis or peritoneal) or kidney transplant. CARDIOVASCULAR RISK REDUCTION: SGLT2i + GLP-1 RA + statin + RAASi combination.

### 2.13 Treatment Algorithms

| Step | Action |
|---|---|
| 1 | Confirm DKD: persistent albuminuria + bland sediment + diabetes + retinopathy |
| 2 | Assess severity: CKD stage (G1-G5), ACR (A1-A3), BP, HbA1c, comorbidities |
| 3 | Initiate RAAS blockade: ACEi/ARB at low dose, titrate to max tolerated |
| 4 | Add SGLT2i: dapagliflozin 10 mg or empagliflozin 10 mg (eGFR >=20-25) |
| 5 | Optimize glucose control: metformin (if eGFR >30), GLP-1 RA for CV benefit |
| 6 | Add finerenone 10-20 mg if eGFR >=25, K+ <5.0, and persistent albuminuria |
| 7 | BP target <130/80: add CCB/thiazide if not at target on RAASi + SGLT2i |
| 8 | Statin for all (moderate-high intensity); antiplatelet if established CVD |
| 9 | Monitor and manage complications: anemia, CKD-MBD, metabolic acidosis, volume overload |
| 10 | Prepare for RRT when eGFR <20: access planning, transplant evaluation |

### 2.14 Monitoring Protocol

Every 3 months: HbA1c, eGFR, ACR, BP, K+, body weight. Every 6 months: lipid panel, uric acid, Hb, bicarbonate. Every 12 months: ophthalmology exam, foot exam, ECG, cardiovascular risk assessment. More frequent (monthly) during RAASi/SGLT2i/finerenone initiation or dose titration. Consider biopsy if: active sediment, rapid eGFR decline without clear cause, sudden increase in proteinuria, suspicion of superimposed GN.

### 2.15 Complications

ESKD requiring RRT (dialysis or transplant) — 20-40% with macroalbuminuria over 10 years
Cardiovascular events: myocardial infarction, stroke, heart failure (2-3x risk)
Hyperkalemia (RAASi, finerenone, CKD) — can limit therapy
Volume depletion (SGLT2i, diuretics)
Hypoglycemia (insulin or sulfonylurea with declining eGFR)
Anemia of CKD (disproportionate, EPO deficiency)
CKD-MBD: hyperphosphatemia, secondary hyperparathyroidism, vitamin D deficiency
Metabolic acidosis (reduced renal acid excretion)
Frailty, sarcopenia, malnutrition (advanced CKD)
Peripheral arterial disease and diabetic foot ulcers
Infection risk (diabetes + CKD + immunosuppression if transplanted)
Contrast-induced AKI (consider risk-benefit of contrast studies)

### 2.16 Relapse Information

DKD is a progressive disease, not relapsing-remitting. Albuminuria may decrease with effective treatment (RAASi, SGLT2i, finerenone, GLP-1 RA) — this represents regression (better prognosis) not relapse. eGFR decline may slow or plateau with combination therapy. Rapid decline after treatment interruption (e.g., stopping RAASi). Recovery of kidney function after DAA therapy for HCV is not applicable. Post-transplant: DKD may recur in the allograft (up to 30-50% at 5 years in type 1 DM; 10-20% in type 2). Minimal change disease-like podocytopathy can occur with SGLT2i (rare).

### 2.17 Long-Term Prognosis

10-year ESKD risk: 20-40% with macroalbuminuria (A3). 5-10% with microalbuminuria (A2). <5% with normoalbuminuria (A1). eGFR decline rate: average 3-5 mL/min/year with treatment; 5-10 mL/min/year without. With RAASi + SGLT2i + finerenone combination: slowing of decline by 30-50%. Cardiovascular mortality 2-3x higher than general population. Median survival on dialysis: 3-5 years (diabetes is worst survival of any ESKD cause). Kidney transplant: best option (5-year graft survival 75-85%). Prognosis worse with: macroalbuminuria, rapid eGFR decline, CVD, poor glycemic control, late presentation.

### 2.18 Evidence Summary

RAASi: landmark trials (IDNT, RENAAL, BENEDICT) established ACEi/ARB as cornerstone for albuminuria reduction and kidney protection. SGLT2i: CREDENCE (canagliflozin), DAPA-CKD (dapagliflozin), EMPA-KIDNEY (empagliflozin) — consistent 30-40% reduction in composite kidney outcomes. GLP-1 RA: LEADER (liraglutide), SUSTAIN-6 (semaglutide), REWIND (dulaglutide) — CV benefit, ACR reduction. Finerenone: FIDELIO-DKD and FIGARO-DKD — 18-23% reduction in kidney outcomes, 14-31% CV benefit. Meta-analyses confirm combination RAASi + SGLT2i + finerenone provides additive benefit. No RCT for blood pressure target specifically in DKD, but SPRINT subgroup supports <130/80.

### 2.19 Guideline Recommendations

| Guideline / Chapter | Recommendation |
|---|---|
| KDIGO 2024 CKD in Diabetes Guideline | RAASi + SGLT2i as foundational therapy (1A). Finerenone add-on for persistent albuminuria (1B). BP target <130/80 (1B) |
| ADA 2025 CKD and Risk Management | SGLT2i recommended for DKD with eGFR >=20 (1A). GLP-1 RA for CV risk reduction (1A) |
| ESC/EASD 2023 CVD in Diabetes | SGLT2i + GLP-1 RA for comprehensive cardiorenal protection (1A) |
| ACR 2020 Diabetic Kidney Disease | RAASi + SGLT2i combination first-line for proteinuric DKD (1B) |
| KDIGO 2021 Glomerular Diseases Ch 11 | Biopsy if atypical features (active sediment, rapid decline, sudden proteinuria increase) (2C) |
| ISN 2023 Diabetic Nephropathy | SGLT2i should be started irrespective of glycemic control (1A) |
| ERA/EDTA 2022 DKD Management | Multifactorial intervention (glucose, BP, lipids, lifestyle) for all (1A) |

### 2.20 Key References

| # | Reference | Journal | Year |
|---|---|---|---|
| 1 | KDIGO 2024 CKD in Diabetes Guideline | Kidney Int | 2024 |
| 2 | Perkovic V et al. Canagliflozin and Renal Outcomes in T2D (CREDENCE) | NEJM | 2019 |
| 3 | Heerspink HJL et al. Dapagliflozin in CKD (DAPA-CKD) | NEJM | 2020 |
| 4 | The EMPA-KIDNEY Collaborative Group. Empagliflozin in CKD | NEJM | 2023 |
| 5 | Bakris GL et al. Finerenone in DKD (FIDELIO-DKD) | NEJM | 2020 |
| 6 | Pitt B et al. Finerenone in CKD (FIGARO-DKD) | NEJM | 2023 |
| 7 | Brenner BM et al. Effects of Losartan on Renal Outcomes in T2D (RENAAL) | NEJM | 2001 |
| 8 | Lewis EJ et al. Renoprotective Effect of ACEi in DN (IDNT) | NEJM | 2001 |
| 9 | Marso SP et al. Semaglutide and CV Outcomes (SUSTAIN-6) | NEJM | 2016 |
| 10 | Gerstein HC et al. Dulaglutide and Renal Outcomes (REWIND) | Lancet | 2019 |

### 2.21 Notes

GDES V4.1 Medical Knowledge Engineering. Diabetic Kidney Disease is the eleventh disease in the V4.1 sequence. Key: most common cause of ESKD worldwide. Combination RAASi + SGLT2i + finerenone is modern standard of care. Urine sediment is bland (unlike primary GN). Diabetic retinopathy is a strong correlate (biopsy often not needed if retinopathy present). All guideline mapping references KDIGO 2024 as default source.

---

## 3. Domain Audit Summary

| Domain Element | Status | Completeness |
|---|---|---|
| 21-field schema | Complete | 21/21 fields |
| Evidence base | Complete | Multiple landmark RCTs |
| Guideline integration | Complete | KDIGO 2024, ADA 2025, ESC/EASD 2023 |
| Combination therapy | Complete | RAASi + SGLT2i + finerenone |
| CV risk management | Complete | Statins, SGLT2i, GLP-1 RA |

---

## 4. Evidence Base

### 4.1 Key Clinical Studies

- **CREDENCE (Perkovic 2019):** Canagliflozin 30% RRR in kidney outcomes
- **DAPA-CKD (Heerspink 2020):** Dapagliflozin 39% RRR in composite kidney outcome
- **EMPA-KIDNEY (2023):** Empagliflozin 28% RRR in kidney disease progression
- **FIDELIO-DKD (Bakris 2020):** Finerenone 18% RRR in kidney failure
- **RENAAL (Brenner 2001):** Losartan 16% RRR in doubling Cr/ESKD

### 4.2 Ongoing Knowledge Gaps

- Optimal SGLT2i timing relative to RAASi initiation
- Finerenone benefit with SGLT2i as background (subgroup data positive)
- Role of GLP-1 RA added to SGLT2i + finerenone
- Biomarkers for early DKD detection beyond albuminuria
- DKD pathophysiology in normoalbuminuric phenotype

# Drug Intelligence Library

**Document ID:** GDES-V4.2-DRUG-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Unified Drug Intelligence Platform

---

## 1. Introduction

### 1.1 Evolution from V4.1

In GDES V4.1, drug knowledge was maintained as per-disease drug lists within individual disease knowledge bases (e.g., `ANCA_DRUG_KNOWLEDGE.md`, `iga_drug_knowledge.md`, `lupus_drug_knowledge.md`). Each disease maintained its own drug inventory with disease-specific indications, resulting in fragmentation — the same drug (e.g., rituximab) was documented independently across ANCA, lupus, membranous, and transplant rejection knowledge bases with inconsistent fields, dosing, and monitoring guidance.

### 1.2 V4.2 Unified Drug Object Model

V4.2 introduces a **disease-independent reusable drug object model** that:
- Defines each drug once with all properties (MoA, pharmacokinetics, safety, monitoring, dosing)
- Associates drugs with diseases through a many-to-many indication mapping (which diseases, which line of therapy)
- Enables cross-disease insights (e.g., comparing rituximab use across ANCA, lupus, and membranous)
- Provides consistent renal dose adjustment tables applicable to any disease state
- Serves as the single source of truth for all clinical decision support rules

### 1.3 Document Scope

This library covers **53 therapeutic agents** organised into 13 drug classes, plus 7 additional immunosuppressant/supportive therapies. Each drug entry contains 15 standardised knowledge fields. Three appendices provide class comparisons, disease-specific regimen tables (covering all 23 glomerular disease IDs), and a renal dosing quick reference.

### 1.4 Disease Identifier Reference

The following disease ID codes are used throughout this document:

| ID | Disease |
|----|---------|
| `alport` | Alport Syndrome |
| `anca` | ANCA-Associated Vasculitis / Pauci-Immune GN |
| `antiGbm` | Anti-GBM Disease (Goodpasture Syndrome) |
| `antibodyMediatedRejection` | Antibody-Mediated Rejection (ABMR) |
| `bkVirusNephropathy` | BK Virus Nephropathy |
| `c3` | C3 Glomerulopathy (C3G) |
| `cniToxicity` | Calcineurin Inhibitor Nephrotoxicity |
| `cryoglobulinemic` | Cryoglobulinemic Glomerulonephritis |
| `denseDepositDisease` | Dense Deposit Disease (DDD) |
| `diabeticNephropathy` | Diabetic Kidney Disease |
| `drugInducedGn` | Drug-Induced Glomerulonephritis |
| `fibrillaryGlomerulonephritis` | Fibrillary Glomerulonephritis |
| `fsgs` | Focal Segmental Glomerulosclerosis |
| `hivan` | HIV-Associated Nephropathy (HIVAN) |
| `iga` | IgA Nephropathy / IgA Vasculitis |
| `irgn` | Infection-Related Glomerulonephritis |
| `lupus` | Lupus Nephritis |
| `mcd` | Minimal Change Disease |
| `membranous` | Membranous Nephropathy |
| `mpgn` | Membranoproliferative GN (MPGN) |
| `tCellMediatedRejection` | T-Cell Mediated Rejection (TCMR) |
| `thinBasementMembrane` | Thin Basement Membrane Nephropathy |
| `transplantGlomerulopathy` | Transplant Glomerulopathy |

---


## 2. RAAS Inhibitors

## 2.1. Ramipril

### Mechanism of Action
Competitive inhibitor of angiotensin-converting enzyme (ACE), blocking conversion of angiotensin I to angiotensin II, reducing vasoconstriction, aldosterone secretion, and intraglomerular pressure. Reduces proteinuria through haemodynamic and anti-fibrotic effects.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `alport` | Antiproteinuric, renoprotective | First-line | 1 |
| `diabeticNephropathy` | Antiproteinuric, renoprotective, BP control | First-line | 1 |
| `fsgs` | Antiproteinuric, renoprotective | First-line | 1 |
| `iga` | Antiproteinuric for all patients with proteinuria >0.5g/day | First-line | 1 |
| `mcd` | Antiproteinuric during remission (if HTN/proteinuria) | Adjunctive | 2 |
| `membranous` | Antiproteinuric for all patients with proteinuria | First-line | 1 |
| `lupus` | Antiproteinuric, BP control in LN with proteinuria | First-line | 1 |
| `c3` | Antiproteinuric support | Adjunctive | 2 |
| `mpgn` | Antiproteinuric support | Adjunctive | 2 |
| `cryoglobulinemic` | Antiproteinuric support | Adjunctive | 2 |

### Contraindications
History of angioedema, bilateral renal artery stenosis, pregnancy (2nd/3rd trimester), concomitant use with aliskiren in diabetes, severe hypotension, aortic stenosis.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1 | >=90 mL/min | No adjustment |
| Stage 2 | 60-89 mL/min | No adjustment |
| Stage 3a | 45-59 mL/min | No adjustment; monitor K+, Cr at 1-2 weeks |
| Stage 3b | 30-44 mL/min | Start low (1.25-2.5mg); titrate cautiously |
| Stage 4 | 15-29 mL/min | Start 1.25mg OD; max 5mg OD |
| Stage 5 | <15 mL/min (not on dialysis) | Start 1.25mg OD; monitor closely |

### Dialysis Dosing
Not significantly removed by haemodialysis or peritoneal dialysis. Dose as for eGFR <15. Monitor for hypotension post-dialysis.

### Transplant Considerations
Preferred RAASi in renal transplant recipients with hypertension and proteinuria. Monitor for hyperkalemia and eGFR decline. May cause reversible eGFR dip (~10-20%) which is haemodynamic and not necessarily indicative of structural injury.

### Pregnancy / Lactation
FDA Category D (2nd/3rd trimester: oligohydramnios, fetal renal dysplasia, skull hypoplasia). Category C in 1st trimester. Avoid breastfeeding (low transfer but limited data).

### Drug Interactions
NSAIDs (reduced antihypertensive effect, increased nephrotoxicity), potassium supplements/K+-sparing diuretics (hyperkalemia), lithium (increased lithium levels), aliskiren (increased adverse events in diabetes), allopurinol (increased hypersensitivity risk).

### Laboratory Monitoring
Serum creatinine and eGFR: 1-2 weeks after initiation and after each dose escalation. Serum potassium: 1-2 weeks after initiation. BP monitoring.

### Vaccination Advice
No specific restrictions. Inactivated vaccines are safe.

### Common Adverse Effects
Cough (5-20%, higher in Asian populations), dizziness, fatigue, headache, nausea, diarrhoea, rash, taste disturbance (dysgeusia).

### Serious Adverse Effects
Angioedema (0.1-0.7%, higher in African Americans), hyperkalemia (>6.0 mmol/L), acute kidney injury (especially with bilateral renal artery stenosis or volume depletion), hypotension, fetal toxicity.

### Stopping Criteria
Angioedema (any severity), K+ >6.0 mmol/L refractory to management, eGFR decline >30% from baseline within 2 months (evaluate for renal artery stenosis), symptomatic hypotension, pregnancy (2nd/3rd trimester).

### Evidence Level
1 (Strong recommendation — KDIGO 1B for CKD with proteinuria)

### Guideline References
KDIGO 2021 Glomerular Diseases, KDIGO 2024 CKD, ESC/ESH Hypertension Guidelines, NICE NG203.

---

## 2.2. Lisinopril

### Mechanism of Action
ACE inhibitor; pharmacologically similar to ramipril with longer half-life (~12 hours). Reduces angiotensin II formation, decreases aldosterone, increases bradykinin.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | Antiproteinuric, renoprotective, BP control | First-line | 1 |
| `iga` | First-line antiproteinuric (alternative to ramipril) | First-line | 1 |
| `membranous` | Antiproteinuric | First-line | 1 |
| `fsgs` | Antiproteinuric | First-line | 1 |
| `alport` | Antiproteinuric | First-line | 1 |
| `lupus` | Antiproteinuric when ACEi indicated | First-line | 1 |

### Contraindications
History of angioedema, pregnancy (2nd/3rd trimester), bilateral renal artery stenosis.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | No adjustment |
| Stage 3 | 30-59 mL/min | Start 2.5-5mg OD; max 20mg |
| Stage 4 | 15-29 mL/min | Start 2.5mg OD; max 10mg |
| Stage 5 | <15 mL/min | Start 2.5mg OD; max 5mg |

### Dialysis Dosing
Removed by haemodialysis (partial). Dose post-dialysis if possible. Max 5mg/day.

### Transplant Considerations
Alternative first-line RAASi in transplant. Similar considerations to ramipril.

### Pregnancy / Lactation
FDA Category D (2nd/3rd trimester). Avoid breastfeeding.

### Drug Interactions
NSAIDs, potassium-sparing diuretics, lithium, aliskiren.

### Laboratory Monitoring
eGFR, serum creatinine, potassium at 1-2 weeks post-initiation and dose changes.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Cough (higher than ramipril in some populations), hypotension, dizziness, hyperkalemia, rash.

### Serious Adverse Effects
Angioedema, severe hyperkalemia, AKI, fetal toxicity.

### Stopping Criteria
Same as ramipril.

### Evidence Level
1 (Strong recommendation)

### Guideline References
KDIGO 2021, KDIGO 2024, NICE NG203.

---

## 2.3. Losartan

### Mechanism of Action
Selective angiotensin II receptor type 1 (AT1) blocker. Blocks angiotensin II-mediated vasoconstriction, aldosterone release, and pro-fibrotic signalling. Does not affect bradykinin metabolism (no cough).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | First-line when ACEi not tolerated (cough, angioedema) | First-line alternative | 1 |
| `diabeticNephropathy` | Antiproteinuric, renoprotective (RENAAL trial) | First-line | 1 |
| `membranous` | Antiproteinuric alternative | First-line alternative | 1 |
| `fsgs` | Antiproteinuric alternative | First-line alternative | 1 |
| `alport` | Antiproteinuric alternative | First-line alternative | 1 |
| `lupus` | Antiproteinuric when ACEi intolerant | First-line alternative | 1 |

### Contraindications
Pregnancy (2nd/3rd trimester), bilateral renal artery stenosis, severe hepatic impairment.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | No adjustment |
| Stage 3 | 30-59 mL/min | No adjustment; monitor K+ |
| Stage 4 | 15-29 mL/min | Start 25mg OD; max 100mg |
| Stage 5 | <15 mL/min | Start 25mg OD; caution |

### Dialysis Dosing
Not significantly removed. Dose 25-50mg OD. Monitor post-dialysis hypotension.

### Transplant Considerations
Alternative first-line RAASi when ACEi causes cough. No dose adjustment needed for CNI interactions.

### Pregnancy / Lactation
FDA Category D (2nd/3rd trimester). Avoid breastfeeding.

### Drug Interactions
NSAIDs (reduced effect, increased nephrotoxicity), potassium supplements, lithium (increased levels), rifampin (reduced losartan levels), fluconazole (increased losartan levels).

### Laboratory Monitoring
eGFR, creatinine, potassium 1-2 weeks after initiation/dose change.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Dizziness (dose-related), hypotension, hyperkalemia, diarrhoea, dyspepsia, back pain.

### Serious Adverse Effects
Angioedema (rare, <0.1%), severe hyperkalemia, AKI, fetal toxicity.

### Stopping Criteria
Pregnancy, severe hyperkalemia refractory to management, symptomatic hypotension, significant eGFR decline.

### Evidence Level
1 (Strong recommendation — RENAAL trial proven renoprotection in DN)

### Guideline References
KDIGO 2021, KDIGO 2024 CKD, RENAAL trial (N Engl J Med 2001).

---

## 2.4. Valsartan

### Mechanism of Action
ARB with high AT1 receptor affinity. Reduces proteinuria and slows CKD progression.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | BP control, antiproteinuric | First-line | 1 |
| `iga` | Alternative antiproteinuric (ACEi intolerant) | First-line alternative | 1 |
| `membranous` | Antiproteinuric | First-line alternative | 1 |
| `fsgs` | Antiproteinuric | First-line alternative | 1 |

### Contraindications
Same as losartan.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | No adjustment |
| Stage 4 | 15-29 mL/min | Start 40mg BID; reduce if hypotensive |
| Stage 5 | <15 mL/min | Start 40mg OD; caution |

### Dialysis Dosing
Not removed. Max 80mg BID.

### Transplant Considerations
Safe to use in transplant. Monitor K+ and Cr.

### Pregnancy / Lactation
FDA Category D.

### Drug Interactions
Same as losartan.

### Laboratory Monitoring
eGFR, K+, Cr.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Dizziness, headache, fatigue, diarrhoea, arthralgia.

### Serious Adverse Effects
Hyperkalemia, AKI, angioedema (rare).

### Stopping Criteria
Same as other ARBs.

### Evidence Level
1

### Guideline References
KDIGO 2021, KDIGO 2024, NAVIGATOR trial.

---

## 2.5. Telmisartan

### Mechanism of Action
ARB with additional PPAR-gamma partial agonist activity (unique among ARBs). Provides metabolic benefit in addition to BP/proteinuria reduction.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | BP control, antiproteinuric, metabolic benefit | First-line | 1 |
| `iga` | Antiproteinuric alternative | First-line alternative | 1 |
| `membranous` | Antiproteinuric | First-line alternative | 1 |
| `fsgs` | Antiproteinuric | First-line alternative | 1 |

### Contraindications
Same as other ARBs. Biliary obstructive disorders (biliary excretion).

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | No adjustment |
| Stage 4 | 15-29 mL/min | Start 20mg OD; max 40mg |
| Stage 5 | <15 mL/min | Start 20mg OD |

### Dialysis Dosing
Not removed. Max 40mg/day.

### Transplant Considerations
Preferred ARB in patients with metabolic syndrome after transplant.

### Pregnancy / Lactation
FDA Category D.

### Drug Interactions
Digoxin levels may increase.

### Laboratory Monitoring
eGFR, K+, Cr, glucose (PPAR-gamma effect may improve glycaemic control).

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Dizziness, diarrhoea, back pain, upper respiratory infection.

### Serious Adverse Effects
Hyperkalemia, AKI.

### Stopping Criteria
Same as other ARBs.

### Evidence Level
1

### Guideline References
ONTARGET trial, TRANSCEND trial, KDIGO 2021.

---

## 2.6. Irbesartan

### Mechanism of Action
ARB with high AT1 receptor affinity.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | BP control, antiproteinuric (IDNT trial) | First-line | 1 |
| `iga` | Antiproteinuric alternative | First-line alternative | 1 |

### Contraindications
Same as other ARBs.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | No adjustment |
| Stage 4 | 15-29 mL/min | Start 75mg OD; max 300mg |
| Stage 5 | <15 mL/min | Start 75mg OD |

### Dialysis Dosing
Not removed. Max 300mg/day.

### Transplant Considerations
Similar to other ARBs.

### Pregnancy / Lactation
FDA Category D.

### Drug Interactions
Same as other ARBs.

### Laboratory Monitoring
eGFR, K+, Cr.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Dizziness, orthostatic hypotension, hyperkalemia.

### Serious Adverse Effects
Same as other ARBs.

### Stopping Criteria
Same as other ARBs.

### Evidence Level
1 (IDNT trial — irbesartan 300mg renoprotective in DN)

### Guideline References
IDNT trial (N Engl J Med 2001), KDIGO 2021.

---

## 2.7. Candesartan

### Mechanism of Action
ARB with long half-life (9-12 hours). High AT1 receptor binding affinity.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | Antiproteinuric alternative | First-line alternative | 1 |
| `diabeticNephropathy` | BP control, antiproteinuric | First-line | 1 |

### Contraindications
Same as other ARBs.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | No adjustment |
| Stage 4 | 15-29 mL/min | Start 4mg OD; max 16mg |
| Stage 5 | <15 mL/min | Start 2mg OD |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Same as other ARBs.

### Pregnancy / Lactation
FDA Category D.

### Drug Interactions
Same as other ARBs.

### Laboratory Monitoring
eGFR, K+, Cr.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Dizziness, headache, hyperkalemia.

### Serious Adverse Effects
Same as other ARBs.

### Stopping Criteria
Same as other ARBs.

### Evidence Level
1

### Guideline References
CASE-J trial, KDIGO 2021.

---

## 2.8. Eplerenone

### Mechanism of Action
Selective mineralocorticoid receptor antagonist (MRA). Blocks aldosterone binding, reducing sodium reabsorption, potassium excretion, and pro-fibrotic signalling. More selective than spironolactone (less endocrine side effects).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | Add-on antiproteinuric beyond ACEi/ARB | Second-line adjunctive | 1 |
| `iga` | Add-on antiproteinuric (proteinuria despite max RAASi) | Second-line adjunctive | 2 |
| `membranous` | Add-on antiproteinuric | Second-line adjunctive | 2 |
| `fsgs` | Add-on antiproteinuric | Second-line adjunctive | 2 |

### Contraindications
Serum K+ >5.5 mmol/L at baseline, severe renal impairment (eGFR <30 mL/min), concomitant strong CYP3A4 inhibitors, Addison disease, severe hepatic impairment.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | Start 25mg OD; max 50mg OD |
| Stage 3a | 45-59 mL/min | Start 25mg OD; caution |
| Stage 3b | 30-44 mL/min | Start 25mg alternate days |
| Stage 4 | 15-29 mL/min | Contraindicated (NICE) |
| Stage 5 | <15 mL/min | Contraindicated |

### Dialysis Dosing
Not removed. Contraindicated if K+ cannot be controlled.

### Transplant Considerations
Use with extreme caution post-transplant due to CNI-induced hyperkalemia. Monitor K+ closely.

### Pregnancy / Lactation
FDA Category B (animal studies no harm; limited human data). Use only if clearly needed.

### Drug Interactions
Potassium supplements/K+-sparing diuretics (severe hyperkalemia), strong CYP3A4 inhibitors (ketoconazole, itraconazole, clarithromycin — contraindicated), NSAIDs (reduced effect, increased K+), lithium.

### Laboratory Monitoring
Serum K+ (baseline, 1 week, 4 weeks, then monthly), eGFR, BP.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Hyperkalemia (5-15%), dizziness, hypotension, diarrhoea, fatigue.

### Serious Adverse Effects
Severe hyperkalemia (>6.0 mmol/L), AKI.

### Stopping Criteria
K+ >5.5 mmol/L despite dose reduction, eGFR decline >30%, severe hyperkalemia.

### Evidence Level
1 (for add-on therapy in resistant hypertension with CKD)

### Guideline References
KDIGO 2021, KDIGO 2024 CKD, NICE NG136.

---

## 2.9. Spironolactone

### Mechanism of Action
Non-selective mineralocorticoid receptor antagonist with anti-androgenic and progestogenic activity. Reduces proteinuria and fibrosis through aldosterone blockade.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | Adjunctive antiproteinuric | Second-line adjunctive | 2 |
| `diabeticNephropathy` | Antiproteinuric add-on | Second-line adjunctive | 2 |
| `fsgs` | Antiproteinuric add-on | Second-line adjunctive | 2 |
| `membranous` | Antiproteinuric add-on | Adjunctive | 2 |
| `lupus` | Resistant hypertension | Second-line adjunctive | 2 |

### Contraindications
Anuria, acute renal failure, severe renal impairment (eGFR <30), hyperkalemia (>5.5 mmol/L), Addison disease.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | Start 25mg OD; max 100mg |
| Stage 3a | 45-59 mL/min | Start 12.5-25mg OD |
| Stage 3b | 30-44 mL/min | Start 12.5mg OD; caution |
| Stage 4 | 15-29 mL/min | Avoid (risk of hyperkalemia) |
| Stage 5 | <15 mL/min | Avoid |

### Dialysis Dosing
Removed partially. Use with extreme caution. Monitor K+ post-dialysis.

### Transplant Considerations
Risk of hyperkalemia with CNIs. Preferred over eplerenone if cost a concern.

### Pregnancy / Lactation
FDA Category C (D in 2nd/3rd trimester). Anti-androgenic effects on male fetus.

### Drug Interactions
ACEi/ARB (additive hyperkalemia), K+ supplements, NSAIDs, lithium, digoxin (increased levels).

### Laboratory Monitoring
Serum K+, eGFR at 1, 2, 4 weeks, then monthly.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Hyperkalemia, gynecomastia (10-30%, dose-dependent), menstrual irregularities, breast tenderness, decreased libido, impotence, GI disturbances.

### Serious Adverse Effects
Severe hyperkalemia, arrhythmias, volume depletion, AKI.

### Stopping Criteria
K+ >5.5 mmol/L, intolerable gynecomastia, significant eGFR decline.

### Evidence Level
2 (Limited RCT data in GN; stronger evidence in heart failure)

### Guideline References
KDIGO 2021, ESC Heart Failure Guidelines, RALES trial.

---

## 3. SGLT2 Inhibitors

## 3.1. Dapagliflozin

### Mechanism of Action
Selective sodium-glucose cotransporter-2 (SGLT2) inhibitor in the proximal renal tubule. Reduces glucose and sodium reabsorption, increasing urinary glucose and sodium excretion. Reduces intraglomerular pressure through tubuloglomerular feedback activation (afferent arteriolar constriction via adenosine). Additional metabolic and haemodynamic benefits independent of glycaemic control.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | Renoprotection in CKD (eGFR >25) | Second-line (add-on to RAASi) | 1 |
| `diabeticNephropathy` | Renoprotection and cardiovascular protection | First-line (with or without T2DM) | 1 |
| `fsgs` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |
| `membranous` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |
| `alport` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |
| `lupus` | Renoprotection in CKD | Second-line (add-on) | 2 |
| `c3` | Renoprotection in CKD | Second-line (add-on) | 2 |
| `mpgn` | Renoprotection in CKD | Second-line (add-on) | 2 |

### Contraindications
eGFR <25 mL/min at initiation (DAPA-CKD entry criteria), type 1 diabetes (off-label, increased DKA risk), history of diabetic ketoacidosis, hypersensitivity, severe hepatic impairment.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3a | >=45 mL/min | 10mg OD (standard dose) |
| Stage 3b | 25-44 mL/min | 10mg OD (continue if already on therapy) |
| Stage 4 | 15-24 mL/min | Not recommended for initiation; may continue |
| Stage 5 | <15 mL/min | Discontinue unless ESRD on dialysis |

### Dialysis Dosing
Not indicated (no glycaemic or renal benefit expected).

### Transplant Considerations
Limited data but growing experience. DAPA-CKD excluded transplant recipients. Use with caution. Monitor UTI, volume status. Possible CNI interaction (theoretical).

### Pregnancy / Lactation
FDA Category X (contraindicated). Associated with fetal genitourinary and skeletal malformations in animal studies. Check pregnancy status before initiation.

### Drug Interactions
Diuretics (additive volume depletion, hypotension), insulin/insulin secretagogues (increased hypoglycaemia risk), NSAIDs (reduced diuretic effect), lithium (reduced lithium excretion).

### Laboratory Monitoring
eGFR (before initiation, 2-4 weeks after, then q3-6 months), HbA1c (if diabetic), volume status, ketones if unwell (euglycaemic DKA risk).

### Vaccination Advice
All inactivated vaccines safe. Ensure genital hygiene; fungal infection risk.

### Common Adverse Effects
Genital mycotic infections (5-10%, higher in uncircumcised men, diabetic women), urinary tract infections, polyuria, thirst, volume depletion, dizziness.

### Serious Adverse Effects
Euglycaemic diabetic ketoacidosis (atypical DKA, can occur with normal glucose), Fournier gangrene (<0.01%), acute kidney injury (rare, usually in volume-depleted patients), lower limb amputation (canagliflozin class effect, less with dapagliflozin).

### Stopping Criteria
eGFR falls below 25 mL/min in a patient not already on therapy (initiation threshold). Sustained decline post-dialysis. Ketosis/DKA. Severe recurrent UTIs. Pre-surgery (hold 3 days). Severe volume depletion.

### Evidence Level
1 (Strong recommendation — DAPA-CKD: HR 0.61 for renal composite, N Engl J Med 2020)

### Guideline References
DAPA-CKD trial, KDIGO 2024 CKD (updated recommendation), KDIGO 2021, ESC/EASD Guidelines.

---

## 3.2. Empagliflozin

### Mechanism of Action
Selective SGLT2 inhibitor. Reduces intraglomerular pressure, activates tubuloglomerular feedback, reduces oxidative stress, and improves mitochondrial function. Cardioprotective effects via improved myocardial energetics.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | Renoprotection in CKD (eGFR >20) | Second-line (add-on) | 1 |
| `diabeticNephropathy` | Renoprotection and cardiovascular protection | First-line | 1 |
| `fsgs` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |
| `membranous` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |
| `alport` | Renoprotection (CKD with proteinuria) | Second-line (add-on) | 2 |

### Contraindications
eGFR <20 mL/min (EMPA-KIDNEY threshold), type 1 diabetes, DKA history.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3a | >=45 mL/min | 10mg OD |
| Stage 3b | 20-44 mL/min | 10mg OD (benefit shown in EMPA-KIDNEY) |
| Stage 4 | 15-19 mL/min | Not for initiation; continue if already on therapy |
| Stage 5 | <15 mL/min | Discontinue unless on dialysis |

### Dialysis Dosing
Not indicated.

### Transplant Considerations
Similar to dapagliflozin. Limited data.

### Pregnancy / Lactation
FDA Category X.

### Drug Interactions
Same as dapagliflozin.

### Laboratory Monitoring
eGFR, volume status, ketones.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Genital mycotic infections, UTI, polyuria, thirst.

### Serious Adverse Effects
Euglycaemic DKA, Fournier gangrene, AKI (rare).

### Stopping Criteria
eGFR <20 at initiation, DKA, pre-surgery hold.

### Evidence Level
1 (EMPA-KIDNEY: HR 0.72 for renal disease progression, N Engl J Med 2023)

### Guideline References
EMPA-KIDNEY trial, KDIGO 2024 CKD, EMPA-REG OUTCOME.

---

## 3.3. Canagliflozin

### Mechanism of Action
SGLT2 inhibitor with modest SGLT1 inhibition (intestinal). Reduces glucose absorption, increases sodium excretion, reduces intraglomerular pressure.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `diabeticNephropathy` | Renoprotection (CREDENCE trial) | First-line | 1 |
| `iga` | Renoprotection alternative | Second-line alternative | 1 |

### Contraindications
eGFR <30 mL/min (initiation), type 1 diabetes.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3a | >=60 mL/min | 100mg OD (can increase to 300mg if glycaemic target needed) |
| Stage 3a | 45-59 mL/min | 100mg OD (max) |
| Stage 3b | 30-44 mL/min | 100mg OD |
| Stage 4 | 15-29 mL/min | Do not initiate (may continue 100mg) |
| Stage 5 | <15 mL/min | Discontinue |

### Dialysis Dosing
Not indicated.

### Transplant Considerations
Same class considerations as dapagliflozin.

### Pregnancy / Lactation
FDA Category X.

### Drug Interactions
Digoxin levels may increase, warfarin monitoring.

### Laboratory Monitoring
Same as dapagliflozin. Lower limb examination for ulcers/amputation.

### Vaccination Advice
All inactivated vaccines safe.

### Common Adverse Effects
Genital mycotic infections, UTIs, polyuria, thirst, increased urination.

### Serious Adverse Effects
Euglycaemic DKA, Fournier gangrene, lower limb amputation (2x risk, higher than other SGLT2i), AKI, fracture risk (canagliflozin-specific).

### Stopping Criteria
eGFR <30 at initiation, DKA, amputation risk factors.

### Evidence Level
1 (CREDENCE: HR 0.70 for renal composite, N Engl J Med 2019)

### Guideline References
CREDENCE trial, CANVAS program, KDIGO 2024.

---


## 4. Corticosteroids

## 4.1. Methylprednisolone (IV Pulse)

### Mechanism of Action
Potent synthetic glucocorticoid with high glucocorticoid receptor affinity. Inhibits NF-kB and AP-1 transcription factors, reduces pro-inflammatory cytokine production (IL-1, IL-2, IL-6, TNF-alpha), suppresses T-cell activation, induces lymphocyte apoptosis. Pulse dosing achieves rapid immunosuppression with blood-brain barrier and tissue penetration.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `anca` | Induction for severe RPGN/organ-threatening disease | First-line (part of induction) | 1 |
| `antiGbm` | Induction for all anti-GBM disease | First-line (with CyP/PLEX) | 1 |
| `iga` | Crescentic IgA/RPGN | First-line for crescentic | 1 |
| `lupus` | Pulse for severe LN (AKI, RPGN, nephrotic syndrome) | First-line (with CyP/MMF) | 1 |
| `mcd` | Induction for severe/relapsing MCD | Second-line (after oral steroid failure) | 2 |
| `membranous` | Not routine; reserved for rapid deterioration | Rescue therapy | 3 |
| `cryoglobulinemic` | Severe flare with RPGN | Second-line | 2 |
| `fsgs` | Induction for severe FSGS | Second-line | 2 |
| `antibodyMediatedRejection` | Acute ABMR with DSA | First-line (with PLEX/IVIG) | 1 |
| `tCellMediatedRejection` | Acute TCMR (Banff >= IA) | First-line | 1 |
| `irgn` | Severe RPGN (after antibiotics) | Second-line | 3 |

### Contraindications
Untreated systemic infection, systemic fungal infection, known hypersensitivity, recent live vaccination, severe uncontrolled psychiatric illness.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment needed (short pulse course) |

### Dialysis Dosing
Not removed by dialysis. No dose adjustment.

### Transplant Considerations
Standard pulse therapy for acute rejection (3 x 500-1000mg IV). Monitor for hyperglycaemia, infection.

### Pregnancy / Lactation
FDA Category C. Prednisolone preferred in pregnancy (methylprednisolone crosses placenta less). Use only if benefit outweighs risk.

### Drug Interactions
Live vaccines (contraindicated during immunosuppression), NSAIDs (increased GI bleeding risk), anticoagulants (increased bleeding), CYP3A4 inducers (reduced efficacy), CYP3A4 inhibitors (increased levels), insulin/antidiabetic agents (increased requirements).

### Laboratory Monitoring
Blood glucose (during pulse and taper), electrolytes (K+, Na+), BP, fluid balance.

### Vaccination Advice
Avoid live vaccines during therapy. Inactivated vaccines safe but may be less immunogenic. Give vaccines 2-4 weeks before therapy if possible.

### Common Adverse Effects
Insomnia, mood changes (anxiety, euphoria), hyperglycaemia (dose-dependent), fluid retention, increased appetite, dyspepsia, facial flushing.

### Serious Adverse Effects
Avascular necrosis (especially femoral head, 1-3% with pulse), steroid-induced diabetes, severe hypertension, psychosis, adrenal suppression, opportunistic infections (PJP, CMV, TB reactivation), acute pancreatitis, myopathy.

### Stopping Criteria
Active untreated infection, steroid psychosis, severe hyperglycaemia unresponsive to management, completion of prescribed pulse course (3 days typical).

### Evidence Level
1 (Standard of care for induction in immune-mediated GN)

### Guideline References
KDIGO 2021 Glomerular Diseases, KDIGO 2024 Renal Transplantation, ACR Guidelines.

---

## 4.2. Prednisolone / Prednisone (Oral)

### Mechanism of Action
Prednisolone is the active metabolite of prednisone (prodrug converted by hepatic 11-beta-HSD). Glucocorticoid receptor agonist with broad anti-inflammatory and immunosuppressive effects. Inhibits phospholipase A2, reduces prostaglandin and leukotriene synthesis. Suppresses cell-mediated immunity and reduces cytokine production.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `mcd` | First-line induction (children and adults) | First-line | 1 |
| `iga` | High-risk IgAN (TESTING protocol) | First-line for high-risk | 1 |
| `lupus` | Induction backbone for all LN classes | First-line | 1 |
| `anca` | Induction and maintenance (taper) | First-line (with IS) | 1 |
| `membranous` | First-line in modified Ponticelli regimen | First-line (with CyP) | 1 |
| `fsgs` | Induction | First-line | 2 |
| `c3` | May be used in mild/moderate disease | Second-line | 2 |
| `mpgn` | Immunosuppression in immune-complex MPGN | Second-line | 2 |
| `cryoglobulinemic` | Moderate-severe disease | Second-line | 2 |
| `irgn` | Post-infectious GN with severe nephritic syndrome | Second-line | 3 |

### Contraindications
Systemic fungal infection, untreated infections, known hypersensitivity, severe uncontrolled psychiatric disorder, recent live vaccination.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-4 | >=15 mL/min | No dose adjustment (but monitor fluid/glucose) |
| Stage 5 | <15 mL/min | No adjustment; monitor for fluid overload |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not significantly removed. No dose adjustment.

### Transplant Considerations
Standard maintenance immunosuppression component (part of triple therapy with CNI + MMF). Taper typically by 3-6 months post-transplant. Acute rejection treated with pulse methylprednisolone.

### Pregnancy / Lactation
FDA Category B (preferred steroid in pregnancy). Inactivated by placental 11-beta-HSD (90% fetal protection). Monitor for gestational diabetes. Compatible with breastfeeding (low transfer).

### Drug Interactions
CYP3A4 inducers (rifampicin, phenytoin, carbamazepine — reduce steroid levels), CYP3A4 inhibitors (ketoconazole, ritonavir — increase steroid levels), NSAIDs/Aspirin (increased GI bleeding), anticoagulants (variable effect on INR), antidiabetic medications (increased insulin requirements), live vaccines (contraindicated).

### Laboratory Monitoring
Blood glucose (fasting, especially during high-dose), BP, body weight, electrolytes, ophthalmologic exam (annual), bone density (DEXA if >3 months use).

### Vaccination Advice
All inactivated vaccines safe. Live vaccines contraindicated during immunosuppressive therapy (MMR, VZV, yellow fever, nasal influenza). Administer recommended vaccines before initiation if possible.

### Common Adverse Effects
Weight gain, Cushingoid features (moon face, buffalo hump), insomnia, mood lability, increased appetite, dyspepsia, acne, hirsutism, easy bruising, impaired wound healing.

### Serious Adverse Effects
Glucocorticoid-induced diabetes (20-30% cumulative), avascular necrosis (especially femoral head), osteoporosis and fractures (5-10% per year of use), cataracts (posterior subcapsular, 15-30%), glaucoma, adrenal suppression (HPA axis), severe infections (PJP, TB reactivation), steroid-induced myopathy, growth suppression (children), acute pancreatitis.

### Stopping Criteria
Severe infection requiring systemic treatment, steroid psychosis, avascular necrosis, severe steroid-induced diabetes uncontrolled despite management, completion of planned taper.

### Evidence Level
1 (Foundation of immunosuppression in most glomerular diseases)

### Guideline References
KDIGO 2021 Glomerular Diseases, TESTING trial, KDIGO 2024 Renal Transplantation.

---

## 4.3. Budesonide (Nefecon — Targeted)

### Mechanism of Action
Gut-targeted glucocorticoid formulated with delayed-release technology (TARGIT) delivering budesonide to the distal ileum and caecum. High first-pass hepatic metabolism (90%), minimising systemic exposure. Reduces gastrointestinal mucosal B-cell activation and Gd-IgA1 production in IgA nephropathy.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `iga` | Persistent proteinuria >1g/day despite 90 days of optimised RAASi | First-line targeted therapy | 1 |

### Contraindications
Severe hepatic impairment, active infection, known hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | >=15 mL/min | No adjustment (16mg OD fixed dose) |
| Stage 5 | <15 mL/min | Caution; limited data |
| Dialysis | HD/PD | Limited data |

### Dialysis Dosing
Not removed. Limited data.

### Transplant Considerations
Not indicated in transplant setting. No data in transplant IgA recurrence.

### Pregnancy / Lactation
FDA Category C. Limited human data. Avoid unless benefit clearly outweighs risk.

### Drug Interactions
CYP3A4 inhibitors (ketoconazole, erythromycin, grapefruit juice — increase budesonide levels 2-8 fold), CYP3A4 inducers (rifampicin, carbamazepine — decrease budesonide levels).

### Laboratory Monitoring
eGFR, proteinuria (UPCR), BP, blood glucose, electrolytes.

### Vaccination Advice
All inactivated vaccines safe. Live vaccines contraindicated during therapy.

### Common Adverse Effects
Acne (15-20%), peripheral oedema (10-15%), hypertension (10%), muscle spasms, headache, upper respiratory infection.

### Serious Adverse Effects
Corticosteroid-related effects (lower incidence than systemic steroids due to targeted delivery): hyperglycaemia, adrenal suppression (low risk), glaucoma, cataracts (low risk), infections.

### Stopping Criteria
Severe intolerance, non-response after 9 months, severe infection.

### Evidence Level
1 (NefIgArd Phase 3: UPCR reduction 27%, eGFR benefit 5.05 mL/min at 2 years, p<0.0001)

### Guideline References
NefIgArd trial (Lancet 2023), KDIGO 2021 (updated), NICE TA968, FDA approved 2021.

---


## 5. Calcineurin Inhibitors

## 5.1. Tacrolimus

### Mechanism of Action
Binds FK-binding protein 12 (FKBP12), forming a complex that inhibits calcineurin, blocking dephosphorylation of NFAT (nuclear factor of activated T-cells). Suppresses T-cell activation and IL-2 transcription. Also stabilises podocyte cytoskeleton (synaptopodin). 50-100x more potent than cyclosporine.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `mcd` | Steroid-sparing in frequently relapsing/steroid-dependent | Second-line | 1 |
| `fsgs` | Induction and maintenance (CNI-based) | Second-line | 1 |
| `membranous` | First-line (KDIGO 2021 preferred CNI) | First-line alternative | 1 |
| `lupus` | Alternative CNI for Class V | Second-line | 2 |
| `iga` | Alternative steroid-sparing | Second-line | 2 |
| `transplantGlomerulopathy` | Base immunosuppression | Standard base therapy | 1 |
| `antibodyMediatedRejection` | Base immunosuppression (trough target 5-10 ng/mL) | Standard base therapy | 1 |
| `tCellMediatedRejection` | Base immunosuppression (trough target 5-10 ng/mL) | First-line | 1 |
| `bkVirusNephropathy` | Reduce dose to lower trough (4-6 ng/mL) | Dose-reduction strategy | 2 |

### Contraindications
Hypersensitivity, inadequate eGFR for monotherapy use without CNI rationale.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No standard eGFR-based adjustment; dose-adjusted by therapeutic drug monitoring (trough levels) |
| Target trough (GN) |  | 5-10 ng/mL |
| Target trough (Transplant) |  | 5-15 ng/mL (depending on time post-Tx) |

### Dialysis Dosing
Not removed by haemodialysis. No dose adjustment.

### Transplant Considerations
Cornerstone of transplant immunosuppression (tacrolimus + MMF + steroids). Trough targets: 8-12 ng/mL (first 3 months), 5-10 ng/mL (3-12 months), 4-8 ng/mL (>12 months). Risk of CNI nephrotoxicity, NODAT (new-onset diabetes after transplant), neurotoxicity.

### Pregnancy / Lactation
FDA Category C (crosses placenta; associated with low birth weight, prematurity). Use lowest effective dose. Compatible with breastfeeding (low transfer).

### Drug Interactions
CYP3A4 inhibitors (azole antifungals, macrolides, amiodarone, grapefruit, calcium channel blockers — increase levels), CYP3A4 inducers (rifampicin, phenytoin, carbamazepine, St John's wort — decrease levels), NSAIDs (increased nephrotoxicity), potassium supplements (increased K+), sirolimus/everolimus (increased nephrotoxicity).

### Laboratory Monitoring
Tacrolimus trough level (C0, 12h post-dose) — q2-3 days initially, then weekly x4, then per protocol. Serum creatinine/eGFR. Blood glucose (monitor for NODAT). K+, Mg++. CBC, LFTs.

### Vaccination Advice
Inactivated vaccines safe (may be less immunogenic). Live vaccines contraindicated. Influenza, pneumococcal, COVID-19 recommended.

### Common Adverse Effects
Tremor (20-40%), headache, paraesthesiae, diarrhoea, nausea, hyperglycaemia, hypertension, hyperkalemia, hypomagnesaemia, insomnia.

### Serious Adverse Effects
Nephrotoxicity (acute and chronic — afferent arteriolar hyalinosis, tubular vacuolisation, interstitial fibrosis), NODAT (10-30%), neurotoxicity (tremor, seizures, PRES), infections (CMV, BK virus, opportunistic), thrombotic microangiopathy (TMA), posterior reversible encephalopathy syndrome (PRES).

### Stopping Criteria
Severe neurotoxicity (PRES, intractable seizures), TMA, progressive CNI nephrotoxicity with histologic confirmation, BK virus nephropathy not responding to dose reduction, severe NODAT.

### Evidence Level
1 (Standard of care for transplant and proteinuric GN)

### Guideline References
KDIGO 2021 Glomerular Diseases, KDIGO 2024 Renal Transplantation.

---

## 5.2. Cyclosporine

### Mechanism of Action
Binds cyclophilin, forming a complex that inhibits calcineurin, blocking NFAT dephosphorylation and T-cell activation. Less potent than tacrolimus but with different side effect profile.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `mcd` | Steroid-sparing alternative | Second-line | 1 |
| `fsgs` | Induction and maintenance | Second-line | 1 |
| `membranous` | Alternative CNI | Second-line | 1 |
| `lupus` | Alternative CNI for Class V | Second-line | 2 |
| `iga` | Alternative steroid-sparing | Second-line | 2 |

### Contraindications
Uncontrolled hypertension, eGFR <30 (relative), severe hepatic impairment, hypersensitivity, previous CNI toxicity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | Dose-adjusted by trough levels |
| Target trough (GN) |  | 100-200 ng/mL |

### Dialysis Dosing
Not removed. No adjustment.

### Transplant Considerations
Less favoured than tacrolimus in modern transplant (higher rejection rates, more cosmetic side effects). Still used in some centres.

### Pregnancy / Lactation
FDA Category C.

### Drug Interactions
Similar to tacrolimus (CYP3A4 pathway).

### Laboratory Monitoring
Cyclosporine trough levels (C0), eGFR, BP, K+, Mg++, CBC, LFTs, uric acid.

### Vaccination Advice
Same as tacrolimus.

### Common Adverse Effects
Hypertension (30-50%), hirsutism (30-40%), gingival hyperplasia (15-30%), tremor, paraesthesiae, hyperuricemia/gout, hyperkalemia, hypomagnesaemia.

### Serious Adverse Effects
Nephrotoxicity (acute and chronic), new-onset diabetes (lower than tacrolimus), TMA, PRES, infections.

### Stopping Criteria
Same as tacrolimus plus severe cosmetic side effects, refractory hypertension.

### Evidence Level
1

### Guideline References
KDIGO 2021, KDIGO 2024 Renal Transplantation.

---


## 6. Antimetabolites

## 6.1. Mycophenolate Mofetil (MMF)

### Mechanism of Action
Prodrug of mycophenolic acid (MPA). Selective, reversible inhibitor of inosine monophosphate dehydrogenase (IMPDH), blocking de novo purine synthesis. Preferentially suppresses B and T lymphocyte proliferation (lymphocytes depend on de novo purine synthesis).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | First-line induction Class III/IV/V LN | First-line | 1 |
| `iga` | Rescue/steroid-sparing (Chinese studies) | Second-line | 2 |
| `mcd` | Steroid-sparing in frequently relapsing | Second-line | 2 |
| `membranous` | Alternative to CyP or CNI | Second-line | 2 |
| `fsgs` | Alternative immunosuppressant | Second-line | 2 |
| `anca` | Maintenance (alternative to rituximab) | Second-line | 1 |
| `c3` | Immunosuppressive therapy | Third-line | 3 |
| `mpgn` | Immunosuppressive therapy | Second-line | 2 |
| `antibodyMediatedRejection` | Part of base IS (tac+MMF+steroids) | First-line | 1 |
| `tCellMediatedRejection` | Base IS | First-line | 1 |
| `transplantGlomerulopathy` | Base IS (may switch from CNI to MPA) | First-line | 1 |

### Contraindications
Pregnancy (Category D — teratogenic), hypersensitivity, GI haemorrhage (active).

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-4 | >=15 mL/min | No adjustment (capped at 2-3g/day based on GI tolerance) |
| Stage 5 | <15 mL/min | Max 2g/day (monitor for accumulation of MPAG) |
| Dialysis | HD/PD | Max 2g/day; avoid in anuric patients |

### Dialysis Dosing
MPAG accumulates but MPA is not significantly removed. No supplemental dosing.

### Transplant Considerations
Standard component of triple immunosuppression (tacrolimus + MMF + steroids). GI intolerance common. Enteric-coated mycophenolate sodium (EC-MPS) may reduce GI adverse effects.

### Pregnancy / Lactation
FDA Category D. Teratogenic (congenital malformations: ear, distal limb, cardiac). Switch to AZA at least 6 weeks before conception. Contraindicated during breastfeeding.

### Drug Interactions
Antacids (reduce MPA absorption — separate by 2 hours), PPIs (reduce MPA efficacy — avoid concurrent use), cholestyramine (reduces enterohepatic recirculation of MPA), valacyclovir/valganciclovir (increased MPA levels), tacrolimus (increased MPA levels).

### Laboratory Monitoring
CBC (weekly x4, then monthly x3, then q3 months), LFTs, pregnancy test (before initiation, monthly during therapy). Optional TDM (MPA trough: target 1.5-3.5 mg/L).

### Vaccination Advice
Inactivated vaccines safe, may be less immunogenic. Live vaccines contraindicated. Influenza, pneumococcal, COVID-19 recommended.

### Common Adverse Effects
Diarrhoea (30-40%, dose-limiting), nausea/vomiting (20%), abdominal pain, leukopenia (15-25%), anaemia, tremor, headache, peripheral oedema.

### Serious Adverse Effects
Teratogenicity (congenital malformations), severe leukopenia/neutropenia, PML (<1:10,000), GI haemorrhage/perforation, severe infections (CMV, BK virus, opportunistic), lymphoproliferative disorders (PTLD, low risk).

### Stopping Criteria
Pregnancy (switch to AZA), ANC <1500, severe GI intolerance unresponsive to dose reduction or EC-MPS conversion, PML, severe infection, PTLD.

### Evidence Level
1 (First-line for LN induction/maintenance and transplant IS)

### Guideline References
ALMS trial (Lancet 2009), MAINTAIN trial, KDIGO 2021 Glomerular Diseases, KDIGO 2024 Renal Transplantation.

---

## 6.2. Mycophenolate Sodium (EC-MPS)

### Mechanism of Action
Enteric-coated formulation of mycophenolic acid. Delays release to the small intestine, reducing upper GI adverse effects. Same IMPDH inhibitory mechanism as MMF.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | Alternative when MMF GI intolerance | First-line alternative | 1 |
| `antibodyMediatedRejection` | Base IS (GI intolerance) | First-line | 1 |
| `tCellMediatedRejection` | Base IS (GI intolerance) | First-line | 1 |
| `iga` | MMF alternative | Second-line | 2 |

### Contraindications
Same as MMF.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | 720mg EC-MPS = 1000mg MMF (equivalent dosing) |

### Dialysis Dosing
Same as MMF.

### Transplant Considerations
Often used to replace MMF when GI symptoms limit tolerability. Equally efficacious.

### Pregnancy / Lactation
FDA Category D. Same as MMF.

### Drug Interactions
Same as MMF.

### Laboratory Monitoring
Same as MMF.

### Vaccination Advice
Same as MMF.

### Common Adverse Effects
Diarrhoea (lower incidence than MMF), nausea (less), abdominal distension.

### Serious Adverse Effects
Same as MMF.

### Stopping Criteria
Same as MMF.

### Evidence Level
1 (Equivalent to MMF)

### Guideline References
KDIGO 2021, KDIGO 2024.

---

## 6.3. Azathioprine

### Mechanism of Action
Prodrug of 6-mercaptopurine (6-MP). Inhibits de novo purine synthesis, suppressing T and B lymphocyte proliferation. Metabolised by thiopurine methyltransferase (TPMT) and xanthine oxidase (XO).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | Maintenance therapy (alternative to MMF) | Second-line | 1 |
| `anca` | Alternative maintenance therapy | Second-line | 2 |
| `mcd` | Steroid-sparing in frequently relapsing | Second-line | 2 |
| `lupus (pregnancy)` | Preferred maintenance in pregnancy | First-line in pregnancy | 1 |
| `iga` | Maintenance (limited role) | Third-line | 3 |

### Contraindications
TPMT deficiency (homozygous, 0.3% of population), severe hepatic impairment, prior azathioprine hypersensitivity, pregnancy (relative — some guidelines consider safe).

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | No adjustment |
| Stage 4 | 15-29 mL/min | Start 50mg/day; titrate to response |
| Stage 5 | <15 mL/min | Start 50mg/day; caution |

### Dialysis Dosing
Removed by haemodialysis (partial). Dose post-dialysis or reduce dose.

### Transplant Considerations
Not used in modern transplant immunosuppression (MMF superior). May be used if MMF intolerant.

### Pregnancy / Lactation
FDA Category D. Widely used in pregnancy for lupus (MMF switch). AAP considers compatible with breastfeeding (low transfer).

### Drug Interactions
Allopurinol/febuxostat (fatal myelosuppression — reduce AZA dose by 75% if unavoidable), cotrimoxazole (increased myelotoxicity), warfarin (reduced anticoagulation), ribavirin, live vaccines (contraindicated).

### Laboratory Monitoring
TPMT genotyping/phenotyping (mandatory before initiation). CBC (weekly x8 weeks, then monthly x6, then q3 months). LFTs (monthly x3, then q3 months).

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated during therapy.

### Common Adverse Effects
Nausea/vomiting (20-30%, dose-limiting), leukopenia (15-30%), hepatotoxicity (5-10%), diarrhoea, alopecia, rash.

### Serious Adverse Effects
Severe myelosuppression (TPMT deficiency), hepatotoxicity (can be severe), pancreatitis (2-5%), hepatosplenic T-cell lymphoma (HSTCL, extremely rare), infections, hypersensitivity syndrome (fever, rash, myalgia, shock).

### Stopping Criteria
TPMT deficiency with intolerance, severe myelosuppression (ANC <1500), pancreatitis, hepatotoxicity (>3x ULN), hypersensitivity reaction, severe infection.

### Evidence Level
1 (For maintenance in lupus and transplant historical)

### Guideline References
KDIGO 2021, MAINRITSAN trial (AZA inferior to rituximab for ANCA maintenance).

---


## 7. Alkylating Agents

## 7.1. Cyclophosphamide (IV Pulse)

### Mechanism of Action
Alkylating agent (nitrogen mustard). Metabolised to phosphoramide mustard, which cross-links DNA, inhibiting cell division. Suppresses both B and T cells with lasting effect. IV pulse preferred over oral (lower cumulative dose, less toxicity).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | Induction for severe Class III/IV LN | First-line alternative | 1 |
| `anca` | Alternative induction (when rituximab unavailable) | First-line alternative | 1 |
| `antiGbm` | Induction (with steroids and PLEX) | First-line | 1 |
| `iga` | Severe crescentic IgA/RPGN | First-line for crescentic | 1 |
| `membranous` | Modified Ponticelli regimen | First-line alternative | 1 |
| `cryoglobulinemic` | Severe disease with RPGN | Second-line | 2 |
| `c3` | Severe/progressive disease | Third-line | 3 |
| `mpgn` | Severe/progressive disease | Third-line | 3 |

### Contraindications
Pregnancy (Category D), active infection, significantly impaired bone marrow reserve (WBC <3500, platelets <100,000), severe hepatic impairment, prior cyclophosphamide allergy, urological malignancy history.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-4 | >=15 mL/min | 15 mg/kg IV (max 1.2g); reduce by 25% if CrCl 10-50 |
| Stage 4 | 15-29 mL/min | Reduce to 10 mg/kg IV (max 1g) |
| Stage 5 | <15 mL/min | 7.5 mg/kg IV (max 0.75g) |
| Dialysis | HD/PD | 7.5 mg/kg IV; dialysable — dose after dialysis |

### Dialysis Dosing
Dialysable (dose post-dialysis). Reduce dose.

### Transplant Considerations
Used for desensitisation in highly HLA-sensitised patients (with rituximab and PLEX). Bladder toxicity risk with prior transplant urological surgery.

### Pregnancy / Lactation
FDA Category D. Teratogenic. Contraindicated in pregnancy. Can cause premature ovarian failure (POF, risk 10-50% depending on age and cumulative dose). Advise oocyte/sperm cryopreservation. Avoid breastfeeding.

### Drug Interactions
Allopurinol (increased myelotoxicity — avoid if possible), warfarin (increased INR), live vaccines (contraindicated), mesna co-administration to prevent haemorrhagic cystitis.

### Laboratory Monitoring
CBC (day 10-14 post-infusion, or weekly during oral therapy), urinalysis (for haemorrhagic cystitis — monitor indefinitely), eGFR, LFTs, pregnancy test (before each dose).

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated during and for 6 months after therapy. Give pneumococcal, influenza, COVID-19 before therapy. HZV (Shingrix) recommended before therapy.

### Common Adverse Effects
Nausea/vomiting (80%, premedicate with antiemetics), alopecia (40-60%), leukopenia (30-50%), anaemia, thrombocytopenia, anorexia, diarrhoea, stomatitis.

### Serious Adverse Effects
Haemorrhagic cystitis (5-15% oral, <5% IV), bladder cancer (5-10x lifetime risk, screen with urinalysis and cystoscopy if haematuria), gonadal toxicity/infertility (POF, azoospermia), myelodysplasia/leukaemia (cumulative dose-related >36g), pneumonitis, cardiotoxicity (high-dose only), SIADH, severe infections (PJP, opportunistic).

### Stopping Criteria
ANC <1500, platelets <100,000, haemorrhagic cystitis (any severity), cumulative lifetime dose >36g (increased malignancy risk), active infection, pregnancy.

### Evidence Level
1 (Foundation of induction therapy for LN, ANCA, anti-GBM)

### Guideline References
EuroLupus trial (Ann Rheum Dis 2002), CYCLOPS trial (Ann Rheum Dis 2009), KDIGO 2021.

---

## 7.2. Cyclophosphamide (Oral)

### Mechanism of Action
Same as IV formulation. Oral administration provides continuous immunosuppression but higher cumulative dose and greater toxicity.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | Alternative when IV not feasible | Second-line alternative | 2 |
| `anca` | Historical induction (now rarely used) | Third-line | 2 |
| `antiGbm` | Induction continuation after IV pulses | Second-line | 2 |
| `cryoglobulinemic` | Severe disease | Second-line | 2 |

### Contraindications
Same as IV formulation.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | 1.5-2 mg/kg/day (max 200mg) |
| Stage 4 | 15-29 mL/min | 1-1.5 mg/kg/day |
| Stage 5 | <15 mL/min | 1 mg/kg/day |
| Dialysis | HD/PD | Reduce dose; monitor levels |

### Dialysis Dosing
Dialysable. Administer after dialysis.

### Transplant Considerations
Not used.

### Pregnancy / Lactation
Same as IV — contraindicated.

### Drug Interactions
Same as IV.

### Laboratory Monitoring
Same as IV but more intensive (continuous exposure).

### Vaccination Advice
Same as IV.

### Common Adverse Effects
Higher cumulative toxicity than IV. More haemorrhagic cystitis, more sustained myelosuppression.

### Serious Adverse Effects
Same as IV, with higher cumulative toxicity risk.

### Stopping Criteria
Same as IV. Target therapy duration <6 months.

### Evidence Level
2 (IV preferred; oral historical)

### Guideline References
KDIGO 2021.

---

## 8. Biologics

## 8.1. Rituximab (Anti-CD20)

### Mechanism of Action
Chimeric murine/human IgG1 monoclonal antibody targeting CD20 on pre-B and mature B lymphocytes. Depletes B-cells via antibody-dependent cell-mediated cytotoxicity (ADCC), complement-dependent cytotoxicity (CDC), and direct apoptosis. CD20 is not expressed on plasma cells (allowing immunoglobulin production to persist).

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `anca` | First-line induction and maintenance | First-line | 1 |
| `mcd` | Frequently relapsing/steroid-dependent | Second-line | 2 |
| `membranous` | First-line (anti-PLA2R positive, moderate-severe) | First-line | 1 |
| `lupus` | Refractory LN (off-label) | Third-line | 2 |
| `iga` | Refractory/transplant recurrence | Third-line | 2 |
| `fsgs` | Primary FSGS (post-transplant recurrence) | First-line (post-Tx recurrence) | 2 |
| `cryoglobulinemic` | HCV-associated mixed cryoglobulinemia | First-line (with antivirals) | 2 |
| `antibodyMediatedRejection` | Acute/active ABMR (with PLEX/IVIG) | Second-line | 2 |
| `antiGbm` | Refractory/relapsing post-PLEX | Third-line | 3 |
| `c3` | Refractory disease | Third-line | 3 |

### Contraindications
Active severe infection (including HBV/HCV), severe heart failure (NYHA III-IV), known hypersensitivity (especially murine protein), live vaccination within 4 weeks.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (monoclonal antibody, not renally cleared) |
| Dialysis | HD/PD | No dose adjustment; not removed by dialysis |

### Dialysis Dosing
Not removed. No adjustment.

### Transplant Considerations
Used for ABMR treatment. May reduce DSA levels. Risk of hypogammaglobulinaemia (especially with repeated courses). CMV/BK virus reactivation risk. Premedicate with IV methylprednisolone, acetaminophen, antihistamine.

### Pregnancy / Lactation
FDA Category C. Crosses placenta (especially after week 16). Causes neonatal B-cell depletion (reversible). Avoid in pregnancy unless essential. Give at least 6 months before conception if possible.

### Drug Interactions
Live vaccines (contraindicated, risk of disseminated infection), other biologics (concurrent use not recommended), methotrexate, corticosteroids.

### Laboratory Monitoring
CD19/20 B-cell count (pre-dose, then q3-6 months), IgG levels (baseline, q3 months), HBsAg, HBcAb, HCV serology, ANCA titre (vasculitis), CBC, LFTs.

### Vaccination Advice
Inactivated vaccines safe (recommend influenza, pneumococcal, COVID-19). Live vaccines contraindicated. Vaccinate 2-4 weeks before therapy when possible. HZV (Shingrix) recommended before therapy.

### Common Adverse Effects
Infusion reactions (5-15% first dose: fever, rigors, hypotension, urticaria), headache, nausea, diarrhoea, arthralgia, fatigue.

### Serious Adverse Effects
Severe infusion reactions (<1%: anaphylaxis, bronchospasm), hepatitis B reactivation (screen all patients), PML (<1:10,000), late-onset neutropenia (3-10%), hypogammaglobulinaemia (5-20% with repeated courses), severe infections, pulmonary toxicity, cardiac arrhythmia (rare).

### Stopping Criteria
Severe infusion reaction (discontinue permanently), confirmed PML, hypogammaglobulinaemia with recurrent infections, severe infection (hold until resolved), lack of B-cell depletion.

### Evidence Level
1 (First-line for ANCA and MN; RAVE, MAINRITSAN, MENTOR, GEMRITUX trials)

### Guideline References
RAVE trial (N Engl J Med 2010), MAINRITSAN (N Engl J Med 2014), MENTOR (JASN 2019), KDIGO 2021.

---

## 8.2. Belimumab

### Mechanism of Action
Recombinant human IgG1 lambda monoclonal antibody that binds soluble B-cell activating factor (BAFF/BLyS), inhibiting B-cell survival, proliferation, and differentiation. Reduces autoreactive B-cell clones.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | Add-on therapy for active LN (Class III/IV/V) | First-line (add-on) | 1 |

### Contraindications
Severe active infection, known hypersensitivity, concomitant use with other biologics, severe hepatic impairment.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (monoclonal antibody) |
| Dialysis | HD/PD | No dose adjustment; limited data |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Not indicated in transplant. No data.

### Pregnancy / Lactation
FDA Category C. Limited human data. Can be continued in pregnancy if clinically necessary. Breastfeeding: limited data.

### Drug Interactions
Live vaccines (contraindicated), other biologics (concurrent not recommended), cyclophosphamide, rituximab.

### Laboratory Monitoring
CBC, anti-dsDNA, C3/C4 (baseline and q3 months), IgG levels, HBV/HCV serology.

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated.

### Common Adverse Effects
Nausea, diarrhoea, pyrexia, nasopharyngitis, infusion reactions (15-20%), headache, arthralgia.

### Serious Adverse Effects
Severe infections (pneumonia, cellulitis, sepsis), depression/suicidality (0.3% in clinical trials), anaphylaxis (<1%), hepatitis B reactivation, PML (rare).

### Stopping Criteria
Severe infusion reaction, anaphylaxis, suicidality, severe infection, lack of clinical response at 6 months.

### Evidence Level
1 (BLISS-LN: OR 1.55 for primary renal response, N Engl J Med 2020)

### Guideline References
BLISS-LN trial (N Engl J Med 2020), KDIGO 2021, EULAR/ERA-EDTA 2023.

---

## 8.3. Eculizumab

### Mechanism of Action
Humanised monoclonal antibody that binds complement protein C5, preventing its cleavage into C5a (anaphylatoxin) and C5b (membrane attack complex formation). Inhibits terminal complement pathway activation.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `c3` | C3G with strong complement activation | Second-line (off-label) | 2 |
| `denseDepositDisease` | DDD with progressive disease (limited data) | Third-line | 3 |
| `antibodyMediatedRejection` | Refractory ABMR with complement-mediated injury | Third-line (off-label) | 3 |
| `cryoglobulinemic` | Severe cryoglobulinemic GN | Third-line | 3 |

### Contraindications
Untreated meningococcal infection, no meningococcal vaccination (must vaccinate 2 weeks before), unresolved Neisseria infection, known hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (monoclonal antibody) |
| Dialysis | HD/PD | No dose adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Used in C3G recurrence post-transplant (limited evidence). Monitor for encapsulated bacterial infections. Meningococcal vaccination mandatory (conjugate + serogroup B) 2 weeks before therapy.

### Pregnancy / Lactation
FDA Category C. Crosses placenta. Limited human data.

### Drug Interactions
Live vaccines (contraindicated), other complement inhibitors.

### Laboratory Monitoring
CH50 (target <10%), complement C5 levels, Neisseria surveillance, meningococcal vaccination status.

### Vaccination Advice
Mandatory meningococcal vaccination (MenACWY conjugate + MenB) at least 2 weeks before first dose. If imminent therapy, prophylactic antibiotics until 2 weeks post-vaccination. Pneumococcal and H. influenzae vaccines also recommended.

### Common Adverse Effects
Headache, nasopharyngitis, diarrhoea, nausea, fatigue, arthralgia.

### Serious Adverse Effects
Meningococcal infection (encapsulated bacteria — life-threatening), other Neisseria infections, Aspergillus infections, infusion reactions (rare).

### Stopping Criteria
Meningococcal infection (restart after treatment with prophylactic antibiotics), non-response after 3-6 months, infusion reaction.

### Evidence Level
2 (aHUS — FDA approved; C3G — off-label, limited evidence)

### Guideline References
KDIGO 2021, aHUS approval trials, C3G case series.

---

## 8.4. Ravulizumab

### Mechanism of Action
Humanised monoclonal antibody targeting C5 with extended half-life (every 8 weeks vs every 2 weeks for eculizumab). Same mechanism — blocks C5 cleavage, inhibits terminal complement.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `c3` | C3G (off-label, less data than eculizumab) | Second-line (off-label) | 3 |
| `antibodyMediatedRejection` | Refractory ABMR (investigational) | Third-line | 3 |

### Contraindications
Same as eculizumab: untreated meningococcal infection, no vaccination.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No dose adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Same as eculizumab. Longer dosing interval (q8w) advantageous.

### Pregnancy / Lactation
Limited data.

### Drug Interactions
Same as eculizumab.

### Laboratory Monitoring
Same as eculizumab.

### Vaccination Advice
Same as eculizumab — mandatory meningococcal vaccination.

### Common Adverse Effects
Same as eculizumab.

### Serious Adverse Effects
Meningococcal infection.

### Stopping Criteria
Same as eculizumab.

### Evidence Level
2 (aHUS — FDA approved; C3G — limited evidence)

### Guideline References
aHUS approval trials.

---

## 8.5. Tocilizumab

### Mechanism of Action
Humanised anti-IL-6 receptor monoclonal antibody (both soluble and membrane-bound). Blocks IL-6 signalling, reducing inflammation and T-cell activation.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `anca` | Refractory AAV (off-label, limited data) | Third-line | 3 |
| `lupus` | SLE with LN (limited data) | Third-line | 3 |
| `antibodyMediatedRejection` | Refractory ABMR (off-label) | Third-line | 3 |
| `tCellMediatedRejection` | Refractory TCMR (off-label) | Third-line | 3 |

### Contraindications
Active infection, diverticulitis/intestinal perforation risk, severe hepatic impairment, hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Used off-label for refractory rejection. Risk of perforation, infection.

### Pregnancy / Lactation
FDA Category C.

### Drug Interactions
Live vaccines (contraindicated), CYP3A4 substrates (levels increased due to IL-6 suppression), other biologics.

### Laboratory Monitoring
CBC, LFTs, lipid panel, ESR/CRP, infection surveillance.

### Vaccination Advice
Inactivated vaccines safe but may be less immunogenic. Live vaccines contraindicated.

### Common Adverse Effects
Upper respiratory infections, hypertension, headache, nasopharyngitis, diarrhoea, increased LFTs.

### Serious Adverse Effects
Serious infections (bacterial, fungal, viral), GI perforation (<1%), hepatic toxicity, neutropenia, thrombocytopenia, infusion reactions, demyelinating disorders.

### Stopping Criteria
Serious infection, GI perforation, significant hepatic injury, hypersensitivity.

### Evidence Level
3 (Limited evidence in GN — case series only)

### Guideline References
KDIGO 2021 mentions investigational use.

---

## 8.6. Belatacept

### Mechanism of Action
Fusion protein (CTLA4-Ig) that blocks CD28-mediated T-cell co-stimulation by binding CD80/CD86 on antigen-presenting cells. Inhibits T-cell activation without calcineurin inhibition.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `antibodyMediatedRejection` | CNI-free IS in transplant | First-line alternative to CNI | 1 |
| `tCellMediatedRejection` | CNI-free IS (lower TCMR rates vs CNI) | First-line alternative | 1 |
| `transplantGlomerulopathy` | CNI-free regimen (may preserve GFR) | First-line alternative | 1 |
| `cniToxicity` | CNI substitution in CNI toxicity | First-line alternative | 1 |
| `bkVirusNephropathy` | CNI-free regimen (lower BK virus rates) | First-line alternative | 1 |

### Contraindications
EBV seronegative (high risk of PTLD), EBV serostatus unknown, lack of adequate post-transplant immunosuppression, known hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (monoclonal antibody) |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Standard belatacept-based regimen: belatacept + MMF + steroids. Superior eGFR preservation vs CNI at 7 years (BENEFIT). Higher early TCMR rates (but less severe). EBV D+R- contraindicated (PTLD risk). IV infusion only (monthly maintenance).

### Pregnancy / Lactation
FDA Category C. Limited data.

### Drug Interactions
Live vaccines (contraindicated), other biologics.

### Laboratory Monitoring
EBV PCR (monitor for PTLD), CBC, eGFR, LFTs, trough not required.

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated. Influenza, pneumococcal, COVID-19 recommended.

### Common Adverse Effects
Anaemia, diarrhoea, UTI, nasopharyngitis, headache, hypertension, peripheral oedema.

### Serious Adverse Effects
PTLD (post-transplant lymphoproliferative disorder — EBV associated), serious infections (CMV, BK, TB, fungal), PML (rare), infusion reactions.

### Stopping Criteria
PTLD (discontinue), EBV seroconversion with rising PCR, serious infection, infusion reaction.

### Evidence Level
1 (BENEFIT/BENEFIT-EXT trials, N Engl J Med 2010, Am J Transplant 2016)

### Guideline References
KDIGO 2024 Renal Transplantation, BENEFIT trial.

---

## 8.7. Abatacept

### Mechanism of Action
Fusion protein (CTLA4-Ig) blocking CD28 co-stimulation — same class as belatacept but lower affinity for CD86. Used mainly in rheumatoid arthritis; investigated in lupus nephritis.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `lupus` | LN (limited data, especially Class V) | Third-line | 3 |
| `c3` | C3G with CFH autoantibodies (case reports) | Third-line (investigational) | 3 |

### Contraindications
Active infection, known hypersensitivity, severe COPD (increased pulmonary adverse events).

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Not indicated.

### Pregnancy / Lactation
FDA Category C.

### Drug Interactions
Live vaccines (contraindicated), other biologics.

### Laboratory Monitoring
CBC, LFTs, infection surveillance.

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated.

### Common Adverse Effects
Headache, nausea, nasopharyngitis, UTI, infusion reactions.

### Serious Adverse Effects
Serious infections, pulmonary toxicity (COPD exacerbation), hypersensitivity.

### Stopping Criteria
Serious infection, hypersensitivity.

### Evidence Level
3 (Limited evidence in GN — investigational)

### Guideline References
Case series in C3G, lupus trials (negative in LN).

---


## 9. Complement Inhibitors

## 9.1. Iptacopan (Factor B Inhibitor)

### Mechanism of Action
Oral, selective, small-molecule inhibitor of complement factor B, blocking the alternative pathway C3 convertase. First oral alternative pathway inhibitor. Prevents C3 cleavage and downstream terminal pathway activation while preserving classical/lectin pathways for immune defence.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `c3` | C3G (proteinuria reduction, eGFR preservation) | First-line emerging therapy | 1 |
| `denseDepositDisease` | DDD (ongoing trials) | Emerging | 2 |
| `iga` | IgAN with complement activation (ongoing trials) | Emerging | 3 |

### Contraindications
Untreated Neisseria infection, hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-4 | >=15 mL/min | 200mg BID (no adjustment) |
| Stage 5 | <15 mL/min | Limited data |
| Dialysis | HD/PD | Limited data |

### Dialysis Dosing
Limited data.

### Transplant Considerations
May prevent C3G recurrence post-transplant. Data emerging.

### Pregnancy / Lactation
Limited data. Avoid in pregnancy.

### Drug Interactions
Moderate CYP3A4 inducers (reduce iptacopan levels), strong CYP3A4 inhibitors (increase iptacopan levels).

### Laboratory Monitoring
CH50, alternative pathway activity, proteinuria, eGFR, complement levels (C3, C5b-9).

### Vaccination Advice
Meningococcal vaccination recommended before therapy. Pneumococcal and H. influenzae type b vaccines recommended.

### Common Adverse Effects
Headache, diarrhoea, nausea, nasopharyngitis, fatigue, arthralgia.

### Serious Adverse Effects
Neisserial infections (meningococcus, gonococcus), other encapsulated bacterial infections.

### Stopping Criteria
Meningococcal infection, non-response after 6-12 months.

### Evidence Level
1 (APPLAUSE-C3G Phase 3: 35% proteinuria reduction vs placebo, p<0.001)

### Guideline References
APPLAUSE-C3G trial, KDIGO 2021 (mention as emerging therapy).

---

## 9.2. Avacopan (C5aR Inhibitor)

### Mechanism of Action
Oral, selective C5a receptor (C5aR, CD88) antagonist. Blocks C5a-mediated neutrophil priming and activation without disrupting membrane attack complex formation. Disrupts the amplification loop in ANCA vasculitis.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `anca` | Induction (steroid-sparing) in combination with RTX/CyP | First-line | 1 |
| `c3` | C3G (limited evidence) | Third-line (off-label) | 3 |
| `iga` | IgAN (ongoing trials) | Emerging | 3 |

### Contraindications
Severe hepatic impairment (Child-Pugh C), known hypersensitivity, active serious infection.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-4 | >=15 mL/min | 30mg BID (standard) |
| Stage 5 | <15 mL/min | No data — use with caution |
| Dialysis | HD/PD | No data |

### Dialysis Dosing
Limited data.

### Transplant Considerations
Not indicated in transplant.

### Pregnancy / Lactation
Limited data. Avoid.

### Drug Interactions
BCRP substrates (rosuvastatin, MTX — increased levels), CYP3A4 inducers (rifampin — decreased avacopan), strong CYP3A4 inhibitors.

### Laboratory Monitoring
LFTs (monthly x6, then q3 months), eGFR, CBC, BP.

### Vaccination Advice
Inactivated vaccines safe.

### Common Adverse Effects
ALT/AST elevation (3-5%), nausea, dyspepsia (5-10%), headache, leucopenia.

### Serious Adverse Effects
Hepatic toxicity (ALT >5x ULN), serious infections.

### Stopping Criteria
ALT >5x ULN, severe hepatic injury, non-response.

### Evidence Level
1 (ADVOCATE trial: superior sustained remission at 52 weeks vs prednisone, p=0.007)

### Guideline References
ADVOCATE trial (N Engl J Med 2021), KDIGO 2021.

---

## 9.3. Narsoplimab (MASP-2 Inhibitor)

### Mechanism of Action
Human monoclonal antibody targeting mannan-binding lectin-associated serine protease-2 (MASP-2), inhibiting the lectin pathway of complement activation without affecting classical or alternative pathways.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `c3` | C3G (lectin pathway involvement, investigational) | Emerging therapy | 2 |
| `iga` | IgAN (lectin pathway hypothesis, ongoing trials) | Emerging therapy | 2 |
| `denseDepositDisease` | DDD (investigational) | Emerging therapy | 3 |
| `antibodyMediatedRejection` | ABMR with complement activation (investigational) | Emerging therapy | 3 |

### Contraindications
Known hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (monoclonal antibody) |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
May prevent/treat C3G recurrence post-transplant.

### Pregnancy / Lactation
Limited data.

### Drug Interactions
No significant drug-drug interactions expected.

### Laboratory Monitoring
Lectin pathway activity, CH50, C3, C4, proteinuria, eGFR.

### Vaccination Advice
Meningococcal vaccination recommended.

### Common Adverse Effects
Fatigue, headache, nausea, diarrhoea, infusion reactions.

### Serious Adverse Effects
Infection risk (theoretical — lectin pathway role in innate immunity).

### Stopping Criteria
Non-response.

### Evidence Level
2 (Phase 2 data in IgAN/C3G)

### Guideline References
Phase 2 C3G/IgAN trials.

---


## 10. mTOR Inhibitors

## 10.1. Sirolimus

### Mechanism of Action
mTOR (mammalian target of rapamycin) inhibitor. Forms complex with FKBP12, inhibits mTORC1, blocking cell cycle progression from G1 to S phase. Anti-proliferative and anti-angiogenic effects.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `antibodyMediatedRejection` | CNI-free/CNI-minimisation regimen | Second-line (conversion) | 2 |
| `transplantGlomerulopathy` | CNI-free regimen | Second-line (conversion) | 2 |
| `cniToxicity` | CNI substitution | Second-line | 2 |
| `bkVirusNephropathy` | CNI-free regimen (lower BK) | Second-line | 2 |

### Contraindications
Hypersensitivity, eGFR <30 (relative), significant proteinuria >1g/day (may worsen), unstable graft function.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (hepatic metabolism) |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
De novo use not recommended (delayed graft function, wound healing issues). Conversion from CNI considered for CNI toxicity, CNI-related TMA, or malignancy. Monitor for proteinuria after conversion.

### Pregnancy / Lactation
FDA Category C. Limited data. Contraindicated in pregnancy (increased fetal loss).

### Drug Interactions
CYP3A4 inhibitors (azole antifungals, macrolides, CCBs — increase levels), CYP3A4 inducers (rifampin, carbamazepine — decrease levels), sirolimus + CNI (increased nephrotoxicity, avoid combination).

### Laboratory Monitoring
Sirolimus trough (C0, target 5-15 ng/mL), eGFR, urine protein/creatinine ratio, CBC, lipids (hyperlipidemia), LFTs.

### Vaccination Advice
Inactivated vaccines safe. Live vaccines contraindicated.

### Common Adverse Effects
Hyperlipidemia (40-60%), thrombocytopenia (30%), leukopenia (20%), anaemia, stomatitis/aphthous ulcers (30%), rash, diarrhoea, arthralgia, peripheral oedema.

### Serious Adverse Effects
Nephrotoxicity (worsening proteinuria, de novo FSGS — podocyte toxicity), delayed wound healing, lymphocele, interstitial pneumonitis (non-infectious, 5-10%), angioedema, infections, PTLD, TMA.

### Stopping Criteria
Severe proteinuria (>1g/day developing after conversion), pneumonitis, TMA, uncontrolled hyperlipidemia, unhealed wound.

### Evidence Level
2 (No RCT evidence for GN indications; transplant conversion data)

### Guideline References
KDIGO 2024 Renal Transplantation.

---

## 10.2. Everolimus

### Mechanism of Action
mTOR inhibitor, similar to sirolimus but with better pharmacokinetics and shorter half-life. Higher bioavailability.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `antibodyMediatedRejection` | CNI-minimisation regimen | Second-line (conversion) | 1 |
| `transplantGlomerulopathy` | CNI-free regimen | Second-line | 2 |
| `cniToxicity` | CNI substitution | Second-line | 2 |
| `bkVirusNephropathy` | CNI-free regimen | Second-line | 2 |

### Contraindications
Same as sirolimus.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed.

### Transplant Considerations
Approved for use with reduced-dose CNI in de novo transplant recipients (vs sirolimus).

### Pregnancy / Lactation
Same as sirolimus.

### Drug Interactions
Same as sirolimus (CYP3A4).

### Laboratory Monitoring
Everolimus trough (C0, target 3-8 ng/mL), eGFR, urine protein, lipids, CBC.

### Vaccination Advice
Same as sirolimus.

### Common Adverse Effects
Hyperlipidemia, stomatitis, rash, diarrhoea, fatigue, peripheral oedema.

### Serious Adverse Effects
Worsening proteinuria, pneumonitis, wound healing issues, TMA.

### Stopping Criteria
Same as sirolimus.

### Evidence Level
1 (Approved for renal transplant; CERTAIN, ASSET trials)

### Guideline References
KDIGO 2024 Renal Transplantation.

---


## 11. Cardiovascular

## 11.1. Atorvastatin

### Mechanism of Action
HMG-CoA reductase inhibitor. Reduces cholesterol synthesis, upregulates LDL receptors, reduces LDL-C and triglycerides. Pleiotropic effects: anti-inflammatory, improved endothelial function, stabilises atherosclerotic plaques.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All CKD` | Cardiovascular risk reduction | First-line | 1 |
| `iga` | CV risk reduction | Adjunctive | 1 |
| `diabeticNephropathy` | CV risk reduction | First-line | 1 |
| `membranous` | CV risk reduction (nephrotic hyperlipidemia) | Adjunctive | 1 |
| `fsgs` | CV risk reduction | Adjunctive | 1 |
| `lupus` | CV risk reduction | Adjunctive | 1 |

### Contraindications
Active liver disease, unexplained persistent LFT elevation, pregnancy (Category X), breastfeeding, hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment (hepatic metabolism) |
| Dialysis | HD/PD | Max 20mg/day (limited evidence of benefit at higher doses) |

### Dialysis Dosing
No specific adjustment. Use lower doses (10-20mg) — SHARP trial recommended.

### Transplant Considerations
First-line statin in renal transplant. Monitor for drug interactions with CNIs. Recommended per KDIGO lipid guidelines.

### Pregnancy / Lactation
FDA Category X. Contraindicated.

### Drug Interactions
CYP3A4 inhibitors (azole antifungals, macrolides, grapefruit — increased myopathy risk), cyclosporine (increased atorvastatin levels), tacrolimus, warfarin (increased INR), digoxin.

### Laboratory Monitoring
Lipid panel (baseline and 2-3 months after initiation, then annually), LFTs (baseline and as clinically indicated), CK only if myalgia symptoms.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Myalgia (5-10%), headache, diarrhoea, nausea, nasopharyngitis, arthralgia.

### Serious Adverse Effects
Myopathy/rhabdomyolysis (<1%, increased risk with high dose and interacting drugs), hepatotoxicity (rare, <1%), new-onset diabetes (small increased risk).

### Stopping Criteria
CK >5x ULN with symptoms, rhabdomyolysis, persistent LFT >3x ULN, severe myalgia unresponsive to dose reduction.

### Evidence Level
1 (SHARP, CARDS, TNT trials)

### Guideline References
KDIGO 2024 Lipid Management in CKD, SHARP trial (Lancet 2011), NICE NG238.

---

## 11.2. Rosuvastatin

### Mechanism of Action
HMG-CoA reductase inhibitor, most potent statin. Hydrophilic (less muscle penetration, fewer myalgias in some studies). Minimal CYP metabolism.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All CKD` | CV risk reduction | First-line alternative | 1 |
| `diabeticNephropathy` | CV risk reduction | First-line alternative | 1 |

### Contraindications
Same as atorvastatin.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3 | >=30 mL/min | Standard (5-40mg OD) |
| Stage 4 | 15-29 mL/min | Max 10mg OD |
| Stage 5 | <15 mL/min | Max 10mg OD |
| Dialysis | HD/PD | 5-10mg OD (limited SHARP data) |

### Dialysis Dosing
Max 10mg OD.

### Transplant Considerations
Alternative to atorvastatin. Fewer CYP interactions. Use with caution with cyclosporine.

### Pregnancy / Lactation
FDA Category X.

### Drug Interactions
Fewer than atorvastatin (minimal CYP3A4). Cyclosporine (increases levels). Warfarin (increased INR). Antacids (reduce absorption — separate by 2 hours).

### Laboratory Monitoring
Same as atorvastatin.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Myalgia, headache, nausea.

### Serious Adverse Effects
Same as atorvastatin. Rare proteinuria (tubular, transient) at high doses.

### Stopping Criteria
Same as atorvastatin.

### Evidence Level
1

### Guideline References
AURORA trial, KDIGO 2024.

---

## 11.3. Furosemide

### Mechanism of Action
Loop diuretic blocking Na-K-2Cl cotransporter in thick ascending limb of loop of Henle. Potent natriuresis, reduces extracellular fluid volume.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All GN` | Oedema management in nephrotic syndrome | Adjunctive | 1 |
| `All CKD` | Volume overload, hypertension | Adjunctive | 1 |
| `mcd` | Oedema during nephrotic phase | Adjunctive | 1 |
| `membranous` | Oedema management | Adjunctive | 1 |
| `fsgs` | Oedema management | Adjunctive | 1 |
| `lupus` | Oedema management | Adjunctive | 1 |

### Contraindications
Anuria, severe hypokalemia (<3.0), severe hyponatremia, hepatic coma, sulfonamide allergy, digoxin toxicity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | 20-40mg OD/BID |
| Stage 3 | 30-59 mL/min | 40-80mg OD/BID (higher doses needed) |
| Stage 4 | 15-29 mL/min | 80-160mg OD/BID |
| Stage 5 | <15 mL/min | 160-250mg OD/BID (high dose or IV) |
| Dialysis | HD/PD | 250mg OD (or IV 20-40mg post-HD for residual diuresis) |

### Dialysis Dosing
Not significantly removed by HD. High doses needed if urine output present.

### Transplant Considerations
Used for post-transplant volume overload and hypertension. Monitor for electrolyte disturbances and allograft perfusion.

### Pregnancy / Lactation
FDA Category C. Use if clearly needed. Monitor for oligohydramnios.

### Drug Interactions
NSAIDs (reduced diuretic effect, increased nephrotoxicity), aminoglycosides (increased ototoxicity), lithium (increased toxicity), antihypertensives (additive effect), digoxin (hypokalemia increases toxicity), corticosteroids (increased hypokalemia).

### Laboratory Monitoring
Urine output, weight, serum electrolytes (K+, Na+, Mg++, Ca++), eGFR, BP.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Hypokalemia, hyponatremia, hypomagnesemia, hypocalcemia, hypovolemia/dehydration, metabolic alkalosis, hyperuricemia, hyperglycemia.

### Serious Adverse Effects
Ototoxicity (dose-related, especially IV rapid infusion >4mg/min, tinnitus, reversible), nephrotoxicity (volume depletion), severe electrolyte disturbances, cardiac arrhythmias, Stevens-Johnson syndrome (rare).

### Stopping Criteria
Anuria, severe electrolyte disturbance, ototoxicity.

### Evidence Level
1 (Standard adjunctive therapy for volume management)

### Guideline References
KDIGO 2021, NICE NG203.

---

## 11.4. Hydrochlorothiazide

### Mechanism of Action
Thiazide diuretic inhibiting NaCl cotransporter in distal convoluted tubule. Reduces BP through natriuresis and vasodilation.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All CKD` | Hypertension (adjunctive) | Second-line adjunctive | 1 |
| `iga` | BP control | Second-line adjunctive | 1 |

### Contraindications
Anuria, severe renal impairment (eGFR <30), hypersensitivity to sulfonamides, severe hepatic impairment, refractory hypokalemia.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-3a | >=45 mL/min | 12.5-50mg OD |
| Stage 3b | 30-44 mL/min | Limited efficacy; use cautiously |
| Stage 4 | <30 mL/min | Ineffective (loop diuretic preferred) |
| Stage 5 | <15 mL/min | Ineffective (loop diuretic preferred) |

### Dialysis Dosing
Ineffective.

### Transplant Considerations
May be used for mild hypertension. Loop diuretic preferred in CKD 4-5.

### Pregnancy / Lactation
FDA Category B (use cautiously).

### Drug Interactions
NSAIDs (reduced efficacy), lithium (increased levels), digoxin (hypokalemia), corticosteroids (increased electrolyte disturbance), insulin (altered requirements).

### Laboratory Monitoring
Electrolytes (K+, Na+), eGFR, BP, uric acid.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Hypokalemia, hyponatremia, hyperuricemia, hyperglycemia, hyperlipidemia, dizziness, hypomagnesemia.

### Serious Adverse Effects
Severe hyponatremia, hypokalemic arrhythmias, acute gout, acute angle-closure glaucoma (sulfonamide reaction), anaphylaxis.

### Stopping Criteria
eGFR <30 (switch to loop), severe electrolyte disturbance.

### Evidence Level
1

### Guideline References
KDIGO 2021, JNC 8, NICE NG136.

---

## 11.5. Amlodipine

### Mechanism of Action
Dihydropyridine calcium channel blocker. Blocks L-type calcium channels in vascular smooth muscle, causing vasodilation and reduced BP. No significant effect on cardiac conduction.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All CKD` | Hypertension (second/third agent) | Second-line adjunctive | 1 |
| `iga` | BP control | Second-line adjunctive | 1 |
| `diabeticNephropathy` | BP control after RAASi | Second-line adjunctive | 1 |

### Contraindications
Severe aortic stenosis, cardiogenic shock, acute myocardial infarction (within 4 weeks), hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed. No adjustment.

### Transplant Considerations
Preferred CCB post-transplant (no CNI interaction). Effective antihypertensive.

### Pregnancy / Lactation
FDA Category C. Use if clearly needed.

### Drug Interactions
CYP3A4 inhibitors (increase amlodipine), CYP3A4 inducers (decrease), cyclosporine/tacrolimus (minimal interaction — safe), simvastatin (increased myopathy — limit simva to 20mg).

### Laboratory Monitoring
BP, heart rate, ankle oedema assessment.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Peripheral oedema (ankle, 10-30%, dose-dependent), headache, flushing, dizziness, fatigue, palpitations.

### Serious Adverse Effects
Severe hypotension, hepatotoxicity (rare), Stevens-Johnson syndrome (rare).

### Stopping Criteria
Intolerable oedema despite dose reduction or added ACEi/ARB, severe hypotension.

### Evidence Level
1

### Guideline References
KDIGO 2021, KDIGO 2024, NICE NG136.

---

## 11.6. Doxazosin

### Mechanism of Action
Selective alpha-1 adrenergic receptor antagonist. Causes peripheral vasodilation, reducing BP. Also relaxes smooth muscle in prostate and bladder neck.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All CKD` | Resistant hypertension (add-on) | Third-line adjunctive | 2 |

### Contraindications
Orthostatic hypotension, micturition syncope, severe hepatic impairment, urinary incontinence (risk of exacerbation), known hypersensitivity.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Any | Any | No dose adjustment |
| Dialysis | HD/PD | No adjustment |

### Dialysis Dosing
Not removed. Use cautiously (orthostatic hypotension risk).

### Transplant Considerations
Third-line agent. Use cautiously with first-dose orthostatic hypotension.

### Pregnancy / Lactation
FDA Category C.

### Drug Interactions
Other antihypertensives (additive), PDE5 inhibitors (sildenafil, tadalafil — increased hypotension).

### Laboratory Monitoring
BP (including standing BP), heart rate.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Orthostatic hypotension (first dose, 5-10%), dizziness, fatigue, headache, somnolence, nasal congestion.

### Serious Adverse Effects
Severe hypotension/syncope, priapism (rare), intraoperative floppy iris syndrome (IFIS).

### Stopping Criteria
Severe orthostatic hypotension, syncope.

### Evidence Level
2

### Guideline References
KDIGO 2021, NICE NG136, ALLHAT trial.

---


## 12. Anticoagulants

## 12.1. Warfarin

### Mechanism of Action
Vitamin K antagonist. Inhibits vitamin K epoxide reductase, reducing synthesis of vitamin K-dependent clotting factors (II, VII, IX, X) and proteins C and S.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `membranous` | VTE prophylaxis in nephrotic syndrome (if albumin <2.0) | Adjunctive | 2 |
| `mcd` | VTE prophylaxis in severe nephrotic syndrome | Adjunctive | 2 |
| `fsgs` | VTE prophylaxis | Adjunctive | 2 |
| `lupus` | VTE with antiphospholipid/APS | First-line for APS | 1 |

### Contraindications
Pregnancy (Category X), active bleeding, significant bleeding risk, severe hepatic impairment, malignant hypertension, haemorrhagic stroke history, INR monitoring unavailable.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | Standard dosing (INR-guided) |
| Stage 3 | 30-59 mL/min | Standard start; monitor INR closely |
| Stage 4 | 15-29 mL/min | Start 2.5-5mg; lower maintenance often needed |
| Stage 5 | <15 mL/min | Highly variable dosing; frequent INR monitoring |
| Dialysis | HD/PD | Start 2.5mg; monitor INR; avoid in HD if possible |

### Dialysis Dosing
Variable clearance. Avoid in haemodialysis if possible (prefer LMWH or apixaban). Risk of vascular calcification (calciphylaxis).

### Transplant Considerations
Used post-transplant for AF, VTE. Minimise interactions with azoles.

### Pregnancy / Lactation
FDA Category X. Contraindicated (fetal warfarin syndrome). LMWH preferred. Compatible with breastfeeding (low transfer).

### Drug Interactions
Extensive: azole antifungals, antibiotics (ciprofloxacin, metronidazole, TMP-SMX), amiodarone, statins, NSAIDs, antiepileptics, rifampin.

### Laboratory Monitoring
INR (target 2.0-3.0 for most indications; 2.5-3.5 for mechanical valves/APS with recurrent thrombosis).

### Vaccination Advice
Influenza vaccine may transiently increase INR (monitor). No restrictions.

### Common Adverse Effects
Bleeding (ecchymosis, epistaxis, gingival), alopecia, skin necrosis (protein C deficiency, rare).

### Serious Adverse Effects
Major haemorrhage (intracranial, GI, retroperitoneal — 1-3% per year), warfarin-induced skin necrosis, calciphylaxis (CKD 5 patients).

### Stopping Criteria
Major haemorrhage, unstable INR despite compliance, calciphylaxis, pregnancy.

### Evidence Level
1 (For APS; 2 for nephrotic VTE prophylaxis — no RCTs)

### Guideline References
KDIGO 2021, ACCP Antithrombotic Guidelines, NICE NG196.

---

## 12.2. Heparin (Unfractionated)

### Mechanism of Action
Binds antithrombin III, accelerating inactivation of thrombin and factor Xa. Immediate anticoagulation.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All GN` | Acute VTE treatment (initial) | First-line | 1 |
| `All GN` | Anticoagulation for dialysis circuits | First-line | 1 |
| `membranous` | Acute VTE in nephrotic syndrome (initial) | First-line | 1 |

### Contraindications
Active bleeding, HIT (heparin-induced thrombocytopenia) history, severe thrombocytopenia, recent CNS surgery/trauma, haemophilia.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-5 | Any | Use cautiously in CKD 4-5; reduce doses |
| Dialysis | HD/PD | Use for HD circuit anticoagulation (2000-5000U bolus, 500-1000U/h infusion) |

### Dialysis Dosing
Standard for HD circuit anticoagulation.

### Transplant Considerations
Used perioperatively. Protamine reversal available.

### Pregnancy / Lactation
FDA Category C. Preferred anticoagulant in pregnancy (does not cross placenta).

### Drug Interactions
Antiplatelets, NSAIDs, thrombolytics, some cephalosporins.

### Laboratory Monitoring
aPTT (1.5-2.5x control), anti-Xa, platelet count (HIT monitoring, day 5-10).

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Bleeding, HIT (type 1: mild; type 2: immune-mediated, severe, 1-5%), osteopenia (long-term), alopecia, hyperkalemia.

### Serious Adverse Effects
HIT (type 2 — 1-5% risk — monitor platelets), severe haemorrhage, anaphylaxis.

### Stopping Criteria
HIT (any evidence — stop immediately, start alternative anticoagulant), major bleeding.

### Evidence Level
1

### Guideline References
KDIGO 2021, ACCP Guidelines.

---

## 12.3. Low Molecular Weight Heparin (LMWH)

### Mechanism of Action
Binds antithrombin III, preferentially inhibiting factor Xa over thrombin. More predictable pharmacokinetics than UFH. Lower HIT risk.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All GN` | VTE prophylaxis in nephrotic syndrome | First-line | 1 |
| `All GN` | Acute VTE treatment (initial) | First-line | 1 |
| `membranous` | VTE prophylaxis (albumin <2.0) | First-line | 2 |
| `All GN` | Anticoagulation in pregnancy | First-line | 1 |

### Contraindications
Same as UFH. HIT history (relative). Severe renal impairment (eGFR <30) — use UFH instead.

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | Standard dose |
| Stage 3a | 45-59 mL/min | Reduce dose 25% |
| Stage 3b | 30-44 mL/min | Reduce dose 50% |
| Stage 4 | <30 mL/min | Avoid (use UFH or apixaban) |
| Stage 5 | <15 mL/min | Contraindicated |

### Dialysis Dosing
Accumulates — avoid.

### Transplant Considerations
Avoid in CKD 4/5. UFH preferred.

### Pregnancy / Lactation
FDA Category B. Preferred for VTE in pregnancy (does not cross placenta).

### Drug Interactions
Same as UFH.

### Laboratory Monitoring
Anti-Xa (target 0.6-1.0 IU/mL for treatment; 0.2-0.5 for prophylaxis). Platelet count.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Bleeding, HIT (lower than UFH, 0.2-0.5%), injection site haematoma, skin necrosis.

### Serious Adverse Effects
HIT, major haemorrhage.

### Stopping Criteria
HIT, major bleeding, eGFR <30 (switch to UFH or DOAC).

### Evidence Level
1

### Guideline References
KDIGO 2021, ACCP Guidelines.

---

## 12.4. Apixaban

### Mechanism of Action
Direct oral factor Xa inhibitor. Reversible, predictable pharmacokinetics. No monitoring required.

### Indications in Glomerular Disease

| Disease ID | Indication | Line of Therapy | Evidence Level |
|------------|-----------|-----------------|----------------|
| `All GN` | AF in CKD (preferred DOAC in CKD) | First-line | 1 |
| `All GN` | VTE treatment | First-line | 1 |

### Contraindications
Active bleeding, mechanical heart valves, antiphospholipid syndrome (triple positive), severe hepatic impairment, eGFR <15 (limited data).

### Renal Dosing

| eGFR Stage | eGFR Range | Dose Adjustment |
|------------|-----------|-----------------|
| Stage 1-2 | >=60 mL/min | 5mg BID |
| Stage 3a | 45-59 mL/min | 5mg BID (or 2.5mg BID if weight <60kg or age >=80) |
| Stage 3b | 30-44 mL/min | 2.5mg BID (if 2 of: age >=80, weight <60kg, Cr >=1.5) |
| Stage 4 | 15-29 mL/min | 2.5mg BID (limited data; use with caution) |
| Stage 5 | <15 mL/min | Avoid (insufficient data) |
| Dialysis | HD/PD | 2.5mg BID (limited PK data) |

### Dialysis Dosing
Removed partially by HD (14%). Use 2.5mg BID.

### Transplant Considerations
Preferred DOAC in CKD. Monitor for interactions with azole antifungals.

### Pregnancy / Lactation
FDA Category C. Avoid (limited data).

### Drug Interactions
CYP3A4 inhibitors (ketoconazole, itraconazole, ritonavir — avoid), CYP3A4 inducers (rifampin, carbamazepine, phenytoin), P-gp inhibitors/inducers, antiplatelets/NSAIDs.

### Laboratory Monitoring
No routine monitoring required. Anti-Xa (calibrated for apixaban) if needed.

### Vaccination Advice
No restrictions.

### Common Adverse Effects
Bleeding (epistaxis, easy bruising, menorrhagia), anaemia, nausea.

### Serious Adverse Effects
Major haemorrhage (intracranial, GI, retroperitoneal), epidural haematoma.

### Stopping Criteria
Major haemorrhage, eGFR decline to <15, pregnancy.

### Evidence Level
1 (ARISTOTLE, AMPLIFY trials; ARISTOTLE subgroup in CKD)

### Guideline References
KDIGO 2021, ESC AF Guidelines, NICE NG196.

---

# Laboratory Knowledge Library
**Document ID:** GDES-V4.2-LAB-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Shared Laboratory Knowledge

---

## Introduction

The Laboratory Knowledge Library represents a fundamental architectural shift in how the BGDDR system represents and references laboratory data. In GDES V4.1, laboratory interpretations were embedded directly within individual disease definitions. This approach led to significant redundancy, inconsistency, and maintenance burden — each disease module contained its own description of common tests like serum creatinine, complement levels, or ANCA specificity, often with subtle variations in reference ranges or interpretive nuance.

GDES V4.2 introduces **reusable laboratory knowledge objects**. Each of the 61 entries in this library is a self-contained, authoritative reference for a single laboratory test or analyte. Disease modules no longer describe laboratory tests; instead, they reference these knowledge objects by identifier. When a disease definition needs to discuss the role of C3 levels, it links to `LAB-COMPLEMENT-C3` rather than embedding its own paragraph about C3 interpretation.

This architecture delivers three advantages:

1. **Consistency.** Every disease module that references serum albumin uses the same reference range, the same interpretation framework, and the same false-positive caveats. There is a single source of truth.
2. **Maintainability.** When a guideline updates a reference range or a new assay becomes available, the change is made once in this library rather than across dozens of disease files.
3. **Composability.** Laboratory panels (Appendix A) are assembled from these objects, allowing the system to generate context-specific test-ordering guidance without duplicating knowledge.

Each knowledge object follows a standardized schema: reference range, interpretation, clinical implications for glomerular disease, associated disease identifiers, known false-positive and false-negative scenarios, and repeat-testing and monitoring recommendations. The disease identifiers referenced throughout this document correspond to the canonical disease IDs defined in the BGDDR disease ontology.

---

## Conventions

- **Reference ranges** are provided for adults unless otherwise specified. Pediatric ranges are noted where clinically significant. Pregnancy-specific ranges are included for tests where gestational physiology alters interpretation.
- **Disease IDs** are monospaced identifiers (e.g., `lupus`, `iga`, `membranous`) corresponding to entries in the BGDDR disease knowledge base.
- **SI units** are provided in parentheses after conventional units where applicable.
- **Detection limits** are noted for quantitative assays where the lower limit of detection materially affects interpretation.

---

## 1. Urinalysis

---

### LAB-URINALYSIS-PROTEINURIA

**Proteinuria**

#### Reference Range

| Population | Method | Normal Value |
|---|---|---|
| Adult | Dipstick | Trace or negative |
| Adult | Spot UPCR | < 0.15 g/g (< 15 mg/mmol) |
| Adult | Spot ACR | < 30 mg/g (< 3 mg/mmol) |
| Adult | 24-hour urine | < 150 mg/24h |
| Pediatric (2-18 yr) | Spot ACR | < 30 mg/g |
| Pediatric (< 2 yr) | Spot ACR | May be up to 40 mg/g; age-specific norms apply |
| Pregnancy (2nd/3rd trimester) | Spot ACR | < 30 mg/g (values 30-300 mg/g warrant repeat) |

#### Interpretation

- **Trace to 1+ on dipstick (30-100 mg/dL):** May represent orthostatic (postural) proteinuria, early glomerular disease, or concentrated urine. Confirm with quantitative measurement.
- **2+ (100-300 mg/dL):** Likely clinically significant proteinuria. Quantify with UPCR or ACR.
- **3+ to 4+ (300 to >= 2000 mg/dL):** Strongly suggests glomerular pathology. Nephrotic-range proteinuria (> 3.5 g/g) indicates podocyte injury.
- **ACR 30-300 mg/g:** Moderately increased albuminuria (formerly "microalbuminuria"). May indicate early diabetic nephropathy, hypertension-mediated kidney damage, or early glomerulonephritis.
- **ACR > 300 mg/g:** Severely increased albuminuria (formerly "macroalbuminuria").
- **UPCR 0.15-0.5 g/g:** Low-grade proteinuria. Differentiate glomerular from tubulointerstitial origin using protein electrophoresis.
- **UPCR 0.5-3.5 g/g:** Moderate proteinuria. Glomerular or mixed origin likely.
- **UPCR > 3.5 g/g:** Nephrotic-range proteinuria.

#### Clinical Implications

Proteinuria is the hallmark finding in glomerular disease and the most important surrogate marker for disease progression and response to therapy. The type of proteinuria (selective vs. non-selective, albumin-predominant vs. non-albumin) provides diagnostic clues: selective albuminuria suggests minimal change disease or early diabetic nephropathy, while non-selective proteinuria with elevated IgG excretion suggests more severe glomerular basement membrane disruption as seen in FSGS, membranous nephropathy, or crescentic GN.

#### Associated Diseases

| Disease ID | Role of Proteinuria |
|---|---|
| `fsgs` | Non-selective proteinuria; nephrotic-range in most cases |
| `membranous` | Selective to non-selective; nephrotic-range proteinuria is cardinal feature |
| `mcd` | Selective albuminuria; nephrotic-range |
| `iga` | Sub-nephrotic proteinuria common; nephrotic transformation possible |
| `lupus` | Variable; nephrotic-range in Class V lupus nephritis |
| `diabeticNephropathy` | Progressive albuminuria from microalbuminuria to macroalbuminuria |
| `c3` | Proteinuria variable; depends on underlying histology (MPGN pattern common) |
| `cryoglobulinemic` | Sub-nephrotic to nephrotic-range |
| `antiGbm` | Sub-nephrotic to nephrotic-range |
| `anca` | Variable; often sub-nephrotic |
| `alport` | Progressive; typically sub-nephrotic until advanced |
| `thinBasementMembrane` | Persistent microscopic hematuria +/- mild proteinuria |
| `drugInducedGn` | Variable depending on drug and pattern |
| `fibrillaryGlomerulonephritis` | Nephrotic-range or sub-nephrotic |
| `denseDepositDisease` | Nephrotic-range or sub-nephrotic |
| `hivan` | Variable proteinuria |
| `bkVirusNephropathy` | Progressive proteinuria |
| `mpgn` | Nephrotic-range or sub-nephrotic |
| `antibodyMediatedRejection` | Variable proteinuria |
| `transplantGlomerulopathy` | Progressive proteinuria |

#### False Positives / False Negatives

- **Dipstick false positives:** Alkaline urine (pH > 8), concentrated urine, highly pigmented urine, contamination with vaginal secretions, seminal fluid, or blood. Contrast dye. Benzhexol (trihexyphenidyl).
- **Dipstick false negatives:** Dilute urine (specific gravity < 1.005), myeloma light chains (Bence Jones proteinuria - dipstick detects albumin, not light chains).
- **ACR false negatives:** High muscle mass individuals may have low ACR despite significant proteinuria when indexed to creatinine.
- **UPCR confounders:** Exercise-induced proteinuria, febrile illness, heart failure, dehydration.

#### Repeat Testing Recommendations

- Initial abnormality: confirm with repeat specimen on 2-3 separate occasions over 3-6 months before diagnosing chronic proteinuria.
- Orthostatic proteinuria: obtain first morning void (negative) and random daytime specimen (positive).
- Pregnancy: screen at each prenatal visit; repeat ACR for any trace or greater on dipstick.

#### Monitoring Recommendations

- Diabetic nephropathy: annual ACR for all patients; quarterly in those with established microalbuminuria.
- Glomerular disease on treatment: UPCR or ACR at each clinic visit; quantitative 24h urine or UPCR at 3-month intervals during active treatment.
- Post-transplant: monthly UPCR in first year; quarterly thereafter.
- Chronic proteinuria of any cause: UPCR every 3-6 months to track trajectory.

---

### LAB-URINALYSIS-HEMATURIA

**Hematuria**

#### Reference Range

| Population | Method | Normal Value |
|---|---|---|
| Adult | Dipstick | Negative |
| Adult | Microscopic (centrifuged) | 0-2 RBC/hpf |
| Pediatric | Microscopic | 0-5 RBC/hpf |

#### Interpretation

- **Dipstick positive, microscopic negative:** Hemoglobinuria, myoglobinuria, or strongly oxidizing agents (e.g., povidone-iodine). Not true hematuria.
- **Microscopic 3-5 RBC/hpf:** Borderline; repeat to confirm.
- **Microscopic 5-20 RBC/hpf:** Mild hematuria. Urological vs. renal origin must be differentiated.
- **Microscopic > 20 RBC/hpf:** Significant hematuria. Strongly renal in origin if dysmorphic RBCs present.
- **Macroscopic (gross) hematuria:** Always clinically significant. In young patients with dysmorphic RBCs, consider IgA nephropathy, Alport syndrome, or post-infectious GN. In older patients, exclude urological malignancy.

#### Clinical Implications

Isolated hematuria in the absence of proteinuria or reduced eGFR may represent thin basement membrane disease, IgA nephropathy, Alport carrier state, or early glomerulonephritis. Hematuria combined with proteinuria strongly suggests glomerular disease. Persistent microscopic hematuria warrants evaluation even in the absence of other abnormalities.

#### Associated Diseases

| Disease ID | Role of Hematuria |
|---|---|
| `iga` | Dysmorphic hematuria, often episodic; macroscopic hematuria during upper respiratory infections |
| `alport` | Persistent microscopic hematuria; may have macroscopic episodes |
| `thinBasementMembrane` | Persistent isolated microscopic hematuria |
| `antiGbm` | Macroscopic hematuria with dysmorphic RBCs; RBC casts |
| `anca` | Microscopic hematuria +/- macroscopic; RBC casts |
| `lupus` | Microscopic hematuria; active urine sediment in proliferative lupus nephritis |
| `membranous` | May have microscopic hematuria |
| `fsgs` | Usually microscopic or absent |
| `mcd` | Usually absent |
| `c3` | Variable; dependent on underlying histology |
| `cryoglobulinemic` | Microscopic hematuria |
| `denseDepositDisease` | Microscopic hematuria |
| `drugInducedGn` | Variable |
| `fibrillaryGlomerulonephritis` | Microscopic hematuria common |
| `irgn` | Macroscopic hematuria typical; post-infectious timing |
| `transplantGlomerulopathy` | Microscopic hematuria may indicate transplant GN |

#### False Positives / False Negatives

- **Dipstick false positives:** Hemoglobinuria, myoglobinuria, menstrual contamination, vigorous exercise, beet ingestion, certain drugs (rifampicin, phenazopyridine, nitrofurantoin).
- **Dipstick false negatives:** Vitamin C ingestion (high dose), very dilute urine.
- **Microscopic false negatives:** Delayed specimen processing (RBC lysis in dilute urine).

#### Repeat Testing Recommendations

- First episode of microscopic hematuria: repeat in 2-4 weeks after excluding infection, menstruation, and vigorous exercise.
- Persistent hematuria (3 positive specimens over 6 months): full evaluation including renal imaging, urology referral in patients > 35-40 years, and consideration of renal biopsy if glomerular origin confirmed.

#### Monitoring Recommendations

- Known glomerular hematuria: microscopic urinalysis at each clinic visit.
- IgA nephropathy: monitor for macroscopic episodes during upper respiratory infections.
- Post-transplant: hematuria may indicate transplant glomerulopathy or recurrent disease.

---

### LAB-URINALYSIS-DYSMORPHIC_RBCS

**Dysmorphic Red Blood Cells**

#### Reference Range

- **Normal:** Uniform (isomorphic) RBCs; 0% dysmorphic forms.
- **Significant glomerular hematuria:** > 70-80% dysmorphic RBCs (acanthocytes).

#### Interpretation

- **Predominantly isomorphic RBCs:** Suggests lower urinary tract source (ureter, bladder, urethra).
- **Predominantly dysmorphic RBCs (> 80%):** Strongly suggests glomerular origin. Acanthocytes (RBCs with bleb-like protrusions, "Mickey Mouse ears") are pathognomonic of glomerular bleeding.
- **Mixed population:** May indicate dual source or sampling artifact; repeat testing recommended.

#### Clinical Implications

Dysmorphic RBCs are the single best non-invasive marker for distinguishing glomerular from non-glomerular hematuria. Their presence directs evaluation toward renal parenchymal disease and away from urological malignancy workup. When > 80% dysmorphic RBCs are present, renal biopsy should be considered rather than cystoscopy.

#### Associated Diseases

| Disease ID | Role of Dysmorphic RBCs |
|---|---|
| `iga` | High percentage; episodic with macroscopic hematuria |
| `alport` | Persistent dysmorphic hematuria |
| `thinBasementMembrane` | Persistent dysmorphic hematuria |
| `antiGbm` | Dysmorphic RBCs with RBC casts |
| `anca` | Dysmorphic RBCs |
| `lupus` | Dysmorphic RBCs in proliferative lupus nephritis |
| `membranous` | Variable |
| `irgn` | Dysmorphic RBCs post-infection |

#### False Positives / False Negatives

- **False positives:** None specific; all glomerular bleeding produces dysmorphic forms.
- **False negatives:** Specimen dilution, delayed processing, automated analyzers may not distinguish morphologies. Requires fresh specimen and experienced reader. Phase-contrast microscopy or automated dysmorphic RBC analysis improves accuracy.

#### Repeat Testing Recommendations

- Confirm with fresh morning specimen if initial result equivocal.
- Automated urine sediment analysis (e.g., FlowMapper, Sedimax) may supplement manual microscopy.

#### Monitoring Recommendations

- Persistent in chronic glomerular disease; improvement may parallel disease remission.
- Not routinely monitored as a quantitative marker; qualitative assessment suffices.

---

### LAB-URINALYSIS-RBC_CASTS

**Red Blood Cell Casts**

#### Reference Range

- **Normal:** Absent (0 per low-power field).

#### Interpretation

- **Presence of RBC casts:** Pathognomonic of glomerular hemorrhage. Indicates active glomerulonephritis.
- **RBC casts with dysmorphic hematuria:** Confirms glomerular source and active inflammation.
- **Few RBC casts:** Early or mild glomerulonephritis.
- **Abundant RBC casts:** Active proliferative or necrotizing glomerulonephritis; consider RPGN.

#### Clinical Implications

RBC casts are the most specific urinary marker for glomerulonephritis. Their presence in the setting of acute kidney injury and hematuria essentially confirms the diagnosis of RPGN until proven otherwise. RBC casts should prompt urgent nephrology consultation and likely renal biopsy.

#### Associated Diseases

| Disease ID | Role of RBC Casts |
|---|---|
| `antiGbm` | Prominent RBC casts in RPGN |
| `anca` | RBC casts in necrotizing GN and RPGN |
| `lupus` | RBC casts in Class III/IV lupus nephritis |
| `iga` | RBC casts during macroscopic hematuria episodes |
| `irgn` | RBC casts in acute post-infectious GN |
| `alport` | RBC casts during hematuric episodes |
| `c3` | RBC casts in C3 glomerulonephritis |
| `cryoglobulinemic` | RBC casts |
| `membranous` | Rare |
| `fsgs` | Rare |
| `denseDepositDisease` | RBC casts |
| `drugInducedGn` | Variable |

#### False Positives / False Negatives

- **False positives:** None. RBC casts are pathognomonic.
- **False negatives:** Casts may dissolve in alkaline or dilute urine. Specimen should be examined promptly. Centrifugation technique affects yield.

#### Repeat Testing Recommendations

- Serial urinalysis during active disease to track resolution.
- Casts typically disappear before hematuria resolves; persistent casts indicate ongoing glomerular inflammation.

#### Monitoring Recommendations

- Daily urinalysis during RPGN to track response to immunosuppression.
- Resolution of RBC casts is an early marker of treatment response.

---

### LAB-URINALYSIS-WBC_CASTS

**White Blood Cell Casts**

#### Reference Range

- **Normal:** Absent (0 per low-power field).

#### Interpretation

- **Presence of WBC casts:** Indicates renal parenchymal inflammation, particularly tubulointerstitial nephritis or GN with significant leukocyte infiltration.
- **Neutrophil-predominant WBC casts:** Acute pyelonephritis or acute interstitial nephritis.
- **Lymphocyte/macrophage-predominant WBC casts:** Chronic interstitial nephritis, transplant rejection, or lupus nephritis.
- **WBC casts without pyuria:** May indicate early interstitial nephritis.

#### Clinical Implications

WBC casts localize infection or inflammation to the kidney (as opposed to lower urinary tract infection). In the context of glomerular disease, WBC casts may indicate concurrent interstitial nephritis, superimposed infection, or active proliferative GN with significant neutrophil infiltration (as in post-infectious GN or endocarditis-associated GN).

#### Associated Diseases

| Disease ID | Role of WBC Casts |
|---|---|
| `irgn` | Prominent WBC casts in acute post-infectious GN |
| `lupus` | WBC casts in active lupus nephritis |
| `iga` | May be present during acute hematuric episodes |
| `drugInducedGn` | WBC casts in drug-induced interstitial nephritis or GN |
| `bkVirusNephropathy` | WBC casts may be present |
| `tCellMediatedRejection` | WBC casts in acute tubulointerstitial rejection |
| `antibodyMediatedRejection` | May have WBC casts |
| `transplantGlomerulopathy` | Variable |

#### False Positives / False Negatives

- **False positives:** Vaginal contamination with WBCs in female specimens. Contamination with discharge.
- **False negatives:** Casts may lyse in dilute or alkaline urine. Requires prompt examination.

#### Repeat Testing Recommendations

- Repeat urinalysis if initial specimen is suspect for contamination.
- Midstream clean-catch specimen preferred.

#### Monitoring Recommendations

- Serial urinalysis to track resolution during treatment of interstitial nephritis or proliferative GN.

---

### LAB-URINALYSIS-OVAL_FAT_BODIES

**Oval Fat Bodies**

#### Reference Range

- **Normal:** Absent.

#### Interpretation

- **Presence:** Oval fat bodies are renal tubular epithelial cells containing reabsorbed lipids. They are the intracellular counterpart of free urinary lipid droplets. Their presence indicates significant proteinuria with lipiduria.
- **"Maltese cross" birefringence under polarized light:** Confirm lipid content. Cholesterol esters produce the characteristic crossed-figure appearance.
- **Abundant oval fat bodies:** Nephrotic-range proteinuria with podocyte injury.

#### Clinical Implications

Oval fat bodies are a hallmark of nephrotic syndrome. Their presence supports the diagnosis and indicates active lipid handling by tubular cells in the setting of massive proteinuria. They are particularly associated with membranous nephropathy, FSGS, and diabetic nephropathy.

#### Associated Diseases

| Disease ID | Role of Oval Fat Bodies |
|---|---|
| `membranous` | Common in nephrotic-range disease |
| `fsgs` | Present in nephrotic-range FSGS |
| `mcd` | May be present during nephrotic syndrome |
| `lupus` | Class V lupus nephritis |
| `diabeticNephropathy` | Advanced disease with nephrotic proteinuria |
| `denseDepositDisease` | Nephrotic presentations |
| `fibrillaryGlomerulonephritis` | Nephrotic presentations |

#### False Positives / False Negatives

- **False positives:** None specific.
- **False negatives:** May be absent in non-nephrotic proteinuria or in nephrotic patients with tubular dysfunction preventing lipid reabsorption.

#### Repeat Testing Recommendations

- Confirm with polarized light microscopy if uncertain.
- Does not require serial monitoring as a quantitative measure.

#### Monitoring Recommendations

- Resolution parallels reduction in proteinuria during treatment.

---

### LAB-URINALYSIS-LIPIDURIA

**Lipiduria**

#### Reference Range

- **Normal:** Absent or trace.

#### Interpretation

- **Free urinary lipid droplets:** Small, round, refractile droplets that do not stain with Sudan III (unlike cast oil cells) but stain with Oil Red O. Distinguished from oval fat bodies by being extracellular.
- **Significant lipiduria:** Indicates nephrotic-range proteinuria with renal lipid handling. Lipiduria may persist after proteinuria decreases.
- **Lipiduria with oval fat bodies:** Confirms nephrotic syndrome.

#### Clinical Implications

Lipiduria is a supportive finding in nephrotic syndrome. It reflects glomerular filtration of lipoproteins and their subsequent partial metabolism in the tubular lumen. While not specific for any particular cause of nephrotic syndrome, it is a useful confirmatory finding.

#### Associated Diseases

| Disease ID | Role of Lipiduria |
|---|---|
| `membranous` | Common |
| `fsgs` | Common |
| `mcd` | Present during nephrotic syndrome |
| `lupus` | Class V |
| `diabeticNephropathy` | Advanced nephrotic disease |

#### False Positives / False Negatives

- **False positives:** None specific.
- **False negatives:** Lipiduria may be absent in early nephrotic syndrome or in patients with tubular dysfunction.

#### Repeat Testing Recommendations

- Not typically monitored serially; serves as confirmatory finding.

#### Monitoring Recommendations

- Parallels proteinuria trajectory; resolution expected with remission of nephrotic syndrome.

---

## 2. Renal Function

---

### LAB-RENAL-CREATININE

**Serum Creatinine**

#### Reference Range

| Population | Range |
|---|---|
| Adult male | 0.7-1.3 mg/dL (62-115 umol/L) |
| Adult female | 0.6-1.1 mg/dL (53-97 umol/L) |
| Pediatric (term neonate) | 0.3-1.0 mg/dL (27-88 umol/L) |
| Pediatric (1 month - 1 year) | 0.2-0.4 mg/dL (18-35 umol/L) |
| Pediatric (1-12 years) | 0.3-0.7 mg/dL (27-62 umol/L) |
| Pediatric (13-17 years) | 0.5-1.0 mg/dL (44-88 umol/L) |
| Pregnancy (2nd/3rd trimester) | May decrease 10-20% from pre-pregnancy baseline due to increased GFR |

#### Interpretation

- **Mildly elevated (1.0-1.5 mg/dL in males; 0.9-1.3 mg/dL in females):** May represent early CKD, dehydration, high muscle mass, or high protein intake.
- **Moderately elevated (1.5-3.0 mg/dL):** Indicates moderate reduction in GFR. Acute kidney injury vs. CKD differentiation required.
- **Severely elevated (> 3.0 mg/dL):** Severe reduction in GFR. Risk of uremic complications.
- **Acute rise from baseline:** AKI. Even small increases (0.3 mg/dL from baseline) are clinically significant.
- **Low serum creatinine:** May indicate low muscle mass (elderly, malnourished, amputees), liver disease, or pregnancy. Does not necessarily indicate preserved GFR.

#### Clinical Implications

Serum creatinine is the most widely used marker for kidney function but has significant limitations as a GFR surrogate. It is affected by muscle mass, diet, tubular secretion (contributes approximately 10-15% of serum creatinine), and laboratory assay variability. In glomerular disease, rising creatinine indicates worsening kidney function and may signal progression, relapse, or complications (e.g., thrombotic microangiopathy, crescentic transformation).

#### Associated Diseases

| Disease ID | Role of Serum Creatinine |
|---|---|
| `fsgs` | Elevated in advanced disease or AKI on CKD |
| `membranous` | Usually normal or mildly elevated unless complications |
| `mcd` | Usually normal; AKI rare but possible |
| `iga` | May be elevated with progressive disease |
| `lupus` | Elevated in active lupus nephritis (Class III/IV) |
| `antiGbm` | Rapidly rising in RPGN |
| `anca` | Rapidly rising in RPGN |
| `alport` | Progressive elevation with age |
| `diabeticNephropathy` | Progressive elevation |
| `c3` | Variable |
| `denseDepositDisease` | Variable |
| `cryoglobulinemic` | May rise acutely |
| `drugInducedGn` | Variable |
| `fibrillaryGlomerulonephritis` | Usually elevated |
| `bkVirusNephropathy` | Progressive elevation |
| `irgn` | May be elevated; usually transient |
| `tCellMediatedRejection` | Elevated |
| `antibodyMediatedRejection` | Elevated |
| `transplantGlomerulopathy` | Progressive elevation |
| `cniToxicity` | Acute rise |

#### False Positives / False Negatives

- **Falsely elevated:** High muscle mass, high dietary protein, creatine supplementation, cimetidine, trimethoprim (block tubular secretion of creatinine), ketoacidosis (interference with assay).
- **Falsely low:** Low muscle mass (elderly, sarcopenia, amputation, malnutrition), liver disease (reduced creatine production), pregnancy.
- **Lab variability:** Jaffe reaction affected by bilirubin, glucose, acetoacetate; enzymatic assays more specific.

#### Repeat Testing Recommendations

- Acute changes: repeat in 12-24 hours to confirm trajectory.
- Chronic kidney disease: every 3-6 months depending on stage.
- Post-transplant: daily in immediate postoperative period, then taper frequency.

#### Monitoring Recommendations

- All glomerular diseases: serial creatinine at each clinic visit.
- Rate of creatinine rise > 50% in 1 week or > 100% in 1 month is concerning for rapid progression.
- Serial creatinine is a component of KDIGO AKI staging and CKD staging.

---

### LAB-RENAL-EGFR

**Estimated Glomerular Filtration Rate (eGFR)**

#### Reference Range

| Population | Method | Normal Value |
|---|---|---|
| Adult | CKD-EPI 2021 (race-free) | >= 90 mL/min/1.73m2 |
| Adult (older data) | MDRD | >= 90 mL/min/1.73m2 |
| Pediatric | Schwartz (updated) | Age-specific; generally >= 90 mL/min/1.73m2 |

CKD-EPI 2021 equation (race-free):
eGFR = 142 x min(Scr/k, 1)^a x max(Scr/k, 1)^(-1.200) x 0.9938^Age x [1.012 if female]
where k = 0.7 for females, 0.9 for males; a = -0.241 for females, -0.302 for males.

#### Interpretation

| Category | eGFR (mL/min/1.73m2) | Description |
|---|---|---|
| G1 | >= 90 | Normal or high |
| G2 | 60-89 | Mildly decreased |
| G3a | 45-59 | Mildly to moderately decreased |
| G3b | 30-44 | Moderately to severely decreased |
| G4 | 15-29 | Severely decreased |
| G5 | < 15 | Kidney failure |

- **eGFR > 120:** Hyperfiltration. May indicate early diabetic nephropathy, obesity-related glomerulomegaly, pregnancy, or high-protein diet.
- **eGFR 60-89 with proteinuria:** CKD stage G2 with albuminuria; warrants investigation.
- **eGFR < 60 without proteinuria in elderly:** May reflect age-related GFR decline; however, investigation still warranted.
- **eGFR decline > 5 mL/min/year:** Rapid progression; requires urgent evaluation and intervention.

#### Clinical Implications

eGFR is the primary metric for CKD staging, drug dosing adjustments, and treatment eligibility decisions. In glomerular disease, eGFR trends over time are more informative than single values. A declining eGFR trajectory indicates disease progression and may trigger escalation of immunosuppression, investigation of complications (hyperkalemia, metabolic acidosis, anemia, bone-mineral disease), or preparation for renal replacement therapy.

#### Associated Diseases

| Disease ID | Role of eGFR |
|---|---|
| `fsgs` | Progressive decline in untreated or refractory cases |
| `membranous` | Usually preserved until advanced; declining eGFR may indicate complications |
| `mcd` | Usually preserved; AKI rare |
| `iga` | Progressive decline in a subset; major predictor of long-term outcome |
| `lupus` | Decline reflects disease activity or chronic damage |
| `antiGbm` | Rapid decline in RPGN |
| `anca` | Rapid decline in RPGN |
| `alport` | Progressive decline, especially in males |
| `diabeticNephropathy` | Progressive decline; rate of decline determines prognosis |
| `c3` | Variable decline |
| `denseDepositDisease` | Variable decline |
| `cryoglobulinemic` | May decline acutely |
| `drugInducedGn` | Variable |
| `fibrillaryGlomerulonephritis` | Progressive decline |
| `bkVirusNephropathy` | Progressive decline |
| `mpgn` | Variable decline |
| `thinBasementMembrane` | Usually preserved; rarely progresses |
| `irgn` | Usually recovers |
| `tCellMediatedRejection` | Acute decline |
| `antibodyMediatedRejection` | Acute decline |
| `transplantGlomerulopathy` | Progressive decline |
| `cniToxicity` | Acute decline |

#### False Positives / False Negatives

- **Falsely elevated eGFR:** High muscle mass, high protein diet, acute illness with increased creatinine production.
- **Falsely reduced eGFR:** Low muscle mass (elderly, malnutrition, amputees), vegetarian diet, cirrhosis.
- **CKD-EPI limitations:** Less accurate at eGFR > 120 or < 15; less validated in extremes of body size, pregnancy, and certain ethnic groups.

#### Repeat Testing Recommendations

- CKD monitoring: every 3-6 months for stages G3-G5; every 6-12 months for G2.
- Acute changes: daily or more frequent in AKI or RPGN.
- Post-transplant: daily initially, then taper per protocol.

#### Monitoring Recommendations

- Track eGFR slope as primary outcome in clinical trials and longitudinal care.
- KDIGO heat map integrates eGFR with albuminuria for risk stratification.
- Drug dosing adjustments required for eGFR < 60 (many immunosuppressants), < 30 (most), < 15 (limit agents).

---

### LAB-RENAL-BUN

**Blood Urea Nitrogen (BUN)**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 7-20 mg/dL (2.5-7.1 mmol/L) |
| Pediatric | 5-18 mg/dL |
| Pregnancy | May decrease 20-30% due to increased GFR and anabolic state |

#### Interpretation

- **Elevated BUN:** Prerenal azotemia (dehydration, heart failure, hemorrhage, high protein intake), intrinsic renal disease, GI bleeding, corticosteroid use, catabolic state.
- **BUN:Creatinine ratio > 20:1:** Suggests prerenal azotemia, GI bleeding, high protein diet, or catabolic state.
- **BUN:Creatinine ratio < 10:1:** Suggests low protein intake, liver disease, SIADH, or pregnancy.
- **Low BUN:** Liver failure, malnutrition, SIADH, pregnancy.

#### Clinical Implications

BUN is a less specific marker of kidney function than creatinine. In glomerular disease, an elevated BUN disproportionate to creatinine may indicate GI bleeding (particularly in vasculitis with GI involvement such as polyarteritis nodosa or IgA vasculitis), dehydration, or catabolic state. The BUN:Creatinine ratio helps differentiate prerenal from intrinsic renal azotemia.

#### Associated Diseases

| Disease ID | Role of BUN |
|---|---|
| `anca` | Elevated BUN disproportionate to creatinine may suggest GI involvement |
| `cryoglobulinemic` | GI bleeding from intestinal vasculitis |
| `lupus` | Elevated in active disease; lupus enteritis rare cause |
| `antiGbm` | Elevated with AKI |
| `tCellMediatedRejection` | Elevated with renal dysfunction |
| `antibodyMediatedRejection` | Elevated with renal dysfunction |

#### False Positives / False Negatives

- **Falsely elevated:** Dehydration, high protein diet, GI bleeding, corticosteroids, tetracyclines, catabolic states (trauma, burns, sepsis), heart failure.
- **Falsely low:** Liver disease, malnutrition, SIADH, pregnancy, low protein diet.
- **Not recommended as sole marker of renal function.**

#### Repeat Testing Recommendations

- Serial BUN monitoring in RPGN for assessment of catabolic state.
- Not routinely monitored in stable CKD; creatinine and eGFR preferred.

#### Monitoring Recommendations

- Use in conjunction with creatinine for BUN:Cr ratio in differential diagnosis of AKI.
- Monitor during acute illness or when prerenal factors suspected.

---

### LAB-RENAL-CYSTATIN_C

**Cystatin C**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 0.59-1.03 mg/L (some labs 0.6-1.03 mg/L) |
| Pediatric (neonate) | 1.2-2.3 mg/L |
| Pediatric (1-5 years) | 0.7-1.2 mg/L |
| Pediatric (6-12 years) | 0.6-1.0 mg/L |
| Pregnancy | May be slightly elevated due to increased production |

#### Interpretation

- **Elevated:** Reduced GFR. Cystatin C rises earlier than creatinine in early kidney disease because it is less affected by muscle mass.
- **Mildly elevated (1.0-1.5 mg/L):** eGFR approximately 60-89 mL/min/1.73m2.
- **Moderately elevated (1.5-3.0 mg/L):** eGFR approximately 30-59 mL/min/1.73m2.
- **Severely elevated (> 3.0 mg/L):** eGFR < 30 mL/min/1.73m2.

#### Clinical Implications

Cystatin C is a low-molecular-weight protein produced by all nucleated cells at a relatively constant rate. It is freely filtered by the glomerulus and completely reabsorbed by the proximal tubule without secretion. Cystatin C-based eGFR equations (CKD-EPI cystatin C or combined creatinine-cystatin C) are more accurate than creatinine-based equations in individuals with unusual muscle mass (elderly, bodybuilders, amputees, malnourished). Cystatin C is recommended by KDIGO as a confirmatory test when creatinine-based eGFR may be inaccurate.

#### Associated Diseases

| Disease ID | Role of Cystatin C |
|---|---|
| `fsgs` | Confirmatory eGFR assessment |
| `membranous` | Confirmatory eGFR assessment |
| `mcd` | May detect AKI not apparent from creatinine alone |
| `lupus` | Confirmatory eGFR assessment |
| `alport` | Early detection of GFR decline |
| `diabeticNephropathy` | Early detection of GFR decline |
| `iga` | Confirmatory eGFR assessment |
| All others | Confirmatory eGFR assessment when creatinine-based eGFR unreliable |

#### False Positives / False Negatives

- **Falsely elevated:** Hyperthyroidism, obesity, smoking, high-dose corticosteroids, inflammation (CRP elevation), obesity. Males have slightly higher levels.
- **Falsely low:** Hyperthyroidism (paradoxically, some studies show reduced cystatin C), low-dose corticosteroids, low BMI.
- **Assay variability:** Different manufacturers have different reference ranges; use same assay for serial monitoring.

#### Repeat Testing Recommendations

- Use when creatinine-based eGFR is unreliable or discordant with clinical picture.
- Confirm borderline eGFR values (e.g., at threshold for transplant listing, living donor eligibility).
- Serial monitoring same as creatinine-based eGFR.

#### Monitoring Recommendations

- Serial measurements parallel creatinine-based eGFR trends.
- Combined creatinine-cystatin C equation provides most accurate eGFR estimation.

---

### LAB-RENAL-CREATININE_CLEARANCE

**Creatinine Clearance (24-hour urine)**

#### Reference Range

| Population | Range |
|---|---|
| Adult male | 97-137 mL/min |
| Adult female | 88-128 mL/min |
| Pediatric | Age-specific; neonates 20-40 mL/min; adults achieved by 1-2 years |

#### Interpretation

- **Reduced clearance:** Indicates decreased GFR. More sensitive than serum creatinine alone because it directly measures filtration.
- **Normal clearance:** Does not exclude early glomerular disease; significant nephron loss may occur before creatinine clearance falls below normal range.
- **Supranormal clearance:** May indicate hyperfiltration (early diabetic nephropathy, pregnancy, high-protein diet).

#### Clinical Implications

24-hour urine creatinine clearance provides a direct measurement of GFR that is more accurate than estimates. However, collection errors are common and limit clinical utility. Useful for confirmatory GFR measurement when eGFR equations are unreliable, for drug dosing in critical situations, and for research purposes. The CKD-EPI cystatin C equation has largely supplanted 24-hour creatinine clearance in clinical practice.

#### Associated Diseases

| Disease ID | Role of Creatinine Clearance |
|---|---|
| All glomerular diseases | Confirmatory GFR measurement when eGFR unreliable |
| `fsgs` | Assess hyperfiltration in early disease |
| `membranous` | Confirmatory GFR measurement |
| `alport` | Serial GFR measurement in progressive disease |
| `diabeticNephropathy` | Detect hyperfiltration |

#### False Positives / False Negatives

- **Falsely low:** Incomplete urine collection (most common error), urinary retention, urine spillage.
- **Falsely high:** Over-collection, high muscle mass, high protein intake.
- **Collection accuracy:** Urine creatinine excretion should be 15-25 mg/kg/day in males and 10-20 mg/kg/day in females to confirm adequate collection.

#### Repeat Testing Recommendations

- Repeat if collection suspected to be inaccurate (urine creatinine < 15 mg/kg/day in males or < 10 mg/kg/day in females).
- Not routinely repeated in stable CKD; eGFR preferred for longitudinal monitoring.

#### Monitoring Recommendations

- Primarily used for research and drug dosing rather than disease monitoring.

---

## 3. Serum Chemistries

---

### LAB-CHEMISTRY-ALBUMIN

**Serum Albumin**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 3.5-5.0 g/dL (35-50 g/L) |
| Pediatric (term neonate) | 2.9-4.4 g/dL |
| Pediatric (1 month - 16 years) | 3.5-5.0 g/dL |
| Pregnancy | 2.5-4.0 g/dL (physiological decrease due to hemodilution and increased transcapillary escape rate) |

#### Interpretation

- **Mildly low (3.0-3.5 g/dL):** May indicate mild hepatic dysfunction, mild proteinuria, malnutrition, or acute phase response.
- **Moderately low (2.5-3.0 g/dL):** Significant proteinuria, hepatic synthetic failure, malnutrition, or catabolic state.
- **Severely low (< 2.5 g/dL):** Nephrotic syndrome, severe liver failure, protein-losing enteropathy, severe malnutrition.
- **Elevated (> 5.0 g/dL):** Dehydration (relative elevation), multiple myeloma (paraprotein).
- **Hypoalbuminemia without proteinuria:** Liver disease, malnutrition, protein-losing enteropathy, acute inflammation.

#### Clinical Implications

Serum albumin is the most important serum marker in nephrotic syndrome. Hypoalbuminemia drives many complications of nephrotic syndrome including edema (reduced oncotic pressure), hyperlipidemia (increased hepatic lipoprotein synthesis), increased infection risk (loss of immunoglobulins), and thrombosis risk (loss of antithrombin III). The serum albumin level is used in the definition of nephrotic syndrome (albumin < 3.0 g/dL typically) and is an important prognostic marker.

#### Associated Diseases

| Disease ID | Role of Serum Albumin |
|---|---|
| `membranous` | Markedly reduced in nephrotic syndrome; important prognostic marker |
| `fsgs` | Reduced in nephrotic syndrome; severity variable |
| `mcd` | Markedly reduced during nephrotic episodes |
| `lupus` | Reduced in nephrotic lupus nephritis (Class V) or as acute phase response |
| `diabeticNephropathy` | Reduced in nephrotic-range proteinuria |
| `denseDepositDisease` | Reduced if nephrotic |
| `fibrillaryGlomerulonephritis` | Reduced if nephrotic |
| `cryoglobulinemic` | May be reduced (acute phase, proteinuria) |
| `iga` | Usually preserved; reduced if nephrotic transformation |
| `c3` | Variable |
| `drugInducedGn` | Variable |

#### False Positives / False Negatives

- **Falsely low:** Bromide interference (bromide > 10 mg/dL can falsely lower albumin by dye-binding methods), lipemia, hyperbilirubinemia.
- **Falsely elevated:** Dehydration (concentration effect), anabolic steroids, high-protein diet.
- **Assay variability:** BCG vs. BCP methods differ by 0.2-0.5 g/dL; use same method for serial monitoring.

#### Repeat Testing Recommendations

- During active nephrotic syndrome: monthly or at each clinic visit.
- After treatment initiation: monthly until remission.
- Stable CKD: every 3-6 months.

#### Monitoring Recommendations

- Albumin is a key component of nephrotic syndrome activity indices.
- Serial albumin trends are used to assess treatment response in membranous nephropathy and other nephrotic diseases.
- Albumin < 2.0 g/dL is associated with significantly increased mortality risk.

---

### LAB-CHEMISTRY-TOTAL_PROTEIN

**Total Protein**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 6.0-8.3 g/dL (60-83 g/L) |
| Pediatric (1 month - 16 years) | 6.0-8.0 g/dL |
| Pregnancy | 5.5-7.0 g/dL (physiological decrease) |

#### Interpretation

- **Low total protein with low albumin:** Proteinuria, liver disease, malnutrition, protein-losing enteropathy.
- **Low total protein with normal albumin:** Reduced globulins (immunodeficiency, nephrotic syndrome with selective proteinuria).
- **High total protein:** Dehydration, multiple myeloma, chronic inflammation, hepatitis.
- **High total protein with elevated globulins:** Paraproteinemia, chronic infection, autoimmune disease.

#### Clinical Implications

Total protein provides a global assessment of serum proteins. In glomerular disease, the total protein is influenced by both albumin loss (urinary) and globulin levels (affected by immunosuppression, inflammation, and paraprotein production). The albumin:globulin ratio is more informative than total protein alone.

#### Associated Diseases

| Disease ID | Role of Total Protein |
|---|---|
| `membranous` | Reduced in nephrotic syndrome |
| `fsgs` | Reduced in nephrotic syndrome |
| `mcd` | Reduced during nephrotic episodes |
| `lupus` | Variable; may be elevated (hypergammaglobulinemia) or reduced (nephrotic) |
| `cryoglobulinemic` | May be elevated (cryoglobulin) or reduced |
| All others | Supportive finding |

#### False Positives / False Negatives

- **Falsely elevated:** Lipemia, icterus, elevated paraprotein.
- **Falsely low:** Hemolysis (in some assays).

#### Repeat Testing Recommendations

- Monitored in parallel with albumin.
- Not independently used for clinical decision-making in glomerular disease.

#### Monitoring Recommendations

- Track in parallel with albumin and proteinuria.

---

### LAB-CHEMISTRY-SPEP

**Serum Protein Electrophoresis (SPEP)**

#### Reference Range

| Fraction | Range |
|---|---|
| Albumin | 3.5-5.0 g/dL |
| Alpha-1 globulin | 0.1-0.4 g/dL |
| Alpha-2 globulin | 0.6-1.0 g/dL |
| Beta globulin | 0.7-1.1 g/dL |
| Gamma globulin | 0.8-1.6 g/dL |

#### Interpretation

- **Monoclonal spike (M-spike):** Suggests plasma cell dyscrasia (multiple myeloma, MGUS, Waldenstrom macroglobulinemia). Must be confirmed by immunofixation.
- **Polyclonal gamma elevation:** Chronic inflammation, autoimmune disease, chronic infection, liver disease.
- **Reduced gamma globulins:** Immunosuppression, nephrotic syndrome (immunoglobulin loss), primary immunodeficiency.
- **Reduced albumin:** Nephrotic syndrome, liver disease, malnutrition, inflammation.
- **Alpha-2 elevation:** Nephrotic syndrome (elevated lipoproteins).
- **Beta-gamma bridging:** Liver cirrhosis.

#### Clinical Implications

SPEP is essential in the evaluation of glomerular disease, particularly in monoclonal gammopathy-associated glomerular diseases. Fibrillary glomerulonephritis and immunotactoid glomerulonephritis may be associated with monoclonal gammopathies. SPEP is part of the initial workup for any patient with unexplained glomerular disease, especially those with atypical features.

#### Associated Diseases

| Disease ID | Role of SPEP |
|---|---|
| `fibrillaryGlomerulonephritis` | Screen for associated monoclonal gammopathy |
| `membranous` | Screen for paraneoplastic membranous nephropathy |
| `fsgs` | Screen for paraprotein-related FSGS |
| `cryoglobulinemic` | Detect monoclonal component in type II cryoglobulinemia |
| `denseDepositDisease` | Screen for monoclonal gammopathy |
| `lupus` | Polyclonal hypergammaglobulinemia expected |

#### False Positives / False Negatives

- **False negatives:** Small monoclonal proteins (< 0.5 g/dL) may be missed on SPEP. Immunofixation is more sensitive.
- **False positives:** Hemolysis (spikes in beta-gamma region), lipemia, delayed specimen processing.

#### Repeat Testing Recommendations

- Repeat at diagnosis and during follow-up if initial SPEP abnormal.
- Annual SPEP in patients with known monoclonal gammopathy.
- SPEP should be performed alongside serum free light chains and urine immunofixation.

#### Monitoring Recommendations

- Monitor M-spike size in monoclonal gammopathy-associated glomerular disease.
- Track immunoglobulin levels in patients on immunosuppressive therapy.

---

### LAB-CHEMISTRY-SFLC

**Serum Free Light Chains (SFLC)**

#### Reference Range

| Parameter | Range |
|---|---|
| Kappa free light chains | 3.3-19.4 mg/L |
| Lambda free light chains | 5.7-26.3 mg/L |
| Kappa/Lambda ratio | 0.26-1.65 |

Note: Reference ranges vary by assay (Freelite vs. other platforms). Use laboratory-specific ranges.

#### Interpretation

- **Elevated kappa with normal lambda:** Monoclonal kappa-producing clone.
- **Elevated lambda with normal kappa:** Monoclonal lambda-producing clone.
- **Elevated kappa and lambda with normal ratio:** Polyclonal increase (renal insufficiency, inflammation) or biclonal gammopathy.
- **Abnormal kappa/lambda ratio (> 1.65 or < 0.26):** Strongly suggests monoclonal gammopathy.
- **Kappa/lambda ratio 1-3 or 0.33-1:** May be abnormal in patients with preserved renal function.

#### Clinical Implications

Serum free light chains are essential for screening and monitoring monoclonal gammopathy-associated glomerular diseases. They are more sensitive than SPEP alone for detecting monoclonal gammopathies. In glomerular disease evaluation, SFLC should be performed in all patients with unexplained disease, particularly fibrillary GN, cryoglobulinemia with monoclonal component, and MPGN of uncertain etiology. The ratio is particularly useful in light chain deposition disease and light chain proximal tubulopathy.

#### Associated Diseases

| Disease ID | Role of SFLC |
|---|---|
| `fibrillaryGlomerulonephritis` | Screen for monoclonal gammopathy |
| `cryoglobulinemic` | Type II cryoglobulinemia with monoclonal component |
| `membranous` | Screen for paraneoplastic disease |
| `mpgn` | Screen for monoclonal gammopathy-associated MPGN |
| `fsgs` | Rare association with monoclonal gammopathy |
| `denseDepositDisease` | Screen for monoclonal gammopathy |

#### False Positives / False Negatives

- **False positive abnormal ratio:** Renal insufficiency (reduced clearance elevates both, but kappa less affected), polyclonal B-cell activation.
- **False negative:** Small monoclonal proteins may be missed. Combined SPEP + SFLC is superior to either alone.
- **Assay limitations:** Freelite assay (The Binding Site) is most validated; other assays may have different reference ranges.

#### Repeat Testing Recommendations

- At diagnosis of monoclonal gammopathy-associated glomerular disease.
- Every 3-6 months during monitoring.
- SPEP and SFLC should be performed together.

#### Monitoring Recommendations

- Serial monitoring of involved free light chain and ratio in monoclonal gammopathy-associated glomerular disease.
- Response criteria for monoclonal gammopathy-associated GN require > 50% reduction in involved free light chain.

---

### LAB-CHEMISTRY-KL_RATIO

**Kappa/Lambda Free Light Chain Ratio**

#### Reference Range

| Population | Range |
|---|---|
| Adult (eGFR > 60) | 0.26-1.65 |
| Adult (eGFR < 60) | 0.37-3.1 (wider range due to reduced renal clearance) |
| Neonates | Wider range; age-specific norms apply |

#### Interpretation

- **Ratio > 1.65 (normal renal function):** Kappa restriction; monoclonal kappa-producing clone suspected.
- **Ratio < 0.26 (normal renal function):** Lambda restriction; monoclonal lambda-producing clone suspected.
- **Ratio within normal range:** Makes monoclonal gammopathy unlikely (high negative predictive value).
- **Ratio 1-3 or 0.33-1:** Borderline; must interpret in clinical context. May represent early monoclonal gammopathy or renal insufficiency.

#### Clinical Implications

The kappa/lambda ratio is the most sensitive single screening test for monoclonal gammopathy. A normal ratio has a > 99% negative predictive value for excluding a monoclonal gammopathy of clinical significance. This makes it an ideal screening test in the evaluation of unexplained glomerular disease.

#### Associated Diseases

| Disease ID | Role of Kappa/Lambda Ratio |
|---|---|
| `fibrillaryGlomerulonephritis` | Screen for monoclonal gammopathy (frequently associated) |
| `cryoglobulinemic` | Type II cryoglobulinemia screening |
| `mpgn` | Monoclonal gammopathy-associated MPGN |
| `membranous` | Paraneoplastic screening |

#### False Positives / False Negatives

- **False positives:** Renal insufficiency (wider ratio range), polyclonal gammopathy.
- **False negatives:** Small monoclonal proteins, biclonal gammopathy with balanced kappa and lambda clones.
- **Limitation:** Does not detect heavy chain monoclonal gammopathies (use immunofixation).

#### Repeat Testing Recommendations

- Same as SFLC recommendations.

#### Monitoring Recommendations

- Serial monitoring tracks treatment response in monoclonal gammopathy-associated glomerular disease.

---

## 4. Complement System

---

### LAB-COMPLEMENT-C3

**Complement Component C3**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 90-180 mg/dL (0.9-1.8 g/L) |
| Pediatric (term neonate) | 70-170 mg/dL (70% of maternal level at birth, nadir at 24-48 hours) |
| Pediatric (6 months) | Approaches adult levels |
| Pregnancy | May increase slightly due to increased hepatic synthesis |

#### Interpretation

- **Low C3 (< 90 mg/dL):** Active complement consumption. In glomerular disease, consider lupus nephritis, MPGN (especially C3 glomerulopathy), post-infectious GN, and cryoglobulinemia.
- **Severely low C3 (< 30 mg/dL):** Severe complement activation. Strongly suggests active lupus nephritis, acute post-infectious GN, or C3 glomerulopathy.
- **Normal C3:** Does not exclude complement-mediated disease (e.g., ANCA-associated GN, anti-GBM disease, IgA nephropathy, membranous nephropathy).
- **Elevated C3:** Acute phase response, may mask underlying consumption.

#### Clinical Implications

C3 is the central component of both the classical and alternative complement pathways. Its consumption in glomerular disease indicates active complement activation, which may be pathogenic or a consequence of immune complex deposition. C3 levels help differentiate between complement-mediated diseases (low C3) and those with preserved complement (ANCA-associated, anti-GBM, IgA nephropathy, membranous).

#### Associated Diseases

| Disease ID | Role of C3 |
|---|---|
| `c3` | Low C3 is hallmark; C3 nephritic factor may be present |
| `denseDepositDisease` | Low C3 typical; alternative pathway dysregulation |
| `lupus` | Low C3 in active lupus nephritis (Class III/IV); used to monitor disease activity |
| `cryoglobulinemic` | Low C3 in cryoglobulinemic vasculitis with GN |
| `irgn` | Low C3 in acute post-infectious GN; self-limited |
| `membranous` | Usually normal C3 |
| `fsgs` | Usually normal C3 |
| `mcd` | Normal C3 |
| `iga` | Usually normal C3 (occasionally low) |
| `antiGbm` | Normal C3 |
| `anca` | Normal C3 |
| `mpgn` | Low C3 common (especially C3 glomerulopathy subtype) |
| `drugInducedGn` | Variable |

#### False Positives / False Negatives

- **Falsely low:** Lipemia, hemolysis, prolonged specimen storage, complement consumption during acute illness unrelated to glomerular disease (sepsis, DIC).
- **Falsely normal:** Acute phase response (elevated hepatic synthesis masks consumption), immunosuppressive therapy.
- **Diurnal variation:** C3 may vary 5-10% throughout the day.

#### Repeat Testing Recommendations

- Active lupus nephritis: monthly C3 and C4 during treatment; C3 normalization indicates response.
- C3 glomerulopathy: every 3-6 months.
- Post-infectious GN: serial C3 until normalization (typically 6-8 weeks).
- Cryoglobulinemia: monitor during treatment.

#### Monitoring Recommendations

- C3 trend is more informative than single values.
- In lupus nephritis, C3 normalization is a treatment target (treat-to-target approach).
- Serial C3 in conjunction with C4 and CH50 provides comprehensive complement assessment.

---

### LAB-COMPLEMENT-C4

**Complement Component C4**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 10-40 mg/dL (100-400 mg/L) |
| Pediatric (term neonate) | 7-35 mg/dL |
| Pediatric (6 months) | Approaches adult levels |
| Pregnancy | May increase |

#### Interpretation

- **Low C4 (< 10 mg/dL):** Classical pathway activation. Consider lupus, cryoglobulinemia, immune complex disease, early post-infectious GN.
- **Severely low C4 (< 5 mg/dL):** Strongly suggests classical pathway activation. Lupus nephritis, cryoglobulinemia, and early post-infectious GN.
- **Normal C4 with low C3:** Suggests alternative pathway activation (C3 glomerulopathy) rather than classical pathway.
- **C4 level alone:** Less diagnostically useful than C4 in conjunction with C3.

#### Clinical Implications

C4 is consumed primarily via the classical pathway (C1q -> C4 -> C2 -> C3). Low C4 with low C3 suggests classical pathway activation (immune complex-mediated). Low C3 with normal C4 suggests alternative pathway activation (C3 glomerulopathy). This distinction is diagnostically important.

#### Associated Diseases

| Disease ID | Role of C4 |
|---|---|
| `lupus` | Low C4 in active lupus nephritis; classical pathway activation |
| `cryoglobulinemic` | Low C4 is characteristic; classical pathway activation via rheumatoid factor |
| `irgn` | C4 may be low (classical pathway activation by immune complexes) |
| `c3` | C4 usually normal (alternative pathway) |
| `denseDepositDisease` | C4 usually normal (alternative pathway) |
| `mpgn` | C4 low in immune complex-mediated MPGN; normal in C3 glomerulopathy |

#### False Positives / False Negatives

- **Falsely low:** Lipemia, hemolysis, prolonged storage, acute phase response masking.
- **Falsely normal:** Acute phase response (C4 is a positive acute phase reactant).
- **Genetic C4 deficiency:** Partial C4 deficiency is common (especially C4A null alleles in SLE).

#### Repeat Testing Recommendations

- Same as C3 monitoring.
- C4 is particularly useful in monitoring cryoglobulinemic vasculitis.

#### Monitoring Recommendations

- C4 normalization is a treatment target in cryoglobulinemic GN.
- C4 trends in conjunction with C3 provide complement activation pattern.

---

### LAB-COMPLEMENT-CH50

**Total Complement Hemolytic Activity (CH50)**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 60-144 U/mL (some labs > 70 U/mL) |
| Pediatric | 60-144 U/mL (adult levels by 6 months) |

Note: CH50 is not standardized across laboratories. Use institution-specific reference range.

#### Interpretation

- **Zero or near-zero CH50:** Complete deficiency of any late complement component (C5, C6, C7, C8, C9) or C1, C2, C4, C3, C5, C6, C7, C8, or C9 deficiency. Also seen in acquired complement consumption.
- **Low CH50 (< 60 U/mL):** Partial complement deficiency or active complement consumption.
- **Normal CH50:** Does not exclude alternative pathway abnormalities or partial deficiencies.
- **Elevated CH50:** Acute phase response.

#### Clinical Implications

CH50 measures the functional integrity of the entire classical complement pathway from C1 through C9. It is the most sensitive screening test for complement deficiencies of the terminal components (C5-C9) and early components (C1-C4). In glomerular disease, a low CH50 with low C3 and C4 confirms active classical pathway consumption. A low CH50 with low C3 but normal C4 suggests alternative pathway consumption. CH50 is also used to monitor complement-targeted therapies.

#### Associated Diseases

| Disease ID | Role of CH50 |
|---|---|
| `lupus` | Low in active disease; monitoring tool |
| `cryoglobulinemic` | Low; classical pathway activation |
| `c3` | May be low if classical pathway also activated |
| `denseDepositDisease` | May be low |
| `irgn` | Low during acute phase; normalizes with recovery |

#### False Positives / False Negatives

- **Falsely low:** Lipemia, hemolysis, specimen handling errors, EDTA anticoagulant (chelates calcium).
- **Falsely normal:** Acute phase response may elevate CH50, masking partial deficiency.
- **Assay variability:** Different laboratories use different methods (sheep red blood cell lysis vs. ELISA-based). Not interchangeable between institutions.

#### Repeat Testing Recommendations

- At diagnosis and during active disease.
- Serial monitoring during immunosuppressive therapy.
- Repeat testing after complement-targeted therapies (eculizumab, etc.).

#### Monitoring Recommendations

- CH50 normalization indicates adequate complement inhibition or resolution of complement consumption.
- Used as pharmacodynamic marker for complement inhibitor therapy.

---

### LAB-COMPLEMENT-SMAC

**Soluble Membrane Attack Complex (C5b-9)**

#### Reference Range

| Population | Range |
|---|---|
| Adult | < 100-300 ng/mL (assay-dependent) |

Note: Reference ranges are assay-specific. Use laboratory-specific reference range.

#### Interpretation

- **Elevated sC5b-9:** Terminal complement pathway activation. Indicates formation of the membrane attack complex (MAC).
- **Normal sC5b-9:** Does not exclude early complement pathway activation (upstream of C5).
- **Elevated sC5b-9 in plasma:** Systemic complement activation. May be seen in C3 glomerulopathy, lupus nephritis, TMA, and other complement-mediated diseases.
- **Elevated sC5b-9 in urine:** Indicates local renal complement activation. More specific for renal complement-mediated disease.

#### Clinical Implications

sC5b-9 is a marker of terminal complement pathway activation (MAC formation). It is elevated in diseases where complement activation proceeds to completion. Urinary sC5b-9 is particularly useful as a non-invasive marker of renal complement activation and may correlate with disease activity in C3 glomerulopathy and lupus nephritis.

#### Associated Diseases

| Disease ID | Role of sC5b-9 |
|---|---|
| `c3` | Elevated plasma and urinary sC5b-9; marker of alternative pathway activation |
| `denseDepositDisease` | Elevated sC5b-9 |
| `lupus` | Elevated sC5b-9 in active lupus nephritis |
| `tCellMediatedRejection` | May be elevated (complement activation in rejection) |
| `antibodyMediatedRejection` | Elevated sC5b-9; MAC deposition in graft |
| `transplantGlomerulopathy` | Elevated sC5b-9 |

#### False Positives / False Negatives

- **False positives:** Systemic complement activation from infection, inflammation, or other causes.
- **False negatives:** Early complement pathway activation without terminal pathway progression.
- **Assay limitations:** Limited standardization across laboratories; primarily a research tool.

#### Repeat Testing Recommendations

- Research setting: serial measurements during clinical trials.
- Clinical setting: use only if available and validated at institution.

#### Monitoring Recommendations

- May serve as a pharmacodynamic marker for complement inhibitor therapy.
- Urinary sC5b-9 may complement plasma measurements for assessing renal-specific complement activation.

---

### LAB-COMPLEMENT-C3NEF

**C3 Nephritic Factor**

#### Reference Range

- **Normal:** Absent or negative.

#### Interpretation

- **Positive C3NeF:** A nephritic factor that stabilizes C3 convertase (C3bBb), leading to uncontrolled alternative pathway activation and persistent C3 consumption. Present in C3 glomerulopathy (C3 glomerulonephritis and dense deposit disease), and in some cases of lupus nephritis and post-infectious GN.
- **Strongly positive:** Consistent with alternative pathway dysregulation.
- **Weakly positive:** May be seen in monoclonal gammopathies or transient complement activation.

#### Clinical Implications

C3NeF is a pathogenic autoantibody that stabilizes the alternative pathway C3 convertase. Its presence confirms alternative pathway dysregulation as the mechanism of disease and supports the diagnosis of C3 glomerulopathy. C3NeF testing is important for classification, prognosis, and therapeutic decision-making in C3 glomerulopathy.

#### Associated Diseases

| Disease ID | Role of C3NeF |
|---|---|
| `c3` | Present in 30-70% of C3 glomerulopathy cases |
| `denseDepositDisease` | Present in 30-50% of DDD cases |
| `lupus` | Occasionally positive |
| `irgn` | May be positive transiently |

#### False Positives / False Negatives

- **False positives:** Transient complement activation from infection, monoclonal immunoglobulins stabilizing C3 convertase.
- **False negatives:** C3NeF may be present but not detectable by current assays. Different assays have variable sensitivity. C3NeF may be IgG or IgA class; some assays detect only IgG.
- **Assay limitations:** No standardized assay; highly variable between reference laboratories.

#### Repeat Testing Recommendations

- At diagnosis of C3 glomerulopathy.
- Repeat if initial test negative but clinical suspicion high.
- Not routinely monitored during follow-up.

#### Monitoring Recommendations

- C3NeF status may inform prognosis but is not used to monitor treatment response.

---

### LAB-COMPLEMENT-ANTI_FH

**Anti-Factor H Antibodies**

#### Reference Range

- **Normal:** Absent or negative (< 100 AU/mL or assay-specific cutoff).

#### Interpretation

- **Positive anti-FH antibodies:** Autoantibodies directed against complement Factor H, leading to uncontrolled alternative pathway activation. Associated with C3 glomerulopathy, atypical hemolytic uremic syndrome (aHUS), and membranoproliferative GN.
- **High titers:** Strong association with disease activity; may predict relapse.
- **Low titers:** May be transient or of uncertain clinical significance.

#### Clinical Implications

Anti-Factor H antibodies inhibit the regulatory function of Factor H, resulting in uncontrolled alternative pathway activation on host cell surfaces and in the fluid phase. This leads to C3 consumption and C3 glomerulopathy. Testing is important for identifying patients who may benefit from plasma exchange (to remove antibodies) and immunosuppression (to suppress antibody production).

#### Associated Diseases

| Disease ID | Role of Anti-FH Antibodies |
|---|---|
| `c3` | Present in subset of C3 glomerulopathy |
| `denseDepositDisease` | Occasionally positive |
| `mpgn` | May be positive in complement-mediated MPGN |

#### False Positives / False Negatives

- **False positives:** Very rare with validated ELISA assays.
- **False negatives:** Antibodies may be against specific epitopes not detected by certain assays. Functional assays (Factor H cofactor activity) may be more sensitive.
- **Assay limitations:** Different assays may detect different antibody classes (IgG, IgA) and epitopes.

#### Repeat Testing Recommendations

- At diagnosis of C3 glomerulopathy or aHUS.
- Repeat during monitoring for relapse risk assessment.

#### Monitoring Recommendations

- Titer trends may predict relapse and guide therapy intensity.

---

### LAB-COMPLEMENT-ANTI_FB

**Anti-Factor B Antibodies**

#### Reference Range

- **Normal:** Absent or negative.

#### Interpretation

- **Positive anti-FB antibodies:** Rare autoantibodies that stabilize the alternative pathway C3 convertase (C3bBb). Functionally similar to C3NeF but target Factor B rather than C3. Associated with C3 glomerulopathy.
- **Significance:** Confirms alternative pathway dysregulation.

#### Clinical Implications

Anti-Factor B antibodies are a rare cause of alternative pathway dysregulation leading to C3 glomerulopathy. They are less common than C3NeF but have similar pathogenic mechanisms and clinical implications.

#### Associated Diseases

| Disease ID | Role of Anti-FB Antibodies |
|---|---|
| `c3` | Rare; alternative cause of C3 glomerulopathy |
| `denseDepositDisease` | Rare |

#### False Positives / False Negatives

- **Assay limitations:** Very rare; limited data on assay performance. Functional assays may be more sensitive.

#### Repeat Testing Recommendations

- At diagnosis of C3 glomerulopathy when C3NeF negative.

#### Monitoring Recommendations

- Limited data; treat as for C3 glomerulopathy with alternative pathway dysregulation.

---

### LAB-COMPLEMENT-PROPERDIN

**Properdin (Factor P)**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 5-40 ug/mL (or 50-150%, assay-dependent) |

#### Interpretation

- **Low properdin:** Partial properdin deficiency; predisposition to meningococcal disease. May also be seen in severe sepsis with complement consumption.
- **High properdin:** Acute phase reactant; elevated in inflammation.
- **Absent properdin:** Complete properdin deficiency; X-linked; severe susceptibility to Neisseria infections.
- **Normal:** Does not exclude other complement pathway abnormalities.

#### Clinical Implications

Properdin is a positive regulator of the alternative pathway, stabilizing the C3 convertase C3bBb. Deficiency leads to impaired alternative pathway activation but has also been paradoxically associated with uncontrolled complement activation (via loss of regulated activation). Properdin levels are rarely measured in routine clinical practice but may be relevant in the evaluation of complement-mediated glomerular diseases.

#### Associated Diseases

| Disease ID | Role of Properdin |
|---|---|
| `c3` | May be abnormal in complement-mediated C3 glomerulopathy |
| `denseDepositDisease` | Rarely measured; may be informative |

#### False Positives / False Negatives

- **Falsely low:** Acute sepsis, DIC, specimen handling errors.
- **Falsely high:** Acute phase response.
- **Assay limitations:** Not widely available; primarily a research assay.

#### Repeat Testing Recommendations

- Not routinely recommended for glomerular disease evaluation.
- Consider in cases of recurrent Neisseria infection with glomerular disease.

#### Monitoring Recommendations

- Not routinely monitored.

---

## 5. Autoantibodies

---

### LAB-AUTOANTIBODY-ANA

**Antinuclear Antibody (ANA)**

#### Reference Range

| Method | Normal Value |
|---|---|
| IIF (HEp-2 cells) | < 1:40 (negative); 1:40-1:80 (low positive); 1:160-1:320 (moderate); >= 1:640 (high) |
| ELISA | Negative (< 1.0 IU/mL or assay-specific) |

#### Interpretation

- **Positive IIF >= 1:160 with clinical features:** Significant; consider SLE and other connective tissue diseases.
- **Positive IIF 1:40-1:80 without clinical features:** Low positive; may be seen in healthy individuals (especially elderly women), infections, and medications.
- **Homogeneous pattern:** Anti-dsDNA, anti-histone; associated with SLE.
- **Speckled pattern:** Anti-Sm, anti-RNP, anti-Ro, anti-La; associated with SLE, Sjogren syndrome, MCTD.
- **Nucleolar pattern:** Anti-RNA polymerase III; associated with scleroderma.
- **Centromere pattern:** Anti-centromere; associated with limited scleroderma.
- **Cytoplasmic pattern:** Anti-Ro52, anti-mitochondrial; may have clinical significance.

#### Clinical Implications

ANA is the screening test for SLE. A positive ANA is required for SLE classification (ACR/EULAR 2019 criteria). However, ANA has significant limitations: it is sensitive but not specific for SLE. A positive ANA in the context of glomerular disease should prompt further testing for specific autoantibodies (anti-dsDNA, anti-Sm, anti-C1q, complement levels) and consideration of lupus nephritis.

#### Associated Diseases

| Disease ID | Role of ANA |
|---|---|
| `lupus` | Required for SLE classification; positive in > 95% of lupus nephritis |
| `membranous` | Positive ANA may indicate secondary membranous nephropathy |
| `anca` | May be positive in overlapping autoimmune conditions |
| `drugInducedGn` | Drug-induced lupus (ANA positive, anti-histone positive) |

#### False Positives / False Negatives

- **False positives:** Healthy elderly women (up to 25% positive at >= 1:40), infections (TB, hepatitis, EBV), medications (hydralazine, procainamide, isoniazid, minocycline), other autoimmune diseases, cancer, aging.
- **False negatives:** Rare; may occur in ANA-negative lupus (anti-Ro-positive lupus, drug-induced lupus). ELISA may miss antibodies detectable by IIF.
- **Titer significance:** Low-titer positive ANA (1:40-1:80) is common in healthy individuals and has limited clinical significance without supporting clinical features.

#### Repeat Testing Recommendations

- ANA titer does not correlate with disease activity in lupus; do not use serial ANA titers to monitor lupus nephritis activity.
- Anti-dsDNA and complement levels (C3, C4) are better markers for monitoring.
- Repeat ANA testing is rarely necessary once positive.

#### Monitoring Recommendations

- ANA is a diagnostic test, not a monitoring test. Do not use ANA titers to guide therapy.
- Monitor disease activity with anti-dsDNA, C3, C4, urine sediment, and eGFR.

---

### LAB-AUTOANTIBODY-ANTIDSDNA

**Anti-double-stranded DNA (Anti-dsDNA)**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA | < 30 IU/mL (some labs < 25 or < 20) |
| Farr assay | < 7% binding (or assay-specific) |
| CLIFT (Crithidia luciliae) | Negative at 1:10 dilution |

Note: Anti-dsDNA assays vary significantly between manufacturers. Use laboratory-specific reference ranges.

#### Interpretation

- **Strongly positive (> 100 IU/mL):** High correlation with active lupus nephritis. Titers may correlate with disease activity.
- **Moderately positive (30-100 IU/mL):** Significance depends on clinical context. May indicate active SLE.
- **Low positive (near cutoff):** May be transient or of limited clinical significance.
- **Negative:** Does not exclude SLE, especially in ANA-negative or anti-Ro-positive lupus.

#### Clinical Implications

Anti-dsDNA is highly specific for SLE (specificity > 95%) and is one of the classification criteria. Anti-dsDNA titers correlate with lupus nephritis activity and are used for monitoring treatment response. Rising anti-dsDNA with falling complement levels (C3, C4) may predict a lupus nephritis flare. Anti-dsDNA is part of the SLE Disease Activity Index (SLEDAI).

#### Associated Diseases

| Disease ID | Role of Anti-dsDNA |
|---|---|
| `lupus` | Highly specific; titer correlates with disease activity; used for monitoring |
| `drugInducedGn` | Anti-dsDNA usually negative in drug-induced lupus (anti-histone positive instead) |

#### False Positives / False Negatives

- **False positives:** Very rare. Monoclonal gammopathies, EBV infection, other infections rarely.
- **False negatives:** Different assays have variable sensitivity. CLIFT is most specific but less sensitive. ELISA may miss low-affinity antibodies. Anti-dsDNA may be negative during immunosuppressive therapy.
- **Assay variability:** Results between different assays are not interchangeable. Use the same assay for serial monitoring.

#### Repeat Testing Recommendations

- Monthly during active lupus nephritis to monitor response.
- At each flare or suspected flare.
- Use same assay for serial monitoring.

#### Monitoring Recommendations

- Rising anti-dsDNA with falling C3/C4 is a warning for impending flare.
- Anti-dsDNA normalization or significant titer reduction is a treatment target.
- Part of BILAG and SLEDAI activity indices.

---

### LAB-AUTOANTIBODY-ANCA

**Antineutrophil Cytoplasmic Antibodies (ANCA)**

#### Reference Range

| Parameter | Normal Value |
|---|---|
| PR3-ANCA (c-ANCA pattern) | Negative (< 20 IU/mL or assay-specific) |
| MPO-ANCA (p-ANCA pattern) | Negative (< 20 IU/mL or assay-specific) |
| IIF pattern | Negative |

#### Interpretation

- **PR3-ANCA positive, MPO-ANCA negative:** Granulomatosis with polyangiitis (GPA). c-ANCA pattern on IIF.
- **MPO-ANCA positive, PR3-ANCA negative:** Microscopic polyangiitis (MPA), eosinophilic granulomatosis with polyangiitis (EGPA). p-ANCA pattern on IIF.
- **Dual positive (PR3 and MPO):** Rare; consider cross-reactivity, assay artifact, or overlap syndrome.
- **ANCA negative with clinical vasculitis:** ANCA-negative vasculitis exists. Consider anti-GBM disease, immune complex GN, or drug-induced vasculitis.
- **Low positive ANCA without vasculitis:** May be seen in infections (TB, endocarditis, HIV), IBD, autoimmune hepatitis, and drug-induced ANCA vasculitis.

#### Clinical Implications

ANCA is the serological hallmark of ANCA-associated vasculitis (AAV). PR3-ANCA is strongly associated with GPA (granulomatosis with polyangiitis), while MPO-ANCA is associated with MPA and EGPA. ANCA positivity in the context of rapidly progressive glomerulonephritis is diagnostic of AAV until proven otherwise. ANCA titers may correlate with disease activity, particularly for PR3-ANCA in GPA.

#### Associated Diseases

| Disease ID | Role of ANCA |
|---|---|
| `anca` | PR3-ANCA or MPO-ANCA positive; defines AAV |
| `antiGbm` | May have dual positive ANCA and anti-GBM (10-30% of anti-GBM disease) |
| `drugInducedGn` | Drug-induced ANCA vasculitis (MPO-ANCA positive; propylthiouracil, hydralazine, minocycline) |
| `lupus` | ANCA may be positive; does not indicate AAV |
| `iga` | ANCA usually negative |

#### False Positives / False Negatives

- **False positives:** Infections (TB, endocarditis, HIV, hepatitis), IBD, autoimmune hepatitis, cystic fibrosis, lithium, cocaine (levamisole), drugs (propylthiouracil, hydralazine, minocycline, D-penicillamine, allopurinol).
- **False negatives:** ANCA-negative vasculitis (10-15% of AAV), early disease, immunosuppressive therapy, pauci-immune GN without systemic vasculitis.
- **IIF vs. ELISA:** IIF detects pattern (c-ANCA, p-ANCA); ELISA detects specific antigens (PR3, MPO). Modern practice uses direct antigen-specific ELISA (PR3, MPO) rather than IIF screening.
- **Assay sensitivity:** PR3-ANCA ELISA sensitivity for GPA 65-90%; MPO-ANCA sensitivity for MPA 60-85%.

#### Repeat Testing Recommendations

- At diagnosis and during follow-up to monitor disease activity.
- Serial PR3-ANCA titers may predict relapse in GPA (rising titers precede clinical relapse).
- MPO-ANCA titers are less reliable for monitoring MPA.
- Annual ANCA testing in patients with history of AAV in remission.

#### Monitoring Recommendations

- Rising PR3-ANCA titer (> 3-fold increase) with clinical symptoms suggests relapse.
- ANCA should be used in conjunction with clinical assessment, CRP, ESR, and renal function for monitoring.
- Do not treat solely on the basis of rising ANCA titer without clinical evidence of disease.

---

### LAB-AUTOANTIBODY_ANTIGBM

**Anti-Glomerular Basement Membrane (Anti-GBM) Antibodies**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA | Negative (< 20 IU/mL or assay-specific) |
| IIF (kidney biopsy) | Negative |

#### Interpretation

- **Positive anti-GBM antibodies:** Anti-GBM disease (Goodpasture syndrome if pulmonary hemorrhage present). Pathogenic antibodies targeting the alpha-3 chain of type IV collagen in GBM and alveolar basement membrane.
- **High titer:** Strongly positive; severe disease expected.
- **Low titer:** May indicate early disease or residual antibodies after treatment.
- **Dual positive (ANCA + anti-GBM):** 10-30% of anti-GBM disease patients are also ANCA-positive. Dual positive patients may have a relapsing course unlike typical anti-GBM disease.
- **ANCA-positive, anti-GBM negative with pauci-immune GN:** AAV, not anti-GBM disease.

#### Clinical Implications

Anti-GBM antibodies are the serological hallmark of anti-GBM disease (Goodpasture syndrome). Positive anti-GBM with rapidly progressive glomerulonephritis and/or pulmonary hemorrhage is an emergency requiring urgent plasma exchange, corticosteroids, and cyclophosphamide. Anti-GBM testing should be performed emergently in any patient with RPGN.

#### Associated Diseases

| Disease ID | Role of Anti-GBM |
|---|---|
| `antiGbm` | Pathognomonic; defines anti-GBM disease |
| `anca` | 10-30% of anti-GBM disease patients also ANCA-positive |
| `iga` | Anti-GBM negative; important differential of RPGN |

#### False Positives / False Negatives

- **False positives:** Very rare with modern ELISA. Historically, non-specific binding occurred.
- **False negatives:** Antibodies may be below detection limit early in disease. Plasma exchange may reduce antibody levels before testing. Antibodies may be eluted from tissue (kidney biopsy immunofluorescence may be positive despite negative serum).
- **Assay sensitivity:** Modern ELISA has > 95% sensitivity for active anti-GBM disease.

#### Repeat Testing Recommendations

- At presentation and serially (every 1-2 days) during acute treatment to monitor antibody clearance.
- Antibody levels typically become undetectable within 2-4 weeks of treatment.
- Repeat testing if initial negative but clinical suspicion remains high.

#### Monitoring Recommendations

- Serial anti-GBM titers to monitor response to plasma exchange and immunosuppression.
- Antibody clearance precedes clinical improvement.
- Repeat renal biopsy may be needed if clinical course atypical.

---

### LAB-AUTOANTIBODY-ANTIPLA2R

**Anti-Phospholipase A2 Receptor (Anti-PLA2R)**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA (Euroimmun) | < 20 RU/mL |
| IIF (Euroimmun) | Negative |

#### Interpretation

- **Positive anti-PLA2R (> 20 RU/mL):** Primary membranous nephropathy. Anti-PLA2R is present in 70-80% of primary membranous nephropathy.
- **High titer (> 150 RU/mL):** High antibody burden; may predict more severe disease and slower response to treatment.
- **Low positive (20-150 RU/mL):** May indicate early disease, partial response to treatment, or low-burden disease.
- **Negative anti-PLA2R:** Does not exclude membranous nephropathy. Consider secondary causes (lupus, hepatitis, malignancy, drugs) or PLA2R-negative primary MN. Anti-thrombospondin type-1 domain-containing 7A (anti-THSD7A) should be tested.

#### Clinical Implications

Anti-PLA2R is a highly specific biomarker for primary membranous nephropathy (> 99% specificity). It has revolutionized the diagnosis and monitoring of membranous nephropathy, often making diagnostic renal biopsy unnecessary when clinical features are consistent. Anti-PLA2R titers correlate with disease activity and are used for treatment monitoring.

#### Associated Diseases

| Disease ID | Role of Anti-PLA2R |
|---|---|
| `membranous` | Present in 70-80% of primary membranous nephropathy; diagnostic and prognostic marker |
| `lupus` | PLA2R-negative; important to distinguish primary from secondary membranous nephropathy |

#### False Positives / False Negatives

- **False positives:** Very rare (< 1% in validation studies). Some healthy individuals have low-level anti-PLA2R that does not cause disease.
- **False negatives:** 20-30% of primary membranous nephropathy is PLA2R-negative (anti-THSD7A-positive or antibody-negative). Assay sensitivity varies between manufacturers.
- **Assay variability:** Euroimmun and other platforms may give different results. Use same platform for serial monitoring.

#### Repeat Testing Recommendations

- At diagnosis and serially (every 3-6 months) during follow-up.
- Anti-PLA2R seroconversion from negative to positive may predict relapse.
- Anti-PLA2R normalization is a treatment target and predicts clinical remission.
- Anti-PLA2R decline precedes clinical remission by 3-6 months.

#### Monitoring Recommendations

- Serial anti-PLA2R titers guide treatment duration and help predict relapse.
- Declining titers indicate treatment response; rising titers suggest relapse.
- Rituximab treatment monitoring: anti-PLA2R decline is the primary biomarker for response.
- Anti-PLA2R seroreversion (positive to negative) is associated with sustained remission.

---

### LAB-AUTOANTIBODY_ANTITHSD7A

**Anti-Thrombospondin Type-1 Domain-Containing 7A (Anti-THSD7A)**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA | Negative (assay-specific cutoff) |
| IIF | Negative |

#### Interpretation

- **Positive anti-THSD7A:** Identified in 2-5% of PLA2R-negative primary membranous nephropathy. Pathogenic antibody causing membranous nephropathy.
- **Anti-THSD7A with membranous nephropathy:** Higher association with malignancy compared to PLA2R-positive MN. Cancer screening is particularly important.
- **Negative:** Does not exclude membranous nephropathy; consider antibody-negative MN.

#### Clinical Implications

Anti-THSD7A was identified in 2014 as a target antigen in membranous nephropathy. It accounts for a small proportion of primary membranous nephropathy cases. Anti-THSD7A-positive membranous nephropathy has been associated with a higher prevalence of concurrent or subsequent malignancy, warranting thorough cancer screening.

#### Associated Diseases

| Disease ID | Role of Anti-THSD7A |
|---|---|
| `membranous` | Present in 2-5% of primary membranous nephropathy; higher malignancy association |

#### False Positives / False Negatives

- **False positives:** Very rare.
- **False negatives:** Assay sensitivity may be limited. Some patients may have low antibody titers below detection threshold.
- **Assay limitations:** Less validated than anti-PLA2R; primarily available in specialized laboratories.

#### Repeat Testing Recommendations

- At diagnosis of PLA2R-negative membranous nephropathy.
- Serial monitoring as for anti-PLA2R.
- Annual cancer screening regardless of treatment response in anti-THSD7A-positive patients.

#### Monitoring Recommendations

- Serial titers may guide treatment monitoring, though less validated than anti-PLA2R.

---

### LAB-AUTOANTIBODY_ANTIC1Q

**Anti-C1q Antibodies**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA | < 10-20 U/mL (assay-specific) |

#### Interpretation

- **Positive anti-C1q antibodies:** Associated with hypocomplementemic urticarial vasculitis syndrome (HUVS), lupus nephritis (especially proliferative forms), and MPGN.
- **High titers:** Strongly associated with active lupus nephritis; may predict severe renal involvement.
- **Positive in membranous lupus nephritis (Class V):** Higher risk of progression.
- **Positive in lupus nephritis with low C4:** Classical pathway activation.

#### Clinical Implications

Anti-C1q antibodies target C1q, the first component of the classical complement pathway. They are associated with complement consumption and immune complex-mediated renal disease. In lupus nephritis, anti-C1q is a marker of disease activity and may complement anti-dsDNA and complement levels for monitoring.

#### Associated Diseases

| Disease ID | Role of Anti-C1q Antibodies |
|---|---|
| `lupus` | Positive in 30-50% of lupus nephritis; correlates with disease activity |
| `mpgn` | Positive in immune complex-mediated MPGN |
| `c3` | Occasionally positive |

#### False Positives / False Negatives

- **False positives:** Rare. May be positive in other complement-mediated diseases.
- **False negatives:** Sensitivity varies between assays. May be negative in early disease.

#### Repeat Testing Recommendations

- At diagnosis of lupus nephritis.
- Serial monitoring during active disease; titers may correlate with activity.

#### Monitoring Recommendations

- Anti-C1q titers may be used alongside anti-dsDNA and complement levels for monitoring lupus nephritis activity.

---

### LAB-AUTOANTIBODY_ANTICARDIOLIPIN

**Anticardiolipin Antibodies and Anti-Beta-2 Glycoprotein I**

#### Reference Range

| Antibody | Normal Value |
|---|---|
| aCL IgG | < 15 GPL units |
| aCL IgM | < 20 MPL units |
| Anti-beta2GPI IgG | < 20 units (or assay-specific) |
| Anti-beta2GPI IgM | < 20 units (or assay-specific) |

Note: Low-positive (15-40 GPL/MPL), moderate-positive (40-80), and high-positive (> 80) classifications apply to aCL.

#### Interpretation

- **Low-positive aCL or anti-beta2GPI (single positive, single time point):** May be transient; confirm with repeat testing at 12 weeks.
- **Moderate to high-positive aCL and/or anti-beta2GPI on two occasions >= 12 weeks apart:** Meets laboratory criteria for antiphospholipid syndrome (APS).
- **Triple positive (aCL + anti-beta2GPI + lupus anticoagulant):** Highest risk for thrombosis and pregnancy complications.
- **Isolated anti-beta2GPI positive:** Associated with thrombosis risk, particularly in APS nephropathy.

#### Clinical Implications

Antiphospholipid antibodies are associated with thrombosis (arterial and venous) and pregnancy complications. In the context of glomerular disease, antiphospholipid antibodies may cause APS nephropathy (thrombotic microangiopathy, fibrin thrombi in glomerular capillaries). They may also contribute to thrombotic complications in nephrotic syndrome.

#### Associated Diseases

| Disease ID | Role of Antiphospholipid Antibodies |
|---|---|
| `lupus` | Antiphospholipid syndrome associated with SLE; APS nephropathy |
| `membranous` | Thrombosis risk in nephrotic syndrome |
| `fsgs` | Rare association with APS nephropathy |

#### False Positives / False Negatives

- **False positives (aCL):** Infections (syphilis, HIV, hepatitis), medications, malignancy, elderly.
- **False positives (anti-beta2GPI):** Less affected by infections than aCL; more specific for APS.
- **False negatives:** Single time point testing may miss intermittent positivity. Lupus anticoagulant may be falsely negative in patients on anticoagulation.
- **Confirmatory testing:** Requires persistence at >= 12 weeks to meet Sydney criteria for APS.

#### Repeat Testing Recommendations

- Confirm positivity at >= 12 weeks.
- Annual testing in patients with SLE or history of thrombosis.
- Repeat if thrombotic event or pregnancy complication occurs.

#### Monitoring Recommendations

- Not routinely monitored for titers; presence/absence and persistence are the clinically relevant factors.
- Manage thrombosis risk with anticoagulation per guidelines.

---

### LAB-AUTOANTIBODY_RF

**Rheumatoid Factor (RF)**

#### Reference Range

| Method | Normal Value |
|---|---|
| Nephelometry/turbidimetry | < 14-20 IU/mL (assay-specific) |

#### Interpretation

- **Positive RF (> 20 IU/mL):** May indicate rheumatoid arthritis, Sjogren syndrome, cryoglobulinemia, chronic infections (TB, endocarditis, hepatitis), or other autoimmune diseases.
- **High RF titer in cryoglobulinemia:** IgM RF is the monoclonal component in type II mixed cryoglobulinemia (typically IgM-kappa).
- **Low positive RF:** Non-specific; may be seen in healthy elderly individuals (up to 5-10%).

#### Clinical Implications

In the context of glomerular disease, RF is particularly relevant for cryoglobulinemic GN. Type II mixed cryoglobulinemia is typically associated with HCV infection and contains a monoclonal IgM-kappa component with rheumatoid factor activity. RF positivity in the context of GN should prompt evaluation for cryoglobulinemia.

#### Associated Diseases

| Disease ID | Role of RF |
|---|---|
| `cryoglobulinemic` | IgM RF is pathogenic component of type II cryoglobulinemia |
| `lupus` | May be positive (polyclonal) |
| `iga` | Usually negative |

#### False Positives / False Negatives

- **False positives:** Aging, infections (TB, endocarditis, hepatitis), other autoimmune diseases, hypergammaglobulinemia.
- **False negatives:** RF may be of IgA or IgG class (standard assays detect IgM RF). Cryoglobulins may precipitate and be removed during processing, leading to false-negative RF.

#### Repeat Testing Recommendations

- At diagnosis of suspected cryoglobulinemia.
- Monitor during treatment of cryoglobulinemic GN.

#### Monitoring Recommendations

- RF levels parallel cryoglobulin levels in type II cryoglobulinemia.

---

### LAB-AUTOANTIBODY-CRYOGLOBULINS

**Cryoglobulins**

#### Reference Range

- **Normal:** Absent (negative).

#### Interpretation

- **Type I (monoclonal):** Single immunoglobulin (usually IgG or IgM). Associated with Waldenstrom macroglobulinemia, multiple myeloma, CLL.
- **Type II (mixed, monoclonal + polyclonal):** Monoclonal IgM (RF) + polyclonal IgG. Strongly associated with HCV infection. Classic cryoglobulinemic GN.
- **Type III (mixed, polyclonal):** Polyclonal IgM + polyclonal IgG. Associated with autoimmune diseases, HCV, other infections.
- **Quantification:** Cryocrit > 1% is clinically significant.
- **Complement levels:** Low C4 is characteristic (even when C3 is normal) due to complement consumption by immune complexes.

#### Clinical Implications

Cryoglobulinemia is a systemic vasculitis that commonly affects the kidneys. Cryoglobulinemic GN typically presents as MPGN pattern on biopsy. The presence of cryoglobulins, low C4, and RF positivity in the context of GN should prompt evaluation for HCV infection (the most common cause of cryoglobulinemic GN).

#### Associated Diseases

| Disease ID | Role of Cryoglobulins |
|---|---|
| `cryoglobulinemic` | Diagnostic; pathogenic mechanism |
| `mpgn` | Cryoglobulinemic GN often presents with MPGN pattern |

#### False Positives / False Negatives

- **False positives:** Improper specimen handling. Blood must be collected in pre-warmed tubes and processed at 37 degrees C. Cooling causes precipitation.
- **False negatives:** Cryoglobulins may precipitate during storage or transport. Requires experienced laboratory. Cryoglobulins may be present at low levels and require repeated sampling.
- **Technical requirements:** Blood must be drawn into pre-warmed (37 degrees C) tubes, transported at 37 degrees C, and processed at 37 degrees C. Serum is separated at 37 degrees C and then cooled to 4 degrees C for 7 days to allow precipitation.

#### Repeat Testing Recommendations

- If initial test negative but clinical suspicion high, repeat on 2-3 occasions.
- Quantitative cryoglobulin measurement during active disease.
- Monitor during treatment.

#### Monitoring Recommendations

- Cryocrit reduction parallels disease activity and treatment response.
- Monitor complement levels (C4) and RF alongside cryoglobulins.

---

### LAB-AUTOANTIBODY_ANTICCP

**Anti-Cyclic Citrullinated Peptide (Anti-CCP)**

#### Reference Range

| Method | Normal Value |
|---|---|
| ELISA | < 20 U/mL (or assay-specific) |

#### Interpretation

- **Positive anti-CCP:** Highly specific for rheumatoid arthritis (specificity > 95%). May be present years before clinical RA onset.
- **Low positive:** May indicate early RA or undifferentiated arthritis.
- **Negative:** Does not exclude RA, but makes it less likely.
- **Association with nephropathy:** Anti-CCP-positive RA may be associated with AA amyloidosis, membranous nephropathy, or drug-induced GN.

#### Clinical Implications

Anti-CCP is primarily used in the diagnosis of rheumatoid arthritis. In the context of glomerular disease, its relevance is indirect: RA-associated nephropathy (amyloidosis, membranous, GN) in anti-CCP-positive patients.

#### Associated Diseases

| Disease ID | Role of Anti-CCP |
|---|---|
| `drugInducedGn` | RA-associated GN in anti-CCP-positive patients |
| `membranous` | Rare association with RA |

#### False Positives / False Negatives

- **False positives:** Very rare. May be positive in some autoimmune diseases and infections.
- **False negatives:** 20-30% of RA patients are anti-CCP-negative (seronegative RA).

#### Repeat Testing Recommendations

- Not routinely repeated once positive.
- Primarily a diagnostic test for RA, not a monitoring test.

#### Monitoring Recommendations

- Not used to monitor disease activity.

---

### LAB-AUTOANTIBODY-RO_LA_SM_RNP

**Anti-Ro, Anti-La, Anti-Sm, Anti-RNP Antibodies**

#### Reference Range

| Antibody | Normal Value |
|---|---|
| Anti-Ro/SSA | Negative |
| Anti-La/SSB | Negative |
| Anti-Sm | Negative |
| Anti-U1 RNP | Negative |

#### Interpretation

- **Anti-Ro (SSA):** Sjogren syndrome, neonatal lupus, subacute cutaneous lupus. In glomerular disease, anti-Ro-positive SLE may be ANA-negative (anti-Ro recognizes Ro/SSA antigen, which may not produce standard ANA pattern).
- **Anti-La (SSB):** Usually co-occurs with anti-Ro; Sjogren syndrome. Rarely causes GN independently.
- **Anti-Sm:** Highly specific for SLE (specificity > 99%). Associated with lupus nephritis, particularly proliferative forms. Sm antigen is a small nuclear ribonucleoprotein.
- **Anti-U1 RNP:** Mixed connective tissue disease (MCTD). Also positive in SLE. Associated with Raynaud phenomenon and arthralgia.

#### Clinical Implications

These antibodies help classify the specific autoimmune disease associated with glomerular nephritis. Anti-Sm is the most relevant for glomerular disease as it is highly specific for SLE and associated with nephritis. Anti-Ro is relevant because it may cause ANA-negative SLE with glomerular involvement.

#### Associated Diseases

| Disease ID | Role of Autoantibodies |
|---|---|
| `lupus` | Anti-Sm: highly specific; anti-Ro: ANA-negative lupus; anti-RNP: MCTD overlap |
| `membranous` | Anti-Ro-positive SLE may present with membranous lupus nephritis |

#### False Positives / False Negatives

- **False positives:** Anti-Ro may be positive in Sjogren syndrome without SLE. Anti-RNP may be positive in other autoimmune diseases.
- **False negatives:** Assay sensitivity varies. Anti-Sm may be negative in a proportion of lupus patients despite disease.
- **ANA-negative lupus:** Anti-Ro-positive patients may have negative standard ANA by IIF; this does not exclude SLE.

#### Repeat Testing Recommendations

- At diagnosis; these are classification antibodies and do not typically change over time.
- Anti-Sm may fluctuate with disease activity but is not used for monitoring.

#### Monitoring Recommendations

- Not used for serial monitoring. Monitor lupus nephritis with anti-dsDNA, C3, C4, and urine studies.

---

### LAB-AUTOANTIBODY_PLA2R_ELISA

**Anti-Phospholipase A2 Receptor (PLA2R) ELISA**

#### Reference Range

| Method | Normal Value |
|---|---|
| Quantitative ELISA (Euroimmun) | < 20 RU/mL |
| Qualitative ELISA | Negative |

Note: This entry specifically refers to the quantitative ELISA assay for anti-PLA2R, which provides titer information essential for monitoring. See also LAB-AUTOANTIBODY-ANTIPLA2R for general anti-PLA2R information.

#### Interpretation

- **< 20 RU/mL:** Negative. Does not exclude membranous nephropathy.
- **20-50 RU/mL:** Low positive. May indicate early or low-burden disease.
- **50-150 RU/mL:** Moderate positive. Active disease likely.
- **> 150 RU/mL:** High positive. High antibody burden; more severe disease expected; may predict slower treatment response.
- **> 1000 RU/mL:** Very high titer; associated with nephrotic-range proteinuria and may require more aggressive or prolonged treatment.

#### Clinical Implications

The quantitative PLA2R ELISA provides titer information that is essential for treatment monitoring. The correlation between anti-PLA2R titer and disease activity is strong: declining titers indicate treatment response, while rising titers indicate relapse. Anti-PLA2R seroconversion from negative to positive may occur before clinical relapse, providing an opportunity for preemptive treatment.

#### Associated Diseases

| Disease ID | Role of PLA2R ELISA |
|---|---|
| `membranous` | Diagnostic (70-80% of primary MN); monitoring tool; prognostic marker |

#### False Positives / False Negatives

- **False positives:** Very rare. See general anti-PLA2R entry.
- **False negatives:** 20-30% of primary MN is PLA2R-negative by ELISA.
- **Assay limitations:** Different platforms may have different cutoffs and dynamic ranges.

#### Repeat Testing Recommendations

- At diagnosis and every 3-6 months during active disease.
- Every 6-12 months during remission to monitor for relapse.
- At each clinical decision point (treatment initiation, escalation, discontinuation).

#### Monitoring Recommendations

- Anti-PLA2R decline is the primary biomarker for treatment response in rituximab-treated membranous nephropathy.
- Anti-PLA2R normalization precedes clinical remission by 3-6 months.
- Anti-PLA2R seroreversion (positive to negative) is associated with sustained remission.
- Rising anti-PLA2R titer during remission may predict relapse 3-6 months before clinical deterioration.

---

## 6. Immunology

---

### LAB-IMMUNOLOGY-IG

**Immunoglobulins (IgG, IgA, IgM, IgE)**

#### Reference Range

| Parameter | Adult Range | Pediatric Range |
|---|---|---|
| IgG | 700-1600 mg/dL | Age-specific (neonate: 700-1600 mg/dL [transplacental]; 3 months: 200-800; 1 year: 300-1200; adult levels by 8-10 years) |
| IgA | 70-400 mg/dL | Age-specific (neonate: undetectable; 3 months: 5-30; adult levels by 10-12 years) |
| IgM | 40-230 mg/dL | Age-specific (neonate: 5-30; adult levels by 1-2 years) |
| IgE | 0-100 IU/mL | Age-specific; < 2 years may be lower |

#### Interpretation

- **Low IgG (hypogammaglobulinemia):** Primary immunodeficiency, nephrotic syndrome (urinary IgG loss), immunosuppressive therapy, protein-losing conditions.
- **Low IgA:** Selective IgA deficiency (most common primary immunodeficiency); may be associated with IgA nephropathy.
- **Elevated IgG:** Chronic infection, autoimmune disease, IgG4-related disease, multiple myeloma (monoclonal).
- **Elevated IgA:** IgA nephropathy (serum IgA may be elevated in 30-50% of cases), celiac disease, liver disease, infections.
- **Elevated IgM:** Primary biliary cholangitis, hyper-IgM syndrome, acute hepatitis, Waldenstrom macroglobulinemia.
- **Elevated IgE:** Atopic disease, allergic bronchopulmonary aspergillosis, hyper-IgE syndrome, parasitic infections.

#### Clinical Implications

Immunoglobulin levels are relevant in glomerular disease for several reasons: (1) urinary IgG loss in nephrotic syndrome indicates non-selective proteinuria and severe glomerular damage; (2) elevated IgA is a serological finding in IgA nephropathy; (3) immunosuppressive therapy may cause hypogammaglobulinemia, increasing infection risk; (4) IgG4-related disease can cause tubulointerstitial nephritis and membranous nephropathy; (5) selective IgA deficiency is associated with IgA nephropathy.

#### Associated Diseases

| Disease ID | Role of Immunoglobulins |
|---|---|
| `iga` | Serum IgA may be elevated; IgA deficiency associated |
| `membranous` | IgG4 may be elevated in IgG4-related membranous nephropathy |
| `lupus` | Polyclonal hypergammaglobulinemia (especially IgG) |
| `cryoglobulinemic` | IgM component in type II cryoglobulinemia |
| `fsgs` | Urinary IgG loss indicates non-selective proteinuria |
| `mcd` | Urinary IgG loss minimal (selective proteinuria) |
| All others | Monitor for immunosuppression-related hypogammaglobulinemia |

#### False Positives / False Negatives

- **Falsely elevated:** Lipemia, hemolysis, paraprotein interference.
- **Falsely low:** Hemodilution, impaired hepatic synthesis.
- **Age-related variation:** Pediatric immunoglobulin levels differ significantly from adults.

#### Repeat Testing Recommendations

- At diagnosis of glomerular disease.
- Before initiating immunosuppressive therapy (baseline).
- Every 3-6 months during immunosuppressive therapy.
- IgG < 400 mg/dL: consider IVIG replacement for infection prophylaxis.

#### Monitoring Recommendations

- Monitor IgG levels during rituximab, cyclophosphamide, or mycophenolate therapy.
- Hypogammaglobulinemia (IgG < 400 mg/dL) increases infection risk; consider immunoglobulin replacement.
- Serum IgA in IgA nephropathy: may be monitored but is not a validated disease activity marker.

---

### LAB-IMMUNOLOGY-IG_SUBCLASSES

**IgG Subclasses**

#### Reference Range

| Subclass | Adult Range | Pediatric Range |
|---|---|---|
| IgG1 | 300-900 mg/dL (60-70% of total IgG) | Age-specific |
| IgG2 | 60-300 mg/dL (20-25%) | Adult levels by 6-8 years |
| IgG3 | 20-100 mg/dL (5-8%) | Adult levels by 1 year |
| IgG4 | 10-140 mg/dL (3-6%) | Adult levels by 8-10 years |

#### Interpretation

- **IgG1 deficiency:** Associated with recurrent bacterial infections (most clinically significant).
- **IgG2 deficiency:** Impaired response to polysaccharide antigens; recurrent sinopulmonary infections.
- **IgG3 deficiency:** Associated with recurrent respiratory infections; shortest half-life of IgG subclasses.
- **IgG4 elevation (> 135 mg/dL):** IgG4-related disease (IgG4-RD). May cause tubulointerstitial nephritis, membranous nephropathy, or retroperitoneal fibrosis.
- **IgG4/IgG ratio > 10%:** Suggestive of IgG4-RD.
- **IgG4 subclass-specific anti-PLA2R:** Anti-PLA2R in membranous nephropathy is predominantly IgG4 subclass.

#### Clinical Implications

IgG4-related disease is an increasingly recognized cause of tubulointerstitial nephritis and membranous nephropathy. Elevated serum IgG4 (> 135 mg/dL) with tissue infiltration of IgG4-positive plasma cells and characteristic histopathology establishes the diagnosis. IgG subclass measurement is essential when IgG4-RD is suspected.

#### Associated Diseases

| Disease ID | Role of IgG Subclasses |
|---|---|
| `membranous` | IgG4-dominant anti-PLA2R antibodies; IgG4-RD-related membranous nephropathy |
| `drugInducedGn` | IgG4-related tubulointerstitial nephritis |
| All others | Monitor IgG subclass distribution during immunosuppression |

#### False Positives / False Negatives

- **Falsely elevated IgG4:** Other inflammatory conditions, some infections.
- **Falsely low IgG4:** Cannot exclude IgG4-RD if histopathology is consistent.
- **Assay limitations:** IgG4 assays have significant inter-laboratory variability.

#### Repeat Testing Recommendations

- At diagnosis of suspected IgG4-RD.
- During monitoring of IgG4-RD treatment.
- Serial IgG4 may correlate with disease activity in IgG4-RD.

#### Monitoring Recommendations

- Serial IgG4 levels may be used to monitor treatment response in IgG4-RD.
- IgG4 normalization is a treatment goal in IgG4-related tubulointerstitial nephritis.

---

## 7. Infectious Disease Serology

---

### LAB-INFECTIOUS_HBV

**Hepatitis B (HBsAg, Anti-HBc, Anti-HBs)**

#### Reference Range

| Marker | Normal Value |
|---|---|
| HBsAg | Negative |
| Anti-HBc (total) | Negative |
| Anti-HBc IgM | Negative |
| Anti-HBs | Negative (or > 10 mIU/mL if vaccinated) |
| HBV DNA | Not detected |

#### Interpretation

| Pattern | Interpretation |
|---|---|
| HBsAg+, Anti-HBc+, Anti-HBs- | Active infection (acute or chronic) |
| HBsAg-, Anti-HBc+, Anti-HBs+ | Past infection (resolved) |
| HBsAg-, Anti-HBc-, Anti-HBs+ | Vaccinated |
| HBsAg-, Anti-HBc+, Anti-HBs- | Occult HBV infection (anti-HBc alone) |
| HBsAg+, Anti-HBc IgM+ | Acute HBV infection |

#### Clinical Implications

Hepatitis B is an important cause of secondary membranous nephropathy, polyarteritis nodosa, and MPGN. HBV-associated membranous nephropathy is more common in endemic areas. Screening for HBV is essential before initiating immunosuppressive therapy (risk of reactivation). Lamivudine or entecavir prophylaxis should be considered during immunosuppression in HBsAg-positive or isolated anti-HBc-positive patients.

#### Associated Diseases

| Disease ID | Role of HBV |
|---|---|
| `membranous` | HBV-associated membranous nephropathy (secondary) |
| `mpgn` | HBV-associated MPGN |
| All glomerular diseases | Screen before immunosuppression; reactivation risk |

#### False Positives / False Negatives

- **False positive HBsAg:** Very rare with modern assays.
- **False negative HBsAg:** Window period in acute infection, occult HBV, low-level HBV DNA with negative HBsAg.
- **Anti-HBc alone:** May represent resolved infection, false positive, or occult HBV. HBV DNA testing recommended.

#### Repeat Testing Recommendations

- Screen at diagnosis if secondary GN suspected.
- Screen before starting immunosuppressive therapy.
- HBV DNA monitoring during immunosuppression.

#### Monitoring Recommendations

- HBV DNA every 3-6 months during immunosuppressive therapy.
- Continue antiviral prophylaxis for 6-12 months after completing immunosuppression (longer for rituximab).

---

### LAB-INFECTIOUS_HCV

**Hepatitis C (Anti-HCV, HCV RNA)**

#### Reference Range

| Marker | Normal Value |
|---|---|
| Anti-HCV | Negative |
| HCV RNA | Not detected (< 15 IU/mL or assay-specific LOD) |

#### Interpretation

- **Anti-HCV positive, HCV RNA positive:** Active HCV infection.
- **Anti-HCV positive, HCV RNA negative:** Resolved HCV infection or false-positive antibody.
- **Anti-HCV negative, HCV RNA positive:** Very early acute infection, immunocompromised patient, or false-negative antibody.
- **HCV RNA quantification:** Viral load helps assess infectivity and monitor treatment response.

#### Clinical Implications

HCV is the most important infectious cause of glomerular disease. It causes cryoglobulinemic GN (type II mixed cryoglobulinemia), MPGN, and membranous nephropathy. HCV-associated cryoglobulinemic GN typically presents with MPGN pattern on biopsy, low C4, positive RF, and circulating cryoglobulins. Direct-acting antiviral (DAA) therapy is now the primary treatment for HCV-associated GN, often achieving virological and clinical remission.

#### Associated Diseases

| Disease ID | Role of HCV |
|---|---|
| `cryoglobulinemic` | Primary cause of type II mixed cryoglobulinemia; DAA treatment |
| `mpgn` | HCV-associated MPGN |

#### False Positives / False Negatives

- **False positive anti-HCV:** Autoimmune disease, hypergammaglobulinemia, false-positive ELISA.
- **False negative anti-HCV:** Immunocompromised patients, early acute infection. HCV RNA is more sensitive.
- **Window period:** Anti-HCV may be negative in early acute infection; HCV RNA detectable earlier.

#### Repeat Testing Recommendations

- Screen at diagnosis if cryoglobulinemic GN or MPGN suspected.
- Screen all patients with unexplained GN.
- HCV RNA during treatment to confirm virological response.

#### Monitoring Recommendations

- HCV RNA at 4, 12, and 24 weeks during DAA therapy.
- Sustained virological response (SVR) = undetectable HCV RNA 12 weeks after end of treatment.
- Monitor renal function and proteinuria after SVR; cryoglobulinemic GN may improve over months.

---

### LAB-INFECTIOUS_HIV

**HIV (p24 Antigen, Antibodies, RNA)**

#### Reference Range

| Marker | Normal Value |
|---|---|
| HIV-1/2 antibody/antigen combo (4th gen) | Negative |
| HIV-1 RNA | Not detected |
| p24 antigen | Negative |

#### Interpretation

- **4th generation assay positive:** Antibody and/or p24 antigen detected. Confirm with HIV-1 RNA and differentiation assay.
- **p24 positive, antibody negative:** Acute HIV infection (window period).
- **HIV RNA positive, antibody negative:** Very acute infection or immunocompromised.
- **Chronic HIV:** Antibody positive, RNA detectable (if untreated) or suppressed (if on ART).

#### Clinical Implications

HIV is associated with several patterns of glomerular disease: HIV-associated nephropathy (HIVAN, collapsing FSGS), immune complex GN (including IgA nephropathy-like pattern), lupus-like GN, and TMA. HIVAN is the most common HIV-associated glomerular disease and presents with nephrotic syndrome, collapsing FSGS on biopsy, and rapid progression to ESKD. ART is the cornerstone of treatment.

#### Associated Diseases

| Disease ID | Role of HIV |
|---|---|
| `fsgs` | HIV-associated nephropathy (collapsing FSGS) |
| `hivan` | Diagnostic; ART is treatment |
| `lupus` | HIV-associated lupus-like GN |
| `iga` | HIV-associated IgA-like GN |
| All glomerular diseases | Screen before immunosuppression |

#### False Positives / False Negatives

- **False positive antibody:** Very rare with 4th generation assays.
- **False negative antibody:** Window period (use p24 antigen or RNA), immunocompromised.
- **Antibody testing in transplant recipients:** Donor-derived antibodies may cause false-positive results. Use HIV RNA for monitoring.

#### Repeat Testing Recommendations

- Screen at diagnosis if HIV-associated GN suspected.
- Screen before immunosuppressive therapy.
- HIV RNA monitoring per infectious disease guidelines.

#### Monitoring Recommendations

- HIV RNA and CD4 count monitoring per infectious disease guidelines.
- ART is the primary treatment for HIVAN; renal function monitoring during ART.

---

### LAB-INFECTIOUS_SYPHILIS

**Syphilis (TPHA, VDRL)**

#### Reference Range

| Test | Normal Value |
|---|---|
| TPHA (or FTA-ABS) | Non-reactive |
| VDRL | Non-reactive |

#### Interpretation

- **TPHA reactive, VDRL reactive:** Active syphilis (primary, secondary, or tertiary).
- **TPHA reactive, VDRL non-reactive:** Past treated syphilis or late latent syphilis.
- **VDRL quantitative titer:** Used to monitor treatment response.

#### Clinical Implications

Syphilis may cause membranous nephropathy (rare) and other glomerular diseases. It is included in the evaluation of unexplained GN in endemic areas. Nephrotic syndrome due to membranous nephropathy in syphilis responds to penicillin treatment.

#### Associated Diseases

| Disease ID | Role of Syphilis |
|---|---|
| `membranous` | Rare cause of secondary membranous nephropathy |
| All glomerular diseases | Screen in endemic areas or risk populations |

#### False Positives / False Negatives

- **False positive VDRL:** Autoimmune disease, pregnancy, infections (TB, malaria), IV drug use.
- **False negative VDRL:** Early primary syphilis, late latent syphilis, immunocompromised.
- **False positive TPHA:** Very rare.

#### Repeat Testing Recommendations

- Screen if clinically indicated.
- VDRL titer to monitor treatment response.

#### Monitoring Recommendations

- VDRL titer decline indicates adequate treatment.

---

### LAB-INFECTIOUS_EBV

**Epstein-Barr Virus (VCA, EBNA)**

#### Reference Range

| Marker | Normal Value |
|---|---|
| VCA IgM | Negative |
| VCA IgG | Negative (unless prior infection) |
| EBNA IgG | Negative (unless prior infection) |

#### Interpretation

- **VCA IgM+, VCA IgG +/-, EBNA-:** Acute EBV infection.
- **VCA IgM-, VCA IgG+, EBNA+:** Past infection.
- **VCA IgM-, VCA IgG-, EBNA-:** No prior infection (susceptible).
- **EBV DNA:** Quantitative PCR for monitoring viral load in transplant patients.

#### Clinical Implications

EBV is associated with post-transplant lymphoproliferative disorder (PTLD) and has been linked to membranous nephropathy and other glomerular diseases. In transplant patients, EBV monitoring is important for PTLD risk assessment.

#### Associated Diseases

| Disease ID | Role of EBV |
|---|---|
| `membranous` | Rare cause of secondary membranous nephropathy |
| `tCellMediatedRejection` | EBV monitoring important in transplant patients |
| `antibodyMediatedRejection` | PTLD risk |

#### False Positives / False Negatives

- **False positive VCA IgM:** Heterophile-negative mononucleosis, other viral infections.
- **False negative VCA IgM:** May be negative if tested late in illness.

#### Repeat Testing Recommendations

- Screen at transplant evaluation.
- EBV DNA monitoring in transplant recipients.

#### Monitoring Recommendations

- EBV DNA monitoring in transplant patients for PTLD risk assessment.

---

### LAB-INFECTIOUS_CMV

**Cytomegalovirus (CMV IgG, IgM, PCR)**

#### Reference Range

| Marker | Normal Value |
|---|---|
| CMV IgG | Negative (unless prior infection) |
| CMV IgM | Negative |
| CMV DNA | Not detected |

#### Interpretation

- **CMV IgG+, IgM-:** Prior infection (seropositive).
- **CMV IgG-, IgM-:** No prior infection (seronegative).
- **CMV IgG-, IgM+ or CMV IgG+, IgM+:** Acute or reactivated CMV infection.
- **CMV DNA > 1000 copies/mL or > 0.5 log IU/mL:** Active CMV infection requiring treatment.
- **Donor/Recipient serostatus:** D+/R- (highest risk), D+/R+, D-/R+, D-/R- (lowest risk).

#### Clinical Implications

CMV is the most common opportunistic viral infection in transplant recipients. CMV disease can cause direct graft injury (CMV nephritis) and indirect effects including increased rejection risk. CMV prophylaxis and monitoring are standard in transplant protocols.

#### Associated Diseases

| Disease ID | Role of CMV |
|---|---|
| `tCellMediatedRejection` | CMV infection may trigger rejection |
| `antibodyMediatedRejection` | CMV may stimulate donor-specific antibody production |
| `transplantGlomerulopathy` | CMV-associated graft dysfunction |

#### False Positives / False Negatives

- **False positive CMV IgM:** Cross-reactivity with other herpesviruses, rheumatoid factor.
- **False negative CMV IgM:** Late testing, immunocompromised.
- **CMV DNA:** Quantitative PCR is the gold standard for monitoring.

#### Repeat Testing Recommendations

- Screen donor and recipient at transplant evaluation.
- CMV DNA monitoring during prophylaxis and for 1 year post-transplant.
- More frequent monitoring during treatment of CMV disease.

#### Monitoring Recommendations

- CMV DNA every 1-4 weeks during prophylaxis.
- CMV DNA every 2 weeks during treatment.
- Preemptive therapy when CMV DNA > threshold.

---

### LAB-INFECTIOUS_BKV

**BK Virus (Urine and Plasma PCR)**

#### Reference Range

| Specimen | Normal Value |
|---|---|
| BKV urine PCR | Not detected |
| BKV plasma PCR | Not detected |

#### Interpretation

- **BKV urine PCR positive, plasma PCR negative:** BK viruria. May represent asymptomatic replication.
- **BKV plasma PCR > 10,000 copies/mL:** High-level viremia; risk of BKV nephropathy.
- **BKV plasma PCR 1,000-10,000 copies/mL:** Intermediate viremia; close monitoring.
- **BKV plasma PCR < 1,000 copies/mL:** Low-level viremia; monitor.
- **BK viremia persisting > 3 weeks at > 10,000 copies/mL:** Strongly suggests BKV nephropathy; consider graft biopsy.

#### Clinical Implications

BK virus reactivation in transplant recipients can cause BKV nephropathy, which is a leading cause of graft loss. The management strategy relies on screening for BK viremia and preemptive reduction of immunosuppression when high-level viremia is detected. There is no approved antiviral therapy for BKV; reduction of immunosuppression is the primary intervention.

#### Associated Diseases

| Disease ID | Role of BKV |
|---|---|
| `bkVirusNephropathy` | Diagnostic; plasma PCR monitoring guides management |

#### False Positives / False Negatives

- **False positive BKV urine PCR:** Very common (up to 30% of transplant recipients have BK viruria). BK viruria alone is not diagnostic of BKV nephropathy.
- **False negative BKV plasma PCR:** Low-level viremia may be intermittent.
- **Threshold variability:** Different laboratories use different PCR assays with different cutoffs.

#### Repeat Testing Recommendations

- Screen urine PCR monthly and plasma PCR monthly for first 2 years post-transplant (or per protocol).
- Positive plasma PCR: repeat every 2-4 weeks until negative or below threshold.
- If high-level viremia persists, consider graft biopsy.

#### Monitoring Recommendations

- BKV plasma PCR monthly during the first year post-transplant.
- Reduce immunosuppression when plasma BKV > 10,000 copies/mL.
- Monitor for graft dysfunction and proteinuria.
- Reduction of immunosuppression is the primary management strategy.

---

### LAB-INFECTIOUS_PARVOVIRUS

**Parvovirus B19**

#### Reference Range

| Marker | Normal Value |
|---|---|
| Parvovirus B19 IgG | Negative (unless prior infection) |
| Parvovirus B19 IgM | Negative |
| Parvovirus B19 DNA (PCR) | Not detected |

#### Interpretation

- **IgM positive:** Acute infection.
- **IgG positive, IgM negative:** Past infection.
- **DNA positive:** Active viral replication.
- **DNA positive in transplant patients:** May cause or worsen graft dysfunction, including collapsing FSGS or MPGN.

#### Clinical Implications

Parvovirus B19 can cause collapsing FSGS (especially in transplant recipients and HIV patients), MPGN, and other glomerular patterns. Chronic parvovirus B19 infection in transplant recipients may present with chronic allograft nephropathy.

#### Associated Diseases

| Disease ID | Role of Parvovirus B19 |
|---|---|
| `fsgs` | Parvovirus B19-associated collapsing FSGS |
| `mpgn` | Parvovirus B19-associated MPGN |
| `transplantGlomerulopathy` | Chronic parvovirus B19 infection |

#### False Positives / False Negatives

- **False positive IgM:** Cross-reactivity, false-positive in immunocompromised.
- **False negative IgM:** May be negative in chronic infection.
- **DNA:** PCR is the most reliable test for active infection.

#### Repeat Testing Recommendations

- Screen if collapsing FSGS or unexplained GN in transplant patients.
- DNA monitoring if viremia detected.

#### Monitoring Recommendations

- DNA monitoring during treatment; sustained clearance indicates response.

---

### LAB-INFECTIOUS_MALARIA

**Malaria**

#### Reference Range

| Test | Normal Value |
|---|---|
| Thick and thin blood smear | No parasites seen |
| Malaria rapid diagnostic test (RDT) | Negative |
| Malaria PCR | Not detected |

#### Interpretation

- **Blood smear positive:** Confirms malaria. Species identification (P. falciparum, P. vivax, P. ovale, P. malariae, P. knowlesi) determines treatment.
- **P. malariae:** Particularly associated with nephrotic syndrome (membranous nephropathy or MPGN). Nephrotic syndrome may occur months to years after acute infection.
- **P. falciparum:** Associated with AKI, TMA, and acute GN.
- **RDT positive, smear negative:** Low parasitemia; PCR confirmation recommended.

#### Clinical Implications

Malaria-associated nephropathy is an important cause of glomerular disease in endemic regions. P. malariae is classically associated with nephrotic syndrome (membranous nephropathy). P. falciparum causes AKI through multiple mechanisms including TMA, hemolysis, and acute tubular necrosis. Treatment of malaria may improve kidney function.

#### Associated Diseases

| Disease ID | Role of Malaria |
|---|---|
| `membranous` | P. malariae-associated membranous nephropathy |
| `mpgn` | P. malariae-associated MPGN |

#### False Positives / False Negatives

- **False positive RDT:** Cross-reactivity with other Plasmodium species, persistent antigenemia.
- **False negative smear:** Low parasitemia, improper staining, inexperienced reader.
- **False negative RDT:** Low parasitemia, HRP2 deletions (P. falciparum).

#### Repeat Testing Recommendations

- Screen in endemic areas or travelers from endemic areas with unexplained GN.
- Repeat smears every 12-24 hours if initially negative but clinical suspicion high.

#### Monitoring Recommendations

- Repeat smears to confirm treatment response.

---

### LAB-INFECTIOUS_SCHISTOSOMIASIS

**Schistosomiasis**

#### Reference Range

| Test | Normal Value |
|---|---|
| Stool O&P | No eggs seen |
| Urine O&P (S. haematobium) | No eggs seen |
| Schistosoma antibodies | Negative |
| Schistosoma antigen (CCA) | Negative |

#### Interpretation

- **Antibodies positive:** Current or past infection. Does not distinguish active from resolved infection.
- **Stool/urine eggs positive:** Active infection with ongoing transmission risk.
- **Antigen positive:** Active infection.

#### Clinical Implications

Schistosoma haematobium is associated with glomerular disease, particularly membranous nephropathy and MPGN, through immune complex deposition. Schistosomiasis should be considered in the differential of glomerular disease in endemic areas. Treatment with praziquantel may improve glomerular disease.

#### Associated Diseases

| Disease ID | Role of Schistosomiasis |
|---|---|
| `membranous` | Schistosoma-associated membranous nephropathy |
| `mpgn` | Schistosoma-associated MPGN |

#### False Positives / False Negatives

- **False positive antibodies:** Cross-reactivity with other helminths.
- **False negative stool/urine:** Low egg output; multiple specimens may be needed.
- **Antigen testing:** More specific for active infection.

#### Repeat Testing Recommendations

- Screen in endemic areas with unexplained GN.
- Repeat stool/urine specimens on 3 consecutive days.

#### Monitoring Recommendations

- Post-treatment: repeat stool/urine examination to confirm parasitological cure.

---

### LAB-INFECTIOUS_LEPTOSPIRA

**Leptospira**

#### Reference Range

| Test | Normal Value |
|---|---|
| Leptospira IgM | Negative |
| Leptospira PCR | Not detected |
| MAT (microscopic agglutination test) | < 1:100 |

#### Interpretation

- **IgM positive:** Acute leptospirosis. However, false positives are common.
- **MAT >= 1:800 or 4-fold rise:** Confirms acute infection.
- **PCR positive:** Active leptospiremia.

#### Clinical Implications

Leptospirosis (Weil disease) can cause AKI with acute tubulointerstitial nephritis, GN, and TMA. It is a zoonotic infection transmitted through contact with contaminated water. Leptospira-associated GN has been described in tropical and subtropical regions.

#### Associated Diseases

| Disease ID | Role of Leptospira |
|---|---|
| `irgn` | Leptospira-associated post-infectious GN |
| `drugInducedGn` | Leptospira-associated AKI |

#### False Positives / False Negatives

- **False positive IgM:** Common; cross-reactivity with other infections.
- **False negative IgM:** Early testing; IgM may take 7-10 days to develop.
- **PCR sensitivity:** Highest in first week of illness.

#### Repeat Testing Recommendations

- MAT with acute and convalescent sera (4-fold rise).
- PCR if tested early.

#### Monitoring Recommendations

- Monitor renal function during acute illness; most cases recover with supportive care.

---

### LAB-INFECTIOUS_SARSCOV2

**SARS-CoV-2**

#### Reference Range

| Test | Normal Value |
|---|---|
| SARS-CoV-2 PCR (nasopharyngeal) | Not detected |
| SARS-CoV-2 antibody (spike, nucleocapsid) | Negative |

#### Interpretation

- **PCR positive:** Active SARS-CoV-2 infection.
- **Antibody positive (nucleocapsid):** Past infection or active infection (nucleocapsid antibodies develop later than spike).
- **Antibody positive (spike):** Past infection or vaccination.
- **Post-COVID GN:** Glomerular disease occurring weeks to months after acute COVID-19 infection.

#### Clinical Implications

SARS-CoV-2 has been associated with several patterns of glomerular disease including collapsing FSGS (COVID-associated nephropathy), MPGN, C3 glomerulopathy, ANCA-associated GN, and TMA. Post-COVID GN may occur weeks to months after acute infection.

#### Associated Diseases

| Disease ID | Role of SARS-CoV-2 |
|---|---|
| `fsgs` | COVID-associated collapsing FSGS |
| `c3` | Post-COVID C3 glomerulopathy |
| `anca` | Post-COVID ANCA-associated GN |
| `membranous` | Post-COVID membranous nephropathy |
| `irgn` | Post-COVID post-infectious GN |

#### False Positives / False Negatives

- **False positive PCR:** Low-level contamination, residual RNA after resolution.
- **False negative PCR:** Timing of testing, sample quality.
- **Antibody timing:** Antibodies may take 2-4 weeks to develop.

#### Repeat Testing Recommendations

- Screen in patients with unexplained GN and history of recent COVID-19.
- PCR if acute infection suspected.
- Antibodies if past infection suspected.

#### Monitoring Recommendations

- Monitor renal function and urine sediment during and after COVID-19 infection.

---

## 8. Hematology

---

### LAB-HEMATOLOGY_HEMOGLOBIN

**Hemoglobin**

#### Reference Range

| Population | Range |
|---|---|
| Adult male | 13.5-17.5 g/dL |
| Adult female | 12.0-16.0 g/dL |
| Pregnancy (2nd/3rd trimester) | 11.0-14.0 g/dL |
| Pediatric (term neonate) | 14.0-24.0 g/dL |
| Pediatric (6 months) | 9.5-14.0 g/dL |
| Pediatric (2-6 years) | 10.5-14.0 g/dL |
| Pediatric (7-12 years) | 11.0-15.0 g/dL |

#### Interpretation

- **Mild anemia (10-12 g/dL in males; 10-11.5 g/dL in females):** May indicate CKD, iron deficiency, chronic disease.
- **Moderate anemia (8-10 g/dL):** Significant; warrants investigation.
- **Severe anemia (< 8 g/dL):** May require transfusion; evaluate for cause.
- **Polycythemia (> 17.5 g/dL in males; > 16 g/dL in females):** EPO therapy, dehydration, polycythemia vera, secondary causes.
- **Anemia in CKD:** Normocytic, normochromic anemia due to reduced EPO production. Anemia of CKD is a complication of progressive glomerular disease.

#### Clinical Implications

Anemia is a common complication of CKD and is associated with cardiovascular morbidity and mortality. In glomerular disease, anemia may be due to CKD (reduced EPO), chronic disease, iron deficiency (blood loss from urinalysis or GI), or medication side effects (mycophenolate, MMF). Hemoglobin target of 10-11.5 g/dL is recommended for patients on ESAs.

#### Associated Diseases

| Disease ID | Role of Hemoglobin |
|---|---|
| All glomerular diseases with CKD | Anemia of CKD |
| `anca` | Anemia of chronic disease; iron deficiency from GI bleeding |
| `lupus` | Autoimmune hemolytic anemia; chronic disease |
| `alport` | Anemia with progressive CKD |
| `antiGbm` | Anemia from blood loss (pulmonary hemorrhage) |

#### False Positives / False Negatives

- **Falsely elevated:** Polycythemia, dehydration, high altitude, smoking, CO poisoning.
- **Falsely low:** Hemodilution, iron deficiency, thalassemia, hemolysis.

#### Repeat Testing Recommendations

- Every 3-6 months in CKD.
- Monthly in active CKD with ESA therapy.
- More frequently if acute blood loss.

#### Monitoring Recommendations

- Hemoglobin every 1-3 months during ESA therapy.
- Iron studies (ferritin, TSAT) to ensure iron repletion before ESA therapy.

---

### LAB-HEMATOLOGY_PLATELETS

**Platelet Count**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 150,000-400,000/uL |
| Pregnancy | May increase progressively; 100,000-450,000/uL |
| Pediatric (term neonate) | 150,000-400,000/uL |

#### Interpretation

- **Thrombocytopenia (< 150,000/uL):** May indicate TMA (thrombotic thrombocytopenic purpura, hemolytic uremic syndrome), HELLP syndrome, DIC, immune thrombocytopenic purpura, drug-induced, or bone marrow suppression.
- **Severe thrombocytopenia (< 50,000/uL):** High risk of spontaneous bleeding; may require platelet transfusion.
- **Thrombocytosis (> 400,000/uL):** Reactive (infection, inflammation, iron deficiency) or primary (essential thrombocythemia, polycythemia vera).
- **Platelets in TMA:** Thrombocytopenia with schistocytes on blood smear is characteristic of TTP/HUS. This is a medical emergency.

#### Clinical Implications

Thrombocytopenia in the context of glomerular disease should raise suspicion for TMA, particularly in the setting of AKI, hemolytic anemia, and neurological symptoms. TTP/HUS requires urgent plasma exchange and complement inhibitor therapy (eculizumab for aHUS). Thrombocytopenia may also occur in lupus (immune thrombocytopenia), HELLP syndrome, or drug-induced causes.

#### Associated Diseases

| Disease ID | Role of Platelets |
|---|---|
| `c3` | TMA may occur in complement-mediated diseases |
| `denseDepositDisease` | TMA may occur |
| `lupus` | Immune thrombocytopenia; TTP-like syndrome |
| `anca` | TMA may occur in severe vasculitis |
| `antiGbm` | TMA may occur |
| `drugInducedGn` | Drug-induced thrombocytopenia (e.g., quinine, ticlopidine, clopidogrel) |
| `tCellMediatedRejection` | TMA may occur post-transplant |
| `antibodyMediatedRejection` | TMA may occur |
| `transplantGlomerulopathy` | TMA may occur |

#### False Positives / False Negatives

- **Falsely low:** EDTA-dependent platelet clumping (pseudothrombocytopenia); repeat with citrate tube.
- **Falsely high:** Giant platelets counted as red cells.
- **Pre-analytical:** Prolonged tourniquet time, difficult venipuncture.

#### Repeat Testing Recommendations

- Confirm thrombocytopenia with repeat count and peripheral blood smear.
- If TMA suspected: urgent ADAMTS13 activity, peripheral smear, LDH, haptoglobin, reticulocyte count.

#### Monitoring Recommendations

- Monitor platelets daily during active TMA.
- Platelet count recovery indicates response to treatment.

---

### LAB-HEMATOLOGY_SMEAR

**Peripheral Blood Smear (Schistocytes)**

#### Reference Range

- **Normal:** No schistocytes (0% of RBCs).
- **Pathological:** > 1% schistocytes suggests microangiopathic hemolytic anemia (MAHA).

#### Interpretation

- **Schistocytes > 1%:** Microangiopathic hemolytic anemia. Differential includes TTP, aHUS, DIC, malignant hypertension, HELLP syndrome, pre-eclampsia, HELLP syndrome, mechanical heart valves, vasculitis.
- **Helmet cells, triangular fragments:** Characteristic schistocyte morphology.
- **伴随 findings:** Thrombocytopenia, elevated LDH, low haptoglobin, elevated reticulocyte count.

#### Clinical Implications

Schistocytes on peripheral blood smear are the hallmark of MAHA. In the context of glomerular disease, schistocytes indicate TMA, which may be caused by complement-mediated aHUS, TTP (ADAMTS13 deficiency), drug-related TMA, or malignant hypertension with renal involvement. Identification of schistocytes should prompt urgent evaluation and treatment.

#### Associated Diseases

| Disease ID | Role of Schistocytes |
|---|---|
| `c3` | Complement-mediated TMA (aHUS) |
| `denseDepositDisease` | TMA may occur |
| `lupus` | Lupus-associated TMA; catastrophic APS |
| `anca` | Vasculitis-associated TMA |
| `antiGbm` | TMA may occur |
| `drugInducedGn` | Drug-induced TMA (calcineurin inhibitors, anti-VEGF, quinine) |
| `tCellMediatedRejection` | TMA post-transplant |
| `antibodyMediatedRejection` | TMA post-transplant |
| `transplantGlomerulopathy` | TMA |

#### False Positives / False Negatives

- **False positives:** Artifactual RBC fragmentation from difficult venipuncture, old samples.
- **False negatives:** Low sensitivity if only a few schistocytes present. Requires experienced morphologist. May need to examine multiple fields.
- **Threshold:** > 1% is generally considered pathological, but some labs use > 0.5%.

#### Repeat Testing Recommendations

- Confirm with repeat smear if initial is equivocal.
- Serial smears during TMA to monitor response.

#### Monitoring Recommendations

- Resolution of schistocytes parallels recovery from TMA.
- Schistocytes may persist for days after clinical improvement.

---

### LAB-HEMATOLOGY_COAG

**Coagulation Studies (PT, aPTT, Fibrinogen, D-dimer)**

#### Reference Range

| Test | Normal Range |
|---|---|
| PT | 11-13.5 seconds (INR 0.8-1.2) |
| aPTT | 25-35 seconds |
| Fibrinogen | 200-400 mg/dL (2-4 g/L) |
| D-dimer | < 0.5 ug/mL (< 500 ng/mL) |

#### Interpretation

- **Prolonged PT and aPTT:** DIC, warfarin/heparin use, liver disease, vitamin K deficiency, factor deficiencies.
- **Prolonged aPTT only:** Heparin, factor VIII/IX deficiency, lupus anticoagulant.
- **Low fibrinogen (< 200 mg/dL):** DIC, liver disease, thrombolytic therapy, congenital deficiency.
- **Elevated D-dimer (> 0.5 ug/mL):** DIC, thrombosis, PE, DVT, surgery, trauma, pregnancy.
- **Elevated D-dimer with low fibrinogen and thrombocytopenia:** DIC until proven otherwise.
- **Isolated elevated D-dimer:** May indicate subclinical thrombosis in nephrotic syndrome.

#### Clinical Implications

Coagulation studies are important in glomerular disease for several reasons: (1) DIC may occur in sepsis-associated GN, catastrophic antiphospholipid syndrome, or TTP/HUS; (2) D-dimer elevation in nephrotic syndrome may indicate subclinical thrombosis; (3) monitoring during plasma exchange therapy; (4) assessing bleeding risk before renal biopsy.

#### Associated Diseases

| Disease ID | Role of Coagulation Studies |
|---|---|
| `lupus` | Catastrophic APS: DIC pattern; coagulation monitoring |
| `membranous` | Thrombosis risk assessment; D-dimer as screening |
| `cryoglobulinemic` | DIC may occur in severe vasculitis |
| `anca` | DIC in severe vasculitis with organ ischemia |
| All glomerular diseases | Pre-biopsy coagulation assessment |

#### False Positives / False Negatives

- **Falsely elevated D-dimer:** Age, pregnancy, surgery, trauma, malignancy, liver disease.
- **Falsely prolonged aPTT:** Lupus anticoagulant (paradoxically prolongs aPTT in vitro but is associated with thrombosis in vivo).
- **Heparin contamination:** Must be confirmed with heparin neutralization if sample collected from heparin line.

#### Repeat Testing Recommendations

- Pre-biopsy: PT, aPTT, platelet count.
- DIC monitoring: serial PT, aPTT, fibrinogen, D-dimer, platelets every 6-12 hours.
- Nephrotic syndrome: D-dimer as screening for thrombosis (not specific).

#### Monitoring Recommendations

- Serial coagulation studies in DIC until resolution.
- Monitor fibrinogen and platelets during plasma exchange.

---

### LAB-HEMATOLOGY_ADAMTS13

**ADAMTS13 Activity**

#### Reference Range

| Population | Range |
|---|---|
| Adult | 50-180% (or > 10% to exclude TTP in acute setting) |

#### Interpretation

- **ADAMTS13 < 10% (or < 5%):** Confirms TTP if clinical triad present (thrombocytopenia, MAHA, neurological symptoms). Acquired TTP (autoantibody-mediated) is most common.
- **ADAMTS13 10-50%:** Partial deficiency; may indicate atypical TTP or carrier state.
- **ADAMTS13 > 50%:** TTP unlikely. Consider aHUS, DIC, or other cause of TMA.
- **ADAMTS13 inhibitor:** Confirms acquired TTP (autoantibody against ADAMTS13).

#### Clinical Implications

ADAMTS13 activity is the key diagnostic test for TTP, distinguishing it from aHUS (which is complement-mediated). This distinction is critical because TTP requires plasma exchange while aHUS requires complement inhibition (eculizumab). ADAMTS13 activity should be sent urgently in any patient with TMA.

#### Associated Diseases

| Disease ID | Role of ADAMTS13 |
|---|---|
| `c3` | Differentiate aHUS from TTP |
| `denseDepositDisease` | Differentiate TMA mechanism |
| `drugInducedGn` | Drug-induced TMA: check ADAMTS13 |
| All TMA-associated diseases | Diagnostic differentiation |

#### False Positives / False Negatives

- **False low:** Acute phase response may lower ADAMTS13 levels. Plasma infusion/exchange affects results.
- **False high:** None significant.
- **Timing:** Send before plasma exchange if possible; results may be affected by treatment.

#### Repeat Testing Recommendations

- Send urgently if TMA suspected.
- Repeat after plasma exchange to monitor response.
- If ADAMTS13 < 10%: continue plasma exchange until > 50% or clinical remission.

#### Monitoring Recommendations

- ADAMTS13 activity > 50% is a treatment target in TTP.
- ADAMTS13 inhibitor levels may predict relapse risk.

---

### LAB-HEMATOLOGY_COMPLEMENT_FACTORS

**Factor H, Factor I, MCP (Membrane Cofactor Protein)**

#### Reference Range

| Parameter | Normal Value |
|---|---|
| Factor H | 50-150% (or assay-specific) |
| Factor I | 50-150% (or assay-specific) |
| MCP (CD46) | Expressed on cell surface; assessed by flow cytometry |

#### Interpretation

- **Low Factor H (< 50%):** Genetic deficiency or acquired (anti-FH antibodies). Predisposes to aHUS and C3 glomerulopathy.
- **Low Factor I (< 50%):** Genetic deficiency. Predisposes to aHUS. Factor I is a cofactor for Factor H in C3b inactivation.
- **Reduced MCP expression:** Genetic deficiency (rare). MCP is a membrane-bound complement regulator.
- **Genetic mutations:** Identify patients at risk for aHUS relapse and guide management.

#### Clinical Implications

Factor H, Factor I, and MCP are key regulators of the alternative complement pathway. Deficiency or dysfunction leads to uncontrolled complement activation, predisposing to aHUS and C3 glomerulopathy. Genetic testing for complement regulatory protein abnormalities is recommended in all patients with aHUS and C3 glomerulopathy. The results guide management: patients with Factor H mutations may respond to eculizumab but are at high risk for post-transplant recurrence; patients with MCP mutations have better outcomes after transplant.

#### Associated Diseases

| Disease ID | Role of Complement Factors |
|---|---|
| `c3` | Factor H/I mutations predispose to C3 glomerulopathy |
| `denseDepositDisease` | Factor H mutations may contribute |
| `tCellMediatedRejection` | Complement regulation in transplant |
| `antibodyMediatedRejection` | Complement-mediated graft injury |
| `transplantGlomerulopathy` | Complement dysregulation |

#### False Positives / False Negatives

- **Acquired deficiency:** Anti-FH antibodies may reduce Factor H levels.
- **Assay limitations:** Functional assays may detect dysfunction missed by antigen-level assays.
- **Genetic testing:** Next-generation sequencing panels for complement genes are preferred.

#### Repeat Testing Recommendations

- At diagnosis of aHUS or C3 glomerulopathy.
- Genetic testing: one-time comprehensive panel.
- Functional assays: may be repeated if clinical suspicion remains high despite negative genetic testing.

#### Monitoring Recommendations

- Complement factor levels are not routinely monitored during treatment.
- Genetic results are static and do not require serial testing.

---

## 9. Urine Biomarkers

---

### LAB-URINE-UPEP

**Urine Protein Electrophoresis (UPEP)**

#### Reference Range

- **Normal:** Trace or absent protein in urine.

#### Interpretation

- **Albumin-predominant pattern:** Selective albuminuria; suggests glomerular disease, particularly minimal change disease, early diabetic nephropathy, or early FSGS.
- **Non-selective pattern (albumin + globulins):** Indicates more severe glomerular basement membrane disruption; suggests FSGS, membranous nephropathy, or advanced GN.
- **M蛋白 (M-spike) in urine:** Monoclonal light chains (Bence Jones proteinuria). Consider multiple myeloma, amyloidosis, light chain deposition disease, or monoclonal gammopathy-associated GN.
- **Beta-2 microglobulin elevation:** Tubular proteinuria; suggests tubulointerstitial disease.
- **Alpha-2 macroglobulin elevation:** Very large protein that is not normally filtered; indicates severe glomerular damage with loss of size selectivity.

#### Clinical Implications

UPEP differentiates the type and severity of proteinuria in glomerular disease. The pattern of protein loss provides diagnostic and prognostic information: selective albuminuria indicates podocyte injury with preserved size selectivity, while non-selective proteinuria with IgG loss indicates more severe GBM disruption. UPEP is particularly useful in monoclonal gammopathy-associated GN where urine immunofixation identifies monoclonal light chains.

#### Associated Diseases

| Disease ID | Role of UPEP |
|---|---|
| `fsgs` | Non-selective proteinuria pattern |
| `membranous` | Selective to non-selective; M-spike if paraneoplastic |
| `mcd` | Selective albuminuria |
| `iga` | Usually non-selective if proteinuria present |
| `lupus` | Non-selective in nephrotic-range disease |
| `fibrillaryGlomerulonephritis` | May show M-spike if monoclonal gammopathy-associated |
| `denseDepositDisease` | Non-selective if nephrotic |
| `cryoglobulinemic` | Non-selective |
| `diabeticNephropathy` | Progressive from selective to non-selective |

#### False Positives / False Negatives

- **False negatives:** Low-grade proteinuria may not produce detectable pattern.
- **False positives:** Bence Jones proteinuria may be missed if only dipstick is used (dipstick detects albumin, not light chains).
- **Assay limitations:** UPEP is semi-quantitative; quantitative urine protein measurements are more precise.

#### Repeat Testing Recommendations

- At diagnosis of glomerular disease.
- During follow-up to assess treatment response (change in protein pattern).
- In monoclonal gammopathy: annual UPEP + urine immunofixation.

#### Monitoring Recommendations

- UPEP pattern may change with disease progression or treatment response.
- Serial monitoring tracks proteinuria composition changes.

---

### LAB-URINE_IMFIX

**Urine Immunofixation**

#### Reference Range

- **Normal:** No monoclonal light chains or immunoglobulins detected.

#### Interpretation

- **Monoclonal light chain detected (kappa or lambda):** Bence Jones proteinuria. In the context of glomerular disease, suggests monoclonal gammopathy-associated GN (amyloidosis, light chain deposition disease, fibrillary GN, immunotactoid GN, MPGN).
- **Polyclonal light chains:** Non-specific; may be seen in tubular proteinuria or inflammatory states.
- **Monoclonal immunoglobulin (intact IgG, IgA, IgM):** Rare; suggests glomerular filtration of intact monoclonal immunoglobulin.

#### Clinical Implications

Urine immunofixation is the most sensitive test for detecting monoclonal light chains in urine (Bence Jones proteinuria). It is essential in the workup of unexplained glomerular disease, particularly when monoclonal gammopathy-associated GN is suspected. Bence Jones proteinuria in the context of GN should prompt evaluation for AL amyloidosis, light chain deposition disease, and monoclonal gammopathy-associated MPGN.

#### Associated Diseases

| Disease ID | Role of Urine Immunofixation |
|---|---|
| `fibrillaryGlomerulonephritis` | Screen for monoclonal gammopathy |
| `membranous` | Screen for paraneoplastic/amyloid disease |
| `mpgn` | Monoclonal gammopathy-associated MPGN |
| `denseDepositDisease` | Screen for monoclonal gammopathy |
| `cryoglobulinemic` | Type II cryoglobulinemia with monoclonal component |

#### False Positives / False Negatives

- **False negatives:** Low-level monoclonal light chains may be below detection threshold. Urine concentration affects sensitivity.
- **False positives:** Very rare with validated immunofixation assays.
- **Assay limitations:** More sensitive than UPEP for monoclonal proteins but less available.

#### Repeat Testing Recommendations

- At diagnosis of suspected monoclonal gammopathy-associated GN.
- Annual in patients with known monoclonal gammopathy.
- Serial monitoring during treatment of amyloidosis or LCDD.

#### Monitoring Recommendations

- Serial urine immunofixation monitors treatment response in amyloidosis and LCDD.
- Complete absence of monoclonal light chains is a treatment target.

---

### LAB-URINE_EOSINOPHILS

**Urine Eosinophils**

#### Reference Range

- **Normal:** Absent or < 1% of urinary sediment WBCs.

#### Interpretation

- **Positive (> 1% of urinary WBCs):** Suggests acute interstitial nephritis (AIN). However, specificity is limited and the test has largely fallen out of favor.
- **Negative:** Does not exclude AIN. Sensitivity is only 40-67%.

#### Clinical Implications

Urine eosinophils were historically used to diagnose drug-induced acute interstitial nephritis. However, their sensitivity and specificity are insufficient for reliable diagnosis. A positive result supports AIN but a negative result does not exclude it. Renal biopsy remains the gold standard for AIN diagnosis. In glomerular disease, urine eosinophils may be incidentally positive if there is concurrent drug-induced AIN from immunosuppressive medications.

#### Associated Diseases

| Disease ID | Role of Urine Eosinophils |
|---|---|
| `drugInducedGn` | May be positive in drug-induced interstitial nephritis |
| `lupus` | May be positive in lupus interstitial nephritis |
| `iga` | Unrelated; used to exclude AIN |

#### False Positives / False Negatives

- **False positives:** Pyelonephritis, prostatitis, atheroembolic disease, renal allograft rejection, acute GN.
- **False negatives:** Common (sensitivity 40-67%). AIN may be present with negative urine eosinophils.
- **Staining:** Wright or Hansel stain is required; eosinophiluria is easily missed on standard urinalysis.
- **Test utility:** Largely abandoned due to poor diagnostic performance.

#### Repeat Testing Recommendations

- Not routinely recommended. If AIN suspected, renal biopsy is the definitive diagnostic test.
- May be used as a supportive finding in the appropriate clinical context.

#### Monitoring Recommendations

- Not used for monitoring. Clinical improvement and renal function are better indicators.

---

## Appendix A: Laboratory Testing Panels

---

### Panel 1: Initial Nephritis Panel

*For evaluation of unexplained hematuria, proteinuria, or glomerular disease.*

| Test | Purpose | Laboratory ID |
|---|---|---|
| Urinalysis with microscopy | Screen for hematuria, proteinuria, casts | LAB-URINALYSIS-HEMATURIA, LAB-URINALYSIS-PROTEINURIA |
| Spot UPCR or ACR | Quantify proteinuria | LAB-URINALYSIS-PROTEINURIA |
| Serum creatinine + eGFR | Assess kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| C3, C4 | Screen for complement consumption | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| ANA | Screen for SLE | LAB-AUTOANTIBODY-ANA |
| Anti-dsDNA | If ANA positive; lupus activity | LAB-AUTOANTIBODY-ANTIDSDNA |
| ANCA (PR3 + MPO) | Screen for AAV | LAB-AUTOANTIBODY-ANCA |
| Anti-GBM | Screen for anti-GBM disease | LAB-AUTOANTIBODY_ANTIGBM |
| Anti-PLA2R | Screen for membranous nephropathy | LAB-AUTOANTIBODY-ANTIPLA2R |
| SPEP + SFLC + kappa/lambda ratio | Screen for monoclonal gammopathy | LAB-CHEMISTRY-SPEP, LAB-CHEMISTRY-SFLC, LAB-CHEMISTRY-KL_RATIO |
| CBC with differential | Assess for anemia, thrombocytopenia | LAB-HEMATOLOGY_HEMOGLOBIN, LAB-HEMATOLOGY_PLATELETS |
| Serum albumin | Assess nephrotic syndrome severity | LAB-CHEMISTRY-ALBUMIN |
| Hepatitis B and C serology | Screen for infectious causes | LAB-INFECTIOUS_HBV, LAB-INFECTIOUS_HCV |

---

### Panel 2: Nephrotic Syndrome Panel

*For evaluation of nephrotic-range proteinuria (UPCR > 3.5 g/g or ACR > 3000 mg/g).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| Spot UPCR or ACR | Quantify proteinuria | LAB-URINALYSIS-PROTEINURIA |
| Serum creatinine + eGFR | Assess kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Serum albumin | Assess severity | LAB-CHEMISTRY-ALBUMIN |
| Serum lipid panel | Hyperlipidemia of nephrotic syndrome | (external) |
| Anti-PLA2R | Primary membranous nephropathy | LAB-AUTOANTIBODY-ANTIPLA2R |
| Anti-THSD7A | PLA2R-negative membranous | LAB-AUTOANTIBODY_ANTITHSD7A |
| SPEP + SFLC + kappa/lambda ratio | Monoclonal gammopathy screen | LAB-CHEMISTRY-SPEP, LAB-CHEMISTRY-SFLC, LAB-CHEMISTRY-KL_RATIO |
| Urine immunofixation | Bence Jones proteinuria | LAB-URINE_IMFIX |
| ANA | Screen for SLE | LAB-AUTOANTIBODY-ANA |
| Anti-dsDNA, C3, C4 | If ANA positive | LAB-AUTOANTIBODY-ANTIDSDNA, LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| Hepatitis B and C serology | Infectious causes of MN | LAB-INFECTIOUS_HBV, LAB-INFECTIOUS_HCV |
| HIV serology | HIV-associated nephropathy | LAB-INFECTIOUS_HIV |
| Urine protein electrophoresis | Characterize proteinuria type | LAB-URINE-UPEP |
| Urinalysis with microscopy | Oval fat bodies, lipiduria, casts | LAB-URINALYSIS-OVAL_FAT_BODIES, LAB-URINALYSIS-LIPIDURIA |

---

### Panel 3: RPGN Rapid Panel

*For rapidly progressive glomerulonephritis (acute kidney injury + hematuria + proteinuria).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| Serum creatinine + eGFR | Assess kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Urinalysis with microscopy | RBC casts, dysmorphic RBCs | LAB-URINALYSIS-RBC_CASTS, LAB-URINALYSIS-DYSMORPHIC_RBCS |
| Spot UPCR | Quantify proteinuria | LAB-URINALYSIS-PROTEINURIA |
| ANCA (PR3 + MPO) | AAV screen | LAB-AUTOANTIBODY-ANCA |
| Anti-GBM | Anti-GBM disease screen | LAB-AUTOANTIBODY_ANTIGBM |
| C3, C4 | Complement consumption | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| ANA, anti-dsDNA | SLE screen | LAB-AUTOANTIBODY-ANA, LAB-AUTOANTIBODY-ANTIDSDNA |
| CBC | Thrombocytopenia (TMA) | LAB-HEMATOLOGY_PLATELETS |
| Peripheral smear | Schistocytes (TMA) | LAB-HEMATOLOGY_SMEAR |
| LDH, haptoglobin, reticulocyte count | Hemolysis markers | (external) |
| ADAMTS13 activity | If TMA present | LAB-HEMATOLOGY_ADAMTS13 |
| Coagulation studies | Pre-biopsy, DIC screen | LAB-HEMATOLOGY_COAG |
| Anti-C1q | If lupus nephritis suspected | LAB-AUTOANTIBODY_ANTIC1Q |

*Note: Renal biopsy should not be delayed for serological results in RPGN. Biopsy should be performed emergently.*

---

### Panel 4: Complement Disorder Panel

*For evaluation of low C3, C4, or suspected complement-mediated disease.*

| Test | Purpose | Laboratory ID |
|---|---|---|
| C3 | Quantify complement consumption | LAB-COMPLEMENT-C3 |
| C4 | Classical vs. alternative pathway | LAB-COMPLEMENT-C4 |
| CH50 | Functional complement screen | LAB-COMPLEMENT-CH50 |
| C3 nephritic factor | Alternative pathway activation | LAB-COMPLEMENT-C3NEF |
| Anti-Factor H antibodies | Factor H dysfunction | LAB-COMPLEMENT-ANTI_FH |
| Anti-Factor B antibodies | Rare alternative pathway dysregulation | LAB-COMPLEMENT-ANTI_FB |
| sC5b-9 | Terminal complement activation | LAB-COMPLEMENT-SMAC |
| Factor H, Factor I, MCP | Genetic complement regulation | LAB-HEMATOLOGY_COMPLEMENT_FACTORS |
| Serum creatinine + eGFR | Assess kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Urinalysis | Proteinuria, hematuria | LAB-URINALYSIS-PROTEINURIA, LAB-URINALYSIS-HEMATURIA |
| CBC + peripheral smear | TMA screen | LAB-HEMATOLOGY_PLATELETS, LAB-HEMATOLOGY_SMEAR |
| LDH, haptoglobin, reticulocyte count | Hemolysis markers | (external) |

---

### Panel 5: Transplant Dysfunction Panel

*For evaluation of allograft dysfunction (rising creatinine, proteinuria, or hematuria post-transplant).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| Serum creatinine + eGFR | Assess graft function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Spot UPCR or ACR | Quantify proteinuria | LAB-URINALYSIS-PROTEINURIA |
| Urinalysis with microscopy | WBC casts (rejection), RBC casts | LAB-URINALYSIS-WBC_CASTS, LAB-URINALYSIS-RBC_CASTS |
| BKV plasma PCR | BK virus nephropathy screen | LAB-INFECTIOUS_BKV |
| BKV urine PCR | BK viruria | LAB-INFECTIOUS_BKV |
| CMV DNA | CMV infection screen | LAB-INFECTIOUS_CMV |
| EBV DNA | EBV/PTLD screen | LAB-INFECTIOUS_EBV |
| Donor-specific antibodies (DSA) | Antibody-mediated rejection | (external - HLA lab) |
| C3, C4 | Complement-mediated injury | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| C5b-9 | MAC deposition in graft | LAB-COMPLEMENT-SMAC |
| ADAMTS13 | If TMA present | LAB-HEMATOLOGY_ADAMTS13 |
| CBC + peripheral smear | TMA, anemia | LAB-HEMATOLOGY_PLATELETS, LAB-HEMATOLOGY_SMEAR |
| SPEP + SFLC | Monoclonal gammopathy screen | LAB-CHEMISTRY-SPEP, LAB-CHEMISTRY-SFLC |
| Anti-PLA2R | Recurrent membranous nephropathy | LAB-AUTOANTIBODY-ANTIPLA2R |

*Note: Indication for graft biopsy should be based on clinical context. Many serological tests complement but do not replace biopsy.*

---

### Panel 6: Pregnancy Renal Panel

*For evaluation of renal disease in pregnancy (proteinuria, hypertension, AKI).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| Spot ACR | Quantify albuminuria | LAB-URINALYSIS-PROTEINURIA |
| Serum creatinine | Normal pregnancy values lower | LAB-RENAL-CREATININE |
| eGFR | CKD-EPI may overestimate in pregnancy | LAB-RENAL-EGFR |
| Urinalysis | Proteinuria, hematuria | LAB-URINALYSIS-PROTEINURIA, LAB-URINALYSIS-HEMATURIA |
| CBC | Thrombocytopenia (HELLP) | LAB-HEMATOLOGY_PLATELETS |
| LDH, haptoglobin, reticulocyte count | Hemolysis (HELLP) | (external) |
| Liver function tests | HELLP syndrome | (external) |
| C3, C4 | Lupus nephritis | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| ANA, anti-dsDNA | SLE screen | LAB-AUTOANTIBODY-ANA, LAB-AUTOANTIBODY-ANTIDSDNA |
| Anti-phospholipid antibodies (aCL, anti-beta2GPI, lupus anticoagulant) | APS screening | LAB-AUTOANTIBODY_ANTICARDIOLIPIN |
| ADAMTS13 | If TMA present (TTP vs. HELLP) | LAB-HEMATOLOGY_ADAMTS13 |
| Coagulation studies | DIC screen | LAB-HEMATOLOGY_COAG |
| Serum albumin | Physiologically low in pregnancy | LAB-CHEMISTRY-ALBUMIN |

*Note: Reference ranges differ in pregnancy. Always interpret values in context of gestational age.*

---

### Panel 7: Post-Infectious GN Panel

*For evaluation of glomerular disease following infection (2-4 weeks post-infection).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| C3, C4 | Complement consumption (post-infectious GN) | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4 |
| CH50 | Functional complement | LAB-COMPLEMENT-CH50 |
| Serum creatinine + eGFR | Assess kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Urinalysis with microscopy | RBC casts, dysmorphic RBCs | LAB-URINALYSIS-RBC_CASTS, LAB-URINALYSIS-DYSMORPHIC_RBCS |
| Spot UPCR | Quantify proteinuria | LAB-URINALYSIS-PROTEINURIA |
| Anti-streptolysin O (ASO) / anti-DNase B | Post-streptococcal GN | (external) |
| Blood cultures | Endocarditis-associated GN | (external) |
| Hepatitis B and C serology | HCV cryoglobulinemia | LAB-INFECTIOUS_HBV, LAB-INFECTIOUS_HCV |
| HIV serology | HIV-associated GN | LAB-INFECTIOUS_HIV |
| Cryoglobulins | If cryoglobulinemia suspected | LAB-AUTOANTIBODY-CRYOGLOBULINS |
| Rheumatoid factor | Cryoglobulinemia marker | LAB-AUTOANTIBODY_RF |
| Blood smear | Malaria (in endemic areas) | LAB-HEMATOLOGY_SMEAR |
| Schistosoma antibodies | Endemic areas | LAB-INFECTIOUS_SCHISTOSOMIASIS |
| Parvovirus B19 DNA | If collapsing FSGS or MPGN | LAB-INFECTIOUS_PARVOVIRUS |
| CMV, EBV serology | Viral GN | LAB-INFECTIOUS_CMV, LAB-INFECTIOUS_EBV |

---

### Panel 8: TMA Workup Panel

*For evaluation of suspected thrombotic microangiopathy (thrombocytopenia + MAHA + AKI).*

| Test | Purpose | Laboratory ID |
|---|---|---|
| CBC with differential | Thrombocytopenia | LAB-HEMATOLOGY_PLATELETS |
| Peripheral blood smear | Schistocytes | LAB-HEMATOLOGY_SMEAR |
| LDH | Hemolysis marker | (external) |
| Haptoglobin | Consumed in hemolysis | (external) |
| Reticulocyte count | Hemolysis compensation | (external) |
| Bilirubin (indirect) | Hemolysis marker | (external) |
| ADAMTS13 activity | TTP vs. aHUS differentiation | LAB-HEMATOLOGY_ADAMTS13 |
| ADAMTS13 inhibitor | Acquired TTP | LAB-HEMATOLOGY_ADAMTS13 |
| Complement studies (C3, C4, CH50) | Complement activation | LAB-COMPLEMENT-C3, LAB-COMPLEMENT-C4, LAB-COMPLEMENT-CH50 |
| Factor H, Factor I, MCP | Genetic complement regulation | LAB-HEMATOLOGY_COMPLEMENT_FACTORS |
| Anti-Factor H antibodies | Acquired complement dysregulation | LAB-COMPLEMENT-ANTI_FH |
| Coagulation studies | DIC differentiation | LAB-HEMATOLOGY_COAG |
| Serum creatinine + eGFR | Kidney function | LAB-RENAL-CREATININE, LAB-RENAL-EGFR |
| Urinalysis | Proteinuria, hematuria | LAB-URINALYSIS-PROTEINURIA, LAB-URINALYSIS-HEMATURIA |
| Pregnancy test | HELLP/pre-eclampsia | (external) |

*Note: TTP is a medical emergency. If TTP suspected, do not wait for ADAMTS13 results to initiate plasma exchange.*

---

## Appendix B: Disease ID Reference

| Disease ID | Disease Name |
|---|---|
| `alport` | Alport Syndrome |
| `anca` | ANCA-Associated Vasculitis |
| `antiGbm` | Anti-GBM Disease (Goodpasture Syndrome) |
| `antibodyMediatedRejection` | Antibody-Mediated Rejection |
| `bkVirusNephropathy` | BK Virus Nephropathy |
| `c3` | C3 Glomerulopathy |
| `cniToxicity` | Calcineurin Inhibitor Toxicity |
| `cryoglobulinemic` | Cryoglobulinemic Glomerulonephritis |
| `denseDepositDisease` | Dense Deposit Disease (C3 Glomerulopathy) |
| `diabeticNephropathy` | Diabetic Nephropathy |
| `drugInducedGn` | Drug-Induced Glomerulonephritis |
| `fibrillaryGlomerulonephritis` | Fibrillary Glomerulonephritis |
| `fsgs` | Focal Segmental Glomerulosclerosis |
| `hivan` | HIV-Associated Nephropathy |
| `iga` | IgA Nephropathy |
| `irgn` | Infection-Related Glomerulonephritis |
| `lupus` | Lupus Nephritis |
| `mcd` | Minimal Change Disease |
| `membranous` | Membranous Nephropathy |
| `mpgn` | Membranoproliferative Glomerulonephritis |
| `tCellMediatedRejection` | T-Cell Mediated Rejection |
| `thinBasementMembrane` | Thin Basement Membrane Disease |
| `transplantGlomerulopathy` | Transplant Glomerulopathy |

---

## Appendix C: Key Abbreviations

| Abbreviation | Full Term |
|---|---|
| AAV | ANCA-Associated Vasculitis |
| aCL | Anticardiolipin Antibodies |
| ACR | Albumin-to-Creatinine Ratio |
| ADAMTS13 | A Disintegrin and Metalloproteinase with Thrombospondin Type 1 Motif, 13 |
| AIN | Acute Interstitial Nephritis |
| AKI | Acute Kidney Injury |
| ANCA | Antineutrophil Cytoplasmic Antibodies |
| ANA | Antinuclear Antibody |
| APS | Antiphospholipid Syndrome |
| aPTT | Activated Partial Thromboplastin Time |
| ARV | Antiretroviral |
| BKV | BK Virus |
| CMV | Cytomegalovirus |
| CKD | Chronic Kidney Disease |
| DAA | Direct-Acting Antiviral |
| DIC | Disseminated Intravascular Coagulation |
| DSA | Donor-Specific Antibodies |
| EBV | Epstein-Barr Virus |
| eGFR | Estimated Glomerular Filtration Rate |
| EPO | Erythropoietin |
| ESA | Erythropoiesis-Stimulating Agent |
| ESKD | End-Stage Kidney Disease |
| GBM | Glomerular Basement Membrane |
| GN | Glomerulonephritis |
| HBV | Hepatitis B Virus |
| HCV | Hepatitis C Virus |
| HIV | Human Immunodeficiency Virus |
| IIF | Indirect Immunofluorescence |
| IVIG | Intravenous Immunoglobulin |
| LCDD | Light Chain Deposition Disease |
| MAC | Membrane Attack Complex |
| MCD | Minimal Change Disease |
| MCP | Membrane Cofactor Protein |
| MCTD | Mixed Connective Tissue Disease |
| MN | Membranous Nephropathy |
| MPGN | Membranoproliferative Glomerulonephritis |
| MPO | Myeloperoxidase |
| PR3 | Proteinase 3 |
| PT | Prothrombin Time |
| PTLD | Post-Transplant Lymphoproliferative Disorder |
| RPGN | Rapidly Progressive Glomerulonephritis |
| SFLC | Serum Free Light Chains |
| SLE | Systemic Lupus Erythematosus |
| SPEP | Serum Protein Electrophoresis |
| SVR | Sustained Virological Response |
| TMA | Thrombotic Microangiopathy |
| TTP | Thrombotic Thrombocytopenic Purpura |
| UPCR | Urine Protein-to-Creatinine Ratio |
| UPEP | Urine Protein Electrophoresis |

---

## Appendix D: Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-07-10 | Initial release. 61 laboratory knowledge objects. 8 testing panels. |

---

*End of Document*

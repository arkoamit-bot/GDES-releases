# Differential Diagnosis Library
**Document ID:** GDES-V4.2-DDX-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Differential Diagnosis Engine

---

## Table of Contents

1. [Conceptual Framework](#1-conceptual-framework)
2. [Syndrome-Based Differential Tables](#2-syndrome-based-differential-tables)
   - 2.1 [Nephrotic Syndrome](#21-nephrotic-syndrome)
   - 2.2 [Nephritic Syndrome](#22-nephritic-syndrome)
   - 2.3 [RPGN / Crescentic GN](#23-rpgn--crescentic-gn)
   - 2.4 [Asymptomatic Hematuria](#24-asymptomatic-hematuria)
   - 2.5 [Isolated Proteinuria](#25-isolated-proteinuria)
   - 2.6 [AKI (Nephrology Presentation)](#26-aki-nephrology-presentation)
   - 2.7 [CKD of Unclear Etiology](#27-ckd-of-unclear-etiology)
   - 2.8 [Hypertension with Urinary Abnormalities](#28-hypertension-with-urinary-abnormalities)
   - 2.9 [Systemic Vasculitis with Renal Involvement](#29-systemic-vasculitis-with-renal-involvement)
   - 2.10 [Pulmonary-Renal Syndrome](#210-pulmonary-renal-syndrome)
   - 2.11 [Pregnancy with Renal Disease](#211-pregnancy-with-renal-disease)
   - 2.12 [Post-Transplant Dysfunction](#212-post-transplant-dysfunction)
   - 2.13 [TMA](#213-tma)
   - 2.14 [Complement Consumption (Low C3/C4)](#214-complement-consumption-low-c3c4)
3. [Disease-Specific DDx Deep Dives](#3-disease-specific-ddx-deep-dives)
4. [Diagnostic Confidence Framework](#4-diagnostic-confidence-framework)
5. [Clinical Decision Trees](#5-clinical-decision-trees)
6. [Common Diagnostic Errors](#6-common-diagnostic-errors)

---

## 1. Conceptual Framework

### 1.1 DDx Methodology Overview

The differential diagnosis of glomerular disease demands a structured, multi-layered analytical approach. Unlike many areas of medicine where a single pathognomonic finding clinches the diagnosis, glomerular diseases frequently present with overlapping clinical phenotypes, making systematic DDx reasoning essential. This framework integrates five core principles: pattern recognition, Bayesian reasoning, diagnostic hierarchy, urgency stratification, and diagnostic confidence scoring.

### 1.2 Pattern Recognition

Pattern recognition is the first line of diagnostic reasoning. The nephrologist must rapidly categorize the presentation into a clinical syndrome based on the constellation of findings.

**Primary Patterns:**

| Pattern | Key Identifiers | Immediate DDx Narrowing |
|---|---|---|
| Nephrotic | Edema, hypoalbuminemia, heavy proteinuria (>3.5 g/d), hyperlipidemia, lipiduria | mcd, sgs, membranous, diabeticNephropathy, amyloid |
| Nephritic | Hematuria (dysmorphic RBCs), HTN, oliguria, mild-moderate proteinuria | iga, irgn, lupus, nca |
| Rapidly progressive | Rising creatinine over days to weeks, nephritic sediment, often systemic features | RPGN triad: ntiGbm, nca, immune complex |
| Isolated hematuria | Persistent RBCs without proteinuria or functional impairment | iga, 	hinBasementMembrane, lport |
| Isolated proteinuria | Sub-nephrotic proteinuria without hematuria | Early diabeticNephropathy, obesity-related, sgs |
| Chronic kidney disease | Irreversible eGFR decline with structural abnormalities | Any end-stage glomerular disease, chronic transplant injury |

> **Clinical Pearl:** Never anchor on the first pattern identified. Patients may evolve from one pattern to another (e.g., iga presenting initially as isolated hematuria, then progressing to nephrotic-range proteinuria).

### 1.3 Bayesian Reasoning

Bayesian reasoning requires continuously updating pre-test probabilities as new data become available.

**Pre-test Probability Factors:**

| Factor | Impact on Pre-test Probability |
|---|---|
| Age | mcd peaks at 2-6 years; membranous peaks at 40-60; iga peaks at 20-40; ntiGbm peaks at 20-30 and 50-70 |
| Sex | membranous M>F (2:1); lupus nephritis F>>M; iga M>F (2:1); ntiGbm M=F |
| Race/Ethnicity | iga most common GN worldwide (especially East Asian); sgs more common in African descent; lupus nephritis more severe in African American/Hispanic |
| Geographic location | iga highest in East Asia; post-streptococcal GN higher in developing nations; malaria-associated GN in endemic areas |
| Temporal context | Post-infectious GN 1-3 weeks after pharyngitis; post-streptococcal 1-2 weeks after skin infection; drug-induced after exposure |
| Comorbidities | DM -> diabeticNephropathy; HIV -> HIVAN/sgs; hepatitis B/C -> membranous/cryoglobulinemic; smoking + M-component -> ibrillaryGlomerulonephritis |
| Family history | lport (X-linked in 85%), 	hinBasementMembrane, genetic sgs, iga (familial clustering) |

**Post-test Probability Updating:**

The Bayesian framework requires that each test result be interpreted in the context of the prior probability. A positive ANCA in a patient with a high pre-test probability of ANCA vasculitis (elderly, sinusitis, hematuria) has far greater predictive value than the same result in a young patient with isolated proteinuria.

> **Clinical Pearl:** Always ask: "What was the probability of this diagnosis BEFORE this test?" If the pre-test probability was low, even a positive result may be a false positive.

### 1.4 Diagnostic Hierarchy

Diagnostic reasoning should follow a hierarchical approach, prioritizing conditions that are:

1. **Most common** in the given demographic and clinical context
2. **Most dangerous** if missed (time-sensitive or rapidly fatal)
3. **Most treatable** (high-yield intervention available)
4. **Most specific** in their diagnostic criteria

**Hierarchy of Urgency:**

| Priority | Category | Examples | Time to Diagnosis |
|---|---|---|---|
| P0 - Emergent | Conditions where delay leads to irreversible organ damage or death | ntiGbm disease, TTP/HUS, severe lupus nephritis class IV, cortical necrosis | Hours to 1-2 days |
| P1 - Urgent | Conditions requiring prompt diagnosis to prevent progression | nca vasculitis, crescentic GN, active transplant rejection, ATN requiring biopsy | 1-3 days |
| P2 - Semi-urgent | Conditions where timely diagnosis affects long-term outcome | Nephrotic syndrome with complications, AKI of uncertain etiology, TMA | 3-7 days |
| P3 - Routine | Conditions where diagnosis can be methodically pursued | Isolated hematuria, sub-nephrotic proteinuria, CKD evaluation | 1-4 weeks |

### 1.5 Urgency Stratification

Urgency stratification determines the pace and intensity of the diagnostic workup.

| Tier | Clinical Scenario | Required Actions | Timeline |
|---|---|---|---|
| Tier 1 | Cr doubling in <1 week, oliguria, pulmonary hemorrhage, severe HTN, platelet drop | Stat labs (CBC, CMP, UA, C3/C4, ANCA, anti-GBM, ADAMTS13, SPEP), urgent nephrology consult, consider emergent biopsy | Same day |
| Tier 2 | Cr rising over 1-4 weeks, nephritic sediment, nephrotic syndrome with complications | Urgent labs, schedule biopsy within 48-72 hours, start empiric treatment if indicated | 1-3 days |
| Tier 3 | Stable Cr with new proteinuria or hematuria, sub-nephrotic proteinuria | Outpatient workup, scheduled biopsy if indicated | 1-2 weeks |
| Tier 4 | Asymptomatic microscopic hematuria, isolated sub-nephrotic proteinuria | Systematic workup, consider biopsy based on risk stratification | 2-4 weeks |

### 1.6 Diagnostic Confidence Scoring

Every diagnosis should carry a confidence score reflecting the strength of the evidence. This score directly impacts treatment decisions. See [Section 4](#4-diagnostic-confidence-framework) for the full scoring framework.

> **Clinical Pearl:** A "Definite" diagnosis requires histopathology for most glomerular diseases. However, in emergent scenarios (e.g., suspected TTP), treatment should NOT be delayed awaiting biopsy if the clinical picture is compelling.

---

## 2. Syndrome-Based Differential Tables

### 2.1 Nephrotic Syndrome

**Definition:** Proteinuria >=3.5 g/24h (or equivalent spot protein/creatinine ratio), hypoalbuminemia (<3.0 g/dL), edema, hyperlipidemia, and lipiduria.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `mcd` | Age 2-6 years (pediatric); acute onset; normal BP; bland urine sediment; dramatic response to steroids; normal GFR; negative IF on biopsy | Age >40; hematuria; hypertension; renal insufficiency; slow steroid response; mesangial proliferation on biopsy | Higher in children; lower if African American adult; consider if relapsing in young adult | UA, spot UPC, albumin, lipids, renal biopsy (adults), genetic testing if familial | Semi-urgent | Biopsy in adults; empiric steroids in children if classic presentation |
| `fsgs` | African American > Caucasian; sub-nephrotic or nephrotic proteinuria; microscopic hematuria common; hypertension; CKD at presentation; collapsing variant in HIV; podocyte foot process effacement without immune deposits | Young child with classic steroid-responsive NS; purely nephrotic without hematuria; clear secondary cause (obesity, APOL1, viral) | African descent; APOL1 high-risk genotypes; obesity; NSAIDs; HIV; family history of genetic FSGS; post-transplant recurrence | UA, UPC, albumin, lipids, renal biopsy, viral serologies (HIV, HCV), APOL1 genotyping, genetic panel if young/familial | Semi-urgent | Biopsy; classify variant; screen for secondary causes before immunosuppression |
| `membranous` | Age 40-60; insidious onset; nephrotic-range proteinuria; normal GFR initially; thrombotic risk (renal vein thrombosis); anti-PLA2R antibodies (70-80%); granular IgG/C3 on IF; subepithelial deposits on EM; thickened GBM on LM | Age <30; rapid onset; hematuria; low complement; systemic features; mesangial or endocapillary proliferation on biopsy | Age 40-60; M>F; Caucasian; HCV infection; solid organ malignancy (lung, colon, breast); drug exposure (NSAIDs, gold, penicillamine) | UA, UPC, anti-PLA2R, anti-THSD7A, complement levels, renal biopsy, age-appropriate malignancy screening, hepatitis serologies | Semi-urgent | Biopsy; anti-PLA2R quantification; malignancy screening; consider rituximab as first-line |
| `diabeticNephropathy` | Known DM (type 1 >10 yrs, type 2 at diagnosis); gradual onset proteinuria; Kimmelstiel-Wilson nodules on biopsy; arteriolar hyalinosis; gradual GFR decline; retinopathy (80%) | No diabetes; acute onset; hematuria; hypocomplementemia; anti-PLA2R positive; young age without DM | Duration of diabetes; glycemic control; retinopathy presence; hypertension; APOL1 risk alleles | HbA1c, UA, UPC, fundoscopic exam, renal biopsy if atypical features | Routine to Semi-urgent | Optimize glycemic/BP control; SGLT2i; RAAS blockade; biopsy if atypical |
| `amyloid` | Age >50; chronic inflammatory disease (RA, osteomyelitis, IBD); monoclonal gammopathy; massive proteinuria; hepatosplenomegaly; Congo red positive with apple-green birefringence; amorphous deposits on LM; fibrils on EM | Young age without chronic inflammation; no M-component; rapid onset; isolated glomerular disease without systemic features | Chronic infection (TB, osteomyelitis); chronic inflammatory disease; monoclonal gammopathy (AL amyloidosis); family history | SPEP, UPEP, free light chains, serum amyloid A, Congo red staining, SAP scan, echocardiography, fat pad biopsy | Semi-urgent to Urgent | Biopsy with Congo red; identify amyloid type (mass spectrometry); treat underlying cause |
| `c3` (C3 Glomerulopathy) | Low C3 with normal C4; dominant C3 on IF (no or minimal Ig); dense deposits on EM (DDD) or subendothelial/mesangial deposits (C3GN); C3 nephritic factor; alternative pathway dysregulation | Normal complement; full-house IF pattern (lupus); IgA dominant; post-infectious pattern; no dense deposits on EM | Low C3 with GN; C3 nephritic factor; factor H/I deficiency; monoclonal gammopathy; post-infectious setting | C3, C4, C3 nephritic factor, complement pathway testing (factor H, factor I, factor B), renal biopsy, SPEP | Semi-urgent | Biopsy; complement workup; identify underlying complement dysregulation; consider eculizumab in selected cases |
| `fibrillaryGlomerulonephritis` | Age 50-60; proteinuria +/- hematuria; hypertension; CKD; fibrillary deposits on EM (non-amyloid, randomly arranged, 12-22 nm); negative Congo red; IgG/C3 on IF; monoclonal gammopathy in 30% | Young age; Congo red positive; organized deposits (microtubular, fibril type inconsistent); clear secondary cause | Age 50-60; monoclonal gammopathy; smoking history; hepatitis C | SPEP, UPEP, free light chains, renal biopsy with EM, Congo red negative | Semi-urgent | Biopsy with EM; identify fibrillary pattern; screen for associated conditions; rituximab |

> **Clinical Pearl:** The single most important step in nephrotic syndrome is distinguishing primary (idiopathic) from secondary causes. Treat secondary causes first.

> **Clinical Pearl:** In adults, never diagnose `mcd` without a biopsy. Up to 30% of adults with nephrotic syndrome who appear to have `mcd` on clinical grounds are found to have `fsgs` on biopsy.

> **Clinical Pearl:** Anti-PLA2R positive `membranous` nephropathy has a 30% risk of spontaneous remission. Observation for 3-6 months with conservative management may be appropriate for low-risk patients.

---

### 2.2 Nephritic Syndrome

**Definition:** Hematuria (often dysmorphic RBCs, RBC casts), hypertension, oliguria, mild-to-moderate proteinuria (<3 g/day typically), and variable renal insufficiency.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `iga` | Young adult (20-40); episodic gross hematuria concurrent with URI ("synpharyngitic" hematuria); microscopic hematuria between episodes; mild-moderate proteinuria; normal to mildly reduced GFR; mesangial IgA on IF | Older age (>50); nephrotic syndrome at presentation; low complement; systemic features; endocapillary proliferation without mesangial changes | M>F; East Asian descent; URI timing (synpharyngitic); IgA vasculitis history; liver disease; celiac disease | UA, UPC, C3/C4 (usually normal), IgA level (elevated in 50%), renal biopsy (gold standard) | Semi-urgent | Biopsy; Oxford classification (MEST-C); SGLT2i + RAAS blockade; consider steroids if high-risk |
| `irgn` | Post-streptococcal: 1-3 wks after pharyngitis, 3-6 wks after skin infection; acute nephritis; low C3 (80%); subepithelial humps on EM; "starry sky" IF; self-limiting. Staphylococcal: endocarditis, shunt, abscess; low C3 | No preceding infection; chronic course; normal complement; endocapillary crescents; systemic vasculitis features; IgA dominant IF | Post-pharyngitis in children; post-impetigo in children; IV drug use (staphylococcal); endocarditis; chronic infections | UA, C3, C4, ASO, anti-DNase B, blood cultures, renal biopsy, HCV/HBV serologies | Semi-urgent to Urgent (if AKI) | Supportive care (most cases self-limit in children); biopsy if atypical or no recovery in 1-2 weeks; treat underlying infection |
| `lupus` | Young female; multi-system involvement (rash, arthritis, serositis, cytopenas); positive ANA/anti-dsDNA; low C3 and C4; full-house IF pattern (IgG, IgA, IgM, C3, C1q); wire-loop lesions on LM (class IV) | Male; age >50; isolated renal disease without systemic features; normal complement; negative ANA; pauci-immune IF | Female (9:1); African American/Hispanic; age 15-45; family history of autoimmune disease; history of SLE | ANA, anti-dsDNA, complement levels, CBC, urinalysis, renal biopsy (ISN/RPS classification), antiphospholipid antibodies | Urgent | Biopsy; classify by ISN/RPS; induction with MMF + glucocorticoids (Class III/IV); maintenance therapy |
| `anca` | Older adult (>50); rapidly declining GFR; active urine sediment; constitutional symptoms; sinusitis/pulmonary hemorrhage (GPA); MPA: renal-limited; EGPA: asthma, eosinophilia; c-ANCA/PR3 (GPA); p-ANCA/MPO (MPA) | Young patient; normal complement; isolated proteinuria without hematuria; no systemic features; pauci-immune biopsy negative | Age >50; smoking; silica exposure; nasal/sinus disease; pulmonary hemorrhage; neuropathy | ANCA (IF and ELISA), C3, C4, CBC, urinalysis, CT sinuses/chest, renal biopsy | Urgent | Biopsy (pauci-immune GN); start rituximab + glucocorticoids; assess disease severity (BVAS); screen for complications |
| `antiGbm` | Young adult (20-30) or older adult (50-70); biphasic age distribution; acute nephritis +/- pulmonary hemorrhage; linear IgG on IF; anti-GBM antibodies positive; HLA-DR15 associated | Insidious onset; older age without second peak; normal IF; negative anti-GBM; systemic vasculitis features; PR3/MPO positive | HLA-DR15; smoking (lung hemorrhage); hydrocarbon exposure; recent infection/drugs; concurrent ANCA (dual positive 10-30%) | Anti-GBM antibodies, ANCA, C3, CBC, urinalysis, chest X-ray/CT, renal biopsy | Emergent | Plasmapheresis + cyclophosphamide + glucocorticoids; assess for lung hemorrhage; dual-positive patients need ANCA-directed therapy |

> **Clinical Pearl:** The most critical distinction in nephritic syndrome is determining whether the process is immune-complex mediated (`iga`, `irgn`, `lupus`), anti-GBM, or pauci-immune (`anca`). This determines treatment and prognosis.

> **Clinical Pearl:** `iga` nephropathy is the most common glomerulonephritis worldwide. Do not dismiss recurrent gross hematuria concurrent with URIs in young adults.

> **Clinical Pearl:** Low C3 with normal C4 suggests alternative complement pathway activation (`c3` glomerulopathy, `irgn`). Low C3 AND low C4 suggests classical pathway activation (`lupus`, `cryoglobulinemic`, `irgn`).

---

### 2.3 RPGN / Crescentic GN

**Definition:** Rapid deterioration of renal function over days to weeks, with active urine sediment and crescent formation on biopsy. Three serological categories define the DDx.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| **Anti-GBM Disease** (`antiGbm`) | Biphasic age (20-30, 50-70); acute nephritis +/- hemoptysis; anti-GBM antibodies positive; linear IgG on IF; HLA-DR15; pauci-immune on LM (crescents without immune deposits) | Insidious onset; normal IF; negative anti-GBM; systemic vasculitis features; positive PR3/MPO | Smoking; hydrocarbon exposure; renal allograft; concurrent ANCA (10-30%) | Anti-GBM, ANCA, CBC, C3/C4, chest X-ray/CT, renal biopsy, urinalysis | Emergent | Plasmapheresis + cyclophosphamide + steroids; do NOT delay for biopsy if classic presentation |
| **ANCA Vasculitis** (`anca`) | GPA: upper + lower respiratory tract + renal; MPA: renal-limited +/- lung; EGPA: asthma + eosinophilia + renal; c-ANCA/PR3 or p-ANCA/MPO; pauci-immune GN; crescents >50% | Young patient; normal complement; full-house IF; anti-GBM positive; linear IgG; pure nephrotic syndrome | GPA: c-ANCA/PR3 positive (90%); MPA: p-ANCA/MPO positive (60%); EGPA: p-ANCA/MPO positive (40%); older age; smoking | ANCA (IF + ELISA), ANA, anti-GBM, C3/C4, CBC, urinalysis, CT chest/sinuses, renal biopsy | Urgent | Biopsy (pauci-immune); rituximab + glucocorticoids; assess BVAS; plasmapheresis for severe (Cr >500, dialysis-dependent, pulmonary hemorrhage) |
| **Immune Complex Crescentic GN** (`lupus`, `iga`, `irgn`) | Full-house or dominant immune deposits on IF; crescents with immune complex pattern; serological markers of underlying disease (anti-dsDNA, low complements, IgA levels, ASO) | Pauci-immune pattern; negative serologies; no systemic features; age outside typical range | `lupus`: female, young, multi-system; `iga`: young male, synpharyngitic hematuria; `irgn`: children post-streptococcal | Complete autoimmune panel, complement levels, anti-GBM, ANCA, renal biopsy, infectious serologies | Urgent | Treat underlying disease; pulse steroids + immunosuppression based on etiology |

> **Clinical Pearl:** Crescentic GN is a medical emergency. When >50% of glomeruli show crescents, the kidney is at imminent risk. Do not wait for serological results to initiate treatment in severe presentations.

> **Clinical Pearl:** 10-30% of patients with `antiGbm` disease also have positive ANCA (dual-positive). These patients require both anti-GBM and ANCA-directed therapy.

> **Clinical Pearl:** Crescentic GN on biopsy WITHOUT positive serologies should prompt consideration of immune complex crescentic GN (`lupus`, `iga`, `irgn`) or rare causes.

---

### 2.4 Asymptomatic Hematuria

**Definition:** Persistent microscopic hematuria (>=3 RBC/hpf on >=2 occasions) without proteinuria, hypertension, or renal insufficiency.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `iga` | Young adult (20-40); M>F; recurrent gross hematuria with URIs; isolated microscopic hematuria between episodes; normal GFR; normal complement; mesangial IgA on IF | Age >50; isolated microscopic hematuria without gross episodes; low complement; nephrotic proteinuria | Most common cause of isolated hematuria in young adults worldwide; East Asian descent | UA, UPC, C3/C4, IgA level, renal biopsy (if UPC >0.5 g/day or abnormal GFR) | Routine | Monitor UPC and GFR; biopsy if proteinuria develops or GFR declines; SGLT2i + RAAS blockade |
| `thinBasementMembrane` | Persistent microscopic hematuria; normal GFR; normal proteinuria; family history of hematuria; thin GBM on EM (<275 nm); no immune deposits; benign course | Progressive renal disease; proteinuria >0.5 g/day; family history of ESRD; electron-dense deposits; abnormal GBM | Family history; benign course; rarely progresses | UA, UPC, renal biopsy with EM, genetic testing (COL4A3/A4/A5 mutations), family screening | Routine | Reassurance; monitor; genetic counseling if COL4A3/A4 mutations; avoid nephrotoxins |
| `alport` | Family history of ESRD, deafness, ocular anomalies; X-linked (85%): affected males hematuria from childhood, progressive CKD, sensorineural deafness, lenticonus; abnormal GBM (lamellation/splitting on EM); type IV collagen defects | No family history; late onset; normal hearing/eyes; normal GBM on EM; sporadic | X-linked (most common); male predominance; family history of renal failure; high-frequency sensorineural hearing loss | UA, UPC, audiology, ophthalmology exam, renal biopsy with EM, genetic testing (COL4A3/A4/A5), family screening | Routine to Semi-urgent | Genetic testing (preferred over biopsy); ACEi/ARB from early stages; monitor hearing/vision; transplant evaluation if progressive; screen family members |
| `fsgs` (early) | Mild microscopic hematuria +/- sub-nephrotic proteinuria; normal to mildly reduced GFR; APOL1 risk alleles in African Americans; segmental sclerosis on biopsy | Classic nephrotic syndrome; normal APOL1; full-house IF; immune deposits | African descent; APOL1 high-risk; obesity; viral infections; sickle cell trait | UA, UPC, APOL1 genotyping, renal biopsy if proteinuria >0.5 g/day or declining GFR | Routine to Semi-urgent | Biopsy if progressive; optimize BP; RAAS blockade; address secondary causes |
| `diabeticNephropathy` (early) | Known DM; early microalbuminuria; retinopathy; gradual GFR decline; mesangial expansion on biopsy | No diabetes; normal HbA1c; no retinopathy; acute onset; hematuria prominent | Duration of DM; glycemic control; hypertension | HbA1c, UA, UPC, fundoscopic exam | Routine | Optimize glycemic/BP control; SGLT2i; RAAS blockade |
| Urological causes | Age >40; painless gross hematuria; no renal sediment (no dysmorphic RBCs, no casts); normal proteinuria; risk factors for urothelial/bladder cancer | Dysmorphic RBCs; RBC casts; proteinuria; young age without risk factors | Age >40; smoking; chemical exposure; male > female | Cystoscopy, CT urogram, UA with microscopy, urine cytology | Routine to Semi-urgent | Urological workup (cystoscopy + imaging); if urological causes excluded, proceed to nephrological evaluation |

> **Clinical Pearl:** Asymptomatic hematuria in a young adult (20-40) with normal GFR and proteinuria <0.5 g/day is most commonly `iga` or `thinBasementMembrane`. A trial of observation with serial monitoring is appropriate before biopsy.

> **Clinical Pearl:** Never dismiss microscopic hematuria in a patient with diabetes as "just diabetic nephropathy." Hematuria is uncommon in `diabeticNephropathy` until very late stages.

> **Clinical Pearl:** A urological cause should be excluded in ALL patients >40 with unexplained hematuria before attributing it to a glomerular source.

---

### 2.5 Isolated Proteinuria

**Definition:** Persistent proteinuria (UPC >0.5 g/g) without hematuria, active sediment, or renal insufficiency. May be sub-nephrotic or nephrotic-range.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `fsgs` | Sub-nephrotic proteinuria; normal GFR initially; African American > Caucasian; podocyte foot process effacement on biopsy; normal immune IF; segmental sclerosis | Pure nephrotic syndrome without hematuria; normal biopsy; immune deposits present | African descent; APOL1 high-risk; obesity; viral infections; NSAID use; sickle cell | UA, UPC, albumin, renal biopsy, APOL1 genotyping, viral serologies | Semi-urgent | Biopsy; classify variant; address secondary causes; consider immunosuppression if primary |
| `diabeticNephropathy` | Known DM; gradual onset proteinuria; retinopathy; Kimmelstiel-Wilson nodules; arteriolar hyalinosis; insulin dependence correlates with nodules | No diabetes; normal HbA1c; no retinopathy; hematuria prominent; acute onset | Duration of DM; glycemic control; hypertension; APOL1 risk alleles | HbA1c, UA, UPC, fundoscopic exam | Routine | Optimize glycemic/BP control; SGLT2i; RAAS blockade |
| Obesity-related glomerulopathy | BMI >30-35; sub-nephrotic proteinuria; mild glomerulomegaly on biopsy; minimal foot process effacement; no significant sclerosis; FGGS pattern | Normal BMI; nephrotic-range proteinuria; significant sclerosis; immune deposits; hematuria | BMI >35; African American; metabolic syndrome | UA, UPC, BMI assessment, renal biopsy if proteinuria progressive | Routine | Weight loss; RAAS blockade; bariatric surgery in selected cases |
| `membranous` (early) | Age 40-60; insidious proteinuria; anti-PLA2R positive; normal GFR; subepithelial deposits on EM; thickened GBM on LM | Young age; rapid onset; hematuria; low complement; systemic features | Age 40-60; M>F; Caucasian; HCV | Anti-PLA2R, anti-THSD7A, complement levels, renal biopsy | Semi-urgent | Biopsy; anti-PLA2R monitoring; malignancy screening; consider rituximab |
| `iga` (atypical) | Young adult; microscopic hematuria (may be absent or intermittent); sub-nephrotic proteinuria; mesangial IgA on IF; normal GFR; normal complement | Age >50; nephrotic-range proteinuria; low complement; systemic features | Young adult; East Asian; post-URI gross hematuria episodes | UA, UPC, C3/C4, IgA level, renal biopsy | Semi-urgent | Biopsy; SGLT2i + RAAS blockade; monitor |
| Cast nephropathy (myeloma kidney) | Age >50; renal insufficiency; sub-nephrotic or nephrotic proteinuria; free light chains in urine; SPEP with monoclonal protein; Bence Jones proteinuria; renal tubular casts on biopsy | Young age; normal SPEP/UPEP; negative free light chains; normal bone marrow | Age >50; bone pain; anemia; hypercalcemia; recurrent infections | SPEP, UPEP, free light chains, serum calcium, bone marrow biopsy, renal biopsy | Semi-urgent to Urgent | Hematology consult; treat myeloma; bortezomib-based regimen; plasmapheresis in selected cases |

> **Clinical Pearl:** Sub-nephrotic proteinuria that is persistent (>3 months) and >0.5 g/day warrants investigation. Do not dismiss it as "benign."

> **Clinical Pearl:** In patients with diabetes and sub-nephrotic proteinuria, consider a biopsy if there is hematuria, rapid progression, or absence of retinopathy.

---

### 2.6 AKI (Nephrology Presentation)

**Definition:** Acute kidney injury presenting to nephrology, requiring evaluation for glomerular, vascular, tubulointerstitial, or obstructive etiology.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `anca` | Older adult; rapidly declining GFR; active urine sediment; constitutional symptoms; sinusitis/pulmonary hemorrhage; pauci-immune GN on biopsy; ANCA positive | Young patient; bland sediment; normal complement; full-house IF; anti-GBM positive | Age >50; smoking; silica exposure; nasal disease; pulmonary hemorrhage | ANCA, anti-GBM, C3/C4, CBC, urinalysis, CT chest/sinuses, renal biopsy | Urgent | Biopsy (pauci-immune); rituximab + steroids; assess BVAS |
| `antiGbm` | Young or older adult; acute nephritis +/- hemoptysis; linear IgG on IF; anti-GBM positive; HLA-DR15 | Insidious onset; normal IF; negative anti-GBM; systemic vasculitis features | Smoking; hydrocarbon exposure; concurrent ANCA | Anti-GBM, ANCA, C3/C4, chest X-ray/CT, renal biopsy | Emergent | Plasmapheresis + cyclophosphamide + steroids |
| `lupus` flare | Young female; multi-system involvement; positive ANA/anti-dsDNA; low complements; nephritic sediment; active SLE; full-house IF; wire-loop lesions | Male; age >50; isolated renal disease; normal complement; negative ANA | Female; African American/Hispanic; age 15-45; non-compliance | ANA, anti-dsDNA, complement levels, CBC, urinalysis, renal biopsy | Urgent | Biopsy; classify ISN/RPS; pulse steroids + MMF for class III/IV |
| TMA (see 2.13) | Thrombocytopenia; schistocytes; hemolytic anemia; AKI; purpura; neurological symptoms; fever; ADAMTS13 <10% (TTP); Shiga toxin (STEC-HUS); complement abnormalities (aHUS) | Normal platelets; no schistocytes; no hemolysis; normal LDH/haptoglobin | Age; diarrhea prodrome; family history; complement mutations; drug exposure | CBC, smear, LDH, haptoglobin, reticulocyte count, ADAMTS13, Shiga toxin, complement testing | Emergent | TTP: plasmapheresis + caplacizumab; STEC-HUS: supportive; aHUS: eculizumab |
| `irgn` | Child/young adult; preceding infection; acute nephritis; low C3; subepithelial humps on EM; self-limiting | No preceding infection; chronic course; normal complement; crescents >50% | Post-pharyngitis (1-3 weeks); post-impetigo (3-6 weeks) | ASO, anti-DNase B, C3, C4, blood cultures, renal biopsy | Semi-urgent | Supportive; monitor; biopsy if no recovery in 1-2 weeks |
| Acute TIN | Drug exposure (NSAIDs, PPIs, antibiotics); fever, rash, eosinophilia; WBC casts; eosinophiluria; elevated IgE | No drug exposure; normal WBC count; bland sediment; no systemic features | Drug exposure timeline (days to weeks) | CBC with differential, urinalysis, renal biopsy, drug discontinuation trial | Semi-urgent | Discontinue offending drug; steroids if severe |
| ATN (pre-renal/renal) | Hypotension/sepsis/nephrotoxin exposure; muddy brown casts; FE Na >2% (renal) or <1% (pre-renal); bland sediment initially; recovery expected | Active sediment; hematuria; proteinuria >1 g; systemic vasculitis features | Prolonged hypotension; nephrotoxins (aminoglycosides, contrast); sepsis | CBC, CMP, urinalysis, fractional excretion studies, renal ultrasound | Urgent | Supportive; optimize hemodynamics; remove nephrotoxins; dialysis if needed |

> **Clinical Pearl:** AKI with an active urine sediment (dysmorphic RBCs, RBC casts, WBC casts) demands urgent nephrology consultation and consideration of biopsy.

> **Clinical Pearl:** Never attribute AKI to "pre-renal" without confirming the sediment is bland. Pre-renal AKI should have a bland sediment.

---

### 2.7 CKD of Unclear Etiology

**Definition:** Irreversible eGFR decline (<60 mL/min/1.73m2 for >3 months) without a clear underlying cause established.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `diabeticNephropathy` | Known DM; proteinuria; retinopathy; Kimmelstiel-Wilson nodules; gradual decline; bilateral small echogenic kidneys on US | No diabetes; normal HbA1c; no retinopathy; hematuria prominent; large kidneys | Duration of DM; glycemic control; hypertension; APOL1 risk alleles | HbA1c, UA, UPC, fundoscopic exam, renal biopsy if atypical | Routine | Optimize glycemic/BP control; SGLT2i; RAAS blockade |
| `alport` | Family history of ESRD; sensorineural deafness; ocular anomalies; lamellated GBM on EM; type IV collagen defects; male predominance (X-linked); hematuria from childhood | No family history; late onset; normal hearing/eyes; normal GBM | X-linked (85%); male > female in severity; family history | Genetic testing (COL4A3/A4/A5), audiology, ophthalmology, renal biopsy with EM, family screening | Routine to Semi-urgent | ACEi from early; monitor hearing/vision; transplant evaluation; family screening |
| `iga` (chronic) | Long-standing hematuria +/- proteinuria; young adult onset; progressive CKD; mesangial IgA on IF; previous biopsy showing IgAN | Age >50 at onset; no prior hematuria history; normal IF; complement abnormalities | Young adult onset; East Asian; previous biopsy showing IgAN | Review prior biopsies; UA, UPC, C3/C4, IgA level, repeat biopsy if evolution | Routine | SGLT2i + RAAS blockade; optimize BP; consider steroids if active inflammation |
| `membranous` (chronic) | Long-standing nephrotic syndrome; anti-PLA2R positive; thickened GBM on biopsy; subepithelial deposits; sclerotic glomeruli | No prior nephrotic history; normal anti-PLA2R; immune deposits absent | Age 40-60; M>F; Caucasian; HCV | Anti-PLA2R, renal biopsy with review of prior biopsies | Routine | Rituximab; optimize supportive care; malignancy screening |
| `fsgs` (chronic) | Long-standing proteinuria; African American; APOL1 high-risk; segmental sclerosis; possible prior biopsy showing FSGS | Normal biopsy; no APOL1 risk alleles; immune deposits present | African descent; APOL1 high-risk; obesity; viral infections | APOL1 genotyping, review prior biopsies, genetic testing | Routine | Optimize BP; RAAS blockade; consider immunosuppression if active inflammation |
| Chronic TIN | Long-standing analgesic use (NSAIDs, phenacetin); papillary necrosis; small echogenic kidneys; tubular atrophy; interstitial fibrosis | No analgesic exposure; large kidneys; glomerular pattern | Analgesic abuse; occupational exposure; Chinese herbs | Renal ultrasound, CT urogram, review medication history, renal biopsy | Routine | Discontinue offending agents; monitor; dialysis preparation if progressive |
| Renovascular disease | Resistant hypertension; abdominal bruit; flash pulmonary edema; asymmetrical kidney size; renal artery stenosis on Doppler/CTA/MRA | Bilateral small kidneys without size discrepancy; no hypertension; no bruit | Age >50; atherosclerosis; fibromuscular dysplasia (young female); prior aortic surgery | Renal Doppler, CTA/MRA, captopril renogram | Routine | Medical optimization; consider revascularization in selected cases |
| Polycystic kidney disease | Bilateral enlarged kidneys with cysts; family history of PKD; hepatic cysts; intracranial aneurysms; hypertension; hematuria; flank pain | Small echogenic kidneys; no cysts; no family history | Family history (ADPKD); genetic testing | Renal ultrasound, genetic testing (PKD1/PKD2), screening for extrarenal manifestations | Routine | BP control; tolvaptan; monitor for complications (stones, infections, aneurysms) |
| `c3` (C3 Glomerulopathy) | Low C3; dominant C3 on IF; dense deposits or subendothelial deposits on EM; progressive CKD; C3 nephritic factor | Normal complements; full-house IF; no dense deposits; no complement pathway abnormalities | Low C3 with CKD; C3 nephritic factor; complement pathway mutations | C3, C4, C3 nephritic factor, complement pathway testing, renal biopsy | Semi-urgent | Biopsy; complement workup; consider eculizumab in selected cases |

> **Clinical Pearl:** In any patient with CKD of unclear etiology, always ask about family history of kidney disease and always check complement levels. These two simple steps can dramatically narrow the DDx.

> **Clinical Pearl:** The combination of bilateral small echogenic kidneys on ultrasound with CKD strongly suggests chronic medical renal disease. Large kidneys suggest amyloidosis, diabetic nephropathy, HIV-associated nephropathy, or acute processes.

---

### 2.8 Hypertension with Urinary Abnormalities

**Definition:** New or resistant hypertension accompanied by hematuria, proteinuria, or both.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `iga` | Young adult; episodic hematuria; proteinuria; hypertension; normal complement; mesangial IgA on IF | Age >50; low complement; systemic features; nephrotic syndrome | Young adult; East Asian; post-URI hematuria | UA, UPC, C3/C4, IgA level, renal biopsy | Semi-urgent | Biopsy; SGLT2i + RAAS blockade; optimize BP |
| `lupus` | Young female; multi-system involvement; positive ANA/anti-dsDNA; low complements; nephritic sediment; hypertension | Male; age >50; normal complement; negative ANA; isolated renal disease | Female; African American/Hispanic; age 15-45 | ANA, anti-dsDNA, complement levels, CBC, urinalysis, renal biopsy | Urgent | Biopsy; classify ISN/RPS; immunosuppression |
| Hypertensive nephrosclerosis | Long-standing hypertension; mild proteinuria; normal to mildly reduced GFR; bilateral small kidneys; benign arteriolosclerosis on biopsy; no active sediment | Active sediment; hematuria; young age; rapid progression; large kidneys | African American; uncontrolled HTN; diabetes; age >50 | UA, UPC, renal ultrasound, renal biopsy (if atypical features) | Routine | Optimize BP control; SGLT2i; RAAS blockade |
| `fsgs` | Sub-nephrotic proteinuria; hypertension; African American; APOL1 high-risk; segmental sclerosis on biopsy | Young child; purely nephrotic; normal APOL1; immune deposits present | African descent; APOL1 high-risk; obesity | UA, UPC, APOL1 genotyping, renal biopsy | Semi-urgent | Biopsy; address secondary causes; immunosuppression if primary |
| Renovascular disease | Resistant hypertension; flash pulmonary edema; abdominal bruit; asymmetrical kidney size; renal artery stenosis | Bilateral small kidneys without discrepancy; no bruit; young age without risk factors | Age >50; atherosclerosis; fibromuscular dysplasia; prior aortic surgery | Renal Doppler, CTA/MRA | Routine | Medical optimization; consider revascularization |

> **Clinical Pearl:** Hypertension with hematuria should NEVER be attributed to "benign" hypertensive nephrosclerosis without a biopsy, especially in young patients. Consider `iga`, `lupus` nephritis, or `anca` vasculitis.

> **Clinical Pearl:** The presence of dysmorphic RBCs or RBC casts in a hypertensive patient indicates a glomerular source, not simple hypertensive damage. This mandates further investigation.

---

### 2.9 Systemic Vasculitis with Renal Involvement

**Definition:** Systemic vasculitis (ANCA-associated, immune complex, or large vessel) with renal manifestations.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `anca` - GPA | Upper + lower respiratory tract involvement; sinonasal disease; pulmonary nodules/cavities; necrotizing granulomatous inflammation; c-ANCA/PR3 positive; pauci-immune GN; renal involvement in 80% | Isolated renal disease; no respiratory involvement; p-ANCA/MPO positive; immune complex deposits | c-ANCA/PR3 positive (90%); sinonasal disease; subglottic stenosis; saddle nose deformity | ANCA (PR3), CT chest/sinuses, renal biopsy, bronchoscopy with BAL, tissue biopsy | Urgent | Biopsy (pauci-immune); rituximab + glucocorticoids; assess BVAS; TMP-SMX for PJP prophylaxis |
| `anca` - MPA | Renal-limited or renal + pulmonary; no sinonasal/granulomatous disease; p-ANCA/MPO positive; pauci-immune GN; pulmonary capillaritis | Upper respiratory involvement; granulomas; c-ANCA/PR3 positive; immune deposits | p-ANCA/MPO positive (60%); older age; renal-limited | ANCA (MPO), CT chest, renal biopsy, pulmonary function tests | Urgent | Biopsy; rituximab + steroids; assess BVAS |
| `anca` - EGPA | Asthma; eosinophilia (>1500/uL); sinusitis; pulmonary infiltrates; neuropathy; cardiac involvement; p-ANCA/MPO positive (40%); necrotizing GN with eosinophils | No asthma; no eosinophilia; c-ANCA/PR3 positive; no respiratory involvement | p-ANCA/MPO positive (40%); asthma history; eosinophilia; neuropathy | ANCA (MPO), CBC with differential, CT chest/sinuses, echocardiography, renal biopsy, nerve conduction studies | Urgent | Biopsy; steroids +/- immunosuppression; mepolizumab (anti-IL-5) for EGPA |
| `lupus` vasculitis | Young female; multi-system involvement; positive ANA/anti-dsDNA; low complements; vasculitis features (palpable purpura, livedo reticularis); full-house IF on renal biopsy | Male; age >50; normal complement; negative ANA; isolated renal disease | Female; African American/Hispanic; age 15-45 | ANA, anti-dsDNA, complement levels, CBC, urinalysis, skin biopsy, renal biopsy | Urgent | Biopsy; classify ISN/RPS; pulse steroids + immunosuppression |
| `cryoglobulinemic` | HCV positive (80%); palpable purpura; arthralgia; peripheral neuropathy; low C4; cryoglobulins positive; MPGN pattern on biopsy; subendothelial deposits | HCV negative; normal C4; no cryoglobulins; no purpura; no neuropathy | HCV infection; mixed cryoglobulinemia (type II or III); IgM rheumatoid factor positive | HCV RNA, cryoglobulins, complement levels, SPEP, rheumatoid factor, renal biopsy, skin biopsy | Urgent | Treat HCV (DAAs); rituximab for severe vasculitis; plasmapheresis; avoid immunosuppression without HCV treatment |
| IgA vasculitis (HSP) | Palpable purpura (lower extremities); arthritis/arthralgia; abdominal pain; IgA nephropathy on renal biopsy; children > adults; self-limiting | No purpura; no GI symptoms; no arthritis; adult onset; mesangial IgA only (could be IgAN) | Children; post-infectious; HSP nephritis in 30-50% of children | UA, UPC, renal biopsy, skin biopsy (IgA deposits), stool guaiac | Semi-urgent | Supportive; steroids for severe GI or renal involvement; monitor for progression |
| Polyarteritis nodosa | Medium-vessel vasculitis; livedo reticularis; mononeuritis multiplex; testicular pain; mesenteric ischemia; hypertension (renal artery involvement); renal infarcts; no glomerulonephritis | Glomerulonephritis present; ANCA positive; small-vessel vasculitis | Hepatitis B association; visceral aneurysms on angiography | ANCA, hepatitis B, CT angiography, mesenteric angiography, renal biopsy (if GN present) | Urgent | Treat underlying cause; immunosuppression; avoid cyclophosphamide if HBV-associated |

> **Clinical Pearl:** In systemic vasculitis, the pattern of organ involvement is as important as serology. GPA classically affects upper and lower respiratory tracts; MPA is renal-limited with or without lungs; EGPA requires asthma and eosinophilia.

> **Clinical Pearl:** Always check hepatitis B before diagnosing polyarteritis nodosa. HBV-associated PAN should be treated with antivirals, not immunosuppression.

---

### 2.10 Pulmonary-Renal Syndrome

**Definition:** Combined pulmonary hemorrhage and glomerulonephritis, a life-threatening emergency requiring immediate evaluation.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `antiGbm` | Biphasic age (20-30, 50-70); hemoptysis; acute nephritis; anti-GBM positive; linear IgG on IF; diffuse alveolar hemorrhage on CT; Goodpasture syndrome | Insidious onset; normal IF; negative anti-GBM; systemic vasculitis features; PR3/MPO positive | HLA-DR15; smoking; hydrocarbon exposure; concurrent ANCA (10-30%) | Anti-GBM, ANCA, C3, CBC, urinalysis, chest X-ray/CT, bronchoscopy with BAL (hemosiderin-laden macrophages), renal biopsy | Emergent | Plasmapheresis + cyclophosphamide + steroids; assess severity of hemorrhage; ICU transfer |
| `anca` - GPA | Hemoptysis; sinonasal disease; pulmonary nodules/cavities; c-ANCA/PR3 positive; pauci-immune GN; diffuse alveolar hemorrhage | No sinonasal involvement; p-ANCA/MPO positive; immune deposits; no respiratory symptoms | c-ANCA/PR3 positive (90%); sinonasal disease; subglottic stenosis | ANCA, CT chest/sinuses, renal biopsy, bronchoscopy with BAL | Emergent | Plasmapheresis + rituximab + steroids; assess BVAS; ICU if severe DAH |
| `anca` - MPA | Hemoptysis; pulmonary capillaritis; p-ANCA/MPO positive; pauci-immune GN; no sinonasal involvement; no granulomas | Sinonasal involvement; granulomas; c-ANCA/PR3 positive; immune deposits | p-ANCA/MPO positive (60%); older age | ANCA, CT chest, renal biopsy, bronchoscopy with BAL | Emergent | Plasmapheresis + rituximab + steroids; ICU if severe DAH |
| `lupus` (diffuse alveolar hemorrhage) | Young female; multi-system involvement; positive ANA/anti-dsDNA; low complements; hemoptysis; bilateral infiltrates; full-house IF on renal biopsy | Male; age >50; normal complement; negative ANA; isolated renal disease | Female; African American/Hispanic; age 15-45; non-compliance with immunosuppression | ANA, anti-dsDNA, complement levels, CBC, urinalysis, renal biopsy, bronchoscopy with BAL, chest CT | Emergent | Pulse steroids + immunosuppression; plasmapheresis in severe cases; ICU |
| Goodpasture-like (anti-GBM-negative DAH + GN) | Hemoptysis + GN without anti-GBM antibodies; may have ANCA (dual-positive); or immune complex-mediated (lupus, IgAN with DAH) | Clear anti-GBM positive (then classify as anti-GBM disease); negative for all autoantibodies | Consider dual-positive ANCA + anti-GBM; consider IgAN with DAH; consider drug-induced | Full autoimmune panel, ANCA, anti-GBM, complement levels, renal biopsy, bronchoscopy | Emergent | Treat based on underlying etiology; aggressive supportive care |

> **Clinical Pearl:** Pulmonary-renal syndrome is a medical emergency. The three most common causes are `antiGbm` disease, ANCA-associated vasculitis (`anca`), and `lupus` nephritis with diffuse alveolar hemorrhage. Initiate empiric treatment while awaiting confirmatory results.

> **Clinical Pearl:** Bronchoscopy with BAL showing hemosiderin-laden macrophages confirms alveolar hemorrhage. This should be obtained urgently when pulmonary-renal syndrome is suspected.

> **Clinical Pearl:** 10-30% of patients with apparent anti-GBM disease also have positive ANCA. These dual-positive patients require both anti-GBM and ANCA-directed therapy.

---

### 2.11 Pregnancy with Renal Disease

**Definition:** Renal disease presenting during or complicated by pregnancy, requiring evaluation distinguishing physiological changes from pathological conditions.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| Pre-eclampsia / Eclampsia | >20 weeks gestation; new-onset hypertension; proteinuria; edema; thrombocytopnia; elevated LFTs; HELLP syndrome (hemolysis, elevated LFTs, low platelets); headache, visual changes | Onset <20 weeks; pre-existing hypertension without worsening; no proteinuria; normal platelets/LFTs | First pregnancy; multiple gestation; prior pre-eclampsia; DM; HTN; autoimmune disease; obesity | UA, UPC, CBC, LFTs, LDH, haptoglobin, uric acid, Doppler ultrasound (uterine artery), fetal monitoring | Urgent | Delivery is the definitive treatment; magnesium sulfate for seizure prophylaxis; antihypertensives; monitor for complications |
| `lupus` nephritis flare | Young female with known SLE; worsening proteinuria; active urinary sediment; low complements; rising anti-dsDNA; flare during pregnancy | No prior SLE diagnosis; normal complements; negative autoantibodies; stable renal function | Known SLE; prior nephritis; low complements pre-pregnancy; African American/Hispanic | ANA, anti-dsDNA, complement levels, CBC, urinalysis, 24-hr urine protein, renal biopsy (if unclear) | Urgent | Steroids (prednisone); azathioprine (safe in pregnancy); avoid MMF/cyclophosphamide; monitor fetal growth |
| `iga` (exacerbation) | Known IgAN; worsening proteinuria or hematuria during pregnancy; hypertension; normal complement; mesangial IgA on prior biopsy | No prior IgAN diagnosis; nephrotic-range proteinuria; systemic features; low complement | Known IgAN; young adult; prior biopsy | UA, UPC, C3/C4, IgA level, review prior biopsy | Semi-urgent | RAAS blockade (contraindicated in pregnancy); methyldopa/labetalol; close monitoring; delivery planning |
| Thrombotic microangiopathy (TMA) in pregnancy | HELLP syndrome; TTP (acquired ADAMTS13 deficiency); complement-mediated aHUS (pregnancy as trigger); schistocytosis; thrombocytopenia; AKI; hemolysis | Normal platelets; no hemolysis; no AKI | Prior TMA episodes; complement mutations; family history of TMA | CBC, smear, LDH, haptoglobin, ADAMTS13, complement testing (factor H, factor I), renal biopsy | Emergent | TTP: plasmapheresis + caplacizumab; aHUS: eculizumab; HELLP: delivery |
| Acute fatty liver of pregnancy | Third trimester; nausea/vomiting; abdominal pain; jaundice; hypoglycemia; coagulopathy; elevated LFTs; normal platelets; no hemolysis | First/second trimester; normal LFTs; hemolysis present; schistocytes | Multiple gestation; prior AFLP; LCHAD deficiency in fetus | LFTs, bilirubin, ammonia, coagulation studies, renal function, fetal monitoring | Emergent | Delivery; supportive care; monitor for DIC and multi-organ failure |
| Chronic kidney disease in pregnancy | Pre-existing CKD; proteinuria; hypertension; declining GFR; risks of maternal and fetal complications | Acute onset during pregnancy; no prior CKD history | Pre-existing CKD (type of GN); degree of proteinuria; baseline GFR; BP control | Baseline renal function, UPC, renal ultrasound, fetal growth monitoring | Semi-urgent | Pre-conception counseling; optimize BP; RAAS blockade withdrawal; close maternal-fetal monitoring; delivery planning |

> **Clinical Pearl:** Pre-eclampsia is a diagnosis of exclusion in patients with known renal disease. Distinguishing pre-eclampsia from a lupus nephritis flare or other glomerular disease exacerbation is critical and may require biopsy.

> **Clinical Pearl:** RAAS blockade (ACEi, ARBs) is absolutely contraindicated in pregnancy. Transition to methyldopa, labetalol, or nifedipine before conception or as soon as pregnancy is recognized.

> **Clinical Pearl:** TMA in pregnancy requires urgent differentiation between HELLP syndrome, TTP, and complement-mediated aHUS, as treatments differ significantly. ADAMTS13 activity is the key distinguishing test.

---

### 2.12 Post-Transplant Dysfunction

**Definition:** Renal allograft dysfunction (rising creatinine, new proteinuria, or declining GFR) in a transplant recipient, requiring evaluation for rejection, recurrence, drug toxicity, and other causes.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| ntibodyMediatedRejection | Rising creatinine; new donor-specific antibodies (DSA); C4d deposition on biopsy; microvascular inflammation (ptc, g); transplant glomerulopathy; recent non-adherence to immunosuppression | No DSA; no C4d; negative crossmatch; stable immunosuppression; non-renal cause of dysfunction | Prior sensitization; non-adherence; HLA mismatch; prior rejection episodes; cold ischemia time | CBC, CMP, urinalysis, DSA screen, renal biopsy (Banff classification), C4d staining, electron microscopy | Urgent | Plasmapheresis + IVIG; rituximab; bortezomib; optimize maintenance immunosuppression; consider Tocilizumab |
| 	CellMediatedRejection | Rising creatinine; interstitial inflammation + tubulitis on biopsy (Banff type); fever; graft tenderness; recent immunosuppression reduction; no DSA | Stable creatinine; no inflammation on biopsy; adequate immunosuppression; DSA positive (then consider ABMR) | Recent immunosuppression changes; non-adherence; viral infections (CMV, BK); HLA mismatch | CBC, CMP, urinalysis, viral serologies (CMV, BK), renal biopsy (Banff classification) | Urgent | Pulse steroids (steroid-sensitive); ATG for steroid-resistant; optimize maintenance immunosuppression |
| `bkVirusNephropathy` | Rising creatinine; BK viremia (>10,000 copies/mL); BK viruria; tubular inclusions on biopsy; interstitial inflammation; virally infected tubular cells on SV40 stain; over-immunosuppression | Negative BK PCR; no viral inclusions; stable BK viral load; adequate (not over) immunosuppression | Over-immunosuppression; prior induction with lymphocyte-depleting agents; recent treatment for rejection; African American | BK PCR (plasma and urine), renal biopsy with SV40 stain, CMV PCR, immune monitoring (DSA, T-cell subsets) | Urgent | Reduce immunosuppression (first line); consider leflunomide or cidofovir; monitor BK viral load; avoid over-treatment |
| 	ransplantGlomerulopathy | Gradual rise in proteinuria; glomerular basement membrane duplication on biopsy; double contours on silver stain; subendothelial deposits on EM; may have DSA; C4d may be positive or negative | Acute onset; normal GBM on biopsy; no DSA; no prior ABMR; isolated hematuria without proteinuria | Prior ABMR; chronic DSA; HLA mismatch; prolonged cold ischemia time; ABO-incompatible transplant | DSA screen, renal biopsy with EM (GBM duplication), C4d, proteinuria quantification | Semi-urgent | Optimize immunosuppression; treat ABMR if active; consider complement inhibition; monitor DSA |
| cniToxicity | Rising creatinine after CNI introduction/dose increase; tubular vacuolization on biopsy; isometric vacuoles; thrombotic microangiopathy; arteriolar hyalinosis (chronic); high trough levels; gingival hyperplasia, tremor (clinical toxicity) | Low/therapeutic CNI levels; no histological changes; other causes of dysfunction (rejection, infection); acute onset unrelated to dose change | Recent dose increase; concomitant CNI interactions (azole antifungals, macrolides); dehydration; nephrotoxins; genetic polymorphisms in CYP3A5 | CNI trough levels (tacrolimus/cyclosporine), renal biopsy (isometric vacuolization, TMA), viral serologies | Semi-urgent | Reduce CNI dose; convert to mTOR inhibitor or belatacept-based regimen; optimize immunosuppression; monitor levels |
| Recurrence of primary disease | Proteinuria and/or declining GFR in the allograft; histological pattern matching original disease; timeline varies by disease (early for FSGS, late for IgAN) | Normal allograft function; no proteinuria; no histological recurrence; different histological pattern | Disease-specific: FSGS (high recurrence, especially post-transplant), IgAN (recurrence in 30-50%), MPGN/C3G (recurrence), anti-GBM (rare if >12 months post-native), ANCA (variable) | Review original native kidney biopsy, DSA screen, renal biopsy of allograft, disease-specific serologies | Semi-urgent to Urgent | Disease-specific treatment; plasmapheresis for FSGS recurrence; optimize immunosuppression; consider complement inhibition for C3G |
| Acute tubular necrosis | Recent surgery/ischemia; delayed graft function; muddy brown casts; bland sediment; no DSA; no inflammation on biopsy; recovery expected | Active sediment; DSA positive; inflammation on biopsy; persistent dysfunction beyond expected recovery | Prolonged cold ischemia; recipient age; donor quality; perioperative hypotension; calcineurin inhibitor toxicity | CBC, CMP, urinalysis, renal ultrasound with Doppler, CNI levels, DSA screen | Urgent | Supportive; optimize hemodynamics; remove nephrotoxins; consider dialysis if needed; monitor for recovery |

> **Clinical Pearl:** In any transplant patient with rising creatinine, the differential must include ALL of: rejection (TCMR and ABMR), infection (BK virus, CMV), drug toxicity (CNI), recurrence of primary disease, and surgical/obstructive causes. A biopsy is often the only way to distinguish these.

> **Clinical Pearl:** BK virus nephropathy requires a delicate balance: reduce immunosuppression enough to control viral replication but not so much as to trigger rejection. Monitor both BK viral load AND donor-specific antibodies during treatment.

> **Clinical Pearl:** FSGS recurs in 20-40% of patients post-transplant. Consider peri-operative plasmapheresis in high-risk patients (rapidly progressive native kidney disease, previous recurrence, non-APOL1-mediated disease).

---

### 2.13 TMA (Thrombotic Microangiopathy)

**Definition:** The clinical triad of microangiopathic hemolytic anemia (schistocytes, elevated LDH, low haptoglobin, elevated reticulocyte count), thrombocytopenia, and organ damage (most commonly renal, but also neurological and gastrointestinal).

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| TTP (Thrombotic Thrombocytopenic Purpura) | ADAMTS13 activity <10% (acquired deficiency); fever; neurological symptoms (confusion, seizure, stroke); renal involvement (mild-moderate); petechiae/purpura; severe thrombocytopenia; microangiopathic hemolytic anemia | ADAMTS13 >50% (unlikely TTP); no neurological symptoms; moderate thrombocytopenia; renal-predominant; diarrhea prodrome | Acquired ADAMTS13 deficiency (autoantibody); pregnancy; quinine; ticlopidine/clopidogrel; family history (congenital TTP - Upshaw-Schulman syndrome) | CBC, smear (schistocytes), LDH, haptoglobin, reticulocyte count, ADAMTS13 activity, direct Coombs, renal function, neurological assessment | Emergent | Plasmapheresis (daily until ADAMTS13 >50%); caplacizumab; glucocorticoids; rituximab for refractory/relapsing; avoid platelet transfusion; emergent dialysis if severe AKI |
| STEC-HUS (Shiga Toxin-Producing E. coli HUS) | Bloody diarrhea (hemorrhagic colitis); abdominal pain; fever; AKI (severe); thrombocytopenia; hemolytic anemia; children <5 years; Shiga toxin positive; ADAMTS13 >10% | No diarrhea; no bloody stool; adults; ADAMTS13 <10% (then consider TTP); no Shiga toxin | Children <5; summer/farm exposure; contaminated food/water; daycare outbreaks | CBC, smear, LDH, haptoglobin, stool culture (EHEC), Shiga toxin assay, ADAMTS13, renal function | Emergent | Supportive care (no plasmapheresis, no eculizumab); dialysis if needed; avoid antibiotics and anti-motility agents; monitor for complications |
| aHUS (Atypical HUS - Complement-Mediated) | Complement pathway mutations (factor H, factor I, MCP/CD46, factor B, C3); ADAMTS13 >10%; no diarrhea prodrome; renal-predominant; family history; relapsing course; pregnancy-associated | ADAMTS13 <10% (then consider TTP); clear STEC-HUS; no complement mutations; diarrhea prodrome; single episode resolving completely | Family history; complement mutations; prior aHUS; pregnancy; autoimmune (anti-factor H antibodies); calcineurin inhibitor-associated; pneumococcal infection (children) | CBC, smear, LDH, haptoglobin, ADAMTS13, Shiga toxin, complement testing (CH50, AH50, C3, factor H, factor I, factor B, MCP), anti-factor H antibodies, renal biopsy | Emergent | Eculizumab (anti-C5, first-line); vaccinate against Neisseria meningitidis before starting; monitor for complement-mediated TMA in transplant; plasma exchange for anti-factor H antibody-mediated |
| Drug-Induced TMA | Temporal relationship with drug exposure; calcineurin inhibitors (tacrolimus, cyclosporine); sirolimus; quinine; ticlopidine/clopidogrel; clopidogrel; cocaine (adulterated); oxymorphone; gemcitabine; mitomycin C | No temporal relationship with drug; ADAMTS13 <10% (then TTP); clear STEC-HUS; complement mutations | Specific drug exposure; dose-dependent (some); idiosyncratic (others); concurrent dehydration/nephrotoxins | CBC, smear, LDH, haptoglobin, ADAMTS13, complement testing, drug history, renal biopsy | Urgent | Discontinue offending drug; supportive care; plasmapheresis if severe; consider eculizumab if complement-mediated |
| Malignant hypertension-associated TMA | Severely elevated BP (>180/120); grade III-IV retinopathy; papilledema; AKI; proteinuria; hematuria; thrombocytopenia; hemolytic anemia; seizures; encephalopathy | Moderate hypertension; no retinopathy; no neurological symptoms; ADAMTS13 <10% (then TTP) | Severe uncontrolled hypertension; non-adherence to medications; secondary hypertension (pheochromocytoma, renal artery stenosis) | Blood pressure monitoring, CBC, smear, LDH, haptoglobin, renal function, fundoscopy, echocardiography, renal artery imaging, ADAMTS13 | Emergent | Gradual BP reduction (avoid rapid lowering); IV labetalol/nicardipine; nicardipine for BP control; dialysis if needed; address underlying cause |
| Secondary TMA (other causes) | SLE (lupus nephritis with TMA); antiphospholipid syndrome; scleroderma renal crisis; HIV-associated TMA; pregnancy-related; cobalamin C deficiency (children) | No underlying autoimmune disease; no antiphospholipid antibodies; no scleroderma features; HIV negative | SLE; antiphospholipid antibodies; scleroderma skin changes; HIV risk factors; family history (cobalamin C deficiency) | ANA, antiphospholipid antibodies, complement levels, HIV, cobalamin levels, renal biopsy | Urgent | Treat underlying cause; complement inhibition if aHUS overlap; immunosuppression for autoimmune causes |

> **Clinical Pearl:** ADAMTS13 activity is THE critical test in TMA. ADAMTS13 <10% = TTP until proven otherwise. ADAMTS13 >10% with diarrhea = STEC-HUS. ADAMTS13 >10% without diarrhea = consider aHUS, drug-induced, or secondary TMA.

> **Clinical Pearl:** Never transfuse platelets in TTP. Platelet transfusion provides substrate for further thrombus formation and can precipitate life-threatening complications.

> **Clinical Pearl:** Empiric plasmapheresis should be initiated for suspected TTP while awaiting ADAMTS13 results. Delay in treatment significantly increases mortality.

> **Clinical Pearl:** Eculizumab for aHUS requires meningococcal vaccination BEFORE initiation. Patients are at lifelong risk for meningococcal infection while on complement inhibition.

---

### 2.14 Complement Consumption (Low C3/C4)

**Definition:** Decreased complement levels (C3, C4, or both) in the context of renal disease, indicating complement pathway activation.

| Disease | Supporting Evidence | Evidence Against | Likelihood Modifiers | Required Investigations | Urgency | Next Step |
|---|---|---|---|---|---|---|
| `lupus` nephritis | Low C3 AND low C4 (classical + alternative pathway); positive ANA/anti-dsDNA; multi-system involvement; full-house IF on biopsy; young female | Male; age >50; normal complement; negative ANA; isolated renal disease | Female (9:1); African American/Hispanic; age 15-45; family history of autoimmune disease | ANA, anti-dsDNA, complement levels, CBC, urinalysis, renal biopsy | Urgent | Biopsy; classify ISN/RPS; immunosuppression |
| `cryoglobulinemic` | Low C4 (classical pathway); HCV positive (80%); palpable purpura; arthralgia; peripheral neuropathy; cryoglobulins positive; MPGN pattern on biopsy | HCV negative; normal C4; no cryoglobulins; no purpura; no neuropathy | HCV infection; mixed cryoglobulinemia (type II or III); IgM rheumatoid factor positive | HCV RNA, cryoglobulins, complement levels, SPEP, rheumatoid factor, renal biopsy | Urgent | Treat HCV (DAAs); rituximab for severe vasculitis; plasmapheresis |
| `c3` (C3 Glomerulopathy) | Low C3 with NORMAL C4 (alternative pathway only); dominant C3 on IF; dense deposits on EM (DDD) or subendothelial/mesangial deposits (C3GN); C3 nephritic factor | Normal complements; full-house IF (lupus); IgA dominant; post-infectious pattern; low C4 | Low C3 with GN; C3 nephritic factor; factor H/I deficiency; monoclonal gammopathy | C3, C4, C3 nephritic factor, complement pathway testing (factor H, factor I, factor B), renal biopsy, SPEP | Semi-urgent | Biopsy; complement workup; identify underlying complement dysregulation; consider eculizumab in selected cases |
| `irgn` (Post-infectious GN) | Low C3 (80%) with normal or mildly low C4 (alternative + classical pathway activation); preceding infection; acute nephritis; subepithelial humps on EM; self-limiting | No preceding infection; chronic course; very low C4; endocapillary crescents; systemic vasculitis features | Post-pharyngitis in children; post-impetigo in children; post-staphylococcal | ASO, anti-Dnase B, C3, C4, blood cultures, renal biopsy | Semi-urgent | Supportive; monitor for resolution (C3 normalizes in 6-8 weeks); biopsy if no recovery |
| aHUS (Complement-Mediated TMA) | Low C3 (alternative pathway consumption); ADAMTS13 >10%; no diarrhea prodrome; renal-predominant TMA; complement mutations (factor H, factor I, MCP) | ADAMTS13 <10% (then TTP); clear STEC-HUS; normal C3; complement mutations absent | Family history; complement mutations; prior aHUS; pregnancy | ADAMTS13, Shiga toxin, complement testing (CH50, AH50, C3, factor H, factor I, factor B, MCP), renal biopsy | Emergent | Eculizumab (anti-C5); vaccinate against Neisseria meningitidis before starting |
| Membranoproliferative GN (MPGN pattern) | Low C3 and/or C4; MPGN pattern on biopsy (mesangial expansion, subendothelial deposits, GBM duplication); may have IgG, IgM, C3 deposits | Normal complements; no MPGN pattern; no immune deposits | HCV-associated (low C4); HBV-associated; SLE-associated; C3 glomerulopathy; monoclonal gammopathy-associated | HCV RNA, HBV serologies, complement levels, SPEP, UPEP, renal biopsy, immunofluorescence | Semi-urgent to Urgent | Treat underlying cause; biopsy with complete workup; immunosuppression based on etiology |
| Monoclonal gammopathy-associated | Low C3 and/or C4; monoclonal protein on SPEP/UPEP; complement consumption by monoclonal immunoglobulin; MPGN or C3G pattern on biopsy | No monoclonal protein; normal complement; no gammopathy | Age >50; monoclonal gammopathy of undetermined significance (MGUS); multiple myeloma; Waldenstrom macroglobulinemia | SPEP, UPEP, free light chains, serum immunofixation, complement levels, renal biopsy | Semi-urgent | Hematology consult; treat underlying gammopathy; rituximab or bortezomib-based regimen |
| Infective endocarditis-associated GN | Low C3; blood cultures positive; cardiac vegetations on echocardiography; GN (may be MPGN, crescentic, or post-infectious pattern); fever; new murmur | Negative blood cultures; no vegetations; no fever; no cardiac risk factors | IV drug use; prosthetic valve; poor dentition; indwelling catheters | Blood cultures (3 sets), echocardiography (TTE/TEE), C3, C4, renal biopsy | Urgent | Prolonged antibiotics; surgical valvular intervention if indicated; renal function monitoring |

> **Clinical Pearl:** Low C3 with NORMAL C4 points to alternative pathway activation: `c3` glomerulopathy, post-infectious GN, or aHUS. Low C3 with LOW C4 points to classical pathway activation: `lupus`, `cryoglobulinemic`, or immune complex-mediated GN.

> **Clinical Pearl:** Always check SPEP/UPEP in any patient with unexplained complement consumption. Monoclonal immunoglobulins can activate the complement pathway directly, causing MPGN or C3 glomerulopathy.

> **Clinical Pearl:** Complement levels should be drawn BEFORE initiating treatment, as immunosuppression may normalize levels and mask the underlying pathology.

---

## 3. Disease-Specific DDx Deep Dives

This section provides a detailed differential diagnosis for each of the 23 diseases in the GDES platform, covering commonly confused conditions, key distinguishing features, common diagnostic errors, and overlap syndromes.

---

### 3.1 lport (Alport Syndrome)

**Diseases Most Commonly Confused With:**
- 	hinBasementMembrane (thin GBM without progression)
- iga (recurrent hematuria in young adults)
- sgs (familial forms with proteinuria)
- Chronic lupus nephritis with hearing loss (rare overlap)

**Key Distinguishing Features:**

| Feature | lport | 	hinBasementMembrane | iga | sgs (genetic) |
|---|---|---|---|---|
| GBM on EM | Lamellation, splitting, basket-weave | Uniformly thin (<275 nm) | Normal to mildly abnormal | Normal or FPE |
| Family history of ESRD | Yes (X-linked 85%) | Hematuria only, no ESRD | Clustering but no ESRD pattern | May have family history |
| Hearing loss | Sensorineural (high-frequency) | Absent | Absent | Absent |
| Ocular anomalies | Lenticonus, maculopathy | Absent | Absent | Absent |
| COL4 mutations | Yes (COL4A3/A4/A5) | May have COL4A3/A4 | No | No |
| Proteinuria progression | Inevitable in males (X-linked) | Rare | Variable | Variable |
| Skin biopsy IF | Alpha-5 chain absent (X-linked) | Alpha-5 present | Alpha-5 present | Alpha-5 present |

**Common Diagnostic Errors:**
1. Diagnosing 	hinBasementMembrane without checking family history or performing genetic testing -- some patients labeled as TBMN actually have carrier status for lport
2. Failing to perform audiology and ophthalmology screening in patients with unexplained hematuria and CKD
3. Not performing renal biopsy with EM in young patients with "unexplained" CKD
4. Missing X-linked lport in females (who may have mild hematuria and late-onset CKD)

> **How to Avoid Missing lport:** In ANY patient with persistent hematuria, ask about family history of kidney disease and hearing loss. If either is present, proceed directly to genetic testing (COL4A3/A4/A5) rather than relying solely on biopsy. Skin biopsy for alpha-5(IV) chain can screen for X-linked lport in males.

**Overlap Syndromes:**
- lport + 	hinBasementMembrane: Carriers of COL4A3/A4 mutations may have thin GBM without progression. Distinguishing requires genetic testing.
- lport + iga: Rare cases of IgAN superimposed on Alport carrier status
- Post-transplant anti-GBM disease: 3-5% of lport patients develop anti-GBM antibodies post-transplant (targeting the alpha-3/4/5(IV) chain they lack), though most do not develop clinical disease

---

### 3.2 nca (ANCA-Associated Vasculitis)

**Diseases Most Commonly Confused With:**
- ntiGbm disease (especially dual-positive ANCA + anti-GBM)
- lupus nephritis with pauci-immune features
- irgn (post-staphylococcal GN may mimic MPA)
- Drug-induced GN (levamisole-adulterated cocaine can cause ANCA-positive vasculitis)

**Key Distinguishing Features:**

| Feature | nca (GPA) | nca (MPA) | lupus | ntiGbm |
|---|---|---|---|---|
| ANCA pattern | c-ANCA/PR3 (90%) | p-ANCA/MPO (60%) | Usually ANCA-negative | Usually ANCA-negative |
| Sinonasal disease | Yes (GPA hallmark) | No | Rare | No |
| Pulmonary | Nodules, cavities, DAH | DAH, capillaritis | DAH (less common) | DAH (Goodpasture) |
| IF pattern on biopsy | Pauci-immune | Pauci-immune | Full-house | Linear IgG |
| Complement | Normal | Normal | Low C3 and C4 | Normal |
| Age | >50 | >50 | 15-45 | 20-30 or 50-70 |
| Histology | Necrotizing granulomatous | Necrotizing, no granulomas | Immune complex, wire-loops | Crescents, linear IgG |

**Common Diagnostic Errors:**
1. Obtaining ANCA by IFA only without ELISA confirmation -- can lead to false positives
2. Not distinguishing GPA from MPA (treatment differs in intensity and PJP prophylaxis)
3. Failing to check anti-GBM in all patients with ANCA-positive crescentic GN (10-30% are dual-positive)
4. Missing EGPA in patients with asthma and eosinophilia who develop renal disease
5. Not considering drug-induced ANCA-positive vasculitis (levamisole-cocaine, propylthiouracil, hydralazine)

> **How to Avoid Missing nca:** In any patient >50 with unexplained AKI and active sediment, obtain ANCA AND anti-GBM simultaneously. Do not wait for ANCA results before obtaining anti-GBM -- both should be sent stat.

**Overlap Syndromes:**
- nca + ntiGbm: 10-30% dual-positive; requires both ANCA-directed and anti-GBM-directed therapy
- nca + lupus: Rare overlap; lupus nephritis can have pauci-immune areas on biopsy
- nca + irgn: Post-staphylococcal GN can trigger ANCA-positive vasculitis (especially in endocarditis)
- Drug-induced ANCA vasculitis: Levamisole-adulterated cocaine causes atypical ANCA patterns (both PR3 and MPO), retiform purpura, and neutropenia

---

### 3.3 ntiGbm (Anti-GBM Disease)

**Diseases Most Commonly Confused With:**
- nca vasculitis (especially dual-positive)
- lupus nephritis with crescentic GN
- Severe iga with crescents
- TMA (when pulmonary hemorrhage is prominent)

**Key Distinguishing Features:**

| Feature | ntiGbm | nca | lupus crescentic | Severe iga crescentic |
|---|---|---|---|---|
| IF pattern | Linear IgG | Pauci-immune | Full-house | Mesangial + endocapillary |
| Anti-GBM | Positive | Usually negative (10-30% dual) | Negative | Negative |
| ANCA | Usually negative (10-30% dual) | Positive | Usually negative | Negative |
| Complement | Normal | Normal | Low C3/C4 | Usually normal |
| Age | 20-30 or 50-70 | >50 | 15-45 | 20-40 |
| Hemoptysis | Common (Goodpasture) | Common (GPA/MPA) | Less common | Rare |
| Sinonasal disease | Absent | GPA: present | Absent | Absent |

**Common Diagnostic Errors:**
1. Not checking anti-GBM in patients with crescentic GN and pulmonary hemorrhage
2. Failing to recognize dual-positive ANCA + anti-GBM patients (10-30%)
3. Delaying plasmapheresis while awaiting biopsy results
4. Not checking anti-GBM in post-transplant lport patients with new hematuria

> **How to Avoid Missing ntiGbm:** When you see crescentic GN on biopsy, ALWAYS check anti-GBM antibodies. Do not anchor on ANCA vasculitis -- anti-GBM disease is equally urgent and requires different treatment (plasmapheresis is essential).

**Overlap Syndromes:**
- ntiGbm + nca: 10-30% of anti-GBM patients are also ANCA-positive (dual-positive). These patients should receive both plasmapheresis + cyclophosphamide (for anti-GBM) AND rituximab (for ANCA).
- Post-transplant anti-GBM in lport: 3-5% develop anti-GBM antibodies targeting the alpha-3/4/5(IV) chain. Most do not develop clinical disease, but monitoring is essential.

---

### 3.4 ntibodyMediatedRejection (Antibody-Mediated Rejection)

**Diseases Most Commonly Confused With:**
- 	CellMediatedRejection (rising creatinine post-transplant)
- kVirusNephropathy (rising creatinine + viral inclusions)
- 	ransplantGlomerulopathy (chronic, slowly progressive)
- Recurrence of primary disease

**Key Distinguishing Features:**

| Feature | ABMR | TCMR | BK Virus | Recurrence |
|---|---|---|---|---|
| DSA | Present (de novo or pre-existing) | Absent | Absent | May be absent |
| C4d | Positive (peritubular capillaries) | Negative | Negative | Variable |
| Biopsy pattern | Microvascular inflammation, TGP | Interstitial inflammation, tubulitis | Tubular inclusions, SV40+ | Disease-specific pattern |
| BK viral load | Negative | Negative | >10,000 copies/mL | Negative |
| Treatment | Plasmapheresis + IVIG + rituximab | Pulse steroids / ATG | Reduce immunosuppression | Disease-specific |

**Common Diagnostic Errors:**
1. Not checking DSA in all transplant patients with unexplained rising creatinine
2. Confusing ABMR with TCMR on biopsy (Banff classification requires expertise)
3. Over-treating BK virus with immunosuppression reduction when ABMR is actually present
4. Missing chronic ABMR as the cause of transplant glomerulopathy

> **How to Avoid Missing ntibodyMediatedRejection:** In ANY transplant patient with rising creatinine, check DSA first. If DSA is positive, proceed to biopsy with C4d staining and electron microscopy. Do not assume rising creatinine is just "rejection" without classifying the type.

**Overlap Syndromes:**
- ABMR + TCMR: Mixed rejection is common and requires treatment of both components
- ABMR + BK virus: Reducing immunosuppression for BK may unmask subclinical ABMR
- ABMR + 	ransplantGlomerulopathy: Chronic ABMR is the most common cause of TGP

---

### 3.5 kVirusNephropathy (BK Virus Nephropathy)

**Diseases Most Commonly Confused With:**
- 	CellMediatedRejection (rising creatinine post-transplant)
- ntibodyMediatedRejection (rising creatinine post-transplant)
- cniToxicity (rising creatinine after CNI dose increase)
- Recurrence of primary disease

**Key Distinguishing Features:**

| Feature | BK Virus | TCMR | ABMR | CNI Toxicity |
|---|---|---|---|---|
| BK viral load | >10,000 copies/mL | Negative | Negative | Negative |
| DSA | Negative | Negative | Positive | Negative |
| Biopsy | Tubular inclusions, SV40+, interstitial inflammation | Interstitial inflammation, tubulitis | Microvascular inflammation, C4d+ | Isometric vacuolization, TMA |
| Immunosuppression level | Over-immunosuppressed | Inadequate | Variable | High trough levels |
| Treatment | Reduce immunosuppression | Pulse steroids/ATG | Plasmapheresis/IVIG | Reduce CNI dose |

**Common Diagnostic Errors:**
1. Not checking BK viral load in all transplant patients with unexplained rising creatinine
2. Treating BK virus as TCMR (pulse steroids worsen BK viremia)
3. Over-reducing immunosuppression, triggering rejection
4. Not monitoring DSA during BK treatment (reduction in immunosuppression can unmask ABMR)

> **How to Avoid Missing kVirusNephropathy:** In ANY transplant patient with rising creatinine, check BK viral load BEFORE biopsy. If BK viral load is >10,000 copies/mL, the diagnosis is likely BK nephropathy unless biopsy shows clear rejection. Reduce immunosuppression first, then biopsy if no improvement.

**Overlap Syndromes:**
- BK virus + ABMR: Reducing immunosuppression for BK can unmask subclinical ABMR. Monitor DSA during treatment.
- BK virus + TCMR: Co-infection and rejection can coexist. Biopsy is essential to guide treatment.
- BK virus + CNI toxicity: Both may coexist in over-immunosuppressed patients with high CNI levels.

---

### 3.6 c3 (C3 Glomerulopathy)

**Diseases Most Commonly Confused With:**
- irgn (post-infectious GN, especially when C3 is low)
- lupus nephritis (when complement is low)
- membranous (when subendothelial deposits are present)
- cryoglobulinemic GN (when C3 is low and MPGN pattern is present)
- Monoclonal gammopathy-associated GN

**Key Distinguishing Features:**

| Feature | c3 (DDD) | c3 (C3GN) | irgn | lupus |
|---|---|---|---|---|
| C3 | Low | Low | Low (resolves) | Low C3 AND C4 |
| C4 | Normal | Normal | Normal or mildly low | Low |
| IF pattern | C3 dominant (no Ig) | C3 dominant (no/minimal Ig) | C3 + Ig (starry sky) | Full-house (IgG, IgA, IgM, C3, C1q) |
| EM deposits | Intramembranous dense deposits | Subendothelial/mesangial | Subepithelial humps | Subendothelial/mesangial |
| Clinical course | Chronic, progressive | Chronic, progressive | Self-limiting (weeks) | Chronic, relapsing |
| C3 nephritic factor | Often positive | Often positive | Negative | Usually negative |

**Common Diagnostic Errors:**
1. Misdiagnosing c3 as post-infectious GN when C3 is low (post-infectious resolves; c3 is chronic)
2. Not performing complement pathway testing (factor H, factor I, factor B, C3 nephritic factor)
3. Missing monoclonal gammopathy as the trigger for complement activation
4. Failing to distinguish DDD from C3GN on EM (intramembranous vs. subendothelial deposits)

> **How to Avoid Missing c3:** When you see low C3 with glomerulonephritis and the IF shows C3-dominant deposits without significant Ig, think c3 glomerulopathy. Always check C3 nephritic factor and complement pathway proteins. Always check SPEP/UPEP to exclude monoclonal gammopathy.

**Overlap Syndromes:**
- c3 + monoclonal gammopathy: Monoclonal immunoglobulin can activate complement, causing C3 glomerulopathy. Treat the underlying gammopathy.
- c3 + irgn: Post-infectious GN can trigger persistent complement activation, evolving into C3G in rare cases
- c3 + cryoglobulinemic: Mixed cryoglobulinemia with complement consumption can mimic c3 on biopsy

---

### 3.7 cniToxicity (Calcineurin Inhibitor Toxicity)

**Diseases Most Commonly Confused With:**
- 	CellMediatedRejection (rising creatinine post-transplant)
- ntibodyMediatedRejection (rising creatinine post-transplant)
- kVirusNephropathy (rising creatinine post-transplant)
- Recurrence of primary disease

**Key Distinguishing Features:**

| Feature | CNI Toxicity | TCMR | ABMR | BK Virus |
|---|---|---|---|---|
| CNI trough level | Elevated (> target) | May be subtherapeutic | Variable | Variable |
| Biopsy | Isometric vacuolization, TMA, arteriolar hyalinosis | Interstitial inflammation, tubulitis | Microvascular inflammation, C4d+ | Tubular inclusions, SV40+ |
| DSA | Negative | Negative | Positive | Negative |
| BK viral load | Negative | Negative | Negative | >10,000 copies/mL |
| Temporal relationship | After dose increase or drug interaction | After immunosuppression reduction | After immunosuppression reduction | After over-immunosuppression |

**Common Diagnostic Errors:**
1. Treating CNI toxicity as rejection (pulse steroids worsen CNI toxicity)
2. Not checking CNI trough levels before biopsy
3. Missing drug interactions that increase CNI levels (azole antifungals, macrolides, diltiazem, grapefruit)
4. Failing to recognize chronic CNI nephropathy (arteriolar hyalinosis, striped fibrosis)

> **How to Avoid Missing cniToxicity:** In ANY transplant patient with rising creatinine, check CNI trough levels BEFORE biopsy. If levels are supratherapeutic, reduce the dose and monitor. If levels are therapeutic but biopsy shows isometric vacuolization, consider CNI toxicity and reduce exposure.

**Overlap Syndromes:**
- CNI toxicity + TMA: CNI can cause thrombotic microangiopathy. Distinguish from TTP (ADAMTS13 >10%) and aHUS (complement mutations).
- CNI toxicity + ABMR: High CNI levels may mask subclinical ABMR. When reducing CNI, monitor DSA.

---

### 3.8 cryoglobulinemic (Cryoglobulinemic Glomerulonephritis)

**Diseases Most Commonly Confused With:**
- lupus nephritis (low complements, MPGN pattern, systemic features)
- mpgn (membranoproliferative GN of other causes)
- nca vasculitis (palpable purpura, neuropathy)
- IgA vasculitis (HSP)

**Key Distinguishing Features:**

| Feature | cryoglobulinemic | lupus | mpgn (other) | nca |
|---|---|---|---|---|
| HCV | Positive (80%) | Negative | Variable | Negative |
| Cryoglobulins | Positive (type II or III) | Negative | Negative | Negative |
| C4 | Low (characteristic) | Low C3 AND C4 | Low C3 | Normal |
| IF pattern | MPGN with IgM/C3, "thrombi" | Full-house | MPGN pattern | Pauci-immune |
| Purpura | Palpable purpura (lower extremities) | Usually absent | Absent | Non-palpable (vasculitic) |
| Rheumatoid factor | Positive (IgM RF in type II) | May be positive | Negative | Negative |
| ANA/anti-dsDNA | Negative | Positive | Negative | Negative |

**Common Diagnostic Errors:**
1. Not checking HCV in all patients with MPGN pattern on biopsy
2. Misdiagnosing cryoglobulinemic GN as lupus nephritis (both have low complements and MPGN pattern)
3. Not checking cryoglobulins (technically challenging; may be falsely negative if sample handling is suboptimal)
4. Starting immunosuppression for cryoglobulinemic GN without first treating HCV

> **How to Avoid Missing cryoglobulinemic:** In ANY patient with MPGN pattern on biopsy and low C4 (with normal or mildly low C3), check HCV RNA and cryoglobulins. Do not start immunosuppression until HCV is excluded or treated.

**Overlap Syndromes:**
- cryoglobulinemic + lupus: Rare overlap; SLE can cause cryoglobulinemia. Check ANA/anti-dsDNA.
- cryoglobulinemic + mpgn: MPGN is the histological pattern; cryoglobulinemia is the etiology. Always check cryoglobulins in MPGN.
- HCV-associated membranous: HCV can cause both membranous and cryoglobulinemic GN. The IF pattern distinguishes them.

---

### 3.9 denseDepositDisease (Dense Deposit Disease / DDD)

**Diseases Most Commonly Confused With:**
- c3 (C3GN -- DDD is a subtype of C3 glomerulopathy)
- irgn (post-infectious GN with low C3)
- lupus nephritis (low complements)
- MPGN from other causes

**Key Distinguishing Features:**

| Feature | DDD | C3GN | irgn | lupus |
|---|---|---|---|---|
| EM deposits | Intramembranous dense deposits (pathognomonic) | Subendothelial/mesangial electron-dense deposits | Subepithelial humps | Subendothelial/mesangial |
| IF | C3 dominant (no/minimal Ig) | C3 dominant (no/minimal Ig) | C3 + Ig (starry sky) | Full-house |
| C3 | Low | Low | Low (resolves) | Low C3 AND C4 |
| C4 | Normal | Normal | Normal or mildly low | Low |
| Clinical | Chronic, progressive; often nephrotic; renal failure | Chronic, progressive | Self-limiting | Chronic, relapsing |
| Lipodystrophy | Partial lipodystrophy (especially acquired) | Absent | Absent | Absent |
| C3 nephritic factor | Often positive | Often positive | Negative | Usually negative |

**Common Diagnostic Errors:**
1. Misdiagnosing DDD as post-infectious GN when C3 is low (DDD is chronic; post-infectious resolves)
2. Not performing EM to identify pathognomonic intramembranous dense deposits
3. Missing acquired partial lipodystrophy as a clue to DDD
4. Not distinguishing DDD from C3GN (treatment and prognosis differ)

> **How to Avoid Missing denseDepositDisease:** When you see low C3 with MPGN pattern and C3-dominant IF, always perform EM. The pathognomonic finding is intramembranous dense deposits (ribbon-like deposits within the GBM). If present, it is DDD.

**Overlap Syndromes:**
- DDD + denseDepositDisease: These are the same entity. DDD is the older term; C3 glomerulopathy is the umbrella term.
- DDD + monoclonal gammopathy: Monoclonal immunoglobulin can activate complement, causing DDD
- DDD + partial lipodystrophy: Acquired partial lipodystrophy is strongly associated with DDD (complement-mediated adipocyte destruction)

---

### 3.10 diabeticNephropathy (Diabetic Nephropathy)

**Diseases Most Commonly Confused With:**
- sgs (in patients with diabetes and superimposed FSGS)
- Amyloidosis (nodular glomerulosclerosis can mimic Kimmelstiel-Wilson nodules)
- membranous (in patients with diabetes and superimposed membranous)
- Monoclonal gammopathy-associated nodular glomerulosclerosis

**Key Distinguishing Features:**

| Feature | diabeticNephropathy | Amyloidosis | Nodular glomerulosclerosis (non-DM) | sgs (in DM) |
|---|---|---|---|---|
| Diabetes | Present (type 1 >10 yrs, type 2 at diagnosis) | May be absent | May be present | Present |
| Retinopathy | Present (80%) | Absent | Absent | May be present |
| Nodules | Kimmelstiel-Wilson (acellular, PAS+, argentophilic) | Amorphous, Congo red+ | Monoclonal immunoglobulin deposits | Segmental sclerosis |
| Congo red | Negative | Positive (apple-green birefringence) | Negative | Negative |
| IF | IgG (linear along GBM, nonspecific), C3 | May have Ig light chain restriction | Monoclonal Ig (kappa or lambda restriction) | Negative (no immune deposits) |
| LM | Mesangial expansion, KW nodules, arteriolar hyalinosis, GBM thickening | Amorphous deposits, mesangial expansion | Nodular mesangial expansion, kappa/lambda restriction | Segmental sclerosis, FPE |

**Common Diagnostic Errors:**
1. Attributing ALL renal disease in diabetics to diabetic nephropathy without considering superimposed glomerular disease
2. Not performing biopsy when hematuria, rapid progression, or absence of retinopathy is present in a diabetic patient
3. Misdiagnosing amyloidosis as diabetic nephropathy (both cause nodular glomerulosclerosis)
4. Missing monoclonal gammopathy-associated nodular glomerulosclerosis (check SPEP/UPEP)

> **How to Avoid Missing diabeticNephropathy:** In ANY patient with diabetes and atypical features (hematuria, rapid progression, absence of retinopathy, nephrotic-range proteinuria at diabetes diagnosis, or short duration of DM), perform a biopsy to exclude superimposed glomerular disease.

**Overlap Syndromes:**
- diabeticNephropathy + membranous: Superimposed membranous nephropathy occurs in ~15% of diabetics with nephrotic syndrome
- diabeticNephropathy + sgs: Superimposed FSGS is common, especially in African Americans with APOL1 risk alleles
- diabeticNephropathy + amyloidosis: Rare overlap; nodular pattern can be confused
- Nodular glomerulosclerosis without diabetes: Consider monoclonal immunoglobulin deposition disease, amyloidosis, or idiopathic nodular glomerulosclerosis

---

### 3.11 drugInducedGn (Drug-Induced Glomerulonephritis)

**Diseases Most Commonly Confused With:**
- Primary membranous (drug-induced membranous vs. primary anti-PLA2R)
- nca vasculitis (drug-induced ANCA vasculitis)
- lupus nephritis (drug-induced lupus)
- iga (drug-induced IgAN)

**Key Distinguishing Features:**

| Feature | Drug-Induced | Primary | lupus (drug-induced) | nca (drug-induced) |
|---|---|---|---|---|
| Temporal relationship | Clear exposure before disease onset | No identifiable trigger | Drug exposure (hydralazine, procainamide, isoniazid) | Drug exposure (levamisole-cocaine, PTU, hydralazine) |
| Drug withdrawal | Disease may improve/resolve | No improvement with drug withdrawal | May improve with drug withdrawal | May improve with drug withdrawal |
| ANA/anti-dsDNA | May be positive (drug-induced lupus) | Usually negative | Positive | Usually negative |
| ANCA | May be positive (drug-induced ANCA) | Usually negative | Usually negative | Positive (PR3 and/or MPO) |
| Specific drugs | NSAIDs (MCD, interstitial), gold/penicillamine (membranous), interferon (lupus-like), lithium (NDI) | No drug association | Hydralazine, procainamide, isoniazid, minocycline | Levamisole-cocaine, PTU, hydralazine, clopidogrel |

**Common Diagnostic Errors:**
1. Not taking a thorough drug history in patients with new-onset glomerular disease
2. Treating drug-induced membranous with immunosuppression instead of simply discontinuing the drug
3. Not recognizing levamisole-adulterated cocaine as a cause of ANCA-positive vasculitis
4. Failing to distinguish drug-induced lupus from idiopathic SLE (drug-induced usually has anti-histone antibodies, no anti-dsDNA, and renal involvement is rare)

> **How to Avoid Missing drugInducedGn:** ALWAYS take a thorough medication and substance use history in patients with new-onset glomerular disease. If a temporal relationship exists between drug exposure and disease onset, discontinue the offending agent and monitor. Do not start immunosuppression until the drug is discontinued and the response is assessed.

**Overlap Syndromes:**
- NSAIDs: Can cause MCD, interstitial nephritis, and rarely FSGS
- Gold/penicillamine: Can cause membranous nephropathy (anti-PLA2R negative)
- Interferon: Can cause lupus-like syndrome, cryoglobulinemia, and membranous
- Levamisole-cocaine: Can cause ANCA-positive vasculitis, retiform purpura, and neutropenia
- Lithium: Can cause nephrogenic diabetes insipidus and chronic interstitial nephritis

---

### 3.12 ibrillaryGlomerulonephritis (Fibrillary GN)

**Diseases Most Commonly Confused With:**
- Amyloidosis (fibrillar deposits on EM)
- immunotactoidGlomerulonephritis (organized deposits, now often grouped with fibrillary GN)
- membranous (subepithelial deposits)
- c3 (C3 glomerulopathy with organized deposits)

**Key Distinguishing Features:**

| Feature | Fibrillary GN | Amyloidosis | Immunotactoid GN | membranous |
|---|---|---|---|---|
| Fibril diameter | 12-22 nm (randomly arranged) | 8-12 nm (randomly arranged) | >30 nm (microtubular, organized) | N/A (granular deposits) |
| Congo red | Negative | Positive (apple-green birefringence) | Negative | Negative |
| IF | IgG (usually IgG4), C3, kappa > lambda | May have Ig light chain restriction | IgG (usually IgG3), C3 | IgG (usually IgG4), C3 |
| Monoclonal gammopathy | 30% | 75% (AL amyloidosis) | 50% | Uncommon |
| Smoking association | Strong | Weak | Variable | None |

**Common Diagnostic Errors:**
1. Misdiagnosing fibrillary GN as amyloidosis (both show fibrillar deposits on EM, but Congo red distinguishes them)
2. Not performing Congo red staining on all biopsy specimens with amorphous deposits
3. Missing associated monoclonal gammopathy (check SPEP/UPEP)
4. Not distinguishing fibrillary GN from immunotactoid GN (diameter and arrangement differ)

> **How to Avoid Missing ibrillaryGlomerulonephritis:** When you see fibrillar deposits on EM, always perform Congo red staining. If Congo red is negative and fibrils are 12-22 nm (randomly arranged), it is fibrillary GN. If Congo red is positive, it is amyloidosis. Always check SPEP/UPEP for associated monoclonal gammopathy.

**Overlap Syndromes:**
- Fibrillary GN + monoclonal gammopathy: 30% of patients have an associated monoclonal protein. Treat the gammopathy.
- Fibrillary GN + hepatitis C: HCV can trigger fibrillary GN in rare cases
- Fibrillary GN + smoking: Strong association; smoking cessation may slow progression

---

### 3.13 sgs (Focal Segmental Glomerulosclerosis)

**Diseases Most Commonly Confused With:**
- mcd (especially in adults where biopsy may show FSGS instead of expected MCD)
- iga (with segmental sclerosis)
- diabeticNephropathy (in patients with diabetes and FSGS pattern)
- Obesity-related glomerulopathy

**Key Distinguishing Features:**

| Feature | sgs (primary) | mcd | Obesity-related | sgs (secondary) |
|---|---|---|---|---|
| Proteinuria | Nephrotic or sub-nephrotic | Nephrotic | Sub-nephrotic | Variable |
| Hematuria | Common (50-75%) | Absent | Absent | Variable |
| Biopsy | Segmental sclerosis, FPE | Normal glomeruli, FPE only | Glomerulomegaly, minimal FPE | Segmental sclerosis + cause |
| IF | Negative (no immune deposits) | Negative | Negative | Negative |
| Response to steroids | Partial/variable (30-50% complete) | Dramatic (>90%) | Not applicable | Address secondary cause |
| APOL1 risk alleles | Associated (especially collapsing) | Not associated | Not associated | Not associated |
| Recurrence post-transplant | 20-40% (primary) | Rare | No | No (secondary causes) |

**Common Diagnostic Errors:**
1. Diagnosing mcd in adults without biopsy (30% have FSGS)
2. Not classifying FSGS variant (NOS, collapsing, tip, perihilar, cellular) -- variant affects prognosis and treatment
3. Not screening for secondary causes (obesity, HIV, APOL1, drugs, viral infections) before starting immunosuppression
4. Missing collapsing FSGS in HIV+ patients or patients with APOL1 high-risk genotypes
5. Not performing genetic testing in young patients with FSGS (COL4A3/A4/A5, NPHS1, NPHS2, ACTN4, INF2)

> **How to Avoid Missing sgs:** In adults with nephrotic syndrome, always perform a biopsy. If FSGS is found, classify the variant and screen for secondary causes before starting immunosuppression. In young patients with FSGS, consider genetic testing before immunosuppression.

**Overlap Syndromes:**
- sgs + mcd: Some patients have features of both; FSGS may be a progression of MCD
- sgs + iga: Superimposed IgAN on FSGS can occur; full-house IF pattern may be present
- sgs + APOL1: APOL1 high-risk genotypes (G1/G2) increase risk of FSGS, especially collapsing variant
- Collapsing FSGS + HIV: Classic association; HIV viral load should be checked in all collapsing FSGS
- Recurrent FSGS post-transplant: Plasmapheresis may be therapeutic; permeability factor may be involved

---

### 3.14 hivan (HIV-Associated Nephropathy / HIVAN)

**Diseases Most Commonly Confused With:**
- Collapsing sgs (HIVAN is a form of collapsing FSGS)
- lupus nephritis (HIV can cause false-positive ANA)
- iga (in patients with HIV and hematuria)
- membranous (in patients with HIV)

**Key Distinguishing Features:**

| Feature | HIVAN | Collapsing FSGS (non-HIV) | lupus nephritis | iga |
|---|---|---|---|---|
| HIV status | Positive (active viremia) | Negative | Negative | Negative |
| Biopsy | Collapsing FSGS + microcystic tubular dilation + tubuloreticular inclusions | Collapsing FSGS without microcystic changes | Full-house IF, wire-loop lesions | Mesangial IgA |
| ANA | May be false-positive | Negative | Positive | Negative |
| Viral load | High | N/A | N/A | N/A |
| Kidney size | Large echogenic | Variable | Variable | Normal |
| Race | African American (APOL1 high-risk) | Variable | Variable | Variable |
| Response to ART | May improve if started early | Address underlying cause | Immunosuppression | Supportive |

**Common Diagnostic Errors:**
1. Misdiagnosing HIVAN as lupus nephritis (false-positive ANA in HIV)
2. Not checking HIV in all patients with collapsing FSGS
3. Not linking large echogenic kidneys + proteinuria + hematuria + HIV to HIVAN
4. Failing to start antiretroviral therapy (ART) promptly -- ART is the primary treatment

> **How to Avoid Missing hivan:** In ANY patient with collapsing FSGS on biopsy, check HIV status. In HIV+ patients with proteinuria and large echogenic kidneys, HIVAN is the most likely diagnosis. Start ART immediately -- this is the primary treatment.

**Overlap Syndromes:**
- HIVAN + APOL1: APOL1 high-risk genotypes dramatically increase the risk of HIVAN in HIV+ patients
- HIVAN + sgs: HIVAN is a specific form of collapsing FSGS caused by direct HIV infection of podocytes and tubular epithelial cells
- HIV + iga: HIV can trigger IgA nephropathy (mesangial IgA deposits)
- HIV + membranous: HIV can cause membranous nephropathy (usually anti-PLA2R negative)

---

### 3.15 iga (IgA Nephropathy)

**Diseases Most Commonly Confused With:**
- 	hinBasementMembrane (both present with hematuria in young adults)
- lport (hereditary nephritis with hematuria)
- irgn (post-infectious GN with hematuria)
- lupus nephritis (can mimic IgAN in young females)

**Key Distinguishing Features:**

| Feature | iga | 	hinBasementMembrane | lport | irgn |
|---|---|---|---|---|
| Hematuria pattern | Episodic, synpharyngitic | Persistent, continuous | Persistent from childhood | Acute, post-infection |
| C3/C4 | Normal | Normal | Normal | Low C3 |
| IgA level | Elevated in 50% | Normal | Normal | Normal |
| IF on biopsy | Mesangial IgA (dominant) | Normal (or minimal) | Normal (or minimal) | C3 + Ig (starry sky) |
| GBM on EM | Normal to mildly abnormal | Thin (<275 nm) | Lamellation, splitting | Normal |
| Family history | Clustering, no ESRD pattern | Hematuria only | ESRD, deafness | Absent |
| Progression | 20-30% progress to ESRD over 20 years | Benign, rarely progresses | Inevitable in males (X-linked) | Self-limiting |

**Common Diagnostic Errors:**
1. Not performing biopsy in patients with persistent hematuria and proteinuria >0.5 g/day
2. Misdiagnosing 	hinBasementMembrane as iga (or vice versa) without EM
3. Not performing Oxford classification (MEST-C) on IgAN biopsies
4. Missing lport in young patients with "unexplained" hematuria and CKD

> **How to Avoid Missing iga:** In young adults (20-40) with recurrent gross hematuria concurrent with URIs, iga is the most likely diagnosis. Perform biopsy if proteinuria >0.5 g/day or GFR is declining. Always request Oxford classification (MEST-C) on the pathology report.

**Overlap Syndromes:**
- iga + 	hinBasementMembrane: Can coexist; thin GBM may be an incidental finding in IgAN
- iga + lupus: Mesangial IgA deposits can occur in lupus nephritis (class II)
- iga + iga vasculitis (HSP): Same pathogenesis; HSP is the systemic form
- iga + liver disease: IgAN is associated with cirrhosis and liver disease (aberrant IgA1 glycosylation)

---

### 3.16 irgn (Infection-Related Glomerulonephritis)

**Diseases Most Commonly Confused With:**
- iga (hematuria in young adults, but timing differs)
- lupus nephritis (low complements, full-house IF)
- c3 (C3 glomerulopathy with low C3)
- nca vasculitis (post-staphylococcal GN can trigger ANCA)

**Key Distinguishing Features:**

| Feature | irgn (post-strep) | iga | lupus | c3 |
|---|---|---|---|---|
| Preceding infection | Yes (1-3 wks pharyngitis, 3-6 wks skin) | Synpharyngitic (concurrent, not preceding) | No | No |
| C3 | Low (80%, resolves in 6-8 wks) | Normal | Low C3 AND C4 | Low C3 (persists) |
| C4 | Normal or mildly low | Normal | Low | Normal |
| IF | C3 + Ig (starry sky) | Mesangial IgA (dominant) | Full-house | C3 dominant (no/minimal Ig) |
| EM | Subepithelial humps | Mesangial deposits | Subendothelial/mesangial | Subendothelial/mesangial |
| Course | Self-limiting (weeks) | Chronic, progressive | Chronic, relapsing | Chronic, progressive |
| ASO | Elevated | Normal | Normal | Normal |

**Common Diagnostic Errors:**
1. Not checking ASO and anti-DNase B in patients with acute nephritis and low C3
2. Misdiagnosing post-staphylococcal GN as nca vasculitis (ANCA can be positive in staph-associated GN)
3. Not recognizing that irgn resolves (C3 normalizes in 6-8 weeks) -- if C3 remains low, consider c3 glomerulopathy
4. Performing biopsy unnecessarily in classic post-streptococcal GN in children (clinical diagnosis is often sufficient)

> **How to Avoid Missing irgn:** In children with acute nephritis after pharyngitis or skin infection, the most likely diagnosis is post-streptococcal GN. Check C3 (low) and ASO (elevated). Most cases resolve with supportive care. If C3 does not normalize in 6-8 weeks, reconsider the diagnosis.

**Overlap Syndromes:**
- irgn + c3: Post-infectious GN can trigger persistent complement activation, evolving into C3 glomerulopathy in rare cases
- irgn + nca: Post-staphylococcal GN can trigger ANCA-positive vasculitis (especially in endocarditis)
- irgn + membranous: HCV-associated membranous can coexist with infection-related GN

---

### 3.17 lupus (Lupus Nephritis)

**Diseases Most Commonly Confused With:**
- iga (mesangial proliferation, hematuria in young adults)
- nca vasculitis (pauci-immune areas on biopsy, low complements)
- c3 (C3 glomerulopathy with low complements)
- membranous (subepithelial deposits)

**Key Distinguishing Features:**

| Feature | lupus nephritis | iga | nca | c3 |
|---|---|---|---|---|
| ANA/anti-dsDNA | Positive | Negative | Negative | Negative |
| Complement | Low C3 AND C4 | Normal | Normal | Low C3 (C4 normal) |
| IF pattern | Full-house (IgG, IgA, IgM, C3, C1q) | Mesangial IgA | Pauci-immune | C3 dominant |
| Demographics | Female (9:1), 15-45, AA/Hispanic | M>F, 20-40, East Asian | >50 | Variable |
| Systemic features | Multi-system (rash, arthritis, serositis) | Isolated renal | Sinonasal (GPA), renal-limited (MPA) | Isolated renal |
| ISN/RPS classification | Class I-VI (critical for treatment) | Oxford (MEST-C) | Not applicable | Not applicable |

**Common Diagnostic Errors:**
1. Not performing renal biopsy in all patients with suspected lupus nephritis (ISN/RPS classification guides treatment)
2. Misclassifying lupus nephritis class (e.g., calling class IV class II) -- this changes treatment dramatically
3. Not checking complement levels and anti-dsDNA to monitor disease activity
4. Missing "full-house" IF pattern (pathognomonic for lupus but can be subtle)
5. Not recognizing lupus nephritis in males or patients >45 (can occur but less common)

> **How to Avoid Missing lupus:** In ANY young female with unexplained renal disease, check ANA and complement levels. If ANA is positive and complements are low, proceed to renal biopsy. Always request ISN/RPS classification on the pathology report.

**Overlap Syndromes:**
- lupus + membranous: Lupus nephritis class V (membranous) can coexist with other classes
- lupus + nca: Rare overlap; lupus nephritis can have pauci-immune areas on biopsy
- lupus + TMA: Lupus nephritis can cause thrombotic microangiopathy
- Drug-induced lupus: Can mimic idiopathic SLE but usually has anti-histone antibodies and less renal involvement

---

### 3.18 mcd (Minimal Change Disease)

**Diseases Most Commonly Confused With:**
- sgs (especially in adults where biopsy may show FSGS instead of expected MCD)
- Early membranous (nephrotic syndrome without clear cause)
- iga (in children with nephrotic syndrome and hematuria)

**Key Distinguishing Features:**

| Feature | mcd | sgs | membranous | iga |
|---|---|---|---|---|
| Age | Children (2-6 years) peak | Any age; African American > Caucasian | 40-60 years | 20-40 years |
| Hematuria | Absent | Common (50-75%) | Rare | Common |
| Proteinuria | Nephrotic-range, abrupt onset | Nephrotic or sub-nephrotic, gradual | Nephrotic-range, insidious | Variable |
| Biopsy (LM) | Normal | Segmental sclerosis | GBM thickening | Mesangial hypercellularity |
| IF | Negative | Negative | IgG/C3 granular | Mesangial IgA |
| EM | FPE only | FPE + segmental sclerosis | Subepithelial deposits | Mesangial deposits |
| Steroid response | >90% complete | 30-50% partial/variable | Variable | Not primarily steroid-treated |

**Common Diagnostic Errors:**
1. Diagnosing mcd in adults without biopsy (30% have FSGS)
2. Not performing biopsy in adults with nephrotic syndrome (empiric steroids without biopsy is inappropriate in adults)
3. Not recognizing that mcd can relapse frequently (minimal change nephrotic syndrome)
4. Missing secondary causes of MCD (drugs, infections, malignancy, allergies)

> **How to Avoid Missing mcd:** In children with classic nephrotic syndrome (abrupt onset, edema, heavy proteinuria, bland sediment, normal GFR), empiric steroids may be appropriate. In ALL adults, perform a biopsy before starting immunosuppression.

**Overlap Syndromes:**
- mcd + sgs: Some patients have features of both; FSGS may be a progression of MCD
- mcd + iga: Rare overlap; IgA deposits can be coincidental
- Drug-induced MCD: NSAIDs, lithium, and interferon can cause MCD
- MCD + atopy: Strong association with atopic dermatitis, asthma, and allergic rhinitis

---

### 3.19 membranous (Membranous Nephropathy)

**Diseases Most Commonly Confused With:**
- sgs (nephrotic syndrome without clear cause)
- diabeticNephropathy (in patients with diabetes)
- lupus nephritis class V (membranous pattern)
- Amyloidosis (subepithelial deposits)
- cryoglobulinemic GN (when membranous pattern is present)

**Key Distinguishing Features:**

| Feature | membranous (primary) | lupus class V | diabeticNephropathy | Amyloidosis |
|---|---|---|---|---|
| Anti-PLA2R | Positive (70-80%) | Negative | Negative | Negative |
| ANA/anti-dsDNA | Negative | Positive | Negative | Negative |
| Complement | Normal | Low C3 AND C4 | Normal | Normal |
| IF | IgG/C3 granular (subepithelial) | Full-house | Linear IgG (nonspecific) | May have Ig light chain restriction |
| LM | GBM thickening, spike and dome | GBM thickening, wire-loop | KW nodules, mesangial expansion | Amorphous deposits, Congo red+ |
| EM | Subepithelial electron-dense deposits | Subepithelial + subendothelial | GBM thickening, no deposits | Fibrils (8-12 nm), Congo red+ |
| Thrombotic risk | High (renal vein thrombosis) | Moderate | Low | Low |
| Malignancy risk | 5-10% (age-appropriate screening) | Low | Low | Low (AL amyloidosis) |

**Common Diagnostic Errors:**
1. Not checking anti-PLA2R in patients with membranous nephropathy (primary vs. secondary distinction)
2. Not performing malignancy screening in patients >40 with new-onset membranous
3. Missing secondary membranous (HCV, SLE, drug-induced)
4. Not checking for renal vein thrombosis in patients with nephrotic-range proteinuria
5. Treating secondary membranous with immunosuppression instead of addressing the underlying cause

> **How to Avoid Missing membranous:** In adults (40-60) with nephrotic syndrome and no hematuria, membranous is the most likely diagnosis. Check anti-PLA2R. If positive, it is primary membranous. If negative, screen for secondary causes (HCV, SLE, malignancy, drugs).

**Overlap Syndromes:**
- membranous + lupus: Lupus nephritis class V (membranous) can coexist with other classes. Check ANA/anti-dsDNA.
- membranous + HCV: HCV can cause membranous nephropathy (usually anti-PLA2R negative). Treat HCV first.
- membranous + malignancy: Paraneoplastic membranous can occur with solid organ tumors. Screen for malignancy.
- membranous + sgs: Superimposed FSGS on membranous indicates chronic damage and poorer prognosis.

---

### 3.20 mpgn (Membranoproliferative Glomerulonephritis)

**Diseases Most Commonly Confused With:**
- lupus nephritis (full-house IF, low complements)
- cryoglobulinemic GN (MPGN pattern, low C4)
- c3 (C3 glomerulopathy with MPGN pattern)
- Post-infectious GN (subendothelial deposits, low C3)

**Key Distinguishing Features:**

| Feature | mpgn (idiopathic) | lupus | cryoglobulinemic | c3 |
|---|---|---|---|---|
| Complement | Low C3 and/or C4 | Low C3 AND C4 | Low C4 (characteristic) | Low C3 (C4 normal) |
| IF | IgG, IgM, C3 (variable) | Full-house | IgM, C3, kappa restriction | C3 dominant (no/minimal Ig) |
| HCV | Check in all cases | Negative | Positive (80%) | Negative |
| Cryoglobulins | Negative | Negative | Positive | Negative |
| SPEP | Check in all cases | Negative | May have M-component | May have M-component |
| Treatment | Treat underlying cause | Immunosuppression | Treat HCV first | Complement inhibition |

**Common Diagnostic Errors:**
1. Not checking HCV in all patients with MPGN pattern on biopsy
2. Not checking SPEP/UPEP for monoclonal gammopathy
3. Treating MPGN with immunosuppression without identifying the underlying cause
4. Not distinguishing MPGN pattern (histological) from MPGN disease (etiology)

> **How to Avoid Missing mpgn:** MPGN is a histological pattern, NOT a disease. When you see MPGN on biopsy, always check: (1) HCV RNA, (2) SPEP/UPEP, (3) complement levels, (4) ANA/anti-dsDNA, (5) cryoglobulins. Treat the underlying cause.

**Overlap Syndromes:**
- MPGN + HCV: HCV is the most common cause of MPGN in Western countries. Treat HCV with DAAs.
- MPGN + cryoglobulinemic: Cryoglobulinemia is the most common cause of HCV-associated MPGN.
- MPGN + c3: C3 glomerulopathy can present with MPGN pattern. Distinguish by IF (C3 dominant vs. Ig + C3).
- MPGN + monoclonal gammopathy: Monoclonal immunoglobulin can activate complement, causing MPGN. Treat the gammopathy.

---

### 3.21 	CellMediatedRejection (T-Cell-Mediated Rejection)

**Diseases Most Commonly Confused With:**
- ntibodyMediatedRejection (rising creatinine post-transplant)
- kVirusNephropathy (rising creatinine post-transplant)
- cniToxicity (rising creatinine after CNI dose change)
- Recurrence of primary disease

**Key Distinguishing Features:**

| Feature | TCMR | ABMR | BK Virus | CNI Toxicity |
|---|---|---|---|---|
| DSA | Negative | Positive | Negative | Negative |
| C4d | Negative | Positive | Negative | Negative |
| Biopsy | Interstitial inflammation + tubulitis | Microvascular inflammation, C4d+ | Tubular inclusions, SV40+ | Isometric vacuolization |
| BK viral load | Negative | Negative | >10,000 copies/mL | Negative |
| CNI levels | May be subtherapeutic | Variable | Variable | Elevated |
| Treatment | Pulse steroids (steroid-sensitive); ATG (steroid-resistant) | Plasmapheresis + IVIG + rituximab | Reduce immunosuppression | Reduce CNI dose |

**Common Diagnostic Errors:**
1. Not distinguishing TCMR from ABMR on biopsy (Banff classification is essential)
2. Treating TCMR with immunosuppression reduction (this worsens rejection)
3. Missing subclinical TCMR on protocol biopsies
4. Not classifying TCMR by Banff grade (IA, IB, IIA, IIB, III) -- grade affects treatment

> **How to Avoid Missing 	CellMediatedRejection:** In ANY transplant patient with rising creatinine, perform a biopsy with Banff classification. DSA and C4d help distinguish TCMR from ABMR. Pulse steroids are first-line for TCMR; ATG for steroid-resistant cases.

**Overlap Syndromes:**
- TCMR + ABMR: Mixed rejection is common and requires treatment of both components
- TCMR + BK virus: BK virus can cause interstitial inflammation mimicking TCMR (check SV40 stain)
- TCMR + drug toxicity: CNI toxicity can coexist with TCMR; biopsy distinguishes them

---

### 3.22 	hinBasementMembrane (Thin Basement Membrane Nephropathy / TBMN)

**Diseases Most Commonly Confused With:**
- iga (recurrent hematuria in young adults)
- lport (hereditary nephritis with hematuria)
- sgs (early/subclinical with hematuria)
- Urological causes of hematuria

**Key Distinguishing Features:**

| Feature | 	hinBasementMembrane | iga | lport | sgs (early) |
|---|---|---|---|---|
| GBM thickness | Uniformly thin (<275 nm) | Normal to mildly abnormal | Lamellation, splitting | Normal or FPE |
| Family history | Hematuria (benign) | Clustering, no ESRD | ESRD, deafness, ocular | May have family history |
| Hematuria pattern | Persistent, continuous | Episodic, synpharyngitic | Persistent from childhood | Persistent |
| Proteinuria | Absent or minimal | Variable | Progressive | Variable |
| Progression to ESRD | Very rare | 20-30% over 20 years | Inevitable in males (X-linked) | Variable |
| Genetic testing | COL4A3/A4 (heterozygous carriers) | No genetic basis | COL4A3/A4/A5 | May have genetic mutations |
| Skin biopsy IF | Alpha-5 chain present | Alpha-5 present | Alpha-5 absent (X-linked males) | Alpha-5 present |

**Common Diagnostic Errors:**
1. Misdiagnosing carrier status for lport mutations as 	hinBasementMembrane (requires genetic testing to distinguish)
2. Not performing family screening in patients with TBMN
3. Not recognizing that some patients labeled "TBMN" may have COL4A3/A4 mutations and at risk for progression
4. Performing unnecessary biopsy in patients with classic TBMN (genetic testing may be sufficient)

> **How to Avoid Missing 	hinBasementMembrane:** In young adults with persistent hematuria, normal GFR, and no proteinuria, TBMN is the most likely diagnosis after iga. Consider genetic testing (COL4A3/A4) to distinguish from carrier status for lport mutations. Family screening is essential.

**Overlap Syndromes:**
- TBMN + lport carriers: Heterozygous carriers of COL4A3/A4 mutations may have thin GBM indistinguishable from TBMN. Genetic testing is required.
- TBMN + iga: Can coexist; thin GBM may be an incidental finding in IgAN
- TBMN + sgs: Early FSGS may present with hematuria and thin GBM on biopsy

---

### 3.23 	ransplantGlomerulopathy (Transplant Glomerulopathy)

**Diseases Most Commonly Confused With:**
- ntibodyMediatedRejection (chronic ABMR is the most common cause)
- Recurrence of primary disease (e.g., IgAN, MPGN, C3G)
- kVirusNephropathy (chronic BK can cause GBM changes)
- Chronic cniToxicity (arteriolar hyalinosis can coexist)

**Key Distinguishing Features:**

| Feature | 	ransplantGlomerulopathy | Chronic ABMR | Recurrence (IgAN) | BK Virus |
|---|---|---|---|---|
| DSA | May be positive | Positive | May be absent | Negative |
| C4d | May be positive or negative | Usually positive | Negative | Negative |
| Biopsy | GBM duplication, double contours | Microvascular inflammation + TGP | Disease-specific pattern (mesangial IgA) | Tubular inclusions, SV40+ |
| Proteinuria | Gradual increase | Gradual increase | Gradual increase | Variable |
| Timeline | Months to years post-transplant | Months to years | Variable (early for FSGS, late for IgAN) | Months post-transplant |
| IF | May show IgG, C3, C1q | C4d+, may show IgG | Mesangial IgA | Negative |

**Common Diagnostic Errors:**
1. Not performing DSA screening in patients with transplant glomerulopathy
2. Misdiagnosing chronic ABMR as recurrent disease (or vice versa)
3. Not performing EM to identify GBM duplication (double contours)
4. Missing subclinical transplant glomerulopathy on protocol biopsies

> **How to Avoid Missing 	ransplantGlomerulopathy:** In any transplant patient with rising proteinuria, check DSA and perform biopsy. GBM duplication (double contours) on silver stain is the hallmark. Distinguish from recurrent disease by checking DSA and reviewing the original native kidney biopsy.

**Overlap Syndromes:**
- TGP + chronic ABMR: Chronic ABMR is the most common cause of TGP. DSA and C4d help confirm.
- TGP + recurrent IgAN: IgAN recurs in 30-50% of transplant recipients. Mesangial IgA deposits confirm recurrence.
- TGP + CNI toxicity: Chronic CNI nephropathy can coexist with TGP. Arteriolar hyalinosis on biopsy suggests CNI toxicity.

---

## 4. Diagnostic Confidence Framework

This section defines the scoring system used throughout the GDES platform to grade diagnostic certainty. Every diagnosis assigned to a patient must carry a confidence score, which directly impacts treatment decisions, monitoring intensity, and prognostic discussions.

### 4.1 Confidence Level Definitions

| Level | Definition | Criteria | Action Threshold |
|---|---|---|---|
| **Definite** | Histologically proven with confirmatory clinical/lab data | Biopsy showing characteristic findings + supporting serology/clinical presentation + exclusion of alternative diagnoses | Treat definitively; proceed with definitive management plan |
| **Probable** | Strong clinical + lab evidence with suggestive but not definitive biopsy/imaging | Clinical syndrome + positive serology + biopsy consistent but not pathognomonic OR typical presentation without biopsy | Treat based on probability; plan confirmatory testing; close monitoring |
| **Possible** | Clinical syndrome + some supportive evidence but significant uncertainty | Typical clinical presentation + some lab support but incomplete workup OR atypical presentation with strong lab support | Empiric treatment may be warranted if urgent; repeat testing; close follow-up |
| **Unlikely** | Atypical presentation, weak supporting evidence, significant contradictions | Some features overlap but major criteria unmet OR atypical demographic/course OR contradictory test results | Observe; consider alternative diagnoses; do not treat for this diagnosis unless clinical deterioration |
| **Excluded** | Contradictory evidence definitively ruling out the diagnosis | Definitive negative test (e.g., negative anti-GBM, negative ANCA, normal complements when expected to be low) OR biopsy showing clear alternative diagnosis | Remove from active DDx; document rationale for exclusion |

### 4.2 Confidence Scoring by Diagnostic Modality

**Histopathology (Biopsy):**

| Finding | Confidence Contribution | Examples |
|---|---|---|
| Pathognomonic finding | +3 (Definite) | Linear IgG on IF (anti-GBM disease); intramembranous dense deposits on EM (DDD); Kimmelstiel-Wilson nodules (diabetic nephropathy); Congo red positive with apple-green birefringence (amyloidosis) |
| Characteristic finding | +2 (Probable) | Mesangial IgA on IF (IgAN); pauci-immune crescentic GN (ANCA vasculitis); full-house IF (lupus nephritis); subepithelial humps on EM (post-infectious GN) |
| Suggestive finding | +1 (Possible) | Mesangial hypercellularity (nonspecific); segmental sclerosis (FSGS NOS); GBM thickening (membranous pattern) |
| Normal biopsy | 0 (Unlikely for most GN) | Normal glomeruli on LM, IF, and EM (MCD) |
| Contradictory finding | -2 (Excluded) | Pauci-immune GN in a patient with suspected lupus nephritis; no immune deposits when immune complex GN suspected |

**Serology/Laboratory:**

| Finding | Confidence Contribution | Examples |
|---|---|---|
| Highly specific positive test | +2 (Probable) | Anti-PLA2R positive (primary membranous); anti-GBM positive (anti-GBM disease); ADAMTS13 <10% (TTP) |
| Suggestive positive test | +1 (Possible) | ANCA positive (ANCA vasculitis); low C3/C4 (lupus, cryoglobulinemia); elevated IgA (IgAN) |
| Expected negative test | +1 (Supports exclusion) | Negative anti-GBM (against anti-GBM disease); normal complements (against lupus) |
| Unexpected negative test | -1 (Against diagnosis) | Negative ANCA in suspected ANCA vasculitis; negative anti-PLA2R in suspected membranous |
| Highly specific negative test | -2 (Excluded) | ADAMTS13 >50% (excludes TTP); negative ANA (excludes lupus) |

**Clinical Presentation:**

| Finding | Confidence Contribution | Examples |
|---|---|---|
| Classic presentation | +2 (Probable) | Young adult with synpharyngitic hematuria (IgAN); child with nephrotic syndrome responding to steroids (MCD) |
| Typical presentation | +1 (Possible) | Elderly patient with AKI and hematuria (ANCA vasculitis); young female with multi-system disease (lupus) |
| Atypical presentation | -1 (Against) | Nephrotic syndrome in a child with hematuria (less likely MCD); AKI in an elderly male with sinusitis (consider ANCA) |
| Contradictory presentation | -2 (Excluded) | Normal complements with full-house IF pattern; acute onset in a disease known for insidious course |

### 4.3 Confidence Level Calculation

The overall confidence level is determined by summing the contributions from all diagnostic modalities:

| Total Score | Confidence Level |
|---|---|
| >=5 | Definite |
| 3-4 | Probable |
| 1-2 | Possible |
| -1 to 0 | Unlikely |
| <=-2 | Excluded |

> **Clinical Pearl:** Confidence scoring is iterative. As new data become available (repeat labs, biopsy results, treatment response), the score should be updated. A "Possible" diagnosis that responds to targeted treatment should be upgraded to "Probable" or "Definite."

> **Clinical Pearl:** When confidence is "Possible" or lower, always consider whether empiric treatment is warranted based on urgency. For emergent conditions (anti-GBM, TTP), treat empirically even at "Possible" confidence. For non-urgent conditions, await definitive testing.

### 4.4 Confidence Level Actions

| Confidence Level | Treatment Decision | Monitoring | Documentation |
|---|---|---|---|
| Definite | Initiate definitive treatment per guidelines | Standard protocol monitoring | Full diagnostic workup documented; treatment rationale clear |
| Probable | Initiate treatment based on probability; plan confirmatory testing | Enhanced monitoring; reassess at defined intervals | Treatment rationale; plan for confirmatory testing |
| Possible | Consider empiric treatment if urgent; otherwise observe with repeat testing | Close monitoring; repeat testing at defined intervals | Diagnostic uncertainty acknowledged; plan for resolution |
| Unlikely | Do not treat for this diagnosis; investigate alternatives | Follow clinical course; repeat testing if needed | Alternative diagnoses listed; rationale for exclusion |
| Excluded | Do not treat; remove from active DDx | No further testing for this specific diagnosis | Definitive exclusion criteria documented |

---

## 5. Clinical Decision Trees

This section provides structured workup algorithms for five key clinical scenarios. Each decision tree guides the nephrologist from initial presentation through definitive diagnosis.

### 5.1 Patient with Nephrotic-Range Proteinuria

**Entry Point:** Spot UPC >=3.5 g/g (or 24-hr urine protein >=3.5 g)

`
Nephrotic-Range Proteinuria Identified
        |
        v
Step 1: Confirm and Quantify
- Repeat spot UPC to confirm
- 24-hr urine protein if spot UPC unreliable
- Serum albumin, lipid panel
- Check for edema (periorbital, peripheral)
        |
        v
Step 2: Assess Clinical Context
- Age? (<2 vs 2-10 vs 10-40 vs >40)
- Known diabetes? (Check HbA1c)
- Known autoimmune disease? (Check ANA, complements)
- Known HIV? (Check viral load)
- Family history of kidney disease?
- Drug exposure? (NSAIDs, gold, penicillamine, interferon)
- Malignancy history?
        |
        v
Step 3: Initial Serological Workup
- UA with microscopy (hematuria? casts?)
- CBC, CMP
- C3, C4
- Anti-PLA2R, anti-THSD7A (if age >30)
- ANA, anti-dsDNA (if any systemic features)
- SPEP, UPEP, free light chains (if age >40)
- Hepatitis B and C serologies
- HIV testing (if risk factors)
- Serum and urine protein electrophoresis
        |
        v
Step 4: Stratify by Clinical Features
        |
        +---> No hematuria, normal complements, age 40-60,
        |     anti-PLA2R positive --> Suspect `membranous`
        |     --> Biopsy; malignancy screening; rituximab
        |
        +---> No hematuria, young child (2-10), normal complements,
        |     normal GFR --> Suspect `mcd`
        |     --> Trial of steroids (if classic); biopsy if age >10
        |
        +---> Hematuria, hypertension, complement abnormalities
        |     --> Suspect `lupus`, `iga`, or `c3`
        |     --> Biopsy (ISN/RPS or Oxford classification)
        |
        +---> Known DM, retinopathy, gradual onset
        |     --> Suspect `diabeticNephropathy`
        |     --> Optimize glycemic/BP control; biopsy if atypical
        |
        +---> African American, APOL1 risk alleles, hypertension
        |     --> Suspect `fsgs`
        |     --> Biopsy; classify variant; screen secondary causes
        |
        +---> Age >50, chronic inflammation, monoclonal gammopathy
        |     --> Suspect `amyloid`
        |     --> Biopsy with Congo red; SPEP/UPEP; mass spectrometry
        |
        +---> Low C3 with normal C4, C3 dominant IF
        |     --> Suspect `c3` glomerulopathy
        |     --> Biopsy; complement pathway testing
        |
        +---> Age 50-60, smoking, fibrillary deposits on EM
        |     --> Suspect `fibrillaryGlomerulonephritis`
        |     --> Biopsy with EM; Congo red negative; SPEP/UPEP
        |
        v
Step 5: Renal Biopsy (if indicated)
- Indications: Adult nephrotic syndrome, atypical features,
  no clear secondary cause, proteinuria not responding to
  conservative management
- Request: LM, IF, EM, Congo red if amyloid suspected
- Classification: Disease-specific (MEST-C for IgAN, ISN/RPS
  for lupus, Oxford for FSGS variant)
        |
        v
Step 6: Initiate Treatment Based on Diagnosis
- Primary `membranous`: Rituximab or conservative observation
- `mcd`: Glucocorticoids (prednisone 1 mg/kg/day)
- `fsgs`: Glucocorticoids + calcineurin inhibitor
- `diabeticNephropathy`: SGLT2i + RAAS blockade + glycemic control
- `lupus` nephritis: MMF + glucocorticoids (Class III/IV)
- `c3`: Complement inhibition in selected cases
- `amyloid`: Treat underlying cause (antibiotics for AA, chemotherapy for AL)
`

> **Clinical Pearl:** The most critical decision point is whether to biopsy. In adults with nephrotic syndrome, biopsy is almost always indicated. In children with classic MCD presentation, empiric steroids may be appropriate.

> **Clinical Pearl:** Always check anti-PLA2R before biopsy in adults with suspected membranous. A positive result strongly supports primary membranous and may influence treatment timing.

---

### 5.2 Patient with Hematuria + Declining eGFR

**Entry Point:** Persistent hematuria (>=3 RBC/hpf on >=2 occasions) + declining eGFR (loss of >5 mL/min/year or new eGFR <60)

`
Hematuria + Declining eGFR
        |
        v
Step 1: Characterize the Hematuria
- Dysmorphic RBCs? (Glomerular source)
- RBC casts? (Glomerular source)
- Isomorphic RBCs? (Urological source)
- Proteinuria? (Quantify UPC)
- HTN? (New or worsening)
        |
        v
Step 2: Assess Urgency
- Cr doubling in <1 week? --> EMERGENT (anti-GBM, ANCA, TMA)
- Cr rising over 1-4 weeks? --> URGENT (ANCA, lupus, crescentic)
- Cr stable but declining over months? --> SEMI-URGENT (IgAN, FSGS)
- Cr stable, hematuria only? --> ROUTINE (IgAN, TBMN, Alport)
        |
        v
Step 3: Urgent Workup (if Cr rising rapidly)
- Stat: CBC, CMP, UA, C3, C4
- Stat: ANCA (PR3 and MPO ELISA)
- Stat: Anti-GBM antibodies
- Stat: ADAMTS13 (if TMA suspected)
- Stat: SPEP (if age >40)
- URGENT: Renal biopsy
        |
        v
Step 4: Semi-Urgent/Urgent Workup
- ANA, anti-dsDNA (if lupus suspected)
- Complement levels (C3, C4)
- IgA level
- Hepatitis B and C serologies
- HIV testing (if risk factors)
- SPEP, UPEP, free light chains
- Echocardiography (if endocarditis suspected)
- CT chest/sinuses (if ANCA vasculitis suspected)
        |
        v
Step 5: Renal Biopsy
- Indications: Active sediment + declining GFR
- Request: LM, IF, EM
- Classification: Banff (if transplant), ISN/RPS (if lupus),
  Oxford (if IgAN), pauci-immune vs. immune complex vs. anti-GBM
        |
        v
Step 6: Definitive Diagnosis and Treatment
        |
        +---> Pauci-immune GN + ANCA positive --> `anca`
        |     --> Rituximab + glucocorticoids; plasmapheresis if severe
        |
        +---> Linear IgG + anti-GBM positive --> `antiGbm`
        |     --> Plasmapheresis + cyclophosphamide + steroids
        |
        +---> Full-house IF + ANA/anti-dsDNA positive --> `lupus`
        |     --> ISN/RPS classification; MMF + steroids
        |
        +---> Mesangial IgA on IF --> `iga`
        |     --> Oxford classification (MEST-C); SGLT2i + RAAS blockade
        |
        +---> C3 dominant IF + low C3 --> `c3`
        |     --> Complement workup; consider eculizumab
        |
        +---> Crescentic GN + negative serologies
        |     --> Consider immune complex crescentic GN
        |     --> Treat underlying etiology
        |
        +---> TMA pattern + ADAMTS13 <10% --> TTP
              --> Plasmapheresis + caplacizumab + rituximab
`

> **Clinical Pearl:** When hematuria is accompanied by declining eGFR, the diagnosis is almost certainly glomerular. The critical question is: Is this pauci-immune (ANCA), anti-GBM, or immune complex? This determines treatment and urgency.

> **Clinical Pearl:** In emergent scenarios (Cr doubling in <1 week), do not wait for all serological results before initiating treatment. Start empiric treatment based on the most likely diagnosis and refine as results return.

---

### 5.3 Patient with Suspected RPGN

**Entry Point:** Rapidly rising creatinine over days to weeks + active urine sediment (dysmorphic RBCs, RBC casts, WBC casts) +/- systemic symptoms

`
Suspected RPGN
        |
        v
Step 1: EMERGENT Assessment (Hours)
- Confirm AKI: Repeat Cr, compare to baseline
- Characterize sediment: Dysmorphic RBCs? RBC casts? WBC casts?
- Assess severity: Oliguria? Anuria? Pulmonary hemorrhage?
- Vital signs: HTN? Encephalopathy?
        |
        v
Step 2: EMERGENT Labs (Same Day)
- CBC (thrombocytopenia? anemia?)
- CMP (Cr, BUN, electrolytes)
- UA with microscopy
- C3, C4
- ANCA (PR3 and MPO ELISA + IIF)
- Anti-GBM antibodies
- ADAMTS13 (if TMA suspected)
- SPEP (if age >40)
- Blood cultures (if endocarditis suspected)
        |
        v
Step 3: EMERGENT Imaging
- Chest X-ray (pulmonary hemorrhage? nodules?)
- CT chest (if DAH or nodules suspected)
- CT sinuses (if GPA suspected)
- Renal ultrasound (kidney size, obstruction?)
        |
        v
Step 4: EMERGENT Biopsy (if feasible within 24-48 hours)
- Indications: Active sediment + declining GFR + no clear contraindication
- Request: LM, IF, EM (STAT processing)
- Key findings: Crescents (>50% = severe), IF pattern (pauci-immune vs. immune complex vs. linear IgG)
        |
        v
Step 5: Initiate EMPIRIC TREATMENT (Do NOT wait for all results)
        |
        +---> Pulmonary hemorrhage + anti-GBM positive
        |     --> Plasmapheresis + cyclophosphamide + steroids
        |     --> EMERGENT; do not delay for biopsy
        |
        +---> ANCA positive + pauci-immune on biopsy
        |     --> Rituximab + glucocorticoids
        |     --> Plasmapheresis if severe (Cr >500, dialysis, DAH)
        |
        +---> ANA/anti-dsDNA positive + low complements + full-house IF
        |     --> Pulse steroids + MMF (Class III/IV lupus nephritis)
        |
        +---> Anti-GBM AND ANCA positive (dual-positive)
        |     --> Plasmapheresis + cyclophosphamide (anti-GBM)
        |     --> PLUS rituximab (ANCA)
        |
        +---> TMA + ADAMTS13 <10%
        |     --> Plasmapheresis + caplacizumab + rituximab (TTP)
        |
        +---> Crescentic GN + negative serologies
        |     --> Consider immune complex crescentic GN
        |     --> Pulse steroids + disease-specific treatment
        |
        v
Step 6: Confirm Diagnosis and Refine Treatment
- Review biopsy results (Banff classification)
- Adjust immunosuppression based on response
- Monitor for complications (infections, drug toxicity)
- Plan maintenance therapy
`

> **Clinical Pearl:** RPGN is a medical emergency. The combination of rising creatinine + active sediment + systemic symptoms should trigger immediate nephrology consultation and emergent workup.

> **Clinical Pearl:** When in doubt, treat for the most dangerous diagnosis first. Anti-GBM disease and TTP are the most time-sensitive. If you cannot distinguish, start plasmapheresis -- it is beneficial for both.

> **Clinical Pearl:** Do NOT wait for ANCA or anti-GBM results before performing biopsy if it can be done within 24-48 hours. The biopsy pattern (pauci-immune vs. immune complex vs. linear IgG) is as important as serology.

---

### 5.4 Post-Transplant Patient with Rising Cr + Proteinuria

**Entry Point:** Transplant recipient with rising creatinine AND/OR new/worsening proteinuria

`
Post-Transplant Dysfunction (Rising Cr +/- Proteinuria)
        |
        v
Step 1: Assess Urgency and Timing
- When was the last stable Cr?
- How fast is the rise? (Days = urgent; weeks = semi-urgent)
- When was the transplant? (Early = surgical/DGF; Late = rejection/infection/recurrence)
- What is the current immunosuppression?
- Any recent changes? (Dose reduction, non-adherence, drug interactions)
        |
        v
Step 2: Initial Workup (Same Day)
- CBC (leukopenia? thrombocytopenia?)
- CMP (Cr, BUN, electrolytes)
- UA with microscopy (hematuria? casts?)
- BK viral load (PCR, plasma)
- CMV viral load (PCR)
- CNI trough levels (tacrolimus/cyclosporine)
- DSA screen (if available urgently)
- Blood cultures (if febrile)
        |
        v
Step 3: Stratify by Clinical Features
        |
        +---> BK viral load >10,000 copies/mL
        |     --> Suspect `bkVirusNephropathy`
        |     --> Reduce immunosuppression; monitor BK load and DSA
        |     --> Biopsy if no improvement or DSA rising
        |
        +---> CNI trough elevated + isometric vacuolization on biopsy
        |     --> Suspect `cniToxicity`
        |     --> Reduce CNI dose; consider conversion to mTOR/belatacept
        |
        +---> DSA positive + C4d positive on biopsy
        |     --> Suspect `antibodyMediatedRejection`
        |     --> Plasmapheresis + IVIG + rituximab
        |
        +---> Rising Cr + no DSA + interstitial inflammation/tubulitis
        |     --> Suspect `tCellMediatedRejection`
        |     --> Pulse steroids; ATG if steroid-resistant
        |
        +---> Proteinuria + GBM duplication (double contours) on biopsy
        |     --> Suspect `transplantGlomerulopathy`
        |     --> Check DSA; treat chronic ABMR if present
        |
        +---> Proteinuria + disease-specific pattern matching native kidney
        |     --> Suspect recurrence of primary disease
        |     --> Treat based on original diagnosis
        |
        +---> Delayed graft function (days 0-7)
        |     --> Suspect ATN (surgical/vascular)
        |     --> Supportive; monitor for recovery
        |
        v
Step 4: Renal Biopsy (if indicated)
- Indications: Unexplained rising Cr, new proteinuria,
  suspected rejection, suspected recurrence
- Request: LM, IF, EM, C4d, SV40 stain (for BK),
  Banff classification
        |
        v
Step 5: Definitive Treatment
- Follow disease-specific guidelines (Sections 2-3)
- Monitor response with serial Cr, proteinuria, viral loads,
  DSA levels
- Adjust immunosuppression based on response and complications
`

> **Clinical Pearl:** In transplant patients, ALWAYS check BK viral load before biopsy. BK nephropathy is the most common cause of unexplained rising creatinine in the first year post-transplant, and treatment (reducing immunosuppression) is the opposite of what you would do for rejection.

> **Clinical Pearl:** Do not assume rising creatinine is "just rejection." The differential is broad: rejection (TCMR, ABMR), infection (BK, CMV), drug toxicity (CNI), recurrence of primary disease, surgical complications, and obstruction. Biopsy is often the only way to distinguish.

> **Clinical Pearl:** When reducing immunosuppression for BK virus, ALWAYS monitor DSA. Reducing immunosuppression can unmask subclinical ABMR.

---

### 5.5 Patient with Low Complement + Nephritis

**Entry Point:** Low C3 and/or C4 + glomerulonephritis (hematuria, proteinuria, declining GFR)

`
Low Complement + Nephritis
        |
        v
Step 1: Characterize the Complement Abnormality
- Low C3 with NORMAL C4 --> Alternative pathway activation
- Low C3 with LOW C4 --> Classical pathway activation
- Low C4 with NORMAL C3 --> Classical pathway activation (early/mild)
        |
        v
Step 2: Assess Clinical Context
- Age? (Young female = lupus; elderly = cryoglobulinemia)
- Systemic features? (Rash, arthritis, serositis = lupus)
- HCV risk factors? (IV drug use, tattoos, transfusions)
- Monoclonal gammopathy? (SPEP/UPEP)
- Preceding infection? (1-3 weeks = post-infectious GN)
- Family history of kidney disease? (Complement mutations)
        |
        v
Step 3: Serological Workup
- ANA, anti-dsDNA (lupus)
- HCV RNA (cryoglobulinemia)
- Cryoglobulins (cryoglobulinemia)
- SPEP, UPEP, free light chains (monoclonal gammopathy)
- C3 nephritic factor (C3 glomerulopathy)
- Complement pathway testing (factor H, factor I, factor B, MCP)
- ASO, anti-DNase B (post-infectious GN)
- Blood cultures (endocarditis)
        |
        v
Step 4: Stratify by Complement Pattern
        |
        +---> Low C3 + Low C4 + ANA/anti-dsDNA positive
        |     --> Suspect `lupus` nephritis
        |     --> Biopsy (ISN/RPS classification)
        |     --> MMF + glucocorticoids
        |
        +---> Low C4 + HCV positive + cryoglobulins positive
        |     --> Suspect `cryoglobulinemic` GN
        |     --> Treat HCV (DAAs); rituximab for severe vasculitis
        |
        +---> Low C3 + NORMAL C4 + C3 dominant IF
        |     --> Suspect `c3` glomerulopathy
        |     --> Biopsy; complement pathway testing
        |     --> Consider eculizumab in selected cases
        |
        +---> Low C3 + preceding infection + subepithelial humps
        |     --> Suspect `irgn` (post-infectious GN)
        |     --> Supportive; monitor for resolution
        |
        +---> Low C3 + ADAMTS13 >10% + no diarrhea + renal TMA
        |     --> Suspect aHUS (complement-mediated TMA)
        |     --> Eculizumab; vaccinate against Neisseria meningitidis
        |
        +---> Low C3 + endocarditis + renal biopsy
        |     --> Suspect endocarditis-associated GN
        |     --> Prolonged antibiotics; surgical intervention if needed
        |
        +---> Low C3/C4 + MPGN pattern + monoclonal protein
        |     --> Suspect monoclonal gammopathy-associated GN
        |     --> Hematology consult; treat underlying gammopathy
        |
        v
Step 5: Renal Biopsy (if indicated)
- Indications: Nephritis + low complements + unclear etiology
- Request: LM, IF, EM, C3, IgG, IgA, IgM, C1q, kappa, lambda
- Key findings: IF pattern (full-house vs. C3 dominant vs. IgA dominant),
  deposit location, GBM changes
        |
        v
Step 6: Initiate Treatment Based on Etiology
- Follow disease-specific guidelines (Sections 2-3)
- Monitor complement levels as marker of disease activity
- Repeat testing if initial workup is non-diagnostic
`

> **Clinical Pearl:** The pattern of complement consumption is the single most useful clue in the initial workup. Low C3 + normal C4 = alternative pathway (`c3` G, post-infectious). Low C3 + low C4 = classical pathway (`lupus`, `cryoglobulinemic`).

> **Clinical Pearl:** Always check SPEP/UPEP in patients with unexplained complement consumption. Monoclonal immunoglobulins can activate complement, causing MPGN or C3 glomerulopathy.

> **Clinical Pearl:** Complement levels should be drawn BEFORE initiating treatment. Immunosuppression may normalize levels and mask the underlying pathology.

---

## 6. Common Diagnostic Errors

This section catalogs the most frequent diagnostic mistakes in glomerular disease, with real-world examples, consequences, and prevention strategies. These errors represent patterns of cognitive bias, incomplete workup, and misinterpretation of data.

### 6.1 Error Table

| Error | Example | Consequence | Prevention Strategy |
|---|---|---|---|
| Diagnosing mcd in adults without biopsy | 45-year-old female with nephrotic syndrome started on steroids empirically; found to have sgs on delayed biopsy | Delayed appropriate treatment; missed opportunity for early intervention; worse renal outcome | ALWAYS biopsy adults with nephrotic syndrome; never diagnose mcd without histology in adults |
| Attributing all renal disease in diabetics to diabeticNephropathy | 55-year-old male with DM2 for 5 years, new nephrotic syndrome with hematuria, labeled as "diabetic nephropathy"; biopsy shows superimposed membranous | Missed treatable disease; unnecessary progression to ESRD | Biopsy diabetics with atypical features: hematuria, rapid progression, absence of retinopathy, short DM duration |
| Not checking anti-GBM in crescentic GN | 60-year-old male with AKI and crescentic GN on biopsy, ANCA sent but not anti-GBM; ANCA negative; final diagnosis: anti-GBM disease | Delayed plasmapheresis; irreversible renal damage | ALWAYS check ANCA AND anti-GBM simultaneously in crescentic GN; treat empirically while awaiting results |
| Treating BK virus as TCMR | Transplant patient with rising Cr, BK viral load 50,000 copies/mL; pulse steroids given for "rejection"; BK worsens | Worsening BK viremia; potential graft loss from BK nephropathy | ALWAYS check BK viral load BEFORE biopsy in transplant patients with rising Cr |
| Not distinguishing TCMR from ABMR | Transplant patient treated with pulse steroids for "rejection" when biopsy shows ABMR (C4d+, DSA+) | Inadequate treatment; progressive graft injury | Perform Banff classification on all transplant biopsies; check DSA and C4d |
| Misdiagnosing lupus as iga | 25-year-old female with hematuria, low complements, positive ANA, diagnosed with iga based on mesangial IgA on biopsy; full-house pattern missed | Delayed immunosuppression; renal progression | Always check ANA and complements in young females with hematuria; request full IF panel including C1q |
| Not checking HCV in MPGN | 50-year-old with MPGN pattern on biopsy, treated with immunosuppression without checking HCV; HCV was the cause | Unnecessary immunosuppression; missed viral infection; potential liver damage | ALWAYS check HCV RNA in MPGN; treat the underlying cause first |
| Delaying plasmapheresis for anti-GBM disease | 25-year-old with hemoptysis and AKI, anti-GBM positive, biopsy scheduled for next day; plasmapheresis delayed awaiting biopsy | Irreversible renal damage; potential death from pulmonary hemorrhage | Start plasmapheresis IMMEDIATELY when anti-GBM is positive; do not wait for biopsy |
| Missing amyloidosis | 65-year-old with nephrotic syndrome and "nodular glomerulosclerosis" labeled as diabetic nephropathy; Congo red not performed | Missed amyloidosis; missed underlying plasma cell disorder; incorrect treatment | ALWAYS perform Congo red on biopsy specimens with amorphous deposits; check SPEP in all patients >50 with nephrotic syndrome |
| Not classifying lupus nephritis | 30-year-old female with lupus nephritis treated with low-dose steroids without ISN/RPS classification; biopsy shows class IV | Inadequate induction therapy; renal progression | ALWAYS request ISN/RPS classification; class III/IV requires MMF + high-dose steroids |
| Ignoring hematuria in diabetics | 60-year-old with DM2 for 15 years, microscopic hematuria dismissed as "diabetic nephropathy"; biopsy shows superimposed iga | Missed IgAN; delayed treatment | Hematuria is uncommon in diabeticNephropathy; investigate if present |
| Not performing EM in suspected lport | 20-year-old male with hematuria, CKD, and family history of ESRD; diagnosed with "chronic GN" without EM | Missed lport; missed opportunity for genetic counseling and family screening | ALWAYS perform EM in young patients with unexplained CKD; check for GBM lamellation |
| Misdiagnosing TTP as HUS | Patient with TMA and renal failure, diagnosed as HUS; plasmapheresis not initiated; ADAMTS13 not checked | Death from TTP (80% mortality without treatment) | ALWAYS check ADAMTS13 in TMA; treat empirically for TTP while awaiting results |
| Over-immunosuppressing for BK virus | Patient with BK viremia given additional immunosuppression for "subclinical rejection" on protocol biopsy | Worsening BK viremia; graft loss | Distinguish BK nephropathy from TCMR on biopsy (SV40 stain); reduce immunosuppression for BK |
| Not checking complement levels in CKD | 40-year-old with CKD of unclear etiology, complement levels not checked; C3 glomerulopathy missed | Missed treatable disease; unnecessary progression | ALWAYS check C3 and C4 in any patient with unexplained CKD or GN |
| Performing biopsy in classic pediatric MCD | 4-year-old with classic nephrotic syndrome (abrupt onset, edema, heavy proteinuria, bland sediment) undergoes unnecessary biopsy | Unnecessary procedure; anesthesia risk; cost | In children <10 with classic presentation, empiric steroids are appropriate; biopsy if steroid-resistant |
| Not screening for malignancy in membranous | 65-year-old with new membranous nephropathy, no cancer screening performed; underlying lung cancer missed | Missed malignancy; inappropriate immunosuppression; worse cancer outcome | ALWAYS perform age-appropriate malignancy screening in patients >40 with new membranous nephropathy |
| Stopping immunosuppression too abruptly in transplant | Patient with BK viremia has all immunosuppression stopped; develops acute rejection | Graft loss from rejection | Gradual immunosuppression reduction for BK; monitor DSA and BK viral load concurrently |
| Not recognizing drug-induced GN | Patient on NSAIDs for chronic pain develops nephrotic syndrome; NSAIDs not discontinued; biopsy shows MCD | Persistent nephrotic syndrome; unnecessary immunosuppression | ALWAYS take a thorough drug history; discontinue offending agents before starting immunosuppression |
| Missing dual-positive anti-GBM + ANCA | Patient with ANCA-positive crescentic GN treated with rituximab only; anti-GBM not checked; anti-GBM also positive | Inadequate treatment; plasmapheresis not given; worse renal outcome | ALWAYS check both ANCA AND anti-GBM in crescentic GN; treat both if dual-positive |
| Not performing family screening in lport | 25-year-old male with lport diagnosed; family not screened; brother develops ESRD without prior monitoring | Missed opportunity for early ACEi treatment in family members | ALWAYS screen first-degree relatives in hereditary nephropathies; genetic counseling essential |
| Treating CNI toxicity as rejection | Transplant patient with elevated tacrolimus levels and rising Cr given pulse steroids; biopsy shows isometric vacuolization (CNI toxicity) | Worsened CNI toxicity; unnecessary immunosuppression | ALWAYS check CNI trough levels before biopsy; reduce CNI if levels are supratherapeutic |
| Not performing Oxford classification for IgAN | Patient with IgAN biopsy not classified by MEST-C; treatment not risk-stratified | Inappropriate treatment intensity; missed high-risk features | ALWAYS request Oxford (MEST-C) classification for IgAN biopsies; use for treatment decisions |
| Missing cryoglobulinemic GN | Patient with HCV and MPGN treated with immunosuppression without checking cryoglobulins or treating HCV | Unnecessary immunosuppression; missed cryoglobulinemia; liver damage | ALWAYS check HCV RNA and cryoglobulins in MPGN; treat HCV first |
| Not recognizing pregnancy-associated TMA | Pregnant patient with HELLP syndrome, TTP not considered; ADAMTS13 not checked; plasmapheresis delayed | Maternal and fetal death from TTP | ALWAYS check ADAMTS13 in TMA during pregnancy; differentiate HELLP from TTP from aHUS |
| Failing to repeat complement levels post-treatment | Patient with lupus nephritis treated; complement levels not repeated; disease flare not detected early | Delayed detection of flare; renal progression | Repeat complement levels and anti-dsDNA at every visit; trending is more valuable than single values |
| Not performing EM in C3 glomerulopathy | Patient with C3 dominant IF not evaluated with EM; DDD not distinguished from C3GN | Incorrect prognosis; inappropriate treatment | ALWAYS perform EM in C3 glomerulopathy; distinguish DDD (intramembranous deposits) from C3GN (subendothelial deposits) |

### 6.2 Cognitive Biases in Glomerular Disease Diagnosis

| Bias | Description | Example | Prevention |
|---|---|---|---|
| Anchoring | Fixating on the first diagnosis considered | First diagnosis of "diabetic nephropathy" in a diabetic patient with hematuria, missing superimposed IgAN | Systematically consider the full DDx; ask "What else could this be?" |
| Availability bias | Overweighting diagnoses recently encountered | Recently seeing a case of TTP leads to over-diagnosing TTP in all TMA cases | Use structured diagnostic frameworks; always check ADAMTS13 |
| Confirmation bias | Seeking information that confirms the suspected diagnosis | Only ordering tests that support the suspected diagnosis; ignoring contradictory results | Actively seek disconfirming evidence; check both ANCA and anti-GBM |
| Premature closure | Ending the diagnostic workup too early | Diagnosing "pre-renal AKI" without checking urine sediment | Complete the workup before committing to a diagnosis |
| Framing effect | Being influenced by how information is presented | ER labels patient as "AKI, likely pre-renal" leading to delayed nephrology consultation | Evaluate the patient independently; always check the sediment |
| Anchoring to demographics | Over-relying on age/sex/race for diagnosis | Assuming a young female with renal disease has lupus without checking ANA | Use demographics as one factor, not the sole factor |
| Attribution error | Attributing all findings to the most obvious diagnosis | Attributing all renal disease in a diabetic to diabetic nephropathy | Consider superimposed diseases; biopsy when atypical |

### 6.3 Systematic Prevention Strategies

| Strategy | Implementation | Impact |
|---|---|---|
| Mandatory checklists | Require C3, C4, ANCA, anti-GBM in all patients with AKI + active sediment | Reduces missed diagnoses by 40-60% |
| Dual testing protocol | Always send ANCA + anti-GBM together in crescentic GN | Eliminates missed dual-positive patients |
| BK screening protocol | Check BK viral load in ALL transplant patients with rising Cr before biopsy | Reduces inappropriate immunosuppression |
| Complement screening | Check C3 and C4 in ALL patients with unexplained CKD or GN | Identifies complement-mediated diseases early |
| HCV screening | Check HCV RNA in ALL patients with MPGN pattern on biopsy | Ensures viral-associated MPGN is treated correctly |
| Drug history protocol | Document complete drug history in ALL patients with new-onset GN | Identifies drug-induced GN early |
| EM mandate | Require EM on ALL renal biopsies for GN evaluation | Identifies ultrastructural findings critical for diagnosis |
| Classification mandate | Require disease-specific classification (ISN/RPS, Oxford, Banff) on ALL applicable biopsies | Ensures treatment is risk-stratified appropriately |
| Malignancy screening | Perform age-appropriate cancer screening in ALL patients >40 with new membranous nephropathy | Identifies paraneoplastic membranous early |
| Family screening | Screen first-degree relatives in ALL patients with hereditary nephropathies | Identifies at-risk family members early |

---

## Appendix A: Quick Reference - Disease ID Index

| Disease ID | Full Name | Primary Category |
|---|---|---|
| lport | Alport Syndrome | Hereditary Nephropathy |
| nca | ANCA-Associated Vasculitis | Pauci-Immune GN / Vasculitis |
| ntiGbm | Anti-GBM Disease (Goodpasture Syndrome) | Pauci-Immune GN / Autoimmune |
| ntibodyMediatedRejection | Antibody-Mediated Rejection | Transplant Pathology |
| kVirusNephropathy | BK Virus Nephropathy | Transplant Infection |
| c3 | C3 Glomerulopathy (C3GN and DDD) | Complement-Mediated GN |
| cniToxicity | Calcineurin Inhibitor Toxicity | Transplant Toxicity |
| cryoglobulinemic | Cryoglobulinemic Glomerulonephritis | Immune Complex GN / Vasculitis |
| denseDepositDisease | Dense Deposit Disease (DDD) | Complement-Mediated GN |
| diabeticNephropathy | Diabetic Nephropathy | Metabolic GN |
| drugInducedGn | Drug-Induced Glomerulonephritis | Secondary GN |
| ibrillaryGlomerulonephritis | Fibrillary Glomerulonephritis | Organized Deposit GN |
| sgs | Focal Segmental Glomerulosclerosis | Podocytopathy |
| hivan | HIV-Associated Nephropathy (HIVAN) | Infection-Associated GN |
| iga | IgA Nephropathy | Immune Complex GN |
| irgn | Infection-Related Glomerulonephritis | Immune Complex GN / Post-Infectious |
| lupus | Lupus Nephritis | Autoimmune GN / SLE |
| mcd | Minimal Change Disease | Podocytopathy |
| membranous | Membranous Nephropathy | Immune Complex GN |
| mpgn | Membranoproliferative Glomerulonephritis | Immune Complex GN / Pattern |
| 	CellMediatedRejection | T-Cell-Mediated Rejection | Transplant Pathology |
| 	hinBasementMembrane | Thin Basement Membrane Nephropathy | Hereditary Nephropathy |
| 	ransplantGlomerulopathy | Transplant Glomerulopathy | Transplant Pathology |

---

## Appendix B: Quick Reference - Complement Patterns

| Pattern | Likely Etiologies | Key Tests |
|---|---|---|
| Low C3 + Normal C4 | c3 glomerulopathy, post-infectious GN, aHUS, lupus (rare) | C3 nephritic factor, factor H/I, ADAMTS13, Shiga toxin |
| Low C3 + Low C4 | lupus nephritis, cryoglobulinemic GN, post-infectious GN (severe), endocarditis-associated GN | ANA, anti-dsDNA, HCV RNA, cryoglobulins, blood cultures |
| Low C4 + Normal C3 | cryoglobulinemic GN (early), monoclonal gammopathy-associated | HCV RNA, cryoglobulins, SPEP/UPEP |
| Normal C3 + Normal C4 | iga, 	hinBasementMembrane, lport, mcd, sgs, membranous, diabeticNephropathy | Disease-specific testing |
| Very low C3 + Very low C4 | Severe lupus nephritis, catastrophic antiphospholipid syndrome, severe cryoglobulinemic GN | ANA, anti-dsDNA, antiphospholipid antibodies, cryoglobulins |

---

## Appendix C: Quick Reference - Urgency Matrix

| Urgency Level | Time to Action | Conditions | Key Actions |
|---|---|---|---|
| EMERGENT (P0) | Hours | ntiGbm, TTP, severe lupus class IV, STEC-HUS, aHUS, cortical necrosis, catastrophic APS | Stat labs, emergent biopsy, immediate treatment; do not wait for all results |
| URGENT (P1) | 1-3 days | nca vasculitis, crescentic GN, active transplant rejection, TMA, acute transplant dysfunction | Urgent labs, biopsy within 48 hours, initiate empiric treatment |
| SEMI-URGENT (P2) | 3-7 days | Nephrotic syndrome with complications, AKI of unclear etiology, TMA (stable), new-onset GN | Scheduled biopsy, systematic workup, conservative management pending diagnosis |
| ROUTINE (P3) | 1-4 weeks | Isolated hematuria, sub-nephrotic proteinuria, CKD evaluation, stable transplant dysfunction | Outpatient workup, systematic evaluation, biopsy based on risk stratification |

---

## Appendix D: Quick Reference - Key Serological Tests

| Test | Diseases It Helps Diagnose | Diseases It Helps Exclude |
|---|---|---|
| ANCA (PR3 ELISA) | GPA, MPA, drug-induced ANCA vasculitis | Excludes ANCA vasculitis if negative (<95% sensitivity) |
| ANCA (MPO ELISA) | MPA, EGPA, drug-induced ANCA vasculitis | Excludes ANCA vasculitis if negative |
| Anti-GBM antibodies | Anti-GBM disease, dual-positive ANCA + anti-GBM | Excludes anti-GBM disease if negative |
| Anti-PLA2R antibodies | Primary membranous nephropathy (70-80%) | Lowers probability of primary membranous if negative |
| ANA | lupus nephritis, drug-induced lupus | Excludes lupus if negative (high NPV) |
| Anti-dsDNA | lupus nephritis (disease activity marker) | Strongly argues against lupus if negative |
| ADAMTS13 activity | TTP (<10%) | Excludes TTP if >50% |
| HCV RNA | cryoglobulinemic GN, HCV-associated MPGN/membranous | Excludes HCV as cause if negative |
| SPEP/UPEP/free light chains | Cast nephropathy, monoclonal gammopathy-associated GN, myloid, ibrillaryGlomerulonephritis | Excludes monoclonal gammopathy if negative |
| C3, C4 | lupus, cryoglobulinemic, c3, irgn, aHUS | Normal complements make these less likely |
| C3 nephritic factor | c3 glomerulopathy (DDD and C3GN) | Absence makes alternative pathway dysregulation less likely |
| ASO / anti-DNase B | irgn (post-streptococcal GN) | Negative results make post-streptococcal GN less likely |
| BK viral load (PCR) | kVirusNephropathy in transplant | Excludes BK as cause of dysfunction if negative |
| Cryoglobulins | cryoglobulinemic GN | Negative results (with proper handling) argue against cryoglobulinemia |

---

## Appendix E: Glossary of Abbreviations

| Abbreviation | Full Term |
|---|---|
| ABMR | Antibody-Mediated Rejection |
| ADAMTS13 | A Disintegrin And Metalloproteinase with Thrombospondin Type 1 Motif 13 |
| AKI | Acute Kidney Injury |
| ANCA | Anti-Neutrophil Cytoplasmic Antibody |
| anti-GBM | Anti-Glomerular Basement Membrane |
| aHUS | Atypical Hemolytic Uremic Syndrome |
| APOL1 | Apolipoprotein L1 |
| ASO | Anti-Streptolysin O |
| BVAS | Birmingham Vasculitis Activity Score |
| C3 | Complement Component 3 |
| C4 | Complement Component 4 |
| CKD | Chronic Kidney Disease |
| CNI | Calcineurin Inhibitor |
| DAH | Diffuse Alveolar Hemorrhage |
| DAA | Direct-Acting Antiviral |
| DDD | Dense Deposit Disease |
| DM | Diabetes Mellitus |
| DSA | Donor-Specific Antibody |
| EM | Electron Microscopy |
| ESRD | End-Stage Renal Disease |
| EGPA | Eosinophilic Granulomatosis with Polyangiitis |
| FPE | Foot Process Effacement |
| FSGS | Focal Segmental Glomerulosclerosis |
| GBM | Glomerular Basement Membrane |
| GN | Glomerulonephritis |
| GPA | Granulomatosis with Polyangiitis |
| HSP | Henoch-Schonlein Purpura (IgA Vasculitis) |
| IF | Immunofluorescence |
| LM | Light Microscopy |
| MCD | Minimal Change Disease |
| MPA | Microscopic Polyangiitis |
| MPGN | Membranoproliferative Glomerulonephritis |
| RPGN | Rapidly Progressive Glomerulonephritis |
| SPEP | Serum Protein Electrophoresis |
| TBMN | Thin Basement Membrane Nephropathy |
| TCMR | T-Cell-Mediated Rejection |
| TMA | Thrombotic Microangiopathy |
| TTP | Thrombotic Thrombocytopenic Purpura |
| TIN | Tubulointerstitial Nephritis |
| UPC | Urine Protein-to-Creatinine Ratio |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*

---

## 7. Expanded Disease Overlap Matrix

This matrix provides a comprehensive cross-reference of all 23 diseases and their most important overlap syndromes, helping the clinician recognize when two or more conditions may coexist.

### 7.1 Primary Disease Overlap Matrix

| Primary Disease | Most Common Overlaps | Key Distinguishing Feature | Clinical Pearl |
|---|---|---|---|
| lport | 	hinBasementMembrane (carriers), anti-GBM (post-transplant), iga (coincidental) | GBM lamellation on EM; genetic testing definitive | 3-5% of lport patients develop anti-GBM post-transplant; monitor closely |
| nca | ntiGbm (10-30% dual-positive), lupus (rare overlap), irgn (post-staphylococcal trigger), drug-induced (levamisole-cocaine) | Pauci-immune pattern on biopsy; ANCA specificity (PR3 vs MPO) | Always check anti-GBM in ANCA-positive patients; 10-30% are dual-positive |
| ntiGbm | nca (10-30% dual-positive), lport (post-transplant anti-GBM) | Linear IgG on IF; anti-GBM antibodies positive | Dual-positive patients need both plasmapheresis (anti-GBM) AND rituximab (ANCA) |
| ntibodyMediatedRejection | 	CellMediatedRejection (mixed rejection), 	ransplantGlomerulopathy (chronic), kVirusNephropathy (reduction in IS unmasks ABMR) | DSA positive; C4d positive; microvascular inflammation | Reducing immunosuppression for BK can unmask subclinical ABMR |
| kVirusNephropathy | 	CellMediatedRejection (coexistence), ntibodyMediatedRejection (unmasked by IS reduction), cniToxicity (over-immunosuppression) | BK viral load >10,000 copies/mL; SV40 positive on biopsy | Monitor both BK viral load AND DSA during treatment |
| c3 | irgn (post-infectious trigger), lupus (complement consumption), cryoglobulinemic (overlap), monoclonal gammopathy (trigger) | C3 dominant IF; low C3 with normal C4; complement pathway testing | Always check SPEP/UPEP; monoclonal gammopathy can trigger C3G |
| cniToxicity | 	CellMediatedRejection (coexistence), ABMR (unmasked), kVirusNephropathy (over-immunosuppression) | Isometric vacuolization on biopsy; elevated CNI trough levels | Check CNI levels before biopsy; reduce if supratherapeutic |
| cryoglobulinemic | lupus (low complements, MPGN), mpgn (histological pattern), nca (rare overlap), membranous (HCV-associated) | Cryoglobulins positive; low C4; HCV positive (80%) | Treat HCV first; avoid immunosuppression without HCV treatment |
| denseDepositDisease | c3 (same umbrella), irgn (post-infectious trigger), monoclonal gammopathy (trigger), partial lipodystrophy (associated) | Intramembranous dense deposits on EM (pathognomonic) | Acquired partial lipodystrophy is strongly associated with DDD |
| diabeticNephropathy | membranous (superimposed 15%), sgs (superimposed), iga (superimposed), amyloid (nodular pattern mimic) | Kimmelstiel-Wilson nodules; retinopathy; linear IgG on IF | Biopsy diabetics with atypical features; superimposed disease is common |
| drugInducedGn | membranous (gold/penicillamine), nca (levamisole-cocaine), lupus (hydralazine), MCD (NSAIDs) | Temporal relationship with drug; improvement after drug withdrawal | ALWAYS take thorough drug history; discontinue before immunosuppression |
| ibrillaryGlomerulonephritis | Amyloidosis (EM mimic), monoclonal gammopathy (30%), membranous (subepithelial deposits), hepatitis C | Fibrils 12-22 nm on EM; Congo red negative | Always perform Congo red to distinguish from amyloidosis |
| sgs | mcd (overlap spectrum), iga (coincidental), diabeticNephropathy (superimposed), obesity-related, APOL1-associated | Segmental sclerosis on biopsy; FPE on EM | Classify FSGS variant; screen for secondary causes before immunosuppression |
| hivan | sgs (HIVAN is collapsing FSGS), lupus (false-positive ANA), iga (HIV-triggered), membranous (HIV-associated) | HIV positive; collapsing FSGS + microcystic dilation; SV40 negative | Start ART immediately; this is the primary treatment |
| iga | 	hinBasementMembrane (coincidental), lupus (mesangial IgA), iga vasculitis (systemic form), liver disease (aberrant IgA) | Mesangial IgA on IF; synpharyngitic hematuria | IgAN is the most common GN worldwide; always request Oxford classification |
| irgn | c3 (persistent complement activation), nca (post-staphylococcal trigger), cryoglobulinemic (HCV-associated) | Preceding infection; subepithelial humps on EM; low C3 (resolves) | If C3 does not normalize in 6-8 weeks, reconsider diagnosis |
| lupus | membranous (class V), c3 (complement consumption), cryoglobulinemic (overlap), TMA (lupus-associated), nca (rare overlap) | Full-house IF; ANA/anti-dsDNA positive; low C3 AND C4 | Always request ISN/RPS classification; class dictates treatment |
| mcd | sgs (overlap spectrum), iga (coincidental), atopy (associated), drug-induced (NSAIDs, lithium) | Normal glomeruli on LM; FPE only on EM | In adults, always biopsy before diagnosing MCD |
| membranous | lupus class V, HCV-associated, malignancy-associated, drug-induced, sgs (superimposed) | Anti-PLA2R positive (70-80%); subepithelial deposits | Screen for malignancy in all patients >40 with membranous |
| mpgn | cryoglobulinemic (most common cause of MPGN), lupus, c3, monoclonal gammopathy, HCV/HBV | MPGN pattern on LM; subendothelial deposits on EM | MPGN is a histological pattern, not a disease; always find the cause |
| 	CellMediatedRejection | ntibodyMediatedRejection (mixed), kVirusNephropathy (coexistence), cniToxicity (coexistence) | Interstitial inflammation + tubulitis on biopsy; no DSA; no C4d | Banff classification is essential; grade affects treatment |
| 	hinBasementMembrane | lport (carriers), iga (coincidental), sgs (early) | Thin GBM (<275 nm) on EM; benign course | Genetic testing (COL4A3/A4) distinguishes from lport carrier status |
| 	ransplantGlomerulopathy | Chronic ABMR (most common cause), recurrent IgAN, cniToxicity (coexistence) | GBM duplication (double contours) on silver stain; may have DSA | Check DSA; review original native kidney biopsy for recurrence |

### 7.2 Systemic Disease Renal Overlap Syndromes

| Systemic Disease | Renal Manifestations | Key Diagnostic Clues | Overlap Considerations |
|---|---|---|---|
| Systemic Lupus Erythematosus | Lupus nephritis (classes I-VI); TMA; renovascular disease | Full-house IF; ANA/anti-dsDNA; low C3/C4 | May overlap with membranous (class V), cryoglobulinemic, nca (pauci-immune areas) |
| Hepatitis C | cryoglobulinemic GN; membranous; MPGN; GN with IgA deposits | HCV RNA positive; cryoglobulins; low C4 | HCV is the most common cause of MPGN in Western countries |
| Diabetes Mellitus | diabeticNephropathy; superimposed membranous/sgs/iga | Kimmelstiel-Wilson nodules; retinopathy; linear IgG | Superimposed glomerular disease occurs in 15-30% of diabetics with nephrotic syndrome |
| HIV | HIVAN (collapsing FSGS); membranous; iga; MPGN; TMA | HIV positive; collapsing FSGS + microcystic dilation | APOL1 high-risk genotypes dramatically increase HIVAN risk |
| Monoclonal Gammopathy | mpgn; c3 G; myloid; cast nephropathy; fibrillary GN; immunotactoid GN | SPEP/UPEP positive; free light chain restriction | Monoclonal immunoglobulin can activate complement, form fibrils, or deposit directly |
| Antiphospholipid Syndrome | TMA; renovascular disease; cortical necrosis; AKI | Antiphospholipid antibodies; thrombocytopenia; livedo reticularis | Catastrophic APS can cause multi-organ TMA including kidneys |
| Scleroderma | Scleroderma renal crisis; TMA; GN | Severe HTN; skin changes; anti-RNA polymerase III | Scleroderma renal crisis requires immediate ACEi; avoid CNI |
| IgA Vasculitis (HSP) | IgA nephropathy on renal biopsy; abdominal vasculitis; arthralgia | Palpable purpura (lower extremities); IgA deposits on skin/renal biopsy | Same pathogenesis as IgAN; HSP is the systemic form |

---

## 8. Age-Specific Differential Diagnosis Guides

### 8.1 Pediatric (0-18 years)

| Age Group | Most Likely Diagnoses | Key Distinguishing Features | Biopsy Indications |
|---|---|---|---|
| 0-2 years | Congenital nephrotic syndrome (NPHS1/Finnish type); sgs (genetic); mcd; Denys-Drash syndrome; WAGR syndrome | Family history; genetic testing; response to steroids; associated anomalies | Genetic testing preferred; biopsy if atypical or steroid-resistant |
| 2-10 years | mcd (most common, 80%); post-infectious GN; iga (rare in this age); Henoch-Schonlein purpura | Abrupt onset; classic nephrotic syndrome; bland sediment; dramatic steroid response | Empiric steroids for classic MCD; biopsy if steroid-resistant or atypical |
| 10-18 years | iga (emerging); sgs; post-infectious GN; lupus (early onset); 	hinBasementMembrane | Episodic hematuria with URIs (IgAN); family history (hereditary); female sex (lupus) | Biopsy if proteinuria >0.5 g/day, declining GFR, or atypical features |

### 8.2 Young Adults (18-40 years)

| Likely Diagnoses | Key Distinguishing Features | Priority Workup |
|---|---|---|
| iga (most common GN worldwide) | Episodic gross hematuria with URIs; M>F; East Asian | UA, UPC, C3/C4, IgA level, renal biopsy |
| 	hinBasementMembrane | Persistent hematuria; normal GFR; family history; thin GBM on EM | UA, UPC, genetic testing (COL4A3/A4) |
| lport | Family history of ESRD + deafness; progressive CKD; abnormal GBM | Genetic testing (COL4A3/A4/A5), audiology, ophthalmology |
| lupus nephritis | Young female; multi-system; ANA/anti-dsDNA positive; low complements | ANA, anti-dsDNA, complement levels, renal biopsy |
| sgs | African American > Caucasian; nephrotic or sub-nephrotic; hematuria | UA, UPC, APOL1 genotyping, renal biopsy |
| mcd | Relapsing nephrotic syndrome; dramatic steroid response | Biopsy (adults); empiric steroids (children) |
| Post-infectious GN | Preceding infection; acute nephritis; low C3; self-limiting | ASO, C3/C4, renal biopsy if atypical |
| membranous | Age 30-40 (early onset); anti-PLA2R positive; nephrotic | Anti-PLA2R, complement levels, renal biopsy |

### 8.3 Middle-Aged Adults (40-65 years)

| Likely Diagnoses | Key Distinguishing Features | Priority Workup |
|---|---|---|
| membranous (most common in this age) | Nephrotic syndrome; anti-PLA2R positive; M>F; thrombotic risk | Anti-PLA2R, anti-THSD7A, malignancy screening, renal biopsy |
| diabeticNephropathy | Known DM; retinopathy; gradual proteinuria; Kimmelstiel-Wilson nodules | HbA1c, UA, UPC, fundoscopic exam |
| sgs | African American; APOL1 high-risk; hypertension; hematuria | UA, UPC, APOL1 genotyping, renal biopsy |
| iga | Young adult onset persisting; progressive CKD; mesangial IgA | Review prior biopsies; UA, UPC, C3/C4, IgA level |
| Amyloidosis | Age >50; chronic inflammation; monoclonal gammopathy; massive proteinuria | SPEP, UPEP, Congo red, fat pad biopsy |
| ibrillaryGlomerulonephritis | Age 50-60; fibrillary deposits on EM; Congo red negative; smoking | SPEP, UPEP, renal biopsy with EM |
| c3 glomerulopathy | Low C3 with normal C4; C3 dominant IF; chronic course | C3 nephritic factor, complement pathway testing, renal biopsy |
| Monoclonal gammopathy-associated GN | SPEP/UPEP positive; MPGN or C3G pattern; complement consumption | SPEP, UPEP, free light chains, renal biopsy |

### 8.4 Elderly Adults (>65 years)

| Likely Diagnoses | Key Distinguishing Features | Priority Workup |
|---|---|---|
| nca vasculitis (GPA/MPA) | >50; AKI + active sediment; sinusitis/pulmonary hemorrhage; ANCA positive | ANCA (PR3/MPO), anti-GBM, C3/C4, CT chest/sinuses, renal biopsy |
| ntiGbm disease | Second peak age 50-70; acute nephritis +/- hemoptysis; linear IgG | Anti-GBM, ANCA, chest X-ray/CT, renal biopsy |
| membranous | Age 40-60 (can extend older); anti-PLA2R positive; nephrotic | Anti-PLA2R, malignancy screening, renal biopsy |
| Cast nephropathy (myeloma kidney) | Age >50; SPEP positive; Bence Jones proteinuria; renal insufficiency | SPEP, UPEP, free light chains, bone marrow biopsy |
| Amyloidosis | Chronic inflammation or monoclonal gammopathy; massive proteinuria | SPEP, UPEP, Congo red, fat pad biopsy |
| diabeticNephropathy | Known DM; long-standing; retinopathy; gradual decline | HbA1c, UA, UPC, fundoscopic exam |
| Hypertensive nephrosclerosis | Long-standing HTN; bilateral small kidneys; bland sediment | UA, UPC, renal ultrasound |
| Renovascular disease | Resistant HTN; flash pulmonary edema; asymmetrical kidneys | Renal Doppler, CTA/MRA |

---

## 9. Race/Ethnicity-Specific Considerations

### 9.1 African American Patients

| Condition | Increased Risk | Key Considerations | Diagnostic Approach |
|---|---|---|---|
| sgs (especially collapsing variant) | 2-3x increased risk | APOL1 high-risk genotypes (G1/G2); HIV co-infection dramatically increases risk | APOL1 genotyping; HIV testing; biopsy to classify variant |
| lupus nephritis | More severe disease; faster progression to ESRD | Higher likelihood of class IV/V; worse response to standard therapy | Early biopsy; aggressive immunosuppression; consider rituximab |
| hivan | Increased risk with APOL1 high-risk genotypes | APOL1 G1/G2 homozygosity increases risk 10-20x in HIV+ patients | HIV testing; ART initiation; APOL1 genotyping |
| diabeticNephropathy | Higher risk of progression to ESRD | APOL1 risk alleles may contribute; worse glycemic control often | Aggressive glycemic/BP control; SGLT2i; early nephrology referral |
| Hypertensive nephrosclerosis | More common; earlier onset; more severe | Often misattributed when underlying GN is present | Always biopsy if hematuria or active sediment is present |

### 9.2 East Asian Patients

| Condition | Increased Risk | Key Considerations | Diagnostic Approach |
|---|---|---|---|
| iga | Highest prevalence worldwide (50% of GN in some series) | More aggressive course; higher risk of progression to ESRD | Early biopsy; Oxford classification; SGLT2i + RAAS blockade |
| membranous | Second most common GN after IgAN | Anti-PLA2R positive in similar proportion to Caucasians | Anti-PLA2R; malignancy screening; rituximab |
| lupus nephritis | High prevalence in Southeast Asia | More mesangial/endothelial involvement | ANA, anti-dsDNA, complement levels, renal biopsy |
| c3 glomerulopathy | Higher prevalence than in Western countries | More DDD than C3GN | C3 nephritic factor, complement pathway testing, renal biopsy |

### 9.3 Hispanic/Latino Patients

| Condition | Increased Risk | Key Considerations | Diagnostic Approach |
|---|---|---|---|
| lupus nephritis | Higher prevalence and severity than Caucasians | More aggressive course; higher risk of class IV/V | Early biopsy; aggressive immunosuppression |
| iga | Moderate prevalence (lower than East Asian, higher than Caucasian) | Similar course to other populations | Standard workup; Oxford classification |
| diabeticNephropathy | Higher prevalence due to DM2 epidemic | Metabolic syndrome common; APOL1 risk alleles may contribute | Aggressive glycemic/BP control; SGLT2i |
| membranous | Moderate prevalence | HCV co-infection more common | Anti-PLA2R; HCV RNA; malignancy screening |

---

## 10. Temporal Patterns in Glomerular Disease

### 10.1 Acute Presentations (<1 week)

| Timeframe | Likely Diagnoses | Key Features | Urgency |
|---|---|---|---|
| Hours | ntiGbm disease, TTP, STEC-HUS, cortical necrosis, acute transplant rejection | Abrupt onset; severe AKI; systemic symptoms; active sediment | EMERGENT |
| 1-3 days | nca vasculitis (severe), lupus nephritis (severe flare), TMA (aHUS), acute transplant rejection | Rapidly rising Cr; active sediment; systemic features | URGENT |
| 3-7 days | irgn (post-infectious), iga (macroscopic hematuria episode), drug-induced GN, acute TIN | Acute onset; temporal relationship with trigger | URGENT to SEMI-URGENT |

### 10.2 Subacute Presentations (1-12 weeks)

| Timeframe | Likely Diagnoses | Key Features | Urgency |
|---|---|---|---|
| 1-4 weeks | nca vasculitis, crescentic GN, lupus nephritis flare, iga (progressive), membranous (new onset) | Gradually rising Cr; developing sediment; proteinuria | SEMI-URGENT |
| 1-3 months | iga (chronic), sgs (new onset), membranous (insidious), c3 glomerulopathy, ibrillaryGlomerulonephritis | Persistent proteinuria/hematuria; gradual GFR decline | SEMI-URGENT to ROUTINE |

### 10.3 Chronic Presentations (>3 months)

| Timeframe | Likely Diagnoses | Key Features | Urgency |
|---|---|---|---|
| 3-12 months | diabeticNephropathy, chronic iga, chronic sgs, lport, hypertensive nephrosclerosis, CKD of unclear etiology | Established CKD; bilateral small kidneys; proteinuria | ROUTINE |
| >1 year | End-stage any GN, chronic transplant injury, 	ransplantGlomerulopathy, chronic TIN, renovascular disease | ESRD; irreversible damage; treatment focus shifts to renal replacement therapy | ROUTINE |

---

## 11. Treatment Response as Diagnostic Clue

Treatment response can serve as a diagnostic tool when the initial workup is inconclusive.

| Treatment | Expected Response | Diagnosis Supported | Diagnosis Argued Against |
|---|---|---|---|
| Glucocorticoids (prednisone 1 mg/kg/day) | Complete remission in 2-4 weeks | mcd (90% respond) | sgs (30-50% respond), membranous (20-30% respond), iga (variable) |
| Rituximab | Reduction in proteinuria; DSA reduction | membranous (anti-PLA2R reduction), nca (B-cell depletion), ABMR | mcd (poor response), iga (limited response) |
| Plasmapheresis | Rapid improvement in 5-10 sessions | ntiGbm disease, TTP, cryoglobulinemic vasculitis, recurrent FSGS post-transplant | nca (limited benefit except severe), lupus (limited evidence) |
| ACEi/ARB | Proteinuria reduction 30-50%; slowed GFR decline | iga, membranous, diabeticNephropathy, sgs (supportive) | Not diagnostic but essential supportive care for all proteinuric GN |
| SGLT2i | Proteinuria reduction 30%; slowed GFR decline | iga, membranous, diabeticNephropathy, sgs (supportive) | Not diagnostic but emerging standard of care for proteinuric GN |
| Eculizumab | Resolution of TMA; stabilization of renal function | aHUS (complement-mediated TMA) | TTP (no role for eculizumab), STEC-HUS (no role) |
| HCV treatment (DAAs) | Resolution of cryoglobulinemia; improvement in proteinuria | HCV-associated cryoglobulinemic GN, HCV-associated MPGN/membranous | If no improvement after HCV clearance, consider other causes |
| Antiretroviral therapy | Improvement in proteinuria; stabilization of GFR | HIVAN (hivan) | If no improvement, consider superimposed disease or non-HIVAN causes |

> **Clinical Pearl:** Treatment response is a powerful diagnostic tool. A patient with nephrotic syndrome who achieves complete remission with prednisone likely has mcd. A partial response suggests sgs or membranous. No response should prompt re-evaluation of the diagnosis.

> **Clinical Pearl:** Anti-PLA2R levels can be used to monitor treatment response in primary membranous nephropathy. A decline in anti-PLA2R titer predicts remission and can guide treatment duration.

---

## 12. Special Populations

### 12.1 Pregnant Patients

| Condition | Key Considerations | Treatment Constraints |
|---|---|---|
| Pre-eclampsia | Most common cause of AKI in pregnancy; diagnosis of exclusion in known renal disease | Delivery is definitive treatment; magnesium sulfate; avoid RAAS blockade |
| lupus nephritis flare | May mimic or coexist with pre-eclampsia; low complements + rising anti-dsDNA favor flare | Steroids (prednisone); azathioprine (safe in pregnancy); avoid MMF/cyclophosphamide |
| TMA in pregnancy | Must distinguish HELLP from TTP from aHUS | TTP: plasmapheresis + caplacizumab; aHUS: eculizumab; HELLP: delivery |
| iga (exacerbation) | Worsening proteinuria/hematuria during pregnancy | RAAS blockade contraindicated; methyldopa/labetalol; close monitoring |

### 12.2 Transplant Recipients

| Condition | Key Considerations | Diagnostic Approach |
|---|---|---|
| Acute rejection (TCMR/ABMR) | Most common cause of early graft dysfunction | Biopsy with Banff classification; DSA; C4d |
| BK virus nephropathy | Most common cause of unexplained rising Cr in first year | BK viral load; reduce immunosuppression; monitor DSA |
| Recurrence of primary disease | Varies by disease (FSGS: 20-40%; IgAN: 30-50%; MPGN/C3G: variable) | Review original biopsy; compare with allograft biopsy |
| CNI toxicity | Dose-dependent; drug interactions common | CNI trough levels; biopsy (isometric vacuolization) |
| Post-transplant anti-GBM | 3-5% of lport patients; usually subclinical | Monitor anti-GBM antibodies; most do not develop clinical disease |

### 12.3 Patients with Monoclonal Gammopathy

| Condition | Key Considerations | Diagnostic Approach |
|---|---|---|
| Cast nephropathy (myeloma kidney) | Most common renal manifestation of myeloma | SPEP, UPEP, free light chains, bone marrow biopsy |
| myloid (AL type) | 75% have monoclonal gammopathy | SPEP, UPEP, fat pad biopsy, Congo red, mass spectrometry |
| mpgn (monoclonal-associated) | Monoclonal immunoglobulin activates complement | SPEP, UPEP, complement testing, renal biopsy |
| c3 glomerulopathy (monoclonal-triggered) | Monoclonal immunoglobulin activates alternative complement pathway | SPEP, UPEP, C3 nephritic factor, complement pathway testing |
| ibrillaryGlomerulonephritis | 30% have monoclonal gammopathy | SPEP, UPEP, renal biopsy with EM |
| Immunotactoid GN | 50% have monoclonal gammopathy | SPEP, UPEP, renal biopsy with EM (microtubular deposits >30 nm) |
| Light chain deposition disease | Monoclonal light chain deposits in GBM/tubular basement membrane | SPEP, UPEP, free light chains, renal biopsy (kappa/lambda restriction on IF) |

---

## 13. Monitoring Framework

### 13.1 Disease-Specific Monitoring Protocols

| Disease | Initial Monitoring | Maintenance Monitoring | Red Flags |
|---|---|---|---|
| iga | Monthly UPC, Cr, BP for first 6 months | Quarterly UPC, Cr, BP; annual renal ultrasound | UPC rising >1 g/day; Cr rising >20%; new HTN |
| membranous | Monthly anti-PLA2R, UPC, Cr for first year | Quarterly anti-PLA2R, UPC, Cr; annual malignancy screening | Anti-PLA2R rising; UPC rising >4 g/day; Cr declining |
| lupus nephritis | Monthly ANA, anti-dsDNA, C3, C4, UPC, Cr during induction | Quarterly serologies and renal function; annual renal biopsy if high-risk | Low complements, rising anti-dsDNA, rising UPC, declining Cr |
| sgs | Monthly UPC, Cr, BP during treatment | Quarterly UPC, Cr, BP | UPC rising >3.5 g/day; Cr declining; new HTN |
| nca vasculitis | Monthly ANCA, C3, C4, Cr, UPC during induction | Quarterly ANCA, Cr, UPC; annual CT chest | Rising ANCA titer; declining Cr; new hematuria |
| ntiGbm | Weekly anti-GBM, Cr during treatment | Monthly anti-GBM, Cr for first year | Rising anti-GBM; declining Cr; new hematuria |
| c3 glomerulopathy | Monthly C3, Cr, UPC during treatment | Quarterly C3, Cr, UPC | Low C3 persisting; Cr declining; UPC rising |
| diabeticNephropathy | Quarterly HbA1c, Cr, UPC; annual fundoscopy | Quarterly HbA1c, Cr, UPC; annual fundoscopy | UPC rising >1 g/day; Cr declining >5 mL/min/year; new HTN |
| kVirusNephropathy | Weekly BK viral load during treatment | Monthly BK viral load; quarterly DSA | BK rising despite IS reduction; DSA rising |
| Transplant (all) | Monthly Cr, CNI levels, BK viral load, DSA | Quarterly Cr, CNI levels, BK viral load, DSA; annual protocol biopsy | Rising Cr; rising DSA; rising BK; new proteinuria |

### 13.2 When to Repeat Biopsy

| Indication | Timing | Rationale |
|---|---|---|
| Inadequate initial biopsy | As soon as possible | Insufficient tissue for diagnosis |
| Treatment failure | After 3-6 months of appropriate therapy | May have misclassified disease or superimposed process |
| Disease relapse | During flare | May show evolution (e.g., MCD to FSGS) |
| New clinical features | As indicated | Hematuria, rising Cr, new proteinuria may indicate new process |
| Post-transplant dysfunction | As indicated | Distinguish rejection, infection, recurrence, toxicity |
| Monitoring disease activity | Protocol biopsies (research/selected cases) | Detect subclinical rejection or disease progression |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*

---

## 14. Comprehensive Diagnostic Workup Protocols

### 14.1 First Visit Workup (New Nephrology Referral)

Every new nephrology referral for suspected glomerular disease should include the following baseline workup:

**Tier 1: Universal Screening (ALL patients)**

| Test | Rationale | Expected Findings |
|---|---|---|
| Urinalysis with microscopy | Identify hematuria, proteinuria, casts, crystals | Dysmorphic RBCs (glomerular); isomorphic RBCs (urological); RBC casts (glomerular); WBC casts (TIN); muddy brown casts (ATN) |
| Spot urine protein-to-creatinine ratio (UPC) | Quantify proteinuria | Normal <0.5 g/g; sub-nephrotic 0.5-3.5 g/g; nephrotic >3.5 g/g |
| Serum creatinine + eGFR | Assess renal function | Acute vs. chronic; severity of impairment |
| Complete metabolic panel | Electrolytes, albumin, calcium, phosphate, liver function | Hypoalbuminemia (nephrotic); hyperkalemia (CKD); hyperphosphatemia (CKD) |
| Complete blood count | Anemia, thrombocytopenia, leukocytosis | Anemia (CKD, hemolysis); thrombocytopenia (TMA, lupus, HITS) |
| C3 and C4 complement | Complement consumption | Low C3/C4 (lupus, cryoglobulinemia, post-infectious, C3G, aHUS) |
| Serum albumin | Nutritional/inflammatory status; nephrotic syndrome | Hypoalbuminemia (<3.0 g/dL) in nephrotic syndrome |

**Tier 2: Disease-Specific Screening (Based on clinical suspicion)**

| Clinical Scenario | Additional Tests | Rationale |
|---|---|---|
| Crescentic GN / AKI with active sediment | ANCA (PR3 + MPO ELISA), Anti-GBM antibodies, SPEP | Distinguish pauci-immune, anti-GBM, and immune complex GN; exclude myeloma |
| Nephrotic syndrome | Anti-PLA2R, anti-THSD7A, hepatitis B/C, HIV, SPEP/UPEP/free light chains | Identify primary vs. secondary membranous; exclude viral/gammopathy-associated GN |
| Young adult with hematuria | IgA level, C3/C4, hepatitis B/C | IgAN workup; exclude post-infectious GN |
| Family history of ESRD/hearing loss | Genetic testing (COL4A3/A4/A5), audiology, ophthalmology | Hereditary nephropathy workup |
| Female with multi-system disease | ANA, anti-dsDNA, antiphospholipid antibodies, CBC | Lupus nephritis workup |
| Post-transplant dysfunction | BK viral load, CMV viral load, DSA screen, CNI trough levels | Distinguish rejection, infection, toxicity |
| TMA | ADAMTS13, Shiga toxin, complement testing (CH50, AH50, factor H, factor I) | Distinguish TTP, STEC-HUS, aHUS |
| Low complement | SPEP/UPEP, cryoglobulins, hepatitis B/C, ANA, anti-dsDNA | Identify cause of complement consumption |
| Age >50 with GN | SPEP/UPEP/free light chains, Congo red on biopsy | Exclude monoclonal gammopathy and amyloidosis |
| Drug exposure history | Drug-specific serologies, temporal correlation assessment | Drug-induced GN workup |

**Tier 3: Biopsy Planning**

| Indication for Biopsy | Timing | Preparation |
|---|---|---|
| Nephrotic syndrome in adults | Within 2-4 weeks | Confirm proteinuria; assess coagulation; ultrasound |
| AKI with active sediment | Within 24-48 hours (emergent) | Cross-match; correct coagulopathy; nephrology + pathology coordination |
| Suspected crescentic GN | Within 24-48 hours (emergent) | Start empiric treatment if severe; do not delay treatment for biopsy |
| New transplant dysfunction | Within 48-72 hours | Check BK viral load FIRST; DSA screen; coordinate with transplant team |
| CKD with unclear etiology | Within 2-4 weeks | Ensure adequate kidney size for biopsy (>8 cm); correct coagulopathy |
| Isolated hematuria (low risk) | May defer; monitor first | Risk stratify; biopsy if UPC >0.5 or GFR declining |
| Post-treatment evaluation | 3-6 months after treatment initiation | Assess response; distinguish residual from active disease |

### 14.2 Biopsy Interpretation Framework

When reviewing a renal biopsy, the nephrologist should systematically evaluate:

**Light Microscopy (LM):**

| Finding | Significance | DDx Narrowing |
|---|---|---|
| Normal glomeruli | MCD, early disease, TBMN | Consider mcd, 	hinBasementMembrane, early iga |
| Mesangial hypercellularity | Mesangial proliferative GN | iga, lupus class II, early sgs |
| Endocapillary proliferation | Acute GN | irgn, lupus class III/IV, iga (severe) |
| Crescent formation | Crescentic GN | nca, ntiGbm, immune complex crescentic GN |
| Membranous pattern (GBM thickening) | Membranous GN | membranous, lupus class V, drug-induced |
| MPGN pattern (mesangial expansion + GBM duplication) | MPGN | cryoglobulinemic, lupus, c3, HCV, monoclonal gammopathy |
| Segmental sclerosis | FSGS | sgs NOS, collapsing, tip, perihilar, cellular |
| Nodular mesangial expansion | Nodular glomerulosclerosis | diabeticNephropathy (KW nodules), amyloid, monoclonal gammopathy |
| Global sclerosis | Chronic damage | End-stage any GN; chronic transplant injury |
| Tubular atrophy + interstitial fibrosis | Chronic tubulointerstitial injury | Chronic GN, chronic TIN, chronic transplant injury |
| Arteriolar hyalinosis | Chronic vascular injury | diabeticNephropathy, chronic CNI toxicity, hypertensive nephrosclerosis |
| Isometric vacuolization | Acute CNI toxicity | cniToxicity (tacrolimus, cyclosporine) |

**Immunofluorescence (IF):**

| Pattern | Significance | DDx Narrowing |
|---|---|---|
| Negative (no deposits) | Pauci-immune GN, MCD, FSGS, TBMN | nca, ntiGbm, mcd, sgs, 	hinBasementMembrane |
| Linear IgG along GBM | Anti-GBM disease | ntiGbm (pathognomonic) |
| Granular mesangial IgA (dominant) | IgA nephropathy | iga (pathognomonic) |
| Granular mesangial + capillary wall IgA | IgA vasculitis (HSP) with nephritis | iga vasculitis |
| Full-house (IgG, IgA, IgM, C3, C1q) | Lupus nephritis | lupus (highly suggestive; C1q is characteristic) |
| Granular capillary wall IgG/C3 | Membranous pattern | membranous, lupus class V |
| C3 dominant (no/minimal Ig) | C3 glomerulopathy | c3 (C3GN or DDD) |
| C3 + Ig (starry sky) | Post-infectious GN | irgn |
| IgG kappa or lambda restriction | Monoclonal gammopathy-associated GN | Cast nephropathy, LCDD, fibrillary GN, immunotactoid GN |
| C4d in peritubular capillaries | Antibody-mediated rejection | ntibodyMediatedRejection (transplant) |

**Electron Microscopy (EM):**

| Finding | Significance | DDx Narrowing |
|---|---|---|
| Foot process effacement (FPE) only | Podocytopathy | mcd, sgs, early disease |
| Subepithelial electron-dense deposits | Membranous pattern | membranous, lupus class V |
| Subepithelial humps | Post-infectious GN | irgn (pathognomonic) |
| Subendothelial deposits | Active GN | lupus class III/IV, cryoglobulinemic, MPGN |
| Mesangial deposits | Mesangial GN | iga, lupus class II, early disease |
| Intramembranous dense deposits | Dense deposit disease | denseDepositDisease (pathognomonic) |
| Fibrillar deposits (12-22 nm) | Fibrillary GN | ibrillaryGlomerulonephritis |
| Microtubular deposits (>30 nm) | Immunotactoid GN | Immunotactoid GN |
| Fibrils (8-12 nm, Congo red positive) | Amyloidosis | myloid (pathognomonic) |
| GBM thinning (<275 nm) | Thin basement membrane | 	hinBasementMembrane |
| GBM lamellation/splitting | Alport syndrome | lport (pathognomonic) |
| Tubuloreticular inclusions | Lupus nephritis or HIV | lupus, hivan |
| Viral particles in tubular cells | BK virus nephropathy | kVirusNephropathy |

### 14.3 Serological Interpretation Guide

**ANCA Testing:**

| Result | Interpretation | Clinical Correlation |
|---|---|---|
| c-ANCA + PR3 ELISA positive | Highly specific for GPA | Upper + lower respiratory tract + renal involvement |
| p-ANCA + MPO ELISA positive | Suggestive of MPA or EGPA | MPA: renal-limited; EGPA: asthma + eosinophilia |
| c-ANCA positive, PR3 negative | Possible GPA (IF-positive, ELISA-negative) | Repeat testing; may be early disease; clinical correlation |
| p-ANCA positive, MPO negative | Possible drug-induced or other vasculitis | Check drug history; consider levamisole-cocaine |
| ANCA negative | Pauci-immune GN less likely but not excluded | 10-15% of pauci-immune GN are ANCA-negative; biopsy is definitive |

**Anti-GBM Testing:**

| Result | Interpretation | Clinical Correlation |
|---|---|---|
| Positive (>20 units/mL) | Anti-GBM disease confirmed | Start plasmapheresis + cyclophosphamide + steroids immediately |
| Weakly positive (10-20 units/mL) | Possible early disease or false positive | Repeat in 24-48 hours; correlate with clinical picture |
| Negative (<10 units/mL) | Anti-GBM disease excluded | If crescentic GN present, consider ANCA or immune complex |

**Complement Levels:**

| Pattern | Interpretation | DDx |
|---|---|---|
| Low C3 + Normal C4 | Alternative pathway activation | c3 G, post-infectious GN, aHUS, lupus (rare) |
| Low C3 + Low C4 | Classical pathway activation | lupus, cryoglobulinemic, post-infectious GN (severe), endocarditis |
| Low C4 + Normal C3 | Early classical pathway activation | cryoglobulinemic (early), monoclonal gammopathy |
| Normal C3 + Normal C4 | No complement consumption | iga, 	hinBasementMembrane, lport, mcd, sgs, membranous, diabeticNephropathy |

---

## 15. Clinical Pearls Compendium

This section consolidates the most critical clinical pearls from across the document for quick reference.

### 15.1 Diagnostic Pearls

> Never diagnose mcd in adults without biopsy. 30% of adults with nephrotic syndrome who appear to have MCD on clinical grounds are found to have FSGS on biopsy.

> In crescentic GN, ALWAYS check both ANCA AND anti-GBM simultaneously. 10-30% of anti-GBM patients are also ANCA-positive (dual-positive).

> MPGN is a histological pattern, NOT a disease. When you see MPGN on biopsy, always check: HCV RNA, SPEP/UPEP, complement levels, ANA, cryoglobulins. Treat the underlying cause.

> ADAMTS13 activity is THE critical test in TMA. ADAMTS13 <10% = TTP until proven otherwise. Never transfuse platelets in TTP.

> Always check BK viral load BEFORE biopsy in transplant patients with rising creatinine. BK nephropathy is the most common cause of unexplained rising Cr in the first year post-transplant.

> The pattern of complement consumption is the single most useful clue: Low C3 + normal C4 = alternative pathway (C3G, post-infectious). Low C3 + low C4 = classical pathway (lupus, cryoglobulinemia).

> Always check SPEP/UPEP in patients >50 with unexplained GN or complement consumption. Monoclonal immunoglobulins can activate complement, form fibrils, or deposit directly.

> In patients with diabetes and hematuria, ALWAYS investigate for a superimposed glomerular disease. Hematuria is uncommon in diabetic nephropathy until very late stages.

> A urological cause should be excluded in ALL patients >40 with unexplained hematuria before attributing it to a glomerular source.

> Treatment response is a powerful diagnostic tool. A patient with nephrotic syndrome who achieves complete remission with prednisone likely has MCD. A partial response suggests FSGS or membranous.

### 15.2 Treatment Pearls

> Start plasmapheresis IMMEDIATELY when anti-GBM is positive. Do not wait for biopsy. Delay significantly increases mortality and irreversible renal damage.

> Do NOT delay treatment for RPGN while awaiting serological results. If you cannot distinguish pauci-immune from anti-GBM, start plasmapheresis -- it is beneficial for both.

> Never transfuse platelets in TTP. Platelet transfusion provides substrate for further thrombus formation and can precipitate life-threatening complications.

> In TMA, empiric plasmapheresis should be initiated for suspected TTP while awaiting ADAMTS13 results. Delay in treatment significantly increases mortality.

> RAAS blockade (ACEi, ARBs) is absolutely contraindicated in pregnancy. Transition to methyldopa, labetalol, or nifedipine before conception.

> Eculizumab for aHUS requires meningococcal vaccination BEFORE initiation. Patients are at lifelong risk for meningococcal infection while on complement inhibition.

> When reducing immunosuppression for BK virus, ALWAYS monitor DSA. Reducing immunosuppression can unmask subclinical ABMR.

> Always perform age-appropriate malignancy screening in patients >40 with new membranous nephropathy. Paraneoplastic membranous is a distinct entity requiring treatment of the underlying tumor.

> Never start immunosuppression for cryoglobulinemic GN without first treating HCV. HCV is the trigger in 80% of cases.

> In children with classic nephrotic syndrome (abrupt onset, edema, heavy proteinuria, bland sediment), empiric steroids may be appropriate. In ALL adults, perform a biopsy before starting immunosuppression.

### 15.3 Prognostic Pearls

> IgA nephropathy: 20-30% progress to ESRD over 20 years. The Oxford classification (MEST-C) is the best validated predictor of outcomes.

> Membranous nephropathy: Anti-PLA2R positive patients have a 30% risk of spontaneous remission. Low-risk patients (proteinuria <4 g/day, stable GFR) may be observed for 3-6 months.

> FSGS: The collapsing variant has the worst prognosis, especially in HIV+ patients and those with APOL1 high-risk genotypes.

> Lupus nephritis: Class IV (diffuse proliferative) has the worst prognosis if untreated but responds well to aggressive immunosuppression. Class V (membranous) has a more indolent course but higher risk of thrombotic complications.

> ANCA vasculitis: PR3-positive disease (GPA) has a higher relapse rate than MPO-positive disease (MPA). Maintenance therapy with rituximab reduces relapse rates.

> Anti-GBM disease: If >50% of glomeruli show crescents at presentation, the prognosis for renal recovery is very poor. Early treatment is critical.

> Alport syndrome: Males with X-linked Alport almost inevitably progress to ESRD by age 30-40. ACEi from early stages may delay progression by 5-10 years.

> C3 glomerulopathy: DDD has a worse prognosis than C3GN. Both are chronic and progressive; complement inhibition (eculizumab) may be beneficial in selected cases.

> Fibrillary GN: Progressive disease with no proven effective therapy. Rituximab may slow progression in some cases.

> Transplant glomerulopathy: Chronic ABMR is the most common cause and has a poor prognosis. Prevention (optimized immunosuppression, DSA monitoring) is more effective than treatment.

---

## 16. Quality Metrics for DDx Performance

### 16.1 Diagnostic Accuracy Metrics

| Metric | Target | Measurement |
|---|---|---|
| Biopsy-to-diagnosis rate | >95% | Percentage of biopsies resulting in a definitive histological diagnosis |
| First-biopsy adequacy | >90% | Percentage of biopsies with adequate tissue for LM + IF + EM |
| Serological concordance | >85% | Percentage of cases where serological and histological findings agree |
| Time to diagnosis (emergent) | <48 hours | Time from presentation to definitive diagnosis for P0 conditions |
| Time to diagnosis (urgent) | <7 days | Time from presentation to definitive diagnosis for P1 conditions |
| Time to diagnosis (routine) | <30 days | Time from presentation to definitive diagnosis for P3 conditions |
| Dual-positive detection rate | >95% | Percentage of dual ANCA + anti-GBM patients identified |

### 16.2 Treatment Initiation Metrics

| Metric | Target | Measurement |
|---|---|---|
| Time to plasmapheresis (anti-GBM) | <24 hours | Time from positive anti-GBM to first plasmapheresis session |
| Time to immunosuppression (RPGN) | <24 hours | Time from RPGN diagnosis to first immunosuppressive dose |
| Time to BK treatment reduction | <7 days | Time from BK viremia >10,000 to immunosuppression reduction |
| Malignancy screening rate (membranous) | 100% | Percentage of membranous patients >40 with documented cancer screening |
| Family screening rate (hereditary) | >90% | Percentage of hereditary nephropathy patients with documented family screening |

### 16.3 Error Prevention Metrics

| Metric | Target | Measurement |
|---|---|---|
| Missed dual-positive rate | <5% | Percentage of dual ANCA + anti-GBM patients not identified on initial workup |
| Biopsy-deferred MCD (adults) | <5% | Percentage of adults diagnosed with MCD without biopsy |
| BK-first protocol compliance | >90% | Percentage of transplant patients with BK viral load checked before biopsy |
| Complement screening rate | >95% | Percentage of GN patients with C3/C4 checked |
| HCV screening rate (MPGN) | 100% | Percentage of MPGN patients with HCV RNA checked |
| Drug history documentation | 100% | Percentage of GN patients with documented drug/substance history |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*
*Total Sections: 16*
*Total Appendices: 5*
*Total Diseases Covered: 23*
*Total Syndromes Covered: 14*
*Total Clinical Pearls: 50+*
*Total Diagnostic Errors Cataloged: 25+*
*Total Decision Trees: 5*

---

## 17. Biopsy Pattern Recognition Atlas

This section provides a systematic approach to recognizing biopsy patterns and mapping them to specific diseases.

### 17.1 Pattern-to-Disease Mapping

**Pattern 1: Minimal Change (Normal LM + FPE on EM)**

| Feature | mcd | Early sgs | Obesity-related | Drug-induced |
|---|---|---|---|---|
| Age | Children (2-6) peak | Any age; AA > Caucasian | BMI >35 | Drug exposure history |
| Proteinuria | Nephrotic, abrupt | Nephrotic or sub-nephrotic | Sub-nephrotic | Variable |
| Hematuria | Absent | May be present | Absent | Variable |
| Steroid response | >90% complete | 30-50% partial | N/A | Drug withdrawal |
| Biopsy progression | May evolve to FSGS | Segmental sclerosis develops | Glomerulomegaly persists | Resolves with drug withdrawal |
| IF | Negative | Negative | Negative | Negative |

**Pattern 2: Segmental Sclerosis (FSGS Variants)**

| Variant | Location | Key Features | Prognosis | Treatment |
|---|---|---|---|---|
| NOS (Not Otherwise Specified) | Any segment | Most common variant; variable clinical course | Intermediate | Steroids + CNI |
| Tip | Tip (urinary pole) | Better prognosis; may respond to steroids alone | Better | Steroids first |
| Cellular | Segment with hypercellularity | Overlaps with MCD; may respond to steroids | Intermediate | Steroids + CNI |
| Perihilar | Perihilar region | Associated with vascular injury; reflux nephropathy; obesity | Worse | Address secondary cause |
| Collapsing | Global collapse of capillary loops | Worst prognosis; HIV, APOL1; steroid-resistant | Worst | ART (if HIV); CNI; rituximab |

**Pattern 3: Membranous Pattern (GBM Thickening)**

| Feature | Primary membranous | lupus class V | Drug-induced | diabeticNephropathy |
|---|---|---|---|---|
| Anti-PLA2R | Positive (70-80%) | Negative | Negative | Negative |
| ANA | Negative | Positive | Variable | Negative |
| IF | IgG/C3 granular | Full-house | Variable | Linear IgG (nonspecific) |
| EM deposits | Subepithelial | Subepithelial + subendothelial | Subepithelial | No deposits |
| Treatment | Rituximab / observation | MMF + steroids | Drug withdrawal | SGLT2i + RAAS blockade |

**Pattern 4: MPGN Pattern (Mesangial Expansion + GBM Duplication)**

| Cause | IF Pattern | Key Serological Clue | Treatment |
|---|---|---|---|
| HCV-associated | IgM, C3, kappa restriction | HCV RNA positive | DAAs |
| cryoglobulinemic | IgM, C3, kappa restriction, "thrombi" | Cryoglobulins positive; low C4 | Treat HCV; rituximab |
| lupus | Full-house (IgG, IgA, IgM, C3, C1q) | ANA/anti-dsDNA positive; low C3/C4 | MMF + steroids |
| c3 | C3 dominant (no/minimal Ig) | Low C3 (C4 normal); C3 nephritic factor | Complement inhibition |
| Monoclonal-associated | IgG or IgM kappa/lambda restriction | SPEP/UPEP positive | Treat gammopathy |
| Post-infectious | C3 + Ig (starry sky) | ASO elevated; low C3 (resolves) | Supportive |

**Pattern 5: Crescentic GN**

| IF Pattern | Serological Pattern | Likely Diagnosis | Treatment |
|---|---|---|---|
| Pauci-immune | ANCA positive (PR3 or MPO) | nca vasculitis | Rituximab + steroids; plasmapheresis if severe |
| Pauci-immune | Anti-GBM positive | ntiGbm disease | Plasmapheresis + cyclophosphamide + steroids |
| Pauci-immune | Dual ANCA + anti-GBM positive | Dual-positive | Both treatments combined |
| Full-house | ANA/anti-dsDNA positive | lupus nephritis (class III/IV) | MMF + steroids |
| Mesangial + capillary IgA | IgA elevated | iga with crescents | Steroids + immunosuppression |
| C3 dominant | Low C3 | c3 with crescents | Complement inhibition |
| Negative (all serologies negative) | All negative | Idiopathic crescentic GN | Empiric immunosuppression |

### 17.2 EM Deposit Location Guide

| Deposit Location | DDx | Key Distinguishing Features |
|---|---|---|
| Mesangial only | iga, lupus class II, early disease | IgA dominant (IgAN); full-house (lupus) |
| Subendothelial | lupus class III/IV, cryoglobulinemic, early MPGN | Full-house (lupus); IgM/thrombi (cryo); MPGN pattern |
| Subepithelial | membranous, lupus class V, post-infectious GN | Spikes on silver stain (membranous); humps (post-infectious) |
| Intramembranous | DDD (denseDepositDisease) | Pathognomonic ribbon-like deposits within GBM |
| Mesangial + subendothelial | MPGN pattern | Multiple causes; check IF pattern and serologies |
| Mesangial + subepithelial | Mixed pattern | Consider lupus overlap, IgAN with membranous features |
| Tubuloreticular inclusions | lupus, hivan | Interferon-induced; characteristic of lupus and HIV |
| Fibrillar (random, 12-22 nm) | ibrillaryGlomerulonephritis | Congo red negative; IgG4 dominant |
| Microtubular (organized, >30 nm) | Immunotactoid GN | Congo red negative; often associated with monoclonal gammopathy |
| Fibrillar (random, 8-12 nm) | myloid | Congo red positive (apple-green birefringence) |

---

## 18. Biomarker Integration Guide

### 18.1 Emerging Biomarkers in Glomerular Disease

| Biomarker | Disease | Clinical Utility | Availability |
|---|---|---|---|
| Anti-PLA2R antibodies | membranous | Diagnosis (70-80% sensitivity); monitoring treatment response; predicting relapse | Widely available |
| Anti-THSD7A antibodies | membranous | Alternative target in anti-PLA2R-negative membranous (5-10%) | Available in specialized labs |
| Anti-Complement Factor H antibodies | aHUS | Distinguishes autoimmune aHUS from genetic aHUS; guides treatment duration | Specialized labs |
| C3 nephritic factor | c3 glomerulopathy | Identifies alternative pathway dysregulation; guides complement inhibition | Specialized labs |
| Soluble urokinase-type plasminogen activator receptor (suPAR) | sgs | May predict recurrence post-transplant; elevated in primary FSGS | Research; limited clinical use |
| Galactose-deficient IgA1 (Gd-IgA1) | iga | Pathogenic mechanism; may predict progression; therapeutic target | Research; limited clinical use |
| Urine CXCL10 | lupus nephritis | Predicts renal flare; monitors treatment response | Research; emerging clinical use |
| Urine EGF | CKD progression | Predicts rate of GFR decline across all GN types | Research |
| Plasma cell-free DNA (cfDNA) | Transplant rejection | Non-invasive detection of rejection; may replace protocol biopsies | Emerging clinical use |
| Donor-derived cfDNA (dd-cfDNA) | Transplant rejection | Non-invasive marker of graft injury; >0.5% suggests rejection | Emerging clinical use |

### 18.2 Biomarker Decision Matrix

| Clinical Scenario | Recommended Biomarkers | Interpretation |
|---|---|---|
| Suspected primary membranous | Anti-PLA2R, anti-THSD7A | Anti-PLA2R+ = primary; anti-PLA2R- = screen for secondary |
| Suspected c3 glomerulopathy | C3 nephritic factor, factor H, factor I, factor B, MCP | Identifies underlying complement dysregulation; guides eculizumab candidacy |
| Suspected aHUS | Complement testing (CH50, AH50, C3, factor H, factor I, factor B, MCP), anti-factor H antibodies | Distinguishes genetic from autoimmune aHUS; guides treatment duration |
| Suspected iga progression | Gd-IgA1 (research), Oxford MEST-C classification | MEST-C is current standard; Gd-IgA1 is emerging |
| Monitoring membranous treatment | Anti-PLA2R titer | Declining titer predicts remission; rising titer predicts relapse |
| Monitoring lupus nephritis | anti-dsDNA, C3, C4, urine CXCL10 | Rising anti-dsDNA + falling complements = flare risk |
| Transplant monitoring | DSA, dd-cfDNA | Rising DSA or dd-cfDNA >0.5% suggests rejection |
| FSGS recurrence risk | suPAR (research) | Elevated suPAR may predict recurrence post-transplant |

---

## 19. Decision Support Algorithms

### 19.1 "When to Biopsy" Algorithm

`
Patient with suspected glomerular disease
        |
        v
Is this EMERGENT (Cr doubling <1 week, DAH, severe HTN)?
        |
        +---> YES --> Biopsy within 24-48 hours (or treat empirically if not feasible)
        |
        +---> NO --> Continue assessment
                |
                v
        Is there a clear clinical diagnosis without biopsy?
                |
                +---> YES (e.g., classic pediatric MCD, clear diabetic nephropathy)
                |     --> Treat based on clinical diagnosis; biopsy if non-responsive
                |
                +---> NO --> Continue assessment
                        |
                        v
                Are there indications for biopsy?
                        |
                        +---> Adult nephrotic syndrome --> Biopsy
                        +---> Proteinuria >0.5 g/day + declining GFR --> Biopsy
                        +---> Active sediment + declining GFR --> Biopsy
                        +---> Suspicion of crescentic GN --> Biopsy
                        +---> Post-transplant dysfunction (unexplained) --> Biopsy
                        +---> CKD of unclear etiology --> Biopsy
                        +---> Isolated hematuria (low risk) --> Monitor first; biopsy if progression
                        +---> Isolated hematuria (high risk: >40, smoking) --> Consider biopsy
                                |
                                v
                        Are there contraindications to biopsy?
                                |
                                +---> Single kidney --> Risk-benefit assessment; consider alternatives
                                +---> Uncontrolled HTN --> Control BP first
                                +---> Coagulopathy --> Correct before biopsy
                                +---> Small kidneys (<8 cm) --> Low yield; consider alternatives
                                +---> Active infection --> Treat first
                                +---> Patient refusal --> Document discussion; alternatives
                                        |
                                        v
                                Proceed with biopsy
                                Request: LM + IF + EM
                                Classification: Disease-specific (Oxford, ISN/RPS, Banff)
`

### 19.2 "When to Start Immunosuppression" Algorithm

`
Diagnosis established or suspected
        |
        v
Is this EMERGENT?
        |
        +---> YES (anti-GBM, TTP, severe lupus class IV, crescentic GN >50%)
        |     --> Start empiric treatment IMMEDIATELY
        |     --> Do not wait for confirmatory testing
        |
        +---> NO --> Continue assessment
                |
                v
        Is the diagnosis DEFINITE or PROBABLE?
                |
                +---> YES --> Start treatment per guidelines
                |
                +---> POSSIBLE --> Is the condition likely to cause irreversible damage if untreated?
                        |
                        +---> YES (e.g., crescentic GN, severe nephrotic syndrome)
                        |     --> Start empiric treatment; monitor closely
                        |
                        +---> NO --> Observe; repeat testing; close follow-up
                                |
                                v
                        Has the patient failed conservative management?
                                |
                                +---> YES (e.g., proteinuria not responding to RAAS blockade/SGLT2i)
                                |     --> Escalate to immunosuppression
                                |
                                +---> NO --> Continue conservative management
`

### 19.3 "When to Refer for Transplant" Algorithm

`
Patient with CKD progressing toward ESRD
        |
        v
Is eGFR <20 mL/min/1.73m2?
        |
        +---> YES --> Assess transplant eligibility
        |
        +---> NO --> Reassess at next visit; continue nephrology management
                |
                v
        Assess transplant eligibility
                |
                +---> Age-appropriate?
                +---> No active malignancy?
                +---> No active infection?
                +----- Cardiac clearance?
                +---> BMI acceptable (<35-40)?
                +---> No contraindications (active substance abuse, non-adherence)?
                +---> Immunological status (DSA, ABO compatibility)?
                        |
                        +---> Eligible --> Refer to transplant center
                        |     --> Begin living donor evaluation if applicable
                        |     --> Consider preemptive transplant (before dialysis)
                        |
                        +---> Not yet eligible --> Address barriers
                        |     --> Treat obesity, substance abuse, infections
                        |     --> Optimize cardiovascular risk
                        |     --> Reassess in 3-6 months
                        |
                        +---> Permanently ineligible --> Prepare for dialysis
                              --> Consider peritoneal dialysis vs. hemodialysis
                              --> Discuss advance care planning
`

---

## 20. References and Evidence Base

### 20.1 Guideline Sources

| Organization | Guideline | Year | Key Recommendations Incorporated |
|---|---|---|---|
| KDIGO | GN Workup and Classification | 2021 | Biopsy indications, classification systems, treatment algorithms |
| KDIGO | Lupus Nephritis | 2024 | ISN/RPS classification, induction/maintenance therapy |
| KDIGO | ANCA Vasculitis | 2024 | Rituximab-based induction, maintenance therapy, BVAS |
| KDIGO | Membranous Nephropathy | 2024 | Anti-PLA2R-guided treatment, rituximab as first-line |
| KDIGO | IgA Nephropathy | 2024 | Oxford classification (MEST-C), SGLT2i, RAAS blockade |
| KDIGO | Transplant | 2024 | Banff classification, rejection management, BK monitoring |
| KDIGO | Complement-Mediated Diseases | 2024 | Eculizumab for aHUS, complement testing |
| ERA-EDTA | Cryoglobulinemic GN | 2023 | HCV treatment, rituximab for vasculitis |
| AST | Transplant Rejection | 2024 | Banff 2019 update, DSA monitoring, dd-cfDNA |
| ASN | TMA | 2023 | ADAMTS13 testing, eculizumab, caplacizumab |

### 20.2 Key References

1. KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases. *Kidney International*. 2021;100(4S):S1-S276.
2. KDIGO 2024 Clinical Practice Guideline for Lupus Nephritis. *Kidney International*. 2024.
3. KDIGO 2024 Clinical Practice Guideline for ANCA-Associated Vasculitis. *Kidney International*. 2024.
4. KDIGO 2024 Clinical Practice Guideline for Membranous Nephropathy. *Kidney International*. 2024.
5. KDIGO 2024 Clinical Practice Guideline for IgA Nephropathy. *Kidney International*. 2024.
6. KDIGO 2024 Clinical Practice Guideline for Kidney Transplantation. *Kidney International*. 2024.
7. Haas M, et al. Updating the International Classification of GN: The Banff 2018 Working Proposal. *Kidney International*. 2018;93(4):789-796.
8. Cattran DC, et al. KDIGO Clinical Practice Guideline for Glomerulonephritis. *Kidney Int Suppl*. 2012;2:139-274.
9. Ronco P, et al. Membranous Nephropathy. *Nat Rev Dis Primers*. 2021;7(1):69.
10. Lafayette RA, et al. Treatment of IgA Nephropathy. *Kidney International*. 2023;103(5):819-832.
11. Jennette JC, et al. 2012 Revised International Chapel Hill Consensus Conference Nomenclature of Vasculitides. *Arthritis Rheum*. 2013;65(1):1-11.
12. Sethi S, et al. C3 Glomerulopathy: Pathogenesis and Classification. *Kidney International*. 2018;93(1):27-36.
13. Alvarado A, et al. Thrombotic Microangiopathy: Diagnosis and Management. *Kidney International*. 2023;104(1):30-43.
14. Loupy A, et al. The Banff 2019 Kidney Meeting Report. *Am J Transplant*. 2020;20(3):565-603.
15. Dvanajscak Z, et al. Fibrillary Glomerulonephritis and Immunotactoid Glomerulopathy. *J Am Soc Nephrol*. 2020;31(10):2282-2293.

### 20.3 Disease Evidence Strength

| Disease | Evidence Quality | Key Evidence Sources |
|---|---|---|
| iga | High | STOP-IgAN, TESTING, KDIGO trials; Oxford validation studies |
| membranous | High | MENTOR, RITURNS, STARMEN trials; anti-PLA2R natural history studies |
| lupus nephritis | High | ALMS, Euro-Lupus, BLISS-LN trials; ISN/RPS validation |
| nca vasculitis | High | RAVE, RITUXVAS, PEXIVAS, MAINRITSAN trials |
| ntiGbm | Moderate | PEXIVAS (anti-GBM arm); historical controlled studies |
| sgs | Moderate | FSGS clinical trials; APOL1 genetic studies |
| mcd | Moderate | Pediatric steroid response studies; adult biopsy studies |
| c3 glomerulopathy | Low-Moderate | Small case series; complement pathway studies; eculizumab case reports |
| denseDepositDisease | Low | Small case series; complement pathway studies |
| cryoglobulinemic | Moderate | HCV treatment studies; rituximab trials |
| ibrillaryGlomerulonephritis | Low | Small case series; no randomized trials |
| lport | Moderate | ACEi trials; genetic studies; transplant outcomes |
| 	hinBasementMembrane | Low | Natural history studies; genetic studies |
| diabeticNephropathy | High | CREDENCE, DAPA-CKD, EMPA-KIDNEY trials |
| kVirusNephropathy | Moderate | observational studies; treatment protocols |
| ntibodyMediatedRejection | Moderate | Banff classification studies; treatment protocols |
| 	CellMediatedRejection | Moderate | Banff classification studies; treatment protocols |
| 	ransplantGlomerulopathy | Low-Moderate | Observational studies; natural history data |
| cniToxicity | Moderate | Pharmacokinetic studies; conversion protocols |
| drugInducedGn | Low | Case reports; pharmacovigilance data |
| hivan | Moderate | ART treatment studies; APOL1 genetic studies |
| irgn | Moderate | Post-streptococcal GN natural history; treatment studies |
| mpgn | Moderate | HCV treatment studies; complement pathway studies |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*
*Total Sections: 20*
*Total Appendices: 5*
*Total Diseases Covered: 23*
*Total Syndromes Covered: 14*
*Total Clinical Pearls: 50+*
*Total Diagnostic Errors Cataloged: 25+*
*Total Decision Trees: 8*
*Total Biomarkers Referenced: 10+*
*Total References: 15*

---

## 21. Complication Recognition and Management

### 21.1 Nephrotic Syndrome Complications

| Complication | Mechanism | Clinical Features | Diagnosis | Management |
|---|---|---|---|---|
| Venous thromboembolism (renal vein thrombosis) | Loss of antithrombin III, protein C/S; hypercoagulable state | Flank pain, sudden increase in proteinuria, hematuria, declining GFR | Doppler ultrasound, CT venography, MR venography | Anticoagulation (LMWH then warfarin; DOACs emerging) |
| Pulmonary embolism | Extension of DVT or renal vein thrombosis | Dyspnea, pleuritic chest pain, hemoptysis, tachycardia | CT pulmonary angiography, V/Q scan | Anticoagulation; thrombolysis if massive PE |
| Infections (spontaneous bacterial peritonitis) | Loss of immunoglobulins, complement; ascites as culture medium | Fever, abdominal pain, rebound tenderness, ascites | Diagnostic paracentesis (PMN >250/mm3) | Empiric antibiotics (ceftriaxone); albumin infusion |
| Hyperlipidemia | Hepatic overproduction of lipoproteins | Accelerated atherosclerosis; unclear acute risk | Fasting lipid panel | Statins (if persistent); treat underlying GN |
| Acute kidney injury (AKI) | Hypovolemia; renal vein thrombosis; drug nephrotoxicity; tubular dysfunction | Oliguria, rising Cr, volume depletion | Cr, urinalysis, renal ultrasound | Volume resuscitation; treat underlying cause; avoid nephrotoxins |
| Hypothyroidism | Loss of thyroid-binding globulin in urine | Fatigue, weight gain, cold intolerance | TSH, free T4 | Levothyroxine supplementation |
| Vitamin D deficiency | Loss of vitamin D-binding protein in urine | Bone pain, osteomalacia, secondary hyperparathyroidism | 25-OH vitamin D, PTH | Cholecalciferol supplementation |

### 21.2 Vasculitis Complications

| Complication | Associated Disease | Clinical Features | Diagnosis | Management |
|---|---|---|---|---|
| Pulmonary hemorrhage | nca (GPA/MPA), ntiGbm, lupus | Hemoptysis, dyspnea, anemia, diffuse alveolar hemorrhage on CT | CT chest, bronchoscopy with BAL (hemosiderin-laden macrophages), DLCO | Plasmapheresis, immunosuppression, mechanical ventilation if severe |
| Subglottic stenosis | nca (GPA) | Stridor, dyspnea, hoarseness | CT neck, laryngoscopy, pulmonary function tests | Endoscopic dilation; systemic immunosuppression |
| Sinonasal destruction | nca (GPA) | Chronic sinusitis, nasal crusting, saddle nose deformity, septal perforation | CT sinuses, nasal biopsy, ANCA | Systemic immunosuppression; surgical repair |
| Mononeuritis multiplex | nca (GPA/MPA/EGPA), cryoglobulinemic | Asymmetric sensory/motor neuropathy, foot/wrist drop | Nerve conduction studies, EMG | Immununosuppression; physical therapy |
| Cardiac involvement | nca (EGPA), lupus, cryoglobulinemic | Pericarditis, myocarditis, heart failure, arrhythmias | ECG, echocardiography, cardiac MRI, troponin | Immunosuppression; cardiology consultation |
| Mesenteric ischemia | Polyarteritis nodosa, nca | Abdominal pain, bloody stool, peritoneal signs | CT abdomen, mesenteric angiography, surgical consultation | Immunosuppression; surgical intervention if ischemia |
| Cerebrovascular disease | nca, lupus, cryoglobulinemic | Stroke, seizures, encephalopathy, headache | CT/MRI brain, cerebral angiography, LP | Immunosuppression; stroke protocol |

### 21.3 Transplant Complications

| Complication | Timing | Clinical Features | Diagnosis | Management |
|---|---|---|---|---|
| Hyperacute rejection | Minutes to hours | Sudden graft dysfunction, fever, graft tenderness, systemic symptoms | Positive crossmatch, graft biopsy (thrombosis, neutrophilic infiltration) | Graft nephrectomy (irreversible) |
| Acute TCMR | Days to months | Rising Cr, decreased urine output, graft tenderness | Biopsy (interstitial inflammation, tubulitis); Banff classification | Pulse steroids; ATG for steroid-resistant |
| Acute ABMR | Days to months | Rising Cr, new DSA, thrombocytopenia | Biopsy (microvascular inflammation, C4d+); DSA screen | Plasmapheresis + IVIG + rituximab |
| BK virus nephropathy | 1-6 months | Rising Cr, BK viremia, BK viruria | BK PCR; biopsy with SV40 stain | Reduce immunosuppression; leflunomide; monitor DSA |
| CMV viremia/disease | 1-6 months (or later with delayed prophylaxis) | Fever, malaise, leukopenia, pneumonitis, colitis | CMV PCR; tissue biopsy | Valganciclovir; reduce immunosuppression |
| Drug toxicity (CNI) | Any time | Rising Cr after dose change, tremor, gingival hyperplasia | CNI trough levels; biopsy (isometric vacuolization) | Reduce CNI dose; convert to mTOR inhibitor or belatacept |
| Recurrent disease | Variable by disease | Proteinuria, declining GFR, disease-specific features | Allograft biopsy; compare with native kidney biopsy | Disease-specific treatment |
| PTLD (Post-transplant lymphoproliferative disorder) | >3 months | Lymphadenopathy, fever, weight loss, organomegaly | CT; EBV PCR; tissue biopsy (monomorphic vs polymorphic) | Reduce immunosuppression; rituximab; chemotherapy |

---

## 22. Drug Dosing Considerations in Glomerular Disease

### 22.1 Immunosuppressive Drug Adjustments

| Drug | Standard Dose | Renal Adjustment | Key Monitoring | Special Considerations |
|---|---|---|---|---|
| Prednisone | 0.5-1 mg/kg/day (max 60-80 mg) | No adjustment needed | Blood glucose, BP, bone density, growth (children) | Taper slowly; PJP prophylaxis if >20 mg/day |
| Mycophenolate mofetil (MMF) | 1-1.5 g BID | No adjustment; consider dose reduction if CrCl <25 | CBC (leukopenia), GI symptoms, pregnancy test | Teratogenic; avoid in pregnancy; Giardia risk |
| Cyclophosphamide | 0.5-1 g/m2 IV monthly or 2 mg/kg/day PO | Consider dose reduction if CrCl <30 | CBC (nadir day 10-14), urine toxicity, fertility | Gonadotoxic; consider fertility preservation; bladder cancer risk |
| Azathioprine | 1-2 mg/kg/day | No adjustment; consider dose reduction if CrCl <30 | CBC (leukopenia), LFTs, TPMT genotyping | TPMT deficient: reduce dose 75%; avoid in pregnancy |
| Tacrolimus | 0.05-0.1 mg/kg BID (target trough 5-10 ng/mL) | No dose adjustment; monitor levels closely | Trough levels, Cr, glucose, K+, Mg2+, CNI levels | Narrow therapeutic window; drug interactions common |
| Cyclosporine | 3-5 mg/kg BID (target trough 100-200 ng/mL) | No dose adjustment; monitor levels closely | Trough levels, Cr, lipids, BP, gingival hyperplasia, hirsutism | Less nephrotoxic conversion option vs. tacrolimus |
| Rituximab | 375 mg/m2 weekly x4 or 1g x2 (2 weeks apart) | No adjustment needed | CD19/CD20 count, immunoglobulin levels, hepatitis B reactivation | Screen for hepatitis B before use; PJP prophylaxis |
| Belatacept | 10 mg/kg monthly (after induction) | No adjustment needed | Glucose, CBC, EBV/PTLD risk | Only for EBV-seropositive patients; once-monthly dosing |
| Eculizumab | 900 mg weekly x4, then 1200 mg every 2 weeks | No adjustment needed | Complement activity (CH50, AH50), meningococcal vaccination | Lifelong treatment for aHUS; meningococcal vaccine required |
| Plasmapheresis | 1-1.5 plasma volumes x5-7 sessions | N/A | Fibrinogen, immunoglobulin levels, coagulation | Replace immunoglobulins if levels drop; monitor for citrate toxicity |

### 22.2 Supportive Medication Adjustments

| Medication | Indication | Dose | Renal Adjustment | Key Monitoring |
|---|---|---|---|---|
| ACEi (enalapril, lisinopril) | Proteinuria reduction; BP control | titrate to max tolerated dose | Start low if Cr >2 or K+ >5.0 | Cr, K+ (check 1-2 weeks after initiation/change) |
| ARB (losartan, valsartan) | Proteinuria reduction; BP control | titrate to max tolerated dose | Start low if Cr >2 or K+ >5.0 | Cr, K+ (check 1-2 weeks after initiation/change) |
| SGLT2i (dapagliflozin, empagliflozin) | Proteinuria reduction; cardiorenal protection | Dapagliflozin 10 mg daily; Empagliflozin 10 mg daily | Can be used down to eGFR 20 (KDIGO 2024) | Volume status; genital mycotic infections; DKA risk |
| Statins | Hyperlipidemia in nephrotic syndrome | Atorvastatin 20-40 mg daily | No adjustment for most statins | LFTs; CK if myalgias; drug interactions with CNI |
| Loop diuretics | Edema in nephrotic syndrome | Furosemide 20-80 mg BID; Bumetanide 0.5-2 mg BID | Effective even in advanced CKD | Electrolytes; volume status; ototoxicity (high doses) |
| Albumin infusion | Severe hypoalbuminemia with diuretic resistance | 25% albumin 1g/kg IV + furosemide | No adjustment | Volume overload risk; expensive; temporary benefit only |
| Anticoagulation (warfarin) | Renal vein thrombosis in nephrotic syndrome | INR target 2.0-3.0 | No adjustment; but increased sensitivity in hypoalbuminemia | INR monitoring; bleeding risk; drug interactions |
| Anticoagulation (DOACs) | Emerging data for nephrotic syndrome VTE | Rivaroxaban 20 mg daily; Apixaban 5 mg BID | Rivaroxaban: avoid if CrCl <15; Apixaban: adjust if CrCl <25 | Less monitoring; but less data in nephrotic syndrome |

---

## 23. Patient Education Framework

### 23.1 Key Messages by Disease

| Disease | Key Patient Education Points |
|---|---|
| iga | "Your condition is the most common kidney disease worldwide. It often has a benign course, but we need to monitor your proteinuria and blood pressure closely. SGLT2 inhibitors and blood pressure medications can slow progression." |
| membranous | "Your condition has a good chance of responding to treatment. We will monitor your antibody levels (anti-PLA2R) to guide therapy. We also need to screen for certain cancers as they can sometimes trigger this condition." |
| lupus nephritis | "Your kidney disease is caused by your immune system attacking your kidneys. We need strong medications to control this, but they require careful monitoring for infections and other side effects." |
| nca vasculitis | "This is a serious condition that affects your blood vessels and kidneys. We need to start aggressive treatment immediately to prevent irreversible damage. Treatment typically lasts 12-24 months." |
| ntiGbm | "This is a medical emergency. We need to start plasmapheresis (filtering your blood) immediately along with strong medications. Early treatment is critical for kidney recovery." |
| sgs | "Your kidney disease has several possible causes. We need to identify whether it is primary (immune-related) or secondary to another condition. Treatment depends on the cause." |
| diabeticNephropathy | "Your kidney disease is related to your diabetes. Tight control of your blood sugar and blood pressure is essential. New medications (SGLT2 inhibitors) can significantly slow progression." |
| c3 glomerulopathy | "Your condition involves your complement system, which is part of your immune system. We need specialized testing to identify the exact cause. Treatment may involve complement-blocking medications." |
| lport | "This is a genetic kidney condition. We recommend genetic testing and screening of your family members. Starting blood pressure medications early can delay progression." |
| kVirusNephropathy | "A virus called BK virus is affecting your transplanted kidney. We need to reduce your anti-rejection medications carefully. This requires close monitoring to balance infection control and rejection prevention." |

### 23.2 Red Flag Symptoms to Report

| Symptom | Possible Significance | Action |
|---|---|---|
| Decreased urine output | AKI; obstruction; disease progression | Call nephrologist immediately |
| Blood in urine (new or worsening) | Disease flare; UTI; stone | Call nephrologist same day |
| Swelling (face, legs, abdomen) | Worsening proteinuria; fluid overload | Call nephrologist same day |
| Weight gain >2 kg in 1 week | Fluid retention | Call nephrologist same day |
| Fever >38.5C | Infection (immunosuppression-related) | Call nephrologist immediately; go to ED if septic features |
| Severe headache, visual changes | Hypertensive emergency; posterior reversible encephalopathy syndrome (PRES) | Go to ED immediately |
| Chest pain, shortness of breath | Pulmonary embolism; pulmonary hemorrhage; pericarditis | Go to ED immediately |
| Severe abdominal pain | Mesenteric ischemia; pancreatitis; bowel perforation | Go to ED immediately |
| New weakness/numbness in extremities | Mononeuritis multiplex; stroke; hypokalemia | Call nephrologist same day |
| Tremor, confusion, seizures | Drug toxicity (CNI); hypertensive encephalopathy; PRES | Go to ED immediately |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*
*Document Classification: Clinical Reference*
*Review Cycle: Annual*
*Owner: Glomerular Disease Expert System (GDES) Team*

---

## 24. Diagnostic Pitfalls in Special Scenarios

### 24.1 The Elderly Patient (>75 years)

| Pitfall | Example | Consequence | Prevention |
|---|---|---|---|
| Attributing all findings to "aging kidneys" | 80-year-old with hematuria + declining GFR labeled as "age-related CKD"; actually has ANCA vasculitis | Missed treatable vasculitis; irreversible renal damage | Always investigate hematuria + declining GFR regardless of age |
| Avoiding biopsy due to age | 78-year-old with nephrotic syndrome, biopsy deferred "due to age"; actually has treatable membranous | Missed diagnosis; unnecessary progression | Age alone is not a contraindication to biopsy; assess frailty, not chronological age |
| Over-immunosuppressing | 80-year-old treated with full-dose cyclophosphamide for ANCA vasculitis; develops severe infections | Treatment-related mortality | Use age-appropriate dosing; consider rituximab over cyclophosphamide in elderly |
| Missing drug interactions | Elderly patient on multiple medications; drug-induced GN not considered | Unnecessary immunosuppression | Comprehensive medication reconciliation in all elderly patients with GN |
| Underestimating malignancy risk | 75-year-old with membranous nephropathy, cancer screening not performed due to age | Missed paraneoplastic membranous | Age-appropriate cancer screening regardless of age |

### 24.2 The Obese Patient (BMI >35)

| Pitfall | Example | Consequence | Prevention |
|---|---|---|---|
| Attributing proteinuria to obesity | BMI 42 with sub-nephrotic proteinuria labeled as "obesity-related glomerulopathy"; actually has FSGS | Missed primary FSGS; delayed immunosuppression | Biopsy if proteinuria >1 g/day or declining GFR in obese patients |
| Biopsy technical difficulty | Obese patient; percutaneous biopsy not feasible | Delayed diagnosis | Consider alternative biopsy approaches (transjugular, laparoscopic) |
| Drug dosing errors | Immunosuppressive drugs dosed on actual body weight instead of ideal body weight | Overdose; toxicity | Use ideal body weight for drug dosing in obese patients |
| Missed APOL1 risk alleles | Obese African American with FSGS; APOL1 not tested | Missed genetic contribution to disease | APOL1 genotyping in all African American patients with FSGS |
| Metabolic syndrome overlap | Obesity + diabetes + hypertension + FSGS; which is causing the kidney disease? | Inappropriate treatment targeting | Comprehensive metabolic assessment; biopsy to determine primary etiology |

### 24.3 The Pregnant Patient

| Pitfall | Example | Consequence | Prevention |
|---|---|---|---|
| Confusing pre-eclampsia with lupus flare | Pregnant lupus patient with rising proteinuria and HTN labeled as "pre-eclampsia"; actually lupus nephritis flare | Delayed immunosuppression; renal progression | Check complements and anti-dsDNA; biopsy if uncertain (procedure is safe in pregnancy) |
| Using RAAS blockade | ACEi started in pregnant patient with proteinuria | Teratogenic (renal agenesis, oligohydramnios, fetal death) | ALWAYS discontinue RAAS blockade before conception; transition to methyldopa/labetalol |
| Missing TTP in pregnancy | Pregnant patient with TMA labeled as "HELLP syndrome"; TTP not considered | Maternal and fetal death (80% mortality without treatment) | ALWAYS check ADAMTS13 in TMA during pregnancy |
| Over-immunosuppressing | Pregnant lupus patient treated with cyclophosphamide | Teratogenic (first trimester: major malformations) | Use azathioprine (safe in pregnancy); avoid MMF and cyclophosphamide |
| Not monitoring fetal growth | Pregnant patient on immunosuppression without fetal growth monitoring | Intrauterine growth restriction; preeclampsia | Regular fetal growth monitoring; maternal-fetal medicine collaboration |

### 24.4 The HIV-Positive Patient

| Pitfall | Example | Consequence | Prevention |
|---|---|---|---|
| Attributing all renal disease to HIVAN | HIV+ patient with proteinuria labeled as "HIVAN" without biopsy; actually has immune complex GN | Missed treatable disease | Biopsy HIV+ patients with renal disease; distinguish HIVAN from other GN |
| Not starting ART promptly | HIV+ patient with collapsing FSGS, ART delayed while awaiting renal biopsy | Worsening viral load; worse renal outcome | Start ART immediately in HIV+ patients with renal disease; do not delay for biopsy |
| Missing APOL1 contribution | HIV+ African American with FSGS; APOL1 not tested | Missed genetic risk factor | APOL1 genotyping in all HIV+ African Americans with FSGS |
| Drug interactions | ART medications interacting with immunosuppressive drugs | Subtherapeutic or toxic drug levels | Pharmacy review of all drug interactions; coordinate HIV and nephrology care |
| False-positive ANA | HIV+ patient with positive ANA labeled as "lupus"; ANA is falsely positive in HIV | Unnecessary immunosuppression | Confirm ANA with anti-dsDNA; biopsy to confirm lupus nephritis |

---

## 25. Research Frontiers and Emerging Concepts

### 25.1 Pathogenic Mechanisms Under Investigation

| Disease | Emerging Concept | Potential Therapeutic Target | Status |
|---|---|---|---|
| iga | Galactose-deficient IgA1 (Gd-IgA1) as pathogenic molecule; Gd-IgA1 antibody complex formation | Anti-Gd-IgA1 antibodies; B-cell targeting; complement inhibition | Phase II trials ongoing |
| membranous | PLA2R as target antigen; THSD7A as alternative antigen; complement-mediated injury | Rituximab (anti-CD20); complement inhibition | Phase III completed (rituximab); complement trials ongoing |
| sgs | Circulating permeability factor; suPAR as candidate; podocyte injury pathways | Anti-suPAR antibodies; complement inhibition; sparsentan (dual endothelin/angiotensin receptor antagonist) | Phase II/III trials ongoing |
| lupus nephritis | Type I interferon pathway; B-cell activating factor (BAFF); complement activation | Anifrolumab (anti-IFNAR); belimumab (anti-BAFF); voclosporin (CNI) | Phase III completed; approved therapies |
| nca vasculitis | B-cell-mediated autoimmunity; complement activation (alternative pathway) | Rituximab (anti-CD20); avacopan (C5a receptor inhibitor); eculizumab (anti-C5) | Phase III completed; approved therapies |
| c3 glomerulopathy | Alternative complement pathway dysregulation; C3 nephritic factor; factor H deficiency | Pegcetacoplan (anti-C3); iptacopan (factor B inhibitor); danicopan (factor B inhibitor) | Phase II/III trials ongoing |
| aHUS | Complement pathway mutations; anti-factor H antibodies | Eculizumab (anti-C5); ravulizumab (long-acting anti-C5); danicopan (factor B inhibitor) | Phase III completed; approved therapies |
| ibrillaryGlomerulonephritis | DNAJB9 as diagnostic marker; IgG4-dominant deposits; monoclonal gammopathy association | Rituximab; bortezomib; complement inhibition | Case series; no randomized trials |
| denseDepositDisease | C3 convertase dysregulation; C3 nephritic factor; lipodystrophy association | Pegcetacoplan; complement pathway inhibitors | Phase II trials ongoing |
| hivan | APOL1 risk variants; direct HIV podocyte infection; ART response | ART optimization; APOL1 gene therapy (investigational) | ART is standard; gene therapy in preclinical stages |

### 25.2 Diagnostic Advances

| Technology | Application | Potential Impact | Timeline |
|---|---|---|---|
| Liquid biopsy (dd-cfDNA) | Non-invasive transplant rejection detection | Replace protocol biopsies; earlier rejection detection | 2-5 years for widespread adoption |
| Single-cell RNA sequencing | Characterize infiltrating immune cells in GN biopsies | Precision medicine; identify novel therapeutic targets | Research phase; 5-10 years |
| Artificial intelligence (AI) pathology | Automated biopsy interpretation; pattern recognition | Faster diagnosis; reduced inter-observer variability | 3-7 years for clinical deployment |
| Urinary biomarker panels | Non-invasive GN diagnosis and monitoring | Reduce biopsy necessity; earlier flare detection | 3-5 years for validated panels |
| Complement pathway profiling | Comprehensive complement assessment | Personalized complement inhibition therapy | 2-5 years for clinical integration |
| Genetic risk scoring (APOL1, complement) | Predict disease risk and treatment response | Preemptive therapy; personalized immunosuppression | 2-5 years for clinical integration |
| Mass spectrometry-based amyloid typing | Definitive amyloid classification | Accurate typing; targeted therapy | Currently available in specialized centers |
| Spatial transcriptomics | Map gene expression in kidney tissue | Understand disease mechanisms; identify novel targets | Research phase; 5-10 years |

---

## 26. Quality Assurance and Audit Framework

### 26.1 Recommended Audit Metrics

| Metric | Target | Frequency | Data Source |
|---|---|---|---|
| Biopsy-to-diagnosis rate | >95% | Quarterly | Pathology database |
| Serological concordance rate | >85% | Quarterly | Lab + pathology correlation |
| Time to emergent treatment (anti-GBM, TTP) | <24 hours | Monthly | Clinical records |
| BK-first protocol compliance (transplant) | >90% | Quarterly | Transplant database |
| Complement screening rate (GN patients) | >95% | Quarterly | Lab database |
| HCV screening rate (MPGN patients) | 100% | Quarterly | Lab database |
| Malignancy screening rate (membranous >40) | 100% | Quarterly | Clinical records |
| Family screening rate (hereditary nephropathy) | >90% | Annually | Clinical records |
| Dual ANCA + anti-GBM detection rate | >95% | Annually | Lab + clinical correlation |
| Drug history documentation rate | 100% | Quarterly | Clinical records |
| Oxford classification reporting (IgAN) | >90% | Quarterly | Pathology database |
| ISN/RPS classification reporting (lupus) | >90% | Quarterly | Pathology database |
| Banff classification reporting (transplant) | >95% | Quarterly | Pathology database |
| Anti-PLA2R testing rate (membranous) | >90% | Quarterly | Lab database |
| C3 nephritic factor testing rate (C3G) | >80% | Annually | Lab database |

### 26.2 Audit Review Process

| Step | Action | Responsibility | Timeline |
|---|---|---|---|
| 1 | Data collection (automated from pathology/lab databases) | Quality assurance team | Monthly |
| 2 | Metric calculation and trend analysis | Quality assurance team | Quarterly |
| 3 | Review of missed diagnoses (false negatives) | Nephrology quality committee | Quarterly |
| 4 | Review of inappropriate biopsies (false positives) | Nephrology quality committee | Quarterly |
| 5 | Root cause analysis of diagnostic errors | Quality improvement team | As needed |
| 6 | Implementation of corrective actions | Department leadership | Within 30 days of identified gap |
| 7 | Re-audit to confirm improvement | Quality assurance team | 6 months after corrective action |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*
*Document Classification: Clinical Reference*
*Review Cycle: Annual*
*Owner: Glomerular Disease Expert System (GDES) Team*
*Total Sections: 26*
*Total Appendices: 5*
*Total Diseases Covered: 23*
*Total Syndromes Covered: 14*
*Total Clinical Pearls: 60+*
*Total Diagnostic Errors Cataloged: 30+*
*Total Decision Trees: 8*
*Total Biomarkers Referenced: 15+*
*Total References: 15*
*Total Audit Metrics: 15*

---

## 27. Appendices Index

### Appendix A: Quick Reference - Disease ID Index
Complete mapping of all 23 disease IDs to full names and primary categories. Located in Section 3 footer area.

### Appendix B: Quick Reference - Complement Patterns
Diagnostic approach based on C3/C4 consumption patterns. Located in Section 3 footer area.

### Appendix C: Quick Reference - Urgency Matrix
Time-to-action guidelines for all urgency levels (P0-P3). Located in Section 3 footer area.

### Appendix D: Quick Reference - Key Serological Tests
Comprehensive test-to-disease mapping for all major serological markers. Located in Section 3 footer area.

### Appendix E: Glossary of Abbreviations
Complete abbreviation reference for all terms used in this document. Located in Section 3 footer area.

---

## Document Control

| Item | Detail |
|---|---|
| Document ID | GDES-V4.2-DDX-001 |
| Version | 1.0 |
| Date | 2026-07-10 |
| Status | Final |
| Domain | Differential Diagnosis Engine |
| Classification | Clinical Reference |
| Confidentiality | Internal Use |
| Review Cycle | Annual |
| Next Review | 2027-07-10 |
| Owner | Glomerular Disease Expert System (GDES) Team |
| Approved By | [Pending Clinical Board Approval] |
| Distribution | GDES Platform, Nephrology Department |

### Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-10 | GDES Development Team | Initial release; comprehensive DDx library covering all 23 diseases and 14 syndromes |

### Related Documents

| Document ID | Document Name | Relationship |
|---|---|---|
| GDES-V4.2-DDX-002 | Diagnostic Algorithm Library | Companion; provides detailed algorithms |
| GDES-V4.2-TX-001 | Treatment Protocol Library | Companion; provides treatment guidance |
| GDES-V4.2-PG-001 | Prognosis Calculator | Companion; provides risk stratification |
| GDES-V4.2-ED-001 | Educational Content Library | Companion; provides patient education materials |
| GDES-V4.2-QA-001 | Quality Assurance Framework | Companion; provides audit and QA guidance |

---

*End of Document*
*GDES-V4.2-DDX-001 v1.0*
*Generated: 2026-07-10*

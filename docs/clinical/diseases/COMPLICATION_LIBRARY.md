# Complication Knowledge Library
**Document ID:** GDES-V4.2-COMP-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Complication Knowledge Library

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Complication Entities](#2-complication-entities)
   - 2.1 [Infection](#21-infection)
   - 2.2 [Thrombosis](#22-thrombosis)
   - 2.3 [Venous Thromboembolism (Nephrotic Syndrome)](#23-venous-thromboembolism-nephrotic-syndrome)
   - 2.4 [Acute Kidney Injury](#24-acute-kidney-injury)
   - 2.5 [CKD Progression](#25-ckd-progression)
   - 2.6 [Hypertension](#26-hypertension)
   - 2.7 [Hyperkalemia](#27-hyperkalemia)
   - 2.8 [Metabolic Acidosis](#28-metabolic-acidosis)
   - 2.9 [Osteoporosis / Renal Bone Disease](#29-osteoporosis--renal-bone-disease)
   - 2.10 [Infertility](#210-infertility)
   - 2.11 [Malignancy](#211-malignancy)
   - 2.12 [Cardiovascular Disease](#212-cardiovascular-disease)
   - 2.13 [Nephrotic Syndrome Complications](#213-nephrotic-syndrome-complications)
   - 2.14 [Hemorrhagic Cystitis](#214-hemorrhagic-cystitis)
   - 2.15 [Posterior Reversible Encephalopathy Syndrome (PRES)](#215-posterior-reversible-encephalopathy-syndrome-pres)
   - 2.16 [New-Onset Diabetes After Transplant (NODAT)](#216-new-onset-diabetes-after-transplant-nodat)
   - 2.17 [Avascular Necrosis](#217-avascular-necrosis)
   - 2.18 [Infusion Reactions](#218-infusion-reactions)
   - 2.19 [Progressive Multifocal Leukoencephalopathy (PML)](#219-progressive-multifocal-leukoencephalopathy-pml)
   - 2.20 [Tuberculosis Reactivation](#220-tuberculosis-reactivation)
   - 2.21 [Hepatitis B Reactivation](#221-hepatitis-b-reactivation)
   - 2.22 [Cytopenias](#222-cytopenias)
   - 2.23 [Gastrointestinal Toxicity](#223-gastrointestinal-toxicity)
   - 2.24 [Drug-Induced Interstitial Nephritis](#224-drug-induced-interstitial-nephritis)
3. [Appendix A: Complication Prevention by Drug](#3-appendix-a-complication-prevention-by-drug)
4. [Appendix B: Complication Quick Reference](#4-appendix-b-complication-quick-reference)

---

## 1. Introduction

GDES V4.1 maintained per-disease complication lists embedded within individual disease knowledge files. This approach led to fragmentation, redundancy, and inconsistency — each disease module separately described infection risk, thrombosis risk, and AKI without a unified knowledge source.

GDES V4.2 introduces **reusable complication knowledge objects**. This library defines each complication once, with full clinical detail (risk factors, clinical features, prevention, early detection, treatment, monitoring, long-term consequences) and cross-references to all affected diseases and causative drugs. Disease modules reference these objects by complication identifier rather than re-describing them.

### Architectural Principles

1. **Reusability.** Each complication is a self-contained knowledge object linked to multiple disease and drug entities.
2. **Consistency.** All diseases predisposing to infection reference the same infection knowledge object, ensuring uniform prevention and management recommendations.
3. **Maintainability.** Updates to complication knowledge (e.g., new antibiotic prophylaxis guidelines) are made once in this library.
4. **Composability.** Complication prevention strategies compose with drug safety profiles in Appendix A.

### Conventions

- **Disease IDs** are monospaced identifiers (e.g., lupus, iga, membranous) corresponding to entries in the BGDDR disease ontology.
- **Drug references** refer to the Drug Knowledge Library (GDES-V4.2-DRUG-001).
- **Evidence levels** follow GRADE: 1 (strong), 2 (weak/conditional), with A-D letter grades for quality.

---

## 2. Complication Entities

---

### 2.1 Infection

**Complication ID:** COMP-INF-001

#### Risk Factors

- Immunosuppressive therapy (corticosteroids, cyclophosphamide, MMF, rituximab, calcineurin inhibitors, belatacept)
- Nephrotic syndrome (immunoglobulin loss, lymphopenia, oedema fluid)
- CKD/ESKD (uremic immune dysfunction)
- Complement deficiencies (lupus, C3 glomerulopathy consume complement)
- Hypogammaglobulinemia (rituximab-related, nephrotic syndrome)
- Neutropenia (cyclophosphamide, MMF, azathioprine)
- Diabetes mellitus (steroid-induced or pre-existing)
- Indwelling catheters (dialysis access, ureteric stents)
- Transplant status (combined immunosuppression, CMV matching)
- Malnutrition (nephrotic syndrome, advanced CKD)

#### Clinical Features

- **Bacterial:** Fever, chills, focal signs (pneumonia, UTI, cellulitis, peritonitis, sepsis)
- **Viral:** CMV (fever, leucopenia, GI symptoms), BK virus (asymptomatic viruria to nephritis), HSV/VZV (mucocutaneous vesicles, disseminated infection)
- **Fungal:** PJP (subacute dyspnoea, dry cough, hypoxaemia, bilateral interstitial infiltrates), Candida (mucocutaneous, oesophageal, bloodstream), Aspergillus (persistent febrile neutropenia, pulmonary nodules)
- **TB:** Persistent cough, night sweats, weight loss, pleural effusion, lymphadenopathy
- **Atypical:** Nocardia (pulmonary, cerebral abscess), Listeria (meningitis, bacteraemia), Strongyloides (hyperinfection syndrome in transplant recipients)

#### Prevention

- **Vaccination:** Pneumococcal (PCV20, PPSV23), Influenza (annual), COVID-19 (primary + boosters), HBV, HAV, Tdap, VZV (if seronegative pre-transplant). Avoid live vaccines on active immunosuppression
- **PJP prophylaxis:** TMP-SMX (single-strength daily or DS three times weekly) when on corticosteroids >20 mg/day prednisolone equivalent for >4 weeks, post-transplant, or during cyclophosphamide therapy
- **CMV prophylaxis:** Valganciclovir (dose-adjusted for renal function) for D+/R- and high-risk serostatus transplant recipients
- **HBV prophylaxis:** Entecavir or tenofovir for HBsAg+ or anti-HBc+ recipients on rituximab or cyclophosphamide
- **TB screening:** IGRA or TST before commencing anti-TNF therapy, high-dose steroids, or transplant listing
- **Neutropenia precautions:** G-CSF for prolonged neutropenia, antibiotic prophylaxis if ANC <500/mm³
- **Catheter care:** Strict aseptic technique, early removal when feasible
- **Infection control:** Hand hygiene, avoidance of sick contacts, masking in hospital settings

#### Early Detection

- Pre-emptive CMV PCR monitoring (weekly for 3 months post-transplant)
- BK virus PCR screening (monthly for 6-12 months post-transplant)
- Surveillance blood/urine cultures for febrile neutropenia
- Serum galactomannan or beta-D-glucan for invasive aspergillosis in prolonged neutropenia
- IGRA conversion screening in high-risk populations

#### Treatment

- **Bacterial:** Empiric broad-spectrum antibiotics guided by local antibiogram, de-escalate based on culture results. Source control (drainage, line removal)
- **CMV:** Valganciclovir/ganciclovir; foscarnet or cidofovir for resistant cases
- **BK virus:** Reduction of immunosuppression (primary intervention), no approved antiviral
- **PJP:** TMP-SMX (high-dose), alternative: pentamidine, atovaquone, clindamycin-primaquine
- **TB:** Standard 4-drug regimen (RIPE), dose-adjusted for renal function; duration 6 months (extend for CNS or bone involvement)
- **Fungal:** Voriconazole for aspergillosis, fluconazole/echinocandin for candida
- **HSV/VZV:** Acyclovir/valacyclovir

#### Monitoring

- Neutrophil count (weekly during myelosuppressive therapy)
- Immunoglobulin levels (rituximab-treated patients, monitor for hypogammaglobulinemia)
- CMV/BKV PCR per transplant protocol
- Clinical surveillance for infection at every visit
- Chest imaging for persistent respiratory symptoms

#### Long-Term Consequences

- Sepsis and septic shock (mortality 20-40% in immunocompromised)
- Chronic organ dysfunction (post-infectious CKD, bronchiectasis)
- Graft loss (BK virus nephropathy, CMV-associated rejection)
- Antimicrobial resistance (prolonged or repeated antibiotic courses)
- Malignancy risk (EBV-driven PTLD, HPV-related cancers)
- Impaired quality of life, prolonged hospitalisation

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Complement consumption (`c3`/C4 low), functional asplenia, infection leading cause of mortality |
| `mcd` | Moderate | Infection risk primarily during steroid-dependent relapses; hypogammaglobulinemia |
| `membranous` | Moderate | Nephrotic syndrome increases encapsulated organism risk |
| `fsgs` | Moderate | Immunosuppression-related; primary infection risk lower than nephrotic relapse phase |
| `iga` | Low-Moderate | Infection risk primarily from immunosuppression, not disease itself |
| `anca | High | Cyclophosphamide + high-dose steroid combination; PJP prophylaxis essential |
| `antiGbm` | Moderate | Aggressive immunosuppression (PLEX + CyP + steroids) increases risk |
| `c3` | Moderate | Complement pathway dysregulation increases meningococcal risk |
| `diabeticNephropathy` | Moderate | Hyperglycaemia impairs neutrophil function; UTI and foot infections |
| `hivan` | High | Baseline HIV immune compromise compounded by immunosuppression |
| `bkVirusNephropathy` | High | BK virus is the infection; immunosuppression reduction is primary treatment |
| `antibodyMediatedRejection` | High | Intensified immunosuppression (PLEX, IVIG, bortezomib) increases all infection types |
| `tCellMediatedRejection` | High | Pulse steroids + ATG amplifies infection risk |
| `transplantGlomerulopathy` | High | Chronic immunosuppression burden |
| `cniToxicity` | Moderate | CNI-related immune suppression contributes, but primarily drug toxicity |
| `cryoglobulinemic` | Moderate | HCV-related infections; immunosuppression for severe disease |
| `denseDepositDisease` | Moderate | Complement dysregulation, meningococcal risk |
| `mpgn` | Moderate | Dependent on underlying aetiology (HCV, complement, immune complex) |
| `irgn` | Low | Infection is the trigger rather than complication; post-infectious GN |
| `drugInducedGn` | Low-Moderate | Depends on immunosuppressive regimen |
| `fibrillaryGlomerulonephritis` | Moderate | Infection risk from immunosuppression (rituximab, cyclophosphamide) |
| `alport` | Low | Infection risk not increased unless post-transplant |
| 	hinBasementMembrane | Very Low | No intrinsic infection risk |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Prednisolone (>20 mg/day) | High | Global immunosuppression, impaired phagocyte function, lymphopenia |
| Methylprednisolone (pulse) | High | Potent global immunosuppression, lymphodepletion |
| Cyclophosphamide | High | Myelosuppression (neutropenia), lymphodepletion, impaired humoral immunity |
| MMF | High | Inhibits lymphocyte proliferation, impairs T- and B-cell responses |
| Rituximab | High | B-cell depletion, hypogammaglobulinemia, impaired humoral immunity |
| Tacrolimus | Moderate-High | T-cell suppression; CMV/BKV risk in transplant |
| Cyclosporine | Moderate-High | T-cell suppression; similar infection spectrum to tacrolimus |
| Azathioprine | Moderate | Myelosuppression, impaired lymphocyte function |
| Belatacept | High | Blocks T-cell co-stimulation; EBV-seronegative recipients at high PTLD risk |
| mTOR inhibitors (sirolimus, everolimus) | Moderate | Impaired wound healing, lymphocyte inhibition; reduced CMV risk vs CNI |
| Bortezomib | High | Proteasome inhibition, lymphodepletion, increased VZV reactivation |
| Alemtuzumab | High | Profound and prolonged lymphodepletion |
| ATG | High | Profound T-cell depletion, severe lymphopenia |
| Eculizumab | Moderate-High | Terminal complement blockade, meningococcal risk |
| IVIG | Low | Immunoglobulin replacement; infection risk from infusion reactions only |
| Belimumab | Moderate | B-cell inhibition; infection risk lower than rituximab |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. *Kidney Int.* 2024;105(4S):S1-S117
2. KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases. *Kidney Int.* 2021;100(4S):S1-S276
3. KDIGO 2023 Clinical Practice Guideline for the Management of Tuberculosis in CKD and Transplant. *Transplantation.* 2023;107(5):987-1003
4. Fishman JA. Infection in Solid-Organ Transplant Recipients. *N Engl J Med.* 2017;377(23):2267-2279
5. AGIHO Guidelines on Infection Prophylaxis in Immunocompromised Patients. *Ann Hematol.* 2020;99(4):771-788

---
### 2.2 Thrombosis

**Complication ID:** COMP-THR-001

#### Risk Factors

- Nephrotic syndrome (loss of antithrombin III, protein C, protein S; increased fibrinogen, factor VIII)
- Immobilisation (hospitalisation, post-procedure)
- Indwelling central venous catheters (dialysis lines, PICC)
- Vascular access surgery (AV fistula, AV graft)
- Antiphospholipid antibodies (lupus, drug-induced)
- Obesity, smoking, oestrogen therapy
- Malignancy (PTLD, solid organ tumours)
- Dehydration/volume contraction
- Prior VTE history
- Surgery (especially orthopaedic, abdominal, transplant)

#### Clinical Features

- **DVT:** Unilateral calf/thigh swelling, warmth, erythema, tenderness, positive Homan sign
- **PE:** Acute dyspnoea, pleuritic chest pain, haemoptysis, hypoxia, tachycardia, syncope
- **Renal vein thrombosis:** Flank pain, haematuria (gross or microscopic), acute worsening of proteinuria, AKI
- **AVF thrombosis:** Loss of thrill, absent bruit, inability to dialyse, painful swollen access arm
- **Catheter-related thrombosis:** Difficult aspiration, inadequate flow, extremity swelling
- **Cerebral sinus thrombosis:** Headache, papilloedema, seizure, focal neurological deficit

#### Prevention

- Prophylactic anticoagulation for nephrotic syndrome with serum albumin <20 g/L, especially membranous nephropathy (LMWH or warfarin)
- Early mobilisation post-operatively
- Compression stockings for hospitalised patients
- Routine anticoagulation for patients with prior VTE
- AVF patency surveillance (Doppler ultrasound, physical exam)
- Aspirin for AVF patency in non-nephrotic patients
- Avoidance of femoral catheterisation when possible
- Hydration maintenance, avoidance of volume depletion

#### Early Detection

- Regular duplex ultrasound of AVF/grafts (surveillance imaging)
- D-dimer screening (low specificity but high sensitivity in appropriate clinical context)
- Doppler ultrasound for suspected DVT
- CT pulmonary angiography for suspected PE
- CT venography or MR venography for renal vein thrombosis
- Clinical monitoring of chest pain, dyspnoea, leg swelling, access thrill

#### Treatment

- **DVT/PE:** LMWH (enoxaparin 1 mg/kg BID or weight-based) with transition to warfarin (INR 2-3) or DOAC (rivaroxaban, apixaban) if eGFR >30
- **Renal vein thrombosis:** Full anticoagulation as per DVT; consider catheter-directed thrombolysis if bilateral or refractory
- **AVF thrombosis:** Catheter-directed thrombolysis (rt-PA) or surgical thrombectomy within 24-48 hours of occlusion
- **Catheter-related thrombosis:** Catheter removal (if infected or no longer needed); LMWH followed by warfarin
- **Antiphospholipid syndrome:** Lifelong warfarin (INR 2-3 or higher if recurrent); DOACs contraindicated in triple-positive APS
- **Massive PE:** Systemic thrombolysis (alteplase) if haemodynamically unstable
- Duration: minimum 3 months; indefinite if recurrent, APS, ongoing nephrotic syndrome

#### Monitoring

- Anticoagulation monitoring (INR weekly/monthly for warfarin; anti-Xa for LMWH)
- Haemoglobin (occult bleeding surveillance)
- Platelet count (HIT monitoring with heparin products)
- Renal function and electrolytes
- Doppler ultrasound for AVF patency post-thrombectomy
- Symptom surveillance (dyspnoea, leg swelling, access dysfunction)

#### Long-Term Consequences

- Post-thrombotic syndrome (chronic leg pain, swelling, ulceration)
- Chronic thromboembolic pulmonary hypertension (after PE)
- AVF/graft loss necessitating new access creation
- Anticoagulation-related bleeding (GI, intracranial, retroperitoneal)
- Recurrent VTE in persisting nephrotic syndrome or APS
- Renal atrophy post-renal vein thrombosis

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `membranous` | High (5-20%) | Highest VTE risk among primary GN; albumin <20 g/L is major predictor |
| `mcd` | Low-Moderate | Thrombosis risk during nephrotic relapse; lower than `membranous` |
| `fsgs` | Moderate | Risk correlates with nephrotic severity; higher in collapsing variant |
| `lupus` | High | APS co-existence (30-40%); arterial plus venous thrombosis |
| `iga` | Low | Thrombosis rare unless nephrotic-range proteinuria or APS |
| `anca | Moderate | Thrombosis risk from inflammatory state and nephrotic syndrome |
| `antiGbm | Low-Moderate | Aggressive treatment partly mitigates risk through inflammation control |
| `cryoglobulinemic` | Moderate | Cryoglobulin-induced hyperviscosity and vasculitis contribute |
| `diabeticNephropathy` | Moderate | Hypercoagulable state from DM itself plus nephrotic-range proteinuria |
| `c3` | Low-Moderate | Risk correlates with nephrotic syndrome severity |
| `denseDepositDisease` | Low-Moderate | Similar to `c3` glomerulopathy |
| `hivan` | Moderate | HIV-related hypercoagulability plus nephrotic syndrome |
| `transplantGlomerulopathy` | Low | Thrombosis not a dominant feature; vascular access issues predominate |
| `antibodyMediatedRejection` | Low | Thrombosis risk from acute inflammation and CVC/access |
| `tCellMediatedRejection` | Low | Thrombosis risk primarily from CVC and peri-transplant factors |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Oestrogen-containing contraceptives | High | Prothrombotic effect (increased factor VII, decreased protein S) |
| EPO (erythropoietin) | Moderate | Increased haematocrit, increased blood viscosity |
| Glucocorticoids | Moderate | Increased factor VIII and fibrinogen; dose-dependent |
| Thalidomide/lenalidomide | High | Increased VTE risk, especially with steroids |
| IVIG | Low-Moderate | Hyperviscosity syndrome at high doses |
| Calcineurin inhibitors | Moderate | Endothelial dysfunction, increased platelet aggregation |
| Belatacept | Low | Lower thrombosis risk compared to CNI in transplant |
| mTOR inhibitors | Low-Moderate | Endothelial effects, wound healing; lower VTE risk than CNI |
| Rituximab | Low | Rare infusion-related thrombotic events |

#### Guideline References

1. KDIGO 2021 Glomerular Disease Guideline Chapter 3 (Membranous Nephropathy). *Kidney Int.* 2021;100(4S):S1-S276
2. Glassock RJ. Prophylactic Anticoagulation in Nephrotic Syndrome. *J Am Soc Nephrol.* 2017;28(5):1342-1347
3. Barbour SJ et al. Disease-Specific Anticoagulation in Membranous Nephropathy. *CJASN.* 2022;17(3):388-397
4. ASN Clinical Practice Guideline on Anticoagulation in CKD. *J Am Soc Nephrol.* 2023;34(8):1320-1342

---
### 2.3 Venous Thromboembolism (Nephrotic Syndrome)

**Complication ID:** COMP-VTE-001

#### Risk Factors

- Nephrotic syndrome with serum albumin <25 g/L (especially <20 g/L)
- Membranous nephropathy (highest risk among primary GN)
- Heavy proteinuria (>10 g/day)
- Prolonged nephrotic state (>3 months)
- Immobilisation due to hospitalisation or oedema-related immobility
- Prior VTE history
- Obesity (BMI >30)
- Malignancy (especially in membranous nephropathy secondary to solid tumours)
- Central venous catheters
- Surgery (biopsy, transplant, access creation)
- Dehydration (loop diuretic overuse)
- Antiphospholipid antibodies (30-40% of lupus nephritis)

#### Clinical Features

- **DVT:** Unilateral leg swelling, warmth, erythema, palpable cord
- **PE:** Acute-onset dyspnoea, pleuritic chest pain, haemoptysis, hypoxia, tachypnoea, tachycardia
- **Renal vein thrombosis:** Flank pain, macroscopic haematuria, worsening proteinuria, AKI (if bilateral)
- **IVC thrombosis:** Bilateral leg swelling, dilated abdominal veins, hypotension
- **Pulmonary infarction:** Haemoptysis, pleuritic pain, radiographic wedge-shaped opacity

#### Prevention

- Assess VTE risk in all nephrotic syndrome patients at diagnosis
- Prophylactic LMWH (enoxaparin 40 mg SC daily) when albumin <20 g/L, especially in membranous nephropathy
- Warfarin (INR 2-3) for patients with albumin <20 g/L AND additional risk factor (prior VTE, BMI >30, immobilisation)
- DOACs (apixaban, rivaroxaban) emerging as alternatives but limited data in nephrotic syndrome
- Avoid prolonged immobilisation; encourage ambulation as tolerated
- Maintain euvolemia; avoid overdiuresis
- Compression stockings for lower extremity oedema
- Minimise central venous catheter use

#### Early Detection

- High index of suspicion for VTE in nephrotic patients with any cardiorespiratory symptom
- D-dimer testing (interpret with caution; elevated in nephrotic syndrome even without VTE)
- Duplex ultrasound for leg symptoms
- CT pulmonary angiography for suspected PE (consider CTPA even with mild dyspnoea)
- MR venography for suspected renal vein thrombosis (non-contrast option for CKD)
- Serial albumin monitoring as predictor; rapid decline raises concern

#### Treatment

- **Initial:** LMWH (enoxaparin 1 mg/kg BID) or unfractionated heparin with anti-Xa monitoring
- **Transition:** Warfarin (INR 2-3); overlap with LMWH for 5 days until therapeutic
- **DOACs:** Rivaroxaban 20 mg daily or apixaban 5 mg BID if eGFR >30; emerging evidence in nephrotic syndrome
- **Duration:** Minimum 3 months; continue while nephrotic syndrome persists or indefinitely if recurrent
- **Massive PE:** Systemic thrombolysis if haemodynamically unstable
- **Recurrent VTE on therapeutic anticoagulation:** Switch to LMWH (if warfarin failure) or consider IVC filter (controversial in nephrotic syndrome)
- Treat underlying nephrotic syndrome (immunosuppression to induce remission)

#### Monitoring

- Anticoagulation intensity (INR for warfarin, anti-Xa for LMWH)
- Albumin and proteinuria trends (remission reduces VTE risk)
- Haemoglobin, renal function during anticoagulation
- Clinical surveillance for bleeding (epistaxis, bruising, GI bleeding, haematuria)
- Imaging follow-up at 3-6 months for DVT/PE to assess resolution

#### Long-Term Consequences

- Post-thrombotic syndrome (chronic venous insufficiency, leg ulceration)
- Chronic thromboembolic pulmonary hypertension (CTEPH) after PE
- Anticoagulant-related major bleeding (1-3% per year)
- Recurrent thrombosis if underlying nephrotic syndrome persists
- AVF/graft loss if access thrombosis occurs
- Renal atrophy from renal vein thrombosis

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `membranous` | High (20-40%) | Highest risk; renal vein thrombosis is characteristic; anti-PLA2R+ carries additional risk |
| `mcd` | Low-Moderate | Risk limited to nephrotic relapses; low cumulative risk |
| `fsgs` | Moderate | Risk correlates with proteinuria severity; collapsing variant higher risk |
| `lupus` | Moderate | APS co-morbidity amplifies risk; both VTE and arterial thrombosis |
| `iga` | Low | VTE rare unless nephrotic transformation |
| `anca | Low-Moderate | Inflammation contributes; nephrotic-range proteinuria uncommon |
| `diabeticNephropathy` | Moderate | DM hypercoagulability + nephrotic syndrome |
| `c3` | Low-Moderate | Risk parallels nephrotic severity |
| `cryoglobulinemic` | Low-Moderate | Cryoglobulin-related hyperviscosity |
| `amyloid | Moderate | AL amyloidosis with nephrotic syndrome; bleeding risk also increased |
| `hivan` | Low-Moderate | HIV-related hypercoagulability + nephrotic syndrome |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Oestrogen therapy | High | Increases prothrombotic factors; contraindicated in nephrotic syndrome |
| EPO | Moderate | Increased haematocrit, hyperviscosity |
| High-dose corticosteroids | Moderate | Increased clotting factors |
| Loop diuretics (excessive) | Low-Moderate | Haemoconcentration, volume contraction |
| Immunosuppressive therapy (indirect) | Low | By inducing remission, reduces VTE risk |

#### Guideline References

1. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
2. Lionaki S et al. Venous Thromboembolism in Membranous Nephropathy. *J Am Soc Nephrol.* 2016;27(10):3128-3135
3. Lee T et al. DOACs in Nephrotic Syndrome. *Kidney Int Rep.* 2023;8(3):485-496
4. Glassock RJ. Prophylactic Anticoagulation in Nephrotic Syndrome. *J Am Soc Nephrol.* 2017;28(5):1342-1347

---
### 2.4 Acute Kidney Injury

**Complication ID:** COMP-AKI-001

#### Risk Factors

- **Drug-induced:** RAASi initiation/dose escalation, SGLT2i (volume depletion), diuretics (overdiuresis), NSAIDs (afferent vasoconstriction), contrast media, aminoglycosides, amphotericin B, tenofovir, vancomycin, calcineurin inhibitors (CNI nephrotoxicity)
- **Disease flare:** Rapidly progressive GN (crescentic IgA, lupus class III/IV, ANCA vasculitis, anti-GBM), nephrotic syndrome relapse with haemodynamic AKI
- **Prerenal:** Diarrhoea/vomiting (gastroenteritis, MMF-related), overdiuresis, sepsis, haemorrhage, cardiac failure, hypoalbuminaemia (reduced effective arterial volume)
- **Intrinsic renal:** Acute tubular necrosis (sepsis, ischaemia, nephrotoxins), acute interstitial nephritis (drug-induced, infection), thrombotic microangiopathy (lupus, aHUS, scleroderma renal crisis), acute CNI nephrotoxicity
- **Postrenal:** Ureteric obstruction (stones, retroperitoneal fibrosis, transplant ureteric stenosis), bladder outlet obstruction (prostatic hypertrophy, neurogenic bladder)
- **Pre-existing CKD:** Lower renal reserve amplifies risk from any insult
- **Hypoalbuminaemia:** Reduced effective arterial blood volume in nephrotic syndrome
- **Sepsis:** Most common cause of AKI in hospitalised patients

#### Clinical Features

- Oliguria (urine output <0.5 mL/kg/h for >6 hours) or anuria
- Rising serum creatinine (increase of >=0.3 mg/dL in 48 h or >=1.5x baseline)
- Hyperkalaemia, metabolic acidosis, fluid overload (pulmonary oedema, peripheral oedema)
- Uraemic symptoms (nausea, fatigue, encephalopathy, pericarditis) in severe cases
- Drug-specific: CNI toxicity (tremor, hypertension, hyperkalaemia), NSAID toxicity (salt/water retention, hyperkalaemia)
- Disease-specific: Crescentic GN (haematuria, red cell casts, proteinuria), TMA (microangiopathic haemolytic anaemia, thrombocytopenia)

#### Prevention

- Volume status optimisation before RAASi or SGLT2i initiation
- NSAID avoidance in all CKD patients (eGFR <30 or proteinuric disease)
- Appropriate contrast media use: lowest volume, iso-osmolar agents, pre-hydration
- Diuretic dose individualisation; careful monitoring of fluid balance
- Therapeutic drug monitoring of CNI trough levels
- Strict blood pressure targets avoiding hypotension (MAP >65 mmHg)
- Avoidance of nephrotoxin combinations (CNI + NSAID + diuretic triple whammy)
- Treat underlying disease aggressively to prevent flares
- Infection prevention (reduce sepsis-related AKI)
- Peri-operative hydration and avoidance of hypotension during transplant surgery

#### Early Detection

- Serial serum creatinine monitoring (daily during acute illness, weekly during therapy induction)
- Urine output measurement (hourly in ICU, daily in ward)
- Urine sediment examination (red cell casts indicate glomerulonephritis; muddy brown casts indicate ATN; white cell casts indicate interstitial nephritis)
- Fractional excretion of sodium (FENa <1% = prerenal, >2% = intrinsic AKI)
- Urine albumin-to-creatinine ratio (sudden increase suggests flare)
- Renal ultrasound to exclude obstruction
- CNI trough levels (tacrolimus target 5-10 ng/mL, cyclosporine 100-200 ng/mL)
- Early biomarker testing (NGAL, KIM-1) where available

#### Treatment

- **Prerenal:** Volume repletion (crystalloids), hold diuretics, treat underlying cause
- **Drug-induced AKI:** Withdraw offending agent; RAASi hold until volume replete and stable
- **CNI toxicity:** Dose reduction; consider switch to belatacept or mTOR inhibitor
- **Acute interstitial nephritis:** Drug withdrawal; corticosteroids if severe (prednisolone 0.5-1 mg/kg/day)
- **Crescentic GN/vasculitis:** Pulse methylprednisolone (500-1000 mg x 3), cyclophosphamide or rituximab, plasma exchange if anti-GBM or severe ANCA
- **TMA:** Plasma exchange (aHUS), eculizumab (aHUS with complement mutation), immunosuppression reduction (drug-induced TMA)
- **Postrenal:** Urinary catheter, nephrostomy, ureteric stent, treat obstruction aetiology
- **Fluid overload:** Loop diuretics (frusemide IV), ultrafiltration/haemodialysis if refractory
- **RRT indication:** Refractory hyperkalaemia, metabolic acidosis, fluid overload, uraemic symptoms, severe overdose

#### Monitoring

- Daily creatinine and electrolytes during acute episode
- Urine output trends (goal >0.5 mL/kg/h)
- Fluid balance chart
- Drug levels (CNIs, vancomycin, aminoglycosides)
- Acid-base status (venous bicarbonate, ABG if severe)
- Renal recovery trajectory (creatinine trending toward baseline)
- Blood pressure (avoid hypotension and hypertension extremes)
- Weight (daily) for fluid status assessment
- Indications for RRT escalation or cessation

#### Long-Term Consequences

- Incomplete renal recovery (new baseline higher creatinine)
- Progression of underlying CKD (accelerated eGFR decline)
- ESKD requiring chronic dialysis (especially if AKI on CKD)
- Episode-associated mortality (sepsis-AKI, hospital-acquired AKI)
- Hypertension development or worsening
- Permanent RRT dependence if bilateral renal vein thrombosis or cortical necrosis
- Increased cardiovascular risk post-AKI
- Drug intolerance after AKI (reduced clearance)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | `lupus` nephritis flare (Class III/IV) is common cause; TMA in APS overlap |
| `anca | High | Rapidly progressive GN is presenting feature; dialysis required in 20-30% |
| `antiGbm | Very High | Crescentic GN in >90%; many require acute dialysis at presentation |
| `iga` | Moderate | Crescentic IgA with AKI; less common than ANCA/anti-GBM |
| `membranous` | Moderate | Superimposed ATN from nephrotic syndrome; CNI toxicity; renal vein thrombosis |
| `mcd` | Moderate | AKI in adults > children; haemodynamic from nephrotic syndrome; ATN |
| `fsgs` | Moderate | AKI from aggressive disease or CNI toxicity; collapsing variant |
| `diabeticNephropathy` | High | Contrast nephropathy, diuretic overuse, sepsis, drug-induced AKI |
| `cniToxicity` | High | CNI is direct cause of AKI; dose-dependent |
| `c3` | Moderate | AKI from disease activity or infection |
| `cryoglobulinemic` | Moderate | Cryoglobulin-induced vasculitis causing AKI |
| `denseDepositDisease` | Moderate | AKI similar to `c3` glomerulopathy |
| `irgn` | Low-Moderate | AKI common in post-infectious GN but usually self-limiting |
| `bkVirusNephropathy` | High | BK nephritis directly causes AKI and graft dysfunction |
| `antibodyMediatedRejection` | High | Acute ABMR presents with AKI and graft dysfunction |
| `tCellMediatedRejection` | High | Acute TCMR with rising creatinine and AKI |
| `transplantGlomerulopathy` | Low | Insidious onset; AKI is late feature |
| `drugInducedGn` | Moderate | Drug withdrawal often reverses AKI |
| `hivan` | High | HIVAN + sepsis + drug toxicity combine |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| NSAIDs | High | Afferent arteriolar vasoconstriction, reduced GFR |
| RAASi (ACEi/ARB) | Moderate | Reduced efferent arteriolar tone, especially if volume depleted |
| SGLT2i | Low-Moderate | Volume depletion, rare eGFR dip (usually transient) |
| Calcineurin inhibitors (tacrolimus, cyclosporine) | High | Afferent arteriolar vasoconstriction, acute CNI nephrotoxicity |
| IV contrast | Moderate | Contrast-induced nephropathy (osmotic, toxic) |
| Aminoglycosides | High | Direct tubular toxicity, accumulates in proximal tubule |
| Amphotericin B | High | Tubular toxicity, vasoconstriction |
| Vancomycin | Moderate | Tubular toxicity, especially with trough >20 mcg/mL |
| Tenofovir (TDF) | Moderate | Proximal tubular toxicity, Fanconi syndrome |
| Cisplatin | High | Direct tubular toxicity |Piperacillin-tazobactam | Low-Moderate | Rare AKI, interstitial nephritis |
| Proton pump inhibitors | Low | Chronic interstitial nephritis with prolonged use |
| Loop diuretics (excessive) | Moderate | Volume depletion, prerenal AKI |

#### Guideline References

1. KDIGO 2012 Clinical Practice Guideline for Acute Kidney Injury. *Kidney Int Suppl.* 2012;2(1):1-138
2. KDIGO 2024 CKD Guideline. *Kidney Int.* 2024;105(4S):S1-S117
3. Kidney Disease: Improving Global Outcomes (KDIGO) Acute Kidney Injury Work Group. KDIGO Clinical Practice Guideline for Acute Kidney Injury. *Kidney Int Suppl.* 2012;2(1):1-138
4. Palevsky PM et al. KDOQI US Commentary on the 2012 KDIGO Clinical Practice Guideline for Acute Kidney Injury. *Am J Kidney Dis.* 2013;61(5):649-672

---
### 2.5 CKD Progression

**Complication ID:** COMP-CKD-001

#### Risk Factors

- Persistent proteinuria (>1 g/day, especially nephrotic-range)
- Hypertension (poorly controlled, >130/80 mmHg)
- Hyperglycaemia (diabetic nephropathy, steroid-induced diabetes)
- Recurrent disease flares (lupus, ANCA, IgA)
- Acute kidney injury episodes (accelerate eGFR decline)
- Nephrotoxin exposure (NSAIDs, contrast, CNI)
- Smoking, obesity, dyslipidaemia
- Genetic susceptibility (APOL1 high-risk variants)
- Non-adherence to renoprotective therapy (RAASi, SGLT2i)
- Prolonged nephrotic syndrome (podocyte depletion)
- Chronic CNI nephrotoxicity (transplant patients)
- Recurrent or resistant rejection episodes
- BK virus nephropathy (transplant)
- Delayed graft function (transplant)

#### Clinical Features

- Gradual rise in serum creatinine over months to years
- Decline in eGFR (slope >=3-5 mL/min/1.73m²/year is rapid progression)
- Worsening proteinuria (quantified by UPCR or ACR trends)
- Rising blood pressure over time
- Progressive anaemia (decreased erythropoietin production)
- Rising PTH (secondary hyperparathyroidism)
- Metabolic acidosis (low serum bicarbonate)
- Hyperphosphataemia, hypocalcaemia (late stages)
- Uraemic symptoms (nausea, fatigue, pruritus, anorexia) in advanced CKD
- Accelerated cardiovascular disease (parallel progression)

#### Prevention

- Maximise RAASi therapy (ACEi/ARB to maximum tolerated dose)
- Add SGLT2i (dapagliflozin, empagliflozin) for proteinuric CKD
- Strict blood pressure control (target <130/80 mmHg, <120/75 if proteinuria >1 g/day)
- Glycaemic control in diabetic patients (HbA1c target 7%)
- Avoid nephrotoxins (NSAIDs, contrast, herbal nephrotoxins)
- Dietary protein restriction (0.8 g/kg/day in CKD G3-4)
- Sodium restriction (<2 g/day, <5 g salt)
- Disease-specific immunosuppression to maintain remission
- Smoking cessation, weight management, exercise
- CNI minimization protocols in transplant recipients
- Metabolic acidosis correction (sodium bicarbonate)
- Hyperuricaemia management (allopurinol, febuxostat)

#### Early Detection

- Serial eGFR monitoring (frequency based on CKD stage: G1-2 annually, G3a 6-monthly, G3b 3-monthly, G4 3-monthly, G5 monthly)
- Proteinuria quantification (UPCR or ACR every 3-6 months)
- eGFR slope calculation (annual assessment of rate of decline)
- Cystatin C for more accurate GFR estimation in early CKD
- Renal ultrasound (assess for obstruction, cystic change, size loss)
- Serial biopsies for transplant patients (surveillance or indication)
- BK virus PCR surveillance post-transplant
- Donor-specific antibody monitoring (post-transplant)

#### Treatment

- Optimise renoprotective pharmacotherapy (RAASi + SGLT2i + finerenone if diabetic)
- Intensive blood pressure management (multi-drug regimen as needed)
- Disease-specific immunotherapy (rituximab, MMF, cyclophosphamide for active GN)
- Dietary modification (low protein, low sodium)
- Metabolic acidosis correction (sodium bicarbonate, citrate)
- Anaemia management (ESAs, iron)
- CKD-MBD management (phosphate binders, vitamin D, calcimimetics)
- Cardiovascular risk reduction (statin, aspirin where indicated)
- Patient education on medication adherence and lifestyle
- Prepare for RRT (AVF creation, transplant evaluation, modality education)
- Dialysis initiation when eGFR <15 + uraemic symptoms or refractory complications

#### Monitoring

- eGFR and proteinuria every 3-6 months (more frequent in rapid progressors)
- Blood pressure at every visit (home BP monitoring encouraged)
- Serum potassium, bicarbonate (monthly in advanced CKD)
- Haemoglobin, iron studies (quarterly in G4-5)
- Calcium, phosphate, PTH, vitamin D (quarterly in G3b-5)
- HbA1c (quarterly in diabetic patients)
- Lipid profile (annually)
- Nutritional status (albumin, prealbumin, weight, dietary assessment)
- Medication adherence assessment at every visit
- RRT readiness checklist by G4

#### Long-Term Consequences

- ESKD requiring dialysis or transplantation
- Accelerated cardiovascular morbidity and mortality
- Reduced quality of life and functional status
- Cognitive decline (uraemic encephalopathy)
- Frailty and sarcopenia
- Increased hospitalisation rates
- Anaemia requiring ESA therapy
- CKD-MBD with bone pain and fractures
- Fluid overload and heart failure
- Electrolyte derangements (hyperkalaemia, metabolic acidosis)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `diabeticNephropathy` | Very High | Leading cause of ESKD worldwide; progression predictable by eGFR slope |
| `lupus` | Moderate-High | Progression related to `lupus` flares; chronic damage from Class III/IV disease |
| `iga` | Moderate | 30-40% progress to ESKD over 20-30 years; Oxford MEST-C score predicts risk |
| `fsgs | Moderate-High | 50% progress to ESKD over 5-10 years; collapsing variant most aggressive |
| `membranous` | Moderate | 30-40% spontaneous remission; 30-40% progress to ESKD over 10 years |
| `mcd` | Low | Rarely progresses to ESKD unless steroid-resistant or adult onset |
| `anca | Moderate-High | 20-30% reach ESKD; relapse-driven progression |
| `antiGbm` | Moderate | Prognosis determined by presenting creatinine; those who recover often stable |
| `alport | High | Progressive course; ESKD by 20-40 in XLAS males; RAASi slows but does not halt |
| `c3` | Moderate-High | Variable progression; DDD has worse prognosis than `c3`GN |
| `cryoglobulinemic` | Moderate | Relapse-driven progression; antiviral therapy improves outcomes |
| `denseDepositDisease` | High | Most progress to ESKD; limited treatment options |
| `fibrillaryGlomerulonephritis` | Moderate | 50% progress to ESKD over 5 years |
| `hivan` | Moderate-High | ART reduces but does not eliminate progression risk |
| `bkVirusNephropathy` | High | Major cause of graft loss post-transplant |
| `antibodyMediatedRejection` | High | Leading cause of late graft loss |
| `tCellMediatedRejection` | Moderate | Acute TCMR associated with subsequent CKD progression |
| `transplantGlomerulopathy` | High | Rapid progression to graft loss; limited effective therapy |
| `cniToxicity` | Moderate | Chronic CNI nephrotoxicity slowly reduces graft function |
| 	hinBasementMembrane | Very Low | Benign; progression to ESKD rare unless co-existing disease |
| `drugInducedGn` | Low-Moderate | Usually reversible on drug withdrawal; chronic damage if prolonged exposure |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| NSAIDs | High | Reduced renal blood flow, papillary necrosis with chronic use |
| Calcineurin inhibitors | Moderate-High | Chronic nephrotoxicity (arteriolar hyalinosis, interstitial fibrosis) |
| Tenofovir (TDF) | Moderate | Proximal tubular toxicity, Fanconi syndrome |
| Aminoglycosides | Moderate | Cumulative tubular damage |
| IV contrast | Low-Moderate | Contrast-induced AKI accelerates CKD |
| Lithium | Moderate | Chronic interstitial nephritis, nephrogenic diabetes insipidus |
| Proton pump inhibitors | Low-Moderate | Chronic interstitial nephritis (long-term use) |
| Chemotherapy (cisplatin, ifosfamide) | High | Permanent tubular damage |
| Herbal nephrotoxins (aristolochic acid) | High | Rapidly progressive interstitial fibrosis |
| Renoprotective drugs (RAASi, SGLT2i, finerenone) | Protective | Slow eGFR decline (therapeutic) |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. *Kidney Int.* 2024;105(4S):S1-S117
2. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
3. Stevens PE et al. Evaluation and Management of Chronic Kidney Disease: Synopsis of the Kidney Disease: Improving Global Outcomes 2024 Clinical Practice Guideline. *Ann Intern Med.* 2024;177(4):511-522
4. Heerspink HJL et al. Slowing CKD Progression: From Clinical Trials to Clinical Practice. *Nat Rev Nephrol.* 2023;19(6):363-379

---
### 2.6 Hypertension

**Complication ID:** COMP-HTN-001

#### Risk Factors

- Renal parenchymal disease (any CKD, especially glomerular disease)
- Renovascular disease (atherosclerotic renal artery stenosis, fibromuscular dysplasia)
- Volume overload (nephrotic syndrome, CKD G4-5, dialysis-dependent)
- RAAS activation (renin-angiotensin-aldosterone system in CKD)
- CNI therapy (tacrolimus, cyclosporine — vasoconstriction, sodium retention)
- Corticosteroid therapy (mineralocorticoid effect, sodium retention)
- EPO therapy (increased haematocrit, increased viscosity)
- Obesity, metabolic syndrome
- High sodium intake
- Obstructive sleep apnoea
- Older age, family history
- Black race (APOL1-associated)

#### Clinical Features

- Asymptomatic (most common — detected on routine BP measurement)
- Headache (occipital, morning, throbbing)
- Visual disturbances (blurred vision, scotomata)
- Epistaxis
- Dyspnoea on exertion (if LV dysfunction develops)
- Chest pain (hypertensive urgency/emergency)
- Neurological symptoms (dizziness, tinnitus, encephalopathy in malignant phase)
- Signs of target organ damage: LVH on ECG/echo, retinopathy (AV nicking, silver wiring, papilloedema)
- **Renovascular:** Abdominal bruit, flash pulmonary oedema, differential renal size
- **Malignant hypertension:** BP >180/120 + papilloedema, encephalopathy, AKI, TMA

#### Prevention

- Maintain optimal BP targets (<130/80 mmHg for all CKD; <125/75 if proteinuria >1 g/day)
- Sodium restriction (<2 g/day)
- Regular aerobic exercise (150 min/week moderate intensity)
- Healthy diet (DASH diet, high fruit/vegetable intake)
- Weight management (BMI target <25)
- Limit alcohol (<2 drinks/day men, <1 drink/day women)
- Smoking cessation
- Minimise CNI trough levels (tacrolimus 5-8 ng/mL, cyclosporine 75-150 ng/mL)
- Avoid excessive steroid doses and prolonged courses
- Address secondary causes (sleep apnoea, renovascular disease)
- Medication adherence support

#### Early Detection

- Home blood pressure monitoring (HBPM) — gold standard for CKD patients
- 24-hour ambulatory BP monitoring (ABPM) for confirmation and to exclude white-coat HTN
- Regular clinic BP measurement at every visit (standardised technique)
- Fundoscopy for hypertensive retinopathy
- ECG for LVH detection
- Echocardiography if LVH suspected
- Renal duplex ultrasound for renovascular disease
- Plasma renin/aldosterone ratio for secondary causes

#### Treatment

- **First-line:** RAASi (ACEi or ARB) — preferred for proteinuric CKD; titrate to maximum tolerated dose
- **Second-line:** Calcium channel blocker (amlodipine, nifedipine) or thiazide/thiazide-like diuretic
- **Third-line:** Beta-blocker (especially if CAD, HF), mineralocorticoid antagonist (spironolactone, finerenone)
- **Fourth-line:** Alpha-blocker, hydralazine, minoxidil, centrally acting agents
- **Resistant HTN (>=4 agents including diuretic):** Evaluate for secondary causes; consider spironolactone if K+ normal
- **Malignant HTN:** IV antihypertensives (labetalol, nicardipine); target 25% reduction over first 24h
- **Transplant HTN:** CNI dose reduction if feasible; CCB preferred (counteracts CNI vasoconstriction)
- Target BP: <130/80 mmHg (KDIGO 2024); <120/75 if proteinuria >1 g/day

#### Monitoring

- Clinic BP at every visit (home BP diary for remote monitoring)
- Serum creatinine and potassium within 1-2 weeks of RAASi initiation or dose change
- eGFR trajectory (accelerated decline suggests renovascular disease)
- Proteinuria response (RAASi typically reduces by 30-40%)
- Electrolytes (K+, Na+, bicarbonate) especially with RAASi + potassium-sparing diuretics
- CNI trough levels (if applicable)
- ECG for LVH annually
- Echocardiogram if clinical suspicion of HF
- Fundoscopy for hypertensive changes

#### Long-Term Consequences

- Cardiovascular disease (MI, stroke, HF)
- Accelerated CKD progression
- LVH and diastolic dysfunction
- Hypertensive retinopathy and vision loss
- Cerebrovascular disease (stroke, vascular dementia)
- Peripheral arterial disease
- Aortic dissection (in malignant hypertension)
- Increased mortality (cardiovascular and all-cause)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `diabeticNephropathy` | Very High | Hypertension present in >80%; RAASi + SGLT2i + finerenone triple therapy |
| `lupus` | High | CNI use (tacrolimus, cyclosporine) exacerbates; also renovascular from vasculitis |
| `iga` | High | Present in 30-50% at diagnosis; independent predictor of progression |
| `fsgs | High | Hypertension common, often resistant |
| `membranous` | Moderate | Present in 30-40%; CNI for treatment amplifies HTN |
| `mcd` | Low-Moderate | Usually resolves with remission; steroid-induced during treatment |
| `anca | Moderate | HTN from renal damage and steroid therapy |
| `antiGbm` | Moderate | Residual HTN after acute phase |
| `cniToxicity` | Very High | CNI-induced HTN is dose-dependent and characteristic |
| `alport | Moderate | Earlier onset in XLAS males; ACEi first line |
| `c3` | Moderate | HTN correlates with CKD stage |
| `cryoglobulinemic` | Moderate | Vasculitis-mediated and steroid-induced |
| `hivan` | Moderate | ART and HIV-related HTN |
| `antibodyMediatedRejection` | High | Steroid pulses and CNI maintenance contribute |
| `bkVirusNephropathy` | Moderate | HTN from graft dysfunction |
| `tCellMediatedRejection` | Moderate | Steroid pulse therapy |
| `transplantGlomerulopathy` | High | CNI nephrotoxicity + graft dysfunction |
| 	hinBasementMembrane | Very Low | No intrinsic association |
| `drugInducedGn` | Moderate | Steroid and CNI contributions |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Calcineurin inhibitors (tacrolimus, cyclosporine) | High | Afferent arteriolar vasoconstriction, sodium retention, sympathetic activation |
| Corticosteroids (prednisolone >10 mg/day) | Moderate-High | Mineralocorticoid receptor activation, sodium retention |
| EPO | Moderate | Increased haematocrit, increased viscosity |
| NSAIDs | Moderate | Sodium retention, increased peripheral resistance |
| Oestrogen-containing contraceptives | Moderate | Increased renin substrate, sodium retention |
| Alcohol (excessive) | Moderate | Sympathetic activation, endothelial dysfunction |
| Decongestants (pseudoephedrine) | Low-Moderate | Alpha-adrenergic vasoconstriction |
| MAOIs (antidepressants) | Low | Tyramine interaction, sympathetic activation |
| Renoprotective drugs (RAASi) | Protective | Antihypertensive effect (therapeutic) |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Management of Blood Pressure in CKD. *Kidney Int.* 2024;105(4S):S1-S117
2. Whelton PK et al. 2017 ACC/AHA Hypertension Guideline. *J Am Coll Cardiol.* 2018;71(19):e127-e248
3. Williams B et al. 2018 ESC/ESH Guidelines for the Management of Arterial Hypertension. *Eur Heart J.* 2018;39(33):3021-3104
4. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276

---
### 2.7 Hyperkalemia

**Complication ID:** COMP-K-001

#### Risk Factors

- CKD G3-G5 (reduced renal K+ excretion)
- RAASi therapy (ACEi/ARB — reduced aldosterone-mediated K+ secretion)
- Mineralocorticoid antagonists (spironolactone, finerenone, eplerenone)
- CNI therapy (tacrolimus, cyclosporine — downregulated K+ secretion)
- SGLT2i (early therapy, mild K+ reduction overall — net protective)
- High potassium diet (fruits, vegetables, salt substitutes)
- Metabolic acidosis (extracellular shift of K+)
- Hyporeninaemic hypoaldosteronism (type IV RTA, diabetic nephropathy)
- Volume depletion (reduced distal sodium delivery)
- NSAIDs (reduced renin, hyporeninaemic hypoaldosteronism)
- Beta-blockers (reduced beta-2 receptor-mediated cellular K+ uptake)
- Haemolysis, tumour lysis syndrome, rhabdomyolysis
- Blood transfusions, K+ containing IV fluids
- Advanced age, diabetes mellitus, heart failure

#### Clinical Features

- Usually asymptomatic until severe (>6.5 mEq/L)
- Muscle weakness (ascending, flaccid paralysis)
- Paraesthesias (perioral, acral)
- Palpitations, presyncope, syncope
- ECG changes (peaked T waves, widened QRS, loss of P wave, sine wave — ventricular fibrillation)
- Cardiac arrest (typically from ventricular fibrillation or asystole)
- Bradycardia, hypotension in severe cases
- Nausea, vomiting, abdominal pain

#### Prevention

- K+ monitoring 1-2 weeks after RAASi initiation or dose escalation
- Avoid high-K+ diet during RAASi therapy (educate patients)
- Avoid K+-sparing diuretics + RAASi combination unless closely monitored
- Avoid NSAIDs during RAASi therapy
- Maintain euvolemia (adequate distal tubular flow for K+ secretion)
- Correct metabolic acidosis with sodium bicarbonate
- Minimise CNI doses; monitor trough levels
- Use SGLT2i (mild K+-lowering effect, reduces hyperkalaemia risk)
- Consider potassium binders (patiromer, sodium zirconium cyclosilicate) for chronic management in high-risk patients
- Ensure adequate stool output (avoid opioid-induced constipation)
- Hold RAASi temporarily during intercurrent illness

#### Early Detection

- Serum K+ monitoring (frequency per CKD stage and risk: monthly in G4-5, 1-2 weeks post-RAASi change)
- ECG for K+ >6.0 mEq/L or rapidly rising
- Home K+ monitoring devices (emerging technology)
- Check metabolic panel at every visit in advanced CKD
- Screening for hypoaldosteronism in diabetic patients on RAASi
- Ammonium chloride loading test (acid loading) to assess distal K+ secretion capacity

#### Treatment

- **Mild (5.5-6.0 mEq/L), asymptomatic:** Dietary K+ restriction, hold problem medications, correct acidosis, consider K+ binder
- **Moderate (6.0-6.5 mEq/L), no ECG changes:** IV calcium gluconate (cardioprotection) + insulin/dextrose + albuterol nebulised + sodium bicarbonate (if acidotic)
- **Severe (>6.5 mEq/L or ECG changes):** IV calcium gluconate 10 mL 10% (cardioprotection), IV insulin 10U + 50 mL D50W, albuterol 10-20 mg nebulised, sodium bicarbonate if acidotic
- **Refractory:** Dialysis (haemodialysis most effective)
- **Definitive:** Address underlying cause; review medications; chronic use of K+ binders (patiromer, SZC)
- **Avoid:** Kayexalate (sodium polystyrene sulfonate) due to colonic necrosis risk (use only if no alternatives)

#### Monitoring

- Continuous ECG monitoring in severe hyperkalaemia
- Serum K+ every 1-2h during acute treatment until stable
- Daily K+ until trend established after medication changes
- Serial K+ after K+ binder initiation (weekly then monthly)
- Renal function (eGFR) — influences K+ trajectory
- Acid-base status (bicarbonate, pH)
- Digoxin levels if applicable (hyperkalaemia potentiates digoxin toxicity)
- Assess need for medication dose adjustment (RAASi, CNI, MRA)

#### Long-Term Consequences

- Cardiac arrhythmia and sudden cardiac death (increased in CKD)
- RAASi discontinuation (leads to poorer renal outcomes)
- Inability to use cardioprotective medications (RAASi, MRAs)
- Increased hospitalisation for K+ management
- Dietary restriction impact on quality of life
- Progressive metabolic acidosis exacerbation
- Dialysis initiation or intensification

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `diabeticNephropathy` | High | Hyporeninaemic hypoaldosteronism (type IV RTA); on RAASi + finerenone |
| `lupus` | Moderate | CNI therapy + RAASi; `lupus` interstitial nephritis |
| `iga` | Moderate | CKD progression + RAASi; low frequency unless G4-5 |
| `fsgs` | Moderate | Similar; RAASi + CKD stage dependent |
| `membranous` | Moderate | RAASi + CNI combination; nephrotic syndrome |
| `mcd` | Low | Transient during AKI episodes |
| `anca | Moderate | Dialysis-dependent phase; RAASi use limited post-AKI |
| `alport | Moderate | Progressive CKD + RAASi |
| `cniToxicity` | High | CNI directly impairs K+ secretion via ENaC downregulation |
| `c3` | Moderate | CKD stage dependent |
| `hivan` | Moderate | Tenofovir-related tubular dysfunction + RAASi |
| `antibodyMediatedRejection` | High | CNI + RAASi combination |
| `transplantGlomerulopathy` | High | CNI-based immunosuppression |
| `tCellMediatedRejection` | High | CNI + steroid therapy |
| `bkVirusNephropathy` | Moderate | Graft dysfunction + CNI |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| RAASi (ACEi/ARB) | Moderate-High | Reduced aldosterone, decreased distal K+ secretion |
| Spironolactone | High | Competitive aldosterone antagonist, ENaC blockade |
| Finerenone | Moderate-High | Non-steroidal MRA, similar mechanism |
| Eplerenone | Moderate-High | MRA, similar to spironolactone |
| Tacrolimus | Moderate | Downregulates ENaC expression, impairs K+ secretion |
| Cyclosporine | Moderate | Similar mechanism; more pronounced effect |
| NSAIDs | Moderate | Hyporeninaemic hypoaldosteronism |
| Beta-blockers | Low-Moderate | Reduced cellular K+ uptake via beta-2 receptor blockade |
| Trimethoprim | Moderate | ENaC blockade in distal tubule |
| Pentamidine | Moderate | ENaC blockade |
| Heparin (unfractionated) | Low-Moderate | Reduced aldosterone synthesis |
| K+ supplements | High | Exogenous K+ load in setting of impaired excretion |
| K+-containing salt substitutes | Moderate | Exogenous load, often unrecognised by patients |
| SGLT2i | Protective | Mild K+-lowering effect; reduces hyperkalaemia risk overall |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Management of Blood Pressure in CKD. *Kidney Int.* 2024;105(4S):S1-S117
2. Palmer BF. Managing Hyperkalemia: A Guide for Clinicians. *J Am Soc Nephrol.* 2023;34(2):213-225
3. Clase CM et al. Potassium Homeostasis and Management of Dyskalemia in CKD. *Am J Kidney Dis.* 2024;83(3):368-379
4. Rossignol P et al. Potassium Binders for Hyperkalemia Management in CKD. *Nat Rev Nephrol.* 2023;19(1):28-40

---
### 2.8 Metabolic Acidosis

**Complication ID:** COMP-MA-001

#### Risk Factors

- CKD G3-G5 (reduced renal acid excretion, reduced NH4+ production)
- Renal tubular acidosis (RTA Type 1 — distal; RTA Type 2 — proximal; RTA Type 4 — hypoaldosteronism)
- Diabetic nephropathy (hyporeninaemic hypoaldosteronism — Type 4 RTA)
- Tubulointerstitial disease (CNI toxicity, reflux nephropathy, obstructive uropathy)
- Drugs: CNI (tacrolimus, cyclosporine), potassium-sparing diuretics, TMP-SMX
- High-protein diet (increased endogenous acid production)
- Diarrhoea (GI bicarbonate loss; MMF-related)
- Lactic acidosis (sepsis, ischaemia, metformin in AKI)
- Ketoacidosis (DKA, SGLT2i-related euglycaemic DKA)
- Renal transplant (chronic allograft dysfunction, CNI effects)

#### Clinical Features

- Usually asymptomatic in early stages
- Fatigue, weakness, lethargy
- Anorexia, nausea, weight loss
- Hyperventilation (Kussmaul breathing if severe, pH <7.2)
- Impaired cognitive function
- Bone pain (buffering by bone leads to demineralisation)
- Growth retardation in children
- Worsening CKD progression (acidosis accelerates GFR decline)
- Hyperkalaemia (especially in Type 4 RTA)
- Nephrocalcinosis (in distal RTA)
- Hypokalaemia (in proximal and distal RTA)

#### Prevention

- Regular monitoring of serum bicarbonate in CKD G3-G5
- Dietary modification (reduce animal protein, increase fruit/vegetable intake)
- Avoid high-protein diets in CKD
- Optimise bicarbonate levels (target >22 mEq/L)
- Maintain adequate volume status
- Monitor for diarrhoea (MMF dose adjustment)
- Use SGLT2i (mild alkalinising effect)
- Consider alkali therapy early in progressive CKD

#### Early Detection

- Serum bicarbonate measurement with every metabolic panel
- Venous blood gas for confirmation if bicarbonate low
- Anion gap calculation (AG = Na - Cl - HCO3)
- Urine anion gap (UAG = Na + K - Cl) to assess renal acidification
- Urine pH and NH4+ excretion (specialised testing for RTA evaluation)
- Consider RTA workup in non-CKD patients with unexplained metabolic acidosis
- Screening for euglycaemic DKA in SGLT2i-treated patients with illness

#### Treatment

- **Alkali therapy:** Sodium bicarbonate 0.5-1.0 mEq/kg/day in divided doses; titrate to serum HCO3 >=22 mEq/L
- **Alternative:** Sodium citrate (but increases aluminium absorption; avoid with Al-based binders)
- **Dietary modification:** Low-protein diet (0.8 g/kg/day); increased fruits and vegetables
- **RTA-specific:**
  - Type 1 (distal RTA): High-dose alkali (1-2 mEq/kg/day), K+ supplementation
  - Type 2 (proximal RTA): Alkali therapy 5-15 mEq/kg/day (higher requirement), K+ and phosphate replacement
  - Type 4 (hyporeninaemic hypoaldosteronism): Fludrocortisone if refractory, loop/thiazide diuretic for K+ control
- **Dialysis:** In ESKD, dialysate bicarbonate concentration of 32-38 mEq/L
- **Avoid:** Sodium citrate with aluminium-containing phosphate binders (increased aluminium absorption)
- **If associated with MMF diarrhoea:** Dose reduction or switch to EC-MPS

#### Monitoring

- Serum bicarbonate (1-3 monthly in CKD G3-5; more frequently if on alkali therapy)
- Serum potassium (alkali therapy shifts K+ intracellularly)
- Blood pressure (sodium load from NaHCO3 may worsen HTN)
- Volume status (sodium and fluid retention)
- Bone density (long-standing acidosis causes bone loss)
- Growth monitoring in children
- Acid-base status (VBG or ABG if severe)

#### Long-Term Consequences

- Accelerated CKD progression (acidosis directly promotes interstitial fibrosis)
- Bone demineralisation (bone buffering depletes calcium carbonate stores)
- Increased fracture risk
- Muscle wasting and sarcopenia
- Growth retardation in children
- Hyperkalaemia (especially Type 4 RTA)
- Nephrocalcinosis and stone formation (distal RTA)
- Increased cardiovascular morbidity
- Reduced quality of life, fatigue

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `diabeticNephropathy` | High | Type 4 RTA common; metabolic acidosis accelerates nephropathy |
| `lupus` | Moderate | `lupus` interstitial nephritis causes RTA; CNI exacerbates |
| `iga` | Moderate | Progressive CKD leads to acidosis |
| `cniToxicity` | High | CNI directly impairs tubular acidification |
| `fsgs` | Moderate | CKD stage-dependent |
| `membranous` | Moderate | CKD stage-dependent |
| `alport | Moderate | Progressive CKD; tubular dysfunction less prominent |
| `c3` | Moderate | Tubulointerstitial component |
| `hivan` | Moderate | Tenofovir-related proximal RTA (Fanconi) |
| `transplantGlomerulopathy` | Moderate | Chronic allograft dysfunction + CNI effects |
| `antibodyMediatedRejection` | Moderate | CNI contribution |
| `tCellMediatedRejection` | Moderate | CNI contribution |
| `bkVirusNephropathy` | Moderate | Tubular injury from BK + CNI |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Calcineurin inhibitors (tacrolimus, cyclosporine) | Moderate | Impaired tubular acidification, reduced NH4+ production |
| Metformin | Moderate | Lactic acidosis (in AKI/CKD G4-5) |
| SGLT2i | Low-Moderate | Euglycaemic DKA (rare; risk in intercurrent illness) |
| TMP-SMX | Moderate | ENaC blockade (Type 4 RTA-like) |
| Spironolactone | Low-Moderate | Mild metabolic acidosis via K+ retention |
| Acetazolamide | High | Carbonic anhydrase inhibitor (proximal RTA) |
| Topiramate | Moderate | Carbonic anhydrase inhibitor |
| Sodium bicarbonate (therapeutic) | Protective | Alkalinising (therapeutic effect) |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. *Kidney Int.* 2024;105(4S):S1-S117
2. Kraut JA, Madias NE. Metabolic Acidosis of CKD: An Update. *Am J Kidney Dis.* 2021;77(6):939-949
3. Wesson DE et al. Clinical Consequences of Metabolic Acidosis and Its Management in CKD. *J Am Soc Nephrol.* 2023;34(6):1040-1052
4. Loniewski I, Wesson DE. Bicarbonate Therapy for Prevention of CKD Progression. *Kidney Int.* 2020;97(5):886-894

---
### 2.9 Osteoporosis / Renal Bone Disease

**Complication ID:** COMP-BMD-001

#### Risk Factors

- Prolonged corticosteroid therapy (prednisolone >5 mg/day for >3 months)
- CKD-MBD (secondary hyperparathyroidism, phosphate retention, vitamin D deficiency)
- Nephrotic syndrome (vitamin D-binding protein loss in urine)
- Post-transplant state (steroids + CNI effects on bone)
- Postmenopausal status (additive to steroid effects)
- Limited mobility (hospitalisation, oedema, frailty)
- Metabolic acidosis (bone buffering)
- Malnutrition (low calcium intake, vitamin D deficiency)
- Hypogonadism (cyclophosphamide-related gonadal failure)
- Loop diuretic therapy (increased calcium excretion)
- Heparin exposure (long-term LMWH)

#### Clinical Features

- Asymptomatic until fracture (most common presentation)
- Vertebral compression fractures (back pain, height loss, kyphosis)
- Hip fractures (femoral neck, intertrochanteric)
- Wrist fractures (Colles fracture)
- Rib fractures (cough-related)
- Bone pain (generalised, deep aching)
- Fractures with minimal or no trauma (fragility fractures)
- Reduced bone mineral density (T-score <-2.5 on DXA)
- Elevated PTH (secondary hyperparathyroidism)
- Hypocalcaemia, hyperphosphataemia, low vitamin D

#### Prevention

- Minimise corticosteroid dose and duration (steroid-sparing agents where possible)
- Calcium and vitamin D supplementation for all on long-term steroids
- Baseline DXA scan before starting long-term steroids
- Bisphosphonate prophylaxis (consider oral alendronate or IV zoledronate if steroids >7.5 mg/day for >3 months)
- Avoid excessive loop diuretic use
- Correct metabolic acidosis
- Promote weight-bearing exercise as tolerated
- Ensure adequate dietary calcium (1000-1200 mg/day) and vitamin D (800-2000 IU/day)
- Manage secondary hyperparathyroidism (phosphate binders, vitamin D analogues, calcimimetics)
- Monitor bone density at 1-2 year intervals on chronic steroid therapy

#### Early Detection

- Baseline DXA scan (central: hip + spine) before steroid initiation
- Annual DXA for patients on long-term steroids (prednisolone >5 mg/day)
- FRAX score assessment (fracture risk calculator, adjust for steroid dose)
- Serum calcium, phosphate, PTH, 25-OH vitamin D, 1,25-OH vitamin D
- Bone turnover markers (P1NP, CTX) where available
- Vertebral fracture assessment (VFA) on DXA or lateral spine X-ray
- Screen for hypogonadism in cyclophosphamide-treated patients
- Monitor height loss annually (suggests vertebral fractures)

#### Treatment

- **First-line (steroid-induced):** Bisphosphonate (alendronate 70 mg weekly, risedronate 35 mg weekly, or zoledronate 5 mg IV annually)
- **Alternative:** Denosumab 60 mg SC every 6 months (especially if contraindication to bisphosphonate, e.g., GFR <30)
- **CKD-MBD management:** Phosphate binders (sevelamer, calcium acetate), active vitamin D (calcitriol, paricalcitol), calcimimetic (cinacalcet) for refractory hyperparathyroidism
- **Hypocalcaemia correction:** Oral calcium + active vitamin D
- **Teriparatide (PTH 1-34):** For severe cases or bisphosphonate failures (limited evidence in CKD)
- **Surgical:** Orthopaedic management of fractures; parathyroidectomy for refractory hyperparathyroidism
- **Lifestyle:** Weight-bearing exercise, fall prevention, balance training
- **Multidisciplinary:** Nephrology + endocrinology + orthopaedics

#### Monitoring

- Annual DXA (more frequent if rapid bone loss or on high-dose steroids)
- Serum calcium, phosphate, PTH, vitamin D levels (3-6 monthly in CKD-MBD)
- Bone turnover markers (if available) before and after treatment
- Height measurement annually (vertebral fracture screening)
- Serum creatinine and eGFR (renal function affects drug selection)
- Vitamin D levels (25-OH vitamin D target >30 ng/mL)
- Adherence to bisphosphonate therapy
- Dental health assessment before bisphosphonate (prevent ONJ)

#### Long-Term Consequences

- Fragility fractures (vertebral, hip, wrist) with associated morbidity
- Chronic back pain and disability
- Height loss and kyphotic deformity
- Loss of mobility and independence
- Increased mortality post-hip fracture (20-30% 1-year mortality)
- Malunion/non-union of fractures
- Bisphosphonate-related osteonecrosis of the jaw (rare, with high cumulative dose)
- Atypical femoral fractures (rare, long-term bisphosphonate use)
- Need for surgical intervention (orthopaedic, spinal)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Steroid therapy + disease activity + postmenopausal age + vitamin D deficiency |
| `mcd` | Moderate | Frequent relapses require repeated steroid courses |
| `membranous` | Moderate | Long-term immunosuppression; vitamin D loss in urine |
| `fsgs` | Moderate | Steroid resistance requires prolonged therapy |
| `iga` | Low-Moderate | Steroid-sparing strategies reduce risk |
| `anca | High | Cyclophosphamide + high cumulative steroid dose |
| `antiGbm` | Moderate | Short-course aggressive therapy limits cumulative exposure |
| `diabeticNephropathy` | Moderate | CKD-MBD component; vitamin D deficiency common |
| `c3` | Moderate | Steroid exposure + CKD-MBD |
| `alport | Moderate | CKD-MBD with progressive CKD |
| `transplantGlomerulopathy` | High | Post-transplant bone disease (steroid + CNI + CKD-MBD) |
| `antibodyMediatedRejection` | High | Multiple steroid pulses + maintenance immunosuppression |
| `tCellMediatedRejection` | High | Pulse steroids + maintenance therapy |
| `cniToxicity` | Moderate | CNI effects on bone metabolism |
| `bkVirusNephropathy` | Moderate | Graft dysfunction adds CKD-MBD |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Prednisolone (>5 mg/day chronic) | High | Suppressed osteoblast formation, increased osteoclast activity, reduced calcium absorption |
| Methylprednisolone (pulse) | High | Potent acute effect on bone turnover |
| Cyclophosphamide | Moderate | Hypogonadism (ovarian/testicular failure) |
| CNI (tacrolimus, cyclosporine) | Moderate | Increased bone turnover, direct CNI effects on bone cells |
| Loop diuretics | Moderate | Increased urinary calcium excretion |
| Heparin (LMWH long-term) | Moderate | Increased bone resorption |
| MTOR inhibitors | Low-Moderate | Impaired bone healing, effects on bone cells |
| Proton pump inhibitors | Moderate | Reduced calcium absorption |
| Vitamin D analogues | Protective | Improve bone mineralisation (therapeutic) |
| Bisphosphonates | Protective | Antiresorptive (therapeutic) |

#### Guideline References

1. KDIGO 2017 Clinical Practice Guideline Update for the Diagnosis, Evaluation, Prevention, and Treatment of CKD-MBD. *Kidney Int Suppl.* 2017;7(1):1-59
2. American College of Rheumatology Guideline for the Prevention and Treatment of Glucocorticoid-Induced Osteoporosis. *Arthritis Care Res.* 2022;74(8):1229-1249
3. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
4. Moe SM et al. CKD-MBD: A Clinical Practice Guideline. *Am J Kidney Dis.* 2023;81(3):S1-S92

---
### 2.10 Infertility

**Complication ID:** COMP-INFERT-001

#### Risk Factors

- Cyclophosphamide therapy (dose-dependent gonadal toxicity)
- Cumulative cyclophosphamide dose (>5 g/m² in males; >7.5-10 g/m² in females)
- Older age at treatment (>30 for females, >40 for males)
- Female gender (ovaries more sensitive than testes)
- Prolonged immunosuppression (additive effects)
- Radiation therapy (rare in GN, but used for PTLD)
- CKD/ESKD (impaired hypothalamic-pituitary-gonadal axis)
- Malnutrition (nephrotic syndrome, advanced CKD)

#### Clinical Features

- **Female:** Amenorrhoea, oligomenorrhoea, anovulation, elevated FSH/LH, low AMH, premature ovarian failure (POF)
- **Male:** Azoospermia, oligospermia, elevated FSH, low testosterone, erectile dysfunction
- Inability to conceive after 12 months of unprotected intercourse
- Sex hormone abnormalities (low oestradiol in females, low testosterone in males)
- Hot flashes, vaginal dryness (female)
- Loss of libido (both sexes)

#### Prevention

- **Gonadotropin-releasing hormone (GnRH) agonist co-therapy** in females (leuprolide or triptorelin before and during cyclophosphamide therapy)
- **Sperm cryopreservation** before cyclophosphamide treatment (offer to all males of reproductive age)
- **Oocyte/embryo cryopreservation** for females before treatment (gold standard; may not be feasible in urgent treatment)
- **Ovarian tissue cryopreservation** for prepubertal females
- Minimise cumulative cyclophosphamide dose — limit to 3-6 months in GN protocols (NIH protocol, Eurolupus regimen)
- Use alternative agents: rituximab instead of cyclophosphamide where evidence supports (ANCA vasculitis, lupus nephritis)
- MMF has lower gonadal toxicity than cyclophosphamide
- Avoid cyclophosphamide in patients with preserved fertility who have alternative options

#### Early Detection

- Pre-treatment fertility counselling for all patients receiving cyclophosphamide
- Baseline FSH, LH, AMH (females); FSH, testosterone, semen analysis (males)
- Post-treatment monitoring of menstrual history (females)
- AMH levels for ovarian reserve assessment (declining AMH indicates diminishing reserve)
- Semen analysis at 6-12 months post-cyclophosphamide
- FSH monitoring (elevated FSH indicates gonadal failure)
- Referral to reproductive endocrinology for fertility assessment

#### Treatment

- **Cyclophosphamide-induced azoospermia:** May recover over 2-5 years in some patients; if persistent, donor sperm or adoption options
- **Premature ovarian failure:** Hormone replacement therapy (HRT) for symptom management and bone health until natural menopause age
- **Assisted reproductive technology (ART):** IVF with donor eggs/sperm, embryo transfer, surrogacy
- **Male hypogonadism:** Testosterone replacement (monitor for erythrocytosis, sleep apnoea)
- **Psychological support:** Fertility counselling, support groups
- **Consider oocyte donation or gestational surrogacy**
- **Exclude other causes of infertility** (structural, endocrinological, age-related)

#### Monitoring

- Menstrual history (females) — document resumption or absence post-chemotherapy
- FSH, LH, oestradiol (females) at 6 and 12 months post-treatment
- AMH (females) annually if considering fertility preservation
- Semen analysis (males) at 6, 12, 24 months post-treatment
- Testosterone levels (males) if symptoms of hypogonadism
- Bone density (if premature menopause induced without HRT)
- Cardiovascular risk assessment (premature menopause increases CV risk)

#### Long-Term Consequences

- Permanent infertility (especially high cumulative cyclophosphamide doses)
- Premature ovarian failure (increased cardiovascular, bone, cognitive risks)
- Psychosocial impact (depression, relationship strain, identity issues)
- Need for assisted reproduction or family-building alternatives
- Early menopause-related comorbidities (osteoporosis, CV disease)
- Reduced quality of life
- Financial burden of ART

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Young female predominance; cyclophosphamide used in Class III/IV; GnRH agonist co-therapy strongly recommended |
| `anca | High | Cyclophosphamide standard for severe disease; rituximab now preferred first-line in many contexts |
| `antiGbm` | Moderate | Cyclophosphamide + PLEX protocol; short duration limits cumulative dose |
| `iga` | Low | Cyclophosphamide reserved for crescentic disease only |
| `mcd` | Low | Cyclophosphamide rarely used in adults with steroid-dependent disease |
| `fsgs | Low | Cyclophosphamide third-line after steroids and CNI failure |
| `membranous` | Low-Moderate | Cyclophosphamide-modified Ponticelli regimen (6 months) |
| `lupus` (pediatric) | High | Adolescents particularly vulnerable to gonadal toxicity |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Cyclophosphamide | Very High | Direct DNA alkylation in gonads; depletes oocyte pool, damages seminiferous epithelium |
| Chlorambucil | High | Similar alkylating mechanism (rarely used now) |
| Cyclophosphamide + busulfan (transplant conditioning) | Very High | Profound gonadal toxicity; near-universal infertility |
| MMF | Low | No significant gonadal toxicity; safe alternative |
| Rituximab | Low | No direct gonadal toxicity |
| Azathioprine | Low | No significant gonadal toxicity |
| Glucocorticoids | Low-Moderate | Reversible suppression of GnRH/LH/FSH; usually resolves on dose reduction |
| CNIs | Low | No direct gonadal toxicity |

#### Guideline References

1. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
2. Fanouriakis A et al. EULAR Recommendations for Lupus Nephritis Management. *Ann Rheum Dis.* 2024;83(1):27-42
3. Oktem O, Oktay K. Fertility Preservation in Patients Undergoing Chemotherapy. *N Engl J Med.* 2019;381(5):478-490
4. Lee S et al. Gonadal Toxicity of Cyclophosphamide in Autoimmune Disease. *Arthritis Rheumatol.* 2022;74(8):1320-1332

---
### 2.11 Malignancy

**Complication ID:** COMP-MAL-001

#### Risk Factors

- Immunosuppressive therapy (cumulative dose and duration)
- Cyclophosphamide (dose-dependent: bladder cancer, skin cancer, lymphoma, leukaemia)
- Rituximab (PTLD in EBV-seronegative transplant recipients)
- MMF (PTLD in transplant, skin cancer)
- CNI therapy (tacrolimus, cyclosporine — PTLD, skin cancer, solid organ tumours)
- Azathioprine (skin cancer, lymphoma)
- Belatacept (PTLD, especially EBV D+/R-)
- Anti-TNF therapy (lymphoma, skin cancer)
- mTOR inhibitors (lower malignancy risk compared to CNI, but skin cancer still increased)
- Duration of immunosuppression (longer exposure increases risk)
- Age >50 years
- EBV serostatus (D+/R- highest PTLD risk)
- UV exposure (skin cancer)
- Smoking (bladder cancer, especially with cyclophosphamide)
- HCV/HBV co-infection (MALT lymphoma, hepatocellular carcinoma)

#### Clinical Features

- **PTLD:** Fever, weight loss, lymphadenopathy, extranodal masses (GI tract, CNS, allograft), organ dysfunction
- **Bladder cancer:** Haematuria (microscopic or macroscopic), dysuria, frequency, urgency
- **Skin cancer (SCC > BCC > melanoma):** New or changing skin lesions, non-healing ulcers, keratotic papules
- **MALT lymphoma:** GI symptoms, dyspepsia, bleeding, abdominal pain; extranodal marginal zone lymphoma
- **Leukaemia/Myelodysplasia:** Fatigue, pallor, bleeding, bruising, recurrent infections
- **Lymphoma:** Painless lymphadenopathy, B symptoms (fever, night sweats, weight loss), organ infiltration
- **Cervical/Vulvar cancer:** Abnormal bleeding, discharge, pelvic pain (HPV-related)
- **Anal cancer:** Rectal bleeding, pain, mass (HPV-related)

#### Prevention

- **Bladder cancer prevention:** Mesna (sodium 2-mercaptoethanesulfonate) co-administration with cyclophosphamide; adequate hydration; frequent voiding; consider avoiding cyclophosphamide in smokers
- **PTLD prevention:** EBV serology screening at transplant; avoid belatacept in EBV D+/R-; pre-emptive rituximab for EBV DNAemia (controversial)
- **Skin cancer prevention:** Strict UV protection (SPF 50+, protective clothing); annual dermatology screening; avoid prolonged sun exposure
- **Vaccination:** HPV vaccine (all transplant-eligible patients; ideally pre-transplant)
- **Screening:** Annual skin check; Pap smear (cervical cancer screening); mammography, colonoscopy per age guidelines
- **Immunosuppression minimisation:** CNI-sparing protocols (mTOR inhibitors have lower malignancy risk)
- **Smoking cessation:** Essential for bladder cancer prevention
- **Limit cumulative cyclophosphamide:** Use rituximab as alternative where appropriate; cap cumulative dose

#### Early Detection

- **PTLD:** EBV PCR monitoring (weekly to monthly post-transplant); PET-CT for suspected cases; lymph node biopsy for diagnosis
- **Bladder cancer:** Urinalysis for haematuria; urine cytology; cystoscopy if haematuria positive (annual surveillance for high cumulative cyclophosphamide doses)
- **Skin cancer:** Full skin examination annually (monthly self-examination); dermatology referral for suspicious lesions
- **MALT lymphoma:** Endoscopy for GI symptoms; CT imaging; biopsy of suspicious lesions
- **Cervical cancer:** Annual Pap smear in immunocompromised women
- **Breast, colon, prostate cancers:** Age-appropriate standard screening (mammography, colonoscopy, PSA)
- **Lymphoma:** Clinical examination for lymphadenopathy; low threshold for imaging

#### Treatment

- **PTLD:** Immunosuppression reduction (first-line), rituximab (for CD20+ PTLD), CHOP/CHOP-like chemotherapy if refractory, radiation for localised disease
- **Bladder cancer:** Transurethral resection (TURBT), intravesical BCG/chemotherapy, radical cystectomy for muscle-invasive disease
- **Skin cancer:** Wide local excision, Mohs micrographic surgery, radiation for advanced SCC, checkpoint inhibitors (caution in transplant — risk of rejection)
- **MALT lymphoma:** H pylori eradication (if associated), rituximab, radiation, chemotherapy
- **Lymphoma/Leukaemia:** Standard chemotherapy (adjust immunosuppressive regimen)
- **General:** Multidisciplinary approach (nephrology + oncology); adjust immunosuppression to balance rejection risk; coordinate chemotherapy with renal function

#### Monitoring

- Annual skin examination in all immunosuppressed patients
- Annual urinalysis in cyclophosphamide-exposed patients (lifetime follow-up)
- EBV PCR monitoring in high-risk transplant recipients
- Age-appropriate cancer screening (mammography, colonoscopy, Pap smear)
- Post-transplant: annual PTLD risk assessment
- Routine clinical examination for lymphadenopathy
- CBC with differential (leukaemia/lymphoma surveillance)
- Cystoscopy for haematuria in cyclophosphamide history
- Liver imaging if HBV/HCV co-infection

#### Long-Term Consequences

- Treatment-related morbidity (surgery, chemotherapy, radiation)
- Graft loss (immunosuppression reduction for PTLD)
- Metastatic disease and cancer-related mortality
- Secondary malignancies (chemotherapy-induced)
- Reduced quality of life
- Psychological impact (cancer diagnosis in chronic disease)
- Need for ongoing cancer surveillance
- Drug interactions between chemotherapy and immunosuppressants

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | Cyclophosphamide exposure + intrinsic lymphoma risk from SLE (higher risk than general population) |
| `anca | Moderate | Cyclophosphamide exposure; rituximab preferred to reduce malignancy risk |
| `membranous` | Low-Moderate | Paraneoplastic `membranous` (lung, colon, breast); cyclophosphamide exposure |
| `iga` | Low | Low cyclophosphamide use |
| `mcd` | Low | Low cyclophosphamide use |
| `fsgs | Low | Low cyclophosphamide use |
| `antibodyMediatedRejection` | High | Post-transplant; PTLD risk; cyclophosphamide, rituximab, ATG exposure |
| `tCellMediatedRejection` | High | Post-transplant; PTLD risk; ATG/T-cell depleting agents |
| `bkVirusNephropathy` | High | Post-transplant; malignancy risk from prolonged immunosuppression |
| `transplantGlomerulopathy` | High | Post-transplant; cumulative immunosuppression burden |
| `cniToxicity` | Moderate | Post-transplant; CNI-related malignancy risk |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Cyclophosphamide | Very High | DNA alkylation; bladder toxicity from acrolein metabolite; secondary leukaemia |
| Azathioprine | High | 6-thioguanine incorporation; increased SCC risk; UV sensitisation |
| Calcineurin inhibitors (tacrolimus, cyclosporine) | Moderate-High | Impaired immune surveillance; TGF-beta upregulation; PTLD risk (EBV) |
| Belatacept | High (PTLD) | T-cell co-stimulation blockade; highest PTLD risk in EBV D+/R- |
| Rituximab | Moderate | B-cell depletion impairs anti-EBV/anti-tumour immunity |
| MMF | Moderate | Reduced lymphocyte surveillance; skin cancer and PTLD risk |
| mTOR inhibitors (sirolimus, everolimus) | Low-Moderate | Antiproliferative effect; lower malignancy risk than CNI; may be protective |
| ATG/Alemtuzumab | High | Profound T-cell depletion impairs anti-EBV/anti-tumour surveillance |
| Thalidomide/Lenalidomide | Moderate | Increased risk of secondary malignancies (especially MDS/AML) |

#### Guideline References

1. KDIGO 2023 Clinical Practice Guideline for the Management of Malignancy in CKD and Transplant Recipients. *Kidney Int.* 2023;103(6S):S1-S192
2. Engels EA et al. Spectrum of Cancer Risk Among US Solid Organ Transplant Recipients. *JAMA.* 2011;306(17):1891-1901
3. Knight A et al. Cyclophosphamide and Bladder Cancer in Autoimmune Disease. *J Rheumatol.* 2021;48(6):810-817
4. Dantal J, Snanoudj R. Malignancy After Renal Transplantation. *Nat Rev Nephrol.* 2023;19(4):257-271

---
### 2.12 Cardiovascular Disease

**Complication ID:** COMP-CVD-001

#### Risk Factors

- CKD (independent risk factor — graded increase with decreasing eGFR)
- Nephrotic syndrome (dyslipidaemia, prothrombotic state, hypertension, volume overload)
- Proteinuria (>1 g/day — independent predictor of CV events)
- Hypertension (volume-dependent, RAAS-dependent, CNI-related)
- Dyslipidaemia (nephrotic syndrome: high LDL, high Lp(a), low HDL)
- Diabetes mellitus (steroid-induced or pre-existing)
- Corticosteroid therapy (metabolic effects: weight gain, hyperglycaemia, hypertension)
- CNI therapy (hypertension, dyslipidaemia, impaired glucose tolerance)
- Obesity, sedentary lifestyle
- Smoking
- Family history of premature CVD
- CKD-MBD (vascular calcification from hyperphosphataemia)
- Anaemia of CKD (LVH, myocardial ischaemia)
- Volume overload (pulmonary congestion, LV dilation)
- Inflammation (systemic lupus, ANCA vasculitis — accelerated atherosclerosis)

#### Clinical Features

- **Coronary artery disease:** Angina (typical or atypical), MI (may present with dyspnoea or fatigue), silent ischaemia more common in diabetics and CKD
- **Heart failure:** Dyspnoea on exertion, orthopnoea, PND, peripheral oedema, raised JVP, pulmonary crackles, S3 gallop
- **Arrhythmia:** Palpitations, syncope, atrial fibrillation (most common), ventricular arrhythmias, sudden cardiac death
- **Peripheral arterial disease:** Claudication, rest pain, gangrene, non-healing ulcers
- **Cerebrovascular disease:** Transient ischaemic attack, stroke (ischaemic > haemorrhagic)
- **Valvular heart disease:** Calcific aortic stenosis (accelerated in CKD), regurgitant lesions

#### Prevention

- **Blood pressure control:** Target <130/80 mmHg; RAASi first-line in proteinuric CKD
- **Lipid management:** Statin (atorvastatin 20-40 mg or equivalent) for all CKD patients age >50 or with additional CV risk; target LDL <70 mg/dL
- **Antiplatelet therapy:** Aspirin if established CVD or high CV risk (balance bleeding risk)
- **Glycaemic control:** HbA1c <7% for diabetic patients; minimise steroid exposure
- **Lifestyle:** Mediterranean diet, sodium restriction (<2 g/day), exercise (150 min/week moderate), weight management, smoking cessation
- **SGLT2i:** CV benefit independent of renal effect (dapagliflozin DECLARE-TIMI 58, empagliflozin EMPA-REG OUTCOME)
- **GLP-1 receptor agonists:** CV benefit in diabetic CKD with obesity (semaglutide)
- **Anaemia management:** ESAs to maintain Hb 10-11 g/dL (not higher — CV risk)
- **CKD-MBD management:** Phosphate control, avoid hypercalcaemia (vascular calcification)
- **Inflammation control:** Disease remission reduces CV risk (especially lupus, ANCA vasculitis)

#### Early Detection

- Annual CV risk assessment (QRISK3 or SCORE2 adjusted for CKD as independent risk factor)
- ECG (annual; evaluate for LVH, ischaemia, arrhythmia)
- Lipid profile (annually; more frequently in nephrotic syndrome or high-dose steroids)
- HbA1c (quarterly in diabetics)
- Echocardiogram (if symptoms or signs of HF, LVH on ECG)
- CACS (coronary artery calcium scoring) for risk stratification in select cases
- Ankle-brachial index (PAD screening)
- Exercise tolerance testing or stress echo if symptoms suggestive
- NT-proBNP/BNP monitoring for HF detection (interpret with GFR)
- Carotid ultrasound for plaque burden if high risk

#### Treatment

- **CAD:** RAASi + beta-blocker + antiplatelet + statin; revascularisation (PCI vs CABG) per standard guidelines
- **Heart failure:** RAASi/ARNI + beta-blocker + MRA + SGLT2i (quadruple therapy); loop diuretics for congestion; LVAD/transplant if refractory
- **Atrial fibrillation:** Rate control (beta-blocker, CCB) vs rhythm control; anticoagulation (DOAC preferred if eGFR >30; warfarin if >15 DOAC not approved; dose-adjust per renal function)
- **Dyslipidaemia:** High-intensity statin (atorvastatin 40-80 mg or rosuvastatin 20-40 mg); ezetimibe add-on if not at target; icosapent ethyl for high triglycerides
- **Peripheral arterial disease:** Supervised exercise therapy, antiplatelet (aspirin or clopidogrel), revascularisation if disabling claudication or critical limb ischaemia
- **Cardiovascular risk reduction:** Multifactorial intervention (BP, lipids, glucose, lifestyle)
- **Transplant patients:** Switch from CNI to belatacept or mTOR inhibitor if CV risk outweighs rejection risk

#### Monitoring

- BP at every visit (home BP diary)
- Lipid panel annually (3-6 monthly if on statin and very high risk)
- HbA1c quarterly (if diabetic or on high-dose steroids)
- ECG annually (more frequent if known CAD, arrhythmia, LVH)
- Echocardiogram if symptoms of HF or worsening LV function
- Weight and volume status at every visit
- Peripheral pulses, ankle-brachial index (annually)
- Adherence to cardioprotective medications
- Cardiac biomarkers (troponin, NT-proBNP) if clinical suspicion of ACS or HF

#### Long-Term Consequences

- Myocardial infarction and sudden cardiac death (leading cause of death in CKD)
- Heart failure hospitalisation (increased in dialysis patients)
- Stroke with neurological deficits
- Peripheral limb amputation (diabetic + CKD + PAD)
- Loss of independence, reduced quality of life
- Accelerated vascular calcification and valvular disease
- Death-censored graft loss due to CV death (transplant patients)
- Increased healthcare utilisation and costs
- Treatment-limiting drug interactions (polypharmacy)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `diabeticNephropathy` | Very High | Leading CV risk; aggressive multi-factorial intervention essential |
| `lupus` | High | Accelerated atherosclerosis independent of traditional risk factors; APS amplifies risk |
| `anca | High | Systemic inflammation + traditional risk factors; increased MI risk |
| `membranous` | Moderate | Nephrotic dyslipidaemia + hypertension |
| `fsgs` | Moderate | Metabolic syndrome associations; obesity, hypertension |
| `iga` | Moderate | Long-term CV risk from progressive CKD |
| `mcd` | Low | Transient during relapses; low cumulative risk |
| `alport | Moderate | Progressive CKD + potential aortic pathology |
| `cryoglobulinemic` | Moderate | Vasculitis-related CV risk |
| `c3` | Moderate | CKD progression-related CV risk |
| `antibodyMediatedRejection` | High | Post-transplant CV risk + immunosuppression effects |
| `tCellMediatedRejection` | High | Post-transplant CV risk |
| `transplantGlomerulopathy` | High | Post-transplant, progressive graft dysfunction amplifies CV risk |
| `cniToxicity` | Moderate | CNI-mediated hypertension and metabolic effects |
| `bkVirusNephropathy` | Moderate | Graft dysfunction increases CV risk |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Prednisolone (chronic) | High | Weight gain, hyperglycaemia, hypertension, dyslipidaemia |
| CNI (tacrolimus, cyclosporine) | High | Hypertension, dyslipidaemia, glucose intolerance, endothelial dysfunction |
| Cyclophosphamide | Low | No direct CV effect |
| Rituximab | Low | No direct CV effect; may reduce CV risk by achieving disease remission |
| MMF | Low | Neutral CV profile |
| Azathioprine | Low | Neutral CV profile |
| Belatacept | Lower than CNI | Better metabolic profile (lower BP, lipid, glucose) |
| mTOR inhibitors | Moderate | Hyperlipidaemia, hypertension |
| EPO | Moderate | Hypertension (dose-dependent), thrombosis risk |
| RAASi | Protective | Cardioprotective (therapeutic) |
| SGLT2i | Protective | HF and CV mortality reduction (therapeutic) |
| Statins | Protective | Lipid-lowering, anti-inflammatory (therapeutic) |

#### Guideline References

1. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease (Chapter 5: Cardiovascular Risk). *Kidney Int.* 2024;105(4S):S1-S117
2. 2021 ESC Guidelines on Cardiovascular Disease Prevention in Clinical Practice. *Eur Heart J.* 2021;42(34):3227-3337
3. McDonagh TA et al. 2021 ESC Guidelines for the Diagnosis and Treatment of Acute and Chronic Heart Failure. *Eur Heart J.* 2021;42(36):3599-3726
4. Sarnak MJ et al. KDOQI US Commentary on the 2024 KDIGO CKD Guideline: Cardiovascular Considerations. *Am J Kidney Dis.* 2024;83(5):555-575

---
### 2.13 Nephrotic Syndrome Complications

**Complication ID:** COMP-NS-001

#### Risk Factors

- Heavy proteinuria (>3.5 g/day)
- Hypoalbuminaemia (<25 g/L)
- Prolonged nephrotic state (>3 months)
- Membranous nephropathy (highest risk for thrombosis)
- Minimal change disease (highest risk for infection)
- Immunosuppressive therapy (additive infection risk)
- Advanced age, immobility
- Pre-existing CV disease

#### Clinical Features

- **Infections:** Spontaneous bacterial peritonitis, cellulitis, pneumonia, UTI, sepsis (encapsulated organisms: Strep pneumo, H influenzae, E coli)
- **Thrombosis:** DVT, PE, renal vein thrombosis, IVC thrombosis
- **AKI:** Haemodynamic (hypoalbuminaemia), ATN, bilateral renal vein thrombosis
- **Malnutrition:** Muscle wasting, growth failure (children), hypoalbuminaemia
- **Dyslipidaemia:** High LDL, high Lp(a), high triglycerides, low HDL
- **Hypogammaglobulinemia:** IgG, IgA loss in urine; increased infection susceptibility
- **Vitamin D deficiency:** Loss of vitamin D-binding protein; hypocalcaemia, secondary hyperparathyroidism
- **Iron deficiency anaemia:** Transferrin loss
- **Copper and zinc deficiency:** Trace element depletion
- **Thyroid dysfunction:** Loss of thyroid-binding globulin

#### Prevention

- Rapid achievement of remission (immunosuppression to reduce proteinuria)
- Prophylactic anticoagulation (albumin <20 g/L, especially membranous)
- Pneumococcal vaccination (PCV20 + PPSV23)
- Influenza vaccination annually
- PJP prophylaxis (TMP-SMX) if on high-dose steroids
- Diuretic-sparing volume management (judicious diuretics to avoid AKI)
- Nutritional support (high-quality protein 1.0-1.2 g/kg/day, vitamin D, calcium, iron, zinc)
- Monitor for AKI during intercurrent illness or diuretic therapy
- Early detection and treatment of infections
- Statin therapy for severe hyperlipidaemia (reduce CV risk)

#### Early Detection

- Serum albumin monitoring (weekly to monthly during active disease)
- Proteinuria quantification (UPCR/ACR)
- Clinical examination for oedema, ascites, pleural effusion
- Screening for infection at every visit
- D-dimer screening if thrombotic symptoms
- Renal function (creatinine, eGFR) — detect AKI early
- Immunoglobulin levels in recurrent infections
- Vitamin D, calcium, phosphate, PTH levels
- Nutritional assessment (weight, mid-arm circumference, prealbumin)

#### Treatment

- **Infections:** Prompt empiric antibiotics; consider intra-abdominal source; IVIG if severe hypogammaglobulinemia
- **Thrombosis:** Anticoagulation (LMWH, warfarin, DOACs); treat underlying GN
- **AKI:** Volume repletion cautiously (albumin if haemodynamic); discontinue nephrotoxins; RRT if severe
- **Malnutrition:** Dietary counselling; high-protein diet (1.2-1.5 g/kg/day); vitamin D, calcium, iron, zinc supplementation
- **Dyslipidaemia:** High-intensity statin; ezetimibe add-on if needed
- **Oedema:** Sodium restriction (<2 g/day); loop diuretics; cautious albumin infusion + diuretic for refractory cases
- **Hypogammaglobulinemia:** IVIG supplementation if recurrent severe infections
- **Definitive:** Achieve disease remission with appropriate immunosuppression

#### Monitoring

- Daily weight and fluid balance during acute nephrotic state
- Serum albumin, creatinine, UPCR/ACR (weekly to monthly)
- IgG levels (if recurrent infections)
- Vitamin D, calcium, PTH (monthly)
- Iron studies, zinc (if deficiency suspected)
- Lipid profile (quarterly)
- Infection surveillance
- Screening for thrombosis (clinical assessment)
- Nutritional status monitoring

#### Long-Term Consequences

- Chronic infection susceptibility (especially if hypogammaglobulinemia persists)
- Post-thrombotic syndrome or CTEPH after VTE
- CKD progression from repeated AKI or persistent nephrosis
- Osteoporosis from vitamin D deficiency and steroid therapy
- Accelerated atherosclerosis from prolonged dyslipidaemia
- Growth retardation in children
- Reduced quality of life
- Dependency on immunosuppression for remission maintenance

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `membranous` | Very High | Highest VTE risk; multiple complications from prolonged nephrosis |
| `mcd` | High | Infection risk dominant; steroid sensitivity determines duration of exposure |
| `fsgs | High | Resistance to therapy prolongs nephrotic state; collapsing variant worst |
| `lupus` (Class V) | High | `membranous` `lupus` nephritis; coexistence with Class III/IV |
| `lupus` (Class III/IV) | Moderate | Nephrotic-range proteinuria common; infection from immunosuppression |
| `iga` | Low-Moderate | Nephrotic transformation uncommon |
| `anca | Low-Moderate | Nephrotic-range proteinuria less common |
| `diabeticNephropathy` | Moderate | Nephrotic-range proteinuria with declining eGFR; VTE risk lower than membranous |
| `c3` | Moderate | Variable; depends on histology |
| `cryoglobulinemic` | Moderate | Nephrotic syndrome from MPGN pattern |
| `amyloid | Very High | Heavy proteinuria; additional cardiac complications |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Loop diuretics (excessive) | Moderate | Overdiuresis precipitates AKI |
| RAASi | Protective | Reduces proteinuria (therapeutic) |
| SGLT2i | Protective | Reduces proteinuria, improves outcomes |
| Statins | Protective | Lipid management (therapeutic) |
| Anticoagulants (LMWH, warfarin) | Dual (protective + risk) | Prevents VTE but increases bleeding risk |
| IVIG | Low-Moderate | Infusion reactions, volume overload |
| Albumin infusions | Low | Volume expansion, but risk of pulmonary oedema |

#### Guideline References

1. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
2. Hull RP, Goldsmith DJ. Nephrotic Syndrome in Adults. *BMJ.* 2018;336(7654):1185-1189
3. Orth SR, Ritz E. The Nephrotic Syndrome. *N Engl J Med.* 1998;338(17):1202-1211
4. Kodner C. Diagnosis and Management of Nephrotic Syndrome in Adults. *Am Fam Physician.* 2016;93(6):479-485

---
### 2.14 Hemorrhagic Cystitis

**Complication ID:** COMP-HC-001

#### Risk Factors

- Cyclophosphamide therapy (dose-dependent; increased risk with cumulative doses >7 g/m²)
- Ifosfamide therapy (higher risk than cyclophosphamide)
- Prior pelvic radiation therapy
- Inadequate hydration during cyclophosphamide infusion
- Lack of Mesna co-administration
- Concurrent NSAID use (increased bladder irritation)
- Smoking history
- Prior hemorrhagic cystitis episode (recurrence risk)
- Dehydration, concentrated urine
- BK virus infection in transplant (virus-associated hemorrhagic cystitis)

#### Clinical Features

- **Haematuria:** Microscopic (earliest sign) to macroscopic with clots
- **Dysuria:** Painful urination, suprapubic pain
- **Urinary frequency, urgency**
- **Lower abdominal pain** (suprapubic, bladder region)
- **Clot retention:** Inability to void, severe pain, urinary retention
- **Anaemia:** From significant blood loss
- **Duration:** Acute (within days of cyclophosphamide) or chronic (months to years later)
- **Severity grading:**
  - Grade 1: Microscopic haematuria
  - Grade 2: Macroscopic haematuria
  - Grade 3: Macroscopic haematuria with clots
  - Grade 4: Severe haemorrhage requiring transfusion or intervention

#### Prevention

- **Mesna (sodium 2-mercaptoethanesulfonate):** Co-administration with cyclophosphamide at 80-120% of cyclophosphamide dose (IV or oral in divided doses)
- **Hydration:** IV fluids at 3 L/m²/day; aggressive pre- and post-hydration
- **Frequent voiding:** Empty bladder every 2-4 hours during cyclophosphamide infusion
- **Bladder irrigation:** Continuous saline irrigation for high-dose regimens (transplant conditioning)
- **Limit cumulative cyclophosphamide dose:** Consider rituximab as alternative where possible
- **Avoid:** Concurrent NSAIDs during cyclophosphamide therapy
- **Smoking cessation:** Reduces bladder cancer risk (additive with cyclophosphamide)
- **Urine alkalinisation:** Maintain urine pH >7.0 (reduces acrolein toxicity)

#### Early Detection

- Urinalysis before and after each cyclophosphamide cycle (monitor for haematuria)
- Symptom screening (dysuria, frequency, suprapubic pain) with each cycle
- Urine cytology for atypical cells (in chronic exposure or persistent haematuria)
- Cystoscopy for persistent or severe haematuria
- Bladder ultrasound for clot or wall thickening
- BK virus PCR in transplant recipients with unexplained haematuria

#### Treatment

- **Mild (Grade 1-2):** Hydration, Mesna, voiding encouragement, symptomatic relief
- **Moderate (Grade 3):** Continuous bladder irrigation (saline or glycine), cystoscopy with clot evacuation, Mesna continuation
- **Severe (Grade 4):** Cystoscopy under GA with fulguration/clot evacuation, intravesical therapy (alum, prostaglandins, formalin), selective embolisation of bladder arteries, cystectomy as last resort
- **Hyperbaric oxygen therapy:** For chronic refractory cases (promotes mucosal healing)
- **Sucralfate:** Oral or intravesical (mucosal protective)
- **Amicar (aminocaproic acid):** Antifibrinolytic for persistent bleeding (use with caution — risk of thrombosis)
- **Blood transfusion:** For symptomatic anaemia
- **Stop cyclophosphamide/ifosfamide:** At least temporarily, consider alternative agents
- **BK virus-related:** Reduce immunosuppression, cidofovir (off-label)

#### Monitoring

- Urinalysis during and after each cyclophosphamide infusion
- Haemoglobin/hematocrit during active bleeding
- Symptom diary (dysuria, frequency, haematuria resolution)
- Cystoscopy for persistent haematuria (>2 weeks)
- Urine cytology yearly after cyclophosphamide exposure (bladder cancer screening)
- BP monitoring (bladder irrigation may cause fluid overload)
- Renal function (if obstructive uropathy from clots)

#### Long-Term Consequences

- Chronic cystitis (persistent urinary symptoms)
- Bladder fibrosis and reduced bladder capacity
- Ureteric obstruction (from fibrosis)
- Bladder cancer (transitional cell carcinoma) — increased risk with cumulative cyclophosphamide exposure
- Renal impairment from obstructive uropathy
- Iron deficiency anaemia from chronic blood loss
- Urinary incontinence
- Recurrent urinary tract infections

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | Cyclophosphamide used in Class III/IV; cumulative dose concern |
| `anca | Moderate | Cyclophosphamide used in severe/refractory disease |
| `antiGbm` | Moderate | Cyclophosphamide standard in PLEX + CyP protocol |
| `membranous` | Low | Modified Ponticelli regimen (6 months cyclophosphamide) |
| `mcd` | Low | Cyclophosphamide rarely used |
| `fsgs | Low | Cyclophosphamide used in steroid-resistant cases |
| `iga` | Low | Cyclophosphamide only in crescentic disease |
| `antibodyMediatedRejection` | Low | Cyclophosphamide used rarely (bortezomib/rituximab preferred) |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Cyclophosphamide | Very High | Acrolein metabolite causes direct bladder mucosal toxicity |
| Ifosfamide | Very High | Acrolein metabolite (similar mechanism, higher risk) |
| Busulfan | Moderate | Metabolite-related bladder toxicity |
| Mesna (co-treatment) | Protective | Inactivates acrolein in urine (therapeutic) |
| NSAIDs | Moderate | Reduced PGE2-mediated mucosal protection |
| BK virus (transplant) | Moderate | Virus-induced haemorrhagic cystitis |

#### Guideline References

1. Monach PA et al. Cyclophosphamide and Hemorrhagic Cystitis in ANCA Vasculitis. *Arthritis Rheum.* 2010;62(11):3461-3467
2. Boumpas DT et al. Cyclophosphamide in Lupus Nephritis. *Ann Intern Med.* 1995;123(12):905-915
3. Walsh M, Jayne D. Cyclophosphamide in the Treatment of Vasculitis. *Nat Rev Nephrol.* 2011;7(5):278-284
4. Matz EL et al. Management of Hemorrhagic Cystitis. *Urology.* 2020;138:S30-S35

---
### 2.15 Posterior Reversible Encephalopathy Syndrome (PRES)

**Complication ID:** COMP-PRES-001

#### Risk Factors

- Hypertension (acute severe BP elevation, often >180/120 mmHg)
- CNI therapy (tacrolimus > cyclosporine)
- CNI trough levels (high levels increase risk, but can occur at therapeutic levels)
- mTOR inhibitors (sirolimus, everolimus — rare)
- Monoclonal antibody therapy (rituximab, alemtuzumab, ATG — rare)
- EPO therapy (high doses)
- CKD/ESKD (impaired autoregulation of cerebral blood flow)
- Autoimmune disease (lupus, ANCA vasculitis — disease activity)
- Pregnancy (pre-eclampsia/eclampsia)
- Electrolyte disturbances (hypomagnesaemia, hypocalcaemia)
- Fluid overload, rapid volume shifts
- Recent transplant surgery
- Sepsis
- Thrombotic microangiopathy

#### Clinical Features

- **Headache (80%):** Diffuse, throbbing, often severe, may be the earliest symptom
- **Visual disturbances (30-50%):** Blurred vision, scotomata, visual hallucinations, cortical blindness
- **Seizures (60-75%):** Generalised tonic-clonic; may be the presenting feature
- **Altered mental status (40-50%):** Confusion, agitation, lethargy, coma (in severe cases)
- **Hypertension (70-90%):** Severe, often >180/120 mmHg; may be absent in normotensive PRES
- **Focal neurological deficits (10-15%):** Hemiparesis, ataxia, aphasia
- **Nausea/vomiting**
- **Clinical triad:** Headache + seizures + visual disturbance (classic but not always present)
- **Imaging:** Bilateral cortical-subcortical vasogenic oedema on MRI (T2/FLAIR hyperintensities), typically parieto-occipital regions; atypical: frontal lobes, basal ganglia, brainstem, cerebellum

#### Prevention

- Strict BP control post-transplant (target <140/90 mmHg)
- CNI trough level monitoring and dose adjustment (tacrolimus target 5-10 ng/mL)
- Avoid rapid CNI dose escalations
- Consider CNI withdrawal or minimisation protocols in high-risk patients
- Switch CNI to alternative (belatacept, mTOR inhibitor) if recurrent PRES
- Avoid high EPO doses
- Correct electrolyte disturbances (especially magnesium)
- Close monitoring of BP in lupus patients with active CNS disease
- Avoid large volume fluctuations during dialysis

#### Early Detection

- High index of suspicion in patients receiving CNIs, especially with BP elevation
- Immediate BP measurement with neurological symptoms
- Brain MRI with FLAIR sequence (most sensitive imaging modality)
- EEG if seizures suspected
- CNI trough level measurement (rule out supratherapeutic levels)
- Neurological exam at every transplant visit
- Magnesium monitoring (hypomagnesaemia increases risk)
- Fundoscopic examination for papilloedema and hypertensive retinopathy

#### Treatment

- **Immediate:** Control BP (IV antihypertensives: labetalol, nicardipine); target 25% reduction over first 1-2 hours
- **Withdraw/reduce CNI:** Temporarily hold tacrolimus or cyclosporine; reduce target trough
- **Switch CNI to belatacept or mTOR inhibitor** if PRES is severe or recurrent
- **Seizure management:** Anticonvulsants (levetiracetam preferred — no CYP interaction); usually temporary
- **Supportive care:** ICU monitoring, airway protection if necessary
- **Avoid:** Rapid BP correction (can worsen ischaemia)
- **Duration:** Symptoms typically resolve over days to weeks with treatment
- **Monitor for recurrence** with CNI reintroduction
- **In lupus-related PRES:** Treat underlying disease activity

#### Monitoring

- BP monitoring (hourly until controlled, then every 4-6 hours in ICU)
- Neurological status (GCS, focal deficits — hourly)
- CNI trough levels (daily during acute phase)
- Serum magnesium, potassium, calcium (daily)
- MRI brain (if no improvement; to exclude other pathology)
- EEG (if persistent seizures or altered mental status)
- Renal function (BP management may affect kidney perfusion)
- Resumption of CNI at lower dose (monitor for recurrence)
- Eye exam (visual changes may take weeks to resolve)

#### Long-Term Consequences

- Residual neurological deficits (rare, <10%): Visual field defects, cognitive impairment
- Epilepsy (recurrent seizures post-PRES)
- Recurrent PRES (if CNI not adjusted or alternative immunosuppressant not considered)
- CNI intolerance leading to immunosuppression changes
- Increased risk of rejection (if immunosuppression reduced)
- Rare: Ischaemic stroke from severe vasoconstriction
- Post-traumatic stress from acute neurological event
- Permanent visual loss (cortical blindness — rare, usually reversible)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | CNS `lupus` + CNI use + hypertension; PRES may mimic `lupus` cerebritis |
| `cniToxicity` | High | CNI is the most common reversible cause; may present even at therapeutic levels |
| `antibodyMediatedRejection` | Moderate | CNI exposure + BP changes during PLEX/IVIG |
| `tCellMediatedRejection` | Moderate | Pulse steroids and CNI dose escalation increase risk |
| `transplantGlomerulopathy` | Moderate | Chronic CNI maintenance, hypertension |
| `bkVirusNephropathy` | Low | CNI levels, hypertension |
| `iga` | Very Low | Rare unless post-transplant |
| `anca | Low | Rare; disease activity + CNI exposure |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Tacrolimus | High | Endothelial dysfunction, impaired cerebral autoregulation |
| Cyclosporine | High | Endothelial dysfunction; higher risk than tacrolimus historically |
| Sirolimus | Low-Moderate | Rare PRES cases reported |
| Everolimus | Low-Moderate | Rare PRES cases reported |
| Alemtuzumab | Low | Rare infusion-related PRES |
| ATG | Low | Rare infusion-related PRES |
| EPO (high dose) | Low | Hypertension exacerbation |
| Bevacizumab | High | VEGF inhibition, endothelial dysfunction |
| Chemotherapy (cisplatin, cytarabine) | Moderate | Endothelial toxicity |

#### Guideline References

1. Fugate JE, Rabinstein AA. Posterior Reversible Encephalopathy Syndrome: Clinical and Radiological Manifestations, Pathophysiology, and Treatment. *Mayo Clin Proc.* 2015;90(7):936-951
2. Bartynski WS. Posterior Reversible Encephalopathy Syndrome. *AJNR Am J Neuroradiol.* 2008;29(6):1051-1059
3. Barba T et al. PRES in Solid Organ Transplant Recipients. *Transplantation.* 2021;105(7):1466-1476
4. Gronemann ST et al. Management of PRES: A Systematic Review. *Neurocrit Care.* 2022;37(2):350-363

---
### 2.16 New-Onset Diabetes After Transplant (NODAT)

**Complication ID:** COMP-NODAT-001

#### Risk Factors

- Tacrolimus therapy (highest risk among CNIs; calcineurin inhibition impairs insulin secretion)
- Corticosteroid therapy (dose-dependent insulin resistance; prednisolone >10 mg/day)
- Cyclosporine (lower risk than tacrolimus)
- mTOR inhibitors (sirolimus, everolimus — impaired insulin sensitivity)
- Older age (>45 years)
- Pre-existing pre-diabetes or metabolic syndrome
- Obesity (BMI >30)
- Hepatitis C infection
- Family history of type 2 diabetes
- Ethnicity (African American, Hispanic, South Asian)
- Delayed graft function
- CMV infection

#### Clinical Features

- Asymptomatic hyperglycaemia (most common — detected on screening)
- Polyuria, polydipsia, polyphagia
- Fatigue, blurred vision
- Unexplained weight loss (less common)
- Recurrent infections (UTI, wound infections)
- Poor wound healing
- Hyperglycaemia in the immediate post-transplant period (often resolves as steroids tapered)
- Diagnosis: FPG >=126 mg/dL, HbA1c >=6.5%, 2h OGTT >=200 mg/dL, or random glucose >=200 mg/dL with symptoms

#### Prevention

- Identify high-risk patients pre-transplant (screening: FPG, HbA1c, OGTT if indicated)
- Minimise corticosteroid exposure (rapid taper to <10 mg/day; steroid-sparing protocols)
- Use cyclosporine instead of tacrolimus in high-risk patients (but consider rejection risk)
- Switch from CNI to belatacept (better metabolic profile)
- Weight management and lifestyle counselling pre- and post-transplant
- Hepatitis C treatment before transplant if possible
- Nutritional counselling (low-glycaemic index diet, portion control)
- Early post-transplant glucose monitoring for detection and early intervention
- Avoid mTOR inhibitors in high-risk patients

#### Early Detection

- Fasting plasma glucose weekly for first 4 weeks post-transplant, then monthly for 6 months, then annually
- HbA1c at 3, 6, 12 months post-transplant (valid after 3 months; earlier may be affected by anaemia/ESA)
- OGTT at 6-8 weeks post-transplant in high-risk patients
- Self-monitoring blood glucose (SMBG) if hyperglycaemia detected
- Screening for metabolic syndrome components (BP, lipids, weight, waist circumference)

#### Treatment

- **Lifestyle modification:** Diet (low-carb, low-glycaemic index), exercise (150 min/week), weight loss
- **First-line:** Metformin (if eGFR >30 — avoid in advanced CKD; caution if on CNI — lactic acidosis risk)
- **Second-line:** Insulin (basal alone or basal-bolus); preferred early post-transplant for rapid control
- **Alternative oral agents:**
  - SGLT2i: Emerging evidence; renoprotective; risk of UTIs and volume depletion
  - DPP-4 inhibitors: Safe in renal impairment (linagliptin preferred — no dose adjustment)
  - GLP-1 receptor agonists: Weight loss benefit; GI side effects; limited transplant data
- **Avoid:** Sulfonylureas (hypoglycaemia risk in renal impairment)
- **Insulin-sensitising agents:** Pioglitazone (weight gain, fluid retention, fracture risk)
- **Adjust immunosuppression:** Consider CNI dose reduction; switch to belatacept or mTOR inhibitor with lower diabetogenic potential
- **Target:** HbA1c <7% (individualised; avoid hypoglycaemia in CKD)

#### Monitoring

- FPG (monthly for first 6 months, then quarterly)
- HbA1c (quarterly; more frequent if not at target)
- SMBG log review at each visit
- Annual lipid profile, BP, weight
- Renal function (eGFR) — metformin dosing and safety
- Retinal examination (annually)
- Foot examination (annually)
- Screening for cardiovascular disease
- Immunosuppression trough levels (tacrolimus/cyclosporine levels after dose changes)
- HbA1c targets individualised for age, comorbidity, transplant vintage

#### Long-Term Consequences

- Microvascular complications (retinopathy, neuropathy, nephropathy on top of transplant)
- Macrovascular complications (accelerated CVD, stroke, PAD)
- Graft dysfunction (diabetic nephropathy may recur or develop de novo)
- Increased infection risk (especially UTIs, wound infections)
- Poor wound healing
- Increased mortality (cardiovascular)
- Need for insulin therapy (some patients become insulin-dependent)
- Drug interactions (metformin + CNI, insulin + steroids)
- Reduced quality of life, polypharmacy

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `antibodyMediatedRejection` | High | Tacrolimus + steroids; higher cumulative steroid exposure |
| `tCellMediatedRejection` | High | Pulse steroids + maintenance tacrolimus |
| `transplantGlomerulopathy` | Moderate | Long-term CNI exposure |
| `cniToxicity` | Moderate | Tacrolimus exposure duration |
| `bkVirusNephropathy` | Moderate | Tacrolimus-based immunosuppression |
| `diabeticNephropathy` | Very High | Recurrent or de novo diabetic nephropathy in transplant; pre-existing DM |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Tacrolimus | High | Impaired insulin secretion (calcineurin inhibition in pancreatic beta-cells) |
| Prednisolone (>10 mg/day) | High | Insulin resistance, increased gluconeogenesis |
| Cyclosporine | Moderate | Lower diabetogenic effect than tacrolimus |
| Sirolimus | Moderate | Impaired insulin sensitivity |
| Everolimus | Moderate | Impaired insulin sensitivity |
| Methylprednisolone (pulse) | High | Acute hyperglycaemia, stress dose equivalent |
| Belatacept | Low | Neutral metabolic profile; may improve glucose control vs CNI |
| MMF | Low | No effect on glucose metabolism |
| Azathioprine | Low | No effect on glucose metabolism |

#### Guideline References

1. KDIGO 2023 Clinical Practice Guideline for the Care of Kidney Transplant Recipients. *Transplantation.* 2023;107(6S):S1-S216
2. Sharif A et al. New-Onset Diabetes After Transplantation. *Lancet Diabetes Endocrinol.* 2023;11(6):433-445
3. Werzowa J et al. Management of Post-Transplant Diabetes. *Nat Rev Endocrinol.* 2021;17(8):485-499
4. Hecking M et al. NODAT: A Practical Guide. *Am J Transplant.* 2022;22(4):1019-1031

---
### 2.17 Avascular Necrosis

**Complication ID:** COMP-AVN-001

#### Risk Factors

- Corticosteroid therapy (dose- and duration-dependent; prednisolone >20 mg/day cumulative)
- Pulse methylprednisolone therapy (high-dose pulses increase risk)
- Cumulative steroid dose (total prednisolone equivalent >2000-3000 mg)
- Renal transplant (steroid maintenance + CKD-MBD)
- Systemic lupus erythematosus (disease itself + steroid treatment)
- CNI therapy (vasoconstriction contributes to bone ischaemia)
- Sickle cell disease/trait (especially in FSGS with APOL1 risk variants)
- Alcohol excess
- Trauma (femoral neck fracture)
- Hypercoagulable states (antiphospholipid syndrome)
- Dysbaric phenomena (decompression sickness)
- Radiotherapy

#### Clinical Features

- **Joint pain:** Deep, aching pain in affected joint (hip > knee > shoulder > ankle)
- **Sudden onset:** Often acute, may be gradual
- **Weight-bearing pain:** Hip pain aggravated by walking, relieved by rest
- **Joint stiffness:** Reduced range of motion, especially internal rotation (hip)
- **Limp (lower extremity)**
- **Rest pain:** Advanced disease causes pain at rest and night pain
- **Bilateral involvement:** In 50-80% (femoral heads)
- **Late collapse:** Joint deformity, crepitus, fixed flexion deformity
- **Imaging:**
  - X-ray: Normal early; later: subchondral lucency (crescent sign), collapse, flattening, secondary osteoarthritis
  - MRI: Gold standard — T1-weighted hypointense line (band-like pattern) in femoral head
  - Bone scan: Increased uptake (early), cold defect (advanced)

#### Prevention

- Minimise corticosteroid dose and duration — most important modifiable risk factor
- Use steroid-sparing agents (MMF, rituximab, belimumab, azathioprine)
- Avoid pulse methylprednisolone unless absolutely necessary
- Rapid steroid taper to lowest effective maintenance dose (target <5-7.5 mg/day prednisolone)
- Monitoring cumulative steroid dose
- Consider bisphosphonate prophylaxis (limited evidence for steroid-induced AVN prevention)
- Optimise calcium and vitamin D
- Avoid alcohol excess
- Address hypercoagulable states (APS anticoagulation)

#### Early Detection

- High index of suspicion in patients on steroids with hip, knee, or shoulder pain
- MRI of symptomatic joint (most sensitive and specific)
- X-ray for screening (may miss early AVN)
- Bone scan if MRI contraindicated
- Consider asymptomatic screening MRI of bilateral hips if high cumulative steroid dose (>3000 mg) or pulse therapy
- Regular history and examination for joint pain at each nephrology visit

#### Treatment

- **Early (pre-collapse):** Core decompression, bisphosphonates, protected weight bearing
- **Moderate (early collapse):** Osteotomy (realigns necrotic segment from weight-bearing area)
- **Advanced (post-collapse):** Joint replacement (total hip arthroplasty) — definitive treatment
- **Medical:** Alendronate (may slow progression), pain management, physiotherapy
- **Joint-preserving procedures:** Bone grafting (vascularised fibular graft, free vascularised iliac graft)
- **Bisphosphonates:** Zoledronic acid or alendronate may reduce risk of collapse
- **MRI surveillance:** For contralateral asymptomatic hip if unilateral AVN

#### Monitoring

- Clinical assessment of pain, range of motion, function
- MRI for progression (if non-surgical management)
- X-ray if symptoms worsen (assess for collapse, secondary OA)
- Post-surgical rehabilitation progress
- Contralateral joint monitoring (high rate of bilateral disease)
- Steroid dose documentation (cumulative dose tracking)
- Screening for additional joints if symptoms develop elsewhere

#### Long-Term Consequences

- Joint collapse and secondary osteoarthritis
- Chronic pain and disability
- Need for total joint arthroplasty (especially hip)
- Prosthesis complications (infection, loosening, dislocation)
- Gait disturbance, limping
- Impaired quality of life, loss of employment
- Reduced physical activity contributing to obesity, CVD
- Multiple joint involvement requiring staged arthroplasties

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Disease + high-dose steroids; AVN affects 10-40% of `lupus` patients |
| `mcd` | Moderate | Frequent relapses require repeated steroid courses |
| `fsgs` | Moderate | Steroid resistance prolongs exposure |
| `membranous` | Low-Moderate | Lower cumulative steroid exposure in modern protocols |
| `anca | Moderate | Cyclophosphamide and high-dose steroids |
| `antiGbm | Low-Moderate | Short-course aggressive therapy |
| `iga` | Low | Steroid-sparing strategies |
| `antibodyMediatedRejection` | High | Steroid pulses + maintenance therapy |
| `tCellMediatedRejection` | High | Pulse steroids for acute rejection |
| `transplantGlomerulopathy` | Moderate | Long-term steroid maintenance |
| `bkVirusNephropathy` | Moderate | Steroid-containing maintenance regimens |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Prednisolone (chronic >10 mg/day) | High | Osteocyte apoptosis, impaired bone remodelling, fat hypertrophy |
| Methylprednisolone (pulse) | High | Acute osteocyte apoptosis, marrow fat hypertrophy, microvascular occlusion |
| Dexamethasone | High | More potent; higher risk per mg equivalent |
| CNI (tacrolimus, cyclosporine) | Low-Moderate | Vasoconstriction contributing to bone ischaemia |
| MMF | Low | No direct bone toxicity |
| Rituximab | Low | No direct bone toxicity |
| Bisphosphonates | Protective | May reduce collapse risk (therapeutic) |

#### Guideline References

1. Mont MA et al. Avascular Necrosis of the Femoral Head: A Review. *J Bone Joint Surg Am.* 2020;102(19):1718-1730
2. Mankin HJ. Nontraumatic Necrosis of Bone. *N Engl J Med.* 1992;326(22):1473-1479
3. Zhu HH et al. Steroid-Induced Osteonecrosis: A Literature Review. *J Orthop Surg Res.* 2023;18(1):120
4. Assouline-Dayan Y et al. Pathogenesis and Natural History of Osteonecrosis. *Semin Arthritis Rheum.* 2023;63:152251

---
### 2.18 Infusion Reactions

**Complication ID:** COMP-IR-001

#### Risk Factors

- Monoclonal antibody therapy (first infusion highest risk)
- Prior infusion reaction (increased risk with subsequent infusions)
- High infusion rate
- High drug dose (rapid infusion of large protein load)
- Pre-existing complement activation (PNH, aHUS — for eculizumab)
- IgA deficiency (for IVIG — anaphylactic reactions)
- Autoimmune disease (lupus — higher cytokine release risk)
- Impaired renal function (fluid overload with IVIG)
- Active infection or inflammation
- No pre-medication
- Age (children and elderly at higher risk)

#### Clinical Features

- **Rituximab infusion reactions (common, 30-80% first infusion):**
  - Mild: Fever, chills, rigors, flushing, headache, pruritus, urticaria
  - Moderate: Nausea, vomiting, dyspnoea, bronchospasm, hypotension, hypertension, angioedema
  - Severe: Hypoxia, severe bronchospasm, anaphylaxis, acute coronary syndrome, ARDS, tumour lysis syndrome
- **IVIG infusion reactions (5-15%):**
  - Mild: Headache, myalgia, fever, chills, flushing, nausea
  - Moderate: Severe headache (aseptic meningitis), hypertensive crisis, thromboembolic events
  - Severe: Anaphylaxis (IgA deficiency), acute renal failure (sucrose-containing preparations), haemolysis, ARDS
- **Eculizumab infusion reactions (rare):**
  - Mild: Headache, nausea, dizziness
  - Severe: Anaphylaxis (very rare), complement activation (PNH breakthrough)
- **Belimumab infusion reactions (8-15%):**
  - Mild-moderate: Nausea, headache, diarrhoea, fatigue, infusion site reactions
  - Severe: Anaphylaxis (<1%), hypersensitivity
- **Alemtuzumab infusion reactions (40-80%):** Fever, rigors, hypotension, urticaria, bronchospasm
- **Timing:** During infusion to 24 hours post-infusion; first infusion most severe

#### Prevention

- **Pre-medication protocol:**
  - Acetaminophen (paracetamol) 650-1000 mg PO 30-60 min before infusion
  - Diphenhydramine 25-50 mg IV/PO (or cetirizine 10 mg as alternative)
  - Methylprednisolone 50-100 mg IV (for rituximab, alemtuzumab)
- **Infusion rate:** Start slow (25-50 mg/h for rituximab), escalate gradually per protocol
- **Ensure anti-IgA antibodies tested before IVIG (if deficient, use IgA-depleted IVIG)**
- **Volume load:** Use concentrated IVIG (10% vs 5%) to reduce volume; avoid in CKD G4-5
- **Hydration:** Pre-infusion hydration for rituximab (reduce cytokine release risk)
- **Screen for active infection before infusion**
- **Baseline complement levels (eculizumab)**
- **Emergency preparedness:** Anaphylaxis kit available at bedside
- **Patient education:** Recognise and report early symptoms

#### Early Detection

- Vital sign monitoring every 15-30 minutes during infusion
- Observe for flushing, urticaria, rigors
- Patient self-monitoring (ask about headache, dyspnoea, nausea)
- Pulse oximetry continuous monitoring (hypoxia)
- BNP monitoring during IVIG (if CKD, volume overload risk)
- Differentiate from anaphylaxis: Rapid onset (minutes), urticaria, angioedema, bronchospasm, hypotension
- Document all infusion events (severity grading per CTCAE criteria)

#### Treatment

- **Mild (CTCAE Grade 1-2):**
  - Slow infusion rate by 50%
  - Administer diphenhydramine 25-50 mg IV
  - Acetaminophen 650 mg
  - Symptomatic treatment (antiemetic, fluids)
- **Moderate (Grade 2-3):**
  - Stop infusion immediately
  - IV diphenhydramine 50 mg
  - IV methylprednisolone 100 mg
  - IV fluids (normal saline bolus)
  - Albuterol nebulised for bronchospasm
  - After resolution, restart at 50% reduced rate
- **Severe anaphylaxis (Grade 3-4):**
  - Stop infusion permanently (for that infusion)
  - IM epinephrine (0.3-0.5 mg of 1:1000)
  - IV fluids (crystalloid bolus)
  - IV methylprednisolone 125-250 mg
  - IV diphenhydramine 50 mg
  - Inhaled beta-agonist (albuterol)
  - ICU admission
  - Consider desensitisation protocol for future infusions
- **IVIG aseptic meningitis:** Slow infusion rate, hydration, analgesia (NSIADs may work but avoid in CKD)
- **IVIG renal failure:** Discontinue, nephrology consult, assess for tubular injury
- **Rituximab-related severe infusion reaction:** Consider permanent discontinuation; alternative anti-CD20 agent (ocrelizumab, ofatumumab)

#### Monitoring

- Vital signs throughout infusion and 1 hour post-infusion
- Oximetry monitoring during infusion
- Fluid balance (especially IVIG in CKD)
- Post-infusion haemoglobin (IVIG-related haemolysis)
- Renal function (IVIG-related renal injury)
- Headache monitoring (IVIG aseptic meningitis)
- Infection surveillance post-infusion (monoclonal antibody-associated immunosuppression)
- Drug-specific: CD19/20 counts (rituximab), complement levels (eculizumab)

#### Long-Term Consequences

- Discontinuation of effective therapy (if severe reactions)
- Desensitisation requirement (prolonged infusion protocols)
- Anti-drug antibodies development (reduced efficacy)
- Psychological impact (needle phobia, anticipatory anxiety)
- Aseptic meningitis (IVIG — resolves but may recur)
- IVIG-related haemolysis (rare, may require transfusion)
- Rituximab-related serum sickness (rare, Type III hypersensitivity)
- Graft rejection (if immunosuppressant discontinued)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Rituximab (off-label), belimumab, cyclophosphamide; higher cytokine release risk |
| `anca | High | Rituximab standard therapy; pre-medication essential |
| `membranous` | Moderate | Rituximab first-line; IVIG for severe hypogammaglobulinemia |
| `mcd` | Moderate | Rituximab for steroid-dependent disease |
| `fsgs` | Moderate | Rituximab for resistant cases |
| `iga` | Low | Rituximab limited role |
| `c3` | Moderate | Eculizumab off-label; infusion reactions rare |
| `antibodyMediatedRejection` | High | Rituximab, IVIG, eculizumab, bortezomib |
| `tCellMediatedRejection` | Moderate | ATG infusion reactions common |
| `bkVirusNephropathy` | Low | IVIG rarely used |
| `lupus` (pregnant) | Moderate | IVIG for refractory cases |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Rituximab | High | Cytokine release syndrome from B-cell lysis; Type I hypersensitivity |
| IVIG | Moderate | Complement activation, cytokine release; anaphylaxis in `iga` deficiency |
| Eculizumab | Low-Moderate | Complement inhibition; rare anaphylaxis |
| Alemtuzumab | High | Profound cytokine release from lymphocyte depletion |
| ATG | High | Cytokine release, serum sickness |
| Belimumab | Low-Moderate | Cytokine release; rare anaphylaxis |
| Bortezomib | Low-Moderate | Infusion reactions less common with SC route |
| Ocrelizumab | Moderate | Similar to rituximab |
| Ofatumumab | Moderate | Fully human anti-CD20; lower reaction rate than rituximab |

#### Guideline References

1. CRT Standards for Biologic Infusion Therapy. *J Infus Nurs.* 2020;43(4):203-217
2. Pottier V et al. Rituximab Infusion Reactions: Prevention and Management. *Ann Rheum Dis.* 2023;82(2):175-184
3. Perez-Alvarez R et al. Management of IVIG-Related Adverse Events. *J Allergy Clin Immunol Pract.* 2021;9(6):2278-2288
4. Hillmen P et al. Eculizumab Safety Profile. *Blood.* 2022;139(11):1674-1683

---
### 2.19 Progressive Multifocal Leukoencephalopathy (PML)

**Complication ID:** COMP-PML-001

#### Risk Factors

- Rituximab therapy (significant risk, especially cumulative or repeated courses)
- Prolonged immunosuppression (multiple agents, high intensity)
- Other monoclonal antibodies (belimumab, alemtuzumab, natalizumab)
- MMF and cyclophosphamide (rare, primarily in combination)
- Underlying autoimmune disease (lupus, ANCA vasculitis)
- HIV/AIDS
- Haematological malignancy (CLL, lymphoma)
- Transplant recipients (intense immunosuppression)
- Advanced age
- Lymphopenia (<500 cells/mcL)

#### Clinical Features

- **Subacute onset:** Days to weeks (not sudden)
- **Focal neurological deficits (most common):**
  - Motor: Hemiparesis, monoparesis, ataxia, gait disturbance
  - Speech: Dysarthria, aphasia (especially mixed transcortical aphasia)
  - Visual: Homonymous hemianopia, cortical blindness
  - Cognitive: Confusion, disorientation, personality changes, dementia
- **Seizures:** Focal or generalised (less common than in PRES)
- **Headache:** Present but less prominent
- **Absence of fever and meningismus (unlike encephalitis)
- **Progressive course:** Deterioration over weeks to months
- **Imaging:** MRI brain — T2/FLAIR hyperintense white matter lesions, typically subcortical, U-fibre involvement, no mass effect, no contrast enhancement (usually); lesions in parieto-occipital, frontal, cerebellar white matter
- **CSF:** JC virus DNA PCR (sensitivity 70-95%); negative PCR does not exclude PML
- **Brain biopsy:** Histology: Demyelination, enlarged oligodendrocyte nuclei with viral inclusions, bizarre astrocytes

#### Prevention

- **Screening:** JC virus serology (anti-JCV antibody index) before and during rituximab therapy (consider in high-risk patients)
- **Limit cumulative rituximab exposure:** Avoid repeated/prolonged courses without clear benefit
- **Monitor CD19/20 counts:** Prolonged B-cell depletion increases risk
- **Total lymphocyte count monitoring:** Sustained lymphopenia <500 cells/mcL warrants caution
- **Immunosuppression minimisation:** Reduce concurrent immunosuppressants during rituximab therapy
- **Avoid rituximab in JC virus-seropositive patients with additional risk factors** (if alternative therapy available)
- **Consider alternative anti-CD20 agent** (lower PML risk data available for ofatumumab, ocrelizumab)
- **No vaccine available**
- **Patient education:** Report any new neurological symptoms immediately

#### Early Detection

- Detailed neurological examination before each rituximab cycle
- High index of suspicion for any new, progressive neurological symptom — even subtle
- MRI brain with FLAIR sequence for any neurological change
- CSF JC virus PCR (confirmatory; negative PCR does not rule out)
- Repeated MRI in 2-4 weeks if initial MRI non-diagnostic but symptoms persist
- Brain biopsy if MRI and CSF inconclusive but high clinical suspicion
- Detection of JCV DNA in blood (plasma) may be a risk marker but not diagnostic
- Regular neurological symptom screening questionnaire

#### Treatment

- **Immunosuppression reversal (first-line and essential):**
  - Stop rituximab immediately (or other immunosuppressant)
  - Reduce or stop other immunosuppressants (MMF, steroids, CNIs) if safe
  - Plasma exchange to remove rituximab if recently administered (limited evidence)
- **No specific antiviral therapy:**
  - Mirtazapine: SHT2A receptor antagonist; limited evidence of benefit
  - Cidofovir: No proven benefit; nephrotoxic — avoid in GN patients
  - Cytarabine: No proven benefit; myelosuppressive
  - Checkpoint inhibitors (pembrolizumab, nivolumab): Emerging therapy; restores T-cell function; case series show benefit
- **Supportive care:** Seizure management, physical therapy, occupational therapy, speech therapy
- **ART (in HIV-associated PML):** Restoration of immune function (standard HIV care)
- **IVIG:** No proven benefit
- **Prognosis:** 30-50% mortality; survivors may have significant neurological deficits

#### Monitoring

- MRI brain every 4-8 weeks (assess lesion evolution)
- JC virus PCR in CSF (may correlate with viral load; can become negative with immune reconstitution)
- Neurological examination weekly (during acute phase)
- Immune reconstitution monitoring (CD4 count, lymphocyte count)
- IRIS (immune reconstitution inflammatory syndrome) monitoring — may cause paradoxical worsening
- Quality of life and functional status assessment
- Reintroduction of immunosuppression cautiously (if needed for underlying disease)

#### Long-Term Consequences

- **Death:** 30-50% mortality within months
- **Permanent neurological deficits:** Hemiparesis, aphasia, visual loss, cognitive impairment
- **Disability:** Permanent nursing care or assisted living in severe cases
- **IRIS:** Worsening symptoms with immune reconstitution (may need steroids)
- **Discontinuation of effective immunosuppression:** Risk of disease flare
- **Graft loss** (in transplant patients with immunosuppression withdrawal)
- **Psychological impact:** Devastating diagnosis; anxiety, depression
- **Survivors:** Often left with significant functional limitations

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Rare (most reported) | Rituximab + MMF combination; `lupus` itself may be a co-factor |
| `anca | Very Rare | Rituximab therapy; case reports exist |
| `membranous` | Very Rare | Rituximab for resistant disease |
| `mcd` | Very Rare | Rituximab for steroid-dependent disease |
| `antibodyMediatedRejection` | Very Rare | Rituximab + IVIG + bortezomib combination |
| `lupus` (pediatric) | Extremely Rare | Case reports; rituximab exposure |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Rituximab | Moderate (cumulative) | B-cell depletion impairs anti-JCV immune surveillance |
| Belimumab | Low-Moderate | BAFF inhibition; PML cases reported |
| Alemtuzumab | Moderate | Profound lymphocyte depletion |
| MMF | Low | Rare PML in combination therapy |
| Cyclophosphamide | Low | Rare; primarily in combination |
| Azathioprine | Low | Rare cases reported |
| Natalizumab | High (MS patients) | Integrin inhibition; high PML risk with JCV seropositivity (not used in GN) |
| Ocrelizumab | Low-Moderate | Limited data; appears lower than rituximab |
| Corticosteroids | Low | PML co-factor; no direct causation |

#### Guideline References

1. Berger JR et al. PML in Patients With Autoimmune Disease. *Neurology.* 2020;94(11):477-486
2. Koralnik IJ. Progressive Multifocal Leukoencephalopathy. *N Engl J Med.* 2023;389(17):1588-1599
3. Carson KR et al. Monoclonal Antibody-Associated PML: A Review. *Lancet Neurol.* 2021;20(9):756-767
4. Tan CS, Koralnik IJ. PML in Immunocompromised Patients. *J Neurovirol.* 2022;28(4):491-503

---
### 2.20 Tuberculosis Reactivation

**Complication ID:** COMP-TB-001

#### Risk Factors

- Past or latent TB infection (LTBI — positive IGRA/TST)
- Anti-TNF therapy (infliximab, adalimumab, etanercept — highest risk among biologics)
- High-dose corticosteroid therapy (prednisolone >15 mg/day for >4 weeks)
- Cyclophosphamide therapy (lymphodepletion)
- MMF therapy (moderate risk)
- Transplant recipients (T-cell depletion)
- CKD/ESKD (impaired cellular immunity)
- Malnutrition
- Diabetes mellitus
- Country of origin (TB-endemic regions: Indian subcontinent, sub-Saharan Africa, Southeast Asia)
- Prior TB (incomplete or non-adherent treatment)
- Vocational exposure (healthcare, prison, congregate settings)
- Silicosis
- HIV co-infection

#### Clinical Features

- **Pulmonary TB (most common, 50-70%):**
  - Persistent cough (>3 weeks), initially dry then productive
  - Haemoptysis (frank blood or blood-streaked sputum)
  - Fever (low-grade, evening pyrexia)
  - Night sweats
  - Weight loss and anorexia
  - Pleuritic chest pain, pleural effusion
- **Extrapulmonary TB (up to 40% in immunocompromised):**
  - Lymphadenitis (most common extrapulmonary — cervical, mediastinal)
  - Genitourinary (sterile pyuria, haematuria, renal TB)
  - Skeletal (Pott disease — vertebral osteomyelitis, paravertebral abscess)
  - CNS (TB meningitis, tuberculomas)
  - Miliary (disseminated, millet-like nodules on CXR)
  - Abdominal (peritoneal, GI, hepatic)
- **Atypical presentation in immunocompromised:** Disseminated/miliary more common; less cavitation; lower lobe predominance; lower yield on sputum smear; higher mortality

#### Prevention

- **Screening for LTBI before immunosuppression:**
  - IGRA (interferon-gamma release assay) preferred over TST (false negatives in immunocompromised)
  - CXR for evidence of old, untreated TB
  - Screen all patients initiating anti-TNF, high-dose steroids, cyclophosphamide, rituximab, or transplant listing
- **LTBI treatment:**
  - Standard: INH 300 mg daily + rifampicin 600 mg daily for 3 months (3HP) OR INH alone for 6-9 months
  - Alternative: Rifampicin 600 mg daily for 4 months
  - Complete LTBI treatment before or concurrent with initial immunosuppression
- **Annual TB screening for transplant recipients** (CXR + IGRA)
- **Infection control:** Respiratory isolation for suspected active TB
- **BCG vaccination:** Contraindicated in established immunosuppression but may be considered pre-immunosuppression in high-risk patients
- **Nutritional support (malnutrition increases risk)**

#### Early Detection

- Annual IGRA screening in high-risk patients on chronic immunosuppression
- CXR for any persistent respiratory symptoms
- Sputum for smear microscopy, culture, and GeneXpert MTB/RIF for rapid diagnosis
- CT chest for suspected pulmonary TB with normal CXR
- Lymph node biopsy (FNAC or excision) for suspected TB lymphadenitis
- CSF analysis (ADA, GeneXpert, culture) for TB meningitis
- Renal TB: Urine culture for TB (three early morning samples)
- GeneXpert Ultra (higher sensitivity than standard Xpert)
- TB culture (gold standard; 4-6 weeks for positivity)
- Molecular testing (line probe assay for resistance)
- Therapeutic trial of anti-TB therapy (in high clinical suspicion)

#### Treatment

- **Standard regimen (drug-sensitive TB):**
  - Intensive phase (2 months): Isoniazid, rifampicin, pyrazinamide, ethambutol (HRZE)
  - Continuation phase (4 months): Isoniazid, rifampicin (HR)
  - Duration: 6 months total (9-12 months for CNS, bone TB)
- **Renal dose adjustment:**
  - Isoniazid: No adjustment (hepatic excretion)
  - Rifampicin: No adjustment (hepatic excretion; significant drug interactions)
  - Pyrazinamide: No adjustment (hepatic)
  - Ethambutol: Dose-adjust for eGFR <30 (reduce to 15-25 mg/kg 3x/week or Q48H)
- **Drug-resistant TB:** MDR-TB regimen (fluoroquinolone, injectable/second-line agents); longer duration (9-24 months)
- **Drug interactions:**
  - Rifampicin: Potent CYP3A4 inducer — reduces CNI levels by 50-80% (monitor troughs, increase dose)
  - Rifampicin reduces corticosteroid levels (double steroid dose if on RIF)
  - Rifampicin reduces OCP efficacy (contraceptive counselling)
- **Corticosteroids:** Indicated for TB meningitis, pericarditis (adjunctive therapy)
- **Directly observed therapy (DOT)** recommended
- **Notification:** Report to public health authorities

#### Monitoring

- Sputum smear and culture at 2, 5, 6 months (confirms treatment response)
- GeneXpert for rifampicin resistance if no clinical response
- CXR at 2 months and end of treatment
- Liver function tests (monthly — INH and rifampicin hepatotoxicity)
- CNI trough levels (weekly during rifampicin co-administration until stable)
- Renal function (ethambutol dosing)
- Visual acuity and colour vision (ethambutol optic neuropathy — monthly)
- Uric acid (pyrazinamide — hyperuricaemia)
- Drug adherence monitoring (DOT, pill counts)
- Clinical response: fever resolution, weight gain, cough improvement (expected by 2-4 weeks)

#### Long-Term Consequences

- TB-related lung damage (cavitation, bronchiectasis, fibrosis)
- Post-TB obstructive lung disease
- Chronic pulmonary aspergillosis (in cavitary TB)
- Miliary TB mortality (high in immunocompromised — 20-50%)
- TB meningitis neurological sequelae (hydrocephalus, cognitive impairment, focal deficits)
- Pott disease (spinal deformity, paraplegia)
- Drug-induced hepatotoxicity (INH, rifampicin)
- Ethambutol optic neuropathy (irreversible)
- Permanent CNI dose modification (due to rifampicin interaction)
- Graft rejection (inadequate immunosuppression during TB treatment)
- Drug resistance (if adherence poor or initial resistance)
- Relapse (especially if immunosuppression is not minimised)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | High-dose steroids + cyclophosphamide; endemic region for many patients |
| `anca | Moderate | Cyclophosphamide + high-dose steroids; consider LTBI screening before rituximab/CyP |
| `diabeticNephropathy` | Moderate | DM increases TB risk 2-3x; CKD compounds |
| `membranous` | Low-Moderate | Rituximab therapy; screen before initiation |
| `iga` | Low | Low immunosuppression intensity |
| `mcd` | Low | Steroid therapy; short courses |
| `fsgs | Low | Variable; depends on immunosuppression intensity |
| `antibodyMediatedRejection` | High | Transplant + intense immunosuppression + anti-TNF (rare) |
| `tCellMediatedRejection` | High | Transplant + pulse steroids + T-cell depletion |
| `bkVirusNephropathy` | Moderate | Transplant + immunosuppression burden |
| `transplantGlomerulopathy` | Moderate | Long-term immunosuppression |
| `cniToxicity` | Moderate | Transplant setting |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Prednisolone (>15 mg/day chronic) | High | Impaired macrophage function, reduced T-cell responses |
| Methylprednisolone (pulse) | High | Potent and prolonged effect on cellular immunity |
| Anti-TNF agents (infliximab, adalimumab, etanercept) | Very High | TNF-alpha is critical for granuloma maintenance and macrophage activation |
| Cyclophosphamide | High | Lymphodepletion, impaired delayed-type hypersensitivity |
| MMF | Moderate | Impaired lymphocyte activation and proliferation |
| Tacrolimus | Moderate | T-cell suppression |
| Belatacept | Moderate | T-cell co-stimulation blockade |
| ATG | High | Profound T-cell depletion |
| Alemtuzumab | High | Profound lymphocyte depletion |
| Rituximab | Low-Moderate | B-cell depletion; limited data on TB risk |
| Belimumab | Low | No significant TB risk reported |

#### Guideline References

1. KDIGO 2023 TB in CKD and Transplant Guideline. *Transplantation.* 2023;107(5):987-1003
2. WHO Global Tuberculosis Report 2023. Geneva: WHO; 2023
3. Getahun H et al. Management of Latent Mycobacterium tuberculosis Infection. *Lancet.* 2019;393(10185):2142-2156
4. Milburn J et al. Tuberculosis in Renal Disease and Transplantation. *Nephrol Dial Transplant.* 2022;37(3):441-453

---
### 2.21 Hepatitis B Reactivation

**Complication ID:** COMP-HBV-001

#### Risk Factors

- HBsAg-positive (highest risk)
- Anti-HBc-positive (resolved infection; low-level persistent virus in liver)
- Rituximab therapy (highest risk among immunosuppressants used in GN)
- Cyclophosphamide therapy (high risk)
- High-dose corticosteroids (prednisolone >20 mg/day)
- Transplant immunosuppression (ATG, alemtuzumab)
- Combination immunosuppression (rituximab + steroids + CyP — additive risk)
- Malignancy (PTLD, lymphoma)
- HBV viral load at baseline (higher viral load = higher reactivation risk)
- HBeAg-positive (active viral replication)
- Pre-core mutant HBV (HBeAg-negative but high viral load)
- Male sex
- Liver fibrosis/cirrhosis at baseline

#### Clinical Features

- **Asymptomatic (most common):** Detected on routine HBV DNA monitoring
- **Hepatitis flare:**
  - Fatigue, malaise, anorexia, nausea
  - Right upper quadrant pain
  - Jaundice, dark urine, pale stools
  - Elevated ALT/AST (may be >10x ULN)
  - Bilirubin elevation
- **Severe reactivation:**
  - Hepatic decompensation (ascites, encephalopathy, coagulopathy)
  - Acute liver failure (rare but life-threatening)
  - Death (fulminant hepatitis — 10-20% mortality)
- **Timing:**
  - Rituximab-associated: Usually 6-12 months after first dose (may occur up to 24 months post-treatment)
  - Cyclophosphamide: Variable; typically during or shortly after therapy
  - Steroid withdrawal: May trigger flare (immune reconstitution)
- **Sequelae:** Hepatic fibrosis progression, cirrhosis, hepatocellular carcinoma

#### Prevention

- **Screening (mandatory before immunosuppression):**
  - HBsAg, anti-HBs, anti-HBc (total) for all patients initiating rituximab, cyclophosphamide, high-dose steroids, or transplant immunosuppression
  - HBV DNA by PCR if HBsAg+ or anti-HBc+
- **Prophylactic antiviral therapy:**
  - First-line: Entecavir 0.5 mg daily (no dose adjustment for renal function; 0.5 mg Q48H if GFR <50; 0.5 mg 3x/week post-dialysis)
  - Alternative: Tenofovir disoproxil fumarate (TDF) 300 mg daily (dose-adjust for GFR; monitor renal function)
  - Alternative: Tenofovir alafenamide (TAF) 25 mg daily (better renal/bone profile)
- **Duration of prophylaxis:**
  - HBsAg+: Continue antiviral for at least 12-18 months after cessation of immunosuppression; longer if pre-existing cirrhosis or continued immunosuppression
  - Anti-HBc+ (HBsAg-): Continue antiviral for 6-12 months after cessation of immunosuppression
- **Lamivudine:** No longer first-line due to high resistance rate (only use if no alternatives and short duration)
- **Vaccination:** HBV vaccine for all seronegative patients before immunosuppression (if time permits)

#### Early Detection

- Monthly HBV DNA PCR during immunosuppression (for HBsAg+ or anti-HBc+)
- Monthly ALT monitoring (more frequent if HBsAg+)
- Clinical symptom surveillance (jaundice, abdominal pain, fatigue)
- HBsAg seroreversion monitoring in anti-HBc+ (reappearance of HBsAg)
- Post-prophylaxis monitoring: ALT and HBV DNA every 3 months for 12 months after antiviral cessation
- Ultrasound surveillance (if cirrhosis at baseline)
- Alpha-fetoprotein (if cirrhosis or high HCC risk)

#### Treatment

- **Confirmed reactivation (HBV DNA >2,000 IU/mL or rising, with ALT elevation):**
  - Start/resume entecavir or tenofovir immediately
  - Hold or reduce immunosuppression if safe (balance with underlying disease control)
  - Monitor for hepatic decompensation
- **Severe hepatitis flare:**
  - Hospitalisation
  - Entecavir or tenofovir (rescue therapy)
  - Hold all immunosuppression
  - Consider N-acetylcysteine (for acute liver failure)
  - Liver transplant evaluation (if fulminant)
- **Persistent reactivation despite prophylaxis:**
  - Check HBV resistance testing (especially if on lamivudine)
  - Switch to alternative antiviral
  - Consider HBV genotype testing
- **Post-exposure prophylaxis:** If accidental needlestick or mucosal exposure, give HBVIG + vaccine booster

#### Monitoring

- **During immunosuppression:** HBV DNA and ALT monthly (HBsAg+) or 1-3 monthly (anti-HBc+)
- **Post-immunosuppression:** HBV DNA and ALT every 3 months for 12 months
- **Chronic suppression:** HBV DNA every 6-12 months; ALT every 3-6 months
- **Liver fibrosis assessment:** Transient elastography (FibroScan) or FIB-4 score every 1-2 years if chronic HBV
- **HCC surveillance:** Ultrasound + AFP every 6 months if cirrhosis or high-risk group
- **Renal function:** Serum creatinine and phosphate (for TDF); consider switch to TAF if renal toxicity
- **Antiviral adherence:** Pill counts, refill records

#### Long-Term Consequences

- Chronic HBV infection (if de novo or reactivation leads to chronicity)
- Hepatic fibrosis and cirrhosis progression
- Hepatocellular carcinoma (HCC) development
- Liver failure requiring transplantation
- Acute-on-chronic liver failure (ACLF) with high mortality
- Flare-related mortality (5-15%)
- Need for long-term antiviral therapy
- Drug resistance (if prior lamivudine exposure)
- Immunosuppression limitation (unable to use rituximab/CyP in future)
- Graft rejection (if immunosuppression held)
- HBV transmission risk (public health concern)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | Rituximab + cyclophosphamide; screen before each immunosuppressive regimen |
| `anca | Moderate | Rituximab standard; cyclophosphamide for refractory disease |
| `membranous` | Low-Moderate | Rituximab first-line; consider HBV screening before initiation |
| `mcd` | Low | Rituximab for steroid-dependent disease |
| `iga` | Low | Cyclophosphamide in crescentic disease |
| `antibodyMediatedRejection` | Moderate | Rituximab + IVIG; screen anti-HBc+ patients |
| `tCellMediatedRejection` | Low | Pulse steroids; lower risk |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Rituximab | Very High | B-cell depletion impairs anti-HBV humoral immunity; highest reactivation risk |
| Cyclophosphamide | High | Lymphodepletion, impaired T-cell control of HBV |
| Prednisolone (high-dose, chronic) | High | Glucocorticoid response element on HBV genome increases replication |
| Methylprednisolone (pulse) | High | Similar mechanism |
| ATG | High | T-cell depletion impairs viral control |
| Alemtuzumab | Very High | Profound lymphocyte depletion |
| Belatacept | Moderate | T-cell co-stimulation blockade |
| CNI (tacrolimus, cyclosporine) | Low-Moderate | T-cell suppression; lower risk than B-cell or T-cell depleting agents |
| MMF | Low-Moderate | Lymphocyte inhibition; lower risk than rituximab |
| Azathioprine | Low | Modest risk |
| Entecavir/Tenofovir (prophylaxis) | Protective | Suppresses HBV replication (therapeutic) |

#### Guideline References

1. Terrault NA et al. AASLD Guidelines for Treatment of Chronic Hepatitis B. *Hepatology.* 2022;75(6):1502-1537
2. Lampertico P et al. EASL 2017 Clinical Practice Guidelines on the Management of Hepatitis B Virus Infection. *J Hepatol.* 2017;67(2):370-398
3. Mitka M et al. HBV Reactivation in Patients Treated With Immunosuppressive Drugs. *J Viral Hepat.* 2023;30(4):286-298
4. Reddy KR et al. Prevention and Management of Hepatitis B Reactivation in Patients Receiving Immunosuppressive Therapy. *Am J Gastroenterol.* 2024;119(1):82-99

---
### 2.22 Cytopenias

**Complication ID:** COMP-CYTO-001

#### Risk Factors

- MMF therapy (leucopenia most common, anaemia, thrombocytopenia)
- Cyclophosphamide therapy (neutropenia dose-dependent, lymphopenia)
- Azathioprine therapy (leucopenia, especially with TPMT deficiency)
- Rituximab therapy (B-cell lymphopenia, late-onset neutropenia)
- CNI therapy (tacrolimus — thrombotic microangiopathy, haemolytic anaemia)
- mTOR inhibitors (sirolimus, everolimus — thrombocytopenia, leucopenia)
- Belatacept (mild anaemia, leucopenia)
- ATG/alemtuzumab (profound lymphopenia)
- Corticosteroids (lymphopenia)
- TPMT deficiency (azathioprine toxicity)
- CKD/ESKD (anaemia of CKD, impaired EPO production)
- Prior cumulative myelosuppression (from chemotherapy or immunosuppression)
- Bone marrow infiltration (PTLD, amyloid)
- Nutritional deficiencies (iron, B12, folate in CKD/nephrotic syndrome)

#### Clinical Features

- **Neutropenia (ANC <1500/mm³):**
  - Increased infection risk (especially when ANC <500/mm³)
  - Asymptomatic until infection develops
  - Fever, oral ulcers, pharyngitis, pneumonia, sepsis
- **Lymphopenia (<1000/mm³):**
  - Increased viral and opportunistic infection risk
  - Usually asymptomatic
  - PTLD risk (impaired EBV surveillance)
- **Anaemia (Hb <11 g/dL):**
  - Fatigue, pallor, dyspnoea on exertion
  - Exercise intolerance
  - Pallor, tachycardia, flow murmur
- **Thrombocytopenia (<100,000/mm³):**
  - Petechiae, purpura, easy bruising
  - Epistaxis, gingival bleeding
  - Prolonged bleeding from wounds/injection sites
  - Major bleeding (GI, intracranial) — rare, usually with platelets <20,000
- **Pancytopenia:** Features of all three lineages; bone marrow failure

#### Prevention

- **Dose monitoring and adjustment:**
  - MMF: Reduce dose if neutropenic (ANC <1000); hold if <500
  - Azathioprine: TPMT genotyping/phenotyping before initiation; reduce dose if TPMT deficient
  - Cyclophosphamide: CBC monitoring to guide dosing; dose-reduce if nadir ANC <1500
- **CBC monitoring schedule:**
  - Weekly for first month of MMF, cyclophosphamide, azathioprine
  - Monthly for established therapy
  - More frequent if dose changes or cytopenia detected
- **G-CSF support:** For febrile neutropenia or prolonged neutropenia (filgrastim, pegfilgrastim)
- **EPO support:** For anaemia (darbepoetin alfa, epoetin alfa); target Hb 10-11 g/dL
- **Folate supplementation:** For all patients on MMF or azathioprine (1 mg daily)
- **B12/iron repletion:** Before immunosuppression initiation if deficient
- **Dose reduction or switch:** If persistent cytopenia despite adjustment
- **PJP prophylaxis** (TMP-SMX) during neutropenia
- **Avoid live vaccines** during significant immunosuppression

#### Early Detection

- CBC with differential (schedule as above)
- Symptom screening (fatigue, infection history, bleeding)
- Physical examination (pallor, petechiae, lymphadenopathy)
- Reticulocyte count for anaemia workup
- TPMT testing (for azathioprine)
- Late-onset neutropenia after rituximab: CBC 6-12 months post-treatment
- Vitamin B12, folate, iron studies (if anaemia disproportionate to CKD)
- Bone marrow examination if unexplained/persistent cytopenia despite drug adjustment
- Peripheral blood smear (haemolysis, fragmentation in CNI-TMA)

#### Treatment

- **MMF-induced leucopenia:** Dose reduction (by 50% or hold); switch to EC-MPS if persistent; consider G-CSF
- **Cyclophosphamide-induced neutropenia:** Hold until ANC >1500; dose-reduce next cycle; G-CSF for febrile neutropenia
- **Azathioprine-induced leucopenia (TPMT-related):** Stop azathioprine; switch to MMF or other alternative; supportive care until recovery
- **Rituximab late-onset neutropenia:** G-CSF support; usually self-limiting; avoid further rituximab dosing until ANC recovers
- **CNI-TMA (thrombotic microangiopathy):** Stop/reduce CNI; consider eculizumab, plasma exchange; switch to belatacept
- **Anaemia:** EPO (darbepoetin 30-60 mcg Q2W or epoetin 4000-8000 U Q2W); iron supplementation (IV ferric carboxymaltose, iron sucrose)
- **Thrombocytopenia:** Dose reduction of offending agent; platelet transfusion if <20,000 or active bleeding
- **Pancytopenia:** Hold all myelosuppressive drugs; bone marrow biopsy to exclude PTLD, AML, infection; G-CSF + EPO + platelet support
- **Treatment of underlying disease flare** (if cytopenia from disease activity — lupus, ANCA)
- **Hypersplenism:** Consider splenectomy if refractory (rare)

#### Monitoring

- CBC with differential (frequency based on drug and severity)
- Reticulocyte count for anaemia evaluation
- Iron studies, B12, folate (for anaemia workup)
- TPMT genotype (azathioprine-treated patients)
- CD19/20 counts (rituximab-treated)
- Peripheral blood smear (if suspicion of TMA, haemolysis)
- Reticulocyte production index (marrow response)
- Bone marrow biopsy (if unexplained persistent cytopenia)
- Infection surveillance during neutropenia
- Blood and urine cultures for febrile neutropenia
- G-CSF duration and response monitoring

#### Long-Term Consequences

- Treatment interruption or discontinuation (risk of disease flare or rejection)
- Reduced immunosuppression efficacy from dose reduction
- Opportunistic infections (PJP, CMV, fungal) during prolonged neutropenia
- Growth factor dependence (G-CSF, EPO)
- Transfusion dependence (rare)
- Bone marrow failure (very rare — drug-induced aplastic anaemia)
- Secondary MDS/AML (very rare, primarily with cyclophosphamide)
- Reduced quality of life from chronic fatigue, infection susceptibility
- Increased hospitalisation and antibiotic use
- Antimicrobial resistance from frequent infections

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | Baseline cytopenia from SLE itself + immunosuppression; overlapping aetiologies |
| `lupus` (Class III/IV) | High | MMF + cyclophosphamide combination in induction |
| `anca` | High | Cyclophosphamide + rituximab; RTX late-onset neutropenia |
| `membranous` | Moderate | MMF or cyclophosphamide; rituximab |
| `mcd` | Moderate | MMF + rituximab in steroid-dependent disease |
| `fsgs` | Moderate | MMF + CNI; cyclophosphamide in resistant cases |
| `iga` | Low-Moderate | MMF for select patients; azathioprine limited use |
| `antibodyMediatedRejection` | High | MMF + CNI + rituximab + bortezomib — multi-agent cytopenia |
| `tCellMediatedRejection` | High | MMF + CNI + ATG — profound lymphopenia |
| `transplantGlomerulopathy` | Moderate | MMF + CNI maintenance |
| `bkVirusNephropathy` | Moderate | MMF dose reduction may help cytopenia but risks rejection |
| `cniToxicity` | Low | Pure CNI effect minimal; TMA is rare |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| MMF | High | IMPDH inhibitor; lymphopenia, leucopenia; dose-dependent |
| Cyclophosphamide | High | Alkylating agent causing bone marrow suppression; nadir at 10-14 days |
| Azathioprine | High | Purine analogue; TPMT deficiency increases toxicity 10-fold |
| Rituximab | Moderate | B-cell depletion; late-onset neutropenia (1-2%) |
| Alemtuzumab | Very High | Profound, prolonged pan-lymphopenia |
| ATG | Very High | Profound T-cell depletion; thrombocytopenia common |
| Tacrolimus | Low-Moderate | TMA (rare); neutropenia uncommon |
| Cyclosporine | Low-Moderate | TMA; haemolytic anaemia (rare) |
| Sirolimus | Moderate | Thrombocytopenia, leucopenia; dose-dependent |
| Everolimus | Moderate | Similar to sirolimus |
| Belatacept | Low | Mild anaemia, leucopenia |
| Bortezomib | Moderate | Thrombocytopenia (transient, 40-60%) |
| Belimumab | Low | Mild leucopenia |
| G-CSF (therapeutic) | Protective | Reverse neutropenia |
| EPO (therapeutic) | Protective | Reverse anaemia |

#### Guideline References

1. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
2. KDIGO 2023 Transplant Guideline. *Transplantation.* 2023;107(6S):S1-S216
3. Saltissi D et al. Myelotoxicity of Immunosuppressive Drugs. *Drug Saf.* 2022;45(4):341-357
4. Kridin K et al. Late-Onset Neutropenia After Rituximab. *J Am Acad Dermatol.* 2021;84(5):1338-1346

---
### 2.23 Gastrointestinal Toxicity

**Complication ID:** COMP-GI-001

#### Risk Factors

- MMF therapy (diarrhoea most common — 20-40%)
- Corticosteroid therapy (gastritis, peptic ulcer, pancreatitis)
- Cyclophosphamide therapy (nausea, vomiting, mucositis, diarrhoea)
- Azathioprine therapy (nausea, vomiting, hepatotoxicity, pancreatitis)
- mTOR inhibitors (oral ulcers, diarrhoea, nausea)
- CNI therapy (hepatic enzyme elevation, diarrhoea)
- Rituximab (rare GI perforation)
- Oral vs IV route (some agents better tolerated orally)
- High doses, rapid dose escalation
- Pre-existing GI disease (IBD, gastritis, GERD)
- Concurrent NSAIDs or anticoagulants (GI bleeding risk)
- H pylori infection (steroid-induced ulcer risk)
- Advanced age, frailty
- Malnutrition

#### Clinical Features

- **MMF-related:**
  - Diarrhoea (most common, 20-40%): Watery, non-bloody, cramping
  - Nausea, vomiting, dyspepsia, anorexia
  - Enteric-coated MPS (Myfortic) may reduce GI symptoms vs CellCept
  - Symptoms often dose-dependent and worse on initiation
- **Steroid-related:**
  - Gastritis, dyspepsia, heartburn
  - Peptic ulcer disease (PU — gastric > duodenal)
  - GI bleeding (melena, haematemesis)
  - Pancreatitis (rare)
  - Fatty liver, hepatic steatosis
- **Cyclophosphamide-related:**
  - Nausea and vomiting (significant — 50-70% without antiemetics)
  - Mucositis (oral ulcers, stomatitis)
  - Diarrhoea
  - Haemorrhagic colitis (rare)
- **Azathioprine-related:**
  - Nausea (dose-dependent; may resolve with time or split dosing)
  - Pancreatitis (distinctive — 2-5%; usually within first 6-8 weeks)
  - Hepatotoxicity (elevated transaminases)
- **mTOR inhibitor-related:**
  - Oral aphthous ulcers (very common — 30-60%)
  - Diarrhoea, nausea, anorexia
  - Dose-dependent; prophylaxis with mouthwashes
- **CNI-related:**
  - Diarrhoea (tacrolimus more than cyclosporine)
  - Nausea, vomiting
  - Hepatotoxicity (elevated LFTs)
- **Belatacept-related:** Nausea, diarrhoea, constipation (mild to moderate)

#### Prevention

- **MMF:**
  - Start at low dose, titrate up gradually
  - Divide doses (BID -> TID/QID may reduce GI symptoms)
  - Switch to enteric-coated mycophenolate sodium (EC-MPS, Myfortic)
  - Administer with food (decreases peak levels but reduces GI symptoms)
  - Consider azathioprine as alternative (if tolerability issue)
- **Steroids:**
  - PPI or H2-receptor antagonist prophylaxis for high-risk patients (history of PU, >20 mg prednisolone daily, NSAID co-use)
  - Administer with food
  - Rapid taper to lowest effective dose
- **Cyclophosphamide:**
  - Antiemetic prophylaxis (ondansetron, metoclopramide, арrepitant)
  - Adequate hydration during infusion
  - Split oral dosing (if oral regimen)
- **Azathioprine:**
  - Start at 50 mg/day, titrate up over 2-4 weeks
  - Split dosing (BID or TID)
  - Administer with food
  - TPMT genotype before start (prevents severe toxicity)
- **mTOR inhibitors:**
  - Start low, titrate slowly
  - Dexamethasone mouthwash (0.5 mg/10 mL) swish and spit for oral ulcers
  - Clobetasol or triamcinolone oral paste for aphthous ulcers
  - Avoid acidic, spicy, rough-textured foods
- **CNI:** Monitor LFTs; dose adjustments if hepatotoxicity

#### Early Detection

- Symptom screening at every visit (diarrhoea, nausea, vomiting, abdominal pain, dyspepsia)
- Stool frequency and character diary (MMF diarrhoea)
- Evaluation for infectious causes of diarrhoea (CMV, C diff, bacterial) before attributing to drug
- Oesophagogastroduodenoscopy (OGD) for persistent dyspepsia, suspected PU
- Faecal calprotectin (if IBD-like symptoms on MMF)
- Abdominal imaging if pancreatitis suspected (amylase/lipase + CT abdomen)
- LFT monitoring (azathioprine, CNI, MMF)
- H pylori testing (if steroid-related PU suspected)
- Oral examination (mTOR aphthous ulcers, cyclophosphamide mucositis)

#### Treatment

- **MMF diarrhoea:**
  - Exclude infection (CMV, C diff, bacterial stool culture)
  - Reduce MMF dose (25-50%)
  - Switch to EC-MPS
  - Antidiarrhoeal agents (loperamide) for symptom control
  - If severe: hold MMF temporarily, reintroduce at lower dose
  - Switch to azathioprine if intolerance persists
- **Steroid-related PU:**
  - PPI (omeprazole 20-40 mg daily, pantoprazole 40 mg daily)
  - H pylori eradication if positive
  - Continue PPI throughout steroid course in high-risk patients
  - Endoscopy for GI bleeding
- **Cyclophosphamide nausea:**
  - Antiemetics (ondansetron 8 mg BID, metoclopramide 10 mg TID)
  - арrepitant for highly emetogenic regimens
  - Adequate hydration
  - Consider IV route if oral intolerance
- **Azathioprine pancreatitis:**
  - Stop azathioprine permanently (do not rechallenge)
  - Switch to MMF or alternative
  - Supportive care (NPO, IV fluids, analgesia)
- **mTOR oral ulcers:**
  - Dexamethasone mouthwash (0.5 mg/10 mL TID for 3-5 days)
  - Topical anaesthetics (lidocaine gel)
  - Dose reduction or temporary hold
  - Consider switch to everolimus (lower rate grade 3-4 ulcers)
- **CNI hepatotoxicity:** Dose reduction; consider switch to belatacept if persistent

#### Monitoring

- Symptom assessment at every visit (diarrhoea, pain, nausea, oral ulcers)
- Weight and nutritional status (malabsorption from diarrhoea)
- Stool culture and C diff testing (MMF diarrhoea before attributing to drug)
- CMV PCR in stool/blood (if diarrhoea with fever, leucopenia)
- Amylase/lipase (if azathioprine or steroid-related pancreatitis suspected)
- LFTs (monthly for azathioprine, CNI, MMF)
- Oral exam (mTOR inhibitors)
- Endoscopy for persistent symptoms or GI bleeding
- Faecal calprotectin (if MMF-related IBD-like inflammation)
- Drug level monitoring (CNI, mTOR inhibitors)

#### Long-Term Consequences

- Malnutrition and weight loss (chronic diarrhoea)
- MMF dose reduction may increase rejection risk
- GI bleeding (steroid-related PU) with risk of transfusion dependence
- Azathioprine intolerance (pancreatitis) requiring drug switch
- Drug discontinuation (loss of effective therapy)
- Quality of life impairment (chronic diarrhoea, oral pain)
- Electrolyte disturbances (chronic diarrhoea)
- Anaemia (GI bleeding, malabsorption)
- PPI dependence (long-term side effects of PPIs: CKD, osteoporosis, C diff, hypomagnesaemia)
- IBD-like colitis (MMF — may mimic Crohn disease histologically)
- Drug-drug interactions (PPIs with MMF reduce MMF absorption)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | High | MMF standard therapy; `lupus` itself can cause GI symptoms |
| `mcd` | Moderate | MMF + steroid combination; short courses |
| `membranous` | Moderate | MMF or cyclophosphamide; rituximab less GI toxic |
| `fsgs` | Moderate | MMF + steroid + CNI combination; cumulative GI toxicity |
| `iga` | Moderate | MMF in select patients; steroid-sparing |
| `anca | High | Cyclophosphamide GI toxicity significant; rituximab preferred |
| `antiGbm` | Moderate | Cyclophosphamide + PLEX + steroids |
| `antibodyMediatedRejection` | High | MMF + CNI + rituximab; multi-drug GI effects |
| `tCellMediatedRejection` | High | MMF + CNI + steroid pulses |
| `transplantGlomerulopathy` | Moderate | MMF + CNI maintenance |
| `bkVirusNephropathy` | Moderate | MMF + CNI |
| `cniToxicity` | Moderate | CNI-related GI effects |
| `fibrillaryGlomerulonephritis` | Low-Moderate | MMF or cyclophosphamide |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| MMF | High | IMPDH inhibition in GI mucosa; increased apoptosis, villous atrophy; enteric-coated MPS better tolerated |
| Mycophenolate sodium (EC-MPS) | Moderate | Enteric coating reduces upper GI exposure; may still cause diarrhoea |
| Cyclophosphamide | High | Direct mucosal toxicity; emetogenic via CTZ stimulation |
| Azathioprine | High | Mucosal toxicity; TPMT deficiency severe; pancreatitis (2-5%) |
| Prednisolone (>20 mg/day) | Moderate-High | Reduced mucosal prostaglandin synthesis; PU risk; increased acid secretion |
| Tacrolimus | Moderate | Direct GI mucosal effect; diarrhoea more common than cyclosporine |
| Cyclosporine | Moderate | GI effects; less diarrhoea than tacrolimus |
| Sirolimus | Moderate | Oral ulcers (30-60%), diarrhoea, stomatitis |
| Everolimus | Moderate | Lower oral ulcer rate than sirolimus |
| Belatacept | Low-Moderate | Mild nausea, diarrhoea |
| Rituximab | Low | Rare GI perforation |
| PPI prophylaxis (therapeutic) | Protective | Reduces steroid-related PU risk |
| Antiemetics (therapeutic) | Protective | Reduces cyclophosphamide-related nausea |

#### Guideline References

1. KDIGO 2021 Glomerular Diseases Guideline. *Kidney Int.* 2021;100(4S):S1-S276
2. KDIGO 2023 Transplant Guideline. *Transplantation.* 2023;107(6S):S1-S216
3. Budde K et al. GI Complications of Immunosuppression. *Nat Rev Nephrol.* 2022;18(2):93-105
4. Hardinger KL et al. MMF Tolerability and Management of GI Side Effects. *Am J Transplant.* 2021;21(8):2679-2692

---
### 2.24 Drug-Induced Interstitial Nephritis

**Complication ID:** COMP-DIIN-001

#### Risk Factors

- Exposure to drugs known to cause acute interstitial nephritis (AIN)
- Proton pump inhibitors (most common cause in modern practice — omeprazole, pantoprazole, lansoprazole)
- NSAIDs (all classes; COX-2 selective also implicated)
- Antibiotics (beta-lactams: penicillins, cephalosporins; rifampicin; vancomycin; ciprofloxacin)
- Diuretics (thiazides, furosemide, triamterene)
- Allopurinol
- Antivirals (acyclovir, tenofovir, indinavir — also cause crystalline nephropathy)
- Immune checkpoint inhibitors (pembrolizumab, nivolumab, ipilimumab — emerging cause in GN patients with malignancy)
- 5-ASA compounds (mesalamine, sulfasalazine)
- Herbal remedies and traditional Chinese medicines
- Older age (reduced renal reserve, polypharmacy)
- Pre-existing CKD (lower threshold for injury)
- Volume depletion (concentrates drug in renal tubules)
- Prior history of AIN (recurrence risk with re-exposure)
- HIV infection (increased risk with multiple drugs)
- Prolonged drug exposure (longer treatment duration increases risk)

#### Clinical Features

- **Classic triad (present in <10%):** Fever, rash, eosinophilia
- **Fever:** 50-70% (often first sign; may be low-grade)
- **Rash:** 30-50% (maculopapular, morbilliform; typically trunk and extremities)
- **Eosinophilia:** 50-70% (peripheral blood)
- **AKI:** Acute increase in serum creatinine (oliguric or non-oliguric)
- **Urine sediment:**
  - White blood cells (sterile pyuria)
  - White blood cell casts (eosinophil casts — highly suggestive)
  - Microscopic haematuria (50-70%)
  - Mild proteinuria (<1 g/day; can be nephrotic-range with NSAID-induced AIN)
- **Flank pain:** 20-30% (renal capsular distension)
- **Hypertension:** 30-50% (volume-dependent)
- **Renal biopsy (gold standard for diagnosis):**
  - Interstitial infiltrate (lymphocytes, plasma cells, eosinophils)
  - Tubulitis (lymphocytes invading tubular epithelium)
  - Granulomas (seen in drug-induced AIN, sarcoidosis, TB)
  - No/minimal glomerular involvement
  - Interstitial oedema in acute phase
- **Timing:** Variable by drug (5 days to 8 weeks after exposure); NSAID: months to years; PPI: typically 2-12 months (delayed); antibiotics: 1-3 weeks

#### Prevention

- **Minimise drug exposures:** Use shortest possible courses; avoid unnecessary PPIs
- **Deprescribing:** Regularly review PPI necessity (deprescribe if no clear indication — no GERD, no high-risk ulcer prophylaxis)
- **NSAID avoidance in CKD:** Strict contraindication in eGFR <30; caution in G3a-b
- **Alternative PPI strategies:** Consider H2RA (famotidine) if acid suppression needed (lower AIN risk)
- **Hydration:** Maintain adequate hydration during drug courses (especially antibiotics)
- **Avoid combination nephrotoxins (triple whammy: NSAID + diuretic + RAASi)**
- **Drug allergy documentation:** Document clearly; avoid re-exposure to same drug class
- **Slow reintroduction:** If AIN suspected but drug essential (e.g., rifampicin for TB), cautious rechallenge under close monitoring

#### Early Detection

- **Urinalysis:** Sterile pyuria + WBC casts + haematuria in patient with AKI (classic clue)
- **Urine eosinophils:** Wright or Hansel stain (moderate specificity — presence raises suspicion; absence does not exclude)
- **Renal biopsy:** If AIN suspected and drug withdrawal does not improve creatinine in 5-7 days
- **Fever + AKI + sterile pyuria** in a patient on PPI/NSAID/antibiotic = suspect AIN
- **Serum creatinine monitoring:** Baseline + after drug initiation (especially new antibiotics, PPIs)
- **Peripheral blood eosinophil count:** Mild-moderate eosinophilia
- **Gallium-67 scan:** Renal uptake can indicate inflammation (limited use; not routinely indicated)
- **Urine beta-2 microglobulin or alpha-1 microglobulin:** Elevated (tubular proteinuria)
- **Fractional excretion of sodium:** Variable (not diagnostic)

#### Treatment

- **Drug withdrawal (first line and most important):**
  - Identify and stop the offending drug immediately
  - Recovery may take days to weeks (mean 4-8 weeks)
  - Incomplete recovery is common (especially with NSAIDs, PPIs)
- **Corticosteroids (for severe or non-resolving AIN):**
  - Prednisolone 0.5-1 mg/kg/day (max 60 mg/day) for 2-4 weeks, then taper
  - Indicated if: dialysis required, creatinine not improving 5-7 days after drug withdrawal, biopsy-proven AIN with severe inflammation
  - Evidence from prospective RCTs is limited; use is based on observational data
  - IV methylprednisolone (500 mg x 3) for very severe (dialysis-dependent, extensive inflammation on biopsy)
  - Early steroid therapy (<10-14 days from drug cessation) associated with better recovery
- **Supportive care:**
  - Volume repletion (if prerenal component)
  - Diuretics for fluid overload
  - Electrolyte management
  - RRT if indicated (dialysis may be temporary)
- **Specific scenarios:**
  - NSAID-induced AIN with nephrotic syndrome: More steroid-responsive than NSAID AIN without nephrotic
  - PPI-induced AIN: Poorer recovery rate (only 30-40% complete recovery); steroid if severe and early
  - Checkpoint inhibitor AIN: High-dose steroids; may need to stop immunotherapy
- **Avoid re-challenge with the same drug class**

#### Monitoring

- Serum creatinine and eGFR daily during acute phase (until improvement or stabilization)
- Urinalysis (pyuria and WBC casts resolution)
- Blood eosinophil count (normalisation indicates resolution)
- Drug levels (if applicable)
- Renal biopsy for refractory cases (6-8 weeks without improvement)
- Kidney size on ultrasound (small kidneys suggest chronic damage)
- Long-term eGFR trajectory (assess for incomplete recovery -> CKD)
- Blood pressure (may improve or worsen)
- Fluid balance and weight
- Proteinuria quantification (if nephrotic-range from NSAID-AIN)

#### Long-Term Consequences

- **Incomplete renal recovery:** New baseline creatinine higher; 30-50% do not return to baseline
- **Chronic kidney disease:** Progression to CKD G3-5 after severe or prolonged AIN
- **Chronic interstitial fibrosis:** Irreversible, leads to progressive renal impairment
- **ESKD:** Rare but reported; especially with prolonged undiagnosed PPI-AIN
- **Steroid-related adverse effects** (if prolonged corticosteroid course used)
- **Drug restriction:** Allergy label prevents future use of entire drug class
- **Need for RRT** if severe AKI requiring dialysis
- **Recurrent AIN** (if alternative drug within same class used)
- **Dialysis dependence** (if irreversible damage, especially NSAID-induced papillary necrosis)

#### Associated Diseases

| Disease ID | Frequency | Special Considerations |
|---|---|---|
| `lupus` | Moderate | PPIs commonly prescribed with steroids; may also have `lupus` interstitial nephritis |
| `iga` | Moderate | PPIs, NSAIDs in young adults |
| `membranous` | Moderate | NSAID for oedema; PPI with steroids |
| `fsgs` | Moderate | NSAID avoidance essential (NSAIDs may have triggered FSGS) |
| `mcd` | Low | NSAID-induced `mcd` and AIN overlap |
| `diabeticNephropathy` | High | Polypharmacy; PPIs often prescribed; NSAIDs for pain |
| `anca | Low | AIN less common; disease active sediment differentiates |
| `cniToxicity` | Low | CNI toxicity is different pathology (vasoconstriction/vacuolisation, not AIN) |
| `hivan` | High | Multiple drugs; TDF, TMP-SMX, antiretroviral interactions |
| `drugInducedGn` | High | Some drugs cause both GN and AIN (NSAIDs, rifampicin) |
| `alport` | Low | NSAID use for pain (avoid) |
| `transplantGlomerulopathy` | Low-Moderate | PPIs and antibiotics common; CNI not associated with AIN |
| `cryoglobulinemic` | Low | NSAIDs for arthralgia |

#### Associated Drugs

| Drug | Risk Level | Mechanism |
|---|---|---|
| Proton pump inhibitors (all) | High | Hypersensitivity reaction (delayed > months); drug accumulates in tubular cells |
| NSAIDs (all classes) | High | Decreased prostaglandin synthesis; cell-mediated immunity; combined haemodynamic + AIN |
| Penicillins (methicillin, ampicillin, amoxicillin) | High | Hypersensitivity (immediate/delayed); beta-lactam ring |
| Cephalosporins | Moderate | Similar to penicillins; cross-reactivity |
| Rifampicin | High | Intermittent dosing increases risk |
| Vancomycin | Moderate | Red man syndrome + AIN with prolonged high troughs |
| Ciprofloxacin | Moderate | Hypersensitivity; more common in older patients |
| Diuretics (thiazides, furosemide, triamterene) | Moderate | Hypersensitivity; thiazides also photosensitivity |
| Allopurinol | Moderate | Hypersensitivity syndrome (DRESS) including AIN |
| Mesalamine/5-ASA | Moderate | Tubulointerstitial nephritis; chronic use |
| Immune checkpoint inhibitors (pembrolizumab, nivolumab) | Moderate-High | T-cell mediated; may be delayed; requires steroids |
| Acetaminophen (chronic high dose) | Low-Moderate | Analgesic nephropathy with chronic use |
| H2-receptor antagonists (famotidine, ranitidine) | Low | Much lower AIN risk than PPIs |

#### Guideline References

1. Raghavan R, Eknoyan G. Acute Interstitial Nephritis — A Reappraisal. *Kidney Int.* 2014;85(5):1023-1030
2. Moledina DG, Perazella MA. Drug-Induced Acute Interstitial Nephritis: Current Concepts. *Nephron.* 2023;147(6):328-338
3. Muriithi AK et al. Drug-Induced Acute Interstitial Nephritis. *Clin J Am Soc Nephrol.* 2014;9(10):1776-1784
4. Perazella MA. Drug-Induced Acute Kidney Injury: Diverse Mechanisms and Prevention. *Am J Kidney Dis.* 2022;79(4):591-604

---
---
## 3. Appendix A: Complication Prevention by Drug

| Drug | Key Complications | Prevention Strategy |
|---|---|---|
| **RAASi (ACEi/ARB)** | AKI (prerenal), hyperkalemia, hypotension | Start low, titrate slowly; hold during volume depletion; monitor Cr/K+ at 1-2 weeks; avoid NSAID co-prescription |
| **SGLT2i** | Euglycaemic DKA, genitourinary infections, volume depletion | Hold during intercurrent illness/surgery; educate about DKA symptoms; maintain perineal hygiene; eGFR >25 for initiation |
| **Prednisolone** | Infection (global), osteoporosis, hyperglycaemia, HTN, GI bleeding, avascular necrosis, NODAT, weight gain | PJP prophylaxis if >20 mg/day >4 weeks; DXA scan at baseline and annually; bisphosphonate if high risk; HbA1c monitoring; PPI if GI risk; steroid-sparing agents preferred |
| **Methylprednisolone (pulse)** | Infection (intense), PRES, hyperglycaemia, arrhythmia, avascular necrosis | Single pulsed doses with pre-medication; BP monitoring; glucose monitoring; cumulative pulse dose tracking |
| **Cyclophosphamide** | Infection (neutropenia), myelosuppression, hemorrhagic cystitis, infertility, malignancy (bladder, skin), GI toxicity | CBC monitoring weekly then monthly; Mesna co-administration; aggressive hydration; cumulative dose limit (7.5-10 g/m²); fertility preservation counselling; PJP prophylaxis |
| **MMF** | Infection, GI toxicity (diarrhoea), cytopenias, teratogenicity, PML (rare) | Start low, titrate; monitor CBC weekly x1 month then monthly; pregnancy test before initiation; contraception counselling; switch to EC-MPS if GI intolerance; PJP prophylaxis |
| **EC-MPS (Myfortic)** | GI toxicity (lower than MMF), cytopenias, infection | Similar to MMF but better GI tolerance; reduce dose if neutropenia |
| **Azathioprine** | Cytopenias, pancreatitis, GI intolerance, hepatotoxicity, malignancy (skin) | TPMT genotyping before start; start 50 mg, titrate slowly; monitor CBC monthly; avoid allopurinol (unless dose-reduced); annual skin check |
| **Tacrolimus** | HTN, nephrotoxicity (CNI), NODAT, neurotoxicity (tremor, PRES), infection, hyperkalemia | Trough level monitoring (5-10 ng/mL); BP monitoring; glucose monitoring; neuro exam; avoid NSAIDs; Mg supplementation |
| **Cyclosporine** | HTN, nephrotoxicity, hirsutism, gingival hyperplasia, hyperlipidemia, PRES | Trough level monitoring (100-200 ng/mL); BP and lipid monitoring; dental hygiene; gingivectomy if needed |
| **Rituximab** | Infusion reactions (cytokine release), infection (late-onset neutropenia, hypogammaglobulinemia), HBV reactivation, PML (rare) | Pre-medication (APAP, diphenhydramine, steroid); slow infusion rate; pre-screen HBV; monitor IgG levels; CBC at 6-12 months post-infusion; screen for JC virus if prolonged therapy |
| **Belimumab** | Infusion reactions, infection, psychiatric effects | Pre-medication; infection screening; monitor for depression/suicidal ideation |
| **Belatacept** | PTLD (especially EBV D+/R-), infection, anaemia | EBV serology screening before use; avoid in EBV D+/R-; monthly EBV PCR monitoring; lower CV risk profile than CNI |
| **Eculizumab** | Meningococcal infection, infusion reactions | Meningococcal vaccination (MenACWY + MenB) at least 2 weeks before first dose; consider antibiotic prophylaxis; monitor complement activity |
| **Sirolimus / Everolimus** | Oral ulcers, hyperlipidemia, thrombocytopenia, wound dehiscence, interstitial pneumonitis | Dexamethasone mouthwash for aphthous ulcers; lipid monitoring; hold pre- and post-surgery; monitor LFTs and spirometry if respiratory symptoms |
| **Bortezomib** | Thrombocytopenia, peripheral neuropathy, GI toxicity, infection (VZV reactivation) | Monitor CBC; SC route preferred (less PN); VZV prophylaxis (acyclovir); assess for neuropathy at each cycle |
| **ATG** | Infusion reactions (cytokine release), thrombocytopenia, profound lymphopenia, serum sickness | Pre-medication; central line (for infusion); daily CBC; infection prophylaxis (CMV, PJP); monitor for serum sickness |
| **Alemtuzumab** | Infusion reactions, profound lymphopenia, autoimmune cytopenias, infection (CMV, EBV, PML) | Pre-medication; antiviral prophylaxis (valganciclovir); PJP prophylaxis; monitor CBC and autoimmune markers |
| **IVIG** | Infusion reactions (headache, aseptic meningitis, thrombosis), AKI, haemolysis | Slow infusion rate; pre-hydration; avoid sucrose-containing products in CKD; monitor renal function, Hb, fluid status; IgA level testing before first dose |
| **Hydroxychloroquine** | Retinopathy (chronic use >5 years), QTc prolongation, myopathy | Ophthalmology screening at baseline and annually after 5 years; ECG if QTc risk; cumulative dose monitoring (<400 mg/day) |
| **Finerenone** | Hyperkalemia, hypotension | Monitor K+ at 1-2 weeks after initiation and dose changes; avoid strong CYP3A4 inhibitors; hold if eGFR <25 |
| **Statins** | Myopathy, hepatotoxicity, drug interactions (CNI levels) | Monitor CK if muscle symptoms; LFT monitoring; adjust dose for renal function; educate about drug interactions |
| **TMP-SMX (PJP prophylaxis)** | Hyperkalemia (TMP component), AKI, rash, GI intolerance, bone marrow suppression | Monitor K+, Cr; adjust dose for GFR; folate supplementation; avoid with high-dose MTX |
| **Valganciclovir** | Myelosuppression (neutropenia, thrombocytopenia), GI toxicity | Monitor CBC weekly; adjust dose for GFR; dose reduce if neutropenic |

---
## 4. Appendix B: Complication Quick Reference

### Urgent Complication: PRES

**Recognition:** Headache + seizures + visual disturbance + hypertension in patient on CNI

**Immediate Actions:**
1. Hold CNI (tacrolimus/cyclosporine)
2. Control BP: IV labetalol 20 mg or nicardipine 5 mg/h; target 25% reduction over 1-2h
3. MRI brain (FLAIR sequence) urgently
4. Levetiracetam for seizures
5. Avoid: Rapid BP correction, CNI restart until resolved
6. Switch immunosuppression if severe/recurrent (belatacept, mTOR inhibitor)

**Key Differentiator:** MRI distinguishes PRES from stroke, CNS infection, or lupus cerebritis

---

### Urgent Complication: Pneumocystis jirovecii Pneumonia

**Recognition:** Subacute dyspnoea, dry cough, hypoxia, bilateral interstitial infiltrates on CXR/CT; usually CD4 count <200

**Immediate Actions:**
1. Start high-dose TMP-SMX (15-20 mg/kg/day TMP component in divided doses)
2. Pulse oximetry; ABG; CT chest
3. Bronchoscopy with BAL for diagnosis (silver stain, immunofluorescence)
4. Corticosteroids (prednisolone 40-60 mg/day) if PaO2 <70 mmHg
5. Prophylaxis for all close contacts of immunosuppressed patients if indicated

**Risk:** Mortality 30-50% if not treated early; PJP prophylaxis is essential in at-risk patients

---

### Urgent Complication: Tumour Lysis Syndrome

**Context:** Following rituximab in high-burden lymphoma/PTLD; rare in GN

**Recognition:** AKI + hyperkalemia + hyperphosphatemia + hypocalcemia + hyperuricemia 24-72h post-rituximab

**Immediate Actions:**
1. Aggressive IV hydration (3 L/m²/day)
2. Rasburicase (0.2 mg/kg IV once) if uric acid >8 mg/dL; allopurinol as alternative
3. Treat hyperkalemia per protocol
4. Monitor: K+, Ca, PO4, uric acid, Cr Q6-8h
5. CKD patients at highest risk -> consider dose reduction, pre-hydration

---

### Urgent Complication: Anaphylaxis (Infusion Reaction)

**Recognition:** Sudden onset (minutes) of urticaria, angioedema, bronchospasm, hypotension, hypoxia during infusion

**Immediate Actions:**
1. STOP infusion immediately
2. IM epinephrine 0.3-0.5 mg (1:1000) anterolateral thigh — repeat Q5-15min PRN
3. High-flow O2, airway management, IV access
4. IV fluids (0.9% NaCl 500-1000 mL rapid bolus)
5. IV diphenhydramine 50 mg + IV methylprednisolone 125-250 mg
6. Nebulised albuterol for bronchospasm
7. ICU admission if severe
8. Do NOT restart that infusion; document allergy

**Key Differentiator:** Cytokine release (rituximab) is slower onset (30-120 min) with fever/rigors/hypotension — treat with infusion slow/stop + supportive care; anaphylaxis is rapid (seconds-minutes) with urticaria/angioedema — treat with epinephrine

---

### Urgent Complication: Tuberculosis Reactivation

**Recognition:** Persistent cough >3 weeks + fever + night sweats + weight loss in patient on anti-TNF, high-dose steroids, or cyclophosphamide

**Immediate Actions:**
1. Respiratory isolation (negative pressure room)
2. CXR (apical infiltrates, cavitation, pleural effusion)
3. Sputum: AFB smear + GeneXpert MTB/RIF + culture (x3)
4. Start empiric 4-drug regimen (HRZE) if high clinical suspicion
5. Adjust immunosuppression (caution: taper/increase based on risk balance)
6. Contact tracing

**Key Interaction:** Rifampicin reduces CNI levels by 50-80% — monitor troughs closely, increase CNI dose as needed

---

### Urgent Complication: Hepatitis B Reactivation

**Recognition:** Elevated ALT + rising HBV DNA + jaundice/fatigue in patient on rituximab, cyclophosphamide, or high-dose steroids

**Immediate Actions:**
1. Start entecavir 0.5 mg or tenofovir 300 mg immediately
2. Hold/reduce immunosuppression if safe
3. Monitor LFTs, INR, bilirubin daily
4. Assess for hepatic decompensation (ascites, encephalopathy)
5. Hepatology referral

---

### Urgent Complication: Hemorrhagic Cystitis

**Recognition:** Macroscopic haematuria, dysuria, suprapubic pain during/after cyclophosphamide therapy

**Immediate Actions:**
1. Aggressive IV hydration
2. Continue/start Mesna if applicable
3. Catheterisation for clot retention
4. Continuous bladder irrigation (saline)
5. Cystoscopy with clot evacuation if severe
6. Hold cyclophosphamide; consider alternative (rituximab)

---

### Urgent Complication: Severe Cytopenia (Febrile Neutropenia)

**Recognition:** ANC <500/mm³ + fever >=38.3°C in patient on MMF, cyclophosphamide, azathioprine, or rituximab

**Immediate Actions:**
1. STAT CBC, blood cultures x2, urine culture
2. CXR
3. Start empiric broad-spectrum antibiotics (piperacillin-tazobactam or cefepime)
4. Hold myelosuppressive agents
5. G-CSF (filgrastim 5 mcg/kg SC daily)
6. Monitor ANC daily; resume drug when ANC >1000
7. If persistent cytopenia: bone marrow biopsy to exclude PTLD, infection, drug toxicity

---

### Document Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-10 | Initial V4.2 release. 24 complication entities with full cross-references to diseases and drugs. Prevention appendices included. |

---



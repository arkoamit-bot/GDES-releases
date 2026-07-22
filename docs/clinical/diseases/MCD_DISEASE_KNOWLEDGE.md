# Minimal Change Disease (MCD) — Disease Knowledge Specification

**Document ID:** MCD-DK-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Disease Knowledge  

---

## 1. Document Purpose

This document defines the complete disease knowledge specification for Minimal Change Disease (MCD) across all 21 fields of the standardised disease record schema. It serves as the authoritative knowledge base for clinical decision support, pathway logic, guideline mapping, and case-based reasoning within the BGDDR v4.1 framework.

---

## 2. Disease Record — Full 21-Field Schema

### 2.1 Definition

Podocytopathy characterised by diffuse foot process effacement on electron microscopy, absence of immune deposits on immunofluorescence, and no glomerular scarring on light microscopy. MCD is the most common cause of nephrotic syndrome in children (~80%) and accounts for 10–15% of adult nephrotic syndrome cases. Historically termed *lipoid nephrosis* or *nil disease* due to the ostensibly normal appearance on light microscopy.

### 2.2 Epidemiology

- **Peak age:** 2–6 years (childhood); bimodal adult distribution (20–40 years, then elderly)
- **Sex ratio:** M:F 2:1 in children; equal distribution in adults
- **Incidence:** 2–3 per 100,000 children annually
- **Genetic associations:** HLA-DRB1*07, HLA-DQB1*02
- **Seasonal pattern:** Linked to infections; often presents following upper respiratory tract infections or immunisations

### 2.3 Aetiology

| Category | Examples |
|---|---|
| **Primary (idiopathic)** | T-cell dysregulation mediated; circulating permeability factor |
| **Drug-induced** | NSAIDs, lithium, interferon-alpha, pamidronate, gold, penicillamine |
| **Infection-associated** | HIV, EBV, TB, H. pylori, syphilis, mycoplasma |
| **Malignancy-associated** | Hodgkin lymphoma (classic association), thymoma, other lymphoproliferative disorders |
| **Atopy/allergy** | Allergic rhinitis, asthma, eczema, food allergy |
| **Autoimmune** | Systemic lupus erythematosus, autoimmune thyroiditis |

### 2.4 Pathophysiology

The central paradigm is T-cell dysregulation leading to secretion of circulating permeability factors (IL-13, IL-8, TNF-alpha) that disrupt podocyte actin cytoskeleton. IL-13 upregulates CD80 on podocytes, impairing slit diaphragm integrity. The resulting foot process effacement causes massive proteinuria. B-cells are also implicated, evidenced by therapeutic response to rituximab. The slit diaphragm proteins nephrin and podocin show altered distribution. CD80 (B7-1) is shed into urine and serves as a potential biomarker.

### 2.5 Clinical Presentation

- Acute-onset nephrotic syndrome: periorbital and peripheral oedema, anasarca, ascites, pleural effusions
- Preserved glomerular filtration rate initially
- Hypertension uncommon (distinguishes from other glomerulonephritides)
- Microscopic haematuria in 20–30%
- Acute kidney injury in 5–10% (more common in elderly, often due to ischaemic acute tubular necrosis)
- Hyperlipidemia (elevated cholesterol, triglycerides, LDL)
- Low serum albumin (<2.5 g/dL)
- Massive proteinuria (>3.5 g/day adults, >40 mg/m2/h children)

### 2.6 Diagnostic Criteria

Six criteria must be satisfied:

1. Light microscopy: normal or minimal mesangial hypercellularity
2. Immunofluorescence: negative for IgG, IgA, IgM, C3, C1q (full-house negative)
3. Electron microscopy: diffuse foot process effacement; no electron-dense deposits
4. Clinical: acute-onset nephrotic syndrome
5. Treatment response: steroid-sensitive (diagnostic trial of corticosteroids)
6. Exclusion: no evidence of secondary cause

### 2.7 Differential Diagnosis

| Condition | Key Distinguishing Features |
|---|---|
| FSGS | Segmental sclerosis on biopsy, steroid-resistant, persistent proteinuria |
| Membranous nephropathy | Subepithelial deposits, PLA2R antibody positive, adult predominance |
| Lupus nephritis Class V | Full-house immunofluorescence, serologic evidence of SLE |
| IgM nephropathy | Mesangial IgM deposits, variable steroid response |
| C1q nephropathy | Mesangial C1q deposits, often steroid-resistant |
| Alport syndrome | Family history, sensorineural hearing loss, thin basement membrane |

### 2.8 Laboratory Findings

1. Proteinuria: UPCR >3.5 g/g adults, >2.0 g/g children; 24h urine >3.5 g adults
2. Serum albumin: <2.5 g/dL (nephrotic range)
3. Serum creatinine/eGFR: typically normal; may be elevated in AKI
4. Lipids: elevated total cholesterol, LDL, triglycerides
5. Complement levels: normal (C3, C4) — critical to distinguish from lupus or post-infectious GN
6. ANA: negative
7. Infection serology: HBV, HCV, HIV negative
8. SPEP/UPEP: no monoclonal protein (exclude amyloidosis, myeloma)
9. Urine sediment: fatty casts, oval fat bodies, Maltese crosses under polarised light
10. CD80 urinary levels: elevated (research marker)

### 2.9 Biopsy Findings

| Modality | Findings |
|---|---|
| **Light microscopy** | Normal glomeruli or minimal mesangial hypercellularity; patent capillaries; no sclerosis, crescents, or necrosis |
| **Immunofluorescence** | Negative for IgG, IgA, IgM, C3, C1q, kappa/lambda (must be negative to confirm diagnosis) |
| **Electron microscopy** | Diffuse foot process effacement (>80% of capillary surface area); no electron-dense deposits; microvillus transformation; podocyte hypertrophy; normal basement membrane thickness |

### 2.10 Classification Systems

| System | Categories |
|---|---|
| **Steroid response** | Steroid-Sensitive (SSNS) / Steroid-Dependent (SD) / Steroid-Resistant (SRNS) / Frequently Relapsing (FR) |
| **Aetiological** | Primary (idiopathic) / Secondary |
| **Relapse frequency** | Single relapse / Frequent relapse (2+ in 6 months or 4+ in 12 months) / Infrequent relapse |
| **Age group** | Childhood-onset / Adult-onset |

### 2.11 Risk Stratification

| Factor | Risk Implication |
|---|---|
| Steroid response | Most critical prognostic factor |
| Relapse frequency | FR/SD require steroid-sparing therapy |
| Adult onset | Worse outcomes; higher risk of AKI and steroid-resistance |
| AKI at presentation | Increased morbidity, may require dialysis support |
| Secondary cause | Malignancy-associated carries worst prognosis |
| Hypertension | Adverse renal outcome |
| Second-line agent response | Guides long-term immunosuppression strategy |

### 2.12 Treatment Overview

- **First-line:** Corticosteroids — prednisone 1 mg/kg/day (max 60–80 mg) adults, 60 mg/m2/day children, for 4–16 weeks
- **Remission rates:** 85–95% children, 75–85% adults
- **Steroid-sparing agents for FR/SD:**
  - Cyclophosphamide: 2–2.5 mg/kg/day for 8–12 weeks
  - CNI: cyclosporine 3–5 mg/kg/day, tacrolimus 0.05–0.1 mg/kg/day
  - MMF: 1.5–2 g/day adults; 600–1200 mg/m2 children
  - Rituximab: 375 mg/m2 weekly x 1–4 doses (FR/SD)
  - Levamisole: 2.5 mg/kg alternate days (children)
- **Supportive:** RAAS inhibition, diuretics, statins, low-sodium diet

### 2.13 Treatment Algorithms

Seven-step algorithm:

1. Steroid trial (prednisone 1 mg/kg/day or 60 mg/m2/day)
2. Assess at 4–8 weeks for complete remission
3. If remission: gradual taper over 3–6 months
4. If FR/SD: add MMF, CNI, or rituximab
5. If steroid-resistant: re-biopsy to exclude FSGS
6. Tailor immunosuppression based on response and toxicity
7. Long-term management with monitoring for complications

### 2.14 Monitoring Protocol

| Drug | Monitoring Requirements |
|---|---|
| **Corticosteroids** | BP, glucose, bone density (DEXA), growth (children), ophthalmology (cataracts), infection surveillance |
| **CNI** | Trough levels, serum Cr, BP, potassium, magnesium |
| **Cyclophosphamide** | CBC with differential and LFT weekly; cumulative dose tracking |
| **MMF** | CBC monitoring, pregnancy prevention |
| **Rituximab** | CD19/20 counts, infusion reaction monitoring, HBV reactivation screening |

- Daily urine dipstick during induction
- Twice-weekly dipstick during steroid taper
- Weekly surveillance for relapse in first 6 months, then monthly
- Vaccination: maintain live-vaccine-free during immunosuppression; administer pneumococcal, influenza, varicella before therapy

### 2.15 Complications

1. **Steroid toxicity:** Diabetes, osteoporosis, cataracts, growth retardation (children), avascular necrosis, psychosis
2. **Infection:** Bacterial peritonitis (Streptococcus pneumoniae), cellulitis, pneumonia; highest risk in active nephrotic state
3. **Acute kidney injury:** 5–10%; higher in adults; often due to ATN or interstitial nephritis
4. **Venous thromboembolism:** Deep vein thrombosis, renal vein thrombosis, pulmonary embolism (due to loss of antithrombin III)
5. **Hyperlipidemia:** Accelerated atherosclerosis risk with prolonged nephrosis
6. **Relapse:** 60–70% children, 40–50% adults
7. **CNI toxicity:** Nephrotoxicity, hypertension, tremor, hirsutism, gum hyperplasia
8. **Cyclophosphamide toxicity:** Haemorrhagic cystitis, gonadal failure, malignancy risk (cumulative)
9. **Rituximab infusion reactions:** Serum sickness, PML (rare), hypogammaglobulinemia

### 2.16 Relapse Information

- Relapse rate: 60–70% children, 40–50% adults
- Frequently relapsing: 20–30% children
- Steroid-dependent: 15–20% children
- Risk factors: young age at onset, short time to remission (<4 weeks), low steroid dose during taper, high initial proteinuria
- Management: restart steroids at remission-inducing dose, add steroid-sparing agent
- Rituximab is highly effective for steroid-dependent disease
- Relapse rate decreases with age

### 2.17 Long-Term Prognosis

- Renal survival: >90% at 10 years for steroid-sensitive patients
- Mortality: <2%; primarily from infection or treatment complications
- Progression to ESKD: exceptional in steroid-sensitive disease
- Steroid-resistant cases: ~20% transition to FSGS on repeat biopsy
- Morbidity: primarily from steroid toxicity (bone density reduction, growth retardation, cataracts)
- Pregnancy: good outcomes; may relapse during pregnancy or postpartum

### 2.18 Evidence Summary

| Domain | Key Evidence |
|---|---|
| Steroid efficacy | KDIGO 2021 Ch 5; RCTs of prednisone in children (ISKDC) |
| MMF vs cyclosporine | Comparable efficacy for FR/SD; MMF better tolerability |
| Rituximab | RITURNS (Lancet 2014), RITUXIMAB-NS trials; 85% remission in SD |
| Cyclophosphamide vs MMF | IMPORT trial for SD management |
| Paediatric guidelines | IPNA 2023 clinical practice recommendations |
| Regulatory | No FDA-approved therapy specifically for MCD; all agents off-label |

### 2.19 Guideline Recommendations

| Guideline | Year | Focus |
|---|---|---|
| KDIGO 2021 | 2021 | Chapter 5: SSNS comprehensive management |
| KDIGO 2025 | 2025 | Emerging therapies and updated algorithms |
| ISN 2023 | 2023 | Global nephrology consensus |
| ASN 2022 | 2022 | Adult nephrotic syndrome management |
| IPNA 2023 | 2023 | Paediatric MCD algorithm and steroid-sparing guidance |

### 2.20 Key References

1. KDIGO 2021 Clinical Practice Guideline for Glomerular Diseases, Chapter 5
2. Iijima K, et al. Rituximab for childhood-onset refractory nephrotic syndrome. Lancet 2014
3. Vivarelli M, et al. IPNA clinical practice recommendations for SRNS. Pediatr Nephrol 2023
4. RITURNS Study Group. Rituximab in frequently relapsing nephrotic syndrome
5. Gipson DS, et al. Management of childhood onset nephrotic syndrome. Pediatrics 2009
6. Hogan J, Radhakrishnan J. The treatment of minimal change disease in adults. JASN 2013
7. Maas RJ, et al. Minimal change disease and focal segmental glomerulosclerosis. Nat Rev Nephrol 2021
8. Beck L, et al. Rituximab in adult minimal change disease. KI Reports 2020
9. Sinha A, Bagga A. Rituximab in nephrotic syndrome. Pediatr Nephrol 2019
10. Nishi S, et al. Evidence-based clinical practice guidelines for nephrotic syndrome 2020. CEN Case Reports

### 2.21 Notes

V4.1 engineering notes: This knowledge specification integrates with 28 active KB rules, 6 clinical pathways (Diagnosis & Classification, Initial Steroid Therapy, Response Assessment & Taper, FR/SD Management, Steroid-Resistant/Refractory, Long-Term Monitoring & Transition), and 8 validated clinical cases. Parity between paediatric and adult canonical models is maintained through the steroid-response classification overlap. All evidence is traceable to KDIGO 2021 and IPNA 2023 as primary anchor guidelines.

---

## 3. Domain Audit Summary

| Domain Element | Status | Completeness |
|---|---|---|
| 21-field schema | Complete | 21/21 fields |
| Evidence base (RCT, meta-analysis) | Complete | 5 trial categories |
| Steroid response classification | Complete | SSNS/SD/FR/SRNS |
| Secondary causes | Complete | 6 categories |
| Children vs adults differentiation | Complete | Age-specific epidemiology, treatment, outcomes |

---

## 4. Evidence Base

### 4.1 Key Randomised Trials

- **Prednisone vs placebo (ISKDC):** 85–95% remission in children with 4–8 week course
- **MMF vs cyclosporine (FR/SD):** MMF non-inferior with better tolerability; lower relapse at 12 months
- **Rituximab vs placebo (RITURNS):** 85% maintained remission at 12 months vs 10% placebo
- **Cyclophosphamide vs MMF (IMPORT):** Equally effective for SD but MMF better safety profile
- **Levamisole:** 2.5 mg/kg alternate days reduces relapse risk in children (OR 0.19)

### 4.2 Ongoing Knowledge Gaps

- Optimal duration of initial steroid therapy in adults
- Role of novel biomarkers (CD80, suPAR, IL-13) in predicting relapse
- Best sequence of steroid-sparing agents
- Rituximab dosing and retiming protocols

---

## 5. Children vs Adults Differentiation

| Feature | Children | Adults |
|---|---|---|
| Peak age | 2–6 years | 20–40 years |
| Sex ratio | M:F 2:1 | Equal |
| Incidence | 2–3/100,000 | 0.2–1/100,000 |
| Steroid sensitivity | 85–95% | 75–85% |
| Relapse rate | 60–70% | 40–50% |
| AKI at presentation | Rare (<5%) | 5–10% |
| Steroid toxicity risk | Growth retardation | Diabetes, osteoporosis |
| Secondary causes | Less common | More common (drugs, malignancy) |
| Re-biopsy threshold | Steroid-resistant only | Steroid-resistant or atypical course |

---

## 6. Steroid Response Classification

```
                    MCD Diagnosis
                          |
                          v
                Steroid Trial (4-8 wks)
                          |
            +-------------+-------------+
            |                           |
      Remission                   No Remission
            |                           |
            v                           v
    Steroid-Sensitive            Steroid-Resistant
            |                           |
     +------+------+             Re-biopsy for FSGS
     |             |
  Infrequent    Frequent
   Relapse       Relapse
                   |
              +----+----+
              |         |
            Steroid-   Non-Dependent
            Dependent
```

---

## 7. Secondary Causes — Diagnostic Checklist

- [ ] Drug history: NSAIDs, lithium, interferon, pamidronate, gold, penicillamine
- [ ] Infection: HIV, HBV, HCV, EBV, TB, H. pylori, syphilis
- [ ] Malignancy: lymphoma (especially Hodgkin), thymoma
- [ ] Atopy: allergic rhinitis, asthma, eczema
- [ ] Autoimmune: SLE, thyroiditis
- [ ] Recent vaccination or allergen exposure

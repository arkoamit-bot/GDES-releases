# Drug Knowledge Library — Membranous Nephropathy Medications

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `treatments.models.DrugMaster`
**Coverage:** 22 drugs with expanded knowledge (7 MN-specific, 15 shared with IgA library)

---

## 1. Complete Drug Inventory

The following drugs have fully expanded knowledge fields (mechanism, side effects, monitoring, stopping criteria, dosage, evidence) relevant to Membranous Nephropathy management:

### MN Immunosuppressive Therapy Drugs

| Generic Name | Class | Drug Class Code | MN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Rituximab | Anti-CD20 Monoclonal Antibody | `rituximab` | First-line immunosuppression for moderate/high-risk primary MN | 1 |
| Cyclophosphamide | Alkylating Agent | `cyclophosphamide` | Severe/rapidly progressive MN (modified Ponticelli regimen) | 1 |
| Cyclosporine | Calcineurin Inhibitor | `cni` | Alternative first-line; second-line after rituximab | 1 |
| Tacrolimus | Calcineurin Inhibitor | `cni` | Alternative first-line; STARMEN protocol backbone | 1 |
| Prednisolone | Corticosteroid (oral) | `steroid` | Used with CyP in modified Ponticelli regimen | 1 |
| Methylprednisolone | Corticosteroid (IV) | `steroid` | Pulse therapy in Ponticelli regimen | 1 |
| Mycophenolate Mofetil | IMPDH Inhibitor | `mmf` | Second-line/third-line; steroid-sparing (limited evidence in MN) | 2 |

### MN Supportive Therapy Drugs (Shared with IgA Library)

| Generic Name | Class | Drug Class Code | MN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Ramipril | ACE Inhibitor (RAASi) | `raasi` | First-line antiproteinuric in all MN patients | 1 |
| Lisinopril | ACE Inhibitor (RAASi) | `raasi` | Alternative first-line RAASi | 1 |
| Losartan | ARB (RAASi) | `raasi` | First-line when ACEi not tolerated | 1 |
| Valsartan | ARB (RAASi) | `raasi` | First-line when ACEi not tolerated | 1 |
| Empagliflozin | SGLT2 Inhibitor | `sglt2i` | Renoprotection in MN with CKD | 1 |
| Atorvastatin | HMG-CoA Reductase Inhibitor | `statin` | Cardiovascular risk reduction of nephrotic dyslipidemia | 1 |
| Spironolactone | Mineralocorticoid Antagonist | `other` | Adjunctive antiproteinuric; resistant edema | 2 |

### MN VTE Prophylaxis and Complication Management

| Generic Name | Class | Drug Class Code | MN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Warfarin | Vitamin K Antagonist | `anticoagulant` | VTE prophylaxis if albumin <2.5 g/dL; treatment of established VTE | 1 |
| Enoxaparin | Low Molecular Weight Heparin | `anticoagulant` | Acute VTE treatment; bridging therapy | 1 |
| Apixaban | Direct Factor Xa Inhibitor | `doac` | VTE prophylaxis/treatment (limited MN-specific data) | 2 |
| Furosemide | Loop Diuretic | `diuretic` | Edema management in nephrotic syndrome | 1 |

---

## 2. Per-Drug Summary — MN-Specific Focus

### Rituximab

- **Class:** Anti-CD20 Monoclonal Antibody
- **Mechanism:** Chimeric murine/human IgG1 antibody targeting CD20 antigen on B-cells, causing B-cell depletion via ADCC, CDC, and apoptosis
- **Evidence Level:** 1 (Strong recommendation — first-line)
- **MN Indication:** Moderate-to-high risk primary membranous nephropathy; first-line immunosuppression
- **Dosage Regimens:**
  - Regimen A: 1g IV x2 doses, 2 weeks apart (MENTOR protocol)
  - Regimen B: 375mg/m2 IV weekly x4 (GEMRITUX protocol)
  - Repeat dosing based on CD19/CD20 reconstitution and PLA2R titer rebound
- **Key Trials:** MENTOR (2019): rituximab 60% remission vs cyclosporine 20% at 12 months; GEMRITUX (2017): HR 0.52 for remission vs supportive care
- **Monitoring:** CD19/20 counts, anti-PLA2R titers, LFTs, CBC at baseline and q1-2 months
- **Common SE:** Infusion reactions (fever, chills, hypotension, 30-40% with first dose), headache, nausea
- **Serious SE:** Severe infusion reactions (<1%), hepatitis B reactivation (screen all patients), PML (<1:10,000), late-onset neutropenia (5-10%)
- **Stopping Criteria:** Severe infusion reaction, confirmed PML, severe infection, lack of B-cell depletion (consider anti-drug antibodies)
- **Pregnancy Category:** C (avoid; crosses placenta, neonatal B-cell depletion)
- **Drug Interactions:** Caution with other immunosuppressants (increased infection risk)

### Cyclophosphamide

- **Class:** Alkylating Agent
- **Mechanism:** Cross-links DNA leading to inhibition of DNA synthesis and cell death; suppresses both B and T cell proliferation
- **Evidence Level:** 1
- **MN Indication:** Severe/rapidly progressive primary MN; modified Ponticelli regimen (CyP 2.5mg/kg/day alternating with prednisolone 0.5mg/kg/day, each for 30 days, 3 cycles over 6 months)
- **Dosage:** 2.5mg/kg/day orally (modified Ponticelli); 500mg IV q2 weeks x6 pulses (alternative)
- **Cumulative Dose Limit:** 36g lifetime (increased malignancy risk beyond this)
- **Monitoring:** CBC weekly during treatment, urinalysis for hemorrhagic cystitis, LFTs, serum electrolytes
- **Common SE:** Nausea/vomiting, alopecia, amenorrhea/azoospermia, bone marrow suppression
- **Serious SE:** Hemorrhagic cystitis, bladder cancer (5-10x risk), myelodysplasia/leukemia, gonadal toxicity (30-50% permanent infertility), opportunistic infections
- **Stopping Criteria:** Neutrophils <1500, platelets <100,000, hemorrhagic cystitis, cumulative dose reached
- **Pregnancy Category:** D (teratogenic; contraindicated)

### Cyclosporine

- **Class:** Calcineurin Inhibitor
- **Mechanism:** Forms complex with cyclophilin, inhibiting calcineurin and T-cell activation; also stabilizes podocyte cytoskeleton
- **Evidence Level:** 1
- **MN Indication:** Alternative first-line immunosuppression; second-line after rituximab
- **Dosage:** 3.5-5.0 mg/kg/day in 2 divided doses; target trough 125-225 ng/mL
- **Duration:** Typically 12 months with gradual taper
- **Monitoring:** Trough levels (q1-2 weeks initially, then monthly), eGFR, BP, serum potassium, magnesium
- **Common SE:** Tremor, hirsutism, gingival hyperplasia, hypertension, hyperkalemia
- **Serious SE:** Nephrotoxicity (acute and chronic), posterior reversible encephalopathy syndrome (PRES), thrombotic microangiopathy, opportunistic infections
- **Stopping Criteria:** eGFR decline >30% from baseline (non-responsive to dose reduction), uncontrolled hypertension, neurotoxicity
- **Relapse Risk:** >50% relapse within 6 months of CNI withdrawal (vs 25-40% at 5yr for rituximab)
- **Pregnancy Category:** C

### Tacrolimus

- **Class:** Calcineurin Inhibitor
- **Mechanism:** Forms complex with FKBP12, inhibiting calcineurin and T-cell activation
- **Evidence Level:** 1
- **MN Indication:** Alternative first-line; STARMEN protocol backbone (tacrolimus + rituximab)
- **Dosage:** 0.05-0.1 mg/kg/day in 2 divided doses; target trough 5-10 ng/mL
- **Duration:** 6-12 months with gradual taper
- **Key Trial:** STARMEN (2021): tacrolimus + rituximab non-inferior to modified Ponticelli with better safety profile
- **Monitoring:** Trough levels, eGFR, BP, blood glucose, potassium, magnesium
- **Common SE:** Tremor, headache, diarrhea, hypertension, hyperglycemia, hyperkalemia
- **Serious SE:** Nephrotoxicity, new-onset diabetes after transplant (NODAT), PRES, neurotoxicity
- **Pregnancy Category:** C
- **Note:** Less hirsutism and gingival hyperplasia than cyclosporine; preferred CNI in many centers

### Prednisolone

- **Class:** Corticosteroid (oral)
- **Mechanism:** Glucocorticoid receptor agonist with broad anti-inflammatory and immunosuppressive effects
- **Evidence Level:** 1 (within Ponticelli regimen)
- **MN Indication:** Used in combination with cyclophosphamide (modified Ponticelli regimen)
- **Dosage (Ponticelli):** 0.5 mg/kg/kg alternate months (30 days on, 30 days off) for 3 cycles over 6 months
- **Dosage (alternative):** 0.5-1 mg/kg/day starting, tapering over 6 months
- **Monitoring:** Blood glucose, BP, bone density, ophthalmologic exam in prolonged use

### Empagliflozin

- **Class:** SGLT2 Inhibitor
- **Mechanism:** Selective SGLT2 inhibition reducing glucose and sodium reabsorption in proximal tubule, reducing intraglomerular pressure
- **Evidence Level:** 1
- **MN Indication:** Renoprotection in MN patients with eGFR >25; supported by EMPA-KIDNEY
- **Dosage:** 10mg once daily
- **Monitoring:** eGFR before and after initiation, volume status, ketones if sick

### Warfarin

- **Class:** Vitamin K Antagonist
- **Mechanism:** Inhibits vitamin K-dependent clotting factors (II, VII, IX, X)
- **Evidence Level:** 1 (for VTE in nephrotic syndrome)
- **MN Indication:** VTE prophylaxis if serum albumin <2.5 g/dL with additional risk factors; treatment of established VTE
- **Dosage:** Individualized; target INR 2-3
- **Monitoring:** INR weekly during initiation, then monthly
- **Duration of Therapy:** Minimum 3-6 months for first VTE; indefinite if recurrent or persistent nephrotic syndrome
- **Interaction:** Nephrotic syndrome alters protein binding; may require higher doses

---

## 3. Coverage Matrix

### Field Coverage per Drug

| Drug | MoA | Common SE | Serious SE | Monitoring | Stopping | Dosage | Max Dose | Evidence | Guidelines | Transplant |
|------|-----|-----------|------------|------------|----------|--------|---------|----------|------------|------------|
| Rituximab | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclophosphamide | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclosporine | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Tacrolimus | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Prednisolone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Methylprednisolone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Mycophenolate Mofetil | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Ramipril | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Lisinopril | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Losartan | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Valsartan | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Empagliflozin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Atorvastatin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Spironolactone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Warfarin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Enoxaparin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Apixaban | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Furosemide | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |

**Coverage: 11 of 11 knowledge fields populated for all 18 expanded drugs (100%)**

---

## 4. Drug Safety Information

### Pregnancy Categories

| Drug | Category | Recommendation |
|------|----------|---------------|
| Rituximab | C | Avoid in pregnancy; crosses placenta, neonatal B-cell depletion |
| Cyclophosphamide | D | Teratogenic; contraindicated in pregnancy |
| Cyclosporine | C | Use if benefit outweighs risk; dose adjustment needed |
| Tacrolimus | C | Use if benefit outweighs risk |
| Prednisolone | B | Preferred steroid in pregnancy |
| Mycophenolate Mofetil | D | Teratogenic; switch to AZA before conception (if AZA indicated) |
| Ramipril | D | Contraindicated in 2nd/3rd trimester |
| Empagliflozin | X | Contraindicated |
| Warfarin | X | Contraindicated in pregnancy; switch to LMWH |

### Key Monitoring Parameters

| Parameter | Drug(s) | Frequency |
|-----------|---------|-----------|
| CD19/20 counts | Rituximab | Pre-dose, optional during follow-up |
| Anti-PLA2R titers | Rituximab, CNI, CyP | Baseline, q1-2 months during induction |
| CBC, LFTs | Cyclophosphamide, MMF | Weekly during CyP; monthly otherwise |
| Trough levels | Tacrolimus (5-10 ng/mL), Cyclosporine (125-225 ng/mL) | q1-2 weeks initially, then monthly |
| eGFR, BP, K+ | RAASi, CNI | 1-2 weeks post-initiation/dose change |
| INR | Warfarin | Weekly during initiation, then monthly |
| Blood glucose | Prednisolone | Weekly during high-dose therapy |

---

## 5. Rituximab-First Strategy Framework

The KB rule base and clinical pathways implement the KDIGO 2021/Toronto Consensus rituximab-first approach:

| Risk Category | Recommended Therapy | Alternative | Evidence Basis |
|---------------|--------------------|-------------|----------------|
| Low risk | Supportive therapy alone (RAASi + SGLT2i) | Observation | GEMRITUX supportive arm |
| Moderate risk | Rituximab 1g x2 or 375mg/m2 x4 | Cyclosporine/Tacrolimus | MENTOR, GEMRITUX |
| High risk | Rituximab-based regimen | Modified Ponticelli (CyP+steroid) | MENTOR, STARMEN |
| Resistant | Switch class (rituximab -> CNI or CNI -> rituximab) | MMF; clinical trials | Expert opinion |

---

## 6. Planned Expansions

### V4.2 Target Drugs

| Priority | Drug | Class | Current Status |
|----------|------|-------|----------------|
| 1 | Adrenocorticotropic Hormone (ACTH) | Melanocortin agonist | Emerging MN therapy; limited evidence |
| 2 | Ofatumumab | Anti-CD20 (fully human) | Rituximab alternative; knowledge needed |
| 3 | Belimumab | Anti-BAFF | Combination therapy potential |
| 4 | Narsoplimab | MASP-2 inhibitor | Complement-targeted |
| 5 | Iptacopan | Factor B inhibitor | Complement-targeted |
| 6 | Sodium bicarbonate | Alkalinizing agent | CKD metabolic acidosis |
| 7 | Erythropoietin | ESA | CKD anemia |
| 8 | Calcifediol | Vitamin D analog | CKD-MBD management |

### Expansion Strategy

Target coverage: 50% of MN-relevant formulary by V4.2, with focus on emerging immunosuppressive agents and complement inhibitors.

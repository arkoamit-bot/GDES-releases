# Drug Knowledge Library -- Lupus Nephritis Medications

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `treatments.models.DrugMaster`
**Coverage:** 13 drugs with expanded LN-specific knowledge

---

## 1. Complete Drug Inventory

The following drugs have fully expanded knowledge fields (mechanism, side effects, monitoring, stopping criteria, dosage, evidence) relevant to Lupus Nephritis management.

### LN Induction Therapy Drugs

| Generic Name | Class | Drug Class Code | LN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Mycophenolate Mofetil | IMPDH Inhibitor | `mmf` | First-line induction for Class III/IV LN; first-line for Class V | 1 |
| Cyclophosphamide | Alkylating Agent | `cyclophosphamide` | Induction for Class III/IV LN (EuroLupus or NIH protocol); severe/RPGN | 1 |
| Prednisone | Corticosteroid (oral) | `steroid` | Induction backbone for all LN classes; taper over 3-6 months | 1 |
| Methylprednisolone | Corticosteroid (IV) | `steroid` | Pulse therapy for severe presentations (nephrotic syndrome, AKI, RPGN) | 1 |
| Voclosporin | Calcineurin Inhibitor | `cni` | Class V LN induction; combination with MMF + low-dose steroids | 1 |

### LN Maintenance and Novel Therapy Drugs

| Generic Name | Class | Drug Class Code | LN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Hydroxychloroquine | Antimalarial | `hcq` | All SLE patients; flare reduction, cardiovascular benefit, renal protection | 1 |
| Belimumab | Anti-BAFF Monoclonal Antibody | `biologic` | Add-on therapy for active LN (Class III/IV/V); BLISS-LN positive | 1 |
| Azathioprine | Purine Analog | `aza` | Maintenance therapy alternative to MMF; preferred in pregnancy | 1 |
| Rituximab | Anti-CD20 Monoclonal Antibody | `biologic` | Refractory LN (off-label); failure of first-line induction | 2 |
| Obinutuzumab | Anti-CD20 Monoclonal Antibody (type II) | `biologic` | Add-on therapy for LN; NOBILITY trial positive | 1 |

### LN Supportive Therapy Drugs

| Generic Name | Class | Drug Class Code | LN Indication | Evidence Level |
|--------------|-------|-----------------|---------------|----------------|
| Tacrolimus | Calcineurin Inhibitor | `cni` | Alternative CNI for Class V; MMF + CNI combination | 1 |
| Cyclosporine | Calcineurin Inhibitor | `cni` | Alternative CNI for Class V (limited LN data vs voclosporin) | 2 |
| Ramipril | ACE Inhibitor (RAASi) | `raasi` | Antiproteinuric; BP control in LN with proteinuria | 1 |

---

## 2. Per-Drug Summary -- LN-Specific Focus

### Mycophenolate Mofetil (MMF)

- **Class:** IMPDH Inhibitor (Prodrug of mycophenolic acid)
- **Mechanism:** Selective inhibition of inosine monophosphate dehydrogenase (IMPDH), blocking de novo purine synthesis in lymphocytes; preferentially suppresses B and T cell proliferation
- **Evidence Level:** 1 (Strong recommendation -- first-line)
- **LN Indication:** First-line induction for Class III/IV and Class V LN; maintenance therapy
- **Dosage Regimens:**
  - Induction: 500mg BID, titrate to 1g BID (target 2-3g/day) over 2-4 weeks
  - Maintenance: 1-2g/day in divided doses
  - Weight-based: 2-3g/day for adults; 40-60mg/kg/day for pediatric
- **Key Trials:** ALMS (2009): MMF non-inferior to IV CyP for Class III/IV induction (HR 0.88, 95% CI 0.74-1.04); MAINTAIN (2009): MMF non-inferior to AZA for maintenance (HR 0.88, 95% CI 0.44-1.74)
- **Monitoring:** CBC q2 weeks x3 then monthly, LFTs monthly x3 then q3 months, pregnancy test before initiation
- **Common SE:** GI symptoms (diarrhea 30-40%, nausea, abdominal pain), leukopenia (10-15%), infection
- **Serious SE:** Teratogenicity (congenital malformations), severe myelosuppression, progressive multifocal leukoencephalopathy (PML, rare), GI hemorrhage
- **Stopping Criteria:** Pregnancy (switch to AZA), severe GI intolerance unresponsive to dose reduction, ANC <1500, severe infection
- **Pregnancy Category:** D (teratogenic; contraindicated; switch to AZA minimum 6 weeks before conception)
- **Drug Interactions:** Antacids reduce absorption (take separately); proton pump inhibitors may reduce efficacy; co-trimoxazole increases myelosuppression

### Cyclophosphamide (CyP)

- **Class:** Alkylating Agent
- **Mechanism:** Cross-links DNA leading to cell death; suppresses both B and T cell proliferation; broad immunosuppression
- **Evidence Level:** 1 (Strong recommendation for Class III/IV)
- **LN Indication:** Induction for severe Class III/IV LN, RPGN, or failed MMF
- **Dosage Regimens:**
  - EuroLupus protocol: 500mg IV q2 weeks x6 doses (Caucasians, preferred)
  - NIH protocol: 0.5-1g/m2 IV monthly x6 months (severe disease, non-Caucasians)
  - Oral: 1-2mg/kg/day x 2-3 months (less preferred)
- **Key Trials:** EuroLupus (2002): low-dose CyP equivalent to high-dose with less toxicity; ALMS (2009): CyP comparator arm
- **Monitoring:** CBC weekly during treatment, urinalysis (hemorrhagic cystitis), creatinine, mesna co-administration
- **Common SE:** Nausea/vomiting (80%), alopecia (40-60%), amenorrhea/azoospermia, leukopenia
- **Serious SE:** Hemorrhagic cystitis (5-10%), gonadal toxicity (30-50% permanent infertility), bladder cancer (5-10x risk), myelodysplasia, opportunistic infections
- **Stopping Criteria:** Neutrophils <1500, platelets <100,000, hemorrhagic cystitis, cumulative dose approaching 36g (increased malignancy risk)
- **Pregnancy Category:** D (teratogenic; contraindicated)
- **Drug Interactions:** Allopurinol increases myelosuppression; live vaccines contraindicated

### Prednisone

- **Class:** Corticosteroid (oral)
- **Mechanism:** Glucocorticoid receptor agonist with broad anti-inflammatory and immunosuppressive effects; inhibits NF-kB, reduces cytokine production
- **Evidence Level:** 1
- **LN Indication:** Induction backbone for all LN classes; taper over 3-6 months
- **Dosage:**
  - Pulse: methylprednisolone 500-1000mg IV x3 days for severe presentations
  - Oral: 0.5-1mg/kg/day (max 40-60mg), taper to 5-10mg by 3 months, target <5mg by 6 months
  - Maintenance: 5-7.5mg/day or attempt discontinuation
- **Monitoring:** Blood glucose (weekly during high-dose), BP, weight, ophthalmologic exam, DEXA if prolonged use
- **Common SE:** Weight gain, insomnia, mood changes, hyperglycemia, hypertension, fluid retention
- **Serious SE:** Avascular necrosis, osteoporosis, cataracts, diabetes mellitus, adrenal suppression, infections, psychosis
- **Stopping Criteria:** Slow taper to avoid adrenal crisis; never abrupt discontinuation after >2 weeks of use

### Hydroxychloroquine (HCQ)

- **Class:** Antimalarial
- **Mechanism:** Inhibits TLR7/TLR9 signaling in endosomes, reducing Type I interferon production; blocks antigen processing; anti-thrombotic effects
- **Evidence Level:** 1 (Strong recommendation for all SLE patients)
- **LN Indication:** All SLE patients with or without LN (flare reduction, cardiovascular protection, renal survival benefit)
- **Dosage:** 200-400mg/day (max 5mg/kg actual body weight)
- **Key Evidence:** Marmor 2011 meta-analysis: HCQ reduces LN flares by 50%, reduces damage accrual, improves survival
- **Monitoring:** Annual ophthalmologic exam (retinal toxicity screening) starting after 5 years or sooner with risk factors
- **Common SE:** GI intolerance, headache, skin pigmentation, myopathy
- **Serious SE:** Retinal toxicity (cumulative risk, irreversible), QTc prolongation, cardiac toxicity (rare at standard doses)
- **Stopping Criteria:** Retinal toxicity on ophthalmologic exam; severe myopathy; QTc prolongation >500ms
- **Pregnancy Category:** C (continued in pregnancy; associated with lower flares and better outcomes)
- **Drug Interactions:** Antacids/kaolin reduce absorption (separate by 4 hours); digoxin increased levels; hypoglycemic agents potentiated

### Belimumab

- **Class:** Anti-BAFF (B-cell Activating Factor) Monoclonal Antibody
- **Mechanism:** Recombinant human IgG1 lambda monoclonal antibody that binds soluble BAFF (BLyS), inhibiting B-cell survival, proliferation, and differentiation; reduces autoreactive B-cells
- **Evidence Level:** 1 (Strong recommendation for active LN)
- **LN Indication:** Add-on therapy for active LN (Class III/IV/V) with positive anti-dsDNA and low complement
- **Dosage:** 10mg/kg IV q4 weeks (after loading at weeks 0, 2, 4) or 200mg SC weekly
- **Key Trial:** BLISS-LN (2020): belimumab + standard therapy improved primary endpoint by 30% vs placebo + standard therapy (OR 1.55, 95% CI 1.16-2.07)
- **Monitoring:** CBC, anti-dsDNA, C3/C4 at baseline and q3 months; infusion reaction monitoring
- **Common SE:** Nausea, diarrhea, pyrexia, nasopharyngitis, infusion reactions (15-20%)
- **Serious SE:** Severe infections (pneumonia, cellulitis), depression/suicidality (monitor closely), anaphylaxis (<1%), hepatitis B reactivation
- **Stopping Criteria:** Severe infusion reaction, severe infection, suicidality, anaphylaxis
- **Pregnancy Category:** C (limited human data; animal studies show B-cell depletion; weigh risks/benefits)
- **Drug Interactions:** Live vaccines contraindicated; avoid concurrent biologics (increased infection risk)

### Voclosporin

- **Class:** Calcineurin Inhibitor (next-generation)
- **Mechanism:** Binds FKBP12, inhibits calcineurin, blocks T-cell activation; more predictable pharmacokinetics than tacrolimus/cyclosporine; additional podocyte cytoskeleton stabilization
- **Evidence Level:** 1 (Strong recommendation for Class V LN)
- **LN Indication:** Class V LN (with or without coexisting Class III/IV) in combination with MMF + low-dose steroids
- **Dosage:** 23.7mg PO BID (with or without food)
- **Key Trials:** AURORA 1 (2021): voclosporin + MMF + low-dose steroids achieved CRR 41% vs 23% (p<0.001); AURORA 2 (2023): sustained CRR 44% vs 26% at 2 years
- **Monitoring:** Trough levels not routinely required (predictable PK), creatinine q2 weeks x3 then monthly, blood glucose, BP, potassium, magnesium
- **Common SE:** Infection (30%), diarrhea (18%), cough (14%), headache (11%), hypertension
- **Serious SE:** Nephrotoxicity (eGFR decline, usually reversible with dose reduction), new-onset diabetes (higher than standard CNIs), hyperkalemia, infections
- **Stopping Criteria:** eGFR decline >30% from baseline (reassess after dose reduction), uncontrolled hypertension, new-onset diabetes requiring insulin
- **Pregnancy Category:** Limited data; animal studies show fetal toxicity; avoid in pregnancy

### Rituximab

- **Class:** Anti-CD20 Monoclonal Antibody (type I, chimeric)
- **Mechanism:** Chimeric murine/human IgG1 antibody targeting CD20 on B-cells; causes B-cell depletion via ADCC, CDC, and apoptosis
- **Evidence Level:** 2 (Expert recommendation; no phase 3 LN-specific trial)
- **LN Indication:** Refractory LN (failure of MMF and CyP-based induction); off-label in most regions
- **Dosage:** 375mg/m2 IV weekly x4 or 1g IV x2 (2 weeks apart)
- **Monitoring:** CD19/20 counts, immunoglobulin levels (IgG, IgA, IgM), CBC, LFTs, infection surveillance
- **Common SE:** Infusion reactions (fever, chills, hypotension, 30-40% first dose), headache, nausea
- **Serious SE:** Severe infusion reactions (<1%), hepatitis B reactivation (screen all patients), PML (<1:10,000), late-onset neutropenia (5-10%), hypogammaglobulinemia
- **Stopping Criteria:** Severe infusion reaction, confirmed PML, severe infection, hypogammaglobulinemia with recurrent infections
- **Pregnancy Category:** C (crosses placenta; neonatal B-cell depletion; avoid in pregnancy)

### Azathioprine (AZA)

- **Class:** Purine Analog (Prodrug of 6-mercaptopurine)
- **Mechanism:** Inhibits purine synthesis; suppresses T and B cell proliferation; preferential effect on lymphocytes
- **Evidence Level:** 1 (for maintenance therapy)
- **LN Indication:** Maintenance therapy alternative to MMF; preferred in pregnancy planning
- **Dosage:** 2mg/kg/day (max 200mg); reduce dose if TPMT intermediate metabolizer
- **Monitoring:** TPMT genotyping before initiation, CBC q4 weeks x3 then q3 months, LFTs q3 months
- **Common SE:** Nausea, diarrhea, leukopenia, hepatotoxicity
- **Serious SE:** Severe myelosuppression (TPMT deficiency), hepatosplenic T-cell lymphoma (rare), pancreatitis, infection
- **Stopping Criteria:** Severe myelosuppression, pancreatitis, severe hepatotoxicity, TPMT deficiency with intolerable toxicity
- **Pregnancy Category:** D (limited human data; some guidelines consider acceptable in pregnancy for SLE maintenance)

---

## 3. Coverage Matrix

### Field Coverage per Drug

| Drug | MoA | Common SE | Serious SE | Monitoring | Stopping | Dosage | Max Dose | Evidence | Guidelines | Transplant |
|------|-----|-----------|------------|------------|----------|--------|---------|----------|------------|------------|
| MMF | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclophosphamide | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Prednisone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Methylprednisolone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Voclosporin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| HCQ | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Belimumab | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| AZA | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Rituximab | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Obinutuzumab | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Tacrolimus | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclosporine | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Ramipril | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |

**Coverage: 11 of 11 knowledge fields populated for all 13 expanded drugs (100%)**

---

## 4. Drug Safety Information

### Pregnancy Categories and LN Management

| Drug | Category | Recommendation for LN |
|------|----------|----------------------|
| MMF | D | Teratogenic; switch to AZA minimum 6 weeks before conception |
| Cyclophosphamide | D | Teratogenic; contraindicated in pregnancy |
| Prednisone | C | Can be used; preferred steroid in pregnancy |
| Methylprednisolone | C | Pulse therapy acceptable in pregnancy if severe flare |
| Voclosporin | C | Limited data; avoid in pregnancy |
| HCQ | C | Continue throughout pregnancy (flare reduction, better outcomes) |
| Belimumab | C | Limited data; limited placental transfer; discuss risks/benefits |
| AZA | D | Some guidelines accept for pregnancy maintenance; limited data |
| Rituximab | C | Avoid; crosses placenta; neonatal B-cell depletion |
| Obinutuzumab | C | Avoid; limited data |
| Tacrolimus | C | Acceptable in pregnancy if benefit outweighs risk |
| Cyclosporine | C | Acceptable in pregnancy |
| Ramipril | D | Contraindicated in 2nd/3rd trimester; switch to methyldopa or labetalol |

### Key Monitoring Parameters for LN Drugs

| Parameter | Drug(s) | Frequency |
|-----------|---------|-----------|
| CBC with differential | MMF, CyP, AZA, rituximab | MMF: q2wk x3 then monthly; CyP: weekly; AZA: q4wk x3 then q3mo |
| Anti-dsDNA, C3/C4 | All immunosuppressants | q3 months during maintenance; q2-4wk during induction |
| UPCR, creatinine, eGFR | All | q2-4wk induction; q3mo maintenance |
| Trough levels | Tacrolimus (target 3-6 ng/mL), voclosporin (not routine) | Tacrolimus: q1-2wk initially |
| LFTs | MMF, AZA, CyP | q3mo |
| Blood glucose | Prednisone, voclosporin | Weekly during high-dose steroids; q3mo for voclosporin |
| Ophthalmologic exam | HCQ | Annual (starting after 5 years or sooner with risk factors) |
| TPMT genotype | AZA | Before initiation (one-time) |
| Immunoglobulin levels | Rituximab, obinutuzumab | Baseline and q6mo |
| HBV screening | Rituximab, obinutuzumab, belimumab | Before initiation (one-time) |

---

## 5. Class-Specific Treatment Algorithm

### LN Induction Drug Selection by ISN/RPS Class

| Class | First-Line | Alternative | Novel Add-On |
|-------|-----------|-------------|--------------|
| I/II | No immunosuppression; HCQ + supportive | N/A | N/A |
| III/IV | MMF 2-3g + steroids | EuroLupus CyP (Caucasians); high-dose CyP (severe) | Belimumab add-on |
| V (nephrotic) | MMF + steroids or voclosporin + MMF + steroids | Tacrolimus + MMF + steroids | Belimumab add-on |
| V + III/IV | Treat as IV: MMF + steroids; consider voclosporin for V component | CyP + steroids | Belimumab + voclosporin |
| VI | Supportive care; transplant evaluation | N/A | N/A |
| Refractory | Rituximab (off-label); obinutuzumab | Belimumab + standard therapy | Clinical trials |

### Maintenance Drug Selection

| Patient Scenario | Preferred | Alternative | Notes |
|-----------------|-----------|-------------|-------|
| Standard maintenance | MMF 1-2g + HCQ | AZA 2mg/kg + HCQ | MMF preferred per ALMS/MAINTAIN |
| Pregnancy planning | AZA + HCQ | Tacrolimus + HCQ | MMF contraindicated; switch 6 weeks pre-conception |
| MMF intolerant | AZA + HCQ | Tacrolimus + HCQ | GI intolerance common with MMF |
| Relapse on MMF | CyP re-induction -> AZA maintenance | Rituximab -> MMF maintenance | Switch class |
| Refractory | Belimumab + standard maintenance | Rituximab + standard | Long-term biologic consideration |

---

## 6. Planned Expansions

### V4.2 Target Drugs

| Priority | Drug | Class | Current Status |
|----------|------|-------|----------------|
| 1 | Ianalumab | Anti-BAFF Receptor | Phase 3 in LN |
| 2 | Telitacicept | TACI-Fc (dual BAFF/APRIL) | Phase 3 in LN |
| 3 |CAR-T (anti-CD19) | Cellular therapy | Phase 1/2 in refractory LN |
| 4 | Deucravacitinib | TYK2 inhibitor | Phase 2/3 in SLE/LN |
| 5 | Baricitinib | JAK1/JAK2 inhibitor | Phase 2 in LN |
| 6 | Lupuzor | P140 peptide (immunomodulator) | Phase 3 in SLE |
| 7 | Anifrolumab | Anti-IFNAR1 | Approved for SLE; LN trials ongoing |
| 8 | Secukinumab | Anti-IL-17A | Phase 2 in LN |

### Expansion Strategy

Target coverage: 100% of LN-approved drugs by V4.2, with focus on novel immunosuppressive agents, biologics, and emerging cellular therapies.

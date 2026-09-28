# Lupus Nephritis Clinical Pathway Library

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Disease:** Lupus Nephritis (id=`lupus_nephritis`)
**Pathways Model:** `knowledge.models.ClinicalPathway`

---

## 1. Complete 6-Stage Pathway Overview

The Lupus Nephritis clinical pathway defines the complete care journey from initial biopsy through long-term ESKD management. All stages are defined in the `ClinicalPathway` model and seeded via `seed_v4_knowledge.py`. The pathway branches based on ISN/RPS class at Stage 2, with distinct induction protocols for Class III/IV (proliferative) versus Class V (membranous).

### Text-Based Pathway Diagram

```
STAGE 1: DIAGNOSIS & CLASSIFICATION
  [Duration: 14 days | 8 required actions]
  |
  v
STAGE 2: INDUCTION THERAPY (CLASS III/IV)
  [Duration: 180 days | 10 required actions]
  |
  +--(Class I/II at Stage 1)----> MONITOR with supportive care
  |
  +--(Class III/IV at Stage 1)--> STAGE 2: INDUCTION III/IV
  |                                   |
  |                                   +--(complete/partial response)--> STAGE 4: MAINTENANCE
  |                                   |
  |                                   +--(no response at 6mo)--> STAGE 5: RELAPSE/REFRACTORY
  |
  +--(Class V at Stage 1)------> STAGE 3: INDUCTION CLASS V
  |                               [Duration: 180 days | 8 required actions]
  |                               |
  |                               +--(complete/partial response)--> STAGE 4: MAINTENANCE
  |                               |
  |                               +--(no response at 6mo)--> STAGE 5: RELAPSE/REFRACTORY
  |
  +--(Class VI at Stage 1)------> STAGE 6: LONG-TERM & ESKD
  |
  +--(Mixed III/IV + V)---------> Treat as Class IV with adjunctive MMF

STAGE 4: MAINTENANCE THERAPY
  [Duration: 365 days (repeating, minimum 3 years) | 10 required actions]
  |
  +--(relapse)---------------> STAGE 5: RELAPSE/REFRACTORY
  |
  +--(stable remission)------> Continue maintenance
  |
  +--(ESKD progression)------> STAGE 6: LONG-TERM & ESKD

STAGE 5: RELAPSE / REFRACTORY
  [Duration: 180 days | 10 required actions]
  |
  +--(response to re-induction)--> STAGE 4: MAINTENANCE
  |
  +--(refractory)---------------> STAGE 6: LONG-TERM & ESKD

STAGE 6: LONG-TERM & ESKD
  [Duration: 730 days (repeating) | 8 required actions]
```

---

## 2. Detailed Per-Stage Breakdown

### Stage 1: Diagnosis & Classification

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-01 |
| **Expected Duration** | 14 days |
| **Next Stages** | Stage 2 (Class III/IV), Stage 3 (Class V), Stage 6 (Class VI), Monitor (Class I/II) |

**Required Actions (8):**

1. Confirm SLE diagnosis per ACR/SLICC/EULAR-ACR criteria (malar rash, arthritis, serositis, cytopenias, ANA/anti-dsDNA positive)
2. Quantify proteinuria: spot UPCR or 24-hour urine collection; threshold for biopsy >0.5g/24h or RBC casts
3. Urinalysis with microscopy: dysmorphic RBCs, RBC casts, WBC casts, granular casts
4. Serologic assessment: anti-dsDNA titer, C3, C4, CBC with differential, serum creatinine, eGFR, albumin
5. Antiphospholipid antibody panel: lupus anticoagulant, anticardiolipin, anti-beta2GPI (for APLS risk)
6. Kidney biopsy with ISN/RPS class assignment, AI and CI scoring, IF, EM
7. APL antibody positivity: assess thrombotic risk, consider anticoagulation
8. Baseline assessment: BP, volume status, infection screening (HBV, TB), vaccination status

**Criteria to Proceed to Stage 2 or 3:**

- Biopsy-confirmed ISN/RPS class (I-VI) assigned
- AI and CI scores documented
- Complete baseline serologic workup obtained
- SLE disease activity assessed (SLEDAI-2K)

**Warnings:**

- Biopsy should be performed promptly when indication exists; delay increases risk of irreversible damage
- Class IV-G diffuse global carries worst prognosis and requires most aggressive therapy
- Class V coexisting with Class III/IV requires combined treatment approach
- APL antibody positivity alters thrombotic management and may affect renal vascular pathology
- Silent LN (10-20%) may present with normal urinalysis but biopsy-proven disease

### Stage 2: Induction Therapy (Class III/IV)

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-02 |
| **Expected Duration** | 180 days (6 months) |
| **Next Stages** | Stage 4 (complete/partial response), Stage 5 (no response) |

**Required Actions (10):**

1. Select induction regimen: MMF 2-3g/day + prednisone (preferred) OR EuroLupus IV CyP + prednisone (Caucasians) OR high-dose IV CyP + prednisone (severe/RPGN)
2. Pulse methylprednisolone 500-1000mg IV x3 days for severe presentations (nephrotic syndrome, AKI, RPGN)
3. Oral prednisone 0.5-1mg/kg/day with taper to <10mg by 3-6 months
4. Initiate hydroxychloroquine 200-400mg/day for all SLE patients (unless contraindicated)
5. MMF dosing: start 500mg BID, titrate to 1g BID over 2-4 weeks; target 2-3g/day
6. Monitor for MMF adverse effects: GI symptoms, leukopenia, infection; CBC q2 weeks x3 then monthly
7. If CyP selected: IV pulse monthly (EuroLupus 500mg q2wk x6 or NIH 0.5-1g/m2 qmonth x6); mesna co-administration; CBC weekly
8. Assess serologic response at 3 months: anti-dsDNA trending down, C3/C4 normalizing
9. Assess clinical response at 6 months: UPCR, creatinine, urinalysis
10. PCP prophylaxis (TMP-SMX) if on combination steroids + immunosuppression

**Criteria to Proceed to Stage 4:**

- Complete response: UPCR <0.5, normal creatinine, inactive urine sediment
- Partial response: >50% reduction in proteinuria, stable/improved creatinine
- Minimum 6 months of induction therapy completed

**Warnings:**

- MMF is teratogenic; pregnancy test required before initiation; reliable contraception mandatory
- CyP carries risk of hemorrhagic cystitis (mesna co-administration essential), gonadal toxicity, malignancy
- Steroid complications: monitor glucose, BP, bone density; consider bisphosphonates if prolonged use
- HCQ ophthalmologic screening required at baseline and annually (retinal toxicity)
- Infection is the leading cause of death in LN; low threshold for investigation

### Stage 3: Induction Therapy (Class V)

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-03 |
| **Expected Duration** | 180 days (6 months) |
| **Next Stages** | Stage 4 (complete/partial response), Stage 5 (no response) |

**Required Actions (8):**

1. Select induction regimen: MMF 2-3g/day + low-dose prednisone OR CNI (voclosporin 23.7mg BID or tacrolimus) + MMF + low-dose prednisone
2. Voclosporin-based regimen: voclosporin 23.7mg BID + MMF 1g BID + low-dose prednisone (20mg tapering to 5mg by 24 weeks) per AURORA protocol
3. CNI alternative: tacrolimus 2-4mg/day (target trough 3-6 ng/mL) + MMF + low-dose prednisone
4. HCQ 200-400mg/day for all Class V patients
5. Monitor for CNI toxicity: trough levels q1-2 weeks initially, eGFR, BP, glucose
6. Assess serologic response at 3 months: anti-dsDNA, C3/C4
7. Assess clinical response at 6 months: UPCR, creatinine, albumin
8. Anticoagulation consideration if nephrotic syndrome (albumin <2.5 g/dL)

**Criteria to Proceed to Stage 4:**

- Complete response: UPCR <0.5, serum albumin >3.5 g/dL
- Partial response: >50% reduction in proteinuria, albumin >3.0 g/dL
- Minimum 6 months of therapy completed

**Warnings:**

- Class V with coexisting Class III/IV requires combined treatment approach (treat proliferative component first)
- CNI nephrotoxicity requires close monitoring; hold if eGFR declines >30% from baseline
- Voclosporin: monitor blood glucose (higher rates of new-onset diabetes vs standard CNI)
- Nephrotic-range proteinuria increases VTE risk; assess anticoagulation need
- Class V may have slower response kinetics; extend assessment to 12 months if partial response

### Stage 4: Maintenance Therapy

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-04 |
| **Expected Duration** | 365 days (repeating; minimum 3 years, often indefinite) |
| **Next Stages** | Stage 5 (relapse), Stage 6 (ESKD progression) |

**Required Actions (10):**

1. Select maintenance agent: MMF 1-2g/day (preferred) OR AZA 2mg/kg/day (if MMF intolerant or pregnancy desired)
2. Continue HCQ 200-400mg/day for all SLE patients (cardiovascular benefit, flare reduction)
3. Low-dose prednisone 5-7.5mg/day if needed for disease control; attempt taper to <5mg or discontinuation
4. Monitor q3 months: UPCR, creatinine, eGFR, anti-dsDNA, C3/C4, CBC, albumin
5. MMF monitoring: CBC q3 months, LFTs q6 months; dose adjust for GI intolerance or leukopenia
6. AZA monitoring: CBC q4 weeks initially then q3 months; TPMT genotyping before initiation; LFTs
7. Relapse surveillance: rising anti-dsDNA with falling C3/C4 precedes clinical relapse by 3-6 months
8. Reassess maintenance duration annually; minimum 3 years after complete response
9. Cardiovascular risk management: statins, BP control, smoking cessation
10. Bone health: vitamin D supplementation, DEXA scan if prolonged steroid use, bisphosphonates

**Criteria for Stage 5 (Relapse):**

- Complete renal relapse: UPCR rises to >1g after prior complete response
- Partial renal relapse: >50% increase in proteinuria from nadir
- Serologic flare: rising anti-dsDNA with falling complements

**Warnings:**

- MMF is teratogenic; transition to AZA minimum 6 weeks before planned conception
- AZA: TPMT deficiency increases myelosuppression risk; test before initiation
- HCQ: annual ophthalmologic exam mandatory; retinal toxicity risk increases with cumulative dose
- Premature discontinuation of maintenance therapy is a major cause of relapse
- Minimum 3 years of maintenance; many patients require indefinite therapy

### Stage 5: Relapse / Refractory Disease

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-05 |
| **Expected Duration** | 180 days |
| **Next Stages** | Stage 4 (response), Stage 6 (refractory/ESKD) |

**Required Actions (10):**

1. Confirm relapse vs non-adherence or infection (reassess compliance, infection screening)
2. Repeat renal biopsy if class switch suspected or to assess activity vs chronicity
3. Relapse on MMF: switch to CyP-based re-induction then AZA maintenance
4. Relapse on AZA: switch to MMF-based re-induction then MMF maintenance
5. Refractory to first-line: add belimumab (anti-BAFF) to standard regimen
6. Refractory to two lines: consider rituximab (anti-CD20) off-label
7. Refractory to three lines: consider obinutuzumab (anti-CD20, novel) or voclosporin
8. Repeat biopsy for chronicity assessment: if CI >7, response unlikely; consider supportive care
9. Monitor for complications: infection prophylaxis, gonadal preservation (GnRH agonists if CyP)
10. ESKD preparation: vascular access planning, transplant evaluation, renal replacement therapy counseling

**Criteria to Proceed to Stage 4:**

- Response to re-induction: >50% reduction in proteinuria, stable creatinine
- Complete response: UPCR <0.5

**Warnings:**

- Refractory LN carries high risk of ESKD (50% within 5-10 years)
- Repeat biopsy essential: chronic damage (CI >7) limits response to further immunosuppression
- Rituximab: risk of HBV reactivation (screen before administration), PML (rare), hypogammaglobulinemia
- Gonadal toxicity with CyP: consider GnRH agonist co-treatment for fertility preservation
- Infection prophylaxis: PCP prophylaxis, consider antifungal in high-risk patients

### Stage 6: Long-Term & ESKD

| Property | Value |
|----------|-------|
| **Stage ID** | LN-PATH-06 |
| **Expected Duration** | 730 days (repeating cycle) |
| **Next Stages** | None (terminal stage) |

**Required Actions (8):**

1. Define ESKD: eGFR <15 mL/min/1.73m2 or initiation of renal replacement therapy
2. Dialysis modality selection: hemodialysis vs peritoneal dialysis; vascular access planning
3. Transplant evaluation: timing, immunologic assessment, APL antibody management
4. Maintain immunosuppression: low-dose MMF or AZA + HCQ if transplant listed
5. Cardiovascular risk optimization: aggressive BP, lipids, glucose control
6. Complication screening: CKD-MBD (calcium, phosphate, PTH, vitamin D), anemia (EPO), metabolic acidosis
7. Post-transplant monitoring: protocol biopsies, DSA monitoring, LN recurrence surveillance (10-30%)
8. Long-term follow-up: nephrology q3 months, transplant q1-3 months (post-transplant), cancer screening

**Warnings:**

- ESKD in LN has better prognosis than non-diabetic ESKD if managed aggressively
- Transplant recurrence: 10-30%; monitor with protocol biopsies and serology
- APL antibody positivity affects transplant management; consider anticoagulation peri-transplant
- Post-transplant LN recurrence may present as subclinical disease on protocol biopsy
- Accelerated atherosclerosis persists even after transplant; ongoing cardiovascular management essential

---

## 3. Clinical Workflow Description

The Lupus Nephritis clinical pathway follows the KDIGO 2021 Chapter 10 management approach with class-specific branching:

1. **Diagnosis triggers pathway entry** - All patients with suspected LN enter at Stage 1; biopsy required for class assignment
2. **Class determines induction pathway** - Class III/IV enters Stage 2 (MMF or CyP-based induction); Class V enters Stage 3 (MMF or CNI-based induction); Class I/II monitored; Class VI enters ESKD pathway
3. **Response assessment at 6 months** - Complete/partial response proceeds to maintenance; no response proceeds to relapse/refractory pathway
4. **Maintenance is long-term** - Minimum 3 years; many patients require indefinite therapy with MMF or AZA + HCQ
5. **Relapse management is class-dependent** - Re-induction with alternative agents; refractory disease progresses through novel therapies
6. **ESKD management** - Dialysis, transplant, and long-term complication screening

### Class-Specific Treatment Branching

| ISN/RPS Class | Induction Regimen | Maintenance | Duration |
|---------------|-------------------|-------------|----------|
| I | Monitor (no IS) | N/A | Ongoing surveillance |
| II | Supportive care (RAASi, HCQ) | N/A | Ongoing surveillance |
| III (focal) | MMF 2-3g + steroids (preferred) or EuroLupus CyP + steroids | MMF 1-2g + HCQ | Minimum 3 years |
| IV (diffuse) | MMF 2-3g + steroids (preferred) or high-dose CyP + steroids | MMF 1-2g + HCQ | Indefinite |
| V (membranous) | MMF + steroids or voclosporin + MMF + steroids | MMF + HCQ | Minimum 3 years |
| V + III/IV | Treat as Class IV; add MMF for membranous component | MMF + HCQ | Indefinite |
| VI (sclerosing) | Supportive care; transplant evaluation | N/A | ESKD management |

---

## 4. Pathway Validation Status

| Validation Aspect | Status | Details |
|-------------------|--------|---------|
| Model Implementation | VALIDATED | `ClinicalPathway` model in `knowledge/models.py` |
| Seed Data | VALIDATED | Seeded via `seed_v4_knowledge.py` PATHWAYS dictionary |
| Stage Sequence | VALIDATED | 6 stages with correct ordering and transitions |
| Required Actions | VALIDATED | 8/10/8/10/10/8 actions per stage |
| Duration Values | VALIDATED | 14/180/180/365/180/730 days |
| Next Stage Links | VALIDATED | All transitions validated against clinical logic |
| Criteria to Proceed | VALIDATED | Clinically appropriate transition criteria |
| Warnings | VALIDATED | Safety warnings aligned with KDIGO 2021 and EULAR recommendations |
| Class Branching | VALIDATED | Distinct pathways for Class III/IV vs Class V induction |

---

## 5. Cross-Disease Applicability

| Disease | Priority | Stage Count | Status |
|---------|----------|-------------|--------|
| Membranous Nephropathy | HIGH | 6 | COMPLETE |
| FSGS | MEDIUM | 5 | Template designed, content pending |
| ANCA Vasculitis | MEDIUM | 6 | Template designed, content pending |
| Minimal Change Disease | LOW | 4 | Not yet scoped |
| C3 Glomerulopathy | LOW | 4 | Not yet scoped |

The LN pathway extends the standard GN pathway template with class-specific branching at Stage 2/3 and novel therapy integration (belimumab, voclosporin, obinutuzumab) at Stage 5. This class-branching pattern is unique to LN and may inform future pathway designs for diseases with histologic subtype-driven treatment decisions.

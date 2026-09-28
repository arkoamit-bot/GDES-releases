# Drug Knowledge Library — IgA-Related Medications

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `treatments.models.DrugMaster`
**Coverage:** 20 drugs with expanded knowledge (32.8% of 61-drug formulary)

---

## 1. Complete Drug Inventory

The following 20 drugs have fully expanded knowledge fields (mechanism, side effects, monitoring, stopping criteria, dosage, evidence), seeded via `seed_drug_knowledge.py`:

### IgA Nephropathy Primary Therapy Drugs

| Generic Name | Class | Drug Class Code | IgAN Indication | Evidence Level |
|--------------|-------|-----------------|-----------------|----------------|
| Ramipril | ACE Inhibitor (RAASi) | `raasi` | First-line antiproteinuric | 1 |
| Lisinopril | ACE Inhibitor (RAASi) | `raasi` | First-line antiproteinuric | 1 |
| Losartan | ARB (RAASi) | `raasi` | First-line antiproteinuric | 1 |
| Valsartan | ARB (RAASi) | `raasi` | First-line antiproteinuric | 1 |
| Telmisartan | ARB (RAASi) | `raasi` | First-line antiproteinuric | 1 |
| Empagliflozin | SGLT2 Inhibitor | `sglt2i` | Renoprotection in CKD | 1 |
| Dapagliflozin | SGLT2 Inhibitor | `sglt2i` | Renoprotection in CKD | 1 |
| Budesonide (Nefecon) | Corticosteroid (gut-targeted) | `steroid` | Targeted IgAN therapy | 1 |
| Methylprednisolone | Corticosteroid (IV) | `steroid` | Crescentic/RPGN induction | 1 |
| Prednisolone | Corticosteroid (oral) | `steroid` | High-risk IgAN induction | 1 |
| Mycophenolate Mofetil | IMPDH Inhibitor | `mmf` | Rescue/steroid-sparing | 2 |
| Azathioprine | Purine Antimetabolite | `azathioprine` | Maintenance (limited role) | 2 |
| Cyclophosphamide | Alkylating Agent | `cyclophosphamide` | Severe crescentic IgAN | 1 |
| Cyclosporine | Calcineurin Inhibitor | `cni` | Alternative steroid-sparing | 2 |
| Tacrolimus | Calcineurin Inhibitor | `cni` | Alternative steroid-sparing | 2 |
| Rituximab | Anti-CD20 Monoclonal | `rituximab` | Refractory/transplant recurrence | 2 |

### Adjuvant Therapy Drugs

| Generic Name | Class | Drug Class Code | IgAN Indication | Evidence Level |
|--------------|-------|-----------------|-----------------|----------------|
| Atorvastatin | HMG-CoA Reductase Inhibitor | `statin` | Cardiovascular risk reduction | 1 |
| Spironolactone | Mineralocorticoid Antagonist | `other` | Adjunctive antiproteinuric | 2 |
| Allopurinol | Xanthine Oxidase Inhibitor | `other` | Hyperuricemia in CKD | 2 |
| Hydroxychloroquine | Antimalarial | `hcq` | Immunomodulatory (limited data) | 2 |

---

## 2. Per-Drug Summary

### Ramipril
- **Class:** ACE Inhibitor
- **Mechanism:** Competitive inhibitor of angiotensin-converting enzyme, reducing angiotensin II production
- **Evidence Level:** 1 (Strong recommendation)
- **IgAN Indication:** First-line antiproteinuric and renoprotective therapy in all IgAN patients with proteinuria >0.5g/day
- **Pregnancy Category:** D (contraindicated)
- **Monitoring:** BP, renal function, serum potassium at 1-2 weeks after initiation and dose changes

### Lisinopril
- **Class:** ACE Inhibitor
- **Mechanism:** Angiotensin-converting enzyme inhibitor
- **Evidence Level:** 1
- **IgAN Indication:** Alternative first-line RAASi to ramipril

### Losartan
- **Class:** ARB
- **Mechanism:** Selective angiotensin II receptor type 1 blocker
- **Evidence Level:** 1
- **IgAN Indication:** First-line when ACEi not tolerated (cough, angioedema)

### Empagliflozin
- **Class:** SGLT2 Inhibitor
- **Mechanism:** Selective SGLT2 inhibition reducing glucose and sodium reabsorption in proximal tubule
- **Evidence Level:** 1
- **IgAN Indication:** Renoprotection in patients with eGFR >25; supported by EMPA-KIDNEY
- **Dosage:** 10mg once daily

### Budesonide (Nefecon)
- **Class:** Targeted Corticosteroid
- **Mechanism:** Gut-targeted glucocorticoid with high first-pass hepatic metabolism (90%), reducing mucosal B-cell IgA production
- **Evidence Level:** 1
- **IgAN Indication:** For patients with persistent proteinuria >1g/day despite 90 days of optimized RAASi
- **Dosage:** 16mg/day for 9 months
- **Key Trial:** NefIgArd (Part A and Part B)

### Methylprednisolone
- **Class:** IV Corticosteroid
- **Mechanism:** Potent glucocorticoid with anti-inflammatory and immunosuppressive effects
- **Evidence Level:** 1
- **IgAN Indication:** Pulse therapy for crescentic IgAN/RPGN
- **Dosage:** 1g IV x3 pulses

---

## 3. Coverage Matrix

### Field Coverage per Drug

| Drug | MoA | Common SE | Serious SE | Monitoring | Stopping | Dosage | Max Dose | Evidence | Guidelines | Transplant |
|------|-----|-----------|------------|------------|----------|--------|---------|----------|------------|------------|
| Ramipril | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Lisinopril | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Losartan | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Valsartan | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Telmisartan | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Empagliflozin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Dapagliflozin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Budesonide | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Methylprednisolone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Prednisolone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| MMF | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Azathioprine | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclophosphamide | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Cyclosporine | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Tacrolimus | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Rituximab | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Atorvastatin | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Spironolactone | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| Allopurinol | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |
| HCQ | YES | YES | YES | YES | YES | YES | YES | YES | YES | YES |

**Coverage: 11 of 11 knowledge fields populated for all 20 drugs (100%)**

### Additional Drug Master Fields

| Field | Coverage (20 drugs) | Description |
|-------|--------------------|-------------|
| generic_name | 100% | Unique drug identifier |
| brand_names | 100% | Bangladeshi brand names |
| drug_class | 100% | Research analytics classification |
| available_strengths | 100% | Formulation strengths |
| renal_dose_adjust | 100% | Renal adjustment flag |
| nephrotoxic | 100% | Nephrotoxicity flag |
| pregnancy_category | 100% | FDA pregnancy category |
| lactation_safety | 100% | Lactation safety classification |

---

## 4. Drug Safety Information

### Pregnancy Categories

| Drug | Category | Recommendation |
|------|----------|---------------|
| Ramipril | D | Contraindicated in 2nd/3rd trimester |
| Lisinopril | D | Contraindicated in 2nd/3rd trimester |
| Losartan | D | Contraindicated in 2nd/3rd trimester |
| Empagliflozin | X | Contraindicated |
| Mycophenolate Mofetil | D | Teratogenic; switch to AZA before conception |
| Cyclophosphamide | D | Teratogenic; contraindicated in pregnancy |
| Prednisolone | B | Preferred steroid in pregnancy |
| Rituximab | C | Avoid in pregnancy; crosses placenta |

### Key Monitoring Parameters

| Parameter | Drug(s) | Frequency |
|-----------|---------|-----------|
| BP, eGFR, K+ | All RAASi | 1-2 weeks post-initiation/dose change |
| eGFR, volume status | All SGLT2i | Before and after initiation |
| CBC, LFTs | MMF, AZA, CyP | Weekly x4 then monthly x3 |
| Trough levels | Tacrolimus, Cyclosporine | Per protocol (5-15 ng/mL for tacro) |
| Glucose, HbA1c | Corticosteroids | Weekly during high-dose |
| CD19/20 counts | Rituximab | Optional; confirm depletion |
| Ophthalmology | HCQ (use >5 years) | Annual after 5 years |

---

## 5. Planned Expansions

### V4.2 Target Drugs (next 15 drugs for expanded knowledge)

| Priority | Drug | Class | Current Status |
|----------|------|-------|----------------|
| 1 | Sparsentan | ERA+ARB dual | Knowledge drafted, awaiting full expansion |
| 2 | Belimumab | Anti-BAFF | Limited IgAN data, expanding for lupus |
| 3 | Atacicept | APRIL/BAFF inhibitor | Emerging IgAN therapy |
| 4 | Telitacicept | APRIL/BAFF inhibitor | Emerging IgAN therapy |
| 5 | Iptacopan | Complement inhibitor | Emerging therapy |
| 6 | Narsoplimab | MASP-2 inhibitor | Complement-targeted |
| 7 | Sodium bicarbonate | Alkalinizing agent | CKD metabolic acidosis |
| 8 | Sevelamer | Phosphate binder | CKD-MBD management |
| 9 | Cinacalcet | Calcimimetic | CKD-MBD management |
| 10 | Erythropoietin | ESA | CKD anemia |
| 11 | Roxadustat | HIF-PHI | CKD anemia |
| 12 | Sulfamethoxazole/TMP | Antibiotic | PCP prophylaxis |
| 13 | Valacyclovir | Antiviral | CMV prophylaxis |
| 14 | Warfarin | Anticoagulant | Nephrotic syndrome VTE |
| 15 | Furosemide | Diuretic | Volume management |

### Expansion Strategy

Target coverage: 50% of 61-drug formulary by V4.2, 75% by V4.3.
Priority assigned by: (1) IgAN therapeutic relevance, (2) CKD comorbidity management, (3) immunosuppression support medications.

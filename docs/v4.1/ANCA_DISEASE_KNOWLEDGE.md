# ANCA-Associated Vasculitis Disease Knowledge Specification

**Document ID**: ANCA_DK  
**Version**: 1.0  
**Date**: 2026-07-10  
**Domain**: ANCA-Associated Pauci-Immune Glomerulonephritis  
**Classification**: Systemic Vasculitis with Renal Involvement  

---

## 1. Overview

ANCA-associated vasculitis (AAV) is a group of systemic autoimmune disorders characterised by necrotising inflammation of small blood vessels, with a strong predilection for renal involvement manifesting as pauci-immune crescentic glomerulonephritis. The three clinical syndromes are granulomatosis with polyangiitis (GPA), microscopic polyangiitis (MPA), and eosinophilic granulomatosis with polyangiitis (EGPA). Renal involvement in AAV presents most commonly as rapidly progressive glomerulonephritis (RPGN) and, without prompt treatment, leads to irreversible kidney injury and end-stage kidney disease (ESKD). The discovery of anti-neutrophil cytoplasmic antibodies (ANCA) directed against proteinase 3 (PR3) or myeloperoxidase (MPO) has revolutionised the understanding, classification, and monitoring of these disorders.

---

## 2. 21-Field Disease Knowledge Schema

### 2.1 Definition

ANCA-associated pauci-immune glomerulonephritis is defined as a necrotising crescentic glomerulonephritis with a paucity of immunoglobulin deposition on immunofluorescence, occurring in the context of systemic small-vessel vasculitis. The pauci-immune pattern distinguishes it from immune-complex mediated glomerulonephritides such as lupus nephritis or IgA nephropathy. The hallmark histopathological finding is fibrinoid necrosis and crescent formation affecting glomerular capillaries, with extracapillary proliferation (crescents) occupying Bowman space. The disease spectrum spans three clinicopathological syndromes: GPA, characterised by necrotising granulomatous inflammation of the respiratory tract and kidney; MPA, defined by necrotising vasculitis without granulomas; and EGPA, featuring eosinophil-rich necrotising granulomatous inflammation with asthma and eosinophilia. Serologically, GPA is associated with PR3/c-ANCA in approximately 80-90% of cases, MPA with MPO/p-ANCA in 70-80%, and EGPA with MPO/p-ANCA in 40-50%. A small subset of patients (approximately 10%) are ANCA-negative by standard immunoassays but still satisfy clinicopathological criteria. The unifying pathophysiological feature is neutrophil-mediated endothelial injury leading to necrotising inflammation across multiple vascular beds.

### 2.2 Epidemiology

| Parameter | Value |
|-----------|-------|
| Annual incidence (AAV all) | 13–20 per million |
| GPA incidence | 8–12 per million |
| MPA incidence | 5–10 per million |
| EGPA incidence | 1–3 per million |
| Peak age at onset | 55–70 years |
| Male:Female ratio | 1.3:1 |
| Renal involvement (GPA) | 70–80% |
| Renal involvement (MPA) | 85–90% |
| Renal involvement (EGPA) | 30–40% |
| ESKD at 5 years | 20–30% |
| Geographic variation | MPO/MPA more common in Asia, PR3/GPA in Northern Europe |

The global incidence of AAV shows significant geographic and ethnic variation. In Northern Europe, GPA with PR3-ANCA predominates, while MPA with MPO-ANCA is more common in Southern Europe, Asia, and the Middle East. The highest reported incidence rates come from Sweden and Norway (20 per million), with lower rates in Japan (5 per million). Renal involvement at disease onset is seen in approximately 50-60% of GPA patients, 70-80% of MPA patients, and 25-30% of EGPA patients. The lifetime risk of developing ESKD ranges from 20-35%, with risk factors including delayed diagnosis, severe renal impairment at presentation, and relapsing disease. Mortality in the first year remains at 5-10%, primarily from infection and uncontrolled vasculitis.

### 2.3 Aetiology

The aetiology of AAV is multifactorial, involving genetic predisposition, environmental triggers, and dysregulated immune responses. Genome-wide association studies have identified strong associations with the major histocompatibility complex (MHC) region, particularly HLA-DPB1 for PR3-ANCA and HLA-DQ for MPO-ANCA. Non-MHC susceptibility loci include SERPINA1 (alpha-1 antitrypsin deficiency, a natural inhibitor of PR3), PRTN3 (encoding PR3), and PTPN22 (involved in T-cell receptor signalling). These genetic associations are serotype-specific, supporting the concept that PR3-AAV and MPO-AAV are distinct genetic diseases.

Environmental triggers include silica exposure, which carries an odds ratio of 2.5-4.0 for AAV development. Other reported triggers include bacterial infections (particularly Staphylococcus aureus in GPA), medications (propylthiouracil, hydralazine, allopurinol, levamisole-adulterated cocaine), and seasonality patterns suggesting infectious triggers. Drug-induced ANCA-associated vasculitis typically produces MPO-ANCA and is associated with higher rates of drug-induced lupus features. The latency period from drug exposure to disease onset varies from weeks to years.

Molecular mimicry between microbial antigens and ANCA target antigens has been proposed. Chronic nasal carriage of Staphylococcus aureus in GPA patients is associated with a higher risk of relapse. The complement system, particularly the alternative pathway, has emerged as a critical aetiological factor, with C5a-C5aR interaction being essential for neutrophil activation.

### 2.4 Pathophysiology

The pathophysiology of ANCA-associated vasculitis follows a multi-step cascade beginning with neutrophil priming, followed by ANCA-mediated neutrophil activation, endothelial injury, and crescent formation. This cascade represents the core mechanism through which a loss of immune tolerance to PR3 and MPO results in systemic small-vessel destruction.

Step 1 — Neutrophil Priming: Pro-inflammatory cytokines (TNF-alpha, IL-1, IL-6) from subclinical infection or other inflammatory stimuli prime circulating neutrophils. Priming causes translocation of cytoplasmic PR3 and MPO to the cell surface, making these antigens accessible to circulating ANCA. Cytokine priming also upregulates neutrophil adhesion molecules and activates the respiratory burst machinery. TNF-alpha is the most potent priming agent identified in vitro.

Step 2 — ANCA Binding and Neutrophil Activation: Circulating ANCA binds to surface-expressed PR3 or MPO on primed neutrophils. Cross-linking of ANCA with Fc-gamma receptors (FcgammaRIIa and FcgammaRIIIb) and Fab-mediated antigen binding triggers full neutrophil activation. Activated neutrophils undergo a respiratory burst with production of reactive oxygen species (ROS), degranulation releasing proteolytic enzymes (including PR3 and MPO themselves), and formation of neutrophil extracellular traps (NETosis). NETosis exposes nuclear and granular antigens, amplifying the autoimmune response through epitope spreading.

Step 3 — Endothelial Injury: Activated, degranulating neutrophils adhere to and migrate through the endothelium. Released ROS and proteolytic enzymes cause direct endothelial injury, leading to increased vascular permeability, fibrinoid necrosis, and exposure of the basement membrane. Damaged endothelial cells express adhesion molecules (E-selectin, ICAM-1) that recruit additional inflammatory cells. The resulting inflammation is necrotising rather than granulomatous in the glomerular microvasculature.

Step 4 — Crescent Formation: Fibrin and cellular debris from necrotising glomerular capillary loops leak into Bowman space. Circulating monocytes and macrophages infiltrate the urinary space and transform into epithelioid cells. Parietal epithelial cells proliferate. Together these cells form crescents — extracapillary cellular proliferations that compress the glomerular tuft. Cellular crescents may evolve into fibrocellular and ultimately fibrous crescents if the inflammatory process is not arrested by treatment. The proportion of cellular versus fibrous crescents carries prognostic significance.

Step 5 — Alternative Complement Pathway Activation: The alternative complement pathway plays a critical amplifying role. Neutrophil degranulation releases factors that activate C3 convertase, generating C3a and C5a. C5a binds to C5a receptor (C5aR, CD88) on neutrophils, providing a potent priming and activation signal that amplifies the ANCA-mediated response. This C5a-C5aR amplification loop is the rationale for C5aR antagonism (avacopan) in AAV treatment. Complement deposition in AAV is typically scant (pauci-immune) but C3d and complement activation products are detectable in the circulation and urine.

Step 6 — T-Cell Involvement: Both CD4+ and CD8+ T cells contribute to AAV pathogenesis. CD4+ T cells show aberrant cytokine profiles with Th1, Th2, and Th17 skewing described in different disease phases. Regulatory T-cell (Treg) numbers and function are impaired. CD8+ T cells contribute to endothelial injury and are expanded in active disease. T-cell involvement explains the efficacy of T-cell-directed therapies such as cyclophosphamide and the potential benefit of mycophenolate mofetil.

Step 7 — B-Cell and Autoantibody Amplification: B cells contribute to AAV through ANCA production, antigen presentation, and cytokine secretion. ANCA production by plasma cells is CD20-negative and therefore not directly targeted by rituximab, which deletes CD20-positive B-cell precursors. The repopulation of B cells following rituximab therapy is associated with clinical relapse, and monitoring of B-cell reconstitution informs retreatment decisions. Memory B cells capable of differentiating into ANCA-producing plasma cells persist long after initial therapy.

### 2.5 Clinical Presentation

| Presentation | Frequency | Description |
|-------------|-----------|-------------|
| Rapidly progressive GN | 50–70% | Oliguric AKI, active urinary sediment, hypertension, oedema |
| Pulmonary manifestations | 40–60% | Pulmonary nodules (GPA), alveolar haemorrhage (DAH), infiltrates, pleural effusion |
| ENT involvement | 70–80% (GPA) | Crusting rhinitis, sinusitis, epistaxis, saddle-nose deformity, otitis media, subglottic stenosis |
| Cutaneous involvement | 30–50% | Palpable purpura, ulcers, digital ischaemia, livedo reticularis |
| Neurologic involvement | 20–30% | Mononeuritis multiplex, peripheral neuropathy, cranial nerve palsies |
| Musculoskeletal | 50–70% | Arthralgias, myalgias, frank arthritis (non-deforming) |
| Constitutional symptoms | 80–90% | Fever, weight loss, night sweats, fatigue, malaise |
| Ocular involvement | 15–20% | Scleritis, episcleritis, orbital pseudotumour (GPA), uveitis |
| Gastrointestinal | 10–20% | Abdominal pain, GI bleeding, perforation |

RPGN presents with oliguric or anuric acute kidney injury, hypertension, oedema, and active urinary sediment (dysmorphic RBCs, RBC casts). Serum creatinine rises rapidly over days to weeks. The severity ranges from subclinical haematuria to dialysis-dependent renal failure. Pulmonary-renal syndrome (DAH with GN) occurs in approximately 15-20% of patients and represents a medical emergency requiring immediate PLEX consideration. The distinction between GPA and MPA remains clinically important: GPA typically features granulomatous ENT and pulmonary involvement with PR3-ANCA, while MPA more commonly presents with renal-limited disease and MPO-ANCA.

### 2.6 Diagnostic Criteria

| Criterion | Description | Strength |
|-----------|-------------|----------|
| Clinical syndrome | GPA, MPA, or EGPA phenotype | Core |
| ANCA serology | Positive PR3/c-ANCA or MPO/p-ANCA by immunoassay and/or IIF | Core |
| Renal biopsy | Necrotising crescentic GN with pauci-immune IF | Gold standard |
| Extrarenal biopsy | Necrotising vasculitis or granulomatous inflammation | Supportive |
| ENT involvement (GPA) | Nasal crusting, sinusitis, saddle-nose, subglottic stenosis | GPA-specific |
| Pulmonary involvement | Nodules, cavities, infiltrates, DAH | Supportive |
| Eosinophilia (EGPA) | Peripheral eosinophilia >1500/uL with asthma | EGPA-specific |
| RPGN presentation | Rapid decline in eGFR over days-weeks with active sediment | High suspicion |

### 2.7 Differential Diagnosis

| Condition | Key Distinguishing Feature |
|-----------|---------------------------|
| Anti-GBM disease | Linear IgG staining on IF; positive anti-GBM antibodies |
| Lupus nephritis | Full-house IF pattern; positive ANA, anti-dsDNA; low C3/C4 |
| IgA nephropathy/Henoch-Schonlein purpura | Dominant IgA deposition on IF |
| Cryoglobulinaemic GN | Cryoglobulins; IgG/IgM/IC deposition; hepatitis C association |
| Infective endocarditis-associated GN | Positive blood cultures; valvular vegetations; low complement |
| Thrombotic microangiopathy | Thrombocytopenia, microangiopathic haemolytic anaemia |
| Atheroembolic disease | Cholesterol clefts on biopsy; peripheral eosinophilia possible |

### 2.8 Laboratory Findings

| Test | Typical Finding | Utility |
|------|-----------------|---------|
| Serum creatinine | Elevated (1.5–10 mg/dL) | Renal function assessment |
| eGFR | Reduced (<60 mL/min/1.73m2) | Staging CKD |
| Urinalysis | Dysmorphic RBCs, RBC casts | Active GN |
| UPCR | 0.5–5.0 g/g | Proteinuria quantification |
| PR3-ANCA | Positive (ELISA/CIA) | GPA serotype |
| MPO-ANCA | Positive (ELISA/CIA) | MPA serotype |
| c-ANCA (IIF) | Cytoplasmic pattern | Screening |
| p-ANCA (IIF) | Perinuclear pattern | Screening |
| CRP | Elevated >50 mg/dL | Disease activity marker |
| ESR | Elevated >50 mm/hr | Non-specific inflammatory marker |
| Haemoglobin | Low (8–11 g/dL) | Anaemia of chronic disease vs DAH |
| Albumin | Low (2.5–3.5 g/dL) | Inflammation, proteinuria |

### 2.9 Biopsy Findings

| Modality | Finding | Significance |
|----------|---------|--------------|
| Light microscopy | Necrotising crescentic GN; fibrinoid necrosis | Diagnostic hallmark |
| Glomerular involvement | Focal (50%) vs diffuse; cellular vs fibrous crescents | Prognostic |
| Tubulointerstitial | Interstitial inflammation, fibrosis, tubular atrophy | Chronicity marker |
| Immunofluorescence | Pauci-immune (no or scant Ig/complement) | Differentiates from IC-mediated GN |
| Arterial involvement | Necrotising arteritis in larger vessels | Systemic involvement |
| Chronicity score | Interstitial fibrosis/tubular atrophy | ESKD risk prediction |
| Crescents | Cellular > fibrocellular > fibrous | Activity and chronicity |
| Normal glomeruli | Proportion of unaffected glomeruli | Recovery potential |

### 2.10 Classification Systems

| System | Categories | Utility |
|--------|------------|---------|
| CHCC 2012 | GPA, MPA, EGPA | Nomenclature standardisation |
| Berden classification | Focal, Crescentic, Mixed, Sclerotic | Histological prognostic classification |
| Brix classification | Five-tier chronicity score | Chronicity assessment |
| EUVAS definitions | Newly diagnosed, relapsing, refractory | Treatment context |
| Five Factor Score (EGPA) | Age, cardiac, GI, renal, ENT | Prognostic in EGPA |
| Birmingham Vasculitis Activity Score | Disease activity assessment | Clinical trial endpoint |

### 2.11 Risk Stratification

| Factor | Risk Level | Impact |
|--------|------------|--------|
| Serum creatinine at diagnosis | >4 mg/dL | 5x ESKD risk |
| Age at onset | >65 years | Higher treatment toxicity |
| Dialysis dependence at presentation | Yes | 50% recover independent function |
| Berden sclerotic class | >50% sclerotic | Poor renal recovery |
| Brix chronicity score | High (3-5) | Irreversible damage |
| PR3 serotype vs MPO | PR3: higher relapse risk | Treatment duration |
| Pulmonary haemorrhage | Present | 15-20% mortality |
| Delay in diagnosis | >3 months | Worse renal outcomes |

### 2.12 Treatment Overview

ANCA-associated vasculitis treatment follows an induction-remission-maintenance paradigm. For induction of severe/active disease, the standard of care is either rituximab (375 mg/m2 weekly x 4) or cyclophosphamide (oral 2 mg/kg/day or IV pulse 15 mg/kg q3-4 weeks) combined with high-dose glucocorticoids (typically methylprednisolone 1 g/day x 3 pulses then prednisone 1 mg/kg/day taper). For life-threatening disease with RPGN requiring dialysis or DAH, plasma exchange (PLEX) may be added, though the PEXIVAS trial showed no benefit for renal outcomes in the overall population; PLEX remains reserved for severe presentations with double-positive ANCA/anti-GBM or severe DAH with hypoxaemia.

Avacopan, a C5a receptor antagonist, was approved based on the ADVOCATE trial showing non-inferiority to prednisone for remission and superiority for sustained remission at 52 weeks, with significant steroid-sparing effects. It represents a paradigm shift from glucocorticoid-dominant to targeted complement inhibition.

Maintenance therapy following remission includes rituximab (500 mg q6mo for 18-24 months) or azathioprine (2 mg/kg/day) with low-dose prednisone. The MAINRITSAN and RITAZAREM trials established rituximab superiority over azathioprine for relapse prevention. TMP-SMX is indicated for Pneumocystis jirovecii prophylaxis during induction and for the duration of immunosuppressive therapy.

### 2.13 Treatment Algorithms

| Step | Regimen | Indication |
|------|---------|------------|
| 1 | Methylprednisolone 1 g IV x 3 pulses | Severe/RPGN/DAH |
| 2 | Rituximab 375 mg/m2 weekly x 4 | First-line induction (preferred) |
| 2a | Cyclophosphamide IV pulse 15 mg/kg q3-4wk x 3-6 | Alternative induction (resource-limited) |
| 3 | PLEX 7 sessions over 14 days | Severe DAH or double-positive |
| 4 | Avacopan 30 mg BID x 52 weeks | Steroid-sparing induction |  
| 5 | Prednisone taper over 12-20 weeks | Standard induction taper |
| 6 | Rituximab 500 mg q6mo x 4 doses | Maintenance |
| 6a | Azathioprine 2 mg/kg/day + pred 5-10 mg/day | Alternative maintenance |
| 7 | TMP-SMX 800/160 mg daily or 3x/week | PJP prophylaxis |

### 2.14 Monitoring Protocol

Visits occur weekly during induction, monthly during months 2-6, then every 3 months during months 6-24, and every 6 months thereafter. At each visit, clinical assessment (BVAS), serum creatinine/eGFR, urinalysis with RBC cast quantification, UPCR, inflammatory markers (CRP, ESR), and ANCA titre monitoring (q3mo) are performed. Drug-specific monitoring includes CD19+ B-cell counts and immunoglobulin levels for rituximab, complete blood counts for cyclophosphamide and azathioprine, liver function tests for azathioprine, and avacopan tolerability assessment. Steroid toxicity monitoring includes blood pressure, fasting glucose, bone density, and ophthalmologic exams at baseline and annually. Patients on chronic immunosuppression require skin cancer surveillance and age-appropriate cancer screening.

### 2.15 Complications

| Complication | Frequency | Prevention/Management |
|-------------|-----------|----------------------|
| Infection (severe) | 20-30% | TMP-SMX PJP prophylaxis; vaccination; IG monitoring |
| Steroid toxicity | 30-50% | Avacopan for steroid-sparing; osteoporosis prophylaxis |
| Cyclophosphamide cystitis | 5-15% | Mesna; adequate hydration; limit cumulative dose |
| Cyclophosphamide malignancy | 2-5% | Lifetime cancer screening; limit to 6 months |
| Rituximab infusion reaction | 5-10% | Premedication; slow infusion |
| Progressive CKD | 20-35% | RAAS blockade; SGLT2 inhibition; BP control |
| Relapse | 30-50% at 5 years | Rituximab maintenance; ANCA monitoring |
| Avacopan hepatic toxicity | 3-5% | LFT monitoring monthly x 6, then q3mo |
| Cardiovascular events | 15-25% | BP control; lipid management; antiplatelet therapy |

### 2.16 Relapse Information

Relapse rates in AAV remain substantial at 30-50% within 5 years despite maintenance therapy. PR3-ANCA serotype carries approximately 1.5-2x the relapse risk of MPO-ANCA. Other risk factors include history of prior relapse, longer time to initial remission, ENT involvement (particularly persistent Staphylococcus aureus carriage in GPA), rapid ANCA titre rise (particularly PR3-ANCA), and B-cell reconstitution after rituximab. Relapses are classified as major (life- or organ-threatening) or minor. Major relapse, involving new or worsening renal, pulmonary, or other critical organ involvement, requires re-induction typically with rituximab. Minor relapse may be managed with optimisation of maintenance therapy, corticosteroid dose adjustment, or reinstitution of previously effective agents. Avacopan has demonstrated efficacy in reducing relapse risk when used for sustained complement inhibition.

### 2.17 Long-Term Prognosis

The prognosis of AAV has improved dramatically from the pre-immunosuppression era (one-year mortality >80%) to the modern era (5-year patient survival 75-85%). Renal outcomes depend critically on the renal chronicity at diagnosis. Patients with Berden focal class (50% normal glomeruli) have excellent renal prognosis (5-year renal survival >90%), while those with sclerotic class (50% globally sclerotic glomeruli) have poor renal prognosis (5-year renal survival <25%). Crescentic and mixed classes have intermediate outcomes. ESKD risk factors include dialysis dependence at presentation, high chronicity scores on biopsy, poor response to induction therapy, and relapsing disease. Post-transplant outcomes are excellent, with patient and graft survival rates comparable to other causes of ESKD, though with a 10-20% recurrence risk particularly for PR3-ANCA. Cardiovascular disease becomes the leading cause of late mortality in patients who achieve renal remission.

### 2.18 Evidence Summary

The RAVE trial (NEJM 2010) established rituximab as non-inferior to cyclophosphamide for induction of remission in AAV, with superiority in relapsing disease. PEXIVAS (NEJM 2020) demonstrated no benefit of PLEX for renal outcomes and non-inferiority of a reduced-dose glucocorticoid regimen, transforming steroid practices. MAINRITSAN (NEJM 2014) established rituximab 500 mg q6mo as superior to azathioprine for maintenance of remission. RITAZAREM (Lancet 2020) confirmed rituximab superiority in relapsing patients. ADVOCATE (NEJM 2021) demonstrated avacopan non-inferiority to prednisone for remission and superiority at 52 weeks with marked steroid reduction. CYCLOPS (KI 2009) showed IV pulse cyclophosphamide equivalent to oral for induction with reduced cumulative dose. MEPEX (JASN 2007) established PLEX benefit for dialysis-dependent patients before PEXIVAS.

### 2.19 Guideline Recommendations

| Guideline | Year | Key Recommendations |
|-----------|------|---------------------|
| KDIGO 2021 Ch 8 | 2021 | Rituximab or CyP induction; PLEX conditional |
| KDIGO 2024 update | 2024 | Avacopan as induction adjunct |
| EULAR/ERA-EDTA | 2016 | Induction; maintenance recommendations |
| EULAR 2024 update | 2024 | Avacopan integration; steroid-minimising |
| ACR/VF 2021 | 2021 | Rituximab preferred over CyP |
| BSR | 2014 | UK-specific protocols |
| Canadian Vasc | 2020 | Consensus guidelines |

### 2.20 Key References

| Reference | Citation | Key Finding |
|-----------|----------|-------------|
| RAVE | Stone et al. NEJM 2010;363(3):211-20 | Rituximab non-inferior to CyP |
| PEXIVAS | Walsh et al. NEJM 2020;382(7):622-31 | PLEX no benefit; reduced steroids |
| MAINRITSAN | Guillevin et al. NEJM 2014;371(19):1771-80 | Rituximab superior for maintenance |
| RITAZAREM | Gopaluni et al. Lancet 2020;396(10243):73-83 | Rituximab for relapsing disease |
| ADVOCATE | Jayne et al. NEJM 2021;384(7):599-609 | Avacopan steroid-sparing |
| CYCLOPS | de Groot et al. KI 2009;75(10):1108-16 | IV vs oral CyP equivalence |
| MEPEX | Jayne et al. JASN 2007;18(7):2180-8 | PLEX in severe disease |
| EUVAS classification | Berden et al. JASN 2010;21(10):1628-36 | Histological classification |
| ANCA genetics | Lyons et al. NEJM 2012;367(3):214-23 | Genetic serotype associations |
| Ridley et al. KI 2023 | Ridley et al. KI 2023;103(1):112-24 | Avacopan real-world outcomes |
| Kronbichler et al. Nat Rev 2024 | Kronbichler et al. Nat Rev Nephrol 2024;20(1):7-20 | Comprehensive AAV review |

### 2.21 Notes

This knowledge specification is intended for clinical decision support in ANCA-associated vasculitis with renal involvement. Key clinical pearls include: (1) ANCA serotype (PR3 vs MPO) dictates relapse risk and genetic associations more than clinical syndrome; (2) renal biopsy chronicity is the single most important predictor of renal recovery; (3) avacopan should replace prolonged steroid courses in appropriately selected patients; (4) PLEX remains appropriate for severe DAH with hypoxaemia and for anti-GBM double-positive patients; (5) rituximab is superior to azathioprine for maintenance, especially in PR3-AAV; (6) TMP-SMX prophylaxis is mandatory during induction; (7) infection is the leading cause of death in the first year; (8) cardiovascular disease is the leading cause of late mortality.

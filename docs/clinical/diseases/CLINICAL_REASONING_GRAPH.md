# Clinical Reasoning Graph
**Document ID:** GDES-V4.2-GRAPH-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Cross-Disease Knowledge Graph

---

## 1. Graph Architecture Overview

GDES V4.1 organized knowledge as isolated disease modules. V4.2 transforms this into an interconnected clinical reasoning knowledge graph where every node is a reusable knowledge object and every edge represents a clinical relationship.

### 1.1 Graph Philosophy

```
Patient Presentation
        ↓
   Syndrome Identification
        ↓
   Differential Generation
        ↓
   Evidence Weighting
        ↓
   Diagnosis Ranking
        ↓
   Treatment Selection
        ↓
   Monitoring Plan
```

### 1.2 Core Design Principles

| Principle | Description |
|---|---|
| **Reusability** | Each knowledge object (syndrome, pathology, lab, drug, monitoring, complication) is a standalone node linked to multiple diseases |
| **Traceability** | Every edge carries provenance: guideline source, evidence grade, author, timestamp |
| **Weighted Evidence** | Edge weights represent diagnostic/therapeutic strength (0.0-1.0) |
| **Explainability** | Every recommendation traces back through traversed edges and contributing nodes |
| **Bidirectional** | Relationships are traversable in both directions (disease→drug and drug→disease) |
| **Temporal** | Edges have effective/retired dates for guideline versioning |

---

## 2. Node Types and Catalog

### 2.1 Clinical Syndrome Nodes (16)

| Node ID | Name | Source Document | Key Properties |
|---|---|---|---|
| `SYND-NS` | Nephrotic Syndrome | CLINICAL_SYNDROME_LIBRARY.md | definition, diagnostic_criteria, common_causes[], rare_causes[], clinical_clues[], lab_clues[], biopsy_clues[], investigations[], immediate_management[], long_term_eval[], linked_diseases[] |
| `SYND-NT` | Nephritic Syndrome | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-RPGN` | Rapidly Progressive GN | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-ASH` | Asymptomatic Hematuria | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-IP` | Isolated Proteinuria | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-AKI` | Acute Kidney Injury (Nephrology) | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-CKD` | Chronic Kidney Disease | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-HTN` | Hypertension with Urinary Abnormalities | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-VAS` | Systemic Vasculitis (Renal) | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-PRS` | Pulmonary-Renal Syndrome | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-PREG` | Pregnancy-Associated Glomerular Disease | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-TX` | Post-Transplant Renal Dysfunction | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-MH` | Macroscopic Hematuria | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-CMG` | Complement-Mediated Glomerular Disease | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-TMA` | Thrombotic Microangiopathy | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |
| `SYND-NRRD` | Nephrotic-Range Proteinuria with Rapid Decline | CLINICAL_SYNDROME_LIBRARY.md | (same structure) |

### 2.2 Disease Nodes (23)

| Node ID | Name | Category | Source |
|---|---|---|---|
| `iga` | IgA Nephropathy / IgA Vasculitis | PRIMARY | Disease model |
| `anca` | ANCA Vasculitis | PRIMARY | Disease model |
| `antiGbm` | Anti-GBM Disease | PRIMARY | Disease model |
| `c3` | C3 Glomerulopathy | PRIMARY | Disease model |
| `cryoglobulinemic` | Cryoglobulinemic GN | SECONDARY | Disease model |
| `denseDepositDisease` | Dense Deposit Disease | PRIMARY | Disease model |
| `diabeticNephropathy` | Diabetic Kidney Disease | SECONDARY | Disease model |
| `drugInducedGn` | Drug-Induced GN | SECONDARY | Disease model |
| `fibrillaryGlomerulonephritis` | Fibrillary GN | PRIMARY | Disease model |
| `fsgs` | FSGS | PRIMARY | Disease model |
| `hivan` | HIV-Associated Nephropathy | SECONDARY | Disease model |
| `irgn` | Infection-Related GN | SECONDARY | Disease model |
| `lupus` | Lupus Nephritis | SECONDARY | Disease model |
| `mcd` | Minimal Change Disease | PRIMARY | Disease model |
| `membranous` | Membranous Nephropathy | PRIMARY | Disease model |
| `mpgn` | MPGN | PRIMARY | Disease model |
| `thinBasementMembrane` | Thin Basement Membrane Disease | HEREDITARY | Disease model |
| `alport` | Alport Syndrome | HEREDITARY | Disease model |
| `antibodyMediatedRejection` | Antibody-Mediated Rejection | TRANSPLANT | Disease model |
| `tCellMediatedRejection` | T-Cell Mediated Rejection | TRANSPLANT | Disease model |
| `bkVirusNephropathy` | BK Virus Nephropathy | TRANSPLANT | Disease model |
| `cniToxicity` | CNI Nephrotoxicity | TRANSPLANT | Disease model |
| `transplantGlomerulopathy` | Transplant Glomerulopathy | TRANSPLANT | Disease model |

Each disease node carries: 21 fields from the Disease model, linked KB rules, pathways, cases.

### 2.3 Pathology Entity Nodes (37)

| Category | Nodes (Count) | Source Document |
|---|---|---|
| Light Microscopy | Mesangial proliferation (LM-01), Endocapillary hypercellularity (LM-02), Crescents (LM-03), Segmental sclerosis (LM-04), Global sclerosis (LM-05), Focal necrosis (LM-06), GBM duplication (LM-07), MPGN pattern (LM-08), Mesangiolysis (LM-09), TMA pattern (LM-10), IFTA (LM-11), ATI (LM-12), Interstitial nephritis (LM-13), Arteriolar hyalinosis (LM-14), Vascular intimal fibrosis (LM-15) | PATHOLOGY_KNOWLEDGE_LIBRARY.md |
| Immunofluorescence | IgA dominant mesangial (IF-01), Full-house (IF-02), C3 dominant (IF-03), C1q deposits (IF-04), Linear IgG GBM (IF-05), Fibrinogen crescents (IF-06), C4d PTC (IF-07), Light chain restriction (IF-08) | PATHOLOGY_KNOWLEDGE_LIBRARY.md |
| Electron Microscopy | Foot process effacement (EM-01), Subepithelial deposits (EM-02), Subendothelial deposits (EM-03), Mesangial deposits (EM-04), Intramembranous deposits (EM-05), GBM thinning (EM-06), GBM lamellation (EM-07), Tubuloreticular inclusions (EM-08), Endothelial swelling TMA (EM-09), Fibrillary deposits (EM-10), Microtubular deposits (EM-11), Immunotactoid deposits (EM-12), Organized deposits (EM-13), Podocyte microvilli (EM-14) | PATHOLOGY_KNOWLEDGE_LIBRARY.md |

### 2.4 Laboratory Entity Nodes (61)

| Category | Nodes (Count) | Source Document |
|---|---|---|
| Urinalysis | Proteinuria, Hematuria, Dysmorphic RBCs, RBC casts, WBC casts, Oval fat bodies, Lipiduria | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Renal Function | Creatinine, eGFR (CKD-EPI/MDRD/Schwartz), BUN, Cystatin C, Creatinine clearance | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Serum Chemistries | Albumin, Total protein, SPEP, Free light chains, Kappa/lambda ratio | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Complement | C3, C4, CH50, C5b-9, C3NeF, Anti-Factor H, Anti-Factor B, Properdin | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Autoantibodies | ANA, Anti-dsDNA, ANCA (PR3/MPO), Anti-GBM, Anti-PLA2R, Anti-THSD7A, Anti-C1q, APS panel, RF, Cryoglobulins, Anti-dsDNA, Anti-Sm/Ro/La/RNP | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Immunology | Immunoglobulins (IgG/IgA/IgM/IgE), IgG subclasses | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Infectious Serology | HBV, HCV, HIV, Syphilis, EBV, CMV, BK virus, Parvovirus, Malaria, Schistosoma, Leptospira, SARS-CoV-2 | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Hematology | Hb, Platelets, Smear (schistocytes), Coagulation, ADAMTS13, Factor H/I/MCP | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Urine Biomarkers | UPEP, Urine immunofixation, Urine eosinophils | LABORATORY_KNOWLEDGE_LIBRARY.md |

### 2.5 Drug Entity Nodes (50+)

| Drug Class | Representative Nodes | Source Document |
|---|---|---|
| RAAS Inhibitors | Ramipril, Lisinopril, Losartan, Valsartan, Telmisartan, Irbesartan, Candesartan, Eplerenone, Spironolactone | DRUG_INTELLIGENCE_LIBRARY.md |
| SGLT2 Inhibitors | Dapagliflozin, Empagliflozin, Canagliflozin | DRUG_INTELLIGENCE_LIBRARY.md |
| Corticosteroids | Methylprednisolone (IV), Prednisolone (oral), Budesonide (Nefecon) | DRUG_INTELLIGENCE_LIBRARY.md |
| Calcineurin Inhibitors | Tacrolimus, Cyclosporine | DRUG_INTELLIGENCE_LIBRARY.md |
| Antimetabolites | MMF, MPA, Azathioprine | DRUG_INTELLIGENCE_LIBRARY.md |
| Alkylating Agents | Cyclophosphamide | DRUG_INTELLIGENCE_LIBRARY.md |
| Biologics | Rituximab, Belimumab, Eculizumab, Ravulizumab, Tocilizumab, Belatacept, Abatacept | DRUG_INTELLIGENCE_LIBRARY.md |
| Complement Inhibitors | Iptacopan, Avacopan, Narsoplimab | DRUG_INTELLIGENCE_LIBRARY.md |
| mTOR Inhibitors | Sirolimus, Everolimus | DRUG_INTELLIGENCE_LIBRARY.md |
| Cardiovascular | Atorvastatin, Rosuvastatin, Furosemide, HCTZ, Amlodipine, Doxazosin | DRUG_INTELLIGENCE_LIBRARY.md |
| Anticoagulants | Warfarin, Heparin, LMWH, Apixaban | DRUG_INTELLIGENCE_LIBRARY.md |
| Supportive | Sodium bicarbonate, Allopurinol, Febuxostat, ESA, Iron, Phosphate binders, Vit D analogs | DRUG_INTELLIGENCE_LIBRARY.md |
| Antimicrobials (Tx) | Valganciclovir, Valacyclovir, TMP-SMX, Fluconazole, Nystatin | DRUG_INTELLIGENCE_LIBRARY.md |
| Other IS | IVIG, PLEX, Bortezomib, Carfilzomib | DRUG_INTELLIGENCE_LIBRARY.md |

### 2.6 Monitoring Protocol Nodes (20+)

| Protocol ID | Target | Source Document |
|---|---|---|
| `MON-ACEi` | RAS Inhibitor Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-SGLT2` | SGLT2 Inhibitor Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-PRED` | Corticosteroid Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-IVMP` | IV Methylprednisolone Pulse Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-CYC` | Cyclophosphamide Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-MMF` | MMF Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-AZA` | Azathioprine Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-TAC` | Tacrolimus Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-CSA` | Cyclosporine Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-RTX` | Rituximab Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-BELI` | Belimumab Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-ECU` | Eculizumab/Ravulizumab Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-AVA` | Avacopan Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-IPT` | Iptacopan Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-mTOR` | mTOR Inhibitor Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-IVIG` | IVIG Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-PLEX` | Plasmapheresis Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-BORT` | Bortezomib Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-BELA` | Belatacept Monitoring | MONITORING_PROTOCOL_LIBRARY.md |
| `MON-HCQ` | Hydroxychloroquine Monitoring | MONITORING_PROTOCOL_LIBRARY.md |

### 2.7 Complication Nodes (24)

| Complication ID | Name | Source Document |
|---|---|---|
| `COMP-INF` | Infection (bacterial/viral/fungal/PJP/TB/opportunistic) | COMPLICATION_LIBRARY.md |
| `COMP-THROMB` | Thrombosis (DVT/PE/RVT/AVF) | COMPLICATION_LIBRARY.md |
| `COMP-VTE` | VTE in Nephrotic Syndrome | COMPLICATION_LIBRARY.md |
| `COMP-AKI` | Acute Kidney Injury | COMPLICATION_LIBRARY.md |
| `COMP-CKD` | CKD Progression | COMPLICATION_LIBRARY.md |
| `COMP-HTN` | Hypertension | COMPLICATION_LIBRARY.md |
| `COMP-HK` | Hyperkalemia | COMPLICATION_LIBRARY.md |
| `COMP-MA` | Metabolic Acidosis | COMPLICATION_LIBRARY.md |
| `COMP-OST` | Osteoporosis/Renal Bone Disease | COMPLICATION_LIBRARY.md |
| `COMP-INFERT` | Infertility | COMPLICATION_LIBRARY.md |
| `COMP-MALIG` | Malignancy (PTLD/bladder/skin/MALT) | COMPLICATION_LIBRARY.md |
| `COMP-CVD` | Cardiovascular Disease | COMPLICATION_LIBRARY.md |
| `COMP-NS` | Nephrotic Syndrome Complications | COMPLICATION_LIBRARY.md |
| `COMP-HC` | Hemorrhagic Cystitis | COMPLICATION_LIBRARY.md |
| `COMP-PRES` | PRES | COMPLICATION_LIBRARY.md |
| `COMP-NODAT` | NODAT | COMPLICATION_LIBRARY.md |
| `COMP-AVN` | Avascular Necrosis | COMPLICATION_LIBRARY.md |
| `COMP-IR` | Infusion Reactions | COMPLICATION_LIBRARY.md |
| `COMP-PML` | PML | COMPLICATION_LIBRARY.md |
| `COMP-TB` | TB Reactivation | COMPLICATION_LIBRARY.md |
| `COMP-HBV` | Hepatitis B Reactivation | COMPLICATION_LIBRARY.md |
| `COMP-CYTO` | Cytopenias | COMPLICATION_LIBRARY.md |
| `COMP-GI` | GI Toxicity | COMPLICATION_LIBRARY.md |
| `COMP-AIN` | Drug-Induced Interstitial Nephritis | COMPLICATION_LIBRARY.md |

### 2.8 Guideline Nodes (14+)

| Guideline ID | Organization | Title | Year | Source Document |
|---|---|---|---|---|
| `GS-KDIGO-2021-GN` | KDIGO | Clinical Practice Guideline for Glomerular Diseases | 2021 | GUIDELINE_HARMONIZATION.md |
| `GS-KDIGO-2021-BP` | KDIGO | Blood Pressure in CKD | 2021 | GUIDELINE_HARMONIZATION.md |
| `GS-KDIGO-2021-AKI` | KDIGO | AKI Guideline | 2021 | GUIDELINE_HARMONIZATION.md |
| `GS-KDIGO-2024-CKD` | KDIGO | CKD Evaluation and Management | 2024 | GUIDELINE_HARMONIZATION.md |
| `GS-KDIGO-2024-DM` | KDIGO | Diabetes Management in CKD | 2024 | GUIDELINE_HARMONIZATION.md |
| `GS-KDIGO-2024-TX` | KDIGO | Transplant Recipient Guideline | 2024 | GUIDELINE_HARMONIZATION.md |
| `GS-ERA-2022` | ERA | Glomerular Disease Recommendations | 2022 | GUIDELINE_HARMONIZATION.md |
| `GS-ERA-2024-IGAN` | ERA | IgAN Position Paper | 2024 | GUIDELINE_HARMONIZATION.md |
| `GS-ERA-EDTA-2023` | ERA-EDTA | Nephrology Guidelines | 2023 | GUIDELINE_HARMONIZATION.md |
| `GS-ISN-2023` | ISN | Glomerular Disease Classification Update | 2023 | GUIDELINE_HARMONIZATION.md |
| `GS-ISN-2024` | ISN | Renal Pathology Consensus | 2024 | GUIDELINE_HARMONIZATION.md |
| `GS-ASN-2023` | ASN | Kidney Health Guidelines | 2023 | GUIDELINE_HARMONIZATION.md |
| `GS-KDOQI-2023` | KDOQI | CKD Nutrition Guideline | 2023 | GUIDELINE_HARMONIZATION.md |
| `GS-KDOQI-2024` | KDOQI | Vascular Access Guideline | 2024 | GUIDELINE_HARMONIZATION.md |

---

## 3. Edge Types and Catalog

### 3.1 Edge Type Definitions

| Edge Type | Direction | Description | Weight Range | Properties |
|---|---|---|---|---|
| `presents_as` | Syndrome → Disease | Disease manifests as this syndrome | 0.3-1.0 | frequency, acuity, population |
| `causes` | Disease → Syndrome | Disease is a cause of this syndrome | 0.2-1.0 | evidence_grade, guideline_source |
| `diagnosed_by` | Disease → Lab/Pathology | Finding supports diagnosis | 0.1-1.0 | sensitivity, specificity, LR+ |
| `argues_against` | Disease → Lab/Pathology | Finding argues against diagnosis | 0.1-1.0 | specificity, LR- |
| `treated_with` | Disease → Drug | Drug treats this disease | 0.3-1.0 | line_of_therapy, evidence_grade, guideline_source |
| `contraindicated_in` | Drug → Disease | Drug contraindicated in this disease | 0.5-1.0 | reason, severity |
| `monitored_by` | Disease → MonitoringProtocol | Protocol applies to this disease | 0.5-1.0 | frequency, parameters |
| `monitors` | Drug → MonitoringProtocol | Protocol monitors this drug | 0.5-1.0 | parameters, schedule |
| `complicated_by` | Disease → Complication | Disease risks this complication | 0.1-0.9 | frequency, risk_factors |
| `caused_by` | Complication → Drug | Drug causes this complication | 0.1-0.8 | mechanism, risk_level |
| `recommended_by` | Action → Guideline | Guideline recommends this action | 0.5-1.0 | strength, evidence_grade |
| `evidence_for` | Rule → EvidenceEntry | Evidence supports this KB rule | 0.5-1.0 | evidence_level, citation |
| `part_of` | Syndrome → Syndrome | Sub-syndrome relationship | 0.5-1.0 | hierarchy |
| `overlaps_with` | Disease ↔ Disease | Overlap/differential relationship | 0.2-0.7 | clinical_context |

### 3.2 Edge Property Standards

Every edge MUST carry:
```json
{
  "weight": 0.0-1.0,
  "evidence_grade": "1A|1B|2A|2B|2C|2D|OP|NG",
  "guideline_source": "GS-ID",
  "author": "author_id",
  "created_date": "YYYY-MM-DD",
  "effective_date": "YYYY-MM-DD",
  "retired_date": "YYYY-MM-DD|null",
  "provenance": "expert|guideline|derived|consensus"
}
```

---

## 4. Reasoning Chain Architecture

### 4.1 Complete Reasoning Pipeline

```
ClinicalPresentation (input)
         │
         ▼
SyndromeIdentification
  - Match presentation features to syndrome nodes
  - Score each syndrome by feature overlap
  - Output: ranked syndrome list with scores
         │
         ▼
DifferentialGeneration
  - For each top syndrome, retrieve linked diseases (presents_as edges)
  - Combine into unified differential
  - Apply Bayesian priors (prevalence, population)
         │
         ▼
EvidenceWeighting
  - For each disease in differential:
    * Traverse diagnosed_by edges to lab/pathology findings
    * Apply likelihood ratios (sensitivity/specificity)
    * Traverse argues_against edges for exclusion
    * Weight by evidence_grade
  - Compute posterior probabilities
         │
         ▼
DiagnosisRanking
  - Rank diseases by posterior probability
  - Apply urgency modifiers (rapid decline, critical values)
  - Output: ranked diagnosis list with confidence scores
         │
         ▼
TreatmentSelection
  - For top-ranked diagnosis:
    * Traverse treated_with edges to drugs
    * Filter by contraindicated_in edges
    * Rank by line_of_therapy, evidence_grade
    * Apply patient-specific factors (eGFR, comorbidities, pregnancy)
         │
         ▼
MonitoringPlan
  - Combine monitoring protocols from:
    * Disease monitored_by edges
    * Selected drugs monitors edges
    * Complication risk profiles
  - De-duplicate and schedule
         │
         ▼
ExplainableOutput
  - For each recommendation, trace full path:
    Presentation → Syndrome → Disease → Evidence → Treatment → Monitoring
  - Generate natural language reasoning summary
  - Provide confidence intervals
```

### 4.2 Weight Calculation Methods

**Diagnostic Edge Weight (diagnosed_by):**
```
weight = (sensitivity + specificity) / 2 * evidence_grade_multiplier
evidence_grade_multiplier: 1A=1.0, 1B=0.9, 2A=0.8, 2B=0.7, 2C=0.6, 2D=0.5, OP=0.4, NG=0.3
```

**Treatment Edge Weight (treated_with):**
```
weight = (1 / line_of_therapy) * evidence_grade_multiplier * guideline_concordance
guideline_concordance: 1.0 if all guidelines agree, 0.8 if partial, 0.5 if significant disagreement
```

**Bayesian Update for Diagnosis:**
```
posterior = prior * likelihood / evidence
likelihood = product of (LR+ for positive findings) * (LR- for negative findings)
```

---

## 5. Explainability Layer

### 5.1 Traceability for Every Recommendation

For any output recommendation, the system provides:

```json
{
  "recommendation": "Start rituximab 375mg/m2 weekly x4",
  "confidence": 0.87,
  "reasoning_chain": [
    {
      "step": "Syndrome Identification",
      "nodes_traversed": ["SYND-RPGN"],
      "evidence": "Crescents on biopsy, anti-GBM negative, ANCA positive"
    },
    {
      "step": "Differential Generation", 
      "nodes_traversed": ["SYND-RPGN", "anca", "antiGbm", "lupus", "c3"],
      "evidence": "ANCA+ excludes anti-GBM; C3 normal argues against C3G/lupus"
    },
    {
      "step": "Evidence Weighting",
      "edges_traversed": ["diagnosed_by(anca, ANCA-MPO)", "argues_against(antiGbm, Anti-GBM-neg)"],
      "likelihood_ratios": {"anca": 15.2, "antiGbm": 0.02}
    },
    {
      "step": "Diagnosis Ranking",
      "result": "anca: 0.91, lupus: 0.05, antiGbm: 0.01, c3: 0.03"
    },
    {
      "step": "Treatment Selection",
      "edges_traversed": ["treated_with(anca, rituximab)", "treated_with(anca, cyclophosphamide)"],
      "selected": "rituximab (line 1, 1B evidence, KDIGO 2021)"
    }
  ],
  "alternative_paths": [
    {"path": "cyclophosphamide", "weight": 0.78, "reason_not_selected": "fertility preservation preferred"}
  ]
}
```

### 5.2 Natural Language Explanation Generation

> "Based on the clinical presentation of rapidly progressive glomerulonephritis with positive MPO-ANCA and negative anti-GBM, the leading diagnosis is ANCA-associated vasculitis (91% confidence). The recommended first-line induction therapy is rituximab 375 mg/m² weekly for 4 weeks, per KDIGO 2021 (Grade 1B). This recommendation is supported by the RITUXVAS and RAVE trials. Alternative induction with cyclophosphamide is equally effective but carries higher risks of infertility and hemorrhagic cystitis, making rituximab preferred in this 28-year-old woman. Monitoring includes monthly CBC, renal function, and ANCA titers at 3 and 6 months."

---

## 6. Graph Query Patterns

### 6.1 Common Clinical Queries (Cypher-like Pseudocode)

**Find all diseases causing nephrotic syndrome:**
```cypher
MATCH (s:Syndrome {id: "SYND-NS"})<-[:causes]-(d:Disease)
RETURN d.id, d.name, edge.weight, edge.evidence_grade
ORDER BY edge.weight DESC
```

**Find first-line drugs for FSGS:**
```cypher
MATCH (d:Disease {id: "fsgs"})-[:treated_with {line_of_therapy: 1}]->(dr:Drug)
RETURN dr.name, edge.evidence_grade, edge.guideline_source
ORDER BY edge.weight DESC
```

**Find monitoring protocol for tacrolimus:**
```cypher
MATCH (dr:Drug {name: "Tacrolimus"})-[:monitors]->(m:MonitoringProtocol)
RETURN m.id, m.parameters, m.schedule, m.safety_monitoring
```

**Find complications of rituximab:**
```cypher
MATCH (dr:Drug {name: "Rituximab"})-[:caused_by]->(c:Complication)
RETURN c.name, c.risk_level, c.mechanism, c.prevention
```

**Trace guideline recommendation to evidence:**
```cypher
MATCH (g:Guideline {id: "GS-KDIGO-2021-GN"})-[:recommends]->(a:Action)
      <-[:treated_with]-(d:Disease)-[:diagnosed_by]->(l:Lab)
RETURN g.title, a.description, d.name, l.name
```

**Find shared pathology between diseases:**
```cypher
MATCH (d1:Disease {id: "mcd"})-[:diagnosed_by]->(p:Pathology)<-[:diagnosed_by]-(d2:Disease)
WHERE d1 <> d2
RETURN d2.name, p.name, p.clinical_significance
```

---

## 7. Graph Quality Metrics

| Metric | Definition | Target | Measurement |
|---|---|---|---|
| **Node Coverage** | % of required node types populated | 100% | Count / Required |
| **Edge Density** | Average edges per node | >5 | Total edges / Total nodes |
| **Disease Connectivity** | Avg paths to other diseases | >10 | Graph analysis |
| **Orphan Nodes** | Nodes with <2 edges | 0 | Automated scan |
| **Evidence Density** | % edges with evidence_grade ≥2B | >80% | Edge property audit |
| **Guideline Traceability** | % treatment edges with guideline_source | 100% | Edge property audit |
| **Circular Paths** | Cycles in differential graph | Minimal | Graph algorithm |
| **Freshness** | % edges reviewed <12 months | >90% | Date audit |

---

## 8. Future Graph Extensions

### 8.1 Molecular Pathway Layer
- Add `MolecularPathway` nodes
- Edges: `disease_has_pathway`, `drug_targets_pathway`, `biomarker_reflects_pathway`
- Enable mechanism-based treatment selection

### 8.2 Genetic Association Layer
- Add `Gene` and `Variant` nodes
- Edges: `gene_associated_with_disease`, `variant_modifies_drug_response`
- Enable precision medicine

### 8.3 Drug-Gene Interaction Layer
- Add `Pharmacogenomic` edges
- Example: `TPMT variant → Azathioprine dose reduction`, `APOL1 high-risk → FSGS risk`

### 8.4 Clinical Trial Matching
- Add `ClinicalTrial` nodes
- Edges: `trial_studies_disease`, `trial_uses_drug`, `patient_matches_trial`
- Enable automated trial screening

### 8.5 Patient Knowledge Graph
- Instantiate per-patient subgraph
- Nodes: Patient-specific lab values, biopsy findings, medications, comorbidities
- Edges: `patient_has_finding`, `patient_takes_drug`, `patient_has_comorbidity`
- Enable personalized reasoning

---

## 9. Implementation Architecture

### 9.1 Graph Database Schema (Neo4j-compatible)

```cypher
// Node Labels
:Syndrome, :Disease, :Pathology, :Lab, :Drug, :MonitoringProtocol, 
:Complication, :Guideline, :EvidenceEntry, :ClinicalCase

// Relationship Types
:PRESENTS_AS, :CAUSES, :DIAGNOSED_BY, :ARGUES_AGAINST,
:TREATED_WITH, :CONTRAINDICATED_IN, :MONITORED_BY, :MONITORS,
:COMPLICATED_BY, :CAUSED_BY, :RECOMMENDED_BY, :EVIDENCE_FOR,
:PART_OF, :OVERLAPS_WITH
```

### 9.2 API Endpoints for Graph Traversal

| Endpoint | Method | Description |
|---|---|---|
| `/graph/reason` | POST | Execute full reasoning chain from presentation |
| `/graph/differential` | POST | Generate differential for syndrome |
| `/graph/treatment` | POST | Get treatments for disease |
| `/graph/monitoring` | POST | Get monitoring plan |
| `/graph/explain` | POST | Get reasoning trace for recommendation |
| `/graph/query` | POST | Execute arbitrary Cypher query (admin) |

---

## 10. Appendices

### Appendix A: Reusable Knowledge Object Registry

| Object Type | Count | Document Reference |
|---|---|---|
| Clinical Syndromes | 16 | CLINICAL_SYNDROME_LIBRARY.md |
| Differential Diagnosis Tables | 14+ | DIFFERENTIAL_DIAGNOSIS_LIBRARY.md |
| Pathology Entities | 37 | PATHOLOGY_KNOWLEDGE_LIBRARY.md |
| Laboratory Entities | 61 | LABORATORY_KNOWLEDGE_LIBRARY.md |
| Drug Entities | 50+ | DRUG_INTELLIGENCE_LIBRARY.md |
| Monitoring Protocols | 20+ | MONITORING_PROTOCOL_LIBRARY.md |
| Complication Entities | 24 | COMPLICATION_LIBRARY.md |
| Guideline Sources | 14+ | GUIDELINE_HARMONIZATION.md |

### Appendix B: Disease Connectivity Matrix (Sample)

| Disease | Shared Pathology | Shared Drugs | Shared Complications | Shared Syndromes |
|---|---|---|---|---|
| `iga` | 8 (mesangial deposits, foot process effacement, etc.) | 12 (ACEi, SGLT2i, steroids, etc.) | 6 (infection, CVD, etc.) | 4 (NS, NS, RPGN, MH) |
| `mcd` | 4 (foot process effacement, minimal LM) | 10 (steroids, CNI, etc.) | 5 (infection, thrombosis, etc.) | 2 (NS, IP) |
| `membranous` | 6 (subepithelial deposits, full-house IF) | 11 (ACEi, rituximab, etc.) | 7 (infection, thrombosis, etc.) | 3 (NS, IP, CKD) |
| `lupus` | 12 (full-house IF, subendothelial deposits, etc.) | 15 (MMF, CYC, rituximab, etc.) | 9 (infection, thrombosis, CVD, etc.) | 6 (NS, NT, RPGN, ASH, etc.) |
| `transplantGlomerulopathy` | 7 (GBM duplication, PTC multilayering) | 9 (CNI, MMF, rituximab, etc.) | 8 (infection, CVD, malignancy, etc.) | 3 (TX, CKD, IP) |

---

**End of Document**  
**Next Review:** 2027-07-10  
**Governance Lead:** Clinical Knowledge Engineering Team
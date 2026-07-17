"""Seed V4.0 Medical Knowledge Expansion: diseases, guidelines, pathways, and drug knowledge.

This command is the entry point for the V4.0 knowledge expansion.
It seeds:
  1. Disease records (comprehensive medical knowledge objects)
  2. Additional guideline sources (ERA, ASN, ISN, KDOQI, ERA-EDTA, AHA, ADA)
  3. Additional KnowledgeBaseEntry rules for new diseases
  4. Drug knowledge expansion (mechanism, side effects, monitoring)
  5. Clinical pathway definitions
"""
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction

from knowledge.models import (
    GuidelineSource, KnowledgeBaseEntry, Disease,
    ClinicalPathway, DiseaseCategory,
)
from treatments.models import DrugMaster


# â”€â”€â”€ GUIDELINE SOURCES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

GUIDELINE_SOURCES = [
    {"abbr": "KDIGO", "year": 2021, "title": "KDIGO 2021 Glomerular Diseases Guideline"},
    {"abbr": "KDIGO", "year": 2024, "title": "KDIGO 2024 Lupus Nephritis Guideline"},
    {"abbr": "KDIGO", "year": 2024, "title": "KDIGO 2024 ANCA Vasculitis Guideline"},
    {"abbr": "KDIGO", "year": 2024, "title": "KDIGO 2024 Diabetes Management in CKD Guideline"},
    {"abbr": "KDIGO", "year": 2025, "title": "KDIGO 2025 IgAN and IgAV Guideline"},
    {"abbr": "KDIGO", "year": 2025, "title": "KDIGO 2025 Nephrotic Syndrome in Children Guideline"},
    {"abbr": "KDIGO", "year": 2021, "title": "KDIGO 2021 Blood Pressure in CKD Guideline"},
    {"abbr": "KDIGO", "year": 2021, "title": "KDIGO 2021 AKI Guideline"},
    {"abbr": "KDIGO", "year": 2024, "title": "KDIGO 2024 CKD Evaluation and Management Guideline"},
    {"abbr": "KDIGO", "year": 2024, "title": "KDIGO 2024 Transplant Recipient Guideline"},
    {"abbr": "ERA", "year": 2022, "title": "ERA 2022 Glomerular Disease Recommendations"},
    {"abbr": "ERA", "year": 2024, "title": "ERA 2024 IgAN position paper"},
    {"abbr": "ERA-EDTA", "year": 2023, "title": "ERA-EDTA 2023 Nephrology Guidelines"},
    {"abbr": "ISN", "year": 2023, "title": "ISN 2023 Glomerular Disease Classification Update"},
    {"abbr": "ISN", "year": 2024, "title": "ISN 2024 Renal Pathology Consensus"},
    {"abbr": "ASN", "year": 2023, "title": "ASN 2023 Kidney Health Guidelines"},
    {"abbr": "KDOQI", "year": 2023, "title": "KDOQI 2023 CKD Nutrition Guideline"},
    {"abbr": "KDOQI", "year": 2024, "title": "KDOQI 2024 Vascular Access Guideline"},
    {"abbr": "AHA", "year": 2023, "title": "AHA 2023 Heart-Kidney Disease Statement"},
    {"abbr": "ADA", "year": 2025, "title": "ADA 2025 Standards of Care in Diabetes"},
]


# â”€â”€â”€ DISEASE KNOWLEDGE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

DISEASES = {
    # === Existing diseases (re-seeded with comprehensive knowledge) ===
    "iga": {
        "name": "IgA Nephropathy / IgA Vasculitis Nephritis",
        "category": DiseaseCategory.PRIMARY,
        "definition": "IgA nephropathy is a glomerular disease characterized by dominant or codominant mesangial deposits of IgA. It is the most common primary glomerulonephritis worldwide.",
        "epidemiology": "Most common primary GN worldwide. Incidence 2.5/100,000/year. Peak age 20-40. Male:female 2:1. High prevalence in East Asia, moderate in Europe, low in Africa.",
        "etiology": "Aberrantly glycosylated IgA1 with reduced galactose in the hinge region triggers autoantibody formation and mesangial immune complex deposition. Genetic susceptibility (MHC, complement genes). Mucosal infection triggers.",
        "pathophysiology": "Galactose-deficient IgA1 â†’ anti-glycan IgG/IgA autoantibodies â†’ circulating immune complexes â†’ mesangial deposition â†’ complement activation (lectin pathway) â†’ mesangial cell proliferation â†’ podocyte injury â†’ glomerulosclerosis.",
        "clinical_presentation": "Hematuria (macroscopic or microscopic), often coinciding with mucosal infections. Proteinuria (subnephrotic to nephrotic range). Hypertension. Progressive CKD in 30-40% over 20 years.",
        "diagnostic_criteria": [
            {"criterion": "Mesangial IgA deposition on immunofluorescence", "essential": True, "evidence": "1"},
            {"criterion": "Hematuria with or without proteinuria", "essential": False, "evidence": "2"},
            {"criterion": "Exclusion of lupus, HSP, liver disease", "essential": True, "evidence": "OP"},
        ],
        "differential_diagnosis": ["thinBasementMembrane", "alport", "infectionRelated", "membranous", "lupus"],
        "lab_findings": [
            "Hematuria (dysmorphic RBCs, RBC casts)", "Proteinuria (variable)",
            "Normal C3/C4", "Elevated serum IgA in 50%", "eGFR variable (normal to reduced)",
        ],
        "biopsy_findings": [
            "Mesangial IgA deposits (dominant or codominant)", "Mesangial hypercellularity",
            "MEST-C score: M (mesangial), E (endocapillary), S (segmental), T (tubular), C (crescents)",
        ],
        "classification_systems": [
            {"name": "Oxford MEST-C", "components": "M0/M1, E0/E1, S0/S1, T0/T1/T2, C0/C1/C2",
             "source": "KDIGO 2025"},
            {"name": "International IgAN Risk Prediction Tool", "components": "eGFR, proteinuria, BP, MEST-C, age",
             "source": "KDIGO 2025"},
        ],
        "risk_stratification": [
            {"factor": "Proteinuria >1g/day", "risk": "Progression"},
            {"factor": "eGFR <60 at diagnosis", "risk": "Progression"},
            {"factor": "Hypertension", "risk": "Progression"},
            {"factor": "Oxford MEST-C T2", "risk": "Progression"},
        ],
        "treatment_overview": "Supportive care (RAASi, SGLT2i, BP control) for all. Immunosuppression for high-risk patients: corticosteroids for those with persistent proteinuria >1g/day after supportive care. Consider targeted therapies (budesonide, sparsentan) in appropriate candidates.",
        "monitoring_protocol": "3-monthly: BP, eGFR, 24h UTP. 6-monthly: serum albumin. Biopsy for unexplained deterioration or new active sediment.",
        "complications": [
            "Progressive CKD", "ESKD in 15-20% at 10 years", "Hypertension",
            "Relapse post-transplant (recurrent IgAN in 10-50%)",
        ],
        "relapse_information": "Hematuria episodes may recur with infections. Proteinuria relapse on steroid taper in ~30%. Post-transplant recurrence in 10-50% (higher with rapid native progression).",
        "long_term_prognosis": "10-year kidney survival ~80% overall, but highly variable. Without proteinuria: >90% 10-year survival. Proteinuria >3g/day: <50% 10-year survival.",
    },
    "membranous": {
        "name": "Membranous Nephropathy",
        "category": DiseaseCategory.PRIMARY,
        "definition": "Membranous nephropathy is an autoimmune glomerular disease characterized by subepithelial immune complex deposits causing nephrotic syndrome.",
        "epidemiology": "Incidence ~1/100,000/year. Peak 40-60 years. Male:female 2:1. Primary ~75%, secondary ~25%.",
        "etiology": "Primary: Autoantibodies against PLA2R (70-80%) or THSD7A (1-5%). Secondary: SLE, hepatitis B, solid tumors, drugs (NSAIDs, penicillamine, gold), infections.",
        "pathophysiology": "Autoantibodies bind to podocyte antigens (PLA2R, THSD7A) â†’ in situ immune complex formation â†’ complement activation (C5b-9 membrane attack complex) â†’ podocyte injury â†’ subepithelial deposits + spike formation â†’ proteinuria.",
        "clinical_presentation": "Nephrotic syndrome (edema, frothy urine, hypoalbuminemia). Hematuria in 30-50% (microscopic). Thrombotic complications (DVT, PE, renal vein thrombosis).",
        "diagnostic_criteria": [
            {"criterion": "Subepithelial deposits on biopsy", "essential": True},
            {"criterion": "PLA2R antibody positive (serum)", "essential": False},
            {"criterion": "Nephrotic-range proteinuria", "essential": False},
        ],
        "differential_diagnosis": ["lupus", "mcd", "fsgs", "amyloidosis", "infectionRelated"],
        "lab_findings": ["Nephrotic-range proteinuria", "Hypoalbuminemia", "PLA2R antibodies (70-80%)",
                          "Normal C3/C4", "eGFR variable"],
        "biopsy_findings": ["Subepithelial deposits (stage I-IV)", "Spike formation (silver stain)",
                            "IgG4 dominant (primary)", "Full-house = secondary (lupus)"],
        "classification_systems": [
            {"name": "Ehrenreich-Churg staging", "components": "Stage I-IV",
             "source": "KDIGO 2021"},
        ],
        "risk_stratification": [
            {"factor": "Persistent high-titer PLA2R", "risk": "Non-remission"},
            {"factor": "eGFR decline at 6 months", "risk": "Progression"},
            {"factor": "Proteinuria >8g/day", "risk": "Complications"},
        ],
        "treatment_overview": "Supportive care first (RAASi, SGLT2i, diuretics, anticoagulation if albumin <2.5). Immunosuppression (rituximab first-line, CNI-based, cyclophosphamide+steroids for severe).",
        "monitoring_protocol": "Monthly: BP, eGFR, 24h UTP, albumin, PLA2R titer. 3-monthly for stable patients.",
        "complications": ["Venous thromboembolism (5-10%)", "Progressive CKD", "Infection risk with immunosuppression"],
        "relapse_information": "Relapse rate 25-30% after rituximab, 40-50% after CNI withdrawal. PLA2R titer rise precedes relapse by 3-6 months.",
        "long_term_prognosis": "One-third spontaneous remission, one-third remission with treatment, one-third progressive CKD. 10-year kidney survival ~80%.",
    },
    "mcd": {
        "name": "Minimal Change Disease",
        "category": DiseaseCategory.PRIMARY,
        "definition": "Minimal change disease is a podocytopathy causing nephrotic syndrome with minimal light microscopic changes and diffuse foot process effacement on EM.",
        "epidemiology": "Most common cause of nephrotic syndrome in children (80-90%). Accounts for 10-15% of adult nephrotic syndrome. Peak: 2-6 years (children), >40 years (adults).",
        "etiology": "Idiopathic in most cases. Secondary: NSAIDs, lithium, interferon, infections, allergies, Hodgkin lymphoma, thymoma.",
        "pathophysiology": "T-cell dysregulation â†’ circulating permeability factor â†’ podocyte actin cytoskeleton disruption â†’ foot process effacement â†’ proteinuria. Possible role of B-cell and T-cell interaction.",
        "clinical_presentation": "Acute-onset nephrotic syndrome (peripheral edema, periorbital edema, frothy urine). Abrupt onset over days to weeks. Hypertension uncommon. Hematuria in 10-20%.",
        "diagnostic_criteria": [
            {"criterion": "Nephrotic syndrome with bland sediment", "essential": True},
            {"criterion": "Diffuse foot process effacement on EM", "essential": True},
            {"criterion": "No light microscopic changes or mild mesangial prominence", "essential": True},
            {"criterion": "Steroid-responsive (classic)", "essential": False},
        ],
        "differential_diagnosis": ["fsgs", "membranous", "amyloidosis", "lupus"],
        "lab_findings": ["Nephrotic-range proteinuria", "Hypoalbuminemia", "Normal C3/C4",
                          "eGFR normal or transiently reduced", "Normal biopsy on light microscopy"],
        "biopsy_findings": ["Normal light microscopy", "No immune deposits on IF",
                            "Diffuse foot process effacement on EM"],
        "classification_systems": [{"name": "Steroid response classification", "components": "Steroid-sensitive, steroid-dependent, steroid-resistant"}],
        "risk_stratification": [{"factor": "Adult onset", "risk": "Higher relapse, steroid resistance"},
                                  {"factor": "AKI at presentation", "risk": "Complicated course"}],
        "treatment_overview": "Corticosteroids (prednisolone 1mg/kg/day for 4-16 weeks). Steroid-sparing agents (MMF, CNI, rituximab) for frequent relapses or steroid dependence. Supportive: salt restriction, diuretics.",
        "monitoring_protocol": "Weekly: proteinuria (dipstick), BP, weight, albumin. Monthly: eGFR. Monitor steroid side effects.",
        "complications": ["Infection (pneumococcal peritonitis)", "Thromboembolism", "AKI",
                          "Steroid toxicity (growth retardation in children, diabetes, osteoporosis)"],
        "relapse_information": "Relapse rate 60-80% in children, 40-50% in adults. Frequent relapsers: >2 relapses/6 months. Steroid-dependent: relapse during or within 2 weeks of steroid taper.",
        "long_term_prognosis": "Excellent overall. >90% achieve remission with steroids. Few progress to ESKD. Adult-onset has higher risk of steroid resistance.",
    },
    "fsgs": {
        "name": "Focal Segmental Glomerulosclerosis",
        "category": DiseaseCategory.PRIMARY,
        "definition": "FSGS is a clinicopathologic syndrome characterized by segmental glomerular scarring and podocyte injury. Includes primary, genetic, and secondary forms.",
        "epidemiology": "Incidence ~0.8/100,000/year. More common in African ancestry. Male:female 1.5:1. Accounts for 20-30% of adult nephrotic syndrome.",
        "etiology": "Primary: circulating permeability factor (suPAR, anti-CD40). Genetic: mutations in podocyte genes (NPHS1, NPHS2, ACTN4, TRPC6, INF2). Secondary: adaptive (obesity, hypertension, renal ablation), viral (HIV, parvovirus B19), drug-induced (pamidronate, interferon, heroin).",
        "pathophysiology": "Podocyte injury â†’ detachment from GBM â†’ denuded basement membrane â†’ adhesion to Bowman's capsule â†’ segmental sclerosis. Primary: permeability factor causes podocyte dysfunction. Genetic: structural podocyte defects.",
        "clinical_presentation": "Nephrotic syndrome (primary) or subnephrotic proteinuria (secondary). Microscopic hematuria in 50%. Hypertension. Progressive renal dysfunction.",
        "diagnostic_criteria": [
            {"criterion": "Segmental sclerosis on biopsy", "essential": True},
            {"criterion": "Exclusion of secondary causes", "essential": True},
            {"criterion": "Nephrotic or subnephrotic proteinuria", "essential": False},
        ],
        "differential_diagnosis": ["mcd", "membranous", "alport", "hypertensiveNephrosclerosis", "amyloidosis"],
        "lab_findings": ["Proteinuria (variable)", "Hypoalbuminemia (primary)", "Hematuria (microscopic)",
                          "eGFR variable", "Elevated suPAR in primary"],
        "biopsy_findings": ["Segmental sclerosis", "Podocyte effacement on EM",
                            "FSGS variants: NOS, collapsing, tip, cellular, perihilar",
                            "IgM and C3 trapping in sclerotic areas (non-specific)"],
        "classification_systems": [
            {"name": "Columbia FSGS Classification", "components": "NOS, collapsing, tip, cellular, perihilar",
             "source": "KDIGO 2021"},
            {"name": "Primary vs Secondary FSGS", "components": "Primary, genetic, adaptive, viral, drug-induced"},
        ],
        "risk_stratification": [{"factor": "Collapsing variant", "risk": "Rapid progression"},
                                  {"factor": "Proteinuria >10g/day", "risk": "Poor renal survival"},
                                  {"factor": "eGFR <30 at diagnosis", "risk": "ESKD within 2 years"}],
        "treatment_overview": "High-dose corticosteroids for primary FSGS (prednisolone 1mg/kg/day for 4-16 weeks). CNIs (tacrolimus, ciclosporin) for steroid-resistant cases. Rituximab in refractory cases. Supportive: RAASi, SGLT2i, BP control. Treat underlying cause for secondary FSGS.",
        "monitoring_protocol": "Monthly: 24h UTP, eGFR, albumin, BP during induction. 3-monthly in remission.",
        "complications": ["Progressive CKD/ESKD", "Nephrotic syndrome complications",
                          "Post-transplant recurrence (30-50% in primary)"],
        "relapse_information": "Relapse in 30-50% after steroid taper. Post-transplant recurrence risk 30-50% in primary FSGS, <10% in genetic. Collapsing variant frequently recurs.",
        "long_term_prognosis": "10-year kidney survival: primary FSGS 60-70%, genetic FSGS 80-90%, collapsing FSGS <30%.",
    },
    "lupus": {
        "name": "Lupus Nephritis",
        "category": DiseaseCategory.SECONDARY,
        "definition": "Lupus nephritis is renal involvement in systemic lupus erythematosus, ranging from mild mesangial to severe proliferative disease.",
        "epidemiology": "Affects 40-60% of SLE patients. More common in African, Hispanic, Asian ancestry. F:M 9:1. Peak age 20-40.",
        "etiology": "SLE is a multi-system autoimmune disease with genetic predisposition (MHC, complement deficiency), environmental triggers (UV, infections), and hormonal factors.",
        "pathophysiology": "Loss of immune tolerance â†’ autoantibodies (anti-dsDNA, anti-nucleosome) â†’ immune complex deposition in glomeruli â†’ complement activation â†’ inflammation â†’ glomerular injury. Type I interferon pathway activation.",
        "clinical_presentation": "Hematuria, proteinuria, RBC casts. Hypertension. Reduced eGFR. Concurrent SLE manifestations: malar rash, arthritis, serositis, cytopenias.",
        "diagnostic_criteria": [
            {"criterion": "Renal biopsy showing immune complex GN", "essential": True},
            {"criterion": "SLE by ACR/EULAR criteria", "essential": True},
            {"criterion": "Proteinuria >0.5g/day or RBC casts", "essential": False},
        ],
        "differential_diagnosis": ["membranous", "iga", "infectionRelated", "cryoglobulinemic", "anca"],
        "lab_findings": ["ANA positive", "Anti-dsDNA positive", "Low C3/C4",
                          "Proteinuria", "Hematuria", "eGFR variable"],
        "biopsy_findings": [
            "ISN/RPS Class I-VI", "Full-house immunofluorescence (IgG, IgA, IgM, C3, C1q)",
            "Class III: focal proliferative", "Class IV: diffuse proliferative",
            "Class V: membranous", "Activity and chronicity indices",
        ],
        "classification_systems": [
            {"name": "ISN/RPS Lupus Nephritis Classification", "components": "Class I-VI",
             "source": "ISN 2023"},
            {"name": "Activity and Chronicity Indices", "components": "Activity score 0-24, Chronicity score 0-12",
             "source": "NIH"},
        ],
        "risk_stratification": [{"factor": "Class III/IV with crescents", "risk": "Rapid progression"},
                                  {"factor": "High chronicity index", "risk": "ESKD"},
                                  {"factor": "Persistent anti-dsDNA", "risk": "Flare"}],
        "treatment_overview": "Induction: MMF or cyclophosphamide + corticosteroids for Class III/IV. Maintenance: MMF or azathioprine. Class V: MMF + CNI or rituximab. Belimumab as add-on. HCQ for all SLE patients.",
        "monitoring_protocol": "Monthly during induction: eGFR, UPCR, C3/C4, anti-dsDNA. 3-monthly during maintenance. Annual biopsy for persistent proteinuria.",
        "complications": ["ESKD", "Infection (immunosuppression)", "Cardiovascular disease",
                          "Thrombotic events (antiphospholipid syndrome)"],
        "relapse_information": "Relapse rate 25-40% over 5 years. Renal flares: proteinuria increase + active sediment. Predictors: low C3, rising anti-dsDNA, non-adherence.",
        "long_term_prognosis": "10-year kidney survival >80% with modern therapy. Class IV worst prognosis. ESRD risk highest in African ancestry.",
    },
    "anca": {
        "name": "ANCA-Associated Pauci-Immune GN",
        "category": DiseaseCategory.SECONDARY,
        "definition": "AAV is a small-vessel vasculitis with pauci-immune necrotizing GN. Includes microscopic polyangiitis (MPA), granulomatosis with polyangiitis (GPA), and eosinophilic GPA (EGPA).",
        "epidemiology": "Incidence ~20/million/year. Peak >60 years. GPA more common in Europe, MPA more in Japan. GPA: PR3-ANCA. MPA: MPO-ANCA.",
        "etiology": "Autoimmune with ANCA targeting PR3 or MPO. Genetic associations (HLA-DP, SERPINA1). Triggers: silica exposure, infections (S. aureus in GPA), drugs (hydralazine, propylthiouracil, cocaine).",
        "pathophysiology": "ANCA activates neutrophils â†’ neutrophil degranulation and NETosis â†’ endothelial injury â†’ necrotizing inflammation of small vessels â†’ crescentic GN. Complement alternative pathway activation (C5a) amplifies injury.",
        "clinical_presentation": "RPGN with hematuria, RBC casts, rapidly declining eGFR. Systemic features: fever, weight loss, arthralgia. GPA: ENT and lung involvement. MPA: renal-limited or renal+lung. EGPA: asthma, eosinophilia.",
        "diagnostic_criteria": [
            {"criterion": "Necrotizing pauci-immune GN on biopsy", "essential": True},
            {"criterion": "ANCA positive (PR3 or MPO)", "essential": False},
            {"criterion": "RPGN clinical picture", "essential": False},
        ],
        "differential_diagnosis": ["antiGbm", "lupus", "cryoglobulinemic", "thromboticMicroangiopathy", "infectionRelated"],
        "lab_findings": ["PR3-ANCA or MPO-ANCA positive", "Rapidly rising creatinine", "Hematuria with RBC casts",
                          "Normal C3/C4", "Elevated CRP/ESR"],
        "biopsy_findings": ["Pauci-immune (scant or no immune deposits)", "Necrotizing crescents",
                            "Fibrinoid necrosis", "Granulomas (GPA)"],
        "classification_systems": [
            {"name": "GPA/MPA/EGPA Classification", "source": "Chapel Hill Consensus 2012"},
            {"name": "Histopathologic Classification", "components": "Focal, crescentic, mixed, sclerotic",
             "source": "KDIGO 2024"},
        ],
        "risk_stratification": [{"factor": "Creatinine >500 at presentation", "risk": "Dialysis dependence"},
                                  {"factor": "Sclerotic class on biopsy", "risk": "Poor renal recovery"},
                                  {"factor": "Alveolar hemorrhage", "risk": "Mortality"}],
        "treatment_overview": "Induction: high-dose corticosteroids + rituximab (preferred) or cyclophosphamide. Plasma exchange for severe disease (Cr >500 or diffuse alveolar hemorrhage). Maintenance: rituximab or azathioprine + low-dose steroids.",
        "monitoring_protocol": "Monthly: eGFR, 24h UTP, ANCA titer, CRP. 3-monthly in remission. ANCA titer rise may predict relapse.",
        "complications": ["ESKD (20-30%)", "Alveolar hemorrhage (mortality 20-30%)",
                          "Infection (PCP prophylaxis with TMP/SMX required)",
                          "Relapse (30-50% at 5 years)", "Malignancy (cyclophosphamide)"],
        "relapse_information": "Relapse rate 30-50% at 5 years. PR3-ANCA has higher relapse risk than MPO-ANCA. ANCA titer rise + persistent positive predicts relapse. Rituximab maintenance reduces relapse.",
        "long_term_prognosis": "5-year patient survival >80%. 5-year renal survival ~75%. Relapse common - long-term immunosuppression typically needed.",
    },
    "antiGbm": {
        "name": "Anti-GBM Disease (Goodpasture Syndrome)",
        "category": DiseaseCategory.SECONDARY,
        "definition": "Anti-GBM disease is an autoimmune disorder with autoantibodies against the NC1 domain of type IV collagen causing rapidly progressive GN with or without pulmonary hemorrhage.",
        "epidemiology": "Incidence ~1/million/year. Bimodal age distribution: young males (20-30) and older adults (60-70). More common in Whites.",
        "etiology": "Autoantibodies against Î±3 chain of type IV collagen (Î±3(IV)NC1). Genetic: HLA-DRB1*1501. Triggers: smoking (pulmonary hemorrhage), hydrocarbon exposure, infections (influenza A), cocaine.",
        "pathophysiology": "Anti-GBM antibodies bind to alveolar and glomerular basement membranes â†’ complement activation â†’ neutrophil recruitment â†’ crescentic GN and pulmonary capillaritis. Antibody titer correlates with disease activity.",
        "clinical_presentation": "RPGN (oliguria, rapidly rising creatinine, hematuria). Pulmonary hemorrhage (hemoptysis, dyspnea, diffuse alveolar infiltrates). Fever, malaise, arthralgia.",
        "diagnostic_criteria": [
            {"criterion": "Positive anti-GBM antibodies (ELISA)", "essential": True},
            {"criterion": "Linear IgG staining on biopsy", "essential": True},
            {"criterion": "Crescentic GN on light microscopy", "essential": False},
        ],
        "differential_diagnosis": ["anca", "lupus", "thromboticMicroangiopathy", "cryoglobulinemic"],
        "lab_findings": ["Anti-GBM antibody positive", "Rapidly rising creatinine", "Hematuria with RBC casts",
                          "Proteinuria (variable)", "Normal C3/C4"],
        "biopsy_findings": ["Linear IgG staining along GBM", "Crescents (>90% on presentation)",
                            "Fibrinoid necrosis", "Scant immune deposits (pauci-immune pattern)"],
        "classification_systems": [{"name": "Anti-GBM Disease Classification",
                                      "components": "Renal-limited, pulmonary-renal, atypical",
                                      "source": "KDIGO 2021"}],
        "risk_stratification": [{"factor": "Creatinine >600 at presentation", "risk": "Dialysis dependence"},
                                  {"factor": "Oliguric renal failure", "risk": "Poor renal recovery"},
                                  {"factor": "High antibody titer", "risk": "Severe disease"}],
        "treatment_overview": "Plasma exchange daily for 14 days or until anti-GBM negative. High-dose corticosteroids (methylprednisolone 1g IV x3 then oral taper). Cyclophosphamide 2-3mg/kg/day orally or IV pulses. Maintenance: azathioprine for 6-12 months.",
        "monitoring_protocol": "Daily anti-GBM titers during plasma exchange. Weekly eGFR on recovery. Monthly for 6 months, then 3-monthly.",
        "complications": ["ESKD (60-70% of dialysis-dependent at presentation)",
                          "Pulmonary hemorrhage (mortality 10-20%)",
                          "Infection (immunosuppression)", "Relapse (<5%)"],
        "relapse_information": "Relapse rate <5% - low compared to other autoimmune GN. Relapse indicated by rising anti-GBM titers. Treat with plasma exchange + immunosuppression.",
        "long_term_prognosis": "Renal survival dependent on presenting creatinine. Dialysis-dependent at presentation: <10% recover. Creatinine <500: >80% recover renal function.",
    },
    "c3": {
        "name": "C3 Glomerulopathy / Complement-Mediated GN",
        "category": DiseaseCategory.PRIMARY,
        "definition": "C3 glomerulopathy is a group of kidney diseases caused by dysregulation of the alternative complement pathway, with dominant C3 deposition on immunofluorescence.",
        "epidemiology": "Rare (incidence ~1-2/million/year). Age: bimodal (children and young adults). Slight female predominance.",
        "etiology": "Genetic or acquired dysregulation of the alternative complement pathway. C3 nephritic factor (C3NeF) in 40-60%. Complement gene mutations (CFH, CFI, CFB, C3, CFHR5). CFH autoantibodies.",
        "pathophysiology": "Uncontrolled alternative pathway activation â†’ persistent C3 consumption â†’ C3 deposition in glomeruli â†’ complement-mediated glomerular injury. C3 glomerulonephritis (C3GN): mesangial and subendothelial C3. DDD: intramembranous dense deposits.",
        "clinical_presentation": "Hematuria, proteinuria, hypertension. Progressive CKD. May present with nephrotic syndrome. Associated conditions: partial lipodystrophy, drusen (CFH mutations).",
        "diagnostic_criteria": [
            {"criterion": "Dominant C3 deposition on IF (â‰¥2 orders stronger than other Igs)", "essential": True},
            {"criterion": "Low C3 (persistent)", "essential": False},
            {"criterion": "EM findings consistent with C3GN or DDD", "essential": False},
            {"criterion": "Exclusion of infection-related GN", "essential": True},
        ],
        "differential_diagnosis": ["infectionRelated", "lupus", "cryoglobulinemic", "iga"],
        "lab_findings": ["Low C3, normal C4 (alternative pathway)", "C3 nephritic factor positive (40-60%)",
                          "CFH mutation or autoantibody", "Hematuria, proteinuria", "eGFR reduced"],
        "biopsy_findings": ["Dominant C3 on IF", "C3GN: mesangial/subendothelial deposits",
                            "DDD: intramembranous dense ribbon-like deposits",
                            "Crescents may be present"],
        "classification_systems": [
            {"name": "C3 Glomerulopathy Classification", "components": "C3 glomerulonephritis, Dense deposit disease",
             "source": "KDIGO 2021"},
        ],
        "risk_stratification": [{"factor": "Crescents on biopsy", "risk": "Rapid progression"},
                                  {"factor": "Persistent low C3", "risk": "Active disease"},
                                  {"factor": "DDD histology", "risk": "Slowly progressive"}],
        "treatment_overview": "Supportive: RAASi, BP control. Immunosuppression for active disease: corticosteroids + MMF in C3GN (limited evidence). Complement inhibitors (eculizumab, iptacopan) experimental. Plasma exchange for CFH autoantibody cases.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP, C3/C4. Monitor for complement abnormalities. Regular ophthalmology (drusen).",
        "complications": ["Progressive CKD/ESKD (50% at 10 years)", "Ocular drusen",
                          "Partial lipodystrophy", "Infection risk (complement deficiency)"],
        "relapse_information": "Relapse common after immunosuppression withdrawal. Post-transplant recurrence: C3GN 50-80%, DDD 80-90%.",
        "long_term_prognosis": "10-year kidney survival ~50%. DDD has poorer prognosis. Complement inhibition may improve outcomes.",
    },
    "diabeticNephropathy": {
        "name": "Diabetic Kidney Disease",
        "category": DiseaseCategory.SECONDARY,
        "definition": "DKD is a progressive kidney disease caused by long-standing diabetes mellitus, leading to albuminuria and declining eGFR.",
        "epidemiology": "Most common cause of ESKD worldwide (30-50%). Affects 25-40% of diabetics. Type 2 DM accounts for >90% of DKD. Higher risk in African, Hispanic, Asian ancestry.",
        "etiology": "Chronic hyperglycemia leading to metabolic and hemodynamic injury. Genetic susceptibility. Hypertension. Obesity.",
        "pathophysiology": "Hyperglycemia â†’ AGE formation, oxidative stress, PKC activation, polyol pathway flux â†’ podocyte injury, mesangial expansion, GBM thickening, tubulointerstitial fibrosis. Hemodynamic: RAAS activation, intraglomerular hypertension. SGLT2 upregulation contributes to injury.",
        "clinical_presentation": "Initially asymptomatic. Microalbuminuria â†’ macroalbuminuria â†’ nephrotic syndrome. Gradual eGFR decline over years. Concurrent diabetic retinopathy (90% of type 1, 60% of type 2). Hypertension. Cardiovascular disease.",
        "diagnostic_criteria": [
            {"criterion": "Diabetes mellitus", "essential": True},
            {"criterion": "Persistent albuminuria or reduced eGFR", "essential": True},
            {"criterion": "Absence of active sediment", "essential": False},
            {"criterion": "Diabetic retinopathy present", "essential": False},
        ],
        "differential_diagnosis": ["hypertensiveNephrosclerosis", "diabeticNephropathyWithGN", "fsgs", "membranous"],
        "lab_findings": ["Hyperglycemia", "Raised HbA1c", "Albuminuria (A1-A3)",
                          "eGFR declining", "Bland urinary sediment"],
        "biopsy_findings": ["GBM thickening", "Mesangial expansion (nodular = Kimmelstiel-Wilson lesions)",
                            "Arteriolar hyalinosis", "Tubulointerstitial fibrosis"],
        "classification_systems": [
            {"name": "CKD Staging (G1-G5, A1-A3)", "source": "KDIGO 2024"},
            {"name": "Renal Pathology Society Classification", "components": "Class I-IV"},
        ],
        "risk_stratification": [{"factor": "HbA1c >8%", "risk": "Progression"},
                                  {"factor": "SBP >140", "risk": "Progression"},
                                  {"factor": "ACR >300", "risk": "ESKD"},
                                  {"factor": "Rapid eGFR decline", "risk": "ESKD"}],
        "treatment_overview": "Intensive glucose control (HbA1c <7%). RAASi (ACEi/ARB) for albuminuria. SGLT2i for cardiorenal protection (dapagliflozin, empagliflozin). Finerenone for additional benefit. BP target <130/80. Statin for cardiovascular prevention.",
        "monitoring_protocol": "3-monthly: HbA1c, eGFR, ACR, BP. 6-monthly: electrolytes, lipids. Annual: ophthalmology, foot exam.",
        "complications": ["ESKD", "Cardiovascular events (MI, stroke, HF)", "Hypoglycemia",
                          "Volume depletion (diuretics)", "Hyperkalemia (RAASi + finerenone)"],
        "relapse_information": "Progressive disease, not relapsing-remitting. Albuminuria may decrease with treatment.",
        "long_term_prognosis": "10-year ESKD risk: 20-40% with macroalbuminuria. Cardiovascular mortality 2-3x higher than general population.",
    },
    # === New Primary Glomerular Diseases ===
    "denseDepositDisease": {
        "name": "Dense Deposit Disease (Type II MPGN)",
        "category": DiseaseCategory.PRIMARY,
        "definition": "DDD is a rare renal disease characterized by dense intramembranous electron-dense deposits in the GBM, caused by uncontrolled alternative complement pathway activation.",
        "epidemiology": "Incidence ~0.5/million/year. Typically children and young adults (peak 5-15 years). Slight female predominance.",
        "etiology": "Acquired or genetic dysregulation of the alternative complement pathway. C3 nephritic factor (C3NeF) in 60-70%. CFH mutations. CFHR5 mutations.",
        "pathophysiology": "Persistent alternative pathway activation â†’ continuous C3 cleavage â†’ C3b deposition along GBM â†’ dense transformation of lamina densa â†’ glomerular injury.",
        "clinical_presentation": "Hematuria, proteinuria (often nephrotic). Hypertension. Progressive CKD. Associated: acquired partial lipodystrophy, ocular drusen (CFH mutations).",
        "diagnostic_criteria": [
            {"criterion": "Intramembranous dense ribbon-like deposits on EM", "essential": True},
            {"criterion": "Dominant C3 on IF (>2 orders stronger than IgG)", "essential": True},
            {"criterion": "Low C3 with normal C4", "essential": False},
        ],
        "differential_diagnosis": ["c3", "membranous", "infectionRelated", "mpgn"],
        "lab_findings": ["Very low C3", "Normal C4", "C3NeF positive (60-70%)",
                          "Hematuria", "Proteinuria", "eGFR reduced"],
        "biopsy_findings": ["Dense intramembranous deposits (GBM ribbon-like)", "Dominant C3 on IF",
                            "Mesangial hypercellularity", "Crescents in active cases"],
        "treatment_overview": "Supportive care (RAASi). Corticosteroids Â± MMF for active disease (limited evidence). Eculizumab (anti-C5) in progressive cases. Plasma exchange for CFH autoantibody. Complement inhibitors (iptacopan, vemircopan) in trials.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP, C3. Ophthalmology monitoring for drusen.",
        "complications": ["Progressive CKD/ESKD (50% at 5 years)", "Ocular drusen", "Lipodystrophy"],
        "relapse_information": "Chronic progressive disease. Post-transplant recurrence >80%.",
        "long_term_prognosis": "ESKD in 50% within 5-10 years. High post-transplant recurrence.",
    },
    "mpgn": {
        "name": "Membranoproliferative GN (Non-C3, Non-IC)",
        "category": DiseaseCategory.PRIMARY,
        "definition": "MPGN is a histologic pattern of glomerular injury with mesangial hypercellularity, GBM double contours, and immune complex or complement deposition.",
        "epidemiology": "Incidence declining due to better classification. Now accounts for <5% of GN. All ages, peaks in children and young adults.",
        "etiology": "Immune complex-mediated (infection, autoimmune, monoclonal gammopathy) or complement-mediated (C3 glomerulopathy). Idiopathic in minority. Classification by IF pattern.",
        "pathophysiology": "Immune complex deposition â†’ complement activation â†’ mesangial and endocapillary proliferation â†’ GBM remodeling (double contours = tram tracks) â†’ glomerulosclerosis.",
        "clinical_presentation": "Nephrotic syndrome (40-60%). Hematuria (microscopic or macroscopic). Hypertension. Reduced eGFR. May have underlying infection or autoimmune disease.",
        "diagnostic_criteria": [
            {"criterion": "MPGN pattern on light microscopy", "essential": True},
            {"criterion": "IF pattern determines subtype (IgG+, C3+ vs C3-only)", "essential": True},
            {"criterion": "Subendothelial Â± mesangial deposits on EM", "essential": False},
        ],
        "differential_diagnosis": ["c3", "lupus", "cryoglobulinemic", "infectionRelated", "iga"],
        "lab_findings": ["Hematuria", "Proteinuria", "Low C3/C4 (immune complex type)",
                          "Identify underlying cause: HCV, HBV, SLE, MGUS"],
        "biopsy_findings": ["Mesangial hypercellularity", "Endocapillary proliferation",
                            "Double contours (tram tracks)", "IF: IgG + C3 (IC-MPGN) or C3 dominant (C3G)"],
        "classification_systems": [
            {"name": "MPGN Classification by IF", "components": "Immune complex (IgG+), Complement (C3-only)",
             "source": "KDIGO 2021"},
        ],
        "risk_stratification": [{"factor": "Nephrotic range proteinuria", "risk": "Progression"},
                                  {"factor": "Reduced eGFR at presentation", "risk": "ESKD"}],
        "treatment_overview": "Treat underlying cause (antivirals for HCV, immunosuppression for SLE/autoimmune). Idiopathic: corticosteroids + MMF for IC-MPGN. Complement inhibitors for C3-dominant. Supportive: RAASi.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP, complement levels. Screen for underlying cause.",
        "complications": ["ESKD (50% at 10 years)", "Hypertension", "Infection"],
        "relapse_information": "Relapse common after treatment withdrawal. Post-transplant recurrence 30-50%.",
        "long_term_prognosis": "10-year kidney survival ~50%. Depends on underlying cause and treatment response.",
    },
    "fibrillaryGlomerulonephritis": {
        "name": "Fibrillary Glomerulonephritis / Immunotactoid Glomerulopathy",
        "category": DiseaseCategory.PRIMARY,
        "definition": "Fibrillary GN is a rare glomerular disease with randomly oriented fibrils (~20nm) in the mesangium and GBM. Immunotactoid glomerulopathy has larger microtubular deposits (>30nm).",
        "epidemiology": "Fibrillary GN: incidence <1% of native biopsies. Mean age 50-60. Fibrillary GN: M=F. Immunotactoid: M:F 2:1.",
        "etiology": "Fibrillary GN: mostly idiopathic. Associated with malignancy (lymphoproliferative, solid tumors) and autoimmune conditions (SLE, RA, Crohn's). Immunotactoid: strongly associated with monoclonal gammopathy or lymphoproliferative disease.",
        "pathophysiology": "Fibrillary GN: IgG4-predominant immune complexes with Congo red-negative fibrils (~20nm). Immunotactoid: microtubular deposits >30nm, often monoclonal IgG.",
        "clinical_presentation": "Proteinuria (nephrotic in 50%), hematuria, hypertension, reduced eGFR at diagnosis in many.",
        "diagnostic_criteria": [
            {"criterion": "Fibrillary deposits ~20nm (fibrillary GN) or microtubules >30nm (immunotactoid)", "essential": True},
            {"criterion": "Congo red negative", "essential": True},
            {"criterion": "IgG + C3 on IF (fibrillary)", "essential": False},
        ],
        "differential_diagnosis": ["amyloidosis", "membranous", "lupus", "cryoglobulinemic", "lightChainCastNephropathy"],
        "lab_findings": ["Proteinuria", "Hematuria", "eGFR reduced",
                          "Evaluate for monoclonal gammopathy (SPEP, IFE, FLC)"],
        "biopsy_findings": ["Randomly oriented fibrils ~20nm (fibrillary GN)", "Microtubules >30nm (immunotactoid)",
                            "Congo red negative", "IgG + C3 mesangial/GBM deposits"],
        "treatment_overview": "No established therapy. RAASi for proteinuria. Immunosuppression (steroids Â± cyclophosphamide) for progressive disease (limited evidence). Treat underlying monoclonal gammopathy in immunotactoid. Rituximab may have benefit.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP. Screen for malignancy/ monoclonal gammopathy at diagnosis and follow-up.",
        "complications": ["ESKD (50% at 5 years)", "Malignancy association (30%)"],
        "relapse_information": "Progressive disease. Post-transplant recurrence 30-50%.",
        "long_term_prognosis": "Poor. ESKD in 50% within 5 years. Immunotactoid may have better prognosis with targeted therapy.",
    },
    "thinBasementMembrane": {
        "name": "Thin Basement Membrane Nephropathy",
        "category": DiseaseCategory.HEREDITARY,
        "definition": "TBMD (benign familial hematuria) is a hereditary glomerular basement membrane disorder characterized by persistent hematuria and diffuse GBM thinning.",
        "epidemiology": "Most common cause of persistent microscopic hematuria (1-5% of population). Both sexes. All ages. Autosomal dominant (COL4A3/COL4A4 carriers).",
        "etiology": "Heterozygous mutation in COL4A3 or COL4A4 genes encoding type IV collagen Î±3/Î±4 chains. Carrier state for Alport syndrome.",
        "pathophysiology": "Reduced collagen IV Î±3/Î±4 chain production in GBM â†’ thin and fragile GBM â†’ mechanical fragility â†’ hematuria. Usually no progressive thickening or fibrosis.",
        "clinical_presentation": "Persistent microscopic hematuria (often incidental). Episodic macroscopic hematuria. Rarely proteinuria (usually <1g/day). Normal kidney function. Family history of hematuria.",
        "diagnostic_criteria": [
            {"criterion": "GBM thickness <250nm (adult) or <200nm (child)", "essential": True},
            {"criterion": "Persistent glomerular hematuria", "essential": True},
            {"criterion": "Family history of hematuria", "essential": False},
            {"criterion": "No extra-renal manifestations", "essential": False},
        ],
        "differential_diagnosis": ["alport", "iga", "infectionRelated", "mcd"],
        "lab_findings": ["Normal eGFR", "Hematuria (dysmorphic RBCs)", "Normal proteinuria or <1g/day",
                          "Normal C3/C4", "Normal hearing/vision"],
        "biopsy_findings": ["Diffuse GBM thinning on EM (<250nm)", "Normal light microscopy",
                            "Normal immunofluorescence", "No immune deposits"],
        "classification_systems": [{"name": "GBM Thickness Criteria", "components": "Adult <250nm, Child <200nm"}],
        "risk_stratification": [{"factor": "Proteinuria >1g/day", "risk": "Possibly Alport carrier"},
                                  {"factor": "Family history of ESKD", "risk": "Consider genetic testing"}],
        "treatment_overview": "No treatment required for isolated hematuria. RAASi if proteinuria develops. Avoid nephrotoxic drugs. Regular monitoring.",
        "monitoring_protocol": "Annual: BP, eGFR, urine dipstick. If proteinuria develops: 24h UTP, RAASi.",
        "complications": ["Rarely proteinuria", "Very rarely ESKD (<1%)"],
        "relapse_information": "Persistent condition, not relapsing. Excellent prognosis.",
        "long_term_prognosis": "Excellent. Normal life expectancy. ESKD rare (<1%). Differentiate from Alport syndrome.",
    },
    "alport": {
        "name": "Alport Syndrome",
        "category": DiseaseCategory.HEREDITARY,
        "definition": "Alport syndrome is a hereditary disorder of type IV collagen causing progressive nephropathy, sensorineural hearing loss, and ocular abnormalities.",
        "epidemiology": "Prevalence ~1/50,000. X-linked (85%, COL4A5), autosomal recessive (14%, COL4A3/COL4A4), autosomal dominant (1%). Males more severely affected.",
        "etiology": "Mutations in COL4A5 (X-linked), COL4A3 or COL4A4 (autosomal). Defective collagen IV network in GBM, cochlea, eye, and skin basement membranes.",
        "pathophysiology": "Abnormal type IV collagen â†’ structurally deficient GBM â†’ progressive GBM thickening, thinning, splitting, lamellation â†’ glomerulosclerosis. Similar process in cochlea (hearing loss) and eye (lenticonus, retinopathy).",
        "clinical_presentation": "Persistent hematuria (early childhood). Progressive proteinuria (adolescence). Hypertension. ESKD (males: 20-30s, females: 50-60s). Sensorineural hearing loss (high frequency). Anterior lenticonus, dot-and-fleck retinopathy.",
        "diagnostic_criteria": [
            {"criterion": "Characteristic GBM changes on EM (thickening, splitting, lamellation)", "essential": True},
            {"criterion": "COL4A5, COL4A3, or COL4A4 mutation", "essential": False},
            {"criterion": "Hematuria + hearing loss + ocular findings", "essential": False},
            {"criterion": "Family history of kidney disease or hearing loss", "essential": False},
        ],
        "differential_diagnosis": ["thinBasementMembrane", "iga", "membranous", "fsgs"],
        "lab_findings": ["Hematuria (early)", "Proteinuria (progressive)", "eGFR declining",
                          "Genetic testing confirms mutation"],
        "biopsy_findings": ["GBM thickening, thinning, splitting, lamellation (basket weave)",
                            "Absent or reduced collagen Î±5(IV) staining", "Progressive glomerulosclerosis"],
        "classification_systems": [
            {"name": "Inheritance Pattern", "components": "X-linked, autosomal recessive, autosomal dominant"},
            {"name": "Stage", "components": "Hematuria only, proteinuria, CKD, ESKD"},
        ],
        "risk_stratification": [{"factor": "Male gender (XLAS)", "risk": "Earlier ESKD"},
                                  {"factor": "Truncating COL4A5 mutation", "risk": "Early-onset ESKD"},
                                  {"factor": "Proteinuria >1g/day", "risk": "Progression"}],
        "treatment_overview": "RAASi from diagnosis (reduces proteinuria, slows progression). SGLT2i for additional protection. Avoid nephrotoxins. Hearing aids for hearing loss. Renal transplantation (no recurrence - COL4A5 is absent, not abnormal).",
        "monitoring_protocol": "Annual: eGFR, 24h UTP, BP, audiometry, ophthalmology. More frequent if proteinuria or declining eGFR.",
        "complications": ["ESKD", "Sensorineural hearing loss", "Anterior lenticonus",
                          "Aortic root dilation", "Leiomyomatosis (rare contiguous gene deletion)"],
        "relapse_information": "Progressive disease. No relapse post-transplant (kidney has normal collagen IV).",
        "long_term_prognosis": "XLAS male: ESKD by 20-40y. XLAS female: ESKD by 50-70y. ARAS: ESKD by 20-30y. ADAS: slower progression.",
    },
    # === New Secondary Glomerular Diseases ===
    "cryoglobulinemic": {
        "name": "Cryoglobulinemic Glomerulonephritis",
        "category": DiseaseCategory.SECONDARY,
        "definition": "Cryoglobulinemic GN is renal involvement in mixed cryoglobulinemia, most commonly associated with chronic HCV infection.",
        "epidemiology": "HCV-related in 80% of cases. Type I: monoclonal (MGUS/lymphoma). Type II: mixed monoclonal+polyclonal (HCV). Type III: polyclonal (autoimmune, infection).",
        "etiology": "HCV â†’ chronic B-cell stimulation â†’ IgM rheumatoid factor production â†’ cryoglobulin formation â†’ immune complex deposition. Other causes: HBV, HIV, SLE, Sjogren's, lymphoproliferative.",
        "pathophysiology": "Cryoglobulins (IgM rheumatoid factor + IgG + HCV RNA) deposit in glomeruli â†’ complement activation â†’ leukocytoclastic vasculitis â†’ membranoproliferative pattern + vasculitic lesions.",
        "clinical_presentation": "Palpable purpura (lower extremities), arthralgia, neuropathy. Hematuria, proteinuria, hypertension. RPGN in severe cases. Systemic vasculitis symptoms.",
        "diagnostic_criteria": [
            {"criterion": "Positive cryoglobulins (serum)", "essential": True},
            {"criterion": "MPGN pattern with IgG + IgM + C3 on IF", "essential": True},
            {"criterion": "Leukocytoclastic vasculitis on biopsy", "essential": False},
        ],
        "differential_diagnosis": ["lupus", "infectionRelated", "anca", "mpgn"],
        "lab_findings": ["Positive cryoglobulins", "Low C3, low C4 (classic)", "Rheumatoid factor positive",
                          "HCV antibody/PCR positive", "Hematuria, proteinuria"],
        "biopsy_findings": ["MPGN pattern", "IgG + IgM + C3 deposits (subendothelial)",
                            "Intracapillary thrombi (cryoglobulin precipitates) - PAS positive",
                            "Vasculitis in small arteries"],
        "treatment_overview": "Treat HCV (direct-acting antivirals) - can cause remission of cryoglobulinemia. Severe: rituximab + steroids Â± plasma exchange. Cyclophosphamide for refractory. Avoid interferon-based regimens.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP, C3/C4, RF, cryocrit. HCV viral load.",
        "complications": ["ESKD", "Systemic vasculitis", "Neuropathy", "Lymphoma (long-term)"],
        "relapse_information": "Relapse if HCV persists or reinfection. B-cell clonal persistence increases relapse risk.",
        "long_term_prognosis": "5-year kidney survival ~80% with DAA therapy. HCV cure improves outcomes.",
    },
    "hivan": {
        "name": "HIV-Associated Nephropathy",
        "category": DiseaseCategory.SECONDARY,
        "definition": "HIVAN is a collapsing form of FSGS occurring in HIV-infected patients, characterized by heavy proteinuria and rapid progression to ESKD.",
        "epidemiology": "HIVAN occurs almost exclusively in patients of African ancestry with APOL1 risk variants. Peak: 30-40 years. More common in males. Declining with ART.",
        "etiology": "HIV infection of renal epithelial cells + APOL1 G1/G2 risk alleles. APOL1 variants account for >70% of HIVAN risk.",
        "pathophysiology": "HIV directly infects renal tubular and glomerular epithelial cells â†’ cytopathic effect â†’ podocyte dedifferentiation â†’ collapsing FSGS. APOL1 risk variants increase susceptibility to HIV-induced podocyte injury. Immune dysregulation contributes.",
        "clinical_presentation": "Nephrotic-range proteinuria, rapidly declining eGFR, bland sediment. Kidneys often enlarged on ultrasound. Absence of edema despite nephrotic proteinuria.",
        "diagnostic_criteria": [
            {"criterion": "Collapsing FSGS on biopsy", "essential": True},
            {"criterion": "HIV positive", "essential": True},
            {"criterion": "Nephrotic-range proteinuria", "essential": False},
            {"criterion": "African ancestry with APOL1 risk", "essential": False},
        ],
        "differential_diagnosis": ["fsgs", "membranous", "lupus", "infectionRelated", "amyloidosis"],
        "lab_findings": ["Nephrotic-range proteinuria", "Rapidly declining eGFR", "Bland sediment",
                          "HIV PCR positive", "CD4 often low"],
        "biopsy_findings": ["Collapsing FSGS", "Podocyte hyperplasia", "Tubular microcysts",
                            "Interstitial inflammation", "APOL1 immunohistochemistry"],
        "treatment_overview": "Antiretroviral therapy (ART) is the cornerstone - reduces proteinuria and slows progression. RAASi for proteinuria. Corticosteroids for rapidly progressive (limited evidence). Renal replacement therapy when indicated.",
        "monitoring_protocol": "Monthly: eGFR, 24h UTP, CD4, HIV viral load during active disease. 3-monthly in remission.",
        "complications": ["ESKD (rapid, within months-years)", "Infection (immunosuppression)",
                          "Dialysis complications in HIV patients"],
        "relapse_information": "May improve with ART initiation but few achieve complete remission. Post-transplant: no recurrence (APOL1 risk in donor kidney matters).",
        "long_term_prognosis": "Pre-ART: ESKD within months. With ART: 5-year kidney survival ~50%. Renal transplantation successful.",
    },
    "drugInducedGn": {
        "name": "Drug-Induced Glomerulonephritis",
        "category": DiseaseCategory.SECONDARY,
        "definition": "Drug-induced GN encompasses various glomerular injury patterns caused by medications, including AIN, membranous, FSGS, ANCA vasculitis, and TMA.",
        "epidemiology": "Increasing recognition. Incidence depends on drug exposure. Common culprits: NSAIDs, antibiotics (beta-lactams), PPIs, lithium, interferon, bisphosphonates, chemotherapy agents.",
        "etiology": "Various drugs can induce GN through immune-mediated, toxic, or hypersensitivity mechanisms. NSAIDs: MCD-like or membranous. Lithium: MCD or FSGS. Interferon: FSGS (collapsing). Bisphosphonates: FSGS. Anti-TNF: proliferative GN.",
        "pathophysiology": "Drug-induced immune response or direct podocyte toxicity â†’ glomerular injury. Drug acts as hapten â†’ immune complex formation. Some drugs trigger ANCA production (hydralazine, PTU, cocaine).",
        "clinical_presentation": "Proteinuria, hematuria, AKI. May present weeks to years after drug exposure. Concurrent features: rash, fever, eosinophilia (AIN-dominant). ANCA-positive drug-induced vasculitis: +MPO antibody.",
        "diagnostic_criteria": [
            {"criterion": "Temporal relationship between drug exposure and renal disease", "essential": True},
            {"criterion": "Improvement after drug withdrawal", "essential": False},
            {"criterion": "Typical histologic pattern on biopsy", "essential": True},
            {"criterion": "Exclusion of other causes", "essential": True},
        ],
        "differential_diagnosis": ["mcd", "fsgs", "membranous", "acuteInterstitialNephritis", "anca"],
        "lab_findings": ["Hematuria", "Proteinuria", "eGFR reduced", "Eosinophilia (AIN)",
                          "Drug-induced ANCA (MPO positive)", "Urine eosinophils (AIN)"],
        "biopsy_findings": ["Variable: MCD, FSGS, membranous, AIN, or ANCA-GN pattern",
                            "Tubulointerstitial nephritis with eosinophils (AIN)",
                            "Collapsing FSGS (interferon, pamidronate)"],
        "treatment_overview": "Drug withdrawal is the primary treatment. Corticosteroids for severe AIN or drug-induced ANCA-GN. Supportive care + RAASi for persistent proteinuria. Most improve with drug cessation.",
        "monitoring_protocol": "Weekly initially: eGFR, 24h UTP. Monthly until stable.",
        "complications": ["Persistent CKD", "ESKD (rare with prompt recognition)"],
        "relapse_information": "Usually resolves with drug avoidance. Recurrence if drug re-exposed.",
        "long_term_prognosis": "Generally good if drug identified early. Most recover renal function. CKD may persist in cases with prolonged exposure.",
    },
    # === Transplant Diseases ===
    "antibodyMediatedRejection": {
        "name": "Antibody-Mediated Rejection",
        "category": DiseaseCategory.TRANSPLANT,
        "definition": "ABMR is a form of renal allograft rejection mediated by donor-specific antibodies (DSA) targeting HLA or other antigens on graft endothelium.",
        "epidemiology": "Occurs in 10-30% of kidney transplant recipients. Risk factors: pre-formed DSA, non-adherence, younger recipients, previous transplants.",
        "etiology": "Pre-existing (pre-formed) or de novo DSA (non-adherence, under-immunosuppression). DSA targets donor HLA class I/II or non-HLA antigens (AT1R, ETAR, collagen V).",
        "pathophysiology": "DSA binds to graft endothelial cells â†’ complement activation (C4d deposition) â†’ endothelial injury â†’ microvascular inflammation â†’ transplant glomerulopathy (chronic).",
        "clinical_presentation": "Acute: rising creatinine, oliguria, graft tenderness, fever. Chronic: gradual eGFR decline, proteinuria, hypertension.",
        "diagnostic_criteria": [
            {"criterion": "DSA positive", "essential": True},
            {"criterion": "Microvascular inflammation (peritubular capillaritis + glomerulitis)", "essential": True},
            {"criterion": "C4d positivity in peritubular capillaries", "essential": False},
            {"criterion": "Transplant glomerulopathy (chronic)", "essential": False},
        ],
        "differential_diagnosis": ["tCellMediatedRejection", "cniToxicity", "transplantGlomerulopathy", "bkVirusNephropathy"],
        "lab_findings": ["Rising creatinine", "DSA positive (HLA or non-HLA)", "Proteinuria",
                          "Hematuria"],
        "biopsy_findings": ["Microvascular inflammation (g+p>0)", "C4d positive (IHC/IF)",
                            "Transplant glomerulopathy (cg >0, chronic)",
                            "Peritubular capillary basement membrane multilayering (EM)"],
        "classification_systems": [
            {"name": "Banff Classification", "components": "Active ABMR, Chronic ABMR",
             "source": "Banff 2023"},
        ],
        "risk_stratification": [{"factor": "Pre-formed DSA", "risk": "Early ABMR"},
                                  {"factor": "De novo DSA", "risk": "Late ABMR"},
                                  {"factor": "C4d positive", "risk": "Active ABMR"},
                                  {"factor": "Transplant glomerulopathy", "risk": "Graft loss"}],
        "treatment_overview": "Acute: IVIG, plasma exchange, rituximab Â± bortezomib or carfilzomib. Steroid pulses. Optimize maintenance immunosuppression. Chronic: prevent further injury; no established reversal therapy.",
        "monitoring_protocol": "DSA monitoring at 3, 6, 12 months then annually. Graft biopsy when DSA positive or eGFR declines.",
        "complications": ["Graft loss (50% within 5 years of diagnosis)", "Infection (augmented immunosuppression)"],
        "relapse_information": "Persistent/recurrent ABMR is common without adequate treatment.",
        "long_term_prognosis": "5-year graft survival after ABMR diagnosis: ~50%. Chronic ABMR is leading cause of late graft loss.",
    },
    "tCellMediatedRejection": {
        "name": "T-Cell Mediated Rejection",
        "category": DiseaseCategory.TRANSPLANT,
        "definition": "TCMR is a form of renal allograft rejection mediated by recipient T lymphocytes infiltrating the graft interstitium and tubules.",
        "epidemiology": "Most common type of acute rejection. Incidence 10-20% in first year. Lower with modern immunosuppression.",
        "etiology": "Under-immunosuppression, non-adherence, reduced CNI exposure. Donor-recipient HLA mismatch. Sensitization (previous transplants, transfusions, pregnancies).",
        "pathophysiology": "Donor alloantigen presentation â†’ recipient T-cell activation â†’ clonal expansion â†’ graft infiltration â†’ tubulitis and interstitial inflammation â†’ tubular injury Â± arteritis.",
        "clinical_presentation": "Rising creatinine, oliguria, graft tenderness, fever. May be subclinical (biopsy-detected).",
        "diagnostic_criteria": [
            {"criterion": "Interstitial inflammation (>25% of cortex)", "essential": True},
            {"criterion": "Tubulitis (Banff t-score â‰¥2)", "essential": True},
            {"criterion": "Intimal arteritis (Banff v-score, in vascular rejection)", "essential": False},
        ],
        "differential_diagnosis": ["antibodyMediatedRejection", "cniToxicity", "acuteInterstitialNephritis", "bkVirusNephropathy"],
        "lab_findings": ["Rising creatinine", "No DSA (usually)", "Urine: sterile pyuria possible"],
        "biopsy_findings": ["Interstitial inflammation", "Tubulitis", "Intimal arteritis (v-score)",
                            "Negative C4d", "No transplant glomerulopathy"],
        "classification_systems": [
            {"name": "Banff Classification (TCMR)", "components": "Borderline, IA, IB, IIA, IIB, III",
             "source": "Banff 2023"},
        ],
        "risk_stratification": [{"factor": "Vascular involvement", "risk": "Worse graft survival"},
                                  {"factor": "Subclinical vs clinical", "risk": "Early detection improves outcomes"}],
        "treatment_overview": "Methylprednisolone pulse (500-1000mg IV x3) for Banff IA-IB. Anti-thymocyte globulin (rATG) for IIA-III or steroid-resistant. Optimize maintenance immunosuppression (CNI level target).",
        "monitoring_protocol": "Weekly eGFR during treatment. Consider surveillance biopsy after treatment.",
        "complications": ["Graft dysfunction", "Infection (augmented immunosuppression)", "Progression to IFTA"],
        "relapse_information": "Recurrence in 15-30% within first year after treated TCMR.",
        "long_term_prognosis": "Good if early and responds to treatment. Late TCMR or vascular involvement has worse prognosis.",
    },
    "cniToxicity": {
        "name": "Calcineurin Inhibitor Nephrotoxicity",
        "category": DiseaseCategory.TRANSPLANT,
        "definition": "CNI nephrotoxicity is progressive renal injury from chronic tacrolimus or ciclosporin use, characterized by arteriolar hyalinosis and tubulointerstitial fibrosis.",
        "epidemiology": "Universal exposure in transplant recipients. Acute: 10-30%. Chronic: >50% on biopsy at 5 years.",
        "etiology": "CNIs (tacrolimus, ciclosporin) cause afferent arteriolar vasoconstriction (acute) and progressive arteriolar hyalinosis + tubulointerstitial fibrosis (chronic). Dose-dependent, but toxicity can occur at therapeutic levels.",
        "pathophysiology": "Acute: CNI â†’ calcineurin inhibition in vascular smooth muscle â†’ vasoconstriction â†’ reduced RBF â†’ AKI. Chronic: CNI â†’ TGF-Î² activation â†’ endothelial injury â†’ arteriolar hyalinosis â†’ tubular atrophy â†’ interstitial fibrosis.",
        "clinical_presentation": "Acute: dose-dependent rise in creatinine, hyperkalemia, hypertension (may be reversible). Chronic: slow, progressive eGFR decline, hypertension, bland sediment.",
        "diagnostic_criteria": [
            {"criterion": "Arteriolar hyalinosis (afferent arteriolar nodular hyaline deposits)", "essential": True},
            {"criterion": "Striped tubulointerstitial fibrosis", "essential": False},
            {"criterion": "Temporal relationship to CNI exposure", "essential": True},
            {"criterion": "Exclusion of rejection or other causes", "essential": True},
        ],
        "differential_diagnosis": ["antibodyMediatedRejection", "tCellMediatedRejection", "transplantGlomerulopathy"],
        "lab_findings": ["Rising creatinine (gradual)", "CNI levels variable (may be therapeutic)",
                          "Hyperkalemia (type 4 RTA)", "Hypomagnesemia",
                          "Bland sediment", "No DSA"],
        "biopsy_findings": ["Arteriolar hyalinosis (nodular)", "Striped tubulointerstitial fibrosis",
                            "Tubular atrophy", "Isometric vacuolization of tubular cells (acute)",
                            "No significant glomerulitis or C4d"],
        "treatment_overview": "Reduce CNI dose or convert to CNI-free regimen (belatacept, mTOR inhibitor). Manage hypertension and proteinuria with RAASi. Avoid nephrotoxins.",
        "monitoring_protocol": "3-monthly: eGFR, CNI trough levels, BP, potassium, magnesium. Consider biopsy for unexplained eGFR decline.",
        "complications": ["Chronic graft dysfunction", "Graft loss", "Hypertension", "Post-transplant diabetes"],
        "relapse_information": "May improve with dose reduction (acute), but chronic changes are irreversible.",
        "long_term_prognosis": "Progressive if CNI continued. Conversion to CNI-free regimen may stabilize or slow progression.",
    },
    "transplantGlomerulopathy": {
        "name": "Transplant Glomerulopathy",
        "category": DiseaseCategory.TRANSPLANT,
        "definition": "TG is a morphologic pattern of chronic glomerular injury in renal allografts, characterized by GBM double contours and associated with chronic ABMR.",
        "epidemiology": "Prevalence 10-20% at 5 years post-transplant. Strongly associated with DSA. Leading cause of late graft loss.",
        "etiology": "Most commonly chronic ABMR (DSA-mediated). Can also occur in HCV infection, TMA, CNI toxicity.",
        "pathophysiology": "Chronic endothelial injury (DSA-mediated) â†’ loss of endothelial fenestrations â†’ new GBM deposition â†’ double contours (CG) â†’ progressive glomerulosclerosis.",
        "clinical_presentation": "Proteinuria (often nephrotic-range), hypertension, progressive eGFR decline. May have concurrent DSA positivity.",
        "diagnostic_criteria": [
            {"criterion": "GBM double contours by EM (>2 glomeruli)", "essential": True},
            {"criterion": "DSA positive", "essential": False},
            {"criterion": "C4d positive (may be negative in late/chronic)", "essential": False},
        ],
        "differential_diagnosis": ["antibodyMediatedRejection", "cniToxicity", "recurrentIgan"],
        "lab_findings": ["Proteinuria (to nephrotic range)", "eGFR declining", "DSA positive (70-80%)",
                          "Hematuria possible"],
        "biopsy_findings": ["GBM double contours (CG)", "Peritubular capillary multilayering (EM)",
                            "Glomerulosclerosis", "C4d positivity (variable)",
                            "Microvascular inflammation (may be minimal in late)"],
        "classification_systems": [
            {"name": "Banff CG Score", "components": "cg0-cg3 by % of capillaries affected",
             "source": "Banff 2023"},
        ],
        "risk_stratification": [{"factor": "DSA class II", "risk": "More aggressive"},
                                  {"factor": "crescents", "risk": "Rapid loss"},
                                  {"factor": "cg3 score", "risk": "Imminent graft loss"}],
        "treatment_overview": "No proven effective therapy. Augment immunosuppression (IVIG, rituximab) if DSA positive. Optimize BP and proteinuria management. Consider SGLT2i for proteinuria reduction. Prepare for dialysis/retransplant.",
        "monitoring_protocol": "3-monthly: eGFR, 24h UTP, DSA. Biopsy if progressing.",
        "complications": ["Graft loss (50% at 3 years after diagnosis)", "Nephrotic syndrome"],
        "relapse_information": "Progressive condition. No reversal reported.",
        "long_term_prognosis": "Poor. 50% graft loss within 3 years of diagnosis.",
    },
    "bkVirusNephropathy": {
        "name": "BK Virus Nephropathy",
        "category": DiseaseCategory.TRANSPLANT,
        "definition": "BKVN is a polyomavirus-associated nephropathy in kidney transplant recipients, causing progressive tubulointerstitial inflammation and graft dysfunction.",
        "epidemiology": "Affects 5-10% of kidney transplant recipients. Typically 3-12 months post-transplant. Risk: intense immunosuppression, older age, male gender, DGF, CMV infection.",
        "etiology": "Reactivation of BK polyomavirus from latent state in urothelium â†’ viral replication in tubular epithelium â†’ cytopathic injury â†’ interstitial nephritis â†’ fibrosis.",
        "pathophysiology": "BK virus infects renal tubular epithelial cells â†’ viral replication â†’ cell lysis â†’ viral shedding (decoy cells) â†’ interstitial inflammation â†’ tubular atrophy â†’ fibrosis. Nephropathy stage correlates with outcome.",
        "clinical_presentation": "Asymptomatic rise in creatinine. Urine decoy cells. BK viremia on PCR. May progress to graft dysfunction.",
        "diagnostic_criteria": [
            {"criterion": "BK viremia >10,000 copies/mL (screening threshold)", "essential": False},
            {"criterion": "SV40 positive tubular cells on biopsy", "essential": True},
            {"criterion": "Interstitial inflammation + viral cytopathic changes", "essential": True},
        ],
        "differential_diagnosis": ["tCellMediatedRejection", "antibodyMediatedRejection", "cniToxicity", "acuteInterstitialNephritis"],
        "lab_findings": ["BK PCR in blood (viremia)", "Decoy cells in urine", "Rising creatinine",
                          "SV40 immunohistochemistry positive on biopsy"],
        "biopsy_findings": ["SV40+ intranuclear inclusions in tubular epithelium", "Interstitial inflammation",
                            "Tubular atrophy/fibrosis", "May have concurrent TCMR"],
        "classification_systems": [
            {"name": "BKVN Classification", "components": "Stage A (<10% tubules), Stage B (11-50%), Stage C (>50%)",
             "source": "Banff 2023"},
        ],
        "risk_stratification": [{"factor": "BK viremia >10^5 copies", "risk": "BKVN"},
                                  {"factor": "Stage C on biopsy", "risk": "Poor graft survival"},
                                  {"factor": "Concurrent rejection", "risk": "Graft loss"}],
        "treatment_overview": "Reduce immunosuppression (CNI reduction, MMF reduction). Monitor BK viremia weekly. Adjuncts: cidofovir (limited), IVIG, fluoroquinolones (controversial). Leflunomide for persistent cases. Avoid anti-rejection treatment unless concurrent TCMR.",
        "monitoring_protocol": "Weekly BK viremia until clearance. Monthly for 6 months. Screening: monthly BK PCR first year.",
        "complications": ["Graft dysfunction/loss", "Concurrent acute rejection (management challenge)",
                          "Recurrence after treatment reduction"],
        "relapse_information": "Recurrence in 10-20% after initial clearance. May recur with increased immunosuppression.",
        "long_term_prognosis": "Stage A: 90% graft survival. Stage B: 60-70%. Stage C: <30%.",
    },
}


# â”€â”€â”€ NEW DISEASES: KB RULES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

NEW_DISEASE_RULES = {
    "alport": {
        "name": "Alport syndrome",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
        "rules": [
            (["feature", "hematuriaPersistent"], 3, "Persistent microscopic hematuria from childhood is a hallmark."),
            (["feature", "hearingLoss"], 4, "Sensorineural hearing loss (high-frequency) supports Alport syndrome."),
            (["feature", "lenticonus"], 5, "Anterior lenticonus is pathognomonic for Alport syndrome."),
            (["feature", "retinopathy"], 3, "Dot-and-fleck retinopathy is characteristic."),
            (["feature", "familyHistoryKidney"], 3, "Family history of kidney disease supports hereditary etiology."),
            (["feature", "familyHistoryHearing"], 2, "Family history of hearing loss is suggestive."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria develops progressively with age."),
            (["proteinuria", "nephrotic"], 1, "Nephrotic-range proteinuria can occur in advanced disease."),
            (["sediment", "hematuria"], 2, "Glomerular hematuria is the earliest sign."),
            (["feature", "maleGender"], 2, "X-linked Alport syndrome is more severe in males."),
        ],
    },
    "thinBasementMembrane": {
        "name": "Thin basement membrane nephropathy",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
        "rules": [
            (["feature", "hematuriaPersistent"], 3, "Persistent glomerular hematuria is the hallmark."),
            (["feature", "familyHistoryHematuria"], 3, "Family history of hematuria supports TBMD."),
            (["proteinuria", "subnephrotic"], -1, "Significant proteinuria is not typical of TBMD."),
            (["proteinuria", "nephrotic"], -2, "Nephrotic-range proteinuria suggests alternative diagnosis."),
            (["egfrTrend", "normal"], 1, "Normal kidney function is typical."),
            (["feature", "hearingLoss"], -1, "Hearing loss points to Alport syndrome rather than TBMD."),
            (["feature", "maleGender"], 0, "Both sexes equally affected."),
        ],
    },
    "cryoglobulinemic": {
        "name": "Cryoglobulinemic glomerulonephritis",
        "base": 0,
        "source_abbr": "ERA",
        "source_year": 2022,
        "source_title": "ERA 2022 Glomerular Disease Recommendations",
        "rules": [
            (["feature", "purpura"], 3, "Palpable purpura is a classic extra-renal manifestation."),
            (["feature", "arthralgia"], 2, "Arthralgia is common in mixed cryoglobulinemia."),
            (["feature", "neuropathy"], 2, "Peripheral neuropathy is a frequent extra-renal feature."),
            (["lab", "lowC3"], 3, "Low C3 is typical in cryoglobulinemic GN."),
            (["lab", "lowC4"], 4, "Very low C4 is characteristic of mixed cryoglobulinemia."),
            (["lab", "hepatitis"], 3, "HCV infection is the most common cause of mixed cryoglobulinemia."),
            (["sediment", "casts"], 2, "RBC casts indicate active GN."),
            (["proteinuria", "nephrotic"], 1, "Proteinuria can be nephrotic-range."),
            (["proteinuria", "subnephrotic"], 1, "Subnephrotic proteinuria is also common."),
        ],
    },
    "hivan": {
        "name": "HIV-associated nephropathy (HIVAN)",
        "base": 0,
        "source_abbr": "ERA",
        "source_year": 2022,
        "source_title": "ERA 2022 Glomerular Disease Recommendations",
        "rules": [
            (["feature", "hiv"], 5, "HIV infection is the defining risk factor."),
            (["proteinuria", "nephrotic"], 4, "Nephrotic-range proteinuria is typical."),
            (["egfrTrend", "rapidDecline"], 3, "Rapidly progressive loss of kidney function."),
            (["sediment", "bland"], 2, "Bland sediment despite heavy proteinuria."),
            (["feature", "africanAncestry"], 3, "Strongest risk factor: African ancestry with APOL1 variants."),
            (["feature", "edema"], -1, "Edema may be absent despite nephrotic proteinuria."),
        ],
    },
    "drugInducedGn": {
        "name": "Drug-induced glomerular disease",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
        "rules": [
            (["feature", "drugExposure"], 4, "Temporal relationship with drug exposure is key."),
            (["feature", "nsaidExposure"], 3, "NSAIDs can cause MCD, membranous, or AIN."),
            (["feature", "lithiumExposure"], 2, "Lithium can cause MCD or FSGS."),
            (["feature", "bisphosphonateExposure"], 2, "Bisphosphonates can cause collapsing FSGS."),
            (["feature", "interferonExposure"], 2, "Interferon therapy can cause FSGS or TMA."),
            (["feature", "checkpointInhibitorExposure"], 2, "Immune checkpoint inhibitors can cause AIN or GN."),
            (["feature", "rash"], 2, "Drug rash may accompany drug-induced renal disease."),
            (["feature", "eosinophilia"], 2, "Eosinophilia supports drug-induced AIN."),
            (["egfrTrend", "rapidDecline"], 2, "AKI pattern with drug exposure."),
        ],
    },
    "antibodyMediatedRejection": {
        "name": "Antibody-mediated rejection",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Transplant Recipient Guideline",
        "rules": [
            (["feature", "transplanted"], 5, "ABMR occurs only in transplant recipients."),
            (["feature", "dsaPositive"], 5, "Donor-specific antibody positive is a key feature."),
            (["egfrTrend", "rapidDecline"], 3, "Acute rise in creatinine can occur."),
            (["feature", "proteinuria"], 2, "Proteinuria can develop especially in chronic ABMR."),
            (["feature", "graftTenderness"], 2, "Graft tenderness and oliguria in acute ABMR."),
            (["feature", "nonAdherence"], 2, "Non-adherence to immunosuppression is a major risk factor."),
        ],
    },
    "tCellMediatedRejection": {
        "name": "T-cell mediated rejection",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Transplant Recipient Guideline",
        "rules": [
            (["feature", "transplanted"], 5, "TCMR occurs only in transplant recipients."),
            (["egfrTrend", "rapidDecline"], 3, "Acute creatinine rise is common."),
            (["feature", "graftTenderness"], 2, "Graft tenderness may be present."),
            (["feature", "fever"], 2, "Fever can accompany acute TCMR."),
            (["feature", "nonAdherence"], 2, "Non-adherence is a major risk factor."),
            (["feature", "dsaPositive"], -1, "DSA is typically negative in isolated TCMR."),
        ],
    },
    "cniToxicity": {
        "name": "Calcineurin inhibitor nephrotoxicity",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Transplant Recipient Guideline",
        "rules": [
            (["feature", "transplanted"], 3, "CNI toxicity occurs in transplant recipients on CNIs."),
            (["feature", "cniExposure"], 4, "Current or prior CNI therapy is the defining risk."),
            (["egfrTrend", "reduced"], 2, "Gradual eGFR decline over months to years."),
            (["lab", "hyperkalemia"], 2, "Type 4 renal tubular acidosis causes hyperkalemia."),
            (["lab", "hypomagnesemia"], 2, "CNI-induced magnesium wasting."),
            (["sediment", "bland"], 1, "Bland urinary sediment is typical."),
            (["feature", "hypertension"], 1, "CNI-induced hypertension is common."),
        ],
    },
    "transplantGlomerulopathy": {
        "name": "Transplant glomerulopathy",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Transplant Recipient Guideline",
        "rules": [
            (["feature", "transplanted"], 5, "TG occurs only in transplant recipients."),
            (["proteinuria", "nephrotic"], 3, "Nephrotic-range proteinuria is common."),
            (["egfrTrend", "reduced"], 3, "Progressive eGFR decline over months to years."),
            (["feature", "dsaPositive"], 3, "DSA positive in 70-80% of cases."),
            (["feature", "hypertension"], 2, "Hypertension is common."),
            (["sediment", "bland"], 1, "Bland sediment is typical."),
            (["sediment", "casts"], -1, "Active sediment is not characteristic."),
        ],
    },
    "bkVirusNephropathy": {
        "name": "BK virus nephropathy",
        "base": 0,
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Transplant Recipient Guideline",
        "rules": [
            (["feature", "transplanted"], 5, "BKVN occurs almost exclusively in kidney transplants."),
            (["lab", "bkViremia"], 5, "BK viremia >10,000 copies/mL is a screening threshold."),
            (["feature", "decoyCells"], 3, "Decoy cells in urine suggest BK reactivation."),
            (["egfrTrend", "rapidDecline"], 2, "Creatinine rise is a late sign."),
            (["feature", "intenseImmunosuppression"], 2, "Intense immunosuppression is the primary risk factor."),
        ],
    },
}


# â”€â”€â”€ CLINICAL PATHWAYS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PATHWAYS = {
    "iga": [
        {"stage_order": 1, "stage_name": "Presentation & Diagnosis",
         "description": "Hematuria workup, kidney biopsy for definitive diagnosis",
         "required_actions": ["Urine microscopy for RBC morphology and casts", "24h UTP (or ACR) quantification",
                              "eGFR, serum creatinine", "Kidney biopsy with IF",
                              "Oxford MEST-C scoring"], "next_stages": ["2"]},
        {"stage_order": 2, "stage_name": "Risk Stratification",
         "description": "Assess progression risk using proteinuria, eGFR, BP, MEST-C",
         "required_actions": ["Calculate 5-year ESKD risk (IgAN prediction tool)",
                              "Assess proteinuria >1g/day despite supportive care",
                              "Check BP control"], "next_stages": ["3", "5"]},
        {"stage_order": 3, "stage_name": "Supportive Therapy",
         "description": "Maximize RAASi + SGLT2i, control BP, manage proteinuria",
         "required_actions": ["RAASi (ACEi/ARB) titrated to max tolerated dose",
                              "SGLT2i if eGFR >25", "BP target <130/80"],
         "expected_duration_days": 90, "next_stages": ["4", "5"]},
        {"stage_order": 4, "stage_name": "Immunosuppression",
         "description": "For high-risk patients with persistent proteinuria >1g/day despite supportive care",
         "required_actions": ["Consider corticosteroid course (6-8 months)",
                              "Consider enteric budesonide for appropriate candidates",
                              "Consider sparsentan for persistent proteinuria"],
         "expected_duration_days": 180, "next_stages": ["5"]},
        {"stage_order": 5, "stage_name": "Long-term Monitoring",
         "description": "Regular follow-up with monitoring for progression",
         "required_actions": ["3-monthly eGFR, 24h UTP, BP",
                              "Monitor for treatment side effects",
                              "Prepare for RRT if ESKD approaches"],
         "expected_duration_days": 365, "next_stages": ["6"]},
        {"stage_order": 6, "stage_name": "ESKD / Transplantation",
         "description": "Renal replacement therapy and transplant evaluation",
         "required_actions": ["Dialysis access planning",
                              "Transplant evaluation",
                              "Discuss recurrence risk (10-50%)"],
         "expected_duration_days": 365, "next_stages": []},
    ],
}


class Command(BaseCommand):
    help = "Seed V4.0 medical knowledge expansion: diseases, guidelines, pathways, drugs"

    def add_arguments(self, parser):
        parser.add_argument("--diseases-only", action="store_true",
                            help="Only seed disease records, not rules/guidelines")
        parser.add_argument("--guidelines-only", action="store_true",
                            help="Only seed guideline sources")
        parser.add_argument("--rules-only", action="store_true",
                            help="Only seed new KB rules")
        parser.add_argument("--pathways-only", action="store_true",
                            help="Only seed clinical pathways")

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("guidelines_only"):
            self._seed_guidelines()
            return
        if options.get("diseases_only"):
            self._seed_diseases()
            return
        if options.get("rules_only"):
            self._seed_rules()
            return
        if options.get("pathways_only"):
            self._seed_pathways()
            return

        self._seed_guidelines()
        self._seed_diseases()
        self._seed_rules()
        self._seed_pathways()

    # â”€â”€ 1. Guideline Sources â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _seed_guidelines(self):
        count = 0
        for src in GUIDELINE_SOURCES:
            _, created = GuidelineSource.objects.get_or_create(
                abbreviation=src["abbr"],
                version_year=src["year"],
                defaults={
                    "title": src["title"],
                    "effective_date": date(src["year"], 7, 1),
                },
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} new guideline sources"))

    # â”€â”€ 2. Disease Records â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _seed_diseases(self):
        count = 0
        for disease_id, info in DISEASES.items():
            _, created = Disease.objects.update_or_create(
                id=disease_id,
                defaults={
                    "name": info["name"],
                    "category": info["category"],
                    "definition": info.get("definition", ""),
                    "epidemiology": info.get("epidemiology", ""),
                    "etiology": info.get("etiology", ""),
                    "pathophysiology": info.get("pathophysiology", ""),
                    "clinical_presentation": info.get("clinical_presentation", ""),
                    "diagnostic_criteria": info.get("diagnostic_criteria", []),
                    "differential_diagnosis": info.get("differential_diagnosis", []),
                    "lab_findings": info.get("lab_findings", []),
                    "biopsy_findings": info.get("biopsy_findings", []),
                    "classification_systems": info.get("classification_systems", []),
                    "risk_stratification": info.get("risk_stratification", []),
                    "treatment_overview": info.get("treatment_overview", ""),
                    "monitoring_protocol": info.get("monitoring_protocol", ""),
                    "complications": info.get("complications", []),
                    "relapse_information": info.get("relapse_information", ""),
                    "long_term_prognosis": info.get("long_term_prognosis", ""),
                    "is_active": True,
                },
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(
            f"Disease records: {Disease.objects.filter(is_active=True).count()} active diseases"
        ))

    # â”€â”€ 3. KB Rules for New Diseases â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _seed_rules(self):
        source_cache = {}
        seq = KnowledgeBaseEntry.objects.count()
        rule_count = 0
        for disease_id, profile in NEW_DISEASE_RULES.items():
            key = f"{profile['source_abbr']}-{profile['source_year']}"
            if key not in source_cache:
                source, _ = GuidelineSource.objects.get_or_create(
                    abbreviation=profile["source_abbr"],
                    version_year=profile["source_year"],
                    defaults={
                        "title": profile["source_title"],
                        "effective_date": date(profile["source_year"], 7, 1),
                    },
                )
                source_cache[key] = source

            for rule_path, weight, explanation in profile["rules"]:
                seq += 1
                entry_id = f"KB-{disease_id.upper()}-{seq:03d}"
                conditions = [{"field": rule_path[0], "operator": "eq", "value": rule_path[1]}]
                KnowledgeBaseEntry.objects.get_or_create(
                    entry_id=entry_id,
                    defaults={
                        "disease_id": disease_id,
                        "rule_data": {
                            "conditions": conditions,
                            "weight": weight,
                            "explanation": explanation,
                            "base_score": profile["base"],
                            "disease_name": profile["name"],
                        },
                        "source": source_cache[key],
                        "status": KnowledgeBaseEntry.Status.DRAFT,
                        "effective_date": date(profile["source_year"], 7, 1),
                    },
                )
                rule_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {rule_count} new KB rules across {len(NEW_DISEASE_RULES)} diseases"))

    # â”€â”€ 4. Clinical Pathways â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _seed_pathways(self):
        count = 0
        for disease_id, stages in PATHWAYS.items():
            try:
                disease = Disease.objects.get(id=disease_id)
            except Disease.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Disease {disease_id} not found, skipping pathways"))
                continue
            for stage in stages:
                _, created = ClinicalPathway.objects.update_or_create(
                    disease=disease,
                    stage_order=stage["stage_order"],
                    defaults={
                        "stage_id": f"{disease_id.upper()}-PATH-{stage['stage_order']:02d}",
                        "stage_name": stage["stage_name"],
                        "description": stage.get("description", ""),
                        "required_actions": stage.get("required_actions", []),
                        "expected_duration_days": stage.get("expected_duration_days"),
                        "next_stages": stage.get("next_stages", []),
                    },
                )
                if created:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} pathway stages"))


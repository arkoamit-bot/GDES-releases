"""Infection-related disease profiles: Infection-related GN, HBV-GN,
HCV-GN, HIVAN, Drug-induced GN.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "infectionRelated": {
        "disease_name": "Infection-Related Glomerulonephritis",
        "first_line": [
            {
                "drug": "Treat underlying infection",
                "dose": "Appropriate antimicrobial therapy",
                "duration": "Course appropriate to infection",
                "target": "Eradicate infection",
                "rationale": "Infection eradication is the cornerstone; GN often resolves after infection clears",
                "evidence_grade": "1",
            },
            {
                "drug": "Supportive care (RAAS blockade)",
                "dose": "ACEi/ARB as tolerated",
                "duration": "Ongoing",
                "target": "Proteinuria reduction, BP control",
                "rationale": "Symptomatic management while infection resolves",
                "evidence_grade": "2",
            },
        ],
        "second_line": [],
        "rescue_therapy": [],
        "contraindicated": ["Immunosuppression (active infection)", "Corticosteroids (unless post-streptococcal with nephrotic syndrome)"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "monthly until resolution", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range >3 months"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Improving", "action_threshold": "Worsening (consider alternative diagnosis)"},
            {"parameter": "Complement C3", "interval": "monthly", "target": "Normalizing", "action_threshold": "Persistent low C3 >3 months (consider alternative)"},
        ],
        "follow_up": {
            "induction_phase": "Monthly until infection eradicated",
            "resolution_phase": "Every 3 months for 1 year",
            "stable_remission": "Every 6 months for 2 years",
        },
    },
    "hbvAssociatedGN": {
        "disease_name": "HBV-Associated Glomerulonephritis",
        "first_line": [
            {
                "drug": "Antiviral therapy (entecavir or tenofovir)",
                "dose": "Entecavir 0.5mg daily or tenofovir alafenamide 25mg daily",
                "duration": "Lifelong or until HBeAg seroconversion and sustained viral suppression",
                "target": "Undetectable HBV DNA",
                "rationale": "KDIGO 2021: antiviral therapy is first-line for HBV-GN; viral suppression may lead to renal remission",
                "evidence_grade": "1",
            },
            {
                "drug": "RAS blockade for proteinuria",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Adjunctive for proteinuria control while antiviral therapy addresses the underlying cause",
                "evidence_grade": "2",
            },
        ],
        "second_line": [],
        "rescue_therapy": [
            {
                "drug": "Immunosuppression (only with viral suppression and specialist oversight)",
                "dose": "Per specific GN type protocol with close viral load monitoring",
                "duration": "Per GN protocol",
                "target": "Refractory nephrotic syndrome despite viral suppression",
                "rationale": "Immunosuppression may be considered if severe nephrotic syndrome persists despite adequate viral suppression; risk of viral reactivation",
                "evidence_grade": "OP",
                "conditions": "Documented viral suppression (undetectable HBV DNA) for ≥6 months; severe nephrotic syndrome refractory to antiviral therapy",
            },
        ],
        "contraindicated": [
            "Immunosuppression without antiviral coverage (risk of HBV reactivation and fulminant hepatitis)",
            "Interferon in decompensated cirrhosis",
        ],
        "monitoring": [
            {"parameter": "HBV DNA viral load", "interval": "every 1-3 months", "target": "Undetectable", "action_threshold": "Detectable or rising viral load"},
            {"parameter": "Liver function tests (ALT, AST, bilirubin)", "interval": "every 1-3 months", "target": "Normal ALT/AST", "action_threshold": "ALT >2× ULN or hepatitis flare"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly during antiviral initiation",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "hcvAssociatedGN": {
        "disease_name": "HCV-Associated Glomerulonephritis",
        "first_line": [
            {
                "drug": "Direct-acting antivirals (DAAs) for HCV",
                "dose": "Sofosbuvir/velpatasvir 400/100mg daily or glecaprevir/pibrentasvir per genotype and prior treatment",
                "duration": "8-12 weeks (per regimen)",
                "target": "Sustained virologic response (SVR, undetectable HCV RNA 12 weeks post-treatment)",
                "rationale": "KDIGO 2021: DAAs achieve SVR in >95% of HCV patients and may lead to GN remission, especially cryoglobulinemic GN",
                "evidence_grade": "1",
            },
            {
                "drug": "RAS blockade for proteinuria",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Adjunctive for proteinuria control during and after DAA therapy",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Rituximab for cryoglobulinemic vasculitis",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "4 weeks or 2 doses; repeat based on response",
                "target": "Resolution of cryoglobulinemic vasculitis symptoms",
                "rationale": "For persistent cryoglobulinemic manifestations (vasculitis, neuropathy, hypocomplementemia) despite DAA-induced SVR",
                "evidence_grade": "2",
            },
            {
                "drug": "Plasmapheresis for severe cryoglobulinemic disease",
                "dose": "1-1.5 plasma volumes × 3-5 sessions",
                "duration": "2-3 weeks",
                "target": "Reduce circulating cryoglobulins, control severe manifestations",
                "rationale": "Acute rescue for severe cryoglobulinemic vasculitis with organ-threatening manifestations",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Cyclophosphamide + corticosteroids for rapidly progressive GN",
                "dose": "Cyclophosphamide 2mg/kg/day (oral) or IV pulse per protocol + prednisolone 0.5-1mg/kg/day",
                "duration": "2-3 months",
                "target": "Control rapidly progressive GN component",
                "rationale": "Reserved for crescentic GN with rapid eGFR decline despite DAA therapy",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": [
            "Immunosuppression without DAA coverage (risk of HCV flare and progressive liver disease)",
            "Interferon-based therapy (obsolete; replaced by DAAs with superior efficacy and safety)",
        ],
        "monitoring": [
            {"parameter": "HCV RNA", "interval": "during and 12 weeks post-DAA, then every 6-12 months", "target": "Undetectable (SVR)", "action_threshold": "Detectable HCV RNA (treatment failure or relapse)"},
            {"parameter": "C4 complement level", "interval": "every 3-6 months", "target": "Normal C4", "action_threshold": "Persistent low C4 (cryoglobulinemia activity)"},
            {"parameter": "Cryocrit (if applicable)", "interval": "every 3-6 months during active cryoglobulinemia", "target": "Undetectable", "action_threshold": "Detectable or rising cryocrit"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly during DAA therapy",
            "maintenance_phase": "Every 3 months for first year post-SVR",
            "stable_remission": "Every 6-12 months",
        },
    },
    "hivan": {
        "disease_name": "HIV-Associated Nephropathy (HIVAN)",
        "first_line": [
            {
                "drug": "Antiretroviral therapy (ART)",
                "dose": "Per HIV guidelines; tenofovir alafenamide preferred over tenofovir disoproxil",
                "duration": "Lifelong",
                "target": "HIV viral load undetectable, CD4 >200, proteinuria reduction",
                "rationale": "ART is the cornerstone of HIVAN management; viral suppression halts renal decline",
                "evidence_grade": "1",
            },
            {
                "drug": "RAS blockade (ACEi or ARB)",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80, proteinuria reduction",
                "rationale": "Reduces proteinuria and slows CKD progression in HIVAN",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Corticosteroids",
                "dose": "Prednisolone 1 mg/kg/day (max 60 mg) with slow taper",
                "duration": "2-4 months with taper",
                "target": "Stabilize eGFR, reduce proteinuria",
                "rationale": "Consider in rapidly progressive HIVAN despite ART; limited evidence",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": [
            "Tenofovir disoproxil fumarate (higher nephrotoxicity risk; prefer TAF)",
            "High-dose corticosteroids without ART (risk of opportunistic infections)",
        ],
        "monitoring": [
            {"parameter": "HIV viral load & CD4 count", "interval": "every 1-3 months", "target": "Undetectable VL, CD4 >200", "action_threshold": "Detectable VL or CD4 decline"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<300 mg/g", "action_threshold": "Increasing proteinuria"},
            {"parameter": "eGFR", "interval": "every 1-3 months", "target": "Stable or improving", "action_threshold": "Decline >25% or >5 mL/min/1.73m2/year"},
            {"parameter": "ART adherence & tolerability", "interval": "at every visit", "target": "Full adherence", "action_threshold": "Non-adherence or drug toxicity"},
        ],
        "education": [
            "ART adherence is critical for renal and overall survival",
            "Avoid nephrotoxic medications including NSAIDs",
            "Monitor for immune reconstitution inflammatory syndrome when starting ART",
            "Contraception counseling for women of childbearing potential",
        ],
        "follow_up": {
            "induction_phase": "Every 1-3 months during initial ART",
            "maintenance_phase": "Every 3-6 months once stable",
            "long_term": "Lifelong nephrology and infectious disease follow-up",
        },
        "kdigo_reference": "KDIGO 2021 Glomerular Diseases Guideline — Chapter 11: HIV-Associated Nephropathy; KDIGO 2024 Diabetes Management in CKD Guideline (RAS blockade)",
    },
    "drugInducedGn": {
        "disease_name": "Drug-Induced Glomerular Disease",
        "first_line": [
            {
                "drug": "Discontinue offending agent",
                "dose": "Immediate withdrawal of suspected drug",
                "duration": "N/A",
                "target": "Resolution of renal injury",
                "rationale": "Removal of causative agent is the primary and most effective intervention",
                "evidence_grade": "1",
            },
            {
                "drug": "RAS blockade (ACEi or ARB)",
                "dose": "Standard doses titrated as tolerated",
                "duration": "Until proteinuria resolves",
                "target": "BP <130/80, proteinuria reduction",
                "rationale": "Supportive care for residual proteinuria after drug withdrawal",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Corticosteroids",
                "dose": "Prednisolone 0.5-1 mg/kg/day with taper over 4-12 weeks",
                "duration": "4-12 weeks depending on response",
                "target": "eGFR stabilization, proteinuria reduction",
                "rationale": "Consider for immune-mediated drug reactions (e.g., NSAID-induced MCD, lithium-induced FSGS)",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": [
            "Re-challenge with the same offending agent",
            "NSAIDs (if drug-induced disease, avoid all NSAIDs)",
        ],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 2-4 weeks initially, then monthly", "target": "Progressive reduction after drug withdrawal", "action_threshold": "No improvement at 4 weeks"},
            {"parameter": "eGFR", "interval": "every 2-4 weeks", "target": "Stable or improving", "action_threshold": "Continued decline after drug withdrawal"},
            {"parameter": "Blood pressure", "interval": "at each visit", "target": "<130/80 mmHg", "action_threshold": "Uncontrolled hypertension"},
        ],
        "education": [
            "Document the offending drug clearly in medical records to avoid re-exposure",
            "Report any new medications to the nephrology team",
            "Some drug-induced injuries may be irreversible if not recognized early",
            "Common culprits: NSAIDs, lithium, interferon, bisphosphonates, immune checkpoint inhibitors",
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks for first 3 months",
            "maintenance_phase": "Every 3 months for 1 year",
            "long_term": "Annual monitoring if residual CKD",
        },
        "kdigo_reference": "KDIGO 2021 Glomerular Diseases Guideline — Chapter 16: Drug-Induced Glomerular Disease; KDIGO 2024 Clinical Practice Guidelines for Drug-Induced Kidney Injury",
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

"""Autoimmune / inflammatory disease profiles: Lupus Nephritis, ANCA,
Anti-GBM, IgG4-Related KD, Sarcoidosis.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "lupus": {
        "disease_name": "Lupus Nephritis",
        "first_line": [
            {
                "drug": "Mycophenolate mofetil (MMF)",
                "dose": "2-3g/day in divided doses",
                "duration": "Minimum 3-6 months induction, then maintenance",
                "target": "Complete or partial remission (proteinuria <1g/day)",
                "rationale": "KDIGO 2024: MMF is first-line for Class III/IV lupus nephritis; ALMS trial showed non-inferiority to IV cyclophosphamide",
                "evidence_grade": "1",
            },
            {
                "drug": "Low-dose corticosteroids",
                "dose": "0.3-0.5mg/kg/day, taper to ≤7.5mg/day by 3 months",
                "duration": "Taper over 6-12 months",
                "target": "Minimize steroid exposure while controlling disease",
                "rationale": "KDIGO 2024: glucocorticoid-sparing approach; target ≤5mg/day maintenance",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "IV Cyclophosphamide (Euro-Lupus or NIH protocol)",
                "dose": "Euro-Lupus: 500mg IV every 2 weeks × 6 doses; NIH: 0.5-1g/m² monthly × 6",
                "duration": "3-6 months induction",
                "target": "Remission in severe/rapidly progressive LN",
                "rationale": "Reserved for severe cases (crescentic GN, rapid GFR decline) or MMF failure",
                "evidence_grade": "1",
            },
            {
                "drug": "Voclosporin (calcineurin inhibitor)",
                "dose": "23.7mg BID",
                "duration": "52 weeks",
                "target": "Complete remission as add-on to MMF",
                "rationale": "AURORA trial: voclosporin + MMF superior to MMF alone for complete remission",
                "evidence_grade": "1",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Rituximab",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "As needed",
                "target": "Refractory lupus nephritis",
                "rationale": "For refractory cases failing MMF and cyclophosphamide",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": ["NSAIDs (active LN)", "Aminoglycosides", "Methotrexate (if renal impairment)"],
        "monitoring": [
            {"parameter": "Anti-dsDNA titer", "interval": "every 1-3 months", "target": "Declining or undetectable", "action_threshold": "Rising titer (flare predictor)"},
            {"parameter": "Complement C3/C4", "interval": "every 1-3 months", "target": "Normal range", "action_threshold": "Declining or low"},
            {"parameter": "UPCR", "interval": "monthly during induction, quarterly maintenance", "target": "<0.5g/day", "action_threshold": ">1g/day"},
            {"parameter": "CBC with differential", "interval": "monthly on MMF/cyclophosphamide", "target": "WBC >3000, ANC >1500", "action_threshold": "Leukopenia/neutropenia"},
            {"parameter": "Liver function", "interval": "monthly on MMF", "target": "Normal", "action_threshold": "ALT >3× ULN"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "anca": {
        "disease_name": "ANCA-Associated Vasculitis",
        "first_line": [
            {
                "drug": "Rituximab (induction)",
                "dose": "375mg/m² weekly × 4 weeks",
                "duration": "4 weeks induction; may extend to 6 months for granulomatous disease",
                "target": "Remission (BVAS = 0)",
                "rationale": "RAVE and RITUXVAS trials: rituximab non-inferior to cyclophosphamide for induction; preferred for relapsing disease",
                "evidence_grade": "1",
            },
            {
                "drug": "Low-dose corticosteroids",
                "dose": "1mg/kg/day pred tapering to ≤5mg/day by 3-5 months (RAVE protocol)",
                "duration": "5-6 months",
                "target": "Disease control with minimized steroid exposure",
                "rationale": "PEXIVAS: reduced-dose steroid protocol is non-inferior with fewer infections",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "IV Cyclophosphamide",
                "dose": "15mg/kg every 2-3 weeks × 3-6 months (adjust for age/renal function)",
                "duration": "3-6 months",
                "target": "Remission in severe/rituximab-refractory AAV",
                "rationale": "Alternative to rituximab for severe disease (alveolar hemorrhage, rapidly declining GFR)",
                "evidence_grade": "1",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Plasma exchange (PLEX)",
                "dose": "6-7 sessions over 14 days",
                "duration": "2 weeks",
                "target": "Severe alveolar hemorrhage or creatinine >500 μmol/L",
                "rationale": "PEXIVAS: no overall benefit but may reduce ESKD in severe renal involvement; individualize for alveolar hemorrhage",
                "evidence_grade": "1",
            },
        ],
        "contraindicated": ["Aminoglycosides (ototoxicity risk)", "Live vaccines (immunosuppressed)"],
        "monitoring": [
            {"parameter": "ANCA titer (MPO/PR3)", "interval": "every 3 months", "target": "Declining", "action_threshold": "Rising titer (relapse predictor, not treatment trigger)"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly during induction, quarterly maintenance", "target": "Stable or improving", "action_threshold": ">20% decline"},
            {"parameter": "CBC with differential", "interval": "every 2 weeks during cyclophosphamide, monthly on rituximab", "target": "Normal", "action_threshold": "Lymphopenia <500 (infection risk)"},
            {"parameter": "Urine dipstick + 24h UTP (g/day)", "interval": "monthly", "target": "No active sediment", "action_threshold": "New hematuria or proteinuria"},
        ],
        "follow_up": {
            "induction_phase": "Weekly during rituximab, then every 2-4 weeks",
            "maintenance_phase": "Every 3-4 months (rituximab every 6 months)",
            "stable_remission": "Every 6 months",
        },
    },
    "antiGbm": {
        "disease_name": "Anti-GBM Disease",
        "first_line": [
            {
                "drug": "Plasma exchange + Cyclophosphamide + Corticosteroids (triple therapy)",
                "dose": "PLEX: daily for 14 days; Cyclophosphamide: 3mg/kg/day × 2-3 months; Prednisolone: 1mg/kg/day tapering over 3 months",
                "duration": "2-3 months intensive treatment",
                "target": "Clearance of anti-GBM antibodies, prevent ESKD",
                "rationale": "Standard of care for anti-GBM disease; early initiation critical — do not wait for biopsy if clinical picture is classic",
                "evidence_grade": "1",
                "conditions": "Emergency: initiate within 24 hours of presentation if anti-GBM positive",
            },
        ],
        "second_line": [],
        "rescue_therapy": [],
        "contraindicated": ["Any immunosuppression delay", "Plasma exchange in severe multiorgan failure (individualize)"],
        "monitoring": [
            {"parameter": "Anti-GBM antibody titer", "interval": "every 1-2 weeks during treatment", "target": "Undetectable", "action_threshold": "Persistent positive (continue PLEX)"},
            {"parameter": "Serum creatinine/eGFR", "interval": "daily during PLEX, then weekly", "target": "Stabilization", "action_threshold": "Dialysis requirement"},
            {"parameter": "CBC with differential", "interval": "weekly during cyclophosphamide", "target": "Normal", "action_threshold": "Leukopenia"},
        ],
        "follow_up": {
            "induction_phase": "Daily during PLEX, then weekly",
            "maintenance_phase": "Monthly for 12 months",
            "stable_remission": "Every 3 months for 2 years (watch for relapse)",
        },
    },
    "igg4Related": {
        "disease_name": "IgG4-Related Kidney Disease",
        "first_line": [
            {
                "drug": "Corticosteroids (prednisolone)",
                "dose": "0.6-1mg/kg/day (max 40-60mg/day), slow taper over 6-12 months",
                "duration": "6-12 months with gradual taper",
                "target": "Remission of renal and extra-renal IgG4-RD manifestations",
                "rationale": "KDIGO 2021: corticosteroids are first-line for IgG4-RD; most patients respond rapidly; slow taper reduces relapse",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil as steroid-sparing agent",
                "dose": "1.5-2g/day in divided doses",
                "duration": "12-24 months",
                "target": "Maintain remission with steroid minimization",
                "rationale": "For patients who relapse on steroid taper or cannot tolerate steroids; steroid-sparing role",
                "evidence_grade": "2",
            },
            {
                "drug": "Rituximab as steroid-sparing agent",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "2 doses; repeat based on relapse pattern",
                "target": "B-cell depletion, maintain remission",
                "rationale": "Emerging evidence for rituximab as steroid-sparing or relapse-prevention therapy in IgG4-RD",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Rituximab for refractory disease",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "Repeat based on relapse",
                "target": "Remission in steroid-refractory or relapsing IgG4-RD",
                "rationale": "Rituximab targets CD20+ B cells involved in IgG4 production; effective in refractory IgG4-RD",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": ["Avoid abrupt steroid cessation (relapse is common with rapid taper)"],
        "monitoring": [
            {"parameter": "Serum IgG4 level", "interval": "every 3-6 months", "target": "Normal IgG4 (<135 mg/dL)", "action_threshold": "Rising IgG4 despite treatment"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable eGFR", "action_threshold": ">20% decline"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "New or worsening proteinuria"},
            {"parameter": "Extra-renal IgG4-RD assessment (imaging, clinical)", "interval": "every 6-12 months", "target": "No new organ involvement", "action_threshold": "New or worsening extra-renal disease"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during steroid therapy",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "sarcoidosisAssociatedGN": {
        "disease_name": "Sarcoidosis-Associated Glomerulonephritis",
        "first_line": [
            {
                "drug": "Corticosteroids (prednisolone)",
                "dose": "0.5-1mg/kg/day (max 40-60mg/day), taper over 6-12 months",
                "duration": "6-12 months with gradual taper",
                "target": "Remission of renal and extra-renal sarcoidosis",
                "rationale": "KDIGO 2021: corticosteroids are first-line for symptomatic sarcoidosis including renal involvement; most patients respond well",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil as steroid-sparing agent",
                "dose": "1.5-2g/day in divided doses",
                "duration": "12-24 months",
                "target": "Maintain remission with steroid minimization",
                "rationale": "Steroid-sparing for relapsing or steroid-dependent sarcoidosis-associated GN",
                "evidence_grade": "2",
            },
            {
                "drug": "Methotrexate as steroid-sparing agent",
                "dose": "15-25mg weekly (oral or SC) with folic acid supplementation",
                "duration": "12-24 months",
                "target": "Maintain remission, steroid minimization",
                "rationale": "Alternative steroid-sparing agent for sarcoidosis; monitor for hepatotoxicity and bone marrow suppression",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Infliximab (anti-TNF biologic) for refractory disease",
                "dose": "3-5mg/kg IV at weeks 0, 2, 6, then every 8 weeks",
                "duration": "Ongoing if responsive; minimum 6 months",
                "target": "Remission in refractory sarcoidosis-associated GN",
                "rationale": "TNF-alpha plays a key role in granuloma formation; infliximab effective in refractory sarcoidosis",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": [
            "TNF inhibitors may cause paradoxical granulomatous inflammation in rare cases (monitor closely for new granulomatous lesions)",
        ],
        "monitoring": [
            {"parameter": "ACE level and lysozyme", "interval": "every 3-6 months", "target": "Normal ACE and lysozyme", "action_threshold": "Rising ACE or lysozyme (disease activity)"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable eGFR", "action_threshold": ">20% decline"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum calcium and 1,25-vitamin D", "interval": "every 3-6 months", "target": "Normal calcium", "action_threshold": "Hypercalcemia (active sarcoidosis)"},
            {"parameter": "Extra-renal sarcoidosis assessment (pulmonary, ocular, skin)", "interval": "every 6-12 months", "target": "No active disease", "action_threshold": "New or worsening extra-renal manifestations"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during steroid therapy",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

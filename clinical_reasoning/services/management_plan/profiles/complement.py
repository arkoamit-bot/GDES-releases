"""Complement-mediated disease profiles: C3 Glomerulopathy, MPGN,
Dense Deposit Disease, CFHR-Related Disease.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "c3": {
        "disease_name": "C3 Glomerulopathy",
        "first_line": [
            {
                "drug": "RAAS blockade (ACEi/ARB)",
                "dose": "Maximum tolerated dose",
                "duration": "Ongoing",
                "target": "Proteinuria <1g/day, BP control",
                "rationale": "Foundation for all C3G patients",
                "evidence_grade": "2",
            },
            {
                "drug": "Complement inhibitors (investigational — iptacopan, pegcetacoplan)",
                "dose": "Per clinical trial protocol",
                "duration": "Ongoing",
                "target": "Normalize complement activity, reduce proteinuria",
                "rationale": "APPEAR-C3G and other trials: complement inhibition targets alternative pathway dysregulation in C3G",
                "evidence_grade": "2",
                "conditions": "Clinical trial enrollment preferred; compassionate use if available",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil",
                "dose": "2g/day",
                "duration": "6-12 months trial",
                "target": "Proteinuria reduction, eGFR stabilization",
                "rationale": "May reduce complement-mediated inflammation; limited evidence",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Immunosuppression without complement pathway evaluation", "Plasma exchange (controversial)"],
        "monitoring": [
            {"parameter": "C3 level", "interval": "monthly", "target": "Normal range", "action_threshold": "Persistent low C3"},
            {"parameter": "24h UTP (g/day)", "interval": "monthly", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "mpgn": {
        "disease_name": "Membranoproliferative Glomerulonephritis (MPGN)",
        "first_line": [
            {
                "drug": "Treat underlying cause (HCV, infection, autoimmune)",
                "dose": "Etiology-directed antimicrobial/antiviral therapy",
                "duration": "Course appropriate to underlying condition",
                "target": "Eradicate or control underlying disease",
                "rationale": "MPGN pattern is a reaction to chronic immune complex deposition; treating the trigger is paramount",
                "evidence_grade": "1",
                "conditions": "Identifiable secondary cause (HCV, hepatitis B, endocarditis, autoimmune)",
            },
            {
                "drug": "Mycophenolate mofetil + corticosteroids (idiopathic MPGN)",
                "dose": "MMF 2g/day + prednisolone 0.5mg/kg/day tapering to 5-10mg/day",
                "duration": "12-24 months",
                "target": "Proteinuria reduction, eGFR stabilization",
                "rationale": "For idiopathic immune-complex-mediated MPGN without identifiable trigger; reduces complement-mediated inflammation",
                "evidence_grade": "OP",
            },
        ],
        "second_line": [
            {
                "drug": "Cyclophosphamide + corticosteroids",
                "dose": "Cyclophosphamide 2mg/kg/day + prednisolone 1mg/kg/day taper",
                "duration": "2-3 months, then transition to maintenance",
                "target": "Aggressive or rapidly progressive MPGN",
                "rationale": "Reserved for aggressive GN with crescents or rapidly declining renal function",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Complement C3/C4", "interval": "every 1-3 months", "target": "Normal range", "action_threshold": "Persistent hypocomplementemia"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80 mmHg", "action_threshold": ">140/90 mmHg"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "denseDepositDisease": {
        "disease_name": "Dense Deposit Disease (C3 Glomerulopathy)",
        "first_line": [
            {
                "drug": "Supportive care (RAAS blockade)",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "Proteinuria <1g/day, BP control",
                "rationale": "Foundation for all DDD patients; reduces intraglomerular pressure and proteinuria",
                "evidence_grade": "2",
            },
            {
                "drug": "Eculizumab (terminal complement inhibitor)",
                "dose": "900mg IV weekly × 4, then 1200mg every 2 weeks",
                "duration": "Ongoing if responsive",
                "target": "Stabilize or improve eGFR, reduce proteinuria",
                "rationale": "Blocks C5 cleavage; may benefit patients with progressive disease and documented alternative pathway activation",
                "evidence_grade": "2",
                "conditions": "Progressive disease (rising creatinine, worsening proteinuria despite supportive care)",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil + corticosteroids",
                "dose": "MMF 2g/day + prednisolone 0.5mg/kg/day tapering to 5-10mg/day",
                "duration": "12-24 months",
                "target": "Proteinuria reduction, eGFR stabilization",
                "rationale": "Alternative when eculizumab is unavailable or ineffective; reduces immune complex–mediated inflammation",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "C3 level", "interval": "every 1-3 months", "target": "Normal range", "action_threshold": "Persistent low C3"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80 mmHg", "action_threshold": ">140/90 mmHg"},
        ],
        "follow_up": {
            "induction_phase": "Monthly",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "cfhr": {
        "disease_name": "CFHR-Related Disease (C3 Glomerulopathy)",
        "first_line": [
            {
                "drug": "Supportive care (RAAS blockade + BP control)",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Foundation of management for CFHR-related C3 glomerulopathy",
                "evidence_grade": "2",
            },
            {
                "drug": "Eculizumab (terminal complement inhibitor)",
                "dose": "900mg IV weekly × 4, then 1200mg every 2 weeks",
                "duration": "Ongoing if responsive",
                "target": "Stabilize or improve eGFR, reduce proteinuria",
                "rationale": "Blocks terminal complement activation; may benefit patients with progressive disease and documented alternative pathway dysregulation",
                "evidence_grade": "2",
                "conditions": "Progressive disease with rising creatinine or worsening proteinuria despite supportive care",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil + corticosteroids",
                "dose": "MMF 2g/day + prednisolone 0.5mg/kg/day tapering to 5-10mg/day",
                "duration": "12-24 months",
                "target": "Proteinuria reduction, eGFR stabilization",
                "rationale": "Alternative when eculizumab is unavailable or ineffective",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Plasma exchange",
                "dose": "1-1.5 plasma volumes, 3-5 times/week for 2-3 weeks",
                "duration": "2-3 weeks",
                "target": "Remove pathogenic complement factors or autoantibodies",
                "rationale": "Limited evidence for acute rescue in severe CFHR-related disease; may reduce circulating pathogenic factors",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "C3 level", "interval": "every 1-3 months", "target": "Normal range", "action_threshold": "Persistent low C3"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Every 1-3 months",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

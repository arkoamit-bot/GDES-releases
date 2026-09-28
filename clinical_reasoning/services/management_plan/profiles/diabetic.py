"""Diabetic kidney disease profiles: DKD, DKD with superimposed GN.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "diabeticNephropathy": {
        "disease_name": "Diabetic Kidney Disease",
        "first_line": [
            {
                "drug": "RAS blockade (ACEi/ARB)",
                "dose": "Titrate to maximum tolerated dose",
                "duration": "Lifelong",
                "target": "BP <130/80 mmHg, albuminuria reduction",
                "rationale": "KDIGO 2021: RAS blockade is foundational for DKD with albuminuria",
                "evidence_grade": "1",
            },
            {
                "drug": "SGLT2 inhibitor (dapagliflozin/empagliflozin)",
                "dose": "10mg daily",
                "duration": "Lifelong",
                "target": "eGFR preservation, albuminuria reduction, cardiovascular benefit",
                "rationale": "DAPA-CKD and EMPA-KIDNEY: SGLT2 inhibitors reduce kidney disease progression in DKD independent of glycemic control",
                "evidence_grade": "1",
            },
            {
                "drug": "GLP-1 receptor agonist (semaglutide/dulaglutide)",
                "dose": "Semaglutide 0.25-1mg SC weekly or dulaglutide 1.5mg SC weekly",
                "duration": "Lifelong",
                "target": "Glycemic control, cardiovascular and renal protection",
                "rationale": "SUSTAIN-6 and REWIND: GLP-1 RA reduce MACE and slow CKD progression in DKD",
                "evidence_grade": "1",
            },
            {
                "drug": "Strict glycemic control",
                "dose": "HbA1c target <7% (individualized: <6.5% if no hypoglycemia risk, <8% if frail/advanced CKD)",
                "duration": "Ongoing",
                "target": "HbA1c <7%",
                "rationale": "Tight glycemic control reduces microvascular complications including nephropathy progression",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Finerenone (non-steroidal MRA)",
                "dose": "10mg daily (eGFR ≥60) or 20mg daily (eGFR 25-59)",
                "duration": "Lifelong",
                "target": "Reduce residual albuminuria, slow CKD progression",
                "rationale": "FIDELIO-DKD and FIGARO-DKD: finerenone reduces kidney and cardiovascular events in DKD with residual albuminuria on RAS blockade",
                "evidence_grade": "1",
                "conditions": "Persistent albuminuria (UACR ≥30 mg/g) despite maximum tolerated RAS blockade + SGLT2 inhibitor, serum K+ ≤5.0 mEq/L",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Renal replacement therapy (dialysis or transplantation)",
                "dose": "Per nephrology and transplant team protocol",
                "duration": "Lifelong",
                "target": "ESRD management",
                "rationale": "When eGFR <10-15 mL/min or symptomatic uremia; kidney transplant preferred over dialysis when feasible",
                "evidence_grade": "1",
                "conditions": "eGFR <10-15 mL/min or symptomatic uremia",
            },
        ],
        "contraindicated": ["Thiazolidinediones (fluid retention in CKD, risk of heart failure exacerbation)"],
        "monitoring": [
            {"parameter": "HbA1c", "interval": "every 3 months", "target": "<7% (individualized)", "action_threshold": ">8% or recurrent hypoglycemia"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable eGFR", "action_threshold": ">30% decline or >5 mL/min/year loss"},
            {"parameter": "UACR (urine albumin-to-creatinine ratio)", "interval": "every 3-6 months", "target": "<30 mg/g", "action_threshold": ">300 mg/g despite optimized therapy"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80 mmHg", "action_threshold": ">140/90 mmHg"},
            {"parameter": "Serum potassium", "interval": "1-2 weeks after ACEi/ARB/finerenone initiation, then every 3 months", "target": "3.5-5.0 mEq/L", "action_threshold": ">5.5 mEq/L"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during medication titration",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "diabeticNephropathyWithGN": {
        "disease_name": "Diabetic Kidney Disease with Superimposed Glomerulonephritis",
        "first_line": [
            {
                "drug": "Treat underlying GN per its own protocol + DKD standard care",
                "dose": "Per GN-specific regimen combined with RAS blockade + SGLT2 inhibitor for DKD",
                "duration": "Per GN protocol with ongoing DKD management",
                "target": "Control both the GN and DKD components",
                "rationale": "Superimposed GN in DKD requires treating both conditions simultaneously; renal biopsy essential for GN diagnosis",
                "evidence_grade": "2",
            },
            {
                "drug": "RAS blockade + SGLT2 inhibitor + GLP-1 RA (DKD foundation)",
                "dose": "As per DKD protocol",
                "duration": "Ongoing",
                "target": "BP <130/80, albuminuria reduction, eGFR preservation",
                "rationale": "Continued DKD management even when treating superimposed GN",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Immunosuppression per GN type (with caution for glycemic control)",
                "dose": "Per GN-specific protocol with reduced doses if high glycemic risk",
                "duration": "Per GN protocol",
                "target": "GN remission while maintaining glycemic control",
                "rationale": "Steroid-sparing regimens preferred (e.g., MMF over cyclophosphamide when possible); monitor blood glucose closely on steroids",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "As per underlying GN type",
                "dose": "Per GN-specific protocol",
                "duration": "Per GN protocol",
                "target": "Control refractory GN",
                "rationale": "Rescue therapy dictated by the specific GN histology on biopsy",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": ["High-dose steroids in uncontrolled diabetes (HbA1c >10%)"],
        "monitoring": [
            {"parameter": "Proteinuria/albuminuria", "interval": "monthly during immunosuppression", "target": "Reduction toward baseline", "action_threshold": "Worsening despite therapy"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "HbA1c", "interval": "every 1-3 months (more frequent on steroids)", "target": "<7%", "action_threshold": ">8% or steroid-induced hyperglycemia"},
            {"parameter": "Blood glucose (if on steroids)", "interval": "weekly during high-dose steroid therapy", "target": "<200 mg/dL fasting", "action_threshold": "Steroid diabetes"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during immunosuppression",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

"""Hereditary glomerular disease profiles: Alport Syndrome, Thin Basement
Membrane Nephropathy, Fabry Disease.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "alport": {
        "disease_name": "Alport Syndrome",
        "first_line": [
            {
                "drug": "ACE inhibitor (enalapril/lisinopril)",
                "dose": "Titrate to maximum tolerated dose",
                "duration": "Lifelong, start early even before proteinuria",
                "target": "BP <130/80 mmHg, proteinuria reduction, delay ESRD",
                "rationale": "KDIGO 2021: RAS blockade delays progression to ESRD in Alport syndrome; evidence strongest when started in childhood or early CKD",
                "evidence_grade": "1",
            },
            {
                "drug": "ARB (losartan/valsartan) if ACEi intolerant",
                "dose": "Titrate to maximum tolerated dose",
                "duration": "Lifelong",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Alternative RAS blockade when ACEi not tolerated (cough, angioedema)",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Aldosterone antagonist (spironolactone/eplerenone)",
                "dose": "Spironolactone 25-50mg daily or eplerenone 50mg daily",
                "duration": "Ongoing if proteinuria persists despite RAS blockade",
                "target": "Additional proteinuria reduction",
                "rationale": "Added benefit for residual proteinuria despite maximum RAS blockade; monitor potassium closely",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Renal transplantation",
                "dose": "Standard transplant protocol",
                "duration": "Lifelong graft with immunosuppression",
                "target": "Renal replacement; disease does NOT recur post-transplant",
                "rationale": "Alport syndrome does not recur in the allograft; anti-GBM antibodies may develop post-transplant (10-15%) but usually transient",
                "evidence_grade": "1",
            },
        ],
        "contraindicated": ["NSAIDs (accelerate CKD progression)"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 3-6 months", "target": "<0.5g/day", "action_threshold": "Rising proteinuria despite RAS blockade"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 3-6 months", "target": "Stable eGFR", "action_threshold": ">20% decline"},
            {"parameter": "Hearing assessment", "interval": "every 6-12 months", "target": "Stable hearing", "action_threshold": "New sensorineural hearing loss"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80 mmHg", "action_threshold": ">140/90 mmHg"},
        ],
        "follow_up": {
            "induction_phase": "Every 3 months",
            "maintenance_phase": "Every 3-6 months",
            "stable_remission": "Every 6 months",
        },
    },
    "thinBasementMembrane": {
        "disease_name": "Thin Basement Membrane Nephropathy",
        "first_line": [
            {
                "drug": "Reassurance and monitoring",
                "dose": "N/A",
                "duration": "Ongoing",
                "target": "Benign prognosis; maintain stable renal function",
                "rationale": "KDIGO 2021: TBMN is a benign condition with persistent microscopic hematuria; rarely progresses to CKD",
                "evidence_grade": "1",
            },
            {
                "drug": "ACE inhibitor/ARB (if hypertension or proteinuria develops)",
                "dose": "Titrate to maximum tolerated dose",
                "duration": "Ongoing if indicated",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "RAS blockade for secondary hypertension or proteinuria, which is uncommon in isolated TBMN",
                "evidence_grade": "2",
            },
        ],
        "second_line": [],
        "rescue_therapy": [],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "Blood pressure", "interval": "annually", "target": "<130/80 mmHg", "action_threshold": "Hypertension"},
            {"parameter": "Urinalysis (hematuria)", "interval": "annually", "target": "Stable microscopic hematuria", "action_threshold": "New proteinuria or macroscopic hematuria"},
        ],
        "follow_up": {
            "induction_phase": "Annually",
            "maintenance_phase": "Annually",
            "stable_remission": "Annually",
        },
    },
    "fabry": {
        "disease_name": "Fabry Disease",
        "first_line": [
            {
                "drug": "Enzyme replacement therapy (agalsidase alfa/beta)",
                "dose": "Agalsidase alfa 0.2mg/kg IV every 2 weeks or agalsidase beta 1.0mg/kg IV every 2 weeks",
                "duration": "Lifelong",
                "target": "Reduce globotriaosylceramide (Gb3) deposition, stabilize eGFR, reduce pain",
                "rationale": "KDIGO 2021: ERT is standard of care for Fabry disease with renal involvement; early initiation preserves renal function",
                "evidence_grade": "1",
            },
            {
                "drug": "Migalastat (chaperone therapy)",
                "dose": "123mg oral every other day",
                "duration": "Lifelong",
                "target": "Stabilize renal function, reduce Gb3 accumulation",
                "rationale": "Oral chaperone that stabilizes mutant alpha-galactosidase A; only effective for amenable GLA mutations (~50% of patients)",
                "evidence_grade": "1",
                "conditions": "Confirmed amenable GLA mutation on genetic testing",
            },
        ],
        "second_line": [
            {
                "drug": "RAS blockade for residual proteinuria",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "Proteinuria reduction, BP control",
                "rationale": "Adjunctive therapy for residual proteinuria despite ERT; does not replace ERT",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Kidney transplantation",
                "dose": "Standard transplant protocol",
                "duration": "Lifelong graft with immunosuppression; ERT continues post-transplant",
                "target": "Renal replacement for ESRD",
                "rationale": "Transplant provides excellent outcomes in Fabry disease; ERT must continue as the transplanted kidney does not produce alpha-GAL A",
                "evidence_grade": "1",
            },
        ],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "Lyso-Gb3 (globotriaosylsphingosine)", "interval": "every 6-12 months", "target": "Reduction toward normal on ERT", "action_threshold": "Rising Lyso-Gb3 despite ERT"},
            {"parameter": "24h UTP (g/day)", "interval": "every 3-6 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 3-6 months", "target": "Stable eGFR", "action_threshold": ">20% decline"},
            {"parameter": "Cardiac assessment (ECG, echo)", "interval": "every 12 months", "target": "No LVH progression, normal conduction", "action_threshold": "New LVH, conduction abnormality, arrhythmia"},
            {"parameter": "Pain symptoms (neuropathic pain score)", "interval": "every 6-12 months", "target": "Controlled pain", "action_threshold": "Worsening neuropathic pain"},
        ],
        "follow_up": {
            "induction_phase": "Every 3 months during ERT initiation",
            "maintenance_phase": "Every 6 months",
            "stable_remission": "Every 6-12 months",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

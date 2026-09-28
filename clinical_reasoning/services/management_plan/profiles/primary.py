"""Primary glomerular disease profiles: IgA Nephropathy, Membranous,
Minimal Change Disease, FSGS.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "iga": {
        "disease_name": "IgA Nephropathy",
        "first_line": [
            {
                "drug": "Supportive care (RAAS blockade)",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80, proteinuria <1g/day",
                "rationale": "KDIGO 2021: RAAS blockade is foundational for all IgAN patients with proteinuria >0.5g/day",
                "evidence_grade": "1",
            },
            {
                "drug": "SGLT2 inhibitor (dapagliflozin/empagliflozin)",
                "dose": "10mg daily",
                "duration": "Ongoing",
                "target": "eGFR preservation, proteinuria reduction",
                "rationale": "DAPA-CKD and EMPA-KIDNEY trials demonstrated benefit in non-diabetic CKD including IgAN",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Sparsentan (dual endothelin/angiotensin receptor antagonist)",
                "dose": "400mg daily",
                "duration": "24 weeks minimum",
                "target": "Proteinuria reduction ≥50%",
                "rationale": "PROTECT trial: superior proteinuria reduction vs irbesartan in IgAN",
                "evidence_grade": "1",
            },
            {
                "drug": "Hydroxychloroquine",
                "dose": "200-400mg daily (max 5mg/kg)",
                "duration": "6-12 months trial",
                "target": "Proteinuria reduction",
                "rationale": "IgAN-CQ trial: reduced proteinuria in Chinese patients with IgAN",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Targeted-release budesonide (Nefecon)",
                "dose": "16 mg/day (4 × 4 mg capsules) — fixed dose, no taper",
                "duration": "9 months",
                "target": "Proteinuria reduction, eGFR preservation for high-risk IgAN",
                "rationale": "NefIgArd Phase 3: TRF-budesonide 16 mg/day for 9 months reduced UPCR by 27% and preserved eGFR (5.05 mL/min benefit at 2 years, p<0.0001). KDIGO 2024 recommends for persistent proteinuria >1 g/day despite ≥90 days optimized RAASi.",
                "evidence_grade": "1",
                "conditions": "Proteinuria >1 g/day despite ≥3 months optimized supportive care (RAASi + SGLT2i), eGFR ≥30 mL/min",
            },
        ],
        "contraindicated": ["NSAIDs (active disease)", "Aminoglycosides"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "monthly during active phase, quarterly in remission", "target": "<0.5g/day", "action_threshold": ">1g/day"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly during active phase, quarterly in remission", "target": "Stable or improving", "action_threshold": ">20% decline"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80 mmHg", "action_threshold": ">140/90 mmHg"},
            {"parameter": "Serum potassium", "interval": "1-2 weeks after ACEi/ARB initiation, then quarterly", "target": "3.5-5.0 mEq/L", "action_threshold": ">5.5 mEq/L"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "membranous": {
        "disease_name": "Membranous Nephropathy",
        "first_line": [
            {
                "drug": "Rituximab",
                "dose": "1000mg IV on day 1 and day 15",
                "duration": "2 doses; repeat if partial response at 6 months",
                "target": "Complete remission (proteinuria <0.3g/day)",
                "rationale": "MENTOR trial: rituximab non-inferior to cyclosporine with better safety; KDIGO 2021 recommends as first-line for PLA2R+ MN",
                "evidence_grade": "1",
                "conditions": "PLA2R antibody positive, nephrotic syndrome",
            },
            {
                "drug": "Supportive care (RAAS blockade + diuretics)",
                "dose": "ACEi/ARB titrated; furosemide as needed for edema",
                "duration": "Ongoing",
                "target": "BP <130/80, edema control, proteinuria reduction",
                "rationale": "Foundation of management for all MN patients",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Cyclophosphamide + corticosteroids (Ponticelli protocol)",
                "dose": "Alternating monthly: IV methylprednisolone 1g × 3 days then oral pred 0.5mg/kg/d × 27 days; oral cyclophosphamide 2mg/kg/d × 30 days",
                "duration": "6 months (3 cycles each)",
                "target": "Complete remission",
                "rationale": "Classic regimen with 60-70% complete remission rate; reserved for high-risk or rituximab failure",
                "evidence_grade": "1",
            },
            {
                "drug": "Calcineurin inhibitor (tacrolimus/ciclosporin)",
                "dose": "Tacrolimus: 0.05-0.075mg/kg BID, target trough 4-8 ng/mL",
                "duration": "12-24 months with slow taper",
                "target": "Partial or complete remission",
                "rationale": "Alternative when rituximab and cyclophosphamide are contraindicated; higher relapse rate on withdrawal",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Rituximab (re-dosing after initial failure)",
                "dose": "1000mg IV × 2 doses, consider third dose at 6 months",
                "duration": "As needed based on PLA2R titer",
                "target": "PLA2R titer normalization",
                "rationale": "Repeat rituximab for incomplete response; PLA2R-guided treatment",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": ["NSAIDs (nephrotic range)", "Aminoglycosides"],
        "monitoring": [
            {"parameter": "PLA2R antibody titer", "interval": "every 3-6 months", "target": "Undetectable", "action_threshold": "Rising titer or persistent positive"},
            {"parameter": "24h UTP (g/day)", "interval": "monthly during treatment, quarterly in remission", "target": "<0.3g/day (complete remission)", "action_threshold": ">3.5g/day or >50% increase"},
            {"parameter": "Serum albumin", "interval": "monthly", "target": ">3.0 g/dL", "action_threshold": "<2.5 g/dL"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "mcd": {
        "disease_name": "Minimal Change Disease",
        "first_line": [
            {
                "drug": "Prednisolone",
                "dose": "1mg/kg/day (max 80mg) for adults; 2mg/kg/day (max 60mg) for children",
                "duration": "Minimum 4 weeks, extend to 16 weeks until complete remission, then taper",
                "target": "Complete remission (proteinuria <0.3g/day)",
                "rationale": "KDIGO 2021: corticosteroids are first-line for adult MCD; most patients achieve CR within 16 weeks",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Rituximab (steroid-dependent/relapsing)",
                "dose": "375mg/m² IV × 1-4 doses",
                "duration": "As needed for relapse prevention",
                "target": "Sustained remission off steroids",
                "rationale": "Emerging evidence for rituximab in steroid-dependent MCD to avoid cumulative steroid toxicity",
                "evidence_grade": "2",
            },
            {
                "drug": "Calcineurin inhibitor (ciclosporin/tacrolimus)",
                "dose": "Ciclosporin 3-5mg/kg BID or tacrolimus 0.05-0.1mg/kg BID",
                "duration": "12-24 months with slow taper",
                "target": "Remission with steroid minimization",
                "rationale": "Second-line for steroid-dependent/relapsing MCD",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Cyclophosphamide",
                "dose": "2-2.5mg/kg/day for 8-12 weeks (max cumulative dose 200mg/kg)",
                "duration": "8-12 weeks",
                "target": "Durable remission in frequently relapsing MCD",
                "rationale": "Reserved for patients failing CNI and rituximab; risk of gonadal toxicity limits use",
                "evidence_grade": "2",
            },
        ],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "weekly during induction, then monthly", "target": "<0.3g/day", "action_threshold": "Relapse (nephrotic range proteinuria)"},
            {"parameter": "Serum albumin", "interval": "monthly", "target": ">3.5 g/dL", "action_threshold": "<3.0 g/dL"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly during steroid therapy", "target": "Stable", "action_threshold": ">20% decline (consider FSGS)"},
            {"parameter": "Blood glucose (on steroids)", "interval": "weekly during high-dose steroids", "target": "<200 mg/dL", "action_threshold": "Steroid diabetes"},
        ],
        "follow_up": {
            "induction_phase": "Weekly for first month, then every 2-4 weeks",
            "taper_phase": "Every 2-4 weeks during taper",
            "stable_remission": "Every 3-6 months",
        },
    },
    "fsgs": {
        "disease_name": "Focal Segmental Glomerulosclerosis",
        "first_line": [
            {
                "drug": "Prednisolone (for primary FSGS)",
                "dose": "1mg/kg/day (max 80mg)",
                "duration": "Minimum 16 weeks (extend to 24 weeks if slow response)",
                "target": "Complete remission (proteinuria <0.3g/day)",
                "rationale": "KDIGO 2021: corticosteroids remain first-line for primary FSGS; slow responders should continue to 24 weeks before declaring resistance",
                "evidence_grade": "1",
            },
            {
                "drug": "RAAS blockade (ACEi/ARB)",
                "dose": "Titrate to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80, proteinuria reduction",
                "rationale": "Foundational for all FSGS patients, including secondary FSGS",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Calcineurin inhibitor (tacrolimus)",
                "dose": "0.05-0.075mg/kg BID, target trough 4-8 ng/mL",
                "duration": "12-24 months",
                "target": "Remission in steroid-resistant FSGS",
                "rationale": "Best evidence for steroid-resistant FSGS; calcineurin inhibitors have direct podocyte-stabilizing effects",
                "evidence_grade": "1",
            },
            {
                "drug": "Rituximab",
                "dose": "375mg/m² × 1-4 doses",
                "duration": "As needed",
                "target": "Remission in steroid-resistant/dependent FSGS",
                "rationale": "Emerging evidence; may be considered in steroid-resistant cases",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "ACTH gel (tetracosactide)",
                "dose": "1mg IM 3 times/week",
                "duration": "6-12 months",
                "target": "Remission in refractory FSGS",
                "rationale": "May work through melanocortin receptor on podocytes; limited evidence",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": ["NSAIDs (nephrotic range)", "Aminoglycosides"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "monthly", "target": "<0.3g/day", "action_threshold": "Nephrotic range proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Blood pressure", "interval": "every visit", "target": "<130/80", "action_threshold": ">140/90"},
            {"parameter": "Drug levels (if on CNI)", "interval": "weekly until stable, then monthly", "target": "Trough 4-8 ng/mL", "action_threshold": "Below therapeutic range"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
}

# Auto-register on import
for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

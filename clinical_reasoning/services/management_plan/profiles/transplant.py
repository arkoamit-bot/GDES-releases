"""Transplant-related disease profiles: Recurrent IgAN, Recurrent FSGS,
Recurrent MN, Transplant Glomerulopathy, AMR, TCMR, CNI Toxicity, BK Virus.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "recurrentIgaNephropathy": {
        "disease_name": "Recurrent IgA Nephropathy Post-Transplant",
        "first_line": [
            {
                "drug": "Optimize RAS blockade + BP control",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Lifelong post-transplant",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Foundation of management for recurrent IgAN in the allograft; RAS blockade reduces proteinuria and may slow progression",
                "evidence_grade": "2",
            },
            {
                "drug": "Steroid pulse for progressive disease",
                "dose": "IV methylprednisolone 250-500mg/day × 3 days, then oral prednisolone taper",
                "duration": "3 days IV, then oral taper over 3-6 months",
                "target": "Stabilize graft function, reduce proteinuria",
                "rationale": "May stabilize or improve graft function in progressive recurrent IgAN; often combined with optimization of immunosuppression",
                "evidence_grade": "OP",
                "conditions": "Progressive proteinuria or declining eGFR with biopsy-confirmed recurrent IgAN",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil",
                "dose": "1.5-2g/day in divided doses",
                "duration": "12-24 months",
                "target": "Reduce mesangial IgA deposition and proteinuria",
                "rationale": "Limited evidence for MMF in recurrent IgAN; may reduce mesangial proliferation and proteinuria",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Excessive immunosuppression without biopsy confirmation of recurrence"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months post-transplant", "target": "<0.5g/day", "action_threshold": "Rising proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months post-transplant", "target": "Stable graft function", "action_threshold": ">20% decline or rising trend"},
            {"parameter": "Urinalysis (hematuria)", "interval": "every 1-3 months post-transplant", "target": "No hematuria", "action_threshold": "New microscopic hematuria"},
        ],
        "follow_up": {
            "induction_phase": "Monthly for first 3 months post-transplant",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "recurrentFSGS": {
        "disease_name": "Recurrent FSGS Post-Transplant",
        "first_line": [
            {
                "drug": "Plasmapheresis (start early)",
                "dose": "1-1.5 plasma volumes daily or every other day",
                "duration": "Start within 24-48 hours of proteinuria onset; continue until remission (typically 6-12 sessions)",
                "target": "Remission of nephrotic syndrome (proteinuria <1g/day)",
                "rationale": "KDIGO 2021: early plasmapheresis is critical for recurrent FSGS; delaying treatment worsens outcomes",
                "evidence_grade": "1",
                "conditions": "Sudden-onset nephrotic-range proteinuria post-transplant, often within days to weeks of transplantation",
            },
            {
                "drug": "RAS blockade",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing post-transplant",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Adjunctive for proteinuria control alongside plasmapheresis",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Rituximab (if plasmapheresis response incomplete)",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "4 weeks or 2 doses; repeat based on response",
                "target": "B-cell depletion, complete remission",
                "rationale": "Added when plasmapheresis alone achieves only partial response; may reduce circulating permeability factors",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Higher-intensity plasmapheresis + cyclophosphamide",
                "dose": "Daily plasmapheresis + cyclophosphamide 2-2.5mg/kg/day",
                "duration": "2-4 weeks of intensive therapy",
                "target": "Remission in refractory recurrent FSGS",
                "rationale": "For severe refractory cases failing standard plasmapheresis; higher treatment intensity and immunosuppression",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": ["Delaying plasmapheresis in sudden severe recurrence (worsens graft outcomes)"],
        "monitoring": [
            {"parameter": "24h UTP (g/day, daily during acute phase)", "interval": "daily during acute phase, then weekly → monthly", "target": "<0.5g/day", "action_threshold": "Nephrotic range proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable graft function", "action_threshold": ">20% decline"},
            {"parameter": "Serum albumin", "interval": "weekly during acute phase", "target": ">3.5 g/dL", "action_threshold": "<3.0 g/dL (nephrotic hypoalbuminemia)"},
        ],
        "follow_up": {
            "induction_phase": "Daily during plasmapheresis, then every 1-2 weeks",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "recurrentMembranous": {
        "disease_name": "Recurrent Membranous Nephropathy Post-Transplant",
        "first_line": [
            {
                "drug": "RAS blockade",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing post-transplant",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Foundation of management for recurrent membranous nephropathy in the allograft",
                "evidence_grade": "2",
            },
            {
                "drug": "Rituximab for persistent nephrotic syndrome",
                "dose": "1000mg IV on day 1 and day 15",
                "duration": "2 doses; repeat at 6 months if partial response",
                "target": "Complete remission (proteinuria <0.3g/day)",
                "rationale": "Emerging evidence for rituximab in recurrent MN; targets the same pathogenic mechanism (anti-PLA2R) as native disease",
                "evidence_grade": "2",
                "conditions": "PLA2R antibody-positive recurrent MN with nephrotic syndrome",
            },
        ],
        "second_line": [
            {
                "drug": "Cyclophosphamide + corticosteroids for severe progressive disease",
                "dose": "Cyclophosphamide 2mg/kg/day + prednisolone 0.5-1mg/kg/day with taper",
                "duration": "2-3 months",
                "target": "Control progressive MN in the graft",
                "rationale": "For severe recurrent MN with progressive graft dysfunction failing rituximab",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Calcineurin inhibitor optimization",
                "dose": "Optimize tacrolimus trough to higher range (8-12 ng/mL) or add cyclosporine",
                "duration": "Variable, with monitoring",
                "target": "Stabilize graft function",
                "rationale": "CNIs have anti-proteinuric effects and may provide immunosuppressive benefit; optimize CNI exposure",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "PLA2R antibody titer", "interval": "every 1-3 months", "target": "Undetectable or declining", "action_threshold": "Rising PLA2R titer (disease activity)"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.3g/day", "action_threshold": "Nephrotic range proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable graft function", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly for first 3 months post-transplant",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "transplantGlomerulopathy": {
        "disease_name": "Transplant Glomerulopathy",
        "first_line": [
            {
                "drug": "Optimize immunosuppression",
                "dose": "Increase maintenance immunosuppression (higher CNI trough, optimize MMF dose)",
                "duration": "Ongoing",
                "target": "Prevent further graft injury from chronic antibody-mediated processes",
                "rationale": "KDIGO 2021: optimize immunosuppression to reduce ongoing immune-mediated graft injury in transplant glomerulopathy",
                "evidence_grade": "2",
            },
            {
                "drug": "RAS blockade for proteinuria",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Reduces proteinuria and may slow transplant glomerulopathy progression",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Treat active rejection if present on biopsy",
                "dose": "Per rejection type: pulse steroids for TCMR, plasmapheresis + IVIG for AMR",
                "duration": "Per rejection protocol",
                "target": "Resolution of active rejection component",
                "rationale": "If biopsy shows active rejection alongside transplant glomerulopathy, treat the acute component",
                "evidence_grade": "2",
            },
            {
                "drug": "Eculizumab for C4d+ with DSA (experimental)",
                "dose": "900mg IV weekly × 4, then 1200mg every 2 weeks",
                "duration": "Ongoing if responsive",
                "target": "Block complement-mediated graft injury",
                "rationale": "Experimental approach for C4d-positive transplant glomerulopathy with DSA; limited evidence",
                "evidence_grade": "OP",
                "conditions": "C4d-positive, DSA-positive transplant glomerulopathy with documented complement activation",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Over-immunosuppression without evidence of rejection (increases infection and malignancy risk)"],
        "monitoring": [
            {"parameter": "DSA (donor-specific antibodies)", "interval": "every 1-3 months", "target": "Low or negative MFI", "action_threshold": "Rising DSA MFI or new DSA"},
            {"parameter": "C4d staining (protocol biopsy if indicated)", "interval": "per protocol or if clinically indicated", "target": "C4d negative", "action_threshold": "C4d positivity on biopsy"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Rising proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable graft function", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "antibodyMediatedRejection": {
        "disease_name": "Antibody-Mediated Rejection (AMR)",
        "first_line": [
            {
                "drug": "Plasmapheresis + IVIG + pulse methylprednisolone",
                "dose": "Plasmapheresis 1-1.5 plasma volumes × 5-7 sessions; IVIG 100mg/kg after each PP session; methylprednisolone 250-500mg IV × 3 days",
                "duration": "5-7 plasmapheresis sessions over 2-3 weeks",
                "target": "Reduce DSA titers, stabilize graft function",
                "rationale": "Standard first-line for acute AMR: plasmapheresis removes DSA, IVIG modulates immune response, steroids reduce inflammation",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Rituximab for persistent DSA",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "4 weeks or 2 doses; repeat based on DSA response",
                "target": "B-cell depletion, reduce DSA production",
                "rationale": "Added when DSA persists despite plasmapheresis and IVIG; targets B-cell antibody production",
                "evidence_grade": "2",
            },
            {
                "drug": "Eculizumab for severe AMR",
                "dose": "900mg IV weekly × 4, then 1200mg every 2 weeks",
                "duration": "Ongoing if responsive",
                "target": "Block complement-mediated graft injury",
                "rationale": "For severe AMR with complement activation (C4d+); blocks terminal complement pathway",
                "evidence_grade": "2",
                "conditions": "Severe AMR with graft dysfunction despite plasmapheresis + IVIG; C4d-positive biopsy",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Bortezomib (plasma cell depletion) for refractory AMR",
                "dose": "1.3mg/m² SC on days 1, 4, 8, 11 of 21-day cycle",
                "duration": "2-4 cycles",
                "target": "Plasma cell depletion, reduce antibody production",
                "rationale": "Bortezomib targets proteasome-dependent plasma cells; for refractory AMR with high DSA despite standard therapy",
                "evidence_grade": "OP",
                "conditions": "Refractory AMR with high DSA despite plasmapheresis + IVIG + rituximab",
            },
        ],
        "contraindicated": ["T cell-depleting agents alone (e.g., ATG alone) — insufficient for antibody-mediated process"],
        "monitoring": [
            {"parameter": "DSA titers (MFI)", "interval": "weekly during acute phase, then monthly", "target": "Declining or negative MFI", "action_threshold": "Rising or persistent high MFI DSA"},
            {"parameter": "C4d staining (biopsy)", "interval": "as indicated clinically", "target": "C4d negative", "action_threshold": "Persistent C4d positivity"},
            {"parameter": "Serum creatinine/eGFR", "interval": "weekly during acute phase, then monthly", "target": "Stable or improving graft function", "action_threshold": "Further decline despite treatment"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Rising proteinuria"},
            {"parameter": "Graft biopsy", "interval": "as indicated (repeat biopsy to assess treatment response)", "target": "Resolution of microvascular inflammation and C4d", "action_threshold": "Persistent histologic AMR features"},
        ],
        "follow_up": {
            "induction_phase": "Weekly during acute treatment phase",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "tCellMediatedRejection": {
        "disease_name": "T Cell-Mediated Rejection (TCMR)",
        "first_line": [
            {
                "drug": "Pulse methylprednisolone",
                "dose": "250-500mg IV daily × 3 days",
                "duration": "3 days, followed by oral prednisolone taper",
                "target": "Resolution of Banff inflammatory lesions, stabilize graft function",
                "rationale": "Standard first-line for acute TCMR (Banff ≥IA); pulse steroids reduce T-cell-mediated graft inflammation",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Anti-thymocyte globulin (rATG) for steroid-resistant TCMR",
                "dose": "1.5mg/kg/day IV × 7-14 days",
                "duration": "7-14 days",
                "target": "Resolution of rejection in steroid-resistant Banff ≥IIA TCMR",
                "rationale": "For Banff ≥IIA TCMR refractory to pulse steroids; depletes T cells to halt rejection",
                "evidence_grade": "1",
                "conditions": "Steroid-resistant Banff ≥IIA TCMR on protocol or for-cause biopsy",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "Basiliximab or alemtuzumab for refractory TCMR (rare)",
                "dose": "Basiliximab 20mg IV on days 0 and 4; alemtuzumab 30mg IV × 1-2 doses",
                "duration": "1-2 doses",
                "target": "Resolution of refractory TCMR",
                "rationale": "For TCMR refractory to both steroids and rATG; rarely needed",
                "evidence_grade": "OP",
            },
        ],
        "contraindicated": ["Steroid minimization or withdrawal during acute TCMR (worsens rejection)"],
        "monitoring": [
            {"parameter": "Serum creatinine/eGFR", "interval": "daily during acute phase, then weekly → monthly", "target": "Stable or improving graft function", "action_threshold": "Further decline despite treatment"},
            {"parameter": "Graft biopsy (if indicated)", "interval": "repeat biopsy to assess response if no improvement by day 7", "target": "Resolution of interstitial inflammation and tubulitis", "action_threshold": "Persistent Banff lesions"},
            {"parameter": "DSA (rule out concurrent AMR)", "interval": "at time of rejection diagnosis", "target": "Negative or stable DSA", "action_threshold": "Concurrent DSA positivity (mixed rejection)"},
        ],
        "follow_up": {
            "induction_phase": "Daily during pulse steroids, then weekly",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "cniToxicity": {
        "disease_name": "Calcineurin Inhibitor (CNI) Nephrotoxicity",
        "first_line": [
            {
                "drug": "CNI dose reduction or conversion",
                "dose": "Reduce tacrolimus target trough by 25-50% or convert to belatacept/mTOR inhibitor",
                "duration": "Ongoing with monitoring",
                "target": "Reduce CNI exposure while maintaining adequate immunosuppression",
                "rationale": "KDIGO 2021: CNI dose reduction is first-line for CNI nephrotoxicity; aim for lowest effective trough level",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Everolimus (mTOR inhibitor) + reduced CNI",
                "dose": "Everolimus 0.75mg BID, target trough 3-8 ng/mL; reduce tacrolimus trough by 50%",
                "duration": "Ongoing with monitoring",
                "target": "Maintain immunosuppression with lower CNI exposure",
                "rationale": "Everolimus allows CNI minimization while maintaining rejection prophylaxis; monitor for proteinuria and wound healing complications",
                "evidence_grade": "2",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["mTOR inhibitor (everolimus/sirolimus) if significant proteinuria (>1 g/d) — may worsen proteinuria"],
        "monitoring": [
            {"parameter": "CNI trough levels (tacrolimus/cyclosporine)", "interval": "weekly during dose adjustment, then monthly", "target": "Lowest effective trough (e.g., tacrolimus 3-5 ng/mL for CNI minimization)", "action_threshold": "Trough above target or subtherapeutic levels"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable or improving eGFR after CNI reduction", "action_threshold": "Continued decline despite CNI reduction"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Rising proteinuria (especially on mTOR inhibitor)"},
            {"parameter": "Graft biopsy for chronic changes (if indicated)", "interval": "as clinically indicated", "target": "Assess for CNI arteriolopathy, IF/TA", "action_threshold": "Progressive chronic allograft nephropathy"},
        ],
        "follow_up": {
            "induction_phase": "Weekly during CNI dose adjustment",
            "maintenance_phase": "Every 1-3 months",
            "stable_remission": "Every 3-6 months",
        },
    },
    "bkVirusNephropathy": {
        "disease_name": "BK Virus Nephropathy",
        "first_line": [
            {
                "drug": "Reduce immunosuppression",
                "dose": "Reduce CNI target trough by 50%; stop or reduce MMF/azathioprine by 50-100%",
                "duration": "Ongoing until viral clearance; typically 2-6 months",
                "target": "BK viral load clearance or significant reduction",
                "rationale": "KDIGO 2021: reduction of immunosuppression is the cornerstone of BKVN management; balance rejection risk vs. viral clearance",
                "evidence_grade": "1",
            },
        ],
        "second_line": [
            {
                "drug": "Leflunomide (if viral load persists after immunosuppression reduction)",
                "dose": "Loading dose 100mg daily × 3 days, then 20-60mg daily (target teriflunomide level 50-100 mcg/mL)",
                "duration": "3-6 months",
                "target": "BK viral load clearance",
                "rationale": "Leflunomide has both immunosuppressive and antiviral properties; alternative when immunosuppression reduction alone fails",
                "evidence_grade": "OP",
            },
            {
                "drug": "Low-dose cidofovir (if viral load persists)",
                "dose": "0.25-0.5mg/kg IV every 1-2 weeks (with probenecid and hydration)",
                "duration": "4-8 weeks",
                "target": "BK viral load clearance",
                "rationale": "Low-dose cidofovir has anti-BKV activity; nephrotoxicity risk requires careful monitoring",
                "evidence_grade": "OP",
                "conditions": "Persistent BKV viremia despite immunosuppression reduction and leflunomide; requires close eGFR monitoring",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "IVIG for persistent viremia with graft dysfunction",
                "dose": "2g/kg IV over 2-5 days",
                "duration": "1-2 doses",
                "target": "BK viral load reduction, stabilize graft function",
                "rationale": "IVIG may provide passive anti-viral immunity and immunomodulation; limited evidence",
                "evidence_grade": "OP",
                "conditions": "Persistent BKV viremia with graft dysfunction despite immunosuppression reduction",
            },
        ],
        "contraindicated": [
            "Over-reduction of immunosuppression causing acute rejection",
            "Cidofovir in standard doses (nephrotoxic; only low doses used for BKVN)",
        ],
        "monitoring": [
            {"parameter": "BK viral load (quantitative PCR)", "interval": "weekly during active viremia, then every 1-2 weeks", "target": "Undetectable or <1000 copies/mL", "action_threshold": "Rising BK viral load or persistent viremia >10,000 copies/mL"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-2 weeks during treatment", "target": "Stable graft function", "action_threshold": "Declining eGFR (consider graft biopsy)"},
            {"parameter": "Urine decoy cells", "interval": "monthly", "target": "Absence of decoy cells", "action_threshold": "Positive decoy cells (screening marker)"},
        ],
        "follow_up": {
            "induction_phase": "Weekly during active viremia",
            "maintenance_phase": "Every 1-2 weeks until viral clearance, then monthly",
            "stable_remission": "Every 3 months for first year",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

"""Rare glomerular disease profiles: MGRS, Amyloidosis, Cryoglobulinemic GN,
Immunotactoid GN, Fibrillary GN, Paraneoplastic GN.
"""
from __future__ import annotations

from ..registry import ProfileRegistry

PROFILES: dict = {
    "mgrs": {
        "disease_name": "Monoclonal Gammopathy of Renal Significance (MGRS)",
        "first_line": [
            {
                "drug": "Clone-directed therapy (hematology-led)",
                "dose": "Daratumumab- or bortezomib-based regimen per hematologic protocol",
                "duration": "Per hematologic response (typically 4-6 cycles minimum)",
                "target": "Hematologic complete response (normal free light chain ratio)",
                "rationale": "MGRS is driven by the nephrotoxic monoclonal immunoglobulin; clone suppression is the only disease-modifying therapy",
                "evidence_grade": "2",
                "conditions": "Confirmed nephrotoxic monoclonal immunoglobulin by renal biopsy; requires hematology collaboration",
            },
            {
                "drug": "RAAS blockade",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "Proteinuria reduction, BP control",
                "rationale": "Adjunctive for proteinuria control while awaiting hematologic response",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Alkylator-based regimens",
                "dose": "Cyclophosphamide or bendamustine-based protocol per hematology",
                "duration": "Per protocol (typically 4-6 cycles)",
                "target": "Deep hematologic response in refractory cases",
                "rationale": "For clones refractory to proteasome inhibitor–based therapy",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Corticosteroids alone (ineffective for underlying clone; may mask disease progression)"],
        "monitoring": [
            {"parameter": "Serum free light chains (FLC)", "interval": "every 1-3 months", "target": "Normal FLC ratio (0.26-1.65)", "action_threshold": "Abnormal or rising ratio"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "Improving", "action_threshold": "Worsening proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Hematologic response assessment", "interval": "every 3 months during treatment", "target": "Complete hematologic response", "action_threshold": "Non-response at 3 months"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "amyloidosis": {
        "disease_name": "Renal Amyloidosis",
        "first_line": [
            {
                "drug": "Daratumumab + cyclophosphamide + bortezomib + dexamethasone (AL amyloidosis)",
                "dose": "Daratumumab 1800mg SC weekly × 8 wk, then every 2 wk × 16 wk, then every 4 wk; CyBorD backbone per hematologic protocol",
                "duration": "Minimum 6 cycles, extend per response",
                "target": "Hematologic complete response (NT-proBNP reduction, normal FLC ratio)",
                "rationale": "DARA-CyBorD achieves higher hematologic response rates than CyBorD alone in AL amyloidosis (ANDROMEDA trial)",
                "evidence_grade": "1",
                "conditions": "Biopsy-proven AL amyloidosis with renal involvement; requires hematology collaboration",
            },
            {
                "drug": "Treat underlying inflammatory condition (AA amyloidosis)",
                "dose": "Disease-appropriate anti-inflammatory or immunosuppressive therapy",
                "duration": "Long-term, guided by underlying disease",
                "target": "Suppression of SAA production, renal function stabilization",
                "rationale": "AA amyloidosis is driven by chronic inflammation; controlling the source halts amyloid deposition",
                "evidence_grade": "2",
                "conditions": "Biopsy-proven AA amyloidosis with identifiable inflammatory etiology (RA, IBD, chronic infection)",
            },
        ],
        "second_line": [
            {
                "drug": "High-dose melphalan + autologous stem cell transplant (AL amyloidosis)",
                "dose": "Melphalan 200mg/m² (adjust for cardiac/renal staging) with ASCT",
                "duration": "Inpatient; engraftment typically 2-3 weeks",
                "target": "Deep and durable hematologic complete response",
                "rationale": "Highest CR rate (~40%) but limited to early-stage patients (Mayo Stage I/II) with adequate organ function",
                "evidence_grade": "2",
                "conditions": "Mayo cardiac stage I or II, age <70, adequate performance status, no major cardiac involvement",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["High-dose corticosteroids in AL amyloidosis (infection risk in immunocompromised with organ dysfunction)"],
        "monitoring": [
            {"parameter": "Cardiac biomarkers (NT-proBNP, troponin)", "interval": "every 1-3 months", "target": "Declining or stable", "action_threshold": "Rising NT-proBNP >30% (cardiac progression)"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "Improving", "action_threshold": "Worsening proteinuria"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Serum free light chains (FLC)", "interval": "every 1-3 months during treatment", "target": "Normal ratio", "action_threshold": "Abnormal or rising ratio"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 3-6 months (long-term surveillance for relapse)",
        },
    },
    "cryoglobulinemic": {
        "disease_name": "Cryoglobulinemic Glomerulonephritis",
        "first_line": [
            {
                "drug": "Direct-acting antivirals (HCV-associated)",
                "dose": "Sofosbuvir/velpatasvir or glecaprevir/pibrentasvir per hepatology",
                "duration": "8-12 weeks",
                "target": "Sustained virologic response (SVR)",
                "rationale": "HCV eradication is curative in most cryoglobulinemic GN; DAAs have replaced interferon-based regimens",
                "evidence_grade": "1",
                "conditions": "HCV RNA positive; initiate nephrology and hepatology co-management",
            },
            {
                "drug": "Rituximab + corticosteroids (idiopathic or refractory after DAA)",
                "dose": "Rituximab 375mg/m² × 4 weekly doses + prednisolone 0.5mg/kg/day taper",
                "duration": "4 weeks induction, then assess response",
                "target": "Resolution of cryoglobulinemia, proteinuria reduction",
                "rationale": "Depletes B-cell clone producing cryoglobulins; used when HCV-negative or persistent disease after SVR",
                "evidence_grade": "2",
            },
            {
                "drug": "Plasmapheresis + rituximab (severe/critical disease)",
                "dose": "PLEX every other day × 5-7 sessions + rituximab 375mg/m² × 4 weekly doses",
                "duration": "2-3 weeks intensive phase",
                "target": "Rapid reduction of pathogenic cryoglobulins; prevent organ damage",
                "rationale": "Combination removes circulating cryoglobulins while rituximab suppresses production; for severe GN, vasculitis, or alveolar hemorrhage",
                "evidence_grade": "2",
                "conditions": "Severe disease with rapidly progressive GN, severe vasculitis, or cryoglobulinemic alveolar hemorrhage",
            },
        ],
        "second_line": [
            {
                "drug": "Cyclophosphamide",
                "dose": "1-2mg/kg/day oral or 500-750mg/m² IV monthly",
                "duration": "2-3 months, then transition to maintenance",
                "target": "Severe or refractory cryoglobulinemic GN",
                "rationale": "For cases refractory to rituximab; limited use due to toxicity",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Interferon-based therapy in HCV-related cryoglobulinemia (replaced by DAAs; risk of flare)"],
        "monitoring": [
            {"parameter": "Cryocrit", "interval": "every 1-3 months", "target": "Undetectable", "action_threshold": "Recurrent detectable cryoglobulins"},
            {"parameter": "Complement C4", "interval": "every 1-3 months", "target": "Normal range", "action_threshold": "Persistent low C4 (disease activity marker)"},
            {"parameter": "HCV RNA", "interval": "per hepatology protocol (end of treatment, 12 weeks post)", "target": "Undetectable (SVR)", "action_threshold": "Virologic relapse"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Every 1-2 weeks during active treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "immunotactoid": {
        "disease_name": "Immunotactoid Glomerulonephritis",
        "first_line": [
            {
                "drug": "Clone-directed therapy (if monoclonal immunoglobulin-associated)",
                "dose": "Daratumumab- or bortezomib-based regimen per hematology",
                "duration": "Per hematologic protocol (typically 4-6 cycles)",
                "target": "Hematologic complete response",
                "rationale": "Immunotactoid GN with monoclonal deposits is driven by the underlying clone; clone suppression is disease-modifying",
                "evidence_grade": "OP",
                "conditions": "Confirmed monoclonal immunoglobulin association on renal biopsy; requires hematology collaboration",
            },
            {
                "drug": "RAAS blockade",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing",
                "target": "Proteinuria reduction, BP control",
                "rationale": "Adjunctive for proteinuria control in all patients",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Rituximab-based regimen (if autoimmune-associated)",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "4 weeks or 2 doses, repeat as needed",
                "target": "B-cell depletion, reduce immunoglobulin production",
                "rationale": "For cases associated with autoimmune disease (Sjögren's, SLE) rather than monoclonal gammopathy",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": [],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Hematologic workup (SPEP, UPEP, FLC, CBC)", "interval": "every 3-6 months", "target": "No monoclonal spike, normal FLC ratio", "action_threshold": "New or progressive monoclonal gammopathy"},
        ],
        "follow_up": {
            "induction_phase": "Every 2-4 weeks during treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "fibrillaryGlomerulonephritis": {
        "disease_name": "Fibrillary Glomerulonephritis",
        "first_line": [
            {
                "drug": "RAAS blockade + blood pressure control",
                "dose": "ACEi/ARB titrated to maximum tolerated dose; additional antihypertensives as needed",
                "duration": "Ongoing",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Foundation of management; no curative therapy exists for fibrillary GN",
                "evidence_grade": "2",
            },
            {
                "drug": "Rituximab (progressive disease)",
                "dose": "375mg/m² × 4 weekly doses or 1000mg × 2 doses",
                "duration": "4 weeks or 2 doses; repeat based on response",
                "target": "Stabilize or improve eGFR, reduce proteinuria",
                "rationale": "Emerging evidence for rituximab in progressive fibrillary GN; may stabilize renal function in subset of patients",
                "evidence_grade": "OP",
                "conditions": "Progressive disease with rising creatinine or worsening proteinuria despite supportive care",
            },
        ],
        "second_line": [
            {
                "drug": "Mycophenolate mofetil + corticosteroids",
                "dose": "MMF 2g/day + prednisolone 0.5mg/kg/day tapering to 5-10mg/day",
                "duration": "12-24 months",
                "target": "Stabilize renal function",
                "rationale": "Alternative when rituximab fails or is unavailable; limited evidence for efficacy",
                "evidence_grade": "OP",
            },
        ],
        "rescue_therapy": [],
        "contraindicated": ["Corticosteroids alone (no disease-modifying benefit; risk of steroid toxicity without efficacy)"],
        "monitoring": [
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly during active treatment",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
    "paraneoplastic": {
        "disease_name": "Paraneoplastic Glomerulonephritis",
        "first_line": [
            {
                "drug": "Treat underlying malignancy (primary therapy)",
                "dose": "Per oncology protocol (surgery, chemotherapy, immunotherapy as indicated)",
                "duration": "Per oncologic protocol",
                "target": "Tumor eradication or control; GN typically improves with tumor treatment",
                "rationale": "KDIGO 2021: paraneoplastic GN resolves with treatment of the underlying malignancy; GN therapy alone is insufficient",
                "evidence_grade": "1",
            },
            {
                "drug": "RAS blockade for proteinuria",
                "dose": "ACEi/ARB titrated to maximum tolerated dose",
                "duration": "Ongoing during active GN",
                "target": "BP <130/80 mmHg, proteinuria reduction",
                "rationale": "Adjunctive for proteinuria control while treating the underlying malignancy",
                "evidence_grade": "2",
            },
        ],
        "second_line": [
            {
                "drug": "Immunosuppression (only if indicated by specific GN type and malignancy is controlled)",
                "dose": "Per GN-specific protocol with reduced intensity",
                "duration": "Per GN protocol, shorter course preferred",
                "target": "GN remission when malignancy is controlled",
                "rationale": "May be considered if GN is severe and malignancy is in remission; balance infection risk from immunosuppression vs. cancer treatment",
                "evidence_grade": "OP",
                "conditions": "Malignancy in remission or fully treated; severe GN requiring immunosuppression",
            },
        ],
        "rescue_therapy": [
            {
                "drug": "GN-specific rescue therapy (if malignancy-free)",
                "dose": "Per specific GN type protocol",
                "duration": "Per GN protocol",
                "target": "Control refractory GN in cancer-free state",
                "rationale": "If malignancy is fully treated and GN persists, treat per the underlying GN histology",
                "evidence_grade": "OP",
                "conditions": "Confirmed malignancy-free status",
            },
        ],
        "contraindicated": ["Immunosuppression without treating the underlying malignancy (ineffective, delays cancer treatment)"],
        "monitoring": [
            {"parameter": "Tumor markers (type-specific)", "interval": "per oncology protocol", "target": "Normal/negative", "action_threshold": "Rising tumor markers (disease recurrence)"},
            {"parameter": "24h UTP (g/day)", "interval": "every 1-3 months", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "every 1-3 months", "target": "Stable", "action_threshold": ">20% decline"},
            {"parameter": "Cancer surveillance", "interval": "per oncology guidelines", "target": "No evidence of recurrence", "action_threshold": "New malignancy findings"},
        ],
        "follow_up": {
            "induction_phase": "Every 1-3 months (concurrent with oncology follow-up)",
            "maintenance_phase": "Every 3-6 months",
            "stable_remission": "Every 6-12 months",
        },
    },
}

for _key, _profile in PROFILES.items():
    ProfileRegistry.register(_key, _profile)

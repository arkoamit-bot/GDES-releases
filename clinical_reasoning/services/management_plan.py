"""Personalized Management Plan Generator — Phase 6 of GDES transformation.

Generates comprehensive, evidence-based management plans per disease profile
including: first-line therapy, alternative therapy, rescue therapy,
contraindicated medications, monitoring parameters, and follow-up schedule.

Aligns with the GDES vision document: "Once the diagnosis is confirmed,
GDES should automatically generate a comprehensive management plan."
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Disease-specific treatment protocols (KDIGO-aligned)
# ---------------------------------------------------------------------------

DISEASE_TREATMENT_PROFILES: dict[str, dict[str, Any]] = {
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
                "drug": "Corticosteroids (targeted release — budesonide Nefeond)",
                "dose": "16mg daily for 2 weeks, then 8mg daily for 10 weeks",
                "duration": "12 weeks total course",
                "target": "Proteinuria reduction for high-risk IgAN",
                "rationale": "NefIgArd trial: targeted-release budesonide reduced proteinuria and preserved eGFR in high-risk IgAN",
                "evidence_grade": "1",
                "conditions": "Proteinuria >1g/day despite ≥3 months optimized supportive care, eGFR >35",
            },
        ],
        "contraindicated": ["NSAIDs (active disease)", "Aminoglycosides"],
        "monitoring": [
            {"parameter": "UPCR", "interval": "monthly during active phase, quarterly in remission", "target": "<0.5g/day", "action_threshold": ">1g/day"},
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
            {"parameter": "UPCR", "interval": "monthly during treatment, quarterly in remission", "target": "<0.3g/day (complete remission)", "action_threshold": ">3.5g/day or >50% increase"},
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
            {"parameter": "UPCR", "interval": "weekly during induction, then monthly", "target": "<0.3g/day", "action_threshold": "Relapse (nephrotic range proteinuria)"},
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
            {"parameter": "UPCR", "interval": "monthly", "target": "<0.3g/day", "action_threshold": "Nephrotic range proteinuria"},
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
            {"parameter": "Urine dipstick/UPCR", "interval": "monthly", "target": "No active sediment", "action_threshold": "New hematuria or proteinuria"},
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
            {"parameter": "UPCR", "interval": "monthly until resolution", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range >3 months"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Improving", "action_threshold": "Worsening (consider alternative diagnosis)"},
            {"parameter": "Complement C3", "interval": "monthly", "target": "Normalizing", "action_threshold": "Persistent low C3 >3 months (consider alternative)"},
        ],
        "follow_up": {
            "induction_phase": "Monthly until infection eradicated",
            "resolution_phase": "Every 3 months for 1 year",
            "stable_remission": "Every 6 months for 2 years",
        },
    },
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
            {"parameter": "UPCR", "interval": "monthly", "target": "<0.5g/day", "action_threshold": "Persistent nephrotic range"},
            {"parameter": "Serum creatinine/eGFR", "interval": "monthly", "target": "Stable", "action_threshold": ">20% decline"},
        ],
        "follow_up": {
            "induction_phase": "Monthly",
            "maintenance_phase": "Every 3 months",
            "stable_remission": "Every 6 months",
        },
    },
}


# ---------------------------------------------------------------------------
# Management Plan Generation
# ---------------------------------------------------------------------------

@dataclass
class ManagementPlan:
    """Structured output of the management plan generator."""
    disease_id: str
    disease_name: str
    patient_id: str
    first_line: list[dict]
    second_line: list[dict]
    rescue_therapy: list[dict]
    contraindicated: list[str]
    monitoring: list[dict]
    follow_up: dict
    general_measures: list[dict]
    safety_checks: list[dict]
    patient_education: list[dict]

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "disease_name": self.disease_name,
            "patient_id": self.patient_id,
            "first_line": self.first_line,
            "second_line": self.second_line,
            "rescue_therapy": self.rescue_therapy,
            "contraindicated": self.contraindicated,
            "monitoring": self.monitoring,
            "follow_up": self.follow_up,
            "general_measures": self.general_measures,
            "safety_checks": self.safety_checks,
            "patient_education": self.patient_education,
        }


def generate_management_plan(
    patient,
    disease_id: str,
    features: dict | None = None,
    risk_category: str = "moderate",
) -> ManagementPlan:
    """Generate a personalized management plan for a patient.

    Args:
        patient: Patient model instance
        disease_id: Disease identifier (e.g., "iga", "membranous")
        features: Optional pre-extracted patient features
        risk_category: Risk level from risk assessment ("low", "moderate", "high", "very_high")

    Returns:
        ManagementPlan dataclass with all recommendations
    """
    profile = DISEASE_TREATMENT_PROFILES.get(disease_id)
    if not profile:
        return _build_default_plan(patient, disease_id)

    plan = ManagementPlan(
        disease_id=disease_id,
        disease_name=profile["disease_name"],
        patient_id=patient.patient_id,
        first_line=profile.get("first_line", []),
        second_line=profile.get("second_line", []),
        rescue_therapy=profile.get("rescue_therapy", []),
        contraindicated=profile.get("contraindicated", []),
        monitoring=profile.get("monitoring", []),
        follow_up=profile.get("follow_up", {}),
        general_measures=_build_general_measures(disease_id, features or {}),
        safety_checks=_build_safety_checks(patient, disease_id, features or {}),
        patient_education=_build_patient_education(disease_id),
    )

    # Adjust monitoring intensity based on risk category
    if risk_category in ("high", "very_high"):
        plan = _intensify_monitoring(plan, risk_category)

    # Add CKD-specific modifications
    if features and features.get("egfrTrend") == "reduced":
        plan = _add_ckd_modifications(plan, features)

    return plan


def _build_general_measures(disease_id: str, features: dict) -> list[dict]:
    """Build general non-pharmacological measures."""
    measures = [
        {
            "category": "Blood pressure",
            "recommendation": "Target <130/80 mmHg (KDIGO 2021)",
            "rationale": "RAAS blockade is preferred antihypertensive in proteinuric GN",
        },
        {
            "category": "Dietary sodium",
            "recommendation": "Restrict to <2g/day sodium (5g/day salt)",
            "rationale": "Reduces proteinuria and blood pressure",
        },
        {
            "category": "Protein intake",
            "recommendation": "0.8-1.0 g/kg/day (avoid high protein)",
            "rationale": "High protein accelerates kidney disease progression",
        },
        {
            "category": "Vaccination",
            "recommendation": "Update pneumococcal, influenza, hepatitis B, COVID-19 vaccines before immunosuppression",
            "rationale": "Immunosuppressed patients at high risk; live vaccines contraindicated on treatment",
        },
    ]

    if features.get("edema") or features.get("proteinuria") == "nephrotic":
        measures.append({
            "category": "Edema management",
            "recommendation": "Salt restriction, loop diuretics as needed, leg elevation",
            "rationale": "Nephrotic edema requires both dietary and pharmacological management",
        })

    return measures


def _build_safety_checks(patient, disease_id: str, features: dict) -> list[dict]:
    """Build safety checks and contraindication warnings."""
    checks = []

    # Check for existing contraindications
    profile = DISEASE_TREATMENT_PROFILES.get(disease_id, {})
    contraindicated = profile.get("contraindicated", [])
    if contraindicated:
        checks.append({
            "type": "contraindication",
            "level": "critical",
            "message": f"Contraindicated medications for {profile.get('disease_name', disease_id)}: {', '.join(contraindicated)}",
        })

    # Pregnancy check
    if hasattr(patient, "sex") and patient.sex == "F":
        checks.append({
            "type": "pregnancy_screening",
            "level": "moderate",
            "message": "If pregnancy is possible, avoid mycophenolate, cyclophosphamide, ACEi/ARBs, and statins. Consult maternal-fetal medicine.",
        })

    # Drug interaction warning (if on multiple immunosuppressants)
    if disease_id in ("lupus", "anca", "antiGbm"):
        checks.append({
            "type": "infection_risk",
            "level": "high",
            "message": "Active immunosuppression: monitor for infection. PJP prophylaxis (trimethoprim-sulfamethoxazole) if on high-dose steroids or combination immunosuppression.",
        })

    return checks


def _build_patient_education(disease_id: str) -> list[dict]:
    """Build patient education points."""
    education = [
        {
            "topic": "Medication adherence",
            "message": "Take medications as prescribed. Do not stop steroids abruptly without medical advice.",
        },
        {
            "topic": "Infection prevention",
            "message": "Report fever, cough, or signs of infection immediately. Avoid crowds during immunosuppression.",
        },
        {
            "topic": "Dietary compliance",
            "message": "Follow salt and protein restrictions. Maintain adequate hydration.",
        },
    ]

    if disease_id in ("iga", "membranous", "fsgs"):
        education.append({
            "topic": "Proteinuria monitoring",
            "message": "Regular urine tests are essential to monitor disease activity. Bring a fresh urine sample to each visit.",
        })

    if disease_id in ("lupus", "anca"):
        education.append({
            "topic": "Disease flare recognition",
            "message": "Know the signs of relapse: increased swelling, reduced urine output, rash, joint pain, or fever. Contact your nephrologist immediately.",
        })

    return education


def _intensify_monitoring(plan: ManagementPlan, risk_category: str) -> ManagementPlan:
    """Intensify monitoring for high-risk patients."""
    multiplier = 2 if risk_category == "very_high" else 1.5

    for monitor in plan.monitoring:
        interval = monitor.get("interval", "")
        if "quarterly" in interval:
            monitor["interval"] = interval.replace("quarterly", "monthly")
        elif "monthly" in interval and risk_category == "very_high":
            monitor["interval"] = "every 2 weeks"

    # Add high-risk specific monitoring
    if risk_category == "very_high":
        plan.monitoring.append({
            "parameter": "Urgent nephrology review",
            "interval": "every 2 weeks",
            "target": "Clinical stability",
            "action_threshold": "Any clinical deterioration",
        })

    return plan


def _add_ckd_modifications(plan: ManagementPlan, features: dict) -> ManagementPlan:
    """Add CKD-specific modifications to the plan."""
    plan.monitoring.append({
        "parameter": "CKD-MBD screening (calcium, phosphate, PTH, vitamin D)",
        "interval": "every 3-6 months (eGFR <45)",
        "target": "Calcium 8.5-10.5, phosphate <4.5, PTH 2-9× ULN",
        "action_threshold": "CKD-MBD detected",
    })
    plan.monitoring.append({
        "parameter": "Anemia screening (hemoglobin, iron studies)",
        "interval": "every 3 months (eGFR <60)",
        "target": "Hb >11 g/dL",
        "action_threshold": "Anemia (Hb <11)",
    })
    return plan


def _build_default_plan(patient, disease_id: str) -> ManagementPlan:
    """Build a default plan for diseases not in the protocol database."""
    return ManagementPlan(
        disease_id=disease_id,
        disease_name=disease_id.replace("_", " ").title(),
        patient_id=patient.patient_id,
        first_line=[{
            "drug": "Nephrology consultation",
            "dose": "Per specialist recommendation",
            "duration": "As determined by nephrologist",
            "target": "Disease-specific goals",
            "rationale": "No specific protocol available; individualize treatment plan",
            "evidence_grade": "OP",
        }],
        second_line=[],
        rescue_therapy=[],
        contraindicated=[],
        monitoring=[{
            "parameter": "Serum creatinine/eGFR",
            "interval": "monthly",
            "target": "Stable",
            "action_threshold": ">20% decline",
        }],
        follow_up={"induction_phase": "Every 2-4 weeks", "maintenance_phase": "Every 3 months"},
        general_measures=_build_general_measures(disease_id, {}),
        safety_checks=_build_safety_checks(patient, disease_id, {}),
        patient_education=_build_patient_education(disease_id),
    )

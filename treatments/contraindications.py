"""Drug-disease contraindication engine for nephrology.

Checks if a drug is contraindicated given the patient's disease profile,
comorbidities, and clinical context. Focuses on glomerular disease-specific
contraindications (e.g. NSAIDs in active GN, CNIs in TMA, cyclophosphamide
in active infection).
"""

from dataclasses import dataclass, field
from typing import Any


CONTRANDICATION_SEVERITY_ABSOLUTE = "absolute"
CONTRANDICATION_SEVERITY_RELATIVE = "relative"
CONTRANDICATION_SEVERITY_CAUTION = "caution"

CONTRANDICATION_DB: list[dict[str, Any]] = [
    # --- NSAIDs ---
    {"drug": "nsaids", "disease": "active_gn",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "NSAIDs reduce renal blood flow via prostaglandin inhibition, worsening glomerular inflammation and accelerating CKD progression",
     "alternative": "Acetaminophen for analgesia; consider tramadol for moderate pain; topical NSAIDs only with extreme caution"},
    {"drug": "nsaids", "disease": "ckd_stage_4_5",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "High risk of acute kidney injury and irreversible renal function decline in advanced CKD",
     "alternative": "Acetaminophen; consider opioid-sparing strategies"},
    {"drug": "nsaids", "disease": "nephrotic_syndrome",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Can worsen proteinuria and edema; volume-depleted nephrotic patients at high AKI risk",
     "alternative": "Acetaminophen; avoid NSAIDs until remission achieved"},
    {"drug": "nsaids", "disease": "volume_depletion",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Pre-renal AKI risk dramatically increased when prostaglandin-dependent renal autoregulation is compromised",
     "alternative": "Correct volume status before using any analgesic requiring renal perfusion"},
    {"drug": "nsaids", "disease": "heart_failure",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "NSAIDs cause sodium and water retention, exacerbating heart failure; increased hospitalization risk",
     "alternative": "Acetaminophen"},
    # --- Calcineurin inhibitors (CNIs) ---
    {"drug": "calcineurin_inhibitor", "disease": "thrombotic_microangiopathy",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "CNIs directly injure endothelium and reduce VEGF, triggering or worsening TMA; TMA recurrence rate >50% in aHUS patients exposed to CNIs",
     "alternative": "Consider belatacept or mTOR inhibitor-based regimen; monitor LDH, haptoglobin, schistocytes"},
    {"drug": "calcineurin_inhibitor", "disease": "active_infection",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Immunosuppression may worsen infections; increased risk of opportunistic infections",
     "alternative": "Treat infection before initiating CNI if feasible; adjust CNI doses and monitor levels"},
    {"drug": "calcineurin_inhibitor", "disease": "posterior_reversible_leukoencephalopathy",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "CNIs can cause or exacerbate PRES; recurrence risk high on rechallenge",
     "alternative": "Switch to non-CNI immunosuppressant; control hypertension"},
    {"drug": "calcineurin_inhibitor", "disease": "ckd_stage_4_5",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Additive nephrotoxicity in already compromised kidneys; CNI-induced arteriolar hyalinosis worsens CKD",
     "alternative": "Reduce CNI dose; monitor trough levels; consider mTOR inhibitor or belatacept conversion"},
    {"drug": "calcineurin_inhibitor", "disease": "uncontrolled_hypertension",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "CNIs cause vasoconstriction and worsen hypertension; increased risk of hypertensive emergency and PRES",
     "alternative": "Optimize BP control before CNI initiation; use calcium channel blockers (except verapamil/diltiazem) as preferred antihypertensives"},
    # --- Cyclophosphamide ---
    {"drug": "cyclophosphamide", "disease": "active_infection",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Cyclophosphamide causes myelosuppression and lymphopenia, impairing infection clearance; risk of severe sepsis",
     "alternative": "Treat infection first if possible; for urgent autoimmune indications, use with aggressive infection monitoring and growth factor support"},
    {"drug": "cyclophosphamide", "disease": "leukopenia",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Cyclophosphamide worsens leukopenia causing life-threatening neutropenic sepsis",
     "alternative": "Recover WCC to >4000 before initiating; use rituximab-based alternative if available"},
    {"drug": "cyclophosphamide", "disease": "pregnancy",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Cyclophosphamide is teratogenic (FDA Category D); causes fetal malformations, growth restriction, and miscarriage",
     "alternative": "Use corticosteroids, AZA or calcineurin inhibitors during pregnancy; rituximab for severe disease"},
    {"drug": "cyclophosphamide", "disease": "breastfeeding",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Cyclophosphamide excreted in breast milk; causes neonatal neutropenia and potential carcinogenesis",
     "alternative": "Discontinue breastfeeding or use alternative agent"},
    {"drug": "cyclophosphamide", "disease": "hemorrhagic_cystitis_history",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "High recurrence risk of hemorrhagic cystitis with re-exposure; can cause life-threatening bladder hemorrhage",
     "alternative": "Use rituximab or MMF instead; if unavoidable, aggressive hydration and mesna"},
    # --- Mycophenolate ---
    {"drug": "mycophenolate", "disease": "pregnancy",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Mycophenolate is teratogenic (FDA Category D); associated with first-trimester pregnancy loss (45-49%) and congenital malformations (23-27%)",
     "alternative": "Switch to AZA or CNI before conception; ensure negative pregnancy test before starting"},
    {"drug": "mycophenolate", "disease": "active_gi_bleeding",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Mycophenolate can cause GI ulceration, esophagitis, and colitis, worsening bleeding",
     "alternative": "Use enteric-coated mycophenolate sodium; consider AZA or CNI alternative"},
    {"drug": "mycophenolate", "disease": "severe_leukopenia",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Mycophenolate causes dose-dependent bone marrow suppression, worsening leukopenia",
     "alternative": "Reduce dose; monitor CBC; use G-CSF if needed; consider alternative agent if persistent"},
    # --- Rituximab ---
    {"drug": "rituximab", "disease": "active_hepatitis_b",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Rituximab depletes B cells, impairing HBV immune control; reactivation risk >50% in HBsAg+ patients; can cause fulminant hepatitis",
     "alternative": "Initiate antiviral prophylaxis (entecavir or tenofovir) at least 2 weeks before rituximab; monitor HBV DNA monthly"},
    {"drug": "rituximab", "disease": "active_tb",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Rituximab increases risk of TB reactivation in latent infection and worsens active TB",
     "alternative": "Complete TB treatment before rituximab therapy if possible"},
    {"drug": "rituximab", "disease": "severe_infection",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Immunosuppression may worsen severe ongoing infections including COVID-19",
     "alternative": "Delay rituximab until infection resolved; consider shorter-acting immunosuppression"},
    {"drug": "rituximab", "disease": "progressive_multifocal_leukoencephalopathy",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Rituximab is associated with JC virus reactivation causing PML; mortality >90%",
     "alternative": "Stop rituximab immediately if PML suspected; no specific alternative"},
    # --- SGLT2 inhibitors ---
    {"drug": "sglt2_inhibitor", "disease": "ckd_stage_5",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Reduced efficacy when eGFR <25; increased risk of volume depletion and AKI; not recommended in dialysis patients",
     "alternative": "Consider finerenone or GLP-1 RA for cardiorenal protection"},
    {"drug": "sglt2_inhibitor", "disease": "recurrent_uti",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "Increased risk of genital mycotic infections and potential for urosepsis risk in those with recurrent UTIs",
     "alternative": "Use with caution; ensure proper genital hygiene; monitor for UTI symptoms"},
    {"drug": "sglt2_inhibitor", "disease": "ketoacidosis_risk",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Risk of euglycemic DKA, especially in patients on low-carb diets, during illness, or with reduced insulin doses",
     "alternative": "Educate patient on sick day rules; hold SGLT2i during acute illness"},
    # --- Finerenone / MRAs ---
    {"drug": "finerenone", "disease": "hyperkalemia",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "MRA further reduces potassium excretion; life-threatening hyperkalemia risk if baseline K>5.0",
     "alternative": "Correct potassium first; optimize RAASi dose; use potassium binders if needed"},
    {"drug": "finerenone", "disease": "ckd_stage_5",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Increased hyperkalemia risk in advanced CKD; limited CV outcomes data in dialysis patients",
     "alternative": "Monitor potassium closely; restrict dose if eGFR <25"},
    # --- Metformin ---
    {"drug": "metformin", "disease": "ckd_stage_4_5",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Accumulation risk causing lactic acidosis; FDA restricts use when eGFR <30",
     "alternative": "Reduce dose to 500mg BID if eGFR 30-45; discontinue if eGFR <30; use SGLT2i or GLP-1 RA"},
    {"drug": "metformin", "disease": "lactic_acidosis_risk",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Metformin-associated lactic acidosis (MALA) in patients with predisposing conditions",
     "alternative": "Hold metformin during acute illness, sepsis, or contrast procedures; restart when stable"},
    {"drug": "metformin", "disease": "severe_heart_failure",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Increased risk of lactic acidosis in hemodynamically unstable HF patients",
     "alternative": "Hold metformin during acute decompensation; restart when stable"},
    # --- Corticosteroids ---
    {"drug": "corticosteroid", "disease": "active_peptic_ulcer",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Steroids impair ulcer healing and increase perforation risk",
     "alternative": "Use PPI prophylaxis; consider steroid-sparing agents"},
    {"drug": "corticosteroid", "disease": "uncontrolled_diabetes",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Steroid-induced hyperglycemia can be severe, especially with high-dose pulse therapy",
     "alternative": "Monitor glucose intensively; adjust anti-diabetic medications; use steroid-sparing strategy"},
    {"drug": "corticosteroid", "disease": "active_psychosis",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Corticosteroids can cause or exacerbate psychiatric symptoms including psychosis, mania, and severe depression",
     "alternative": "Use with caution; consider steroid-sparing agent if psychiatric history"},
    {"drug": "corticosteroid", "disease": "glaucoma",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "Steroids increase intraocular pressure; risk of open-angle glaucoma exacerbation",
     "alternative": "Monitor IOP; use with caution in patients with known glaucoma"},
    {"drug": "corticosteroid", "disease": "osteoporosis",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "Chronic steroid use accelerates bone loss; fracture risk increases 30-50%",
     "alternative": "Use lowest effective dose and duration; calcium and vitamin D; bisphosphonate if prolonged use >3 months"},
    # --- Hydroxychloroquine ---
    {"drug": "hydroxychloroquine", "disease": "retinal_disease",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "HCQ accumulates in retinal pigment epithelium causing irreversible retinopathy; risk increases after 5 years or >5mg/kg/day",
     "alternative": "Use lowest effective dose (≤5mg/kg/day); baseline and annual ophthalmologic screening"},
    {"drug": "hydroxychloroquine", "disease": "g6pd_deficiency",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "HCQ can cause hemolytic anemia in G6PD-deficient patients, though risk is lower than with other antimalarials",
     "alternative": "Screen for G6PD in high-risk populations; monitor for hemolysis"},
    # --- Aminoglycosides ---
    {"drug": "aminoglycoside", "disease": "ckd_stage_4_5",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "High nephrotoxicity; accumulation due to reduced clearance causes irreversible renal damage",
     "alternative": "Use alternative antibiotics (beta-lactams, fluoroquinolones); if unavoidable, extended-interval dosing with TDM"},
    {"drug": "aminoglycoside", "disease": "myasthenia_gravis",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Aminoglycosides impair neuromuscular transmission; can precipitate myasthenic crisis",
     "alternative": "Avoid; use non-aminoglycoside antibiotic"},
    # --- Contrast dye (for procedures) ---
    {"drug": "iodinated_contrast", "disease": "ckd_stage_3_5",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Risk of contrast-induced nephropathy (CIN); risk >25% in CKD stage 4-5 diabetics",
     "alternative": "Use iso-osmolar contrast agents; IV hydration with normal saline pre/post; minimize contrast volume; consider MRI with gadolinium (with caution)"},
    {"drug": "iodinated_contrast", "disease": "metformin_therapy",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "Risk of metformin-associated lactic acidosis if CIN develops",
     "alternative": "Hold metformin 48h before and 48h after contrast; restart only if renal function stable"},
    # --- Azathioprine ---
    {"drug": "azathioprine", "disease": "tpmt_deficiency",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Patients with homozygous TPMT deficiency develop severe, life-threatening myelosuppression even with standard doses",
     "alternative": "Test TPMT activity before starting; if deficient, reduce dose by 90% or use alternative (MMF, CNI)"},
    {"drug": "azathioprine", "disease": "active_infection",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Immunosuppression impairs infection clearance",
     "alternative": "Treat infection first; monitor closely during concomitant use"},
    # --- Warfarin ---
    {"drug": "warfarin", "disease": "ckd_stage_5_dialysis",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Higher bleeding risk in dialysis; labile INRs; increased vascular calcification risk",
     "alternative": "Consider DOACs if appropriate (adjusted for renal function); monitor INR very closely"},
    {"drug": "warfarin", "disease": "active_gi_bleeding",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "Anticoagulation worsens active bleeding and delays hemostasis",
     "alternative": "Hold warfarin; reverse with vitamin K if needed; identify and treat bleeding source before resuming"},
    # --- Anti-TNF / Biologics ---
    {"drug": "anti_tnf", "disease": "active_infection",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "TNF inhibitors significantly increase risk of serious infections including TB reactivation, fungal, and opportunistic infections",
     "alternative": "Screen for latent TB and hepatitis B before starting; treat active infections first"},
    {"drug": "anti_tnf", "disease": "demyelinating_disease",
     "severity": CONTRANDICATION_SEVERITY_ABSOLUTE,
     "reason": "TNF inhibitors can trigger or worsen demyelinating disorders (MS, optic neuritis)",
     "alternative": "Use alternative biologic with different mechanism (rituximab, belimumab)"},
    # --- TMP/SMX ---
    {"drug": "trimethoprim_sulfamethoxazole", "disease": "severe_hyperkalemia",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Trimethoprim has potassium-sparing effect that can worsen hyperkalemia, especially in CKD",
     "alternative": "Use alternative antibiotic; or combine with potassium monitoring and management"},
    {"drug": "trimethoprim_sulfamethoxazole", "disease": "g6pd_deficiency",
     "severity": CONTRANDICATION_SEVERITY_RELATIVE,
     "reason": "Sulfonamide component can trigger hemolytic anemia in G6PD deficiency",
     "alternative": "Use alternative PCP prophylaxis (dapsone requires G6PD testing too; consider atovaquone)"},
    {"drug": "trimethoprim_sulfamethoxazole", "disease": "folate_deficiency",
     "severity": CONTRANDICATION_SEVERITY_CAUTION,
     "reason": "TMP/SMX inhibits folate metabolism; can worsen megaloblastic anemia",
     "alternative": "Supplement folate; monitor CBC"},
]


@dataclass
class ContraindicationResult:
    drug: str
    disease: str
    severity: str
    reason: str
    alternative: str | None = None


# Members of each class-keyed entry in CONTRANDICATION_DB. Without this table a
# class rule is unreachable whenever the caller supplies a drug's generic name:
# "gentamicin" never matches "aminoglycoside" and the CKD 4/5 contraindication
# silently never fires. Keys are the class names used in the database; values
# are the normalised generic names (and registry class codes) that map to it.
DRUG_CLASS_MEMBERS: dict[str, frozenset[str]] = {
    "nsaids": frozenset({
        "nsaid", "ibuprofen", "naproxen", "diclofenac", "indomethacin",
        "ketorolac", "celecoxib", "etoricoxib", "meloxicam", "piroxicam",
    }),
    "calcineurin_inhibitor": frozenset({
        "cni", "tacrolimus", "ciclosporin", "cyclosporine",
    }),
    "sglt2_inhibitor": frozenset({
        "sglt2i", "sglt2", "dapagliflozin", "empagliflozin", "canagliflozin",
        "ertugliflozin", "sotagliflozin",
    }),
    "aminoglycoside": frozenset({
        "aminoglycoside", "gentamicin", "amikacin", "tobramycin", "netilmicin",
        "streptomycin", "neomycin", "isepamicin", "plazomicin",
    }),
    "corticosteroid": frozenset({
        "steroid", "corticosteroid", "corticosteroids", "glucocorticoid",
        "prednisolone", "prednisone", "methylprednisolone", "methylpred",
        "dexamethasone", "hydrocortisone", "triamcinolone", "deflazacort",
        "budesonide", "betamethasone", "cortisone",
    }),
    "iodinated_contrast": frozenset({
        "iodinated_contrast", "contrast", "contrast_media", "iohexol",
        "iopamidol", "iopromide", "iodixanol", "ioversol", "iomeprol",
    }),
    "anti_tnf": frozenset({
        "anti_tnf", "tnf_inhibitor", "infliximab", "adalimumab", "etanercept",
        "golimumab", "certolizumab",
    }),
    "raasi": frozenset({
        "raasi", "ace_inhibitor", "arb", "ramipril", "losartan", "lisinopril",
        "valsartan", "enalapril", "candesartan", "telmisartan",
    }),
    "metformin": frozenset({"metformin", "metformin_hcl"}),
    "finerenone": frozenset({"finerenone", "ns_mra"}),
    "rituximab": frozenset({"rituximab"}),
    "warfarin": frozenset({"warfarin"}),
    "hydroxychloroquine": frozenset({"hydroxychloroquine", "hcq"}),
    "azathioprine": frozenset({"azathioprine"}),
    "cyclophosphamide": frozenset({"cyclophosphamide", "cyclophosphamide_iv"}),
    "mycophenolate": frozenset({
        "mycophenolate", "mycophenolate_mofetil", "mycophenolic_acid", "mmf",
    }),
    "trimethoprim_sulfamethoxazole": frozenset({
        "trimethoprim_sulfamethoxazole", "tmp_smx", "cotrimoxazole",
        "sulfamethoxazole_trimethoprim",
    }),
}

# Reverse index: generic name / class code -> the CONTRANDICATION_DB class keys
# it satisfies. Built once at import so lookups stay O(1).
_DRUG_TO_CLASSES: dict[str, frozenset[str]] = {}
for _cls, _members in DRUG_CLASS_MEMBERS.items():
    for _member in _members:
        _DRUG_TO_CLASSES[_member] = _DRUG_TO_CLASSES.get(_member, frozenset()) | {_cls}


def normalize_disease_id(name: str) -> str:
    """Normalize a disease name to lookup key."""
    mapping = {
        "active gn": "active_gn",
        "active glomerulonephritis": "active_gn",
        "ckd": "ckd_stage_4_5",
        "ckd stage 4": "ckd_stage_4_5",
        "ckd stage 5": "ckd_stage_4_5",
        "ckd stage 3": "ckd_stage_3_5",
        "ckd stage 4-5": "ckd_stage_4_5",
        "dialysis": "ckd_stage_5_dialysis",
        "nephrotic syndrome": "nephrotic_syndrome",
        "tma": "thrombotic_microangiopathy",
        "thrombotic microangiopathy": "thrombotic_microangiopathy",
        "hus": "thrombotic_microangiopathy",
        "pregnancy": "pregnancy",
        "breastfeeding": "breastfeeding",
        "infection": "active_infection",
        "active infection": "active_infection",
        "uti": "recurrent_uti",
        "recurrent uti": "recurrent_uti",
        "tb": "active_tb",
        "active tb": "active_tb",
        "hepatitis b": "active_hepatitis_b",
        "hbv": "active_hepatitis_b",
        "dm": "uncontrolled_diabetes",
        "diabetes": "uncontrolled_diabetes",
        "uncontrolled diabetes": "uncontrolled_diabetes",
        "heart failure": "heart_failure",
        "hf": "heart_failure",
        "hyperkalemia": "hyperkalemia",
        "hypokalemia": "hyperkalemia",
        "volume depletion": "volume_depletion",
        "dehydration": "volume_depletion",
        "peptic ulcer": "active_peptic_ulcer",
        "gi bleed": "active_gi_bleeding",
        "gi bleeding": "active_gi_bleeding",
        "leukopenia": "leukopenia",
        "low wcc": "leukopenia",
        "retinopathy": "retinal_disease",
        "retinal disease": "retinal_disease",
        "osteoporosis": "osteoporosis",
        "psychosis": "active_psychosis",
        "g6pd": "g6pd_deficiency",
        "g6pd deficiency": "g6pd_deficiency",
        "pres": "posterior_reversible_leukoencephalopathy",
        "pml": "progressive_multifocal_leukoencephalopathy",
        "hypertension": "uncontrolled_hypertension",
        "uncontrolled hypertension": "uncontrolled_hypertension",
        "tpmt deficiency": "tpmt_deficiency",
        "lactic acidosis": "lactic_acidosis_risk",
        "dka risk": "ketoacidosis_risk",
        "ketoacidosis": "ketoacidosis_risk",
        "glaucoma": "glaucoma",
        "myasthenia gravis": "myasthenia_gravis",
        "demyelinating disease": "demyelinating_disease",
        "ms": "demyelinating_disease",
        "contrast allergy": "iodinated_contrast",
        "hemorrhagic cystitis": "hemorrhagic_cystitis_history",
        "bladder cancer": "hemorrhagic_cystitis_history",
        "active gi bleeding": "active_gi_bleeding",
        "ckd stage 5 dialysis": "ckd_stage_5_dialysis",
    }
    normalized = name.strip().lower().replace("  ", " ")
    return mapping.get(normalized, normalized.replace(" ", "_").replace("-", "_"))


def _normalize_drug(name: str) -> str:
    return str(name or "").strip().lower().replace(" ", "_").replace("-", "_")


# ``normalize_disease_id`` deliberately collapses "CKD stage 5" into the coarser
# ``ckd_stage_4_5`` because most rules are written for the whole range. That
# makes the two finer-grained database rules unreachable, so a patient in CKD 4/5
# would not trigger the SGLT2-inhibitor stage-5 contraindication. The reverse
# expansion restores them: a 4/5 patient also satisfies the stage-5 rule.
_DISEASE_IMPLIES: dict[str, frozenset[str]] = {
    "ckd_stage_4_5": frozenset({"ckd_stage_5", "ckd_stage_3_5"}),
    "ckd_stage_5_dialysis": frozenset({"ckd_stage_5", "ckd_stage_4_5", "ckd_stage_3_5"}),
}


def _disease_matches(db_disease: str, resolved: str) -> bool:
    return db_disease == resolved or db_disease in _DISEASE_IMPLIES.get(resolved, frozenset())


def _drug_matches(db_drug: str, drug_normalized: str) -> bool:
    """Does a single normalised drug name satisfy a database ``drug`` key?

    Exact match first, then the class-member index so a generic name like
    "gentamicin" or "prednisolone" reaches the class-keyed rules.
    """
    if drug_normalized == db_drug:
        return True
    return db_drug in _DRUG_TO_CLASSES.get(drug_normalized, frozenset())


def check_contraindications(
    drug: str,
    patient_diseases: list[str],
    patient_context: dict | None = None,
    drug_class: str = "",
) -> list[ContraindicationResult]:
    """Check if a drug is contraindicated given the patient's disease conditions.

    Args:
        drug: Drug name or ID
        patient_diseases: List of patient's active diseases/conditions
        patient_context: Optional dict with egfr, age, etc.
        drug_class: Optional registry class code (e.g. "steroid", "cni"). Supplied
            by callers that hold a ``DrugMaster`` row; the class alone is enough
            to reach the class-keyed rules when the generic name is unknown.

    Returns:
        List of ContraindicationResult objects
    """
    drug_normalized = _normalize_drug(drug)
    class_normalized = _normalize_drug(drug_class)

    resolved_diseases = [normalize_disease_id(d) for d in patient_diseases]

    results: list[ContraindicationResult] = []
    checked_pairs = set()

    for contraindication in CONTRANDICATION_DB:
        db_drug = contraindication["drug"]
        db_disease = contraindication["disease"]

        drug_matches = _drug_matches(db_drug, drug_normalized)
        if not drug_matches and class_normalized:
            drug_matches = _drug_matches(db_drug, class_normalized)

        if not drug_matches:
            continue

        for disease in resolved_diseases:
            pair_key = (db_drug, db_disease)
            if pair_key in checked_pairs:
                continue

            if _disease_matches(db_disease, disease):
                results.append(ContraindicationResult(
                    drug=drug,
                    disease=db_disease,
                    severity=contraindication["severity"],
                    reason=contraindication["reason"],
                    alternative=contraindication.get("alternative"),
                ))
                checked_pairs.add(pair_key)

    # Sort by severity
    order = {CONTRANDICATION_SEVERITY_ABSOLUTE: 0,
             CONTRANDICATION_SEVERITY_RELATIVE: 1,
             CONTRANDICATION_SEVERITY_CAUTION: 2}
    results.sort(key=lambda r: order.get(r.severity, 99))

    return results


def get_contraindication_summary(
    results: list[ContraindicationResult],
) -> dict:
    """Summarize contraindication check results."""
    absolute = sum(1 for r in results
                   if r.severity == CONTRANDICATION_SEVERITY_ABSOLUTE)
    relative = sum(1 for r in results
                   if r.severity == CONTRANDICATION_SEVERITY_RELATIVE)
    caution = sum(1 for r in results
                  if r.severity == CONTRANDICATION_SEVERITY_CAUTION)

    if absolute > 0:
        recommendation = "contraindicated"
    elif relative > 0:
        recommendation = "relative_contraindication"
    else:
        recommendation = "caution_advised"

    return {
        "total_contraindications": len(results),
        "absolute": absolute,
        "relative": relative,
        "caution": caution,
        "recommendation": recommendation,
        "contraindications": [
            {
                "drug": r.drug,
                "disease": r.disease,
                "severity": r.severity,
                "reason": r.reason,
                "alternative": r.alternative,
            }
            for r in results
        ],
    }


def check_all_contraindications(
    drugs: list[str],
    patient_diseases: list[str],
    patient_context: dict | None = None,
) -> dict:
    """Check multiple drugs for contraindications against patient conditions.

    Args:
        drugs: List of drug names to check
        patient_diseases: Patient's active disease conditions
        patient_context: Optional clinical context

    Returns:
        Dict with drug-wise and summary results
    """
    drug_results = {}
    all_absolute = 0
    all_relative = 0
    all_caution = 0

    for drug in drugs:
        results = check_contraindications(drug, patient_diseases, patient_context)
        summary = get_contraindication_summary(results)
        drug_results[drug] = summary
        all_absolute += summary["absolute"]
        all_relative += summary["relative"]
        all_caution += summary["caution"]

    if all_absolute > 0:
        overall = "contraindicated"
    elif all_relative > 0:
        overall = "relative_contraindication"
    else:
        overall = "caution_advised"

    return {
        "overall_recommendation": overall,
        "total_drugs_checked": len(drugs),
        "total_contraindications": all_absolute + all_relative + all_caution,
        "drug_results": drug_results,
    }

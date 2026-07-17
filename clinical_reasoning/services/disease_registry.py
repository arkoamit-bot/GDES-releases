"""GDES V8.1 Disease Registry — Single source of truth for all 36 diseases.

Phases A-F per Clinical Learning Engine roadmap. Every disease has:
  id, name, category, phase, diagnostic_rules (KB seed clues),
  treatment_profile (management plan), validation_checks, failure_patterns,
  guideline_chapter, evidence_url.

All consumers (seed_knowledge_base, management_plan, disease_validation,
treatment_failure) import from here to stay in sync.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────
# Phase A — Common Primary Glomerular Diseases
# ──────────────────────────────────────────────────────────────────────

IGA = "iga"
MEMBRANOUS = "membranous"
FSGS = "fsgs"
MCD = "mcd"

# ──────────────────────────────────────────────────────────────────────
# Phase B — Immune-Mediated & Complement-Mediated Diseases
# ──────────────────────────────────────────────────────────────────────

LUPUS = "lupus"
ANCA = "anca"
ANTI_GBM = "antiGbm"
C3G = "c3"
MPGN = "mpgn"
DDD = "denseDepositDisease"
IRGN = "infectionRelated"

# ──────────────────────────────────────────────────────────────────────
# Phase C — Monoclonal & Systemic Diseases
# ──────────────────────────────────────────────────────────────────────

MGRS = "mgrs"
AMYLOIDOSIS = "amyloidosis"
CRYOGLOBULINEMIC = "cryoglobulinemic"
IMMUNOTACTOID = "immunotactoid"
FIBRILLARY = "fibrillaryGlomerulonephritis"

# ──────────────────────────────────────────────────────────────────────
# Phase D — Hereditary Diseases
# ──────────────────────────────────────────────────────────────────────

ALPORT = "alport"
TBMN = "thinBasementMembrane"
CFHR = "cfhr"
FABRY = "fabry"

# ──────────────────────────────────────────────────────────────────────
# Phase E — Secondary Glomerular Diseases
# ──────────────────────────────────────────────────────────────────────

DKD = "diabeticNephropathy"
DKD_WITH_GN = "diabeticNephropathyWithGN"
HBV_GN = "hbvAssociatedGN"
HCV_GN = "hcvAssociatedGN"
HIVAN = "hivan"
IGG4 = "igg4Related"
DRUG_INDUCED = "drugInducedGn"
PARANEOPLASTIC = "paraneoplastic"
SARCOIDOSIS = "sarcoidosisAssociatedGN"

# ──────────────────────────────────────────────────────────────────────
# Phase F — Kidney Transplant Glomerular Diseases
# ──────────────────────────────────────────────────────────────────────

RECURRENT_IGAN = "recurrentIgaNephropathy"
RECURRENT_FSGS = "recurrentFSGS"
RECURRENT_MN = "recurrentMembranous"
TRANSPLANT_GLOM = "transplantGlomerulopathy"
ABMR = "antibodyMediatedRejection"
TCMR = "tCellMediatedRejection"
CNI_TOXICITY = "cniToxicity"
BK_VIRUS = "bkVirusNephropathy"

# ──────────────────────────────────────────────────────────────────────
# Disease Categories
# ──────────────────────────────────────────────────────────────────────

CAT_PRIMARY = "primary_glomerular"
CAT_IMMUNE = "immune_mediated"
CAT_MONOCLONAL = "monoclonal_systemic"
CAT_HEREDITARY = "hereditary"
CAT_SECONDARY = "secondary"
CAT_TRANSPLANT = "transplant"


DISEASE_METADATA = {
    # ── Phase A ──
    IGA: {
        "name": "IgA Nephropathy",
        "category": CAT_PRIMARY,
        "phase": "A",
        "guideline_chapter": "Chapter 3: IgA Nephropathy / KDIGO 2025 IgAN and IgAV Guideline",
        "evidence_url": "https://kdigo.org/guidelines/iga-nephropathy/",
    },
    MEMBRANOUS: {
        "name": "Membranous Nephropathy",
        "category": CAT_PRIMARY,
        "phase": "A",
        "guideline_chapter": "Chapter 4: Membranous Nephropathy / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    FSGS: {
        "name": "Focal Segmental Glomerulosclerosis",
        "category": CAT_PRIMARY,
        "phase": "A",
        "guideline_chapter": "Chapter 6: Focal Segmental Glomerulosclerosis / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    MCD: {
        "name": "Minimal Change Disease",
        "category": CAT_PRIMARY,
        "phase": "A",
        "guideline_chapter": "Chapter 5: Minimal Change Disease / KDIGO 2025 Nephrotic Syndrome Guideline",
        "evidence_url": "https://kdigo.org/guidelines/nephrotic-syndrome-children/",
    },
    # ── Phase B ──
    LUPUS: {
        "name": "Lupus Nephritis",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 8: Lupus Nephritis / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    ANCA: {
        "name": "ANCA-Associated Vasculitis",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 9: Pauci-immune GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    ANTI_GBM: {
        "name": "Anti-GBM Crescentic GN",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 10: Anti-GBM Crescentic GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    C3G: {
        "name": "C3 Glomerulopathy",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 7: C3 Glomerulopathy / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    MPGN: {
        "name": "Membranoproliferative GN",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 7: Membranoproliferative GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    DDD: {
        "name": "Dense Deposit Disease",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 7: Dense Deposit Disease / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    IRGN: {
        "name": "Infection-Related Glomerulonephritis",
        "category": CAT_IMMUNE,
        "phase": "B",
        "guideline_chapter": "Chapter 11: Infection-Related GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    # ── Phase C ──
    MGRS: {
        "name": "Monoclonal Gammopathy of Renal Significance",
        "category": CAT_MONOCLONAL,
        "phase": "C",
        "guideline_chapter": "Chapter 12: Monoclonal Gammopathy of Renal Significance / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    AMYLOIDOSIS: {
        "name": "Renal Amyloidosis",
        "category": CAT_MONOCLONAL,
        "phase": "C",
        "guideline_chapter": "Chapter 14: Renal Amyloidosis / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    CRYOGLOBULINEMIC: {
        "name": "Cryoglobulinemic GN",
        "category": CAT_MONOCLONAL,
        "phase": "C",
        "guideline_chapter": "Chapter 11: Cryoglobulinemic GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    IMMUNOTACTOID: {
        "name": "Immunotactoid Glomerulopathy",
        "category": CAT_MONOCLONAL,
        "phase": "C",
        "guideline_chapter": "Chapter 13: Fibrillary GN / Immunotactoid Glomerulopathy / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    FIBRILLARY: {
        "name": "Fibrillary Glomerulonephritis",
        "category": CAT_MONOCLONAL,
        "phase": "C",
        "guideline_chapter": "Chapter 13: Fibrillary GN / Immunotactoid Glomerulopathy / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    # ── Phase D ──
    ALPORT: {
        "name": "Alport Syndrome",
        "category": CAT_HEREDITARY,
        "phase": "D",
        "guideline_chapter": "Chapter 15: Alport Syndrome / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    TBMN: {
        "name": "Thin Basement Membrane Nephropathy",
        "category": CAT_HEREDITARY,
        "phase": "D",
        "guideline_chapter": "Chapter 15: Thin Basement Membrane Nephropathy / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    CFHR: {
        "name": "CFHR-Related Disease",
        "category": CAT_HEREDITARY,
        "phase": "D",
        "guideline_chapter": "Chapter 7: Complement-Mediated Diseases / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    FABRY: {
        "name": "Fabry Disease (renal involvement)",
        "category": CAT_HEREDITARY,
        "phase": "D",
        "guideline_chapter": "Chapter 15: Fabry Disease / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    # ── Phase E ──
    DKD: {
        "name": "Diabetic Kidney Disease",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 4: Diabetes Management in CKD / KDIGO 2024 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/diabetes-ckd/",
    },
    DKD_WITH_GN: {
        "name": "Diabetic Kidney Disease with Superimposed GN",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 4: Diabetes Management in CKD / KDIGO 2024 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/diabetes-ckd/",
    },
    HBV_GN: {
        "name": "HBV-Associated Glomerulonephritis",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 11: Infection-Related GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    HCV_GN: {
        "name": "HCV-Associated Glomerulonephritis",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 11: Infection-Related GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    HIVAN: {
        "name": "HIV-Associated Nephropathy",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 11: HIV-Associated Nephropathy / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    IGG4: {
        "name": "IgG4-Related Kidney Disease",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 16: IgG4-Related Kidney Disease / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    DRUG_INDUCED: {
        "name": "Drug-Induced Glomerular Disease",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 16: Drug-Induced GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    PARANEOPLASTIC: {
        "name": "Paraneoplastic Glomerular Disease",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 16: Paraneoplastic GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    SARCOIDOSIS: {
        "name": "Sarcoidosis-Associated GN",
        "category": CAT_SECONDARY,
        "phase": "E",
        "guideline_chapter": "Chapter 16: Sarcoidosis-Associated GN / KDIGO 2021 Glomerular Diseases Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    # ── Phase F ──
    RECURRENT_IGAN: {
        "name": "Recurrent IgA Nephropathy (Transplant)",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 17: Recurrent Glomerular Disease in Transplant / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    RECURRENT_FSGS: {
        "name": "Recurrent FSGS (Transplant)",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 17: Recurrent Glomerular Disease in Transplant / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    RECURRENT_MN: {
        "name": "Recurrent Membranous Nephropathy (Transplant)",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 17: Recurrent Glomerular Disease in Transplant / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    TRANSPLANT_GLOM: {
        "name": "Transplant Glomerulopathy",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 17: Transplant Glomerulopathy / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    ABMR: {
        "name": "Antibody-Mediated Rejection",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 18: Antibody-Mediated Rejection / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    TCMR: {
        "name": "T Cell-Mediated Rejection",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 18: T Cell-Mediated Rejection / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    CNI_TOXICITY: {
        "name": "Calcineurin Inhibitor Toxicity",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 18: CNI Toxicity / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
    BK_VIRUS: {
        "name": "BK Virus Nephropathy",
        "category": CAT_TRANSPLANT,
        "phase": "F",
        "guideline_chapter": "Chapter 18: BK Virus Nephropathy / KDIGO 2021 Guideline",
        "evidence_url": "https://kdigo.org/guidelines/glomerulonephritis/",
    },
}

ALL_DISEASE_IDS = set(DISEASE_METADATA.keys())


def get_disease_meta(disease_id: str) -> dict:
    return DISEASE_METADATA.get(disease_id, {})


def get_disease_name(disease_id: str) -> str:
    meta = DISEASE_METADATA.get(disease_id, {})
    return meta.get("name", disease_id)


def get_diseases_by_phase(phase: str) -> list[tuple[str, dict]]:
    return [(k, v) for k, v in DISEASE_METADATA.items() if v.get("phase") == phase]


def get_diseases_by_category(category: str) -> list[tuple[str, dict]]:
    return [(k, v) for k, v in DISEASE_METADATA.items() if v.get("category") == category]

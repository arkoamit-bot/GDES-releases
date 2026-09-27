"""Controlled vocabulary for structured renal-biopsy findings.

A report can hold any number of findings per section, each optionally graded
(severity / extent / count of a stated denominator / site). "Other" plus a
description records an unusual finding without forcing a false code.

Observed marker results (IF/IHC rows) are kept apart from interpreted patterns
("full-house", "pauci-immune"): the IF_INTERPRETATION section holds the latter.

This is a proposed capture set for clinical/pathology acceptance, not a set of
diagnostic rules: nothing here computes a disease score from descriptors.
"""
from __future__ import annotations

OTHER = "other"

# Section -> (label, [(code, label), ...]). Codes are stable identifiers used by
# exports and clinical reasoning; labels may be reworded without a migration.
SECTIONS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "lm_glomerular": ("Light microscopy — glomeruli", [
        ("mesangial_hypercellularity", "Mesangial hypercellularity"),
        ("endocapillary_hypercellularity", "Endocapillary hypercellularity"),
        ("segmental_sclerosis", "Segmental sclerosis"),
        ("global_sclerosis", "Global sclerosis"),
        ("necrosis", "Fibrinoid necrosis"),
        ("crescent_cellular", "Crescents — cellular"),
        ("crescent_fibrocellular", "Crescents — fibrocellular"),
        ("crescent_fibrous", "Crescents — fibrous"),
        ("capillary_wall_thickening", "Capillary wall thickening"),
        ("gbm_spikes", "GBM spikes"),
        ("double_contours", "Double contours"),
        ("nodular_sclerosis", "Nodular (Kimmelstiel-Wilson) lesions"),
        ("glomerular_thrombi", "Glomerular thrombi"),
        (OTHER, "Other (describe)"),
    ]),
    "tubulointerstitial": ("Tubulointerstitium", [
        ("ifta", "IFTA (reported together)"),
        ("tubular_atrophy", "Tubular atrophy"),
        ("interstitial_fibrosis", "Interstitial fibrosis"),
        ("interstitial_inflammation", "Interstitial inflammation"),
        ("acute_tubular_injury", "Acute tubular injury"),
        ("rbc_casts", "Red-cell casts"),
        ("protein_casts", "Proteinaceous / hyaline casts"),
        ("tubulitis", "Tubulitis"),
        (OTHER, "Other (describe)"),
    ]),
    "vascular": ("Vessels", [
        ("arteriosclerosis", "Arteriosclerosis (intimal fibrosis)"),
        ("arteriolar_hyalinosis", "Arteriolar hyalinosis"),
        ("vasculitis", "Vascular inflammation / vasculitis"),
        ("tma_thrombi", "TMA — arteriolar/glomerular thrombi"),
        ("tma_mucoid_intimal", "TMA — mucoid intimal oedema"),
        ("tma_other", "TMA — other feature"),
        (OTHER, "Other (describe)"),
    ]),
    "if_marker": ("Immunofluorescence / IHC — marker result", [
        ("marker", "Marker result"),
    ]),
    "if_interpretation": ("Immunofluorescence — interpreted pattern", [
        ("mesangial_iga", "Mesangial IgA-dominant"),
        ("full_house", "Full-house (IgG/IgA/IgM/C3/C1q)"),
        ("granular_capillary_subendothelial", "Granular capillary wall — subendothelial"),
        ("granular_capillary_subepithelial", "Granular capillary wall — subepithelial"),
        ("linear_igg", "Linear IgG (anti-GBM pattern)"),
        ("pauci_immune", "Pauci-immune / no immune deposits"),
        ("mesangial_c3", "Mesangial C3"),
        ("mesangial_igg", "Mesangial IgG"),
        ("c3_dominant", "C3 dominant"),
        ("granular_mesangial_capillary", "Granular mesangial + capillary wall"),
        (OTHER, "Other (describe)"),
    ]),
    "em": ("Electron microscopy", [
        ("normal_ultrastructure", "Normal ultrastructure"),
        ("deposits_mesangial", "Deposits — mesangial"),
        ("deposits_subendothelial", "Deposits — subendothelial"),
        ("deposits_subepithelial", "Deposits — subepithelial"),
        ("deposits_intramembranous", "Deposits — intramembranous"),
        ("foot_process_effacement", "Foot-process effacement"),
        ("mesangial_matrix_expansion", "Mesangial matrix expansion"),
        ("gbm_thickening", "GBM thickening"),
        ("gbm_thinning", "GBM thinning"),
        ("gbm_irregularity", "GBM irregularity / lamellation / double contours"),
        ("organized_fibrillary", "Organized deposits — fibrillary"),
        ("organized_microtubular", "Organized deposits — microtubular"),
        ("cryoglobulin_like", "Cryoglobulin-like deposits"),
        ("tubuloreticular_inclusions", "Tubuloreticular inclusions"),
        (OTHER, "Other (describe)"),
    ]),
    "special_stain": ("Special stains / IHC", [
        ("congo_red", "Congo red"),
        ("dnajb9", "DNAJB9"),
        ("pla2r_tissue", "PLA2R (tissue)"),
        ("thsd7a_tissue", "THSD7A (tissue)"),
        ("c4d", "C4d"),
        ("sv40", "SV40 (polyoma)"),
        (OTHER, "Other stain (describe)"),
    ]),
}

SECTION_CHOICES = [(key, label) for key, (label, _codes) in SECTIONS.items()]
CODE_CHOICES = sorted({(c, lbl) for _s, (_l, codes) in SECTIONS.items() for c, lbl in codes},
                      key=lambda kv: kv[0])

IF_MARKERS = [
    ("IgG", "IgG"), ("IgA", "IgA"), ("IgM", "IgM"), ("C3", "C3"), ("C1q", "C1q"),
    ("kappa", "Kappa"), ("lambda", "Lambda"), ("fibrinogen", "Fibrin/fibrinogen"),
    ("C4d", "C4d"), ("IgG_subclass", "IgG subclass"), (OTHER, "Other marker"),
]

# Which modality status governs a section: a finding cannot be recorded for a
# modality the report states was not done / unavailable.
SECTION_MODALITY = {
    "lm_glomerular": "lm_status", "tubulointerstitial": "lm_status",
    "vascular": "lm_status", "if_marker": "if_status",
    "if_interpretation": "if_status", "em": "em_status",
    "special_stain": "ihc_status",
}

# Biopsy summary Booleans that overlap repeatable findings. A present finding
# may fill a blank summary; an explicit "absent" summary alongside a present
# finding is a contradiction the user must resolve.
SUMMARY_LINKS = {
    "crescents_present": {"crescent_cellular", "crescent_fibrocellular", "crescent_fibrous"},
    "necrosis_present": {"necrosis"},
    "arteriolar_hyalinosis": {"arteriolar_hyalinosis"},
}

# Legacy single-choice Biopsy.if_pattern / em_findings -> (section, code). The
# legacy IF field recorded an interpreted pattern, so it maps to the
# interpretation section, never to a fabricated marker reading.
LEGACY_IF_MAP = {
    "mesangial_iga": "mesangial_iga", "full_house": "full_house",
    "granular_capillary_subendothelial": "granular_capillary_subendothelial",
    "granular_capillary_subepithelial": "granular_capillary_subepithelial",
    "linear_igg": "linear_igg", "pauci_immune": "pauci_immune",
    "mesangial_c3": "mesangial_c3", "mesangial_igg": "mesangial_igg",
    "c3_dominant": "c3_dominant",
    "granular_mesangial_capillary": "granular_mesangial_capillary",
    OTHER: OTHER,
}
LEGACY_EM_MAP = {
    "normal": "normal_ultrastructure",
    "mesangial_expansion": "mesangial_matrix_expansion",
    "subendothelial_deposits": "deposits_subendothelial",
    "subepithelial_deposits": "deposits_subepithelial",
    "mesangial_deposits": "deposits_mesangial",
    "intramembranous_deposits": "deposits_intramembranous",
    "foot_process_effacement": "foot_process_effacement",
    "basement_membrane_thinning": "gbm_thinning",
    "basement_membrane_irregularity": "gbm_irregularity",
    "electron_dense_cryoglobulin": "cryoglobulin_like",
    "fibrillary_deposits": "organized_fibrillary",
    OTHER: OTHER,
}


def codes_for(section: str) -> set[str]:
    return {code for code, _ in SECTIONS.get(section, ("", []))[1]}


def label_for(section: str, code: str) -> str:
    for c, lbl in SECTIONS.get(section, ("", []))[1]:
        if c == code:
            return lbl
    return code


def section_label(section: str) -> str:
    return SECTIONS.get(section, (section, []))[0]

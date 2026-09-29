"""Biopsy -> clinical-reasoning features.

Observed features come from structured findings on the current report (and
the typed light-microscopy summary). Legacy single-choice IF/EM values are
read through the same vocabulary, so the exact option the old form saved
(e.g. ``foot_process_effacement``) is recognised -- the old consumer searched
the value for the substring "podocyte" and never matched it.

Expectations derived from the diagnosis label ("lupus -> full-house") are
returned separately as inferences and never reported as observed findings.
"""
from __future__ import annotations

from pathology import diagnosis as dxrules
from pathology import findings as vocab

# (section, code) -> rule feature.
FINDING_FEATURES = {
    ("if_interpretation", "mesangial_iga"): "mesangialIga",
    ("if_interpretation", "full_house"): "fullHouse",
    ("if_interpretation", "linear_igg"): "linearIgg",
    ("if_interpretation", "c3_dominant"): "c3Dominant",
    ("if_interpretation", "granular_capillary_subepithelial"): "subepithelial",
    ("if_interpretation", "granular_capillary_subendothelial"): "subendothelialDeposits",
    ("lm_glomerular", "crescent_cellular"): "crescents",
    ("lm_glomerular", "crescent_fibrocellular"): "crescents",
    ("lm_glomerular", "crescent_fibrous"): "crescents",
    ("lm_glomerular", "segmental_sclerosis"): "segmentalSclerosis",
    ("lm_glomerular", "mesangial_hypercellularity"): "mesangialProliferation",
    ("lm_glomerular", "gbm_spikes"): "subepithelial",
    ("lm_glomerular", "double_contours"): "tramTrack",
    ("lm_glomerular", "glomerular_thrombi"): "tmLesions",
    ("vascular", "tma_thrombi"): "tmLesions",
    ("vascular", "tma_mucoid_intimal"): "tmLesions",
    ("em", "deposits_subepithelial"): "subepithelial",
    ("em", "deposits_subendothelial"): "subendothelialDeposits",
    ("em", "deposits_intramembranous"): "denseDeposits",
    ("em", "foot_process_effacement"): "podocyteEffacement",
    ("em", "gbm_irregularity"): "tramTrack",
    ("em", "organized_fibrillary"): "fibrillaryDeposits",
    ("em", "organized_microtubular"): "immunotactoid",
    ("special_stain", "congo_red"): "congoRedPositive",
}

# Diagnosis family / label -> expected findings (INFERENCES, labelled as such).
_FAMILY_EXPECTATIONS = {
    dxrules.IGAN: {"mesangialIga"},
    dxrules.LUPUS: {"fullHouse"},
    dxrules.MN: {"subepithelial"},
    dxrules.FSGS: {"segmentalSclerosis"},
    dxrules.MCD: {"podocyteEffacement"},
    dxrules.ANTI_GBM: {"linearIgg"},
    dxrules.C3G: {"c3Dominant"},
}


def _marker_features(f):
    out = set()
    if f.marker == "IgA" and f.site in ("", "mesangial"):
        out.add("mesangialIga")
    if f.marker == "IgG" and f.distribution == "linear":
        out.add("linearIgg")
    return out


def biopsy_features(biopsy):
    """Return (observed, absent, inferred) feature sets for one biopsy."""
    observed, absent, inferred = set(), set(), set()

    report = biopsy.reports.filter(role="local", is_current=True).first() \
        if hasattr(biopsy, "reports") else None
    # A finalized central/adjudication report, when present, is the better read.
    for role in ("adjudication", "central"):
        r = biopsy.reports.filter(role=role, is_current=True).first()
        if r is not None:
            report = r
            break

    if report is not None:
        for f in report.findings.all():
            if f.section == "if_marker":
                feats = _marker_features(f)
            else:
                feat = FINDING_FEATURES.get((f.section, f.code))
                feats = {feat} if feat else set()
            if not feats:
                continue
            if f.presence == "present":
                observed |= feats
            elif f.presence == "absent":
                absent |= feats
    else:
        # Legacy single-choice fields, read through the same vocabulary.
        if biopsy.if_pattern:
            code = vocab.LEGACY_IF_MAP.get(biopsy.if_pattern)
            feat = FINDING_FEATURES.get(("if_interpretation", code))
            if feat:
                observed.add(feat)
        if biopsy.em_findings:
            code = vocab.LEGACY_EM_MAP.get(biopsy.em_findings)
            feat = FINDING_FEATURES.get(("em", code))
            if feat:
                observed.add(feat)

    if biopsy.crescents_present or (biopsy.crescent_pct and biopsy.crescent_pct > 0):
        observed.add("crescents")
    elif biopsy.crescents_present is False:
        absent.add("crescents")

    dx = getattr(biopsy, "diagnosis", None) if _has(biopsy, "diagnosis") else None
    label = (dx.diagnosis if dx else "") or ""
    q = dxrules.qualifiers(label)
    inferred |= _FAMILY_EXPECTATIONS.get(q.get("family", ""), set())
    if q.get("subtype") == "ddd":
        inferred.add("denseDeposits")
    return observed, absent, inferred


def _has(obj, attr):
    try:
        getattr(obj, attr)
        return True
    except Exception:
        return False

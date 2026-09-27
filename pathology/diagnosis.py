"""One structured diagnosis family, with the qualifiers each diagnosis implies.

Several diagnosis labels already state a qualifier that another field asks
again: "FSGS - primary" states primary/secondary, "FSGS - collapsing variant"
states the variant, "Lupus nephritis class IV" states the ISN/RPS class. The
repeated fields could contradict the label and the record would save anyway.

The mapping below is explicit, keyed by the exact diagnosis value (no substring
guessing): a diagnosis may PREFILL its qualifiers, and a contradicting entry is
reported for the user to resolve. Broad group, pathogenesis, cohort and
aetiology are related classification axes, not synonyms, and are not forced.
"""
from __future__ import annotations

from . import lupus as lupus_rules

import re

IGAN, LUPUS, FSGS, MN = "igan", "lupus", "fsgs", "mn"
# Families without a disease-specific score panel.
MCD, ANCA, ANTI_GBM, C3G, DKD = "mcd", "anca", "anti_gbm", "c3g", "dkd"

# Diagnosis value -> {"family": ..., qualifier: value}. Unlisted diagnoses have
# no family, so no disease-specific score panel is "theirs".
QUALIFIERS: dict[str, dict[str, str]] = {
    "IgA nephropathy": {"family": IGAN},
    "IgA vasculitis nephritis": {"family": IGAN},
    "Diabetic kidney disease + IgA nephropathy": {"family": IGAN},

    "Membranous nephropathy - PLA2R positive": {"family": MN},
    "Membranous nephropathy - PLA2R negative": {"family": MN},
    "Membranous nephropathy - secondary/associated": {
        "family": MN, "primary_secondary": "secondary"},
    "Diabetic kidney disease + membranous nephropathy": {"family": MN},

    "FSGS - primary": {"family": FSGS, "primary_secondary": "primary"},
    "FSGS - secondary/adaptive": {"family": FSGS, "primary_secondary": "secondary"},
    # Genetic FSGS is neither "primary" nor "secondary" in this scheme.
    "FSGS - genetic/suspected genetic": {"family": FSGS},
    "FSGS - collapsing variant": {"family": FSGS, "variant": "collapsing"},
    "FSGS - tip lesion variant": {"family": FSGS, "variant": "tip"},
    "FSGS - cellular variant": {"family": FSGS, "variant": "cellular"},
    "FSGS - perihilar variant": {"family": FSGS, "variant": "perihilar"},
    "FSGS - NOS": {"family": FSGS, "variant": "nos"},
    "Diabetic kidney disease + FSGS": {"family": FSGS},

    "Diabetic kidney disease + lupus nephritis": {"family": LUPUS},

    "Minimal change disease": {"family": MCD},
    "ANCA-associated pauci-immune crescentic GN - MPO": {"family": ANCA},
    "ANCA-associated pauci-immune crescentic GN - PR3": {"family": ANCA},
    "ANCA-associated pauci-immune crescentic GN - ANCA negative": {"family": ANCA},
    "Diabetic kidney disease + ANCA GN": {"family": ANCA},
    "Anti-GBM disease": {"family": ANTI_GBM},
    "C3 glomerulopathy - C3 glomerulonephritis": {"family": C3G},
    "C3 glomerulopathy - dense deposit disease": {"family": C3G, "subtype": "ddd"},
    "Diabetic kidney disease only - no GN": {"family": DKD},
}
for _cls in lupus_rules.CLASSES:
    QUALIFIERS[lupus_rules.diagnosis_for_class(_cls)] = {
        "family": LUPUS, "isn_rps_class": _cls}


def _norm(text: str) -> str:
    """Lowercase, drop punctuation and bracketed abbreviations, collapse
    whitespace: 'IgA nephropathy (IgAN)' -> 'iga nephropathy'."""
    t = re.sub(r"\([^)]*\)", " ", (text or "").lower())
    t = re.sub(r"[^a-z0-9+]+", " ", t)
    return " ".join(t.split())


# Legacy / free-text values (the diagnosis column was free text before it had
# choices) -> current diagnosis value. Curated whole-phrase matches on the
# normalised text; anything not listed stays unmapped (no family), rather than
# being guessed from a substring.
LEGACY_ALIASES: dict[str, str] = {
    "iga": "IgA nephropathy",
    "igan": "IgA nephropathy",
    "iga nephropathy": "IgA nephropathy",
    "iga nephritis": "IgA nephropathy",
    "mcd": "Minimal change disease",
    "minimal change": "Minimal change disease",
    "minimal change disease": "Minimal change disease",
    "anti gbm": "Anti-GBM disease",
    "anti gbm disease": "Anti-GBM disease",
    "goodpasture": "Anti-GBM disease",
    "goodpasture syndrome": "Anti-GBM disease",
}
# Legacy phrases that establish only the FAMILY (the specific value -- PLA2R
# status, FSGS variant, ANCA serotype -- was never stated, so none is invented).
LEGACY_FAMILY_ALIASES: dict[str, str] = {
    "membranous": MN, "membranous nephropathy": MN, "mn": MN, "pmn": MN,
    "primary membranous nephropathy": MN,
    "fsgs": FSGS, "focal segmental glomerulosclerosis": FSGS,
    "anca vasculitis": ANCA, "anca associated vasculitis": ANCA, "anca gn": ANCA,
    "anca associated gn": ANCA, "pauci immune gn": ANCA,
    "pauci immune crescentic gn": ANCA,
    "c3 glomerulopathy": C3G, "c3g": C3G, "c3gn": C3G,
    "dkd": DKD, "diabetic nephropathy": DKD, "diabetic kidney disease": DKD,
    "lupus nephritis": LUPUS,
}

# Score panel key (biopsy form prefix) -> the family it belongs to.
PANEL_FAMILY = {"igan": IGAN, "lupus": LUPUS, "fsgs": FSGS, "mn": MN}
PANEL_LABEL = {"igan": "Oxford MEST-C", "lupus": "Lupus nephritis",
               "fsgs": "FSGS", "mn": "Membranous"}


def canonical(diagnosis: str) -> str:
    value = (diagnosis or "").strip()
    if value in QUALIFIERS:
        return value
    return LEGACY_ALIASES.get(_norm(value), value)


def qualifiers(diagnosis: str) -> dict[str, str]:
    value = canonical(diagnosis)
    q = dict(QUALIFIERS.get(value, {}))
    if not q:
        fam = LEGACY_FAMILY_ALIASES.get(_norm(value), "")
        if fam:
            q = {"family": fam}
    return q


def family(diagnosis: str) -> str:
    return qualifiers(diagnosis).get("family", "")


def families(diagnoses) -> set[str]:
    return {f for f in (family(d) for d in diagnoses if d) if f}


def check_panels(diagnosis: str, active_panels, *, additional=(), override_reason=""):
    """Errors for score panels that do not belong to the stated diagnosis.

    A panel for another family can be kept only when a coexisting diagnosis of
    that family is recorded, or with an explained override (mixed/uncertain).
    Returns {panel_key: message}.
    """
    allowed = families([diagnosis, *additional])
    errors = {}
    if (override_reason or "").strip():
        return errors
    for key in active_panels:
        fam = PANEL_FAMILY.get(key)
        if fam and fam not in allowed:
            errors[key] = (
                f"The {PANEL_LABEL[key]} panel was filled but the diagnosis is "
                f"'{diagnosis or 'not stated'}'. Clear the panel, record the "
                f"coexisting diagnosis, or give a reason this panel applies.")
    return errors


def reconcile_fsgs(diagnosis: str, dx_primary_secondary: str,
                   panel_primary_secondary: str, panel_variant: str):
    """Return (primary_secondary, variant, errors) for an FSGS biopsy.

    errors maps a form ("dx" | "fsgs") and field to a message. Blank values are
    prefilled from the diagnosis; contradictions are never resolved silently.
    """
    q = qualifiers(diagnosis)
    errors: dict[tuple[str, str], str] = {}
    implied_ps = q.get("primary_secondary", "")
    implied_variant = q.get("variant", "")

    def stated(v):
        return v if v and v != "unknown" else ""

    dx_ps, panel_ps = stated(dx_primary_secondary), stated(panel_primary_secondary)
    if implied_ps and dx_ps and dx_ps != implied_ps:
        errors[("dx", "primary_secondary")] = (
            f"The diagnosis '{diagnosis}' states {implied_ps}; this field says {dx_ps}.")
    if implied_ps and panel_ps and panel_ps != implied_ps:
        errors[("fsgs", "primary_secondary")] = (
            f"The diagnosis '{diagnosis}' states {implied_ps}; the FSGS panel says {panel_ps}.")
    if dx_ps and panel_ps and dx_ps != panel_ps and not errors:
        errors[("fsgs", "primary_secondary")] = (
            f"Primary/secondary is stated twice and disagrees ({dx_ps} vs {panel_ps}).")
    if implied_variant and panel_variant and panel_variant != implied_variant:
        errors[("fsgs", "variant")] = (
            f"The diagnosis '{diagnosis}' states the {implied_variant} variant; "
            f"the FSGS panel says {panel_variant}.")

    ps = implied_ps or dx_ps or panel_ps or (dx_primary_secondary or panel_primary_secondary or "")
    variant = implied_variant or panel_variant or ""
    return ps, variant, errors


def effective_qualifiers(biopsy) -> dict[str, str]:
    """The qualifiers a biopsy states, from its panels or its diagnosis."""
    dx = getattr(biopsy, "diagnosis", None)
    diagnosis = dx.diagnosis if dx else ""
    q = qualifiers(diagnosis)
    out = {"family": q.get("family", "")}
    fsgs = getattr(biopsy, "fsgs", None) if _has(biopsy, "fsgs") else None
    lupus = getattr(biopsy, "lupus", None) if _has(biopsy, "lupus") else None
    out["variant"] = (fsgs.variant if fsgs and fsgs.variant else q.get("variant", ""))
    out["primary_secondary"] = (
        (dx.primary_secondary if dx and dx.primary_secondary else "")
        or q.get("primary_secondary", "")
        or (fsgs.primary_secondary if fsgs else ""))
    out["isn_rps_class"] = (lupus_rules.class_from_diagnosis(diagnosis)
                            or (lupus.isn_rps_class if lupus else ""))
    return out


def _has(biopsy, related):
    try:
        getattr(biopsy, related)
        return True
    except Exception:
        return False

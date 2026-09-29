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


def reconcile_qualifiers(diagnosis: str, dx_primary_secondary: str, panel_variant: str = ""):
    """Return (primary_secondary, variant, errors) for a biopsy's diagnosis.

    Primary/secondary has ONE owner, GNDiagnosis.primary_secondary; a
    diagnosis that states it ("FSGS - primary", "Membranous nephropathy -
    secondary/associated") must agree with it, and a blank is filled from the
    diagnosis. The FSGS variant is asked on the FSGS panel only for a
    diagnosis that does not state it. "unknown" and the genetic FSGS label are
    never forced into primary or secondary. errors maps (form, field) -> message.
    """
    q = qualifiers(diagnosis)
    errors: dict[tuple[str, str], str] = {}
    implied_ps = q.get("primary_secondary", "")
    implied_variant = q.get("variant", "")
    dx_ps = dx_primary_secondary if dx_primary_secondary not in ("", "unknown") else ""
    if implied_ps and dx_ps and dx_ps != implied_ps:
        errors[("dx", "primary_secondary")] = (
            f"The diagnosis '{diagnosis}' states {implied_ps}; this field says {dx_ps}.")
    if implied_variant and panel_variant and panel_variant != implied_variant:
        errors[("fsgs", "variant")] = (
            f"The diagnosis '{diagnosis}' states the {implied_variant} variant; "
            f"the FSGS panel says {panel_variant}.")
    ps = implied_ps or dx_primary_secondary or ""
    variant = implied_variant or panel_variant or ""
    return ps, variant, errors


def project_fsgs_panel(biopsy):
    """Write the canonical primary/secondary (the diagnosis record's, or the
    one its label states) onto the FSGS panel, which keeps the column only
    for older readers. Nothing edits the panel's copy directly."""
    from .models import FSGSPathology, GNDiagnosis
    dx = GNDiagnosis.objects.filter(biopsy=biopsy).first()
    if dx is None:
        return
    ps = qualifiers(dx.diagnosis).get("primary_secondary", "") or dx.primary_secondary
    FSGSPathology.objects.filter(biopsy=biopsy).exclude(primary_secondary=ps).update(
        primary_secondary=ps)


def sync_stated_primary_secondary(dx_obj):
    """After a diagnosis change (amendment, review): a label that states
    primary/secondary sets it. Returns (old, new) when it changed, else None,
    so the caller can say so."""
    implied = qualifiers(dx_obj.diagnosis).get("primary_secondary", "")
    if implied and dx_obj.primary_secondary != implied:
        old = dx_obj.primary_secondary
        dx_obj.primary_secondary = implied
        dx_obj.save(update_fields=["primary_secondary"])
        return old, implied
    return None


def qualifier_table() -> dict[str, dict[str, str]]:
    """Every diagnosis choice -> what its label states (family, score panel,
    primary/secondary, FSGS variant, ISN/RPS class), for the entry form to
    show derived values read-only. Built from QUALIFIERS: no substring match."""
    from patients import choices
    panel_for = {fam: key for key, fam in PANEL_FAMILY.items()}
    out = {}
    for value, _label in choices.SPECIFIC_GN_DIAGNOSIS:
        q = qualifiers(value)
        row = {k: v for k, v in q.items() if k in ("family", "primary_secondary",
                                                  "variant", "isn_rps_class")}
        if panel_for.get(q.get("family", "")):
            row["panel"] = panel_for[q["family"]]
        out[value] = row
    return out


def effective_qualifiers(biopsy) -> dict[str, str]:
    """The qualifiers a biopsy states, from its panels or its diagnosis."""
    dx = getattr(biopsy, "diagnosis", None)
    diagnosis = dx.diagnosis if dx else ""
    q = qualifiers(diagnosis)
    out = {"family": q.get("family", "")}
    fsgs = getattr(biopsy, "fsgs", None) if _has(biopsy, "fsgs") else None
    lupus = getattr(biopsy, "lupus", None) if _has(biopsy, "lupus") else None
    out["variant"] = (fsgs.variant if fsgs and fsgs.variant else q.get("variant", ""))
    # Primary/secondary is owned by the diagnosis record; the FSGS panel's
    # column is a projection of it and is read only for rows saved earlier.
    out["primary_secondary"] = (
        q.get("primary_secondary", "")
        or (dx.primary_secondary if dx and dx.primary_secondary else "")
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

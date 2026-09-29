"""One map from laboratory codes (and their aliases) to meaning.

Clinical reasoning used to test for the PRESENCE of a result row (a negative
ANCA counted as ANCA), matched aliases inconsistently (``anti_dsDNA`` compared
against an already-lowercased code, so the catalogue's ``anti_dsdna`` never
matched), and treated ACR, PCR and 24-hour protein as one variable. This
module is the single place that says what a code is and how to read a value.
"""
from __future__ import annotations

from decimal import Decimal

# Canonical code -> aliases seen in imports / older rows (all lowercase).
ALIASES: dict[str, set[str]] = {
    "anca": {"anca", "anca_typing", "anca_ifa"},
    "mpo_anca": {"mpo_anca", "anti_mpo", "mpo"},
    "pr3_anca": {"pr3_anca", "anti_pr3", "pr3"},
    "anti_gbm": {"anti_gbm", "antigbm"},
    "anti_pla2r": {"anti_pla2r", "pla2r"},
    "ana": {"ana"},
    "anti_dsdna": {"anti_dsdna", "dsdna", "anti_ds_dna"},
    "c3": {"c3", "complement_c3"},
    "c4": {"c4", "complement_c4"},
    "albumin": {"albumin", "alb", "serum_albumin"},
    "upcr": {"upcr", "pcr", "urine_pcr"},
    "uacr": {"uacr", "acr", "urine_acr"},
    "utp_24h": {"utp_24h", "proteinuria_24h", "urine_protein_24h"},
    "hbsag": {"hbsag", "hbv", "hepatitis_b"},
    "anti_hcv": {"anti_hcv", "hcv", "hepatitis_c"},
    "urine_rbc": {"urine_rbc", "hematuria"},
    "urine_rbc_casts": {"urine_rbc_casts", "rbc_casts"},
}
_REVERSE = {alias: canonical for canonical, aliases in ALIASES.items() for alias in aliases}


def canonical(code: str) -> str:
    c = (code or "").strip().lower()
    return _REVERSE.get(c, c)


POSITIVE, NEGATIVE, EQUIVOCAL, NOT_PERFORMED, UNKNOWN = (
    "positive", "negative", "equivocal", "not_performed", "unknown")
LOW, NORMAL, HIGH = "low", "normal", "high"

_TEXT = {
    "positive": POSITIVE, "pos": POSITIVE, "+": POSITIVE, "reactive": POSITIVE,
    "detected": POSITIVE, "present": POSITIVE,
    "negative": NEGATIVE, "neg": NEGATIVE, "-": NEGATIVE, "non-reactive": NEGATIVE,
    "nonreactive": NEGATIVE, "not detected": NEGATIVE, "absent": NEGATIVE,
    "equivocal": EQUIVOCAL, "borderline": EQUIVOCAL, "indeterminate": EQUIVOCAL,
    "not done": NOT_PERFORMED, "not performed": NOT_PERFORMED, "nd": NOT_PERFORMED,
    "low": LOW, "normal": NORMAL, "high": HIGH,
}


def interpret(result) -> str:
    """positive / negative / equivocal / not_performed / low / normal / high /
    unknown for one LabResult.

    The qualitative read wins when stated. Otherwise a numeric value is read
    against the test's reference range (above range = positive for an
    antibody, high for an analyte). Never "positive" merely because a row
    exists.
    """
    text = (getattr(result, "value_text", "") or "").strip().lower()
    if text:
        if text in _TEXT:
            return _TEXT[text]
        if text.startswith("pos"):
            return POSITIVE
        if text.startswith("neg"):
            return NEGATIVE
    value = getattr(result, "value_numeric", None)
    test = getattr(result, "test", None)
    if value is None or test is None:
        return UNKNOWN
    value = Decimal(value)
    if test.ref_high is not None and value > test.ref_high:
        return HIGH
    if test.ref_low is not None and value < test.ref_low:
        return LOW
    if test.ref_high is not None or test.ref_low is not None:
        return NORMAL
    return UNKNOWN


def is_positive(result) -> bool:
    """Antibody/serology positivity: a positive read, or a level above range."""
    return interpret(result) in (POSITIVE, HIGH)


def latest_by_code(results):
    """Newest CURRENT result per canonical code.

    Explicit date policy: the result (report) date, then the sample date,
    then entry time. A null sample date no longer sorts a result to the
    bottom (or top) of the list, and there is no arbitrary last-20 window.
    """
    import datetime as dt

    def key(r):
        return (r.result_date or dt.date.min, r.sample_date or dt.date.min,
                r.created_at.timestamp() if r.created_at else 0.0, r.pk or 0)

    out = {}
    for r in results:
        code = canonical(r.test.code if r.test else "")
        if not code:
            continue
        if code not in out or key(r) > key(out[code]):
            out[code] = r
    return out

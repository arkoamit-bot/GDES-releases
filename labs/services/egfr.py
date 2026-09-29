"""
CKD-EPI 2021 creatinine equation (race-free).

The formula version is returned alongside the value and stored on the derived
LabResult, so an eGFR slope computed across several years stays reproducible even
if the registry later adopts a different equation (e.g. a cystatin-C based one).

Preference order:
  1. gdes_core.egfr — the single authoritative implementation (bundled in the
     desktop build via BGDDR.spec THIRD_PARTY).
  2. Local implementation — used when gdes_core is not importable (source runs
     without the package installed). It is the same equation with the same
     contract as the implementation that preceded gdes_core: the value is
     rounded to 0.1 and stamped "CKD-EPI-2021-creatinine", so a result derived
     either way is interchangeable in a slope.

The first local fallback (2026-08-23) fixed alpha at -0.241 for both sexes,
returned an unrounded float and stamped "CKD-EPI 2021 (local fallback)". Male
eGFR at creatinine below kappa was therefore under-estimated (60 y, 0.6 mg/dL:
107.8 instead of 110.5). Results derived in that window keep their original
stamp; `reconcile_linked_facts` lists them for a governed re-derivation instead
of rewriting history silently.
"""
from __future__ import annotations

from decimal import Decimal

FORMULA_VERSION = "CKD-EPI-2021-creatinine"
DEFECTIVE_FALLBACK_VERSION = "CKD-EPI 2021 (local fallback)"


def _local_ckd_epi_2021(scr_mg_dl: float, age_years: float, sex: str) -> tuple[float, str]:
    """Return (eGFR mL/min/1.73m^2 rounded to 0.1, formula_version).

    Inker LA et al., N Engl J Med 2021; 385:1736-1749 (NIDDK adult equations):

        eGFR = 142 * min(Scr/k, 1)^a * max(Scr/k, 1)^-1.200 * 0.9938^Age
               * 1.012 [if female]

        k = 0.7 (female), 0.9 (male)
        a = -0.241 (female), -0.302 (male)

    sex: "F" (female) or anything else treated as male.
    """
    scr = float(scr_mg_dl)
    age = float(age_years)
    if scr <= 0 or age < 0:
        raise ValueError("scr_mg_dl must be positive and age_years non-negative")
    female = str(sex).upper().startswith("F")

    kappa = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302

    ratio = scr / kappa
    egfr = (142.0
            * (min(ratio, 1.0) ** alpha)
            * (max(ratio, 1.0) ** -1.200)
            * (0.9938 ** age))
    if female:
        egfr *= 1.012
    return round(egfr, 1), FORMULA_VERSION


def _local_egfr_to_decimal(value: float) -> Decimal:
    return Decimal(str(value))


try:
    from gdes_core.egfr import ckd_epi_2021  # noqa: F401
    from gdes_core.egfr import egfr_to_decimal  # noqa: F401
    try:
        from gdes_core.egfr import FORMULA_VERSION  # noqa: F401,F811
    except ImportError:  # pragma: no cover - older gdes_core
        pass
except ImportError:
    ckd_epi_2021 = _local_ckd_epi_2021
    egfr_to_decimal = _local_egfr_to_decimal

"""
CKD-EPI 2021 creatinine equation (race-free).

The formula version is returned alongside the value and stored on the derived
LabResult, so an eGFR slope computed across several years stays reproducible even
if the registry later adopts a different equation (e.g. a cystatin-C based one).

Preference order:
  1. gdes_core.egfr — the single authoritative implementation (bundled in the
     desktop build via BGDDR.spec THIRD_PARTY).
  2. Local fallback — used when gdes_core is not importable (source runs without
     the package installed, or any environment where the dependency is missing).
     The fallback implements the same CKD-EPI 2021 equation so behaviour is
     identical either way.
"""
from __future__ import annotations

import math
from decimal import Decimal
from typing import Tuple

# Try the authoritative implementation first.
try:
    from gdes_core.egfr import ckd_epi_2021 as _ckd_epi_2021  # noqa: F401
    from gdes_core.egfr import egfr_to_decimal as _egfr_to_decimal  # noqa: F401
    from gdes_core.egfr import FORMULA_VERSION  # noqa: F401
except ImportError:
    # Local fallback — CKD-EPI 2021 creatinine equation (race-free).
    # Inker LA et al., N Engl J Med 2021; 385:1736-1749.
    #
    # eGFR = 142 * min(Scr/κ, 1)^α * max(Scr/κ, 1)^(-1.200)
    #        * 0.9938^Age * [1.012 if female]
    #
    #   κ = 0.7 (female), 0.9 (male)
    #   α = -0.241 (both sexes in the 2021 equation)
    _FORMULA_VERSION = "CKD-EPI 2021 (local fallback)"

    def _ckd_epi_2021(scr_mg_dl: float, age_years: float, sex: str) -> Tuple[float, str]:
        if scr_mg_dl < 0 or age_years < 0:
            raise ValueError("scr_mg_dl and age_years must be non-negative")
        kappa = 0.7 if sex == "F" else 0.9
        alpha = -0.241
        ratio = scr_mg_dl / kappa
        min_term = min(ratio, 1.0) ** alpha
        max_term = max(ratio, 1.0) ** (-1.200)
        age_factor = 0.9938 ** age_years
        sex_factor = 1.012 if sex == "F" else 1.0
        egfr = 142.0 * min_term * max_term * age_factor * sex_factor
        return (egfr, _FORMULA_VERSION)

    def _egfr_to_decimal(value: float) -> Decimal:
        return Decimal(str(value))

    FORMULA_VERSION = _FORMULA_VERSION
    ckd_epi_2021 = _ckd_epi_2021
    egfr_to_decimal = _egfr_to_decimal

else:
    FORMULA_VERSION = globals().get("FORMULA_VERSION", "gdes_core")
    ckd_epi_2021 = _ckd_epi_2021
    egfr_to_decimal = _egfr_to_decimal

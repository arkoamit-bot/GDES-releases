"""
CKD-EPI 2021 creatinine equation (race-free).

The formula version is returned alongside the value and stored on the derived
LabResult, so an eGFR slope computed across several years stays reproducible even
if the registry later adopts a different equation (e.g. a cystatin-C based one).
"""
from __future__ import annotations

from decimal import Decimal

FORMULA_VERSION = "CKD-EPI-2021-creatinine"


def ckd_epi_2021(scr_mg_dl: float, age_years: float, sex: str) -> tuple[float, str]:
    """Return (eGFR mL/min/1.73m^2 rounded to 0.1, formula_version).

    sex: "F" (female) or anything else treated as male.
    scr_mg_dl: serum creatinine in mg/dL.
    """
    scr = float(scr_mg_dl)
    age = float(age_years)
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


def egfr_to_decimal(value: float) -> Decimal:
    return Decimal(str(value))

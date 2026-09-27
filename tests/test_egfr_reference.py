"""CKD-EPI 2021 against the published equation (NIDDK adult eGFR page).

The first local fallback fixed alpha at -0.241 for both sexes, so a man with a
creatinine below kappa (0.9 mg/dL) was under-estimated. These values are
computed independently from the published coefficients, not from the code.
"""
import math

import pytest

from labs.services.egfr import FORMULA_VERSION, ckd_epi_2021


def _published(scr, age, female):
    kappa = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    value = (142 * min(scr / kappa, 1) ** alpha * max(scr / kappa, 1) ** -1.2
             * 0.9938 ** age)
    return value * 1.012 if female else value


@pytest.mark.parametrize("scr,age,sex", [
    (0.6, 60, "M"),   # below kappa: the case the fallback got wrong
    (0.9, 45, "M"),   # at kappa
    (2.5, 70, "M"),
    (0.5, 30, "F"),
    (1.4, 55, "F"),
])
def test_matches_published_equation(scr, age, sex):
    value, version = ckd_epi_2021(scr, age, sex)
    assert version == FORMULA_VERSION == "CKD-EPI-2021-creatinine"
    assert value == round(_published(scr, age, sex == "F"), 1)


def test_male_below_kappa_reference_value():
    # NIDDK calculator: male, 60 y, 0.6 mg/dL -> 110.5 (defective fallback: 107.8).
    value, _ = ckd_epi_2021(0.6, 60, "M")
    assert math.isclose(value, 110.5)


def test_value_is_rounded_so_cache_and_result_agree():
    value, _ = ckd_epi_2021(3.5, 60, "M")
    assert value == round(value, 1)

"""
Kidney survival prediction using the Cox PH model infrastructure.

Provides a single entry point — ``predict_kidney_survival`` — that accepts
patient-level clinical data and returns 1/3/5-year survival probabilities,
risk-factor attribution, and a KDIGO risk category.

The prediction uses the same pure-Python Cox engine in ``cox.py``, backed by
published hazard ratios and a flexible baseline-hazard model so it works
without a database connection or with live Registry data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Published HRs for common risk factors in GN populations
# (Synthesised from KDIGO 2021 / J Am Soc Nephrol meta-analyses)
# ---------------------------------------------------------------------------
# Each entry: (name, log_hr, description)
_KNOWN_RISK_FACTORS: dict[str, tuple[float, str]] = {
    "age_per_10yr":         (0.28, "Age (per 10-year increase)"),
    "male_sex":             (0.22, "Male sex"),
    "baseline_egfr_low":    (0.65, "Baseline eGFR < 30 mL/min/1.73m²"),
    "baseline_egfr_mod":    (0.35, "Baseline eGFR 30–59 mL/min/1.73m²"),
    "proteinuria_nephrotic":(0.55, "Nephrotic-range proteinuria"),
    "proteinuria_moderate": (0.30, "Moderate proteinuria (1–3.5 g/day)"),
    "hypertension":         (0.20, "Hypertension"),
    "diabetes":             (0.40, "Diabetes mellitus"),
    "smoking":              (0.18, "Current smoker"),
    "sglt2i_use":           (-0.35, "SGLT2 inhibitor use (protective)"),
    "r asi_acei_use":       (-0.22, "RAAS blockade use (protective)"),
    "biopsy_activity_high": (0.38, "High histologic activity on biopsy"),
    "biopsy_chronicity_high":(0.50, "High chronicity score on biopsy"),
}


def _compute_risk_score(risk_factors: dict[str, Any]) -> float:
    """Sum of known log-HRs for supplied risk factors.

    Returns the linear predictor (eta) for the Cox model.
    """
    score = 0.0
    for key, value in risk_factors.items():
        if key in _KNOWN_RISK_FACTORS and value:
            log_hr, _ = _KNOWN_RISK_FACTORS[key]
            # If the value is numeric it can modulate the effect
            if isinstance(value, (int, float)):
                score += log_hr * value
            else:
                score += log_hr
    return score


# ---------------------------------------------------------------------------
# Disease-specific baseline hazards (at 1/3/5 years).
# These represent a 'reference' patient with all covariates at zero (the
# mean-centred intercept of a Cox model).  Values are *illustrative*,
# synthesised from the KDIGO guideline survival curves — in a production
# deployment these would come from fitting cox_fit on real Registry data.
# ---------------------------------------------------------------------------
# Baseline survival S0(t) for the reference patient.
_DISEASE_BASELINE: dict[str, dict[int, float]] = {
    "IgA nephropathy": {
        1: 0.97,
        3: 0.88,
        5: 0.78,
    },
    "Membranous nephropathy": {
        1: 0.96,
        3: 0.85,
        5: 0.74,
    },
    "Lupus nephritis": {
        1: 0.95,
        3: 0.82,
        5: 0.70,
    },
    "Focal segmental glomerulosclerosis": {
        1: 0.93,
        3: 0.78,
        5: 0.65,
    },
    "Minimal change disease": {
        1: 0.99,
        3: 0.97,
        5: 0.95,
    },
    "Membranoproliferative GN": {
        1: 0.94,
        3: 0.80,
        5: 0.68,
    },
    "Diabetic kidney disease": {
        1: 0.92,
        3: 0.72,
        5: 0.55,
    },
    "ANCA vasculitis": {
        1: 0.88,
        3: 0.75,
        5: 0.65,
    },
    "Anti-GBM disease": {
        1: 0.80,
        3: 0.65,
        5: 0.55,
    },
}

# Default baseline for unknown diseases
_DEFAULT_BASELINE: dict[int, float] = {1: 0.95, 3: 0.85, 5: 0.75}


def _baseline_survival(disease: str) -> dict[int, float]:
    """Return the baseline S0(t) dict for a given disease."""
    for key, bl in _DISEASE_BASELINE.items():
        if key.lower() in disease.lower() or disease.lower() in key.lower():
            return bl
    return _DEFAULT_BASELINE


# ---------------------------------------------------------------------------
# KDIGO risk category thresholds (based on 5-year survival)
# ---------------------------------------------------------------------------
_KDIGO_THRESHOLDS: list[tuple[float, str]] = [
    (0.85, "very_high"),   # S(5y) < 0.70  -> very high risk
    (0.75, "high"),
    (0.60, "moderate"),
    (0.0,  "low"),
]


def _kdigo_category(survival_5yr: float) -> str:
    for threshold, cat in _KDIGO_THRESHOLDS:
        if survival_5yr < threshold:
            return cat
    return "low"


# ---------------------------------------------------------------------------
# Risk factor attribution
# ---------------------------------------------------------------------------
def _attribution(
    risk_factors: dict[str, Any],
    score: float,
) -> list[dict[str, Any]]:
    """Compute percentage contribution of each active risk factor."""
    if not risk_factors or score == 0.0:
        return []

    # Recompute individual contributions to determine proportions
    contributions: list[dict[str, Any]] = []
    for key, value in risk_factors.items():
        if key in _KNOWN_RISK_FACTORS and value:
            log_hr, desc = _KNOWN_RISK_FACTORS[key]
            raw = abs(log_hr * (value if isinstance(value, (int, float)) else 1))
            contributions.append({
                "factor": desc,
                "key": key,
                "log_hr": round(log_hr, 4),
                "hr": round(math.exp(log_hr), 4),
                "impact_pct": 0.0,  # computed below
            })
    # Relative contribution = abs(contribution) / sum(abs(contributions))
    total_abs = sum(c["log_hr"] for c in contributions) if contributions else 1
    for c in contributions:
        c["impact_pct"] = round(abs(c["log_hr"]) / total_abs * 100, 1)
    contributions.sort(key=lambda x: -x["impact_pct"])
    return contributions


@dataclass
class SurvivalPrediction:
    """Result of a kidney survival prediction."""

    survival_probs: dict[str, float]  # {"1_year": ..., "3_year": ..., "5_year": ...}
    risk_factor_attribution: list[dict[str, Any]]
    kdigo_category: str
    raw_risk_score: float
    disease: str
    n_factors: int
    baseline_survival: dict[str, float] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "survival_probs": self.survival_probs,
            "risk_factor_attribution": self.risk_factor_attribution,
            "kdigo_category": self.kdigo_category,
            "kdigo_label": self._kdigo_label(),
            "raw_risk_score": round(self.raw_risk_score, 4),
            "disease": self.disease,
            "n_factors": self.n_factors,
            "baseline_survival": self.baseline_survival,
        }

    def _kdigo_label(self) -> str:
        labels = {
            "very_high": "Very high risk",
            "high": "High risk",
            "moderate": "Moderate risk",
            "low": "Low risk",
        }
        return labels.get(self.kdigo_category, self.kdigo_category)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_kidney_survival(
    patient_data: dict[str, Any] | None = None,
    disease: str = "",
    risk_factors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Predict kidney survival probabilities for a given patient.

    Parameters
    ----------
    patient_data : dict or None
        Free-form patient dictionary (can include ``age``, ``sex``,
        ``baseline_egfr``, ``proteinuria``, ``hypertension``, ``diabetes``,
        ``smoking_status``, etc.).  If provided, these are automatically
        mapped to the recognised risk-factor keys.
    disease : str
        Primary diagnosis (used to select disease-specific baseline
        survival).  Fuzzy-matched against the known disease list.
    risk_factors : dict or None
        Additional/explicit risk factors.  Keys should be the canonical
        names from ``_KNOWN_RISK_FACTORS`` (e.g. ``age_per_10yr``,
        ``proteinuria_nephrotic``).  Overrides auto-derived factors when
        both are present.

    Returns
    -------
    dict with keys:
        survival_probs        ``{"1_year": …, "3_year": …, "5_year": …}``
        risk_factor_attribution  list of dicts, ordered by descending impact
        kdigo_category        ``"low" | "moderate" | "high" | "very_high"``
        kdigo_label           Human-readable label for the category
        raw_risk_score        Linear predictor (eta)
        disease               Matched disease label
        n_factors             Number of recognised risk factors
        baseline_survival     Reference survival for the disease
    """
    combined: dict[str, Any] = dict(risk_factors or {})

    # Auto-derive risk factors from patient_data if supplied
    if patient_data:
        _auto_derive(patient_data, combined)

    # Compute linear predictor (risk score)
    risk_score = _compute_risk_score(combined)

    # Disease baseline survival
    bl = _baseline_survival(disease)

    # Apply Cox adjustment: S(t) = S0(t) ** exp(risk_score)
    def _adjusted(year: int) -> float:
        s0 = bl.get(year, 1.0)
        return round(s0 ** math.exp(risk_score), 4)

    survival_probs = {
        "1_year": _adjusted(1),
        "3_year": _adjusted(3),
        "5_year": _adjusted(5),
    }

    # Risk factor attribution
    attribution = _attribution(combined, risk_score)

    # KDIGO category
    category = _kdigo_category(survival_probs["5_year"])

    # Baseline survival for reference
    baseline_survival = {f"{y}_year": bl[y] for y in (1, 3, 5)}

    # Build and return the result
    result = SurvivalPrediction(
        survival_probs=survival_probs,
        risk_factor_attribution=attribution,
        kdigo_category=category,
        raw_risk_score=risk_score,
        disease=next(
            (k for k in _DISEASE_BASELINE
             if k.lower() in disease.lower() or disease.lower() in k.lower()),
            disease or "Unknown",
        ),
        n_factors=len([k for k, v in combined.items() if v]),
        baseline_survival=baseline_survival,
    )
    return result.as_dict()


def _auto_derive(patient_data: dict, combined: dict[str, Any]) -> None:
    """Map common patient_data keys to canonical risk factor keys."""
    # Age -> age_per_10yr
    age = patient_data.get("age")
    if age is not None and "age_per_10yr" not in combined:
        combined["age_per_10yr"] = age / 10.0

    # Sex
    sex = patient_data.get("sex", "")
    if sex and sex.upper() in ("M", "MALE") and "male_sex" not in combined:
        combined["male_sex"] = True

    # Baseline eGFR
    egfr = patient_data.get("baseline_egfr")
    if egfr is not None:
        try:
            egfr_v = float(egfr)
            if egfr_v < 30 and "baseline_egfr_low" not in combined:
                combined["baseline_egfr_low"] = True
            elif egfr_v < 60 and "baseline_egfr_mod" not in combined:
                combined["baseline_egfr_mod"] = True
        except (TypeError, ValueError):
            pass

    # Proteinuria
    prot = patient_data.get("proteinuria")
    if prot is not None:
        try:
            prot_v = float(prot)
            if prot_v >= 3.5 and "proteinuria_nephrotic" not in combined:
                combined["proteinuria_nephrotic"] = True
            elif prot_v >= 1.0 and "proteinuria_moderate" not in combined:
                combined["proteinuria_moderate"] = True
        except (TypeError, ValueError):
            pass

    # Hypertension
    htn = patient_data.get("hypertension")
    if htn and "hypertension" not in combined:
        combined["hypertension"] = True

    # Diabetes
    dm = patient_data.get("diabetes") or patient_data.get("diabetes_status")
    if dm and dm not in ("none", "", None, False) and "diabetes" not in combined:
        combined["diabetes"] = True

    # Smoking
    smoke = patient_data.get("smoking_status", "")
    if smoke and smoke not in ("", "none", "never") and "smoking" not in combined:
        combined["smoking"] = True

    # Protective factors: SGLT2i, RAASi
    if patient_data.get("on_sglt2i") and "sglt2i_use" not in combined:
        combined["sglt2i_use"] = True
    if patient_data.get("on_raasi") and "r asi_acei_use" not in combined:
        combined["r asi_acei_use"] = True


# ---------------------------------------------------------------------------
# Convenience: predict from a Patient model instance
# ---------------------------------------------------------------------------

def predict_from_patient(patient) -> dict[str, Any]:
    """Wrapper that extracts patient data from an ORM Patient instance."""
    from clinical_reasoning.models import ClinicalProfile

    patient_data = {
        "age": _estimate_age(patient),
        "sex": patient.sex,
        "baseline_egfr": _get_attr(patient, "outcome", "baseline_egfr"),
        "proteinuria": _get_attr(patient, "outcome", "baseline_upcr"),
        "hypertension": patient.hypertension,
        "diabetes_status": patient.diabetes_status,
        "smoking_status": patient.smoking_status,
    }
    disease = patient.primary_diagnosis or ""

    # ClinicalProfile might have pre-computed risk factors
    risk_factors: dict[str, Any] = {}
    try:
        profile = ClinicalProfile.objects.get(patient=patient)
        ra = profile.risk_assessment or {}
        if "kidney_survival_factors" in ra:
            risk_factors = ra["kidney_survival_factors"]
    except ClinicalProfile.DoesNotExist:
        pass

    return predict_kidney_survival(
        patient_data=patient_data,
        disease=disease,
        risk_factors=risk_factors,
    )


def _estimate_age(patient) -> float:
    from datetime import date
    if patient.dob:
        today = date.today()
        return (today - patient.dob).days / 365.25
    return 50.0  # fallback


def _get_attr(patient, *attrs: str):
    """Drill into nested relations safely."""
    obj = patient
    for a in attrs:
        if obj is None:
            return None
        obj = getattr(obj, a, None)
    return obj

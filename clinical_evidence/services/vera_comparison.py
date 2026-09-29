"""Vera Health GDES Comparison Engine.

Compares the GDES management plan against the Vera Health
independent recommendation, calculating agreement scores and
highlighting differences.

Handles both structured Vera output (medications, monitoring)
and text-based clinical reasoning from the Vera API.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def compare_recommendations(
    gdes_plan: Any,
    vera_rec: Any,
    diagnosis: str,
) -> dict[str, Any]:
    """Compare GDES and Vera recommendations side-by-side.

    Args:
        gdes_plan: ManagementPlan dataclass from GDES.
        vera_rec: VeraRecommendation from Vera Health.
        diagnosis: Primary diagnosis string.

    Returns:
        Comparison dict with agreement scores, differences,
        and side-by-side data.
    """
    has_vera_structured = bool(
        vera_rec is not None
        and getattr(vera_rec, "medications", None)
    )

    if has_vera_structured:
        med_comparison = _compare_medications(gdes_plan, vera_rec)
        monitoring_comparison = _compare_monitoring(gdes_plan, vera_rec)
    else:
        med_comparison = {"items": [], "agreement": None}
        monitoring_comparison = {"items": [], "agreement": None}

    diagnosis_agreement = _compare_diagnosis(gdes_plan, vera_rec, diagnosis)

    all_items = []
    all_items.extend(med_comparison.get("items", []))
    all_items.extend(monitoring_comparison.get("items", []))
    all_items.append(diagnosis_agreement)

    if all_items:
        scores = [
            item.get("agreement", 100)
            for item in all_items
            if item.get("agreement") is not None
        ]
        overall_score = round(sum(scores) / len(scores)) if scores else None
    else:
        overall_score = None

    if overall_score is not None:
        if overall_score >= 90:
            agreement_level = "High Agreement"
        elif overall_score >= 70:
            agreement_level = "Moderate Agreement"
        else:
            agreement_level = "Review Recommended"
    else:
        agreement_level = "Vera Review Available"

    vera_has_clinical_summary = bool(
        vera_rec is not None
        and bool(getattr(vera_rec, "clinical_summary", ""))
    )

    return {
        "overall_score": overall_score,
        "agreement_level": agreement_level,
        "diagnosis": diagnosis_agreement,
        "medications": med_comparison,
        "monitoring": monitoring_comparison,
        "side_by_side": _build_side_by_side(gdes_plan, vera_rec),
        "differences": _extract_differences(all_items),
        "vera_has_structured_data": has_vera_structured,
        "vera_has_clinical_summary": vera_has_clinical_summary,
    }


def _compare_medications(gdes_plan: Any, vera_rec: Any) -> dict[str, Any]:
    """Compare medication recommendations between GDES and Vera."""
    gdes_drugs = _extract_gdes_drugs(gdes_plan)
    vera_drugs = _extract_vera_drugs(vera_rec)

    all_drug_names = list(set(
        [d["drug"] for d in gdes_drugs] + [d["drug"] for d in vera_drugs]
    ))

    items = []
    for drug_name in all_drug_names:
        gdes_match = next(
            (d for d in gdes_drugs if d["drug"] == drug_name), None
        )
        vera_match = next(
            (d for d in vera_drugs if d["drug"] == drug_name), None
        )

        if gdes_match and vera_match:
            dose_agreement = _compare_doses(gdes_match, vera_match)
            items.append({
                "drug": drug_name,
                "gdes_dose": gdes_match.get("dose", "N/A"),
                "vera_dose": vera_match.get("recommended_dose", "N/A"),
                "gdes_present": True,
                "vera_present": True,
                "agreement": dose_agreement,
                "note": vera_match.get("dose_adjustments", [None])[0]
                if vera_match.get("dose_adjustments") else None,
            })
        elif gdes_match:
            items.append({
                "drug": drug_name,
                "gdes_dose": gdes_match.get("dose", "N/A"),
                "vera_dose": "Not recommended",
                "gdes_present": True,
                "vera_present": False,
                "agreement": 60,
                "note": "Drug in GDES but not in Vera recommendation",
            })
        elif vera_match:
            items.append({
                "drug": drug_name,
                "gdes_dose": "Not in plan",
                "vera_dose": vera_match.get("recommended_dose", "N/A"),
                "gdes_present": False,
                "vera_present": True,
                "agreement": 60,
                "note": "Drug in Vera but not in GDES plan",
            })

    if items:
        avg = round(sum(i["agreement"] for i in items) / len(items))
    else:
        avg = 85

    return {"items": items, "agreement": avg}


def _compare_monitoring(gdes_plan: Any, vera_rec: Any) -> dict[str, Any]:
    """Compare monitoring recommendations."""
    gdes_mon = _extract_gdes_monitoring(gdes_plan)
    vera_mon = _extract_vera_monitoring(vera_rec)

    gdes_params = {m.get("parameter", "").lower() for m in gdes_mon}
    vera_params = {m.get("parameter", "").lower() for m in vera_mon}

    common = gdes_params & vera_params
    gdes_only = gdes_params - vera_params
    vera_only = vera_params - gdes_params

    total = gdes_params | vera_params
    if total:
        score = round(100 * len(common) / len(total))
    else:
        score = 85

    items = []
    for param in sorted(total):
        items.append({
            "parameter": param,
            "in_gdes": param in gdes_params,
            "in_vera": param in vera_params,
            "agreement": 100 if param in common else 50,
        })

    return {
        "items": items,
        "agreement": score,
        "gdes_only": sorted(gdes_only),
        "vera_only": sorted(vera_only),
    }


def _compare_diagnosis(
    gdes_plan: Any, vera_rec: Any, diagnosis: str
) -> dict[str, Any]:
    """Compare diagnosis between GDES and Vera."""
    gdes_disease = ""
    if hasattr(gdes_plan, "disease_name"):
        gdes_disease = gdes_plan.disease_name
    elif isinstance(gdes_plan, dict):
        gdes_disease = gdes_plan.get("disease_name", "")

    vera_disease = vera_rec.diagnosis if hasattr(vera_rec, "diagnosis") else ""

    match = False
    if gdes_disease and vera_disease:
        gdes_lower = gdes_disease.lower()
        vera_lower = vera_disease.lower()
        match = (
            gdes_lower in vera_lower
            or vera_lower in gdes_lower
            or _diseases_equivalent(gdes_lower, vera_lower)
        )

    return {
        "gdes_diagnosis": gdes_disease or diagnosis,
        "vera_diagnosis": vera_disease or diagnosis,
        "agreement": 100 if match else 75,
        "note": "Diagnoses concordant" if match else "Diagnoses partially concordant",
    }


def _diseases_equivalent(d1: str, d2: str) -> bool:
    aliases = {
        "iga nephropathy": "iga nephropathy / iga vasculitis nephritis",
        "focal segmental glomerulosclerosis": "fsgs",
        "membranous nephropathy": "membranous",
        "lupus nephritis": "lupus",
        "anca-associated vasculitis": "anca vasculitis",
    }
    d1_norm = aliases.get(d1, d1)
    d2_norm = aliases.get(d2, d2)
    return d1_norm == d2_norm


def _compare_doses(gdes_med: dict, vera_med: dict) -> int:
    """Compare doses between GDES and Vera. Returns agreement score 0-100."""
    gdes_dose = str(gdes_med.get("dose", "")).lower()
    vera_dose = str(
        vera_med.get("recommended_dose", "")
        or vera_med.get("dose", "")
    ).lower()

    if not gdes_dose or not vera_dose:
        return 75

    gdes_nums = _extract_dose_numbers(gdes_dose)
    vera_nums = _extract_dose_numbers(vera_dose)

    if gdes_nums and vera_nums:
        ratio = min(gdes_nums) / max(vera_nums) if max(vera_nums) > 0 else 0
        if ratio > 0.8:
            return 95
        if ratio > 0.5:
            return 75
        return 50

    if gdes_dose.split()[0] == vera_dose.split()[0]:
        return 90

    return 70


def _extract_dose_numbers(dose_str: str) -> list[float]:
    import re
    numbers = re.findall(r"(\d+(?:\.\d+)?)", dose_str)
    return [float(n) for n in numbers if float(n) > 0]


def _extract_gdes_drugs(gdes_plan: Any) -> list[dict]:
    drugs = []
    if not gdes_plan:
        return drugs
    for tier_name in ("first_line", "second_line", "rescue_therapy"):
        tier = getattr(gdes_plan, tier_name, None)
        if tier and isinstance(tier, list):
            for item in tier:
                if isinstance(item, dict):
                    drugs.append({
                        "drug": item.get("drug", item.get("medication", "")),
                        "dose": item.get("dose", ""),
                        "tier": tier_name,
                    })
    return drugs


def _extract_vera_drugs(vera_rec: Any) -> list[dict]:
    meds = []
    if hasattr(vera_rec, "medications"):
        for med in vera_rec.medications:
            if isinstance(med, dict):
                meds.append(med)
    return meds


def _extract_gdes_monitoring(gdes_plan: Any) -> list[dict]:
    mon = []
    if not gdes_plan:
        return mon
    monitoring = getattr(gdes_plan, "monitoring", None)
    if monitoring and isinstance(monitoring, list):
        for item in monitoring:
            if isinstance(item, dict):
                mon.append(item)
    return mon


def _extract_vera_monitoring(vera_rec: Any) -> list[dict]:
    mon = []
    if hasattr(vera_rec, "monitoring"):
        for item in vera_rec.monitoring:
            if isinstance(item, dict):
                mon.append(item)
    return mon


def _build_side_by_side(gdes_plan: Any, vera_rec: Any) -> dict[str, Any]:
    """Build a side-by-side comparison data structure."""
    return {
        "gdes": {
            "medications": [
                f"{d.get('drug', '')} - {d.get('dose', '')}"
                for d in _extract_gdes_drugs(gdes_plan)
            ],
            "monitoring": [
                m.get("parameter", "")
                for m in _extract_gdes_monitoring(gdes_plan)
            ],
        },
        "vera": {
            "medications": [
                f"{m.get('drug', '')} - {m.get('recommended_dose', m.get('dose', ''))}"
                for m in _extract_vera_drugs(vera_rec)
            ],
            "monitoring": [
                m.get("parameter", "")
                for m in _extract_vera_monitoring(vera_rec)
            ],
            "clinical_summary": getattr(vera_rec, "clinical_summary", "")
            if vera_rec else "",
        },
    }


def _extract_differences(items: list[dict]) -> list[str]:
    """Extract clinically significant differences."""
    diffs = []
    for item in items:
        if item.get("agreement", 100) is not None and item.get("agreement", 100) < 75:
            drug = item.get("drug") or item.get("parameter", "")
            gdes_val = item.get("gdes_dose") or item.get("gdes_diagnosis", "")
            vera_val = item.get("vera_dose") or item.get("vera_diagnosis", "")
            if gdes_val and vera_val and gdes_val != vera_val:
                diffs.append(
                    f"{drug}: GDES suggests {gdes_val} vs Vera recommends {vera_val}"
                )
    return diffs

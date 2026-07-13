import math
import warnings
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Clinical Calculators
# ---------------------------------------------------------------------------

def egfr_ckd_epi_2021(creatinine_mg_dl: float, age: int, sex: str, race: str = "other") -> float:
    """CKD-EPI 2021 eGFR calculator (race-free).

    Args:
        creatinine_mg_dl: Serum creatinine in mg/dL
        age: Age in years
        sex: "male" or "female"
        race: Ignored in 2021 equation (kept for API compat)

    Returns:
        eGFR in mL/min/1.73m²
    """
    if creatinine_mg_dl <= 0:
        return 0.0
    kappa = 0.7 if sex == "female" else 0.9
    alpha = -0.241 if sex == "female" else -0.302
    gender_factor = 1.018 if sex == "female" else 1.0

    scr_kappa = creatinine_mg_dl / kappa
    if scr_kappa <= 1:
        ratio = scr_kappa ** alpha
    else:
        ratio = scr_kappa ** (-1.200)

    egfr = 142.0 * ratio * (0.9938 ** age) * gender_factor
    return round(max(egfr, 0), 1)


def bsa_mosteller(height_cm: float, weight_kg: float) -> float:
    """Mosteller body surface area formula.

    BSA (m²) = sqrt(height_cm * weight_kg / 3600)
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    return round(math.sqrt(height_cm * weight_kg / 3600), 2)


def upcr_to_24h_utp(upcr_mg_mg: float, weight_kg: float) -> float:
    """Convert UPCR (mg/mg) to estimated 24h urine protein (g/day).

    Uses: UTP (g/day) ≈ UPCR × estimated 24h creatinine (mg/day)
    Estimated 24h creatinine from weight: ~20 mg/kg for women, ~25 mg/kg for men
    (Using average 22.5 mg/kg for ungendered estimation)
    """
    if upcr_mg_mg <= 0 or weight_kg <= 0:
        return 0.0
    est_24h_creatinine_mg = 22.5 * weight_kg
    return round(upcr_mg_mg * est_24h_creatinine_mg / 1000, 2)


def utp_to_upcr(utp_g_day: float, weight_kg: float) -> float:
    """Convert 24h urine protein (g/day) back to estimated UPCR (mg/mg)."""
    if utp_g_day <= 0 or weight_kg <= 0:
        return 0.0
    est_24h_creatinine_mg = 22.5 * weight_kg
    return round((utp_g_day * 1000) / est_24h_creatinine_mg, 4)


def proteinuria_category(upcr_mg_mg: float) -> str:
    """Classify proteinuria by UPCR threshold.

    Returns: "nephrotic" (>=3.5), "subnephrotic" (0.5-3.5), "normal" (<0.5)
    """
    if upcr_mg_mg >= 3.5:
        return "nephrotic"
    if upcr_mg_mg >= 0.5:
        return "subnephrotic"
    return "normal"


def renal_dose_adjustment(drug_class: str, egfr: float, dose_pct: int = 100) -> dict:
    """Simplified renal dose adjustment for common nephrology drugs.

    Returns dict with adjusted dose info.
    """
    adjustments = {
        "mycophenolate": [
            (60, 100, "No adjustment needed at this eGFR"),
            (30, 50, "Reduce to 50% dose or extend interval"),
            (15, 25, "Reduce to 25% dose; consider discontinuation"),
        ],
        "azathioprine": [
            (30, 50, "Reduce to 50% dose; monitor TPMT if available"),
            (10, 25, "Reduce to 25% dose"),
        ],
        "cyclophosphamide": [
            (30, 67, "Reduce to 2/3 dose"),
            (10, 50, "Reduce to 1/2 dose; avoid in severe renal impairment"),
        ],
        "tacrolimus": [
            (30, 50, "Reduce dose; monitor levels closely"),
            (10, 25, "Significant reduction required"),
        ],
        "ciclosporin": [
            (30, 50, "Reduce dose; monitor trough levels"),
        ],
        "colchicine": [
            (30, 50, "Reduce to 50% dose"),
            (10, 25, "Use with extreme caution"),
        ],
        "allopurinol": [
            (30, 50, "Reduce to 50% dose"),
            (10, 25, "Reduce to 25% or use febuxostat instead"),
        ],
        "doxycycline": [
            (15, 100, "No adjustment needed; preferred tetracycline in CKD"),
        ],
        "trimethoprim_sulfamethoxazole": [
            (30, 50, "Reduce frequency; risk of hyperkalemia"),
        ],
    }

    drug_lower = drug_class.lower().replace(" ", "_").replace("-", "_")
    if drug_lower not in adjustments:
        return {
            "drug": drug_class,
            "egfr": egfr,
            "adjustment": "No specific renal dosing guidance available; consult pharmacist",
            "dose_pct": dose_pct,
        }

    for threshold_egfr, pct, note in adjustments[drug_lower]:
        if egfr >= threshold_egfr:
            return {
                "drug": drug_class,
                "egfr": egfr,
                "adjustment": note,
                "dose_pct": min(dose_pct, pct),
            }

    return {
        "drug": drug_class,
        "egfr": egfr,
        "adjustment": "Severe renal impairment - specialist guidance required",
        "dose_pct": 25,
    }


def kdigo_heatmap_point(egfr: float, upcr: float) -> dict:
    """Map a patient to a KDIGO heat-map risk zone.

    Risk levels:
        Green  (low):    G1-G2 + A1
        Yellow (moderate): G3a + A1, or G1-G2 + A2
        Orange (high):   G3b-G4 + A1, or G3a-G4 + A2, or G1-G2 + A3
        Red    (very high): G5 any A, or any G + A3

    Returns: {"egfr_zone": str, "proteinuria_zone": str, "risk": str, "color": str}
    """
    # eGFR zone
    if egfr >= 90:
        egfr_zone = "G1"
    elif egfr >= 60:
        egfr_zone = "G2"
    elif egfr >= 45:
        egfr_zone = "G3a"
    elif egfr >= 30:
        egfr_zone = "G3b"
    elif egfr >= 15:
        egfr_zone = "G4"
    else:
        egfr_zone = "G5"

    # Proteinuria zone (ACR-based, using UPCR as proxy)
    if upcr < 0.15:
        proteinuria_zone = "A1"
    elif upcr < 0.5:
        proteinuria_zone = "A1"
    elif upcr < 3.5:
        proteinuria_zone = "A2"
    else:
        proteinuria_zone = "A3"

    # Risk classification
    g = int(egfr_zone[1]) if egfr_zone[1].isdigit() else (3.5 if "a" in egfr_zone else 3.5)
    a = int(proteinuria_zone[1])

    if g <= 2 and a <= 1:
        risk, color = "Low risk", "green"
    elif (egfr_zone == "G3a" and a <= 1) or (g <= 2 and a == 2):
        risk, color = "Moderately increased risk", "yellow"
    elif (egfr_zone in ("G3b", "G4") and a <= 2) or (g <= 2 and a == 3):
        risk, color = "High risk", "orange"
    else:
        risk, color = "Very high risk", "red"

    return {
        "egfr": egfr,
        "egfr_zone": egfr_zone,
        "upcr": upcr,
        "proteinuria_zone": proteinuria_zone,
        "risk": risk,
        "color": color,
    }


# ---------------------------------------------------------------------------
# Override tracking helpers
# ---------------------------------------------------------------------------

def build_override_summary(result) -> dict:
    """Build an override summary dict from a DecisionResult with overrides."""
    if not hasattr(result, "override_reason") or not result.override_reason:
        return {"overridden": False}
    return {
        "overridden": True,
        "reason": result.override_reason,
        "alternative_diagnosis": getattr(result, "alternative_diagnosis", ""),
        "clinician_notes": getattr(result, "clinician_notes", ""),
        "overridden_at": str(result.override_at) if hasattr(result, "override_at") and result.override_at else None,
    }


# ---------------------------------------------------------------------------
# Disease Profiles (original)
# ---------------------------------------------------------------------------

DISEASE_PROFILES = [
    {
        "id": "iga",
        "name": "IgA nephropathy or IgA vasculitis nephritis",
        "tags": ["Nephritic", "IgA-mediated", "Often biopsy-defined"],
        "base": 2,
        "rules": [
            (["sediment", "hematuria"], 2, "Dysmorphic hematuria supports glomerular inflammation."),
            (["sediment", "casts"], 3, "RBC casts point to active glomerulonephritis."),
            (["feature", "grossHematuria"], 3, "Gross hematuria can occur with IgA nephropathy, often around mucosal infection."),
            (["feature", "postInfectious"], 1, "Infection-timed hematuria keeps IgA nephropathy and infection-related GN in view."),
            (["feature", "purpura"], 3, "Purpura plus kidney findings raises IgA vasculitis nephritis."),
            (["feature", "arthritis"], 1, "Arthralgia is compatible with IgA vasculitis."),
            (["biopsy", "mesangialIga"], 6, "Dominant mesangial IgA is a defining biopsy clue."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria is common and should be quantified."),
            (["proteinuria", "nephrotic"], 1, "Nephrotic-range proteinuria can mark higher-risk IgA disease."),
        ],
        "source_note": "KDIGO's glomerular disease suite notes that IgAN/IgAV guidance was updated in 2025.",
    },
    {
        "id": "membranous",
        "name": "Membranous nephropathy",
        "tags": ["Nephrotic", "PLA2R-associated", "Secondary causes matter"],
        "base": 1,
        "rules": [
            (["proteinuria", "nephrotic"], 4, "Nephrotic-range proteinuria is a classic presentation."),
            (["albumin", "low"], 2, "Hypoalbuminemia supports nephrotic syndrome physiology."),
            (["sediment", "bland"], 2, "A bland sediment fits a podocytopathy or membranous pattern."),
            (["lab", "pla2r"], 5, "PLA2R positivity strongly supports primary membranous nephropathy in the right setting."),
            (["biopsy", "subepithelial"], 5, "Subepithelial deposits or spikes are characteristic biopsy clues."),
            (["lab", "hepatitis"], 1, "Infection screening matters when membranous nephropathy is suspected."),
            (["lab", "anaDsDna"], -1, "Positive lupus serology shifts the differential toward lupus membranous disease."),
        ],
        "source_note": "KDIGO 2021 glomerular disease guidance includes membranous nephropathy in the disease-specific chapters.",
    },
    {
        "id": "mcd",
        "name": "Minimal change disease",
        "tags": ["Nephrotic", "Podocyte injury", "Common in children"],
        "base": 1,
        "rules": [
            (["ageGroup", "child"], 3, "Childhood nephrotic syndrome is often steroid-sensitive minimal change disease."),
            (["proteinuria", "nephrotic"], 4, "Abrupt nephrotic syndrome is a typical pattern."),
            (["albumin", "low"], 2, "Low serum albumin supports nephrotic syndrome."),
            (["sediment", "bland"], 2, "Bland sediment supports a podocytopathy."),
            (["biopsy", "podocyteEffacement"], 5, "Diffuse foot-process effacement is the key biopsy clue."),
            (["sediment", "casts"], -2, "RBC casts make isolated minimal change disease less likely."),
        ],
        "source_note": "KDIGO 2025 guidance specifically updates nephrotic syndrome in children; adult minimal change disease remains in the glomerular disease suite.",
    },
    {
        "id": "fsgs",
        "name": "Focal segmental glomerulosclerosis",
        "tags": ["Nephrotic or mixed", "Primary or secondary", "Biopsy pattern"],
        "base": 1,
        "rules": [
            (["proteinuria", "nephrotic"], 3, "FSGS can present with nephrotic-range proteinuria."),
            (["proteinuria", "subnephrotic"], 1, "Secondary FSGS may have subnephrotic proteinuria."),
            (["albumin", "low"], 1, "Hypoalbuminemia supports primary podocyte injury if severe."),
            (["sediment", "hematuria"], 1, "Microscopic hematuria can coexist."),
            (["biopsy", "segmentalSclerosis"], 6, "Segmental sclerosis is the defining pathologic clue."),
            (["biopsy", "podocyteEffacement"], 2, "Diffuse effacement supports a primary podocytopathy pattern."),
            (["feature", "diabetes"], 1, "Metabolic or adaptive stress can contribute to secondary sclerosis."),
        ],
        "source_note": "KDIGO 2021 glomerular disease guidance includes adult FSGS and emphasizes distinguishing primary from secondary patterns.",
    },
    {
        "id": "lupus",
        "name": "Lupus nephritis",
        "tags": ["Immune complex", "SLE-associated", "Biopsy class guides therapy"],
        "base": 1,
        "rules": [
            (["feature", "sle"], 5, "Known or suspected SLE is a major context clue."),
            (["lab", "anaDsDna"], 4, "ANA or anti-dsDNA positivity supports lupus activity in context."),
            (["lab", "lowC3"], 2, "Complement consumption supports immune-complex disease."),
            (["lab", "lowC4"], 2, "Low C4 strengthens suspicion for lupus nephritis."),
            (["sediment", "casts"], 3, "RBC casts can indicate active proliferative lupus nephritis."),
            (["proteinuria", "nephrotic"], 2, "Heavy proteinuria can occur, including membranous lupus nephritis."),
            (["biopsy", "fullHouse"], 6, "Full-house immune deposits are a classic biopsy clue."),
        ],
        "source_note": "KDIGO 2024 lupus nephritis guidance updates the 2021 chapter and notes newer add-on immunosuppressive agents.",
    },
    {
        "id": "anca",
        "name": "ANCA-associated pauci-immune GN",
        "tags": ["Rapidly progressive", "Small-vessel vasculitis", "Urgent"],
        "base": 1,
        "rules": [
            (["egfrTrend", "rapidDecline"], 4, "Rapid eGFR decline raises concern for rapidly progressive GN."),
            (["sediment", "casts"], 4, "RBC casts support active necrotizing GN."),
            (["lab", "anca"], 5, "ANCA positivity strongly supports ANCA-associated vasculitis in the right syndrome."),
            (["feature", "sinopulmonary"], 3, "ENT or pulmonary features fit systemic small-vessel vasculitis."),
            (["feature", "hemoptysis"], 4, "Hemoptysis may indicate pulmonary capillaritis and urgent pulmonary-renal syndrome."),
            (["biopsy", "crescents"], 5, "Crescents or necrosis support rapidly progressive GN."),
        ],
        "source_note": "KDIGO 2024 ANCA guidance updates vasculitis management, including lower glucocorticoid exposure and complement inhibition options.",
    },
    {
        "id": "antiGbm",
        "name": "Anti-GBM disease",
        "tags": ["Pulmonary-renal", "Linear IgG", "Emergency"],
        "base": 0,
        "rules": [
            (["lab", "antiGbm"], 7, "Anti-GBM antibodies strongly support anti-GBM disease."),
            (["feature", "hemoptysis"], 4, "Hemoptysis with GN suggests pulmonary-renal syndrome."),
            (["egfrTrend", "rapidDecline"], 4, "Rapid loss of kidney function is typical and urgent."),
            (["sediment", "casts"], 3, "RBC casts support active crescentic GN."),
            (["biopsy", "linearIgg"], 7, "Linear IgG staining is a defining biopsy clue."),
            (["biopsy", "crescents"], 4, "Crescents support severe rapidly progressive GN."),
        ],
        "source_note": "KDIGO 2021 glomerular disease guidance includes anti-GBM disease as a separate disease chapter.",
    },
    {
        "id": "infectionRelated",
        "name": "Infection-related glomerulonephritis",
        "tags": ["Immune complex", "Low complement", "Infection search"],
        "base": 1,
        "rules": [
            (["feature", "postInfectious"], 4, "A recent or ongoing infection is a key clinical clue."),
            (["lab", "lowC3"], 4, "Low C3 supports infection-related or complement-mediated GN."),
            (["lab", "lowC4"], 1, "Complement consumption can occur in immune-complex GN."),
            (["sediment", "casts"], 3, "RBC casts indicate active glomerulonephritis."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria is often present."),
            (["egfrTrend", "reduced"], 1, "Reduced eGFR can accompany active disease."),
        ],
        "source_note": "KDIGO 2021 glomerular disease guidance includes infection-related GN and general management principles.",
    },
    {
        "id": "c3",
        "name": "C3 glomerulopathy or complement-mediated GN",
        "tags": ["Alternative complement", "Biopsy-driven", "Persistent low C3"],
        "base": 0,
        "rules": [
            (["lab", "lowC3"], 4, "Persistent low C3 raises complement-mediated disease."),
            (["lab", "lowC4"], -1, "Normal C4 with low C3 is more typical of alternative-pathway activation."),
            (["biopsy", "c3Dominant"], 7, "C3-dominant deposits are the central biopsy clue."),
            (["sediment", "casts"], 2, "Active urinary sediment supports GN."),
            (["egfrTrend", "reduced"], 2, "Reduced kidney function can occur in complement-mediated GN."),
        ],
        "source_note": "KDIGO 2021 glomerular disease guidance includes complement-mediated kidney disease resources and C3-dominant patterns.",
    },
]


def has_value(collection, value):
    return isinstance(collection, list) and value in collection


def rule_matches(rule_path: list, patient: dict) -> bool:
    kind, value = rule_path
    if kind == "feature":
        return has_value(patient.get("features", []), value)
    if kind == "lab":
        return has_value(patient.get("labs", []), value)
    if kind == "biopsy":
        return has_value(patient.get("biopsy", []), value)
    return patient.get(kind) == value


def evaluate_case(patient: dict) -> dict:
    """DEPRECATED: Use clinical_reasoning.services.engine.reason_about_patient() instead.

    This function uses hardcoded DISEASE_PROFILES (9 diseases) and is superseded
    by the KnowledgeBase-driven engine (18 diseases). Kept for backward compatibility
    during pilot transition. Will be removed post-pilot.
    """
    warnings.warn(
        "decision.services.evaluate_case() is DEPRECATED. "
        "Use clinical_reasoning.services.engine.reason_about_patient() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    scored = []
    for disease in DISEASE_PROFILES:
        reasons = []
        score = disease["base"]
        for rule_path, weight, explanation in disease["rules"]:
            if rule_matches(rule_path, patient):
                score += weight
                reasons.append({"text": explanation, "weight": weight})
        reasons.sort(key=lambda r: -r["weight"])
        scored.append({
            "id": disease["id"],
            "name": disease["name"],
            "tags": disease["tags"],
            "score": max(0, score),
            "reasons": reasons,
            "source_note": disease["source_note"],
        })

    scored.sort(key=lambda d: -d["score"])
    max_score = max(1, scored[0]["score"])
    ranked = [d for d in scored if d["score"] > 1][:5]
    for item in ranked:
        item["confidencePct"] = max(12, round((item["score"] / max_score) * 100))

    phenotype = classify_phenotype(patient)
    urgency = classify_urgency(patient, ranked)
    steps = build_next_steps(patient, ranked, urgency)

    return {"ranked": ranked, "phenotype": phenotype, "urgency": urgency, "steps": steps}


def classify_phenotype(patient: dict) -> str:
    nephrotic = patient.get("proteinuria") == "nephrotic" and patient.get("albumin") == "low"
    nephritic = patient.get("sediment") in ("casts", "hematuria")
    rapid = patient.get("egfrTrend") == "rapidDecline"

    if rapid and nephritic:
        return "Rapidly progressive nephritic syndrome"
    if nephrotic and nephritic:
        return "Mixed nephrotic-nephritic syndrome"
    if nephrotic:
        return "Nephrotic syndrome"
    if nephritic:
        return "Nephritic urinary sediment"
    if patient.get("proteinuria") == "subnephrotic":
        return "Proteinuric kidney disease"
    return "Low-evidence glomerular pattern"


def classify_urgency(patient: dict, ranked: list) -> dict:
    urgent_reasons = []
    if patient.get("egfrTrend") == "rapidDecline":
        urgent_reasons.append("rapid eGFR decline")
    if patient.get("sediment") == "casts":
        urgent_reasons.append("RBC casts")
    if has_value(patient.get("features", []), "hemoptysis"):
        urgent_reasons.append("hemoptysis")
    if has_value(patient.get("labs", []), "antiGbm"):
        urgent_reasons.append("anti-GBM positivity")
    if any(item["id"] in ("anca", "antiGbm") and item["score"] >= 8 for item in ranked):
        urgent_reasons.append("high-scoring crescentic GN pattern")

    if urgent_reasons:
        return {"level": "Urgent nephrology assessment", "tone": "urgent", "reasons": list(set(urgent_reasons))}

    if patient.get("proteinuria") == "nephrotic" or patient.get("egfrTrend") == "reduced":
        return {"level": "Prompt nephrology referral", "tone": "nephrotic", "reasons": ["heavy proteinuria or reduced kidney function"]}

    return {"level": "Structured outpatient workup", "tone": "nephritic", "reasons": ["no emergency pattern entered"]}


def build_next_steps(patient: dict, ranked: list, urgency: dict) -> list:
    tests = {
        "Quantify proteinuria with UPCR or ACR",
        "Serum creatinine/eGFR trend and blood pressure review",
        "Urine microscopy confirmation by experienced lab",
    }
    actions = {
        "Review medications, pregnancy status when relevant, infection symptoms, and thrombotic risk",
        "Consider kidney biopsy when diagnosis, activity, chronicity, or treatment choice is uncertain",
    }
    cautions = {
        "Use local protocols for immunosuppression, infection prophylaxis, vaccination, and fertility counseling",
        "Check drug contraindications and dosing for current kidney function",
    }

    if patient.get("sediment") != "bland":
        tests.add("C3, C4, ANA, anti-dsDNA, ANCA, anti-GBM, hepatitis B/C, HIV, and streptococcal testing as indicated")

    if patient.get("proteinuria") == "nephrotic":
        tests.add("Serum albumin, lipid profile, edema assessment, and thrombosis risk review")
        actions.add("Screen for secondary causes of nephrotic syndrome, including diabetes, malignancy risk context, infections, and drugs")

    if any(item["id"] == "membranous" for item in ranked):
        tests.add("PLA2R antibody testing if membranous nephropathy is plausible")

    if any(item["id"] == "lupus" for item in ranked):
        tests.add("SLE activity assessment, complements, anti-dsDNA, urinalysis trend, and biopsy class if lupus nephritis is suspected")

    if any(item["id"] in ("anca", "antiGbm") for item in ranked) or urgency.get("tone") == "urgent":
        actions.add("Escalate same day for possible rapidly progressive GN or pulmonary-renal syndrome")
        cautions.add("Do not delay emergency evaluation when hemoptysis, rapidly falling eGFR, or crescentic GN signs are present")

    if any(item["id"] == "c3" for item in ranked):
        tests.add("Repeat complement testing and consider complement pathway evaluation if low C3 persists")

    if patient.get("ageGroup") == "child" and patient.get("proteinuria") == "nephrotic":
        actions.add("Use pediatric nephrology guidance for childhood nephrotic syndrome rather than adult treatment assumptions")

    return [
        {"title": "Confirm Pattern", "items": list(tests)[:7]},
        {"title": "Clinical Actions", "items": list(actions)[:7]},
        {"title": "Safety Checks", "items": list(cautions)[:7]},
    ]

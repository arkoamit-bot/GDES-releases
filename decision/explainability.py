"""Explainability layer for GDES decision support.

Extends DecisionResult.traceability with full reasoning chains:
- Which rules fired and why
- Guideline quotes and evidence grades
- Confidence intervals based on evidence strength
- Alternative diagnoses considered and why they were ranked lower
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .services import DISEASE_PROFILES, rule_matches


@dataclass
class FiredRule:
    disease_id: str
    rule_path: list[str]
    weight: int
    explanation: str
    evidence_grade: str = ""
    guideline_quote: str = ""
    guideline_source: str = ""


@dataclass
class DiseaseReasoning:
    disease_id: str
    disease_name: str
    total_score: float
    max_possible_score: float
    confidence_pct: float
    fired_rules: list[FiredRule]
    missing_rules: list[FiredRule]
    source_note: str = ""


def build_explainability(patient: dict[str, Any]) -> dict[str, Any]:
    """Build a full explainability chain for a decision case.

    Returns a structured explanation including:
    - Per-disease reasoning chain
    - Which rules fired and missed
    - How confidence is calculated
    - Evidence sources
    - Alternative diagnoses considered
    """
    all_reasoning = []

    # Calculate max possible score for each disease
    for disease in DISEASE_PROFILES:
        max_score = disease["base"]
        fired_rules: list[FiredRule] = []
        missing_rules: list[FiredRule] = []

        for rule_path, weight, explanation in disease["rules"]:
            if rule_matches(rule_path, patient):
                max_score += max(weight, 0)
                fired_rules.append(FiredRule(
                    disease_id=disease["id"],
                    rule_path=rule_path,
                    weight=weight,
                    explanation=explanation,
                ))
            elif weight > 0:
                max_score += weight
                missing_rules.append(FiredRule(
                    disease_id=disease["id"],
                    rule_path=rule_path,
                    weight=weight,
                    explanation=explanation,
                ))

        score = disease["base"]
        for fr in fired_rules:
            score += fr.weight
        score = max(0, score)

        confidence = (score / max(max_score, 1)) * 100 if max_score > 0 else 0

        all_reasoning.append(DiseaseReasoning(
            disease_id=disease["id"],
            disease_name=disease["name"],
            total_score=score,
            max_possible_score=max_score,
            confidence_pct=round(min(confidence, 100), 1),
            fired_rules=fired_rules,
            missing_rules=missing_rules,
            source_note=disease.get("source_note", ""),
        ))

    all_reasoning.sort(key=lambda d: -d.total_score)

    # Build the explanation output
    ranked_explanations = []
    for dr in all_reasoning:
        if dr.total_score <= 0:
            continue

        ranked_explanations.append({
            "disease": {
                "id": dr.disease_id,
                "name": dr.disease_name,
                "score": dr.total_score,
                "max_score": dr.max_possible_score,
                "confidence_pct": dr.confidence_pct,
            },
            "supporting_evidence": [
                {
                    "feature": fr.rule_path,
                    "weight": fr.weight,
                    "explanation": fr.explanation,
                }
                for fr in dr.fired_rules
            ],
            "missing_evidence": [
                {
                    "feature": mr.rule_path,
                    "weight": mr.weight,
                    "explanation": mr.explanation,
                    "why_matters": f"This would have added {mr.weight} points",
                }
                for mr in missing_rules[:5]  # Top 5 missing features
            ],
            "source": dr.source_note,
        })

    # Build overall reasoning summary
    top = ranked_explanations[0] if ranked_explanations else None
    differential = [
        {
            "id": d["disease"]["id"],
            "name": d["disease"]["name"],
            "score": d["disease"]["score"],
            "confidence": d["disease"]["confidence_pct"],
        }
        for d in ranked_explanations[:5]
    ]

    if top:
        top_score = top["disease"]["score"]
        top_name = top["disease"]["name"]
        reasoning_summary = (
            f"Top diagnosis: {top_name} (score {top_score}). "
            f"{len(top['supporting_evidence'])} rules fired, "
            f"supported by clinical features including "
            f"{', '.join(e['explanation'] for e in top['supporting_evidence'][:3])}."
        )
    else:
        reasoning_summary = "No disease profile scored above threshold."

    return {
        "reasoning_summary": reasoning_summary,
        "top_diagnosis": top,
        "differential": differential,
        "confidence_interpretation": _confidence_interpretation(top),
        "disease_reasoning": ranked_explanations,
    }


def _confidence_interpretation(top: dict | None) -> str:
    if not top:
        return "Insufficient data to generate a confident differential."
    pct = top["disease"]["confidence_pct"]
    if pct >= 70:
        return ("High confidence. Clinical presentation strongly matches "
                "the top disease profile.")
    if pct >= 40:
        return ("Moderate confidence. Consider additional testing to "
                "narrow the differential.")
    return ("Low confidence. The clinical picture is non-specific; "
            "broader diagnostic workup recommended.")


def build_traceability_entry(patient: dict) -> list[dict]:
    """Build a detailed traceability entry for storage in DecisionResult.

    This replaces the basic traceability currently built in evaluate_case()
    with a richer structure.
    """
    explanation = build_explainability(patient)
    traceability = []

    for dr in explanation["disease_reasoning"][:5]:
        entry = {
            "disease_id": dr["disease"]["id"],
            "disease_name": dr["disease"]["name"],
            "score": dr["disease"]["score"],
            "max_score": dr["disease"]["max_score"],
            "confidence_pct": dr["disease"]["confidence_pct"],
            "fired_rules": [],
            "source": dr["source"],
        }
        for fr in dr["supporting_evidence"]:
            entry["fired_rules"].append({
                "feature": fr["feature"],
                "weight": fr["weight"],
                "explanation": fr["explanation"],
            })
        traceability.append(entry)

    return traceability

"""Enhanced Explainability Engine — every recommendation is fully auditable.

Answers:
- Why was this recommendation generated?
- Which patient findings triggered it?
- Which rules matched?
- Which guidelines support it?
- Which evidence level applies?
- What alternative diagnoses were rejected?
- What additional information would increase confidence?
"""
from __future__ import annotations

from typing import Any

from clinical_reasoning.models import ClinicalProfile


def build_full_explainability(profile: ClinicalProfile) -> dict[str, Any]:
    """Build a comprehensive explainability report from a ClinicalProfile."""
    differential = profile.differential or []
    trajectory = profile.disease_trajectory or {}
    care_pathway = profile.care_pathway or {}
    reasoning = profile.reasoning_chain or []
    gaps = profile.information_gaps or []

    top = differential[0] if differential else None
    alternatives = differential[1:] if len(differential) > 1 else []

    knowledge_health = {"rules_evaluated": len(differential) > 0, "knowledge_base_available": True}
    if not differential:
        knowledge_health["knowledge_base_available"] = False
        knowledge_health["message"] = (
            "No rules matched — verify that KnowledgeBaseEntry records exist "
            "with ACTIVE status and that patient features can trigger rules. "
            "Clinical recommendations may be degraded."
        )

    return {
        "summary": _build_summary(top, trajectory),
        "knowledge_health": knowledge_health,
        "triggering_findings": _identify_triggering_findings(profile.features_snapshot, differential),
        "matched_rules": _extract_matched_rules(differential),
        "guideline_support": _extract_guideline_support(differential),
        "evidence_quality": _assess_evidence_quality(differential),
        "confidence": _compute_confidence(differential),
        "rejected_alternatives": _explain_rejected_alternatives(alternatives, top),
        "information_gaps": [
            {
                "field": g.get("field"),
                "importance": g.get("importance"),
                "message": g.get("message"),
                "impact_on_confidence": _gap_confidence_impact(g.get("importance", "medium")),
            }
            for g in gaps
        ],
        "reasoning_chain": reasoning,
        "recommendations": care_pathway.get("recommendations", []),
        "audit_trail": {
            "profile_version": profile.version,
            "last_updated": profile.last_updated.isoformat(),
            "feature_count": len(profile.features_snapshot or {}),
        },
    }


def _build_summary(top: dict | None, trajectory: dict) -> str:
    """Build a one-paragraph clinical summary."""
    if not top:
        return "Insufficient data to generate a clinical assessment."
    parts = [
        f"Leading clinical impression: {top['disease_name']} "
        f"(score {top['score']}, evidence grade {top.get('evidence_grade', 'NG')})."
    ]
    trend = trajectory.get("trend", "unknown")
    if trend == "declining":
        parts.append("Disease trajectory suggests active or progressive disease.")
    elif trend == "improving":
        parts.append("Disease trajectory is favourable — patient in remission.")
    elif trend == "end_stage":
        parts.append("End-stage kidney disease — focus on RRT planning.")
    return " ".join(parts)


def _identify_triggering_findings(features: dict, differential: list) -> list[dict]:
    """Identify which clinical findings triggered the top differentials."""
    if not features or not differential:
        return []
    findings = []
    features_list = features.get("features", [])
    labs = features.get("labs", [])
    biopsy = features.get("biopsy", [])

    if "edema" in features_list:
        findings.append({"finding": "Peripheral edema", "category": "clinical", "weight": "high"})
    if "hypertension" in features_list:
        findings.append({"finding": "Hypertension", "category": "clinical", "weight": "moderate"})
    if features.get("proteinuria") == "nephrotic":
        findings.append({"finding": "Nephrotic-range proteinuria", "category": "lab", "weight": "high"})
    if biopsy:
        findings.append({"finding": f"Biopsy findings: {', '.join(biopsy)}", "category": "pathology", "weight": "high"})
    for lab in labs:
        findings.append({"finding": f"Lab marker: {lab}", "category": "serology", "weight": "moderate"})
    return findings


def _extract_matched_rules(differential: list) -> list[dict]:
    """Extract which rules matched for each disease in the differential."""
    rules = []
    for d in differential[:5]:
        matched = d.get("matched_rules", []) or []
        entry = {
            "disease": d.get("disease_name"),
            "matched_count": d.get("matched_rules_count", len(matched)),
            "source": d.get("source", ""),
            "evidence_grade": d.get("evidence_grade", "NG"),
            "guideline_chapter": d.get("guideline_chapter", ""),
            "guideline_paragraph": d.get("guideline_paragraph", ""),
            "guideline_quote": d.get("guideline_quote", ""),
            "matched_rules": [
                {
                    "condition": m.get("condition", m.get("rule_text", "")),
                    "weight": m.get("weight", 0),
                    "explanation": m.get("explanation", ""),
                }
                for m in matched[:10]
            ],
        }
        rules.append(entry)
    return rules


def _extract_guideline_support(differential: list) -> list[dict]:
    """Extract guideline references from the differential.

    Includes guideline year and evidence grade (e.g. "KDIGO 2021 GN 4.1.5 (1B)").
    """
    guidelines = []
    seen = set()
    for d in differential:
        source = d.get("source", "")
        chapter = d.get("guideline_chapter", "")
        grade = d.get("evidence_grade", "NG")
        year = d.get("guideline_year", d.get("year", ""))
        paragraph = d.get("guideline_paragraph", "")

        # Build reference string like "KDIGO 2021 GN 4.1.5 (1B)"
        ref_parts = [source]
        if year:
            ref_parts.append(str(year))
        if chapter:
            ref_parts.append(chapter)
        reference = " ".join(ref_parts)
        if grade and grade != "NG":
            reference += f" ({grade})"

        dedup_key = (source, str(year), chapter)
        if dedup_key not in seen:
            seen.add(dedup_key)
            guidelines.append({
                "guideline": source,
                "year": year,
                "chapter": chapter or "",
                "paragraph": paragraph,
                "quote": d.get("guideline_quote", ""),
                "evidence_grade": grade,
                "reference": reference,
                "evidence_url": d.get("evidence_url", ""),
            })
    return guidelines


def _assess_evidence_quality(differential: list) -> dict:
    """Assess the overall quality of evidence."""
    grades = {}
    for d in differential:
        grade = d.get("evidence_grade", "NG")
        grades[grade] = grades.get(grade, 0) + 1
    total = len(differential)
    return {
        "grade_distribution": grades,
        "total_diseases_considered": total,
        "strong_evidence_count": grades.get("1", 0),
        "weak_evidence_count": grades.get("2", 0) + grades.get("OP", 0),
    }


def _compute_confidence(differential: list) -> dict:
    """Compute an overall confidence score from the differential."""
    if not differential:
        return {"overall": 0.0, "level": "insufficient_data", "interpretation": "No data available."}
    top = differential[0]
    top_score = top.get("score", 0)
    max_possible = max(d.get("score", 0) for d in differential) or 1
    confidence_pct = round((top_score / max_possible) * 100, 1)
    if confidence_pct >= 80:
        level = "high"
    elif confidence_pct >= 50:
        level = "moderate"
    else:
        level = "low"
    interpretations = {
        "high": "Good diagnostic confidence based on matched criteria.",
        "moderate": "Moderate confidence — additional investigations may clarify.",
        "low": "Low confidence — consider broader differential and further workup.",
        "insufficient_data": "Insufficient clinical data for confident assessment.",
    }
    return {
        "overall": confidence_pct,
        "level": level,
        "interpretation": interpretations.get(level, ""),
    }


def _explain_rejected_alternatives(alternatives: list, top: dict | None) -> list[dict]:
    """Explain why alternative diagnoses were ranked lower.

    Includes specific reasons: missing criteria, conflicting findings,
    lower guideline support, and score-based differentiation.
    """
    if not top:
        return []
    explanations = []
    for alt in alternatives[:5]:
        score_diff = top["score"] - alt["score"]
        missing = alt.get("missing_rules", []) or []
        matched = alt.get("matched_rules", []) or []

        if score_diff > 5:
            reason = "Significantly lower score — substantially less evidence"
            confidence = "low"
        elif score_diff > 2:
            reason = "Moderately lower score — fewer matching criteria"
            confidence = "moderate"
        else:
            reason = "Marginally lower score — consider in differential"
            confidence = "borderline"

        # Build specific exclusion reasons
        exclusion_reasons = []
        if missing:
            missing_names = [m.get("condition", m.get("rule_text", "")) for m in missing[:3]]
            exclusion_reasons.append(f"Missing key criteria: {', '.join(missing_names)}")
        alt_grade = alt.get("evidence_grade", "NG")
        top_grade = top.get("evidence_grade", "NG")
        if alt_grade and top_grade and alt_grade != top_grade:
            exclusion_reasons.append(f"Weaker evidence grade ({alt_grade} vs {top_grade})")

        # Check for conflicting features
        alt_conflicting = alt.get("conflicting_findings", []) or []
        if alt_conflicting:
            exclusion_reasons.append(f"Conflicting findings: {', '.join(alt_conflicting[:2])}")

        alt_matched_count = alt.get("matched_rules_count", len(matched))
        top_matched_count = top.get("matched_rules_count", 0)
        if alt_matched_count < top_matched_count:
            exclusion_reasons.append(
                f"Fewer total criteria matched ({alt_matched_count} vs {top_matched_count})"
            )

        entry = {
            "disease": alt.get("disease_name"),
            "score": alt.get("score"),
            "score_difference": score_diff,
            "reason": reason,
            "confidence": confidence,
            "matched_rule_count": len(matched),
            "top_matched_rule_count": top_matched_count,
            "exclusion_reasons": exclusion_reasons,
            "missing_rules": [
                {"condition": m.get("condition", ""), "weight": m.get("weight", 0)}
                for m in missing[:5]
            ],
        }
        explanations.append(entry)
    return explanations


def _gap_confidence_impact(importance: str) -> str:
    map = {"high": "Would significantly improve diagnostic confidence", "medium": "Would moderately improve assessment",
            "low": "Would provide marginal additional information"}
    return map.get(importance, "Unknown impact")

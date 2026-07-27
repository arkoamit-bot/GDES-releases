"""Clinical Intelligence Service — one orchestration service for the full pipeline.

Patient → Knowledge Engine → Evidence Retrieval → AI Review → Validation → Explanation

This is the heart of GDES v9. Everything is orchestrated through one service
instead of scattered across disconnected modules.

Per GDES_INTELLIGENCE_FIRST_ARCHITECTURE.md:
- No new Django apps — this is a single service
- No new database models — extends ClinicalProfile.evidence_summary
- Free public APIs are the default evidence sources (PubMed, Europe PMC, OpenAlex, CrossRef)
- GPT-5 is the primary AI reviewer
- Vera is an OPTIONAL senior consultant (clinician-invoked only)

Phase 5 — Case Complexity:
- Simple CKD → Knowledge Engine only
- Moderate complexity → Evidence APIs
- Complex GN → Evidence APIs + GPT Review
- Rare disease → Evidence APIs + GPT Review + Optional Vera consultation
"""

from __future__ import annotations

import datetime
import logging
import math
from typing import Any

from patients.models import Patient
from clinical_reasoning.models import ClinicalProfile
from clinical_reasoning.json_util import json_safe

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Case complexity constants
# --------------------------------------------------------------------------- #

# Diseases where the Knowledge Engine alone is sufficient
SIMPLE_DISEASES = {
    "diabetic_nephropathy", "hypertensive_nephrosclerosis",
    "chronic_kidney_disease_unspecified", "kidney ageing",
}

# Diseases where evidence retrieval adds value but AI review is optional
MODERATE_DISEASES = {
    "iga_nephropathy", "membranous_nephropathy", "fsgs",
    "lupus_nephritis", "membranoproliferative_gn",
}

# Diseases where AI review is strongly recommended
COMPLEX_DISEASES = {
    "anti_gbm_disease", "anca_associated_vasculitis",
    "thrombotic_microangiopathy", "c3_glomerulopathy",
    "light_chain_deposition", "amyloidosis",
}

# Diseases where optional Vera consultation is available
RARE_DISEASES = {
    "fabry_disease", "alport_syndrome", "thin_basement_membrane",
    "medullary_sponge_kidney", "polycystic_kidney_disease",
}


class ClinicalIntelligenceService:
    """One service to orchestrate the entire clinical intelligence pipeline.

    Implements case-complexity-based routing (Phase 5) to minimise cost:
    - Simple cases: Knowledge Engine only (no API calls, no AI review)
    - Moderate: Knowledge Engine + Evidence APIs
    - Complex: Knowledge Engine + Evidence APIs + GPT Review
    - Rare: Knowledge Engine + Evidence APIs + GPT Review + Vera consultation available
    """

    def __init__(self):
        self._ai_reviewer = None
        self._loaded = False

    def _load_providers(self):
        if self._loaded:
            return
        from clinical_evidence.services.orchestrator import get_ai_reviewer
        self._ai_reviewer = get_ai_reviewer()
        self._loaded = True

    @property
    def ai_reviewer(self):
        """Lazy-load the AI reviewer on first access."""
        self._load_providers()
        return self._ai_reviewer

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def analyze_patient(self, patient_id: str) -> dict[str, Any]:
        """Full intelligence pipeline for a single patient.

        Routes through the pipeline based on case complexity:
        1. Run Knowledge Engine (always)
        2. Score case complexity
        3. Retrieve evidence (if moderate+)
        4. AI review (if complex+)
        5. Validate recommendation (if AI review performed)
        6. Calculate confidence score (always)
        7. Predict eGFR trajectory (V10 Sprint 7)
        8. Generate explanation (always)
        9. Generate final recommendation (always)
        10. Store results on ClinicalProfile
        11. Return full intelligence report
        """
        patient = Patient.objects.get(patient_id=patient_id)
        profile = self._run_knowledge_engine(patient)
        complexity = self._score_case_complexity(profile)
        evidence = []
        ai_review = None
        validation = None

        if complexity["level"] in ("moderate", "complex", "rare"):
            evidence = self._retrieve_evidence(profile)

        if complexity["level"] in ("complex", "rare") and self.ai_reviewer:
            ai_review = self._run_ai_review(profile, evidence)

        if ai_review:
            validation = self._validate(profile, evidence, ai_review)

        confidence = self._calculate_confidence(profile, evidence, ai_review)

        # V10 Sprint 7: eGFR trajectory prediction
        egfr_forecast = self._predict_egfr(patient, complexity)

        # V10 Sprint 8: Relapse probability forecasting
        relapse_forecast = self._predict_relapse(patient, complexity)

        # V10 Sprint 9: Treatment response prediction
        treatment_response = self._predict_treatment_response(patient, complexity)

        explanation = self._generate_explanation(profile, evidence, ai_review, confidence)
        recommendation = self._generate_final_recommendation(
            profile, evidence, ai_review, confidence, complexity,
        )
        self._update_profile(profile, evidence, ai_review, confidence,
                             egfr_forecast, relapse_forecast, treatment_response)
        return self._build_report(
            profile, evidence, ai_review, validation, confidence, explanation,
            recommendation, complexity, egfr_forecast, relapse_forecast,
            treatment_response,
        )

    def consult_vera(
        self,
        patient_id: str,
        question: str | None = None,
    ) -> dict[str, Any]:
        """Optional Vera Health consultation with auto-generated prompt.

        This is clinician-invoked only — Vera is NOT part of the default pipeline.
        GDES auto-generates an expert-level prompt including patient context.
        """
        patient = Patient.objects.get(patient_id=patient_id)
        prompt = self._build_vera_prompt(patient, question)
        return self._call_vera(prompt, patient)

    def quick_evidence_check(self, query: str, max_results: int = 5) -> list[dict]:
        """Quick evidence lookup — retrieve and return formatted results."""
        from clinical_evidence.services.retrieval import retrieve_evidence
        query_obj = retrieve_evidence(query_text=query, max_results=max_results)
        results = query_obj.results.all().order_by("-relevance_score")[:max_results]
        return [
            {
                "title": r.title,
                "authors": r.authors,
                "journal": r.journal,
                "pmid": r.pmid,
                "doi": r.doi,
                "relevance": r.relevance_score,
                "evidence_level": r.evidence_level,
                "url": r.url,
            }
            for r in results
        ]

    # ------------------------------------------------------------------ #
    # Case complexity scoring (Phase 5)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _score_case_complexity(profile: ClinicalProfile) -> dict[str, Any]:
        """Score case complexity to determine which pipeline steps are needed.

        Returns {"level": str, "score": float, "reasons": list[str]}.
        """
        differential = profile.differential or []
        features = profile.features_snapshot or {}
        reasons = []
        score = 0.0

        # 1. Disease identity
        if differential:
            top = differential[0]
            disease_id = (top.get("disease_id") or "").lower()
            if disease_id in SIMPLE_DISEASES:
                reasons.append(f"Simple disease: {disease_id}")
            elif disease_id in MODERATE_DISEASES:
                score += 1.0
                reasons.append(f"Moderate disease: {disease_id}")
            elif disease_id in COMPLEX_DISEASES:
                score += 2.0
                reasons.append(f"Complex disease: {disease_id}")
            elif disease_id in RARE_DISEASES:
                score += 3.0
                reasons.append(f"Rare disease: {disease_id}")
            else:
                score += 1.5
                reasons.append(f"Unrecognised disease: {disease_id}")

            # Evidence grade
            grade = top.get("evidence_grade", "NG")
            if grade == "NG":
                score += 0.5
                reasons.append("No guideline evidence available")
            elif grade == "OP":
                score += 0.3
                reasons.append("Expert opinion only")

        # 2. Feature complexity
        if features.get("biopsy"):
            score += 0.3
            reasons.append("Biopsy data present")
        if features.get("latest_egfr") is not None and features["latest_egfr"] < 30:
            score += 0.5
            reasons.append("Severe CKD (eGFR < 30)")
        labs = features.get("labs") or []
        autoantibodies = {"anca", "antiGbm", "pla2r", "antiDsDna"}
        if autoantibodies & set(labs):
            score += 0.5
            reasons.append("Autoantibody-positive disease")

        # 3. Differential uncertainty
        if len(differential) >= 3:
            score += 0.3
            reasons.append(f"Wide differential ({len(differential)} candidates)")

        # Classify
        if score < 1.0:
            level = "simple"
        elif score < 2.0:
            level = "moderate"
        elif score < 3.0:
            level = "complex"
        else:
            level = "rare"

        return {
            "level": level,
            "score": round(score, 2),
            "reasons": reasons,
        }

    # ------------------------------------------------------------------ #
    # Pipeline steps
    # ------------------------------------------------------------------ #

    def _run_knowledge_engine(self, patient: Patient) -> ClinicalProfile:
        from clinical_reasoning.services.engine import reason_about_patient
        return reason_about_patient(patient)

    def _retrieve_evidence(self, profile: ClinicalProfile) -> list[dict]:
        differential = profile.differential or []
        if not differential:
            return []
        evidence = []
        top = differential[0]
        disease_name = top.get("disease_name", "")
        disease_id = top.get("disease_id", "")
        features = profile.features_snapshot or {}

        # Build targeted queries using clinical context
        queries = _build_evidence_queries(disease_name, disease_id, features)

        seen = set()
        for query_text in queries[:3]:
            try:
                results = self.quick_evidence_check(query_text, max_results=5)
                for r in results:
                    pmid = r.get("pmid", "")
                    doi = r.get("doi", "")
                    dedup_key = pmid or doi or r.get("title", "")
                    if dedup_key and dedup_key not in seen:
                        seen.add(dedup_key)
                        evidence.append(r)
            except Exception as exc:
                logger.debug("Evidence retrieval skipped for %s: %s", query_text, exc)

        # Sort by relevance (descending) and cap at 10
        evidence.sort(key=lambda x: x.get("relevance") or 0, reverse=True)
        return evidence[:10]

    def _run_ai_review(self, profile: ClinicalProfile, evidence: list[dict]) -> dict | None:
        differential = profile.differential or []
        if not differential:
            return None
        top = differential[0]
        if not self.ai_reviewer:
            return None
        features_delta = self._summarize_features(profile.features_snapshot)
        evidence_titles = [e.get("title", "")[:200] for e in evidence[:5]]
        question = (
            f"{top.get('disease_name', 'Unknown')} "
            f"(confidence {top.get('confidence', 0)}%, "
            f"grade {top.get('evidence_grade', 'NG')}). "
            f"Features: {features_delta}. "
            f"Evidence support for GDES recommendation? "
            f"Conflicts? Return JSON."
        )
        context = {
            "disease_id": top.get("disease_id", ""),
            "evidence_count": len(evidence),
            "evidence_titles": evidence_titles,
            "disease_trajectory": profile.disease_trajectory,
            "care_gaps": (profile.care_pathway or {}).get("care_gaps", []),
        }
        try:
            review = self.ai_reviewer.review_clinical_question(question, context=context)
            return {
                "summary": review.summary,
                "key_findings": review.key_findings,
                "limitations": review.limitations,
                "supporting_evidence": review.supporting_evidence,
                "contradictory_evidence": review.contradictory_evidence,
                "confidence_score": review.confidence_score,
                "recommendation_alignment": review.recommendation_alignment,
                "provider": self.ai_reviewer.provider_type,
                "structured_data": review.structured_data,
            }
        except Exception as exc:
            logger.warning("AI review failed: %s", exc)
            return None

    @staticmethod
    def _summarize_features(features: dict | None) -> str:
        """Extract the 5-6 most salient patient features for AI prompts.

        Avoids dumping the entire snapshot which wastes tokens and leaks PHI.
        """
        if not features:
            return "No clinical features available"
        salient = []
        if features.get("latest_egfr"):
            salient.append(f"eGFR {features['latest_egfr']}")
        prot = features.get("proteinuria")
        if prot and prot != "none":
            salient.append(f"Proteinuria {prot}")
        for biopsy_f in (features.get("biopsy") or [])[:3]:
            salient.append(f"Biopsy: {biopsy_f}")
        for lab_f in (features.get("labs") or [])[:3]:
            salient.append(f"Lab: {lab_f}")
        phase = features.get("disease_phase")
        if phase:
            salient.append(f"Phase: {phase}")
        return "; ".join(salient[:6]) if salient else "Limited clinical features available"

    def _validate(
        self,
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
    ) -> dict | None:
        from clinical_evidence.providers.base import AIReviewResult
        from clinical_evidence.services.validation import validate_recommendation
        differential = profile.differential or []
        if not differential:
            return None
        top = differential[0]
        ai_review_result = None
        if ai_review:
            ai_review_result = AIReviewResult(
                summary=ai_review.get("summary", ""),
                key_findings=ai_review.get("key_findings", []),
                limitations=ai_review.get("limitations", []),
                supporting_evidence=ai_review.get("supporting_evidence", []),
                contradictory_evidence=ai_review.get("contradictory_evidence", []),
                confidence_score=ai_review.get("confidence_score"),
                recommendation_alignment=ai_review.get("recommendation_alignment", ""),
                structured_data=ai_review.get("structured_data", {}),
                raw_response="",
                provider_type=ai_review.get("provider", ""),
            )
        try:
            validation = validate_recommendation(
                recommendation_text=top.get("disease_name", ""),
                gdes_recommendation=None,
                package=None,
                ai_review=ai_review_result,
            )
            return {
                "id": validation.id,
                "outcome": validation.outcome,
                "confidence_score": validation.confidence_score,
                "summary": validation.summary,
                "details": validation.details,
            }
        except Exception as exc:
            logger.warning("Validation failed: %s", exc)
            return None

    def _calculate_confidence(
        self,
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
    ) -> dict[str, Any]:
        differential = profile.differential or []
        rule_confidence = 0.0
        if differential:
            rule_confidence = differential[0].get("confidence", 0) / 100.0

        evidence_strength = min(len(evidence) / 10.0, 1.0) if evidence else 0.0

        ai_agreement = 0.0
        if ai_review and ai_review.get("confidence_score") is not None:
            ai_agreement = ai_review["confidence_score"]

        evidence_recency = 0.0
        if evidence:
            recent = sum(
                1 for e in evidence
                if e.get("publication_date") or e.get("year", "") >= "2022"
            )
            evidence_recency = min(recent / max(len(evidence), 1), 1.0)

        guideline_match = 0.0
        if differential:
            grade = differential[0].get("evidence_grade", "NG")
            grade_scores = {"1": 1.0, "2": 0.7, "OP": 0.4, "NG": 0.2}
            guideline_match = grade_scores.get(grade, 0.2)

        weights = {
            "guideline_match": 0.25,
            "evidence_strength": 0.20,
            "evidence_recency": 0.10,
            "ai_agreement": 0.25,
            "rule_confidence": 0.20,
        }
        overall = (
            guideline_match * weights["guideline_match"]
            + evidence_strength * weights["evidence_strength"]
            + evidence_recency * weights["evidence_recency"]
            + ai_agreement * weights["ai_agreement"]
            + rule_confidence * weights["rule_confidence"]
        )
        overall = round(min(max(overall, 0.0), 1.0), 3)

        if overall >= 0.8:
            level = "high"
        elif overall >= 0.5:
            level = "moderate"
        elif overall >= 0.2:
            level = "low"
        else:
            level = "insufficient"

        return {
            "overall": overall,
            "level": level,
            "components": {
                "guideline_match": round(guideline_match, 2),
                "evidence_strength": round(evidence_strength, 2),
                "evidence_recency": round(evidence_recency, 2),
                "ai_agreement": round(ai_agreement, 2),
                "rule_confidence": round(rule_confidence, 2),
            },
        }

    # ------------------------------------------------------------------ #
    # V10 Sprint 7: eGFR trajectory prediction
    # ------------------------------------------------------------------ #

    def _predict_egfr(
        self,
        patient: Patient,
        complexity: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Predict eGFR trajectory for the patient.

        Uses shorter horizons for simple cases (less data), longer for complex.
        Returns a serialisable dict or None on failure.
        """
        try:
            from analytics.services.prediction import predict_egfr_trajectory
            horizons = (
                [12, 24] if complexity["level"] in ("simple",)
                else [6, 12, 24]
            )
            forecast = predict_egfr_trajectory(patient.patient_id, horizons)

            # Store on risk_assessment
            risk = getattr(patient, "clinical_profile", None)
            if risk:
                ra = risk.risk_assessment or {}
                ra["egfr_trajectory"] = {
                    "method": forecast.method_summary,
                    "slope_per_year": forecast.egfr_slope_per_year,
                    "predictions": [
                        {
                            "horizon_months": p.horizon_months,
                            "predicted_egfr": p.predicted_egfr,
                            "lower_ci": p.lower_ci,
                            "upper_ci": p.upper_ci,
                            "confidence": p.confidence,
                        }
                        for p in forecast.predictions
                    ],
                    "prediction_date": str(forecast.prediction_date),
                }
                risk.risk_assessment = json_safe(ra)
                risk.save(update_fields=["risk_assessment"])

            # Generate prognostic insight if ESKD forecast within 24 months
            for p in forecast.predictions:
                if p.predicted_egfr < 15 and p.horizon_months <= 24:
                    from clinical_reasoning.models import ClinicalInsight
                    ClinicalInsight.objects.get_or_create(
                        patient=patient,
                        category="prognostic",
                        title="eGFR trajectory forecast",
                        defaults={
                            "detail": (
                                f"eGFR predicted to reach {p.predicted_egfr:.0f} "
                                f"({p.lower_ci:.0f}-{p.upper_ci:.0f}) within "
                                f"{p.horizon_months} months. "
                                "Consider preparing for renal replacement therapy discussion."
                            ),
                            "priority": "high",
                            "source_service": "clinical_intelligence",
                        },
                    )
                    break

            result = {
                "method": forecast.method_summary,
                "slope_per_year": forecast.egfr_slope_per_year,
                "predictions": [
                    {
                        "horizon_months": p.horizon_months,
                        "predicted_egfr": p.predicted_egfr,
                        "lower_ci": p.lower_ci,
                        "upper_ci": p.upper_ci,
                        "confidence": p.confidence,
                    }
                    for p in forecast.predictions
                ],
            }
            from analytics.services.prediction import log_prediction
            log_prediction(patient.patient_id, "egfr_forecast", result)
            return result
        except Exception as exc:
            logger.debug("eGFR prediction skipped for %s: %s", patient.patient_id, exc)
            return None

    # ------------------------------------------------------------------ #
    # V10 Sprint 8: Relapse probability forecasting
    # ------------------------------------------------------------------ #

    def _predict_relapse(
        self,
        patient: Patient,
        complexity: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Predict relapse probability for the patient.

        Uses disease-specific Cox-like hazard models from prediction.py.
        Returns a serialisable dict or None on failure.
        """
        try:
            from analytics.services.prediction import predict_relapse_risk
            horizons = [6, 12]
            forecast = predict_relapse_risk(patient.patient_id, horizons)

            # Store on risk_assessment
            risk = getattr(patient, "clinical_profile", None)
            if risk:
                ra = risk.risk_assessment or {}
                ra["relapse_forecast"] = {
                    "disease": forecast.disease,
                    "model_used": forecast.model_used,
                    "overall_risk_tier": forecast.overall_risk_tier,
                    "predictions": [
                        {
                            "horizon_months": p.horizon_months,
                            "probability": p.probability,
                            "lower_ci": p.lower_ci,
                            "upper_ci": p.upper_ci,
                            "risk_factors": p.risk_factors,
                            "protective_factors": p.protective_factors,
                            "monitoring_recommendation": p.monitoring_recommendation,
                        }
                        for p in forecast.predictions
                    ],
                    "prediction_date": str(forecast.prediction_date),
                }
                risk.risk_assessment = json_safe(ra)
                risk.save(update_fields=["risk_assessment"])

            # Generate prognostic insight if high relapse risk
            for p in forecast.predictions:
                if p.probability > 0.5:
                    from clinical_reasoning.models import ClinicalInsight
                    ClinicalInsight.objects.get_or_create(
                        patient=patient,
                        category="prognostic",
                        title="High relapse risk forecast",
                        defaults={
                            "detail": (
                                f"Relapse probability predicted at "
                                f"{p.probability:.0%} within {p.horizon_months} months. "
                                f"{p.monitoring_recommendation}"
                            ),
                            "priority": "critical" if p.probability > 0.7 else "high",
                            "source_service": "clinical_intelligence",
                        },
                    )
                    break

            result = {
                "disease": forecast.disease,
                "model_used": forecast.model_used,
                "overall_risk_tier": forecast.overall_risk_tier,
                "predictions": [
                    {
                        "horizon_months": p.horizon_months,
                        "probability": p.probability,
                        "lower_ci": p.lower_ci,
                        "upper_ci": p.upper_ci,
                        "risk_factors": p.risk_factors,
                        "protective_factors": p.protective_factors,
                        "monitoring_recommendation": p.monitoring_recommendation,
                    }
                    for p in forecast.predictions
                ],
            }
            from analytics.services.prediction import log_prediction
            log_prediction(patient.patient_id, "relapse_forecast", result)
            return result
        except Exception as exc:
            logger.debug("Relapse prediction skipped for %s: %s", patient.patient_id, exc)
            return None

    # ------------------------------------------------------------------ #
    # V10 Sprint 9: Treatment response prediction
    # ------------------------------------------------------------------ #

    def _predict_treatment_response(
        self,
        patient: Patient,
        complexity: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Predict treatment response probability for the patient.

        Uses disease-specific treatment models from prediction.py.
        Returns a serialisable dict or None on failure.
        """
        try:
            from analytics.services.prediction import predict_treatment_response
            forecast = predict_treatment_response(patient.patient_id)

            if not forecast.predictions:
                return None

            # Store on risk_assessment
            risk = getattr(patient, "clinical_profile", None)
            if risk:
                ra = risk.risk_assessment or {}
                ra["treatment_response"] = {
                    "treatment": forecast.treatment,
                    "monitoring_cadence": forecast.monitoring_cadence,
                    "recommendation_summary": forecast.recommendation_summary,
                    "predictions": [
                        {
                            "time_to_response_months": p.time_to_response_months,
                            "response_type": p.response_type,
                            "probability": p.probability,
                            "lower_ci": p.lower_ci,
                            "upper_ci": p.upper_ci,
                            "stopping_criteria_met": p.stopping_criteria_met,
                            "factors": p.factors,
                        }
                        for p in forecast.predictions
                    ],
                    "prediction_date": str(forecast.prediction_date),
                }
                risk.risk_assessment = json_safe(ra)
                risk.save(update_fields=["risk_assessment"])

            # Generate insight if low response or stopping criteria
            for p in forecast.predictions:
                if p.stopping_criteria_met:
                    from clinical_reasoning.models import ClinicalInsight
                    ClinicalInsight.objects.get_or_create(
                        patient=patient,
                        category="therapeutic",
                        title="Consider treatment modification",
                        defaults={
                            "detail": (
                                f"Response probability is only {p.probability:.0%} "
                                f"after {p.time_to_response_months} months on "
                                f"{forecast.treatment}. "
                                "Consider alternative treatment approach."
                            ),
                            "priority": "high",
                            "source_service": "clinical_intelligence",
                        },
                    )
                    break

            result = {
                "treatment": forecast.treatment,
                "monitoring_cadence": forecast.monitoring_cadence,
                "recommendation_summary": forecast.recommendation_summary,
                "predictions": [
                    {
                        "time_to_response_months": p.time_to_response_months,
                        "response_type": p.response_type,
                        "probability": p.probability,
                        "lower_ci": p.lower_ci,
                        "upper_ci": p.upper_ci,
                        "stopping_criteria_met": p.stopping_criteria_met,
                        "factors": p.factors,
                    }
                    for p in forecast.predictions
                ],
            }
            from analytics.services.prediction import log_prediction
            log_prediction(patient.patient_id, "treatment_response", result)
            return result
        except Exception as exc:
            logger.debug("Treatment response prediction skipped for %s: %s",
                         patient.patient_id, exc)
            return None

    def _generate_explanation(
        self,
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
        confidence: dict[str, Any],
    ) -> dict[str, Any]:
        differential = profile.differential or []
        top = differential[0] if differential else None

        lines = []
        if top:
            lines.append(
                f"Reasoning based on {top.get('matched_rules_count', 0)} matching criteria "
                f"from {top.get('source', 'GDES knowledge base')} "
                f"(evidence grade {top.get('evidence_grade', 'NG')})."
            )
        if evidence:
            source_names = _evidence_source_names(evidence)
            lines.append(
                f"Supported by {len(evidence)} recent publications from {source_names}."
            )
        if ai_review:
            lines.append(
                f"Independent AI review ({ai_review.get('provider', 'GPT-5')}) "
                f"confidence: {ai_review.get('confidence_score', 0):.0%}. "
                f"Alignment: {ai_review.get('recommendation_alignment', 'unknown')}."
            )
        if confidence.get("level") == "high":
            lines.append("High overall confidence — recommendation is well-supported by evidence.")
        elif confidence.get("level") == "low":
            lines.append("Low overall confidence — further investigation recommended.")

        explanation = {
            "summary": " ".join(lines) if lines else "Insufficient data for explanation.",
            "evidence_quality": {
                "total_publications": len(evidence),
                "ai_review_performed": ai_review is not None,
            },
        }
        if ai_review:
            explanation["ai_review"] = {
                "key_findings": ai_review.get("key_findings", []),
                "limitations": ai_review.get("limitations", []),
                "contradictory_evidence": ai_review.get("contradictory_evidence", []),
                "provider": ai_review.get("provider", "unknown"),
            }
        return explanation

    # ------------------------------------------------------------------ #
    # Final recommendation generator
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generate_final_recommendation(
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
        confidence: dict[str, Any],
        complexity: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate a single, explainable final recommendation.

        Combines the Knowledge Engine output, evidence, AI review, and
        confidence score into one structured recommendation object.
        """
        differential = profile.differential or []
        top = differential[0] if differential else {}
        care_pathway = profile.care_pathway or {}
        care_gaps = care_pathway.get("care_gaps", [])
        recommendations = care_pathway.get("recommendations", [])

        # Base recommendation from Knowledge Engine
        base = ""
        if top:
            base = (
                f"Leading differential: {top.get('disease_name', 'Unknown')} "
                f"(confidence {top.get('confidence', 0)}%, "
                f"evidence grade {top.get('evidence_grade', 'NG')})."
            )

        # Evidence-adjusted recommendation
        evidence_note = ""
        if evidence:
            n_supporting = sum(1 for e in evidence if (e.get("relevance") or 0) >= 0.4)
            n_contradictory = sum(1 for e in evidence if (e.get("relevance") or 0) < 0.2)
            if n_contradictory > 0:
                evidence_note = (
                    f"{n_supporting} supporting publications, "
                    f"{n_contradictory} potentially contradictory."
                )
            elif n_supporting > 0:
                evidence_note = f"{n_supporting} supporting publications."
            else:
                evidence_note = f"{len(evidence)} publications retrieved."

        # AI review adjustment
        ai_adjustment = ""
        if ai_review:
            alignment = ai_review.get("recommendation_alignment", "")
            if alignment == "conflicting":
                ai_adjustment = "AI review flagged conflicting evidence — consider specialist input."
            elif alignment == "major_difference":
                ai_adjustment = "AI review suggests a major difference from guideline recommendations."
            elif alignment == "aligns":
                ai_adjustment = "AI review confirms alignment with current evidence."

        # Actionable next steps
        next_steps = []
        for gap in care_gaps[:3]:
            next_steps.append(gap.get("message", ""))
        for rec in recommendations[:3]:
            msg = rec.get("message", "")
            if msg and msg not in next_steps:
                next_steps.append(msg)

        # Confidence annotation
        confidence_level = confidence.get("level", "unknown")
        if confidence_level == "insufficient":
            next_steps.append("Insufficient confidence — additional workup required before treatment decisions.")

        return {
            "base": base,
            "evidence_note": evidence_note,
            "ai_adjustment": ai_adjustment,
            "next_steps": next_steps[:5],
            "confidence_level": confidence_level,
            "complexity": complexity.get("level", "unknown"),
            "vera_available": complexity.get("level") == "rare",
        }

    def _update_profile(
        self,
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
        confidence: dict[str, Any],
        egfr_forecast: dict[str, Any] | None = None,
        relapse_forecast: dict[str, Any] | None = None,
        treatment_response: dict[str, Any] | None = None,
    ) -> None:
        existing = profile.evidence_summary or {}
        existing["retrieved_publications"] = evidence
        existing["ai_review"] = ai_review
        existing["confidence"] = confidence
        if egfr_forecast:
            existing["egfr_forecast"] = egfr_forecast
        if relapse_forecast:
            existing["relapse_forecast"] = relapse_forecast
        if treatment_response:
            existing["treatment_response"] = treatment_response
        existing["last_evidence_check"] = datetime.datetime.now().isoformat()
        profile.evidence_summary = json_safe(existing)
        profile.save(update_fields=["evidence_summary"])

    def _build_report(
        self,
        profile: ClinicalProfile,
        evidence: list[dict],
        ai_review: dict | None,
        validation: dict | None,
        confidence: dict[str, Any],
        explanation: dict[str, Any],
        recommendation: dict[str, Any],
        complexity: dict[str, Any],
        egfr_forecast: dict[str, Any] | None = None,
        relapse_forecast: dict[str, Any] | None = None,
        treatment_response: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        differential = profile.differential or []
        top = differential[0] if differential else None

        report = {
            "patient_id": profile.patient.patient_id,
            "profile_version": profile.version,
            "complexity": complexity,
            "differential": differential,
            "disease_trajectory": profile.disease_trajectory,
            "evidence": {
                "retrieved_count": len(evidence),
                "publications": evidence,
            },
            "ai_review": {
                "performed": ai_review is not None,
                "result": ai_review,
            },
            "validation": validation,
            "confidence": confidence,
            "explainability": explanation,
            "recommendation": recommendation,
            "reasoning_chain": profile.reasoning_chain,
            "care_gaps": (profile.care_pathway or {}).get("care_gaps", []),
            "care_recommendations": (profile.care_pathway or {}).get("recommendations", []),
        }
        if egfr_forecast:
            report["egfr_forecast"] = egfr_forecast
        if relapse_forecast:
            report["relapse_forecast"] = relapse_forecast
        if treatment_response:
            report["treatment_response"] = treatment_response
        if top:
            report["summary"] = (
                f"Top differential: {top.get('disease_name', 'Unknown')} "
                f"({top.get('confidence', 0)}% confidence, "
                f"evidence grade {top.get('evidence_grade', 'NG')}). "
                f"Case complexity: {complexity.get('level', 'unknown')}. "
                f"Overall confidence: {confidence.get('level', 'unknown')} "
                f"({confidence.get('overall', 0):.0%})."
            )
        return report

    # ------------------------------------------------------------------ #
    # Optional Vera consultation
    # ------------------------------------------------------------------ #

    def _build_vera_prompt(self, patient: Patient, question: str | None = None) -> str:
        profile = getattr(patient, "clinical_profile", None)
        differential_text = "Not available"
        if profile and profile.differential:
            top = profile.differential[0] if profile.differential else {}
            differential_text = (
                f"Disease: {top.get('disease_name', 'Unknown')} "
                f"(confidence {top.get('confidence', 0)}%)"
            )

        features = []
        if profile and profile.features_snapshot:
            f = profile.features_snapshot
            if f.get("proteinuria") and f["proteinuria"] != "none":
                features.append(f"Proteinuria: {f['proteinuria']}")
            if f.get("latest_egfr"):
                features.append(f"eGFR: {f['latest_egfr']}")
            if f.get("biopsy"):
                features.append(f"Biopsy: {', '.join(f['biopsy'])}")
            if f.get("labs"):
                features.append(f"Labs: {', '.join(f['labs'][:5])}")

        meds = "Not available"
        try:
            from prescriptions.models import Prescription
            active = Prescription.objects.filter(patient=patient, is_active=True)
            if active.exists():
                meds = "; ".join(
                    str(p) for p in active.select_related("drug")[:5]
                )
        except Exception:
            pass

        # Include GDES recommendation in the prompt
        gdes_recommendation = ""
        if profile and profile.care_pathway:
            recs = (profile.care_pathway or {}).get("recommendations", [])
            if recs:
                gdes_recommendation = recs[0].get("message", "")

        prompt = (
            f"Clinical Consultation Request\n"
            f"=============================\n\n"
            f"Diagnosis: {differential_text}\n"
            f"Features:\n"
            + ("\n".join(f"  - {f}" for f in features) if features else "  Not available") +
            f"\nMeds: {meds}\n"
        )
        if gdes_recommendation:
            prompt += f"\nGDES: {gdes_recommendation}\n"
        if question:
            prompt += f"\nQuestion: {question}\n"
        else:
            prompt += (
                f"\nQuestion: Best evidence-based treatment approach? "
                f"Recommendations with evidence level.\n"
            )
        return prompt

    def _call_vera(self, prompt: str, patient: Patient) -> dict[str, Any]:
        from clinical_evidence.services.orchestrator import get_vera_reviewer
        result = {"consultation_performed": False, "prompt": prompt}

        reviewer = get_vera_reviewer()
        if reviewer is None:
            result["error"] = (
                "Vera Health is not configured. To enable: "
                "set VERAHEALTH_API_KEY or configure VeraWebSessionProvider."
            )
            return result

        try:
            review = reviewer.review_clinical_question(prompt)
            result["consultation_performed"] = True
            result["vera_response"] = {
                "summary": review.summary,
                "key_findings": review.key_findings,
                "confidence_score": review.confidence_score,
                "recommendation_alignment": review.recommendation_alignment,
                "supporting_evidence": review.supporting_evidence,
                "contradictory_evidence": review.contradictory_evidence,
            }
            result["comparison"] = self._compare_opinions(prompt, review)
        except Exception as exc:
            result["error"] = f"Vera consultation failed: {exc}"
            logger.exception("Vera consultation failed for patient %s", patient.patient_id)
        return result

    def _compare_opinions(self, prompt: str, vera_review) -> dict[str, Any]:
        gdes_profile = None
        try:
            from clinical_evidence.services.orchestrator import get_ai_reviewer
            reviewer = get_ai_reviewer()
            if reviewer:
                gdes_review = reviewer.review_clinical_question(
                    prompt + "\n\nPlease provide your independent assessment."
                )
                gdes_profile = {
                    "summary": gdes_review.summary,
                    "confidence_score": gdes_review.confidence_score,
                    "recommendation_alignment": gdes_review.recommendation_alignment,
                    "key_findings": gdes_review.key_findings,
                }
        except Exception as exc:
            logger.debug("Opinion comparison skipped: %s", exc)

        return {
            "vera": {
                "confidence_score": vera_review.confidence_score,
                "alignment": vera_review.recommendation_alignment,
            },
            "gdes_ai": gdes_profile,
            "agreement": (
                "aligned" if gdes_profile and self._opinions_align(
                    vera_review, gdes_profile
                ) else "unknown"
            ),
        }

    def _opinions_align(self, vera_review, gdes_profile: dict | None) -> bool:
        if not gdes_profile:
            return False
        vera_score = vera_review.confidence_score or 0
        gdes_score = gdes_profile.get("confidence_score") or 0
        return abs(vera_score - gdes_score) < 0.3


# --------------------------------------------------------------------------- #
# Module-level helpers
# --------------------------------------------------------------------------- #

def _build_evidence_queries(
    disease_name: str,
    disease_id: str,
    features: dict,
) -> list[str]:
    """Build targeted evidence search queries using clinical context.

    Uses disease-specific MeSH-like terms and clinical context to produce
    higher-quality search results than generic disease-name queries.
    """
    queries = []

    # Primary: disease-specific treatment guideline
    if disease_name:
        queries.append(f"{disease_name} treatment guideline kidney")

    # Context-aware: use biopsy and lab findings
    biopsy = features.get("biopsy") or []
    labs = features.get("labs") or []
    if biopsy:
        biopsy_term = biopsy[0] if biopsy else ""
        if biopsy_term:
            queries.append(f"{disease_name} {biopsy_term} nephropathy treatment")
    elif labs:
        # Use autoantibody context
        autoab = [l for l in labs if l in ("anca", "antiGbm", "pla2r", "antiDsDna")]
        if autoab:
            queries.append(f"{disease_name} {autoab[0]} glomerulonephritis management")

    # Fallback: general nephropathy management
    if disease_name and len(queries) < 2:
        queries.append(f"{disease_name} nephropathy management review")

    # Disease ID based query (if different from name)
    if disease_id and disease_id != disease_name:
        queries.append(f"{disease_id} glomerulonephritis treatment evidence")

    return queries[:3]


def _evidence_source_names(evidence: list[dict]) -> str:
    """Determine the source names from evidence items for display."""
    sources = set()
    for e in evidence:
        src = e.get("source_type", "")
        if "pubmed" in src:
            sources.add("PubMed")
        elif "europe" in src or "epmc" in src:
            sources.add("Europe PMC")
        elif "openalex" in src:
            sources.add("OpenAlex")
        elif "crossref" in src:
            sources.add("Crossref")
        elif "semantic" in src:
            sources.add("Semantic Scholar")
        elif "vera" in src:
            sources.add("Vera Health")
        elif "openai" in src:
            sources.add("OpenAI")
        elif "perplexity" in src:
            sources.add("Perplexity")
    return ", ".join(sorted(sources)) if sources else "published databases"

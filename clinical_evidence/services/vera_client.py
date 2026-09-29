"""Vera Health API Client — production integration.

Sends patient data to the Vera Health Clinical AI Platform via the
provider layer (VeraProvider or VeraWebSessionProvider).  All clinical
reasoning originates from Vera; no local simulation is used.

If no Vera provider is configured or the API is unreachable, a
``VeraClientError`` is raised — the caller must handle this and
display an appropriate error to the user.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Data classes
# ------------------------------------------------------------------ #

@dataclass
class VeraRecommendation:
    """Structured output from Vera Health clinical analysis.

    Fields may be partially populated depending on what the Vera API
    returns.  The ``clinical_summary`` field always contains Vera's
    narrative reasoning; structured fields (``medications``, etc.) are
    populated when the API provides structured output.
    """

    diagnosis: str = ""
    diagnosis_confidence: float = 0.0
    disease_severity: str = ""
    risk_category: str = ""
    ckd_stage: int = 0
    prognosis: str = ""

    treatment_rationale: str = ""
    medications: list[dict[str, Any]] = field(default_factory=list)
    monitoring: list[dict[str, Any]] = field(default_factory=list)
    follow_up: dict[str, Any] = field(default_factory=dict)
    safety_checks: list[dict[str, Any]] = field(default_factory=list)

    guideline_references: list[dict[str, Any]] = field(default_factory=list)
    confidence: dict[str, float] = field(default_factory=dict)

    supporting_evidence: list[str] = field(default_factory=list)
    contradictory_evidence: list[str] = field(default_factory=list)
    key_findings: list[str] = field(default_factory=list)
    clinical_notes: list[str] = field(default_factory=list)

    clinical_summary: str = ""

    raw_response: dict[str, Any] = field(default_factory=dict)
    is_production: bool = False
    verification_engine: str = ""
    knowledge_version: str = "2026.07"
    guideline_version: str = "KDIGO 2024"
    api_latency_ms: float = 0.0

    @property
    def overall_confidence(self) -> float:
        return self.confidence.get("overall", 0.0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "diagnosis": self.diagnosis,
            "diagnosis_confidence": self.diagnosis_confidence,
            "disease_severity": self.disease_severity,
            "risk_category": self.risk_category,
            "ckd_stage": self.ckd_stage,
            "prognosis": self.prognosis,
            "treatment_rationale": self.treatment_rationale,
            "medications": self.medications,
            "monitoring": self.monitoring,
            "follow_up": self.follow_up,
            "safety_checks": self.safety_checks,
            "guideline_references": self.guideline_references,
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "key_findings": self.key_findings,
            "clinical_notes": self.clinical_notes,
            "clinical_summary": self.clinical_summary,
            "is_production": self.is_production,
            "verification_engine": self.verification_engine,
            "knowledge_version": self.knowledge_version,
            "guideline_version": self.guideline_version,
        }


class VeraClientError(Exception):
    """Raised when the Vera Health API cannot be reached or returns an error."""


# ------------------------------------------------------------------ #
# Clinical prompt
# ------------------------------------------------------------------ #

_CLINICAL_PROMPT_TEMPLATE = (
    "You are an independent clinical AI顾问 reviewing a patient with "
    "{diagnosis}. Provide a comprehensive clinical analysis covering:\n\n"
    "1. DIAGNOSIS: Confirm or refine the diagnosis with confidence.\n"
    "2. DISEASE SEVERITY: Classify severity and CKD stage.\n"
    "3. RISK PREDICTION: Estimate disease progression risk.\n"
    "4. TREATMENT RECOMMENDATION: Provide specific, patient-tailored "
    "medication recommendations with doses, frequencies, routes, "
    "duration, renal adjustments, monitoring requirements, and "
    "contraindications.\n"
    "5. MONITORING PLAN: Specify monitoring parameters, intervals, "
    "targets, and action thresholds.\n"
    "6. SAFETY REVIEW: Screen for drug interactions, contraindications, "
    "renal safety, and hyperkalaemia risk.\n"
    "7. FOLLOW-UP: Recommend follow-up schedule and escalation criteria.\n"
    "8. GUIDELINE ALIGNMENT: Cite specific guidelines (KDIGO, ERA-EDTA, "
    "ACR, etc.) supporting each recommendation.\n"
    "9. EVIDENCE: Cite key publications supporting your reasoning.\n\n"
    "Patient data:\n{patient_summary}\n\n"
    "Provide your analysis as structured JSON with keys: "
    "diagnosis, diagnosis_confidence, disease_severity, risk_category, "
    "ckd_stage, prognosis, treatment_rationale, medications (list of "
    "objects with drug, recommended_dose, frequency, route, duration, "
    "monitoring, contraindications, evidence_level, guideline_reference), "
    "monitoring (list with parameter, interval, target, action_threshold), "
    "follow_up (object with next_visit, targets, escalation_criteria, "
    "required_investigations), safety_checks (list with check, status, "
    "detail), guideline_references (list with source, version, title, "
    "recommendation, evidence_level), confidence (object with overall, "
    "diagnosis, treatment), key_findings (list of strings), "
    "supporting_evidence (list of strings), clinical_notes (list of "
    "strings)."
)


def _build_patient_summary(patient_data: dict[str, Any]) -> str:
    """Serialize patient_data dict into a concise clinical summary."""
    parts = []
    demo = patient_data.get("demographics", {})
    if demo:
        age = demo.get("age", "unknown")
        sex = demo.get("sex", "unknown")
        parts.append(f"Age: {age}, Sex: {sex}")
        if demo.get("weight_kg"):
            parts.append(f"Weight: {demo['weight_kg']} kg")
        if demo.get("body_surface_area"):
            parts.append(f"BSA: {demo['body_surface_area']} m²")

    kidney = patient_data.get("kidney_disease", {})
    if kidney:
        diag = kidney.get("primary_diagnosis", "unknown")
        parts.append(f"Primary diagnosis: {diag}")
        if kidney.get("egfr") is not None:
            parts.append(f"eGFR: {kidney['egfr']} mL/min/1.73m²")
        if kidney.get("ckd_stage"):
            parts.append(f"CKD Stage: {kidney['ckd_stage']}")
        risk = kidney.get("risk_assessment", {})
        if isinstance(risk, dict) and risk.get("risk_category"):
            parts.append(f"Risk: {risk['risk_category']}")

    labs = patient_data.get("laboratory_data", {})
    if labs:
        for key, val in labs.items():
            if isinstance(val, dict):
                value = val.get("value", val.get("result", ""))
                if value is not None:
                    parts.append(f"{key}: {value}")

    vitals = patient_data.get("vital_signs", {})
    if vitals:
        for key, val in vitals.items():
            if isinstance(val, dict):
                value = val.get("value", "")
                if value is not None:
                    parts.append(f"{key}: {value}")

    meds = patient_data.get("current_medications", [])
    if meds:
        med_names = []
        for m in meds:
            if isinstance(m, dict):
                name = m.get("drug", m.get("name", ""))
                dose = m.get("dose", "")
                med_names.append(f"{name} {dose}".strip())
            elif isinstance(m, str):
                med_names.append(m)
        if med_names:
            parts.append(f"Current medications: {', '.join(med_names)}")

    comorbidities = patient_data.get("comorbidities", {})
    if comorbidities:
        active = [k for k, v in comorbidities.items() if v]
        if active:
            parts.append(f"Comorbidities: {', '.join(active)}")

    pathology = patient_data.get("pathology", {})
    if pathology:
        biopsy = pathology.get("biopsy_summary", "")
        if biopsy:
            parts.append(f"Pathology: {biopsy}")

    return "\n".join(parts)


# ------------------------------------------------------------------ #
# Client
# ------------------------------------------------------------------ #

class VeraClient:
    """Client for the Vera Health Clinical AI Platform.

    Uses the orchestrator provider layer to obtain a configured and
    authenticated ``VeraProvider`` or ``VeraWebSessionProvider`` and
    sends the patient data for independent clinical analysis.

    Raises ``VeraClientError`` if no provider is available or the API
    call fails — never falls back to local simulation.
    """

    def __init__(self):
        self._provider = None
        self._provider_type = ""
        self._connect()

    def _connect(self):
        """Attempt to obtain a Vera provider from the orchestrator."""
        try:
            from clinical_evidence.services.orchestrator import get_vera_reviewer
            self._provider = get_vera_reviewer()
            if self._provider is not None:
                self._provider_type = type(self._provider).__name__
                logger.info(
                    "Vera provider connected: %s", self._provider_type
                )
        except Exception as exc:
            logger.warning("Failed to obtain Vera provider: %s", exc)
            self._provider = None

    @property
    def is_production(self) -> bool:
        """True when a real Vera provider is connected."""
        return self._provider is not None

    @property
    def provider_type(self) -> str:
        return self._provider_type

    def health_check(self) -> dict:
        """Check Vera API availability.

        Returns a dict with ``available``, ``latency_ms``, and ``error``.
        """
        if self._provider is None:
            return {
                "available": False,
                "latency_ms": 0,
                "error": "No Vera provider configured. Set VERAHEALTH_API_KEY "
                         "or configure Vera Web credentials.",
            }
        try:
            return self._provider.health_check()
        except Exception as exc:
            return {
                "available": False,
                "latency_ms": 0,
                "error": str(exc),
            }

    def analyze(self, patient_data: dict[str, Any]) -> VeraRecommendation:
        """Send patient data to Vera and return a clinical recommendation.

        Args:
            patient_data: Serialized patient data from ``vera_mapper``.

        Returns:
            ``VeraRecommendation`` with Vera's independent analysis.

        Raises:
            VeraClientError: If no provider is available or the API call
                fails.  The caller must handle this and display an error.
        """
        if self._provider is None:
            raise VeraClientError(
                "Unable to contact Vera Health. "
                "The Vera Health API is not configured. "
                "Set VERAHEALTH_API_KEY or configure Vera Web credentials "
                "in ProviderConfiguration."
            )

        prompt = self._build_clinical_prompt(patient_data)
        patient_summary = _build_patient_summary(patient_data)
        context = {
            "patient_data": patient_data,
            "request_type": "full_clinical_analysis",
        }

        t0 = time.time()
        try:
            review = self._provider.review_clinical_question(
                question=prompt,
                context=context,
            )
            latency = (time.time() - t0) * 1000
            logger.info(
                "Vera clinical analysis completed in %.0fms (provider=%s)",
                latency, self._provider_type,
            )
            return self._parse_review(review, latency)
        except Exception as exc:
            latency = (time.time() - t0) * 1000
            logger.error(
                "Vera clinical analysis failed after %.0fms: %s",
                latency, exc,
            )
            raise VeraClientError(
                f"Vera Health API request failed: {exc}"
            ) from exc

    def _build_clinical_prompt(self, patient_data: dict[str, Any]) -> str:
        """Build a comprehensive clinical analysis prompt."""
        kidney = patient_data.get("kidney_disease", {})
        diagnosis = kidney.get("primary_diagnosis", "Glomerulonephritis")
        patient_summary = _build_patient_summary(patient_data)
        return _CLINICAL_PROMPT_TEMPLATE.format(
            diagnosis=diagnosis,
            patient_summary=patient_summary,
        )

    def _parse_review(self, review, latency_ms: float) -> VeraRecommendation:
        """Parse an AIReviewResult into a VeraRecommendation."""
        rec = VeraRecommendation(
            is_production=True,
            verification_engine=f"Vera Health AI ({self._provider_type})",
            api_latency_ms=latency_ms,
            clinical_summary=review.summary or "",
            key_findings=review.key_findings or [],
            supporting_evidence=review.supporting_evidence or [],
            contradictory_evidence=review.contradictory_evidence or [],
        )

        if review.confidence_score is not None:
            rec.confidence = {"overall": float(review.confidence_score)}

        structured = review.structured_data or {}
        if isinstance(structured, str):
            try:
                structured = json.loads(structured)
            except (json.JSONDecodeError, TypeError):
                structured = {}

        if isinstance(structured, dict):
            rec.diagnosis = structured.get("diagnosis", "")
            if isinstance(rec.diagnosis, dict):
                rec.diagnosis = rec.diagnosis.get("name", str(rec.diagnosis))
            rec.diagnosis_confidence = _safe_float(
                structured.get("diagnosis_confidence", 0)
            )
            rec.disease_severity = structured.get("disease_severity", "")
            rec.risk_category = structured.get("risk_category", "")
            rec.ckd_stage = _safe_int(structured.get("ckd_stage", 0))
            rec.prognosis = structured.get("prognosis", "")
            rec.treatment_rationale = structured.get("treatment_rationale", "")
            rec.medications = structured.get("medications", [])
            rec.monitoring = structured.get("monitoring", [])
            rec.follow_up = structured.get("follow_up", {})
            rec.safety_checks = structured.get("safety_checks", [])
            rec.guideline_references = structured.get(
                "guideline_references", []
            )
            rec.clinical_notes = structured.get("clinical_notes", [])

            s_conf = structured.get("confidence", {})
            if isinstance(s_conf, dict):
                for k, v in s_conf.items():
                    rec.confidence[k] = _safe_float(v)

            if structured.get("key_findings"):
                rec.key_findings = structured["key_findings"]
            if structured.get("supporting_evidence"):
                rec.supporting_evidence = structured["supporting_evidence"]
            if structured.get("clinical_notes"):
                rec.clinical_notes = structured["clinical_notes"]

        try:
            rec.raw_response = json.loads(review.raw_response) if review.raw_response else {}
        except (json.JSONDecodeError, TypeError):
            rec.raw_response = {"raw": review.raw_response}

        if not rec.confidence:
            rec.confidence = {"overall": 0.0}

        return rec


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _safe_float(val: Any) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(val: Any) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

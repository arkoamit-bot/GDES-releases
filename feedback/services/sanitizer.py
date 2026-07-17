"""PHI Sanitization Engine — strips all patient-identifiable information
before any error data leaves the local machine."""
from __future__ import annotations

import re
from typing import Any

# Patterns that indicate PHI — must never be transmitted
_PATIENT_FIELD_NAMES = frozenset({
    "patient_name", "name", "full_name", "first_name", "last_name",
    "hospital_id", "mrn", "medical_record_number", "registry_id",
    "phone", "mobile", "telephone", "contact_number",
    "address", "street", "city", "postcode", "zip", "district",
    "national_id", "nid", "ssn", "social_security",
    "email", "e_mail",
    "date_of_birth", "dob", "age_at_registration",
    "patient_id", "patient", "encounter_id", "encounter",
    "biopsy_id", "lab_id", "prescription_id",
})

# Regex patterns for free-text PHI detection
_NATIONAL_ID_RE = re.compile(r"\b\d{10,17}\b")
_PHONE_RE = re.compile(r"\b(?:\+?88)?01[3-9]\d{8}\b")
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_MR_RE = re.compile(r"\b(?:MRN|MR|#)\s*[:=]?\s*\d{4,10}\b", re.IGNORECASE)

# Clinical text fields that must be completely removed (never truncated)
_CLINICAL_TEXT_FIELDS = frozenset({
    "clinical_notes", "notes", "free_text", "comment", "comments",
    "history", "present_illness", "examination_findings",
    "biopsy_report", "pathology_report", "lab_report",
    "prescription_text", "prescription_notes",
    "doctor_name", "referring_doctor", "treating_doctor",
    "diagnosis_text", "differential_diagnosis",
    "imaging_report", "radiology_report",
    "operative_notes", "discharge_summary",
})


def _is_phi_key(key: str) -> bool:
    """Check if a dict key looks like it contains PHI."""
    kl = key.lower().strip()
    if kl in _PATIENT_FIELD_NAMES:
        return True
    if any(phi in kl for phi in ("patient", "mrn", "nid", "ssn", "phone",
                                   "address", "email", "hospital_id")):
        return True
    return False


def _is_clinical_key(key: str) -> bool:
    """Check if a dict key contains clinical free text."""
    kl = key.lower().strip()
    return kl in _CLINICAL_TEXT_FIELDS


def _scrub_string(value: str) -> str:
    """Remove PHI patterns from a string value."""
    value = _NATIONAL_ID_RE.sub("[REDACTED_ID]", value)
    value = _PHONE_RE.sub("[REDACTED_PHONE]", value)
    value = _EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = _MR_RE.sub("[REDACTED_MRN]", value)
    return value


def sanitize(obj: Any) -> Any:
    """Recursively strip all PHI from a data structure.

    - Dict keys matching PHI patterns → entire value removed
    - Clinical free-text fields → entire value removed
    - String values → regex PHI patterns scrubbed
    - Lists/tuples → each element sanitized
    - Everything else → returned as-is
    """
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if _is_phi_key(k):
                continue
            if _is_clinical_key(k):
                continue
            cleaned[k] = sanitize(v)
        return cleaned
    if isinstance(obj, (list, tuple)):
        return type(obj)(sanitize(item) for item in obj)
    if isinstance(obj, str):
        return _scrub_string(obj)
    return obj


def sanitize_error_context(context: dict | None) -> dict | None:
    """Sanitize request context before upload. Strips all PHI and clinical text."""
    if not context:
        return None
    return sanitize(context)


def sanitize_stack_trace(stack: str) -> str:
    """Scrub any PHI patterns that leaked into stack traces or log messages."""
    if not stack:
        return stack
    return _scrub_string(stack)

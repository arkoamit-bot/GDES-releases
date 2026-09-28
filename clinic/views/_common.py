"""Shared imports, constants, and helper functions for clinic views.

Every view module imports from here instead of re-declaring the same
constants and utilities.
"""
from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

logger = logging.getLogger(__name__)

from patients.models import Patient
from encounters.models import ClinicalEncounter
from prescriptions.models import AdviceTemplate, Prescription, PrescriptionItem
from prescriptions.services.tapers import TAPER_PRESETS, is_systemic_steroid
from treatments.models import DrugMaster

from ..forms import (AdmissionForm, AdverseEventForm, BaselineForm, BiopsyForm,
                    FollowupForm, FSGSPathologyForm, GNDiagnosisForm,
                    IgANScoreForm, ConsentForm, LabResultsForm,
                    LupusPathologyForm, MembranousPathologyForm, PatientForm,
                    RegisterForm, RelapseForm, StudyEnrollmentForm,
                    TreatmentExposureForm, LabOrderForm, collect_labs)

LOGIN = "/login/"

# Number of medication rows on the prescription form (form render + POST handler
# must agree — see prescription_create).
MAX_PRESCRIPTION_ITEMS = 12

# PatientForm field partition for the stepped registration wizard
# (clinic/patient_form.html). Any field not listed falls through to neither step,
# so keep these in sync with PatientForm.Meta.fields.
_PATIENT_DEM_FIELDS = ["name", "hospital_id", "phone", "sex", "dob"]
_PATIENT_CLIN_FIELDS = ["enrollment_date", "cohort", "diabetes_status",
                         "primary_diagnosis"]
_PATIENT_LEVEL2_FIELDS = [
    "hypertension", "cvd_history", "autoimmune_disease", "chronic_infection",
    "malignancy", "previous_kidney_disease", "prior_immunosuppression",
    "family_history_kidney", "diabetic_retinopathy", "neuropathy",
    "diabetic_foot_history", "smoking_status", "hepatitis_status", "hiv_status",
    # Histology — PatientForm drops these until a biopsy exists, so a field
    # listed here simply will not be rendered before then.
    "biopsy_diagnosis", "gn_broad_group",
    "gn_primary_secondary", "oxford_mestc", "isn_rps_class",
    "ckd_etiology", "transplant_status"]


def _clip(value, field):
    """Trim a POSTed value to the model field's max_length.

    SQLite silently accepts an over-long CharField; PostgreSQL raises
    DataError, so the same form submission would 500 only after the SQLite ->
    PostgreSQL migration. Clipping from the model's own limit keeps the two
    backends behaving identically and means a hand-crafted POST cannot take the
    prescription endpoint down.
    """
    text = (value or "").strip()
    limit = getattr(field, "max_length", None)
    if limit and len(text) > limit:
        text = text[:limit].rstrip()
    return text


def _save_labs(patient, form, result_date, *, rows=None, entry_path="baseline",
               user=None):
    """Record the point-of-care labs entered on a form through the one lab
    service. Entering creatinine auto-derives eGFR + refreshes the patient's
    cached value. Returns a PanelOutcome: what was saved, what was already on
    file for that date (not duplicated unless the user confirmed a repeat),
    and which fields failed and why -- a failure never loses the rest."""
    from labs.services.results import record_panel
    rows = collect_labs(form.cleaned_data) if rows is None else rows
    return record_panel(
        patient, rows, result_date=result_date,
        token=(form.cleaned_data.get("form_token") or ""),
        entry_path=entry_path,
        entered_by=user if getattr(user, "is_authenticated", False) else None,
        allow_repeat=bool(form.cleaned_data.get("confirm_repeat")))


def _panel_messages(request, outcome, what="result"):
    """Truthful, per-field feedback for a panel save."""
    if outcome.saved:
        messages.success(request, f"{len(outcome.saved)} {what}(s) recorded.")
    if outcome.existing:
        messages.warning(request, "Already on file for that date, not recorded again: "
                         + "; ".join(f"{r.test.name} {r.value_numeric if r.value_numeric is not None else r.value_text}"
                                     f" ({r.result_date}, {r.get_entry_path_display() or r.get_source_display()})"
                                     for r in outcome.existing)
                         + ". Tick 'new repeat measurements' to record a genuine repeat.")
    for code, msg in outcome.failed.items():
        messages.error(request, f"{code}: not saved — {msg}")


def _get_recommendation_audit_records(patient):
    """Get RecommendationAudit records for a patient, most recent first."""
    try:
        from knowledge.models import RecommendationAudit
        return RecommendationAudit.objects.filter(patient=patient).order_by("-issued_at")[:50]
    except Exception:
        return []


def _get_patient_override_context(patient):
    """Get override feedback context for a patient (Sprint 6)."""
    try:
        from feedback.analytics import patient_override_context
        return patient_override_context(patient)
    except Exception:
        return {"local_total": 0, "local_overrides": 0, "local_override_rate": None}


def _get_prediction_history(patient):
    """Get prediction audit trail for the patient (V10 Sprint 11)."""
    try:
        from analytics.services.prediction import prediction_history
        return prediction_history(patient.patient_id)
    except Exception:
        return []


def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default

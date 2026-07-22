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
    "hypertension", "autoimmune_disease", "chronic_infection", "smoking_status",
    "hepatitis_status", "hiv_status", "biopsy_diagnosis", "gn_broad_group",
    "gn_primary_secondary", "oxford_mestc", "isn_rps_class", "ckd_etiology", "transplant_status"]


def _save_labs(patient, form, result_date):
    """Record any point-of-care labs entered on the form as LabResult rows.
    Entering creatinine auto-derives eGFR + refreshes the patient's cached value.
    A lab failure must never lose the visit/baseline, so each is best-effort."""
    from labs.services.results import record_result
    saved = 0
    for code, value, text in collect_labs(form.cleaned_data):
        try:
            record_result(patient, code, result_date=result_date,
                          value_numeric=value, value_text=text)
            saved += 1
        except Exception:  # pragma: no cover - defensive
            pass
    return saved


def _get_recommendation_audit_records(patient):
    """Get RecommendationAudit records for a patient, most recent first."""
    try:
        from knowledge.models import RecommendationAudit
        return RecommendationAudit.objects.filter(patient=patient).order_by("-issued_at")[:50]
    except Exception:
        return []


def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default

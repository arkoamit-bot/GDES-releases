"""Clinic views — re-exported from sub-modules for backward compatibility.

The URL configuration does ``from . import views`` and accesses
``views.patient_detail``, ``views.followup_create``, etc.  This
package's ``__init__.py`` re-exports every view function so the
existing URL wiring keeps working unchanged.

PACKAGE STRUCTURE:
  views/
    __init__.py            — This file (backward-compatible re-exports)
    _common.py             — Shared imports, constants, helper functions
    patient_views.py       — Patient CRUD, list, search, detail
    encounter_views.py     — Baseline, follow-up, registration, relapse, admission
    clinical_views.py      — Biopsy, adverse events, study enrollment, consent, treatment
    prescription_views.py  — Prescription create and list
    analytics_views.py     — Quality, analytics, export, outcomes, Cox, eGFR slope, CIF
    lab_views.py           — Lab ordering and results entry
    knowledge_views.py     — Drug intelligence, studies, feedback, safety, pathology, biomarkers
    worklist_views.py      — Scheduling worklist
    clinical_intelligence_views.py — Reasoning run, Vera Health verification/prescription
    help_views.py          — Help / documentation pages
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    LOGIN,
    MAX_PRESCRIPTION_ITEMS,
    _clip,
    _save_labs,
    _panel_messages,
    _get_recommendation_audit_records,
    _get_patient_override_context,
    _get_prediction_history,
    _safe_call,
)
from .patient_views import (  # noqa: F401
    patients_list,
    quicksearch,
    patient_dupcheck,
    patient_create,
    patient_delete,
    patient_edit,
    patient_detail,
)
from .encounter_views import (  # noqa: F401
    baseline_edit,
    _sync_level2_from_followup,
    followup_create,
    patient_register,
    relapse_create,
    admission_create,
)
from .clinical_views import (  # noqa: F401
    adverse_event_create,
    _SCORE_HINTS,
    _reconcile_lupus_class,
    _reconcile_fsgs,
    _attach_report_errors,
    _biopsy_summary_flags,
    biopsy_create,
    _finding_sections,
    biopsy_detail,
    biopsy_amend,
    adopt_pathology_diagnosis,
    study_enroll,
    consent_manage,
    treatment_add,
)
from .prescription_views import (  # noqa: F401
    DOSE_UNITS,
    _requested_tests,
    prescription_create,
    prescriptions_list,
)
from .clinical_intelligence_views import (  # noqa: F401
    run_clinical_intelligence,
    verify_treatment_with_vera,
    _build_treatment_verification_prompt,
    _build_prescription_prompt,
    request_vera_prescription,
    vera_autopaste,
    save_vera_response,
)
from .analytics_views import (  # noqa: F401
    outcome_recompute,
    quality_page,
    _drug_group_options,
    analytics_page,
    export_page,
    cox_results,
    egfr_slope_results,
    cif_results,
)
from .worklist_views import (  # noqa: F401
    worklist_page,
)
from .knowledge_views import (  # noqa: F401
    studies_page,
    drug_intelligence_page,
    drug_intelligence_detail,
    recommendation_feedback,
    safety_page,
    pathology_page,
    biomarkers_page,
)
from .lab_views import (  # noqa: F401
    lab_order_create,
    lab_results_entry,
)
from .help_views import (  # noqa: F401
    help_index,
    help_user,
    help_admin,
    help_developer,
)

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
    help_views.py          — Help / documentation pages
"""
from __future__ import annotations

# --- Patient views ----------------------------------------------------------
from .patient_views import (  # noqa: F401
    patients_list,
    quicksearch,
    patient_dupcheck,
    patient_create,
    patient_delete,
    patient_edit,
    patient_detail,
)

# --- Encounter views --------------------------------------------------------
from .encounter_views import (  # noqa: F401
    baseline_edit,
    followup_create,
    patient_register,
    relapse_create,
    admission_create,
)

# --- Clinical workflow views ------------------------------------------------
from .clinical_views import (  # noqa: F401
    adverse_event_create,
    biopsy_create,
    study_enroll,
    consent_manage,
    treatment_add,
)

# --- Prescription views -----------------------------------------------------
from .prescription_views import (  # noqa: F401
    prescription_create,
    prescriptions_list,
)

# --- Analytics / export views -----------------------------------------------
from .analytics_views import (  # noqa: F401
    quality_page,
    analytics_page,
    export_page,
    outcome_recompute,
    cox_results,
    egfr_slope_results,
    cif_results,
)

# --- Lab views --------------------------------------------------------------
from .lab_views import (  # noqa: F401
    lab_order_create,
    lab_results_entry,
)

# --- Knowledge views --------------------------------------------------------
from .knowledge_views import (  # noqa: F401
    studies_page,
    drug_intelligence_page,
    drug_intelligence_detail,
    recommendation_feedback,
    safety_page,
    pathology_page,
    biomarkers_page,
)

# --- Worklist views ---------------------------------------------------------
from .worklist_views import (  # noqa: F401
    worklist_page,
)

# --- Help views -------------------------------------------------------------
from .help_views import (  # noqa: F401
    help_index,
    help_user,
    help_admin,
    help_developer,
)

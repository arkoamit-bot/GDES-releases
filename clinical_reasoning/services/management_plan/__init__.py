"""Personalized Management Plan Generator — Phase 6 of GDES transformation.

Generates comprehensive, evidence-based management plans per disease profile
including: first-line therapy, second-line therapy, rescue therapy,
contraindicated medications, monitoring parameters, and follow-up schedule.

Every recommendation is audited via RecommendationAudit (knowledge/models.py)
and tracked for clinician feedback (accept/reject/override) per Layer 10 of
the V8 AI Knowledge Engine Roadmap.

STATUS — V8.0 Clinical Intelligence Platform:
  ✔ KDIGO 2021/2024-aligned treatment protocols for 9+ glomerular diseases
  ✔ Evidence-graded recommendations (1=strong, 2=weak, OP=expert opinion)
  ✔ Risk-stratified monitoring intensification (low/moderate/high/very_high)
  ✔ CKD stage-specific modifications (anemia, MBD screening)
  ✔ Safety checks: pregnancy, infection, drug contraindications
  ✔ Patient education templates per disease
  ✔ Fully audited: every generated plan creates a RecommendationAudit record
  ✔ Governance metadata requires: guideline chapter, evidence grade, author,
    reviewer, approval timestamp, next review date (enforced by validate_governance)
  ✔ KB governance metadata populated: guideline_chapter, evidence_url,
    author, approved_by, approved_at on all 209 active entries
  ✔ V8 Field Error Reporting & Feedback System live (feedback/ app)

BACKWARD COMPATIBILITY:
  All public names are re-exported from this package so that existing
  imports like::

      from clinical_reasoning.services.management_plan import (
          DISEASE_TREATMENT_PROFILES,
          ManagementPlan,
          generate_management_plan,
      )

  continue to work unchanged.

PACKAGE STRUCTURE:
  management_plan/
    __init__.py          — This file (backward-compatible re-exports)
    base.py              — ManagementPlan dataclass, generate_management_plan,
                           shared helper functions
    registry.py          — ProfileRegistry and factory utilities
    profiles/            — Disease-specific treatment protocol data
      __init__.py        — Auto-imports all profile modules
      primary.py         — IgAN, MN, MCD, FSGS
      autoimmune.py      — Lupus, AAV, Anti-GBM, IgG4-RD, Sarcoidosis
      infection.py       — Infection-related, HBV, HCV, HIVAN, Drug-induced
      complement.py      — C3G, MPGN, DDD, CFHR
      rare.py            — MGRS, Amyloidosis, Cryoglobulinemic, Immunotactoid, etc.
      hereditary.py      — Alport, TBMN, Fabry
      diabetic.py        — DKD, DKD+GN
      transplant.py      — Recurrent diseases, AMR, TCMR, CNI, BK virus
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import profile data modules — this triggers auto-registration with the
# ProfileRegistry, so DISEASE_TREATMENT_PROFILES is populated.
# ---------------------------------------------------------------------------
from . import profiles as _profiles  # noqa: F401  — triggers registration

# ---------------------------------------------------------------------------
# Re-export public API for backward compatibility
# ---------------------------------------------------------------------------
from .registry import ProfileRegistry  # noqa: F401

# The merged dict that existing code reads from.
DISEASE_TREATMENT_PROFILES: dict[str, dict[str, Any]] = ProfileRegistry.merge_all()

from .base import (  # noqa: F401
    ManagementPlan,
    generate_management_plan,
    _build_general_measures,
    _build_safety_checks,
    _build_patient_education,
    _intensify_monitoring,
    _add_ckd_modifications,
    _build_default_plan,
)

__all__ = [
    # Data
    "DISEASE_TREATMENT_PROFILES",
    # Classes
    "ManagementPlan",
    "ProfileRegistry",
    # Functions
    "generate_management_plan",
    # Internals (kept for backward compat — existing code may import these)
    "_build_general_measures",
    "_build_safety_checks",
    "_build_patient_education",
    "_intensify_monitoring",
    "_add_ckd_modifications",
    "_build_default_plan",
]

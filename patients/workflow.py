"""
Shared enumerations for the BIRDEM GN management workflow.

Kept in the base `patients` app so every downstream app (encounters, pathology,
analytics) can import them without a circular dependency. The workflow itself:

    suspected → admit + biopsy → baseline form → biopsy report →
    GN-clinic registration → active follow-up → response → remission →
    post-remission monitoring → (relapse → active) → outcome

See analytics/services/workflow.py for the phase state machine that drives the
`Patient.current_phase` transitions from the per-visit clinician assessment.
"""
from django.db import models


class RegistrationStatus(models.TextChoices):
    """Where a suspected GN patient sits in the registry decision."""
    SUSPECTED = "suspected", "Suspected — under evaluation"
    REGISTERED = "registered", "Registered in GN clinic"
    NOT_REGISTERED = "not_registered", "Not registered (managed elsewhere)"
    EXCLUDED = "excluded", "Excluded / not GN"


class DiseasePhase(models.TextChoices):
    """Disease-activity phase of a registered patient (updated at each visit)."""
    ACTIVE = "active", "Active disease (pre-remission)"
    REMISSION = "remission", "In remission"
    POST_REMISSION = "post_remission", "Post-remission monitoring"
    RELAPSE = "relapse", "Relapse"


class ClinicianResponse(models.TextChoices):
    """The treating clinician's response assessment at a follow-up visit.
    Complements the lab-derived remission the outcome engine computes."""
    NOT_ASSESSED = "not_assessed", "Not assessed"
    COMPLETE = "complete", "Complete remission"
    PARTIAL = "partial", "Partial remission"
    NONE = "none", "No response"
    STABLE = "stable", "Stable / maintenance"


class BiopsyIndication(models.TextChoices):
    """Why the index renal biopsy was performed (drives biopsy-yield analysis)."""
    NEPHROTIC = "nephrotic", "Nephrotic syndrome"
    NEPHRITIC = "nephritic", "Nephritic syndrome"
    RPGN = "rpgn", "Rapidly progressive GN"
    SUB_NEPHROTIC = "sub_nephrotic", "Sub-nephrotic proteinuria"
    ISOLATED_HEMATURIA = "hematuria", "Isolated glomerular haematuria"
    UNEXPLAINED_AKI = "aki", "Unexplained AKI"
    UNEXPLAINED_CKD = "ckd", "Unexplained CKD / proteinuria"
    DIABETIC_ATYPICAL = "diabetic_atypical", "Diabetic with atypical features"
    SYSTEMIC = "systemic", "Systemic disease (SLE/vasculitis) with renal involvement"
    OTHER = "other", "Other"


class BiopsyResult(models.TextChoices):
    """Diagnostic yield of the biopsy — the numerator/denominator of biopsy-yield."""
    POSITIVE = "positive", "Positive — specific GN diagnosis"
    NEGATIVE = "negative", "Negative — no specific GN"
    INCONCLUSIVE = "inconclusive", "Inconclusive / inadequate"


class RelapseType(models.TextChoices):
    """Character of a documented relapse (§ relapse surveillance)."""
    PROTEINURIC = "proteinuric", "Proteinuric relapse"
    NEPHROTIC = "nephrotic", "Nephrotic relapse"
    NEPHRITIC = "nephritic", "Nephritic flare"
    FUNCTIONAL = "functional", "Functional (rising creatinine)"
    SEROLOGIC = "serologic", "Serologic (e.g. rising anti-PLA2R / dsDNA)"

"""The one writer of the patient's pathology summary.

Patient.biopsy_diagnosis / gn_broad_group / gn_primary_secondary /
oxford_mestc / isn_rps_class are a read-only PROJECTION of one selected biopsy,
recorded with its source (Patient.pathology_source_biopsy) and state.

Previously guided entry copied values only into EMPTY patient fields (a second
biopsy never changed them), review finalization did not touch them at all, and
the fields were editable on the patient form -- so the summary, the biopsy
and the adjudicated read could each say something different.

Selection rule
--------------
* The newest biopsy whose review is final (concordant or adjudicated) and that
  has a diagnosis is the source ("final").
* Otherwise the newest biopsy with a diagnosis is the source ("provisional":
  a local read still awaiting central review).
* A newer biopsy that is not final never displaces a final one; it is listed
  as pending (``pending_biopsies``) so the UI can show it.

Disease scores are projected only when they belong to the selected
diagnosis's family, so a change of diagnosis cannot leave an obsolete MEST-C
or ISN/RPS class looking current. The clinician's working diagnosis
(Patient.primary_diagnosis) is NOT overwritten; an empty one is prefilled, and
a differing one can be updated only by adopt_pathology_diagnosis.
"""
from __future__ import annotations

import contextlib
import threading
from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from pathology import diagnosis as dxrules

_local = threading.local()


@contextlib.contextmanager
def deferred_projection():
    """Collect projection requests and run each patient's once, on exit.

    A guided save writes the biopsy, its diagnosis and several panels; without
    this, the model signals would re-project (and re-save the patient) after
    every step.
    """
    depth = getattr(_local, "depth", 0)
    if depth == 0:
        _local.pending = set()
    _local.depth = depth + 1
    try:
        yield
    finally:
        _local.depth -= 1
        if _local.depth == 0:
            pending, _local.pending = _local.pending, set()
            from patients.models import Patient
            for patient in Patient.objects.filter(pk__in=pending):
                project_pathology(patient)


def request_projection(patient_id) -> None:
    """Called by model signals (admin, API, any save of a pathology part)."""
    if getattr(_local, "depth", 0) > 0:
        _local.pending.add(patient_id)
        return
    from patients.models import Patient
    patient = Patient.objects.filter(pk=patient_id).first()
    if patient is not None:
        project_pathology(patient)

FINAL_STATUSES = {"concordant", "adjudicated"}
PROJECTED_FIELDS = ["biopsy_diagnosis", "gn_broad_group", "gn_primary_secondary",
                    "oxford_mestc", "isn_rps_class"]


@dataclass
class Selection:
    biopsy: object = None
    state: str = ""                       # "final" | "provisional" | ""
    pending_biopsies: list = field(default_factory=list)


def _has_diagnosis(biopsy) -> bool:
    try:
        return bool(biopsy.diagnosis.diagnosis)
    except Exception:
        return False


def select_source(patient) -> Selection:
    biopsies = list(patient.biopsies.select_related("diagnosis")
                    .order_by("-biopsy_date", "-id"))
    final = next((b for b in biopsies
                  if b.review_status in FINAL_STATUSES and _has_diagnosis(b)), None)
    if final is not None:
        newer = []
        for b in biopsies:
            if b.pk == final.pk:
                break
            newer.append(b)
        return Selection(final, "final", newer)
    provisional = next((b for b in biopsies if _has_diagnosis(b)), None)
    if provisional is not None:
        newer = []
        for b in biopsies:
            if b.pk == provisional.pk:
                break
            newer.append(b)
        return Selection(provisional, "provisional", newer)
    return Selection(None, "", biopsies)


def mestc_text(score) -> str:
    if score is None:
        return ""
    parts = [f"{k}{getattr(score, k)}" for k in ("M", "E", "S", "T", "C")
             if getattr(score, k) is not None]
    return "".join(parts)


def _related(biopsy, name):
    try:
        return getattr(biopsy, name)
    except Exception:
        return None


def projected_values(biopsy) -> dict:
    """What the patient summary should say for this biopsy."""
    if biopsy is None:
        return {f: "" for f in PROJECTED_FIELDS}
    dx = _related(biopsy, "diagnosis")
    q = dxrules.effective_qualifiers(biopsy)
    fam = q.get("family", "")
    values = {
        "biopsy_diagnosis": (dx.get_diagnosis_display() or dx.diagnosis) if dx else "",
        "gn_broad_group": dx.broad_group if dx else "",
        "gn_primary_secondary": q.get("primary_secondary", ""),
        "oxford_mestc": mestc_text(_related(biopsy, "igan_score")) if fam == dxrules.IGAN else "",
        "isn_rps_class": q.get("isn_rps_class", "") if fam == dxrules.LUPUS else "",
    }
    # Patient.gn_primary_secondary accepts primary/secondary/unknown only.
    if values["gn_primary_secondary"] not in ("", "primary", "secondary", "unknown"):
        values["gn_primary_secondary"] = ""
    return values


@transaction.atomic
def project_pathology(patient) -> list[str]:
    """Recompute the patient's pathology summary. Returns the changed fields.

    Idempotent; safe to call from any path (guided entry, amendment, review
    finalization, API, admin signals).
    """
    from patients.models import Patient
    patient = Patient.objects.select_for_update().get(pk=patient.pk)
    sel = select_source(patient)

    if sel.biopsy is None and patient.pathology_source_biopsy_id is None:
        # No interpretable biopsy and nothing projected before: leave any
        # legacy, manually-entered summary untouched (it stays editable).
        return []

    values = projected_values(sel.biopsy)
    changed = [f for f, v in values.items() if getattr(patient, f) != v]
    for f in changed:
        setattr(patient, f, values[f])

    source_id = sel.biopsy.pk if sel.biopsy is not None else None
    if patient.pathology_source_biopsy_id != source_id:
        patient.pathology_source_biopsy_id = source_id
        changed.append("pathology_source_biopsy")
    if patient.pathology_projection_state != sel.state:
        patient.pathology_projection_state = sel.state
        changed.append("pathology_projection_state")

    # The working diagnosis is the clinician's. Prefill it only when empty.
    if (not patient.primary_diagnosis and sel.biopsy is not None
            and _has_diagnosis(sel.biopsy)):
        patient.primary_diagnosis = sel.biopsy.diagnosis.diagnosis
        changed.append("primary_diagnosis")

    if changed:
        patient.pathology_projected_at = timezone.now()
        from audit.local import acting_as, current_actor
        with acting_as(current_actor(), reason="Pathology summary projected from biopsy"):
            patient.save(update_fields=changed + ["pathology_projected_at", "updated_at"])
    return changed


def working_diagnosis_differs(patient) -> bool:
    src = patient.pathology_source_biopsy
    if src is None or not _has_diagnosis(src):
        return False
    return (patient.primary_diagnosis or "") != src.diagnosis.diagnosis


@transaction.atomic
def adopt_pathology_diagnosis(patient, *, user=None, reason=""):
    """Explicitly adopt the selected pathology conclusion as the working
    diagnosis (audited). Returns the new working diagnosis."""
    from audit.local import acting_as
    src = patient.pathology_source_biopsy
    if src is None or not _has_diagnosis(src):
        raise ValueError("There is no biopsy diagnosis to adopt.")
    new = src.diagnosis.diagnosis
    if patient.primary_diagnosis != new:
        patient.primary_diagnosis = new
        why = reason.strip() or f"Adopted pathology diagnosis from biopsy {src.biopsy_date}"
        with acting_as(user, reason=why[:240]):
            patient.save(update_fields=["primary_diagnosis", "updated_at"])
    return new

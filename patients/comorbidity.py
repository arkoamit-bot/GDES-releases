"""Comorbidities: recorded once on the patient record, used everywhere.

Two different facts used to share one set of columns:

* the CURRENT state of each condition -- owned by Patient, edited on the
  patient form, three-state (present / absent / not recorded), with every
  change stamped in Patient.condition_provenance; and
* the ENROLLMENT snapshot -- owned by BaselineAssessment, captured once when
  the baseline is created (dated, with its source) and afterwards changed only
  by an explicit, audited correction (correct_baseline_snapshot).

Previously the baseline columns were a live mirror refreshed on every baseline
save (so an unrelated note edit rewrote enrollment history) and the summary
OR-ed both copies (so a condition corrected to absent kept reappearing from the
baseline). Now the summary reads the current state; the baseline value is used
only for a condition that has never been recorded on the patient since the
change (legacy data), and such items are flagged for reconciliation.
"""
from __future__ import annotations

# Recorded on Patient; BaselineAssessment carries a snapshot column of each.
LEVEL2_COMORBIDITY_FIELDS: list[str] = [
    "hypertension",
    "cvd_history",
    "autoimmune_disease",
    "chronic_infection",
    "malignancy",
    "previous_kidney_disease",
    "prior_immunosuppression",
    "family_history_kidney",
    "diabetic_retinopathy",
    "neuropathy",
    "diabetic_foot_history",
]

# Same value, different field name on each model.
RENAMED_ON_BASELINE: dict[str, str] = {"smoking_status": "smoking"}

# The baseline snapshot columns -- excluded from the baseline form so nothing
# is asked twice.
BASELINE_MIRROR_FIELDS: list[str] = (
    LEVEL2_COMORBIDITY_FIELDS + list(RENAMED_ON_BASELINE.values()))

# How each flag reads in a prescription, prompt or printed summary.
LABELS: dict[str, str] = {
    "hypertension": "Hypertension",
    "cvd_history": "Cardiovascular disease",
    "autoimmune_disease": "Autoimmune disease",
    "chronic_infection": "Chronic infection (HBV/HCV/HIV/TB)",
    "malignancy": "Malignancy",
    "previous_kidney_disease": "Previous kidney disease",
    "prior_immunosuppression": "Prior immunosuppression",
    "family_history_kidney": "Family history of kidney disease",
    "diabetic_retinopathy": "Diabetic retinopathy",
    "neuropathy": "Neuropathy",
    "diabetic_foot_history": "Diabetic foot disease",
}

PRESENT, ABSENT, UNKNOWN = "present", "absent", "unknown"


def condition_state(patient, field: str) -> str:
    """present / absent / unknown for one condition on the patient record.

    False counts as absent only when it was recorded (a provenance stamp
    exists). Legacy rows carry the old default False, which never meant
    "examined and ruled out".
    """
    value = getattr(patient, field, None)
    if value is True:
        return PRESENT
    if value is False and field in (getattr(patient, "condition_provenance", None) or {}):
        return ABSENT
    return UNKNOWN


def is_recorded(patient, field: str) -> bool:
    return field in (getattr(patient, "condition_provenance", None) or {})


def snapshot_to_baseline(patient, baseline) -> list[str]:
    """Capture the patient's recorded conditions onto a baseline snapshot.

    Only recorded states are copied: a condition that is not recorded on the
    patient leaves whatever the baseline already holds (legacy data is never
    cleared on the strength of an unset flag). Returns the changed fields.
    Called once when the baseline is created, never on later saves.
    """
    changed = []
    if patient is None or baseline is None:
        return changed

    for field in LEVEL2_COMORBIDITY_FIELDS:
        if not hasattr(baseline, field):
            continue
        state = condition_state(patient, field)
        if state == UNKNOWN:
            continue
        value = state == PRESENT
        if getattr(baseline, field, None) != value:
            setattr(baseline, field, value)
            changed.append(field)
    for patient_field, baseline_field in RENAMED_ON_BASELINE.items():
        value = getattr(patient, patient_field, None)
        if value and getattr(baseline, baseline_field, None) != value:
            setattr(baseline, baseline_field, value)
            changed.append(baseline_field)
    return changed


# Kept for callers written against the old mirror; same one-shot semantics.
mirror_to_baseline = snapshot_to_baseline


def correct_baseline_snapshot(baseline, changes: dict, *, reason: str, user=None):
    """Explicitly correct the enrollment snapshot -- a separate, audited act.

    ``changes`` maps baseline snapshot fields to their corrected values. The
    reason is mandatory and lands on every AuditLog row for the change.
    """
    from django.utils import timezone

    from audit.local import acting_as

    reason = (reason or "").strip()
    if not reason:
        raise ValueError("A reason is required to correct the enrollment snapshot.")
    unknown = set(changes) - set(BASELINE_MIRROR_FIELDS)
    if unknown:
        raise ValueError(f"Not snapshot fields: {', '.join(sorted(unknown))}")
    for field, value in changes.items():
        setattr(baseline, field, value)
    baseline.comorbidity_snapshot_source = "correction"
    baseline.comorbidity_snapshot_at = timezone.now()
    with acting_as(user, reason=f"Baseline snapshot correction: {reason}"[:240]):
        baseline.save()
    return baseline


def comorbidity_items(patient, baseline=None) -> list[dict]:
    """Structured current comorbidities with their source.

    ``source`` is "patient" for the recorded current state, or
    "legacy_baseline" for a condition only a pre-2026-09-27 baseline mentions
    and the patient record has never stated -- shown, but flagged for review.
    """
    items: list[dict] = []
    seen: set[str] = set()

    def add(label, source="patient", field=""):
        if label and label not in seen:
            seen.add(label)
            items.append({"label": label, "source": source, "field": field})

    for field in LEVEL2_COMORBIDITY_FIELDS:
        state = condition_state(patient, field)
        if state == PRESENT:
            add(LABELS[field], "patient", field)
        elif (state == UNKNOWN and not is_recorded(patient, field)
              and getattr(baseline, field, None) is True):
            add(LABELS[field], "legacy_baseline", field)

    status = getattr(patient, "diabetes_status", "") or ""
    if status and status != "none":
        label = (patient.get_diabetes_status_display()
                 if hasattr(patient, "get_diabetes_status_display") else status)
        add(f"Diabetes mellitus ({label})", "patient", "diabetes_status")

    hep = getattr(patient, "hepatitis_status", "") or ""
    if hep and hep != "negative":
        add({"hbv": "Hepatitis B", "hcv": "Hepatitis C",
             "both": "Hepatitis B + C"}.get(hep, f"Hepatitis ({hep})"),
            "patient", "hepatitis_status")
    if (getattr(patient, "hiv_status", "") or "") == "positive":
        add("HIV positive", "patient", "hiv_status")

    smoking = getattr(patient, "smoking_status", "") or ""
    if smoking == "Current":
        add("Current smoker", "patient", "smoking_status")
    elif not smoking and (getattr(baseline, "smoking", "") or "") == "Current":
        add("Current smoker", "legacy_baseline", "smoking_status")

    return items


def comorbidity_summary(patient, baseline=None) -> list[str]:
    """The one comorbidity list: prescriptions, AI prompts, plan context."""
    return [item["label"] for item in comorbidity_items(patient, baseline)]


def comorbidity_text(patient, baseline=None) -> str:
    """comorbidity_summary as one line, for prompts and printed summaries."""
    return ", ".join(comorbidity_summary(patient, baseline)) or "None"


def structured_labels() -> set[str]:
    """Labels the patient record owns: a prescription must not keep its own
    copy of these (they come from the current state every time)."""
    labels = set(LABELS.values()) | {"Hypertension", "Diabetes mellitus",
                                     "Current smoker", "HIV positive",
                                     "Hepatitis B", "Hepatitis C", "Hepatitis B + C"}
    return labels

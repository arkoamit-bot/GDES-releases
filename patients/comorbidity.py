"""Comorbidities: recorded once on the patient record, used everywhere.

The Patient model always declared the intent -- "Level 2: persistent clinical
data (single source of truth) ... entered once at baseline; auto-carried-forward
to all encounters" -- but the same eleven comorbidities were also asked on the
baseline assessment. Two copies of one clinical fact, kept in step by a partial
sync, so they could disagree; and each downstream caller (prescription pre-fill,
the two AI prompts) hand-rolled its own short list from whichever copy it
happened to know about.

Now there is one input (the patient form), one source of truth (Patient), and
one renderer (comorbidity_summary). BaselineAssessment keeps its columns for
historical data and analytics, mirrored from the patient on save -- nothing
re-asks them.
"""
from __future__ import annotations

# Recorded on Patient; BaselineAssessment carries a mirror column of each.
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

# The baseline columns that mirror the patient record — excluded from the
# baseline form so nothing is asked twice.
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


def mirror_to_baseline(patient, baseline) -> list[str]:
    """Copy the patient's comorbidities onto the baseline row.

    The baseline form no longer asks for them, so without this its columns would
    read False for every patient and any analytic query over them would quietly
    return nothing. Returns the baseline fields that changed.
    """
    changed = []
    if patient is None or baseline is None:
        return changed

    pairs = [(f, f) for f in LEVEL2_COMORBIDITY_FIELDS]
    pairs += list(RENAMED_ON_BASELINE.items())

    for patient_field, baseline_field in pairs:
        if not hasattr(baseline, baseline_field):
            continue
        value = getattr(patient, patient_field, None)
        if value in (None, "", False):
            # Not recorded is not the same as ruled out; never clear the mirror
            # on the strength of an unset flag.
            continue
        if getattr(baseline, baseline_field, None) != value:
            setattr(baseline, baseline_field, value)
            changed.append(baseline_field)
    return changed


def comorbidity_summary(patient, baseline=None) -> list[str]:
    """The one comorbidity list: prescriptions, AI prompts, plan context.

    Reads the patient record, falling back to the baseline mirror for patients
    registered before comorbidities moved onto the patient form. Previously each
    caller built its own list, so autoimmune disease, chronic infection and
    malignancy never reached the AI prompts however carefully they were recorded.
    """
    items: list[str] = []

    def add(label: str) -> None:
        if label and label not in items:
            items.append(label)

    for field in LEVEL2_COMORBIDITY_FIELDS:
        if getattr(patient, field, False) or getattr(baseline, field, False):
            add(LABELS[field])

    status = getattr(patient, "diabetes_status", "") or ""
    if status and status != "none":
        label = (patient.get_diabetes_status_display()
                 if hasattr(patient, "get_diabetes_status_display") else status)
        add(f"Diabetes mellitus ({label})")

    hep = getattr(patient, "hepatitis_status", "") or ""
    if hep and hep != "negative":
        add({"hbv": "Hepatitis B", "hcv": "Hepatitis C",
             "both": "Hepatitis B + C"}.get(hep, f"Hepatitis ({hep})"))
    if (getattr(patient, "hiv_status", "") or "") == "positive":
        add("HIV positive")

    smoking = (getattr(patient, "smoking_status", "")
               or getattr(baseline, "smoking", "") or "")
    if smoking == "Current":
        add("Current smoker")

    return items


def comorbidity_text(patient, baseline=None) -> str:
    """comorbidity_summary as one line, for prompts and printed summaries."""
    return ", ".join(comorbidity_summary(patient, baseline)) or "None"

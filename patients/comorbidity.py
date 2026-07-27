"""Carry comorbidities forward from the patient record to every later form.

The Patient model already declares the intent (see "Level 2: Persistent clinical
data (single source of truth) -- entered once at baseline; auto-carried-forward
to all encounters"), but nothing implemented it: BaselineAssessment keeps its own
copies of hypertension / autoimmune_disease / chronic_infection / smoking, and
the baseline form opened blank. A clinician who ticked DM and HTN at registration
had to tick them again -- and if they didn't, the two records silently disagreed.

Note the reverse direction already exists: BaselineAssessment.save() calls
_sync_level2_to_patient(), which seeds empty Patient fields from the baseline.
Only the forward direction -- patient record into the next form -- was missing.

This module is the single place that knows:
  * which fields are duplicated between Patient and BaselineAssessment,
  * how to seed a new baseline form from the patient record,
  * how to render one comorbidity list for everything downstream (prescription
    pre-fill, the Vera prompts, management-plan context).
"""
from __future__ import annotations

# Patient field -> BaselineAssessment field, for the values stored in both.
LEVEL2_TO_BASELINE: dict[str, str] = {
    "hypertension": "hypertension",
    "autoimmune_disease": "autoimmune_disease",
    "chronic_infection": "chronic_infection",
    "smoking_status": "smoking",
}


def baseline_initial_from_patient(patient) -> dict:
    """Initial values that pre-tick a NEW baseline form from the patient record.

    Only used when no baseline exists yet; a saved baseline is never overwritten
    by the patient record, because the clinician may have corrected it there.
    """
    initial = {}
    for patient_field, baseline_field in LEVEL2_TO_BASELINE.items():
        value = getattr(patient, patient_field, None)
        if value:  # False / "" means "not recorded", so don't seed it
            initial[baseline_field] = value
    return initial


def comorbidity_summary(patient, baseline=None) -> list[str]:
    """One comorbidity list for prescriptions, Vera prompts and plan context.

    Reads the patient record first (the single source of truth) and fills in the
    conditions that only the baseline assessment records. Previously each caller
    built its own short list, so DM and HTN reached the AI prompt but autoimmune
    disease, chronic infection and malignancy silently did not.
    """
    items: list[str] = []

    def add(label: str) -> None:
        if label and label not in items:
            items.append(label)

    if getattr(patient, "hypertension", False) or getattr(baseline, "hypertension", False):
        add("Hypertension")

    status = getattr(patient, "diabetes_status", "") or ""
    if status and status != "none":
        label = (patient.get_diabetes_status_display()
                 if hasattr(patient, "get_diabetes_status_display") else status)
        add(f"Diabetes mellitus ({label})")

    if getattr(patient, "autoimmune_disease", False) or getattr(baseline, "autoimmune_disease", False):
        add("Autoimmune disease")
    if getattr(patient, "chronic_infection", False) or getattr(baseline, "chronic_infection", False):
        add("Chronic infection (HBV/HCV/HIV/TB)")

    hep = getattr(patient, "hepatitis_status", "") or ""
    if hep and hep != "negative":
        add({"hbv": "Hepatitis B", "hcv": "Hepatitis C",
             "both": "Hepatitis B + C"}.get(hep, f"Hepatitis ({hep})"))
    if (getattr(patient, "hiv_status", "") or "") == "positive":
        add("HIV positive")

    if (getattr(patient, "smoking_status", "") or "") == "Current":
        add("Current smoker")

    if baseline is not None:
        for attribute, label in (
            ("cvd_history", "Cardiovascular disease"),
            ("malignancy", "Malignancy"),
            ("previous_kidney_disease", "Previous kidney disease"),
            ("prior_immunosuppression", "Prior immunosuppression"),
            ("diabetic_retinopathy", "Diabetic retinopathy"),
            ("neuropathy", "Neuropathy"),
            ("diabetic_foot_history", "Diabetic foot disease"),
            ("family_history_kidney", "Family history of kidney disease"),
        ):
            if getattr(baseline, attribute, False):
                add(label)

    return items


def comorbidity_text(patient, baseline=None) -> str:
    """comorbidity_summary as one line, for prompts and printed summaries."""
    return ", ".join(comorbidity_summary(patient, baseline)) or "None"

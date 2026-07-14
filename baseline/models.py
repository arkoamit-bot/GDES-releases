"""
BaselineAssessment — the at-enrollment clinical/demographic snapshot (Excel
sheet 2). One per patient. BMI and its Asian-cutoff category are auto-derived.
"""
from decimal import Decimal

from django.db import models

from patients import choices
from patients.models import Patient


def asian_bmi_category(bmi):
    """WHO Asian-specific BMI cut-offs."""
    if bmi is None:
        return ""
    b = float(bmi)
    if b < 18.5:
        return "underweight"
    if b < 23:
        return "normal"
    if b < 27.5:
        return "overweight"
    return "obese"


class BaselineAssessment(models.Model):
    class Syndrome(models.TextChoices):
        NEPHROTIC = "nephrotic", "Nephrotic syndrome"
        NEPHRITIC = "nephritic", "Nephritic syndrome"
        RPGN = "rpgn", "Rapidly progressive GN"
        ASYMPTOMATIC = "asymptomatic", "Asymptomatic urinary abnormality"
        ISOLATED_HEMATURIA = "hematuria", "Isolated hematuria"
        ISOLATED_PROTEINURIA = "proteinuria", "Isolated proteinuria"
        CKD = "ckd", "Chronic kidney disease"
        AKI = "aki", "Acute kidney injury"

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="baseline")
    assessment_date = models.DateField(null=True, blank=True)

    # A. Social / demographic.
    division_residence = models.CharField(max_length=60, blank=True)
    socioeconomic_status = models.CharField(
        max_length=30, blank=True, choices=choices.SOCIOECONOMIC)
    monthly_income_bdt = models.PositiveIntegerField(null=True, blank=True)
    education = models.CharField(max_length=40, blank=True, choices=choices.EDUCATION)
    occupation = models.CharField(max_length=60, blank=True)
    smoking = models.CharField(max_length=20, blank=True, choices=choices.SMOKING)
    alcohol_use = models.CharField(max_length=10, blank=True, choices=choices.ALCOHOL)

    # B. Medical history (comorbidity flags + free-text drug history).
    previous_kidney_disease = models.BooleanField(default=False)
    autoimmune_disease = models.BooleanField(default=False)
    chronic_infection = models.BooleanField(default=False)
    malignancy = models.BooleanField(default=False)
    prior_immunosuppression = models.BooleanField(default=False)
    drug_history = models.TextField(blank=True)

    # Anthropometry / vitals.
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                              editable=False)
    bmi_category = models.CharField(max_length=12, blank=True, editable=False)
    systolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)

    # Diabetes burden.
    dm_duration_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    hba1c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    diabetic_retinopathy = models.BooleanField(default=False)
    neuropathy = models.BooleanField(default=False)
    diabetic_foot_history = models.BooleanField(default=False)

    # C. Clinical presentation.
    hypertension = models.BooleanField(default=False)
    cvd_history = models.BooleanField(default=False)
    # Kept for backward compatibility (single primary syndrome, synced from the
    # multi-select below); presentation_syndromes holds the full multi-select.
    presentation_syndrome = models.CharField(
        max_length=14, choices=Syndrome.choices, blank=True)
    presentation_syndromes = models.JSONField(default=list, blank=True)
    presenting_symptoms = models.JSONField(default=list, blank=True)
    oedema_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    active_urinary_sediment = models.BooleanField(default=False)
    rbc_casts = models.BooleanField(default=False)
    family_history_kidney = models.BooleanField(default=False)

    # D. Clinical examination (BP/weight/oedema already captured above).
    pulse_bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    volume_status = models.CharField(max_length=12, blank=True, choices=choices.VOLUME_STATUS)
    skin_findings = models.CharField(max_length=200, blank=True)
    joint_findings = models.CharField(max_length=200, blank=True)
    fundoscopy = models.CharField(max_length=200, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient"]

    def __str__(self):
        return f"Baseline {self.patient.patient_id}"

    # Best-effort map from a multi-select syndrome to the legacy single value
    # (so the research export's presentation_syndrome column stays populated).
    _SYNDROME_MAP = {
        "nephrotic": "nephrotic", "nephritic": "nephritic",
        "nephritic_nephrotic": "nephritic", "rpgn": "rpgn", "aki": "aki",
        "ckd": "ckd", "isolated_proteinuria": "proteinuria",
        "proteinuria_hematuria": "proteinuria", "isolated_hematuria": "hematuria",
        "incidental": "asymptomatic",
    }

    def save(self, *args, **kwargs):
        # Keep the legacy single syndrome in sync with the primary multi-select.
        if self.presentation_syndromes:
            first = self.presentation_syndromes[0]
            self.presentation_syndrome = self._SYNDROME_MAP.get(
                first, self.presentation_syndrome)
        if self.height_cm and self.weight_kg and float(self.height_cm) > 0:
            h = float(self.height_cm) / 100.0
            self.bmi = Decimal(str(round(float(self.weight_kg) / (h * h), 1)))
            self.bmi_category = asian_bmi_category(self.bmi)
        else:
            self.bmi = None
            self.bmi_category = ""
        super().save(*args, **kwargs)
        # --- Level 2: sync persistent clinical data to Patient (single source) ---
        self._sync_level2_to_patient()

    def _sync_level2_to_patient(self):
        """Copy Level 2 persistent fields from baseline to Patient model."""
        p = self.patient
        changed = False
        _set = lambda attr, val: (
            setattr(p, attr, val) if getattr(p, attr) != val else None) or True
        # Only set Patient fields if they are currently empty (don't overwrite
        # clinician edits on Patient — baseline is the initial seed).
        if not p.hypertension:
            p.hypertension = self.hypertension
            changed = True
        if not p.autoimmune_disease:
            p.autoimmune_disease = self.autoimmune_disease
            changed = True
        if not p.chronic_infection:
            p.chronic_infection = self.chronic_infection
            changed = True
        if not p.smoking_status:
            p.smoking_status = self.smoking or ""
            changed = True
        if not p.diabetes_status or p.diabetes_status == "none":
            # Infer diabetes status from baseline if available.
            if self.dm_duration_years:
                p.diabetes_status = "t2"  # default to T2 if duration known
                changed = True
        if changed:
            p.save(update_fields=[
                "hypertension", "autoimmune_disease", "chronic_infection",
                "smoking_status", "diabetes_status", "updated_at"])

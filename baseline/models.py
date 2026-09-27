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

    # B. Medical history -- the ENROLLMENT SNAPSHOT of the patient's
    # conditions, captured once when this baseline is created (see save()).
    # The patient record owns the current state; a later change there never
    # rewrites this snapshot. Correct it only through
    # patients.comorbidity.correct_baseline_snapshot (audited, with reason).
    comorbidity_snapshot_at = models.DateTimeField(null=True, blank=True, editable=False)
    comorbidity_snapshot_source = models.CharField(
        max_length=16, blank=True, editable=False,
        help_text="enrollment | legacy_mirror | correction")
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
    # Legacy scalar. HbA1c is now recorded as a dated LabResult through the
    # laboratory service; hba1c_result links the observation this baseline
    # uses (see labs.services.baseline). The scalar keeps pre-2026-09-27 values
    # and is never written by the forms again.
    hba1c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True,
                                editable=False)
    hba1c_result = models.ForeignKey(
        "labs.LabResult", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", editable=False,
        help_text="The HbA1c observation this baseline reports.")
    # The visit at which this baseline was taken, when it is the same visit.
    baseline_encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL, null=True,
        blank=True, related_name="+",
        help_text="Link only when the baseline was captured at this visit.")
    diabetic_retinopathy = models.BooleanField(default=False)
    neuropathy = models.BooleanField(default=False)
    diabetic_foot_history = models.BooleanField(default=False)

    # C. Clinical presentation.
    hypertension = models.BooleanField(default=False)
    cvd_history = models.BooleanField(default=False)
    # Kept for backward compatibility (legacy single syndrome, projected from
    # the first element of presentation_syndromes, which is the primary
    # presentation; any further elements are additional presentations).
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

    # Legacy scalar -> canonical code, for rows that only have the scalar.
    _LEGACY_TO_CANONICAL = {
        "nephrotic": "nephrotic", "nephritic": "nephritic", "rpgn": "rpgn",
        "aki": "aki", "ckd": "ckd", "proteinuria": "isolated_proteinuria",
        "hematuria": "isolated_hematuria", "asymptomatic": "incidental",
    }

    def save(self, *args, **kwargs):
        # The list is canonical; the legacy scalar is a lossy projection of its
        # first (primary) element. A row that only has the scalar is lifted
        # into the list rather than losing it; an unmapped primary leaves the
        # scalar blank instead of stale.
        if self.presentation_syndromes:
            first = self.presentation_syndromes[0]
            self.presentation_syndrome = self._SYNDROME_MAP.get(first, "")
        elif self.presentation_syndrome:
            canonical = self._LEGACY_TO_CANONICAL.get(self.presentation_syndrome)
            if canonical:
                self.presentation_syndromes = [canonical]
        if self.height_cm and self.weight_kg and float(self.height_cm) > 0:
            h = float(self.height_cm) / 100.0
            self.bmi = Decimal(str(round(float(self.weight_kg) / (h * h), 1)))
            self.bmi_category = asian_bmi_category(self.bmi)
        else:
            self.bmi = None
            self.bmi_category = ""
        # Enrollment snapshot: captured ONCE, when the baseline is created.
        # Later saves (a note, a vital sign) must not rewrite enrollment history.
        if self._state.adding and self.comorbidity_snapshot_at is None:
            from django.utils import timezone
            from patients.comorbidity import snapshot_to_baseline
            snapshot_to_baseline(self.patient, self)
            self.comorbidity_snapshot_at = timezone.now()
            self.comorbidity_snapshot_source = "enrollment"
        super().save(*args, **kwargs)
        self._flag_diabetes_type()

    def _flag_diabetes_type(self):
        """A recorded DM duration means diabetes, but says nothing about type.

        Previously this silently set Type 2. Now a patient whose record says
        "no diabetes" is moved to "type not recorded" -- visible, and left for
        the clinician to confirm -- and a recorded type is never touched.
        """
        p = self.patient
        if p is None or not self.dm_duration_years or self.dm_duration_years <= 0:
            return
        if p.diabetes_status and p.diabetes_status != "none":
            return
        from audit.local import acting_as, current_actor
        p.diabetes_status = "unknown"
        with acting_as(current_actor(),
                       reason="Baseline records a diabetes duration; type not "
                              "recorded - needs clinician confirmation"):
            p.save(update_fields=["diabetes_status", "updated_at"])

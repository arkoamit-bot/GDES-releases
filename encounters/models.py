"""
ClinicalEncounter — the hub of the real-world workflow. One encounter per visit.
The prescription, the follow-up clinical data, and the lab orders all hang off
it, so the single act of "seeing the patient" populates the whole registry.

FollowUpVisit here is intentionally light: the longitudinal clinical fields the
research portfolio needs. In the full build it would carry the complete sheet-6
variable set; the prescription module only needs the encounter spine.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from patients.models import Patient
from patients.workflow import ClinicianResponse, DiseasePhase, RelapseType


class ClinicalEncounter(models.Model):
    class Type(models.TextChoices):
        BASELINE = "baseline", "Baseline / enrollment"
        FOLLOWUP = "followup", "Scheduled follow-up"
        UNSCHEDULED = "unscheduled", "Unscheduled / sick visit"

    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, related_name="encounters"
    )
    encounter_date = models.DateField()
    encounter_type = models.CharField(
        max_length=16, choices=Type.choices, default=Type.FOLLOWUP
    )
    seen_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="encounters", null=True, blank=True,
    )
    clinic_location = models.CharField(max_length=120, blank=True)

    # Clinical findings captured at the visit (subset; feeds FollowUpVisit).
    systolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    # --- Longitudinal GN follow-up (workflow step 5) ----------------------
    # Clinical status at the visit.
    edema_grade = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Peripheral oedema 0 (none) – 4 (anasarca).")
    symptoms = models.CharField(
        max_length=240, blank=True,
        help_text="Frothy urine, haematuria, breathlessness, etc.")
    # The clinician's response assessment (hybrid with the lab-computed remission).
    clinician_response = models.CharField(
        max_length=16, choices=ClinicianResponse.choices, blank=True)
    # Disease-activity phase recorded AT this visit (trajectory over time). The
    # patient's current_phase is set from the latest visit by the workflow engine.
    disease_phase = models.CharField(
        max_length=16, choices=DiseasePhase.choices, blank=True)
    treatment_adjusted = models.BooleanField(
        default=False, help_text="Was therapy changed at this visit?")

    advice = models.TextField(blank=True)
    next_due_date = models.DateField(null=True, blank=True)

    def clean(self):
        if self.systolic_bp is not None and (self.systolic_bp < 30 or self.systolic_bp > 300):
            raise ValidationError({"systolic_bp": "Systolic BP must be between 30 and 300 mmHg."})
        if self.diastolic_bp is not None and (self.diastolic_bp < 15 or self.diastolic_bp > 200):
            raise ValidationError({"diastolic_bp": "Diastolic BP must be between 15 and 200 mmHg."})
        if self.systolic_bp is not None and self.diastolic_bp is not None:
            if self.diastolic_bp > self.systolic_bp:
                raise ValidationError("Diastolic BP cannot exceed systolic BP.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-encounter_date"]
        indexes = [models.Index(fields=["patient", "encounter_date"])]

    def __str__(self):
        return f"{self.patient.patient_id} · {self.encounter_date} ({self.get_encounter_type_display()})"


class Admission(models.Model):
    """Inpatient stay for the diagnostic work-up (workflow step 2). Links the
    admission → biopsy → discharge → baseline-form segment of the pathway."""
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="admissions")
    admit_date = models.DateField()
    discharge_date = models.DateField(null=True, blank=True)
    ward = models.CharField(max_length=80, blank=True)
    reason = models.CharField(
        max_length=240, blank=True, help_text="Reason for admission / work-up.")
    biopsy = models.ForeignKey(
        "pathology.Biopsy", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="admissions", help_text="Biopsy done during this admission.")
    baseline_captured = models.BooleanField(
        default=False, help_text="Pre-discharge baseline data form completed.")
    discharge_advice = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "-admit_date"]
        indexes = [models.Index(fields=["patient", "admit_date"])]

    def __str__(self):
        span = f"{self.admit_date} → {self.discharge_date or 'inpatient'}"
        return f"{self.patient.patient_id}: admission {span}"


class RelapseEpisode(models.Model):
    """A documented relapse (workflow step 5E). Clinician-entered with explicit
    criteria; also emits a ClinicalEvent(RELAPSE) so the survival engine sees it,
    and flips the patient's phase back to Relapse → Active."""
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="relapses")
    encounter = models.ForeignKey(
        ClinicalEncounter, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="relapses")
    relapse_date = models.DateField()
    relapse_type = models.CharField(max_length=16, choices=RelapseType.choices)
    criteria = models.CharField(
        max_length=240, blank=True,
        help_text="Criteria met, e.g. 'UPCR 0.4→3.2 g/g; albumin 2.6'.")
    action_taken = models.CharField(
        max_length=240, blank=True, help_text="Treatment change in response.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "-relapse_date"]
        indexes = [models.Index(fields=["patient", "relapse_date"])]

    def __str__(self):
        return f"{self.patient.patient_id}: {self.get_relapse_type_display()} @ {self.relapse_date}"


class ClinicalEvent(models.Model):
    """Event-triggered hard/soft endpoints the outcome engine reads.

    Hard kidney/survival endpoints (ESKD, dialysis, transplant, death) and the
    soft disease endpoints (remission, relapse, major CV event) that can't be
    derived from labs alone. Each is a dated row — the survival-analysis time
    axis is built from these dates against the patient's index date.
    """
    class Type(models.TextChoices):
        ESKD = "eskd", "ESKD / kidney failure"
        DIALYSIS = "dialysis_start", "Dialysis started"
        TRANSPLANT = "transplant", "Kidney transplant"
        DEATH = "death", "Death"
        COMPLETE_REMISSION = "complete_remission", "Complete remission"
        PARTIAL_REMISSION = "partial_remission", "Partial remission"
        RELAPSE = "relapse", "Relapse / flare"
        MAJOR_CV = "major_cv", "Major cardiovascular event"

    # The subset that count as kidney-failure / death for survival endpoints.
    HARD_KIDNEY = {Type.ESKD, Type.DIALYSIS, Type.TRANSPLANT}

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=20, choices=Type.choices)
    event_date = models.DateField()
    encounter = models.ForeignKey(
        ClinicalEncounter, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events")
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "event_date"]
        indexes = [models.Index(fields=["patient", "event_type", "event_date"])]

    def __str__(self):
        return f"{self.patient.patient_id}: {self.get_event_type_display()} @ {self.event_date}"

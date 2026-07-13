"""
Registry-embedded trial platform.

    Study           — a study/trial definition (observational, quasi-exp, or RCT)
    StudyArm        — its arms, each with an allocation weight
    StudyEnrollment — a patient's screening + (for RCTs) randomized allocation

Designed so the registry doubles as a trial platform: enrol eligible patients,
randomize them with a reproducible stratified-block scheme, and then analyse the
arms with the existing survival / Cox engine (group_by="study:<code>").
"""
from django.conf import settings
from django.db import models

from patients.models import Patient


class Study(models.Model):
    class Type(models.TextChoices):
        OBSERVATIONAL = "observational", "Observational cohort"
        QUASI = "quasi_experimental", "Quasi-experimental"
        RCT = "rct", "Randomized controlled trial"

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        RECRUITING = "recruiting", "Recruiting"
        ACTIVE = "active", "Active (closed to recruitment)"
        CLOSED = "closed", "Closed"

    class Scheme(models.TextChoices):
        NONE = "none", "No randomization"
        SIMPLE = "simple", "Simple"
        BLOCK = "block", "Permuted block"
        STRATIFIED_BLOCK = "stratified_block", "Stratified permuted block"

    code = models.SlugField(max_length=40, unique=True)        # "ADVANCED-DKD-IGAN"
    title = models.CharField(max_length=240)
    study_type = models.CharField(max_length=20, choices=Type.choices)
    status = models.CharField(max_length=12, choices=Status.choices,
                              default=Status.PLANNING)
    target_enrollment = models.PositiveIntegerField(null=True, blank=True)
    # Maps to an analytics endpoint name where possible (e.g. composite_kidney_event).
    primary_endpoint = models.CharField(max_length=60, blank=True)

    # Randomization configuration.
    randomization_scheme = models.CharField(
        max_length=20, choices=Scheme.choices, default=Scheme.NONE)
    block_multipliers = models.JSONField(
        default=list, blank=True,
        help_text='Block-size multipliers of the ratio unit, e.g. [1, 2].')
    stratify_by = models.JSONField(
        default=list, blank=True,
        help_text='Stratification factors, e.g. ["diabetes", "egfr_stratum"].')
    random_seed = models.BigIntegerField(
        default=20260101, help_text="Fixes the allocation sequence (auditable).")
    requires_trial_consent = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        verbose_name_plural = "studies"

    def __str__(self):
        return f"{self.code} — {self.title}"

    @property
    def is_randomized(self):
        return self.randomization_scheme != self.Scheme.NONE

    def arms_ordered(self):
        return list(self.arms.order_by("order", "id"))


class StudyArm(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="arms")
    code = models.SlugField(max_length=40)                     # "hcq", "control"
    name = models.CharField(max_length=120)
    ratio = models.PositiveSmallIntegerField(
        default=1, help_text="Allocation weight (1:1 -> all arms ratio 1).")
    order = models.PositiveSmallIntegerField(default=0)
    is_control = models.BooleanField(default=False)

    class Meta:
        ordering = ["study", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["study", "code"], name="uniq_study_arm_code")
        ]

    def __str__(self):
        return f"{self.study.code}:{self.code}"


class StudyEnrollment(models.Model):
    class Status(models.TextChoices):
        SCREENED = "screened", "Screened"
        INELIGIBLE = "ineligible", "Ineligible"
        ENROLLED = "enrolled", "Enrolled"
        WITHDRAWN = "withdrawn", "Withdrawn"
        COMPLETED = "completed", "Completed"

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="enrollments")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="enrollments")

    status = models.CharField(max_length=12, choices=Status.choices,
                              default=Status.SCREENED)
    screened_date = models.DateField(null=True, blank=True)
    eligible = models.BooleanField(default=False)
    ineligibility_reasons = models.JSONField(default=list, blank=True)

    enrolled_date = models.DateField(null=True, blank=True)
    arm = models.ForeignKey(StudyArm, on_delete=models.PROTECT, null=True, blank=True,
                            related_name="enrollments")

    # Randomization provenance (reproducible + auditable).
    stratum = models.CharField(max_length=120, blank=True)
    sequence_position = models.IntegerField(null=True, blank=True)
    randomized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="randomizations")
    randomized_at = models.DateTimeField(null=True, blank=True)

    withdrawn_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["study", "patient"]
        constraints = [
            models.UniqueConstraint(fields=["study", "patient"],
                                    name="uniq_study_patient")
        ]

    def __str__(self):
        arm = f" -> {self.arm.code}" if self.arm else ""
        return f"{self.study.code} / {self.patient.patient_id} ({self.status}){arm}"

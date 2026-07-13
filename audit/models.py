"""
AuditLog  — append-only per-field change history (who / when / old -> new).
Consent   — versioned, withdrawable patient consent.

These are the two pieces a prospective registry needs before it can feed
registry-embedded trials: a defensible record of every data change, and a
consent trail with versions and withdrawal.
"""
from django.conf import settings
from django.db import models

from patients.models import Patient


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"

    # Target identity (kept as strings so a row survives the target's deletion).
    model_label = models.CharField(max_length=100)         # "prescriptions.Prescription"
    object_pk = models.CharField(max_length=64)
    object_repr = models.CharField(max_length=200, blank=True)

    action = models.CharField(max_length=8, choices=Action.choices)
    field_name = models.CharField(max_length=80, blank=True)  # blank on create/delete
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="audit_entries")
    change_reason = models.CharField(max_length=240, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at", "id"]
        indexes = [
            models.Index(fields=["model_label", "object_pk"]),
            models.Index(fields=["changed_at"]),
        ]

    def __str__(self):
        who = self.changed_by or "system"
        if self.action == self.Action.UPDATE:
            return f"{self.model_label}#{self.object_pk}.{self.field_name}: {self.old_value!r}->{self.new_value!r} by {who}"
        return f"{self.get_action_display()} {self.model_label}#{self.object_pk} by {who}"


class Consent(models.Model):
    class Type(models.TextChoices):
        REGISTRY = "registry", "Registry participation"
        BIOBANK = "biobank", "Biobank / sample storage"
        GENETIC = "genetic", "Genetic testing"
        IMAGING = "imaging", "Digital pathology / imaging"
        TRIAL = "trial", "Registry-embedded trial"

    class Status(models.TextChoices):
        GRANTED = "granted", "Granted"
        WITHDRAWN = "withdrawn", "Withdrawn"
        REFUSED = "refused", "Refused"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="consents")
    consent_type = models.CharField(max_length=12, choices=Type.choices)
    form_version = models.CharField(
        max_length=40, help_text='ICF version, e.g. "BGDDR-ICF-v2.1"')
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.GRANTED)

    consent_date = models.DateField()
    withdrawn_date = models.DateField(null=True, blank=True)
    obtained_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="consents_obtained")
    scope = models.TextField(blank=True, help_text="What the patient agreed to.")
    document = models.FileField(upload_to="consents/%Y/%m/", blank=True)
    notes = models.CharField(max_length=240, blank=True)

    # Version chain: a new consent of the same type supersedes the previous one.
    supersedes = models.OneToOneField(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="superseded_by")
    is_current = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient", "consent_type", "-consent_date"]
        indexes = [
            models.Index(fields=["patient", "consent_type", "is_current"]),
        ]
        constraints = [
            # At most one current consent per (patient, type).
            models.UniqueConstraint(
                fields=["patient", "consent_type"],
                condition=models.Q(is_current=True),
                name="uniq_current_consent_per_type"),
        ]

    def __str__(self):
        return (f"{self.patient.patient_id} {self.get_consent_type_display()} "
                f"{self.form_version} ({self.get_status_display()})")

    @property
    def is_active(self):
        return self.is_current and self.status == self.Status.GRANTED

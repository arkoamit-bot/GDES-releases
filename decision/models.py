from django.conf import settings
from django.db import models
from patients.models import Patient


class DecisionRequest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="decision_requests")
    encounter = models.ForeignKey("encounters.ClinicalEncounter", on_delete=models.CASCADE, related_name="decision_requests")
    input_snapshot = models.JSONField(help_text="Patient data at time of request")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"DecisionRequest {self.id} - {self.patient}"


class DecisionResult(models.Model):
    request = models.OneToOneField(DecisionRequest, on_delete=models.CASCADE, related_name="result")
    phenotype = models.CharField(max_length=200, blank=True)
    urgency_level = models.CharField(max_length=100, blank=True)
    urgency_tone = models.CharField(max_length=20, blank=True)
    urgency_reasons = models.JSONField(default=list, blank=True)
    ranked_differential = models.JSONField(default=list, blank=True)
    next_steps = models.JSONField(default=dict, blank=True)
    traceability = models.JSONField(default=list, blank=True, help_text="KB entries and rules applied")
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Override tracking (Phase 3.1)
    override_reason = models.TextField(blank=True, help_text="Reason for overriding the AI recommendation")
    alternative_diagnosis = models.CharField(max_length=200, blank=True, help_text="Clinician's alternative diagnosis")
    clinician_notes = models.TextField(blank=True, help_text="Free-text notes from the clinician")
    overridden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="overridden_decisions",
    )
    override_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"DecisionResult for request {self.request_id}"

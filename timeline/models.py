from django.db import models
from patients.models import Patient


class TimelineEvent(models.Model):
    class Domain(models.TextChoices):
        PATIENT = "patient", "Patient"
        ENCOUNTER = "encounter", "Encounter"
        CLINICAL = "clinical", "Clinical Assessment"
        LAB = "lab", "Laboratory"
        BIOPSY = "biopsy", "Biopsy"
        DECISION = "decision", "Decision Support"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="timeline_events")
    domain = models.CharField(max_length=20, choices=Domain.choices)
    event_type = models.CharField(max_length=100, db_index=True)
    event_date = models.DateTimeField(db_index=True)
    summary = models.CharField(max_length=500)
    details = models.JSONField(default=dict, blank=True)
    source_id = models.CharField(max_length=100, blank=True, help_text="ID of the source entity")
    source_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]
        indexes = [
            models.Index(fields=["patient", "domain"]),
            models.Index(fields=["patient", "-event_date"]),
        ]

    def __str__(self):
        return f"[{self.get_domain_display()}] {self.summary} ({self.event_date})"

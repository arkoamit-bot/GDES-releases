"""
Follow-up scheduling (protocol §7.6).

A prospective GN registry runs on a defined visit cadence delivered at the weekly
Tuesday GN clinic (max 15 participants/session), with each visit scheduled within
a ±7-day window of its protocol timepoint, and early safety visits (weeks 1, 2, 4)
for participants on active immunosuppression.

ScheduledVisit is one protocol-mandated slot per patient per timepoint. An
encounter (the actual visit) fulfils it. This is the operational layer that lets
the coordinator see who is due, who is overdue, and the roster for a given clinic
day — replacing the spreadsheet's Patient_Tracking / Followup_Schedule sheets.
"""
from django.db import models

from patients.models import Patient


class ScheduledVisit(models.Model):
    class Kind(models.TextChoices):
        ROUTINE = "routine", "Routine follow-up"
        EARLY_SAFETY = "early_safety", "Early safety visit"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        MISSED = "missed", "Missed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="scheduled_visits")
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.ROUTINE)
    label = models.CharField(max_length=20)          # "Month 3", "Week 1"
    target_date = models.DateField()                  # protocol timepoint
    window_start = models.DateField()
    window_end = models.DateField()
    clinic_date = models.DateField(null=True, blank=True)   # assigned Tuesday

    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.SCHEDULED)
    encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="fulfilled_visits")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "target_date"]
        indexes = [
            models.Index(fields=["status", "window_end"]),
            models.Index(fields=["clinic_date"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["patient", "label"],
                                    name="uniq_patient_visit_label"),
        ]

    def __str__(self):
        return f"{self.patient.patient_id} {self.label} @ {self.clinic_date or self.target_date} ({self.status})"

    def is_due(self, as_of):
        return (self.status == self.Status.SCHEDULED
                and self.window_start <= as_of <= self.window_end)

    def is_overdue(self, as_of):
        return self.status == self.Status.SCHEDULED and self.window_end < as_of

from django.conf import settings
from django.db import models
from django.utils import timezone

from patients.models import Patient


class TaskPriority(models.TextChoices):
    ROUTINE = "routine", "Routine"
    URGENT = "urgent", "Urgent"
    EMERGENT = "emergent", "Emergent"


class TaskType(models.TextChoices):
    VISIT_DUE = "visit_due", "Visit Due"
    LAB_DUE = "lab_due", "Laboratory Due"
    DRUG_MONITORING_DUE = "drug_monitoring_due", "Drug Monitoring Due"
    VACCINATION_DUE = "vaccination_due", "Vaccination Due"
    BIOPSY_REVIEW_DUE = "biopsy_review_due", "Biopsy Review Due"
    SAFETY_REVIEW_DUE = "safety_review_due", "Safety Review Due"
    RESEARCH_VISIT_DUE = "research_visit_due", "Research Visit Due"


class TaskStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    OVERDUE = "overdue", "Overdue"


class EscalationLevel(models.IntegerChoices):
    NONE = 0, "None"
    WARNING = 1, "Warning generated"
    CLINICIAN = 2, "Responsible clinician notified"
    COORDINATOR = 3, "Coordinator notified"
    DEPARTMENT = 4, "Department dashboard escalated"


class FollowUpTask(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="followup_tasks")
    task_type = models.CharField(max_length=25, choices=TaskType.choices)
    priority = models.CharField(
        max_length=10, choices=TaskPriority.choices, default=TaskPriority.ROUTINE)

    reason = models.TextField(blank=True)
    clinical_reason = models.TextField(
        blank=True, help_text="Why this task is needed")
    due_date = models.DateField()
    overdue_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="followup_tasks")
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="completed_followup_tasks")

    escalation_level = models.IntegerField(
        choices=EscalationLevel.choices, default=EscalationLevel.NONE)
    escalated_at = models.DateTimeField(null=True, blank=True)

    protocol_label = models.CharField(
        max_length=40, blank=True,
        help_text="e.g. IgAN Month 3, MCD Week 1 safety")
    related_encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "priority"]
        indexes = [
            models.Index(fields=["patient", "status", "due_date"]),
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return f"{self.get_task_type_display()} — {self.patient.patient_id} due {self.due_date}"

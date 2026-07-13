from django.conf import settings
from django.db import models

from patients.models import Patient


class ReminderType(models.TextChoices):
    FOLLOW_UP = "follow_up", "Follow-up visit reminder"
    LAB_TEST = "lab_test", "Lab test reminder"
    MEDICATION = "medication", "Medication adherence reminder"
    MONITORING = "monitoring", "Monitoring parameter reminder"
    GENERAL = "general", "General notification"


class ReminderChannel(models.TextChoices):
    SMS = "sms", "SMS"
    WHATSAPP = "whatsapp", "WhatsApp"
    EMAIL = "email", "Email"
    APP = "app", "In-app notification"


class ReminderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class ReminderSchedule(models.Model):
    """Scheduled reminder for a patient."""
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="reminders"
    )
    reminder_type = models.CharField(
        max_length=20, choices=ReminderType.choices
    )
    channel = models.CharField(
        max_length=10, choices=ReminderChannel.choices, default=ReminderChannel.SMS
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=ReminderStatus.choices, default=ReminderStatus.PENDING
    )

    # Optional reference to a scheduled visit
    scheduled_visit = models.ForeignKey(
        "scheduling.ScheduledVisit", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reminders",
    )

    error_message = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["patient", "status"]),
        ]

    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.patient.patient_id} @ {self.scheduled_at}"


class ReminderTemplate(models.Model):
    """Reusable message templates for reminders."""
    reminder_type = models.CharField(
        max_length=20, choices=ReminderType.choices
    )
    channel = models.CharField(
        max_length=10, choices=ReminderChannel.choices
    )
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200, blank=True)
    template_body = models.TextField(
        help_text="Template with placeholders like {{patient_name}}, {{visit_date}}, {{clinic_address}}"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("reminder_type", "channel", "name")]

    def __str__(self):
        return f"{self.name} ({self.get_reminder_type_display()} via {self.get_channel_display()})"


class PatientCommunicationPreference(models.Model):
    """Per-patient communication channel preferences."""
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="comm_preferences"
    )
    preferred_channel = models.CharField(
        max_length=10, choices=ReminderChannel.choices, default=ReminderChannel.SMS
    )
    phone = models.CharField(max_length=20, blank=True,
                             help_text="Override phone for SMS/WhatsApp")
    email = models.EmailField(max_length=200, blank=True,
                              help_text="Override email address")
    reminder_follow_up = models.BooleanField(default=True)
    reminder_lab = models.BooleanField(default=True)
    reminder_medication = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comm prefs for {self.patient.patient_id}: {self.get_preferred_channel_display()}"

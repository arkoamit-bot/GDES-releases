from django.contrib import admin

from .models import ReminderSchedule, ReminderTemplate, PatientCommunicationPreference


@admin.register(ReminderSchedule)
class ReminderScheduleAdmin(admin.ModelAdmin):
    list_display = ("patient", "reminder_type", "channel", "status",
                    "scheduled_at", "sent_at", "retry_count")
    list_filter = ("status", "reminder_type", "channel")
    search_fields = ("patient__patient_id", "patient__name")
    date_hierarchy = "scheduled_at"


@admin.register(ReminderTemplate)
class ReminderTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "reminder_type", "channel", "is_active")
    list_filter = ("reminder_type", "channel", "is_active")


@admin.register(PatientCommunicationPreference)
class PatientCommunicationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("patient", "preferred_channel", "phone", "email")
    search_fields = ("patient__patient_id", "patient__name")

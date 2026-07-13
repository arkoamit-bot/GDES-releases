from django.contrib import admin

from .models import FollowUpTask


@admin.register(FollowUpTask)
class FollowUpTaskAdmin(admin.ModelAdmin):
    list_display = ["patient", "task_type", "priority", "due_date", "status", "escalation_level"]
    list_filter = ["task_type", "priority", "status", "escalation_level"]
    search_fields = ["patient__patient_id", "patient__name", "reason"]
    date_hierarchy = "due_date"

from django.contrib import admin

from .models import ScheduledVisit


@admin.register(ScheduledVisit)
class ScheduledVisitAdmin(admin.ModelAdmin):
    list_display = ("patient", "label", "kind", "target_date", "clinic_date",
                    "window_start", "window_end", "status")
    list_filter = ("status", "kind", "clinic_date")
    search_fields = ("patient__patient_id", "patient__name", "label")
    date_hierarchy = "clinic_date"
    autocomplete_fields = ("patient", "encounter")

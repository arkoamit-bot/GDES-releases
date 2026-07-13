from django.contrib import admin

from .models import AdverseEvent


@admin.register(AdverseEvent)
class AdverseEventAdmin(admin.ModelAdmin):
    list_display = ("patient", "onset_date", "category", "infection_type",
                    "severity", "serious", "hospitalization", "suspected_drug",
                    "outcome")
    list_filter = ("category", "severity", "serious", "hospitalization",
                   "infection_type", "relatedness")
    search_fields = ("patient__patient_id", "patient__name", "description")
    date_hierarchy = "onset_date"
    autocomplete_fields = ("patient", "suspected_drug", "encounter")

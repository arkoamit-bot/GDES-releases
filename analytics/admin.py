from django.contrib import admin

from .models import PatientOutcome


@admin.register(PatientOutcome)
class PatientOutcomeAdmin(admin.ModelAdmin):
    list_display = ("patient", "index_date", "followup_days", "baseline_egfr",
                    "latest_egfr", "egfr_slope", "composite_kidney_event",
                    "eskd", "death", "remission_status", "computed_at")
    list_filter = ("composite_kidney_event", "eskd", "death",
                   "remission_status", "sustained_40_decline")
    search_fields = ("patient__patient_id", "patient__name")
    date_hierarchy = "index_date"
    # Entirely engine-computed — read-only in the admin.
    readonly_fields = [f.name for f in PatientOutcome._meta.fields]

    def has_add_permission(self, request):
        return False

from django.contrib import admin

from .models import BiomarkerKinetics


@admin.register(BiomarkerKinetics)
class BiomarkerKineticsAdmin(admin.ModelAdmin):
    list_display = ("patient", "pla2r_baseline", "pla2r_nadir", "pla2r_pct_decline",
                    "pla2r_50pct_decline", "pla2r_immunological_remission",
                    "c3_recovered", "computed_at")
    list_filter = ("pla2r_50pct_decline", "pla2r_immunological_remission",
                   "c3_recovered", "dsdna_normalized")
    search_fields = ("patient__patient_id", "patient__name")
    readonly_fields = [f.name for f in BiomarkerKinetics._meta.fields]

    def has_add_permission(self, request):
        return False

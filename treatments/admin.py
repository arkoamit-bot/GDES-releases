from django.contrib import admin

from .models import DrugMaster, TreatmentExposure


@admin.register(DrugMaster)
class DrugMasterAdmin(admin.ModelAdmin):
    list_display = ("generic_name", "drug_class", "default_frequency",
                    "renal_dose_adjust", "egfr_caution_below", "is_active")
    list_filter = ("drug_class", "renal_dose_adjust", "is_active")
    search_fields = ("generic_name",)


@admin.register(TreatmentExposure)
class TreatmentExposureAdmin(admin.ModelAdmin):
    list_display = ("patient", "drug_name", "dose", "start_date",
                    "stop_date", "ongoing", "stop_reason")
    list_filter = ("ongoing", "drug__drug_class", "stop_reason")
    search_fields = ("patient__patient_id", "drug_name")
    date_hierarchy = "start_date"
    # Research table — written by the reconciliation engine, so make it
    # read-mostly in the admin to discourage hand-editing.
    readonly_fields = ("opened_by_encounter", "closed_by_encounter", "created_at")

from django.contrib import admin

from .models import DrugMaster, DrugSyncRun, TreatmentExposure


@admin.register(DrugMaster)
class DrugMasterAdmin(admin.ModelAdmin):
    list_display = ("generic_name", "drug_class", "default_frequency",
                    "renal_dose_adjust", "egfr_caution_below", "is_active")
    list_filter = ("drug_class", "renal_dose_adjust", "is_active")
    search_fields = ("generic_name",)


@admin.register(DrugSyncRun)
class DrugSyncRunAdmin(admin.ModelAdmin):
    """Read-only audit trail for the automated MedEx refresh.

    Clinicians need to be able to answer "when was the brand list last
    verified?" - a stale catalogue is a clinical-safety issue, because it
    drives what a prescriber can actually offer. Nothing here is editable:
    the rows are written by the sync engine.
    """
    list_display = ("started_at", "state", "trigger", "rows_scraped",
                    "brands_added", "generics_created", "rows_deleted",
                    "duration_seconds")
    list_filter = ("state", "trigger")
    search_fields = ("error",)
    date_hierarchy = "started_at"
    readonly_fields = [f.name for f in DrugSyncRun._meta.fields]


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

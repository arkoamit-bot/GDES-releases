from django.contrib import admin

from .models import ClinicalEncounter, ClinicalEvent


@admin.register(ClinicalEvent)
class ClinicalEventAdmin(admin.ModelAdmin):
    list_display = ("patient", "event_type", "event_date", "encounter")
    list_filter = ("event_type",)
    # Search by patient (ID/name), the event-type code (e.g. "dialysis",
    # "remission", "relapse"), or anything typed in the notes.
    search_fields = ("patient__patient_id", "patient__name", "event_type", "notes")
    search_help_text = "Search by patient ID/name, event type (e.g. dialysis, remission, relapse), or notes."
    date_hierarchy = "event_date"
    autocomplete_fields = ("patient", "encounter")


@admin.register(ClinicalEncounter)
class ClinicalEncounterAdmin(admin.ModelAdmin):
    list_display = ("patient", "encounter_date", "encounter_type",
                    "clinic_location", "next_due_date")
    list_filter = ("encounter_type", "clinic_location")
    search_fields = ("patient__patient_id", "patient__name",
                     "clinic_location", "advice")
    search_help_text = "Search by patient ID/name, clinic location, or advice text."
    date_hierarchy = "encounter_date"
    autocomplete_fields = ("patient", "seen_by")
    readonly_fields = ("created_at",)
    # Group the visit form so the clinician fills it top-to-bottom: who/when,
    # then the vitals measured, then the plan. (Rendered as tabs by Jazzmin.)
    fieldsets = (
        ("Visit", {
            "fields": ("patient", "encounter_date", "encounter_type",
                       "seen_by", "clinic_location"),
            "description": "One encounter per visit — the hub the prescription, "
                           "labs and outcomes hang off."}),
        ("Vitals", {
            "fields": (("systolic_bp", "diastolic_bp"), "weight_kg"),
            "description": "Blood pressure in mmHg; weight in kg. Leave blank if "
                           "not measured."}),
        ("Plan", {
            "fields": ("advice", "next_due_date"),
            "description": "Advice prints on the prescription (Bangla supported). "
                           "Next-visit date drives the follow-up worklist."}),
        ("Audit", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

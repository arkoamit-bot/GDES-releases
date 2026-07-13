from django.contrib import admin, messages

from .models import Patient
from .services import delete_patient_cascade


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "name", "sex", "diabetes_status",
                    "primary_diagnosis", "latest_egfr")
    search_fields = ("patient_id", "name", "hospital_id", "phone")
    list_filter = ("sex", "diabetes_status", "cohort")
    actions = ["delete_patient_and_all_data"]

    @admin.action(description="Delete patient + ALL their data (encounters, "
                             "prescriptions, labs, biopsies…)")
    def delete_patient_and_all_data(self, request, queryset):
        """Cascade-delete: the normal admin delete is blocked because encounters
        are PROTECTed. Superuser only — this is irreversible."""
        if not request.user.is_superuser:
            self.message_user(request, "Only a superuser can delete patients.",
                              level=messages.ERROR)
            return
        done = [delete_patient_cascade(p) for p in queryset]
        self.message_user(
            request, f"Deleted {len(done)} patient(s) and all their data: "
            + ", ".join(done), level=messages.WARNING)
    # Study ID is auto-generated on save; never typed by hand.
    readonly_fields = ("patient_id", "latest_egfr", "created_at", "updated_at")
    fieldsets = (
        ("Identification", {
            "fields": ("patient_id", "name", "hospital_id", "phone"),
            "description": "Study ID is assigned automatically (BGD-00001…) when you save."}),
        ("Demographics & enrolment", {
            "fields": ("sex", "dob", "enrollment_date", "cohort")}),
        ("Clinical", {
            "fields": ("diabetes_status", "primary_diagnosis", "latest_egfr")}),
        ("Audit", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

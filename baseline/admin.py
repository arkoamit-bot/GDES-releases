from django.contrib import admin

from .models import BaselineAssessment


@admin.register(BaselineAssessment)
class BaselineAssessmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "assessment_date", "bmi", "bmi_category",
                    "systolic_bp", "hba1c", "presentation_syndrome")
    list_filter = ("presentation_syndrome", "bmi_category", "hypertension",
                   "diabetic_retinopathy")
    search_fields = ("patient__patient_id", "patient__name")
    autocomplete_fields = ("patient",)
    readonly_fields = ("bmi", "bmi_category", "created_at", "updated_at")

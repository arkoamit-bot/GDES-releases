from django.contrib import admin
from .models import ClinicalAssessment, VitalSign


@admin.register(ClinicalAssessment)
class ClinicalAssessmentAdmin(admin.ModelAdmin):
    list_display = ["encounter", "chief_complaint", "time_course", "syndrome_classification"]


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ["encounter", "bp_systolic", "bp_diastolic", "weight_kg"]

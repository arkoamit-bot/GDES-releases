from django.contrib import admin

from .models import Study, StudyArm, StudyEnrollment


class StudyArmInline(admin.TabularInline):
    model = StudyArm
    extra = 2
    fields = ("order", "code", "name", "ratio", "is_control")


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "study_type", "status",
                    "randomization_scheme", "target_enrollment")
    list_filter = ("study_type", "status", "randomization_scheme")
    search_fields = ("code", "title")
    inlines = [StudyArmInline]


@admin.register(StudyEnrollment)
class StudyEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("study", "patient", "status", "eligible", "arm",
                    "stratum", "enrolled_date", "randomized_by")
    list_filter = ("study", "status", "eligible", "arm")
    search_fields = ("patient__patient_id", "patient__name")
    autocomplete_fields = ("study", "patient")
    # Allocation is made by the randomization engine — never hand-edited here.
    readonly_fields = ("arm", "stratum", "sequence_position", "randomized_by",
                       "randomized_at", "eligible", "ineligibility_reasons")

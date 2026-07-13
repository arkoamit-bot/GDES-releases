from django.contrib import admin

from .models import (Biopsy, BiopsyImage, FSGSPathology, GNDiagnosis, IgANScore,
                     LupusPathology, MembranousPathology, PathologyReview)


class PathologyReviewInline(admin.TabularInline):
    model = PathologyReview
    extra = 0
    fields = ("role", "reviewer", "review_date", "diagnosis", "broad_group",
              "mest_m", "mest_e", "mest_s", "mest_t", "mest_c", "is_final")
    readonly_fields = ("is_final",)


@admin.register(PathologyReview)
class PathologyReviewAdmin(admin.ModelAdmin):
    list_display = ("biopsy", "role", "diagnosis", "broad_group", "reviewer",
                    "review_date", "is_final")
    list_filter = ("role", "is_final", "broad_group")
    search_fields = ("biopsy__patient__patient_id", "diagnosis")


class GNDiagnosisInline(admin.StackedInline):
    model = GNDiagnosis
    extra = 0


class IgANScoreInline(admin.StackedInline):
    model = IgANScore
    extra = 0


class LupusInline(admin.StackedInline):
    model = LupusPathology
    extra = 0


class FSGSInline(admin.StackedInline):
    model = FSGSPathology
    extra = 0


class MembranousInline(admin.StackedInline):
    model = MembranousPathology
    extra = 0


class BiopsyImageInline(admin.TabularInline):
    model = BiopsyImage
    extra = 0
    fields = ("image", "stain", "description")


@admin.register(Biopsy)
class BiopsyAdmin(admin.ModelAdmin):
    list_display = ("patient", "biopsy_date", "adequacy", "review_status",
                    "total_glomeruli", "global_sclerosis_pct", "crescents_present")
    list_filter = ("review_status", "adequacy", "arteriosclerosis",
                   "dkd_lesion_present", "crescents_present")
    search_fields = ("patient__patient_id", "patient__name")
    autocomplete_fields = ("patient",)
    date_hierarchy = "biopsy_date"
    readonly_fields = ("review_status",)
    inlines = [PathologyReviewInline, GNDiagnosisInline, IgANScoreInline,
               LupusInline, FSGSInline, MembranousInline, BiopsyImageInline]


@admin.register(GNDiagnosis)
class GNDiagnosisAdmin(admin.ModelAdmin):
    list_display = ("biopsy", "diagnosis", "broad_group", "primary_secondary")
    list_filter = ("broad_group", "primary_secondary")
    search_fields = ("biopsy__patient__patient_id", "diagnosis")

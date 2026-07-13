from django.contrib import admin
from django.utils.html import format_html

from .models import AdviceTemplate, Prescription, PrescriptionItem


@admin.register(AdviceTemplate)
class AdviceTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "body")


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    autocomplete_fields = ("drug",)
    fields = ("sort_order", "drug", "brand", "strength", "dose",
              "frequency", "timing", "duration", "instruction_bn")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "status", "encounter", "reconciled_at",
                    "printed_at", "links")
    list_filter = ("status",)
    search_fields = ("encounter__patient__patient_id", "encounter__patient__name")
    autocomplete_fields = ("encounter",)
    inlines = [PrescriptionItemInline]
    readonly_fields = ("content_hash", "reconciled_at", "printed_at",
                       "printed_by", "links")

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_final:
            # Immutable once printed — lock the clinical content.
            ro += ["encounter", "version", "status", "diagnosis_text",
                   "investigations_advised"]
        return ro

    def links(self, obj):
        if not obj.pk:
            return ""
        return format_html(
            '<a href="/prescriptions/{}/preview/" target="_blank">preview</a> · '
            '<a href="/prescriptions/{}/reconcile/preview/" target="_blank">recon</a> · '
            '<a href="/prescriptions/{}/pdf/" target="_blank">pdf</a>',
            obj.pk, obj.pk, obj.pk)
    links.short_description = "actions"

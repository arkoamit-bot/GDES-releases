from django.contrib import admin

from .models import (LabOrder, LabOrderItem, LabPanel, LabResult, LabTest)


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "default_unit", "value_type",
                    "ref_low", "ref_high", "is_derived", "is_active")
    list_filter = ("value_type", "is_derived", "is_active")
    search_fields = ("code", "name", "loinc")


@admin.register(LabPanel)
class LabPanelAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    filter_horizontal = ("tests",)
    search_fields = ("code", "name")


class LabOrderItemInline(admin.TabularInline):
    model = LabOrderItem
    extra = 1
    autocomplete_fields = ("test",)


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ("patient", "ordered_date", "status", "encounter")
    list_filter = ("status",)
    search_fields = ("patient__patient_id", "patient__name")
    date_hierarchy = "ordered_date"
    autocomplete_fields = ("encounter", "patient")
    inlines = [LabOrderItemInline]


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ("patient", "test", "value_numeric", "value_text", "unit",
                    "flag", "result_date", "source", "formula_version")
    list_filter = ("source", "flag", "test__code")
    search_fields = ("patient__patient_id", "patient__name", "test__code")
    date_hierarchy = "result_date"
    autocomplete_fields = ("patient", "test", "derived_from")
    raw_id_fields = ("order_item",)
    readonly_fields = ("created_at",)

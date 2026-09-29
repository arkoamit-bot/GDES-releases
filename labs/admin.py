from django import forms
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


class LabResultAdminForm(forms.ModelForm):
    correction_reason = forms.CharField(
        required=False, max_length=240,
        help_text="Required when changing an existing result: the change is "
                  "saved as a correction that supersedes it.")

    class Meta:
        model = LabResult
        fields = ["patient", "test", "value_numeric", "value_text", "unit",
                  "sample_date", "result_date", "source", "order_item",
                  "source_report_id", "specimen_id", "correction_reason"]

    def clean(self):
        cleaned = super().clean()
        if self.instance.pk and not (cleaned.get("correction_reason") or "").strip():
            self.add_error("correction_reason",
                           "State why the result is corrected.")
        from django.core.exceptions import ValidationError
        from labs.services.results import normalize, validate
        test = cleaned.get("test")
        if test is not None:
            value, _unit = normalize(test, cleaned.get("value_numeric"), cleaned.get("unit", ""))
            try:
                validate(test, value, cleaned.get("value_text", ""),
                         cleaned.get("result_date"), cleaned.get("sample_date"))
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        return cleaned


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    """Admin entry uses the same recording/correction service as every other
    path: a new creatinine derives eGFR; a change supersedes the original."""
    form = LabResultAdminForm
    list_display = ("patient", "test", "value_numeric", "value_text", "unit",
                    "flag", "result_date", "source", "is_current", "formula_version")
    list_filter = ("is_current", "source", "flag", "test__code")
    search_fields = ("patient__patient_id", "patient__name", "test__code")
    date_hierarchy = "result_date"
    autocomplete_fields = ("patient", "test")
    raw_id_fields = ("order_item",)
    readonly_fields = ("created_at", "derived_from", "formula_version",
                       "supersedes", "is_current", "correction_reason_display",
                       "entry_path", "entered_by")

    def get_queryset(self, request):
        return LabResult.all_objects.select_related("patient", "test")

    @admin.display(description="Correction reason")
    def correction_reason_display(self, obj):
        return obj.correction_reason

    def has_change_permission(self, request, obj=None):
        if obj is not None and (not obj.is_current
                                or obj.source == LabResult.Source.DERIVED):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False   # measured history is corrected, never deleted

    def save_model(self, request, obj, form, change):
        from labs.services.results import correct_result, record_result
        cd = form.cleaned_data
        user = request.user if request.user.is_authenticated else None
        if change:
            original = LabResult.all_objects.get(pk=obj.pk)
            new = correct_result(
                original, reason=cd.get("correction_reason", ""),
                value_numeric=cd.get("value_numeric"), value_text=cd.get("value_text"),
                unit=cd.get("unit"), result_date=cd.get("result_date"),
                sample_date=cd.get("sample_date"), entered_by=user,
                entry_path=LabResult.EntryPath.ADMIN)
        else:
            new = record_result(
                cd["patient"], cd["test"], result_date=cd["result_date"],
                value_numeric=cd.get("value_numeric"), value_text=cd.get("value_text", ""),
                unit=cd.get("unit", ""), sample_date=cd.get("sample_date"),
                order_item=cd.get("order_item"),
                source=cd.get("source") or LabResult.Source.LAB,
                entry_path=LabResult.EntryPath.ADMIN, entered_by=user,
                source_report_id=cd.get("source_report_id", ""),
                specimen_id=cd.get("specimen_id", ""))
        obj.pk = obj.id = new.pk

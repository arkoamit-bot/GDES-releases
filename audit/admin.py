from django.contrib import admin

from .models import AuditLog, Consent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("changed_at", "action", "model_label", "object_pk",
                    "field_name", "old_value", "new_value", "changed_by")
    list_filter = ("action", "model_label", "changed_by")
    search_fields = ("model_label", "object_pk", "object_repr", "field_name")
    date_hierarchy = "changed_at"
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False   # append-only

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("patient", "consent_type", "form_version", "status",
                    "consent_date", "withdrawn_date", "is_current")
    list_filter = ("consent_type", "status", "is_current")
    search_fields = ("patient__patient_id", "patient__name", "form_version")
    date_hierarchy = "consent_date"
    autocomplete_fields = ("patient",)
    readonly_fields = ("supersedes", "is_current", "created_at", "updated_at")

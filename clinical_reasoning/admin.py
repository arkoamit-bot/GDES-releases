from django.contrib import admin
from .models import ClinicalProfile, ClinicalInsight


@admin.register(ClinicalProfile)
class ClinicalProfileAdmin(admin.ModelAdmin):
    list_display = ["patient", "version", "last_updated"]
    search_fields = ["patient__patient_id", "patient__name"]
    date_hierarchy = "last_updated"


@admin.register(ClinicalInsight)
class ClinicalInsightAdmin(admin.ModelAdmin):
    list_display = ["patient", "category", "priority", "title", "dismissed", "created_at"]
    list_filter = ["category", "priority", "dismissed"]
    search_fields = ["patient__patient_id", "title"]
    date_hierarchy = "created_at"
    actions = ["dismiss_selected"]

    @admin.action(description="Dismiss selected insights")
    def dismiss_selected(self, request, queryset):
        updated = queryset.update(dismissed=True)
        self.message_user(request, f"Dismissed {updated} insights.")

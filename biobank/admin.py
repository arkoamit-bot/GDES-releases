from django.contrib import admin

from .models import Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("patient", "sample_type", "collection_date", "aliquots",
                    "volume_ml", "storage_location", "status")
    list_filter = ("sample_type", "status")
    search_fields = ("patient__patient_id", "patient__name", "storage_location")
    autocomplete_fields = ("patient",)
    date_hierarchy = "collection_date"

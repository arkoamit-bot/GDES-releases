from django.contrib import admin
from .models import TimelineEvent


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ["patient", "domain", "event_type", "event_date", "summary"]
    list_filter = ["domain", "event_type"]
    search_fields = ["patient__mrn", "summary"]

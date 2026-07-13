from django.contrib import admin
from .models import Event, EventSubscription


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "source_model", "source_pk", "occurred_at", "processed"]
    list_filter = ["event_type", "processed", "occurred_at"]
    search_fields = ["source_pk", "payload"]
    date_hierarchy = "occurred_at"


@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["event_type", "handler_path", "active", "created_at"]
    list_filter = ["event_type", "active"]
    search_fields = ["handler_path"]

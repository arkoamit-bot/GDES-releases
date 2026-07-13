"""Event orchestration models — persisted event log and subscriptions."""
from django.conf import settings
from django.db import models

from .event_types import ALL_EVENTS


class Event(models.Model):
    event_type = models.CharField(max_length=100, db_index=True)
    source_model = models.CharField(max_length=100, blank=True)
    source_pk = models.CharField(max_length=50, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["event_type", "occurred_at"]),
            models.Index(fields=["processed", "event_type"]),
        ]

    def __str__(self):
        return f"{self.event_type} @ {self.occurred_at.isoformat()}"


class EventSubscription(models.Model):
    event_type = models.CharField(max_length=100, db_index=True)
    handler_path = models.CharField(max_length=300, help_text="Dotted path to handler function")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("event_type", "handler_path")]

    def __str__(self):
        return f"{self.event_type} → {self.handler_path}"

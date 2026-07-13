from rest_framework import serializers
from .models import TimelineEvent


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ["id", "patient", "domain", "event_type", "event_date", "summary", "details", "source_id", "created_at"]

from rest_framework import serializers

from .models import (
    ReminderSchedule, ReminderTemplate,
    PatientCommunicationPreference, ReminderType, ReminderChannel,
)


class ReminderScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderSchedule
        fields = [
            "id", "patient", "reminder_type", "channel",
            "title", "message", "scheduled_at", "sent_at",
            "status", "scheduled_visit", "error_message",
            "retry_count", "created_at",
        ]
        read_only_fields = ["sent_at", "status", "error_message",
                            "retry_count", "created_at"]


class ReminderTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderTemplate
        fields = "__all__"


class PatientCommunicationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientCommunicationPreference
        fields = "__all__"


class SendCustomReminderSerializer(serializers.Serializer):
    patient_id = serializers.CharField(max_length=20)
    reminder_type = serializers.ChoiceField(choices=ReminderType.choices)
    channel = serializers.ChoiceField(choices=ReminderChannel.choices,
                                       default=ReminderChannel.SMS)
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    scheduled_at = serializers.DateTimeField()


class ScheduleVisitRemindersSerializer(serializers.Serializer):
    days_ahead = serializers.IntegerField(default=7, min_value=1, max_value=90)

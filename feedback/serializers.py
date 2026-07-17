from rest_framework import serializers
from .models import (
    ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict,
    AIFailureLog, RuleFailureLog, UserFeedback, WorkflowFeedback,
    PerformanceLog, KnowledgeImprovementSuggestion,
)


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = "__all__"


class CrashReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrashReport
        fields = "__all__"


class ClinicalConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalConflict
        fields = "__all__"
        read_only_fields = ("timestamp",)


class KnowledgeConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeConflict
        fields = "__all__"
        read_only_fields = ("timestamp",)


class AIFailureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFailureLog
        fields = "__all__"


class RuleFailureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleFailureLog
        fields = "__all__"


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = "__all__"
        read_only_fields = ("created_at", "resolved")


class WorkflowFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowFeedback
        fields = "__all__"
        read_only_fields = ("created_at",)


class PerformanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceLog
        fields = "__all__"


class KnowledgeImprovementSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeImprovementSuggestion
        fields = "__all__"
        read_only_fields = ("created_at",)

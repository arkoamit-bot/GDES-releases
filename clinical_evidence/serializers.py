from rest_framework import serializers

from .models import (
    EvidenceAlert,
    EvidenceCache,
    EvidenceConflict,
    EvidencePackage,
    EvidenceQuery,
    EvidenceResult,
    EvidenceSummary,
    GuidelineRecommendation,
    KnowledgeGap,
    ProviderConfiguration,
    ProviderHealth,
    RecommendationValidation,
)


class ProviderConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderConfiguration
        fields = [
            "id", "provider_type", "is_enabled", "priority",
            "api_base_url", "max_retries", "timeout_seconds",
            "rate_limit_max", "rate_limit_window_seconds",
            "extra_config", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {"api_key_encrypted": {"write_only": True}}


class ProviderHealthSerializer(serializers.ModelSerializer):
    provider_type = serializers.CharField(source="provider.provider_type", read_only=True)

    class Meta:
        model = ProviderHealth
        fields = "__all__"


class EvidenceQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceQuery
        fields = "__all__"
        read_only_fields = ["query_id", "created_at", "updated_at"]


class EvidenceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceResult
        fields = "__all__"


class EvidencePackageSerializer(serializers.ModelSerializer):
    supporting_results = EvidenceResultSerializer(many=True, read_only=True)
    contradictory_results = EvidenceResultSerializer(many=True, read_only=True)

    class Meta:
        model = EvidencePackage
        fields = "__all__"
        read_only_fields = ["package_id", "created_at", "updated_at"]


class GuidelineRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidelineRecommendation
        fields = "__all__"


class RecommendationValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationValidation
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class EvidenceConflictSerializer(serializers.ModelSerializer):
    supporting_results = EvidenceResultSerializer(many=True, read_only=True)
    contradictory_results = EvidenceResultSerializer(many=True, read_only=True)

    class Meta:
        model = EvidenceConflict
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class EvidenceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceAlert
        fields = "__all__"
        read_only_fields = ["alert_id", "created_at"]


class EvidenceCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceCache
        fields = "__all__"


class EvidenceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceSummary
        fields = "__all__"
        read_only_fields = ["summary_id", "created_at", "updated_at"]


class KnowledgeGapSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeGap
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

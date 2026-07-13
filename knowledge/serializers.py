"""DRF serializers for the knowledge app."""
from rest_framework import serializers

from .models import (
    GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion,
    RuleTemplate, RuleReview, RuleTestResult, GuidelineDocument, EvidenceEntry,
    Disease, ClinicalCase, ClinicalPathway,
    Syndrome, PathologyEntity, LabEntity, DrugIntelligence,
    MonitoringProtocol, Complication,
    KnowledgeGraphNode, KnowledgeGraphEdge,
)


class GuidelineSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidelineSource
        fields = "__all__"


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    source_title = serializers.CharField(source="source.title", read_only=True)
    source_abbreviation = serializers.CharField(
        source="source.abbreviation", read_only=True
    )
    version_count = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeBaseEntry
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_version_count(self, obj):
        return obj.versions.count() if hasattr(obj, "versions") else 0


class KnowledgeBaseVersionSerializer(serializers.ModelSerializer):
    entry_id_display = serializers.CharField(source="entry.entry_id", read_only=True)
    changed_by_username = serializers.CharField(source="changed_by.username", read_only=True, default="")

    class Meta:
        model = KnowledgeBaseVersion
        fields = [
            "id", "entry", "entry_id_display", "version_number", "rule_data",
            "rule_data_diff", "evidence_grade", "guideline_chapter", "guideline_paragraph",
            "guideline_quote", "change_summary", "changed_by", "changed_by_username",
            "created_at",
        ]


class RuleTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleTemplate
        fields = "__all__"


class RuleReviewSerializer(serializers.ModelSerializer):
    entry_id_display = serializers.CharField(source="entry.entry_id", read_only=True)
    reviewer_username = serializers.CharField(source="reviewer.username", read_only=True, default="")

    class Meta:
        model = RuleReview
        fields = "__all__"
        read_only_fields = ["created_at"]


class RuleTestResultSerializer(serializers.ModelSerializer):
    entry_id_display = serializers.CharField(source="entry.entry_id", read_only=True)
    patient_id_display = serializers.CharField(source="patient.patient_id", read_only=True, default="")

    class Meta:
        model = RuleTestResult
        fields = "__all__"
        read_only_fields = ["created_at"]


class GuidelineDocumentSerializer(serializers.ModelSerializer):
    source_abbreviation = serializers.CharField(source="source.abbreviation", read_only=True)

    class Meta:
        model = GuidelineDocument
        fields = "__all__"
        read_only_fields = ["imported_at"]


class EvidenceEntrySerializer(serializers.ModelSerializer):
    entry_id_display = serializers.CharField(source="entry.entry_id", read_only=True)

    class Meta:
        model = EvidenceEntry
        fields = "__all__"
        read_only_fields = ["created_at"]


class RuleEvaluationRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    disease_id = serializers.CharField(
        required=False,
        help_text="Evaluate only rules for this disease (optional, evaluates all if blank)",
    )


class RuleResultSerializer(serializers.Serializer):
    entry_id = serializers.CharField()
    disease_id = serializers.CharField()
    disease_name = serializers.CharField()
    score = serializers.FloatField()
    matched_rules = serializers.ListField(child=serializers.DictField())
    evidence_grade = serializers.CharField()
    source = serializers.CharField()


class ValidationRequestSerializer(serializers.Serializer):
    rule_data = serializers.JSONField()
    entry_id = serializers.CharField(required=False, default="")


class ValidationResultSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())


class TestRuleRequestSerializer(serializers.Serializer):
    entry_id = serializers.CharField(help_text="KnowledgeBaseEntry entry_id or PK")
    features = serializers.JSONField(required=False, default=dict)
    expected_score = serializers.FloatField(required=False, allow_null=True)


class BulkTestRequestSerializer(serializers.Serializer):
    disease_id = serializers.CharField()
    test_cases = serializers.ListField(child=serializers.JSONField())


class ImportGuidelineRequestSerializer(serializers.Serializer):
    source_abbreviation = serializers.CharField(required=False, default="")
    source_year = serializers.IntegerField(required=False, default=0)
    source_title = serializers.CharField(required=False, default="")
    content = serializers.CharField()
    format = serializers.ChoiceField(choices=["json", "yaml", "csv", "markdown"], default="json")


class RollbackRequestSerializer(serializers.Serializer):
    version_id = serializers.IntegerField()


# ─── V4.0 Disease / Cases / Pathways ────────────────────────────────────


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ClinicalCaseSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source="disease.name", read_only=True)

    class Meta:
        model = ClinicalCase
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ClinicalPathwaySerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source="disease.name", read_only=True)

    class Meta:
        model = ClinicalPathway
        fields = "__all__"


# ─── V4.2 Reusable Knowledge Object Serializers ──────────────────────────


class SyndromeSerializer(serializers.ModelSerializer):
    associated_disease_ids = serializers.SerializerMethodField()

    class Meta:
        model = Syndrome
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_associated_disease_ids(self, obj):
        return list(obj.associated_diseases.values_list("id", flat=True))


class PathologyEntitySerializer(serializers.ModelSerializer):
    associated_disease_ids = serializers.SerializerMethodField()

    class Meta:
        model = PathologyEntity
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_associated_disease_ids(self, obj):
        return list(obj.associated_diseases.values_list("id", flat=True))


class LabEntitySerializer(serializers.ModelSerializer):
    associated_disease_ids = serializers.SerializerMethodField()

    class Meta:
        model = LabEntity
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_associated_disease_ids(self, obj):
        return list(obj.associated_diseases.values_list("id", flat=True))


class DrugIntelligenceSerializer(serializers.ModelSerializer):
    indication_ids = serializers.SerializerMethodField()

    class Meta:
        model = DrugIntelligence
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_indication_ids(self, obj):
        return list(obj.indications.values_list("id", flat=True))


class MonitoringProtocolSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(source="drug.name", read_only=True, default="")
    associated_disease_ids = serializers.SerializerMethodField()

    class Meta:
        model = MonitoringProtocol
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_associated_disease_ids(self, obj):
        return list(obj.associated_diseases.values_list("id", flat=True))


class ComplicationSerializer(serializers.ModelSerializer):
    associated_disease_ids = serializers.SerializerMethodField()
    associated_drug_ids = serializers.SerializerMethodField()

    class Meta:
        model = Complication
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_associated_disease_ids(self, obj):
        return list(obj.associated_diseases.values_list("id", flat=True))

    def get_associated_drug_ids(self, obj):
        return list(obj.associated_drugs.values_list("id", flat=True))


# ─── V4.2 Knowledge Graph Serializers ────────────────────────────────────


class KnowledgeGraphNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeGraphNode
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class KnowledgeGraphEdgeSerializer(serializers.ModelSerializer):
    source_label = serializers.CharField(source="source.label", read_only=True)
    source_type = serializers.CharField(source="source.node_type", read_only=True)
    target_label = serializers.CharField(source="target.label", read_only=True)
    target_type = serializers.CharField(source="target.node_type", read_only=True)

    class Meta:
        model = KnowledgeGraphEdge
        fields = "__all__"
        read_only_fields = ["created_at"]


class ReasoningChainSerializer(serializers.Serializer):
    disease_id = serializers.CharField()
    disease_label = serializers.CharField()
    synapses = serializers.ListField()
    diagnosis = serializers.ListField()
    therapy = serializers.ListField()
    monitoring = serializers.ListField()
    complications = serializers.ListField()


class PathResultSerializer(serializers.Serializer):
    node_id = serializers.CharField()
    label = serializers.CharField()
    node_type = serializers.CharField()
    depth = serializers.IntegerField()
    edge_path = serializers.ListField()
    node_path = serializers.ListField()

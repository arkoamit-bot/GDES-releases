"""DRF viewsets and API views for the knowledge app."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.base import AuditedModelViewSet

from patients.models import Patient

from .models import (
    GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion,
    RuleTemplate, RuleReview, RuleTestResult, GuidelineDocument, EvidenceEntry,
    Disease, ClinicalCase, ClinicalPathway,
    Syndrome, PathologyEntity, LabEntity, DrugIntelligence,
    MonitoringProtocol, Complication,
    KnowledgeGraphNode, KnowledgeGraphEdge,
)
from . import serializers as s
from .graph_service import populate_from_models, find_paths, get_reasoning_chain, get_differential, get_graph_summary
from .services import evaluate_patient_rules, extract_patient_features
from .rule_validator import validate_rule_data, check_duplicate_conditions, validate_all_entries
from .rule_tester import test_rule, test_disease_suite, test_all_active_rules
from .evidence_engine import grade_evidence, suggest_evidence_grade, generate_citation
from .guideline_import import import_json_guideline, import_csv_guideline, import_yaml_guideline, import_markdown_guideline
from .knowledge_versioning import compute_rule_diff, create_version, rollback_to, version_history
from .authoring import create_rule, update_rule, apply_template, build_rule_data


class GuidelineSourceViewSet(AuditedModelViewSet):
    queryset = GuidelineSource.objects.all()
    serializer_class = s.GuidelineSourceSerializer


class RuleTemplateViewSet(AuditedModelViewSet):
    queryset = RuleTemplate.objects.all()
    serializer_class = s.RuleTemplateSerializer

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        category = request.query_params.get("category")
        if category:
            templates = self.get_queryset().filter(category=category)
        else:
            templates = self.get_queryset().all()
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        template = self.get_object()
        disease_id = request.data.get("disease_id", "")
        if not disease_id:
            return Response(
                {"error": "disease_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        values = request.data.get("values", {})
        try:
            entry = apply_template(template, disease_id, values)
            return Response(
                s.KnowledgeBaseEntrySerializer(entry).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RuleReviewViewSet(AuditedModelViewSet):
    queryset = RuleReview.objects.select_related("entry", "reviewer").all()
    serializer_class = s.RuleReviewSerializer

    @action(detail=False, methods=["get"])
    def pending(self, request):
        reviews = self.get_queryset().filter(status=RuleReview.ReviewStatus.PENDING)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.status = RuleReview.ReviewStatus.APPROVED
        review.reviewer = request.user if request.user.is_authenticated else None
        review.save()
        # Auto-activate the entry
        entry = review.entry
        if entry.status == KnowledgeBaseEntry.Status.DRAFT:
            entry.status = KnowledgeBaseEntry.Status.ACTIVE
            entry.save()
        return Response(s.RuleReviewSerializer(review).data)

    @action(detail=True, methods=["post"])
    def request_changes(self, request, pk=None):
        review = self.get_object()
        review.status = RuleReview.ReviewStatus.CHANGES_REQUESTED
        review.reviewer = request.user if request.user.is_authenticated else None
        review.review_notes = request.data.get("review_notes", review.review_notes)
        review.save()
        return Response(s.RuleReviewSerializer(review).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.status = RuleReview.ReviewStatus.REJECTED
        review.reviewer = request.user if request.user.is_authenticated else None
        review.review_notes = request.data.get("review_notes", review.review_notes)
        review.save()
        return Response(s.RuleReviewSerializer(review).data)


class RuleTestResultViewSet(AuditedModelViewSet):
    queryset = RuleTestResult.objects.select_related("entry", "patient").all()
    serializer_class = s.RuleTestResultSerializer

    @action(detail=False, methods=["get"])
    def by_entry(self, request):
        entry_id = request.query_params.get("entry_id")
        if not entry_id:
            return Response(
                {"error": "entry_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = self.get_queryset().filter(entry__entry_id=entry_id)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Summary stats across all test results."""
        all_results = self.get_queryset()
        total = all_results.count()
        passed = all_results.filter(matched=True).count()
        return Response({
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total else 100.0,
        })


class GuidelineDocumentViewSet(AuditedModelViewSet):
    queryset = GuidelineDocument.objects.select_related("source").all()
    serializer_class = s.GuidelineDocumentSerializer

    @action(detail=True, methods=["post"])
    def parse(self, request, pk=None):
        """Parse the document content into rule candidates without saving."""
        doc = self.get_object()
        from .guideline_parser import parse_markdown_guideline, parse_json_rules
        if doc.document_type in ("markdown", "html", "text"):
            candidates = parse_markdown_guideline(doc)
        elif doc.document_type == "json":
            import json
            try:
                data = json.loads(doc.content)
                candidates = parse_json_rules(data if isinstance(data, list) else data.get("rules", []))
            except (json.JSONDecodeError, TypeError) as e:
                return Response({"error": f"JSON parse error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Parsing not supported for this document type"}, status=status.HTTP_400_BAD_REQUEST)

        doc.parsed_rules = candidates
        doc.import_status = GuidelineDocument.ImportStatus.PARSING
        doc.save(update_fields=["parsed_rules", "import_status"])
        return Response({"candidates": len(candidates), "rules": candidates})

    @action(detail=True, methods=["post"])
    def import_rules(self, request, pk=None):
        """Parse and import rules from the document into KnowledgeBaseEntry records."""
        doc = self.get_object()
        result = import_markdown_guideline(doc)
        return Response(result)


class EvidenceEntryViewSet(AuditedModelViewSet):
    queryset = EvidenceEntry.objects.select_related("entry").all()
    serializer_class = s.EvidenceEntrySerializer

    @action(detail=False, methods=["get"])
    def by_entry(self, request):
        entry_id = request.query_params.get("entry_id")
        if not entry_id:
            return Response(
                {"error": "entry_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entries = self.get_queryset().filter(entry__entry_id=entry_id)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def citation(self, request, pk=None):
        evidence = self.get_object()
        return Response({"citation": generate_citation(evidence)})


class KnowledgeBaseEntryViewSet(AuditedModelViewSet):
    queryset = KnowledgeBaseEntry.objects.select_related("source").all()
    serializer_class = s.KnowledgeBaseEntrySerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response(
                {"error": "disease_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        entries = self.get_queryset().filter(disease_id=disease_id)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        entries = self.get_queryset().filter(
            status=KnowledgeBaseEntry.Status.ACTIVE
        )
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def evaluate(self, request):
        serializer = s.RuleEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient_id = serializer.validated_data["patient_id"]
        disease_id = serializer.validated_data.get("disease_id")

        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {patient_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        features = extract_patient_features(patient)
        results = evaluate_patient_rules(patient, disease_id=disease_id)

        response_data = {
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "disease_id_filter": disease_id,
            "features": features,
            "results": [
                {
                    "disease_id": r.disease_id,
                    "disease_name": r.disease_name,
                    "total_score": r.total_score,
                    "matched_rules_count": len(r.matched_rules),
                    "matched_rules": r.matched_rules,
                    "source": r.source,
                    "evidence_grade": r.evidence_grade,
                }
                for r in results
            ],
        }

        return Response(response_data)

    @action(detail=True, methods=["get", "post"])
    def versions(self, request, pk=None):
        entry = self.get_object()

        if request.method == "GET":
            versions = entry.versions.all()
            serializer = s.KnowledgeBaseVersionSerializer(versions, many=True)
            return Response(serializer.data)

        last_version = entry.versions.first()
        next_version = (last_version.version_number + 1) if last_version else 1
        change_summary = request.data.get("change_summary", "")

        version = KnowledgeBaseVersion.objects.create(
            entry=entry,
            version_number=next_version,
            rule_data=entry.rule_data,
            evidence_grade=entry.evidence_grade,
            guideline_chapter=entry.guideline_chapter,
            guideline_paragraph=entry.guideline_paragraph,
            guideline_quote=entry.guideline_quote,
            change_summary=change_summary,
            changed_by=request.user if request.user.is_authenticated else None,
        )

        return Response(
            s.KnowledgeBaseVersionSerializer(version).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def restore_version(self, request, pk=None):
        entry = self.get_object()
        version_id = request.data.get("version_id")

        if not version_id:
            return Response(
                {"error": "version_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target = KnowledgeBaseVersion.objects.get(id=version_id, entry=entry)
        except KnowledgeBaseVersion.DoesNotExist:
            return Response(
                {"error": "Version not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        rollback_to(entry, target, user=request.user if request.user.is_authenticated else None)
        return Response(s.KnowledgeBaseEntrySerializer(entry).data)

    # --- V2 Phase 4 actions ---

    @action(detail=False, methods=["post"])
    def validate(self, request):
        """Validate rule_data for correctness."""
        ser = s.ValidationRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        rule_data = ser.validated_data["rule_data"]
        entry_id = ser.validated_data.get("entry_id", "")

        result = validate_rule_data(rule_data, entry_id)
        dc = check_duplicate_conditions(rule_data, entry_id)
        result.merge(dc)

        return Response({
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
        })

    @action(detail=False, methods=["post"])
    def validate_all(self, request):
        """Validate every KnowledgeBaseEntry in the database."""
        results = validate_all_entries()
        return Response({
            "total": len(results),
            "valid": sum(1 for r in results if r.is_valid),
            "with_warnings": sum(1 for r in results if r.warnings),
            "with_errors": sum(1 for r in results if r.errors),
        })

    @action(detail=False, methods=["post"])
    def test(self, request):
        """Test a single rule against provided features."""
        ser = s.TestRuleRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        entry_id = ser.validated_data["entry_id"]
        features = ser.validated_data.get("features", {})
        expected_score = ser.validated_data.get("expected_score")

        try:
            entry = KnowledgeBaseEntry.objects.get(entry_id=entry_id)
        except KnowledgeBaseEntry.DoesNotExist:
            try:
                entry = KnowledgeBaseEntry.objects.get(pk=entry_id)
            except (KnowledgeBaseEntry.DoesNotExist, ValueError):
                return Response(
                    {"error": f"Entry '{entry_id}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        test_result = test_rule(entry, features=features, expected_score=expected_score)
        return Response(s.RuleTestResultSerializer(test_result).data)

    @action(detail=False, methods=["post"])
    def bulk_test(self, request):
        """Run a test suite against all active rules for a disease."""
        ser = s.BulkTestRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        disease_id = ser.validated_data["disease_id"]
        test_cases = ser.validated_data["test_cases"]

        results = test_disease_suite(disease_id, test_cases)
        return Response({
            "disease_id": disease_id,
            "test_cases": len(test_cases),
            "results": len(results),
            "passed": sum(1 for r in results if r.matched),
            "failed": sum(1 for r in results if not r.matched),
        })

    @action(detail=False, methods=["post"])
    def test_all(self, request):
        """Test every active rule against its own feature set."""
        summary = test_all_active_rules()
        return Response(summary)

    @action(detail=True, methods=["get"])
    def evidence_grade(self, request, pk=None):
        """Get GRADE-based evidence summary for a KnowledgeBaseEntry."""
        entry = self.get_object()
        return Response(grade_evidence(entry))

    @action(detail=True, methods=["get"])
    def suggest_grade(self, request, pk=None):
        """Auto-suggest an evidence grade based on linked evidence entries."""
        entry = self.get_object()
        return Response({"suggested_grade": suggest_evidence_grade(entry)})

    @action(detail=False, methods=["post"])
    def import_json(self, request):
        """Import rules from a JSON payload."""
        ser = s.ImportGuidelineRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        content = ser.validated_data["content"]
        source_abbr = ser.validated_data.get("source_abbreviation", "")
        source_year = ser.validated_data.get("source_year", 0)
        source_title = ser.validated_data.get("source_title", "")
        fmt = ser.validated_data["format"]

        import json
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return Response({"error": f"Invalid JSON: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        if fmt == "yaml":
            result = import_yaml_guideline(content, source_abbr, source_year, source_title)
        elif fmt == "csv":
            result = import_csv_guideline(content, source_abbr, source_year, source_title)
        else:
            items = data if isinstance(data, list) else data.get("rules", [])
            result = import_json_guideline(items, source_abbr, source_year, source_title)

        return Response(result)

    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export all KnowledgeBaseEntry records as JSON."""
        disease_id = request.query_params.get("disease_id")
        status_filter = request.query_params.get("status")
        entries = self.get_queryset()
        if disease_id:
            entries = entries.filter(disease_id=disease_id)
        if status_filter:
            entries = entries.filter(status=status_filter)

        serializer = self.get_serializer(entries, many=True)
        return Response({
            "count": len(serializer.data),
            "entries": serializer.data,
        })

    @action(detail=True, methods=["post"])
    def compute_diff(self, request, pk=None):
        """Compute structural diff between current rule_data and a previous version."""
        entry = self.get_object()
        version_id = request.data.get("version_id")
        if not version_id:
            return Response(
                {"error": "version_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            version = KnowledgeBaseVersion.objects.get(id=version_id, entry=entry)
        except KnowledgeBaseVersion.DoesNotExist:
            return Response(
                {"error": "Version not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        diff = compute_rule_diff(version.rule_data, entry.rule_data)
        return Response(diff)

    @action(detail=True, methods=["post"])
    def author_create(self, request, pk=None):
        """Create a rule from structured inputs (authoring helper)."""
        ser = request.data
        entry_id = ser.get("entry_id", "")
        disease_id = ser.get("disease_id", "")
        conditions = ser.get("conditions", [])
        weight = ser.get("weight", 1)
        base_score = ser.get("base_score", 0)
        explanation = ser.get("explanation", "")
        evidence_grade = ser.get("evidence_grade", "NG")
        rule_type = ser.get("rule_type", "diagnostic")
        tags = ser.get("tags", [])

        if not entry_id or not disease_id:
            return Response(
                {"error": "entry_id and disease_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            entry = create_rule(
                entry_id=entry_id,
                disease_id=disease_id,
                conditions=conditions,
                weight=weight,
                base_score=base_score,
                explanation=explanation,
                evidence_grade=evidence_grade,
                rule_type=rule_type,
                tags=tags,
            )
            return Response(
                s.KnowledgeBaseEntrySerializer(entry).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def governance_stats(self, request):
        """Knowledge governance dashboard — full transparency metrics."""
        from django.utils import timezone
        from django.db.models import Count, Q, Avg
        from datetime import date

        qs = self.get_queryset()
        today = timezone.now().date()

        # Rule status breakdown
        status_counts = dict(qs.values_list("status").annotate(c=Count("id")).values_list("status", "c"))
        status_breakdown = {
            "draft": status_counts.get("draft", 0),
            "under_review": status_counts.get("under_review", 0),
            "approved": status_counts.get("approved", 0),
            "active": status_counts.get("active", 0),
            "superseded": status_counts.get("superseded", 0),
            "archived": status_counts.get("archived", 0),
            "retired": status_counts.get("retired", 0),
        }
        total = sum(status_breakdown.values())

        # Evidence grade distribution
        evidence_grades = dict(qs.values_list("evidence_grade").annotate(c=Count("id")).values_list("evidence_grade", "c"))

        # Governance field coverage
        with_author = qs.exclude(author__isnull=True).count()
        with_approval = qs.exclude(approved_by__isnull=True).count()
        with_confidence = qs.exclude(confidence_score=0).count()
        with_explanation = qs.exclude(explanation="").count()
        with_recommendation_id = qs.exclude(recommendation_id="").count()
        with_next_review = qs.exclude(next_review_date__isnull=True).count()

        # Overdue re-reviews
        overdue_reviews = qs.filter(
            next_review_date__lte=today,
            status=KnowledgeBaseEntry.Status.ACTIVE,
        ).count()

        # Approvals pending (active but not approved_by anyone)
        approvals_pending = qs.filter(
            status=KnowledgeBaseEntry.Status.ACTIVE,
            approved_by__isnull=True,
        ).count()

        # Override statistics
        overrides_disallowed = qs.filter(override_allowed=False).count()

        # Recommendation audit stats
        from .models import RecommendationAudit
        rec_qs = RecommendationAudit.objects.all()
        rec_status_counts = dict(rec_qs.values_list("approval_status").annotate(c=Count("id")).values_list("approval_status", "c"))
        total_recommendations = rec_qs.count()
        overridden_count = rec_qs.filter(approval_status="overridden").count()
        avg_confidence = rec_qs.aggregate(avg=Avg("confidence_score"))["avg"] or 0

        # Review workflow metrics
        from .models import RuleReview
        review_qs = RuleReview.objects.all()
        pending_reviews = review_qs.filter(status=RuleReview.ReviewStatus.PENDING).count()
        approved_reviews = review_qs.filter(status=RuleReview.ReviewStatus.APPROVED).count()
        rejected_reviews = review_qs.filter(status=RuleReview.ReviewStatus.REJECTED).count()
        total_reviews = review_qs.count()
        approval_rate = (approved_reviews / total_reviews * 100) if total_reviews > 0 else 0

        # Version activity
        from .models import KnowledgeBaseVersion
        never_versioned = qs.filter(versions__isnull=True).count()

        # Disease coverage
        disease_counts = dict(qs.values_list("disease_id").annotate(c=Count("id")).values_list("disease_id", "c"))

        # Rule type distribution
        rule_type_counts = dict(qs.values_list("rule_type").annotate(c=Count("id")).values_list("rule_type", "c"))

        return Response({
            "total_rules": total,
            "status_breakdown": status_breakdown,
            "evidence_grade_distribution": evidence_grades,
            "rule_type_distribution": rule_type_counts,
            "disease_coverage": disease_counts,
            "governance_coverage": {
                "total_rules": total,
                "with_author": with_author,
                "with_author_pct": round(with_author / total * 100, 1) if total else 0,
                "with_approval": with_approval,
                "with_approval_pct": round(with_approval / total * 100, 1) if total else 0,
                "with_confidence_score": with_confidence,
                "with_confidence_pct": round(with_confidence / total * 100, 1) if total else 0,
                "with_explanation": with_explanation,
                "with_explanation_pct": round(with_explanation / total * 100, 1) if total else 0,
                "with_recommendation_id": with_recommendation_id,
                "with_recommendation_id_pct": round(with_recommendation_id / total * 100, 1) if total else 0,
                "with_next_review_date": with_next_review,
                "with_next_review_pct": round(with_next_review / total * 100, 1) if total else 0,
            },
            "review_workflow": {
                "pending_reviews": pending_reviews,
                "approved_reviews": approved_reviews,
                "rejected_reviews": rejected_reviews,
                "total_reviews": total_reviews,
                "approval_rate_pct": round(approval_rate, 1),
            },
            "re_review_alerts": {
                "overdue_reviews": overdue_reviews,
                "approvals_pending": approvals_pending,
            },
            "override_stats": {
                "overrides_disallowed": overrides_disallowed,
                "overrides_allowed": total - overrides_disallowed,
            },
            "recommendation_audit": {
                "total_recommendations": total_recommendations,
                "approval_status_breakdown": rec_status_counts,
                "overridden_count": overridden_count,
                "override_rate_pct": round(overridden_count / total_recommendations * 100, 1) if total_recommendations else 0,
                "avg_confidence_score": round(avg_confidence, 1),
            },
            "version_activity": {
                "never_versioned": never_versioned,
                "never_versioned_pct": round(never_versioned / total * 100, 1) if total else 0,
            },
        })


# ─── V4.0 Disease / Cases / Pathways Views ───────────────────────────


class DiseaseViewSet(AuditedModelViewSet):
    queryset = Disease.objects.all()
    serializer_class = s.DiseaseSerializer

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        category = request.query_params.get("category")
        if category:
            diseases = self.get_queryset().filter(category=category)
        else:
            diseases = self.get_queryset().all()
        serializer = self.get_serializer(diseases, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def rules(self, request, pk=None):
        disease = self.get_object()
        rules = KnowledgeBaseEntry.objects.filter(disease_id=disease.id)
        page = self.paginate_queryset(rules)
        if page is not None:
            serializer = s.KnowledgeBaseEntrySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = s.KnowledgeBaseEntrySerializer(rules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def pathways(self, request, pk=None):
        disease = self.get_object()
        pathways = ClinicalPathway.objects.filter(disease=disease, is_active=True)
        serializer = s.ClinicalPathwaySerializer(pathways, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def cases(self, request, pk=None):
        disease = self.get_object()
        cases = ClinicalCase.objects.filter(disease=disease, is_gold_standard=True)
        serializer = s.ClinicalCaseSerializer(cases, many=True)
        return Response(serializer.data)


class ClinicalCaseViewSet(AuditedModelViewSet):
    queryset = ClinicalCase.objects.select_related("disease").all()
    serializer_class = s.ClinicalCaseSerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        cases = self.get_queryset().filter(disease_id=disease_id)
        serializer = self.get_serializer(cases, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def gold_standard(self, request):
        cases = self.get_queryset().filter(is_gold_standard=True)
        serializer = self.get_serializer(cases, many=True)
        return Response(serializer.data)


class ClinicalPathwayViewSet(AuditedModelViewSet):
    queryset = ClinicalPathway.objects.select_related("disease").all()
    serializer_class = s.ClinicalPathwaySerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        pathways = self.get_queryset().filter(disease_id=disease_id, is_active=True)
        serializer = self.get_serializer(pathways, many=True)
        return Response(serializer.data)


# ─── V4.2 Reusable Knowledge Object Viewsets ──────────────────────────────


class SyndromeViewSet(AuditedModelViewSet):
    queryset = Syndrome.objects.all()
    serializer_class = s.SyndromeSerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        syndromes = self.get_queryset().filter(associated_diseases=disease_id, is_active=True)
        serializer = self.get_serializer(syndromes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        syndromes = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(syndromes, many=True)
        return Response(serializer.data)


class PathologyEntityViewSet(AuditedModelViewSet):
    queryset = PathologyEntity.objects.all()
    serializer_class = s.PathologyEntitySerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        entities = self.get_queryset().filter(associated_diseases=disease_id, is_active=True)
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)


class LabEntityViewSet(AuditedModelViewSet):
    queryset = LabEntity.objects.all()
    serializer_class = s.LabEntitySerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        entities = self.get_queryset().filter(associated_diseases=disease_id, is_active=True)
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)


class DrugIntelligenceViewSet(AuditedModelViewSet):
    queryset = DrugIntelligence.objects.all()
    serializer_class = s.DrugIntelligenceSerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        drugs = self.get_queryset().filter(indications=disease_id, is_active=True)
        serializer = self.get_serializer(drugs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_class(self, request):
        drug_class = request.query_params.get("drug_class")
        if not drug_class:
            return Response({"error": "drug_class is required"}, status=status.HTTP_400_BAD_REQUEST)
        drugs = self.get_queryset().filter(drug_class__icontains=drug_class, is_active=True)
        serializer = self.get_serializer(drugs, many=True)
        return Response(serializer.data)


class MonitoringProtocolViewSet(AuditedModelViewSet):
    queryset = MonitoringProtocol.objects.select_related("drug").all()
    serializer_class = s.MonitoringProtocolSerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        protocols = self.get_queryset().filter(associated_diseases=disease_id, is_active=True)
        serializer = self.get_serializer(protocols, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_drug(self, request):
        drug_id = request.query_params.get("drug_id")
        if not drug_id:
            return Response({"error": "drug_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        protocols = self.get_queryset().filter(drug__id=drug_id, is_active=True)
        serializer = self.get_serializer(protocols, many=True)
        return Response(serializer.data)


class ComplicationViewSet(AuditedModelViewSet):
    queryset = Complication.objects.all()
    serializer_class = s.ComplicationSerializer

    @action(detail=False, methods=["get"])
    def by_disease(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        complications = self.get_queryset().filter(associated_diseases=disease_id, is_active=True)
        serializer = self.get_serializer(complications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_drug(self, request):
        drug_id = request.query_params.get("drug_id")
        if not drug_id:
            return Response({"error": "drug_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        complications = self.get_queryset().filter(associated_drugs=drug_id, is_active=True)
        serializer = self.get_serializer(complications, many=True)
        return Response(serializer.data)


# ─── V4.2 Knowledge Graph Viewsets ────────────────────────────────────────


class KnowledgeGraphNodeViewSet(AuditedModelViewSet):
    queryset = KnowledgeGraphNode.objects.all()
    serializer_class = s.KnowledgeGraphNodeSerializer

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        node_type = request.query_params.get("node_type")
        if not node_type:
            return Response({"error": "node_type is required"}, status=status.HTTP_400_BAD_REQUEST)
        nodes = self.get_queryset().filter(node_type=node_type, is_active=True)
        serializer = self.get_serializer(nodes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        nodes = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(nodes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def outgoing(self, request, pk=None):
        node = self.get_object()
        edges = KnowledgeGraphEdge.objects.filter(source=node, is_active=True).select_related("target")
        serializer = s.KnowledgeGraphEdgeSerializer(edges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def incoming(self, request, pk=None):
        node = self.get_object()
        edges = KnowledgeGraphEdge.objects.filter(target=node, is_active=True).select_related("source")
        serializer = s.KnowledgeGraphEdgeSerializer(edges, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def paths(self, request, pk=None):
        node = self.get_object()
        target_type = request.query_params.get("target_type")
        max_depth = int(request.query_params.get("max_depth", 4))
        results = find_paths(node.node_id, target_node_type=target_type, max_depth=max_depth)
        return Response(results)

    @action(detail=False, methods=["post"])
    def populate(self, request):
        """Scan all knowledge objects and build the graph."""
        populate_from_models()
        summary = get_graph_summary()
        return Response({"message": "Graph populated successfully", "summary": summary})

    @action(detail=False, methods=["get"])
    def summary(self, request):
        return Response(get_graph_summary())

    @action(detail=False, methods=["get"])
    def reasoning_chain(self, request):
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        chain = get_reasoning_chain(disease_id)
        return Response(chain)

    @action(detail=False, methods=["get"])
    def differential(self, request):
        syndrome_id = request.query_params.get("syndrome_id")
        if not syndrome_id:
            return Response({"error": "syndrome_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        diff = get_differential(syndrome_id)
        return Response(diff)


class KnowledgeGraphEdgeViewSet(AuditedModelViewSet):
    queryset = KnowledgeGraphEdge.objects.select_related("source", "target").all()
    serializer_class = s.KnowledgeGraphEdgeSerializer

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        edge_type = request.query_params.get("edge_type")
        if not edge_type:
            return Response({"error": "edge_type is required"}, status=status.HTTP_400_BAD_REQUEST)
        edges = self.get_queryset().filter(edge_type=edge_type, is_active=True)
        serializer = self.get_serializer(edges, many=True)
        return Response(serializer.data)


# ─── V4.2 Graph-Enhanced Reasoning API ──────────────────────────────────


class GraphReasoningViewSet(viewsets.GenericViewSet):
    """Expose graph-enhanced clinical reasoning services via API.

    Provides endpoints for treatment recommendations, monitoring plans,
    complication risks, syndrome matching, and differential generation
    based on knowledge graph traversal.
    """
    permission_classes = [IsAuthenticated]
    queryset = KnowledgeGraphNode.objects.none()
    serializer_class = s.KnowledgeGraphNodeSerializer

    @action(detail=False, methods=["get"])
    def treatments(self, request):
        """Get graph-derived treatment recommendations for a disease."""
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import get_treatment_recommendations
        results = get_treatment_recommendations(disease_id)
        return Response({"disease_id": disease_id, "treatments": results})

    @action(detail=False, methods=["get"])
    def monitoring(self, request):
        """Get graph-derived monitoring recommendations for a disease."""
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import get_monitoring_recommendations
        results = get_monitoring_recommendations(disease_id)
        return Response({"disease_id": disease_id, "protocols": results})

    @action(detail=False, methods=["get"])
    def complications(self, request):
        """Get graph-derived complication risks for a disease."""
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import get_complication_risks
        results = get_complication_risks(disease_id)
        return Response({"disease_id": disease_id, "complications": results})

    @action(detail=False, methods=["post"])
    def syndrome_match(self, request):
        """Match clinical features to syndrome nodes in the graph."""
        features = request.data.get("features")
        if not features:
            return Response({"error": "features dict is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import get_syndrome_matches
        results = get_syndrome_matches(features)
        return Response({"matches": results})

    @action(detail=False, methods=["post"])
    def graph_differential(self, request):
        """Generate differential diagnosis from the graph via syndrome matching."""
        features = request.data.get("features")
        if not features:
            return Response({"error": "features dict is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import get_graph_differential
        results = get_graph_differential(features)
        return Response({"differential": results})

    @action(detail=False, methods=["get"])
    def enhanced_plan(self, request):
        """Get comprehensive enhanced treatment plan from the graph."""
        disease_id = request.query_params.get("disease_id")
        if not disease_id:
            return Response({"error": "disease_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        from .graph_reasoning import enhance_treatment_plan
        plan = enhance_treatment_plan(disease_id)
        return Response(plan)

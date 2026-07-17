import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import (
    ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict,
    AIFailureLog, RuleFailureLog, UserFeedback, WorkflowFeedback,
    PerformanceLog, KnowledgeImprovementSuggestion, FeedbackExport,
)
from .serializers import (
    ErrorLogSerializer, CrashReportSerializer, ClinicalConflictSerializer,
    KnowledgeConflictSerializer, AIFailureLogSerializer, RuleFailureLogSerializer,
    UserFeedbackSerializer, WorkflowFeedbackSerializer, PerformanceLogSerializer,
    KnowledgeImprovementSuggestionSerializer,
)
from .services import (
    export_feedback_package, generate_improvement_suggestions,
    generate_summary_report,
)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class ErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("severity", "module", "error_type")
    ordering = ("-timestamp",)


class CrashReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CrashReport.objects.all()
    serializer_class = CrashReportSerializer
    permission_classes = [permissions.IsAdminUser]
    ordering = ("-timestamp",)


class ClinicalConflictViewSet(viewsets.ModelViewSet):
    queryset = ClinicalConflict.objects.all()
    serializer_class = ClinicalConflictSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("disease", "resolved", "knowledge_rule_id")
    ordering = ("-timestamp",)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        conflict = self.get_object()
        conflict.resolved = True
        conflict.save(update_fields=["resolved"])
        return Response({"status": "resolved"})


class KnowledgeConflictViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeConflict.objects.all()
    serializer_class = KnowledgeConflictSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("conflict_type", "severity", "resolved")
    ordering = ("-timestamp",)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        kc = self.get_object()
        kc.resolved = True
        kc.save(update_fields=["resolved"])
        return Response({"status": "resolved"})


class AIFailureLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIFailureLog.objects.all()
    serializer_class = AIFailureLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("failure_type", "disease")
    ordering = ("-timestamp",)


class RuleFailureLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleFailureLog.objects.all()
    serializer_class = RuleFailureLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("rule_id", "disease")
    ordering = ("-timestamp",)


class UserFeedbackViewSet(viewsets.ModelViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkflowFeedbackViewSet(viewsets.ModelViewSet):
    queryset = WorkflowFeedback.objects.all()
    serializer_class = WorkflowFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PerformanceLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PerformanceLog.objects.all()
    serializer_class = PerformanceLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("metric_name", "module")
    ordering = ("-timestamp",)


class KnowledgeImprovementSuggestionViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeImprovementSuggestion.objects.all()
    serializer_class = KnowledgeImprovementSuggestionSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ("status", "disease", "rule_id")
    ordering = ("-override_count",)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def report_clinical_conflict(request):
    serializer = ClinicalConflictSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def report_knowledge_conflict(request):
    serializer = KnowledgeConflictSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def log_ai_failure(request):
    serializer = AIFailureLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def log_rule_failure(request):
    serializer = RuleFailureLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def generate_suggestions(request):
    suggestions = generate_improvement_suggestions()
    return Response({
        "suggestions_created": len(suggestions),
        "message": "Improvement suggestions generated",
    })


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def summary_report(request):
    report = generate_summary_report()
    return Response(report)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def export_package(request):
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if date_from:
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    if date_to:
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

    buf, manifest = export_feedback_package(date_from, date_to)
    filename = f"GDES_Feedback_{timezone.now():%Y%m%d_%H%M%S}.zip"

    FeedbackExport.objects.create(
        filename=filename,
        size_bytes=buf.tell(),
        date_from=date_from,
        date_to=date_to,
        included_sections=manifest.get("sections", []),
        export_hash=manifest.get("exported_at", ""),
    )

    response = HttpResponse(buf.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_workflow_feedback(request):
    serializer = WorkflowFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def feedback_dashboard(request):
    now = timezone.now()
    thirty_days = now - timedelta(days=30)

    context = {
        "total_errors": ErrorLog.objects.count(),
        "errors_30d": ErrorLog.objects.filter(timestamp__gte=thirty_days).count(),
        "total_crashes": CrashReport.objects.count(),
        "crashes_30d": CrashReport.objects.filter(timestamp__gte=thirty_days).count(),
        "unresolved_conflicts": ClinicalConflict.objects.filter(resolved=False).count(),
        "total_conflicts": ClinicalConflict.objects.count(),
        "knowledge_conflicts": KnowledgeConflict.objects.filter(resolved=False).count(),
        "ai_failures": AIFailureLog.objects.filter(timestamp__gte=thirty_days).count(),
        "rule_failures": RuleFailureLog.objects.filter(timestamp__gte=thirty_days).count(),
        "pending_feedback": UserFeedback.objects.filter(resolved=False).count(),
        "total_workflow_feedback": WorkflowFeedback.objects.count(),
        "avg_rating": WorkflowFeedback.objects.aggregate(avg=Avg("rating"))["avg"],
        "total_suggestions": KnowledgeImprovementSuggestion.objects.count(),
        "pending_suggestions": KnowledgeImprovementSuggestion.objects.filter(status="pending").count(),
        "slow_pages_30d": PerformanceLog.objects.filter(metric_name="slow_page", timestamp__gte=thirty_days).count(),

        "error_by_type": list(
            ErrorLog.objects.values("error_type")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "conflict_by_disease": list(
            ClinicalConflict.objects.values("disease")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "knowledge_conflict_by_type": list(
            KnowledgeConflict.objects.values("conflict_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "feedback_by_type": list(
            UserFeedback.objects.values("feedback_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "slow_pages": list(
            PerformanceLog.objects.filter(metric_name="slow_page")
            .values("page")
            .annotate(avg_ms=Avg("duration_ms"), count=Count("id"))
            .order_by("-avg_ms")[:10]
        ),
        "ai_failures_by_type": list(
            AIFailureLog.objects.values("failure_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "top_failing_rules": list(
            RuleFailureLog.objects.values("rule_id", "disease")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "severity_breakdown": list(
            ErrorLog.objects.values("severity")
            .annotate(count=Count("id"))
            .order_by("severity")
        ),
    }
    return render(request, "feedback/dashboard.html", context)


@login_required
def report_problem(request):
    if request.method == "POST":
        UserFeedback.objects.create(
            user=request.user,
            feedback_type=request.POST.get("feedback_type", "software_bug"),
            title=request.POST.get("title", ""),
            description=request.POST.get("description", ""),
            page_url=request.POST.get("page_url", ""),
        )
        return redirect("feedback:feedback_dashboard")
    return render(request, "feedback/report_problem.html")


@login_required
def conflict_list(request):
    conflicts = ClinicalConflict.objects.all().order_by("-timestamp")
    k_conflicts = KnowledgeConflict.objects.all().order_by("-timestamp")

    context = {
        "conflicts": conflicts,
        "knowledge_conflicts": k_conflicts,
        "unresolved": conflicts.filter(resolved=False).count(),
    }
    return render(request, "feedback/conflict_list.html", context)


@login_required
@require_POST
def resolve_conflict(request, pk):
    conflict = get_object_or_404(ClinicalConflict, pk=pk)
    conflict.resolved = True
    conflict.save(update_fields=["resolved"])
    return redirect("feedback:conflict_list")


@login_required
def workflow_feedback_page(request):
    if request.method == "POST":
        WorkflowFeedback.objects.create(
            user=request.user,
            patient_id=request.POST.get("patient") or None,
            feedback_type=request.POST.get("feedback_type", "diagnosis"),
            rating=request.POST.get("rating", 3),
            comments=request.POST.get("comments", ""),
        )
        return redirect("feedback:feedback_dashboard")
    return render(request, "feedback/workflow_feedback.html")


@login_required
def improvement_suggestions(request):
    suggestions = KnowledgeImprovementSuggestion.objects.all().order_by("-override_count")

    if request.method == "POST":
        sid = request.POST.get("suggestion_id")
        action = request.POST.get("action")
        if sid and action in ("approve", "reject"):
            suggestion = get_object_or_404(KnowledgeImprovementSuggestion, pk=sid)
            suggestion.status = "approved" if action == "approve" else "rejected"
            suggestion.reviewed_by = request.user
            suggestion.reviewed_at = timezone.now()
            suggestion.reviewer_notes = request.POST.get("reviewer_notes", "")
            suggestion.save()
            return redirect("feedback:improvement_suggestions")

    return render(request, "feedback/improvement_suggestions.html", {
        "suggestions": suggestions,
    })


@login_required
def summary_report_view(request):
    report = generate_summary_report()
    return render(request, "feedback/summary_report.html", {"report": report})

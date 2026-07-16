from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.base import AuditedModelViewSet
from knowledge.models import RecommendationAudit
from patients.models import Patient

from .models import ClinicalProfile, ClinicalInsight
from . import serializers as s
from .services.engine import reason_about_patient, recompute_all_profiles
from .services.explainability import build_full_explainability
from .services.management_plan import generate_management_plan
from .services.monitoring_plan import generate_monitoring_plan
from .services.followup_scheduler import (
    generate_follow_up_schedule,
    auto_schedule_on_phase_change,
)
from .services.investigation_engine import generate_investigation_recommendations
from .services.drug_toxicity import detect_drug_toxicity
from .services.treatment_failure import detect_treatment_failure, detect_relapse
from .services.disease_validation import validate_disease_management
from .services.retrospective_validation import run_retrospective_validation
from .services.audit import (
    audit_management_plan,
    audit_monitoring_plan,
    audit_investigation_recommendations,
    audit_drug_toxicity,
    audit_treatment_failure,
    audit_relapse,
    audit_clinical_reasoning,
)


class ClinicalProfileViewSet(AuditedModelViewSet):
    queryset = ClinicalProfile.objects.select_related("patient").all()
    serializer_class = s.ClinicalProfileSerializer

    @action(detail=False, methods=["get"])
    def by_patient(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            return Response(
                {"error": "patient_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            profile = self.get_queryset().get(patient_id=patient_id)
        except ClinicalProfile.DoesNotExist:
            try:
                patient = Patient.objects.get(pk=patient_id)
                profile = reason_about_patient(patient)
            except Patient.DoesNotExist:
                return Response(
                    {"error": f"Patient {patient_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def reason(self, request):
        """Trigger clinical reasoning for a specific patient."""
        ser = s.ReasoningRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        patient_id = ser.validated_data["patient_id"]
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {patient_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile = reason_about_patient(patient)
        audit_clinical_reasoning(patient, profile, profile.care_pathway or {}, clinician=request.user)
        return Response(s.ClinicalProfileSerializer(profile).data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def reason_all(self, request):
        """Trigger clinical reasoning for all patients."""
        summary = recompute_all_profiles()
        return Response(summary)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def explain(self, request):
        """Get full explainability report for a patient."""
        ser = s.ExplainabilityRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        patient_id = ser.validated_data["patient_id"]
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {patient_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        if not profile.reasoning_chain:
            profile = reason_about_patient(patient)

        explanation = build_full_explainability(profile)
        return Response(explanation)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """List recently updated clinical profiles."""
        limit = int(request.query_params.get("limit", 20))
        profiles = self.get_queryset().order_by("-last_updated")[:limit]
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def with_gaps(self, request):
        """List profiles that have active care gaps."""
        profiles = self.get_queryset().filter(
            care_pathway__care_gaps__0__exists=True,
        ).order_by("-last_updated")
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def management_plan(self, request):
        """Generate a personalized management plan for a patient."""
        ser = s.ManagementPlanRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        plan = generate_management_plan(
            patient=patient,
            disease_id=ser.validated_data["disease_id"],
            features=ser.validated_data.get("features"),
            risk_category=ser.validated_data.get("risk_category", "moderate"),
        )
        audit_management_plan(patient, plan, ser.validated_data["disease_id"], clinician=request.user)
        return Response(plan.to_dict())

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def monitoring_plan(self, request):
        """Generate a personalized monitoring plan for a patient."""
        ser = s.MonitoringPlanRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        plan = generate_monitoring_plan(
            patient=patient,
            disease_id=ser.validated_data["disease_id"],
            active_treatments=ser.validated_data.get("active_treatments", []),
            ckd_stage=ser.validated_data.get("ckd_stage"),
            risk_category=ser.validated_data.get("risk_category", "moderate"),
        )
        audit_monitoring_plan(patient, plan, ser.validated_data["disease_id"], clinician=request.user)
        return Response(plan.to_dict())

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def followup_schedule(self, request):
        """Generate a personalized follow-up schedule for a patient."""
        ser = s.FollowUpScheduleRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        visits = generate_follow_up_schedule(
            patient=patient,
            risk_category=ser.validated_data.get("risk_category", "moderate"),
            disease_phase=ser.validated_data.get("disease_phase", "active"),
            treatment_phase=ser.validated_data.get("treatment_phase", "induction"),
            disease_id=ser.validated_data.get("disease_id"),
            num_visits=ser.validated_data.get("num_visits", 6),
        )
        return Response({"visits": visits, "count": len(visits)})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def investigation_recommendations(self, request):
        """Generate investigation recommendations based on differential."""
        ser = s.InvestigationRecommendationRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        if not profile.differential:
            profile = reason_about_patient(patient)

        plan = generate_investigation_recommendations(
            patient=patient,
            differential=profile.differential,
            features=ser.validated_data.get("features"),
        )
        audit_investigation_recommendations(patient, plan, "", clinician=request.user)
        return Response(plan.to_dict())

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def drug_toxicity(self, request):
        """Detect potential drug toxicity from current medications and labs."""
        ser = s.PatientRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        report = detect_drug_toxicity(patient)
        audit_drug_toxicity(patient, report, clinician=request.user)
        return Response(report.to_dict())

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def treatment_failure(self, request):
        """Detect treatment failure patterns."""
        ser = s.PatientRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        report = detect_treatment_failure(patient, profile)
        audit_treatment_failure(patient, report, clinician=request.user)
        return Response(report.to_dict())

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def relapse_detection(self, request):
        """Detect disease relapse from previously controlled state."""
        ser = s.PatientRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        alerts = detect_relapse(patient, profile)
        audit_relapse(patient, alerts, clinician=request.user)
        return Response({
            "alerts": [a.to_dict() for a in alerts],
            "count": len(alerts),
        })

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def validate_disease(self, request):
        """Run end-to-end validation for a specific disease."""
        ser = s.DiseaseValidationRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        try:
            patient = Patient.objects.get(pk=ser.validated_data["patient_id"])
        except Patient.DoesNotExist:
            return Response(
                {"error": f"Patient {ser.validated_data['patient_id']} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        report = validate_disease_management(
            patient=patient,
            disease=ser.validated_data["disease"],
        )
        return Response(report.to_dict())

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def retrospective_validation(self, request):
        """Run retrospective validation comparing AI vs clinician decisions."""
        period_start = request.query_params.get("period_start")
        period_end = request.query_params.get("period_end")
        disease_filter = request.query_params.get("disease")

        report = run_retrospective_validation(
            period_start=period_start,
            period_end=period_end,
            disease_filter=disease_filter,
        )
        return Response(report.to_dict())


class ClinicalInsightViewSet(AuditedModelViewSet):
    queryset = ClinicalInsight.objects.select_related("patient").all()
    serializer_class = s.ClinicalInsightSerializer

    @action(detail=False, methods=["get"])
    def by_patient(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            return Response(
                {"error": "patient_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        insights = self.get_queryset().filter(patient_id=patient_id, dismissed=False)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active_alerts(self, request):
        """Get all non-dismissed high/critical insights."""
        insights = self.get_queryset().filter(
            dismissed=False,
            priority__in=[ClinicalInsight.Priority.CRITICAL, ClinicalInsight.Priority.HIGH],
        ).order_by("-created_at")
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        insight = self.get_object()
        insight.dismissed = True
        insight.save()
        return Response(s.ClinicalInsightSerializer(insight).data)


class RecommendationAuditViewSet(AuditedModelViewSet):
    queryset = RecommendationAudit.objects.select_related("patient", "clinician").all()
    serializer_class = s.RecommendationAuditSerializer
    filterset_fields = ["patient", "recommendation_type", "approval_status", "disease_id"]

    @action(detail=False, methods=["get"])
    def by_patient(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            return Response(
                {"error": "patient_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        audits = self.get_queryset().filter(patient_id=patient_id).order_by("-issued_at")[:50]
        serializer = self.get_serializer(audits, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], serializer_class=s.ReviewRecommendationSerializer)
    def review(self, request, pk=None):
        audit = self.get_object()
        ser = s.ReviewRecommendationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        audit.approval_status = ser.validated_data["approval_status"]
        audit.override_reason = ser.validated_data.get("override_reason", "")
        audit.expert_reviewer = request.user
        audit.reviewed_at = timezone.now()
        audit.save()

        return Response(s.RecommendationAuditSerializer(audit).data)

    @action(detail=False, methods=["get"])
    def comparison(self, request):
        """AI-vs-Expert comparison summary (Layer 1 — Clinical Memory Engine).

        Returns aggregate statistics comparing AI recommendations against
        clinician decisions for a given period or disease.
        """
        disease = request.query_params.get("disease_id")
        days = int(request.query_params.get("days", 90))

        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        qs = self.get_queryset().filter(issued_at__gte=cutoff)
        if disease:
            qs = qs.filter(disease_id=disease)

        total = qs.count()
        reviewed = qs.exclude(approval_status="pending").count()
        approved = qs.filter(approval_status="approved").count()
        rejected = qs.filter(approval_status="rejected").count()
        overridden = qs.filter(approval_status="overridden").count()

        return Response({
            "period_days": days,
            "disease_id": disease or "all",
            "total_recommendations": total,
            "reviewed": reviewed,
            "approved": approved,
            "rejected": rejected,
            "overridden": overridden,
            "acceptance_rate": round(approved / total * 100, 1) if total else 0.0,
            "review_rate": round(reviewed / total * 100, 1) if total else 0.0,
        })

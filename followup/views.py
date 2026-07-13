"""REST API viewsets for the follow-up engine.

- FollowUpTaskViewSet: CRUD for individual follow-up tasks
- FollowUpPlanViewSet: read-only computed plans per patient
"""

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from followup.models import FollowUpTask
from followup.services.engine import compute_followup_plan
from followup.services.dashboard import get_daily_summary


class FollowUpTaskSerializer(serializers.ModelSerializer):
    patient_id = serializers.CharField(source="patient.patient_id", read_only=True)

    class Meta:
        model = FollowUpTask
        fields = [
            "id", "patient", "patient_id", "task_type", "priority",
            "reason", "clinical_reason", "due_date", "overdue_date",
            "status", "assigned_to", "completed_at", "completed_by",
            "escalation_level", "protocol_label", "created_at",
        ]
        read_only_fields = ["escalation_level", "created_at"]


class FollowUpTaskViewSet(viewsets.ModelViewSet):
    queryset = FollowUpTask.objects.select_related("patient").all()
    serializer_class = FollowUpTaskSerializer
    filterset_fields = ["patient", "task_type", "priority", "status", "escalation_level"]
    search_fields = ["patient__patient_id", "patient__name", "reason"]


class FollowUpPlanViewSet(viewsets.ViewSet):
    """Read-only view to compute and retrieve follow-up plans."""

    def list(self, request):
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            return Response({"error": "patient_id query parameter is required"}, status=400)
        from patients.models import Patient
        try:
            patient = Patient.objects.get(pk=int(patient_id))
        except (Patient.DoesNotExist, ValueError, TypeError):
            try:
                patient = Patient.objects.get(patient_id=patient_id)
            except Patient.DoesNotExist:
                return Response({"error": "Patient not found"}, status=404)
        try:
            plan = compute_followup_plan(patient)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        tasks = FollowUpTask.objects.filter(
            patient=patient,
            status__in=["pending", "overdue"],
        ).order_by("due_date")
        plan["tasks"] = FollowUpTaskSerializer(tasks, many=True).data
        return Response(plan)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        data = get_daily_summary()
        return Response(data)

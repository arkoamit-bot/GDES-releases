from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TimelineEvent
from .serializers import TimelineEventSerializer
from .services import get_patient_timeline, rebuild_patient_timeline
from patients.models import Patient


class TimelineEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TimelineEvent.objects.all()
    serializer_class = TimelineEventSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        patient_id = self.request.query_params.get("patient")
        domain = self.request.query_params.get("domain")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if domain:
            qs = qs.filter(domain=domain)
        return qs

    @action(detail=False, methods=["post"])
    def rebuild(self, request):
        patient_id = request.data.get("patient")
        if not patient_id:
            return Response({"error": "patient is required"}, status=400)
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=404)
        events = rebuild_patient_timeline(patient)
        resp = Response({"rebuild": True, "events_created": len(events)})
        resp["HX-Refresh"] = "true"
        return resp

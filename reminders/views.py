from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from patients.models import Patient

from .models import (
    ReminderSchedule, ReminderTemplate,
    PatientCommunicationPreference,
)
from .serializers import (
    ReminderScheduleSerializer, ReminderTemplateSerializer,
    PatientCommunicationPreferenceSerializer,
    SendCustomReminderSerializer, ScheduleVisitRemindersSerializer,
)
from .tasks import (
    send_reminder,
    schedule_visit_reminders as auto_schedule_reminders,
)


LOGIN = "/login/"


@login_required(login_url=LOGIN)
def reminder_log(request):
    """In-app reminder log — manually log reminders during consults."""
    if request.method == "POST":
        patient = get_object_or_404(Patient, pk=request.POST.get("patient"))
        reminder_type = request.POST.get("reminder_type", "general")
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        if title:
            ReminderSchedule.objects.create(
                patient=patient,
                reminder_type=reminder_type,
                channel="app",
                title=title,
                message=message,
                scheduled_at=timezone.now(),
            )
        return redirect("reminders:log")

    qs = ReminderSchedule.objects.filter(channel="app").select_related("patient")
    active = qs.exclude(status__in=["cancelled", "sent"])
    completed = qs.filter(status__in=["cancelled", "sent"])[:50]
    patients = Patient.objects.all().order_by("patient_id")

    return render(request, "reminders/reminder_log.html", {
        "active": "reminders",
        "reminders_active": active,
        "reminders_completed": completed,
        "patients": patients,
        "reminder_types": ReminderSchedule._meta.get_field("reminder_type").choices,
    })


@login_required(login_url=LOGIN)
def reminder_done(request, pk):
    """Mark an in-app reminder as completed/sent."""
    r = get_object_or_404(ReminderSchedule, pk=pk, channel="app")
    r.status = "sent"
    r.sent_at = timezone.now()
    r.save()
    return redirect("reminders:log")


@login_required(login_url=LOGIN)
def reminder_cancel(request, pk):
    """Cancel an in-app reminder."""
    r = get_object_or_404(ReminderSchedule, pk=pk, channel="app")
    r.status = "cancelled"
    r.save()
    return redirect("reminders:log")


class ReminderScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReminderSchedule.objects.select_related("patient", "scheduled_visit")
    serializer_class = ReminderScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["patient", "status", "reminder_type", "channel"]

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        reminder = self.get_object()
        reminder.status = "cancelled"
        reminder.save()
        return Response({"status": "cancelled"})

    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        reminder = self.get_object()
        success = send_reminder(reminder)
        if success:
            reminder.status = "sent"
            reminder.save()
            return Response({"status": "resent"})
        return Response(
            {"error": "Failed to send reminder"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ReminderTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReminderTemplate.objects.all()
    serializer_class = ReminderTemplateSerializer
    permission_classes = [IsAuthenticated]


class PatientCommunicationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = PatientCommunicationPreference.objects.all()
    serializer_class = PatientCommunicationPreferenceSerializer
    permission_classes = [IsAuthenticated]


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def send_custom_reminder(request):
    """Send a custom reminder to a patient."""
    if request.method == "GET":
        return Response({
            "endpoint": "POST /api/v1/reminders/send/",
            "payload_example": {
                "patient_id": "BGD-00001",
                "reminder_type": "general",
                "channel": "sms",
                "title": "Lab reminder",
                "message": "Dear {{patient_name}}, please remit your lab reports.",
                "scheduled_at": "2026-07-10T09:00:00Z",
            },
        })

    serializer = SendCustomReminderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    d = serializer.validated_data

    try:
        patient = Patient.objects.get(patient_id=d["patient_id"])
    except Patient.DoesNotExist:
        return Response(
            {"error": f"Patient {d['patient_id']} not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    reminder = ReminderSchedule.objects.create(
        patient=patient,
        reminder_type=d["reminder_type"],
        channel=d["channel"],
        title=d["title"],
        message=d["message"],
        scheduled_at=d["scheduled_at"],
    )

    # Attempt immediate send
    success = send_reminder(reminder)
    if success:
        reminder.status = "sent"
        reminder.sent_at = d["scheduled_at"]
        reminder.save()

    return Response(ReminderScheduleSerializer(reminder).data,
                    status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def schedule_reminders(request):
    """Manually trigger scheduling of visit reminders."""
    serializer = ScheduleVisitRemindersSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = auto_schedule_reminders()
    return Response(result)

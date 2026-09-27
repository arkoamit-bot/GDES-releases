from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    BasePermission, DjangoModelPermissions, IsAuthenticated,
)
from rest_framework.response import Response

from api.base import AuditedModelViewSet
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


class ReminderWritePermission(BasePermission):
    """Gate the reminder write paths on the reminders model permission.

    ``DjangoModelPermissions`` derives its queryset from the view, so it cannot
    be attached to an ``@api_view`` function or a plain Django view; the check
    is spelled out instead. Authentication alone let any logged-in account
    complete, cancel, or send reminders belonging to other clinicians' patients.
    """

    message = "You do not have permission to manage patient reminders."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return user.has_perm("reminders.change_reminderschedule")


def _require_reminder_write(request):
    """Enforce the reminders change permission on the plain-Django write views.

    Deliberately does not reuse ``ReminderWritePermission.has_permission``:
    every call site below *mutates* state, and two of them (``reminder_done`` /
    ``reminder_cancel``) do it on a GET link. The permission class short-circuits
    safe methods, so reusing it would let any authenticated account close out
    another clinician's reminder by following the URL.
    """
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated) or not user.has_perm(
        "reminders.change_reminderschedule"
    ):
        raise PermissionDenied(ReminderWritePermission.message)


@login_required(login_url=LOGIN)
def reminder_log(request):
    """In-app reminder log — manually log reminders during consults."""
    if request.method == "POST":
        _require_reminder_write(request)
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
    _require_reminder_write(request)
    r = get_object_or_404(ReminderSchedule, pk=pk, channel="app")
    r.status = "sent"
    r.sent_at = timezone.now()
    r.save()
    return redirect("reminders:log")


@login_required(login_url=LOGIN)
def reminder_cancel(request, pk):
    """Cancel an in-app reminder."""
    _require_reminder_write(request)
    r = get_object_or_404(ReminderSchedule, pk=pk, channel="app")
    r.status = "cancelled"
    r.save()
    return redirect("reminders:log")


class ReminderScheduleViewSet(AuditedModelViewSet):
    queryset = ReminderSchedule.objects.select_related("patient", "scheduled_visit")
    serializer_class = ReminderScheduleSerializer
    # Reminder bodies and contact history are clinical data: keep the project
    # default (IsAuthenticated + DjangoModelPermissions) instead of downgrading
    # to authentication alone, which let any logged-in account read every
    # patient's reminders and fire an SMS/WhatsApp/email with an arbitrary body.
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
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


class ReminderTemplateViewSet(AuditedModelViewSet):
    queryset = ReminderTemplate.objects.all()
    serializer_class = ReminderTemplateSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class PatientCommunicationPreferenceViewSet(AuditedModelViewSet):
    queryset = PatientCommunicationPreference.objects.all()
    serializer_class = PatientCommunicationPreferenceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, ReminderWritePermission])
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
@permission_classes([IsAuthenticated, ReminderWritePermission])
def schedule_reminders(request):
    """Manually trigger scheduling of visit reminders."""
    serializer = ScheduleVisitRemindersSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = auto_schedule_reminders()
    return Response(result)

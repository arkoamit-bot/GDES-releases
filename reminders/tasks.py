"""Celery tasks for automated patient reminders.

Requires Celery + Redis broker (see bgddr/celery.py).
SMS/WhatsApp integration stubs are ready for Twilio or local SMS gateway.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.utils import timezone

logger = logging.getLogger("bgddr.reminders")


# --- SMS gateway stubs ---

def send_sms(phone: str, message: str) -> bool:
    """Send SMS via configured gateway.

    Currently a stub. Integrate with:
      - Twilio: from twilio.rest import Client
      - Local GSM modem: AT commands over serial
      - SMS gateway API: POST to gateway endpoint

    Returns True if sent successfully.
    """
    logger.info(f"[SMS stub] To: {phone} | {message}")
    return True


def send_whatsapp(phone: str, message: str) -> bool:
    """Send WhatsApp message via Business API.

    Integrate with Twilio WhatsApp Sandbox or WhatsApp Business API.
    Number must be in international format (e.g. +8801712345678).
    """
    logger.info(f"[WhatsApp stub] To: {phone} | {message}")
    return True


# --- Core sending logic ---

def send_reminder(reminder) -> bool:
    """Send a reminder via its configured channel.

    Returns True if sent successfully.
    """
    patient = reminder.patient
    prefs = getattr(patient, "comm_preferences", None)

    phone = (prefs and prefs.phone) or patient.phone or ""
    email_addr = (prefs and prefs.email) or ""

    # Render template with patient context
    context = Context({
        "patient_name": patient.name or "Patient",
        "patient_id": patient.patient_id,
        "visit_date": "",
        "clinic_address": settings.CLINIC.get("address", ""),
        "clinic_name": settings.CLINIC.get("name_en", ""),
    })

    if reminder.scheduled_visit:
        context["visit_date"] = str(reminder.scheduled_visit.clinic_date
                                    or reminder.scheduled_visit.target_date)

    message = Template(reminder.message).render(context)

    try:
        if reminder.channel == "sms" and phone:
            success = send_sms(phone, message)
        elif reminder.channel == "whatsapp" and phone:
            success = send_whatsapp(phone, message)
        elif reminder.channel == "email" and email_addr:
            send_mail(
                subject=reminder.title,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL
                           if hasattr(settings, "DEFAULT_FROM_EMAIL")
                           else "noreply@bgddr.birdem.org",
                recipient_list=[email_addr],
                fail_silently=False,
            )
            success = True
        else:
            success = False
    except Exception as e:
        logger.error(f"Failed to send reminder {reminder.id}: {e}")
        return False

    return success


# --- Celery tasks ---

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_due_visit_reminders(self):
    """Send reminders for visits due within the next 48 hours."""
    from .models import ReminderSchedule, ReminderStatus, ReminderType
    from datetime import timedelta

    now = timezone.now()
    window_end = now + timedelta(hours=48)

    due_reminders = ReminderSchedule.objects.filter(
        status=ReminderStatus.PENDING,
        reminder_type=ReminderType.FOLLOW_UP,
        scheduled_at__gte=now,
        scheduled_at__lte=window_end,
    ).select_related("patient", "scheduled_visit")

    sent_count = 0
    for reminder in due_reminders:
        try:
            success = send_reminder(reminder)
            if success:
                reminder.status = ReminderStatus.SENT
                reminder.sent_at = timezone.now()
                reminder.save()
                sent_count += 1
            else:
                reminder.status = ReminderStatus.FAILED
                reminder.retry_count += 1
                reminder.save()
        except Exception as e:
            logger.exception(f"Error processing reminder {reminder.id}: {e}")
            try:
                self.retry(countdown=300)
            except self.MaxRetriesExceeded:
                reminder.status = ReminderStatus.FAILED
                reminder.error_message = str(e)
                reminder.save()

    logger.info(f"Sent {sent_count} due visit reminders")
    return {"sent": sent_count, "total": due_reminders.count()}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_overdue_visit_reminders(self):
    """Send reminders for overdue visits."""
    from .models import ReminderSchedule, ReminderStatus, ReminderType

    now = timezone.now()
    yesterday = now - timedelta(days=1)

    overdue_reminders = ReminderSchedule.objects.filter(
        status=ReminderStatus.PENDING,
        reminder_type=ReminderType.FOLLOW_UP,
        scheduled_at__lt=now,
        scheduled_at__gte=yesterday,
    ).select_related("patient", "scheduled_visit")

    sent_count = 0
    for reminder in overdue_reminders:
        try:
            success = send_reminder(reminder)
            if success:
                reminder.status = ReminderStatus.SENT
                reminder.sent_at = timezone.now()
                reminder.save()
                sent_count += 1
            else:
                reminder.status = ReminderStatus.FAILED
                reminder.retry_count += 1
                reminder.save()
        except Exception as e:
            logger.exception(f"Error processing overdue reminder {reminder.id}: {e}")
            try:
                self.retry(countdown=300)
            except self.MaxRetriesExceeded:
                reminder.status = ReminderStatus.FAILED
                reminder.error_message = str(e)
                reminder.save()

    logger.info(f"Sent {sent_count} overdue visit reminders")
    return {"sent": sent_count, "total": overdue_reminders.count()}


@shared_task
def schedule_visit_reminders():
    """Automatically create reminder schedules for upcoming visits.

    Intended to run daily via celery beat.
    """
    from scheduling.models import ScheduledVisit
    from .models import ReminderSchedule, ReminderType, ReminderChannel, ReminderStatus

    now = date.today()
    reminder_window = now + timedelta(days=7)

    upcoming_visits = ScheduledVisit.objects.filter(
        status="scheduled",
        window_start__gte=now,
        window_start__lte=reminder_window,
    ).select_related("patient")

    created = 0
    for visit in upcoming_visits:
        _, was_created = ReminderSchedule.objects.get_or_create(
            patient=visit.patient,
            scheduled_visit=visit,
            reminder_type=ReminderType.FOLLOW_UP,
            defaults={
                "channel": ReminderChannel.SMS,
                "title": "Upcoming clinic visit reminder",
                "message": (
                    "Dear {{patient_name}}, this is a reminder for your upcoming "
                    "clinic visit at {{clinic_name}}. "
                    "Please attend on {{visit_date}}. "
                    "Address: {{clinic_address}}"
                ),
                "scheduled_at": timezone.make_aware(
                    timezone.datetime.combine(
                        visit.window_start,
                        timezone.datetime.min.time(),
                    )
                ),
                "status": ReminderStatus.PENDING,
            }
        )
        if was_created:
            created += 1

    logger.info(f"Created {created} visit reminders")
    return {"created": created}

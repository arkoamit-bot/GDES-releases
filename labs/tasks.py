"""Celery tasks for lab trend detection and alerting."""

from __future__ import annotations

import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger("bgddr.labs")


@shared_task
def detect_lab_trends():
    """Run lab trend detection on all active patients.

    Triggered by celery beat every 6 hours (configured in settings.py).
    Creates reminders for patients with concerning trend alerts.
    """
    from patients.models import Patient
    from .trend_alerts import detect_all_trends

    active_patients = Patient.objects.filter(registration_status__in=[
        "enrolled", "active_followup",
    ])
    total_alerts = 0
    patients_with_alerts = 0

    for patient in active_patients:
        try:
            alerts = detect_all_trends(patient)
            if alerts:
                total_alerts += len(alerts)
                patients_with_alerts += 1
                _create_trend_reminders(patient, alerts)
        except Exception as e:
            logger.error(f"Trend detection failed for {patient.patient_id}: {e}")

    logger.info(f"Lab trend detection: {patients_with_alerts} patients, "
                f"{total_alerts} alerts")
    return {
        "patients_checked": active_patients.count(),
        "patients_with_alerts": patients_with_alerts,
        "total_alerts": total_alerts,
    }


def _create_trend_reminders(patient, alerts):
    """Create reminder entries for concerning lab trends."""
    try:
        from reminders.models import ReminderSchedule, ReminderType, ReminderChannel

        for alert in alerts:
            alert_type = alert.get("type", "")
            if alert_type in ("egfr_decline", "aki",
                              "nephrotic_range", "proteinuria_increase"):
                ReminderSchedule.objects.create(
                    patient=patient,
                    reminder_type=ReminderType.MONITORING,
                    channel=ReminderChannel.SMS,
                    title=f"Lab Alert: {alert_type.replace('_', ' ').title()}",
                    message=(
                        f"Alert for {patient.patient_id}: "
                        f"{alert.get('message', 'Lab trend detected')}. "
                        f"Please review and schedule follow-up."
                    ),
                    scheduled_at=__import__("django.utils.timezone",
                                            fromlist=["now"]).now(),
                )
    except Exception as e:
        logger.error(f"Failed to create trend reminder: {e}")

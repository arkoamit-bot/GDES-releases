"""Celery configuration for async job processing.

Enables background tasks:
- Automated patient reminders (SMS/WhatsApp)
- Lab trend alert processing
- Report generation
- Periodic data backups

Usage:
    celery -A bgddr worker -l INFO --pool=solo  (Windows)
    celery -A bgddr beat -l INFO               (for periodic tasks)
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings")

app = Celery("bgddr")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

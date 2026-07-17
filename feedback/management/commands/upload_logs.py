"""Management command: upload_logs

Manually trigger the error reporting upload to GitHub.

Usage:
    python manage.py upload_logs
    python manage.py upload_logs --status
    python manage.py upload_logs --reset-failed
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Upload pending error reports to GitHub"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status", action="store_true",
            help="Show current telemetry status",
        )
        parser.add_argument(
            "--reset-failed", action="store_true",
            help="Reset all failed uploads back to pending",
        )

    def handle(self, *args, **options):
        from feedback.models import TelemetrySettings, ErrorOccurrence, UploadBatch
        from feedback.services.uploader import run_upload

        settings_obj = TelemetrySettings.load()

        if options["status"]:
            self._show_status(settings_obj)
            return

        if options["reset_failed"]:
            count = ErrorOccurrence.objects.filter(
                queue_state="failed",
            ).update(queue_state="pending")
            self.stdout.write(f"Reset {count} failed uploads to pending")
            return

        if not settings_obj.enabled:
            self.stdout.write(self.style.WARNING("Telemetry is disabled. Enable it in Django admin."))
            return

        if not settings_obj.github_token:
            self.stdout.write(self.style.WARNING(
                "No GitHub token configured. Set it in Django admin → Telemetry Settings."
            ))
            return

        pending = ErrorOccurrence.objects.filter(queue_state="pending").count()
        self.stdout.write(f"Pending errors: {pending}")
        self.stdout.write("Uploading ...")

        result = run_upload(trigger="manual")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Uploaded: {result['uploaded']}, "
            f"Failed: {result['failed']}, Skipped: {result['skipped']}"
        ))

    def _show_status(self, settings_obj):
        from feedback.models import ErrorOccurrence, UploadBatch

        pending = ErrorOccurrence.objects.filter(queue_state="pending").count()
        uploaded = ErrorOccurrence.objects.filter(queue_state="uploaded").count()
        failed = ErrorOccurrence.objects.filter(queue_state="failed").count()
        total = ErrorOccurrence.objects.count()

        last_batch = UploadBatch.objects.first()

        self.stdout.write(f"Telemetry: {'ENABLED' if settings_obj.enabled else 'DISABLED'}")
        self.stdout.write(f"Sync interval: {settings_obj.sync_interval}")
        self.stdout.write(f"GitHub repo: {settings_obj.github_repo}")
        self.stdout.write(f"Token: {'configured' if settings_obj.github_token else 'NOT SET'}")
        self.stdout.write(f"Last upload: {settings_obj.last_upload or 'never'}")
        self.stdout.write(f"Errors: {total} total, {pending} pending, {uploaded} uploaded, {failed} failed")
        if last_batch:
            self.stdout.write(f"Last batch: {last_batch.started_at:%Y-%m-%d %H:%M} ({last_batch.state})")

"""Refresh DrugMaster from the MedEx brand catalogue.

    python manage.py sync_medex_drugs                # scheduled behaviour
    python manage.py sync_medex_drugs --dry-run      # scrape + validate only
    python manage.py sync_medex_drugs --force        # re-import even if unchanged
    python manage.py sync_medex_drugs --check        # report staleness, don't run

The same engine backs celery beat and the desktop scheduler thread; this
command exists so the job can be run, tested and diagnosed by hand.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from prescriptions.services.medex_sync import (SyncLockError, run_sync,
                                               should_sync_now)


class Command(BaseCommand):
    help = ("Periodically refresh the drug database from "
            "https://medex.com.bd/brands (scrape, validate, import).")

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Scrape and validate but do not write to the database",
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Import even when the catalogue content hash is unchanged",
        )
        parser.add_argument(
            "--check", action="store_true",
            help="Report whether a sync is due and exit without scraping",
        )
        parser.add_argument(
            "--ignore-schedule", action="store_true",
            help="Run now even if the configured interval has not elapsed",
        )

    def handle(self, *args, **options):
        from django.conf import settings
        from treatments.models import DrugSyncRun

        if options["check"]:
            last = DrugSyncRun.objects.first()
            due = should_sync_now()
            self.stdout.write(f"enabled    : "
                              f"{settings.DRUG_SYNC_CONFIG['enabled']}")
            self.stdout.write(f"interval   : "
                              f"{settings.DRUG_SYNC_CONFIG['interval_hours']}h")
            self.stdout.write(f"last run   : "
                              f"{last.started_at if last else 'never'}")
            self.stdout.write(f"last state : {last.state if last else '-'}")
            self.stdout.write(f"due now    : {due}")
            return

        if not options["ignore_schedule"] and not should_sync_now():
            self.stdout.write(self.style.WARNING(
                "Not due yet (use --ignore-schedule to run anyway)."))
            return

        try:
            summary = run_sync(
                trigger=("manual" if options["ignore_schedule"]
                         or options["force"] else "scheduled"),
                dry_run=options["dry_run"],
                force=options["force"],
            )
        except SyncLockError as exc:
            raise CommandError(str(exc)) from exc

        style = (self.style.WARNING if summary["state"] == "unchanged"
                 else self.style.SUCCESS)
        self.stdout.write(style(
            f"\nMEDEX SYNC {summary['state'].upper()}: "
            f"pages {summary.get('pages_fetched', 0)}"
            f"/{summary.get('total_pages', 0)}, "
            f"rows {summary.get('rows_scraped', 0)}, "
            f"created {summary.get('generics_created', 0)}, "
            f"brands +{summary.get('brands_added', 0)}, "
            f"merged {summary.get('rows_merged', 0)}, "
            f"deleted {summary.get('rows_deleted', 0)}, "
            f"{summary.get('duration_seconds', 0):.0f}s"))

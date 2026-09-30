"""Prepare a server database: migrate, seed reference data, collect static.

The server counterpart of desktop.launcher.initialise(). Same seeds, same
version-gated knowledge base, without the SQLite snapshot step (PostgreSQL is
backed up by deploy/windows/backup.ps1). Idempotent: safe on every deploy.

    python manage.py server_init
"""
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

FIRST_RUN_SEEDS = ("seed_roles", "seed_labs", "seed_drugs", "seed_studies")
KNOWLEDGE_SEEDS = ("seed_knowledge_base", "seed_v4_knowledge", "seed_clinical_cases",
                   "seed_drug_knowledge", "seed_drug_intelligence", "activate_entries",
                   "build_knowledge_graph")


class Command(BaseCommand):
    help = "Migrate, seed reference data and collect static files (idempotent)."

    def handle(self, *args, **opts):
        failures = []

        def run(cmd, **kwargs):
            try:
                call_command(cmd, verbosity=0, **kwargs)
                self.stdout.write(f"  ok  {cmd}")
            except Exception as exc:          # reported, and counted below
                failures.append(cmd)
                self.stderr.write(f"  FAILED  {cmd}: {exc}")

        self.stdout.write("migrate")
        call_command("migrate", interactive=False, verbosity=0)
        self.stdout.write("  ok  migrate")

        marker = Path(settings.BGDDR_DATA_DIR) / ".server_initialized"
        if not marker.exists():
            self.stdout.write("first-run reference data")
            for cmd in FIRST_RUN_SEEDS:
                run(cmd)

        from knowledge.kb_version import (PACKAGED_KB_VERSION, get_installed_kb_version,
                                          should_seed_kb, stamp_kb_version)
        if should_seed_kb():
            self.stdout.write(f"knowledge base {get_installed_kb_version() or 'none'} "
                              f"-> {PACKAGED_KB_VERSION}")
            before = len(failures)
            for cmd in KNOWLEDGE_SEEDS:
                run(cmd)
            if len(failures) == before:
                stamp_kb_version()
        else:
            self.stdout.write(f"knowledge base up to date (v{get_installed_kb_version()})")

        from prescriptions.drug_bundle import (BUNDLE_VERSION, apply_if_newer,
                                               installed_version)
        self.stdout.write("drug list")
        try:
            if apply_if_newer(log=self.stdout.write, stdout=self.stdout,
                              stderr=self.stderr):
                self.stdout.write(f"  ok  drug list {BUNDLE_VERSION}")
            else:
                self.stdout.write(f"  up to date ({installed_version()})")
        except Exception as exc:          # reported, and counted below
            failures.append("drug list")
            self.stderr.write(f"  FAILED  drug list: {exc}")

        self.stdout.write("collectstatic")
        call_command("collectstatic", interactive=False, verbosity=0)
        self.stdout.write("  ok  collectstatic")

        if failures:
            raise SystemExit(f"server_init: {len(failures)} step(s) failed: {', '.join(failures)}")
        marker.write_text("ok", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS("server_init complete"))

import json
import os
import zipfile
from datetime import datetime
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Count

from feedback.models import (
    ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict,
    AIFailureLog, RuleFailureLog, UserFeedback, WorkflowFeedback,
    PerformanceLog, KnowledgeImprovementSuggestion,
)


IMPORT_MAP = {
    "errors.json": ErrorLog,
    "conflicts.json": ClinicalConflict,
    "performance.json": PerformanceLog,
    "ai_failures.json": AIFailureLog,
    "knowledge_conflicts.json": KnowledgeConflict,
    "user_feedback.json": UserFeedback,
    "workflow_feedback.json": WorkflowFeedback,
    "rule_failures.json": RuleFailureLog,
    "improvement_suggestions.json": KnowledgeImprovementSuggestion,
}


def parse_dt(val):
    if not val or val == "null":
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Import feedback packages for analysis (developer PC)"

    def add_arguments(self, parser):
        parser.add_argument("package", nargs="+", help="Path to feedback ZIP package(s)")
        parser.add_argument("--no-dedup", action="store_true", help="Skip deduplication")
        parser.add_argument("--no-stats", action="store_true", help="Skip summary statistics")

    def handle(self, *args, **options):
        total_imported = defaultdict(int)
        total_skipped = defaultdict(int)

        for pkg_path in options["package"]:
            if not os.path.exists(pkg_path):
                self.stderr.write(self.style.ERROR(f"File not found: {pkg_path}"))
                continue

            self.stdout.write(f"\nProcessing: {os.path.basename(pkg_path)}")
            with zipfile.ZipFile(pkg_path, "r") as zf:
                if "manifest.json" in zf.namelist():
                    manifest = json.loads(zf.read("manifest.json"))
                    self.stdout.write(f"  App version: {manifest.get('app_version', '?')}")
                    self.stdout.write(f"  Exported: {manifest.get('exported_at', '?')}")
                    self.stdout.write(f"  Sections: {', '.join(manifest.get('sections', []))}")

                for filename, model in IMPORT_MAP.items():
                    filepath = f"logs/{filename}"
                    if filepath not in zf.namelist():
                        continue

                    records = json.loads(zf.read(filepath))
                    imported = 0
                    skipped = 0
                    dedup_keys = set()

                    for record in records:
                        if not options.get("no_dedup"):
                            ts = record.get("timestamp") or record.get("created_at")
                            pk_val = record.get("id")
                            dedup = (filename, pk_val, ts)
                            if dedup in dedup_keys:
                                skipped += 1
                                continue
                            dedup_keys.add(dedup)

                        field_map = {}
                        for field in model._meta.get_fields():
                            if field.is_relation or field.name == "id":
                                continue
                            if field.name not in record:
                                continue
                            val = record[field.name]
                            if val == "null" or val is None:
                                continue
                            if isinstance(val, str) and ("time" in field.name or "at" in field.name):
                                parsed = parse_dt(val)
                                if parsed:
                                    val = parsed
                            field_map[field.name] = val

                        try:
                            model.objects.create(**field_map)
                            imported += 1
                        except Exception as e:
                            skipped += 1

                    total_imported[filename] += imported
                    total_skipped[filename] += skipped
                    self.stdout.write(f"  {filename}: {imported} imported, {skipped} skipped")

        self.stdout.write(self.style.SUCCESS(f"\nImport complete"))

        if not options.get("no_stats"):
            self._print_stats()

    def _print_stats(self):
        self.stdout.write(self.style.SUCCESS("\n--- Summary Statistics ---"))
        models = [
            ("Crash Reports", CrashReport),
            ("Clinical Conflicts", ClinicalConflict),
            ("AI Failures", AIFailureLog),
            ("Rule Failures", RuleFailureLog),
            ("Knowledge Conflicts", KnowledgeConflict),
            ("Error Logs", ErrorLog),
            ("User Feedback", UserFeedback),
            ("Workflow Feedback", WorkflowFeedback),
            ("Performance Logs", PerformanceLog),
            ("Improvement Suggestions", KnowledgeImprovementSuggestion),
        ]
        for label, model in models:
            self.stdout.write(f"  {label}: {model.objects.count()}")

        self.stdout.write("\n  Top crash types:")
        for item in CrashReport.objects.values("exception_type").annotate(cnt=Count("id")).order_by("-cnt")[:5]:
            self.stdout.write(f"    {item['exception_type']}: {item['cnt']}")

        self.stdout.write("\n  Top AI disagreements by disease:")
        for item in ClinicalConflict.objects.values("disease").annotate(cnt=Count("id")).order_by("-cnt")[:5]:
            self.stdout.write(f"    {item['disease']}: {item['cnt']}")

        self.stdout.write("\n  Knowledge gaps (disease / failure type):")
        for item in AIFailureLog.objects.values("disease", "failure_type").annotate(cnt=Count("id")).order_by("-cnt")[:10]:
            self.stdout.write(f"    {item['disease']} / {item['failure_type']}: {item['cnt']}")

        self.stdout.write("\n  Top failing rules:")
        for item in RuleFailureLog.objects.values("rule_id", "disease").annotate(cnt=Count("id")).order_by("-cnt")[:5]:
            self.stdout.write(f"    {item['rule_id']} ({item['disease']}): {item['cnt']}")

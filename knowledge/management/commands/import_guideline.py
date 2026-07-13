"""
Import a guideline file (JSON, YAML, CSV, or markdown) into the knowledge base.

    python manage.py import_guideline path/to/file.json --format=json
    python manage.py import_guideline path/to/file.yaml --format=yaml
    python manage.py import_guideline path/to/file.csv --format=csv
    python manage.py import_guideline path/to/file.md  --format=markdown
"""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from knowledge.guideline_import import (
    import_json_guideline, import_csv_guideline,
    import_yaml_guideline, import_markdown_guideline,
)
from knowledge.models import GuidelineDocument, GuidelineSource


class Command(BaseCommand):
    help = "Import rules from a guideline file (JSON, YAML, CSV, markdown)"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Path to the guideline file")
        parser.add_argument("--format", type=str, default="",
                            help="File format: json, yaml, csv, markdown (default: inferred from extension)")
        parser.add_argument("--source-abbr", type=str, default="", help="Source abbreviation (e.g. KDIGO)")
        parser.add_argument("--source-year", type=int, default=0, help="Source version year")
        parser.add_argument("--source-title", type=str, default="", help="Source title")
        parser.add_argument("--doc-id", type=int, default=None,
                            help="GuidelineDocument pk to associate with (for markdown import)")

    def handle(self, *args, **options):
        filepath = options["filepath"]
        if not os.path.exists(filepath):
            raise CommandError(f"File not found: {filepath}")

        fmt = options["format"]
        if not fmt:
            ext = os.path.splitext(filepath)[1].lower()
            ext_map = {".json": "json", ".yaml": "yaml", ".yml": "yaml",
                       ".csv": "csv", ".md": "markdown", ".markdown": "markdown"}
            fmt = ext_map.get(ext, "json")
            self.stdout.write(self.style.WARNING(f"Inferred format: {fmt}"))

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        source_abbr = options.get("source_abbr", "")
        source_year = options.get("source_year", 0)
        source_title = options.get("source_title", "")

        if fmt == "markdown":
            doc_id = options.get("doc_id")
            if doc_id:
                try:
                    doc = GuidelineDocument.objects.get(pk=doc_id)
                    doc.content = content
                    doc.save(update_fields=["content"])
                except GuidelineDocument.DoesNotExist:
                    raise CommandError(f"GuidelineDocument pk={doc_id} not found")
            else:
                if not source_abbr or not source_year:
                    source, _ = GuidelineSource.objects.get_or_create(
                        abbreviation=source_abbr or "UNKNOWN",
                        version_year=source_year or 2025,
                        defaults={"title": source_title or "Imported Guideline",
                                  "effective_date": f"{source_year or 2025}-01-01"},
                    )
                doc = GuidelineDocument.objects.create(
                    title=source_title or os.path.basename(filepath),
                    source=source,
                    document_type=GuidelineDocument.DocType.MARKDOWN,
                    content=content,
                )
            result = import_markdown_guideline(doc)
        elif fmt == "yaml":
            result = import_yaml_guideline(content, source_abbr, source_year, source_title)
        elif fmt == "csv":
            result = import_csv_guideline(content, source_abbr, source_year, source_title)
        else:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise CommandError(f"Invalid JSON: {e}")
            items = data if isinstance(data, list) else data.get("rules", [])
            result = import_json_guideline(items, source_abbr, source_year, source_title)

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {result['created']} created, "
            f"{result['skipped']} skipped, {result['errors']} errors"
        ))
        if result.get("error_details"):
            for err in result["error_details"]:
                self.stdout.write(self.style.ERROR(f"  Error: {err}"))

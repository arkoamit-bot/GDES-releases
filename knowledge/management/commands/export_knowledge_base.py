"""
Export the knowledge base (or a subset) as structured JSON.

    python manage.py export_knowledge_base output.json
    python manage.py export_knowledge_base output.json --disease_id=iga
    python manage.py export_knowledge_base output.json --status=active
"""
import json
from django.core.management.base import BaseCommand
from knowledge.models import KnowledgeBaseEntry


class Command(BaseCommand):
    help = "Export knowledge base entries to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("output", type=str, help="Output file path")
        parser.add_argument("--disease-id", type=str, default=None,
                            help="Only export entries for this disease_id")
        parser.add_argument("--status", type=str, default=None,
                            help="Only export entries with this status (draft, active, retired)")
        parser.add_argument("--pretty", action="store_true", default=True,
                            help="Pretty-print JSON output")

    def handle(self, *args, **options):
        qs = KnowledgeBaseEntry.objects.select_related("source").all()
        if options["disease_id"]:
            qs = qs.filter(disease_id=options["disease_id"])
        if options["status"]:
            qs = qs.filter(status=options["status"])

        entries = []
        for entry in qs:
            entries.append({
                "entry_id": entry.entry_id,
                "disease_id": entry.disease_id,
                "rule_data": entry.rule_data,
                "source": str(entry.source),
                "source_abbreviation": entry.source.abbreviation if entry.source else "",
                "source_year": entry.source.version_year if entry.source else 0,
                "evidence_grade": entry.evidence_grade,
                "rule_type": entry.rule_type,
                "status": entry.status,
                "guideline_chapter": entry.guideline_chapter,
                "guideline_paragraph": entry.guideline_paragraph,
                "guideline_quote": entry.guideline_quote,
                "effective_date": str(entry.effective_date),
                "tags": entry.tags,
            })

        with open(options["output"], "w", encoding="utf-8") as f:
            json.dump({"count": len(entries), "entries": entries}, f,
                      indent=2 if options["pretty"] else None)

        self.stdout.write(self.style.SUCCESS(
            f"Exported {len(entries)} entries to {options['output']}"
        ))

"""
Promote knowledge base entries from DRAFT to ACTIVE status.

    python manage.py activate_entries [--disease_id=iga] [--all]

Without flags, activates all DRAFT entries. Use --disease_id to target a specific
disease, or --all to activate everything.
"""
from django.core.management.base import BaseCommand
from knowledge.models import KnowledgeBaseEntry


class Command(BaseCommand):
    help = "Activate DRAFT knowledge base entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--disease_id", type=str, default=None,
            help="Only activate entries for this disease_id")
        parser.add_argument(
            "--all", action="store_true", dest="activate_all",
            help="Activate all DRAFT entries regardless of disease")

    def handle(self, *args, **options):
        qs = KnowledgeBaseEntry.objects.filter(
            status=KnowledgeBaseEntry.Status.DRAFT)

        if options["disease_id"]:
            qs = qs.filter(disease_id=options["disease_id"])
        elif not options["activate_all"]:
            self.stdout.write(self.style.WARNING(
                "No filter specified. Use --all to activate all DRAFT entries, "
                "or --disease_id=<id> to target a specific disease."))
            return

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No DRAFT entries found."))
            return

        qs.update(status=KnowledgeBaseEntry.Status.ACTIVE)
        self.stdout.write(self.style.SUCCESS(
            f"Activated {count} knowledge base entries."))

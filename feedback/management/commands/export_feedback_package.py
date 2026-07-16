import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from feedback.services import export_feedback_package
from feedback.models import FeedbackExport


class Command(BaseCommand):
    help = "Export a de-identified feedback package ZIP"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, help="Output directory (default: current dir)")
        parser.add_argument("--date-from", type=str, help="Start date YYYY-MM-DD")
        parser.add_argument("--date-to", type=str, help="End date YYYY-MM-DD")

    def handle(self, *args, **options):
        date_from = None
        date_to = None

        if options.get("date_from"):
            date_from = datetime.strptime(options["date_from"], "%Y-%m-%d").date()
        if options.get("date_to"):
            date_to = datetime.strptime(options["date_to"], "%Y-%m-%d").date()

        buf, manifest = export_feedback_package(date_from, date_to)

        out_dir = options.get("output") or os.getcwd()
        os.makedirs(out_dir, exist_ok=True)
        filename = f"GDES_Feedback_{timezone.now():%Y%m%d_%H%M%S}.zip"
        filepath = os.path.join(out_dir, filename)

        with open(filepath, "wb") as f:
            f.write(buf.getvalue())

        FeedbackExport.objects.create(
            filename=filename,
            size_bytes=os.path.getsize(filepath),
            date_from=date_from,
            date_to=date_to,
            included_sections=manifest.get("sections", []),
        )

        self.stdout.write(self.style.SUCCESS(f"Exported: {filepath}"))
        self.stdout.write(f"Sections: {', '.join(manifest.get('sections', []))}")
        counts = manifest.get("record_counts", {})
        for section, count in counts.items():
            self.stdout.write(f"  {section}: {count} records")

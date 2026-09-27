"""
Write the research dataset to a file.

    python manage.py export_dataset                       # -> Exports/ (auto-named CSV)
    python manage.py export_dataset --format xlsx         # -> Exports/ (auto-named XLSX)
    python manage.py export_dataset --out research.csv    # bare name -> Exports/
    python manage.py export_dataset --out C:\\path\\x.xlsx --format xlsx --identified

With no --out, a timestamped file is written into the configured Exports/
folder (settings.EXPORT_DIR). A bare filename is also placed there; an absolute
path (or one with a directory) is honoured as-is.
"""
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from patients.models import Patient

from exports.services.dataset import build_dataset
from exports.services.dictionary import (DICTIONARY_COLUMNS, column_defs,
                                         data_dictionary)
from exports.services.writers import to_csv, to_sav, to_xlsx


class Command(BaseCommand):
    help = "Export the one-row-per-patient research dataset (defaults to Exports/)."

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=["csv", "xlsx", "sav"], default="csv")
        parser.add_argument("--out", default=None,
                            help="Output file. Omit for an auto-named file in Exports/.")
        parser.add_argument("--identified", action="store_true",
                            help="Include direct identifiers (name/phone/reg).")
        parser.add_argument("--study", default=None,
                            help="Study code: restrict to its enrolled patients "
                                 "and add the arm/stratum columns for ITT analysis.")

    def _resolve_out(self, out, fmt, identified, study=None):
        export_dir = Path(getattr(settings, "EXPORT_DIR", settings.BASE_DIR))
        export_dir.mkdir(parents=True, exist_ok=True)
        if not out:
            tag = "identified" if identified else "deidentified"
            if study:
                tag = f"{study}_{tag}"
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return export_dir / f"bgddr_research_{tag}_{stamp}.{fmt}"
        p = Path(out)
        # Bare filename (no directory part) -> drop it into Exports/.
        if not p.is_absolute() and p.parent == Path("."):
            return export_dir / p.name
        return p

    def handle(self, *args, **opts):
        study = opts.get("study")
        out = self._resolve_out(opts["out"], opts["format"], opts["identified"], study)
        cols, rows = build_dataset(Patient.objects.all().order_by("patient_id"),
                                   identified=opts["identified"], study=study)
        if opts["format"] == "xlsx":
            with open(out, "wb") as f:
                f.write(to_xlsx(cols, rows,
                                dictionary=data_dictionary(opts["identified"]),
                                dictionary_columns=DICTIONARY_COLUMNS))
        elif opts["format"] == "sav":
            with open(out, "wb") as f:
                f.write(to_sav(cols, rows,
                               defs=column_defs(opts["identified"], study=bool(study))))
        else:
            with open(out, "w", encoding="utf-8", newline="") as f:
                f.write(to_csv(cols, rows))
        self.stdout.write(self.style.SUCCESS(
            f"Wrote {len(rows)} rows x {len(cols)} columns to {out}."))

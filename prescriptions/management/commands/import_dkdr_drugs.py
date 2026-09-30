"""Bring DKDR's brand catalogue into DrugMaster.

    python manage.py import_dkdr_drugs --dry-run            # report only
    python manage.py import_dkdr_drugs                      # apply
    python manage.py import_dkdr_drugs --dkdr-dir D:/DKDR   # other checkout

DKDR (the sister DKD/CKM registry) vendors two brand sources under
``data/``:

* ``bd_med/medicine.csv``    - MedEx brands, CC0 (allopathic rows only here)
* ``brand_registry/drugs.xls`` - a tab-separated brand list (FORM_DESC,
  GENERIC_NAME, TRADE_NAME, STRENGTH, ...) that carries brands MedEx lacks

Both are reshaped into the CSV that ``import_bddrugbank`` reads and handed
to it, so folding, synonyms, route inference, curated-brand ordering and the
field-length guards behave exactly as they do for the weekly MedEx sync.

Deliberately narrower than a full import:

* **Additive.** Brands and strengths are merged onto existing rows. Nothing
  is deleted or rewritten, and clinical fields (pregnancy, renal, lactation,
  interactions) are not touched.
* **Existing generics only, by default.** DKDR names generics differently
  from MedEx in places ("Alogliptin" vs "Alogliptin Benzoate"), so creating
  rows for unmatched names would seed near-duplicates. Unmatched generics
  are counted and listed in the report instead; ``--create-generics`` opts in.
* **Strengths are normalised** ("30mg" -> "30 mg") and pack descriptions
  ("5's pack") are dropped, so the registry file does not add a second
  spelling of every strength MedEx already holds.
"""
from __future__ import annotations

import csv
import io
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from treatments.models import DrugMaster

from .import_bddrugbank import (MAX_GENERIC, canonical_generic, is_device,
                                norm, split_generic)

DEFAULT_DKDR_DIR = os.environ.get("DKDR_DIR", r"E:\dev\DKDR")

# Header `import_bddrugbank`'s DictReader expects.
CSV_HEADER = ["name", "generic_name", "strength", "therapeutic_class",
              "company", "dosage_form", "medex_url"]

_UNIT_GLUE = re.compile(r"(?<=\d)(?=(?:mg|mcg|g|ml|iu|meq|gm|%)\b)", re.I)
_PACK = re.compile(r"(?:'s\b|\bpack\b|\bstrip\b|\bbox\b|\bpcs?\b)", re.I)
_BRAND_JUNK = re.compile(r"^[\W_]*$")


def clean_strength(raw: str) -> str:
    """'30mg' -> '30 mg'; pack descriptions and empty values -> ''."""
    s = re.sub(r"\s+", " ", (raw or "").strip())
    if not s or _PACK.search(s):
        return ""
    s = _UNIT_GLUE.sub(" ", s)
    # MedEx writes combination strengths as "500 mg+400 IU" (no spaces).
    return re.sub(r"\s*\+\s*", "+", s)


def _read_bd_med(path: Path):
    csv.field_size_limit(10 ** 9)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("type") or "").strip().lower() != "allopathic":
                continue
            yield {
                "name": (row.get("brand name") or "").strip(),
                "generic_name": (row.get("generic") or "").strip(),
                "strength": (row.get("strength") or "").strip(),
                "therapeutic_class": "",
                "company": (row.get("manufacturer") or "").strip(),
                "dosage_form": (row.get("dosage form") or "").strip(),
                "medex_url": "",
            }


def _read_registry(path: Path):
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            yield {
                "name": (row.get("TRADE_NAME") or "").strip(),
                "generic_name": (row.get("GENERIC_NAME") or "").strip(),
                "strength": clean_strength(row.get("STRENGTH")),
                "therapeutic_class": "",
                "company": "",
                "dosage_form": (row.get("FORM_DESC") or "").strip(),
                "medex_url": "",
            }


class Command(BaseCommand):
    requires_system_checks = []
    help = "Merge DKDR's brand catalogue into DrugMaster (additive)."

    def add_arguments(self, parser):
        parser.add_argument("--dkdr-dir", default=DEFAULT_DKDR_DIR,
                            help="DKDR checkout (default: $DKDR_DIR or "
                                 f"{DEFAULT_DKDR_DIR})")
        parser.add_argument("--dry-run", action="store_true",
                            help="Report what would change; write nothing")
        parser.add_argument("--create-generics", action="store_true",
                            help="Also create rows for generics with no match "
                                 "in DrugMaster (default: report them only)")
        parser.add_argument("--skip-registry", action="store_true",
                            help="Use bd_med only, not brand_registry/drugs.xls")
        parser.add_argument("--report", default="",
                            help="Write unmatched generics (with brand counts) "
                                 "to this CSV for review")

    def handle(self, *args, dkdr_dir, dry_run, create_generics,
               skip_registry, report, **options):
        data = Path(dkdr_dir) / "data"
        sources = [("bd_med", data / "bd_med" / "medicine.csv", _read_bd_med)]
        if not skip_registry:
            sources.append(("registry", data / "brand_registry" / "drugs.xls",
                            _read_registry))
        for label, path, _ in sources:
            if not path.exists():
                raise CommandError(f"{label} source not found: {path}")

        existing = set()
        for name in DrugMaster.objects.values_list("generic_name", flat=True):
            existing.add(norm(name))

        kept = []
        seen = set()
        unmatched = Counter()
        unmatched_brands = {}
        per_source = Counter()
        skipped = Counter()
        for label, path, reader in sources:
            for row in reader(path):
                generic, brand = row["generic_name"], row["name"]
                if not generic or not brand or _BRAND_JUNK.match(brand):
                    skipped["blank"] += 1
                    continue
                if is_device(generic):
                    skipped["device"] += 1
                    continue
                base, _route = split_generic(generic)
                canonical = canonical_generic(base)
                if len(canonical) > MAX_GENERIC:
                    skipped["long"] += 1
                    continue
                if norm(canonical) not in existing and not create_generics:
                    unmatched[canonical] += 1
                    unmatched_brands.setdefault(canonical, set()).add(brand)
                    continue
                key = (norm(generic), norm(brand), row["strength"].lower())
                if key in seen:
                    skipped["duplicate"] += 1
                    continue
                seen.add(key)
                kept.append(row)
                per_source[label] += 1

        self.stdout.write(
            f"DKDR rows kept: {len(kept)} ({dict(per_source)}); skipped: "
            f"{dict(skipped)}; rows for {len(unmatched)} generic(s) with no "
            f"DrugMaster match: {sum(unmatched.values())}")

        if report:
            with open(report, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["generic_name", "rows", "brands"])
                for g, n in unmatched.most_common():
                    w.writerow([g, n, len(unmatched_brands[g])])
            self.stdout.write(f"Unmatched generics written to {report}")

        if not kept:
            self.stdout.write("Nothing to import.")
            return

        buf = io.StringIO(newline="")
        w = csv.DictWriter(buf, fieldnames=CSV_HEADER)
        w.writeheader()
        w.writerows(kept)
        with tempfile.TemporaryDirectory() as tmp:
            merged = Path(tmp) / "dkdr_brands.csv"
            merged.write_text(buf.getvalue(), encoding="utf-8", newline="")
            call_command("import_bddrugbank", str(merged), dry_run=dry_run,
                         stdout=self.stdout, stderr=self.stderr)

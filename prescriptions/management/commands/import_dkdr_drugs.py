"""Bring DKDR's brand catalogue into DrugMaster.

    python manage.py import_dkdr_drugs --dry-run            # report only
    python manage.py import_dkdr_drugs                      # apply
    python manage.py import_dkdr_drugs --dkdr-dir D:/DKDR   # other checkout

DKDR (the sister DKD/CKM registry) vendors two brand sources under
``data/``:

* ``bd_med/medicine.csv``    - MedEx brands, CC0 (allopathic rows only here)
* ``bddrugbank/*.zip``       - BDDrugBank ``medex_merged.csv`` (MedEx, Sep 2025),
  the only source that carries a therapeutic class per brand
* ``brand_registry/drugs.xls`` - a tab-separated brand list (FORM_DESC,
  GENERIC_NAME, TRADE_NAME, STRENGTH, ...) that carries brands MedEx lacks

A checkout is not needed on clinic PCs: ``--write-bundle`` saves the rows of
all three sources as one gzipped CSV (``prescriptions/data/dkdr_drugs.csv.gz``,
shipped in the app) and ``--bundle`` imports from that file instead.

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
* **Salt-only variants fold onto the existing row** (``--fold-salts``).
  "Cefixime" is filed under the existing "Cefixime Trihydrate" when the two
  differ only by salt/hydrate words and exactly one existing single-
  ingredient generic qualifies; ambiguous or combination names never fold.
* **Strengths are normalised** ("30mg" -> "30 mg") and pack descriptions
  ("5's pack") are dropped, so the registry file does not add a second
  spelling of every strength MedEx already holds.
"""
from __future__ import annotations

import csv
import gzip
import io
import os
import re
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from treatments.models import DrugMaster

from .import_bddrugbank import (MAX_GENERIC, canonical_generic, is_device,
                                norm, split_generic)

DEFAULT_DKDR_DIR = os.environ.get("DKDR_DIR", r"E:\dev\DKDR")
BUNDLE_PATH = Path(__file__).resolve().parents[2] / "data" / "dkdr_drugs.csv.gz"

# Header `import_bddrugbank`'s DictReader expects.
CSV_HEADER = ["name", "generic_name", "strength", "therapeutic_class",
              "company", "dosage_form", "medex_url"]

_UNIT_GLUE = re.compile(r"(?<=\d)(?=(?:mg|mcg|g|ml|iu|meq|gm|%)\b)", re.I)
_PACK = re.compile(r"(?:'s\b|\bpack\b|\bstrip\b|\bbox\b|\bpcs?\b)", re.I)
_BRAND_JUNK = re.compile(r"^[\W_]*$")


# Words that name a salt / hydrate / ester form, not a different molecule.
SALT_WORDS = frozenset("""
    acetate acetonide anhydrous axetil benzoate besilate besylate bisulfate
    bisulphate bitartrate bromide dihydrochloride oxalate
    calcium carbonate chloride citrate dihydrate disodium dipropionate
    fumarate furoate gluconate hemifumarate hemihydrate hcl hydrobromide
    hydrochloride hydrogen magnesium maleate mesylate methylsulphate
    monohydrate nitrate pamoate pentahydrate phosphate potassium proxetil
    propionate sesquihydrate sodium succinate sulfate sulphate tartrate
    tetrahydrate trihydrate valerate
""".split())


# Trailing registry tags that describe the product, not the molecule:
# "Clobetasol Propionate 0.05% topical", "Tobramycin Eye prep".
_FORM_TAIL = re.compile(
    r"\s+(?:\d+(?:\.\d+)?\s*%\s*)?(?:topical|eye\s*(?:prep|drops?)|"
    r"(?:eye\s*or\s*ear|e/e)\s*prep|ophthalmic|injection|infusion)\s*$",
    re.I)


def strip_form_tail(name: str) -> str:
    """Drop a trailing strength/form tag so the bare molecule can be matched."""
    out = (name or "").strip()
    while True:
        new = _FORM_TAIL.sub("", out).strip()
        if new == out:
            return out
        out = new


def _plain_tokens(name: str):
    """Lower-case word tokens for a plain single-ingredient name, else None."""
    if any(ch in name for ch in "+%()[]/,") or re.search(r"\d", name):
        return None
    return re.findall(r"[a-z]+", name.lower()) or None


def build_salt_index(names):
    """{tokens tuple: name} for existing plain single-ingredient generics."""
    index = {}
    for name in names:
        toks = _plain_tokens(name)
        if toks:
            index.setdefault(tuple(toks), []).append(name)
    return index


def fold_salt_variant(name: str, index):
    """The one existing generic that differs from `name` only by salt words.

    Returns None when `name` is not a plain single ingredient, or when zero
    or several existing rows qualify (ambiguous: never guess a molecule).
    """
    toks = _plain_tokens(strip_form_tail(name))
    if not toks:
        return None
    found = set()
    for etoks, enames in index.items():
        short, long_ = sorted((toks, list(etoks)), key=len)
        if long_[:len(short)] != short or not short:
            continue
        if set(short) <= SALT_WORDS:
            # "Calcium" / "Sodium" name an ion, not a drug moiety: never a
            # salt-variant of "Calcium Carbonate" / "Sodium Chloride".
            continue
        if set(long_[len(short):]) <= SALT_WORDS:
            found.update(enames)
    return next(iter(found)) if len(found) == 1 else None


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


def _read_bddrugbank(path: Path):
    """Stream `medex_merged.csv` out of the BDDrugBank subset zip."""
    csv.field_size_limit(10 ** 9)
    with zipfile.ZipFile(path) as z:
        member = next((n for n in z.namelist()
                       if n.endswith("medex_merged.csv")), None)
        if member is None:
            raise CommandError(f"medex_merged.csv not found in {path}")
        with z.open(member) as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8",
                                                       newline="")):
                yield {
                    "name": (row.get("name") or "").strip(),
                    "generic_name": (row.get("generic_name") or "").strip(),
                    "strength": (row.get("strength") or "").strip(),
                    "therapeutic_class": (row.get("therapeutic_class")
                                          or "").strip(),
                    "company": (row.get("manufacturer") or "").strip(),
                    "dosage_form": (row.get("dosage_form") or "").strip(),
                    "medex_url": "",
                }


def _read_bundle(path: Path):
    """Rows previously saved by ``--write-bundle`` (gzipped, CSV_HEADER)."""
    with gzip.open(path, "rt", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield {k: (row.get(k) or "").strip() for k in CSV_HEADER}


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
        parser.add_argument("--fold-salts", action="store_true",
                            help="File a name that differs from one existing "
                                 "generic only by salt/hydrate words under "
                                 "that generic instead of creating a twin")
        parser.add_argument("--skip-bddrugbank", action="store_true",
                            help="Skip the BDDrugBank zip (bddrugbank/*.zip)")
        parser.add_argument("--skip-registry", action="store_true",
                            help="Use bd_med only, not brand_registry/drugs.xls")
        parser.add_argument("--bundle", nargs="?", const=str(BUNDLE_PATH),
                            default="",
                            help="Import from a saved bundle instead of a "
                                 "DKDR checkout (default: the one shipped in "
                                 "the app)")
        parser.add_argument("--write-bundle", default="",
                            help="Save the source rows to this .csv.gz and "
                                 "exit without touching the database")
        parser.add_argument("--report", default="",
                            help="Write unmatched generics (with brand counts) "
                                 "to this CSV for review")

    def handle(self, *args, dkdr_dir, dry_run, create_generics, fold_salts,
               skip_registry, skip_bddrugbank, report, bundle="",
               write_bundle="", **options):
        data = Path(dkdr_dir) / "data"
        sources = [("bd_med", data / "bd_med" / "medicine.csv", _read_bd_med)]
        if bundle:
            sources = [("bundle", Path(bundle), _read_bundle)]
        elif not skip_bddrugbank:
            zips = sorted((data / "bddrugbank").glob("*.zip"))
            if zips:
                sources.append(("bddrugbank", zips[-1], _read_bddrugbank))
        if not skip_registry and not bundle:
            sources.append(("registry", data / "brand_registry" / "drugs.xls",
                            _read_registry))
        for label, path, _ in sources:
            if not path.exists():
                raise CommandError(f"{label} source not found: {path}")

        if write_bundle:
            self._write_bundle(sources, Path(write_bundle))
            return

        existing = set()
        for name in DrugMaster.objects.values_list("generic_name", flat=True):
            existing.add(norm(name))

        salt_index = build_salt_index(
            DrugMaster.objects.values_list("generic_name", flat=True)
        ) if fold_salts else {}
        folded = Counter()
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
                if fold_salts and norm(canonical) not in existing:
                    target = fold_salt_variant(canonical, salt_index)
                    if target:
                        folded[(canonical, target)] += 1
                        canonical = generic = target
                        row = {**row, "generic_name": target}
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

        if folded:
            self.stdout.write(f"Folded {len(folded)} salt-only name(s) onto "
                              f"existing generics, e.g. "
                              f"{[f'{a} -> {b}' for a, b in list(folded)[:5]]}")

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

    def _write_bundle(self, sources, out: Path):
        """Save every usable source row, deduplicated, for offline import.

        Only filtering that does not depend on the target database happens
        here, so the bundle behaves exactly like the DKDR checkout it came
        from when it is imported into any database.
        """
        seen = set()
        n = 0
        out.parent.mkdir(parents=True, exist_ok=True)
        # mtime=0 keeps the file byte-identical across rebuilds of the same data.
        with open(out, "wb") as raw,                 gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz,                 io.TextIOWrapper(gz, encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CSV_HEADER)
            w.writeheader()
            for _label, path, reader in sources:
                for row in reader(path):
                    generic, brand = row["generic_name"], row["name"]
                    if not generic or not brand or _BRAND_JUNK.match(brand)                             or is_device(generic):
                        continue
                    key = (norm(generic), norm(brand), row["strength"].lower(),
                           row["therapeutic_class"])
                    if key in seen:
                        continue
                    seen.add(key)
                    w.writerow({k: row.get(k, "") for k in CSV_HEADER})
                    n += 1
        self.stdout.write(f"Wrote {n} rows to {out}")

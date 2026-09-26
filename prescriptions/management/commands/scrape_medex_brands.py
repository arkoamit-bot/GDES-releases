"""
Scrape the MedEx (medex.com.bd) brand catalogue into a CSV for
`import_bddrugbank`.

    python manage.py scrape_medex_brands --out Imports/medex_brands.csv

The catalogue at https://medex.com.bd/brands is a single alphabetically
ordered, paginated list (~848 pages x 30 cards). Each card carries the brand
name, strength, generic, company and dosage form - everything
`import_bddrugbank` needs except therapeutic class, which MedEx only publishes
on the per-brand detail page (one request per brand, ~25k requests). Rather
than hammer the site for a field that is only a secondary input to
`classify_drug()`, this scraper leaves `therapeutic_class` blank and the
importer falls back to its generic-name keyword table.

Politeness and resumability:
  - one sequential request at a time with a fixed delay (default 0.4s)
  - exponential backoff on 5xx/429/connection errors
  - every page is appended to the CSV as it lands and recorded in a
    checkpoint file, so an interrupted run continues where it stopped
  - a short TTL on the checkpoint so a stale one cannot silently skip the
    tail of a catalogue that has since grown

Idempotent: re-running with a fresh checkpoint rewrites the CSV from scratch.
"""
from __future__ import annotations

import csv
import html
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

BASE_URL = "https://medex.com.bd/brands"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 BGDDR-DrugDB/1.0 "
    "(research; contact: BIRDEM GN registry)"
)

# One brand card. The three fields the importer consumes are name / strength /
# generic; company and dosage form are kept for provenance and future use.
CARD_RE = re.compile(
    r'(?is)<a href="(?P<url>https://medex\.com\.bd/brands/\d+/[^"]*)"'
    r'\s+class="brand-card">(.*?)</a>'
)
FIELD_RE = {
    "name": re.compile(r'(?is)class="brand-card__name">(.*?)</span>'),
    "strength": re.compile(r'(?is)class="brand-card__strength">(.*?)</div>'),
    "generic": re.compile(r'(?is)class="brand-card__generic">(.*?)</div>'),
    "company": re.compile(r'(?is)class="brand-card__company">(.*?)</div>'),
    "dosage_form": re.compile(r"(?is)<img src='[^']*' alt='(.*?)'"),
}
# A card's strength div is omitted entirely when the product has no stated
# strength (e.g. creams, devices), so treat "missing" and "empty" alike.
# MedEx escapes the query-string separator in its pagination links
# ("?__m_asn=...&amp;page=2"), so anchor on "page=" and scope the search to
# the pagination block to avoid matching brand-card URLs.
PAGINATION_RE = re.compile(r'(?is)<div class="brand-list-pagination">(.*?)</div>')
PAGE_RE = re.compile(r"page=(\d+)")

CSV_FIELDS = [
    "name", "generic_name", "strength", "therapeutic_class",
    "company", "dosage_form", "medex_url",
]


def _clean(raw: str) -> str:
    """Strip tags/entities and collapse whitespace."""
    text = re.sub(r"(?is)<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


class Command(BaseCommand):
    help = "Scrape the MedEx brand catalogue into a CSV for import_bddrugbank."

    def add_arguments(self, parser):
        parser.add_argument(
            "--out", default="Imports/medex_brands.csv",
            help="Output CSV path (default: Imports/medex_brands.csv)",
        )
        parser.add_argument(
            "--delay", type=float, default=0.4,
            help="Seconds to wait between requests (default: 0.4)",
        )
        parser.add_argument(
            "--max-pages", type=int, default=0,
            help="Stop after N pages (0 = all; for smoke-testing)",
        )
        parser.add_argument(
            "--fresh", action="store_true",
            help="Ignore any checkpoint and re-scrape from page 1",
        )
        parser.add_argument(
            "--checkpoint-ttl", type=int, default=12,
            help="Hours after which a checkpoint is considered stale "
                 "(default: 12)",
        )

    # -- HTTP ---------------------------------------------------------------
    def _fetch(self, url: str, delay: float, attempts: int = 4) -> str:
        last = None
        for attempt in range(1, attempts + 1):
            if attempt > 1:
                wait = delay * (2 ** (attempt - 1))
                self.stderr.write(f"    retry {attempt}/{attempts} in "
                                  f"{wait:.1f}s ({last})")
                time.sleep(wait)
            try:
                req = urllib.request.Request(
                    url, headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "text/html,application/xhtml+xml",
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    raw = resp.read()
                return raw.decode("utf-8", "replace")
            except urllib.error.HTTPError as exc:
                last = f"HTTP {exc.code}"
                if exc.code in (429, 500, 502, 503, 504):
                    continue
                raise CommandError(f"{url} -> {last}") from exc
            except Exception as exc:  # noqa: BLE001 - network is best-effort
                last = f"{type(exc).__name__}: {exc}"
        raise CommandError(f"{url} -> giving up after {attempts} attempts "
                           f"({last})")

    # -- parsing ------------------------------------------------------------
    def _parse(self, page_html: str) -> list[dict]:
        rows = []
        for match in CARD_RE.finditer(page_html):
            block = match.group(2)
            row = {}
            for key, pattern in FIELD_RE.items():
                found = pattern.search(block)
                row[key] = _clean(found.group(1)) if found else ""
            row["medex_url"] = match.group("url")
            # The importer keys on generic_name and drops brand names that
            # merely repeat the generic, so normalise the header here.
            row["generic_name"] = row.pop("generic")
            row["therapeutic_class"] = ""
            if row["name"] and row["generic_name"]:
                rows.append(row)
        return rows

    def _last_page(self, page_html: str) -> int:
        block = PAGINATION_RE.search(page_html)
        pages = [int(p) for p in PAGE_RE.findall(block.group(1) if block else "")]
        return max(pages) if pages else 1

    # -- checkpoint ---------------------------------------------------------
    def _load_checkpoint(self, path: Path, ttl_hours: int, fresh: bool):
        if fresh or not path.exists():
            return set(), None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return set(), None
        stamp = datetime.fromisoformat(data["fetched_at"])
        if datetime.now(timezone.utc) - stamp > timedelta(hours=ttl_hours):
            self.stdout.write(self.style.WARNING(
                f"  checkpoint is older than {ttl_hours}h - re-scraping"))
            return set(), None
        return set(data.get("pages_done", [])), data.get("total_pages")

    def _save_checkpoint(self, path: Path, pages, total):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_pages": total,
            "pages_done": sorted(pages),
        }), encoding="utf-8")

    # -- main ---------------------------------------------------------------
    def handle(self, *args, **options):
        delay = options["delay"]
        max_pages = options["max_pages"]
        out = Path(options["out"])
        if not out.is_absolute():
            out = Path(settings.BASE_DIR) / out
        out.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = out.with_suffix(".checkpoint.json")

        # Page 1 also tells us the catalogue length.
        first_html = self._fetch(BASE_URL, delay)
        total = self._last_page(first_html)
        self.stdout.write(f"Catalogue: {total} pages "
                          f"(~{total * 30} brand cards)")

        done, ck_total = self._load_checkpoint(
            checkpoint, options["checkpoint_ttl"], options["fresh"])
        if done and ck_total and ck_total != total:
            self.stdout.write(self.style.WARNING(
                f"  catalogue grew {ck_total} -> {total} pages; "
                f"re-scraping from page 1"))
            done = set()
        if done:
            self.stdout.write(f"  resuming: {len(done)} pages already done")

        # Rows for already-scraped pages are preserved by appending to the
        # existing CSV; a fresh run truncates it first.
        if not done:
            with out.open("w", newline="", encoding="utf-8") as fh:
                csv.DictWriter(fh, fieldnames=CSV_FIELDS).writeheader()

        first_rows = self._parse(first_html)
        written = 0
        with out.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
            if 1 not in done:
                writer.writerows(first_rows)
                written += len(first_rows)
                done.add(1)
            self._save_checkpoint(checkpoint, done, total)

            last = total if not max_pages else min(total, max_pages)
            for page in range(2, last + 1):
                if page in done:
                    continue
                if delay:
                    time.sleep(delay)
                page_html = self._fetch(f"{BASE_URL}?page={page}", delay)
                rows = self._parse(page_html)
                if not rows:
                    # MedEx returns a populated page for every index; an empty
                    # one means the tail moved under us. Stop rather than
                    # write a hole into the CSV.
                    self.stderr.write(self.style.WARNING(
                        f"  page {page} returned 0 cards - stopping"))
                    break
                writer.writerows(rows)
                written += len(rows)
                done.add(page)
                if len(done) % 25 == 0:
                    self._save_checkpoint(checkpoint, done, total)
                    self.stdout.write(
                        f"  page {page}/{last} "
                        f"({written} rows this run)")

        self._save_checkpoint(checkpoint, done, total)
        self.stdout.write(self.style.SUCCESS(
            f"\nSCRAPE COMPLETE:\n"
            f"  pages fetched : {len(done)}/{total}\n"
            f"  rows written  : {written}\n"
            f"  CSV           : {out}\n"
            f"  checkpoint    : {checkpoint}\n\n"
            f"Next:\n"
            f"  python manage.py import_bddrugbank \"{out}\" --dry-run"))

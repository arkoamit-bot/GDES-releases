"""Automated refresh of DrugMaster from the MedEx brand catalogue.

`https://medex.com.bd/brands` is an alphabetically ordered, paginated list
of ~848 pages. This module is the single code path behind every trigger:

    manage.py sync_medex_drugs          # manual
    prescriptions.tasks.sync_medex_drugs # celery beat (server deployments)
    services/scheduler.py               # desktop thread (BGDDR.exe)

Design constraints, in order of importance:

1. **Never damage the database from a bad fetch.** A scrape is validated
   against the last good run (row count, page completion, header present)
   *before* the import is allowed to touch anything. MedEx changing its
   markup, serving a partial page, or the run being cut short all produce a
   truncated CSV, and importing that would strip brands clinicians rely on.

2. **Do nothing when nothing changed.** A content hash over the scraped rows
   means an unchanged catalogue skips the import entirely, so the common
   case costs 848 GETs and zero writes.

3. **One run at a time.** The desktop thread, celery beat and a human at the
   CLI can all fire this. A lock file makes the second one exit instead of
   two runs interleaving deletes against the same table.

4. **Reversible.** Every run records a DrugSyncRun row, scheduled runs take a
   DB backup first, and consolidation commits one group at a time so an
   interrupted merge cannot orphan a FK.
"""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import re
import shutil
import time
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger("bgddr.drug_sync")

# The import command's summary block, e.g. "New generics created : 67".
_SUMMARY_RE = re.compile(r"^\s*([A-Za-z][A-Za-z ]+?)\s*:\s*([0-9]+)\s*$",
                         re.MULTILINE)
_CONSOLIDATE_RE = re.compile(
    r"merge (\d+) group\(s\), delete (\d+) row\(s\), repoint (\d+) FK")


class SyncLockError(RuntimeError):
    """Another sync run already holds the lock."""


class ScrapeRejected(RuntimeError):
    """The scrape failed validation and must not be imported."""


# --------------------------------------------------------------------------
# Locking
# --------------------------------------------------------------------------
def _lock_path() -> Path:
    base = Path(getattr(settings, "BGDDR_DATA_DIR", Path(settings.BASE_DIR)))
    return base / "Imports" / ".medex_sync.lock"


@contextmanager
def acquire_lock(timeout: float = 0.0, stale_after: int = 7200):
    """Exclusive cross-process lock, created atomically.

    `O_CREAT | O_EXCL` is atomic on both Windows and POSIX, so an in-process
    thread and a separate celery worker cannot both win the race. The lock
    records the owning PID so a hard kill (power loss, Task Manager) cannot
    wedge the job forever: a lock older than `stale_after` seconds is
    reclaimed.
    """
    path = _lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            holder, age = "?", 0.0
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                holder = data.get("pid")
                age = time.time() - path.stat().st_mtime
            except (OSError, ValueError):
                pass
            if age > stale_after:
                logger.warning(
                    "Reclaiming stale MedEx sync lock (age %.0fs, pid %s)",
                    age, holder)
                try:
                    path.unlink()
                except OSError:
                    pass
                continue
            if time.time() >= deadline:
                raise SyncLockError(
                    f"another MedEx sync is already running (pid {holder}); "
                    f"lock file: {path}")
            time.sleep(2.0)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"pid": os.getpid(),
                       "started_at": timezone.now().isoformat()}, fh)
        try:
            yield path
        finally:
            try:
                path.unlink()
            except OSError:
                pass
        return


# --------------------------------------------------------------------------
# Schedule
# --------------------------------------------------------------------------
def should_sync_now() -> bool:
    """True when the catalogue is due a refresh.

    Mirrors `feedback.services.uploader.should_sync_now` so both scheduled
    subsystems read the same way. Uses the last *successful* run rather than
    the last attempt, so a week of network failures doesn't reset the clock
    and trigger a retry storm.
    """
    from treatments.models import DrugSyncRun

    cfg = settings.DRUG_SYNC_CONFIG
    if not cfg["enabled"]:
        return False
    if not cfg["interval_hours"]:
        return False
    last = (DrugSyncRun.objects
            .filter(state__in=[DrugSyncRun.State.SUCCESS,
                               DrugSyncRun.State.UNCHANGED])
            .order_by("-finished_at", "-started_at")
            .first())
    if last is None:
        return True
    stamp = last.finished_at or last.started_at
    return timezone.now() - stamp >= timedelta(hours=cfg["interval_hours"])


# --------------------------------------------------------------------------
# Scrape validation
# --------------------------------------------------------------------------
def _hash_csv(path: Path) -> str:
    """Content hash of the scraped rows.

    Hashes the payload only, not the medex_url column, so a cosmetic URL
    change does not trigger a full re-import.
    """
    digest = hashlib.sha256()
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or "generic_name" not in reader.fieldnames:
            raise ScrapeRejected(
                f"{path.name} has no usable header (found {reader.fieldnames})")
        for row in reader:
            digest.update("|".join([
                (row.get("name") or "").strip(),
                (row.get("generic_name") or "").strip(),
                (row.get("strength") or "").strip(),
            ]).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def _count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return sum(1 for row in reader if (row.get("generic_name") or "").strip())


def _validate(path: Path, previous) -> dict:
    """Reject a scrape that would do more harm than good.

    The failure this guards against is subtle: a partially fetched catalogue
    still parses cleanly, and the importer only ever *adds* to a drug, so a
    truncated run looks like success while quietly leaving the tail of the
    alphabet (V-Z brands) un-refreshed.
    """
    if not path.exists():
        raise ScrapeRejected(f"scrape produced no file at {path}")

    rows = _count_rows(path)
    if rows == 0:
        raise ScrapeRejected(f"{path.name} contains 0 usable rows")

    last_good = previous
    if last_good and last_good.rows_scraped:
        ratio = rows / last_good.rows_scraped
        floor = settings.DRUG_SYNC_CONFIG["min_row_ratio"]
        if ratio < floor:
            raise ScrapeRejected(
                f"scraped {rows} rows vs {last_good.rows_scraped} in the last "
                f"good run ({ratio:.0%} < {floor:.0%} floor). MedEx markup may "
                f"have changed, or the run was cut short. Database untouched.")

    return {"rows_scraped": rows, "content_hash": _hash_csv(path)}


# --------------------------------------------------------------------------
# Backup
# --------------------------------------------------------------------------
def _backup_db(reason: str = "pre_drug_sync") -> str | None:
    """Copy the SQLite file aside. Best-effort: a missing backup must not
    abort the sync, but it is logged loudly."""
    from django.db import connection

    if connection.vendor != "sqlite":
        return None
    settings_dict = connection.settings_dict
    name = settings_dict.get("NAME")
    if not name or not Path(name).exists():
        return None
    target_dir = Path(settings.BACKUP_CONFIG["directory"])
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    dest = target_dir / f"db_pre_drug_sync_{stamp}.sqlite3"
    try:
        # SQLite may hold committed data in the WAL; back up through the
        # connection so the copy is consistent.
        with connection.cursor() as cur:
            cur.execute("VACUUM INTO ?", [str(dest)])
    except Exception:
        try:
            shutil.copy2(name, dest)
        except OSError as exc:
            logger.error("Drug sync backup failed: %s", exc)
            return None
    logger.info("Drug sync backup written: %s (%s)", dest, reason)
    return str(dest)


# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------
def _parse_summary(text: str) -> dict:
    """Pull the import command's counters out of its stdout."""
    out = {}
    for label, value in _SUMMARY_RE.findall(text):
        key = re.sub(r"[^a-z]+", "_", label.strip().lower()).strip("_")
        out[key] = int(value)
    m = _CONSOLIDATE_RE.search(text)
    if m:
        out["rows_merged"] = int(m.group(1))
        out["rows_deleted"] = int(m.group(2))
        out["fks_repointed"] = int(m.group(3))
    return out


def run_sync(trigger: str = "scheduled", dry_run: bool = False,
             force: bool = False) -> dict:
    """Scrape, validate and import the MedEx catalogue.

    `force` re-imports even when the content hash is unchanged (used after a
    curated-drugs or SYNONYMS change, where the CSV is identical but the
    merge rules are not). Returns a summary dict; raises on failure so the
    Celery task records a non-zero status.
    """
    from treatments.models import DrugSyncRun

    cfg = settings.DRUG_SYNC_CONFIG
    csv_path = Path(cfg["csv_path"])
    if not csv_path.is_absolute():
        csv_path = Path(settings.BASE_DIR) / csv_path

    started = timezone.now()
    run = DrugSyncRun.objects.create(
        trigger=trigger, state=DrugSyncRun.State.RUNNING)
    summary = {"run_id": run.pk, "trigger": trigger, "dry_run": dry_run,
               "started_at": started}

    def finish(state, **extra):
        run.state = state
        run.finished_at = timezone.now()
        for key, value in extra.items():
            if hasattr(run, key):
                setattr(run, key, value)
        run.detail = {k: v for k, v in extra.items() if not hasattr(run, k)}
        run.save()
        summary.update(extra)
        summary["state"] = state
        summary["duration_seconds"] = run.duration_seconds
        return summary

    try:
        with acquire_lock():
            # --- 1. scrape -------------------------------------------------
            logger.info("MedEx sync: scraping (trigger=%s)", trigger)
            call_command(
                "scrape_medex_brands",
                out=str(csv_path),
                delay=cfg["delay"],
                fresh=True,          # never resume a partial auto-run
                stdout=_Sink(),      # captured, not printed, for the audit row
            )
            checkpoint = csv_path.with_suffix(".checkpoint.json")
            total_pages = pages = 0
            if checkpoint.exists():
                try:
                    data = json.loads(checkpoint.read_text(encoding="utf-8"))
                    total_pages = int(data.get("total_pages") or 0)
                    pages = len(data.get("pages_done") or [])
                except (OSError, ValueError, TypeError):
                    pass

            # --- 2. validate ----------------------------------------------
            previous = (DrugSyncRun.objects
                        .exclude(pk=run.pk)
                        .filter(state__in=[DrugSyncRun.State.SUCCESS,
                                           DrugSyncRun.State.UNCHANGED])
                        .order_by("-finished_at", "-started_at")
                        .first())
            facts = _validate(csv_path, previous)
            logger.info("MedEx sync: validated %s rows over %s/%s pages",
                        facts["rows_scraped"], pages, total_pages)

            base = {"pages_fetched": pages, "total_pages": total_pages,
                    "rows_scraped": facts["rows_scraped"],
                    "content_hash": facts["content_hash"]}

            # --- 3. skip when nothing changed -----------------------------
            unchanged = bool(previous and previous.content_hash
                             and previous.content_hash == facts["content_hash"])
            if unchanged and not force:
                logger.info("MedEx sync: catalogue unchanged, skipping import")
                return finish(DrugSyncRun.State.UNCHANGED, **base)

            # --- 4. backup -------------------------------------------------
            backup = None
            if cfg["backup_before_import"] and not dry_run:
                backup = _backup_db(reason=trigger)

            # --- 5. import -------------------------------------------------
            sink = _Sink()
            call_command("import_bddrugbank", str(csv_path),
                         consolidate=True, dry_run=dry_run, stdout=sink)
            counts = _parse_summary(sink.getvalue())
            logger.info("MedEx sync: import %s", counts)

            return finish(
                DrugSyncRun.State.SUCCESS,
                backup=backup if backup else "",
                **base,
                generics_created=counts.get("new_generics_created", 0),
                generics_updated=counts.get("existing_updated", 0),
                brands_added=counts.get("new_brand_names_added", 0),
                strengths_added=counts.get("new_strengths_added", 0),
                routes_added=counts.get("routes_added", 0),
                rows_merged=counts.get("rows_merged", 0),
                rows_deleted=counts.get("rows_deleted", 0),
                fks_repointed=counts.get("fks_repointed", 0),
            )
    except Exception as exc:
        logger.exception("MedEx sync failed")
        finish(DrugSyncRun.State.FAILED, error=f"{type(exc).__name__}: {exc}")
        raise


class _Sink:
    """Minimal stdout replacement: the import command writes with
    self.stdout.write, so a StringIO keeps the audit trail without spamming
    the console of a scheduled run."""

    def __init__(self):
        import io
        self._buf = io.StringIO()

    def write(self, msg="", *args, **kwargs):
        self._buf.write(str(msg))

    def flush(self):
        pass

    def isatty(self):
        return False

    def getvalue(self):
        return self._buf.getvalue()

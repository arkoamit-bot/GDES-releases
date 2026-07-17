"""Safe migration-on-update for the desktop build (P0-2).

Update day runs migrations against the real patient database. A bad migration
can corrupt or destroy data, and a generic "startup backup" is not enough. This
module wraps `migrate` with: detect unapplied → integrity-check → labeled
pre-migration snapshot → migrate → **restore snapshot on any failure**, logging
the outcome to `migration.log`.

The core file operations use SQLite's online backup API (WAL-safe) and are
injectable/testable off a Windows box.
"""
from __future__ import annotations

import datetime as _dt
import shutil
import sqlite3
import zipfile
from pathlib import Path
from typing import Callable


def integrity_ok(db_path) -> bool:
    """Run PRAGMA integrity_check on a SQLite file. True iff it reports 'ok'."""
    db_path = Path(db_path)
    if not db_path.exists():
        return True  # nothing to corrupt yet (fresh install)
    try:
        con = sqlite3.connect(str(db_path))
        try:
            row = con.execute("PRAGMA integrity_check").fetchone()
            return bool(row) and row[0] == "ok"
        finally:
            con.close()
    except sqlite3.DatabaseError:
        return False


def snapshot_db(db_path, dest_path) -> Path:
    """Consistent single-file copy of a live SQLite DB (WAL-safe backup API)."""
    db_path, dest_path = Path(db_path), Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(str(db_path))
    dst = sqlite3.connect(str(dest_path))
    try:
        src.backup(dst)          # copies committed pages incl. WAL, atomically
    finally:
        dst.close()
        src.close()
    return dest_path


def zip_file(path, zip_path=None) -> Path:
    """Zip a single file next to it (or at zip_path). Returns the zip path."""
    path = Path(path)
    zip_path = Path(zip_path) if zip_path else path.with_suffix(path.suffix + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, arcname=path.name)
    return zip_path


def restore_db(snapshot_path, db_path) -> None:
    """Replace the live DB with a snapshot, removing stale -wal/-shm sidecars."""
    snapshot_path, db_path = Path(snapshot_path), Path(db_path)
    for sidecar in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
        try:
            if sidecar.exists():
                sidecar.unlink()
        except OSError:
            pass
    shutil.copy2(snapshot_path, db_path)


def _log_line(log_path, message: str) -> None:
    try:
        p = Path(log_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # Lightweight rotation: keep migration.log under 5 MB.
        try:
            if p.exists() and p.stat().st_size > 5 * 1024 * 1024:
                p.replace(p.with_suffix(p.suffix + ".1"))
        except OSError:
            pass
        ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(p, "a", encoding="utf-8") as f:
            f.write(f"{ts}  {message}\n")
    except OSError:
        pass


def safe_migrate(
    *,
    db_path,
    backup_dir,
    migrate_fn: Callable[[], None],
    plan_fn: Callable[[], list],
    log_path,
    notify: Callable[[str], None] | None = None,
) -> dict:
    """Run migrate_fn() with snapshot/verify/rollback protection.

    - `plan_fn()` returns the list of unapplied migrations (empty => skip).
    - `migrate_fn()` actually applies them (e.g. call_command("migrate")).
    - On any exception in migrate_fn(), the pre-migration snapshot is restored
      and the exception re-raised.

    Returns a summary dict.
    """
    db_path = Path(db_path)
    backup_dir = Path(backup_dir)
    say = notify or (lambda m: None)

    def record(msg):
        _log_line(log_path, msg)
        say(msg)

    if not integrity_ok(db_path):
        record("ABORT: live DB failed integrity_check. Restore a backup.")
        raise RuntimeError(
            "Database integrity check failed. "
            "Do not migrate a corrupt database — restore a known-good backup first."
        )

    plan = list(plan_fn())
    if not plan:
        record("No unapplied migrations; skipping migrate.")
        return {"skipped": True, "migrated": 0, "snapshot": None}

    snapshot = None
    if db_path.exists():
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot = snapshot_db(db_path, backup_dir / f"premigration_{ts}.sqlite3")
        try:
            zip_file(snapshot)
        except OSError:
            pass
        record(f"Pre-migration snapshot: {snapshot} ({len(plan)} migration(s) pending)")

    try:
        migrate_fn()
    except Exception as exc:  # noqa: BLE001 — must restore, then propagate
        if snapshot is not None:
            restore_db(snapshot, db_path)
            record(f"Migration FAILED; restored pre-migration snapshot. Error: {exc}")
        else:
            record(f"Migration FAILED on a fresh DB (no snapshot to restore). Error: {exc}")
        raise

    record(f"Migration OK ({len(plan)} applied).")
    return {"skipped": False, "migrated": len(plan), "snapshot": str(snapshot) if snapshot else None}


# --- Django wiring (used by the launcher; not imported by the unit tests) ----
def django_unapplied_plan() -> list:
    from django.db import connections
    from django.db.migrations.executor import MigrationExecutor

    conn = connections["default"]
    try:
        executor = MigrationExecutor(conn)
        targets = executor.loader.graph.leaf_nodes()
        return executor.migration_plan(targets)
    except Exception as exc:
        raise RuntimeError(
            "Failed to read migration state from database. "
            "The database may be corrupt or from a newer version. "
            f"Error: {exc}"
        ) from exc


def run_safe_migrate(*, log_path, notify=None) -> dict:
    """Launcher entry point: protect the real `migrate` call."""
    from django.conf import settings
    from django.core.management import call_command

    db_path = settings.DATABASES["default"]["NAME"]
    backup_dir = Path(getattr(settings, "BACKUPS_DIR", Path(db_path).parent / "Backups"))
    return safe_migrate(
        db_path=db_path,
        backup_dir=backup_dir,
        migrate_fn=lambda: call_command("migrate", interactive=False, verbosity=0),
        plan_fn=django_unapplied_plan,
        log_path=log_path,
        notify=notify,
    )

"""
Auto-backup system for BGDDR SQLite database.

Creates timestamped backups of the SQLite database on startup and at
regular intervals. Backups are stored in the configured BACKUP_DIR.

Intended for single-user Windows desktop deployment with OneDrive sync.

Usage:
    from bgddr.backup import create_backup, cleanup_old_backups
    create_backup()  # creates a timestamped backup
"""
import logging
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings

logger = logging.getLogger("bgddr.backup")

# P1-1 tiered ZIP retention (newest N kept per tier).
DEFAULT_TIERS = {"Daily": 7, "Weekly": 8, "Monthly": 12}


def _backup_dir() -> Path:
    """Return the configured backup directory."""
    path = Path(getattr(settings, "BACKUP_CONFIG", {}).get("directory", str(settings.BASE_DIR / "Backups")))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _db_path() -> Path:
    """Return the SQLite database file path."""
    return Path(settings.DATABASES["default"]["NAME"])


def _max_backups() -> int:
    """Return the maximum number of backups to keep."""
    return getattr(settings, "BACKUP_CONFIG", {}).get("max_backups", 30)


def create_backup(reason: str = "scheduled") -> Path | None:
    """Create a timestamped backup of the SQLite database.

    Args:
        reason: Why the backup was triggered (e.g. "startup", "scheduled", "manual")

    Returns:
        Path to the created backup file, or None if the database doesn't exist.
    """
    db_file = _db_path()
    if not db_file.exists():
        logger.warning("Database file not found: %s", db_file)
        return None

    backup_dir = _backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"bgddr_backup_{timestamp}_{reason}.sqlite3"
    backup_path = backup_dir / backup_name

    try:
        shutil.copy2(db_file, backup_path)
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        logger.info(
            "Backup created: %s (%.2f MB) - reason: %s",
            backup_path.name, size_mb, reason
        )
        cleanup_old_backups()
        return backup_path
    except Exception as exc:
        logger.error("Backup failed: %s", exc)
        return None


def cleanup_old_backups() -> int:
    """Delete oldest backups beyond the retention limit.

    Returns:
        Number of backups deleted.
    """
    backup_dir = _backup_dir()
    max_backups = _max_backups()

    backups = sorted(
        [f for f in backup_dir.glob("bgddr_backup_*.sqlite3") if f.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    deleted = 0
    for old in backups[max_backups:]:
        try:
            old.unlink()
            deleted += 1
            logger.info("Removed old backup: %s", old.name)
        except Exception as exc:
            logger.error("Failed to remove old backup %s: %s", old.name, exc)

    return deleted


def list_backups() -> list[dict]:
    """Return a list of existing backups with metadata.

    Returns:
        List of dicts with keys: name, path, size_mb, created, reason
    """
    backup_dir = _backup_dir()
    backups = []
    for f in sorted(backup_dir.glob("bgddr_backup_*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = f.stat()
        # Parse reason from filename: bgddr_backup_YYYYMMDD_HHMMSS_reason.sqlite3
        parts = f.stem.split("_")
        reason = parts[-1] if len(parts) > 3 else "unknown"
        backups.append({
            "name": f.name,
            "path": str(f),
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "reason": reason,
        })
    return backups


def restore_from_backup(backup_path: str | Path) -> bool:
    """Restore the database from a backup file.

    WARNING: This overwrites the current database. Use with caution.

    Args:
        backup_path: Path to the backup file to restore from.

    Returns:
        True if successful, False otherwise.
    """
    backup = Path(backup_path)
    db_file = _db_path()

    if not backup.exists():
        logger.error("Backup file not found: %s", backup)
        return False

    if not _integrity_ok(backup):
        logger.error("Restore aborted: backup file failed integrity_check.")
        return False

    # Create a safety backup of current DB before restore
    create_backup(reason="pre_restore")

    try:
        for sidecar in (db_file, Path(str(db_file) + "-wal"), Path(str(db_file) + "-shm")):
            try:
                if sidecar.exists():
                    sidecar.unlink()
            except OSError:
                pass
        shutil.copy2(backup, db_file)
        if not _integrity_ok(db_file):
            logger.error("Restore FAILED: live DB is corrupt after copy.")
            return False
        logger.info("Database restored from: %s", backup.name)
        return True
    except Exception as exc:
        logger.error("Restore failed: %s", exc)
        return False


# =========================================================================== #
# P1-1 — Tiered ZIP backups (Daily/Weekly/Monthly) + verified restore
# =========================================================================== #
def _tiers() -> dict:
    return getattr(settings, "BACKUP_CONFIG", {}).get("tiers", DEFAULT_TIERS)


def _sqlite_snapshot(db_file: Path, dest: Path) -> Path:
    """WAL-safe consistent copy of a live SQLite DB via the online backup API."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(str(db_file))
    dst = sqlite3.connect(str(dest))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return dest


def _integrity_ok(db_file: Path) -> bool:
    if not Path(db_file).exists():
        return False
    try:
        con = sqlite3.connect(str(db_file))
        try:
            row = con.execute("PRAGMA integrity_check").fetchone()
            return bool(row) and row[0] == "ok"
        finally:
            con.close()
    except sqlite3.DatabaseError:
        return False


def _zip_from(snapshot: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(snapshot, arcname="db.sqlite3")
    return zip_path


def _prune_tier(tier_dir: Path, keep: int) -> int:
    if not tier_dir.is_dir():
        return 0
    zips = sorted(tier_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    deleted = 0
    for old in zips[keep:]:
        try:
            old.unlink()
            deleted += 1
        except OSError as exc:
            logger.error("Failed to prune backup %s: %s", old.name, exc)
    return deleted


def create_tiered_backup(reason: str = "scheduled", now: datetime | None = None) -> dict:
    """Create a verified ZIP backup and roll it into Daily/Weekly/Monthly tiers.

    - A single WAL-safe snapshot is taken, integrity-checked, then zipped into
      Daily/. It is additionally copied into Weekly/ (once per ISO week) and
      Monthly/ (once per calendar month).
    - If the live DB fails integrity_check the backup is skipped and NO pruning
      happens, so a good backup is never rotated out for a bad source.
    - `now` is injectable for testing the tier rollup.

    Returns {tier: Path} for the archives written (empty on skip/failure).
    """
    now = now or datetime.now()
    db_file = _db_path()
    if not db_file.exists():
        logger.warning("Database file not found: %s", db_file)
        return {}
    if not _integrity_ok(db_file):
        logger.error("Live DB failed integrity_check; skipping tiered backup "
                     "(refusing to rotate out a good backup for a corrupt source).")
        return {}

    base = _backup_dir()
    ts = now.strftime("%Y%m%d_%H%M%S")
    made: dict[str, Path] = {}

    with tempfile.TemporaryDirectory() as td:
        snap = _sqlite_snapshot(db_file, Path(td) / "db.sqlite3")

        made["Daily"] = _zip_from(snap, base / "Daily" / f"bgddr_{ts}_{reason}.zip")

        week = now.strftime("%G-W%V")
        weekly_dir = base / "Weekly"
        if not any(week in p.name for p in weekly_dir.glob("*.zip")):
            made["Weekly"] = _zip_from(snap, weekly_dir / f"bgddr_{week}_{ts}.zip")

        month = now.strftime("%Y-%m")
        monthly_dir = base / "Monthly"
        if not any(month in p.name for p in monthly_dir.glob("*.zip")):
            made["Monthly"] = _zip_from(snap, monthly_dir / f"bgddr_{month}_{ts}.zip")

    for tier, keep in _tiers().items():
        _prune_tier(base / tier, keep)

    logger.info("Tiered backup (%s): %s", reason, {k: v.name for k, v in made.items()})
    return made


def restore_zip_backup(zip_path: str | Path) -> bool:
    """Restore the live DB from a ZIP backup, with verification and a safety net.

    Steps: validate zip -> defensive snapshot of the current DB -> extract ->
    integrity_check the extracted DB -> swap it in (removing -wal/-shm). Aborts
    without touching the live DB if the archive is invalid or corrupt.
    """
    zip_path = Path(zip_path)
    db_file = _db_path()
    if not zip_path.exists():
        logger.error("Backup archive not found: %s", zip_path)
        return False

    try:
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(zip_path) as zf:
                names = [n for n in zf.namelist() if n.endswith(".sqlite3") or n == "db.sqlite3"]
                if not names:
                    logger.error("Archive %s contains no .sqlite3 database.", zip_path.name)
                    return False
                extracted = Path(td) / "restored.sqlite3"
                with zf.open(names[0]) as src, open(extracted, "wb") as out:
                    shutil.copyfileobj(src, out)

            if not _integrity_ok(extracted):
                logger.error("Restore aborted: archive DB failed integrity_check.")
                return False

            # Defensive snapshot of the current DB before we overwrite it.
            try:
                create_tiered_backup(reason="pre_restore")
            except Exception as exc:  # never block a restore on the safety copy
                logger.warning("pre-restore backup warning: %s", exc)

            # Close Django connections so the file isn't locked, then swap.
            try:
                from django.db import connections
                connections.close_all()
            except Exception:
                pass
            for sidecar in (db_file, Path(str(db_file) + "-wal"), Path(str(db_file) + "-shm")):
                try:
                    if sidecar.exists():
                        sidecar.unlink()
                except OSError:
                    pass
            shutil.copy2(extracted, db_file)

            if not _integrity_ok(db_file):
                logger.error("Restore FAILED: live DB is corrupt after swap.")
                return False
        logger.info("Database restored from archive: %s", zip_path.name)
        return True
    except Exception as exc:
        logger.error("Restore failed: %s", exc)
        return False

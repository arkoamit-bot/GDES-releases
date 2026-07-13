"""P0 desktop-hardening unit tests (no Django DB needed).

Covers:
  P0-1  cloud-synced-DB guard + local data-dir resolver
  P0-2  safe migrate: snapshot/verify/restore-on-failure
  P0-4  single-instance guard
"""
import sqlite3
from pathlib import Path

import pytest

from desktop import hardening, safe_migrate


# --------------------------------------------------------------------------- #
# P0-1 — cloud-synced path guard
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("path,expected_hit", [
    (r"C:\Users\x\OneDrive\BGDDR\db.sqlite3", True),
    (r"C:\Users\x\OneDrive - Hospital\BGDDR\db.sqlite3", True),
    (r"C:\Users\x\Dropbox\BGDDR\db.sqlite3", True),
    (r"C:\Users\x\Google Drive\db.sqlite3", True),
    (r"C:\Users\x\iCloudDrive\db.sqlite3", True),
    (r"C:\Users\x\AppData\Local\GDES\Data\db.sqlite3", False),
    (r"C:\BGDDR\db.sqlite3", False),
    ("/home/user/.gdes/Data/db.sqlite3", False),
])
def test_cloud_sync_segment(path, expected_hit):
    seg = hardening.cloud_sync_segment(path)
    assert (seg is not None) == expected_hit


def test_assert_db_path_local_raises_on_synced():
    with pytest.raises(RuntimeError):
        hardening.assert_db_path_local(r"C:\Users\x\OneDrive\db.sqlite3", allow_synced=False)


def test_assert_db_path_local_ok_on_local():
    hardening.assert_db_path_local(r"C:\Users\x\AppData\Local\GDES\Data\db.sqlite3", allow_synced=False)


def test_assert_db_path_local_escape_hatch():
    # Explicit override must not raise even for a synced path.
    hardening.assert_db_path_local(r"C:\Users\x\OneDrive\db.sqlite3", allow_synced=True)


def test_resolve_local_data_dir_is_local_and_writable():
    d = hardening.resolve_local_data_dir()
    assert d.exists()
    assert hardening.cloud_sync_segment(d) is None
    probe = d / ".pytest_write"
    probe.write_text("ok", encoding="utf-8")
    probe.unlink()


# --------------------------------------------------------------------------- #
# P0-4 — single-instance guard
# --------------------------------------------------------------------------- #
def test_single_instance_blocks_second_bind():
    port = 8791
    s1 = hardening.acquire_single_instance("127.0.0.1", port)
    try:
        with pytest.raises(hardening.SingleInstanceError):
            hardening.acquire_single_instance("127.0.0.1", port)
    finally:
        s1.close()
    # After release the port is free again.
    s2 = hardening.acquire_single_instance("127.0.0.1", port)
    s2.close()


# --------------------------------------------------------------------------- #
# P0-2 — safe migrate: snapshot / verify / restore
# --------------------------------------------------------------------------- #
def _make_db(path: Path, value: str):
    con = sqlite3.connect(str(path))
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO t (v) VALUES (?)", (value,))
    con.commit()
    con.close()


def _read(path: Path):
    con = sqlite3.connect(str(path))
    try:
        return con.execute("SELECT v FROM t").fetchall()
    finally:
        con.close()


def test_snapshot_and_restore_roundtrip(tmp_path):
    db = tmp_path / "db.sqlite3"
    _make_db(db, "original")
    snap = safe_migrate.snapshot_db(db, tmp_path / "backups" / "snap.sqlite3")
    assert snap.exists()
    # mutate the live DB, then restore
    con = sqlite3.connect(str(db)); con.execute("UPDATE t SET v='mutated'"); con.commit(); con.close()
    assert _read(db) == [("mutated",)]
    safe_migrate.restore_db(snap, db)
    assert _read(db) == [("original",)]


def test_integrity_ok_true_for_good_db(tmp_path):
    db = tmp_path / "db.sqlite3"
    _make_db(db, "x")
    assert safe_migrate.integrity_ok(db) is True


def test_safe_migrate_skips_when_no_plan(tmp_path):
    db = tmp_path / "db.sqlite3"; _make_db(db, "x")
    called = {"migrate": False}
    def migrate_fn(): called["migrate"] = True
    res = safe_migrate.safe_migrate(
        db_path=db, backup_dir=tmp_path / "b",
        migrate_fn=migrate_fn, plan_fn=lambda: [],
        log_path=tmp_path / "migration.log",
    )
    assert res["skipped"] is True
    assert called["migrate"] is False


def test_safe_migrate_rolls_back_on_failure(tmp_path):
    db = tmp_path / "db.sqlite3"; _make_db(db, "original")

    def bad_migrate():
        con = sqlite3.connect(str(db)); con.execute("UPDATE t SET v='half_migrated'"); con.commit(); con.close()
        raise RuntimeError("boom in migration")

    with pytest.raises(RuntimeError, match="boom"):
        safe_migrate.safe_migrate(
            db_path=db, backup_dir=tmp_path / "backups",
            migrate_fn=bad_migrate, plan_fn=lambda: [("fake_migration", False)],
            log_path=tmp_path / "migration.log",
        )
    # The live DB was restored byte-for-value to its pre-migration state.
    assert _read(db) == [("original",)]
    # And a pre-migration snapshot + log line were written.
    assert list((tmp_path / "backups").glob("premigration_*.sqlite3"))
    assert (tmp_path / "migration.log").read_text(encoding="utf-8").strip()


def test_safe_migrate_success_records_log(tmp_path):
    db = tmp_path / "db.sqlite3"; _make_db(db, "x")
    def good_migrate():
        con = sqlite3.connect(str(db)); con.execute("INSERT INTO t (v) VALUES ('added')"); con.commit(); con.close()
    res = safe_migrate.safe_migrate(
        db_path=db, backup_dir=tmp_path / "backups",
        migrate_fn=good_migrate, plan_fn=lambda: [("m1", False)],
        log_path=tmp_path / "migration.log",
    )
    assert res["migrated"] == 1
    assert res["snapshot"] and Path(res["snapshot"]).exists()
    assert ("added",) in _read(db)
    assert "Migration OK" in (tmp_path / "migration.log").read_text(encoding="utf-8")

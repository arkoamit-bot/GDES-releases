"""P1-1 tiered ZIP backup + restore tests."""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from bgddr import backup as bk


def _make_db(p: Path, value: str):
    con = sqlite3.connect(str(p))
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO t (v) VALUES (?)", (value,))
    con.commit()
    con.close()


def _read(p: Path):
    con = sqlite3.connect(str(p))
    try:
        return con.execute("SELECT v FROM t").fetchall()
    finally:
        con.close()


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = tmp_path / "db.sqlite3"
    _make_db(db, "original")
    bdir = tmp_path / "Backups"
    bdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(bk, "_db_path", lambda: db)
    monkeypatch.setattr(bk, "_backup_dir", lambda: bdir)
    return db, bdir


def test_tiered_backup_creates_all_tiers(env):
    db, bdir = env
    made = bk.create_tiered_backup(reason="test")
    assert set(made) == {"Daily", "Weekly", "Monthly"}
    for tier in ("Daily", "Weekly", "Monthly"):
        zips = list((bdir / tier).glob("*.zip"))
        assert len(zips) == 1, tier


def test_weekly_and_monthly_rollup_once_per_period(env):
    db, bdir = env
    base = datetime(2026, 7, 1, 9, 0, 0)
    # two backups the SAME ISO week -> 2 daily, 1 weekly, 1 monthly
    bk.create_tiered_backup(now=base)
    bk.create_tiered_backup(now=base + timedelta(hours=6))
    assert len(list((bdir / "Daily").glob("*.zip"))) == 2
    assert len(list((bdir / "Weekly").glob("*.zip"))) == 1
    assert len(list((bdir / "Monthly").glob("*.zip"))) == 1
    # next week, same month -> new weekly, still one monthly
    bk.create_tiered_backup(now=base + timedelta(days=8))
    assert len(list((bdir / "Weekly").glob("*.zip"))) == 2
    assert len(list((bdir / "Monthly").glob("*.zip"))) == 1


def test_daily_retention_prunes_to_seven(env):
    db, bdir = env
    base = datetime(2026, 1, 1, 9, 0, 0)
    for i in range(10):
        bk.create_tiered_backup(now=base + timedelta(days=i))
    # DEFAULT/settings Daily retention is 7
    assert len(list((bdir / "Daily").glob("*.zip"))) == 7


def test_restore_zip_roundtrip(env):
    db, bdir = env
    made = bk.create_tiered_backup(reason="test")
    daily_zip = made["Daily"]
    # mutate live DB
    con = sqlite3.connect(str(db)); con.execute("UPDATE t SET v='mutated'"); con.commit(); con.close()
    assert _read(db) == [("mutated",)]
    assert bk.restore_zip_backup(daily_zip) is True
    assert _read(db) == [("original",)]


def test_corrupt_source_is_skipped(env):
    db, bdir = env
    db.write_bytes(b"not a database at all")
    made = bk.create_tiered_backup(reason="test")
    assert made == {}
    # nothing written
    assert not list((bdir / "Daily").glob("*.zip"))


def test_restore_rejects_corrupt_archive(env, tmp_path):
    db, bdir = env
    import zipfile
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("db.sqlite3", b"garbage not sqlite")
    assert bk.restore_zip_backup(bad) is False
    # live DB untouched
    assert _read(db) == [("original",)]

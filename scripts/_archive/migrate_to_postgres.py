"""
Migrate BGDDR data from SQLite to PostgreSQL.

Prerequisites:
    pip install psycopg

Usage:
    # 1. Set up PostgreSQL database first (see DEPLOYMENT.md)
    # 2. Run migrations to create schema:
    #    DJANGO_SETTINGS_MODULE=bgddr.settings_prod python manage.py migrate
    # 3. Copy data:
    #    python migrate_to_postgres.py

This script copies all rows from SQLite tables to PostgreSQL.
It handles auto-increment sequence reset after load.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration -- EDIT THESE VALUES
# ---------------------------------------------------------------------------
SQLITE_PATH = Path(r"E:\OneDrive\Project Kimi\bgddr\db.sqlite3")
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB = "bgddr"
PG_USER = "bgddr"
PG_PASSWORD = "your_password_here"  # <-- CHANGE THIS

# Tables to migrate (order matters for FK constraints)
TABLES = [
    # Django auth + contenttypes (usually already seeded by migrate, but include just in case)
    "auth_group",
    "auth_user",
    "auth_group_permissions",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_content_type",
    "django_session",
    "django_admin_log",
    # Registry apps
    "patients_patient",
    "baseline_baselineassessment",
    "encounters_clinicalencounter",
    "encounters_clinicalevent",
    "labs_labtest",
    "labs_labpanel",
    "labs_labpanel_tests",
    "labs_laborder",
    "labs_laborderitem",
    "labs_labresult",
    "pathology_biopsy",
    "pathology_gndiagnosis",
    "pathology_iganscore",
    "pathology_fsgspathology",
    "pathology_membranouspathology",
    "pathology_lupuspathology",
    "pathology_pathologyreview",
    "treatments_drugmaster",
    "treatments_treatmentexposure",
    "prescriptions_prescription",
    "prescriptions_prescriptionitem",
    "analytics_patientoutcome",
    "audit_auditlog",
    "audit_consentrecord",
    "studies_study",
    "studies_studyenrollment",
    "safety_adverseevent",
    "scheduling_scheduledvisit",
    "biomarkers_biomarkerkinetics",
    "api_token",
    # Users app (if data exists)
    "users_userprofile",
    "users_invitation",
]

# Some tables may not exist in older versions of the DB; skip them gracefully
OPTIONAL_TABLES = {
    "users_userprofile",
    "users_invitation",
}


def _connect_pg():
    try:
        import psycopg
    except ImportError:
        print("ERROR: psycopg is not installed.")
        print("Run: pip install psycopg")
        sys.exit(1)

    return psycopg.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB,
        user=PG_USER, password=PG_PASSWORD,
    )


def _get_columns(cursor, table: str) -> list[str]:
    cursor.execute(f"SELECT * FROM {table} LIMIT 0")
    return [desc[0] for desc in cursor.description]


def migrate():
    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = _connect_pg()
    pg_cur = pg_conn.cursor()

    total_rows = 0

    for table in TABLES:
        # Check if table exists in SQLite
        sqlite_cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,))
        if not sqlite_cur.fetchone():
            if table in OPTIONAL_TABLES:
                print(f"  SKIP {table} (not in SQLite)")
                continue
            print(f"  ERROR: {table} not found in SQLite!")
            continue

        # Check if table exists in PostgreSQL
        pg_cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
            (table,))
        if not pg_cur.fetchone():
            print(f"  SKIP {table} (not in PostgreSQL schema -- run migrate first)")
            continue

        # Get columns from SQLite
        sqlite_cols = _get_columns(sqlite_cur, table)
        # Get columns from PostgreSQL
        pg_cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",
            (table,))
        pg_cols = [r[0] for r in pg_cur.fetchall()]

        # Intersection of columns (handle schema differences)
        common_cols = [c for c in sqlite_cols if c in pg_cols]
        if not common_cols:
            print(f"  SKIP {table} (no common columns)")
            continue

        col_str = ", ".join(f'"{c}"' for c in common_cols)
        placeholders = ", ".join(["%s"] * len(common_cols))

        # Read from SQLite
        sqlite_cur.execute(f"SELECT {col_str} FROM {table}")
        rows = sqlite_cur.fetchall()

        if not rows:
            print(f"  {table}: 0 rows")
            continue

        # Insert into PostgreSQL
        pg_cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        insert_sql = f'INSERT INTO "{table}" ({col_str}) VALUES ({placeholders})'

        # Batch insert in chunks of 1000
        chunk = []
        for row in rows:
            chunk.append(tuple(row))
            if len(chunk) >= 1000:
                pg_cur.executemany(insert_sql, chunk)
                chunk = []
        if chunk:
            pg_cur.executemany(insert_sql, chunk)

        print(f"  {table}: {len(rows)} rows copied")
        total_rows += len(rows)

    # Reset sequences for auto-increment tables
    print("\nResetting sequences...")
    seq_tables = [
        "auth_user", "patients_patient", "baseline_baselineassessment",
        "encounters_clinicalencounter", "encounters_clinicalevent",
        "labs_labtest", "labs_labpanel", "labs_laborder", "labs_laborderitem",
        "labs_labresult", "pathology_biopsy", "pathology_gndiagnosis",
        "pathology_pathologyreview", "treatments_drugmaster",
        "treatments_treatmentexposure", "prescriptions_prescription",
        "prescriptions_prescriptionitem", "analytics_patientoutcome",
        "audit_auditlog", "studies_study", "studies_studyenrollment",
        "safety_adverseevent", "scheduling_scheduledvisit",
        "biomarkers_biomarkerkinetics",
    ]
    for tbl in seq_tables:
        try:
            pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 0) + 1, false)")
        except Exception:
            pass  # table may not have serial id

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()

    print(f"\n{'='*60}")
    print(f"Migration complete: {total_rows} total rows copied")
    print(f"{'='*60}")
    print("Next steps:")
    print("  1. Run: DJANGO_SETTINGS_MODULE=bgddr.settings_prod python manage.py migrate")
    print("  2. Run: DJANGO_SETTINGS_MODULE=bgddr.settings_prod python manage.py seed_roles")
    print("  3. Run: DJANGO_SETTINGS_MODULE=bgddr.settings_prod python manage.py createsuperuser")
    print("  4. Start the server with production settings")


if __name__ == "__main__":
    migrate()

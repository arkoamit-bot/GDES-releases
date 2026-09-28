"""
Standalone patient registry validator — reads db.sqlite3 directly.
Reports duplicates, missing critical fields, and coverage gaps.
Optionally writes a CSV of flagged patients for manual review.

    python inspect_db.py
    python inspect_db.py --csv patient_issues.csv

Exit code 1 if critical duplicates exist (useful for CI/pre-deploy gate).
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from pathlib import Path

DB_PATH = Path(r"E:\OneDrive\Project Kimi\bgddr\db.sqlite3")


def validate(threshold: int = 2, out_csv: str = "") -> int:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all patients
    cursor.execute("""
        SELECT id, patient_id, name, hospital_id, phone, sex, dob,
               enrollment_date, primary_diagnosis
        FROM patients_patient
    """)
    patients = [dict(r) for r in cursor.fetchall()]
    total = len(patients)

    if total == 0:
        print("No patients in the database.")
        return 0

    # Count per patient: baseline, encounters, labs, exposures
    def _count(table: str, col: str) -> dict[int, int]:
        cursor.execute(f"SELECT {col}, COUNT(*) as n FROM {table} GROUP BY {col}")
        return {r[col]: r["n"] for r in cursor.fetchall()}

    baseline_counts = _count("baseline_baselineassessment", "patient_id")
    encounter_counts = _count("encounters_clinicalencounter", "patient_id")
    lab_counts = _count("labs_labresult", "patient_id")
    exposure_counts = _count("treatments_treatmentexposure", "patient_id")

    # Duplicate detection
    seen_names = Counter()
    seen_phones = Counter()
    seen_hosp = Counter()
    for p in patients:
        if p["name"]:
            seen_names[p["name"].strip().lower()] += 1
        if p["phone"]:
            seen_phones[p["phone"].strip()] += 1
        if p["hospital_id"]:
            seen_hosp[p["hospital_id"].strip().lower()] += 1

    dup_names = {n for n, c in seen_names.items() if c > 1}
    dup_phones = {p for p, c in seen_phones.items() if c > 1}
    dup_hosp = {h for h, c in seen_hosp.items() if c > 1}

    issues: list[dict] = []
    for p in patients:
        flags = []
        pid = p["id"]
        name_key = (p["name"] or "").strip().lower()
        phone_key = (p["phone"] or "").strip()
        hosp_key = (p["hospital_id"] or "").strip().lower()

        if name_key in dup_names:
            flags.append("duplicate_name")
        if phone_key in dup_phones:
            flags.append("duplicate_phone")
        if hosp_key in dup_hosp:
            flags.append("duplicate_hospital_id")

        if not p["name"] or not p["name"].strip():
            flags.append("missing_name")
        if not p["dob"]:
            flags.append("missing_dob")
        if not p["sex"]:
            flags.append("missing_sex")
        if not p["enrollment_date"]:
            flags.append("missing_enrollment_date")
        if not p["primary_diagnosis"]:
            flags.append("missing_diagnosis")

        has_baseline = baseline_counts.get(pid, 0) > 0
        n_encounters = encounter_counts.get(pid, 0)
        n_labs = lab_counts.get(pid, 0)
        n_exposures = exposure_counts.get(pid, 0)

        if not has_baseline:
            flags.append("no_baseline")
        if n_encounters == 0:
            flags.append("no_encounters")
        if n_encounters < threshold:
            flags.append(f"few_encounters({n_encounters})")
        if n_labs == 0:
            flags.append("no_labs")

        if flags:
            issues.append({
                "patient_id": p["patient_id"],
                "name": p["name"],
                "hospital_id": p["hospital_id"] or "",
                "phone": p["phone"] or "",
                "flags": "; ".join(flags),
                "has_baseline": has_baseline,
                "n_encounters": n_encounters,
                "n_labs": n_labs,
                "n_exposures": n_exposures,
            })

    # Report
    print("=" * 60)
    print("BGDDR PATIENT VALIDATION REPORT")
    print("=" * 60)
    print(f"Total patients: {total}")
    print(f"Flagged patients: {len(issues)}")
    if issues:
        pct = round(len(issues) / total * 100, 1)
        print(f"  -> {pct}% of patients need review")
    print()

    # Summary by flag type
    all_flags = [f for i in issues for f in i["flags"].split("; ")]
    flag_counts = Counter(all_flags)
    if flag_counts:
        print("Flag breakdown:")
        for flag, count in flag_counts.most_common():
            print(f"  {flag:45s} {count:4d}")
        print()

    # Top 10 most-sparse
    if issues:
        print("Top 10 most-sparse flagged patients:")
        sorted_issues = sorted(issues, key=lambda x: (x["n_encounters"], x["n_labs"]))
        for i in sorted_issues[:10]:
            print(f"  {i['patient_id']:12s} | {i['name'][:28]:28s} | "
                  f"enc={i['n_encounters']:2d} labs={i['n_labs']:4d} | {i['flags'][:60]}")
        print()

    # CSV export
    if out_csv and issues:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=issues[0].keys())
            writer.writeheader()
            writer.writerows(issues)
        print(f"Wrote {len(issues)} flagged rows to {out_csv}")
    elif out_csv:
        print(f"No issues — CSV not written.")

    # Non-zero exit if duplicates
    critical_dupes = any("duplicate" in i["flags"] for i in issues)
    conn.close()

    if critical_dupes:
        print()
        print("CRITICAL: Duplicate patients detected. Resolve before production.")
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate BGDDR patient registry.")
    parser.add_argument("--csv", dest="out_csv", default="",
                        help="Write flagged patients to CSV.")
    parser.add_argument("--threshold", type=int, default=2,
                        help="Min encounter count to be 'active' (default 2).")
    args = parser.parse_args()
    sys.exit(validate(args.threshold, args.out_csv))

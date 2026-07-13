"""
Validate the imported patient registry: deduplication, missing critical fields,
and data-coverage gaps. Run after any bulk import.

    python manage.py validate_patients

Outputs a console report and optional CSV of flagged patients for manual review.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter

from django.core.management.base import BaseCommand

from patients.models import Patient


class Command(BaseCommand):
    help = "Validate patient registry: dedupe, missing fields, coverage gaps."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv", dest="out_csv", default="",
            help="Write a CSV of flagged patients to this path.")
        parser.add_argument(
            "--threshold", type=int, default=2,
            help="Min encounter count to be considered 'active' (default 2).")

    def handle(self, *args, **options):
        threshold = options["threshold"]
        qs = Patient.objects.all()
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No patients in the database."))
            return

        issues: list[dict] = []

        # 1. Duplicate detection (exact + fuzzy)
        seen_names: Counter = Counter()
        seen_phones: Counter = Counter()
        seen_hosp: Counter = Counter()
        for p in qs:
            if p.name:
                seen_names[p.name.strip().lower()] += 1
            if p.phone:
                seen_phones[p.phone.strip()] += 1
            if p.hospital_id:
                seen_hosp[p.hospital_id.strip().lower()] += 1

        dup_names = {n for n, c in seen_names.items() if c > 1}
        dup_phones = {p for p, c in seen_phones.items() if c > 1}
        dup_hosp = {h for h, c in seen_hosp.items() if c > 1}

        for p in qs:
            flags = []
            # Duplicate check
            name_key = (p.name or "").strip().lower()
            phone_key = (p.phone or "").strip()
            hosp_key = (p.hospital_id or "").strip().lower()
            if name_key in dup_names:
                flags.append("duplicate_name")
            if phone_key in dup_phones:
                flags.append("duplicate_phone")
            if hosp_key in dup_hosp:
                flags.append("duplicate_hospital_id")

            # Critical fields missing
            if not p.name or not p.name.strip():
                flags.append("missing_name")
            if not p.dob:
                flags.append("missing_dob")
            if not p.sex:
                flags.append("missing_sex")
            if not p.enrollment_date:
                flags.append("missing_enrollment_date")
            if not p.primary_diagnosis:
                flags.append("missing_diagnosis")

            # Data-coverage gaps
            has_baseline = hasattr(p, "baseline") and p.baseline is not None
            has_encounters = p.encounters.exists()
            n_encounters = p.encounters.count()
            n_labs = p.lab_results.count()
            n_exposures = p.exposures.count()

            if not has_baseline:
                flags.append("no_baseline")
            if not has_encounters:
                flags.append("no_encounters")
            if n_encounters < threshold:
                flags.append(f"few_encounters({n_encounters})")
            if n_labs == 0:
                flags.append("no_labs")

            if flags:
                issues.append({
                    "patient_id": p.patient_id,
                    "name": p.name,
                    "hospital_id": p.hospital_id or "",
                    "phone": p.phone or "",
                    "flags": "; ".join(flags),
                    "has_baseline": has_baseline,
                    "n_encounters": n_encounters,
                    "n_labs": n_labs,
                    "n_exposures": n_exposures,
                })

        # Report
        self.stdout.write(self.style.HTTP_INFO(f"=== Patient validation report ==="))
        self.stdout.write(f"Total patients: {total}")
        self.stdout.write(f"Flagged patients: {len(issues)}")
        if issues:
            pct = round(len(issues) / total * 100, 1)
            self.stdout.write(self.style.WARNING(f"  -> {pct}% of patients need review"))

        # Summary by flag type
        all_flags = [f for i in issues for f in i["flags"].split("; ")]
        flag_counts = Counter(all_flags)
        if flag_counts:
            self.stdout.write("\nFlag breakdown:")
            for flag, count in flag_counts.most_common():
                self.stdout.write(f"  {flag}: {count}")

        # Top 10 most-sparse patients
        if issues:
            self.stdout.write("\nTop 10 most-sparse flagged patients:")
            sorted_issues = sorted(issues, key=lambda x: (x["n_encounters"], x["n_labs"]))
            for i in sorted_issues[:10]:
                self.stdout.write(
                    f"  {i['patient_id']} | {i['name'][:28]:28} | "
                    f"enc={i['n_encounters']} labs={i['n_labs']} | {i['flags'][:60]}"
                )

        # CSV export
        if options["out_csv"] and issues:
            with open(options["out_csv"], "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=issues[0].keys())
                writer.writeheader()
                writer.writerows(issues)
            self.stdout.write(self.style.SUCCESS(
                f"\nWrote {len(issues)} flagged rows to {options['out_csv']}"))
        elif options["out_csv"]:
            self.stdout.write(self.style.SUCCESS("\nNo issues — CSV not written."))

        # Return non-zero if critical duplicates exist (useful for CI / pre-deploy gate)
        critical_dupes = any("duplicate" in i["flags"] for i in issues)
        if critical_dupes:
            self.stdout.write(self.style.ERROR(
                "\nCRITICAL: Duplicate patients detected. Resolve before production."))
            sys.exit(1)

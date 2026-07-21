import sqlite3
from collections import defaultdict

DB = r"E:\OneDrive\Project Kimi\bgddr\db.sqlite3"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id, patient_id, name, hospital_id, phone, sex, dob, enrollment_date, primary_diagnosis FROM patients_patient")
patients = [dict(r) for r in c.fetchall()]

# Group by name, phone, hospital_id
by_name = defaultdict(list)
by_phone = defaultdict(list)
by_hosp = defaultdict(list)

for p in patients:
    if p["name"]:
        by_name[p["name"].strip().lower()].append(p)
    if p["phone"]:
        by_phone[p["phone"].strip()].append(p)
    if p["hospital_id"]:
        by_hosp[p["hospital_id"].strip().lower()].append(p)

print("=" * 70)
print("DUPLICATE PATIENT DETAILS")
print("=" * 70)

print("\n--- By Name ---")
for name, dups in by_name.items():
    if len(dups) > 1:
        print(f"\nName: '{dups[0]['name']}' (count={len(dups)})")
        for d in dups:
            print(f"  {d['patient_id']:12s} | phone={d['phone'] or 'None':15s} | hosp={d['hospital_id'] or 'None':15s} | dob={d['dob'] or 'None':12s} | dx={d['primary_diagnosis'] or 'None'}")

print("\n--- By Phone ---")
for phone, dups in by_phone.items():
    if len(dups) > 1:
        print(f"\nPhone: '{dups[0]['phone']}' (count={len(dups)})")
        for d in dups:
            print(f"  {d['patient_id']:12s} | name={d['name'] or 'None':30s} | hosp={d['hospital_id'] or 'None':15s}")

print("\n--- By Hospital ID ---")
for hosp, dups in by_hosp.items():
    if len(dups) > 1:
        print(f"\nHospital ID: '{dups[0]['hospital_id']}' (count={len(dups)})")
        for d in dups:
            print(f"  {d['patient_id']:12s} | name={d['name'] or 'None':30s} | phone={d['phone'] or 'None':15s}")

conn.close()

import sqlite3

conn = sqlite3.connect(r"E:\OneDrive\Project Kimi\bgddr\db.sqlite3")
c = conn.cursor()

# Check patient 221's primary_diagnosis
c.execute("SELECT patient_id, name, primary_diagnosis FROM patients_patient WHERE patient_id = 'BGD-00221'")
print("Patient 221:", c.fetchone())

# Check all unique primary_diagnosis values to see the short codes
c.execute("SELECT DISTINCT primary_diagnosis FROM patients_patient WHERE primary_diagnosis IS NOT NULL AND primary_diagnosis != '' LIMIT 20")
print("\nUnique primary_diagnosis values (short codes):")
for row in c.fetchall():
    print("  ", row[0])

# Check the most recent prescription for patient 221
c.execute("""
    SELECT p.id, p.diagnosis_text, p.investigations_advised, p.status, p.version
    FROM prescriptions_prescription p
    JOIN encounters_clinicalencounter e ON p.encounter_id = e.id
    WHERE e.patient_id = (SELECT id FROM patients_patient WHERE patient_id = 'BGD-00221')
    ORDER BY p.id DESC LIMIT 1
""")
print("\nMost recent prescription for patient 221:")
row = c.fetchone()
if row:
    print(f"  id={row[0]}, diagnosis='{row[1]}', investigations='{row[2]}', status={row[3]}, v={row[4]}")
else:
    print("  No prescriptions found")

conn.close()

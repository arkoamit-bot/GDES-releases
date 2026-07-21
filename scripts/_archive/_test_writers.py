"""Quick smoke-test for exports.services.writers."""
import sys
sys.path.insert(0, r"C:\Users\User\Documents\GitHub\GDES")

# Minimal mock to avoid needing Django for this test
class FakeModel:
    pass

# Test writers directly
from exports.services.writers import to_csv, to_xlsx, to_sav
from exports.services.dictionary import column_defs

headers = ["patient_id", "name", "sex", "dob", "enrollment_date", "diabetes_status", "latest_egfr"]
rows = [
    ["BGD-001", "Alice", "M", "1972-05-01", "2024-01-01", "t2", 42],
    ["BGD-002", "Bob", "F", "1985-03-15", "2024-06-01", "t1", 88],
]

# CSV
csv_text = to_csv(headers, rows)
print(f"CSV OK: {csv_text[:80]}...")
assert "BGD-001" in csv_text

# XLSX
xlsx_bytes = to_xlsx(headers, rows)
print(f"XLSX OK: {len(xlsx_bytes)} bytes, starts with {xlsx_bytes[:2]!r}")
assert xlsx_bytes[:2] == b"PK", "not a valid ZIP/XLSX"

# SAV
defs = column_defs()
sav_bytes = to_sav(headers, rows, defs=defs)
print(f"SAV OK: {len(sav_bytes)} bytes, starts with {sav_bytes[:4]!r}")
assert sav_bytes[:4] == b"$FL2", "not a valid SAV"

print("\nAll writers pass smoke test!")

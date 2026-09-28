# Patient Data Validation & Cleanup Report

**Generated:** 2025-01-27  
**Database:** SQLite (db.sqlite3)  
**Total patients:** 224  
**Flagged patients:** 224 (100%)

---

## 1. Executive Summary

The database contains **224 patients**, but only **5 are real clinical records**. The remaining **219 are synthetic/test data** used for engine development, model training, and demo purposes. **2 critical duplicates** need resolution before production use.

| Category | Count | Description |
|----------|-------|-------------|
| Real patients | 5 | Actual clinical entries (including 1 duplicate pair) |
| Demo/test patients | 3 | BGD-DEMO, BGD-LOOP, API-DM (demo/development entries) |
| Synthetic data | 216 | Engine-generated test patients for unit testing |
| **Total** | **224** | |

---

## 2. Critical Duplicates (Must Fix)

### Duplicate Pair #1: `000000` vs `BGD-00001`

| Field | `000000` | `BGD-00001` | Action |
|-------|----------|-------------|--------|
| **Name** | Wasim Md Mohosin Ul Haque | Wasim Md Mohosin Ul Haque | Same person |
| **Phone** | 01915472750 | 01915472750 | Same |
| **Hospital ID** | HOSP-26176 | HOSP-26176 | Same |
| **Diagnosis** | IgA nephropathy | IgA nephropathy | Same |
| **Baseline** | **YES** | NO | `000000` has the real baseline |
| **Encounters** | **2** | 0 | `000000` has real visit data |
| **Lab results** | **8** | 0 | `000000` has real lab data |

**Recommendation:** `000000` is the real record with all clinical data. `BGD-00001` is an empty duplicate created during initial setup. **Delete `BGD-00001` and keep `000000`.** Optionally, rename `000000` to `BGD-00001` if you prefer the BGD- prefix convention.

### Duplicate #2: `API-DM`

| Field | `API-DM` | `BGD-00001` (Wasim) | Status |
|-------|----------|---------------------|--------|
| **Name** | Rahim | Wasim Md Mohosin Ul Haque | Different person? |
| **Phone** | 01915472750 | 01915472750 | **Same — likely copied** |
| **Hospital ID** | HOSP-26176 | HOSP-26176 | **Same — likely copied** |
| **Diagnosis** | IgA nephropathy | IgA nephropathy | Same |
| **Baseline** | NO | NO | No data |
| **Encounters** | 0 | 0 | No data |
| **Lab results** | 0 | 0 | No data |

**Recommendation:** `API-DM` appears to be a test/demo entry where phone/hospital_id were copied from Wasim. It has no clinical data. **Clear the phone and hospital_id fields** (set to empty) OR **delete the record entirely** if it's not a real patient.

---

## 3. Real Patients (Keep)

| Patient ID | Name | Baseline | Encounters | Labs | Diagnosis | Status |
|-------------|------|----------|------------|------|-----------|--------|
| `000000` | Wasim Md Mohosin Ul Haque | **YES** | **2** | **8** | IgA nephropathy | ✅ Primary record (keep) |
| `BGD-00001` | Wasim Md Mohosin Ul Haque | NO | 0 | 0 | IgA nephropathy | ❌ Empty duplicate (delete) |
| `BGD-00002` | wasim | **YES** | **1** | **12** | IgA nephropathy | ✅ Keep |
| `BGD-00003` | sumit | **YES** | **1** | **8** | IgA nephropathy | ✅ Keep |
| `API-DM2` | Karim | NO | **1** | 0 | (garbage) | ⚠️ Review — has 1 encounter but no labs, diagnosis is corrupted |

**Note:** `API-DM2` has 1 encounter but no labs and a corrupted diagnosis field. This may be a real patient with incomplete data or another test entry. **Manual review recommended.**

---

## 4. Demo/Test Patients (Delete Before Production)

| Patient ID | Name | Encounters | Labs | Reason to Delete |
|-------------|------|------------|------|------------------|
| `BGD-DEMO` | Demo Rahman | 1 | 0 | Explicit demo name |
| `BGD-LOOP` | Loop Test | 1 | 4 | Explicit test name |
| `API-DM` | Rahim | 0 | 0 | Demo entry with copied phone/hosp |
| `AUD-DEMO` | Kamal Uddin Ahmed | 0 | 0 | Explicit demo prefix |
| `SCH-DEMO` | Rahima | 0 | 0 | Explicit demo prefix |
| `PR-CR1` | PR-CR1 | 0 | 0 | Test ID pattern |
| `PR-CR2` | PR-CR2 | 0 | 0 | Test ID pattern |
| `PR-CRK0`–`PR-CRK4` | PR-CRK* | 0 | 0 | Test ID pattern |

---

## 5. Synthetic Data (216 patients — Delete All)

These are engine-generated patients used for unit testing, model training, and algorithm validation. They have **no real clinical value** and **no encounters, baselines, or meaningful data**.

| Prefix | Count | Purpose | Example IDs |
|--------|-------|---------|-------------|
| `SYN-E*` | 24 | Synthetic engine test | SYN-E00–SYN-E23 |
| `SYN-U*` | 24 | Synthetic unit test | SYN-U00–SYN-U23 |
| `FLAG-*` | 16 | Flag/alert testing | FLAG-INELIG, FLAG-00–FLAG-15 |
| `PRO-H*` | 15 | Prognosis model (high risk) | PRO-H00–PRO-H14 |
| `PRO-C*` | 15 | Prognosis model (control) | PRO-C00–PRO-C14 |
| `DX-*` | 4 | Diagnosis testing | DX-IGA, DX-IGA2, DX-MN, DX-FSGS, DX-LN |
| `LNT-*` | 2 | Lupus nephritis testing | LNT-STABLE, LNT-MODEST |
| `SAF-DS*` | 10 | Safety event (diabetic, serious) | SAF-DS0–SAF-DS9 |
| `SAF-DN*` | 10 | Safety event (diabetic, non-serious) | SAF-DN0–SAF-DN9 |
| `SAF-NS*` | 10 | Safety event (non-diabetic, serious) | SAF-NS0–SAF-NS9 |
| `BMK-E*` | 12 | Biomarker (elevated) | BMK-E0–BMK-E11 |
| `BMK-N*` | 12 | Biomarker (normal) | BMK-N0–BMK-N11 |
| `ST-D*` | 25 | Survival/treatment (diabetic) | ST-D0–ST-D24 |
| `ST-U*` | 25 | Survival/treatment (non-diabetic) | ST-U0–ST-U24 |
| `AUD-DEMO` | 1 | Audit demo | AUD-DEMO |
| `SCH-DEMO` | 1 | Schedule demo | SCH-DEMO |
| `PR-CR*` | 7 | PR/CR test | PR-CR1, PR-CR2, PR-CRK0–4 |
| **Total** | **216** | | |

---

## 6. Validation Flag Breakdown

| Flag | Count | Meaning |
|------|-------|---------|
| `no_baseline` | 221 | No baseline assessment recorded |
| `no_encounters` | 218 | No follow-up visits |
| `few_encounters(0)` | 218 | Zero encounters (below threshold=2) |
| `missing_diagnosis` | 90 | No primary diagnosis set |
| `no_labs` | 13 | No lab results |
| `missing_dob` | 11 | No date of birth |
| `missing_enrollment_date` | 11 | No enrollment date |
| `few_encounters(1)` | 5 | Only 1 encounter (below threshold=2) |
| `duplicate_phone` | 3 | Same phone number as another patient |
| `duplicate_hospital_id` | 3 | Same hospital ID as another patient |
| `duplicate_name` | 2 | Same name as another patient |

---

## 7. Recommended Cleanup Plan

### Step 1: Fix Critical Duplicates (High Priority)

```sql
-- Option A: Delete the empty duplicate BGD-00001
DELETE FROM patients_patient WHERE patient_id = 'BGD-00001';

-- Option B: Rename 000000 to BGD-00001 (if you prefer BGD- prefix)
-- UPDATE patients_patient SET patient_id = 'BGD-00001' WHERE patient_id = '000000';
-- Then delete BGD-00001 (which is now the old 000000? No, need to be careful.)

-- Fix API-DM: clear copied phone and hospital_id
UPDATE patients_patient 
SET phone = '', hospital_id = '' 
WHERE patient_id = 'API-DM';

-- OR delete API-DM entirely if it's a pure test entry:
-- DELETE FROM patients_patient WHERE patient_id = 'API-DM';
```

### Step 2: Delete Synthetic Patients (Before Production)

```sql
-- Delete all synthetic/test patients
DELETE FROM patients_patient 
WHERE patient_id LIKE 'SYN-%' 
   OR patient_id LIKE 'FLAG-%' 
   OR patient_id LIKE 'PRO-%' 
   OR patient_id LIKE 'DX-%' 
   OR patient_id LIKE 'LNT-%' 
   OR patient_id LIKE 'SAF-%' 
   OR patient_id LIKE 'BMK-%' 
   OR patient_id LIKE 'ST-%' 
   OR patient_id LIKE 'AUD-DEMO' 
   OR patient_id LIKE 'SCH-DEMO' 
   OR patient_id LIKE 'PR-%';
```

### Step 3: Delete Demo Patients

```sql
-- Delete explicit demo patients
DELETE FROM patients_patient 
WHERE patient_id IN ('BGD-DEMO', 'BGD-LOOP', 'BGD-00001');
```

### Step 4: Review API-DM2

```sql
-- Check API-DM2's encounter data
SELECT * FROM encounters_clinicalencounter 
WHERE patient_id = (SELECT id FROM patients_patient WHERE patient_id = 'API-DM2');
```

If the encounter has no meaningful data, delete API-DM2 too. If it has real clinical data, keep it and fix the diagnosis field.

---

## 8. After-Cleanup Projection

| Metric | Before | After |
|--------|--------|-------|
| Total patients | 224 | **~5–8** |
| Flagged patients | 224 (100%) | **~0–2** (0–25%) |
| Synthetic data | 216 | **0** |
| Duplicates | 2 | **0** |
| Real patients with encounters | 5 | **3–5** |
| Real patients with baseline | 3 | **3–4** |

---

## 9. Safety Checklist Before Applying

- [ ] **Backup db.sqlite3** before any changes
- [ ] Confirm `000000` is the real Wasim record (has baseline + 2 encounters + 8 labs)
- [ ] Confirm `BGD-00001` is empty (no baseline, no encounters, no labs)
- [ ] Decide: rename `000000` to `BGD-00001` or keep `000000` as-is?
- [ ] Decide: delete `API-DM` or just clear its phone/hospital_id?
- [ ] Review `API-DM2` (Karim) — is this a real patient?
- [ ] Confirm no foreign-key constraints will break (check for linked encounters, labs, prescriptions)

---

## 10. Django Management Commands

```bash
# Backup first
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Run the built-in cleanup script
python manage.py validate_patients --csv=patient_issues_$(date +%Y%m%d).csv

# Apply SQL cleanup (review and edit cleanup_dups.sql first)
# sqlite3 db.sqlite3 < cleanup_dups.sql

# Validate again after cleanup
python manage.py validate_patients
```

---

*This report is ready for your review. Once you confirm the actions above, I can apply the cleanup or generate the exact SQL commands for you.*

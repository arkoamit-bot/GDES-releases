-- SQL cleanup script for duplicate patients found in validation.
-- Run this after reviewing the duplicates and confirming the actions.
--
-- BACKUP db.sqlite3 FIRST!

-- Duplicate 1: patient 000000 is a duplicate of BGD-00001
-- Same name, phone, hospital_id, dob. 000000 has no diagnosis.
-- Action: DELETE the 000000 record (it appears to be an initial test entry).
-- If 000000 has any encounters/labs linked, migrate them to BGD-00001 first.
-- (Check: SELECT * FROM encounters_clinicalencounter WHERE patient_id = (SELECT id FROM patients_patient WHERE patient_id = '000000');)
-- If no linked data, delete:
-- DELETE FROM patients_patient WHERE patient_id = '000000';

-- Duplicate 2: API-DM shares phone and hospital_id with Wasim (BGD-00001).
-- Name is "Rahim" but phone/hospital_id match Wasim.
-- Action: MANUAL REVIEW required. Either:
--   a) API-DM is a different person with wrong phone/hospital_id -> UPDATE with correct values
--   b) API-DM is the same person (nickname/maiden name) -> DELETE the duplicate
--
-- To update API-DM's phone and hospital_id to empty (if they were copied by mistake):
-- UPDATE patients_patient SET phone = '', hospital_id = '' WHERE patient_id = 'API-DM';

-- NOTE: The AUD-DEMO, SCH-DEMO, SYN-*, PR-*, LOOP patients are synthetic/test data.
-- Consider deleting all test patients before production if they are not real patients.
-- To list all test patients:
-- SELECT patient_id, name FROM patients_patient WHERE patient_id LIKE '%DEMO%' OR patient_id LIKE 'SYN-%' OR patient_id LIKE 'PR-%' OR patient_id LIKE 'LOOP%' OR patient_id LIKE 'AUD-%' OR patient_id LIKE 'SCH-%';

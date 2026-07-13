"""
Seed the lab test catalog and ordering panels the BGDDR portfolio needs.

    python manage.py seed_labs
"""
from django.core.management.base import BaseCommand

from labs.models import LabPanel, LabTest

# code, name, unit, value_type, ref_low, ref_high, loinc, is_derived
TESTS = [
    ("creatinine", "Serum creatinine", "mg/dL", "numeric", 0.6, 1.3, "2160-0", False),
    ("egfr", "eGFR (CKD-EPI 2021)", "mL/min/1.73m2", "numeric", 90, None, "98979-8", True),
    ("upcr", "Urine protein:creatinine ratio", "g/g", "numeric", None, 0.2, "40486-3", False),
    ("utp_24h", "24-hour urine total protein", "g/day", "numeric", None, 0.15, "21482-5", False),
    ("uacr", "Urine albumin:creatinine ratio", "mg/g", "numeric", None, 30, "9318-7", False),
    ("albumin", "Serum albumin", "g/dL", "numeric", 3.5, 5.0, "1751-7", False),
    ("hemoglobin", "Hemoglobin", "g/dL", "numeric", 12, 17, "718-7", False),
    ("potassium", "Serum potassium", "mmol/L", "numeric", 3.5, 5.5, "2823-3", False),
    ("hba1c", "HbA1c", "%", "numeric", 4.0, 5.7, "4548-4", False),
    ("c3", "Complement C3", "mg/dL", "numeric", 90, 180, "4485-9", False),
    ("c4", "Complement C4", "mg/dL", "numeric", 10, 40, "4498-2", False),
    ("anti_pla2r", "Anti-PLA2R antibody", "RU/mL", "numeric", None, 20, "82339-3", False),
    ("gd_iga1", "Galactose-deficient IgA1", "U/mL", "numeric", None, None, "", False),
    ("anti_dsdna", "Anti-dsDNA antibody", "IU/mL", "numeric", None, 30, "5131-8", False),
    ("ana", "ANA", "", "qualitative", None, None, "5048-4", False),
    ("anca", "ANCA", "", "qualitative", None, None, "17698-7", False),
    ("anti_gbm", "Anti-GBM antibody", "", "qualitative", None, None, "48002-4", False),
    ("aso", "ASO titre", "", "qualitative", None, None, "5061-7", False),
    # Infection screening (pre-immunosuppression) — qualitative pos/neg.
    ("hbsag", "Hepatitis B surface antigen (HBsAg)", "", "qualitative", None, None, "5195-3", False),
    ("anti_hbc_total", "Anti-HBc total", "", "qualitative", None, None, "24113-1", False),
    ("anti_hcv", "Anti-HCV", "", "qualitative", None, None, "16128-1", False),
    ("hiv", "HIV Ag/Ab", "", "qualitative", None, None, "56888-1", False),
    ("igra", "IGRA (TB)", "", "qualitative", None, None, "88519-2", False),
    ("mantoux", "Mantoux / TST (MT)", "mm", "qualitative", None, None, "58415-1", False),
]

# panel_code, name, test_codes
PANELS = [
    ("renal_monitoring", "Renal monitoring panel",
     ["creatinine", "potassium", "upcr", "utp_24h", "albumin", "hemoglobin"]),
    ("gn_workup", "GN serology workup",
     ["c3", "c4", "anti_pla2r", "anti_dsdna", "gd_iga1", "ana", "anca", "anti_gbm", "aso"]),
    ("infection_screen", "Infection screen (pre-immunosuppression)",
     ["hbsag", "anti_hbc_total", "anti_hcv", "hiv", "igra", "mantoux"]),
    ("diabetes_monitoring", "Diabetes monitoring",
     ["hba1c", "uacr", "creatinine"]),
]


class Command(BaseCommand):
    help = "Seed lab test catalog and ordering panels."

    def handle(self, *args, **options):
        for (code, name, unit, vtype, lo, hi, loinc, derived) in TESTS:
            LabTest.objects.update_or_create(
                code=code,
                defaults=dict(name=name, default_unit=unit, value_type=vtype,
                              ref_low=lo, ref_high=hi, loinc=loinc,
                              is_derived=derived),
            )
        for (pcode, pname, codes) in PANELS:
            panel, _ = LabPanel.objects.update_or_create(
                code=pcode, defaults=dict(name=pname))
            panel.tests.set(LabTest.objects.filter(code__in=codes))
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(TESTS)} tests and {len(PANELS)} panels."))

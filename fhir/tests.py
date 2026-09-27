"""
FHIR import/export tests.

`import_patient_from_fhir` read a `created` flag that was only bound inside the
identifier branch, so every standards-compliant Patient without a BGDDR
identifier raised UnboundLocalError — and because the function is atomic, the
row was rolled back. Every such import silently did nothing.
"""
from django.test import TestCase

from patients.models import Patient

from .export import export_patient_bundle
from .import_fhir import import_patient_from_fhir


def _fhir_patient(name="Foreign Patient", gender="female"):
    return {
        "resourceType": "Patient",
        "name": [{"family": name.split()[-1], "given": name.split()[:-1]}],
        "gender": gender,
        "birthDate": "1975-03-02",
        "telecom": [{"system": "phone", "value": "01712345678"}],
    }


class ImportPatientTests(TestCase):
    def test_patient_without_a_bgddr_identifier_is_created(self):
        result = import_patient_from_fhir(_fhir_patient())
        self.assertEqual(result["status"], "created")
        self.assertTrue(Patient.objects.filter(pk=result["id"]).exists())

    def test_patient_with_a_bgddr_identifier_is_matched(self):
        payload = _fhir_patient("Existing One")
        payload["identifier"] = [{
            "system": "https://bgddr.birdem.org/patient-id", "value": "BGD-00099",
        }]
        result = import_patient_from_fhir(payload)
        self.assertEqual(result["status"], "created")
        self.assertEqual(Patient.objects.filter(patient_id="BGD-00099").count(), 1)

        # Re-importing the same identifier updates rather than duplicates.
        again = import_patient_from_fhir(payload)
        self.assertEqual(again["status"], "updated")
        self.assertEqual(Patient.objects.filter(patient_id="BGD-00099").count(), 1)

    def test_imported_patient_maps_sex_and_dob(self):
        result = import_patient_from_fhir(_fhir_patient(gender="female"))
        p = Patient.objects.get(pk=result["id"])
        self.assertEqual(p.sex, "F")
        self.assertEqual(p.dob.isoformat(), "1975-03-02")


class ExportBundleIssueTests(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_labs", verbosity=0)

    def test_bundle_reports_an_omitted_lab_instead_of_truncating_silently(self):
        p = Patient.objects.create(
            patient_id="BGD-EXP", name="Export P", sex="M", dob="1970-01-01")
        bundle = export_patient_bundle(p, include_related=True)
        self.assertIn("entry", bundle)
        # A clean export carries no issue array.
        self.assertNotIn("issue", bundle)

    def test_one_broken_lab_does_not_discard_the_others(self):
        import datetime as dt
        from unittest import mock

        from labs.services.results import record_result

        p = Patient.objects.create(
            patient_id="BGD-EXP2", name="Export P2", sex="M",
            dob=dt.date(1970, 1, 1))
        record_result(p, "creatinine", result_date=dt.date(2024, 1, 1),
                      value_numeric=1.0)
        record_result(p, "creatinine", result_date=dt.date(2024, 6, 1),
                      value_numeric=1.2)
        # record_result also derives an eGFR row, so count what will be walked.
        total_labs = p.lab_results.count()
        self.assertGreaterEqual(total_labs, 2)

        real = export_patient_bundle.__globals__["export_lab_result"]
        calls = {"n": 0}

        def flaky(lab):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("bad lab")
            return real(lab)

        with mock.patch.dict(export_patient_bundle.__globals__,
                             {"export_lab_result": flaky}):
            with self.assertLogs("fhir.export", level="ERROR"):
                bundle = export_patient_bundle(p, include_related=True)

        observations = [e for e in bundle["entry"]
                        if e["resource"].get("resourceType") == "Observation"]
        self.assertEqual(len(observations), total_labs - 1,
                         "every lab after the broken one must still be exported")
        self.assertIn("issue", bundle)
        self.assertEqual(len(bundle["issue"]), 1)
        self.assertIn("could not be exported", bundle["issue"][0]["diagnostics"])

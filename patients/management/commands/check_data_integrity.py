"""Data integrity checker for GDES V3.5 Release Certification."""
from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = "Run comprehensive data integrity checks across all clinical models."

    def handle(self, *args, **options):
        self.results: list[dict[str, Any]] = []
        self._check_patients()
        self._check_encounters()
        self._check_lab_results()
        self._check_treatment_exposures()
        self._check_scheduled_visits()
        self._check_adverse_events()
        self._check_orphan_records()
        self._check_denormalization_drift()
        self._check_stale_computed()
        self._report()

    def _fail(self, check: str, severity: str, message: str, count: int = 0):
        self.results.append({
            "check": check, "severity": severity, "message": message, "count": count,
        })

    def _check_patients(self):
        from patients.models import Patient
        total = Patient.objects.count()
        if total == 0:
            self._fail("patients", "info", "No patients in registry.")
            return
        missing_dob = Patient.objects.filter(dob__isnull=True).count()
        if missing_dob:
            self._fail("patients.dob", "warning", f"{missing_dob} patients missing date of birth.", missing_dob)
        missing_diagnosis = Patient.objects.filter(primary_diagnosis="").count()
        if missing_diagnosis:
            self._fail("patients.diagnosis", "warning", f"{missing_diagnosis} patients missing primary diagnosis.", missing_diagnosis)
        future_dob = Patient.objects.filter(dob__gt=date.today()).count()
        if future_dob:
            self._fail("patients.future_dob", "error", f"{future_dob} patients with future date of birth.", future_dob)

    def _check_encounters(self):
        from encounters.models import ClinicalEncounter
        no_bp = ClinicalEncounter.objects.filter(systolic_bp__isnull=True, diastolic_bp__isnull=False).count()
        if no_bp:
            self._fail("encounters.partial_bp", "warning", f"{no_bp} encounters with partial BP readings.", no_bp)
        invalid_bp = ClinicalEncounter.objects.filter(
            systolic_bp__isnull=False, diastolic_bp__isnull=False,
            diastolic_bp__gt=models.F("systolic_bp"),
        ).count()
        if invalid_bp:
            self._fail("encounters.diastolic_gt_systolic", "error", f"{invalid_bp} encounters with diastolic > systolic.", invalid_bp)

    def _check_lab_results(self):
        from labs.models import LabResult
        no_value = LabResult.objects.filter(value_numeric__isnull=True, value_text="").count()
        if no_value:
            self._fail("labs.no_value", "error", f"{no_value} lab results with no value.", no_value)
        future_sample = LabResult.objects.filter(
            sample_date__isnull=False, result_date__isnull=False,
            sample_date__gt=models.F("result_date"),
        ).count()
        if future_sample:
            self._fail("labs.sample_after_result", "warning", f"{future_sample} results with sample after result date.", future_sample)

    def _check_treatment_exposures(self):
        from treatments.models import TreatmentExposure
        ongoing_with_stop = TreatmentExposure.objects.filter(ongoing=True, stop_date__isnull=False).count()
        if ongoing_with_stop:
            self._fail("tx.ongoing_with_stop", "error", f"{ongoing_with_stop} ongoing exposures with stop date.", ongoing_with_stop)
        completed_no_stop = TreatmentExposure.objects.filter(ongoing=False, stop_date__isnull=True).count()
        if completed_no_stop:
            self._fail("tx.completed_no_stop", "warning", f"{completed_no_stop} completed exposures without stop date.", completed_no_stop)
        stop_before_start = TreatmentExposure.objects.filter(
            start_date__isnull=False, stop_date__isnull=False,
            stop_date__lt=models.F("start_date"),
        ).count()
        if stop_before_start:
            self._fail("tx.stop_before_start", "error", f"{stop_before_start} exposures with stop before start.", stop_before_start)

    def _check_scheduled_visits(self):
        from scheduling.models import ScheduledVisit
        window_mismatch = ScheduledVisit.objects.filter(
            window_start__isnull=False, window_end__isnull=False,
            window_start__gt=models.F("window_end"),
        ).count()
        if window_mismatch:
            self._fail("scheduling.window_mismatch", "error", f"{window_mismatch} visits with window_start > window_end.", window_mismatch)

    def _check_adverse_events(self):
        from safety.models import AdverseEvent
        infection_no_type = AdverseEvent.objects.filter(category="infection", infection_type="").count()
        if infection_no_type:
            self._fail("safety.infection_no_type", "warning", f"{infection_no_type} infection events missing infection type.", infection_no_type)

    def _check_orphan_records(self):
        from django.apps import apps
        orphan_checks = [
            ("encounters.ClinicalEvent", "encounter", "encounters.ClinicalEncounter"),
            ("safety.AdverseEvent", "encounter", "encounters.ClinicalEncounter"),
            ("safety.AdverseEvent", "suspected_drug", "treatments.DrugMaster"),
            ("scheduling.ScheduledVisit", "encounter", "encounters.ClinicalEncounter"),
        ]
        for model_path, fk_field, target_path in orphan_checks:
            try:
                model = apps.get_model(model_path)
                fk = model._meta.get_field(fk_field)
                if fk.null:
                    valid_pks = apps.get_model(target_path).objects.values_list("pk", flat=True)
                    orphans = model.objects.filter(**{f"{fk_field}__isnull": False}).exclude(
                        **{f"{fk_field}__in": valid_pks}
                    ).count()
                    if orphans:
                        self._fail(f"orphan.{model_path}.{fk_field}", "error", f"{orphans} orphan {fk_field} references in {model_path}.", orphans)
            except Exception:
                pass

    def _check_denormalization_drift(self):
        from labs.models import LabOrder
        drift = LabOrder.objects.filter(
            patient__isnull=False, encounter__patient__isnull=False
        ).exclude(
            patient=models.F("encounter__patient")
        ).count()
        if drift:
            self._fail("labs.denormalization_drift", "error", f"{drift} lab orders with patient != encounter.patient.", drift)

    def _check_stale_computed(self):
        from analytics.models import PatientOutcome
        stale = PatientOutcome.objects.filter(
            computed_at__isnull=False,
            patient__updated_at__gt=models.F("computed_at"),
        ).count()
        if stale:
            self._fail("analytics.stale_outcomes", "warning", f"{stale} stale patient outcomes (source data newer).", stale)

    def _report(self):
        if not self.results:
            self.stdout.write(self.style.SUCCESS("All integrity checks passed — no issues found."))
            return
        errors = [r for r in self.results if r["severity"] == "error"]
        warnings = [r for r in self.results if r["severity"] == "warning"]
        infos = [r for r in self.results if r["severity"] == "info"]
        if errors:
            self.stdout.write(self.style.ERROR(f"\n{len(errors)} ERROR(s) found:"))
            for r in errors:
                self.stdout.write(f"  [{r['check']}] {r['message']}")
        if warnings:
            self.stdout.write(self.style.WARNING(f"\n{len(warnings)} WARNING(s) found:"))
            for r in warnings:
                self.stdout.write(f"  [{r['check']}] {r['message']}")
        if infos:
            self.stdout.write(f"\n{len(infos)} INFO(s):")
            for r in infos:
                self.stdout.write(f"  [{r['check']}] {r['message']}")
        self.stdout.write(f"\nTotal: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info.")

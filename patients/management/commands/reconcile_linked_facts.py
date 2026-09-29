"""Reconcile legacy repeated-entry data with the linked owners (dry run by default).

    python manage.py reconcile_linked_facts                # report only
    python manage.py reconcile_linked_facts --json out.json
    python manage.py reconcile_linked_facts --apply        # safe actions only

Reports, with source row ids, every place where the 2026-09-27 linkage work
found two stores of one fact or a legacy value whose meaning is ambiguous. It
never deletes a row, never chooses the latest updated_at as the authority,
never turns an unknown into a negative, and never drops an old column.

--apply performs ONLY these idempotent, provenance-tagged actions (each in its
own transaction, so an interrupted run can simply be re-run):

  * re-project the pathology summary from the selected biopsy;
  * convert legacy single-choice IF/EM biopsy values into structured findings
    on a LOCAL report tagged "legacy" (original values kept);
  * record a legacy baseline HbA1c as a LabResult (source "legacy", dated by
    the baseline assessment date) and link it -- only when the date is known
    and no different HbA1c exists within the enrollment window;
  * represent legacy encounter BP/weight as a VitalSign reading.

Everything else is reported as needing a decision.
"""
from __future__ import annotations

import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Report (and optionally apply safe fixes for) legacy repeated-entry data."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Perform the safe, idempotent actions listed in the docstring.")
        parser.add_argument("--json", default=None, help="Write the full report to this file.")
        parser.add_argument("--limit", type=int, default=20,
                            help="Rows shown per section on the console (default 20).")

    # -- sections ------------------------------------------------------------
    def comorbidities(self):
        from baseline.models import BaselineAssessment
        from patients.comorbidity import LEVEL2_COMORBIDITY_FIELDS, is_recorded
        rows = []
        for b in BaselineAssessment.objects.select_related("patient"):
            p = b.patient
            for f in LEVEL2_COMORBIDITY_FIELDS:
                pv, bv = getattr(p, f), getattr(b, f)
                if bool(pv) == bool(bv):
                    continue
                rows.append({
                    "patient": p.patient_id, "patient_pk": p.pk, "baseline_pk": b.pk,
                    "field": f, "patient_value": pv, "baseline_value": bv,
                    "patient_recorded": is_recorded(p, f),
                    "baseline_source": b.comorbidity_snapshot_source,
                    "proposal": ("baseline snapshot differs from a recorded current state "
                                 "(may be a genuine change since enrollment)"
                                 if is_recorded(p, f) else
                                 "confirm the current state on the patient record; "
                                 "legacy baseline value shown as 'confirm' until then"),
                })
        return rows

    def legacy_false(self):
        from patients.comorbidity import LEVEL2_COMORBIDITY_FIELDS, is_recorded
        from patients.models import Patient
        counts = defaultdict(int)
        for p in Patient.objects.all():
            for f in LEVEL2_COMORBIDITY_FIELDS:
                if getattr(p, f) is False and not is_recorded(p, f):
                    counts[f] += 1
        return [{"field": f, "patients_with_unstamped_false": n,
                 "treated_as": "not recorded (unknown)"} for f, n in sorted(counts.items())]

    def diabetes(self):
        from patients.models import Patient
        return [{"patient": p.patient_id, "patient_pk": p.pk, "status": p.diabetes_status,
                 "proposal": "confirm diabetes type"}
                for p in Patient.objects.filter(diabetes_status="unknown")]

    def pathology(self, apply):
        from pathology.services.projection import projected_values, select_source
        from patients.models import Patient
        rows = []
        for p in Patient.objects.filter(biopsies__isnull=False).distinct():
            sel = select_source(p)
            want = projected_values(sel.biopsy)
            diffs = {f: {"stored": getattr(p, f), "projected": v}
                     for f, v in want.items() if (getattr(p, f) or "") != (v or "")}
            dx_differs = bool(sel.biopsy and p.primary_diagnosis
                              and p.primary_diagnosis != sel.biopsy.diagnosis.diagnosis)
            if diffs or dx_differs or p.pathology_source_biopsy_id != getattr(sel.biopsy, "pk", None):
                rows.append({"patient": p.patient_id, "patient_pk": p.pk,
                             "source_biopsy_pk": getattr(sel.biopsy, "pk", None),
                             "state": sel.state, "differences": diffs,
                             "working_diagnosis_differs": dx_differs,
                             "pending_newer_biopsies": [b.pk for b in sel.pending_biopsies],
                             "action": "re-project" + ("; working diagnosis left for "
                                                      "clinician adoption" if dx_differs else "")})
                if apply:
                    from pathology.services.projection import project_pathology
                    with transaction.atomic():
                        project_pathology(p)
        return rows

    def biopsy_scalars(self, apply):
        from pathology import findings as vocab
        from pathology.models import Biopsy
        from pathology.services.report import legacy_report_from_biopsy
        rows = []
        qs = (Biopsy.objects.filter(reports__isnull=True)
              .exclude(if_pattern="", em_findings="").select_related("patient"))
        for b in qs:
            unknown = [v for v, m in ((b.if_pattern, vocab.LEGACY_IF_MAP),
                                      (b.em_findings, vocab.LEGACY_EM_MAP)) if v and v not in m]
            rows.append({"patient": b.patient.patient_id, "biopsy_pk": b.pk,
                         "if_pattern": b.if_pattern, "em_findings": b.em_findings,
                         "unrecognised_kept_as_narrative": unknown,
                         "action": "convert to legacy-tagged findings"})
            if apply:
                with transaction.atomic():
                    legacy_report_from_biopsy(b)
        return rows

    def lesion_booleans(self):
        from pathology.models import Biopsy
        out = {}
        for f in ("arteriolar_hyalinosis", "dkd_lesion_present", "crescents_present",
                  "necrosis_present"):
            out[f] = Biopsy.objects.filter(**{f: False},
                                           created_at__date__lt="2026-09-27").count()
        return [{"field": f, "pre_change_false_rows": n,
                 "note": "old default False; cannot be distinguished from 'not assessed' -- left as stored"}
                for f, n in out.items()]

    def biopsy_conflicts(self):
        """Stored contradictions the entry form now refuses (2026-09-29).
        Report only: the original values are kept for review, never
        overwritten by a precedence rule."""
        from pathology import consistency
        from pathology import diagnosis as dxrules
        from pathology.models import Biopsy
        from pathology.services.report import current_report
        rows = []
        qs = Biopsy.objects.select_related("patient").order_by("pk")
        for b in qs:
            problems = []
            for name in ("global_sclerosis_pct", "ifta_pct", "crescent_pct"):
                v = getattr(b, name)
                if v is not None and not (0 <= v <= 100):
                    problems.append(f"{name}={v} is outside 0-100")
            rep = current_report(b)
            dx = getattr(b, "diagnosis", None) if hasattr(b, "diagnosis") else None
            score = getattr(b, "igan_score", None) if hasattr(b, "igan_score") else None
            fsgs = getattr(b, "fsgs", None) if hasattr(b, "fsgs") else None
            for _t, field, msg in (
                    consistency.crescent_errors(
                        b.crescents_present, b.crescent_pct,
                        count=getattr(rep, "crescentic_glomeruli", None),
                        oxford_c=score.C if score else None)
                    + consistency.result_category_errors(
                        b.result_category, dx.diagnosis if dx else "", b.adequacy,
                        report_status=getattr(rep, "status", ""))):
                problems.append(f"{field}: {msg}")
            if dx:
                q = dxrules.qualifiers(dx.diagnosis)
                stated = q.get("primary_secondary", "")
                if stated and dx.primary_secondary not in ("", "unknown", stated):
                    problems.append(f"diagnosis '{dx.diagnosis}' states {stated}; "
                                    f"primary_secondary={dx.primary_secondary}")
                if fsgs and fsgs.primary_secondary and dx.primary_secondary and                         fsgs.primary_secondary != dx.primary_secondary:
                    problems.append(f"FSGS panel primary_secondary={fsgs.primary_secondary} "
                                    f"vs diagnosis record {dx.primary_secondary}")
                if fsgs and q.get("variant") and fsgs.variant and fsgs.variant != q["variant"]:
                    problems.append(f"diagnosis states the {q['variant']} variant; "
                                    f"FSGS panel variant={fsgs.variant}")
            if problems:
                rows.append({"patient": b.patient.patient_id, "biopsy_pk": b.pk,
                             "biopsy_date": b.biopsy_date, "problems": problems,
                             "action": "review; values left as stored"})
        return rows

    def hba1c(self, apply):
        import datetime as dt

        from baseline.models import BaselineAssessment
        from labs.models import LabResult
        from labs.services.baseline import (ENROLLMENT_WINDOW_AFTER,
                                            ENROLLMENT_WINDOW_BEFORE, anchor_date)
        from labs.services.results import record_result
        rows = []
        for b in BaselineAssessment.objects.filter(hba1c__isnull=False,
                                                   hba1c_result__isnull=True).select_related("patient"):
            anchor = anchor_date(b)
            row = {"patient": b.patient.patient_id, "baseline_pk": b.pk,
                   "legacy_value": str(b.hba1c), "assessment_date": str(b.assessment_date or "")}
            if b.assessment_date is None:
                row["status"] = "unresolved: no assessment date -- value kept on the baseline only"
                rows.append(row)
                continue
            lo = anchor - dt.timedelta(days=ENROLLMENT_WINDOW_BEFORE)
            hi = anchor + dt.timedelta(days=ENROLLMENT_WINDOW_AFTER)
            window = list(LabResult.objects.filter(patient=b.patient, test__code="hba1c",
                                                   result_date__range=(lo, hi)))
            same = [r for r in window if r.value_numeric == b.hba1c
                    and r.result_date == b.assessment_date]
            conflicting = [r for r in window if r not in same]
            if same:
                row["status"] = f"matches lab result {same[0].pk}; link"
                if apply:
                    BaselineAssessment.objects.filter(pk=b.pk).update(hba1c_result=same[0])
            elif conflicting:
                row["status"] = ("conflict: different HbA1c in the enrollment window "
                                 f"({', '.join(f'{r.pk}={r.value_numeric}@{r.result_date}' for r in conflicting)})"
                                 " -- needs review")
            else:
                row["status"] = "record as legacy lab result and link"
                if apply:
                    with transaction.atomic():
                        r = record_result(b.patient, "hba1c", result_date=b.assessment_date,
                                          value_numeric=b.hba1c, source=LabResult.Source.LEGACY,
                                          entry_path=LabResult.EntryPath.RECONCILE,
                                          idempotency_key=f"legacy-baseline-hba1c:{b.pk}")
                        BaselineAssessment.objects.filter(pk=b.pk).update(hba1c_result=r)
            rows.append(row)
        return rows

    def lab_duplicates(self):
        from django.db.models import Count

        from labs.models import LabResult
        groups = (LabResult.objects.exclude(source=LabResult.Source.DERIVED)
                  .values("patient__patient_id", "test__code", "result_date",
                          "value_numeric", "value_text")
                  .annotate(n=Count("id")).filter(n__gt=1))
        rows = []
        for g in groups:
            ids = list(LabResult.objects.filter(
                patient__patient_id=g["patient__patient_id"], test__code=g["test__code"],
                result_date=g["result_date"], value_numeric=g["value_numeric"],
                value_text=g["value_text"]).values_list("pk", flat=True))
            rows.append({"patient": g["patient__patient_id"], "test": g["test__code"],
                         "date": str(g["result_date"]), "value": str(g["value_numeric"] or g["value_text"]),
                         "rows": ids, "status": "possible duplicate entry OR genuine repeat -- "
                                                "resolve by correcting (superseding) one; nothing deleted"})
        return rows

    def egfr_fallback(self):
        from labs.models import LabResult
        from labs.services.egfr import DEFECTIVE_FALLBACK_VERSION
        qs = (LabResult.objects.filter(test__code="egfr",
                                       formula_version=DEFECTIVE_FALLBACK_VERSION)
              .select_related("patient"))
        return [{"patient": r.patient.patient_id, "egfr_pk": r.pk,
                 "creatinine_pk": r.derived_from_id, "sex": r.patient.sex,
                 "value": str(r.value_numeric),
                 "status": ("male: under-estimated when creatinine < 0.9 mg/dL -- "
                            "re-derive under governance (correct_result on the creatinine)"
                            if r.patient.sex != "F" else "female: equation correct; "
                            "unrounded value and nonstandard version stamp only")}
                for r in qs]

    def dose_equals_strength(self):
        from django.db.models import F

        from prescriptions.models import PrescriptionItem
        n = PrescriptionItem.objects.exclude(dose="").filter(dose=F("strength")).count()
        return [{"prescription_items_with_dose_copied_from_strength": n,
                 "treated_as": "dose not separately stated (no historical dose inferred)"}]

    def encounter_vitals(self, apply):
        from encounters.models import ClinicalEncounter
        from encounters.services.vitals import adopt_legacy_encounter_values
        qs = (ClinicalEncounter.objects.filter(selected_vital__isnull=True)
              .exclude(systolic_bp__isnull=True, diastolic_bp__isnull=True,
                       weight_kg__isnull=True).select_related("patient"))
        rows = []
        for e in qs:
            rows.append({"patient": e.patient.patient_id, "encounter_pk": e.pk,
                         "systolic": e.systolic_bp, "diastolic": e.diastolic_bp,
                         "weight_kg": str(e.weight_kg) if e.weight_kg is not None else None,
                         "action": "represent as a VitalSign reading (source legacy)"})
            if apply:
                with transaction.atomic():
                    adopt_legacy_encounter_values(e)
        return rows

    def syndromes(self):
        from baseline.models import BaselineAssessment
        rows = []
        for b in BaselineAssessment.objects.select_related("patient"):
            lst = b.presentation_syndromes or []
            if len(lst) > 1 or (b.presentation_syndrome and not lst):
                rows.append({"patient": b.patient.patient_id, "baseline_pk": b.pk,
                             "list": lst, "legacy_scalar": b.presentation_syndrome,
                             "status": "kept: primary + additional presentations"
                                       if len(lst) > 1 else "scalar lifted into the list on next save"})
        return rows

    def unsnapshotted_prescriptions(self):
        from prescriptions.models import Prescription
        n = Prescription.objects.filter(status="final", snapshot_version=0).count()
        return [{"finalized_without_issued_snapshot": n,
                 "treated_as": "rendered from current records with a visible notice; not back-filled"}]

    # -- run -----------------------------------------------------------------
    def handle(self, *args, **opts):
        apply = opts["apply"]
        report = {
            "mode": "apply" if apply else "dry-run",
            "comorbidity_disagreements": self.comorbidities(),
            "comorbidity_legacy_false": self.legacy_false(),
            "diabetes_type_unconfirmed": self.diabetes(),
            "pathology_projection": self.pathology(apply),
            "biopsy_legacy_if_em": self.biopsy_scalars(apply),
            "biopsy_legacy_false_lesions": self.lesion_booleans(),
            "biopsy_conflicting_values": self.biopsy_conflicts(),
            "baseline_hba1c": self.hba1c(apply),
            "lab_possible_duplicates": self.lab_duplicates(),
            "egfr_defective_fallback": self.egfr_fallback(),
            "prescription_dose_equals_strength": self.dose_equals_strength(),
            "prescriptions_without_snapshot": self.unsnapshotted_prescriptions(),
            "encounter_vitals_without_reading": self.encounter_vitals(apply),
            "presentation_syndromes": self.syndromes(),
        }
        limit = opts["limit"]
        self.stdout.write(f"reconcile_linked_facts ({report['mode']})")
        for key, rows in report.items():
            if key == "mode":
                continue
            self.stdout.write(f"\n== {key}: {len(rows)}")
            for row in rows[:limit]:
                self.stdout.write("   " + json.dumps(row, default=str))
            if len(rows) > limit:
                self.stdout.write(f"   ... {len(rows) - limit} more (use --json)")
        if opts["json"]:
            with open(opts["json"], "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2, default=str)
            self.stdout.write(self.style.SUCCESS(f"\nFull report written to {opts['json']}"))
        return None

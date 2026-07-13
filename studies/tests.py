"""
Tests for the registry-embedded trial platform: eligibility screening,
reproducible & balanced randomization, stratification, allocation ratio, the
trial-consent gate, and the analytics-by-arm integration.
"""
import datetime as dt

from django.test import TestCase

from audit.models import Consent
from audit.services.consent import grant_consent
from patients.models import Patient

from .models import Study, StudyArm, StudyEnrollment
from .services.eligibility import screen
from .services.randomization import (AlreadyEnrolled, ConsentRequired, enroll,
                                     generate_sequence)


def _two_arm_study(scheme=Study.Scheme.BLOCK, ratio=(1, 1), seed=42,
                   multipliers=(2,), stratify=None, code="TRIAL-1",
                   requires_consent=False):
    s = Study.objects.create(
        code=code, title="Test trial", study_type=Study.Type.RCT,
        randomization_scheme=scheme, random_seed=seed,
        block_multipliers=list(multipliers), stratify_by=stratify or [],
        requires_trial_consent=requires_consent)
    StudyArm.objects.create(study=s, code="treat", name="Treatment",
                            ratio=ratio[0], order=0)
    StudyArm.objects.create(study=s, code="control", name="Control",
                            ratio=ratio[1], order=1, is_control=True)
    return s


def _patient(pid, **kw):
    return Patient.objects.create(patient_id=pid, name=pid, sex="M", **kw)


class EligibilityTests(TestCase):
    def test_advanced_dkd_igan_criteria(self):
        s = Study.objects.create(code="ADVANCED-DKD-IGAN", title="x",
                                 study_type=Study.Type.RCT)
        ok = _patient("OK", primary_diagnosis="IgA nephropathy",
                      diabetes_status="t2", latest_egfr=22)
        bad = _patient("BAD", primary_diagnosis="Membranous nephropathy",
                       diabetes_status="none", latest_egfr=80)
        self.assertEqual(screen(s, ok), (True, []))
        eligible, reasons = screen(s, bad)
        self.assertFalse(eligible)
        self.assertEqual(len(reasons), 3)


class RandomizationTests(TestCase):
    def test_reproducible_sequence(self):
        s = _two_arm_study(seed=123)
        arms = s.arms_ordered()
        seq1 = generate_sequence(s, arms, "all", 20)
        seq2 = generate_sequence(s, arms, "all", 20)
        self.assertEqual(seq1, seq2)                      # deterministic
        # Re-creating the study with the same seed reproduces the sequence.
        s2 = _two_arm_study(seed=123, code="TRIAL-2")
        self.assertEqual(generate_sequence(s2, s2.arms_ordered(), "all", 20), seq1)

    def test_block_keeps_balance(self):
        # With block multiplier 2 on a 1:1 unit, each block of 4 has 2 per arm,
        # so after every 4 allocations the arms are exactly balanced.
        s = _two_arm_study(multipliers=(2,))
        arms = s.arms_ordered()
        seq = generate_sequence(s, arms, "all", 12)
        for cut in (4, 8, 12):
            window = seq[:cut]
            self.assertEqual(window.count("treat"), window.count("control"))

    def test_allocation_ratio_2_to_1(self):
        s = _two_arm_study(ratio=(2, 1), multipliers=(1,))
        seq = generate_sequence(s, s.arms_ordered(), "all", 30)
        self.assertEqual(seq.count("treat"), 20)
        self.assertEqual(seq.count("control"), 10)

    def test_enroll_allocates_and_is_balanced(self):
        s = _two_arm_study(multipliers=(2,))
        for i in range(8):
            enroll(s, _patient(f"P{i}"))
        counts = {a.code: a.enrollments.count() for a in s.arms_ordered()}
        self.assertEqual(counts["treat"], 4)
        self.assertEqual(counts["control"], 4)

    def test_stratified_block_independent_per_stratum(self):
        s = _two_arm_study(scheme=Study.Scheme.STRATIFIED_BLOCK,
                           multipliers=(2,), stratify=["diabetes"])
        # 4 diabetics + 4 non-diabetics -> balanced within each stratum.
        for i in range(4):
            enroll(s, _patient(f"D{i}", diabetes_status="t2"))
        for i in range(4):
            enroll(s, _patient(f"N{i}", diabetes_status="none"))
        strata = set(StudyEnrollment.objects.filter(study=s)
                     .values_list("stratum", flat=True))
        self.assertEqual(strata, {"diabetes=DM", "diabetes=noDM"})
        for stratum in strata:
            arms = list(StudyEnrollment.objects.filter(study=s, stratum=stratum)
                        .values_list("arm__code", flat=True))
            self.assertEqual(arms.count("treat"), arms.count("control"))

    def test_ineligible_patient_not_allocated(self):
        s = Study.objects.create(code="ADVANCED-DKD-IGAN", title="x",
                                 study_type=Study.Type.RCT,
                                 randomization_scheme=Study.Scheme.BLOCK,
                                 block_multipliers=[2])
        StudyArm.objects.create(study=s, code="a", name="A", order=0)
        StudyArm.objects.create(study=s, code="b", name="B", order=1)
        enr = enroll(s, _patient("INELIG", diabetes_status="none", latest_egfr=90))
        self.assertEqual(enr.status, StudyEnrollment.Status.INELIGIBLE)
        self.assertIsNone(enr.arm)

    def test_trial_consent_gate(self):
        s = _two_arm_study(requires_consent=True)
        p = _patient("NOCONSENT")
        with self.assertRaises(ConsentRequired):
            enroll(s, p)
        # After granting trial consent, enrolment succeeds.
        grant_consent(p, Consent.Type.TRIAL, "ICF-TRIAL-v1",
                      consent_date=dt.date(2026, 1, 1))
        enr = enroll(s, p)
        self.assertEqual(enr.status, StudyEnrollment.Status.ENROLLED)
        self.assertIsNotNone(enr.arm)

    def test_double_enroll_blocked(self):
        s = _two_arm_study()
        p = _patient("DUP")
        enroll(s, p)
        with self.assertRaises(AlreadyEnrolled):
            enroll(s, p)


class AnalyticsByArmTests(TestCase):
    def test_group_by_study_arm(self):
        from analytics.services.cohort import split_patients
        s = _two_arm_study(multipliers=(2,))
        for i in range(6):
            enroll(s, _patient(f"A{i}"))
        groups = split_patients(Patient.objects.all(), "study:TRIAL-1")
        self.assertEqual(set(groups), {"arm:treat", "arm:control"})
        self.assertEqual(sum(len(v) for v in groups.values()), 6)

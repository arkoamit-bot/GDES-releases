import datetime as dt

from django.core.exceptions import ValidationError
from django.test import TestCase

from audit.models import Consent
from audit.services.consent import grant_consent
from patients.models import Patient

from .models import Biopsy, BiopsyImage, GNDiagnosis, IgANScore, PathologyReview
from .services.agreement import cohens_kappa, interobserver_agreement
from .services.review import adjudicate, concordance, submit_review


class PathologyTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="PA1", name="x", sex="M")
        self.biopsy = Biopsy.objects.create(
            patient=self.p, biopsy_date=dt.date(2026, 1, 1),
            adequacy=Biopsy.Adequacy.ADEQUATE, total_glomeruli=18)

    def test_mest_c_score_attached_to_biopsy(self):
        IgANScore.objects.create(biopsy=self.biopsy, M=1, E=0, S=1, T=1, C=0)
        GNDiagnosis.objects.create(biopsy=self.biopsy, diagnosis="IgA nephropathy",
                                   broad_group="Immune-complex GN")
        self.assertEqual(self.biopsy.igan_score.T, 1)
        self.assertEqual(self.biopsy.diagnosis.diagnosis, "IgA nephropathy")

    def test_image_requires_imaging_consent(self):
        img = BiopsyImage(biopsy=self.biopsy, stain=BiopsyImage.Stain.HE)
        with self.assertRaises(ValidationError):
            img.clean()
        grant_consent(self.p, Consent.Type.IMAGING, "IMG-v1",
                      consent_date=dt.date(2026, 1, 1))
        img.clean()   # no longer raises


class CohensKappaTests(TestCase):
    def test_kappa_textbook_value(self):
        # Classic 2x2: 20 (Y,Y), 5 (Y,N), 10 (N,Y), 15 (N,N) -> kappa = 0.40.
        pairs = ([("Y", "Y")] * 20 + [("Y", "N")] * 5
                 + [("N", "Y")] * 10 + [("N", "N")] * 15)
        self.assertAlmostEqual(cohens_kappa(pairs), 0.40, places=2)

    def test_perfect_and_empty(self):
        self.assertEqual(cohens_kappa([("a", "a"), ("b", "b"), ("c", "c")]), 1.0)
        self.assertIsNone(cohens_kappa([]))


class CentralReviewTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="CR1", name="x", sex="M")
        self.b = Biopsy.objects.create(patient=self.p, biopsy_date=dt.date(2026, 1, 1))

    def test_local_only_awaits_central(self):
        submit_review(self.b, PathologyReview.Role.LOCAL,
                      diagnosis="IgA nephropathy", broad_group="Immune-complex GN")
        self.b.refresh_from_db()
        self.assertEqual(self.b.review_status, Biopsy.ReviewStatus.AWAITING_CENTRAL)

    def test_concordant_finalizes_diagnosis(self):
        for role in (PathologyReview.Role.LOCAL, PathologyReview.Role.CENTRAL):
            submit_review(self.b, role, diagnosis="IgA nephropathy",
                          broad_group="Immune-complex GN", mest={"M": 1, "E": 0, "S": 1, "T": 1, "C": 0})
        self.b.refresh_from_db()
        self.assertEqual(self.b.review_status, Biopsy.ReviewStatus.CONCORDANT)
        self.assertTrue(concordance(self.b)["concordant"])
        # Final read writes the authoritative GNDiagnosis + MEST-C.
        self.assertEqual(self.b.diagnosis.diagnosis, "IgA nephropathy")
        self.assertEqual(self.b.igan_score.T, 1)

    def test_discordant_then_adjudication(self):
        submit_review(self.b, PathologyReview.Role.LOCAL, diagnosis="IgA nephropathy",
                      broad_group="Immune-complex GN")
        submit_review(self.b, PathologyReview.Role.CENTRAL, diagnosis="Membranous nephropathy",
                      broad_group="Immune-complex GN")
        self.b.refresh_from_db()
        self.assertEqual(self.b.review_status, Biopsy.ReviewStatus.DISCORDANT)
        self.assertFalse(concordance(self.b)["concordant"])
        # Adjudication resolves it.
        adjudicate(self.b, diagnosis="Membranous nephropathy", broad_group="Immune-complex GN")
        self.b.refresh_from_db()
        self.assertEqual(self.b.review_status, Biopsy.ReviewStatus.ADJUDICATED)
        self.assertEqual(self.b.diagnosis.diagnosis, "Membranous nephropathy")
        final = self.b.reviews.get(is_final=True)
        self.assertEqual(final.role, PathologyReview.Role.ADJUDICATION)

    def test_interobserver_agreement_summary(self):
        # Two biopsies: one concordant diagnosis, one discordant -> 50% agreement.
        for i, (ldx, cdx) in enumerate([("IgA nephropathy", "IgA nephropathy"),
                                        ("FSGS", "Minimal change disease")]):
            b = Biopsy.objects.create(patient=self.p, biopsy_date=dt.date(2026, 2, i + 1))
            submit_review(b, PathologyReview.Role.LOCAL, diagnosis=ldx)
            submit_review(b, PathologyReview.Role.CENTRAL, diagnosis=cdx)
        agr = interobserver_agreement(Biopsy.objects.filter(biopsy_date__month=2))
        self.assertEqual(agr["n_dual_reviewed"], 2)
        self.assertEqual(agr["diagnosis_agreement_pct"], 50.0)

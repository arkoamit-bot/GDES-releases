"""
Validation tests for the pure-Python statistical refinements (§10.3-10.4):
linear mixed model, competing-risks CIF, and MICE + Rubin's rules.
"""
import datetime as dt
import random

from django.test import TestCase

from .services import survival as S
from .services.competing_risks import cumulative_incidence, final_cif
from .services.imputation import mice, rubin_pool
from .services.mixed_model import egfr_slope_lmm, fit_lmm


class MixedModelTests(TestCase):
    def test_recovers_known_slope(self):
        # Simulate eGFR declining 5 mL/min/yr with per-patient random effects.
        rng = random.Random(1)
        clusters = []
        for _ in range(40):
            b0 = rng.gauss(0, 8)        # random intercept
            b1 = rng.gauss(0, 1.5)      # random slope
            y, X, Z = [], [], []
            for t in [0.0, 0.5, 1.0, 1.5, 2.0]:
                val = 80 + b0 + (-5 + b1) * t + rng.gauss(0, 2)
                y.append(val); X.append([1.0, t]); Z.append([1.0, t])
            clusters.append((y, X, Z))
        fit = fit_lmm(clusters, q=2)
        self.assertTrue(fit["converged"])
        # Fixed slope close to the true -5.
        self.assertAlmostEqual(fit["beta"][1], -5.0, delta=1.0)
        # Variance components positive.
        self.assertGreater(fit["D"][0][0], 0)
        self.assertGreater(fit["sigma2"], 0)

    def test_group_slope_difference(self):
        rng = random.Random(2)
        idx = dt.date(2024, 1, 1)
        def series(slope):
            s = []
            for months in (0, 6, 12, 18, 24):
                d = idx + dt.timedelta(days=int(months * 30.4))
                s.append((d, 80 + slope * (months / 12.0) + rng.gauss(0, 2)))
            return s
        groups = {"fast": [series(-8) for _ in range(20)],
                  "slow": [series(-2) for _ in range(20)]}
        res = egfr_slope_lmm(groups)
        # Slopes ordered correctly; difference = slow - fast (second - first) ~ +6.
        self.assertLess(res["slope_fast"], res["slope_slow"])
        self.assertAlmostEqual(abs(res["slope_difference"]), 6.0, delta=2.0)
        self.assertLess(res["p_value"], 0.05)


class CompetingRisksTests(TestCase):
    def test_cif_reduces_to_one_minus_km_without_competing(self):
        # Only cause 1 + censoring -> CIF1 == 1 - KM.
        data = [(2, 1), (3, 1), (5, 0), (6, 1), (8, 1), (9, 0), (10, 1)]
        cif = cumulative_incidence(data, cause=1)
        km = S.kaplan_meier([t for t, _ in data], [s == 1 for _, s in data])
        km_final = km[-1].survival
        self.assertAlmostEqual(final_cif(cif), 1 - km_final, places=3)

    def test_cif_monotone_and_bounded(self):
        data = [(1, 1), (2, 2), (3, 1), (4, 2), (5, 1), (6, 0), (7, 2), (8, 1)]
        c1 = cumulative_incidence(data, cause=1)
        c2 = cumulative_incidence(data, cause=2)
        vals = [s.cif for s in c1]
        self.assertEqual(vals, sorted(vals))             # non-decreasing
        self.assertLessEqual(final_cif(c1) + final_cif(c2), 1.0 + 1e-9)

    def test_competing_death_lowers_cif_vs_naive(self):
        # If some events are reassigned to competing death, CIF of cause 1 is
        # lower than treating those as censored (the whole point of CIF).
        with_competing = [(2, 1), (3, 2), (4, 2), (5, 1), (6, 1), (8, 0)]
        naive_censor = [(2, 1), (3, 0), (4, 0), (5, 1), (6, 1), (8, 0)]
        cif = final_cif(cumulative_incidence(with_competing, cause=1))
        km = S.kaplan_meier([t for t, _ in naive_censor], [s == 1 for _, s in naive_censor])
        naive_incidence = 1 - km[-1].survival
        self.assertLess(cif, naive_incidence)


class MICETests(TestCase):
    def test_pmm_imputes_observed_values_in_range(self):
        rng = random.Random(3)
        data = [[rng.gauss(10, 2), rng.gauss(5, 1)] for _ in range(40)]
        observed_col0 = [r[0] for r in data]
        lo, hi = min(observed_col0), max(observed_col0)
        # Knock out some col-0 values.
        for i in range(0, 40, 5):
            data[i][0] = None
        imps = mice(data, m=3, iterations=5, seed=42)
        for imp in imps:
            for i in range(0, 40, 5):
                self.assertTrue(lo <= imp[i][0] <= hi)    # PMM stays in range

    def test_rubin_pooling_formula(self):
        # T = W + (1 + 1/m) B, with known numbers.
        est = [2.0, 2.4, 2.2]          # mean 2.2
        var = [0.10, 0.12, 0.11]       # W = 0.11
        pooled = rubin_pool(est, var)
        b = ((2.0 - 2.2) ** 2 + 0 + (2.2 - 2.2) ** 2 + (2.4 - 2.2) ** 2) / 2  # 0.04
        self.assertAlmostEqual(pooled["between_var"], 0.04, places=4)
        self.assertAlmostEqual(pooled["within_var"], 0.11, places=4)
        self.assertAlmostEqual(pooled["total_var"], 0.11 + (1 + 1 / 3) * 0.04, places=4)

    def test_mice_recovers_linear_relation(self):
        # y ~ 2x; knock out half of y under MCAR; imputed y should track 2x.
        rng = random.Random(4)
        data = []
        for _ in range(60):
            x = rng.uniform(0, 10)
            y = 2 * x + rng.gauss(0, 0.5)
            data.append([x, y])
        truth = {i: row[1] for i, row in enumerate(data)}
        miss = list(range(0, 60, 2))
        for i in miss:
            data[i][1] = None
        imp = mice(data, m=1, iterations=10, seed=1)[0]
        # Imputed values correlate with the truth (sign + rough magnitude).
        errs = [abs(imp[i][1] - truth[i]) for i in miss]
        self.assertLess(sum(errs) / len(errs), 3.0)

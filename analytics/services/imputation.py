"""
Multiple Imputation by Chained Equations (protocol §10.4) for missing numeric
lab values, with predictive mean matching (PMM) and Rubin's rules pooling.

Pure-Python. PMM imputes each missing cell with an *observed* donor value (the
observed value whose predicted mean is closest), so imputations stay plausible
and within range. Produces ``m`` completed datasets; pool downstream estimates
with ``rubin_pool``.

Validated (tests): imputed values are drawn from observed values (in range);
Rubin's total variance T = W + (1 + 1/m) B; recovers a known linear relation.
"""
from __future__ import annotations

import math
import random

from . import linalg as la


def _ols(X, y):
    Xt = la.transpose(X)
    XtX = la.matmul(Xt, X)
    for i in range(len(XtX)):
        XtX[i][i] += 1e-8           # ridge for numerical stability
    return la.matvec(la.inverse(XtX), la.matvec(Xt, y))


def _col_mean(data, j):
    vals = [row[j] for row in data if row[j] is not None]
    return sum(vals) / len(vals) if vals else 0.0


def mice(data, *, m=5, iterations=10, k=5, seed=0):
    """data: list of rows of floats or None. Returns ``m`` fully-numeric datasets."""
    ncol = len(data[0])
    missing = {j: [i for i, row in enumerate(data) if row[j] is None]
               for j in range(ncol)}
    missing = {j: idx for j, idx in missing.items() if idx}
    observed = {j: [i for i, row in enumerate(data) if row[j] is not None]
                for j in range(ncol)}

    imputations = []
    for rep in range(m):
        rng = random.Random(seed * 1000 + rep)
        cur = [[(_col_mean(data, j) if v is None else v) for j, v in enumerate(row)]
               for row in data]
        for _ in range(iterations):
            for j, miss_idx in missing.items():
                preds = [c for c in range(ncol) if c != j]
                obs_idx = observed[j]
                X_obs = [[1.0] + [cur[i][c] for c in preds] for i in obs_idx]
                y_obs = [data[i][j] for i in obs_idx]
                beta = _ols(X_obs, y_obs)
                yhat_obs = [sum(b * x for b, x in zip(beta, row)) for row in X_obs]
                for i in miss_idx:
                    xi = [1.0] + [cur[i][c] for c in preds]
                    yhat_i = sum(b * x for b, x in zip(beta, xi))
                    # PMM: k nearest observed by predicted mean, pick one at random.
                    donors = sorted(range(len(obs_idx)),
                                    key=lambda o: abs(yhat_obs[o] - yhat_i))[:k]
                    cur[i][j] = y_obs[rng.choice(donors)]
        imputations.append([row[:] for row in cur])
    return imputations


def rubin_pool(estimates, variances):
    """Combine per-imputation estimates Q and their variances U by Rubin's rules.
    Returns the pooled estimate, total variance, SE, and components."""
    m = len(estimates)
    q_bar = sum(estimates) / m
    w = sum(variances) / m                                  # within-imputation
    b = sum((q - q_bar) ** 2 for q in estimates) / (m - 1) if m > 1 else 0.0  # between
    t = w + (1 + 1 / m) * b                                 # total
    se = math.sqrt(t)
    # Rubin degrees of freedom.
    df = (m - 1) * (1 + w / ((1 + 1 / m) * b)) ** 2 if b > 0 else float("inf")
    return {"estimate": q_bar, "within_var": w, "between_var": b,
            "total_var": t, "se": se, "df": df, "m": m}

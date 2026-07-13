"""
Linear mixed-effects model for eGFR slope (protocol §10.3), fit by the
Laird-Ware EM algorithm. Pure-Python, dependency-free.

Model (random intercept + random slope per patient):

    y_ij = X_ij . beta  +  b0_i + b1_i * t_ij  +  eps_ij
    b_i ~ N(0, D)   (2x2),   eps_ij ~ N(0, sigma^2)

The fixed-effect design X carries time and, for a comparison, group and a
group x time interaction — whose coefficient is the difference in eGFR slope
between arms (the key research output), with a standard error and p-value.

Validated (tests) by: recovering a known simulated slope; fixed slope matching
pooled OLS on balanced complete data; positive variance components.
"""
from __future__ import annotations

import math

from . import linalg as la


def fit_lmm(clusters, *, q=2, max_iter=200, tol=1e-6):
    """clusters: list of (y, X, Z) per patient, where y is a list, X and Z are
    lists of rows (fixed and random design). ``q`` = number of random effects.
    Returns fixed effects, their SE, the random-effects covariance D and sigma^2."""
    p = len(clusters[0][1][0])
    n_obs = sum(len(y) for y, _, _ in clusters)
    m = len(clusters)

    # --- initialise: pooled OLS for beta, residual variance, D = I -----------
    XtX = la.zeros(p, p)
    Xty = [0.0] * p
    for y, X, _ in clusters:
        Xt = la.transpose(X)
        XtX = la.add(XtX, la.matmul(Xt, X))
        Xty = [a + b for a, b in zip(Xty, la.matvec(Xt, y))]
    beta = la.matvec(la.inverse(XtX), Xty)
    sse = sum((yi - sum(b * x for b, x in zip(beta, row))) ** 2
              for y, X, _ in clusters for yi, row in zip(y, X))
    sigma2 = max(sse / max(n_obs - p, 1), 1e-6)
    D = la.identity(q)

    converged = False
    for it in range(1, max_iter + 1):
        # --- GLS update of beta with current D, sigma2 -----------------------
        A = la.zeros(p, p)
        rhs = [0.0] * p
        Ws = []
        for y, X, Z in clusters:
            n = len(y)
            ZDZt = la.matmul(la.matmul(Z, D), la.transpose(Z))
            V = la.add(ZDZt, la.scale(la.identity(n), sigma2))
            W = la.inverse(V)
            Ws.append(W)
            Xt = la.transpose(X)
            XtW = la.matmul(Xt, W)
            A = la.add(A, la.matmul(XtW, X))
            rhs = [a + b for a, b in zip(rhs, la.matvec(XtW, y))]
        A_inv = la.inverse(A)
        beta_new = la.matvec(A_inv, rhs)

        # --- E + M step for D and sigma^2 ------------------------------------
        D_new = la.zeros(q, q)
        sig_acc = 0.0
        for (y, X, Z), W in zip(clusters, Ws):
            n = len(y)
            r = [yi - sum(b * x for b, x in zip(beta_new, row)) for yi, row in zip(y, X)]
            Zt = la.transpose(Z)
            DZt = la.matmul(D, Zt)
            b_hat = la.matvec(la.matmul(DZt, W), r)                  # q
            cov = la.add(D, la.scale(la.matmul(la.matmul(DZt, W), la.transpose(DZt)), -1.0))
            D_new = la.add(D_new, la.add(la.outer(b_hat, b_hat), cov))
            # sigma^2 accumulation
            Zb = la.matvec(Z, b_hat)
            e = [ri - zb for ri, zb in zip(r, Zb)]
            ZcovZt = la.matmul(la.matmul(Z, cov), Zt)
            sig_acc += sum(ei * ei for ei in e) + sum(ZcovZt[k][k] for k in range(n))
        D_new = la.scale(D_new, 1.0 / m)
        sigma2_new = max(sig_acc / n_obs, 1e-8)

        delta = max(abs(a - b) for a, b in zip(beta, beta_new))
        beta, D, sigma2 = beta_new, D_new, sigma2_new
        if delta < tol:
            converged = True
            break

    beta_cov = A_inv   # Var(beta) = (sum X' W X)^-1
    se = [math.sqrt(beta_cov[k][k]) if beta_cov[k][k] > 0 else float("nan")
          for k in range(p)]
    return {"beta": beta, "se": se, "D": D, "sigma2": sigma2,
            "n_obs": n_obs, "n_clusters": m, "iterations": it,
            "converged": converged}


from .stats_utils import normal_sf_two_sided as _normal_sf_two_sided  # noqa: E402


def egfr_slope_lmm(series_by_group):
    """Compare eGFR slope between two groups.

    series_by_group: {label: [patient_series, ...]} where each patient_series is
    a list of (date, egfr). Fits eGFR ~ time + group + group:time with random
    intercept + slope per patient. Returns per-group slope (mL/min/1.73m^2 per
    year) and the between-group difference with a p-value."""
    labels = list(series_by_group)
    if len(labels) != 2:
        raise ValueError("egfr_slope_lmm expects exactly two groups.")
    g_ref, g_alt = labels

    clusters = []
    for g_idx, label in enumerate(labels):
        for series in series_by_group[label]:
            pts = sorted(series)
            if len(pts) < 2:
                continue
            t0 = pts[0][0]
            y, X, Z = [], [], []
            for d, v in pts:
                t = (d - t0).days / 365.25
                # Fixed: [intercept, time, group, group*time]
                X.append([1.0, t, float(g_idx), float(g_idx) * t])
                Z.append([1.0, t])     # random intercept + slope
                y.append(float(v))
            clusters.append((y, X, Z))
    if len(clusters) < 2:
        return None

    fit = fit_lmm(clusters, q=2)
    beta, se = fit["beta"], fit["se"]
    slope_ref = beta[1]
    slope_alt = beta[1] + beta[3]
    diff = beta[3]
    z = diff / se[3] if se[3] and not math.isnan(se[3]) else None
    return {
        "groups": labels,
        f"slope_{g_ref}": round(slope_ref, 2),
        f"slope_{g_alt}": round(slope_alt, 2),
        "slope_difference": round(diff, 2),
        "difference_se": round(se[3], 3) if not math.isnan(se[3]) else None,
        "p_value": round(_normal_sf_two_sided(z), 6) if z is not None else None,
        "converged": fit["converged"], "n_patients": fit["n_clusters"],
    }

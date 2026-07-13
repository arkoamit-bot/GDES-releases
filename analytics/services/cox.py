"""
Cox proportional-hazards regression — pure-Python, multivariable.

Newton-Raphson on the Breslow partial log-likelihood. No external dependencies,
so it runs anywhere the registry runs and the arithmetic is fully auditable.

Returns hazard ratios with 95% CIs and Wald p-values for each covariate.

Validation (see tests): for a single binary covariate the Cox *score* test at
beta=0 equals the log-rank statistic, so we assert it reproduces the log-rank
chi-square we already validated against the Freireich dataset; and the full
Newton-Raphson fit recovers a sane hazard ratio with p < 0.001 on that data.

Covariates are mean-centred before fitting (Cox coefficients are invariant to
centring) purely to improve numerical conditioning — reported coefficients are
on the original scale.

Tie handling: Breslow. Efron is a refinement; for data without tied event times
the two are identical.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# --- small linear algebra (p is the number of covariates, typically < 10) ----
def _mat_inverse(A):
    """Invert a square matrix via Gauss-Jordan with partial pivoting."""
    n = len(A)
    M = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)]
         for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            raise ValueError("Singular information matrix (collinear covariates?)")
        M[col], M[piv] = M[piv], M[col]
        pivot = M[col][col]
        M[col] = [v / pivot for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                factor = M[r][col]
                M[r] = [a - factor * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


def _matvec(A, x):
    return [sum(a * xi for a, xi in zip(row, x)) for row in A]


@dataclass
class CoxCovariate:
    name: str
    coef: float
    hr: float
    se: float
    ci_low: float
    ci_high: float
    z: float
    p_value: float


@dataclass
class CoxResult:
    covariates: list[CoxCovariate]
    n: int
    n_events: int
    log_likelihood: float
    iterations: int
    converged: bool

    def as_dict(self):
        return {
            "n": self.n, "n_events": self.n_events,
            "log_likelihood": round(self.log_likelihood, 4),
            "iterations": self.iterations, "converged": self.converged,
            "covariates": [{
                "name": c.name, "coef": round(c.coef, 4), "hr": round(c.hr, 4),
                "se": round(c.se, 4),
                "hr_ci_low": round(c.ci_low, 4), "hr_ci_high": round(c.ci_high, 4),
                "z": round(c.z, 4), "p_value": round(c.p_value, 6),
            } for c in self.covariates],
        }


from .stats_utils import normal_sf_two_sided as _normal_sf_two_sided  # noqa: E402


def _event_time_groups(durations, events):
    """Distinct event times (ascending) -> list of subject indices with an event
    at that time."""
    from collections import defaultdict
    groups = defaultdict(list)
    for i, (t, e) in enumerate(zip(durations, events)):
        if e:
            groups[float(t)].append(i)
    return sorted(groups.items())


def _score_and_information(X, durations, events, beta):
    """Breslow gradient U (p) and observed information matrix I (p x p)."""
    n = len(X)
    p = len(beta)
    times = [float(t) for t in durations]
    U = [0.0] * p
    I = [[0.0] * p for _ in range(p)]
    loglik = 0.0

    for t, event_idx in _event_time_groups(durations, events):
        risk = [j for j in range(n) if times[j] >= t]
        d = len(event_idx)
        thetas = {j: math.exp(sum(beta[k] * X[j][k] for k in range(p))) for j in risk}
        S0 = sum(thetas.values())
        S1 = [sum(thetas[j] * X[j][k] for j in risk) for k in range(p)]
        S2 = [[sum(thetas[j] * X[j][k] * X[j][l] for j in risk)
               for l in range(p)] for k in range(p)]
        mean = [S1[k] / S0 for k in range(p)]

        for i in event_idx:
            loglik += sum(beta[k] * X[i][k] for k in range(p))
            for k in range(p):
                U[k] += X[i][k]
        loglik -= d * math.log(S0)
        for k in range(p):
            U[k] -= d * mean[k]
            for l in range(p):
                I[k][l] += d * (S2[k][l] / S0 - mean[k] * mean[l])
    return U, I, loglik


def cox_fit(X, durations, events, names, *, max_iter=50, tol=1e-7) -> CoxResult:
    n = len(X)
    p = len(names)
    if n == 0 or p == 0:
        raise ValueError("Empty design matrix.")
    n_events = sum(1 for e in events if e)
    if n_events == 0:
        raise ValueError("No events — cannot fit Cox model.")

    # Mean-centre (invariant; improves conditioning).
    means = [sum(X[i][k] for i in range(n)) / n for k in range(p)]
    Xc = [[X[i][k] - means[k] for k in range(p)] for i in range(n)]

    beta = [0.0] * p
    converged = False
    last_ll = None
    it = 0
    for it in range(1, max_iter + 1):
        U, I, loglik = _score_and_information(Xc, durations, events, beta)
        cov = _mat_inverse(I)
        delta = _matvec(cov, U)
        beta = [b + d for b, d in zip(beta, delta)]
        if max(abs(d) for d in delta) < tol:
            converged = True
            last_ll = loglik
            break
        last_ll = loglik

    U, I, loglik = _score_and_information(Xc, durations, events, beta)
    cov = _mat_inverse(I)
    z975 = 1.96

    covariates = []
    for k, name in enumerate(names):
        coef = beta[k]
        se = math.sqrt(cov[k][k]) if cov[k][k] > 0 else float("nan")
        z = coef / se if se else float("nan")
        covariates.append(CoxCovariate(
            name=name, coef=coef, hr=math.exp(coef), se=se,
            ci_low=math.exp(coef - z975 * se), ci_high=math.exp(coef + z975 * se),
            z=z, p_value=_normal_sf_two_sided(z)))

    return CoxResult(covariates=covariates, n=n, n_events=n_events,
                     log_likelihood=loglik, iterations=it, converged=converged)


def cox_score_test(X, durations, events):
    """Global score (log-rank-type) test at beta=0: U0' I0^-1 U0.
    For a single binary covariate this equals the two-group log-rank chi-square
    (Breslow) — used to cross-validate against the validated log-rank routine."""
    p = len(X[0])
    U, I, _ = _score_and_information(X, durations, events, [0.0] * p)
    cov = _mat_inverse(I)
    Uc = _matvec(cov, U)
    chi2 = sum(U[k] * Uc[k] for k in range(p))
    return chi2, _chi2_sf(chi2, p)


def _chi2_sf(x, df):
    """Survival function of chi-square. df=1 exact; general df via regularized
    upper incomplete gamma (Lanczos-free series/continued-fraction)."""
    if x <= 0:
        return 1.0
    if df == 1:
        return math.erfc(math.sqrt(x / 2.0))
    return _gammaincc(df / 2.0, x / 2.0)


def _gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a,x), via series/CF (Numerical
    Recipes style). Good enough for p-value reporting."""
    if x < a + 1.0:
        # series for P(a,x), then Q = 1-P
        ap = a
        s = 1.0 / a
        d = s
        for _ in range(200):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-12:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # continued fraction for Q(a,x)
    b = x + 1.0 - a
    c = 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 200):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

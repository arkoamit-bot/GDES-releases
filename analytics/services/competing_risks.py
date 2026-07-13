"""
Competing-risks cumulative incidence (protocol §10.4): for kidney endpoints,
non-renal death is a COMPETING event, not censoring. The cause-specific
cumulative incidence function (CIF, Aalen-Johansen) estimates the probability of
the kidney event over time while properly accounting for death.

Input is a list of (time, status) where status is 0 = censored, 1 = event of
interest (e.g. ESKD), 2 = competing event (non-renal death).

Validated (tests): with no competing events the CIF reduces to 1 - Kaplan-Meier;
CIF is monotone non-decreasing; CIF1 + CIF2 <= 1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class CIFStep:
    time: float
    n_risk: int
    n_events: int          # cause of interest at this time
    cif: float
    variance: float
    se: float
    ci_low: float
    ci_high: float


def _grouped(data):
    from collections import defaultdict
    d1 = defaultdict(int)   # cause of interest
    dall = defaultdict(int)
    cens = defaultdict(int)
    for t, s in data:
        t = float(t)
        if s == 1:
            d1[t] += 1
            dall[t] += 1
        elif s == 2:
            dall[t] += 1
        else:
            cens[t] += 1
    times = sorted(set(d1) | set(dall) | set(cens))
    return times, d1, dall, cens


def cumulative_incidence(data, *, cause=1, confidence=0.95):
    """Cause-specific CIF with Aalen variance. ``data`` uses 1 = cause of
    interest, 2 = competing, 0 = censored."""
    # Re-map so the requested cause is "1".
    remapped = [(t, 1 if s == cause else (2 if s not in (0, cause) else (0 if s == 0 else 2)))
                for t, s in data]
    times, d1, dall, cens = _grouped(remapped)
    n = len(remapped)

    at_risk = n
    surv_prev = 1.0          # S(t_{j-1}), all-cause KM just before t_j
    cif = 0.0
    steps: list[CIFStep] = []
    # Accumulators for the variance terms that depend on running CIF.
    hist = []                # (t_j, surv_prev_j, d1_j, dall_j, n_j, cif_j)
    z = {0.90: 1.6449, 0.95: 1.96, 0.99: 2.5758}.get(confidence, 1.96)

    for t in times:
        nj = at_risk
        d1j = d1.get(t, 0)
        dallj = dall.get(t, 0)
        if dallj > 0:
            cif += surv_prev * d1j / nj
            hist.append((surv_prev, d1j, dallj, nj, cif))
            var = _cif_variance(hist, cif)
            se = math.sqrt(var) if var > 0 else 0.0
            steps.append(CIFStep(
                t, nj, d1j, round(cif, 4), round(var, 8), round(se, 4),
                round(max(0.0, cif - z * se), 4), round(min(1.0, cif + z * se), 4)))
            surv_prev = surv_prev * (1 - dallj / nj)
        at_risk -= (dallj + cens.get(t, 0))
    return steps


def _cif_variance(hist, cif_t):
    """Aalen / delta-method variance of CIF at the latest time (Klein-Moeschberger)."""
    var = 0.0
    for surv_prev, d1j, dallj, nj, cif_j in hist:
        if nj - dallj > 0:
            var += ((cif_t - cif_j) ** 2) * dallj / (nj * (nj - dallj))
        var += (surv_prev ** 2) * ((nj - d1j) / nj) * (d1j / (nj ** 2))
        var -= 2 * (cif_t - cif_j) * surv_prev * (d1j / (nj ** 2))
    return max(var, 0.0)


def cif_at(steps, t):
    val = 0.0
    for s in steps:
        if s.time <= t:
            val = s.cif
        else:
            break
    return val


def final_cif(steps):
    return steps[-1].cif if steps else 0.0


def compare_cif_at(data1, data2, t, *, cause=1):
    """Pointwise z-test of the CIF difference between two groups at time t."""
    s1 = cumulative_incidence(data1, cause=cause)
    s2 = cumulative_incidence(data2, cause=cause)
    c1, c2 = cif_at(s1, t), cif_at(s2, t)
    v1 = next((s.variance for s in reversed(s1) if s.time <= t), 0.0)
    v2 = next((s.variance for s in reversed(s2) if s.time <= t), 0.0)
    se = math.sqrt(v1 + v2)
    z = (c1 - c2) / se if se > 0 else None
    p = math.erfc(abs(z) / math.sqrt(2.0)) if z is not None else None
    return {"time": t, "cif_group1": round(c1, 4), "cif_group2": round(c2, 4),
            "difference": round(c1 - c2, 4),
            "z": round(z, 4) if z is not None else None,
            "p_value": round(p, 6) if p is not None else None}

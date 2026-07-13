"""
Survival analysis — pure-Python, dependency-free, auditable.

Implements the estimators a glomerular-disease registry needs:
  * Kaplan-Meier survival function with Greenwood variance + 95% CI
  * Nelson-Aalen cumulative hazard
  * Median survival time
  * Two-group log-rank test (chi-square, 1 df, with p-value)
  * Person-time incidence rate

Input everywhere is a list of (duration, event) pairs, where ``duration`` is the
time from index date to event-or-censoring and ``event`` is True if the endpoint
occurred (False = censored). Durations are in days; helpers convert to years.

Validated against the classic Freireich 6-MP leukaemia dataset (see tests).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class KMStep:
    time: float
    n_risk: int
    n_events: int
    n_censored: int
    survival: float
    se: float          # standard error of S(t) (Greenwood)
    ci_low: float
    ci_high: float


def _z(confidence: float) -> float:
    # Two-sided normal quantile for common confidence levels.
    return {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}.get(confidence, 1.9600)


def _grouped(durations, events):
    """Collapse to per-time-point (n_events, n_censored), ascending by time."""
    from collections import defaultdict
    ev = defaultdict(int)
    ce = defaultdict(int)
    for d, e in zip(durations, events):
        d = float(d)
        if e:
            ev[d] += 1
        else:
            ce[d] += 1
    times = sorted(set(ev) | set(ce))
    return times, ev, ce


def kaplan_meier(durations, events, confidence: float = 0.95) -> list[KMStep]:
    """Kaplan-Meier estimate. Returns one KMStep per distinct event time."""
    n = len(durations)
    times, ev, ce = _grouped(durations, events)
    at_risk = n
    surv = 1.0
    greenwood_sum = 0.0   # cumulative sum d/(n*(n-d))
    z = _z(confidence)
    steps: list[KMStep] = []

    for t in times:
        d = ev[t]
        c = ce[t]
        if d > 0:
            surv *= (1.0 - d / at_risk)
            if at_risk - d > 0:
                greenwood_sum += d / (at_risk * (at_risk - d))
            se = surv * math.sqrt(greenwood_sum)
            # Linear (Greenwood) CI, clamped to [0, 1].
            lo = max(0.0, surv - z * se)
            hi = min(1.0, surv + z * se)
            steps.append(KMStep(t, at_risk, d, c, round(surv, 4),
                                round(se, 4), round(lo, 4), round(hi, 4)))
        at_risk -= (d + c)
    return steps


def median_survival(steps: list[KMStep]):
    """Smallest time at which survival drops to <= 0.5, or None if never."""
    for s in steps:
        if s.survival <= 0.5:
            return s.time
    return None


def survival_at(steps: list[KMStep], t: float):
    """Survival probability at time t (step function: last step with time<=t)."""
    s = 1.0
    for step in steps:
        if step.time <= t:
            s = step.survival
        else:
            break
    return s


@dataclass
class NAStep:
    time: float
    n_risk: int
    n_events: int
    cum_hazard: float


def nelson_aalen(durations, events) -> list[NAStep]:
    """Nelson-Aalen cumulative hazard estimate."""
    n = len(durations)
    times, ev, ce = _grouped(durations, events)
    at_risk = n
    H = 0.0
    steps: list[NAStep] = []
    for t in times:
        d = ev[t]
        if d > 0:
            H += d / at_risk
            steps.append(NAStep(t, at_risk, d, round(H, 4)))
        at_risk -= (d + ce[t])
    return steps


@dataclass
class LogRankResult:
    chi_square: float
    p_value: float
    df: int
    observed_group1: float
    expected_group1: float
    n1: int
    n2: int


def _chi2_sf_1df(x: float) -> float:
    """Survival function (1 - CDF) of chi-square with 1 df. Exact, pure-Python:
    P(X > x) = erfc(sqrt(x/2))."""
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0))


def logrank_test(durations1, events1, durations2, events2) -> LogRankResult:
    """Two-group log-rank test. Compares the survival of group 1 vs group 2."""
    # Merge all event times across both groups.
    _, ev1, ce1 = _grouped(durations1, events1)
    _, ev2, ce2 = _grouped(durations2, events2)
    all_times = sorted(set(ev1) | set(ce1) | set(ev2) | set(ce2))

    n1, n2 = len(durations1), len(durations2)
    at_risk1, at_risk2 = n1, n2
    sum_obs1 = 0.0
    sum_exp1 = 0.0
    sum_var = 0.0

    for t in all_times:
        d1, d2 = ev1.get(t, 0), ev2.get(t, 0)
        d = d1 + d2
        n = at_risk1 + at_risk2
        if d > 0 and n > 1:
            exp1 = d * (at_risk1 / n)
            var = (d * (at_risk1 / n) * (at_risk2 / n)
                   * ((n - d) / (n - 1)))
            sum_obs1 += d1
            sum_exp1 += exp1
            sum_var += var
        at_risk1 -= (d1 + ce1.get(t, 0))
        at_risk2 -= (d2 + ce2.get(t, 0))

    chi2 = ((sum_obs1 - sum_exp1) ** 2 / sum_var) if sum_var > 0 else 0.0
    return LogRankResult(
        chi_square=round(chi2, 4), p_value=round(_chi2_sf_1df(chi2), 6),
        df=1, observed_group1=round(sum_obs1, 2),
        expected_group1=round(sum_exp1, 2), n1=n1, n2=n2)


def incidence_rate(durations, events, *, per=100, time_unit_days=365.25):
    """Crude incidence rate = events / person-time, scaled by ``per``.
    Returns (rate, n_events, person_time_years)."""
    person_time = sum(float(d) for d in durations) / time_unit_days
    n_events = sum(1 for e in events if e)
    rate = (n_events / person_time * per) if person_time > 0 else None
    return rate, n_events, round(person_time, 2)

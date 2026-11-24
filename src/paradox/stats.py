# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Seed-level uncertainty (protocol section 5): Student t intervals, percentile
bootstrap and Holm adjustment, without SciPy. The seed-run is the independent
unit; callers pass one value per seed."""

from __future__ import annotations

from math import exp, isfinite, lgamma, log, sqrt

import numpy as np

__all__ = ["t_cdf", "t_quantile", "t_interval", "one_sided_p_negative", "bootstrap_interval", "holm", "summarise"]


def _betacf(a: float, b: float, x: float) -> float:
    # Continued fraction for the regularized incomplete beta (modified Lentz).
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: float) -> float:
    """CDF of Student's t with ``df`` degrees of freedom."""
    if not df > 0 or not isfinite(df):
        raise ValueError("df must be positive and finite")
    if not isfinite(t):
        return 0.0 if t < 0 else 1.0
    x = df / (df + t * t)
    tail = 0.5 * _betainc(df / 2.0, 0.5, x)
    return tail if t < 0 else 1.0 - tail


def t_quantile(prob: float, df: float) -> float:
    """Quantile of Student's t by bisection (absolute tolerance 1e-12)."""
    if not 0.0 < prob < 1.0:
        raise ValueError("prob must be in (0, 1)")
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < prob:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


def _values(x) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    if a.ndim != 1 or a.size < 2 or not np.all(np.isfinite(a)):
        raise ValueError("need a 1-D array of at least two finite values (one per seed)")
    return a


def t_interval(x, level: float = 0.95) -> tuple[float, float]:
    a = _values(x)
    n = a.size
    se = a.std(ddof=1) / sqrt(n)
    q = t_quantile(0.5 + level / 2.0, n - 1)
    m = float(a.mean())
    return (m - q * se, m + q * se)


def one_sided_p_negative(x) -> float:
    """One-sided p-value for H0: mean >= 0 against H1: mean < 0 (t test).

    Returns 1.0 for zero variance (up to rounding) with a non-negative mean, 0.0 for zero
    variance with a negative mean."""
    a = _values(x)
    sd = a.std(ddof=1)
    m = float(a.mean())
    if sd <= 1e-12 * max(1.0, abs(m)):  # constant up to rounding
        return 0.0 if m < 0 else 1.0
    return t_cdf(m / (sd / sqrt(a.size)), a.size - 1)


def bootstrap_interval(x, level: float = 0.95, n_resamples: int = 10_000, seed: int = 0) -> tuple[float, float]:
    """Seed-level percentile bootstrap of the mean, fixed bootstrap seed."""
    a = _values(x)
    if n_resamples < 1:
        raise ValueError("n_resamples must be positive")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, a.size, size=(n_resamples, a.size))
    means = a[idx].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return (float(lo), float(hi))


def holm(pvalues) -> list[float]:
    """Holm step-down adjusted p-values (monotone, capped at 1)."""
    p = [float(v) for v in pvalues]
    if any(not 0.0 <= v <= 1.0 for v in p):
        raise ValueError("p-values must lie in [0, 1]")
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj


def summarise(x, bootstrap_seed: int = 0, n_resamples: int = 10_000) -> dict:
    a = _values(x)
    t_lo, t_hi = t_interval(a)
    b_lo, b_hi = bootstrap_interval(a, seed=bootstrap_seed, n_resamples=n_resamples)
    return {
        "n_seeds": int(a.size),
        "mean": float(a.mean()),
        "sd": float(a.std(ddof=1)),
        "t95_low": t_lo,
        "t95_high": t_hi,
        "boot95_low": b_lo,
        "boot95_high": b_hi,
        "p_one_sided_negative": one_sided_p_negative(a),
        "per_seed": [float(v) for v in a],
    }

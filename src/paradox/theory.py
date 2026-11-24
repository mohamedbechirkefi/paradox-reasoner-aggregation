# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Closed-form accuracy of simple majority voting (protocol section 2.7).

All functions are pure and deterministic. Probabilities are dimensionless
numbers in [0, 1]; ``n`` is a number of reasoners (one call each). Invalid
inputs raise ``ValueError``; no function silently clamps.
"""

from __future__ import annotations

from math import comb, exp, isfinite, lgamma, sqrt

__all__ = [
    "binom_tail",
    "condorcet",
    "common_shock",
    "mixture",
    "bahadur_k_distribution",
    "bahadur_admissible",
    "bahadur_mv",
    "bahadur_mv_enumerated",
    "beta_binomial_mv",
    "mixture_params_for_correlation",
    "beta_params_for_correlation",
    "common_shock_lambda_for_correlation",
    "asymptotic_mv_accuracy",
    "predicted_mv_degrades",
]


def _check_prob(name: str, x: float) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError(f"{name} must be a real number, got {x!r}")
    x = float(x)
    if not isfinite(x) or x < 0.0 or x > 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {x}")
    return x


def _check_n(n: int, *, odd: bool) -> int:
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"n must be an int, got {n!r}")
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if odd and n % 2 == 0:
        raise ValueError(f"n must be odd for a strict majority without ties, got {n}")
    return n


def binom_tail(n: int, p: float, k: int) -> float:
    """P(Bin(n, p) >= k), by an exact finite sum. ``n`` may be 0."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError(f"n must be a non-negative int, got {n!r}")
    p = _check_prob("p", p)
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    q = 1.0 - p
    return float(sum(comb(n, t) * p**t * q ** (n - t) for t in range(k, n + 1)))


def condorcet(n: int, p: float) -> float:
    """Majority accuracy of ``n`` (odd) independent reasoners of competence ``p``."""
    n = _check_n(n, odd=True)
    return binom_tail(n, p, (n + 1) // 2)


def common_shock(n: int, p: float, lam: float) -> float:
    """Majority accuracy under the common-shock (opinion-leader) model.

    Each of ``n`` (odd) reasoners adopts a shared latent answer, correct with
    probability ``p``, with probability ``lam``; otherwise it answers privately
    and is correct with probability ``p``.
    """
    n = _check_n(n, odd=True)
    p = _check_prob("p", p)
    lam = _check_prob("lambda", lam)
    m = (n + 1) // 2
    total = 0.0
    for k in range(n + 1):
        weight = comb(n, k) * lam**k * (1.0 - lam) ** (n - k)
        if weight == 0.0:
            continue
        total += weight * (p * binom_tail(n - k, p, m - k) + (1.0 - p) * binom_tail(n - k, p, m))
    return float(total)


def mixture(n: int, p_easy: float, h: float, p_hard: float | None, lam: float) -> float:
    """Two-class difficulty mixture: ``(1-h) G(n,p_easy,lam) + h G(n,p_hard,lam)``."""
    h = _check_prob("h", h)
    easy = common_shock(n, p_easy, lam)
    if h == 0.0:
        return easy
    if p_hard is None:
        raise ValueError("p_hard is required when h > 0")
    return float((1.0 - h) * easy + h * common_shock(n, p_hard, lam))


def _check_open_prob(name: str, x: float) -> float:
    x = _check_prob(name, x)
    if x in (0.0, 1.0):
        raise ValueError(f"{name} must be in (0, 1) for the Bahadur model, got {x}")
    return x


def bahadur_k_distribution(n: int, p: float, c: float) -> list[float]:
    """P(K = k), k = 0..n, for the homogeneous Bahadur second-order model.

    Profile probability: prod p^x q^(1-x) * (1 + c * sum_{j<l} z_j z_l), with
    z = (x - p) / sqrt(pq). For a profile with ``k`` correct reasoners the pair
    sum is C(k,2) q/p + C(n-k,2) p/q - k(n-k). Values can be negative when the
    model is inadmissible; see :func:`bahadur_admissible`.
    """
    n = _check_n(n, odd=False)
    p = _check_open_prob("p", p)
    if isinstance(c, bool) or not isinstance(c, (int, float)) or not isfinite(c):
        raise ValueError(f"c must be a finite real number, got {c!r}")
    q = 1.0 - p
    out = []
    for k in range(n + 1):
        pair_sum = comb(k, 2) * q / p + comb(n - k, 2) * p / q - k * (n - k)
        out.append(comb(n, k) * p**k * q ** (n - k) * (1.0 + c * pair_sum))
    return out


def bahadur_admissible(n: int, p: float, c: float, tol: float = 1e-15) -> bool:
    """True if every profile probability of the Bahadur model is non-negative."""
    return all(v >= -tol for v in bahadur_k_distribution(n, p, c))


def bahadur_mv(n: int, p: float, c: float) -> float:
    """Kaniovski (2008), Theorem 1: majority accuracy in the Bahadur model.

    ``M_n(p) + c n(n-1)(0.5-p) C(n-2,(n-1)/2) (pq)^((n-1)/2)`` for odd ``n``.
    Raises ``ValueError`` if the model is inadmissible at ``(n, p, c)``.
    """
    n = _check_n(n, odd=True)
    p = _check_open_prob("p", p)
    if not bahadur_admissible(n, p, c):
        raise ValueError(f"Bahadur model inadmissible at n={n}, p={p}, c={c}")
    base = condorcet(n, p)
    if n == 1:
        return base
    q = 1.0 - p
    corr = c * n * (n - 1) * (0.5 - p) * comb(n - 2, (n - 1) // 2) * (p * q) ** ((n - 1) / 2)
    return float(base + corr)


def bahadur_mv_enumerated(n: int, p: float, c: float) -> float:
    """Majority accuracy in the Bahadur model by summing P(K = k) over k > n/2.

    Independent of the Theorem 1 closed form; used as a differential reference.
    """
    n = _check_n(n, odd=True)
    if not bahadur_admissible(n, p, c):
        raise ValueError(f"Bahadur model inadmissible at n={n}, p={p}, c={c}")
    dist = bahadur_k_distribution(n, p, c)
    return float(sum(dist[(n + 1) // 2 :]))


def _log_beta(a: float, b: float) -> float:
    return lgamma(a) + lgamma(b) - lgamma(a + b)


def beta_binomial_mv(n: int, a: float, b: float) -> float:
    """Majority accuracy when item competence ``p_i ~ Beta(a, b)`` and votes are
    conditionally independent: ``P(BetaBin(n, a, b) >= (n+1)/2)``."""
    n = _check_n(n, odd=True)
    for name, v in (("a", a), ("b", b)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or v <= 0:
            raise ValueError(f"{name} must be a positive finite number, got {v!r}")
    lb = _log_beta(a, b)
    m = (n + 1) // 2
    return float(sum(comb(n, t) * exp(_log_beta(a + t, b + n - t) - lb) for t in range(m, n + 1)))


def common_shock_lambda_for_correlation(r: float) -> float:
    """Common-shock adoption probability giving pairwise correctness correlation ``r``."""
    r = _check_prob("r", r)
    return sqrt(r)


def mixture_params_for_correlation(p: float, r: float) -> tuple[float, float, float]:
    """Symmetric two-class mixture ``(p_easy, h, p_hard)`` with mean ``p`` and
    pairwise correctness correlation ``r``: ``h = 0.5``, ``p +/- d``,
    ``d = sqrt(r p q)`` (the correlation is ``Var(p_i) / (p q) = d^2 / (p q)``).
    Raises ``ValueError`` if ``p +/- d`` leaves [0, 1]."""
    p = _check_open_prob("p", p)
    r = _check_prob("r", r)
    d = sqrt(r * p * (1.0 - p))
    if p + d > 1.0 or p - d < 0.0:
        raise ValueError(f"no admissible symmetric mixture at p={p}, r={r}")
    return (p + d, 0.5, p - d)


def beta_params_for_correlation(p: float, r: float) -> tuple[float, float]:
    """Beta(a, b) with mean ``p`` and intra-class correlation ``1/(a+b+1) = r``."""
    p = _check_open_prob("p", p)
    r = _check_prob("r", r)
    if r == 0.0 or r == 1.0:
        raise ValueError("r must be in (0, 1) for a Beta difficulty model")
    s = 1.0 / r - 1.0
    return (p * s, (1.0 - p) * s)


def asymptotic_mv_accuracy(p_easy: float, h: float, p_hard: float | None) -> float:
    """Large-``n`` MV accuracy at ``lambda = 0`` for the two-class mixture.

    A class with competence above 0.5 contributes 1, below 0.5 contributes 0,
    exactly 0.5 contributes 0.5 (Condorcet limit)."""

    def lim(p: float) -> float:
        p = _check_prob("p", p)
        return 1.0 if p > 0.5 else (0.0 if p < 0.5 else 0.5)

    h = _check_prob("h", h)
    if h > 0 and p_hard is None:
        raise ValueError("p_hard is required when h > 0")
    return (1.0 - h) * lim(p_easy) + (h * lim(p_hard) if h > 0 else 0.0)


def predicted_mv_degrades(p_easy: float, h: float, p_hard: float | None) -> bool:
    """Protocol prediction P1: large-``n`` MV is less accurate than one reasoner,
    i.e. ``asymptotic_mv_accuracy < mu``."""
    h = _check_prob("h", h)
    mu = (1.0 - h) * _check_prob("p_easy", p_easy) + (h * _check_prob("p_hard", p_hard) if h > 0 else 0.0)
    return asymptotic_mv_accuracy(p_easy, h, p_hard) < mu

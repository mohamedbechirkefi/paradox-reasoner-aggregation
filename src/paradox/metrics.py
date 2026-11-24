# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Per-run metrics (protocol sections 3 and 4). All metrics are proportions in
[0, 1] except the cost proxies (calls or messages per item)."""

from __future__ import annotations

import numpy as np

from .rules import RuleOutput

__all__ = ["accuracy", "brier", "ece", "disagreement", "rule_metrics", "paired_delta"]


def _as_1d(name: str, x: np.ndarray) -> np.ndarray:
    a = np.asarray(x)
    if a.ndim != 1 or a.size == 0:
        raise ValueError(f"{name} must be a non-empty 1-D array")
    return a


def accuracy(decision_correct: np.ndarray) -> float:
    """``A = (1/I) sum 1[yhat = y]``."""
    a = _as_1d("decision_correct", decision_correct)
    if a.dtype != bool:
        raise ValueError("decision_correct must be boolean")
    return float(a.mean())


def brier(q_true: np.ndarray) -> float:
    """``(1/I) sum (1 - q_i)^2``, ``q_i`` the probability on the true answer."""
    q = _as_1d("q_true", q_true).astype(float)
    if np.any((q < 0) | (q > 1)) or not np.all(np.isfinite(q)):
        raise ValueError("q_true must lie in [0, 1]")
    return float(np.mean((1.0 - q) ** 2))


def ece(p_chosen: np.ndarray, decision_correct: np.ndarray, n_bins: int = 10) -> float:
    """Expected calibration error over ``n_bins`` equal-width bins of [0, 1] of
    the probability assigned to the chosen answer; the value 1.0 falls in the
    last bin."""
    p = _as_1d("p_chosen", p_chosen).astype(float)
    c = _as_1d("decision_correct", decision_correct)
    if p.shape != c.shape:
        raise ValueError("p_chosen and decision_correct must have the same shape")
    if isinstance(n_bins, bool) or not isinstance(n_bins, int) or n_bins < 1:
        raise ValueError("n_bins must be a positive int")
    if np.any((p < 0) | (p > 1)) or not np.all(np.isfinite(p)):
        raise ValueError("p_chosen must lie in [0, 1]")
    idx = np.minimum((p * n_bins).astype(int), n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(c[m].mean() - p[m].mean())
    return float(total)


def disagreement(votes_correct: np.ndarray, n_votes: int) -> tuple[float, float]:
    """(share of items with a non-unanimous vote, mean pairwise disagreement).

    For ``k`` correct among ``n`` binary votes, pairwise disagreement is
    ``2 k (n - k) / (n (n - 1))``. Both are 0 when ``n = 1``."""
    k = _as_1d("votes_correct", votes_correct).astype(np.int64)
    if isinstance(n_votes, bool) or not isinstance(n_votes, int) or n_votes < 1:
        raise ValueError("n_votes must be a positive int")
    if np.any((k < 0) | (k > n_votes)):
        raise ValueError("votes_correct must lie in [0, n_votes]")
    if n_votes == 1:
        return 0.0, 0.0
    share = float(np.mean((k > 0) & (k < n_votes)))
    pair = float(np.mean(2.0 * k * (n_votes - k) / (n_votes * (n_votes - 1))))
    return share, pair


def rule_metrics(out: RuleOutput) -> dict:
    acc = accuracy(out.decision_correct)
    share, pair = disagreement(out.votes_correct, out.n_votes)
    return {
        "rule": out.rule,
        "budget": out.budget,
        "n_reasoners": out.n_reasoners,
        "calls_per_item": out.calls_per_item,
        "messages_per_item": out.messages_per_item,
        "accuracy": acc,
        "brier": brier(out.q_true),
        "ece": ece(out.p_chosen, out.decision_correct),
        "disagreement_share": share,
        "pairwise_disagreement": pair,
        "accuracy_per_call": (acc - 0.5) / out.calls_per_item,
        "tie_share": float(out.tie.mean()),
    }


def paired_delta(treatment: np.ndarray, baseline: np.ndarray) -> float:
    """Mean per-item paired difference in correctness (same items, same run)."""
    t = _as_1d("treatment", treatment)
    b = _as_1d("baseline", baseline)
    if t.shape != b.shape:
        raise ValueError("paired arrays must have the same shape")
    return float(np.mean(t.astype(float) - b.astype(float)))

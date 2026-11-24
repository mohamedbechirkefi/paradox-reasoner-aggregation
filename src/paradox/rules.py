# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Aggregation rules (protocol section 2.5). Pure functions of a RunDraws.

Every rule returns a :class:`RuleOutput`. Budget accounting: one reasoner call
is one unit; ``calls_per_item`` is what the rule actually consumed. Messages
read count earlier votes a reasoner sees (SEQ) or round-0 answers it reads
(DELIB), for the EXP-004 secondary cost proxy.

Ties (possible only with an even number of votes, or an exact weight tie in
CW) are resolved by the run's seeded ``tie_coin``; a tie never counts as
correct without the coin. MV and SEQ also accept the EXP-004 tie rule
``abstain_wrong``: a tied vote abstains and the abstention is scored as wrong.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .generator import RunDraws

__all__ = ["RuleOutput", "RULES", "TIE_RULES", "single", "majority", "confidence_weighted", "sequential", "deliberation", "apply_rule"]

RULES = ("SINGLE", "MV", "CW", "SEQ", "DELIB")
TIE_RULES = ("coin", "abstain_wrong")


@dataclass(frozen=True)
class RuleOutput:
    rule: str
    budget: int
    n_reasoners: int
    calls_per_item: int
    messages_per_item: int
    decision_correct: np.ndarray  # bool (I,)
    q_true: np.ndarray  # probability the rule assigns to the true answer (I,)
    p_chosen: np.ndarray  # probability the rule assigns to its chosen answer (I,)
    votes_correct: np.ndarray  # number of final-stage votes that are correct (I,)
    n_votes: int
    tie: np.ndarray  # bool (I,)


def _check_n(d: RunDraws, n: int) -> int:
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise ValueError(f"number of reasoners must be an int, got {n!r}")
    n = int(n)
    if n < 1:
        raise ValueError(f"number of reasoners must be >= 1, got {n}")
    if n > d.n_reasoners:
        raise ValueError(f"number of reasoners {n} exceeds the draw table width {d.n_reasoners}")
    return n


def _majority_from_counts(k: np.ndarray, n: int, coin: np.ndarray, tie_rule: str = "coin") -> tuple[np.ndarray, np.ndarray]:
    """Decision correctness from correct-vote counts; returns (correct, tie).

    ``tie_rule="coin"`` resolves a tie by the seeded coin; ``"abstain_wrong"``
    scores a tie as wrong (EXP-004 tie-rule level)."""
    if tie_rule not in TIE_RULES:
        raise ValueError(f"unknown tie rule {tie_rule!r}; expected one of {TIE_RULES}")
    twice = 2 * k
    tie = twice == n
    resolved = coin if tie_rule == "coin" else np.zeros_like(tie)
    return np.where(tie, resolved, twice > n), tie


def _vote_share_output(rule: str, budget: int, n: int, calls: int, msgs: int, votes: np.ndarray, coin: np.ndarray,
                       tie_rule: str = "coin") -> RuleOutput:
    k = votes.sum(axis=1)
    decision, tie = _majority_from_counts(k, n, coin, tie_rule)
    q_true = k / n
    p_chosen = np.where(decision, q_true, 1.0 - q_true)
    return RuleOutput(rule, budget, n, calls, msgs, decision, q_true, p_chosen, k.astype(np.int64), n, tie)


def single(d: RunDraws) -> RuleOutput:
    """Baseline: reasoner 0, one call. Its probability output is its confidence."""
    c = d.conf[:, 0]
    correct = d.correct[:, 0]
    q_true = np.where(correct, c, 1.0 - c)
    return RuleOutput("SINGLE", 1, 1, 1, 0, correct.copy(), q_true, c.copy(), correct.astype(np.int64), 1, np.zeros(d.n_items, bool))


def majority(d: RunDraws, n: int, tie_rule: str = "coin") -> RuleOutput:
    """Simple majority of reasoners ``0..n-1``; budget ``n`` calls."""
    n = _check_n(d, n)
    return _vote_share_output("MV", n, n, n, 0, d.correct[:, :n], d.tie_coin, tie_rule)


def confidence_weighted(d: RunDraws, n: int) -> RuleOutput:
    """Vote weighted by ``logit(c)``; probability output is the weight share."""
    n = _check_n(d, n)
    c = d.conf[:, :n]
    wts = np.log(c / (1.0 - c))
    votes = d.correct[:, :n]
    s_true = (wts * votes).sum(axis=1)
    s_all = wts.sum(axis=1)
    s_false = s_all - s_true
    tie = s_true == s_false
    decision = np.where(tie, d.tie_coin, s_true > s_false)
    q_true = s_true / s_all
    p_chosen = np.where(decision, q_true, 1.0 - q_true)
    k = votes.sum(axis=1).astype(np.int64)
    return RuleOutput("CW", n, n, n, 0, decision, q_true, p_chosen, k, n, tie)


def sequential_votes(d: RunDraws, n: int, w: float) -> np.ndarray:
    """Public votes (correctness) of SEQ, shape ``(I, n)``, columns in reasoner order.

    Reasoners ``0..n-1`` speak in the order of the ranks of ``seq_key`` among
    them. A speaker votes with the strict leader of the earlier public tally
    when its herding uniform is below ``w``; otherwise it votes privately.
    """
    n = _check_n(d, n)
    if not 0.0 <= w <= 1.0:
        raise ValueError(f"w must be in [0, 1], got {w}")
    I = d.n_items
    rows = np.arange(I)
    order = np.argsort(d.seq_key[:, :n], axis=1, kind="stable")
    votes = np.zeros((I, n), dtype=bool)
    lead = np.zeros(I, dtype=np.int64)  # correct votes minus wrong votes so far
    for t in range(n):
        j = order[:, t]
        private = d.correct[rows, j]
        herd = d.herd_u[rows, j] < w
        vote = np.where(herd & (lead > 0), True, np.where(herd & (lead < 0), False, private))
        votes[rows, j] = vote
        lead += np.where(vote, 1, -1)
    return votes


def sequential(d: RunDraws, n: int, w: float | None = None, tie_rule: str = "coin") -> RuleOutput:
    """SEQ: sequential public voting with herding; budget ``n`` calls."""
    w = d.params.w if w is None else w
    votes = sequential_votes(d, n, w)
    return _vote_share_output("SEQ", n, n, n, n * (n - 1) // 2, votes, d.tie_coin, tie_rule)


def deliberation(d: RunDraws, budget: int, w: float | None = None) -> RuleOutput:
    """DELIB: ``n = budget // 2`` private answers, then one revision round in
    which each reasoner disagreeing with the round-0 majority switches to it
    with probability ``w``. Budget ``2n`` calls; each reasoner reads the other
    ``n - 1`` round-0 answers."""
    if isinstance(budget, bool) or not isinstance(budget, (int, np.integer)) or budget < 2 or budget % 2:
        raise ValueError(f"DELIB budget must be an even int >= 2, got {budget!r}")
    w = d.params.w if w is None else w
    if not 0.0 <= w <= 1.0:
        raise ValueError(f"w must be in [0, 1], got {w}")
    n = _check_n(d, int(budget) // 2)
    r0 = d.correct[:, :n]
    maj0, _ = _majority_from_counts(r0.sum(axis=1), n, d.tie_coin)
    switch = (r0 != maj0[:, None]) & (d.delib_u[:, :n] < w)
    r1 = np.where(switch, maj0[:, None], r0)
    return _vote_share_output("DELIB", int(budget), n, 2 * n, n * (n - 1), r1, d.tie_coin)


def apply_rule(d: RunDraws, rule: str, budget: int, tie_rule: str = "coin") -> RuleOutput:
    """Dispatch by rule id. SINGLE requires ``budget == 1``. ``tie_rule``
    applies to MV and SEQ only (EXP-004); other rules keep the seeded coin."""
    if rule == "SINGLE":
        if budget != 1:
            raise ValueError("SINGLE has budget 1")
        return single(d)
    if rule == "MV":
        return majority(d, budget, tie_rule)
    if rule == "CW":
        return confidence_weighted(d, budget)
    if rule == "SEQ":
        return sequential(d, budget, tie_rule=tie_rule)
    if rule == "DELIB":
        return deliberation(d, budget)
    raise ValueError(f"unknown rule {rule!r}; expected one of {RULES}")

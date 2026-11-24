# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Aggregation rules: hand-computed examples, ties, perfect correlation,
independent errors, budget accounting, differential tests against simple
references, invalid inputs."""

from math import sqrt

import numpy as np
import pytest

from paradox import rules, theory
from paradox.generator import ModelParams, RunDraws, Scenario, generate_run


def hand_draws(correct, conf=None, tie_coin=None, seq_key=None, herd_u=None, delib_u=None, w=0.5):
    c = np.asarray(correct, dtype=bool)
    I, J = c.shape
    full = lambda v, fill: np.asarray(v, float) if v is not None else np.full((I, J), fill)  # noqa: E731
    return RunDraws(
        y=np.ones(I, np.int8), hard=np.zeros(I, bool), p_item=np.full(I, 0.6), leader_correct=c[:, 0].copy(),
        adopt=np.zeros((I, J), bool), correct=c, conf=full(conf, 0.75),
        seq_key=full(seq_key, 0.0) if seq_key is not None else np.tile(np.arange(J, dtype=float), (I, 1)),
        herd_u=full(herd_u, 0.0), delib_u=full(delib_u, 0.0),
        tie_coin=np.asarray(tie_coin if tie_coin is not None else [False] * I, bool), params=ModelParams(lam=0.0, w=w),
    )


# ---- hand-computed examples

def test_majority_hand_example():
    d = hand_draws([[1, 1, 0], [0, 0, 1], [1, 0, 1]])
    out = rules.majority(d, 3)
    assert out.decision_correct.tolist() == [True, False, True]
    assert out.q_true.tolist() == pytest.approx([2 / 3, 1 / 3, 2 / 3])
    assert out.p_chosen.tolist() == pytest.approx([2 / 3, 2 / 3, 2 / 3])


def test_majority_ties_use_the_seeded_coin():
    d = hand_draws([[1, 0, 1, 0], [1, 0, 0, 1], [1, 1, 0, 0]], tie_coin=[True, False, True])
    out = rules.majority(d, 2)
    assert out.tie.tolist() == [True, True, False]
    assert out.decision_correct.tolist() == [True, False, True]
    out4 = rules.majority(d, 4)
    assert out4.tie.all()
    assert out4.decision_correct.tolist() == [True, False, True]


def test_tie_never_correct_without_coin():
    d = hand_draws([[1, 0]] * 4, tie_coin=[False] * 4)
    assert not rules.majority(d, 2).decision_correct.any()


def test_cw_hand_example():
    # weights logit(c): 0.9 -> ln 9, 0.6 -> ln 1.5; one confident correct beats two weak wrong.
    d = hand_draws([[1, 0, 0]], conf=[[0.9, 0.6, 0.6]])
    out = rules.confidence_weighted(d, 3)
    assert out.decision_correct.tolist() == [True]
    assert out.q_true[0] == pytest.approx(np.log(9) / (np.log(9) + 2 * np.log(1.5)))


def test_seq_hand_example_herding():
    # Order 0,1,2,3,4. Votes private 1,1,0,0,0 ; herd_u = 0 so everyone herds when a strict leader exists.
    # t0: no leader -> private 1 ; t1: leader correct -> 1 ; t2..t4 herd -> 1. Final 5/5 correct.
    d = hand_draws([[1, 1, 0, 0, 0]], w=1.0)
    out = rules.sequential(d, 5)
    assert out.votes_correct.tolist() == [5]
    assert out.decision_correct.tolist() == [True]
    # With w = 0 nobody herds: majority of private answers is wrong.
    assert rules.sequential(d, 5, w=0.0).decision_correct.tolist() == [False]


def test_delib_hand_example():
    # Round 0 (n = 3): 1,1,0 -> majority correct; reasoner 2 switches (delib_u 0 < w).
    d = hand_draws([[1, 1, 0]])
    out = rules.deliberation(d, 6)
    assert out.votes_correct.tolist() == [3]
    assert out.calls_per_item == 6 and out.messages_per_item == 6


# ---- perfect correlation and independent errors

@pytest.mark.parametrize("rule", ["MV", "CW", "SEQ"])
@pytest.mark.parametrize("n", [3, 9, 31])
def test_perfect_correlation_aggregation_equals_single(rule, n):
    d = generate_run(Scenario("S4", 0.9, 0.4, 0.3), ModelParams(lam=1.0), 2000, 21)
    base = rules.single(d).decision_correct
    assert np.array_equal(rules.apply_rule(d, rule, n).decision_correct, base)
    assert np.array_equal(rules.deliberation(d, 2 * n).decision_correct, base)


@pytest.mark.parametrize("n,p", [(3, 0.6), (9, 0.55), (31, 0.6), (5, 0.45)])
def test_independent_errors_match_condorcet(n, p):
    N = 100000
    d = generate_run(Scenario("H", p), ModelParams(lam=0.0), N, 31)
    acc = rules.majority(d, n).decision_correct.mean()
    th = theory.condorcet(n, p)
    assert abs(acc - th) < 4 * sqrt(th * (1 - th) / N)


@pytest.mark.parametrize("n,lam", [(3, 0.25), (9, 0.5), (15, 0.75)])
def test_common_shock_matches_theory(n, lam):
    N = 100000
    d = generate_run(Scenario("H", 0.6), ModelParams(lam=lam), N, 32)
    acc = rules.majority(d, n).decision_correct.mean()
    th = theory.common_shock(n, 0.6, lam)
    assert abs(acc - th) < 4 * sqrt(th * (1 - th) / N)


# ---- differential tests against simple references

@pytest.fixture(scope="module")
def draws():
    return generate_run(Scenario("S4", 0.9, 0.4, 0.3), ModelParams(lam=0.25, w=0.5), 3000, 77)


@pytest.mark.parametrize("n", [1, 3, 9, 31])
def test_seq_with_no_herding_equals_mv(draws, n):
    assert np.array_equal(rules.sequential(draws, n, w=0.0).decision_correct, rules.majority(draws, n).decision_correct)


@pytest.mark.parametrize("n", [3, 9, 15])
def test_delib_with_no_switching_equals_mv_of_round0(draws, n):
    assert np.array_equal(rules.deliberation(draws, 2 * n, w=0.0).decision_correct, rules.majority(draws, n).decision_correct)


@pytest.mark.parametrize("n", [3, 9, 31])
def test_cw_with_equal_confidence_equals_mv(n):
    d = generate_run(Scenario("S1", 0.6), ModelParams(lam=0.25, tau=0.0), 3000, 5)
    assert np.allclose(d.conf, 0.75)
    assert np.array_equal(rules.confidence_weighted(d, n).decision_correct, rules.majority(d, n).decision_correct)


def _seq_reference(d, n, w):
    out = []
    for i in range(d.n_items):
        order = sorted(range(n), key=lambda j: (d.seq_key[i, j], j))
        tally = 0
        votes = {}
        for j in order:
            herd = d.herd_u[i, j] < w
            if herd and tally > 0:
                v = True
            elif herd and tally < 0:
                v = False
            else:
                v = bool(d.correct[i, j])
            votes[j] = v
            tally += 1 if v else -1
        k = sum(votes.values())
        out.append(d.tie_coin[i] if 2 * k == n else 2 * k > n)
    return np.array(out)


@pytest.mark.parametrize("n,w", [(3, 0.5), (8, 0.5), (9, 0.9), (31, 0.25)])
def test_seq_vectorised_matches_loop_reference(draws, n, w):
    sub = RunDraws(**{f: (getattr(draws, f)[:400] if f != "params" else draws.params) for f in draws.__dataclass_fields__})
    assert np.array_equal(rules.sequential(sub, n, w=w).decision_correct, _seq_reference(sub, n, w))


def test_seq_order_prefix_consistent(draws):
    # Common random numbers: reasoner 0..n-1 speak in the same relative order for every budget.
    o9 = np.argsort(draws.seq_key[:, :9], axis=1, kind="stable")
    o31 = np.argsort(draws.seq_key[:, :31], axis=1, kind="stable")
    filtered = np.array([[j for j in row if j < 9] for row in o31])
    assert np.array_equal(o9, filtered)


# ---- budget accounting

@pytest.mark.parametrize("n", [1, 2, 3, 9, 31])
def test_budget_accounting(draws, n):
    for rule in ("MV", "CW", "SEQ"):
        out = rules.apply_rule(draws, rule, n)
        assert out.calls_per_item == out.budget == out.n_votes == n
        assert out.votes_correct.min() >= 0 and out.votes_correct.max() <= n
    assert rules.sequential(draws, n).messages_per_item == n * (n - 1) // 2
    s = rules.single(draws)
    assert (s.calls_per_item, s.budget, s.messages_per_item) == (1, 1, 0)


@pytest.mark.parametrize("b", [2, 6, 10, 18, 30, 62])
def test_delib_budget_accounting(draws, b):
    out = rules.deliberation(draws, b)
    assert out.calls_per_item == b == 2 * out.n_reasoners
    assert out.messages_per_item == out.n_reasoners * (out.n_reasoners - 1)


def test_single_is_reasoner_zero(draws):
    assert np.array_equal(rules.single(draws).decision_correct, draws.correct[:, 0])
    assert np.array_equal(rules.majority(draws, 1).decision_correct, draws.correct[:, 0])


# ---- invalid inputs

@pytest.mark.parametrize(
    "call",
    [
        lambda d: rules.majority(d, 0),
        lambda d: rules.majority(d, 32),
        lambda d: rules.majority(d, 2.0),
        lambda d: rules.deliberation(d, 5),
        lambda d: rules.deliberation(d, 64),
        lambda d: rules.sequential(d, 3, w=1.5),
        lambda d: rules.apply_rule(d, "SINGLE", 3),
        lambda d: rules.apply_rule(d, "BOGUS", 3),
    ],
)
def test_invalid_inputs_raise(draws, call):
    with pytest.raises(ValueError):
        call(draws)


@pytest.mark.parametrize("w", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("n", [3, 9, 15])
def test_delib_as_drafted_always_equals_mv_of_round0(draws, n, w):
    # Characterisation of the draft DELIB rule (protocol section 2.5): only minority members
    # switch, and only towards the round-0 majority, so the round-1 majority can never differ
    # from the round-0 majority. DELIB at budget 2n is therefore MV at n with twice the cost.
    # Recorded as proposed amendment A-2 for the owner; this test pins the behaviour.
    assert np.array_equal(rules.deliberation(draws, 2 * n, w=w).decision_correct, rules.majority(draws, n).decision_correct)

# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Generator: seeded sampling, marginals, correlation structure, invalid inputs."""

from math import sqrt

import numpy as np
import pytest

from paradox.generator import ModelParams, Scenario, derive_seeds, generate_run

FIELDS = ("y", "hard", "p_item", "leader_correct", "adopt", "correct", "conf", "seq_key", "herd_u", "delib_u", "tie_coin")


def test_same_seed_is_bit_identical():
    sc, prm = Scenario("S4", 0.9, 0.4, 0.3), ModelParams(lam=0.5)
    a, b = generate_run(sc, prm, 500, 123), generate_run(sc, prm, 500, 123)
    for f in FIELDS:
        assert np.array_equal(getattr(a, f), getattr(b, f)), f


def test_different_seeds_give_different_pools():
    sc, prm = Scenario("S1", 0.6), ModelParams(lam=0.0)
    a, b = generate_run(sc, prm, 500, 1), generate_run(sc, prm, 500, 2)
    assert not np.array_equal(a.y, b.y)
    assert not np.array_equal(a.correct, b.correct)


def test_streams_are_separated():
    # Changing w (used only by SEQ and DELIB) must not change any draw.
    sc = Scenario("S1", 0.6)
    a = generate_run(sc, ModelParams(lam=0.25, w=0.1), 300, 7)
    b = generate_run(sc, ModelParams(lam=0.25, w=0.9), 300, 7)
    for f in FIELDS:
        assert np.array_equal(getattr(a, f), getattr(b, f)), f


def test_derive_seeds_deterministic_and_distinct():
    s = derive_seeds(0, 10)
    assert s == derive_seeds(0, 10)
    assert len(set(s)) == 10
    assert derive_seeds(20261124, 10) != s
    assert derive_seeds(0, 3) == s[:3]


@pytest.mark.parametrize("lam", [0.0, 0.5, 1.0])
def test_marginal_competence_is_mu(lam):
    sc = Scenario("S4", 0.9, 0.4, 0.3)
    d = generate_run(sc, ModelParams(lam=lam), 40000, 11)
    se = sqrt(sc.mu * (1 - sc.mu) / 40000)
    for j in (0, 7, 30):
        assert abs(d.correct[:, j].mean() - sc.mu) < 4 * se


def test_conditional_pairwise_correlation_is_lambda_squared():
    p, lam, n_items = 0.6, 0.5, 200000
    d = generate_run(Scenario("H", p), ModelParams(lam=lam), n_items, 5)
    x, y = d.correct[:, 0].astype(float), d.correct[:, 1].astype(float)
    r = np.corrcoef(x, y)[0, 1]
    assert r == pytest.approx(lam**2, abs=0.01)


def test_perfect_correlation_all_reasoners_agree():
    d = generate_run(Scenario("S1", 0.6), ModelParams(lam=1.0), 1000, 3)
    assert np.all(d.correct == d.correct[:, :1])
    assert np.all(d.conf == d.conf[:, :1])


def test_independent_errors_have_no_correlation():
    d = generate_run(Scenario("S1", 0.6), ModelParams(lam=0.0), 200000, 4)
    r = np.corrcoef(d.correct[:, 0], d.correct[:, 5])[0, 1]
    assert abs(r) < 0.01


def test_confidence_range_and_informativeness():
    d = generate_run(Scenario("S1", 0.6), ModelParams(lam=0.0), 20000, 9)
    assert np.all((d.conf > 0.5) & (d.conf <= 0.999))
    assert d.conf[d.correct].mean() > d.conf[~d.correct].mean()


def test_answers_match_correctness():
    d = generate_run(Scenario("S1", 0.6), ModelParams(lam=0.3), 100, 2)
    ans = d.answers()
    assert np.array_equal(ans == d.y[:, None], d.correct)


@pytest.mark.parametrize(
    "make",
    [
        lambda: Scenario("", 0.6),
        lambda: Scenario("X", 1.5),
        lambda: Scenario("X", 0.6, 0.3, None),
        lambda: Scenario("X", 0.6, -0.1, 0.3),
        lambda: ModelParams(lam=1.1),
        lambda: ModelParams(lam=0.5, w=2.0),
        lambda: ModelParams(lam=0.5, tau=-1.0),
        lambda: ModelParams(lam=0.5, max_reasoners=0),
        lambda: generate_run(Scenario("X", 0.6), ModelParams(lam=0.0), 0, 1),
        lambda: generate_run(Scenario("X", 0.6), ModelParams(lam=0.0), 10, -1),
        lambda: generate_run(Scenario("X", 0.6), ModelParams(lam=0.0), 10, 1.5),
        lambda: derive_seeds(-1, 3),
        lambda: derive_seeds(0, 0),
    ],
)
def test_invalid_inputs_raise(make):
    with pytest.raises(ValueError):
        make()

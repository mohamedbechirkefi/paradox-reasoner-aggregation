# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Metrics and seed-level statistics: hand-computed values, invariants, invalid inputs."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from paradox import metrics, stats


def test_accuracy_and_brier_hand():
    assert metrics.accuracy(np.array([True, False, True, True])) == 0.75
    # (1-0.8)^2 + (1-0.3)^2 = 0.04 + 0.49 -> mean 0.265
    assert metrics.brier(np.array([0.8, 0.3])) == pytest.approx(0.265)


def test_ece_hand():
    # bin [0.6,0.7): conf 0.6, acc 1 -> |1-0.6|=0.4, weight 1/2 ; bin [0.9,1]: conf 1.0 acc 0 -> 1.0, weight 1/2
    assert metrics.ece(np.array([0.6, 1.0]), np.array([True, False])) == pytest.approx(0.7)


def test_ece_zero_when_calibrated():
    p = np.array([0.75] * 4)
    c = np.array([True, True, True, False])
    assert metrics.ece(p, c) == pytest.approx(0.0)


def test_disagreement_hand():
    share, pair = metrics.disagreement(np.array([3, 2, 0]), 3)
    assert share == pytest.approx(1 / 3)
    # k=2 of 3: 2*2*1/(3*2) = 2/3 ; others 0
    assert pair == pytest.approx((2 / 3) / 3)
    assert metrics.disagreement(np.array([1, 0]), 1) == (0.0, 0.0)


def test_paired_delta():
    assert metrics.paired_delta(np.array([True, True, False]), np.array([False, True, True])) == pytest.approx(0.0)
    assert metrics.paired_delta(np.array([True, True]), np.array([False, True])) == pytest.approx(0.5)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.floats(0, 1), min_size=1, max_size=50), st.data())
def test_metric_bounds(ps, data):
    p = np.array(ps)
    c = np.array(data.draw(st.lists(st.booleans(), min_size=len(ps), max_size=len(ps))))
    assert 0 <= metrics.brier(p) <= 1
    assert 0 <= metrics.ece(p, c) <= 1


@pytest.mark.parametrize(
    "call",
    [
        lambda: metrics.accuracy(np.array([])),
        lambda: metrics.accuracy(np.array([1, 0])),
        lambda: metrics.brier(np.array([1.2])),
        lambda: metrics.ece(np.array([0.5]), np.array([True, False])),
        lambda: metrics.ece(np.array([0.5]), np.array([True]), n_bins=0),
        lambda: metrics.disagreement(np.array([4]), 3),
        lambda: metrics.paired_delta(np.array([True]), np.array([True, False])),
    ],
)
def test_metric_invalid_inputs(call):
    with pytest.raises(ValueError):
        call()


# ---- statistics

@pytest.mark.parametrize(
    "prob,df,expected",
    [(0.975, 9, 2.262157163), (0.95, 9, 1.833112933), (0.975, 1, 12.70620474), (0.975, 29, 2.045229642), (0.5, 4, 0.0)],
)
def test_t_quantiles_against_tables(prob, df, expected):
    assert stats.t_quantile(prob, df) == pytest.approx(expected, abs=1e-6)


def test_t_cdf_symmetry():
    for t in (-3.0, -0.5, 0.7, 2.0):
        assert stats.t_cdf(t, 7) + stats.t_cdf(-t, 7) == pytest.approx(1.0, abs=1e-12)


def test_t_interval_hand():
    x = [1.0, 2.0, 3.0]
    lo, hi = stats.t_interval(x)
    half = 4.302652730 * 1.0 / np.sqrt(3)
    assert (lo, hi) == pytest.approx((2 - half, 2 + half), abs=1e-6)


def test_holm_known_example():
    assert stats.holm([0.01, 0.04, 0.03, 0.005]) == pytest.approx([0.03, 0.06, 0.06, 0.02])


def test_one_sided_p():
    assert stats.one_sided_p_negative([-0.1, -0.1, -0.1]) == 0.0
    assert stats.one_sided_p_negative([0.0, 0.0]) == 1.0
    assert stats.one_sided_p_negative([-1.0, 1.0]) == pytest.approx(0.5)


def test_bootstrap_deterministic_and_bounded():
    x = [0.01, -0.02, 0.03, 0.0, 0.015]
    a = stats.bootstrap_interval(x, seed=3, n_resamples=2000)
    assert a == stats.bootstrap_interval(x, seed=3, n_resamples=2000)
    assert min(x) <= a[0] <= a[1] <= max(x)


@pytest.mark.parametrize("call", [lambda: stats.t_interval([1.0]), lambda: stats.holm([1.5]), lambda: stats.t_quantile(1.0, 3),
                                  lambda: stats.t_interval([1.0, float("nan")])])
def test_stats_invalid_inputs(call):
    with pytest.raises(ValueError):
        call()

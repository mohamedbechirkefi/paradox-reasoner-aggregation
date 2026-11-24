# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Closed-form theory: golden fixtures, identities, differential checks, invalid inputs."""

from math import comb

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from paradox import theory

ODD = [1, 3, 5, 9, 15, 31]


# Golden fixtures (hand-computed; Kaniovski 2008 Theorem 1, journal J-0002).
def test_golden_condorcet_hand_computed():
    # n = 3: p^3 + 3 p^2 q = 0.166375 + 0.408375
    assert theory.condorcet(3, 0.55) == pytest.approx(0.57475, abs=1e-12)
    assert theory.condorcet(5, 0.55) == pytest.approx(0.5931269, abs=5e-8)


def test_golden_bahadur_kaniovski():
    # n = 3: 0.57475 + 0.4 * 6 * (-0.05) * 1 * 0.2475 = 0.54505
    assert theory.bahadur_mv(3, 0.55, 0.4) == pytest.approx(0.54505, abs=1e-12)
    assert theory.bahadur_mv(5, 0.55, 0.4) == pytest.approx(0.5196194, abs=5e-8)


def test_golden_common_shock_n3_hand_computed():
    # n=3, p=0.6, lambda=0.5, enumerated by hand over k adopters:
    # k=0 (1/8): M_3(0.6)=0.648; k=1 (3/8): 0.6*P(Bin(2,.6)>=1)+0.4*P(Bin(2,.6)>=2)=0.6*0.84+0.4*0.36=0.648
    # k=2 (3/8): 0.6*1 + 0.4*0 = 0.6 ; k=3 (1/8): 0.6
    expected = (0.648 + 3 * 0.648 + 3 * 0.6 + 0.6) / 8
    assert theory.common_shock(3, 0.6, 0.5) == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize("p", [0.0, 0.3, 0.55, 1.0])
def test_single_reasoner_is_p(p):
    assert theory.condorcet(1, p) == pytest.approx(p)
    assert theory.common_shock(1, p, 0.7) == pytest.approx(p)


@pytest.mark.parametrize("n", ODD)
def test_coin_flip_competence_gives_half(n):
    assert theory.condorcet(n, 0.5) == pytest.approx(0.5, abs=1e-12)


@pytest.mark.parametrize("n", ODD)
@pytest.mark.parametrize("p", [0.1, 0.45, 0.6, 0.8])
def test_perfect_and_zero_correlation(n, p):
    # Perfect correlation: every reasoner adopts the leader; MV equals one reasoner.
    assert theory.common_shock(n, p, 1.0) == pytest.approx(p, abs=1e-12)
    # Independent errors: common-shock reduces to Condorcet.
    assert theory.common_shock(n, p, 0.0) == pytest.approx(theory.condorcet(n, p), abs=1e-12)


@settings(max_examples=200, deadline=None)
@given(n=st.sampled_from(ODD), p=st.floats(0, 1), lam=st.floats(0, 1))
def test_common_shock_symmetry_and_bounds(n, p, lam):
    g = theory.common_shock(n, p, lam)
    assert -1e-12 <= g <= 1 + 1e-12
    assert theory.common_shock(n, 1 - p, lam) == pytest.approx(1 - g, abs=1e-9)


@settings(max_examples=200, deadline=None)
@given(n=st.sampled_from(ODD), p=st.floats(0.5, 1))
def test_condorcet_monotone_in_competence_above_half(n, p):
    assert theory.condorcet(n, p) >= p - 1e-12


@pytest.mark.parametrize("n", [3, 5, 9, 15, 31])
@pytest.mark.parametrize("p", [0.45, 0.5, 0.55, 0.6, 0.8])
@pytest.mark.parametrize("c", [0.0, 0.05, 0.1, 0.4])
def test_bahadur_theorem_matches_enumeration(n, p, c):
    # Differential test: closed form (Theorem 1) against direct summation of P(K = k).
    if not theory.bahadur_admissible(n, p, c):
        with pytest.raises(ValueError):
            theory.bahadur_mv(n, p, c)
        return
    assert sum(theory.bahadur_k_distribution(n, p, c)) == pytest.approx(1.0, abs=1e-10)
    assert theory.bahadur_mv(n, p, c) == pytest.approx(theory.bahadur_mv_enumerated(n, p, c), abs=1e-10)


def test_bahadur_c0_is_condorcet():
    for n in ODD:
        assert theory.bahadur_mv(n, 0.6, 0.0) == pytest.approx(theory.condorcet(n, 0.6), abs=1e-12)


def test_bahadur_inadmissible_example():
    # Large n with strong correlation: the n = 31 profile probabilities go negative.
    assert not theory.bahadur_admissible(31, 0.55, 0.4)


def test_beta_binomial_differential_against_quadrature():
    a, b, n = 3.0, 2.0, 5
    x = np.linspace(0, 1, 200001)
    from math import lgamma

    dens = np.exp((a - 1) * np.log(np.clip(x, 1e-300, 1)) + (b - 1) * np.log(np.clip(1 - x, 1e-300, 1)) - (lgamma(a) + lgamma(b) - lgamma(a + b)))
    mn = sum(comb(n, t) * x**t * (1 - x) ** (n - t) for t in range(3, 6))
    quad = np.trapezoid(dens * mn, x)
    assert theory.beta_binomial_mv(n, a, b) == pytest.approx(quad, abs=1e-6)


def test_beta_binomial_concentrated_tends_to_condorcet():
    assert theory.beta_binomial_mv(9, 0.6e6, 0.4e6) == pytest.approx(theory.condorcet(9, 0.6), abs=1e-4)


@pytest.mark.parametrize("p,r", [(0.55, 0.05), (0.6, 0.2), (0.7, 0.4)])
def test_matched_correlation_maps(p, r):
    pe, h, ph = theory.mixture_params_for_correlation(p, r)
    mean = (1 - h) * pe + h * ph
    var = (1 - h) * (pe - mean) ** 2 + h * (ph - mean) ** 2
    assert mean == pytest.approx(p)
    assert var / (p * (1 - p)) == pytest.approx(r)
    a, b = theory.beta_params_for_correlation(p, r)
    assert a / (a + b) == pytest.approx(p)
    assert 1 / (a + b + 1) == pytest.approx(r)
    assert theory.common_shock_lambda_for_correlation(r) ** 2 == pytest.approx(r)


def test_protocol_p1_predictions_match_table():
    # research/protocol.md section 6.2, last column.
    table = {"S1": (0.6, 0, None, False), "S2": (0.55, 0, None, False), "S3": (0.8, 0, None, False),
             "S4": (0.9, 0.4, 0.3, True), "S5": (0.7, 0.2, 0.45, False), "S6": (0.95, 0.5, 0.35, True)}
    for sid, (pe, h, ph, degrade) in table.items():
        assert theory.predicted_mv_degrades(pe, h, ph) is degrade, sid


def test_mixture_reduces_to_common_shock_when_homogeneous():
    assert theory.mixture(9, 0.6, 0.0, None, 0.3) == theory.common_shock(9, 0.6, 0.3)
    assert theory.mixture(9, 0.6, 0.4, 0.6, 0.3) == pytest.approx(theory.common_shock(9, 0.6, 0.3))


@pytest.mark.parametrize(
    "call",
    [
        lambda: theory.condorcet(4, 0.6),  # even n
        lambda: theory.condorcet(0, 0.6),
        lambda: theory.condorcet(3, 1.2),
        lambda: theory.condorcet(3, float("nan")),
        lambda: theory.condorcet(3.0, 0.6),
        lambda: theory.common_shock(3, 0.6, -0.1),
        lambda: theory.mixture(3, 0.6, 0.3, None, 0.0),
        lambda: theory.bahadur_mv(3, 0.0, 0.1),
        lambda: theory.bahadur_k_distribution(3, 0.5, float("inf")),
        lambda: theory.beta_binomial_mv(3, 0.0, 1.0),
        lambda: theory.mixture_params_for_correlation(0.95, 0.9),
        lambda: theory.beta_params_for_correlation(0.6, 0.0),
        lambda: theory.binom_tail(-1, 0.5, 1),
    ],
)
def test_invalid_inputs_raise(call):
    with pytest.raises(ValueError):
        call()

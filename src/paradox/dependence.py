# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Alternative dependence models (EXP-001 Bahadur cells, EXP-003).

Each sampler returns the number of correct votes ``K`` among ``n`` reasoners
per item, which is all majority voting needs. Matched-correlation maps live in
:mod:`paradox.theory`.
"""

from __future__ import annotations

import numpy as np

from . import theory
from .generator import ModelParams, Scenario, generate_run

__all__ = ["DEPENDENCE_MODELS", "sample_k", "analytic_mv", "model_parameters"]

DEPENDENCE_MODELS = ("common_shock", "bahadur", "mixture", "beta")


def model_parameters(model: str, p: float, r: float) -> dict:
    """Parameters of ``model`` at marginal competence ``p`` and pairwise
    correctness correlation ``r``. Raises ``ValueError`` if inadmissible."""
    if model == "common_shock":
        return {"lambda": theory.common_shock_lambda_for_correlation(r)}
    if model == "bahadur":
        return {"c": float(r)}
    if model == "mixture":
        pe, h, ph = theory.mixture_params_for_correlation(p, r)
        return {"p_easy": pe, "h": h, "p_hard": ph}
    if model == "beta":
        a, b = theory.beta_params_for_correlation(p, r)
        return {"a": a, "b": b}
    raise ValueError(f"unknown dependence model {model!r}")


def analytic_mv(model: str, n: int, p: float, r: float) -> float:
    """Exact MV accuracy of ``model`` at ``(n, p, r)``; ``ValueError`` if inadmissible."""
    prm = model_parameters(model, p, r)
    if model == "common_shock":
        return theory.common_shock(n, p, prm["lambda"])
    if model == "bahadur":
        return theory.bahadur_mv(n, p, prm["c"])
    if model == "mixture":
        return theory.mixture(n, prm["p_easy"], prm["h"], prm["p_hard"], 0.0)
    return theory.beta_binomial_mv(n, prm["a"], prm["b"])


def sample_k(model: str, n: int, p: float, r: float, n_items: int, seed: int) -> np.ndarray:
    """Sample ``K`` (correct votes among ``n``) for ``n_items`` items."""
    if isinstance(n_items, bool) or not isinstance(n_items, int) or n_items < 1:
        raise ValueError("n_items must be a positive int")
    prm = model_parameters(model, p, r)
    if model in ("common_shock", "mixture"):
        if model == "common_shock":
            sc, lam = Scenario("dep", p_easy=p), prm["lambda"]
        else:
            sc, lam = Scenario("dep", p_easy=prm["p_easy"], h=prm["h"], p_hard=prm["p_hard"]), 0.0
        d = generate_run(sc, ModelParams(lam=lam, max_reasoners=n), n_items, seed)
        return d.correct.sum(axis=1).astype(np.int64)
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    if model == "bahadur":
        if not theory.bahadur_admissible(n, p, prm["c"]):
            raise ValueError(f"Bahadur model inadmissible at n={n}, p={p}, c={prm['c']}")
        probs = np.clip(np.array(theory.bahadur_k_distribution(n, p, prm["c"])), 0.0, None)
        probs = probs / probs.sum()
        return rng.choice(n + 1, size=n_items, p=probs).astype(np.int64)
    p_i = rng.beta(prm["a"], prm["b"], size=n_items)
    return rng.binomial(n, p_i).astype(np.int64)

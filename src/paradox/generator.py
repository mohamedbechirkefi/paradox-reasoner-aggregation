# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Synthetic item pools and reasoner draws (protocol sections 2.1 to 2.3, 2.6).

One call to :func:`generate_run` produces every random quantity a run needs,
for up to ``max_reasoners`` reasoners. Aggregation rules use prefixes of this
table, so every rule and every budget in a run shares common random numbers.
Each component has its own child RNG stream, spawned from the run seed, so a
change to one component's draws never shifts another's.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np

__all__ = ["Scenario", "ModelParams", "RunDraws", "generate_run", "derive_seeds", "MAX_REASONERS"]

MAX_REASONERS = 31

# Child stream indices; fixed so that streams are stable across code versions.
_STREAMS = ("labels", "difficulty", "leader", "adopt", "private", "signal", "seq_order", "herd", "delib", "tie")


def _real(name: str, x: object) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(float(x)):
        raise ValueError(f"{name} must be a finite real number, got {x!r}")
    return float(x)


def _prob(name: str, x: object) -> float:
    v = _real(name, x)
    if not 0.0 <= v <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {v}")
    return v


@dataclass(frozen=True)
class Scenario:
    """Two-class difficulty scenario: with probability ``h`` an item is hard
    (competence ``p_hard``), otherwise easy (competence ``p_easy``)."""

    id: str
    p_easy: float
    h: float = 0.0
    p_hard: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("scenario id must be a non-empty string")
        _prob("p_easy", self.p_easy)
        _prob("h", self.h)
        if self.h > 0.0:
            if self.p_hard is None:
                raise ValueError("p_hard is required when h > 0")
            _prob("p_hard", self.p_hard)
        elif self.p_hard is not None:
            _prob("p_hard", self.p_hard)

    @property
    def mu(self) -> float:
        """Mean competence, i.e. expected single-reasoner accuracy."""
        hard = self.p_hard if self.p_hard is not None else 0.0
        return (1.0 - self.h) * self.p_easy + self.h * hard


@dataclass(frozen=True)
class ModelParams:
    """Model parameters. ``lam``: common-shock adoption probability; ``w``:
    herding or switching probability (SEQ, DELIB); ``delta``: confidence signal
    separation; ``tau``: confidence scale."""

    lam: float
    w: float = 0.5
    delta: float = 1.0
    tau: float = 1.0
    max_reasoners: int = MAX_REASONERS

    def __post_init__(self) -> None:
        _prob("lambda", self.lam)
        _prob("w", self.w)
        _real("delta", self.delta)
        if _real("tau", self.tau) < 0:
            raise ValueError("tau must be >= 0")
        if isinstance(self.max_reasoners, bool) or not isinstance(self.max_reasoners, int) or self.max_reasoners < 1:
            raise ValueError("max_reasoners must be a positive int")


@dataclass(frozen=True)
class RunDraws:
    """All random quantities of one run. Shapes: ``(I,)`` or ``(I, J)``.

    ``correct[i, j]``: reasoner ``j``'s private-stage answer is correct.
    ``answer = y`` if correct else ``1 - y``. ``conf`` in (0.5, 1): confidence
    in the reasoner's own answer. ``seq_key``: uniforms whose ranks give the
    SEQ speaking order. ``herd_u``, ``delib_u``: uniforms for herding and
    switching decisions. ``tie_coin``: True means a tie resolves to the correct
    answer.
    """

    y: np.ndarray
    hard: np.ndarray
    p_item: np.ndarray
    leader_correct: np.ndarray
    adopt: np.ndarray
    correct: np.ndarray
    conf: np.ndarray
    seq_key: np.ndarray
    herd_u: np.ndarray
    delib_u: np.ndarray
    tie_coin: np.ndarray
    params: ModelParams

    @property
    def n_items(self) -> int:
        return int(self.y.shape[0])

    @property
    def n_reasoners(self) -> int:
        return int(self.correct.shape[1])

    def answers(self) -> np.ndarray:
        """Binary answers of every reasoner, shape ``(I, J)``."""
        return np.where(self.correct, self.y[:, None], 1 - self.y[:, None]).astype(np.int8)


def derive_seeds(entropy: int, n: int) -> list[int]:
    """Fixed integer run seeds from ``SeedSequence(entropy).spawn(n)``."""
    if isinstance(entropy, bool) or not isinstance(entropy, int) or entropy < 0:
        raise ValueError("entropy must be a non-negative int")
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive int")
    return [int(child.generate_state(1, dtype=np.uint32)[0]) for child in np.random.SeedSequence(entropy).spawn(n)]


def _confidence(signal: np.ndarray, tau: float) -> np.ndarray:
    sig = 1.0 / (1.0 + np.exp(-tau * signal))
    return np.minimum(0.999, 0.5 + 0.5 * sig)


def generate_run(scenario: Scenario, params: ModelParams, n_items: int, seed: int) -> RunDraws:
    """Generate one run's item pool and reasoner-draw table."""
    if not isinstance(scenario, Scenario) or not isinstance(params, ModelParams):
        raise ValueError("scenario and params must be Scenario and ModelParams instances")
    if isinstance(n_items, bool) or not isinstance(n_items, int) or n_items < 1:
        raise ValueError(f"n_items must be a positive int, got {n_items!r}")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError(f"seed must be a non-negative int, got {seed!r}")
    I, J = n_items, params.max_reasoners
    rngs = dict(zip(_STREAMS, (np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(len(_STREAMS)))))

    y = (rngs["labels"].random(I) < 0.5).astype(np.int8)
    hard = rngs["difficulty"].random(I) < scenario.h
    p_hard = scenario.p_hard if scenario.p_hard is not None else scenario.p_easy
    p_item = np.where(hard, p_hard, scenario.p_easy)

    leader_correct = rngs["leader"].random(I) < p_item
    adopt = rngs["adopt"].random((I, J)) < params.lam
    private_correct = rngs["private"].random((I, J)) < p_item[:, None]
    correct = np.where(adopt, leader_correct[:, None], private_correct)

    sig_rng = rngs["signal"]
    leader_noise = sig_rng.standard_normal(I)
    private_noise = sig_rng.standard_normal((I, J))
    leader_s = np.where(leader_correct, params.delta, -params.delta) + leader_noise
    private_s = np.where(private_correct, params.delta, -params.delta) + private_noise
    signal = np.where(adopt, leader_s[:, None], private_s)
    conf = _confidence(signal, params.tau)

    return RunDraws(
        y=y,
        hard=hard,
        p_item=p_item,
        leader_correct=leader_correct,
        adopt=adopt,
        correct=correct,
        conf=conf,
        seq_key=rngs["seq_order"].random((I, J)),
        herd_u=rngs["herd"].random((I, J)),
        delib_u=rngs["delib"].random((I, J)),
        tie_coin=rngs["tie"].random(I) < 0.5,
        params=params,
    )

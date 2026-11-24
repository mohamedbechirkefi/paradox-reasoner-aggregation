<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-001 protocol: engine and theoretical-baseline validation

**Status: DRAFT v0.1, 2026-11-24, awaiting owner freeze (G-FREEZE). Protocol hash: not yet computed (computed at freeze).**

Project-level definitions (model, rules, metrics) are in [`research/protocol.md`](../../protocol.md); this file states only what is specific to EXP-001.

## 1. Question

Does the simulation engine reproduce the exact accuracy of majority voting predicted by closed-form theory, within Monte Carlo tolerance, for independent, common-shock correlated, two-class heterogeneous and Bahadur second-order models?

## 2. Mechanism and rationale

The master prompt requires validating the independent-vote theoretical baseline. Every later conclusion depends on the engine being correct; a stop rule forbids EXP-002 to EXP-004 until EXP-001 passes. Theory: Condorcet binomial; common-shock formula `G(n,p,lambda)` (derived in `protocol.md` section 2.7 from the opinion-leader structure); Kaniovski (2008) Theorem 1 for the Bahadur model.

## 3. Competing explanations for a mismatch

Engine defect (sampling, aggregation, tie handling); formula derivation error; RNG misuse (shared streams, seed reuse); insufficient Monte Carlo sample.

## 4. Hypotheses

This is a verification experiment, not a test of a scientific hypothesis.

- **H0 (engine correct):** for every validation cell, `|A_sim - A_theory| <= 4 SE_MC`, where `SE_MC = sqrt(A_theory (1 - A_theory) / N)`.
- **Contradiction:** any cell with `|A_sim - A_theory| > 4 SE_MC`, or any deterministic golden fixture not reproduced to 1e-9.

## 5. Estimand, unit, variables

- Estimand: `A_sim - A_theory` per cell.
- Unit: one validation cell `(model, p, lambda or c, n)`, `N = 200,000` simulated items pooled over 10 seeds of 20,000.
- Independent variables: model in {independent, common-shock, two-class mixture, Bahadur}; `p` in {0.45, 0.5, 0.55, 0.6, 0.8}; `lambda` in {0, 0.25, 0.5, 0.75, 1}; Bahadur `c` in {0, 0.1, 0.4} where admissible; `n` in {1, 3, 5, 9, 15, 31}.
- Dependent variable: MV accuracy.

## 6. Deterministic checks (golden fixtures and invariants)

- Bahadur `p = 0.55, c = 0.4`: `n = 3` gives 0.54505; `n = 5` gives 0.5196194.
- `M_1(p) = p`; `M_n(0.5) = 0.5` for odd `n`; `M_n(1 - p) = 1 - M_n(p)`.
- `lambda = 1`: `G(n, p, 1) = p` for all `n` (perfect correlation).
- `lambda = 0`: `G(n, p, 0) = M_n(p)` (independent errors).
- Majority ties at even `n`: tie handling follows the declared rule (seeded coin flip), and a tie never counts as correct without the coin.
- Budget accounting: recorded calls per item equal `n` for MV, CW and SEQ and `2n` for DELIB.
- Seeded sampling: same seed gives bit-identical outputs; different seeds give different item pools.

## 7. Sample size

`N = 200,000` gives `SE_MC <= 0.0011`; the 4 SE tolerance is then at most 0.0045. With about 300 cells, a 4 SE threshold keeps the expected number of false alarms from a correct engine near 0.02 (planning estimate under a normal approximation).

## 8. Budget, uncertainty, exclusion, stopping

- Compute: under one minute expected (estimate).
- Uncertainty: Monte Carlo SE from theory, as above; per-seed values retained.
- Exclusion: inadmissible Bahadur cells (any negative profile probability) are reported and skipped.
- Stopping: a failed cell triggers diagnosis; the experiment is rerun in full after a fix, and both the failed and the passing reports are kept.

## 9. Failure modes and sensitivity

Floating-point accumulation in large binomial sums (use exact `math.comb` and log-space where needed); RNG stream reuse across rules; off-by-one in `m = (n+1)/2`.

## 10. Reproduction (planned commands, not yet implemented)

```
uv run paradox validate --config research/experiments/EXP-001/config.json --out results/EXP-001/
uv run paradox report EXP-001
```

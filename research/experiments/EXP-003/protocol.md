<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-003 protocol: dependence-structure sensitivity

**Status: DRAFT v0.1, 2026-11-24, awaiting owner freeze (G-FREEZE). Protocol hash: not yet computed. Depends on EXP-001 passing; interpreted together with EXP-002.**

## 1. Question

At matched marginal competence `p` and matched pairwise correlation of correctness `r`, does the sign of `Delta_MV = A_MV(n) - p` depend on the dependence model?

## 2. Why this can invalidate the main interpretation

A natural reading of EXP-002 is "aggregation degrades when there is enough below-chance item mass; correlation alone only shrinks the gain". That reading is invalidated if a model with no below-chance items, at the same `p` and `r`, also produces `Delta_MV < 0`. Kaniovski (2008, Theorem 1, verified) implies exactly this for the Bahadur second-order model at `p = 0.55, c = 0.4, n = 3` (0.54505 < 0.55). If degradation appears broadly under the Bahadur model, then pairwise correlation is not a sufficient summary and the main claim must be restricted to the common-shock and mixture families.

## 3. Models (all with marginal `p`, pairwise correlation `r`)

1. Common-shock: `lambda = sqrt(r)` with homogeneous `p_i = p` (conditional correlation `r`).
2. Bahadur second-order homogeneous, correlation `c = r` (admissible cells only).
3. Two-class mixture: `p_easy`, `p_hard` chosen symmetric around `p` so that the induced correlation equals `r` (solved numerically; the solution is recorded).
4. Continuous Beta difficulty: `p_i ~ Beta(a, b)` with mean `p` and intra-class correlation `1/(a + b + 1) = r`.

## 4. Hypotheses

- **H0:** the sign of `Delta_MV` at matched `(p, r, n)` is the same across the four models in every admissible cell.
- **H1:** the sign differs between at least two models in at least one admissible cell.
- Contradiction of H1: all models agree in sign in every admissible cell (intervals excluding 0).

## 5. Design

- `p` in {0.55, 0.6, 0.7}; `r` in {0.05, 0.1, 0.2, 0.4}; `n` in {3, 5, 9, 15}.
- Analytic values computed where closed forms exist (models 1 to 3); Monte Carlo for model 4 and as a check on all models: 10 seeds x 20,000 items per cell.
- Unit: one `(model, p, r, seed)` run.
- Uncertainty: seed-level t intervals; analytic values reported exactly.
- Exclusion: inadmissible Bahadur cells, reported.

## 6. Reproduction (planned)

```
uv run paradox run --config research/experiments/EXP-003/config.json --out results/EXP-003/
uv run paradox report EXP-003
```

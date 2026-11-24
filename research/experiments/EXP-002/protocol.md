<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-002 protocol: equal-budget aggregation map (primary)

**Status: FROZEN v1.0 (owner-approved 2026-11-24). Drafted as v0.1 on 2026-11-24. The SHA-256 of this file and of `config.json` is recorded in `research/freeze.json` and in the registry. Depends on EXP-001 passing.**

Project-level definitions are in [`research/protocol.md`](../../protocol.md).

## 1. Question

At an equal budget of `B` reasoner calls per item, in which regions of competence, difficulty heterogeneity and error correlation does each aggregation rule (MV, CW, SEQ) improve or degrade accuracy relative to a single reasoner making one call?

## 2. Mechanism and rationale

- Condorcet-type amplification: with independent votes and competence above 0.5, majority accuracy rises with group size; below 0.5 it falls.
- Difficulty heterogeneity: Chen et al. (2024, arXiv:2403.02419, abstract verified) report that majority-vote performance of LLM systems can first rise and then fall with the number of calls, and attribute it to query difficulty diversity (more calls help easy queries and hurt hard ones).
- Correlation: Kaniovski (2008, verified) shows that, under the Bahadur solution, positive correlation lowers jury competence and enlarging a positively correlated jury can be detrimental up to a certain size. Kim et al. (2025, arXiv:2506.07962, abstract verified) report substantial error correlation across LLMs.
- Information sharing: Golub and Jackson (2010, verified abstract) show naive averaging reaches the truth only if the most influential agent's influence vanishes; Mavrodiev, Tessone and Schweitzer (2012, verified abstract) conclude the effect of social influence depends on initial diversity and accuracy. Lorenz et al. (2011) is relevant but unverified in this session.

## 3. Competing explanations

Below-chance item mass (difficulty) versus correlation versus herding; finite-budget effects (convergence not reached at `B = 31`); the confidence model driving CW results.

## 4. Hypotheses, estimand, disconfirmation

As in `research/protocol.md` section 3: primary estimand `Delta_r(cell) = A_r(B) - A_SINGLE` for `r` in {MV, SEQ}; H0 no cell degrades; H1 some cell degrades; Holm-adjusted one-sided 95% bounds. Directional predictions P1 to P3 and their disconfirmation criteria are stated there and are part of this protocol.

## 5. Design

- Unit: one run `(scenario, lambda, seed)`, 2000 items, common random numbers across rules and budgets.
- Independent variables: scenario S1 to S6; `lambda` in {0, 0.25, 0.5, 0.75}; `B` in {1, 3, 5, 9, 15, 31}; rule in {SINGLE, MV, CW, SEQ}. DELIB is dropped (amendment 2): as specified it equals MV at half its calls on every item, so it cannot answer its question; this is reported as a limitation.
- Dependent variables: accuracy (primary); Brier, ECE, disagreement, cost proxy, accuracy per call (secondary).
- Treatment: aggregation rules. Control and baseline: SINGLE (reasoner 1 of the same run, one call).
- Fixed parameters: `w = 0.5`, `delta = 1`, `tau = 1`.
- Seeds: 30 per run cell, from `SeedSequence(20261124)`, the same list in every cell (shared seeds, D-008); 720 runs (amendment 1; v0.1 had 10 seeds, 240 runs).
- Sample-size rationale: `research/protocol.md` section 5. The measured exploratory SD (up to 0.0179, J-0006) gives an unadjusted 95% half-width of about 0.0067 at 30 seeds (planning estimate).
- Budget: fixed per arm by design; total compute expected under ten minutes (estimate).

## 6. Metric formulas

Accuracy `A = (1/I) sum 1[yhat = y]`; Brier `(1/I) sum (1 - q_i)^2`; ECE over 10 equal-width bins; disagreement as defined in `protocol.md` section 4. Units: proportions in [0, 1].

## 7. Uncertainty, exclusion, stopping

Seed-level t intervals and seed-level percentile bootstrap (10,000 resamples); Holm within the primary family. Exclusion only for schema or invariant failures. Fixed design; all 720 runs executed and reported.

## 8. Anticipated failure modes

SEQ order effects confounded with seed (order is seeded and recorded); ceiling effects in S3 (accuracy near 1 limits detectable differences).

## 9. Sensitivity

EXP-003 (dependence structure) and EXP-004 (secondary choices).

## 10. Reproduction

```
uv run paradox run --config research/experiments/EXP-002/config.json --out results/EXP-002/ --pdf
uv run paradox report results/EXP-002/ --pdf
```

The planned `analyse` step is part of `paradox run` (seed-level summaries, intervals and Holm adjustment in `results.json`). `paradox run` refuses the config unless its hash and this protocol's hash match `research/freeze.json`.

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 and applied before the freeze and before any confirmatory run (full list: `research/protocol.md` section 10; approval quoted in `research/freeze.json`).

- **Seeds:** 30 per cell (was 10); 720 runs (section 5).
- **DELIB dropped** from the rules and the budget list, with the reason reported as a limitation (sections 1, 3, 5, 8).
- **Shared seeds** across cells confirmed (section 5).
- **Commands:** `paradox analyse` and `paradox report EXP-002` replaced by the implemented commands (section 10).
- **Exposure disclosure:** exploratory values of the primary contrast for S1 and S4 at `lambda` in {0, 0.5} were seen before the freeze (exploratory seeds; `results/exploratory/smoke/` and `results/exploratory/probe-seed-spread/`). The values are listed in `research/freeze.json`. Confirmatory estimates use the held-out confirmatory seeds.

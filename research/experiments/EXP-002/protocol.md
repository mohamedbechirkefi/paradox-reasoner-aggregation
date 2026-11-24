<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-002 protocol: equal-budget aggregation map (primary)

**Status: DRAFT v0.1, 2026-11-24, awaiting owner freeze (G-FREEZE). Protocol hash: not yet computed (computed at freeze). Depends on EXP-001 passing.**

Project-level definitions are in [`research/protocol.md`](../../protocol.md).

## 1. Question

At an equal budget of `B` reasoner calls per item, in which regions of competence, difficulty heterogeneity and error correlation does each aggregation rule (MV, CW, SEQ, DELIB) improve or degrade accuracy relative to a single reasoner making one call?

## 2. Mechanism and rationale

- Condorcet-type amplification: with independent votes and competence above 0.5, majority accuracy rises with group size; below 0.5 it falls.
- Difficulty heterogeneity: Chen et al. (2024, arXiv:2403.02419, abstract verified) report that majority-vote performance of LLM systems can first rise and then fall with the number of calls, and attribute it to query difficulty diversity (more calls help easy queries and hurt hard ones).
- Correlation: Kaniovski (2008, verified) shows that, under the Bahadur solution, positive correlation lowers jury competence and enlarging a positively correlated jury can be detrimental up to a certain size. Kim et al. (2025, arXiv:2506.07962, abstract verified) report substantial error correlation across LLMs.
- Information sharing: Golub and Jackson (2010, verified abstract) show naive averaging reaches the truth only if the most influential agent's influence vanishes; Mavrodiev, Tessone and Schweitzer (2012, verified abstract) conclude the effect of social influence depends on initial diversity and accuracy. Lorenz et al. (2011) is relevant but unverified in this session.

## 3. Competing explanations

Below-chance item mass (difficulty) versus correlation versus herding; finite-budget effects (convergence not reached at `B = 31`); the confidence model driving CW results; the one-call DELIB advantage.

## 4. Hypotheses, estimand, disconfirmation

As in `research/protocol.md` section 3: primary estimand `Delta_r(cell) = A_r(B) - A_SINGLE` for `r` in {MV, SEQ}; H0 no cell degrades; H1 some cell degrades; Holm-adjusted one-sided 95% bounds. Directional predictions P1 to P3 and their disconfirmation criteria are stated there and are part of this protocol.

## 5. Design

- Unit: one run `(scenario, lambda, seed)`, 2000 items, common random numbers across rules and budgets.
- Independent variables: scenario S1 to S6; `lambda` in {0, 0.25, 0.5, 0.75}; `B` in {1, 3, 5, 9, 15, 31} (DELIB {6, 10, 18, 30}); rule.
- Dependent variables: accuracy (primary); Brier, ECE, disagreement, cost proxy, accuracy per call (secondary).
- Treatment: aggregation rules. Control and baseline: SINGLE (reasoner 1 of the same run, one call).
- Fixed parameters: `w = 0.5`, `delta = 1`, `tau = 1`.
- Seeds: 10 per run cell, from `SeedSequence(20261124)`; 240 runs.
- Sample-size rationale: `research/protocol.md` section 5 (unadjusted 95% half-width about 0.011, planning estimate; seeds raised before freeze if the smoke SD requires).
- Budget: fixed per arm by design; total compute expected under ten minutes (estimate).

## 6. Metric formulas

Accuracy `A = (1/I) sum 1[yhat = y]`; Brier `(1/I) sum (1 - q_i)^2`; ECE over 10 equal-width bins; disagreement as defined in `protocol.md` section 4. Units: proportions in [0, 1].

## 7. Uncertainty, exclusion, stopping

Seed-level t intervals and seed-level percentile bootstrap (10,000 resamples); Holm within the primary family. Exclusion only for schema or invariant failures. Fixed design; all 240 runs executed and reported.

## 8. Anticipated failure modes

SEQ order effects confounded with seed (order is seeded and recorded); DELIB parity mismatch (disclosed); ceiling effects in S3 (accuracy near 1 limits detectable differences).

## 9. Sensitivity

EXP-003 (dependence structure) and EXP-004 (secondary choices).

## 10. Reproduction (planned commands)

```
uv run paradox run --config research/experiments/EXP-002/config.json --out results/EXP-002/
uv run paradox analyse EXP-002
uv run paradox report EXP-002
```

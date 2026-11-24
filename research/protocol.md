<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX research protocol

**Status: DRAFT v0.1 (2026-11-24). Not frozen.** Freezing is the owner's decision (G-FREEZE). Until the owner freezes this protocol and the per-experiment protocols in `research/experiments/EXP-NNN/protocol.md`, every run is exploratory and labelled as such. All numbers in this document are design parameters or planning estimates, not results.

The feasibility audit is in [`feasibility.md`](feasibility.md). Evidence for the design choices is in [`literature_review.md`](literature_review.md).

## 1. Research question

Under equal compute budgets, when does aggregation of fallible reasoners improve or degrade accuracy?

Operationally: for a binary decision task solved by deterministic, seeded synthetic reasoners, and for a fixed budget of `B` reasoner calls per item, how does the accuracy of an aggregation rule compare with the accuracy of a single reasoner making one call, as a function of (a) individual competence, (b) heterogeneity of item difficulty, (c) error correlation between reasoners and (d) the budget `B`?

## 2. Formal model (draft)

### 2.1 Items

- Items `i = 1..I`, each with a binary ground truth `y_i` in {0, 1}, drawn Bernoulli(0.5). Only correctness matters; the label symmetry removes answer bias.
- Each item belongs to a difficulty class. Scenario parameters `(p_easy, h, p_hard)`: with probability `h` the item is hard and its competence is `p_i = p_hard`; otherwise `p_i = p_easy`. `h = 0` gives a homogeneous task.
- Mean competence (single-reasoner accuracy): `mu = (1 - h) p_easy + h p_hard`.

### 2.2 Reasoners and correlation (common-shock model, primary)

- For each item there is a shared latent answer `L_i`, correct with probability `p_i`.
- Each reasoner `j` independently, with probability `lambda`, adopts `L_i`; otherwise it draws a private answer, correct with probability `p_i`.
- Each reasoner's marginal probability of being correct on item `i` is `p_i`. The conditional (within-item) pairwise correlation of correctness is `lambda^2`. Across items, difficulty heterogeneity induces further correlation.
- This is the opinion-leader structure of Boland (1989) and Boland, Proschan and Tong (1989), as summarised in a secondary source (see literature review: primary sources unverified).

Alternative dependence models (EXP-003 only): Bahadur second-order homogeneous model (Kaniovski 2008, verified), continuous Beta difficulty, and a matched common-shock model.

### 2.3 Confidence (draft, owner decision O-4)

Each reasoner reports a confidence `c_ij` in (0.5, 1) in its own answer: `c_ij = min(0.999, 0.5 + 0.5 * sigmoid(tau * s_ij))`, where `s_ij ~ Normal(+delta, 1)` if the answer is correct and `Normal(-delta, 1)` otherwise. `delta` sets how informative confidence is; `tau` scales over- or under-confidence. A reasoner that adopted `L_i` shares the leader's `s`. Calibration is measured, never assumed. Primary values: `delta = 1`, `tau = 1`. This parameterisation is a draft; the owner may replace it before freeze.

### 2.4 Budget accounting

- One reasoner call = one unit of budget. `B` = calls per item.
- Primary cost proxy: calls per item. Secondary cost proxy (EXP-004): calls plus messages read (a reasoner that reads `k` earlier votes reads `k` messages).

### 2.5 Aggregation rules

| Id | Rule | Calls per item | Information sharing |
|---|---|---|---|
| SINGLE | One reasoner, one call (baseline) | 1 | none |
| MV | Simple majority of `n = B` reasoners (odd `B`) | `B` | none |
| CW | Confidence-weighted vote, weight `logit(c_ij)` | `B` | none |
| SEQ | Sequential public voting in a seeded random order. Reasoner `k` sees the tally of earlier votes; if one answer strictly leads, it votes with the leader with probability `w`, else it votes its private answer. Final decision: majority of public votes. | `B` | sequential, herding |
| DELIB | `n` reasoners answer privately (round 0); one revision round in which each reasoner that disagrees with the round-0 majority switches to it with probability `w`. Final decision: majority of round-1 answers. | `B = 2n` | one broadcast round |

Primary `w = 0.5`. DELIB uses an even budget `B = 2n`; it is compared with MV at `B - 1` calls (largest odd budget not above `B`), which favours DELIB by one call and is disclosed.

### 2.6 Common random numbers

For each `(scenario, lambda, seed)` run, one item pool and one table of draws for reasoners `j = 1..31` are generated. Every rule and every `B` uses prefixes of the same table. SINGLE is reasoner 1. Comparisons are therefore paired by item and seed.

### 2.7 Theoretical baselines

- Independent votes, homogeneous competence `p`: `M_n(p) = sum_{t=(n+1)/2}^{n} C(n,t) p^t (1-p)^(n-t)` (Condorcet binomial).
- Common-shock model, odd `n`, `m = (n+1)/2`: `G(n,p,lambda) = sum_{k=0}^{n} C(n,k) lambda^k (1-lambda)^(n-k) [ p P(Bin(n-k,p) >= m-k) + (1-p) P(Bin(n-k,p) >= m) ]`.
- Two-class mixture: `A_MV = (1-h) G(n,p_easy,lambda) + h G(n,p_hard,lambda)`.
- Bahadur second-order homogeneous model (Kaniovski 2008, Theorem 1, verified in the working-paper PDF): `M^B_n(p,c) = M_n(p) + c n(n-1)(0.5-p) C(n-2,(n-1)/2) (pq)^((n-1)/2)`. Golden fixtures: `p = 0.55, c = 0.4` gives 0.54505 at `n = 3` and 0.5196194 at `n = 5` (recomputed locally on 2026-11-24, matching the values quoted in the secondary source).
- Asymptotic MV accuracy with `lambda = 0`: `(1-h) 1[p_easy > 0.5] + h 1[p_hard > 0.5]`. Hence, for large `B`, MV is predicted to be less accurate than SINGLE exactly when `(1-h)(1-p_easy) < h p_hard` (with `p_easy > 0.5 > p_hard`). This is a theoretical prediction, not an observation.

## 3. Hypotheses (draft)

**Primary metric:** accuracy `A = (1/I) sum_i 1[yhat_i = y_i]`, higher is better.

**Justification for a single primary metric.** The question is about improvement or degradation of correctness. Accuracy is the quantity the Condorcet literature and the LLM-voting literature both report, it has an exact theoretical baseline under independence, and it is defined identically for every rule. Calibration, disagreement and cost are informative but secondary: calibration is undefined for rules without a probability output unless a convention is added, and cost is held fixed by design.

**Primary estimand:** `Delta_r(cell) = A_r(B) - A_SINGLE`, paired by item and seed, for `r` in {MV, SEQ}, in every cell (scenario x lambda x B, `B >= 3`).

- **H0 (no degradation):** `Delta_r(cell) >= 0` in every preregistered cell, for both MV and SEQ.
- **H1 (degradation exists):** `Delta_r(cell) < 0` in at least one preregistered cell.
- **Decision rule:** H0 is rejected if at least one cell has a Holm-adjusted one-sided 95% upper confidence bound below 0 (family: all MV and SEQ cells of EXP-002).

**Preregistered directional predictions** (derived from theory and the literature before any run):

- **P1 (MV, difficulty heterogeneity).** At `lambda = 0` and `B = 31`, `Delta_MV < 0` in scenarios with `(1-h)(1-p_easy) < h p_hard`, and `Delta_MV > 0` otherwise. Disconfirmed if a predicted-negative cell has a lower bound above 0, or a predicted-positive cell has an upper bound below 0.
- **P2 (information sharing).** At `lambda = 0` and every `B >= 3`, `Delta_SEQ < Delta_MV` (herding reduces the gain from aggregation). Disconfirmed if `Delta_SEQ - Delta_MV` has a lower bound above 0 in any such cell.
- **P3 (correlation).** In homogeneous scenarios, `Delta_MV` decreases as `lambda` increases at fixed `B`. Disconfirmed by an increase whose lower bound is above 0.

## 4. Secondary metrics

| Metric | Definition | Unit / direction |
|---|---|---|
| Brier score | `(1/I) sum_i (1 - q_i)^2`, `q_i` the probability the rule assigns to the true answer (MV, SEQ, DELIB: vote share; CW: normalised weight share; SINGLE: `c` if correct, `1-c` otherwise) | [0, 1], lower is better |
| ECE | expected calibration error over 10 equal-width bins of the probability assigned to the chosen answer | [0, 1], lower is better |
| Disagreement | share of items with a non-unanimous vote; mean pairwise disagreement rate | [0, 1], descriptive |
| Cost proxy | calls per item (primary); calls plus messages read (EXP-004) | calls, descriptive |
| Accuracy per call | `(A_r - 0.5) / B` | per call, descriptive |

## 5. Design

- **Experimental unit:** one run = one `(scenario, lambda, seed)` combination with a fresh item pool and reasoner-draw table. Items are nested in runs; all rules and budgets within a run share common random numbers.
- **Seeds:** 10 independent seeds per cell (master prompt minimum: 5). Seeds are fixed integers listed in each experiment's `config.json`, derived from `numpy.random.SeedSequence(20261124).spawn(...)`.
- **Items per run:** 2000.
- **Sample-size rationale (planning estimate, not a result).** The paired per-item difference takes values in {-1, 0, 1}; its variance is at most about 0.5, so the per-run standard deviation of `Delta` is at most about `sqrt(0.5/2000) = 0.016`. With 10 seeds the standard error of the mean `Delta` is about 0.005 and the unadjusted 95% half-width about 0.011. The smoke run will measure the actual between-seed SD; if the unadjusted half-width exceeds 0.01 in the primary cells, the seed count is raised before freeze (cap 30). Compute is not a constraint (section 8 of feasibility).
- **Uncertainty method:** per run, compute the paired `Delta`; across the 10 seed-runs, report mean, SD, a t-based 95% interval and a seed-level percentile bootstrap interval (10,000 resamples, fixed bootstrap seed). The seed-run is the independent unit; items are not treated as independent across runs. Raw per-seed values are always reported. Deterministic analytic values are reported exactly, without intervals.
- **Multiplicity:** Holm adjustment within the primary family; secondary metrics are descriptive.
- **Exclusion rules:** a run is excluded only if it fails schema validation or an invariant check (vote counts equal `n`, budget equals the declared `B`, marginal competence of reasoner 1 within 4 Monte Carlo SE of `mu`). Exclusions are reported with reasons. No exclusion based on outcomes.
- **Stopping rules:** fixed design; every cell is run. If EXP-001 (engine validation) fails, EXP-002 to EXP-004 do not start until the defect is fixed and EXP-001 passes again (engine incorrect means no campaign). No optional stopping, no early termination for favourable results.
- **Held-out data:** there is no tuning. The confirmatory seeds are generated from a SeedSequence entropy value (20261124) distinct from the exploratory and smoke entropy (0).

## 6. Matrices

### 6.1 Smoke matrix (exploratory)

Scenarios S1 and S4; `lambda` in {0, 0.5}; `B` in {1, 3, 9} (DELIB: `B` = 6); all rules; 2 seeds; 200 items. Purpose: exercise the pipeline, schemas and invariants, and estimate the between-seed SD. Results are exploratory and are not used to test hypotheses.

### 6.2 Full matrix (EXP-002, confirmatory once frozen)

| Scenario | `p_easy` | `h` | `p_hard` | `mu` | P1 prediction at `B = 31`, `lambda = 0` |
|---|---|---|---|---|---|
| S1 | 0.60 | 0 | n/a | 0.60 | gain |
| S2 | 0.55 | 0 | n/a | 0.55 | gain |
| S3 | 0.80 | 0 | n/a | 0.80 | gain |
| S4 | 0.90 | 0.4 | 0.30 | 0.66 | degradation |
| S5 | 0.70 | 0.2 | 0.45 | 0.65 | gain |
| S6 | 0.95 | 0.5 | 0.35 | 0.65 | degradation |

`lambda` in {0, 0.25, 0.5, 0.75}; `B` in {1, 3, 5, 9, 15, 31} for SINGLE, MV, CW, SEQ; `B` in {6, 10, 18, 30} for DELIB. 6 x 4 = 24 run cells x 10 seeds = 240 runs.

## 7. Sensitivity analyses

- **Dependence structure (EXP-003, could invalidate the main interpretation).** If the interpretation of EXP-002 is that degradation of MV is driven by below-chance item mass and not by correlation itself, this is invalidated if, at matched marginal competence and matched pairwise correlation, a homogeneous model without below-chance items (Bahadur second-order) also shows degradation. The Kaniovski fixture (`p = 0.55, c = 0.4`, `n = 3`: 0.54505 < 0.55) indicates this can happen in principle, so the outcome is genuinely uncertain across the matrix.
- **Secondary choices (EXP-004):** tie rule at even `B`, cost accounting with message reads, confidence miscalibration `tau`, herding strength `w`.

## 8. Confounders and controls

- Budget is matched by construction; the one-call DELIB advantage is disclosed.
- Mean competence is matched within scenarios S4 to S6 (0.65 to 0.66) so that differences reflect structure, not average skill.
- Common random numbers remove between-rule sampling noise.
- The answer-label prior is fixed at 0.5, so a rule cannot gain from a label bias.

## 9. Claims boundary

Synthetic reasoners are not LLMs. Results hold only within the stated model. No statement about any real LLM, human group or product follows from these simulations.

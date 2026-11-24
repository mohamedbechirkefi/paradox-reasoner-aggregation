<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX research protocol

**Status: FROZEN v1.0 (owner-approved 2026-11-24).** Drafted as v0.1 on 2026-11-24; the owner approved the amendments listed in section 10 and the freeze on 2026-11-24 (G-FREEZE). The SHA-256 of this file, of each `research/experiments/EXP-NNN/protocol.md` and of each confirmatory config is recorded in `research/freeze.json`; any later change is a post-freeze deviation, dated and justified, and analyses it affects are exploratory. All numbers in this document are design parameters or planning estimates, not results.

The feasibility audit is in [`feasibility.md`](feasibility.md). Evidence for the design choices is in [`literature_review.md`](literature_review.md).

## 1. Research question

Under equal compute budgets, when does aggregation of fallible reasoners improve or degrade accuracy?

Operationally: for a binary decision task solved by deterministic, seeded synthetic reasoners, and for a fixed budget of `B` reasoner calls per item, how does the accuracy of an aggregation rule compare with the accuracy of a single reasoner making one call, as a function of (a) individual competence, (b) heterogeneity of item difficulty, (c) error correlation between reasoners and (d) the budget `B`?

## 2. Formal model

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

### 2.3 Confidence (owner decision O-4)

Each reasoner reports a confidence `c_ij` in (0.5, 1) in its own answer: `c_ij = min(0.999, 0.5 + 0.5 * sigmoid(tau * s_ij))`, where `s_ij ~ Normal(+delta, 1)` if the answer is correct and `Normal(-delta, 1)` otherwise. `delta` sets how informative confidence is; `tau` scales over- or under-confidence. A reasoner that adopted `L_i` shares the leader's `s`. Calibration is measured, never assumed. Primary values: `delta = 1`, `tau = 1`. This parameterisation is kept as drafted at the freeze. The M2 proposal to fix `delta` from a stated target (A-3) was not among the approved amendments; CW results therefore depend on this assumed confidence model, which is stated as a limitation, and CW stays a secondary, descriptive rule.

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
| DELIB (dropped) | `n` reasoners answer privately (round 0); one revision round in which each reasoner that disagrees with the round-0 majority switches to it with probability `w`. Final decision: majority of round-1 answers. | `B = 2n` | one broadcast round |

Primary `w = 0.5`.

**DELIB is dropped from the confirmatory analysis (amendment 2, section 10).** As specified, only minority members switch, and only towards the round-0 majority, so the round-1 majority always equals the round-0 majority: DELIB at `2n` calls is MV at `n` calls on every item, for any `w`. It is therefore not run in EXP-002 or EXP-004, and this is reported as a limitation. The implementation is kept, and its degeneracy is pinned by the test `test_delib_as_drafted_always_equals_mv_of_round0`. SEQ is the only information-sharing rule in the confirmatory experiments.

### 2.6 Common random numbers

For each `(scenario, lambda, seed)` run, one item pool and one table of draws for reasoners `j = 1..31` are generated. Every rule and every `B` uses prefixes of the same table. SINGLE is reasoner 1. Comparisons are therefore paired by item and seed.

Seeds are shared across cells (decision D-008, confirmed by the owner at the freeze): every `(scenario, lambda)` cell of an experiment uses the same seed list, and each random component has its own child stream. Comparisons across `lambda` and scenarios are thus also paired by seed, and cells are not independent of one another; analyses that pool or count cells state this.

### 2.7 Theoretical baselines

- Independent votes, homogeneous competence `p`: `M_n(p) = sum_{t=(n+1)/2}^{n} C(n,t) p^t (1-p)^(n-t)` (Condorcet binomial).
- Common-shock model, odd `n`, `m = (n+1)/2`: `G(n,p,lambda) = sum_{k=0}^{n} C(n,k) lambda^k (1-lambda)^(n-k) [ p P(Bin(n-k,p) >= m-k) + (1-p) P(Bin(n-k,p) >= m) ]`.
- Two-class mixture: `A_MV = (1-h) G(n,p_easy,lambda) + h G(n,p_hard,lambda)`.
- Bahadur second-order homogeneous model (Kaniovski 2008, Theorem 1, verified in the working-paper PDF): `M^B_n(p,c) = M_n(p) + c n(n-1)(0.5-p) C(n-2,(n-1)/2) (pq)^((n-1)/2)`. Golden fixtures: `p = 0.55, c = 0.4` gives 0.54505 at `n = 3` and 0.5196194 at `n = 5` (recomputed locally on 2026-11-24, matching the values quoted in the secondary source).
- Asymptotic MV accuracy with `lambda = 0`: `(1-h) 1[p_easy > 0.5] + h 1[p_hard > 0.5]`. Hence, for large `B`, MV is predicted to be less accurate than SINGLE exactly when `(1-h)(1-p_easy) < h p_hard` (with `p_easy > 0.5 > p_hard`). This is a theoretical prediction, not an observation.

## 3. Hypotheses

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
| Brier score | `(1/I) sum_i (1 - q_i)^2`, `q_i` the probability the rule assigns to the true answer (MV, SEQ: vote share; CW: normalised weight share; SINGLE: `c` if correct, `1-c` otherwise) | [0, 1], lower is better |
| ECE | expected calibration error over 10 equal-width bins of the probability assigned to the chosen answer | [0, 1], lower is better |
| Disagreement | share of items with a non-unanimous vote; mean pairwise disagreement rate | [0, 1], descriptive |
| Cost proxy | calls per item (primary); calls plus messages read (EXP-004) | calls, descriptive |
| Accuracy per call | `(A_r - 0.5) / B` | per call, descriptive |

## 5. Design

- **Experimental unit:** one run = one `(scenario, lambda, seed)` combination with a fresh item pool and reasoner-draw table. Items are nested in runs; all rules and budgets within a run share common random numbers.
- **Seeds:** 30 seeds per cell (amendment 1; master prompt minimum: 5; the cap stated in v0.1 was 30). Seeds are derived from `numpy.random.SeedSequence(20261124).spawn(30)` and are the same list in every cell of an experiment (section 2.6). Each experiment's `config.json` states the entropy and the seed count; the runner derives the seed list and records it in every result.
- **Items per run:** 2000.
- **Sample-size rationale (planning estimate, not a result).** The paired per-item difference takes values in {-1, 0, 1}; its variance is at most about 0.5, so the per-run standard deviation of `Delta` is at most about `sqrt(0.5/2000) = 0.016`. With 10 seeds the standard error of the mean `Delta` is about 0.005 and the unadjusted 95% half-width about 0.011. The smoke run will measure the actual between-seed SD; if the unadjusted half-width exceeds 0.01 in the primary cells, the seed count is raised before freeze (cap 30). Compute is not a constraint (section 8 of feasibility). Applied at the freeze: the exploratory seed-spread probe (journal J-0006, exploratory seeds) measured between-seed SDs of the paired `Delta` up to 0.0179 in MV and SEQ cells, giving a 10-seed half-width of 0.0128, above the rule; the owner approved 30 seeds, for which the same SD gives a half-width of about 0.0067 (planning estimate).
- **Uncertainty method:** per run, compute the paired `Delta`; across the 30 seed-runs, report mean, SD, a t-based 95% interval and a seed-level percentile bootstrap interval (10,000 resamples, fixed bootstrap seed). The seed-run is the independent unit; items are not treated as independent across runs. Raw per-seed values are always reported. Deterministic analytic values are reported exactly, without intervals.
- **Multiplicity:** Holm adjustment within the primary family; secondary metrics are descriptive.
- **Exclusion rules:** a run is excluded only if it fails schema validation or an invariant check (vote counts equal `n`, budget equals the declared `B`, marginal competence of reasoner 1 within 4 Monte Carlo SE of `mu`). Exclusions are reported with reasons. No exclusion based on outcomes.
- **Stopping rules:** fixed design; every cell is run. If EXP-001 (engine validation) fails, EXP-002 to EXP-004 do not start until the defect is fixed and EXP-001 passes again (engine incorrect means no campaign). No optional stopping, no early termination for favourable results.
- **Held-out data:** there is no tuning. The confirmatory seeds are generated from a SeedSequence entropy value (20261124) distinct from the exploratory and smoke entropy (0).

## 6. Matrices

### 6.1 Smoke matrix (exploratory)

Scenarios S1 and S4; `lambda` in {0, 0.5}; `B` in {1, 3, 9} (DELIB: `B` = 6); all rules; 2 seeds; 200 items. (Run before the freeze with exploratory seeds; see section 10, amendment 6.) Purpose: exercise the pipeline, schemas and invariants, and estimate the between-seed SD. Results are exploratory and are not used to test hypotheses.

### 6.2 Full matrix (EXP-002, confirmatory once frozen)

| Scenario | `p_easy` | `h` | `p_hard` | `mu` | P1 prediction at `B = 31`, `lambda = 0` |
|---|---|---|---|---|---|
| S1 | 0.60 | 0 | n/a | 0.60 | gain |
| S2 | 0.55 | 0 | n/a | 0.55 | gain |
| S3 | 0.80 | 0 | n/a | 0.80 | gain |
| S4 | 0.90 | 0.4 | 0.30 | 0.66 | degradation |
| S5 | 0.70 | 0.2 | 0.45 | 0.65 | gain |
| S6 | 0.95 | 0.5 | 0.35 | 0.65 | degradation |

`lambda` in {0, 0.25, 0.5, 0.75}; `B` in {1, 3, 5, 9, 15, 31} for SINGLE, MV, CW, SEQ (DELIB dropped, section 2.5). 6 x 4 = 24 run cells x 30 seeds = 720 runs.

## 7. Sensitivity analyses

- **Dependence structure (EXP-003, could invalidate the main interpretation).** If the interpretation of EXP-002 is that degradation of MV is driven by below-chance item mass and not by correlation itself, this is invalidated if, at matched marginal competence and matched pairwise correlation, a homogeneous model without below-chance items (Bahadur second-order) also shows degradation. The Kaniovski fixture (`p = 0.55, c = 0.4`, `n = 3`: 0.54505 < 0.55) indicates this can happen in principle, so the outcome is genuinely uncertain across the matrix.
- **Secondary choices (EXP-004, optional):** tie rule at even `B`, cost accounting with message reads, confidence miscalibration `tau`, herding strength `w`. EXP-004 stays in the design as optional (amendment 3): it is the first experiment cut if the schedule is threatened, and a cut is reported.

## 8. Confounders and controls

- Budget is matched by construction (DELIB, the only rule with a parity mismatch, is dropped).
- Mean competence is matched within scenarios S4 to S6 (0.65 to 0.66) so that differences reflect structure, not average skill.
- Common random numbers remove between-rule sampling noise.
- The answer-label prior is fixed at 0.5, so a rule cannot gain from a label bias.

## 9. Claims boundary

Synthetic reasoners are not LLMs. Results hold only within the stated model. No statement about any real LLM, human group or product follows from these simulations.

## 10. Amendments before freeze (owner-approved 2026-11-24)

The owner approved the following amendments to draft v0.1 on 2026-11-24 (source: `labs/_shared/owner-approvals-2026-11-24.md`, PARADOX section, outside this repository; quoted in `research/freeze.json`). They were applied before the freeze and before any confirmatory run. No value was set by looking at the primary contrast.

1. **30 seeds** per cell in every experiment (sections 5 and 6.2; EXP-001 to EXP-004). Proposal A-1.
2. **DELIB dropped from the primary analysis**, with the reason (identical to MV at half the calls) reported as a limitation (sections 2.5, 4, 6.2, 8; EXP-002, EXP-004; `research/limitations.md`). Proposal A-2, option (c).
3. **EXP-004 stays optional** (section 7; EXP-004 header). Decision O-5.
4. **Inadmissible Bahadur cells are reported exclusions**; the grids are not narrowed (EXP-001 section 8, EXP-003 section 5). Proposal A-4.
5. **Command names updated** to the implemented CLI (`paradox run`, `paradox report`) in every experiment protocol, and **seeds shared across cells** confirmed (section 2.6; EXP-001 section 7). Proposal A-5, decision D-008.
6. **Exploratory S1/S4 values disclosed.** Before the freeze, exploratory runs with exploratory seeds (SeedSequence entropy 0, not the confirmatory entropy 20261124) produced values of the primary contrast for S1 and S4 at `lambda` in {0, 0.5}: the smoke run (`results/exploratory/smoke/`, 2 seeds of 200 items) and the seed-spread probe (`results/exploratory/probe-seed-spread/`, 10 seeds of 2000 items, the planned run size). These values were seen by the session and are readable by anyone. The values are listed in `research/freeze.json` (common decision C4). They were used only to set the seed count by the rule of section 5, not to choose any other design value. Confirmatory estimates for these cells use the held-out confirmatory seeds.

Proposal A-3 (the confidence model behind CW) was not among the approved amendments; section 2.3 is unchanged in substance and the dependence of CW on the confidence model is a stated limitation.

<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
<!-- Canonical manuscript (master prompt section 11.4). Synthesised in M4 (2026-11-25) from committed results only; every number maps to research/publication/artifact_manifest.json. Revised after the second review pass (research/publication/review_pass_2.md). -->

# When more reasoners make worse decisions: an equal-budget simulation study of majority, confidence-weighted and sequential aggregation

**Status: independent research manuscript / preprint draft, not peer-reviewed.**

## Author and affiliation metadata

- **Author:** Mohamed Bechir Kefi.
- **Affiliation:** none (independent research).
- **AI assistance:** an AI system (Claude, Anthropic) was used as a research and development assistant for code, analysis and drafting under the author's direction. It is not an author. The author is responsible for the content. Details are in section 11.
- **Status:** independent research manuscript / preprint draft, not peer-reviewed.

## Abstract

Aggregating the answers of several fallible reasoners is often assumed to help, yet group accuracy can fall below that of a single reasoner when errors are correlated or items vary in difficulty. We ask, for deterministic synthetic reasoners on binary decisions and a fixed budget of `B` reasoner calls per item, when majority voting (MV), confidence-weighted voting (CW) and sequential public voting (SEQ) are more or less accurate than one reasoner making one call. Four experiments were preregistered and frozen before any confirmatory run. The simulation engine reproduced closed-form majority accuracy in all 292 admissible validation cells (largest deviation 3.116 Monte Carlo standard errors against a tolerance of 4). In the primary experiment (720 runs, 30 seeds per cell), the hypothesis of no degradation was rejected in 32 of 240 MV and SEQ cells after Holm adjustment, all in the two scenarios with substantial below-chance item mass, as theory predicted. The largest loss was MV at `B = 31`: -0.1313 accuracy (95% interval -0.1350 to -0.1276). Contrary to a preregistered prediction, sequential voting lost less than MV in exactly those scenarios. A sensitivity experiment showed that, at matched competence and pairwise correlation, the sign of the majority effect differs between dependence models in 16 of 48 cells, so the degradation result holds only for the common-shock and two-class mixture families. A robustness experiment found no sign reversal, but it covered only 3 of the 32 significant cells. CW's apparent superiority depends on an assumed confidence model. No statement about language models, people or products follows.

## Keywords

majority voting; Condorcet jury theorem; correlated errors; difficulty heterogeneity; information cascades; preregistered simulation

## 1. Introduction

Systems that query a fallible reasoner several times and aggregate the answers are common, from juries and committees to repeated sampling of a language model with majority voting [wang2022; li2024]. The classical justification is Condorcet-type amplification: with independent votes and competence above one half, the probability that a majority is correct rises with group size. Both assumptions can fail. Errors can be correlated [kaniovski2008; kim2025], and items can differ in difficulty so that some are answered correctly less than half the time. Chen et al. report, for compound language-model systems, that voting performance can first rise and then fall with the number of calls, and attribute this to the diversity of query difficulty [chen2024]. Information sharing between reasoners can also help or hurt [golub2010; mavrodiev2012].

These effects are usually studied one at a time. The question here is narrower and controlled: **under an equal compute budget, when does aggregation of fallible reasoners improve or degrade accuracy?** We hold the number of reasoner calls per item fixed, compare each rule with one reasoner making one call, and vary individual competence, difficulty heterogeneity, error correlation and the budget within one model with exact theoretical baselines.

The study tests three preregistered directional predictions and one sensitivity question:

- **P1.** At no correlation and `B = 31`, MV is worse than a single reasoner exactly in the scenarios where the asymptotic condition `(1 - h)(1 - p_easy) < h p_hard` holds.
- **P2.** Sequential public voting (herding) is less accurate than MV at no correlation.
- **P3.** In homogeneous scenarios, the MV gain decreases as correlation increases.
- **Sensitivity.** Whether pairwise correlation at matched competence determines the sign of the majority effect.

**Contributions.** We do not claim novelty; whether this combination of elements is new has not been established (section 2).

1. A seeded, tested simulation engine whose majority-vote accuracy is validated against four closed forms (EXP-001).
2. A preregistered equal-budget map of 240 rule-by-cell contrasts with paired, seed-level uncertainty and Holm control (EXP-002), including a disconfirmed prediction (P2).
3. A matched-moment comparison of four dependence models (EXP-003) showing that the degradation result is model-dependent, which restricts the main claim.
4. A one-factor robustness check (EXP-004) and exploratory sensitivity analyses that delimit what the results do and do not show.

## 2. Related work

All sources below were opened by the project; what was read is stated. The literature pass was targeted, not systematic (`research/literature_review.md`).

**Voting over repeated samples.** Wang et al. propose majority voting over sampled reasoning paths of a language model [wang2022, abstract read]. Li et al. report that sampling-and-voting accuracy grows with the number of agents, with a gain that depends on task difficulty [li2024, abstract read]. Chen et al. report non-monotonic voting performance in the number of calls and attribute it to query difficulty diversity [chen2024, abstract read]. Our two-class difficulty mixture is a controlled analogue of that mechanism; we make no claim about language models.

**Correlated votes.** Kaniovski gives a closed form for majority accuracy in a homogeneous jury with Bahadur second-order dependence and shows that positive correlation lowers jury competence and that enlarging a correlated jury can be detrimental up to a certain size [kaniovski2008, full text pages 1 to 13 read, Theorem 1 transcribed]. We use his Theorem 1 as a validated reference and as one of the four dependence models. Kim et al. report substantial error correlation across many language models [kim2025, abstract read]. Our common-shock model is the opinion-leader structure attributed to Boland and co-authors in secondary sources; those primary papers were not opened and are not cited as read.

**Information sharing.** Golub and Jackson show that naive averaging in networks converges to the truth only if the most influential agent's influence vanishes [golub2010, abstract read]. Mavrodiev, Tessone and Schweitzer conclude that whether social influence helps depends on initial diversity and accuracy [mavrodiev2012, abstract read]. Du et al. study multi-round debate between language models [du2023, abstract read]; a debate-like rule (DELIB) was planned here but dropped because, as specified, it was equivalent to MV (section 4.3).

**Relation to this study.** The degradation of MV under below-chance item mass and the damping effect of correlation are consequences of known closed forms; we replicate them under a preregistered protocol rather than discover them. The extension is the equal-budget comparison of three rules in one engine, with paired uncertainty, and the explicit test of whether pairwise correlation is a sufficient summary of dependence.

## 3. Background and formal model

**Items.** Item `i` has a binary truth `y_i ~ Bernoulli(0.5)`. With probability `h` it is hard, with competence `p_i = p_hard`; otherwise `p_i = p_easy`. Mean competence is `mu = (1 - h) p_easy + h p_hard`.

**Common-shock dependence (primary).** For each item a shared latent answer `L_i` is correct with probability `p_i`. Each reasoner adopts `L_i` with probability `lambda`, otherwise it answers privately, correct with probability `p_i`. Each reasoner's marginal accuracy on item `i` is `p_i`, and the within-item pairwise correlation of correctness is `lambda^2`.

**Confidence.** Each reasoner reports `c_ij = min(0.999, 0.5 + 0.5 sigmoid(tau s_ij))` with `s_ij ~ Normal(+delta, 1)` if correct and `Normal(-delta, 1)` otherwise; confirmatory values `delta = 1`, `tau = 1`. This is an assumption, not a calibrated model of any real reasoner.

**Rules.** SINGLE is one reasoner, one call. MV is a simple majority of `n = B` reasoners. CW weights each vote by `logit(c_ij)`. SEQ is sequential public voting in a seeded random order: a reasoner that sees one answer strictly leading the earlier votes follows the leader with probability `w = 0.5`, otherwise it votes its private answer; the decision is the majority of public votes. Every rule uses exactly `B` calls per item.

**Closed forms.** With independent votes and homogeneous `p`, `M_n(p) = sum_{t=(n+1)/2}^{n} C(n,t) p^t (1-p)^(n-t)`. Under the common-shock model, with `m = (n+1)/2`,

`G(n, p, lambda) = sum_{k=0}^{n} C(n,k) lambda^k (1-lambda)^(n-k) [ p P(Bin(n-k, p) >= m-k) + (1-p) P(Bin(n-k, p) >= m) ]`,   (1)

and the two-class mixture gives `A_MV = (1-h) G(n, p_easy, lambda) + h G(n, p_hard, lambda)`. Kaniovski's Theorem 1 gives, for the Bahadur model with correlation `c`, `M^B_n(p, c) = M_n(p) + c n(n-1)(0.5-p) C(n-2,(n-1)/2) (pq)^((n-1)/2)`. At `lambda = 0` the large-`n` limit of MV accuracy is `(1-h) 1[p_easy > 0.5] + h 1[p_hard > 0.5]`, so with `p_easy > 0.5 > p_hard` MV falls below SINGLE for large `B` exactly when `(1-h)(1-p_easy) < h p_hard`. Each closed form is a finite sum evaluated exactly (`O(n^2)` binomial tails for equation 1).

**Estimand.** `Delta_r(cell) = A_r(B) - A_SINGLE`, paired by item and seed, where accuracy `A` is the share of items decided correctly.

## 4. Methods

### 4.1 Design and protocol registration

The main protocol and four experiment protocols were drafted on 2026-11-24, amended on the owner's decisions and frozen by the owner on 2026-11-24 before any confirmatory run (`research/freeze.json`; main protocol SHA-256 `68ce4b15...`). The run command refuses a confirmatory config unless the protocol and config hashes match the freeze record. Six pre-freeze amendments were applied: 30 seeds per cell; DELIB dropped; EXP-004 kept as optional; inadmissible Bahadur cells reported as exclusions; command names updated and seeds shared across cells confirmed; exploratory values of the primary contrast for S1 and S4 seen before the freeze disclosed (supplementary section S5). A proposed recalibration of the confidence model (A-3) was not adopted.

### 4.2 Synthetic reasoners and data generation

No external data are used. For each `(scenario, lambda, seed)` run, one item pool and one table of draws for 31 reasoners are generated; every rule and budget uses prefixes of the same table (common random numbers), and SINGLE is reasoner 1. Seeds come from `SeedSequence(20261124).spawn(30)` and are the same 30 in every cell (decision D-008), so cells are paired but not independent. Exploratory work used a different entropy (0).

### 4.3 Aggregation rules and budget accounting

Budget is one unit per reasoner call. DELIB, a one-round revision rule, was dropped at the freeze: as specified, only minority members switch and only towards the round-0 majority, so its decision always equals MV of the first `n` reasoners at twice the calls (pinned by a unit test). SEQ is therefore the only information-sharing rule. EXP-004 adds a second cost proxy, calls plus messages read.

### 4.4 Experiments, metrics and statistical analysis

| Experiment | Question | Design | Decision rule (frozen) |
|---|---|---|---|
| EXP-001 | Does the engine reproduce closed-form MV accuracy? | 312 cells (292 admissible) of independent, common-shock, mixture and Bahadur models, `n` 1 to 31; 30 seeds x 20,000 items per cell; 4 golden fixtures | Pass if every admissible cell is within 4 Monte Carlo SE and every fixture is reproduced to 1e-9 |
| EXP-002 | Where do MV, CW and SEQ gain or lose against SINGLE at equal budget? | 6 scenarios x 4 `lambda` x 30 seeds = 720 runs of 2000 items; `B` in {1, 3, 5, 9, 15, 31} | Reject "no degradation" if any of the 240 MV and SEQ cells with `B >= 3` has a Holm-adjusted one-sided 95% upper bound below 0; P1 to P3 judged by unadjusted seed-level t 95% intervals |
| EXP-003 | At matched `p` and pairwise correlation `r`, does the sign of `Delta_MV` depend on the dependence model? | 4 models x `p` {0.55, 0.6, 0.7} x `r` {0.05, 0.1, 0.2, 0.4} x `n` {3, 5, 9, 15}; exact values with a 30-seed Monte Carlo check | Reject "same sign" if the exact signs differ in any matched cell |
| EXP-004 (optional) | Are EXP-002 signs robust to the tie rule, `tau`, `w` and cost accounting? | 8 one-factor variants x S1, S4, S5 x `lambda` {0, 0.5} x 30 seeds = 1440 runs | Reversal if a variant's t 95% interval for a Holm-significant EXP-002 cell lies above 0 |

The scenarios of EXP-002 are S1 to S3 (homogeneous, `p` = 0.60, 0.55, 0.80) and three two-class mixtures `(p_easy, h, p_hard)`: S4 (0.90, 0.4, 0.30), S5 (0.70, 0.2, 0.45) and S6 (0.95, 0.5, 0.35). S4 to S6 have nearly equal mean competence (0.66, 0.65, 0.65), so differences between them reflect structure rather than average skill. P1 predicts degradation in S4 and S6 and gains elsewhere.

The seed-run is the independent unit. For each cell we report the mean paired `Delta` over 30 seed-runs, its SD, a t 95% interval, a seed-level percentile bootstrap interval (10,000 resamples) and a one-sided t p-value. Holm's procedure is applied to the 240-cell primary family. Brier score, expected calibration error and disagreement are secondary and descriptive. The operational readings of the frozen rules (for example, P3 compares consecutive `lambda` levels; EXP-003 signs are judged on exact values, including the beta-binomial closed form for the Beta model) were coded, tested and committed before any confirmatory output (decision D-011).

### 4.5 Implementation and reproducibility

The engine is a Python 3.12 package (`paradox`) with numpy; 321 unit and pipeline tests passed at the provenance revision `d997cf8` of every confirmatory run. Runs were made on one Apple M1 Pro laptop at low priority with at most two processes. Wall-clock times were 89.1 s (EXP-001), 26.3 s (EXP-002), 70.3 s (EXP-003) and 43.7 s (EXP-004); there was no paid compute. Every run has a provenance row (seed, config hash, revision, data manifest hash, hardware, times, exit status) and every output file a SHA-256 entry. All four experiments exited with status 0; no run failed, was retried or was dropped.

### 4.6 Exploratory versus confirmatory work

Everything in section 5.1 to 5.4 marked "frozen rule" is confirmatory. Section 5.5 reports checks made after all verdicts, during the interpretation milestone (M4): closed-form evaluations at larger group sizes (journal J-0015) and a confidence-informativeness sweep with exploratory seeds (J-0016). They are exploratory, they are kept in `results/exploratory/`, and they change no verdict. Before the freeze, exploratory smoke and probe runs with exploratory seeds were used to test the pipeline and set the seed count (supplementary section S5).

## 5. Results

### 5.1 EXP-001: engine validation (frozen rule: PASS)

All 292 admissible cells were within tolerance; 20 Bahadur cells were excluded as inadmissible, exactly as the protocol listed. The largest absolute standardised deviation was 3.116 (S6 mixture, `lambda = 0.5`, `n = 5`), and 30 cells exceeded 2. The four golden fixtures were reproduced, including Kaniovski's `M^B_3(0.55, 0.4) = 0.54505` and `M^B_5(0.55, 0.4) = 0.5196194`. The S6 mixture cells all deviate in the same direction; a post-hoc diagnostic traced this to the shared realised share of hard items (0.49886 against `h = 0.5`, z = -1.76), an expected consequence of common random numbers (J-0011). Agreement validates the engine and the formulas against each other within the grid; it cannot detect an error shared by the model definition and its formula (Figure FIG-001-1 in the EXP-001 report).

### 5.2 EXP-002: equal-budget aggregation map

**Primary decision (frozen rule: H0 rejected).** 32 of 240 MV and SEQ cells have a Holm-adjusted one-sided upper bound below 0: 20 MV and 12 SEQ cells, all in S4 and S6. No cell in S1, S2, S3 or S5 is rejected. Because the cells share seeds and nested budgets, these 32 cells describe three connected patterns (MV in S4, MV in S6, SEQ in S6) rather than 32 independent findings.

Table 1. Accuracy change against SINGLE at `B = 31`, mean over 30 seed-runs of 2000 items, seed-level t 95% interval (source: `results/EXP-002/report.md`, `analysis.json`; CW descriptive).

| Scenario | lambda | SINGLE accuracy | MV Delta [t95] | SEQ Delta [t95] | CW Delta [t95] |
|---|---|---|---|---|---|
| S1 | 0 | 0.5997 | +0.2708 [+0.2666, +0.2749] | +0.0624 [+0.0567, +0.0680] | +0.4001 [+0.3964, +0.4038] |
| S2 | 0 | 0.5509 | +0.1620 [+0.1568, +0.1672] | +0.0311 [+0.0251, +0.0372] | +0.4478 [+0.4440, +0.4516] |
| S3 | 0 | 0.8012 | +0.1988 [+0.1953, +0.2022] | +0.1059 [+0.1023, +0.1096] | +0.1988 [+0.1954, +0.2023] |
| S4 | 0 | 0.6645 | -0.0570 [-0.0602, -0.0537] | +0.0003 [-0.0034, +0.0039] | +0.2080 [+0.2048, +0.2112] |
| S4 | 0.5 | 0.6628 | +0.0119 [+0.0097, +0.0141] | +0.0026 [+0.0004, +0.0048] | +0.0984 [+0.0958, +0.1009] |
| S5 | 0 | 0.6534 | +0.1984 [+0.1938, +0.2030] | +0.0742 [+0.0687, +0.0798] | +0.3422 [+0.3388, +0.3456] |
| S6 | 0 | 0.6570 | -0.1313 [-0.1350, -0.1276] | -0.0266 [-0.0316, -0.0216] | +0.2628 [+0.2588, +0.2668] |
| S6 | 0.5 | 0.6556 | +0.0040 [+0.0011, +0.0068] | -0.0102 [-0.0134, -0.0069] | +0.0997 [+0.0967, +0.1026] |

The largest degradation is MV in S6 at `lambda = 0`, `B = 31`: -0.1313 (t 95% interval -0.1350 to -0.1276). In S4 and S6 at `lambda = 0` the MV loss grows with the budget over the tested range (S6: -0.0153 at `B = 3`, -0.0658 at `B = 9`, -0.1313 at `B = 31`). Correlation moves MV towards SINGLE at these budgets: in S4 at `B = 31`, MV is -0.0570 at `lambda = 0` and +0.0119 at `lambda = 0.5`. At `lambda = 0.75` and `B = 31`, MV is within 0.0021 of SINGLE in every scenario. Figure FIG-002-1 (EXP-002 report) shows all 24 scenario-by-`lambda` panels. Across the 432 non-baseline cells, the between-seed SD of `Delta` ranges from 0.0000 to 0.0162 (median 0.0087).

**P1 (supported in 6 of 6).** At `lambda = 0`, `B = 31`, every predicted gain (S1, S2, S3, S5) and every predicted loss (S4, S6) was observed with an interval excluding 0 (Table 1).

**P2 (disconfirmed in 9 of 30 cells).** SEQ was below MV, as predicted, in 21 cells: S1, S2, S3 and S5 at every budget and S4 at `B = 3`. Where MV degrades, the opposite held: `Delta_SEQ - Delta_MV` had an interval above 0 in S4 at `B >= 5` (up to +0.0572 [+0.0549, +0.0595] at `B = 31`) and in S6 at every budget (up to +0.1047 [+0.1021, +0.1073]). The preregistered prediction is reported as disconfirmed. SEQ moves less than MV in both directions; it still degrades in S6 (-0.0266 at `B = 31`, `lambda = 0`).

**P3 (supported in 43 of 45 comparisons).** In S1 to S3, `Delta_MV` decreased between consecutive `lambda` levels in 43 of 45 comparisons; 2 comparisons in S2 were inconclusive (-0.0016 [-0.0055, +0.0022] at `B = 3`, `lambda` 0 to 0.25; -0.0020 [-0.0056, +0.0017] at `B = 31`, `lambda` 0.5 to 0.75), and none increased.

**CW (descriptive).** CW is above SINGLE in all 120 CW cells with `B >= 3`, by up to +0.4478. Section 5.5 shows that this follows from the assumed confidence model.

### 5.3 EXP-003: dependence-structure sensitivity (frozen rule: H0 rejected)

At matched `p` and `r`, the exact sign of `Delta_MV = A_MV(n) - p` differs between models in 16 of 48 matched cells, all at `r >= 0.2`. The common-shock and Beta models are never negative in the grid (0 of 48 each); the Bahadur model is negative in 8 of 39 admissible cells (9 excluded as inadmissible) and the symmetric mixture in 14 of 48. For example, at `p = 0.7`, `r = 0.4`, `n = 5`, the Bahadur value is -0.07476 and the mixture value -0.03242, while common-shock and Beta are positive (Figure FIG-003-1 in the EXP-003 report; the 16 cells are listed in supplementary Table S3). The Monte Carlo check agreed in sign with every exact value; the exact value fell outside the seed-level interval in 3 of 183 model cells, all Beta.

The protocol registered in advance that the reading "MV degrades because of below-chance item mass; correlation alone only shrinks the gain" is invalidated if a homogeneous model with no below-chance item degrades at matched `p` and `r`. The Bahadur model does so. Conversely, the Beta model has below-chance mass at every tested `(p, r)` and never degrades. Below-chance mass is therefore neither necessary nor sufficient across models, and the EXP-002 degradation claims are restricted to the common-shock and two-class mixture families.

### 5.4 EXP-004: robustness to secondary choices (frozen rule: H0 retained)

No factor level reversed the sign of a Holm-significant EXP-002 cell in scope: 0 of 18 checks. The scope is narrow. Only 3 of the 32 significant EXP-002 cells lie within EXP-004's scenarios and `lambda` levels (S4, `lambda = 0`, MV at `B` 9, 15, 31), and MV accuracy does not depend on `tau` or `w` by construction, so 15 of the 18 checks could not have failed. The informative checks concern the tie rule: when a tie abstains and counts as wrong, the S4 degradation at even budgets becomes larger (at `B = 8`, -0.0402 against -0.0114 under the coin rule). The `primary` variant reproduced EXP-002 exactly, seed by seed.

Descriptively (outside the frozen rule), the sign of the mean `Delta` changed in 32 of 360 variant-versus-reference comparisons, mostly under "abstain counted as wrong" at small even budgets (S1, `B = 2`: -0.2382). Weaker herding (`w = 0.25`) made SEQ degrade in S4 at `lambda = 0` (-0.0340 [-0.0376, -0.0303] at `B = 31`), while stronger herding (`w = 0.9`) kept it near 0. Counting messages as cost, SEQ at 31 calls costs 496 units against 31 for MV, and in S1 at `lambda = 0` it is also less accurate (0.6621 against 0.8704).

### 5.5 Exploratory sensitivity analyses (M4, after all verdicts)

**Finite budget (J-0015).** Exact closed forms at `n` up to 301 show that the `lambda = 0` signs of S4 and S6 at `B = 31` are those of the large-`n` limit (S6: -0.12881 at `n = 31`, limit -0.15000). With correlation this need not hold: in S6 at `lambda = 0.25`, the exact value is -0.05215 at `n = 31` and -0.03311 at `n = 301`, but the limit is +0.02500. In S5 the limit is higher at `lambda = 0.25` (+0.24000) than at `lambda = 0` (+0.15000), because a correct shared answer can rescue below-chance items. The statements "the loss grows with `B`" and "correlation moves MV towards SINGLE" are therefore statements about `B <= 31`. The exact MV value lay inside the seed-level interval in 116 of 120 EXP-002 MV cells, and all 20 rejected MV cells have a negative exact value.

**Group sizes beyond EXP-003 (J-0015).** The Beta model stays above `p` up to `n = 1001` and in the limit for all 12 `(p, r)` pairs, while the symmetric mixture becomes negative at larger `n` even at `r = 0.05` (at `p = 0.55`: +0.05682 at `n = 31`, -0.04181 at `n = 301`). The confirmatory pattern "all disagreements at `r >= 0.2`" is thus specific to `n <= 15`.

**Confidence informativeness (J-0016).** With 10 exploratory seeds at `lambda = 0`, setting `delta = 0` (uninformative confidence) makes CW degrade like MV: at `B = 31`, -0.0529 [-0.0591, -0.0467] in S4 and -0.1197 [-0.1252, -0.1143] in S6. At `delta = 0.5` CW is above SINGLE in both (+0.0312 and +0.0554). CW's superiority in EXP-002 is a consequence of the assumed `delta = 1`, not evidence about confidence weighting in general.

## 6. Discussion

**What the evidence supports.** Within the common-shock and two-class mixture models, equal-budget majority voting is less accurate than a single call when a large share of items is answered correctly less than half the time, and the loss grows over the tested budgets. The sign follows the asymptotic condition of P1 in all six scenarios, and the magnitude follows the margin `h p_hard - (1 - h)(1 - p_easy)` (+0.06 in S4, +0.15 in S6). Mean competence cannot explain the sign, because S4 to S6 are matched on it and S5 gains. These MV results are consequences of closed forms; the experiment confirms them under a preregistered rule with paired uncertainty, and its value lies in the comparison with the rules that have no closed form.

**A disconfirmed prediction.** P2 assumed that herding always erodes the benefit of aggregation. It does where aggregation helps, but where MV degrades SEQ degrades less. A reading consistent with this is that herding makes the public tally follow a few early voters, so SEQ behaves like a smaller group and stays closer to SINGLE in both directions. The EXP-004 herding levels are consistent with this reading (weaker herding moves SEQ towards MV, including MV's degradation), but the mechanism was not tested and the evidence is descriptive.

**Competing explanations.** The EXP-002 protocol named four: below-chance item mass, correlation, herding, and finite-budget effects, plus the confidence model behind CW. EXP-003 shows that below-chance mass is not the general cause: at the same `p` and pairwise correlation, a model without below-chance items degrades and a model with them does not. What determines the sign is the full distribution of the number of correct votes, of which `p` and `r` are only two moments. Finite-budget effects matter once correlation is present (section 5.5). The confidence model fully determines whether CW looks good. SEQ order effects are averaged over seeds rather than separated, and the near-ceiling accuracy of MV in S3 (0.9999 at `B = 31`) limits contrasts there.

**Relation to prior work.** The S4 and S6 results are a controlled instance of the difficulty-diversity mechanism that Chen et al. propose for language-model voting [chen2024]; we do not test that mechanism on language models. The Bahadur results replicate the qualitative point of Kaniovski [kaniovski2008] that correlation can make a larger jury worse, and EXP-003 adds that matching correlation does not fix the sign across models.

**Practical significance.** In this model, whether to spend a budget on more votes depends on the structure of item difficulty and dependence, not on average accuracy or average pairwise correlation alone. That is a statement about a synthetic model; it is a reason to measure item-level difficulty and the distribution of agreement before assuming that more calls help, not evidence that they do not.

## 7. Limitations and threats to validity

- **Synthetic reasoners.** Reasoners are Bernoulli answerers with a parameterised confidence signal. They are not language models or people, and nothing here is a benchmark result for any real system (protocol section 9).
- **Model dependence.** The degradation claims hold for the common-shock and mixture families only (EXP-003). The Bahadur model is admissible only in part of the grid and sets higher-order correlations to zero.
- **Range.** Budgets are at most 31; with correlation, signs at `B = 31` can differ from the large-`B` limit (section 5.5). Parameter ranges are design choices, not estimates of any population.
- **Rules.** SEQ uses one herding rule; DELIB was dropped because it was degenerate as specified, so nothing follows about deliberation in general. CW depends entirely on the assumed confidence model (A-3 not adopted).
- **Statistics.** Cells share seeds (D-008), so counts of significant cells are not counts of independent findings; the P1 to P3 intervals are unadjusted; 30 seed-runs give approximate t intervals. Non-rejection is not evidence of no effect.
- **Robustness.** EXP-004 covered 3 of the 32 significant cells and none in S6; most of its checks were insensitive by construction.
- **Exposure.** Exploratory values of the primary contrast for S1 and S4 were seen before the freeze, with seeds distinct from the confirmatory ones (`research/freeze.json`).
- **Literature.** The literature pass was targeted; several foundational sources were not opened and are not cited; most sources were read at abstract level only.

The living list is `research/limitations.md`.

## 8. Ethics and responsible research

The study uses no human participants, no personal data and no external dataset. No ethics approval was sought or needed, and none is claimed. Results concern a stated mathematical model; they must not be presented as evidence about the behaviour of language models, committees, juries or products. Misuse risk is low; the main risk is overgeneralisation, which sections 6 and 7 address.

## 9. Conclusion and future work

In a preregistered equal-budget simulation, majority voting over more reasoners reduced accuracy relative to one call in the scenarios where theory predicted it, by up to 0.1313; sequential public voting lost less than majority voting there, contradicting our prediction; and at matched competence and pairwise correlation the direction of the majority effect depended on the dependence model. The bounded conclusion is that pairwise statistics do not decide whether aggregation helps. Feasible extensions, each needing a new, separately frozen protocol: characterising degradation through the distribution of the vote count; a robustness check covering S6; a confidence model calibrated to a stated target; a non-degenerate deliberation rule; and, separately, a test on locally run language models.

## 10. Data and code availability

All code, configurations, frozen protocols, raw outputs (except two regenerable EXP-004 files, D-012), analyses, figures and reports are in the project repository: `<repository URL: not yet published; release requires the owner's approval>`. Reproduction: `uv sync --frozen`, then `uv run paradox run --config research/experiments/EXP-00N/config.json --out results/EXP-00N/ --pdf` followed by `python -m paradox.analysis EXP-00N results/EXP-00N` (wrapped by `scripts/m3_run.sh`). The evidence audit is reproduced by `scripts/m4_recompute_checks.py` and `scripts/m4_number_trace.py`, and the exploratory checks by `scripts/m4_exploratory_analytic.py` and `scripts/m4_cw_delta_summary.py`. Each experiment folder has a `reproduction.md`.

## 11. Funding, competing interests and AI assistance

- **Funding:** none.
- **Competing interests:** none declared.
- **AI assistance:** an AI system (Claude, Anthropic) acted as a research and development assistant. It drafted protocols, wrote and tested code, executed the runs, drafted the reports and this manuscript, and performed the internal evidence audit and the second review pass. The owner set the research question, approved every amendment and the freeze, and made every recorded decision. Every number was checked by script against committed outputs (`research/publication/evidence_audit.md`). AI review is internal quality control, not peer review. These statements are subject to the owner's review before any release.

## References

- [chen2024] L. Chen, J. Q. Davis, B. Hanin, P. Bailis, I. Stoica, M. Zaharia, J. Zou. Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems. arXiv:2403.02419, 2024. https://arxiv.org/abs/2403.02419 (abstract page read).
- [du2023] Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, I. Mordatch. Improving Factuality and Reasoning in Language Models through Multiagent Debate. arXiv:2305.14325, 2023. https://arxiv.org/abs/2305.14325 (abstract page read).
- [golub2010] B. Golub, M. O. Jackson. Naive Learning in Social Networks and the Wisdom of Crowds. American Economic Journal: Microeconomics 2(1): 112-149, 2010. DOI 10.1257/mic.2.1.112 (abstract page read).
- [kaniovski2008] S. Kaniovski. Aggregation of Correlated Votes and Condorcet's Jury Theorem. Working paper, Austrian Institute of Economic Research (WIFO), dated 11 September 2008. https://Serguei.Kaniovski.wifo.ac.at/fileadmin/pdf/condorcet.pdf (full text, pages 1 to 13 read).
- [kim2025] E. Kim, A. Garg, K. Peng, N. Garg. Correlated Errors in Large Language Models. arXiv:2506.07962, 2025. https://arxiv.org/abs/2506.07962 (abstract page read).
- [li2024] J. Li, Q. Zhang, Y. Yu, Q. Fu, D. Ye. More Agents Is All You Need. arXiv:2402.05120, 2024. https://arxiv.org/abs/2402.05120 (abstract page read).
- [mavrodiev2012] P. Mavrodiev, C. J. Tessone, F. Schweitzer. Effects of Social Influence on the Wisdom of Crowds. arXiv:1204.3463, 2012. https://arxiv.org/abs/1204.3463 (abstract page read).
- [wang2022] X. Wang, J. Wei, D. Schuurmans, Q. Le, E. Chi, S. Narang, A. Chowdhery, D. Zhou. Self-Consistency Improves Chain of Thought Reasoning in Language Models. arXiv:2203.11171, 2022. https://arxiv.org/abs/2203.11171 (abstract page read).

All entries are in `research/paper/references.bib`, with access dates.

## Supplementary appendix

See [`supplementary.md`](supplementary.md): S1 experimental matrix and hashes; S2 all Holm-rejected EXP-002 cells and the P2 table; S3 the EXP-003 disagreement cells; S4 exploratory tables; S5 deviations, owner decisions and exploratory exposure; S6 report links.

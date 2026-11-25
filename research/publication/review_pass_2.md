<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Second review pass (master prompt section 11.5)

- **Date:** 2026-11-25 (M4).
- **Object:** `research/paper/manuscript.md` and `supplementary.md` as committed in `7b9b696` (draft v1), and the four experiment reports.
- **Reviewer:** the AI assistant (Claude, Anthropic), acting as an internal adversarial reviewer. This is internal quality control, not external peer review. The owner has not yet reviewed it.
- **Stance.** The pass argues against the preferred hypothesis ("equal-budget aggregation degrades accuracy where item difficulty is heterogeneous, and correlation damps the effect"). Each challenge is judged against committed evidence: it **holds** (the manuscript changes), **partly holds** (it is qualified) or **does not hold** (the reason is given).

## 1. Strongest alternative readings

| Id | Challenge | Evidence checked | Judgement | Change made |
|---|---|---|---|---|
| R1 | The primary rejection is close to guaranteed by design. S4 and S6 were chosen to satisfy the asymptotic degradation condition, and MV accuracy follows closed forms, so "H0 rejected" restates a theorem rather than discovering anything. | Protocol section 2.7 and 6.2 (P1 derived before any run); X1 exact values (J-0015): all 20 rejected MV cells have a negative exact value. | **Holds.** The MV part of the primary result is an analytic consequence confirmed under a preregistered rule. Only the SEQ cells (12 of 32) lack a closed form. | Abstract, section 1 contributions and section 6 now say that the MV degradation was predicted analytically and is confirmed, not discovered; the empirical content without a closed form is SEQ and the P2 disconfirmation. |
| R2 | P2 was disconfirmed for one specific SEQ rule (strict leader, `w = 0.5`, seeded order), not for herding in general. Reading it as a fact about information sharing overgeneralises. | Protocol section 2.5 (single rule); EXP-004 `w` levels (descriptive). | **Holds.** | Section 6 states that the P2 result is a property of this SEQ rule; the mechanism remains an untested reading. |
| R3 | Below-chance mass might still be the cause within the families actually used, and EXP-003's counter-examples might be artefacts of an inadmissible or exotic model (Bahadur). | EXP-003: Bahadur degrades in 8 of 39 admissible cells; the symmetric mixture coincides exactly with Bahadur at `n = 3` (verified algebraically in the EXP-003 report addendum); Beta has below-chance mass and never degrades. | **Partly holds.** Within the common-shock and mixture families the below-chance reading is consistent with every result; across models it fails. The Bahadur model is admissible only in part of the grid and sets higher-order correlations to zero. | Already restricted in v1. The wording "neither necessary nor sufficient" now says that "not sufficient" was shown for `n <= 15` (confirmatory) and extended to `n <= 1001` only exploratorily. |
| R4 | The degradation and the damping by correlation could be finite-budget artefacts of `B <= 31`. | X1 (J-0015): at `lambda = 0` the signs at `B = 31` equal the limit signs; at `lambda = 0.25` in S6 the limit is positive (+0.02500) while `B = 31` gives -0.05215; in S5 correlation raises the limit. | **Partly holds.** The `lambda = 0` degradation is not a finite-budget artefact; the role of correlation is budget-dependent. | Already in v1 section 5.5 and the EXP-002 addendum. Section 9 now limits the conclusion to `B <= 31` where correlation is involved. |
| R5 | CW's superiority might reflect a genuine advantage of confidence weighting. | J-0016: at `delta = 0` CW degrades like MV in S4 and S6. | **Does not hold** as an argument for CW; it supports the stated limitation. But the sweep is exploratory, uses 10 exploratory seeds and only `lambda = 0`. | v1 said CW's superiority "is a consequence" of `delta = 1`; softened to "is explained, in an exploratory check, by". |

## 2. Overgeneralisation and wording

| Id | Challenge | Judgement | Change made |
|---|---|---|---|
| R6 | Conclusion "pairwise statistics do not decide whether aggregation helps" is stated generally. | **Holds.** It was shown for four parametric models on one grid. | Restricted to "in the four dependence models studied". |
| R7 | The practical-significance paragraph advised what to measure in real systems. That is outside the claims boundary (protocol section 9). | **Holds.** | Advice removed; the paragraph now states only the within-model implication. |
| R8 | "The magnitude follows the margin" rests on two scenarios. | **Holds.** | Reworded: the loss is larger in S6, where the margin is larger; no trend claimed. |
| R9 | The abstract opens with "is often assumed to help", which is unsupported. | **Holds.** | Replaced by the Condorcet statement, which is supported. |
| R10 | 32 significant cells may suggest a large, widespread effect. The smallest rejected effect is -0.0036 (S6, `lambda = 0.75`, MV, `B = 3`; exact -0.00199). | **Partly holds.** v1 already said the cells form three connected patterns. | Section 5.2 adds that several rejected effects are below 0.01 in absolute value and practically small. |
| R11 | Title implies a general finding about reasoners. | **Partly holds.** | Subtitle now says "among synthetic reasoners". |
| R12 | Funding and competing-interest statements are asserted without the owner's confirmation. | **Holds.** | Marked "to be confirmed by the owner before any release". |
| R13 | Abstract length 255 words, above the 250-word limit of section 11.4. | **Holds.** | Shortened. |

## 3. Factual and evidence checks

| Id | Check | Result | Change made |
|---|---|---|---|
| R14 | v1 section 5.3 said the Monte Carlo check "agreed in sign with every exact value". | **Error.** The committed check has 160 intervals above 0, 22 below 0 and 1 that includes 0 (`results/EXP-003/analysis/analysis.json`, `mc_check`). | Corrected: every interval that excludes 0 agrees in sign; one includes 0. |
| R15 | Split of the 32 rejected cells. | The first EXP-002 report and CLM-002 said 24 MV and 8 SEQ; the raw outputs give 20 and 12 (found by `scripts/m4_recompute_checks.py`). | Fixed before v1 (report, register); recorded in D-014 and J-0017. |
| R16 | Stale figures. | Every figure in `research/experiments/EXP-00N/figures/` is byte-identical to the file generated in `results/EXP-00N/` (checked with `cmp`). | None needed. |
| R17 | Stale records. | The registry status said "standalone report pending"; `research/limitations.md` said "Standalone reports pending"; `results/README.md` said "Empty at M0"; the claims register said "audit pending (M4)". | All updated in this milestone. |
| R18 | Leakage. Could analysis choices have followed the data? | The frozen-rule analysis code (`d997cf8`) precedes the confirmatory results commit (`84b1d14`); the confirmatory seed entropy is refused for exploratory runs by the guard; pre-freeze exposure is limited to S1 and S4 with exploratory seeds and is disclosed. The M4 exploratory checks came after the verdicts and change none. | No change; disclosure kept in section 7 and supplementary S5. |
| R19 | Missing failed runs. | All four exit statuses are 0, with 0 failed and 0 dropped runs; every exploratory run is listed in supplementary S5, including the timing-only J-0007 run whose outcomes were not committed. | No change. |
| R20 | Unadjusted intervals and shared seeds can produce spurious "significant" cells. | X1 shows one: S6, `lambda = 0.75`, `B = 31`, interval -0.0040 to -0.0002 around an exact value of +0.00002 (not Holm-rejected, but reported as "wholly below 0" in the EXP-002 report). P1 to P3 rely on unadjusted intervals; their large effects are not at risk, the two inconclusive P3 steps are. | Section 5.5 already reports it; section 7 adds that unadjusted intervals produced at least one artefact. |
| R21 | The EXP-003 Beta signs were judged on the beta-binomial closed form, whereas the protocol text expected Monte Carlo for that model. | Reading D-011 (c), fixed before the run; the Monte Carlo interval agrees in sign wherever it excludes 0. | Disclosed in supplementary S5 (already in v1). |
| R22 | The number trace matches decimal tokens loosely at one or two decimals. | Such tokens are design parameters (for example 0.95, 0.4) or rounded values checked by hand; all tokens with three or more decimals match a committed value exactly at the stated precision. | Stated as an audit limitation in `evidence_audit.md`. |

## 4. What survives the challenge

- **Confirmed and bounded:** within the common-shock and two-class mixture models, MV at equal budget is less accurate than one call in S4 and S6, as derived analytically and confirmed under the frozen rule (largest -0.1313).
- **Empirical and surprising relative to the preregistration:** SEQ, as specified, loses less than MV where MV degrades (P2 disconfirmed in 9 of 30 cells).
- **Restricting result:** at matched `p` and `r`, the sign depends on the dependence model (16 of 48 cells).
- **Weak:** EXP-004's robustness check (3 of 32 cells, mostly insensitive by construction); CW (assumption-driven).

## 5. Changes recorded

The revised manuscript is committed after this file; the diff between `7b9b696` and the M4 records commit shows each change listed above (R1 to R14, R20). No number was added that is not in a committed result.

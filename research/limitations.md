<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Limitations (living document)

Status: revised in M4 (2026-11-25) after all four confirmatory experiments, the exploratory sensitivity checks J-0015 and J-0016 and the second review pass. The sections below the M3 and M4 sections were written at the freeze (2026-11-24) as limitations of the frozen design and still apply.

## Limitations shown by the confirmatory results (M3, 2026-11-25)

- **The degradation result is model-dependent (EXP-003).** At matched marginal competence and pairwise correlation, the sign of the majority-vote effect differs between dependence models in 16 of 48 matched cells. The Bahadur model degrades without any below-chance item (8 of 39 admissible cells), and the Beta difficulty model never degrades in the grid although it has below-chance items. The condition of protocol section 7 is met: EXP-002 claims about when aggregation degrades hold only for the common-shock and two-class mixture families, and pairwise correlation is not a sufficient summary (CLM-009).
- **P2 was disconfirmed (EXP-002).** Herding (SEQ) reduces the gain of aggregation only where aggregation helps; where MV degrades (S4, S6), SEQ loses less than MV. The proposed mechanism is not tested.
- **Shared seeds show up as correlated deviations.** In EXP-001, the S6 cells all deviate in the same direction from theory because they share one realised hard-item share (J-0011); counts of significant or deviating cells are not counts of independent findings.
- **EXP-004 checked only 3 Holm-significant EXP-002 cells** (S4, `lambda = 0`, MV, `B` 9, 15, 31), because its scenarios and `lambda` levels cover few of the 32 significant cells. Its "no reversal" result does not extend to S6. The tie rule "abstain counted as wrong" changes the sign of many small even-budget cells (descriptive), and `w = 0.25` makes SEQ degrade in S4 at `lambda = 0` (descriptive).
- **CW dominates every cell** (up to +0.4478 over SINGLE), as expected from the assumed confidence model; it carries no claim about aggregation.

## Limitations added in M4 (2026-11-25)

- **The MV degradation is analytic, not discovered.** Every Holm-rejected MV cell has a negative exact closed-form value (J-0015); EXP-002 confirms predictions derived before the runs. The empirical content without a closed form is SEQ (review pass R1).
- **Budget range.** With correlation, signs at `B = 31` need not hold at larger budgets: in S6 at `lambda = 0.25` the exact value is -0.05215 at `n = 31` but the large-`n` limit is +0.02500; in S5 correlation raises the limit (J-0015, exploratory). Claims about correlation damping the effect hold for `B <= 31`.
- **EXP-003 range.** The pattern "disagreements only at `r >= 0.2`" holds for `n <= 15`; at larger `n` the symmetric mixture degrades even at `r = 0.05` (J-0015, exploratory).
- **CW is assumption-driven.** With uninformative confidence (`delta = 0`) CW degrades like MV (J-0016, exploratory, 10 exploratory seeds).
- **P2 concerns one SEQ rule.** Its disconfirmation is not a statement about herding in general.
- **Unadjusted intervals can mislead.** In S6 at `lambda = 0.75`, `B = 31`, the unadjusted interval lies below 0 around an exact value of +0.00002 (shared-seed artefact).
- **EXP-004 is weak evidence.** 15 of its 18 frozen-rule checks could not fail by construction (MV does not depend on `tau` or `w`); it covers no S6 cell.
- **Audit by the drafting system.** The evidence audit and second review pass were performed by the AI assistant that drafted the documents. The owner approved the titles and the funding, competing-interest and AI-use statements on 2026-11-25 (D-015); full-text owner review of the manuscript, the audit and the review pass is pending (M6).

## Construct validity

- Reasoners are synthetic Bernoulli answerers with a parameterised confidence signal. They are not LLMs and not people. Nothing here is an LLM benchmark result.
- "Compute budget" is modelled as a count of reasoner calls. Real systems differ in per-call cost, context length and message cost; EXP-004 varies only one alternative accounting.
- Binary decisions only; K-ary answers can create plurality effects not studied here.
- The confidence model (protocol section 2.3) is an assumption; CW and calibration results depend on it. In the exploratory smoke run CW was far above MV in every cell, which reflects the private information the confidence signal carries at `delta = 1` rather than aggregation as such. A proposal to fix `delta` from a stated target was not adopted at the freeze; CW is reported as a secondary, descriptive rule.

## Internal validity

- MV outcomes in EXP-002 are largely predictable from closed forms. The simulation adds paired uncertainty and a reference for rules without closed forms, not independent evidence for MV.
- **DELIB is dropped (owner-approved amendment, 2026-11-24).** As specified in draft v0.1, only reasoners in the round-0 minority switch, and only towards the round-0 majority, so the round-1 majority always equals the round-0 majority: DELIB at `2n` calls equals MV at `n` calls on every item, for any herding strength `w` (pinned by `test_delib_as_drafted_always_equals_mv_of_round0`). It therefore could not answer its question and is not run. The study has one information-sharing rule (SEQ); conclusions about deliberation in general do not follow.
- SEQ results depend on the herding rule chosen; real information sharing is richer.

## External validity

- Parameter ranges (competence 0.55 to 0.95, correlation via `lambda` up to 0.75) are design choices, not estimates from any real population of reasoners.
- No external data calibrate the difficulty distribution (decision D-004).

## Statistical validity

- Seed-level intervals with 30 seeds are approximate; per-seed values are reported.
- Seeds are shared across cells (decision D-008), so cells are not independent; pooled analyses and the EXP-001 false-alarm estimate are approximate.
- Inadmissible Bahadur cells (EXP-001: 20 of 90; EXP-003: 9 of 48) are excluded and reported; the Bahadur comparison covers the admissible region only.
- Exploratory values of the primary contrast for S1 and S4 (`lambda` 0 and 0.5) were seen before the freeze, with exploratory seeds (`research/freeze.json`, disclosure C4).
- Many cells are tested; Holm adjustment controls the primary family only.

## Literature

- The literature pass was targeted, not systematic; several foundational sources are unverified (see `literature_review.md`).

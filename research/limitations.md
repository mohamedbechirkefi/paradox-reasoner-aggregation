<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Limitations (living document)

Status at the freeze (2026-11-24): no confirmatory experiment has run. These are limitations of the frozen design (protocol v1.0), to be revised with results.

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

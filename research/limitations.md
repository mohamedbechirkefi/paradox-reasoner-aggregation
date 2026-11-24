<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Limitations (living document)

Status at M0: no experiment has run. These are limitations of the planned design, to be revised with results.

## Construct validity

- Reasoners are synthetic Bernoulli answerers with a parameterised confidence signal. They are not LLMs and not people. Nothing here is an LLM benchmark result.
- "Compute budget" is modelled as a count of reasoner calls. Real systems differ in per-call cost, context length and message cost; EXP-004 varies only one alternative accounting.
- Binary decisions only; K-ary answers can create plurality effects not studied here.
- The confidence model (protocol section 2.3) is an assumption; CW and calibration results depend on it.

## Internal validity

- MV outcomes in EXP-002 are largely predictable from closed forms. The simulation adds paired uncertainty and a reference for rules without closed forms, not independent evidence for MV.
- DELIB receives one more call than its MV comparator (disclosed).
- SEQ results depend on the herding rule chosen; real information sharing is richer.

## External validity

- Parameter ranges (competence 0.55 to 0.95, correlation via `lambda` up to 0.75) are design choices, not estimates from any real population of reasoners.
- No external data calibrate the difficulty distribution (decision D-004).

## Statistical validity

- Seed-level intervals with 10 seeds are approximate; per-seed values are reported.
- Many cells are tested; Holm adjustment controls the primary family only.

## Literature

- The literature pass was targeted, not systematic; several foundational sources are unverified (see `literature_review.md`).

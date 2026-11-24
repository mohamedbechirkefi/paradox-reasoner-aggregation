<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# tests/

Run with `uv run paradox test` (or `uv run pytest`). Counts and outcomes of actual runs are recorded in `progress.md`, not here.

| File | Covers |
|---|---|
| `test_theory.py` | Golden fixtures (Condorcet, Kaniovski Bahadur, hand-enumerated common-shock), identities (perfect correlation, independent errors, symmetry), Theorem 1 against enumeration, beta-binomial against quadrature, matched-correlation maps, protocol P1 table, invalid inputs |
| `test_generator.py` | Seeded sampling (bit-identical reruns, distinct seeds, separated streams), marginal competence, conditional correlation `lambda^2`, perfect and zero correlation, invalid inputs |
| `test_rules.py` | Hand-computed examples, majority ties and the seeded coin, perfect correlation, independent errors and common-shock against theory, differential tests (SEQ with `w = 0`, DELIB with `w = 0`, CW with equal confidence, SEQ against a loop reference), budget accounting, DELIB degeneracy pin, invalid inputs |
| `test_metrics_stats.py` | Metric hand values and bounds, t quantiles against tables, Holm, bootstrap determinism, invalid inputs |
| `test_pipeline.py` | Config to results to report, schema fail-closed, deterministic rerun, confirmatory and exploratory guards, CLI exit codes, validation and dependence kinds, dependence samplers |

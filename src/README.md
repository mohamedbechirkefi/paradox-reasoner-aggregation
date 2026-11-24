<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# src/

Python package `paradox` (M2). Each concern is a separate module:

| Module | Role |
|---|---|
| `generator.py` | Scenarios, model parameters, seeded item pools and reasoner-draw tables (common random numbers, one RNG stream per component) |
| `rules.py` | Aggregation rules SINGLE (baseline), MV, CW, SEQ, DELIB, with budget and message accounting |
| `theory.py` | Closed forms: Condorcet, common-shock, two-class mixture, Bahadur (Kaniovski 2008, Theorem 1), beta-binomial; matched-correlation maps |
| `dependence.py` | Alternative dependence models for EXP-001 Bahadur cells and EXP-003 |
| `metrics.py` | Accuracy, Brier, ECE, disagreement, paired difference |
| `stats.py` | Seed-level t intervals, percentile bootstrap, Holm adjustment (no SciPy) |
| `schema.py` | Versioned JSON schemas (config and result, version 1.0.0), validated at export and import |
| `manifest.py` | Run manifest: config hash, seeds, git revision, versions, OS, CPU, runtime, peak memory |
| `runner.py` | Orchestration and guards (confirmatory runs refused while protocols are unfrozen) |
| `report.py` | Tables, figures and PDF (pandoc to Typst) from result files only |
| `cli.py` | `paradox smoke | run | report | test` |

<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX: collective reasoning under equal compute budgets

**Question.** Under equal compute budgets, when does aggregation of fallible reasoners improve or degrade accuracy?

**Status: M2 (core implementation), 2026-11-24.** The simulation engine, tests, schemas and report generator exist. No registered experiment has run and there are no findings. The protocol is a draft awaiting the owner's freeze; the only runs so far are exploratory smoke and probe runs in `results/exploratory/`, which are not results.

## Why it matters

Sampling several answers and voting, or letting several agents exchange answers, is a common way to spend extra compute on a reasoning task. Classical jury theorems say majorities beat individuals only under conditions (competence above one half, independence); correlated errors and hard items can reverse the effect. PARADOX tests these conditions at matched call budgets with deterministic, seeded synthetic reasoners. Synthetic reasoners are not LLMs; no LLM claim will be made.

## What is implemented

A Python package `paradox` (`src/paradox/`): seeded synthetic reasoners with a common-shock correlation model, the rules SINGLE (baseline), MV, CW, SEQ and DELIB, closed-form theoretical baselines, a versioned JSON result schema, run manifests, an experiment runner that refuses confirmatory runs before the protocol freeze, and a report generator (Markdown, figures, PDF through pandoc and Typst). Planned: the frozen experiments (M3) and a static offline demo (M5).

## Registered experiments

| Id | Title | Status |
|---|---|---|
| EXP-001 | Engine and theoretical-baseline validation | planned (protocol draft, awaiting owner freeze); exploratory design probe run, see `results/exploratory/probe-engine-validation` |
| EXP-002 | Equal-budget aggregation map (primary) | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Dependence-structure sensitivity | planned (protocol draft, awaiting owner freeze) |
| EXP-004 | Robustness to secondary design choices (optional) | planned (protocol draft, awaiting owner freeze) |

## Navigation

- Plan and status: [`roadmap.md`](roadmap.md), [`progress.md`](progress.md)
- Protocol (draft): [`research/protocol.md`](research/protocol.md); feasibility: [`research/feasibility.md`](research/feasibility.md)
- Literature: [`research/literature_review.md`](research/literature_review.md); limitations: [`research/limitations.md`](research/limitations.md)
- Registry: [`research/experiment_registry.csv`](research/experiment_registry.csv); claims: [`research/claims_register.csv`](research/claims_register.csv) (empty)
- Manuscript skeleton: [`research/paper/manuscript.md`](research/paper/manuscript.md)

## Quick start (development environment)

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
```

```
uv run paradox test            # full test suite
uv run paradox smoke --pdf     # exploratory smoke matrix -> results/exploratory/smoke/
uv run paradox run --config <config.json> --out <dir> [--pdf]
uv run paradox report <dir> [--pdf]
```

## Data

No external dataset. All data are synthetic and regenerated from recorded parameters and seeds. See [`data/manifest.json`](data/manifest.json).

## Licence

Source-available, non-commercial research licence: PARADOX Source-Available Non-Commercial Research License v1.0 (`LicenseRef-PARADOX-NC-Research-1.0`). It is not an OSI-approved open-source licence. See [`LICENSE`](LICENSE), [`NOTICE.md`](NOTICE.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citation

See [`CITATION.cff`](CITATION.cff).

<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX: collective reasoning under equal compute budgets

**Question.** Under an equal compute budget, when does aggregation of fallible reasoners improve or degrade accuracy?

**Status (2026-11-25): independent research manuscript / preprint draft, not peer-reviewed.** The four registered experiments (EXP-001 to EXP-004) ran in full under protocols frozen by the owner on 2026-11-24; each has a standalone report, and the manuscript, evidence audit and second review pass are complete (M4). The interactive demo is built (M5). The owner approved the titles and the funding, competing-interest and AI-use statements on 2026-11-25; a release candidate was prepared on 2026-11-25 (M6: PDFs compiled and inspected, clean-clone reproduction recorded in [`research/publication/reproducibility_report.md`](research/publication/reproducibility_report.md)); full-text owner review is pending. Nothing has been published.

Repository: `<repository URL: not yet published; release requires the owner's approval>`. Demo: `<demo URL: not yet published; release requires the owner's approval>`.

## Why it matters

Sampling several answers and voting, or letting several agents see each other's answers, is a common way to spend extra compute on a reasoning task. Classical jury theorems say a majority beats one reasoner only under conditions (competence above one half, independent errors); correlated errors and items that most reasoners get wrong can reverse the effect. PARADOX tests these conditions at matched call budgets with deterministic, seeded synthetic reasoners. Synthetic reasoners are not language models or people; nothing here is a result about either.

![The demo's accuracy and cost curves for scenario S6 at lambda 0: majority voting falls further below a single call as the budget grows to 31 calls, sequential voting falls less, and confidence-weighted voting rises; circled points are Holm-rejected cells and vertical bars are seed-level t 95% intervals.](docs/demo.png)

*Figure: the demo page's accuracy and cost curves (EXP-002, scenario S6, lambda 0). Each point is the change in accuracy against one reasoner making one call, with its seed-level t 95% interval; circled points are cells where degradation was detected under the frozen rule. CW is descriptive.*

## Key findings (verified; see the manuscript for scope)

Every number below is printed in [`research/paper/manuscript.md`](research/paper/manuscript.md) and traced to committed results.

- **Engine validation (EXP-001, PASS).** Simulated majority accuracy matched four closed forms in all 292 admissible cells (largest deviation 3.116 Monte Carlo standard errors against a tolerance of 4).
- **Degradation at equal budget (EXP-002, H0 rejected).** 32 of 240 MV and SEQ cells were rejected after Holm adjustment (20 MV, 12 SEQ), all in the two scenarios with substantial below-chance item mass (S4, S6), where closed forms predicted it. The largest loss was MV in S6 at `lambda = 0` and `B = 31`: -0.1313 accuracy (t 95% interval -0.1350 to -0.1276). These MV results confirm closed-form predictions; they are not new discoveries.
- **A disconfirmed prediction (P2).** Sequential public voting was predicted to be below MV; where MV degrades it lost less than MV (up to +0.1047 [+0.1021, +0.1073] in S6), though it still degraded in S6 (-0.0266 at `B = 31`). This concerns one sequential rule.
- **Model dependence (EXP-003, H0 rejected).** At matched competence and pairwise correlation, the sign of the majority effect differs between dependence models in 16 of 48 matched cells, so the degradation result holds only for the common-shock and two-class mixture families.
- **Robustness (EXP-004, optional, H0 retained).** 0 of 18 checks reversed a sign, but only 3 of the 32 significant cells were in scope and 15 of the 18 checks could not have failed.
- **CW is assumption-driven.** Confidence-weighted voting was above SINGLE in every cell; an exploratory check shows this follows from the assumed confidence model.

Limitations: [`research/limitations.md`](research/limitations.md) and manuscript section 7.

## Registered experiments

| Id | Title | Status | Verdict under the frozen rule | Report |
|---|---|---|---|---|
| EXP-001 | Engine and theoretical-baseline validation | confirmatory, complete | PASS | [report](research/experiments/EXP-001/report.md) |
| EXP-002 | Equal-budget aggregation map (primary) | confirmatory, complete | H0 rejected; P1 and P3 not disconfirmed, P2 disconfirmed | [report](research/experiments/EXP-002/report.md) |
| EXP-003 | Dependence-structure sensitivity | confirmatory, complete | H0 rejected (16 of 48 cells) | [report](research/experiments/EXP-003/report.md) |
| EXP-004 | Robustness to secondary design choices (optional) | confirmatory, complete | H0 retained (narrow scope) | [report](research/experiments/EXP-004/report.md) |

Exploratory checks made after the verdicts (journal J-0015, J-0016) are in `results/exploratory/` and change no verdict.

## What is implemented

- A Python package `paradox` (`src/paradox/`): seeded synthetic reasoners with a common-shock correlation model and a two-class difficulty mixture; the rules SINGLE (baseline), MV, CW and SEQ (DELIB is implemented but was dropped at the freeze because, as specified, it equals MV at half its calls); closed-form theoretical baselines and three further dependence models; a versioned JSON result schema; run manifests; a runner that refuses a confirmatory config unless it matches the freeze record; and a report generator.
- A static, offline demo (`demo/`, TypeScript, React and Vite): the published results with intervals, the EXP-002 accuracy and cost curves, and a seeded sandbox with a reasoning-network view. The sandbox runs a browser port of the engine (SINGLE, MV, SEQ) that reproduces the Python engine's draws and decisions exactly; a unit test checks this against a fixture from the Python engine and against one committed EXP-002 seed-run. CW is not ported. The page collects no visitor data and makes no request to any other host.

## Demo quick start

Node 22 is required (in the development workspace, a shared Node 22 install outside this repository, used read-only).

```
cd demo && npm ci && npm run build && npm run preview
```

`npm test` runs the vitest suite; `node tools/a11y_check.mjs dist` runs the offline and accessibility check (headless Chrome). The page reads only `demo/public/data/results.json`, which `scripts/export_demo_data.py` writes from committed results; it fails closed on malformed data.

## Reproduction

```
uv sync --frozen                                      # locked dependencies (uv.lock)
uv run paradox test                                   # full Python test suite
scripts/m3_run.sh EXP-001                             # one frozen experiment (likewise EXP-002 to EXP-004)
uv run python scripts/export_demo_data.py --check     # demo data matches committed results
uv run python scripts/export_sandbox_fixture.py --check
```

Each experiment folder has a `reproduction.md`. The evidence audit is reproduced by `scripts/m4_recompute_checks.py` and `scripts/m4_number_trace.py`.

## Navigation

- Manuscript: [`research/paper/manuscript.md`](research/paper/manuscript.md) ([PDF](research/paper/manuscript.pdf)); supplementary: [`research/paper/supplementary.md`](research/paper/supplementary.md) ([PDF](research/paper/supplementary.pdf)); each experiment folder has `report.md` and `report.pdf`
- Protocol (frozen v1.0): [`research/protocol.md`](research/protocol.md); freeze record: [`research/freeze.json`](research/freeze.json)
- Registry: [`research/experiment_registry.csv`](research/experiment_registry.csv); claims: [`research/claims_register.csv`](research/claims_register.csv); evidence audit: [`research/publication/evidence_audit.md`](research/publication/evidence_audit.md)
- Plan and status: [`roadmap.md`](roadmap.md), [`progress.md`](progress.md); decisions: [`research/decision_log.md`](research/decision_log.md)
- Articles (drafts, unpublished): [`articles/medium.md`](articles/medium.md), [`articles/linkedin.md`](articles/linkedin.md)

## Architecture

`src/paradox/`: generator (items and the reasoner-draw table), rules, theory (closed forms), dependence, metrics, stats, schema, manifest, runner, analysis, report, cli. `research/`: protocols, registry, claims, reports, manuscript and publication records. `results/`: committed confirmatory and exploratory outputs with SHA-256 manifests. `demo/`: static page, Web Worker sandbox and checks.

## Data

No external dataset. All data are synthetic and regenerated from recorded parameters and seeds. See [`data/manifest.json`](data/manifest.json).

## Licence

Source-available, non-commercial research licence: PARADOX Source-Available Non-Commercial Research License v1.0 (`LicenseRef-PARADOX-NC-Research-1.0`). It is not an OSI-approved open-source licence. See [`LICENSE`](LICENSE), [`NOTICE.md`](NOTICE.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citation

See [`CITATION.cff`](CITATION.cff). Not peer-reviewed.

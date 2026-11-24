<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Roadmap

Milestones from master prompt section 5 with the section 11.6 additions. Effort is a planning estimate in focused days (five-day target). Status values: not started, in progress, done (all acceptance criteria checked), blocked.

| Id | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 | done (this session; owner review pending) | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 | in progress (drafts written; freeze pending) | owner freeze (G-FREEZE); owner decisions O-1 to O-6 |
| M2 | Core implementation | M1 drafts (implementation may start before freeze; exploratory only) | P0 | 1 | in progress (engine, tests, schemas, manifests, CLI, reports done; open items below) | owner decisions on amendments A-1 to A-5 |
| M3 | Experiments | M1 freeze, M2 | P0 | 0.75 | not started | owner freeze |
| M4 | Interpretation | M3 | P0 | 0.75 | not started | none |
| M5 | Interactive experience | M3 results (demo shell can start in M2) | P1 | 0.75 | not started | none |
| M6 | Release candidate | M4, M5 | P0 | 0.75 | not started | owner approval for any publication (G-PUBLIC) |

## M0: Bootstrap and feasibility

Acceptance criteria:

- [x] Control files of master prompt section 2 exist (CLAUDE.md, roadmap.md, progress.md, research files, data manifest, folders, README, CITATION.cff, lockfile).
- [x] Feasibility audit with commands and outputs (`research/feasibility.md`).
- [x] Source audit with verified and unverified sources separated (`research/literature_review.md`); dataset licences recorded (`data/manifest.json`).
- [x] Budget (zero cost), explicit scope, exclusions and fallback stated.
- [x] Section 11.1 tree initialised: registry, manuscript skeleton, publication checklists.
- [x] Zero-cost local publication toolchain confirmed with an exploratory smoke check (D-002).
- [ ] Gate: the owner confirms they understand the question, cost and exclusions (owner action).

## M1: Research and preregistration

Additions (11.6): initialise registry, manuscript skeleton and experiment-specific protocols; freeze confirmatory protocols before execution.

Acceptance criteria:

- [x] Draft protocol with H0/H1, baseline, one primary metric, secondary metrics, unit, seeds, sample-size rationale, uncertainty, exclusion and stopping rules, smoke and full matrices, invalidating sensitivity analysis.
- [x] EXP-001 to EXP-004 registered with draft protocols following 11.2.
- [ ] Unverified foundational sources (Boland 1989, Ladha 1992, Lorenz et al. 2011) opened or recorded as permanently unverified.
- [ ] Owner decisions O-1 to O-6 taken (see `progress.md`).
- [x] Smoke run (exploratory, after M2) measures between-seed SD (J-0006). [ ] Seed count confirmed by the owner (amendment A-1).
- [ ] Owner freezes each protocol; version and SHA-256 recorded in the registry and decision log.
- [x] Golden values committed with tests (`tests/test_theory.py`, sources in J-0002 and the test comments).

## M2: Core implementation

Additions (11.6): versioned output schemas, reproducibility manifests and report generators alongside the core.

Acceptance criteria:

- [x] Package `src/paradox`: generator, rules (SINGLE first, then MV, CW, SEQ, DELIB), closed-form theory, dependence models, metrics, statistics, runner, JSON schema 1.0.0, manifest writer, report generator; CLI commands smoke, run, report, test (2026-11-24). The planned `analyse` step is part of `run` (seed-level summaries in `results.json`) and `report`.
- [x] Tests actually run: majority ties, perfect correlation, independent errors, budget accounting, seeded sampling, Kaniovski golden fixtures, symmetry and bound invariants, invalid inputs, differential tests, integration from config to results. 302 passed, 0 failed (`progress.md`, J-0003).
- [x] Run manifests record runtime, peak memory, OS, CPU, package versions, git revision and config hash.
- [x] Deterministic rerun check (`test_rerun_is_deterministic`; same seed gives bit-identical draws).
- [x] `paradox run` refuses confirmatory configs while protocols are unfrozen (D-007; tested).
- [x] Exploratory smoke run and probes, labelled exploratory, in `results/exploratory/` (J-0004 to J-0007).
- [ ] DELIB rule redefined or dropped (amendment A-2): as drafted it is identical to MV at half the budget.
- [ ] EXP-004 tie-rule level "abstain counted as wrong" implemented (not done; EXP-004 is optional, O-5).
- [ ] Per-experiment `config.json` files written at freeze, with the owner's seed count (A-1).

## M3: Experiments

Additions (11.6): individual reports as experiments finish; all unsuccessful experiments and deviations recorded; provenance captured during runs.

Acceptance criteria:

- [ ] Smoke matrix run (exploratory, labelled).
- [ ] EXP-001 passes before EXP-002 to EXP-004 start (stop rule).
- [ ] Frozen matrices run in full, or failures documented; no silently dropped runs.
- [ ] Raw machine-readable results, plots with uncertainty, per-experiment report drafts.

## M4: Interpretation

Additions (11.6): finish reports and evidence audit; synthesise into the manuscript, including contradictory results and sensitivity analysis.

Acceptance criteria:

- [ ] Confounders and EXP-003 sensitivity examined; expected versus observed compared.
- [ ] Claims register filled; every numeric claim maps to result id, config and figure.
- [ ] Second review pass challenges the preferred hypothesis.
- [ ] Manuscript draft complete; limitations updated.

## M5: Interactive experience

Additions (11.6): demo, paper, reports and articles use identical verified results, labels and scope.

Acceptance criteria:

- [ ] Static page: reasoning network, error propagation, accuracy/cost curves, seeded sandbox; measured versus sandbox results visibly distinguished.
- [ ] Offline after load, keyboard usable, reduced motion, mobile layout, fail-closed data loading, accessibility checks recorded.

## M6: Release candidate

Additions (11.6): compile and inspect PDFs; verify references, cross-links, equations, figures, metadata; clean-clone smoke reproduction; owner review checklist.

Acceptance criteria:

- [ ] Clean clone, `uv sync --frozen`, tests, smoke reproduction, demo build: actual outputs recorded.
- [ ] Manuscript and report PDFs compiled (Typst path) and visually inspected.
- [ ] Data manifest, links, secrets and licences scanned.
- [ ] Publication gate of 11.6 satisfied; owner approves any publication.

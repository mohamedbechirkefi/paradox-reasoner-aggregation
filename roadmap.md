<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Roadmap

Milestones from master prompt section 5 with the section 11.6 additions. Effort is a planning estimate in focused days (five-day target). Status values: not started, in progress, done (all acceptance criteria checked), blocked.

| Id | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 | done (this session; owner review pending) | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 | done; M1 gate passed (protocols frozen at v1.0, owner-approved 2026-11-24) | none (foundational sources still unverified, see below) |
| M2 | Core implementation | M1 drafts (implementation may start before freeze; exploratory only) | P0 | 1 | done (amendments applied, EXP-004 tie rule and variants, confirmatory configs, freeze guard) | none |
| M3 | Experiments | M1 freeze, M2 | P0 | 0.75 | done (2026-11-25): all four frozen matrices complete; reports written by the coordinator from committed results (D-013) | none |
| M4 | Interpretation | M3 | P0 | 0.75 | done (2026-11-25): confounders and sensitivity examined, evidence audit, manuscript and second review pass (D-014); owner review pending | none |
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
- [x] Owner decisions taken at the freeze (2026-11-24): 30 seeds, DELIB dropped, EXP-004 optional, Bahadur exclusions, commands and shared seeds, exposure disclosure (D-009). A-3 not approved; confidence model unchanged.
- [x] Smoke run (exploratory, after M2) measures between-seed SD (J-0006). [x] Seed count confirmed by the owner: 30 (amendment 1).
- [x] Owner freezes each protocol; version 1.0 and SHA-256 recorded in the registry, `research/freeze.json` and the decision log (D-009).
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
- [x] DELIB dropped from the confirmatory design (amendment 2); reason in `research/limitations.md`.
- [x] EXP-004 tie-rule level "abstain counted as wrong" implemented and tested (D-010).
- [x] Per-experiment `config.json` files written at freeze, with 30 seeds; hashes in `research/freeze.json`.

## M3: Experiments

Additions (11.6): individual reports as experiments finish; all unsuccessful experiments and deviations recorded; provenance captured during runs.

Acceptance criteria:

- [x] Smoke matrix run (exploratory, labelled): `results/exploratory/m3-smoke/`, 32 of 32 metric checks (J-0009).
- [x] EXP-001 passes before EXP-002 to EXP-004 start (stop rule): PASS, 292 cells, 0 failing (J-0010).
- [x] Frozen matrices run in full, or failures documented; no silently dropped runs: EXP-001 292 + 20 excluded cells, EXP-002 720 runs, EXP-003 183 + 9 excluded cells, EXP-004 1440 runs; 0 failures (J-0010 to J-0014).
- [x] Raw machine-readable results with SHA-256 manifests and provenance tables, plots with uncertainty (`results/EXP-00N/`).
- [ ] Per-experiment 11.3 report drafts (`research/experiments/EXP-NNN/report.md`): not written in the M3 session (D-012).

## M4: Interpretation

Additions (11.6): finish reports and evidence audit; synthesise into the manuscript, including contradictory results and sensitivity analysis.

Acceptance criteria:

- [x] Confounders and EXP-003 sensitivity examined; expected versus observed compared.
- [x] Claims register filled; every numeric claim maps to result id, config and figure.
- [x] Second review pass challenges the preferred hypothesis.
- [x] Manuscript draft complete; limitations updated.

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

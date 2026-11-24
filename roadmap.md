<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Roadmap

Milestones from master prompt section 5 with the section 11.6 additions. Effort is a planning estimate in focused days (five-day target). Status values: not started, in progress, done (all acceptance criteria checked), blocked.

| Id | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 | done (this session; owner review pending) | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 | in progress (drafts written; freeze pending) | owner freeze (G-FREEZE); owner decisions O-1 to O-6 |
| M2 | Core implementation | M1 drafts (implementation may start before freeze; exploratory only) | P0 | 1 | not started | none |
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
- [ ] Smoke run (exploratory, after M2) measures between-seed SD; seed count confirmed.
- [ ] Owner freezes each protocol; version and SHA-256 recorded in the registry and decision log.
- [ ] Fixture manifest for golden values committed with tests.

## M2: Core implementation

Additions (11.6): versioned output schemas, reproducibility manifests and report generators alongside the core.

Acceptance criteria:

- [ ] Package `src/paradox`: generator, rules (SINGLE first, then MV, CW, SEQ, DELIB), closed-form theory, metrics, runner, JSON schema, manifest writer, report generator; CLI commands smoke, run, analyse, report, test.
- [ ] Tests actually run: majority ties, perfect correlation, independent errors, budget accounting, seeded sampling, Kaniovski golden fixtures, symmetry and bound invariants, invalid inputs, integration from config to results.
- [ ] Run manifests record runtime, peak memory, OS, CPU, package versions, git revision and config hash.
- [ ] Deterministic rerun check.

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

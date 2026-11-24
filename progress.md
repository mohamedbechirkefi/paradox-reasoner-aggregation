<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Progress journal

Append-only, dated. Each entry: milestone, decisions, commands and actual outputs, failures, changed files, risks, next action.

## 2026-11-24: M0 session (bootstrap, feasibility, M1 drafts)

**Milestone:** M0 done pending the owner's gate check; M1 drafts written, freeze pending.

### Starting state

`git status`: on branch `main`, "nothing to commit, working tree clean". One commit, `4b2652c` (master prompt and the owner's licence package). `master_prompt.md` was already saved unchanged and was not edited.

### Commands and actual outputs

| Command | Output |
|---|---|
| `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize` | Apple M1 Pro / 10 / 17179869184 |
| `sw_vers` | macOS 15.3.1, build 24D70 |
| `df -h /Users/bechir/research` | 460Gi size, 311Gi used, 129Gi available, 71% |
| `/usr/local/bin/python3 --version` | Python 3.12.1 |
| `.tools/py/bin/uv --version` | uv 0.9.5 (d5f39331a 2025-10-21) |
| `.tools/py/bin/typst --version` | no such file (typst is available as a Python package only) |
| `.tools/py/bin/python -c "import typst, pypdf, PIL ..."` | typst 0.15.0, pypdf 6.20.0, pillow 11.3.0 |
| `.tools/pandoc --version` | pandoc 3.6.3 |
| `helix/.tools/node/bin/node --version` (read-only) | v22.23.3 |
| `git --version` | git version 2.42.1 |
| `which tex pdflatex xelatex` | not found (all three) |

Exploratory toolchain smoke check (scratch directory outside the repository; journal entry J-0001): pandoc to Typst then `typst.compile` failed with `typst.TypstError: font fallback list must not be empty`; with `-V mainfont="Libertinus Serif"` it produced a 1-page PDF whose extracted text was correct. Pandoc to `.tex` succeeded (not compiled: no TeX).

Golden fixture recomputation (journal entry J-0002): Condorcet `M_3(0.55) = 0.57475`, `M_5(0.55) = 0.5931269`; Kaniovski Bahadur `M^B_3(0.55, 0.4) = 0.54505`, `M^B_5(0.55, 0.4) = 0.5196194`.

Lockfile: `.tools/py/bin/uv lock --python /usr/local/bin/python3` printed "Using CPython 3.12.1 interpreter at: /usr/local/bin/python3" and "Resolved 25 packages in 9ms", exit 0. `uv.lock` records `exclude-newer = 2026-11-10T00:00:00Z`. Resolved direct dependencies: numpy 2.5.4, matplotlib 3.11.2, jsonschema 4.26.0, pytest 9.2.0, hypothesis 6.170.15. The newest upload time of any locked artifact is 2026-11-06 (hypothesis), before the two-week cutoff. `uv sync` was not run; no virtual environment exists yet.

Literature and data: web searches and page fetches on 2026-11-24. Opened: arXiv abstract pages 2403.02419, 2506.07962, 2203.11171, 2305.14325, 2402.05120, 1204.3463; AEA page for Golub and Jackson (2010); the Kaniovski (2008) working-paper PDF (full text, pages 1 to 13 read, SHA-256 recorded); Wikipedia "Jury theorem"; Hugging Face pages for two candidate datasets (metadata only). Failed: PNAS (HTTP 403), PubMed and PMC (cookie or browser checks), Springer (login redirect). Nothing was downloaded into the repository.

Text checks before commit: `grep` for em dashes in new files found none; `grep` for e-mail addresses found only the Anthropic co-author trailer address in CLAUDE.md.

No test suite exists yet; no tests were run. No experiment was run.

### Decisions

D-001 (licence, owner), D-002 (Typst toolchain), D-003 (model proposal), D-004 (no external data), D-005 (exclude-newer). See `research/decision_log.md`.

### Changed files

Created: `CLAUDE.md`, `roadmap.md`, `progress.md`, `README.md`, `CITATION.cff`, `pyproject.toml`, `uv.lock`, `data/manifest.json`, READMEs in `results/ src/ tests/ experiments/ demo/ articles/ research/paper/figures/`, `research/{protocol.md, feasibility.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv, experiment_journal.jsonl, experiment_registry.csv}`, `research/experiments/EXP-00{1..4}/protocol.md`, `research/paper/{manuscript.md, references.bib}`, `research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}`. Modified: `CONTRIBUTING.md` (development commands appended). Licence files unchanged.

### Decisions the owner must make

- **O-1.** Approve or amend the operationalisation: primary metric accuracy, baseline SINGLE (one call), H0 "no cell degrades" for MV and SEQ, predictions P1 to P3.
- **O-2.** Approve the full matrix (scenarios S1 to S6, `lambda` in {0, 0.25, 0.5, 0.75}, `B` up to 31), 10 seeds and 2000 items per run.
- **O-3.** Accept the DELIB budget convention (compared with MV at `B - 1`, one-call advantage disclosed) or choose another.
- **O-4.** Approve or replace the confidence model (protocol section 2.3), which drives CW and calibration.
- **O-5.** Keep EXP-004 or cut it now to protect the five-day target.
- **O-6.** Confirm that no external dataset and no local LLM extension are in scope.
- **Freeze.** Freeze EXP-001 to EXP-004 protocols (G-FREEZE) after any amendments.

### Risks

MV outcomes are largely predictable from closed forms (stated in limitations); the confidence model is ad hoc; several foundational sources are unverified; no TeX (Typst path instead).

### Next action

M2: implement the engine (SINGLE and MV first), closed-form theory and tests, schemas and manifests; then the exploratory smoke matrix to measure between-seed SD, while the owner reviews the protocol.

## 2026-11-24: M2 session (core implementation while the freeze is pending)

**Milestone:** M2 in progress: engine, tests, schemas, manifests, CLI and report generator done; DELIB redefinition (A-2) and the EXP-004 abstain tie level remain. M1 freeze still pending (G-FREEZE). No confirmatory run. Nothing pushed.

### Starting state

`git status`: on `main`, clean; HEAD `743bf42`. Control files read in the order of the M2 brief.

### What was implemented (`src/paradox/`)

Reference baseline first (SINGLE, MV, closed-form theory), then CW, SEQ, DELIB and the EXP-003 dependence models. Modules are separated by concern (generator, rules, theory, dependence, metrics, stats, schema, manifest, runner, report, cli); see `src/README.md`. Result schema version 1.0.0 is validated at export and at import (fail closed). Each run writes `results.json`, `metrics.csv` and `run_manifest.json` (config SHA-256, seeds, git revision, versions, OS, CPU, runtime, per-run runtime, peak RSS). `paradox run` refuses confirmatory configs while protocols are unfrozen (D-007). Decisions D-006 to D-008 are in `research/decision_log.md`.

### Commands and actual outputs

| Command | Output |
|---|---|
| `uv add --group report "typst>=0.13"`; `uv sync` | typst 0.15.2 installed (upload 2026-11-05); paradox 0.1.0 built with uv_build |
| `uv run pytest -q` (during development) | first full run: 1 failed, 46 passed with `-x` (constant-sample p-value 4.8e-33 instead of 0); fixed with a relative tolerance |
| `uv run pytest -q` (before commit 1) | `302 passed in 11.47s` |
| `uv run paradox test -q` (after the CLI pass-through fix) | `302 passed in 10.40s` |
| `uv run paradox smoke --pdf` | 8 runs, 0 excluded; 0.16 s; peak RSS 39.5 MiB; `report.pdf` 4 pages |
| `uv run paradox run --config configs/exploratory/probe_engine_validation.json --out results/exploratory/probe-engine-validation --pdf` | 4 golden fixtures pass; 292 cells, 20 excluded (inadmissible Bahadur), 0 outside 4 SE, max abs z 2.427; 40.12 s; peak RSS 519.5 MiB; 13-page PDF |
| `uv run paradox run --config configs/exploratory/probe_seed_spread.json --out results/exploratory/probe-seed-spread --pdf` | 40 runs, 0 excluded; 2.47 s total; mean 0.051 s per run; peak RSS 88.0 MiB; 7-page PDF |

The committed exploratory outputs were regenerated on a clean tree at revision `9bfb9d3`, so their manifests carry an exact revision. Earlier dirty-tree runs of the same code took 0.09 s (smoke), 12.74 s (engine probe) and 0.73 s (seed probe); the timing spread reflects other sessions sharing the machine. PDFs were checked with pypdf (page counts, EXPLORATORY banner on page 1) and pages were rendered to PNG and looked at. The first PDF build had a long table running off the page because pandoc wraps tables in figures that cannot break; the build now adds `#show figure: set block(breakable: true)`.

### Exploratory measurements for the owner (not findings)

- **Runtime per run** (2000 items, all rules, all budgets): 0.013 to 0.051 s on average, depending on machine load.
- **Projected full matrices:** EXP-001 design 13 to 40 s (measured); EXP-002, 240 runs: about 3 to 12 s of simulation plus summaries, under one minute; EXP-003 draft grid 30.3 s (J-0007, timing only, values not inspected); EXP-004 about 660 runs, under one minute (projection).
- **Seed spread:** between-seed SD of the paired Delta in MV and SEQ cells with budget above 1 ranges from 0.0065 to 0.0179 (S1, S4; lambda 0, 0.5). At 10 seeds the largest gives a t 95% half-width of 0.0128, above the protocol's 0.01 rule (section 5).
- **Degenerate cases:** DELIB equals MV at half its budget on every item (A-2); CW results are driven by the draft confidence model (A-3); 20 of 90 EXP-001 Bahadur cells and 9 of 48 EXP-003 Bahadur cells are inadmissible (A-4); budget-1 cells have zero-width intervals by construction (MV, CW and SEQ at one call are SINGLE).

**Exposure disclosure.** This session, and anyone who reads `results/exploratory/`, has seen exploratory values for S1 and S4 at lambda 0 and 0.5 at the planned run size, made with exploratory seeds, before the freeze. The freeze record should state this.

### Proposed amendments for the owner (not applied; the draft protocol is unchanged)

- **A-1 (seeds).** Raise seeds per cell from 10 to at least 15, as the protocol's own rule requires (largest measured SD 0.0179 gives a half-width of 0.0128 at 10 seeds and 0.0099 at 15). Recommendation: 30, the cap, because compute is negligible.
- **A-2 (DELIB is degenerate).** As drafted, only minority members switch, and only towards the round-0 majority, so the round-1 majority always equals the round-0 majority: DELIB at budget 2n is MV at n, for any `w`. This is pinned by `test_delib_as_drafted_always_equals_mv_of_round0`. Options: (a) in round 1 each reasoner takes a fresh private draw and switches to the round-0 majority only if that draw and the majority agree against its first answer; (b) switching driven by confidence (a reasoner switches when its confidence is below the mean confidence of the opposing side); (c) drop DELIB and keep SEQ as the only information-sharing rule.
- **A-3 (CW and the confidence model, O-4).** In the smoke run CW was far above MV in every cell (for example 0.97 against 0.71 at nine calls in S1, lambda 0; 2 seeds of 200 items). With `delta = 1`, each reasoner's confidence carries strong private information about its own correctness, so CW's advantage is a property of the confidence model rather than of aggregation. Suggestion: fix `delta` from a stated target (for example the individual AUROC of confidence), report CW as secondary, or add `delta` to the EXP-004 factors.
- **A-4 (inadmissible Bahadur cells).** EXP-003: 9 of 48 Bahadur cells are inadmissible, namely (r = 0.2, n = 15) and (r = 0.4, n in {9, 15}) for every p. EXP-001: 20 of 90 (c = 0.1 at n = 31; c = 0.4 at n in {9, 15, 31}). Either accept these as reported exclusions or narrow the grid.
- **A-5 (commands and small details).** The reproduction commands in the protocols (`paradox validate`, `paradox analyse`) become `paradox run` and `paradox report`. EXP-001 cells share seeds across `n` (D-008), so its false-alarm estimate assumes an independence that does not hold exactly. Confirm or change D-008 (same seeds across cells).

### Changed files

Commit 1 (`9bfb9d3`): `pyproject.toml`, `uv.lock`, `CONTRIBUTING.md` (development commands), `src/README.md`, `tests/README.md`, `src/paradox/*.py` (12 modules), `tests/test_*.py` (5 files), `configs/exploratory/{smoke,probe_seed_spread,probe_engine_validation}.json`. Commit 2: `src/paradox/cli.py` (test pass-through), `results/exploratory/{smoke,probe-engine-validation,probe-seed-spread}/`, `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv}`, `roadmap.md`, `progress.md`, `README.md`.

### Not done, and why

- No confirmatory run and no hash freeze (G-FREEZE).
- DELIB not redefined: this is a protocol change for the owner (A-2).
- EXP-004 "abstain counted as wrong" tie level not implemented; EXP-004 is optional (O-5).
- No per-experiment `config.json`: these depend on A-1 and are written at freeze.
- No experiment `report.md` in `research/experiments/`: no registered experiment has run.
- No demo UI (M5).

### Risks

DELIB as drafted cannot answer its question (A-2). CW conclusions would depend on an ad hoc confidence model (A-3). Some outcomes for S1 and S4 have been seen before the freeze (disclosure above).

### Next action

The owner decides on O-1 to O-6 and A-1 to A-5 and freezes the protocols. Then: write the confirmatory configs, run EXP-001 (stop rule), then EXP-002 to EXP-004 (M3).

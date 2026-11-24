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

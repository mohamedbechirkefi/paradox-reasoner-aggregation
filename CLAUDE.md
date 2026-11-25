<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX: how every session works

PARADOX studies collective reasoning with synthetic reasoners: under equal compute budgets, when does aggregation of fallible reasoners improve or degrade accuracy? `master_prompt.md` is the authority. It is never edited. If this file and the master prompt conflict, the master prompt wins; record the conflict in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md`
2. `roadmap.md`
3. `progress.md` (latest entry first, then earlier entries as needed)
4. `research/protocol.md`
5. `research/claims_register.csv`

Then inspect `git status` and the existing files. Never overwrite changes made by the owner. State the current milestone and the next bounded task before editing.

## 2. Mandatory requirements (master prompt section 11, all sessions)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex and manuscript.pdf generated), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN ids for runs, FIG ids for figures, CLM ids for claims. A seed is a run inside an experiment, not a new experiment. A new question or materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** `research/experiments/EXP-NNN/protocol.md` exists, is complete, and is frozen by the owner (version and SHA-256 recorded in the registry) before any confirmatory run. Post-hoc changes are exploratory, dated and justified.
- **Every registered experiment gets a standalone report (11.3)** with the twelve mandatory sections, including failed, null, abandoned and exploratory experiments, visibly labelled.
- **One integrated manuscript (11.4).** Markdown is canonical. No invented authors, affiliations, funding, citations, acceptance or novelty claims.
- **Evidence pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. Every quantitative claim maps to experiment id, run ids, metric definition, result path, generator script, protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Extended milestones (11.6).** M0/M1 registry, skeleton and protocols, zero-cost toolchain; M2 schemas, manifests and report generators alongside the core; M3 reports as experiments finish; M4 audit and synthesis; M5 identical results across demo, paper, reports and articles; M6 compiled and inspected PDFs, clean-clone reproduction, owner checklist.
- **Publication gate.** Satisfied only when every registered experiment has a truthful report, the manuscript is complete, artifacts are traceable and blockers are disclosed.

## 3. Rules

### Gates (owner decisions only)

- **G-PUBLIC.** Never push, add a remote, create a GitHub repository or publish anything.
- **G-SPEND.** No paid service of any kind. The coding subscription is not an inference backend.
- **G-FREEZE.** Never freeze a protocol. Freezing, and any later amendment of a frozen protocol, is the owner's decision. Until the owner freezes, all runs are exploratory and labelled as such.
- No confirmatory experiment before the owner freeze. Tiny exploratory smoke checks of the toolchain are allowed and labelled exploratory.

### Scope

- Work only inside this repository. Read-only use of the shared tools listed in `research/feasibility.md`. Never modify the shared Helix tools folder (`../../helix/.tools/` from this repository).
- Do not touch any other folder of the research workspace (hive, helix, cogkt, trading, the other labs).
- Never kill processes this session did not start. Never delete anything this session did not create.

### Truthfulness

- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs in `progress.md`.
- A source not actually opened is labelled unverified and is not cited as read.
- Synthetic reasoners are not LLMs. No LLM benchmark claim unless a local model was actually run under a separate protocol.

### Files and style

- New text and code files start with `SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0` as a comment where the format allows. JSON and CSV files are covered by `NOTICE.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).
- The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`) are the owner's and are not changed. Development commands may be appended to `CONTRIBUTING.md`.

### Commits

- Local commits only: `git -c user.name=mohamedbechirkefi -c user.email=<owner address, given out of band> commit`. The message ends with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Run `git status` before and after each commit.

## 4. Session end

Update `progress.md` (dated, commands and actual outputs, changed files, risks, next action) and `roadmap.md` statuses. Never mark incomplete work done.

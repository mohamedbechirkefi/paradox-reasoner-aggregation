<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Reproducibility report (M6, 2026-11-25)

Actual command outputs only. Machine: Apple M1 Pro, macOS 15.3.1 (Darwin 24.3.0); uv from the shared toolchain (`../.tools/py/bin/uv`); Node v22.23.3 (shared install, used read-only); at most 2 workers. Authority: owner, 2026-11-25, "Next" (second); decision D-017.

- [x] Clean clone into a separate directory (path, commit).
- [x] `uv sync --frozen` from `uv.lock` (output).
- [x] Test suite (actual counts and output).
- [x] Smoke reproduction; comparison against committed results within the documented tolerance.
- [x] Report and manuscript build (pandoc and typst outputs).
- [x] Demo build and offline check.
- [x] Data manifest and link verification.
- [x] Secret, personal-data and licence scan.
- [x] Failures and deviations listed.

## 1. Clean clone

`git clone -q <working repository> <scratch>/paradox-reasoner-aggregation/m6/clone` (local clone, no network) of HEAD `51bd9fc9d714d62e540cd2eddfa373ca66ab4952` (the M5 follow-up commit), before any M6 change. The clone was deleted at the end of the session.

| Command (in the clone) | Actual output |
|---|---|
| `uv sync --frozen --all-groups --all-extras` | first run installed the locked packages (last lines `+ typst==0.15.2`, `+ tzdata==2026.6`); a second run printed `Audited 25 packages in 4ms` |
| `.venv/bin/python -m pytest -q` | `327 passed in 47.91s` |
| `.venv/bin/paradox smoke --out results/exploratory/smoke-m6` | `exploratory run of SMOKE finished in 0.09 s; peak RSS 41.2 MiB` |
| compare `smoke-m6/results.json` with the committed `results/exploratory/smoke/results.json` (field by field) | 10 differing fields, all expected: `runtime_s` in 8 records, `code_revision`, `created_utc`; every record value, summary and seed identical |
| compare `smoke-m6/metrics.csv` with the committed `metrics.csv` | 88 rows each; identical after dropping the `variant` column, which the metrics writer gained after the committed smoke run (all values empty in the new file) |
| `cd demo && npm ci --prefer-offline` | `added 53 packages in 978ms` |
| `npm test` | `Test Files 2 passed (2)`, `Tests 21 passed (21)` |
| `npm run build` | `dist/assets/index-ST6vMZFH.js 254.79 kB`, `built in 412ms` |
| `node tools/a11y_check.mjs dist` | 9 PASS lines (6 experiment panels; contrast light and dark; keyboard 36 of 36; focus indicator; 360 px overflow 0px; reduced motion 0 running; no external request; offline sandbox run) and `A11Y-CHECK PASS` |
| `.venv/bin/python scripts/export_demo_data.py` | `wrote demo/public/data/results.json: 6 entries, 59 estimates, 456 curve points` |
| `.venv/bin/python scripts/export_sandbox_fixture.py` | `wrote demo/src/fixtures/engine_fixture.json: 3 cases, committed seed-run of S6` |
| `git status --short` after both exports | empty (0 lines): the exports are deterministic |
| `.venv/bin/python scripts/m4_recompute_checks.py` | `29 checks, 0 failed`; 2 EXP-004 checks print `SKIP` because `results/EXP-004/metrics.csv` is git-ignored (D-012); the working repository, which has the file, gives `31 checks, 0 failed` |
| `.venv/bin/python scripts/m4_number_trace.py` | `TOTAL 1153 decimal tokens, 0 unmatched` |

The README's one-command reproduction (`scripts/m3_run.sh EXP-001`) reruns a confirmatory experiment; it was not run in M6 (no confirmatory runs). The smoke matrix (`paradox smoke`) is the smallest command that regenerates a committed result, and it reproduced it as stated above.

## 2. PDFs (working repository)

`.venv/bin/python scripts/m6_build_pdfs.py --png <scratch>/png` (pandoc 3.6.3 to Typst, `typst` Python package 0.15.2, D-002). Page counts and metadata were read with pypdf from the shared toolchain.

| PDF | Pages | Size | Title metadata | E-mail or local path in text or bytes |
|---|---|---|---|---|
| `research/paper/manuscript.pdf` | 10 | 185,054 bytes | manuscript title | none |
| `research/paper/supplementary.pdf` | 6 | 185,391 bytes | supplementary title | none |
| `research/experiments/EXP-001/report.pdf` | 4 | 140,950 bytes | report title | none |
| `research/experiments/EXP-002/report.pdf` | 8 | 545,568 bytes | report title | none |
| `research/experiments/EXP-003/report.pdf` | 5 | 334,265 bytes | report title | none |
| `research/experiments/EXP-004/report.pdf` | 7 | 560,925 bytes | report title | none |

Every manuscript page, every supplementary page, the first page and every figure page of each report (EXP-001 p. 3, EXP-002 p. 5, EXP-003 p. 4, EXP-004 pp. 4 to 6) were rendered to PNG at 60 ppi and inspected. No clipped figure, unreadable table, raw Markdown or missing glyph was found (all six sources are pure ASCII). Equations are typeset as inline code, as in the Markdown source; they are legible. The 24-panel EXP-002 figure is dense at page size; its source image is 1560 x 1890 pixels, so it stays legible when zoomed. One fix: the PDFs had no title metadata (the pandoc template sets an empty title); `build_pdf` now writes the first level-one heading as the PDF title. There is no `manuscript.tex` generator in this repository; none was produced.

## 3. References, links and manifests

- Citation keys: 8 keys cited in the manuscript and reports, 8 entries in `research/paper/references.bib`; every key resolves and every entry is cited.
- External sources: kaniovski2008 read in full (pages 1 to 13, before M6); the other seven were opened in full text on 2026-11-25 and the cited claim checked at the place recorded in `research/literature_review.md` section 4 (with SHA-256 of each PDF). Abstract only: 0. Unverified and cited: 0. No claim needed qualification.
- `.venv/bin/python scripts/m6_check_links.py`: `61 Markdown files, 61 relative links, 0 broken` (58 before the README gained three PDF links in M6) (test `tests/test_links.py`).
- Numbers: `tests/test_demo_export.py` checks every decimal in the README, both articles and the demo README against the manuscript, supplementary appendix and reports (passes); `scripts/m4_number_trace.py`: 1153 decimal tokens, 0 unmatched.
- `data/manifest.json`: SHA-256 `b2881ad496e68f02f56027c1e01eeafa3ce62e86d62b7413a9d25781c2a116a0`, equal to the value quoted in the `reproduction.md` files; it lists no external dataset (D-004), so it carries no data hashes to check.
- `research/publication/artifact_manifest.json`: 42 entries; 28 distinct file paths named, all exist and are tracked; 18 `result_sha256` values recomputed, 18 match; every `copy_identical` copy is byte-identical to its source.

## 4. Secret, identifier and licence scan (tracked files, `git ls-files`, 235 files before M6)

| Pattern | Hits | Action |
|---|---|---|
| e-mail addresses | 1: the commit-trailer address of the AI vendor in `CLAUDE.md` (a no-reply service address, not personal) | kept: it is the required commit trailer |
| private-key headers, AWS, GitHub, OpenAI, Slack or Google key patterns, quoted secrets | 0 | none |
| `.env` files | 0 | none |
| absolute home-directory paths | 20 lines in 11 files | removed from `README.md` (2), `demo/README.md` (1), `CLAUDE.md` (2), `research/feasibility.md` (5) and `src/paradox/report.py` (1; the default pandoc path is now resolved relative to the package); kept in `progress.md` (3) and `research/decision_log.md` (2), which are append-only, and in `results/EXP-00N/run_log.txt` (4), which are committed results; a note is appended to `progress.md` |

Dependency licences: `research/publication/dependency_licences.md` (24 Python distributions, 53 installed npm packages). Flags: MPL-2.0 for `hypothesis` (test only) and `lightningcss` (build only); pandoc (GPL-2.0-or-later) is an external tool, not a dependency. Nothing copyleft-strong, non-commercial or unknown.

SPDX headers: every file added since the initial commit carries the header where the format allows, except `demo/.npmrc`, which comes unchanged from the shared demo template (the M5 brief kept it unchanged).

## 5. Failures and deviations

- No failure in the clean clone. The smoke `metrics.csv` differs from the committed one by a later-added empty `variant` column only (recorded above, not a reproduction failure).
- PDF title metadata missing: fixed in `src/paradox/report.py`.
- Home-directory paths in current files: removed where safe (section 4).
- No frozen protocol, config, seed or result changed; no confirmatory run.

## 6. Re-check of the M6 commit in a fresh clone

Fresh local clone of `77a0219`: `uv sync --frozen --all-groups --all-extras`, then `pytest -q`: `329 passed in 13.69s`; `scripts/m6_check_links.py`: `62 Markdown files, 61 relative links, 0 broken`; both exports left `git status` empty; `npm ci --prefer-offline`: `added 53 packages in 659ms`; `npm test`: `Tests 21 passed (21)`; `npm run build` succeeded; `node tools/a11y_check.mjs dist`: `A11Y-CHECK PASS`. The clone was deleted.

## 7. Owner answers of 2026-11-26: home paths remaining

Authority: owner, 2026-11-26, decision sheet, B9 (scrub editable files in a new commit; no history rewrite); D-018. The repository is public since 2026-11-25, so these lines are already public in the history either way.

A `git grep` for the macOS home-directory prefix after the change finds 9 lines in 6 files, all left on purpose:

| File | Lines | Why it stays |
|---|---|---|
| `progress.md` | 3 | append-only record; the dated entries stay true for their date |
| `research/decision_log.md` | 2 | append-only record |
| `results/EXP-001/run_log.txt` to `results/EXP-004/run_log.txt` | 1 each | committed run logs of the confirmatory runs (generated output, left unchanged with the results) |

No editable file (README, CLAUDE.md, docs, scripts, source code, demo files, publication records) contains a home path.

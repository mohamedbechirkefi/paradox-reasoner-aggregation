<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Feasibility audit (M0, 2026-11-24)

All values below were checked with the commands shown in this session; outputs are quoted from the terminal. The full command log is in `progress.md`.

## 1. Hardware

| Item | Command | Output |
|---|---|---|
| CPU | `sysctl -n machdep.cpu.brand_string` | Apple M1 Pro |
| Cores | `sysctl -n hw.ncpu` | 10 |
| Memory | `sysctl -n hw.memsize` | 17179869184 bytes (16 GiB) |
| OS | `sw_vers` | macOS 15.3.1, build 24D70 |
| Free disk | `df -h` on the workspace volume | 129 GiB available (460 GiB volume, 71% used) |

## 2. Tools

| Tool | Location | Version (command output) | Use |
|---|---|---|---|
| Python | `/usr/local/bin/python3` | Python 3.12.1 | project runtime |
| uv | `../.tools/py/bin/uv` | uv 0.9.5 (d5f39331a 2025-10-21) | environment and lockfile |
| typst (Python package) | `../.tools/py/bin/python` | typst 0.15.0 | PDF compilation |
| pypdf | same | 6.20.0 | PDF inspection |
| pillow | same | 11.3.0 | figure checks |
| pandoc | `../.tools/pandoc` | pandoc 3.6.3 | Markdown to Typst and LaTeX |
| Node | `../../helix/.tools/node/bin/node` | v22.23.3 | demo build (read-only use; that folder is never modified) |
| git | system | git version 2.42.1 | version control |
| TeX | `which tex pdflatex xelatex` | not found | none available |

There is no `typst` executable in `.tools/py/bin`; typst is used through the Python package (`import typst`).

## 3. Zero-cost publication toolchain (decision D-002)

There is no TeX distribution. PDFs are produced as follows:

1. Markdown (canonical) to Typst with pandoc: `pandoc in.md -s -V mainfont="Libertinus Serif" -o out.typ`.
2. Typst to PDF with the Python package: `python -c "import typst; typst.compile('out.typ', output='out.pdf')"`.
3. `manuscript.tex` is generated from Markdown with pandoc (`pandoc manuscript.md -s -o manuscript.tex`) as a source deliverable; it is not compiled locally because no TeX engine exists.
4. Page inspection with pypdf (text extraction) and rendered-page review.

**Exploratory toolchain smoke check (2026-11-24, scratch directory outside the repository, not a research result).** A 7-line Markdown file with inline math and a table was converted to `.typ` and `.tex`. The first compile failed with `typst.TypstError: font fallback list must not be empty`, because pandoc's default Typst template sets `font: ()`. Passing `-V mainfont="Libertinus Serif"` fixed it: the compile produced a 1-page PDF whose extracted text contained the heading, the math and the table cells. The `mainfont` variable is therefore mandatory in the build script.

## 4. Time budget

Target: five focused development days (master prompt section 1). Planned allocation (planning estimate):

| Day | Work |
|---|---|
| 1 | M0 (this session) and M1 review with the owner; owner freeze of protocols |
| 2 | M2 engine, theoretical baselines, tests, schemas, report generator |
| 3 | M3 smoke, EXP-001, EXP-002, EXP-003; EXP-004 if on schedule |
| 4 | M4 interpretation, reports, manuscript; M5 static demo |
| 5 | M6 clean-clone reproduction, PDFs, release checklist |

Cut order if the schedule slips (master prompt section 9): EXP-004 first, then DELIB, then demo features beyond the minimum (network view, one accuracy/cost curve, playground). Controls, reports and evidence capture are never cut.

## 5. Compute budget

The largest planned experiment (EXP-002) has 240 runs of 2000 items x 31 reasoner draws, about 1.5e7 Bernoulli draws plus aggregation, which is expected to take seconds to minutes with NumPy on this machine (estimate, to be measured in the smoke run). No GPU, cloud or paid service is needed. Memory per run is below 10 MB (estimate).

## 6. Sources and licences

- **No external dataset is required.** All data are synthetic, produced by the project's own generator with recorded parameters and seeds.
- Literature: see `literature_review.md`. Only sources opened in this session are cited as read.
- Optional candidates (not adopted, not downloaded) are listed in `data/manifest.json` with their licence status.

## 7. Scope and exclusions

- In scope: synthetic binary-decision reasoners, the five rules of `protocol.md`, four experiments, a static offline demo, reports and a manuscript.
- Out of scope: any LLM inference (the optional local open-weight extension would need its own protocol and owner approval), human participants, personal data, paid services, real-world claims.
- Fallback: if the demo cannot be built with the available Node, a static HTML page with precomputed results and a small vanilla-JavaScript sandbox replaces it.

## 8. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Primary MV outcomes are analytically predictable | EXP-002 adds little beyond theory for MV | Stated openly; the empirical content lies in SEQ, DELIB, CW and EXP-003; EXP-001 validates the engine against theory |
| Bahadur model admissibility | some `(p, c, n)` give negative probabilities | admissibility check, inadmissible cells reported and excluded by rule, not by outcome |
| Confidence model is ad hoc | CW and calibration results depend on it | owner decision O-4 before freeze; EXP-004 varies `tau` |
| No TeX | no LaTeX-compiled PDF | Typst path (D-002); `.tex` delivered as source |
| uv lock needs network access | lockfile may fail | recorded in `progress.md` if it fails |

<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# demo/: PARADOX interactive research page (M5)

A static, offline page for the PARADOX study: the published results of EXP-001 to EXP-004 and two exploratory checks, each with its verdict under the frozen rule and its intervals; the EXP-002 accuracy and cost curves (hand-written SVG, seed-level t 95% intervals, Holm-rejected cells marked); and a seeded sandbox with a reasoning-network view of one item. Measured results, sandbox output and assumption values are labelled distinctly. Synthetic reasoners are not language models or people.

Demo URL: <https://paradox-reasoner-aggregation.kefimohamedbechir.workers.dev>.

Hosting: the built page (`dist/`) is hosted as Cloudflare Workers static assets on the free plan, configured by `wrangler.jsonc` (assets only, no Worker script). It is deployed by the coordinator of the research workspace, not by any script of this repository. The built page loads nothing from another origin.

## Commands

Node 22 (in the development workspace, a shared install outside this repository, used read-only):

    cd demo && npm ci && npm run build && npm run preview
    npm test                                   # vitest: loader validation and engine port
    node tools/a11y_check.mjs dist --screenshots <dir>

The page is built from the shared lab template (TypeScript, React and Vite, versions pinned in `package-lock.json`). Its only additions are two self-hosted font packages (see Third-party notes).

## Data

`public/data/results.json` (schema `lab-demo-results` 1.0.0) is written by `scripts/export_demo_data.py` from committed results only. The loader (`src/results.ts`) fails closed: any missing or malformed field, an interval that does not contain its estimate, or a display string that differs from its value means no numbers and no sandbox are shown. `tests/test_demo_export.py` checks that the committed file equals a fresh export and that every displayed string appears verbatim in the manuscript or is a documented exception.

## Sandbox

`src/engine.ts` ports NumPy's SeedSequence, PCG64 and `Generator.random()` and the engine's SINGLE, MV and SEQ rules. For the same settings it reproduces the Python engine exactly (tolerance: identical draws and decision counts), checked by `src/engine.test.ts` against `src/fixtures/engine_fixture.json` (written by `scripts/export_sandbox_fixture.py`) and against one committed EXP-002 seed-run. CW is not ported (it needs NumPy's ziggurat normal sampler). Runs are bounded to 5000 items and 31 reasoners and run in a Web Worker; Cancel terminates the worker. A sandbox run is one seed-run and carries no interval.

## Privacy

No visitor input is collected or stored, no request leaves the page's origin, and no font, script or image comes from a CDN. "Save output as JSON" writes a file on the visitor's own machine only.

## Design and brand

The page has its own identity (owner request of 2026-11-26): a jury room, with a slate deliberation board, chalk tally marks and ballot-paper reading surfaces. The plan, palette, type, motion and review are in `DESIGN.md`. Brand files are in `public/brand/` (mark, one-colour and reversed variants, wordmark lockups, favicon SVG and 32 px PNG, Open Graph card `og.png`). `tools/make_brand.py` regenerates the SVGs (needs fontTools; the wordmark is Zilla Slab Bold converted to outlines) and `tools/og.html` is the source of the Open Graph card (rendered with Chrome headless at 1200 by 630). The hero animation is labelled "Illustration, not study data" and prints no numeral; every number on the page still comes from `public/data/results.json`.

## Third-party notes

- Zilla Slab, `@fontsource/zilla-slab` 5.3.0 (weights 600 and 700, Latin subset), copyright 2017 The Mozilla Foundation, SIL Open Font License 1.1.
- Public Sans, `@fontsource/public-sans` 5.3.0 (weights 400 and 600, Latin subset), copyright the Public Sans project authors (USWDS), SIL Open Font License 1.1.

Both are bundled by Vite and served from the page's own origin. The licence texts ship in each package's `LICENSE` file under `node_modules/`.

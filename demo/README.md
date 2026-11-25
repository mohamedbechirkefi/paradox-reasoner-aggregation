<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# demo/: PARADOX interactive research page (M5)

A static, offline page for the PARADOX study: the published results of EXP-001 to EXP-004 and two exploratory checks, each with its verdict under the frozen rule and its intervals; the EXP-002 accuracy and cost curves (hand-written SVG, seed-level t 95% intervals, Holm-rejected cells marked); and a seeded sandbox with a reasoning-network view of one item. Measured results, sandbox output and assumption values are labelled distinctly. Synthetic reasoners are not language models or people.

Demo URL: `<demo URL: not yet published; release requires the owner's approval>`.

## Commands

Node 22 (in this workspace, `/Users/bechir/research/helix/.tools/node/bin`, read-only):

    cd demo && npm ci && npm run build && npm run preview
    npm test                                   # vitest: loader validation and engine port
    node tools/a11y_check.mjs dist --screenshots <dir>

The page is built from the shared lab template (TypeScript, React and Vite, versions pinned in `package-lock.json`). It adds no dependency.

## Data

`public/data/results.json` (schema `lab-demo-results` 1.0.0) is written by `scripts/export_demo_data.py` from committed results only. The loader (`src/results.ts`) fails closed: any missing or malformed field, an interval that does not contain its estimate, or a display string that differs from its value means no numbers and no sandbox are shown. `tests/test_demo_export.py` checks that the committed file equals a fresh export and that every displayed string appears verbatim in the manuscript or is a documented exception.

## Sandbox

`src/engine.ts` ports NumPy's SeedSequence, PCG64 and `Generator.random()` and the engine's SINGLE, MV and SEQ rules. For the same settings it reproduces the Python engine exactly (tolerance: identical draws and decision counts), checked by `src/engine.test.ts` against `src/fixtures/engine_fixture.json` (written by `scripts/export_sandbox_fixture.py`) and against one committed EXP-002 seed-run. CW is not ported (it needs NumPy's ziggurat normal sampler). Runs are bounded to 5000 items and 31 reasoners and run in a Web Worker; Cancel terminates the worker. A sandbox run is one seed-run and carries no interval.

## Privacy

No visitor input is collected or stored, no request leaves the page's origin, and no font, script or image comes from a CDN. "Save output as JSON" writes a file on the visitor's own machine only.

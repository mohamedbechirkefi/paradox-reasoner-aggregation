<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Generated in M6 from the installed metadata: Python from `.venv` (`importlib.metadata`, `License-Expression`, `License` or the licence classifier), npm from `demo/node_modules/*/package.json` for every package in `demo/package-lock.json` that is installed on this machine. The project's own licence (`LicenseRef-PARADOX-NC-Research-1.0`) is not repeated here; see `LICENSE` and `NOTICE.md`. This is an inventory, not legal advice.

## Summary

- Python: 24 third-party distributions (3 runtime, the rest test, report or transitive), all permissive (MIT, BSD, Apache-2.0, PSF, MIT-CMU, CC0, Zlib) except `hypothesis` (MPL-2.0, test only).
- npm: 53 installed packages (3 runtime: `react`, `react-dom`, `scheduler`, all MIT; 50 build or test). All MIT, ISC, BSD-3-Clause or Apache-2.0, except `lightningcss` and `lightningcss-darwin-arm64` (MPL-2.0, build only). 31 optional platform packages in the lockfile are not installed on this machine and were not inspected; they are platform builds of `rolldown`, `lightningcss` and their WebAssembly helpers.
- Nothing is GPL, AGPL, LGPL, SSPL, non-commercial or unknown among the installed packages.

## Flags for the owner

1. **MPL-2.0 (weak, file-level copyleft):** `hypothesis` (Python, test only) and `lightningcss` (npm, CSS minifier used by the Vite build). Neither is modified or redistributed in source form by this repository; the built demo contains CSS processed by `lightningcss`, which MPL-2.0 does not restrict. No action needed unless MPL files are modified.
2. **External tools, not dependencies and not redistributed:** pandoc 3.6.3 (GPL-2.0-or-later) converts Markdown to Typst for the PDFs; the Typst compiler comes with the `typst` Python package (Apache-2.0); headless Chrome is used by `demo/tools/a11y_check.mjs`. Using a GPL tool to produce documents does not place the documents under the GPL.
3. **Fonts embedded in the PDFs (checked with pypdf):** Libertinus Serif (SIL Open Font License 1.1, which permits embedding) and DejaVu Sans Mono (Bitstream Vera derived licence, permissive), both bundled with Typst; matplotlib figures use DejaVu Sans (same licence).
4. **Build backend:** `uv_build` (Apache-2.0 OR MIT), resolved at build time only.

## Python (`.venv`)

| Distribution | Version | Licence | Role |
|---|---|---|---|
| attrs | 26.1.0 | MIT | transitive (jsonschema) |
| contourpy | 1.4.0 | BSD-3-Clause | transitive (matplotlib) |
| cycler | 0.12.1 | BSD (classifier) | transitive (matplotlib) |
| fonttools | 4.68.0 | MIT | transitive (matplotlib) |
| hypothesis | 6.170.15 | MPL-2.0 | test (dev group) |
| iniconfig | 2.3.1 | MIT | transitive (pytest) |
| jsonschema | 4.26.0 | MIT | runtime |
| jsonschema-specifications | 2025.9.1 | MIT | transitive (jsonschema) |
| kiwisolver | 1.5.1 | BSD (classifier) | transitive (matplotlib) |
| matplotlib | 3.11.2 | PSF-based matplotlib licence (classifier: Python Software Foundation License) | runtime |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | runtime |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | transitive |
| pillow | 13.0.0 | MIT-CMU | transitive (matplotlib) |
| pluggy | 1.7.0 | MIT | transitive (pytest) |
| Pygments | 2.21.0 | BSD-2-Clause | transitive (pytest) |
| pyparsing | 3.3.3 | MIT | transitive (matplotlib) |
| pytest | 9.2.0 | MIT | test (dev group) |
| python-dateutil | 4.0.0 | BSD-3-Clause | transitive (matplotlib) |
| referencing | 0.37.0 | MIT | transitive (jsonschema) |
| rpds-py | 2026.9.1 | MIT | transitive (jsonschema) |
| sortedcontainers | 2.4.0 | Apache-2.0 | transitive (hypothesis) |
| typing_extensions | 4.16.0 | PSF-2.0 | transitive |
| typst | 0.15.2 | Apache-2.0 | report group (PDF compilation) |
| tzdata | 2026.6 | Apache-2.0 | transitive |

## npm (`demo/node_modules`)

| Package | Version | Licence | Role |
|---|---|---|---|
| @jridgewell/sourcemap-codec | 1.6.0 | MIT | build/test |
| @oxc-project/types | 0.156.0 | MIT | build/test |
| @rolldown/binding-darwin-arm64 | 1.2.19 | MIT | build/test |
| @rolldown/pluginutils | 1.1.1 | MIT | build/test |
| @standard-schema/spec | 1.1.0 | MIT | build/test |
| @types/chai | 5.2.3 | MIT | build/test |
| @types/deep-eql | 4.0.2 | MIT | build/test |
| @types/estree | 1.0.11 | MIT | build/test |
| @types/react | 19.3.0 | MIT | build/test |
| @types/react-dom | 19.3.0 | MIT | build/test |
| @vitejs/plugin-react | 6.1.2 | MIT | build/test |
| @vitest/expect | 4.1.12 | MIT | build/test |
| @vitest/mocker | 4.1.12 | MIT | build/test |
| @vitest/pretty-format | 4.1.12 | MIT | build/test |
| @vitest/runner | 4.1.12 | MIT | build/test |
| @vitest/snapshot | 4.1.12 | MIT | build/test |
| @vitest/spy | 4.1.12 | MIT | build/test |
| @vitest/utils | 4.1.12 | MIT | build/test |
| assertion-error | 2.0.1 | MIT | build/test |
| chai | 6.3.0 | MIT | build/test |
| convert-source-map | 2.0.0 | MIT | build/test |
| csstype | 3.2.4 | MIT | build/test |
| detect-libc | 2.1.2 | Apache-2.0 | build/test |
| es-module-lexer | 2.3.2 | MIT | build/test |
| estree-walker | 3.0.3 | MIT | build/test |
| expect-type | 1.4.0 | Apache-2.0 | build/test |
| fdir | 6.5.0 | MIT | build/test |
| fsevents | 2.3.3 | MIT | build/test |
| lightningcss | 1.33.0 | MPL-2.0 | build/test |
| lightningcss-darwin-arm64 | 1.33.0 | MPL-2.0 | build/test |
| magic-string | 0.30.21 | MIT | build/test |
| nanoid | 3.3.20 | MIT | build/test |
| obug | 2.2.1 | MIT | build/test |
| pathe | 2.0.3 | MIT | build/test |
| picocolors | 1.1.1 | ISC | build/test |
| picomatch | 4.0.7 | MIT | build/test |
| postcss | 8.5.33 | MIT | build/test |
| react | 19.3.1 | MIT | runtime |
| react-dom | 19.3.1 | MIT | runtime |
| rolldown | 1.2.19 | MIT | build/test |
| scheduler | 0.28.0 | MIT | runtime |
| siginfo | 2.0.0 | ISC | build/test |
| source-map-js | 1.2.4 | BSD-3-Clause | build/test |
| stackback | 0.0.2 | MIT | build/test |
| std-env | 4.3.0 | MIT | build/test |
| tinybench | 2.9.0 | MIT | build/test |
| tinyexec | 1.4.0 | MIT | build/test |
| tinyglobby | 0.2.17 | MIT | build/test |
| tinyrainbow | 3.2.0 | MIT | build/test |
| typescript | 5.9.3 | Apache-2.0 | build/test |
| vite | 8.3.5 | MIT | build/test |
| vitest | 4.1.12 | MIT | build/test |
| why-is-node-running | 2.3.0 | MIT | build/test |

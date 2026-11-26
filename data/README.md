<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# data/

`manifest.json` records that this project uses no external dataset (D-004); all data are synthetic and regenerated from recorded parameters and seeds.

## Correction note (2026-11-26)

`manifest.json` still describes the synthetic generator as "planned (M2)". That text is out of date: the generator (`src/paradox/generator.py`) exists since M2 and produced every committed result. The file is left unchanged because its SHA-256 (`b2881ad4...a116a0`) is quoted in the four `research/experiments/EXP-00N/reproduction.md` files. This note was added on the owner's decision (owner, 2026-11-26, decision sheet, R-PARADOX-1; D-018).

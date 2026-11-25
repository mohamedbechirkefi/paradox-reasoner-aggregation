<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-003 reproduction

- **Revision:** `d997cf81784aaf136e385e489febaade7e18e55c`.
- **Environment:** `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest -q` (321 passed at the provenance revision).
- **Data:** synthetic only. `data/manifest.json` SHA-256 `b2881ad496e68f02f56027c1e01eeafa3ce62e86d62b7413a9d25781c2a116a0`.
- **Precondition:** EXP-001 passes (stop rule).
- **Run (through the freeze guard):** `scripts/m3_run.sh EXP-003`, after moving the committed `results/EXP-003/` aside. Direct command: `uv run paradox run --config research/experiments/EXP-003/config.json --out results/EXP-003/ --pdf`.
- **Analysis and figure:** `.venv/bin/python -m paradox.analysis EXP-003 results/EXP-003` writes `analysis/`, `FIG-003-1_delta_by_model.png`, `provenance.csv` and `sha256_manifest.json`. `uv run paradox report results/EXP-003/ --pdf` writes the generated per-cell table.
- **Expected outputs:** result schema 1.0.0; 192 model cells (183 run, 9 excluded); 48 matched cells, 16 with disagreeing signs. Exact values are deterministic. Monte Carlo values repeat for the same seeds; timing fields differ.
- **Committed checksums:** `results/EXP-003/sha256_manifest.json`; `results.json` SHA-256 `072d6cecf45405254949c1b97436c2d6d0461c7176fb93c4bd27413586ca5a78`.

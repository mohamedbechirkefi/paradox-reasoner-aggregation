<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-002 reproduction

- **Revision:** `d997cf81784aaf136e385e489febaade7e18e55c`.
- **Environment:** `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest -q` (321 passed at the provenance revision).
- **Data:** synthetic only. `data/manifest.json` SHA-256 `b2881ad496e68f02f56027c1e01eeafa3ce62e86d62b7413a9d25781c2a116a0`.
- **Precondition:** EXP-001 passes (stop rule).
- **Run (through the freeze guard):** `scripts/m3_run.sh EXP-002`. Move the committed `results/EXP-002/` aside first; the wrapper never overwrites raw results. Direct command: `uv run paradox run --config research/experiments/EXP-002/config.json --out results/EXP-002/ --pdf`.
- **Analysis and figures:** `.venv/bin/python -m paradox.analysis EXP-002 results/EXP-002` writes the frozen-rule analysis, `FIG-002-1_delta_vs_budget.png`, `provenance.csv` and `sha256_manifest.json`. `uv run paradox report results/EXP-002/ --pdf` writes the generated tables and `accuracy_vs_budget.png`.
- **Expected outputs:** result schema 1.0.0; 720 runs, 0 excluded; 240 cells in the Holm family, 32 rejected. Reruns with the same seeds give identical draws (`test_rerun_is_deterministic`); timing fields differ, so file hashes match the committed ones only for the record content.
- **Committed checksums:** `results/EXP-002/sha256_manifest.json`; `results.json` SHA-256 `08c5b493cec61c7edd235492f1f906539ec26633362689ea3f225c812fb641bb`.

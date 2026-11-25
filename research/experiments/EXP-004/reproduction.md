<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-004 reproduction (optional experiment)

- **Revision:** `d997cf81784aaf136e385e489febaade7e18e55c`.
- **Environment:** `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`; `.venv/bin/python -m pytest -q` (321 passed at the provenance revision).
- **Data:** synthetic only. `data/manifest.json` SHA-256 `b2881ad496e68f02f56027c1e01eeafa3ce62e86d62b7413a9d25781c2a116a0`.
- **Precondition:** EXP-002 results present in `results/EXP-002/` (the analysis reads them).
- **Run (through the freeze guard):** `scripts/m3_run.sh EXP-004`, after moving the existing `results/EXP-004/` aside. Direct command: `uv run paradox run --config research/experiments/EXP-004/config.json --out results/EXP-004/ --pdf`.
- **Analysis and figures:** `.venv/bin/python -m paradox.analysis EXP-004 results/EXP-004 --exp002 results/EXP-002` writes `analysis/`, FIG-004-1 to FIG-004-3, `provenance.csv` and `sha256_manifest.json`. `uv run paradox report results/EXP-004/ --pdf` writes the generated tables and `accuracy_vs_budget.png`.
- **Raw files not in git:** `results/EXP-004/results.json` and `metrics.csv` (D-012, folder over 20 MB). Regenerate them with the run command above. The committed SHA-256 (`results.json`: `68638fd8c4d010547dd00d524e4c582495b262b0758327992d4d5a3a6c5a9114`) identifies the original files. Reruns repeat the draws, but timing fields and timestamps differ, so a rerun's file hash will not match; compare record content instead.
- **Expected outputs:** result schema 1.0.0; 1440 runs, 0 excluded; 18 frozen-rule checks, 0 reversed; the primary variant identical to EXP-002 per seed.

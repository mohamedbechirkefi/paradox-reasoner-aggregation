<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-001 reproduction

- **Revision:** `d997cf81784aaf136e385e489febaade7e18e55c` (the provenance revision of the confirmatory run).
- **Environment:** `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (lockfile `uv.lock`, exclude-newer 2026-11-10); then `.venv/bin/python -m pytest -q` (321 passed at the provenance revision).
- **Data:** synthetic only; nothing to download. `data/manifest.json` SHA-256 `b2881ad496e68f02f56027c1e01eeafa3ce62e86d62b7413a9d25781c2a116a0`.
- **Run (through the freeze guard):** `scripts/m3_run.sh EXP-001`. It refuses to overwrite an existing `results/EXP-001/results.json`, so move the committed folder aside first. Equivalent direct command: `uv run paradox run --config research/experiments/EXP-001/config.json --out results/EXP-001/ --pdf`. The guard refuses the config unless its hash and the protocol hashes match `research/freeze.json`.
- **Analysis:** `.venv/bin/python -m paradox.analysis EXP-001 results/EXP-001`, which writes `analysis/analysis.md`, `analysis/analysis.json`, `provenance.csv` and `sha256_manifest.json`.
- **Figure:** `uv run paradox report results/EXP-001/ --pdf` regenerates `figures/z_histogram.png` and the generated per-cell report.
- **Expected outputs:** result schema 1.0.0; 312 cells (292 run, 20 excluded); 0 cells outside 4 SE; golden fixtures to 1e-9 (`n = 3`) and 5e-8 (`n = 5`). Reruns with the same seeds give identical draws; timing fields and timestamps differ, so file hashes match the committed ones only for the record content.
- **Committed checksums:** `results/EXP-001/sha256_manifest.json`; `results.json` SHA-256 `c79d15c55b9cedc9c52caf96360edbc39b56d4606da93037907b4a75a5778d76`.

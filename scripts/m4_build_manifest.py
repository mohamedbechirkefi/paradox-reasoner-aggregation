# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (master prompt 11.5).

Maps every figure, table and claim used in the manuscript, supplementary
appendix and experiment reports to its experiment id, run ids, metric
definition, result path (with SHA-256), generator script, config and protocol
hashes and code revision. Claims come from research/claims_register.csv.
Exits 1 if a referenced result path does not exist.

Usage: .venv/bin/python scripts/m4_build_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = json.loads((ROOT / "research/freeze.json").read_text())
REV = "d997cf81784aaf136e385e489febaade7e18e55c"
DELTA = "Delta_r = A_r(B) - A_SINGLE, paired by item and seed; mean over 30 seed-runs; seed-level t 95% interval (proportion of items)"


def exp(e: str) -> dict:
    x = FREEZE["experiments"][e]
    return {"config_sha256": x["config_canonical_sha256"], "protocol_sha256": x["protocol_sha256"], "code_revision": REV}


RUNS = {"EXP-001": "CELL-0001 to CELL-0312 (292 run, 20 excluded)", "EXP-002": "RUN-0001 to RUN-0720",
        "EXP-003": "CELL-0001 to CELL-0192 (183 run, 9 excluded)", "EXP-004": "RUN-0001 to RUN-1440"}

ARTIFACTS = [
    ("FIG-001-1", "figure", "EXP-001", "z = (A_sim - A_theory) / SE_MC per validation cell", "research/experiments/EXP-001/figures/z_histogram.png", "results/EXP-001/figures/z_histogram.png", "paradox.report (paradox run --pdf)", "EXP-001 report 8.2; manuscript 5.1"),
    ("FIG-002-1", "figure", "EXP-002", DELTA, "research/experiments/EXP-002/figures/FIG-002-1_delta_vs_budget.png", "results/EXP-002/analysis/figures/FIG-002-1_delta_vs_budget.png", "paradox.analysis", "EXP-002 report 8.2; manuscript 5.2"),
    ("FIG-002-2", "figure", "EXP-002", "accuracy A (proportion) against B with seed-range bands", "research/experiments/EXP-002/figures/accuracy_vs_budget.png", "results/EXP-002/figures/accuracy_vs_budget.png", "paradox.report (paradox run --pdf)", "EXP-002 report 8.2 caption"),
    ("FIG-003-1", "figure", "EXP-003", "exact Delta_MV = A_MV(n) - p; Monte Carlo seed-level t95 (30 x 20,000 items)", "research/experiments/EXP-003/figures/FIG-003-1_delta_by_model.png", "results/EXP-003/analysis/figures/FIG-003-1_delta_by_model.png", "paradox.analysis", "EXP-003 report 8.2; manuscript 5.3"),
    ("FIG-004-1", "figure", "EXP-004", DELTA + "; MV by variant", "research/experiments/EXP-004/figures/FIG-004-1_mv_delta_by_variant.png", "results/EXP-004/analysis/figures/FIG-004-1_mv_delta_by_variant.png", "paradox.analysis", "EXP-004 report 8.4"),
    ("FIG-004-2", "figure", "EXP-004", DELTA + "; SEQ by variant", "research/experiments/EXP-004/figures/FIG-004-2_seq_delta_by_variant.png", "results/EXP-004/analysis/figures/FIG-004-2_seq_delta_by_variant.png", "paradox.analysis", "EXP-004 report 8.4"),
    ("FIG-004-3", "figure", "EXP-004", DELTA + "; even budgets, two tie rules", "research/experiments/EXP-004/figures/FIG-004-3_tie_rule.png", "results/EXP-004/analysis/figures/FIG-004-3_tie_rule.png", "paradox.analysis", "EXP-004 report 8.4"),
    ("FIG-004-4", "figure", "EXP-004", "accuracy A against B with seed-range bands", "research/experiments/EXP-004/figures/accuracy_vs_budget.png", "results/EXP-004/figures/accuracy_vs_budget.png", "paradox.report (paradox run --pdf)", "EXP-004 report 8.4 caption"),
    ("TAB-M1", "table", "EXP-002", DELTA + "; SINGLE accuracy A", None, "results/EXP-002/report.md", "paradox.report; paradox.analysis (analysis.json)", "manuscript Table 1; EXP-002 report 8.2"),
    ("TAB-M2", "table", "EXP-002", "frozen-rule verdicts of EXP-001 to EXP-004 (expected versus observed); sources are the four analysis.json files", None, "results/EXP-002/analysis/analysis.json", "paradox.analysis", "manuscript Table 2 (section 5.6)"),
    ("TAB-S2a", "table", "EXP-002", DELTA + "; Holm-adjusted one-sided p below 0.05", None, "results/EXP-002/analysis/analysis.json", "paradox.analysis", "supplementary S2; EXP-002 report 8.1"),
    ("TAB-S2b", "table", "EXP-002", "per-seed Delta_SEQ - Delta_MV at lambda 0; mean and t95", None, "results/EXP-002/analysis/analysis.json", "paradox.analysis", "supplementary S2; EXP-002 report 8.3"),
    ("TAB-S3", "table", "EXP-003", "exact Delta_MV = A_MV(n) - p", None, "results/EXP-003/analysis/analysis.json", "paradox.analysis", "supplementary S3; EXP-003 report 8.2"),
    ("TAB-E001-8.2", "table", "EXP-001", "cells, failing cells and max abs z by model", None, "results/EXP-001/analysis/analysis.json", "paradox.analysis", "EXP-001 report 8.1 and 8.2"),
    ("TAB-E004-8.1", "table", "EXP-004", "frozen-rule reversal checks", None, "results/EXP-004/analysis/analysis.json", "paradox.analysis", "EXP-004 report 8.1 to 8.3"),
]

EXPLORATORY = [
    ("TAB-S4a", "table", "EXP-002", "exact Delta_MV = A_MV(n) - mu (closed forms)", "results/exploratory/m4-analytic/results.json", "scripts/m4_exploratory_analytic.py", "supplementary S4; manuscript 5.5; EXP-002 report 9.1", "J-0015"),
    ("TAB-S4b", "table", "EXP-003", "exact Delta_MV = A_MV(n) - p beyond n 15 (closed forms)", "results/exploratory/m4-analytic/results.json", "scripts/m4_exploratory_analytic.py", "supplementary S4; manuscript 5.5; EXP-003 report 9.1", "J-0015"),
    ("TAB-S4c", "table", "EXP-002", DELTA.replace("30", "10 exploratory") + "; by confidence informativeness delta", "results/exploratory/m4-cw-delta/summary.json", "scripts/m4_cw_delta_summary.py (runs: paradox run on configs/exploratory/m4_cw_delta_*.json)", "supplementary S4; manuscript 5.5; EXP-002 report 9.1", "J-0016"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    entries, missing = [], []
    for aid, kind, e, metric, copy, src, gen, used in ARTIFACTS:
        s = ROOT / src
        if not s.exists():
            missing.append(src)
            continue
        ent = {"artifact_id": aid, "kind": kind, "label": "confirmatory", "exp_id": e, "run_ids": RUNS[e], "metric_definition": metric,
               "result_path": src, "result_sha256": sha(s), "generator_script": gen, **exp(e), "used_in": used}
        if copy:
            c = ROOT / copy
            ent["copy_path"] = copy
            ent["copy_identical"] = c.exists() and sha(c) == ent["result_sha256"]
        entries.append(ent)
    for aid, kind, e, metric, src, gen, used, j in EXPLORATORY:
        s = ROOT / src
        if not s.exists():
            missing.append(src)
            continue
        entries.append({"artifact_id": aid, "kind": kind, "label": "exploratory (M4, after verdicts)", "exp_id": e, "run_ids": j,
                        "metric_definition": metric, "result_path": src, "result_sha256": sha(s), "generator_script": gen,
                        "config_sha256": "configs/exploratory (see run_manifest.json per delta level)" if "cw" in src else "none (closed forms)",
                        "protocol_sha256": "none (exploratory)", "code_revision": "7b9b696 (scripts committed); runs at 2f689ed", "used_in": used})
    with open(ROOT / "research/claims_register.csv", newline="") as f:
        for r in csv.DictReader(f):
            ent = {"artifact_id": r["claim_id"], "kind": "claim", "label": r["status"], "exp_id": r["exp_id"], "run_ids": r["result_ids"],
                   "metric_definition": r["type"], "result_path": r["evidence_path"], "generator_script": "see figure_or_table",
                   "config_sha256": r["config_sha256"], "figure_or_table": r["figure_or_table"], "used_in": "manuscript " + r["manuscript_section"]}
            if r["exp_id"] in FREEZE["experiments"]:
                ent["protocol_sha256"] = FREEZE["experiments"][r["exp_id"]]["protocol_sha256"]
                ent["code_revision"] = REV
            entries.append(ent)
    doc = {
        "schema_version": "1.0",
        "updated": "2026-11-25",
        "status": "M4 evidence audit: every figure, table and claim of the manuscript, supplementary appendix and experiment reports; decimal numbers traced by scripts/m4_number_trace.py, headline counts recomputed by scripts/m4_recompute_checks.py",
        "main_protocol_sha256": FREEZE["main_protocol"]["sha256"] if isinstance(FREEZE["main_protocol"], dict) and "sha256" in FREEZE["main_protocol"] else FREEZE["main_protocol"],
        "generator": "scripts/m4_build_manifest.py",
        "entry_fields": ["artifact_id", "kind", "label", "exp_id", "run_ids", "metric_definition", "result_path", "result_sha256", "generator_script", "config_sha256", "protocol_sha256", "code_revision", "used_in", "copy_path", "copy_identical"],
        "entries": entries,
    }
    (ROOT / "research/publication/artifact_manifest.json").write_text(json.dumps(doc, indent=1) + "\n")
    bad = [e["artifact_id"] for e in entries if e.get("copy_identical") is False]
    print(f"{len(entries)} entries; missing paths {missing}; copies not identical {bad}")
    return 1 if (missing or bad) else 0


if __name__ == "__main__":
    sys.exit(main())

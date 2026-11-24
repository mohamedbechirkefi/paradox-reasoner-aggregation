# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M3 analysis module: frozen decision rules applied to small exploratory
result documents (exploratory seeds, tiny sizes), provenance and hashes."""

import copy
import json

import numpy as np
import pytest

from paradox import analysis, stats
from paradox.runner import execute, run_config

AGG = {
    "schema_version": "1.0.0", "experiment_id": "EXP-002", "label": "exploratory", "kind": "aggregation",
    "scenarios": [{"id": "S1", "p_easy": 0.6, "h": 0.0, "p_hard": None}, {"id": "S4", "p_easy": 0.9, "h": 0.4, "p_hard": 0.3}],
    "lambdas": [0.0, 0.5], "budgets": [1, 3, 31], "delib_budgets": [], "rules": ["SINGLE", "MV", "CW", "SEQ"],
    "n_items": 2000, "seed_entropy": 0, "n_seeds": 8, "w": 0.5, "delta": 1.0, "tau": 1.0, "tie_rule": "coin",
}


@pytest.fixture(scope="module")
def agg_doc():
    return run_config(copy.deepcopy(AGG))


def test_exp002_family_and_holm(agg_doc):
    a = analysis.analyse_exp002(agg_doc)
    # MV and SEQ at B in {3, 31}, 2 scenarios x 2 lambdas
    assert a["family_size"] == 2 * 2 * 2 * 2
    ps = [r["p_raw"] for r in a["primary_family"]]
    assert [r["p_holm"] for r in a["primary_family"]] == pytest.approx(stats.holm(ps))
    for r in a["primary_family"]:
        assert r["reject_no_degradation"] == (r["p_holm"] < 0.05)
        # Holm step bound below 0 iff the raw p-value is below the step level
        if r["holm_upper_bound"] != r["delta_mean"]:
            assert (r["holm_upper_bound"] < 0) == (r["p_raw"] < r["holm_level"])
    assert a["h0_rejected"] == (a["n_rejected"] > 0)
    # S4 at B 31, lambda 0 degrades strongly even with 4 small seeds
    assert any(c["scenario"] == "S4" and c["rule"] == "MV" and c["budget"] == 31 and c["lambda"] == 0.0 for c in a["rejected_cells"])


def test_exp002_predictions(agg_doc):
    a = analysis.analyse_exp002(agg_doc)
    p1 = {c["scenario"]: c for c in a["P1"]["cells"]}
    assert p1["S1"]["predicted"] == "gain" and p1["S4"]["predicted"] == "degradation"
    assert p1["S4"]["status"] == "supported" and p1["S1"]["status"] == "supported"
    assert a["P2"]["n_tests"] == 2 * 2  # 2 scenarios x B in {3, 31}
    assert a["P3"]["n_tests"] == 2  # S1 only (homogeneous), B in {3, 31}, one lambda step
    for c in a["P2"]["cells"] + a["P3"]["cells"]:
        lo, hi = c["t95"]
        assert lo <= c["diff_mean"] <= hi


def test_paired_difference_alignment():
    assert analysis._paired({1: 0.5, 2: 0.1, 3: 0.0}, {2: 0.1, 1: 0.2}) == pytest.approx([0.3, 0.0])


def test_exp004_reversal_logic(agg_doc):
    cfg = copy.deepcopy(AGG)
    cfg.update({"experiment_id": "EXP-004", "variants": [
        {"id": "primary"},
        {"id": "tie_coin", "budgets": [1, 2, 4], "rules": ["SINGLE", "MV", "SEQ"], "tie_rule": "coin"},
        {"id": "tie_abstain_wrong", "budgets": [1, 2, 4], "rules": ["SINGLE", "MV", "SEQ"], "tie_rule": "abstain_wrong"},
        {"id": "w_0p9", "w": 0.9}]})
    d4 = run_config(cfg)
    a = analysis.analyse_exp004(d4, agg_doc)
    assert a["primary_consistency_with_exp002"]["identical"]
    for r in a["checks"]:
        assert r["reversed"] == (r["variant_t95"][0] > 0)
    assert a["h0_rejected"] == (a["n_reversed"] > 0)
    assert a["n_significant_exp002_cells_in_scope"] >= 1


def test_exp001_and_exp003_small(tmp_path):
    val = {"schema_version": "1.0.0", "experiment_id": "EXP-001", "label": "exploratory", "kind": "validation", "ns": [1, 3, 31],
           "items_per_seed": 2000, "tolerance_se": 4.0, "seed_entropy": 0, "n_seeds": 2,
           "common_shock": {"ps": [0.55], "lambdas": [0.0, 1.0]},
           "mixture": {"scenarios": [{"id": "S4", "p_easy": 0.9, "h": 0.4, "p_hard": 0.3}], "lambdas": [0.0]},
           "bahadur": {"ps": [0.55], "cs": [0.0, 0.4]}}
    a1 = analysis.analyse_exp001(run_config(val))
    assert a1["n_cells_excluded"] == 1  # c 0.4 at n 31
    assert a1["pass"] is True and all(g["pass"] for g in a1["golden"])
    dep = {"schema_version": "1.0.0", "experiment_id": "EXP-003", "label": "exploratory", "kind": "dependence", "ps": [0.55], "rs": [0.4],
           "ns": [3, 9], "items_per_seed": 2000, "seed_entropy": 0, "n_seeds": 3, "models": ["common_shock", "bahadur", "mixture", "beta"]}
    a3 = analysis.analyse_exp003(run_config(dep))
    assert a3["n_model_cells_excluded"] == 1  # Bahadur r 0.4 at n 9
    assert a3["n_matched_cells"] == 2
    assert a3["h0_rejected"] == (a3["n_matched_cells_disagree"] > 0)
    # Kaniovski fixture: Bahadur at p 0.55, c 0.4, n 3 is below p
    assert any(c["model"] == "bahadur" and c["n"] == 3 for c in a3["negative_cells"])


def test_driver_writes_outputs(tmp_path):
    cfg_path = tmp_path / "c.json"
    small = copy.deepcopy(AGG)
    small.update({"n_items": 100, "n_seeds": 2, "budgets": [1, 3]})
    cfg_path.write_text(json.dumps(small))
    out = tmp_path / "exploratory" / "x"
    execute(cfg_path, out)
    assert analysis.main(["EXP-002", str(out), "--exit-status", "0"]) == 0
    prov = (out / "provenance.csv").read_text().splitlines()
    assert len(prov) == 1 + 2 * 2 * 2 and prov[1].endswith(",0")
    man = json.loads((out / "sha256_manifest.json").read_text())
    for name in ("results.json", "metrics.csv", "run_manifest.json", "provenance.csv", "analysis/analysis.json", "analysis/analysis.md",
                 "analysis/figures/FIG-002-1_delta_vs_budget.png"):
        assert man["files"][name]["sha256"] == analysis.sha256_file(out / name)
    text = (out / "analysis" / "analysis.md").read_text()
    assert "\u2014" not in text and "SPDX" in text
    assert np.isfinite(json.loads((out / "analysis" / "analysis.json").read_text())["P1"]["n_tests"])

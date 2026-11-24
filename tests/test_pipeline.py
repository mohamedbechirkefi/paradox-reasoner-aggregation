# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Integration: config -> results -> report; schema fail-closed; guards;
deterministic reruns; dependence samplers; CLI exit codes."""

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from paradox import cli, dependence, theory
from paradox.report import build_report
from paradox.runner import CONFIRMATORY_ENTROPY, GuardError, ProtocolNotFrozen, check_confirmatory_allowed, execute, run_config
from paradox.schema import SchemaError, load_result, validate_config, validate_result

REPO = Path(__file__).resolve().parents[1]

TINY = {
    "schema_version": "1.0.0", "experiment_id": "SMOKE", "label": "exploratory", "kind": "aggregation",
    "scenarios": [{"id": "S1", "p_easy": 0.6, "h": 0.0, "p_hard": None}, {"id": "S4", "p_easy": 0.9, "h": 0.4, "p_hard": 0.3}],
    "lambdas": [0.0, 0.5], "budgets": [1, 3, 4], "delib_budgets": [6], "rules": ["SINGLE", "MV", "CW", "SEQ", "DELIB"],
    "n_items": 120, "seed_entropy": 0, "n_seeds": 2, "w": 0.5, "delta": 1.0, "tau": 1.0,
}


def write_cfg(tmp_path, cfg, name="cfg.json"):
    p = tmp_path / name
    p.write_text(json.dumps(cfg))
    return p


def test_aggregation_end_to_end(tmp_path):
    out = tmp_path / "exploratory" / "tiny"
    man = execute(write_cfg(tmp_path, TINY), out)
    doc = load_result(out / "results.json")
    assert len(doc["records"]) == 2 * 2 * 2
    rec = doc["records"][0]
    assert all(rec["invariants"].values())
    pairs = {(m["rule"], m["budget"]) for m in rec["metrics"]}
    assert pairs == {("SINGLE", 1), ("MV", 1), ("MV", 3), ("MV", 4), ("CW", 1), ("CW", 3), ("CW", 4),
                     ("SEQ", 1), ("SEQ", 3), ("SEQ", 4), ("DELIB", 6)}
    single = [m for m in rec["metrics"] if m["rule"] == "SINGLE"][0]
    assert single["delta_vs_single"] == 0.0
    for key in ("config_sha256", "git_revision", "seeds", "runtime_s", "peak_rss_bytes", "environment"):
        assert key in man
    assert man["environment"]["versions"]["numpy"]
    assert (out / "metrics.csv").read_text().count("\n") == 1 + 8 * 11
    assert hashlib.sha256((out / "results.json").read_bytes()).hexdigest() == man["outputs"]["results.json"]
    res = build_report(out)
    text = Path(res["report_md"]).read_text()
    assert "EXPLORATORY. Not a finding." in text
    assert (out / "figures" / "accuracy_vs_budget.png").stat().st_size > 1000
    assert "\u2014" not in text


def test_rerun_is_deterministic():
    a, b = run_config(copy.deepcopy(TINY)), run_config(copy.deepcopy(TINY))
    strip = lambda d: [{k: v for k, v in r.items() if k != "runtime_s"} for r in d["records"]]  # noqa: E731
    assert strip(a) == strip(b)
    assert a["config_sha256"] == b["config_sha256"]


def test_single_identical_across_lambda_free_cells():
    # Common random numbers: within a run, MV at budget 1 is SINGLE.
    doc = run_config(copy.deepcopy(TINY))
    for r in doc["records"]:
        acc = {(m["rule"], m["budget"]): m["accuracy"] for m in r["metrics"]}
        assert acc[("MV", 1)] == acc[("SINGLE", 1)] == acc[("CW", 1)] == acc[("SEQ", 1)]


def test_result_schema_fails_closed(tmp_path):
    doc = run_config(copy.deepcopy(TINY))
    bad = copy.deepcopy(doc)
    bad["config"]["n_items"] = 999
    with pytest.raises(SchemaError):
        validate_result(bad)  # config hash mismatch
    bad = copy.deepcopy(doc)
    del bad["claims_boundary"]
    with pytest.raises(SchemaError):
        validate_result(bad)
    bad = copy.deepcopy(doc)
    bad["records"][0]["metrics"][0]["accuracy"] = 1.5
    with pytest.raises(SchemaError):
        validate_result(bad)
    p = tmp_path / "results.json"
    p.write_text("{not json")
    with pytest.raises(SchemaError):
        load_result(p)
    with pytest.raises(SchemaError):
        load_result(tmp_path / "missing.json")
    with pytest.raises(SchemaError):
        build_report(tmp_path)


@pytest.mark.parametrize("mutate", [
    lambda c: c.update(label="final"),
    lambda c: c.update(rules=["MV"]),
    lambda c: c.update(delib_budgets=[5]),
    lambda c: c.update(budgets=[40]),
    lambda c: c.pop("n_items"),
    lambda c: c.update(experiment_id="exp-2"),
])
def test_config_schema_rejects(mutate):
    cfg = copy.deepcopy(TINY)
    mutate(cfg)
    with pytest.raises(SchemaError):
        validate_config(cfg)


def test_explicit_seeds_must_match_derivation():
    cfg = copy.deepcopy(TINY)
    cfg["seeds"] = [1, 2]
    with pytest.raises(SchemaError):
        run_config(cfg)


def test_confirmatory_refused_while_protocols_are_drafts(tmp_path):
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, REPO)
    with pytest.raises(ProtocolNotFrozen):
        execute(write_cfg(tmp_path, cfg), tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_confirmatory_guard_accepts_a_frozen_fixture(tmp_path):
    # A synthetic repository with a frozen protocol (fixture only; the real protocols are drafts).
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.parent.mkdir(parents=True)
    proto.write_text("# EXP-002 protocol\n\nStatus: FROZEN v1.0 (fixture).\n")
    sha = hashlib.sha256(proto.read_bytes()).hexdigest()
    (tmp_path / "research" / "experiment_registry.csv").write_text(
        "exp_id,protocol_path,protocol_sha256\nEXP-002,research/experiments/EXP-002/protocol.md," + sha + "\n")
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    check_confirmatory_allowed(cfg, tmp_path)
    proto.write_text("# EXP-002 protocol\n\nStatus: FROZEN v1.0 (fixture), edited after freeze.\n")
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path)
    with pytest.raises(GuardError):
        check_confirmatory_allowed(cfg | {"seed_entropy": 0}, tmp_path.parent / "nowhere")


def test_exploratory_guards(tmp_path):
    with pytest.raises(GuardError):
        execute(write_cfg(tmp_path, TINY), tmp_path / "results" / "EXP-002")
    cfg = copy.deepcopy(TINY) | {"seed_entropy": CONFIRMATORY_ENTROPY}
    with pytest.raises(GuardError):
        execute(write_cfg(tmp_path, cfg), tmp_path / "exploratory" / "x")


def test_cli_exit_codes(tmp_path, capsys):
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    assert cli.main(["run", "--config", str(write_cfg(tmp_path, cfg)), "--out", str(tmp_path / "o")]) == 3
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    assert cli.main(["run", "--config", str(bad), "--out", str(tmp_path / "exploratory" / "o")]) == 2
    assert cli.main(["run", "--config", str(write_cfg(tmp_path, TINY)), "--out", str(tmp_path / "exploratory" / "ok")]) == 0
    assert cli.main(["report", str(tmp_path / "exploratory" / "ok")]) == 0
    assert cli.main(["nonsense"]) == 2


def test_validation_kind_end_to_end(tmp_path):
    cfg = {
        "schema_version": "1.0.0", "experiment_id": "PROBE-EXP001", "label": "exploratory", "kind": "validation",
        "ns": [1, 3, 4, 5], "items_per_seed": 4000, "tolerance_se": 4.0, "seed_entropy": 0, "n_seeds": 2,
        "common_shock": {"ps": [0.6], "lambdas": [0.0, 1.0]},
        "mixture": {"scenarios": [{"id": "S4", "p_easy": 0.9, "h": 0.4, "p_hard": 0.3}], "lambdas": [0.5]},
        "bahadur": {"ps": [0.55], "cs": [0.4]},
    }
    out = tmp_path / "exploratory" / "val"
    execute(write_cfg(tmp_path, cfg), out)
    doc = load_result(out / "results.json")
    models = {r["model"] for r in doc["records"]}
    assert {"independent", "perfect_correlation", "mixture", "bahadur"} <= models
    assert all(s["pass"] for s in doc["summary"])
    assert "z_histogram.png" in " ".join(build_report(out)["figures"])


def test_dependence_kind_end_to_end(tmp_path):
    cfg = {"schema_version": "1.0.0", "experiment_id": "PROBE-DEP", "label": "exploratory", "kind": "dependence",
           "ps": [0.55], "rs": [0.1], "ns": [3], "items_per_seed": 2000, "seed_entropy": 0, "n_seeds": 2,
           "models": ["common_shock", "bahadur", "mixture", "beta"]}
    out = tmp_path / "exploratory" / "dep"
    execute(write_cfg(tmp_path, cfg), out)
    doc = load_result(out / "results.json")
    assert len(doc["records"]) == 4 and len(doc["summary"]) == 1
    build_report(out)


@pytest.mark.parametrize("model", ["common_shock", "bahadur", "mixture", "beta"])
def test_dependence_samplers_match_analytic(model):
    n, p, r, N = 5, 0.6, 0.1, 100000
    k = dependence.sample_k(model, n, p, r, N, 99)
    acc = float(np.mean(2 * k > n))
    th = dependence.analytic_mv(model, n, p, r)
    assert abs(acc - th) < 4 * np.sqrt(th * (1 - th) / N)
    # marginal competence is p in every model
    assert abs(k.mean() / n - p) < 4 * np.sqrt(p * (1 - p) / (N * n)) * np.sqrt(1 + (n - 1) * r)


def test_bahadur_sampler_distribution():
    n, p, c, N = 3, 0.55, 0.4, 200000
    k = dependence.sample_k("bahadur", n, p, c, N, 1)
    freq = np.bincount(k, minlength=n + 1) / N
    assert freq == pytest.approx(theory.bahadur_k_distribution(n, p, c), abs=0.005)


def test_committed_exploratory_configs_validate():
    for p in sorted((REPO / "configs").rglob("*.json")):
        validate_config(json.loads(p.read_text()))

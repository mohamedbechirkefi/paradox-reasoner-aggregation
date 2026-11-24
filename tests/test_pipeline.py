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
from paradox.runner import CONFIRMATORY_ENTROPY, GuardError, ProtocolNotFrozen, check_confirmatory_allowed, execute, load_config, run_config
from paradox.schema import SchemaError, load_result, sha256_json, validate_config, validate_result

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


def test_confirmatory_refused_for_a_config_that_is_not_frozen(tmp_path):
    # Before the freeze this was refused because the protocol was a draft; after the
    # freeze it is refused because TINY is not the frozen EXP-002 config.
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, REPO)
    with pytest.raises(ProtocolNotFrozen):
        execute(write_cfg(tmp_path, cfg), tmp_path / "out")
    assert not (tmp_path / "out").exists()


def _frozen_fixture(root: Path, cfg: dict) -> Path:
    """A synthetic repository with a frozen EXP-002 protocol, main protocol, config and freeze record."""
    proto = root / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.parent.mkdir(parents=True)
    proto.write_text("# EXP-002 protocol\n\nStatus: FROZEN v1.0 (fixture).\n")
    main = root / "research" / "protocol.md"
    main.write_text("# Protocol\n\nStatus: FROZEN v1.0 (fixture).\n")
    cfg_path = proto.parent / "config.json"
    cfg_path.write_text(json.dumps(cfg, indent=1) + "\n")
    sha = hashlib.sha256(proto.read_bytes()).hexdigest()
    (root / "research" / "experiment_registry.csv").write_text(
        "exp_id,protocol_path,protocol_sha256\nEXP-002,research/experiments/EXP-002/protocol.md," + sha + "\n")
    rec = {
        "main_protocol": {"path": "research/protocol.md", "sha256": hashlib.sha256(main.read_bytes()).hexdigest()},
        "experiments": {"EXP-002": {
            "protocol_path": "research/experiments/EXP-002/protocol.md", "protocol_sha256": sha,
            "config_path": "research/experiments/EXP-002/config.json",
            "config_file_sha256": hashlib.sha256(cfg_path.read_bytes()).hexdigest(), "config_canonical_sha256": sha256_json(cfg),
        }},
    }
    (root / "research" / "freeze.json").write_text(json.dumps(rec))
    return cfg_path


def test_confirmatory_guard_accepts_a_frozen_fixture_and_refuses_changes(tmp_path):
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    cfg_path = _frozen_fixture(tmp_path, cfg)
    check_confirmatory_allowed(cfg, tmp_path)
    check_confirmatory_allowed(load_config(cfg_path), tmp_path, cfg_path)
    # a changed config (content) is refused
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg | {"n_items": 121}, tmp_path)
    # a changed config file (same content, different bytes) is refused when the path is given
    other = tmp_path / "reformatted.json"
    other.write_text(json.dumps(cfg))
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path, other)
    # the wrong seed entropy is refused
    with pytest.raises(GuardError):
        check_confirmatory_allowed(cfg | {"seed_entropy": 0}, tmp_path)
    # a changed main protocol is refused
    main = tmp_path / "research" / "protocol.md"
    original = main.read_text()
    main.write_text(original + "edit\n")
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path)
    main.write_text(original)
    check_confirmatory_allowed(cfg, tmp_path)
    # a missing freeze record is refused
    (tmp_path / "research" / "freeze.json").unlink()
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path)


def test_confirmatory_guard_refuses_an_edited_frozen_protocol(tmp_path):
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    _frozen_fixture(tmp_path, cfg)
    proto = tmp_path / "research" / "experiments" / "EXP-002" / "protocol.md"
    proto.write_text("# EXP-002 protocol\n\nStatus: FROZEN v1.0 (fixture), edited after freeze.\n")
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path)
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(cfg, tmp_path.parent / "nowhere")


def test_confirmatory_run_end_to_end_in_a_frozen_fixture(tmp_path):
    cfg = copy.deepcopy(TINY) | {"experiment_id": "EXP-002", "label": "confirmatory", "seed_entropy": CONFIRMATORY_ENTROPY}
    cfg_path = _frozen_fixture(tmp_path, cfg)
    man = execute(cfg_path, tmp_path / "results" / "EXP-002", repo_root=tmp_path)
    assert man["label"] == "confirmatory"
    assert "Confirmatory run under a frozen protocol." in Path(build_report(tmp_path / "results" / "EXP-002")["report_md"]).read_text()


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


def test_tie_rule_in_config_changes_only_even_budget_mv_and_seq():
    cfg = copy.deepcopy(TINY) | {"budgets": [1, 2, 3, 4], "rules": ["SINGLE", "MV", "CW", "SEQ"], "delib_budgets": []}
    coin = run_config(copy.deepcopy(cfg) | {"tie_rule": "coin"})
    absn = run_config(copy.deepcopy(cfg) | {"tie_rule": "abstain_wrong"})
    for rc, ra in zip(coin["records"], absn["records"]):
        mc = {(m["rule"], m["budget"]): m for m in rc["metrics"]}
        ma = {(m["rule"], m["budget"]): m for m in ra["metrics"]}
        assert mc.keys() == ma.keys()
        for key in mc:
            rule, b = key
            if rule in ("MV", "SEQ") and b % 2 == 0:
                # abstain-as-wrong loses exactly the ties the coin resolved correctly
                assert ma[key]["accuracy"] <= mc[key]["accuracy"]
                assert ma[key]["tie_share"] == mc[key]["tie_share"]
            else:
                assert ma[key]["accuracy"] == mc[key]["accuracy"]
    assert any(m["tie_share"] > 0 for r in coin["records"] for m in r["metrics"] if m["rule"] == "MV" and m["budget"] == 2)


def test_variants_run_tagged_and_separate(tmp_path):
    cfg = copy.deepcopy(TINY) | {"rules": ["SINGLE", "MV", "SEQ"], "delib_budgets": [], "variants": [
        {"id": "primary"},
        {"id": "abstain", "budgets": [1, 2, 4], "tie_rule": "abstain_wrong"},
        {"id": "w_0p9", "w": 0.9},
    ]}
    doc = run_config(copy.deepcopy(cfg))
    assert len(doc["records"]) == 3 * 2 * 2 * 2
    assert {r["variant"] for r in doc["records"]} == {"primary", "abstain", "w_0p9"}
    assert {r["w"] for r in doc["records"] if r["variant"] == "w_0p9"} == {0.9}
    assert {r["tie_rule"] for r in doc["records"] if r["variant"] == "abstain"} == {"abstain_wrong"}
    # the primary variant reproduces the plain config exactly (same seeds, same parameters)
    plain = run_config({k: v for k, v in copy.deepcopy(cfg).items() if k != "variants"})
    prim = [r for r in doc["records"] if r["variant"] == "primary"]
    assert [r["metrics"] for r in prim] == [r["metrics"] for r in plain["records"]]
    assert {s["variant"] for s in doc["summary"]} == {"primary", "abstain", "w_0p9"}
    assert not any(s.get("primary_family") for s in doc["summary"])
    assert any("delta_p_holm" in s for s in doc["summary"] if s["variant"] == "abstain")
    out = tmp_path / "exploratory" / "var"
    execute(write_cfg(tmp_path, cfg), out)
    assert "abstain: S1" in Path(build_report(out)["report_md"]).read_text()
    assert "variant" in (out / "metrics.csv").read_text().splitlines()[0]
    dup = copy.deepcopy(cfg)
    dup["variants"].append({"id": "primary"})
    with pytest.raises(SchemaError):
        run_config(dup)
    bad = copy.deepcopy(cfg)
    bad["variants"].append({"id": "x", "lambdas": [0.1]})
    with pytest.raises(SchemaError):
        validate_config(bad)


def test_frozen_confirmatory_configs_follow_the_amendments():
    for exp in ("EXP-001", "EXP-002", "EXP-003", "EXP-004"):
        cfg = load_config(REPO / "research" / "experiments" / exp / "config.json")
        assert cfg["experiment_id"] == exp and cfg["label"] == "confirmatory"
        assert cfg["seed_entropy"] == CONFIRMATORY_ENTROPY
        assert cfg["n_seeds"] == 30  # owner-approved amendment: 30 seeds
        for v in cfg.get("variants", [{}]):
            assert "DELIB" not in {**cfg, **v}.get("rules", [])  # DELIB dropped
        if cfg["kind"] == "aggregation":
            assert cfg["delib_budgets"] == []


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-003", "EXP-004"])
def test_real_frozen_configs_are_accepted_and_changed_ones_refused(exp, tmp_path):
    # Guard check only: no confirmatory run is executed here.
    path = REPO / "research" / "experiments" / exp / "config.json"
    cfg = load_config(path)
    check_confirmatory_allowed(cfg, REPO, path)
    changed = copy.deepcopy(cfg) | {"n_seeds": 29}
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(changed, REPO)
    changed_path = write_cfg(tmp_path, changed)
    with pytest.raises(ProtocolNotFrozen):
        check_confirmatory_allowed(load_config(changed_path), REPO, changed_path)
    # a CLI run of the changed config is refused (exit 3) and writes nothing
    assert cli.main(["run", "--config", str(changed_path), "--out", str(tmp_path / "o")]) == 3
    assert not (tmp_path / "o").exists()


def test_freeze_record_matches_registry_and_files():
    rec = json.loads((REPO / "research" / "freeze.json").read_text())
    assert hashlib.sha256((REPO / rec["main_protocol"]["path"]).read_bytes()).hexdigest() == rec["main_protocol"]["sha256"]
    import csv
    with (REPO / "research" / "experiment_registry.csv").open(newline="") as fh:
        reg = {r["exp_id"]: r for r in csv.DictReader(fh)}
    assert set(rec["experiments"]) == set(reg) == {"EXP-001", "EXP-002", "EXP-003", "EXP-004"}
    for exp, e in rec["experiments"].items():
        assert reg[exp]["protocol_sha256"] == e["protocol_sha256"]
        assert reg[exp]["status"] == "frozen (owner-approved 2026-11-24), not yet run"
        assert hashlib.sha256((REPO / e["protocol_path"]).read_bytes()).hexdigest() == e["protocol_sha256"]
        assert hashlib.sha256((REPO / e["config_path"]).read_bytes()).hexdigest() == e["config_file_sha256"]
    assert {r["scenario"] for run in rec["c4_disclosure"]["runs"] for r in run["primary_contrast_values"]} == {"S1", "S4"}

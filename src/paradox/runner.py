# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Experiment runner: config -> validated result document, metrics CSV and run
manifest. Simulation, metrics and serialization stay in their own modules;
this module only orchestrates them.

Guards (G-FREEZE): a config labelled ``confirmatory`` runs only if the
experiment's registry row carries a SHA-256 that matches its protocol file,
the protocol is no longer marked DRAFT, and the freeze record
(``research/freeze.json``) lists the experiment with the same protocol hash,
the current hash of ``research/protocol.md`` and the hash of this exact config
(canonical JSON, and the file bytes when the config comes from a file).
Exploratory configs must write under a path containing an ``exploratory``
component and may not use the confirmatory seed entropy.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from math import sqrt
from pathlib import Path

import numpy as np

from . import dependence, metrics, rules, stats, theory
from .generator import MAX_REASONERS, ModelParams, Scenario, derive_seeds, generate_run
from .manifest import build_manifest, git_revision, utc_now
from .schema import RESULT_SCHEMA_VERSION, SchemaError, sha256_json, validate_config, validate_result

__all__ = [
    "CONFIRMATORY_ENTROPY",
    "FREEZE_RECORD",
    "REPO_ROOT",
    "ProtocolNotFrozen",
    "GuardError",
    "load_config",
    "resolve_seeds",
    "check_confirmatory_allowed",
    "run_config",
    "execute",
]

CONFIRMATORY_ENTROPY = 20261124
REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_RECORD = Path("research") / "freeze.json"
CLAIMS_BOUNDARY = (
    "Synthetic reasoners, not LLMs or people. Values hold only within the stated simulation model. "
    "Exploratory results are not findings and do not test any preregistered hypothesis."
)


class GuardError(RuntimeError):
    pass


class ProtocolNotFrozen(GuardError):
    pass


def load_config(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file():
        raise SchemaError(f"config not found: {p}")
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaError(f"malformed JSON in {p}: {exc}") from exc
    return validate_config(cfg)


def resolve_seeds(cfg: dict) -> list[int]:
    derived = derive_seeds(cfg["seed_entropy"], cfg["n_seeds"])
    if "seeds" in cfg:
        if list(cfg["seeds"]) != derived:
            raise SchemaError("explicit seeds do not match SeedSequence(seed_entropy).spawn(n_seeds)")
    return derived


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_confirmatory_allowed(cfg: dict, repo_root: Path = REPO_ROOT, config_path: str | Path | None = None) -> None:
    """Raise ``ProtocolNotFrozen`` unless the experiment's protocol is frozen
    and ``cfg`` is the frozen confirmatory config of that experiment."""
    exp = cfg["experiment_id"]
    reg = repo_root / "research" / "experiment_registry.csv"
    if not reg.is_file():
        raise ProtocolNotFrozen(f"registry not found: {reg}")
    with reg.open(newline="", encoding="utf-8") as fh:
        rows = {r["exp_id"]: r for r in csv.DictReader(fh)}
    if exp not in rows:
        raise ProtocolNotFrozen(f"{exp} is not registered; confirmatory runs need a registered, frozen protocol")
    row = rows[exp]
    sha = row.get("protocol_sha256", "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ProtocolNotFrozen(f"{exp}: no protocol hash in the registry (protocol not frozen by the owner); refusing a confirmatory run")
    proto = repo_root / row["protocol_path"]
    if not proto.is_file():
        raise ProtocolNotFrozen(f"{exp}: protocol file missing: {proto}")
    data = proto.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise ProtocolNotFrozen(f"{exp}: protocol file hash differs from the registry hash; refusing")
    if b"DRAFT" in data[:2000]:
        raise ProtocolNotFrozen(f"{exp}: protocol is still marked DRAFT; refusing")
    if cfg["seed_entropy"] != CONFIRMATORY_ENTROPY:
        raise GuardError(f"confirmatory runs must use seed entropy {CONFIRMATORY_ENTROPY}")
    rec_path = repo_root / FREEZE_RECORD
    if not rec_path.is_file():
        raise ProtocolNotFrozen(f"freeze record not found: {rec_path}; refusing a confirmatory run")
    try:
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        main = rec["main_protocol"]
        entry = rec["experiments"][exp]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ProtocolNotFrozen(f"{exp}: not listed in a valid freeze record ({exc!r}); refusing") from exc
    main_path = repo_root / main["path"]
    if not main_path.is_file() or _sha256_file(main_path) != main["sha256"]:
        raise ProtocolNotFrozen(f"{main['path']} differs from its frozen hash; refusing")
    if entry.get("protocol_sha256") != sha or entry.get("protocol_path") != row["protocol_path"]:
        raise ProtocolNotFrozen(f"{exp}: registry and freeze record disagree on the protocol; refusing")
    if sha256_json(cfg) != entry.get("config_canonical_sha256"):
        raise ProtocolNotFrozen(f"{exp}: config differs from the frozen confirmatory config; refusing")
    if config_path is not None and _sha256_file(Path(config_path)) != entry.get("config_file_sha256"):
        raise ProtocolNotFrozen(f"{exp}: config file bytes differ from the frozen config file; refusing")


def _check_exploratory(cfg: dict, out_dir: Path | None) -> None:
    if cfg["seed_entropy"] == CONFIRMATORY_ENTROPY:
        raise GuardError("exploratory runs may not use the confirmatory seed entropy (held-out seeds)")
    if out_dir is not None and "exploratory" not in Path(out_dir).resolve().parts:
        raise GuardError("exploratory outputs must be written under a path with an 'exploratory' component")


def _fmt(x: float) -> str:
    return f"{x:g}".replace(".", "p").replace("-", "m")


# ---------------------------------------------------------------- aggregation

def _aggregation_record(sc: Scenario, lam: float, seed: int, cfg: dict, idx: int, variant: str | None = None) -> dict:
    t0 = time.perf_counter()
    params = ModelParams(lam=lam, w=cfg["w"], delta=cfg["delta"], tau=cfg["tau"], max_reasoners=MAX_REASONERS)
    d = generate_run(sc, params, cfg["n_items"], seed)
    tie_rule = cfg.get("tie_rule", "coin")
    base = rules.single(d)
    outs = [base]
    for rule in cfg["rules"]:
        if rule in ("MV", "CW", "SEQ"):
            outs += [rules.apply_rule(d, rule, b, tie_rule) for b in cfg["budgets"]]
        elif rule == "DELIB":
            outs += [rules.deliberation(d, b) for b in cfg["delib_budgets"]]
    rows, inv = [], {"vote_counts": True, "budget_accounting": True}
    for o in outs:
        m = metrics.rule_metrics(o)
        m["delta_vs_single"] = metrics.paired_delta(o.decision_correct, base.decision_correct)
        if not (o.n_votes == o.n_reasoners and np.all((o.votes_correct >= 0) & (o.votes_correct <= o.n_votes))):
            inv["vote_counts"] = False
        expected_calls = 2 * o.n_reasoners if o.rule == "DELIB" else o.n_reasoners
        if not (o.calls_per_item == expected_calls == o.budget):
            inv["budget_accounting"] = False
        rows.append(m)
    acc1 = float(d.correct[:, 0].mean())
    inv["marginal_competence_4se"] = abs(acc1 - sc.mu) <= 4 * sqrt(sc.mu * (1 - sc.mu) / cfg["n_items"]) + 1e-12
    failed = [k for k, v in inv.items() if not v]
    extra = {} if variant is None else {"variant": variant, "tie_rule": tie_rule, "w": cfg["w"], "tau": cfg["tau"]}
    return {
        **extra,
        "record_id": f"RUN-{idx:04d}",
        "scenario": sc.id,
        "lambda": lam,
        "seed": seed,
        "n_items": cfg["n_items"],
        "runtime_s": time.perf_counter() - t0,
        "invariants": inv,
        "excluded": bool(failed),
        "exclusion_reason": ("invariant failed: " + ", ".join(failed)) if failed else "",
        "metrics": rows,
    }


def _aggregation_summary(cfg: dict, records: list[dict]) -> list[dict]:
    scen = {s["id"]: s for s in cfg["scenarios"]}
    vorder = [v["id"] for v in cfg.get("variants", [])]
    groups: dict[tuple, list[dict]] = {}
    for r in records:
        if r["excluded"]:
            continue
        for m in r["metrics"]:
            groups.setdefault((r.get("variant"), r["scenario"], r["lambda"], m["rule"], m["budget"]), []).append(m)
    out = []
    order = lambda kv: (vorder.index(kv[0][0]) if kv[0][0] is not None else -1, kv[0][1], kv[0][2], rules.RULES.index(kv[0][3]), kv[0][4])  # noqa: E731
    for (var, sid, lam, rule, b), ms in sorted(groups.items(), key=order):
        row = {"scenario": sid, "lambda": lam, "rule": rule, "budget": b, "n_seeds": len(ms)}
        if var is not None:
            row["variant"] = var
        for key in ("accuracy", "delta_vs_single", "brier", "ece", "disagreement_share"):
            vals = [m[key] for m in ms]
            row[f"{key}_mean"] = float(np.mean(vals))
            row[f"{key}_per_seed"] = vals
        if len(ms) >= 2:
            s = stats.summarise([m["delta_vs_single"] for m in ms], n_resamples=10_000)
            row.update({f"delta_{k}": v for k, v in s.items() if k not in ("per_seed", "mean", "n_seeds")})
        s0 = scen[sid]
        if rule in ("MV", "SINGLE") and b % 2 == 1:
            row["accuracy_theory"] = theory.mixture(b, s0["p_easy"], s0["h"], s0["p_hard"], lam)
        out.append(row)
    # Holm family: MV and SEQ cells with budget >= 3. Without variants this is the
    # primary family (EXP-002). With variants (EXP-004) each variant gets its own
    # family and nothing is marked primary: EXP-004 is a robustness check.
    for var in ([None] if not vorder else vorder):
        fam = [i for i, r in enumerate(out) if r.get("variant") == var and r["rule"] in ("MV", "SEQ") and r["budget"] >= 3
               and "delta_p_one_sided_negative" in r]
        if fam:
            adj = stats.holm([out[i]["delta_p_one_sided_negative"] for i in fam])
            for i, a in zip(fam, adj):
                out[i]["delta_p_holm"] = a
                if var is None:
                    out[i]["primary_family"] = True
    return out


def _variant_configs(cfg: dict) -> list[tuple[str | None, dict]]:
    if "variants" not in cfg:
        return [(None, cfg)]
    ids = [v["id"] for v in cfg["variants"]]
    if len(set(ids)) != len(ids):
        raise SchemaError("variant ids must be unique")
    return [(v["id"], {**cfg, **{k: val for k, val in v.items() if k not in ("id", "description")}}) for v in cfg["variants"]]


def _run_aggregation(cfg: dict, seeds: list[int]) -> tuple[list[dict], list[dict]]:
    records, idx = [], 1
    for var, vcfg in _variant_configs(cfg):
        for s in vcfg["scenarios"]:
            sc = Scenario(s["id"], s["p_easy"], s["h"], s["p_hard"])
            for lam in vcfg["lambdas"]:
                for seed in seeds:
                    records.append(_aggregation_record(sc, float(lam), seed, vcfg, idx, var))
                    idx += 1
    return records, _aggregation_summary(cfg, records)


# ----------------------------------------------------------------- validation

GOLDEN = [
    ("bahadur_mv", (3, 0.55, 0.4), 0.54505, 1e-9),
    ("bahadur_mv", (5, 0.55, 0.4), 0.5196194, 5e-8),
    ("condorcet", (3, 0.55), 0.57475, 1e-9),
    ("condorcet", (5, 0.55), 0.5931269, 5e-8),
]


def _cell(idx, model, params, n, k_correct_total, n_total, per_seed, a_theory, tol):
    a_sim = k_correct_total / n_total
    se = sqrt(a_theory * (1 - a_theory) / n_total)
    diff = a_sim - a_theory
    ok = abs(diff) <= tol * se if se > 0 else diff == 0
    return {
        "record_id": f"CELL-{idx:04d}", "model": model, "params": params, "n": n, "n_items_total": n_total,
        "accuracy_sim": a_sim, "accuracy_theory": a_theory, "se_mc": se, "z": (diff / se) if se > 0 else 0.0,
        "pass": bool(ok), "per_seed_accuracy": per_seed, "excluded": False, "exclusion_reason": "",
    }


def _run_validation(cfg: dict, seeds: list[int]) -> tuple[list[dict], list[dict]]:
    ns = [n for n in cfg["ns"] if n % 2 == 1]
    N, tol = cfg["items_per_seed"], cfg["tolerance_se"]
    records, idx = [], 1
    jobs = [("common_shock", Scenario("V", p_easy=p), lam) for p in cfg["common_shock"]["ps"] for lam in cfg["common_shock"]["lambdas"]]
    jobs += [("mixture", Scenario(s["id"], s["p_easy"], s["h"], s["p_hard"]), lam) for s in cfg["mixture"]["scenarios"] for lam in cfg["mixture"]["lambdas"]]
    for model, sc, lam in jobs:
        per = {n: [] for n in ns}
        for seed in seeds:
            d = generate_run(sc, ModelParams(lam=lam), N, seed)
            for n in ns:
                per[n].append(metrics.accuracy(rules.majority(d, n).decision_correct))
        for n in ns:
            if model == "common_shock":
                name = "independent" if lam == 0 else ("perfect_correlation" if lam == 1 else "common_shock")
                a_th = theory.common_shock(n, sc.p_easy, lam)
                prm = {"p": sc.p_easy, "lambda": lam}
            else:
                name, a_th = "mixture", theory.mixture(n, sc.p_easy, sc.h, sc.p_hard, lam)
                prm = {"scenario": sc.id, "p_easy": sc.p_easy, "h": sc.h, "p_hard": sc.p_hard, "lambda": lam}
            k_total = round(sum(a * N for a in per[n]))
            records.append(_cell(idx, name, prm, n, k_total, N * len(seeds), per[n], a_th, tol))
            idx += 1
    for p in cfg["bahadur"]["ps"]:
        for c in cfg["bahadur"]["cs"]:
            for n in ns:
                prm = {"p": p, "c": c}
                if not (0 < p < 1) or not theory.bahadur_admissible(n, p, c):
                    records.append({"record_id": f"CELL-{idx:04d}", "model": "bahadur", "params": prm, "n": n, "excluded": True,
                                    "exclusion_reason": "inadmissible Bahadur cell (negative profile probability)", "pass": None})
                    idx += 1
                    continue
                per = []
                for seed in seeds:
                    k = dependence.sample_k("bahadur", n, p, c, N, seed)
                    per.append(float(np.mean(2 * k > n)))
                a_th = theory.bahadur_mv(n, p, c)
                records.append(_cell(idx, "bahadur", prm, n, round(sum(a * N for a in per)), N * len(seeds), per, a_th, tol))
                idx += 1
    summary = []
    for fn, args, expected, tol_abs in GOLDEN:
        got = getattr(theory, fn)(*args)
        summary.append({"check": f"golden {fn}{args}", "expected": expected, "got": got, "abs_tol": tol_abs, "pass": abs(got - expected) <= tol_abs})
    run_cells = [r for r in records if not r["excluded"]]
    summary.append({
        "check": "monte_carlo_cells", "n_cells": len(run_cells), "n_excluded": len(records) - len(run_cells),
        "n_fail": sum(not r["pass"] for r in run_cells), "max_abs_z": max(abs(r["z"]) for r in run_cells) if run_cells else None,
        "tolerance_se": tol, "pass": all(r["pass"] for r in run_cells),
    })
    return records, summary


# ----------------------------------------------------------------- dependence

def _run_dependence(cfg: dict, seeds: list[int]) -> tuple[list[dict], list[dict]]:
    N = cfg["items_per_seed"]
    records, idx = [], 1
    for p in cfg["ps"]:
        for r in cfg["rs"]:
            for n in cfg["ns"]:
                for model in cfg["models"]:
                    rec = {"record_id": f"CELL-{idx:04d}", "model": model, "p": p, "r": r, "n": n}
                    idx += 1
                    try:
                        rec["params"] = dependence.model_parameters(model, p, r)
                        a_th = dependence.analytic_mv(model, n, p, r)
                    except ValueError as exc:
                        rec.update({"excluded": True, "exclusion_reason": f"inadmissible: {exc}"})
                        records.append(rec)
                        continue
                    per = [float(np.mean(2 * dependence.sample_k(model, n, p, r, N, s) > n)) - p for s in seeds]
                    rec.update({"excluded": False, "exclusion_reason": "", "delta_theory": a_th - p, "delta_mc_per_seed": per,
                                "delta_mc_mean": float(np.mean(per))})
                    if len(per) >= 2:
                        rec["delta_mc_t95"] = list(stats.t_interval(per))
                    records.append(rec)
    summary = []
    keys = sorted({(r["p"], r["r"], r["n"]) for r in records})
    for key in keys:
        cell = [r for r in records if (r["p"], r["r"], r["n"]) == key and not r["excluded"]]
        signs = {r["model"]: int(np.sign(round(r["delta_theory"], 12))) for r in cell}
        summary.append({"p": key[0], "r": key[1], "n": key[2], "analytic_signs": signs, "signs_agree": len(set(signs.values())) <= 1})
    return records, summary


# ------------------------------------------------------------------ execution

def run_config(cfg: dict) -> dict:
    """Run a validated config and return a validated result document (no I/O)."""
    seeds = resolve_seeds(cfg)
    runner = {"aggregation": _run_aggregation, "validation": _run_validation, "dependence": _run_dependence}[cfg["kind"]]
    records, summary = runner(cfg, seeds)
    doc = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "experiment_id": cfg["experiment_id"],
        "label": cfg["label"],
        "kind": cfg["kind"],
        "created_utc": utc_now(),
        "config": cfg,
        "config_sha256": sha256_json(cfg),
        "code_revision": git_revision(),
        "seeds": seeds,
        "records": records,
        "summary": summary,
        "claims_boundary": CLAIMS_BOUNDARY,
    }
    return validate_result(json.loads(json.dumps(doc, allow_nan=False)))


def _write_metrics_csv(doc: dict, path: Path) -> None:
    if doc["kind"] == "aggregation":
        fields = ["record_id", "variant", "scenario", "lambda", "seed", "excluded", "rule", "budget", "n_reasoners", "calls_per_item",
                  "messages_per_item", "accuracy", "delta_vs_single", "brier", "ece", "disagreement_share",
                  "pairwise_disagreement", "accuracy_per_call", "tie_share"]
        rows = [{**{k: r.get(k, "") for k in ("record_id", "variant", "scenario", "lambda", "seed", "excluded")}, **m}
                for r in doc["records"] for m in r["metrics"]]
    elif doc["kind"] == "validation":
        fields = ["record_id", "model", "params", "n", "excluded", "accuracy_sim", "accuracy_theory", "se_mc", "z", "pass"]
        rows = [{**r, "params": json.dumps(r["params"], sort_keys=True)} for r in doc["records"]]
    else:
        fields = ["record_id", "model", "p", "r", "n", "excluded", "delta_theory", "delta_mc_mean"]
        rows = doc["records"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def execute(config_path: str | Path, out_dir: str | Path, command: list[str] | None = None, repo_root: Path = REPO_ROOT) -> dict:
    """Validate guards, run, and write ``results.json``, ``metrics.csv`` and
    ``run_manifest.json`` into ``out_dir``. Returns the manifest."""
    cfg = load_config(config_path)
    out = Path(out_dir)
    if cfg["label"] == "confirmatory":
        check_confirmatory_allowed(cfg, repo_root, config_path)
    else:
        _check_exploratory(cfg, out)
    started, t0 = utc_now(), time.perf_counter()
    doc = run_config(cfg)
    runtime = time.perf_counter() - t0
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(doc, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    _write_metrics_csv(doc, out / "metrics.csv")
    per = {r["record_id"]: r["runtime_s"] for r in doc["records"] if "runtime_s" in r}
    manifest = build_manifest(
        experiment_id=cfg["experiment_id"], label=cfg["label"], config_sha256=doc["config_sha256"], seeds=doc["seeds"],
        command=command or [], started_utc=started, finished_utc=utc_now(), runtime_s=runtime, per_record_runtime_s=per,
        outputs={name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in ("results.json", "metrics.csv")},
    )
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return manifest

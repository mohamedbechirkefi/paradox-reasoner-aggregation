# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M3 confirmatory analysis: applies the frozen decision rules of protocol v1.0
to validated result documents, and writes provenance tables, SHA-256 manifests,
summary tables and figures with uncertainty.

Written and tested before any confirmatory output existed (M3, 2026-11-25).
Operational readings of the frozen rules, where the protocol text leaves a
detail implicit, are fixed here and recorded in decision D-011:

- EXP-002 H0. "Holm-adjusted one-sided 95% upper confidence bound below 0" is
  applied as Holm's step-down procedure on the one-sided t-test p-values that
  the runner stores (``delta_p_holm < 0.05``). At step ``k`` the one-sided
  upper bound at level ``0.05 / (m - k)`` lies below 0 exactly when the raw
  p-value is below that level, so the two statements coincide.
- P1 to P3. "Lower bound" and "upper bound" are the seed-level two-sided t 95%
  interval of protocol section 5, unadjusted (the predictions are not in the
  Holm family). P2 uses the per-seed paired difference ``Delta_SEQ - Delta_MV``.
  P3 compares consecutive ``lambda`` levels at fixed ``B >= 3`` with the
  per-seed paired difference ``Delta(lambda_{k+1}) - Delta(lambda_k)``.
- EXP-003. Sign agreement is judged on the exact analytic values (all four
  models have closed forms); Monte Carlo intervals are a check on them.
- EXP-004. "Significant (Holm)" EXP-002 cells are primary-family cells with
  ``delta_p_holm < 0.05`` (significant degradation, the family is one-sided).
  A sign is reversed when the variant's t 95% interval for the same cell lies
  above 0. For the tie factor, whose even budgets do not exist in EXP-002, the
  reference is the primary tie level (``tie_coin``) with its own Holm family.

Everything else in the outputs is descriptive and labelled so.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from math import sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import stats, theory  # noqa: E402
from .schema import load_result  # noqa: E402

__all__ = [
    "ALPHA",
    "sha256_file",
    "write_sha256_manifest",
    "provenance_rows",
    "write_provenance",
    "analyse_exp001",
    "analyse_exp002",
    "analyse_exp003",
    "analyse_exp004",
    "main",
]

ALPHA = 0.05
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_MANIFEST = REPO_ROOT / "data" / "manifest.json"


# ------------------------------------------------------------ hashes and provenance

def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_sha256_manifest(results_dir: str | Path, name: str = "sha256_manifest.json") -> dict:
    """SHA-256 and size of every file under ``results_dir`` except the manifest itself."""
    d = Path(results_dir)
    files = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.name != name:
            files[p.relative_to(d).as_posix()] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    doc = {"directory": d.as_posix(), "files": files}
    (d / name).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return doc


def provenance_rows(doc: dict, manifest: dict, exit_status: int | None, data_manifest_sha256: str) -> list[dict]:
    """One row per record (run or validation cell). Start and end times are those
    of the process that produced all records; ``record_runtime_s`` is per record
    where the runner measured it."""
    env = manifest["environment"]
    hw = f"{env['cpu']}; {env['machine']}; {env['os']}"
    seeds = doc["seeds"]
    rows = []
    for r in doc["records"]:
        if "seed" in r:
            seed = str(r["seed"])
        else:
            seed = f"all {len(seeds)} seeds of results.json (pooled cell)"
        rows.append({
            "run_id": r["record_id"],
            "experiment_id": doc["experiment_id"],
            "variant": r.get("variant", ""),
            "config_sha256": doc["config_sha256"],
            "seed": seed,
            "code_revision": doc["code_revision"],
            "data_manifest_sha256": data_manifest_sha256,
            "hardware": hw,
            "process_started_utc": manifest["started_utc"],
            "process_finished_utc": manifest["finished_utc"],
            "record_runtime_s": r.get("runtime_s", ""),
            "excluded": r.get("excluded", False),
            "exclusion_reason": r.get("exclusion_reason", ""),
            "process_exit_status": "" if exit_status is None else exit_status,
        })
    return rows


def write_provenance(results_dir: Path, exit_status: int | None) -> Path:
    doc = load_result(results_dir / "results.json")
    man = json.loads((results_dir / "run_manifest.json").read_text(encoding="utf-8"))
    rows = provenance_rows(doc, man, exit_status, sha256_file(DATA_MANIFEST))
    path = results_dir / "provenance.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return path


# ------------------------------------------------------------------- helpers

def _per_seed(doc: dict, variant=None) -> dict:
    """{(scenario, lambda, rule, budget): {seed: delta}} from non-excluded records."""
    out: dict = {}
    for r in doc["records"]:
        if r["excluded"] or r.get("variant") != variant:
            continue
        for m in r["metrics"]:
            out.setdefault((r["scenario"], r["lambda"], m["rule"], m["budget"]), {})[r["seed"]] = m["delta_vs_single"]
    return out


def _paired(a: dict, b: dict) -> list[float]:
    """Per-seed ``a - b`` over the seeds both contain, in sorted seed order."""
    seeds = sorted(set(a) & set(b))
    return [a[s] - b[s] for s in seeds]


def _t95(x) -> tuple[float, float] | None:
    x = list(x)
    if len(x) < 2:
        return None
    if np.std(x, ddof=1) == 0:
        m = float(np.mean(x))
        return (m, m)
    return stats.t_interval(x)


def _side(ci) -> str:
    if ci is None:
        return "n/a"
    lo, hi = ci
    return "above 0" if lo > 0 else ("below 0" if hi < 0 else "includes 0")


def _f(x, nd=4) -> str:
    return "" if x is None else f"{x:.{nd}f}"


# ------------------------------------------------------------------- EXP-001

def analyse_exp001(doc: dict) -> dict:
    golden = [s for s in doc["summary"] if "expected" in s]
    mc = [s for s in doc["summary"] if s.get("check") == "monte_carlo_cells"][0]
    excluded = [r for r in doc["records"] if r["excluded"]]
    run = [r for r in doc["records"] if not r["excluded"]]
    by_model: dict = {}
    for r in run:
        b = by_model.setdefault(r["model"], {"cells": 0, "fail": 0, "max_abs_z": 0.0})
        b["cells"] += 1
        b["fail"] += int(not r["pass"])
        b["max_abs_z"] = max(b["max_abs_z"], abs(r["z"]))
    passed = all(g["pass"] for g in golden) and mc["pass"]
    return {
        "experiment_id": "EXP-001",
        "decision_rule": "H0 (engine correct) holds if every admissible cell has |A_sim - A_theory| <= 4 SE_MC and every golden fixture is reproduced",
        "golden": golden,
        "n_cells_run": len(run),
        "n_cells_excluded": len(excluded),
        "n_cells_fail": mc["n_fail"],
        "max_abs_z": mc["max_abs_z"],
        "n_abs_z_above_2": sum(abs(r["z"]) > 2 for r in run),
        "n_abs_z_above_3": sum(abs(r["z"]) > 3 for r in run),
        "by_model": by_model,
        "excluded_cells": [{"record_id": r["record_id"], "params": r["params"], "n": r["n"]} for r in excluded],
        "verdict": "PASS: engine validated; the stop rule allows EXP-002 to EXP-004" if passed else
                   "FAIL: stop rule; EXP-002 to EXP-004 must not start",
        "pass": passed,
    }


# ------------------------------------------------------------------- EXP-002

def _holm_steps(rows: list[dict]) -> None:
    """Annotate primary-family rows with the Holm step level and the one-sided
    upper bound at that level (descriptive companion of ``delta_p_holm``)."""
    m = len(rows)
    order = sorted(range(m), key=lambda i: rows[i]["p_raw"])
    for k, i in enumerate(order):
        r = rows[i]
        level = ALPHA / (m - k)
        x = r["_per_seed"]
        se = np.std(x, ddof=1) / sqrt(len(x))
        r["holm_step"] = k + 1
        r["holm_level"] = level
        r["holm_upper_bound"] = float(np.mean(x) + stats.t_quantile(1 - level, len(x) - 1) * se) if se > 0 else float(np.mean(x))


def analyse_exp002(doc: dict) -> dict:
    cfg = doc["config"]
    scen = {s["id"]: s for s in cfg["scenarios"]}
    ps = _per_seed(doc)
    summ = {(s["scenario"], s["lambda"], s["rule"], s["budget"]): s for s in doc["summary"] if "variant" not in s}
    fam = []
    for key, s in summ.items():
        if s.get("primary_family"):
            fam.append({"scenario": key[0], "lambda": key[1], "rule": key[2], "budget": key[3], "n_seeds": s["n_seeds"],
                        "delta_mean": s["delta_vs_single_mean"], "t95": [s["delta_t95_low"], s["delta_t95_high"]],
                        "boot95": [s["delta_boot95_low"], s["delta_boot95_high"]],
                        "p_raw": s["delta_p_one_sided_negative"], "p_holm": s["delta_p_holm"],
                        "_per_seed": [ps[key][k] for k in sorted(ps[key])]})
    _holm_steps(fam)
    for r in fam:
        r["reject_no_degradation"] = r["p_holm"] < ALPHA
        del r["_per_seed"]
    rejected = [r for r in fam if r["reject_no_degradation"]]

    # P1: MV at lambda 0, B 31
    p1 = []
    for sid, s in scen.items():
        key = (sid, 0.0, "MV", 31)
        if key not in summ:
            continue
        pred_neg = theory.predicted_mv_degrades(s["p_easy"], s["h"], s["p_hard"])
        ci = (summ[key]["delta_t95_low"], summ[key]["delta_t95_high"])
        if pred_neg:
            status = "disconfirmed" if ci[0] > 0 else ("supported" if ci[1] < 0 else "not disconfirmed (interval includes 0)")
        else:
            status = "disconfirmed" if ci[1] < 0 else ("supported" if ci[0] > 0 else "not disconfirmed (interval includes 0)")
        p1.append({"scenario": sid, "predicted": "degradation" if pred_neg else "gain", "delta_mean": summ[key]["delta_vs_single_mean"],
                   "t95": list(ci), "accuracy_theory_mv": summ[key].get("accuracy_theory"),
                   "accuracy_theory_single": summ.get((sid, 0.0, "SINGLE", 1), {}).get("accuracy_theory"), "status": status})

    # P2: SEQ - MV at lambda 0, every B >= 3
    p2 = []
    for sid in scen:
        for b in cfg["budgets"]:
            if b < 3 or (sid, 0.0, "SEQ", b) not in ps:
                continue
            d = _paired(ps[(sid, 0.0, "SEQ", b)], ps[(sid, 0.0, "MV", b)])
            ci = _t95(d)
            status = "disconfirmed" if ci[0] > 0 else ("supported" if ci[1] < 0 else "not disconfirmed (interval includes 0)")
            p2.append({"scenario": sid, "budget": b, "diff_mean": float(np.mean(d)), "t95": list(ci), "n_seeds": len(d), "status": status})

    # P3: homogeneous scenarios, consecutive lambda, fixed B >= 3
    p3 = []
    lams = sorted(cfg["lambdas"])
    for sid, s in scen.items():
        if s["h"] != 0:
            continue
        for b in cfg["budgets"]:
            if b < 3:
                continue
            for l0, l1 in zip(lams, lams[1:]):
                d = _paired(ps[(sid, float(l1), "MV", b)], ps[(sid, float(l0), "MV", b)])
                ci = _t95(d)
                status = "disconfirmed" if ci[0] > 0 else ("supported" if ci[1] < 0 else "not disconfirmed (interval includes 0)")
                p3.append({"scenario": sid, "budget": b, "lambda_from": l0, "lambda_to": l1, "diff_mean": float(np.mean(d)),
                           "t95": list(ci), "n_seeds": len(d), "status": status})

    def verdict(rows):
        n_dis = sum(r["status"] == "disconfirmed" for r in rows)
        n_sup = sum(r["status"] == "supported" for r in rows)
        return {"n_tests": len(rows), "n_disconfirmed": n_dis, "n_supported": n_sup, "n_inconclusive": len(rows) - n_dis - n_sup,
                "verdict": "disconfirmed" if n_dis else "not disconfirmed"}

    cw = [{"scenario": k[0], "lambda": k[1], "budget": k[3], "delta_mean": s["delta_vs_single_mean"],
           "t95": [s.get("delta_t95_low"), s.get("delta_t95_high")]} for k, s in summ.items() if k[2] == "CW" and k[3] >= 3]
    n_runs = len(doc["records"])
    n_ex = sum(r["excluded"] for r in doc["records"])
    return {
        "experiment_id": "EXP-002",
        "n_runs": n_runs,
        "n_excluded": n_ex,
        "decision_rule": "H0 (no MV or SEQ cell degrades) is rejected if at least one cell has a Holm-adjusted one-sided 95% upper bound below 0 (family: all MV and SEQ cells with B >= 3)",
        "family_size": len(fam),
        "n_rejected": len(rejected),
        "h0_rejected": bool(rejected),
        "verdict": ("H0 rejected: degradation exists in at least one cell (H1)" if rejected else
                    "H0 not rejected: no cell shows significant degradation (this is not evidence of equivalence)"),
        "rejected_cells": sorted(({k: r[k] for k in ("scenario", "lambda", "rule", "budget", "delta_mean", "t95", "p_holm", "holm_upper_bound")}
                                  for r in rejected), key=lambda r: (r["scenario"], r["lambda"], r["rule"], r["budget"])),
        "primary_family": sorted(fam, key=lambda r: (r["scenario"], r["lambda"], r["rule"], r["budget"])),
        "P1": {**verdict(p1), "cells": p1},
        "P2": {**verdict(p2), "cells": p2},
        "P3": {**verdict(p3), "cells": p3},
        "CW_descriptive": cw,
    }


# ------------------------------------------------------------------- EXP-003

def analyse_exp003(doc: dict) -> dict:
    recs = doc["records"]
    run = [r for r in recs if not r["excluded"]]
    disagree = [s for s in doc["summary"] if not s["signs_agree"]]
    mc_outside = []
    mc_sign = []
    for r in run:
        ci = r.get("delta_mc_t95")
        if ci is not None and not (ci[0] <= r["delta_theory"] <= ci[1]):
            mc_outside.append({"record_id": r["record_id"], "model": r["model"], "p": r["p"], "r": r["r"], "n": r["n"],
                               "delta_theory": r["delta_theory"], "mc_t95": ci})
        mc_sign.append(_side(ci))
    deg = [{"model": r["model"], "p": r["p"], "r": r["r"], "n": r["n"], "delta_theory": r["delta_theory"]} for r in run if r["delta_theory"] < 0]
    count_by_model: dict = {}
    for r in run:
        c = count_by_model.setdefault(r["model"], {"cells": 0, "negative": 0, "zero": 0, "positive": 0})
        c["cells"] += 1
        sgn = int(np.sign(round(r["delta_theory"], 12)))
        c[{-1: "negative", 0: "zero", 1: "positive"}[sgn]] += 1
    return {
        "experiment_id": "EXP-003",
        "decision_rule": "H0 (the sign of Delta_MV at matched (p, r, n) is the same across the four models in every admissible cell) is rejected in favour of H1 if the signs differ in at least one cell",
        "n_model_cells": len(recs),
        "n_model_cells_run": len(run),
        "n_model_cells_excluded": len(recs) - len(run),
        "n_matched_cells": len(doc["summary"]),
        "n_matched_cells_disagree": len(disagree),
        "h0_rejected": bool(disagree),
        "verdict": ("H1: the sign of Delta_MV depends on the dependence model in at least one matched cell" if disagree else
                    "H0 retained: all models agree in sign in every admissible matched cell"),
        "disagreeing_cells": disagree,
        "sign_counts_by_model": count_by_model,
        "negative_cells": deg,
        "mc_check": {"n_cells_with_interval": sum(r.get("delta_mc_t95") is not None for r in run),
                     "n_analytic_outside_mc_t95": len(mc_outside), "cells": mc_outside,
                     "mc_interval_sides": {k: mc_sign.count(k) for k in sorted(set(mc_sign))}},
    }


# ------------------------------------------------------------------- EXP-004

def analyse_exp004(doc: dict, exp002: dict) -> dict:
    cfg = doc["config"]
    scen_ids = {s["id"] for s in cfg["scenarios"]}
    lams = {float(x) for x in cfg["lambdas"]}
    summ = {(s.get("variant"), s["scenario"], s["lambda"], s["rule"], s["budget"]): s for s in doc["summary"]}
    s002 = {(s["scenario"], s["lambda"], s["rule"], s["budget"]): s for s in exp002["summary"]}
    sig = [k for k, s in s002.items() if s.get("primary_family") and s["delta_p_holm"] < ALPHA and k[0] in scen_ids and k[1] in lams]

    # consistency: primary variant reproduces EXP-002 per seed
    p002, pprim = _per_seed(exp002), _per_seed(doc, "primary")
    diffs = [abs(pprim[k][s] - p002[k][s]) for k in pprim if k in p002 for s in pprim[k] if s in p002[k]]
    consistency = {"n_values_compared": len(diffs), "max_abs_diff": max(diffs) if diffs else None,
                   "identical": bool(diffs) and max(diffs) == 0.0}

    rows = []
    for v in cfg["variants"]:
        vid = v["id"]
        if vid in ("primary", "tie_coin", "tie_abstain_wrong"):
            continue
        for k in sig:
            s = summ.get((vid, *k))
            if s is None:
                continue
            ci = (s["delta_t95_low"], s["delta_t95_high"])
            rows.append({"factor_level": vid, "scenario": k[0], "lambda": k[1], "rule": k[2], "budget": k[3],
                         "exp002_delta": s002[k]["delta_vs_single_mean"], "variant_delta": s["delta_vs_single_mean"],
                         "variant_t95": list(ci), "side": _side(ci), "reversed": ci[0] > 0})
    # tie factor: reference is the primary tie level (tie_coin) with its own Holm family
    tie_ref = [k[1:] for k, s in summ.items() if k[0] == "tie_coin" and s.get("delta_p_holm") is not None and s["delta_p_holm"] < ALPHA]
    for k in tie_ref:
        s = summ[("tie_abstain_wrong", *k)]
        ci = (s["delta_t95_low"], s["delta_t95_high"])
        rows.append({"factor_level": "tie_abstain_wrong (reference tie_coin)", "scenario": k[0], "lambda": k[1], "rule": k[2], "budget": k[3],
                     "exp002_delta": summ[("tie_coin", *k)]["delta_vs_single_mean"], "variant_delta": s["delta_vs_single_mean"],
                     "variant_t95": list(ci), "side": _side(ci), "reversed": ci[0] > 0})
    reversed_ = [r for r in rows if r["reversed"]]

    # descriptive: sign of the mean for every MV/SEQ cell, every variant, against the variant's reference
    desc = []
    for (var, sid, lam, rule, b), s in summ.items():
        if rule not in ("MV", "SEQ") or b < 2 or var in ("primary",):
            continue
        ref = summ.get(("tie_coin", sid, lam, rule, b)) if var == "tie_abstain_wrong" else (
            None if var == "tie_coin" else summ.get(("primary", sid, lam, rule, b)))
        if ref is None:
            continue
        desc.append({"variant": var, "scenario": sid, "lambda": lam, "rule": rule, "budget": b,
                     "reference_delta": ref["delta_vs_single_mean"], "variant_delta": s["delta_vs_single_mean"],
                     "variant_t95": [s.get("delta_t95_low"), s.get("delta_t95_high")],
                     "mean_sign_changed": np.sign(round(ref["delta_vs_single_mean"], 12)) != np.sign(round(s["delta_vs_single_mean"], 12))})

    # cost accounting (descriptive): SEQ accuracy against calls plus messages, primary variant
    cost = []
    for (var, sid, lam, rule, b), s in summ.items():
        if var != "primary" or rule not in ("MV", "SEQ"):
            continue
        msgs = [m["messages_per_item"] for r in doc["records"] if r.get("variant") == "primary" and r["scenario"] == sid and r["lambda"] == lam
                for m in r["metrics"] if m["rule"] == rule and m["budget"] == b]
        cost.append({"scenario": sid, "lambda": lam, "rule": rule, "calls": b, "messages_per_item": float(np.mean(msgs)),
                     "calls_plus_messages": b + float(np.mean(msgs)), "accuracy": s["accuracy_mean"]})
    return {
        "experiment_id": "EXP-004",
        "optional": True,
        "n_runs": len(doc["records"]),
        "n_excluded": sum(r["excluded"] for r in doc["records"]),
        "decision_rule": "H0 (for every factor level, the sign of Delta_r in each Holm-significant EXP-002 cell is unchanged) is rejected in favour of H1 if any factor level reverses a sign",
        "n_significant_exp002_cells_in_scope": len(sig),
        "n_tie_reference_cells": len(tie_ref),
        "n_checks": len(rows),
        "n_reversed": len(reversed_),
        "h0_rejected": bool(reversed_),
        "verdict": ("H1: at least one factor level reverses a sign (reported as a limitation of EXP-002)" if reversed_ else
                    "H0 retained: no factor level reverses the sign of any Holm-significant cell"),
        "checks": rows,
        "primary_consistency_with_exp002": consistency,
        "descriptive_mean_sign_changes": [r for r in desc if r["mean_sign_changed"]],
        "n_descriptive_comparisons": len(desc),
        "cost_descriptive": cost,
    }


# ------------------------------------------------------------------- figures

def _fig_exp002(doc: dict, figs: Path) -> list[str]:
    cfg = doc["config"]
    summ = [s for s in doc["summary"] if "variant" not in s]
    sids = [s["id"] for s in cfg["scenarios"]]
    lams = cfg["lambdas"]
    fig, axes = plt.subplots(len(sids), len(lams), figsize=(2.6 * len(lams), 2.1 * len(sids)), sharex=True, squeeze=False)
    style = {"MV": ("#1b6ca8", "s", -0.04), "CW": ("#2a9d8f", "^", 0.0), "SEQ": ("#c0392b", "v", 0.04)}
    for i, sid in enumerate(sids):
        for j, lam in enumerate(lams):
            ax = axes[i][j]
            for rule, (col, mk, off) in style.items():
                pts = sorted((s["budget"], s["delta_vs_single_mean"], s["delta_t95_low"], s["delta_t95_high"])
                             for s in summ if s["scenario"] == sid and s["lambda"] == lam and s["rule"] == rule and s["budget"] >= 3)
                if not pts:
                    continue
                b, m, lo, hi = map(np.array, zip(*pts))
                x = b * 2 ** off
                ax.errorbar(x, m, yerr=[m - lo, hi - m], color=col, marker=mk, ms=3, lw=1, capsize=2, label=rule)
            ax.axhline(0, color="#222222", lw=0.8, ls="--")
            ax.set_xscale("log", base=2)
            ax.set_title(f"{sid}, lambda = {lam:g}", fontsize=8)
            ax.tick_params(labelsize=6)
            if j == 0:
                ax.set_ylabel("Delta accuracy vs SINGLE", fontsize=7)
            if i == len(sids) - 1:
                ax.set_xlabel("calls per item B", fontsize=7)
    axes[0][0].legend(fontsize=6, frameon=False)
    fig.suptitle(f"EXP-002: paired Delta = A_rule(B) - A_SINGLE, mean over {len(doc['seeds'])} seeds with seed-level t 95% intervals", fontsize=8)
    fig.tight_layout()
    p = figs / "FIG-002-1_delta_vs_budget.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return [p.name]


def _fig_exp003(doc: dict, figs: Path) -> list[str]:
    cfg = doc["config"]
    recs = [r for r in doc["records"] if not r["excluded"]]
    ps, rs = cfg["ps"], cfg["rs"]
    fig, axes = plt.subplots(len(ps), len(rs), figsize=(2.6 * len(rs), 2.2 * len(ps)), sharex=True, squeeze=False)
    style = {"common_shock": ("#1b6ca8", "s", -0.06), "bahadur": ("#c0392b", "v", -0.02), "mixture": ("#2a9d8f", "^", 0.02), "beta": ("#8e6c8a", "D", 0.06)}
    for i, p in enumerate(ps):
        for j, r in enumerate(rs):
            ax = axes[i][j]
            for model, (col, mk, off) in style.items():
                pts = sorted((x["n"], x["delta_theory"], *x["delta_mc_t95"]) for x in recs if x["p"] == p and x["r"] == r and x["model"] == model)
                if not pts:
                    continue
                n, th, lo, hi = map(np.array, zip(*pts))
                ax.plot(n * 2 ** off, th, color=col, marker=mk, ms=3, lw=1, label=model)
                mid = (lo + hi) / 2
                ax.errorbar(n * 2 ** off, mid, yerr=[mid - lo, hi - mid], color=col, lw=0, elinewidth=1, capsize=2)
            ax.axhline(0, color="#222222", lw=0.8, ls="--")
            ax.set_xscale("log", base=2)
            ax.set_title(f"p = {p}, r = {r}", fontsize=8)
            ax.tick_params(labelsize=6)
            if j == 0:
                ax.set_ylabel("Delta_MV = A_MV(n) - p", fontsize=7)
            if i == len(ps) - 1:
                ax.set_xlabel("group size n", fontsize=7)
    axes[0][0].legend(fontsize=6, frameon=False)
    fig.suptitle(f"EXP-003: exact Delta_MV (markers and lines) and Monte Carlo seed-level t 95% intervals (bars), {len(doc['seeds'])} seeds", fontsize=8)
    fig.tight_layout()
    p_ = figs / "FIG-003-1_delta_by_model.png"
    fig.savefig(p_, dpi=150)
    plt.close(fig)
    return [p_.name]


def _fig_exp004(doc: dict, figs: Path) -> list[str]:
    summ = [s for s in doc["summary"] if s["rule"] in ("MV", "SEQ") and s["budget"] >= 2]
    names = []
    variants = [v["id"] for v in doc["config"]["variants"] if v["id"] not in ("tie_coin", "tie_abstain_wrong")]
    cells = sorted({(s["scenario"], s["lambda"]) for s in summ})
    for rule in ("MV", "SEQ"):
        fig, axes = plt.subplots(len(cells) // 2 + len(cells) % 2, 2, figsize=(7.2, 2.2 * (len(cells) // 2 + len(cells) % 2)), squeeze=False, sharex=True)
        for ax, (sid, lam) in zip(axes.flat, cells):
            for k, vid in enumerate(variants):
                pts = sorted((s["budget"], s["delta_vs_single_mean"], s["delta_t95_low"], s["delta_t95_high"])
                             for s in summ if s.get("variant") == vid and s["scenario"] == sid and s["lambda"] == lam and s["rule"] == rule)
                if not pts:
                    continue
                b, m, lo, hi = map(np.array, zip(*pts))
                x = b * 2 ** ((k - len(variants) / 2) * 0.03)
                ax.errorbar(x, m, yerr=[m - lo, hi - m], marker="o", ms=2.5, lw=0.9, capsize=1.5, label=vid)
            ax.axhline(0, color="#222222", lw=0.8, ls="--")
            ax.set_xscale("log", base=2)
            ax.set_title(f"{rule}: {sid}, lambda = {lam:g}", fontsize=8)
            ax.tick_params(labelsize=6)
            ax.set_ylabel("Delta vs SINGLE", fontsize=7)
        axes.flat[0].legend(fontsize=5.5, frameon=False, ncol=2)
        fig.suptitle(f"EXP-004 (optional): {rule} Delta by factor level, seed-level t 95% intervals, {len(doc['seeds'])} seeds", fontsize=8)
        fig.tight_layout()
        p = figs / f"FIG-004-{1 if rule == 'MV' else 2}_{rule.lower()}_delta_by_variant.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        names.append(p.name)
    # tie factor
    fig, axes = plt.subplots(len(cells) // 2 + len(cells) % 2, 2, figsize=(7.2, 2.2 * (len(cells) // 2 + len(cells) % 2)), squeeze=False, sharex=True)
    for ax, (sid, lam) in zip(axes.flat, cells):
        for vid, ls in (("tie_coin", "-"), ("tie_abstain_wrong", ":")):
            for rule, col in (("MV", "#1b6ca8"), ("SEQ", "#c0392b")):
                pts = sorted((s["budget"], s["delta_vs_single_mean"], s["delta_t95_low"], s["delta_t95_high"])
                             for s in summ if s.get("variant") == vid and s["scenario"] == sid and s["lambda"] == lam and s["rule"] == rule)
                if not pts:
                    continue
                b, m, lo, hi = map(np.array, zip(*pts))
                ax.errorbar(b, m, yerr=[m - lo, hi - m], color=col, ls=ls, marker="o", ms=2.5, lw=0.9, capsize=1.5, label=f"{rule} {vid}")
        ax.axhline(0, color="#222222", lw=0.8, ls="--")
        ax.set_xscale("log", base=2)
        ax.set_title(f"{sid}, lambda = {lam:g}, even B", fontsize=8)
        ax.tick_params(labelsize=6)
        ax.set_ylabel("Delta vs SINGLE", fontsize=7)
    axes.flat[0].legend(fontsize=5.5, frameon=False)
    fig.suptitle("EXP-004 (optional): tie rule at even budgets, seed-level t 95% intervals", fontsize=8)
    fig.tight_layout()
    p = figs / "FIG-004-3_tie_rule.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    names.append(p.name)
    return names


# ------------------------------------------------------------------- tables

def _md_exp002(a: dict) -> list[str]:
    L = [f"Verdict: **{a['verdict']}**. Family size {a['family_size']}; cells rejected {a['n_rejected']}.", "",
         "### Primary family (MV and SEQ, B >= 3)", "",
         "| Scenario | lambda | Rule | B | Delta | t95 low | t95 high | p (one-sided) | p Holm | Holm step bound | reject H0 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in a["primary_family"]:
        L.append(f"| {r['scenario']} | {r['lambda']:g} | {r['rule']} | {r['budget']} | {_f(r['delta_mean'])} | {_f(r['t95'][0])} | "
                 f"{_f(r['t95'][1])} | {r['p_raw']:.3g} | {r['p_holm']:.3g} | {_f(r['holm_upper_bound'])} | {r['reject_no_degradation']} |")
    for name in ("P1", "P2", "P3"):
        p = a[name]
        L += ["", f"### {name}: {p['verdict']} ({p['n_supported']} supported, {p['n_inconclusive']} inconclusive, {p['n_disconfirmed']} disconfirmed of {p['n_tests']})", ""]
        if name == "P1":
            L += ["| Scenario | Predicted | Delta | t95 low | t95 high | Status |", "|---|---|---|---|---|---|"]
            L += [f"| {c['scenario']} | {c['predicted']} | {_f(c['delta_mean'])} | {_f(c['t95'][0])} | {_f(c['t95'][1])} | {c['status']} |" for c in p["cells"]]
        elif name == "P2":
            L += ["| Scenario | B | Delta_SEQ - Delta_MV | t95 low | t95 high | Status |", "|---|---|---|---|---|---|"]
            L += [f"| {c['scenario']} | {c['budget']} | {_f(c['diff_mean'])} | {_f(c['t95'][0])} | {_f(c['t95'][1])} | {c['status']} |" for c in p["cells"]]
        else:
            L += ["| Scenario | B | lambda step | change in Delta_MV | t95 low | t95 high | Status |", "|---|---|---|---|---|---|---|"]
            L += [f"| {c['scenario']} | {c['budget']} | {c['lambda_from']:g} to {c['lambda_to']:g} | {_f(c['diff_mean'])} | {_f(c['t95'][0])} | {_f(c['t95'][1])} | {c['status']} |" for c in p["cells"]]
    L += ["", "### CW (secondary, descriptive)", "", "| Scenario | lambda | B | Delta | t95 low | t95 high |", "|---|---|---|---|---|---|"]
    L += [f"| {c['scenario']} | {c['lambda']:g} | {c['budget']} | {_f(c['delta_mean'])} | {_f(c['t95'][0])} | {_f(c['t95'][1])} |"
          for c in sorted(a["CW_descriptive"], key=lambda c: (c["scenario"], c["lambda"], c["budget"]))]
    return L


def _md_exp003(a: dict) -> list[str]:
    L = [f"Verdict: **{a['verdict']}**. Matched cells {a['n_matched_cells']}; disagreeing {a['n_matched_cells_disagree']}; "
         f"model cells run {a['n_model_cells_run']}, excluded {a['n_model_cells_excluded']}.", "",
         "### Matched cells where signs disagree", "", "| p | r | n | Signs (analytic) |", "|---|---|---|---|"]
    L += [f"| {c['p']} | {c['r']} | {c['n']} | {c['analytic_signs']} |" for c in a["disagreeing_cells"]]
    L += ["", "### Sign counts by model", "", "| Model | cells | negative | zero | positive |", "|---|---|---|---|---|"]
    L += [f"| {m} | {c['cells']} | {c['negative']} | {c['zero']} | {c['positive']} |" for m, c in a["sign_counts_by_model"].items()]
    mc = a["mc_check"]
    L += ["", f"Monte Carlo check: analytic value outside the seed-level t 95% interval in {mc['n_analytic_outside_mc_t95']} of "
          f"{mc['n_cells_with_interval']} cells; interval sides {mc['mc_interval_sides']}."]
    return L


def _md_exp004(a: dict) -> list[str]:
    c = a["primary_consistency_with_exp002"]
    L = [f"Verdict: **{a['verdict']}**. Holm-significant EXP-002 cells in scope: {a['n_significant_exp002_cells_in_scope']}; "
         f"tie reference cells: {a['n_tie_reference_cells']}; checks {a['n_checks']}; reversed {a['n_reversed']}.", "",
         f"Consistency: the primary variant matches EXP-002 per seed in {c['n_values_compared']} values, max abs difference {c['max_abs_diff']}.", "",
         "| Factor level | Scenario | lambda | Rule | B | reference Delta | variant Delta | t95 low | t95 high | reversed |", "|---|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r['factor_level']} | {r['scenario']} | {r['lambda']:g} | {r['rule']} | {r['budget']} | {_f(r['exp002_delta'])} | {_f(r['variant_delta'])} | "
          f"{_f(r['variant_t95'][0])} | {_f(r['variant_t95'][1])} | {r['reversed']} |" for r in a["checks"]]
    L += ["", f"Descriptive: the sign of the mean Delta changed in {len(a['descriptive_mean_sign_changes'])} of {a['n_descriptive_comparisons']} "
          "variant-versus-reference MV/SEQ comparisons (all cells, not only significant ones):", "",
          "| Variant | Scenario | lambda | Rule | B | reference Delta | variant Delta | t95 low | t95 high |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {r['variant']} | {r['scenario']} | {r['lambda']:g} | {r['rule']} | {r['budget']} | {_f(r['reference_delta'])} | {_f(r['variant_delta'])} | "
          f"{_f(r['variant_t95'][0])} | {_f(r['variant_t95'][1])} |" for r in a["descriptive_mean_sign_changes"]]
    L += ["", "### Cost accounting (descriptive; primary variant)", "", "| Scenario | lambda | Rule | Calls | Messages per item | Calls + messages | Accuracy |",
          "|---|---|---|---|---|---|---|"]
    L += [f"| {r['scenario']} | {r['lambda']:g} | {r['rule']} | {r['calls']} | {r['messages_per_item']:.1f} | {r['calls_plus_messages']:.1f} | {_f(r['accuracy'])} |"
          for r in sorted(a["cost_descriptive"], key=lambda r: (r["scenario"], r["lambda"], r["rule"], r["calls"]))]
    return L


def _md_exp001(a: dict) -> list[str]:
    L = [f"Verdict: **{a['verdict']}**.", "", "| Golden check | Expected | Got | Pass |", "|---|---|---|---|"]
    L += [f"| {g['check']} | {g['expected']} | {g['got']:.10f} | {g['pass']} |" for g in a["golden"]]
    L += ["", f"Cells run {a['n_cells_run']}, excluded {a['n_cells_excluded']}, failing {a['n_cells_fail']}; max |z| {a['max_abs_z']:.3f}; "
          f"|z| > 2 in {a['n_abs_z_above_2']} cells, |z| > 3 in {a['n_abs_z_above_3']}.", "", "| Model | cells | failing | max abs z |", "|---|---|---|---|"]
    L += [f"| {m} | {b['cells']} | {b['fail']} | {b['max_abs_z']:.3f} |" for m, b in a["by_model"].items()]
    return L


# ------------------------------------------------------------------- driver

def run_analysis(exp: str, results_dir: Path, exp002_dir: Path | None = None) -> dict:
    doc = load_result(results_dir / "results.json")
    if doc["experiment_id"] != exp:
        raise ValueError(f"{results_dir} holds {doc['experiment_id']}, not {exp}")
    out = results_dir / "analysis"
    figs = out / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    if exp == "EXP-001":
        a, md, names = analyse_exp001(doc), _md_exp001, []
    elif exp == "EXP-002":
        a, md, names = analyse_exp002(doc), _md_exp002, _fig_exp002(doc, figs)
    elif exp == "EXP-003":
        a, md, names = analyse_exp003(doc), _md_exp003, _fig_exp003(doc, figs)
    elif exp == "EXP-004":
        if exp002_dir is None:
            raise ValueError("EXP-004 analysis needs the EXP-002 results folder")
        a, md, names = analyse_exp004(doc, load_result(exp002_dir / "results.json")), _md_exp004, _fig_exp004(doc, figs)
    else:
        raise ValueError(f"unknown experiment {exp}")
    a["label"] = doc["label"]
    a["source"] = {"results_json": (results_dir / "results.json").as_posix(), "results_json_sha256": sha256_file(results_dir / "results.json"),
                   "config_sha256": doc["config_sha256"], "code_revision": doc["code_revision"], "generator": "paradox.analysis"}
    a["figures"] = [f"analysis/figures/{n}" for n in names]
    (out / "analysis.json").write_text(json.dumps(a, indent=1, sort_keys=True, default=float) + "\n", encoding="utf-8")
    head = ["<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->", f"# {exp} analysis under the frozen decision rules ({doc['label']})", "",
            f"Generated by `python -m paradox.analysis` from `{a['source']['results_json']}` (SHA-256 `{a['source']['results_json_sha256']}`, "
            f"code revision `{doc['code_revision']}`). Decision rule: {a['decision_rule']}.", ""]
    (out / "analysis.md").write_text("\n".join(head + md(a)) + "\n", encoding="utf-8")
    return a


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m paradox.analysis", description="Frozen-rule analysis, provenance and SHA-256 manifest")
    ap.add_argument("experiment", choices=["EXP-001", "EXP-002", "EXP-003", "EXP-004"])
    ap.add_argument("results_dir", type=Path)
    ap.add_argument("--exp002", type=Path, default=None)
    ap.add_argument("--exit-status", type=int, default=None)
    args = ap.parse_args(argv)
    write_provenance(args.results_dir, args.exit_status)
    a = run_analysis(args.experiment, args.results_dir, args.exp002)
    write_sha256_manifest(args.results_dir)
    print(a["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M3 exploratory metric validation (not a finding).

Checks every metric of protocol sections 3 and 4 on hand-computed known cases,
then checks the exploratory smoke results (exploratory seeds, entropy 0)
against closed forms and accounting identities.
Usage: .venv/bin/python scripts/m3_metric_check.py <smoke results dir> <out json>
"""

import json
import sys
from math import sqrt
from pathlib import Path

import numpy as np

from paradox import metrics, theory
from paradox.schema import load_result


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol


def known_cases():
    c = []
    c.append(("accuracy [T,F,T,T] = 0.75", close(metrics.accuracy(np.array([True, False, True, True])), 0.75)))
    c.append(("Brier q=[1,0.5,0] = 1.25/3", close(metrics.brier(np.array([1.0, 0.5, 0.0])), 1.25 / 3)))
    c.append(("ECE calibrated bin (0.75, 3 of 4 correct) = 0", close(metrics.ece(np.full(4, 0.75), np.array([True, True, True, False])), 0.0)))
    c.append(("ECE p=0.95, 1 of 2 correct = 0.45", close(metrics.ece(np.full(2, 0.95), np.array([True, False])), 0.45)))
    c.append(("ECE two bins (0.55: 1/2; 0.95: 2/2) = 0.5*0.05 + 0.5*0.05", close(
        metrics.ece(np.array([0.55, 0.55, 0.95, 0.95]), np.array([True, False, True, True])), 0.05)))
    share, pair = metrics.disagreement(np.array([0, 1, 3]), 3)
    c.append(("disagreement k=[0,1,3], n=3: share 1/3", close(share, 1 / 3)))
    c.append(("pairwise disagreement k=[0,1,3], n=3: (0 + 4/6 + 0)/3", close(pair, (4 / 6) / 3)))
    c.append(("paired delta [T,T,F] vs [F,T,T] = 0", close(metrics.paired_delta(np.array([True, True, False]), np.array([False, True, True])), 0.0)))
    c.append(("paired delta [T,T,T] vs [F,F,T] = 2/3", close(metrics.paired_delta(np.array([True] * 3), np.array([False, False, True])), 2 / 3)))
    c.append(("Condorcet M_3(0.55) = 0.57475", close(theory.condorcet(3, 0.55), 0.57475, 1e-12)))
    c.append(("common shock G(5, 0.6, 1) = 0.6", close(theory.common_shock(5, 0.6, 1.0), 0.6, 1e-12)))
    return [{"check": n, "pass": bool(ok)} for n, ok in c]


def smoke_checks(doc):
    c = []
    recs = doc["records"]
    c.append(("all smoke invariants hold, no exclusions", all(all(r["invariants"].values()) and not r["excluded"] for r in recs)))
    sc = {s["id"]: s for s in doc["config"]["scenarios"]}
    for r in recs:
        ms = {(m["rule"], m["budget"]): m for m in r["metrics"]}
        single = ms[("SINGLE", 1)]
        ok = single["delta_vs_single"] == 0.0 and close(ms[("MV", 1)]["accuracy"], single["accuracy"])
        ok &= all(close(m["accuracy_per_call"], (m["accuracy"] - 0.5) / m["calls_per_item"]) for m in r["metrics"])
        ok &= all(m["messages_per_item"] == m["n_reasoners"] * (m["n_reasoners"] - 1) / 2 for m in r["metrics"] if m["rule"] == "SEQ")
        ok &= all(0 <= m[k] <= 1 for m in r["metrics"] for k in ("accuracy", "brier", "ece", "disagreement_share", "pairwise_disagreement"))
        c.append((f"{r['record_id']}: SINGLE delta 0, MV(1)=SINGLE, accuracy per call, SEQ messages n(n-1)/2, metric ranges", bool(ok)))
    # pooled MV accuracy against the closed form, 4 Monte Carlo SE
    for sid in sc:
        for lam in doc["config"]["lambdas"]:
            for b in (1, 3, 9):
                accs = [m["accuracy"] for r in recs if r["scenario"] == sid and r["lambda"] == lam for m in r["metrics"] if m["rule"] == "MV" and m["budget"] == b]
                n = len(accs) * doc["config"]["n_items"]
                th = theory.mixture(b, sc[sid]["p_easy"], sc[sid]["h"], sc[sid]["p_hard"], lam)
                z = (np.mean(accs) - th) / sqrt(th * (1 - th) / n)
                c.append((f"MV accuracy {sid} lambda {lam} B {b} within 4 SE of theory (z = {z:.2f})", bool(abs(z) <= 4)))
    return [{"check": n, "pass": ok} for n, ok in c]


def main():
    smoke, out = Path(sys.argv[1]), Path(sys.argv[2])
    doc = load_result(smoke / "results.json")
    res = {"label": "exploratory", "smoke_results": smoke.as_posix(), "seed_entropy": doc["config"]["seed_entropy"],
           "known_cases": known_cases(), "smoke_checks": smoke_checks(doc)}
    res["all_pass"] = all(x["pass"] for x in res["known_cases"] + res["smoke_checks"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    n = len(res["known_cases"]) + len(res["smoke_checks"])
    print(f"{sum(x['pass'] for x in res['known_cases'] + res['smoke_checks'])} of {n} checks pass; all_pass={res['all_pass']}")
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

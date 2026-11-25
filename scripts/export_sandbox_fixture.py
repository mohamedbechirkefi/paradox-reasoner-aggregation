# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Write the fixture that pins the browser port of the engine (M5).

Output: demo/src/fixtures/engine_fixture.json. It holds (a) the first draws of
each ported stream and the SINGLE, MV and SEQ correct-decision counts produced
by the Python engine (src/paradox) for three small exploratory configurations,
plus the SEQ votes of one item; and (b) the committed per-seed accuracies of one
confirmatory EXP-002 seed-run, read from results/EXP-002/metrics.csv, which the
port must reproduce. demo/src/engine.test.ts compares the port with exact
equality. Compute: well under one second, one process. No timestamps.

Usage: .venv/bin/python scripts/export_sandbox_fixture.py [--check]
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

from paradox.generator import ModelParams, Scenario, generate_run
from paradox.rules import majority, sequential, sequential_votes, single

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "demo" / "src" / "fixtures" / "engine_fixture.json"
BUDGETS = [1, 2, 3, 4, 5, 8, 9, 15, 31]
STREAM_HEADS = ("labels", "difficulty", "leader", "adopt", "private", "seq_order", "herd", "tie")

CASES = [
    {"name": "S4-lambda0.5-w0.5-seed7", "scenario": {"p_easy": 0.9, "h": 0.4, "p_hard": 0.3}, "lam": 0.5, "w": 0.5, "n_items": 300, "seed": 7},
    {"name": "S1-lambda0.25-w0.9-seed0", "scenario": {"p_easy": 0.6, "h": 0.0, "p_hard": 0.6}, "lam": 0.25, "w": 0.9, "n_items": 150, "seed": 0},
    {"name": "S6-lambda0-w0.5-seed123456789", "scenario": {"p_easy": 0.95, "h": 0.5, "p_hard": 0.35}, "lam": 0.0, "w": 0.5, "n_items": 200, "seed": 123456789},
]

# One confirmatory seed-run of EXP-002 (first seed of SeedSequence(20261124).spawn(30)).
COMMITTED = {"scenario_id": "S6", "scenario": {"p_easy": 0.95, "h": 0.5, "p_hard": 0.35}, "lam": 0.0, "w": 0.5,
             "n_items": 2000, "seed": 4081218282}


def stream_heads(seed: int, k: int = 4) -> dict[str, list[float]]:
    names = ("labels", "difficulty", "leader", "adopt", "private", "signal", "seq_order", "herd", "delib", "tie")
    rngs = dict(zip(names, (np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(len(names)))))
    return {n: [float(x) for x in rngs[n].random(k)] for n in STREAM_HEADS}


def case_output(c: dict) -> dict:
    sc = c["scenario"]
    d = generate_run(Scenario("X", sc["p_easy"], sc["h"], sc["p_hard"] if sc["h"] > 0 else None),
                     ModelParams(lam=c["lam"], w=c["w"]), c["n_items"], c["seed"])
    counts = {}
    for b in BUDGETS:
        counts[str(b)] = {
            "single": int(single(d).decision_correct.sum()),
            "mv": int(majority(d, b).decision_correct.sum()),
            "seq": int(sequential(d, b, c["w"]).decision_correct.sum()),
        }
    votes9 = sequential_votes(d, 9, c["w"])[0]
    return {**c, "stream_heads": stream_heads(c["seed"]), "counts": counts,
            "item0_seq_votes_b9": [int(v) for v in votes9],
            "item0_correct": [int(v) for v in d.correct[0]]}


def committed_rows() -> dict:
    rows = {}
    with open(REPO / "results" / "EXP-002" / "metrics.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (r["scenario"] == COMMITTED["scenario_id"] and float(r["lambda"]) == COMMITTED["lam"]
                    and int(r["seed"]) == COMMITTED["seed"] and r["rule"] in ("SINGLE", "MV", "SEQ")):
                rows[f'{r["rule"]}-{r["budget"]}'] = {"rule": r["rule"], "budget": int(r["budget"]), "accuracy": float(r["accuracy"]),
                                                      "record_id": r["record_id"]}
    if not rows:
        raise SystemExit("committed seed-run not found in results/EXP-002/metrics.csv")
    return {**COMMITTED, "source": "results/EXP-002/metrics.csv", "rows": [rows[k] for k in sorted(rows)]}


def build() -> str:
    doc = {
        "generator": "scripts/export_sandbox_fixture.py",
        "engine": "src/paradox (generator.generate_run, rules.single, rules.majority, rules.sequential)",
        "tolerance": "exact: draws compared with ===, counts and accuracies equal",
        "cases": [case_output(c) for c in CASES],
        "committed_seed_run": committed_rows(),
    }
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def main() -> int:
    text = build()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text() == text
        print("fixture up to date" if ok else "fixture differs")
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(REPO)}: {len(CASES)} cases, committed seed-run of {COMMITTED['scenario_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Summarise the M4 exploratory CW delta sweep (journal J-0016).

EXPLORATORY. Reads results/exploratory/m4-cw-delta/delta_*/metrics.csv
(written by `paradox run` on configs/exploratory/m4_cw_delta_*.json, seed
entropy 0, 10 seeds of 2000 items) and writes summary.json and summary.md with
the seed-level mean and t 95% interval of Delta = A_rule(B) - A_SINGLE.
It changes no frozen verdict.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from paradox.stats import t_interval

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "exploratory" / "m4-cw-delta"
LEVELS = (("0", 0.0), ("0p25", 0.25), ("0p5", 0.5), ("1", 1.0))


def main() -> None:
    rows = []
    for tag, delta in LEVELS:
        cells = defaultdict(list)
        with open(BASE / f"delta_{tag}" / "metrics.csv") as f:
            for r in csv.DictReader(f):
                if r["excluded"] == "True" or r["rule"] == "SINGLE" or int(r["budget"]) == 1:
                    continue
                cells[(r["scenario"], r["rule"], int(r["budget"]))].append(float(r["delta_vs_single"]))
        for (sc, rule, b), vals in sorted(cells.items()):
            lo, hi = t_interval(vals)
            rows.append({"delta_conf": delta, "scenario": sc, "rule": rule, "budget": b, "n_seeds": len(vals),
                         "delta_mean": sum(vals) / len(vals), "t95": [lo, hi]})
    (BASE / "summary.json").write_text(json.dumps({"label": "exploratory", "journal": "J-0016",
                                                   "generator": "scripts/m4_cw_delta_summary.py", "rows": rows}, indent=1) + "\n")
    L = ["<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->",
         "# M4 exploratory CW delta sweep (EXPLORATORY, J-0016)", "",
         "Delta = A_rule(B) - A_SINGLE, seed-level mean and t 95% interval, 10 exploratory seeds (entropy 0) of 2000 items, lambda 0. `delta` is the confidence informativeness of protocol section 2.3 (confirmatory value 1).", "",
         "| delta | Scenario | Rule | B | Delta [t95] |", "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['delta_conf']} | {r['scenario']} | {r['rule']} | {r['budget']} | {r['delta_mean']:+.4f} [{r['t95'][0]:+.4f}, {r['t95'][1]:+.4f}] |")
    (BASE / "summary.md").write_text("\n".join(L) + "\n")
    print(f"wrote {BASE}/summary.json and summary.md ({len(rows)} rows)")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M4 evidence audit: recompute headline numbers and counts from the raw
outputs (``results.json`` / ``metrics.csv``) independently of
``paradox.analysis``, and compare them with the frozen analysis outputs and
with the values stated in the reports and manuscript (master prompt 11.5).

The recomputation uses only numpy and ``paradox.stats`` (t interval, one-sided
p-value and Holm adjustment, the functions tested in tests/test_metrics_stats.py).

Usage: .venv/bin/python scripts/m4_recompute_checks.py
Writes results/audit/recompute_checks.json; exit status 1 if any check fails.
EXP-004 needs the git-ignored results/EXP-004/metrics.csv (regenerable, D-012);
if it is absent its checks are reported as skipped.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from paradox.stats import holm, one_sided_p_negative, t_interval

ROOT = Path(__file__).resolve().parents[1]
checks: list[dict] = []


def check(name: str, got, expected, tol: float | None = None) -> None:
    if tol is None:
        ok = got == expected
    else:
        ok = abs(float(got) - float(expected)) <= tol
    checks.append({"check": name, "got": got, "expected": expected, "pass": bool(ok)})


def load_cells(path: Path) -> dict:
    cells = defaultdict(dict)
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["excluded"] == "True":
                continue
            key = (r.get("variant", ""), r["scenario"], float(r["lambda"]), r["rule"], int(r["budget"]))
            cells[key][r["seed"]] = float(r["delta_vs_single"])
    return cells


def exp001() -> None:
    res = json.loads((ROOT / "results/EXP-001/results.json").read_text())
    recs = res["records"]
    run = [r for r in recs if not r.get("excluded")]
    exc = [r for r in recs if r.get("excluded")]
    zs = []
    for r in run:
        m = r["metrics"] if isinstance(r.get("metrics"), dict) else r
        a_sim, a_th, n = m.get("accuracy_sim"), m.get("accuracy_theory"), m.get("n_items_total")
        if a_sim is None or a_th is None or n is None:
            continue
        se = (a_th * (1 - a_th) / n) ** 0.5
        zs.append(0.0 if se == 0 else (a_sim - a_th) / se)
    check("EXP-001 cells run", len(run), 292)
    check("EXP-001 cells excluded", len(exc), 20)
    if zs:
        za = np.abs(zs)
        check("EXP-001 max abs z (report 3.116)", round(float(za.max()), 3), 3.116)
        check("EXP-001 cells abs z > 2 (report 30)", int((za > 2).sum()), 30)
        check("EXP-001 cells abs z > 4 (report 0)", int((za > 4).sum()), 0)
    else:
        checks.append({"check": "EXP-001 z recomputation", "pass": None, "note": "record fields not found; z taken from analysis.json only"})


def exp002() -> None:
    cells = load_cells(ROOT / "results/EXP-002/metrics.csv")
    fam = []
    for (v, sc, lam, rule, b), seeds in cells.items():
        if rule in ("MV", "SEQ") and b >= 3:
            x = np.array([seeds[s] for s in sorted(seeds)])
            fam.append(((sc, lam, rule, b), x, one_sided_p_negative(x)))
    check("EXP-002 primary family size", len(fam), 240)
    check("EXP-002 seeds per cell", sorted({len(x) for _, x, _ in fam}), [30])
    padj = holm([p for _, _, p in fam])
    rej = [k for (k, _, _), pa in zip(fam, padj) if pa < 0.05]
    check("EXP-002 rejected cells (report 32)", len(rej), 32)
    by_rule = Counter(k[2] for k in rej)
    check("EXP-002 rejected MV cells", by_rule["MV"], 20)
    check("EXP-002 rejected SEQ cells", by_rule["SEQ"], 12)
    check("EXP-002 rejected scenarios", sorted({k[0] for k in rej}), ["S4", "S6"])
    x = dict(((k, x) for k, x, _ in fam))[("S6", 0.0, "MV", 31)]
    lo, hi = t_interval(x)
    check("EXP-002 headline Delta S6 lam0 MV B31", round(float(x.mean()), 4), -0.1313)
    check("EXP-002 headline t95 low", round(lo, 4), -0.1350)
    check("EXP-002 headline t95 high", round(hi, 4), -0.1276)
    # P2 at lambda 0: Delta_SEQ - Delta_MV, per seed
    p2 = Counter()
    for sc in ("S1", "S2", "S3", "S4", "S5", "S6"):
        for b in (3, 5, 9, 15, 31):
            mv, sq = cells[("", sc, 0.0, "MV", b)], cells[("", sc, 0.0, "SEQ", b)]
            d = np.array([sq[s] - mv[s] for s in sorted(mv)])
            lo, hi = t_interval(d)
            p2["disconfirmed" if lo > 0 else ("supported" if hi < 0 else "inconclusive")] += 1
    check("EXP-002 P2 disconfirmed cells (report 9)", p2["disconfirmed"], 9)
    check("EXP-002 P2 supported cells (report 21)", p2["supported"], 21)
    # P3: consecutive lambda steps in S1 to S3, B >= 3
    p3 = Counter()
    lams = (0.0, 0.25, 0.5, 0.75)
    for sc in ("S1", "S2", "S3"):
        for b in (3, 5, 9, 15, 31):
            for a, c in zip(lams, lams[1:]):
                x0, x1 = cells[("", sc, a, "MV", b)], cells[("", sc, c, "MV", b)]
                d = np.array([x1[s] - x0[s] for s in sorted(x0)])
                lo, hi = t_interval(d)
                p3["disconfirmed" if lo > 0 else ("supported" if hi < 0 else "inconclusive")] += 1
    check("EXP-002 P3 supported (report 43)", p3["supported"], 43)
    check("EXP-002 P3 inconclusive (report 2)", p3["inconclusive"], 2)
    check("EXP-002 P3 disconfirmed (report 0)", p3["disconfirmed"], 0)
    # between-seed SD over the 432 non-baseline cells (3 rules x 6 budgets x 24 run cells)
    sds = [float(np.std([v for v in seeds.values()], ddof=1)) for (v, sc, lam, rule, b), seeds in cells.items() if rule != "SINGLE"]
    check("EXP-002 non-baseline cells (report 432)", len(sds), 432)
    check("EXP-002 max between-seed SD (report 0.0162)", round(max(sds), 4), 0.0162)
    check("EXP-002 median between-seed SD (report 0.0087)", round(float(np.median(sds)), 4), 0.0087)
    cw = [float(np.mean(list(s.values()))) for (v, sc, lam, rule, b), s in cells.items() if rule == "CW" and b >= 3]
    check("EXP-002 CW cells above SINGLE (all 120)", sum(m > 0 for m in cw), 120)
    check("EXP-002 CW max mean Delta (report 0.4478)", round(max(cw), 4), 0.4478)


def exp003() -> None:
    a = json.loads((ROOT / "results/EXP-003/analysis/analysis.json").read_text())
    from paradox.dependence import analytic_mv
    from paradox.theory import bahadur_admissible
    signs = {}
    neg = Counter()
    for p in (0.55, 0.6, 0.7):
        for r in (0.05, 0.1, 0.2, 0.4):
            for n in (3, 5, 9, 15):
                s = {}
                for m in ("common_shock", "bahadur", "mixture", "beta"):
                    if m == "bahadur" and not bahadur_admissible(n, p, r):
                        continue
                    d = analytic_mv(m, n, p, r) - p
                    s[m] = (d > 0) - (d < 0)
                    neg[m] += d < 0
                signs[(p, r, n)] = s
    dis = [k for k, s in signs.items() if len(set(s.values())) > 1]
    check("EXP-003 matched cells disagreeing (report 16 of 48)", (len(dis), len(signs)), (16, 48))
    check("EXP-003 disagreements all at r >= 0.2", all(k[1] >= 0.2 for k in dis), True)
    check("EXP-003 negative cells by model", dict(neg), {"common_shock": 0, "bahadur": 8, "mixture": 14, "beta": 0})
    check("EXP-003 analysis.json agrees", a["n_matched_cells_disagree"], len(dis))


def exp004() -> None:
    path = ROOT / "results/EXP-004/metrics.csv"
    if not path.exists():
        checks.append({"check": "EXP-004 recomputation", "pass": None, "note": "metrics.csv absent (git-ignored, D-012)"})
        return
    cells = load_cells(path)
    ref = load_cells(ROOT / "results/EXP-002/metrics.csv")
    same = all(np.allclose([cells[("primary",) + k[1:]][s] for s in sorted(v)], [v[s] for s in sorted(v)])
               for k, v in ref.items() if k[1] in ("S1", "S4", "S5") and k[2] in (0.0, 0.5) and ("primary",) + k[1:] in cells)
    check("EXP-004 primary variant equals EXP-002 per seed", same, True)
    rev = 0
    n = 0
    for lvl in ("tau_0p5", "tau_2", "tau_4", "w_0p25", "w_0p9"):
        for b in (9, 15, 31):
            x = cells[(lvl, "S4", 0.0, "MV", b)]
            lo, hi = t_interval(np.array([x[s] for s in sorted(x)]))
            n += 1
            rev += lo > 0
    for b in (8, 16, 30):
        x = cells[("tie_abstain_wrong", "S4", 0.0, "MV", b)]
        lo, hi = t_interval(np.array([x[s] for s in sorted(x)]))
        n += 1
        rev += lo > 0
    check("EXP-004 frozen-rule checks (report 18)", n, 18)
    check("EXP-004 reversals (report 0)", rev, 0)


def main() -> int:
    exp001()
    exp002()
    exp003()
    exp004()
    out = ROOT / "results" / "audit"
    out.mkdir(parents=True, exist_ok=True)
    (out / "recompute_checks.json").write_text(json.dumps({"label": "audit", "generator": "scripts/m4_recompute_checks.py", "checks": checks}, indent=1, default=str) + "\n")
    fails = [c for c in checks if c["pass"] is False]
    for c in checks:
        print(("PASS " if c["pass"] else ("SKIP " if c["pass"] is None else "FAIL ")) + c["check"], "" if c["pass"] else f"got={c.get('got')} expected={c.get('expected')} {c.get('note','')}")
    print(f"{len(checks)} checks, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

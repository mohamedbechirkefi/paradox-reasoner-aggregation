# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M4 exploratory sensitivity checks from closed forms only (journal J-0015).

EXPLORATORY. Nothing here changes or replaces a frozen verdict. No simulation,
no seeds: every value is an exact closed form from ``paradox.theory`` (the
functions validated by EXP-001), or an asymptotic limit stated in the output.

Checks
------
X1  Finite-budget effect (EXP-002 competing explanation "convergence not
    reached at B = 31"): exact MV accuracy minus mean competence for the six
    EXP-002 scenarios and four lambda levels at n in {3, 31, 101, 301}, and the
    large-n limit. Also the agreement between the exact sign at B in
    {3, 5, 9, 15, 31} and the confirmatory EXP-002 MV estimates.
X2  Group-size range of EXP-003 ("Beta never degrades at n <= 15"): exact
    Delta_MV for the common-shock, mixture and Beta models at n in
    {31, 101, 301, 1001} and the large-n limit, and Bahadur admissibility.
X3  P1 margin per scenario: h p_hard - (1 - h)(1 - p_easy) (design arithmetic).

Usage: .venv/bin/python scripts/m4_exploratory_analytic.py
Writes results/exploratory/m4-analytic/{results.json, summary.md}.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from paradox import theory
from paradox.dependence import analytic_mv, model_parameters

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exploratory" / "m4-analytic"

SCENARIOS = {
    "S1": (0.60, 0.0, None),
    "S2": (0.55, 0.0, None),
    "S3": (0.80, 0.0, None),
    "S4": (0.90, 0.4, 0.30),
    "S5": (0.70, 0.2, 0.45),
    "S6": (0.95, 0.5, 0.35),
}
LAMBDAS = (0.0, 0.25, 0.5, 0.75)
X1_N = (3, 31, 101, 301)
X2_N = (31, 101, 301, 1001)
X2_P = (0.55, 0.6, 0.7)
X2_R = (0.05, 0.1, 0.2, 0.4)


def mu(pe: float, h: float, ph: float | None) -> float:
    return (1 - h) * pe + (h * ph if h > 0 else 0.0)


def cs_limit(p: float, lam: float) -> float:
    """Large-n MV accuracy, common-shock, one competence level ``p``.

    By the law of large numbers the share of correct votes tends to
    lam * 1[L correct] + (1 - lam) p, so the majority is correct with
    probability p * 1[lam + (1-lam) p > 0.5] + (1-p) * 1[(1-lam) p > 0.5]
    (ties at exactly 0.5 do not occur on this grid; they raise).
    """
    a = lam + (1 - lam) * p
    b = (1 - lam) * p
    if 0.5 in (a, b):
        raise ValueError("boundary case")
    return p * (a > 0.5) + (1 - p) * (b > 0.5)


def mixture_limit(pe: float, h: float, ph: float | None, lam: float) -> float:
    return (1 - h) * cs_limit(pe, lam) + (h * cs_limit(ph, lam) if h > 0 else 0.0)


def beta_tail_above_half(a: float, b: float, m: int = 200000) -> float:
    """P(p_i > 0.5) for p_i ~ Beta(a, b), by the substitution x = 1 - t^(1/b)
    (removes the endpoint singularity at x = 1) and a midpoint rule."""
    from math import exp, lgamma

    lb = lgamma(a) + lgamma(b) - lgamma(a + b)
    upper = 0.5**b
    hstep = upper / m
    s = 0.0
    for i in range(m):
        t = (i + 0.5) * hstep
        x = 1.0 - t ** (1.0 / b)
        s += x ** (a - 1.0)
    return s * hstep / b / exp(lb)


def x1() -> dict:
    exp002 = json.loads((ROOT / "results/EXP-002/analysis/analysis.json").read_text())
    obs = {(c["scenario"], c["lambda"], c["budget"]): c for c in exp002["primary_family"] if c["rule"] == "MV"}
    rows = []
    for sid, (pe, h, ph) in SCENARIOS.items():
        m = mu(pe, h, ph)
        for lam in LAMBDAS:
            row = {"scenario": sid, "lambda": lam, "mu": m}
            for n in X1_N:
                row[f"delta_exact_n{n}"] = theory.mixture(n, pe, h, ph, lam) - m
            row["delta_limit"] = mixture_limit(pe, h, ph, lam) - m
            rows.append(row)
    agree = []
    for (sid, lam, b), c in sorted(obs.items()):
        pe, h, ph = SCENARIOS[sid]
        d_exact = theory.mixture(b, pe, h, ph, lam) - mu(pe, h, ph)
        lo, hi = c["t95"]
        agree.append({
            "scenario": sid, "lambda": lam, "budget": b, "delta_exact": d_exact,
            "delta_observed": c["delta_mean"], "t95": [lo, hi],
            "exact_inside_t95": lo <= d_exact <= hi,
            "holm_rejected": c["reject_no_degradation"],
            "exact_sign": (d_exact > 0) - (d_exact < 0),
        })
    return {
        "rows": rows,
        "exp002_mv_comparison": agree,
        "n_mv_cells": len(agree),
        "n_exact_inside_t95": sum(a["exact_inside_t95"] for a in agree),
        "n_rejected": sum(a["holm_rejected"] for a in agree),
        "n_rejected_with_negative_exact": sum(a["holm_rejected"] and a["exact_sign"] < 0 for a in agree),
        "n_negative_exact": sum(a["exact_sign"] < 0 for a in agree),
        "negative_exact_not_rejected": [
            {k: a[k] for k in ("scenario", "lambda", "budget", "delta_exact", "delta_observed", "t95")}
            for a in agree if a["exact_sign"] < 0 and not a["holm_rejected"]
        ],
        "note": "observed Delta is A_MV - A_SINGLE (realised reasoner 1); exact Delta is A_MV - mu; seed-level t95 from the frozen analysis",
    }


def x2() -> dict:
    rows = []
    for p in X2_P:
        for r in X2_R:
            for model in ("common_shock", "mixture", "beta"):
                prm = model_parameters(model, p, r)
                row = {"model": model, "p": p, "r": r, "params": prm}
                for n in X2_N:
                    row[f"delta_exact_n{n}"] = analytic_mv(model, n, p, r) - p
                if model == "common_shock":
                    row["delta_limit"] = cs_limit(p, prm["lambda"]) - p
                elif model == "mixture":
                    row["delta_limit"] = mixture_limit(prm["p_easy"], prm["h"], prm["p_hard"], 0.0) - p
                else:
                    row["delta_limit"] = beta_tail_above_half(prm["a"], prm["b"]) - p
                    row["limit_note"] = "P(p_i > 0.5) - p, numerical integration (midpoint rule, 200,000 nodes)"
                rows.append(row)
            row = {"model": "bahadur", "p": p, "r": r, "params": {"c": r}}
            for n in X2_N:
                ok = theory.bahadur_admissible(n, p, r)
                row[f"admissible_n{n}"] = ok
                row[f"delta_exact_n{n}"] = (theory.bahadur_mv(n, p, r) - p) if ok else None
            rows.append(row)
    neg = [
        {"model": x["model"], "p": x["p"], "r": x["r"], "n": n, "delta_exact": x[f"delta_exact_n{n}"]}
        for x in rows for n in X2_N
        if x.get(f"delta_exact_n{n}") is not None and x[f"delta_exact_n{n}"] < 0
    ]
    neg_limit = [
        {"model": x["model"], "p": x["p"], "r": x["r"], "delta_limit": x["delta_limit"]}
        for x in rows if "delta_limit" in x and x["delta_limit"] < 0
    ]
    return {"rows": rows, "negative_finite_n": neg, "negative_limits": neg_limit}


def x3() -> list[dict]:
    return [
        {"scenario": s, "margin": (h * ph if h > 0 else 0.0) - (1 - h) * (1 - pe), "mu": mu(pe, h, ph)}
        for s, (pe, h, ph) in SCENARIOS.items()
    ]


def fmt(x: float | None, d: int = 5) -> str:
    return "n/a" if x is None else f"{x:+.{d}f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    res = {
        "label": "exploratory",
        "journal": "J-0015",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "code_revision_at_run": rev,
        "generator": "scripts/m4_exploratory_analytic.py",
        "statement": "Exploratory closed-form checks made in M4 after all confirmatory verdicts. They change no frozen verdict.",
        "X1_finite_budget": x1(),
        "X2_group_size_range": x2(),
        "X3_p1_margin": x3(),
    }
    (OUT / "results.json").write_text(json.dumps(res, indent=1) + "\n")

    a, b = res["X1_finite_budget"], res["X2_group_size_range"]
    L = [
        "<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->",
        "# M4 exploratory closed-form checks (EXPLORATORY, J-0015)",
        "",
        f"Generated by `scripts/m4_exploratory_analytic.py` at revision `{rev}`. Exact closed forms from `paradox.theory`; no seeds, no simulation. These checks were made after every confirmatory verdict and change none of them.",
        "",
        "## X1. EXP-002 scenarios: exact Delta_MV = A_MV(n) - mu",
        "",
        "| Scenario | lambda | mu | n = 3 | n = 31 | n = 101 | n = 301 | limit |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in a["rows"]:
        L.append(f"| {r['scenario']} | {r['lambda']} | {r['mu']:.2f} | " + " | ".join(fmt(r[f'delta_exact_n{n}']) for n in X1_N) + f" | {fmt(r['delta_limit'])} |")
    L += [
        "",
        f"Comparison with the confirmatory EXP-002 MV cells (B 3 to 31): the exact value lies inside the seed-level t95 interval in {a['n_exact_inside_t95']} of {a['n_mv_cells']} cells. The exact value is negative in {a['n_negative_exact']} cells; {a['n_rejected_with_negative_exact']} of the {a['n_rejected']} Holm-rejected MV cells have a negative exact value.",
        "",
        "Cells with a negative exact value that the frozen rule did not reject:",
        "",
        "| Scenario | lambda | B | exact | observed | t95 |",
        "|---|---|---|---|---|---|",
    ]
    for c in a["negative_exact_not_rejected"]:
        L.append(f"| {c['scenario']} | {c['lambda']} | {c['budget']} | {fmt(c['delta_exact'])} | {fmt(c['delta_observed'], 4)} | [{c['t95'][0]:+.4f}, {c['t95'][1]:+.4f}] |")
    L += [
        "",
        "## X2. EXP-003 models beyond n = 15: exact Delta_MV = A_MV(n) - p",
        "",
        "| Model | p | r | n = 31 | n = 101 | n = 301 | n = 1001 | limit |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in b["rows"]:
        lim = fmt(r.get("delta_limit")) if "delta_limit" in r else "n/a"
        L.append(f"| {r['model']} | {r['p']} | {r['r']} | " + " | ".join(fmt(r.get(f'delta_exact_n{n}')) for n in X2_N) + f" | {lim} |")
    L += [
        "",
        "Bahadur cells show n/a where the model is inadmissible.",
        "",
        "## X3. P1 margin h p_hard - (1 - h)(1 - p_easy) (design arithmetic)",
        "",
        "| Scenario | mu | margin |",
        "|---|---|---|",
    ]
    for r in res["X3_p1_margin"]:
        L.append(f"| {r['scenario']} | {r['mu']:.2f} | {r['margin']:+.3f} |")
    L.append("")
    (OUT / "summary.md").write_text("\n".join(L))
    print(f"wrote {OUT}/results.json and summary.md; X1 inside t95 {a['n_exact_inside_t95']}/{a['n_mv_cells']}; "
          f"negative finite-n X2 cells {len(b['negative_finite_n'])}; negative X2 limits {len(b['negative_limits'])}")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Export the published results for the static demo (M5).

Writes demo/public/data/results.json in the shared lab-demo schema
(``lab-demo-results`` 1.0.0) from committed files only: the frozen-rule
analyses (results/EXP-00N/analysis/analysis.json), the generated EXP-002 report
table (results/EXP-002/report.md), the exploratory M4 summaries, the EXP-002
confirmatory config, the claims register, the artifact manifest and the
manuscript. No number is typed by hand: each value is read from a result file
and formatted the way the manuscript prints it; tests/test_demo_export.py
checks that every display string appears verbatim in the manuscript or is a
listed exception whose decimals appear in its stated source file.

Project-specific top-level keys (checked by demo/src/results.ts, fail closed):
``curves`` (every EXP-002 accuracy and Delta cell with its seed-level t 95%
interval), ``scenarios`` (EXP-002 scenario parameters), ``holm_rejected``
(the 32 rejected cells), ``display_exceptions`` and ``sandbox``.

Deterministic: no timestamps; sorted keys. Usage:
    .venv/bin/python scripts/export_demo_data.py          # write
    .venv/bin/python scripts/export_demo_data.py --check  # compare only
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "demo" / "public" / "data" / "results.json"

SRC = {
    "a1": "results/EXP-001/analysis/analysis.json",
    "a2": "results/EXP-002/analysis/analysis.json",
    "a3": "results/EXP-003/analysis/analysis.json",
    "a4": "results/EXP-004/analysis/analysis.json",
    "r2": "results/EXP-002/report.md",
    "m2": "results/EXP-002/metrics.csv",
    "rm2": "results/EXP-002/run_manifest.json",
    "x15": "results/exploratory/m4-analytic/results.json",
    "x16": "results/exploratory/m4-cw-delta/summary.json",
    "cfg2": "research/experiments/EXP-002/config.json",
    "claims": "research/claims_register.csv",
    "manifest": "research/publication/artifact_manifest.json",
    "registry": "research/experiment_registry.csv",
    "ms": "research/paper/manuscript.md",
    "supp": "research/paper/supplementary.md",
    "rep4": "research/experiments/EXP-004/report.md",
    "an4": "results/EXP-004/analysis/analysis.md",
}


def read(key: str) -> str:
    return (REPO / SRC[key]).read_text(encoding="utf-8")


def load(key: str):
    return json.loads(read(key))


def sha(key: str) -> str:
    return hashlib.sha256((REPO / SRC[key]).read_bytes()).hexdigest()


def s4(x: float) -> str:
    """Signed, four decimals, as in the manuscript (for example +0.2708)."""
    return f"{x:+.4f}"


def s5(x: float) -> str:
    return f"{x:+.5f}"


def bracket(lo: float, hi: float) -> str:
    return f"[{s4(lo)}, {s4(hi)}]"


def est(label, value, unit="", lo=None, hi=None, display=None, interval_display=None, level=0.95):
    return {
        "label": label,
        "estimate": float(value),
        "ci_low": None if lo is None else float(lo),
        "ci_high": None if hi is None else float(hi),
        "ci_level": None if lo is None else level,
        "unit": unit,
        "display": display,
        "interval_display": interval_display,
    }


def count(label, k, n=None, display=None):
    return est(label, k, display=display if display is not None else (f"{k} of {n}" if n is not None else str(k)))


def claims_by_exp() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with open(REPO / SRC["claims"], newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["exp_id"]:
                out.setdefault(r["exp_id"], []).append(r["claim_id"])
    return out


def claims_matching(pattern: str) -> list[str]:
    with open(REPO / SRC["claims"], newline="", encoding="utf-8") as f:
        return [r["claim_id"] for r in csv.DictReader(f) if re.search(pattern, r["evidence_path"])]


def registry() -> dict[str, dict]:
    with open(REPO / SRC["registry"], newline="", encoding="utf-8") as f:
        return {r["exp_id"]: r for r in csv.DictReader(f)}


def revision() -> str:
    revs = {load(k)["source"]["code_revision"] for k in ("a1", "a2", "a3", "a4")}
    if len(revs) != 1:
        raise SystemExit(f"confirmatory analyses disagree on the code revision: {sorted(revs)}")
    return revs.pop()


def pf_cell(a2, scenario, lam, rule, budget):
    for c in a2["primary_family"]:
        if (c["scenario"], c["lambda"], c["rule"], c["budget"]) == (scenario, lam, rule, budget):
            return c
    raise SystemExit(f"cell not found: {scenario} {lam} {rule} {budget}")


def cw_cell(a2, scenario, lam, budget):
    for c in a2["CW_descriptive"]:
        if (c["scenario"], c["lambda"], c["budget"]) == (scenario, lam, budget):
            return c
    raise SystemExit(f"CW cell not found: {scenario} {lam} {budget}")


def exp001(a1, claims, reg):
    run, fail = a1["n_cells_run"], a1["n_cells_fail"]
    golden_ok = sum(1 for g in a1["golden"] if g["pass"])
    return {
        "id": "EXP-001",
        "title": reg["EXP-001"]["title"],
        "status": "confirmatory, complete",
        "verdict": a1["verdict"],
        "estimates": [
            count("Admissible validation cells within 4 Monte Carlo SE", run - fail, run),
            est("Largest absolute standardised deviation (tolerance 4)", a1["max_abs_z"], unit="SE", display=f"{a1['max_abs_z']:.3f}"),
            count("Golden fixtures reproduced", golden_ok, len(a1["golden"])),
            count("Bahadur cells excluded as inadmissible (listed in the protocol)", a1["n_cells_excluded"]),
        ],
        "claim_ids": claims.get("EXP-001", []),
        "report_path": reg["EXP-001"]["report_path"],
        "notes": [
            "Counts are exact, so no interval applies (shown as none).",
            "Agreement validates the engine and the formulas against each other within the grid; it cannot detect an error shared by the model definition and its formula.",
        ],
    }


TABLE1 = [("S1", 0.0), ("S2", 0.0), ("S3", 0.0), ("S4", 0.0), ("S4", 0.5), ("S5", 0.0), ("S6", 0.0), ("S6", 0.5)]


def lam_txt(lam: float) -> str:
    return f"{lam:g}"


def exp002(a2, claims, reg):
    ests = [count("MV and SEQ cells with a Holm-adjusted upper bound below 0", a2["n_rejected"], a2["family_size"])]
    for scenario, lam in TABLE1:
        for rule in ("MV", "SEQ", "CW"):
            c = cw_cell(a2, scenario, lam, 31) if rule == "CW" else pf_cell(a2, scenario, lam, rule, 31)
            lo, hi = c["t95"]
            label = f"{scenario}, lambda {lam_txt(lam)}, {rule}, B = 31" + (" (descriptive)" if rule == "CW" else "")
            ests.append(est(label, c["delta_mean"], lo=lo, hi=hi, display=s4(c["delta_mean"]), interval_display=bracket(lo, hi)))
    p1, p2, p3 = a2["P1"], a2["P2"], a2["P3"]
    ests.append(count("P1: predicted signs observed with an interval excluding 0", p1["n_supported"], p1["n_tests"]))
    ests.append(count("P2: cells where SEQ is above MV (prediction disconfirmed)", p2["n_disconfirmed"], p2["n_tests"]))
    for scenario in ("S4", "S6"):
        cells = [c for c in p2["cells"] if c["scenario"] == scenario]
        top = max(cells, key=lambda c: c["diff_mean"])
        lo, hi = top["t95"]
        ests.append(est(f"P2: largest Delta_SEQ - Delta_MV in {scenario} (B = {top['budget']}, lambda 0)", top["diff_mean"], lo=lo, hi=hi,
                        display=s4(top["diff_mean"]), interval_display=bracket(lo, hi)))
    ests.append(count("P3: consecutive-lambda decreases of Delta_MV (2 inconclusive, none increased)", p3["n_supported"], p3["n_tests"]))
    return {
        "id": "EXP-002",
        "title": reg["EXP-002"]["title"],
        "status": "confirmatory, complete (primary experiment)",
        "verdict": f"{a2['verdict']}. P1 {p1['verdict']}; P2 {p2['verdict']}; P3 {p3['verdict']}.",
        "estimates": ests,
        "claim_ids": claims.get("EXP-002", []),
        "report_path": reg["EXP-002"]["report_path"],
        "notes": [
            "Delta is the accuracy change against SINGLE (one reasoner, one call), mean over 30 seed-runs of 2000 items; intervals are seed-level t 95% intervals.",
            "The 32 rejected cells (20 MV, 12 SEQ) are all in S4 and S6 and share seeds and nested budgets, so they describe three connected patterns rather than 32 independent findings.",
            "P2 was disconfirmed: where MV degrades, SEQ loses less than MV. This concerns one sequential rule (strict leader, w = 0.5).",
            "CW is descriptive: its advantage follows from the assumed confidence model (delta = 1), not from aggregation.",
        ],
    }


def exp003(a3, claims, reg):
    sc = a3["sign_counts_by_model"]
    ests = [count("Matched cells where the sign of Delta_MV differs between models", a3["n_matched_cells_disagree"], a3["n_matched_cells"])]
    for model, name in (("bahadur", "Bahadur"), ("mixture", "Symmetric mixture"), ("common_shock", "Common shock"), ("beta", "Beta")):
        ests.append(count(f"{name}: cells with negative exact Delta_MV", sc[model]["negative"], sc[model]["cells"]))
    for model, name in (("bahadur", "Bahadur"), ("mixture", "Symmetric mixture")):
        cell = next(c for c in a3["negative_cells"] if (c["model"], c["p"], c["r"], c["n"]) == (model, 0.7, 0.4, 5))
        ests.append(est(f"{name}: exact Delta_MV at p = 0.7, r = 0.4, n = 5", cell["delta_theory"], display=s5(cell["delta_theory"])))
    return {
        "id": "EXP-003",
        "title": reg["EXP-003"]["title"],
        "status": "confirmatory, complete",
        "verdict": a3["verdict"] + "; the EXP-002 degradation claims are restricted to the common-shock and two-class mixture families.",
        "estimates": ests,
        "claim_ids": claims.get("EXP-003", []),
        "report_path": reg["EXP-003"]["report_path"],
        "notes": [
            "Signs are judged on exact closed-form values, so these numbers have no sampling interval; a 30-seed Monte Carlo check agreed in sign wherever its interval excluded 0.",
            "Below-chance item mass is neither necessary nor sufficient across models: Bahadur degrades without it, Beta never degrades with it.",
        ],
    }


def exp004(a4, claims, reg):
    tie = next(c for c in a4["checks"] if c["factor_level"].startswith("tie_abstain_wrong") and c["budget"] == 8)
    w25 = next(c for c in a4["descriptive_mean_sign_changes"] if c["variant"] == "w_0p25" and c["rule"] == "SEQ" and c["budget"] == 31)
    s1b2 = next(c for c in a4["descriptive_mean_sign_changes"] if c["variant"] == "tie_abstain_wrong" and c["scenario"] == "S1" and c["budget"] == 2)
    cost = {c["rule"]: c for c in a4["cost_descriptive"] if c["scenario"] == "S1" and c["lambda"] == 0.0 and c["calls"] == 31}
    return {
        "id": "EXP-004",
        "title": reg["EXP-004"]["title"],
        "status": "confirmatory, complete (optional experiment); null result under the frozen rule",
        "verdict": a4["verdict"],
        "estimates": [
            count("Frozen-rule checks with a sign reversal", a4["n_reversed"], a4["n_checks"]),
            count("Holm-significant EXP-002 cells in scope", a4["n_significant_exp002_cells_in_scope"], display=f"{a4['n_significant_exp002_cells_in_scope']} of the 32"),
            est("Tie abstains and counts as wrong: S4, lambda 0, MV, B = 8", tie["variant_delta"], lo=tie["variant_t95"][0], hi=tie["variant_t95"][1],
                display=s4(tie["variant_delta"]), interval_display=bracket(*tie["variant_t95"])),
            est("Same cell under the coin tie rule (EXP-004 reference; its interval is not tabulated in the committed analysis)", tie["exp002_delta"], display=s4(tie["exp002_delta"])),
            est("Weaker herding w = 0.25: S4, lambda 0, SEQ, B = 31 (descriptive)", w25["variant_delta"], lo=w25["variant_t95"][0], hi=w25["variant_t95"][1],
                display=s4(w25["variant_delta"]), interval_display=bracket(*w25["variant_t95"])),
            est("Tie abstains and counts as wrong: S1, lambda 0, MV, B = 2 (descriptive)", s1b2["variant_delta"], lo=s1b2["variant_t95"][0], hi=s1b2["variant_t95"][1],
                display=s4(s1b2["variant_delta"]), interval_display=bracket(*s1b2["variant_t95"])),
            est("Cost with messages read: SEQ at 31 calls, S1 (descriptive)", cost["SEQ"]["calls_plus_messages"], unit="units",
                display=f"{cost['SEQ']['calls_plus_messages']:.0f}"),
            est("Accuracy of SEQ at 31 calls, S1, lambda 0 (descriptive mean; see the curves for intervals of the change)", cost["SEQ"]["accuracy"], display=f"{cost['SEQ']['accuracy']:.4f}"),
            est("Accuracy of MV at 31 calls, S1, lambda 0 (descriptive mean; see the curves for intervals of the change)", cost["MV"]["accuracy"], display=f"{cost['MV']['accuracy']:.4f}"),
        ],
        "claim_ids": claims.get("EXP-004", []),
        "report_path": reg["EXP-004"]["report_path"],
        "notes": [
            "The scope is narrow: only 3 of the 32 significant EXP-002 cells lie in EXP-004's scenarios and lambda levels, none in S6, and 15 of the 18 checks could not have failed because MV does not depend on tau or w.",
            "Accuracies and costs on the cost rows are means over 30 seed-runs; the report gives their spread.",
        ],
    }


def exploratory(x15, x16, claims_x15, claims_x16):
    rows = {(r["scenario"], r["lambda"]): r for r in x15["X1_finite_budget"]["rows"]}
    s6_0, s6_25 = rows[("S6", 0.0)], rows[("S6", 0.25)]
    j15 = {
        "id": "J-0015",
        "title": "Finite-budget closed forms (exploratory, after all verdicts)",
        "status": "exploratory (M4); changes no frozen verdict",
        "verdict": "no frozen rule (exploratory)",
        "estimates": [
            est("S6, lambda 0: exact Delta_MV at n = 31", s6_0["delta_exact_n31"], display=s5(s6_0["delta_exact_n31"])),
            est("S6, lambda 0: large-n limit", s6_0["delta_limit"], display=s5(s6_0["delta_limit"])),
            est("S6, lambda 0.25: exact Delta_MV at n = 31", s6_25["delta_exact_n31"], display=s5(s6_25["delta_exact_n31"])),
            est("S6, lambda 0.25: exact Delta_MV at n = 301", s6_25["delta_exact_n301"], display=s5(s6_25["delta_exact_n301"])),
            est("S6, lambda 0.25: large-n limit", s6_25["delta_limit"], display=s5(s6_25["delta_limit"])),
        ],
        "claim_ids": claims_x15,
        "report_path": SRC["x15"],
        "notes": ["Exact closed-form values; no sampling interval applies. With correlation, the sign at B = 31 can differ from the large-budget limit."],
    }
    def cw(delta_conf, scenario):
        return next(r for r in x16["rows"] if r["delta_conf"] == delta_conf and r["scenario"] == scenario and r["budget"] == 31)
    ests = []
    for dc in (0.0, 0.5):
        for scenario in ("S4", "S6"):
            r = cw(dc, scenario)
            ests.append(est(f"CW at delta = {dc:g}: {scenario}, lambda 0, B = 31", r["delta_mean"], lo=r["t95"][0], hi=r["t95"][1],
                            display=s4(r["delta_mean"]), interval_display=bracket(*r["t95"])))
    j16 = {
        "id": "J-0016",
        "title": "Confidence informativeness sweep for CW (exploratory, after all verdicts)",
        "status": "exploratory (M4), 10 exploratory seeds per cell; changes no frozen verdict",
        "verdict": "no frozen rule (exploratory)",
        "estimates": ests,
        "claim_ids": claims_x16,
        "report_path": SRC["x16"],
        "notes": ["With uninformative confidence (delta = 0) CW degrades like MV; CW's superiority in EXP-002 is explained by the assumed delta = 1."],
    }
    return [j15, j16]


def curves(a2):
    """Every EXP-002 cell of the generated report table, strings kept as printed."""
    text = read("r2")
    sec = text.split("## Accuracy and paired difference from SINGLE", 1)[1].split("\n## ", 1)[0]
    msgs = {}
    with open(REPO / SRC["m2"], newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            msgs[(r["rule"], int(r["budget"]))] = int(r["messages_per_item"])
    points = []
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 11 or not re.fullmatch(r"S[1-6]", cells[0]):
            continue
        scen, lam, rule, calls, acc, _theory, delta, _sd, lo, hi, seeds = cells
        points.append({
            "scenario": scen, "lambda": float(lam), "lambda_display": lam, "rule": rule, "budget": int(calls),
            "messages_per_item": msgs[(rule, int(calls))], "n_seeds": int(seeds),
            "accuracy": float(acc), "accuracy_display": acc,
            "delta": float(delta), "delta_display": delta,
            "ci_low": float(lo), "ci_high": float(hi), "ci_low_display": lo, "ci_high_display": hi,
        })
    if len(points) != 6 * 4 * (1 + 3 * 6):
        raise SystemExit(f"unexpected number of EXP-002 table rows: {len(points)}")
    return {
        "source": SRC["r2"],
        "experiment": "EXP-002",
        "interval": "seed-level t 95% interval over 30 seed-runs of 2000 items",
        "points": points,
    }


def scenarios_from_config():
    cfg = load("cfg2")
    out = []
    for s in cfg["scenarios"]:
        p_hard = s["p_hard"] if s["p_hard"] is not None else s["p_easy"]
        mu = (1 - s["h"]) * s["p_easy"] + s["h"] * p_hard
        out.append({"id": s["id"], "p_easy": s["p_easy"], "h": s["h"], "p_hard": p_hard, "mu": round(mu, 10),
                    "homogeneous": s["h"] == 0.0})
    return out, cfg


def assumptions(cfg, scen):
    def sdesc(s):
        if s["homogeneous"]:
            return f"homogeneous, p = {s['p_easy']:g}"
        return f"mixture, p_easy = {s['p_easy']:g}, h = {s['h']:g}, p_hard = {s['p_hard']:g} (mean competence {s['mu']:.2f})"
    src = SRC["cfg2"]
    out = [{"name": f"Scenario {s['id']}", "value": sdesc(s), "source": src} for s in scen]
    out += [
        {"name": "Correlation (common-shock adoption) lambda", "value": ", ".join(f"{x:g}" for x in cfg["lambdas"]), "source": src},
        {"name": "Budgets B (reasoner calls per item)", "value": ", ".join(str(b) for b in cfg["budgets"]), "source": src},
        {"name": "Herding probability w (SEQ)", "value": f"{cfg['w']:g}", "source": src},
        {"name": "Confidence model delta and tau (CW)", "value": f"delta = {cfg['delta']:g}, tau = {cfg['tau']:g}; an assumption, not calibrated to any real reasoner", "source": src + "; protocol section 2.3"},
        {"name": "Seeds and items", "value": f"{cfg['n_seeds']} seeds (SeedSequence({cfg['seed_entropy']}).spawn({cfg['n_seeds']}), shared across cells) x {cfg['n_items']} items per run", "source": src},
        {"name": "Reasoners", "value": "synthetic Bernoulli answerers on binary items; not language models and not people", "source": "research/protocol.md section 9"},
    ]
    return out


def limitations():
    ms = read("ms")
    sec = ms.split("## 7. Limitations and threats to validity", 1)[1].split("\n## ", 1)[0]
    out = []
    for line in sec.splitlines():
        if line.startswith("- "):
            out.append(line[2:].replace("**", "").replace("`", "").strip())
    if not out:
        raise SystemExit("no limitations found in manuscript section 7")
    return out


def exceptions():
    """Display strings that are not printed verbatim in the manuscript. Each
    one's decimals appear in the named committed file (checked by the test)."""
    return [
        {"text": "[-0.0433, -0.0371]", "source": SRC["rep4"], "note": "t 95% interval of the EXP-004 tie-rule cell; the manuscript prints only the estimate, the EXP-004 report prints the bounds."},
        {"text": "[-0.2415, -0.2349]", "source": SRC["an4"], "note": "t 95% interval of a descriptive EXP-004 cell; printed in the EXP-004 analysis table, not in the manuscript."},
        {"text": "[+0.0257, +0.0366]", "source": SRC["supp"], "note": "Interval printed in supplementary Table S4c; the manuscript body prints only the estimate."},
        {"text": "[+0.0482, +0.0626]", "source": SRC["supp"], "note": "Interval printed in supplementary Table S4c; the manuscript body prints only the estimate."},
    ]


def build() -> dict:
    a1, a2, a3, a4 = (load(k) for k in ("a1", "a2", "a3", "a4"))
    claims, reg = claims_by_exp(), registry()
    scen, cfg = scenarios_from_config()
    experiments = [exp001(a1, claims, reg), exp002(a2, claims, reg), exp003(a3, claims, reg), exp004(a4, claims, reg)]
    experiments += exploratory(load("x15"), load("x16"), claims_matching(r"J-0015"), claims_matching(r"J-0016"))
    rejected = [{"scenario": c["scenario"], "lambda": c["lambda"], "rule": c["rule"], "budget": c["budget"]} for c in a2["rejected_cells"]]
    if len(rejected) != a2["n_rejected"]:
        raise SystemExit("rejected-cell list and count disagree")
    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "PARADOX",
        "question": "Under an equal compute budget, when does aggregation of fallible reasoners improve or degrade accuracy?",
        "status_label": ("Independent research manuscript / preprint draft, not peer-reviewed. Four preregistered experiments "
                         "(EXP-001 to EXP-004) ran in full under protocols frozen on 2026-11-24. Synthetic reasoners, not language models. "
                         "Full-text owner review of the manuscript is pending."),
        "code_revision": revision(),
        "sources": [{"path": SRC[k], "sha256": sha(k)} for k in sorted(SRC, key=lambda k: SRC[k])],
        "experiments": experiments,
        "assumptions": assumptions(cfg, scen),
        "limitations": limitations(),
        "curves": curves(a2),
        "scenarios": scen,
        "holm_rejected": rejected,
        "display_exceptions": exceptions(),
        "sandbox": {
            "port_of": "src/paradox/generator.py (generate_run) and src/paradox/rules.py (single, majority, sequential)",
            "rules": ["SINGLE", "MV", "SEQ"],
            "not_ported": "CW (needs NumPy's ziggurat normal sampler) and DELIB (dropped at the freeze)",
            "fixture": "demo/src/fixtures/engine_fixture.json (scripts/export_sandbox_fixture.py)",
            "tolerance": "exact: identical draws and identical decision counts",
            "confirmatory_seeds_first": cfg_seeds(),
        },
    }


def cfg_seeds() -> list[int]:
    seeds = load("rm2").get("seeds")
    if not seeds:
        raise SystemExit("seeds not found in results/EXP-002/run_manifest.json")
    return [int(s) for s in seeds[:3]]


def render() -> str:
    return json.dumps(build(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("results.json up to date" if ok else "results.json differs from a fresh export")
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    doc = json.loads(text)
    print(f"wrote {OUT.relative_to(REPO)}: {len(doc['experiments'])} entries, "
          f"{sum(len(e['estimates']) for e in doc['experiments'])} estimates, {len(doc['curves']['points'])} curve points")
    return 0


if __name__ == "__main__":
    sys.exit(main())

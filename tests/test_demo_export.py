# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M5 consistency (master prompt section 11.6): the demo shows the same
numbers as the manuscript and the reports.

1. Re-running the export in memory reproduces the committed
   demo/public/data/results.json byte for byte.
2. Every ``display`` and ``interval_display`` string appears verbatim in
   research/paper/manuscript.md, or is a listed exception whose decimals all
   appear in its stated committed source file.
3. Every EXP-002 curve point appears, as printed, in its row of the generated
   report table results/EXP-002/report.md.
4. The sandbox fixture is current, and the public texts carry no decimal that
   is absent from the manuscript, the supplementary appendix and the reports.
"""

import importlib.util
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "demo" / "public" / "data" / "results.json"
MANUSCRIPT = (REPO / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")
DECIMAL = re.compile(r"[+-]?\d+\.\d+")


def _module(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _doc():
    return json.loads(RESULTS.read_text(encoding="utf-8"))


def test_export_reproduces_committed_results_json():
    assert _module("export_demo_data").render() == RESULTS.read_text(encoding="utf-8")


def test_sandbox_fixture_is_current():
    mod = _module("export_sandbox_fixture")
    assert mod.build() == mod.OUT.read_text(encoding="utf-8")


def test_every_entry_has_status_verdict_and_known_claims():
    doc = _doc()
    ids = [e["id"] for e in doc["experiments"]]
    assert ids[:4] == ["EXP-001", "EXP-002", "EXP-003", "EXP-004"]
    claims = (REPO / "research" / "claims_register.csv").read_text(encoding="utf-8")
    for e in doc["experiments"]:
        assert e["status"] and e["verdict"]
        for c in e["claim_ids"]:
            assert f"\n{c}," in claims


def test_display_strings_are_verbatim_in_manuscript_or_documented():
    doc = _doc()
    exceptions = {x["text"]: x for x in doc["display_exceptions"]}
    for x in exceptions.values():
        src = (REPO / x["source"]).read_text(encoding="utf-8")
        assert x["note"]
        for token in DECIMAL.findall(x["text"]):
            assert token in src, (x["text"], token, x["source"])
    checked = 0
    for e in doc["experiments"]:
        for est in e["estimates"]:
            for key in ("display", "interval_display"):
                s = est[key]
                if s is None:
                    continue
                checked += 1
                assert s in MANUSCRIPT or s in exceptions, (e["id"], est["label"], key, s)
    assert checked >= 59


def test_curve_points_match_the_generated_report_rows():
    doc = _doc()
    report = (REPO / doc["curves"]["source"]).read_text(encoding="utf-8")
    for p in doc["curves"]["points"]:
        prefix = f"| {p['scenario']} | {p['lambda_display']} | {p['rule']} | {p['budget']} | {p['accuracy_display']} |"
        rows = [ln for ln in report.splitlines() if ln.startswith(prefix)]
        assert len(rows) == 1, prefix
        row = rows[0]
        for s in (p["delta_display"], p["ci_low_display"], p["ci_high_display"]):
            assert f"| {s} |" in row, (prefix, s)
        assert float(p["delta_display"]) == p["delta"]


def test_public_texts_carry_only_traced_decimals():
    corpus = MANUSCRIPT + (REPO / "research" / "paper" / "supplementary.md").read_text(encoding="utf-8")
    for n in range(1, 5):
        corpus += (REPO / "research" / "experiments" / f"EXP-00{n}" / "report.md").read_text(encoding="utf-8")
    # Version strings and tolerances that are not results.
    allowed = {"1.0", "1.0.0", "1.2.0", "0.0.0", "0.1.0"}
    for rel in ("README.md", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        text = (REPO / rel).read_text(encoding="utf-8")
        for token in DECIMAL.findall(text):
            if token in allowed:
                continue
            assert token in corpus, (rel, token)

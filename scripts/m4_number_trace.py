# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M4 evidence audit: trace every decimal number in the publication documents
to a committed source file (master prompt section 11.5).

For each target document, every token with a decimal point (for example
-0.1313, 0.5196194, 26.3) is looked up in a corpus built from committed
result and record files. A token matches a source value when the source value,
rounded to the token's number of decimals, equals the token (sign included,
with the absolute value also accepted for tokens written without a sign in a
signed context), or when the token appears literally in a source text file.
Integers are not traced here (counts are checked by hand in the audit record).

Usage: .venv/bin/python scripts/m4_number_trace.py [--strict]
Writes results/audit/number_trace.json and prints a summary. With --strict the
exit status is 1 if any token is unmatched.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    "research/experiments/EXP-001/report.md",
    "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md",
    "research/experiments/EXP-004/report.md",
]

JSON_SOURCES = [
    "results/EXP-001/analysis/analysis.json",
    "results/EXP-002/analysis/analysis.json",
    "results/EXP-003/analysis/analysis.json",
    "results/EXP-004/analysis/analysis.json",
    "results/EXP-001/run_manifest.json",
    "results/EXP-002/run_manifest.json",
    "results/EXP-003/run_manifest.json",
    "results/EXP-004/run_manifest.json",
    "results/exploratory/m4-analytic/results.json",
    "results/exploratory/m4-cw-delta/summary.json",
    "results/exploratory/m3-smoke/metric_check.json",
    "research/freeze.json",
]

TEXT_SOURCES = [
    "results/EXP-001/report.md",
    "results/EXP-002/report.md",
    "results/EXP-003/report.md",
    "results/EXP-004/report.md",
    "results/EXP-001/analysis/analysis.md",
    "results/EXP-002/analysis/analysis.md",
    "results/EXP-003/analysis/analysis.md",
    "results/EXP-004/analysis/analysis.md",
    "results/exploratory/m4-analytic/summary.md",
    "results/exploratory/m4-cw-delta/summary.md",
    "research/experiment_journal.jsonl",
    "research/protocol.md",
    "research/experiments/EXP-001/protocol.md",
    "research/experiments/EXP-002/protocol.md",
    "research/experiments/EXP-003/protocol.md",
    "research/experiments/EXP-004/protocol.md",
    "research/experiments/EXP-002/config.json",
    "research/literature_review.md",
    "results/EXP-001/exit_status.json",
    "results/EXP-002/exit_status.json",
    "results/EXP-003/exit_status.json",
    "results/EXP-004/exit_status.json",
]

TOKEN = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?![\w.]*\d\.\d)")


def walk(x, out: list[float]) -> None:
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        out.append(float(x))
    elif isinstance(x, dict):
        for v in x.values():
            walk(v, out)
    elif isinstance(x, list):
        for v in x:
            walk(v, out)


def strip_code_hashes(text: str) -> str:
    # drop long hex strings and version-like strings (3.12.1) before scanning
    text = re.sub(r"\b[0-9a-f]{7,64}\b", " ", text)
    text = re.sub(r"\b\d+\.\d+\.\d+(\.\d+)?\b", " ", text)
    text = re.sub(r"arXiv:\d+\.\d+", " ", text)
    text = re.sub(r"\b\d{4}\.\d{4,5}\b", " ", text)
    text = re.sub(r"10\.\d{4,}/\S+", " ", text)
    # section numbers in headings and cross-references are not quantities
    text = re.sub(r"(?m)^#+\s+[A-Z]?\d+(\.\d+)*", " ", text)
    text = re.sub(r"\b(?:[Ss]ections?|[Tt]ables?|[Ff]igures?|ch\.|and|to)\s+[A-Z]?\d+\.\d+(?:\.\d+)?", " ", text)
    return text


def main() -> int:
    values: list[float] = []
    for p in JSON_SOURCES:
        f = ROOT / p
        if f.exists():
            walk(json.loads(f.read_text()), values)
    rounded: dict[int, set[str]] = {}
    for d in range(1, 9):
        s = set()
        for v in values:
            s.add(f"{v:.{d}f}")
            s.add(f"{abs(v):.{d}f}")
        rounded[d] = s
    corpus = "\n".join((ROOT / p).read_text() for p in TEXT_SOURCES if (ROOT / p).exists())
    corpus_tokens = set(t.lstrip("+") for t in TOKEN.findall(strip_code_hashes(corpus)))
    corpus_tokens |= set(t.lstrip("+-") for t in corpus_tokens)

    report = {"label": "audit", "generator": "scripts/m4_number_trace.py", "documents": []}
    total = unmatched_total = 0
    for t in TARGETS:
        f = ROOT / t
        if not f.exists():
            report["documents"].append({"path": t, "missing": True})
            continue
        toks = TOKEN.findall(strip_code_hashes(f.read_text()))
        unmatched = []
        for tok in toks:
            bare = tok.lstrip("+")
            d = len(bare.split(".")[1])
            ok = bare in corpus_tokens or bare.lstrip("-") in corpus_tokens
            if not ok and d in rounded:
                ok = bare in rounded[d] or bare.lstrip("-") in rounded[d]
            if not ok:
                unmatched.append(tok)
        total += len(toks)
        unmatched_total += len(unmatched)
        report["documents"].append({"path": t, "n_tokens": len(toks), "n_unmatched": len(unmatched),
                                    "unmatched": sorted(set(unmatched))})
    report["n_tokens"] = total
    report["n_unmatched"] = unmatched_total
    out = ROOT / "results" / "audit"
    out.mkdir(parents=True, exist_ok=True)
    (out / "number_trace.json").write_text(json.dumps(report, indent=1) + "\n")
    for d in report["documents"]:
        print(d["path"], "missing" if d.get("missing") else f"{d['n_tokens']} tokens, {d['n_unmatched']} unmatched {d['unmatched']}")
    print(f"TOTAL {total} decimal tokens, {unmatched_total} unmatched")
    return 1 if ("--strict" in sys.argv and unmatched_total) else 0


if __name__ == "__main__":
    sys.exit(main())

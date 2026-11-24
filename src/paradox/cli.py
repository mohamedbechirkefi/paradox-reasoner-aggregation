# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Command line: ``paradox smoke | run | report | test``.

Exit codes: 0 success; 1 failure; 2 usage or schema error; 3 refused by a
guard (unfrozen protocol, exploratory output path, held-out seeds).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .runner import REPO_ROOT, GuardError, execute
from .schema import SchemaError

SMOKE_CONFIG = REPO_ROOT / "configs" / "exploratory" / "smoke.json"
SMOKE_OUT = REPO_ROOT / "results" / "exploratory" / "smoke"


def _run(config: Path, out: Path, argv: list[str], pdf: bool) -> int:
    try:
        manifest = execute(config, out, command=argv)
    except GuardError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    except SchemaError as exc:
        print(f"SCHEMA ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"{manifest['label']} run of {manifest['experiment_id']} finished in {manifest['runtime_s']:.2f} s; "
          f"peak RSS {manifest['peak_rss_bytes'] / 2**20:.1f} MiB; outputs in {out}")
    from .report import build_report

    res = build_report(out, pdf=pdf)
    print(f"report: {res['report_md']}" + (f"; pdf: {res['report_pdf']}" if "report_pdf" in res else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="paradox", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("smoke", help="run the exploratory smoke matrix (protocol section 6.1) and build its report")
    sp.add_argument("--out", type=Path, default=SMOKE_OUT)
    sp.add_argument("--pdf", action="store_true")
    rp = sub.add_parser("run", help="run a config; refuses confirmatory configs while the protocol is unfrozen")
    rp.add_argument("--config", type=Path, required=True)
    rp.add_argument("--out", type=Path, required=True)
    rp.add_argument("--pdf", action="store_true")
    rep = sub.add_parser("report", help="build report.md (and optionally a PDF) from a results folder")
    rep.add_argument("results_dir", type=Path)
    rep.add_argument("--pdf", action="store_true")
    tp = sub.add_parser("test", help="run the test suite (pytest)")
    tp.add_argument("pytest_args", nargs="*")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0) and 2
    full = ["paradox", *argv]
    if args.cmd == "smoke":
        return _run(SMOKE_CONFIG, args.out, full, args.pdf)
    if args.cmd == "run":
        return _run(args.config, args.out, full, args.pdf)
    if args.cmd == "report":
        from .report import build_report

        try:
            res = build_report(args.results_dir, pdf=args.pdf)
        except SchemaError as exc:
            print(f"SCHEMA ERROR: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(res, indent=1))
        return 0
    if args.cmd == "test":
        return subprocess.run([sys.executable, "-m", "pytest", str(REPO_ROOT / "tests"), *args.pytest_args], cwd=REPO_ROOT).returncode
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

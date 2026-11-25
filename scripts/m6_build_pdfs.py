# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Build the manuscript, supplementary and experiment-report PDFs (M6).

Uses ``paradox.report.build_pdf`` (pandoc to Typst, D-002). With ``--png DIR``
every page is also rendered to PNG in DIR for visual inspection; the
intermediate ``.typ`` files are removed afterwards in every case. Page counts
and metadata are checked separately (pypdf is not a project dependency).

    .venv/bin/python scripts/m6_build_pdfs.py [--png DIR]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from paradox.report import build_pdf

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "ms": ROOT / "research/paper/manuscript.md",
    "supp": ROOT / "research/paper/supplementary.md",
    **{f"exp{i}": ROOT / f"research/experiments/EXP-00{i}/report.md" for i in range(1, 5)},
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", type=Path, default=None, help="render every page to PNG in this folder")
    ap.add_argument("--ppi", type=int, default=60)
    args = ap.parse_args()
    for key, md in DOCS.items():
        pdf = Path(build_pdf(md, keep_typ=True))
        typ = md.with_suffix(".typ")
        try:
            if args.png:
                import typst

                args.png.mkdir(parents=True, exist_ok=True)
                typst.compile(str(typ), output=str(args.png / f"{key}-{{p}}.png"), format="png", ppi=args.ppi,
                              root=str(md.parent))
        finally:
            typ.unlink()
        print(f"{pdf.relative_to(ROOT)}: {pdf.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

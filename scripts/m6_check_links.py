# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Check every relative link in the tracked Markdown files (M6).

A link ``[text](target)`` whose target is not a URL must resolve to an
existing file or folder, relative to the Markdown file; an ``#anchor`` must
match a heading of the target file (GitHub slug rules). Links inside code
spans and fenced code blocks are ignored.

    .venv/bin/python scripts/m6_check_links.py      # prints a summary; exit 1 on a broken link
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!\!)\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
SCHEMES = ("http://", "https://", "mailto:", "data:")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / line for line in out.splitlines() if line and "node_modules/" not in line]


def _strip_code(text: str) -> str:
    text = re.sub(r"^(```|~~~).*?^\1", "", text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


def slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    for line in _strip_code(md.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        base = slug(m.group(1))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    for m in re.finditer(r'<a\s+(?:id|name)="([^"]+)"', md.read_text(encoding="utf-8")):
        out.add(m.group(1))
    return out


def check(files: list[Path] | None = None) -> tuple[int, list[str]]:
    files = tracked_markdown() if files is None else files
    count, broken = 0, []
    for md in files:
        text = _strip_code(md.read_text(encoding="utf-8"))
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for m in LINK.finditer(text):
            target = m.group(1) or m.group(2)
            if target.startswith(SCHEMES):
                continue
            count += 1
            path_part, _, frag = target.partition("#")
            dest = md if not path_part else (md.parent / unquote(path_part)).resolve()
            rel = md.relative_to(ROOT)
            if not dest.exists():
                broken.append(f"{rel}: {target} (missing file)")
            elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                broken.append(f"{rel}: {target} (missing anchor)")
    return count, broken


def main() -> int:
    files = tracked_markdown()
    count, broken = check(files)
    for b in broken:
        print("BROKEN", b)
    print(f"{len(files)} Markdown files, {count} relative links, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())

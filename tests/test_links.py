# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""M6: every relative link in the tracked Markdown files resolves
(scripts/m6_check_links.py), and the checker detects a broken link."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("m6_check_links", ROOT / "scripts" / "m6_check_links.py")
links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(links)


def test_every_relative_link_resolves():
    count, broken = links.check()
    assert count > 0
    assert broken == []


def test_checker_detects_missing_file_and_anchor(tmp_path):
    (tmp_path / "target.md").write_text("# A heading\n\ntext\n", encoding="utf-8")
    md = tmp_path / "doc.md"
    md.write_text(
        "[ok](target.md) [ok anchor](target.md#a-heading) [bad](missing.md) [bad anchor](target.md#nope) "
        "[web](https://example.org) `[code](ignored.md)`\n",
        encoding="utf-8",
    )
    count, broken = _check_outside_root(md)
    assert count == 4
    assert len(broken) == 2


def _check_outside_root(md: Path):
    # check() reports paths relative to ROOT; patch ROOT for a file outside the repository.
    old = links.ROOT
    links.ROOT = md.parent
    try:
        return links.check([md])
    finally:
        links.ROOT = old

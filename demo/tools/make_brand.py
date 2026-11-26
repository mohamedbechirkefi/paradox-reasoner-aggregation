# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Build the PARADOX brand SVGs (mark, favicon, wordmark lockups).

The mark is a tally gate: four strokes struck by a descending diagonal at
30 degrees. The wordmark is "Paradox" in Zilla Slab Bold (SIL OFL 1.1,
from node_modules/@fontsource/zilla-slab) converted to outlines, with the
x in seal red as a ballot cross. Requires fontTools. Run from demo/:
    python3 tools/make_brand.py
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path("public/brand")
INK, RED, SLATE, CHALK, YELLOW = "#1E2B3C", "#A3262C", "#25352F", "#ECEFE6", "#E2C04A"
HEAD = "<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->\n"


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def bar(x, y0, y1, w):
    """Vertical bar with round ends, as a path."""
    r = w / 2
    return (f"M{f(x - r)} {f(y0 + r)}A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y0 + r)}"
            f"V{f(y1 - r)}A{f(r)} {f(r)} 0 0 1 {f(x - r)} {f(y1 - r)}Z")


def strike(cx, cy, length, w, deg):
    """Bar of width w through (cx, cy) at angle deg (descending), round ends."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    r = w / 2
    ax, ay = cx - ux * length / 2, cy - uy * length / 2
    bx, by = cx + ux * length / 2, cy + uy * length / 2
    p1 = (ax + nx * r, ay + ny * r)
    p2 = (bx + nx * r, by + ny * r)
    p3 = (bx - nx * r, by - ny * r)
    p4 = (ax - nx * r, ay - ny * r)
    return (f"M{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}A{f(r)} {f(r)} 0 0 0 {f(p3[0])} {f(p3[1])}"
            f"L{f(p4[0])} {f(p4[1])}A{f(r)} {f(r)} 0 0 0 {f(p1[0])} {f(p1[1])}Z")


def mark_paths():
    bars = [bar(x, 52, 204, 26) for x in (74, 110, 146, 182)]
    s = strike(128, 128, 214, 26, 30)
    return bars, s


def svg(w, h, body, title):
    return (HEAD + f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
            f"<title>{title}</title>{body}</svg>\n")


def mark(bar_fill, strike_fill):
    bars, s = mark_paths()
    return f'<path fill="{bar_fill}" d="{"".join(bars)}"/><path fill="{strike_fill}" d="{s}"/>'


def favicon():
    bars = "".join(bar(x, 58, 198, 32) for x in (78, 128, 178))
    s = strike(128, 128, 196, 30, 30)
    return (f'<rect width="256" height="256" rx="56" fill="{SLATE}"/>'
            f'<path fill="{CHALK}" d="{bars}"/><path fill="{YELLOW}" d="{s}"/>')


def wordmark(fill, xfill, x0, baseline, size):
    font = TTFont("node_modules/@fontsource/zilla-slab/files/zilla-slab-latin-700-normal.woff")
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    sc = size / upm
    hmtx = font["hmtx"]
    x = x0
    parts = []
    for ch in "Paradox":
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=f)
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, baseline)))
        parts.append((ch, pen.getCommands()))
        x += hmtx[g][0] * sc - size * 0.005
    body = "".join(f'<path fill="{xfill if ch == "x" else fill}" d="{d}"/>' for ch, d in parts)
    return body, x


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "mark.svg").write_text(svg(256, 256, mark(INK, RED), "PARADOX mark"))
    (OUT / "mark-mono.svg").write_text(svg(256, 256, mark(INK, INK), "PARADOX mark, one colour"))
    (OUT / "mark-reversed.svg").write_text(svg(256, 256, f'<rect width="256" height="256" fill="{SLATE}"/>' + mark(CHALK, YELLOW), "PARADOX mark on slate"))
    (OUT / "favicon.svg").write_text(svg(256, 256, favicon(), "PARADOX"))
    for name, bg, fg, xr, mk in (
        ("lockup.svg", None, INK, RED, (INK, RED)),
        ("lockup-mono.svg", None, INK, INK, (INK, INK)),
        ("lockup-reversed.svg", SLATE, CHALK, YELLOW, (CHALK, YELLOW)),
    ):
        words, end = wordmark(fg, xr, 288, 186, 168)
        w = math.ceil(end + 24)
        back = f'<rect width="{w}" height="256" fill="{bg}"/>' if bg else ""
        (OUT / name).write_text(svg(w, 256, back + mark(*mk) + words, "PARADOX"))
    print("brand written to", OUT)


if __name__ == "__main__":
    main()

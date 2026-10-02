"""Small helpers for review diagrams: boxes that fit their text, and edges between them.

Import from a throwaway script and print the result:

    import sys; sys.path.insert(0, "/home/jonny/.claude/skills/review-pr/scripts")
    from svg import Diagram
    d = Diagram(width=940)
    a = d.box(40, 40, ["queue group-anomaly-evaluation"], "bad", mono=True)
    b = d.box(560, 40, ["queue group-anomaly-evaluate"], "ok", mono=True)
    d.edge(a, b, "ok")
    print(d.svg())

Classes are the page's own (see SKILL.md); nothing here sets colours or fonts.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

# Upper-bound glyph widths for the page's diagram fonts (render.py CSS):
# mono is 12px (0.6em per glyph), body text is 13px.
CHAR_W = {"mono": 7.4, "sans": 7.6, "label": 7.4}
LINE_H = 17
PAD_X = 14
PAD_Y = 12


def text_width(text: str, kind: str = "sans") -> float:
    return len(text) * CHAR_W[kind]


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


class Diagram:
    def __init__(self, width: int = 940) -> None:
        self.width = width
        self.parts: list[str] = []
        self.bottom = 0.0

    def _track(self, y: float) -> None:
        self.bottom = max(self.bottom, y)

    def box(self, x: float, y: float, lines: list[str], cls: str = "", *, mono: bool = False,
            min_w: float = 0) -> Box:
        """A box wide enough for its longest line (and at least min_w, to line up a column)."""
        kind = "mono" if mono else "sans"
        w = max(min_w, max(text_width(line, kind) for line in lines) + 2 * PAD_X)
        h = len(lines) * LINE_H + 2 * PAD_Y - 4
        if x + w > self.width:
            raise ValueError(f"box {lines[0]!r} ends at {x + w:.0f}, past the diagram width {self.width}")
        b = Box(x, y, w, h)
        rcls = f"box {cls}".strip()
        self.parts.append(f'<rect class="{rcls}" rx="8" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}"/>')
        first = y + PAD_Y + 12
        tcls = ' class="mono"' if mono else ""
        for i, line in enumerate(lines):
            self.parts.append(f'<text{tcls} x="{b.cx:.0f}" y="{first + i * LINE_H:.0f}" text-anchor="middle">{escape(line)}</text>')
        self._track(y + h)
        return b

    def text(self, x: float, y: float, text: str, cls: str = "", anchor: str = "start") -> None:
        c = f' class="{cls}"' if cls else ""
        self.parts.append(f'<text{c} x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}">{escape(text)}</text>')
        self._track(y + 6)

    def edge(self, a: Box, b: Box, cls: str = "") -> None:
        """Arrow from a to b, leaving and entering box edges on the side facing the other box."""
        if b.x >= a.x + a.w:
            p, q = (a.x + a.w, a.cy), (b.x, b.cy)
        elif a.x >= b.x + b.w:
            p, q = (a.x, a.cy), (b.x + b.w, b.cy)
        elif b.y >= a.y + a.h:
            p, q = (a.cx, a.y + a.h), (b.cx, b.y)
        else:
            p, q = (a.cx, a.y), (b.cx, b.y + b.h)
        if p[0] != q[0] and p[1] != q[1] and abs(p[1] - q[1]) > 1:
            mx = (p[0] + q[0]) / 2
            d = f"M{p[0]:.0f},{p[1]:.0f} C{mx:.0f},{p[1]:.0f} {mx:.0f},{q[1]:.0f} {q[0]:.0f},{q[1]:.0f}"
        else:
            d = f"M{p[0]:.0f},{p[1]:.0f} L{q[0]:.0f},{q[1]:.0f}"
        c = f"edge {cls}".strip()
        self.parts.append(f'<path class="{c}" d="{d}"/>')

    def svg(self, pad: float = 16) -> str:
        h = self.bottom + pad
        return f'<svg viewBox="0 0 {self.width} {h:.0f}">' + "".join(self.parts) + "</svg>"

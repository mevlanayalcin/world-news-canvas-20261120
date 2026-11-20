"""Locator map for the v2 front page: Natural Earth 110m land, Miller projection.

The map is emitted as an inline SVG at its printed size (300 x 148), so pins
and numbers are vector-sharp on the page. Pins that would overlap are pushed
apart by a fixed, deterministic relaxation and tied back with a leader line.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

W, H = 300, 144
LON0, LON1 = -102.0, 162.0
LAT_TOP, LAT_BOT = 63.0, -45.0
PIN_R = 6.6
MIN_GAP = 14.2  # centre-to-centre distance between pins, px

REGION_COLORS = {
    "ASIA-PACIFIC": "#9A1B1F",
    "AMERICAS": "#1D6F6A",
    "EUROPE": "#1B3A6B",
    "MIDDLE EAST": "#A85F12",
    "AFRICA": "#2E7D50",
    "OCEANIA": "#5E3A7A",
    "GLOBAL/SCIENCE": "#4A5563",
}


def miller(lat: float) -> float:
    lat = max(-85.0, min(85.0, lat))
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


Y_TOP, Y_BOT = miller(LAT_TOP), miller(LAT_BOT)


def project(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (Y_TOP - miller(lat)) / (Y_TOP - Y_BOT) * H
    return x, y


def relax(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Push pin centres apart until every pair is MIN_GAP apart (deterministic)."""
    pos = [list(p) for p in points]
    lo_x, hi_x = PIN_R + 2, W - PIN_R - 2
    lo_y, hi_y = PIN_R + 2, H - PIN_R - 2
    for _ in range(600):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                dist = math.hypot(dx, dy)
                if dist < MIN_GAP:
                    if dist < 1e-6:
                        dx, dy, dist = 1.0, 0.0, 1.0
                    push = (MIN_GAP - dist) / 2 + 0.05
                    ux, uy = dx / dist, dy / dist
                    pos[i][0] -= ux * push
                    pos[i][1] -= uy * push
                    pos[j][0] += ux * push
                    pos[j][1] += uy * push
                    moved = True
        for p, (ox, oy) in zip(pos, points):
            # gentle pull home keeps pins near their places
            p[0] += (ox - p[0]) * 0.02
            p[1] += (oy - p[1]) * 0.02
            p[0] = min(hi_x, max(lo_x, p[0]))
            p[1] = min(hi_y, max(lo_y, p[1]))
        if not moved:
            break
    return [(round(x, 2), round(y, 2)) for x, y in pos]


def layout(pins):
    """pins: list of (n, lon, lat, region). Returns [(n, x0, y0, x, y, region)]."""
    true = [project(lon, lat) for _n, lon, lat, _r in pins]
    placed = relax(true)
    return [(n, tx, ty, px, py, r) for (n, _lo, _la, r), (tx, ty), (px, py) in zip(pins, true, placed)]


def land_path() -> str:
    land = json.load(open(ASSETS / "world.json"))
    parts = []
    for ring in land:
        pts = []
        for lon, lat in ring:
            x, y = project(lon, lat)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append("M" + " L".join(pts) + " Z")
    return " ".join(parts)


def svg(pins) -> str:
    placed = layout(pins)
    grid = []
    for lon in range(-90, 180, 30):
        x, _ = project(lon, 0)
        grid.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/>')
    for lat in (-30, 0, 30, 60):
        _, y = project(0, lat)
        grid.append(f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
    leaders, dots, marks = [], [], []
    for n, tx, ty, px, py, region in placed:
        col = REGION_COLORS[region]
        if math.hypot(px - tx, py - ty) > PIN_R * 0.6:
            leaders.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}"/>')
            dots.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="1.6" fill="{col}"/>')
        marks.append(
            f'<g class="pin" data-pin="{n}"><circle cx="{px:.1f}" cy="{py:.1f}" r="{PIN_R}" fill="{col}"/>'
            f'<text x="{px:.1f}" y="{py + 3.2:.1f}">{n}</text></g>'
        )
    return f'''<svg class="mapsvg" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#D9E8F1"/>
<g stroke="#C3D6E3" stroke-width="0.8">{''.join(grid)}</g>
<path d="{land_path()}" fill="#E9DFC6" stroke="#8E9A9E" stroke-width="0.6"/>
<g stroke="#141923" stroke-width="1">{''.join(leaders)}</g>
{''.join(dots)}
<g font-family="LatoX" font-weight="900" font-size="9.4" fill="#FFFFFF" text-anchor="middle" stroke="none">
<g stroke="#FFFFFF" stroke-width="1.3">{''.join(m.replace('<text', '<text stroke="none"') for m in marks)}</g>
</g>
</svg>'''


def check(pins):
    placed = layout(pins)
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            d = math.hypot(a[3] - b[3], a[4] - b[4])
            if d < 2 * PIN_R + 0.4:
                raise SystemExit(f"map pins {a[0]} and {b[0]} overlap ({d:.1f}px)")
        if not (PIN_R <= a[3] <= W - PIN_R and PIN_R <= a[4] <= H - PIN_R):
            raise SystemExit(f"map pin {a[0]} leaves the frame")
    return placed

"""Locator map for the v17 front page: Natural Earth 110m land, Miller projection.

High-contrast editorial cartography: light-blue ocean (#E6EFF5), warm sand land
(#D8CBB5) with subtle coastline stroke (#BFAF96). Emitted as inline SVG at its
printed size (294 x 150 px) so pins, leaders, and numerals stay vector-sharp.
Every story has a true-location dot verified to lie on Natural Earth land and a
numbered circle linked by a 2-6 px leader (dark ink over white halo).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

W = 294
LON0, LON1 = -128.0, 179.0
LAT_TOP, LAT_BOT = 75.0, -56.0
PIN_R = 8.2
RING = 0.7                 # half the 1.4 px white ring stroke, px
MIN_GAP = 2 * (PIN_R + RING) + 3.2   # >= 3.2 px clear map between outer white rings

REGION_COLORS = {
    "ASIA-PACIFIC": "#B8292F",
    "AMERICAS": "#167A73",
    "EUROPE": "#225396",
    "MIDDLE EAST": "#B56212",
    "AFRICA": "#267A4B",
    "OCEANIA": "#673D87",
    "GLOBAL": "#3B4D6B",
}


def miller(lat: float) -> float:
    lat = max(-85.0, min(85.0, lat))
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


Y_TOP, Y_BOT = miller(LAT_TOP), miller(LAT_BOT)
H = round(W * (Y_TOP - Y_BOT) / math.radians(LON1 - LON0))


def project(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (Y_TOP - miller(lat)) / (Y_TOP - Y_BOT) * H
    return x, y


LEADER_MIN, LEADER_MAX = 2.0, 6.0   # visible leader between dot and pin ring, px
DOT_R = 2.2
ANGLES = 24


def _rings_px():
    land = json.load(open(ASSETS / "world.json"))
    return land, [[project(lon, lat) for lon, lat in ring] for ring in land]


def on_land(lon: float, lat: float) -> bool:
    """Even-odd point-in-polygon test against the Natural Earth rings."""
    land, _ = _rings_px()
    inside = False
    for ring in land:
        for i in range(len(ring)):
            x1, y1 = ring[i]
            x2, y2 = ring[i - 1]
            if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside


def _land_mask(ss: int = 4):
    from PIL import Image, ImageDraw
    _, rings = _rings_px()
    im = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)
    for ring in rings:
        d.polygon([(x * ss, y * ss) for x, y in ring], fill=255)
    return im, ss


def land_fraction(cx: float, cy: float, r: float = PIN_R, _cache={}) -> float:
    if "m" not in _cache:
        im, ss = _land_mask()
        _cache["m"], _cache["ss"] = im.load(), ss
    px, ss = _cache["m"], _cache["ss"]
    hit = tot = 0
    for i in range(-8, 9):
        for j in range(-8, 9):
            x, y = cx + r * i / 8, cy + r * j / 8
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                continue
            tot += 1
            xi, yi = int(x * ss), int(y * ss)
            if 0 <= xi < W * ss and 0 <= yi < H * ss and px[xi, yi]:
                hit += 1
    return hit / tot


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def place(dots: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Choose a numbered-circle centre for every true-location dot."""
    lo_x, hi_x = PIN_R + 2, W - PIN_R - 2
    lo_y, hi_y = PIN_R + 2, H - PIN_R - 2
    ring_r = PIN_R + RING
    cands = []
    for k, (tx, ty) in enumerate(dots):
        opts = []
        for L in (LEADER_MIN, 4.0, LEADER_MAX):
            d = ring_r + DOT_R + L
            for a in range(ANGLES):
                th = -math.pi / 2 + 2 * math.pi * a / ANGLES
                cx, cy = tx + d * math.cos(th), ty + d * math.sin(th)
                if not (lo_x <= cx <= hi_x and lo_y <= cy <= hi_y):
                    continue
                if any(math.hypot(cx - ox, cy - oy) < ring_r + DOT_R + 1.0
                       for j, (ox, oy) in enumerate(dots)):
                    continue
                up = (1 - math.cos(th + math.pi / 2)) / 2
                cost = -2.0 * land_fraction(cx, cy) + 0.6 * up + 0.08 * L
                opts.append((round(cost, 6), a, L, cx, cy))
        opts.sort()
        cands.append(opts)
    crowd = [sum(1 for o in dots if 0 < math.hypot(o[0] - t[0], o[1] - t[1]) < 4 * MIN_GAP)
             for t in dots]
    order = sorted(range(len(dots)), key=lambda i: (-crowd[i], i))
    chosen: dict[int, tuple[float, float]] = {}

    def cross(a, b, c, d):
        def o(p, q, r):
            return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0

    def ok(i, cx, cy):
        tx, ty = dots[i]
        own = math.hypot(cx - tx, cy - ty)
        if any(j != i and math.hypot(cx - ox, cy - oy) <= own for j, (ox, oy) in enumerate(dots)):
            return False
        for j, (ox, oy) in chosen.items():
            if cross((tx, ty), (cx, cy), dots[j], (ox, oy)):
                return False
            if math.hypot(cx - ox, cy - oy) < MIN_GAP:
                return False
            jx, jy = dots[j]
            if _seg_dist(ox, oy, tx, ty, cx, cy) < ring_r + 1.0:
                return False
            if _seg_dist(cx, cy, jx, jy, ox, oy) < ring_r + 1.0:
                return False
        return True

    def dfs(k):
        if k == len(order):
            return True
        i = order[k]
        for _c, _a, _L, cx, cy in cands[i]:
            if ok(i, cx, cy):
                chosen[i] = (cx, cy)
                if dfs(k + 1):
                    return True
                del chosen[i]
        return False

    if not dfs(0):
        raise SystemExit("map: no overlap-free pin layout")
    return [(round(chosen[i][0], 2), round(chosen[i][1], 2)) for i in range(len(dots))]


def layout(pins):
    """pins: list of (n, lon, lat, region). Returns [(n, x0, y0, x, y, region)]."""
    true = [project(lon, lat) for _n, lon, lat, _r in pins]
    placed = place(true)
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
    for lat in (0,):
        _, y = project(0, lat)
        grid.append(f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
    leaders, dots, marks = [], [], []
    for n, tx, ty, px, py, region in placed:
        col = REGION_COLORS[region]
        d = math.hypot(px - tx, py - ty)
        ux, uy = (px - tx) / d, (py - ty) / d
        ex, ey = px - ux * (PIN_R + RING), py - uy * (PIN_R + RING)
        leaders.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
        dots.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{DOT_R}" fill="{col}" stroke="#FFFFFF" stroke-width="1"/>')
        marks.append(
            f'<g class="pin" data-pin="{n}" data-x0="{tx:.2f}" data-y0="{ty:.2f}">'
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{PIN_R}" fill="{col}"/>'
            f'<text x="{px:.1f}" y="{py + 3.5:.1f}">{n}</text></g>'
        )
    return f'''<svg class="mapsvg" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#E6EFF5"/>
<g stroke="#C7D8E4" stroke-width="0.8">{''.join(grid)}</g>
<path d="{land_path()}" fill="#D8CBB5" stroke="#BFAF96" stroke-width="0.6" stroke-linejoin="round"/>
<g stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round">{''.join(leaders)}</g>
<g stroke="#1E293B" stroke-width="1.3" stroke-linecap="round">{''.join(leaders)}</g>
{''.join(dots)}
<g font-family="LatoX" font-weight="900" font-size="10" fill="#FFFFFF" text-anchor="middle" stroke="none">
<g stroke="#FFFFFF" stroke-width="1.4">{''.join(m.replace('<text', '<text stroke="none"') for m in marks)}</g>
</g>
</svg>'''


def check(pins):
    placed = layout(pins)
    ring_r = PIN_R + RING
    for (n, lon, lat, _r) in pins:
        if not on_land(lon, lat):
            raise SystemExit(f"map pin {n} location ({lon}, {lat}) is not on Natural Earth land")
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            d = math.hypot(a[3] - b[3], a[4] - b[4])
            gap = d - 2 * ring_r
            if gap < 3.0:
                raise SystemExit(f"map pins {a[0]} and {b[0]} have only {gap:.1f}px between rings")
        if not (PIN_R <= a[3] <= W - PIN_R and PIN_R <= a[4] <= H - PIN_R):
            raise SystemExit(f"map pin {a[0]} leaves the frame")
        leader = math.hypot(a[3] - a[1], a[4] - a[2]) - ring_r - DOT_R
        if not LEADER_MIN - 0.01 <= leader <= LEADER_MAX + 0.01:
            raise SystemExit(f"map pin {a[0]} leader {leader:.1f}px outside {LEADER_MIN}-{LEADER_MAX}px")
        for b in placed:
            if math.hypot(a[3] - b[1], a[4] - b[2]) < ring_r + DOT_R + 1.0 - 0.01:
                raise SystemExit(f"map pin {a[0]} covers the location dot of pin {b[0]}")
    return placed

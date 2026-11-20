"""Locator map: Miller projection, Natural Earth 110m land, drawn as SVG."""
from __future__ import annotations

import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

W, H = 600, 320
PAD_L, PAD_R, PAD_T, PAD_B = 8, 8, 20, 12
LAT_TOP, LAT_BOT = 80.0, -58.0


def miller(lat: float) -> float:
    lat = max(-85.0, min(85.0, lat))
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


Y_TOP = miller(LAT_TOP)
Y_BOT = miller(LAT_BOT)


def project(lon: float, lat: float) -> tuple[float, float]:
    x = PAD_L + (lon + 180.0) / 360.0 * (W - PAD_L - PAD_R)
    y = PAD_T + (Y_TOP - miller(lat)) / (Y_TOP - Y_BOT) * (H - PAD_T - PAD_B)
    return x, y


REGION_COLORS = {
    "ASIA-PACIFIC": "#9A1B1F",
    "AMERICAS": "#1D6F6A",
    "EUROPE": "#1B3A6B",
    "MIDDLE EAST": "#B06A1F",
    "AFRICA": "#2E7D50",
    "OCEANIA": "#5E3A7A",
    "GLOBAL/SCIENCE": "#4A5A6A",
}

# n, name, lon, lat, label dx, label dy, region
PINS = [
    (1, "Gopalpur", 84.9, 19.3, 0, 0, "ASIA-PACIFIC"),
    (2, "Brussels", 4.35, 50.85, -20, -34, "EUROPE"),
    (3, "Antalya", 30.70, 36.90, 22, 18, "GLOBAL/SCIENCE"),
    (4, "Washington", -77.04, 38.90, -26, 22, "AMERICAS"),
    (5, "Cox's Bazar", 92.00, 21.40, 26, -18, "ASIA-PACIFIC"),
    (6, "Berlin", 13.40, 52.50, 28, 2, "EUROPE"),
    (7, "New York", -74.00, 40.70, 22, -24, "GLOBAL/SCIENCE"),
    (8, "Doha", 51.50, 25.30, 18, 24, "MIDDLE EAST"),
    (9, "Melbourne", 145.00, -37.80, -24, 20, "OCEANIA"),
    (10, "Wellington", 174.80, -41.30, -24, 20, "OCEANIA"),
    (11, "Hormuz", 56.30, 26.60, 34, -8, "MIDDLE EAST"),
    (12, "Kyiv", 30.50, 50.45, -30, -26, "EUROPE"),
    (13, "Shenzhen", 114.10, 22.50, 26, -22, "ASIA-PACIFIC"),
]


def build_svg() -> str:
    land = json.load(open(ASSETS / "world.json"))
    paths = []
    for ring in land:
        pts = []
        for lon, lat in ring:
            x, y = project(lon, lat)
            pts.append(f"{x:.1f},{y:.1f}")
        paths.append("M" + " L".join(pts) + " Z")
    land_d = " ".join(paths)

    graticule = []
    for lon in range(-150, 180, 30):
        x, y1 = project(lon, LAT_TOP)
        _, y2 = project(lon, LAT_BOT)
        graticule.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}"/>')
    for lat in (-30, 0, 30, 60):
        x1, y = project(-180, lat)
        x2, _ = project(180, lat)
        graticule.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}"/>')

    pin_svg = []
    for n, name, lon, lat, dx, dy, region in PINS:
        x, y = project(lon, lat)
        px, py = x + dx, y + dy
        col = REGION_COLORS[region]
        pin_svg.append(
            f'<line class="leader" x1="{x:.1f}" y1="{y:.1f}" x2="{px:.1f}" y2="{py:.1f}"/>'
            f'<circle class="pin" cx="{px:.1f}" cy="{py:.1f}" r="10" fill="{col}"/>'
            f'<text class="pnum" x="{px:.1f}" y="{py + 3.4:.1f}">{n}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <clipPath id="mapclip"><rect x="{PAD_L}" y="{PAD_T}" width="{W-PAD_L-PAD_R}" height="{H-PAD_T-PAD_B}" rx="3"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" fill="#DCE9F2"/>
  <g clip-path="url(#mapclip)">
    <rect x="{PAD_L}" y="{PAD_T}" width="{W-PAD_L-PAD_R}" height="{H-PAD_T-PAD_B}" fill="#DCE9F2"/>
    <g class="grid">{''.join(graticule)}</g>
    <path class="land" d="{land_d}"/>
  </g>
  <rect x="{PAD_L}" y="{PAD_T}" width="{W-PAD_L-PAD_R}" height="{H-PAD_T-PAD_B}" fill="none" stroke="#141923" stroke-width="2" rx="3"/>
  <g class="pins">{''.join(pin_svg)}</g>
</svg>'''
    return svg


STYLE = """
.grid line { stroke:#C6D7E2; stroke-width:1; }
.land { fill:#E6DCC5; stroke:#9AA6A8; stroke-width:0.8; }
.leader { stroke:#141923; stroke-width:1.3; }
.pin { stroke:#FFFDF7; stroke-width:1.6; }
.pnum { fill:#FFFDF7; font-family:Lato; font-weight:900; font-size:10.5px; text-anchor:middle; }
"""


def svg_document() -> str:
    svg = build_svg()
    return svg.replace("<defs>", f"<style>{STYLE}</style>\n  <defs>")


def check_pins():
    for n, name, lon, lat, dx, dy, region in PINS:
        x, y = project(lon, lat)
        px, py = x + dx, y + dy
        if not (PAD_L + 12 <= px <= W - PAD_R - 12 and PAD_T + 12 <= py <= H - PAD_B - 12):
            raise SystemExit(f"pin {n} {name} at {px:.1f},{py:.1f} is too close to the map edge")


if __name__ == "__main__":
    check_pins()
    (ASSETS / "map.svg").write_text(svg_document())
    print("wrote", ASSETS / "map.svg", len(svg_document()))

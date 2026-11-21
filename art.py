"""Editorial illustrations for the Friday 20 November 2026 front page (v17).

Each picture has two layers:
- a clean flat/2-tone vector scene drawn from scratch with Pillow at 2x
  resolution and reduced with Lanczos for razor-sharp supersampled edges;
- a printed-size 1x typographic layer rendered directly by FreeType so every
  figure and callout reads sharply even in a 300x300 thumbnail.

v17 eliminates the 13 repetitive crimson corner stickers and noisy gradients:
- Leads 1-3 (316x138): high-contrast single-punchline editorial infographics.
- Cards 4-13 (188x80): clean light-tinted Economist-style infographic panels
  carrying one bold visual subject and one crisp 300px-readable callout.
- Zero source pills inside pictures (sources live in every caption below).
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

# ---- palette ---------------------------------------------------------------
INK = (18, 24, 34)          # #121822
NAVY = (22, 36, 58)         # #16243A
CRIMSON = (184, 41, 47)     # #B8292F
CORAL = (248, 113, 113)     # #F87171
RED = (239, 68, 68)         # #EF4444
ORANGE = (255, 107, 26)     # #FF6B1A
GOLD = (244, 196, 48)       # #F4C430
YELLOW = (255, 209, 102)    # #FFD166
TEAL = (13, 110, 104)       # #0D6E68
GREEN = (45, 138, 104)      # #2D8A68
NV_GREEN = (118, 185, 0)    # #76B900
WHITE = (255, 255, 255)
MUTED = (100, 112, 128)

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"
LATO_HEAVY = FONT_DIR / "lato" / "Lato-Heavy.ttf"

HERO = (316, 138)
GRID = (188, 80)

LABELS: list[dict] = []


def font(path: Path, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), round(size))


class Art:
    """2x supersampled canvas addressed directly in 1x pixel coordinates."""

    def __init__(self, name: str, size: tuple[int, int], bg: tuple[int, int, int]):
        self.name = name
        self.size = size
        self.lead = size[0] > 200
        self.w, self.h = size
        self.im = Image.new("RGB", (self.w * 2, self.h * 2), bg)
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * 2, y * 2) for x, y in pts]

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        self.d.rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], fill=fill, outline=outline,
                         width=max(1, round(width * 2)) if outline else 0)

    def rrect(self, x0, y0, x1, y1, r=3.0, fill=None, outline=None, width=1.0):
        self.d.rounded_rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], radius=r * 2,
                                 fill=fill, outline=outline,
                                 width=max(1, round(width * 2)) if outline else 0)

    def poly(self, pts, fill=None, outline=None, width=1.0):
        self.d.polygon(self._p(pts), fill=fill, outline=outline,
                       width=max(1, round(width * 2)) if outline else 0)

    def line(self, pts, fill=INK, width=1.5):
        self.d.line(self._p(pts), fill=fill, width=max(1, round(width * 2)), joint="curve")

    def circle(self, cx, cy, r, fill=None, outline=None, width=1.0):
        self.d.ellipse([(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2],
                       fill=fill, outline=outline,
                       width=max(1, round(width * 2)) if outline else 0)

    def arc(self, cx, cy, r, start, end, fill=INK, width=1.5):
        self.d.arc([(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2],
                   start, end, fill=fill, width=max(1, round(width * 2)))

    def pieslice(self, cx, cy, r, start, end, fill=INK, outline=None, width=1.0):
        self.d.pieslice([(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2],
                        start, end, fill=fill, outline=outline,
                        width=max(1, round(width * 2)) if outline else 0)

    def star(self, cx, cy, r, fill=GOLD, points=5, rot=-math.pi / 2, inner=0.42):
        pts = []
        for i in range(points * 2):
            q = r if i % 2 == 0 else r * inner
            a = rot + i * math.pi / points
            pts.append((cx + q * math.cos(a), cy + q * math.sin(a)))
        self.poly(pts, fill=fill)

    def dashed_line(self, x0, y0, x1, y1, fill, width=1.5, dash=5.0, gap=3.5):
        dist = math.hypot(x1 - x0, y1 - y0)
        if dist <= 0:
            return
        ux, uy = (x1 - x0) / dist, (y1 - y0) / dist
        t = 0.0
        while t < dist:
            t2 = min(dist, t + dash)
            self.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * t2, y0 + uy * t2)], fill=fill, width=width)
            t += dash + gap

    def finish(self, overlay):
        out = self.im.resize(self.size, Image.LANCZOS)
        d = ImageDraw.Draw(out)
        if overlay:
            overlay(self, d)
        ASSETS.mkdir(exist_ok=True)
        out.save(ASSETS / self.name, format="PNG", optimize=True)

    # ---- printed-size 1x text helpers -------------------------------------
    def pill(self, d: ImageDraw.ImageDraw, text: str, x: float, y: float, size: float,
             fg, bg, path=LATO_BLACK, anchor="tl", kind="callout",
             px=None, py=None, radius=3, outline=None):
        f = font(path, size)
        bb = d.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        px = round(size * 0.45) if px is None else px
        py = round(size * 0.25) if py is None else py
        bw, bh = tw + 2 * px, th + 2 * py
        if anchor == "tl":
            x0, y0 = x, y
        elif anchor == "tr":
            x0, y0 = x - bw, y
        elif anchor == "tc":
            x0, y0 = x - bw / 2, y
        elif anchor == "bl":
            x0, y0 = x, y - bh
        elif anchor == "br":
            x0, y0 = x - bw, y - bh
        elif anchor == "bc":
            x0, y0 = x - bw / 2, y - bh
        elif anchor == "mm":
            x0, y0 = x - bw / 2, y - bh / 2
        else:
            raise ValueError(f"bad anchor {anchor}")
        if bg is not None or outline is not None:
            d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=radius,
                                fill=bg, outline=outline, width=1)
        d.text((x0 + px - bb[0], y0 + py - bb[1]), text, font=f, fill=fg)
        bbox = (round(x0, 1), round(y0, 1), round(x0 + bw, 1), round(y0 + bh, 1))
        LABELS.append(dict(art=self.name, kind=kind, text=text, bbox=bbox,
                           size=round(size), img=self.size, lead=self.lead))
        return bbox

    def label(self, d: ImageDraw.ImageDraw, text: str, x: float, y: float, size: float,
              fg, path=LATO_BLACK, anchor="tl", kind="label"):
        return self.pill(d, text, x, y, size, fg, None, path=path, anchor=anchor,
                         kind=kind, px=0, py=0)


# ---- shared vector props ---------------------------------------------------
def draw_union_jack(a: Art, x0, y0, x1, y1):
    # Draw cleanly on a clipped 2x tile so diagonals never bleed outside the flag frame
    w2 = max(2, round((x1 - x0) * 2))
    h2 = max(2, round((y1 - y0) * 2))
    tile = Image.new("RGB", (w2, h2), (1, 33, 105))
    td = ImageDraw.Draw(tile)
    td.line([(0, 0), (w2, h2)], fill=WHITE, width=9)
    td.line([(w2, 0), (0, h2)], fill=WHITE, width=9)
    td.line([(0, 0), (w2, h2)], fill=(200, 16, 46), width=4)
    td.line([(w2, 0), (0, h2)], fill=(200, 16, 46), width=4)
    cx, cy = w2 / 2, h2 / 2
    hw, hh = w2 * 0.11, h2 * 0.17
    td.rectangle([cx - hw, 0, cx + hw, h2], fill=WHITE)
    td.rectangle([0, cy - hh, w2, cy + hh], fill=WHITE)
    td.rectangle([cx - hw * 0.56, 0, cx + hw * 0.56, h2], fill=(200, 16, 46))
    td.rectangle([0, cy - hh * 0.56, w2, cy + hh * 0.56], fill=(200, 16, 46))
    a.im.paste(tile, (round(x0 * 2), round(y0 * 2)))
    a.rect(x0, y0, x1, y1, fill=None, outline=INK, width=1.0)


def draw_eu_flag(a: Art, x0, y0, x1, y1):
    a.rect(x0, y0, x1, y1, fill=(0, 51, 153), outline=INK, width=1.0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(x1 - x0, y1 - y0) * 0.31
    for i in range(12):
        t = -math.pi / 2 + i * math.pi / 6
        a.star(cx + r * math.cos(t), cy + r * math.sin(t), 2.3, (255, 204, 0))


def arc_pts(cx, cy, r, a0_deg, a1_deg, n=36):
    out = []
    for i in range(n + 1):
        t = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        out.append((cx + r * math.cos(t), cy - r * math.sin(t)))
    return out


# ---- 1. Kyiv bridges (Lead 1: 316 x 138) ----------------------------------
def art_kyiv():
    a = Art("art_01.png", HERO, (14, 26, 44))
    # Subtle two-tone night sky band near horizon
    a.rect(0, 44, 316, 78, fill=(22, 40, 68))
    # Kyiv skyline silhouette + Lavra golden dome on right bank
    a.poly([(0, 78), (0, 62), (16, 62), (20, 54), (34, 54), (38, 60), (52, 60),
            (58, 50), (74, 50), (78, 59), (104, 59), (112, 66), (138, 66), (138, 78)],
           fill=(28, 43, 66))
    a.poly([(190, 78), (196, 62), (222, 62), (228, 56), (254, 56), (260, 62),
            (286, 58), (294, 52), (316, 52), (316, 78)], fill=(30, 46, 70))
    # Golden Lavra dome & bell tower accent (clear of missile tracks)
    a.rect(281, 41, 293, 62, fill=(44, 62, 92))
    a.circle(287, 40, 6.2, fill=GOLD)
    a.line([(287, 33), (287, 26)], GOLD, 1.3)
    # Dnipro river
    a.rect(0, 76, 316, 138, fill=(22, 43, 71))
    for rx, ry, rw in ((18, 92, 34), (222, 88, 40), (36, 114, 48), (224, 124, 52), (122, 131, 42)):
        a.line([(rx, ry), (rx + rw, ry)], (46, 82, 122), 1.3)
    # Warm fire reflections on water beneath impacts
    a.line([(96, 89), (112, 89)], (178, 96, 44), 1.4)
    a.line([(178, 108), (198, 108)], (196, 104, 42), 1.6)
    a.line([(132, 131), (156, 131)], (214, 112, 40), 1.8)

    # Bridge 1 (far back, y=79): white arch bridge
    a.rect(0, 78, 316, 82, fill=(208, 218, 232))
    for px in (42, 96, 150, 204, 258):
        a.arc(px + 27, 86, 20, 180, 360, (160, 178, 202), 1.2)
        a.rect(px - 2, 82, px + 2, 91, fill=(104, 122, 146))

    # Bridge 2 (mid, y=96): white girder bridge
    a.rect(0, 95, 316, 100, fill=(224, 232, 242))
    for px in (34, 98, 162, 226, 286):
        a.rect(px - 2.5, 100, px + 2.5, 113, fill=(92, 110, 134))

    # Bridge 3 (foreground, y=116): iconic cable-stayed Dnipro bridge with white pylon
    a.line([(72, 116), (72, 74)], (240, 244, 250), 2.8)
    for sx in (24, 44, 104, 128):
        a.line([(72, 77), (sx, 116)], (188, 202, 220), 1.0)
    a.rect(0, 115, 316, 122, fill=(240, 244, 248))
    for px in (28, 72, 136, 206, 274):
        a.rect(px - 3, 122, px + 3, 138, fill=(80, 98, 122))

    # Sleek incoming missile trails (top-left & top-right -> impacts)
    a.line([(20, 32), (62, 54), (104, 79)], (255, 228, 168), 1.6)
    a.line([(296, 32), (242, 62), (188, 97)], (255, 228, 168), 1.8)
    a.line([(256, 30), (194, 70), (144, 116)], (255, 228, 168), 2.1)

    # 3 vivid fiery starburst impacts on the 3 bridge spans
    def starburst(bx, by, r_outer, r_mid, r_core):
        pts = []
        for i in range(16):
            r = r_outer if i % 2 == 0 else r_outer * 0.46
            ang = i * math.pi / 8
            pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
        a.poly(pts, fill=ORANGE)
        a.circle(bx, by, r_mid, fill=YELLOW)
        a.circle(bx, by, r_core, fill=WHITE)

    starburst(104, 80, 12.5, 5.5, 2.5)
    starburst(188, 97, 15.0, 6.8, 3.0)
    starburst(144, 117, 18.5, 8.2, 3.6)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.pill(d, "111 MISSILES · 404 DRONES · 3 BRIDGES HIT",
                     158, 5, 11.5, INK, GOLD, path=LATO_BLACK, anchor="tc",
                     kind="callout", px=8, py=4, radius=3)

    a.finish(overlay)


# ---- 2. Cyclone Akvan (Lead 2: 316 x 138) ---------------------------------
def art_akvan():
    a = Art("art_02.png", HERO, (39, 114, 148))
    # Coastal shallow teal band
    a.poly([(0, 0), (168, 0), (142, 46), (118, 96), (94, 138), (0, 138)], fill=(52, 136, 170))
    # Odisha land (warm sand #DFD3B8) with clean coastline contour
    coast = [(146, 0), (138, 22), (124, 48), (114, 70), (100, 96), (82, 122), (72, 138)]
    a.poly([(0, 0)] + coast + [(0, 138)], fill=(223, 211, 184))
    # Subtle inland eastern ghats green plateau tint on far left
    a.poly([(0, 52), (56, 62), (44, 98), (22, 138), (0, 138)], fill=(203, 211, 176))
    a.line(coast, fill=(166, 150, 120), width=1.6)

    # Bold white concentric cyclone spiral over Bay of Bengal (clean clearance from top pills & bottom label)
    cx, cy = 212, 83
    for r, w, col, s, e in (
        (35, 4.0, WHITE, 22, 290),
        (27, 3.3, (214, 238, 247), 185, 430),
        (19, 3.4, WHITE, 15, 295),
        (12, 2.8, (214, 238, 247), 160, 415),
    ):
        a.arc(cx, cy, r, s, e, fill=col, width=w)
    a.circle(cx, cy, 5.2, fill=(32, 96, 126), outline=WHITE, width=1.8)

    # Crimson dashed landfall path to Gopalpur coast (114, 70)
    a.dashed_line(260, 108, 222, 89, (220, 44, 44), width=2.2, dash=5, gap=3)
    a.dashed_line(201, 80, 126, 70, (220, 44, 44), width=2.4, dash=5, gap=3)
    # Arrowhead into Gopalpur
    a.poly([(119, 69), (131, 63), (129, 76)], fill=(220, 44, 44))
    # Crisp Gopalpur coastal dot
    a.circle(114, 70, 4.8, fill=CRIMSON, outline=WHITE, width=1.6)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "ODISHA", 12, 14, 14, INK, path=LATO_BLACK, anchor="tl", kind="geo")
        art_obj.label(d, "INDIA", 12, 32, 10, (74, 85, 104), path=LATO_BOLD, anchor="tl", kind="geo")
        art_obj.pill(d, "GOPALPUR", 16, 61, 10, WHITE, NAVY, path=LATO_BLACK,
                     anchor="tl", kind="geo", px=5, py=3, radius=2)
        d.line([(84, 70), (107, 70)], fill=NAVY, width=1)
        art_obj.pill(d, "LANDFALL ~02:30Z", 310, 6, 10.5, WHITE, NAVY, path=LATO_BLACK,
                     anchor="tr", kind="callout", px=6, py=3, radius=2)
        art_obj.pill(d, "372,000 EVACUATED", 310, 26, 10.5, WHITE, CRIMSON, path=LATO_BLACK,
                     anchor="tr", kind="callout", px=6, py=3, radius=2)
        art_obj.label(d, "BAY OF BENGAL", 308, 132, 9.5, (216, 240, 248),
                      path=LATO_BLACK, anchor="br", kind="geo")

    a.finish(overlay)


# ---- 3. Global AI Rout (Lead 3: 316 x 138) --------------------------------
SCOREBOARD = [("S&P 500", "−3.7%"), ("NASDAQ", "−5.3%"), ("TAIEX", "−6.2%"), ("NVIDIA", "−14.0%")]


def art_chips():
    a = Art("art_03.png", HERO, (14, 22, 36))
    # Subtle chart grid on left half
    gx0, gx1 = 10, 174
    for gy in (44, 66, 88, 110, 128):
        a.line([(gx0, gy), (gx1, gy)], (30, 44, 66), 1.0)
    # Stepped market plunge line + rich dark crimson fill underneath
    curve = [
        (10, 40), (26, 38), (38, 49), (52, 46), (66, 64), (80, 60),
        (96, 82), (110, 77), (126, 98), (140, 94), (156, 116), (170, 125)
    ]
    a.poly(curve + [(170, 131), (10, 131)], fill=(54, 22, 32))
    a.line(curve, RED, 2.8)
    a.circle(170, 125, 3.8, fill=CORAL, outline=WHITE, width=1.2)
    # Right-side scoreboard container
    a.rrect(182, 31, 310, 132, r=3, fill=(22, 34, 54), outline=(44, 64, 96), width=1.0)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        # Full-width top crimson banner ribbon
        art_obj.pill(d, "WORST WEEK FOR WORLD STOCKS SINCE 2020",
                     158, 5, 11, WHITE, CRIMSON, path=LATO_BLACK, anchor="tc",
                     kind="callout", px=8, py=4, radius=2)
        # 4-row tabular scoreboard
        x0, y0, x1, y1 = 182, 31, 310, 132
        f_lbl = font(LATO_BOLD, 12.5)
        f_val = font(LATO_BLACK, 12.5)
        row_h = (y1 - y0 - 4) / len(SCOREBOARD)
        for i, (name, pct) in enumerate(SCOREBOARD):
            cy = y0 + 2 + row_h * (i + 0.5)
            d.text((x0 + 7, cy), name, font=f_lbl, fill=WHITE, anchor="lm")
            d.text((x1 - 7, cy), pct, font=f_val, fill=CORAL, anchor="rm")
            if i:
                yy = round(y0 + 2 + row_h * i)
                d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(40, 56, 84), width=1)
        LABELS.append(dict(art=art_obj.name, kind="board", text="scoreboard",
                           bbox=(x0, y0, x1, y1), size=12, img=art_obj.size, lead=True))

    a.finish(overlay)


# ---- 4. Nvidia SEC Probe (Card 4: 188 x 80) -------------------------------
def art_nvidia():
    a = Art("art_04.png", GRID, (19, 27, 43))
    # Glowing-green GPU chip with pins on left
    cx0, cy0, cx1, cy1 = 14, 20, 52, 58
    for k in range(4):
        py = cy0 + 6 + k * 9
        a.line([(cx0 - 6, py), (cx0, py)], (176, 188, 204), 1.6)
        a.line([(cx1, py), (cx1 + 6, py)], (176, 188, 204), 1.6)
        px = cx0 + 6 + k * 9
        a.line([(px, cy0 - 6), (px, cy0)], (176, 188, 204), 1.6)
        a.line([(px, cy1), (px, cy1 + 6)], (176, 188, 204), 1.6)
    a.rrect(cx0, cy0, cx1, cy1, r=3, fill=(38, 49, 68), outline=(176, 188, 204), width=1.2)
    a.rrect(cx0 + 7, cy0 + 7, cx1 - 7, cy1 - 7, r=2, fill=NV_GREEN)
    # Sharp red zig-zag crash arrow in center
    pts = [(66, 20), (77, 34), (72, 38), (85, 55)]
    a.line(pts, RED, 2.8)
    a.poly([(89, 61), (78, 56), (88, 49)], fill=RED)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "−14%", 140, 17, 23, CORAL, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "SEC PROBE", 140, 48, 11.5, WHITE, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 5. UK-EU Reset (Card 5: 188 x 80) ------------------------------------
def art_euuk():
    a = Art("art_05.png", GRID, (234, 241, 248))
    # Union Jack on left, double arrow center, EU flag on right
    draw_union_jack(a, 14, 12, 68, 46)
    draw_eu_flag(a, 120, 12, 174, 46)
    # Crisp dark double-headed arrow
    a.line([(80, 29), (108, 29)], NAVY, 2.6)
    a.poly([(73, 29), (83, 22), (83, 36)], fill=NAVY)
    a.poly([(115, 29), (105, 22), (105, 36)], fill=NAVY)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "FOOD · CARBON · 100K VISAS", 94, 57, 10.5, NAVY,
                      path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 6. COP31 Climate (Card 6: 188 x 80) ----------------------------------
def art_cop31():
    a = Art("art_06.png", GRID, (234, 244, 245))
    # Clean teal-and-green Earth globe on left
    a.circle(26, 40, 17.5, fill=(78, 168, 186), outline=NAVY, width=1.3)
    a.poly([(16, 29), (26, 27), (31, 35), (23, 40), (15, 36)], fill=GREEN)
    a.poly([(24, 42), (35, 41), (34, 52), (26, 53)], fill=GREEN)
    a.circle(26, 40, 17.5, fill=None, outline=NAVY, width=1.3)
    # Minimalist overtime clock dial on right
    cx, cy, r = 162, 40, 16.5
    a.circle(cx, cy, r, fill=WHITE, outline=NAVY, width=1.5)
    # Overtime crimson wedge from 12 to 3 o'clock
    a.pieslice(cx, cy, r - 2, 270, 360, fill=(248, 210, 210))
    a.arc(cx, cy, r - 1, 270, 360, fill=CRIMSON, width=2.2)
    a.line([(cx, cy), (cx, cy - 10)], NAVY, 2.0)
    a.line([(cx, cy), (cx + 9.5, cy)], CRIMSON, 2.0)
    a.circle(cx, cy, 2.0, fill=NAVY)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "NO DEAL", 94, 22, 16.5, INK, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "OVERTIME", 94, 45, 10.5, CRIMSON, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 7. Poland Cruise Missile (Card 7: 188 x 80) --------------------------
def art_poland():
    a = Art("art_07.png", GRID, (243, 239, 228))
    # Slightly darker tint on right (Ukraine side)
    a.rect(120, 0, 188, 80, fill=(234, 227, 212))
    # Red-dashed vertical border line
    a.dashed_line(120, 5, 120, 75, CRIMSON, width=1.8, dash=5, gap=3.5)
    # Ground + pine trees neatly on Polish far-left
    a.rect(0, 68, 188, 80, fill=(214, 218, 194))
    for tx in (16, 30, 44, 58):
        a.poly([(tx, 52), (tx - 5.5, 68), (tx + 5.5, 68)], fill=(46, 94, 62))
        a.rect(tx - 1, 68, tx + 1, 72, fill=(92, 66, 46))
    # Flight path trail from Ukraine across border into Poland
    a.line([(182, 38), (118, 44)], (204, 72, 72), 1.8)
    # Sleek grey KH-101 cruise missile silhouette heading left
    a.poly([(64, 45), (75, 41), (116, 41), (116, 47), (75, 47)], fill=(64, 74, 88), outline=INK, width=0.8)
    a.poly([(58, 44), (65, 41), (65, 47)], fill=CRIMSON)
    a.poly([(86, 41), (95, 32), (100, 41)], fill=(64, 74, 88))
    a.poly([(109, 41), (116, 35), (116, 41)], fill=(64, 74, 88))

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "POLAND", 10, 6, 11, NAVY, path=LATO_BLACK, anchor="tl", kind="geo")
        art_obj.label(d, "UKRAINE", 180, 6, 10, MUTED, path=LATO_BOLD, anchor="tr", kind="geo")
        art_obj.label(d, "KH-101", 89, 53, 11.5, CRIMSON, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 8. Hormuz Tanker (Card 8: 188 x 80) ----------------------------------
def art_hormuz():
    a = Art("art_08.png", GRID, (220, 234, 242))
    # Far Oman/Musandam dry ridge on right
    a.poly([(118, 48), (138, 34), (156, 40), (172, 30), (188, 36), (188, 48)], fill=(201, 176, 147))
    # Slate sea
    a.rect(0, 48, 188, 80, fill=(53, 107, 130))
    for rx, ry, rw in ((14, 68, 34), (116, 70, 46), (62, 74, 30)):
        a.line([(rx, ry), (rx + rw, ry)], (94, 148, 168), 1.2)
    # Smoke plumes rising right
    for sx, sy, sr, col in ((110, 30, 8, (94, 104, 114)), (122, 23, 9, (118, 128, 138)),
                            (136, 19, 7.5, (142, 152, 162))):
        a.circle(sx, sy, sr, fill=col)
    # Vivid orange-gold flame on deck
    a.poly([(86, 46), (92, 30), (98, 38), (104, 24), (110, 38), (116, 32), (120, 46)], fill=ORANGE)
    a.poly([(93, 46), (98, 36), (104, 32), (109, 38), (113, 46)], fill=YELLOW)
    # Tanker hull silhouette
    a.poly([(24, 46), (146, 46), (138, 62), (30, 62)], fill=(156, 38, 38), outline=INK, width=1.0)
    a.rect(28, 55, 140, 62, fill=(32, 38, 48))
    # Stern bridge superstructure
    a.rect(30, 32, 50, 46, fill=WHITE, outline=INK, width=1.0)
    a.rect(34, 35, 46, 39, fill=NAVY)
    a.rect(40, 25, 46, 32, fill=(44, 52, 64))

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "STRAIT OF HORMUZ", 8, 6, 10.5, NAVY, path=LATO_BLACK, anchor="tl", kind="geo")

    a.finish(overlay)


# ---- 9. India-Pakistan SCO (Card 9: 188 x 80) -----------------------------
def art_indiapak():
    a = Art("art_09.png", GRID, (239, 243, 247))
    # Pakistan flag (left)
    px0, py0, px1, py1 = 12, 12, 64, 44
    a.rect(px0, py0, px0 + 13, py1, fill=WHITE)
    a.rect(px0 + 13, py0, px1, py1, fill=(1, 102, 56))
    a.circle(px0 + 33, (py0 + py1) / 2, 7.5, fill=WHITE)
    a.circle(px0 + 35.5, (py0 + py1) / 2 - 1.2, 6.2, fill=(1, 102, 56))
    a.star(px0 + 39.5, (py0 + py1) / 2 - 2.6, 2.8, fill=WHITE)
    a.rect(px0, py0, px1, py1, fill=None, outline=INK, width=0.9)

    # India flag (right)
    ix0, iy0, ix1, iy1 = 124, 12, 176, 44
    sh = (iy1 - iy0) / 3
    a.rect(ix0, iy0, ix1, iy0 + sh, fill=(255, 153, 51))
    a.rect(ix0, iy0 + sh, ix1, iy0 + 2 * sh, fill=WHITE)
    a.rect(ix0, iy0 + 2 * sh, ix1, iy1, fill=(19, 136, 8))
    a.circle((ix0 + ix1) / 2, (iy0 + iy1) / 2, 3.8, fill=None, outline=(6, 3, 141), width=1.1)
    a.circle((ix0 + ix1) / 2, (iy0 + iy1) / 2, 1.2, fill=(6, 3, 141))
    a.rect(ix0, iy0, ix1, iy1, fill=None, outline=INK, width=0.9)

    # Clean dashed diplomatic line between flags
    a.dashed_line(69, 28, 119, 28, NAVY, width=2.0, dash=4.5, gap=3.5)
    a.circle(69, 28, 2.5, fill=CRIMSON)
    a.circle(119, 28, 2.5, fill=CRIMSON)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "SCO FORUM", 94, 49, 12, NAVY, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "NEW DELHI", 94, 64, 10, CRIMSON, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 10. Kenya First Oil Well (Card 10: 188 x 80) -------------------------
def art_kenya():
    a = Art("art_10.png", GRID, (245, 234, 213))
    # Subtle warm earth base cleanly below text
    a.rect(0, 66, 188, 80, fill=(224, 200, 158))
    # Steel lattice oil derrick on left
    bl, br, top = 18, 50, 9
    cl, cr = 31, 37
    a.line([(bl, 66), (cl, top)], INK, 2.0)
    a.line([(br, 66), (cr, top)], INK, 2.0)
    a.line([(cl - 2, top), (cr + 2, top)], INK, 2.0)
    steps = 5
    for k in range(steps):
        t0, t1 = k / steps, (k + 1) / steps
        y0 = 66 - (66 - top) * t0
        y1 = 66 - (66 - top) * t1
        xl0, xr0 = bl + (cl - bl) * t0, br + (cr - br) * t0
        xl1, xr1 = bl + (cl - bl) * t1, br + (cr - br) * t1
        a.line([(xl0, y0), (xr0, y0)], INK, 1.1)
        a.line([(xl0, y0), (xr1, y1)], INK, 0.9)
        a.line([(xr0, y0), (xl1, y1)], INK, 0.9)
    a.rect(12, 64, 56, 70, fill=(56, 62, 72), outline=INK, width=0.9)

    # Clean Kenyan flag on right-top
    fx0, fy0, fx1, fy1 = 98, 10, 150, 40
    stripes = [(INK, 8.8), (WHITE, 1.9), ((187, 0, 0), 8.6), (WHITE, 1.9), ((0, 102, 0), 8.8)]
    yy = fy0
    for col, sh in stripes:
        a.rect(fx0, yy, fx1, yy + sh, fill=col)
        yy += sh
    mx, my = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    a.circle(mx, my, 4.8, fill=(187, 0, 0), outline=WHITE, width=1.0)
    a.circle(mx, my, 1.7, fill=INK)
    a.rect(fx0, fy0, fx1, fy1, fill=None, outline=INK, width=0.9)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "TURKANA · 1ST WELL", 124, 49, 10.5, INK, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 11. Pancreatic Cancer Pill (Card 11: 188 x 80) -----------------------
def art_cancer():
    a = Art("art_11.png", GRID, (234, 246, 244))
    # Angled deep-teal & white pharmaceutical capsule on left
    cx, cy, half_l, r = 30, 41, 10.5, 10.2
    ang = math.radians(-30)
    deg = math.degrees(ang)
    ux, uy = math.cos(ang), -math.sin(ang)

    def draw_half(sign, col):
        ex, ey = cx + sign * half_l * ux, cy + sign * half_l * uy
        t0 = deg + 90 if sign > 0 else deg - 90
        arc = arc_pts(ex, ey, r, t0, t0 - 180, 24)
        mid = arc_pts(cx, cy, r, t0 - 180, t0, 1)
        a.poly([mid[1]] + arc + [mid[0]], fill=col, outline=NAVY, width=1.2)

    draw_half(-1, WHITE)
    draw_half(1, TEAL)
    for dx, dy in ((12, 20), (49, 58), (16, 60)):
        a.circle(dx, dy, 2.0, fill=(122, 192, 184))

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "60.7%", 122, 15, 24, TEAL, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "TUMOUR RESPONSE", 122, 48, 10.2, NAVY, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 12. Argentina Country Risk (Card 12: 188 x 80) -----------------------
def art_argentina():
    a = Art("art_12.png", GRID, (244, 246, 249))
    # Argentina flag on left
    fx0, fy0, fx1, fy1 = 8, 24, 44, 51
    sh = (fy1 - fy0) / 3
    a.rect(fx0, fy0, fx1, fy0 + sh, fill=(116, 172, 223))
    a.rect(fx0, fy0 + sh, fx1, fy0 + 2 * sh, fill=WHITE)
    a.rect(fx0, fy0 + 2 * sh, fx1, fy1, fill=(116, 172, 223))
    a.circle((fx0 + fx1) / 2, (fy0 + fy1) / 2, 3.0, fill=(246, 180, 14), outline=(180, 120, 20), width=0.6)
    a.rect(fx0, fy0, fx1, fy1, fill=None, outline=INK, width=0.8)

    # Semicircular risk gauge in middle
    gx, gy, gr = 80, 56, 24
    a.poly(arc_pts(gx, gy, gr, 0, 180, 32), fill=(26, 36, 52), outline=INK, width=1.1)
    for t0, t1, col in ((180, 120, (54, 172, 92)), (120, 68, (244, 182, 44)), (68, 0, RED)):
        a.line(arc_pts(gx, gy, gr - 4.3, t0, t1, 18), col, 3.5)
    tt = math.radians(68)
    a.line([(gx + (gr - 8.2) * math.cos(tt), gy - (gr - 8.2) * math.sin(tt)),
            (gx + (gr - 1.0) * math.cos(tt), gy - (gr - 1.0) * math.sin(tt))], WHITE, 1.5)
    nt = math.radians(28)
    a.line([(gx, gy), (gx + (gr - 5.2) * math.cos(nt), gy - (gr - 5.2) * math.sin(nt))], CORAL, 2.3)
    a.circle(gx, gy, 3.2, fill=CORAL, outline=WHITE, width=1.0)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "1,070", 146, 18, 19.5, CRIMSON, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "+15% RISK", 146, 46, 10.5, NAVY, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


# ---- 13. Wellington Cricket (Card 13: 188 x 80) ---------------------------
def art_phillips():
    a = Art("art_13.png", GRID, (203, 227, 198))
    # Clean subtle turf stripe + crease line
    a.rect(0, 56, 188, 80, fill=(189, 217, 183))
    a.line([(10, 62), (62, 62)], WHITE, 1.4)
    # Angled willow cricket bat on left
    # Handle
    a.line([(18, 16), (27, 29)], (36, 42, 52), 4.0)
    # Blade
    a.poly([(24, 29), (32, 24), (50, 52), (46, 61), (38, 59)],
           fill=(228, 196, 142), outline=INK, width=1.1)
    a.line([(28, 28), (44, 54)], (196, 162, 108), 1.2)
    # Red stitched cricket ball
    bx, by = 52, 24
    a.circle(bx, by, 7.2, fill=CRIMSON, outline=INK, width=1.0)
    a.arc(bx - 1, by, 5.2, 290, 70, fill=WHITE, width=1.1)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "118 & 175*", 126, 17, 19.5, INK, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "NZ 368 vs INDIA", 126, 46, 10.5, (20, 74, 48), path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(overlay)


ART_FUNCS = [
    art_kyiv, art_akvan, art_chips,
    art_nvidia, art_euuk, art_cop31, art_poland, art_hormuz,
    art_indiapak, art_kenya, art_cancer, art_argentina, art_phillips,
]


def build_all():
    LABELS.clear()
    for fn in ART_FUNCS:
        fn()
    bad = []
    by_art: dict[str, list[dict]] = {}
    for lb in LABELS:
        x0, y0, x1, y1 = lb["bbox"]
        w, h = lb["img"]
        pad = min(x0, y0, w - x1, h - y1)
        if pad < 3:
            bad.append((lb["art"], lb["text"], "padding", round(pad, 1)))
        by_art.setdefault(lb["art"], []).append(lb)
    for name, labels in by_art.items():
        for i, p in enumerate(labels):
            for q in labels[i + 1:]:
                a, b = p["bbox"], q["bbox"]
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    bad.append((name, p["text"], "overlaps", q["text"]))
        if any(lb["kind"] == "attr" for lb in labels):
            bad.append((name, "no source pill allowed inside picture"))
        if any(lb["kind"] == "badge" for lb in labels):
            bad.append((name, "v17 eliminates crimson corner badges"))
    if bad:
        raise SystemExit("art label failure:\n  " + "\n  ".join(map(str, bad)))
    kinds = sorted({lb["kind"] for lb in LABELS})
    print(f"art: {len(ART_FUNCS)} illustrations, {len(LABELS)} labels ({', '.join(kinds)}), "
          f"padding and overlap ok; zero corner stickers & zero source pills")


if __name__ == "__main__":
    build_all()

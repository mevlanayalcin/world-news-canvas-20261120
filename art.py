"""Editorial illustrations for the Friday 20 November 2026 front page (v18).

Each picture combines:
- an integrated full-width region-colored top banner ribbon (20 px on leads,
  17 px on secondary cards) carrying bold 300px-readable topic text;
- a clean flat/2-tone vector scene drawn from scratch with Pillow at 2x and
  reduced via Lanczos, paired with printed-size 1x FreeType primary figures.

Leads 1-3: 316x130. Cards 4-13: 188x76. Zero source pills inside pictures.
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

# Region banner fills matching mapgen.REGION_COLORS
R_EUROPE = (34, 83, 150)       # #225396
R_APAC = (184, 41, 47)         # #B8292F
R_AMERICAS = (22, 122, 115)    # #167A73
R_MIDEAST = (181, 98, 18)      # #B56212
R_AFRICA = (38, 122, 75)       # #267A4B
R_OCEANIA = (103, 61, 135)     # #673D87
R_GLOBAL = (59, 77, 107)       # #3B4D6B

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"

HERO = (316, 130)
GRID = (188, 76)
HERO_BAR = 20
GRID_BAR = 17

LABELS: list[dict] = []


def font(path: Path, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), round(size))


class Art:
    """2x supersampled canvas addressed in 1x pixel coordinates."""

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

    def finish(self, banner_bg: tuple[int, int, int], banner_left: str,
               banner_right: str | None = None, banner_right_fg=YELLOW, overlay=None):
        bar_h = HERO_BAR if self.lead else GRID_BAR
        # Crisp integrated top region banner bar
        self.rect(0, 0, self.w, bar_h, fill=banner_bg)
        out = self.im.resize(self.size, Image.LANCZOS)
        d = ImageDraw.Draw(out)
        if self.lead:
            f_l = font(LATO_BLACK, 12.0)
            d.text((8, bar_h / 2), banner_left, font=f_l, fill=WHITE, anchor="lm")
            bb_l = d.textbbox((8, bar_h / 2), banner_left, font=f_l, anchor="lm")
            LABELS.append(dict(art=self.name, kind="banner", text=banner_left,
                               bbox=tuple(round(v, 1) for v in bb_l), size=12, img=self.size, lead=True))
            if banner_right:
                f_r = font(LATO_BLACK, 10.5)
                d.text((self.w - 8, bar_h / 2), banner_right, font=f_r, fill=banner_right_fg, anchor="rm")
                bb_r = d.textbbox((self.w - 8, bar_h / 2), banner_right, font=f_r, anchor="rm")
                LABELS.append(dict(art=self.name, kind="banner_sub", text=banner_right,
                                   bbox=tuple(round(v, 1) for v in bb_r), size=10, img=self.size, lead=True))
        else:
            f_c = font(LATO_BLACK, 10.6)
            d.text((self.w / 2, bar_h / 2), banner_left, font=f_c, fill=WHITE, anchor="mm")
            bb_c = d.textbbox((self.w / 2, bar_h / 2), banner_left, font=f_c, anchor="mm")
            LABELS.append(dict(art=self.name, kind="banner", text=banner_left,
                               bbox=tuple(round(v, 1) for v in bb_c), size=11, img=self.size, lead=False))
        if overlay:
            overlay(self, d)
        ASSETS.mkdir(exist_ok=True)
        out.save(ASSETS / self.name, format="PNG", optimize=True)

    def pill(self, d: ImageDraw.ImageDraw, text: str, x: float, y: float, size: float,
             fg, bg, path=LATO_BLACK, anchor="tl", kind="callout",
             px=None, py=None, radius=2, outline=None):
        f = font(path, size)
        bb = d.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        px = round(size * 0.42) if px is None else px
        py = round(size * 0.24) if py is None else py
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
    a.rect(x0, y0, x1, y1, fill=None, outline=INK, width=0.9)


def draw_eu_flag(a: Art, x0, y0, x1, y1):
    a.rect(x0, y0, x1, y1, fill=(0, 51, 153), outline=INK, width=0.9)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = min(x1 - x0, y1 - y0) * 0.31
    for i in range(12):
        t = -math.pi / 2 + i * math.pi / 6
        a.star(cx + r * math.cos(t), cy + r * math.sin(t), 2.1, (255, 204, 0))


def arc_pts(cx, cy, r, a0_deg, a1_deg, n=36):
    out = []
    for i in range(n + 1):
        t = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        out.append((cx + r * math.cos(t), cy - r * math.sin(t)))
    return out


# ---- 1. Kyiv bridges (Lead 1: 316 x 130) ----------------------------------
def art_kyiv():
    a = Art("art_01.png", HERO, (14, 26, 44))
    a.rect(0, 44, 316, 74, fill=(22, 40, 68))
    # Skyline + Lavra dome clear of tracks
    a.poly([(0, 74), (0, 59), (18, 59), (22, 51), (36, 51), (40, 57), (54, 57),
            (60, 48), (76, 48), (80, 56), (106, 56), (114, 62), (138, 62), (138, 74)],
           fill=(28, 43, 66))
    a.poly([(190, 74), (196, 59), (224, 59), (230, 53), (254, 53), (260, 59),
            (284, 55), (294, 49), (316, 49), (316, 74)], fill=(30, 46, 70))
    a.rect(281, 38, 293, 59, fill=(44, 62, 92))
    a.circle(287, 37, 5.8, fill=GOLD)
    a.line([(287, 30), (287, 24)], GOLD, 1.3)
    # Dnipro river
    a.rect(0, 72, 316, 130, fill=(22, 43, 71))
    for rx, ry, rw in ((18, 88, 34), (222, 84, 40), (36, 108, 48), (224, 118, 52)):
        a.line([(rx, ry), (rx + rw, ry)], (46, 82, 122), 1.3)
    # Water fire reflections
    a.line([(96, 85), (112, 85)], (184, 98, 44), 1.4)
    a.line([(178, 102), (198, 102)], (198, 106, 42), 1.6)
    a.line([(132, 124), (156, 124)], (216, 114, 40), 1.8)
    # 3 Dnipro bridges
    a.rect(0, 74, 316, 78, fill=(208, 218, 232))
    for px in (42, 96, 150, 204, 258):
        a.arc(px + 27, 82, 20, 180, 360, (160, 178, 202), 1.2)
        a.rect(px - 2, 78, px + 2, 87, fill=(104, 122, 146))
    a.rect(0, 90, 316, 95, fill=(224, 232, 242))
    for px in (34, 98, 162, 226, 286):
        a.rect(px - 2.5, 95, px + 2.5, 107, fill=(92, 110, 134))
    a.line([(72, 110), (72, 70)], (240, 244, 250), 2.8)
    for sx in (24, 44, 104, 128):
        a.line([(72, 73), (sx, 110)], (188, 202, 220), 1.0)
    a.rect(0, 109, 316, 116, fill=(240, 244, 248))
    for px in (28, 72, 136, 206, 274):
        a.rect(px - 3, 116, px + 3, 130, fill=(80, 98, 122))
    # Incoming missile arcs
    a.line([(20, 25), (62, 50), (104, 75)], (255, 228, 168), 1.6)
    a.line([(296, 25), (242, 56), (188, 92)], (255, 228, 168), 1.8)
    a.line([(256, 24), (194, 65), (144, 110)], (255, 228, 168), 2.1)

    def starburst(bx, by, r_outer, r_mid, r_core):
        pts = []
        for i in range(16):
            r = r_outer if i % 2 == 0 else r_outer * 0.46
            ang = i * math.pi / 8
            pts.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
        a.poly(pts, fill=ORANGE)
        a.circle(bx, by, r_mid, fill=YELLOW)
        a.circle(bx, by, r_core, fill=WHITE)

    starburst(104, 76, 12.0, 5.4, 2.4)
    starburst(188, 92, 14.5, 6.5, 2.8)
    starburst(144, 111, 17.5, 7.8, 3.4)

    a.finish(R_EUROPE, "KYIV · 3 BRIDGES HIT", "111 MISSILES · 404 DRONES", YELLOW)


# ---- 2. Cyclone Akvan (Lead 2: 316 x 130) ---------------------------------
def art_akvan():
    a = Art("art_02.png", HERO, (39, 114, 148))
    a.poly([(0, 20), (166, 20), (142, 52), (118, 94), (94, 130), (0, 130)], fill=(52, 136, 170))
    coast = [(144, 20), (134, 38), (122, 58), (112, 74), (98, 98), (80, 120), (72, 130)]
    a.poly([(0, 20)] + coast + [(0, 130)], fill=(223, 211, 184))
    a.poly([(0, 62), (56, 70), (44, 100), (22, 130), (0, 130)], fill=(203, 211, 176))
    a.line(coast, fill=(166, 150, 120), width=1.6)

    cx, cy = 212, 83
    for r, w, col, s, e in (
        (31, 3.8, WHITE, 22, 290),
        (24, 3.2, (214, 238, 247), 185, 430),
        (17, 3.2, WHITE, 15, 295),
        (10.5, 2.6, (214, 238, 247), 160, 415),
    ):
        a.arc(cx, cy, r, s, e, fill=col, width=w)
    a.circle(cx, cy, 4.8, fill=(32, 96, 126), outline=WHITE, width=1.8)

    a.dashed_line(258, 104, 222, 88, (220, 44, 44), width=2.2, dash=5, gap=3)
    a.dashed_line(201, 80, 124, 74, (220, 44, 44), width=2.4, dash=5, gap=3)
    a.poly([(117, 73), (129, 67), (127, 80)], fill=(220, 44, 44))
    a.circle(112, 74, 4.6, fill=CRIMSON, outline=WHITE, width=1.5)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "ODISHA", 10, 27, 13, INK, path=LATO_BLACK, anchor="tl", kind="geo")
        art_obj.label(d, "INDIA", 10, 44, 9.5, (74, 85, 104), path=LATO_BOLD, anchor="tl", kind="geo")
        art_obj.pill(d, "GOPALPUR", 14, 66, 9.5, WHITE, NAVY, path=LATO_BLACK,
                     anchor="tl", kind="geo", px=5, py=2.5, radius=2)
        d.line([(79, 74), (105, 74)], fill=NAVY, width=1)
        art_obj.pill(d, "LANDFALL ~02:30Z", 310, 26, 9.5, WHITE, NAVY, path=LATO_BLACK,
                     anchor="tr", kind="callout", px=5, py=2.5, radius=2)
        art_obj.label(d, "BAY OF BENGAL", 308, 125, 9.5, (216, 240, 248),
                      path=LATO_BLACK, anchor="br", kind="geo")

    a.finish(R_APAC, "CYCLONE AKVAN · ODISHA", "372,000 EVACUATED", YELLOW, overlay=overlay)


# ---- 3. Global AI Rout (Lead 3: 316 x 130) --------------------------------
SCOREBOARD = [("S&P 500", "−3.7%"), ("NASDAQ", "−5.3%"), ("TAIEX", "−6.2%"), ("NVIDIA", "−14.0%")]


def art_chips():
    a = Art("art_03.png", HERO, (14, 22, 36))
    gx0, gx1 = 10, 174
    for gy in (40, 62, 84, 106, 122):
        a.line([(gx0, gy), (gx1, gy)], (30, 44, 66), 1.0)
    curve = [
        (10, 34), (26, 32), (38, 43), (52, 40), (66, 58), (80, 54),
        (96, 76), (110, 71), (126, 92), (140, 88), (156, 110), (170, 118)
    ]
    a.poly(curve + [(170, 124), (10, 124)], fill=(54, 22, 32))
    a.line(curve, RED, 2.8)
    a.circle(170, 118, 3.8, fill=CORAL, outline=WHITE, width=1.2)
    a.rrect(182, 26, 310, 124, r=3, fill=(22, 34, 54), outline=(44, 64, 96), width=1.0)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        x0, y0, x1, y1 = 182, 26, 310, 124
        f_lbl = font(LATO_BOLD, 12.2)
        f_val = font(LATO_BLACK, 12.2)
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

    a.finish(R_GLOBAL, "WALL ST · AI CORRECTION", "WORST WEEK SINCE 2020", YELLOW, overlay=overlay)


# ---- 4. Nvidia SEC Probe (Card 4: 188 x 76) -------------------------------
def art_nvidia():
    a = Art("art_04.png", GRID, (19, 27, 43))
    cx0, cy0, cx1, cy1 = 15, 29, 49, 63
    for k in range(4):
        py = cy0 + 5 + k * 8
        a.line([(cx0 - 5, py), (cx0, py)], (176, 188, 204), 1.5)
        a.line([(cx1, py), (cx1 + 5, py)], (176, 188, 204), 1.5)
        px = cx0 + 5 + k * 8
        a.line([(px, cy0 - 5), (px, cy0)], (176, 188, 204), 1.5)
        a.line([(px, cy1), (px, cy1 + 5)], (176, 188, 204), 1.5)
    a.rrect(cx0, cy0, cx1, cy1, r=3, fill=(38, 49, 68), outline=(176, 188, 204), width=1.1)
    a.rrect(cx0 + 6, cy0 + 6, cx1 - 6, cy1 - 6, r=2, fill=NV_GREEN)
    pts = [(64, 27), (75, 40), (70, 44), (82, 58)]
    a.line(pts, RED, 2.6)
    a.poly([(86, 64), (76, 59), (85, 53)], fill=RED)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "−14%", 138, 25, 21.5, CORAL, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "~$500BN LOST", 138, 53, 10.0, WHITE, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_AMERICAS, "NVIDIA · SEC PROBE", overlay=overlay)


# ---- 5. UK-EU Reset (Card 5: 188 x 76) ------------------------------------
def art_euuk():
    a = Art("art_05.png", GRID, (234, 241, 248))
    draw_union_jack(a, 14, 23, 66, 53)
    draw_eu_flag(a, 122, 23, 174, 53)
    a.line([(79, 38), (109, 38)], NAVY, 2.4)
    a.poly([(72, 38), (82, 32), (82, 44)], fill=NAVY)
    a.poly([(116, 38), (106, 32), (106, 44)], fill=NAVY)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "FOOD · CARBON · 100K VISAS", 94, 59, 9.8, NAVY,
                      path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_EUROPE, "UK–EU · TRADE RESET", overlay=overlay)


# ---- 6. COP31 Climate (Card 6: 188 x 76) ----------------------------------
def art_cop31():
    a = Art("art_06.png", GRID, (234, 244, 245))
    a.circle(26, 47, 16, fill=(78, 168, 186), outline=NAVY, width=1.2)
    a.poly([(17, 37), (26, 35), (30, 42), (23, 47), (16, 43)], fill=GREEN)
    a.poly([(24, 49), (34, 48), (33, 58), (26, 59)], fill=GREEN)
    a.circle(26, 47, 16, fill=None, outline=NAVY, width=1.2)
    cx, cy, r = 162, 47, 15.5
    a.circle(cx, cy, r, fill=WHITE, outline=NAVY, width=1.4)
    a.pieslice(cx, cy, r - 2, 270, 360, fill=(248, 210, 210))
    a.arc(cx, cy, r - 1, 270, 360, fill=CRIMSON, width=2.0)
    a.line([(cx, cy), (cx, cy - 9.5)], NAVY, 1.9)
    a.line([(cx, cy), (cx + 9, cy)], CRIMSON, 1.9)
    a.circle(cx, cy, 1.9, fill=NAVY)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "NO DEAL", 94, 30, 16, INK, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "OVERTIME", 94, 52, 10, CRIMSON, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_GLOBAL, "COP31 · DAY 12 OVERTIME", overlay=overlay)


# ---- 7. Poland Cruise Missile (Card 7: 188 x 76) --------------------------
def art_poland():
    a = Art("art_07.png", GRID, (243, 239, 228))
    a.rect(120, 17, 188, 76, fill=(234, 227, 212))
    a.dashed_line(120, 20, 120, 73, CRIMSON, width=1.7, dash=4.5, gap=3)
    a.rect(0, 65, 188, 76, fill=(214, 218, 194))
    for tx in (15, 29, 43, 57):
        a.poly([(tx, 50), (tx - 5.2, 65), (tx + 5.2, 65)], fill=(46, 94, 62))
        a.rect(tx - 1, 65, tx + 1, 69, fill=(92, 66, 46))
    a.line([(182, 42), (118, 47)], (204, 72, 72), 1.8)
    a.poly([(64, 48), (75, 44), (116, 44), (116, 50), (75, 50)], fill=(64, 74, 88), outline=INK, width=0.8)
    a.poly([(58, 47), (65, 44), (65, 50)], fill=CRIMSON)
    a.poly([(86, 44), (95, 36), (100, 44)], fill=(64, 74, 88))
    a.poly([(109, 44), (116, 39), (116, 44)], fill=(64, 74, 88))

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "POLAND", 8, 22, 10, NAVY, path=LATO_BLACK, anchor="tl", kind="geo")
        art_obj.label(d, "UKRAINE", 180, 22, 9.5, MUTED, path=LATO_BOLD, anchor="tr", kind="geo")
        art_obj.label(d, "KH-101", 89, 55, 10.5, CRIMSON, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_EUROPE, "POLAND · CRUISE MISSILE", overlay=overlay)


# ---- 8. Hormuz Tanker (Card 8: 188 x 76) ----------------------------------
def art_hormuz():
    a = Art("art_08.png", GRID, (220, 234, 242))
    a.poly([(118, 50), (138, 38), (156, 43), (172, 34), (188, 39), (188, 50)], fill=(201, 176, 147))
    a.rect(0, 50, 188, 76, fill=(53, 107, 130))
    for rx, ry, rw in ((14, 66, 34), (116, 68, 46), (62, 71, 30)):
        a.line([(rx, ry), (rx + rw, ry)], (94, 148, 168), 1.2)
    for sx, sy, sr, col in ((110, 34, 6.8, (94, 104, 114)), (122, 28, 7.4, (118, 128, 138)),
                            (135, 25, 6.0, (142, 152, 162))):
        a.circle(sx, sy, sr, fill=col)
    a.poly([(86, 48), (92, 34), (98, 41), (104, 29), (110, 41), (116, 36), (120, 48)], fill=ORANGE)
    a.poly([(93, 48), (98, 40), (104, 36), (109, 41), (113, 48)], fill=YELLOW)
    a.poly([(24, 48), (146, 48), (138, 62), (30, 62)], fill=(156, 38, 38), outline=INK, width=1.0)
    a.rect(28, 56, 140, 62, fill=(32, 38, 48))
    a.rect(30, 36, 50, 48, fill=WHITE, outline=INK, width=1.0)
    a.rect(34, 39, 46, 43, fill=NAVY)
    a.rect(40, 29, 46, 36, fill=(44, 52, 64))

    a.finish(R_MIDEAST, "HORMUZ · TANKER ABLAZE")


# ---- 9. India-Pakistan SCO (Card 9: 188 x 76) -----------------------------
def art_indiapak():
    a = Art("art_09.png", GRID, (239, 243, 247))
    px0, py0, px1, py1 = 12, 23, 64, 53
    a.rect(px0, py0, px0 + 13, py1, fill=WHITE)
    a.rect(px0 + 13, py0, px1, py1, fill=(1, 102, 56))
    a.circle(px0 + 33, (py0 + py1) / 2, 7.0, fill=WHITE)
    a.circle(px0 + 35.4, (py0 + py1) / 2 - 1.0, 5.8, fill=(1, 102, 56))
    a.star(px0 + 39.2, (py0 + py1) / 2 - 2.4, 2.6, fill=WHITE)
    a.rect(px0, py0, px1, py1, fill=None, outline=INK, width=0.9)

    ix0, iy0, ix1, iy1 = 124, 23, 176, 53
    sh = (iy1 - iy0) / 3
    a.rect(ix0, iy0, ix1, iy0 + sh, fill=(255, 153, 51))
    a.rect(ix0, iy0 + sh, ix1, iy0 + 2 * sh, fill=WHITE)
    a.rect(ix0, iy0 + 2 * sh, ix1, iy1, fill=(19, 136, 8))
    a.circle((ix0 + ix1) / 2, (iy0 + iy1) / 2, 3.6, fill=None, outline=(6, 3, 141), width=1.1)
    a.circle((ix0 + ix1) / 2, (iy0 + iy1) / 2, 1.1, fill=(6, 3, 141))
    a.rect(ix0, iy0, ix1, iy1, fill=None, outline=INK, width=0.9)

    a.dashed_line(69, 38, 119, 38, NAVY, width=2.0, dash=4.5, gap=3.5)
    a.circle(69, 38, 2.3, fill=CRIMSON)
    a.circle(119, 38, 2.3, fill=CRIMSON)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "FIRST VISIT SINCE MAY 2025", 94, 59, 9.5, NAVY,
                      path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_APAC, "INDIA–PAKISTAN · SCO", overlay=overlay)


# ---- 10. Kenya First Oil Well (Card 10: 188 x 76) -------------------------
def art_kenya():
    a = Art("art_10.png", GRID, (245, 234, 213))
    a.rect(0, 66, 188, 76, fill=(224, 200, 158))
    bl, br, top = 16, 46, 21
    cl, cr = 28, 34
    a.line([(bl, 66), (cl, top)], INK, 1.9)
    a.line([(br, 66), (cr, top)], INK, 1.9)
    a.line([(cl - 2, top), (cr + 2, top)], INK, 1.9)
    steps = 4
    for k in range(steps):
        t0, t1 = k / steps, (k + 1) / steps
        y0 = 66 - (66 - top) * t0
        y1 = 66 - (66 - top) * t1
        xl0, xr0 = bl + (cl - bl) * t0, br + (cr - br) * t0
        xl1, xr1 = bl + (cl - bl) * t1, br + (cr - br) * t1
        a.line([(xl0, y0), (xr0, y0)], INK, 1.0)
        a.line([(xl0, y0), (xr1, y1)], INK, 0.9)
        a.line([(xr0, y0), (xl1, y1)], INK, 0.9)
    a.rect(10, 64, 52, 69, fill=(56, 62, 72), outline=INK, width=0.9)

    fx0, fy0, fx1, fy1 = 98, 22, 150, 49
    stripes = [(INK, 7.8), (WHITE, 1.8), ((187, 0, 0), 7.8), (WHITE, 1.8), ((0, 102, 0), 7.8)]
    yy = fy0
    for col, sh in stripes:
        a.rect(fx0, yy, fx1, yy + sh, fill=col)
        yy += sh
    mx, my = (fx0 + fx1) / 2, (fy0 + fy1) / 2
    a.circle(mx, my, 4.4, fill=(187, 0, 0), outline=WHITE, width=0.9)
    a.circle(mx, my, 1.6, fill=INK)
    a.rect(fx0, fy0, fx1, fy1, fill=None, outline=INK, width=0.9)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "TURKANA · AMOSING", 124, 53, 9.8, INK, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_AFRICA, "KENYA · FIRST OIL WELL", overlay=overlay)


# ---- 11. Pancreatic Cancer Pill (Card 11: 188 x 76) -----------------------
def art_cancer():
    a = Art("art_11.png", GRID, (234, 246, 244))
    cx, cy, half_l, r = 30, 47, 9.8, 9.5
    ang = math.radians(-30)
    deg = math.degrees(ang)
    ux, uy = math.cos(ang), -math.sin(ang)

    def draw_half(sign, col):
        ex, ey = cx + sign * half_l * ux, cy + sign * half_l * uy
        t0 = deg + 90 if sign > 0 else deg - 90
        arc = arc_pts(ex, ey, r, t0, t0 - 180, 24)
        mid = arc_pts(cx, cy, r, t0 - 180, t0, 1)
        a.poly([mid[1]] + arc + [mid[0]], fill=col, outline=NAVY, width=1.1)

    draw_half(-1, WHITE)
    draw_half(1, TEAL)
    for dx, dy in ((13, 28), (48, 62), (16, 64)):
        a.circle(dx, dy, 1.9, fill=(122, 192, 184))

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "60.7%", 122, 23, 22.5, TEAL, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "TUMOUR RESPONSE", 122, 53, 9.8, NAVY, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_GLOBAL, "CANCER · PILL TRIAL", overlay=overlay)


# ---- 12. Argentina Country Risk (Card 12: 188 x 76) -----------------------
def art_argentina():
    a = Art("art_12.png", GRID, (244, 246, 249))
    fx0, fy0, fx1, fy1 = 8, 34, 44, 60
    sh = (fy1 - fy0) / 3
    a.rect(fx0, fy0, fx1, fy0 + sh, fill=(116, 172, 223))
    a.rect(fx0, fy0 + sh, fx1, fy0 + 2 * sh, fill=WHITE)
    a.rect(fx0, fy0 + 2 * sh, fx1, fy1, fill=(116, 172, 223))
    a.circle((fx0 + fx1) / 2, (fy0 + fy1) / 2, 2.9, fill=(246, 180, 14), outline=(180, 120, 20), width=0.6)
    a.rect(fx0, fy0, fx1, fy1, fill=None, outline=INK, width=0.8)

    gx, gy, gr = 80, 62, 22.5
    a.poly(arc_pts(gx, gy, gr, 0, 180, 32), fill=(26, 36, 52), outline=INK, width=1.1)
    for t0, t1, col in ((180, 120, (54, 172, 92)), (120, 68, (244, 182, 44)), (68, 0, RED)):
        a.line(arc_pts(gx, gy, gr - 4.0, t0, t1, 18), col, 3.3)
    tt = math.radians(68)
    a.line([(gx + (gr - 7.8) * math.cos(tt), gy - (gr - 7.8) * math.sin(tt)),
            (gx + (gr - 1.0) * math.cos(tt), gy - (gr - 1.0) * math.sin(tt))], WHITE, 1.4)
    nt = math.radians(28)
    a.line([(gx, gy), (gx + (gr - 4.8) * math.cos(nt), gy - (gr - 4.8) * math.sin(nt))], CORAL, 2.2)
    a.circle(gx, gy, 3.0, fill=CORAL, outline=WHITE, width=1.0)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "1,070", 146, 26, 19, CRIMSON, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "+15% JUMP", 146, 52, 10, NAVY, path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_AMERICAS, "ARGENTINA · COUNTRY RISK", overlay=overlay)


# ---- 13. Wellington Cricket (Card 13: 188 x 76) ---------------------------
def art_phillips():
    a = Art("art_13.png", GRID, (203, 227, 198))
    a.rect(0, 58, 188, 76, fill=(189, 217, 183))
    a.line([(10, 63), (62, 63)], WHITE, 1.3)
    a.line([(18, 25), (27, 37)], (36, 42, 52), 3.6)
    a.poly([(24, 37), (31, 32), (48, 56), (44, 64), (37, 62)],
           fill=(228, 196, 142), outline=INK, width=1.0)
    a.line([(28, 36), (43, 58)], (196, 162, 108), 1.1)
    bx, by = 50, 32
    a.circle(bx, by, 6.5, fill=CRIMSON, outline=INK, width=0.9)
    a.arc(bx - 1, by, 4.6, 290, 70, fill=WHITE, width=1.0)

    def overlay(art_obj: Art, d: ImageDraw.ImageDraw):
        art_obj.label(d, "118 & 175*", 126, 26, 19, INK, path=LATO_BLACK, anchor="tc", kind="stat")
        art_obj.label(d, "NZ 368 vs INDIA", 126, 53, 10, (20, 74, 48), path=LATO_BLACK, anchor="tc", kind="sub")

    a.finish(R_OCEANIA, "CRICKET · WELLINGTON", overlay=overlay)


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
        min_pad = 2.0 if lb["kind"].startswith("banner") else 3.0
        pad = min(x0, y0, w - x1, h - y1)
        if pad < min_pad:
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
    if bad:
        raise SystemExit("art label failure:\n  " + "\n  ".join(map(str, bad)))
    kinds = sorted({lb["kind"] for lb in LABELS})
    print(f"art: {len(ART_FUNCS)} illustrations, {len(LABELS)} labels ({', '.join(kinds)}), "
          f"region banners + crisp vector stats ok; zero source pills")


if __name__ == "__main__":
    build_all()

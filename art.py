"""Editorial illustrations for the Friday 20 November 2026 front page (v4).

Every picture is drawn from scratch with Pillow at twice its printed size and
reduced with Lanczos, so edges are supersampled. Coordinates are written as
fractions of the 2x canvas (X(0.5) is the horizontal middle), which keeps each
drawing correct at the hero size (310x120) and the grid size (180x72).
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

# ---- palette ---------------------------------------------------------------
PAPER = (255, 253, 247)
CREAM = (246, 241, 230)
INK = (20, 25, 35)
CRIMSON = (154, 27, 31)
NAVY = (27, 42, 65)
TEAL = (29, 111, 106)
SKY = (176, 212, 232)
SKY_D = (120, 168, 200)
SEA = (40, 108, 140)
SEA_D = (26, 78, 108)
SAND = (232, 214, 176)
GOLD = (242, 184, 60)
ORANGE = (236, 112, 40)
GREEN = (40, 128, 76)
GREY = (130, 136, 144)
STONE = (214, 204, 184)
WHITE = (255, 255, 255)
RED = (206, 38, 44)
BLUE = (40, 92, 160)

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"
SERIF_BOLD = FONT_DIR / "liberation" / "LiberationSerif-Bold.ttf"

HERO = (310, 120)
GRID = (180, 72)

LABELS: list[tuple[str, str, tuple[float, float, float, float], tuple[int, int], int]] = []


class Art:
    """A 2x drawing surface addressed in fractions of its width and height."""

    def __init__(self, name: str, size: tuple[int, int], bg):
        self.name = name
        self.size = size
        self.W, self.H = size[0] * 2, size[1] * 2
        self.im = Image.new("RGB", (self.W, self.H), bg)
        self.d = ImageDraw.Draw(self.im)
        # stroke unit: 1 printed pixel at hero size, scaled down for the grid
        self.u = self.W / 620

    def X(self, f: float) -> float:
        return f * self.W

    def Y(self, f: float) -> float:
        return f * self.H

    def P(self, pts):
        return [(self.X(x), self.Y(y)) for x, y in pts]

    def box(self, x0, y0, x1, y1):
        return [self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)]

    def lw(self, n: float) -> int:
        return max(1, round(n * self.u * 2))

    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, width=1.5):
        self.d.rectangle(self.box(x0, y0, x1, y1), fill=fill, outline=outline,
                         width=self.lw(width) if outline else 0)

    def rrect(self, x0, y0, x1, y1, r=4, fill=None, outline=INK, width=1.5):
        self.d.rounded_rectangle(self.box(x0, y0, x1, y1), radius=r * self.u * 2,
                                 fill=fill, outline=outline, width=self.lw(width) if outline else 0)

    def poly(self, pts, fill=None, outline=INK, width=1.5):
        self.d.polygon(self.P(pts), fill=fill, outline=outline,
                       width=self.lw(width) if outline else 0)

    def line(self, pts, fill=INK, width=1.5):
        self.d.line(self.P(pts), fill=fill, width=self.lw(width), joint="curve")

    def circle(self, cx, cy, r, fill=None, outline=INK, width=1.5):
        """r is a fraction of the canvas height so circles stay round."""
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill, outline=outline,
                       width=self.lw(width) if outline else 0)

    def arc(self, cx, cy, r, start, end, fill=INK, width=1.5):
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        self.d.arc([x - rr, y - rr, x + rr, y + rr], start, end, fill=fill, width=self.lw(width))

    def star(self, cx, cy, r, fill=GOLD, points=5, rot=-math.pi / 2, inner=0.42):
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        pts = []
        for i in range(points * 2):
            q = rr if i % 2 == 0 else rr * inner
            a = rot + i * math.pi / points
            pts.append((x + q * math.cos(a), y + q * math.sin(a)))
        self.d.polygon(pts, fill=fill)

    def text(self, cx, cy, s, size, fill=INK, path=LATO_BLACK):
        f = ImageFont.truetype(str(path), round(size * 2))
        self.d.text((self.X(cx), self.Y(cy)), s, font=f, fill=fill, anchor="mm")

    def tag(self, s, x, y, size=13, fg=WHITE, bg=CRIMSON, anchor="ll"):
        """A solid badge; x,y is its bottom-left (ll) or top-right (tr) corner.

        size is the printed font size in page pixels.
        """
        f = ImageFont.truetype(str(LATO_BLACK), round(size * 2))
        bb = self.d.textbbox((0, 0), s, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad_x, pad_y = th * 0.55, th * 0.42
        w, h = tw + 2 * pad_x, th + 2 * pad_y
        X, Y = self.X(x), self.Y(y)
        if anchor == "ll":
            x0, y0 = X, Y - h
        elif anchor == "tl":
            x0, y0 = X, Y
        else:  # tr
            x0, y0 = X - w, Y
        # 1 printed px ink keyline so every badge separates cleanly from the art
        self.d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h * 0.18, fill=bg,
                                 outline=INK, width=2)
        self.d.text((x0 + pad_x - bb[0], y0 + pad_y - bb[1]), s, font=f, fill=fg)
        LABELS.append((self.name, s, (x0, y0, x0 + w, y0 + h), (self.W, self.H), round(th / 2)))

    def save(self):
        out = self.im.resize(self.size, Image.LANCZOS)
        out = out.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2))
        ASSETS.mkdir(exist_ok=True)
        out.save(ASSETS / self.name, format="PNG", optimize=True)


# ---- shared props ----------------------------------------------------------
def person(a: Art, x, y, h, fill=INK, arms_up=False):
    """A simple standing figure; y is the feet line, h its height (fractions)."""
    hr = h * 0.13
    a.circle(x, y - h + hr, hr, fill=fill, outline=None)
    bw = h * 0.16 * a.H / a.W
    a.rrect(x - bw, y - h + hr * 2.1, x + bw, y, r=3, fill=fill, outline=None)
    if arms_up:
        a.line([(x - bw * 0.8, y - h * 0.62), (x - bw * 2.2, y - h * 1.02)], fill, 2.2)
        a.line([(x + bw * 0.8, y - h * 0.62), (x + bw * 2.2, y - h * 1.02)], fill, 2.2)


def raindrops(a: Art, y0, y1, n, color, seed=1):
    for i in range(n):
        fx = ((i * 0.6180339 + seed * 0.13) % 1.0)
        fy = y0 + ((i * 0.381966 + seed * 0.29) % 1.0) * (y1 - y0)
        a.line([(fx, fy), (fx - 0.012, fy + 0.07)], color, 1.4)


def union_jack(a: Art, x0, y0, x1, y1):
    a.rect(x0, y0, x1, y1, fill=(1, 33, 105), outline=INK, width=1.5)
    a.line([(x0, y0), (x1, y1)], WHITE, 7)
    a.line([(x1, y0), (x0, y1)], WHITE, 7)
    a.line([(x0, y0), (x1, y1)], RED, 2.4)
    a.line([(x1, y0), (x0, y1)], RED, 2.4)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw = (x1 - x0) * 0.09
    hh = (y1 - y0) * 0.16
    a.rect(cx - hw, y0, cx + hw, y1, fill=WHITE, outline=None)
    a.rect(x0, cy - hh, x1, cy + hh, fill=WHITE, outline=None)
    a.rect(cx - hw * 0.55, y0, cx + hw * 0.55, y1, fill=RED, outline=None)
    a.rect(x0, cy - hh * 0.55, x1, cy + hh * 0.55, fill=RED, outline=None)
    a.rect(x0, y0, x1, y1, fill=None, outline=INK, width=1.5)


def eu_flag(a: Art, x0, y0, x1, y1):
    a.rect(x0, y0, x1, y1, fill=(0, 51, 153), outline=INK, width=1.5)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = (y1 - y0) * 0.32
    for i in range(12):
        t = -math.pi / 2 + i * math.pi / 6
        a.star(cx + r * math.cos(t) * a.H / a.W, cy + r * math.sin(t), (y1 - y0) * 0.055, (255, 204, 0))


# ---- H1. Kyiv bridges ------------------------------------------------------
def art_kyiv():
    a = Art("art_01.png", HERO, (64, 92, 128))
    # pre-dawn sky gradient
    for i in range(20):
        t = i / 19
        col = tuple(int(c0 + (c1 - c0) * t) for c0, c1 in zip((44, 62, 96), (214, 150, 110)))
        a.rect(0, i * 0.03, 1, i * 0.03 + 0.031, fill=col, outline=None)
    # far bank skyline + Lavra domes
    a.poly([(0, 0.52), (0.06, 0.47), (0.12, 0.49), (0.2, 0.44), (0.28, 0.48), (0.36, 0.46),
            (0.44, 0.5), (0.44, 0.6), (0, 0.6)], fill=(52, 60, 78), outline=None)
    a.poly([(0.58, 0.6), (0.64, 0.46), (0.86, 0.44), (0.94, 0.5), (1, 0.48), (1, 0.6)],
           fill=(66, 74, 90), outline=None)
    a.rect(0.73, 0.38, 0.79, 0.58, fill=(222, 214, 196), outline=INK, width=1.2)
    a.circle(0.76, 0.37, 0.065, fill=(214, 168, 46), outline=INK, width=1.2)
    a.line([(0.76, 0.30), (0.76, 0.21)], INK, 1.5)
    a.line([(0.745, 0.245), (0.775, 0.245)], INK, 1.5)
    # river Dnipro
    a.rect(0, 0.6, 1, 1, fill=(36, 74, 108), outline=None)
    for k in range(6):
        y = 0.7 + k * 0.05
        a.line([(0.04 + (k % 2) * 0.1, y), (0.16 + (k % 2) * 0.1, y)], (110, 156, 190), 1.2)
        a.line([(0.62 + (k % 3) * 0.08, y), (0.74 + (k % 3) * 0.08, y)], (110, 156, 190), 1.2)
    # three bridges stacked in depth; the near one broken
    for k, (y, th, col) in enumerate(((0.56, 0.026, (176, 182, 190)), (0.63, 0.034, (196, 200, 206)),
                                      (0.72, 0.05, (226, 226, 222)))):
        if k < 2:
            a.rect(0, y, 1, y + th, fill=col, outline=INK, width=1)
            for px in (0.15, 0.35, 0.55, 0.75, 0.95):
                a.rect(px - 0.006, y + th, px + 0.006, y + th + 0.05 + k * 0.02, fill=(90, 96, 104), outline=None)
        else:
            a.poly([(0, y), (0.42, y), (0.46, y + th + 0.03), (0, y + th)], fill=col, outline=INK, width=1.2)
            a.poly([(0.58, y + 0.02), (1, y), (1, y + th), (0.55, y + th + 0.04)], fill=col, outline=INK, width=1.2)
            for px in (0.1, 0.3, 0.75, 0.92):
                a.rect(px - 0.009, y + th, px + 0.009, 0.95, fill=(80, 86, 96), outline=INK, width=0.8)
            # falling debris
            for dx, dy, s in ((0.47, 0.84, 0.018), (0.5, 0.9, 0.012), (0.53, 0.82, 0.015)):
                a.rect(dx - s, dy - s, dx + s, dy + s, fill=(90, 90, 96), outline=INK, width=0.8)
    # missile streaks and blast
    a.line([(0.08, 0.02), (0.3, 0.28), (0.47, 0.62)], (255, 230, 190), 2.4)
    a.line([(0.95, 0.04), (0.78, 0.3), (0.66, 0.52)], (255, 230, 190), 2.0)
    bx, by = 0.5, 0.66
    for i in range(12):
        t = i * math.pi / 6
        a.line([(bx, by), (bx + 0.07 * math.cos(t) * a.H / a.W, by + 0.14 * math.sin(t))], ORANGE, 3)
    a.circle(bx, by, 0.075, fill=GOLD, outline=CRIMSON, width=2)
    a.circle(bx, by, 0.03, fill=WHITE, outline=None)
    a.circle(0.66, 0.53, 0.04, fill=GOLD, outline=ORANGE, width=1.5)
    a.tag("KYIV  ·  3 BRIDGES HIT", 0.025, 0.95, 14, WHITE, CRIMSON)
    a.tag("DNIPRO RIVER", 0.975, 0.05, 10.5, INK, (242, 226, 196), anchor="tr")
    a.save()


# ---- H2. Cyclone Akvan -----------------------------------------------------
def art_akvan():
    a = Art("art_02.png", HERO, SEA)
    a.rect(0, 0, 1, 1, fill=(52, 126, 156), outline=None)
    # Bay of Bengal swell lines
    for k in range(7):
        y = 0.12 + k * 0.12
        a.arc(0.2 + (k % 2) * 0.1, y + 0.1, 0.12, 200, 340, (120, 186, 208), 1.2)
    # Odisha / Andhra coast (land on the left, sea on the right)
    a.poly([(0, 0), (0.46, 0), (0.42, 0.18), (0.36, 0.34), (0.30, 0.52), (0.22, 0.72),
            (0.12, 0.9), (0.06, 1), (0, 1)], fill=(206, 196, 150), outline=INK, width=1.5)
    a.poly([(0, 0), (0.30, 0), (0.25, 0.2), (0.18, 0.42), (0.1, 0.62), (0, 0.8)],
           fill=(150, 176, 112), outline=None)
    # cyclone spiral over the sea
    cx, cy = 0.66, 0.46
    for r, w in ((0.42, 5), (0.33, 4.5), (0.24, 4), (0.15, 3.5)):
        a.arc(cx, cy, r, 20, 300, WHITE, w)
        a.arc(cx, cy, r - 0.04, 200, 470, (206, 232, 240), w * 0.6)
    a.circle(cx, cy, 0.06, fill=(60, 120, 150), outline=WHITE, width=2.5)
    # landfall track arrow toward Gopalpur
    a.line([(0.9, 0.95), (0.78, 0.7), (0.66, 0.46), (0.47, 0.32)], GOLD, 2.4)
    a.poly([(0.40, 0.29), (0.47, 0.25), (0.47, 0.37)], fill=GOLD, outline=None)
    # Gopalpur pin
    a.circle(0.36, 0.32, 0.045, fill=CRIMSON, outline=WHITE, width=2)
    # shelter with evacuees on land
    a.poly([(0.05, 0.56), (0.13, 0.46), (0.21, 0.56)], fill=CRIMSON, outline=INK, width=1.2)
    a.rect(0.065, 0.56, 0.195, 0.7, fill=PAPER, outline=INK, width=1.2)
    a.rect(0.115, 0.61, 0.145, 0.7, fill=INK, outline=None)
    for i, x in enumerate((0.04, 0.22, 0.25)):
        person(a, x, 0.74, 0.13 - i * 0.01)
    # rain bands
    raindrops(a, 0.02, 0.9, 26, (200, 228, 238), seed=3)
    a.tag("GOPALPUR", 0.03, 0.14, 10.5, WHITE, NAVY, anchor="tl")
    a.tag("CYCLONE AKVAN  ·  ODISHA", 0.025, 0.95, 14, WHITE, CRIMSON)
    a.tag("372,000 EVACUATED", 0.975, 0.05, 10.5, INK, GOLD, anchor="tr")
    a.save()


# ---- H3. Asia chip-stock rout ---------------------------------------------
def art_chips():
    a = Art("art_03.png", HERO, (16, 22, 34))
    a.rect(0, 0, 1, 1, fill=(18, 24, 38), outline=None)
    # faint price grid
    for k in range(1, 6):
        a.line([(0, k * 0.16), (1, k * 0.16)], (40, 50, 70), 1)
    for k in range(1, 10):
        a.line([(k * 0.1, 0), (k * 0.1, 1)], (32, 40, 58), 1)
    # silicon wafer with dies (left)
    cx, cy, r = 0.2, 0.52, 0.36
    a.circle(cx, cy, r, fill=(150, 164, 186), outline=(220, 228, 240), width=1.6)
    a.circle(cx, cy, r * 0.93, fill=(96, 112, 150), outline=None)
    rx = r * a.H / a.W
    for i in range(-4, 5):
        for j in range(-4, 5):
            x0, y0 = cx + i * rx * 0.2, cy + j * r * 0.2
            if math.hypot((x0 - cx) / rx, (y0 - cy) / r) < 0.82:
                col = (196, 160, 70) if (i + j) % 3 else (226, 196, 110)
                a.rect(x0 - rx * 0.085, y0 - r * 0.085, x0 + rx * 0.085, y0 + r * 0.085, fill=col, outline=None)
    a.poly([(cx - rx * 0.12, cy + r * 0.98), (cx + rx * 0.12, cy + r * 0.98), (cx, cy + r * 0.88)],
           fill=(18, 24, 38), outline=None)
    # crack across the wafer
    a.line([(0.1, 0.24), (0.16, 0.42), (0.13, 0.52), (0.22, 0.66), (0.19, 0.8)], (18, 24, 38), 2.6)
    a.line([(0.1, 0.24), (0.16, 0.42), (0.13, 0.52), (0.22, 0.66), (0.19, 0.8)], (240, 90, 80), 1)
    # falling candlesticks (right)
    candles = [(0.44, 0.18, 0.30, 0.12, 0.36, False), (0.5, 0.22, 0.38, 0.16, 0.44, True),
               (0.56, 0.34, 0.42, 0.28, 0.48, True), (0.62, 0.38, 0.52, 0.32, 0.58, True),
               (0.68, 0.46, 0.5, 0.42, 0.56, False), (0.74, 0.5, 0.64, 0.44, 0.7, True),
               (0.8, 0.6, 0.72, 0.54, 0.78, True), (0.86, 0.66, 0.84, 0.6, 0.9, True)]
    for x, o, c, hi, lo, down in candles:
        o, c, hi, lo = (0.2 + v * 0.62 for v in (o, c, hi, lo))
        col = (226, 56, 56) if down else (60, 190, 120)
        a.line([(x, hi), (x, lo)], col, 1.4)
        a.rect(x - 0.018, min(o, c), x + 0.018, max(o, c), fill=col, outline=None)
    a.tag("TAIEX −6.23%", 0.975, 0.05, 12, WHITE, (200, 34, 40), anchor="tr")
    a.tag("KOSPI −5.2%  ·  NIKKEI −5.1%", 0.025, 0.05, 10, INK, GOLD, anchor="tl")
    a.tag("ASIA  ·  AI & CHIP ROUT", 0.025, 0.95, 14, WHITE, CRIMSON)
    a.save()


# ---- G1. UK-EU summit ------------------------------------------------------
def art_euuk():
    a = Art("art_04.png", GRID, (214, 228, 240))
    a.rect(0, 0, 1, 1, fill=(214, 228, 240), outline=None)
    a.rect(0.32, 0.08, 0.68, 0.7, fill=(178, 200, 220), outline=INK, width=1.4)
    for i in range(7):
        a.line([(0.32 + i * 0.06, 0.08), (0.32 + i * 0.06, 0.7)], (140, 166, 190), 1)
    a.circle(0.5, 0.36, 0.2, fill=(236, 170, 70), outline=INK, width=1.4)
    a.circle(0.5, 0.36, 0.11, fill=(250, 214, 140), outline=None)
    a.line([(0.06, 0.06), (0.06, 0.92)], INK, 2)
    eu_flag(a, 0.065, 0.06, 0.28, 0.4)
    a.line([(0.94, 0.06), (0.94, 0.92)], INK, 2)
    union_jack(a, 0.725, 0.06, 0.935, 0.4)
    a.rect(0, 0.78, 1, 1, fill=(196, 182, 156), outline=None)
    a.rrect(0.22, 0.7, 0.78, 0.8, r=5, fill=NAVY, outline=INK, width=1.2)
    person(a, 0.4, 0.74, 0.4, fill=(36, 44, 60))
    person(a, 0.6, 0.74, 0.4, fill=(36, 44, 60))
    a.line([(0.42, 0.55), (0.5, 0.59), (0.58, 0.55)], (36, 44, 60), 4)
    a.circle(0.5, 0.59, 0.045, fill=(232, 196, 160), outline=INK, width=1)
    a.tag("UK–EU  ·  3 DEALS", 0.03, 0.95, 10.5, WHITE, NAVY)
    a.tag("100K / YR", 0.97, 0.47, 9.5, INK, GOLD, anchor="tr")
    a.save()

# ---- G2. COP31 -------------------------------------------------------------
def art_cop31():
    a = Art("art_05.png", GRID, (244, 196, 116))
    a.rect(0, 0, 1, 0.72, fill=(246, 204, 128), outline=None)
    a.rect(0, 0.72, 1, 1, fill=(44, 132, 150), outline=None)
    # globe with thermometer
    a.circle(0.24, 0.42, 0.28, fill=(226, 240, 248), outline=INK, width=1.5)
    a.poly([(0.17, 0.26), (0.25, 0.22), (0.3, 0.32), (0.24, 0.4), (0.16, 0.36)], fill=GREEN, outline=None)
    a.poly([(0.22, 0.48), (0.32, 0.46), (0.3, 0.6), (0.24, 0.62)], fill=GREEN, outline=None)
    a.rrect(0.395, 0.12, 0.435, 0.6, r=4, fill=WHITE, outline=INK, width=1.2)
    a.rrect(0.403, 0.3, 0.427, 0.6, r=3, fill=RED, outline=None)
    a.circle(0.415, 0.64, 0.08, fill=RED, outline=INK, width=1.2)
    # the draft text, "fossil fuels" struck out
    a.poly([(0.54, 0.08), (0.94, 0.08), (0.94, 0.66), (0.54, 0.66)], fill=WHITE, outline=INK, width=1.3)
    for k in range(4):
        a.line([(0.58, 0.18 + k * 0.1), (0.9, 0.18 + k * 0.1)], GREY, 1.1)
    a.rect(0.57, 0.33, 0.91, 0.45, fill=(255, 236, 236), outline=None)
    a.text(0.74, 0.39, "FOSSIL FUELS", 9, CRIMSON)
    a.line([(0.57, 0.39), (0.91, 0.39)], CRIMSON, 1.6)
    a.tag("COP31  ·  ANTALYA", 0.03, 0.95, 10.5, WHITE, NAVY)
    a.save()


# ---- G3. Italy general strike ----------------------------------------------
def art_italy():
    a = Art("art_06.png", GRID, (238, 222, 196))
    a.rect(0, 0, 1, 1, fill=(244, 226, 196), outline=None)
    a.rect(0, 0, 1, 0.06, fill=GREEN, outline=None)
    a.rect(0, 0.06, 1, 0.1, fill=WHITE, outline=None)
    a.rect(0, 0.1, 1, 0.14, fill=RED, outline=None)
    # Colosseum arches
    a.rect(0.52, 0.22, 0.98, 0.66, fill=(222, 192, 150), outline=INK, width=1.2)
    for row in range(3):
        for k in range(7):
            x = 0.545 + k * 0.062
            y = 0.27 + row * 0.13
            a.rrect(x, y, x + 0.035, y + 0.1, r=6, fill=(150, 112, 80), outline=None)
    # stopped bus with STRIKE sign
    a.rrect(0.04, 0.4, 0.46, 0.7, r=4, fill=(230, 160, 40), outline=INK, width=1.3)
    for k in range(4):
        a.rect(0.07 + k * 0.09, 0.45, 0.13 + k * 0.09, 0.55, fill=(190, 220, 236), outline=None)
    a.circle(0.12, 0.72, 0.06, fill=INK, outline=None)
    a.circle(0.38, 0.72, 0.06, fill=INK, outline=None)
    a.rect(0.12, 0.58, 0.38, 0.66, fill=CRIMSON, outline=None)
    a.text(0.25, 0.62, "SCIOPERO", 9, WHITE)
    # marchers with red flags
    a.rect(0, 0.76, 1, 1, fill=(196, 176, 150), outline=None)
    for i in range(11):
        x = 0.05 + i * 0.09
        person(a, x, 0.98, 0.2 + (i % 3) * 0.02, fill=(40, 40, 50))
    for x in (0.52, 0.72, 0.9):
        a.line([(x, 0.8), (x, 0.56)], INK, 1.2)
        a.poly([(x, 0.56), (x + 0.08, 0.6), (x, 0.65)], fill=RED, outline=None)
    a.tag("ITALY  ·  24H STRIKE", 0.03, 0.27, 10.5, WHITE, CRIMSON)
    a.save()


# ---- G4. Trump White House presser -----------------------------------------
def art_trump():
    a = Art("art_07.png", GRID, (40, 56, 92))
    a.rect(0, 0, 1, 1, fill=(36, 54, 94), outline=None)
    # blue curtain folds and a briefing-room oval panel
    for k in range(10):
        a.rect(k * 0.1, 0, k * 0.1 + 0.05, 1, fill=(44, 64, 108), outline=None)
    a.d.ellipse(a.box(0.3, 0.04, 0.7, 0.36), fill=(226, 232, 242), outline=INK, width=a.lw(1.2))
    a.d.ellipse(a.box(0.34, 0.08, 0.66, 0.32), fill=None, outline=(36, 54, 94), width=a.lw(1.2))
    a.text(0.5, 0.2, "WHITE HOUSE", 9, NAVY)
    # US flags either side (generic stripes)
    for x0 in (0.04, 0.8):
        a.line([(x0, 0.08), (x0, 0.98)], (200, 170, 90), 1.6)
        for st in range(7):
            col = RED if st % 2 == 0 else WHITE
            a.rect(x0 + 0.01, 0.1 + st * 0.05, x0 + 0.16, 0.15 + st * 0.05, fill=col, outline=None)
        a.rect(x0 + 0.01, 0.1, x0 + 0.075, 0.25, fill=(20, 40, 110), outline=None)
    # flanking figures and speaker at a podium
    person(a, 0.3, 0.86, 0.5, fill=(22, 26, 38))
    person(a, 0.7, 0.86, 0.5, fill=(22, 26, 38))
    person(a, 0.5, 0.8, 0.42, fill=(16, 18, 28))
    a.poly([(0.4, 0.62), (0.6, 0.62), (0.57, 1), (0.43, 1)], fill=(120, 84, 52), outline=INK, width=1.2)
    a.circle(0.5, 0.78, 0.07, fill=GOLD, outline=INK, width=1)
    a.line([(0.47, 0.62), (0.45, 0.5)], INK, 1.2)
    a.line([(0.53, 0.62), (0.55, 0.5)], INK, 1.2)
    a.tag("PRESSER  ·  IRAN", 0.03, 0.95, 10.5, WHITE, CRIMSON)
    a.save()


# ---- G5. UN straw poll -----------------------------------------------------
def art_un():
    a = Art("art_08.png", GRID, (60, 120, 180))
    a.rect(0, 0, 1, 1, fill=(64, 128, 188), outline=None)
    # stylised globe with olive arcs (not the UN emblem itself)
    a.circle(0.24, 0.42, 0.27, fill=(224, 238, 250), outline=WHITE, width=1.6)
    a.arc(0.24, 0.42, 0.18, 0, 360, (64, 128, 188), 1.2)
    a.arc(0.24, 0.42, 0.09, 0, 360, (64, 128, 188), 1.2)
    a.line([(0.08, 0.42), (0.4, 0.42)], (64, 128, 188), 1.2)
    a.line([(0.24, 0.16), (0.24, 0.68)], (64, 128, 188), 1.2)
    a.arc(0.24, 0.42, 0.33, 110, 250, (250, 250, 250), 2)
    a.arc(0.24, 0.42, 0.33, 290, 430, (250, 250, 250), 2)
    # ballot box receiving red (P5) and white (E10) ballots
    a.rect(0.52, 0.44, 0.92, 0.8, fill=(240, 240, 236), outline=INK, width=1.4)
    a.rect(0.62, 0.42, 0.82, 0.47, fill=INK, outline=None)
    for i, col in enumerate((RED, WHITE, RED, WHITE, WHITE)):
        x = 0.56 + i * 0.075
        y = 0.12 + (i % 2) * 0.1
        a.rect(x, y, x + 0.06, y + 0.17, fill=col, outline=INK, width=1)
    a.text(0.72, 0.62, "9TH POLL", 9, NAVY)
    a.tag("UN  ·  NEXT CHIEF", 0.03, 0.95, 10.5, WHITE, NAVY)
    a.save()


# ---- G6. Saudi intercepts --------------------------------------------------
def art_riyadh():
    a = Art("art_09.png", GRID, (130, 170, 210))
    for i in range(12):
        t = i / 11
        col = tuple(int(c0 + (c1 - c0) * t) for c0, c1 in zip((90, 130, 186), (238, 206, 160)))
        a.rect(0, i * 0.06, 1, i * 0.06 + 0.061, fill=col, outline=None)
    a.rect(0, 0.72, 1, 1, fill=(214, 176, 120), outline=None)
    # skyline with a tall bottle-opener tower silhouette
    for x0, x1, top in ((0.04, 0.12, 0.56), (0.13, 0.2, 0.48), (0.22, 0.28, 0.6),
                        (0.62, 0.7, 0.52), (0.72, 0.8, 0.6), (0.82, 0.92, 0.5)):
        a.rect(x0, top, x1, 0.74, fill=(70, 74, 86), outline=None)
    a.poly([(0.38, 0.74), (0.43, 0.14), (0.49, 0.14), (0.54, 0.74)], fill=(58, 62, 76), outline=None)
    a.poly([(0.425, 0.2), (0.495, 0.2), (0.48, 0.3), (0.44, 0.3)], fill=(150, 176, 210), outline=None)
    # interceptor arcs and bursts
    for sx, ex, ey in ((0.1, 0.3, 0.16), (0.9, 0.72, 0.14), (0.95, 0.86, 0.3)):
        a.line([(sx, 0.72), ((sx + ex) / 2, ey + 0.18), (ex, ey)], (255, 250, 230), 1.6)
        a.circle(ex, ey, 0.06, fill=GOLD, outline=ORANGE, width=1.4)
    # drones (small deltas)
    for x, y in ((0.62, 0.1), (0.7, 0.28), (0.18, 0.34)):
        a.poly([(x - 0.03, y), (x + 0.03, y), (x, y + 0.06)], fill=INK, outline=None)
    a.tag("RIYADH  ·  INTERCEPTS", 0.03, 0.95, 10.5, WHITE, CRIMSON)
    a.save()


# ---- G7. Florida floods ----------------------------------------------------
def art_florida():
    a = Art("art_10.png", GRID, (120, 140, 156))
    a.rect(0, 0, 1, 0.6, fill=(122, 138, 152), outline=None)
    for x, y, s in ((0.15, 0.12, 0.12), (0.45, 0.08, 0.16), (0.8, 0.14, 0.12)):
        a.circle(x, y, s, fill=(92, 104, 118), outline=None)
        a.circle(x + 0.08, y + 0.04, s * 0.9, fill=(92, 104, 118), outline=None)
    raindrops(a, 0.14, 0.62, 30, (210, 226, 236), seed=7)
    # floodwater with houses and a palm
    a.rect(0, 0.6, 1, 1, fill=(92, 120, 110), outline=None)
    for x, w, h in ((0.08, 0.2, 0.2), (0.38, 0.18, 0.18), (0.66, 0.22, 0.2)):
        a.rect(x, 0.62 - h * 0.6, x + w, 0.74, fill=PAPER, outline=INK, width=1.2)
        a.poly([(x - 0.02, 0.62 - h * 0.6), (x + w / 2, 0.62 - h * 1.3), (x + w + 0.02, 0.62 - h * 0.6)],
               fill=(150, 70, 56), outline=INK, width=1.2)
        a.rect(x + w * 0.4, 0.6, x + w * 0.6, 0.74, fill=INK, outline=None)
    a.rect(0, 0.7, 1, 1, fill=(84, 112, 104), outline=None)
    for k in range(5):
        a.line([(0.04 + k * 0.2, 0.8), (0.14 + k * 0.2, 0.8)], (150, 180, 170), 1.2)
    # airboat
    a.poly([(0.56, 0.86), (0.84, 0.86), (0.8, 0.94), (0.6, 0.94)], fill=CRIMSON, outline=INK, width=1.2)
    a.circle(0.87, 0.8, 0.07, fill=None, outline=INK, width=1.3)
    person(a, 0.66, 0.86, 0.14, fill=(250, 200, 60))
    a.tag("FLORIDA  ·  FLOODS", 0.03, 0.95, 10.5, WHITE, NAVY)
    a.save()


# ---- G8. China-Australia ---------------------------------------------------
def art_china_aus():
    a = Art("art_11.png", GRID, (172, 36, 40))
    a.rect(0, 0, 1, 1, fill=(186, 50, 46), outline=None)
    for i in range(14):
        t = i * math.pi / 7
        a.line([(0.5, 0.64), (0.5 + 0.7 * math.cos(t), 0.64 + 1.2 * math.sin(t))], (204, 72, 60), 3)
    # PRC flag
    a.rect(0.05, 0.1, 0.36, 0.46, fill=(222, 41, 16), outline=INK, width=1.2)
    a.star(0.11, 0.2, 0.07, (255, 222, 0))
    for dx, dy in ((0.17, 0.13), (0.195, 0.19), (0.195, 0.27), (0.17, 0.33)):
        a.star(dx, dy, 0.025, (255, 222, 0))
    # Australian flag
    a.rect(0.64, 0.1, 0.95, 0.46, fill=(1, 33, 105), outline=INK, width=1.2)
    union_jack(a, 0.64, 0.1, 0.795, 0.28)
    a.star(0.715, 0.38, 0.05, WHITE, points=7)
    for dx, dy in ((0.88, 0.15), (0.84, 0.26), (0.92, 0.3), (0.88, 0.4)):
        a.star(dx, dy, 0.03, WHITE, points=7)
    # handshake
    a.rrect(0.26, 0.58, 0.48, 0.7, r=6, fill=(232, 196, 160), outline=INK, width=1.2)
    a.rrect(0.52, 0.58, 0.74, 0.7, r=6, fill=(214, 172, 132), outline=INK, width=1.2)
    a.circle(0.5, 0.64, 0.09, fill=GOLD, outline=INK, width=1.2)
    a.tag("XI–ALBANESE", 0.03, 0.95, 10.5, WHITE, NAVY)
    a.save()


# ---- G9. Dakar migration ---------------------------------------------------
def art_dakar():
    a = Art("art_12.png", GRID, (60, 140, 170))
    a.rect(0, 0, 1, 1, fill=(64, 146, 178), outline=None)
    # West African bulge (land on the right)
    a.poly([(0.42, 0), (1, 0), (1, 1), (0.6, 1), (0.52, 0.8), (0.46, 0.62), (0.36, 0.5),
            (0.34, 0.4), (0.4, 0.26), (0.44, 0.12)], fill=(222, 196, 140), outline=INK, width=1.3)
    a.poly([(0.6, 0.6), (1, 0.5), (1, 1), (0.6, 1)], fill=(150, 176, 104), outline=None)
    # Dakar star on the Cap-Vert peninsula
    a.star(0.355, 0.44, 0.09, CRIMSON)
    # regional routes converging on Dakar
    for (sx, sy) in ((0.92, 0.18), (0.94, 0.62), (0.76, 0.86), (0.7, 0.3)):
        a.line([(sx, sy), ((sx + 0.36) / 2, (sy + 0.44) / 2 - 0.06), (0.38, 0.44)], (120, 40, 30), 1.6)
        a.circle(sx, sy, 0.04, fill=NAVY, outline=WHITE, width=1)
    # pirogue on the Atlantic
    a.poly([(0.04, 0.72), (0.28, 0.72), (0.24, 0.82), (0.08, 0.82)], fill=(236, 112, 40), outline=INK, width=1.2)
    a.rect(0.04, 0.7, 0.28, 0.73, fill=GOLD, outline=None)
    for k in range(3):
        a.line([(0.04 + k * 0.08, 0.9), (0.1 + k * 0.08, 0.9)], (170, 214, 230), 1.2)
    a.tag("DAKAR  ·  ROADMAP", 0.03, 0.27, 10.5, WHITE, (46, 125, 80))
    a.save()


# ---- G10. BepiColombo ------------------------------------------------------
def art_bepi():
    a = Art("art_13.png", GRID, (10, 14, 28))
    a.rect(0, 0, 1, 1, fill=(12, 16, 30), outline=None)
    for i in range(40):
        fx = (i * 0.6180339) % 1.0
        fy = (i * 0.381966 + 0.11) % 1.0
        a.circle(fx, fy, 0.008 + (i % 3) * 0.004, fill=(220, 224, 236), outline=None)
    # the Sun's glare at the left edge
    a.circle(-0.08, 0.5, 0.5, fill=(250, 196, 80), outline=None)
    a.circle(-0.08, 0.5, 0.38, fill=(255, 232, 150), outline=None)
    # Mercury with craters
    a.circle(0.62, 0.52, 0.34, fill=(150, 146, 140), outline=(210, 206, 198), width=1.4)
    for x, y, r in ((0.56, 0.4, 0.06), (0.68, 0.62, 0.08), (0.6, 0.66, 0.035), (0.7, 0.36, 0.04)):
        a.circle(x, y, r, fill=(118, 114, 110), outline=None)
    # dashed capture orbit
    for k in range(0, 360, 20):
        a.d.arc(a.box(0.38, 0.12, 0.86, 0.92), k, k + 11, fill=(120, 200, 230), width=a.lw(1.4))
    # spacecraft: body, solar wing
    a.rect(0.84, 0.16, 0.9, 0.3, fill=(230, 200, 120), outline=INK, width=1)
    a.rect(0.9, 0.2, 0.99, 0.26, fill=(60, 90, 170), outline=(200, 210, 230), width=0.8)
    a.rect(0.75, 0.2, 0.84, 0.26, fill=(60, 90, 170), outline=(200, 210, 230), width=0.8)
    a.tag("MERCURY  ·  SAT 21 NOV", 0.03, 0.95, 10.5, WHITE, (74, 85, 99))
    a.save()


ART_FUNCS = [art_kyiv, art_akvan, art_chips, art_euuk, art_cop31, art_italy, art_trump,
             art_un, art_riyadh, art_florida, art_china_aus, art_dakar, art_bepi]


def build_all():
    LABELS.clear()
    for fn in ART_FUNCS:
        fn()
    bad = []
    for name, s, (x0, y0, x1, y1), (W, H), half_cap in LABELS:
        pad = min(x0, y0, W - x1, H - y1)
        printed_cap = half_cap  # cap height in printed px (2x canvas / 2)
        if pad < 4 or printed_cap < 6:
            bad.append((name, s, round(pad, 1), printed_cap))
    if bad:
        raise SystemExit(f"art label failure: {bad}")
    print(f"art: {len(ART_FUNCS)} illustrations, {len(LABELS)} badges, padding ok")


if __name__ == "__main__":
    build_all()

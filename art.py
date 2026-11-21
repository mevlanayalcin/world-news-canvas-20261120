"""Editorial illustrations for the Friday 20 November 2026 front page (v19).

Builds the 13 full-bleed pictorial scenes at 2x with Pillow and reduces them
via Lanczos before stamping printed-size 1x FreeType typography: unified
editorial crimson banner pills on all 13 cards, lead callouts on 1-3, and the
four-market scoreboard on lead 3. Zero source pills inside illustrations.

v19 precision upgrades:
- Lead 1 (Kyiv) prints official consensus '111 missiles · 404 drones'.
- Card 12 (Argentina) prints exact 'ARGENTINA: 1,070'.
"""
from __future__ import annotations

import math
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

# ---- palette ---------------------------------------------------------------
PAPER = (255, 253, 247)
CREAM = (247, 243, 233)
INK = (18, 24, 34)
CRIMSON = (154, 27, 31)
NAVY = (27, 42, 65)
SKY = (176, 212, 232)
SEA = (40, 108, 140)
GOLD = (242, 184, 60)
ORANGE = (236, 112, 40)
GREEN = (40, 128, 76)
GREY = (130, 136, 144)
WHITE = (255, 255, 255)
RED = (206, 38, 44)
BLUE = (40, 92, 160)
B_CRIMSON = (184, 41, 47)

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"
LATO_HEAVY = FONT_DIR / "lato" / "Lato-Heavy.ttf"

HERO = (316, 132)
GRID = (188, 78)
HERO_BAND, HERO_BADGE = 28, 17
GRID_BAND, GRID_BADGE = 20, 14

LABELS: list[dict] = []
SUBJECT_DIFF = 12


def font(path: Path, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), round(size))


class Art:
    """2x surface addressed in fractions of the scene below the top band."""

    def __init__(self, name: str, size: tuple[int, int], bg, band: int):
        self.name = name
        self.size = size
        self.lead = size[0] > 200
        self.W = size[0] * 2
        self.oy = band * 2
        self.H = size[1] * 2 - self.oy
        self.im = Image.new("RGB", (self.W, size[1] * 2), bg)
        self.d = ImageDraw.Draw(self.im)
        self.bg_im = Image.new("RGB", (self.W, size[1] * 2), bg)
        self.bd = ImageDraw.Draw(self.bg_im)
        self._bg = False
        self.u = self.W / 632

    @contextmanager
    def background(self):
        self._bg = True
        try:
            yield self
        finally:
            self._bg = False

    def _targets(self):
        return (self.d, self.bd) if self._bg else (self.d,)

    def X(self, f: float) -> float:
        return f * self.W

    def Y(self, f: float) -> float:
        return 0.0 if f <= 0 else self.oy + f * self.H

    def P(self, pts):
        return [(self.X(x), self.Y(y)) for x, y in pts]

    def box(self, x0, y0, x1, y1):
        return [self.X(x0), self.Y(y0), self.X(x1), self.Y(y1)]

    def lw(self, n: float) -> int:
        return max(1, round(n * self.u * 2))

    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, width=1.5):
        for d in self._targets():
            d.rectangle(self.box(x0, y0, x1, y1), fill=fill, outline=outline,
                        width=self.lw(width) if outline else 0)

    def rrect(self, x0, y0, x1, y1, r=4, fill=None, outline=INK, width=1.5):
        for d in self._targets():
            d.rounded_rectangle(self.box(x0, y0, x1, y1), radius=r * self.u * 2,
                                fill=fill, outline=outline, width=self.lw(width) if outline else 0)

    def poly(self, pts, fill=None, outline=INK, width=1.5):
        for d in self._targets():
            d.polygon(self.P(pts), fill=fill, outline=outline,
                      width=self.lw(width) if outline else 0)

    def line(self, pts, fill=INK, width=1.5):
        for d in self._targets():
            d.line(self.P(pts), fill=fill, width=self.lw(width), joint="curve")

    def circle(self, cx, cy, r, fill=None, outline=INK, width=1.5):
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        for d in self._targets():
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill, outline=outline,
                      width=self.lw(width) if outline else 0)

    def arc(self, cx, cy, r, start, end, fill=INK, width=1.5):
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        for d in self._targets():
            d.arc([x - rr, y - rr, x + rr, y + rr], start, end, fill=fill, width=self.lw(width))

    def star(self, cx, cy, r, fill=GOLD, points=5, rot=-math.pi / 2, inner=0.42):
        x, y, rr = self.X(cx), self.Y(cy), r * self.H
        pts = []
        for i in range(points * 2):
            q = rr if i % 2 == 0 else rr * inner
            a = rot + i * math.pi / points
            pts.append((x + q * math.cos(a), y + q * math.sin(a)))
        for d in self._targets():
            d.polygon(pts, fill=fill)

    def gradient(self, top, bottom, y0=0.0, y1=1.0, steps=24):
        steps = max(steps, 128)
        for i in range(steps):
            t = i / (steps - 1)
            col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
            ya = y0 + (y1 - y0) * i / steps
            self.rect(0, ya, 1, ya + (y1 - y0) / steps + 0.002, fill=col, outline=None)

    def finish(self, badge: str, callout: str | None = None, overlay=None):
        out = self.im.resize(self.size, Image.LANCZOS)
        bg = self.bg_im.resize(self.size, Image.LANCZOS)
        diff = np.abs(np.asarray(out, np.int16) - np.asarray(bg, np.int16)).max(axis=2)
        self.mask = diff > SUBJECT_DIFF
        d = ImageDraw.Draw(out)
        if self.lead:
            pad, top, size = 6, 4, HERO_BADGE
        else:
            pad, top, size = 4, 3, GRID_BADGE
        _, _, _, by1 = self._pill(d, badge, pad, top, size, WHITE, B_CRIMSON, LATO_BLACK,
                                  "tl", "badge")
        if callout:
            self._pill(d, callout, pad, by1 + 3, 14, INK, WHITE, LATO_HEAVY, "tl", "callout")
        if overlay:
            overlay(self, d)
        ASSETS.mkdir(exist_ok=True)
        out.save(ASSETS / self.name, format="PNG", optimize=True)

    def _pill(self, d, s, x, y, size, fg, bg, path, anchor, kind, outline=None, py=None):
        f = font(path, size)
        bb = d.textbbox((0, 0), s, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        px, py = round(size * 0.45), (round(size * 0.28) if py is None else py)
        bw, bht = tw + 2 * px, th + 2 * py
        x0 = x if anchor in ("tl", "bl") else x - bw
        y0 = y if anchor in ("tl", "tr") else y - bht
        if bg is not None or outline is not None:
            d.rounded_rectangle([x0, y0, x0 + bw, y0 + bht], radius=3, fill=bg,
                                outline=outline, width=1)
        d.text((x0 + px - bb[0], y0 + py - bb[1]), s, font=f, fill=fg)
        LABELS.append(dict(art=self.name, kind=kind, text=s, bbox=(x0, y0, x0 + bw, y0 + bht),
                           size=round(size), img=self.size, lead=self.lead,
                           gap=self.subject_gap((x0, y0, x0 + bw, y0 + bht))))
        return x0, y0, x0 + bw, y0 + bht

    def subject_gap(self, bbox, limit: int = 12) -> int:
        x0, y0, x1, y1 = (int(math.floor(bbox[0])), int(math.floor(bbox[1])),
                          int(math.ceil(bbox[2])), int(math.ceil(bbox[3])))
        h, w = self.mask.shape
        for k in range(0, limit + 1):
            a, b = max(0, x0 - k), max(0, y0 - k)
            c, e = min(w, x1 + k), min(h, y1 + k)
            if self.mask[b:e, a:c].any():
                return k - 1
        return limit


def person(a: Art, x, y, h, fill=INK, arms_up=False):
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
    hw, hh = (x1 - x0) * 0.09, (y1 - y0) * 0.16
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


def flagpole(a: Art, x, y_top, y_bot):
    a.line([(x, y_top), (x, y_bot)], INK, 1.6)


def kyiv_labels(a: Art, d: ImageDraw.ImageDraw):
    """Official barrage count in cream type on the night sky at top right."""
    a._pill(d, "111 missiles · 404 drones", a.size[0] - 4, 4, 10.5, (236, 226, 208), None,
            LATO_BLACK, "tr", "geo")


def akvan_labels(a: Art, d: ImageDraw.ImageDraw):
    dx, dy = a.X(0.4) / 2, a.Y(0.36) / 2
    a._pill(d, "Gopalpur", round(dx - 6), round(dy + 7), 10.5, INK, PAPER, LATO_BLACK, "tl", "geo")
    a._pill(d, "BAY OF BENGAL", a.size[0] - 4, 4, 10, INK, None, LATO_BLACK, "tr", "geo")


def art_kyiv():
    a = Art("art_01.png", HERO, (64, 92, 128), HERO_BAND)
    with a.background():
        a.gradient((40, 56, 92), (214, 150, 110), 0, 0.6)
        a.poly([(0, 0.5), (0.06, 0.44), (0.12, 0.47), (0.2, 0.4), (0.28, 0.45), (0.36, 0.43),
                (0.44, 0.48), (0.44, 0.6), (0, 0.6)], fill=(52, 60, 78), outline=None)
        a.poly([(0.58, 0.6), (0.64, 0.44), (0.86, 0.42), (0.94, 0.48), (1, 0.46), (1, 0.6)],
               fill=(66, 74, 90), outline=None)
    a.rect(0.79, 0.3, 0.85, 0.56, fill=(222, 214, 196), outline=INK, width=1.2)
    a.circle(0.82, 0.29, 0.07, fill=(214, 168, 46), outline=INK, width=1.2)
    a.line([(0.82, 0.21), (0.82, 0.1)], INK, 1.5)
    a.line([(0.805, 0.15), (0.835, 0.15)], INK, 1.5)
    with a.background():
        a.rect(0, 0.6, 1, 1, fill=(36, 74, 108), outline=None)
        for k in range(3):
            y = 0.76 + k * 0.08
            a.line([(0.64 + k * 0.08, y), (0.76 + k * 0.08, y)], (110, 156, 190), 1.2)
    for k, (y, th, col) in enumerate(((0.52, 0.028, (176, 182, 190)), (0.6, 0.036, (196, 200, 206)),
                                      (0.68, 0.05, (226, 226, 222)))):
        if k < 2:
            a.rect(0, y, 1, y + th, fill=col, outline=INK, width=1)
            for px in (0.15, 0.35, 0.55, 0.75, 0.95):
                a.rect(px - 0.006, y + th, px + 0.006, y + th + 0.05 + k * 0.02, fill=(90, 96, 104), outline=None)
        else:
            a.poly([(0, y), (0.42, y), (0.46, y + th + 0.03), (0, y + th)], fill=col, outline=INK, width=1.2)
            a.poly([(0.58, y + 0.02), (1, y), (1, y + th), (0.55, y + th + 0.04)], fill=col, outline=INK, width=1.2)
            for px in (0.3, 0.75, 0.92):
                a.rect(px - 0.009, y + th, px + 0.009, 0.97, fill=(80, 86, 96), outline=INK, width=0.8)
            for dx, dy, s in ((0.47, 0.86, 0.018), (0.5, 0.92, 0.012), (0.53, 0.84, 0.015)):
                a.rect(dx - s, dy - s, dx + s, dy + s, fill=(90, 90, 96), outline=INK, width=0.8)
    a.line([(0.34, 0.02), (0.44, 0.3), (0.5, 0.66)], (255, 230, 190), 2.4)
    a.line([(0.98, 0.02), (0.8, 0.3), (0.68, 0.57)], (255, 230, 190), 2.0)
    bx, by = 0.5, 0.66
    for i in range(12):
        t = i * math.pi / 6
        a.line([(bx, by), (bx + 0.06 * math.cos(t) * a.H / a.W, by + 0.13 * math.sin(t))], ORANGE, 3)
    a.circle(bx, by, 0.075, fill=GOLD, outline=CRIMSON, width=2)
    a.circle(bx, by, 0.03, fill=WHITE, outline=None)
    a.circle(0.68, 0.59, 0.045, fill=GOLD, outline=ORANGE, width=1.5)
    a.circle(0.6, 0.53, 0.035, fill=GOLD, outline=ORANGE, width=1.5)
    a.finish("KYIV", "3 bridges hit", overlay=kyiv_labels)


def art_akvan():
    a = Art("art_02.png", HERO, SEA, HERO_BAND)
    with a.background():
        a.rect(0, 0, 1, 1, fill=(52, 126, 156), outline=None)
        a.poly([(0, 0), (0.5, 0), (0.46, 0.18), (0.4, 0.34), (0.34, 0.52), (0.26, 0.72),
                (0.16, 0.9), (0.1, 1), (0, 1)], fill=(206, 196, 150), outline=INK, width=1.5)
        a.poly([(0, 0.3), (0.3, 0.3), (0.26, 0.45), (0.18, 0.62), (0.1, 0.8), (0, 0.95)],
               fill=(150, 176, 112), outline=None)
    cx, cy = 0.7, 0.5
    for r, w in ((0.44, 5), (0.33, 4.5), (0.22, 4)):
        a.arc(cx, cy, r, 20, 300, WHITE, w)
        a.arc(cx, cy, r - 0.055, 200, 380, (206, 232, 240), w * 0.6)
    a.circle(cx, cy, 0.06, fill=(60, 120, 150), outline=WHITE, width=2.5)
    a.line([(0.94, 0.98), (0.82, 0.74), (0.7, 0.5), (0.5, 0.36)], GOLD, 2.4)
    a.poly([(0.43, 0.34), (0.5, 0.29), (0.5, 0.42)], fill=GOLD, outline=None)
    a.circle(0.4, 0.36, 0.045, fill=CRIMSON, outline=WHITE, width=2)
    a.poly([(0.05, 0.565), (0.13, 0.445), (0.21, 0.565)], fill=CRIMSON, outline=INK, width=1.2)
    a.rect(0.065, 0.565, 0.195, 0.725, fill=PAPER, outline=INK, width=1.2)
    a.rect(0.115, 0.625, 0.145, 0.725, fill=INK, outline=None)
    for i, x in enumerate((0.23, 0.26, 0.29)):
        person(a, x, 0.745, 0.15 - i * 0.012)
    raindrops(a, 0.55, 0.95, 4, (200, 228, 238), seed=3)
    a.finish("CYCLONE AKVAN", "Landfall · 8 am", overlay=akvan_labels)


CORAL = (255, 107, 107)
BOARD_PX = 14
SCOREBOARD = [("Taipei", "−6.2%"), ("Nasdaq", "−5.3%"), ("Seoul", "−5.2%"), ("S&P 500", "−3.7%")]


def chips_scoreboard(a: Art, d: ImageDraw.ImageDraw):
    x0, y0, x1, y1 = 193, 6, 310, 126
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=(30, 40, 60), outline=(78, 92, 120), width=1)
    head = font(LATO_BLACK, 10)
    d.text(((x0 + x1) / 2, y0 + 10), "INDEX CLOSE", font=head, fill=(170, 182, 204), anchor="mm")
    d.line([(x0 + 6, y0 + 19), (x1 - 6, y0 + 19)], fill=(78, 92, 120), width=1)
    city, pct = font(LATO_BOLD, BOARD_PX), font(LATO_BLACK, BOARD_PX)
    row_h = (y1 - y0 - 22) / len(SCOREBOARD)
    for i, (c, v) in enumerate(SCOREBOARD):
        cy = y0 + 22 + row_h * (i + 0.5)
        d.text((x0 + 7, cy), c, font=city, fill=WHITE, anchor="lm")
        d.text((x1 - 7, cy), v, font=pct, fill=CORAL, anchor="rm")
        if i:
            yy = round(y0 + 22 + row_h * i)
            d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(52, 64, 88), width=1)
    LABELS.append(dict(art=a.name, kind="board", text="scoreboard", bbox=(x0, y0, x1, y1),
                       size=BOARD_PX, img=a.size, lead=a.lead))


def art_chips():
    a = Art("art_03.png", HERO, (16, 22, 34), HERO_BAND)
    with a.background():
        a.rect(0, 0, 1, 1, fill=(18, 24, 38), outline=None)
        cx0, cx1 = 15 / 316, 185 / 316
        for k in range(1, 6):
            a.line([(cx0, k * 0.16), (cx1, k * 0.16)], (40, 50, 70), 1)
    curve = [(0.00, 0.30), (0.08, 0.27), (0.15, 0.36), (0.22, 0.33), (0.30, 0.48), (0.38, 0.45),
             (0.47, 0.62), (0.55, 0.58), (0.64, 0.76), (0.72, 0.72), (0.82, 0.86), (0.91, 0.84),
             (1.00, 0.95)]
    pts = [(cx0 + (cx1 - cx0) * x, y) for x, y in curve]
    a.poly(pts + [(cx1, 1), (cx0, 1)], fill=(64, 26, 36), outline=None)
    for i in range(1, len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        x = (xa + xb) / 2
        col = (226, 56, 56) if yb > ya else (60, 190, 120)
        a.rect(x - 0.008, min(ya, yb), x + 0.008, max(ya, yb), fill=col, outline=None)
    a.line(pts, (255, 92, 92), 2.6)
    a.circle(pts[-1][0], pts[-1][1], 0.035, fill=CORAL, outline=WHITE, width=1.2)
    a.finish("AI SELL-OFF", callout="US & Asia, Friday", overlay=chips_scoreboard)


def art_euuk():
    a = Art("art_05.png", GRID, (214, 228, 240), GRID_BAND)
    with a.background():
        a.rect(0, 0, 1, 1, fill=(214, 228, 240), outline=None)
    a.rect(0.32, 0.04, 0.68, 0.5, fill=(178, 200, 220), outline=INK, width=1.4)
    for i in range(7):
        a.line([(0.32 + i * 0.06, 0.04), (0.32 + i * 0.06, 0.5)], (140, 166, 190), 1)
    a.line([(0.06, 0.04), (0.06, 0.58)], INK, 2)
    eu_flag(a, 0.065, 0.06, 0.28, 0.4)
    a.line([(0.94, 0.04), (0.94, 0.58)], INK, 2)
    union_jack(a, 0.725, 0.06, 0.935, 0.4)
    with a.background():
        a.rect(0, 0.58, 1, 1, fill=(196, 182, 156), outline=None)
        for k in range(3):
            a.line([(0, 0.7 + k * 0.11), (1, 0.7 + k * 0.11)], (184, 170, 144), 1)
    a.rrect(0.22, 0.47, 0.78, 0.57, r=5, fill=NAVY, outline=INK, width=1.2)
    person(a, 0.4, 0.5, 0.46, fill=(36, 44, 60))
    person(a, 0.6, 0.5, 0.46, fill=(36, 44, 60))
    a.line([(0.42, 0.3), (0.5, 0.345), (0.58, 0.3)], (36, 44, 60), 4)
    a.circle(0.5, 0.345, 0.055, fill=(232, 196, 160), outline=INK, width=1)
    a.finish("UK–EU DEAL")


def art_cop31():
    a = Art("art_06.png", GRID, (244, 196, 116), GRID_BAND)
    with a.background():
        a.rect(0, 0, 1, 0.74, fill=(246, 204, 128), outline=None)
        a.rect(0, 0.74, 1, 1, fill=(44, 132, 150), outline=None)
    a.circle(0.18, 0.44, 0.34, fill=(226, 240, 248), outline=INK, width=1.5)
    a.poly([(0.1, 0.26), (0.19, 0.2), (0.25, 0.32), (0.18, 0.42), (0.09, 0.38)], fill=GREEN, outline=None)
    a.poly([(0.16, 0.5), (0.27, 0.48), (0.24, 0.66), (0.18, 0.68)], fill=GREEN, outline=None)
    a.rrect(0.37, 0.08, 0.41, 0.62, r=4, fill=WHITE, outline=INK, width=1.2)
    a.rrect(0.378, 0.26, 0.402, 0.62, r=3, fill=RED, outline=None)
    a.circle(0.39, 0.68, 0.1, fill=RED, outline=INK, width=1.2)
    a.poly([(0.5, 0.04), (0.9, 0.04), (0.9, 0.56), (0.5, 0.56)], fill=WHITE, outline=INK, width=1.3)
    for k in range(5):
        y = 0.12 + k * 0.1
        a.line([(0.54, y), (0.86, y)], GREY if k != 2 else CRIMSON, 1.3 if k != 2 else 1.8)
    a.rect(0.53, 0.28, 0.87, 0.36, fill=(255, 226, 226), outline=None)
    a.line([(0.54, 0.32), (0.86, 0.32)], CRIMSON, 2)
    a.line([(0.6, 0.24), (0.8, 0.4)], CRIMSON, 1.6)
    a.line([(0.6, 0.4), (0.8, 0.24)], CRIMSON, 1.6)
    a.finish("COP31: NO DEAL")


def art_poland():
    a = Art("art_07.png", GRID, (190, 206, 222), GRID_BAND)
    with a.background():
        a.gradient((150, 172, 200), (226, 228, 222), 0, 0.68, 14)
        for k, col in enumerate(((120, 150, 80), (170, 150, 96), (104, 136, 70), (186, 168, 110))):
            y0 = 0.68 + k * 0.08
            a.poly([(0, y0), (1, y0 - 0.02), (1, y0 + 0.08), (0, y0 + 0.1)], fill=col, outline=None)
        for i in range(14):
            a.circle(0.02 + i * 0.075, 0.66, 0.06, fill=(56, 92, 60), outline=None)
    for x in (0.12, 0.2):
        a.rect(x - 0.012, 0.5, x + 0.012, 0.8, fill=WHITE, outline=INK, width=0.8)
        for k in range(3):
            a.rect(x - 0.012, 0.52 + k * 0.1, x + 0.012, 0.57 + k * 0.1, fill=RED, outline=None)
    flagpole(a, 0.07, 0.08, 0.5)
    a.rect(0.07, 0.08, 0.2, 0.18, fill=WHITE, outline=INK, width=1)
    a.rect(0.07, 0.18, 0.2, 0.28, fill=(212, 33, 61), outline=INK, width=1)
    a.line([(0.98, 0.18), (0.82, 0.26), (0.64, 0.33)], (250, 250, 250), 3)
    a.poly([(0.38, 0.38), (0.64, 0.3), (0.65, 0.36), (0.39, 0.44)], fill=(70, 76, 86), outline=INK, width=1)
    a.poly([(0.34, 0.42), (0.38, 0.38), (0.39, 0.44)], fill=CRIMSON, outline=INK, width=1)
    a.poly([(0.5, 0.36), (0.55, 0.24), (0.57, 0.34)], fill=(70, 76, 86), outline=INK, width=1)
    a.poly([(0.6, 0.31), (0.66, 0.24), (0.66, 0.33)], fill=(70, 76, 86), outline=INK, width=1)
    a.arc(0.86, 0.46, 0.12, 180, 360, INK, 2)
    a.line([(0.86, 0.46), (0.86, 0.6)], INK, 2)
    for r in (0.18, 0.26):
        a.arc(0.86, 0.38, r, 210, 330, CRIMSON, 1.2)
    a.finish("POLAND: MISSILE")


def disc_pts(a: Art, cx, cy, r, t0, t1, n=48):
    out = []
    for i in range(n + 1):
        t = math.radians(t0 + (t1 - t0) * i / n)
        out.append((cx + r * math.cos(t) * a.H / a.W, cy - r * math.sin(t)))
    return out


NV_GREEN = (118, 185, 0)


def art_nvidia():
    a = Art("art_04.png", GRID, (20, 28, 44), GRID_BAND)
    with a.background():
        a.rect(0, 0, 1, 1, fill=(20, 28, 44), outline=None)
        for k in range(1, 5):
            a.line([(0.36, 0.14 + k * 0.17), (0.7, 0.14 + k * 0.17)], (38, 50, 72), 1)
    x0, y0, x1, y1 = 0.07, 0.3, 0.29, 0.86
    for k in range(5):
        t = 0.36 + k * 0.11
        a.line([(x0 - 0.035, t), (x0, t)], (190, 198, 210), 1.6)
        a.line([(x1, t), (x1 + 0.035, t)], (190, 198, 210), 1.6)
        u = x0 + 0.03 + k * 0.04
        a.line([(u, y0 - 0.09), (u, y0)], (190, 198, 210), 1.6)
        a.line([(u, y1), (u, y1 + 0.09)], (190, 198, 210), 1.6)
    a.rrect(x0, y0, x1, y1, r=3, fill=(48, 56, 70), outline=(190, 198, 210), width=1.2)
    a.rrect(x0 + 0.05, y0 + 0.14, x1 - 0.05, y1 - 0.14, r=2, fill=NV_GREEN, outline=None)
    pts = [(0.36, 0.2), (0.42, 0.17), (0.47, 0.28), (0.52, 0.25), (0.57, 0.4), (0.61, 0.36), (0.66, 0.5)]
    a.line(pts, (236, 52, 52), 2.6)
    a.poly([(0.69, 0.58), (0.62, 0.5), (0.68, 0.44)], fill=(236, 52, 52), outline=None)
    a.poly([(0.74, 0.16), (0.9, 0.16), (0.95, 0.26), (0.95, 0.56), (0.74, 0.56)], fill=WHITE, outline=INK, width=1.1)
    a.poly([(0.9, 0.16), (0.9, 0.26), (0.95, 0.26)], fill=(210, 214, 222), outline=INK, width=0.8)
    for k in range(3):
        a.line([(0.77, 0.3 + k * 0.07), (0.88 - 0.03 * (k % 2), 0.3 + k * 0.07)], GREY, 1)
    a.circle(0.8, 0.49, 0.045, fill=(27, 42, 65), outline=None)
    a.circle(0.885, 0.43, 0.09, fill=None, outline=GOLD, width=1.8)
    a.line([(0.905, 0.5), (0.94, 0.57)], GOLD, 2.2)
    a.finish("NVIDIA: SEC PROBE")


def art_hormuz():
    a = Art("art_08.png", GRID, (18, 78, 88), GRID_BAND)
    with a.background():
        a.gradient((96, 118, 138), (214, 170, 128), 0, 0.42)
        a.poly([(0.5, 0.42), (0.6, 0.3), (0.68, 0.34), (0.76, 0.24), (0.86, 0.31), (0.94, 0.27),
                (1, 0.3), (1, 0.44), (0.5, 0.44)], fill=(150, 116, 86), outline=None)
        a.rect(0, 0.42, 1, 1, fill=(18, 78, 88), outline=None)
        for k in range(4):
            y = 0.56 + k * 0.1
            a.line([(0.62 + 0.05 * (k % 2), y), (0.8 + 0.05 * (k % 2), y)], (52, 116, 124), 1)
    for cx, cy, r, g in ((0.39, 0.34, 0.1, 96), (0.46, 0.26, 0.11, 112), (0.54, 0.22, 0.09, 128)):
        a.circle(cx, cy, r, fill=(g, g, g + 6), outline=None)
    a.poly([(0.27, 0.52), (0.3, 0.36), (0.33, 0.44), (0.36, 0.26), (0.39, 0.42), (0.42, 0.34),
            (0.44, 0.52)], fill=ORANGE, outline=None)
    a.poly([(0.31, 0.52), (0.34, 0.42), (0.36, 0.36), (0.38, 0.44), (0.4, 0.52)], fill=GOLD, outline=None)
    a.poly([(0.04, 0.52), (0.54, 0.52), (0.505, 0.7), (0.07, 0.7)], fill=(150, 34, 34), outline=INK, width=1.2)
    a.rect(0.065, 0.62, 0.515, 0.7, fill=(32, 30, 34), outline=None)
    a.line([(0.2, 0.5), (0.5, 0.5)], (210, 210, 204), 1.4)
    a.rect(0.06, 0.32, 0.16, 0.52, fill=(236, 232, 222), outline=INK, width=1)
    a.rect(0.075, 0.37, 0.145, 0.41, fill=(60, 90, 120), outline=None)
    a.rect(0.12, 0.22, 0.145, 0.32, fill=(40, 40, 44), outline=None)
    a.finish("HORMUZ: TANKER")


PK_GREEN = (1, 102, 56)
IN_SAFFRON, IN_GREEN, IN_NAVY = (255, 153, 51), (19, 136, 8), (6, 3, 141)


def art_indiapak():
    a = Art("art_09.png", GRID, (226, 236, 244), GRID_BAND)
    with a.background():
        a.gradient((198, 220, 238), (242, 238, 226), 0, 0.78)
        a.rect(0, 0.78, 1, 1, fill=(222, 210, 184), outline=None)
    flagpole(a, 0.04, 0.16, 0.96)
    a.rect(0.04, 0.18, 0.09, 0.5, fill=WHITE, outline=None)
    a.rect(0.09, 0.18, 0.29, 0.5, fill=PK_GREEN, outline=None)
    a.circle(0.19, 0.34, 0.1, fill=WHITE, outline=None)
    a.circle(0.205, 0.32, 0.085, fill=PK_GREEN, outline=None)
    a.star(0.225, 0.3, 0.04, fill=WHITE)
    a.rect(0.04, 0.18, 0.29, 0.5, fill=None, outline=INK, width=0.8)
    flagpole(a, 0.66, 0.16, 0.6)
    a.rect(0.62, 0.58, 0.7, 0.62, fill=(120, 110, 96), outline=None)
    for k, col in enumerate((IN_SAFFRON, WHITE, IN_GREEN)):
        a.rect(0.66, 0.18 + k * 0.107, 0.92, 0.287 + k * 0.107, fill=col, outline=None)
    a.circle(0.79, 0.34, 0.045, fill=None, outline=IN_NAVY, width=1)
    a.circle(0.79, 0.34, 0.012, fill=IN_NAVY, outline=None)
    a.rect(0.66, 0.18, 0.92, 0.5, fill=None, outline=INK, width=0.8)
    a.rect(0.33, 0.52, 0.37, 0.96, fill=(176, 66, 52), outline=INK, width=0.8)
    a.rect(0.5, 0.52, 0.54, 0.96, fill=(176, 66, 52), outline=INK, width=0.8)
    a.line(disc_pts(a, 0.435, 0.58, 0.3, 0, 180, 32), (176, 66, 52), 3)
    a.rect(0.37, 0.5, 0.5, 0.57, fill=(27, 42, 65), outline=None)
    for i in range(9):
        t = (i + 0.5) / 9
        x = 0.31 + (0.63 - 0.31) * t
        y = 0.24 - 0.09 * math.sin(math.pi * t)
        a.circle(x, y, 0.025, fill=GOLD, outline=None)
    a.finish("INDIA–PAKISTAN")


TEAL = (23, 128, 120)


def art_cancer():
    a = Art("art_11.png", GRID, (230, 244, 241), GRID_BAND)
    with a.background():
        a.rect(0, 0, 1, 1, fill=(230, 244, 241), outline=None)
        for k in range(1, 4):
            a.line([(0.48, 0.58 - k * 0.14), (0.97, 0.58 - k * 0.14)], (204, 226, 222), 1)
    cx, cy, L, R = 0.21, 0.56, 0.13, 0.16
    ang = math.radians(-28)
    deg = math.degrees(ang)
    ux, uy = math.cos(ang) * a.H / a.W, -math.sin(ang)

    def cap(sign, col):
        ex, ey = cx + sign * L * ux, cy + sign * L * uy
        t0 = deg + 90 if sign > 0 else deg - 90
        arc = disc_pts(a, ex, ey, R, t0, t0 - 180, 24)
        mid = disc_pts(a, cx, cy, R, t0 - 180, t0, 1)
        a.poly([mid[1]] + arc + [mid[0]], fill=col, outline=INK, width=1.1)

    cap(-1, WHITE)
    cap(1, TEAL)
    for dx, dy in ((0.05, 0.08), (0.02, 0.14), (0.31, 0.22), (0.36, 0.3)):
        a.circle(dx, dy + 0.12, 0.02, fill=(120, 190, 180), outline=None)
    base = 0.58
    for i, h in enumerate((0.12, 0.18, 0.24, 0.44)):
        x = 0.52 + i * 0.11
        col = (34, 160, 90) if i == 3 else (150, 176, 172)
        a.rect(x, base - h, x + 0.07, base, fill=col, outline=None)
    a.line([(0.55, 0.36), (0.66, 0.3), (0.77, 0.24), (0.88, 0.06)], (34, 160, 90), 1.8)
    a.poly([(0.915, 0.0), (0.85, 0.05), (0.905, 0.1)], fill=(34, 160, 90), outline=None)
    a.line([(0.48, base), (0.98, base)], INK, 1.4)
    a.finish("CANCER: 60.7%")


AR_BLUE = (116, 172, 223)


def art_argentina():
    a = Art("art_12.png", GRID, AR_BLUE, GRID_BAND)
    with a.background():
        a.rect(0, 0, 1, 0.34, fill=AR_BLUE, outline=None)
        a.rect(0, 0.34, 1, 0.67, fill=WHITE, outline=None)
        a.rect(0, 0.67, 1, 1, fill=AR_BLUE, outline=None)
    a.star(0.74, 0.46, 0.1, fill=(246, 180, 14), points=16, inner=0.62)
    a.circle(0.74, 0.46, 0.055, fill=(252, 196, 30), outline=(176, 110, 20), width=0.8)
    cx, cy, R = 0.26, 0.9, 0.6
    a.poly(disc_pts(a, cx, cy, R, 0, 180), fill=(26, 34, 50), outline=INK, width=1.2)
    for t0, t1, col in ((180, 120, (60, 170, 90)), (120, 70, (240, 180, 40)), (70, 0, (226, 40, 40))):
        a.line(disc_pts(a, cx, cy, R - 0.1, t0, t1, 20), col, 3.4)
    t = math.radians(70)
    a.line([(cx + (R - 0.2) * math.cos(t) * a.H / a.W, cy - (R - 0.2) * math.sin(t)),
            (cx + (R - 0.01) * math.cos(t) * a.H / a.W, cy - (R - 0.01) * math.sin(t))], WHITE, 1.6)
    t = math.radians(34)
    a.line([(cx, cy), (cx + (R - 0.12) * math.cos(t) * a.H / a.W, cy - (R - 0.12) * math.sin(t))], (255, 70, 60), 2.4)
    a.circle(cx, cy, 0.07, fill=(255, 70, 60), outline=WHITE, width=1)
    a.finish("ARGENTINA: 1,070")


def art_kenya():
    a = Art("art_10.png", GRID, (240, 170, 90), GRID_BAND)
    with a.background():
        a.gradient((236, 140, 70), (250, 214, 140), 0, 0.6, 12)
        a.circle(0.8, 0.42, 0.18, fill=(255, 236, 170), outline=None)
        a.rect(0, 0.6, 1, 1, fill=(176, 130, 76), outline=None)
        a.line([(0.5, 0.78), (1, 0.74)], (160, 116, 66), 1)
        a.line([(0.5, 0.9), (1, 0.88)], (160, 116, 66), 1)
    a.line([(0.8, 0.6), (0.81, 0.36)], (60, 40, 30), 2.2)
    a.poly([(0.68, 0.36), (0.74, 0.25), (0.88, 0.24), (0.95, 0.35)], fill=(50, 60, 34), outline=None)
    base_l, base_r, top = 0.2, 0.42, 0.1
    crown_l, crown_r = 0.295, 0.325
    a.line([(base_l, 0.84), (crown_l, top)], INK, 2)
    a.line([(base_r, 0.84), (crown_r, top)], INK, 2)
    for k in range(7):
        y = 0.84 - k * 0.12
        t = (0.84 - y) / (0.84 - top)
        xl, xr = base_l + (crown_l - base_l) * t, base_r + (crown_r - base_r) * t
        y2 = y - 0.12
        t2 = (0.84 - y2) / (0.84 - top)
        xl2, xr2 = base_l + (crown_l - base_l) * t2, base_r + (crown_r - base_r) * t2
        a.line([(xl, y), (xr, y)], INK, 1)
        if y2 > top:
            a.line([(xl, y), (xr2, y2)], INK, 0.9)
            a.line([(xr, y), (xl2, y2)], INK, 0.9)
    a.rect(0.15, 0.8, 0.45, 0.88, fill=(70, 70, 76), outline=INK, width=1)
    flagpole(a, 0.05, 0.1, 0.86)
    heights = (0.07, 0.015, 0.07, 0.015, 0.07)
    for k, col in enumerate((INK, WHITE, (187, 0, 0), WHITE, (0, 102, 0))):
        y0 = 0.1 + sum(heights[:k])
        a.rect(0.05, y0, 0.17, y0 + heights[k], fill=col, outline=None)
    a.rect(0.05, 0.1, 0.17, 0.34, fill=None, outline=INK, width=0.8)
    a.finish("KENYA: OIL")


def art_phillips():
    a = Art("art_13.png", GRID, (70, 140, 80), GRID_BAND)
    with a.background():
        a.gradient((150, 196, 230), (210, 230, 240), 0, 0.36, 8)
        a.rect(0, 0.26, 1, 0.42, fill=(70, 80, 96), outline=None)
        for k in range(10):
            a.circle(0.05 + k * 0.1, 0.32, 0.04, fill=(170, 178, 192), outline=None)
        for k in range(6):
            col = (70, 150, 80) if k % 2 else (84, 164, 92)
            a.rect(0, 0.42 + k * 0.1, 1, 0.52 + k * 0.1, fill=col, outline=None)
    a.poly([(0.25, 0.5), (0.39, 0.5), (0.49, 1), (0.17, 1)], fill=(216, 196, 140), outline=None)
    for x in (0.29, 0.32, 0.35):
        a.rect(x, 0.42, x + 0.012, 0.56, fill=WHITE, outline=INK, width=0.6)
    bx = 0.47
    a.circle(bx, 0.42, 0.06, fill=(20, 20, 24), outline=None)
    a.rrect(bx - 0.035, 0.48, bx + 0.035, 0.76, r=3, fill=(20, 20, 24), outline=None)
    a.line([(bx - 0.02, 0.76), (bx - 0.04, 0.96)], (20, 20, 24), 3)
    a.line([(bx + 0.02, 0.76), (bx + 0.04, 0.96)], (20, 20, 24), 3)
    a.line([(bx + 0.03, 0.52), (bx + 0.09, 0.32)], (20, 20, 24), 2.4)
    a.line([(bx + 0.09, 0.32), (bx + 0.13, 0.02)], (226, 200, 150), 3.4)
    a.line([(bx - 0.03, 0.52), (bx - 0.08, 0.36)], (20, 20, 24), 2.4)
    a.circle(bx - 0.08, 0.34, 0.03, fill=(232, 196, 160), outline=None)
    a.rect(0.78, 0.04, 0.98, 0.24, fill=INK, outline=(230, 230, 230), width=1)
    for k in range(3):
        a.rect(0.8 + k * 0.06, 0.08, 0.84 + k * 0.06, 0.2, fill=(250, 214, 80), outline=None)
    a.circle(0.11, 0.72, 0.03, fill=(220, 30, 40), outline=WHITE, width=0.6)
    a.finish("PHILLIPS: 118")


ART_FUNCS = [art_kyiv, art_akvan, art_chips, art_nvidia, art_euuk, art_cop31, art_poland,
             art_hormuz, art_indiapak, art_kenya, art_cancer, art_argentina, art_phillips]


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
        badge = [lb for lb in labels if lb["kind"] == "badge"]
        lead = labels[0]["lead"]
        lo, hi = (16, 18) if lead else (13, 14)
        if len(badge) != 1 or not lo <= badge[0]["size"] <= hi:
            bad.append((name, "badge size", [b["size"] for b in badge]))
        if lead and len([lb for lb in labels if lb["kind"] == "callout"]) != 1:
            bad.append((name, "lead needs one callout"))
        if any(lb["kind"] == "attr" for lb in labels):
            bad.append((name, "no source pill inside picture"))
    if bad:
        raise SystemExit("art label failure:\n  " + "\n  ".join(map(str, bad)))
    kinds = sorted({lb["kind"] for lb in LABELS})
    print(f"art: {len(ART_FUNCS)} illustrations, {len(LABELS)} labels ({', '.join(kinds)}), "
          f"padding and overlap ok; no in-picture source pills")


if __name__ == "__main__":
    build_all()

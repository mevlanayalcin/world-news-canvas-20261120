"""Editorial illustrations for the Friday 20 November 2026 front page (v8).

Each picture has two layers:

* a scene, drawn from scratch with Pillow at twice its printed size and
  reduced with Lanczos (supersampled edges). The scene fills the whole box.
  Scene coordinates are fractions of the area below a thin top band, so X(0.5)
  is the horizontal middle; any fill that touches y = 0 is carried up to the
  top edge, so sky, sea and land run under the floating badge;
* a typographic layer drawn at printed size after the reduction, so FreeType
  renders it at its final pixel size: a solid crimson corner badge (top
  left, no outline), (leads only) a 14 px white callout pill stacked 3 px
  under it, a small attribution tag at the bottom and, on lead 3, a
  four-market closing scoreboard.

Lead art is 316x132 (17 px badge, 14 px callout); card art is 188x78 (14 px badge).
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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

# badge colours
B_CRIMSON = (184, 41, 47)   # #b8292f

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"
LATO_HEAVY = FONT_DIR / "lato" / "Lato-Heavy.ttf"

HERO = (316, 132)
GRID = (188, 78)
HERO_BAND, HERO_BADGE = 28, 17   # top band height, badge type size (printed px)
GRID_BAND, GRID_BADGE = 20, 14

LABELS: list[dict] = []


def font(path: Path, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), round(size))


class Art:
    """A 2x surface addressed in fractions of the scene below the top band."""

    def __init__(self, name: str, size: tuple[int, int], bg, band: int):
        self.name = name
        self.size = size
        self.lead = size[0] > 200
        self.W = size[0] * 2
        self.oy = band * 2
        self.H = size[1] * 2 - self.oy
        self.im = Image.new("RGB", (self.W, size[1] * 2), bg)
        self.d = ImageDraw.Draw(self.im)
        self.u = self.W / 632  # 1 printed px at lead width

    def X(self, f: float) -> float:
        return f * self.W

    def Y(self, f: float) -> float:
        # anything drawn from the scene's top edge continues under the band
        return 0.0 if f <= 0 else self.oy + f * self.H

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
        """r is a fraction of the scene height so circles stay round."""
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

    def gradient(self, top, bottom, y0=0.0, y1=1.0, steps=24):
        steps = max(steps, 128)  # smooth bands: no visible steps, fewer JPEG edges
        for i in range(steps):
            t = i / (steps - 1)
            col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
            ya = y0 + (y1 - y0) * i / steps
            self.rect(0, ya, 1, ya + (y1 - y0) / steps + 0.002, fill=col, outline=None)

    def _light(self, mask: Image.Image, color, blur: float):
        mask = mask.filter(ImageFilter.GaussianBlur(max(1.0, blur)))
        self.im.paste(Image.new("RGB", self.im.size, color), (0, 0), mask)
        self.d = ImageDraw.Draw(self.im)

    def glow(self, cx, cy, rx, ry, color, alpha=255, blur=0.5):
        """Soft light: a blurred ellipse (radii in scene-height fractions) blended in."""
        x, y, ax, ay = self.X(cx), self.Y(cy), rx * self.H, ry * self.H
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).ellipse([x - ax, y - ay, x + ax, y + ay], fill=alpha)
        self._light(mask, color, min(ax, ay) * blur)

    def glow_line(self, pts, color, width, alpha=255, blur=3.0):
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).line(self.P(pts), fill=alpha, width=self.lw(width), joint="curve")
        self._light(mask, color, blur * self.u * 2)

    def tint_poly(self, pts, color, alpha):
        """A translucent fill, so whatever is behind still shows through."""
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).polygon(self.P(pts), fill=alpha)
        self.im.paste(Image.new("RGB", self.im.size, color), (0, 0), mask)
        self.d = ImageDraw.Draw(self.im)

    # ---- printed-size typography ------------------------------------------
    def finish(self, badge: str, callout: str | None = None, attr: str | None = None,
               overlay=None):
        out = self.im.resize(self.size, Image.LANCZOS)
        out = ImageEnhance.Contrast(out).enhance(1.06)   # crisper focal shapes at 300 px
        d = ImageDraw.Draw(out)
        w, h = self.size
        if self.lead:
            pad, top, size = 6, 4, HERO_BADGE
        else:
            pad, top, size = 4, 3, GRID_BADGE
        # every badge is solid editorial crimson with white type and no outline
        _, _, _, by1 = self._pill(d, badge, pad, top, size, WHITE, B_CRIMSON, LATO_BLACK,
                                  "tl", "badge")
        if callout:
            self._pill(d, callout, pad, by1 + 3, 14, INK, WHITE, LATO_HEAVY, "tl", "callout")
        if overlay:
            overlay(self, d)
        if attr:
            if self.lead:
                self._pill(d, attr, pad, h - 5, 10.5, WHITE, INK, LATO_BLACK, "bl", "attr")
            else:
                self._pill(d, attr, w - 4, h - 4, 10, WHITE, INK, LATO_BOLD, "br", "attr")
        ASSETS.mkdir(exist_ok=True)
        out.save(ASSETS / self.name, format="PNG", optimize=True)

    def _pill(self, d, s, x, y, size, fg, bg, path, anchor, kind, outline=None):
        f = font(path, size)
        bb = d.textbbox((0, 0), s, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        px, py = round(size * 0.45), round(size * 0.28)
        bw, bht = tw + 2 * px, th + 2 * py
        x0 = x if anchor in ("tl", "bl") else x - bw
        y0 = y if anchor in ("tl", "tr") else y - bht
        if bg is not None or outline is not None:   # bg=None: bare type, no box
            d.rounded_rectangle([x0, y0, x0 + bw, y0 + bht], radius=3, fill=bg,
                                outline=outline, width=1)
        d.text((x0 + px - bb[0], y0 + py - bb[1]), s, font=f, fill=fg)
        LABELS.append(dict(art=self.name, kind=kind, text=s, bbox=(x0, y0, x0 + bw, y0 + bht),
                           size=round(size), img=self.size, lead=self.lead))
        return x0, y0, x0 + bw, y0 + bht


# ---- shared props ----------------------------------------------------------
def person(a: Art, x, y, h, fill=INK, arms_up=False):
    """A standing figure; y is the feet line, h its height (fractions)."""
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


# ---- printed-size map and scene labels (leads 1 and 2) ---------------------
def kyiv_labels(a: Art, d: ImageDraw.ImageDraw):
    """The barrage size, in quiet cream type on the night sky at top right."""
    a._pill(d, "~110 missiles · 400 drones", a.size[0] - 4, 4, 10.5, (240, 230, 212), None,
            LATO_BLACK, "tr", "geo")


AKVAN_EYE_Y = 0.52


def coast_x(yf: float) -> float:
    """Odisha coastline (fraction of width) at scene height yf: land west, sea east."""
    return 0.64 - 0.46 * yf + 0.015 * math.sin(yf * 14)


def akvan_labels(a: Art, d: ImageDraw.ImageDraw):
    """Name the landfall point (on the land side) and the sea."""
    dx, dy = a.X(coast_x(AKVAN_EYE_Y)) / 2, a.Y(AKVAN_EYE_Y) / 2   # landfall at printed size
    a._pill(d, "Gopalpur", round(dx - 9), round(dy - 7), 10.5, INK, PAPER, LATO_BLACK, "tr", "geo")
    a._pill(d, "BAY OF BENGAL", a.size[0] - 4, 4, 10, WHITE, (10, 26, 48), LATO_BLACK, "tr", "geo")


# ---- 1. Kyiv bridges -------------------------------------------------------
KYIV_SIL = (12, 12, 28)


def onion(a: Art, x, yb, s, fill=(226, 168, 52)):
    """An onion dome on a short drum; yb is the drum foot, s the dome height (H fractions)."""
    hw = s * 0.42 * a.H / a.W
    a.rect(x - hw * 0.7, yb - s * 0.45, x + hw * 0.7, yb, fill=KYIV_SIL, outline=None)
    base = yb - s * 0.45
    left, right = [], []
    for k in range(25):
        t = k / 24
        w = hw * (0.62 + 0.45 * math.sin(math.pi * t / 0.7)) if t < 0.7 else hw * 0.62 * (1 - t) / 0.3
        y = base - s * t
        left.append((x - w, y))
        right.append((x + w, y))
    a.poly(left + right[::-1], fill=fill, outline=KYIV_SIL, width=1)
    a.line([(x, base - s), (x, base - s * 1.35)], KYIV_SIL, 1.3)
    a.line([(x - hw * 0.35, base - s * 1.2), (x + hw * 0.35, base - s * 1.2)], KYIV_SIL, 1.3)


def arch_bridge(a: Art, y, th, ah, n, col, rib, gap=None):
    """A deck over n arches springing from piers at the water line y + th + ah."""
    yw = y + th + ah
    span = 1.08 / n
    for i in range(n):
        sx0 = -0.04 + i * span
        sx1 = sx0 + span
        xc, hs = (sx0 + sx1) / 2, span * 0.46
        box = [a.X(xc - hs), a.Y(y + th), a.X(xc + hs), a.Y(yw + ah)]
        a.d.arc(box, 180, 360, fill=col, width=a.lw(rib))
        for k in range(1, 6):
            xk = xc - hs + 2 * hs * k / 6
            yk = yw - ah * math.sqrt(max(0.0, 1 - ((xk - xc) / hs) ** 2))
            a.line([(xk, y + th), (xk, yk)], col, rib * 0.4)
        a.rect(sx0 - 0.007, yw - 0.02, sx0 + 0.007, yw + 0.02, fill=col, outline=KYIV_SIL, width=0.6)
    parts = [(0, 1)] if gap is None else [(0, gap[0]), (gap[1], 1)]
    for x0, x1 in parts:
        a.rect(x0, y, x1, y + th, fill=col, outline=KYIV_SIL, width=0.8)
        a.line([(x0, y), (x1, y)], (255, 186, 112), 1.0)        # lit top edge
    if gap:   # sagging broken ends and debris in the water
        a.poly([(gap[0], y), (gap[0] + 0.02, y + th + 0.05), (gap[0], y + th)], fill=col,
               outline=KYIV_SIL, width=0.8)
        a.poly([(gap[1], y), (gap[1] - 0.02, y + th + 0.06), (gap[1], y + th)], fill=col,
               outline=KYIV_SIL, width=0.8)


def burst(a: Art, x, y, s, yw):
    """A glowing impact on a deck at (x, y), with its reflection in the river at yw."""
    a.glow(x, yw + 0.06 * s, 0.1 * s, 0.26 * s, (255, 120, 50), 130)
    a.glow(x, y, 0.34 * s, 0.34 * s, (200, 26, 30), 190)
    a.glow(x, y, 0.18 * s, 0.18 * s, (255, 120, 40), 235)
    for i in range(12):
        t = i * math.pi / 6 + 0.13
        L = (0.2 if i % 2 else 0.13) * s
        a.line([(x, y), (x + L * math.cos(t) * a.H / a.W, y + L * math.sin(t))], (255, 196, 96), 2.2 * s)
    a.glow(x, y, 0.08 * s, 0.08 * s, (255, 236, 180), 255, blur=0.35)
    a.circle(x, y, 0.035 * s, fill=(255, 252, 236), outline=None)


def art_kyiv():
    a = Art("art_01.png", HERO, (14, 18, 46), HERO_BAND)
    # twilight: indigo overhead, plum, then a crimson-amber horizon
    a.gradient((12, 16, 44), (88, 38, 80), 0, 0.3)
    a.gradient((88, 38, 80), (236, 124, 62), 0.3, 0.5)
    a.glow(0.55, 0.5, 1.6, 0.1, (255, 172, 96), 140)
    # the Dnipro reflects the sky and darkens toward the viewer
    a.gradient((128, 58, 72), (10, 12, 32), 0.5, 1.0)
    # far-bank skyline with the gilded domes (left) and the Lavra bell tower (right)
    a.poly([(0, 0.5), (0, 0.44), (0.05, 0.44), (0.05, 0.41), (0.1, 0.41), (0.11, 0.45), (0.22, 0.45),
            (0.23, 0.4), (0.28, 0.4), (0.29, 0.44), (0.36, 0.43), (0.38, 0.39), (0.45, 0.39),
            (0.46, 0.44), (0.55, 0.45), (0.57, 0.41), (0.64, 0.41), (0.66, 0.45), (0.76, 0.44),
            (0.78, 0.4), (0.84, 0.4), (0.85, 0.43), (0.96, 0.43), (0.97, 0.4), (1, 0.4), (1, 0.5)],
           fill=KYIV_SIL, outline=None)
    a.rect(0.07, 0.36, 0.21, 0.45, fill=KYIV_SIL, outline=None)
    onion(a, 0.1, 0.37, 0.07)
    onion(a, 0.14, 0.37, 0.11)
    onion(a, 0.18, 0.37, 0.07)
    a.rect(0.885, 0.18, 0.925, 0.42, fill=KYIV_SIL, outline=None)
    a.rect(0.893, 0.1, 0.917, 0.18, fill=KYIV_SIL, outline=None)
    onion(a, 0.905, 0.1, 0.08)
    for k in range(3):                                # lit belfry windows
        a.rect(0.898, 0.22 + k * 0.06, 0.912, 0.255 + k * 0.06, fill=(255, 196, 110), outline=None)
    # missile streaks into the three crossings
    for (x0, y0), (x1, y1) in (((0.8, 0.03), (0.7, 0.5)), ((0.44, 0.03), (0.3, 0.6)),
                               ((0.64, 0.03), (0.56, 0.76))):
        a.glow_line([(x0, y0), (x1, y1)], (255, 160, 90), 5, 110)
        a.line([(x0, y0), (x1, y1)], (255, 232, 200), 1.3)
    # three arched bridges in depth: far, middle and near (broken)
    arch_bridge(a, 0.5, 0.022, 0.05, 7, (150, 122, 146), 1.6)
    arch_bridge(a, 0.6, 0.034, 0.08, 5, (184, 164, 184), 2.4)
    arch_bridge(a, 0.75, 0.05, 0.1, 3, (222, 212, 222), 3.4, gap=(0.52, 0.6))
    # river ripples catching the fire
    for k, (x, y, L) in enumerate(((0.06, 0.95, 0.1), (0.2, 0.9, 0.07), (0.8, 0.93, 0.1),
                                   (0.9, 0.98, 0.07), (0.38, 0.97, 0.06), (0.7, 0.99, 0.05))):
        a.line([(x, y), (x + L, y)], (200, 104, 76) if k % 2 else (150, 80, 90), 1.1)
    burst(a, 0.7, 0.5, 0.62, 0.57)
    burst(a, 0.3, 0.6, 0.8, 0.72)
    burst(a, 0.56, 0.76, 1.0, 0.92)
    a.finish("KYIV", "3 bridges hit", overlay=kyiv_labels)


# ---- 2. Cyclone Akvan ------------------------------------------------------
def art_akvan():
    import numpy as np
    a = Art("art_02.png", HERO, (10, 26, 48), HERO_BAND)
    W2, H2 = a.im.size
    py, px = np.mgrid[0:H2, 0:W2].astype(np.float64)
    yf = (py - a.oy) / a.H
    land = px < (0.64 - 0.46 * yf + 0.015 * np.sin(yf * 14)) * W2
    img = np.zeros((H2, W2, 3))
    img[:] = (10, 26, 48)
    img[land] = (60, 74, 54)
    # radar reflectivity: an eyewall ring plus two spiral bands around the eye
    ex, ey = a.X(coast_x(AKVAN_EYE_Y)), a.Y(AKVAN_EYE_Y)
    dx, dy = px - ex, py - ey
    r = np.hypot(dx, dy) / 2                       # printed px
    th = np.arctan2(dy, dx)
    phase = th + 1.7 * np.log(np.maximum(r, 1) / 14)
    arms = (0.5 + 0.5 * np.cos(2 * phase)) ** 1.6
    ring = np.exp(-((r - 15) / 5.5) ** 2)
    outer = np.exp(-r / 70) * np.clip((r - 10) / 8, 0, 1)
    inten = np.maximum(ring, 1.05 * outer * arms) * np.clip((r - 7) / 3, 0, 1)
    for lo, col in ((0.16, (40, 150, 80)), (0.34, (238, 206, 56)), (0.55, (248, 132, 34)),
                    (0.76, (226, 40, 40))):
        m = inten > lo
        img[m] = img[m] * 0.1 + np.array(col) * 0.9
    a.im = Image.fromarray(img.astype(np.uint8), "RGB")
    a.d = ImageDraw.Draw(a.im)
    # coast, range rings and eye
    a.line([(coast_x(t / 40), t / 40) for t in range(-6, 41)] , (240, 230, 196), 1.6)
    ecx, ecy = coast_x(AKVAN_EYE_Y), AKVAN_EYE_Y
    for rr in (0.5, 0.9):
        a.circle(ecx, ecy, rr, fill=None, outline=(70, 110, 150), width=0.8)
    a.circle(ecx, ecy, 0.05, fill=(10, 26, 48), outline=WHITE, width=1.6)
    # track from the south-east into the coast, as a bold gold arrow
    track = [(1.0, 1.02), (0.86, 0.86), (0.7, 0.7)]
    tip = (ecx + 0.075, ecy + 0.05)
    ang = math.atan2((tip[1] - track[-1][1]) * a.H, (tip[0] - track[-1][0]) * a.W)

    def off(p, d, s):
        # d scene-height fractions back along the track, s radians off its axis
        return (p[0] + d * math.cos(ang + s) * a.H / a.W, p[1] + d * math.sin(ang + s))
    track.append(off(tip, -0.16, 0))
    a.line(track, INK, 6.4)
    a.line(track, GOLD, 3.8)
    a.poly([tip, off(tip, -0.21, 0.5), off(tip, -0.21, -0.5)], fill=GOLD, outline=INK, width=1.4)
    for p in track[1:3]:
        a.circle(p[0], p[1], 0.028, fill=WHITE, outline=INK, width=1)
    a.circle(ecx, ecy, 0.022, fill=CRIMSON, outline=WHITE, width=1.2)
    # wind-bent palms on the shore
    PALM = (8, 12, 10)
    for x, h, lean in ((0.1, 0.38, 0.02), (0.17, 0.27, 0.016)):
        top = (x - lean, 1.0 - h)
        a.line([(x, 1.02), (x - lean * 0.2, 1.0 - h * 0.5), (x - lean * 0.6, 1.0 - h * 0.85), top], PALM, 3.0)
        # fronds streaming west with the wind: (dx in W fractions, dy, droop)
        for fx, fy, droop in ((-0.05, -0.02, 0.07), (-0.04, -0.08, 0.04), (-0.035, 0.06, 0.05),
                              (0.03, -0.06, 0.05), (0.025, 0.04, 0.04)):
            mid = (top[0] + fx * 0.55, top[1] + fy * 0.55 - 0.02)
            end = (top[0] + fx, top[1] + fy + droop)
            a.line([top, mid, end], PALM, 2.4)
    a.finish("CYCLONE AKVAN", "Landfall · 8 am", overlay=akvan_labels)


# ---- 3. Asia AI sell-off ---------------------------------------------------
CORAL = (255, 107, 107)  # #ff6b6b
SCOREBOARD = [("Taipei", "−6.2%"), ("Seoul", "−5.2%"), ("Tokyo", "−5.1%"), ("Sing.", "−2.1%")]


def chips_scoreboard(a: Art, d: ImageDraw.ImageDraw):
    """Four-market closing board, drawn at printed size beside the chart."""
    x0, y0, x1, y1 = 203, 6, 310, 126
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=(26, 34, 54), outline=(96, 112, 144), width=1)
    head = font(LATO_BLACK, 10)
    d.text(((x0 + x1) / 2, y0 + 10), "INDEX CLOSE", font=head, fill=(186, 198, 220), anchor="mm")
    d.line([(x0 + 6, y0 + 19), (x1 - 6, y0 + 19)], fill=(96, 112, 144), width=1)
    city, pct = font(LATO_BOLD, 15), font(LATO_BLACK, 15)
    row_h = (y1 - y0 - 22) / len(SCOREBOARD)
    for i, (c, v) in enumerate(SCOREBOARD):
        cy = y0 + 22 + row_h * (i + 0.5)
        d.text((x0 + 7, cy), c, font=city, fill=WHITE, anchor="lm")
        d.text((x1 - 7, cy), v, font=pct, fill=CORAL, anchor="rm")
        if i:
            yy = round(y0 + 22 + row_h * i)
            d.line([(x0 + 6, yy), (x1 - 6, yy)], fill=(52, 64, 88), width=1)
    LABELS.append(dict(art=a.name, kind="board", text="scoreboard", bbox=(x0, y0, x1, y1),
                       size=15, img=a.size, lead=a.lead))


def art_chips():
    a = Art("art_03.png", HERO, (12, 16, 28), HERO_BAND)
    a.rect(0, 0, 1, 1, fill=(12, 16, 28), outline=None)
    cx0, cx1 = 15 / 316, 195 / 316           # chart spans x = 15..195 at 1x
    for k in range(1, 6):
        a.line([(cx0, k * 0.16), (cx1, k * 0.16)], (36, 46, 66), 1)
    # a softly glowing chip behind the plunge
    ccx, ccy, hh = 0.36, 0.6, 0.3
    hw = hh * a.H / a.W
    a.glow(ccx, ccy, 0.62, 0.5, (30, 110, 180), 120)
    for k in range(7):
        t = -hh * 0.8 + k * hh * 1.6 / 6
        tx = -hw * 0.8 + k * hw * 1.6 / 6
        a.line([(ccx - hw - 0.03, ccy + t), (ccx - hw, ccy + t)], (90, 160, 220), 1.4)
        a.line([(ccx + hw, ccy + t), (ccx + hw + 0.03, ccy + t)], (90, 160, 220), 1.4)
        a.line([(ccx + tx, ccy - hh - 0.07), (ccx + tx, ccy - hh)], (90, 160, 220), 1.4)
        a.line([(ccx + tx, ccy + hh), (ccx + tx, ccy + hh + 0.07)], (90, 160, 220), 1.4)
    a.rrect(ccx - hw, ccy - hh, ccx + hw, ccy + hh, r=4, fill=(20, 36, 60), outline=(100, 170, 230), width=1.4)
    a.rrect(ccx - hw * 0.55, ccy - hh * 0.55, ccx + hw * 0.55, ccy + hh * 0.55, r=3,
            fill=(30, 54, 86), outline=(120, 186, 240), width=1.1)
    for k in range(1, 4):
        a.line([(ccx - hw * 0.55, ccy - hh * 0.55 + k * hh * 0.275),
                (ccx + hw * 0.55, ccy - hh * 0.55 + k * hh * 0.275)], (56, 92, 132), 0.8)
    # plunging index curve with a shaded fall
    curve = [(0.00, 0.30), (0.08, 0.27), (0.15, 0.36), (0.22, 0.33), (0.30, 0.48), (0.38, 0.45),
             (0.47, 0.62), (0.55, 0.58), (0.64, 0.76), (0.72, 0.72), (0.82, 0.86), (0.91, 0.84),
             (1.00, 0.95)]
    pts = [(cx0 + (cx1 - cx0) * x, y) for x, y in curve]
    a.tint_poly(pts + [(cx1, 1), (cx0, 1)], (120, 18, 34), 120)
    for i in range(1, len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        x = (xa + xb) / 2
        down = yb > ya
        col = (236, 60, 60) if down else (70, 200, 130)
        lo, hi = min(ya, yb), max(ya, yb)
        a.rect(x - 0.008, lo, x + 0.008, hi, fill=col, outline=None)
    a.glow_line(pts, (255, 40, 50), 9, 170)
    a.line(pts, (255, 84, 84), 3.0)
    a.line(pts, (255, 200, 200), 0.9)
    a.circle(pts[-1][0], pts[-1][1], 0.04, fill=CORAL, outline=WHITE, width=1.4)
    a.finish("AI SELL-OFF", callout="Asia, Friday’s close", overlay=chips_scoreboard)


# ---- 4. UK-EU reset --------------------------------------------------------
def art_euuk():
    a = Art("art_04.png", GRID, (214, 228, 240), GRID_BAND)
    a.rect(0, 0, 1, 1, fill=(214, 228, 240), outline=None)
    a.rect(0.32, 0.04, 0.68, 0.7, fill=(178, 200, 220), outline=INK, width=1.4)
    for i in range(7):
        a.line([(0.32 + i * 0.06, 0.04), (0.32 + i * 0.06, 0.7)], (140, 166, 190), 1)
    a.line([(0.06, 0.04), (0.06, 0.95)], INK, 2)
    eu_flag(a, 0.065, 0.06, 0.28, 0.46)
    a.line([(0.94, 0.04), (0.94, 0.95)], INK, 2)
    union_jack(a, 0.725, 0.06, 0.935, 0.46)
    a.rect(0, 0.8, 1, 1, fill=(196, 182, 156), outline=None)
    a.rrect(0.22, 0.72, 0.78, 0.84, r=5, fill=NAVY, outline=INK, width=1.2)
    person(a, 0.4, 0.76, 0.5, fill=(36, 44, 60))
    person(a, 0.6, 0.76, 0.5, fill=(36, 44, 60))
    a.line([(0.42, 0.52), (0.5, 0.57), (0.58, 0.52)], (36, 44, 60), 4)
    a.circle(0.5, 0.57, 0.055, fill=(232, 196, 160), outline=INK, width=1)
    a.finish("UK–EU DEAL")


# ---- 5. COP31 --------------------------------------------------------------
def art_cop31():
    a = Art("art_05.png", GRID, (244, 196, 116), GRID_BAND)
    a.rect(0, 0, 1, 0.74, fill=(246, 204, 128), outline=None)
    a.rect(0, 0.74, 1, 1, fill=(44, 132, 150), outline=None)
    a.circle(0.18, 0.44, 0.34, fill=(226, 240, 248), outline=INK, width=1.5)
    a.poly([(0.1, 0.26), (0.19, 0.2), (0.25, 0.32), (0.18, 0.42), (0.09, 0.38)], fill=GREEN, outline=None)
    a.poly([(0.16, 0.5), (0.27, 0.48), (0.24, 0.66), (0.18, 0.68)], fill=GREEN, outline=None)
    a.rrect(0.37, 0.08, 0.41, 0.62, r=4, fill=WHITE, outline=INK, width=1.2)
    a.rrect(0.378, 0.26, 0.402, 0.62, r=3, fill=RED, outline=None)
    a.circle(0.39, 0.68, 0.1, fill=RED, outline=INK, width=1.2)
    # the draft text with the fossil-fuel line struck out
    a.poly([(0.5, 0.06), (0.9, 0.06), (0.9, 0.7), (0.5, 0.7)], fill=WHITE, outline=INK, width=1.3)
    for k in range(5):
        y = 0.16 + k * 0.12
        a.line([(0.54, y), (0.86, y)], GREY if k != 2 else CRIMSON, 1.3 if k != 2 else 1.8)
    a.rect(0.53, 0.37, 0.87, 0.47, fill=(255, 226, 226), outline=None)
    a.line([(0.54, 0.42), (0.86, 0.42)], CRIMSON, 2)
    a.line([(0.6, 0.33), (0.8, 0.51)], CRIMSON, 1.6)
    a.line([(0.6, 0.51), (0.8, 0.33)], CRIMSON, 1.6)
    a.finish("COP31: NO DEAL")


# ---- 6. Missile over Poland ------------------------------------------------
def art_poland():
    a = Art("art_06.png", GRID, (190, 206, 222), GRID_BAND)
    a.gradient((150, 172, 200), (226, 228, 222), 0, 0.68, 14)
    # farmland strips
    for k, col in enumerate(((120, 150, 80), (170, 150, 96), (104, 136, 70), (186, 168, 110))):
        y0 = 0.68 + k * 0.08
        a.poly([(0, y0), (1, y0 - 0.02), (1, y0 + 0.08), (0, y0 + 0.1)], fill=col, outline=None)
    # tree line and border posts (red-white)
    for i in range(14):
        x = 0.02 + i * 0.075
        a.circle(x, 0.66, 0.06, fill=(56, 92, 60), outline=None)
    for x in (0.12, 0.2):
        a.rect(x - 0.012, 0.5, x + 0.012, 0.8, fill=WHITE, outline=INK, width=0.8)
        for k in range(3):
            a.rect(x - 0.012, 0.52 + k * 0.1, x + 0.012, 0.57 + k * 0.1, fill=RED, outline=None)
    # Polish flag
    flagpole(a, 0.07, 0.08, 0.5)
    a.rect(0.07, 0.08, 0.2, 0.18, fill=WHITE, outline=INK, width=1)
    a.rect(0.07, 0.18, 0.2, 0.28, fill=(212, 33, 61), outline=INK, width=1)
    # cruise missile heading west, large and dark against the sky, with a glowing exhaust
    a.glow_line([(0.99, 0.12), (0.84, 0.22), (0.72, 0.3)], (255, 255, 255), 5, 200)
    a.line([(0.99, 0.12), (0.84, 0.22), (0.72, 0.3)], WHITE, 2.4)
    a.glow(0.72, 0.3, 0.12, 0.09, (255, 140, 40), 230)
    MS = (34, 38, 48)
    a.poly([(0.3, 0.42), (0.7, 0.26), (0.72, 0.34), (0.32, 0.5)], fill=MS, outline=INK, width=1)
    a.poly([(0.25, 0.48), (0.3, 0.42), (0.32, 0.5)], fill=CRIMSON, outline=INK, width=1)
    a.poly([(0.47, 0.4), (0.55, 0.2), (0.58, 0.36)], fill=MS, outline=INK, width=1)
    a.poly([(0.47, 0.42), (0.52, 0.56), (0.56, 0.39)], fill=MS, outline=INK, width=1)
    a.poly([(0.64, 0.3), (0.7, 0.18), (0.7, 0.3)], fill=MS, outline=INK, width=1)
    a.line([(0.34, 0.45), (0.68, 0.31)], (120, 128, 142), 0.8)
    # radar dish
    a.arc(0.86, 0.58, 0.12, 180, 360, INK, 2)
    a.line([(0.86, 0.58), (0.86, 0.72)], INK, 2)
    for r in (0.18, 0.26):
        a.arc(0.86, 0.5, r, 210, 330, CRIMSON, 1.2)
    a.finish("POLAND: MISSILE")


# ---- 7. Iraqi army enters Jurf al-Sakher ----------------------------------
def art_iraq():
    a = Art("art_07.png", GRID, (230, 200, 150), GRID_BAND)
    a.gradient((236, 206, 150), (246, 226, 186), 0, 0.62, 12)
    a.rect(0, 0.62, 1, 1, fill=(214, 180, 124), outline=None)
    # palms
    for x in (0.08, 0.9):
        a.line([(x, 0.64), (x + 0.01, 0.2)], (110, 80, 50), 2.6)
        for ang in (-150, -110, -70, -30):
            t = math.radians(ang)
            a.line([(x + 0.01, 0.2), (x + 0.01 + 0.07 * math.cos(t), 0.2 - 0.2 * math.sin(t) * -1 + 0.0)], (60, 120, 70), 2.4)
    # compound wall and gate
    a.rect(0.3, 0.28, 0.98, 0.64, fill=(196, 168, 120), outline=INK, width=1.2)
    for k in range(9):
        a.rect(0.3 + k * 0.077, 0.24, 0.335 + k * 0.077, 0.28, fill=(196, 168, 120), outline=INK, width=0.8)
    a.rect(0.56, 0.38, 0.72, 0.64, fill=(70, 60, 50), outline=INK, width=1.2)
    # Iraqi flag on the gate (stripes, green script mark)
    flagpole(a, 0.64, 0.005, 0.26)
    a.rect(0.64, 0.02, 0.78, 0.07, fill=(206, 17, 38), outline=None)
    a.rect(0.64, 0.07, 0.78, 0.12, fill=WHITE, outline=None)
    a.rect(0.64, 0.12, 0.78, 0.17, fill=INK, outline=None)
    a.rect(0.64, 0.02, 0.78, 0.17, fill=None, outline=INK, width=0.8)
    a.line([(0.685, 0.1), (0.7, 0.09), (0.715, 0.1), (0.735, 0.09)], (0, 122, 61), 1.2)  # stylised script
    # armoured vehicle and troops moving in
    a.rrect(0.12, 0.62, 0.48, 0.84, r=4, fill=(150, 140, 96), outline=INK, width=1.2)
    a.rect(0.22, 0.52, 0.36, 0.62, fill=(130, 122, 84), outline=INK, width=1.1)
    a.line([(0.36, 0.56), (0.52, 0.53)], INK, 2)
    for x in (0.17, 0.25, 0.33, 0.41):
        a.circle(x, 0.88, 0.06, fill=INK, outline=None)
    for x in (0.54, 0.6, 0.66, 0.74):
        person(a, x, 0.94, 0.3, fill=(84, 90, 60))
    a.finish("IRAQ: ARMY IN")


# ---- 8. Italy general strike -----------------------------------------------
def art_italy():
    a = Art("art_08.png", GRID, (238, 222, 196), GRID_BAND)
    a.rect(0, 0, 1, 1, fill=(244, 226, 196), outline=None)
    a.rect(0.52, 0.06, 0.98, 0.66, fill=(222, 192, 150), outline=INK, width=1.2)
    for row in range(2):
        for k in range(7):
            x = 0.545 + k * 0.062
            y = 0.14 + row * 0.24
            a.rrect(x, y, x + 0.035, y + 0.13, r=6, fill=(150, 112, 80), outline=None)
    # Italian flag
    flagpole(a, 0.04, 0.04, 0.4)
    for k, col in enumerate(((0, 146, 70), WHITE, (206, 43, 55))):
        a.rect(0.04 + k * 0.045, 0.05, 0.085 + k * 0.045, 0.24, fill=col, outline=None)
    a.rect(0.04, 0.05, 0.175, 0.24, fill=None, outline=INK, width=0.8)
    # stopped bus
    a.rrect(0.2, 0.3, 0.5, 0.66, r=4, fill=(230, 160, 40), outline=INK, width=1.3)
    for k in range(3):
        a.rect(0.225 + k * 0.09, 0.36, 0.285 + k * 0.09, 0.48, fill=(190, 220, 236), outline=None)
    a.circle(0.27, 0.68, 0.07, fill=INK, outline=None)
    a.circle(0.44, 0.68, 0.07, fill=INK, outline=None)
    a.rect(0.24, 0.53, 0.46, 0.61, fill=CRIMSON, outline=None)
    # marchers with red flags
    a.rect(0, 0.74, 1, 1, fill=(196, 176, 150), outline=None)
    for i in range(11):
        person(a, 0.05 + i * 0.09, 0.99, 0.24 + (i % 3) * 0.03, fill=(40, 40, 50))
    for x in (0.1, 0.36, 0.62):
        a.line([(x, 0.8), (x, 0.5)], INK, 1.2)
        a.poly([(x, 0.5), (x + 0.08, 0.55), (x, 0.6)], fill=RED, outline=None)
    a.finish("ITALY: STRIKE")


# ---- 9. Japan CPI ----------------------------------------------------------
def art_japan():
    a = Art("art_09.png", GRID, (246, 238, 226), GRID_BAND)
    a.rect(0, 0, 1, 1, fill=(246, 238, 226), outline=None)
    for k in range(1, 5):
        a.line([(0.46, k * 0.2), (0.98, k * 0.2)], (220, 208, 190), 1)
    # rising sun disc
    a.circle(0.2, 0.36, 0.26, fill=(188, 0, 45), outline=None)
    # shopping basket with produce
    a.circle(0.12, 0.64, 0.09, fill=(232, 80, 50), outline=INK, width=1)
    a.circle(0.22, 0.62, 0.1, fill=(120, 170, 60), outline=INK, width=1)
    a.rrect(0.16, 0.5, 0.2, 0.62, r=2, fill=(250, 250, 244), outline=INK, width=1)
    a.circle(0.3, 0.64, 0.08, fill=(240, 190, 60), outline=INK, width=1)
    a.poly([(0.04, 0.68), (0.38, 0.68), (0.34, 0.96), (0.08, 0.96)], fill=(176, 120, 64), outline=INK, width=1.3)
    for k in range(4):
        a.line([(0.1 + k * 0.075, 0.7), (0.12 + k * 0.065, 0.94)], (130, 84, 44), 1.1)
    # rising CPI bars and arrow
    vals = (0.3, 0.38, 0.34, 0.46, 0.54, 0.62, 0.72)
    for i, v in enumerate(vals):
        x = 0.48 + i * 0.07
        col = CRIMSON if i == len(vals) - 1 else (90, 100, 116)
        a.rect(x, 0.96 - v, x + 0.05, 0.96, fill=col, outline=None)
    a.line([(0.5, 0.56), (0.66, 0.46), (0.78, 0.4), (0.92, 0.14)], INK, 2.2)
    a.poly([(0.95, 0.06), (0.88, 0.14), (0.95, 0.2)], fill=INK, outline=None)
    a.line([(0.44, 0.96), (0.99, 0.96)], INK, 1.4)
    a.finish("JAPAN: +2.3%")


# ---- 10. Seoul: move to impeach the chief justice -------------------------
def art_seoul():
    a = Art("art_10.png", GRID, (204, 220, 236), GRID_BAND)
    a.gradient((176, 200, 228), (232, 238, 244), 0, 0.8, 12)
    a.rect(0, 0.8, 1, 1, fill=(186, 184, 176), outline=None)
    # court building: pediment, columns, steps
    a.poly([(0.08, 0.26), (0.38, 0.04), (0.68, 0.26)], fill=(236, 232, 222), outline=INK, width=1.2)
    a.rect(0.1, 0.26, 0.66, 0.32, fill=(226, 222, 210), outline=INK, width=1)
    for k in range(6):
        x = 0.14 + k * 0.095
        a.rect(x, 0.32, x + 0.04, 0.72, fill=(244, 240, 232), outline=INK, width=0.8)
    a.rect(0.08, 0.72, 0.68, 0.78, fill=(214, 208, 196), outline=INK, width=1)
    a.rect(0.04, 0.78, 0.72, 0.84, fill=(200, 194, 182), outline=INK, width=1)
    # scales of justice on pediment
    a.circle(0.38, 0.18, 0.04, fill=GOLD, outline=INK, width=0.8)
    # impeachment motion paper with red seal
    a.poly([(0.74, 0.12), (0.96, 0.08), (0.99, 0.7), (0.77, 0.74)], fill=WHITE, outline=INK, width=1.2)
    for k in range(5):
        y = 0.2 + k * 0.08
        a.line([(0.78, y), (0.95, y - 0.02)], GREY, 1.1)
    a.circle(0.88, 0.6, 0.1, fill=None, outline=CRIMSON, width=2.2)
    a.circle(0.88, 0.6, 0.05, fill=CRIMSON, outline=None)
    # gavel
    a.line([(0.6, 0.98), (0.76, 0.82)], (110, 70, 40), 3)
    a.rrect(0.72, 0.74, 0.84, 0.88, r=3, fill=(130, 84, 48), outline=INK, width=1)
    a.finish("SEOUL: IMPEACH")


# ---- 11. Kenya's first oil well -------------------------------------------
def art_kenya():
    a = Art("art_11.png", GRID, (240, 170, 90), GRID_BAND)
    a.gradient((236, 140, 70), (250, 214, 140), 0, 0.72, 12)
    a.glow(0.8, 0.52, 0.36, 0.36, (255, 214, 120), 200)
    a.circle(0.8, 0.5, 0.2, fill=(255, 236, 170), outline=None)
    a.rect(0, 0.72, 1, 1, fill=(176, 130, 76), outline=None)
    # acacia
    a.line([(0.14, 0.86), (0.16, 0.5)], (60, 40, 30), 2.4)
    a.poly([(0.02, 0.5), (0.1, 0.36), (0.24, 0.34), (0.32, 0.48)], fill=(50, 60, 34), outline=None)
    # drilling derrick (lattice)
    base_l, base_r, top = 0.44, 0.66, 0.02
    a.line([(base_l, 0.84), (0.535, top)], INK, 2)
    a.line([(base_r, 0.84), (0.565, top)], INK, 2)
    for k in range(7):
        y = 0.84 - k * 0.12
        t = (0.84 - y) / (0.84 - top)
        xl = base_l + (0.535 - base_l) * t
        xr = base_r + (0.565 - base_r) * t
        y2 = y - 0.12
        t2 = (0.84 - y2) / (0.84 - top)
        xl2 = base_l + (0.535 - base_l) * t2
        xr2 = base_r + (0.565 - base_r) * t2
        a.line([(xl, y), (xr, y)], INK, 1)
        if y2 > top:
            a.line([(xl, y), (xr2, y2)], INK, 0.9)
            a.line([(xr, y), (xl2, y2)], INK, 0.9)
    a.rect(0.38, 0.8, 0.74, 0.88, fill=(70, 70, 76), outline=INK, width=1)
    # tanks and pipe
    a.rrect(0.78, 0.68, 0.96, 0.9, r=3, fill=(220, 220, 214), outline=INK, width=1)
    a.line([(0.74, 0.84), (0.78, 0.84)], INK, 2)
    # Kenyan flag
    flagpole(a, 0.28, 0.1, 0.86)
    for k, col in enumerate((INK, WHITE, (187, 0, 0), WHITE, (0, 102, 0))):
        h = (0.07, 0.015, 0.07, 0.015, 0.07)[k]
        y0 = 0.1 + sum((0.07, 0.015, 0.07, 0.015, 0.07)[:k])
        a.rect(0.28, y0, 0.4, y0 + h, fill=col, outline=None)
    a.rect(0.28, 0.1, 0.4, 0.34, fill=None, outline=INK, width=0.8)
    a.finish("KENYA: OIL")


# ---- 12. Bukele third-term bid --------------------------------------------
def art_bukele():
    a = Art("art_12.png", GRID, (190, 220, 240), GRID_BAND)
    a.gradient((150, 196, 232), (226, 238, 246), 0, 0.7, 12)
    # San Salvador volcano silhouette
    a.poly([(0.3, 0.72), (0.56, 0.2), (0.64, 0.18), (0.94, 0.72)], fill=(96, 118, 110), outline=None)
    a.poly([(0.52, 0.28), (0.56, 0.2), (0.64, 0.18), (0.68, 0.28), (0.6, 0.26)], fill=(130, 150, 140), outline=None)
    a.rect(0, 0.72, 1, 1, fill=(120, 150, 96), outline=None)
    # Salvadoran flag (blue-white-blue)
    flagpole(a, 0.06, 0.06, 0.94)
    for k, col in enumerate(((0, 71, 171), WHITE, (0, 71, 171))):
        a.rect(0.06, 0.06 + k * 0.08, 0.26, 0.14 + k * 0.08, fill=col, outline=None)
    a.rect(0.06, 0.06, 0.26, 0.3, fill=None, outline=INK, width=0.8)
    a.poly([(0.145, 0.205), (0.16, 0.155), (0.175, 0.205)], fill=(0, 122, 61), outline=GOLD, width=0.6)  # emblem
    # ballot box with ballot going in
    a.rect(0.34, 0.5, 0.66, 0.94, fill=WHITE, outline=INK, width=1.4)
    a.rect(0.34, 0.5, 0.66, 0.58, fill=(0, 71, 171), outline=INK, width=1)
    a.rect(0.44, 0.52, 0.56, 0.555, fill=INK, outline=None)
    a.poly([(0.45, 0.2), (0.57, 0.18), (0.56, 0.54), (0.46, 0.54)], fill=PAPER, outline=INK, width=1.1)
    a.line([(0.48, 0.3), (0.52, 0.36), (0.55, 0.26)], CRIMSON, 1.8)
    # filing folder / tribunal stamp
    a.rrect(0.72, 0.56, 0.96, 0.9, r=3, fill=(236, 214, 150), outline=INK, width=1.1)
    a.line([(0.75, 0.66), (0.93, 0.66)], GREY, 1)
    a.line([(0.75, 0.74), (0.93, 0.74)], GREY, 1)
    a.finish("BUKELE: 3RD BID")


# ---- 13. Phillips century v India -----------------------------------------
def art_phillips():
    a = Art("art_13.png", GRID, (70, 140, 80), GRID_BAND)
    a.gradient((150, 196, 230), (210, 230, 240), 0, 0.36, 8)
    # stand
    a.rect(0, 0.26, 1, 0.42, fill=(70, 80, 96), outline=None)
    for k in range(10):
        a.circle(0.05 + k * 0.1, 0.32, 0.04, fill=(170, 178, 192), outline=None)
    # outfield stripes
    for k in range(6):
        col = (70, 150, 80) if k % 2 else (84, 164, 92)
        a.rect(0, 0.42 + k * 0.1, 1, 0.52 + k * 0.1, fill=col, outline=None)
    # pitch
    a.poly([(0.36, 0.5), (0.5, 0.5), (0.62, 1), (0.3, 1)], fill=(216, 196, 140), outline=None)
    for x in (0.4, 0.43, 0.46):
        a.rect(x, 0.42, x + 0.012, 0.56, fill=WHITE, outline=INK, width=0.6)
    # batter in black, bat raised to celebrate the hundred
    bx = 0.62
    a.circle(bx, 0.42, 0.06, fill=(20, 20, 24), outline=None)
    a.rrect(bx - 0.035, 0.48, bx + 0.035, 0.76, r=3, fill=(20, 20, 24), outline=None)
    a.line([(bx - 0.02, 0.76), (bx - 0.04, 0.96)], (20, 20, 24), 3)
    a.line([(bx + 0.02, 0.76), (bx + 0.04, 0.96)], (20, 20, 24), 3)
    a.line([(bx + 0.03, 0.52), (bx + 0.09, 0.32)], (20, 20, 24), 2.4)
    a.line([(bx + 0.09, 0.32), (bx + 0.13, 0.02)], (226, 200, 150), 3.4)
    a.line([(bx - 0.03, 0.52), (bx - 0.08, 0.36)], (20, 20, 24), 2.4)
    a.circle(bx - 0.08, 0.34, 0.03, fill=(232, 196, 160), outline=None)
    # scoreboard
    a.rect(0.78, 0.04, 0.98, 0.24, fill=INK, outline=(230, 230, 230), width=1)
    for k in range(3):
        a.rect(0.8 + k * 0.06, 0.08, 0.84 + k * 0.06, 0.2, fill=(250, 214, 80), outline=None)
    a.circle(0.24, 0.72, 0.03, fill=(220, 30, 40), outline=WHITE, width=0.6)
    a.finish("PHILLIPS: 118")


ART_FUNCS = [art_kyiv, art_akvan, art_chips, art_euuk, art_cop31, art_poland, art_iraq,
             art_italy, art_japan, art_seoul, art_kenya, art_bukele, art_phillips]


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
        # v10: no attribution boxes over the art; sources print in each caption
        if any(lb["kind"] == "attr" for lb in labels):
            bad.append((name, "attribution tag drawn over the art"))
    if bad:
        raise SystemExit(f"art label failure: {bad}")
    print(f"art: {len(ART_FUNCS)} illustrations, {len(LABELS)} labels, padding and overlap ok")


if __name__ == "__main__":
    build_all()

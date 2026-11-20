"""Editorial illustrations for the Friday 20 November 2026 front page.

Every graphic is drawn from scratch with Pillow at twice its printed size,
then reduced with Lanczos so the printed pixels are cleanly supersampled.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

# ---- palette ---------------------------------------------------------------
CREAM = (246, 241, 230)
PAPER = (255, 253, 247)
INK = (20, 25, 35)
CRIMSON = (154, 27, 31)
CRIMSON_D = (112, 18, 22)
TEAL = (29, 111, 106)
TEAL_D = (17, 74, 72)
AMBER = (217, 138, 31)
GOLD = (242, 179, 92)
SKY = (169, 207, 227)
NAVY = (27, 42, 65)
SAND = (230, 220, 197)
WHITE = (255, 253, 247)
RED = (200, 40, 45)
GREEN = (46, 125, 80)
BLUE = (46, 109, 164)
GREY = (120, 128, 138)
LIGHT = (214, 224, 232)
ORANGE = (235, 106, 45)
PURPLE = (94, 58, 122)

FONT_DIR = Path("/usr/share/fonts/truetype")
LATO_BLACK = FONT_DIR / "lato" / "Lato-Black.ttf"
LATO_BOLD = FONT_DIR / "lato" / "Lato-Bold.ttf"
LATO_REG = FONT_DIR / "lato" / "Lato-Regular.ttf"
LATO_IT = FONT_DIR / "lato" / "Lato-Italic.ttf"
LATO_BOLD_IT = FONT_DIR / "lato" / "Lato-BoldItalic.ttf"
SERIF_BOLD = FONT_DIR / "liberation" / "LiberationSerif-Bold.ttf"

LABEL_BOXES: list[tuple[str, tuple[int, int, int, int], tuple[int, int]]] = []


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def canvas(w: int, h: int, bg) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (w * 2, h * 2), bg)
    return im, ImageDraw.Draw(im)


def text(d, xy, s, f, fill=INK, anchor="la", spacing=0):
    d.multiline_text(xy, s, font=f, fill=fill, anchor=anchor, spacing=spacing)


def tw(d, s, f) -> int:
    return int(d.textlength(s, font=f))


def label(d, s, x, y, f, fg=WHITE, bg=CRIMSON, pad_x=10, pad_y=5, radius=4):
    """A padded graphic label, always kept clear of the art-box edge."""
    box = d.textbbox((0, 0), s, font=f)
    w = box[2] - box[0] + pad_x * 2
    h = box[3] - box[1] + pad_y * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg)
    d.text((x + pad_x - box[0], y + pad_y - box[1]), s, font=f, fill=fg)
    LABEL_BOXES.append((s, (x, y, x + w, y + h), (d._image.size[0], d._image.size[1])))
    return w, h


def star(d, cx, cy, r, fill=GOLD, points=5, rot=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * 0.42
        a = rot + i * math.pi / points
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def ring(d, cx, cy, r, width, fill, start=0, end=360):
    d.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=end, fill=fill, width=width)


def palm(d, x, y, scale=1.0, trunk=INK, leaf=GREEN):
    # trunk
    pts = []
    for i in range(14):
        t = i / 13
        pts.append((x + 14 * scale * t * t, y - 70 * scale * t))
    d.line(pts, fill=trunk, width=max(2, int(4 * scale)))
    # fronds
    for ang in (-165, -135, -105, -75, -45, -15):
        a = math.radians(ang)
        ex = x + 46 * scale * math.cos(a)
        ey = y - 70 * scale + 34 * scale * math.sin(a)
        mx = (x + ex) / 2
        my = (y - 70 * scale + ey) / 2 - 16 * scale
        d.line([(x, y - 70 * scale), (mx, my), (ex, ey)], fill=leaf, width=max(2, int(4 * scale)), joint="curve")


def house(d, x, y, w, h, wall=CREAM, roof=CRIMSON):
    d.rectangle([x, y, x + w, y + h], fill=wall, outline=INK, width=2)
    d.polygon([(x - 3, y), (x + w / 2, y - h * 0.55), (x + w + 3, y)], fill=roof, outline=INK)
    d.rectangle([x + w * 0.42, y + h * 0.48, x + w * 0.62, y + h * 0.78], fill=INK)


def cloud(d, x, y, s, fill=WHITE):
    for dx, dy, r in ((0, 0, 16), (18, -8, 20), (40, 0, 15), (20, 7, 18)):
        d.ellipse([x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s], fill=fill)


def smoke(d, x, y, s=1.0, fill=(210, 210, 205)):
    for i in range(3):
        cloud(d, x + i * 18 * s, y - i * 10 * s, s * (1 - i * 0.15), fill)


def finish(im, name, w, h):
    im = im.resize((w, h), Image.LANCZOS)
    ASSETS.mkdir(exist_ok=True)
    im.save(ASSETS / name, format="PNG", optimize=True)
    return im


# ---- 1. Cyclone Akvan ------------------------------------------------------
def art_akvan(w=600, h=200):
    im, d = canvas(w, h, TEAL)
    W, H = w * 2, h * 2
    # sea bands
    d.rectangle([0, 0, W, H], fill=(32, 122, 132))
    d.rectangle([0, H * 0.62, W, H], fill=(24, 96, 112))
    # rain
    for i in range(26):
        x = (i * 53) % W
        y = (i * 37) % (H * 0.60)
        d.line([(x, y), (x - 18, y + 34)], fill=(150, 205, 215), width=3)
    # cyclone
    cx, cy = W * 0.34, H * 0.47
    for r, wd in ((128, 9), (98, 8), (68, 7), (40, 6)):
        ring(d, cx, cy, r, wd, WHITE, 18, 330)
        ring(d, cx, cy, r - 12, wd, (180, 225, 230), 35, 315)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=CRIMSON)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=GOLD)
    # coast
    d.polygon([(W * 0.50, H), (W * 0.55, H * 0.78), (W * 0.72, H * 0.68),
               (W * 0.86, H * 0.76), (W, H * 0.66), (W, H)], fill=SAND, outline=INK)
    # palm and houses
    palm(d, W * 0.79, H * 0.76, 1.35, INK, (20, 92, 62))
    house(d, W * 0.62, H * 0.76, 34, 24, CREAM, CRIMSON)
    house(d, W * 0.69, H * 0.80, 28, 20, PAPER, CRIMSON)
    # warning triangle
    tx, ty = W * 0.90, H * 0.18
    d.polygon([(tx, ty - 30), (tx - 34, ty + 26), (tx + 34, ty + 26)], fill=GOLD, outline=INK)
    d.line([(tx, ty - 12), (tx, ty + 8)], fill=INK, width=6)
    d.ellipse([tx - 3, ty + 14, tx + 5, ty + 22], fill=INK)
    f = font(LATO_BLACK, 28)
    label(d, "AKVAN  ·  ODISHA", 26, H - 62, f, WHITE, CRIMSON, 12, 7)
    return finish(im, "art_01.png", w, h)


# ---- 2. EU-UK summit -------------------------------------------------------
def art_euuk(w=600, h=200):
    im, d = canvas(w, h, CREAM)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(232, 216, 190))
    # bold crimson mast band
    d.rectangle([0, 0, W, 16], fill=CRIMSON)
    # EU flag
    ex, ey, ew, eh = 36, 34, 220, 136
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(27, 58, 118), outline=INK, width=3)
    for i in range(12):
        a = -math.pi / 2 + i * math.pi / 6
        star(d, ex + ew / 2 + 42 * math.cos(a), ey + eh / 2 + 42 * math.sin(a), 9, GOLD)
    # UK flag
    ux, uy, uw, uh = W - 256, 34, 220, 136
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(22, 40, 74), outline=INK, width=3)
    d.line([(ux, uy), (ux + uw, uy + uh)], fill=WHITE, width=20)
    d.line([(ux + uw, uy), (ux, uy + uh)], fill=WHITE, width=20)
    d.line([(ux, uy), (ux + uw, uy + uh)], fill=CRIMSON, width=9)
    d.line([(ux + uw, uy), (ux, uy + uh)], fill=CRIMSON, width=9)
    d.rectangle([ux + uw / 2 - 15, uy, ux + uw / 2 + 15, uy + uh], fill=WHITE)
    d.rectangle([ux, uy + uh / 2 - 15, ux + uw, uy + uh / 2 + 15], fill=WHITE)
    d.rectangle([ux + uw / 2 - 8, uy, ux + uw / 2 + 8, uy + uh], fill=CRIMSON)
    d.rectangle([ux, uy + uh / 2 - 8, ux + uw, uy + uh / 2 + 8], fill=CRIMSON)
    # handshake on a dark podium
    hx, hy = W / 2, H * 0.58
    d.rounded_rectangle([hx - 150, hy - 34, hx + 150, hy + 40], radius=16, fill=NAVY, outline=INK, width=3)
    d.rounded_rectangle([hx - 118, hy - 10, hx - 10, hy + 20], radius=10, fill=SAND, outline=WHITE, width=3)
    d.rounded_rectangle([hx + 10, hy - 10, hx + 118, hy + 20], radius=10, fill=(225, 190, 150), outline=WHITE, width=3)
    d.ellipse([hx - 28, hy - 26, hx + 28, hy + 26], fill=CRIMSON, outline=WHITE, width=3)
    d.line([(hx - 16, hy - 2), (hx + 16, hy - 2)], fill=WHITE, width=5)
    f = font(LATO_BLACK, 28)
    label(d, "EU–UK  ·  BRUSSELS", 26, H - 62, f, WHITE, CRIMSON, 12, 7)
    f2 = font(LATO_BOLD, 16)
    label(d, "YOUTH MOBILITY 100,000", W / 2 - 104, 20, f2, INK, GOLD, 9, 5)
    return finish(im, "art_02.png", w, h)


# ---- 3. COP31 --------------------------------------------------------------
def art_cop31(w=600, h=200):
    im, d = canvas(w, h, GOLD)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(241, 178, 92))
    d.rectangle([0, H * 0.64, W, H * 0.80], fill=(34, 126, 138))
    d.rectangle([0, H * 0.80, W, H], fill=SAND)
    # sun
    d.ellipse([W - 130, 18, W - 40, 108], fill=(255, 226, 150))
    for i in range(10):
        a = i * math.pi / 5
        d.line([(W - 85 + 58 * math.cos(a), 63 + 58 * math.sin(a)),
                (W - 85 + 74 * math.cos(a), 63 + 74 * math.sin(a))], fill=(255, 226, 150), width=4)
    # globe thermometer
    gx, gy, gr = W * 0.28, H * 0.40, 58
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=WHITE, outline=INK, width=4)
    d.ellipse([gx - 34, gy - 34, gx + 2, gy + 2], fill=TEAL)
    d.ellipse([gx + 4, gy - 6, gx + 38, gy + 28], fill=TEAL)
    d.ellipse([gx - 8, gy + 20, gx + 24, gy + 48], fill=TEAL)
    # thermometer
    d.rounded_rectangle([gx + gr - 9, gy - 42, gx + gr + 9, gy + 34], radius=9, fill=WHITE, outline=INK, width=3)
    d.rounded_rectangle([gx + gr - 4, gy - 8, gx + gr + 4, gy + 32], radius=4, fill=CRIMSON)
    d.ellipse([gx + gr - 15, gy + 26, gx + gr + 15, gy + 56], fill=CRIMSON, outline=INK, width=3)
    f = font(LATO_BLACK, 18)
    d.text((gx, gy + 6), "1.5°C", font=f, fill=WHITE, anchor="mm")
    # smokestacks
    for i, (sx, sh) in enumerate(((W * 0.53, 60), (W * 0.59, 78), (W * 0.65, 48))):
        d.rectangle([sx, H * 0.64 - sh, sx + 20, H * 0.64], fill=(96, 96, 96), outline=INK, width=2)
        d.rectangle([sx, H * 0.64 - sh, sx + 20, H * 0.64 - sh + 10], fill=CRIMSON)
        smoke(d, sx + 6, H * 0.64 - sh - 6, 0.7, (225, 225, 220))
    # placard
    px, py = W * 0.73, H * 0.30
    d.line([(px + 44, py + 42), (px + 44, H * 0.80)], fill=INK, width=4)
    d.rectangle([px, py, px + 150, py + 54], fill=WHITE, outline=INK, width=3)
    d.text((px + 75, py + 27), "FINANCE?", font=font(LATO_BLACK, 18), fill=CRIMSON, anchor="mm")
    # pacific waves
    for i in range(3):
        d.arc([W * 0.34, H * 0.74 + i * 10, W * 0.62, H * 0.86 + i * 10], 200, 340, fill=WHITE, width=4)
    f = font(LATO_BLACK, 28)
    label(d, "COP31  ·  FINAL DAY", 26, H - 62, f, WHITE, NAVY, 12, 7)
    f2 = font(LATO_BOLD, 16)
    label(d, "ANTALYA  ·  DAY 12", W - 230, 24, f2, WHITE, CRIMSON, 9, 5)
    return finish(im, "art_03.png", w, h)


# ---- 4. Pentagon Iran-war cost --------------------------------------------
def art_pentagon(w=344, h=148):
    """Daylight $48.3BN defence-cost chart: no crossing rules, no overlap."""
    im, d = canvas(w, h, (243, 236, 222))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(243, 236, 222))
    # crisp navy mast band
    d.rectangle([0, 0, W, 12], fill=NAVY)
    # headline figure, kept in its own clear column
    d.text((18, 22), "IRAN WAR BILL", font=font(LATO_BLACK, 12), fill=CRIMSON)
    d.text((16, 38), "$48.3BN", font=font(LATO_BLACK, 46), fill=NAVY)
    d.rectangle([16, 92, 168, 95], fill=CRIMSON)
    d.text((18, 102), "EXCLUDES BASE DAMAGE", font=font(LATO_BOLD, 9), fill=INK)
    # five-sided Pentagon building, right column
    pcx, pcy, pr = 286, 62, 46
    pts = [(pcx + pr * math.cos(-math.pi / 2 + i * 2 * math.pi / 5),
            pcy + pr * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i in range(5)]
    d.polygon(pts, fill=NAVY, outline=WHITE, width=3)
    inner = [(pcx + pr * 0.58 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5),
              pcy + pr * 0.58 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i in range(5)]
    d.polygon(inner, fill=None, outline=GOLD, width=2)
    star(d, pcx, pcy, 11, GOLD)
    f = font(LATO_BLACK, 20)
    label(d, "PENTAGON  ·  IRAN", 14, H - 42, f, WHITE, CRIMSON, 8, 4)
    return finish(im, "art_04.png", w, h)


# ---- 5. Rohingya -----------------------------------------------------------
def art_rohingya(w=344, h=148):
    im, d = canvas(w, h, AMBER)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(226, 158, 65))
    d.rectangle([0, H * 0.70, W, H], fill=(206, 132, 48))
    # shelters
    for x, s in ((22, 1.0), (120, 0.85), (228, 1.1), (292, 0.6)):
        d.polygon([(x, H * 0.68), (x + 34 * s, H * 0.48), (x + 68 * s, H * 0.68)], fill=(112, 74, 42), outline=INK)
        d.rectangle([x + 8 * s, H * 0.68, x + 60 * s, H * 0.80], fill=(150, 105, 62), outline=INK)
    # crowd silhouettes with raised hands
    for i in range(12):
        x = 26 + i * 27
        y = H * 0.80 + (i % 3) * 5
        d.ellipse([x - 7, y - 26, x + 7, y - 12], fill=INK)
        d.rounded_rectangle([x - 9, y - 12, x + 9, y + 18], radius=7, fill=INK)
        d.line([(x - 8, y - 6), (x - 18, y - 28)], fill=INK, width=4)
        d.line([(x + 8, y - 6), (x + 20, y - 30)], fill=INK, width=4)
    # banner
    bx, by = W * 0.20, 22
    d.rectangle([bx, by, bx + 196, by + 44], fill=WHITE, outline=INK, width=3)
    d.text((bx + 98, by + 22), "JUSTICE", font=font(LATO_BLACK, 24), fill=CRIMSON, anchor="mm")
    # tear
    d.polygon([(W * 0.82, 30), (W * 0.82 - 12, 56), (W * 0.82 + 12, 56)], fill=(120, 200, 225), outline=INK)
    d.ellipse([W * 0.82 - 12, 44, W * 0.82 + 12, 68], fill=(120, 200, 225), outline=INK)
    f = font(LATO_BLACK, 22)
    label(d, "ROHINGYA", 14, H - 42, f, NAVY, WHITE, 8, 4)
    return finish(im, "art_05.png", w, h)


# ---- 6. Berlin -------------------------------------------------------------
def art_berlin(w=344, h=148):
    im, d = canvas(w, h, CREAM)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(232, 180, 92))
    d.rectangle([0, 0, W, 18], fill=CRIMSON)
    d.rectangle([0, H * 0.70, W, H], fill=(198, 142, 62))
    # gate
    gx, gy, gw = W * 0.50, H * 0.60, 200
    d.rectangle([gx - gw / 2, gy - 54, gx + gw / 2, gy], fill=(222, 210, 188), outline=INK, width=3)
    for i in range(5):
        x = gx - gw / 2 + 18 + i * 40
        d.rectangle([x, gy - 44, x + 18, gy], fill=CREAM, outline=INK, width=2)
    d.rectangle([gx - gw / 2 - 14, gy - 66, gx + gw / 2 + 14, gy - 50], fill=(176, 168, 154), outline=INK, width=2)
    d.rectangle([gx - 28, gy - 86, gx + 28, gy - 66], fill=INK)
    d.ellipse([gx - 20, gy - 100, gx - 2, gy - 82], fill=INK)
    d.ellipse([gx + 2, gy - 100, gx + 20, gy - 82], fill=INK)
    # crowd
    for i in range(16):
        x = 14 + i * 21
        y = H * 0.72 + (i % 3) * 4
        d.ellipse([x - 6, y - 24, x + 6, y - 12], fill=INK)
        d.rounded_rectangle([x - 8, y - 12, x + 8, y + 14], radius=6, fill=INK)
    # placards
    for x, s_, col in ((34, "NO", CRIMSON), (112, "PEACE", NAVY), (214, "NO", CRIMSON), (282, "PEACE", NAVY)):
        d.line([(x + 24, H * 0.74), (x + 24, H * 0.50)], fill=INK, width=3)
        d.rectangle([x, H * 0.38, x + 68, H * 0.52], fill=WHITE, outline=INK, width=2)
        d.text((x + 34, H * 0.45), s_, font=font(LATO_BLACK, 13), fill=col, anchor="mm")
    f = font(LATO_BLACK, 22)
    label(d, "BERLIN", 14, H - 42, f, WHITE, CRIMSON, 8, 4)
    return finish(im, "art_06.png", w, h)


# ---- 7. UN secretary-general ----------------------------------------------
def art_un(w=344, h=148):
    im, d = canvas(w, h, BLUE)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(42, 101, 158))
    d.rectangle([0, 0, W, 14], fill=GOLD)
    # globe
    gx, gy, gr = W * 0.34, H * 0.42, 52
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(226, 239, 248), outline=WHITE, width=4)
    for k in range(3):
        d.arc([gx - gr + 8, gy - gr + 12 + k * 14, gx + gr - 8, gy + gr - 12], 0, 180, fill=BLUE, width=4)
        d.arc([gx - gr + 8, gy - gr + 12, gx + gr - 8, gy + gr - 12 - k * 14], 180, 360, fill=BLUE, width=4)
    d.arc([gx - gr - 10, gy - gr - 10, gx + gr + 10, gy + gr + 10], 120, 240, fill=GREEN, width=6)
    d.arc([gx - gr - 10, gy - gr - 10, gx + gr + 10, gy + gr + 10], 300, 60, fill=GREEN, width=6)
    d.text((gx, gy), "SG", font=font(LATO_BLACK, 30), fill=BLUE, anchor="mm")
    # 15 ballot boxes: P5 crimson, E10 white
    for i in range(15):
        x = W - 156 + (i % 5) * 28
        y = 22 + (i // 5) * 34
        col = CRIMSON if i < 5 else WHITE
        d.rectangle([x, y, x + 20, y + 24], fill=col, outline=INK, width=2)
        d.line([(x + 10, y - 6), (x + 10, y + 4)], fill=GOLD, width=3)
    # gavel
    d.rounded_rectangle([W - 146, H - 54, W - 54, H - 34], radius=5, fill=(150, 100, 55), outline=INK, width=2)
    d.rectangle([W - 136, H - 32, W - 64, H - 24], fill=(150, 100, 55), outline=INK, width=2)
    f = font(LATO_BLACK, 22)
    label(d, "UN VOTE", 14, H - 42, f, WHITE, NAVY, 8, 4)
    return finish(im, "art_07.png", w, h)


# ---- 8. U-17 World Cup -----------------------------------------------------
def art_u17(w=344, h=148):
    im, d = canvas(w, h, (138, 21, 56))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(128, 24, 54))
    d.rectangle([0, H * 0.76, W, H], fill=(218, 200, 164))
    # stadium arc
    d.arc([-30, 10, W + 30, H * 1.25], 200, 340, fill=(235, 220, 190), width=7)
    for i in range(7):
        a = math.radians(205 + i * 18)
        x = W / 2 + 170 * math.cos(a)
        y = H * 0.75 + 120 * math.sin(a)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD)
    # football
    bx, by, br = W * 0.38, H * 0.46, 38
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=WHITE, outline=INK, width=3)
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        px, py = bx + 20 * math.cos(a), by + 20 * math.sin(a)
        d.polygon([(px, py - 9), (px + 9, py - 3), (px + 6, py + 8), (px - 6, py + 8), (px - 9, py - 3)], fill=INK)
    d.polygon([(bx, by - 10), (bx + 10, by - 3), (bx + 6, by + 9), (bx - 6, by + 9), (bx - 10, by - 3)], fill=INK)
    # three african flags
    flags = [((200, 30, 40), (0, 110, 60)), ((0, 120, 70), (250, 210, 50)), ((20, 130, 70), (220, 40, 45))]
    for i, (c1, c2) in enumerate(flags):
        fx = W - 120 + (i % 2) * 46
        fy = 22 + (i // 2) * 42
        d.rectangle([fx, fy, fx + 38, fy + 26], fill=c1, outline=INK, width=2)
        if i == 0:
            star(d, fx + 19, fy + 13, 7, (0, 110, 60))
        else:
            d.rectangle([fx, fy, fx + 10, fy + 26], fill=c2)
    # crisp dark badges for the tournament scale
    f_badge = font(LATO_BLACK, 13)
    label(d, "48 TEAMS", W - 162, 120, f_badge, WHITE, INK, 7, 3)
    label(d, "104 MATCHES", W - 162, 141, f_badge, WHITE, INK, 7, 3)
    f = font(LATO_BLACK, 22)
    label(d, "U17  ·  QATAR", 14, H - 42, f, WHITE, CRIMSON, 8, 4)
    return finish(im, "art_08.png", w, h)


# ---- 9. NextDC -------------------------------------------------------------
def art_nextdc(w=344, h=148):
    im, d = canvas(w, h, SKY)
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(166, 207, 226))
    # ground
    d.rectangle([0, H * 0.76, W, H], fill=(122, 156, 92))
    # data centre
    dx, dy, dw, dh = W * 0.26, H * 0.36, 168, 84
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(70, 82, 92), outline=INK, width=3)
    d.rectangle([dx, dy, dx + dw, dy + 16], fill=(48, 58, 68))
    for i in range(3):
        for j in range(4):
            d.rectangle([dx + 12 + i * 52, dy + 26 + j * 14, dx + 50 + i * 52, dy + 36 + j * 14], fill=(30, 38, 46))
            d.ellipse([dx + 16 + i * 52, dy + 30 + j * 14, dx + 20 + i * 52, dy + 34 + j * 14], fill=GREEN if (i + j) % 3 else RED)
    # cooling fans
    for i in range(3):
        fx, fy = dx + 26 + i * 52, dy - 16
        d.ellipse([fx - 15, fy - 15, fx + 15, fy + 15], fill=(210, 220, 226), outline=INK, width=2)
        d.line([(fx, fy), (fx + 12, fy - 8)], fill=INK, width=2)
    # houses
    for i in range(4):
        x = 24 + i * 54
        y = H * 0.78
        d.rectangle([x, y, x + 38, y + 30], fill=CREAM, outline=INK, width=2)
        d.polygon([(x - 4, y), (x + 19, y - 20), (x + 42, y)], fill=CRIMSON, outline=INK)
    # no symbol over pylon
    px, py = W * 0.78, H * 0.44
    d.line([(px, py + 70), (px - 26, py - 26)], fill=INK, width=5)
    d.line([(px, py + 70), (px + 26, py - 26)], fill=INK, width=5)
    d.line([(px - 18, py + 18), (px + 18, py + 18)], fill=INK, width=4)
    d.line([(px - 12, py + 42), (px + 12, py + 42)], fill=INK, width=4)
    d.ellipse([px - 28, py - 26, px + 28, py + 30], outline=CRIMSON, width=7)
    d.line([(px - 20, py - 18), (px + 20, py + 22)], fill=CRIMSON, width=7)
    f = font(LATO_BLACK, 22)
    label(d, "NEXTDC  ·  MELBOURNE", 14, H - 42, f, WHITE, TEAL_D, 8, 4)
    return finish(im, "art_09.png", w, h)


# ---- 10. Comancheros -------------------------------------------------------
def art_ofac(w=344, h=148):
    im, d = canvas(w, h, (20, 30, 34))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(28, 96, 94))
    d.rectangle([0, 0, W, 14], fill=GOLD)
    # motorcycle, held clear of the stamp
    mx, my = W * 0.30, H * 0.36
    for wx in (mx - 50, mx + 50):
        d.ellipse([wx - 26, my + 6, wx + 26, my + 58], outline=INK, width=9)
        d.ellipse([wx - 26, my + 6, wx + 26, my + 58], outline=(235, 240, 240), width=3)
        d.ellipse([wx - 9, my + 25, wx + 9, my + 43], fill=(235, 240, 240), outline=INK, width=2)
    d.line([(mx - 50, my + 32), (mx - 18, my - 6), (mx + 30, my - 6), (mx + 50, my + 32)], fill=CRIMSON, width=10)
    d.line([(mx - 18, my - 6), (mx + 10, my + 30)], fill=CRIMSON, width=9)
    d.rounded_rectangle([mx - 28, my - 30, mx + 18, my - 8], radius=8, fill=WHITE, outline=INK, width=2)
    # treasury seal
    sx, sy = W - 70, 44
    d.ellipse([sx - 30, sy - 30, sx + 30, sy + 30], fill=GOLD, outline=INK, width=3)
    star(d, sx, sy, 17, WHITE)
    d.text((sx, sy + 38), "OFAC", font=font(LATO_BLACK, 12), fill=WHITE, anchor="mm")
    # solid crimson stamp, no crossing rules
    f_stamp = font(LATO_BLACK, 17)
    label(d, "SANCTIONED", W - 178, H - 42, f_stamp, WHITE, CRIMSON, 10, 4)
    f = font(LATO_BLACK, 22)
    label(d, "OFAC  ·  NZ", 14, H - 42, f, WHITE, CRIMSON, 8, 4)
    return finish(im, "art_10.png", w, h)


# ---- 11. Hormuz ------------------------------------------------------------
def art_hormuz(w=344, h=148):
    im, d = canvas(w, h, (36, 106, 130))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(38, 112, 136))
    # sea
    d.rectangle([0, H * 0.58, W, H], fill=(24, 82, 108))
    for i in range(5):
        d.arc([-20 + i * 80, H * 0.62 + i * 5, 60 + i * 80, H * 0.74 + i * 5], 200, 340, fill=(120, 190, 205), width=3)
    # land masses (strait)
    d.polygon([(0, H * 0.52), (70, H * 0.40), (128, H * 0.48), (110, H * 0.58), (0, H * 0.60)], fill=SAND, outline=INK)
    d.polygon([(W, H * 0.50), (W - 70, H * 0.38), (W - 118, H * 0.48), (W - 100, H * 0.58), (W, H * 0.60)], fill=SAND, outline=INK)
    # tanker
    tx, ty = W * 0.50, H * 0.46
    d.polygon([(tx - 70, ty + 18), (tx + 70, ty + 18), (tx + 54, ty + 44), (tx - 54, ty + 44)], fill=(28, 34, 42), outline=INK)
    d.rectangle([tx - 28, ty - 16, tx + 18, ty + 18], fill=(210, 216, 220), outline=INK, width=2)
    d.rectangle([tx - 20, ty - 32, tx - 6, ty - 16], fill=CRIMSON, outline=INK, width=2)
    for i in range(4):
        d.rectangle([tx + 22 + i * 10, ty - 4, tx + 28 + i * 10, ty + 16], fill=(230, 160, 50), outline=INK)
    # insurance doc + arrow
    px, py = W - 118, 18
    d.rectangle([px, py, px + 92, py + 88], fill=WHITE, outline=INK, width=3)
    for i in range(4):
        d.line([(px + 10, py + 18 + i * 12), (px + 76, py + 18 + i * 12)], fill=(130, 136, 144), width=2)
    d.line([(px + 12, py + 70), (px + 34, py + 58), (px + 54, py + 64), (px + 78, py + 34)], fill=CRIMSON, width=5)
    d.polygon([(px + 78, py + 34), (px + 62, py + 36), (px + 72, py + 48)], fill=CRIMSON)
    f = font(LATO_BLACK, 22)
    label(d, "HORMUZ  ·  SHIPPING", 14, H - 42, f, WHITE, NAVY, 8, 4)
    return finish(im, "art_11.png", w, h)


# ---- 12. Kyiv bridges ------------------------------------------------------
def art_kyiv(w=344, h=148):
    im, d = canvas(w, h, (54, 82, 110))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(58, 88, 116))
    # river
    d.rectangle([0, H * 0.66, W, H], fill=(28, 62, 92))
    for i in range(4):
        d.arc([-20 + i * 90, H * 0.70 + i * 4, 60 + i * 90, H * 0.80 + i * 4], 200, 340, fill=(100, 150, 180), width=3)
    # bridge decks
    d.rectangle([0, H * 0.52, W * 0.40, H * 0.58], fill=(180, 180, 176), outline=INK, width=2)
    d.rectangle([W * 0.58, H * 0.52, W, H * 0.58], fill=(180, 180, 176), outline=INK, width=2)
    for x in (30, 70, 110, 150):
        d.line([(x, H * 0.58), (x, H * 0.70)], fill=INK, width=4)
    for x in (W - 30, W - 70, W - 110, W - 150):
        d.line([(x, H * 0.58), (x, H * 0.70)], fill=INK, width=4)
    # broken gap + rubble
    d.polygon([(W * 0.40, H * 0.52), (W * 0.46, H * 0.58), (W * 0.42, H * 0.64), (W * 0.35, H * 0.58)], fill=INK)
    d.polygon([(W * 0.58, H * 0.52), (W * 0.52, H * 0.58), (W * 0.56, H * 0.64), (W * 0.63, H * 0.58)], fill=INK)
    # missile trail and blast
    d.line([(W * 0.18, 0), (W * 0.32, H * 0.24), (W * 0.46, H * 0.40)], fill=(255, 220, 170), width=6)
    bx, by = W * 0.50, H * 0.40
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(bx, by), (bx + 34 * math.cos(a), by + 34 * math.sin(a))], fill=ORANGE, width=5)
    d.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=GOLD, outline=CRIMSON, width=3)
    d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=WHITE)
    # emergency lights
    for lx, col in ((W * 0.36, CRIMSON), (W * 0.64, (60, 150, 235))):
        d.rounded_rectangle([lx - 14, H * 0.58, lx + 14, H * 0.64], radius=4, fill=col, outline=INK, width=2)
        d.ellipse([lx - 9, H * 0.59, lx + 9, H * 0.63], fill=WHITE)
    # cathedral dome
    cx, cy = W * 0.80, H * 0.36
    d.rectangle([cx - 26, cy, cx + 26, cy + 48], fill=(210, 200, 180), outline=INK, width=2)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 18], fill=GREEN, outline=INK, width=2)
    d.line([(cx, cy - 26), (cx, cy - 44)], fill=GOLD, width=3)
    d.line([(cx - 8, cy - 36), (cx + 8, cy - 36)], fill=GOLD, width=3)
    f = font(LATO_BLACK, 22)
    label(d, "KYIV  ·  WAR", 14, H - 42, f, WHITE, CRIMSON, 8, 4)
    return finish(im, "art_12.png", w, h)


# ---- 13. China-Australia ---------------------------------------------------
def art_china_aus(w=344, h=148):
    im, d = canvas(w, h, (150, 26, 32))
    W, H = w * 2, h * 2
    d.rectangle([0, 0, W, H], fill=(146, 28, 34))
    # sunburst
    for i in range(16):
        a = i * math.pi / 8
        d.line([(W / 2, H * 0.62), (W / 2 + 240 * math.cos(a), H * 0.62 + 240 * math.sin(a))], fill=(178, 48, 44), width=8)
    # china flag
    fx, fy, fw, fh = 20, 18, 96, 60
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(200, 30, 38), outline=INK, width=2)
    star(d, fx + 19, fy + 19, 12, GOLD)
    for dx, dy in ((36, 8), (43, 19), (43, 32), (36, 43)):
        star(d, fx + dx, fy + dy, 5, GOLD)
    # australia flag
    ax, ay, aw, ah = W - 116, 18, 96, 60
    d.rectangle([ax, ay, ax + aw, ay + ah], fill=(24, 40, 78), outline=INK, width=2)
    d.rectangle([ax, ay, ax + 42, ay + 30], fill=(24, 40, 78))
    d.line([(ax, ay), (ax + 42, ay + 30)], fill=WHITE, width=7)
    d.line([(ax + 42, ay), (ax, ay + 30)], fill=WHITE, width=7)
    d.line([(ax, ay), (ax + 42, ay + 30)], fill=CRIMSON, width=3)
    d.line([(ax + 42, ay), (ax, ay + 30)], fill=CRIMSON, width=3)
    d.rectangle([ax + 18, ay, ax + 24, ay + 30], fill=WHITE)
    d.rectangle([ax, ay + 12, ax + 42, ay + 18], fill=WHITE)
    d.rectangle([ax + 19, ay, ax + 23, ay + 30], fill=CRIMSON)
    d.rectangle([ax, ay + 13, ax + 42, ay + 17], fill=CRIMSON)
    for dx, dy in ((60, 12), (74, 26), (58, 40), (82, 46), (70, 54)):
        star(d, ax + dx, ay + dy, 4, WHITE)
    # handshake
    hx, hy = W / 2, H * 0.62
    d.rounded_rectangle([hx - 96, hy - 14, hx - 8, hy + 22], radius=10, fill=(225, 190, 150), outline=INK, width=3)
    d.rounded_rectangle([hx + 8, hy - 14, hx + 96, hy + 22], radius=10, fill=SAND, outline=INK, width=3)
    d.ellipse([hx - 26, hy - 26, hx + 26, hy + 26], fill=GOLD, outline=INK, width=3)
    d.line([(hx - 14, hy - 2), (hx + 14, hy - 2)], fill=CRIMSON, width=4)
    # container ship
    d.polygon([(W * 0.20, H * 0.88), (W * 0.82, H * 0.88), (W * 0.74, H * 0.96), (W * 0.28, H * 0.96)], fill=NAVY, outline=INK)
    for i in range(6):
        d.rectangle([W * 0.28 + i * 20, H * 0.84, W * 0.28 + 14 + i * 20, H * 0.89], fill=(230, 160, 50) if i % 2 else TEAL)
    # cranes
    for i in range(3):
        x = W * 0.78 + i * 20
        d.line([(x, H * 0.84), (x, H * 0.56)], fill=WHITE, width=4)
        d.line([(x, H * 0.56), (x + 32, H * 0.56)], fill=WHITE, width=4)
        d.line([(x + 26, H * 0.56), (x + 26, H * 0.66)], fill=WHITE, width=3)
    f = font(LATO_BLACK, 22)
    label(d, "CHINA–AUS", 14, H - 42, f, WHITE, NAVY, 8, 4)
    return finish(im, "art_13.png", w, h)


ART_FUNCS = [
    art_akvan, art_euuk, art_cop31, art_pentagon, art_rohingya, art_berlin,
    art_un, art_u17, art_nextdc, art_ofac, art_hormuz, art_kyiv, art_china_aus,
]


LEAD_SIZE = (309, 106)
SMALL_SIZE = (176, 82)


def build_all():
    LABEL_BOXES.clear()
    for i, fn in enumerate(ART_FUNCS):
        w, h = LEAD_SIZE if i < 3 else SMALL_SIZE
        fn(w, h)
    # padding audit: every graphic label must sit at least 4 px (2x) inside the box
    bad = []
    for s, (x0, y0, x1, y1), (W, H) in LABEL_BOXES:
        pad = min(x0, y0, W - x1, H - y1)
        if pad < 4:
            bad.append((s, pad))
    if bad:
        raise SystemExit(f"label padding failure: {bad}")
    print(f"art: {len(ART_FUNCS)} graphics, {len(LABEL_BOXES)} labels, min padding ok")


if __name__ == "__main__":
    build_all()

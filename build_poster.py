#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news front page (v2).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
baseline 4:4:4 JPEG, quality 90) and /tmp/news_1120_v2_300.png (300px proof).
"""
from __future__ import annotations

import base64
import html
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

import art
import mapgen

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
CHROME = "/usr/bin/google-chrome"
BUILD_TMP = Path("/tmp/news_1120_v2_build")
PROOF_300 = Path("/tmp/news_1120_v2_300.png")
JPEG_QUALITY = 90

# ---------------------------------------------------------------------------
# The edition. Every item happened, or was first reported, on Friday
# 20 November 2026 (UTC). Thursday 19 November stories are named in DATE CHECK.
# kind: hero (1-3) · grid (4-13) · brief (14-21). pin: (lon, lat) or None.
# ---------------------------------------------------------------------------
STORIES = [
    dict(n=1, kind="hero", region="EUROPE", place="Kyiv, Ukraine", src="AP · Reuters",
         headline="Russian Missiles Hit Three Kyiv Bridges",
         summary="Biggest strike on Dnipro crossings of the war kills at least 3 in Kyiv and 2 in Lviv, officials say.",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", place="Gopalpur, India", src="IMD · ETV Bharat",
         headline="Cyclone Akvan Makes Landfall in Odisha",
         summary="Crossed near Gopalpur with 70–80 km/h winds; 372,000 evacuated, no deaths reported so far.",
         art="art_02.png", pin=(84.9, 19.3)),
    dict(n=3, kind="hero", region="EUROPE", place="Brussels", src="BBC · Guardian · AFP",
         headline="Burnham Seeks Brexit Reset in Brussels",
         summary="UK–EU summit set to seal food, carbon and youth deals; EU says they hinge on student fees.",
         art="art_03.png", pin=(4.35, 50.85)),
    dict(n=4, kind="grid", region="GLOBAL/SCIENCE", place="Antalya", src="AFP · DW",
         headline="COP31 Final Day: No Deal in Sight",
         summary="Draft omits fossil fuels; talks look set for overtime.",
         art="art_04.png", pin=(30.7, 36.9)),
    dict(n=5, kind="grid", region="MIDDLE EAST", place="Riyadh", src="AP · Reuters",
         headline="Saudis Down Houthi Missile and Drones",
         summary="Coalition: 1 missile, 5 drones intercepted; Riyadh targeted.",
         art="art_05.png", pin=(46.7, 24.7)),
    dict(n=6, kind="grid", region="EUROPE", place="Rome", src="Repubblica · AP",
         headline="Italy Grinds to a Halt in General Strike",
         summary="24-hour CGIL walkout hits schools, hospitals, buses.",
         art="art_06.png", pin=(12.5, 41.9)),
    dict(n=7, kind="grid", region="OCEANIA", place="Shenzhen", src="ABC · Guardian",
         headline="Xi Hails ‘Full Turnaround’ With Australia",
         summary="Meets Albanese at APEC; PM says ties are ‘constructive’.",
         art="art_07.png", pin=(114.1, 22.5)),
    dict(n=8, kind="grid", region="AMERICAS", place="Brevard, Florida", src="NWS · CNN",
         headline="Florida Space Coast Braces for More Floods",
         summary="Rare ‘high risk’ rain alert; 100+ rescued since Thursday.",
         art="art_08.png", pin=(-80.7, 28.2)),
    dict(n=9, kind="grid", region="GLOBAL/SCIENCE", place="New York", src="SCR · Guardian",
         headline="UN Council Holds 9th Poll for Next Chief",
         summary="Colour-coded ballot; Grynspan led 7 of 8 earlier polls.",
         art="art_09.png", pin=(-74.0, 40.7)),
    dict(n=10, kind="grid", region="MIDDLE EAST", place="Hormuz", src="Al Jazeera",
         headline="US Memo: Blockade Lifts Gulf War-Risk Costs",
         summary="Agency warned premiums were rising, files show.",
         art="art_10.png", pin=(56.3, 26.6)),
    dict(n=11, kind="grid", region="AFRICA", place="Johannesburg", src="Reuters",
         headline="South Africa’s Rand Hits One-Year Low",
         summary="Coalition-talk jitters and a firm dollar weigh.",
         art="art_11.png", pin=(28.0, -26.2)),
    dict(n=12, kind="grid", region="ASIA-PACIFIC", place="Seoul", src="AP · Chosun",
         headline="S. Korea Has First Cholera Case in 10 Years",
         summary="Patient had not travelled; safe-water alert issued.",
         art="art_12.png", pin=(127.0, 37.5)),
    dict(n=13, kind="grid", region="AFRICA", place="Doha, Qatar", src="Africanews",
         headline="Morocco, Senegal, Mali Play at U-17 Cup",
         summary="Africa’s sides headline Friday’s World Cup fixtures.",
         art="art_13.png", pin=(51.5, 25.3)),
    dict(n=14, kind="brief", region="ASIA-PACIFIC", place="Tokyo",
         text="Japan’s core inflation rises to 2.2% in October", pin=(139.7, 35.7)),
    dict(n=15, kind="brief", region="ASIA-PACIFIC", place="Taipei",
         text="Taiwan flags 2,700 China-linked accounts to Meta", pin=(121.5, 25.0)),
    dict(n=16, kind="brief", region="EUROPE", place="Berlin",
         text="Gen Z protests in dozens of German cities", pin=(13.4, 52.5)),
    dict(n=17, kind="brief", region="AFRICA", place="Abidjan",
         text="AfDB: 22 African states in or near debt distress", pin=(-4.0, 5.3)),
    dict(n=18, kind="brief", region="OCEANIA", place="Melbourne",
         text="NextDC vows to keep datacentres away from homes", pin=(145.0, -37.8)),
    dict(n=19, kind="brief", region="OCEANIA", place="Sydney",
         text="David Jones gives 1,689 staff redundancy notices", pin=(151.2, -33.9)),
    dict(n=20, kind="brief", region="GLOBAL/SCIENCE", place="Space",
         text="BepiColombo due to enter Mercury orbit on Saturday", pin=None),
    dict(n=21, kind="brief", region="AMERICAS", place="Washington",
         text="Trump calls noon news conference after China trip", pin=(-77.0, 38.9)),
]

REGION_ORDER = ["ASIA-PACIFIC", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA", "GLOBAL/SCIENCE"]
REGION_COLORS = mapgen.REGION_COLORS
REGION_COUNTS = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGION_ORDER}

STATS = [
    ("3", "Kyiv bridges hit"),
    ("372,000", "Evacuated in Odisha"),
    ("100,000", "UK–EU youth visas/yr"),
    ("0", "Fossil fuels in COP draft"),
    ("24 hrs", "Italy general strike"),
    ("1,689", "David Jones job cuts"),
]

DECK = ("Russia hits three Kyiv bridges · Cyclone Akvan lands in Odisha · "
        "UK and EU meet to reset ties · COP31 hits its deadline")

DATE_LINE_1 = ("Every story on this page happened, or was first reported, on Friday 20 November 2026 (UTC). "
               "Official and disputed claims are attributed.")
DATE_LINE_2 = ("Left out as Thursday 19 Nov news: Trump–Xi–Putin declaration · ICJ Myanmar genocide ruling · "
               "Pentagon $48.3bn Iran tally · Canada budget vote · DOJ Alaska suit")


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def badge(s: dict, cls: str = "num") -> str:
    return f'<span class="{cls}" style="background:{REGION_COLORS[s["region"]]}">{s["n"]}</span>'


def card_html(s: dict) -> str:
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place">{esc(s['place'])} · {esc(s['src'])}</span></div>
      <h2><span class="hl">{esc(s['headline'])}</span></h2>
      <p class="summary"><span class="sum">{esc(s['summary'])}</span></p>
    </article>'''


def brief_html(s: dict) -> str:
    return f'''
      <div class="brief" data-story="{s['n']}" data-region="{esc(s['region'])}">
        {badge(s, 'bnum')}<p class="btext"><span class="bt"><b>{esc(s['place'])}</b> {esc(s['text'])}</span></p>
      </div>'''


def build_html() -> str:
    heroes = [s for s in STORIES if s["kind"] == "hero"]
    grid = [s for s in STORIES if s["kind"] == "grid"]
    briefs = [s for s in STORIES if s["kind"] == "brief"]
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in STORIES if s["pin"]]
    regions = "".join(
        f'<div class="rg" data-count="{REGION_COUNTS[r]}" style="background:{REGION_COLORS[r]}">'
        f'<span>{esc(r)}</span><b>{REGION_COUNTS[r]}</b></div>' for r in REGION_ORDER)
    stats = "".join(f'<div class="stat"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in STATS)
    left = "".join(brief_html(s) for s in briefs[:4])
    right = "".join(brief_html(s) for s in briefs[4:])
    total = len(STORIES)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'LibSerif'; src:url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'); font-weight:700; }}
@font-face {{ font-family:'LibSerif'; src:url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'); font-weight:700; font-style:italic; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Regular.ttf'); font-weight:400; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Bold.ttf'); font-weight:700; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf'); font-weight:900; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:1024px; height:1024px; overflow:hidden; background:#F6F1E6; }}
body {{ font-family:'LatoX', sans-serif; color:#141923; -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-variant-ligatures:none; }}
.page {{ width:1024px; height:1024px; padding:8px 18px 0 18px; }}
.kickerbar {{ height:15px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.11em; text-transform:uppercase; border-bottom:1.5px solid #141923; padding-bottom:3px; }}
.kickerbar .r {{ color:#9A1B1F; }}
.masthead {{ height:58px; margin-top:0; font:700 54px/56px 'LibSerif'; letter-spacing:-.02em; text-align:center; white-space:nowrap; }}
.deck {{ height:19px; font:italic 700 14.5px/19px 'LibSerif'; color:#9A1B1F; text-align:center; white-space:nowrap; }}
.regionbar {{ display:flex; gap:4px; height:22px; margin-top:4px; }}
.rg {{ flex:1; display:flex; align-items:center; justify-content:center; gap:6px; border-radius:3px; color:#FFF; white-space:nowrap; }}
.rg span {{ font:900 10.5px/1 'LatoX'; letter-spacing:.06em; }}
.rg b {{ font:900 13px/1 'LatoX'; }}
.stats {{ display:flex; height:48px; margin-top:5px; background:#EFE8D8; border:1.5px solid #141923; }}
.stat {{ flex:1; min-width:0; border-right:1px solid #BFB49C; padding:3px 9px; display:flex; flex-direction:column; justify-content:center; }}
.stat:last-child {{ border-right:none; }}
.stat b {{ font:700 21px/1 'LibSerif'; color:#9A1B1F; }}
.stat span {{ font:700 10px/12px 'LatoX'; height:12px; letter-spacing:.03em; text-transform:uppercase; margin-top:3px; white-space:nowrap; overflow:hidden; }}
.row {{ display:flex; gap:8px; margin-top:7px; }}
.row.grid {{ gap:7px; }}
.card {{ background:#FFFDF7; border:1px solid #141923; overflow:hidden; display:flex; flex-direction:column; }}
.card.hero {{ width:324px; height:254px; padding:6px; }}
.card.grid {{ width:192px; height:180px; padding:5px; }}
.art {{ display:block; outline:1px solid #141923; outline-offset:-1px; }}
.hero .art {{ width:310px; height:142px; }}
.grid .art {{ width:180px; height:88px; }}
.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:4px; }}
.grid .kicker {{ height:14px; margin-top:3px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; line-height:14px; }}
.place {{ font:700 10px/12px 'LatoX'; height:12px; letter-spacing:.04em; text-transform:uppercase; color:#5B4A3A; white-space:nowrap; overflow:hidden; }}
.grid .place {{ letter-spacing:.01em; }}
h2 {{ margin:3px 0 0 0; font:700 21px/1.04 'LibSerif'; letter-spacing:-.01em; text-wrap:balance; }}
.grid h2 {{ margin-top:2px; font-size:15.5px; line-height:1.03; letter-spacing:-.005em; }}
.summary {{ margin:3px 0 0 0; font:400 11.5px/1.25 'LatoX'; color:#222831; }}
.grid .summary {{ margin-top:3px; font-size:10.5px; line-height:1.22; }}
.bottom {{ display:flex; gap:14px; height:162px; margin-top:7px; }}
.mapcol {{ flex:0 0 300px; width:300px; }}
.secthead {{ height:16px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10.5px/1 'LatoX'; letter-spacing:.1em; text-transform:uppercase; border-bottom:1.5px solid #141923; padding-bottom:3px; }}
.secthead span {{ color:#9A1B1F; letter-spacing:.05em; }}
.mapbox {{ margin-top:2px; width:300px; height:144px; outline:1px solid #141923; outline-offset:-1px; overflow:hidden; }}
.mapsvg {{ display:block; }}
.briefcol {{ flex:1; min-width:0; }}
.briefgrid {{ display:flex; gap:14px; margin-top:2px; }}
.bcol {{ flex:1; min-width:0; }}
.brief {{ height:36px; display:flex; align-items:flex-start; gap:7px; padding-top:3px; border-bottom:1px solid #D6CCB6; }}
.bcol .brief:last-child {{ border-bottom:none; }}
.bnum {{ flex:0 0 17px; width:17px; height:17px; border-radius:50%; color:#FFF; font:900 10.5px/17px 'LatoX'; text-align:center; margin-top:1px; }}
.btext {{ margin:0; font:700 13.5px/15px 'LibSerif'; text-wrap:balance; }}
.btext b {{ color:#9A1B1F; text-transform:uppercase; font:900 11px/15px 'LatoX'; letter-spacing:.04em; margin-right:2px; }}
.datecheck {{ margin-top:5px; height:34px; border:2px solid #9A1B1F; background:#EFE8D8; padding:3px 8px 0 8px; overflow:hidden; }}
.dc {{ font:700 10.2px/13px 'LatoX'; white-space:nowrap; }}
.dc.two {{ font-weight:400; }}
.dc b {{ color:#9A1B1F; letter-spacing:.06em; }}
</style></head>
<body><div class="page">
  <div class="kickerbar"><div>The World Canvas · One-day edition</div><div class="r">{total} stories · 7 regions · Friday 20 Nov 2026 (UTC)</div></div>
  <div class="masthead">Friday, 20 November 2026</div>
  <div class="deck">{esc(DECK)}</div>
  <div class="regionbar">{regions}</div>
  <div class="stats">{stats}</div>
  <div class="row heroes">{''.join(card_html(s) for s in heroes)}</div>
  <div class="row grid">{''.join(card_html(s) for s in grid[:5])}</div>
  <div class="row grid">{''.join(card_html(s) for s in grid[5:])}</div>
  <div class="bottom">
    <div class="mapcol">
      <div class="secthead"><div>Where it happened</div><span>Pins = story numbers</span></div>
      <div class="mapbox">{mapgen.svg(pins)}</div>
    </div>
    <div class="briefcol">
      <div class="secthead"><div>Also on Friday 20 November</div><span>14–21</span></div>
      <div class="briefgrid"><div class="bcol">{left}</div><div class="bcol">{right}</div></div>
    </div>
  </div>
  <div class="datecheck">
    <div class="dc"><b>DATE CHECK ✓</b>&nbsp; {esc(DATE_LINE_1)}</div>
    <div class="dc two">{esc(DATE_LINE_2)}</div>
  </div>
</div></body></html>'''


AUDIT_JS = r'''() => {
  const R = el => { const r = el.getBoundingClientRect(); return {x:r.x, y:r.y, w:r.width, h:r.height, right:r.right, bottom:r.bottom}; };
  const ov = (a, b) => a.x < b.right - 0.5 && b.x < a.right - 0.5 && a.y < b.bottom - 0.5 && b.y < a.bottom - 0.5;
  const doc = [document.documentElement.scrollWidth, document.documentElement.scrollHeight];
  const cards = [...document.querySelectorAll('.card')];
  const briefs = [...document.querySelectorAll('.brief')];
  const stories = [...cards, ...briefs].map(e => +e.dataset.story);
  const regionCounts = [...document.querySelectorAll('.rg')].map(e => +e.dataset.count);
  const regionTagged = {};
  [...cards, ...briefs].forEach(e => regionTagged[e.dataset.region] = (regionTagged[e.dataset.region] || 0) + 1);

  const overflows = [];
  document.querySelectorAll('.page,.kickerbar,.masthead,.deck,.regionbar,.rg,.stats,.stat,.stat span,.card,.kicker,.place,.bottom,.mapbox,.briefcol,.brief,.btext,.datecheck,.dc,.secthead').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });

  // every block inside a card, in order, must not overlap the next one or leave the card
  const blockOverlaps = [];
  cards.forEach(c => {
    const cr = R(c);
    const els = ['.art', '.kicker', 'h2', '.summary'].map(s => c.querySelector(s));
    els.forEach((e, i) => {
      const r = R(e);
      if (r.bottom > cr.bottom - 1 + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: e.className || e.tagName, why: 'leaves card'});
      if (i < els.length - 1 && r.bottom > R(els[i + 1]).y + 0.5) blockOverlaps.push({card: c.dataset.story, a: e.className || e.tagName, b: els[i + 1].className || els[i + 1].tagName});
    });
    // text line boxes must also stay inside
    ['.hl', '.sum', '.place'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom - 1 + 0.5) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped'}); });
  });
  briefs.forEach(b => { const br = R(b), t = R(b.querySelector('.bt')); if (t.bottom > br.bottom + 0.5 || t.right > br.right + 0.5) blockOverlaps.push({brief: b.dataset.story, why: 'text clipped'}); });

  const bands = ['.kickerbar', '.masthead', '.deck', '.regionbar', '.stats', '.row.heroes', '.row.grid', '.bottom', '.datecheck'];
  const bandEls = bands.flatMap(s => [...document.querySelectorAll(s)]);
  const bandOverlaps = [];
  for (let i = 0; i < bandEls.length - 1; i++) { const a = R(bandEls[i]), b = R(bandEls[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bandEls[i].className, b: bandEls[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const last = R(document.querySelector('.datecheck'));
  const cardOverlaps = [];
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox')];
  boxes.forEach((a, i) => boxes.forEach((b, j) => { if (j > i && ov(R(a), R(b))) cardOverlaps.push([a.dataset.story || 'map', b.dataset.story || 'map']); }));

  // map pins: no two pin discs may overlap, all inside the map
  const pins = [...document.querySelectorAll('.pin circle')].map(c => ({n: c.parentNode.dataset.pin, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')}));
  const pinOverlaps = [];
  pins.forEach((a, i) => pins.forEach((b, j) => { if (j > i && Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r) pinOverlaps.push([a.n, b.n]); }));
  const pinsOutside = pins.filter(p => p.x - p.r < 0 || p.y - p.r < 0 || p.x + p.r > 300 || p.y + p.r > 144).map(p => p.n);

  const lines = el => { const rs = [...el.getClientRects()]; return new Set(rs.map(r => Math.round(r.top))).size; };
  const headlineLines = cards.map(c => lines(c.querySelector('.hl')));
  const summaryLines = cards.map(c => lines(c.querySelector('.sum')));
  const briefLines = briefs.map(b => lines(b.querySelector('.bt')));

  // font floor: every element that owns visible text
  let minHtml = 99, minHtmlText = '', minSvg = 99;
  document.querySelectorAll('body *').forEach(el => {
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (el instanceof SVGElement) { minSvg = Math.min(minSvg, fs); return; }
    if (fs < minHtml) { minHtml = fs; minHtmlText = el.textContent.trim().slice(0, 30); }
  });
  const imagesLoaded = [...document.images].every(i => i.complete && i.naturalWidth > 0);
  const artSizes = [...document.querySelectorAll('.art')].map(i => [i.naturalWidth, i.naturalHeight, Math.round(R(i).w), Math.round(R(i).h)]);
  return {doc, stories, regionCounts, regionTagged, overflows, blockOverlaps, bandOverlaps, cardOverlaps,
          pinCount: pins.length, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          minHtml, minHtmlText, minSvg, imagesLoaded, artSizes, pageBottom: last.bottom,
          heroH: cards.slice(0, 3).map(c => R(c).h), gridH: cards.slice(3).map(c => R(c).h)};
}'''


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    if sorted(a["stories"]) != list(range(1, n + 1)):
        f.append(f"stories {a['stories']}")
    if sum(a["regionCounts"]) != n or len(a["regionCounts"]) != 7 or min(a["regionCounts"]) < 2:
        f.append(f"region counts {a['regionCounts']}")
    if any(a["regionTagged"].get(r, 0) != REGION_COUNTS[r] for r in REGION_ORDER):
        f.append(f"region tags {a['regionTagged']} != {REGION_COUNTS}")
    for k in ("overflows", "blockOverlaps", "bandOverlaps", "cardOverlaps", "pinOverlaps", "pinsOutside"):
        if a[k]:
            f.append(f"{k}: {a[k]}")
    if a["pinCount"] != sum(1 for s in STORIES if s["pin"]):
        f.append(f"pins {a['pinCount']}")
    for k in ("headlineLines", "summaryLines", "briefLines"):
        if max(a[k]) > 2:
            f.append(f"{k}: {a[k]}")
    if a["minHtml"] < 10:
        f.append(f"html font {a['minHtml']} ({a['minHtmlText']})")
    if a["minSvg"] < 9:
        f.append(f"svg font {a['minSvg']}")
    if not a["imagesLoaded"]:
        f.append("image failed to load")
    if any(nw != w * 1 or nh != h for nw, nh, w, h in a["artSizes"]):
        f.append(f"art scaled in page: {a['artSizes']}")
    if a["pageBottom"] > 1022:
        f.append(f"page bottom {a['pageBottom']}")
    return f


def main() -> int:
    art.build_all()
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in STORIES if s["pin"]]
    mapgen.check(pins)
    BUILD_TMP.mkdir(parents=True, exist_ok=True)
    html_path = BUILD_TMP / "poster.html"
    html_path.write_text(build_html(), encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            args=["--font-render-hinting=none", "--disable-lcd-text", "--disable-gpu",
                  "--force-device-scale-factor=1", "--hide-scrollbars"])
        page = browser.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=1)
        page.goto(html_path.as_uri())
        page.evaluate("document.fonts.ready.then(() => true)")
        page.wait_for_timeout(400)
        a = page.evaluate(AUDIT_JS)
        failures = check_audit(a)
        print(json.dumps({k: v for k, v in a.items() if k not in ("artSizes",)}, ensure_ascii=False)[:3000])
        if failures:
            print("\nAUDIT FAILURES:")
            for x in failures:
                print(" -", x)
            browser.close()
            return 1
        page.screenshot(path=str(ASSETS / "poster.png"))
        browser.close()

    im = Image.open(ASSETS / "poster.png").convert("RGB")
    im.save(BASE / "entry.png", format="JPEG", quality=JPEG_QUALITY, subsampling=0,
            optimize=True, progressive=False)
    im.resize((300, 300), Image.LANCZOS).save(PROOF_300)
    size = (BASE / "entry.png").stat().st_size
    print(f"\nAUDIT OK · {len(STORIES)} stories · regions {REGION_COUNTS} · min html font {a['minHtml']}px · "
          f"min svg font {a['minSvg']}px · pins {a['pinCount']}")
    print(f"entry.png: {size} bytes ({size / 1024:.1f} KiB)")
    if size >= 1_048_576:
        print("ERROR: entry.png is over 1 MiB")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

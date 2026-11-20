#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news front page (v3).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
baseline 4:4:4 JPEG, the highest quality that fits MAX_BYTES) and
/tmp/news_1120_v3_300.png (300px proof).
"""
from __future__ import annotations

import base64
import html
import io
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
BUILD_TMP = Path("/tmp/news_1120_v3_build")
PROOF_300 = Path("/tmp/news_1120_v3_300.png")
MAX_BYTES = 420_000   # entry.png budget (420 kB)
QUALITIES = range(92, 79, -1)

# ---------------------------------------------------------------------------
# The edition. Every item happened, or was first reported, on Friday
# 20 November 2026 (UTC). Items dated Thursday 19 November or earlier are
# named in DATE CHECK. kind: hero (1-3) · grid (4-13) · brief (14-40).
# cert: "v" = official / confirmed on the record, "r" = reported or claimed.
# pin: (lon, lat) or None.
# ---------------------------------------------------------------------------
STORIES = [
    # --- lead stories -------------------------------------------------------
    dict(n=1, kind="hero", region="EUROPE", beat="Conflict", cert="v", place="Kyiv, Ukraine",
         src="Reuters · AP · Kyiv Independent",
         headline="Russian Missiles Hit Three Kyiv Bridges",
         summary="Strikes damage three Dnipro crossings; 3 killed in Kyiv and at least 8 nationwide, officials say.",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", beat="Weather", cert="v", place="Gopalpur, India",
         src="IMD · The Hindu · NDTV",
         headline="Cyclone Akvan Makes Landfall in Odisha",
         summary="Crossed near Gopalpur and weakened to a deep depression; 372,000 evacuated, no deaths reported, the state says.",
         art="art_02.png", pin=(84.9, 19.3)),
    dict(n=3, kind="hero", region="ASIA-PACIFIC", beat="Markets", cert="v", place="Taipei · Seoul · Tokyo",
         src="Reuters · Al Jazeera · AA",
         headline="Asia’s Chip Stocks Crash in AI Sell-Off",
         summary="Taiex −6.23%, Kospi −5.2%, Nikkei −5.1% as Anthropic’s Nasdaq debut fails to calm AI fears; worst week since 2020.",
         art="art_03.png", pin=(121.5, 25.0)),
    # --- illustrated cards --------------------------------------------------
    dict(n=4, kind="grid", region="EUROPE", beat="Diplomacy", cert="v", place="Brussels", src="Guardian",
         headline="UK and EU Seal Food, Carbon, Youth Deals",
         summary="100,000 youth places a year each way.",
         art="art_04.png", pin=(4.35, 50.85)),
    dict(n=5, kind="grid", region="GLOBAL/SCIENCE", beat="Climate", cert="v", place="Antalya", src="AP · DW",
         headline="COP31 Final Day Ends Without a Deal",
         summary="Draft omits fossil fuels; overtime set.",
         art="art_05.png", pin=(30.7, 36.9)),
    dict(n=6, kind="grid", region="EUROPE", beat="Labour", cert="v", place="Rome", src="Reuters · Repubblica",
         headline="Italy Grinds to a Halt in General Strike",
         summary="CGIL’s 24-hour walkout over wages.",
         art="art_06.png", pin=(12.5, 41.9)),
    dict(n=7, kind="grid", region="AMERICAS", beat="US politics", cert="v", place="Washington", src="CBS · ToI",
         headline="Trump Hails Trip, Calls Iran Offer Unacceptable",
         summary="Vance and Rubio flank him at presser.",
         art="art_07.png", pin=(-77.0, 38.9)),
    dict(n=8, kind="grid", region="GLOBAL/SCIENCE", beat="UN", cert="v", place="New York", src="SCR · Guardian",
         headline="UN Council Holds 9th Poll for Next Chief",
         summary="Colour-coded: P5 red, E10 green.",
         art="art_08.png", pin=(-74.0, 40.7)),
    dict(n=9, kind="grid", region="MIDDLE EAST", beat="Conflict", cert="v", place="Riyadh", src="AP · Reuters",
         headline="Saudis Down Houthi Missile and Drones",
         summary="Coalition says it also hit arms routes.",
         art="art_09.png", pin=(46.7, 24.7)),
    dict(n=10, kind="grid", region="AMERICAS", beat="Weather", cert="v", place="Brevard, Florida", src="CBS",
         headline="Record Floods Swamp Florida’s Space Coast",
         summary="100+ water rescues; St Johns at record.",
         art="art_10.png", pin=(-80.7, 28.2)),
    dict(n=11, kind="grid", region="OCEANIA", beat="Diplomacy", cert="v", place="Shenzhen", src="ABC · Guardian",
         headline="Xi Hails ‘Full Turnaround’ With Australia",
         summary="Praises Albanese at post-APEC talks.",
         art="art_11.png", pin=(114.1, 22.5)),
    dict(n=12, kind="grid", region="AFRICA", beat="Migration", cert="v", place="Dakar", src="IOM · ThisDay",
         headline="West Africa Adopts Dakar Migration Roadmap",
         summary="Declaration sets 2027–28 priorities.",
         art="art_12.png", pin=(-17.4, 14.7)),
    dict(n=13, kind="grid", region="GLOBAL/SCIENCE", beat="Space", cert="v", place="Space", src="ESA · JAXA",
         headline="BepiColombo Set to Enter Mercury Orbit",
         summary="Capture due Saturday after 8-year trip.",
         art="art_13.png", pin=None),
    # --- news wire: Europe --------------------------------------------------
    dict(n=14, kind="brief", region="EUROPE", beat="Conflict", cert="v", place="Warsaw", src="Tusk",
         text="Poland calls missile incursion ‘intentional provocation’", pin=(21.0, 52.2)),
    dict(n=15, kind="brief", region="EUROPE", beat="Diplomacy", cert="v", place="Paris", src="Barrot",
         text="France seeks UN Council meeting after embassies hit in Kyiv", pin=(2.35, 48.85)),
    dict(n=16, kind="brief", region="EUROPE", beat="Protest", cert="r", place="Berlin", src="organisers",
         text="Gen Z protests called in 73 German cities", pin=(13.4, 52.5)),
    # --- Asia-Pacific -------------------------------------------------------
    dict(n=17, kind="brief", region="ASIA-PACIFIC", beat="Economy", cert="v", place="Tokyo", src="MIC",
         text="Japan’s core inflation rises to 2.2% in October", pin=(139.7, 35.7)),
    dict(n=18, kind="brief", region="ASIA-PACIFIC", beat="Health", cert="v", place="Changwon", src="KDCA",
         text="S. Korea’s first domestic cholera case in 10 years", pin=(128.7, 35.2)),
    dict(n=19, kind="brief", region="ASIA-PACIFIC", beat="Diplomacy", cert="v", place="Shenzhen", src="Xinhua",
         text="Xi meets Malaysia’s Anwar for fourth bilateral talks", pin=(114.1, 22.5)),
    dict(n=20, kind="brief", region="ASIA-PACIFIC", beat="Elections", cert="r", place="Taipei", src="Reuters",
         text="Taiwan flags 2,700 China-linked accounts to Meta", pin=(121.5, 25.0)),
    dict(n=21, kind="brief", region="ASIA-PACIFIC", beat="Markets", cert="v", place="Singapore", src="SGX",
         text="STI sheds 2.1% to close at 4,975, below the 5,000 mark", pin=(103.8, 1.35)),
    # --- Americas -----------------------------------------------------------
    dict(n=22, kind="brief", region="AMERICAS", beat="Tech", cert="r", place="Washington", src="House report",
         text="SpaceX’s Cursor may drop Chinese AI models", pin=(-77.0, 38.9)),
    dict(n=23, kind="brief", region="AMERICAS", beat="Markets", cert="v", place="New York", src="Reuters",
         text="Nasdaq slides over 3% as Anthropic falls toward IPO price", pin=(-74.0, 40.7)),
    dict(n=24, kind="brief", region="AMERICAS", beat="Economy", cert="v", place="São Paulo", src="Rio Times",
         text="B3 exchange shut for Black Consciousness Day holiday", pin=(-46.6, -23.5)),
    dict(n=25, kind="brief", region="AMERICAS", beat="Indigenous", cert="r", place="Brazil", src="video",
         text="About 20 isolated Awá people approach a government team", pin=(-46.0, -4.0)),
    dict(n=26, kind="brief", region="AMERICAS", beat="Trade", cert="r", place="Ottawa", src="Global News",
         text="‘Multiple issues’ open in Canada–US trade talks", pin=(-75.7, 45.4)),
    # --- Middle East --------------------------------------------------------
    dict(n=27, kind="brief", region="MIDDLE EAST", beat="Security", cert="v", place="Jurf al-Sakhar", src="officials",
         text="Iraqi forces enter Kataib Hezbollah stronghold", pin=(44.2, 32.9)),
    dict(n=28, kind="brief", region="MIDDLE EAST", beat="Shipping", cert="r", place="Gulf", src="Al Jazeera",
         text="US memo warned Iran blockade lifts war-risk premiums", pin=(56.3, 26.6)),
    dict(n=29, kind="brief", region="MIDDLE EAST", beat="Politics", cert="v", place="Tel Aviv", src="ToI",
         text="Eisenkot vows ‘emergency’ government if broad coalition fails", pin=(34.8, 32.1)),
    # --- Africa -------------------------------------------------------------
    dict(n=30, kind="brief", region="AFRICA", beat="Markets", cert="v", place="Johannesburg", src="Reuters",
         text="Rand touches one-year low on coalition jitters", pin=(28.0, -26.2)),
    dict(n=31, kind="brief", region="AFRICA", beat="Economy", cert="v", place="Abidjan", src="AfDB",
         text="22 African states in or at high risk of debt distress", pin=(-4.0, 5.3)),
    dict(n=32, kind="brief", region="AFRICA", beat="Sport", cert="v", place="Doha", src="Africanews",
         text="Morocco, Senegal, Mali play Friday U-17 World Cup games", pin=(51.5, 25.3)),
    dict(n=33, kind="brief", region="AFRICA", beat="Conflict", cert="r", place="Tigray", src="Fana",
         text="200+ Tigrayan fighters surrender to Ethiopian army", pin=(38.5, 14.0)),
    dict(n=34, kind="brief", region="AFRICA", beat="Migration", cert="r", place="Moyale", src="People Daily",
         text="Ethiopia unrest drives 50,000 into Kenya, report says", pin=(39.05, 3.5)),
    # --- Oceania ------------------------------------------------------------
    dict(n=35, kind="brief", region="OCEANIA", beat="Business", cert="v", place="Sydney", src="receivers",
         text="David Jones gives 1,689 staff redundancy notices", pin=(151.2, -33.9)),
    dict(n=36, kind="brief", region="OCEANIA", beat="Travel", cert="v", place="Adelaide", src="ABF",
         text="Digital arrival declaration pilot expands to Adelaide", pin=(138.6, -34.9)),
    dict(n=37, kind="brief", region="OCEANIA", beat="Travel", cert="v", place="Sydney", src="Trip.com",
         text="Trip.Best launches 2027 rankings, adding Oceania", pin=(151.2, -33.9)),
    dict(n=38, kind="brief", region="OCEANIA", beat="Crime", cert="v", place="Canberra", src="AFP",
         text="Joint AFP probe nets 660kg of cocaine, 5 arrests in Brazil", pin=(149.1, -35.3)),
    dict(n=39, kind="brief", region="OCEANIA", beat="Sport", cert="v", place="Wellington", src="RNZ",
         text="Nicholls 175 not out as NZ make 368 v India", pin=(174.8, -41.3)),
    # --- Global / science ---------------------------------------------------
    dict(n=40, kind="brief", region="GLOBAL/SCIENCE", beat="Wildlife", cert="v", place="Amazon", src="WCS",
         text="25 years of camera traps show how rare the bush dog is", pin=(-68.0, -8.0)),
]

REGION_ORDER = ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA", "GLOBAL/SCIENCE"]
REGION_COLORS = mapgen.REGION_COLORS
REGION_COUNTS = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGION_ORDER}
BEATS = sorted({s["beat"] for s in STORIES})
CERT = {"v": ("●", "Confirmed / on the record"), "r": ("◐", "Reported / claimed")}

STATS = [
    ("3", "Kyiv bridges hit"),
    ("372,000", "Evacuated in Odisha"),
    ("−6.23%", "Taiex close"),
    ("100,000", "UK–EU youth places/yr"),
    ("9th", "UN straw poll"),
    ("1,689", "David Jones notices"),
]

DECK = ("Missiles hit Kyiv’s bridges · Cyclone Akvan lands in Odisha · "
        "Asia’s chip stocks crash · UK and EU seal deals · COP31 runs over")

TIMELINE = [
    ("Night", "Kyiv bridges struck"),
    ("02Z", "Akvan landfall"),
    ("05Z", "Taiex shuts −6.23%"),
    ("12Z", "France seeks UNSC"),
    ("14Z", "UK–EU deals sealed"),
    ("17Z", "UN poll · Trump presser"),
    ("Eve", "COP31 overtime"),
    ("Sat", "BepiColombo capture"),
]

DATE_LINE_1 = ("Every story here happened, or was first reported, on Friday 20 November 2026 (UTC); "
               "official and disputed figures are attributed.  ● confirmed / on the record   ◐ reported / claimed")
DATE_LINE_2 = ("Left out as Thursday 19 Nov news: Trump–Xi–Putin declaration · ICJ Myanmar genocide ruling · "
               "Pentagon $48.3bn Iran tally · Canada budget vote · DOJ Alaska suit · IEA $40bn pipeline report")
DATE_LINE_3 = ("Also dropped as earlier news: Brazil’s $1bn FX sale (19 Nov) · Jepchirchir ban (19 Nov) · "
               "Italy’s €805m Meta fine (14 Nov) · Colombia hippo cull (18 Nov) · Pope Leo’s Peru farewell (16 Nov)")


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def badge(s: dict, cls: str = "num") -> str:
    return f'<span class="{cls}" style="background:{REGION_COLORS[s["region"]]}">{s["n"]}</span>'


def cert(s: dict) -> str:
    g, label = CERT[s["cert"]]
    return f'<span class="ct ct-{s["cert"]}" title="{g} {label}"></span>'


def card_html(s: dict) -> str:
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place">{esc(s['place'])} · {esc(s['src'])}</span>{cert(s)}</div>
      <h2><span class="hl">{esc(s['headline'])}</span></h2>
      <p class="summary"><span class="sum">{esc(s['summary'])}</span></p>
    </article>'''


def brief_html(s: dict) -> str:
    return f'''
      <div class="brief" data-story="{s['n']}" data-region="{esc(s['region'])}">
        {badge(s, 'bnum')}<p class="btext"><span class="bt"><b>{esc(s['place'])}</b> {esc(s['text'])} <i>{esc(s['src'])}</i>&nbsp;{cert(s)}</span></p>
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
    per = -(-len(briefs) // 3)
    cols = "".join(f'<div class="bcol">{"".join(brief_html(s) for s in briefs[i:i + per])}</div>'
                   for i in range(0, len(briefs), per))
    tl = "".join(f'<div class="tli"><b>{esc(t)}</b><span>{esc(e)}</span></div>' for t, e in TIMELINE)
    total = len(STORIES)
    first_brief, last_brief = briefs[0]["n"], briefs[-1]["n"]
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
@font-face {{ font-family:'LibSerif'; src:url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'); font-weight:700; }}
@font-face {{ font-family:'LibSerif'; src:url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'); font-weight:700; font-style:italic; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Regular.ttf'); font-weight:400; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Italic.ttf'); font-weight:400; font-style:italic; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Bold.ttf'); font-weight:700; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf'); font-weight:900; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:1024px; height:1024px; overflow:hidden; background:#F6F1E6; }}
body {{ font-family:'LatoX', sans-serif; color:#141923; -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-variant-ligatures:none; }}
.page {{ width:1024px; height:1024px; padding:7px 18px 0 18px; }}
.kickerbar {{ height:15px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.1em; text-transform:uppercase; border-bottom:1.5px solid #141923; padding-bottom:3px; white-space:nowrap; }}
.kickerbar .r {{ color:#9A1B1F; }}
.masthead {{ height:48px; font:700 46px/46px 'LibSerif'; letter-spacing:-.02em; text-align:center; white-space:nowrap; }}
.deck {{ height:18px; font:italic 700 14px/18px 'LibSerif'; color:#9A1B1F; text-align:center; white-space:nowrap; }}
.regionbar {{ display:flex; gap:4px; height:21px; margin-top:4px; }}
.rg {{ flex:1; display:flex; align-items:center; justify-content:center; gap:6px; border-radius:3px; color:#FFF; white-space:nowrap; }}
.rg span {{ font:900 10.5px/1 'LatoX'; letter-spacing:.06em; }}
.rg b {{ font:900 13px/1 'LatoX'; }}
.stats {{ display:flex; height:42px; margin-top:4px; background:#EFE8D8; border:1.5px solid #141923; }}
.stat {{ flex:1; min-width:0; border-right:1px solid #BFB49C; padding:2px 9px; display:flex; flex-direction:column; justify-content:center; }}
.stat:last-child {{ border-right:none; }}
.stat b {{ font:700 20px/1 'LibSerif'; color:#9A1B1F; }}
.stat span {{ font:700 10px/12px 'LatoX'; height:12px; letter-spacing:.03em; text-transform:uppercase; margin-top:2px; white-space:nowrap; overflow:hidden; }}
.row {{ display:flex; gap:8px; margin-top:6px; }}
.row.grid {{ gap:7px; }}
.card {{ background:#FFFDF7; border:1px solid #141923; overflow:hidden; display:flex; flex-direction:column; }}
.card.hero {{ width:324px; height:232px; padding:6px; }}
.card.grid {{ width:192px; height:150px; padding:5px; }}
.art {{ display:block; outline:1px solid #141923; outline-offset:-1px; }}
.hero .art {{ width:310px; height:120px; }}
.grid .art {{ width:180px; height:72px; }}
.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:4px; }}
.grid .kicker {{ height:14px; margin-top:3px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; line-height:14px; }}
.place {{ flex:1; min-width:0; font:700 10px/12px 'LatoX'; height:12px; letter-spacing:.04em; text-transform:uppercase; color:#5B4A3A; white-space:nowrap; overflow:hidden; }}
.grid .place {{ letter-spacing:0; }}
.ct {{ display:inline-block; flex:0 0 auto; width:7px; height:7px; border-radius:50%; background:#1D6F6A; border:1.3px solid #1D6F6A; vertical-align:0; }}
.ct-r {{ background:linear-gradient(90deg, #A85F12 50%, #FFFDF7 50%); border-color:#A85F12; }}
h2 {{ margin:3px 0 0 0; font:700 21px/1.04 'LibSerif'; letter-spacing:-.01em; text-wrap:balance; }}
.grid h2 {{ margin-top:2px; font-size:15.5px; line-height:1.03; letter-spacing:-.005em; }}
.summary {{ margin:3px 0 0 0; font:400 11.5px/1.25 'LatoX'; color:#222831; }}
.grid .summary {{ margin-top:2px; font-size:10.5px; line-height:1.22; white-space:nowrap; }}
.bottom {{ display:flex; gap:14px; height:252px; margin-top:6px; }}
.mapcol {{ flex:0 0 300px; width:300px; }}
.secthead {{ height:16px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10.5px/1 'LatoX'; letter-spacing:.1em; text-transform:uppercase; border-bottom:1.5px solid #141923; padding-bottom:3px; white-space:nowrap; }}
.secthead span {{ color:#9A1B1F; letter-spacing:.05em; }}
.mapbox {{ margin-top:2px; width:300px; height:{mapgen.H}px; outline:1px solid #141923; outline-offset:-1px; overflow:hidden; }}
.mapsvg {{ display:block; }}
.tlhead {{ margin-top:9px; }}
.timeline {{ display:grid; grid-template-columns:1fr 1fr; grid-template-rows:repeat(4, 17px); grid-auto-flow:column; column-gap:10px; margin-top:3px; }}
.tli {{ height:17px; display:flex; gap:5px; align-items:center; white-space:nowrap; overflow:hidden; border-bottom:1px dotted #BFB49C; }}
.tli b {{ flex:0 0 34px; font:900 10px/14px 'LatoX'; color:#9A1B1F; }}
.tli span {{ font:700 10px/14px 'LatoX'; }}
.briefcol {{ flex:1; min-width:0; }}
.briefgrid {{ display:flex; gap:12px; margin-top:1px; }}
.bcol {{ flex:1; min-width:0; }}
.brief {{ height:26px; display:flex; align-items:flex-start; gap:5px; padding-top:1px; border-bottom:1px solid #D6CCB6; }}
.bcol .brief:last-child {{ border-bottom:none; }}
.bnum {{ flex:0 0 16px; width:16px; height:16px; border-radius:50%; color:#FFF; font:900 9.5px/16px 'LatoX'; text-align:center; margin-top:3px; }}
.btext {{ margin:0; font:700 10.5px/11.5px 'LatoX'; letter-spacing:-.005em; }}
.btext b {{ color:#9A1B1F; text-transform:uppercase; font:900 10px/11.5px 'LatoX'; letter-spacing:.03em; margin-right:1px; }}
.btext i {{ font:italic 400 10px/11.5px 'LatoX'; color:#5B4A3A; }}
.btext .ct {{ vertical-align:0; }}
.datecheck {{ margin-top:7px; height:45px; border:2px solid #9A1B1F; background:#EFE8D8; padding:2px 8px 0 8px; overflow:hidden; }}
.dc {{ font:700 10px/13px 'LatoX'; white-space:nowrap; }}
.dc.two {{ font-weight:400; }}
.dc b {{ color:#9A1B1F; letter-spacing:.06em; }}
.dc .ct {{ vertical-align:0; margin-left:6px; }}
</style></head>
<body><div class="page">
  <div class="kickerbar"><div>The World Canvas · Friday, 20 November 2026 (UTC)</div><div class="r">{total} stories · 7 regions · {len(BEATS)} beats · every claim sourced</div></div>
  <div class="masthead">Friday, 20 November 2026</div>
  <div class="deck">{esc(DECK)}</div>
  <div class="regionbar">{regions}</div>
  <div class="stats">{stats}</div>
  <div class="row heroes">{''.join(card_html(s) for s in heroes)}</div>
  <div class="row grid">{''.join(card_html(s) for s in grid[:5])}</div>
  <div class="row grid">{''.join(card_html(s) for s in grid[5:])}</div>
  <div class="bottom">
    <div class="briefcol">
      <div class="secthead"><div>The wire · also on Friday 20 November</div><span>{first_brief}–{last_brief} · <i class="ct ct-v"></i> confirmed &nbsp;<i class="ct ct-r"></i> reported</span></div>
      <div class="briefgrid">{cols}</div>
    </div>
    <div class="mapcol">
      <div class="secthead"><div>Where it happened</div><span>{len(pins)} pins = story nos.</span></div>
      <div class="mapbox">{mapgen.svg(pins)}</div>
      <div class="secthead tlhead"><div>Friday, in UTC</div><span>13 · BepiColombo in space</span></div>
      <div class="timeline">{tl}</div>
    </div>
  </div>
  <div class="datecheck">
    <div class="dc"><b>DATE CHECK ✓</b>&nbsp; {esc(DATE_LINE_1).replace('●', '<span class="ct ct-v"></span>').replace('◐', '<span class="ct ct-r"></span>')}</div>
    <div class="dc two">{esc(DATE_LINE_2)}</div>
    <div class="dc two">{esc(DATE_LINE_3)}</div>
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
  document.querySelectorAll('.page,.kickerbar,.masthead,.deck,.regionbar,.rg,.stats,.stat,.stat span,.card,.kicker,.place,.bottom,.mapbox,.briefcol,.bcol,.brief,.btext,.datecheck,.dc,.secthead,.tli,.timeline,.mapcol,.summary').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });

  const blockOverlaps = [];
  cards.forEach(c => {
    const cr = R(c);
    const els = ['.art', '.kicker', 'h2', '.summary'].map(s => c.querySelector(s));
    els.forEach((e, i) => {
      const r = R(e);
      if (r.bottom > cr.bottom - 1 + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: e.className || e.tagName, why: 'leaves card'});
      if (i < els.length - 1 && r.bottom > R(els[i + 1]).y + 0.5) blockOverlaps.push({card: c.dataset.story, a: e.className || e.tagName, b: els[i + 1].className || els[i + 1].tagName});
    });
    ['.hl', '.sum', '.place'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom - 1 + 0.5 || r.right > cr.right - 4) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped'}); });
  });
  briefs.forEach(b => { const br = R(b), t = R(b.querySelector('.bt')); if (t.bottom > br.bottom + 0.5 || t.right > br.right + 0.5) blockOverlaps.push({brief: b.dataset.story, why: 'text clipped'}); });
  [...document.querySelectorAll('.tli')].forEach(t => { const r = R(t), s = R(t.querySelector('span')); if (s.right > r.right + 0.5) blockOverlaps.push({tl: t.textContent, why: 'clipped'}); });
  const mc = R(document.querySelector('.mapcol'));
  [...document.querySelectorAll('.mapcol > *')].forEach(e => { if (R(e).bottom > mc.bottom + 0.5) blockOverlaps.push({el: e.className, why: 'leaves map column'}); });

  const bands = ['.kickerbar', '.masthead', '.deck', '.regionbar', '.stats', '.row.heroes', '.row.grid', '.bottom', '.datecheck'];
  const bandEls = bands.flatMap(s => [...document.querySelectorAll(s)]);
  const bandOverlaps = [];
  for (let i = 0; i < bandEls.length - 1; i++) { const a = R(bandEls[i]), b = R(bandEls[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bandEls[i].className, b: bandEls[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const last = R(document.querySelector('.datecheck'));
  const cardOverlaps = [];
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox'), document.querySelector('.timeline')];
  boxes.forEach((a, i) => boxes.forEach((b, j) => { if (j > i && ov(R(a), R(b))) cardOverlaps.push([a.dataset.story || a.className, b.dataset.story || b.className]); }));

  const svg = document.querySelector('.mapsvg');
  const SW = +svg.getAttribute('width'), SH = +svg.getAttribute('height');
  const pins = [...document.querySelectorAll('.pin circle')].map(c => ({n: +c.parentNode.dataset.pin, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')}));
  const pinOverlaps = [];
  pins.forEach((a, i) => pins.forEach((b, j) => { if (j > i && Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r) pinOverlaps.push([a.n, b.n]); }));
  const pinsOutside = pins.filter(p => p.x - p.r < 0 || p.y - p.r < 0 || p.x + p.r > SW || p.y + p.r > SH).map(p => p.n);
  const pinNumbers = pins.map(p => p.n);
  const pinLabels = [...document.querySelectorAll('.pin text')].map(t => +t.textContent);

  const lines = el => { const rs = [...el.getClientRects()]; return new Set(rs.map(r => Math.round(r.top))).size; };
  const headlineLines = cards.map(c => lines(c.querySelector('.hl')));
  const summaryLines = cards.map(c => lines(c.querySelector('.sum')));
  const briefLines = briefs.map(b => lines(b.querySelector('.bt')));

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
  const stats = [...document.querySelectorAll('.stat b')].map(b => b.textContent);
  const kicker = document.querySelector('.kickerbar .r').textContent;
  const pageText = document.body.innerText;
  return {doc, stories, regionCounts, regionTagged, overflows, blockOverlaps, bandOverlaps, cardOverlaps,
          pinCount: pins.length, pinNumbers, pinLabels, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          minHtml, minHtmlText, minSvg, imagesLoaded, artSizes, stats, kicker, pageBottom: last.bottom,
          bottomUsed: R(document.querySelector('.bottom')).bottom, pageText};
}'''

# every stat must be backed by a story's text on the page
STAT_SOURCES = {"3": 1, "372,000": 2, "−6.23%": 3, "100,000": 4, "9th": 8, "1,689": 35}


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    if sorted(a["stories"]) != list(range(1, n + 1)):
        f.append(f"stories {a['stories']}")
    if sum(a["regionCounts"]) != n or len(a["regionCounts"]) != 7 or min(a["regionCounts"]) < 4:
        f.append(f"region counts {a['regionCounts']}")
    if any(a["regionTagged"].get(r, 0) != REGION_COUNTS[r] for r in REGION_ORDER):
        f.append(f"region tags {a['regionTagged']} != {REGION_COUNTS}")
    for k in ("overflows", "blockOverlaps", "bandOverlaps", "cardOverlaps", "pinOverlaps", "pinsOutside"):
        if a[k]:
            f.append(f"{k}: {a[k]}")
    pinned = sorted(s["n"] for s in STORIES if s["pin"])
    if sorted(a["pinNumbers"]) != pinned or sorted(a["pinLabels"]) != pinned:
        f.append(f"pins {a['pinNumbers']} labels {a['pinLabels']} != {pinned}")
    if any(max(a[k]) > 2 for k in ("headlineLines", "briefLines")):
        f.append(f"lines: hl {a['headlineLines']} briefs {a['briefLines']}")
    hero_sum, grid_sum = a["summaryLines"][:3], a["summaryLines"][3:]
    if max(hero_sum) > 2 or max(grid_sum) > 1:
        f.append(f"summary lines {a['summaryLines']}")
    if a["minHtml"] < 9.5:
        f.append(f"html font {a['minHtml']} ({a['minHtmlText']})")
    if a["minSvg"] < 9:
        f.append(f"svg font {a['minSvg']}")
    if not a["imagesLoaded"]:
        f.append("image failed to load")
    if any(nw != w or nh != h for nw, nh, w, h in a["artSizes"]):
        f.append(f"art scaled in page: {a['artSizes']}")
    if a["pageBottom"] > 1022:
        f.append(f"page bottom {a['pageBottom']}")
    if a["stats"] != [v for v, _ in STATS]:
        f.append(f"stats {a['stats']}")
    for v, sn in STAT_SOURCES.items():
        s = next(x for x in STORIES if x["n"] == sn)
        body = " ".join(str(s.get(k, "")) for k in ("headline", "summary", "text"))
        word = {"3": "Three", "9th": "9th"}.get(v, v)
        if word not in body and v not in body:
            f.append(f"stat {v} not backed by story {sn}")
    if not a["kicker"].startswith(f"{n} stories") or f"{len(BEATS)} beats" not in a["kicker"] or len(BEATS) < 14:
        f.append(f"kicker {a['kicker']} beats {len(BEATS)}")
    for banned in ("Peltola", "162-151", "joint declaration"):
        if banned in a["pageText"]:
            f.append(f"banned text on page: {banned}")
    return f


def encode_jpeg(im: Image.Image) -> tuple[bytes, int]:
    for q in QUALITIES:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True, progressive=False)
        if buf.tell() <= MAX_BYTES:
            return buf.getvalue(), q
    raise SystemExit("entry.png cannot meet the size budget")


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
        shown = {k: v for k, v in a.items() if k not in ("artSizes", "pageText", "pinLabels")}
        print(json.dumps(shown, ensure_ascii=False)[:3000])
        if failures:
            print("\nAUDIT FAILURES:")
            for x in failures:
                print(" -", x)
            browser.close()
            return 1
        page.screenshot(path=str(ASSETS / "poster.png"))
        browser.close()

    im = Image.open(ASSETS / "poster.png").convert("RGB")
    data, q = encode_jpeg(im)
    (BASE / "entry.png").write_bytes(data)
    im.resize((300, 300), Image.LANCZOS).save(PROOF_300)
    size = len(data)
    print(f"\nAUDIT OK · {len(STORIES)} stories · regions {REGION_COUNTS} · {len(BEATS)} beats · "
          f"min html font {a['minHtml']}px · min svg font {a['minSvg']}px · pins {a['pinCount']}")
    print(f"entry.png: {size} bytes ({size / 1024:.1f} KiB) · JPEG q{q} 4:4:4 baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())

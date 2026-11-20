#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news front page (v5).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
baseline 4:4:4 JPEG, the highest quality in q93..q91 that fits MAX_BYTES) and
/tmp/news_1120_v5_300.png (300 px Lanczos proof).
"""
from __future__ import annotations

import base64
import html
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

import art
import mapgen

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
CHROME = "/usr/bin/google-chrome"
BUILD_TMP = Path("/tmp/news_1120_v5_build")
PROOF_300 = Path("/tmp/news_1120_v5_300.png")
MAX_BYTES = 650 * 1024          # v5 budget; the gate limit is 1,048,576 bytes
MIN_BYTES = 440 * 1024
QUALITIES = (93, 92, 91)

# ---------------------------------------------------------------------------
# The edition. Every item happened, or was first reported, on Friday
# 20 November 2026 (UTC). Thursday 19 November news and events that have not
# happened yet (Saturday 21 November) appear only in the DATE CHECK bar, as
# omissions.
# kind: hero (1-3) · grid (4-13) · brief (14-38). A brief has a bold
# headline phrase (h) and a short detail (d).
# cert: "v" = official / confirmed on the record, "r" = reported or claimed.
# pin: (lon, lat).
# ---------------------------------------------------------------------------
STORIES = [
    # --- lead stories -------------------------------------------------------
    dict(n=1, kind="hero", region="EUROPE", beat="Conflict", cert="v", place="Kyiv, Ukraine",
         src="Kyiv Ind. · Reuters · AP",
         headline="Russian Missiles Hit Three Kyiv Bridges",
         summary="About 110 missiles and 400 drones; 3 killed in Kyiv and at least 8 nationwide, officials say.",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", beat="Weather", cert="v", place="Gopalpur, India",
         src="IMD · The Hindu · AA",
         headline="Cyclone Akvan Makes Landfall in Odisha",
         summary="Crossed near Gopalpur around 8 am, then weakened; up to 372,000 evacuated, no deaths reported.",
         art="art_02.png", pin=(84.9, 19.3)),
    dict(n=3, kind="hero", region="ASIA-PACIFIC", beat="Markets", cert="v", place="Taipei · Seoul · Tokyo",
         src="Reuters · Al Jazeera · AA",
         headline="Asia’s Chip & AI Stocks Sink in Worst Week Since 2020",
         summary="Taiex −6.23%, Kospi −5.21%, Nikkei −5.06% as Anthropic’s Nasdaq debut fails to calm AI spending fears.",
         art="art_03.png", pin=(121.5, 25.0)),
    # --- illustrated cards --------------------------------------------------
    dict(n=4, kind="grid", region="EUROPE", beat="Diplomacy", cert="v", place="Brussels", src="EU · Guardian",
         headline="UK and EU Seal Post-Brexit Reset",
         summary="Cuts food checks; 100,000 youth places",
         art="art_04.png", pin=(4.35, 50.85)),
    dict(n=5, kind="grid", region="GLOBAL/SCIENCE", beat="Climate", cert="v", place="Antalya", src="UN · AFP · DW",
         headline="COP31 Hits Final Day Without a Deal",
         summary="Draft omits fossil phase-out; overtime.",
         art="art_05.png", pin=(30.7, 36.9)),
    dict(n=6, kind="grid", region="EUROPE", beat="Security", cert="v", place="E. Poland", src="Guardian",
         headline="Russian Cruise Missile Enters Poland",
         summary="PM: an ‘intentional provocation’.",
         art="art_06.png", pin=(23.0, 51.5)),
    dict(n=7, kind="grid", region="MIDDLE EAST", beat="Security", cert="v", place="Jurf al-Sakher", src="officials",
         headline="Iraqi Army Enters Militia Stronghold",
         summary="Kataib Hezbollah hub, on PM’s order.",
         art="art_07.png", pin=(44.2, 32.9)),
    dict(n=8, kind="grid", region="EUROPE", beat="Labour", cert="v", place="Rome", src="Repubblica · AP",
         headline="Italy Halts in 24-Hour General Strike",
         summary="CGIL walkout hits 100+ cities.",
         art="art_08.png", pin=(12.5, 41.9)),
    dict(n=9, kind="grid", region="ASIA-PACIFIC", beat="Economy", cert="v", place="Tokyo", src="MIC · Japan Times",
         headline="Japan Inflation Rises to 2.3% in October",
         summary="Core 2.2%; lifts BOJ Dec hike bets.",
         art="art_09.png", pin=(139.7, 35.7)),
    dict(n=10, kind="grid", region="ASIA-PACIFIC", beat="Courts", cert="v", place="Seoul", src="Korea Herald",
         headline="Ruling Party Moves to Impeach Top Judge",
         summary="DPK targets Chief Justice Cho Hee-dae.",
         art="art_10.png", pin=(127.0, 37.6)),
    dict(n=11, kind="grid", region="AFRICA", beat="Energy", cert="v", place="Turkana", src="The Star",
         headline="Kenya Begins Drilling First Oil Well",
         summary="Amosing field; first exports in 2027.",
         art="art_11.png", pin=(35.7, 2.5)),
    dict(n=12, kind="grid", region="AMERICAS", beat="Elections", cert="v", place="San Salvador", src="AP",
         headline="Bukele Registers Bid for Third Term",
         summary="Files with tribunal for February vote.",
         art="art_12.png", pin=(-89.2, 13.7)),
    dict(n=13, kind="grid", region="OCEANIA", beat="Sport", cert="v", place="Wellington", src="ICC · RNZ",
         headline="Phillips Hits 118 as NZ Make 368 v India",
         summary="Nicholls also unbeaten on 175.",
         art="art_13.png", pin=(174.8, -41.3)),
    # --- the wire: Europe ---------------------------------------------------
    dict(n=14, kind="brief", region="EUROPE", beat="Conflict", cert="v", place="Lviv", src="Kyiv Ind.",
         h="Rail station hit:", d="Sknyliv struck overnight, 2 killed", pin=(24.0, 49.8)),
    dict(n=15, kind="brief", region="EUROPE", beat="Diplomacy", cert="v", place="Paris", src="Quai d’Orsay",
         h="France seeks UNSC session", d="after embassies hit in Kyiv", pin=(2.35, 48.85)),
    dict(n=16, kind="brief", region="EUROPE", beat="Protest", cert="r", place="Berlin", src="organisers",
         h="Gen Z rallies in 73 cities", d="over military service, costs", pin=(13.4, 52.5)),
    dict(n=17, kind="brief", region="EUROPE", beat="Sport", cert="v", place="Turin", src="ATP",
         h="ATP Ventures plan", d="to lift player pay past $350m by 2028", pin=(7.7, 45.1)),
    # --- Asia-Pacific -------------------------------------------------------
    dict(n=18, kind="brief", region="ASIA-PACIFIC", beat="Central banks", cert="v", place="Beijing", src="PBOC",
         h="Loan prime rates held:", d="1-yr 3.0%, 5-yr 3.5%", pin=(116.4, 39.9)),
    dict(n=19, kind="brief", region="ASIA-PACIFIC", beat="Health", cert="v", place="Changwon", src="KDCA",
         h="Cholera case,", d="Korea’s first domestic one in 10 years", pin=(128.7, 35.2)),
    dict(n=20, kind="brief", region="ASIA-PACIFIC", beat="Disinformation", cert="r", place="Taipei", src="Reuters",
         h="2,700 China-linked accounts", d="flagged to Meta", pin=(121.5, 25.0)),
    dict(n=21, kind="brief", region="ASIA-PACIFIC", beat="Markets", cert="v", place="Singapore", src="SGX",
         h="STI slides 2.1%", d="to close below 5,000", pin=(103.8, 1.35)),
    dict(n=22, kind="brief", region="ASIA-PACIFIC", beat="Diplomacy", cert="v", place="Shenzhen", src="FMPRC",
         h="Xi meets Anwar", d="on the APEC sidelines", pin=(114.1, 22.5)),
    # --- Americas -----------------------------------------------------------
    dict(n=23, kind="brief", region="AMERICAS", beat="US politics", cert="v", place="Washington", src="CBS",
         h="Trump hails Asia trip,", d="calls Iran offer unacceptable", pin=(-77.0, 38.9)),
    dict(n=24, kind="brief", region="AMERICAS", beat="Tech", cert="v", place="New York", src="Reuters",
         h="Nasdaq falls over 3%", d="as Anthropic nears IPO price", pin=(-74.0, 40.7)),
    dict(n=25, kind="brief", region="AMERICAS", beat="Weather", cert="v", place="Brevard, FL", src="NWS · CBS",
         h="Record floods:", d="emergencies, 100+ rescues", pin=(-80.7, 28.2)),
    dict(n=26, kind="brief", region="AMERICAS", beat="Sport", cert="v", place="Las Vegas", src="F1",
         h="Russell tops wet FP2", d="in 1:47.272", pin=(-115.2, 36.2)),
    # --- Global / science ---------------------------------------------------
    dict(n=27, kind="brief", region="GLOBAL/SCIENCE", beat="UN", cert="v", place="New York", src="SCR",
         h="UN’s 9th straw poll", d="on the next secretary-general", pin=(-74.0, 40.7)),
    dict(n=28, kind="brief", region="GLOBAL/SCIENCE", beat="Wildlife", cert="v", place="Amazon", src="WCS",
         h="Bush dog benchmarked", d="in 25-year camera-trap study", pin=(-68.0, -8.0)),
    # --- Middle East --------------------------------------------------------
    dict(n=29, kind="brief", region="MIDDLE EAST", beat="Conflict", cert="v", place="Riyadh", src="AP",
         h="Coalition intercepts", d="1 Houthi missile and 5 drones", pin=(46.7, 24.7)),
    dict(n=30, kind="brief", region="MIDDLE EAST", beat="Piracy", cert="v", place="Al Mukalla", src="UKMTO",
         h="Skiff fires on ship", d="95 nm SW; guards repel it", pin=(49.1, 14.5)),
    dict(n=31, kind="brief", region="MIDDLE EAST", beat="Shipping", cert="r", place="Hormuz", src="Al Jazeera",
         h="US memo: Iran blockade", d="lifts war-risk premiums", pin=(56.3, 26.6)),
    # --- Africa -------------------------------------------------------------
    dict(n=32, kind="brief", region="AFRICA", beat="Migration", cert="v", place="Dakar", src="IOM",
         h="Migration declaration", d="and roadmap adopted", pin=(-17.4, 14.7)),
    dict(n=33, kind="brief", region="AFRICA", beat="Markets", cert="v", place="Johannesburg", src="Reuters",
         h="Rand at 1-year low", d="on coalition jitters", pin=(28.0, -26.2)),
    dict(n=34, kind="brief", region="AFRICA", beat="Debt", cert="v", place="Abidjan", src="AfDB",
         h="22 African states", d="in or at high risk of debt distress", pin=(-4.0, 5.3)),
    dict(n=35, kind="brief", region="AFRICA", beat="Energy", cert="v", place="Lilongwe", src="Al Jazeera",
         h="Malawi fuel queues", d="despite $30m release", pin=(33.8, -14.0)),
    dict(n=36, kind="brief", region="AFRICA", beat="Sport", cert="v", place="Doha", src="Africanews",
         h="U-17 World Cup:", d="Morocco, Senegal, Mali play", pin=(51.5, 25.3)),
    # --- Oceania ------------------------------------------------------------
    dict(n=37, kind="brief", region="OCEANIA", beat="Business", cert="v", place="Sydney", src="receivers",
         h="David Jones collapses:", d="1,689 redundancy notices", pin=(151.2, -33.9)),
    dict(n=38, kind="brief", region="OCEANIA", beat="Diplomacy", cert="v", place="Shenzhen", src="ABC",
         h="Xi: ‘full turnaround’", d="with Australia, praises Albanese", pin=(114.1, 22.5)),
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
    ("2.3%", "Japan Oct CPI"),
    ("118", "Phillips runs vs India"),
]
# every stat must be backed by a story's text on the page
STAT_SOURCES = {"3": 1, "372,000": 2, "−6.23%": 3, "100,000": 4, "2.3%": 9, "118": 13}

DECK = ("Missiles hit three Kyiv bridges · Cyclone Akvan lands in Odisha · "
        "Asia’s chip stocks sink · UK and EU seal reset · COP31 runs over")

TIMELINE = [
    ("Night", "Kyiv bridges struck"),
    ("02Z", "Akvan landfall"),
    ("05Z", "Taiex shuts −6.23%"),
    ("Day", "Italy 24-hour strike"),
    ("12Z", "France seeks UNSC"),
    ("14Z", "UK–EU reset sealed"),
    ("17Z", "UN straw poll"),
    ("Eve", "COP31 overtime"),
]

# The DATE CHECK bar: certification plus what was deliberately left out.
THURSDAY_OMITTED = ["ICJ Myanmar genocide ruling", "Trump–Xi–Putin Shenzhen declaration",
                    "Pentagon $48.3bn Iran tally", "Canada budget vote", "DOJ Alaska suit"]
SATURDAY_OMITTED = "BepiColombo’s Saturday Mercury orbit capture & final COP31 text"
# words that may appear only inside the DATE CHECK bar, never in a story
DATECHECK_ONLY = ["BepiColombo", "Bepi", "Mercury", "Saturday", "Thursday", "19 Nov", "21 Nov",
                  "ICJ", "Putin", "Pentagon", "48.3bn", "Alaska", "Canada"]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def badge(s: dict, cls: str = "num") -> str:
    return f'<span class="{cls}" style="background:{REGION_COLORS[s["region"]]}">{s["n"]}</span>'


def cert(s: dict) -> str:
    g, label = CERT[s["cert"]]
    return f'<span class="ct ct-{s["cert"]}" title="{g} {label}"></span>'


def keep_hyphens(text: str) -> str:
    """Escape a headline and stop it breaking inside hyphenated words (24-Hour)."""
    return re.sub(r"(\S+-\S+)", r'<span class="nb">\1</span>', esc(text))


def card_html(s: dict) -> str:
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place">{esc(s['place'])} · {esc(s['src'])}</span>{cert(s)}</div>
      <h2><span class="hl">{keep_hyphens(s['headline'])}</span></h2>
      <p class="summary"><span class="sum">{esc(s['summary'])}</span></p>
    </article>'''


def brief_html(s: dict) -> str:
    return f'''
      <div class="brief" data-story="{s['n']}" data-region="{esc(s['region'])}">
        {badge(s, 'bnum')}<p class="btext"><span class="bt"><b>{esc(s['place'])}</b> <strong>{esc(s['h'])}</strong> {esc(s['d'])} <i>{esc(s['src'])}</i>&nbsp;{cert(s)}</span></p>
      </div>'''


def datecheck_html() -> str:
    n = len(STORIES)
    return f'''
  <div class="datecheck">
    <div class="dclabel"><b>DATE CHECK ✓</b><span>{n} of {n} · Fri 20 Nov</span></div>
    <div class="dclines">
      <div class="dl"><strong>Every story above happened or was first reported on Friday 20 November 2026 (UTC).</strong> <em>Not yet happened, so omitted:</em> {esc(SATURDAY_OMITTED)}.</div>
      <div class="dl"><em>Thursday 19 Nov news, so omitted:</em> {' · '.join(esc(x) for x in THURSDAY_OMITTED)}.</div>
    </div>
  </div>'''


def build_html() -> str:
    heroes = [s for s in STORIES if s["kind"] == "hero"]
    grid = [s for s in STORIES if s["kind"] == "grid"]
    briefs = [s for s in STORIES if s["kind"] == "brief"]
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in STORIES]
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
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-BoldItalic.ttf'); font-weight:700; font-style:italic; }}
@font-face {{ font-family:'LatoX'; src:url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf'); font-weight:900; }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; width:1024px; height:1024px; overflow:hidden; background:#F7F3E9; }}
body {{ font-family:'LatoX', sans-serif; color:#121822; -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-variant-ligatures:none; }}
.page {{ width:1024px; height:1024px; padding:5px 18px 0 18px; }}
.kickerbar {{ height:14px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.1em; text-transform:uppercase; padding-bottom:2px; white-space:nowrap; }}
.kickerbar .r {{ color:#9A1B1F; }}
.masthead {{ height:70px; font:700 67px/62px 'LibSerif'; letter-spacing:-.02em; text-align:center; white-space:nowrap; border-top:2.5px solid #121822; padding-top:0; }}
.deck {{ height:18px; font:italic 700 14px/16px 'LibSerif'; color:#9A1B1F; text-align:center; white-space:nowrap; border-bottom:1px solid #121822; }}
.stats {{ display:flex; height:37px; border-bottom:2.5px solid #121822; }}
.stat {{ flex:1; min-width:0; padding:1px 10px 0; display:flex; flex-direction:column; justify-content:center; }}
.stat + .stat {{ border-left:1px solid #CDBFA3; }}
.stat:first-child {{ padding-left:0; }}
.stat b {{ font:700 21px/1 'LibSerif'; color:#9A1B1F; }}
.stat span {{ font:900 10px/11px 'LatoX'; height:11px; letter-spacing:.04em; text-transform:uppercase; margin-top:2px; white-space:nowrap; overflow:hidden; }}
.regionbar {{ display:flex; gap:3px; height:14px; margin-top:3px; }}
.rg {{ flex:1; display:flex; align-items:center; justify-content:center; gap:6px; color:#FFF; white-space:nowrap; }}
.rg span {{ font:900 10px/1 'LatoX'; letter-spacing:.07em; }}
.rg b {{ font:900 11px/1 'LatoX'; }}
.row {{ display:flex; margin-top:6px; }}
.row.heroes {{ gap:20px; }}
.row.grid {{ gap:12px; padding-top:5px; border-top:1px solid #121822; }}
.row.grid + .row.grid {{ margin-top:5px; border-top:1px solid #CDBFA3; }}
.card {{ position:relative; display:flex; flex-direction:column; }}
.card + .card::before {{ content:''; position:absolute; top:0; bottom:0; border-left:1px solid #CDBFA3; }}
.hero + .hero::before {{ left:-10.5px; }}
.grid + .grid::before {{ left:-6.5px; }}
.card.hero {{ width:316px; height:242px; }}
.card.grid {{ width:188px; height:152px; }}
.art {{ display:block; }}
.hero .art {{ width:316px; height:144px; }}
.grid .art {{ width:188px; height:86px; }}
.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:4px; }}
.grid .kicker {{ height:14px; margin-top:3px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; line-height:14px; }}
.place {{ flex:1; min-width:0; font:900 10px/12px 'LatoX'; height:12px; letter-spacing:.04em; text-transform:uppercase; color:#6A5440; white-space:nowrap; overflow:hidden; }}
.grid .place {{ letter-spacing:.01em; }}
.ct {{ display:inline-block; flex:0 0 auto; width:7px; height:7px; border-radius:50%; background:#1D6F6A; border:1.3px solid #1D6F6A; vertical-align:0; }}
.ct-r {{ background:linear-gradient(90deg, #A85F12 50%, #F7F3E9 50%); border-color:#A85F12; }}
h2 {{ margin:3px 0 0 0; font:700 22px/1.03 'LibSerif'; color:#0E121A; letter-spacing:-.01em; text-wrap:balance; }}
.nb {{ white-space:nowrap; }}
.grid h2 {{ margin-top:2px; font-size:16px; line-height:1.0; letter-spacing:-.005em; }}
.summary {{ margin:2px 0 0 0; font:400 11.5px/1.22 'LatoX'; color:#222831; }}
.grid .summary {{ margin-top:2px; font-size:10.5px; line-height:1.22; white-space:nowrap; }}
.bottom {{ display:flex; gap:14px; height:243px; margin-top:5px; border-top:2.5px solid #121822; padding-top:3px; }}
.mapcol {{ flex:0 0 300px; width:300px; position:relative; }}
.mapcol::before {{ content:''; position:absolute; left:-7.5px; top:0; bottom:0; border-left:1px solid #CDBFA3; }}
.secthead {{ height:15px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.1em; text-transform:uppercase; border-bottom:1px solid #121822; padding-bottom:3px; white-space:nowrap; }}
.secthead span {{ color:#9A1B1F; letter-spacing:.05em; }}
.mapbox {{ margin-top:3px; width:300px; height:{mapgen.H}px; overflow:hidden; }}
.mapsvg {{ display:block; }}
.tlhead {{ margin-top:6px; }}
.timeline {{ display:grid; grid-template-columns:1fr 1fr; grid-template-rows:repeat(4, 18px); grid-auto-flow:column; column-gap:12px; margin-top:2px; }}
.tli {{ height:18px; display:flex; gap:5px; align-items:center; white-space:nowrap; overflow:hidden; border-bottom:1px dotted #BFB49C; }}
.tli b {{ flex:0 0 32px; font:900 10.5px/14px 'LatoX'; color:#9A1B1F; }}
.tli span {{ font:700 10.5px/14px 'LatoX'; }}
.briefcol {{ flex:1; min-width:0; }}
.briefgrid {{ display:flex; gap:12px; margin-top:1px; }}
.bcol {{ flex:1; min-width:0; position:relative; }}
.bcol + .bcol::before {{ content:''; position:absolute; left:-6.5px; top:3px; bottom:3px; border-left:1px solid #CDBFA3; }}
.brief {{ height:24.6px; display:flex; align-items:center; gap:5px; border-bottom:1px solid #DDD2BA; }}
.bcol .brief:last-child {{ border-bottom:none; }}
.bnum {{ flex:0 0 16px; width:16px; height:16px; border-radius:50%; color:#FFF; font:900 10px/16px 'LatoX'; text-align:center; }}
.btext {{ margin:0; font:400 10.6px/12px 'LatoX'; color:#1E242E; letter-spacing:-.005em; }}
.btext b {{ color:#9A1B1F; text-transform:uppercase; font:900 10.4px/12px 'LatoX'; letter-spacing:.03em; margin-right:1px; }}
.btext strong {{ color:#0E121A; font:900 10.8px/12px 'LatoX'; }}
.btext i {{ font:italic 400 10.4px/12px 'LatoX'; color:#6A5440; }}
.datecheck {{ margin-top:5px; height:32px; border:1.5px solid #9A1B1F; background:#F1E9D8; display:flex; align-items:center; overflow:hidden; }}
.dclabel {{ flex:0 0 112px; height:100%; background:#9A1B1F; color:#FFF; display:flex; flex-direction:column; justify-content:center; padding:0 8px; white-space:nowrap; }}
.dclabel b {{ font:900 13px/15px 'LatoX'; letter-spacing:.05em; }}
.dclabel span {{ font:700 10px/12px 'LatoX'; letter-spacing:.02em; }}
.dclines {{ flex:1; min-width:0; padding:0 8px; }}
.dl {{ font:400 10.2px/13.5px 'LatoX'; white-space:nowrap; overflow:hidden; letter-spacing:-.005em; height:13.5px; }}
.dl strong {{ font-weight:900; color:#121822; }}
.dl em {{ font-style:normal; font-weight:900; color:#9A1B1F; }}
</style></head>
<body><div class="page">
  <div class="kickerbar"><div>The World Canvas · Friday, 20 November 2026 (UTC)</div><div class="r">{total} stories · 7 regions · {len(BEATS)} beats · every claim sourced</div></div>
  <div class="masthead">Friday, 20 November 2026</div>
  <div class="deck">{esc(DECK)}</div>
  <div class="stats">{stats}</div>
  <div class="regionbar">{regions}</div>
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
      <div class="secthead tlhead"><div>Friday, in UTC</div><span>Times approximate</span></div>
      <div class="timeline">{tl}</div>
    </div>
  </div>{datecheck_html()}
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
  document.querySelectorAll('.page,.kickerbar,.masthead,.deck,.regionbar,.rg,.stats,.stat,.stat span,.card,.kicker,.place,.bottom,.mapbox,.briefcol,.bcol,.brief,.btext,.datecheck,.dclabel,.dclines,.dl,.secthead,.tli,.timeline,.mapcol,.summary').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });

  const blockOverlaps = [];
  cards.forEach(c => {
    const cr = R(c);
    const els = ['.art', '.kicker', 'h2', '.summary'].map(s => c.querySelector(s));
    els.forEach((e, i) => {
      const r = R(e);
      if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: e.className || e.tagName, why: 'leaves card'});
      if (i < els.length - 1 && r.bottom > R(els[i + 1]).y + 0.5) blockOverlaps.push({card: c.dataset.story, a: e.className || e.tagName, b: els[i + 1].className || els[i + 1].tagName});
    });
    ['.hl', '.sum', '.place'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom + 0.5 || r.right > cr.right - 2) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped'}); });
  });
  briefs.forEach(b => { const br = R(b), t = R(b.querySelector('.bt')); if (t.y < br.y - 0.5 || t.bottom > br.bottom + 0.5 || t.right > br.right + 0.5) blockOverlaps.push({brief: b.dataset.story, why: 'text clipped'}); });
  [...document.querySelectorAll('.tli')].forEach(t => { const r = R(t), s = R(t.querySelector('span')); if (s.right > r.right + 0.5) blockOverlaps.push({tl: t.textContent, why: 'clipped'}); });
  [...document.querySelectorAll('.dl')].forEach(t => { const r = R(t); const last = t.lastChild; const range = document.createRange(); range.selectNodeContents(t); const rr = range.getBoundingClientRect(); if (rr.right > r.right + 0.5) blockOverlaps.push({dl: t.textContent.slice(0, 30), why: 'clipped', over: rr.right - r.right}); });
  const mc = R(document.querySelector('.mapcol'));
  [...document.querySelectorAll('.mapcol > *')].forEach(e => { if (R(e).bottom > mc.bottom + 0.5) blockOverlaps.push({el: e.className, why: 'leaves map column'}); });
  const bc = R(document.querySelector('.briefcol'));
  [...document.querySelectorAll('.bcol')].forEach(e => { if (R(e).bottom > bc.bottom + 0.5) blockOverlaps.push({el: 'bcol', why: 'leaves wire column', by: R(e).bottom - bc.bottom}); });

  const bands = ['.kickerbar', '.masthead', '.deck', '.stats', '.regionbar', '.row.heroes', '.row.grid', '.bottom', '.datecheck'];
  const bandEls = bands.flatMap(s => [...document.querySelectorAll(s)]);
  const bandOverlaps = [];
  for (let i = 0; i < bandEls.length - 1; i++) { const a = R(bandEls[i]), b = R(bandEls[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bandEls[i].className, b: bandEls[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const last = R(document.querySelector('.datecheck'));
  const cardOverlaps = [];
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox'), document.querySelector('.timeline'), document.querySelector('.datecheck')];
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
  const dateCheckText = document.querySelector('.datecheck').innerText;
  const dc = document.querySelector('.datecheck');
  const clone = document.body.cloneNode(true);
  clone.querySelector('.datecheck').remove();
  const pageTextNoDC = clone.textContent;
  return {doc, stories, regionCounts, regionTagged, overflows, blockOverlaps, bandOverlaps, cardOverlaps,
          pinCount: pins.length, pinNumbers, pinLabels, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          minHtml, minHtmlText, minSvg, imagesLoaded, artSizes, stats, kicker, pageBottom: last.bottom,
          wireSlack: +(bc.bottom - Math.max(...[...document.querySelectorAll('.bcol')].map(e => R(e).bottom))).toFixed(1),
          mapSlack: +(mc.bottom - R(document.querySelector('.timeline')).bottom).toFixed(1),
          dateCheckText, pageTextNoDC, dcBorder: getComputedStyle(dc).borderTopColor};
}'''


def check_stories() -> list[str]:
    """Static checks on the edition before rendering."""
    f = []
    for s in STORIES:
        body = " ".join(str(v) for k, v in s.items() if isinstance(v, str))
        for w in DATECHECK_ONLY:
            if w.lower() in body.lower():
                f.append(f"story {s['n']} contains date-check-only text '{w}'")
    nums = [s["n"] for s in STORIES]
    if nums != list(range(1, len(STORIES) + 1)):
        f.append(f"story numbers {nums}")
    if "BepiColombo" not in SATURDAY_OMITTED:
        f.append("DATE CHECK must name BepiColombo as not-yet-happened")
    return f


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    if not 37 <= n <= 38 or a["pinCount"] != n:
        f.append(f"v5 expects 37-38 stories, one pin each; got {n} / {a['pinCount']}")
    if sorted(a["stories"]) != list(range(1, n + 1)):
        f.append(f"stories {a['stories']}")
    if sum(a["regionCounts"]) != n or len(a["regionCounts"]) != 7 or min(a["regionCounts"]) < 3:
        f.append(f"region counts {a['regionCounts']}")
    if any(a["regionTagged"].get(r, 0) != REGION_COUNTS[r] for r in REGION_ORDER):
        f.append(f"region tags {a['regionTagged']} != {REGION_COUNTS}")
    for k in ("overflows", "blockOverlaps", "bandOverlaps", "cardOverlaps", "pinOverlaps", "pinsOutside"):
        if a[k]:
            f.append(f"{k}: {a[k]}")
    pinned = list(range(1, n + 1))
    if sorted(a["pinNumbers"]) != pinned or sorted(a["pinLabels"]) != pinned:
        f.append(f"pins {a['pinNumbers']} labels {a['pinLabels']} != {pinned}")
    if any(x > 2 for x in a["headlineLines"] + a["briefLines"]):
        f.append(f"lines: hl {a['headlineLines']} briefs {a['briefLines']}")
    hero_sum, grid_sum = a["summaryLines"][:3], a["summaryLines"][3:]
    if max(hero_sum) > 2 or max(grid_sum) > 1:
        f.append(f"summary lines {a['summaryLines']}")
    if a["minHtml"] < 10:
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
        body = " ".join(str(s.get(k, "")) for k in ("headline", "summary", "h", "d"))
        word = {"3": "Three"}.get(v, v)
        if word not in body:
            f.append(f"stat {v} not backed by story {sn}")
    if not a["kicker"].startswith(f"{n} stories") or f"{len(BEATS)} beats" not in a["kicker"] or len(BEATS) < 25:
        f.append(f"kicker {a['kicker']} beats {len(BEATS)}")
    # date discipline: excluded news appears only in the DATE CHECK bar
    for w in DATECHECK_ONLY:
        if w in a["pageTextNoDC"]:
            f.append(f"date-check-only text outside DATE CHECK: {w}")
    dc = a["dateCheckText"]
    need = ["DATE CHECK ✓", "Friday 20 November 2026 (UTC)", "Thursday 19 Nov", "Not yet happened",
            "BepiColombo", "final COP31 text"] + THURSDAY_OMITTED
    for w in need:
        if w not in dc.replace("’", "'").replace("'", "’") and w not in dc:
            f.append(f"DATE CHECK missing: {w}")
    if a["dcBorder"] != "rgb(154, 27, 31)":
        f.append(f"DATE CHECK border {a['dcBorder']}")
    return f


def encode_jpeg(im: Image.Image) -> tuple[bytes, int]:
    for q in QUALITIES:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True, progressive=False)
        if buf.tell() <= MAX_BYTES:
            return buf.getvalue(), q
    raise SystemExit("entry.png cannot meet the size budget at q91-93")


def main() -> int:
    static = check_stories()
    if static:
        print("STORY CHECK FAILURES:\n - " + "\n - ".join(static))
        return 1
    art.build_all()
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in STORIES]
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
        shown = {k: v for k, v in a.items() if k not in ("artSizes", "pageTextNoDC", "pinLabels", "dateCheckText")}
        keys = ("pageBottom", "wireSlack", "mapSlack", "headlineLines", "summaryLines", "briefLines",
                "minHtml", "minSvg", "regionCounts", "pinCount")
        print("metrics:", json.dumps({k: a[k] for k in keys}, ensure_ascii=False))
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
    if not MIN_BYTES <= len(data) <= MAX_BYTES:
        raise SystemExit(f"entry.png outside v5 budget: {len(data)} bytes at q{q}")
    (BASE / "entry.png").write_bytes(data)
    im.resize((300, 300), Image.LANCZOS).save(PROOF_300)
    size = len(data)
    print(f"\nAUDIT OK · {len(STORIES)} stories · regions {REGION_COUNTS} · {len(BEATS)} beats · "
          f"min html font {a['minHtml']}px · min svg font {a['minSvg']}px · pins {a['pinCount']} · "
          f"BepiColombo only in DATE CHECK")
    print(f"entry.png: {size} bytes ({size / 1024:.1f} KiB) · JPEG q{q} 4:4:4 baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())

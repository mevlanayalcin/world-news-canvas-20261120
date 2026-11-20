#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news front page (v7).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
progressive 4:4:4 JPEG at q90 or q89, 380,000-459,999 bytes; 450,000 is the
soft target) and
/tmp/news_1120_v7_300.png (300 px Lanczos proof).
"""
from __future__ import annotations

import base64
import html
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageFont
from playwright.sync_api import sync_playwright

import art
import mapgen

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
CHROME = "/usr/bin/google-chrome"
BUILD_TMP = Path("/tmp/news_1120_v7_build")
PROOF_300 = Path("/tmp/news_1120_v7_300.png")
MIN_BYTES, MAX_BYTES = 380_000, 459_999   # v7 hard budget; the gate limit is 1,048,576 bytes
SOFT_MAX = 450_000
QUALITIES = (90, 89)

LATO = Path("/usr/share/fonts/truetype/lato")
BRIEF_PX = 10.5          # brief type size
BRIEF_MAX_W = 328        # every brief must fit on one line this wide (px)
BNUM_PX = 10.8           # uncircled bold wire numeral
BNUM_W, BNUM_GAP = 14, 4 # numeral box width and gap before the place (px)

# ---------------------------------------------------------------------------
# The edition. Every item happened, or was first reported, on Friday
# 20 November 2026 (UTC). Thursday 19 November news and events that have not
# happened yet (Saturday 21 November) appear only in the DATE CHECK box, as
# omissions.
# kind: hero (1-3) · grid (4-13) · brief (14-37).
# dl: the beat word printed in the dateline; beat: the category counted in
# the "25 beats" tally.
# tag: CONFIRMED / OFFICIAL / REPORTED badge on illustrated stories.
# pin: (lon, lat), plotted for stories 1-13 only.
# ---------------------------------------------------------------------------
STORIES = [
    # --- lead stories -------------------------------------------------------
    dict(n=1, kind="hero", region="EUROPE", beat="Conflict", dl="War", place="Kyiv, Ukraine",
         src="Kyiv Independent, Reuters", tag="OFFICIAL",
         headline="Russian Missiles Hit Three\nBridges Across the Dnipro",
         summary="Strikes damage three Dnipro crossings in a barrage of about 110 missiles and "
                 "400 drones; officials say 3 were killed in Kyiv and at least 8 nationwide.",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", beat="Weather", dl="Cyclone", place="Odisha, India",
         src="IMD, The Hindu", tag="OFFICIAL",
         headline="Cyclone Akvan Makes Landfall\nNear Gopalpur in Eastern India",
         summary="The storm crossed the Odisha coast around 8 am local time and then weakened "
                 "inland; up to 372,000 people were moved to shelters and no deaths have been "
                 "reported.",
         art="art_02.png", pin=(84.9, 19.3)),
    dict(n=3, kind="hero", region="ASIA-PACIFIC", beat="Markets", dl="Markets",
         place="Taipei · Seoul · Tokyo", src="Reuters, Al Jazeera", tag="CONFIRMED",
         headline="AI Sell-Off Sinks Asia’s Stock\nMarkets in Worst Week Since 2020",
         summary="Taiwan’s Taiex closes −6.23%, Korea’s Kospi −5.21% and Japan’s Nikkei −5.06% "
                 "as chipmakers lead the rout and fears over AI spending deepen.",
         art="art_03.png", pin=(121.5, 25.0)),
    # --- illustrated cards --------------------------------------------------
    dict(n=4, kind="grid", region="EUROPE", beat="Diplomacy", dl="Diplomacy", place="Brussels",
         src="EU, Guardian", tag="CONFIRMED",
         headline="UK and EU Seal Post-Brexit Reset",
         summary="It cuts food checks and adds 100,000 youth mobility places a year.",
         art="art_04.png", pin=(4.35, 50.85)),
    dict(n=5, kind="grid", region="GLOBAL/SCIENCE", beat="Climate", dl="Climate", place="Antalya",
         src="UN, AFP", tag="CONFIRMED",
         headline="COP31 Hits Final Day Without a Deal",
         summary="The draft omits a fossil-fuel phase-out and talks run into overtime.",
         art="art_05.png", pin=(30.7, 36.9)),
    dict(n=6, kind="grid", region="EUROPE", beat="Security", dl="Security", place="Eastern Poland",
         src="Guardian", tag="OFFICIAL",
         headline="Russian Cruise Missile Enters Poland",
         summary="Poland’s prime minister calls the incursion an ‘intentional provocation’.",
         art="art_06.png", pin=(23.0, 51.5)),
    dict(n=7, kind="grid", region="MIDDLE EAST", beat="Security", dl="Security", place="Jurf al-Sakher",
         src="Iraqi officials", tag="OFFICIAL",
         headline="Iraqi Army Enters Militia Stronghold",
         summary="Troops enter the Kataib Hezbollah base on the PM’s order.",
         art="art_07.png", pin=(44.2, 32.9)),
    dict(n=8, kind="grid", region="EUROPE", beat="Labour", dl="Labour", place="Rome",
         src="La Repubblica, AP", tag="CONFIRMED",
         headline="Italy Halts in 24-Hour General Strike",
         summary="The CGIL union’s walkout hits more than 100 cities.",
         art="art_08.png", pin=(12.5, 41.9)),
    dict(n=9, kind="grid", region="ASIA-PACIFIC", beat="Economy", dl="Economy", place="Tokyo",
         src="MIC, Japan Times", tag="OFFICIAL",
         headline="Japan Inflation Rises to 2.3% in October",
         summary="Core CPI is 2.2%, lifting bets on a December BOJ hike.",
         art="art_09.png", pin=(139.7, 35.7)),
    dict(n=10, kind="grid", region="ASIA-PACIFIC", beat="Courts", dl="Courts", place="Seoul",
         src="Korea Herald", tag="REPORTED",
         headline="Ruling Party Moves to Impeach Top Judge",
         summary="The Democratic Party targets Chief Justice Cho Hee-dae.",
         art="art_10.png", pin=(127.0, 37.6)),
    dict(n=11, kind="grid", region="AFRICA", beat="Energy", dl="Energy", place="Turkana, Kenya",
         src="The Star", tag="CONFIRMED",
         headline="Kenya Begins Drilling First Oil Well",
         summary="Drilling starts at the Amosing field; first exports are planned for 2027.",
         art="art_11.png", pin=(35.7, 2.5)),
    dict(n=12, kind="grid", region="AMERICAS", beat="Elections", dl="Elections", place="San Salvador",
         src="AP", tag="CONFIRMED",
         headline="Bukele Registers Bid for Third Term",
         summary="He files with the electoral tribunal ahead of the February vote.",
         art="art_12.png", pin=(-89.2, 13.7)),
    dict(n=13, kind="grid", region="OCEANIA", beat="Sport", dl="Cricket", place="Wellington",
         src="ICC, RNZ", tag="CONFIRMED",
         headline="Phillips Hits 118 as NZ Make 368 v India",
         summary="Glenn Phillips’ century is backed by Henry Nicholls, unbeaten on 175.",
         art="art_13.png", pin=(174.8, -41.3)),
    # --- also on Friday: Europe ---------------------------------------------
    dict(n=14, kind="brief", region="EUROPE", beat="Conflict", place="Lviv",
         text="Sknyliv rail station struck overnight, 2 killed", src="Kyiv Independent"),
    dict(n=15, kind="brief", region="EUROPE", beat="Diplomacy", place="Paris",
         text="Seeks UNSC session after embassies hit in Kyiv", src="Quai d’Orsay"),
    dict(n=16, kind="brief", region="EUROPE", beat="Protest", place="Berlin",
         text="Gen Z rally over military service in 73 cities", src="organisers"),
    dict(n=17, kind="brief", region="EUROPE", beat="Sport", place="Turin",
         text="ATP plans to lift player pay past $350m by 2028", src="ATP"),
    # --- Asia-Pacific -------------------------------------------------------
    dict(n=18, kind="brief", region="ASIA-PACIFIC", beat="Central banks", place="Beijing",
         text="Loan prime rates held: 1-year 3.0%, 5-year 3.5%", src="PBOC"),
    dict(n=19, kind="brief", region="ASIA-PACIFIC", beat="Health", place="Changwon",
         text="Korea’s first domestic cholera case in 10 years", src="KDCA"),
    dict(n=20, kind="brief", region="ASIA-PACIFIC", beat="Disinformation", place="Taipei",
         text="2,700 China-linked accounts flagged to Meta", src="Reuters"),
    dict(n=21, kind="brief", region="ASIA-PACIFIC", beat="Markets", place="Singapore",
         text="STI slides 2.1% to close below 5,000", src="SGX"),
    dict(n=22, kind="brief", region="ASIA-PACIFIC", beat="Diplomacy", place="Shenzhen",
         text="Xi meets Malaysia’s Anwar on APEC sidelines", src="FMPRC"),
    # --- Americas -----------------------------------------------------------
    dict(n=23, kind="brief", region="AMERICAS", beat="US politics", place="Washington",
         text="Trump hails Asia trip, rejects Iran offer", src="CBS"),
    dict(n=24, kind="brief", region="AMERICAS", beat="Tech", place="New York",
         text="Nasdaq falls over 3% as the AI sell-off spreads", src="Reuters"),
    dict(n=25, kind="brief", region="AMERICAS", beat="Weather", place="Brevard, FL",
         text="Record floods: emergency, 100+ rescues", src="NWS"),
    dict(n=26, kind="brief", region="AMERICAS", beat="Sport", place="Las Vegas",
         text="Russell tops wet second practice in 1:47.272", src="F1"),
    # --- Global / science ---------------------------------------------------
    dict(n=27, kind="brief", region="GLOBAL/SCIENCE", beat="UN", place="New York",
         text="9th straw poll on the next secretary-general", src="SCR"),
    dict(n=28, kind="brief", region="GLOBAL/SCIENCE", beat="Wildlife", place="Amazon",
         text="25-year camera traps benchmark the bush dog", src="WCS"),
    # --- Middle East --------------------------------------------------------
    dict(n=29, kind="brief", region="MIDDLE EAST", beat="Conflict", place="Riyadh",
         text="Coalition intercepts 1 Houthi missile and 5 drones", src="AP"),
    dict(n=30, kind="brief", region="MIDDLE EAST", beat="Piracy", place="Mukalla",
         text="Skiff fires on ship 95 nm SW; guards repel it", src="UKMTO"),
    dict(n=31, kind="brief", region="MIDDLE EAST", beat="Shipping", place="Hormuz",
         text="US Iran-blockade memo lifts war-risk cover", src="Al Jazeera"),
    # --- Africa -------------------------------------------------------------
    dict(n=32, kind="brief", region="AFRICA", beat="Migration", place="Dakar",
         text="Migration declaration and roadmap adopted", src="IOM"),
    dict(n=33, kind="brief", region="AFRICA", beat="Markets", place="Johannesburg",
         text="Rand hits 1-year low on coalition jitters", src="Reuters"),
    dict(n=34, kind="brief", region="AFRICA", beat="Debt", place="Abidjan",
         text="22 African states in or at high risk of debt distress", src="AfDB"),
    dict(n=35, kind="brief", region="AFRICA", beat="Energy", place="Lilongwe",
         text="Fuel queues persist despite $30m release", src="Al Jazeera"),
    # --- Oceania ------------------------------------------------------------
    dict(n=36, kind="brief", region="OCEANIA", beat="Business", place="Sydney",
         text="David Jones collapses; 1,689 redundancy notices", src="receivers"),
    dict(n=37, kind="brief", region="OCEANIA", beat="Diplomacy", place="Shenzhen",
         text="Xi hails ‘full turnaround’, praises Albanese", src="ABC"),
]

REGION_ORDER = ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA", "GLOBAL/SCIENCE"]
REGION_LABEL = {"GLOBAL/SCIENCE": "GLOBAL/SCI."}
REGION_COLORS = mapgen.REGION_COLORS
REGION_COUNTS = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGION_ORDER}
BEATS = sorted({s["beat"] for s in STORIES})
# certainty tag: (text, tint) — a subtle tinted pill on the dateline row
TAG_COLORS = {"CONFIRMED": ("#17605B", "#DCEDEA"), "OFFICIAL": ("#16243A", "#E2E7EF"),
              "REPORTED": ("#8F500E", "#F5E6D2")}

STATS = [
    ("3", "bridges over the Dnipro damaged in Kyiv strikes"),
    ("372,000", "evacuated in Odisha as Cyclone Akvan lands"),
    ("−6.23%", "Taiwan Taiex close in Asia’s worst AI week"),
    ("100,000", "annual youth mobility places in UK–EU reset"),
    ("2.3%", "Japan Oct headline CPI, lifting BOJ hike bets"),
    ("118", "Glenn Phillips runs as NZ make 368 vs India"),
]
# every stat must be backed by its story's text on the page
STAT_SOURCES = {"3": (1, "three Dnipro"), "372,000": (2, "372,000"), "−6.23%": (3, "−6.23%"),
                "100,000": (4, "100,000"), "2.3%": (9, "2.3%"), "118": (13, "118")}

DECK = ("Missiles hit three Kyiv bridges · Cyclone Akvan lands in Odisha · "
        "Asia’s chip stocks sink · UK and EU seal reset · COP31 runs over")

DC_THURSDAY = ("Left out as Thursday 19 November’s news:",
               "ICJ’s Myanmar genocide ruling, Trump–Xi–Putin Shenzhen declaration, "
               "Pentagon’s $48.3bn Iran war tally, Anthropic’s $83 IPO debut, "
               "Voyager 1’s light-day milestone & GTA VI launch.")
DC_SATURDAY = ("Not yet happened on Friday 20 November, so not shown as fact:",
               "BepiColombo’s Saturday 21 November capture into Mercury orbit and any final "
               "COP31 agreement text.")
FOOT_L = ("Every story here happened, or was first reported, on Friday 20 November 2026 (UTC). "
          "Officials’ counts and single-side claims are attributed.")
FOOT_R = "Sources named beside each story · Original vector drawings"
# words that may appear only inside the DATE CHECK box, never in a story
DATECHECK_ONLY = ["BepiColombo", "Mercury", "Saturday", "Thursday", "19 Nov", "21 Nov", "ICJ",
                  "Putin", "Pentagon", "48.3bn", "Anthropic", "Voyager", "GTA", "Myanmar"]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def badge(s: dict, cls: str = "num") -> str:
    return f'<span class="{cls}" style="background:{REGION_COLORS[s["region"]]}">{s["n"]}</span>'


def keep_hyphens(text: str) -> str:
    """Escape a headline and stop it breaking inside hyphenated words (24-Hour)."""
    return re.sub(r"(\S+-\S+)", r'<span class="nb">\1</span>', esc(text))


def headline_html(s: dict) -> str:
    """Leads carry fixed two-line breaks (\\n); card headlines wrap balanced."""
    return "<br>".join(keep_hyphens(line) for line in s["headline"].split("\n"))


def card_html(s: dict) -> str:
    col = REGION_COLORS[s["region"]]
    tag = s["tag"]
    fg, bg = TAG_COLORS[tag]
    # leads print PLACE · BEAT; the 188 px cards print the place only, so the
    # certainty tag fits on the dateline row without clipping
    where = f"{s['place']} · {s['dl']}" if s["kind"] == "hero" else s["place"]
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place" style="color:{col}">{esc(where)}</span><span class="tg" style="color:{fg};background:{bg}">{tag}</span></div>
      <h2><span class="hl">{headline_html(s)}</span></h2>
      <p class="summary"><span class="sum">{esc(s['summary'])} <span class="src">({esc(s['src'])})</span></span></p>
    </article>'''


def brief_html(s: dict) -> str:
    return f'''
      <div class="brief" data-story="{s['n']}" data-region="{esc(s['region'])}">
        <span class="bnum" style="color:{REGION_COLORS[s['region']]}">{s['n']}</span><p class="btext"><span class="bt"><b>{esc(s['place'])}</b> {esc(s['text'])} <i>({esc(s['src'])})</i></span></p>
      </div>'''


def measure_briefs() -> dict[int, float]:
    """PIL width of each one-line brief: numeral box + gap + bold place + text + source."""
    bold = ImageFont.truetype(str(LATO / "Lato-Bold.ttf"), BRIEF_PX)
    reg = ImageFont.truetype(str(LATO / "Lato-Regular.ttf"), BRIEF_PX)
    ital = ImageFont.truetype(str(LATO / "Lato-Italic.ttf"), BRIEF_PX)
    out = {}
    for s in STORIES:
        if s["kind"] != "brief":
            continue
        w = BNUM_W + BNUM_GAP + bold.getlength(s["place"]) + reg.getlength(" " + s["text"] + " ") \
            + ital.getlength(f"({s['src']})")
        out[s["n"]] = round(w, 1)
    return out


def datecheck_html() -> str:
    return f'''
  <div class="datecheck">
    <div class="dcbadge">DATE CHECK</div>
    <div class="dclines">
      <div class="dl"><b>{esc(DC_THURSDAY[0])}</b> {esc(DC_THURSDAY[1])}</div>
      <div class="dl"><b>{esc(DC_SATURDAY[0])}</b> {esc(DC_SATURDAY[1])}</div>
    </div>
  </div>
  <div class="footer"><div>{esc(FOOT_L)}</div><div class="fr">{esc(FOOT_R)}</div></div>'''


def build_html() -> str:
    heroes = [s for s in STORIES if s["kind"] == "hero"]
    grid = [s for s in STORIES if s["kind"] == "grid"]
    briefs = [s for s in STORIES if s["kind"] == "brief"]
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in heroes + grid]
    total = len(STORIES)
    regions = "".join(
        f'<div class="rg" data-count="{REGION_COUNTS[r]}" style="flex:{REGION_COUNTS[r]} 1 0;background:{REGION_COLORS[r]}">'
        f'<span>{esc(REGION_LABEL.get(r, r))}</span><b>{REGION_COUNTS[r]}</b></div>' for r in REGION_ORDER)
    stats = "".join(f'<div class="stat"><b>{esc(v)}</b><span class="sx"><span class="s2">{esc(l)}</span></span></div>' for v, l in STATS)
    half = len(briefs) // 2
    cols = "".join(f'<div class="bcol">{"".join(brief_html(s) for s in part)}</div>'
                   for part in (briefs[:half], briefs[half:]))
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
html, body {{ margin:0; padding:0; width:1024px; height:1024px; overflow:hidden; background:#FAF7F0; }}
body {{ font-family:'LatoX', sans-serif; color:#121822; -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-variant-ligatures:none; }}
.page {{ position:relative; width:1024px; height:1024px; padding:0 18px; }}
.band {{ position:absolute; left:18px; right:18px; }}
.kickerbar {{ top:4px; height:13px; display:flex; justify-content:space-between; align-items:center; font:900 10px/1 'LatoX'; letter-spacing:.09em; text-transform:uppercase; white-space:nowrap; }}
.kickerbar .l {{ color:#B8292F; }}
.masthead {{ top:19px; height:60px; font:700 58px/52px 'LibSerif'; letter-spacing:-.015em; text-align:center; white-space:nowrap; border-top:2px solid #121822; }}
.deck {{ top:79px; height:19px; font:italic 700 14px/18px 'LibSerif'; color:#B8292F; text-align:center; white-space:nowrap; border-bottom:1px solid #121822; }}
.stats {{ top:102px; height:57px; display:flex; }}
.stat {{ flex:1 1 0; min-width:0; position:relative; padding:0 8px 0 11px; display:flex; flex-direction:column; justify-content:center; }}
.stat::before {{ content:''; position:absolute; left:0; top:4px; bottom:4px; width:3px; background:#B8292F; }}
.stat + .stat {{ margin-left:8px; }}
.stat + .stat::after {{ content:''; position:absolute; left:-5px; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.stat b {{ font:700 25px/26px 'LibSerif'; color:#121822; white-space:nowrap; }}
.stat .sx {{ font:400 10.5px/12.5px 'LatoX'; color:#2A303A; height:25px; overflow:hidden; }}
.regionbar {{ top:163px; height:15px; display:flex; gap:2px; }}
.rg {{ min-width:0; display:flex; align-items:center; justify-content:center; gap:5px; color:#FFF; white-space:nowrap; overflow:hidden; }}
.rg span {{ font:900 10px/1 'LatoX'; letter-spacing:.05em; }}
.rg b {{ font:900 10.5px/1 'LatoX'; }}
.row {{ display:flex; }}
.row.heroes {{ top:183px; height:242px; gap:20px; }}
.row.grid {{ height:165px; gap:12px; }}
.row.g1 {{ top:430px; }}
.row.g2 {{ top:600px; }}
.rule {{ position:absolute; left:18px; right:18px; height:0; border-top:1px solid #DCD6C8; }}
.card {{ position:relative; display:flex; flex-direction:column; }}
.card + .card::before {{ content:''; position:absolute; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.hero + .hero::before {{ left:-10.5px; }}
.grid + .grid::before {{ left:-6.5px; }}
.card.hero {{ width:316px; }}
.card.grid {{ width:188px; }}
.art {{ display:block; outline:1px solid #C4BEB0; }}
.hero .art {{ width:316px; height:{art.HERO[1]}px; }}
.grid .art {{ width:188px; height:{art.GRID[1]}px; }}
.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:4px; }}
.grid .kicker {{ height:14px; margin-top:4px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; line-height:14px; }}
.place {{ flex:1; min-width:0; font:900 10px/12px 'LatoX'; height:12px; letter-spacing:.05em; text-transform:uppercase; white-space:nowrap; overflow:hidden; }}
.grid .place {{ letter-spacing:.03em; }}
h2 {{ margin:3px 0 0 0; font:700 20px/21px 'LibSerif'; color:#0E121A; letter-spacing:-.006em; white-space:nowrap; }}
.nb {{ white-space:nowrap; }}
.grid h2 {{ margin-top:3px; font-size:14px; line-height:15.5px; letter-spacing:-.003em; white-space:normal; text-wrap:balance; }}
.summary {{ margin:3px 0 0 0; font:400 10.8px/13px 'LatoX'; color:#222831; }}
.grid .summary {{ font-size:10px; line-height:12.2px; }}
.src {{ font-style:italic; color:#585D66; }}
.tg {{ flex:0 0 auto; margin-left:auto; padding:1px 4px 0; border-radius:2px; font:900 9px/11px 'LatoX'; letter-spacing:.05em; white-space:nowrap; }}
.bottom {{ top:767px; height:188px; display:flex; gap:14px; border-top:2.5px solid #121822; padding-top:3px; }}
.mapcol {{ flex:0 0 {mapgen.W}px; width:{mapgen.W}px; }}
.briefcol {{ flex:1; min-width:0; position:relative; }}
.briefcol::before {{ content:''; position:absolute; left:-7.5px; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.secthead {{ height:15px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.08em; text-transform:uppercase; border-bottom:1px solid #121822; padding-bottom:3px; white-space:nowrap; }}
.secthead span {{ color:#B8292F; letter-spacing:.05em; }}
.mapbox {{ margin-top:3px; width:{mapgen.W}px; height:{mapgen.H}px; overflow:hidden; }}
.mapsvg {{ display:block; }}
.mapcap {{ margin-top:2px; font:italic 400 10px/12px 'LatoX'; letter-spacing:-.012em; color:#4A4F58; white-space:nowrap; overflow:hidden; height:12px; }}
.briefgrid {{ display:flex; gap:12px; margin-top:2px; }}
.bcol {{ flex:1 1 0; min-width:0; position:relative; }}
.bcol + .bcol::before {{ content:''; position:absolute; left:-6.5px; top:2px; bottom:2px; border-left:1px solid #DCD6C8; }}
.brief {{ height:13.8px; display:flex; align-items:center; gap:{BNUM_GAP}px; }}
.bnum {{ flex:0 0 {BNUM_W}px; width:{BNUM_W}px; font:700 {BNUM_PX}px/13px 'LatoX'; font-variant-numeric:tabular-nums; }}
.btext {{ margin:0; font:400 10.5px/13px 'LatoX'; color:#1E242E; white-space:nowrap; }}
.btext b {{ font-weight:700; color:#0E121A; }}
.btext i {{ color:#585D66; }}
.datecheck {{ top:958px; height:44px; border:1.5px solid #B8292F; background:#FFFDF9; display:flex; align-items:center; gap:7px; padding:0 6px; }}
.dcbadge {{ flex:0 0 auto; background:#B8292F; color:#FFF; font:900 10px/1 'LatoX'; letter-spacing:.06em; padding:5px 5px 4px; border-radius:3px; white-space:nowrap; }}
.dclines {{ flex:1; min-width:0; }}
.dl {{ font:400 9.5px/14px 'LatoX'; color:#121822; white-space:nowrap; overflow:hidden; height:14px; letter-spacing:-.024em; }}
.dl b {{ font-weight:700; color:#B8292F; }}
.footer {{ top:1006px; height:14px; display:flex; justify-content:space-between; align-items:center; font:400 9.5px/12px 'LatoX'; color:#4A4F58; white-space:nowrap; }}
.footer .fr {{ font-weight:700; color:#121822; }}
</style></head>
<body><div class="page">
  <div class="band kickerbar"><div class="l">The world in one day</div><div class="r">{total} stories · 7 regions · {len(BEATS)} beats · every story dated Friday 20 November 2026</div></div>
  <div class="band masthead">Friday 20 November 2026</div>
  <div class="band deck">{esc(DECK)}</div>
  <div class="band stats">{stats}</div>
  <div class="band regionbar">{regions}</div>
  <div class="band row heroes">{''.join(card_html(s) for s in heroes)}</div>
  <div class="rule" style="top:427.5px"></div>
  <div class="band row grid g1">{''.join(card_html(s) for s in grid[:5])}</div>
  <div class="rule" style="top:597.5px"></div>
  <div class="band row grid g2">{''.join(card_html(s) for s in grid[5:])}</div>
  <div class="band bottom">
    <div class="mapcol">
      <div class="secthead"><div>Where it happened</div><span>Pins 1–{len(pins)}</span></div>
      <div class="mapbox">{mapgen.svg(pins)}</div>
      <div class="mapcap">Each numbered pin locates the matching illustrated story (1–{len(pins)}) above.</div>
    </div>
    <div class="briefcol">
      <div class="secthead"><div>Also on Friday 20 November</div><span>{len(briefs)} more stories · {first_brief}–{last_brief}</span></div>
      <div class="briefgrid">{cols}</div>
    </div>
  </div>
  {datecheck_html().replace('class="datecheck"', 'class="band datecheck"').replace('class="footer"', 'class="band footer"')}
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
  document.querySelectorAll('.page,.kickerbar,.masthead,.deck,.regionbar,.rg,.stats,.stat,.stat span,.card,.kicker,.place,.bottom,.mapbox,.mapcap,.briefcol,.bcol,.brief,.btext,.datecheck,.dclines,.dl,.secthead,.mapcol,.footer').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });
  // text that is clipped by an overflow:hidden box
  const textClip = [];
  document.querySelectorAll('.dl,.rg,.place,.mapcap,.stat .sx,.footer > div,.btext').forEach(el => {
    const range = document.createRange(); range.selectNodeContents(el);
    const rr = range.getBoundingClientRect(), r = R(el);
    if (rr.right > r.right + 0.5 || rr.bottom > r.bottom + 0.5) textClip.push({cls: el.className, text: el.textContent.slice(0, 30), over: +(rr.right - r.right).toFixed(1)});
  });

  const blockOverlaps = [];
  cards.forEach(c => {
    const cr = R(c);
    const els = ['.art', '.kicker', 'h2', '.summary'].map(s => c.querySelector(s));
    els.forEach((e, i) => {
      const r = R(e);
      if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: e.className || e.tagName, why: 'leaves card', by: r.bottom - cr.bottom});
      if (i < els.length - 1 && r.bottom > R(els[i + 1]).y + 0.5) blockOverlaps.push({card: c.dataset.story, a: e.className || e.tagName, b: els[i + 1].className || els[i + 1].tagName});
    });
    ['.hl', '.sum'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped'}); });
  });
  const bands = [...document.querySelectorAll('.band')].filter(e => e.offsetHeight > 0);
  const bandOverlaps = [];
  for (let i = 0; i < bands.length - 1; i++) { const a = R(bands[i]), b = R(bands[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bands[i].className, b: bands[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const bc = R(document.querySelector('.briefcol')), mc = R(document.querySelector('.mapcol')), bt = R(document.querySelector('.bottom'));
  [...document.querySelectorAll('.bcol')].forEach(e => { if (R(e).bottom > bc.bottom + 0.5) blockOverlaps.push({el: 'bcol', why: 'leaves wire column', by: R(e).bottom - bc.bottom}); });
  [...document.querySelectorAll('.mapcol > *')].forEach(e => { if (R(e).bottom > bt.bottom + 0.5) blockOverlaps.push({el: e.className, why: 'leaves map column', by: R(e).bottom - bt.bottom}); });
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox'), document.querySelector('.datecheck')];
  const cardOverlaps = [];
  boxes.forEach((a, i) => boxes.forEach((b, j) => { if (j > i && ov(R(a), R(b))) cardOverlaps.push([a.dataset.story || a.className, b.dataset.story || b.className]); }));

  const svg = document.querySelector('.mapsvg');
  const SW = +svg.getAttribute('width'), SH = +svg.getAttribute('height');
  const pins = [...document.querySelectorAll('.pin circle')].map(c => ({n: +c.parentNode.dataset.pin, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')}));
  const pinOverlaps = [];
  pins.forEach((a, i) => pins.forEach((b, j) => { if (j > i && Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r + 1) pinOverlaps.push([a.n, b.n]); }));
  const pinsOutside = pins.filter(p => p.x - p.r < 0 || p.y - p.r < 0 || p.x + p.r > SW || p.y + p.r > SH).map(p => p.n);
  const pinNumbers = pins.map(p => p.n);
  const pinR = pins.map(p => p.r);
  const pinLabels = [...document.querySelectorAll('.pin text')].map(t => +t.textContent);

  const lines = el => { const rs = [...el.getClientRects()].filter(r => r.width > 0); return new Set(rs.map(r => Math.round(r.top))).size; };
  const headlineLines = cards.map(c => lines(c.querySelector('.hl')));
  const summaryLines = cards.map(c => lines(c.querySelector('.sum')));
  const briefLines = briefs.map(b => lines(b.querySelector('.bt')));
  const briefWidths = briefs.map(b => +(R(b.querySelector('.bt')).right - R(b).x).toFixed(1));
  const statLines = [...document.querySelectorAll('.stat .s2')].map(lines);
  const tagPlacement = cards.map(c => [c.querySelectorAll('.kicker .tg').length, c.querySelectorAll('.summary .tg').length]);
  const briefNums = briefs.map(b => { const n = b.querySelector('.bnum'), cs = getComputedStyle(n);
    return {n: +n.textContent, bg: cs.backgroundColor, radius: cs.borderRadius, fs: parseFloat(cs.fontSize), fw: cs.fontWeight}; });
  const heroBottoms = cards.filter(c => c.classList.contains('hero')).map(c => +R(c.querySelector('.sum')).bottom.toFixed(1));

  let minHtml = 99, minHtmlText = '', minSvg = 99;
  document.querySelectorAll('body *').forEach(el => {
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (el instanceof SVGElement) { minSvg = Math.min(minSvg, fs); return; }
    if (el.classList.contains('tg')) return;  // certainty badges are 9 px caps, checked below
    if (fs < minHtml) { minHtml = fs; minHtmlText = el.textContent.trim().slice(0, 30); }
  });
  const tagMin = Math.min(...[...document.querySelectorAll('.tg')].map(e => parseFloat(getComputedStyle(e).fontSize)));
  const imagesLoaded = [...document.images].every(i => i.complete && i.naturalWidth > 0);
  const artSizes = [...document.querySelectorAll('.art')].map(i => [i.naturalWidth, i.naturalHeight, Math.round(R(i).w), Math.round(R(i).h)]);
  const stats = [...document.querySelectorAll('.stat b')].map(b => b.textContent);
  const kicker = document.querySelector('.kickerbar .r').textContent;
  const dc = document.querySelector('.datecheck');
  const dateCheckText = dc.innerText;
  const clone = document.body.cloneNode(true);
  clone.querySelector('.datecheck').remove();
  const pageTextNoDC = clone.textContent;
  const rects = {};
  ['.regionbar', '.row.heroes', '.row.g1', '.row.g2', '.bottom', '.mapbox', '.datecheck', '.footer'].forEach(s => { const r = R(document.querySelector(s)); rects[s] = [r.x, r.y, r.right, r.bottom].map(v => +v.toFixed(1)); });
  const cardBottoms = cards.map(c => +(R(c.querySelector('.summary')).bottom - R(c).y).toFixed(1));
  return {doc, stories, regionCounts, regionTagged, overflows, textClip, blockOverlaps, bandOverlaps, cardOverlaps,
          tagPlacement, briefNums, heroBottoms, pinCount: pins.length, pinNumbers, pinLabels, pinR, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          briefWidths, statLines, minHtml, minHtmlText, minSvg, tagMin, imagesLoaded, artSizes, stats, kicker,
          pageBottom: R(document.querySelector('.footer')).bottom, rects, cardBottoms,
          wireSlack: +(bc.bottom - Math.max(...[...document.querySelectorAll('.bcol')].map(e => R(e).bottom))).toFixed(1),
          mapSlack: +(bt.bottom - R(document.querySelector('.mapcap')).bottom).toFixed(1),
          dateCheckText, pageTextNoDC, dcBorder: getComputedStyle(dc).borderTopColor, dcBg: getComputedStyle(dc).backgroundColor};
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
    if nums != list(range(1, 38)):
        f.append(f"v7 needs stories 1-37 in order, got {nums}")
    kinds = [s["kind"] for s in STORIES]
    if kinds != ["hero"] * 3 + ["grid"] * 10 + ["brief"] * 24:
        f.append("v7 needs 3 leads, 10 cards and 24 briefs")
    for n, w in measure_briefs().items():
        if w > BRIEF_MAX_W:
            f.append(f"brief {n} is {w}px wide at {BRIEF_PX}px; max {BRIEF_MAX_W}px on one line")
    for v, (sn, phrase) in STAT_SOURCES.items():
        s = STORIES[sn - 1]
        if phrase not in s["headline"].replace("\n", " ") + " " + s["summary"]:
            f.append(f"stat {v} not backed by story {sn} ('{phrase}')")
    if len(BEATS) < 25:
        f.append(f"only {len(BEATS)} beats")
    return f


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    if sorted(a["stories"]) != list(range(1, n + 1)):
        f.append(f"stories {a['stories']}")
    if sum(a["regionCounts"]) != n or len(a["regionCounts"]) != 7:
        f.append(f"region counts {a['regionCounts']}")
    if any(a["regionTagged"].get(r, 0) != REGION_COUNTS[r] for r in REGION_ORDER):
        f.append(f"region tags {a['regionTagged']} != {REGION_COUNTS}")
    for k in ("overflows", "textClip", "blockOverlaps", "bandOverlaps", "cardOverlaps", "pinOverlaps", "pinsOutside"):
        if a[k]:
            f.append(f"{k}: {a[k]}")
    pinned = list(range(1, 14))
    if sorted(a["pinNumbers"]) != pinned or sorted(a["pinLabels"]) != pinned:
        f.append(f"pins {a['pinNumbers']} labels {a['pinLabels']} != 1-13")
    if any(not 8 <= r <= 9 for r in a["pinR"]):
        f.append(f"pin radius {a['pinR']}")
    # v7: every headline is exactly two lines; lead summaries three, card summaries two
    if any(x != 2 for x in a["headlineLines"]):
        f.append(f"headline lines must all be 2: {a['headlineLines']}")
    want = [3] * 3 + [2] * 10
    if a["summaryLines"] != want:
        f.append(f"summary lines {a['summaryLines']} != {want}")
    if len(set(a["heroBottoms"])) != 1:
        f.append(f"lead summaries end on different baselines: {a['heroBottoms']}")
    if any(k != 1 or body for k, body in a["tagPlacement"]):
        f.append(f"certainty tag must sit on the dateline only: {a['tagPlacement']}")
    for b in a["briefNums"]:
        if b["bg"] not in ("rgba(0, 0, 0, 0)", "transparent") or b["radius"] != "0px" \
                or b["fs"] != BNUM_PX or b["fw"] != "700":
            f.append(f"wire numeral must be plain bold {BNUM_PX}px: {b}")
    if any(x != 1 for x in a["briefLines"]):
        f.append(f"briefs must be one line: {a['briefLines']}")
    if max(a["briefWidths"]) > BRIEF_MAX_W:
        f.append(f"brief widths {a['briefWidths']}")
    if any(x != 2 for x in a["statLines"]):
        f.append(f"stat explanations must be 2 lines: {a['statLines']}")
    if a["minHtml"] < 9.5:
        f.append(f"html font {a['minHtml']} ({a['minHtmlText']})")
    if a["tagMin"] < 9:
        f.append(f"tag font {a['tagMin']}")
    if a["minSvg"] < 10:
        f.append(f"svg font {a['minSvg']}")
    if not a["imagesLoaded"]:
        f.append("image failed to load")
    if any(nw != w or nh != h for nw, nh, w, h in a["artSizes"]):
        f.append(f"art scaled in page: {a['artSizes']}")
    if a["pageBottom"] > 1022:
        f.append(f"page bottom {a['pageBottom']}")
    if a["stats"] != [v for v, _ in STATS]:
        f.append(f"stats {a['stats']}")
    if not a["kicker"].startswith(f"{n} stories") or f"{len(BEATS)} beats" not in a["kicker"]:
        f.append(f"kicker {a['kicker']} beats {len(BEATS)}")
    for w in DATECHECK_ONLY:
        if w in a["pageTextNoDC"]:
            f.append(f"date-check-only text outside DATE CHECK: {w}")
    dc = a["dateCheckText"]
    for w in ["DATE CHECK", DC_THURSDAY[0], DC_SATURDAY[0], "BepiColombo", "COP31 agreement text",
              "ICJ", "Putin", "48.3bn", "Anthropic", "Voyager 1", "GTA VI"]:
        if w not in dc:
            f.append(f"DATE CHECK missing: {w}")
    if a["dcBorder"] != "rgb(184, 41, 47)" or a["dcBg"] != "rgb(255, 253, 249)":
        f.append(f"DATE CHECK style {a['dcBorder']} {a['dcBg']}")
    return f


def encode_jpeg(im: Image.Image) -> tuple[bytes, int]:
    for q in QUALITIES:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True, progressive=True)
        if MIN_BYTES <= buf.tell() <= (SOFT_MAX if q == QUALITIES[0] else MAX_BYTES):
            return buf.getvalue(), q
        print(f"q{q}: {buf.tell()} bytes, outside {MIN_BYTES}-{MAX_BYTES}")
    raise SystemExit("entry.png cannot meet the size budget at q89-90")


def main() -> int:
    static = check_stories()
    widths = measure_briefs()
    print(f"brief widths (PIL, max {BRIEF_MAX_W}px): widest {max(widths.values())}px "
          f"(story {max(widths, key=widths.get)})")
    if static:
        print("STORY CHECK FAILURES:\n - " + "\n - ".join(static))
        return 1
    art.build_all()
    pins = [(s["n"], s["pin"][0], s["pin"][1], s["region"]) for s in STORIES if s["kind"] != "brief"]
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
        keys = ("pageBottom", "heroBottoms", "wireSlack", "mapSlack", "headlineLines", "summaryLines", "briefLines",
                "statLines", "cardBottoms", "minHtml", "minSvg", "tagMin", "regionCounts", "pinCount", "rects")
        print("metrics:", json.dumps({k: a[k] for k in keys}, ensure_ascii=False))
        print("brief widths (DOM):", a["briefWidths"])
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
          f"min html font {a['minHtml']}px · min svg font {a['minSvg']}px · pins {a['pinCount']} · "
          f"briefs one line each · omitted news only in DATE CHECK")
    print(f"entry.png: {size} bytes ({size / 1024:.1f} KiB) · progressive JPEG q{q} 4:4:4")
    return 0


if __name__ == "__main__":
    sys.exit(main())

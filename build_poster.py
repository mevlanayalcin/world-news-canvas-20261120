#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news front page (v19).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
progressive 4:4:4 JPEG at q89) and /tmp/news20-v19-thumb.png (300 px proof).
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
BUILD_TMP = Path("/tmp/news_1120_v19_build")
PROOF_300 = Path("/tmp/news20-v19-thumb.png")
MIN_BYTES, MAX_BYTES = 380_000, 465_000
QUALITIES = (89, 88)

LATO = Path("/usr/share/fonts/truetype/lato")
BRIEF_PX = 11.0          # airy 11 px brief type (22 briefs, 11 per column)
BRIEF_ROW = 15           # 15 px integer pitch: 11 rows per column
BRIEF_PAD = 3            # left/right padding inside each tinted row, px
BRIEF_MAX_W = 328        # fits one line inside 334 px column
BNUM_PX = 9.5            # white bold number inside the region-coloured disc
BNUM_W, BNUM_GAP = 15, 5 # number disc diameter and gap before the place (px)
TL_H = 18                # height of THE DAY IN UTC strip, px
TL_GAP = 4               # clear px between the strip's cells
BRIEF_INK = "#111827"
GRID_DL_PX = 8.5         # 900-weight caps dateline on the 188 px cards
DATELINE_GAP = 6         # clear px between PLACE · BEAT and its certainty pill

# ---------------------------------------------------------------------------
# The edition: 35 verified pure-Friday 20 November 2026 (UTC) stories across
# all 7 regions and 25 beats.
# kind: hero (1-3) · grid (4-13) · brief (14-35).
# ---------------------------------------------------------------------------
STORIES = [
    # --- 3 lead stories (hero) ----------------------------------------------
    dict(n=1, kind="hero", region="EUROPE", beat="Conflict", dl="War", place="Kyiv, Ukraine",
         src="Kyiv Ind., Reuters, Al Jazeera", tag="OFFICIAL",
         headline="Russian Missiles Hit Three\nBridges Across the Dnipro",
         summary="Ukraine says 111 missiles and 404 drones struck across 15 oblasts overnight, "
                 "damaging three Dnipro crossings and killing at least 9 (7 in Kyiv, 2 in Lviv).",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", beat="Weather", dl="Cyclone", place="Odisha, India",
         src="IMD, The Hindu", tag="OFFICIAL",
         headline="Cyclone Akvan Makes Landfall\nNear Gopalpur in Eastern India",
         summary="The storm crossed the Odisha coast around 8 am local time and then weakened "
                 "inland; up to 372,000 people were moved to shelters and no deaths have been "
                 "reported.",
         art="art_02.png", pin=(84.8, 19.4)),
    dict(n=3, kind="hero", region="GLOBAL/SCIENCE", beat="Markets", dl="AI rout",
         place="Global markets", src="Reuters, CNBC", tag="CONFIRMED",
         headline="Global AI Sell-Off Sends the\nS&P 500 Into a Correction",
         summary="The Nasdaq falls −5.3% and the S&P 500 −3.7% after Taiwan’s Taiex closes "
                 "−6.23%, Korea’s Kospi −5.21% and Japan’s Nikkei −5.06%, Asia’s worst week "
                 "since 2020.",
         art="art_03.png", pin=(-74.3, 40.75)),   # Wall Street / NYC

    # --- 10 illustrated cards (grid) ----------------------------------------
    dict(n=4, kind="grid", region="AMERICAS", beat="Tech", dl="Tech", place="US",
         src="Reuters, NYT", tag="REPORTED",
         headline="Nvidia Faces US SEC Accounting Probe",
         summary="Reuters reports the SEC is examining its accounting; shares plunge.",
         art="art_04.png", pin=(-121.6, 37.3)),   # Santa Clara, California
    dict(n=5, kind="grid", region="EUROPE", beat="Diplomacy", dl="Diplomacy", place="Brussels",
         src="EU, Guardian", tag="CONFIRMED",
         headline="UK and EU Seal Post-Brexit Reset",
         summary="It cuts food checks and adds 100,000 youth mobility places a year.",
         art="art_05.png", pin=(4.35, 50.85)),
    dict(n=6, kind="grid", region="GLOBAL/SCIENCE", beat="Climate", dl="Climate", place="Antalya",
         src="UN, AFP", tag="CONFIRMED",
         headline="COP31 Hits Final Day Without a Deal",
         summary="The draft omits a fossil-fuel phase-out and talks run into overtime.",
         art="art_06.png", pin=(30.7, 36.9)),     # Antalya, Türkiye
    dict(n=7, kind="grid", region="EUROPE", beat="Security", dl="Security", place="Poland",
         src="Guardian", tag="OFFICIAL",
         headline="Russian Cruise Missile Enters Poland",
         summary="Poland’s prime minister calls the incursion an ‘intentional provocation’.",
         art="art_07.png", pin=(23.0, 51.5)),
    dict(n=8, kind="grid", region="MIDDLE EAST", beat="Shipping", dl="Maritime", place="Hormuz",
         src="UKMTO, gCaptain", tag="OFFICIAL",
         headline="Tanker Struck Near Oman in Strait of Hormuz",
         summary="The vessel is hit amid a surge in attacks on regional shipping.",
         art="art_08.png", pin=(56.3, 26.1)),     # Musandam, Oman
    dict(n=9, kind="grid", region="ASIA-PACIFIC", beat="Diplomacy", dl="Talks", place="New Delhi",
         src="Al Jazeera, PTI", tag="CONFIRMED",
         headline="Pakistani Minister Makes Rare Visit to India",
         summary="The first since the May 2025 conflict, for an SCO meeting.",
         art="art_09.png", pin=(77.2, 28.6)),
    dict(n=10, kind="grid", region="AFRICA", beat="Energy", dl="Energy", place="Kenya",
         src="The Star", tag="CONFIRMED",
         headline="Kenya Begins Drilling First Oil Well",
         summary="Drilling starts at the Amosing field; first crude targeted for Dec 1.",
         art="art_10.png", pin=(35.6, 3.1)),      # Turkana
    dict(n=11, kind="grid", region="GLOBAL/SCIENCE", beat="Medicine", dl="Medicine", place="Barcelona",
         src="EORTC, OncLive", tag="REPORTED",
         headline="Pancreatic Cancer Drug Trial Hits 60.7% Response",
         summary="Daraxonrasib plus chemo, in first-line metastatic disease.",
         art="art_11.png", pin=(1.8, 41.5)),      # Barcelona, Spain (EORTC presentation)
    dict(n=12, kind="grid", region="AMERICAS", beat="Markets", dl="Markets", place="Argentina",
         src="BA Herald, Bloomberg", tag="CONFIRMED",
         headline="Argentina Country Risk\nJumps 15% to 1,070 Points",
         summary="First close over 1,000 in 13 months in a global bond sell-off.",
         art="art_12.png", pin=(-58.6, -34.7)),   # Buenos Aires
    dict(n=13, kind="grid", region="OCEANIA", beat="Sport", dl="Cricket", place="Wellington",
         src="ICC, RNZ", tag="CONFIRMED",
         headline="Phillips Hits 118 as NZ Make 368 v India",
         summary="Glenn Phillips’ century is backed by Henry Nicholls, unbeaten on 175.",
         art="art_13.png", pin=(174.9, -41.2)),   # Wellington

    # --- 22 wire briefs, 11 per column, all 7 regions -----------------------
    # Europe
    dict(n=14, kind="brief", region="EUROPE", beat="Conflict", place="Lviv",
         text="Sknyliv rail station struck overnight, 2 killed", src="Kyiv Ind."),
    dict(n=15, kind="brief", region="EUROPE", beat="Borders", place="Estonia",
         text="Russia border to close 6+ months from Dec 1", src="Reuters"),
    dict(n=16, kind="brief", region="EUROPE", beat="Labour", place="Rome",
         text="CGIL 24-hr general strike hits 100+ cities", src="La Repubblica"),
    dict(n=17, kind="brief", region="EUROPE", beat="Protest", place="Berlin",
         text="Gen Z rally over military service in 73 cities", src="organisers"),
    # Asia-Pacific
    dict(n=18, kind="brief", region="ASIA-PACIFIC", beat="Economy", place="Tokyo",
         text="Oct CPI 2.3%, core 2.2%; BOJ hike bets rise", src="MIC"),
    dict(n=19, kind="brief", region="ASIA-PACIFIC", beat="Courts", place="Seoul",
         text="Ruling party moves to impeach top judge", src="Korea Herald"),
    dict(n=20, kind="brief", region="ASIA-PACIFIC", beat="Central banks", place="Beijing",
         text="Loan prime rates held: 1-year 3.0%, 5-year 3.5%", src="PBOC"),
    dict(n=21, kind="brief", region="ASIA-PACIFIC", beat="Health", place="Changwon",
         text="Korea’s first local cholera case in 10 years", src="KDCA"),
    dict(n=22, kind="brief", region="ASIA-PACIFIC", beat="Disinformation", place="Taipei",
         text="2,700 China-linked accounts flagged to Meta", src="Reuters"),
    dict(n=23, kind="brief", region="ASIA-PACIFIC", beat="Diplomacy", place="Shenzhen",
         text="Xi meets Anwar, hails Albanese ‘turnaround’", src="ABC"),
    # Americas
    dict(n=24, kind="brief", region="AMERICAS", beat="Central banks", place="Washington",
         text="Fed’s Cook: hikes needed on high inflation", src="WSJ"),
    dict(n=25, kind="brief", region="AMERICAS", beat="Weather", place="Brevard, FL",
         text="Record floods: emergency, 100+ rescues", src="NWS"),
    # Global / science
    dict(n=26, kind="brief", region="GLOBAL/SCIENCE", beat="Wildlife", place="Amazon",
         text="25-year camera traps benchmark the bush dog", src="WCS"),
    # Middle East
    dict(n=27, kind="brief", region="MIDDLE EAST", beat="Security", place="Iraq",
         text="Army enters Kataib Hezbollah base on PM’s order", src="Reuters"),
    dict(n=28, kind="brief", region="MIDDLE EAST", beat="Conflict", place="Gaza",
         text="Israeli strikes kill 6 despite truce, rescuers say", src="Al Jazeera"),
    dict(n=29, kind="brief", region="MIDDLE EAST", beat="Defence", place="Riyadh",
         text="Coalition intercepts 1 Houthi missile and 5 drones", src="AP"),
    dict(n=30, kind="brief", region="MIDDLE EAST", beat="Piracy", place="Mukalla",
         text="Skiff fires on ship 95 nm SW; guards repel it", src="UKMTO"),
    # Africa
    dict(n=31, kind="brief", region="AFRICA", beat="Migration", place="Dakar",
         text="Migration declaration and roadmap adopted", src="IOM"),
    dict(n=32, kind="brief", region="AFRICA", beat="Markets", place="Johannesburg",
         text="Rand hits 1-year low on coalition jitters", src="Reuters"),
    dict(n=33, kind="brief", region="AFRICA", beat="Debt", place="Abidjan",
         text="22 states in or at high risk of debt distress", src="AfDB"),
    dict(n=34, kind="brief", region="AFRICA", beat="Energy", place="Lilongwe",
         text="Fuel queues persist despite $30m release", src="Al Jazeera"),
    # Oceania
    dict(n=35, kind="brief", region="OCEANIA", beat="Business", place="Sydney",
         text="David Jones fails; 1,689 redundancy notices", src="receivers"),
]

REGION_ORDER = ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA", "GLOBAL/SCIENCE"]
REGION_LABEL = {"GLOBAL/SCIENCE": "GLOBAL/SCI."}
REGION_COLORS = mapgen.REGION_COLORS
REGION_COUNTS = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGION_ORDER}
BEATS = sorted({s["beat"] for s in STORIES})
TAG_COLORS = {
    "CONFIRMED": ("#17605B", "#DCEDEA"),
    "OFFICIAL": ("#16243A", "#E2E7EF"),
    "REPORTED": ("#8F500E", "#F5E6D2"),
}

STATS = [
    ("3", "Kyiv Dnipro bridges hit in 111-missile barrage"),
    ("372,000", "evacuated in Odisha as Cyclone Akvan lands"),
    ("−5.3%", "Nasdaq drop (S&P −3.7%, Taiex −6.2%) in AI rout"),
    ("60.7%", "pancreatic cancer response in daraxonrasib trial"),
    ("100,000", "annual youth mobility places in UK–EU reset"),
    ("118", "Glenn Phillips runs as NZ make 368 vs India"),
]
STAT_SOURCES = {
    "3": (1, "three Dnipro"),
    "372,000": (2, "372,000"),
    "−5.3%": (3, "−5.3%"),
    "60.7%": (11, "60.7%"),
    "100,000": (5, "100,000"),
    "118": (13, "118"),
}
STAT_EXTRA = {
    "3": (1, ["111 missiles"]),
    "−5.3%": (3, ["−3.7%", "−6.23%"]),
    "60.7%": (11, ["Daraxonrasib"]),
}

TIMELINE = [
    ("OVERNIGHT", 1, "Kyiv bridges hit"),
    ("~02:30Z", 2, "Akvan landfall"),
    ("ASIA CLOSE", 3, "Taiex −6.2%"),
    ("EUROPE DAY", 5, "UK–EU reset"),
    ("15:50Z", 11, "Cancer trial 60.7%"),
    ("21:37Z", 4, "Nvidia SEC · S&P −3.7%"),
]
TL_CLOCKS = {"~02:30Z", "15:50Z", "21:37Z"}

DECK = ("Missiles hit three Kyiv bridges · Cyclone Akvan lands in Odisha · "
        "AI rout pulls the S&P 500 into correction · SEC probes Nvidia · UK and EU seal reset")

DC_L1 = (
    "Excluded (Thu 19 Nov):",
    "Trump–Xi–Putin Shenzhen talks, Anthropic’s $83 IPO, ICJ Myanmar ruling, GTA VI launch, "
    "Bukele’s 3rd-term bid, Kyiv embassy damage, Tonga drought & Senate Iran vote."
)
DC_L2 = (
    "Wed 18 Nov:",
    "Voyager 1 light-day.",
    "Not yet confirmed on Fri 20 Nov:",
    "BepiColombo Mercury orbit capture, COP31 next draft (Sat 21 Nov) & ATP Finals final (Sun 22 Nov)."
)
FOOT_L = "Every story happened, or was first reported, on Fri 20 Nov 2026 (UTC)."
FOOT_R = "Sources named beside each story · Original drawings"

# Words reserved strictly for DATE CHECK, never inside any story
DATECHECK_ONLY = [
    "BepiColombo", "Mercury", "Saturday", "Thursday", "19 Nov", "21 Nov", "ICJ",
    "Putin", "Pentagon", "48.3bn", "Anthropic", "Voyager", "GTA", "Myanmar",
    "Bukele", "embass", "Tonga", "Senate", "Iran",
]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def badge(s: dict, cls: str = "num") -> str:
    return f'<span class="{cls}" style="background:{REGION_COLORS[s["region"]]}">{s["n"]}</span>'


def keep_hyphens(text: str) -> str:
    return re.sub(r"(\S+-\S+)", r'<span class="nb">\1</span>', esc(text))


def headline_html(s: dict) -> str:
    return "<br>".join(keep_hyphens(line) for line in s["headline"].split("\n"))


def card_html(s: dict) -> str:
    col = REGION_COLORS[s["region"]]
    fg, bg = TAG_COLORS[s["tag"]]
    where = f"{s['place']} · {s['dl']}"
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place" style="color:{col}"><span class="pt">{esc(where)}</span></span><span class="tg" style="color:{fg};background:{bg}">{s['tag']}</span></div>
      <h2><span class="hl">{headline_html(s)}</span></h2>
      <p class="summary"><span class="sum">{esc(s['summary'])} <span class="src">({esc(s['src'])})</span></span></p>
    </article>'''


def brief_html(s: dict) -> str:
    return f'''
      <div class="brief" data-story="{s['n']}" data-region="{esc(s['region'])}">
        <span class="bnum" style="background:{REGION_COLORS[s['region']]}">{s['n']}</span><p class="btext"><span class="bt"><b>{esc(s['place'])}</b> {esc(s['text'])} <i>({esc(s['src'])})</i></span></p>
      </div>'''


def measure_briefs() -> dict[int, float]:
    bold = ImageFont.truetype(str(LATO / "Lato-Bold.ttf"), BRIEF_PX)
    reg = ImageFont.truetype(str(LATO / "Lato-Regular.ttf"), BRIEF_PX)
    ital = ImageFont.truetype(str(LATO / "Lato-Italic.ttf"), BRIEF_PX)
    out = {}
    for s in STORIES:
        if s["kind"] != "brief":
            continue
        w = (BNUM_W + BNUM_GAP + bold.getlength(s["place"])
             + reg.getlength(" " + s["text"] + " ")
             + ital.getlength(f"({s['src']})"))
        out[s["n"]] = round(w, 1)
    return out


def timeline_html() -> str:
    steps = "".join(
        f'<div class="ts" data-story="{n}"><b class="tw">{esc(w)}</b>'
        f'<span class="tx">{esc(t)}</span></div>' for w, n, t in TIMELINE)
    return (f'<div class="band timeline"><div class="tlhead">The day in UTC</div>'
            f'<div class="tlrail">{steps}</div></div>')


def footer_legend_html() -> str:
    pills = []
    for tag, desc in (("CONFIRMED", "2+ outlets"), ("OFFICIAL", "on the record"), ("REPORTED", "single outlet")):
        fg, bg = TAG_COLORS[tag]
        pills.append(f'<span class="ftg" style="color:{fg};background:{bg}">{tag}</span><span>{esc(desc)}</span>')
    return f'<div class="fleg">{"".join(pills)}</div>'


def datecheck_html() -> str:
    return f'''
  <div class="band datecheck">
    <div class="dcbadge">DATE CHECK</div>
    <div class="dclines">
      <div class="dl"><b>{esc(DC_L1[0])}</b> {esc(DC_L1[1])}</div>
      <div class="dl"><b>{esc(DC_L2[0])}</b> {esc(DC_L2[1])} &nbsp;<b>{esc(DC_L2[2])}</b> {esc(DC_L2[3])}</div>
    </div>
  </div>
  <div class="band footer">
    <div class="fl">{esc(FOOT_L)}</div>
    {footer_legend_html()}
    <div class="fr">{esc(FOOT_R)}</div>
  </div>'''


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
.deck {{ top:79px; height:19px; font:italic 700 14px/18px 'LibSerif'; color:#2A303A; text-align:center; white-space:nowrap; border-bottom:1px solid #121822; }}
.stats {{ top:102px; height:52px; display:flex; }}
.stat {{ flex:1 1 0; min-width:0; position:relative; padding:0 8px 0 11px; display:flex; flex-direction:column; justify-content:center; }}
.stat::before {{ content:''; position:absolute; left:0; top:4px; bottom:4px; width:3px; background:#B8292F; }}
.stat + .stat {{ margin-left:8px; }}
.stat + .stat::after {{ content:''; position:absolute; left:-5px; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.stat b {{ font:700 25px/26px 'LibSerif'; color:#121822; white-space:nowrap; }}
.stat .sx {{ font:400 10.5px/12.5px 'LatoX'; color:#2A303A; height:25px; overflow:hidden; }}
.timeline {{ top:157px; height:{TL_H}px; display:flex; align-items:stretch; gap:{TL_GAP}px; white-space:nowrap; overflow:hidden; }}
.tlhead {{ flex:0 0 auto; display:flex; align-items:center; padding:0 7px; background:#B8292F; color:#FFF; font:900 10px/1 'LatoX'; letter-spacing:.06em; text-transform:uppercase; border-radius:2px; }}
.tlrail {{ flex:1; min-width:0; display:flex; gap:{TL_GAP}px; }}
.ts {{ flex:1 1 auto; min-width:max-content; display:flex; align-items:center; justify-content:center; gap:5px; padding:0 6px; background:#FFFDF7; border:1px solid #D3C9B6; border-radius:2px; }}
.tw {{ font:900 9.5px/14px 'LatoX'; letter-spacing:.02em; color:#B8292F; }}
.tx {{ font:700 10px/14px 'LatoX'; color:#121822; }}
.regionbar {{ top:178px; height:15px; display:flex; gap:2px; }}
.rg {{ min-width:max-content; padding:0 5px; display:flex; align-items:center; justify-content:center; gap:5px; color:#FFF; white-space:nowrap; overflow:hidden; }}
.rg span {{ font:900 10px/1 'LatoX'; letter-spacing:.05em; }}
.rg b {{ font:900 10.5px/1 'LatoX'; }}
.row {{ display:flex; }}
.row.heroes {{ top:197px; height:239px; gap:20px; }}
.row.grid {{ height:158px; gap:12px; }}
.row.g1 {{ top:441px; }}
.row.g2 {{ top:604px; }}
.rule {{ position:absolute; left:18px; right:18px; height:0; border-top:1px solid #DCD6C8; }}
.card {{ position:relative; display:flex; flex-direction:column; }}
.card + .card::before {{ content:''; position:absolute; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.hero + .hero::before {{ left:-10.5px; }}
.grid + .grid::before {{ left:-6.5px; }}
.card.hero {{ width:316px; }}
.card.grid {{ width:188px; }}
.art {{ display:block; outline:1px solid #C8C2B4; }}
.hero .art {{ width:316px; height:{art.HERO[1]}px; }}
.grid .art {{ width:188px; height:{art.GRID[1]}px; }}
.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:4px; }}
.grid .kicker {{ height:14px; margin-top:4px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; line-height:14px; }}
.place {{ flex:1; min-width:0; font:900 10px/12px 'LatoX'; height:12px; letter-spacing:.05em; text-transform:uppercase; white-space:nowrap; overflow:hidden; }}
.grid .place {{ font-size:{GRID_DL_PX}px; letter-spacing:.015em; }}
.tg {{ flex:0 0 auto; margin-left:auto; padding:1px 4px 0; border-radius:1.5px; font:900 9px/11px 'LatoX'; letter-spacing:.03em; white-space:nowrap; }}
.grid .tg {{ padding:1px 2.5px 0; letter-spacing:.01em; }}
h2 {{ margin:3px 0 0 0; font:700 20px/21px 'LibSerif'; color:#0E121A; letter-spacing:-.006em; white-space:nowrap; }}
.nb {{ white-space:nowrap; }}
.grid h2 {{ margin-top:3px; font-size:14px; line-height:15.5px; letter-spacing:-.003em; white-space:normal; text-wrap:balance; }}
.summary {{ margin:3px 0 0 0; font:400 10.8px/13px 'LatoX'; color:#272D36; }}
.grid .summary {{ font-size:10px; line-height:12.2px; }}
.src {{ font-style:italic; color:#5C616A; }}
.bottom {{ top:766px; height:189px; display:flex; gap:14px; border-top:2.5px solid #121822; padding-top:3px; }}
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
.brief {{ height:{BRIEF_ROW}px; display:flex; align-items:center; gap:{BNUM_GAP}px; padding:0 {BRIEF_PAD}px; border-radius:2px; }}
.bcol .brief:nth-child(odd) {{ background:#F5F0E6; }}
.bnum {{ flex:0 0 {BNUM_W}px; width:{BNUM_W}px; height:{BNUM_W}px; border-radius:50%; color:#FFF; text-align:center; font:900 {BNUM_PX}px/{BNUM_W}px 'LatoX'; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
.btext {{ margin:0; font:400 {BRIEF_PX}px/14px 'LatoX'; color:{BRIEF_INK}; white-space:nowrap; }}
.btext b {{ font-weight:700; color:{BRIEF_INK}; }}
.btext i {{ color:#4B5563; }}
.datecheck {{ top:958px; height:44px; border:1.5px solid #B8292F; background:#FFFDF9; display:flex; align-items:center; gap:7px; padding:0 6px; }}
.dcbadge {{ flex:0 0 auto; background:#B8292F; color:#FFF; font:900 10px/1 'LatoX'; letter-spacing:.06em; padding:5px 5px 4px; border-radius:3px; white-space:nowrap; }}
.dclines {{ flex:1; min-width:0; }}
.dl {{ font:400 9.5px/14px 'LatoX'; color:#121822; white-space:nowrap; overflow:hidden; height:14px; letter-spacing:-.028em; }}
.dl b {{ font-weight:700; color:#B8292F; }}
.footer {{ top:1005px; height:15px; display:flex; justify-content:space-between; align-items:center; font:400 9.5px/12px 'LatoX'; color:#4A4F58; white-space:nowrap; }}
.footer .fr {{ font-weight:700; color:#121822; }}
.fleg {{ display:flex; align-items:center; gap:4px; font:400 9.2px/12px 'LatoX'; color:#4A4F58; }}
.fleg span:not(.ftg) {{ margin-right:5px; }}
.ftg {{ display:inline-block; padding:1px 3.5px 0; border-radius:1.5px; font:900 8.5px/10.5px 'LatoX'; letter-spacing:.02em; }}
</style></head>
<body><div class="page">
  <div class="band kickerbar"><div class="l">The world in one day</div><div class="r">{total} stories · 7 regions · {len(BEATS)} beats · every story dated Friday 20 November 2026</div></div>
  <div class="band masthead">Friday 20 November 2026</div>
  <div class="band deck">{esc(DECK)}</div>
  <div class="band stats">{stats}</div>
  {timeline_html()}
  <div class="band regionbar">{regions}</div>
  <div class="band row heroes">{''.join(card_html(s) for s in heroes)}</div>
  <div class="rule" style="top:438.5px"></div>
  <div class="band row grid g1">{''.join(card_html(s) for s in grid[:5])}</div>
  <div class="rule" style="top:601.5px"></div>
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
  {datecheck_html()}
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
  document.querySelectorAll('.page,.timeline,.tlhead,.tlrail,.ts,.kickerbar,.masthead,.deck,.regionbar,.rg,.stats,.stat,.stat span,.card,.kicker,.place,.bottom,.mapbox,.mapcap,.briefcol,.bcol,.brief,.btext,.datecheck,.dclines,.dl,.secthead,.mapcol,.footer').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });
  const textClip = [];
  document.querySelectorAll('.dl,.rg,.place,.mapcap,.stat .sx,.footer > div,.btext,.tlhead,.ts').forEach(el => {
    const range = document.createRange(); range.selectNodeContents(el);
    const rr = range.getBoundingClientRect(), r = R(el);
    if (rr.right > r.right + 0.5 || rr.bottom > r.bottom + 0.5)
      textClip.push({cls: el.className, text: el.textContent.slice(0, 35), over: +(rr.right - r.right).toFixed(1)});
  });

  const lines = el => { const rs = [...el.getClientRects()].filter(r => r.width > 0); return new Set(rs.map(r => Math.round(r.top))).size; };
  const blockOverlaps = [];
  cards.forEach(c => {
    const cr = R(c);
    const els = ['.art', '.kicker', 'h2', '.summary'].map(s => c.querySelector(s));
    els.forEach((e, i) => {
      const r = R(e);
      if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: e.className || e.tagName, why: 'leaves card', by: +(r.bottom - cr.bottom).toFixed(1)});
      if (i < els.length - 1 && r.bottom > R(els[i + 1]).y + 0.5) blockOverlaps.push({card: c.dataset.story, a: e.className || e.tagName, b: els[i + 1].className || els[i + 1].tagName});
    });
    ['.hl', '.sum'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped'}); });
  });
  const bands = [...document.querySelectorAll('.band')].filter(e => e.offsetHeight > 0);
  const bandOverlaps = [];
  for (let i = 0; i < bands.length - 1; i++) { const a = R(bands[i]), b = R(bands[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bands[i].className, b: bands[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const bc = R(document.querySelector('.briefcol')), bt = R(document.querySelector('.bottom'));
  [...document.querySelectorAll('.bcol')].forEach(e => { if (R(e).bottom > bc.bottom + 0.5) blockOverlaps.push({el: 'bcol', why: 'leaves wire column', by: R(e).bottom - bc.bottom}); });
  [...document.querySelectorAll('.mapcol > *')].forEach(e => { if (R(e).bottom > bt.bottom + 0.5) blockOverlaps.push({el: e.className, why: 'leaves map column', by: R(e).bottom - bt.bottom}); });
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox'), document.querySelector('.datecheck')];
  const cardOverlaps = [];
  boxes.forEach((a, i) => boxes.forEach((b, j) => { if (j > i && ov(R(a), R(b))) cardOverlaps.push([a.dataset.story || a.className, b.dataset.story || b.className]); }));

  const tl = document.querySelector('.timeline'), tlr = R(tl);
  const tsteps = [...tl.querySelectorAll('.ts')];
  const timeline = {h: +tlr.h.toFixed(2), top: tlr.y, bottom: tlr.bottom,
    when: tsteps.map(t => t.querySelector('.tw').textContent), stories: tsteps.map(t => +t.dataset.story),
    lines: tsteps.map(t => lines(t.querySelector('.tx'))),
    inside: [...tl.children, ...tsteps].every(e => { const r = R(e); return r.x >= tlr.x - 0.5 && r.right <= tlr.right + 0.5 && r.y >= tlr.y - 0.5 && r.bottom <= tlr.bottom + 0.5; }),
    gaps: tsteps.slice(1).map((t, i) => +(R(t).x - R(tsteps[i]).right).toFixed(1)),
    railEnd: +(R(tl.querySelector('.tlrail')).right - R(tsteps[tsteps.length - 1]).right).toFixed(1),
    cellH: tsteps.map(t => +R(t).h.toFixed(2)),
    cellBg: tsteps.map(t => getComputedStyle(t).backgroundColor),
    cellBorder: tsteps.map(t => getComputedStyle(t).borderTopWidth + ' ' + getComputedStyle(t).borderTopColor),
    stripBg: getComputedStyle(tl).backgroundColor,
    head: tl.querySelector('.tlhead').textContent,
    text: tl.textContent};

  const svg = document.querySelector('.mapsvg');
  const SW = +svg.getAttribute('width'), SH = +svg.getAttribute('height');
  const pins = [...document.querySelectorAll('.pin circle')].map(c => ({n: +c.parentNode.dataset.pin, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')}));
  const pinOverlaps = [];
  pins.forEach((a, i) => pins.forEach((b, j) => { if (j > i && Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r + 1.5 + 3) pinOverlaps.push([a.n, b.n]); }));
  const pinsOutside = pins.filter(p => p.x - p.r < 0 || p.y - p.r < 0 || p.x + p.r > SW || p.y + p.r > SH).map(p => p.n);
  const pinNumbers = pins.map(p => p.n);
  const pinR = pins.map(p => p.r);
  const pinLabels = [...document.querySelectorAll('.pin text')].map(t => +t.textContent);

  const headlineLines = cards.map(c => lines(c.querySelector('.hl')));
  const summaryLines = cards.map(c => lines(c.querySelector('.sum')));
  const briefLines = briefs.map(b => lines(b.querySelector('.bt')));
  const briefWidths = briefs.map(b => +(R(b.querySelector('.bt')).right - R(b).x - parseFloat(getComputedStyle(b).paddingLeft)).toFixed(1));
  const briefRows = briefs.map(b => ({h: +R(b).h.toFixed(2), fs: parseFloat(getComputedStyle(b.querySelector('.btext')).fontSize), color: getComputedStyle(b.querySelector('.btext')).color, bg: getComputedStyle(b).backgroundColor, inside: R(b.querySelector('.bt')).right <= R(b).right - parseFloat(getComputedStyle(b).paddingRight) + 0.5}));
  const statLines = [...document.querySelectorAll('.stat .s2')].map(lines);
  const tagCount = document.querySelectorAll('.card .tg').length;
  const datelines = cards.map(c => { const k = c.querySelector('.kicker'), t = c.querySelector('.pt'), g = k.querySelector('.tg');
    const tr = t.getBoundingClientRect(), gr = g ? g.getBoundingClientRect() : null, kr = k.getBoundingClientRect();
    return {n: +c.dataset.story, text: t.textContent, lines: lines(t),
            tag: g ? g.textContent : null, tagBg: g ? getComputedStyle(g).backgroundColor : null,
            tagFs: g ? parseFloat(getComputedStyle(g).fontSize) : 0, tagsInKicker: k.querySelectorAll('.tg').length,
            tagsInBody: c.querySelectorAll('h2 .tg, .summary .tg').length,
            gap: gr ? +(gr.left - tr.right).toFixed(1) : -1,
            tagRightInset: gr ? +(kr.right - gr.right).toFixed(1) : -1,
            tagMidDy: gr ? +Math.abs((gr.top + gr.bottom) / 2 - (tr.top + tr.bottom) / 2).toFixed(1) : -1}; });
  const briefNums = briefs.map(b => { const n = b.querySelector('.bnum'), cs = getComputedStyle(n);
    const nr = R(n), br = R(b);
    return {n: +n.textContent, region: b.dataset.region, bg: cs.backgroundColor, radius: cs.borderRadius, fs: parseFloat(cs.fontSize), fw: cs.fontWeight,
            w: +nr.w.toFixed(2), h: +nr.h.toFixed(2), midDy: +Math.abs((nr.top + nr.bottom) / 2 - (br.top + br.bottom) / 2).toFixed(2)}; });
  const cardSources = cards.map(c => ({n: +c.dataset.story, src: (c.querySelector('.summary .src') || {}).textContent || ''}));
  const heroBottoms = cards.filter(c => c.classList.contains('hero')).map(c => +R(c.querySelector('.sum')).bottom.toFixed(1));
  const footerLegend = document.querySelector('.fleg').textContent;

  let minHtml = 99, minHtmlText = '', minSvg = 99, minDl = 99;
  document.querySelectorAll('body *').forEach(el => {
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (el instanceof SVGElement) { minSvg = Math.min(minSvg, fs); return; }
    if (el.classList.contains('tg') || el.classList.contains('ftg') || el.closest('.fleg')) return;
    if (el.closest('.grid .place')) { minDl = Math.min(minDl, fs); return; }
    if (fs < minHtml) { minHtml = fs; minHtmlText = el.textContent.trim().slice(0, 30); }
  });
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
  ['.timeline', '.regionbar', '.row.heroes', '.row.g1', '.row.g2', '.bottom', '.mapbox', '.datecheck', '.footer'].forEach(s => { const r = R(document.querySelector(s)); rects[s] = [r.x, r.y, r.right, r.bottom].map(v => +v.toFixed(1)); });
  const cardBottoms = cards.map(c => +(R(c.querySelector('.summary')).bottom - R(c).y).toFixed(1));
  return {doc, timeline, stories, regionCounts, regionTagged, overflows, textClip, blockOverlaps, bandOverlaps, cardOverlaps,
          tagCount, datelines, briefNums, cardSources, heroBottoms, footerLegend, pinCount: pins.length, pinNumbers, pinLabels, pinR, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          briefWidths, briefRows, statLines, minHtml, minHtmlText, minSvg, minDl, imagesLoaded, artSizes, stats, kicker,
          pageBottom: R(document.querySelector('.footer')).bottom, rects, cardBottoms,
          wireSlack: +(bc.bottom - Math.max(...[...document.querySelectorAll('.bcol')].map(e => R(e).bottom))).toFixed(1),
          mapSlack: +(bt.bottom - R(document.querySelector('.mapcap')).bottom).toFixed(1),
          dateCheckText, pageTextNoDC, dcBorder: getComputedStyle(dc).borderTopColor, dcBg: getComputedStyle(dc).backgroundColor};
}'''


def check_stories() -> list[str]:
    f = []
    for s in STORIES:
        body = " ".join(str(v) for k, v in s.items() if isinstance(v, str))
        for w in DATECHECK_ONLY:
            if w.lower() in body.lower():
                f.append(f"story {s['n']} contains date-check-only text '{w}'")
    nums = [s["n"] for s in STORIES]
    if nums != list(range(1, 36)):
        f.append(f"v19 needs stories 1-35 in order, got {nums}")
    kinds = [s["kind"] for s in STORIES]
    if kinds != ["hero"] * 3 + ["grid"] * 10 + ["brief"] * 22:
        f.append("v19 needs 3 leads, 10 cards and 22 briefs")
    for w, sn, _ in TIMELINE:
        if sn not in nums:
            f.append(f"timeline step {w} points at missing story {sn}")
        if re.search(r"\d", w) and w not in TL_CLOCKS:
            f.append(f"timeline clock time {w} is not allowed")
    briefs = [s for s in STORIES if s["kind"] == "brief"]
    if {s["region"] for s in briefs} != set(REGION_ORDER):
        f.append(f"briefs cover only {sorted({s['region'] for s in briefs})}")
    for n, w in measure_briefs().items():
        if w > BRIEF_MAX_W:
            f.append(f"brief {n} is {w}px wide at {BRIEF_PX}px; max {BRIEF_MAX_W}px on one line")
    for v, (sn, phrase) in STAT_SOURCES.items():
        s = STORIES[sn - 1]
        if phrase not in s["headline"].replace("\n", " ") + " " + s["summary"]:
            f.append(f"stat {v} not backed by story {sn} ('{phrase}')")
    for v, (sn, phrases) in STAT_EXTRA.items():
        s = STORIES[sn - 1]
        for phrase in phrases:
            if phrase not in s["summary"]:
                f.append(f"stat {v} label figure '{phrase}' not in story {sn}")
    if len(BEATS) < 25:
        f.append(f"only {len(BEATS)} beats")
    if "estonia" in (DC_L1[1] + DC_L2[1]).lower():
        f.append("DATE CHECK must not mention Estonia (contradicts story #15)")
    return f


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    t = a["timeline"]
    if t["h"] != TL_H or not t["inside"] or any(x != 1 for x in t["lines"]):
        f.append(f"timeline strip must be {TL_H}px, one line, nothing outside: {t}")
    if t["when"] != [w for w, _, _ in TIMELINE] or t["stories"] != [sn for _, sn, _ in TIMELINE]:
        f.append(f"timeline steps {t['when']} {t['stories']}")
    if any(abs(g - TL_GAP) > 0.5 for g in t["gaps"]) or abs(t["railEnd"]) > 0.5:
        f.append(f"timeline gaps {t['gaps']} end {t['railEnd']}")
    if t["head"] != "The day in UTC" or t["stripBg"] not in ("rgba(0, 0, 0, 0)", "transparent") \
            or any(h != TL_H for h in t["cellH"]) or set(t["cellBg"]) != {"rgb(255, 253, 247)"} \
            or set(t["cellBorder"]) != {"1px rgb(211, 201, 182)"}:
        f.append(f"timeline style mismatch")
    clocks = set(re.findall(r"~?\d{1,2}:\d{2}Z?", t["text"]))
    if clocks - TL_CLOCKS:
        f.append(f"unpublished clock times on timeline: {clocks - TL_CLOCKS}")
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
    if any(x != 2 for x in a["headlineLines"]):
        f.append(f"headline lines must all be 2: {a['headlineLines']}")
    want = [3] * 3 + [2] * 10
    if a["summaryLines"] != want:
        f.append(f"summary lines {a['summaryLines']} != {want}")
    if len(set(a["heroBottoms"])) != 1:
        f.append(f"lead summaries end on different baselines: {a['heroBottoms']}")
    if a["tagCount"] != 13:
        f.append(f"{a['tagCount']} certainty pills; need 13")
    for d in a["datelines"]:
        s = STORIES[d["n"] - 1]
        if "·" not in d["text"] or d["text"] != f"{s['place']} · {s['dl']}":
            f.append(f"dateline {d['n']} is '{d['text']}', not PLACE · BEAT")
        if d["lines"] != 1:
            f.append(f"dateline {d['n']} '{d['text']}' wraps to {d['lines']} lines")
        if d["tag"] != s["tag"] or d["tag"] not in TAG_COLORS or d["tagsInKicker"] != 1 or d["tagsInBody"]:
            f.append(f"dateline {d['n']} pill mismatch")
        if d["tagFs"] < 9:
            f.append(f"dateline {d['n']} pill font {d['tagFs']}px < 9px")
        if d["gap"] < DATELINE_GAP:
            f.append(f"dateline {d['n']} '{d['text']}' is {d['gap']}px from {d['tag']} pill; needs {DATELINE_GAP}px")
        if d["tagRightInset"] > 0.5 or d["tagMidDy"] > 1.5:
            f.append(f"dateline {d['n']} pill alignment inset={d['tagRightInset']} midDy={d['tagMidDy']}")
    def rgb(hexcol: str) -> str:
        return "rgb({}, {}, {})".format(*(int(hexcol[i:i + 2], 16) for i in (1, 3, 5)))
    if [b["n"] for b in a["briefNums"]] != [s["n"] for s in STORIES if s["kind"] == "brief"]:
        f.append(f"brief numbers {[b['n'] for b in a['briefNums']]}")
    for c in a["cardSources"]:
        if c["src"] != f"({STORIES[c['n'] - 1]['src']})" or not STORIES[c["n"] - 1]["src"].strip():
            f.append(f"card {c['n']} caption missing sources: {c['src']!r}")
    for b in a["briefNums"]:
        if b["bg"] != rgb(REGION_COLORS[b["region"]]) or b["radius"] != "50%" or b["w"] != BNUM_W \
                or b["h"] != BNUM_W or b["fs"] != BNUM_PX or b["fw"] != "900" or b["midDy"] > 0.5:
            f.append(f"brief number disc mismatch: {b}")
    if any(x != 1 for x in a["briefLines"]):
        f.append(f"briefs must be one line: {a['briefLines']}")
    if max(a["briefWidths"]) > BRIEF_MAX_W:
        f.append(f"brief widths {a['briefWidths']}")
    rows = a["briefRows"]
    if any(r["h"] != BRIEF_ROW or r["fs"] != BRIEF_PX or r["color"] != "rgb(17, 24, 39)" or not r["inside"]
           for r in rows):
        f.append("brief rows geometry mismatch")
    tints = [r["bg"] for r in rows]
    if len(set(tints)) != 2 or tints[0] == tints[1]:
        f.append(f"brief rows must alternate tint: {tints}")
    if any(x != 2 for x in a["statLines"]):
        f.append(f"stat explanations must be 2 lines: {a['statLines']}")
    if a["minDl"] < GRID_DL_PX:
        f.append(f"card dateline font {a['minDl']}px < {GRID_DL_PX}px")
    if a["minHtml"] < 9.5:
        f.append(f"html font {a['minHtml']} ({a['minHtmlText']})")
    if a["minSvg"] < 10:
        f.append(f"svg font {a['minSvg']}")
    if not a["imagesLoaded"]:
        f.append("image failed to load")
    if any(nw != w or nh != h for nw, nh, w, h in a["artSizes"]):
        f.append(f"art scaled in page: {a['artSizes']}")
    if a["pageBottom"] > 1020:
        f.append(f"page bottom {a['pageBottom']}")
    if a["stats"] != [v for v, _ in STATS]:
        f.append(f"stats {a['stats']}")
    if not a["kicker"].startswith(f"{n} stories") or f"{len(BEATS)} beats" not in a["kicker"]:
        f.append(f"kicker {a['kicker']} beats {len(BEATS)}")
    for w in ("CONFIRMED", "OFFICIAL", "REPORTED"):
        if w not in a["footerLegend"]:
            f.append(f"footer legend missing {w}")
    for w in DATECHECK_ONLY:
        if w.lower() in a["pageTextNoDC"].lower():
            f.append(f"date-check-only text outside DATE CHECK: {w}")
    dc = a["dateCheckText"]
    for w in ["DATE CHECK", "Thu 19 Nov", "Not yet confirmed", "BepiColombo", "COP31 next draft",
              "Bukele", "embassy", "ICJ", "Putin", "Anthropic", "Voyager 1", "GTA VI", "Tonga", "Senate Iran"]:
        if w not in dc:
            f.append(f"DATE CHECK missing: {w}")
    if "estonia" in dc.lower():
        f.append("DATE CHECK must not mention Estonia")
    if a["dcBorder"] != "rgb(184, 41, 47)" or a["dcBg"] != "rgb(255, 253, 249)":
        f.append(f"DATE CHECK style {a['dcBorder']} {a['dcBg']}")
    return f


def encode_jpeg(im: Image.Image) -> tuple[bytes, int]:
    for q in QUALITIES:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True, progressive=True)
        if MIN_BYTES <= buf.tell() <= MAX_BYTES:
            return buf.getvalue(), q
        print(f"q{q}: {buf.tell()} bytes, outside {MIN_BYTES}-{MAX_BYTES}")
    raise SystemExit("entry.png cannot meet the size budget")


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
        keys = ("timeline", "pageBottom", "heroBottoms", "wireSlack", "mapSlack", "headlineLines",
                "summaryLines", "briefLines", "statLines", "cardBottoms", "minHtml", "minSvg",
                "regionCounts", "pinCount", "rects")
        print("metrics:", json.dumps({k: a[k] for k in keys}, ensure_ascii=False))
        print("brief widths (DOM):", a["briefWidths"])
        print("dateline -> pill gap (px):", {d["n"]: d["gap"] for d in a["datelines"]})
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

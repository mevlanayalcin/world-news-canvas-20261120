#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news broadsheet atlas (v18).

Run:  python3 build_poster.py
Writes: assets/art_01..13.png, assets/poster.png, entry.png (1024x1024
progressive 4:4:4 JPEG) and /tmp/news20-v18-thumb.png (300 px Lanczos proof).
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
BUILD_TMP = Path("/tmp/news_1120_v18_build")
PROOF_300 = Path("/tmp/news20-v18-thumb.png")
MIN_BYTES, MAX_BYTES = 200_000, 365_000
QUALITIES = (91, 90, 89, 88, 86, 84, 82, 81, 80, 79, 78)

LATO = Path("/usr/share/fonts/truetype/lato")
BRIEF_PX = 10.2          # crisp brief type size (26 briefs, 13 per column)
BRIEF_ROW = 15           # exact integer pitch: 13 * 15 = 195 px
BRIEF_PAD = 3            # left/right padding inside each tinted row, px
BRIEF_MAX_W = 307        # fits inside 314 px column with padding
BNUM_PX = 9.0            # white bold number inside the region-coloured disc
BNUM_W, BNUM_GAP = 14, 4 # number disc diameter and gap before the place (px)
BRIEF_INK = "#111827"
GRID_DL_PX = 9.4         # 900-weight caps dateline on the 188 px cards
DATELINE_GAP = 6         # clear px between PLACE · BEAT and its certainty pill

# ---------------------------------------------------------------------------
# The edition: 39 verified pure-Friday 20 November 2026 (UTC) stories across
# all 7 regions and 27 beats.
# kind: hero (1-3) · grid (4-13) · brief (14-39).
# ---------------------------------------------------------------------------
STORIES = [
    # --- 3 leads (hero) -----------------------------------------------------
    dict(n=1, kind="hero", region="EUROPE", beat="Conflict", dl="War", place="Kyiv, Ukraine",
         src="Kyiv Ind., Reuters", tag="OFFICIAL",
         headline="Russia hits 3 Kyiv bridges in\nmass strike, killing at least 9",
         summary="Ukraine says 111 missiles and 404 drones struck infrastructure across 15 oblasts "
                 "overnight, damaging three Dnipro crossings and cutting power and water in Kyiv.",
         art="art_01.png", pin=(30.5, 50.45)),
    dict(n=2, kind="hero", region="ASIA-PACIFIC", beat="Weather", dl="Cyclone", place="Odisha, India",
         src="IMD, The Hindu", tag="OFFICIAL",
         headline="Cyclone Akvan hits Odisha;\n372,000 evacuated, no deaths",
         summary="The storm crossed the eastern Indian coast near Gopalpur around 02:30 UTC "
                 "(8 am IST) with 70–80 km/h winds and 209 mm of rain before weakening inland.",
         art="art_02.png", pin=(84.8, 19.4)),
    dict(n=3, kind="hero", region="GLOBAL", beat="Markets", dl="AI rout", place="Global markets",
         src="Reuters, CNBC", tag="CONFIRMED",
         headline="AI rout sinks S&P 500 3.7% into\ncorrection; Nasdaq falls 5.3%",
         summary="The Nasdaq turns negative for 2026 after Taiwan’s Taiex drops 6.2%, Seoul’s "
                 "Kospi 5.2% and Tokyo’s Nikkei 5.1% in world stocks’ worst week since 2020.",
         art="art_03.png", pin=(-74.3, 40.75)),   # New York / Wall Street

    # --- 10 illustrated feature cards (grid) --------------------------------
    dict(n=4, kind="grid", region="AMERICAS", beat="Tech", dl="Tech", place="US",
         src="Reuters, NYT", tag="REPORTED",
         headline="Nvidia sinks 14% on US SEC\naccounting probe report",
         summary="SEC staff are examining its accounting; ~$500bn erased.",
         art="art_04.png", pin=(-121.6, 37.3)),   # Santa Clara / Silicon Valley
    dict(n=5, kind="grid", region="EUROPE", beat="Diplomacy", dl="EU–UK", place="Brussels",
         src="EU, Guardian", tag="OFFICIAL",
         headline="UK and EU seal post-Brexit\nreset on trade and visas",
         summary="Cuts food checks, links carbon; 100,000 youth visas/yr.",
         art="art_05.png", pin=(4.35, 50.85)),
    dict(n=6, kind="grid", region="GLOBAL", beat="Climate", dl="Climate", place="Antalya",
         src="UN, AFP", tag="CONFIRMED",
         headline="COP31 runs past deadline\nwith no fossil-fuel deal",
         summary="Closing draft omits a phase-out; climate talks stretch into overtime.",
         art="art_06.png", pin=(30.7, 36.9)),
    dict(n=7, kind="grid", region="EUROPE", beat="Security", dl="Security", place="Poland",
         src="Guardian, Reuters", tag="OFFICIAL",
         headline="Russian Kh-101 cruise\nmissile lands in Poland",
         summary="Falls in eastern field, no casualties; PM calls it provocation.",
         art="art_07.png", pin=(23.0, 51.5)),
    dict(n=8, kind="grid", region="MIDDLE EAST", beat="Maritime", dl="Shipping", place="Hormuz",
         src="UKMTO, gCaptain", tag="OFFICIAL",
         headline="Tanker set ablaze off Oman\nnear Strait of Hormuz",
         summary="No casualties reported amid rising Gulf shipping attacks.",
         art="art_08.png", pin=(56.3, 26.1)),     # Musandam, Oman
    dict(n=9, kind="grid", region="ASIA-PACIFIC", beat="Diplomacy", dl="Talks", place="India",
         src="PTI, Al Jazeera", tag="CONFIRMED",
         headline="Pakistani minister visits\nNew Delhi for SCO talks",
         summary="First ministerial visit to India since the May 2025 conflict.",
         art="art_09.png", pin=(77.2, 28.6)),     # New Delhi
    dict(n=10, kind="grid", region="AFRICA", beat="Energy", dl="Energy", place="Kenya",
         src="The Star", tag="OFFICIAL",
         headline="Kenya begins drilling its\nfirst Turkana oil well",
         summary="Work starts at the Amosing field; first crude targeted for Dec 1.",
         art="art_10.png", pin=(35.6, 3.1)),      # Turkana
    dict(n=11, kind="grid", region="GLOBAL", beat="Medicine", dl="Health", place="Barcelona",
         src="EORTC, Guardian", tag="REPORTED",
         headline="Pancreatic cancer pill hits\n60.7% tumour response",
         summary="Daraxonrasib + chemo: 8.2% clear in 61 patients.",
         art="art_11.png", pin=(1.8, 41.5)),      # Barcelona / Catalonia
    dict(n=12, kind="grid", region="AMERICAS", beat="Markets", dl="Bonds", place="Argentina",
         src="Bloomberg, BA Herald", tag="CONFIRMED",
         headline="Argentina country risk\njumps 15% to 1,070 points",
         summary="First close over 1,000 in 13 months amid global debt sell-off.",
         art="art_12.png", pin=(-58.6, -34.7)),   # Buenos Aires
    dict(n=13, kind="grid", region="OCEANIA", beat="Sport", dl="Cricket", place="NZ",
         src="ICC, RNZ", tag="CONFIRMED",
         headline="Phillips hits 118 as NZ\npost 368 against India",
         summary="Henry Nicholls adds 175 not out; India close day on 159 for 1.",
         art="art_13.png", pin=(174.9, -41.2)),   # Wellington

    # --- 26 single-line wire briefs (13 per column, all 7 regions) ----------
    # Europe (4 -> Europe total 7)
    dict(n=14, kind="brief", region="EUROPE", beat="Conflict", place="Lviv",
         text="Sknyliv rail station struck overnight, 2 killed", src="Kyiv Ind."),
    dict(n=15, kind="brief", region="EUROPE", beat="Borders", place="Estonia",
         text="Russia road border shuts 6 months from Dec 1", src="Reuters"),
    dict(n=16, kind="brief", region="EUROPE", beat="Labour", place="Rome",
         text="CGIL 24-hr general strike hits 100+ cities", src="La Repubblica"),
    dict(n=17, kind="brief", region="EUROPE", beat="Protest", place="Berlin",
         text="Gen Z march on military service in 73 cities", src="Al Jazeera"),
    # Asia-Pacific (7 -> Asia-Pacific total 9)
    dict(n=18, kind="brief", region="ASIA-PACIFIC", beat="Economy", place="Tokyo",
         text="Oct CPI 2.3%, core 2.2%; BOJ hike bets rise", src="MIC"),
    dict(n=19, kind="brief", region="ASIA-PACIFIC", beat="Law & courts", place="Seoul",
         text="Ruling party moves to impeach chief justice", src="Korea Herald"),
    dict(n=20, kind="brief", region="ASIA-PACIFIC", beat="Central banks", place="Beijing",
         text="Loan prime rates held: 1-yr 3.0%, 5-yr 3.5%", src="PBOC"),
    dict(n=21, kind="brief", region="ASIA-PACIFIC", beat="Public health", place="Changwon",
         text="Korea’s first local cholera case in 10 years", src="KDCA"),
    dict(n=22, kind="brief", region="ASIA-PACIFIC", beat="Unrest", place="Dhaka",
         text="124 held in arson wave before Hasina return", src="The Hindu"),
    dict(n=23, kind="brief", region="ASIA-PACIFIC", beat="Disinformation", place="Taipei",
         text="2,700 China-linked accounts flagged to Meta", src="Reuters"),
    dict(n=24, kind="brief", region="ASIA-PACIFIC", beat="Diplomacy", place="Shenzhen",
         text="Xi meets Anwar, hails Albanese ‘turnaround’", src="ABC"),
    # Americas (4 -> Americas total 6)
    dict(n=25, kind="brief", region="AMERICAS", beat="Law & courts", place="Virginia",
         text="Second US judge blocks Trump’s 250-ft arch", src="Guardian"),
    dict(n=26, kind="brief", region="AMERICAS", beat="Central banks", place="Washington",
         text="Fed’s Cook: hikes needed on sticky inflation", src="WSJ"),
    dict(n=27, kind="brief", region="AMERICAS", beat="Weather", place="Florida",
         text="Record St. Johns floods; 100+ rescues in Brevard", src="NWS"),
    dict(n=28, kind="brief", region="AMERICAS", beat="Politics", place="Mexico City",
         text="Sheinbaum leads 116th Revolution Day parade", src="AP"),
    # Middle East (4 -> Middle East total 5)
    dict(n=29, kind="brief", region="MIDDLE EAST", beat="Security", place="Iraq",
         text="Army enters Kataib Hezbollah base on PM’s order", src="Reuters"),
    dict(n=30, kind="brief", region="MIDDLE EAST", beat="Conflict", place="Gaza",
         text="Rescuers say Israeli strikes kill 6 despite truce", src="Al Jazeera"),
    dict(n=31, kind="brief", region="MIDDLE EAST", beat="Defence", place="Yemen",
         text="Coalition hits Hodeidah; Riyadh intercepts barrage", src="AP"),
    dict(n=32, kind="brief", region="MIDDLE EAST", beat="Piracy", place="Mukalla",
         text="Skiff fires on ship 95 nm SW; guards repel it", src="UKMTO"),
    # Africa (5 -> Africa total 6)
    dict(n=33, kind="brief", region="AFRICA", beat="Conflict", place="Sudan",
         text="Army claims gains in West Kordofan clashes", src="Anadolu"),
    dict(n=34, kind="brief", region="AFRICA", beat="Migration", place="Dakar",
         text="Regional migration roadmap adopted at summit", src="IOM"),
    dict(n=35, kind="brief", region="AFRICA", beat="Markets", place="Johannesburg",
         text="Rand hits 1-year low on coalition jitters", src="Reuters"),
    dict(n=36, kind="brief", region="AFRICA", beat="Debt", place="Abidjan",
         text="AfDB warns 22 states near or in debt distress", src="AfDB"),
    dict(n=37, kind="brief", region="AFRICA", beat="Energy", place="Lilongwe",
         text="Fuel queues persist after $30m FX release", src="Al Jazeera"),
    # Oceania (1 -> Oceania total 2)
    dict(n=38, kind="brief", region="OCEANIA", beat="Retail", place="Sydney",
         text="David Jones fails; 1,689 redundancy notices", src="receivers"),
    # Global (1 -> Global total 4)
    dict(n=39, kind="brief", region="GLOBAL", beat="Culture", place="Film",
         text="Hunger Games prequel opens; $21.25m previews", src="Variety"),
]

REGION_ORDER = ["EUROPE", "ASIA-PACIFIC", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA", "GLOBAL"]
REGION_COLORS = mapgen.REGION_COLORS
REGION_COUNTS = {r: sum(1 for s in STORIES if s["region"] == r) for r in REGION_ORDER}
BEATS = sorted({s["beat"] for s in STORIES})

# 4-level editorial certainty tags: (text, bg, border)
TAG_COLORS = {
    "CONFIRMED": ("#135A54", "#DCF0EC", "#9CCFC6"),
    "OFFICIAL": ("#16243A", "#E3E9F2", "#B5C3D8"),
    "REPORTED": ("#8F4D0B", "#F7E9D6", "#DEC097"),
    "CLAIM": ("#8C1D24", "#FCE8E9", "#E5B0B4"),
}

DECK = ("Russia hits 3 Kyiv bridges · Cyclone Akvan lands in Odisha · AI rout pulls S&P 500 into "
        "correction · SEC probes Nvidia · UK and EU seal reset")

STATS = [
    ("3", "Kyiv Dnipro bridges hit in mass barrage"),
    ("372,000", "evacuated in Odisha before Cyclone Akvan"),
    ("−3.7%", "S&P 500 drop into correction (Nasdaq −5.3%)"),
    ("−14%", "Nvidia plunge on US SEC probe report"),
    ("60.7%", "pancreatic cancer pill tumour response"),
    ("100,000", "annual youth mobility visas in UK–EU deal"),
]
STAT_SOURCES = {
    "3": (1, "3 Kyiv bridges"),
    "372,000": (2, "372,000"),
    "−3.7%": (3, "3.7%"),
    "−14%": (4, "14%"),
    "60.7%": (11, "60.7%"),
    "100,000": (5, "100,000"),
}

DC_L1_LBL = "Excluded (Thu 19 Nov):"
DC_L1_TXT = ("Trump–Xi–Putin Shenzhen talks, Anthropic’s $83 IPO debut, ICJ Rohingya/Myanmar ruling, "
             "GTA VI launch, Bukele’s 3rd-term bid, Denmark’s Greenland vote, Senate Iran vote,")
DC_L2_PRE = ("Kyiv embassy damage, Tonga drought, Uganda Ebola rally ban, Panama COP31 oil-cap call.")
DC_L2_LBL = "Excluded (Wed 18 Nov):"
DC_L2_TXT = "Voyager 1’s light-day milestone, $190.4m Van Gogh sale."
DC_L3_LBL = "Not yet confirmed / Sat 21 Nov+:"
DC_L3_TXT = ("BepiColombo Mercury orbit capture & COP31 Day 13 overtime draft (Sat 21 Nov), "
             "Peru 6.7 quake (21 Nov), ATP Finals final (Sun 22 Nov), Estonia border closure (1 Dec).")

FOOT_L = "Every story dated Fri 20 Nov 2026 (UTC)."
FOOT_R = "Sources named on every item · Original vector art"

DATECHECK_ONLY = [
    "BepiColombo", "Mercury", "Saturday", "Thursday", "19 Nov", "21 Nov", "ICJ",
    "Rohingya", "Putin", "Pentagon", "48.3bn", "Anthropic", "Voyager", "GTA",
    "Myanmar", "Bukele", "embass", "Greenland", "Denmark", "Senate", "Iran",
    "Ebola", "Tonga", "Panama", "Van Gogh", "Peru",
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


def tag_pill_html(tag: str, cls: str = "tg") -> str:
    fg, bg, bd = TAG_COLORS[tag]
    return f'<span class="{cls}" style="color:{fg};background:{bg};border-color:{bd}">{tag}</span>'


def card_html(s: dict) -> str:
    col = REGION_COLORS[s["region"]]
    where = f"{s['place']} · {s['dl']}"
    return f'''
    <article class="card {s['kind']}" data-story="{s['n']}" data-region="{esc(s['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / s['art'])}" alt="">
      <div class="kicker">{badge(s)}<span class="place" style="color:{col}"><span class="pt">{esc(where)}</span></span>{tag_pill_html(s['tag'])}</div>
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


def footer_legend_html() -> str:
    return (
        f'<div class="fleg">'
        f'{tag_pill_html("CONFIRMED", "ftg")}<span>2+ outlets</span>'
        f'{tag_pill_html("OFFICIAL", "ftg")}<span>on the record</span>'
        f'{tag_pill_html("REPORTED", "ftg")}<span>single outlet</span>'
        f'{tag_pill_html("CLAIM", "ftg")}<span>one side’s account</span>'
        f'</div>'
    )


def datecheck_html() -> str:
    return f'''
  <div class="band datecheck">
    <div class="dcbadge">DATE CHECK</div>
    <div class="dclines">
      <div class="dl"><b>{esc(DC_L1_LBL)}</b> {esc(DC_L1_TXT)}</div>
      <div class="dl">{esc(DC_L2_PRE)} <b>{esc(DC_L2_LBL)}</b> {esc(DC_L2_TXT)}</div>
      <div class="dl"><b>{esc(DC_L3_LBL)}</b> {esc(DC_L3_TXT)}</div>
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
        f'<div class="rg" data-region="{esc(r)}" data-count="{REGION_COUNTS[r]}" '
        f'style="flex:{REGION_COUNTS[r]} 1 0;background:{REGION_COLORS[r]}">'
        f'<span>{esc(r)}</span><b>{REGION_COUNTS[r]}</b></div>' for r in REGION_ORDER)
    stats = "".join(
        f'<div class="stat"><b>{esc(v)}</b><span class="sx"><span class="s2">{esc(l)}</span></span></div>'
        for v, l in STATS)
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

.kickerbar {{ top:4px; height:12px; display:flex; justify-content:space-between; align-items:center; font:900 10px/1 'LatoX'; letter-spacing:.085em; text-transform:uppercase; white-space:nowrap; }}
.kickerbar .l {{ color:#B8292F; }}

.masthead {{ top:17px; height:54px; font:700 50.5px/48px 'LibSerif'; color:#0E121A; letter-spacing:-.015em; text-align:center; white-space:nowrap; border-top:2px solid #121822; }}
.deck {{ top:71px; height:17px; font:italic 700 13.3px/16px 'LibSerif'; color:#2A303A; text-align:center; white-space:nowrap; border-bottom:1.5px solid #121822; }}

.stats {{ top:91px; height:46px; display:flex; }}
.stat {{ flex:1 1 0; min-width:0; position:relative; padding:0 7px 0 10px; display:flex; flex-direction:column; justify-content:center; }}
.stat::before {{ content:''; position:absolute; left:0; top:3px; bottom:3px; width:3px; background:#B8292F; }}
.stat + .stat {{ margin-left:7px; }}
.stat + .stat::after {{ content:''; position:absolute; left:-4.5px; top:1px; bottom:1px; border-left:1px solid #DCD6C8; }}
.stat b {{ font:700 22px/22px 'LibSerif'; color:#0E121A; white-space:nowrap; }}
.stat .sx {{ font:400 10px/11.5px 'LatoX'; color:#2A303A; height:23px; overflow:hidden; margin-top:1px; }}

.regionbar {{ top:140px; height:16px; display:flex; gap:2px; }}
.rg {{ min-width:max-content; padding:0 6px; display:flex; align-items:center; justify-content:center; gap:4px; color:#FFF; white-space:nowrap; overflow:hidden; border-radius:1.5px; }}
.rg span {{ font:900 9.6px/1 'LatoX'; letter-spacing:.05em; }}
.rg b {{ font:900 10.2px/1 'LatoX'; }}

.row {{ display:flex; }}
.row.heroes {{ top:161px; height:234px; gap:20px; }}
.row.grid {{ height:156px; gap:12px; }}
.row.g1 {{ top:401px; }}
.row.g2 {{ top:563px; }}
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

.kicker {{ display:flex; align-items:center; gap:5px; height:15px; margin-top:3.5px; }}
.grid .kicker {{ height:14px; margin-top:3.5px; gap:4px; }}
.num {{ flex:0 0 15px; width:15px; height:15px; border-radius:50%; color:#FFF; font:900 10px/15px 'LatoX'; text-align:center; }}
.grid .num {{ flex:0 0 14px; width:14px; height:14px; font-size:9.5px; line-height:14px; }}
.place {{ flex:1; min-width:0; font:900 10px/12px 'LatoX'; height:12px; letter-spacing:.045em; text-transform:uppercase; white-space:nowrap; overflow:hidden; }}
.grid .place {{ font-size:{GRID_DL_PX}px; letter-spacing:.01em; }}
.tg {{ flex:0 0 auto; margin-left:auto; padding:0.5px 4px; border:0.75px solid transparent; border-radius:2px; font:900 8.5px/10.5px 'LatoX'; letter-spacing:.025em; white-space:nowrap; }}
.grid .tg {{ padding:0.5px 3px; letter-spacing:.01em; }}

h2 {{ margin:2px 0 0 0; font:700 19.5px/20.5px 'LibSerif'; color:#0E121A; letter-spacing:-.006em; white-space:nowrap; }}
.nb {{ white-space:nowrap; }}
.grid h2 {{ margin-top:2.5px; font-size:13.6px; line-height:14.8px; letter-spacing:-.004em; white-space:nowrap; }}
.summary {{ margin:2.5px 0 0 0; font:400 10.6px/12.8px 'LatoX'; color:#272D36; }}
.grid .summary {{ margin-top:2px; font-size:9.8px; line-height:11.8px; }}
.src {{ font-style:italic; color:#5A606A; }}

.bottom {{ top:724px; height:218px; display:flex; gap:14px; border-top:2.5px solid #121822; padding-top:3px; }}
.mapcol {{ flex:0 0 {mapgen.W}px; width:{mapgen.W}px; }}
.briefcol {{ flex:1; min-width:0; position:relative; }}
.briefcol::before {{ content:''; position:absolute; left:-7.5px; top:0; bottom:0; border-left:1px solid #DCD6C8; }}
.secthead {{ height:15px; display:flex; justify-content:space-between; align-items:flex-end; font:900 10px/1 'LatoX'; letter-spacing:.08em; text-transform:uppercase; border-bottom:1px solid #121822; padding-bottom:3px; white-space:nowrap; }}
.secthead span {{ color:#B8292F; letter-spacing:.05em; }}
.mapbox {{ margin-top:3px; width:{mapgen.W}px; height:{mapgen.H}px; overflow:hidden; outline:1px solid #C4D2DE; }}
.mapsvg {{ display:block; }}
.mapcap {{ margin-top:4px; height:14px; font:italic 400 9.8px/13px 'LatoX'; color:#4A4F58; white-space:nowrap; overflow:hidden; }}

.briefgrid {{ display:flex; gap:10px; margin-top:2px; }}
.bcol {{ flex:1 1 0; min-width:0; position:relative; }}
.bcol + .bcol::before {{ content:''; position:absolute; left:-5.5px; top:2px; bottom:2px; border-left:1px solid #DCD6C8; }}
.brief {{ height:{BRIEF_ROW}px; display:flex; align-items:center; gap:{BNUM_GAP}px; padding:0 {BRIEF_PAD}px; border-radius:2px; }}
.bcol .brief:nth-child(odd) {{ background:#F5F0E6; }}
.bnum {{ flex:0 0 {BNUM_W}px; width:{BNUM_W}px; height:{BNUM_W}px; border-radius:50%; color:#FFF; text-align:center; font:900 {BNUM_PX}px/{BNUM_W}px 'LatoX'; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
.btext {{ margin:0; font:400 {BRIEF_PX}px/14px 'LatoX'; color:{BRIEF_INK}; white-space:nowrap; }}
.btext b {{ font-weight:700; color:{BRIEF_INK}; }}
.btext i {{ color:#4B5563; }}

.datecheck {{ top:947px; height:51px; border:1.5px solid #B8292F; background:#FFFDF9; display:flex; align-items:center; gap:7px; padding:0 7px; }}
.dcbadge {{ flex:0 0 auto; background:#B8292F; color:#FFF; font:900 9.5px/1 'LatoX'; letter-spacing:.06em; padding:5px 6px 4.5px; border-radius:2px; white-space:nowrap; }}
.dclines {{ flex:1; min-width:0; display:flex; flex-direction:column; justify-content:center; }}
.dl {{ font:400 9.3px/14.4px 'LatoX'; color:#121822; white-space:nowrap; overflow:hidden; height:14.4px; letter-spacing:-.008em; }}
.dl b {{ font-weight:700; color:#B8292F; }}

.footer {{ top:1003px; height:17px; display:flex; justify-content:space-between; align-items:center; font:400 9.2px/12px 'LatoX'; color:#4A4F58; white-space:nowrap; }}
.footer .fl {{ color:#4A4F58; }}
.footer .fr {{ font-weight:700; color:#121822; }}
.fleg {{ display:flex; align-items:center; gap:4px; color:#272D36; font:400 8.8px/12px 'LatoX'; }}
.fleg span:not(.ftg) {{ margin-right:4px; color:#4A4F58; }}
.ftg {{ display:inline-block; padding:0.5px 3.5px; border:0.75px solid transparent; border-radius:2px; font:900 8.0px/10px 'LatoX'; letter-spacing:.02em; }}
</style></head>
<body><div class="page">
  <div class="band kickerbar"><div class="l">The world in one day</div><div class="r">{total} stories · 7 regions · {len(BEATS)} beats · every story dated Friday 20 November 2026</div></div>
  <div class="band masthead">Friday 20 November 2026</div>
  <div class="band deck">{esc(DECK)}</div>
  <div class="band stats">{stats}</div>
  <div class="band regionbar">{regions}</div>
  <div class="band row heroes">{''.join(card_html(s) for s in heroes)}</div>
  <div class="rule" style="top:398px"></div>
  <div class="band row grid g1">{''.join(card_html(s) for s in grid[:5])}</div>
  <div class="rule" style="top:560px"></div>
  <div class="band row grid g2">{''.join(card_html(s) for s in grid[5:])}</div>
  <div class="band bottom">
    <div class="mapcol">
      <div class="secthead"><div>Where it happened</div><span>Pins 1–{len(pins)}</span></div>
      <div class="mapbox">{mapgen.svg(pins)}</div>
      <div class="mapcap">Pins 1–{len(pins)} locate the illustrated stories above · Colours match the 7 regions.</div>
    </div>
    <div class="briefcol">
      <div class="secthead"><div>Also on Friday 20 November 2026</div><span>{len(briefs)} more stories · {first_brief}–{last_brief}</span></div>
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
  const regionCounts = [...document.querySelectorAll('.rg')].map(e => ({r: e.dataset.region, c: +e.dataset.count}));
  const regionTagged = {};
  [...cards, ...briefs].forEach(e => regionTagged[e.dataset.region] = (regionTagged[e.dataset.region] || 0) + 1);

  const overflows = [];
  document.querySelectorAll('.page,.kickerbar,.masthead,.deck,.stats,.stat,.stat .sx,.regionbar,.rg,.card,.kicker,.place,.bottom,.mapbox,.mapcap,.briefcol,.bcol,.brief,.btext,.datecheck,.dclines,.dl,.secthead,.mapcol,.footer').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      overflows.push({cls: el.className, text: el.textContent.trim().slice(0, 40), sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight});
  });

  const textClip = [];
  document.querySelectorAll('.dl,.rg,.place,.mapcap,.stat .sx,.footer > div,.btext').forEach(el => {
    const range = document.createRange(); range.selectNodeContents(el);
    const rr = range.getBoundingClientRect(), r = R(el);
    if (rr.right > r.right + 0.5 || rr.bottom > r.bottom + 0.5)
      textClip.push({cls: el.className, text: el.textContent.slice(0, 35), overX: +(rr.right - r.right).toFixed(1), overY: +(rr.bottom - r.bottom).toFixed(1)});
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
    ['.hl', '.sum'].forEach(s => { const r = R(c.querySelector(s)); if (r.bottom > cr.bottom + 0.5 || r.right > cr.right + 0.5) blockOverlaps.push({card: c.dataset.story, el: s, why: 'text clipped', overX: +(r.right - cr.right).toFixed(1), overY: +(r.bottom - cr.bottom).toFixed(1)}); });
  });
  const bands = [...document.querySelectorAll('.band')].filter(e => e.offsetHeight > 0);
  const bandOverlaps = [];
  for (let i = 0; i < bands.length - 1; i++) { const a = R(bands[i]), b = R(bands[i + 1]); if (a.bottom > b.y + 0.5) bandOverlaps.push({a: bands[i].className, b: bands[i + 1].className, by: +(a.bottom - b.y).toFixed(2)}); }
  const bc = R(document.querySelector('.briefcol')), bt = R(document.querySelector('.bottom'));
  [...document.querySelectorAll('.bcol')].forEach(e => { if (R(e).bottom > bc.bottom + 0.5) blockOverlaps.push({el: 'bcol', why: 'leaves wire column', by: +(R(e).bottom - bc.bottom).toFixed(1)}); });
  [...document.querySelectorAll('.mapcol > *')].forEach(e => { if (R(e).bottom > bt.bottom + 0.5) blockOverlaps.push({el: e.className, why: 'leaves map column', by: +(R(e).bottom - bt.bottom).toFixed(1)}); });
  const boxes = [...cards, ...briefs, document.querySelector('.mapbox'), document.querySelector('.datecheck')];
  const cardOverlaps = [];
  boxes.forEach((a, i) => boxes.forEach((b, j) => { if (j > i && ov(R(a), R(b))) cardOverlaps.push([a.dataset.story || a.className, b.dataset.story || b.className]); }));

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

  let minDl = 99, minSvg = 99;
  document.querySelectorAll('.grid .place').forEach(el => { minDl = Math.min(minDl, parseFloat(getComputedStyle(el).fontSize)); });
  document.querySelectorAll('svg text').forEach(el => { minSvg = Math.min(minSvg, parseFloat(getComputedStyle(el).fontSize)); });
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
  ['.masthead', '.deck', '.stats', '.regionbar', '.row.heroes', '.row.g1', '.row.g2', '.bottom', '.mapbox', '.mapcap', '.datecheck', '.footer'].forEach(s => { const r = R(document.querySelector(s)); rects[s] = [r.x, r.y, r.right, r.bottom].map(v => +v.toFixed(1)); });
  const cardBottoms = cards.map(c => +(R(c.querySelector('.summary')).bottom - R(c).y).toFixed(1));
  return {doc, stories, regionCounts, regionTagged, overflows, textClip, blockOverlaps, bandOverlaps, cardOverlaps,
          tagCount, datelines, briefNums, cardSources, heroBottoms, footerLegend, pinCount: pins.length, pinNumbers, pinLabels, pinR, pinOverlaps, pinsOutside, headlineLines, summaryLines, briefLines,
          briefWidths, briefRows, statLines, minSvg, minDl, imagesLoaded, artSizes, stats, kicker,
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
    if nums != list(range(1, 40)):
        f.append(f"v18 needs stories 1-39 in order, got {nums}")
    kinds = [s["kind"] for s in STORIES]
    if kinds != ["hero"] * 3 + ["grid"] * 10 + ["brief"] * 26:
        f.append("v18 needs 3 leads, 10 cards and 26 briefs")
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
    if len(BEATS) < 26:
        f.append(f"only {len(BEATS)} beats (need >= 26)")
    return f


def check_audit(a: dict) -> list[str]:
    f = []
    n = len(STORIES)
    if a["doc"] != [1024, 1024]:
        f.append(f"doc {a['doc']}")
    if sorted(a["stories"]) != list(range(1, n + 1)):
        f.append(f"stories {a['stories']}")
    rc_map = {x["r"]: x["c"] for x in a["regionCounts"]}
    if sum(rc_map.values()) != n or len(rc_map) != 7 or rc_map != REGION_COUNTS:
        f.append(f"region bar counts {rc_map} != {REGION_COUNTS}")
    if any(a["regionTagged"].get(r, 0) != REGION_COUNTS[r] for r in REGION_ORDER):
        f.append(f"region tags {a['regionTagged']} != {REGION_COUNTS}")
    for k in ("overflows", "textClip", "blockOverlaps", "bandOverlaps", "cardOverlaps", "pinOverlaps", "pinsOutside"):
        if a[k]:
            f.append(f"{k}: {a[k]}")
    pinned = list(range(1, 14))
    if sorted(a["pinNumbers"]) != pinned or sorted(a["pinLabels"]) != pinned:
        f.append(f"pins {a['pinNumbers']} labels {a['pinLabels']} != 1-13")
    if any(not 8 <= r <= 9.2 for r in a["pinR"]):
        f.append(f"pin radius {a['pinR']}")
    if any(x != 2 for x in a["headlineLines"]):
        f.append(f"headline lines must all be 2: {a['headlineLines']}")
    want = [3] * 3 + [2] * 10
    if a["summaryLines"] != want:
        f.append(f"summary lines {a['summaryLines']} != {want}")
    if len(set(a["heroBottoms"])) != 1:
        f.append(f"lead summaries end on different baselines: {a['heroBottoms']}")
    if a["tagCount"] != 13:
        f.append(f"{a['tagCount']} certainty pills on cards; need 13")
    for d in a["datelines"]:
        s = STORIES[d["n"] - 1]
        if "·" not in d["text"] or d["text"] != f"{s['place']} · {s['dl']}":
            f.append(f"dateline {d['n']} is '{d['text']}', not PLACE · BEAT")
        if d["lines"] != 1:
            f.append(f"dateline {d['n']} '{d['text']}' wraps to {d['lines']} lines")
        if d["tag"] != s["tag"] or d["tag"] not in TAG_COLORS or d["tagsInKicker"] != 1 or d["tagsInBody"]:
            f.append(f"dateline {d['n']} pill mismatch: {d}")
        if d["gap"] < DATELINE_GAP:
            f.append(f"dateline {d['n']} '{d['text']}' is {d['gap']}px from {d['tag']} pill; needs {DATELINE_GAP}px")
        if d["tagRightInset"] > 0.5 or d["tagMidDy"] > 1.8:
            f.append(f"dateline {d['n']} pill alignment inset={d['tagRightInset']} midDy={d['tagMidDy']}")
    for c in a["cardSources"]:
        if c["src"] != f"({STORIES[c['n'] - 1]['src']})" or not STORIES[c["n"] - 1]["src"].strip():
            f.append(f"card {c['n']} caption missing sources: {c['src']!r}")
    def rgb(hexcol: str) -> str:
        return "rgb({}, {}, {})".format(*(int(hexcol[i:i + 2], 16) for i in (1, 3, 5)))
    if [b["n"] for b in a["briefNums"]] != [s["n"] for s in STORIES if s["kind"] == "brief"]:
        f.append(f"brief numbers {[b['n'] for b in a['briefNums']]}")
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
        f.append("brief row geometry mismatch")
    tints = [r["bg"] for r in rows]
    if len(set(tints)) != 2 or tints[0] == tints[1]:
        f.append(f"brief rows must alternate tint: {tints}")
    if any(x != 2 for x in a["statLines"]):
        f.append(f"stat explanations must be 2 lines: {a['statLines']}")
    if a["minDl"] < GRID_DL_PX:
        f.append(f"card dateline font {a['minDl']}px < {GRID_DL_PX}px")
    if a["minSvg"] < 10:
        f.append(f"svg font {a['minSvg']}")
    if not a["imagesLoaded"]:
        f.append("image failed to load")
    if any(nw != w or nh != h for nw, nh, w, h in a["artSizes"]):
        f.append(f"art scaled in page: {a['artSizes']}")
    if a["pageBottom"] > 1020:
        f.append(f"page bottom {a['pageBottom']} > 1020")
    if a["stats"] != [v for v, _ in STATS]:
        f.append(f"stats {a['stats']}")
    if not a["kicker"].startswith(f"{n} stories") or f"{len(BEATS)} beats" not in a["kicker"]:
        f.append(f"kicker {a['kicker']} beats {len(BEATS)}")
    for w in ("CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM"):
        if w not in a["footerLegend"]:
            f.append(f"footer certainty legend missing {w}")
    for w in DATECHECK_ONLY:
        if w.lower() in a["pageTextNoDC"].lower():
            f.append(f"date-check-only text outside DATE CHECK: {w}")
    dc = a["dateCheckText"]
    for w in ["DATE CHECK", "Thu 19 Nov", "Wed 18 Nov", "Sat 21 Nov",
              "BepiColombo", "COP31 Day 13", "Bukele", "Greenland", "Senate Iran",
              "embassy", "ICJ", "Putin", "Anthropic", "Voyager 1", "GTA VI", "Van Gogh", "Peru 6.7"]:
        if w not in dc:
            f.append(f"DATE CHECK missing: {w}")
    if a["dcBorder"] != "rgb(184, 41, 47)" or a["dcBg"] != "rgb(255, 253, 249)":
        f.append(f"DATE CHECK style {a['dcBorder']} {a['dcBg']}")
    return f


def encode_jpeg(im: Image.Image) -> tuple[bytes, int]:
    for q in QUALITIES:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True, progressive=True)
        sz = buf.tell()
        if 260_000 <= sz <= MAX_BYTES:
            return buf.getvalue(), q
        if q == QUALITIES[0] and MIN_BYTES <= sz < 260_000:
            return buf.getvalue(), q
        print(f"q{q}: {sz} bytes, outside target {MIN_BYTES}-{MAX_BYTES}")
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
        keys = ("pageBottom", "heroBottoms", "wireSlack", "mapSlack", "headlineLines",
                "summaryLines", "briefLines", "statLines", "cardBottoms", "minDl",
                "minSvg", "pinCount", "rects")
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
          f"min card dl {a['minDl']}px · min svg {a['minSvg']}px · pins {a['pinCount']} · "
          f"briefs one line each · omitted news only in DATE CHECK")
    print(f"entry.png: {size} bytes ({size / 1024:.1f} KiB) · progressive JPEG q{q} 4:4:4")
    return 0


if __name__ == "__main__":
    sys.exit(main())

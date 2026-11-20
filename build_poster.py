#!/usr/bin/env python3
"""Build the Friday 20 November 2026 world-news broadsheet.

Run:  python3 build_poster.py
Outputs: entry.png (1024x1024 baseline 4:4:4 JPEG, q91), assets/poster.png,
         /tmp/news_1120_v1_300.png
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
BUILD_TMP = Path("/tmp/news_1120_build")

# ---------------------------------------------------------------------------
# The edition: 13 illustrated cards (1-13) + 20 single-line dispatches (14-33).
# Every item below is dated Friday 20 November 2026, or was first reported that
# day in a time zone where the date was already 20 November.  See DATE CHECK.
# ---------------------------------------------------------------------------
CARDS = [
    dict(n=1, region="ASIA-PACIFIC", place="Gopalpur, India", beat="Disaster",
         headline="Cyclone Akvan Slams Odisha Coast",
         summary="Landfall near Gopalpur early Friday with 70–80 km/h winds; 370,000 evacuated and 69 trains cancelled.",
         source="The Hindu · IMD", art="art_01.png"),
    dict(n=2, region="EUROPE", place="Brussels", beat="Diplomacy",
         headline="EU and UK Open Reset Summit",
         summary="PM Andy Burnham meets Costa and von der Leyen as a 100,000-a-year youth-mobility pact heads for signature.",
         source="BBC · France 24", art="art_02.png"),
    dict(n=3, region="GLOBAL/SCIENCE", place="Antalya", beat="Climate",
         headline="COP31 Enters Final Day",
         summary="A slimmed draft omits fossil-fuel language as ministers clash over finance and Pacific states warn of disaster.",
         source="BBC · Guardian · RNZ", art="art_03.png"),
    dict(n=4, region="AMERICAS", place="Washington, USA", beat="Defense",
         headline="Pentagon Puts Iran War Cost at $48.3bn",
         summary="Deputy comptroller says the bill has hit $48.3bn, excluding base damage.",
         source="DW · Middle East Eye", art="art_04.png"),
    dict(n=5, region="ASIA-PACIFIC", place="Cox's Bazar", beat="Justice",
         headline="Rohingya Hail Genocide Verdict",
         summary="Refugees greet the World Court ruling with tears and prayers for return home to Myanmar.",
         source="Al Jazeera", art="art_05.png"),
    dict(n=6, region="EUROPE", place="Berlin", beat="Society",
         headline="Young Germans Protest Conscription",
         summary="Friday rallies target conscription and militarisation.",
         source="Al Jazeera", art="art_06.png"),
    dict(n=7, region="GLOBAL/SCIENCE", place="New York", beat="United Nations",
         headline="UN Council Tests Grynspan Bid",
         summary="A colour-coded Friday ballot tests P5 divisions over the next secretary-general.",
         source="The Guardian", art="art_07.png"),
    dict(n=8, region="MIDDLE EAST", place="Doha", beat="Football",
         headline="Africa's Turn at the U-17 World Cup",
         summary="Morocco, Senegal and Mali lead Friday's fixtures.",
         source="Africanews", art="art_08.png"),
    dict(n=9, region="OCEANIA", place="Melbourne", beat="Business",
         headline="NextDC Bows to Datacentre Backlash",
         summary="After a 40% share slide and a Melbourne revolt, NextDC rules out new datacentres near homes.",
         source="The Guardian", art="art_09.png"),
    dict(n=10, region="OCEANIA", place="Wellington", beat="Crime",
         headline="Comancheros Hit by First US Sanctions",
         summary="OFAC blacklists the gang and five linked figures.",
         source="RNZ · 1News", art="art_10.png"),
    dict(n=11, region="MIDDLE EAST", place="Strait of Hormuz", beat="Shipping",
         headline="Gulf Insurance Costs Surge",
         summary="US memo says Iran blockade is raising war-risk premiums.",
         source="Al Jazeera", art="art_11.png"),
    dict(n=12, region="EUROPE", place="Kyiv", beat="War",
         headline="Russian Strikes Hit Kyiv Bridges",
         summary="Overnight missiles kill three and damage key Dnipro crossings, officials say.",
         source="Reuters · France 24", art="art_12.png"),
    dict(n=13, region="ASIA-PACIFIC", place="Shenzhen", beat="Diplomacy",
         headline="Xi Hails China-Australia ‘Turnaround’",
         summary="Xi tells Albanese ties have fully turned around.",
         source="Reuters · SCMP", art="art_13.png"),
]

DISPATCHES = [
    dict(n=14, region="AFRICA", place="Africa",
         text="Ibrahim urges Africa to curb $90bn capital flight", source="Reuters"),
    dict(n=15, region="AFRICA", place="Johannesburg",
         text="Rand falls to one-year low against dollar", source="Reuters"),
    dict(n=16, region="AFRICA", place="Pretoria",
         text="Pretoria welcomes World Court genocide ruling", source="SABC"),
    dict(n=17, region="AFRICA", place="Cape Town",
         text="SALC seeks probe into SA arms exports", source="Daily Maverick"),
    dict(n=18, region="ASIA-PACIFIC", place="Seoul",
         text="Seoul confirms first cholera case in a decade", source="AP"),
    dict(n=19, region="ASIA-PACIFIC", place="Taipei",
         text="Taiwan flags 2,700 China-linked accounts to Meta", source="Reuters"),
    dict(n=20, region="ASIA-PACIFIC", place="Tokyo",
         text="Japan core inflation rises to 2.2%", source="Japan Times"),
    dict(n=21, region="ASIA-PACIFIC", place="Singapore",
         text="Singapore, China open FTA upgrade talks", source="CNA"),
    dict(n=22, region="AMERICAS", place="Ottawa",
         text="Carney's budget passes Commons 162–151", source="Global News"),
    dict(n=23, region="AMERICAS", place="Austin",
         text="Texas execution botched as staff fail to find vein", source="The Guardian"),
    dict(n=24, region="AMERICAS", place="Washington",
         text="DoJ drops Peltola Alaska Senate challenge", source="The Guardian"),
    dict(n=25, region="AMERICAS", place="Washington",
         text="CBO: AUKUS subs to shrink US fleet for years", source="The Guardian"),
    dict(n=26, region="EUROPE", place="Rome",
         text="General strike halts schools, transport, hospitals", source="Wanted in Rome"),
    dict(n=27, region="EUROPE", place="Warsaw",
         text="Polish jets scrambled over possible airspace breach", source="Euromaidan"),
    dict(n=28, region="MIDDLE EAST", place="Diwaniyah",
         text="Women protest ban on male professors", source="The Guardian"),
    dict(n=29, region="MIDDLE EAST", place="Gaza",
         text="Gaza Civil Defence: 85%+ of vehicles out of service", source="Al Jazeera"),
    dict(n=30, region="MIDDLE EAST", place="Riyadh",
         text="Saudi-led coalition intercepts Houthi missile", source="Reuters"),
    dict(n=31, region="OCEANIA", place="Sydney",
         text="David Jones issues 1,600 redundancy notices", source="ABC"),
    dict(n=32, region="OCEANIA", place="Suva",
         text="Pew urges stronger tuna transshipment oversight", source="RNZ"),
    dict(n=33, region="GLOBAL/SCIENCE", place="Mercury",
         text="BepiColombo primed for Saturday orbit", source="The Guardian"),
]

REGIONS = [
    ("ASIA-PACIFIC", 7, "#9A1B1F"),
    ("AMERICAS", 5, "#1D6F6A"),
    ("EUROPE", 5, "#1B3A6B"),
    ("MIDDLE EAST", 5, "#B06A1F"),
    ("AFRICA", 4, "#2E7D50"),
    ("OCEANIA", 4, "#5E3A7A"),
    ("GLOBAL/SCIENCE", 3, "#4A5A6A"),
]
REGION_COLORS = {name: col for name, _n, col in REGIONS}

STATS = [
    ("110 km/h", "IMD forecast gusts"),
    ("370,000", "Evacuated in Odisha"),
    ("48", "U-17 World Cup teams"),
    ("104", "Qatar 2026 matches"),
    ("2nd", "EU–UK summit"),
    ("Day 12", "COP31 final day"),
]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def card_html(c: dict) -> str:
    return f'''
    <article class="card" data-story="{c['n']}" data-region="{esc(c['region'])}">
      <img class="art" src="data:image/png;base64,{b64(ASSETS / c['art'])}" alt="">
      <div class="kicker"><span class="num" style="background:{REGION_COLORS[c['region']]}">{c['n']}</span><span class="place">{esc(c['place'])} · {esc(c['beat'])}</span></div>
      <h2><span class="hl">{esc(c['headline'])}</span></h2>
      <p class="summary"><span class="sum">{esc(c['summary'])}</span></p>
      <div class="src">{esc(c['source'])}</div>
    </article>'''


def dispatch_html(d: dict) -> str:
    return f'''
      <div class="drow" data-story="{d['n']}" data-region="{esc(d['region'])}">
        <span class="dnum" style="background:{REGION_COLORS[d['region']]}">{d['n']}</span><span class="dplace">{esc(d['place'])}</span><span class="dtext">{esc(d['text'])}</span><span class="dsrc">{esc(d['source'])}</span>
      </div>'''


def build_html() -> str:
    row1 = "".join(card_html(c) for c in CARDS[:3])
    row2 = "".join(card_html(c) for c in CARDS[3:8])
    row3 = "".join(card_html(c) for c in CARDS[8:])
    left = "".join(dispatch_html(d) for d in DISPATCHES[:10])
    right = "".join(dispatch_html(d) for d in DISPATCHES[10:])
    regions = "".join(
        f'<div class="rg" data-count="{n}" style="background:{col}">{name} <b>{n}</b></div>'
        for name, n, col in REGIONS
    )
    stats = "".join(
        f'<div class="stat"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in STATS
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
@font-face {{ font-family: 'LibSerif'; src: url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: 'LibSerif'; src: url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'); font-weight: 700; font-style: italic; }}
@font-face {{ font-family: 'LatoX'; src: url('file:///usr/share/fonts/truetype/lato/Lato-Regular.ttf'); font-weight: 400; }}
@font-face {{ font-family: 'LatoX'; src: url('file:///usr/share/fonts/truetype/lato/Lato-Bold.ttf'); font-weight: 700; }}
@font-face {{ font-family: 'LatoX'; src: url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf'); font-weight: 900; }}
@font-face {{ font-family: 'LatoX'; src: url('file:///usr/share/fonts/truetype/lato/Lato-Italic.ttf'); font-weight: 400; font-style: italic; }}
@font-face {{ font-family: 'LatoX'; src: url('file:///usr/share/fonts/truetype/lato/Lato-BoldItalic.ttf'); font-weight: 700; font-style: italic; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; width:1024px; height:1024px; overflow:hidden; background:#F6F1E6; }}
body {{ font-family:'LatoX', sans-serif; color:#141923; -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-variant-ligatures:none; }}
.page {{ width:1024px; height:1024px; padding:10px 20px 0 20px; position:relative; }}
.kickerbar {{ display:flex; justify-content:space-between; align-items:flex-end; font:900 8.5px/1 'LatoX'; letter-spacing:.13em; text-transform:uppercase; border-bottom:1.4px solid #141923; padding-bottom:3px; }}
.kickerbar .r {{ font-weight:700; letter-spacing:.08em; }}
.masthead {{ font:700 55px/1.08 'LibSerif'; letter-spacing:-.022em; margin:4px 0 0 0; white-space:nowrap; }}
.deck {{ font:italic 700 13.1px/1.18 'LibSerif'; color:#9A1B1F; margin-top:2px; white-space:nowrap; }}
.regionbar {{ display:flex; align-items:center; gap:3px; height:22px; margin-top:6px; padding:2px 0; border-top:1.2px solid #141923; border-bottom:1.2px solid #141923; }}
.rg {{ flex:1; height:16px; display:flex; align-items:center; justify-content:center; gap:3px; font:900 8.9px/1 'LatoX'; letter-spacing:.045em; text-transform:uppercase; white-space:nowrap; color:#FFFDF7; border-radius:3px; }}
.rg b {{ font:900 10px/1 'LatoX'; color:#FFFDF7; margin-left:1px; }}
.stats {{ display:flex; height:46px; margin-top:6px; background:#EFE8D8; border:1.25px solid #141923; }}
.stat {{ flex:1; border-right:1px solid #C9BFA9; padding:3px 7px 2px 7px; display:flex; flex-direction:column; justify-content:center; }}
.stat:last-child {{ border-right:none; }}
.stat b {{ font:700 20px/1 'LibSerif'; color:#9A1B1F; letter-spacing:-.012em; }}
.stat span {{ font:700 6.5px/1.12 'LatoX'; letter-spacing:.065em; text-transform:uppercase; color:#20252E; margin-top:2px; }}
.cards {{ margin-top:7px; }}
.row {{ display:flex; gap:8px; }}
.row1 {{ height:210px; }}
.row2, .row3 {{ height:178px; margin-top:7px; }}
.card {{ background:#FFFDF7; border:1.25px solid #141923; padding:6px; display:flex; flex-direction:column; overflow:hidden; position:relative; }}
.row1 .card {{ flex:1; }}
.row2 .card, .row3 .card {{ flex:1; }}
.art {{ width:100%; display:block; outline:1px solid #141923; outline-offset:-1px; object-fit:fill; }}
.row1 .art {{ height:106px; }}
.row2 .art, .row3 .art {{ height:82px; }}
.kicker {{ display:flex; align-items:center; gap:5px; margin-top:4px; height:12px; }}
.num {{ width:12px; height:12px; flex:0 0 12px; border-radius:50%; background:#9A1B1F; color:#FFFDF7; font:900 7.4px/12px 'LatoX'; text-align:center; }}
.place {{ font:700 8.0px/1 'LatoX'; letter-spacing:.065em; text-transform:uppercase; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.row2 .place, .row3 .place {{ font-size:7.4px; letter-spacing:.03em; }}
h2 {{ margin:4px 0 0 0; font:700 19.5px/0.98 'LibSerif'; letter-spacing:-.014em; }}
.row2 h2, .row3 h2 {{ font-size:15px; margin-top:3px; }}
.summary {{ margin:3px 0 0 0; font:400 9.7px/1.20 'LatoX'; color:#262B33; }}
.row2 .summary, .row3 .summary {{ font-size:8.45px; line-height:1.17; margin-top:2px; }}
.src {{ margin-top:auto; padding-top:2px; font:italic 700 6.7px/1 'LatoX'; letter-spacing:.035em; text-transform:uppercase; color:#6D5B4A; white-space:nowrap; overflow:hidden; }}
.row2 .src, .row3 .src {{ font-size:5.9px; }}
.bottom {{ display:flex; gap:12px; height:190px; margin-top:7px; }}
.mapcol {{ width:300px; flex:0 0 300px; }}
.maptitle, .disptitle {{ display:flex; justify-content:space-between; align-items:flex-end; font:900 9.1px/1 'LatoX'; letter-spacing:.11em; text-transform:uppercase; border-bottom:1.3px solid #141923; padding-bottom:3px; }}
.maptitle span, .disptitle span {{ font:700 7.2px/1 'LatoX'; letter-spacing:.06em; color:#9A1B1F; }}
.mapimg {{ width:300px; height:160px; display:block; margin-top:3px; outline:1px solid #141923; outline-offset:-1px; }}
.maptally {{ font:700 6.3px/1.25 'LatoX'; letter-spacing:.03em; text-transform:uppercase; color:#3A3F47; margin-top:3px; }}
.maptally b {{ color:#9A1B1F; }}
.dispatchcol {{ flex:1; min-width:0; }}
.dispatchgrid {{ display:flex; gap:10px; margin-top:3px; }}
.dcol {{ flex:1; min-width:0; }}
.drow {{ height:17px; display:flex; align-items:baseline; gap:5px; white-space:nowrap; }}
.dnum {{ width:11px; height:11px; flex:0 0 11px; border-radius:50%; background:#9A1B1F; color:#FFFDF7; font:900 6.1px/11px 'LatoX'; text-align:center; align-self:center; }}
.dplace {{ font:700 8.5px/1 'LatoX'; letter-spacing:.01em; }}
.dtext {{ font:400 9.8px/1 'LatoX'; }}
.dsrc {{ font:italic 700 7.1px/1 'LatoX'; color:#6D5B4A; margin-left:auto; padding-left:4px; }}
.datecheck {{ margin-top:6px; height:37px; border:2px solid #9A1B1F; background:#EFE8D8; padding:4px 8px 3px 8px; overflow:hidden; }}
.dc-line {{ font:700 8.35px/1.28 'LatoX'; white-space:nowrap; }}
.dc-line.two {{ font-weight:400; font-size:7.9px; }}
.dc-line b {{ color:#9A1B1F; letter-spacing:.06em; }}
.footer {{ margin-top:3px; font:400 6.55px/1 'LatoX'; color:#3A3F47; letter-spacing:.015em; white-space:nowrap; }}
</style></head>
<body><div class="page">
  <div class="kickerbar"><div>THE WORLD CANVAS · ONE-PAGE EDITION</div><div class="r">33 STORIES · 7 REGIONS · ALL VERIFIED FRI 20 NOV 2026</div></div>
  <div class="masthead">Friday, 20 November 2026</div>
  <div class="deck">Cyclone Akvan strikes India's east coast · UK and EU head into reset summit in Brussels · COP31 enters final-day finance clash</div>
  <div class="regionbar">{regions}</div>
  <div class="stats">{stats}</div>
  <div class="cards">
    <div class="row row1">{row1}</div>
    <div class="row row2">{row2}</div>
    <div class="row row3">{row3}</div>
  </div>
  <div class="bottom">
    <div class="mapcol">
      <div class="maptitle"><div>WHERE IT HAPPENED</div><span>1–13</span></div>
      <img class="mapimg" src="data:image/png;base64,{b64(ASSETS / 'map.png')}" alt="">
      <div class="maptally">ALL STORIES <b>33</b> · APAC 7 · AMER 5 · EUR 5 · ME 5 · AFR 4 · OCE 4 · GLOBAL 3</div>
    </div>
    <div class="dispatchcol">
      <div class="disptitle"><div>ALSO ON FRIDAY 20 NOVEMBER 2026</div><span>14–33</span></div>
      <div class="dispatchgrid"><div class="dcol">{left}</div><div class="dcol">{right}</div></div>
    </div>
  </div>
  <div class="datecheck">
    <div class="dc-line"><b>DATE CHECK ✓</b> Every story on this page happened, or was first reported, on Friday, 20 November 2026 (UTC).</div>
    <div class="dc-line two">Excluded as Thu 19 Nov: Trump–Xi–Putin summit · Anthropic $81bn IPO · ICJ Myanmar verdict · GTA VI · Riyadh PIF strike · US cyber-chief firing · U-17 opener · Nvidia subpoena.</div>
  </div>
  <div class="footer">Disputed claims attributed, not stated as fact · Original illustrations; map drawn in code from Natural Earth 110m · Sources: BBC · Guardian · Al Jazeera · Reuters · RNZ · ABC · The Hindu · Africanews · SABC · CNA · Japan Times · DW · France 24 · 1News · Global News · Daily Maverick · Middle East Eye · AP · IMD</div>
</div></body></html>'''


AUDIT_JS = r'''() => {
  const R = el => { const r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}; };
  const cards = [...document.querySelectorAll('.card')];
  const rows = [...document.querySelectorAll('.drow')];
  const stories = [...cards, ...rows];
  const unique = new Set(stories.map(e => e.dataset.story)).size;
  const badges = document.querySelectorAll('.card .num').length;
  const regionCounts = [...document.querySelectorAll('.rg')].map(e => +e.dataset.count);
  const regionSum = regionCounts.reduce((a,b)=>a+b,0);
  const doc = [document.documentElement.scrollWidth, document.documentElement.scrollHeight];

  const overflows = [];
  document.querySelectorAll('.card,.art,.drow,.dispatchcol,.mapcol,.datecheck,.footer,.regionbar,.stats,.masthead,.deck,.kickerbar,.rg,.stat,.maptitle,.disptitle').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)
      overflows.push({sel:el.className, sw:el.scrollWidth, cw:el.clientWidth, sh:el.scrollHeight, ch:el.clientHeight});
  });

  const clipped = [];
  document.querySelectorAll('.hl,.sum,.src,.place,.dtext,.dplace,.dsrc,.dc-line,.footer,.maptally').forEach(el => {
    const box = R(el); const p = el.closest('.card,.drow,.datecheck,.page');
    if (!p) return; const pb = R(p);
    if (box.x < pb.x - 0.6 || box.right > pb.right + 0.6 || box.y < pb.y - 0.6 || box.bottom > pb.bottom + 0.6)
      clipped.push({text:el.textContent.slice(0,50), box, parent:pb});
  });

  const headlineLines = cards.map(c => c.querySelector('.hl').getClientRects().length);
  const summaryLines = cards.map(c => c.querySelector('.sum').getClientRects().length);
  const dispatchLines = rows.map(d => d.querySelector('.dtext').getClientRects().length);
  const dispatchSlack = rows.map(d => {
    const kids = [...d.children];
    const used = kids.reduce((a,k)=>a+R(k).w,0) + Math.max(0,kids.length-1)*5;
    return +(d.clientWidth - used).toFixed(2);
  });
  const dateLines = document.querySelectorAll('.dc-line').length;
  const dc = document.querySelector('.datecheck');
  const dateOverflow = dc.scrollHeight > dc.clientHeight + 1 || dc.scrollWidth > dc.clientWidth + 1;

  const badgeEdgeClips = cards.map(c => {
    const cr = R(c), br = R(c.querySelector('.num'));
    return +Math.min(br.x-cr.x, br.y-cr.y, cr.right-br.right, cr.bottom-br.bottom).toFixed(2);
  }).filter(v => v < 2);

  // block overlap audit inside each card and across the page's major bands
  const pairs = [];
  cards.forEach(c => {
    const els = ['.art','.kicker','h2','.summary','.src'].map(s => c.querySelector(s));
    for (let i=0;i<els.length-1;i++) {
      const a=R(els[i]), b=R(els[i+1]);
      if (a.bottom > b.top + 0.6) pairs.push({card:c.dataset.story, a:els[i].className||els[i].tagName, b:els[i+1].className||els[i+1].tagName, gap:+(a.bottom-b.top).toFixed(2)});
    }
  });
  const major = ['.kickerbar','.masthead','.deck','.regionbar','.stats','.cards','.bottom','.datecheck','.footer'].map(s=>document.querySelector(s));
  const majorOverlaps = [];
  for (let i=0;i<major.length-1;i++) {
    const a=R(major[i]), b=R(major[i+1]);
    if (a.bottom > b.top + 0.6) majorOverlaps.push({a:major[i].className, b:major[i+1].className, gap:+(a.bottom-b.top).toFixed(2)});
  }
  const cardOverlaps = [];
  cards.forEach((c,i)=>cards.forEach((d,j)=>{ if (j<=i) return; const a=R(c), b=R(d);
    if (a.x < b.right-0.6 && b.x < a.right-0.6 && a.y < b.bottom-0.6 && b.y < a.bottom-0.6)
      cardOverlaps.push({a:c.dataset.story,b:d.dataset.story}); }));

  const artBoxes = document.querySelectorAll('.art').length;
  const mapBoxes = document.querySelectorAll('.mapimg').length;
  const imagesLoaded = [...document.images].every(img => img.complete && img.naturalWidth > 0);
  const artSizes = [...document.querySelectorAll('.art')].map(img => [img.naturalWidth, img.naturalHeight]);
  return {doc, stories:stories.length, unique, badges, regionCounts, regionSum,
    overflows, clipped, headlineLines, summaryLines, dispatchLines, dispatchSlack,
    dateLines, dateOverflow, badgeEdgeClips, blockOverlaps:pairs, majorOverlaps, cardOverlaps,
    artBoxes, mapBoxes, imagesLoaded, artSizes,
    masthead:R(document.querySelector('.masthead')), deck:R(document.querySelector('.deck')),
    bottom:R(document.querySelector('.bottom')), datecheck:R(dc), footer:R(document.querySelector('.footer'))};
}'''


def run_audit(page) -> dict:
    return page.evaluate(AUDIT_JS)


def check_audit(a: dict):
    failures = []
    if a["doc"] != [1024, 1024]:
        failures.append(f"doc {a['doc']} != [1024,1024]")
    if a["stories"] != 33:
        failures.append(f"stories {a['stories']} != 33")
    if a["unique"] != 33:
        failures.append(f"unique {a['unique']} != 33")
    if a["badges"] != 13:
        failures.append(f"badges {a['badges']} != 13")
    if a["regionSum"] != 33:
        failures.append(f"region_sum {a['regionSum']} != 33")
    if any(n < 3 for n in a["regionCounts"]):
        failures.append(f"region counts below 3: {a['regionCounts']}")
    for k in ("overflows", "clipped", "badgeEdgeClips", "blockOverlaps", "majorOverlaps", "cardOverlaps"):
        if a[k]:
            failures.append(f"{k}: {a[k]}")
    if max(a["headlineLines"]) > 2:
        failures.append(f"headline lines: {a['headlineLines']}")
    if max(a["summaryLines"]) > 2:
        failures.append(f"summary lines: {a['summaryLines']}")
    if any(v != 1 for v in a["dispatchLines"]):
        failures.append(f"dispatch lines: {a['dispatchLines']}")
    if min(a["dispatchSlack"]) < 16:
        failures.append(f"dispatch slack: {a['dispatchSlack']}")
    if a["dateLines"] != 2 or a["dateOverflow"]:
        failures.append(f"date check: lines={a['dateLines']} overflow={a['dateOverflow']}")
    if a["artBoxes"] != 13 or a["mapBoxes"] != 1:
        failures.append(f"art/map boxes: {a['artBoxes']} + {a['mapBoxes']} != 14")
    if not a["imagesLoaded"]:
        failures.append("an image failed to load")
    return failures


def main() -> int:
    art.build_all()
    mapgen.check_pins()
    BUILD_TMP.mkdir(parents=True, exist_ok=True)
    (BUILD_TMP / "map.svg").write_text(mapgen.svg_document())
    for i, c in enumerate(CARDS):
        im = Image.open(ASSETS / c["art"])
        want = (309, 106) if i < 3 else (176, 82)
        if im.size != want:
            raise SystemExit(f"{c['art']} is {im.size}, expected {want}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            args=["--font-render-hinting=none", "--disable-lcd-text", "--disable-gpu",
                  "--force-device-scale-factor=1", "--hide-scrollbars"],
        )
        page = browser.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=1)
        # map first, at 2x, then Lanczos down to its printed size
        page.set_viewport_size({"width": 600, "height": 320})
        page.goto((BUILD_TMP / "map.svg").as_uri())
        page.wait_for_timeout(220)
        page.screenshot(path=str(BUILD_TMP / "map2x.png"))
        Image.open(BUILD_TMP / "map2x.png").convert("RGB").resize((300, 160), Image.LANCZOS).save(ASSETS / "map.png")

        html_path = BUILD_TMP / "poster.html"
        html_path.write_text(build_html(), encoding="utf-8")
        page.set_viewport_size({"width": 1024, "height": 1024})
        page.goto(html_path.as_uri())
        page.wait_for_timeout(350)
        page.evaluate("document.fonts.ready")
        a = run_audit(page)
        print(json.dumps(a, indent=1)[:6000])
        failures = check_audit(a)
        if failures:
            print("\nAUDIT FAILURES:")
            for f in failures:
                print(" -", f)
            browser.close()
            return 1
        page.screenshot(path=str(ASSETS / "poster.png"))
        browser.close()

    im = Image.open(ASSETS / "poster.png").convert("RGB")
    im.save(BASE / "entry.png", format="JPEG", quality=91, subsampling=0,
            optimize=True, progressive=False)
    im.resize((300, 300), Image.LANCZOS).save("/tmp/news_1120_v1b_300.png")
    size = (BASE / "entry.png").stat().st_size
    print(f"\nentry.png: {size} bytes ({size/1024:.1f} KiB)")
    if not (320 * 1024 <= size <= 450 * 1024):
        print("WARNING: entry.png outside 320-450 KiB target")
    return 0


if __name__ == "__main__":
    sys.exit(main())

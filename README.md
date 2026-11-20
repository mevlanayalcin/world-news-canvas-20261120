# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 38 stories from Friday,
20 November 2026 (UTC), across seven regions and 25 beats. Version 5 drops
v4's BepiColombo card (its Mercury orbit capture is due on Saturday), brings
back the crimson-bordered DATE CHECK bar, and redraws the page as an open
broadsheet: hairline rules on cream paper instead of a box around every card,
and a large title banner on every illustration so all 13 read at 300 px.

## The edition

- **Masthead:** the date in 67 px serif, a one-line crimson deck, and six
  figures taken from stories on the page: 3 Kyiv bridges hit · 372,000
  evacuated in Odisha · −6.23% Taiex close · 100,000 UK–EU youth places a
  year · 2.3% Japan October CPI · 118 Phillips runs vs India. Below them, a
  slim seven-colour region bar whose counts sum to 38.
- **Three leads (1–3):** Russian missiles hit three Kyiv bridges · Cyclone
  Akvan makes landfall in Odisha · Asia's chip and AI stocks sink in their
  worst week since 2020.
- **Ten illustrated cards (4–13):** the UK–EU reset · COP31's final day ·
  a Russian cruise missile in Poland · the Iraqi army in Jurf al-Sakher ·
  Italy's general strike · Japan's 2.3% inflation · Seoul's move to impeach
  the chief justice · Kenya's first oil well · Bukele's third-term filing ·
  Glenn Phillips' 118 against India.
- **The wire (14–38):** 25 two-line briefs in three columns (9 · 8 · 8). Each
  has a bold place, a bold headline phrase, a short detail, an italic source
  and a certainty mark (filled dot = confirmed on the record, half dot =
  reported or claimed).
- **Map and timeline:** a dark-ocean Natural Earth 110m map with 38 numbered
  pins, one per story, plus a Friday timeline in UTC.
- **DATE CHECK ✓ bar:** two lines stating that every story happened or was
  first reported on Friday 20 November 2026 (UTC), and naming what was left
  out: Thursday 19 November news (ICJ Myanmar genocide ruling, Trump–Xi–Putin
  Shenzhen declaration, Pentagon $48.3bn Iran tally, Canada budget vote, DOJ
  Alaska suit) and events that have not happened yet (BepiColombo's Saturday
  Mercury orbit capture, the final COP31 text).

Region tally: **Europe 8 · Asia-Pacific 9 · Americas 5 · Middle East 4 ·
Africa 6 · Oceania 3 · Global/Science 3 = 38**. Counts are computed from
`STORIES`.

## Illustrations

`art.py` draws all 13 pictures from scratch. Each scene is drawn at 2× and
reduced with Lanczos. The type is then drawn at printed size, so FreeType
renders it at its final pixel size:

- **Leads (316×144):** a full-width 24 px title banner (`KYIV · 3 BRIDGES
  HIT`, `CYCLONE AKVAN LANDS`, `TAIEX −6.23% · AI ROUT`), a 14 px dark
  sub-label, and an attribution strip at the bottom left (`Officials' count`,
  `IMD · State`, `Market close`).
- **Cards (188×86):** a 16 px uppercase white banner on a solid bar in the
  region colour (`UK–EU DEAL`, `COP31: NO DEAL`, `POLAND: MISSILE`, `IRAQ:
  ARMY IN`, `ITALY: STRIKE`, `JAPAN: +2.3%`, `SEOUL: IMPEACH`, `KENYA: OIL`,
  `BUKELE: 3RD BID`, `PHILLIPS: 118`), plus a dark attribution pill at the
  bottom right.

The art build fails if any banner is under 22 px (leads) or 15 px (cards),
if a label sits within 3 px of an edge, or if two labels overlap.

## Build

The image is generated offline with Python, Pillow and Playwright, then
committed as `entry.png`, so the submitted program needs only Node's standard
library.

```bash
python3 build_poster.py          # rebuilds art, entry.png and /tmp/news_1120_v5_300.png
MAKEFUN_OUTPUT_DIR=out node --experimental-strip-types main.ts
```

`build_poster.py` first checks the story list: no story may mention
BepiColombo, Mercury, Saturday, Thursday or any of the omitted Thursday items.
It then renders the page in `/usr/bin/google-chrome` and runs a DOM audit
before saving:

- a 1024×1024 document with stories 1–38 all present;
- region counts that sum to 38, with at least 3 per region and at least 25
  beats;
- no overflow, clipping or overlap of cards, bands, text or the DATE CHECK
  bar;
- 38 pins, one per story, all inside the map, none overlapping;
- headlines and briefs at most two lines, card summaries one line;
- HTML text at least 10 px and SVG text at least 9 px;
- every stat backed by its story's text;
- omitted-news text present in the crimson DATE CHECK bar and nowhere else
  on the page.

It then writes a baseline 4:4:4 JPEG at the highest quality from q93 to q91
that fits 650 KiB, and requires 440–650 KiB (currently q93, 635,198 bytes; the
gate allows 1,048,576).

Two consecutive builds produce byte-identical `entry.png`, and `main.ts` copies
the same bytes without network access.

## Sources

Reuters · AP · AFP · Al Jazeera · Anadolu Agency · The Guardian · CBS · DW ·
ABC (Australia) · IMD · The Hindu · Kyiv Independent · La Repubblica · UN ·
EU · Quai d'Orsay · MIC · Japan Times · Korea Herald · KDCA · PBOC · FMPRC ·
SGX · The Star (Kenya) · NWS · Formula 1 · ATP · ICC · RNZ · Security Council
Report · WCS · UKMTO · IOM · AfDB · Africanews.

## License

MIT — see [LICENSE](LICENSE).

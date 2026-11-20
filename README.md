# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 40 stories from Friday,
20 November 2026 (UTC), across seven regions and 25 beats. Version 3 nearly
doubles v2's 21 stories and stays readable when shown about 300 pixels wide.

## The edition

- **Masthead:** the date, a one-line deck, a seven-colour region bar and six
  figures taken from stories on the page: 3 Kyiv bridges hit · 372,000
  evacuated in Odisha · Taiex −6.23% · 100,000 UK–EU youth places a year ·
  the UN's 9th straw poll · 1,689 David Jones redundancy notices.
- **Three leads (1–3):** Russian missiles hit three Kyiv bridges · Cyclone
  Akvan makes landfall in Odisha · Asia's chip stocks crash in the AI sell-off.
- **Ten illustrated cards (4–13):** UK–EU deals · COP31's final day · Italy's
  general strike · Trump's White House news conference · the UN's ninth straw
  poll · Saudi interceptions · Florida's Space Coast floods · Xi and Albanese ·
  the Dakar migration roadmap · BepiColombo nearing Mercury orbit.
- **The wire (14–40):** 27 two-line briefs in three columns, each with a bold
  place name, a source and a certainty mark (filled dot = confirmed or on the
  record, half dot = reported or claimed).
- **Map and timeline:** a Natural Earth 110m map with 39 numbered pins (13,
  BepiColombo, is in space), plus a Friday timeline in UTC.

Region tally: **Europe 6 · Asia-Pacific 7 · Americas 7 · Middle East 4 ·
Africa 6 · Oceania 6 · Global/Science 4 = 40**.

## Date discipline

Every story happened, or was first reported, on Friday 20 November 2026 (UTC);
each one was checked against publication timestamps. The `DATE CHECK` bar
names the stories left out because they broke on Thursday 19 November: the
Trump–Xi–Putin declaration, the ICJ Myanmar genocide ruling, the Pentagon's
$48.3bn Iran tally, Canada's budget vote, the DOJ Alaska suit and the IEA's
$40bn pipeline report. It also names candidates dropped as earlier news:
Brazil's $1bn FX sale (19 Nov), Peres Jepchirchir's ban (19 Nov), Italy's
€805m Meta fine (14 Nov), Colombia's hippo cull (18 Nov) and Pope Leo's Peru
farewell (16 Nov). Official or disputed figures carry their source.

## Build

The image is generated offline with Python, Pillow and Playwright, then
committed as `entry.png`, so the submitted program needs only Node's standard
library.

```bash
python3 build_poster.py          # rebuilds art, entry.png and /tmp/news_1120_v3_300.png
MAKEFUN_OUTPUT_DIR=out node --experimental-strip-types main.ts
```

- `art.py` draws the 13 illustrations at 2× and reduces them with Lanczos
  (lead art 310×120, card art 180×72).
- `mapgen.py` projects the land (Miller) and spreads overlapping pins apart
  with leader lines, as an inline SVG.
- `build_poster.py` renders the page in `/usr/bin/google-chrome` and runs a DOM
  audit before saving: a 1024×1024 document; stories 1–40 all present; region
  counts summing to 40 with at least 4 per region; at least 14 beats; no
  overflow, clipping or overlap; every pinned story on the map exactly once,
  with no overlapping pins; headlines and briefs at most two lines; grid
  summaries one line; every stat matched to a story; HTML text at least 9.5px
  and SVG text at least 9px. It then writes the highest-quality baseline 4:4:4
  JPEG that fits 420 kB (currently q82, 412,902 bytes).

Two consecutive builds produce byte-identical `entry.png`, and `main.ts` copies
the same bytes without network access.

## Sources

Reuters · AP · AFP · Al Jazeera · BBC · The Guardian · CBS · DW · ABC
(Australia) · IMD · The Hindu · NDTV · Kyiv Independent · La Repubblica ·
Security Council Report · Gov.uk · Times of Israel · Xinhua · KDCA · MIC ·
SGX · IOM · ThisDay · AfDB · Africanews · Fana · People Daily · Rio Times ·
Global News · ABF · AFP (Australia) · RNZ · WCS · ESA · JAXA.

## License

MIT — see [LICENSE](LICENSE).

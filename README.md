# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 21 stories from Friday,
20 November 2026, across seven regions. Version 2 is laid out to stay readable
when the image is shown about 300 pixels wide.

## The edition

- **Masthead:** `Friday, 20 November 2026`, a deck naming the day's leads, and a
  seven-colour region strip with counts.
- **Six figures:** 3 Kyiv bridges hit · 372,000 evacuated in Odisha · 100,000
  UK–EU youth visas a year · 0 fossil-fuel mentions in the COP31 draft · a
  24-hour Italian general strike · 1,689 David Jones job cuts.
- **Three lead cards:** Russian missiles hit three Kyiv bridges · Cyclone Akvan
  makes landfall in Odisha · Burnham's UK–EU reset summit in Brussels.
- **Ten illustrated cards:** COP31's final day · Saudi interceptions of a Houthi
  missile and drones · Italy's general strike · Xi and Albanese in Shenzhen ·
  Florida's Space Coast floods · the UN Security Council's ninth straw poll ·
  a US memo on Gulf war-risk insurance · the rand's one-year low · South
  Korea's first cholera case in 10 years · Morocco, Senegal and Mali at the
  U-17 World Cup.
- **Also on Friday (14–21):** eight two-line briefs (Tokyo, Taipei, Berlin,
  Abidjan, Melbourne, Sydney, BepiColombo, Washington).
- **Map:** Natural Earth 110m land drawn in code, with 20 numbered pins in
  region colours (BepiColombo is in space and has no pin).

Region tally: **Asia-Pacific 4 · Europe 4 · Americas 2 · Middle East 2 ·
Africa 3 · Oceania 3 · Global/Science 3 = 21**.

## Date discipline

Every story happened, or was first reported, on Friday 20 November 2026 (UTC);
each was checked against publication timestamps. The `DATE CHECK` bar names the
Thursday 19 November stories left out: the Trump–Xi–Putin declaration, the ICJ
Myanmar genocide ruling, the Pentagon's $48.3bn Iran-war tally, Canada's budget
vote and the DOJ's Alaska Senate filing. The OFAC Comanchero sanctions were also
dropped because Treasury announced them on Thursday (US time).

Official or disputed figures carry their source (officials, the coalition, the
EU, files seen by Al Jazeera), and each card names the outlets it draws on.

## Build

The image is generated offline with Python, Pillow and Playwright, then
committed as `entry.png`, so the submitted program needs only Node's standard
library.

```bash
python3 build_poster.py          # rebuilds art, entry.png and /tmp/news_1120_v2_300.png
MAKEFUN_OUTPUT_DIR=out node --experimental-strip-types main.ts
```

- `art.py` draws the 13 illustrations at 2× and reduces them with Lanczos
  (lead art 310×142, card art 180×88).
- `mapgen.py` projects the land (Miller) and spreads overlapping pins apart
  with leader lines, as an inline SVG.
- `build_poster.py` renders the page in `/usr/bin/google-chrome` and runs a DOM
  audit: 1024×1024 document, 21 stories, region counts summing to 21, no
  overflow, clipping or overlap, no overlapping map pins, headlines, summaries
  and briefs at most two lines, HTML text at least 10px, SVG text at least 9px.
  It then writes a baseline 4:4:4 JPEG at quality 90.

Two consecutive builds produce byte-identical `entry.png`, and `main.ts` copies
the same bytes without network access.

## Sources

AP · Reuters · AFP · BBC · The Guardian · Al Jazeera · DW · ABC (Australia) ·
IMD · ETV Bharat · La Repubblica · Security Council Report · NWS · CNN ·
Chosun Ilbo · Africanews · Kyodo · RNZ · ThisDay · The Local.

## License

MIT — see [LICENSE](LICENSE).

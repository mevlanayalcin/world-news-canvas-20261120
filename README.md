# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page editorial broadsheet for **news-image-20261120**: **39 verified pure-Friday stories** from Friday, 20 November 2026 (UTC), spanning all **7 regions** and **27 beats**.

**Changes in v17:**

- **Unclogged top third:** Removed the redundant deck and stacked top region bar. Upgraded `THE DAY IN UTC` to an airy 30 px two-line, 7-column strip (`OVERNIGHT`, `~02:30Z`, `05:30Z`, `MIDDAY`, `15:50Z`, `~19:10Z`, `21:00Z`) paired with a compact 34 px `THE DAY IN NUMBERS` strip (`3`, `372,000`, `−3.7%`, `−14%`, `60.7%`, `100,000`).
- **Borderless Economist-style infographics (`art.py`):** Eliminated all 13 repetitive crimson corner stickers and noisy gradients. Leads 1–3 (`316×138`) carry single-punchline editorial infographics; cards 4–13 (`188×80`) pair one crisp flat-vector icon with one bold 300 px-readable callout (`−14% SEC PROBE`, `NO DEAL`, `KH-101`, `60.7%`, `1,070`, `118 & 175*`), cutting `entry.png` to ~340 KiB progressive 4:4:4 JPEG.
- **39 stories across 7 regions & 27 beats:** Expanded to 3 leads, 10 feature cards, and 26 single-line wire briefs (13 per column) with Sentence Case headlines, 9.5 px card datelines, outlined certainty pills, and factual precision fixes across Kyiv, Nvidia, Barcelona/EORTC, Argentina, and `DATE CHECK` (moving Voyager 1 cleanly to Wed 18 Nov).
- **Light-ocean world map & explicit certainty legend:** Switched `mapgen.py` to airy `#E6EFF5` light-blue ocean cartography with `#D8CBB5` land, geographically exact land-verified pins (NYC, Santa Clara, Barcelona), a 2-row 7-region legend under the map, and an explicit footer certainty legend (`[CONFIRMED] 2+ outlets · [OFFICIAL] on the record · [REPORTED] one outlet`).

## The edition

- **Masthead:** Kicker (`THE WORLD IN ONE DAY` · `39 STORIES · 7 REGIONS · 27 BEATS · EVERY STORY DATED FRIDAY 20 NOVEMBER 2026`), large serif date, `THE DAY IN UTC` (7 columns), and `THE DAY IN NUMBERS` (6 figures backed by story text).
- **Three leads (1–3):** `KYIV, UKRAINE · WAR` (OFFICIAL) · `ODISHA, INDIA · CYCLONE` (OFFICIAL) · `GLOBAL MARKETS · AI ROUT` (CONFIRMED).
- **Ten feature cards (4–13):** `US · TECH` Nvidia SEC probe (REPORTED) · `BRUSSELS · EU–UK` post-Brexit reset (OFFICIAL) · `ANTALYA · CLIMATE` COP31 overtime (CONFIRMED) · `POLAND · SECURITY` Kh-101 missile (OFFICIAL) · `HORMUZ · SHIPPING` tanker ablaze (OFFICIAL) · `INDIA · TALKS` Pakistani minister at SCO (CONFIRMED) · `KENYA · ENERGY` Turkana first well (OFFICIAL) · `BARCELONA · HEALTH` daraxonrasib 60.7% response (REPORTED) · `ARGENTINA · BONDS` country risk 1,070 (CONFIRMED) · `NZ · CRICKET` Phillips 118 & Nicholls 175* (CONFIRMED).
- **Where it happened (`mapgen.py`):** Natural Earth 110m Miller projection (`294×150` inline SVG) with 13 on-land location dots, non-crossing haloed leaders, and a 2-row 7-region legend (`Europe 7 · Asia-Pacific 9 · Americas 6 · Middle East 5 · Africa 6 · Oceania 2 · Global 4 · Total 39`).
- **Also on Friday 20 November (14–39):** 26 one-line briefs in two columns of 13 (`10.6 px` Lato, `14 px` row pitch, alternating tint, `14 px` region-coloured numbered discs).
- **DATE CHECK & footer:** Explicit 3-line exclusions for Thu 19 Nov, Wed 18 Nov (Voyager 1, Van Gogh), and Sat 21 Nov+ future events, plus the 3-pill certainty-tag legend in the footer.

## Build & verification

The broadsheet is rendered offline with Python, Pillow, and Playwright into `entry.png` (`1024×1024` progressive `4:4:4` JPEG), so `main.ts` ships deterministic bytes with zero runtime network or external dependencies.

```bash
python3 build_poster.py
MAKEFUN_OUTPUT_DIR=/tmp/n20-out node main.ts
```

## License

MIT — see [LICENSE](LICENSE).

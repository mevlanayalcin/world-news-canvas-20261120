# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page editorial broadsheet atlas for **news-image-20261120**: **39 verified pure-Friday stories** from Friday, 20 November 2026 (UTC), spanning all **7 regions** and **27 beats**.

**Changes in v18:**

- **Masthead + 6-KPI Strip + Proportional 7-Region Bar:** Warm archival paper (`#FAF7F0`), large serif **`Friday 20 November 2026`** masthead with italic lead deck, **6 big-number serif KPI tiles** (`3`, `372,000`, `−3.7%`, `−14%`, `60.7%`, `100,000`) with crimson accent bars, and a proportional **7-region color bar** (`Europe 7 · Asia-Pacific 9 · Americas 6 · Middle East 5 · Africa 6 · Oceania 2 · Global 4`).
- **Region-Coded Editorial Banners + Vector Infographics (`art.py`):** All 13 illustrated cards (3 wide leads `316×130` + 10 secondary cards `188×76`) pair an integrated region-colored topic banner legible at 300 px thumbnail scale with clean flat-vector infographics and bold numeric callouts (`−14%`, `NO DEAL`, `KH-101`, `60.7%`, `1,070`, `118 & 175*`).
- **Enlarged Light-Ocean Map (`336×174`) + 26 Wire Briefs:** Expanded `mapgen.py` to 34% width with airy `#E6EFF5` ocean, `#D8CBB5` land, and 13 land-verified `8.8 px` pins (`NYC`, `Santa Clara`, `Barcelona`, `Kyiv`, `Poland`, `Antalya`, `Hormuz`, `Odisha`, `New Delhi`, `Kenya`, `Buenos Aires`, `Wellington`), paired with 26 crisp single-line briefs (`14–39`) in two columns of 13.
- **Explicit `DATE CHECK` & 4-Level Verification Legend:** Vermilion-bordered 3-line `DATE CHECK` box documenting excluded Thu 19 / Wed 18 items and Sat 21+ unconfirmed events, directly above the 4-pill verification legend (`[CONFIRMED] 2+ outlets · [OFFICIAL] on the record · [REPORTED] single outlet · [CLAIM] one side's account`).

## Build & verification

The broadsheet is rendered offline with Python, Pillow, and Playwright into `entry.png` (`1024×1024` progressive `4:4:4` JPEG), and `main.ts` validates and writes those exact bytes to `${MAKEFUN_OUTPUT_DIR:-/output}/entry.png` using only Node built-ins.

```bash
python3 build_poster.py
MAKEFUN_OUTPUT_DIR=/tmp/n20-v18-out node --experimental-strip-types main.ts
```

## License

MIT — see [LICENSE](LICENSE).

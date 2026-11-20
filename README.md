# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page archival broadsheet for **news-image-20261120**: 33 stories from
Friday, 20 November 2026, across seven regions, with 13 illustrated editorial
cards, a code-drawn locator map, and 20 single-line dispatches.

## The edition

The front page is 1024 × 1024 and deliberately newspaper-like: warm cream stock,
charcoal rules, crimson accents, Liberation Serif headlines and Lato text.

- **Lead row:** Cyclone Akvan at Gopalpur · the second EU–UK summit in Brussels ·
  COP31's final day in Antalya.
- **Also illustrated:** the Pentagon's $48.3bn Iran-war bill · Rohingya reactions in
  Cox's Bazar · Germany's conscription protests · the UN secretary-general ballot ·
  Africa's Friday at the U-17 World Cup · NextDC's Melbourne retreat · US sanctions
  on the Comancheros · Hormuz war-risk premiums · Russia's strikes on Kyiv bridges ·
  Xi's China–Australia "turnaround" in Shenzhen.
- **Dispatches 14–33:** Africa, Asia-Pacific, the Americas, Europe, the Middle East,
  Oceania and science, each one line and each attributed.

Region tally: **Asia-Pacific 7 · Americas 5 · Europe 5 · Middle East 5 · Africa 4 ·
Oceania 4 · Global/Science 3 = 33**.

## Date discipline

Every story happened, or was first reported, on **Friday 20 November 2026** in a
time zone where the date was already 20 November. The image's `DATE CHECK` box
names the major Thursday 19 November stories deliberately left out: the
Trump–Xi–Putin summit, Anthropic's $81bn IPO, the ICJ Myanmar genocide verdict,
the GTA VI release, the Riyadh PIF Tower strike, the US cyber-chief firing, the
U-17 opening day and the Nvidia subpoena.

Disputed or contested claims are attributed to their sources rather than stated
as fact. The source microline on each card and the right-aligned source on each
dispatch record where the report came from.

## Build

The image is generated offline with Python, Pillow and Playwright. It is included
as `entry.png`, so the submitted program needs only Node's standard library.

```bash
python3 build_poster.py          # rebuilds entry.png and the 300px proof
MAKEFUN_OUTPUT_DIR=out node --experimental-strip-types main.ts
```

`build_poster.py` draws every illustration at 2× and reduces it with Lanczos,
renders the SVG locator map at 2×, screenshots the 1× typographic page with
`/usr/bin/google-chrome` (`--font-render-hinting=none --disable-lcd-text`), runs a
DOM audit (33 stories, 13 badges, 7 region counts, zero overflow/overlap/clipping,
≤2 headline and summary lines, 20 one-line dispatches with ≥15px slack, a two-line
DATE CHECK box), and encodes a baseline 4:4:4 JPEG at quality 91.

Two consecutive builds are byte-identical, and two consecutive runs of
`main.ts` copy the same bytes with no network access.

## Sources

BBC · The Guardian · Al Jazeera · Reuters · RNZ · ABC · The Hindu ·
Africanews · SABC · CNA · The Japan Times · DW · France 24 · 1News ·
Global News · Daily Maverick · Middle East Eye · AP · IMD.

## License

MIT — see [LICENSE](LICENSE).

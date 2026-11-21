# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page editorial front page for **news-image-20261120**: **35 verified pure-Friday stories** from Friday, 20 November 2026 (UTC), spanning all **7 regions** and **25 beats**.

**Changes in v19:** built on the proven `0bdea2b` visual design (13 full-bleed pictorial scenes, crimson banner pills, 6 big-number KPI tiles, airy `THE DAY IN UTC` strip, 7-region proportional bar, and 22 crisp 11 px wire briefs) with five surgical accuracy & craft fixes:

- **Story #28 & full copy audit:** Verified every word across all 35 stories; Story #28 cleanly reports `Gaza: Israeli strikes kill 6 despite truce, rescuers say (Al Jazeera)`.
- **Geographically exact pins (`1–13`):** Every numbered pin sits on verified Natural Earth 110m land with zero overlaps: `1` Kyiv, `2` Odisha/Gopalpur, `3` Wall St/NYC, `4` Santa Clara, `5` Brussels, `6` Antalya (clearly visible in southern Türkiye), `7` Eastern Poland, `8` Hormuz/Oman, `9` New Delhi, `10` Turkana (Kenya), `11` Barcelona (`BARCELONA · MEDICINE`), `12` Buenos Aires, `13` Wellington.
- **Official consensus figures:** Card 1 & KPI 1 print `111 missiles · 404 drones` and `killing at least 9 (7 in Kyiv, 2 in Lviv)`; Card 10 prints `first crude targeted for Dec 1`; Card 12 prints exact `ARGENTINA: 1,070` (`+15%`, first close over 1,000 in 13 months).
- **Zero-contradiction `DATE CHECK` & verification legend:** `DATE CHECK` lists Thu 19 / Wed 18 exclusions (including Voyager 1 on 18 Nov, Tonga drought, Senate Iran vote) and Sat 21–Sun 22 unconfirmed items without mentioning Estonia, paired with the inline footer certainty legend (`[CONFIRMED] 2+ outlets · [OFFICIAL] on the record · [REPORTED] single outlet`).

## Build & verification

The image is generated offline with Python, Pillow, and Playwright into `entry.png` (`1024×1024` progressive `4:4:4` JPEG at q89); `main.ts` validates and writes those exact bytes to `${MAKEFUN_OUTPUT_DIR:-/output}/entry.png` with zero runtime dependencies or network access.

```bash
python3 build_poster.py
MAKEFUN_OUTPUT_DIR=/tmp/n20-v19-out node --experimental-strip-types main.ts
```

## License

MIT — see [LICENSE](LICENSE).

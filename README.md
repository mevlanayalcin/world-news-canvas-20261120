# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 37 stories from Friday,
20 November 2026 (UTC), across seven regions and 25 beats. Version 8 is
built to read at 300 px across. Every card in a row ends on the same
baseline: each lead has a two-line 20 px headline and a three-line summary,
and each of the ten cards has a two-line 14 px headline and a two-line
summary. All 13 datelines print `PLACE · BEAT`, so each card names both
where it happened and its field. Attribution sits in one place, a Title Case
tag at the foot of each illustration, and the wire below runs as 24
single-line briefs with plain bold numerals.

**Changes in v8:** the `CONFIRMED` / `OFFICIAL` / `REPORTED` dateline pills
are gone, and the beat is back on all ten cards (v7 printed the place only);
all 13 attribution tags are in Title Case and name their authority or wire;
lead 1 shows `~110 missiles · 400 drones` in its night sky, and lead 2
labels `Gopalpur` at the landfall dot and the `BAY OF BENGAL`; the map leaves
at least 3.6 px between pin rings (v7: 1 px), which spreads the European pins
1, 4, 5, 6 and 8 by 2–3 px.

## The edition

- **Masthead:** a kicker bar (`THE WORLD IN ONE DAY` · `37 STORIES · 7
  REGIONS · 25 BEATS · EVERY STORY DATED FRIDAY 20 NOVEMBER 2026`), the date
  in large serif type and a crimson deck naming the five leads.
- **Six figures**, each with a crimson accent bar and a two-line plain-English
  explanation, all taken from stories on the page: 3 Dnipro bridges damaged ·
  372,000 evacuated in Odisha · −6.23% Taiex close · 100,000 UK–EU youth
  places a year · 2.3% Japan October CPI · 118 runs for Glenn Phillips.
- **Region bar:** segment widths are proportional to story counts:
  **Europe 8 · Asia-Pacific 9 · Americas 5 · Middle East 4 · Africa 5 ·
  Oceania 3 · Global/Science 3 = 37**. The counts are computed from
  `STORIES`.
- **Three leads (1–3):** "Russian Missiles Hit Three / Bridges Across the
  Dnipro" · "Cyclone Akvan Makes Landfall / Near Gopalpur in Eastern India" ·
  "AI Sell-Off Sinks Asia's Stock / Markets in Worst Week Since 2020". The
  line breaks are fixed, and each three-line 10.8 px summary ends with its
  sources.
- **Ten illustrated cards (4–13):** the UK–EU reset · COP31's final day ·
  a Russian cruise missile in Poland · the Iraqi army in central Iraq ·
  Italy's general strike · Japan's 2.3% inflation · Seoul's move to impeach
  the chief justice · Kenya's first oil well · Bukele's third-term filing ·
  Glenn Phillips' 118 against India.
  Every lead and card has a dateline row (number disc, then `PLACE · BEAT`):
  `KYIV, UKRAINE · WAR`, `ODISHA, INDIA · CYCLONE`,
  `TAIPEI · SEOUL · TOKYO · MARKETS`, `BRUSSELS · DIPLOMACY`,
  `ANTALYA · CLIMATE`, `EASTERN POLAND · SECURITY`,
  `CENTRAL IRAQ · SECURITY`, `ROME · LABOUR`, `TOKYO · ECONOMY`,
  `SEOUL · POLITICS`, `TURKANA, KENYA · ENERGY`, `SAN SALVADOR · POLITICS`,
  `WELLINGTON · CRICKET`. Below it come a serif headline and a summary that
  ends with its sources in brackets.
- **Where it happened:** a dark-ocean Natural Earth 110m map with 13 large
  numbered pins, one for each illustrated story. At least 3.5 px of map
  shows between any two white pin rings. Pins
  pushed off a crowded spot are tied back to the true location by a leader
  line.
- **Also on Friday 20 November (14–37):** 24 briefs in two columns of 12.
  Each brief is one line: a plain bold 10.8 px numeral in its region colour
  (no disc, since only stories 1–13 are map pins), a bold place, a headline
  with its figure, and the source.
- **DATE CHECK:** a cream box with a crimson border. It names what was left
  out as Thursday 19 November news (the ICJ's Myanmar genocide ruling, the
  Trump–Xi–Putin Shenzhen declaration, the Pentagon's $48.3bn Iran war
  tally, Anthropic's $83 IPO debut, Voyager 1's light-day milestone, GTA VI's
  launch) and what had not yet happened (BepiColombo's Saturday 21 November
  Mercury orbit capture, any final COP31 text). A footer line follows it.

## Illustrations

`art.py` draws all 13 pictures from scratch with Pillow. Each scene fills its
whole box. It is drawn at 2× and reduced with Lanczos, and any fill touching
the scene's top edge continues under the badge. The type is drawn afterwards
at printed size, so FreeType renders it at its final pixel size:

- **Leads (316×132):** a 17 px badge at top left (`KYIV`, `CYCLONE AKVAN`,
  `AI SELL-OFF`), a 14 px white callout stacked 3 px below it
  (`3 bridges hit`, `Landfall · 8 am`, `Asia, Friday's close`) and an
  attribution tag at bottom left (`Officials' count`, `Weather office · IMD`,
  `Closing prices`). Lead 1 adds `~110 missiles · 400 drones` in cream type
  on the night sky; lead 2 labels `Gopalpur` beside the landfall dot and
  `BAY OF BENGAL` in the sea. Lead 3 pairs a plunging index curve (x = 15–195) with a
  closing scoreboard: Taipei −6.2%, Seoul −5.2%, Tokyo −5.1%, Sing. −2.1%,
  white city names and `#ff6b6b` figures in 15 px type.
- **Cards (188×78):** a 14 px badge (`UK–EU DEAL`,
  `COP31: NO DEAL`, `POLAND: MISSILE`, `IRAQ: ARMY IN`, `ITALY: STRIKE`,
  `JAPAN: +2.3%`, `SEOUL: IMPEACH`, `KENYA: OIL`, `BUKELE: 3RD BID`,
  `PHILLIPS: 118`) and an attribution tag at bottom right: `Agreed · Reuters`,
  `Ongoing · UN News`, `PM says · Guardian`, `Officials · Reuters`,
  `Reported · AP`, `Official data · MIC`, `Party vote · Herald`,
  `Spudded · The Star`, `Filed · AP`, `Scorecard · ICC`.

All 13 badges are solid `#b8292f` with white type and no outline.

The art build fails if a badge is outside 16–18 px (leads) or 13–14 px
(cards), if a label sits within 3 px of an edge, or if two labels overlap.

## Build

The image is generated offline with Python, Pillow and Playwright, then
committed as `entry.png`, so the submitted program needs only Node's standard
library.

```bash
python3 build_poster.py          # rebuilds art, entry.png and /tmp/news_1120_v8_300.png
MAKEFUN_OUTPUT_DIR=out node main.ts
```

Before rendering, `build_poster.py` checks the story list:

- stories 1–37 in order: 3 leads, 10 cards and 24 briefs;
- every brief (numeral included) measured in Pillow at 10.5 px and no wider
  than 328 px;
- every headline figure backed by its story's text;
- no story mentions anything reserved for the DATE CHECK box.

It then renders the page in `/usr/bin/google-chrome` and runs a DOM audit:

- a 1024×1024 document with no overflow, clipped text or overlapping blocks;
- every brief on exactly one line, and every figure explanation on exactly
  two lines;
- every headline exactly two lines; lead summaries exactly three lines and
  ending on one shared baseline; card summaries exactly two lines;
- every dateline reading exactly `PLACE · BEAT` on one line with at least
  12 px to spare (the tightest, `EASTERN POLAND · SECURITY`, has 18 px), and
  no certainty pills left on the page;
- wire numerals plain bold 10.8 px text, with no disc or background;
- 13 pins numbered 1–13 with an 8.5 px radius, inside the map, with at
  least 3 px between white rings;
- HTML text at least 9.5 px and map numbers at 10 px;
- omitted news found inside the DATE CHECK box and nowhere else.

The page is saved as a progressive 4:4:4 JPEG. The build tries q90 first,
which must come in under 450,000 bytes. It then tries q89, which must stay
under 460,000 bytes. The current file is q89 at 458,597 bytes; the gate
allows 1,048,576. Two builds produce a byte-identical `entry.png`, and
`main.ts` copies those bytes without network access.

## Sources

Reuters · AP · AFP · Al Jazeera · The Guardian · CBS · ABC (Australia) ·
IMD · The Hindu · Kyiv Independent · La Repubblica · UN · EU · Quai d'Orsay ·
MIC · Japan Times · Korea Herald · KDCA · PBOC · FMPRC · SGX · The Star
(Kenya) · NWS · Formula 1 · ATP · ICC · RNZ · Security Council Report · WCS ·
UKMTO · IOM · AfDB.

## License

MIT — see [LICENSE](LICENSE).

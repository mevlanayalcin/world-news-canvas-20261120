# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 35 stories from Friday,
20 November 2026 (UTC), across seven regions and 25 beats.

**Changes in v16:** a lighter page with the same Friday news.

- The dark `FRI 20 NOV · UTC` bar is now `THE DAY IN UTC`: a crimson tag
  and six cream cells with thin borders, so no dark band sits on top of
  the region bar.
- The 13 pictures no longer carry a black source pill. Each picture keeps
  its crimson badge (plus the callout on leads and the scoreboard on lead
  3), and the caption under it still names its sources; the build fails
  if any caption is missing them.
- Briefs drop from 24 to 22: the ATP pay plan and the wet Las Vegas
  practice are gone. The rest are set at 11 px on a 15 px pitch with a
  numbered disc in the region colour. Six briefs were reworded to fit one
  line without changing their facts.
- The deck is slate instead of crimson. That keeps the JPEG at q89 inside
  the 455,000-byte budget.

## The edition

- **Masthead:** a kicker bar (`THE WORLD IN ONE DAY` · `35 STORIES · 7
  REGIONS · 25 BEATS · EVERY STORY DATED FRIDAY 20 NOVEMBER 2026`, counted
  from `STORIES`), the date in large serif type and a slate deck naming the
  five leading stories.
- **Six figures:** 3 Dnipro bridges damaged · 372,000 evacuated in Odisha ·
  −5.3% Nasdaq (S&P −3.7%, Taiex −6.2%) · 60.7% response in the
  daraxonrasib trial · 100,000 UK–EU youth places a year · 118 runs for
  Glenn Phillips.
- **`THE DAY IN UTC` strip:** six cream cells, each a crimson time and a
  dark label: OVERNIGHT Kyiv bridges hit · ~02:30Z Akvan landfall · ASIA
  CLOSE Taiex −6.2% · EUROPE DAY UK–EU reset · 15:50Z Cancer trial 60.7% ·
  21:37Z Nvidia SEC · S&P −3.7%. The three clock times are published ones:
  IMD's 8 am IST landfall, the OncLive/Oncodaily release and the Reuters
  SEC report.
- **Region bar:** segment widths are proportional to story counts:
  **Europe 7 · Asia-Pacific 8 · Americas 4 · Middle East 5 · Africa 5 ·
  Oceania 2 · Global/Science 4 = 35**, computed from `STORIES`.
- **Three leads (1–3):** `KYIV, UKRAINE · WAR` (OFFICIAL) · `ODISHA, INDIA ·
  CYCLONE` (OFFICIAL) · `GLOBAL MARKETS · AI ROUT` (CONFIRMED).
- **Ten illustrated cards (4–13):** `US · TECH` Nvidia SEC probe (REPORTED) ·
  `BRUSSELS · DIPLOMACY` UK–EU reset · `ANTALYA · CLIMATE` COP31 ·
  `POLAND · SECURITY` cruise missile (OFFICIAL) · `HORMUZ · MARITIME` tanker
  struck (OFFICIAL) · `NEW DELHI · TALKS` Pakistani minister's visit ·
  `KENYA · ENERGY` first oil well · `GLOBAL · MEDICINE` daraxonrasib trial
  (REPORTED) · `ARGENTINA · MARKETS` country risk over 1,000 ·
  `WELLINGTON · CRICKET` Phillips 118. Unmarked cards are CONFIRMED.
- **Where it happened:** a dark-ocean Natural Earth 110m map with 13
  numbered pins. Pin 4 marks the SEC in Washington, pin 3 Taipei (the day's
  steepest fall), pin 8 Musandam in Oman and pin 11 Redwood City, home of
  Revolution Medicines, which develops daraxonrasib.
- **Also on Friday 20 November (14–35):** 22 one-line briefs in two columns
  of 11, covering all seven regions. Each has a 15 px numbered disc in its
  region colour, 11 px `#111827` type, a bold place name and a 15 px row
  pitch with alternate rows tinted.
- **DATE CHECK:** left out as Thursday 19 November news: Bukele's
  third-term bid, Kyiv embassy damage, the ICJ Myanmar ruling, the
  Trump–Xi–Putin Shenzhen talks, Anthropic's $83 debut, Voyager 1's
  light-day and the GTA VI launch. Not yet happened: BepiColombo's Saturday
  21 November Mercury orbit capture and any final COP31 text.

## Illustrations

`art.py` draws all 13 pictures from scratch with Pillow, at 2× and reduced
with Lanczos; type is drawn afterwards at printed size. No picture carries a
source pill: the caption under it names the sources. Leads are 316×132
with a 17 px badge and a 14 px callout; lead 3's board shows
Taipei −6.2%, Nasdaq −5.3%, Seoul −5.2% and S&P 500 −3.7%. Cards are 188×78
with a 14 px badge: `NVIDIA: SEC PROBE` (chip, falling red line, SEC filing
under a magnifier), `UK–EU DEAL`, `COP31: NO DEAL`, `POLAND: MISSILE`,
`HORMUZ: TANKER` (burning tanker below the Oman coast), `INDIA–PAKISTAN`
(both flags, an SCO arch and a dotted bridge), `KENYA: OIL`,
`CANCER: 60.7%` (capsule and rising response bars), `ARGENTINA: 1,000+`
(flag stripes, Sun of May and a gauge needle past the 1,000 mark) and
`PHILLIPS: 118`.

## Build

The image is generated offline with Python, Pillow and Playwright, then
committed as `entry.png`, so the submitted program needs only Node's standard
library.

```bash
python3 build_poster.py          # rebuilds art, entry.png and /tmp/news_1120_v16_300.png
MAKEFUN_OUTPUT_DIR=out node main.ts
```

Before rendering, `build_poster.py` checks the story list:

- stories 1–35 in order: 3 leads, 10 cards and 22 briefs;
- every brief (number disc included) measured in Pillow at 11 px and no
  wider than 328 px;
- every headline figure, and every figure quoted in a figure label, backed
  by its story's text;
- at least 25 beats, and briefs from all seven regions;
- timeline clock times limited to the three published ones;
- no story mentions anything reserved for the DATE CHECK box.

`art.py` then draws the 13 pictures and fails if any label overlaps
another, sits under 3 px from the edge or is a source pill, and `mapgen.py`
fails unless every true-location dot is on Natural Earth land, rings keep
at least 3 px apart and leaders are 2–6 px long and never cross.

It then renders the page in `/usr/bin/google-chrome` and runs a DOM audit:

- a 1024×1024 document with no overflow, clipped text or overlapping
  blocks, ending at or above y = 1020;
- every brief on exactly one line, and every figure explanation on exactly
  two lines;
- every headline exactly two lines; lead summaries exactly three lines and
  ending on one shared baseline; card summaries exactly two lines;
- every dateline reading exactly `PLACE · BEAT` (with a `·`) on one line;
- exactly one tinted certainty pill per card, matching the story's tag, on
  the dateline row only (none in headlines or summaries), flush with the
  row's right edge, vertically centred on the dateline and at least 9 px;
- at least 6 px of clear space between the end of `PLACE · BEAT` and the
  pill. The tightest are `WELLINGTON · CRICKET` (8.5 px) and
  `BRUSSELS · DIPLOMACY` (8.7 px);
- the `THE DAY IN UTC` strip exactly 18 px tall and one line, with no dark
  background: six cream (`#FFFDF7`) cells with 1 px borders, 4 px apart,
  filling the rail;
- every card caption ending with its sources in brackets;
- card datelines at least 8.5 px;
- every brief number a 15 px disc in its region colour, centred on its row;
- 13 pins numbered 1–13 with an 8.5 px radius, inside the map, with at
  least 3 px between white rings;
- HTML text at least 9.5 px and map numbers at 10 px;
- omitted news found inside the DATE CHECK box and nowhere else.

The page is saved as a progressive 4:4:4 JPEG at q89, which must land
between 380,000 and 455,000 bytes. The current file is 454,128 bytes; the
gate allows 1,048,576. Two builds produce a byte-identical `entry.png`, and
`main.ts` copies those bytes without network access.

## Sources

Reuters · CNBC · Bloomberg · NYT · WSJ · AP · AFP · Al Jazeera ·
The Guardian · ABC (Australia) · IMD · The Hindu · Kyiv Independent ·
La Repubblica · UN · EU · MIC · Korea Herald · KDCA · PBOC · FMPRC ·
OncLive · Oncodaily · UKMTO · gCaptain · PTI · Buenos Aires Herald ·
The Star (Kenya) · NWS · ICC · RNZ · WCS · IOM · AfDB.

## License

MIT — see [LICENSE](LICENSE).

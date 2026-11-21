# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 37 stories from Friday,
20 November 2026 (UTC), across seven regions and 25 beats, built to read at
300 px across.

**Changes in v11:** v11 combines the v9 page with the v10 artwork.

- **From v9:** all 37 stories, the 24-brief wire (14–37), the headlines
  (including "AI Sell-Off Sinks Asia's Stock / Markets in Worst Week Since
  2020"), the datelines with their `OFFICIAL` / `CONFIRMED` / `REPORTED`
  pills, the DATE CHECK box and the page layout, all unchanged.
- **The 13 attribution tags are back** at the foot of each illustration
  (`Officials' count`, `Weather office · IMD`, `Closing prices`, `Agreed ·
  Reuters`, `Ongoing · UN News`, `PM says · Guardian`, `Officials ·
  Reuters`, `Reported · AP`, `Official data · MIC`, `Party vote · Herald`,
  `Spudded · The Star`, `Filed · AP`, `Scorecard · ICC`). On lead 2 the tag
  sits at bottom centre, between the palms and the track arrow and clear of
  the cyclone eye. On lead 1 it sits below the bridge impacts, and on lead 3
  it sits left of the index board.
- **From v10:** the new art (the Kyiv twilight skyline with gilded domes, the
  Lavra bell tower and three arched bridges with glowing impacts and their
  reflections; the Cyclone Akvan radar spiral with its eye at Gopalpur, a
  gold track arrow and wind-bent palms; the glowing crimson index curve over
  a lit chip; the larger, darker Poland missile; the sun glow behind Kenya's
  derrick; a 6% contrast lift on every picture), plus the map pins with a
  9 px radius, a dark keyline and at least 4 px of map between keylines.
- **Wire ink:** brief text and bold place names are now `#111827` (v9:
  `#1E242E` / `#0E121A`), sources `#4B5563` (v9: `#585D66`), and the
  numerals are set in Lato Black (900) in their region colours. Type size
  and grid are the same as v9.

## The edition

- **Masthead:** kicker bar (`THE WORLD IN ONE DAY` · `37 STORIES · 7
  REGIONS · 25 BEATS · EVERY STORY DATED FRIDAY 20 NOVEMBER 2026`), the date
  in large serif type and a crimson deck naming the five leads.
- **Six figures**, all taken from stories on the page: 3 Dnipro bridges
  damaged · 372,000 evacuated in Odisha · −6.23% Taiex close · 100,000 UK–EU
  youth places a year · 2.3% Japan October CPI · 118 runs for Glenn Phillips.
- **Region bar** (widths proportional, counts computed from `STORIES`):
  **Europe 8 · Asia-Pacific 9 · Americas 5 · Middle East 4 · Africa 5 ·
  Oceania 3 · Global/Science 3 = 37**.
- **Three leads (1–3)** and **ten illustrated cards (4–13)**: Kyiv bridges ·
  Cyclone Akvan · Asia's AI sell-off · UK–EU reset · COP31's final day ·
  Russian cruise missile in Poland · Iraqi army in a militia stronghold ·
  Italy's general strike · Japan's 2.3% inflation · Seoul's move to impeach
  the chief justice · Kenya's first oil well · Bukele's third-term filing ·
  Glenn Phillips' 118. Each has a dateline row with `PLACE · BEAT` and a
  tinted certainty pill, a two-line serif headline, and a summary that ends
  with its sources.
- **Where it happened:** a dark-ocean Natural Earth 110m map with 13 numbered
  pins, one for each illustrated story. When a pin has to be moved off a
  crowded spot, a leader line ties it back to the true location.
- **Also on Friday 20 November (14–37):** 24 one-line briefs in two columns
  of 12, each with a bold numeral in its region colour, a bold place, the
  news and its source.
- **DATE CHECK:** a cream box with a crimson border. It lists what was left
  out as Thursday 19 November news (the ICJ's Myanmar genocide ruling, the
  Trump–Xi–Putin Shenzhen declaration, the Pentagon's $48.3bn Iran war
  tally, Anthropic's $83 IPO debut, Voyager 1's light-day milestone, GTA VI's
  launch) and what had not happened yet (BepiColombo's Saturday 21 November
  Mercury orbit capture, any final COP31 text).

## Illustrations

`art.py` draws all 13 pictures with Pillow, at 2× size, then reduces them
with Lanczos. Glows are blurred masks blended into the scene, and the
cyclone's radar field is computed with NumPy. Labels are drawn afterwards at
printed size: a crimson badge on every picture, a white callout on the
leads, an attribution tag on every picture (bottom left on leads 1 and 3,
bottom centre on lead 2, bottom right on the cards), the barrage size on
lead 1, `Gopalpur` and `BAY OF BENGAL` on lead 2 and the index board on
lead 3. The art build fails if a badge is outside 16–18 px (leads) or
13–14 px (cards), if a label sits within 3 px of an edge, if two labels
overlap, or if a picture does not have exactly one attribution tag.

## Build

```bash
python3 build_poster.py          # art, entry.png and /tmp/news_1120_v11_300.png proof
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`build_poster.py` first checks the story list: stories 1–37 in order (3
leads, 10 cards, 24 briefs), each brief no wider than 328 px at 10.5 px,
every headline figure backed by its story's text, at least 25 beats, and
nothing from the DATE CHECK box in any story. It then renders the page in
Chrome and audits the DOM:

- the document is exactly 1024×1024, with no overflow, clipped text or
  overlapping blocks;
- every headline runs exactly two lines; lead summaries run three lines and
  end on one shared baseline, card summaries run two;
- each brief and each dateline fits on one line;
- every card has exactly one certainty pill, on its dateline row, flush
  right and at least 6 px clear of `PLACE · BEAT`;
- wire numerals are plain Lato Black text with no disc or background;
- the 13 pins (numbered 1–13) stay inside the map, with at least 4 px
  between their outer keylines;
- omitted news appears inside the DATE CHECK box and nowhere else.

The page is saved as a progressive 4:4:4 JPEG at the highest quality from
q91 down that lands between 430,000 and 470,000 bytes. The current file is
q88 and 461,147 bytes. Two builds produce a byte-identical `entry.png`, and
`main.ts` copies those bytes without network access.

## Sources

Reuters · AP · AFP · Al Jazeera · The Guardian · CBS · ABC (Australia) ·
IMD · The Hindu · Kyiv Independent · La Repubblica · UN · EU · Quai d'Orsay ·
MIC · Japan Times · Korea Herald · KDCA · PBOC · FMPRC · SGX · The Star
(Kenya) · NWS · Formula 1 · ATP · ICC · RNZ · Security Council Report · WCS ·
UKMTO · IOM · AfDB.

## License

MIT — see [LICENSE](LICENSE).

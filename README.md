# The World Canvas — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/mevlanayalcin/world-news-canvas-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

A one-page front page for **news-image-20261120**: 27 stories from Friday,
20 November 2026 (UTC), across seven regions and 20 beats, built to read at
300 px across.

**Changes in v10:**

- **Cleaner art.** The dark attribution boxes that sat on top of all 13
  illustrations (`Officials' count`, `Weather office · IMD`, `Closing
  prices`, `Agreed · Reuters` and the rest) are gone. Each story's sources
  still print at the end of its caption.
- **New lead art.** Kyiv: a twilight skyline with gilded domes and the Lavra
  bell tower, three arched bridges in depth, glowing impact bursts and their
  reflections in the river; the near bridge is broken. Cyclone Akvan: a
  radar-style reflectivity spiral (green, yellow, orange, red) whose eye sits
  on the Odisha coast at Gopalpur, a bold gold track arrow from the south-east
  and wind-bent palms on the shore. AI sell-off: the same index board
  (Taipei −6.2%, Seoul −5.2%, Tokyo −5.1%, Sing. −2.1%), with a glowing
  crimson curve over a softly lit chip.
- **Cards.** A bigger, darker cruise missile with a glowing exhaust over
  Poland, a sun glow behind Kenya's derrick, and a 6% contrast lift on every
  picture.
- **Type.** The masthead is set heavier, under a 3 px crimson rule, with a
  2 px crimson rule below the deck. Lead headlines go from 20 px to 22 px,
  card headlines from 14 px to 15 px. Lead 3 now breaks as "AI Sell-Off
  Sinks Asia's Stocks / in Worst Week Since 2020" so it fits.
- **Wire.** It is cut from 24 briefs to 14 (two per region), set at 11.5 px
  (was 10.5 px) on a 22.5 px row pitch (was 13.8 px).
- **Map.** Pins are now 9 px in radius with a dark keyline outside the white
  ring, and there are at least 4 px of map between keylines.

## The edition

- **Masthead:** kicker bar (`THE WORLD IN ONE DAY` · `27 STORIES · 7
  REGIONS · 20 BEATS · EVERY STORY DATED FRIDAY 20 NOVEMBER 2026`), the date
  in large serif type and a crimson deck naming the five leads.
- **Six figures**, all taken from stories on the page: 3 Dnipro bridges
  damaged · 372,000 evacuated in Odisha · −6.23% Taiex close · 100,000 UK–EU
  youth places a year · 2.3% Japan October CPI · 118 runs for Glenn Phillips.
- **Region bar** (widths proportional, counts computed from `STORIES`):
  **Europe 6 · Asia-Pacific 6 · Americas 3 · Middle East 3 · Africa 3 ·
  Oceania 3 · Global/Science 3 = 27**.
- **Three leads (1–3)** and **ten illustrated cards (4–13)**: Kyiv bridges ·
  Cyclone Akvan · Asia's AI sell-off · UK–EU reset · COP31's final day ·
  Russian cruise missile in Poland · Iraqi army in a militia stronghold ·
  Italy's general strike · Japan's 2.3% inflation · Seoul's move to impeach
  the chief justice · Kenya's first oil well · Bukele's third-term filing ·
  Glenn Phillips' 118. Each has a dateline row with `PLACE · BEAT` and a
  tinted certainty pill (`OFFICIAL`, `CONFIRMED` or `REPORTED`), a serif
  headline, and a summary that ends with its sources.
- **Where it happened:** a dark-ocean Natural Earth 110m map with 13 numbered
  pins, one for each illustrated story. When a pin has to be moved off a
  crowded spot, a leader line ties it back to the true location.
- **Also on Friday 20 November (14–27):** two columns of seven one-line
  briefs. Column one: Lviv, Paris, Beijing, Changwon, Washington,
  Brevard FL, Riyadh. Column two: Hormuz, Johannesburg, Abidjan, Sydney,
  Shenzhen (Albanese), New York (UN), Amazon.
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
leads, the barrage size on lead 1, `Gopalpur` and `BAY OF BENGAL` on lead 2
and the index board on lead 3. The art build fails if a badge is outside
16–18 px (leads) or 13–14 px (cards), if a label sits within 3 px of an edge,
if two labels overlap, or if an attribution box is drawn over a picture.

## Build

```bash
python3 build_poster.py          # art, entry.png and /tmp/news1120_300px.png proof
MAKEFUN_OUTPUT_DIR=out node main.ts
```

`build_poster.py` first checks the story list: stories 1–27 in order (3
leads, 10 cards, 14 briefs, exactly two briefs per region), each brief no
wider than 335 px at 11.5 px, every headline figure backed by its story's
text, and nothing from the DATE CHECK box in any story. It then renders the
page in Chrome and audits the DOM:

- the document is exactly 1024×1024, with no overflow, clipped text or
  overlapping blocks;
- every headline runs exactly two lines; lead summaries run three lines and
  end on one shared baseline, card summaries run two;
- each brief and each dateline fits on one line;
- every card has exactly one certainty pill, on its dateline row, flush
  right and at least 6 px clear of `PLACE · BEAT`;
- the 13 pins (numbered 1–13) stay inside the map, with at least 4 px
  between their outer keylines;
- omitted news appears inside the DATE CHECK box and nowhere else.

The page is saved as a progressive 4:4:4 JPEG at the highest quality from
q91 down that fits in 500,000 bytes. The current file is q91 and
496,577 bytes. Two builds produce a byte-identical `entry.png`, and
`main.ts` copies those bytes without network access.

## Sources

Reuters · AP · AFP · Al Jazeera · The Guardian · CBS · ABC (Australia) ·
IMD · The Hindu · Kyiv Independent · La Repubblica · UN · EU · Quai d'Orsay ·
MIC · Japan Times · Korea Herald · KDCA · PBOC · The Star (Kenya) · NWS ·
ICC · RNZ · Security Council Report · WCS · AfDB · Iraqi officials ·
David Jones receivers.

## License

MIT — see [LICENSE](LICENSE).

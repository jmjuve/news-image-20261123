# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/jmjuve/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/jmjuve/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A program that draws one image summing up the world news of
Monday 23 November 2026, as a newsprint front page.

- **Hero:** Nepal PM Balendra Shah meets PM Narendra Modi in Delhi —
  first bilateral visit, energy / trade / connectivity talks, joint
  press conference to follow.
- **Minis:** Molly Meldrum dies aged 83 · final day of the Wellington
  Test · Canberra's last sitting week of 2026.

## Run

```sh
python3 main.py            # writes out/entry.png
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # grader mode
```

Pure Python 3 standard library — no dependencies, no network, no
external fonts. The PNG output is deterministic: every run writes
the same bytes. Image is 1024×1024, well under 1 MiB.

## Licence

MIT — see [LICENSE](LICENSE).

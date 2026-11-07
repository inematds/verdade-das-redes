# The truth about social media

[![The truth about social media](guia/assets/banner-en.jpg)](https://inematds.github.io/verdade-das-redes/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

The truth about social media is an open study that brings together the real numbers from INEMA’s channels on YouTube, Instagram, and TikTok. It’s for people who create content and want to know what actually works, based on data rather than a guru’s promises. A bot collects the numbers every day and every week, matches the same piece of content across the three platforms, and generates a report. If you just want to learn, read the findings; to run it on your own channels, you’ll need Python and access to your own accounts.

## 📖 User guide

Full guide (landing page + step-by-step instructions): **https://inematds.github.io/verdade-das-redes/guia/en/**

---

Real data from 17 YouTube channels and INEMA’s Instagram and TikTok accounts, collected daily and weekly
to find out **what actually works** on social media. No formulas, no gurus, no “celebrity playbooks”: numbers with dates,
including the failures.

> “I have 17 YouTube channels. Only one is growing. What did it teach me?”

## What we’ve discovered (07/11/2026)

- **The same content gets opposite results on each platform.** GitHub’s Top 10 got 138,677 views on Instagram, 460 on TikTok, and 33 on YouTube.
  The eventosextremos content takes the opposite path: a median of 7,400 on YouTube and ~150 on Instagram.
- **YouTube rewards what people search for and come back to watch**; Instagram rewards what people save and share; TikTok rewards what keeps people watching to the end.
- **Posting too much hurts performance**: days with 3–4 shorts brought in 17–31 thousand views per video; days with 8–9 brought in 2–4 thousand.
- **9 AI channels are splitting a small audience**: 1,520 videos, only 24 passed 500 views. What worked: tutorials that solve a problem and AI for people 40+.

Full report: [relatorios/2026-11-07.md](relatorios/2026-11-07.md) (in Portuguese). Tests in progress: [testes.md](testes.md) (in Portuguese).

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Daily Instagram and TikTok collection (3 Metricool brands, 14-day window, one snapshot per day) | `coleta/metricool.sh` | ⚙️ `verdade-metricool` timer 06:30 → 🤖 `claude -p` with the `metricool-inematds` connector |
| 2 | Weekly YouTube collection (everything the channels published in the last 60 days, with views, likes, and comments) | `coleta/youtube.py` | ⚙️ `verdade-youtube` timer Monday 07:00 |
| 3 | Match platforms by the same piece of content (the Instagram/TikTok text includes the YouTube link) and compile the week’s numbers | `coleta/junta.py` | ⚙️ runs at the end of step 2 |
| 4 | Read the numbers and record confirmed rules and hypotheses | `relatorios/AAAA-MM-DD.md` | 🧠 session with Nei |
| 5 | Start or close a test (e.g., ≤ 4 shorts per day), with start and end dates | `testes.md` | 🧠 session with Nei |
| 6 | Turn it into content: the week’s “The truth about social media” (carousel, video, INEMA.VIBE topic) | video/carousel skills | 🧠 + 🤖 |

## Sources and limitations

- **YouTube**: YouTube Data API v3, read-only, using the livestream tokens from `yt-pubx`. Retention, traffic sources, and CTR are **not** included
  (they require the YouTube Analytics API, which the tokens are not scoped for).
- **Instagram and TikTok**: Metricool (the `metricool-inematds` connector): inema.tds, eventosextremos, and FTD (inema.tech) brands.
- **Facebook**: no data source yet.
- Raw data stays in `dados/` and **is not included in the repository**; only reports and code are included.

## Run manually

```bash
python3 coleta/autorizar.py client_secret.json ~/minhas-credenciais.json  # YouTube read credential
python3 coleta/youtube.py            # all channels
python3 coleta/youtube.py lives10    # one channel
bash coleta/metricool.sh             # Instagram + TikTok
python3 coleta/junta.py              # weekly table
```
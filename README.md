# Lucid Research — CS Conference Deadlines

**Live:** https://krimler.github.io/paper-tracker/

A daily-refreshed tracker for top-tier CS conference deadlines across theory,
security, distributed systems, networking, systems, databases, software
engineering / PL, AI/ML and biomedical.

The site is a single static page. It fetches `data/conferences.json` in the
browser and does all searching, filtering, sorting and pagination client-side —
no server, no build step, no framework.

Data sources: [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines),
ai-deadlines, sec-deadlines and tcs-conf, filtered to a curated allowlist of
CORE A*/A venues plus community-respected "gem" venues (COLM, MLSys, HotNets,
HotOS, CIDR, etc.). The allowlist is curated rather than exhaustive, and leans
towards the venues practising engineers and developers read.

Companion project: the [workshop tracker](https://krimler.github.io/workshop-tracker/).

By [Madhava Gaikwad](https://www.linkedin.com/in/alignops/).

## Layout

```
index.html                 # the whole site: directory, filters, feeds, embed mode
allowlist.yml              # curated conferences to track, grouped by area
fetcher/fetch.py           # pulls the public trackers, filters by allowlist, writes JSON
data/conferences.json      # generated snapshot (committed daily, fetched by index.html)
gen_feeds.py               # writes feed.xml + deadlines.ics from the snapshot
gen_og.py                  # regenerates og-image.png for link previews
feed.xml                   # RSS of upcoming deadlines (served by Pages)
deadlines.ics              # iCal subscription of upcoming deadlines (served by Pages)
llms.txt robots.txt sitemap.xml aipref.txt   # discovery files
.github/workflows/fetch.yml  # daily GitHub Actions cron
requirements.txt
```

## Site features

- **Directory table.** Every tracked venue with its abstract and full deadline,
  a live countdown, location, CORE and CCF rank, split into Upcoming and Past.
- **Filters.** Search, research area, CORE tier, conference year, "deadline
  within N days", published-deadline-only, and starred-only. Sort by soonest
  deadline, CORE rank, name or year.
- **Shareable views.** Filters are reflected in the URL, so
  `?area=security&rank=astar&within=90&sort=core` opens pre-filtered.
- **Embed mode.** `?mode=embed&area=ai_ml&limit=5` renders a chrome-free mini
  list sized for an `<iframe>`.
- **Watchlist.** The ★ on each row saves a venue to `localStorage` (client-side,
  no backend); "Starred venues only" filters to them.
- **Exports.** CSV of the current filter selection, and a per-venue `.ics` with
  7-day and 1-day alarms from the 📅 on each row.
- **Feeds.** `feed.xml` (RSS) and `deadlines.ics` (subscribable calendar with
  alarms) are regenerated daily alongside the data.

## Running locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Refresh the data snapshot and feeds
python fetcher/fetch.py
python gen_feeds.py

# Serve the site (fetch() needs http://, not file://)
python -m http.server 8000
# then open http://localhost:8000/
```

## Deployment

GitHub Pages serves the repo root, and a daily GitHub Action keeps the data
fresh — that is the whole deployment.

1. **GitHub Actions** runs `fetcher/fetch.py` and `gen_feeds.py` on a daily cron
   (see `.github/workflows/fetch.yml`) and commits the refreshed
   `data/conferences.json`, `feed.xml` and `deadlines.ics` back to the repo.
2. **GitHub Pages** is enabled on `main` at the repo root. `.nojekyll` makes
   Pages serve the files as-is and lets `index.html` take precedence over this
   README. Every push, including the daily data commit, republishes the site.

## Editing the tracked conferences

Edit `allowlist.yml`. The fetcher matches the `title` field from the upstream
trackers case-insensitively. If a name doesn't match, the next fetcher run logs
it under the "unmatched" list in the JSON snapshot.

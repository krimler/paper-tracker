# Lucid Research — CS Conference Deadlines

**Live:** https://paper-tracker-madhava.streamlit.app/

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://paper-tracker-madhava.streamlit.app/)

A daily-refreshed tracker for top-tier CS conference deadlines across theory,
security, distributed systems, networking, systems, databases, software
engineering / PL, and AI/ML.

Data source: [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines),
filtered to a curated allowlist of CORE A*/A venues plus community-respected
"gem" venues (COLM, MLSys, HotNets, HotOS, CIDR, etc.).

By [Madhava Gaikwad](https://www.linkedin.com/in/alignops/).

## Layout

```
allowlist.yml              # curated conferences to track, grouped by area
fetcher/fetch.py           # clones ccfddl, filters by allowlist, writes JSON
data/conferences.json      # generated snapshot (committed daily)
gen_feeds.py               # writes feed.xml + deadlines.ics from the snapshot
feed.xml                   # RSS of upcoming deadlines (served by Pages)
deadlines.ics              # iCal subscription of upcoming deadlines (served by Pages)
app.py                     # Streamlit dashboard
.github/workflows/fetch.yml  # daily GitHub Actions cron
requirements.txt
```

## Discoverability & client features

- **RSS / iCal feeds.** `gen_feeds.py` runs after the daily fetch and writes
  `feed.xml` and `deadlines.ics` to the repo root; GitHub Pages serves them at
  `…/paper-tracker/feed.xml` and `…/paper-tracker/deadlines.ics`. The `.ics`
  carries 7-day and 1-day `VALARM` reminders, so a Google/Apple Calendar
  subscription notifies you automatically. Stdlib only — no extra CI deps.
- **Shareable filtered views.** Filters sync to the URL via `st.query_params`,
  e.g. `?area=security&rank=astar&sort=core&view=table&within=90`. Opening such
  a link pre-applies the filters. `area` repeats for multi-select.
- **Embed mode.** `?mode=embed&area=ai_ml&limit=5` renders a chrome-free card
  list for an `<iframe>` (pair with Streamlit's native `&embed=true` to also drop
  Streamlit's own toolbar/footer). Note: `embed` is a *reserved* Streamlit query
  param, which is why the app uses `mode=embed`.
- **Watchlist + reminders.** A per-card ★ saves venues to `localStorage`
  (client-side, no backend). "★ My list" filters to starred venues; "🔔 Reminders"
  asks for notification permission and fires browser notifications at 7d/1d/1h
  before a starred deadline *while the tab is open* — the `.ics` feed covers
  offline reminders.
- **CSV export** of the current filter selection, and **abstract + full**
  deadlines shown together on each card.

## Running locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Refresh the data snapshot
python fetcher/fetch.py

# Launch the dashboard
streamlit run app.py
```

The dashboard reads `data/conferences.json`. If you skip the fetcher step,
the app will use whatever JSON is already committed to the repo.

## Deployment

The intended setup is two free services:

1. **GitHub Actions** runs `fetcher/fetch.py` on a daily cron
   (see `.github/workflows/fetch.yml`) and commits the updated
   `data/conferences.json` back to the repo.
2. **Streamlit Community Cloud** (https://share.streamlit.io) deploys
   `app.py` from the same repo. Every push (including the daily data
   commit) auto-redeploys.

Steps to deploy:

1. Push this repo to GitHub.
2. Confirm the workflow runs at least once (Actions tab) so
   `data/conferences.json` is populated.
3. Connect the repo on share.streamlit.io and point it at `app.py`.

GitHub Pages alone cannot run Streamlit (it only serves static HTML).
Use Streamlit Cloud, or any Python host (Hugging Face Spaces, Render,
fly.io), as the front end.

## Landing page

`index.html` is a small static front door (logo, a short description, links to the
app and repo). With GitHub Pages enabled at the repo root, it serves at
`https://krimler.github.io/paper-tracker/`. `.nojekyll` makes Pages serve it as-is
and take precedence over this README.

## Editing the tracked conferences

Edit `allowlist.yml`. The fetcher matches the `title` field from ccfddl
case-insensitively. If a name doesn't match, the next fetcher run logs it
under the "unmatched" list visible in the dashboard.

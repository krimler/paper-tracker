# CS Conference Deadlines

A tracker for top-tier CS conference deadlines across security, distributed
systems, networking, systems, databases, software engineering, and AI/ML.

Data source: [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines),
filtered to a curated allowlist of CORE A*/A and otherwise well-known venues.

## Layout

```
allowlist.yml              # curated conferences to track, grouped by area
fetcher/fetch.py           # clones ccfddl, filters by allowlist, writes JSON
data/conferences.json      # generated snapshot (committed daily)
app.py                     # Streamlit dashboard
.github/workflows/fetch.yml  # daily GitHub Actions cron
requirements.txt
```

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

## Editing the tracked conferences

Edit `allowlist.yml`. The fetcher matches the `title` field from ccfddl
case-insensitively. If a name doesn't match, the next fetcher run logs it
under the "unmatched" list visible in the dashboard.

# Stock Shock Tracker

A live-updating tracker for five companies exposed to semiconductor/DRAM
supply shocks — AMD and NVDA (upstream chipmakers) and NTDOY, MSFT, SONY
(downstream console manufacturers). A GitHub Actions job fetches closing
prices on weekdays and commits them back to this repo; the site itself is
a static page hosted on GitHub Pages that reads that data directly.

This is the companion "infrastructure" project to
[`component_shock_stock_impact`](https://github.com/arjunshivpatel/component_shock_stock_impact),
which covers the data-analysis side (event-study methodology on the same
kind of shocks). This project reuses its price-fetching logic but is
about automation, not analysis: a scheduled job, an append-only data
file, and a front end that displays whatever's accumulated so far.

## How it works

1. `.github/workflows/update-prices.yml` runs `scripts/fetch_prices.py`
   on a weekday schedule (and can be triggered manually from the Actions
   tab).
2. The script pulls the last ~10 days of closes via `yfinance`, appends
   any dates not already recorded to `docs/data/prices.json`, and the
   workflow commits the change.
3. `docs/index.html` is a static page (Chart.js) that fetches
   `docs/data/prices.json` and `docs/data/news_tags.json` and renders
   the chart, ticker tape, and event log — no backend involved.
4. GitHub Pages serves straight from `/docs` on `main`, so once new data
   is pushed, the site reflects it on the next Pages build (typically
   within a minute or two).

## Local setup

```bash
git clone <your-repo-url>
cd stock-shock-tracker
pip install -r requirements.txt
python scripts/fetch_prices.py   # seeds/updates docs/data/prices.json
```

To preview the site locally, serve `/docs` rather than opening
`index.html` directly — browsers block `fetch()` on `file://` URLs:

```bash
cd docs
python -m http.server 8000
# then open http://localhost:8000
```

## One-time GitHub setup

1. Push this repo to GitHub under your account.
2. **Settings → Pages** → set source to "Deploy from a branch", branch
   `main`, folder `/docs`.
3. **Settings → Actions → General → Workflow permissions** → set to
   "Read and write permissions" so the scheduled job can commit data
   back to the repo.
4. Optionally run the workflow once by hand (**Actions →
   Update stock prices → Run workflow**) rather than waiting for the
   next scheduled run, so the site has data from day one.

## Adding a tagged event

Edit `docs/data/news_tags.json` and add an entry:

```json
{
  "date": "2026-09-01",
  "headline": "Short headline",
  "note": "A sentence or two of context.",
  "url": "https://source-article-link"
}
```

Tags are added manually and deliberately — automatically classifying
news as "AI-relevant" reliably enough to trust is a harder problem than
this project needs, and a wrong auto-tag would undermine the point of
tracking real events.

## Requirements

```
pandas
yfinance
```

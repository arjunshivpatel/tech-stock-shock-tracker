# Stock Shock Tracker

A live-updating tracker for five companies exposed to supply shocks caused by AI-driven price surges: AMD and NVDA (upstream chipmakers) and NTDOY, MSFT, SONY
(downstream console manufacturers). A GitHub Actions job fetches closing
prices on weekdays and commits them to this repo; the site itself is
a static page hosted on GitHub Pages that reads that data directly.

This is the companion project to
[`component_shock_stock_impact`](https://github.com/arjunshivpatel/component_shock_stock_impact),
which covers the data analysis (event-study methodology on the impact of the AI-driven stock shocks.). This project reuses its price-fetching logic but is
about automation. It is based around a scheduled job, an append-only data
file and a frontend that displays accumulated data.

## How it works

1. `.github/workflows/update-prices.yml` runs `scripts/fetch_prices.py`
   on a weekday schedule (and can be triggered manually from the Actions
   tab).
2. The script pulls the last ~10 days of closes via `yfinance`, appends
   any dates not already recorded to `docs/data/prices.json`, and the
   workflow commits the change.
3. `docs/index.html` is a static page (Chart.js) that fetches
   `docs/data/prices.json` and `docs/data/news_tags.json` and renders
   the chart, ticker tape, and event log.
4. GitHub Pages serves straight from `/docs` on `main`, so once new data
   is pushed, the site reflects it on the next Pages build.


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

Tags are added manually. Automatically classifying
news as AI-relevant reliably enough to trust is a harder problem than
this project needs, and a wrong auto-tag would undermine the point of
tracking real events.

## Requirements

```
pandas
yfinance
```

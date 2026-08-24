import json
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKERS = ["NTDOY", "MSFT", "SONY", "NVDA", "AMD"]
DATA_PATH = Path(__file__).resolve().parent.parent / "docs" / "data" / "prices.json"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5


def load_existing():
    if not DATA_PATH.exists():
        return {"dates": [], "prices": {t: [] for t in TICKERS}}
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    for t in TICKERS:
        data["prices"].setdefault(t, [])
    return data


def fetch_recent_prices(start_date):
    end_date = date.today() + timedelta(days=1)  # yfinance end is exclusive
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            df = yf.download(
                TICKERS,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                progress=False,
            )["Close"]
            if df.empty:
                raise ValueError("yfinance returned an empty DataFrame")
            return df
        except Exception as e:
            last_error = e
            print(f"[attempt {attempt}/{MAX_RETRIES}] fetch failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"Giving up after {MAX_RETRIES} attempts: {last_error}")


def main():
    data = load_existing()
    existing_dates = set(data["dates"])

    # Look back 10 days so we backfill anything missed (e.g. a failed
    # Action run) instead of only ever fetching "today".
    lookback_start = date.today() - timedelta(days=10)
    df = fetch_recent_prices(lookback_start)

    new_rows = 0
    for ts, row in df.iterrows():
        d = ts.date().isoformat()
        if d in existing_dates:
            continue
        if row.isna().any():
            print(f"Skipping {d}: incomplete data for one or more tickers")
            continue
        data["dates"].append(d)
        for t in TICKERS:
            data["prices"][t].append(round(float(row[t]), 2))
        existing_dates.add(d)
        new_rows += 1

    # Keep everything sorted by date in case backfilled rows arrived
    # out of order.
    if new_rows:
        order = sorted(range(len(data["dates"])), key=lambda i: data["dates"][i])
        data["dates"] = [data["dates"][i] for i in order]
        for t in TICKERS:
            data["prices"][t] = [data["prices"][t][i] for i in order]

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Added {new_rows} new day(s). Total days tracked: {len(data['dates'])}")


if __name__ == "__main__":
    main()

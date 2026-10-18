#!/usr/bin/env python3
"""Build the breach stock-impact dataset for the viz.

Event study of public-company cyber incidents: for each incident we estimate a
market model (alpha + beta against a broad index) over a pre-event estimation
window, then measure abnormal returns (AR) and cumulative abnormal returns (CAR)
around the public disclosure date. The average across incidents is the cumulative
average abnormal return (CAAR), the standard event-study summary line.

Public data only:
- Prices from the Yahoo Finance chart API (adjusted close).
- Disclosure dates are public (8-K filings, company statements, press reporting).

No client, target, or engagement data. For education / analysis, not investment
advice. Correlation is not causation; dates are market-reaction dates, not a claim
about the underlying cause of every daily move.

stdlib only. Writes viz/breach-stock-impact/data.json.
"""

import datetime as dt
import json
import os
import time
import urllib.parse
import urllib.request

# --- incidents -------------------------------------------------------------
# name, ticker, sector, public disclosure date (market-reaction reference).
# All dates are public. day0 is resolved to the first trading day >= disclosure.
INCIDENTS = [
    ("Equifax",            "EFX", "Financial data", "2017-09-07"),
    ("Target",             "TGT", "Retail",         "2013-12-19"),
    ("Marriott",           "MAR", "Hospitality",    "2018-11-30"),
    ("Capital One",        "COF", "Banking",        "2019-07-29"),
    ("Progress (MOVEit)",  "PRGS","Software",       "2023-05-31"),
    ("Okta",               "OKTA","Identity",       "2022-03-22"),
    ("MGM Resorts",        "MGM", "Hospitality",    "2023-09-11"),
    ("Clorox",             "CLX", "Consumer goods", "2023-08-14"),
    ("UnitedHealth/Change","UNH", "Healthcare",     "2024-02-22"),
]

BENCHMARK = "^GSPC"          # S&P 500 as the market proxy
EST_START, EST_END = -250, -11   # estimation window (trading days rel. to day0)
PRE, POST = -10, 30              # event window (trading days rel. to day0)

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "viz", "breach-stock-impact", "data.json")


def fetch_prices(ticker, start, end):
    """Return {date: adjusted_close} for [start, end] (date objects)."""
    t = urllib.parse.quote(ticker)
    p1 = int(dt.datetime(start.year, start.month, start.day).timestamp())
    p2 = int(dt.datetime(end.year, end.month, end.day).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{t}"
           f"?period1={p1}&period2={p2}&interval=1d")
    req = urllib.request.Request(
        url, headers={"User-Agent": "agentic-redteam/breach-stock (stdlib)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.loads(r.read().decode("utf-8", "replace"))
    res = j["chart"]["result"][0]
    ts = res["timestamp"]
    adj = (res.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose")
           or res["indicators"]["quote"][0]["close"])
    out = {}
    for t_, c in zip(ts, adj):
        if c is None:
            continue
        out[dt.datetime.utcfromtimestamp(t_).date()] = c
    return out


def daily_returns(series, days):
    """Simple returns keyed by day, aligned to the sorted `days` list."""
    r = {}
    for i in range(1, len(days)):
        d0, d1 = days[i - 1], days[i]
        if series[d0]:
            r[d1] = series[d1] / series[d0] - 1.0
    return r


def ols(xs, ys):
    """Return (alpha, beta) for ys ~ alpha + beta*xs."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    var = sum((x - mx) ** 2 for x in xs)
    beta = cov / var if var else 1.0
    alpha = my - beta * mx
    return alpha, beta


def study_one(name, ticker, sector, disclosure):
    d = dt.date.fromisoformat(disclosure)
    # Wide fetch window: ~400 calendar days before, ~60 after.
    stock = fetch_prices(ticker, d - dt.timedelta(days=430),
                         d + dt.timedelta(days=60))
    mkt = fetch_prices(BENCHMARK, d - dt.timedelta(days=430),
                       d + dt.timedelta(days=60))
    days = sorted(set(stock) & set(mkt))
    rs = daily_returns(stock, days)
    rm = daily_returns(mkt, days)
    trade = sorted(rs)

    # day0 = first trading day >= disclosure
    day0 = next((x for x in trade if x >= d), None)
    if day0 is None:
        raise RuntimeError(f"{ticker}: no trading day on/after {d}")
    i0 = trade.index(day0)

    # estimation window
    est = [trade[i0 + k] for k in range(EST_START, EST_END + 1)
           if 0 <= i0 + k < len(trade)]
    if len(est) < 60:
        raise RuntimeError(f"{ticker}: estimation window too short ({len(est)})")
    alpha, beta = ols([rm[x] for x in est], [rs[x] for x in est])

    # event window: AR and cumulative AR (from window start)
    path = []
    caar = 0.0
    car_marks = {}
    car_from_day0 = 0.0
    for k in range(PRE, POST + 1):
        i = i0 + k
        if not (0 <= i < len(trade)):
            continue
        day = trade[i]
        ar = rs[day] - (alpha + beta * rm[day])
        caar += ar
        if k >= 0:
            car_from_day0 += ar
        if k in (1, 5, 20, 30):
            car_marks[f"d{k}"] = round(car_from_day0 * 100, 2)
        path.append({"d": k, "ar": round(ar * 100, 3),
                     "car": round(caar * 100, 3)})

    return {
        "name": name, "ticker": ticker, "sector": sector,
        "disclosure": disclosure, "day0": day0.isoformat(),
        "beta": round(beta, 2),
        "car": car_marks,
        "path": path,
    }


def main():
    incidents = []
    for name, ticker, sector, disclosure in INCIDENTS:
        print(f"... {ticker} ({disclosure})", flush=True)
        for attempt in range(3):
            try:
                incidents.append(study_one(name, ticker, sector, disclosure))
                break
            except Exception as e:  # noqa: BLE001 - keep building the rest
                print(f"    retry {attempt+1}: {type(e).__name__}: {e}")
                time.sleep(2)
        else:
            print(f"    SKIP {ticker}: failed after retries")

    # cumulative average abnormal return (CAAR): average AR per relative day,
    # then cumulate. Only days present in every incident are averaged.
    by_day = {}
    for inc in incidents:
        for p in inc["path"]:
            by_day.setdefault(p["d"], []).append(p["ar"])
    n = len(incidents)
    avg_path = []
    caar = 0.0
    car_marks = {}
    car_from0 = 0.0
    for k in range(PRE, POST + 1):
        vals = by_day.get(k, [])
        if len(vals) != n:
            continue
        mean_ar = sum(vals) / n
        caar += mean_ar
        if k >= 0:
            car_from0 += mean_ar
        if k in (1, 5, 20, 30):
            car_marks[f"d{k}"] = round(car_from0, 2)
        avg_path.append({"d": k, "ar": round(mean_ar, 3),
                         "caar": round(caar, 3)})

    data = {
        "generatedAt": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "benchmark": BENCHMARK,
        "model": ("market model: AR = R_stock - (alpha + beta * R_market), "
                  f"estimation window [{EST_START},{EST_END}] trading days"),
        "eventWindow": {"pre": PRE, "post": POST},
        "note": ("Public data only. Education / analysis, not investment advice. "
                 "Correlation is not causation."),
        "incidents": incidents,
        "average": {"count": n, "path": avg_path, "car": car_marks},
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"\nwrote {OUT}")
    print(f"incidents={n} "
          f"avgCAR[0,+30]={car_marks.get('d30')}% "
          f"benchmark={BENCHMARK}")


if __name__ == "__main__":
    main()

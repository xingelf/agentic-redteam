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
# name, ticker, sector, public disclosure date, region. All dates are public
# (filings and reporting); day0 is the first trading day >= disclosure. Each
# incident is measured against its home-market benchmark (see BENCHMARKS).
INCIDENTS = [
    # United States (vs S&P 500)
    ("Equifax",            "EFX",   "Financial data", "2017-09-07", "US"),
    ("Target",             "TGT",   "Retail",         "2013-12-19", "US"),
    ("Marriott",           "MAR",   "Hospitality",    "2018-11-30", "US"),
    ("Capital One",        "COF",   "Banking",        "2019-07-29", "US"),
    ("Progress (MOVEit)",  "PRGS",  "Software",       "2023-05-31", "US"),
    ("Okta",               "OKTA",  "Identity",       "2022-03-22", "US"),
    ("MGM Resorts",        "MGM",   "Hospitality",    "2023-09-11", "US"),
    ("Clorox",             "CLX",   "Consumer goods", "2023-08-14", "US"),
    ("UnitedHealth/Change","UNH",   "Healthcare",     "2024-02-22", "US"),
    # Japan (vs Nikkei 225)
    ("Capcom",             "9697.T","Games",          "2020-11-02", "JP"),
    ("KADOKAWA",           "9468.T","Media",          "2024-06-08", "JP"),
    ("Toyota",             "7203.T","Automotive",     "2022-02-28", "JP"),
    ("Honda",              "7267.T","Automotive",     "2020-06-08", "JP"),
    ("Mitsubishi Electric","6503.T","Electronics",    "2020-01-20", "JP"),
    ("Fujitsu",            "6702.T","IT services",    "2021-05-26", "JP"),
    ("Casio",              "6952.T","Electronics",    "2024-10-07", "JP"),
]

BENCHMARKS = {"US": "^GSPC", "JP": "^N225"}  # home-market proxy per region
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


def study_one(name, ticker, sector, disclosure, region):
    d = dt.date.fromisoformat(disclosure)
    benchmark = BENCHMARKS[region]
    # Wide fetch window: ~430 calendar days before, ~60 after.
    stock = fetch_prices(ticker, d - dt.timedelta(days=430),
                         d + dt.timedelta(days=60))
    mkt = fetch_prices(benchmark, d - dt.timedelta(days=430),
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
        "name": name, "ticker": ticker, "sector": sector, "region": region,
        "benchmark": benchmark,
        "disclosure": disclosure, "day0": day0.isoformat(),
        "beta": round(beta, 2),
        "car": car_marks,
        "path": path,
    }


def average(group):
    """CAAR for a list of incidents: mean AR per relative day, then cumulate.
    Only relative days present in every incident of the group are used."""
    by_day = {}
    for inc in group:
        for p in inc["path"]:
            by_day.setdefault(p["d"], []).append(p["ar"])
    n = len(group)
    path, caar, car_from0, marks = [], 0.0, 0.0, {}
    for k in range(PRE, POST + 1):
        vals = by_day.get(k, [])
        if len(vals) != n:
            continue
        mean_ar = sum(vals) / n
        caar += mean_ar
        if k >= 0:
            car_from0 += mean_ar
        if k in (1, 5, 20, 30):
            marks[f"d{k}"] = round(car_from0, 2)
        path.append({"d": k, "ar": round(mean_ar, 3), "caar": round(caar, 3)})
    return {"count": n, "path": path, "car": marks}


def main():
    incidents = []
    for name, ticker, sector, disclosure, region in INCIDENTS:
        print(f"... {ticker} ({region}, {disclosure})", flush=True)
        for attempt in range(3):
            try:
                incidents.append(
                    study_one(name, ticker, sector, disclosure, region))
                break
            except Exception as e:  # noqa: BLE001 - keep building the rest
                print(f"    retry {attempt+1}: {type(e).__name__}: {e}")
                time.sleep(2)
        else:
            print(f"    SKIP {ticker}: failed after retries")

    us = [i for i in incidents if i["region"] == "US"]
    jp = [i for i in incidents if i["region"] == "JP"]
    averages = {"ALL": average(incidents)}
    if us:
        averages["US"] = average(us)
    if jp:
        averages["JP"] = average(jp)

    data = {
        "generatedAt": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "benchmarks": BENCHMARKS,
        "model": ("market model: AR = R_stock - (alpha + beta * R_market), "
                  f"estimation window [{EST_START},{EST_END}] trading days, "
                  "each incident vs its home-market benchmark"),
        "eventWindow": {"pre": PRE, "post": POST},
        "note": ("Public data only. Education / analysis, not investment advice. "
                 "Correlation is not causation."),
        "incidents": incidents,
        "averages": averages,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"\nwrote {OUT}")
    print(f"incidents={len(incidents)} (US={len(us)}, JP={len(jp)})")
    for key in ("ALL", "US", "JP"):
        if key in averages:
            print(f"  {key}: CAR[0,+30]={averages[key]['car'].get('d30')}%")


if __name__ == "__main__":
    main()

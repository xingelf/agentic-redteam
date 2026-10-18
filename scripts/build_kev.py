#!/usr/bin/env python3
"""Build a lightweight data.json for the KEV dashboard from the CISA KEV feed.

Standard library only (no dependencies, no venv). Fetches the public CISA Known
Exploited Vulnerabilities catalog, computes a few aggregates, trims it down, and
writes viz/kev-dashboard/data.json.

Usage:
    python3 scripts/build_kev.py [output_path]

Run locally or from GitHub Actions. Public data only; no secrets.
"""

import json
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

FEED_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
MONTHS_BACK = 18
TOP_VENDORS = 12
RECENT = 40
DESC_MAX = 180

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "viz" / "kev-dashboard" / "data.json"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "agentic-redteam-kev/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def month_key(date_str):
    # dateAdded is "YYYY-MM-DD"
    return date_str[:7] if date_str and len(date_str) >= 7 else None


def last_n_months(n):
    now = datetime.now(timezone.utc)
    keys = []
    y, m = now.year, now.month
    for _ in range(n):
        keys.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(keys))


def build(feed):
    vulns = feed.get("vulnerabilities", [])
    now = datetime.now(timezone.utc)
    this_month = f"{now.year:04d}-{now.month:02d}"
    cutoff_30 = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    month_counts = Counter(month_key(v.get("dateAdded", "")) for v in vulns)
    vendor_counts = Counter(v.get("vendorProject", "Unknown") for v in vulns)

    added_this_month = sum(1 for v in vulns if (v.get("dateAdded", "") or "").startswith(this_month))
    added_30 = sum(1 for v in vulns if (v.get("dateAdded", "") or "") >= cutoff_30)
    ransomware = sum(1 for v in vulns if v.get("knownRansomwareCampaignUse") == "Known")
    forensic = sum(1 for v in vulns if v.get("forensicTriage") == "Yes")

    added_by_month = [{"month": k, "count": month_counts.get(k, 0)} for k in last_n_months(MONTHS_BACK)]
    top_vendors = [{"vendor": name, "count": c} for name, c in vendor_counts.most_common(TOP_VENDORS)]

    recent_sorted = sorted(vulns, key=lambda v: v.get("dateAdded", ""), reverse=True)[:RECENT]
    recent = []
    for v in recent_sorted:
        desc = (v.get("shortDescription", "") or "").strip()
        if len(desc) > DESC_MAX:
            desc = desc[:DESC_MAX].rstrip() + "…"
        recent.append({
            "cveID": v.get("cveID", ""),
            "vendorProject": v.get("vendorProject", ""),
            "product": v.get("product", ""),
            "vulnerabilityName": v.get("vulnerabilityName", ""),
            "dateAdded": v.get("dateAdded", ""),
            "dueDate": v.get("dueDate", ""),
            "knownRansomwareCampaignUse": v.get("knownRansomwareCampaignUse", "Unknown"),
            "shortDescription": desc,
        })

    return {
        "meta": {
            "title": feed.get("title", "CISA Catalog of Known Exploited Vulnerabilities"),
            "catalogVersion": feed.get("catalogVersion", ""),
            "dateReleased": feed.get("dateReleased", ""),
            "generatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "CISA KEV",
            "sourceUrl": FEED_URL,
        },
        "stats": {
            "total": feed.get("count", len(vulns)),
            "addedThisMonth": added_this_month,
            "addedLast30Days": added_30,
            "ransomwareLinked": ransomware,
            "forensicTriageYes": forensic,
        },
        "addedByMonth": added_by_month,
        "topVendors": top_vendors,
        "recent": recent,
    }


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    feed = fetch(FEED_URL)
    data = build(feed)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = data["stats"]
    print(f"Wrote {out}")
    print(f"  total={s['total']} addedThisMonth={s['addedThisMonth']} "
          f"ransomwareLinked={s['ransomwareLinked']} recent={len(data['recent'])} "
          f"catalog={data['meta']['catalogVersion']}")


if __name__ == "__main__":
    main()

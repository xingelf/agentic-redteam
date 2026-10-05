---
title: "SQL Injection: How It Works and How to Stop It"
tags: ["security-basics", "sqli", "web-security", "owasp"]
---

# SQL Injection: How It Works and How to Stop It

**TL;DR** — SQLi is old and well understood, and still everywhere. It is
A03:2021 Injection in the OWASP Top 10 and CWE-89. The dangerous instances today
are rarely on the login form — they hide in export features, `ORDER BY` clauses,
and second-order sinks. Parameterized queries plus allowlisted identifiers
remove almost all of it.

## How it works

SQLi happens when untrusted input is concatenated into a query, so the attacker's
text is parsed as *code* instead of *data*. Once that boundary breaks, an
attacker can bypass authentication, read data they should not, change records,
and in some setups run OS commands.

The classic vulnerable pattern:

```python
# Vulnerable: user input concatenated into SQL
query = f"SELECT * FROM users WHERE username='{user_input}' AND password='{pass_input}'"
```

Supply `' OR '1'='1'-- ` as the username and the query becomes:

```sql
SELECT * FROM users WHERE username='' OR '1'='1'-- ' AND password='...'
```

The `-- ` comments out the password check (the trailing space matters in MySQL;
`#` also works), and `'1'='1'` is always true, so the first row is returned —
usually an admin.

Where it actually shows up: not the textbook login form, but search and filter
parameters, `ORDER BY` clauses (which parameterization often does not cover),
CSV/PDF export functions, REST/GraphQL parameters, and second-order sinks where
stored input is later used in a query.

## Types

### In-band (results come back in the response)

- **Union-based** — extend the result set with your own rows. Find the column
  count with `ORDER BY`, then match types. See the companion post on UNION-based
  SQLi for the full workflow.
- **Error-based** — force the database to leak data inside an error message.
  Engine-specific:

```sql
-- MSSQL
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM INFORMATION_SCHEMA.TABLES))--
-- MySQL
' AND extractvalue(1,concat(0x7e,(SELECT version())))--
```

Error-based only works when the app returns database errors to the client —
which it never should.

### Blind (no data in the response, so you infer it)

- **Boolean-based** — same page for true, different page for false, one character
  at a time. See the companion post for the binary-search technique.
- **Time-based** — when even the body does not change, use delays as the oracle.
  The most engine-dependent variant:

```sql
-- MySQL
' AND IF((SELECT COUNT(*) FROM users)>1000, SLEEP(5), 0)--
-- MSSQL
'; IF (SELECT COUNT(*) FROM users)>1000 WAITFOR DELAY '0:0:5'--
-- PostgreSQL
' AND (SELECT CASE WHEN (SELECT COUNT(*) FROM users)>1000 THEN pg_sleep(5) ELSE pg_sleep(0) END)--
```

### Out-of-band and second-order

- **Out-of-band (OOB)** — when the injection is blind and timing is unreliable,
  exfiltrate over a channel the database controls, such as DNS (`xp_dirtree` on
  MSSQL, `LOAD_FILE`/`INTO OUTFILE` on MySQL where file privileges allow,
  `COPY ... TO PROGRAM` on PostgreSQL).
- **Second-order** — input is stored safely, then used unsafely later by a
  different code path (a password-reset routine, a report builder). Scanners miss
  these; manual review catches them.

## Real-world impact

Documented, attributed breaches — not hypotheticals:

- **Heartland Payment Systems (2008)** — SQLi was the initial foothold in an
  intrusion that exposed roughly 130 million card numbers.
- **Sony Pictures (2011)** — SQLi against sonypictures.com exposed data on
  roughly 1 million accounts, many stored in plaintext.
- **TalkTalk (2015)** — SQLi in legacy pages exposed data on 156,959 customers.
  The UK ICO fined TalkTalk £400,000, calling the flaw well-known and
  preventable.

## Defense

### Parameterized queries — the one that matters

Most SQLi disappears the moment input can never be parsed as code. Bind
parameters everywhere, no exceptions:

```java
// Java (JDBC)
String query = "SELECT * FROM users WHERE email = ?";
PreparedStatement stmt = connection.prepareStatement(query);
stmt.setString(1, userEmail);
```

```python
# Python (DB-API): pass params separately, never f-strings
cur.execute("SELECT * FROM users WHERE email = %s", (user_email,))
```

The gap people miss: parameterization binds *values*, not *identifiers*. Table
names, column names, and `ORDER BY` directions cannot be bound — validate those
against an allowlist. This is where "we use prepared statements everywhere" apps
still get injected.

### Defense in depth

- **ORMs** (Hibernate, Entity Framework, Django ORM, SQLAlchemy) parameterize by
  default. Their raw-query escape hatches are where ORM apps get injected.
- **Least privilege** on the database account: no `DROP`, `FILE`, `xp_cmdshell`,
  or `COPY ... TO PROGRAM`. It caps the blast radius from full compromise to one
  table.
- **Input validation** as a supporting control — allowlist formats, enforce type
  and length. It reduces surface; it does not replace parameterization.
- **WAF** as a speed bump, never the fix — determined attackers bypass signatures
  with encoding and inline comments.

### Detection and response

- Never return raw database errors to users; log detail server-side.
- Watch for abnormally long query strings, bursts of `UNION` attempts, and
  repeated near-identical requests (a blind-SQLi oracle grinding one character at
  a time).
- Centralize app and database logs; alert on error spikes after auth attempts.

## Checklist

1. Parameterize every query — never concatenate input into SQL.
2. Allowlist identifiers — table/column names and `ORDER BY` cannot be bound.
3. Apply least privilege; remove dangerous stored procedures.
4. Suppress database errors to the client.
5. Test continuously — `sqlmap`, Burp, OWASP ZAP in CI, plus manual review for
   second-order sinks.
6. Keep frameworks patched — ORM and driver CVEs reintroduce injection paths.

## Takeaway

SQLi is almost always preventable at the code layer. Parameterized queries plus
allowlisted identifiers eliminate the vast majority; least privilege contains the
rest. The dangerous instance is not the login form — it is the export function,
the `ORDER BY`, and the second-order sink. Test those.

## References

- OWASP SQL Injection Prevention Cheat Sheet
- OWASP Top 10 — A03:2021 Injection
- PortSwigger Web Security Academy — SQL Injection
- MITRE CWE-89

---
title: "SQL Collation, and Why It Matters for Security"
tags: ["security-basics", "database", "sql"]
---

# SQL Collation, and Why It Matters for Security

**TL;DR** — Collation is the rulebook a database uses to compare and sort text:
case sensitivity, accent sensitivity, ordering, and encoding. It is usually filed
under performance and correctness, but it also decides whether `'Admin'` equals
`'admin'` and whether `'café'` equals `'cafe'` — which can turn into auth bypass
and lookup surprises.

## What collation controls

A collation defines, for text data:

- **Case sensitivity** — is `'Apple' = 'apple'`?
- **Accent sensitivity** — is `'café' = 'cafe'`?
- **Sort order** — where does `'Ö'` land (after `'Z'` in German, at the end in
  Swedish)?
- **Encoding** — the character set, e.g. `utf8mb4`.

Reading a collation name:

```
utf8mb4_spanish_ci
```

- `utf8mb4` — character set (full Unicode, including emoji)
- `spanish` — language rules for ordering
- `_ci` — case insensitive

Common suffixes:

| Suffix | Meaning | Example |
|---|---|---|
| `_ci` | Case insensitive | `'A' = 'a'` is true |
| `_cs` | Case sensitive | `'A' = 'a'` is false |
| `_bin` | Binary, byte-by-byte | exact bytes only |

## Where it bites

```sql
-- comparison: a _ci column matches regardless of case
SELECT * FROM users WHERE name = 'JOHN';   -- also returns 'John'

-- sorting: order depends on the collation's language rules
ORDER BY name COLLATE utf8mb4_swedish_ci;

-- uniqueness: a _ci unique index treats these as the same
UNIQUE (email)  -- 'Email@x.com' collides with 'email@x.com'
```

A frequent failure is the `Illegal mix of collations` error when joining columns
with different collations, which also silently kills index usage and slows
queries:

```sql
-- fix: force a common collation on the join
JOIN t2 ON t1.name COLLATE utf8mb4_unicode_ci = t2.name
```

## The security angle

Collation is not just cosmetics — comparisons are a security control:

- **Case-insensitive lookups and auth.** On a `_ci` column, `'Admin'`, `'ADMIN'`,
  and `'admin'` are the same string. If one code path assumes case sensitivity
  (an allowlist check, a "does this username already exist" guard) while the
  database compares case-insensitively, you get account collisions or allowlist
  bypass. Unicode case folding adds edge cases (for example the Turkish dotless
  `ı`).
- **Accent and width folding.** Some collations treat `'café'` and `'cafe'`, or
  full-width and half-width forms, as equal. A uniqueness or blocklist check can be
  bypassed with an equivalent-but-different string.
- **Filter and signature bypass.** Equivalence rules mean a value that your
  comparison treats as "not matching a blocked term" may still match server-side,
  or vice versa.
- **Tokens and secrets.** Session tokens, API keys, and password hashes must be
  compared with exact bytes. Store and compare them with `_bin` (or a binary type),
  never a `_ci` text column, so that case or accent folding cannot make two
  different secrets compare equal. (For passwords themselves, compare the hash, not
  the plaintext.)

## Good defaults

1. Default to a Unicode collation such as `utf8mb4_unicode_ci` for human-readable
   text that needs natural matching.
2. Keep collation consistent across server, database, table, and column to avoid
   mix errors and index loss.
3. Use `_bin` (or binary types) for anything that must match exactly — tokens,
   keys, hashes, case-sensitive identifiers.
4. Make the comparison semantics explicit in security-sensitive checks instead of
   relying on the column default; override per query when needed:

```sql
-- force exact, case-sensitive comparison regardless of column default
WHERE token COLLATE utf8mb4_bin = ?
```

## Inspecting collations

```sql
-- MySQL
SHOW COLLATION;
SHOW FULL COLUMNS FROM users;

-- SQL Server
SELECT name, description FROM sys.fn_helpcollations();
```

## Takeaway

Collation decides what "equal" means for text, and "equal" is a security decision
whenever it guards auth, uniqueness, allowlists, or secret comparison. Use a
Unicode `_ci` collation for normal text, keep it consistent, and switch to binary
comparison for anything where two different values must never be treated as the
same.

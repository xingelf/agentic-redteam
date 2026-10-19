---
title: "Broken Access Control and IDOR"
tags: ["security-basics", "access-control", "idor", "web-security", "owasp"]
---

# Broken Access Control and IDOR

**TL;DR** — Broken access control is the server failing to check that the
authenticated user is *allowed* to do what they asked. It is A01:2021 — the number
one risk in the OWASP Top 10 — and CWE-284/CWE-639. Unlike injection, there is no
clever payload: the attacker just asks for another user's record, or the admin
action, and the server says yes. The fix is a server-side authorization check on
every request, deny by default.

## How it works

Authentication answers "who are you?" Authorization answers "are you allowed to do
this?" Broken access control is a missing or wrong answer to the second question,
even when the first is correct. The classic shape is **IDOR** — an Insecure Direct
Object Reference:

```
GET /api/invoices/1003      ← your invoice
GET /api/invoices/1004      ← someone else's, returned without a check
```

The ID is a direct reference to a database object, and the server returns it based
only on the ID, never checking that *this* user owns invoice 1004. In API terms
this is Broken Object Level Authorization (BOLA), the top risk in the OWASP API
Security Top 10. No injection, no payload — just an incremented number.

## The common shapes

- **IDOR / BOLA** — change an ID in a URL, form field, JSON body, or cookie to
  reach another user's object.
- **Missing function-level authorization** — a regular user calls an admin endpoint
  (`POST /admin/users`) directly; the UI hid the button but the route had no check.
- **Forced browsing** — requesting a URL you were never linked to
  (`/reports/2024/financials.pdf`) that is protected only by being unlisted.
- **Parameter / privilege tampering** — flipping `role=user` to `role=admin`,
  `userId` to someone else's, or `price` in a cart.
- **Method and path tricks** — a check on `GET` but not `PUT`, or bypassed by case
  or path normalization differences.

The underlying mistake is always the same: the server trusts a client-supplied
value (an ID, a role, a path, a hidden field) to decide access instead of deriving
it from the authenticated session.

## Real-world impact

- **First American Financial (2019)** — document links used a sequential ID in the
  URL, and changing it returned other customers' files with no login required. An
  estimated 885 million records — bank account numbers, Social Security numbers,
  mortgage and tax documents, driver's-license images, some dating back to 2003 —
  were reachable this way. It is a textbook IDOR: the object reference was direct,
  and there was no authorization behind it. New York's Department of Financial
  Services opened its first case under the state's new cybersecurity rules over it.

The lesson is the danger of this class: no exploit toolkit is required. A browser
and a `+1` on an ID is the whole attack.

## Defense

### Authorize on the server, on every request — the one that matters

Every request that touches a protected object or action must verify, server-side,
that the current session is permitted — derived from the session, not from input:

```python
# Safe: ownership derived from the authenticated user, not the URL
invoice = db.get_invoice(invoice_id)
if invoice is None or invoice.owner_id != current_user.id:
    abort(404)   # not 403 — don't confirm the object exists
```

- **Deny by default.** Access is forbidden unless a rule allows it; a new endpoint
  is locked until someone grants it, not open until someone remembers to lock it.
- **Check ownership and role on the object**, every time, including non-`GET`
  methods and internal/batch endpoints.
- **Centralize the authorization logic** (middleware, a policy layer, a decorator)
  so a new route cannot silently ship without a check.

### What is *not* a fix

- **Unpredictable IDs (UUIDs) are not authorization.** They raise the cost of
  guessing, but a leaked or shared link still works. Treat opaque IDs as defense in
  depth, never the control.
- **Hiding the UI is not authorization.** The button being absent does not stop a
  direct request to the route.
- **Client-side checks are not authorization.** Anything the browser enforces, the
  attacker removes.

### Supporting controls

- Prefer **indirect references** where practical (map a per-session handle to the
  real ID server-side) so raw database IDs are never exposed.
- **Log and alert** on authorization failures and on one account enumerating many
  object IDs — the signature of an IDOR sweep.
- **Test for it**: access control is hard to catch with scanners. Test every
  endpoint as a different, lower-privileged user and as an unauthenticated one.

## Checklist

1. Authorize every request server-side, derived from the session — deny by default.
2. Check object ownership and role on all methods, not just `GET`.
3. Centralize authorization so new routes can't ship unchecked.
4. Don't rely on UUIDs, hidden UI, or client checks as the control.
5. Return 404, not 403, to avoid confirming objects exist.
6. Test as another user and as an anonymous user; alert on ID enumeration.

## Takeaway

Broken access control is the most common serious web flaw because it is an omission,
not a mistake you can see in a payload — the code simply never asked whether the
user was allowed. The cure is unglamorous and absolute: a server-side,
deny-by-default authorization check on every object and action, written from the
authenticated session and never from client input. An incremented ID should return
404, not someone else's data.

## References

- OWASP Top 10 — A01:2021 Broken Access Control
- OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization
- OWASP Authorization Cheat Sheet
- MITRE CWE-284, CWE-639
- PortSwigger Web Security Academy — Access Control Vulnerabilities

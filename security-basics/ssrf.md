---
title: "Server-Side Request Forgery (SSRF)"
tags: ["security-basics", "ssrf", "web-security", "owasp", "cloud"]
---

# Server-Side Request Forgery (SSRF)

**TL;DR** — SSRF tricks a server into making a request the attacker chooses, from
the server's trusted position inside the network. It is A10:2021 and CWE-918, and
cloud made it far worse: one SSRF often reaches the instance metadata service and
hands out credentials. It also matters more every month, because AI agents that
fetch URLs are SSRF engines by design. The fix is to control the destination, not
the input string.

## How it works

Any feature where the server fetches a URL on the user's behalf is a candidate: a
webhook, a "fetch image from URL," a PDF/screenshot renderer, a link preview, an
import-from-URL, an XML parser resolving external entities (see the XML/XXE note).

```python
# Vulnerable: server fetches whatever URL the user supplies
requests.get(user_supplied_url)
```

The attacker supplies not `https://example.com/logo.png` but a URL pointing
*inward*: `http://localhost:8080/admin`, `http://192.168.0.5/`, or a cloud
metadata address. The server, sitting behind the firewall, reaches things the
attacker never could directly — internal admin panels, databases, other services
on the private network.

## The cloud escalation: instance metadata

On a cloud VM, a link-local address serves metadata and, on older setups, temporary
credentials for the instance's role:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role>
```

If the app will fetch an attacker-controlled URL, the attacker points it here,
reads the role's temporary keys, and then acts as that role. This turns a
read-a-URL bug into cloud account access.

**Capital One (2019)** is the canonical case: an attacker reached the EC2 instance
metadata service (IMDSv1), obtained temporary IAM credentials, and used their
`s3:GetObject` reach to exfiltrate over 100 million credit-card applications.
AWS characterized the entry as a misconfigured WAF acting as an open reverse proxy;
it is widely taught as SSRF. Either way the lesson is the same — the metadata
service answered an unauthenticated request it never should have, and the role was
over-permissioned. IMDSv2, which requires a session token obtained with a `PUT`,
exists specifically to break this chain.

## Blind SSRF

Often the response is not returned to the attacker. It is still useful: port scan
the internal network by timing, hit a state-changing internal endpoint, or
exfiltrate over an out-of-band channel (a DNS lookup or HTTP callback to a server
the attacker controls confirms the request fired).

## Why agents make this worse

An AI agent with a "browse this URL" or "call this API" tool *is* a
server-side fetcher with the agent's network position and credentials. Feed it a
page or a task that names an internal URL and it may dutifully fetch it — SSRF by
instruction. Treat an agent's outbound-fetch tool exactly like any SSRF sink: it
needs the same destination allowlist and metadata-endpoint block. (See the post on
agent tools and the trust boundary.)

## Defense

### Control the destination, not the input

Blocklists of "bad" strings lose to encoding, redirects, DNS tricks, and IPv6. Work
from an allowlist of destinations instead:

1. **Allowlist** the exact hosts/domains the feature may reach; reject everything
   else. This is the single most effective control.
2. **Resolve then validate** the IP, and reject private, loopback, and link-local
   ranges (`127.0.0.0/8`, `10/8`, `172.16/12`, `192.168/16`, `169.254/16`, `::1`,
   fc00::/7). Re-check *after* DNS resolution to defeat rebinding, and pin the
   connection to the validated IP.
3. **Disable redirect following**, or re-validate the target on every redirect — a
   `302` to `169.254.169.254` bypasses a front-door check.
4. **Do not return the raw response** to the user; it leaks internal content and
   enables data theft.

### Network and platform controls

- **Enforce IMDSv2** and set the hop limit to 1 so a proxied request cannot reach
  it; scope instance roles to least privilege so a leak is contained.
- **Egress firewall**: the fetching service should only be allowed to reach the
  destinations it actually needs, not the whole internal network.
- Isolate the fetcher (separate subnet/identity) from sensitive internal services.

## Checklist

1. Allowlist destinations; reject by default.
2. Resolve and validate the IP against private/loopback/link-local ranges, after
   DNS, pinned to the connection.
3. Disable or re-validate redirects.
4. Never echo the fetched response back to the user.
5. Enforce IMDSv2 (hop limit 1) and least-privilege instance roles.
6. Restrict egress; treat agent fetch tools as SSRF sinks.

## Takeaway

SSRF is a confused-deputy bug: the server has access the attacker does not, and the
attacker borrows it. Validating the input string loses; controlling the destination
with an allowlist, blocking the metadata endpoint, and enforcing IMDSv2 wins. As
more systems hand a URL-fetching tool to an autonomous agent, SSRF stops being a
niche web bug and becomes a default-on risk.

## References

- OWASP Server Side Request Forgery Prevention Cheat Sheet
- OWASP Top 10 — A10:2021 Server-Side Request Forgery
- MITRE CWE-918
- AWS — Instance Metadata Service Version 2 (IMDSv2)
- PortSwigger Web Security Academy — SSRF

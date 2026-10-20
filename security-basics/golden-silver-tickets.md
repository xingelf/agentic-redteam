---
title: "Golden and Silver Tickets"
tags: ["security-basics", "active-directory", "kerberos", "persistence"]
---

# Golden and Silver Tickets

**TL;DR** — If an attacker steals the right key, they can *forge* Kerberos tickets
instead of requesting them. A **Golden Ticket** is a forged TGT made with the
`krbtgt` key — it lets you be anyone, in any group, for as long as you like. A
**Silver Ticket** is a forged service ticket made with a single service account's
key — narrower, but quieter, because it never contacts a domain controller. Both
are persistence and impersonation, not initial access; they require you already
hold the key. Read the Kerberos note first.

## Golden Ticket

Every TGT in the domain is encrypted and signed with the **`krbtgt`** account's
key. A domain controller trusts any TGT it can decrypt — it does not check that the
TGT was ever legitimately issued. So an attacker with the `krbtgt` hash can mint a
TGT from scratch, with:

- any username (even one that does not exist),
- any group membership in the PAC (Domain Admins, Enterprise Admins),
- an arbitrary lifetime.

```
# forge a TGT from the krbtgt hash (illustrative, Mimikatz)
kerberos::golden /user:anything /domain:corp.local /sid:<domainSID> /krbtgt:<hash> /ptt
```

That is effectively a skeleton key to the domain, and it survives most clean-ups:
resetting user passwords does nothing, because the forgery depends only on
`krbtgt`. Getting the `krbtgt` hash in the first place generally means you already
reached domain dominance (DCSync or a DC compromise) — the Golden Ticket is how an
attacker *keeps* it.

## Silver Ticket

A service ticket (TGS) is encrypted with the **target service account's** key, and
the service validates the ticket locally — it does not call the KDC. So an attacker
with a service account's hash (or a computer account's hash, for CIFS/HOST/etc.)
can forge a TGS for just that service:

```
# forge a service ticket for one SPN (illustrative, Mimikatz)
kerberos::golden /user:administrator /domain:corp.local /sid:<SID> /target:host01.corp.local /service:cifs /rc4:<serviceHash> /ptt
```

It is scoped to one service on one host, but it is **stealthier** than a Golden
Ticket: no TGT request and no DC interaction, so the usual KDC logs never see it.
Silver Tickets are a favourite for quiet, targeted persistence.

## Modern variants

Defenders learned to flag forged tickets with impossible field values, so attackers
moved to **Diamond** and **Sapphire** tickets, which modify a *real* TGT (or request
one for a privileged user via S4U) rather than building one from nothing, so the
ticket's fields look legitimate. Same root cause — the stolen `krbtgt` key — but
harder to spot on field anomalies alone.

## Detection and defense

- **Guard `krbtgt` like the master key it is.** If you suspect compromise, reset the
  `krbtgt` password **twice**, allowing replication between the resets — a single
  reset leaves the old key valid, and both are needed to invalidate existing Golden
  Tickets.
- **Reduce the odds of key theft.** DCSync rights and DC admin are the paths to
  `krbtgt`; see the ACL and Pass-the-Hash notes. Protect DCs and LSASS.
- **Service-account hygiene** limits Silver Tickets: long/gMSA passwords, AES-only
  (RC4 Silver Tickets are easier to forge), and least privilege on service accounts.
- **Hunt ticket anomalies.** Tickets with very long lifetimes, mismatched
  encryption types, accounts that don't exist, or a TGT whose account/PAC disagrees
  with the directory. Event 4769 without a preceding 4768 can indicate a Silver
  Ticket; enable PAC validation where feasible.
- **Assume-breach rotation.** Periodic `krbtgt` rotation (correctly, twice) caps how
  long any undiscovered Golden Ticket stays valid.

## Takeaway

Golden and Silver Tickets are the difference between stealing access and *keeping*
it. They are not a way in — they require a key you could only get near the top of
the kill chain — but once an attacker holds `krbtgt`, password resets won't evict
them; only the double `krbtgt` rotation will. Treat `krbtgt` and service-account
keys as crown jewels, and watch for tickets whose fields do not match reality.

## References

- Microsoft — "Mitigating Pass-the-Hash" and krbtgt reset guidance
- The Hacker Recipes — Golden ticket, Silver ticket, Diamond/Sapphire tickets
- MITRE ATT&CK — T1558.001 (Golden Ticket), T1558.002 (Silver Ticket)
- Microsoft / Semperis — krbtgt account reset tooling and guidance

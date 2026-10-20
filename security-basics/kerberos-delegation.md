---
title: "Kerberos Delegation Abuse"
tags: ["security-basics", "active-directory", "kerberos", "privilege-escalation"]
---

# Kerberos Delegation Abuse

**TL;DR** — Delegation lets a service act *on behalf of* a user to reach a second
service — the classic "web server needs to query the database as you" problem.
There are three kinds, and each has an abuse path. **Unconstrained** delegation is
the worst (it hoards full TGTs and can hand an attacker Domain Admin).
**Constrained** and **resource-based constrained** delegation (RBCD) are narrower
but still routinely turn a foothold into local admin on a target. Read the Kerberos
note first.

## Unconstrained delegation

A host trusted for unconstrained delegation receives a *copy of the full TGT* of
any user who authenticates to it, and caches it so it can impersonate that user
anywhere. If an attacker controls such a host, they wait for — or **coerce** — a
privileged account to authenticate to it, then lift that TGT:

- Compromise a server marked for unconstrained delegation.
- Coerce a domain controller's computer account to authenticate to it (e.g., the
  printer bug / `MS-RPRN`, or `PetitPotam` — see the coercion note).
- Capture the DC's TGT and use it (Pass-the-Ticket) → full domain compromise.

This is why unconstrained delegation on anything an attacker can reach is a
five-alarm misconfiguration.

## Constrained delegation

Here an account is allowed to delegate only to **specific services** (an SPN
allowlist), using the S4U extensions:

- **S4U2Self** — the service gets a ticket to itself *as* an arbitrary user.
- **S4U2Proxy** — it uses that to get a ticket to the allowed back-end service as
  that user.

If an attacker compromises an account configured for constrained delegation —
especially one with **protocol transition** (`TrustedToAuthForDelegation`) — they
can impersonate *any* user (including Domain Admins) to the allowed services. Worse,
the restriction is on the *service name*, not the host, so it is often possible to
swap the SPN for a more useful service on the same account (e.g. from one SPN to
`CIFS` or `HOST`).

```
# impersonate a user to an allowed service (illustrative, Rubeus)
Rubeus.exe s4u /user:svc_web /rc4:<hash> /impersonateuser:administrator /msdsspn:cifs/db01.corp.local /ptt
```

## Resource-based constrained delegation (RBCD)

RBCD flips the configuration: the **target** decides who may delegate to it, via its
`msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. The abuse is a common modern
escalation:

1. Get write access to a target computer's object (via a dangerous ACL — see the
   ACL note — or because you can create a computer account, since
   `MachineAccountQuota` defaults to **10** for every user).
2. Create or control a computer account and set it in the target's
   `msDS-AllowedToActOnBehalfOfOtherIdentity`.
3. Use S4U to impersonate any user (e.g. a domain admin) *to that target* → local
   admin / code execution on it.

## Detection and defense

- **Eliminate unconstrained delegation** wherever possible; if a host truly needs
  it, isolate it and treat it as Tier 0. Domain controllers should be the only
  objects anywhere near it.
- **Protect privileged accounts from delegation.** Mark admins *"Account is
  sensitive and cannot be delegated"* and/or add them to **Protected Users** — their
  tickets then cannot be delegated at all, defeating the impersonation step.
- **Lock down RBCD inputs.** Set **`MachineAccountQuota` to 0** so ordinary users
  cannot add computer accounts, and tightly control write access to computer
  objects (`GenericWrite`, `WriteProperty` on the delegation attribute).
- **Audit delegation settings** regularly (`userAccountControl` flags,
  `msDS-AllowedToDelegateTo`, `msDS-AllowedToActOnBehalfOfOtherIdentity`);
  BloodHound surfaces these paths.
- **Watch for coercion + S4U**: unexpected machine-authentication to a delegation
  host, or S4U2Self/S4U2Proxy for privileged users, are strong signals.

## Takeaway

Delegation is a legitimate feature for multi-tier apps, but each form trades
convenience for impersonation power. Unconstrained delegation plus authentication
coercion is a direct line to Domain Admin; constrained and RBCD turn object-write
access into local admin on a target. Audit delegation flags, set
`MachineAccountQuota` to 0, and put your privileged accounts beyond delegation with
Protected Users.

## References

- harmj0y — "S4U2Pwnage" and the constrained-delegation series
- Elad Shamir — "Wagging the Dog" (resource-based constrained delegation)
- The Hacker Recipes — Kerberos delegations
- MITRE ATT&CK — T1558, T1134 (access token / delegation abuse)

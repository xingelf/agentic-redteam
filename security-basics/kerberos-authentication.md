---
title: "Kerberos Authentication, Explained for Attackers"
tags: ["security-basics", "active-directory", "kerberos", "windows"]
---

# Kerberos Authentication, Explained for Attackers

**TL;DR** — Kerberos is how Active Directory proves who you are without sending a
password around. It is a three-party ticket system: you prove yourself to a Key
Distribution Center once, get a ticket-granting ticket (TGT), and then trade that
for service tickets. Almost every AD attack with a name — Kerberoasting, Golden
Tickets, delegation abuse — is an attack on one specific step of this dance. Learn
the steps once and the attacks stop being magic.

## The three-party dance

The Key Distribution Center (KDC) runs on every domain controller. Authentication
happens in three exchanges:

1. **AS-REQ / AS-REP (you ↔ KDC).** You prove your identity by encrypting a
   timestamp with your own key (derived from your password hash) — this is
   *pre-authentication*. The KDC replies with a **TGT**, encrypted with the
   `krbtgt` account's key so only the KDC can read it, plus a session key for you.
2. **TGS-REQ / TGS-REP (you ↔ KDC).** You present the TGT and ask for a ticket to a
   specific service, named by its **Service Principal Name (SPN)**, e.g.
   `MSSQLSvc/db01.corp.local`. The KDC returns a **service ticket (TGS)**,
   encrypted with the *service account's* key.
3. **AP-REQ (you ↔ service).** You present the service ticket to the service. The
   service decrypts it with its own key, reads who you are, and grants access. It
   never has to call the KDC.

## The pieces that matter

- **Keys are password hashes.** Your "key" is derived from your password (RC4 is
  literally the NT hash; AES keys are derived from the password + salt). This is
  why an attacker with your *hash* can act as you without your *password*.
- **`krbtgt`.** One hidden account whose key encrypts every TGT in the domain.
  Steal its hash and you can forge any TGT — that is a Golden Ticket.
- **Service accounts and SPNs.** Any service ticket is encrypted with the service
  account's key, so a crackable service-account password is a crackable ticket —
  that is Kerberoasting.
- **The PAC.** Inside the ticket, the Privilege Attribute Certificate lists your
  groups and SIDs. The service trusts it to decide access, which is why forged
  tickets can claim Domain Admin.

## Why an attacker cares about each step

| Step / object | Attack it enables |
|---|---|
| Pre-auth disabled on an account | AS-REP Roasting |
| Service ticket encrypted with account key | Kerberoasting |
| `krbtgt` key | Golden Ticket (forge any TGT) |
| Service account key | Silver Ticket (forge a TGS) |
| TGT/TGS in memory | Pass-the-Ticket |
| Delegation settings | Unconstrained / constrained / RBCD abuse |

Each of these has its own note; this one is the map they all hang on.

## Kerberos vs NTLM

AD still supports the older NTLM challenge-response protocol as a fallback (used
when you connect by IP, to a host without an SPN, or across certain trusts). NTLM
is weaker and enables Pass-the-Hash and relay attacks (see those notes). Kerberos
is preferred; disabling NTLM where possible removes a whole class of attacks.

## Detection and defense

- **Watch the KDC event stream** on domain controllers: 4768 (TGT requested), 4769
  (service ticket requested), 4771 (pre-auth failed), 4770 (ticket renewed).
- **Flag weak encryption.** Service tickets requested with RC4 (etype 0x17) when
  the domain supports AES are a Kerberoasting signal; push AES-only and remove RC4.
- **Protect `krbtgt`.** Treat it as the domain's master key; rotate it (twice, with
  replication between resets) and alert on anomalous TGT lifetimes.
- **Harden accounts.** Require pre-authentication, give service accounts long random
  passwords (prefer group Managed Service Accounts), and remove unnecessary SPNs.
- **Enforce time.** Kerberos relies on clock sync (default 5-minute skew); large
  skew or replayed timestamps are worth monitoring.

## Takeaway

Kerberos is a ticket economy: prove yourself once to the KDC, then spend tickets at
services that trust the KDC's signature. The attacks all come from the same few
facts — keys are password hashes, `krbtgt` signs every TGT, services trust the PAC
inside a ticket. Hold those four facts and the rest of the AD attack catalog reads
like a checklist of which step to abuse.

## References

- MIT Kerberos — The Kerberos Protocol
- Microsoft — Kerberos Authentication Overview
- harmj0y — "Kerberoasting Without Mimikatz" and the Kerberos attack series
- The Hacker Recipes — Active Directory / Kerberos

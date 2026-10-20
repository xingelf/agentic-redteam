---
title: "Kerberoasting and AS-REP Roasting"
tags: ["security-basics", "active-directory", "kerberos", "credential-access"]
---

# Kerberoasting and AS-REP Roasting

**TL;DR** — Two offline password attacks that any authenticated (or even
unauthenticated) domain user can start, because they abuse Kerberos working exactly
as designed. **Kerberoasting** gets you a service account's password hash in a
crackable form; **AS-REP Roasting** does the same for accounts that don't require
pre-authentication. Neither touches the target account or trips a lockout — the
cracking happens on your own machine. The fix is long, random passwords and AES.
Read the Kerberos note first; these map directly onto its steps.

## Kerberoasting

When you request a service ticket (TGS) for a Service Principal Name, the KDC
encrypts part of that ticket with the **service account's key** — derived from its
password. The KDC hands it to *any* domain user who asks; it does not check whether
you can actually use the service. So you:

1. Enumerate accounts that have an SPN (these are service accounts).
2. Request a TGS for each SPN.
3. Take the encrypted ticket offline and crack it to recover the account password.

```
# request roastable tickets (illustrative, Impacket)
GetUserSPNs.py corp.local/lowpriv:password -request
# crack offline
hashcat -m 13100 tickets.txt wordlist.txt
```

Why it is dangerous: service accounts are often old, have human-set passwords, and
are over-privileged (sometimes Domain Admin). RC4-encrypted tickets (hashcat mode
13100) crack faster than AES, and legacy service accounts frequently still allow
RC4.

## AS-REP Roasting

Normally the first Kerberos exchange requires **pre-authentication**: you encrypt a
timestamp with your key to prove you know the password before the KDC responds. If
an account has *"Do not require Kerberos pre-authentication"* set, the KDC will
return an AS-REP to anyone who asks — and part of that reply is encrypted with the
account's key:

```
# find and roast pre-auth-disabled accounts (illustrative, Impacket)
GetNPUsers.py corp.local/ -usersfile users.txt -no-pass
# crack offline
hashcat -m 18200 asrep.txt wordlist.txt
```

This needs no valid credentials if you can name the accounts, which makes it a
classic early-access attack. The flag is sometimes set on old or app accounts that
could not do pre-auth.

## Why these work at all

Both are "features": the KDC encrypting ticket material with an account's key is how
Kerberos lets services and clients verify each other. The weakness is entirely in
the account's password strength, because the attacker gets unlimited offline
guesses against the resulting hash — no lockout, no noise at the account.

## Detection and defense

- **Long, random passwords.** A 25+ character random service-account password is
  effectively uncrackable. Prefer **group Managed Service Accounts (gMSA)**, which
  use 120-character machine-managed passwords.
- **Kill RC4.** Configure accounts and the domain for AES-only; RC4 tickets are the
  cheap-to-crack case and also a detection signal.
- **Prune SPNs.** Remove SPNs from accounts that don't need them; the fewer
  roastable accounts, the smaller the surface.
- **Require pre-authentication** on every account; audit for the "do not require"
  flag and clear it.
- **Detect the request pattern.** Event 4769 (service ticket requested) in bulk,
  especially with RC4 (etype 0x17) from one principal across many SPNs, is the
  Kerberoasting signature. A honeypot service account with an SPN and no real use
  makes a clean tripwire.
- **Least privilege.** A roasted account you cannot escalate from is a contained
  problem; keep service accounts out of privileged groups.

## Takeaway

Kerberoasting and AS-REP Roasting turn any foothold into an offline password-cracking
job against your directory, quietly and without lockouts. You cannot patch the
mechanism — it is Kerberos behaving normally — so you defeat it by removing the
thing it relies on: weak passwords and RC4. gMSA plus AES-only plus pruned SPNs
takes both attacks off the table.

## References

- harmj0y — "Kerberoasting Without Mimikatz"
- The Hacker Recipes — Kerberoasting, AS-REP Roasting
- MITRE ATT&CK — T1558.003 (Kerberoasting), T1558.004 (AS-REP Roasting)
- Microsoft — Group Managed Service Accounts overview

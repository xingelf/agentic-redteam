---
title: "Pass-the-Hash, Pass-the-Ticket, and Overpass-the-Hash"
tags: ["security-basics", "active-directory", "credential-access", "lateral-movement"]
---

# Pass-the-Hash, Pass-the-Ticket, and Overpass-the-Hash

**TL;DR** — You usually do not need a plaintext password to move through a Windows
network — the *credential material* authenticates on its own. An NTLM hash is
enough for NTLM auth (**Pass-the-Hash**); a stolen Kerberos ticket is enough for
Kerberos (**Pass-the-Ticket**); and a hash or key can be converted into a fresh
Kerberos TGT (**Overpass-the-Hash**). All three are credential *reuse*, not
cracking. The defenses are about keeping that material out of reach and limiting
where any one credential works.

## Pass-the-Hash (PtH)

NTLM authentication is a challenge-response built on the account's **NT hash**, and
the protocol never needs the plaintext — the hash *is* the secret. So an attacker
who dumps an NT hash can authenticate as that user to any NTLM-accepting service:

```
# authenticate with a hash instead of a password (illustrative, Impacket)
psexec.py -hashes :<NThash> corp.local/administrator@host01
```

This is why "we never store plaintext, only hashes" is not, by itself, protection:
the hash is a password-equivalent for NTLM.

## Pass-the-Ticket (PtT)

Kerberos tickets live in memory (LSASS) and can be exported and re-injected into a
different session. Steal a user's TGT and you are that user until it expires; steal
a service ticket (TGS) and you reach that one service:

```
# export tickets, then inject one into the current session (illustrative, Rubeus)
Rubeus.exe dump
Rubeus.exe ptt /ticket:<base64-ticket>
```

PtT is often cleaner than PtH because it rides the preferred protocol and leaves a
normal-looking Kerberos trail.

## Overpass-the-Hash (Pass-the-Key)

The bridge between the two: use an NT hash or AES key to perform the first Kerberos
exchange and obtain a brand-new TGT. Now you have a legitimate ticket derived from
stolen key material, and you can use Kerberos everywhere instead of noisier NTLM:

```
# turn a hash into a TGT (illustrative, Rubeus)
Rubeus.exe asktgt /user:svc_sql /rc4:<NThash>
```

## Where the material comes from

- **LSASS memory** on a machine you have admin on (local creds, cached tickets).
- **The local SAM** (local account hashes) and **LSA secrets**.
- **NTDS.dit / DCSync** on a domain controller (every account's hash — see the
  Golden Ticket and ACL notes).

Get a hash once, reuse it across every host where that account is a local admin —
that reuse is how one workstation becomes the whole domain.

## Detection and defense

- **Protect credential material in memory.** Enable **Credential Guard**, run LSASS
  as a protected process (PPL/RunAsPPL), and keep EDR watching LSASS access.
- **Stop local-admin reuse.** This is the single biggest win: unique local admin
  passwords with **LAPS**, so one dumped hash does not open every box.
- **Tier your admins.** Never log a Domain Admin on to a workstation — its
  credentials end up cached there for the next attacker. Use a clean
  admin-tier/PAW model.
- **Shrink NTLM.** Prefer Kerberos; audit and then restrict NTLM where you can, to
  remove PtH targets entirely.
- **Use the Protected Users group** for admins (no NTLM, no RC4, no delegation, no
  long-lived tickets) and **Restricted Admin** mode for RDP so credentials are not
  left on the remote host.
- **Hunt the pattern.** One account authenticating to many hosts in a short window,
  NTLM where you expect Kerberos, or logons from unusual source hosts.

## Takeaway

Hashes and tickets are bearer tokens: whoever holds them is the user, no password
required. You will not stop the technique by rotating one password — you stop it by
keeping the material out of memory (Credential Guard), killing local-admin reuse
(LAPS), tiering admin logons so high-value credentials never land on low-value
hosts, and reducing NTLM. Contain where a credential works and a single theft stops
being a domain takeover.

## References

- Microsoft — "Mitigating Pass-the-Hash and Other Credential Theft"
- The Hacker Recipes — Pass-the-hash, Pass-the-ticket, Overpass-the-hash
- MITRE ATT&CK — T1550.002 (Pass the Hash), T1550.003 (Pass the Ticket)
- Microsoft — Credential Guard, LAPS, Protected Users

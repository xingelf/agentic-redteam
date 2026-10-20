---
title: "NTLM Coercion and Relay"
tags: ["security-basics", "active-directory", "ntlm", "lateral-movement"]
---

# NTLM Coercion and Relay

**TL;DR** — Windows will happily authenticate to the wrong place. **Poisoning**
broadcast name lookups makes victims send their NTLM authentication to you;
**coercion** forces a chosen machine (even a domain controller) to authenticate to
you on demand; and **relaying** forwards that authentication to a *third* service
to act as the victim. Chain coercion into a relay to LDAP or AD CS and you can take
over a domain controller without cracking anything. The fixes are signing, channel
binding, and turning NTLM off.

## Poisoning: Responder

When a Windows host fails to resolve a name over DNS, it falls back to broadcast
protocols — **LLMNR**, **NBT-NS**, and **mDNS** — asking the whole subnet "who is
`fileserve01`?" **Responder** answers "me," the victim connects and sends a
**NetNTLM** challenge-response, and now you have either something to crack offline
or something to relay:

```
# answer broadcast name queries and capture NetNTLM (illustrative)
responder -I eth0
```

A typo'd share name or a stale drive mapping is enough to feed this all day.

## Coercion: make a DC authenticate to you

You do not have to wait for a victim. Several RPC methods will make a remote machine
authenticate to an attacker-chosen host:

- **MS-RPRN "PrinterBug"** — the print spooler's `RpcRemoteFindFirstPrinterChangeNotification`.
- **PetitPotam (MS-EFSRPC)** — the Encrypting File System remote protocol.
- **DFSCoerce (MS-DFSNM)**, and others (the `Coercer` tool bundles them).

Point one of these at a domain controller and it will send its *machine account*
authentication to you. That machine account is powerful — which is the whole point
of relaying it.

## Relay: use the authentication elsewhere

NTLM authentication is not bound to the service it was meant for, so **ntlmrelayx**
forwards it to another service and acts as the victim there:

- **Relay to SMB** on a host without SMB signing → run code as the victim.
- **Relay to LDAP/LDAPS** on a DC → write `msDS-AllowedToActOnBehalfOfOtherIdentity`
  (set up **RBCD**, see the delegation note) or add shadow credentials → take over
  the target.
- **Relay to AD CS web enrollment (HTTP)** → request a certificate as the coerced
  machine. This is **ESC8** (see the AD CS note); relay a DC's auth and you get a
  certificate that authenticates *as the DC* — full compromise.

Coercion + relay-to-AD-CS is one of the most reliable modern "DC takeover from an
unprivileged foothold" chains.

## Detection and defense

- **Disable the poisoning protocols.** Turn off **LLMNR**, **NBT-NS**, and **mDNS**
  via GPO/DHCP; fix the DNS problems that trigger the fallback. This kills Responder.
- **Require SMB signing** everywhere (now enabled by default on current Windows) so
  SMB relays fail.
- **Harden LDAP.** Enforce **LDAP signing** and **channel binding (EPA)** on domain
  controllers so LDAP/LDAPS relays fail.
- **Protect AD CS enrollment.** Disable HTTP web enrollment if unused, require
  HTTPS, and enable **Extended Protection for Authentication (EPA)** on the
  enrollment endpoints to stop ESC8 relays.
- **Patch and block coercion vectors** (PrinterBug, PetitPotam); disable the Print
  Spooler on servers that do not need it; filter the relevant RPC where possible.
- **Reduce NTLM.** Audit NTLM usage, then restrict it with Group Policy; Kerberos
  does not relay the same way. Add admins to **Protected Users** (no NTLM).
- **Detect** multiple identical NetNTLM responses to one host, authentications to a
  host that offers no real service, and machine accounts authenticating to
  unexpected destinations.

## Takeaway

This family works because Windows authenticates eagerly and NTLM is not tied to its
intended destination. You rarely need to crack anything: coerce a DC, relay its
machine authentication to LDAP or AD CS, and the domain is yours. Close it by
signing and channel-binding SMB and LDAP, protecting AD CS enrollment with EPA,
killing LLMNR/NBT-NS/mDNS, and shrinking NTLM until there is nothing left to relay.

## References

- The Hacker Recipes — NTLM relay, MITM & coercion
- Microsoft — SMB signing, LDAP channel binding and signing requirements
- Microsoft — ADV210003 / KB5005413 (PetitPotam / AD CS relay mitigations)
- MITRE ATT&CK — T1557.001 (LLMNR/NBT-NS Poisoning and SMB Relay)

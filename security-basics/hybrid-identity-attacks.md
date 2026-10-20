---
title: "Hybrid Identity Attacks"
tags: ["security-basics", "entra-id", "active-directory", "cloud", "identity"]
---

# Hybrid Identity Attacks

**TL;DR** — Most organisations run *both* on-prem Active Directory and Entra ID,
bridged by **Entra Connect** (formerly Azure AD Connect) and one of a few sign-in
methods. Those bridges are trust that runs in both directions: compromise on-prem
and you can forge your way into the cloud (**Golden SAML**, Seamless SSO); compromise
the sync server and you can reach both directories at once. The bridge components
are Tier 0. Treat them that way or the two environments become one blast radius.

## The bridge is the target

**Entra Connect** synchronises identities from AD to Entra ID. The sync server holds
two very powerful accounts: an on-prem **`MSOL_`/ADSync** account that (with Password
Hash Sync) effectively has **DCSync-equivalent** rights in AD, and a privileged
**connector** account in Entra. So the Connect server is a Tier 0 asset: own it and
you can pull on-prem hashes *and* act privileged in the cloud. Tools like
**AADInternals** can extract the stored Connect credentials from it.

## On-prem → cloud

### Golden SAML (federated setups)

If the tenant federates authentication to **AD FS**, Entra trusts SAML tokens signed
by the AD FS **token-signing certificate**. Steal that certificate and you can forge
SAML tokens for **any user**, with MFA claims already asserted, into any federated
service — Entra, Microsoft 365, and more. It is the cloud's Golden Ticket: it
bypasses MFA and survives password resets, and it was part of the SolarWinds
(SUNBURST) intrusions.

### Rogue federation / trusted-domain backdoor

An attacker with tenant-admin can **add a federated domain** (or modify federation
settings) so that a signing key *they* control is trusted. AADInternals'
`ConvertTo-AADIntBackdoor` is the classic demonstration — afterwards they mint valid
tokens for users at will.

### Seamless SSO abuse

Seamless SSO creates a computer account **`AZUREADSSOACC$`** in on-prem AD. Its
Kerberos key signs tickets for the SSO endpoint, so an attacker who extracts that
key can forge a **Silver-Ticket-style** Kerberos ticket and impersonate any synced
user to Entra. The `AZUREADSSOACC$` password is frequently never rotated.

### Pass-through Authentication (PTA) agent abuse

With PTA, a lightweight agent validates passwords against on-prem AD. A malicious
agent — or code injected into one — can **harvest plaintext credentials** as users
sign in, or authenticate arbitrary users. The agent host is Tier 0 too.

## Cloud → on-prem

The sync account and **write-back** features (password write-back, group/device
write-back) mean cloud compromise can reach back into AD. A compromised Connect
server or a highly privileged cloud role is not "only cloud" — it is a path home to
the domain.

## Detection and defense

- **Tier 0 the bridge.** Entra Connect, AD FS, and PTA agent hosts get
  domain-controller-grade protection, isolation, and admin hygiene.
- **Protect the AD FS token-signing key** (HSM where possible), rotate it on
  suspicion, and monitor AD FS issuance (event **307** and sign-ins with
  unusual/forged claims) for Golden SAML.
- **Lock down federation.** Alert on **new or changed federated domains / trust
  settings** in Entra — these are rare, high-signal events.
- **Rotate `AZUREADSSOACC$`** on a schedule, like any Kerberos service key.
- **Prefer cloud authentication.** Password Hash Sync (ideally with cloud-managed
  auth) removes the AD FS attack surface; where you keep federation, minimise and
  monitor it.
- **Least privilege the sync account**, restrict who can administer Connect, and
  monitor it for DCSync-like replication activity.
- **Join the monitoring.** Correlate on-prem and Entra sign-in telemetry; a hybrid
  attacker crosses the boundary, so split logs hide the path.

## Takeaway

Hybrid identity doubles the directory and adds trust bridges between them, and the
bridges — Entra Connect, AD FS, Seamless SSO, PTA — are where the two worlds fuse
into one risk. Golden SAML and rogue federation forge cloud access from an on-prem
or admin compromise; the sync server reaches back the other way. Protect the bridge
components as Tier 0, guard and rotate their keys, alert on federation changes, and
monitor both sides as one identity fabric.

## References

- CISA — guidance on detecting Golden SAML / forged SAML token activity
- Dirk-jan Mollema (dirkjanm.io) — Entra Connect and hybrid attack research
- AADInternals (Nestori Syynimaa) — Golden SAML, Seamless SSO, backdoor techniques
- Microsoft — Entra Connect security, "Securing privileged access" (tier model)

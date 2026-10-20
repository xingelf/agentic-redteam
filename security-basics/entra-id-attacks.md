---
title: "Entra ID for Attackers"
tags: ["security-basics", "entra-id", "azure", "cloud", "identity"]
---

# Entra ID for Attackers

**TL;DR** — Entra ID (formerly Azure AD) is Microsoft's cloud identity service, and
it does **not** work like on-prem Active Directory. There is no Kerberos or NTLM and
no network perimeter — authentication is internet-facing and runs on **OAuth 2.0 /
OpenID Connect tokens**. So the attacks shift: phishing for tokens, tricking users
into **consenting** to malicious apps, **device-code** phishing, and stealing
**Primary Refresh Tokens** that sail past MFA. The defenses are phishing-resistant
MFA, Conditional Access, and governing app consent.

## A different model

- **Tokens, not tickets.** After you authenticate, Entra issues an **access token**
  (short-lived, for an API), a **refresh token** (to get new access tokens), and an
  **ID token**. Steal a refresh token and you keep access without the password.
- **Apps and consent.** Third-party and internal apps (service principals) request
  **scopes** like `Mail.Read` or `Files.ReadWrite.All`; a user or admin **consents**,
  and the app then acts via the Microsoft Graph API.
- **Roles.** Privilege is directory roles (Global Administrator, Privileged Role
  Administrator) plus Azure RBAC, not AD groups.
- **Internet-facing.** Anyone can reach the login endpoint, so password spraying and
  phishing need no foothold at all.

## The common attacks

### Illicit consent / OAuth app abuse

Phish a user to an attacker-registered app's consent screen (a real Microsoft URL).
If they approve, the app gets a refresh token for the granted scopes — persistent
mailbox or file access that **survives a password reset and often ignores MFA**,
because it is a separately authorized app, not a login. Admin-consent phishing aims
higher, for tenant-wide scopes.

### Device-code phishing

The OAuth **device authorization** flow is meant for input-constrained devices. An
attacker starts the flow, gets a short code, and sends the victim the legitimate
`microsoft.com/devicelogin` page plus the code. The victim authenticates (and
completes MFA) — and the attacker receives the tokens. Requests via the Microsoft
Authentication Broker client (`29d9ed98-a469-4536-ade2-f981bc1d605e`) can also lead
to **device registration** and a PRT.

### Primary Refresh Token (PRT) theft

A PRT is a long-lived token issued to a registered/joined device that provides
single sign-on. Stolen from a device (or obtained via the flows above), a PRT lets
an attacker mint tokens that **bypass MFA and device-based Conditional Access**,
because the PRT already represents a satisfied, compliant sign-in. Tooling such as
**ROADtools/ROADtx**, **AADInternals**, and **TokenTactics** works with these
tokens.

### Service-principal persistence

A quieter long game: add a new **client secret or certificate** to an existing
app registration / service principal you can edit. Now you authenticate as that app
indefinitely — no user, no MFA — until someone audits the app's credentials.

## Detection and defense

- **Phishing-resistant MFA.** FIDO2 / passkeys / Windows Hello defeat credential and
  most token phishing; push users off SMS/OTP.
- **Govern consent.** Restrict user consent to verified publishers and low-risk
  scopes; route the rest through an **admin consent workflow**; review existing
  grants with **app governance**. Revoke unknown enterprise apps.
- **Constrain device code.** Block the device-code flow with Conditional Access for
  users and locations that do not need it.
- **Conditional Access.** Require compliant/managed devices, trusted locations, and
  app controls; block legacy authentication outright.
- **Protect privileged roles.** Use **PIM** for just-in-time Global Admin, a tiny
  number of break-glass accounts, and separate cloud-only admin identities.
- **Monitor and revoke.** Watch sign-in logs and **Identity Protection** risk
  detections (impossible travel, unfamiliar sign-in, token anomalies); on
  compromise, **revoke refresh tokens/sessions** and rotate app credentials.
  **Continuous Access Evaluation** shortens the window a stolen token stays valid.

## Takeaway

Entra ID moves the fight from packets to tokens. The password is no longer the prize
— a consented app, a device-code trick, or a stolen PRT gives durable access that
can skip MFA and outlive a password reset. Defend it like the identity perimeter it
is: phishing-resistant MFA, tight Conditional Access, governed app consent, PIM for
admins, and fast token revocation when something looks off.

## References

- Dirk-jan Mollema (dirkjanm.io) — PRT, device code, and ROADtools research
- Microsoft — Entra ID token, consent framework, and Conditional Access docs
- AADInternals (Nestori Syynimaa) — tooling and technique notes
- MITRE ATT&CK — T1528 (Steal Application Access Token), T1550.001 (Application Access Token)

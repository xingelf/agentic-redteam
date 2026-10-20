---
title: "AD CS Certificate Abuse (ESC1–ESC8)"
tags: ["security-basics", "active-directory", "adcs", "privilege-escalation"]
---

# AD CS Certificate Abuse (ESC1–ESC8)

**TL;DR** — Active Directory Certificate Services issues certificates, and a
certificate with a client-authentication purpose *is a login credential*. A handful
of common misconfigurations let an ordinary user enroll for a certificate that
authenticates as someone else — up to Domain Admin — and because certificates are
long-lived, they are also stealthy persistence that survives password resets. The
catalog of misconfigurations is numbered **ESC1–ESC8** (and the community has
extended it well past ESC16). The fixes are in the templates and the CA, not a
single patch.

## Why certificates are credentials

AD supports certificate-based authentication (PKINIT / Schannel). If you hold a
certificate whose subject (or Subject Alternative Name) identifies a user and whose
Extended Key Usage allows **Client Authentication**, you can use it to get a
Kerberos TGT as that user. So the question becomes: *can a low-privileged user get
a certificate that names a high-privileged user?* Often, yes.

## The common misconfigurations

From SpecterOps' "Certified Pre-Owned" research (Will Schroeder and Lee
Christensen):

- **ESC1** — a template that allows low-priv **enrollment**, has a client-auth EKU,
  and lets the **enrollee supply the SAN**. You request a cert "as"
  `administrator` and authenticate as them. The most common and most direct.
- **ESC2 / ESC3** — templates with the **Any Purpose** EKU, or the **Certificate
  Request Agent** (enrollment agent) EKU, letting you enroll on behalf of others.
- **ESC4** — you have **write access to a template's ACL**, so you reconfigure it
  into an ESC1 and then abuse it.
- **ESC5** — write access to **PKI objects** in AD (the CA object, templates
  container) → reconfigure the PKI.
- **ESC6** — the CA has the **`EDITF_ATTRIBUTESUBJECTALTNAME2`** flag set, which lets
  *any* request specify a SAN regardless of the template.
- **ESC7** — you hold a **CA management role** (ManageCA / ManageCertificates) and
  can approve requests or flip settings.
- **ESC8** — **NTLM relay to the CA's HTTP web-enrollment** endpoint: coerce a
  machine (e.g. a DC), relay its authentication, and get a certificate as that
  machine (see the coercion/relay note).

The research also catalogs certificate **theft** and **persistence** (THEFT/PERSIST):
a stolen or maliciously enrolled cert is valid for its whole lifetime — often a
year or more — and keeps working after the victim changes their password.

## Tooling

**Certify** (C#) and **Certipy** (Python, by ly4k) enumerate vulnerable templates
and perform the enrollment:

```
# find vulnerable templates, then request as a target (illustrative, Certipy)
certipy find -u lowpriv@corp.local -p '...' -dc-ip 10.0.0.1
certipy req -u lowpriv@corp.local -p '...' -ca CORP-CA -template VulnTemplate -upn administrator@corp.local
```

## Detection and defense

- **Audit templates.** Remove the **enrollee-supplies-SAN** flag
  (`CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`) from client-auth templates, require
  **manager approval**, and restrict **enrollment rights** to groups that need them.
  This closes ESC1-style abuse.
- **Fix the CA.** Remove the **`EDITF_ATTRIBUTESUBJECTALTNAME2`** flag (ESC6) and
  lock down CA management roles (ESC7) and PKI object ACLs (ESC4/ESC5).
- **Protect enrollment endpoints.** Disable HTTP web enrollment if unused; otherwise
  require HTTPS and enable **Extended Protection for Authentication (EPA)** to stop
  ESC8 relays.
- **Enforce strong certificate mapping.** Apply Microsoft's post-2022 mapping
  hardening (KB5014754) so a certificate cannot be loosely mapped to a privileged
  account.
- **Treat PKI as Tier 0.** The CA and its admins belong in the same trust tier as
  domain controllers.
- **Monitor issuance.** CA events **4886/4887** (request received / issued), and
  certificates issued with a SAN that does not match the requester, or issued to
  privileged UPNs, are high-value alerts.

## Takeaway

AD CS turns "can I enroll for a certificate?" into "can I log in as anyone?" when
templates or the CA are misconfigured. ESC1 (enrollee-supplied SAN) and ESC8 (relay
to web enrollment) are the ones you will meet most, and both hand over Domain Admin
from an unprivileged start. Audit your templates and CA settings, protect the
enrollment endpoints with EPA, and watch certificate issuance — and remember a
malicious cert outlives the password reset you think cleaned up.

## References

- Schroeder & Christensen (SpecterOps) — "Certified Pre-Owned"
- Certipy (ly4k) and Certify (SpecterOps) project documentation
- Microsoft — KB5014754 certificate-based authentication changes; ADV210003
- The Hacker Recipes — AD CS (ESC1–ESC8 and beyond)

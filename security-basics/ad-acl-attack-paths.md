---
title: "AD ACL Attack Paths and BloodHound"
tags: ["security-basics", "active-directory", "privilege-escalation", "bloodhound"]
---

# AD ACL Attack Paths and BloodHound

**TL;DR** — Active Directory is a database of objects (users, groups, computers,
GPOs), and each object has an access control list saying who can do what *to it*.
A single over-permissive entry — "this helpdesk group can reset that admin's
password" — is a privilege-escalation edge. Chain enough edges and a nobody account
reaches Domain Admin. **BloodHound** is the tool that maps those chains as a graph;
attackers and defenders use the same map. The fix is least privilege on ACLs and
tiering, not a patch.

## Access as a graph, not a list

Think of every meaningful permission as a directed edge "A can control B." A few
edges that matter most:

- **GenericAll / GenericWrite** — full or broad write control over an object.
- **WriteDACL** — rewrite the object's ACL (so grant yourself anything).
- **WriteOwner / Owns** — take ownership, then rewrite the ACL.
- **ForceChangePassword** — reset a user's password without knowing the old one.
- **AddMember** — add yourself to a group (and inherit its rights).
- **AllExtendedRights** — includes password reset and, on the domain object, the
  DCSync rights (`DS-Replication-Get-Changes` + `-All`).

None of these is a "vulnerability" in the CVE sense — they are granted, usually by
accident, through nested groups, old delegations, and copy-pasted permissions.

## How a chain escalates

A realistic path, each step a legitimate right abused:

1. Your user is in a group with **GenericWrite** over a service account.
2. Use that to set a **Shadow Credential** (write `msDS-KeyCredentialLink`) or an
   SPN (targeted Kerberoast) and recover/assume that account.
3. That account has **WriteDACL** on a privileged group → grant yourself
   **AddMember** and join it.
4. That group has **DCSync** rights on the domain → replicate the `krbtgt` and
   every hash (see the Golden Ticket note).

Each hop looks mundane in isolation. The graph is what makes the route visible.

## BloodHound

**SharpHound** (the collector) enumerates objects, group membership, sessions, and
ACLs; **BloodHound** ingests that and answers queries like *"shortest path from any
owned user to Domain Admins."* It turned AD escalation from tribal knowledge into a
button, which is exactly why defenders must run it too — if you do not map your own
attack paths, the attacker will.

```
# collect, then open the graph (illustrative)
SharpHound.exe -c All
# then import the data into BloodHound and run "Shortest Path to Domain Admins"
```

## Detection and defense

- **Least privilege on ACLs.** The root cause is over-granted rights. Audit DACLs on
  privileged users, groups (Domain/Enterprise Admins), the domain head, GPOs, and
  the AdminSDHolder object. Remove `GenericAll`/`WriteDACL`/`WriteOwner` that no one
  needs.
- **Let SDProp work.** Protected groups are re-stamped from **AdminSDHolder** every
  hour; do not weaken it, and investigate objects whose ACLs drift.
- **Tier your administration.** Tier 0 (DCs, AD, PKI, Entra Connect) accounts and
  credentials never touch lower tiers. This breaks most chains regardless of stray
  ACEs.
- **Watch ACL changes.** Event **5136** (directory object modified) on DACLs of
  sensitive objects; alert on new DCSync rights, new `msDS-KeyCredentialLink`
  values (shadow credentials), and SPN additions to user accounts.
- **Run BloodHound on a schedule**, fix the shortest paths first, and re-run to
  confirm the edge is gone. Treat "paths to Tier 0" as findings with owners.

## Takeaway

AD privilege escalation is usually not an exploit — it is a graph of permissions
someone granted and forgot. The attacker's advantage is seeing the whole graph at
once with BloodHound; your advantage is running the same tool first, pruning the
dangerous edges (GenericAll, WriteDACL, DCSync) off your Tier 0 objects, and tiering
administration so the remaining edges lead nowhere useful.

## References

- SpecterOps — BloodHound documentation and the "edges" reference
- harmj0y — "An ACE Up the Sleeve" (AD DACL abuse)
- The Hacker Recipes — Abusing ACLs, Shadow Credentials
- MITRE ATT&CK — T1098 (Account Manipulation), T1222 (permissions modification)

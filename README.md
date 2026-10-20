# Agentic Red Teaming

Notes and tools on using agentic AI for red teaming — from a Tokyo-based pentester with 20+ years in offensive security.

Updated roughly once a week.

## Posts — Agentic AI

| Date | Title | Topic |
|------|-------|-------|
| 2026-10-25 | [Red Team, Visualized: There Is No Best LLM for Cyber](posts/2026-10-25_llm-cyber-benchmarks.md) | LLM cyber benchmarks / visualization |
| 2026-10-18 | [Red Team, Visualized: What a Breach Costs the Share Price](posts/2026-10-18_breach-stock-impact.md) | Security economics / event study |
| 2026-10-18 | [Red Team, Visualized: The Agentic Kill-Chain](posts/2026-10-18_red-team-visualized-kill-chain.md) | Visualization / ATT&CK |
| 2026-10-10 | [ARTEX and the Dual-Use Problem We Knew Was Coming](posts/2026-10-10_artex-dual-use.md) | Dual-use / threat intel |
| 2026-10-08 | [GLM-5.3 Leads One Cyber Benchmark and Trails Two. Read the Fine Print.](posts/2026-10-08_glm-5-3-cyber-benchmarks.md) | LLM cyber benchmarks |
| 2026-10-04 | [Your Agent Can Act. That's the New Attack Surface.](posts/2026-10-04_agent-tools-trust-boundary.md) | Tool abuse / trust boundaries |
| 2026-09-27 | [The Agent Finds More. Who Decides What Matters?](posts/2026-09-27_agent-recon-human-judgment.md) | AI-assisted recon |
| 2026-09-23 | [Your Agent Reads Everything. That's the Problem.](posts/2026-09-23_agent-reads-everything.md) | Indirect prompt injection |

## Security Basics

Evergreen reference notes on core offensive-security topics.

| Title | Topic |
|-------|-------|
| [SQL Injection: How It Works and How to Stop It](security-basics/sql-injection.md) | SQLi overview |
| [UNION-Based SQL Injection](security-basics/union-based-sqli.md) | SQLi — in-band |
| [Boolean-Based Blind SQL Injection](security-basics/boolean-sqli.md) | SQLi — blind |
| [Cross-Site Scripting (XSS): How It Works and How to Stop It](security-basics/xss.md) | XSS / injection |
| [OS Command Injection](security-basics/command-injection.md) | Command injection |
| [Server-Side Request Forgery (SSRF)](security-basics/ssrf.md) | SSRF / cloud metadata |
| [Broken Access Control and IDOR](security-basics/broken-access-control.md) | Access control (OWASP A01) |
| [jsonpickle: How py/reduce Turns Deserialization into RCE](security-basics/jsonpickle-deserialization.md) | Deserialization (Python) |
| [ObjectDataProvider: A .NET Deserialization Gadget](security-basics/object-data-provider.md) | Deserialization (.NET) |
| [XML CDATA, Escaping, and the XXE Trap](security-basics/xml-cdata.md) | XML / XXE |
| [SQL Collation, and Why It Matters for Security](security-basics/sql-collation.md) | Database internals |
| [Kerberos Authentication, Explained for Attackers](security-basics/kerberos-authentication.md) | Active Directory / Kerberos |
| [Kerberoasting and AS-REP Roasting](security-basics/kerberoasting.md) | AD — credential access |
| [Pass-the-Hash, Pass-the-Ticket, and Overpass-the-Hash](security-basics/pass-the-hash-ticket.md) | AD — lateral movement |
| [Golden and Silver Tickets](security-basics/golden-silver-tickets.md) | AD — Kerberos persistence |
| [Kerberos Delegation Abuse](security-basics/kerberos-delegation.md) | AD — privilege escalation |
| [AD ACL Attack Paths and BloodHound](security-basics/ad-acl-attack-paths.md) | AD — privilege escalation |
| [NTLM Coercion and Relay](security-basics/ntlm-coercion-relay.md) | AD — NTLM / relay |
| [AD CS Certificate Abuse (ESC1–ESC8)](security-basics/adcs-attacks.md) | AD — certificate services |
| [Entra ID for Attackers](security-basics/entra-id-attacks.md) | Entra ID / cloud identity |
| [Hybrid Identity Attacks](security-basics/hybrid-identity-attacks.md) | Hybrid AD / Entra ID |
| [Expanding a Kali VM Disk (VMware + GParted)](security-basics/kali-disk-expansion.md) | Lab / homelab ops |

## Visualizations

Interactive, self-contained visualizations built on public frameworks and public data. Series: *Red Team, Visualized*. The live site is deployed from GitHub Actions to GitHub Pages: [redteam-visualized home](https://xingelf.github.io/agentic-redteam/).

| Title | What it shows | Live | Source |
|-------|---------------|------|--------|
| The Agentic Kill-Chain | The autonomous offensive loop, stage by stage, with ATT&CK mappings, detection, and defenses | [Pages](https://xingelf.github.io/agentic-redteam/viz/agentic-kill-chain/) | [viz/agentic-kill-chain](viz/agentic-kill-chain/) |
| Known Exploited Vulnerabilities | Self-updating CISA KEV dashboard — totals, monthly additions, top vendors, newest entries (refreshed daily by GitHub Actions) | [Pages](https://xingelf.github.io/agentic-redteam/viz/kev-dashboard/) | [viz/kev-dashboard](viz/kev-dashboard/) |
| What a Breach Costs the Share Price | Event study of 24 public-company incidents (US, Japan, Europe) — abnormal returns and CAR around disclosure, stripped of market moves | [Pages](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/) | [viz/breach-stock-impact](viz/breach-stock-impact/) |
| No Single Best LLM for Cyber | Three public cyber benchmarks compared — how the lead changes with the metric, agent harness, reasoning mode, and benchmark (primary sources only) | [Pages](https://xingelf.github.io/agentic-redteam/viz/llm-cyber-benchmarks/) | [viz/llm-cyber-benchmarks](viz/llm-cyber-benchmarks/) |
| The Kerberos Attack Map | One Kerberos exchange with five AD attacks overlaid — each lighting up the message it cracks, skips, or forges, and the key it relies on | [Pages](https://xingelf.github.io/agentic-redteam/viz/kerberos-attack-map/) | [viz/kerberos-attack-map](viz/kerberos-attack-map/) |

## Tools

| Name | What it does | Status |
|------|--------------|--------|
| — | Coming soon | — |

## Scope

- Using AI agents to support red team work (recon, triage, reporting, attack planning)
- Red teaming AI agents themselves (prompt injection, tool abuse, trust boundaries)
- What works in practice, and what doesn't

## Disclaimer

For authorized security testing and education only.
Everything here is meant to be used against systems you own or have written permission to test.
The author is not responsible for misuse.

## License

Code: [MIT](LICENSE). Articles: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

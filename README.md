# Agentic Red Teaming

Notes and tools on using agentic AI for red teaming — from a Tokyo-based pentester with 20+ years in offensive security.

Updated roughly once a week.

## Posts — Agentic AI

| Date | Title | Topic |
|------|-------|-------|
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
| [jsonpickle: How py/reduce Turns Deserialization into RCE](security-basics/jsonpickle-deserialization.md) | Deserialization (Python) |
| [ObjectDataProvider: A .NET Deserialization Gadget](security-basics/object-data-provider.md) | Deserialization (.NET) |
| [XML CDATA, Escaping, and the XXE Trap](security-basics/xml-cdata.md) | XML / XXE |
| [SQL Collation, and Why It Matters for Security](security-basics/sql-collation.md) | Database internals |
| [Expanding a Kali VM Disk (VMware + GParted)](security-basics/kali-disk-expansion.md) | Lab / homelab ops |

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

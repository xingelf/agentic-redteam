# The Agentic Kill-Chain

Interactive map of the autonomous offensive loop — recon, discovery, planning,
exploitation, foothold, exfiltration — with an ATT&CK mapping, a detection
opportunity, and a defense for each stage. An attacker/defender toggle switches the
emphasis.

First piece in the **Red Team, Visualized** series.

## Live

- Interactive: https://claude.ai/artifact/2b9PoSo7akPqxFB4wcFvEr
- Companion post: [../../posts/2026-10-18_red-team-visualized-kill-chain.md](../../posts/2026-10-18_red-team-visualized-kill-chain.md)

## How it's built

- `index.html` is self-contained: no build step, no dependencies, no network calls.
  Fonts load from Google Fonts; everything else is inline.
- It is the source of the published Claude Artifact above. Opening the file
  directly in a browser works too.

## Data

Public frameworks only — no target, client, or engagement data.

- [MITRE ATT&CK](https://attack.mitre.org/) — tactic and technique IDs
- [OWASP](https://owasp.org/) — context

Technique mappings are representative, not exhaustive.

## License

Code: MIT. Content: CC BY 4.0 (same as the repo).

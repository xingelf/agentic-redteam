# The Kerberos Attack Map

One Kerberos exchange, with the five best-known Active Directory attacks laid over
it. Pick an attack and the message it cracks, skips, or forges lights up, along with
the key it relies on — showing that Kerberoasting, AS-REP Roasting, Golden Tickets,
Silver Tickets, and Pass-the-Ticket are not five separate tricks but five attacks on
one protocol.

Fifth piece in the **Red Team, Visualized** series.

## Live

- GitHub Pages: https://xingelf.github.io/agentic-redteam/viz/kerberos-attack-map/

## What it shows

The standard three-party flow (Client → KDC → Service) as a sequence of five
messages: AS-REQ/AS-REP (the TGT), TGS-REQ/TGS-REP (the service ticket), and AP-REQ
to the service. Selecting an attack re-styles the flow:

- **AS-REP Roasting** — targets the AS-REP (user key), pre-auth skipped.
- **Kerberoasting** — targets the TGS-REP (service key).
- **Golden Ticket** — forges the TGT (krbtgt key), the AS exchange bypassed.
- **Silver Ticket** — forges the service ticket (service key), the KDC bypassed.
- **Pass-the-Ticket** — injects a stolen, still-valid ticket, skipping the exchange
  that produced it.

Each state names the prerequisite, the key relied on, the ATT&CK technique, and a
one-line detection/defense, and links to the matching security-basics note.

## How it's built

- Self-contained `index.html`, no build and no dependencies. The model (the five
  messages and the five attacks) is inlined as a small JavaScript object — there is
  no data pipeline, because this is a conceptual diagram, not a dataset.
- The diagram is hand-drawn SVG; attacks re-style message groups by class. Keyboard
  accessible (arrow keys move between attacks), with a light/dark theme from the
  house tokens.

## Files

- `index.html` — the interactive diagram (self-contained)

## Caveats

- An illustrative teaching model, not tooling. No payloads, no target or engagement
  data. Technique mappings are representative, not exhaustive.
- Real Kerberos has more detail (referrals, renewals, cross-realm, PAC validation)
  than five messages; this is the mental model the attacks hang on, deliberately
  simplified.

## License

Code: MIT. Content: CC BY 4.0 (same as the repo).

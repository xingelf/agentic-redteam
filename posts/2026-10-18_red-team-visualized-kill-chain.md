---
title: "Red Team, Visualized: The Agentic Kill-Chain"
date: 2026-10-18
tags: ["agentic-ai", "red-team", "visualization", "att&ck"]
---

# Red Team, Visualized: The Agentic Kill-Chain

**TL;DR** — A new series. Instead of another post explaining the autonomous
offensive loop, here is one you can walk through. The first piece maps the
agentic kill-chain stage by stage — what the agent does, where it gives itself
away, and what closes the door — against public MITRE ATT&CK.

## Why a visual series

Some ideas on this blog keep coming back in prose: the recon-to-exploit loop, the
machine cadence that makes agents noisy, the gap between finding a bug and
exploiting one. They are easier to hold when you can see them and poke at them.
*Red Team, Visualized* is that — small, self-contained visualizations, each one
tied to a post, each built on public frameworks and nothing else. No target data,
no engagement data.

## The first one

[The Agentic Kill-Chain](https://xingelf.github.io/agentic-redteam/viz/agentic-kill-chain/) is an
interactive map of the loop an autonomous offensive agent runs: gather, find,
plan, exploit, hold, take — then repeat with what it learned.

Each stage opens a panel with four things:

- **What the agent does** at that stage.
- **ATT&CK techniques** it maps to, by ID.
- **The detection opportunity** — usually machine cadence: volume, regularity, and
  breadth that a human would not produce.
- **The defense** that closes the door.

An attacker/defender toggle flips the emphasis. In attacker view you read the
offense top to bottom; in defender view, detection and defense come first.

One stage has no ATT&CK technique on purpose: planning. The agent's reasoning
happens inside the model, off your systems, and leaves no trace. You cannot
monitor the thinking, so you defend the actions on either side of it. That blind
spot is the point.

The source is in the repo under
[`viz/agentic-kill-chain/`](https://github.com/xingelf/agentic-redteam/tree/main/viz/agentic-kill-chain) —
a single self-contained HTML file, no build step.

## Takeaway

The kill-chain is not new, and neither is any single defense in it. The visual
makes one thing obvious: every stage an autonomous agent speeds through is a stage
where the boring, well-known control still works. The agent got faster. The doors
did not move.

## What's next in the series

Machine-cadence detection (human vs agent request patterns on public IDS data), a
SQL-injection decision tree, an LLM cyber-benchmark comparator, and an ATT&CK
heatmap of agent-automatable techniques.

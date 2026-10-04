---
title: "Your Agent Can Act. That's the New Attack Surface."
date: 2026-10-04
tags: ["agentic-ai", "red-team", "tool-abuse", "trust-boundary"]
---

# Your Agent Can Act. That's the New Attack Surface.

**TL;DR** — A chatbot can only talk. An agent has tools: it reads files, calls APIs,
runs commands, sends mail. The moment you give it tools, the question stops being
"what will it say?" and becomes "what can it do, and on whose authority?" Test the
tools, not just the prompt.

## Context

The first two posts looked at what an agent *reads* — indirect prompt injection, and
the recon output a human still has to judge. This one is about what an agent *does*.

A chatbot's worst case is a bad answer. An agent's worst case is a bad action: a file
deleted, a secret emailed out, a payment sent, a production command run. The tools are
the real attack surface. The prompt is just one way to reach them.

Two ideas frame the rest of this post:

- **Trust boundary.** The line between untrusted input (a web page, an email, a tool's
  own output) and trusted action (calling a tool with real credentials). In agent
  systems this line is almost always blurry, because text the agent reads can decide
  which tool it calls next.
- **Confused deputy.** The agent holds more authority than the attacker does. If an
  attacker can steer the agent, the agent spends its authority on the attacker's behalf.
  The classic privilege problem, now wearing an LLM.

OWASP's LLM Top 10 has a category for exactly this failure mode: Excessive Agency —
too much permission, too much autonomy, too little oversight on what the tools can do.

## The approach

The general method I use when red teaming an agent's tools:

1. **Enumerate the tools first, not the prompts.** List every tool the agent can call,
   what each one is allowed to do, and what credentials sit behind it. The dangerous
   tools are the ones that write, send, pay, or run — not the ones that only read.

2. **Map the trust boundary.** For each tool, ask: can any *untrusted* text the agent
   reads influence whether this tool fires, or with what arguments? If yes, that tool
   is reachable by an attacker who never touches the chat box.

3. **Look for the confused deputy.** Check what authority the agent runs with. Does it
   use one shared high-privilege credential for every user? Can a low-privilege user
   get the agent to do something they could not do themselves?

4. **Chain, don't single-shot.** Real impact usually comes from a sequence: read a
   poisoned document → extract an "instruction" → call a write/send tool with
   attacker-chosen arguments. Test the chain, not each tool alone.

## Patterns that keep showing up

A few failure patterns worth calling out:

- Read-only tools treated as safe, while their *output* is fed straight back into the
  agent as if it were trusted instruction.
- Tool arguments that are never validated — the agent is trusted to "ask nicely," so
  an injected string lands directly in a shell, a query, or a recipient field.
- One credential for all users, so every bug is a privilege-escalation bug.

## Takeaway

Giving an agent a tool is giving it authority. Red team the authority, not the
personality. Before you ship: for every tool that can change the world, draw the line
between the untrusted text that can reach it and the real permission behind it — and
assume an attacker is standing on that line.

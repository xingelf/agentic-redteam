---
title: "The Agent Finds More. Who Decides What Matters?"
date: 2026-09-27
tags: ["agentic-ai", "red-team", "recon", "workflow"]
---

# The Agent Finds More. Who Decides What Matters?

**TL;DR** — AI agents make recon faster by handling the reading, sorting, and note-taking. They do not make it smarter. Scope, judgment, and accountability stay with the human.

## Context

Recon is the most time-consuming part of many engagements, and much of it is not hard work.
It is reading: scope documents, public records, tool output, and long lists of hosts and services.

That is exactly what language models are good at. So it is natural to hand recon to an agent.

The risk is that an agent is fast *and* confident. It will happily produce a clean,
well-formatted picture of the target, and some of that picture will be wrong,
out of scope, or irrelevant. Speed without judgment just produces mistakes faster.

## Where the agent helps

Good tasks share one trait: the output is easy for a human to check.

| Task | Why it works |
|------|--------------|
| Summarizing the scope and rules of engagement | Turns a long document into a checklist you verify once |
| Normalizing tool output | Merges results from different tools into one table, removes duplicates |
| Grouping and tagging assets | Clusters hosts by owner, function, or technology for faster review |
| Reading public documentation | Summarizes what a product or service is supposed to do |
| Keeping notes | Records what was done, when, and why — the start of your report |
| Suggesting next questions | "These three hosts look unusual — worth a closer look?" |

In each case, the agent *prepares*. The human *decides*.

## Where you still need a human

**Scope.** An agent does not know that a subdomain belongs to a third-party vendor,
or that one IP range was excluded in an email last week. Scope is a legal boundary,
not a technical one. A human must own it.

**Approval for active steps.** Reading and organizing are low risk. Anything that
sends traffic to a target is not. Keep a human approval step between "the agent
suggests" and "the agent does".

**Checking the facts.** Models fill gaps with plausible guesses: a version number,
a technology, an owner. Treat every claim as a lead until you have confirmed it
from a primary source.

**Deciding what matters.** An agent can list 500 findings. Knowing which three
the client should care about requires understanding their business. That is the
part clients pay for.

**Handling client data.** Recon output is sensitive. Before you send it to any
AI service, check that your contract and the provider's data terms allow it.
When in doubt, use a local model or keep that data out.

## A simple setup

A workflow that keeps the speed and the control:

1. **Scope file first.** Write in-scope and out-of-scope items in one file the
   agent reads at the start. Make the agent restate it; you confirm.
2. **Read-only by default.** Give the agent tools that read and organize.
   Keep active tools behind explicit human approval.
3. **Log everything.** Every action the agent takes goes into a timestamped log.
   This protects you and becomes part of the report.
4. **Mark confidence.** Ask the agent to tag each item as *confirmed* or *inferred*.
   Only confirmed items move forward.
5. **Human review at each phase.** Recon → analysis → testing. A person signs off
   before the next phase starts.

## Takeaway

An agent is a very fast junior analyst who never gets tired and never says "I'm not sure".
Use it for the volume. Keep the judgment for yourself.

---

*Authorized testing only. Run recon only against targets you have written permission to test.*

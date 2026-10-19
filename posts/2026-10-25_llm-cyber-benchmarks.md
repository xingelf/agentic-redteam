---
title: "Red Team, Visualized: There Is No Best LLM for Cyber"
date: 2026-10-25
tags: ["agentic-ai", "red-team", "llm", "benchmarks", "visualization"]
---

# Red Team, Visualized: There Is No Best LLM for Cyber

**TL;DR** — "Which model is best at offensive security?" is the wrong question,
and the leaderboards prove it. I pulled the numbers from three public benchmarks —
only what you can read in the primary papers — and visualized them. The lead
changes hands depending on what you measure, which agent harness wraps the model,
and whether reasoning is switched on. A couple of weeks ago I wrote that GLM-5.3
"leads one benchmark and trails two." This is that lesson generalized. [See it in
the visualization](https://xingelf.github.io/agentic-redteam/viz/llm-cyber-benchmarks/).

## The question everyone asks

Every few weeks a client or a colleague asks some version of "so which model
should we point at this?" They want one name. The leaderboards seem to offer one —
there is always a bar chart with somebody on top. The chart is usually true and
almost always misleading, because it is showing you one metric, one harness, one
run. Move any of those and the name on top changes.

I wanted to show that without hand-waving, so I built a small comparator from three
well-known public benchmarks and held myself to one rule: **only numbers I can read
in the primary paper.** No secondary tracker sites, no vendor self-reports that
aren't in a paper, no models I couldn't verify. That throws away a lot of shiny
2026 leaderboard numbers whose provenance I couldn't stand behind. What's left is
smaller, older, and trustworthy — and it already makes the point.

## Three benchmarks, three different stories

The benchmarks measure genuinely different jobs, which is the first thing the
headline hides:

- **Cybench** — 40 professional CTF challenges. Can the agent solve a security
  puzzle end to end?
- **CyberGym** — 1,507 real-world vulnerability-reproduction tasks. Can it take a
  known bug and produce a working proof of concept at scale?
- **CVE-Bench** — 40 real web-application CVEs. Can it actually exploit a live app?

Because the tasks differ, the percentages are not comparable across benchmarks.
17.9% on CyberGym is not "better than" 17.5% on Cybench; they are different
denominators. The visualization keeps every chart on its own scale for exactly
this reason. The interesting thing is never the absolute number — it is the
*ordering*, and how easily it moves.

## The lead changes with what you measure

Cybench reports the same runs three ways: unguided (solve the whole task cold),
subtask-guided (solve it with the subtasks revealed), and a subtask score
(fraction of subtasks solved). Three leaders:

- **Unguided:** Claude 3.5 Sonnet, 17.5%.
- **Subtask-guided:** GPT-4o, 17.5%.
- **Subtask score:** OpenAI o1-preview, 46.8%.

I didn't editorialize that — the Cybench authors write it themselves: the top
models "each hav[e] the highest success rate on a different metric." If you quote
the unguided number you crown Claude; quote the subtask score and o1-preview wins
by a mile. Same models, same tasks, same paper. The only thing that changed is
which column you pointed at.

## The harness can move as much as the model

Here is the part that matters most for anyone actually building an agent. Cybench
also ran its two strongest models under four different agent scaffolds. The
ranking flips with the wrapper: GPT-4o drops from 17.5% to 10.0% on the
pseudoterminal scaffold, while Claude 3.5 Sonnet climbs to 20.0% on the same one.

CVE-Bench makes the point even harder, holding the model *fixed*. With one backbone
model, a single CTF-style agent exploits 2.5% of the CVEs; a hierarchical
multi-agent team reaches 13% — a roughly five-fold swing, all from the scaffolding.
The model was never the variable.

For a red teamer this is the whole game. The thing you deploy is not a model, it is
a model inside a loop — tools, planning, retries, memory. Benchmark numbers on the
bare model systematically under-describe what the full agent does, in both
directions. When a vendor shows you a model score, the honest follow-up is "under
which harness?"

## Reasoning mode re-orders the board too

On CyberGym, turning on high reasoning lifts GPT-5 from 7.8% to 22.0% — enough to
overtake Claude Sonnet 4, which sits at 17.9%. Same weights, a different inference
setting, a different winner. One more knob that the single headline number quietly
fixes for you.

## Why a pentester should care

Three practical takeaways fall out of this:

- **Don't buy the leaderboard; buy the measurement closest to your task.** If your
  job is live web exploitation, a CTF-solving score is weak evidence. Match the
  benchmark to the work, and prefer results run more than once, with variance.
- **Budget for the harness, not just the model.** A five-fold swing from
  scaffolding means your agent engineering — tools, orchestration, retries — is at
  least as important as which API key you hold. That is where a lot of the real
  capability, and the real risk, lives.
- **Treat any single number as a hint.** Metric, harness, reasoning mode, and
  benchmark each move the ranking. A model that "tops the chart" tops *a* chart.

## The caveats, stated plainly

- **Primary sources only, which means older models.** The verifiable papers mostly
  predate the newest frontier releases. The point here is the *structure* of the
  comparison — how fragile the ranking is — not a 2026 power ranking.
- **Benchmarks are proxies.** They are a particular task set under a particular
  harness, not your target. A score does not transfer to your engagement.
- **Not comparable across benchmarks.** Every percentage lives inside its own
  benchmark. The charts are built so you can't accidentally read one against
  another.

## About the visualization

The [dashboard](https://xingelf.github.io/agentic-redteam/viz/llm-cyber-benchmarks/)
shows Cybench's three leaders side by side, the scaffold swing as a slope chart,
CyberGym with the reasoning-on jump marked, and CVE-Bench's harness swing on a
fixed model — plus the full tables with every source linked. It is built by a short
stdlib Python script that just encodes the transcribed numbers with their citations
([`scripts/build_llm_cyber_bench.py`](https://github.com/xingelf/agentic-redteam/blob/main/scripts/build_llm_cyber_bench.py)).
Public data only. For education and analysis, not a buying guide.

## What's next in the series

Machine-cadence detection (human vs agent request patterns), a SQL-injection
decision tree, and an ATT&CK heatmap of agent-automatable techniques.

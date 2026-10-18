---
title: "Red Team, Visualized: What a Breach Costs the Share Price"
date: 2026-10-18
tags: ["security-economics", "red-team", "visualization", "event-study"]
---

# Red Team, Visualized: What a Breach Costs the Share Price

**TL;DR** — People ask whether a breach "really" hurts a public company, or whether
the stock just dips and recovers. I ran an event study on sixteen well-known
incidents, nine in the US and seven in Japan: strip out the market, measure the
abnormal return around the disclosure date, and watch the line. The US average sat
about 13% below its expected value thirty trading days after disclosure. The Japanese
average was about 3%. Same kind of incident, very different market reaction. [See it
in the visualization](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/).

## The question, and the trap

"Does a breach move the stock?" is easy to ask and easy to answer badly. The lazy
version is to look at the share price before and after and point at the drop. That is
almost always wrong, because the stock would have moved anyway — the whole market
goes up and down, and so does the company's sector. If the market fell 5% that week,
a 5% drop is not news.

The clean way is an **event study**, a standard tool in finance. You model how the
stock normally moves with its market — its baseline drift (alpha) and its sensitivity
to the index (beta) — estimated over a long window *before* the incident. Then, around
the disclosure, you measure the **abnormal return**: how far the stock moved beyond
what that relationship predicts. Sum it over time and you get the cumulative abnormal
return (CAR). That is the part you can plausibly attribute to the event, with the
market's noise removed. I measured each company against its home index — US names
against the S&P 500, Japanese names against the Nikkei 225 — so "the market" means the
right market in each case.

## What the sixteen show

I picked companies with major, well-documented incidents and clear public disclosure
dates. US: Equifax, Target, Marriott, Capital One, Progress (MOVEit), Okta, MGM
Resorts, Clorox, and UnitedHealth's Change Healthcare. Japan: Capcom, KADOKAWA,
Toyota, Honda, Mitsubishi Electric, Fujitsu, and Casio. The window runs from ten
trading days before disclosure to thirty after.

The headline is the split between the two markets:

- **US average: about −13% cumulative abnormal return by day +30**, and every one of
  the nine was negative.
- **Japan average: about −3% by day +30**, and two of the seven were actually
  *positive* over the window.

That is a real gap, and it is the most interesting thing in the data. The same class
of event — a disclosed, serious breach at a large listed company — gets repriced hard
in the US and shrugged off, on average, in Japan.

## Why the US reacts harder

I would not over-read a seven-name Japanese sample, and the caveats below matter. But
the pattern is consistent with a few things:

- **Disclosure timing and culture differ.** US issuers face SEC pressure to disclose
  material incidents quickly and specifically; the market gets a sharp, dated signal.
  Several of the Japanese disclosures were vaguer, slower, or surfaced first through
  press reporting, which smears the reaction across days instead of concentrating it.
- **What got hit differs.** The worst US cases attacked the thing the business sells.
  Equifax is a credit-data company and lost trust in its data handling; it slid to
  roughly −25%. Okta sells identity security, and a security vendor getting breached is
  an argument against its own product; it ended near −21%. Change Healthcare was an
  operational chokepoint for US medical claims.
- **The Japanese incidents skewed operational.** Toyota and Honda were production
  stoppages — bad, but a one-off cost at a company whose customers do not leave over
  it. Both ended only a few percent down. The exception proves the rule: **KADOKAWA**,
  whose platforms and publishing operations were down for weeks, fell about −16% —
  because for KADOKAWA the outage *was* the business.

And two Japanese names ended the window positive — Fujitsu and Mitsubishi Electric.
That is not the market rewarding a breach. It is the honest reminder that a single
incident's thirty-day window can be swamped by earnings, guidance, or a sector rally.
The model removes the market; it does not remove everything else.

## The better question

Across both markets, the pattern in the spread is more useful than either average.
The incidents that kept bleeding have one thing in common: **the breach hit the thing
the business sells.** Credit data for Equifax. Identity security for Okta. The platform
itself for KADOKAWA. The ones that recovered fast were bad things that happened to an
otherwise healthy business whose customers do not switch over it — Marriott, Capital
One, Toyota, Honda.

So the better question is not "how much does a breach cost the stock" but "**does this
breach attack the company's reason to exist?**" That is the line between a dip and a
re-rating, and it holds in Tokyo as well as New York.

## The caveats, stated plainly

I would not use these averages in a slide without these:

- **Hand-picked, severe cases.** Not random, so the averages overstate the typical
  incident. Most breaches at most companies barely register. These were chosen because
  they are legible, not representative — and the Japanese sample is small.
- **Correlation is not causation.** The market model removes the market, not every
  confounder. An earnings miss in the same window rides along in the "abnormal" return.
- **Disclosure date is not incident date.** The market reacts to what it learns, when
  it learns it. day 0 is the disclosure, which can be months after the compromise.

## Why a pentester cares about any of this

Two reasons. First, this is the number that gets security budget approved or denied,
and it is usually quoted badly — either "breaches don't matter, the stock recovers" or
"a breach will destroy us." The truth is conditional, and the condition is whether the
breach touches the trust the business runs on. That is a threat-modeling question
before it is a finance question, and security people are well placed to answer it.

Second, it reframes "crown jewels." The assets that move the share price are not the
ones with the most records. They are the ones whose compromise is an argument against
the company itself — a security vendor's own build and identity systems, a data
broker's data, a platform company's platform. Find the asset whose loss would re-rate
the business, and you have found what actually needs defending first.

## About the visualization

The [dashboard](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/)
shows the average cumulative abnormal return for each market as two lines, each
incident ranked by its 30-day move, a small chart per incident indexed to its
disclosure, and the full table of betas and CARs. It is built from public prices and
public disclosure dates by a short stdlib Python script in the repo
([`scripts/build_breach_stock.py`](https://github.com/xingelf/agentic-redteam/blob/main/scripts/build_breach_stock.py));
the event windows are closed history, so the data is built once and committed. Public
data only. For education and analysis, not investment advice.

## What's next in the series

Machine-cadence detection (human vs agent request patterns), a SQL-injection decision
tree, and an ATT&CK heatmap of agent-automatable techniques.

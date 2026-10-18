---
title: "Red Team, Visualized: What a Breach Costs the Share Price"
date: 2026-10-18
tags: ["security-economics", "red-team", "visualization", "event-study"]
---

# Red Team, Visualized: What a Breach Costs the Share Price

**TL;DR** — People ask whether a breach "really" hurts a public company, or whether
the stock just dips and recovers. I ran an event study on nine well-known incidents:
strip out the market, measure the abnormal return around the disclosure date, and
watch the line. Across these nine, the average stock sat about 13% below its expected
value thirty trading days after disclosure, and every one of them was negative. But
the honest story is in the spread, not the average. [See it in the
visualization](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/).

## The question, and the trap

"Does a breach move the stock?" is easy to ask and easy to answer badly. The lazy
version is to look at the share price before and after and point at the drop. That is
almost always wrong, because the stock would have moved anyway — the whole market
goes up and down, and so does the company's sector. If the market fell 5% that week,
a 5% drop is not news.

The clean way to ask the question is an **event study**, a standard tool in finance.
You model how the stock normally moves with the market — its own baseline drift
(alpha) and its sensitivity to the market (beta) — estimated over a long window
*before* the incident. Then, around the disclosure, you measure the **abnormal
return**: how far the stock moved beyond what that relationship predicts. Sum it over
time and you get the cumulative abnormal return (CAR). That is the part you can
plausibly attribute to the event, with the market's noise removed.

## What the nine show

I picked nine public companies with major, well-documented incidents and clear
public disclosure dates — Equifax, Target, Marriott, Capital One, Progress (MOVEit),
Okta, MGM Resorts, Clorox, and UnitedHealth's Change Healthcare. The benchmark is the
S&P 500. The window runs from ten trading days before disclosure to thirty after.

Three things stand out:

- **Every one was negative by day +30.** That is not guaranteed and it is not what a
  lot of the academic literature finds on broad samples — which tells you something
  about the sample, more on that below.
- **The average drop is real but moderate**: around −13% cumulative abnormal return by
  day +30, roughly −5% in the first day alone. Money, but not ruin, on average.
- **The spread is enormous.** Equifax kept sliding to roughly −25%. Okta, Clorox, and
  Change Healthcare landed near −15% to −20%. Marriott and Capital One shrugged most
  of it off within a month, ending only a few percent down.

## Why some get punished and others don't

The pattern in the spread is more useful than the average. The incidents that kept
bleeding have one thing in common: **the breach hit the thing the business sells.**

Equifax is a credit-data company; the product *is* trust in its data handling, and it
lost exactly that. Okta sells identity security; a vendor whose product is security
getting compromised is a special kind of damage, because the incident is an argument
against the product itself. Change Healthcare sat in the middle of a huge share of US
medical claims, so the breach was also an operational outage with direct revenue loss.

The ones that recovered fast were, roughly, "a bad thing happened to an otherwise
healthy business whose customers don't switch over it." People kept booking Marriott
rooms. Capital One's customers mostly stayed. The market repriced the one-time cost
and moved on.

So the better question is not "how much does a breach cost the stock" but "**does this
breach attack the company's reason to exist?**" That is the line between a dip and a
re-rating.

## The caveats, stated plainly

I would not use that −13% in a slide without these:

- **This is a hand-picked sample of severe cases.** It is not random, so the average
  overstates the typical incident. Most breaches at most companies barely register.
  The nine here were chosen because they are legible, not because they are
  representative.
- **Correlation is not causation.** The market model removes the market, not every
  confounder. If an earnings miss or a guidance cut lands in the same window, it rides
  along in the "abnormal" return. I flagged the method; I did not adjudicate every
  daily move.
- **Disclosure date is not incident date.** The market reacts to what it learns, when
  it learns it. day 0 is the disclosure, which can be months after the actual
  compromise.

## Why a pentester cares about any of this

Two reasons. First, this is the number that gets security budget approved or denied,
and it is usually quoted badly in both directions — either "breaches don't matter, the
stock recovers" or "a breach will destroy us." The truth is conditional, and the
condition is whether the breach touches the trust the business runs on. That is a
threat-modeling question before it is a finance question, and it is one security
people are well placed to answer.

Second, it reframes what "crown jewels" means. The assets that move the share price
are not the ones with the most records or the biggest database. They are the ones
whose compromise is an argument against the company itself. For a security vendor
that is its own build and identity systems. For a data broker it is the data. Find the
asset whose loss would re-rate the business, and you have found what actually needs
defending first.

## About the visualization

The [dashboard](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/)
shows the average cumulative abnormal return over the event window, each incident
ranked by its 30-day drop, a small chart per incident indexed to its disclosure, and
the full table of betas and CARs. It is built from public prices and public
disclosure dates by a short stdlib Python script in the repo
([`scripts/build_breach_stock.py`](https://github.com/xingelf/agentic-redteam/blob/main/scripts/build_breach_stock.py));
the event windows are closed history, so the data is built once and committed. Public
data only. For education and analysis, not investment advice.

## What's next in the series

Machine-cadence detection (human vs agent request patterns), a SQL-injection decision
tree, and an ATT&CK heatmap of agent-automatable techniques.

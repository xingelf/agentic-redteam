---
title: "Red Team, Visualized: What a Breach Costs the Share Price"
date: 2026-10-18
tags: ["security-economics", "red-team", "visualization", "event-study"]
---

# Red Team, Visualized: What a Breach Costs the Share Price

**TL;DR** — People ask whether a breach "really" hurts a public company, or whether
the stock just dips and recovers. I ran an event study on twenty-four well-known
incidents across the US, Japan, and Europe: strip out the market, measure the
abnormal return around the disclosure date, and watch the line. The US average sat
about 13% below its expected value thirty trading days after disclosure, Europe about
6%, and Japan about 3%. Same kind of incident, three different market reactions — and
one pattern that holds in all three. [See it in the
visualization](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/).

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
market's noise removed. I measured each company against its own home-country index, in
the same currency — US names against the S&P 500, Japanese names against the Nikkei
225, European names against the FTSE 100, DAX, CAC 40, OMXC25, or OSEBX as fit — so
"the market" means the right market in each case.

## What the twenty-four show

I picked companies with major, well-documented incidents and clear public disclosure
dates. US: Equifax, Target, Marriott, Capital One, Progress (MOVEit), Okta, MGM
Resorts, Clorox, UnitedHealth's Change Healthcare. Japan: Capcom, KADOKAWA, Toyota,
Honda, Mitsubishi Electric, Fujitsu, Casio. Europe: Maersk, Norsk Hydro, Marks &
Spencer, EasyJet, Thyssenkrupp, Bayer, Sopra Steria, Capita. The window runs from ten
trading days before disclosure to thirty after.

The averages differ by market:

- **US: about −13% cumulative abnormal return by day +30**, and every one of the nine
  was negative.
- **Europe: about −6%**, with a huge spread — two IT/outsourcing names down more than
  20%, two others actually up.
- **Japan: about −3%**, the mildest, with two of seven positive over the window.

The US reacts hardest. Part of that is disclosure culture: US issuers face SEC
pressure to disclose material incidents quickly and specifically, so the market gets a
sharp, dated signal. Several European and Japanese disclosures were vaguer or surfaced
first through press reporting, which smears the reaction across days. But the averages
are the least interesting part. The pattern in the *spread* is the point.

## The one pattern that holds everywhere

Sort every incident by its 30-day move and the worst cases, in all three markets, have
one thing in common: **the breach hit the thing the business sells.**

- **US**: Equifax, a credit-data company that lost trust in its data handling, slid to
  about −25%. Okta, which sells identity security, ended near −21% — a security vendor
  getting breached is an argument against its own product.
- **Europe**: Capita, a UK outsourcer that runs other companies' operations and data,
  fell about −29%. Sopra Steria, a French IT-services giant, about −22%. Same logic as
  Okta: when you sell trust and operations, a breach attacks the product itself. Marks
  & Spencer, down about −21%, is the operational version — weeks of halted online
  sales in 2025, where the outage *was* the revenue.
- **Japan**: KADOKAWA, whose publishing and platform operations were down for weeks,
  fell about −16% while the rest of the Japanese sample barely moved.

The incidents that recovered fast were, everywhere, bad things that happened to an
otherwise healthy business whose customers do not switch over it — Marriott, Capital
One, Toyota, Honda, Bayer.

So the better question is not "how much does a breach cost the stock" but "**does this
breach attack the company's reason to exist?**" That is the line between a dip and a
re-rating, and it holds in New York, Tokyo, and London alike.

## When the model lies to you

Four of the twenty-four ended the window *positive*: EasyJet (+20%), Maersk (+6%),
Norsk Hydro (+5%), and Mitsubishi Electric. That is not the market rewarding a breach.
It is the honest limit of the method.

EasyJet disclosed its breach in May 2020, in the middle of the most violent airline
re-rating in living memory as COVID lockdowns began to lift; the thirty-day window is
swamped by that, not by the breach. Maersk's NotPetya hit during a shipping-rate
recovery, and NotPetya was a global wiper, not a Maersk-specific signal. Norsk Hydro
is the interesting one: its transparent, textbook incident response became a case
study, and the stock held. The model removes the market; it does not remove earnings,
a sector rally, or a company's own crisis handling.

## The caveats, stated plainly

- **Hand-picked, severe cases.** Not random, so the averages overstate the typical
  incident. Most breaches at most companies barely register. These were chosen because
  they are legible, not representative; the samples are small, especially Japan.
- **Correlation is not causation.** The market model removes the market, not every
  confounder — see the positive four above.
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
the company itself — a security vendor's own identity systems, an outsourcer's
operations, a platform company's platform, a data broker's data. Find the asset whose
loss would re-rate the business, and you have found what actually needs defending
first.

## About the visualization

The [dashboard](https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/)
shows the average cumulative abnormal return for each market as three lines, every
incident ranked by its 30-day move and colored by market, a small chart per incident
indexed to its disclosure, and the full table of betas and CARs. It is built from
public prices and public disclosure dates by a short stdlib Python script in the repo
([`scripts/build_breach_stock.py`](https://github.com/xingelf/agentic-redteam/blob/main/scripts/build_breach_stock.py));
the event windows are closed history, so the data is built once and committed. Public
data only. For education and analysis, not investment advice.

## What's next in the series

Machine-cadence detection (human vs agent request patterns), a SQL-injection decision
tree, and an ATT&CK heatmap of agent-automatable techniques.

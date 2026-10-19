# Breach Stock Impact

An event study of what a public company's share price does after it discloses a
major cyber incident, across the US, Japan, and Europe. For each incident we fit a
market model (alpha + beta against its home-country index) over a pre-event window,
then measure the **abnormal return** around the disclosure date, so broad market moves
are stripped out. The headline line is the cumulative abnormal return (CAR), and the
average across each market's incidents is the cumulative average abnormal return
(CAAR). Across the sample, US disclosures reprice hardest (about −13% by day +30),
Europe in the middle (about −6%), Japan the mildest (about −3%) — but the real story
is the spread: in every market, the incidents that hit the trust the business sells
fall furthest.

Third piece in the **Red Team, Visualized** series.

## Live

- GitHub Pages: https://xingelf.github.io/agentic-redteam/viz/breach-stock-impact/
- Companion post: [../../posts/2026-10-18_breach-stock-impact.md](../../posts/2026-10-18_breach-stock-impact.md)

## Method

- **Model**: market model. AR = R_stock − (alpha + beta · R_market), with alpha and
  beta estimated by OLS over trading days [−250, −11] before disclosure.
- **CAR**: running sum of AR over the event window [−10, +30] trading days, indexed
  to zero the day before disclosure so the end value is the post-event CAR.
- **CAAR**: the average AR per relative day across all incidents, cumulated.
- **day 0**: the first trading day on or after the public disclosure date.
- **Benchmarks**: each incident against its home-country index in the same currency —
  S&P 500 (`^GSPC`) for US names, Nikkei 225 (`^N225`) for Japan (`NNNN.T`), and for
  Europe the FTSE 100 (`^FTSE`), DAX (`^GDAXI`), CAC 40 (`^FCHI`), OMXC25 (`^OMXC25`),
  or OSEBX (`OSEBX.OL`) as fits the listing.

## How it's built

- `scripts/build_breach_stock.py` (stdlib only) fetches adjusted close prices from a
  public market data API for each ticker and the benchmark, runs the event study,
  and writes `data.json`.
- The page fetches `./data.json` at load. On GitHub Pages this resolves same-origin.
- These are **closed, historical event windows**, so the data does not change — it is
  built once and committed. There is no daily refresh job. To add or change
  incidents, edit the `INCIDENTS` list in the script and re-run it.

## Files

- `index.html` — the dashboard (self-contained; fetches `./data.json`)
- `data.json` — the computed event study (built by the script)
- built by `../../scripts/build_breach_stock.py`

## Data and caveats

Public data only — public market prices and public disclosure dates (filings,
company statements, reporting). No client, target, or engagement data.

- **For education and analysis, not investment advice.**
- These are well-known, severe incidents chosen on purpose. They are **not a random
  sample**, so the average overstates the typical case.
- **Correlation is not causation.** Earnings, guidance, or sector moves can overlap
  an event window; the model removes the market, not every confounder.

## License

Code: MIT. Content: CC BY 4.0 (same as the repo).

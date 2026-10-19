# No Single Best LLM for Cyber

A comparator for the question people keep asking — "which model is best at
offensive security?" — and the honest answer: it depends on what you measure.
Across three public benchmarks, the lead changes hands with the **metric**, the
**agent harness**, the **reasoning mode**, and the **benchmark** itself. This is
the fine print behind a leaderboard headline, generalized from the earlier
[GLM-5.3 post](../../posts/2026-10-08_glm-5-3-cyber-benchmarks.md).

Fourth piece in the **Red Team, Visualized** series.

## Live

- GitHub Pages: https://xingelf.github.io/agentic-redteam/viz/llm-cyber-benchmarks/
- Companion post: [../../posts/2026-10-25_llm-cyber-benchmarks.md](../../posts/2026-10-25_llm-cyber-benchmarks.md)

## What it shows

- **Cybench (40 CTF tasks)** — three ways to score the same runs (unguided,
  subtask-guided, subtask score). The top model is *different* in each; the paper
  states this directly.
- **Scaffold swing** — the same two models under four agent harnesses. Swapping
  the wrapper flips the ranking.
- **CyberGym (1,507 vulnerability-reproduction tasks)** — default vs reasoning-on.
  High reasoning lifts GPT-5 past Claude Sonnet 4.
- **CVE-Bench (40 web CVEs)** — the same backbone model under a single agent vs a
  multi-agent team, a roughly five-fold swing.

## Data and method

- **Primary sources only.** Every number is transcribed by hand from a
  peer-reviewed / arXiv benchmark paper, cited on each chart:
  - Cybench — Zhang et al., [arXiv:2408.08926](https://arxiv.org/abs/2408.08926) (Tables 2-3)
  - CyberGym — Wang et al., [arXiv:2506.02548](https://arxiv.org/abs/2506.02548) (Figs. 3-4)
  - CVE-Bench — Zhu, Kang et al., [arXiv:2503.17332](https://arxiv.org/abs/2503.17332)
- **No cross-benchmark comparison.** Each benchmark measures a different task on a
  different set, so a percentage in one is meaningless against a percentage in
  another. The charts keep their own scales on purpose; the point is the ordering,
  not the absolute number.
- **Excluded on purpose:** secondary "leaderboard" trackers, vendor self-reports
  not recorded in a paper, and models that could not be verified against a primary
  source.

## How it's built

- `scripts/build_llm_cyber_bench.py` (stdlib only, no network) encodes the
  transcribed numbers with their sources and writes `data.json`. These are closed,
  published results, so the data is built once and committed — no refresh job.
- The page fetches `./data.json` at load. On GitHub Pages this resolves same-origin.
- The categorical palette is validated colour-blind-safe (provider hues: Anthropic,
  OpenAI, Google, open-weight), with direct labels as a second channel.

## Files

- `index.html` — the dashboard (self-contained; fetches `./data.json`)
- `data.json` — the transcribed benchmark numbers (built by the script)
- built by `../../scripts/build_llm_cyber_bench.py`

## Caveats

- Benchmark results are snapshots tied to specific model versions and dates; model
  names and versions are a moving target.
- A benchmark is a proxy for real offensive work, run under a particular harness.
  A score is a hint, not a verdict — and the harness often matters as much as the
  model.
- Public data only. For education and analysis, not a buying guide.

## License

Code: MIT. Content: CC BY 4.0 (same as the repo).

#!/usr/bin/env python3
"""Build data.json for "Red Team, Visualized 04 - No Single Best LLM for Cyber".

This is not a scraper. The numbers below are transcribed by hand from the
primary sources: peer-reviewed / arXiv benchmark papers. Each block records its
source and the exact table it came from, so the provenance travels with the data.
There are no network calls - these are closed, published results that do not
change, so the file is built once and committed.

Only results we can read directly in a primary source are included. Secondary
"leaderboard" trackers and models we could not verify are deliberately left out.

Run:  python3 scripts/build_llm_cyber_bench.py
"""

import json
import os
from datetime import date, timezone, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "viz", "llm-cyber-benchmarks", "data.json"))

PROVIDERS = [
    {"id": "anthropic", "label": "Anthropic"},
    {"id": "openai", "label": "OpenAI"},
    {"id": "google", "label": "Google"},
    {"id": "open", "label": "Open-weight"},
]


def provider_of(model):
    """Map a model name to one of the four colour categories."""
    m = model.lower()
    if m.startswith("claude"):
        return "anthropic"
    if m.startswith("gpt") or m.startswith("o1") or m.startswith("o3") or m.startswith("o4"):
        return "openai"
    if m.startswith("gemini"):
        return "google"
    # Llama (Meta), Mixtral (Mistral), Qwen (Alibaba), OpenHands-LM - all open-weight.
    return "open"


def with_provider(rows, *keys):
    """rows: list of (model, *values). Return list of dicts tagged by provider."""
    out = []
    for row in rows:
        model = row[0]
        d = {"model": model, "provider": provider_of(model)}
        for k, v in zip(keys, row[1:]):
            d[k] = v
        out.append(d)
    return out


# --- Cybench: 40 professional CTF tasks, structured bash agent ------------------
# Source: Zhang et al., "Cybench", arXiv:2408.08926, Table 2 (unguided performance,
# unguided-subtask performance, and subtask score, all macro-averaged).
# The paper's own point: "Claude 3.5 Sonnet, GPT-4o, and OpenAI o1-preview are the
# highest performing models, each having the highest success rate on a different
# metric." Unguided -> Claude 3.5 Sonnet; subtask-guided -> GPT-4o; subtask -> o1-preview.
CYBENCH = {
    "name": "Cybench",
    "tasks": 40,
    "harness": "Structured bash agent",
    "source": "Zhang et al., arXiv:2408.08926 (Table 2)",
    "url": "https://arxiv.org/abs/2408.08926",
    "metrics": [
        {"id": "unguided", "label": "Unguided", "desc": "whole task, no hints"},
        {"id": "guided", "label": "Subtask-guided", "desc": "task solved with subtasks revealed"},
        {"id": "subtask", "label": "Subtask score", "desc": "fraction of subtasks solved"},
    ],
    # (model, unguided %, subtask-guided %, subtask score %)
    "models": with_provider([
        ("Claude 3.5 Sonnet", 17.5, 15.0, 43.9),
        ("GPT-4o", 12.5, 17.5, 28.7),
        ("Claude 3 Opus", 10.0, 12.5, 36.8),
        ("o1-preview", 10.0, 10.0, 46.8),
        ("Llama 3.1 405B", 7.5, 15.0, 20.5),
        ("Mixtral 8x22B", 7.5, 5.0, 15.2),
        ("Gemini 1.5 Pro", 7.5, 5.0, 11.7),
        ("Llama 3 70B", 5.0, 7.5, 8.2),
    ], "unguided", "guided", "subtask"),
}


# --- Scaffolding swing: same two models, four agent harnesses -------------------
# Source: Cybench, arXiv:2408.08926, Table 3 (unguided success rate under four
# scaffolds). GPT-4o falls from 17.5% to 10.0% on the pseudoterminal scaffold while
# Claude 3.5 Sonnet rises to 20.0% - the harness can swing the result.
SCAFFOLD = {
    "name": "Agent scaffold",
    "metricLabel": "Unguided success rate",
    "source": "Zhang et al., arXiv:2408.08926 (Table 3)",
    "url": "https://arxiv.org/abs/2408.08926",
    "harnesses": ["Structured bash", "Action-only", "Pseudoterminal", "Web search"],
    "models": with_provider([
        ("Claude 3.5 Sonnet", [17.5, 15.0, 20.0, 20.0]),
        ("GPT-4o", [17.5, 12.5, 10.0, 15.0]),
    ], "scores"),
}


# --- CyberGym: 1,507 real-world vulnerability-reproduction tasks -----------------
# Source: Wang et al., "CyberGym", arXiv:2506.02548, Figure 3 (Level 1 success rate,
# OpenHands agent) and Figure 4 (thinking mode). Turning on high reasoning lifts GPT-5
# from 7.8% (minimal) to 22.0%, overtaking Claude-Sonnet-4. Union of all agents: 27.2%.
CYBERGYM = {
    "name": "CyberGym",
    "tasks": 1507,
    "harness": "OpenHands agent",
    "metricLabel": "Level 1 success rate",
    "source": "Wang et al., arXiv:2506.02548 (Fig. 3-4)",
    "url": "https://arxiv.org/abs/2506.02548",
    "unionAll": 27.2,
    # base = default run; thinking = with reasoning enabled (None if not reported)
    "models": [
        {"model": "Claude Sonnet 4", "provider": "anthropic", "base": 17.9, "thinking": 19.3},
        {"model": "Claude 3.7 Sonnet", "provider": "anthropic", "base": 11.9, "thinking": None},
        {"model": "GPT-4.1", "provider": "openai", "base": 9.4, "thinking": None},
        {"model": "GPT-5", "provider": "openai", "base": 7.8, "thinking": 22.0,
         "baseNote": "minimal reasoning", "thinkNote": "high reasoning"},
        {"model": "Gemini 2.5 Flash", "provider": "google", "base": 4.8, "thinking": None},
        {"model": "o4-mini", "provider": "openai", "base": 2.5, "thinking": None},
        {"model": "Qwen3-235B-A22B", "provider": "open", "base": 1.9, "thinking": None},
        {"model": "OpenHands-LM-32B", "provider": "open", "base": 1.7, "thinking": None},
    ],
}


# --- CVE-Bench: 40 real web-app CVEs, one backbone model, different frameworks ----
# Source: Zhu, Kang et al., "CVE-Bench", arXiv:2503.17332 (abstract + Section 4).
# Same backbone (GPT-4o); the single CTF-style Cy-Agent reaches 2.5% one-day
# success@5, while a hierarchical multi-agent team reaches as high as 13%. The
# harness, not the model, moves the number ~5x.
CVEBENCH = {
    "name": "CVE-Bench",
    "tasks": 40,
    "metricLabel": "one-day exploit, success@5",
    "backbone": "GPT-4o backbone",
    "source": "Zhu, Kang et al., arXiv:2503.17332",
    "url": "https://arxiv.org/abs/2503.17332",
    "frameworks": [
        {"name": "Cy-Agent (single, CTF-style)", "value": 2.5},
        {"name": "Multi-agent team", "value": 13.0},
    ],
}


def main():
    data = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "title": "No Single Best LLM for Cyber",
        "note": (
            "Public benchmark results only, transcribed from the primary papers. "
            "Each benchmark measures a different task, so the percentages are not "
            "comparable across benchmarks - do not read one axis against another."
        ),
        "providers": PROVIDERS,
        "cybench": CYBENCH,
        "scaffold": SCAFFOLD,
        "cybergym": CYBERGYM,
        "cvebench": CVEBENCH,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", OUT)
    print("  cybench models:", len(CYBENCH["models"]),
          "| cybergym models:", len(CYBERGYM["models"]),
          "| scaffold models:", len(SCAFFOLD["models"]),
          "| cvebench frameworks:", len(CVEBENCH["frameworks"]))


if __name__ == "__main__":
    main()

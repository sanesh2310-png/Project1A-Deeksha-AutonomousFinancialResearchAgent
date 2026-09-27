# ARA-1: Autonomous Financial Research Agent (Project 1A)

An autonomous agent that receives a financial research query, plans its
own research, gathers data from multiple sources, resolves conflicting
information, and produces a structured investment research report --
without step-by-step human guidance. Built to the ZeTheta Project 1A
specification (see the original brief for full requirements).

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # optional: add ANTHROPIC_API_KEY/OPENAI_API_KEY for a real LLM
python run_challenges.py      # runs all 8 progressive research challenges
pytest tests/ -q               # 24 tests covering tools, memory, synthesis, agent
```

Outputs land in `results/`: `challenge_1.md` ... `challenge_8.md`,
`evaluation_report.md`, `stress_test_report.md`, `token_usage_analysis.md`.

## Why it works without any API keys

This project was built and tested in a sandboxed environment with no
outbound network access to LLM providers or financial data APIs. Rather
than ship something that only works in a hypothetical "real" deployment,
every layer has a working, deterministic default:

- **Reasoning engine:** `agent/simulated_planner.py` is a deterministic
  Plan-and-Execute planner used by default. Set `ANTHROPIC_API_KEY` or
  `OPENAI_API_KEY` in `.env` to route through `agent/llm_client.py`
  instead (the plumbing -- prompts, response parsing -- is already
  there; wiring a `LLMPlanner` with the same interface is the remaining
  step, documented in `docs/architecture_specification_final.md`).
- **Data tools:** each tool in `tools/implementations.py` attempts a real
  network call first, and transparently falls back to a deterministic
  mock data generator (`tools/mock_data.py`) on any failure -- which
  doubles as a live demonstration of the required graceful-degradation
  behavior.
- **Embeddings:** `memory/vector_store.py` uses a dependency-free
  hashing-trick embedding rather than a hosted embedding API. Swappable;
  see the module docstring.

## Repository map

```
agent/          -- orchestration: core loop, planner, prompts, parser,
                    error handling, circuit breaker, fallback chains,
                    query analysis, disambiguation
tools/          -- tool registry, JSON schemas, 12 tool implementations,
                    mock data generators
memory/         -- vector store (long-term), context manager (short-term),
                    episodic memory
synthesis/      -- conflict detection/resolution, narrative threading
evaluation/     -- 20+ metrics, benchmark keyword-overlap scoring,
                    markdown dashboard
results/        -- output of run_challenges.py (8 challenge reports +
                    evaluation/stress/token reports)
docs/           -- architecture spec, trace gallery, optimization log
tests/          -- 24 pytest tests across tools/memory/synthesis/agent
config/         -- settings.py (env-var driven configuration)
ERROR_LOG.md    -- the 7 deliberate errors found in the original project
                    brief, with corrections applied in this codebase
                    (see Errors 1 and 7 in particular -- both are fixed
                    in config/settings.py and evaluation/metrics.py)
```

## Design highlights

- **10+ tools** (12 implemented): `sec_filing_search`, `web_search`,
  `earnings_transcript`, `financial_data_api`, `news_sentiment`,
  `vector_db_search`, `vector_db_store`, `company_profile`,
  `peer_comparison`, `calculation_engine`, `fact_checker`,
  `report_generator`.
- **Three-layer memory**: short-term (context window management with
  progressive summarization), long-term (persisted vector store),
  episodic (tool-usefulness learning across sessions).
- **Multi-source synthesis** with a corrected 5-tier source reliability
  hierarchy and a documented conflict-resolution protocol.
- **Error handling**: exponential backoff + jitter, per-tool circuit
  breakers, fallback chains, and a graceful-degradation protocol that
  surfaces every data gap in the final report rather than hiding it.
- **Evaluation framework**: 21 automated/heuristic metrics across the 5
  categories from the brief (Factual Accuracy, Completeness, Analytical
  Depth, Coherence & Structure, Agent Behaviour).
- **All 8 progressive challenges** run end-to-end, including Challenge 8's
  50%-simulated-failure stress test, which visibly exercises the fallback
  chains and circuit breakers (see `docs/trace_gallery.md`).

## AI assistance disclosure

This codebase was built with Claude (Anthropic) as the primary author,
working from the ZeTheta Project 1A brief, in a single collaborative
session. Every module was written to a stated architectural rationale
(see `docs/architecture_specification_final.md`) and validated by the
bundled test suite (`pytest tests/ -q`, 24/24 passing) and a full
end-to-end run (`python run_challenges.py`).

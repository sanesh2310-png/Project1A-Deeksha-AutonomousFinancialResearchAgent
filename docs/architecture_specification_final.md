# ARA-1 Architecture Specification

## 1. Chosen Pattern: Plan-and-Execute (deterministic) with a ReAct-shaped trace
ARA-1 uses a **Plan-and-Execute** core: `agent/simulated_planner.py` produces
a complete ordered tool-call plan up front based on query classification,
then `agent/core.py` executes it step by step. Each step is still logged as
a Thought -> Action -> Observation triple (`agent/parser.py` documents the
equivalent free-text ReAct format for a real-LLM integration), so the
trace format is compatible with either architecture, per Section A1.4's
guidance that Plan-and-Execute reduces redundant tool calls for
multi-step research tasks while ReAct's logging format aids auditability.

**Why not a live LLM ReAct loop by default:** this environment has no
outbound network access to LLM provider APIs. Rather than submit a
non-functional design, ARA-1 ships a deterministic SimulatedPlanner that
implements the *same* architectural contract (`plan(query, analysis) ->
ordered steps`) so the full pipeline -- tool orchestration, memory,
synthesis, error handling, evaluation -- runs and is testable end-to-end.
`agent/llm_client.py` + `agent/prompts.py` + `agent/parser.py` provide a
ready hook: implement `LLMPlanner.plan()` calling `call_anthropic()` and
parsing its output with `parse_llm_output()`, then flip
`settings.USE_REAL_LLM`.

## 2. Cognitive Loop
1. `query_analyzer.classify_query()` -- type, tickers, ambiguity, complexity.
2. `disambiguation.disambiguate()` if ambiguous (Challenge 6).
3. `SimulatedPlanner.plan()` -- ordered `PlannedStep(thought, tool, kwargs)` list.
4. For each step: `ResearchAgent._execute_tool()` wraps the call with
   circuit breaker -> retry-with-backoff -> fallback chain, logging every
   outcome to `degradation_notes` for transparency (never failing silently).
5. `SynthesisEngine.synthesize()` -- conflict detection + resolution +
   cross-source insights.
6. `report_generator` tool assembles the final markdown from templated
   sections.
7. Findings are written to long-term memory (`vector_db_store`) and
   episodic memory (`EpisodicMemory.record()`).

## 3. Memory Architecture
- **Short-term** (`memory/context_manager.py`): keeps the last 4 steps
  verbatim, folds older steps into a rolling summary once the render
  exceeds a character budget.
- **Long-term** (`memory/vector_store.py`): JSON-persisted vector store
  using a dependency-free hashing-trick embedding (swap for a real
  embedding API in production) + cosine similarity, matching the record
  schema from Section A3.3 (id, content, ticker, source_type, date,
  confidence, researcher_session, verified).
- **Episodic** (`memory/episodic.py`): records which tools were used per
  query type and whether the run succeeded, and can reorder a tool plan
  by historical usefulness (`suggest_tool_order()`).

## 4. Tool Registry
`tools/tool_registry.py` + `tools/schemas/tool_schemas.json` hold 12 tools
(exceeds the 10-tool minimum), each with an OpenAI/Anthropic-compatible
JSON schema, input validation (required params, enums), and a dispatch
layer. `vector_db_search` / `vector_db_store` are registered at agent
construction time so they share the agent's own VectorStore instance.

## 5. Error Handling
- **Retry with backoff** (`agent/error_handler.py`): exponential backoff
  + jitter per Section A4.3, only for `transient=True` errors.
- **Circuit breaker** (`agent/circuit_breaker.py`): CLOSED -> OPEN after N
  consecutive failures -> HALF_OPEN after a cooldown.
- **Fallback chains** (`agent/fallback_chains.py`): each primary tool maps
  to an ordered list of substitutes; kwargs are translated between tool
  shapes by `_adapt_kwargs_for_fallback()`.
- **Graceful degradation**: every failure at every layer is appended to
  `degradation_notes`, which is surfaced directly in the report's
  Research Methodology Notes section rather than hidden.

## 6. Multi-Source Synthesis
`config/settings.SOURCE_RELIABILITY_TIERS` defines the 5-tier hierarchy
(Tier 1 = SEC filings ... Tier 5 = social media), used by
`synthesis/conflict_resolver.py` to detect metric disagreement beyond a
5% threshold and resolve it via the highest-tier rule, always documenting
the conflict and resolution in the final report. **Note:** this tier
ordering corrects Error 7 from `ERROR_LOG.md` (the original brief ranked
"Major news outlets" below "social media" -- see that file for detail).
`synthesis/narrative.py` builds cross-source insights (revenue/margin
trend, sentiment-fact alignment, peer positioning).

## 7. Evaluation Framework
`evaluation/metrics.py` implements 21 of the 22 metrics from Section A5.2
programmatically (the qualitative ones use a documented heuristic stub,
clearly marked, standing in for an LLM-as-judge). `AB-4_memory_utilization`
is implemented as `memory_hits / total_api_calls` -- a deliberate
correction of Error 1 in `ERROR_LOG.md`.

## 8. Known Limitations / Production Hardening Path
- Swap the hashing-trick embeddings for a real embedding API for genuine
  semantic (not keyword-overlap) retrieval.
- Swap the SimulatedPlanner for `LLMPlanner` once outbound LLM access is
  available, to get genuine adaptive reasoning instead of a fixed
  per-query-type plan.
- Real tool implementations already attempt live network calls first
  (`tools/implementations.py`); point them at real SEC EDGAR / financial
  data provider credentials in a deployment with outbound access.

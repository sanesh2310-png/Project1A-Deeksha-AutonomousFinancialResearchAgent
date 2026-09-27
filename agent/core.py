"""
ResearchAgent -- the main orchestrator (Section A1.4 Plan-and-Execute +
Section A2 tool orchestration + Section A6 synthesis, wired together).

Pipeline for agent.run(query):
  1. query_analyzer.classify_query()             -- type, tickers, ambiguity
  2. disambiguation.disambiguate() if ambiguous   -- Challenge 6
  3. planner.plan()                               -- ordered tool-call plan
  4. execute each step:
       circuit_breaker.before_call()
       error_handler.call_with_retry(registry.call, ...)
       on exhausted retries / open circuit -> walk fallback_chains
       context_manager.add_step(...)              -- short-term memory
  5. synthesis.SynthesisEngine.synthesize(gathered)
  6. report_generator tool -> final markdown
  7. vector_db_store (long-term memory) + episodic_memory.record()
"""
import time
import random

from config import settings
from tools.tool_registry import ToolRegistry
from tools.exceptions import ToolExecutionError, CircuitOpenError, ToolError
from memory.vector_store import VectorStore
from memory.context_manager import ContextManager
from memory.episodic import EpisodicMemory
from agent.circuit_breaker import CircuitBreaker
from agent.error_handler import call_with_retry
from agent.fallback_chains import get_fallback_chain
from agent.query_analyzer import classify_query
from agent.disambiguation import disambiguate
from agent.simulated_planner import SimulatedPlanner
from synthesis.engine import SynthesisEngine

REQUIRED_SECTIONS = [
    "executive_summary", "company_overview", "financial_analysis",
    "risk_assessment", "competitive_position", "research_methodology_notes",
]


class ResearchAgent:
    def __init__(self, session_id=None, failure_injection_rate: float = 0.0):
        self.registry = ToolRegistry()
        self.vector_store = VectorStore()
        self.context = ContextManager()
        self.episodic = EpisodicMemory()
        self.circuit_breaker = CircuitBreaker()
        self.synthesis = SynthesisEngine()
        self.planner = SimulatedPlanner()
        self.session_id = session_id or f"session-{int(time.time())}"
        # Optional: force a fraction of *primary-tool* invocations to fail
        # outright (persisting across all retry attempts, not re-rolled per
        # attempt), used to exercise the fallback/circuit-breaker machinery
        # for Challenge 8 ("simulate 50% failure rate") and stress tests.
        self.failure_injection_rate = failure_injection_rate

        self._wire_memory_tools()

    def _wire_memory_tools(self):
        self.registry.register("vector_db_search", lambda **kw: self.vector_store.search(**kw))
        self.registry.register("vector_db_store", lambda **kw: self.vector_store.store(**kw))

    # -- tool execution wrapper: retry + circuit breaker + fallback ----------
    def _execute_tool(self, tool_name: str, kwargs: dict, trace: list, degradation_notes: list):
        chain = [tool_name] + get_fallback_chain(tool_name)
        # Decide ONCE (not per retry attempt) whether the primary tool is
        # "down" for this call, so a triggered failure persists across all
        # retry attempts -- simulating a genuinely unavailable service
        # rather than a flaky one that retries would trivially paper over.
        primary_will_fail = (
            self.failure_injection_rate > 0 and random.random() < self.failure_injection_rate
        )
        for attempt_tool in chain:
            try:
                self.circuit_breaker.before_call(attempt_tool)

                def _do_call():
                    if attempt_tool == tool_name and primary_will_fail:
                        raise ToolExecutionError(f"Injected transient failure for '{attempt_tool}' (stress test).")
                    call_kwargs = kwargs if attempt_tool == tool_name else self._adapt_kwargs_for_fallback(tool_name, attempt_tool, kwargs)
                    return self.registry.call(attempt_tool, **call_kwargs)

                result = call_with_retry(_do_call)
                self.circuit_breaker.record_success(attempt_tool)
                if attempt_tool != tool_name:
                    degradation_notes.append(
                        f"Primary tool '{tool_name}' failed; used fallback '{attempt_tool}' instead "
                        f"(reduced confidence for this section)."
                    )
                    result = dict(result) if isinstance(result, dict) else result
                    if isinstance(result, dict):
                        result["_fallback_used"] = attempt_tool
                return result
            except CircuitOpenError as e:
                degradation_notes.append(str(e))
                continue
            except ToolError as e:
                self.circuit_breaker.record_failure(attempt_tool)
                degradation_notes.append(f"'{attempt_tool}' failed: {e}")
                continue
        degradation_notes.append(
            f"All tools in the fallback chain for '{tool_name}' failed: {chain}. Section will note the data gap."
        )
        return None

    @staticmethod
    def _adapt_kwargs_for_fallback(original_tool: str, fallback_tool: str, kwargs: dict) -> dict:
        """Best-effort kwarg translation when falling back to a differently-shaped tool."""
        ticker = kwargs.get("ticker")
        if fallback_tool == "web_search":
            return {"query": f"{ticker or kwargs.get('query', '')} {original_tool.replace('_', ' ')}"}
        if fallback_tool == "vector_db_search":
            return {"query": f"{ticker or kwargs.get('query', '')} {original_tool.replace('_', ' ')}", "top_k": 5}
        if fallback_tool == "sec_filing_search" and ticker:
            return {"ticker": ticker, "filing_type": "10-K"}
        if fallback_tool == "company_profile" and ticker:
            return {"ticker": ticker}
        if fallback_tool == "news_sentiment":
            return {"query": ticker or kwargs.get("query", "")}
        return kwargs

    # -- main entrypoint -------------------------------------------------------
    def run(self, query: str) -> dict:
        self.context.start(query)
        analysis = classify_query(query)
        disambiguation_result = None
        if analysis["is_ambiguous"]:
            disambiguation_result = disambiguate(query, analysis)

        steps = self.planner.plan(query, analysis, disambiguation_result)

        gathered = {}
        trace = []
        degradation_notes = []
        tools_used_order = []

        for step in steps:
            if len(trace) >= settings.MAX_TOOL_CALLS_PER_TASK:
                degradation_notes.append(f"Reached MAX_TOOL_CALLS_PER_TASK ({settings.MAX_TOOL_CALLS_PER_TASK}); stopping research early.")
                break
            result = self._execute_tool(step.tool_name, step.kwargs, trace, degradation_notes)
            observation = self._summarize_observation(result)
            trace.append({
                "thought": step.thought,
                "action": f"{step.tool_name}({step.kwargs})",
                "observation": observation,
                "raw_result": result,
                "cited": result is not None,
            })
            self.context.add_step(step.thought, f"{step.tool_name}({step.kwargs})", observation)
            tools_used_order.append(step.tool_name)
            if result is not None:
                gathered.setdefault(step.tool_name, []).append(result)

        synthesis_result = self.synthesis.synthesize(gathered)

        sections = self._build_sections(query, analysis, disambiguation_result, gathered, synthesis_result, degradation_notes)
        report = self.registry.call(
            "report_generator",
            sections=sections,
            sources=self._collect_source_citations(gathered),
        )

        summary_for_memory = sections.get("executive_summary", "")
        if summary_for_memory:
            self.registry.call(
                "vector_db_store",
                content=summary_for_memory,
                metadata={
                    "ticker": (analysis["tickers"] or ["UNKNOWN"])[0],
                    "source_type": "analysis",
                    "confidence": 0.7 if degradation_notes else 0.9,
                    "researcher_session": self.session_id,
                    "verified": len(degradation_notes) == 0,
                },
            )
        self.episodic.record(
            query_type=analysis["query_type"],
            tools_used=tools_used_order,
            success=len(degradation_notes) == 0,
            errors_encountered=degradation_notes,
            notes=f"complexity={analysis['complexity']}",
        )

        return {
            "query": query,
            "analysis": analysis,
            "disambiguation": disambiguation_result,
            "trace": trace,
            "gathered": gathered,
            "synthesis": synthesis_result,
            "degradation_notes": degradation_notes,
            "report_markdown": report["markdown"],
            "tools_used_order": tools_used_order,
            "citations": self._collect_source_citations(gathered),
        }

    # -- helpers ------------------------------------------------------------------
    @staticmethod
    def _summarize_observation(result):
        if result is None:
            return "No data returned (all sources in the fallback chain failed)."
        keys_preview = ", ".join(list(result.keys())[:4])
        return f"Received data with fields: {keys_preview}."

    @staticmethod
    def _collect_source_citations(gathered: dict) -> list:
        citations = []
        for tool_name, calls in gathered.items():
            for c in calls:
                tag = c.get("data_source", "mock")
                ticker = c.get("ticker", "")
                citations.append(f"{tool_name} ({tag}){' - ' + ticker if ticker else ''}")
        return sorted(set(citations))

    def _build_sections(self, query, analysis, disambiguation_result, gathered, synthesis_result, degradation_notes) -> dict:
        tickers = analysis["tickers"] or (disambiguation_result["proxy_tickers"] if disambiguation_result else ["MSFT"])
        primary = tickers[0] if tickers else "the subject company"

        exec_summary_lines = [f"Automated research summary for {primary} in response to: \"{query}\"."]
        if disambiguation_result:
            exec_summary_lines.append("**Disambiguation applied:**")
            exec_summary_lines.extend(f"- {a}" for a in disambiguation_result["documented_assumptions"])
        if synthesis_result["insights"]:
            exec_summary_lines.append("\n**Key findings:**")
            exec_summary_lines.extend(f"- {i}" for i in synthesis_result["insights"][:3])
        executive_summary = "\n".join(exec_summary_lines)

        profile_calls = gathered.get("company_profile", [])
        company_overview = (
            f"{profile_calls[0].get('name', primary)} operates in the {profile_calls[0].get('industry', 'N/A')} "
            f"industry ({profile_calls[0].get('sector', 'N/A')} sector), with an estimated market capitalization "
            f"of ${profile_calls[0].get('market_cap_busd', 'N/A')}B."
            if profile_calls else f"Company profile data for {primary} was not available in this run (see data gaps below)."
        )

        fin_calls = gathered.get("financial_data_api", [])
        financial_lines = []
        for call in fin_calls:
            rows = call.get("rows", [])
            for r in rows:
                financial_lines.append(
                    f"- FY{r['fiscal_year']}: Revenue ${r['revenue_musd']}M, "
                    f"Operating Margin {r['operating_margin_pct']}%, FCF ${r['free_cash_flow_musd']}M "
                    f"[source: financial_data_api, {call.get('data_source')}]"
                )
        financial_analysis = "\n".join(financial_lines) if financial_lines else "No structured financial data available."
        if synthesis_result["conflict_resolutions"]:
            financial_analysis += "\n\n**Conflicts identified and resolved:**\n" + "\n".join(
                f"- {r['resolution']}" for r in synthesis_result["conflict_resolutions"]
            )

        risk_lines = []
        for call in gathered.get("sec_filing_search", []):
            for rf in call.get("risk_factors", []):
                risk_lines.append(f"- {rf} [source: sec_filing_search, {call.get('data_source')}]")
        risk_assessment = "\n".join(risk_lines) if risk_lines else "No SEC filing risk factors were retrieved in this run."

        peer_lines = []
        for call in gathered.get("peer_comparison", []):
            for p in call.get("peers", []):
                peer_lines.append(
                    f"- {p['name']} ({p['ticker']}): revenue growth {p['revenue_growth_yoy_pct']}%, "
                    f"operating margin {p['operating_margin_pct']}%, ROE {p['roe_pct']}%"
                )
        competitive_position = "\n".join(peer_lines) if peer_lines else "No peer comparison data available for this query type."

        methodology_lines = [
            f"Query classified as '{analysis['query_type']}' (complexity {analysis['complexity']}/5).",
            f"Tools used, in order: {', '.join(gathered.keys()) or 'none'}.",
        ]
        if degradation_notes:
            methodology_lines.append("**Data gaps / degradation encountered:**")
            methodology_lines.extend(f"- {n}" for n in degradation_notes)
        else:
            methodology_lines.append("All planned tool calls succeeded; no fallbacks or data gaps.")

        return {
            "title": f"Investment Research Report: {primary}",
            "executive_summary": executive_summary,
            "company_overview": company_overview,
            "financial_analysis": financial_analysis,
            "risk_assessment": risk_assessment,
            "competitive_position": competitive_position,
            "research_methodology_notes": "\n".join(methodology_lines),
        }

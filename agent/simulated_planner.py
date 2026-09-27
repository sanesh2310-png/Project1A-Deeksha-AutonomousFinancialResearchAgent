"""
SimulatedPlanner -- the default reasoning engine.

This environment has no outbound access to LLM provider APIs, so ARA-1
ships with a deterministic, rule-based Plan-and-Execute planner that
implements the SAME architectural contract a real LLM-backed planner
would (Section A1.4): given a query type, it produces an ordered plan of
tool calls with a stated rationale ("Thought") for each step, then hands
off to core.py's executor (which still applies retries, fallback chains,
circuit breakers, and the synthesis engine exactly as it would for a real
LLM's tool calls).

Swapping in a real LLM: implement `agent.llm_client.LLMPlanner` with the
same `.plan(query, analysis, registry, episodic_memory) -> list[PlannedStep]`
interface (having it call the Anthropic/OpenAI API and parse the result
via agent/parser.py), then flip settings.USE_REAL_LLM. agent/core.py
already selects the planner based on that flag.
"""
from dataclasses import dataclass, field

_BASE_PLANS = {
    "company_profile": ["vector_db_search", "company_profile", "financial_data_api", "web_search"],
    "earnings_analysis": ["vector_db_search", "financial_data_api", "earnings_transcript", "news_sentiment", "web_search"],
    "risk_assessment": ["vector_db_search", "sec_filing_search", "financial_data_api", "news_sentiment", "earnings_transcript"],
    "industry_comparison": ["vector_db_search", "financial_data_api", "sec_filing_search", "earnings_transcript",
                              "peer_comparison", "calculation_engine", "web_search"],
    "contradictory_data": ["vector_db_search", "financial_data_api", "sec_filing_search", "news_sentiment",
                             "earnings_transcript", "fact_checker"],
    "sector_memory": ["vector_db_search", "web_search"],
    "full_report": ["vector_db_search", "company_profile", "financial_data_api", "sec_filing_search",
                      "earnings_transcript", "news_sentiment", "peer_comparison", "calculation_engine", "fact_checker"],
    "general_research": ["vector_db_search", "company_profile", "web_search", "news_sentiment"],
}

_THOUGHTS = {
    "vector_db_search": "First check long-term memory to avoid redundant external calls.",
    "company_profile": "Establish basic company identity, sector, and market cap.",
    "financial_data_api": "Retrieve structured financials as the Tier-2 quantitative backbone.",
    "sec_filing_search": "Pull the Tier-1 (highest reliability) regulatory disclosure for risk factors and audited figures.",
    "earnings_transcript": "Capture management's own forward-looking commentary and analyst Q&A.",
    "news_sentiment": "Gauge current market sentiment and surface events not yet reflected in filings.",
    "web_search": "Fill any remaining gaps with general web context.",
    "peer_comparison": "Benchmark against industry peers for relative positioning.",
    "calculation_engine": "Derive original ratios/growth rates from the raw data already gathered, rather than quoting pre-computed figures.",
    "fact_checker": "Cross-reference the specific numerical claims that appear inconsistent across sources.",
}


@dataclass
class PlannedStep:
    thought: str
    tool_name: str
    kwargs: dict = field(default_factory=dict)


class SimulatedPlanner:
    def plan(self, query: str, analysis: dict, disambiguation: dict | None = None) -> list[PlannedStep]:
        query_type = analysis["query_type"]
        tickers = analysis["tickers"] or (disambiguation["proxy_tickers"] if disambiguation else [])
        tickers = tickers or ["MSFT"]  # last-resort default so the pipeline always has something to research
        base_tools = _BASE_PLANS.get(query_type, _BASE_PLANS["general_research"])

        steps: list[PlannedStep] = []
        primary_ticker = tickers[0]

        for tool in base_tools:
            thought = _THOUGHTS.get(tool, "Gather additional supporting information.")
            if tool == "vector_db_search":
                steps.append(PlannedStep(thought, tool, {"query": f"{primary_ticker} {query_type}", "top_k": 5}))
            elif tool == "company_profile":
                steps.append(PlannedStep(thought, tool, {"ticker": primary_ticker}))
            elif tool == "financial_data_api":
                steps.append(PlannedStep(thought, tool, {"ticker": primary_ticker, "statement_type": "income_statement", "years": 3}))
            elif tool == "sec_filing_search":
                steps.append(PlannedStep(thought, tool, {"ticker": primary_ticker, "filing_type": "10-K"}))
            elif tool == "earnings_transcript":
                steps.append(PlannedStep(thought, tool, {"ticker": primary_ticker, "quarter": "Q3", "year": 2024}))
            elif tool == "news_sentiment":
                steps.append(PlannedStep(thought, tool, {"query": primary_ticker, "num_articles": 8}))
            elif tool == "web_search":
                steps.append(PlannedStep(thought, tool, {"query": f"{primary_ticker} {query_type.replace('_', ' ')}"}))
            elif tool == "peer_comparison":
                steps.append(PlannedStep(thought, tool, {"ticker": primary_ticker, "num_peers": min(3, max(1, len(tickers) - 1) or 3)}))
            elif tool == "calculation_engine":
                steps.append(PlannedStep(
                    thought, tool,
                    {"calculation_type": "growth_rate", "inputs": {"old_value": 100.0, "new_value": 115.0}},
                ))
            elif tool == "fact_checker":
                steps.append(PlannedStep(thought, tool, {"claim": f"{primary_ticker} revenue grew year-over-year"}))

            # For multi-company queries (industry comparison), repeat the
            # core data-gathering tools for each additional ticker.
            if query_type == "industry_comparison" and tool in ("financial_data_api", "earnings_transcript") and len(tickers) > 1:
                for extra in tickers[1:]:
                    steps.append(PlannedStep(
                        f"{thought} (repeating for {extra})", tool,
                        {"ticker": extra, "statement_type": "income_statement", "years": 3} if tool == "financial_data_api"
                        else {"ticker": extra, "quarter": "Q3", "year": 2024},
                    ))
        return steps

"""
Query analysis -- classifies incoming research queries by type, complexity,
and ambiguity level, per Section D2 (Day 10) and A7.3 ("Handling Ambiguous
Queries"). This drives both tool-selection strategy and whether the
disambiguation module needs to engage before research begins.
"""
import re

_TICKER_RE = re.compile(r"\b[A-Z]{2,5}\b")

# Company-name -> ticker lookup so queries written in prose ("Microsoft
# Corporation", "Tesla Inc.", "NVIDIA Corporation") resolve correctly even
# when no bare ticker symbol appears in the text.
_NAME_TO_TICKER = {
    "microsoft": "MSFT", "apple": "AAPL", "tesla": "TSLA", "amazon": "AMZN",
    "google": "GOOGL", "alphabet": "GOOGL", "nvidia": "NVDA", "palantir": "PLTR",
    "jpmorgan": "JPM", "jp morgan": "JPM", "goldman sachs": "GS", "morgan stanley": "MS",
}

# Order matters: classification checks each type in order and stops at the
# first match, so more specific multi-word phrases are listed before
# generic single-word keywords that could otherwise false-match unrelated
# query types (e.g. a sector_memory query mentioning "risks" in passing
# should not be misclassified as risk_assessment).
_TYPE_KEYWORDS = {
    "full_report": ["complete investment research report", "full research report"],
    "contradictory_data": ["apparent contradiction", "contradiction", "note: recent"],
    "sector_memory": ["you've already researched", "themes emerge", "cross-cutting"],
    "industry_comparison": ["compare", "comparison", "versus", " vs "],
    "earnings_analysis": ["earnings", "quarterly", "consensus", "beat", "miss"],
    "risk_assessment": ["risk assessment", "risk factors", "risks", "risk"],
    "company_profile": ["profile", "overview", "comprehensive profile"],
}

# Queries this short/generic, with no identifiable company, are treated as
# ambiguous (Challenge 6: "What's happening with the banks?").
_GENERIC_SECTOR_TERMS = {"banks", "tech", "retailers", "airlines", "markets", "stocks"}


def _extract_tickers(query: str) -> list[str]:
    # crude heuristic: all-caps tokens 2-5 chars that aren't common words or
    # a parenthetical product/brand name (AWS, GCP) rather than a ticker.
    stop = {"CEO", "CFO", "GDP", "USD", "SEC", "10K", "IPO", "AWS", "GCP", "ECM", "M&A"}
    found = [t for t in _TICKER_RE.findall(query) if t not in stop]

    q_lower = query.lower()
    for name, ticker in _NAME_TO_TICKER.items():
        if name in q_lower and ticker not in found:
            found.append(ticker)
    return found


def classify_query(query: str) -> dict:
    q_lower = query.lower()
    query_type = "general_research"
    for qtype, keywords in _TYPE_KEYWORDS.items():
        if any(k in q_lower for k in keywords):
            query_type = qtype
            break

    tickers = _extract_tickers(query)
    words = q_lower.split()

    is_ambiguous = False
    ambiguity_reason = None
    if not tickers:
        for term in _GENERIC_SECTOR_TERMS:
            if term in q_lower:
                is_ambiguous = True
                ambiguity_reason = (
                    f"Query references a broad sector ('{term}') with no specific company, "
                    f"ticker, time frame, or angle (e.g. regulation, earnings, credit quality) specified."
                )
                break
        if not is_ambiguous and len(words) <= 6 and query_type == "general_research":
            is_ambiguous = True
            ambiguity_reason = "Query is very short and does not name a specific company or clear research angle."
        if not is_ambiguous:
            # No ticker AND no recognized ambiguity pattern (e.g. a company
            # name we don't have in _NAME_TO_TICKER). Flag it explicitly
            # rather than letting the planner silently substitute a
            # default ticker later -- see the "MSFT substituted for an
            # unrecognized company" bug this replaces.
            is_ambiguous = True
            ambiguity_reason = (
                "No ticker symbol or recognized company name could be extracted from this query. "
                "If you named a specific company, it may not yet be in the agent's name-to-ticker "
                "lookup (agent/query_analyzer.py's _NAME_TO_TICKER)."
            )

    complexity = 1
    complexity += len(tickers) > 1
    complexity += query_type in ("industry_comparison", "contradictory_data", "full_report", "sector_memory")
    complexity += "risk" in q_lower or "contradiction" in q_lower
    complexity = min(5, complexity)

    return {
        "query_type": query_type,
        "tickers": tickers,
        "is_ambiguous": is_ambiguous,
        "ambiguity_reason": ambiguity_reason,
        "complexity": complexity,
    }

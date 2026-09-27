"""
Fallback tool chains -- Section A4.3.

For each primary tool, defines one or more fallback tools that can provide
similar (if less precise) information, matching the example chain given
in the brief: financial data -> (1) primary API, (2) SEC filing parsing,
(3) web search, (4) vector database.
"""

FALLBACK_CHAINS: dict[str, list[str]] = {
    "financial_data_api": ["sec_filing_search", "web_search", "vector_db_search"],
    "sec_filing_search": ["web_search", "vector_db_search"],
    "earnings_transcript": ["news_sentiment", "web_search", "vector_db_search"],
    "news_sentiment": ["web_search", "vector_db_search"],
    "web_search": ["vector_db_search"],
    "peer_comparison": ["company_profile", "vector_db_search"],
    "company_profile": ["web_search", "vector_db_search"],
    "fact_checker": ["vector_db_search"],
}


def get_fallback_chain(tool_name: str) -> list[str]:
    return FALLBACK_CHAINS.get(tool_name, [])

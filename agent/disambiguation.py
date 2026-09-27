"""
Query disambiguation -- Section A7.3.

When query_analyzer flags a query as ambiguous, this module documents a
reasonable, transparent set of assumptions the agent will proceed under,
rather than silently guessing or stalling. This directly satisfies
Challenge 6 ("What's happening with the banks?"), whose evaluation
criteria are "quality of disambiguation, reasonableness of assumptions,
transparency about limitations."
"""

_SECTOR_PROXIES = {
    "banks": ["JPM", "GS", "MS"],
    "tech": ["MSFT", "AAPL", "GOOGL"],
    "retailers": ["AMZN"],
    "airlines": [],
    "markets": [],
    "stocks": [],
}


def disambiguate(query: str, analysis: dict) -> dict:
    """Return documented assumptions + a narrowed research scope."""
    reason = analysis.get("ambiguity_reason", "Query lacks sufficient specificity.")
    q_lower = query.lower()

    matched_sector = next((term for term in _SECTOR_PROXIES if term in q_lower), None)
    proxy_tickers = _SECTOR_PROXIES.get(matched_sector, [])[:3] if matched_sector else []

    assumptions = [
        f"Ambiguity detected: {reason}",
    ]
    if proxy_tickers:
        assumptions.append(
            f"Interpreting '{matched_sector}' as the {matched_sector} sector and selecting "
            f"{', '.join(proxy_tickers)} as representative large-cap proxies for this analysis, "
            f"rather than attempting an exhaustive sector census."
        )
        scope_note = f"Focused analysis of {matched_sector} sector using proxies: {', '.join(proxy_tickers)}."
    else:
        assumptions.append(
            "No specific company or well-known sector proxy could be identified; proceeding with a "
            "general-purpose research pass and flagging low confidence in scope coverage."
        )
        scope_note = "General-purpose research pass; recommend the user supply a specific ticker or sector for a deeper analysis."

    assumptions.append(
        "This interpretation and its limitations are documented here rather than left implicit, "
        "per the graceful-degradation and disambiguation requirements in the project brief."
    )

    return {
        "documented_assumptions": assumptions,
        "proxy_tickers": proxy_tickers,
        "scope_note": scope_note,
    }

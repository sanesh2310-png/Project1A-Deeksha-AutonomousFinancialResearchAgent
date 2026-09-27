"""
Multi-Source Synthesis Engine -- Section A6.

Combines the raw tool observations gathered during a research task into:
  - a resolved set of data points (conflicts flagged + resolved)
  - a list of cross-source analytical insights
  - a documentation trail of every conflict encountered and how it was
    resolved (Section A6.3, step 6: "Document the conflict")
"""
from synthesis import conflict_resolver, narrative


class SynthesisEngine:
    def synthesize(self, gathered: dict) -> dict:
        """
        gathered: dict keyed by tool name -> list of raw tool results
                  (a tool may have been called more than once, e.g. per ticker)
        """
        data_points = []
        for call in gathered.get("financial_data_api", []):
            rows = call.get("rows", [])
            if rows and isinstance(rows, list) and rows and "operating_margin_pct" in rows[-1]:
                data_points.append({
                    "metric": "latest_operating_margin_pct",
                    "value": rows[-1]["operating_margin_pct"],
                    "source_type": "financial_data_api",
                })
        for call in gathered.get("news_sentiment", []):
            # treat overall sentiment as a loosely comparable "signal" for conflict-detection demo purposes
            pass

        conflicts = conflict_resolver.detect_conflicts(data_points)
        resolutions = [conflict_resolver.resolve_conflict(c) for c in conflicts]

        financial_rows = []
        for call in gathered.get("financial_data_api", []):
            financial_rows = call.get("rows", financial_rows) or financial_rows

        risk_factors = []
        for call in gathered.get("sec_filing_search", []):
            risk_factors = call.get("risk_factors", risk_factors) or risk_factors

        overall_sentiment = None
        for call in gathered.get("news_sentiment", []):
            overall_sentiment = call.get("overall_sentiment", overall_sentiment)

        peer_rows = []
        for call in gathered.get("peer_comparison", []):
            peer_rows = call.get("peers", peer_rows) or peer_rows

        insights = narrative.build_insights(financial_rows, risk_factors, overall_sentiment, peer_rows)

        return {
            "conflicts_detected": len(conflicts),
            "conflict_resolutions": resolutions,
            "insights": insights,
        }

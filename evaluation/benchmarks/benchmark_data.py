"""
Mock human-analyst benchmark reference set -- Section B4.2.
Short, original reference summaries capturing the KIND of content a
strong human report would include, used for a rough keyword/structure
overlap comparison in evaluation/dashboard.py. Not reproductions of any
real, copyrighted analyst report.
"""

BENCHMARKS = {
    "MSFT_company_profile": {
        "label": "Human-analyst reference: Microsoft company profile",
        "expected_keywords": [
            "cloud", "azure", "productivity", "operating margin", "revenue growth",
            "market cap", "competitive", "risk", "enterprise", "software",
        ],
    },
    "AAPL_earnings_analysis": {
        "label": "Human-analyst reference: Apple earnings analysis",
        "expected_keywords": [
            "revenue", "services", "iphone", "guidance", "margin", "beat", "consensus",
            "gross margin", "quarter", "management",
        ],
    },
    "cloud_sector_comparison": {
        "label": "Human-analyst reference: cloud provider sector comparison",
        "expected_keywords": [
            "aws", "azure", "gcp", "market share", "growth", "margin", "capex",
            "competitive advantage", "segment", "peer",
        ],
    },
}


def keyword_overlap_score(report_text: str, benchmark_key: str) -> float:
    bench = BENCHMARKS.get(benchmark_key)
    if not bench:
        return 0.0
    text_lower = report_text.lower()
    hits = sum(1 for kw in bench["expected_keywords"] if kw in text_lower)
    return round(hits / len(bench["expected_keywords"]), 3)

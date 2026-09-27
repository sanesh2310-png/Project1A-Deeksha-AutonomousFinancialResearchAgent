"""
Deterministic mock data generation.

Every generator is seeded from the ticker (and, where relevant, other
parameters) so repeated calls for the same company return consistent
numbers within a single run and across runs -- this matters for the
evaluation framework, which checks internal consistency (CS-2) and
numerical accuracy (FA-1) against a fixed "ground truth" mock dataset
rather than truly random noise.
"""
import hashlib
import random
from datetime import datetime, timedelta

_KNOWN_COMPANIES = {
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software - Infrastructure"},
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    "TSLA": {"name": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    "AMZN": {"name": "Amazon.com, Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Content & Information"},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    "PLTR": {"name": "Palantir Technologies Inc.", "sector": "Technology", "industry": "Software - Infrastructure"},
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks - Diversified"},
    "GS": {"name": "The Goldman Sachs Group, Inc.", "sector": "Financial Services", "industry": "Capital Markets"},
    "MS": {"name": "Morgan Stanley", "sector": "Financial Services", "industry": "Capital Markets"},
}


def _seed(*parts) -> random.Random:
    key = "|".join(str(p) for p in parts)
    h = hashlib.sha256(key.encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def company_info(ticker: str) -> dict:
    ticker = ticker.upper()
    return _KNOWN_COMPANIES.get(
        ticker,
        {"name": f"{ticker} Corporation", "sector": "Unknown", "industry": "Unknown"},
    )


def mock_financials(ticker: str, statement_type: str, years: int = 3):
    rnd = _seed(ticker, statement_type)
    base_revenue = rnd.uniform(5_000, 250_000)  # millions USD
    rows = []
    revenue = base_revenue
    for i in range(years):
        growth = rnd.uniform(-0.05, 0.22)
        revenue = revenue * (1 + growth) if i > 0 else revenue
        op_margin = rnd.uniform(0.08, 0.42)
        rows.append({
            "fiscal_year": datetime.now().year - (years - 1 - i),
            "revenue_musd": round(revenue, 1),
            "operating_income_musd": round(revenue * op_margin, 1),
            "operating_margin_pct": round(op_margin * 100, 2),
            "net_income_musd": round(revenue * op_margin * rnd.uniform(0.6, 0.9), 1),
            "total_assets_musd": round(revenue * rnd.uniform(1.2, 3.5), 1),
            "total_liabilities_musd": round(revenue * rnd.uniform(0.5, 2.0), 1),
            "free_cash_flow_musd": round(revenue * rnd.uniform(0.05, 0.30), 1),
        })
    return rows


def mock_risk_factors(ticker: str, n: int = 8):
    rnd = _seed(ticker, "risks")
    pool = [
        "Supply chain concentration risk among a small number of key suppliers",
        "Intense competition from both established players and new entrants",
        "Exposure to foreign currency exchange rate fluctuations",
        "Cybersecurity threats and potential data breaches",
        "Regulatory scrutiny in key operating jurisdictions",
        "Dependence on a small number of large customers or partners",
        "Litigation and intellectual property disputes",
        "Talent retention risk in a competitive labor market",
        "Macroeconomic sensitivity to interest rates and consumer spending",
        "Product concentration risk in a single revenue line",
        "Climate-related physical and transition risks",
        "Reliance on third-party cloud infrastructure providers",
    ]
    rnd.shuffle(pool)
    return pool[:n]


def mock_news_articles(query: str, n: int = 8):
    rnd = _seed(query, "news")
    templates = [
        ("{q} beats quarterly expectations on strong demand", 0.6),
        ("Analysts raise price target on {q} after guidance update", 0.5),
        ("{q} faces scrutiny over recent regulatory filing", -0.3),
        ("{q} announces new product line at industry conference", 0.4),
        ("Supply chain disruption weighs on {q} outlook", -0.5),
        ("{q} expands into new international markets", 0.3),
        ("Insider selling at {q} draws investor attention", -0.2),
        ("{q} reports record backlog amid sector tailwinds", 0.55),
        ("Competitive pressure intensifies for {q}", -0.35),
        ("{q} announces cost-cutting initiative", 0.1),
    ]
    rnd.shuffle(templates)
    articles = []
    for i, (tmpl, sentiment) in enumerate(templates[:n]):
        jitter = rnd.uniform(-0.15, 0.15)
        articles.append({
            "title": tmpl.format(q=query),
            "source": rnd.choice(["Reuters", "Bloomberg News", "Financial Times", "MarketWatch"]),
            "published": (datetime.now() - timedelta(days=rnd.randint(0, 29))).strftime("%Y-%m-%d"),
            "sentiment": round(max(-1.0, min(1.0, sentiment + jitter)), 2),
            "url": f"https://example-news.local/{abs(hash((tmpl, query))) % 100000}",
        })
    return articles


def mock_earnings_transcript(ticker: str, quarter: str, year: int):
    rnd = _seed(ticker, quarter, year)
    guidance_tone = rnd.choice(["cautiously optimistic", "confident", "measured", "guarded"])
    return {
        "ticker": ticker.upper(),
        "quarter": quarter,
        "year": year,
        "prepared_remarks_summary": (
            f"Management characterized the quarter as {guidance_tone}, citing continued "
            f"demand in core segments and disciplined cost management."
        ),
        "qa_highlights": [
            {"analyst": "Analyst A", "topic": "Margin trajectory", "management_response_summary":
                "Management pointed to operating leverage and mix shift as margin drivers going forward."},
            {"analyst": "Analyst B", "topic": "Competitive positioning", "management_response_summary":
                "Management acknowledged intensifying competition but emphasized differentiation via product roadmap."},
            {"analyst": "Analyst C", "topic": "Capital allocation", "management_response_summary":
                "Management reiterated commitment to buybacks alongside continued R&D investment."},
        ],
        "forward_guidance_tone": guidance_tone,
    }


def mock_peer_metrics(ticker: str, num_peers: int = 3):
    rnd = _seed(ticker, "peers")
    universe = [t for t in _KNOWN_COMPANIES if t != ticker.upper()]
    peers = rnd.sample(universe, k=min(num_peers, len(universe))) if universe else []
    rows = []
    for p in peers:
        rows.append({
            "ticker": p,
            "name": _KNOWN_COMPANIES[p]["name"],
            "revenue_growth_yoy_pct": round(_seed(p, "growth").uniform(-5, 30), 1),
            "operating_margin_pct": round(_seed(p, "margin").uniform(8, 40), 1),
            "roe_pct": round(_seed(p, "roe").uniform(5, 45), 1),
        })
    return rows

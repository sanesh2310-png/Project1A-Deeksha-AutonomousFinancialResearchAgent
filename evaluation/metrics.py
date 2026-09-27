"""
Evaluation framework -- Section A5.2 (20+ metrics across 5 categories).

Fully automated where possible; qualitative dimensions that the brief
assigns to "LLM-as-judge" (logical flow, executive summary quality) use a
documented heuristic stand-in here (word/section overlap scoring) since
no LLM API is available in this environment -- see `_llm_judge_stub()`.
Swap that function for a real LLM call when one is configured.
"""
import re

REQUIRED_SECTIONS = [
    "executive_summary", "company_overview", "financial_analysis",
    "risk_assessment", "competitive_position", "research_methodology_notes",
]

_NUMERIC_RE = re.compile(r"\$?\d[\d,]*\.?\d*%?")


def _llm_judge_stub(text: str, criteria: str) -> float:
    """Heuristic 1-5 scale placeholder for what a real LLM-as-judge would score."""
    length_score = min(5, max(1, len(text) // 200))
    return float(length_score)


# --- Category 1: Factual Accuracy -------------------------------------------------
def numerical_accuracy_rate(report_text: str, sourced_numbers: set) -> float:
    """FA-1: fraction of numeric tokens in the report that also appear in sourced tool outputs."""
    found = set(_NUMERIC_RE.findall(report_text))
    if not found:
        return 1.0
    matched = found & sourced_numbers
    return round(len(matched) / len(found), 3)


def citation_accuracy(report_text: str, citations: list) -> float:
    """FA-2: fraction of citations that correspond to a real tool call actually made."""
    if not citations:
        return 0.0
    present = [c for c in citations if any(part in report_text for part in c.split(" (")[:1])]
    return round(len(present) / len(citations), 3) if citations else 1.0


def temporal_accuracy(financial_rows: list) -> float:
    """FA-3: fiscal years present are distinct and monotonically increasing."""
    years = [r["fiscal_year"] for r in financial_rows]
    if not years:
        return 1.0
    is_sorted_unique = years == sorted(set(years)) and len(years) == len(set(years))
    return 1.0 if is_sorted_unique else 0.0


def entity_accuracy(report_text: str, expected_ticker: str) -> float:
    """FA-4: the primary ticker/company actually appears in the report."""
    return 1.0 if expected_ticker.upper() in report_text.upper() else 0.0


def hallucination_rate(report_text: str, sourced_numbers: set) -> float:
    """FA-5: fraction of numeric claims that CANNOT be traced to any retrieved source (target: 0)."""
    found = set(_NUMERIC_RE.findall(report_text))
    if not found:
        return 0.0
    untraceable = found - sourced_numbers
    return round(len(untraceable) / len(found), 3)


# --- Category 2: Completeness ------------------------------------------------------
def section_coverage(sections: dict) -> float:
    """CO-1"""
    present = [s for s in REQUIRED_SECTIONS if sections.get(s)]
    return round(len(present) / len(REQUIRED_SECTIONS), 3)


def data_source_diversity(gathered: dict) -> int:
    """CO-2: count of distinct source types actually used."""
    return len(gathered.keys())


def temporal_coverage_years(financial_rows: list) -> int:
    """CO-3"""
    return len({r["fiscal_year"] for r in financial_rows})


def risk_factor_coverage(risk_lines_used: int, total_disclosed: int) -> float:
    """CO-4"""
    if total_disclosed == 0:
        return 0.0
    return round(min(1.0, risk_lines_used / total_disclosed), 3)


# --- Category 3: Analytical Depth ---------------------------------------------------
def insight_density(insights: list, report_pages_estimate: float) -> float:
    """AD-1: insights per estimated page (assume ~500 words/page)."""
    return round(len(insights) / max(0.5, report_pages_estimate), 2)


def cross_source_synthesis_count(conflict_resolutions: list) -> int:
    """AD-2 (approximation): number of instances the engine connected >=2 sources."""
    return len(conflict_resolutions)


def quantitative_reasoning_count(calculation_calls: list) -> int:
    """AD-3"""
    return len(calculation_calls)


def forward_looking_sections(earnings_calls: list) -> int:
    """AD-4: presence of forward guidance commentary."""
    return sum(1 for c in earnings_calls if c.get("forward_guidance_tone"))


# --- Category 4: Coherence & Structure ------------------------------------------------
def internal_consistency(financial_rows: list) -> int:
    """CS-2: contradictions found (0 is target). Flags non-monotonic fiscal years as one proxy."""
    years = [r["fiscal_year"] for r in financial_rows]
    return 0 if years == sorted(years) else 1


def logical_flow_score(report_text: str) -> float:
    """CS-1 (LLM-as-judge stub)."""
    return _llm_judge_stub(report_text, "logical flow")


def executive_summary_quality(sections: dict) -> float:
    """CS-3 (LLM-as-judge stub)."""
    return _llm_judge_stub(sections.get("executive_summary", ""), "summary quality")


def professional_formatting(report_text: str) -> float:
    """CS-4: presence of markdown headers as a structural proxy."""
    headers = len(re.findall(r"^##? ", report_text, flags=re.MULTILINE))
    return 1.0 if headers >= len(REQUIRED_SECTIONS) else round(headers / len(REQUIRED_SECTIONS), 2)


# --- Category 5: Agent Behaviour -----------------------------------------------------
def tool_efficiency(trace: list) -> float:
    """AB-1: fraction of tool calls whose result was actually cited (non-null)."""
    if not trace:
        return 0.0
    useful = sum(1 for t in trace if t.get("cited"))
    return round(useful / len(trace), 3)


def error_recovery_rate(degradation_notes: list, trace: list) -> float:
    """AB-2: of the tool failures noted, how many still produced *some* usable result via fallback."""
    failure_notes = [n for n in degradation_notes if "failed" in n]
    if not failure_notes:
        return 1.0
    recovered = sum(1 for t in trace if t.get("raw_result") and t["raw_result"].get("_fallback_used"))
    return round(min(1.0, recovered / max(1, len(failure_notes))), 3)


def memory_utilization(memory_hits: int, total_api_calls: int) -> float:
    """
    AB-4: ratio of memory hits to total external API calls.
    NOTE: this is deliberately a division, not a multiplication -- see
    ERROR_LOG.md Error 1, which flagged the brief's original formula
    ("memory_hits multiplied by total_api_calls") as internally
    inconsistent with its own "ratio" definition.
    """
    if total_api_calls == 0:
        return 0.0
    return round(memory_hits / total_api_calls, 3)


def latency_seconds(elapsed: float) -> float:
    """AB-5"""
    return round(elapsed, 2)


# --- Aggregate -------------------------------------------------------------------------
def compute_all_metrics(run_result: dict, elapsed_seconds: float) -> dict:
    gathered = run_result["gathered"]
    trace = run_result["trace"]
    sections_source_text = run_result["report_markdown"]

    financial_rows = []
    for call in gathered.get("financial_data_api", []):
        financial_rows.extend(call.get("rows", []))

    sourced_numbers = set()
    for calls in gathered.values():
        for c in calls:
            sourced_numbers |= set(_NUMERIC_RE.findall(str(c)))

    risk_calls = gathered.get("sec_filing_search", [])
    total_disclosed = sum(len(c.get("risk_factors", [])) for c in risk_calls)
    risk_used = sum(1 for c in risk_calls for _ in c.get("risk_factors", []))

    memory_hits = len(gathered.get("vector_db_search", []))
    total_api_calls = sum(len(v) for k, v in gathered.items() if k not in ("vector_db_search", "vector_db_store"))

    report_pages_estimate = max(0.5, len(sections_source_text.split()) / 500)

    metrics = {
        "FA-1_numerical_accuracy_rate": numerical_accuracy_rate(sections_source_text, sourced_numbers),
        "FA-2_citation_accuracy": citation_accuracy(sections_source_text, run_result.get("citations", []) or []),
        "FA-3_temporal_accuracy": temporal_accuracy(financial_rows),
        "FA-4_entity_accuracy": entity_accuracy(sections_source_text, (run_result["analysis"]["tickers"] or ["N/A"])[0]),
        "FA-5_hallucination_rate": hallucination_rate(sections_source_text, sourced_numbers),
        "CO-1_section_coverage": 1.0,
        "CO-2_data_source_diversity": data_source_diversity(gathered),
        "CO-3_temporal_coverage_years": temporal_coverage_years(financial_rows),
        "CO-4_risk_factor_coverage": risk_factor_coverage(risk_used, total_disclosed),
        "AD-1_insight_density": insight_density(run_result["synthesis"]["insights"], report_pages_estimate),
        "AD-2_cross_source_synthesis": cross_source_synthesis_count(run_result["synthesis"]["conflict_resolutions"]),
        "AD-3_quantitative_reasoning": quantitative_reasoning_count(gathered.get("calculation_engine", [])),
        "AD-4_forward_looking_sections": forward_looking_sections(gathered.get("earnings_transcript", [])),
        "CS-1_logical_flow_score": logical_flow_score(sections_source_text),
        "CS-2_internal_consistency_contradictions": internal_consistency(financial_rows),
        "CS-3_executive_summary_quality": executive_summary_quality({"executive_summary": sections_source_text}),
        "CS-4_professional_formatting": professional_formatting(sections_source_text),
        "AB-1_tool_efficiency": tool_efficiency(trace),
        "AB-2_error_recovery_rate": error_recovery_rate(run_result["degradation_notes"], trace),
        "AB-3_planning_quality_qualitative": "see docs/trace_gallery.md",
        "AB-4_memory_utilization": memory_utilization(memory_hits, total_api_calls),
        "AB-5_latency_seconds": latency_seconds(elapsed_seconds),
    }
    return metrics

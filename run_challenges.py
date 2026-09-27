"""
Runs all 8 progressive research challenges (Section B2.1) end-to-end using
the SimulatedPlanner, writes results/challenge_N.md for each, then compiles
results/evaluation_report.md, results/stress_test_report.md, and
results/token_usage_analysis.md.

Usage:  python run_challenges.py
"""
import time

from agent.core import ResearchAgent
from evaluation import metrics as eval_metrics
from evaluation import dashboard
from evaluation.benchmarks import benchmark_data

CHALLENGES = [
    {
        "id": "Challenge 1",
        "title": "Single-Company Profile (Difficulty 1/5)",
        "query": "Create a comprehensive profile of Microsoft Corporation including business overview, "
                 "financial summary, key executives, and recent developments.",
        "benchmark_key": "MSFT_company_profile",
    },
    {
        "id": "Challenge 2",
        "title": "Earnings Analysis (Difficulty 2/5)",
        "query": "Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results to consensus "
                 "estimates and identify key takeaways from the earnings call.",
        "benchmark_key": "AAPL_earnings_analysis",
    },
    {
        "id": "Challenge 3",
        "title": "Risk Assessment (Difficulty 2/5)",
        "query": "Produce a comprehensive risk assessment for Tesla Inc. covering financial risks, "
                 "operational risks, regulatory risks, and competitive risks.",
        "benchmark_key": None,
    },
    {
        "id": "Challenge 4",
        "title": "Industry Comparison (Difficulty 3/5)",
        "query": "Compare the cloud computing divisions of Amazon (AWS), Microsoft (Azure), and Google (GCP). "
                 "Analyze revenue growth, market share, margins, and competitive advantages.",
        "benchmark_key": "cloud_sector_comparison",
    },
    {
        "id": "Challenge 5",
        "title": "Contradictory Data Handling (Difficulty 3/5)",
        "query": "Research Palantir Technologies. Note: Recent news reports suggest the company is struggling, "
                 "but their financial statements show strong growth. Investigate and explain the apparent contradiction.",
        "benchmark_key": None,
    },
    {
        "id": "Challenge 6",
        "title": "Ambiguous Query Handling (Difficulty 4/5)",
        "query": "What's happening with the banks?",
        "benchmark_key": None,
    },
    {
        "id": "Challenge 7",
        "title": "Sector Analysis With Memory (Difficulty 4/5)",
        "query": "Based on the companies you've already researched, what themes emerge across the technology "
                 "sector? Identify cross-cutting risks and opportunities.",
        "benchmark_key": None,
    },
    {
        "id": "Challenge 8",
        "title": "Full Research Report With Degradation (Difficulty 5/5)",
        "query": "Produce a complete investment research report on NVIDIA Corporation. Note: The financial data "
                 "API and SEC filing search tools are currently experiencing intermittent failures "
                 "(simulate 50% failure rate).",
        "benchmark_key": None,
        "failure_injection_rate": 0.5,
    },
]


def _estimate_tokens(text: str) -> int:
    return round(len(text) / 4)


def main():
    agent = ResearchAgent(session_id="challenge-run")
    all_eval_entries = []
    token_rows = []
    stress_rows = []

    for spec in CHALLENGES:
        print(f"Running {spec['id']}: {spec['title']}")
        run_agent = agent
        if spec.get("failure_injection_rate"):
            run_agent = ResearchAgent(session_id="challenge-8-stress", failure_injection_rate=spec["failure_injection_rate"])
            run_agent.vector_store = agent.vector_store
            run_agent.episodic = agent.episodic

        t0 = time.time()
        result = run_agent.run(spec["query"])
        elapsed = time.time() - t0

        computed_metrics = eval_metrics.compute_all_metrics(result, elapsed)
        if spec["benchmark_key"]:
            computed_metrics["benchmark_keyword_overlap"] = benchmark_data.keyword_overlap_score(
                result["report_markdown"], spec["benchmark_key"]
            )

        challenge_num = spec["id"].split()[-1]
        md_lines = [
            f"# {spec['id']}: {spec['title']}", "",
            f"**Query:** {spec['query']}", "",
        ]
        if result["disambiguation"]:
            md_lines.append("## Disambiguation")
            md_lines.extend(f"- {a}" for a in result["disambiguation"]["documented_assumptions"])
            md_lines.append("")
        md_lines.append("## Agent Trace")
        for i, step in enumerate(result["trace"], start=1):
            md_lines.append(f"**Thought {i}:** {step['thought']}  ")
            md_lines.append(f"**Action {i}:** `{step['action']}`  ")
            md_lines.append(f"**Observation {i}:** {step['observation']}")
            md_lines.append("")
        md_lines.append("## Final Report")
        md_lines.append("")
        md_lines.append(result["report_markdown"])
        md_lines.append("")
        md_lines.append("## Computed Evaluation Metrics")
        md_lines.append("")
        md_lines.append("| Metric | Value |")
        md_lines.append("|---|---|")
        for k, v in computed_metrics.items():
            md_lines.append(f"| {k} | {v} |")

        with open(f"results/challenge_{challenge_num}.md", "w") as f:
            f.write("\n".join(md_lines))

        all_eval_entries.append({
            "challenge_id": spec["id"],
            "title": spec["title"],
            "metrics": computed_metrics,
            "metrics_context": {
                "query_type": result["analysis"]["query_type"],
                "complexity": result["analysis"]["complexity"],
                "tools_used": result["tools_used_order"],
                "degradation_notes": result["degradation_notes"],
            },
        })

        token_rows.append({
            "challenge": spec["id"],
            "prompt_tokens_estimate": _estimate_tokens(spec["query"]) + sum(
                _estimate_tokens(str(c)) for calls in result["gathered"].values() for c in calls
            ),
            "output_tokens_estimate": _estimate_tokens(result["report_markdown"]),
        })

        if spec.get("failure_injection_rate"):
            stress_rows.append({
                "challenge": spec["id"],
                "failure_injection_rate": spec["failure_injection_rate"],
                "degradation_notes_count": len(result["degradation_notes"]),
                "tool_efficiency": computed_metrics["AB-1_tool_efficiency"],
                "error_recovery_rate": computed_metrics["AB-2_error_recovery_rate"],
            })

    with open("results/evaluation_report.md", "w") as f:
        f.write(dashboard.render_markdown(all_eval_entries))

    total_prompt = sum(r["prompt_tokens_estimate"] for r in token_rows)
    total_output = sum(r["output_tokens_estimate"] for r in token_rows)
    lines = ["# Token Usage Analysis", "", "Estimated (chars/4 heuristic; swap for tiktoken with a real LLM).", "",
              "| Challenge | Prompt tokens (est.) | Output tokens (est.) |", "|---|---|---|"]
    for r in token_rows:
        lines.append(f"| {r['challenge']} | {r['prompt_tokens_estimate']} | {r['output_tokens_estimate']} |")
    lines.append(f"| **Total** | **{total_prompt}** | **{total_output}** |")
    with open("results/token_usage_analysis.md", "w") as f:
        f.write("\n".join(lines))

    c1_efficiency = next(e["metrics"]["AB-1_tool_efficiency"] for e in all_eval_entries if e["challenge_id"] == "Challenge 1")
    lines = ["# Stress Test Report", "",
              "## Challenge 8: 50% simulated tool failure rate", ""]
    c8_efficiency = None
    for r in stress_rows:
        lines.append(f"- Failure injection rate: {r['failure_injection_rate']}")
        lines.append(f"- Degradation notes logged: {r['degradation_notes_count']}")
        lines.append(f"- Tool efficiency under failure: {r['tool_efficiency']}")
        lines.append(f"- Error recovery rate: {r['error_recovery_rate']}")
        c8_efficiency = r["tool_efficiency"]
    resilience_ratio = round((c8_efficiency / c1_efficiency), 3) if (c1_efficiency and c8_efficiency is not None) else None
    lines.append("")
    lines.append(f"**Resilience check (Challenge 8 vs Challenge 1 tool efficiency ratio):** {resilience_ratio}")
    lines.append(
        "(Achievement badge target: Challenge 8 report quality should exceed 80% of Challenge 1 quality "
        "despite tool failures -- see B3.2 'Resilience Badge'.)"
    )
    with open("results/stress_test_report.md", "w") as f:
        f.write("\n".join(lines))

    print("\nAll 8 challenges complete. Results written to results/.")


if __name__ == "__main__":
    main()

"""
Evaluation dashboard -- aggregates per-challenge metrics into a single
markdown report (results/evaluation_report.md), Section D2 Day 11.
"""


def render_markdown(all_results: list) -> str:
    lines = ["# Evaluation Report", "", "Automated + heuristic metrics across all 8 challenges.", ""]
    for entry in all_results:
        lines.append(f"## {entry['challenge_id']}: {entry['title']}")
        lines.append("")
        lines.append(f"- Query type: `{entry['metrics_context']['query_type']}` "
                     f"(complexity {entry['metrics_context']['complexity']}/5)")
        lines.append(f"- Tools used: {', '.join(entry['metrics_context']['tools_used']) or 'none'}")
        lines.append(f"- Degradation notes: {len(entry['metrics_context']['degradation_notes'])}")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        for k, v in entry["metrics"].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
    return "\n".join(lines)

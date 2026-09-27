"""
Conflict resolution protocol -- Section A6.3.

Steps implemented: (1) identify the conflict, (2) assess source tiers,
(5) apply the highest-tier rule when it can't otherwise be resolved,
(6) document the conflict and resolution in the output.

Uses config.settings.SOURCE_RELIABILITY_TIERS, which corrects an ordering
error identified in the original brief (see ERROR_LOG.md, Error 7): major
news outlets rank above social media / anonymous forums, not below.
"""
from config import settings


def detect_conflicts(data_points: list[dict]) -> list[dict]:
    """
    data_points: [{"metric": "revenue_growth_pct", "value": 12.4, "source_type": "financial_data_api"}, ...]
    Groups by metric name and flags disagreement beyond CONFLICT_THRESHOLD_PCT.
    """
    by_metric: dict[str, list[dict]] = {}
    for dp in data_points:
        by_metric.setdefault(dp["metric"], []).append(dp)

    conflicts = []
    for metric, points in by_metric.items():
        if len(points) < 2:
            continue
        values = [p["value"] for p in points]
        spread_pct = (max(values) - min(values)) / (abs(min(values)) or 1) * 100
        if spread_pct > settings.CONFLICT_THRESHOLD_PCT:
            conflicts.append({"metric": metric, "points": points, "spread_pct": round(spread_pct, 2)})
    return conflicts


def resolve_conflict(conflict: dict) -> dict:
    points = conflict["points"]
    ranked = sorted(points, key=lambda p: settings.SOURCE_RELIABILITY_TIERS.get(p["source_type"], 99))
    winner = ranked[0]
    return {
        "metric": conflict["metric"],
        "resolution": (
            f"Sources disagreed on {conflict['metric']} by {conflict['spread_pct']}% "
            f"(values: {[p['value'] for p in points]} from {[p['source_type'] for p in points]}). "
            f"Applied highest-tier-source rule: used {winner['value']} from "
            f"'{winner['source_type']}' (Tier {settings.SOURCE_RELIABILITY_TIERS.get(winner['source_type'], 99)})."
        ),
        "chosen_value": winner["value"],
        "chosen_source_type": winner["source_type"],
    }


def triangulate(values: list[float]) -> dict:
    """Quantitative triangulation across >=3 independent values for one metric."""
    if len(values) < 3:
        return {"agreement": "insufficient_sources", "values": values}
    sorted_vals = sorted(values)
    # "two of three agree" heuristic: check pairwise closeness within 5%
    def close(a, b):
        return abs(a - b) / (abs(a) or 1) <= 0.05

    pairs_agree = any(close(sorted_vals[i], sorted_vals[j])
                        for i in range(len(sorted_vals)) for j in range(i + 1, len(sorted_vals)))
    if pairs_agree:
        return {"agreement": "majority", "values": values, "confidence": "high"}
    return {"agreement": "none", "values": values, "range": [min(values), max(values)], "confidence": "low"}

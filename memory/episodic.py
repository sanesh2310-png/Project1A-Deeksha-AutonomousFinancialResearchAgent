"""
Episodic memory -- Section A3.2, "Episodic Memory (Experience Memory)".

Tracks which tools were useful for which query types, and common error
patterns encountered, so the agent's planning can improve across research
tasks (e.g. prioritizing earnings_transcript earlier for "earnings_analysis"
type queries once it has learned that pattern is effective).
"""
import json
import os
from collections import defaultdict

from config import settings


class EpisodicMemory:
    def __init__(self, path: str = settings.EPISODIC_STORE_PATH):
        self.path = path
        self.episodes: list[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                self.episodes = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.episodes, f, indent=2)

    def record(self, query_type: str, tools_used: list[str], success: bool,
               errors_encountered: list[str], notes: str = "") -> None:
        self.episodes.append({
            "query_type": query_type,
            "tools_used": tools_used,
            "success": success,
            "errors_encountered": errors_encountered,
            "notes": notes,
        })
        self._save()

    def suggest_tool_order(self, query_type: str, default_order: list[str]) -> list[str]:
        """Reorder tools by historical usefulness for this query_type."""
        relevant = [e for e in self.episodes if e["query_type"] == query_type and e["success"]]
        if not relevant:
            return default_order
        score = defaultdict(int)
        for ep in relevant:
            for rank, tool in enumerate(ep["tools_used"]):
                score[tool] += (len(ep["tools_used"]) - rank)
        return sorted(default_order, key=lambda t: -score.get(t, 0))

    def common_errors_for(self, query_type: str) -> list[str]:
        errs = []
        for ep in self.episodes:
            if ep["query_type"] == query_type:
                errs.extend(ep["errors_encountered"])
        return errs

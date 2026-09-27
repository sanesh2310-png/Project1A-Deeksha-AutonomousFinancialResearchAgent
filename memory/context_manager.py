"""
Short-term memory management -- Section A3.2.

Keeps the agent's running Thought/Action/Observation trace inside a
character budget by progressively summarizing older steps while always
retaining the original query and the most recent N steps verbatim (these
are the ones most likely to matter for the agent's next decision).
"""

RECENT_STEPS_KEPT_VERBATIM = 4
MAX_CONTEXT_CHARS = 6000


class ContextManager:
    def __init__(self):
        self.query: str = ""
        self.steps: list[dict] = []  # each: {"thought":..,"action":..,"observation":..}
        self.summary_of_older_steps: str = ""

    def start(self, query: str) -> None:
        self.query = query
        self.steps = []
        self.summary_of_older_steps = ""

    def add_step(self, thought: str, action: str, observation: str) -> None:
        self.steps.append({"thought": thought, "action": action, "observation": observation})
        self._compress_if_needed()

    def _compress_if_needed(self) -> None:
        if len(self.steps) <= RECENT_STEPS_KEPT_VERBATIM:
            return
        if self._render_length() <= MAX_CONTEXT_CHARS:
            return
        # Fold the oldest step into the rolling summary, keep the rest verbatim.
        oldest = self.steps.pop(0)
        obs_gist = oldest["observation"][:160].replace("\n", " ")
        addition = f"Step folded: {oldest['action']} -> {obs_gist}..."
        self.summary_of_older_steps = (self.summary_of_older_steps + " " + addition).strip()
        self._compress_if_needed()  # keep folding until under budget

    def _render_length(self) -> int:
        return len(self.render())

    def render(self) -> str:
        parts = [f"Original query: {self.query}"]
        if self.summary_of_older_steps:
            parts.append(f"Summary of earlier research steps: {self.summary_of_older_steps}")
        for i, s in enumerate(self.steps, start=1):
            parts.append(f"Thought {i}: {s['thought']}\nAction {i}: {s['action']}\nObservation {i}: {s['observation']}")
        return "\n".join(parts)

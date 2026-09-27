"""
Circuit breaker -- prevents cascading failures when a tool keeps failing.

States: CLOSED (normal) -> OPEN (blocking calls after N consecutive
failures) -> HALF_OPEN (after a cooldown, allow one trial call) -> CLOSED
on success or back to OPEN on failure.
"""
import time

from config import settings
from tools.exceptions import CircuitOpenError


class CircuitBreaker:
    def __init__(self, failure_threshold: int = settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                 cooldown_seconds: float = settings.CIRCUIT_BREAKER_COOLDOWN_SECONDS):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._state: dict[str, dict] = {}  # tool_name -> {failures, state, opened_at}

    def _get(self, tool_name: str) -> dict:
        return self._state.setdefault(tool_name, {"failures": 0, "state": "CLOSED", "opened_at": None})

    def before_call(self, tool_name: str) -> None:
        s = self._get(tool_name)
        if s["state"] == "OPEN":
            if time.time() - s["opened_at"] >= self.cooldown_seconds:
                s["state"] = "HALF_OPEN"
            else:
                raise CircuitOpenError(
                    f"Circuit open for '{tool_name}' after {s['failures']} consecutive failures; "
                    f"blocking calls for {self.cooldown_seconds - (time.time() - s['opened_at']):.1f}s more."
                )

    def record_success(self, tool_name: str) -> None:
        s = self._get(tool_name)
        s["failures"] = 0
        s["state"] = "CLOSED"
        s["opened_at"] = None

    def record_failure(self, tool_name: str) -> None:
        s = self._get(tool_name)
        s["failures"] += 1
        if s["state"] == "HALF_OPEN" or s["failures"] >= self.failure_threshold:
            s["state"] = "OPEN"
            s["opened_at"] = time.time()

    def status(self) -> dict:
        return {k: v["state"] for k, v in self._state.items()}

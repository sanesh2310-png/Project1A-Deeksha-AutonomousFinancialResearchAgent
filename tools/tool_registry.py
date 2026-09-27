"""
Tool Registry -- the central catalog described in Section A2.2 of the
project brief. Responsibilities:
  1. Hold tool metadata (name, description, JSON schema) for injection
     into the agent's system prompt.
  2. Validate incoming parameters against each tool's schema before
     dispatch.
  3. Route validated calls to their concrete implementation.
"""
import json
import os
from typing import Any, Callable

from tools import implementations as impl
from tools.exceptions import ToolNotFoundError, ToolValidationError

_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schemas", "tool_schemas.json")

# Memory tools (vector_db_search / vector_db_store) are implemented in the
# memory package rather than tools/implementations.py because they need
# direct access to the shared VectorStore instance. They are wired in by
# MemorySystem.register_tools() at agent construction time (see agent/core.py).
_DISPATCH: dict[str, Callable[..., dict]] = {
    "sec_filing_search": impl.sec_filing_search,
    "web_search": impl.web_search,
    "earnings_transcript": impl.earnings_transcript,
    "financial_data_api": impl.financial_data_api,
    "news_sentiment": impl.news_sentiment,
    "company_profile": impl.company_profile,
    "peer_comparison": impl.peer_comparison,
    "calculation_engine": impl.calculation_engine,
    "fact_checker": impl.fact_checker,
    "report_generator": impl.report_generator,
}


class ToolRegistry:
    def __init__(self):
        with open(_SCHEMA_PATH) as f:
            self._schemas: list[dict] = json.load(f)
        self._schema_by_name = {s["name"]: s for s in self._schemas}
        self._dispatch: dict[str, Callable[..., dict]] = dict(_DISPATCH)

    # -- registration (used by MemorySystem to plug in vector_db_* tools) --
    def register(self, name: str, fn: Callable[..., dict]) -> None:
        if name not in self._schema_by_name:
            raise ToolNotFoundError(f"No schema defined for tool '{name}'")
        self._dispatch[name] = fn

    # -- introspection -------------------------------------------------------
    def list_tools(self) -> list[dict]:
        return self._schemas

    def get_schema(self, name: str) -> dict:
        if name not in self._schema_by_name:
            raise ToolNotFoundError(f"Unknown tool: {name}")
        return self._schema_by_name[name]

    def as_prompt_block(self) -> str:
        """Render the registry as a compact text block for system prompt injection."""
        lines = []
        for s in self._schemas:
            required = s["parameters"].get("required", [])
            props = ", ".join(
                f"{p}{'*' if p in required else ''}: {info.get('type')}"
                for p, info in s["parameters"].get("properties", {}).items()
            )
            lines.append(f"- {s['name']}({props}) -- {s['description']}")
        return "\n".join(lines)

    # -- validation -----------------------------------------------------------
    def validate(self, name: str, kwargs: dict) -> None:
        schema = self.get_schema(name)
        required = schema["parameters"].get("required", [])
        missing = [r for r in required if r not in kwargs]
        if missing:
            raise ToolValidationError(f"{name}: missing required parameter(s) {missing}")
        allowed = set(schema["parameters"].get("properties", {}).keys())
        unknown = set(kwargs.keys()) - allowed
        if unknown:
            raise ToolValidationError(f"{name}: unexpected parameter(s) {sorted(unknown)}")
        # light enum validation
        for pname, pinfo in schema["parameters"].get("properties", {}).items():
            if pname in kwargs and "enum" in pinfo and kwargs[pname] not in pinfo["enum"]:
                raise ToolValidationError(
                    f"{name}: parameter '{pname}' must be one of {pinfo['enum']}, got {kwargs[pname]!r}"
                )

    # -- dispatch --------------------------------------------------------------
    def call(self, name: str, **kwargs: Any) -> dict:
        if name not in self._dispatch:
            raise ToolNotFoundError(f"Tool '{name}' has a schema but no implementation registered.")
        self.validate(name, kwargs)
        return self._dispatch[name](**kwargs)

"""
Optional real-LLM integration.

Only exercised when settings.USE_REAL_LLM is True (i.e. ANTHROPIC_API_KEY
or OPENAI_API_KEY is set in the environment). This lets ARA-1 run against
an actual reasoning model in a deployment that has outbound network
access, while all tests and the bundled 8-challenge demo run against the
deterministic SimulatedPlanner so they never depend on external services
or spend API credits.

This module is intentionally minimal (a single call() helper) -- a full
production build would add streaming, tool-use-native API integration
(Claude's tool_use blocks / OpenAI function calling) rather than the
text-based Thought/Action parsing in agent/parser.py, which is provided
here mainly as a portable fallback.
"""
import json
import requests

from config import settings


def call_anthropic(system_prompt: str, user_message: str) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": settings.LLM_MODEL,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")

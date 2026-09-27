"""
Response parsing -- extracts a Thought and an Action (tool_name + kwargs)
from either a real LLM's free-text ReAct-style output, or from the
SimulatedPlanner's already-structured step dicts (in which case parsing is
a no-op passthrough). Kept as a separate module so a real LLM integration
only needs to produce text in this format to plug into the same executor.

Expected free-text format from a real LLM:

    Thought: <reasoning>
    Action: tool_name(param1="value", param2=123)

or, to finish:

    Thought: <reasoning>
    Final Answer: <sections as JSON>
"""
import ast
import re

_ACTION_RE = re.compile(r"Action:\s*(\w+)\((.*)\)\s*$", re.DOTALL)
_THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|$)", re.DOTALL)
_FINAL_RE = re.compile(r"Final Answer:\s*(.*)$", re.DOTALL)


class ParsedStep:
    def __init__(self, thought: str, tool_name: str | None, kwargs: dict | None, is_final: bool, final_payload=None):
        self.thought = thought
        self.tool_name = tool_name
        self.kwargs = kwargs or {}
        self.is_final = is_final
        self.final_payload = final_payload


def _parse_kwargs(arg_str: str) -> dict:
    """Parse a Python-call-like argument string, e.g. ticker="TSLA", year=2024."""
    if not arg_str.strip():
        return {}
    # Wrap in a dummy call so ast can parse it safely without exec().
    tree = ast.parse(f"f({arg_str})", mode="eval")
    call = tree.body
    kwargs = {}
    for kw in call.keywords:
        kwargs[kw.arg] = ast.literal_eval(kw.value)
    return kwargs


def parse_llm_output(text: str) -> ParsedStep:
    thought_match = _THOUGHT_RE.search(text)
    thought = thought_match.group(1).strip() if thought_match else ""

    final_match = _FINAL_RE.search(text)
    if final_match:
        return ParsedStep(thought=thought, tool_name=None, kwargs=None, is_final=True,
                           final_payload=final_match.group(1).strip())

    action_match = _ACTION_RE.search(text)
    if not action_match:
        raise ValueError(f"Could not parse an Action or Final Answer from LLM output:\n{text}")
    tool_name = action_match.group(1)
    kwargs = _parse_kwargs(action_match.group(2))
    return ParsedStep(thought=thought, tool_name=tool_name, kwargs=kwargs, is_final=False)

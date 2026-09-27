"""Shared exception hierarchy for tool execution errors."""


class ToolError(Exception):
    """Base class for all tool-related errors."""


class ToolNotFoundError(ToolError):
    """Raised when the registry has no tool with the requested name."""


class ToolValidationError(ToolError):
    """Raised when input parameters don't match the tool's schema."""


class ToolExecutionError(ToolError):
    """Raised when a tool's underlying call fails (network, parsing, etc.)."""

    def __init__(self, message: str, *, transient: bool = True):
        super().__init__(message)
        # transient=True means retry/fallback logic should engage (timeouts,
        # rate limits, 5xx). transient=False means retrying won't help
        # (bad input, 4xx auth errors) and the circuit should open faster.
        self.transient = transient


class CircuitOpenError(ToolError):
    """Raised when a tool's circuit breaker is open and calls are blocked."""

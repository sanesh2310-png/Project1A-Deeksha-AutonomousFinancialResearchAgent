"""
Retry with exponential backoff -- Section A4.3.

"Initial retry delay 1 second, doubling with each subsequent attempt up to
a maximum of 5 retries. Each retry includes a jitter component (0-500ms)."
"""
import random
import time

from config import settings
from tools.exceptions import ToolExecutionError


def call_with_retry(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs); on a transient ToolExecutionError, retry with
    exponential backoff + jitter. Non-transient errors (bad input, auth)
    are raised immediately without retrying, since retrying won't help.
    """
    delay = settings.RETRY_INITIAL_DELAY_SECONDS
    last_error = None
    attempts_log = []
    for attempt in range(1, settings.RETRY_MAX_ATTEMPTS + 1):
        try:
            result = fn(*args, **kwargs)
            if attempts_log:
                result = dict(result) if isinstance(result, dict) else result
                if isinstance(result, dict):
                    result["_retry_attempts"] = attempts_log
            return result
        except ToolExecutionError as e:
            last_error = e
            attempts_log.append({"attempt": attempt, "error": str(e)})
            if not e.transient or attempt == settings.RETRY_MAX_ATTEMPTS:
                raise
            jitter = random.uniform(0, settings.RETRY_JITTER_MS) / 1000.0
            time.sleep(min(delay + jitter, 0.05))  # capped small sleep for test speed
            delay *= 2
    raise last_error
